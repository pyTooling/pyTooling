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
from datetime                     import datetime, timedelta, timezone
from pathlib                      import Path
from tempfile                     import TemporaryDirectory
from textwrap                     import dedent
from typing                       import Any, Optional as Nullable, Self
from unittest.mock                import patch

from packaging.requirements       import Requirement
from pytest                       import mark
from requests                     import HTTPError, Response

from pyTooling.Dependency.Python  import LazyLoaderState, Project, PythonPackageDependencyGraph, PythonPackageIndex, \
                                         Release, LicenseOverrides, RequirementsFile, RequirementsFileReference, \
                                         RETRY_ATTEMPTS, RETRY_BACKOFF, RETRY_STATUS_CODES
from pyTooling.Dependency         import BrokenRequirementWarning, CircularRequirementsFileError, \
                                         UndeclaredExtraMarkerWarning, UndeclaredExtraWarning, \
                                         UnparsableRequirementWarning, DependencyError, RequirementsFileNotFoundError, \
                                         UnknownLicenseWarning, PackageIndexError, ProjectNotFoundError, \
                                         ReleaseNotFoundError, NoSessionAvailableError, ReleaseDetailsWarning, \
                                         UnsupportedVersionWarning, AlreadyInRequirementsTreeError
from pyTooling.Configuration      import Dictionary
from pyTooling.Exceptions         import ConfigurationError
from pyTooling.Configuration.YAML import Configuration as YAMLConfiguration
from pyTooling.Licensing          import LicenseAbsence, LicenseReference, ProprietaryLicense, SPDXLicense, \
                                         UnknownLicense, WithOperator
from pyTooling.Versioning         import PythonVersion, SemanticVersion
from pyTooling.Warning            import CriticalWarning, UnhandledCriticalWarningError, WarningCollector
from pyTooling.Testing            import Testcase

from tests.unit.Dependency.FakeIndex import DocumentSession, ProjectDocument


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

	def test_Release_Requirements(self) -> None:
		"""The requirements by extra are copied as a mapping, not unpacked from its keys."""
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		project = Project("project", "https://index.org/project/", index=index)
		requirements = {"ab": [], "test": []}
		release = Release(PythonVersion.Parse("v1.0.0"), datetime.now(), requirements=requirements, project=project)

		# 'Requirements' would load the release's details from the index first; the field holds what was passed.
		self.assertEqual({"ab": [], "test": []}, release._requirements)
		self.assertIsNot(requirements, release._requirements)


class NotFoundSession:
	"""HTTP session answering every request with ``404 Not Found``, so no request leaves the process."""

	def get(self, url: str) -> Response:
		"""
		Answer a GET request with ``404 Not Found``.

		:param url: The requested URL.
		:returns:   A response with status code 404.
		"""
		response = Response()
		response.status_code = 404
		response.url =         url

		return response


class NotFound(Testcase):
	"""A project or release the package index doesn't know raises an exception carrying what was requested."""

	def test_ProjectNotFoundError(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		index._session = NotFoundSession()
		project = Project("project", "https://index.org/project/", index=index)

		with self.assertRaises(ProjectNotFoundError) as context:
			project.DownloadDetails()

		self.assertEqual("Package 'project' not found.", str(context.exception))
		self.assertEqual("project", context.exception.ProjectName)

	def test_ProjectNotFoundError_MessageOnly(self) -> None:
		with self.assertRaises(ProjectNotFoundError) as context:
			raise ProjectNotFoundError("Project not found.")

		self.assertEqual("Project not found.", str(context.exception))
		self.assertIsNone(context.exception.ProjectName)

	def test_ProjectNotFoundError_Bases(self) -> None:
		self.assertTrue(issubclass(ProjectNotFoundError, LookupError))
		self.assertTrue(issubclass(ProjectNotFoundError, DependencyError))

	def test_ReleaseNotFoundError(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		index._session = NotFoundSession()
		project = Project("project", "https://index.org/project/", index=index)
		release = Release(PythonVersion.Parse("v1.0.0"), datetime.now(), project=project)

		with self.assertRaises(ReleaseNotFoundError) as context:
			release.DownloadDetails()

		self.assertEqual("project", context.exception.ProjectName)
		self.assertIs(release.Version, context.exception.Version)

	def test_ReleaseNotFoundError_MessageOnly(self) -> None:
		with self.assertRaises(ReleaseNotFoundError) as context:
			raise ReleaseNotFoundError("Release not found.")

		self.assertEqual("Release not found.", str(context.exception))
		self.assertIsNone(context.exception.ProjectName)
		self.assertIsNone(context.exception.Version)

	def test_ReleaseNotFoundError_Bases(self) -> None:
		self.assertTrue(issubclass(ReleaseNotFoundError, LookupError))
		self.assertTrue(issubclass(ReleaseNotFoundError, DependencyError))


class ReleaseWarnings(Testcase):
	"""A warning about one release carries the release's project name and version."""

	def test_UnknownLicenseWarning(self) -> None:
		version = PythonVersion.Parse("1.2.3")
		warning = UnknownLicenseWarning(
			"License of 'project' 1.2.3 couldn't be resolved.",
			projectName="project",
			version=version
		)

		self.assertEqual("License of 'project' 1.2.3 couldn't be resolved.", str(warning))
		self.assertEqual("project", warning.ProjectName)
		self.assertIs(version, warning.Version)

	def test_UnknownLicenseWarning_MessageOnly(self) -> None:
		warning = UnknownLicenseWarning("License couldn't be resolved.")

		self.assertIsNone(warning.ProjectName)
		self.assertIsNone(warning.Version)

	def test_ReleaseDetailsWarning(self) -> None:
		version = PythonVersion.Parse("1.2.3")
		warning = ReleaseDetailsWarning(
			"Dropping release '1.2.3' of package 'project'.",
			projectName="project",
			version=version
		)

		self.assertEqual("Dropping release '1.2.3' of package 'project'.", str(warning))
		self.assertEqual("project", warning.ProjectName)
		self.assertIs(version, warning.Version)

	def test_ReleaseDetailsWarning_MessageOnly(self) -> None:
		warning = ReleaseDetailsWarning("Dropping a release.")

		self.assertIsNone(warning.ProjectName)
		self.assertIsNone(warning.Version)


class BrokenRequirementWarnings(Testcase):
	"""The warnings about a broken requirement share a base class and carry what they are about."""

	def test_Bases(self) -> None:
		for warningClass in (UnparsableRequirementWarning, UndeclaredExtraWarning):
			self.assertTrue(issubclass(warningClass, BrokenRequirementWarning))
			self.assertTrue(issubclass(warningClass, CriticalWarning))

	def test_UndeclaredExtraMarkerWarning_Base(self) -> None:
		"""A requirement under an undeclared extra is a defect of third-party metadata, not a missing dependency."""
		self.assertFalse(issubclass(UndeclaredExtraMarkerWarning, BrokenRequirementWarning))
		self.assertFalse(issubclass(UndeclaredExtraMarkerWarning, CriticalWarning))

	def test_UnparsableRequirementWarning_MessageOnly(self) -> None:
		warning = UnparsableRequirementWarning("Requirement can't be parsed.")

		self.assertIsNone(warning.Line)
		self.assertIsNone(warning.FilePath)
		self.assertIsNone(warning.LineNumber)

	def test_UndeclaredExtraMarkerWarning_MessageOnly(self) -> None:
		warning = UndeclaredExtraMarkerWarning("Requirements name an undeclared extra.")

		self.assertIsNone(warning.Release)
		self.assertTupleEqual((), warning.Requirements)

	def test_UndeclaredExtraWarning_MessageOnly(self) -> None:
		warning = UndeclaredExtraWarning("Requirement names an undeclared extra.")

		self.assertIsNone(warning.Requirement)
		self.assertIsNone(warning.Extra)
		self.assertIsNone(warning.Release)


class ProjectCache(Testcase):
	"""The index downloads a project once and remembers a project it doesn't know."""

	API = "https://api.index.org/v4/"

	def _Index(self, documents: dict[str, dict]) -> PythonPackageIndex:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", self.API, graph=graph)
		index._session = DocumentSession(self.API, documents)
		return index

	def test_SameProject(self) -> None:
		index = self._Index({"demo/json": ProjectDocument("demo", "1.0", "2.0")})

		first =  index.DownloadProject("demo")
		second = index.DownloadProject("demo")

		self.assertIs(first, second)
		self.assertListEqual(["demo/json"], index._session.Requests)
		self.assertEqual(1, index.ProjectCount)

	def test_OtherSpelling(self) -> None:
		"""Names are compared in their canonical form (PEP 503)."""
		index = self._Index({"demo_package/json": ProjectDocument("demo_package", "1.0")})

		first =  index.DownloadProject("demo_package")
		second = index.DownloadProject("Demo-Package")

		self.assertIs(first, second)
		self.assertEqual(1, len(index._session.Requests))

	def test_LoadedFurther(self) -> None:
		"""A project looked up without loading is loaded when a later lookup asks for its details."""
		index = self._Index({"demo/json": ProjectDocument("demo", "1.0")})

		project = index.DownloadProject("demo", LazyLoaderState.Initialized)
		self.assertListEqual([], index._session.Requests)

		self.assertIs(project, index.DownloadProject("demo", LazyLoaderState.PartiallyLoaded))
		self.assertListEqual(["demo/json"], index._session.Requests)
		self.assertEqual(1, len(project.Releases))

	def test_NotDownloadedTwice(self) -> None:
		"""A loaded project asked for its details again isn't downloaded again."""
		index = self._Index({"demo/json": ProjectDocument("demo", "1.0")})

		project = index.DownloadProject("demo", LazyLoaderState.PartiallyLoaded)
		project.__lazy_loader__(LazyLoaderState.FullyLoaded)

		self.assertListEqual(["demo/json"], index._session.Requests)

	def test_UnknownProject(self) -> None:
		index = self._Index({})

		with self.assertRaises(ProjectNotFoundError):
			index.DownloadProject("unknown")

		with self.assertRaises(ProjectNotFoundError) as context:
			index.DownloadProject("Unknown")

		self.assertEqual("Unknown", context.exception.ProjectName)
		self.assertIn(
			"The package index answered '404 Not Found' for it before; it isn't asked again.",
			context.exception.__notes__
		)
		self.assertListEqual(["unknown/json"], index._session.Requests)
		self.assertTupleEqual(("unknown", ), index.UnknownProjects)
		self.assertEqual(0, index.ProjectCount)

	def test_UnknownProject_LoadedFurther(self) -> None:
		"""A project looked up without loading, which turns out to be unknown, is removed from the index."""
		index = self._Index({})

		index.DownloadProject("unknown", LazyLoaderState.Initialized)
		self.assertEqual(1, index.ProjectCount)

		with self.assertRaises(ProjectNotFoundError):
			index.DownloadProject("unknown", LazyLoaderState.PartiallyLoaded)

		self.assertEqual(0, index.ProjectCount)
		self.assertTupleEqual(("unknown", ), index.UnknownProjects)

	def test_ReleaseKeepsRequiredProject(self) -> None:
		"""Downloading a release's details doesn't replace a project it requires, which was looked up before."""
		release = {"info": {"provides_extra": None, "requires_dist": ["dep >= 1.0", "unknown"]}}
		index =   self._Index({
			"demo/json":     ProjectDocument("demo", "1.0"),
			"demo/1.0/json": release,
			"dep/json":      ProjectDocument("dep", "1.0")
		})
		dep = index.DownloadProject("dep")
		with self.assertRaises(ProjectNotFoundError):
			index.DownloadProject("unknown")

		demo = index.DownloadProject("demo")
		demo.LatestRelease.DownloadDetails()

		self.assertIs(dep, index.DownloadProject("dep"))
		self.assertIs(dep, index.Projects["dep"])
		self.assertNotIn("unknown", index.Projects)


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
	def _json(extras, requirements, **info) -> dict:
		return {"info": {"provides_extra": extras, "requires_dist": requirements, **info}}

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

		broken = [warning for warning in collector.Warnings if isinstance(warning, UndeclaredExtraMarkerWarning)]

		self.assertEqual(1, len(broken))
		self.assertIs(release, broken[0].Release)
		self.assertEqual(["lxml>=6.1; extra == \"xml\""], [str(requirement) for requirement in broken[0].Requirements])
		self.assertEqual(["Broken requirement: lxml>=6.1; extra == \"xml\""], broken[0].__notes__)

	def test_Requirement_UnknownExtra_Uncollected(self) -> None:
		"""Without a collector, the non-critical warning is dropped and the requirement is left out."""
		release = self._release()
		json = self._json(["terminal"], ['lxml >= 6.1; extra == "xml"'])

		release.UpdateDetailsFromPyPIJSON(json)

		self.assertSetEqual({None, "terminal"}, set(release.Requirements))
		self.assertEqual(0, sum(len(requirements) for requirements in release.Requirements.values()))


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


class _Response:
	"""Response of :class:`_Session`: a JSON document, or ``None`` for a failed request."""

	_json: Nullable[dict[str, Any]]

	def __init__(self, json: Nullable[dict[str, Any]]) -> None:
		self._json = json

	async def __aenter__(self) -> Self:
		return self

	async def __aexit__(self, *_: Any) -> bool:
		return False

	async def json(self) -> Nullable[dict[str, Any]]:
		return self._json

	def raise_for_status(self) -> None:
		if self._json is None:
			raise ConnectionError("Request failed.")


class _Session:
	"""Replaces :class:`aiohttp.ClientSession` and answers each endpoint from a dictionary."""

	_responses: dict[str, Nullable[dict[str, Any]]]

	def __init__(self, responses: dict[str, Nullable[dict[str, Any]]]) -> None:
		self._responses = responses

	async def __aenter__(self) -> Self:
		return self

	async def __aexit__(self, *_: Any) -> bool:
		return False

	def get(self, endpoint: str) -> _Response:
		return _Response(self._responses[endpoint])


class ReleaseDetailsWarnings(Testcase):
	"""How :meth:`~pyTooling.Dependency.Python.Project.DownloadReleaseDetails` reports a release it can't read."""

	_project: Project

	def setUp(self) -> None:
		super().setUp()

		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		self._project = Project("project", "https://index.org/project/", index=index)

		file = {
			"filename":             "project.whl",
			"url":                  "https://index.org/project.whl",
			"upload_time_iso_8601": "2026-01-01T00:00:00"
		}
		self._project.UpdateDetailsFromPyPIJSON({
			"info":     {"project_url": "https://index.org/project/"},
			"releases": {"1.0.0": [file], "2.0.0": [file]}
		})

	def _download(self, broken: Nullable[dict[str, Any]]) -> None:
		"""Download the details of both releases; release 1.0.0 answers with ``broken``."""
		valid = {"info": {"provides_extra": None, "requires_dist": None}}
		responses = {"project/1.0.0/json": broken, "project/2.0.0/json": valid}

		with patch("pyTooling.Dependency.Python.ClientSession", lambda **_: _Session(responses)):
			self._project.DownloadReleaseDetails()

	def test_BrokenRequirement_Collected(self) -> None:
		"""The warning is collected and the release is kept."""
		with WarningCollector() as warnings:
			self._download({"info": {"provides_extra": [], "requires_dist": ['lxml >= 6.1; extra == "xml"']}})

		self.assertEqual(1, len([warning for warning in warnings if isinstance(warning, UndeclaredExtraMarkerWarning)]))
		self.assertEqual(0, len([warning for warning in warnings if isinstance(warning, ReleaseDetailsWarning)]))
		self.assertSetEqual({"1.0.0", "2.0.0"}, {str(version) for version in self._project.Releases})

	def test_BrokenRequirement_Uncollected(self) -> None:
		"""Without a collector, the non-critical warning is dropped and both releases are kept."""
		self._download({"info": {"provides_extra": [], "requires_dist": ['lxml >= 6.1; extra == "xml"']}})

		self.assertSetEqual({"1.0.0", "2.0.0"}, {str(version) for version in self._project.Releases})

	def test_DownloadFailed_Collected(self) -> None:
		"""The warning is collected and the release is dropped."""
		with WarningCollector() as warnings:
			self._download(None)

		dropped = [warning for warning in warnings if isinstance(warning, ReleaseDetailsWarning)]
		self.assertEqual(1, len(dropped))
		self.assertIsInstance(dropped[0].__cause__, ConnectionError)
		self.assertEqual(["2.0.0"], [str(version) for version in self._project.Releases])

	def test_DownloadFailed_Uncollected(self) -> None:
		"""Without a collector, the warning raises an :exc:`~pyTooling.Warning.UnhandledCriticalWarningError`."""
		with self.assertRaises(UnhandledCriticalWarningError) as context:
			self._download(None)

		warning = context.exception.__cause__
		self.assertIsInstance(warning, ReleaseDetailsWarning)
		self.assertIsInstance(warning.__cause__, ConnectionError)


class ProjectReleases(Testcase):
	"""How UpdateDetailsFromPyPIJSON fills a project with its releases."""

	@staticmethod
	def _project() -> Project:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)

		return Project("project", "https://index.org/project/", index=index)

	@staticmethod
	def _json(*versions: str) -> dict:
		releases = {}
		for version in versions:
			releases[version] = [{
				"filename":             f"project-{version}.tar.gz",
				"url":                  f"https://files.index.org/project-{version}.tar.gz",
				"upload_time_iso_8601": "2026-01-01T00:00:00.000000Z"
			}]

		return {"info": {"project_url": "https://index.org/project/"}, "releases": releases}

	def test_UnsupportedVersion(self) -> None:
		"""A release whose version can't be parsed is skipped and reported as a critical warning."""
		project = self._project()

		with WarningCollector() as collector:
			project.UpdateDetailsFromPyPIJSON(self._json("1.0.0", "2004d"))

		self.assertEqual(1, len(collector))

		warning = collector[0]
		self.assertIsInstance(warning, UnsupportedVersionWarning)
		self.assertEqual("Skipping release '2004d' of package 'project': version format isn't supported.", str(warning))
		self.assertEqual("project", warning.ProjectName)
		self.assertEqual("2004d", warning.Version)
		self.assertIsInstance(warning.__cause__, ValueError)
		self.assertEqual([PythonVersion.Parse("1.0.0")], list(project.Releases))

	def test_UnsupportedVersion_Uncollected(self) -> None:
		"""Without a collector, the critical warning stops filling the project."""
		project = self._project()

		with self.assertRaises(UnhandledCriticalWarningError) as context:
			project.UpdateDetailsFromPyPIJSON(self._json("1.0.0", "2004d"))

		self.assertEqual(
			"Unhandled Critical Warning: Skipping release '2004d' of package 'project': version format isn't supported.",
			str(context.exception)
		)
		self.assertIsInstance(context.exception.__cause__, UnsupportedVersionWarning)


class ProjectURLs(Testcase):
	"""How a release's project URLs are resolved from the free-text ``project_urls`` mapping."""

	@staticmethod
	def _project(overrides: Nullable[LicenseOverrides] = None) -> Project:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph,
		                           licenseOverrides=overrides)

		return Project("project", "https://index.org/project/", index=index)

	def _release(self, project: Nullable[Project] = None, version: str = "v1.0.0") -> Release:
		# 'Package.__len__' is its version count, so a project without versions is falsy - test 'is None' instead.
		return Release(PythonVersion.Parse(version), datetime.now(),
		               project=project if project is not None else self._project())

	@staticmethod
	def _resolve(release: Release, **info) -> None:
		with WarningCollector(handler=lambda warning: False):
			release.UpdateDetailsFromPyPIJSON(
				{"info": {"provides_extra": None, "requires_dist": None, **info}}
			)

	def test_EveryURLIsResolved(self) -> None:
		release = self._release()
		self._resolve(release, project_urls={
			"Source Code":   "https://github.com/org/project",
			"Documentation": "https://project.readthedocs.io",
			"Bug Tracker":   "https://github.com/org/project/issues",
			"Changelog":     "https://github.com/org/project/blob/main/CHANGELOG.md",
			"Homepage":      "https://project.org",
		})

		self.assertEqual("https://github.com/org/project", str(release.RepositoryURL))
		self.assertEqual("https://project.readthedocs.io", str(release.DocumentationURL))
		self.assertEqual("https://github.com/org/project/issues", str(release.IssueTrackerURL))
		self.assertEqual("https://github.com/org/project/blob/main/CHANGELOG.md", str(release.ChangelogURL))
		self.assertEqual("https://project.org", str(release.ProjectURL))

	def test_KeysAreMatchedCaseInsensitively(self) -> None:
		"""``project_urls`` keys are free text, so the spelling of the key can't be relied on."""
		release = self._release()
		self._resolve(release, project_urls={"  SOURCE  ": "https://github.com/org/project"})

		self.assertEqual("https://github.com/org/project", str(release.RepositoryURL))

	def test_TheMostSpecificAliasWins(self) -> None:
		"""A project naming both, ``Source Code`` is the more specific statement."""
		release = self._release()
		self._resolve(release, project_urls={
			"GitHub":      "https://github.com/org/mirror",
			"Source Code": "https://github.com/org/project",
		})

		self.assertEqual("https://github.com/org/project", str(release.RepositoryURL))

	def test_HomePageIsTheFallbackForTheHomepage(self) -> None:
		"""The legacy ``home_page`` field answers when ``project_urls`` names no homepage."""
		release = self._release()
		self._resolve(release, home_page="https://project.org")

		self.assertEqual("https://project.org", str(release.ProjectURL))

	def test_TheHomepageIsTheLastResortForTheRepository(self) -> None:
		"""A package index has no repository field, so an unnamed repository falls back to the homepage."""
		release = self._release()
		self._resolve(release, home_page="https://project.org")

		self.assertEqual("https://project.org", str(release.RepositoryURL))

	def test_NothingPublishedLeavesThemUnknown(self) -> None:
		release = self._release()
		self._resolve(release)

		self.assertIsNone(release.RepositoryURL)
		self.assertIsNone(release.DocumentationURL)
		self.assertIsNone(release.IssueTrackerURL)
		self.assertIsNone(release.ChangelogURL)
		self.assertIsNone(release.ProjectURL)

	def test_AnOverriddenRepositoryWins(self) -> None:
		overrides = LicenseOverrides.FromDictionary({"project": {"repository": "https://forge.org/org/project"}})
		release = self._release(self._project(overrides))
		self._resolve(release, project_urls={"Source": "https://github.com/org/project"})

		self.assertEqual("https://forge.org/org/project", str(release.RepositoryURL))

	def test_AURLCanMoveBetweenReleases(self) -> None:
		"""The reason these live on the release: a project that migrates forge has two different answers."""
		project = self._project()
		old = self._release(project, "v1.0.0")
		new = self._release(project, "v2.0.0")

		self._resolve(old, project_urls={"Source": "https://sourceforge.net/p/project"})
		self._resolve(new, project_urls={"Source": "https://github.com/org/project"})

		self.assertEqual("https://sourceforge.net/p/project", str(old.RepositoryURL))
		self.assertEqual("https://github.com/org/project", str(new.RepositoryURL))

	def test_ThePackageMirrorsItsLatestVersion(self) -> None:
		"""A package answers for the current state of the project, which is what its newest release says."""
		project = self._project()
		# Versions are held newest-first; 'SortVersions' would establish that, but on a Project it walks the lazy
		# loader and downloads, so the order is set up by inserting the newest release first.
		new = self._release(project, "v2.0.0")
		old = self._release(project, "v1.0.0")

		self._resolve(old, project_urls={"Source": "https://sourceforge.net/p/project"})
		self._resolve(new, project_urls={
			"Source":        "https://github.com/org/project",
			"Documentation": "https://project.readthedocs.io",
		})

		self.assertIs(new, project.LatestVersion)
		self.assertEqual("https://github.com/org/project", str(project.RepositoryURL))
		self.assertEqual("https://project.readthedocs.io", str(project.DocumentationURL))

	def test_APackageWithoutVersionsHasNoURLs(self) -> None:
		project = self._project()

		self.assertIsNone(project.LatestVersion)
		self.assertIsNone(project.RepositoryURL)
		self.assertIsNone(project.DocumentationURL)


class Licenses(Testcase):
	"""How a release's license is resolved from what a package index publishes."""

	@staticmethod
	def _release(overrides: Nullable[LicenseOverrides] = None, version: str = "v1.0.0") -> Release:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph,
		                           licenseOverrides=overrides)
		project = Project("project", "https://index.org/project/", index=index)

		return Release(PythonVersion.Parse(version), datetime.now(), project=project)

	@staticmethod
	def _json(**info) -> dict:
		return {"info": {"provides_extra": None, "requires_dist": None, **info}}

	def _resolve(self, release: Release, json: dict) -> list:
		with WarningCollector(handler=lambda warning: False) as collector:
			release.UpdateDetailsFromPyPIJSON(json)

		return [warning for warning in collector.Warnings if isinstance(warning, UnknownLicenseWarning)]

	def test_LicenseExpression(self) -> None:
		"""``license_expression`` is an SPDX expression by definition, so it is trusted first."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="BSD-2-Clause")))
		self.assertEqual(["BSD-2-Clause"], [lic.Identifier for lic in release.Licenses])
		self.assertEqual("BSD-2-Clause", release.PublishedLicense)
		self.assertIsInstance(release.LicenseExpression, SPDXLicense)
		self.assertEqual("BSD-2-Clause", str(release.LicenseExpression))

	def test_LicenseExpression_Choice(self) -> None:
		"""``A OR B`` offers a choice, and both licenses are reported - the metadata doesn't say which applies."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="Apache-2.0 OR BSD-2-Clause")))
		self.assertEqual(["Apache-2.0", "BSD-2-Clause"], [lic.Identifier for lic in release.Licenses])

	def test_LicenseExpression_Conjunction(self) -> None:
		"""``A AND B`` requires both licenses."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="Apache-2.0 AND MIT")))
		self.assertEqual(["Apache-2.0", "MIT"], [lic.Identifier for lic in release.Licenses])

	def test_LicenseExpression_WithException(self) -> None:
		"""``WITH`` names a license exception, which the expression keeps and :attr:`Licenses` does not report."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="Apache-2.0 WITH LLVM-exception")))
		self.assertEqual(["Apache-2.0"], [lic.Identifier for lic in release.Licenses])
		self.assertIsInstance(release.LicenseExpression, WithOperator)
		self.assertEqual("Apache-2.0 WITH LLVM-exception", str(release.LicenseExpression))

	def test_LicenseExpression_Unknown(self) -> None:
		"""An expression naming a license SPDX doesn't define stays unresolved, but is still reported verbatim."""
		release = self._release()
		warnings = self._resolve(release, self._json(license_expression="Definitely-Not-A-License"))

		self.assertEqual(1, len(warnings))
		self.assertEqual("project", warnings[0].ProjectName)
		self.assertIs(release.Version, warnings[0].Version)
		self.assertEqual(["NOASSERTION"], [lic.Identifier for lic in release.Licenses])
		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertEqual("Definitely-Not-A-License", release.PublishedLicense)

	def test_ThePublishedTextIsStoredOnce(self) -> None:
		"""There is one home for it: the expression's ``OriginalText``. ``PackageVersion`` keeps no copy."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="Apache-2.0 OR MIT")))
		self.assertFalse(hasattr(release, "_publishedLicense"))
		self.assertEqual("Apache-2.0 OR MIT", release.LicenseExpression.OriginalText)
		self.assertEqual("Apache-2.0 OR MIT", release.PublishedLicense)

	def test_ThePublishedTextIsNotTheRenderedOne(self) -> None:
		"""``str()`` renders canonically, so the tree can't stand in for what was published."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="Apache-2.0 or MIT")))
		self.assertEqual("Apache-2.0 or MIT", release.PublishedLicense)
		self.assertEqual("Apache-2.0 OR MIT", str(release.LicenseExpression))

	def test_AnUnparsedPublicationIsHeldOnTheExpression(self) -> None:
		"""Nothing parsed, so an 'UnknownLicense' is built - and it carries the text that didn't parse."""
		release = self._release()

		self._resolve(release, self._json(license="MIT License"))

		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertIs(LicenseAbsence.NoAssertion, release.LicenseExpression.Absence)
		self.assertEqual("MIT License", release.LicenseExpression.OriginalText)
		self.assertEqual("MIT License", release.PublishedLicense)

	def test_ALicenseReferenceIsReportedWithTheRest(self) -> None:
		"""``LicenseRef-`` names a license SPDX doesn't know; it is still a license the version is published under."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license_expression="MIT AND LicenseRef-Proprietary")))
		self.assertEqual(["MIT", "LicenseRef-Proprietary"], [lic.Identifier for lic in release.Licenses])

	def test_ALicenseReferenceCarriesNoLicenseObject(self) -> None:
		"""Which is why both kinds are a 'BaseLicense' - only the SPDX one reaches a 'License'."""
		release = self._release()

		self._resolve(release, self._json(license_expression="MIT AND LicenseRef-Proprietary"))
		spdxLicense, reference = release.Licenses

		self.assertIsInstance(spdxLicense, SPDXLicense)
		self.assertIsInstance(reference, LicenseReference)
		self.assertEqual("MIT", spdxLicense.License.SPDXIdentifier)
		self.assertEqual("Proprietary", reference.LicenseIdentifier)
		self.assertFalse(hasattr(reference, "License"))

	def test_ALicenseExceptionIsNotALicense(self) -> None:
		"""The right operand of ``WITH`` is not a 'BaseLicense', so it is not reported as one."""
		release = self._release()

		self._resolve(release, self._json(license_expression="Apache-2.0 WITH LLVM-exception"))

		self.assertEqual(["Apache-2.0"], [lic.Identifier for lic in release.Licenses])

	def test_ProprietaryClassifier(self) -> None:
		"""SPDX can't name a license that isn't published, so the classifier builds a node instead of parsing one."""
		release = self._release()
		warnings = self._resolve(release, self._json(classifiers=["License :: Other/Proprietary License"]))

		self.assertEqual([], warnings)
		self.assertIsInstance(release.LicenseExpression, ProprietaryLicense)
		self.assertEqual(["LicenseRef-Proprietary"], [lic.Identifier for lic in release.Licenses])

	def test_ProprietaryClassifierIsWhatIsReportedAsPublished(self) -> None:
		"""Nothing was parsed, so the expression holds no source text and the classifier is what was published."""
		release = self._release()

		self._resolve(release, self._json(classifiers=["License :: Other/Proprietary License"]))

		self.assertEqual("License :: Other/Proprietary License", release.LicenseExpression.OriginalText)
		self.assertEqual("License :: Other/Proprietary License", release.PublishedLicense)

	def test_NoAssertionResolvesButStillWarns(self) -> None:
		"""The *statement* resolved; the license is still unknown, which is what the warning lists."""
		release = self._release()
		warnings = self._resolve(release, self._json(license_expression="NOASSERTION"))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertIs(LicenseAbsence.NoAssertion, release.LicenseExpression.Absence)
		self.assertEqual("NOASSERTION", release.PublishedLicense)

	def test_AnAbsentLicenseIsReportedAsOne(self) -> None:
		"""It is a 'BaseLicense', so 'Licenses' carries it. Both routes give the same node; the text tells them apart."""
		stated, unresolved = self._release(), self._release()

		self._resolve(stated, self._json(license_expression="NOASSERTION"))
		self._resolve(unresolved, self._json(license="MIT License"))

		self.assertEqual(["NOASSERTION"], [lic.Identifier for lic in stated.Licenses])
		self.assertEqual(["NOASSERTION"], [lic.Identifier for lic in unresolved.Licenses])
		self.assertEqual("NOASSERTION", stated.PublishedLicense)
		self.assertEqual("MIT License", unresolved.PublishedLicense)

	def test_NoneResolvesButStillWarns(self) -> None:
		release = self._release()
		warnings = self._resolve(release, self._json(license_expression="NONE"))

		self.assertEqual(1, len(warnings))
		self.assertIs(LicenseAbsence.NoLicense, release.LicenseExpression.Absence)

	def test_LicenseField_Identifier(self) -> None:
		"""The legacy ``license`` field resolves when it holds an identifier."""
		release = self._release()

		self.assertEqual([], self._resolve(release, self._json(license="MIT")))
		self.assertEqual(["MIT"], [lic.Identifier for lic in release.Licenses])

	def test_LicenseField_Name(self) -> None:
		"""``'MIT License'`` is a name, not an identifier, so it doesn't resolve and has to be stated by hand."""
		release = self._release()
		warnings = self._resolve(release, self._json(license="MIT License"))

		self.assertEqual(1, len(warnings))
		self.assertEqual(["NOASSERTION"], [lic.Identifier for lic in release.Licenses])
		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertEqual("MIT License", release.PublishedLicense)

	def test_LicenseField_FullText(self) -> None:
		"""A ``license`` field holding the license's full text is not an identifier and isn't treated as one."""
		release = self._release()
		fullText = "Permission is hereby granted, free of charge, to any person obtaining a copy of this software"
		warnings = self._resolve(
			release, self._json(license=fullText, classifiers=["License :: OSI Approved :: MIT License"])
		)

		self.assertEqual([], warnings)
		self.assertEqual(["MIT"], [lic.Identifier for lic in release.Licenses])

	def test_Classifier(self) -> None:
		"""A classifier meaning exactly one license resolves."""
		release = self._release()
		warnings = self._resolve(release, self._json(classifiers=["Programming Language :: Python",
		                                                          "License :: OSI Approved :: Apache Software License"]))

		self.assertEqual([], warnings)
		self.assertEqual(["Apache-2.0"], [lic.Identifier for lic in release.Licenses])

	def test_Classifier_Ambiguous(self) -> None:
		"""``License :: OSI Approved :: BSD License`` means either BSD-2-Clause or BSD-3-Clause, so it is not guessed."""
		release = self._release()
		warnings = self._resolve(release, self._json(classifiers=["License :: OSI Approved :: BSD License"]))

		self.assertEqual(1, len(warnings))
		self.assertEqual(["NOASSERTION"], [lic.Identifier for lic in release.Licenses])
		self.assertIn("classifier: License :: OSI Approved :: BSD License", warnings[0].__notes__)

	def test_NoLicenseInformation(self) -> None:
		"""A release publishing nothing at all is reported, so the override file gets written."""
		release = self._release()
		warnings = self._resolve(release, self._json())

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertEqual("", release.PublishedLicense)
		self.assertEqual(["The package index published no license information."], warnings[0].__notes__)

	def test_Override_WinsOverEverything(self) -> None:
		"""An explicit statement beats the published metadata, however well-formed that is."""
		overrides = LicenseOverrides.FromDictionary({"project": {"license": "BSD-3-Clause"}})
		release = self._release(overrides)

		self.assertEqual([], self._resolve(release, self._json(license_expression="BSD-2-Clause")))
		self.assertEqual(["BSD-3-Clause"], [lic.Identifier for lic in release.Licenses])

	def test_Override_PerVersion(self) -> None:
		"""A package that relicensed has one license before the switch and another after it."""
		overrides = LicenseOverrides.FromDictionary({
			"project >=2.0": {"license": "Apache-2.0"},
			"project <2.0":  {"license": "MIT"},
		})

		old = self._release(overrides, "v1.5.0")
		new = self._release(overrides, "v2.1.0")

		self.assertEqual([], self._resolve(old, self._json()))
		self.assertEqual([], self._resolve(new, self._json()))
		self.assertEqual(["MIT"], [lic.Identifier for lic in old.Licenses])
		self.assertEqual(["Apache-2.0"], [lic.Identifier for lic in new.Licenses])

	def test_Override_LicenseURL(self) -> None:
		"""A package index has no field for the license's text, so its URL only comes from an override."""
		overrides = LicenseOverrides.FromDictionary({
			"project": {"license": "MIT", "licenseURL": "https://example.org/LICENSE.txt"}
		})
		release = self._release(overrides)

		self._resolve(release, self._json())

		self.assertEqual("https://example.org/LICENSE.txt", str(release.LicenseURL))

	def test_Override_Rejected(self) -> None:
		"""An override that doesn't parse is reported with its statement, not as unpublished metadata."""
		overrides = LicenseOverrides.FromDictionary({"project": {"license": "BSD-2-Clause-Views"}})
		release = self._release(overrides)
		warnings = self._resolve(release, self._json(license_expression="BSD-2-Clause"))

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(release.LicenseExpression, UnknownLicense)
		self.assertEqual("BSD-2-Clause-Views", release.PublishedLicense)
		self.assertEqual(
			[
				"'BSD-2-Clause-Views', stated by the license overrides, "
				"isn't a license expression 'pyTooling.Licensing' knows."
			],
			warnings[0].__notes__
		)

	def test_Override_RejectedNamesItsFile(self) -> None:
		"""Read from a file, the warning names the file to correct."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "overrides.yml"
			path.write_text(
				'version: "0.1"\nanalysedAt: 2026-09-04\npackages:\n  project:\n    license: BSD-2-Clause-Views\n',
				encoding="utf-8"
			)
			overrides = LicenseOverrides.FromFile(path)

		release = self._release(overrides)
		warnings = self._resolve(release, self._json())

		self.assertEqual(path, overrides.Path)
		self.assertEqual(1, len(warnings))
		self.assertEqual(
			[
				f"'BSD-2-Clause-Views', stated by the license override file '{path}', "
				"isn't a license expression 'pyTooling.Licensing' knows."
			],
			warnings[0].__notes__
		)

	def test_Override_NameIsNormalized(self) -> None:
		"""``ruamel.yaml`` and ``ruamel-yaml`` are the same package."""
		overrides = LicenseOverrides.FromDictionary({"Ruamel_YAML": {"license": "MIT"}})

		self.assertEqual("MIT", overrides.LicenseOf("ruamel.yaml"))
		self.assertEqual("MIT", overrides.LicenseOf("ruamel-yaml"))


class ReadingLicenseOverrides(Testcase):
	"""Reading the override file, which goes through :mod:`pyTooling.Configuration.YAML`."""

	_DIRECTORY = Path("tests/data/Dependency")

	def test_ItReadsWhatTheFileStates(self) -> None:
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")

		self.assertEqual("BSD-3-Clause", overrides.LicenseOf("colorama"))
		self.assertEqual("MIT", overrides.LicenseOf("ruamel-yaml"))
		self.assertEqual("https://github.com/igraph/igraph/blob/master/COPYING", overrides.LicenseURLOf("igraph"))
		self.assertEqual("https://github.com/igraph/igraph", overrides.RepositoryOf("igraph"))

	def test_AKeyNamingNoVersionAnswersWithoutOne(self) -> None:
		"""``igraph`` states the URLs for every version; the licenses are stated by the two narrower keys."""
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")

		self.assertIsNotNone(overrides.LicenseURLOf("igraph"))
		self.assertIsNone(overrides.LicenseOf("igraph"))

	def test_AKeyCarriesItsVersionExpression(self) -> None:
		"""The shape a requirement line has - a name, then optionally an expression."""
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")

		self.assertEqual("GPL-2.0-only", overrides.LicenseOf("igraph", SemanticVersion.Parse("0.9.0")))
		self.assertEqual("GPL-2.0-or-later", overrides.LicenseOf("igraph", SemanticVersion.Parse("0.10.5")))

	def test_ABareVersionIsAnEquality(self) -> None:
		overrides = LicenseOverrides.FromDictionary({"igraph 0.9.10": {"license": "GPL-2.0-only"}})

		self.assertEqual("GPL-2.0-only", overrides.LicenseOf("igraph", SemanticVersion.Parse("0.9.10")))
		self.assertIsNone(overrides.LicenseOf("igraph", SemanticVersion.Parse("0.9.11")))

	def test_AKeyWithoutASpaceSplitsTheSameWay(self) -> None:
		"""``igraph>=0.10`` is how a requirement line writes it, so it reads the same."""
		overrides = LicenseOverrides.FromDictionary({"igraph>=0.10": {"license": "GPL-2.0-or-later"}})

		self.assertEqual("GPL-2.0-or-later", overrides.LicenseOf("igraph", SemanticVersion.Parse("0.10.5")))

	def test_EveryFieldCanBeStatedPerVersion(self) -> None:
		"""A project that moved forge between releases has two ``repository`` statements and no special case."""
		overrides = LicenseOverrides.FromDictionary({
			"project <2.0":  {"repository": "https://old.forge/project"},
			"project >=2.0": {"repository": "https://new.forge/project"},
		})

		self.assertEqual("https://old.forge/project", overrides.RepositoryOf("project", SemanticVersion.Parse("1.9")))
		self.assertEqual("https://new.forge/project", overrides.RepositoryOf("project", SemanticVersion.Parse("2.0")))

	def test_TheNodeIsHandedOverUnconverted(self) -> None:
		""":meth:`FromDictionary` takes the configuration node itself - there is no flattening step."""
		node = YAMLConfiguration(self._DIRECTORY / "licenses.yml")["packages"]
		overrides = LicenseOverrides.FromDictionary(node)

		self.assertIsInstance(node, Dictionary)
		self.assertEqual("BSD-3-Clause", overrides.LicenseOf("colorama"))

	def test_TheAnalysisDateIsRead(self) -> None:
		"""What a package index says is as old as the request; what a human wrote is as old as the human."""
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")

		self.assertEqual(datetime(2026, 9, 2), overrides.AnalysedAt)

	def test_TheDateReadsEitherWayRound(self) -> None:
		"""Unquoted it is YAML's own date type, quoted it is a string. A configuration spells both ISO-8601."""
		unquoted = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")
		quoted =   LicenseOverrides.FromFile(self._DIRECTORY / "licenses-quoted-date.yml")

		self.assertEqual(unquoted.AnalysedAt, quoted.AnalysedAt)

	def test_AFullTimestampIsRead(self) -> None:
		"""A bare date says which day; a timestamp says which build of that day, which is what a re-check needs."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "overrides.yml"
			path.write_text(
				'version: "0.1"\nanalysedAt: 2026-09-04T21:45:00+00:00\npackages:\n  igraph:\n    license: MIT\n',
				encoding="utf-8"
			)

			overrides = LicenseOverrides.FromFile(path)

		self.assertEqual(datetime(2026, 9, 4, 21, 45, tzinfo=timezone.utc), overrides.AnalysedAt)

	def test_TheSchemaVersionIsChecked(self) -> None:
		"""It says which structure the file is written for, so a later one can be told apart rather than misread."""
		self.assertEqual(SemanticVersion(0, 1), LicenseOverrides.SCHEMA_VERSION)

		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")
		self.assertEqual("BSD-3-Clause", overrides.LicenseOf("colorama"))

	def test_AFileWithoutAVersionRaises(self) -> None:
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-no-version.yml")

		self.assertIn("states no 'version'", str(context.exception))

	def test_AFileWrittenForAnotherStructureRaises(self) -> None:
		"""Reading it anyway on the chance that it still fits is the failure mode a version field exists to stop."""
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-wrong-version.yml")

		self.assertIn("written for structure '9.9'", str(context.exception))

	def test_AFileWithoutAnAnalysisDateRaises(self) -> None:
		"""It is required, because nothing else records how old a hand-written statement is."""
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-no-date.yml")

		self.assertIn("no 'analysedAt'", str(context.exception))

	def test_AnAnalysisDateThatIsNotADateRaises(self) -> None:
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-bad-date.yml")

		self.assertIn("isn't an ISO-8601 timestamp", str(context.exception))

	def test_AnEmptyFileRaises(self) -> None:
		"""It states no analysis date either. Before #376 it crashed in the YAML backend instead."""
		with self.assertRaises(DependencyError):
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-empty.yml")

	def test_AFileWithoutPackagesStatesNothing(self) -> None:
		"""A date and no packages is a complete statement: *checked, nothing to override*."""
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses-no-packages.yml")

		self.assertEqual(datetime(2026, 9, 2), overrides.AnalysedAt)
		self.assertIsNone(overrides.LicenseOf("igraph"))

	def test_OverridesBuiltInCodeNeedNoDate(self) -> None:
		"""They are as old as the code, so the date is optional there and ``None`` when nobody passed one."""
		self.assertIsNone(LicenseOverrides.FromDictionary({"igraph": {"license": "MIT"}}).AnalysedAt)
		self.assertEqual(
			datetime(2026, 9, 2),
			LicenseOverrides.FromDictionary({"igraph": {"license": "MIT"}}, datetime(2026, 9, 2)).AnalysedAt
		)

	def test_TheRepositorysOwnOverrideFileLoads(self) -> None:
		"""The repository's own override file is read by the directive, so a format change must reach it."""
		overrides = LicenseOverrides.FromFile(Path("doc/Dependency.PackageOverrides.yaml"))

		self.assertIsNotNone(overrides.AnalysedAt)
		self.assertEqual("Apache-2.0", overrides.LicenseOf("aiohttp", SemanticVersion.Parse("3.14.3")))
		self.assertEqual("https://GitHub.com/aio-libs/aiohttp/blob/master/LICENSE.txt", overrides.LicenseURLOf("aiohttp"))

	def test_TheRepositorysOwnOverrideFileCoversTheCheckedMajorVersion(self) -> None:
		"""A license was checked against one version, so a next major version - where projects relicense - isn't covered."""
		overrides = LicenseOverrides.FromFile(Path("doc/Dependency.PackageOverrides.yaml"))

		self.assertEqual("Apache-2.0", overrides.LicenseOf("aiohttp", SemanticVersion.Parse("3.15.0")))
		self.assertIsNone(overrides.LicenseOf("aiohttp", SemanticVersion.Parse("4.0.0")))
		self.assertIsNone(overrides.LicenseOf("colorama", SemanticVersion.Parse("0.5.0")))

	def test_AMissingFileRaises(self) -> None:
		with self.assertRaises(FileNotFoundError):
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-does-not-exist.yml")

	def test_AFileThatIsNotAMappingRaises(self) -> None:
		"""#376 made this a 'ConfigurationError' naming the document; it used to be an 'AttributeError' from a node."""
		with self.assertRaises(ConfigurationError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-not-a-document.yml")

		self.assertIn("doesn't describe a mapping", str(context.exception))

	def test_APackagesNodeThatIsNotAMappingRaises(self) -> None:
		"""It used to reach ``.items()`` on a string and die there."""
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-malformed.yml")

		self.assertIn("isn't a mapping", str(context.exception))

	def test_AnUnparsableSpecifierRaises(self) -> None:
		with self.assertRaises(DependencyError) as context:
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-bad-specifier.yml")

		self.assertIn("not a specifier", str(context.exception))

class RequirementsFiles(Testcase):
	"""Reading a requirements file and the files it includes."""

	@staticmethod
	def _write(directory: Path, name: str, content: str) -> Path:
		path = directory / name
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(dedent(content).lstrip(), encoding="utf-8")

		return path

	def test_Requirements(self) -> None:
		"""Comments, blank lines and installer options are not requirements."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", """
				# a comment
				pyTooling >= 8.0

				colorama ~= 0.4.6   # trailing comment
				--index-url https://example.org/simple
			""")

			requirementsFile = RequirementsFile.Parse(path)

		self.assertEqual(["pyTooling", "colorama"], [req.name for req in requirementsFile.Requirements])
		self.assertEqual([], list(requirementsFile.ReferencedFiles))
		self.assertEqual(2, len(requirementsFile))

	def test_AnalysisDuration(self) -> None:
		"""Each file read measures its duration, the files it references included."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				pytest ~= 9.1
			""")

			requirementsFile = RequirementsFile.Parse(path)

		base = tuple(requirementsFile.ReferencedFiles)[0]

		self.assertIsInstance(requirementsFile.AnalysisDuration, timedelta)
		self.assertIsInstance(base.AnalysisDuration, timedelta)
		self.assertGreater(base.AnalysisDuration, timedelta(0))
		self.assertGreaterEqual(requirementsFile.AnalysisDuration, base.AnalysisDuration)

	def test_Includes_KeepTheTree(self) -> None:
		"""``-r`` references another file, and which file a requirement came from is not flattened away."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\n")
			self._write(root, "sub/leaf.txt", "colorama ~= 0.4.6\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				-r sub/leaf.txt
				pytest ~= 9.1
			""")

			requirementsFile = RequirementsFile.Parse(path)
			referenced = tuple(requirementsFile.ReferencedFiles)

			self.assertEqual(["pytest"], [req.name for req in requirementsFile.Requirements])
			self.assertEqual(2, len(referenced))
			self.assertEqual(["pyTooling"], [req.name for req in referenced[0]])
			self.assertEqual(["colorama"], [req.name for req in referenced[1]])
			self.assertEqual(
				["pyTooling", "colorama", "pytest"],
				[req.name for req in requirementsFile.AllRequirements]
			)

	def test_EntriesKeepTheFileOrder(self) -> None:
		"""Requirements and references are interleaved in a file, so one list keeps them in the order written."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\n")
			path = self._write(root, "requirements.txt", """
				pytest ~= 9.1
				-r base.txt
				colorama ~= 0.4.6
			""")

			entries = RequirementsFile.Parse(path).Entries

		self.assertEqual(
			["pytest", "base.txt", "colorama"],
			[entry.Path.name if isinstance(entry, RequirementsFile) else entry.name for entry in entries]
		)

	def test_EveryFileKnowsItsParentAndRoot(self) -> None:
		"""A file knows what referenced it and what the tree was read from, so a requirement can name its entrypoint."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "leaf.txt", "colorama ~= 0.4.6\n")
			self._write(root, "base.txt", "-r leaf.txt\n")
			path = self._write(root, "requirements.txt", "-r base.txt\n")

			requirementsFile = RequirementsFile.Parse(path)
			base = next(iter(requirementsFile.ReferencedFiles))
			leaf = next(iter(base.ReferencedFiles))

		self.assertIsNone(requirementsFile.Parent)
		self.assertIs(requirementsFile, requirementsFile.Root)
		self.assertIs(base, leaf.Parent)
		self.assertIs(requirementsFile, leaf.Root)

	def test_Hierarchy(self) -> None:
		"""The chain from the root down to a file, at every depth of a three-level tree."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "leaf.txt", "colorama ~= 0.4.6\n")
			self._write(root, "base.txt", "-r leaf.txt\n")
			path = self._write(root, "requirements.txt", "-r base.txt\n")

			requirementsFile = RequirementsFile.Parse(path)
			base = next(iter(requirementsFile.ReferencedFiles))
			leaf = next(iter(base.ReferencedFiles))

		self.assertEqual((requirementsFile,),             requirementsFile.Hierarchy)
		self.assertEqual((requirementsFile, base),        base.Hierarchy)
		self.assertEqual((requirementsFile, base, leaf),  leaf.Hierarchy)

	def test_TheRootKnowsEveryFileOfItsTree(self) -> None:
		"""What a documentation build registers for rebuild-on-change, and what detects a cycle while reading."""
		with TemporaryDirectory() as directory:
			# deliberately not resolved: this is the spelling macOS and Windows hand a build, and the mapping has to
			# key it the same way it keys a '-r' reference
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\n")
			self._write(root, "sub/leaf.txt", "colorama ~= 0.4.6\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				-r sub/leaf.txt
			""")

			requirementsFile = RequirementsFile.Parse(path)

		self.assertEqual(
			{path.resolve(), (root / "base.txt").resolve(), (root / "sub/leaf.txt").resolve()},
			set(requirementsFile.AnalyzedRequirementFiles)
		)
		self.assertEqual(3, len(list(requirementsFile.IterateTree())))

	def test_Includes_NearerStatementWins(self) -> None:
		"""A requirement stated by the entrypoint overrides the same package required by a file it includes."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pytest ~= 8.0\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				pytest ~= 9.1
			""")

			requirements = {req.name: req for req in RequirementsFile.Parse(path).AllRequirements}

		self.assertEqual("~=9.1", str(requirements["pytest"].specifier))

	def test_AllRequirements_KeepTheFileOrder(self) -> None:
		"""A ``-r`` line contributes where it stands, so a reference in the middle doesn't reorder the file."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\nsphinx ~= 9.1\n")
			path = self._write(root, "requirements.txt", """
				pytest ~= 9.1
				-r base.txt
				colorama ~= 0.4.6
			""")

			allRequirements = [req.name for req in RequirementsFile.Parse(path).AllRequirements]

		self.assertEqual(["pytest", "pyTooling", "sphinx", "colorama"], allRequirements)

	def test_AllRequirements_TheOverridingStatementKeepsThePosition(self) -> None:
		"""A nearer statement wins on version, but the package stays where the reference first placed it."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pytest ~= 8.0\nsphinx ~= 9.1\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				colorama ~= 0.4.6
				pytest ~= 9.1
			""")

			allRequirements = list(RequirementsFile.Parse(path).AllRequirements)

		self.assertEqual(["pytest", "sphinx", "colorama"], [req.name for req in allRequirements])
		self.assertEqual("~=9.1", str(allRequirements[0].specifier))

	def test_Includes_Cycle(self) -> None:
		"""A cycle of ``-r`` lines is raised, not read once and hidden - nobody writes one on purpose."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "other.txt", "-r requirements.txt\ncolorama ~= 0.4.6\n")
			path = self._write(root, "requirements.txt", """
				-r other.txt
				pytest ~= 9.1
			""")

			with self.assertRaises(CircularRequirementsFileError) as exceptionCapture:
				RequirementsFile.Parse(path)

		self.assertIn("other.txt", str(exceptionCapture.exception))

	def test_Includes_SelfReference(self) -> None:
		"""The shortest cycle there is."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", "-r requirements.txt\n")

			with self.assertRaises(CircularRequirementsFileError) as context:
				RequirementsFile.Parse(path)

		self.assertEqual(
			f"Requirements file '{path.resolve()}' referenced in '{path}' line 1 is already being read.",
			str(context.exception)
		)
		self.assertEqual([f"Chain: {path} → {path.resolve()}"], context.exception.__notes__)
		self.assertEqual(path.resolve(), context.exception.FilePath)
		self.assertEqual(path, context.exception.ReferencedIn)
		self.assertEqual(1, context.exception.LineNumber)

	def test_Includes_Diamond(self) -> None:
		"""Two files referencing the same third one is no cycle: it's read once, the second ``-r`` is a reference."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			common = self._write(root, "requirements.txt", "packaging >= 25.0\n")
			self._write(root, "tests/unit/requirements.txt", "-r ../../requirements.txt\npytest ~= 9.0\n")
			self._write(root, "tests/typing/requirements.txt", "-r ../../requirements.txt\nmypy ~= 2.3\n")
			path = self._write(root, "tests/requirements.txt", """
				-r unit/requirements.txt
				-r typing/requirements.txt
			""")

			requirementsFile = RequirementsFile.Parse(path)

			unit, typing = requirementsFile.ReferencedFiles
			shared, = unit.ReferencedFiles
			reference, = typing.FileReferences

			self.assertEqual(["packaging", "pytest", "mypy"], [req.name for req in requirementsFile.AllRequirements])
			self.assertEqual(4, len(requirementsFile.AnalyzedRequirementFiles))
			self.assertIs(shared, requirementsFile.AnalyzedRequirementFiles[common.resolve()])
			self.assertIs(unit, shared.Parent)
			self.assertEqual([], list(typing.ReferencedFiles))
			self.assertIs(shared, reference.Target)
			self.assertIs(typing, reference.Parent)
			self.assertEqual(common.resolve(), reference.Path)
			self.assertEqual(["packaging", "mypy"], [req.name for req in typing.AllRequirements])
			self.assertEqual([requirementsFile, unit, shared, typing], list(requirementsFile.IterateTree()))

	def test_Includes_ThreeTimes(self) -> None:
		"""Every inclusion after the first one is a reference to the same file, also one in the root itself."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 10.0\n")
			self._write(root, "a.txt", "-r base.txt\n")
			self._write(root, "b.txt", "-r base.txt\n")
			path = self._write(root, "requirements.txt", """
				-r a.txt
				-r b.txt
				-r base.txt
				pyTooling >= 10.0.0rc4
			""")

			requirementsFile = RequirementsFile.Parse(path)

			a, b = requirementsFile.ReferencedFiles
			base, = a.ReferencedFiles
			bReference, = b.FileReferences
			rootReference, = requirementsFile.FileReferences

			self.assertIs(base, bReference.Target)
			self.assertIs(base, rootReference.Target)
			self.assertEqual(4, len(requirementsFile.AnalyzedRequirementFiles))
			requirement, = requirementsFile.AllRequirements
			self.assertEqual(">=10.0.0rc4", str(requirement.specifier))

	def test_Includes_CycleThroughDiamond(self) -> None:
		"""A file referenced while it's still being read is a cycle, also next to a diamond."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "-r requirements.txt\n")
			self._write(root, "a.txt", "-r base.txt\n")
			path = self._write(root, "requirements.txt", "-r a.txt\n")

			with self.assertRaises(CircularRequirementsFileError) as context:
				RequirementsFile.Parse(path)

		self.assertEqual(path.resolve(), context.exception.FilePath)

	def test_BrokenRequirement(self) -> None:
		"""A line that isn't a requirement is reported, and the rest of the file is still read."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", """
				pytest ~= 9.1
				this is not a requirement
				colorama ~= 0.4.6
			""")

			with WarningCollector(handler=lambda warning: False) as collector:
				requirementsFile = RequirementsFile.Parse(path)

		self.assertEqual(["pytest", "colorama"], [req.name for req in requirementsFile.Requirements])
		self.assertEqual(1, len(collector.Warnings))
		warning = collector.Warnings[0]
		self.assertIsInstance(warning, UnparsableRequirementWarning)
		self.assertIsInstance(warning, BrokenRequirementWarning)
		self.assertEqual("this is not a requirement", warning.Line)
		self.assertEqual(path, warning.FilePath)
		self.assertEqual(2, warning.LineNumber)

	def test_BrokenRequirement_Uncollected(self) -> None:
		"""Without a collector, the critical warning raises an :exc:`~pyTooling.Warning.UnhandledCriticalWarningError`."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", """
				pytest ~= 9.1
				this is not a requirement
			""")

			with self.assertRaises(UnhandledCriticalWarningError) as context:
				RequirementsFile.Parse(path)

		self.assertIsInstance(context.exception.__cause__, UnparsableRequirementWarning)

	def test_MissingFile(self) -> None:
		"""A requirements file that doesn't exist is an error, not an empty list."""
		with TemporaryDirectory() as directory:
			with self.assertRaises(RequirementsFileNotFoundError) as exceptionCapture:
				RequirementsFile.Parse(Path(directory) / "nothing.txt")

		self.assertIsInstance(exceptionCapture.exception.__cause__, FileNotFoundError)

	def test_RequirementsFileNotFoundError_Bases(self) -> None:
		self.assertTrue(issubclass(RequirementsFileNotFoundError, FileNotFoundError))
		self.assertTrue(issubclass(RequirementsFileNotFoundError, DependencyError))

	def test_MissingReferencedFile(self) -> None:
		"""A ``-r`` line referencing a file that doesn't exist is an error, too."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", "-r nothing.txt\n")

			with self.assertRaises(RequirementsFileNotFoundError) as context:
				RequirementsFile.Parse(path)

		self.assertEqual(
			f"Requirements file '{(path.parent / 'nothing.txt').resolve()}' does not exist.",
			str(context.exception)
		)
		self.assertEqual((path.parent / 'nothing.txt').resolve(), context.exception.FilePath)

	def test_RequirementsFileErrors_MessageOnly(self) -> None:
		"""An exception raised with a message only carries no path."""
		with self.assertRaises(RequirementsFileNotFoundError) as notFoundCapture:
			raise RequirementsFileNotFoundError("Missing file.")

		self.assertIsNone(notFoundCapture.exception.FilePath)

		with self.assertRaises(CircularRequirementsFileError) as circularCapture:
			raise CircularRequirementsFileError("Cycle.")

		self.assertIsNone(circularCapture.exception.FilePath)
		self.assertIsNone(circularCapture.exception.ReferencedIn)
		self.assertIsNone(circularCapture.exception.LineNumber)

	def test_Parse_PathIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			RequirementsFile.Parse(None)

		self.assertEqual("Parameter 'path' is None.", str(context.exception))

	def test_Parse_PathWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFile.Parse("requirements.txt")

		self.assertEqual("Parameter 'path' is not of type 'Path'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)


class RequirementsFileInstantiation(Testcase):
	"""Building a requirements file by hand, without reading one."""

	def test_Empty(self) -> None:
		path =             Path("requirements.txt")
		requirementsFile = RequirementsFile(path)

		self.assertIs(path, requirementsFile.Path)
		self.assertIsNone(requirementsFile.Parent)
		self.assertIs(requirementsFile, requirementsFile.Root)
		self.assertEqual([], requirementsFile.Entries)
		self.assertEqual({path.resolve(): requirementsFile}, requirementsFile.AnalyzedRequirementFiles)
		self.assertIsNone(requirementsFile.AnalysisDuration)
		self.assertEqual(0, len(requirementsFile))

	def test_AnalysisDuration(self) -> None:
		duration =         timedelta(milliseconds=5)
		requirementsFile = RequirementsFile(Path("requirements.txt"), analysisDuration=duration)

		self.assertEqual(duration, requirementsFile.AnalysisDuration)

	def test_AnalysisDurationWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RequirementsFile(Path("requirements.txt"), analysisDuration=0.005)

		self.assertEqual("Parameter 'analysisDuration' is not of type 'timedelta'.", str(context.exception))
		self.assertListEqual(["Got type 'float'."], context.exception.__notes__)

	def test_Entries(self) -> None:
		pytest =           Requirement("pytest ~= 9.1")
		colorama =         Requirement("colorama ~= 0.4.6")
		requirementsFile = RequirementsFile(Path("requirements.txt"), [pytest, colorama])

		self.assertEqual([pytest, colorama], requirementsFile.Entries)
		self.assertEqual([pytest, colorama], list(requirementsFile.Requirements))
		self.assertEqual(2, len(requirementsFile))

	def test_Entries_ReferencedFile(self) -> None:
		"""A file given as an entry is referenced: it and the files it references join the tree."""
		leaf =             RequirementsFile(Path("leaf.txt"), [Requirement("colorama ~= 0.4.6")])
		base =             RequirementsFile(Path("base.txt"), [leaf])
		pytest =           Requirement("pytest ~= 9.1")
		requirementsFile = RequirementsFile(Path("requirements.txt"), [pytest, base])

		self.assertEqual([pytest, base], requirementsFile.Entries)
		self.assertIs(requirementsFile, base.Parent)
		self.assertIs(base, leaf.Parent)
		self.assertIs(requirementsFile, base.Root)
		self.assertIs(requirementsFile, leaf.Root)
		self.assertIsNone(base.AnalyzedRequirementFiles)
		self.assertIsNone(leaf.AnalyzedRequirementFiles)
		self.assertEqual(
			{
				Path("requirements.txt").resolve(): requirementsFile,
				Path("base.txt").resolve():         base,
				Path("leaf.txt").resolve():         leaf
			},
			requirementsFile.AnalyzedRequirementFiles
		)
		self.assertEqual((requirementsFile, base, leaf), leaf.Hierarchy)

	def test_Parent(self) -> None:
		"""A file naming its parent is referenced by it."""
		requirementsFile = RequirementsFile(Path("requirements.txt"))
		base =             RequirementsFile(Path("base.txt"), parent=requirementsFile)

		self.assertIs(requirementsFile, base.Parent)
		self.assertIs(requirementsFile, base.Root)
		self.assertEqual([base], requirementsFile.Entries)
		self.assertIsNone(base.AnalyzedRequirementFiles)
		self.assertIs(base, requirementsFile.AnalyzedRequirementFiles[Path("base.txt").resolve()])

	def test_PathIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			RequirementsFile(None)

		self.assertEqual("Parameter 'path' is None.", str(context.exception))

	def test_PathWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFile("requirements.txt")

		self.assertEqual("Parameter 'path' is not of type 'Path'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_EntriesNotIterable(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFile(Path("requirements.txt"), 42)

		self.assertEqual("Parameter 'entries' is not iterable.", str(context.exception))
		self.assertEqual(["Got type 'int'."], context.exception.__notes__)

	def test_EntriesElementIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			RequirementsFile(Path("requirements.txt"), [None])

		self.assertEqual("An element of parameter 'entries' is None.", str(context.exception))

	def test_EntriesElementWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFile(Path("requirements.txt"), ["pytest ~= 9.1"])

		self.assertEqual(
			"An element of parameter 'entries' is not of type 'Requirement', 'RequirementsFile' or "
			"'RequirementsFileReference'.",
			str(context.exception)
		)
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_EntriesElementAlreadyReferenced(self) -> None:
		"""A file belongs to one tree; giving a referenced file to a second one is an error."""
		base = RequirementsFile(Path("base.txt"))
		RequirementsFile(Path("requirements.txt"), [base])

		with self.assertRaises(AlreadyInRequirementsTreeError) as context:
			RequirementsFile(Path("other.txt"), [base])

		self.assertEqual(
			"Requirements file 'base.txt' is referenced by 'requirements.txt' already.",
			str(context.exception)
		)

	def test_ParentWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFile(Path("requirements.txt"), parent="requirements.txt")

		self.assertEqual("Parameter 'parent' is not of type 'RequirementsFile'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Entries_Reference(self) -> None:
		"""A reference given in ``entries`` is stated by that file; ``AllRequirements`` yields its target once."""
		base =      RequirementsFile(Path("base.txt"), [Requirement("pyTooling >= 10.0")])
		unit =      RequirementsFile(Path("unit.txt"), [base])
		reference = RequirementsFileReference(Path("base.txt"), base)
		typing =    RequirementsFile(Path("typing.txt"), [reference, Requirement("mypy ~= 2.3")])
		root =      RequirementsFile(Path("requirements.txt"), [unit, typing])

		self.assertIs(typing, reference.Parent)
		self.assertIs(base, reference.Target)
		self.assertEqual([reference], list(typing.FileReferences))
		self.assertEqual(["pyTooling", "mypy"], [req.name for req in root.AllRequirements])
		self.assertEqual("base.txt (referenced before)", str(reference))
		self.assertEqual("typing.txt: 1 requirement(s), 1 referenced file(s)", str(typing))

	def test_Reference_Parent(self) -> None:
		base =      RequirementsFile(Path("base.txt"))
		parent =    RequirementsFile(Path("requirements.txt"))
		reference = RequirementsFileReference(Path("base.txt"), base, parent=parent)

		self.assertIs(parent, reference.Parent)
		self.assertEqual([reference], parent.Entries)

	def test_Reference_Unstated(self) -> None:
		reference = RequirementsFileReference(Path("base.txt"), RequirementsFile(Path("base.txt")))

		self.assertIsNone(reference.Parent)

	def test_Reference_PathIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			RequirementsFileReference(None, RequirementsFile(Path("base.txt")))

		self.assertEqual("Parameter 'path' is None.", str(context.exception))

	def test_Reference_PathWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFileReference("base.txt", RequirementsFile(Path("base.txt")))

		self.assertEqual("Parameter 'path' is not of type 'Path'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Reference_TargetIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			RequirementsFileReference(Path("base.txt"), None)

		self.assertEqual("Parameter 'target' is None.", str(context.exception))

	def test_Reference_TargetWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFileReference(Path("base.txt"), "base.txt")

		self.assertEqual("Parameter 'target' is not of type 'RequirementsFile'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Reference_ParentWrongType(self) -> None:
		with self.assertRaises(TypeError) as context:
			RequirementsFileReference(Path("base.txt"), RequirementsFile(Path("base.txt")), parent="requirements.txt")

		self.assertEqual("Parameter 'parent' is not of type 'RequirementsFile'.", str(context.exception))

	def test_EntriesElementAlreadyStated(self) -> None:
		"""A reference belongs to one file; giving it to a second one is an error."""
		reference = RequirementsFileReference(Path("base.txt"), RequirementsFile(Path("base.txt")))
		RequirementsFile(Path("unit.txt"), [reference])

		with self.assertRaises(AlreadyInRequirementsTreeError) as context:
			RequirementsFile(Path("typing.txt"), [reference])

		self.assertEqual(
			"Reference to requirements file 'base.txt' is stated by 'unit.txt' already.",
			str(context.exception)
		)


class IndexSessionRetries(Testcase):
	"""A package index is a third party over the network, so a transient failure is retried rather than reported."""

	@staticmethod
	def _Index() -> PythonPackageIndex:
		graph = PythonPackageDependencyGraph("retries")

		return PythonPackageIndex("index", "https://pypi.org", "https://pypi.org/pypi/", graph, LicenseOverrides())

	def test_TheSessionRetries(self) -> None:
		retries = self._Index()._session.get_adapter("https://pypi.org/pypi/colorama/json").max_retries

		self.assertEqual(RETRY_ATTEMPTS, retries.total)
		self.assertEqual(RETRY_BACKOFF, retries.backoff_factor)
		self.assertEqual(RETRY_STATUS_CODES, tuple(retries.status_forcelist))

	def test_TheAPIMayBeOnAnotherHost(self) -> None:
		"""Mounted per scheme, not per host, so an index serving its API elsewhere retries too."""
		session = self._Index()._session

		for url in ("https://pypi.org/pypi/x/json", "https://files.pythonhosted.org/x", "http://localhost/simple"):
			with self.subTest(url=url):
				self.assertEqual(RETRY_ATTEMPTS, session.get_adapter(url).max_retries.total)

	def test_OnlyIdempotentMethodsAreRetried(self) -> None:
		"""Retrying is safe because every request this index makes is a GET."""
		retries = self._Index()._session.get_adapter("https://pypi.org/").max_retries

		self.assertIn("GET", retries.allowed_methods)
		self.assertNotIn("POST", retries.allowed_methods)


class _ServerErrorSession:
	"""HTTP session answering every request with ``500 Internal Server Error``, so no request leaves the process."""

	def get(self, url: str) -> Response:
		"""
		Answer a GET request with ``500 Internal Server Error``.

		:param url: The requested URL.
		:returns:   A response with status code 500.
		"""
		response = Response()
		response.status_code = 500
		response.reason =      "Internal Server Error"
		response.url =         url

		return response


class NoSession(Testcase):
	"""Downloading details without a session raises, naming the project and, for a release, its version."""

	def _Project(self) -> Project:
		graph =   PythonPackageDependencyGraph("graph")
		index =   PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		project = Project("demo", "https://index.org/demo/", index=index)
		project._session = None
		return project

	def test_Project(self) -> None:
		with self.assertRaises(NoSessionAvailableError) as context:
			self._Project().DownloadDetails()

		self.assertEqual("demo", context.exception.ProjectName)
		self.assertIsNone(context.exception.Version)

	def test_Release(self) -> None:
		release = Release(PythonVersion.Parse("1.0"), datetime.now(), project=self._Project())
		release._session = None

		with self.assertRaises(NoSessionAvailableError) as context:
			release.DownloadDetails()

		self.assertEqual("demo", context.exception.ProjectName)
		self.assertEqual(PythonVersion.Parse("1.0"), context.exception.Version)

	def test_MessageOnly(self) -> None:
		with self.assertRaises(NoSessionAvailableError) as context:
			raise NoSessionAvailableError("No session.")

		self.assertIsNone(context.exception.ProjectName)
		self.assertIsNone(context.exception.Version)


class HTTPErrors(Testcase):
	"""An HTTP error other than ``404 Not Found`` raises a ``PackageIndexError``, instead of being parsed as JSON."""

	def test_Project_ServerError(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		index._session = _ServerErrorSession()
		project = Project("project", "https://index.org/project/", index=index)

		with self.assertRaises(PackageIndexError) as context:
			project.DownloadDetails()

		self.assertEqual("Package index responded 500 Internal Server Error for package 'project'.", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, HTTPError)
		self.assertEqual("project", context.exception.ProjectName)
		self.assertIsNone(context.exception.Version)

	def test_Release_ServerError(self) -> None:
		graph = PythonPackageDependencyGraph("graph")
		index = PythonPackageIndex("index", "https://index.org/", "https://api.index.org/v4/", graph=graph)
		index._session = _ServerErrorSession()
		project = Project("project", "https://index.org/project/", index=index)
		release = Release(PythonVersion.Parse("v1.0.0"), datetime.now(), project=project)

		with self.assertRaises(PackageIndexError) as context:
			release.DownloadDetails()

		self.assertEqual(
			"Package index responded 500 Internal Server Error for release 'v1.0.0' of package 'project'.",
			str(context.exception)
		)
		self.assertIsInstance(context.exception.__cause__, HTTPError)
		self.assertEqual("project", context.exception.ProjectName)
		self.assertEqual(PythonVersion.Parse("v1.0.0"), context.exception.Version)

