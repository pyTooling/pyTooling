# ==================================================================================================================== #
#               _____           _ _               ____ _     ___                                                       #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|                                                      #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |                                                       #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | |                                                       #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___|                                                      #
#   |_|    |___/                          |___/                                                                        #
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
Unit tests for :mod:`pyTooling.CLI`: the program's commands and the parser they are declared with.
"""
from io                 import StringIO
from contextlib         import redirect_stdout
from sys                import argv as sys_argv
from typing             import Iterable

from pyTooling.CLI      import Application, PROGRAM_NAME
from pyTooling.Testing  import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def _run(arguments: Iterable[str]) -> str:
	"""
	Run the program with the given command line and return what it wrote to stdout.

	The program reads :data:`sys.argv`, so the command line is put there for the call, and it writes through two
	streams - its own, captured when it was constructed, and :data:`sys.stdout`, which argparse prints a help page
	to - so both are pointed at the same buffer.

	:param arguments: The command line, without the program's name.
	:returns:         Everything the program printed.
	"""
	application = Application()
	application.Configure()

	output = StringIO()
	argv = sys_argv[:]
	stream = application._stdout
	sys_argv[:] = [PROGRAM_NAME, *arguments]
	application._stdout = output
	try:
		with redirect_stdout(output):
			application.Run(enableAutoComplete=False)
	finally:
		sys_argv[:] = argv
		application._stdout = stream

	return output.getvalue()


class Parser(Testcase):
	def test_TheCommandsAreDeclaredAsAttributes(self) -> None:
		application = Application()

		self.assertEqual(PROGRAM_NAME, application.MainParser.prog)
		self.assertIn("help", application.SubParsers)
		self.assertIn("version", application.SubParsers)

	def test_TheProgramIsASingleton(self) -> None:
		"""A terminal application is a singleton, so asking for it twice hands out the same program."""
		self.assertIs(Application(), Application())


class Commands(Testcase):
	def test_Version(self) -> None:
		output = _run(["version"])

		self.assertIn("Version:", output)
		self.assertIn("Patrick Lehmann", output)

	def test_Help(self) -> None:
		output = _run(["help"])

		self.assertIn("usage: pyTooling", output)
		self.assertIn("version", output)

	def test_HelpForACommand(self) -> None:
		output = _run(["help", "version"])

		self.assertIn("usage: pyTooling version", output)

	def test_NoCommand(self) -> None:
		"""A call without a command prints the help page rather than an error."""
		output = _run([])

		self.assertIn("usage: pyTooling", output)
