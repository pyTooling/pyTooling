# ==================================================================================================================== #
#             _____           _ _             _____         _   _                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__  ___| |_(_)_ __   __ _                                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \/ __| __| | '_ \ / _` |                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/\__ \ |_| | | | | (_| |                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___||___/\__|_|_| |_|\__, |                                         #
# |_|    |___/                          |___/                           |___/                                          #
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
Unit tests for :mod:`pyTooling.Testing`'s markers :deco:`~pyTooling.Testing.testsuite` and
:deco:`~pyTooling.Testing.testcase`.

Also for :mod:`pyTooling.Testing.PyTest`, the plugin collecting what they mark.
"""
from pathlib               import Path
from tempfile              import TemporaryDirectory
from xml.etree.ElementTree import parse as xml_parse

from pyTooling.Testing     import ApplicationTestcase, Testcase, testsuite, testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class TestsuiteMarker(Testcase):
	"""':deco:`testsuite`' attaches the title a test runner should report for a class."""

	def test_WithoutParentheses(self) -> None:
		@testsuite
		class Suite:
			pass

		self.assertEqual("Suite", Suite.__testsuite_title__)

	def test_WithEmptyParentheses(self) -> None:
		@testsuite()
		class Suite:
			pass

		self.assertEqual("Suite", Suite.__testsuite_title__)

	def test_WithATitle(self) -> None:
		@testsuite("My third set of tests.")
		class Suite:
			pass

		self.assertEqual("My third set of tests.", Suite.__testsuite_title__)

	def test_TheSummaryIsTheDocStringsFirstParagraph(self) -> None:
		@testsuite
		class Suite:
			"""
			Compare two release versions.

			Everything about comparing them.
			"""

		self.assertEqual("Suite", Suite.__testsuite_title__)
		self.assertEqual("Compare two release versions.", Suite.__testsuite_summary__)

	def test_TheDescriptionIsTheWholeDocString(self) -> None:
		@testsuite
		class Suite:
			"""
			Compare two release versions.

			Everything about comparing them.
			"""

		self.assertEqual(
			"Compare two release versions.\n\nEverything about comparing them.",
			Suite.__testsuite_description__
		)

	def test_WithoutADocStringSummaryAndDescriptionAreEmpty(self) -> None:
		@testsuite("A title.")
		class Suite:
			pass

		self.assertEqual("A title.", Suite.__testsuite_title__)
		self.assertEqual("", Suite.__testsuite_summary__)
		self.assertEqual("", Suite.__testsuite_description__)

	def test_TheTitleIsIndependentOfTheDocString(self) -> None:
		"""Four names, not a fallback chain: a title never replaces a summary, nor the other way round."""

		@testsuite("A title.")
		class Suite:
			"""A summary."""

		self.assertEqual("A title.", Suite.__testsuite_title__)
		self.assertEqual("A summary.", Suite.__testsuite_summary__)

	def test_TheTitleMustBeAStringOrAClass(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			testsuite(42)

		self.assertEqual("Parameter 'title' is neither a string nor a class.", str(exceptionCapture.exception))

	def test_ItRejectsAMethod(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			@testsuite("Suite")
			def method() -> None:
				pass

		self.assertIn("instead of a class", str(exceptionCapture.exception))

	def test_TheMarkerIsNotItselfATestcase(self) -> None:
		"""Its name starts with 'test', so a test runner has to be told otherwise."""

		self.assertFalse(testsuite.__test__)
		self.assertFalse(testcase.__test__)


class TestcaseMarker(Testcase):
	"""':deco:`testcase`' attaches the title a test runner should report for a method."""

	def test_WithoutParentheses(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				pass

		self.assertEqual("Method", Suite.Method.__testcase_title__)

	def test_WithEmptyParentheses(self) -> None:
		class Suite:
			@testcase()
			def Method(self) -> None:
				pass

		self.assertEqual("Method", Suite.Method.__testcase_title__)

	def test_WithATitle(self) -> None:
		class Suite:
			@testcase("A newer version compares greater.")
			def Method(self) -> None:
				pass

		self.assertEqual("A newer version compares greater.", Suite.Method.__testcase_title__)

	def test_TheSummaryIsTheDocStringsFirstParagraph(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				"""
				A newer version compares greater.

				Only the minor number differs here.
				"""

		self.assertEqual("Method", Suite.Method.__testcase_title__)
		self.assertEqual("A newer version compares greater.", Suite.Method.__testcase_summary__)

	def test_TheDescriptionIsTheWholeDocString(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				"""
				A newer version compares greater.

				Only the minor number differs here.
				"""

		self.assertEqual(
			"A newer version compares greater.\n\nOnly the minor number differs here.",
			Suite.Method.__testcase_description__
		)

	def test_WithoutADocStringSummaryAndDescriptionAreEmpty(self) -> None:
		class Suite:
			@testcase("A title.")
			def Method(self) -> None:
				pass

		self.assertEqual("A title.", Suite.Method.__testcase_title__)
		self.assertEqual("", Suite.Method.__testcase_summary__)
		self.assertEqual("", Suite.Method.__testcase_description__)

	def test_TheTitleIsIndependentOfTheDocString(self) -> None:
		"""Four names, not a fallback chain: a title never replaces a summary, nor the other way round."""

		class Suite:
			@testcase("A title.")
			def Method(self) -> None:
				"""A summary."""

		self.assertEqual("A title.", Suite.Method.__testcase_title__)
		self.assertEqual("A summary.", Suite.Method.__testcase_summary__)

	def test_TheTitleMustBeAStringOrAMethod(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			testcase(42)

		self.assertEqual("Parameter 'title' is neither a string nor a method.", str(exceptionCapture.exception))

	def test_ItRejectsAClass(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			@testcase("Case")
			class Suite:
				pass

		self.assertIn("instead of a method", str(exceptionCapture.exception))


TEST_MODULE = '''
from pyTooling.Testing import Testcase, testsuite, testcase


@testsuite("Version comparison")
class VersionComparison(Testcase):
	@testcase("A newer version compares greater.")
	def NewerIsGreater(self) -> None:
		self.assertGreater((2, 0), (1, 9))

	@testcase
	def UnnamedKeepsItsIdentifier(self) -> None:
		self.assertTrue(True)

	@testcase
	def DescribedByItsDocString(self) -> None:
		"""
		An equal version compares equal.

		The description reaches the report as a property.
		"""
		self.assertEqual((1, 0), (1, 0))

	def NotMarkedSoNotCollected(self) -> None:
		raise AssertionError("must never run")


@testsuite("A plain class")
class PlainSuite:
	@testcase("A class that is no TestCase works too.")
	def PlainWorks(self) -> None:
		assert True


class NameBased(Testcase):
	def test_StillCollectedByName(self) -> None:
		self.assertTrue(True)
'''   #: A test module using both styles, run by the integration tests below.

PYTEST_CONFIGURATION = """\
[pytest]
python_files = test_*
python_functions = test_*
"""   #: The pytest settings the generated module is run with.


class PyTestPlugin(ApplicationTestcase):
	"""The plugin collects what is marked, titles it in the report, and leaves name-based tests alone."""

	_consoleScript  = "pytest"
	_runnableModule = "pytest"

	def _RunPyTest(self, directory: Path, *arguments: str) -> tuple[object, Path]:
		"""
		Write the test module above into the given directory and run pytest over it.

		:param directory: Directory to write the test module and the report into.
		:param arguments: Optional, what pytest should collect. Default: the whole directory.
		:returns:         Tuple of the completed process and the path of the JUnit report.
		"""
		(directory / "test_marked.py").write_text(TEST_MODULE, encoding="utf-8")
		(directory / "pytest.ini").write_text(PYTEST_CONFIGURATION, encoding="utf-8")
		report = directory / "report.xml"

		# the subprocess runs elsewhere, so point it at the sources under test rather than an installed copy.
		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent
		environment = {"PYTHONPATH": str(repositoryRoot)}

		result = self.RunModule(
			"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest",
			f"--junit-xml={report}", *(arguments if len(arguments) > 0 else (str(directory), )),
			environment=environment,
			workingDirectory=directory
		)

		return result, report

	def test_TheMarkersAreNotCollectedAsTestcases(self) -> None:
		"""'testsuite' and 'testcase' start with 'test', which is what pytest's default 'python_functions' matches."""

		module = """\
from pyTooling.Testing import testsuite, testcase


@testsuite("A marked suite")
class Suite:
	@testcase("A marked case")
	def Case(self) -> None:
		assert True
"""
		configuration = """\
[pytest]
python_files = test_*
python_functions = test*
"""

		with TemporaryDirectory() as directory:
			directory = Path(directory)
			(directory / "test_importing.py").write_text(module, encoding="utf-8")
			(directory / "pytest.ini").write_text(configuration, encoding="utf-8")

			repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent
			result = self.RunModule(
				"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest", "--collect-only", "-q", str(directory),
				environment={"PYTHONPATH": str(repositoryRoot)},
				workingDirectory=directory
			)

		self.assertExitCode(result)
		self.assertNotIn("::testsuite", result.stdout, "The 'testsuite' decorator was collected as a testcase.")
		self.assertNotIn("::testcase", result.stdout, "The 'testcase' decorator was collected as a testcase.")
		self.assertIn("::Suite::Case", result.stdout, "The marked testcase was not collected.")

	def test_TheNodeIDStaysCanonicalSoATestcaseCanBeSelected(self) -> None:
		"""The report is titled, the item is not - so an IDE, a command line and '--last-failed' still work."""

		with TemporaryDirectory() as directory:
			result, _ = self._RunPyTest(Path(directory), "test_marked.py::VersionComparison::NewerIsGreater")

			self.assertExitCode(result)
			self.assertIn("1 passed", result.stdout)

	def test_MarkedAndNameBasedTestsRunInOneSession(self) -> None:
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)

			names = [
				(testcaseElement.get("classname").rsplit(".", 1)[-1], testcaseElement.get("name"))
				for testcaseElement in xml_parse(report).getroot().iter("testcase")
			]

		self.assertIn(("VersionComparison", "NewerIsGreater"), names)
		self.assertIn(("VersionComparison", "UnnamedKeepsItsIdentifier"), names)
		self.assertIn(("PlainSuite", "PlainWorks"), names)
		self.assertIn(("NameBased", "test_StillCollectedByName"), names)
		self.assertIn(("VersionComparison", "DescribedByItsDocString"), names)
		self.assertEqual(5, len(names), f"An unmarked method was collected: {names}")

	def test_TheTitlesAreReportedAsProperties(self) -> None:
		"""'classname' and 'name' stay identifiers; the titles are additional information."""

		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)

			properties = {
				testcaseElement.get("name"): {
					propertyElement.get("name"): propertyElement.get("value")
					for propertyElement in testcaseElement.iter("property")
				}
				for testcaseElement in xml_parse(report).getroot().iter("testcase")
			}

		self.assertEqual({"title": "A newer version compares greater."}, properties["NewerIsGreater"])
		self.assertEqual(
			{
				"title":       "DescribedByItsDocString",
				"summary":     "An equal version compares equal.",
				"description": "An equal version compares equal.\n\nThe description reaches the report as a property.",
			},
			properties["DescribedByItsDocString"]
		)
		self.assertEqual({}, properties["test_StillCollectedByName"], "An unmarked testcase carries no properties.")


UNITTEST_MODULE = '''
from unittest import skip

from pyTooling.Testing import Testcase, testsuite, testcase

LOG = []


@testsuite("A marked TestCase class")
class Suite(Testcase):
	@classmethod
	def setUpClass(cls) -> None:
		LOG.append("setUpClass")

	def setUp(self) -> None:
		self.value = 1

	def tearDown(self) -> None:
		LOG.append("tearDown")

	@testcase("Defined first.")
	def Zeta(self) -> None:
		self.assertEqual(1, self.value)

	@testcase("With subtests.")
	def Alpha(self) -> None:
		for index in range(3):
			with self.subTest(index=index):
				self.assertLess(index, 3)

	@testcase("Skipped.")
	@skip("on purpose")
	def Skipped(self) -> None:
		raise AssertionError("must never run")

	def test_ByName(self) -> None:
		self.assertTrue(True)

	def NotMarked(self) -> None:
		raise AssertionError("must never run")

	@testcase("Defined last.")
	def Omega(self) -> None:
		self.assertEqual(["setUpClass", "tearDown", "tearDown", "tearDown"], LOG)
'''   #: A marked 'unittest.TestCase' class, whose testcases aren't named 'test_*'.


class MarkedTestCaseClass(ApplicationTestcase):
	"""A marked :class:`unittest.TestCase` class: its testcases keep their names and run as :mod:`unittest` runs them."""

	_consoleScript  = "pytest"
	_runnableModule = "pytest"

	def _RunPyTest(self, directory: Path, *arguments: str) -> tuple[object, Path]:
		"""
		Write the test module above into the given directory and run pytest over it.

		:param directory: Directory to write the test module and the report into.
		:param arguments: Further arguments to pytest, e.g. what to collect. Default: the whole directory.
		:returns:         Tuple of the completed process and the path of the JUnit report.
		"""
		(directory / "test_unittest.py").write_text(UNITTEST_MODULE, encoding="utf-8")
		(directory / "pytest.ini").write_text(PYTEST_CONFIGURATION, encoding="utf-8")
		report = directory / "report.xml"

		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent

		result = self.RunModule(
			"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest", f"--junit-xml={report}",
			*(arguments if len(arguments) > 0 else (str(directory), )),
			environment={"PYTHONPATH": str(repositoryRoot)},
			workingDirectory=directory
		)

		return result, report

	def test_Names(self) -> None:
		"""A marked method is reported under its own name, in the order the class defines it, after the 'test*' ones."""
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			names = [testcaseElement.get("name") for testcaseElement in xml_parse(report).getroot().iter("testcase")]

		self.assertEqual(["test_ByName", "Zeta", "Alpha", "Skipped", "Omega"], names)

	def test_Selection(self) -> None:
		"""The node ID is the method's name, so it selects the testcase."""
		with TemporaryDirectory() as directory:
			result, _ = self._RunPyTest(Path(directory), "test_unittest.py::Suite::Alpha")

		self.assertExitCode(result)
		self.assertIn("1 passed", result.stdout)

	def test_Unittest(self) -> None:
		"""'setUpClass()', 'setUp()', 'tearDown()', 'subTest()' and 'skip()' work as for a method named 'test_*'."""
		with TemporaryDirectory() as directory:
			result, _ = self._RunPyTest(Path(directory))

		self.assertExitCode(result)
		self.assertIn("4 passed, 1 skipped", result.stdout)

	def test_Xdist(self) -> None:
		"""
		Distributed to 'pytest-xdist' workers, the marked testcases are collected and run alike.

		'Omega' checks what ran before it in the same process, which a worker can't promise, so it is deselected - by
		its own name.
		"""
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory), "-p", "xdist", "-n", "2", "-k", "not Omega", directory)

			self.assertExitCode(result)
			names = {testcaseElement.get("name") for testcaseElement in xml_parse(report).getroot().iter("testcase")}

		self.assertEqual({"test_ByName", "Zeta", "Alpha", "Skipped"}, names)


class ReportFormat(ApplicationTestcase):
	"""pyTooling's own report format: nested test suites, four names, and a schema the file points at."""

	_consoleScript  = "pytest"
	_runnableModule = "pytest"

	def _RunPyTest(self, directory: Path) -> tuple[object, Path]:
		"""
		Write the test module into the given directory and run pytest with the report writer enabled.

		:param directory: Directory to write the test module and the report into.
		:returns:         Tuple of the completed process and the path of the report.
		"""
		(directory / "test_marked.py").write_text(TEST_MODULE, encoding="utf-8")
		(directory / "pytest.ini").write_text(PYTEST_CONFIGURATION, encoding="utf-8")
		report = directory / "report.xml"

		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent

		result = self.RunModule(
			"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest", "-p", "pyTooling.Testing.ReportWriter",
			f"--pytooling-xml={report}", str(directory),
			environment={"PYTHONPATH": str(repositoryRoot)},
			workingDirectory=directory
		)

		return result, report

	def test_TheReportValidatesAgainstItsSchema(self) -> None:
		from xmlschema import XMLSchema

		from pyTooling                      import Resources
		from pyTooling.Common               import getResourceFile
		from pyTooling.Testing.ReportWriter import SCHEMA_FILES, SCHEMA_VERSION_LATEST

		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			XMLSchema(getResourceFile(Resources, SCHEMA_FILES[SCHEMA_VERSION_LATEST])).validate(report)

	def test_TestsuitesAreNested(self) -> None:
		"""What a dotted 'classname' cannot express: one element per level."""

		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			root = xml_parse(report).getroot()

			outer = root.find("Testsuite")
			self.assertEqual("test_marked", outer.get("name"))

			inner = {element.get("name") for element in outer.findall("Testsuite")}

		self.assertIn("VersionComparison", inner)
		self.assertIn("PlainSuite", inner)
		self.assertIn("NameBased", inner)

	def test_EveryNameIsItsOwnElement(self) -> None:
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			root = xml_parse(report).getroot()

			testcase = next(
				element for element in root.iter("Testcase")
				if element.get("name") == "DescribedByItsDocString"
			)
			names = {child.tag: child.text for child in testcase if child.tag in ("Title", "Summary", "Description")}
			status = testcase.get("status")
			nodeID = testcase.get("nodeID")

		self.assertEqual("DescribedByItsDocString", names["Title"])
		self.assertEqual("An equal version compares equal.", names["Summary"])
		self.assertIn("The description reaches the report as a property.", names["Description"])
		self.assertEqual("passed", status)
		self.assertIn("::DescribedByItsDocString", nodeID, "The node ID lets a reader re-run the testcase.")

	def test_ATestsuiteElementCarriesItsOwnNames(self) -> None:
		"""The names of a level come from the marker plugin's hierarchy, not from the testcases inside it."""

		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			suite = next(
				element for element in xml_parse(report).getroot().iter("Testsuite")
				if element.get("name") == "VersionComparison"
			)
			names = {child.tag: child.text for child in suite if child.tag in ("Title", "Summary", "Description")}

		self.assertEqual("Version comparison", names["Title"], "The marker's title reaches the Testsuite element.")
		self.assertNotIn("Summary", names, "That class has no doc-string, so the level has no summary.")

	def test_AnUnmarkedTestcaseCarriesNoNames(self) -> None:
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			root = xml_parse(report).getroot()

			testcase = next(
				element for element in root.iter("Testcase")
				if element.get("name") == "test_StillCollectedByName"
			)
			children = [child.tag for child in testcase]

		self.assertEqual([], children)


class Hierarchy(ApplicationTestcase):
	"""The names of every test suite level, keyed by the dotted path matching a testcase's 'classname'."""

	_consoleScript  = "pytest"
	_runnableModule = "pytest"

	PACKAGE_DOCSTRING = '''"""
The version handling test suite.

Everything about parsing and comparing versions.
"""
'''   #: The '__init__.py' of the generated package, whose doc-string names the outermost level.

	MODULE = '''"""
Version comparison tests.

The module\'s own description.
"""
from pyTooling.Testing import Testcase, testsuite, testcase


@testsuite("Version comparison.")
class VersionComparison(Testcase):
	"""
	Compare two release versions.

	Everything about comparing them.
	"""

	@testcase("A newer version compares greater.")
	def NewerIsGreater(self) -> None:
		self.assertGreater((2, 0), (1, 9))
'''   #: A test module inside that package, whose class carries a marker.

	def _RunPyTest(self, directory: Path) -> tuple[object, Path]:
		"""
		Write a package with a documented '__init__.py' and one test module, and run pytest over it.

		:param directory: Directory to write the package and the report into.
		:returns:         Tuple of the completed process and the path of the JUnit report.
		"""
		package = directory / "versioning"
		package.mkdir()
		(package / "__init__.py").write_text(self.PACKAGE_DOCSTRING, encoding="utf-8")
		(package / "test_comparison.py").write_text(self.MODULE, encoding="utf-8")
		(directory / "pytest.ini").write_text(PYTEST_CONFIGURATION, encoding="utf-8")
		report = directory / "report.xml"

		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent

		result = self.RunModule(
			"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest",
			f"--junit-xml={report}", "versioning",
			environment={"PYTHONPATH": str(repositoryRoot)},
			workingDirectory=directory
		)

		return result, report

	def test_EveryLevelIsKeyedByItsDottedPath(self) -> None:
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			testsuiteElement = xml_parse(report).getroot().find("testsuite")
			properties = {
				propertyElement.get("name"): propertyElement.get("value")
				for propertyElement in testsuiteElement.find("properties")
			}
			classname = testsuiteElement.find("testcase").get("classname")

		self.assertEqual("The version handling test suite.", properties["versioning.summary"])
		self.assertEqual("Version comparison tests.", properties["versioning.test_comparison.summary"])
		self.assertEqual(
			"Version comparison.",
			properties["versioning.test_comparison.VersionComparison.title"]
		)
		self.assertEqual(
			"versioning.test_comparison.VersionComparison",
			classname,
			"The innermost key is the testcase's 'classname', which is what joins the two."
		)

	def test_ThePackageDescriptionIsItsWholeDocString(self) -> None:
		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			properties = {
				propertyElement.get("name"): propertyElement.get("value")
				for propertyElement in xml_parse(report).getroot().find("testsuite").find("properties")
			}

		self.assertEqual(
			"The version handling test suite.\n\nEverything about parsing and comparing versions.",
			properties["versioning.description"]
		)

	def test_TheyAreWrittenOncePerSessionNotPerTestcase(self) -> None:
		"""The reason the keys are on the test suite: a testcase property would repeat for every testcase."""

		with TemporaryDirectory() as directory:
			result, report = self._RunPyTest(Path(directory))

			self.assertExitCode(result)
			testcaseElement = xml_parse(report).getroot().find("testsuite").find("testcase")
			names = [propertyElement.get("name") for propertyElement in testcaseElement.iter("property")]

		self.assertEqual(["title"], names)
