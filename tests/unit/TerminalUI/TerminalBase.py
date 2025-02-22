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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""pyTooling.TerminalUI"""
from io                   import StringIO
from unittest             import TestCase

from pyTooling.Exceptions import ExceptionBase

from pyTooling.TerminalUI import TerminalBaseApplication


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiate(TestCase):
	def test_NoConfigure(self) -> None:
		term = TerminalBaseApplication()

		self.assertGreaterEqual(term.Width, 80)
		self.assertGreaterEqual(term.Height, 25)

	def test_UninitializeColors(self) -> None:
		term = TerminalBaseApplication()
		term.UninitializeColors()

	def test_InitializeColors(self) -> None:
		term = TerminalBaseApplication()
		term.UninitializeColors()
		term.InitializeColors()

	def test_ApplicationDerivedFromTerminal(self) -> None:
		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.FATAL_EXIT_CODE = 0

		app = Application()


class WriteMessages(TestCase):
	def test_WriteToStdOut(self) -> None:
		term = TerminalBaseApplication()
		term._stdout, term._stderr = out, err = StringIO(), StringIO()

		term.WriteToStdOut("Message")

		out.seek(0)
		err.seek(0)

		self.assertEqual("Message", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteLineToStdOut(self) -> None:
		term = TerminalBaseApplication()
		term._stdout, term._stderr = out, err = StringIO(), StringIO()

		term.WriteLineToStdOut("Message")

		out.seek(0)
		err.seek(0)

		self.assertEqual("Message\n", out.readline())
		self.assertEqual(0, err.tell())

	def test_WriteToStdErr(self) -> None:
		term = TerminalBaseApplication()
		term._stdout, term._stderr = out, err = StringIO(), StringIO()

		term.WriteToStdErr("Message")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual("Message", err.readline())

	def test_WriteLineToStdErr(self) -> None:
		term = TerminalBaseApplication()
		term._stdout, term._stderr = out, err = StringIO(), StringIO()

		term.WriteLineToStdErr("Message")

		out.seek(0)
		err.seek(0)

		self.assertEqual(0, out.tell())
		self.assertEqual("Message\n", err.readline())


class Exiting(TestCase):
	def test_Exit(self) -> None:
		term = TerminalBaseApplication()

		with self.assertRaises(SystemExit) as ex:
			term.Exit(1)
		self.assertEqual(1, ex.exception.code)

	def test_FatalExit4(self) -> None:
		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		with self.assertRaises(SystemExit) as ex:
			app.FatalExit(4)
		self.assertEqual(4, ex.exception.code)

	def test_FatalExit254(self) -> None:
		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.FATAL_EXIT_CODE = 254

		app = Application()
		with self.assertRaises(SystemExit) as ex:
			app.FatalExit()
		self.assertEqual(254, ex.exception.code)

	def test_FatalExitDefault(self) -> None:
		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

		app = Application()
		with self.assertRaises(SystemExit) as ex:
			app.FatalExit()
		self.assertEqual(255, ex.exception.code)

	def test_CheckPythonVersion3(self) -> None:
		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()
				super().CheckPythonVersion((3, 8, 0))

		_ = Application()

	def test_CheckPythonVersion4(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()
				super().CheckPythonVersion((4, 9, 0))

		with self.assertRaises(SystemExit) as exitEx:
			_ = Application()
		self.assertEqual(254, exitEx.exception.code)


class ExceptionHandling(TestCase):
	def test_NotImplemented(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.ISSUE_TRACKER_URL = "https://GitHub.com/pyTooling/pyTooling/issues"

			def Run(self):
				raise NotImplementedError(f"Abstract method")

		app = Application()
		try:
			app.Run()
		except NotImplementedError as ex:
			with self.assertRaises(SystemExit) as exitEx:
				app.PrintNotImplementedError(ex)
			self.assertEqual(240, exitEx.exception.code)

	def test_Exception(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.ISSUE_TRACKER_URL = "https://GitHub.com/pyTooling/pyTooling/issues"

			def Run(self):
				raise Exception(f"Common exception")

		app = Application()
		try:
			app.Run()
		except Exception as ex:
			with self.assertRaises(SystemExit) as exitEx:
				app.PrintException(ex)
			self.assertEqual(241, exitEx.exception.code)

	def test_ExceptionWithNestedException(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.ISSUE_TRACKER_URL = "https://GitHub.com/pyTooling/pyTooling/issues"

			def Run(self):
				raise Exception(f"Common exception") from FileNotFoundError(f"File doesn't exist.")

		app = Application()
		try:
			app.Run()
		except Exception as ex:
			with self.assertRaises(SystemExit) as exitEx:
				app.PrintException(ex)
			self.assertEqual(241, exitEx.exception.code)

	def test_ExceptionBase(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.ISSUE_TRACKER_URL = "https://GitHub.com/pyTooling/pyTooling/issues"

			def Run(self):
				raise ExceptionBase(f"Base exception")

		app = Application()
		try:
			app.Run()
		except ExceptionBase as ex:
			with self.assertRaises(SystemExit) as exitEx:
				app.PrintExceptionBase(ex)
			self.assertEqual(241, exitEx.exception.code)

	def test_ExceptionBaseWithNestedException(self) -> None:
		print()

		class Application(TerminalBaseApplication):
			def __init__(self) -> None:
				super().__init__()

				self.__class__.ISSUE_TRACKER_URL = "https://GitHub.com/pyTooling/pyTooling/issues"

			def Run(self):
				raise ExceptionBase(f"Base exception") from FileNotFoundError(f"File doesn't exist.")

		app = Application()
		try:
			app.Run()
		except ExceptionBase as ex:
			with self.assertRaises(SystemExit) as exitEx:
				app.PrintExceptionBase(ex)
			self.assertEqual(241, exitEx.exception.code)
