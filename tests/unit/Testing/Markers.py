# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
# |_|    |___/                          |___/                                                                          #
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
:deco:`~pyTooling.Testing.testcase`, and for :mod:`pyTooling.Testing.PyTest`, the plugin collecting what they mark.
"""
from os                    import environ
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

	def test_TheTitleComesFromTheDocStringSummary(self) -> None:
		@testsuite
		class Suite:
			"""Version comparison."""

		self.assertEqual("Version comparison.", Suite.__testsuite_title__)
		self.assertEqual("", Suite.__testsuite_description__)

	def test_TheDescriptionComesFromTheDocStringBody(self) -> None:
		@testsuite
		class Suite:
			"""
			Version comparison.

			Everything about comparing two versions.
			"""

		self.assertEqual("Version comparison.", Suite.__testsuite_title__)
		self.assertEqual("Everything about comparing two versions.", Suite.__testsuite_description__)

	def test_AnExplicitTitleWinsOverTheDocString(self) -> None:
		@testsuite("An explicit title wins.")
		class Suite:
			"""This summary must not win."""

		self.assertEqual("An explicit title wins.", Suite.__testsuite_title__)

	def test_TheDescriptionMustBeAString(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			testsuite(description=42)

		self.assertEqual("Parameter 'description' is not a string.", str(exceptionCapture.exception))

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

	def test_TheTitleComesFromTheDocStringSummary(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				"""A newer version compares greater."""

		self.assertEqual("A newer version compares greater.", Suite.Method.__testcase_title__)
		self.assertEqual("", Suite.Method.__testcase_description__)

	def test_TheDescriptionComesFromTheDocStringBody(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				"""
				A newer version compares greater.

				Only the minor number differs, so this also pins
				that it is no string comparison.
				"""

		self.assertEqual("A newer version compares greater.", Suite.Method.__testcase_title__)
		self.assertEqual(
			"Only the minor number differs, so this also pins\nthat it is no string comparison.",
			Suite.Method.__testcase_description__
		)

	def test_AMultiLineSummaryBecomesOneLine(self) -> None:
		class Suite:
			@testcase
			def Method(self) -> None:
				"""
				A newer version
				compares greater.
				"""

		self.assertEqual("A newer version compares greater.", Suite.Method.__testcase_title__)

	def test_AnExplicitTitleWinsOverTheDocString(self) -> None:
		class Suite:
			@testcase("An explicit title wins.")
			def Method(self) -> None:
				"""This summary must not win."""

		self.assertEqual("An explicit title wins.", Suite.Method.__testcase_title__)

	def test_AnExplicitDescriptionWinsOverTheDocString(self) -> None:
		class Suite:
			@testcase(description="An explicit description wins.")
			def Method(self) -> None:
				"""
				A summary.

				A body that must not win.
				"""

		self.assertEqual("A summary.", Suite.Method.__testcase_title__)
		self.assertEqual("An explicit description wins.", Suite.Method.__testcase_description__)

	def test_TheDescriptionMustBeAString(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			testcase(description=42)

		self.assertEqual("Parameter 'description' is not a string.", str(exceptionCapture.exception))

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
	def TitledByItsDocString(self) -> None:
		"""An equal version compares equal.

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
		# 'environment' replaces the environment rather than extending it, so it is merged into this process's -
		# without 'SystemRoot' Winsock fails to initialise on Windows, and pytest aborts with an INTERNALERROR.
		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent
		environment = {**environ, "PYTHONPATH": str(repositoryRoot)}

		result = self.RunModule(
			"-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest",
			f"--junit-xml={report}", *(arguments if len(arguments) > 0 else (str(directory), )),
			environment=environment,
			workingDirectory=directory
		)

		return result, report

	def test_TheNodeIDStaysCanonicalSoATestcaseCanBeSelected(self) -> None:
		"""The report is titled, the item is not - so an IDE, a command line and '--last-failed' still work."""

		with TemporaryDirectory() as directory:
			result, _ = self._RunPyTest(Path(directory), "test_marked.py::VersionComparison::test_NewerIsGreater")

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

		self.assertIn(("VersionComparison", "test_NewerIsGreater"), names)
		self.assertIn(("VersionComparison", "test_UnnamedKeepsItsIdentifier"), names)
		self.assertIn(("PlainSuite", "PlainWorks"), names)
		self.assertIn(("NameBased", "test_StillCollectedByName"), names)
		self.assertIn(("VersionComparison", "test_TitledByItsDocString"), names)
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

		self.assertEqual(
			{"title": "A newer version compares greater.", "testsuiteTitle": "Version comparison"},
			properties["test_NewerIsGreater"]
		)
		self.assertEqual(
			{
				"title":         "An equal version compares equal.",
				"description":   "The description reaches the report as a property.",
				"testsuiteTitle": "Version comparison"
			},
			properties["test_TitledByItsDocString"]
		)
		self.assertEqual({}, properties["test_StillCollectedByName"], "An unmarked testcase carries no properties.")
