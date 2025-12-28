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
from datetime import datetime
from typing   import Optional as Nullable, List, Dict, Union, Iterable, Mapping

try:
	from aiohttp import ClientSession
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'aiohttp' not installed. Either install pyTooling with extra dependencies 'pyTooling[pypi]' or install 'aiohttp' directly.") from ex

try:
	from requests import Session
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'requests' not installed. Either install pyTooling with extra dependencies 'pyTooling[pypi]' or install 'requests' directly.") from ex

try:
	from pyTooling.Decorators      import export, readonly
	from pyTooling.MetaClasses     import ExtendedType, abstractmethod, mustoverride
	from pyTooling.Exceptions      import ToolingException
	from pyTooling.Common          import getFullyQualifiedName, firstKey
	from pyTooling.Dependency      import Package, PackageStorage, PackageVersion, PackageDependencyGraph
	from pyTooling.GenericPath.URL import URL
	from pyTooling.Versioning      import SemanticVersion, PythonVersion
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Dependency] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, abstractmethod, mustoverride
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName, firstKey, firstValue
		from Dependency          import Package, PackageStorage, PackageVersion, PackageDependencyGraph
		from GenericPath.URL     import URL
		from Versioning          import SemanticVersion, PythonVersion
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Dependency] Could not import directly!")
		raise ex


class Requirement:
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
class Release(PackageVersion):
	_files:        List[Distribution]
	_requirements: Dict[Union[str, None], List[Requirement]]

	def __init__(
		self,
		version:      PythonVersion,
		timestamp:    datetime,
		files:        Nullable[Iterable[Distribution]] = None,
		requirements: Nullable[Mapping[str, List[Requirement]]] = None,
		project:      Nullable["Project"] = None
	) -> None:
		super().__init__(version, project, timestamp)

		self._files = [file for file in files] if files is not None else []
		self._requirements = {k: v for k, v in requirements} if requirements is not None else {None: []}

	@readonly
	def Project(self) -> "Project":
		return self._package

	@readonly
	def Files(self) -> List[Distribution]:
		return self._files

	@readonly
	def Requirements(self) -> Dict[str, List[Requirement]]:
		return self._requirements

	def __repr__(self) -> str:
		return f"Release: {self._package._name}:{self._version} Files: {len(self._files)}"

	def __str__(self) -> str:
		return f"{self._version}"


@export
class Project(Package):
	_url:       URL

	def __init__(
		self,
		name:     str,
		url:      Union[str, URL],
		releases: Nullable[Iterable[Release]] = None,
		index:    Nullable["PythonPackageIndex"] = None
	) -> None:
		super().__init__(name, storage=index)

		if isinstance(url, str):
			url = URL.Parse(url)
		elif not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		self._url = url
		# self._releases = {release.Version: release for release in sorted(releases, key=lambda r: r.Version)} if releases is not None else {}

	@readonly
	def PackageIndex(self) -> "PythonPackageIndex":
		return self._storage

	@readonly
	def URL(self) -> URL:
		return self._url

	@readonly
	def Releases(self) -> Dict[PythonVersion, Release]:
		return self._releases

	@readonly
	def ReleaseCount(self) -> int:
		return len(self._releases)

	@readonly
	def LatestRelease(self) -> Release:
		return firstValue(self._versions)

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

	def __repr__(self) -> str:
		return f"{self._name}"

	def __str__(self) -> str:
		return f"{self._name}"


@export
class PythonPackageDependencyGraph(PackageDependencyGraph):
	def __init__(self, name: str) -> None:
		super().__init__(name)
