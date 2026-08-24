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
Unit tests for :deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase`, and for the pytest
plugin collecting what they mark.
"""
from os         import environ, pathsep
from pathlib    import Path
from subprocess import run as subprocess_run
from sys        import executable as PythonExecutable
from tempfile   import TemporaryDirectory
from xml.etree.ElementTree import parse as xml_parse

from pyTooling.Testing import Testcase, testsuite, testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Markers(Testcase):
	"""The decorators attach the name a test runner should report."""

	def test_TheClassKeepsItsIdentifierByDefault(self) -> None:
		@testsuite()
		class Suite:
			pass

		self.assertEqual("Suite", Suite.__testsuite__)

	def test_TheMethodKeepsItsIdentifierByDefault(self) -> None:
		class Suite:
			@testcase()
			def Method(self) -> None:
				pass

		self.assertEqual("Method", Suite.Method.__testcase__)

	def test_ADeclaredNameMayBeASentence(self) -> None:
		@testsuite("Version comparison")
		class Suite:
			@testcase("a newer version compares greater")
			def Method(self) -> None:
				pass

		self.assertEqual("Version comparison", Suite.__testsuite__)
		self.assertEqual("a newer version compares greater", Suite.Method.__testcase__)

	def test_TheNameMustBeAString(self) -> None:
		for decorator in (testsuite, testcase):
			with self.subTest(decorator=decorator.__name__):
				with self.assertRaises(TypeError) as exceptionCapture:
					decorator(42)

				self.assertEqual("Parameter 'name' is not a string.", str(exceptionCapture.exception))

	def test_TestsuiteRejectsAMethod(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			@testsuite("Suite")
			def method() -> None:
				pass

		self.assertIn("instead of a class", str(exceptionCapture.exception))

	def test_TestcaseRejectsAClass(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			@testcase("Case")
			class Suite:
				pass

		self.assertIn("instead of a method", str(exceptionCapture.exception))


TEST_MODULE = '''
from pyTooling.Testing import Testcase, testsuite, testcase


@testsuite("Version comparison")
class VersionComparison(Testcase):
	@testcase("a newer version compares greater")
	def NewerIsGreater(self) -> None:
		self.assertGreater((2, 0), (1, 9))

	@testcase()
	def UnnamedKeepsItsIdentifier(self) -> None:
		self.assertTrue(True)

	def NotMarkedSoNotCollected(self) -> None:
		raise AssertionError("must never run")


@testsuite("A plain class")
class PlainSuite:
	@testcase("a class that is no TestCase works too")
	def PlainWorks(self) -> None:
		assert True


class NameBased(Testcase):
	def test_StillCollectedByName(self) -> None:
		self.assertTrue(True)
'''   #: A test module using both styles, run by the integration test below.


class PyTestPlugin(Testcase):
	"""The plugin collects what is marked, reports it under the declared name, and leaves name-based tests alone."""

	@staticmethod
	def _RunPyTest(directory: Path) -> tuple[int, str, Path]:
		"""
		Write the test module above into the given directory and run pytest over it.

		:param directory: Directory to write the test module and the report into.
		:returns:         Tuple of the exit code, the captured output, and the path of the JUnit report.
		"""
		(directory / "test_marked.py").write_text(TEST_MODULE, encoding="utf-8")
		(directory / "pytest.ini").write_text("[pytest]\npython_files = test_*\npython_functions = test_*\n", encoding="utf-8")
		report = directory / "report.xml"

		# the subprocess runs elsewhere, so point it at the sources under test rather than an installed copy
		repositoryRoot = Path(__file__).resolve().parent.parent.parent.parent
		pythonPath = f"{repositoryRoot}{pathsep}{environ['PYTHONPATH']}" if "PYTHONPATH" in environ else str(repositoryRoot)

		process = subprocess_run(
			(
				PythonExecutable, "-m", "pytest", "-p", "no:cacheprovider", "-p", "pyTooling.Testing.PyTest",
				f"--junit-xml={report}", str(directory)
			),
			capture_output=True, encoding="utf-8", cwd=directory, env={**environ, "PYTHONPATH": pythonPath}
		)

		return process.returncode, process.stdout, report

	def test_MarkedAndNameBasedTestsRunInOneSession(self) -> None:
		with TemporaryDirectory() as directory:
			returnCode, output, report = self._RunPyTest(Path(directory))

			self.assertEqual(0, returnCode, output)

			names = [
				(testcaseElement.get("classname").rsplit(".", 1)[-1], testcaseElement.get("name"))
				for testcaseElement in xml_parse(report).getroot().iter("testcase")
			]

		self.assertIn(("Version comparison", "a newer version compares greater"), names)
		self.assertIn(("Version comparison", "UnnamedKeepsItsIdentifier"), names)
		self.assertIn(("A plain class", "a class that is no TestCase works too"), names)
		self.assertIn(("NameBased", "test_StillCollectedByName"), names)
		self.assertEqual(4, len(names), f"An unmarked method was collected: {names}")
