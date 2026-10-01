# ==================================================================================================================== #
#             _____           _ _               ____ ___                                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ _|                                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |    | |                                                               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___ | |                                                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|___|                                                              #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
A data model of a GitHub Actions workflow file.

A workflow file is read once into objects:

.. code-block:: text

   Workflow                 a workflow file, e.g. '.github/workflows/CompletePipeline.yml'
   +-- Input                an input of 'on.workflow_call'
   +-- Output               an output of 'on.workflow_call'
   +-- Secret               a secret of 'on.workflow_call'
   +-- Permission           a permission the workflow declares
   +-- Job                  a job, in file order
       +-- UsesReference    the reusable workflow the job calls
       +-- Permission       a permission the job declares
           +-- UsesReference    the action the step runs

Every element knows its parent, the workflow it belongs to, and the line it starts at in the file, so a consumer can
name the place a finding comes from, as ``CompletePipeline.yml:552``.

The model is independent of :mod:`pyTooling.CI.GitHub`, which models a workflow *run* as the REST API reports it.

:raises MissingDependencyError: If the 'github' extra isn't installed.
"""
from __future__            import annotations

from functools             import cached_property
from pathlib               import Path, PurePosixPath
from typing                import Any, ClassVar, Generic, Iterable, Iterator, Mapping, Optional as Nullable, Self
from typing                import TypeVar, Union

from pyTooling.CI          import CIError
from pyTooling.Common      import getFullyQualifiedName, StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError
from pyTooling.MetaClasses import ExtendedType, abstractclass

try:
	from ruamel.yaml              import YAML, YAMLError
	from ruamel.yaml.comments     import CommentedMap, CommentedSeq
	from ruamel.yaml.scalarbool   import ScalarBoolean
	from ruamel.yaml.scalarfloat  import ScalarFloat
	from ruamel.yaml.scalarint    import ScalarInt
	from ruamel.yaml.scalarstring import ScalarString
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="ruamel.yaml", extra="github") from ex


__all__ = ["ValueT"]

ValueT = Union[str, bool, int, float, None, list["ValueT"], dict[str, "ValueT"]]
"""A value read from a workflow file, converted to plain Python types."""

ParentType = TypeVar("ParentType", bound="Base")
"""A type variable for the type of an element's parent."""

ParentTypes = Nullable[Union[type, tuple[type, ...]]]
"""The type of :attr:`Base._PARENT_TYPE`: ``None``, a class, or a tuple of classes."""


@export
class WorkflowError(CIError):
	"""
	Base-exception of all exceptions raised by :mod:`pyTooling.CI.GitHub.WorkflowFile`.

	The exception is raised for a workflow file that is not a well-formed workflow. It carries the file and the line
	the problem was found at in :attr:`Path` and :attr:`Line`, and names both in a note.
	"""

	_path: Nullable[Path]  #: Path to the workflow file.
	_line: Nullable[int]   #: Line in the workflow file, starting at 1.

	def __init__(self, message: str, path: Nullable[Path] = None, line: Nullable[int] = None) -> None:
		"""
		Initializes a workflow error and names the place it was found at in a note.

		:param message: The exception's message.
		:param path:    Optional, path to the workflow file. Default: ``None``.
		:param line:    Optional, line in the workflow file, starting at 1. Default: ``None``.
		"""
		super().__init__(message)

		self._path = path
		self._line = line

		if path is not None:
			self.add_note(f"In '{path}'." if line is None else f"In '{path}:{line}'.")

	@readonly
	def Path(self) -> Nullable[Path]:
		"""
		Read-only property to access the path to the workflow file (:attr:`_path`).

		:returns: The path, or ``None`` if the problem isn't tied to a file.
		"""
		return self._path

	@readonly
	def Line(self) -> Nullable[int]:
		"""
		Read-only property to access the line the problem was found at (:attr:`_line`).

		:returns: The line, starting at 1, or ``None`` if the problem isn't tied to a line.
		"""
		return self._line


@export
class AccessLevel(StringEnum):
	"""
	The access a permission grants to the ``GITHUB_TOKEN``.

	The members are declared from the least to the most access, so :meth:`Rank` orders them.
	"""

	NoAccess = "none"   #: No access.
	Read =     "read"   #: Read access.
	Write =    "write"  #: Read and write access.

	@cached_property
	def Rank(self) -> int:
		"""
		Read-only property to return the member's position in the order of access, so levels can be compared.

		It is computed once per member.

		:returns: ``0`` for :attr:`NoAccess`, ``1`` for :attr:`Read`, ``2`` for :attr:`Write`.
		"""
		return list(AccessLevel).index(self)


@export
class PermissionScope(StringEnum):
	"""
	The scope a permission grants the ``GITHUB_TOKEN`` access to, as a key of ``permissions``.

	:attr:`All` stands for every scope at once, as ``read-all`` and ``write-all`` grant it.
	"""

	All =                 "*"                     #: Every scope, from ``read-all`` or ``write-all``.
	Actions =             "actions"               #: Workflows, runs and artifacts.
	ArtifactMetadata =    "artifact-metadata"     #: Storage records of artifacts.
	Attestations =        "attestations"          #: Artifact attestations.
	Checks =              "checks"                #: Check runs and check suites.
	CodeQuality =         "code-quality"          #: Code quality findings.
	Contents =            "contents"              #: Repository contents, commits, branches, tags and releases.
	Deployments =         "deployments"           #: Deployments.
	Discussions =         "discussions"           #: GitHub Discussions.
	IDToken =             "id-token"              #: An OpenID Connect token.
	Issues =              "issues"                #: Issues and their comments.
	Packages =            "packages"              #: GitHub Packages.
	Pages =               "pages"                 #: GitHub Pages builds.
	PullRequests =        "pull-requests"         #: Pull requests.
	SecurityEvents =      "security-events"       #: Code scanning alerts.
	Statuses =            "statuses"              #: Commit statuses.
	VulnerabilityAlerts = "vulnerability-alerts"  #: Dependabot alerts.


@export
class InputType(StringEnum):
	"""The type of an input of a reusable workflow."""

	String =  "string"   #: A string.
	Boolean = "boolean"  #: A boolean.
	Number =  "number"   #: A number.


@export
@abstractclass
class Base(Generic[ParentType], metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a workflow file.

	Every element knows the element containing it, the workflow it belongs to, and the line it starts at.
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = None  #: Type a parent must have, or ``None`` when the element has no parent.

	_parent:   Nullable[ParentType]  #: Reference to the containing element.
	_workflow: Nullable[Workflow]    #: Reference to the workflow this element belongs to.
	_line:     int                   #: Line the element starts at in the workflow file, starting at 1.

	def __init__(self, line: int, *, parent: Nullable[ParentType] = None) -> None:
		"""
		Initializes an element of a workflow file.

		:param line:        Line the element starts at in the workflow file, starting at 1.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
		:raises ValueError: If parameter 'line' is ``None``.
		:raises TypeError:  If parameter 'line' is not of type :class:`int`.
		:raises ValueError: If parameter 'line' is not positive.
		:raises TypeError:  If parameter 'parent' is given for a class declaring no :attr:`_PARENT_TYPE`.
		:raises TypeError:  If parameter 'parent' is not of the type this class declares in :attr:`_PARENT_TYPE`.
		"""
		if line is None:
			raise ValueError("Parameter 'line' is None.")
		elif not isinstance(line, int) or isinstance(line, bool):
			ex = TypeError("Parameter 'line' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(line)}'.")
			raise ex
		elif line < 1:
			ex = ValueError("Parameter 'line' is not positive.")
			ex.add_note(f"Got value '{line}'.")
			raise ex

		if parent is not None:
			if self._PARENT_TYPE is None:
				ex = TypeError(f"A '{getFullyQualifiedName(self)}' has no parent.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex
			elif not isinstance(parent, self._PARENT_TYPE):
				parentTypes = self._PARENT_TYPE if isinstance(self._PARENT_TYPE, tuple) else (self._PARENT_TYPE, )
				ex = TypeError(f"Parameter 'parent' is not of type {' or '.join(f'{t.__name__!r}' for t in parentTypes)}.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex

		self._parent =   parent
		self._workflow = None if parent is None else parent._workflow
		self._line =     line

	@readonly
	def Parent(self) -> Nullable[ParentType]:
		"""
		Read-only property to access the containing element (:attr:`_parent`).

		:returns: The containing element, or ``None`` for a :class:`Workflow`.
		"""
		return self._parent

	@readonly
	def Workflow(self) -> Nullable[Workflow]:
		"""
		Read-only property to access the workflow this element belongs to (:attr:`_workflow`).

		:returns: The workflow, or ``None`` for an element outside one.
		"""
		return self._workflow

	@readonly
	def Line(self) -> int:
		"""
		Read-only property to access the line the element starts at in the workflow file (:attr:`_line`).

		:returns: The line, starting at 1.
		"""
		return self._line

	@readonly
	def Location(self) -> str:
		"""
		Read-only property to return the place the element is written at, for a message.

		:returns: The workflow file's name and the line, as ``CompletePipeline.yml:552``, or ``line 552`` for an element
		          outside a workflow.
		"""
		if self._workflow is None:
			return f"line {self._line}"

		return f"{self._workflow._path.name}:{self._line}"

	@staticmethod
	def _KeyLine(mapping: CommentedMap, key: str) -> int:
		"""
		Return the line a key of a mapping is written at.

		:param mapping: The mapping read from the file.
		:param key:     The key.
		:returns:       The line, starting at 1.
		"""
		return mapping.lc.key(key)[0] + 1

	@staticmethod
	def _ToPython(value: Any) -> ValueT:
		"""
		Convert a value read by ``ruamel.yaml`` into plain Python types.

		The round-trip loader returns its own types for mappings, lists, block scalars, anchored booleans, and numbers
		written in another notation than a plain decimal. They derive from the Python types, but keep what they were
		read with - an anchored boolean even prints as ``0`` or ``1``. Every other value is a Python type already.

		:param value: The value read from the file.
		:returns:     The value as :class:`dict`, :class:`list`, :class:`str`, :class:`bool`, :class:`int`,
		              :class:`float` or ``None``.
		"""
		if isinstance(value, CommentedMap):
			return {str(key): Base._ToPython(item) for key, item in value.items()}
		elif isinstance(value, CommentedSeq):
			return [Base._ToPython(item) for item in value]
		elif isinstance(value, ScalarBoolean):
			return bool(value)
		elif isinstance(value, ScalarInt):
			return int(value)
		elif isinstance(value, ScalarFloat):
			return float(value)
		elif isinstance(value, ScalarString):
			return str(value)

		return value


@export
class Workflow(Base[None]):
	"""
	A GitHub Actions workflow file.

	The workflow is named by its file's stem - ``CompletePipeline`` for ``CompletePipeline.yml`` - because that is how
	a caller names it in ``uses``; the ``name`` key is kept as :attr:`DisplayName`.
	"""

	_path:        Path                                         #: Path to the workflow file.
	_name:        str                                          #: Name of the workflow, the file's stem.
	_displayName: Nullable[str]                                #: Name of the workflow, as GitHub displays it.
	_triggers:    tuple[str, ...]                              #: Events triggering the workflow.
	_inputs:      dict[str, Input]                             #: Inputs of ``on.workflow_call``, by name.
	_outputs:     dict[str, Output]                            #: Outputs of ``on.workflow_call``, by name.
	_secrets:     dict[str, Secret]                            #: Secrets of ``on.workflow_call``, by name.
	_permissions: Nullable[dict[PermissionScope, Permission]]  #: Permissions the workflow declares, by scope.
	_jobs:        dict[str, Job]                               #: Jobs of the workflow, by name, in file order.

	def __init__(
		self,
		path:        Path,
		displayName: Nullable[str]                  = None,
		triggers:    Nullable[Iterable[str]]        = None,
		inputs:      Nullable[Iterable[Input]]      = None,
		outputs:     Nullable[Iterable[Output]]     = None,
		secrets:     Nullable[Iterable[Secret]]     = None,
		permissions: Nullable[Iterable[Permission]] = None
	) -> None:
		"""
		Initializes a workflow.

		An input, output, secret or permission is attached by passing it, or by constructing it with the workflow as
		parent. The jobs are attached by constructing them with the workflow as parent. Use :meth:`FromFile` to read a
		workflow file.

		:param path:        Path to the workflow file.
		:param displayName: Optional, name of the workflow, as GitHub displays it. Default: ``None``.
		:param triggers:    Optional, events triggering the workflow, as ``workflow_call``. Default: ``None``.
		:param inputs:      Optional, inputs of ``on.workflow_call``, which are attached to the workflow. Default: ``None``.
		:param outputs:     Optional, outputs of ``on.workflow_call``, which are attached to the workflow. Default:
		                    ``None``.
		:param secrets:     Optional, secrets of ``on.workflow_call``, which are attached to the workflow. Default:
		                    ``None``.
		:param permissions: Optional, permissions the workflow declares for all its jobs, which are attached to the
		                    workflow. Default: ``None``, for a workflow without a ``permissions`` key.
		:raises ValueError: If parameter 'path' is ``None``.
		:raises TypeError:  If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises TypeError:  If parameter 'displayName' is not of type :class:`str`.
		:raises TypeError:  If an element of parameter 'triggers' is not of type :class:`str`.
		:raises TypeError:  If an element of parameter 'inputs' is not of type :class:`Input`.
		:raises TypeError:  If an element of parameter 'outputs' is not of type :class:`Output`.
		:raises TypeError:  If an element of parameter 'secrets' is not of type :class:`Secret`.
		:raises TypeError:  If an element of parameter 'permissions' is not of type :class:`Permission`.
		"""
		super().__init__(1)

		if path is None:
			raise ValueError("Parameter 'path' is None.")
		elif not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		if displayName is not None and not isinstance(displayName, str):
			ex = TypeError("Parameter 'displayName' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(displayName)}'.")
			raise ex

		self._workflow =    self
		self._path =        path
		self._name =        path.stem
		self._displayName = displayName
		self._triggers =    ()
		self._inputs =      {}
		self._outputs =     {}
		self._secrets =     {}
		self._permissions = None
		self._jobs =        {}

		if triggers is not None:
			self._triggers = tuple(triggers)
			for trigger in self._triggers:
				if not isinstance(trigger, str):
					ex = TypeError("An element of parameter 'triggers' is not of type 'str'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(trigger)}'.")
					raise ex

		for parameterName, parameters, parameterClass, container in (
			("inputs",  inputs,  Input,  self._inputs),
			("outputs", outputs, Output, self._outputs),
			("secrets", secrets, Secret, self._secrets)
		):
			if parameters is None:
				continue

			for parameter in parameters:
				if not isinstance(parameter, parameterClass):
					ex = TypeError(f"An element of parameter '{parameterName}' is not of type '{parameterClass.__name__}'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(parameter)}'.")
					raise ex

				container[parameter._name] = parameter
				parameter._parent =   self
				parameter._workflow = self

		if permissions is not None:
			self._permissions = {}
			for permission in permissions:
				if not isinstance(permission, Permission):
					ex = TypeError("An element of parameter 'permissions' is not of type 'Permission'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(permission)}'.")
					raise ex

				self._permissions[permission._scope] = permission
				permission._parent =   self
				permission._workflow = self

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the path to the workflow file (:attr:`_path`).

		:returns: The path.
		"""
		return self._path

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the workflow's name, its file's stem (:attr:`_name`).

		:returns: Name of the workflow, as ``CompletePipeline``.
		"""
		return self._name

	@readonly
	def DisplayName(self) -> Nullable[str]:
		"""
		Read-only property to access the workflow's name, as GitHub displays it (:attr:`_displayName`).

		:returns: The ``name`` key, as written, or ``None`` if the workflow gives none.
		"""
		return self._displayName

	@readonly
	def Triggers(self) -> tuple[str, ...]:
		"""
		Read-only property to access the events triggering the workflow (:attr:`_triggers`).

		:returns: The events, as ``workflow_call`` or ``push``, in the order the ``on`` key lists them.
		"""
		return self._triggers

	@readonly
	def IsCallable(self) -> bool:
		"""
		Read-only property to return whether the workflow is a reusable workflow.

		:returns: ``True``, if the workflow is triggered by ``workflow_call``.
		"""
		return "workflow_call" in self._triggers

	@readonly
	def Inputs(self) -> dict[str, Input]:
		"""
		Read-only property to access the inputs of ``on.workflow_call`` (:attr:`_inputs`).

		:returns: The inputs, by name, in file order.
		"""
		return self._inputs

	@readonly
	def Outputs(self) -> dict[str, Output]:
		"""
		Read-only property to access the outputs of ``on.workflow_call`` (:attr:`_outputs`).

		:returns: The outputs, by name, in file order.
		"""
		return self._outputs

	@readonly
	def Secrets(self) -> dict[str, Secret]:
		"""
		Read-only property to access the secrets of ``on.workflow_call`` (:attr:`_secrets`).

		:returns: The secrets, by name, in file order.
		"""
		return self._secrets

	@readonly
	def Permissions(self) -> Nullable[dict[PermissionScope, Permission]]:
		"""
		Read-only property to access the permissions the workflow declares for all its jobs (:attr:`_permissions`).

		:returns: The permissions, by scope, or ``None`` if the workflow has no ``permissions`` key.
		"""
		return self._permissions

	@readonly
	def Jobs(self) -> dict[str, Job]:
		"""
		Read-only property to access the workflow's jobs (:attr:`_jobs`).

		:returns: The jobs, by name, in file order.
		"""
		return self._jobs


	@readonly
	def JobCount(self) -> int:
		"""
		Read-only property to return the number of jobs of the workflow.

		:returns: Number of jobs.
		"""
		return len(self._jobs)

	def ContainsJob(self, name: str) -> bool:
		"""
		Check whether the workflow has a job of that name.

		:param name: Name of the job, the key it is declared under.
		:returns:    ``True``, if the workflow has a job of that name.
		"""
		return name in self._jobs

	def IterateJobs(self) -> Iterator[Job]:
		"""
		Iterate the workflow's jobs.

		:returns: An iterator over the jobs, in file order.
		"""
		return iter(self._jobs.values())

	def __str__(self) -> str:
		"""
		Return the workflow's name.

		:returns: Name of the workflow, the file's stem.
		"""
		return self._name

	@classmethod
	def FromFile(cls, path: Path) -> Self:
		"""
		Read a workflow file.

		:param path:               Path to the workflow file.
		:returns:                  The workflow, with its parameters, permissions and jobs attached.
		:raises ValueError:        If parameter 'path' is ``None``.
		:raises TypeError:         If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises FileNotFoundError: If the file doesn't exist.
		:raises WorkflowError:     If the file is not a YAML document.
		:raises WorkflowError:     If the document is not a mapping, or has no ``on`` or ``jobs`` key.
		:raises WorkflowError:     If a parameter of ``on.workflow_call`` lacks a key GitHub requires, or has a value of
		                           the wrong kind. |br|
		                           For an unknown input type, the note lists the allowed values.
		:raises WorkflowError:     If a job is malformed, needs a job the workflow doesn't have, or the jobs need each
		                           other in a cycle. |br|
		                           For an unknown job, the note lists the workflow's jobs.
		"""
		if path is None:
			raise ValueError("Parameter 'path' is None.")
		elif not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		try:
			document = YAML(typ="rt").load(path.read_text(encoding="utf-8"))
		except YAMLError as cause:
			mark = getattr(cause, "problem_mark", None)
			line = None if mark is None else mark.line + 1
			raise WorkflowError("Workflow file is not a YAML document.", path, line) from cause

		if document is None:
			raise WorkflowError("Workflow file is empty.", path)
		elif not isinstance(document, CommentedMap):
			ex = WorkflowError("Workflow file is not a mapping.", path, 1)
			ex.add_note(f"Got type '{getFullyQualifiedName(document)}'.")
			raise ex
		elif "on" not in document:
			raise WorkflowError("Workflow file has no 'on' key.", path)
		elif "jobs" not in document:
			raise WorkflowError("Workflow file has no 'jobs' key.", path)

		on = document["on"]
		if isinstance(on, str):
			triggers = (on, )
		elif isinstance(on, (CommentedSeq, CommentedMap)):
			triggers = tuple(str(trigger) for trigger in on)
		else:
			ex = WorkflowError("Key 'on' is neither an event, a list nor a mapping.", path, Base._KeyLine(document, "on"))
			ex.add_note(f"Got type '{getFullyQualifiedName(on)}'.")
			raise ex

		parameters: dict[str, list[Parameter]] = {"inputs": [], "outputs": [], "secrets": []}
		if isinstance(on, CommentedMap) and (call := on.get("workflow_call", None)) is not None:
			if not isinstance(call, CommentedMap):
				ex = WorkflowError("Key 'on.workflow_call' is not a mapping.", path, Base._KeyLine(on, "workflow_call"))
				ex.add_note(f"Got type '{getFullyQualifiedName(call)}'.")
				raise ex

			for section, parameterClass in (("inputs", Input), ("outputs", Output), ("secrets", Secret)):
				if (declarations := call.get(section, None)) is None:
					continue
				elif not isinstance(declarations, CommentedMap):
					ex = WorkflowError(f"Key 'on.workflow_call.{section}' is not a mapping.", path, Base._KeyLine(call, section))
					ex.add_note(f"Got type '{getFullyQualifiedName(declarations)}'.")
					raise ex

				parameters[section] = [
					parameterClass._FromYAML(str(name), declaration, path, Base._KeyLine(declarations, name))
					for name, declaration in declarations.items()
				]

		permissions = None
		if "permissions" in document:
			permissions = Permission._FromYAML(document["permissions"], path, Base._KeyLine(document, "permissions"))

		displayName = document.get("name", None)
		workflow = cls(
			path,
			None if displayName is None else str(displayName),
			triggers,
			parameters["inputs"],
			parameters["outputs"],
			parameters["secrets"],
			permissions
		)

		jobs = document["jobs"]
		if not isinstance(jobs, CommentedMap):
			ex = WorkflowError("Key 'jobs' is not a mapping.", path, Base._KeyLine(document, "jobs"))
			ex.add_note(f"Got type '{getFullyQualifiedName(jobs)}'.")
			raise ex

		for name, job in jobs.items():
			line = Base._KeyLine(jobs, name)
			if not isinstance(job, CommentedMap):
				ex = WorkflowError(f"Job '{name}' is not a mapping.", path, line)
				ex.add_note(f"Got type '{getFullyQualifiedName(job)}'.")
				raise ex

			Job._FromYAML(str(name), job, path, line, workflow)

		for job in workflow._jobs.values():
			for need in job._needNames:
				if need not in workflow._jobs:
					ex = WorkflowError(f"Job '{job._name}' needs job '{need}', which the workflow doesn't have.", path, job._line)
					ex.add_note(f"Jobs: {', '.join(workflow._jobs)}.")
					raise ex

		# Depth-first search: a job still on the stack when it is reached again closes a cycle.
		finished: set[str] = set()
		stack:    list[str] = []

		def visit(job: Job) -> None:
			"""
			Nested function for recursion.

			:param job:            The job whose needs are followed.
			:raises WorkflowError: If the job is reached again while its needs are followed.
			"""
			if job._name in finished:
				return
			elif job._name in stack:
				cycle = stack[stack.index(job._name):] + [job._name]
				raise WorkflowError(f"Jobs need each other in a cycle: {' -> '.join(cycle)}.", path, job._line)

			stack.append(job._name)
			for need in job.Needs:
				visit(need)
			stack.pop()
			finished.add(job._name)

		for job in workflow._jobs.values():
			visit(job)

		return workflow


@export
class Job(Base[Workflow]):
	"""
	A job of a workflow.

	A job either runs steps on a runner selected by :attr:`RunsOn`, or calls the reusable workflow named by
	:attr:`Uses`.
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = Workflow  #: A job is contained in a workflow.

	_name:            str                                          #: Name of the job, the key it is declared under.
	_displayName:     Nullable[str]                                #: Name of the job, as GitHub displays it.
	_needNames:       tuple[str, ...]                              #: Names of the jobs this job needs.
	_condition:       Nullable[str]                                #: Condition under which the job runs.
	_permissions:     Nullable[dict[PermissionScope, Permission]]  #: Permissions the job declares, by scope.
	_runsOn:          tuple[str, ...]                              #: Labels selecting the runner.
	_uses:            Nullable[UsesReference]                      #: The reusable workflow the job calls.
	_with:            dict[str, ValueT]                            #: Inputs passed to the called workflow, by name.
	_secrets:         dict[str, str]                               #: Secrets passed to the called workflow, by name.
	_inheritsSecrets: bool                                         #: ``True``, if secrets are inherited.
	_outputs:         dict[str, str]                               #: Outputs of the job, by name.

	def __init__(
		self,
		name:            str,
		line:            int,
		displayName:     Nullable[str]                  = None,
		needs:           Iterable[str]                  = (),
		condition:       Nullable[str]                  = None,
		runsOn:          Iterable[str]                  = (),
		withInputs:      Nullable[Mapping[str, ValueT]] = None,
		secrets:         Nullable[Mapping[str, str]]    = None,
		inheritsSecrets: bool                           = False,
		outputs:         Nullable[Mapping[str, str]]    = None,
		*,
		parent:          Nullable[Workflow]             = None
	) -> None:
		"""
		Initializes a job of a workflow.

		The reusable workflow a job calls and its permissions are attached by constructing a :class:`UsesReference` or a
		:class:`Permission` with the job as parent.

		:param name:            Name of the job, the key it is declared under.
		:param line:            Line the job's name is written at, starting at 1.
		:param displayName:     Optional, name of the job, as GitHub displays it. Default: ``None``.
		:param needs:           Optional, names of the jobs this job needs. Default: ``()``.
		:param condition:       Optional, condition under which the job runs. Default: ``None``.
		:param runsOn:          Optional, labels selecting the runner. Default: ``()``.
		:param withInputs:      Optional, inputs passed to the called workflow, by name. Default: ``None``.
		:param secrets:         Optional, secrets passed to the called workflow, by name. Default: ``None``.
		:param inheritsSecrets: Optional, ``True``, if the called workflow inherits every secret. Default: ``False``.
		:param outputs:         Optional, outputs of the job, by name. Default: ``None``.
		:param parent:          Optional, reference to the workflow containing the job. Default: ``None``.
		:raises ValueError:     If parameter 'name' is ``None``.
		:raises TypeError:      If parameter 'name' is not of type :class:`str`.
		:raises ValueError:     If parameter 'name' is empty.
		:raises TypeError:      If parameter 'displayName' is not of type :class:`str`.
		:raises TypeError:      If parameter 'condition' is not of type :class:`str`.
		:raises TypeError:      If parameter 'inheritsSecrets' is not of type :class:`bool`.
		"""
		super().__init__(line, parent=parent)

		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		for parameterName, value in (("displayName", displayName), ("condition", condition)):
			if value is not None and not isinstance(value, str):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		if not isinstance(inheritsSecrets, bool):
			ex = TypeError("Parameter 'inheritsSecrets' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(inheritsSecrets)}'.")
			raise ex

		self._name =            name
		self._displayName =     displayName
		self._needNames =       tuple(needs)
		self._condition =       condition
		self._permissions =     None
		self._runsOn =          tuple(runsOn)
		self._uses =            None
		self._with =            {} if withInputs is None else dict(withInputs)
		self._secrets =         {} if secrets is None else dict(secrets)
		self._inheritsSecrets = inheritsSecrets
		self._outputs =         {} if outputs is None else dict(outputs)

		if parent is not None:
			parent._jobs[name] = self

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the job's name, the key it is declared under (:attr:`_name`).

		:returns: Name of the job.
		"""
		return self._name

	@readonly
	def DisplayName(self) -> Nullable[str]:
		"""
		Read-only property to access the job's name, as GitHub displays it (:attr:`_displayName`).

		:returns: The ``name`` key, as written, or ``None`` if the workflow gives none.
		"""
		return self._displayName

	@readonly
	def NeedNames(self) -> tuple[str, ...]:
		"""
		Read-only property to access the names of the jobs this job needs (:attr:`_needNames`).

		:returns: The names, in the order the ``needs`` key lists them.
		"""
		return self._needNames

	@readonly
	def Needs(self) -> tuple[Job, ...]:
		"""
		Read-only property to return the jobs this job needs.

		The names in :attr:`NeedNames` are looked up in the workflow containing the job. :meth:`Workflow.FromFile`
		rejects a name naming no job, so for a workflow read from a file every name is resolved.

		:returns: The jobs, in the order the ``needs`` key lists them, skipping names naming no job of the workflow.
		"""
		if self._workflow is None:
			return ()

		jobs = self._workflow._jobs
		return tuple(jobs[name] for name in self._needNames if name in jobs)

	@readonly
	def Condition(self) -> Nullable[str]:
		"""
		Read-only property to access the condition under which the job runs (:attr:`_condition`).

		The expression is not evaluated.

		:returns: The ``if`` expression, as written, or ``None`` if the job has no condition.
		"""
		return self._condition

	@readonly
	def Permissions(self) -> Nullable[dict[PermissionScope, Permission]]:
		"""
		Read-only property to access the permissions the job declares (:attr:`_permissions`).

		:returns: The permissions, by scope, or ``None`` if the job has no ``permissions`` key and inherits them.
		"""
		return self._permissions

	@readonly
	def RunsOn(self) -> tuple[str, ...]:
		"""
		Read-only property to access the labels selecting the runner (:attr:`_runsOn`).

		:returns: The labels, as written - an expression is not evaluated -, or ``()`` for a job calling a workflow.
		"""
		return self._runsOn

	@readonly
	def Uses(self) -> Nullable[UsesReference]:
		"""
		Read-only property to access the reusable workflow the job calls (:attr:`_uses`).

		:returns: The reference, or ``None`` for a job running steps.
		"""
		return self._uses

	@readonly
	def With(self) -> dict[str, ValueT]:
		"""
		Read-only property to access the inputs passed to the called workflow (:attr:`_with`).

		:returns: The inputs, by name.
		"""
		return self._with

	@readonly
	def Secrets(self) -> dict[str, str]:
		"""
		Read-only property to access the secrets passed to the called workflow (:attr:`_secrets`).

		:returns: The secrets, by name, or an empty dictionary if the job passes none or :attr:`InheritsSecrets`.
		"""
		return self._secrets

	@readonly
	def InheritsSecrets(self) -> bool:
		"""
		Read-only property to access whether the called workflow inherits every secret (:attr:`_inheritsSecrets`).

		:returns: ``True``, if the job says ``secrets: inherit``.
		"""
		return self._inheritsSecrets


	@readonly
	def Outputs(self) -> dict[str, str]:
		"""
		Read-only property to access the job's outputs (:attr:`_outputs`).

		:returns: The expressions the outputs are taken from, by name.
		"""
		return self._outputs


	def __str__(self) -> str:
		"""
		Return the job's name.

		:returns: Name of the job.
		"""
		return self._name

	@classmethod
	def _FromYAML(cls, name: str, mapping: CommentedMap, path: Path, line: int, parent: Workflow) -> Self:
		"""
		Build a job and the elements it contains from its mapping in the workflow file.

		:param name:           Name of the job.
		:param mapping:        The job's mapping.
		:param path:           Path to the workflow file.
		:param line:           Line the job's name is written at, starting at 1.
		:param parent:         Reference to the workflow containing the job.
		:returns:              The job.
		:raises WorkflowError: If the job has neither ``runs-on`` nor ``uses``, or both.
		:raises WorkflowError: If a key of the job holds a value of the wrong kind.
		"""
		if ("runs-on" in mapping) == ("uses" in mapping):
			raise WorkflowError(f"Job '{name}' needs either 'runs-on' or 'uses'.", path, line)

		needs = mapping.get("needs", ())
		if isinstance(needs, str):
			needs = (needs, )
		elif not isinstance(needs, (list, tuple)):
			ex = WorkflowError(
				f"Key 'needs' of job '{name}' is neither a job name nor a list.", path, Base._KeyLine(mapping, "needs")
			)
			ex.add_note(f"Got type '{getFullyQualifiedName(needs)}'.")
			raise ex

		runsOn = mapping.get("runs-on", ())
		if isinstance(runsOn, dict):
			runsOn = runsOn.get("labels", ())
		if isinstance(runsOn, str):
			runsOn = (runsOn, )

		condition = mapping.get("if", None)

		secrets = mapping.get("secrets", None)
		inheritsSecrets = secrets == "inherit"
		if inheritsSecrets:
			secrets = None
		elif secrets is not None:
			if not isinstance(secrets, CommentedMap):
				ex = WorkflowError(f"Key 'secrets' of job '{name}' is not a mapping.", path, Base._KeyLine(mapping, "secrets"))
				ex.add_note(f"Got type '{getFullyQualifiedName(secrets)}'.")
				raise ex

			secrets = {str(key): str(value) for key, value in secrets.items()}

		if (outputs := mapping.get("outputs", None)) is not None:
			if not isinstance(outputs, CommentedMap):
				ex = WorkflowError(f"Key 'outputs' of job '{name}' is not a mapping.", path, Base._KeyLine(mapping, "outputs"))
				ex.add_note(f"Got type '{getFullyQualifiedName(outputs)}'.")
				raise ex

			outputs = {str(key): str(value) for key, value in outputs.items()}

		if (withValues := mapping.get("with", None)) is not None:
			if not isinstance(withValues, CommentedMap):
				ex = WorkflowError(f"Key 'with' of job '{name}' is not a mapping.", path, Base._KeyLine(mapping, "with"))
				ex.add_note(f"Got type '{getFullyQualifiedName(withValues)}'.")
				raise ex

			withValues = Base._ToPython(withValues)

		displayName = mapping.get("name", None)

		job = cls(
			name, line,
			displayName=None if displayName is None else str(displayName),
			needs=(str(need) for need in needs),
			condition=None if condition is None else str(condition),
			runsOn=(str(label) for label in runsOn),
			withInputs=withValues,
			secrets=secrets,
			inheritsSecrets=inheritsSecrets,
			outputs=outputs,
			parent=parent
		)

		if "uses" in mapping:
			job._uses = UsesReference._FromYAML(mapping, f"job '{name}'", path, job)

		if "permissions" in mapping:
			job._permissions = {}
			for permission in Permission._FromYAML(mapping["permissions"], path, Base._KeyLine(mapping, "permissions")):
				job._permissions[permission._scope] = permission
				permission._parent =   job
				permission._workflow = job._workflow

		return job


@export
class UsesReference(Base[Job]):
	"""
	The value of a ``uses`` key: a reusable workflow called by a job, or an action run by a step.

	The forms GitHub accepts are read into their parts:

	.. code-block:: text

	   pyTooling/Actions/.github/workflows/Package.yml@r8   repository, path and ref
	   actions/checkout@v6                                   an action in a repository's root
	   ./.github/workflows/Package.yml                       a file of the same repository and commit
	   docker://alpine:3.22                                  a Docker image
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = Job  #: A reference is contained in a job.

	_text:       str            #: The reference, as written.
	_repository: Nullable[str]  #: The repository, as ``owner/repo``.
	_path:       str            #: The path within the repository.
	_ref:        Nullable[str]  #: The branch, tag or commit.
	_isLocal:    bool           #: ``True``, if the reference names a file of the same repository.
	_isDocker:   bool           #: ``True``, if the reference names a Docker image.

	def __init__(self, text: str, line: int, *, parent: Nullable[Job] = None) -> None:
		"""
		Initializes a ``uses`` reference by reading it into its parts.

		:param text:        The reference, as written.
		:param line:        Line the reference is written at, starting at 1.
		:param parent:      Optional, reference to the job containing it. Default: ``None``.
		:raises ValueError: If parameter 'text' is ``None``.
		:raises TypeError:  If parameter 'text' is not of type :class:`str`.
		:raises ValueError: If parameter 'text' is empty.
		:raises ValueError: If parameter 'text' names a repository without a ref.
		:raises ValueError: If parameter 'text' names no repository as ``owner/repo``.
		"""
		super().__init__(line, parent=parent)

		if text is None:
			raise ValueError("Parameter 'text' is None.")
		elif not isinstance(text, str):
			ex = TypeError("Parameter 'text' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(text)}'.")
			raise ex
		elif text == "":
			raise ValueError("Parameter 'text' is empty.")

		self._text =       text
		self._isLocal =    False
		self._isDocker =   False
		self._repository = None
		self._ref =        None

		if text.startswith("docker://"):
			self._isDocker = True
			self._path =     text[len("docker://"):]
		elif text.startswith("./"):
			self._isLocal = True
			self._path =    text[len("./"):]
		else:
			location, separator, ref = text.partition("@")
			if separator == "" or ref == "":
				ex = ValueError("Parameter 'text' names a repository without a ref.")
				ex.add_note(f"Got '{text}'.")
				raise ex

			owner, _, remainder = location.partition("/")
			repository, _, path = remainder.partition("/")
			if owner == "" or repository == "":
				ex = ValueError("Parameter 'text' names no repository as 'owner/repo'.")
				ex.add_note(f"Got '{text}'.")
				raise ex

			self._repository = f"{owner}/{repository}"
			self._path =       path
			self._ref =        ref

	@readonly
	def Repository(self) -> Nullable[str]:
		"""
		Read-only property to access the repository (:attr:`_repository`).

		:returns: The repository, as ``owner/repo``, or ``None`` for a local reference and a Docker image.
		"""
		return self._repository

	@readonly
	def Path(self) -> str:
		"""
		Read-only property to access the path within the repository (:attr:`_path`).

		:returns: The path, as ``.github/workflows/Package.yml``, without the leading ``./`` of a local reference. It
		          is empty for an action in a repository's root, and the image for a Docker image.
		"""
		return self._path

	@readonly
	def Ref(self) -> Nullable[str]:
		"""
		Read-only property to access the branch, tag or commit (:attr:`_ref`).

		:returns: The ref, as ``r8``, or ``None`` for a local reference and a Docker image.
		"""
		return self._ref

	@readonly
	def IsLocal(self) -> bool:
		"""
		Read-only property to access whether the reference names a file of the same repository (:attr:`_isLocal`).

		:returns: ``True``, if the reference starts with ``./``.
		"""
		return self._isLocal

	@readonly
	def IsDocker(self) -> bool:
		"""
		Read-only property to access whether the reference names a Docker image (:attr:`_isDocker`).

		:returns: ``True``, if the reference starts with ``docker://``.
		"""
		return self._isDocker

	@readonly
	def IsWorkflow(self) -> bool:
		"""
		Read-only property to return whether the reference names a reusable workflow rather than an action.

		:returns: ``True``, if the path names a ``.yml`` or ``.yaml`` file in ``.github/workflows``.
		"""
		path = PurePosixPath(self._path)
		return (
			not self._isDocker and path.parent == PurePosixPath(".github/workflows") and path.suffix in (".yml", ".yaml")
		)

	@readonly
	def FileName(self) -> str:
		"""
		Read-only property to return the last element of the path.

		:returns: The file name, as ``Package.yml`` for a reusable workflow, or ``""`` for an action in a repository's
		          root.
		"""
		return PurePosixPath(self._path).name if not self._isDocker else ""

	@readonly
	def Stem(self) -> str:
		"""
		Read-only property to return the file name without its extension.

		For a reusable workflow, it is the name :class:`Workflow` gives the file it reads, e.g. ``Package``.

		:returns: The file name without its extension, or ``""`` for an action in a repository's root.
		"""
		return PurePosixPath(self._path).stem if not self._isDocker else ""

	def __str__(self) -> str:
		"""
		Return the reference, as written.

		:returns: The reference.
		"""
		return self._text

	@classmethod
	def _FromYAML(cls, mapping: CommentedMap, what: str, path: Path, parent: Job) -> Self:
		"""
		Read the ``uses`` key of a job or step.

		:param mapping:        The mapping of the job or step, which has a ``uses`` key.
		:param what:           The job or step, for the exception's message, as ``job 'Build'``.
		:param path:           Path to the workflow file.
		:param parent:         Reference to the job or step.
		:returns:              The reference.
		:raises WorkflowError: If the value is not a reference.
		"""
		line = Base._KeyLine(mapping, "uses")
		try:
			return cls(str(mapping["uses"]), line, parent=parent)
		except ValueError as cause:
			raise WorkflowError(f"Key 'uses' of {what} is not a reference.", path, line) from cause


@export
class Permission(Base[Union[Workflow, Job]]):
	"""
	A permission a workflow or job declares for the ``GITHUB_TOKEN``, as ``contents: write``.

	The short forms ``read-all`` and ``write-all`` are read as one permission of scope :attr:`PermissionScope.All`.
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = (Workflow, Job)  #: A permission is declared by a workflow or a job.

	_scope: PermissionScope  #: The scope, as ``contents``.
	_level: AccessLevel      #: The access granted.

	def __init__(
		self,
		scope:  PermissionScope,
		level:  AccessLevel,
		line:   int,
		*,
		parent: Nullable[Union[Workflow, Job]] = None
	) -> None:
		"""
		Initializes a permission.

		:param scope:       The scope, as ``contents``.
		:param level:       The access granted.
		:param line:        Line the permission is written at, starting at 1.
		:param parent:      Optional, reference to the workflow or job declaring it, which the permission is attached to.
		                    Default: ``None``.
		:raises ValueError: If parameter 'scope' is ``None``.
		:raises TypeError:  If parameter 'scope' is not of type :class:`PermissionScope`.
		:raises ValueError: If parameter 'level' is ``None``.
		:raises TypeError:  If parameter 'level' is not of type :class:`AccessLevel`.
		"""
		super().__init__(line, parent=parent)

		if scope is None:
			raise ValueError("Parameter 'scope' is None.")
		elif not isinstance(scope, PermissionScope):
			ex = TypeError("Parameter 'scope' is not of type 'PermissionScope'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(scope)}'.")
			raise ex

		if level is None:
			raise ValueError("Parameter 'level' is None.")
		elif not isinstance(level, AccessLevel):
			ex = TypeError("Parameter 'level' is not of type 'AccessLevel'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(level)}'.")
			raise ex

		self._scope = scope
		self._level = level

		if parent is not None:
			if parent._permissions is None:
				parent._permissions = {}

			parent._permissions[scope] = self

	@readonly
	def Scope(self) -> PermissionScope:
		"""
		Read-only property to access the scope (:attr:`_scope`).

		:returns: The scope, as :attr:`PermissionScope.Contents`, or :attr:`PermissionScope.All` for ``read-all`` and
		          ``write-all``.
		"""
		return self._scope

	@readonly
	def Level(self) -> AccessLevel:
		"""
		Read-only property to access the access granted (:attr:`_level`).

		:returns: The access level.
		"""
		return self._level

	def __str__(self) -> str:
		"""
		Return the permission, as written in a workflow file.

		:returns: The permission, as ``contents: write``, or ``read-all`` for scope :attr:`PermissionScope.All`.
		"""
		if self._scope is PermissionScope.All:
			return f"{self._level.value}-all"

		return f"{self._scope}: {self._level.value}"

	@classmethod
	def _FromYAML(cls, value: Any, path: Path, line: int) -> list[Self]:
		"""
		Read the value of a ``permissions`` key into the permissions a workflow or job declares.

		:param value:          The value of the ``permissions`` key.
		:param path:           Path to the workflow file.
		:param line:           Line the key is written at, starting at 1.
		:returns:              The permissions, in file order.
		:raises WorkflowError: If the value is neither ``read-all``, ``write-all`` nor a mapping.
		:raises WorkflowError: If a key is not a permission scope. |br|
		                       The note lists the allowed values.
		:raises WorkflowError: If a scope's value is not an access level. |br|
		                       The note lists the allowed values.
		"""
		if value == "read-all":
			return [cls(PermissionScope.All, AccessLevel.Read, line)]
		elif value == "write-all":
			return [cls(PermissionScope.All, AccessLevel.Write, line)]
		elif not isinstance(value, CommentedMap):
			ex = WorkflowError("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", path, line)
			ex.add_note(f"Got '{value}'." if isinstance(value, str) else f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		permissions = []
		for scope, level in value.items():
			scopeLine = Base._KeyLine(value, scope)
			try:
				permissionScope = PermissionScope(scope)
			except ValueError as cause:
				ex = WorkflowError(f"Key '{scope}' of 'permissions' is not a permission scope.", path, scopeLine)
				scopes = (member.value for member in PermissionScope if member is not PermissionScope.All)
				ex.add_note(f"Allowed values: {', '.join(scopes)}.")
				raise ex from cause

			try:
				accessLevel = AccessLevel(level)
			except ValueError as cause:
				ex = WorkflowError(f"Permission '{scope}' is not an access level.", path, scopeLine)
				ex.add_note(f"Got '{level}'.")
				ex.add_note(f"Allowed values: {', '.join(member.value for member in AccessLevel)}.")
				raise ex from cause

			permissions.append(cls(permissionScope, accessLevel, scopeLine))

		return permissions


@export
@abstractclass
class Parameter(Base[Workflow]):
	"""
	Common behaviour of the inputs, outputs and secrets of a reusable workflow.

	Every parameter has a name and an optional description, and belongs to a :class:`Workflow`.
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = Workflow  #: A parameter is declared by a workflow.

	_name:        str            #: Name of the parameter.
	_description: Nullable[str]  #: Description of the parameter.

	def __init__(
		self,
		name:        str,
		line:        int,
		description: Nullable[str]      = None,
		*,
		parent:      Nullable[Workflow] = None
	) -> None:
		"""
		Initializes a parameter of a reusable workflow.

		:param name:        Name of the parameter.
		:param line:        Line the parameter's name is written at, starting at 1.
		:param description: Optional, description of the parameter. Default: ``None``.
		:param parent:      Optional, reference to the workflow declaring it. Default: ``None``.
		:raises ValueError: If parameter 'name' is ``None``.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'description' is not of type :class:`str`.
		"""
		super().__init__(line, parent=parent)

		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if description is not None and not isinstance(description, str):
			ex = TypeError("Parameter 'description' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(description)}'.")
			raise ex

		self._name =        name
		self._description = description

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the parameter's name (:attr:`_name`).

		:returns: Name of the parameter.
		"""
		return self._name

	@readonly
	def Description(self) -> Nullable[str]:
		"""
		Read-only property to access the parameter's description (:attr:`_description`).

		:returns: The description, or ``None`` if the workflow gives none.
		"""
		return self._description

	def __str__(self) -> str:
		"""
		Return the parameter's name.

		:returns: Name of the parameter.
		"""
		return self._name


@export
class Input(Parameter):
	"""An input of a reusable workflow, declared in ``on.workflow_call.inputs``."""

	_type:     InputType  #: Type of the input.
	_required: bool       #: ``True``, if a caller has to pass the input.
	_default:  ValueT     #: Value of the input, if a caller doesn't pass it.

	def __init__(
		self,
		name:        str,
		line:        int,
		inputType:   InputType,
		required:    bool               = False,
		default:     ValueT             = None,
		description: Nullable[str]      = None,
		*,
		parent:      Nullable[Workflow] = None
	) -> None:
		"""
		Initializes an input of a reusable workflow.

		:param name:        Name of the input.
		:param line:        Line the input's name is written at, starting at 1.
		:param inputType:   Type of the input.
		:param required:    Optional, ``True``, if a caller has to pass the input. Default: ``False``.
		:param default:     Optional, value of the input, if a caller doesn't pass it. Default: ``None``.
		:param description: Optional, description of the input. Default: ``None``.
		:param parent:      Optional, reference to the workflow declaring it. Default: ``None``.
		:raises ValueError: If parameter 'inputType' is ``None``.
		:raises TypeError:  If parameter 'inputType' is not of type :class:`InputType`.
		:raises TypeError:  If parameter 'required' is not of type :class:`bool`.
		"""
		super().__init__(name, line, description, parent=parent)

		if inputType is None:
			raise ValueError("Parameter 'inputType' is None.")
		elif not isinstance(inputType, InputType):
			ex = TypeError("Parameter 'inputType' is not of type 'InputType'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(inputType)}'.")
			raise ex

		if not isinstance(required, bool):
			ex = TypeError("Parameter 'required' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(required)}'.")
			raise ex

		self._type =     inputType
		self._required = required
		self._default =  default

		if parent is not None:
			parent._inputs[name] = self

	@readonly
	def Type(self) -> InputType:
		"""
		Read-only property to access the input's type (:attr:`_type`).

		:returns: Type of the input.
		"""
		return self._type

	@readonly
	def Required(self) -> bool:
		"""
		Read-only property to access whether a caller has to pass the input (:attr:`_required`).

		:returns: ``True``, if the input is required.
		"""
		return self._required

	@readonly
	def Default(self) -> ValueT:
		"""
		Read-only property to access the input's value, if a caller doesn't pass it (:attr:`_default`).

		The value keeps the type it is written with, as ``'3.14'`` or ``false``, and a multi-line value keeps its line
		breaks.

		:returns: The default value, or ``None`` if the workflow gives none.
		"""
		return self._default

	@classmethod
	def _FromYAML(cls, name: str, declaration: Any, path: Path, line: int) -> Self:
		"""
		Read an input's declaration below ``on.workflow_call.inputs``.


		:param name:           Name of the input.
		:param declaration:    The declaration.
		:param path:           Path to the workflow file.
		:param line:           Line the input's name is written at, starting at 1.
		:returns:              The input.
		:raises WorkflowError: If the declaration is not a mapping.
		:raises WorkflowError: If key ``required`` is not a boolean.
		:raises WorkflowError: If the declaration has no ``type`` key.
		:raises WorkflowError: If key ``type`` is not an input type. |br|
		                       The note lists the allowed values.
		"""
		if declaration is None:
			raise WorkflowError(f"Input '{name}' has no 'type' key.", path, line)
		elif not isinstance(declaration, CommentedMap):
			ex = WorkflowError(f"Declaration of '{name}' is not a mapping.", path, line)
			ex.add_note(f"Got type '{getFullyQualifiedName(declaration)}'.")
			raise ex

		description = declaration.get("description", None)
		required = Base._ToPython(declaration.get("required", False))
		if not isinstance(required, bool):
			ex = WorkflowError(f"Key 'required' of '{name}' is not a boolean.", path, line)
			ex.add_note(f"Got '{required}'.")
			raise ex

		if (inputType := declaration.get("type", None)) is None:
			raise WorkflowError(f"Input '{name}' has no 'type' key.", path, line)

		try:
			inputType = InputType.Parse(str(inputType))
		except ValueError as cause:
			ex = WorkflowError(f"Key 'type' of input '{name}' is not an input type.", path, line)
			ex.add_note(f"Got '{inputType}'.")
			ex.add_note(f"Allowed values: {', '.join(member.value for member in InputType)}.")
			raise ex from cause

		default = Base._ToPython(declaration.get("default", None))

		return cls(name, line, inputType, required, default, None if description is None else str(description))


@export
class Output(Parameter):
	"""An output of a reusable workflow, declared in ``on.workflow_call.outputs``."""

	_value: str  #: Expression the output's value is taken from.

	def __init__(
		self,
		name:        str,
		line:        int,
		value:       str,
		description: Nullable[str]      = None,
		*,
		parent:      Nullable[Workflow] = None
	) -> None:
		"""
		Initializes an output of a reusable workflow.

		:param name:        Name of the output.
		:param line:        Line the output's name is written at, starting at 1.
		:param value:       Expression the output's value is taken from, as ``${{ jobs.Build.outputs.version }}``.
		:param description: Optional, description of the output. Default: ``None``.
		:param parent:      Optional, reference to the workflow declaring it. Default: ``None``.
		:raises ValueError: If parameter 'value' is ``None``.
		:raises TypeError:  If parameter 'value' is not of type :class:`str`.
		"""
		super().__init__(name, line, description, parent=parent)

		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif not isinstance(value, str):
			ex = TypeError("Parameter 'value' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._value = value

		if parent is not None:
			parent._outputs[name] = self

	@readonly
	def Value(self) -> str:
		"""
		Read-only property to access the expression the output's value is taken from (:attr:`_value`).

		:returns: The expression, as ``${{ jobs.Build.outputs.version }}``.
		"""
		return self._value

	@classmethod
	def _FromYAML(cls, name: str, declaration: Any, path: Path, line: int) -> Self:
		"""
		Read an output's declaration below ``on.workflow_call.outputs``.


		:param name:           Name of the output.
		:param declaration:    The declaration.
		:param path:           Path to the workflow file.
		:param line:           Line the output's name is written at, starting at 1.
		:returns:              The output.
		:raises WorkflowError: If the declaration is not a mapping.
		:raises WorkflowError: If the declaration has no ``value`` key.
		"""
		if declaration is None:
			raise WorkflowError(f"Output '{name}' has no 'value' key.", path, line)
		elif not isinstance(declaration, CommentedMap):
			ex = WorkflowError(f"Declaration of '{name}' is not a mapping.", path, line)
			ex.add_note(f"Got type '{getFullyQualifiedName(declaration)}'.")
			raise ex

		description = declaration.get("description", None)

		if (value := declaration.get("value", None)) is None:
			raise WorkflowError(f"Output '{name}' has no 'value' key.", path, line)

		return cls(name, line, str(value), None if description is None else str(description))


@export
class Secret(Parameter):
	"""A secret of a reusable workflow, declared in ``on.workflow_call.secrets``."""

	_required: bool  #: ``True``, if a caller has to pass the secret.

	def __init__(
		self,
		name:        str,
		line:        int,
		required:    bool               = False,
		description: Nullable[str]      = None,
		*,
		parent:      Nullable[Workflow] = None
	) -> None:
		"""
		Initializes a secret of a reusable workflow.

		:param name:        Name of the secret.
		:param line:        Line the secret's name is written at, starting at 1.
		:param required:    Optional, ``True``, if a caller has to pass the secret. Default: ``False``.
		:param description: Optional, description of the secret. Default: ``None``.
		:param parent:      Optional, reference to the workflow declaring it. Default: ``None``.
		:raises TypeError:  If parameter 'required' is not of type :class:`bool`.
		"""
		super().__init__(name, line, description, parent=parent)

		if not isinstance(required, bool):
			ex = TypeError("Parameter 'required' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(required)}'.")
			raise ex

		self._required = required

		if parent is not None:
			parent._secrets[name] = self

	@readonly
	def Required(self) -> bool:
		"""
		Read-only property to access whether a caller has to pass the secret (:attr:`_required`).

		:returns: ``True``, if the secret is required.
		"""
		return self._required

	@classmethod
	def _FromYAML(cls, name: str, declaration: Any, path: Path, line: int) -> Self:
		"""
		Read a secret's declaration below ``on.workflow_call.secrets``.


		:param name:           Name of the secret.
		:param declaration:    The declaration.
		:param path:           Path to the workflow file.
		:param line:           Line the secret's name is written at, starting at 1.
		:returns:              The secret.
		:raises WorkflowError: If the declaration is not a mapping.
		:raises WorkflowError: If key ``required`` is not a boolean.
		"""
		if declaration is None:
			return cls(name, line)
		elif not isinstance(declaration, CommentedMap):
			ex = WorkflowError(f"Declaration of '{name}' is not a mapping.", path, line)
			ex.add_note(f"Got type '{getFullyQualifiedName(declaration)}'.")
			raise ex

		description = declaration.get("description", None)
		required = Base._ToPython(declaration.get("required", False))
		if not isinstance(required, bool):
			ex = WorkflowError(f"Key 'required' of '{name}' is not a boolean.", path, line)
			ex.add_note(f"Got '{required}'.")
			raise ex

		return cls(name, line, required, None if description is None else str(description))


