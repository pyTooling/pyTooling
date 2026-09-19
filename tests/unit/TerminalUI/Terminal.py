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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
Unit tests for :class:`pyTooling.TerminalUI.TerminalApplication`.

Covered are the verbosity properties, the counters and the exit-on-counter methods, and which messages
reach ``STDOUT`` and ``STDERR`` in each mode.
"""
from io                   import StringIO

from pyTooling.TerminalUI import TerminalApplication, Severity, Mode
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_LineTerminal(self) -> None:
		term = TerminalApplication()

		self.assertGreaterEqual(term.Width, 80)
		self.assertGreaterEqual(term.Height, 25)
		self.assertFalse(term.Verbose)
		self.assertFalse(term.Debug)
		self.assertFalse(term.Quiet)
		self.assertEqual(Severity.Normal, term.LogLevel)
		self.assertEqual(0, term.BaseIndent)
		self.assertEqual(0, len(term.Lines))
		self.assertEqual(0, term.ErrorCount)
		self.assertEqual(0, term.CriticalWarningCount)
		self.assertEqual(0, term.WarningCount)

	def test_DerivedApplication(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

				self._writeLevel = Severity.Error

		app = Application()
		self.assertEqual(Severity.Error, app.LogLevel)

	def test_ApplicationConfiguration(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app.Configure(verbose=True, debug=True, quiet=True)

		self.assertTrue(app.Verbose)
		self.assertTrue(app.Debug)
		self.assertTrue(app.Quiet)


class Properties(Testcase):
	def test_BaseIndent(self) -> None:
		term = TerminalApplication()
		self.assertEqual(0, term.BaseIndent)

		term.BaseIndent = 2
		self.assertEqual(2, term.BaseIndent)

	def test_LogLevel(self) -> None:
		term = TerminalApplication()
		self.assertEqual(Severity.Normal, term.LogLevel)

		term.LogLevel = Severity.Warning
		self.assertEqual(Severity.Warning, term.LogLevel)


class ExitOnCounters(Testcase):
	def test_Warnings(self) -> None:
		print()

		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()

		app.ExitOnPreviousWarnings()

		app.WriteWarning("Message")

		with self.assertRaises(SystemExit):
			app.ExitOnPreviousWarnings()

	def test_Critical(self) -> None:
		print()

		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()

		app.ExitOnPreviousCriticalWarnings()

		app.WriteCritical("Message")

		with self.assertRaises(SystemExit):
			app.ExitOnPreviousCriticalWarnings()

	def test_Errors(self) -> None:
		print()

		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()

		app.ExitOnPreviousErrors()

		app.WriteError("Message")

		with self.assertRaises(SystemExit):
			app.ExitOnPreviousErrors()


class ToStdOut(Testcase):
	WHITE =       "\x1b[97m"
	YELLOW =      "\x1b[93m"
	DARK_YELLOW = "\x1b[33m"
	RED =         "\x1b[91m"
	PURPLE =      "\x1b[31m"
	NO_COLOR =    "\x1b[39m"

	def test_WriteFatal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		try:
			app.WriteFatal("This is a fatal message.")
		except SystemExit:
			pass

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteFatalNoExit(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteFatal("This is a fatal message.", immediateExit=False)

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteError(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteError("This is a error message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.RED}[ERROR]     This is a error message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteQuiet(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteQuiet("This is a quiet message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a quiet message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteWarning("This is a warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.YELLOW}[WARNING]   This is a warning message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteCriticalWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteCritical("This is a critical warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.DARK_YELLOW}[CRITICAL]  This is a critical warning message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteInfo(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteInfo("This is a info message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a info message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteNormal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteNormal("This is a normal message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a normal message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteDryRun(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDryRun("This is a dryRun message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteVerboseDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteVerbose("This is a verbose message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteDebugDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDebug("This is a debug message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())


class ToStdOut_ToStdErr(Testcase):
	WHITE =       "\x1b[97m"
	YELLOW =      "\x1b[93m"
	DARK_YELLOW = "\x1b[33m"
	RED =         "\x1b[91m"
	PURPLE =      "\x1b[31m"
	NO_COLOR =    "\x1b[39m"

	def test_WriteFatal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		try:
			app.WriteFatal("This is a fatal message.")
		except SystemExit:
			pass

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", err.readline())

	def test_WriteFatalNoExit(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteFatal("This is a fatal message.", immediateExit=False)

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", err.readline())

	def test_WriteError(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteError("This is a error message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.RED}[ERROR]     This is a error message.{self.NO_COLOR}\n", err.readline())

	def test_WriteQuiet(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteQuiet("This is a quiet message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a quiet message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteCriticalWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteCritical("This is a critical warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.DARK_YELLOW}[CRITICAL]  This is a critical warning message.{self.NO_COLOR}\n", err.readline())

	def test_WriteWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteWarning("This is a warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.YELLOW}[WARNING]   This is a warning message.{self.NO_COLOR}\n", err.readline())

	def test_WriteInfo(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteInfo("This is a info message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a info message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteNormal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteNormal("This is a normal message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(f"{self.WHITE}This is a normal message.{self.NO_COLOR}\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteDryRun(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDryRun("This is a dryRun message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteVerboseDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteVerbose("This is a verbose message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteDebugDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.TextToStdOut_ErrorsToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDebug("This is a debug message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())


class DataToStdOut(Testcase):
	WHITE =       "\x1b[97m"
	YELLOW =      "\x1b[93m"
	DARK_YELLOW = "\x1b[33m"
	RED =         "\x1b[91m"
	PURPLE =      "\x1b[31m"
	NO_COLOR =    "\x1b[39m"

	def test_WriteFatal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		try:
			app.WriteFatal("This is a fatal message.")
		except SystemExit:
			pass

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", err.readline())

	def test_WriteFatalNoExit(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteFatal("This is a fatal message.", immediateExit=False)

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.PURPLE}[FATAL]     This is a fatal message.{self.NO_COLOR}\n", err.readline())

	def test_WriteError(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteError("This is a error message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.RED}[ERROR]     This is a error message.{self.NO_COLOR}\n", err.readline())

	def test_WriteQuiet(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteQuiet("This is a quiet message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.WHITE}This is a quiet message.{self.NO_COLOR}\n", err.readline())

	def test_WriteCriticalWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteCritical("This is a critical warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.DARK_YELLOW}[CRITICAL]  This is a critical warning message.{self.NO_COLOR}\n", err.readline())

	def test_WriteWarning(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteWarning("This is a warning message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.YELLOW}[WARNING]   This is a warning message.{self.NO_COLOR}\n", err.readline())

	def test_WriteInfo(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteInfo("This is a info message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.WHITE}This is a info message.{self.NO_COLOR}\n", err.readline())

	def test_WriteNormal(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteNormal("This is a normal message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(f"{self.WHITE}This is a normal message.{self.NO_COLOR}\n", err.readline())

	def test_WriteDryRun(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDryRun("This is a dryRun message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteVerboseDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteVerbose("This is a verbose message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())

	def test_WriteDebugDefault(self) -> None:
		class Application(TerminalApplication):
			def __init__(self) -> None:
				super().__init__(mode=Mode.DataToStdOut_OtherToStdErr)

		app = Application()
		app._stdout, app._stderr = out, err = StringIO(), StringIO()

		app.WriteDebug("This is a debug message.")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual(0, err.tell())


class Indentation(Testcase):
	"""The indentation recorded on a line is applied when the line is printed."""

	@staticmethod
	def _Capture(program: TerminalApplication) -> str:
		"""Redirect the application's STDOUT into a buffer and return what was written."""
		program._stdout = StringIO()
		return program._stdout

	def test_IndentIsPrinted(self) -> None:
		class TestApplication(TerminalApplication):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		buffer = self._Capture(program)
		program.WriteNormal("indented", indent=2)

		self.assertEqual(2, program.Lines[0].Indent)
		self.assertIn(f"{TerminalApplication.INDENT * 2}indented", buffer.getvalue())

	def test_NoIndentPrintsNoLeadingSpace(self) -> None:
		class TestApplication(TerminalApplication):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		buffer = self._Capture(program)
		program.WriteNormal("plain")

		self.assertNotIn(f"{TerminalApplication.INDENT}plain", buffer.getvalue())

	def test_BaseIndentAddsToTheLineIndent(self) -> None:
		class TestApplication(TerminalApplication):    # own class: the base class is a singleton
			pass

		program = TestApplication()
		buffer = self._Capture(program)
		program.BaseIndent = 2
		program.WriteNormal("deeper", indent=3)

		self.assertEqual(5, program.Lines[0].Indent)
		self.assertIn(f"{TerminalApplication.INDENT * 5}deeper", buffer.getvalue())
