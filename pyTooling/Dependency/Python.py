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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Implementation of package dependencies.

.. hint::

   See :ref:`high-level help <DEPENDENCIES>` for explanations and usage examples.
"""
from __future__           import annotations

from asyncio              import run as asyncio_run, gather as asyncio_gather
from datetime             import datetime
from enum                 import IntEnum
from functools            import wraps, update_wrapper
from pathlib              import Path
from re                   import compile as re_compile
from threading            import RLock
from typing               import Any, Optional as Nullable, Union, Iterable, Mapping, Self

from pyTooling.Exceptions import MissingDependencyError

try:
	from aiohttp import ClientSession
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="aiohttp", extra="pypi") from ex

try:
	from packaging.requirements import Requirement
	from packaging.specifiers   import InvalidSpecifier, SpecifierSet
	from packaging.utils        import canonicalize_name
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="packaging", extra="pypi") from ex

try:
	from requests import Session, HTTPError
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="requests", extra="pypi") from ex

from pyTooling.Decorators      import export, readonly
from pyTooling.MetaClasses     import ExtendedType, abstractmethod
from pyTooling.Common          import getFullyQualifiedName, firstValue
from pyTooling.Dependency      import Package, PackageStorage, PackageVersion, PackageDependencyGraph
from pyTooling.Dependency      import BrokenRequirementWarning, DependencyError, NoSessionAvailableError
from pyTooling.Dependency      import ProjectNotFoundError
from pyTooling.Dependency      import ReleaseDetailsWarning, ReleaseNotFoundError, UnknownLicenseWarning
from pyTooling.Licensing       import LicenseExpression, LicenseExpressionError, LICENSES_BY_CLASSIFIER
from pyTooling.Warning         import WarningCollector
from pyTooling.GenericPath.URL import URL
from pyTooling.Versioning      import SemanticVersion, PythonVersion, Parts


#: Longest prefix of a free-text ``license`` field quoted in a warning note, so a full license text doesn't flood it.
_LICENSE_NOTE_LENGTH = 64


#: Aliases matched against the free-text keys of ``project_urls``, lower-cased, most specific first.
_REPOSITORY_URL_ALIASES    = ("source code", "source", "code", "repository", "github", "gitlab")
_DOCUMENTATION_URL_ALIASES = ("documentation", "docs", "read the docs")
_ISSUE_TRACKER_URL_ALIASES = ("bug tracker", "issue tracker", "issues", "bug reports", "tracker")
_PROJECT_URL_ALIASES      = ("homepage", "home page", "home")
_CHANGELOG_URL_ALIASES     = ("changelog", "changes", "release notes", "whatsnew", "what's new")

#: Pattern of an ``extra == "<name>"`` comparison in a requirement's marker.
_EXTRA_MARKER = re_compile(r'''extra\s*==\s*["']([^"']+)["']''')


@export
class LicenseOverrides(metaclass=ExtendedType, slots=True):
	"""
	Licenses stated by hand, for the packages a package index can't answer for.

	A package index is not a reliable source of license information: roughly half of a typical dependency set
	publishes a PEP 639 ``license_expression``, some state a license *name* where an identifier is expected, and the
	classifier ``License :: OSI Approved :: BSD License`` means either ``BSD-2-Clause`` or ``BSD-3-Clause`` with no
	way to tell which. Those packages are answered here instead of guessed at.

	The file is YAML, and a license may be stated for the package as a whole or per version - a package that
	relicensed has one license before the switch and another after it:

	.. code-block:: yaml

	   packages:
	     colorama:
	       license:    BSD-3-Clause
	       licenseURL: https://GitHub.com/tartley/colorama/blob/master/LICENSE.txt
	       repository: https://GitHub.com/tartley/colorama
	     igraph:
	       versions:
	         ">=0.10": GPL-2.0-or-later
	         "<0.10":  GPL-2.0-only

	Version specifiers are matched in the order they are written, so the first one a version satisfies wins.
	"""

	_licenses:     dict[str, str]                             #: License expression per package, for every version.
	_versioned:    dict[str, list[tuple[SpecifierSet, str]]]  #: License expression per package and version range.
	_licenseURLs:  dict[str, str]                             #: URL of the license's text, per package.
	_repositories: dict[str, str]                             #: URL of the source repository, per package.

	def __init__(self) -> None:
		"""Initialize an empty set of overrides."""
		self._licenses     = {}
		self._versioned    = {}
		self._licenseURLs  = {}
		self._repositories = {}

	@classmethod
	def FromFile(cls, path: Path) -> Self:
		"""
		Read overrides from a YAML file.

		:param path:                    Path of the YAML file to read.
		:returns:                       The overrides the file states.
		:raises MissingDependencyError: If ``ruamel.yaml`` isn't installed.
		:raises FileNotFoundError:      If the file doesn't exist.
		:raises DependencyError:        If a version specifier in the file can't be parsed.
		"""
		try:
			from ruamel.yaml import YAML
		except ImportError as ex:  # pragma: no cover
			raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex

		if not path.exists():
			raise FileNotFoundError(f"License override file '{path}' not found.")

		with path.open("r", encoding="utf-8") as file:
			document = YAML(typ="safe").load(file) or {}

		return cls.FromDictionary(document.get("packages", None) or {})

	@classmethod
	def FromDictionary(cls, packages: Mapping[str, Mapping[str, Any]]) -> Self:
		"""
		Build overrides from an already parsed mapping.

		Keeping this apart from :meth:`FromFile` is what lets the overrides be assembled in code, and tested, without
		a file and without YAML.

		:param packages:         Mapping of a package's name to what is stated for it.
		:returns:                The overrides the mapping states.
		:raises DependencyError: If a version specifier can't be parsed.
		"""
		overrides = cls()

		for packageName, statement in packages.items():
			name = canonicalize_name(packageName)

			if (expression := statement.get("license", None)) is not None:
				overrides._licenses[name] = str(expression)

			if (licenseURL := statement.get("licenseURL", None)) is not None:
				overrides._licenseURLs[name] = str(licenseURL)

			if (repository := statement.get("repository", None)) is not None:
				overrides._repositories[name] = str(repository)

			if (versions := statement.get("versions", None)) is not None:
				ranges = []
				for specifier, expression in versions.items():
					try:
						ranges.append((SpecifierSet(str(specifier)), str(expression)))
					except InvalidSpecifier as ex:
						raise DependencyError(
							f"Version specifier '{specifier}' of package '{packageName}' can't be parsed."
						) from ex

				overrides._versioned[name] = ranges

		return overrides

	def LicenseOf(self, packageName: str, version: Nullable[SemanticVersion] = None) -> Nullable[str]:
		"""
		Return the license expression stated for a package, or for one of its versions.

		A version range is consulted first, because it is the more specific statement; the ranges are tried in the
		order they were written and the first match wins.

		:param packageName: Name of the package.
		:param version:     Optional, the version to answer for.
		:returns:           The license expression stated, or ``None`` if the package isn't overridden.
		"""
		name = canonicalize_name(packageName)

		if version is not None and (ranges := self._versioned.get(name, None)) is not None:
			for specifier, expression in ranges:
				if str(version) in specifier:
					return expression

		return self._licenses.get(name, None)

	def LicenseURLOf(self, packageName: str) -> Nullable[str]:
		"""
		Return the URL of a package's license text, where one was stated.

		:param packageName: Name of the package.
		:returns:           The URL stated, or ``None``.
		"""
		return self._licenseURLs.get(canonicalize_name(packageName), None)

	def RepositoryOf(self, packageName: str) -> Nullable[str]:
		"""
		Return the URL of a package's source repository, where one was stated.

		:param packageName: Name of the package.
		:returns:           The URL stated, or ``None``.
		"""
		return self._repositories.get(canonicalize_name(packageName), None)

	def __len__(self) -> int:
		"""
		Return the number of packages that are overridden.

		:returns: Number of overridden packages.
		"""
		return len(set(self._licenses) | set(self._versioned) | set(self._licenseURLs) | set(self._repositories))

	def __str__(self) -> str:
		"""
		Return a string representation of these overrides.

		:returns: The number of packages that are overridden.
		"""
		return f"LicenseOverrides({len(self)} packages)"


@export
class LazyLoaderState(IntEnum):
	"""
	Loading states of a lazy-loadable object, in the order they are reached.

	The states are ordered, so a loader can be asked for *at least* a given state and does nothing when the object is
	already loaded that far.
	"""
	Uninitialized =   0  #: No data or minimal data like ID or name.
	Initialized =     1  #: Initialized by some __init__ parameters.
	PartiallyLoaded = 2  #: Some additional data was loaded.
	FullyLoaded =     3  #: All data is loaded.
	PostProcessed =   4  #: Loaded data triggered further processing.


@export
class lazy:
	"""
	Unified decorator that supports:
	1. @lazy(state) def method()
	2. @lazy(state) @property def prop()
	"""

	def __init__(self, _requiredState: LazyLoaderState = LazyLoaderState.PartiallyLoaded):
		"""
		Initialize the decorator with the loading state its member needs.

		:param _requiredState: Optional, state the object has to be loaded to before the decorated member is used.
		"""
		self._requiredState = _requiredState
		self._wrapped = None

	def __call__(self, wrapped):
		"""
		Apply the decorator to a method or property.

		:param wrapped: The method or property to load lazily.
		:returns:       The decorator itself, which acts as the descriptor of the decorated member.
		"""
		self._wrapped = wrapped
		# If it's a function, we update metadata.
		# If it's a property, it doesn't support update_wrapper directly.
		if hasattr(wrapped, "__name__"):
			update_wrapper(self, wrapped)

		return self

	def __get__(self, obj, objtype=None):
		"""
		Load the object far enough, then hand out the decorated property's value or a bound method.

		:param obj:     The object the decorated member is accessed on, or ``None`` for a class access.
		:param objtype: Optional, the class the decorated member is accessed on.
		:returns:       The property's value, a bound wrapper around the method, or the decorator itself.
		"""
		if obj is None:
			return self

		# 1. Thread-safe state check
		with obj.__lazy_lock__:
			if obj.__lazy_state__ < self._requiredState:
				obj.__lazy_loader__(self._requiredState)

		# 2. Determine if we are wrapping a property or a method
		if isinstance(self._wrapped, property):
			# If it's a property, call its __get__ to return the value
			return self._wrapped.__get__(obj, objtype)

		# 3. Otherwise, treat as a method and return a bound wrapper
		@wraps(self._wrapped)
		def wrapper(*args, **kwargs):
			"""
			Nested function binding the decorated method to the object it was accessed on.

			:param args:   Positional parameters passed to the decorated method.
			:param kwargs: Named parameters passed to the decorated method.
			:returns:      Whatever the decorated method returns.
			"""
			return self._wrapped(obj, *args, **kwargs)

		return wrapper


@export
class LazyLoadableMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for objects whose details are fetched on first use.

	The object is created from what its creator knows - often little more than a name - and everything else is loaded
	when it is needed. The mixin records how far the object is loaded (:attr:`__lazy_state__`) and serializes
	concurrent loading (:attr:`__lazy_lock__`); the deriving class implements a ``__lazy_loader__`` method and decides what
	loading means.
	"""
	__lazy_state__: LazyLoaderState  #: State of the lazy loading process for this object.
	__lazy_lock__:  RLock            #: Lock serializing concurrent lazy loading of this object.

	def __init__(self, targetLevel: LazyLoaderState = LazyLoaderState.Initialized) -> None:
		"""
		Initialize the lazy-loading state of an object.

		:param targetLevel: Optional, state the object should be loaded to immediately; by default nothing is loaded.
		"""
		self.__lazy_state__ = LazyLoaderState.Initialized
		self.__lazy_lock__ = RLock()

		if targetLevel > self.__lazy_state__:
			with self.__lazy_lock__:
				self.__lazy_loader__(targetLevel)

	@abstractmethod
	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Load the object's details up to the given state.

		:param targetLevel: Optional, state the object needs to be loaded to.
		"""
		pass


@export
class Distribution(metaclass=ExtendedType, slots=True):
	"""
	A single downloadable file of a release - a wheel or a source archive.
	"""
	_filename:   str       #: Filename of the distribution's file.
	_url:        URL       #: URL to download the distribution's file from.
	_uploadTime: datetime  #: Time when the distribution was uploaded to the package index.

	def __init__(self, filename: str, url: Union[str, URL], uploadTime: datetime) -> None:
		"""
		Initialize a distribution with the data the package index reports for it.

		:param filename:   Filename of the distribution's file.
		:param url:        URL to download the file from, as a string or a parsed URL.
		:param uploadTime: Time the distribution was uploaded to the package index.
		:raises TypeError: If a parameter is not of the expected type.
		"""
		if not isinstance(filename, str):
			ex = TypeError("Parameter 'filename' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(filename)}'.")
			raise ex

		self._filename = filename

		if isinstance(url, str):
			url = URL.Parse(url)
		elif not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		self._url = url

		if not isinstance(uploadTime, datetime):
			ex = TypeError("Parameter 'uploadTime' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(uploadTime)}'.")
			raise ex

		self._uploadTime = uploadTime

	@readonly
	def Filename(self) -> str:
		"""
		Read-only property to access the distribution's filename (:attr:`_filename`).

		:returns: Filename of the distribution.
		"""
		return self._filename

	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the URL this distribution can be downloaded from (:attr:`_url`).

		:returns: Download URL of the distribution.
		"""
		return self._url

	@readonly
	def UploadTime(self) -> datetime:
		"""
		Read-only property to access the time this distribution was uploaded (:attr:`_uploadTime`).

		:returns: Upload time of the distribution.
		"""
		return self._uploadTime

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this distribution.

		:returns: The distribution's filename, prefixed by its kind.
		"""
		return f"Distribution: {self._filename}"

	def __str__(self) -> str:
		"""
		Return a string representation of this distribution.

		:returns: The distribution's filename.
		"""
		return f"{self._filename}"


@export
class Release(PackageVersion, LazyLoadableMixin):
	"""
	One released version of a project on a Python package index.

	A release knows its distributions (the files that can be downloaded) and its requirements, sorted into the extras
	they belong to. Both are fetched from the index on first use.
	"""
	_files:        list[Distribution]                         #: Distributions (wheels, source archives) of this release.
	_requirements: dict[Union[str, None], list[Requirement]]  #: Requirements per extra; ``None`` collects the unconditional ones.

	_api:          Nullable[URL]                              #: URL of the package index's API, used to load the release's details.
	_session:      Nullable[Session]                          #: HTTP session reused for the API requests.

	def __init__(
		self,
		version:      PythonVersion,
		timestamp:    datetime,
		files:        Nullable[Iterable[Distribution]] = None,
		requirements: Nullable[Mapping[str, list[Requirement]]] = None,
		project:      Nullable[Project] = None,
		lazy:         LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
		"""
		Initialize a release of a project.

		The API endpoint and the HTTP session are taken from the project's package index, so a release created from a
		project can fetch its own details.

		:param version:      Version number of this release.
		:param timestamp:    Time this version was released.
		:param files:        Optional, distributions of this release.
		:param requirements: Optional, requirements of this release, by extra.
		:param project:      Optional, project this release belongs to.
		:param lazy:         Optional, state the release should be loaded to immediately.
		"""
		if project is not None and (storage := project._storage) is not None:
			self._api =     storage._api
			self._session = storage._session
		else:
			self._api =     None
			self._session = None

		super().__init__(version, project, timestamp)
		LazyLoadableMixin.__init__(self, lazy)

		self._files = [file for file in files] if files is not None else []
		self._requirements = {k: v for k, v in requirements} if requirements is not None else {None: []}

	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Download the release's details and post-process them, as far as the target state demands.

		:param targetLevel: Optional, state the release needs to be loaded to.
		"""
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.PostProcess()

	@lazy(LazyLoaderState.PostProcessed)
	@PackageVersion.DependsOn.getter
	def DependsOn(self) -> dict[Package, dict[SemanticVersion, PackageVersion]]:
		"""
		Read-only property to access the packages this release depends on.

		:returns: Dictionary of packages and their versions this release depends on.
		"""
		return super().DependsOn

	@readonly
	def Project(self) -> Project:
		"""
		Read-only property to access the project this release belongs to (:attr:`_package`).

		:returns: The project this release belongs to.
		"""
		return self._package

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Files(self) -> list[Distribution]:
		"""
		Read-only property to access the distributions published for this release (:attr:`_files`).

		:returns: List of distributions.
		"""
		return self._files

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Requirements(self) -> dict[str, list[Requirement]]:
		"""
		Read-only property to access the release's requirements, grouped by extra (:attr:`_requirements`).

		:returns: Dictionary of extras and their requirements. Requirements without an extra are stored under ``None``.
		"""
		return self._requirements

	def _GetPyPIEndpoint(self) -> str:
		"""
		Return the API endpoint describing this release.

		:returns: The endpoint's path, relative to the index's API URL.
		"""
		return f"{self._package._name.lower()}/{self._version}/json"

	def DownloadDetails(self) -> None:
		"""
		Download this release's details from the package index and load the projects it requires.

		:raises NoSessionAvailableError: If the release wasn't created by a package index, so it has no session. |br|
		                                 A session is opened by the package index and handed to the objects it
		                                 creates.
		:raises ReleaseNotFoundError:    If the index doesn't know this release.
		"""
		if self._session is None:
			ex = NoSessionAvailableError(f"No session available to download release '{self._version}' of package '{self._package._name}'.")
			ex.add_note("A session is opened by the package index and handed to the objects it creates.")
			raise ex

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response is not None and ex.response.status_code == 404:
				raise ReleaseNotFoundError(f"Release '{self._version}' of package '{self._package._name}' not found.") from ex

		self.UpdateDetailsFromPyPIJSON(response.json())

		index: PythonPackageIndex = self._package._storage
		for requirement in self._requirements[None]:
			packageName = requirement.name
			index.DownloadProject(packageName, True)

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
		"""
		Fill this release from the JSON document the package index returned.

		The requirements are sorted into the extras they belong to. A requirement lands under ``None`` when it has no
		marker at all, and also when its marker conditions it on the *environment* rather than on an extra -
		``importlib-resources; python_version < "3.7"`` is required unconditionally, just not everywhere. A
		requirement naming an extra the release does not declare is reported as a :class:`BrokenRequirementWarning`.

		Metadata older than core-metadata 2.1 has no ``provides_extra`` field. Its extras are recovered from the
		markers naming them, because dropping every conditional requirement of an old release would empty exactly the
		releases a version-aware dependency graph is built to look at. A declared extra keeps the spelling it was
		declared with; a recovered one has no such spelling, so it keeps the canonical one - ``theme_furo`` written in
		a marker is recovered as ``theme-furo``.

		:param json: The parsed JSON document describing this release.
		"""
		infoNode = json["info"]
		self._ResolveLicense(infoNode)
		self._ResolveURLs(infoNode)

		requirements = [Requirement(requirement) for requirement in (infoNode["requires_dist"] or ())]

		# The declared spelling is kept as the key, while the canonical one - 'code_style' and 'code-style' are the
		# same extra - is what a marker is matched against.
		if (declaredExtras := infoNode["provides_extra"]) is not None:
			extras = {canonicalize_name(extra): extra for extra in declaredExtras}
		else:
			extras = {}
			for requirement in requirements:
				if requirement.marker is not None:
					for name in _EXTRA_MARKER.findall(str(requirement.marker)):
						extras.setdefault(canonicalize_name(name), name)

		self._requirements = {extra: [] for extra in extras.values()}
		self._requirements[None] = []

		if len(requirements) > 0:
			brokenRequirements = []
			for req in requirements:
				# A marker naming no extra conditions the requirement on the interpreter or the platform, so the
				# requirement is unconditional as far as the extras are concerned.
				if req.marker is None or len(namedExtras := _EXTRA_MARKER.findall(str(req.marker))) == 0:
					self._requirements[None].append(req)
					continue

				for name in namedExtras:
					if (extra := extras.get(canonicalize_name(name))) is not None:
						self._requirements[extra].append(req)
						break
				else:
					brokenRequirements.append(req)

			if len(brokenRequirements) > 0:
				WarningCollector.Raise(
					BrokenRequirementWarning(f"Package '{self._package._name}' has {len(brokenRequirements)} requirement(s) whose marker matches no declared extra."),
					notes=[f"Broken requirement: {req}" for req in brokenRequirements]
				)
				# Preserving the broken requirements under the special index 0 makes 'Requirements' a dictionary of mixed
				# key types (str, None and int), which no consumer expects.
				# self._requirements[0] = brokenRequirements

		self.__lazy_state__ = LazyLoaderState.FullyLoaded

	def _ResolveLicense(self, infoNode: Mapping[str, Any]) -> None:
		"""
		Resolve this release's license from what was published, and from what was stated by hand.

		The sources are consulted in order of how much they can be trusted, and the first one that answers wins:

		1. the :class:`LicenseOverrides` of the package index - an explicit statement always wins,
		2. ``license_expression``, the PEP 639 field, which is an SPDX expression by definition,
		3. ``license``, the legacy free-text field - it is handed to the parser like any other candidate, and a field
		   holding the license's full text simply doesn't parse,
		4. a license classifier, but only when it means exactly one license - ``License :: OSI Approved :: BSD
		   License`` means either ``BSD-2-Clause`` or ``BSD-3-Clause`` and is never guessed at.

		Whatever was found is parsed into a :class:`~pyTooling.Licensing.LicenseExpression` and kept verbatim in
		:attr:`~pyTooling.Dependency.PackageVersion.PublishedLicense`, even when it doesn't parse. A release whose
		license stays unresolved is reported as an
		:class:`~pyTooling.Dependency.UnknownLicenseWarning` naming what was published, because that is the list of
		packages the override file has to answer for.

		:param infoNode: The ``info`` node of the JSON document describing this release.
		"""
		index: PythonPackageIndex = self._package._storage
		overrides = index._licenseOverrides
		published = []
		candidates = []

		if (override := overrides.LicenseOf(self._package._name, self._version)) is not None:
			candidates.append(override)
		else:
			if (licenseExpression := infoNode.get("license_expression", None)) is not None:
				published.append(f"license_expression: {licenseExpression}")
				candidates.append(licenseExpression)
			elif (licenseText := (infoNode.get("license", None) or "").strip()) != "":
				published.append(f"license: {licenseText[:_LICENSE_NOTE_LENGTH]}")
				candidates.append(licenseText)

			for classifier in infoNode.get("classifiers", None) or ():
				if not classifier.startswith("License ::"):
					continue

				published.append(f"classifier: {classifier}")
				if len(matches := LICENSES_BY_CLASSIFIER.get(classifier, ())) == 1:
					candidates.append(matches[0].SPDXIdentifier)

				break

		for candidate in candidates:
			try:
				self._licenseExpression = LicenseExpression.Parse(candidate)
			except (LicenseExpressionError, ValueError):
				continue

			# The expression keeps the candidate as its 'ParsedFrom', so '_publishedLicense' stays empty.
			break
		else:
			self._publishedLicense = candidates[0] if len(candidates) > 0 else ""

		if (licenseURL := overrides.LicenseURLOf(self._package._name)) is not None:
			self._licenseURL = URL.Parse(licenseURL)

		if self._licenseExpression is None:
			WarningCollector.Raise(
				UnknownLicenseWarning(
					f"License of '{self._package._name}' {self._version} couldn't be resolved."
				),
				notes=published if len(published) > 0 else ["The package index published no license information."]
			)

	def _ResolveURLs(self, infoNode: Mapping[str, Any]) -> None:
		"""
		Resolve this release's project URLs from what the package index published.

		``project_urls`` is a free-text mapping - one project writes ``Source``, another ``Source Code``,
		``Repository`` or ``GitHub`` for the same thing - so its keys are matched case-insensitively against a list of
		aliases per URL and the first alias present wins. ``home_page`` is the fallback for the homepage, and the
		homepage is the last resort for the repository, which is what the project-level resolver used to do.

		These are resolved per release rather than per package because they move: a project migrating from Google
		Code or SourceForge to GitHub has one repository URL before the migration and another after it.
		:attr:`~pyTooling.Dependency.Package.RepositoryURL` and its siblings mirror the latest release, so the
		package still answers for the current state.

		:param infoNode: The ``info`` node of the JSON document describing this release.
		"""
		projectURLs = {
			str(key).strip().lower(): value
			for key, value in (infoNode.get("project_urls", None) or {}).items()
			if value is not None
		}

		def urlFor(aliases: tuple[str, ...]) -> Nullable[URL]:
			"""
			Return the first of the given aliases the package index published a URL for.

			:param aliases: The keys to look for, most specific first.
			:returns:       The URL of the first alias that is present, or ``None`` if none of them is.
			"""
			for alias in aliases:
				if (url := projectURLs.get(alias, None)) is not None:
					return URL.Parse(url)

			return None

		self._documentationURL = urlFor(_DOCUMENTATION_URL_ALIASES)
		self._issueTrackerURL  = urlFor(_ISSUE_TRACKER_URL_ALIASES)
		self._changelogURL     = urlFor(_CHANGELOG_URL_ALIASES)
		self._projectURL      = urlFor(_PROJECT_URL_ALIASES)

		if self._projectURL is None and (homePage := infoNode.get("home_page", None)) is not None:
			self._projectURL = URL.Parse(homePage)

		index: PythonPackageIndex = self._package._storage
		if (repository := index._licenseOverrides.RepositoryOf(self._package._name)) is not None:
			self._repositoryURL = URL.Parse(repository)
		elif (repositoryURL := urlFor(_REPOSITORY_URL_ALIASES)) is not None:
			self._repositoryURL = repositoryURL
		else:
			self._repositoryURL = self._projectURL

	def PostProcess(self) -> None:
		"""
		Resolve this release's requirements into dependencies on concrete releases.

		Every required project is downloaded and the releases matching the requirement's specifier are attached as
		dependencies of this release.
		"""
		index: PythonPackageIndex = self._package._storage
		for requirement in self._requirements[None]:
			package = index.DownloadProject(requirement.name)

			for release in package:
				if str(release._version) in requirement.specifier:
					self.AddDependencyToPackageVersion(release)

		self.SortDependencies()
		self.__lazy_state__ = LazyLoaderState.PostProcessed

	@lazy(LazyLoaderState.PartiallyLoaded)
	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this release, loading its details if needed.

		:returns: Package name, version and the number of distributions.
		"""
		return f"Release: {self._package._name}:{self._version} Files: {len(self._files)}"

	def __str__(self) -> str:
		"""
		Return a string representation of this release.

		:returns: The release's version number.
		"""
		return f"{self._version}"


@export
class Project(Package, LazyLoadableMixin):
	"""
	A project (package) on a Python package index, with its releases.

	The list of releases and the project's details are fetched from the index on first use.
	"""
	_url:         Nullable[URL]      #: URL of the project's page on the package index.

	_api:         Nullable[URL]      #: URL of the package index's API, used to load the project's details.
	_session:     Nullable[Session]  #: HTTP session reused for the API requests.

	def __init__(
		self,
		name:     str,
		url:      Union[str, URL],
		releases: Nullable[Iterable[Release]] = None,
		index:    Nullable[PythonPackageIndex] = None,
		lazy:     LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
		"""
		Initialize a project on a package index.

		The API endpoint and the HTTP session are taken from the index, so the project can fetch its own details.

		:param name:     Name of the project on the package index.
		:param url:      URL of the project's page, as a string or a parsed URL.
		:param releases: Optional, releases of this project.
		:param index:    Optional, package index this project is hosted on.
		:param lazy:     Optional, state the project should be loaded to immediately.
		"""
		if index is not None:
			self._api =     index._api
			self._session = index._session
		else:
			self._api =     None
			self._session = None

		super().__init__(name, storage=index)
		LazyLoadableMixin.__init__(self, lazy)

		# if isinstance(url, str):
		# 	url = URL.Parse(url)
		# elif not isinstance(url, URL):
		# 	ex = TypeError("Parameter 'url' is not of type 'URL'.")
		# 	ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
		# 	raise ex
		#
		# self._url = url
		# self._releases = {release.Version: release for release in sorted(releases, key=lambda r: r.Version)} if releases is not None else {}

	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Download the project's details and its releases' details, as far as the target state demands.

		:param targetLevel: Optional, state the project needs to be loaded to.
		"""
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.DownloadReleaseDetails()

	@readonly
	def PackageIndex(self) -> PythonPackageIndex:
		"""
		Read-only property to access the package index this project was read from (:attr:`_storage`).

		:returns: The package index this project belongs to.
		"""
		return self._storage

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the project's URL in the package index (:attr:`_url`).

		:returns: URL of the project.
		"""
		return self._url

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Releases(self) -> dict[PythonVersion, Release]:
		"""
		Read-only property to access all known releases of this project (:attr:`_versions`).

		:returns: Dictionary of versions and their releases.
		"""
		return self._versions

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def ReleaseCount(self) -> int:
		"""
		Read-only property to return the number of known releases.

		:returns: Number of releases.
		"""
		return len(self._versions)

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def LatestRelease(self) -> Release:
		"""
		Read-only property to return the most recent release of this project.

		:returns: The latest release.
		"""
		return firstValue(self._versions)

	def _GetPyPIEndpoint(self) -> str:
		"""
		Return the API endpoint describing this project.

		:returns: The endpoint's path, relative to the index's API URL.
		"""
		return f"{self._name.lower()}/json"

	def DownloadDetails(self) -> None:
		"""
		Download this project's details and its list of releases from the package index.

		:raises NoSessionAvailableError: If the project wasn't created by a package index, so it has no session. |br|
		                                 A session is opened by the package index and handed to the objects it
		                                 creates.
		:raises ProjectNotFoundError:    If the index doesn't know this project.
		"""
		if self._session is None:
			ex = NoSessionAvailableError(f"No session available to download details of package '{self._name}'.")
			ex.add_note("A session is opened by the package index and handed to the objects it creates.")
			raise ex

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response is not None and ex.response.status_code == 404:
				raise ProjectNotFoundError(f"Package '{self._name}' not found.") from ex

		self.UpdateDetailsFromPyPIJSON(response.json())

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
		"""
		Fill this project from the JSON document the package index returned.

		Releases without a distribution are skipped, and a version the parser doesn't understand is reported as a
		warning rather than failing the whole project.

		:param json: The parsed JSON document describing this project.
		"""
		infoNode = json["info"]
		releasesNode = json["releases"]

		# Update project/package URL
		self._url = URL.Parse(infoNode["project_url"])

		# Convert key to Version number, skip empty releases
		convertedReleasesNode = {}
		for k, v in releasesNode.items():
			if len(v) == 0:
				continue

			try:
				version = PythonVersion.Parse(k)
				convertedReleasesNode[version] = v
			except ValueError as ex:
				print(f"Unsupported version format '{k}' - {ex}")

		for version, releaseNode in sorted(convertedReleasesNode.items(), key=lambda t: t[0]):
			if Parts.Postfix in version._parts:
				pass

			files = [Distribution(file["filename"], file["url"], datetime.fromisoformat(file["upload_time_iso_8601"]), ) for
							 file in releaseNode]
			lazy = LazyLoaderState.PartiallyLoaded if LazyLoaderState.PartiallyLoaded <= self.__lazy_state__ <= LazyLoaderState.FullyLoaded else LazyLoaderState.Initialized
			Release(
				version,
				files[0]._uploadTime,
				files,
				project=self,
				lazy=lazy
			)

		self.SortVersions()
		self.__lazy_state__ = LazyLoaderState.FullyLoaded

	def DownloadReleaseDetails(self) -> None:
		"""
		Download the details of every release of this project, in parallel.

		The requests run in one :mod:`asyncio` event loop over a shared session, because a project can easily have
		hundreds of releases.
		"""
		async def ParallelDownloadReleaseDetails():
			"""
			Nested coroutine downloading the details of every release over one shared session.
			"""
			async def routine(session, release: Release):
				"""
				Nested coroutine downloading the details of a single release.

				:param session: The HTTP session shared by all requests of this download.
				:param release: The release to download the details for.
				"""
				if Parts.Postfix in release._version._parts:
					pass

				async with session.get(release._GetPyPIEndpoint()) as response:
					json = await response.json()
					response.raise_for_status()

					release.UpdateDetailsFromPyPIJSON(json)

			async with ClientSession(base_url=str(self._api), headers={"accept": "application/json"}) as session:
				tasks = []
				for release in self._versions.values():  # type: Release
					tasks.append(routine(session, release))

				results = await asyncio_gather(*tasks, return_exceptions=True)
				delList = []
				for release, result in zip(self.Releases.values(), results):
					if isinstance(result, Exception):
						delList.append((release, result))

				for release, ex in delList:
					WarningCollector.Raise(
						ReleaseDetailsWarning(f"Dropping release '{release.Version}' of package '{release.Project._name}': details couldn't be downloaded."),
						ex
					)
					del self.Releases[release.Version]

		asyncio_run(ParallelDownloadReleaseDetails())
		self.__lazy_state__ = LazyLoaderState.PostProcessed

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this project.

		:returns: The project's name and its latest release's version.
		"""
		return f"Project: {self._name} latest: {self.LatestRelease._version}"

	def __str__(self) -> str:
		"""
		Return a string representation of this project.

		:returns: The project's name.
		"""
		return f"{self._name}"


@export
class PythonPackageIndex(PackageStorage):
	"""
	A Python package index like PyPI, addressed through its JSON API.

	It is the entry point of the dependency graph: projects are looked up here, and every request to the index reuses
	the same HTTP session.
	"""
	_url:              URL               #: URL of the package index's website.
	_api:              URL               #: URL of the package index's API.
	_session:          Session           #: HTTP session reused for every request to this index.
	_licenseOverrides: LicenseOverrides  #: Licenses stated by hand, for what this index can't answer for.

	def __init__(
		self,
		name: str,
		url: Union[str, URL],
		api: Union[str, URL],
		graph: PackageDependencyGraph,
		licenseOverrides: Nullable[LicenseOverrides] = None
	) -> None:
		"""
		Initialize a package index and open the HTTP session used for every request to it.

		:param name:             Name of the package index.
		:param url:              URL of the index's website, as a string or a parsed URL.
		:param api:              URL of the index's JSON API, as a string or a parsed URL.
		:param graph:            Dependency graph this index belongs to.
		:param licenseOverrides: Optional, licenses stated by hand; an empty set of overrides if not given.
		:raises TypeError:       If parameter 'url' is neither a string nor a :class:`~pyTooling.GenericPath.URL.URL`.
		:raises TypeError:       If parameter 'api' is neither a string nor a :class:`~pyTooling.GenericPath.URL.URL`.
		"""
		super().__init__(name, graph)

		self._licenseOverrides = licenseOverrides if licenseOverrides is not None else LicenseOverrides()

		if isinstance(url, str):
			url = URL.Parse(url)
		elif not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		self._url = url

		if isinstance(api, str):
			api = URL.Parse(api)
		elif not isinstance(api, URL):
			ex = TypeError("Parameter 'api' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(api)}'.")
			raise ex

		self._api = api

		self._session = Session()
		self._session.headers["accept"] = "application/json"

	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the package index' base URL (:attr:`_url`).

		:returns: Base URL of the package index.
		"""
		return self._url

	@readonly
	def LicenseOverrides(self) -> LicenseOverrides:
		"""
		Read-only property to access the licenses stated by hand for this index (:attr:`_licenseOverrides`).

		:returns: The index's license overrides.
		"""
		return self._licenseOverrides

	@readonly
	def API(self) -> URL:
		"""
		Read-only property to access the package index' API URL (:attr:`_api`).

		:returns: API URL of the package index.
		"""
		return self._api

	@readonly
	def Projects(self) -> dict[str, Project]:
		"""
		Read-only property to access all projects known to this package index (:attr:`_packages`).

		:returns: Dictionary of project names and projects.
		"""
		return self._packages

	@readonly
	def ProjectCount(self) -> int:
		"""
		Read-only property to return the number of known projects.

		:returns: Number of projects.
		"""
		return len(self._packages)

	def _GetPyPIEndpoint(self, projectName: str) -> str:
		"""
		Return the API endpoint describing a project.

		:param projectName: Name of the project on the package index.
		:returns:           The endpoint's URL.
		"""
		return f"{self._api}{projectName.lower()}/json"

	def DownloadProject(self, projectName: str, lazy: LazyLoaderState = LazyLoaderState.PartiallyLoaded) -> Project:
		"""
		Look up a project on this package index.

		:param projectName: Name of the project on the package index.
		:param lazy:        Optional, state the project should be loaded to immediately.
		:returns:           The project, loaded as far as ``lazy`` demands.
		"""
		project = Project(projectName, "", index=self, lazy=lazy)

		return project

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this package index.

		:returns: The index's name.
		"""
		return f"{self._name}"

	def __str__(self) -> str:
		"""
		Return a string representation of this package index.

		:returns: The index's name.
		"""
		return f"{self._name}"


@export
class PythonPackageDependencyGraph(PackageDependencyGraph):
	"""
	A dependency graph of Python packages, whose vertices are projects and whose edges are requirements.
	"""

	def __init__(self, name: str) -> None:
		"""
		Initialize an empty dependency graph of Python packages.

		:param name: Name of the dependency graph.
		"""
		super().__init__(name)
