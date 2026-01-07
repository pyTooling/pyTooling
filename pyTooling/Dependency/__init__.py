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
from typing   import Optional as Nullable, Dict, Union, Iterable, Set, Self, Iterator

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType, abstractmethod, mustoverride
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName, firstKey
	from pyTooling.Versioning  import SemanticVersion
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Dependency] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, abstractmethod, mustoverride
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName, firstKey
		from Versioning          import SemanticVersion
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Dependency] Could not import directly!")
		raise ex


@export
class PackageVersion(metaclass=ExtendedType, slots=True):
	"""
	The package's version of a :class:`Package`.

	A :class:`Package` has multiple available versions. A version can have multiple dependencies to other
	:class:`PackageVersion`s.
	"""

	_package:    "Package"                                                #: Reference to the corresponding package
	_version:    SemanticVersion                                          #: :class:`SemanticVersion` of this package version.
	_releasedAt: Nullable[datetime]

	_dependsOn: Dict["Package", Dict[SemanticVersion, "PackageVersion"]]  #: Versioned dependencies to other packages.

	def __init__(self, version: SemanticVersion, package: "Package", releasedAt: Nullable[datetime] = None) -> None:
		"""
		Initializes a package version.

		:param version:           Semantic version of this package.
		:param package:           Package this version is associated to.
		:param releasedAt:        Optional release date and time.
		:raises TypeError:        When parameter 'version' is not of type 'SemanticVersion'.
		:raises TypeError:        When parameter 'package' is not of type 'Package'.
		:raises TypeError:        When parameter 'releasedAt' is not of type 'datetime'.
		:raises ToolingException: When version already exists for the associated package.
		"""
		if not isinstance(version, SemanticVersion):
			ex = TypeError("Parameter 'version' is not of type 'SemanticVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex
		elif version in package._versions:
			raise ToolingException(f"Version '{version}' is already registered in package '{package._name}'.")

		self._version = version
		package._versions[version] = self

		if not isinstance(package, Package):
			ex = TypeError("Parameter 'package' is not of type 'Package'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(package)}'.")
			raise ex

		self._package = package

		if releasedAt is not None and not isinstance(releasedAt, datetime):
			ex = TypeError("Parameter 'releasedAt' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(releasedAt)}'.")
			raise ex

		self._releasedAt = releasedAt

		self._dependsOn = {}

	@readonly
	def Package(self) -> "Package":
		"""
		Read-only property to access the associated package.

		:returns: Associated package.
		"""
		return self._package

	@readonly
	def Version(self) -> SemanticVersion:
		"""
		Read-only property to access the semantic version of a package.

		:returns: Semantic version of a package.
		"""
		return self._version

	@readonly
	def ReleasedAt(self) -> Nullable[datetime]:
		"""
		Read-only property to access the release date and time.

		:returns: Optional release date and time.
		"""
		return self._releasedAt

	@readonly
	def DependsOn(self) -> Dict["Package", Dict[SemanticVersion, "PackageVersion"]]:
		"""
		Read-only property to access the dictionary of dictionaries referencing dependencies.

		The outer dictionary key groups dependencies by :class:`Package`. |br|
		The inner dictionary key accesses dependencies by :class:`~pyTooling.Versioning.SemanticVersion`.

		:returns: Dictionary of dependencies.
		"""
		return self._dependsOn

	def AddDependencyToPackageVersion(self, packageVersion: "PackageVersion") -> None:
		"""
		Add a dependency from current package version to another package version.

		:param packageVersion: Dependency to be added.
		"""
		if (package := packageVersion._package) in self._dependsOn:
			pack = self._dependsOn[package]
			if (version := packageVersion._version) in pack:
				pass
			else:
				pack[version] = packageVersion
		else:
			self._dependsOn[package] = {packageVersion._version: packageVersion}

	def AddDependencyToPackageVersions(self, packageVersions: Iterable["PackageVersion"]) -> None:
		"""
		Add multiple dependencies from current package version to a list of other package versions.

		:param packageVersions: Dependencies to be added.
		"""
		# TODO: check for iterable

		for packageVersion in packageVersions:
			if (package := packageVersion._package) in self._dependsOn:
				pack = self._dependsOn[package]
				if (version := packageVersion._version) in pack:
					pass
				else:
					pack[version] = packageVersion
			else:
				self._dependsOn[package] = {packageVersion._version: packageVersion}

	def AddDependencyTo(
		self,
		package: Union[str, Package],
		version: Union[str, SemanticVersion, Iterable[Union[str, SemanticVersion]]]
	) -> None:
		"""
		Add a dependency from current package version to another package version.

		:param package: :class:`Package` object or name of the package.
		:param version: :class:`~pyTooling.Versioning.SemanticVersion` object or version string or an iterable thereof.
		:return:
		"""
		if isinstance(package, str):
			package = self._package._storage._packages[package]
		elif not isinstance(package, Package):
			ex = TypeError(f"Parameter 'package' is not of type 'str' nor 'Package'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(package)}'.")
			raise ex

		if isinstance(version, str):
			version = SemanticVersion.Parse(version)
		elif isinstance(version, Iterable):
			for v in version:
				if isinstance(v, str):
					v = SemanticVersion.Parse(v)
				elif not isinstance(v, SemanticVersion):
					ex = TypeError(f"Parameter 'version' contains an element, which is not of type 'str' nor 'SemanticVersion'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(v)}'.")
					raise ex#

				packageVersion = package._versions[v]
				self.AddDependencyToPackageVersion(packageVersion)

			return
		elif not isinstance(version, SemanticVersion):
			ex = TypeError(f"Parameter 'version' is not of type 'str' nor 'SemanticVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		packageVersion = package._versions[version]
		self.AddDependencyToPackageVersion(packageVersion)

	def SortDependencies(self) -> Self:
		"""
		Sort versions of a package and dependencies by version, thus dependency resolution can work on pre-sorted lists and
		dictionaries.

		:returns: The instance itself (for method-chaining).
		"""
		for package, versions in self._dependsOn.items():
			self._dependsOn[package] = {version: versions[version] for version in sorted(versions.keys(), reverse=True)}
		return self

	def SolveLatest(self) -> Iterable["PackageVersion"]:
		"""
		Solve the dependency problem, while using preferably latest versions.

		.. todo::

			 Describe algorithm.

		:returns:                 A list of :class:`PackageVersion`s fulfilling the constraints of the dependency problem.
		:raises ToolingException: When there is no valid solution to the problem.
		"""
		solution: Dict["Package", "PackageVersion"] = {self._package: self}

		def _recursion(currentSolution: Dict["Package", "PackageVersion"]) -> bool:
			# 1. Identify all required packages based on current selection
			requiredPackages: Set["Package"] = set()
			for packageVersion in currentSolution.values():
				requiredPackages.update(packageVersion.DependsOn.keys())

			# 2. Identify which required packages are missing from the solution
			missingPackages = requiredPackages - currentSolution.keys()

			# Base Case: If no packages are missing, the graph is complete and valid
			if len(missingPackages) == 0:
				return True

			# 3. Pick the next package to resolve
			# (Heuristic: we just pick the first one, but could be optimized)
			targetPackage = next(iter(missingPackages))

			# 4. Determine valid candidates
			# The candidate version must satisfy the constraints of all parents currently in the solution
			allowedVersions: Nullable[Set[SemanticVersion]] = None

			for parentPackageVersion in currentSolution.values():
				if targetPackage in parentPackageVersion.DependsOn:
					# Get the set of versions allowed by this specific parent
					# (Keys of the inner dict are SemanticVersion objects)
					parentConstraints = set(parentPackageVersion.DependsOn[targetPackage].keys())

					if allowedVersions is None:
						allowedVersions = parentConstraints
					else:
						# Intersect with existing constraints (must satisfy everyone)
						allowedVersions &= parentConstraints

			# If the intersection is empty, no version satisfies all parents -> backtrack
			if not allowedVersions:
				return False

			# 5. Try candidates (sorted descending to prioritize latest)
			# We convert the set to a list and sort it reverse
			for version_key in sorted(list(allowedVersions), reverse=True):
				candidate = targetPackage.Versions[version_key]

				# 6. Check compatibility (reverse dependencies)
				# Does the candidate depend on anything we have already selected?
				# If so, does the candidate accept the version we already picked?
				isCompatible = True
				for existingPackage, existingPackageVersion in currentSolution.items():
					if existingPackage in candidate.DependsOn:
						# If candidate relies on 'existingPackage', check if 'existingPackageVersion' is in the allowed list
						if existingPackageVersion._version not in candidate.DependsOn[existingPackage]:
							isCompatible = False
							break

				if isCompatible:
					# Tentatively add to solution
					currentSolution[targetPackage] = candidate

					# Recurse
					if _recursion(currentSolution):
						return True

					# If recursion failed, remove (backtrack) and try next version
					del currentSolution[targetPackage]

			# If we run out of versions for this package, this path is dead
			return False

		# Run the solver
		if _recursion(solution):
			return list(solution.values())
		else:
			raise ToolingException(f"Could not resolve dependencies for '{self}'.")

	def __len__(self) -> int:
		"""
		Returns the number of dependencies.

		:returns: Number of dependencies.
		"""
		return len(self._dependsOn)

	def __str__(self) -> str:
		"""
		Return a string representation of this package version.

		:returns: The package's name and version.
		"""
		return f"{self._package._name} - {self._version}"


@export
class Package(metaclass=ExtendedType, slots=True):
	"""
	The package, which exists in multiple versions (:class:`PackageVersion`).
	"""
	_storage:  "PackageStorage"                       #: Reference to the package's storage.
	_name:     str                                    #: Name of the package.

	_versions: Dict[SemanticVersion, PackageVersion]  #: A dictionary of available versions for this package.

	def __init__(self, name: str, *, storage: "PackageStorage") -> None:
		"""
		Initializes a package.

		:param name:    Name of the package.
		:param storage: The package's storage.
		"""
		if not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name = name

		if not isinstance(storage, PackageStorage):
			ex = TypeError("Parameter 'storage' is not of type 'PackageStorage'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(storage)}'.")
			raise ex

		self._storage = storage
		storage._packages[name] = self

		self._versions = {}

	@readonly
	def Storage(self) -> "PackageStorage":
		"""
		Read-only property to access the package's storage.

		:returns: Package storage.
		"""
		return self._storage

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the package name.

		:returns: Name of the package.
		"""
		return self._name

	@readonly
	def Versions(self) -> Dict[SemanticVersion, PackageVersion]:
		"""
		Read-only property to access the dictionary of available versions.

		:returns: Available version dictionary.
		"""
		return self._versions

	@readonly
	def VersionCount(self) -> int:
		return len(self._versions)

	def SortVersions(self) -> None:
		"""
		Sort versions within this package in reverse order (latest first).
		"""
		self._versions = {k: self._versions[k].SortDependencies() for k in sorted(self._versions.keys(), reverse=True)}

	def __len__(self) -> int:
		"""
		Returns the number of available versions.

		:returns: Number of versions.
		"""
		return len(self._versions)

	def __iter__(self) -> Iterator[PackageVersion]:
		return iter(self._versions.values())

	def __getitem__(self, version: Union[str, SemanticVersion]) -> PackageVersion:
		"""
		Access a package version in the package by version string or semantic version.

		:param version:   Version as string or instance.
		:returns:         The package version.
		:raises KeyError: If version is not available for the package.
		"""
		if isinstance(version, str):
			version = SemanticVersion.Parse(version)
		elif not isinstance(version, SemanticVersion):
			# TODO: raise proper type error
			raise TypeError()

		return self._versions[version]

	def __str__(self) -> str:
		"""
		Return a string representation of this package.

		:returns: The package's name and latest version.
		"""
		if len(self._versions) == 0:
			return f"{self._name} (empty)"
		else:
			return f"{self._name} (latest: {firstKey(self._versions)})"


@export
class PackageStorage(metaclass=ExtendedType, slots=True):
	"""
	A storage for packages.
	"""
	_graph:    "PackageDependencyGraph"  #: Reference to the overall dependency graph data structure.
	_name:     str                       #: Package dependency graph name
	_packages: Dict[str, Package]        #: Dictionary of known packages.

	def __init__(self, name: str, graph: "PackageDependencyGraph") -> None:
		"""
		Initializes the package storage.

		:param name:  Name of the package storage.
		:param graph: PackageDependencyGraph instance (parent).
		"""
		if not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name = name

		if not isinstance(graph, PackageDependencyGraph):
			ex = TypeError("Parameter 'graph' is not of type 'PackageDependencyGraph'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(graph)}'.")
			raise ex

		self._graph = graph
		graph._storages[name] = self

		self._packages = {}

	@readonly
	def Graph(self) -> "PackageDependencyGraph":
		"""
		Read-only property to access the package dependency graph.

		:returns: Package dependency graph.
		"""
		return self._graph

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the package dependency graph's name.

		:returns: Name of the package dependency graph.
		"""
		return self._name

	@readonly
	def Packages(self) -> Dict[str, Package]:
		"""
		Read-only property to access the dictionary of known packages.

		:returns: Known packages dictionary.
		"""
		return self._packages

	@readonly
	def PackageCount(self) -> int:
		return len(self._packages)

	def CreatePackage(self, packageName: str) -> Package:
		"""
		Create a new package in the package dependency graph.

		:param packageName: Name of the new package.
		:returns:           New package's instance.
		"""
		return Package(packageName, storage=self)

	def CreatePackages(self, packageNames: Iterable[str]) -> Iterable[Package]:
		"""
		Create multiple new packages in the package dependency graph.

		:param packageNames: List of package names.
		:returns:            List of new package instances.
		"""
		return [Package(packageName, storage=self) for packageName in packageNames]

	def CreatePackageVersion(self, packageName: str, version: str) -> PackageVersion:
		"""
		Create a new package and a package version in the package dependency graph.

		:param packageName: Name of the new package.
		:param version:     Version string.
		:returns:           New package version instance.
		"""
		package = Package(packageName, storage=self)
		return PackageVersion(SemanticVersion.Parse(version), package)

	def CreatePackageVersions(self, packageName: str, versions: Iterable[str]) -> Iterable[PackageVersion]:
		"""
		Create a new package and multiple package versions in the package dependency graph.

		:param packageName: Name of the new package.
		:param versions:    List of version string.s
		:returns:           List of new package version instances.
		"""
		package = Package(packageName, storage=self)
		return [PackageVersion(SemanticVersion.Parse(version), package) for version in versions]

	def SortPackageVersions(self) -> None:
		"""
		Sort versions within all known packages in reverse order (latest first).
		"""
		for package in self._packages.values():
			package.SortVersions()

	def __len__(self) -> int:
		"""
		Returns the number of known packages.

		:returns: Number of packages.
		"""
		return len(self._packages)

	def __iter__(self) -> Iterator[Package]:
		return iter(self._packages.values())

	def __getitem__(self, name: str) -> Package:
		"""
		Access a known package in the package dependency graph by package name.

		:param name:      Name of the package.
		:returns:         The package.
		:raises KeyError: If package is not known within the package dependency graph.
		"""
		return self._packages[name]

	def __str__(self) -> str:
		"""
		Return a string representation of this graph.

		:returns: The graph's name and number of known packages.
		"""
		if len(self._packages) == 0:
			return f"{self._name} (empty)"
		else:
			return f"{self._name} ({len(self._packages)})"


@export
class PackageDependencyGraph(metaclass=ExtendedType, slots=True):
	"""
	A package dependency graph collecting all known packages.
	"""
	_name:     str                        #: Package dependency graph name
	_storages: Dict[str, PackageStorage]  #: Dictionary of known package storages.

	def __init__(self, name: str) -> None:
		"""
		Initializes the package dependency graph.

		:param name: Name of the dependency graph.
		"""
		if not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name = name

		self._storages = {}

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the package dependency graph's name.

		:returns: Name of the package dependency graph.
		"""
		return self._name

	@readonly
	def Storages(self) -> Dict[str, PackageStorage]:
		"""
		Read-only property to access the dictionary of known package storages.

		:returns: Known package storage dictionary.
		"""
		return self._storages

	# def CreatePackage(self, packageName: str) -> Package:
	# 	"""
	# 	Create a new package in the package dependency graph.
	#
	# 	:param packageName: Name of the new package.
	# 	:returns:           New package's instance.
	# 	"""
	# 	return Package(packageName, storage=self)
	#
	# def CreatePackages(self, packageNames: Iterable[str]) -> Iterable[Package]:
	# 	"""
	# 	Create multiple new packages in the package dependency graph.
	#
	# 	:param packageNames: List of package names.
	# 	:returns:            List of new package instances.
	# 	"""
	# 	return [Package(packageName, storage=self) for packageName in packageNames]
	#
	# def CreatePackageVersion(self, packageName: str, version: str) -> PackageVersion:
	# 	"""
	# 	Create a new package and a package version in the package dependency graph.
	#
	# 	:param packageName: Name of the new package.
	# 	:param version:     Version string.
	# 	:returns:           New package version instance.
	# 	"""
	# 	package = Package(packageName, storage=self)
	# 	return PackageVersion(SemanticVersion.Parse(version), package)
	#
	# def CreatePackageVersions(self, packageName: str, versions: Iterable[str]) -> Iterable[PackageVersion]:
	# 	"""
	# 	Create a new package and multiple package versions in the package dependency graph.
	#
	# 	:param packageName: Name of the new package.
	# 	:param versions:    List of version string.s
	# 	:returns:           List of new package version instances.
	# 	"""
	# 	package = Package(packageName, storage=self)
	# 	return [PackageVersion(SemanticVersion.Parse(version), package) for version in versions]

	def SortPackageVersions(self) -> None:
		"""
		Sort versions within all known packages in reverse order (latest first).
		"""
		for storage in self._storages.values():
			storage.SortPackageVersions()

	def __len__(self) -> int:
		"""
		Returns the number of known packages.

		:returns: Number of packages.
		"""
		return len(self._storages)

	def __iter__(self) -> Iterator[PackageStorage]:
		return iter(self._storages.values())

	def __getitem__(self, name: str) -> PackageStorage:
		"""
		Access a known package storage in the package dependency graph by storage name.

		:param name:      Name of the package storage.
		:returns:         The package storage.
		:raises KeyError: If package storage is not known within the package dependency graph.
		"""
		return self._storages[name]

	def __str__(self) -> str:
		"""
		Return a string representation of this graph.

		:returns: The graph's name and number of known packages.
		"""
		count = sum(len(storage) for storage in self._storages.values())
		if count == 0:
			return f"{self._name} (empty)"
		else:
			return f"{self._name} ({count})"
