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

Each element knows the element containing it and the line it starts at, and reads its part of the file with a
``_FromYAML()`` class-method:

* :class:`Permission` - a permission for the ``GITHUB_TOKEN``, from a ``permissions`` key.
* :class:`UsesReference` - the value of a ``uses`` key: a reusable workflow a job calls, or an action a step runs.

:raises MissingDependencyError: If the 'github' extra isn't installed.
"""
from __future__            import annotations

from pathlib               import Path, PurePosixPath
from typing                import Any, Optional as Nullable, Self, Union

from pyTooling.CI          import CIError
from pyTooling.Common      import getFullyQualifiedName, StringEnum
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError
from pyTooling.MetaClasses import ExtendedType, abstractclass

try:
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

	def Rank(self) -> int:
		"""
		Return the member's position in the order of access, so levels can be compared.

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
class Base(metaclass=ExtendedType, slots=True):
	"""
	Common behaviour of every element of a workflow file.

	Every element knows the element containing it, and the line it starts at.
	"""

	_parent: Nullable[Base]  #: Reference to the containing element.
	_line:   int             #: Line the element starts at in the workflow file, starting at 1.

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

		self._parent = parent
		self._line =   line

	@readonly
	def Parent(self) -> Nullable[Base]:
		"""
		Read-only property to access the containing element (:attr:`_parent`).

		:returns: The containing element, or ``None``.
		"""
		return self._parent


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

		:returns: The line, as ``line 552``.
		"""
		return f"line {self._line}"

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

	def __init__(self, text: str, line: int, *, parent: Nullable[Base] = None) -> None:
		"""
		Initializes a ``uses`` reference by reading it into its parts.

		:param text:        The reference, as written.
		:param line:        Line the reference is written at, starting at 1.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
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

		For a reusable workflow, it is the name a workflow is given, e.g. ``Package``.

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
	def _FromYAML(cls, mapping: CommentedMap, what: str, path: Path, parent: Base) -> Self:
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
class Permission(Base):
	"""
	A permission a workflow or job declares for the ``GITHUB_TOKEN``, as ``contents: write``.

	The short forms ``read-all`` and ``write-all`` are read as one permission of scope :attr:`PermissionScope.All`.
	"""

	_scope: PermissionScope  #: The scope, as ``contents``.
	_level: AccessLevel      #: The access granted.

	def __init__(
		self,
		scope:  PermissionScope,
		level:  AccessLevel,
		line:   int,
		*,
		parent: Nullable[Base] = None
	) -> None:
		"""
		Initializes a permission.

		:param scope:       The scope, as ``contents``.
		:param level:       The access granted.
		:param line:        Line the permission is written at, starting at 1.
		:param parent:      Optional, reference to the containing element. Default: ``None``.
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
	def _FromYAML(cls, value: Any, path: Path, line: int, parent: Base) -> dict[PermissionScope, Self]:
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


