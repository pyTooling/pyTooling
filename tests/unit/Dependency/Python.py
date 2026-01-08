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
from datetime                    import datetime
from unittest                    import TestCase

from pytest                      import mark

from pyTooling.Dependency.Python import PythonPackageDependencyGraph, PythonPackageIndex, Project, Release, LazyLoaderState
from pyTooling.Versioning        import PythonVersion


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Graph(self) -> None:
		graph = PythonPackageDependencyGraph("graph")

	def test_Index(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)

		self.assertEqual("https://index.org/", str(index.URL))
		self.assertEqual("https://api.index.org/v4/", str(index.API))

	@mark.xfail(reason="LazyLoader algorithm conflicts with manually initialized fields.")
	def test_Project(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		project = Project("project", "https://index.org/project/", index=index)

		self.assertEqual("https://index.org/project/", str(project.URL))

	def test_Release(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		project = Project("project", "https://index.org/project/", index=index)
		release = Release(PythonVersion.Parse("v1.0.0"), (now := datetime.now()), project=project)

		self.assertEqual(now, release.ReleasedAt)


class PyPI(TestCase):
	def test_pyTooling(self) -> None:
		print()

		graph = PythonPackageDependencyGraph("pyTooling")
		pypi = PythonPackageIndex("PyPI", "https://pypi.org", "https://pypi.org/pypi/", graph=graph)

		project = pypi.DownloadProject("pyTooling", LazyLoaderState.PartiallyLoaded)

		self.assertEqual("pyTooling", project.Name)
		self.assertEqual("https://pypi.org/project/pyTooling/", str(project.URL))
		self.assertEqual(83, len(project))

		for release in project:
			self.assertEqual(project, release.Package)
			self.assertEqual(0, len(release))

	def test_pyVersioning(self) -> None:
		print()

		graph = PythonPackageDependencyGraph("pyVersioning")
		pypi = PythonPackageIndex("PyPI", "https://pypi.org", "https://pypi.org/pypi/", graph=graph)

		project = pypi.DownloadProject("pyVersioning", LazyLoaderState.PartiallyLoaded)

		self.assertEqual("pyVersioning", project.Name)
		self.assertEqual("https://pypi.org/project/pyVersioning/", str(project.URL))
		self.assertEqual(39, len(project))

		for release in project:
			self.assertEqual(project, release.Package)
			self.assertEqual(0, len(release))

	def test_SphinxReports(self) -> None:
		print()

		graph = PythonPackageDependencyGraph("sphinx-reports")
		pypi = PythonPackageIndex("PyPI", "https://pypi.org", "https://pypi.org/pypi/", graph=graph)

		project = pypi.DownloadProject("sphinx-reports", LazyLoaderState.PartiallyLoaded)

		self.assertEqual("sphinx-reports", project.Name)
		self.assertEqual("https://pypi.org/project/sphinx-reports/", str(project.URL))
		self.assertEqual(23, len(project))

		for release in project:
			print(f"{release!r}")
			self.assertEqual(project, release.Package)
			self.assertEqual(0, len(release))
