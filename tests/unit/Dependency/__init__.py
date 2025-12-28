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
"""Unit tests for :mod:`pyTooling.Dependency`."""
from unittest             import TestCase

from pyTooling.Exceptions import ToolingException
from pyTooling.Versioning import SemanticVersion

from pyTooling.Dependency import PackageDependencyGraph, PackageStorage, Package, PackageVersion


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Graph(self) -> None:
		graph = PackageDependencyGraph("graph")

		self.assertEqual("graph", graph.Name)
		self.assertEqual(0, len(graph))
		self.assertEqual(0, len(graph.Storages))
		self.assertEqual("graph (empty)", str(graph))

	def test_Storage(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		self.assertIs(graph, storage.Graph)
		self.assertEqual("storage", storage.Name)
		self.assertEqual(0, len(storage))
		self.assertEqual(0, len(storage.Packages))
		self.assertEqual("storage (empty)", str(storage))

	def test_Package(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		package = Package("pack", storage=storage)

		self.assertEqual(1, len(graph))
		self.assertEqual(1, len(graph.Storages))

		self.assertIs(graph, storage.Graph)
		self.assertEqual(1, len(storage))
		self.assertEqual(1, len(storage.Packages))

		self.assertIs(storage, package.Storage)
		self.assertEqual("pack", package.Name)
		self.assertEqual(0, len(package))
		self.assertEqual(0, len(package.Versions))
		self.assertEqual("pack (empty)", str(package))

	def test_CreatePackage(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		package = storage.CreatePackage("pack")

		self.assertEqual(1, len(storage))
		self.assertEqual(1, len(storage.Packages))

		self.assertIs(storage, package.Storage)
		self.assertEqual("pack", package.Name)
		self.assertEqual(0, len(package))
		self.assertEqual(0, len(package.Versions))
		self.assertEqual("pack (empty)", str(package))

	def test_CreatePackages(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		for i, package in enumerate(storage.CreatePackages((
			"pack1",
			"pack2",
		)), start=1):
			self.assertIs(storage, package.Storage)
			self.assertEqual(f"pack{i}", package.Name)
			self.assertEqual(0, len(package))
			self.assertEqual(0, len(package.Versions))
			self.assertEqual(f"pack{i} (empty)", str(package))

		self.assertEqual(2, len(storage))
		self.assertEqual(2, len(storage.Packages))

	def test_PackageVersion(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		package = Package("pack", storage=storage)
		v10 = SemanticVersion.Parse("v1.0")
		v11 = SemanticVersion.Parse("v1.1")
		packageVersion10 = PackageVersion(v10, package)
		packageVersion11 = PackageVersion(v11, package)

		graph.SortPackageVersions()

		self.assertIs(package, packageVersion10.Package)
		self.assertIs(v10, packageVersion10.Version)
		self.assertEqual("pack - v1.0", str(packageVersion10))

		self.assertIs(package, packageVersion11.Package)
		self.assertIs(v11, packageVersion11.Version)
		self.assertEqual("pack - v1.1", str(packageVersion11))

		self.assertEqual("pack (latest: v1.1)", str(package))

	def test_CreatePackageVersion(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		packageVersion = storage.CreatePackageVersion("pack", "v1.0")
		package = packageVersion.Package

		self.assertIs(storage, package.Storage)
		self.assertEqual("v1.0", packageVersion.Version)
		self.assertEqual("pack - v1.0", str(packageVersion))

	def test_CreatePackageVersions(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		for i, packageVersion in enumerate(storage.CreatePackageVersions("pack", (
			"v1.0",
			"v1.1",
			"v1.2",
		))):
			package = packageVersion.Package

			self.assertIs(storage, package.Storage)
			self.assertEqual(f"v1.{i}", packageVersion.Version)
			self.assertEqual(f"pack - v1.{i}", str(packageVersion))

		graph.SortPackageVersions()

		self.assertEqual("pack (latest: v1.2)", str(package))


class Construct(TestCase):
	def test_Package(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		package = storage.CreatePackage("pack")

		self.assertEqual("pack", package.Name)
		self.assertEqual(0, len(package))
		self.assertEqual(0, len(package.Versions))
		self.assertEqual("pack (empty)", str(package))


class DependsOn(TestCase):
	def test_ByObject(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)

		packageA = Package("packA", storage=storage)
		packageA_v10 = PackageVersion(pA_v10 := SemanticVersion.Parse("v1.0"), packageA)
		packageA_v11 = PackageVersion(pA_v11 := SemanticVersion.Parse("v1.1"), packageA)

		packageB = Package("packB", storage=storage)
		packageB_v10 = PackageVersion(pB_v10 := SemanticVersion.Parse("v1.0"), packageB)
		packageB_v20 = PackageVersion(pB_v20 := SemanticVersion.Parse("v2.0"), packageB)
		packageB_v21 = PackageVersion(pB_v21 := SemanticVersion.Parse("v2.1"), packageB)

		packageA_v10.AddDependencyTo(packageB, pB_v10)
		packageA_v11.AddDependencyTo(packageB, pB_v20)
		packageA_v11.AddDependencyTo(packageB, pB_v21)

	def test_ByName(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		root = storage.CreatePackageVersion("app", "v0.0")

		storage.CreatePackageVersions("packA", (
			"v1.0",
			"v1.1"
		))
		storage.CreatePackageVersions("packB", (
			"v1.0",
			"v2.0",
			"v2.1"
		))

		self.assertEqual(3, len(storage))

		root.AddDependencyTo("packA", "v1.0")
		root.AddDependencyTo("packA", "v1.1")

		(pAv10 := storage["packA"]["v1.0"]).AddDependencyTo("packB", "v1.0")
		(pAv11 := storage["packA"]["v1.1"]).AddDependencyTo("packB", ("v2.0", "v2.1"))

		self.assertEqual(1, len(pAv10))
		self.assertEqual(1, len(pAv11))


class SolveLatest(TestCase):
	def test_Simple(self) -> None:
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		root = storage.CreatePackageVersion("app", "v1.0")

		packA = storage.CreatePackageVersions("packA", ("v1.0", "v1.1", "v1.2"))
		root.AddDependencyToPackageVersions(packA)

		graph.SortPackageVersions()
		solution = root.SolveLatest()

		self.assertIn(root, solution)
		self.assertIn(packA[2], solution)

	def test_Advanced(self) -> None:
		print()
		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		root = storage.CreatePackageVersion("app", "v0.0")

		packA = storage.CreatePackageVersions("packA", (
			"v1.0",
			"v1.1"
		))
		packB = storage.CreatePackageVersions("packB", (
			"v1.0",
			"v2.0",
			"v2.1"
		))
		packC = storage.CreatePackageVersions("packC", (
			"v1.0",
			"v1.1",
			"v1.2",
			"v1.3",
			"v1.4",
			"v2.0",
			"v2.1"
		))
		packD = storage.CreatePackageVersions("packD", (
			"v1.0",
			"v2.0",
			"v3.0"
		))

		root.AddDependencyTo("packA", ("v1.0", "v1.1"))
		root.AddDependencyTo("packC", ("v1.3", "v1.4", "v2.0", "v2.1"))

		storage["packA"]["v1.0"].AddDependencyTo("packB", "v1.0")
		storage["packA"]["v1.1"].AddDependencyTo("packB", ("v2.0", "v2.1"))
		storage["packC"]["v1.0"].AddDependencyTo("packD", "v1.0")
		storage["packC"]["v1.1"].AddDependencyTo("packD", "v1.0")
		storage["packC"]["v1.2"].AddDependencyTo("packD", ("v1.0", "v2.0"))
		storage["packC"]["v1.3"].AddDependencyTo("packD", ("v1.0", "v2.0"))
		storage["packC"]["v1.4"].AddDependencyTo("packD", ("v1.0", "v2.0", "v3.0"))
		storage["packC"]["v2.0"].AddDependencyTo("packD", ("v2.0", "v3.0"))
		storage["packC"]["v2.1"].AddDependencyTo("packD", "v3.0")

		graph.SortPackageVersions()
		solution = root.SolveLatest()

		self.assertIn(root, solution)
		self.assertIn(packA[1], solution)
		self.assertIn(packB[2], solution)
		self.assertIn(packC[6], solution)
		self.assertIn(packD[2], solution)

	def test_ConflictBacktracking(self) -> None:
		# Scenario:
		# * packA v2.0.0 (Latest) requires packB v2.0.0.
		# * But root only allows packB v1.0.0.
		# * Solver must reject packA v2.0.0 and pick packA v1.0.0 instead.

		graph = PackageDependencyGraph("graph")
		storage = PackageStorage("storage", graph=graph)
		root = storage.CreatePackageVersion("app", "v1.0")

		storage.CreatePackageVersions("packA", ("v1.0", "v2.0"))
		storage.CreatePackageVersions("packB", ("v1.0", "v2.0"))

		root.AddDependencyTo("packA", "v1.0")
		root.AddDependencyTo("packA", "v2.0")
		root.AddDependencyTo("packB", "v1.0")

		storage["packA"]["v2.0"].AddDependencyTo("packB", "v2.0")
		storage["packA"]["v1.0"].AddDependencyTo("packB", "v1.0")

		graph.SortPackageVersions()
		solution = {pv.Package.Name: pv.Version for pv in root.SolveLatest()}

		self.assertEqual(len(solution), 3)
		self.assertEqual(solution["app"],   "v1.0")
		self.assertEqual(solution["packA"], "v1.0")
		self.assertEqual(solution["packB"], "v1.0")

	def test_CircularDependency(self) -> None:
		graph = PackageDependencyGraph("Circular")
		storage = PackageStorage("storage", graph=graph)
		root = storage.CreatePackageVersion("app", "v1.0")

		pAv10 = storage.CreatePackageVersion("packA", "v1.0")
		pBv10 = storage.CreatePackageVersion("packB", "v1.0")

		root.AddDependencyToPackageVersion(pAv10)
		pAv10.AddDependencyToPackageVersion(pBv10)
		pBv10.AddDependencyToPackageVersion(pAv10)

		graph.SortPackageVersions()
		solution = {pv.Package.Name: pv.Version for pv in root.SolveLatest()}

		self.assertEqual(len(solution), 3)
		self.assertEqual(solution["app"],   "v1.0")
		self.assertEqual(solution["packA"], "v1.0")
		self.assertEqual(solution["packB"], "v1.0")

	def test_ComplexSuccessWithBacktracking(self) -> None:
		# Created by Google Gemini
		graph = PackageDependencyGraph("ComplexSuccess")
		storage = PackageStorage("storage", graph=graph)
		packages = storage.CreatePackages([f"pack{i}" for i in range(10)])

		for package in packages:
			storage.CreatePackageVersions(package.Name, ("v1.0", "v1.1", "v1.2", "v1.3"))

		root = storage["pack0"]["v1.3"]

		# 1. Greedy Path: Root prefers latest of pack1, pack2, pack3
		root.AddDependencyTo("pack1", "v1.3")
		root.AddDependencyTo("pack1", "v1.2")
		root.AddDependencyTo("pack2", "v1.3")
		root.AddDependencyTo("pack2", "v1.2")
		root.AddDependencyTo("pack3", "v1.3")

		# 2. The Conflict: pack1 v1.3.0 requires pack9 v1.3.0
		storage["pack1"]["v1.3"].AddDependencyTo("pack9", "v1.3")

		# 3. The Constraint: pack3 v1.3.0 is older-leaning; it requires pack9 v1.0.0
		# This forces the solver to backtrack from pack1 v1.3.0 to pack1 v1.2.0
		storage["pack3"]["v1.3"].AddDependencyTo("pack9", "v1.0")

		# 4. Deep Dependency: pack1 v1.2.0 depends on pack4, which depends on pack5...
		storage["pack1"]["v1.2"].AddDependencyTo("pack4", "v1.3")
		storage["pack4"]["v1.3"].AddDependencyTo("pack5", "v1.3")

		# 5. Second Backtrack: pack2 v1.3.0 requires pack5 v1.1.0
		# But pack4 v1.3.0 already locked in pack5 v1.3.0.
		# Solver must backtrack pack2 from 1.3.0 to 1.2.0.
		storage["pack2"]["v1.3"].AddDependencyTo("pack5", "v1.1")
		storage["pack2"]["v1.2"].AddDependencyTo("pack5", "v1.3")

		graph.SortPackageVersions()
		solution = {pv.Package.Name: pv.Version for pv in root.SolveLatest()}

		self.assertEqual(len(solution), 7)
		self.assertEqual(solution["pack0"], "v1.3")
		self.assertEqual(solution["pack1"], "v1.2")  # Successful backtrack 1
		self.assertEqual(solution["pack2"], "v1.2")  # Successful backtrack 2

	def test_ComplexFailureDeepConflict(self) -> None:
		# Created by Google Gemini
		graph = PackageDependencyGraph("ComplexFailure")
		storage = PackageStorage("storage", graph=graph)
		packages = storage.CreatePackages([f"pack{i}" for i in range(10)])

		for package in packages:
			storage.CreatePackageVersions(package.Name, ("v1.0", "v1.1", "v1.2", "v1.3"))

		root = storage["pack0"]["v1.3"]

		# Chain of dependencies:
		#   pack0 -> pack1 -> pack2 -> pack3 -> pack4 -> pack5 -> pack6 -> pack7 -> pack8 -> pack9
		# Each allows multiple versions to keep the search space large
		# But, every version of pack8 (which is deep in the chain) requires pack9 to be v1.0.0
		for i in range(9):
			fromPackage = storage[f"pack{i}"]
			toPackage =   storage[f"pack{i + 1}"]
			for fromPackageVersion in (fromPackage[f"v1.{v}"] for v in range(4)):
				if i == 8:
					fromPackageVersion.AddDependencyToPackageVersion(toPackage["v1.0"])
				else:
					for toPackageVersion in (toPackage[f"v1.{v}"] for v in range(4)):
						fromPackageVersion.AddDependencyToPackageVersion(toPackageVersion)

		# The impossible constraint:
		# Root requires pack9 to be v1.3.0
		root.AddDependencyTo("pack9", "v1.3")

		# This will attempt every combination of pack1..pack8 before failing
		graph.SortPackageVersions()
		with self.assertRaises(ToolingException) as ex:
			_ = root.SolveLatest()

		self.assertIn("Could not resolve dependencies", str(ex.exception))
