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
#
"""Unit tests for :mod:`pyTooling.Testing`."""
from shutil     import which
from subprocess import TimeoutExpired

from pyTooling.Platform import CurrentPlatform
from pyTooling.Testing  import ApplicationTestcase, Testcase, TestingException, stripANSIColorCodes


#: Names the Python interpreter may be installed under. Which of them exists is not decided by the platform alone:
#: Debian and Ubuntu ship 'python3' and only add 'python' with the 'python-is-python3' package, Arch ships
#: 'python', a virtual environment provides whichever names it was created with, and Windows adds the 'py'
#: launcher. So the platform picks the order and the first name actually installed wins.
_INTERPRETER_NAMES = ("py", "python", "python3") if CurrentPlatform.IsNativeWindows else ("python3", "python", "py")
PYTHON_CONSOLE_SCRIPT = next((name for name in _INTERPRETER_NAMES if which(name) is not None), _INTERPRETER_NAMES[0])


class StripANSIColorCodes(Testcase):
	def test_PlainTextIsUnchanged(self) -> None:
		self.assertEqual("plain", stripANSIColorCodes("plain"))

	def test_ColorCodesAreRemoved(self) -> None:
		self.assertEqual("red", stripANSIColorCodes("\x1B[31mred\x1B[0m"))

	def test_OnlyTheCodesAreRemoved(self) -> None:
		self.assertEqual("a[31mb", stripANSIColorCodes("a[31m\x1B[1;32mb"))


class RunningAModule(ApplicationTestcase):
	"""The mixin runs a module and reports what it did. 'json.tool' is used because it ships with Python."""

	_consoleScript =  PYTHON_CONSOLE_SCRIPT
	_runnableModule = "json.tool"

	def test_ExitCodeAndOutputAreCaptured(self) -> None:
		result = self.RunModule(stdInput='{"key": [1, 2]}')

		self.assertExitCode(result)
		self.assertIn('"key"', result.stdout)

	def test_AFailingRunKeepsItsExitCodeAndMessage(self) -> None:
		result = self.RunModule(stdInput="not json")

		self.assertNotEqual(0, result.returncode)
		self.assertNotEqual("", result.stderr)

	def test_TheAssertionReportsTheOutput(self) -> None:
		result = self.RunModule(stdInput="not json")

		with self.assertRaises(AssertionError) as context:
			self.assertExitCode(result, 0)

		self.assertIn("--- stderr ---", str(context.exception))
		self.assertIn("Expected exit code 0", str(context.exception))

	def test_TimeoutIsEnforced(self) -> None:
		with self.assertRaises(TimeoutExpired):
			self.RunModule(stdInput="", timeout=0.001)


class RunningAConsoleScript(ApplicationTestcase):
	"""'python' itself is on PATH in every environment this runs in, so it stands in for an installed program."""

	_consoleScript =  PYTHON_CONSOLE_SCRIPT
	_runnableModule = "json.tool"

	def test_TheExecutableIsResolved(self) -> None:
		self.assertIsNotNone(self._executable)

	def test_ItRuns(self) -> None:
		result = self.RunEntrypoint("-c", "print('hello')")

		self.assertExitCode(result)
		self.assertEqual("hello\n", result.stdout)


class ATestcaseThatIsNotSetUp(Testcase):
	"""setUpClass refuses a test class that cannot run anything, rather than letting every testcase fail."""

	def test_AMissingConsoleScriptIsReported(self) -> None:
		class Missing(ApplicationTestcase):
			_runnableModule = "json.tool"

		with self.assertRaises(TestingException) as context:
			Missing.setUpClass()

		self.assertIn("_consoleScript", str(context.exception))

	def test_AMissingRunnableModuleIsReported(self) -> None:
		class Missing(ApplicationTestcase):
			_consoleScript = PYTHON_CONSOLE_SCRIPT

		with self.assertRaises(TestingException) as context:
			Missing.setUpClass()

		self.assertIn("_runnableModule", str(context.exception))

	def test_AnUninstalledConsoleScriptIsReported(self) -> None:
		class Missing(ApplicationTestcase):
			_consoleScript =  "no-such-program-here"
			_runnableModule = "json.tool"

		with self.assertRaises(TestingException) as context:
			Missing.setUpClass()

		self.assertIn("no-such-program-here", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, FileNotFoundError)


class Assertions(Testcase):
	"""The attribute assertions, whether they come from unittest or from the mixin."""

	def test_AnExistingAttributeIsFound(self) -> None:
		self.assertHasAttr(self, "assertHasAttr")

	def test_AMissingAttributeFails(self) -> None:
		with self.assertRaises(AssertionError):
			self.assertHasAttr(object(), "noSuchAttribute")

	def test_AMissingAttributeIsAccepted(self) -> None:
		self.assertNotHasAttr(object(), "noSuchAttribute")

	def test_AnExistingAttributeFailsTheNegation(self) -> None:
		with self.assertRaises(AssertionError):
			self.assertNotHasAttr(object(), "__class__")
