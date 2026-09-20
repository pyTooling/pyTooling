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
Unit tests for :mod:`pyTooling.CLI`: the program's commands and the parser they are declared with.
"""
from io                 import StringIO
from argparse           import Namespace
from contextlib         import redirect_stdout
from pathlib            import Path
from sys                import argv as sys_argv
from typing             import Iterable

from pyTooling.CLI          import Application
from pyTooling.CLI.Pipeline import DEFAULT_TRACE_FORMAT, TRACE_FORMATS, splitFormat
from pyTooling.Testing      import Testcase


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
	sys_argv[:] = ["pyTooling", *arguments]
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

		self.assertEqual("pyTooling", application.MainParser.prog)
		self.assertIn("help", application.SubParsers)
		self.assertIn("version", application.SubParsers)
		self.assertIn("pipeline", application.SubParsers)

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


class SplitFormat(Testcase):
	def test_NoFormat(self) -> None:
		self.assertEqual((DEFAULT_TRACE_FORMAT, Path("report/trace.json")),
		                 splitFormat("report/trace.json", TRACE_FORMATS, DEFAULT_TRACE_FORMAT))

	def test_Format(self) -> None:
		self.assertEqual(("otlp-json", Path("trace.json")),
		                 splitFormat("otlp-json:trace.json", TRACE_FORMATS, DEFAULT_TRACE_FORMAT))

	def test_AWindowsDriveIsNotAFormat(self) -> None:
		"""A format is more than one character long, so a drive letter stays part of the path."""
		value = r"C:\report\trace.json"

		fileFormat, file = splitFormat(value, TRACE_FORMATS, DEFAULT_TRACE_FORMAT)

		self.assertEqual(DEFAULT_TRACE_FORMAT, fileFormat)
		self.assertEqual(Path(value), file, "The whole value is the path, so the drive is still on it.")

	def test_AColonBelowADirectoryIsNotAFormat(self) -> None:
		fileFormat, file = splitFormat("reports/run:2/trace.json", TRACE_FORMATS, DEFAULT_TRACE_FORMAT)

		self.assertEqual(DEFAULT_TRACE_FORMAT, fileFormat)
		self.assertEqual(Path("reports/run:2/trace.json"), file)

	def test_AnUnsupportedFormat(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = splitFormat("json:trace.json", TRACE_FORMATS, DEFAULT_TRACE_FORMAT)

		self.assertEqual("Format 'json' isn't supported.", str(context.exception))
		self.assertIn("Supported formats: otlp-json.", context.exception.__notes__)


class PipelineCommand(Testcase):
	def test_ItsHelpPageNamesItsOptions(self) -> None:
		output = _run(["help", "pipeline"])

		self.assertIn("--github-pipeline-id", output)
		self.assertIn("--trace-file", output)
		self.assertIn("--force", output)

	def test_WithoutARepository(self) -> None:
		"""Nothing is read before the command knows which repository to read from."""
		application = Application()

		with self.assertRaises(SystemExit):
			application.HandlePipeline(Namespace(
				githubRepository=None, githubPipelineID=None, traceFile=None, force=False
			))

	def test_AnUnsupportedFormatIsReportedBeforeAnythingIsRead(self) -> None:
		application = Application()
		arguments = Namespace(githubRepository=None, githubPipelineID=None, traceFile="json:trace.json", force=False)

		with self.assertRaises(SystemExit):
			application.HandlePipeline(arguments)
