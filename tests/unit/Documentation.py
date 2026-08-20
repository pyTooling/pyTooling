# ==================================================================================================================== #
#             _____           _ _             _____                   _             _ _   _ ___                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__ _ __ _ __ ___ (_)_ __   __ _| | | | |_ _|                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | | | | || |                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/ |  | | | | | | | | | | (_| | | |_| || |                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|\___/|___|                       #
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
#
"""Unit tests keeping the tutorial's example programs correct."""
from pathlib              import Path
from sys                  import path as sys_path
from importlib            import import_module
from unittest             import TestLoader, TestResult

from pyTooling.TerminalUI import Severity, TerminalApplication
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


EXAMPLE_DIRECTORY = Path(__file__).parent.parent / "example" / "TerminalApplication"

if str(EXAMPLE_DIRECTORY) not in sys_path:
	sys_path.insert(0, str(EXAMPLE_DIRECTORY))


class ExampleImports(Testcase):
	"""Every example in the tutorial is a module that must import."""

	def test_EveryStepImports(self) -> None:
		for step in range(1, 7):
			with self.subTest(step=step):
				module = import_module(f"Step{step}")

				self.assertTrue(issubclass(module.Application, TerminalApplication))

	def test_NoExampleWasRemovedFromDisk(self) -> None:
		for step in range(1, 7):
			with self.subTest(step=step):
				self.assertTrue((EXAMPLE_DIRECTORY / f"Step{step}.py").exists())


class Step1(Testcase):
	"""The first example writes a normal message and a warning, but no verbose message."""

	def test_TheVerboseMessageIsSuppressedAndTheWarningIsCounted(self) -> None:
		module = import_module("Step1")

		class TestApplication(module.Application):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		program.Run()

		self.assertEqual(1, program.WarningCount)
		self.assertIn(Severity.Warning, [line.Severity for line in program.Lines])
		self.assertNotIn(Severity.Verbose, [line.Severity for line in program.Lines])


class Step6(Testcase):
	"""The 'help' command takes a command name, so 'args.Command' must exist."""

	def test_TheHelpCommandAcceptsACommandName(self) -> None:
		module = import_module("Step6")

		class TestApplication(module.Application):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		parsed = program.MainParser.parse_args(["help", "version"])

		self.assertEqual("version", parsed.Command)

	def test_TheHelpCommandsArgumentIsOptional(self) -> None:
		module = import_module("Step6")

		class TestApplication(module.Application):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		parsed = program.MainParser.parse_args(["help"])

		self.assertIsNone(parsed.Command)


class TutorialTestcase(Testcase):
	"""The testcase shown in the tutorial's testing section is executed, not just displayed."""

	def test_TheDocumentedTestcasePasses(self) -> None:
		module = import_module("Testing")

		suite = TestLoader().loadTestsFromTestCase(module.ApplicationTests)
		result = TestResult()
		suite.run(result)

		self.assertEqual(1, result.testsRun)
		self.assertEqual([], result.failures)
		self.assertEqual([], result.errors)
