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
The commands of the :program:`pyTooling` program, run as the installed console script.
"""
from os         import environ
from pathlib    import Path
from subprocess import CompletedProcess
from tempfile   import TemporaryDirectory
from typing     import ClassVar

from pyTooling.TerminalUI import TerminalApplication
from pyTooling.Testing    import ApplicationTestcase, stripANSIColorCodes


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def environmentWithout(*names: str) -> dict[str, str]:
	"""
	Return this process's environment without the given variables.

	The ``pipeline`` command falls back to the variables a workflow sets, and these tests run inside such a
	workflow, so the fallback has to be taken away to see what the command does without it.

	:param names: Names of the variables to leave out.
	:returns:     The environment to run the program in.
	"""
	return {name: value for name, value in environ.items() if name not in names}


class ProgramMixin:
	"""
	What every testcase here runs, and how it reads what the program printed.

	A **classic mixin** - a plain class, no metaclass: it is combined with :class:`~pyTooling.Testing.Testcase`,
	which derives from :class:`unittest.TestCase` and has no ``__slots__``, so ``mixin=True`` would raise
	:exc:`~pyTooling.Exceptions.BaseClassWithoutSlotsError`.
	"""

	_consoleScript:  ClassVar[str] = "pyTooling"
	_runnableModule: ClassVar[str] = "pyTooling.CLI"

	def Output(self, result: CompletedProcess) -> str:
		"""
		Return what the program printed on both streams, without the ANSI escape sequences colouring it.

		The program colours its output whether or not a terminal is attached, and it writes errors to stderr and
		everything else to stdout, so a testcase looking for a message shouldn't have to know which stream carried it.

		:param result: The completed process.
		:returns:      Both streams, joined and stripped of colour.
		"""
		return stripANSIColorCodes(f"{result.stdout}{result.stderr}")


class CommonCommands(ProgramMixin, ApplicationTestcase):
	"""The commands every pyTooling program has: no command at all, ``help`` and ``version``."""

	def test_NoCommand(self) -> None:
		"""A call without a command prints the headline and the help page."""
		result = self.RunEntrypoint()

		self.assertExitCode(result)
		output = self.Output(result)
		self.assertIn("pyTooling Service Program", output)
		self.assertIn("usage: pyTooling", output)

	def test_Version(self) -> None:
		result = self.RunEntrypoint("version")

		self.assertExitCode(result)
		output = self.Output(result)
		self.assertIn("Version:", output)
		self.assertIn("https://github.com/pyTooling/pyTooling", output)

	def test_Help(self) -> None:
		"""The help page names every command the program has."""
		result = self.RunEntrypoint("help")

		self.assertExitCode(result)
		output = self.Output(result)
		self.assertIn("Display help page(s)", output)
		self.assertIn("Display version information.", output)
		self.assertIn("Read a CI pipeline run", output)

	def test_Help_Command(self) -> None:
		"""The help page of one command names every option of that command."""
		result = self.RunEntrypoint("help", "pipeline")

		self.assertExitCode(result)
		output = self.Output(result)
		for option in ("--github-pipeline-id", "--github-repository", "--trace-file", "--gantt", "--force"):
			self.assertIn(option, output)

	def test_UnknownCommand(self) -> None:
		"""A command the program doesn't have is argparse's error, not a traceback."""
		result = self.RunEntrypoint("nonsense")

		self.assertNotEqual(0, result.returncode)
		output = self.Output(result)
		self.assertIn("invalid choice", output)
		self.assertIn("nonsense", output)

	def test_Module(self) -> None:
		"""Both paths reach the same program, so a difference is in the entry point rather than in the code."""
		entrypoint = self.RunEntrypoint("version")
		module =     self.RunModule("version")

		self.assertExitCode(entrypoint)
		self.assertExitCode(module)
		self.assertEqual(self.Output(entrypoint), self.Output(module))


class PipelineCommand(ProgramMixin, ApplicationTestcase):
	"""
	What the ``pipeline`` command says before it reads anything.

	The command checks its outputs and its arguments before the network round-trip, so everything here runs without
	a GitHub token and without reaching GitHub.
	"""

	def test_TraceFile_UnknownFormat(self) -> None:
		"""A format '--trace-file' doesn't accept is reported with the formats it does."""
		result = self.RunEntrypoint(
			"pipeline", "--github-repository=pyTooling/pyTooling", "--github-pipeline-id=35479251694",
			"--trace-file=nonsense:trace.json"
		)

		self.assertExitCode(result, TerminalApplication.FATAL_EXIT_CODE)
		output = self.Output(result)
		self.assertIn("'nonsense' is not a valid TraceFormat.", output)
		self.assertIn("Allowed values: otlp-json", output)

	def test_Gantt_WrongSuffix(self) -> None:
		"""A Gantt format writing another file type than the name says is reported, not silently renamed."""
		result = self.RunEntrypoint(
			"pipeline", "--github-repository=pyTooling/pyTooling", "--github-pipeline-id=35479251694",
			"--gantt=matplotlib-png:chart.svg"
		)

		self.assertExitCode(result, TerminalApplication.FATAL_EXIT_CODE)
		self.assertIn("writes a '.png' file", self.Output(result))

	def test_TraceFile_Exists(self) -> None:
		"""Without '--force', a file that exists is an error and keeps its content."""
		with TemporaryDirectory() as directory:
			existing = Path(directory) / "trace.json"
			existing.write_text("{}", encoding="utf-8")

			result = self.RunEntrypoint(
				"pipeline", "--github-repository=pyTooling/pyTooling", "--github-pipeline-id=35479251694",
				f"--trace-file={existing}"
			)

			self.assertExitCode(result, TerminalApplication.FATAL_EXIT_CODE)
			output = self.Output(result)
			self.assertIn("exists.", output)
			self.assertIn("--force", output)
			self.assertEqual("{}", existing.read_text(encoding="utf-8"))

	def test_Repository_Missing(self) -> None:
		"""Without '--github-repository' and without $GITHUB_REPOSITORY, the command says which one to set."""
		result = self.RunEntrypoint(
			"pipeline", "--github-pipeline-id=35479251694",
			environment=environmentWithout("GITHUB_REPOSITORY")
		)

		self.assertExitCode(result, 2)
		output = self.Output(result)
		self.assertIn("No repository given.", output)
		self.assertIn("$GITHUB_REPOSITORY", output)

	def test_PipelineID_Missing(self) -> None:
		"""Without '--github-pipeline-id' and without $GITHUB_RUN_ID, the command says which one to set."""
		result = self.RunEntrypoint(
			"pipeline", "--github-repository=pyTooling/pyTooling",
			environment=environmentWithout("GITHUB_RUN_ID")
		)

		self.assertExitCode(result, 2)
		output = self.Output(result)
		self.assertIn("No workflow run given.", output)
		self.assertIn("$GITHUB_RUN_ID", output)

	def test_PipelineID_NotANumber(self) -> None:
		"""A workflow run is the number in its URL, so anything else is rejected before the request."""
		result = self.RunEntrypoint(
			"pipeline", "--github-repository=pyTooling/pyTooling", "--github-pipeline-id=latest"
		)

		self.assertExitCode(result, 2)
		self.assertIn("Workflow run 'latest' isn't a number.", self.Output(result))
