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

Importing this module needs the ``pypi`` extra (:mod:`aiohttp`, :mod:`packaging`), like
:mod:`pyTooling.Dependency.Python`.

:raises MissingDependencyError: If the 'pypi' extra isn't installed.
"""
from __future__                  import annotations

from asyncio                     import run as asyncio_run, gather as asyncio_gather
from enum                        import Enum, auto
from typing                      import Any, Callable, Iterable, Iterator, Optional as Nullable

from pyTooling.Exceptions        import MissingDependencyError

try:
	from aiohttp                   import ClientResponseError, ClientSession
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="aiohttp", extra="pypi") from ex

try:
	from packaging.requirements    import Requirement
	from packaging.utils           import canonicalize_name
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="packaging", extra="pypi") from ex

from pyTooling.Decorators        import export, readonly
from pyTooling.MetaClasses       import ExtendedType
from pyTooling.Common            import StringEnum, getFullyQualifiedName
from pyTooling.Warning           import WarningCollector
from pyTooling.Dependency        import PackageIndexFailureWarning, UnresolvedRequirementWarning
from pyTooling.Dependency.Python import LazyLoaderState, Project, PythonPackageIndex, Release

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

	Resolved =           auto()  #: A release matching the requirement was selected, and its details were downloaded.
	UnknownProject =     auto()  #: The package index doesn't know the required project.
	NoMatchingRelease =  auto()  #: No release of the project matches the requirement's specifier.
	UndescribedRelease = auto()  #: The package index can't describe the selected release.
	Cycle =              auto()  #: The project is required further up the path already, so it isn't followed again.
	LimitReached =       auto()  #: The requirement is below the resolver's limit, so it wasn't resolved.
	IndexFailure =       auto()  #: The package index failed to answer for the project or the selected release.


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
		parent: Nullable[ResolvedRequirement] = None
	) -> None:
		"""
		Initializes a requirement to resolve.

		:param requirement: The requirement as stated.
		:param resolution:  The resolution this requirement belongs to.
		:param parent:      Optional, the requirement whose release requires this one. Default: ``None``, a requirement
		                    given to the resolver.
		:raises ValueError: If parameter 'requirement' is ``None``.
		:raises TypeError:  If parameter 'requirement' is not of type :class:`~packaging.requirements.Requirement`.
		:raises ValueError: If parameter 'resolution' is ``None``.
		:raises TypeError:  If parameter 'resolution' is not of type :class:`Resolution`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`ResolvedRequirement`.
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

		self._resolution =   resolution
		self._parent =       parent
		self._requirement =  requirement
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

		:returns: Tuple of resolved requirements; empty if the requirement wasn't resolved to a release, or closes a
		          cycle.
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
	either policy. The release's requirements are resolved the same way, as deep as the limit allows, either up front or
	when they are first asked for (:class:`ResolutionStrategy`). A project required again further up the path closes a
	cycle and isn't followed. The downloads of one level run in parallel.

	Each requirement keeps what resolving it came to (:class:`ResolutionStatus`): a requirement whose project the index
	doesn't know, or whose selected release it can't describe, is reported as an
	:exc:`~pyTooling.Dependency.UnresolvedRequirementWarning` to a :class:`~pyTooling.Warning.WarningCollector`, and
	stays in the resolution. A server error or a failed connection of the index is reported as a critical
	:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`. The selected releases are connected in the index's
	dependency graph.

	.. attention::

	   It is no installer's solver: every requirement is resolved on its own. Two requirements of the same project with
	   conflicting specifiers select two releases; nothing is backtracked.
	"""

	_index:       PythonPackageIndex        #: The package index the requirements are resolved against.
	_strategy:    ResolutionStrategy        #: When the requirements of a selected release are resolved.
	_limit:       Nullable[int]             #: Number of levels resolved below the given requirements.
	_preReleases: PreReleasePolicy          #: Whether pre-releases are selected.
	_undescribed: set[Release]              #: Releases the index couldn't describe.
	_failed:      set[Project | Release]    #: Projects and releases the index failed to answer for.

	def __init__(
		self,
		index: PythonPackageIndex,
		*,
		strategy: ResolutionStrategy = ResolutionStrategy.DEFAULT,
		limit: Nullable[int] = None,
		preReleases: PreReleasePolicy = PreReleasePolicy.DEFAULT
	) -> None:
		"""
		Initializes a resolver.

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

		self._index =       index
		self._strategy =    strategy
		self._limit =       limit
		self._preReleases = preReleases
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

	def ResolveRequirements(self, requirements: Iterable[Requirement]) -> Resolution:
		"""
		Resolve requirements.

		A project required twice is resolved once: the later requirement replaces the earlier one, in the earlier one's
		position.

		:param requirements: The requirements to resolve.
		:returns:            The resolution.
		:raises ValueError:  If parameter 'requirements' is ``None``.
		:raises TypeError:   If parameter 'requirements' is not iterable.
		:raises TypeError:   If an element of parameter 'requirements' is not of type
		                     :class:`~packaging.requirements.Requirement`.
		"""
		if requirements is None:
			raise ValueError("Parameter 'requirements' is None.")
		elif not isinstance(requirements, Iterable):
			ex = TypeError("Parameter 'requirements' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(requirements)}'.")
			raise ex

		flattened: dict[str, Requirement] = {}
		for requirement in requirements:
			if not isinstance(requirement, Requirement):
				ex = TypeError("An element of parameter 'requirements' is not of type 'Requirement'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(requirement)}'.")
				raise ex

			flattened[canonicalize_name(requirement.name)] = requirement

		return self._Resolve(flattened.values())

	def _Resolve(self, requirements: Iterable[Requirement]) -> Resolution:
		"""
		Resolve the given requirements and, with the strategy :attr:`~ResolutionStrategy.Eager`, everything below them.

		:param requirements: The requirements to resolve.
		:returns:            The resolution.
		"""
		resolution = Resolution(self)
		for requirement in requirements:
			resolution._requirements.append(ResolvedRequirement(requirement, resolution))

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

		A release's dependencies are its unconditional requirements.

		:param requirements: Requirements resolved already, whose dependencies aren't created yet.
		"""
		dependencies: list[ResolvedRequirement] = []
		for requirement in requirements:
			requirement._dependencies = []
			if requirement._status is not ResolutionStatus.Resolved:
				continue

			for dependency in requirement._release.Requirements[None]:
				resolvedDependency = ResolvedRequirement(dependency, requirement._resolution, parent=requirement)
				requirement._dependencies.append(resolvedDependency)
				dependencies.append(resolvedDependency)

		self._ResolveLevel(dependencies)

	def _ResolveLevel(self, requirements: list[ResolvedRequirement]) -> None:
		"""
		Resolve requirements: check cycle and limit, then look up the projects and describe the selected releases, the
		downloads of each step in parallel.

		:param requirements: The requirements to resolve.
		"""
		toLookUp: list[ResolvedRequirement] = []
		for requirement in requirements:
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

		self._LookUpProjects(toLookUp)

		toDescribe: list[ResolvedRequirement] = []
		for requirement in toLookUp:
			if requirement._project is None:
				requirement._status = ResolutionStatus.UnknownProject
				WarningCollector.Raise(UnresolvedRequirementWarning(
					f"Package '{requirement._requirement.name}' is unknown to the package index.",
					projectName=requirement._requirement.name
				))
				continue

			if requirement._project in self._failed:
				requirement._status = ResolutionStatus.IndexFailure
				continue

			preReleases = True if self._preReleases is PreReleasePolicy.Include else None
			releases =    {str(version): release for version, release in requirement._project.Releases.items()}
			matching =    [releases[version] for version in requirement._requirement.specifier.filter(releases, preReleases)]
			if len(matching) == 0:
				requirement._status = ResolutionStatus.NoMatchingRelease
				continue

			requirement._release = max(matching, key=lambda release: release.Version)
			toDescribe.append(requirement)

		self._DescribeReleases(toDescribe)

		for requirement in toDescribe:
			if requirement._release in self._failed:
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

	def _LookUpProjects(self, requirements: list[ResolvedRequirement]) -> None:
		"""
		Look up the required projects on the index, downloading those not loaded yet in parallel.

		A project the index answers ``404 Not Found`` for is forgotten by the index and left ``None``. A project the index
		fails to answer for is remembered as failed and reported as a critical
		:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`.

		:param requirements: The requirements whose project is looked up.
		"""
		toDownload: dict[str, Project] = {}
		for requirement in requirements:
			name = requirement._requirement.name
			if canonicalize_name(name) in self._index._unknownProjects:
				continue

			project = self._index.DownloadProject(name, LazyLoaderState.Initialized)
			if project not in self._failed and project.__lazy_state__ < LazyLoaderState.PartiallyLoaded:
				toDownload[canonicalize_name(name)] = project

		projects = list(toDownload.values())
		documents = self._Download([project._GetPyPIEndpoint() for project in projects])
		for project, document in zip(projects, documents):
			if isinstance(document, BaseException):
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

	def _DescribeReleases(self, requirements: list[ResolvedRequirement]) -> None:
		"""
		Download the details of the selected releases not described yet, in parallel.

		A release the index can't describe - it answers ``404 Not Found``, or the details can't be read - is remembered
		as undescribed. A release the index fails to answer for is remembered as failed and reported as a critical
		:exc:`~pyTooling.Dependency.PackageIndexFailureWarning`.

		:param requirements: The requirements whose selected release is described.
		"""
		toDownload: dict[int, Release] = {}
		for requirement in requirements:
			release = requirement._release
			if release in self._undescribed or release in self._failed:
				continue
			elif release.__lazy_state__ < LazyLoaderState.PartiallyLoaded:
				toDownload[id(release)] = release

		releases = list(toDownload.values())
		documents = self._Download([release._GetPyPIEndpoint() for release in releases])
		for release, document in zip(releases, documents):
			if isinstance(document, BaseException):
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

	def _Download(self, endpoints: list[str]) -> list[Any]:
		"""
		Download JSON documents from the package index's API in parallel, over one session.

		:param endpoints: The endpoints, relative to the index's API URL.
		:returns:         Per endpoint, the parsed document, ``None`` for ``404 Not Found``, or the exception raised.
		"""
		if len(endpoints) == 0:
			return []

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

			async with ClientSession(base_url=str(self._index._api), headers={"accept": "application/json"}) as session:
				return await asyncio_gather(*(download(session, endpoint) for endpoint in endpoints), return_exceptions=True)

		return asyncio_run(downloadAll())


_Resolver = Resolver

