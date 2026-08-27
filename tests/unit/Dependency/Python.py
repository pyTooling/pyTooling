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
from datetime                     import date, datetime
from pathlib                      import Path
from tempfile                     import TemporaryDirectory
from textwrap                     import dedent
from typing                       import Optional as Nullable

from pytest                       import mark

from pyTooling.Dependency.Python  import LazyLoaderState, Project, PythonPackageDependencyGraph
from pyTooling.Dependency.Python  import PythonPackageIndex, Release
from pyTooling.Dependency.Python  import LicenseOverrides, RequirementsFile
from pyTooling.Dependency         import BrokenRequirementWarning, DependencyError, UnknownLicenseWarning
from pyTooling.Configuration      import Dictionary
from pyTooling.Exceptions         import ConfigurationError
from pyTooling.Configuration.YAML import Configuration as YAMLConfiguration
from pyTooling.Licensing          import LicenseAbsence, LicenseReference, BaseLicense, ProprietaryLicense
from pyTooling.Licensing          import SPDXLicense, UnknownLicense, WithOperator
from pyTooling.Versioning         import PythonVersion, SemanticVersion
from pyTooling.Warning            import WarningCollector
from pyTooling.Testing            import Testcase


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

		broken = [warning for warning in collector.Warnings if isinstance(warning, BrokenRequirementWarning)]

		self.assertEqual(1, len(broken))
		self.assertEqual([f"Broken requirement: lxml>=6.1; extra == \"xml\""], broken[0].__notes__)


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

		self.assertEqual(date(2026, 9, 2), overrides.AnalysedAt)

	def test_TheDateReadsEitherWayRound(self) -> None:
		"""Unquoted it is YAML's own date type, quoted it is a string. A configuration spells both ISO-8601."""
		unquoted = LicenseOverrides.FromFile(self._DIRECTORY / "licenses.yml")
		quoted =   LicenseOverrides.FromFile(self._DIRECTORY / "licenses-quoted-date.yml")

		self.assertEqual(unquoted.AnalysedAt, quoted.AnalysedAt)

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

		self.assertIn("isn't an ISO-8601 date", str(context.exception))

	def test_AnEmptyFileRaises(self) -> None:
		"""It states no analysis date either. Before #376 it crashed in the YAML backend instead."""
		with self.assertRaises(DependencyError):
			LicenseOverrides.FromFile(self._DIRECTORY / "licenses-empty.yml")

	def test_AFileWithoutPackagesStatesNothing(self) -> None:
		"""A date and no packages is a complete statement: *checked, nothing to override*."""
		overrides = LicenseOverrides.FromFile(self._DIRECTORY / "licenses-no-packages.yml")

		self.assertEqual(date(2026, 9, 2), overrides.AnalysedAt)
		self.assertIsNone(overrides.LicenseOf("igraph"))

	def test_OverridesBuiltInCodeNeedNoDate(self) -> None:
		"""They are as old as the code, so the date is optional there and ``None`` when nobody passed one."""
		self.assertIsNone(LicenseOverrides.FromDictionary({"igraph": {"license": "MIT"}}).AnalysedAt)
		self.assertEqual(
			date(2026, 9, 2),
			LicenseOverrides.FromDictionary({"igraph": {"license": "MIT"}}, date(2026, 9, 2)).AnalysedAt
		)

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

			requirementsFile = RequirementsFile(path)

		self.assertEqual(["pyTooling", "colorama"], [req.name for req in requirementsFile.Requirements])
		self.assertEqual([], requirementsFile.Includes)
		self.assertEqual(2, len(requirementsFile))

	def test_Includes_KeepTheTree(self) -> None:
		"""``-r`` includes another file, and which file a requirement came from is not flattened away."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pyTooling >= 8.0\n")
			self._write(root, "sub/leaf.txt", "colorama ~= 0.4.6\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				-r sub/leaf.txt
				pytest ~= 9.1
			""")

			requirementsFile = RequirementsFile(path)

			self.assertEqual(["pytest"], [req.name for req in requirementsFile.Requirements])
			self.assertEqual(2, len(requirementsFile.Includes))
			self.assertEqual(["pyTooling"], [req.name for req in requirementsFile.Includes[0]])
			self.assertEqual(["colorama"], [req.name for req in requirementsFile.Includes[1]])
			self.assertEqual({"pytooling", "colorama", "pytest"}, set(requirementsFile.Flatten()))

	def test_Includes_NearerStatementWins(self) -> None:
		"""A requirement stated by the entrypoint overrides the same package required by a file it includes."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "base.txt", "pytest ~= 8.0\n")
			path = self._write(root, "requirements.txt", """
				-r base.txt
				pytest ~= 9.1
			""")

			flattened = RequirementsFile(path).Flatten()

		self.assertEqual("~=9.1", str(flattened["pytest"].specifier))

	def test_Includes_Cycle(self) -> None:
		"""A file including itself, directly or through a cycle, is read once."""
		with TemporaryDirectory() as directory:
			root = Path(directory)
			self._write(root, "other.txt", "-r requirements.txt\ncolorama ~= 0.4.6\n")
			path = self._write(root, "requirements.txt", """
				-r other.txt
				pytest ~= 9.1
			""")

			requirementsFile = RequirementsFile(path)

		self.assertEqual({"colorama", "pytest"}, set(requirementsFile.Flatten()))

	def test_BrokenRequirement(self) -> None:
		"""A line that isn't a requirement is reported, and the rest of the file is still read."""
		with TemporaryDirectory() as directory:
			path = self._write(Path(directory), "requirements.txt", """
				pytest ~= 9.1
				this is not a requirement
				colorama ~= 0.4.6
			""")

			with WarningCollector(handler=lambda warning: False) as collector:
				requirementsFile = RequirementsFile(path)

		self.assertEqual(["pytest", "colorama"], [req.name for req in requirementsFile.Requirements])
		self.assertEqual(1, len(collector.Warnings))
		self.assertIsInstance(collector.Warnings[0], BrokenRequirementWarning)

	def test_MissingFile(self) -> None:
		"""A requirements file that doesn't exist is an error, not an empty list."""
		with TemporaryDirectory() as directory:
			with self.assertRaises(FileNotFoundError):
				RequirementsFile(Path(directory) / "nothing.txt")
