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
from enum                                     import StrEnum
from os                                       import getenv
from pathlib                                  import Path
from typing                                   import ClassVar, Optional as Nullable, Self

from pyTooling.Decorators                     import export
from pyTooling.MetaClasses                    import ExtendedType
from pyTooling.Attributes.ArgParse            import CommandHandler
from pyTooling.Attributes.ArgParse.Flag       import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag import LongValuedFlag
from pyTooling.Tracing                        import Trace
from pyTooling.Tracing.CI.GitHub              import WorkflowRunReader


__all__ = ["DEFAULT_TRACE_FORMAT"]


@export
class OutputFormat(StrEnum):
	"""
	Base-class of the formats an output option of this command accepts.

	It holds no members, so the deriving enumerations can add theirs, and it gives each of them the same parser -
	the one :func:`splitFormat` calls whatever option it is splitting.
	"""

	@classmethod
	def Parse(cls, value: str) -> Self:
		"""
		Return the format of that name.

		:param value:       Name of the format, as a command line spells it.
		:returns:           The format of that name.
		:raises ValueError: If this option accepts no format of that name. The note lists the ones it accepts.
		"""
		if value not in cls._value2member_map_:
			ex = ValueError(f"'{value}' is not a valid {cls.__name__}.")
			ex.add_note(f"Allowed values: {', '.join(item.value for item in cls)}")
			raise ex

		return cls(value)


@export
class TraceFormat(OutputFormat):
	"""The formats a trace can be written in, as ``--trace-file`` names them."""

	OTLPJSON = "otlp-json"  #: OpenTelemetry's OTLP/JSON encoding of a trace.


DEFAULT_TRACE_FORMAT = TraceFormat.OTLPJSON
"""The format a trace is written in when ``--trace-file`` names none."""


@export
def splitFormat(value: str, formats: type[OutputFormat], defaultFormat: OutputFormat) -> tuple[OutputFormat, Path]:
	"""
	Split an option's value of the form ``[<format>:]<file>`` into the format and the file.

	The format is optional, so a value without a colon is a path and gets the default format. A colon alone doesn't
	make a format either: a Windows drive letter (``C:\\report\\trace.json``) and a path holding a colon deeper down
	are paths, because a format is more than one character long and contains no path separator.

	:param value:         The option's value.
	:param formats:       The formats this option accepts.
	:param defaultFormat: The format to assume when the value names none.
	:returns:             The format, and the file to write.
	:raises ValueError:   If the value names a format this option doesn't accept.
	"""
	prefix, colon, rest = value.partition(":")
	if colon == "" or len(prefix) < 2 or "/" in prefix or "\\" in prefix:
		return defaultFormat, Path(value)

	return formats.Parse(prefix), Path(rest)


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
		help=f"Write the trace. Format: {', '.join(item.value for item in TraceFormat)}. Default: {DEFAULT_TRACE_FORMAT}."
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

	def _CheckOutputs(self, args: Namespace) -> list[tuple[str, OutputFormat, Path]]:
		"""
		Read every output option, and report what can't be written before anything is read.

		:param args: The parsed command line.
		:returns:    One ``(option, format, file)`` per output that was asked for and can be written.
		"""
		outputs: list[tuple[str, OutputFormat, Path]] = []
		for option, value, formats, defaultFormat in self._Outputs(args):
			if value is None:
				continue

			try:
				fileFormat, file = splitFormat(value, formats, defaultFormat)
			except ValueError as ex:
				self.WriteError(f"Option '{option}': {ex}")
				for note in ex.__notes__:
					self.WriteErrorNote(note)
				continue

			if file.exists() and not args.force:
				self.WriteError(f"File '{file}' exists.")
				self.WriteErrorNote("Use '--force' to overwrite it.")
				continue

			outputs.append((option, fileFormat, file))

		return outputs

	def _Outputs(self, args: Namespace) -> tuple[tuple[str, Nullable[str], type[OutputFormat], OutputFormat], ...]:
		"""
		Return the output options this command offers, as ``(option, value, formats, default format)``.

		:param args: The parsed command line.
		:returns:    One entry per output option, whether or not it was given.
		"""
		return (
			("--trace-file", args.traceFile, TraceFormat, DEFAULT_TRACE_FORMAT),
		)

	def _WriteOutputs(self, outputs: list[tuple[str, OutputFormat, Path]], trace: Trace) -> None:
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
