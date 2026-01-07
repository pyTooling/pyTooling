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
from asyncio   import run as asyncio_run, gather as asyncio_gather
from datetime  import datetime
from enum      import IntEnum
from functools import wraps, update_wrapper
from threading import RLock
from typing    import Optional as Nullable, List, Dict, Union, Iterable, Mapping, Callable, Iterator

try:
	from aiohttp import ClientSession
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'aiohttp' not installed. Either install pyTooling with extra dependencies 'pyTooling[pypi]' or install 'aiohttp' directly.") from ex

try:
	from packaging.requirements import Requirement
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'packaging' not installed. Either install pyTooling with extra dependencies 'pyTooling[pypi]' or install 'packaging' directly.") from ex

try:
	from requests import Session, HTTPError
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'requests' not installed. Either install pyTooling with extra dependencies 'pyTooling[pypi]' or install 'requests' directly.") from ex

try:
	from pyTooling.Decorators      import export, readonly
	from pyTooling.MetaClasses     import ExtendedType, abstractmethod, mustoverride
	from pyTooling.Exceptions      import ToolingException
	from pyTooling.Common          import getFullyQualifiedName, firstKey, firstValue
	from pyTooling.Dependency      import Package, PackageStorage, PackageVersion, PackageDependencyGraph
	from pyTooling.GenericPath.URL import URL
	from pyTooling.Versioning      import SemanticVersion, PythonVersion, Parts
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Dependency] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, abstractmethod, mustoverride
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName, firstKey, firstValue
		from Dependency          import Package, PackageStorage, PackageVersion, PackageDependencyGraph
		from GenericPath.URL     import URL
		from Versioning          import SemanticVersion, PythonVersion, Parts
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Dependency] Could not import directly!")
		raise ex


@export
class LazyLoaderState(IntEnum):
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
		self._requiredState = _requiredState
		self._wrapped = None

	def __call__(self, wrapped):
		self._wrapped = wrapped
		# If it's a function, we update metadata.
		# If it's a property, it doesn't support update_wrapper directly.
		if hasattr(wrapped, "__name__"):
			update_wrapper(self, wrapped)

		return self

	def __get__(self, obj, objtype=None):
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
			return self._wrapped(obj, *args, **kwargs)

		return wrapper


@export
class LazyLoadableMixin(metaclass=ExtendedType, mixin=True):
	__lazy_state__: LazyLoaderState
	__lazy_lock__:  RLock

	def __init__(self, targetLevel: LazyLoaderState = LazyLoaderState.Initialized) -> None:
		self.__lazy_state__ = LazyLoaderState.Initialized
		self.__lazy_lock__ = RLock()

		if targetLevel > self.__lazy_state__:
			with self.__lazy_lock__:
				self.__lazy_loader__(targetLevel)

	@abstractmethod
	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		pass


@export
class Distribution(metaclass=ExtendedType, slots=True):
	_filename:   str
	_url:        URL
	_uploadTime: datetime

	def __init__(self, filename: str, url: Union[str, URL], uploadTime: datetime) -> None:
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
		return self._filename

	@readonly
	def URL(self) -> URL:
		return self._url

	@readonly
	def UploadTime(self) -> datetime:
		return self._uploadTime

	def __repr__(self) -> str:
		return f"Distribution: {self._filename}"

	def __str__(self) -> str:
		return f"{self._filename}"


@export
class Release(PackageVersion, LazyLoadableMixin):
	_files:        List[Distribution]
	_requirements: Dict[Union[str, None], List[Requirement]]

	_api:          Nullable[URL]
	_session:      Nullable[Session]

	def __init__(
		self,
		version:      PythonVersion,
		timestamp:    datetime,
		files:        Nullable[Iterable[Distribution]] = None,
		requirements: Nullable[Mapping[str, List[Requirement]]] = None,
		project:      Nullable["Project"] = None,
		lazy:         LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
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
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.PostProcess()

	@lazy(LazyLoaderState.PostProcessed)
	@PackageVersion.DependsOn.getter
	def DependsOn(self) -> Dict["Package", Dict[SemanticVersion, "PackageVersion"]]:
		return super().DependsOn

	@readonly
	def Project(self) -> "Project":
		return self._package

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Files(self) -> List[Distribution]:
		return self._files

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Requirements(self) -> Dict[str, List[Requirement]]:
		return self._requirements

	def _GetPyPIEndpoint(self) -> str:
		return f"{self._package._name.lower()}/{self._version}/json"

	def DownloadDetails(self) -> None:
		if self._session is None:
			# TODO: NoSessionAvailableException
			raise ToolingException(f"No session available.")

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response.status_code == 404:
				# TODO: ReleaseNotFoundException
				raise ToolingException(f"Release '{self._version}' of package '{self._package._name}' not found.")

		self.UpdateDetailsFromPyPIJSON(response.json())

		index: PythonPackageIndex = self._package._storage
		for requirement in self._requirements[None]:
			packageName = requirement.name
			index.DownloadProject(packageName, True)

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
		infoNode = json["info"]
		if (extras := infoNode["provides_extra"]) is not None:
			self._requirements = {extra: [] for extra in extras}
			self._requirements[None] = []

		if (requirements := infoNode["requires_dist"]) is not None:
			brokenRequirements = []
			for requirement in requirements:
				req = Requirement(requirement)

				# Handle requirements without an extra marker
				if req.marker is None:
					self._requirements[None].append(req)
					continue

				for extra in self._requirements.keys():
					if extra is not None and req.marker.evaluate({"extra": extra}):
						self._requirements[extra].append(req)
						break
				else:
					brokenRequirements.append(req)

			# TODO: raise a warning
			if len(brokenRequirements) > 0:
				self._requirements[0] = brokenRequirements

		self.__lazy_state__ = LazyLoaderState.FullyLoaded

	def PostProcess(self) -> None:
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
		return f"Release: {self._package._name}:{self._version} Files: {len(self._files)}"

	def __str__(self) -> str:
		return f"{self._version}"


@export
class Project(Package, LazyLoadableMixin):
	_url:         Nullable[URL]

	_api:         Nullable[URL]
	_session:     Nullable[Session]

	def __init__(
		self,
		name:     str,
		url:      Union[str, URL],
		releases: Nullable[Iterable[Release]] = None,
		index:    Nullable["PythonPackageIndex"] = None,
		lazy:     LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
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
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.DownloadReleaseDetails()

	@readonly
	def PackageIndex(self) -> "PythonPackageIndex":
		return self._storage

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def URL(self) -> URL:
		return self._url

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Releases(self) -> Dict[PythonVersion, Release]:
		return self._versions

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def ReleaseCount(self) -> int:
		return len(self._versions)

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def LatestRelease(self) -> Release:
		return firstValue(self._versions)

	def _GetPyPIEndpoint(self) -> str:
		return f"{self._name.lower()}/json"

	def DownloadDetails(self) -> None:
		if self._session is None:
			# TODO: NoSessionAvailableException
			raise ToolingException(f"No session available.")

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response.status_code == 404:
				# TODO: ReleaseNotFoundException
				raise ToolingException(f"Package '{self._name}' not found.")

		self.UpdateDetailsFromPyPIJSON(response.json())

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
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
		async def ParallelDownloadReleaseDetails():
			async def routine(session, release: Release):
				if Parts.Postfix in release._version._parts:
					pass

				async with session.get(self._GetPyPIEndpoint()) as response:
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

				# TODO: raise a warning
				for release, ex in delList:
					print(f"  Removing {release.Project._name} {release.Version} - {ex}")
					del self.Releases[release.Version]

		asyncio_run(ParallelDownloadReleaseDetails())
		self.__lazy_state__ = LazyLoaderState.PostProcessed

	def __repr__(self) -> str:
		return f"Project: {self._name} latest: {self.LatestRelease._version}"

	def __str__(self) -> str:
		return f"{self._name}"


@export
class PythonPackageIndex(PackageStorage):
	_url:     URL

	_api:     URL
	_session: Session

	def __init__(self, name: str, url: Union[str, URL], api: Union[str, URL], graph: "PackageDependencyGraph") -> None:
		super().__init__(name, graph)

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
		return self._url

	@readonly
	def API(self) -> URL:
		return self._api

	@readonly
	def Projects(self) -> Dict[str, Project]:
		return self._packages

	@readonly
	def ProjectCount(self) -> int:
		return len(self._packages)

	def _GetPyPIEndpoint(self, projectName: str) -> str:
		return f"{self._api}{projectName.lower()}/json"

	def DownloadProject(self, projectName: str, lazy: LazyLoaderState = LazyLoaderState.PartiallyLoaded) -> Project:
		project = Project(projectName, "", index=self, lazy=lazy)

		return project

	def __repr__(self) -> str:
		return f"{self._name}"

	def __str__(self) -> str:
		return f"{self._name}"


@export
class PythonPackageDependencyGraph(PackageDependencyGraph):
	def __init__(self, name: str) -> None:
		super().__init__(name)
