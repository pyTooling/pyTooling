# ==================================================================================================================== #
#               _____           _ _               ____ _     ___   ____  _            _ _                              #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _| |  _ \(_)_ __   ___| (_)_ __   ___                   #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |  | |_) | | '_ \ / _ \ | | '_ \ / _ \                  #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | | _|  __/| | |_) |  __/ | | | | |  __/                  #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___(_)_|   |_| .__/ \___|_|_|_| |_|\___|                  #
#   |_|    |___/                          |___/                           |_|                                          #
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
#
"""
The :pycode:`pipeline` command: read a CI pipeline and write what it took.

.. rubric:: Usage

.. code-block:: bash

   pyTooling pipeline --github-repository=pyTooling/pyTooling \
                      --github-pipeline-id=35479251694 \
                      --trace-file=report/Pipeline.otlp.json

.. hint::

   See :ref:`high-level help <CLI/Pipeline>` for explanations and usage examples.
"""
from argparse                                 import Namespace
from os                                       import getenv
from pathlib                                  import Path
from typing                                   import ClassVar, Optional as Nullable, Self

from pyTooling.Common                         import StringEnum
from pyTooling.Decorators                     import export
from pyTooling.MetaClasses                    import ExtendedType
from pyTooling.Attributes.ArgParse            import CommandHandler, splitFormat
from pyTooling.Attributes.ArgParse.Flag       import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag import LongValuedFlag
from pyTooling.Exceptions                     import MissingDependencyError
from pyTooling.Tracing                        import Trace
from pyTooling.Tracing.CI.GitHub              import WorkflowRunReader
from pyTooling.Tracing.Render                 import GanttLayout, ciSpanFilter


@export
class TraceFormat(StringEnum):
	"""The formats a trace can be written in, as ``--trace-file`` names them."""

	OTLPJSON = "otlp-json"  #: OpenTelemetry's OTLP/JSON encoding of a trace.

	DEFAULT = OTLPJSON      #: The format ``--trace-file`` writes when its value names none.


@export
class GanttFormat(StringEnum):
	"""The formats a Gantt chart can be drawn in, as ``--gantt`` names them: the backend and the file format."""

	MatplotlibPNG = "matplotlib-png"  #: A raster image, drawn by matplotlib.
	MatplotlibSVG = "matplotlib-svg"  #: A vector image, drawn by matplotlib.
	MatplotlibPDF = "matplotlib-pdf"  #: A PDF page, drawn by matplotlib.

	DEFAULT = MatplotlibPNG           #: The format ``--gantt`` draws when neither its value nor the suffix names one.

	@classmethod
	def FromPath(cls, file: Path) -> Self:
		"""
		Return the format the file's suffix implies, so the format is rarely written out.

		A format is the backend and the file format - ``matplotlib-svg`` writes the ``.svg`` half - so the suffix
		names the format already, and :pycode:`--gantt=report/Pipeline.svg` draws an SVG.

		:param file: The file ``--gantt`` named.
		:returns:    The format matching the file's suffix, otherwise :attr:`DEFAULT`.
		"""
		try:
			return cls.Parse(f"matplotlib-{file.suffix.lower().lstrip('.')}")
		except ValueError:
			return cls.DEFAULT


@export
class PipelineHandlers(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class contributing the :pycode:`pipeline` command to :class:`~pyTooling.CLI.Application`.

	The command reads one run of a CI pipeline into a :class:`~pyTooling.Tracing.Trace` and writes what was asked
	of it. Reading and writing are separate steps on purpose: the trace is the intermediate every output is derived
	from, so a further output is a further option and not a second reader.
	"""
	ENVIRONMENT_REPOSITORY: ClassVar[str] = "GITHUB_REPOSITORY"  #: Variable naming the repository inside a workflow.
	ENVIRONMENT_RUN_ID:     ClassVar[str] = "GITHUB_RUN_ID"      #: Variable naming the run inside a workflow.
	ENVIRONMENT_TOKEN:      ClassVar[str] = "GITHUB_TOKEN"       #: Variable holding the token to read the run with.

	@CommandHandler(
		"pipeline",
		help="Read a CI pipeline run and write what it took.",
		description="Read a CI pipeline run and write what it took."
	)
	@LongValuedFlag(
		"--github-repository", dest="githubRepository", metaName="owner/name", optional=True,
		help=f"Repository the workflow run belongs to. Default: ${ENVIRONMENT_REPOSITORY}."
	)
	@LongValuedFlag(
		"--github-pipeline-id", dest="githubPipelineID", metaName="ID", optional=True,
		help=f"Identifier of the GitHub Actions workflow run. Default: ${ENVIRONMENT_RUN_ID}."
	)
	@LongValuedFlag(
		"--trace-file", dest="traceFile", metaName="[format:]file", optional=True,
		help=f"Write the trace. Format: {', '.join(TraceFormat)}. Default: {TraceFormat.DEFAULT}."
	)
	@LongValuedFlag(
		"--gantt", dest="gantt", metaName="[format:]file", optional=True,
		help=f"Draw a Gantt chart. Format: {', '.join(GanttFormat)}. Default: {GanttFormat.DEFAULT}."
	)
	@LongFlag("--force", dest="force", help="Overwrite files that exist.")
	def HandlePipeline(self, args: Namespace) -> None:
		"""
		Handle program calls with command ``pipeline``.

		The outputs are checked **before** the pipeline is read, so a misspelled format or a file that exists is
		reported at once instead of after a network round-trip.

		:param args: The parsed command line.
		"""
		self._PrintHeadline()

		outputs = self._CheckOutputs(args)
		self.ExitOnPreviousErrors()

		trace = self._ReadPipeline(args)
		self._PrintSummary(trace)
		self._WriteOutputs(outputs, trace)

		self.ExitOnPreviousErrors()

	def _CheckOutputs(self, args: Namespace) -> list[tuple[str, StringEnum, Path]]:
		"""
		Read every output option, and report what can't be written before anything is read.

		:param args: The parsed command line.
		:returns:    One ``(option, format, file)`` per output that was asked for and can be written.
		"""
		outputs: list[tuple[str, StringEnum, Path]] = []
		for option, value, formats in self._Outputs(args):
			if value is None:
				continue

			try:
				fileFormat, file = splitFormat(value, formats)
			except ValueError as ex:
				self.WriteError(f"Option '{option}': {ex}")
				for note in ex.__notes__:
					self.WriteErrorNote(note)
				continue

			if option == "--gantt" and file.suffix.lower().lstrip(".") != (suffix := fileFormat.partition("-")[2]):
				self.WriteError(f"Option '--gantt': format '{fileFormat}' writes a '.{suffix}' file.")
				self.WriteErrorNote(f"Got '{file.name}'. Name the file '.{suffix}', or state the format it is in.")
				continue

			if file.exists() and not args.force:
				self.WriteError(f"File '{file}' exists.")
				self.WriteErrorNote("Use '--force' to overwrite it.")
				continue

			outputs.append((option, fileFormat, file))

		return outputs

	def _Outputs(self, args: Namespace) -> tuple[tuple[str, Nullable[str], type[StringEnum]], ...]:
		"""
		Return the output options this command offers, as ``(option, value, formats)``.

		What a value naming no format gets is the enumeration's business, not this command's: :class:`TraceFormat`
		answers with its ``DEFAULT``, :class:`GanttFormat` with the one its suffix implies.

		:param args: The parsed command line.
		:returns:    One entry per output option, whether or not it was given.
		"""
		return (
			("--trace-file", args.traceFile, TraceFormat),
			("--gantt",      args.gantt,     GanttFormat),
		)

	def _WriteOutputs(self, outputs: list[tuple[str, StringEnum, Path]], trace: Trace) -> None:
		"""
		Write every output the command line asked for.

		:param outputs: The outputs, as :meth:`_CheckOutputs` returned them.
		:param trace:   The workflow run as a trace.
		"""
		for option, fileFormat, file in outputs:
			if option == "--trace-file":
				self.WriteVerbose(f"Writing the trace as '{fileFormat}' to '{file}' ...")
				trace.WriteJSONFile(file)
				self.WriteNormal(f"Trace:     {file}")
			elif option == "--gantt":
				self._WriteGantt(fileFormat, file, trace)

	def _WriteGantt(self, fileFormat: GanttFormat, file: Path, trace: Trace) -> None:
		"""
		Lay the trace out as a Gantt chart and draw it with the backend the format names.

		The steps of a job are left out: a pipeline of 57 jobs has more than a thousand steps, and a chart of one row
		per step is a different picture than a chart of one row per job.

		:param fileFormat: The format, one of :class:`GanttFormat`.
		:param file:       The file to write.
		:param trace:      The workflow run as a trace.
		"""
		try:
			from pyTooling.Tracing.Render.Matplotlib import MatplotlibRenderer
		except MissingDependencyError as ex:
			self.WriteError(f"Option '--gantt': format '{fileFormat}' needs matplotlib.")
			self.WriteErrorNote(f"{ex}")
			return

		self.WriteVerbose(f"Drawing the Gantt chart as '{fileFormat}' to '{file}' ...")
		layout = GanttLayout(trace, spanFilter=ciSpanFilter())
		MatplotlibRenderer(layout).Write(file)
		self.WriteNormal(f"Gantt:     {file} ({layout.RowCount} rows)")

	def _ReadPipeline(self, args: Namespace) -> Trace:
		"""
		Read the workflow run the command line names into a trace.

		:param args: The parsed command line.
		:returns:    The workflow run as a trace.
		"""
		repository = args.githubRepository if args.githubRepository is not None else getenv(self.ENVIRONMENT_REPOSITORY)
		if repository is None:
			self.WriteError("No repository given.")
			self.WriteErrorNote(f"Set '--github-repository=owner/name', or ${self.ENVIRONMENT_REPOSITORY}.")
			self.Exit(2)

		runID = args.githubPipelineID if args.githubPipelineID is not None else getenv(self.ENVIRONMENT_RUN_ID)
		if runID is None:
			self.WriteError("No workflow run given.")
			self.WriteErrorNote(f"Set '--github-pipeline-id=<ID>', or ${self.ENVIRONMENT_RUN_ID}.")
			self.Exit(2)
		elif not runID.isdigit():
			self.WriteError(f"Workflow run '{runID}' isn't a number.")
			self.WriteErrorNote("It is the number in the run's URL: .../actions/runs/35479251694.")
			self.Exit(2)

		self.WriteVerbose(f"Reading run {runID} of '{repository}' ...")
		reader = WorkflowRunReader(repository, getenv(self.ENVIRONMENT_TOKEN))

		return reader.ReadRun(int(runID))

	def _PrintSummary(self, trace: Trace) -> None:
		"""
		Print what the pipeline took, so the command says something without being asked to write a file.

		:param trace: The workflow run as a trace.
		"""
		self.WriteNormal(f"Pipeline:  {trace.Name}")
		self.WriteNormal(f"Began:     {trace.StartTime}")
		self.WriteNormal(f"Wall time: {trace.Duration:.0f} s")
