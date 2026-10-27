# ==================================================================================================================== #
#             _____           _ _               ____                            _                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___ _ __   ___ _ __   __| | ___ _ __   ___ _   _                #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ '_ \ / _ \ '_ \ / _` |/ _ \ '_ \ / __| | | |               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ |_) |  __/ | | | (_| |  __/ | | | (__| |_| |               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___| .__/ \___|_| |_|\__,_|\___|_| |_|\___|\__, |               #
# |_|    |___/                          |___/             |_|                                     |___/                #
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
"""
Resolving requirements into releases of a Python package index.

A :class:`Resolver` selects the newest release matching each requirement, downloads its details and follows its
requirements, as far as its limit allows. The result is a :class:`Resolution`: a tree of :class:`ResolvedRequirement`
objects, each carrying the selected release or the reason there is none. The selected releases are connected in the
index's dependency graph, too.

Importing this module needs the ``dependencies`` extra (:mod:`aiohttp`, :mod:`packaging`), like
:mod:`pyTooling.Dependency.Python`.

:raises MissingDependencyError: If the 'dependencies' extra isn't installed.
"""
from __future__                  import annotations

from asyncio                     import run as asyncio_run, gather as asyncio_gather
from enum                        import Enum
from typing                      import Any, Callable, Iterable, Iterator, Mapping, Optional as Nullable

from pyTooling.Exceptions        import MissingDependencyError

try:
	from aiohttp                   import ClientResponseError, ClientSession, ClientTimeout
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="aiohttp", extra="dependencies") from ex

try:
	from packaging.markers         import default_environment
	from packaging.requirements    import Requirement
	from packaging.specifiers      import SpecifierSet
	from packaging.utils           import canonicalize_name
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="packaging", extra="dependencies") from ex

from pyTooling.Decorators        import export, readonly
from pyTooling.MetaClasses       import ExtendedType
from pyTooling.Common            import StringEnum, getFullyQualifiedName
from pyTooling.Timeout           import Timeout
from pyTooling.Warning           import WarningCollector
from pyTooling.Dependency        import ExtraNotFoundError, PackageIndexFailureWarning, UndeclaredExtraWarning, \
                                        ReleaseNotFoundError, ResolutionTimeoutWarning, UnresolvedRequirementWarning
from pyTooling.Dependency.Python import LazyLoaderState, Project, PyProjectFile, PythonPackageIndex, Release, \
                                        RequirementsFile

_Requirement = Requirement
_Project =     Project
_Release =     Release


@export
class ResolutionStrategy(StringEnum):
	"""When a :class:`Resolver` resolves the requirements of a selected release."""

	Lazy =  "lazy"   #: A release's requirements are resolved when its dependencies are first asked for.
	Eager = "eager"  #: Every requirement up to the limit is resolved up front, one level at a time.

	DEFAULT = Lazy   #: The strategy used if none is given.


@export
class PreReleasePolicy(StringEnum):
	"""
	Whether a :class:`Resolver` selects pre-releases.

	A requirement naming a pre-release (``pyTooling >= 10.0.0rc3``) admits pre-releases with either policy, as does a
	requirement only pre-releases match (:pep:`440`, as :mod:`packaging` and pip apply it).
	"""

	Exclude = "exclude"  #: Pre-releases only if the requirement names one, or if nothing else matches.
	Include = "include"  #: Pre-releases are selected like final releases.

	DEFAULT = Exclude    #: The policy used if none is given.


@export
class ResolutionStatus(Enum):
	"""What resolving a requirement came to."""

	Resolved =           1  #: A release matching the requirement was selected, and its details were downloaded.
	MarkerNotApplying =  2  #: The requirement's environment marker doesn't apply to the resolver's environment.
	UnknownProject =     3  #: The package index doesn't know the required project.
	NoMatchingRelease =  4  #: No release of the project matches the requirement's specifier.
	UndescribedRelease = 5  #: The package index can't describe the selected release.
	Cycle =              6  #: The project is required further up the path already, so it isn't followed again.
	LimitReached =       7  #: The requirement is below the resolver's limit, so it wasn't resolved.
	IndexFailure =       8  #: The package index failed to answer for the project or the selected release.
	TimeoutExpired =     9  #: The current timeout expired before the requirement was resolved.


@export
class ResolvedRequirement(metaclass=ExtendedType, slots=True):
	"""
	A requirement as a :class:`Resolver` resolved it: the selected release, or the reason there is none.

	A resolved requirement's dependencies are the requirements of its release, resolved again. With the strategy
	:attr:`~ResolutionStrategy.Lazy`, they are resolved when :attr:`Dependencies` is first asked for.
	"""

	_resolution:   Resolution                           #: The resolution this requirement belongs to.
	_parent:       Nullable[ResolvedRequirement]        #: The requirement whose release requires this one.
	_requirement:  _Requirement                         #: The requirement as stated.
	_extra:        Nullable[str]                        #: The extra the requirement belongs to, if any.
	_level:        int                                  #: Number of requirements above this one.
	_status:       Nullable[ResolutionStatus]           #: What resolving the requirement came to.
	_project:      Nullable[_Project]                   #: The required project, if the index knows it.
	_release:      Nullable[_Release]                   #: The selected release, if one matches.
	_dependencies: Nullable[list[ResolvedRequirement]]  #: The release's requirements, once resolved.

	def __init__(
		self,
		requirement: Requirement,
		resolution: Resolution,
		*,
		parent: Nullable[ResolvedRequirement] = None,
		extra: Nullable[str] = None
	) -> None:
		"""
		Initializes a requirement to resolve.

		:param requirement: The requirement as stated.
		:param resolution:  The resolution this requirement belongs to.
		:param parent:      Optional, the requirement whose release requires this one. Default: ``None``, a requirement
		                    given to the resolver.
		:param extra:       Optional, the extra the requirement belongs to. Default: ``None``.
		:raises ValueError: If parameter 'requirement' is ``None``.
		:raises TypeError:  If parameter 'requirement' is not of type :class:`~packaging.requirements.Requirement`.
		:raises ValueError: If parameter 'resolution' is ``None``.
		:raises TypeError:  If parameter 'resolution' is not of type :class:`Resolution`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`ResolvedRequirement`.
		:raises TypeError:  If parameter 'extra' is not of type :class:`str`.
		"""
		if requirement is None:
			raise ValueError("Parameter 'requirement' is None.")
		elif not isinstance(requirement, Requirement):
			ex = TypeError("Parameter 'requirement' is not of type 'Requirement'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(requirement)}'.")
			raise ex

		if resolution is None:
			raise ValueError("Parameter 'resolution' is None.")
		elif not isinstance(resolution, Resolution):
			ex = TypeError("Parameter 'resolution' is not of type 'Resolution'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolution)}'.")
			raise ex

		if parent is not None and not isinstance(parent, ResolvedRequirement):
			ex = TypeError("Parameter 'parent' is not of type 'ResolvedRequirement'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if extra is not None and not isinstance(extra, str):
			ex = TypeError("Parameter 'extra' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(extra)}'.")
			raise ex

		self._resolution =   resolution
		self._parent =       parent
		self._requirement =  requirement
		self._extra =        extra
		self._level =        0 if parent is None else parent._level + 1
		self._status =       None
		self._project =      None
		self._release =      None
		self._dependencies = None

	@readonly
	def Requirement(self) -> Requirement:
		"""
		Read-only property to access the requirement as stated (:attr:`_requirement`).

		:returns: The requirement.
		"""
		return self._requirement

	@readonly
	def Parent(self) -> Nullable[ResolvedRequirement]:
		"""
		Read-only property to access the requirement whose release requires this one (:attr:`_parent`).

		:returns: The requiring requirement, or ``None`` for a requirement given to the resolver.
		"""
		return self._parent

	@readonly
	def Extra(self) -> Nullable[str]:
		"""
		Read-only property to access the extra the requirement belongs to (:attr:`_extra`).

		:returns: The extra's name, or ``None`` for an unconditional requirement.
		"""
		return self._extra

	@readonly
	def Level(self) -> int:
		"""
		Read-only property to access the number of requirements above this one (:attr:`_level`).

		:returns: ``0`` for a requirement given to the resolver, ``1`` for a requirement of its release, and so on.
		"""
		return self._level

	@readonly
	def Status(self) -> Nullable[ResolutionStatus]:
		"""
		Read-only property to access what resolving the requirement came to (:attr:`_status`).

		:returns: The status, or ``None`` while the requirement isn't resolved yet.
		"""
		return self._status

	@readonly
	def Project(self) -> Nullable[Project]:
		"""
		Read-only property to access the required project (:attr:`_project`).

		:returns: The project, or ``None`` if the index doesn't know it or it wasn't looked up.
		"""
		return self._project

	@readonly
	def Release(self) -> Nullable[Release]:
		"""
		Read-only property to access the selected release (:attr:`_release`).

		For a requirement closing a cycle, it's the release selected further up the path.

		:returns: The release, or ``None`` if none was selected.
		"""
		return self._release

	@readonly
	def Dependencies(self) -> tuple[ResolvedRequirement, ...]:
		"""
		Read-only property to return the release's requirements, resolved.

		With the strategy :attr:`~ResolutionStrategy.Lazy`, the first access resolves them. Below the resolver's limit,
		they carry the status :attr:`~ResolutionStatus.LimitReached`.

		:returns:                              Tuple of resolved requirements; empty if the requirement wasn't resolved to
		                                       a release, or closes a cycle.
		:raises UnhandledCriticalWarningError: If the dependencies are resolved now, a critical warning (see
		                                       :class:`Resolver`) is reported and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects it.
		"""
		if self._dependencies is None:
			self._resolution._resolver._ResolveDependencies((self, ))

		return tuple(self._dependencies)

	def IterateDependencies(
		self,
		predicate: Nullable[Callable[[ResolvedRequirement], bool]] = None
	) -> Iterator[ResolvedRequirement]:
		"""
		Iterate the release's requirements, resolved.

		:param predicate: Optional, a filter function; only requirements it returns ``True`` for are yielded.
		:returns:         An iterator over the resolved requirements.
		"""
		if predicate is None:
			yield from self.Dependencies
		else:
			for dependency in self.Dependencies:
				if predicate(dependency):
					yield dependency

	def __str__(self) -> str:
		"""
		Return the requirement and what resolving it came to.

		:returns: The requirement, followed by the selected release's version or the status.
		"""
		if self._status is ResolutionStatus.Resolved:
			return f"{self._requirement} -> {self._release.Version}"

		status = "not resolved" if self._status is None else self._status.name
		return f"{self._requirement} ({status})"


@export
class Resolution(metaclass=ExtendedType, slots=True):
	"""
	The result of a :class:`Resolver`: the requirements it was given, resolved, as the roots of a tree.
	"""

	_resolver:     _Resolver                  #: The resolver that created the resolution.
	_requirements: list[ResolvedRequirement]  #: The requirements given to the resolver, resolved.

	def __init__(self, resolver: Resolver) -> None:
		"""
		Initializes an empty resolution.

		:param resolver:    The resolver creating the resolution.
		:raises ValueError: If parameter 'resolver' is ``None``.
		:raises TypeError:  If parameter 'resolver' is not of type :class:`Resolver`.
		"""
		if resolver is None:
			raise ValueError("Parameter 'resolver' is None.")
		elif not isinstance(resolver, Resolver):
			ex = TypeError("Parameter 'resolver' is not of type 'Resolver'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resolver)}'.")
			raise ex

		self._resolver =     resolver
		self._requirements = []

	@readonly
	def Resolver(self) -> Resolver:
		"""
		Read-only property to access the resolver that created the resolution (:attr:`_resolver`).

		:returns: The resolver.
		"""
		return self._resolver

	@readonly
	def Requirements(self) -> tuple[ResolvedRequirement, ...]:
		"""
		Read-only property to return the requirements given to the resolver, resolved (:attr:`_requirements`).

		:returns: Tuple of resolved requirements, in the order they were given.
		"""
		return tuple(self._requirements)

	@readonly
	def RequirementCount(self) -> int:
		"""
		Read-only property to return the number of requirements given to the resolver.

		:returns: Number of requirements.
		"""
		return len(self._requirements)

	def IterateRequirements(
		self,
		predicate: Nullable[Callable[[ResolvedRequirement], bool]] = None
	) -> Iterator[ResolvedRequirement]:
		"""
		Iterate the requirements given to the resolver, resolved.

		:param predicate: Optional, a filter function; only requirements it returns ``True`` for are yielded.
		:returns:         An iterator over the resolved requirements.
		"""
		if predicate is None:
			yield from self._requirements
		else:
			for requirement in self._requirements:
				if predicate(requirement):
					yield requirement


@export
class Resolver(metaclass=ExtendedType, slots=True):
	"""
	Resolves requirements into releases of a Python package index.

	For each requirement, the newest release matching its specifier is selected, and its details are downloaded. Whether
	a pre-release can be selected is the :class:`PreReleasePolicy`; a requirement naming a pre-release selects one with
	either policy. A requirement naming extras (``pyTooling[yaml]``) brings in those extras' requirements as well, and
	their own requirements in turn. The release's requirements are resolved the same way, as deep as the limit allows,
	either up front or when they are first asked for (:class:`ResolutionStrategy`). A project required again further
	up the path closes a cycle and isn't followed. The downloads of one level run in parallel.

	Each requirement keeps what resolving it came to (:class:`ResolutionStatus`): a requirement whose project the index
	doesn't know, or whose selected release it can't describe, is reported as an
	:exc:`~pyTooling.Dependency.UnresolvedRequirementWarning` to a :class:`~pyTooling.Warning.WarningCollector`, and
	stays in the resolution. A server error or a failed connection of the index is reported as a critical
	:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`. The selected releases are connected in the index's
	dependency graph.

	.. important::

	   The critical warnings must be collected by a :class:`~pyTooling.Warning.WarningCollector` up the
	   call-hierarchy, otherwise :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised and resolving
	   stops: :exc:`~pyTooling.Dependency.PackageIndexFailureWarning`,
	   :exc:`~pyTooling.Dependency.ResolutionTimeoutWarning`, :exc:`~pyTooling.Dependency.UnsupportedVersionWarning`
	   (a release whose version can't be parsed) and :exc:`~pyTooling.Dependency.UndeclaredExtraWarning` (a
	   requirement naming an extra the selected release doesn't declare).

	.. attention::

	   It is no installer's solver: every requirement is resolved on its own. Two requirements of the same project with
	   conflicting specifiers select two releases; nothing is backtracked.

	Environment markers are evaluated if an environment is given (a mapping as
	:func:`packaging.markers.default_environment` returns it); a requirement whose marker doesn't apply gets the status
	:attr:`~ResolutionStatus.MarkerNotApplying`. Without an environment, markers aren't evaluated and every requirement
	is resolved. :class:`CurrentEnvironmentResolver` uses the running interpreter's environment.

	Resolving honours the current :class:`~pyTooling.Timeout.Timeout` of the calling thread: each level checks it, and
	the downloads of a level get the time left as their timeout. Requirements not resolved when it expires get the
	status :attr:`~ResolutionStatus.TimeoutExpired`, reported once per level as a critical
	:exc:`~pyTooling.Dependency.ResolutionTimeoutWarning`; the resolution returned is partial. With the strategy
	:attr:`~ResolutionStrategy.Lazy`, a level resolved later uses the timeout current then.
	"""

	_index:       PythonPackageIndex        #: The package index the requirements are resolved against.
	_strategy:    ResolutionStrategy        #: When the requirements of a selected release are resolved.
	_limit:       Nullable[int]             #: Number of levels resolved below the given requirements.
	_preReleases: PreReleasePolicy          #: Whether pre-releases are selected.
	_environment: Nullable[dict[str, str]]  #: Environment markers are evaluated against, if any.
	_undescribed: set[Release]              #: Releases the index couldn't describe.
	_failed:      set[Project | Release]    #: Projects and releases the index failed to answer for.

	def __init__(
		self,
		index: PythonPackageIndex,
		*,
		strategy: ResolutionStrategy = ResolutionStrategy.DEFAULT,
		limit: Nullable[int] = None,
		preReleases: PreReleasePolicy = PreReleasePolicy.DEFAULT,
		environment: Nullable[Mapping[str, str]] = None
	) -> None:
		"""
		Initializes a resolver.

		:param index:       The package index the requirements are resolved against.
		:param strategy:    Optional, when the requirements of a selected release are resolved. Default:
		                    :attr:`~ResolutionStrategy.Lazy`.
		:param limit:       Optional, number of levels resolved below the given requirements; ``0`` resolves only the
		                    given requirements. Default: ``None``, unlimited.
		:param preReleases: Optional, whether pre-releases are selected. Default: :attr:`~PreReleasePolicy.Exclude`.
		:param environment: Optional, the environment markers are evaluated against. Default: ``None``, markers aren't
		                    evaluated.
		:raises ValueError: If parameter 'index' is ``None``.
		:raises TypeError:  If parameter 'index' is not of type :class:`~pyTooling.Dependency.Python.PythonPackageIndex`.
		:raises ValueError: If parameter 'strategy' is ``None``.
		:raises TypeError:  If parameter 'strategy' is not of type :class:`ResolutionStrategy`.
		:raises TypeError:  If parameter 'limit' is not of type :class:`int`.
		:raises ValueError: If parameter 'limit' is negative.
		:raises ValueError: If parameter 'preReleases' is ``None``.
		:raises TypeError:  If parameter 'preReleases' is not of type :class:`PreReleasePolicy`.
		:raises TypeError:  If parameter 'environment' is not a mapping.
		"""
		if index is None:
			raise ValueError("Parameter 'index' is None.")
		elif not isinstance(index, PythonPackageIndex):
			ex = TypeError("Parameter 'index' is not of type 'PythonPackageIndex'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(index)}'.")
			raise ex

		if strategy is None:
			raise ValueError("Parameter 'strategy' is None.")
		elif not isinstance(strategy, ResolutionStrategy):
			ex = TypeError("Parameter 'strategy' is not of type 'ResolutionStrategy'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(strategy)}'.")
			raise ex

		if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool)):
			ex = TypeError("Parameter 'limit' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(limit)}'.")
			raise ex
		elif limit is not None and limit < 0:
			ex = ValueError("Parameter 'limit' is negative.")
			ex.add_note(f"Got value '{limit}'.")
			raise ex

		if preReleases is None:
			raise ValueError("Parameter 'preReleases' is None.")
		elif not isinstance(preReleases, PreReleasePolicy):
			ex = TypeError("Parameter 'preReleases' is not of type 'PreReleasePolicy'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(preReleases)}'.")
			raise ex

		if environment is not None and not isinstance(environment, Mapping):
			ex = TypeError("Parameter 'environment' is not a mapping.")
			ex.add_note(f"Got type '{getFullyQualifiedName(environment)}'.")
			raise ex

		self._index =       index
		self._strategy =    strategy
		self._limit =       limit
		self._preReleases = preReleases
		self._environment = None if environment is None else dict(environment)
		self._undescribed = set()
		self._failed =      set()

	@readonly
	def Index(self) -> PythonPackageIndex:
		"""
		Read-only property to access the package index the requirements are resolved against (:attr:`_index`).

		:returns: The package index.
		"""
		return self._index

	@readonly
	def Strategy(self) -> ResolutionStrategy:
		"""
		Read-only property to access when the requirements of a selected release are resolved (:attr:`_strategy`).

		:returns: The strategy.
		"""
		return self._strategy

	@readonly
	def Limit(self) -> Nullable[int]:
		"""
		Read-only property to access the number of levels resolved below the given requirements (:attr:`_limit`).

		:returns: The limit, or ``None`` for unlimited.
		"""
		return self._limit

	@readonly
	def PreReleases(self) -> PreReleasePolicy:
		"""
		Read-only property to access whether pre-releases are selected (:attr:`_preReleases`).

		:returns: The pre-release policy.
		"""
		return self._preReleases

	@readonly
	def Environment(self) -> Nullable[dict[str, str]]:
		"""
		Read-only property to access the environment markers are evaluated against (:attr:`_environment`).

		:returns: The environment, or ``None`` if markers aren't evaluated.
		"""
		return self._environment

	def ResolveRequirements(self, requirements: Iterable[Requirement]) -> Resolution:
		"""
		Resolve requirements.

		A project required twice is resolved once: the later requirement replaces the earlier one, in the earlier one's
		position.

		:param requirements:                   The requirements to resolve.
		:returns:                              The resolution.
		:raises ValueError:                    If parameter 'requirements' is ``None``.
		:raises TypeError:                     If parameter 'requirements' is not iterable.
		:raises TypeError:                     If an element of parameter 'requirements' is not of type
		                                       :class:`~packaging.requirements.Requirement`.
		:raises UnhandledCriticalWarningError: If a critical warning (see :class:`Resolver`) is reported and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects it.
		"""
		if requirements is None:
			raise ValueError("Parameter 'requirements' is None.")
		elif not isinstance(requirements, Iterable):
			ex = TypeError("Parameter 'requirements' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(requirements)}'.")
			raise ex

		flattened: dict[str, tuple[Requirement, Nullable[str]]] = {}
		for requirement in requirements:
			if not isinstance(requirement, Requirement):
				ex = TypeError("An element of parameter 'requirements' is not of type 'Requirement'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(requirement)}'.")
				raise ex

			flattened[canonicalize_name(requirement.name)] = (requirement, None)

		return self._Resolve(flattened.values())

	def ResolveRequirementsFile(self, requirementsFile: RequirementsFile) -> Resolution:
		"""
		Resolve what a requirements file and the files it references require.

		The requirements are taken from :attr:`~pyTooling.Dependency.Python.RequirementsFile.AllRequirements`, so the
		nearer statement of a project wins.

		:param requirementsFile:               The requirements file, e.g. read by
		                                       :meth:`~pyTooling.Dependency.Python.RequirementsFile.Parse`.
		:returns:                              The resolution.
		:raises ValueError:                    If parameter 'requirementsFile' is ``None``.
		:raises TypeError:                     If parameter 'requirementsFile' is not of type
		                                       :class:`~pyTooling.Dependency.Python.RequirementsFile`.
		:raises UnhandledCriticalWarningError: If a critical warning (see :class:`Resolver`) is reported and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects it.
		"""
		if requirementsFile is None:
			raise ValueError("Parameter 'requirementsFile' is None.")
		elif not isinstance(requirementsFile, RequirementsFile):
			ex = TypeError("Parameter 'requirementsFile' is not of type 'RequirementsFile'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(requirementsFile)}'.")
			raise ex

		return self.ResolveRequirements(requirementsFile.AllRequirements)

	def ResolvePyProjectFile(self, pyProjectFile: PyProjectFile) -> Resolution:
		"""
		Resolve the build requirements of a ``pyproject.toml`` file.

		The requirements are taken from :attr:`~pyTooling.Dependency.Python.PyProjectFile.BuildRequirements`.

		:param pyProjectFile:                  The ``pyproject.toml`` file, e.g. read by
		                                       :meth:`~pyTooling.Dependency.Python.PyProjectFile.Parse`.
		:returns:                              The resolution.
		:raises ValueError:                    If parameter 'pyProjectFile' is ``None``.
		:raises TypeError:                     If parameter 'pyProjectFile' is not of type
		                                       :class:`~pyTooling.Dependency.Python.PyProjectFile`.
		:raises UnhandledCriticalWarningError: If a critical warning (see :class:`Resolver`) is reported and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects it.
		"""
		if pyProjectFile is None:
			raise ValueError("Parameter 'pyProjectFile' is None.")
		elif not isinstance(pyProjectFile, PyProjectFile):
			ex = TypeError("Parameter 'pyProjectFile' is not of type 'PyProjectFile'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(pyProjectFile)}'.")
			raise ex

		return self.ResolveRequirements(pyProjectFile.BuildRequirements)

	def ResolvePackages(self, packages: Iterable[tuple[str, Nullable[str]]]) -> Resolution:
		"""
		Resolve what the newest releases of packages require, or the requirements of one of their extras.

		The newest release is the newest one the :class:`PreReleasePolicy` admits.

		The packages' requirements are flattened in the order the packages are given, a later package's requirement of a
		project replacing an earlier one's.

		:param packages:                       Pairs of a package name and an extra's name, or ``None`` for the package's
		                                       own requirements.
		:returns:                              The resolution.
		:raises ValueError:                    If parameter 'packages' is ``None``.
		:raises TypeError:                     If parameter 'packages' is not iterable.
		:raises TypeError:                     If an element of parameter 'packages' is not a pair of a :class:`str` and an
		                                       optional :class:`str`.
		:raises ProjectNotFoundError:          If the index doesn't know a package.
		:raises ReleaseNotFoundError:          If a package has no release.
		:raises ReleaseNotFoundError:          If the index can't describe a package's newest release.
		:raises ExtraNotFoundError:            If a package's newest release doesn't declare the extra.
		:raises UnhandledCriticalWarningError: If a critical warning (see :class:`Resolver`) is reported and no
		                                       :class:`~pyTooling.Warning.WarningCollector` collects it.
		"""
		if packages is None:
			raise ValueError("Parameter 'packages' is None.")
		elif not isinstance(packages, Iterable):
			ex = TypeError("Parameter 'packages' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(packages)}'.")
			raise ex

		flattened: dict[str, tuple[Requirement, Nullable[str]]] = {}
		for package in packages:
			if (
				not isinstance(package, tuple) or len(package) != 2 or not isinstance(package[0], str)
				or (package[1] is not None and not isinstance(package[1], str))
			):
				ex = TypeError("An element of parameter 'packages' is not a pair of a 'str' and an optional 'str'.")
				ex.add_note(f"Got '{package!r}'.")
				raise ex

			packageName, extra = package
			if (release := self._SelectRelease(self._index.DownloadProject(packageName), SpecifierSet())) is None:
				raise ReleaseNotFoundError(f"Package '{packageName}' has no release.", projectName=packageName)

			declared = {canonicalize_name(name): name for name in release.Requirements if name is not None}
			if extra is None:
				requirements = release.Requirements[None]
			elif (declaredExtra := declared.get(canonicalize_name(extra), None)) is not None:
				requirements = release.Requirements[declaredExtra]
			else:
				ex = ExtraNotFoundError(
					f"Package '{packageName}' has no extra '{extra}'.",
					projectName=packageName,
					version=release.Version,
					extra=extra
				)
				ex.add_note(f"Known are: {', '.join(sorted(declared.values())) or 'none'}.")
				raise ex

			for requirement in requirements:
				flattened[canonicalize_name(requirement.name)] = (requirement, extra)

		return self._Resolve(flattened.values())

	def _Resolve(self, requirements: Iterable[tuple[Requirement, Nullable[str]]]) -> Resolution:
		"""
		Resolve the given requirements and, with the strategy :attr:`~ResolutionStrategy.Eager`, everything below them.

		:param requirements: Pairs of a requirement and the extra it belongs to.
		:returns:            The resolution.
		"""
		resolution = Resolution(self)
		for requirement, extra in requirements:
			resolution._requirements.append(ResolvedRequirement(requirement, resolution, extra=extra))

		self._ResolveLevel(resolution._requirements)

		if self._strategy is ResolutionStrategy.Eager:
			level = resolution._requirements
			while len(level) > 0:
				self._ResolveDependencies(level)
				level = [dependency for requirement in level for dependency in requirement._dependencies]

		return resolution

	def _ResolveDependencies(self, requirements: Iterable[ResolvedRequirement]) -> None:
		"""
		Create the dependencies of resolved requirements and resolve them, all downloads together.

		A release's dependencies are its unconditional requirements, followed by the requirements of each extra the
		requirement names (``pyTooling[yaml]``). An extra the release doesn't declare is reported as a
		:exc:`~pyTooling.Dependency.UndeclaredExtraWarning`.

		:param requirements: Requirements resolved already, whose dependencies aren't created yet.
		"""
		dependencies: list[ResolvedRequirement] = []
		for requirement in requirements:
			requirement._dependencies = []
			if requirement._status is not ResolutionStatus.Resolved:
				continue

			release =  requirement._release
			declared = {canonicalize_name(extra): extra for extra in release.Requirements if extra is not None}
			groups: list[tuple[Nullable[str], list[Requirement]]] = [(None, release.Requirements[None])]
			for extra in sorted(requirement._requirement.extras):
				if (declaredExtra := declared.get(canonicalize_name(extra), None)) is None:
					WarningCollector.Raise(UndeclaredExtraWarning(
						f"Requirement '{requirement._requirement}' names extra '{extra}', which release '{release.Version}' of "
						f"package '{release.Package.Name}' doesn't declare.",
						requirement=requirement,
						extra=extra,
						release=release
					))
					continue

				groups.append((declaredExtra, release.Requirements[declaredExtra]))

			for extra, group in groups:
				for dependency in group:
					resolvedDependency = ResolvedRequirement(dependency, requirement._resolution, parent=requirement, extra=extra)
					requirement._dependencies.append(resolvedDependency)
					dependencies.append(resolvedDependency)

		self._ResolveLevel(dependencies)

	def _ResolveLevel(self, requirements: list[ResolvedRequirement]) -> None:
		"""
		Resolve requirements: check marker, cycle and limit, then look up the projects and describe the selected
		releases, the downloads of each step in parallel.

		:param requirements: The requirements to resolve.
		"""
		toLookUp: list[ResolvedRequirement] = []
		for requirement in requirements:
			if self._environment is not None and requirement._requirement.marker is not None:
				environment = dict(self._environment)
				environment["extra"] = requirement._extra if requirement._extra is not None else ""
				if not requirement._requirement.marker.evaluate(environment):
					requirement._status = ResolutionStatus.MarkerNotApplying
					continue

			name = canonicalize_name(requirement._requirement.name)
			ancestor = requirement._parent
			while ancestor is not None and canonicalize_name(ancestor._requirement.name) != name:
				ancestor = ancestor._parent

			if ancestor is not None:
				requirement._status =  ResolutionStatus.Cycle
				requirement._project = ancestor._project
				requirement._release = ancestor._release
				requirement._parent._release.AddDependencyToPackageVersion(ancestor._release)
			elif self._limit is not None and requirement._level > self._limit:
				requirement._status = ResolutionStatus.LimitReached
			else:
				toLookUp.append(requirement)

		if Timeout.IsExpired():
			self._ExpireRequirements(toLookUp)
			return

		timedOutProjects = self._LookUpProjects(toLookUp)

		toDescribe: list[ResolvedRequirement] = []
		timedOut:   list[ResolvedRequirement] = []
		for requirement in toLookUp:
			if requirement._project in timedOutProjects:
				requirement._project = None
				timedOut.append(requirement)
				continue
			elif requirement._project is None:
				requirement._status = ResolutionStatus.UnknownProject
				WarningCollector.Raise(UnresolvedRequirementWarning(
					f"Package '{requirement._requirement.name}' is unknown to the package index.",
					projectName=requirement._requirement.name
				))
				continue

			if requirement._project in self._failed:
				requirement._status = ResolutionStatus.IndexFailure
				continue

			if (release := self._SelectRelease(requirement._project, requirement._requirement.specifier)) is None:
				requirement._status = ResolutionStatus.NoMatchingRelease
				continue

			requirement._release = release
			toDescribe.append(requirement)

		timedOutReleases = self._DescribeReleases(toDescribe)

		for requirement in toDescribe:
			if requirement._release in timedOutReleases:
				requirement._release = None
				timedOut.append(requirement)
				continue
			elif requirement._release in self._failed:
				requirement._status = ResolutionStatus.IndexFailure
				continue
			elif requirement._release in self._undescribed:
				requirement._status = ResolutionStatus.UndescribedRelease
				WarningCollector.Raise(UnresolvedRequirementWarning(
					f"The package index can't describe release '{requirement._release.Version}' of package "
					f"'{requirement._project.Name}'.",
					projectName=requirement._project.Name,
					version=requirement._release.Version
				))
				continue

			requirement._status = ResolutionStatus.Resolved
			if (parent := requirement._parent) is not None:
				parent._release.AddDependencyToPackageVersion(requirement._release)

		if len(timedOut) > 0:
			self._ExpireRequirements(timedOut)

	def _ExpireRequirements(self, requirements: list[ResolvedRequirement]) -> None:
		"""
		Give requirements the status :attr:`~ResolutionStatus.TimeoutExpired` and report them as one critical
		:exc:`~pyTooling.Dependency.ResolutionTimeoutWarning`.

		:param requirements: The requirements the expired timeout left unresolved.
		"""
		if len(requirements) == 0:
			return

		for requirement in requirements:
			requirement._status = ResolutionStatus.TimeoutExpired

		seconds = Timeout.Current().Seconds
		WarningCollector.Raise(ResolutionTimeoutWarning(
			f"Timeout of {seconds} seconds expired; {len(requirements)} requirements weren't resolved.",
			seconds=seconds,
			projectNames=(requirement._requirement.name for requirement in requirements)
		))

	def _LookUpProjects(self, requirements: list[ResolvedRequirement]) -> set[Project]:
		"""
		Look up the required projects on the index, downloading those not loaded yet in parallel.

		A project the index answers ``404 Not Found`` for is forgotten by the index and left ``None``. A project the index
		fails to answer for is remembered as failed and reported as a critical
		:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`. A download the current timeout cut off is neither: the
		project stays unloaded, so a later resolution asks for it again.

		:param requirements: The requirements whose project is looked up.
		:returns:            The projects whose download the current timeout cut off.
		"""
		toDownload: dict[str, Project] = {}
		for requirement in requirements:
			name = requirement._requirement.name
			if canonicalize_name(name) in self._index._unknownProjects:
				continue

			project = self._index.DownloadProject(name, LazyLoaderState.Initialized)
			if project not in self._failed and project.__lazy_state__ < LazyLoaderState.PartiallyLoaded:
				toDownload[canonicalize_name(name)] = project

		timedOut: set[Project] = set()
		projects = list(toDownload.values())
		documents = self._Download([project._GetPyPIEndpoint() for project in projects])
		for project, document in zip(projects, documents):
			if isinstance(document, TimeoutError) and Timeout.Current() is not None:
				timedOut.add(project)
			elif isinstance(document, BaseException):
				self._failed.add(project)
				WarningCollector.Raise(
					PackageIndexFailureWarning(
						f"Package index failed to answer for package '{project.Name}': {document}",
						projectName=project.Name,
						statusCode=document.status if isinstance(document, ClientResponseError) else None
					),
					document
				)
			elif document is None:
				self._index._ForgetProject(project)
			else:
				project.UpdateDetailsFromPyPIJSON(document)

		for requirement in requirements:
			requirement._project = self._index._projectCache.get(canonicalize_name(requirement._requirement.name), None)

		return timedOut

	def _DescribeReleases(self, requirements: list[ResolvedRequirement]) -> set[Release]:
		"""
		Download the details of the selected releases not described yet, in parallel.

		A release the index can't describe - it answers ``404 Not Found``, or the details can't be read - is remembered
		as undescribed. A release the index fails to answer for is remembered as failed and reported as a critical
		:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`. A download the current timeout cut off is neither: the
		release stays undescribed, so a later resolution asks for it again.

		:param requirements: The requirements whose selected release is described.
		:returns:            The releases whose download the current timeout cut off.
		"""
		toDownload: dict[int, Release] = {}
		for requirement in requirements:
			release = requirement._release
			if release in self._undescribed or release in self._failed:
				continue
			elif release.__lazy_state__ < LazyLoaderState.PartiallyLoaded:
				toDownload[id(release)] = release

		timedOut: set[Release] = set()
		releases = list(toDownload.values())
		documents = self._Download([release._GetPyPIEndpoint() for release in releases])
		for release, document in zip(releases, documents):
			if isinstance(document, TimeoutError) and Timeout.Current() is not None:
				timedOut.add(release)
				continue
			elif isinstance(document, BaseException):
				self._failed.add(release)
				WarningCollector.Raise(
					PackageIndexFailureWarning(
						f"Package index failed to answer for release '{release.Version}' of package '{release.Package.Name}': "
						f"{document}",
						projectName=release.Package.Name,
						version=release.Version,
						statusCode=document.status if isinstance(document, ClientResponseError) else None
					),
					document
				)
				continue
			elif document is None:
				self._undescribed.add(release)
				continue

			try:
				release.UpdateDetailsFromPyPIJSON(document)
			except (KeyError, ValueError) as ex:
				self._undescribed.add(release)
				WarningCollector.Raise(
					UnresolvedRequirementWarning(
						f"Details of release '{release.Version}' of package '{release.Package.Name}' can't be read.",
						projectName=release.Package.Name,
						version=release.Version
					),
					ex
				)

		return timedOut

	def _SelectRelease(self, project: Project, specifier: SpecifierSet) -> Nullable[Release]:
		"""
		Select the newest release of a project matching a specifier, as far as the pre-release policy admits it.

		:param project:   The project to select a release of.
		:param specifier: The specifier the release has to match.
		:returns:         The newest matching release, or ``None`` if none matches.
		"""
		preReleases = True if self._preReleases is PreReleasePolicy.Include else None
		releases =    {str(version): release for version, release in project.Releases.items()}
		matching =    [releases[version] for version in specifier.filter(releases, preReleases)]

		return max(matching, key=lambda release: release.Version) if len(matching) > 0 else None

	def _Download(self, endpoints: list[str]) -> list[Any]:
		"""
		Download JSON documents from the package index's API in parallel, over one session.

		While a :class:`~pyTooling.Timeout.Timeout` is current, the session's total timeout is the time it has left, so a
		download it cuts off returns a :exc:`TimeoutError`.

		:param endpoints: The endpoints, relative to the index's API URL.
		:returns:         Per endpoint, the parsed document, ``None`` for ``404 Not Found``, or the exception raised.
		"""
		if len(endpoints) == 0:
			return []
		elif (remaining := Timeout.Remaining()) == 0.0:
			return [TimeoutError("Timeout expired before the download.") for _ in endpoints]

		async def downloadAll() -> list[Any]:
			"""
			Nested coroutine downloading every endpoint over one shared session.

			:returns: Per endpoint, the parsed document, ``None`` for ``404 Not Found``, or the exception raised.
			"""
			async def download(session: ClientSession, endpoint: str) -> Nullable[Any]:
				"""
				Nested coroutine downloading a single endpoint.

				:param session:  The HTTP session shared by all requests of this download.
				:param endpoint: The endpoint, relative to the index's API URL.
				:returns:        The parsed document, or ``None`` for ``404 Not Found``.
				"""
				async with session.get(endpoint) as response:
					if response.status == 404:
						return None

					response.raise_for_status()
					return await response.json()

			arguments: dict[str, Any] = {"base_url": str(self._index._api), "headers": {"accept": "application/json"}}
			if remaining is not None:
				arguments["timeout"] = ClientTimeout(total=remaining)

			async with ClientSession(**arguments) as session:
				return await asyncio_gather(*(download(session, endpoint) for endpoint in endpoints), return_exceptions=True)

		return asyncio_run(downloadAll())


_Resolver = Resolver


@export
class CurrentEnvironmentResolver(Resolver):
	"""
	A :class:`Resolver` evaluating environment markers against the running interpreter
	(:func:`packaging.markers.default_environment`).
	"""

	def __init__(
		self,
		index: PythonPackageIndex,
		*,
		strategy: ResolutionStrategy = ResolutionStrategy.DEFAULT,
		limit: Nullable[int] = None,
		preReleases: PreReleasePolicy = PreReleasePolicy.DEFAULT
	) -> None:
		"""
		Initializes a resolver for the running interpreter's environment.

		:param index:       The package index the requirements are resolved against.
		:param strategy:    Optional, when the requirements of a selected release are resolved. Default:
		                    :attr:`~ResolutionStrategy.Lazy`.
		:param limit:       Optional, number of levels resolved below the given requirements; ``0`` resolves only the
		                    given requirements. Default: ``None``, unlimited.
		:param preReleases: Optional, whether pre-releases are selected. Default: :attr:`~PreReleasePolicy.Exclude`.
		:raises ValueError: If parameter 'index' is ``None``.
		:raises TypeError:  If parameter 'index' is not of type :class:`~pyTooling.Dependency.Python.PythonPackageIndex`.
		:raises ValueError: If parameter 'strategy' is ``None``.
		:raises TypeError:  If parameter 'strategy' is not of type :class:`ResolutionStrategy`.
		:raises TypeError:  If parameter 'limit' is not of type :class:`int`.
		:raises ValueError: If parameter 'limit' is negative.
		:raises ValueError: If parameter 'preReleases' is ``None``.
		:raises TypeError:  If parameter 'preReleases' is not of type :class:`PreReleasePolicy`.
		"""
		super().__init__(
			index,
			strategy=strategy,
			limit=limit,
			preReleases=preReleases,
			environment=default_environment()
		)
