# ==================================================================================================================== #
#              _____           _ _               ____  _                           _       _                           #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ ___  _ ____      ____ _| |_ ___| |__                        #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __/ _ \| '_ \ \ /\ / / _` | __/ __| '_ \                       #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | || (_) | |_) \ V  V / (_| | || (__| | | |                      #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__\___/| .__/ \_/\_/ \__,_|\__\___|_| |_|                      #
#  |_|    |___/                          |___/                 |_|                                                     #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for the application testing helpers."""
from subprocess import TimeoutExpired
from unittest   import TestCase

from pyTooling.Testing import ApplicationTestcaseMixin, stripANSIColorCodes


class StripANSIColorCodes(TestCase):
	def test_PlainTextIsUnchanged(self) -> None:
		self.assertEqual("plain", stripANSIColorCodes("plain"))

	def test_ColorCodesAreRemoved(self) -> None:
		self.assertEqual("red", stripANSIColorCodes("\x1B[31mred\x1B[0m"))

	def test_OnlyTheCodesAreRemoved(self) -> None:
		self.assertEqual("a[31mb", stripANSIColorCodes("a[31m\x1B[1;32mb"))


class RunningAModule(ApplicationTestcaseMixin, TestCase):
	"""The mixin runs a module and reports what it did. 'json.tool' is used because it ships with Python."""

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

	def test_WithoutAConsoleScriptTheEntrypointSaysSo(self) -> None:
		with self.assertRaises(NotImplementedError) as context:
			self.RunEntrypoint("--version")

		self.assertIn("_consoleScript", str(context.exception))


class RunningAConsoleScript(ApplicationTestcaseMixin, TestCase):
	"""'python' itself is on PATH in every environment this runs in, so it stands in for an installed program."""

	_consoleScript = "python3"

	def test_TheExecutableIsResolved(self) -> None:
		self.assertIsNotNone(self._executable)

	def test_ItRuns(self) -> None:
		result = self.RunEntrypoint("-c", "print('hello')")

		self.assertExitCode(result)
		self.assertEqual("hello\n", result.stdout)

	def test_WithoutARunnableModuleTheModuleRunnerSaysSo(self) -> None:
		with self.assertRaises(NotImplementedError) as context:
			self.RunModule("--version")

		self.assertIn("_runnableModule", str(context.exception))


class AMissingConsoleScript(TestCase):
	def test_SetUpClassExplainsWhatIsMissing(self) -> None:
		class Missing(ApplicationTestcaseMixin, TestCase):
			_consoleScript = "no-such-program-here"

		with self.assertRaises(FileNotFoundError) as context:
			Missing.setUpClass()

		self.assertIn("no-such-program-here", str(context.exception))
