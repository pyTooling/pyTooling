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
   +-- Permission           a permission the workflow declares
       +-- Permission       a permission the job declares

Every element knows its parent, the workflow it belongs to, and the line it starts at in the file, so a consumer can
name the place a finding comes from, as ``CompletePipeline.yml:552``.

The model is independent of :mod:`pyTooling.CI.GitHub`, which models a workflow *run* as the REST API reports it.

:raises MissingDependencyError: If the 'github' extra isn't installed.
"""
from __future__            import annotations

from functools             import cached_property
from pathlib               import Path
from typing                import Any, ClassVar, Generic, Iterable, Optional as Nullable, Self, TypeVar, Union

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
	_permissions: Nullable[dict[PermissionScope, Permission]]  #: Permissions the workflow declares, by scope.

	def __init__(
		self,
		path:        Path,
		displayName: Nullable[str] = None,
		triggers:    Iterable[str] = ()
	) -> None:
		"""
		Initializes a workflow.

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
		self._permissions = None

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
	def Permissions(self) -> Nullable[dict[PermissionScope, Permission]]:
		"""
		Read-only property to access the permissions the workflow declares for all its jobs (:attr:`_permissions`).

		:returns: The permissions, by scope, or ``None`` if the workflow has no ``permissions`` key.
		"""
		return self._permissions


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
		:returns:                  The workflow, with its permissions attached.
		:raises ValueError:        If parameter 'path' is ``None``.
		:raises TypeError:         If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises FileNotFoundError: If the file doesn't exist.
		:raises WorkflowError:     If the file is not a YAML document.
		:raises WorkflowError:     If the document is not a mapping, or has no ``on`` or ``jobs`` key.
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

		displayName = document.get("name", None)
		workflow = cls(path, None if displayName is None else str(displayName), triggers)

		if "permissions" in document:
			workflow._permissions = Permission._FromYAML(
				document["permissions"], path, Base._KeyLine(document, "permissions"), workflow
			)

		return workflow


@export
class Permission(Base[Workflow]):
	"""
	A permission a workflow or job declares for the ``GITHUB_TOKEN``, as ``contents: write``.

	The short forms ``read-all`` and ``write-all`` are read as one permission of scope :attr:`PermissionScope.All`.
	"""

	_PARENT_TYPE: ClassVar[ParentTypes] = Workflow  #: A permission is declared by a workflow.

	_scope: PermissionScope  #: The scope, as ``contents``.
	_level: AccessLevel      #: The access granted.

	def __init__(
		self,
		scope:  PermissionScope,
		level:  AccessLevel,
		line:   int,
		*,
		parent: Nullable[Workflow]             = None
	) -> None:
		"""
		Initializes a permission.

		:param scope:       The scope, as ``contents``.
		:param level:       The access granted.
		:param line:        Line the permission is written at, starting at 1.
		:param parent:      Optional, reference to the workflow or job declaring it. Default: ``None``.
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
	def _FromYAML(cls, value: Any, path: Path, line: int, parent: Workflow) -> dict[PermissionScope, Self]:
		"""
		Read the value of a ``permissions`` key into the permissions a workflow or job declares.

		:param value:          The value of the ``permissions`` key.
		:param path:           Path to the workflow file.
		:param line:           Line the key is written at, starting at 1.
		:param parent:         Reference to the workflow or job declaring the permissions.
		:returns:              The permissions, by scope.
		:raises WorkflowError: If the value is neither ``read-all``, ``write-all`` nor a mapping.
		:raises WorkflowError: If a key is not a permission scope. |br|
		                       The note lists the allowed values.
		:raises WorkflowError: If a scope's value is not an access level. |br|
		                       The note lists the allowed values.
		"""
		if value == "read-all":
			return {PermissionScope.All: cls(PermissionScope.All, AccessLevel.Read, line, parent=parent)}
		elif value == "write-all":
			return {PermissionScope.All: cls(PermissionScope.All, AccessLevel.Write, line, parent=parent)}
		elif not isinstance(value, CommentedMap):
			ex = WorkflowError("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", path, line)
			ex.add_note(f"Got '{value}'." if isinstance(value, str) else f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		permissions = {}
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

			permissions[permissionScope] = cls(permissionScope, accessLevel, scopeLine, parent=parent)

		return permissions


