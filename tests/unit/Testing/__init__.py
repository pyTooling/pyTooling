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
"""
Unit tests for :mod:`pyTooling.Testing`: the assertions of :class:`~pyTooling.Testing.Testcase`, the ANSI
helper, and running an application as a module or as a console script.
"""
from shutil     import which
from subprocess import TimeoutExpired

from pyTooling.Platform import CurrentPlatform
from pyTooling.Testing  import ApplicationTestcase, Testcase, TestingError, stripANSIColorCodes


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

	_CONSOLE_SCRIPT =  PYTHON_CONSOLE_SCRIPT
	_RUNNABLE_MODULE = "json.tool"

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

	_CONSOLE_SCRIPT =  PYTHON_CONSOLE_SCRIPT
	_RUNNABLE_MODULE = "json.tool"

	def test_TheExecutableIsResolved(self) -> None:
		self.assertIsNotNone(self._executable)

	def test_ItRuns(self) -> None:
		result = self.RunEntrypoint("-c", "print('hello')")

		self.assertExitCode(result)
		self.assertEqual("hello\n", result.stdout)


class TheEnvironment(ApplicationTestcase):
	"""The variables given as 'environment' are merged into this process's environment, not replacing it."""

	_CONSOLE_SCRIPT =  PYTHON_CONSOLE_SCRIPT

	def test_AVariableIsAdded(self) -> None:
		result = self.RunEntrypoint(
			"-c", "import os; print(os.environ['PYTOOLING_TEST'])", environment={"PYTOOLING_TEST": "42"}
		)

		self.assertExitCode(result)
		self.assertEqual("42\n", result.stdout)

	def test_TheRestIsInherited(self) -> None:
		result = self.RunEntrypoint(
			"-c", "import os; print('PATH' in os.environ)", environment={"PYTOOLING_TEST": "42"}
		)

		self.assertEqual("True\n", result.stdout)

	def test_NoneRemovesAVariable(self) -> None:
		result = self.RunEntrypoint("-c", "import os; print('PATH' in os.environ)", environment={"PATH": None})

		self.assertEqual("False\n", result.stdout)


class ATestcaseThatIsNotSetUp(Testcase):
	"""setUpClass refuses a test class that cannot run anything, rather than letting every testcase fail."""

	def test_AMissingConsoleScriptIsReported(self) -> None:
		class Missing(ApplicationTestcase):
			_RUNNABLE_MODULE = "json.tool"

		with self.assertRaises(TestingError) as context:
			Missing.setUpClass()

		self.assertIn("_CONSOLE_SCRIPT", str(context.exception))

	def test_ARunnableModuleIsOptional(self) -> None:
		"""A program without a '__main__' module is tested through its entry point alone."""
		class EntrypointOnly(ApplicationTestcase):
			_CONSOLE_SCRIPT = PYTHON_CONSOLE_SCRIPT

			def test_Nothing(self) -> None:
				pass

		EntrypointOnly.setUpClass()

		self.assertIsNotNone(EntrypointOnly._executable)

	def test_RunningAMissingRunnableModuleIsReported(self) -> None:
		class EntrypointOnly(ApplicationTestcase):
			_CONSOLE_SCRIPT = PYTHON_CONSOLE_SCRIPT

			def test_Nothing(self) -> None:
				pass

		EntrypointOnly.setUpClass()
		with self.assertRaises(TestingError) as context:
			EntrypointOnly("test_Nothing").RunModule()

		self.assertEqual("Testcase 'EntrypointOnly' has no runnable module.", str(context.exception))
		self.assertIn("Set '_RUNNABLE_MODULE' to run the program with 'python -m'.", context.exception.__notes__)

	def test_AnUninstalledConsoleScriptIsReported(self) -> None:
		class Missing(ApplicationTestcase):
			_CONSOLE_SCRIPT =  "no-such-program-here"
			_RUNNABLE_MODULE = "json.tool"

		with self.assertRaises(TestingError) as context:
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


class BackportedAssertions(Testcase):
	"""The assertions Python 3.14 added, with the same messages from unittest (3.14+) or from :class:`Testcase`."""

	def test_HasAttr_Module(self) -> None:
		import json

		with self.assertRaises(AssertionError) as context:
			self.assertHasAttr(json, "noSuchAttribute")

		self.assertEqual("module 'json' has no attribute 'noSuchAttribute'", str(context.exception))

	def test_HasAttr_Type(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertHasAttr(int, "noSuchAttribute")

		self.assertEqual("type object 'int' has no attribute 'noSuchAttribute'", str(context.exception))

	def test_IsSubclass(self) -> None:
		self.assertIsSubclass(bool, int)
		self.assertIsSubclass(bool, (str, int))

	def test_IsSubclass_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertIsSubclass(int, str)

		self.assertEqual("<class 'int'> is not a subclass of <class 'str'>", str(context.exception))

	def test_IsSubclass_FailsTuple(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertIsSubclass(int, (str, bytes))

		self.assertEqual(
			"<class 'int'> is not a subclass of any of (<class 'str'>, <class 'bytes'>)",
			str(context.exception)
		)

	def test_IsSubclass_NoClass(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertIsSubclass(1, int)

		self.assertEqual("1 is not a class", str(context.exception))

	def test_NotIsSubclass(self) -> None:
		self.assertNotIsSubclass(int, (str, bytes))

	def test_NotIsSubclass_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertNotIsSubclass(bool, (str, int))

		self.assertEqual("<class 'bool'> is a subclass of <class 'int'>", str(context.exception))

	def test_StartsWith(self) -> None:
		self.assertStartsWith("pyTooling", "py")
		self.assertStartsWith(b"pyTooling", (b"x", b"py"))

	def test_StartsWith_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertStartsWith("pyTooling", "Tool")

		self.assertEqual("'pyTooling' doesn't start with 'Tool'", str(context.exception))

	def test_StartsWith_FailsTuple(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertStartsWith("pyTooling", ("a", "b"))

		self.assertEqual("'pyTooling' doesn't start with any of ('a', 'b')", str(context.exception))

	def test_StartsWith_WrongType(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertStartsWith(b"pyTooling", "py")

		self.assertEqual("Expected str, not bytes", str(context.exception))

	def test_NotStartsWith(self) -> None:
		self.assertNotStartsWith("pyTooling", ("a", "b"))

	def test_NotStartsWith_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertNotStartsWith("pyTooling", ("a", "py"))

		self.assertEqual("'pyTooling' starts with 'py'", str(context.exception))

	def test_EndsWith(self) -> None:
		self.assertEndsWith("pyTooling", "ing")

	def test_EndsWith_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertEndsWith("pyTooling", "py")

		self.assertEqual("'pyTooling' doesn't end with 'py'", str(context.exception))

	def test_EndsWith_WrongType(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertEndsWith("pyTooling", b"ing")

		self.assertEqual("Expected bytes, not str", str(context.exception))

	def test_NotEndsWith(self) -> None:
		self.assertNotEndsWith("pyTooling", "py")

	def test_NotEndsWith_Fails(self) -> None:
		with self.assertRaises(AssertionError) as context:
			self.assertNotEndsWith("pyTooling", ("x", "ing"))

		self.assertEqual("'pyTooling' ends with 'ing'", str(context.exception))

	def test_Message(self) -> None:
		"""A message is added to the generated one, as ``longMessage`` is on by default."""
		with self.assertRaises(AssertionError) as context:
			self.assertEndsWith("pyTooling", "py", "the package name")

		self.assertEqual("'pyTooling' doesn't end with 'py' : the package name", str(context.exception))

