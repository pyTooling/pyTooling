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
       +-- Matrix           the job's 'strategy.matrix'
       +-- Step             a step of the job
           +-- UsesReference    the action the step runs

Every element knows its parent, the workflow it belongs to, and the line it starts at in the file, so a consumer can
name the place a finding comes from, as ``CompletePipeline.yml:552``.

:class:`WorkflowResolver` reads the reusable workflows a job calls, as far as they are in a local directory.

The model is independent of :mod:`pyTooling.CI.GitHub`, which models a workflow *run* as the REST API reports it.
:meth:`Workflow.ToPipeline` builds the pipeline a workflow defines as a :mod:`pyTooling.CI` model, whose
elements link back to the jobs they were built from, and :meth:`Workflow.ApplyNeeds` gives a run the dependencies
its workflow file declares.

:raises MissingDependencyError: If the 'yaml' extra isn't installed.
"""
from __future__            import annotations

from itertools             import product
from json                  import dumps as json_dumps
from pathlib               import Path, PurePosixPath
from typing                import Any, ClassVar, Hashable, Iterable, Iterator, Mapping, Optional as Nullable, Self
from typing                import Union

from pyTooling.CI          import CIError, DependencyMixin, JobGroup, Matrix as CIMatrix, MatrixInstanceMixin
from pyTooling.CI          import MatrixJob as CIMatrixJob, MatrixWorkflow as CIMatrixWorkflow
from pyTooling.CI          import Job as CIJob, Pipeline as CIPipeline, Step as CIStep, Workflow as CIWorkflow
from pyTooling.Common      import getFullyQualifiedName, StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError
from pyTooling.MetaClasses import ExtendedType, abstractclass

try:
	from ruamel.yaml            import YAML, YAMLError
	from ruamel.yaml.comments   import CommentedMap, CommentedSeq
	from ruamel.yaml.scalarbool import ScalarBoolean
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex


__all__ = ["ValueT"]

ValueT = Union[str, bool, int, float, None, list["ValueT"], dict[str, "ValueT"]]
"""A value read from a workflow file, converted to plain Python types."""


@export
class WorkflowError(CIError):
	"""
	Base-exception of all exceptions raised by :mod:`pyTooling.CI.GitHub.Workflow`.

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

	def Rank(self) -> int:
		"""
		Return the member's position in the order of access, so levels can be compared.

		:returns: ``0`` for :attr:`NoAccess`, ``1`` for :attr:`Read`, ``2`` for :attr:`Write`.
		"""
		return list(AccessLevel).index(self)


@export
class InputType(StringEnum):
	"""The type of an input of a reusable workflow."""

	String =  "string"   #: A string.
	Boolean = "boolean"  #: A boolean.
	Number =  "number"   #: A number.


def _toPython(value: Any) -> ValueT:
	"""
	Convert a value read by ``ruamel.yaml`` into plain Python types.

	The round-trip loader returns its own types - :class:`~ruamel.yaml.comments.CommentedMap`, scalar strings keeping
	their quoting style, and booleans derived from :class:`int`. A consumer compares and prints plain values.

	:param value: The value read from the workflow file.
	:returns:     The value as :class:`dict`, :class:`list`, :class:`str`, :class:`bool`, :class:`int`,
	              :class:`float` or ``None``.
	"""
	if isinstance(value, dict):
		return {str(key): _toPython(item) for key, item in value.items()}
	elif isinstance(value, list):
		return [_toPython(item) for item in value]
	elif isinstance(value, (bool, ScalarBoolean)):
		return bool(value)
	elif isinstance(value, str):
		return str(value)
	elif isinstance(value, int):
		return int(value)
	elif isinstance(value, float):
		return float(value)

	return value


def _keyLine(mapping: CommentedMap, key: str) -> int:
	"""
	Return the line a key of a mapping is written at.

	:param mapping: The mapping read from the workflow file.
	:param key:     The key.
	:returns:       The line, starting at 1.
	"""
	return mapping.lc.key(key)[0] + 1


def _expectMapping(value: Any, what: str, path: Path, line: int) -> CommentedMap:
	"""
	Check that a value read from the workflow file is a mapping.

	:param value:          The value read from the workflow file.
	:param what:           The name of the value, for the exception's message.
	:param path:           Path to the workflow file.
	:param line:           Line the value is written at, starting at 1.
	:returns:              The value.
	:raises WorkflowError: If the value is not a mapping. |br|
	                       The note reports the type that was read.
	"""
	if not isinstance(value, CommentedMap):
		ex = WorkflowError(f"{what} is not a mapping.", path, line)
		ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
		raise ex

	return value


def _parsePermissions(
	value:  Any,
	path:   Path,
	line:   int,
	parent: Union[Workflow, Job]
) -> dict[str, Permission]:
	"""
	Read a ``permissions`` key into permissions attached to a workflow or job.

	:param value:          The value of the ``permissions`` key.
	:param path:           Path to the workflow file.
	:param line:           Line the key is written at, starting at 1.
	:param parent:         Reference to the workflow or job declaring the permissions.
	:returns:              The permissions, by scope.
	:raises WorkflowError: If the value is neither ``read-all``, ``write-all`` nor a mapping.
	:raises WorkflowError: If a scope's value is not an access level. |br|
	                       The note lists the allowed values.
	"""
	if isinstance(value, str):
		if value == "read-all":
			return {Permission.ALL_SCOPES: Permission(Permission.ALL_SCOPES, AccessLevel.Read, line, parent=parent)}
		elif value == "write-all":
			return {Permission.ALL_SCOPES: Permission(Permission.ALL_SCOPES, AccessLevel.Write, line, parent=parent)}

		ex = WorkflowError("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", path, line)
		ex.add_note(f"Got '{value}'.")
		raise ex

	mapping = _expectMapping(value, "Key 'permissions'", path, line)
	permissions = {}
	for scope, level in mapping.items():
		scopeLine = _keyLine(mapping, scope)
		try:
			accessLevel = AccessLevel(level)
		except ValueError as cause:
			ex = WorkflowError(f"Permission '{scope}' is not an access level.", path, scopeLine)
			ex.add_note(f"Got '{level}'.")
			ex.add_note(f"Allowed values: {', '.join(member.value for member in AccessLevel)}.")
			raise ex from cause

		permissions[str(scope)] = Permission(str(scope), accessLevel, scopeLine, parent=parent)

	return permissions


@export
@abstractclass
class Base(metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a workflow file.

	Every element knows the element containing it, the workflow it belongs to, and the line it starts at.
	"""

	_parent:   Nullable[Base]      #: Reference to the containing element.
	_workflow: Nullable[Workflow]  #: Reference to the workflow this element belongs to.
	_line:     int                 #: Line the element starts at in the workflow file, starting at 1.

	def __init__(self, line: int, *, parent: Nullable[Base] = None) -> None:
		"""
		Initializes an element of a workflow file.

		:param line:        Line the element starts at in the workflow file, starting at 1.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
		:raises ValueError: If parameter 'line' is ``None``.
		:raises TypeError:  If parameter 'line' is not of type :class:`int`.
		:raises ValueError: If parameter 'line' is not positive.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Base`.
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

		if parent is not None and not isinstance(parent, Base):
			ex = TypeError("Parameter 'parent' is not of type 'Base'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent =   parent
		self._workflow = None if parent is None else parent._workflow
		self._line =     line

	@readonly
	def Parent(self) -> Nullable[Base]:
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


@export
class UsesReference(Base):
	"""
	The value of a ``uses`` key: a reusable workflow called by a job, or an action run by a step.

	The forms GitHub accepts are read into their parts:

	.. code-block:: text

	   pyTooling/Actions/.github/workflows/Package.yml@r8   repository, path and ref
	   actions/checkout@v6                                   an action in a repository's root
	   ./.github/workflows/Package.yml                       a file of the same repository and commit
	   docker://alpine:3.22                                  a Docker image
	"""

	_text:       str            #: The reference, as written.
	_repository: Nullable[str]  #: The repository, as ``owner/repo``.
	_path:       str            #: The path within the repository.
	_ref:        Nullable[str]  #: The branch, tag or commit.
	_isLocal:    bool           #: ``True``, if the reference names a file of the same repository.
	_isDocker:   bool           #: ``True``, if the reference names a Docker image.

	def __init__(self, text: str, line: int, *, parent: Nullable[Union[Job, Step]] = None) -> None:
		"""
		Initializes a ``uses`` reference by reading it into its parts.

		:param text:        The reference, as written.
		:param line:        Line the reference is written at, starting at 1.
		:param parent:      Optional, reference to the job or step containing it. Default: ``None``.
		:raises ValueError: If parameter 'text' is ``None``.
		:raises TypeError:  If parameter 'text' is not of type :class:`str`.
		:raises ValueError: If parameter 'text' is empty.
		:raises ValueError: If parameter 'text' names a repository without a ref.
		:raises ValueError: If parameter 'text' names no repository as ``owner/repo``.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Job` or :class:`Step`.
		"""
		if parent is not None and not isinstance(parent, (Job, Step)):
			ex = TypeError("Parameter 'parent' is not of type 'Job' or 'Step'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

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
			self._path = text[len("docker://"):]
		elif text.startswith("./"):
			self._isLocal = True
			self._path = text[len("./"):]
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


@export
class Permission(Base):
	"""
	A permission a workflow or job declares for the ``GITHUB_TOKEN``, as ``contents: write``.

	The short forms ``read-all`` and ``write-all`` are read as one permission of scope :attr:`ALL_SCOPES`.
	"""

	ALL_SCOPES: ClassVar[str] = "*"  #: Scope of a permission read from ``read-all`` or ``write-all``.

	_scope: str          #: The scope, as ``contents``.
	_level: AccessLevel  #: The access granted.

	def __init__(
		self,
		scope:  str,
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
		:param parent:      Optional, reference to the workflow or job declaring it. Default: ``None``.
		:raises ValueError: If parameter 'scope' is ``None``.
		:raises TypeError:  If parameter 'scope' is not of type :class:`str`.
		:raises ValueError: If parameter 'scope' is empty.
		:raises ValueError: If parameter 'level' is ``None``.
		:raises TypeError:  If parameter 'level' is not of type :class:`AccessLevel`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Workflow` or :class:`Job`.
		"""
		if parent is not None and not isinstance(parent, (Workflow, Job)):
			ex = TypeError("Parameter 'parent' is not of type 'Workflow' or 'Job'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		super().__init__(line, parent=parent)

		if scope is None:
			raise ValueError("Parameter 'scope' is None.")
		elif not isinstance(scope, str):
			ex = TypeError("Parameter 'scope' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(scope)}'.")
			raise ex
		elif scope == "":
			raise ValueError("Parameter 'scope' is empty.")

		if level is None:
			raise ValueError("Parameter 'level' is None.")
		elif not isinstance(level, AccessLevel):
			ex = TypeError("Parameter 'level' is not of type 'AccessLevel'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(level)}'.")
			raise ex

		self._scope = scope
		self._level = level

	@readonly
	def Scope(self) -> str:
		"""
		Read-only property to access the scope (:attr:`_scope`).

		:returns: The scope, as ``contents``, or :attr:`ALL_SCOPES` for ``read-all`` and ``write-all``.
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

		:returns: The permission, as ``contents: write``, or ``read-all`` for scope :attr:`ALL_SCOPES`.
		"""
		if self._scope == self.ALL_SCOPES:
			return f"{self._level.value}-all"

		return f"{self._scope}: {self._level.value}"


@export
@abstractclass
class Parameter(Base):
	"""
	Common behaviour of the inputs, outputs and secrets of a reusable workflow.

	Every parameter has a name and an optional description, and belongs to a :class:`Workflow`.
	"""

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
		:raises TypeError:  If parameter 'parent' is not of type :class:`Workflow`.
		"""
		if parent is not None and not isinstance(parent, Workflow):
			ex = TypeError("Parameter 'parent' is not of type 'Workflow'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

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


@export
class Matrix(Base):
	"""
	The ``strategy.matrix`` of a job.

	A matrix is *dynamic*, if a part of it is an expression - as ``include: ${{ fromJson(inputs.jobs) }}`` - because
	its instances are then known at run time only.
	"""

	_dimensions: dict[str, ValueT]  #: The dimensions, by name.
	_include:    ValueT             #: The combinations added, or an expression producing them.
	_exclude:    ValueT             #: The combinations removed, or an expression producing them.
	_expression: Nullable[str]      #: The expression the whole matrix is taken from.

	def __init__(
		self,
		line:       int,
		dimensions: Nullable[Mapping[str, ValueT]] = None,
		include:    ValueT                         = None,
		exclude:    ValueT                         = None,
		expression: Nullable[str]                  = None,
		*,
		parent:     Nullable[Job]                  = None
	) -> None:
		"""
		Initializes a job's matrix.

		:param line:       Line the ``matrix`` key is written at, starting at 1.
		:param dimensions: Optional, the dimensions, by name; a dimension's value is a list or an expression.
		                   Default: ``None``.
		:param include:    Optional, the combinations added, or an expression producing them. Default: ``None``.
		:param exclude:    Optional, the combinations removed, or an expression producing them. Default: ``None``.
		:param expression: Optional, the expression the whole matrix is taken from. Default: ``None``.
		:param parent:     Optional, reference to the job the matrix belongs to. Default: ``None``.
		:raises TypeError: If parameter 'dimensions' is not a mapping.
		:raises TypeError: If parameter 'expression' is not of type :class:`str`.
		:raises TypeError: If parameter 'parent' is not of type :class:`Job`.
		"""
		if parent is not None and not isinstance(parent, Job):
			ex = TypeError("Parameter 'parent' is not of type 'Job'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		super().__init__(line, parent=parent)

		if dimensions is not None and not isinstance(dimensions, Mapping):
			ex = TypeError("Parameter 'dimensions' is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(dimensions)}'.")
			raise ex

		if expression is not None and not isinstance(expression, str):
			ex = TypeError("Parameter 'expression' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(expression)}'.")
			raise ex

		self._dimensions = {} if dimensions is None else dict(dimensions)
		self._include =    include
		self._exclude =    exclude
		self._expression = expression

	@readonly
	def Dimensions(self) -> dict[str, ValueT]:
		"""
		Read-only property to access the matrix' dimensions (:attr:`_dimensions`).

		:returns: The dimensions, by name; a dimension's value is a list, or an expression producing one.
		"""
		return self._dimensions

	@readonly
	def Include(self) -> ValueT:
		"""
		Read-only property to access the combinations added to the matrix (:attr:`_include`).

		:returns: A list of combinations, an expression producing them, or ``None`` if the matrix has no ``include``.
		"""
		return self._include

	@readonly
	def Exclude(self) -> ValueT:
		"""
		Read-only property to access the combinations removed from the matrix (:attr:`_exclude`).

		:returns: A list of combinations, an expression producing them, or ``None`` if the matrix has no ``exclude``.
		"""
		return self._exclude

	@readonly
	def Expression(self) -> Nullable[str]:
		"""
		Read-only property to access the expression the whole matrix is taken from (:attr:`_expression`).

		:returns: The expression, as ``${{ fromJson(needs.Params.outputs.matrix) }}``, or ``None`` if the matrix is a
		          mapping.
		"""
		return self._expression

	@readonly
	def IsDynamic(self) -> bool:
		"""
		Read-only property to return whether the matrix' instances are known at run time only.

		:returns: ``True``, if the matrix, its ``include``, its ``exclude`` or one of its dimensions is an expression.
		"""
		return (
			self._expression is not None or isinstance(self._include, str) or isinstance(self._exclude, str) or
			any(isinstance(value, str) for value in self._dimensions.values())
		)

	@readonly
	def Combinations(self) -> list[dict[str, ValueT]]:
		"""
		Read-only property to return the combinations the matrix produces, as GitHub computes them.

		The dimensions are combined in the order they are written, the last one varying fastest. Then ``exclude``
		removes every combination matching all key-value pairs of an entry, and ``include`` extends every remaining
		combination whose dimension values the entry doesn't change - its other keys, and those an earlier entry
		added, it may change. An entry extending no combination is a combination of its own.

		:returns:              The combinations, each a mapping of the dimensions' and included keys' names to values.
		:raises WorkflowError: If the matrix is dynamic, so its combinations are known at run time only.
		:raises WorkflowError: If ``include`` or ``exclude`` is not a list of mappings.
		"""
		path = None if self._workflow is None else self._workflow._path
		if self.IsDynamic:
			raise WorkflowError("Matrix is dynamic; its combinations are known at run time only.", path, self._line)

		for key, entries in (("include", self._include), ("exclude", self._exclude)):
			if entries is not None and (
				not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries)
			):
				raise WorkflowError(f"Key '{key}' of the matrix is not a list of mappings.", path, self._line)

		combinations = []
		if len(self._dimensions) > 0:
			dimensions = {name: value if isinstance(value, list) else [value] for name, value in self._dimensions.items()}
			combinations = [dict(zip(dimensions, values)) for values in product(*dimensions.values())]

		if self._exclude is not None:
			for entry in self._exclude:
				combinations = [
					combination for combination in combinations
					if not all(combination.get(key, None) == value for key, value in entry.items())
				]

		if self._include is None:
			return combinations

		originals = [dict(combination) for combination in combinations]
		for entry in self._include:
			extended = False
			for combination, original in zip(combinations, originals):
				if all(original[key] == value for key, value in entry.items() if key in original):
					combination.update(entry)
					extended = True

			if not extended:
				combinations.append(dict(entry))

		return combinations

	@staticmethod
	def _FormatCombination(combination: Mapping[str, ValueT]) -> dict[str, str]:
		"""
		Format the values of a matrix' combination as GitHub prints them in the name of a matrix instance.

		A string is printed as it is, any other value as JSON: ``true``, ``3``, ``{"os": "ubuntu"}``.

		:param combination: The combination, as :attr:`Matrix.Combinations` returns it.
		:returns:           The combination's names and formatted values, in the combination's order.
		"""
		return {
			name: value if isinstance(value, str) else json_dumps(value, separators=(", ", ": "))
			for name, value in combination.items()
		}


@export
class Step(Base):
	"""A step of a job."""

	_name:       Nullable[str]            #: Name of the step.
	_identifier: Nullable[str]            #: Identifier of the step, as referenced by ``steps.<id>``.
	_condition:  Nullable[str]            #: Condition under which the step runs.
	_uses:       Nullable[UsesReference]  #: The action the step runs.
	_run:        Nullable[str]            #: The script the step runs.

	def __init__(
		self,
		line:       int,
		name:       Nullable[str] = None,
		identifier: Nullable[str] = None,
		condition:  Nullable[str] = None,
		run:        Nullable[str] = None,
		*,
		parent:     Nullable[Job] = None
	) -> None:
		"""
		Initializes a step of a job.

		The action a step runs is attached by constructing a :class:`UsesReference` with the step as parent.

		:param line:       Line the step starts at, starting at 1.
		:param name:       Optional, name of the step. Default: ``None``.
		:param identifier: Optional, identifier of the step. Default: ``None``.
		:param condition:  Optional, condition under which the step runs. Default: ``None``.
		:param run:        Optional, the script the step runs. Default: ``None``.
		:param parent:     Optional, reference to the job containing the step. Default: ``None``.
		:raises TypeError: If parameter 'name' is not of type :class:`str`.
		:raises TypeError: If parameter 'identifier' is not of type :class:`str`.
		:raises TypeError: If parameter 'condition' is not of type :class:`str`.
		:raises TypeError: If parameter 'run' is not of type :class:`str`.
		:raises TypeError: If parameter 'parent' is not of type :class:`Job`.
		"""
		if parent is not None and not isinstance(parent, Job):
			ex = TypeError("Parameter 'parent' is not of type 'Job'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		super().__init__(line, parent=parent)

		for parameterName, value in (("name", name), ("identifier", identifier), ("condition", condition), ("run", run)):
			if value is not None and not isinstance(value, str):
				ex = TypeError(f"Parameter '{parameterName}' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		self._name =       name
		self._identifier = identifier
		self._condition =  condition
		self._uses =       None
		self._run =        run

		if parent is not None:
			parent._steps.append(self)

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property to access the step's name (:attr:`_name`).

		:returns: Name of the step, or ``None`` if the workflow gives none.
		"""
		return self._name

	@readonly
	def ID(self) -> Nullable[str]:
		"""
		Read-only property to access the step's identifier (:attr:`_identifier`).

		:returns: Identifier of the step, or ``None`` if the workflow gives none.
		"""
		return self._identifier

	@readonly
	def Condition(self) -> Nullable[str]:
		"""
		Read-only property to access the condition under which the step runs (:attr:`_condition`).

		:returns: The ``if`` expression, as written, or ``None`` if the step always runs.
		"""
		return self._condition

	@readonly
	def Uses(self) -> Nullable[UsesReference]:
		"""
		Read-only property to access the action the step runs (:attr:`_uses`).

		:returns: The action, or ``None`` for a step running a script.
		"""
		return self._uses

	@readonly
	def Run(self) -> Nullable[str]:
		"""
		Read-only property to access the script the step runs (:attr:`_run`).

		:returns: The script, or ``None`` for a step running an action.
		"""
		return self._run


@export
class Job(Base):
	"""
	A job of a workflow.

	A job either runs :attr:`Steps` on a runner selected by :attr:`RunsOn`, or calls the reusable workflow named by
	:attr:`Uses`.
	"""

	_name:            str                              #: Name of the job, the key it is declared under.
	_displayName:     Nullable[str]                    #: Name of the job, as GitHub displays it.
	_needNames:       tuple[str, ...]                  #: Names of the jobs this job needs.
	_condition:       Nullable[str]                    #: Condition under which the job runs.
	_permissions:     Nullable[dict[str, Permission]]  #: Permissions the job declares, by scope.
	_runsOn:          tuple[str, ...]                  #: Labels selecting the runner.
	_uses:            Nullable[UsesReference]          #: The reusable workflow the job calls.
	_with:            dict[str, ValueT]                #: Inputs passed to the called workflow, by name.
	_secrets:         dict[str, str]                   #: Secrets passed to the called workflow, by name.
	_inheritsSecrets: bool                             #: ``True``, if the called workflow inherits every secret.
	_matrix:          Nullable[Matrix]                 #: The job's matrix.
	_steps:           list[Step]                       #: Steps of the job.
	_outputs:         dict[str, str]                   #: Outputs of the job, by name.

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

		The reusable workflow a job calls, its permissions, its matrix and its steps are attached by constructing a
		:class:`UsesReference`, :class:`Permission`, :class:`Matrix` or :class:`Step` with the job as parent.

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
		:raises TypeError:      If parameter 'parent' is not of type :class:`Workflow`.
		"""
		if parent is not None and not isinstance(parent, Workflow):
			ex = TypeError("Parameter 'parent' is not of type 'Workflow'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

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
		self._matrix =          None
		self._steps =           []
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
	def Permissions(self) -> Nullable[dict[str, Permission]]:
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
	def Matrix(self) -> Nullable[Matrix]:
		"""
		Read-only property to access the job's matrix (:attr:`_matrix`).

		:returns: The matrix, or ``None`` if the job has no ``strategy.matrix``.
		"""
		return self._matrix

	@readonly
	def Steps(self) -> list[Step]:
		"""
		Read-only property to access the job's steps (:attr:`_steps`).

		:returns: The steps, in file order, or an empty list for a job calling a workflow.
		"""
		return self._steps

	@readonly
	def Outputs(self) -> dict[str, str]:
		"""
		Read-only property to access the job's outputs (:attr:`_outputs`).

		:returns: The expressions the outputs are taken from, by name.
		"""
		return self._outputs

	def __len__(self) -> int:
		"""
		Return the number of steps of the job.

		:returns: Number of steps.
		"""
		return len(self._steps)

	def __iter__(self) -> Iterator[Step]:
		"""
		Iterate the job's steps.

		:returns: An iterator over the steps, in file order.
		"""
		return iter(self._steps)

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
				f"Key 'needs' of job '{name}' is neither a job name nor a list.", path, _keyLine(mapping, "needs")
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
			secrets = _expectMapping(secrets, f"Key 'secrets' of job '{name}'", path, _keyLine(mapping, "secrets"))
			secrets = {str(key): str(value) for key, value in secrets.items()}

		outputs = mapping.get("outputs", None)
		if outputs is not None:
			outputs = _expectMapping(outputs, f"Key 'outputs' of job '{name}'", path, _keyLine(mapping, "outputs"))
			outputs = {str(key): str(value) for key, value in outputs.items()}

		withValues = mapping.get("with", None)
		if withValues is not None:
			withValues = _expectMapping(withValues, f"Key 'with' of job '{name}'", path, _keyLine(mapping, "with"))
			withValues = _toPython(withValues)

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

		if (uses := mapping.get("uses", None)) is not None:
			try:
				job._uses = UsesReference(str(uses), _keyLine(mapping, "uses"), parent=job)
			except ValueError as cause:
				raise WorkflowError(
					f"Key 'uses' of job '{name}' is not a reference.", path, _keyLine(mapping, "uses")
				) from cause

		if "permissions" in mapping:
			job._permissions = _parsePermissions(mapping["permissions"], path, _keyLine(mapping, "permissions"), job)

		if (strategy := mapping.get("strategy", None)) is not None:
			strategy = _expectMapping(strategy, f"Key 'strategy' of job '{name}'", path, _keyLine(mapping, "strategy"))
			if "matrix" in strategy:
				matrixLine = _keyLine(strategy, "matrix")
				matrix = strategy["matrix"]
				if isinstance(matrix, str):
					job._matrix = Matrix(matrixLine, expression=str(matrix), parent=job)
				else:
					matrix = _expectMapping(matrix, f"Key 'strategy.matrix' of job '{name}'", path, matrixLine)
					job._matrix = Matrix(
						matrixLine,
						dimensions={key: _toPython(value) for key, value in matrix.items() if key not in ("include", "exclude")},
						include=_toPython(matrix.get("include", None)),
						exclude=_toPython(matrix.get("exclude", None)),
						parent=job
					)

		if (steps := mapping.get("steps", None)) is not None:
			if not isinstance(steps, CommentedSeq):
				ex = WorkflowError(f"Key 'steps' of job '{name}' is not a list.", path, _keyLine(mapping, "steps"))
				ex.add_note(f"Got type '{getFullyQualifiedName(steps)}'.")
				raise ex

			for position, step in enumerate(steps):
				stepLine = steps.lc.item(position)[0] + 1
				step = _expectMapping(step, f"Step {position + 1} of job '{name}'", path, stepLine)
				stepName =   step.get("name", None)
				identifier = step.get("id", None)
				condition =  step.get("if", None)
				run =        step.get("run", None)
				stepObject = Step(
					stepLine,
					name=None if stepName is None else str(stepName),
					identifier=None if identifier is None else str(identifier),
					condition=None if condition is None else str(condition),
					run=None if run is None else str(run),
					parent=job
				)
				if (uses := step.get("uses", None)) is not None:
					try:
						stepObject._uses = UsesReference(str(uses), _keyLine(step, "uses"), parent=stepObject)
					except ValueError as cause:
						raise WorkflowError(
							f"Key 'uses' of step {position + 1} of job '{name}' is not a reference.", path, _keyLine(step, "uses")
						) from cause

		return job


@export
class Workflow(Base):
	"""
	A GitHub Actions workflow file.

	The workflow is named by its file's stem - ``CompletePipeline`` for ``CompletePipeline.yml`` - because that is how
	a caller names it in ``uses``; the ``name`` key is kept as :attr:`DisplayName`.
	"""

	_path:        Path                             #: Path to the workflow file.
	_name:        str                              #: Name of the workflow, the file's stem.
	_displayName: Nullable[str]                    #: Name of the workflow, as GitHub displays it.
	_triggers:    tuple[str, ...]                  #: Events triggering the workflow.
	_inputs:      dict[str, Input]                 #: Inputs of ``on.workflow_call``, by name.
	_outputs:     dict[str, Output]                #: Outputs of ``on.workflow_call``, by name.
	_secrets:     dict[str, Secret]                #: Secrets of ``on.workflow_call``, by name.
	_permissions: Nullable[dict[str, Permission]]  #: Permissions the workflow declares, by scope.
	_jobs:        dict[str, Job]                   #: Jobs of the workflow, by name, in file order.

	def __init__(
		self,
		path:        Path,
		displayName: Nullable[str] = None,
		triggers:    Iterable[str] = ()
	) -> None:
		"""
		Initializes a workflow.

		The inputs, outputs, secrets, permissions and jobs are attached by constructing them with the workflow as parent.
		Use :meth:`FromFile` to read a workflow file.

		:param path:        Path to the workflow file.
		:param displayName: Optional, name of the workflow, as GitHub displays it. Default: ``None``.
		:param triggers:    Optional, events triggering the workflow, as ``workflow_call``. Default: ``()``.
		:raises ValueError: If parameter 'path' is ``None``.
		:raises TypeError:  If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises TypeError:  If parameter 'displayName' is not of type :class:`str`.
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
		self._triggers =    tuple(triggers)
		self._inputs =      {}
		self._outputs =     {}
		self._secrets =     {}
		self._permissions = None
		self._jobs =        {}

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
	def Permissions(self) -> Nullable[dict[str, Permission]]:
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

	def ToPipeline(self, resolver: Nullable[WorkflowResolver] = None, depth: Nullable[int] = None) -> DefinedPipeline:
		"""
		Build the service-independent model of the pipeline this workflow defines.

		Every job becomes an element of :mod:`pyTooling.CI`, named by its key and linked to the job by
		:attr:`~DefinitionMixin.Definition`:

		* a job running steps becomes a :class:`DefinedJob`, its steps :class:`DefinedStep`\\ s;
		* a job calling a reusable workflow becomes a :class:`DefinedWorkflow`, holding the elements of the called
		  workflow, if the resolver reads it and the depth allows it;
		* a job with a ``strategy.matrix`` becomes a :class:`DefinedMatrix`, holding a :class:`DefinedMatrixJob` or a
		  :class:`DefinedMatrixWorkflow` per combination of :attr:`Matrix.Combinations`. A dynamic matrix holds no
		  instances, because its combinations are known at run time only.

		The ``needs`` of the jobs become the elements' :attr:`~pyTooling.CI.DependencyMixin.Needs`, so
		:meth:`~pyTooling.CI.Workflow.ToGraph` converts the result into a graph.

		:param resolver:       Optional, the resolver reading the workflows the jobs call. Without it, called workflows
		                       are not expanded. Default: ``None``.
		:param depth:          Optional, how many levels of called workflows to expand; ``0`` expands none, ``None``
		                       every level. Default: ``None``.
		:returns:              The pipeline.
		:raises TypeError:     If parameter 'resolver' is not of type :class:`WorkflowResolver`.
		:raises TypeError:     If parameter 'depth' is not of type :class:`int`.
		:raises ValueError:    If parameter 'depth' is negative.
		:raises WorkflowError: If a workflow to expand doesn't exist, or is not a well-formed workflow.
		:raises WorkflowError: If a workflow to expand calls itself, directly or through others.
		:raises WorkflowError: If ``include`` or ``exclude`` of a matrix is not a list of mappings.
		"""
		if resolver is not None and not isinstance(resolver, WorkflowResolver):
			ex = TypeError("Parameter 'resolver' is not of type 'WorkflowResolver'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolver)}'.")
			raise ex

		if depth is not None and (not isinstance(depth, int) or isinstance(depth, bool)):
			ex = TypeError("Parameter 'depth' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex
		elif depth is not None and depth < 0:
			ex = ValueError("Parameter 'depth' is negative.")
			ex.add_note(f"Got value '{depth}'.")
			raise ex

		def addElements(workflow: Workflow, group: CIWorkflow, level: int, callers: tuple[Workflow, ...]) -> None:
			"""
			Nested function for recursion.

			:param workflow:       The workflow whose jobs become elements.
			:param group:          The group the elements are added to.
			:param level:          How many levels of called workflows are expanded above this one.
			:param callers:        The workflows expanded above this one, this one last.
			:raises WorkflowError: If a workflow to expand calls itself, directly or through others.
			"""
			elements: dict[str, DependencyMixin] = {}
			for job in workflow._jobs.values():
				called = None
				if job._uses is not None and resolver is not None and (depth is None or level < depth):
					called = resolver.Resolve(job._uses)
					if called is not None and any(caller._path.resolve() == called._path.resolve() for caller in callers):
						ex = WorkflowError(f"Workflow '{called._name}' calls itself.", workflow._path, job._uses._line)
						ex.add_note(f"Calls: {' -> '.join(caller._name for caller in (*callers, called))}.")
						raise ex

				if job._matrix is not None:
					element = DefinedMatrix(job, parent=group)
					if not job._matrix.IsDynamic:
						for combination in job._matrix.Combinations:
							dimensions = Matrix._FormatCombination(combination)
							if job._uses is None:
								instance = DefinedMatrixJob(job, dimensions, parent=element)
								for step in job._steps:
									DefinedStep(step, parent=instance)
							else:
								instance = DefinedMatrixWorkflow(job, dimensions, calledWorkflow=called, parent=element)
								if called is not None:
									addElements(called, instance, level + 1, (*callers, called))
				elif job._uses is not None:
					element = DefinedWorkflow(job, calledWorkflow=called, parent=group)
					if called is not None:
						addElements(called, element, level + 1, (*callers, called))
				else:
					element = DefinedJob(job, parent=group)
					for step in job._steps:
						DefinedStep(step, parent=element)

				elements[job._name] = element

			for job in workflow._jobs.values():
				for need in job.Needs:
					elements[job._name].AddNeed(elements[need._name])

		pipeline = DefinedPipeline(self)
		addElements(self, pipeline, 0, (self, ))

		return pipeline

	def ApplyNeeds(self, pipeline: CIWorkflow, resolver: Nullable[WorkflowResolver] = None) -> list[str]:
		"""
		Give a run of this workflow the dependencies its jobs declare with ``needs``.

		A run read from a service's API, as :class:`pyTooling.CI.GitHub.Pipeline`, knows no ``needs``. Each job of this
		workflow is looked up in the run by its display name, or else by its key, and gets as
		:attr:`~pyTooling.CI.DependencyMixin.Needs` the elements the jobs it needs were found as. A job calling
		a reusable workflow is followed into the called workflow of the run - into each instance, if it is a matrix -,
		as far as the resolver reads the called file. A dependency the run's element has already is kept once.

		A job whose display name is an expression, as ``${{ matrix.os }} Tests``, can't be looked up, and is skipped. A
		job with a condition may have been skipped in the run, so it isn't reported when it is missing.

		A run names a matrix instance's dimensions by position, as ``{"0": "ubuntu-26.04", "1": "3.14"}``. If the job
		declares a static matrix, an instance whose values are those of one of :attr:`Matrix.Combinations` gets that
		combination's names, ``{"os": "ubuntu-26.04", "python": "3.14"}``. The instances of a dynamic matrix, and an
		instance matching no combination, keep the positions.

		:param pipeline:                  The run, or a called workflow of a run.
		:param resolver:                  Optional, the resolver reading the workflows the jobs call. Without it, called
		                                  workflows are not followed. Default: ``None``.
		:returns:                         The qualified names of the jobs of this workflow, and of the workflows followed,
		                                  missing in the run - as the run would name them -, in the order they were looked
		                                  up.
		:raises ValueError:               If parameter 'pipeline' is ``None``.
		:raises TypeError:                If parameter 'pipeline' is not of type :class:`pyTooling.CI.Workflow`.
		:raises TypeError:                If parameter 'resolver' is not of type :class:`WorkflowResolver`.
		:raises WorkflowError:            If a workflow to follow doesn't exist, or is not a well-formed workflow.
		:raises WorkflowError:            If ``include`` or ``exclude`` of a matrix is not a list of mappings.
		:raises NeedDependencyCycleError: If the needs of the run, with the needs added, form a cycle.
		"""
		if pipeline is None:
			raise ValueError("Parameter 'pipeline' is None.")
		elif not isinstance(pipeline, CIWorkflow):
			ex = TypeError("Parameter 'pipeline' is not of type 'Workflow'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(pipeline)}'.")
			raise ex

		if resolver is not None and not isinstance(resolver, WorkflowResolver):
			ex = TypeError("Parameter 'resolver' is not of type 'WorkflowResolver'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolver)}'.")
			raise ex

		missing: list[str] = []

		def apply(workflow: Workflow, group: CIWorkflow) -> None:
			"""
			Nested function for recursion.

			:param workflow: The workflow whose jobs are looked up.
			:param group:    The group of the run the jobs are looked up in.
			"""
			elements: dict[str, DependencyMixin] = {}
			for job in workflow._jobs.values():
				if job._displayName is None:
					names = (job._name, )
				elif "${{" in job._displayName:
					continue
				else:
					names = (job._displayName, job._name)

				if (name := next((name for name in names if group.ContainsElement(name)), None)) is None:
					if job._condition is None:
						missing.append(names[0] if isinstance(group, CIPipeline) else f"{group.QualifiedName} / {names[0]}")
					continue

				element = group.GetElement(name)
				elements[job._name] = element
				if job._matrix is not None and not job._matrix.IsDynamic and isinstance(element, CIMatrix):
					combinations = [Matrix._FormatCombination(combination) for combination in job._matrix.Combinations]
					for instance in element.Instances:
						if not isinstance(instance, MatrixInstanceMixin):
							continue

						values = [str(value) for value in instance._dimensions.values()]
						if (names := next((c for c in combinations if list(c.values()) == values), None)) is not None:
							instance._dimensions = dict(zip(names, instance._dimensions.values()))

				if job._uses is None or resolver is None or (called := resolver.Resolve(job._uses)) is None:
					continue
				elif isinstance(element, CIWorkflow):
					apply(called, element)
				elif isinstance(element, CIMatrix):
					for instance in element.Instances:
						if isinstance(instance, CIWorkflow):
							apply(called, instance)

			for job in workflow._jobs.values():
				if (element := elements.get(job._name, None)) is None:
					continue

				for need in job.Needs:
					if (needed := elements.get(need._name, None)) is not None and needed not in element._needs:
						element.AddNeed(needed)

		apply(self, pipeline)
		pipeline.Validate()

		return missing

	def IterateActions(self) -> Iterator[UsesReference]:
		"""
		Iterate the actions the workflow's steps run.

		An action is yielded as often as a step runs it. The reusable workflows the jobs call are in :attr:`Job.Uses`.

		:returns: An iterator over the actions, in file order.
		"""
		for job in self._jobs.values():
			for step in job._steps:
				if step._uses is not None:
					yield step._uses

	def CollectPermissions(self, resolver: Nullable[WorkflowResolver] = None) -> dict[str, Permission]:
		"""
		Collect the permissions the workflow and its jobs declare, and those of the workflows its jobs call.

		A called workflow can keep or reduce the permissions of the ``GITHUB_TOKEN``, never raise them, so what a
		workflow's jobs declare is what a caller has to grant. When several elements declare a scope, the permission
		granting the most access is returned, so its :attr:`~Base.Location` names where that access is asked for.

		:param resolver:   Optional, the resolver reading the workflows the jobs call. Without it, called workflows are
		                   not followed. Default: ``None``.
		:returns:          The permissions, by scope, in the order they are first declared.
		:raises TypeError: If parameter 'resolver' is not of type :class:`WorkflowResolver`.
		"""
		if resolver is not None and not isinstance(resolver, WorkflowResolver):
			ex = TypeError("Parameter 'resolver' is not of type 'WorkflowResolver'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolver)}'.")
			raise ex

		collected: dict[str, Permission] = {}
		visited:   set[int] = set()

		def collect(workflow: Workflow) -> None:
			"""
			Nested function for recursion.

			:param workflow: The workflow whose permissions are collected.
			"""
			visited.add(id(workflow))

			declarations = [] if workflow._permissions is None else [workflow._permissions]
			for job in workflow._jobs.values():
				if job._permissions is not None:
					declarations.append(job._permissions)

			for permissions in declarations:
				for scope, permission in permissions.items():
					if (known := collected.get(scope, None)) is None or permission._level.Rank() > known._level.Rank():
						collected[scope] = permission

			if resolver is not None:
				for job in workflow._jobs.values():
					if job._uses is None or (called := resolver.Resolve(job._uses)) is None:
						continue
					elif id(called) not in visited:
						collect(called)

		collect(self)

		return collected

	def __len__(self) -> int:
		"""
		Return the number of jobs of the workflow.

		:returns: Number of jobs.
		"""
		return len(self._jobs)

	def __contains__(self, name: str) -> bool:
		"""
		Check whether the workflow has a job of that name.

		:param name: Name of the job, the key it is declared under.
		:returns:    ``True``, if the workflow has a job of that name.
		"""
		return name in self._jobs

	def __iter__(self) -> Iterator[Job]:
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

		document = _expectMapping(document, "Workflow file", path, 1)
		if "on" not in document:
			raise WorkflowError("Workflow file has no 'on' key.", path)
		elif "jobs" not in document:
			raise WorkflowError("Workflow file has no 'jobs' key.", path)

		on = document["on"]
		onLine = _keyLine(document, "on")
		if isinstance(on, str):
			triggers = (on, )
		elif isinstance(on, list):
			triggers = tuple(str(trigger) for trigger in on)
		else:
			triggers = tuple(str(trigger) for trigger in _expectMapping(on, "Key 'on'", path, onLine))

		displayName = document.get("name", None)
		workflow = cls(path, None if displayName is None else str(displayName), triggers)

		if isinstance(on, CommentedMap) and (call := on.get("workflow_call", None)) is not None:
			call = _expectMapping(call, "Key 'on.workflow_call'", path, _keyLine(on, "workflow_call"))

			for section in ("inputs", "outputs", "secrets"):
				if (parameters := call.get(section, None)) is None:
					continue

				parameters = _expectMapping(parameters, f"Key 'on.workflow_call.{section}'", path, _keyLine(call, section))
				for name, declaration in parameters.items():
					line = _keyLine(parameters, name)
					declaration = CommentedMap() if declaration is None else declaration
					declaration = _expectMapping(declaration, f"Declaration of '{name}'", path, line)
					description = declaration.get("description", None)
					description = None if description is None else str(description)
					required = _toPython(declaration.get("required", False))
					if not isinstance(required, bool):
						ex = WorkflowError(f"Key 'required' of '{name}' is not a boolean.", path, line)
						ex.add_note(f"Got '{required}'.")
						raise ex

					if section == "inputs":
						if (inputType := declaration.get("type", None)) is None:
							raise WorkflowError(f"Input '{name}' has no 'type' key.", path, line)

						try:
							inputType = InputType.Parse(str(inputType))
						except ValueError as cause:
							ex = WorkflowError(f"Key 'type' of input '{name}' is not an input type.", path, line)
							ex.add_note(f"Got '{inputType}'.")
							ex.add_note(f"Allowed values: {', '.join(member.value for member in InputType)}.")
							raise ex from cause

						default = _toPython(declaration.get("default", None))
						Input(str(name), line, inputType, required, default, description, parent=workflow)
					elif section == "outputs":
						if (value := declaration.get("value", None)) is None:
							raise WorkflowError(f"Output '{name}' has no 'value' key.", path, line)

						Output(str(name), line, str(value), description, parent=workflow)
					else:
						Secret(str(name), line, required, description, parent=workflow)

		if "permissions" in document:
			permissionsLine = _keyLine(document, "permissions")
			workflow._permissions = _parsePermissions(document["permissions"], path, permissionsLine, workflow)

		jobs = _expectMapping(document["jobs"], "Key 'jobs'", path, _keyLine(document, "jobs"))
		for name, job in jobs.items():
			line = _keyLine(jobs, name)
			Job._FromYAML(str(name), _expectMapping(job, f"Job '{name}'", path, line), path, line, workflow)

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
class WorkflowResolver(metaclass=ExtendedType, slots=True):
	"""
	Reads the reusable workflows jobs call, as far as they are in a local directory.

	A repository is mapped to the directory holding its workflow files, so a reference like
	``pyTooling/Actions/.github/workflows/Package.yml@r8`` reads ``Package.yml`` from that directory, whatever its ref.
	A local reference like ``./.github/workflows/Package.yml`` reads the file next to the calling workflow's file.

	Every file is read once; asking for it again returns the same :class:`Workflow`.
	"""

	_repositories: dict[str, Path]       #: Directories holding the workflow files, by repository in lower case.
	_workflows:    dict[Path, Workflow]  #: Workflows already read, by resolved path.

	def __init__(self, repositories: Nullable[Mapping[str, Path]] = None) -> None:
		"""
		Initializes a resolver.

		:param repositories: Optional, directories holding the workflow files, by repository, as
		                     ``{"pyTooling/Actions": Path(".github/workflows")}``. Default: ``None``.
		:raises TypeError:   If parameter 'repositories' is not a mapping.
		:raises TypeError:   If a key of parameter 'repositories' is not of type :class:`str`.
		:raises ValueError:  If a key of parameter 'repositories' is not of the form ``owner/repo``.
		:raises TypeError:   If a value of parameter 'repositories' is not of type :class:`~pathlib.Path`.
		"""
		self._repositories = {}
		self._workflows =    {}

		if repositories is None:
			return
		elif not isinstance(repositories, Mapping):
			ex = TypeError("Parameter 'repositories' is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(repositories)}'.")
			raise ex

		for repository, directory in repositories.items():
			if not isinstance(repository, str):
				ex = TypeError("Key of parameter 'repositories' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(repository)}'.")
				raise ex
			elif repository.count("/") != 1 or repository.startswith("/") or repository.endswith("/"):
				ex = ValueError("Key of parameter 'repositories' is not of the form 'owner/repo'.")
				ex.add_note(f"Got '{repository}'.")
				raise ex
			elif not isinstance(directory, Path):
				ex = TypeError(f"Value of parameter 'repositories' for '{repository}' is not of type 'Path'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(directory)}'.")
				raise ex

			self._repositories[repository.lower()] = directory

	@readonly
	def Repositories(self) -> dict[str, Path]:
		"""
		Read-only property to access the directories holding the workflow files (:attr:`_repositories`).

		:returns: The directories, by repository in lower case.
		"""
		return self._repositories

	def CanResolve(self, uses: UsesReference) -> bool:
		"""
		Return whether a reference names a file the resolver reads: a local one, or one of a mapped repository.

		:param uses:        The reference, as :attr:`Job.Uses`.
		:returns:           ``True``, if the reference is local, or its repository is in :attr:`Repositories`.
		:raises ValueError: If parameter 'uses' is ``None``.
		:raises TypeError:  If parameter 'uses' is not of type :class:`UsesReference`.
		"""
		if uses is None:
			raise ValueError("Parameter 'uses' is None.")
		elif not isinstance(uses, UsesReference):
			ex = TypeError("Parameter 'uses' is not of type 'UsesReference'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(uses)}'.")
			raise ex

		return uses._isLocal or (uses._repository is not None and uses._repository.lower() in self._repositories)

	def Load(self, path: Path) -> Workflow:
		"""
		Read a workflow file, or return it if it was read before.

		:param path:               Path to the workflow file.
		:returns:                  The workflow.
		:raises ValueError:        If parameter 'path' is ``None``.
		:raises TypeError:         If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises FileNotFoundError: If the file doesn't exist.
		:raises WorkflowError:     If the file is not a well-formed workflow.
		"""
		if path is None:
			raise ValueError("Parameter 'path' is None.")
		elif not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		key = path.resolve()
		if (workflow := self._workflows.get(key, None)) is None:
			workflow = Workflow.FromFile(path)
			self._workflows[key] = workflow

		return workflow

	def Resolve(self, uses: UsesReference) -> Nullable[Workflow]:
		"""
		Return the reusable workflow a reference names, if its file is in a local directory.

		:param uses:           The reference, as :attr:`Job.Uses`.
		:returns:              The workflow, or ``None`` if the reference names an action, or a repository without a
		                       directory.
		:raises ValueError:    If parameter 'uses' is ``None``.
		:raises TypeError:     If parameter 'uses' is not of type :class:`UsesReference`.
		:raises ValueError:    If parameter 'uses' is a local reference outside a workflow.
		:raises WorkflowError: If the workflow file doesn't exist in the directory. |br|
		                       The note names the reference's location.
		:raises WorkflowError: If the file is not a well-formed workflow.
		"""
		if uses is None:
			raise ValueError("Parameter 'uses' is None.")
		elif not isinstance(uses, UsesReference):
			ex = TypeError("Parameter 'uses' is not of type 'UsesReference'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(uses)}'.")
			raise ex

		if not uses.IsWorkflow:
			return None
		elif uses._isLocal:
			if uses._workflow is None:
				ex = ValueError("Parameter 'uses' is a local reference outside a workflow.")
				ex.add_note(f"Got '{uses}'.")
				raise ex

			directory = uses._workflow._path.parent
		elif (directory := self._repositories.get(uses._repository.lower(), None)) is None:
			return None

		path = directory / uses.FileName
		if not path.exists():
			ex = WorkflowError(
				f"Workflow '{uses.FileName}' doesn't exist in '{directory}'.",
				None if uses._workflow is None else uses._workflow._path,
				uses._line
			)
			ex.add_note(f"Called as '{uses}'.")
			raise ex

		return self.Load(path)


@export
class DefinitionMixin(metaclass=ExtendedType, mixin=True, expects=("_DEFINITION_TYPE",)):
	"""
	Mixin-class for an element of :mod:`pyTooling.CI` built from a workflow file, linking it to its definition.

	:meth:`Workflow.ToPipeline` builds the elements, so a consumer of the generic model still reaches the facts only
	the file has: the line an element is written at, the reference a job calls, its permissions.
	"""

	_definition: Union[Workflow, Job, Step]  #: The element of the workflow file this element was built from.

	@classmethod
	def _CheckDefinition(cls, definition: Union[Workflow, Job, Step]) -> None:
		"""
		Check a definition before the element is built from it.

		The host class names the element by its definition, so it checks the definition before calling
		``super().__init__()``.

		:param definition:  The element of the workflow file the element is built from.
		:raises ValueError: If parameter 'definition' is ``None``.
		:raises TypeError:  If parameter 'definition' is not of the type the host class declares in
		                    :attr:`_DEFINITION_TYPE`.
		"""
		if definition is None:
			raise ValueError("Parameter 'definition' is None.")
		elif not isinstance(definition, cls._DEFINITION_TYPE):
			ex = TypeError(f"Parameter 'definition' is not of type '{cls._DEFINITION_TYPE.__name__}'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(definition)}'.")
			raise ex

	def __init__(self, definition: Union[Workflow, Job, Step]) -> None:
		"""
		Initializes the link of an element to its definition, which :meth:`_CheckDefinition` checked.

		:param definition: The element of the workflow file this element is built from.
		"""
		self._definition = definition

	@readonly
	def Definition(self) -> Union[Workflow, Job, Step]:
		"""
		Read-only property to access the element of the workflow file this element was built from (:attr:`_definition`).

		:returns: The :class:`Workflow` of a pipeline, the :class:`Job` of a called workflow, a matrix, a matrix instance
		          and a job, or the :class:`Step` of a step.
		"""
		return self._definition


@export
class CallMixin(metaclass=ExtendedType, mixin=True):
	"""Mixin-class for a called workflow built from a workflow file, holding the workflow file it was expanded from."""

	_calledWorkflow: Nullable[Workflow]  #: The workflow file the called workflow's elements were built from.

	def __init__(self, calledWorkflow: Nullable[Workflow] = None) -> None:
		"""
		Initializes the called workflow file.

		:param calledWorkflow: Optional, the workflow file the called workflow's elements are built from. Default:
		                       ``None``.
		:raises TypeError:     If parameter 'calledWorkflow' is not of type :class:`Workflow`.
		"""
		if calledWorkflow is not None and not isinstance(calledWorkflow, Workflow):
			ex = TypeError("Parameter 'calledWorkflow' is not of type 'Workflow'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(calledWorkflow)}'.")
			raise ex

		self._calledWorkflow = calledWorkflow

	@readonly
	def CalledWorkflow(self) -> Nullable[Workflow]:
		"""
		Read-only property to access the workflow file the called workflow was expanded from (:attr:`_calledWorkflow`).

		:returns: The workflow, or ``None`` if the call wasn't expanded - its file isn't at hand, or the depth was used
		          up.
		"""
		return self._calledWorkflow


@export
class DefinedPipeline(CIPipeline, DefinitionMixin):
	"""The pipeline a workflow file defines, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Workflow  #: A pipeline is built from a workflow file.

	def __init__(
		self,
		definition:    Workflow,
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None
	) -> None:
		"""
		Initializes a pipeline built from a workflow file, named by the file's stem.

		:param definition:    The workflow file.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		"""
		self._CheckDefinition(definition)

		super().__init__(definition._name, keyValuePairs=keyValuePairs)
		DefinitionMixin.__init__(self, definition)


@export
class DefinedWorkflow(CIWorkflow, CallMixin, DefinitionMixin):
	"""A called workflow built from the job calling it, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Job  #: A called workflow is built from the job calling it.

	def __init__(
		self,
		definition:     Job,
		*,
		calledWorkflow: Nullable[Workflow]               = None,
		keyValuePairs:  Nullable[Mapping[Hashable, Any]] = None,
		parent:         Nullable[CIWorkflow]             = None
	) -> None:
		"""
		Initializes a called workflow built from the job calling it, named by the job's key.

		The job's ``uses`` is the workflow's :attr:`~pyTooling.CI.Workflow.Reference`, its ``if`` the
		workflow's :attr:`~pyTooling.CI.ConditionMixin.Condition`.

		:param definition:     The job calling the workflow.
		:param calledWorkflow: Optional, the workflow file the called workflow's elements are built from. Default:
		                       ``None``.
		:param keyValuePairs:  Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:         Optional, reference to the workflow containing the call. Default: ``None``.
		:raises ValueError:    If parameter 'definition' calls no workflow.
		"""
		self._CheckDefinition(definition)

		if definition._uses is None:
			ex = ValueError("Parameter 'definition' calls no workflow.")
			ex.add_note(f"Got job '{definition._name}'.")
			raise ex

		super().__init__(
			definition._name, reference=str(definition._uses), condition=definition._condition, keyValuePairs=keyValuePairs,
			parent=parent
		)
		DefinitionMixin.__init__(self, definition)
		CallMixin.__init__(self, calledWorkflow)


@export
class DefinedMatrix(CIMatrix, DefinitionMixin):
	"""
	A matrix built from the job declaring it, as :meth:`Workflow.ToPipeline` builds it.

	A dynamic matrix - see :attr:`Matrix.IsDynamic` - holds no instances, since its combinations are known at run time
	only.
	"""

	_DEFINITION_TYPE: ClassVar[type] = Job  #: A matrix is built from the job declaring it.

	def __init__(
		self,
		definition:    Job,
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[CIWorkflow]             = None
	) -> None:
		"""
		Initializes a matrix built from the job declaring it, named by the job's key.

		:param definition:    The job declaring the matrix.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the workflow containing the matrix. Default: ``None``.
		:raises ValueError:   If parameter 'definition' declares no matrix.
		"""
		self._CheckDefinition(definition)

		if definition._matrix is None:
			ex = ValueError("Parameter 'definition' declares no matrix.")
			ex.add_note(f"Got job '{definition._name}'.")
			raise ex

		super().__init__(definition._name, condition=definition._condition, keyValuePairs=keyValuePairs, parent=parent)
		DefinitionMixin.__init__(self, definition)


@export
class DefinedMatrixWorkflow(CIMatrixWorkflow, CallMixin, DefinitionMixin):
	"""One instance of a matrix calling a reusable workflow, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Job  #: A matrix instance is built from the job declaring the matrix.

	def __init__(
		self,
		definition:     Job,
		dimensions:     Mapping[str, Any],
		*,
		calledWorkflow: Nullable[Workflow]               = None,
		keyValuePairs:  Nullable[Mapping[Hashable, Any]] = None,
		parent:         Nullable[CIMatrix]               = None
	) -> None:
		"""
		Initializes one instance of a matrix calling a reusable workflow, named by the job's key.

		:param definition:     The job declaring the matrix.
		:param dimensions:     The matrix' combination this instance is called with, the values as GitHub prints them.
		:param calledWorkflow: Optional, the workflow file the called workflow's elements are built from. Default:
		                       ``None``.
		:param keyValuePairs:  Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:         Optional, reference to the matrix containing the instance. Default: ``None``.
		:raises ValueError:    If parameter 'definition' calls no workflow.
		:raises ValueError:    If parameter 'dimensions' is ``None``.
		"""
		self._CheckDefinition(definition)

		if definition._uses is None:
			ex = ValueError("Parameter 'definition' calls no workflow.")
			ex.add_note(f"Got job '{definition._name}'.")
			raise ex
		elif dimensions is None:
			raise ValueError("Parameter 'dimensions' is None.")

		super().__init__(
			definition._name, dimensions, reference=str(definition._uses), condition=definition._condition,
			keyValuePairs=keyValuePairs, parent=parent
		)
		DefinitionMixin.__init__(self, definition)
		CallMixin.__init__(self, calledWorkflow)


@export
class DefinedJob(CIJob, DefinitionMixin):
	"""A job running steps, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Job  #: A job is built from its job in the workflow file.

	def __init__(
		self,
		definition:    Job,
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[JobGroup]               = None
	) -> None:
		"""
		Initializes a job built from its job in the workflow file, named by the job's key.

		:param definition:    The job.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the group containing the job. Default: ``None``.
		"""
		self._CheckDefinition(definition)

		super().__init__(definition._name, condition=definition._condition, keyValuePairs=keyValuePairs, parent=parent)
		DefinitionMixin.__init__(self, definition)


@export
class DefinedMatrixJob(CIMatrixJob, DefinitionMixin):
	"""One instance of a matrix running steps, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Job  #: A matrix instance is built from the job declaring the matrix.

	def __init__(
		self,
		definition:    Job,
		dimensions:    Mapping[str, Any],
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[CIMatrix]               = None
	) -> None:
		"""
		Initializes one instance of a matrix running steps, named by the job's key.

		:param definition:    The job declaring the matrix.
		:param dimensions:    The matrix' combination this instance runs with, the values as GitHub prints them.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the matrix containing the instance. Default: ``None``.
		:raises ValueError:   If parameter 'dimensions' is ``None``.
		"""
		self._CheckDefinition(definition)

		if dimensions is None:
			raise ValueError("Parameter 'dimensions' is None.")

		super().__init__(
			definition._name, dimensions, condition=definition._condition, keyValuePairs=keyValuePairs, parent=parent
		)
		DefinitionMixin.__init__(self, definition)


@export
class DefinedStep(CIStep, DefinitionMixin):
	"""A step of a job, as :meth:`Workflow.ToPipeline` builds it."""

	_DEFINITION_TYPE: ClassVar[type] = Step  #: A step is built from its step in the workflow file.

	def __init__(
		self,
		definition:    Step,
		*,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[CIJob]                  = None
	) -> None:
		"""
		Initializes a step built from its step in the workflow file.

		The step is named as GitHub displays it: by its ``name``, or else ``Run`` followed by the action it runs or the
		first line of its script.

		:param definition:    The step.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, reference to the job containing the step. Default: ``None``.
		"""
		self._CheckDefinition(definition)

		if definition._name is not None:
			name = definition._name
		elif definition._uses is not None:
			name = f"Run {definition._uses}"
		elif definition._run is not None:
			firstLine = definition._run.strip().partition("\n")[0]
			name = f"Run {firstLine}"
		else:
			name = f"Step at line {definition._line}"

		super().__init__(name, condition=definition._condition, keyValuePairs=keyValuePairs, parent=parent)
		DefinitionMixin.__init__(self, definition)
