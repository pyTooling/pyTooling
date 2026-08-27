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
Unit tests for :mod:`pyTooling.Dependency.Python`. The ``PyPI`` testcases talk to the real index, so they
need network access.
"""
from datetime                    import datetime

from pytest                      import mark

from pyTooling.Dependency.Python import PythonPackageDependencyGraph, PythonPackageIndex, Project, Release, LazyLoaderState
from pyTooling.Dependency        import BrokenRequirementWarning
from pyTooling.Versioning        import PythonVersion
from pyTooling.Warning           import WarningCollector
from pyTooling.Testing           import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
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


class PyPI(Testcase):
	def test_pyTooling(self) -> None:
		print()

		graph = PythonPackageDependencyGraph("pyTooling")
		pypi = PythonPackageIndex("PyPI", "https://pypi.org", "https://pypi.org/pypi/", graph=graph)

		project = pypi.DownloadProject("pyTooling", LazyLoaderState.PartiallyLoaded)

		self.assertEqual("pyTooling", project.Name)
		self.assertEqual("https://pypi.org/project/pyTooling/", str(project.URL))
		self.assertGreaterEqual(len(project), 84)

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
		self.assertGreaterEqual(len(project), 39)

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
		self.assertGreaterEqual(len(project), 23)

		for release in project:
			print(f"{release!r}")
			self.assertEqual(project, release.Package)
			self.assertEqual(0, len(release))


class Requirements(Testcase):
	"""How UpdateDetailsFromPyPIJSON sorts requirements into the extras they belong to."""

	@staticmethod
	def _release() -> Release:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		project = Project("project", "https://index.org/project/", index=index)

		return Release(PythonVersion.Parse("v1.0.0"), datetime.now(), project=project)

	@staticmethod
	def _json(extras, requirements) -> dict:
		return {"info": {"provides_extra": extras, "requires_dist": requirements}}

	def test_Requirement(self) -> None:
		"""A requirement without a marker is unconditional, so it lands under ``None``."""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(self._json(["terminal"], ["pyTooling >= 8.0"]))

		self.assertEqual(["pyTooling"], [req.name for req in release.Requirements[None]])
		self.assertEqual([], release.Requirements["terminal"])

	def test_Requirement_Extra(self) -> None:
		"""A requirement carrying an ``extra`` marker lands under that extra."""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(self._json(["terminal"], ['colorama >= 0.4; extra == "terminal"']))

		self.assertEqual(["colorama"], [req.name for req in release.Requirements["terminal"]])
		self.assertEqual([], release.Requirements[None])

	def test_Requirement_EnvironmentMarker(self) -> None:
		"""A marker naming no extra conditions the requirement on the environment, so it lands under ``None``."""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(
			self._json(["terminal"], ['importlib-resources ~= 3.0; python_version < "3.7"'])
		)

		self.assertEqual(["importlib-resources"], [req.name for req in release.Requirements[None]])
		self.assertEqual([], release.Requirements["terminal"])

	def test_Requirement_ExtraAndEnvironmentMarker(self) -> None:
		"""A marker naming an extra *and* an environment lands under that extra."""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(
			self._json(["terminal"], ['colorama >= 0.4; extra == "terminal" and sys_platform == "win32"'])
		)

		self.assertEqual(["colorama"], [req.name for req in release.Requirements["terminal"]])
		self.assertEqual([], release.Requirements[None])

	def test_Requirement_NormalizedExtra(self) -> None:
		"""``code_style`` and ``code-style`` are the same extra, so the declared spelling stays the key."""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(self._json(["code_style"], ['pre-commit ~= 2.12; extra == "code_style"']))

		self.assertEqual(["pre-commit"], [req.name for req in release.Requirements["code_style"]])

	def test_Requirement_UndeclaredExtras(self) -> None:
		"""
		Metadata without ``provides_extra`` gets its extras from the markers.

		Older releases have no ``provides_extra`` field at all - dropping every requirement that names an extra would
		empty exactly the releases a version-aware graph exists to look at. There is no declared spelling to keep in
		that case, so the key is the canonical one: ``theme_furo`` is recovered as ``theme-furo``.
		"""
		release = self._release()

		release.UpdateDetailsFromPyPIJSON(self._json(None, [
			"sphinx <5, >=3",
			'importlib-resources ~= 3.0; python_version < "3.7"',
			'pytest ~= 5.4; extra == "testing"',
			'furo == 2021.7.5; extra == "theme_furo"',
		]))

		self.assertEqual({None, "testing", "theme-furo"}, set(release.Requirements))
		self.assertEqual(["sphinx", "importlib-resources"], [req.name for req in release.Requirements[None]])
		self.assertEqual(["pytest"], [req.name for req in release.Requirements["testing"]])
		self.assertEqual(["furo"], [req.name for req in release.Requirements["theme-furo"]])

	def test_Requirement_UnknownExtra(self) -> None:
		"""A requirement naming an extra the release doesn't provide is reported as a warning."""
		release = self._release()
		json = self._json(["terminal"], ['lxml >= 6.1; extra == "xml"'])

		with WarningCollector(handler=lambda warning: False) as collector:
			release.UpdateDetailsFromPyPIJSON(json)

		self.assertEqual(1, len(collector.Warnings))
		self.assertIsInstance(collector.Warnings[0], BrokenRequirementWarning)
		self.assertEqual([f"Broken requirement: lxml>=6.1; extra == \"xml\""], collector.Warnings[0].__notes__)


class ReleaseDetails(Testcase):
	"""Downloading the details of every release of a project."""

	def test_EachReleaseGetsItsOwnRequirements(self) -> None:
		"""
		Every release is filled from its own endpoint, not from the project's.

		The project's endpoint describes the *latest* release, so filling every release from it gave them all the
		newest release's requirements. ``sphinx_design`` shows the difference: 0.0.1 needs ``importlib-resources``
		and the current release doesn't.
		"""
		print()

		graph = PythonPackageDependencyGraph("sphinx_design")
		pypi = PythonPackageIndex("PyPI", "https://pypi.org", "https://pypi.org/pypi/", graph=graph)

		project = pypi.DownloadProject("sphinx_design", LazyLoaderState.PartiallyLoaded)
		project.DownloadReleaseDetails()

		oldest = project.Releases[min(project.Releases)]
		latest = project.LatestRelease

		oldestRequirements = {requirement.name for requirement in oldest.Requirements[None]}
		latestRequirements = {requirement.name for requirement in latest.Requirements[None]}

		print(f"{oldest.Version}: {sorted(oldestRequirements)}")
		print(f"{latest.Version}: {sorted(latestRequirements)}")

		self.assertIn("importlib-resources", oldestRequirements)
		self.assertNotIn("importlib-resources", latestRequirements)
		self.assertNotEqual(oldestRequirements, latestRequirements)
