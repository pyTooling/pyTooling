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
from datetime           import datetime, timedelta, timezone
from json               import loads as json_loads
from os                 import environ
from pathlib            import Path
from sys                import argv as sys_argv
from tempfile           import TemporaryDirectory
from typing             import ClassVar, Iterable
from unittest           import skipUnless
from unittest.mock      import patch

from pyTooling.Attributes.ArgParse import splitFormat
from pyTooling.CLI                 import Application, main
from pyTooling.CLI.Pipeline        import GanttFormat, TraceFormat
from pyTooling.Exceptions          import MissingDependencyError
from pyTooling.Testing             import Testcase
from pyTooling.Tracing             import Span, Trace
from pyTooling.Tracing.CI          import CI, OTLP
from pyTooling.Tracing.CI.GitHub   import GitHub

try:
	import matplotlib
	HAS_MATPLOTLIB = True
except ImportError:  # pragma: no cover
	HAS_MATPLOTLIB = False


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

	def test_Help_Command(self) -> None:
		output = _run(["help", "version"])

		self.assertIn("usage: pyTooling version", output)

	def test_NoCommand(self) -> None:
		"""A call without a command prints the help page rather than an error."""
		output = _run([])

		self.assertIn("usage: pyTooling", output)


class Formats(Testcase):
	def test_Parse(self) -> None:
		self.assertIs(TraceFormat.OTLPJSON, TraceFormat.Parse("otlp-json"))

	def test_Parse_Unknown(self) -> None:
		"""The enumeration names itself and lists what it accepts, because the user typed the name."""
		with self.assertRaises(ValueError) as context:
			_ = TraceFormat.Parse("json")

		self.assertEqual("'json' is not a valid TraceFormat.", str(context.exception))
		self.assertIn("Allowed values: otlp-json.", context.exception.__notes__)

	def test_ItIsAString(self) -> None:
		"""It's a StrEnum, so a format goes into a message without being unwrapped first."""
		self.assertEqual("otlp-json", f"{TraceFormat.OTLPJSON}")

	def test_Default(self) -> None:
		self.assertIs(TraceFormat.OTLPJSON, TraceFormat.DEFAULT)

	def test_NoFormat(self) -> None:
		"""'--trace-file=report/Pipeline.otlp.json' writes OTLP/JSON, the enumeration's ``DEFAULT``."""
		self.assertEqual((TraceFormat.OTLPJSON, Path("report/Pipeline.otlp.json")),
		                 splitFormat("report/Pipeline.otlp.json", TraceFormat))


class PipelineCommand(Testcase):
	"""
	The ``pipeline`` command, called in-process.

	:meth:`~pyTooling.CLI.Pipeline.PipelineHandlers._ReadPipeline` falls back to the variables a workflow sets, and
	this test suite runs inside such a workflow, so a testcase about a **missing** argument has to take the fallback
	away. Without that it passes on a developer's machine and reads the CI server's own pipeline on the CI server.
	"""

	NO_WORKFLOW: ClassVar[dict[str, str]] = {"GITHUB_REPOSITORY": "", "GITHUB_RUN_ID": ""}  #: The fallback, emptied.

	def test_Help(self) -> None:
		output = _run(["help", "pipeline"])

		self.assertIn("--github-repository", output)
		self.assertIn("--github-pipeline-id", output)
		self.assertIn("--trace-file", output)
		self.assertIn("--gantt", output)
		self.assertIn("--force", output)

	def test_Repository_Missing(self) -> None:
		"""Nothing is read before the command knows which repository to read from."""
		application = Application()

		with patch.dict(environ, self.NO_WORKFLOW):
			with self.assertRaises(SystemExit):
				application.HandlePipeline(Namespace(
					githubRepository=None, githubPipelineID=None, traceFile=None, gantt=None, force=False
				))

	def test_TraceFile_UnsupportedFormat(self) -> None:
		"""A misspelled format is reported before anything is read."""
		application = Application()
		arguments = Namespace(
			githubRepository=None, githubPipelineID=None, traceFile="json:trace.json", gantt=None, force=False
		)

		with patch.dict(environ, self.NO_WORKFLOW):
			with self.assertRaises(SystemExit):
				application.HandlePipeline(arguments)

	def test_Gantt_SuffixContradictsTheFormat(self) -> None:
		application = Application()
		arguments = Namespace(
			githubRepository=None, githubPipelineID=None, traceFile=None, gantt="matplotlib-png:chart.svg", force=False
		)

		with patch.dict(environ, self.NO_WORKFLOW):
			with self.assertRaises(SystemExit):
				application.HandlePipeline(arguments)

	def test_Gantt_NoFormat_NotAPNG(self) -> None:
		"""A value naming no format gets 'matplotlib-png', so an SVG file has to state its format."""
		application = Application()
		errors = StringIO()
		stream = application._stderr
		arguments = Namespace(
			githubRepository=None, githubPipelineID=None, traceFile=None, gantt="chart.svg", force=False
		)

		application._stderr = errors
		try:
			with patch.dict(environ, self.NO_WORKFLOW):
				with self.assertRaises(SystemExit):
					application.HandlePipeline(arguments)
		finally:
			application._stderr = stream

		self.assertIn("Option '--gantt': format 'matplotlib-png' writes a '.png' file.", errors.getvalue())


class GanttFormats(Testcase):
	def test_Default(self) -> None:
		self.assertIs(GanttFormat.MatplotlibPNG, GanttFormat.DEFAULT)

	def test_EveryFormat(self) -> None:
		"""A format is the backend and the file format, and the second half is the file's suffix."""
		for fileFormat in GanttFormat:
			with self.subTest(format=fileFormat):
				backend, _, suffix = fileFormat.value.partition("-")
				self.assertEqual("matplotlib", backend)
				self.assertIn(suffix, ("png", "svg", "pdf"))

	def test_NoFormat(self) -> None:
		"""A value naming no format gets the default, whatever the file's suffix says."""
		self.assertEqual((GanttFormat.MatplotlibPNG, Path("report/Pipeline.svg")),
		                 splitFormat("report/Pipeline.svg", GanttFormat))


class MissingDependency(Testcase):
	def test_MainPrintsTheInstallCommands(self) -> None:
		"""An optional package that isn't installed is not a bug, so 'main' hands it to its own printer."""
		application = Application()
		errors = StringIO()
		stream = application._stderr
		exception = MissingDependencyError(dependency="matplotlib", extra="diagram")

		application._stderr = errors
		try:
			with patch.object(Application, "Run", side_effect=exception):
				with self.assertRaises(SystemExit) as context:
					main()
		finally:
			application._stderr = stream

		self.assertEqual(MissingDependencyError.EXIT_CODE, context.exception.code)
		self.assertIn("matplotlib", errors.getvalue())
		self.assertIn("pip install pyTooling[diagram]", errors.getvalue())



def _pipelineTrace() -> Trace:
	"""
	Build the trace a reader would return for a small finished run: one job with one step.

	:returns: The trace.
	"""
	begin = datetime(2026, 9, 15, 6, 35, 0, tzinfo=timezone.utc)
	trace = Trace("Pipeline", begin, begin + timedelta(seconds=60))
	trace[CI.Span.Kind] = "pipeline"

	job = Span("Build", begin + timedelta(seconds=5), begin + timedelta(seconds=50), parent=trace)
	job[CI.Span.Kind] = "job"
	job[OTLP.CICD.Pipeline.Task.Name] = "Build"
	job[GitHub.Runner.Labels] = ["ubuntu-26.04"]
	job[OTLP.CICD.Pipeline.Task.Run.Result] = "success"

	step = Span("Compile", begin + timedelta(seconds=6), begin + timedelta(seconds=40), parent=job)
	step[CI.Span.Kind] = "step"
	step[OTLP.CICD.Pipeline.Task.Run.Result] = "success"

	return trace


class PipelineOutputs(Testcase):
	"""
	What ``pipeline`` writes once it has read a run, called in-process.

	:meth:`~pyTooling.CLI.Pipeline.PipelineHandlers._ReadPipeline` is replaced by a fixture trace, so the testcases
	run offline and always see the same run.
	"""

	def _Run(self, *outputs: str) -> str:
		"""
		Run ``pipeline`` with the given output options against the fixture trace.

		The program is a singleton, and testcases reporting an error leave it counted, which would make this run exit
		before writing anything; so the count starts at zero.

		:param outputs: The output options, e.g. ``--trace-file=...``.
		:returns:       Everything the program printed.
		"""
		Application()._errorCount = 0
		with patch.object(Application, "_ReadPipeline", return_value=_pipelineTrace()):
			return _run(["pipeline", "--github-repository=owner/name", "--github-pipeline-id=1", *outputs])

	def test_TraceFile(self) -> None:
		with TemporaryDirectory() as directory:
			file = Path(directory) / "report" / "Pipeline.otlp.json"
			output = self._Run(f"--trace-file={file}")
			document = json_loads(file.read_text(encoding="utf-8"))

		spans = document["resourceSpans"][0]["scopeSpans"][0]["spans"]
		self.assertIn(f"Trace:     {file}", output)
		self.assertEqual(["Pipeline", "Build", "Compile"], [span["name"] for span in spans])

	def test_TraceFile_Force(self) -> None:
		"""With '--force', a file that exists is overwritten."""
		with TemporaryDirectory() as directory:
			file = Path(directory) / "Pipeline.otlp.json"
			file.write_text("old", encoding="utf-8")
			output = self._Run(f"--trace-file={file}", "--force")
			content = file.read_text(encoding="utf-8")

		self.assertIn(f"Trace:     {file}", output)
		self.assertIn("resourceSpans", content)

	@skipUnless(HAS_MATPLOTLIB, "Needs matplotlib, installed by the extra 'pyTooling[diagram]'.")
	def test_Gantt(self) -> None:
		"""Every format writes the file type it names, one row per timespan the CI filter keeps."""
		for prefix, suffix, magic in (
			("", "png", b"\x89PNG"),
			("matplotlib-svg:", "svg", b"<?xml"),
			("matplotlib-pdf:", "pdf", b"%PDF"),
		):
			with self.subTest(format=suffix):
				with TemporaryDirectory() as directory:
					file = Path(directory) / f"Pipeline.{suffix}"
					output = self._Run(f"--gantt={prefix}{file}")
					content = file.read_bytes()

				self.assertEqual(magic, content[:len(magic)])
				self.assertIn(f"Gantt:     {file} (2 rows)", output)

	@skipUnless(HAS_MATPLOTLIB, "Needs matplotlib, installed by the extra 'pyTooling[diagram]'.")
	def test_BothOutputs(self) -> None:
		"""The trace is read once, and every output is written from it."""
		with TemporaryDirectory() as directory:
			trace = Path(directory) / "Pipeline.otlp.json"
			chart = Path(directory) / "Pipeline.png"
			output = self._Run(f"--trace-file={trace}", f"--gantt={chart}")

			self.assertTrue(trace.exists())
			self.assertTrue(chart.exists())

		self.assertIn("Pipeline:  Pipeline", output)
		self.assertIn("Wall time: 60 s", output)
