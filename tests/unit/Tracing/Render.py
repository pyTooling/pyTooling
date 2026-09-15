# ==================================================================================================================== #
#             _____           _ _             _____               _                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ __ _  ___(_)_ __   __ _                                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _` |/ __| | '_ \ / _` |                                       #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | | (_| | (__| | | | | (_| |                                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \__,_|\___|_|_| |_|\__, |                                       #
# |_|    |___/                          |___/                             |___/                                        #
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
Unit tests for :mod:`pyTooling.Tracing.Render` and :mod:`pyTooling.Tracing.Render.Matplotlib`.
"""
from datetime                    import datetime, timedelta, timezone
from json                        import loads as json_loads
from pathlib                     import Path
from re                          import search
from tempfile                    import TemporaryDirectory
from typing                      import Optional as Nullable
from unittest                    import skipUnless
from warnings                    import catch_warnings, simplefilter
from xml.etree                   import ElementTree

from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import CI, OTLP, Result, SpanKind
from pyTooling.Tracing.CI.GitHub import GitHub
from pyTooling.Tracing.Render    import GanttLayout, StepExclusion, ciSpanFilter, msys2Environment, runnerCategory
from pyTooling.Testing           import Testcase

try:
	from pyTooling.Tracing.Render.Matplotlib import RenderGantt, WriteGantt
	HAS_MATPLOTLIB = True
except ImportError:  # pragma: no cover
	HAS_MATPLOTLIB = False


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


_BEGIN = datetime(2026, 9, 15, 6, 35, 0, tzinfo=timezone.utc)
"""The time the example pipeline began."""


def _at(seconds: int) -> datetime:
	"""
	Return the time the given number of seconds after the example pipeline began.

	:param seconds: Seconds after the pipeline began.
	:returns:       The time.
	"""
	return _BEGIN + timedelta(seconds=seconds)


def _span(
	name:   str,
	begin:  int,
	end:    Nullable[int],
	parent: Span,
	kind:   str,
	task:   str = "",
	runner: str = "",
	result: str = ""
) -> Span:
	"""
	Create a recorded timespan with CI attributes.

	:param name:   The timespan's name.
	:param begin:  Seconds after the pipeline began, when the timespan began.
	:param end:    Seconds after the pipeline began, when the timespan ended, or ``None`` while running.
	:param parent: The parent timespan.
	:param kind:   The CI span kind.
	:param task:   Optional, the task name.
	:param runner: Optional, the runner label.
	:param result: Optional, the CI result.
	:returns:      The timespan.
	"""
	span = Span(name, _at(begin), None if end is None else _at(end), parent=parent)
	span[CI.Span.Kind] = kind
	if task != "":
		span[OTLP.CICD.Pipeline.Task.Name] = task
	if runner != "":
		span[GitHub.Runner.Labels] = [runner]
	if result != "":
		span[OTLP.CICD.Pipeline.Task.Run.Result] = result
	return span


def _pipeline() -> dict[str, Span]:
	"""
	Build an example pipeline.

	* A finished job with a step and a skipped step.
	* A running called workflow with a running job using MSYS2, a waiting job, and a skipped job.

	:returns: Dictionary of a name to its timespan, including the trace as ``Pipeline``.
	"""
	trace = Trace("Pipeline", _at(0), _at(100))
	trace[CI.Span.Kind] = "pipeline"

	s: dict[str, Span] = {"Pipeline": trace}
	s["Build (queued)"] =   _span("Build (queued)", 1, 4, trace, "queued", "Build", "ubuntu-26.04")
	s["Build"] =            _span("Build", 4, 30, trace, "job", "Build", "ubuntu-26.04", "success")
	s["Compile"] =          _span("Compile", 5, 20, s["Build"], "step", "Compile", result="success")
	s["Upload"] =           _span("Upload", 20, 20, s["Build"], "step", "Upload", result="skip")
	s["Tests"] =            _span("Tests", 10, None, trace, "workflow", "Tests")
	s["Windows (queued)"] = _span("Windows (queued)", 10, 15, s["Tests"], "queued", "Tests / Windows", "windows-2025")
	s["Windows"] =          _span("Windows", 15, None, s["Tests"], "job", "Tests / Windows", "windows-2025")
	s["Setup MSYS2"] =      _span("🟦 Setup MSYS2 for ucrt64", 16, 20, s["Windows"], "step", result="success")
	s["macOS (queued)"] =   _span("macOS (queued)", 12, None, s["Tests"], "queued", "Tests / macOS", "macos-15")
	s["Release"] =          _span("Release", 12, 12, s["Tests"], "job", "Tests / Release", "", "skip")
	return s


class Filter(Testcase):
	def _Names(self, spanFilter) -> list[str]:
		"""
		Lay out the example pipeline with a filter.

		:param spanFilter: The span filter.
		:returns:          The names of the rows.
		"""
		layout = GanttLayout(_pipeline()["Pipeline"], spanFilter=spanFilter, now=_at(50))
		return [row.Name for row in layout.IterateRows()]

	def test_Default(self) -> None:
		self.assertListEqual(["Pipeline", "Build", "Tests", "Windows", "macOS (queued)"], self._Names(ciSpanFilter()))

	def test_ExcludeNothing(self) -> None:
		names = self._Names(ciSpanFilter(excludeSteps=StepExclusion.Nothing, excludeSkippedJobs=False))

		self.assertListEqual(
			[
				"Pipeline", "Build", "Compile", "Upload", "Tests", "Windows", "🟦 Setup MSYS2 for ucrt64", "macOS (queued)",
				"Release"
			],
			names
		)
		self.assertListEqual(names, self._Names(ciSpanFilter(excludeSteps=False, excludeSkippedJobs=False)))

	def test_ExcludeSkippedSteps(self) -> None:
		names = self._Names(ciSpanFilter(excludeSteps=StepExclusion.Skipped))

		self.assertIn("Compile", names)
		self.assertNotIn("Upload", names)
		self.assertNotIn("Release", names)

	def test_ExcludeAllSteps(self) -> None:
		self.assertListEqual(self._Names(ciSpanFilter()), self._Names(ciSpanFilter(excludeSteps=True)))

	def test_HiddenParentHidesSubSpans(self) -> None:
		self.assertListEqual(["Pipeline", "Build", "Compile", "Upload"], self._Names(lambda span: span.Name != "Tests"))

	def test_ExcludeStepsType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ciSpanFilter(excludeSteps="all")

		self.assertEqual(
			"Parameter 'excludeSteps' is neither of type 'bool' nor 'StepExclusion'.", str(context.exception)
		)


class Categories(Testcase):
	def test_Runner(self) -> None:
		spans = _pipeline()

		self.assertEqual("ubuntu-26.04", runnerCategory(spans["Build"]))
		self.assertEqual("ubuntu-26.04", runnerCategory(spans["Compile"]), "A step takes its job's runner.")
		self.assertEqual("", runnerCategory(spans["Tests"]))
		self.assertEqual("", runnerCategory(spans["Pipeline"]))

	def test_MSYS2(self) -> None:
		spans = _pipeline()

		self.assertEqual("UCRT64", msys2Environment(spans["Windows"]))
		self.assertEqual("windows-2025 + UCRT64", runnerCategory(spans["Windows"]))
		self.assertEqual("windows-2025", runnerCategory(spans["Windows (queued)"]), "A waiting timespan has no steps.")

	def test_MSYS2_Native(self) -> None:
		"""A native Windows job skips the MSYS2 setup, or sets up the environment 'native'."""
		trace = Trace("Pipeline", _at(0), _at(10))
		skipped = _span("Windows", 1, 5, trace, "job", "Windows", "windows-2025")
		_span("🟦 Setup MSYS2 for UCRT64", 1, 1, skipped, "step", result="skip")
		native = _span("Windows native", 1, 5, trace, "job", "Windows native", "windows-2025")
		_span("🟦 Setup MSYS2 for native", 1, 2, native, "step", result="success")

		self.assertIsNone(msys2Environment(skipped))
		self.assertIsNone(msys2Environment(native))
		self.assertEqual("windows-2025", runnerCategory(native))


class Layout(Testcase):
	def _Layout(self) -> GanttLayout:
		"""
		Lay out the example pipeline without steps and skipped jobs.

		:returns: The layout.
		"""
		return GanttLayout(_pipeline()["Pipeline"], spanFilter=ciSpanFilter(), now=_at(50))

	def test_Rows(self) -> None:
		layout = self._Layout()

		self.assertListEqual(
			[
				("Pipeline", 0, "pipeline"), ("Build", 1, "job"), ("Tests", 1, "workflow"), ("Windows", 2, "job"),
				("macOS (queued)", 2, "queued")
			],
			[(row.Name, row.Depth, row.Kind) for row in layout.IterateRows()]
		)
		self.assertEqual(5, layout.RowCount)

	def test_ParentSpanID(self) -> None:
		rows = {row.Name: row for row in self._Layout().IterateRows()}

		self.assertIsNone(rows["Pipeline"].ParentSpanID)
		self.assertEqual(rows["Tests"].SpanID, rows["Windows"].ParentSpanID)

	def test_QueuedBarOnJobRow(self) -> None:
		bars = {row.Name: row for row in self._Layout().IterateRows()}["Build"].Bars

		self.assertListEqual(
			[(1.0, 4.0, True), (4.0, 30.0, False)], [(bar.Begin, bar.End, bar.IsQueued) for bar in bars]
		)
		self.assertEqual(26.0, bars[1].Duration)
		self.assertFalse(bars[1].IsRunning)

	def test_WaitingJob(self) -> None:
		"""A job that didn't start yet only has its waiting timespan, which gets a row of its own."""
		bars = {row.Name: row for row in self._Layout().IterateRows()}["macOS (queued)"].Bars

		self.assertEqual(1, len(bars))
		self.assertTrue(bars[0].IsQueued)
		self.assertTrue(bars[0].IsRunning)
		self.assertEqual(50.0, bars[0].End)

	def test_Running(self) -> None:
		rows = {row.Name: row for row in self._Layout().IterateRows()}
		bar = rows["Windows"].Bars[1]

		self.assertEqual((15.0, 50.0, True), (bar.Begin, bar.End, bar.IsRunning))
		self.assertTrue(rows["Tests"].Bars[0].IsRunning)

	def test_Duration(self) -> None:
		self.assertEqual(100.0, self._Layout().Duration)
		self.assertEqual(120.0, GanttLayout(_pipeline()["Pipeline"], now=_at(120)).Duration)

	def test_Times(self) -> None:
		layout = self._Layout()

		self.assertEqual(_at(0), layout.BeginTime)
		self.assertEqual(_at(100), layout.EndTime)
		self.assertFalse(layout.IsRunning)
		self.assertEqual(100.0, layout.WallTime)

	def test_UnmatchedQueued(self) -> None:
		"""A waiting timespan followed by another job stays on a row of its own."""
		trace = Trace("Pipeline", _at(0), _at(10))
		_span("A (queued)", 1, None, trace, "queued", "A")
		_span("B", 2, 5, trace, "job", "B")

		names = [row.Name for row in GanttLayout(trace, now=_at(6)).IterateRows()]
		self.assertListEqual(["Pipeline", "A (queued)", "B"], names)

	def test_SpanWithoutTimes(self) -> None:
		trace = Trace("Pipeline", _at(0), _at(10))
		Span("Skipped", parent=trace)

		self.assertEqual(0, len(list(GanttLayout(trace).IterateRows())[1].Bars))

	def test_NoBeginTime(self) -> None:
		with self.assertRaises(TracingError) as context:
			_ = GanttLayout(Trace("Pipeline"))

		self.assertEqual("Trace 'Pipeline' has no begin time, so it can't be laid out.", str(context.exception))

	def test_TraceType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = GanttLayout(Span("span", _at(0), _at(1)))

		self.assertEqual("Parameter 'trace' is not of type 'Trace'.", str(context.exception))


class Statistics(Testcase):
	def test_PerCategory(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], spanFilter=ciSpanFilter(), now=_at(50))
		statistics = {entry.Category: entry for entry in layout.IterateStatistics()}
		ubuntu = statistics["ubuntu-26.04"]
		msys2 = statistics["windows-2025 + UCRT64"]

		self.assertEqual(("ubuntu-26.04", "windows-2025 + UCRT64", "macos-15"), layout.Categories)
		self.assertEqual(
			{"ubuntu-26.04", "windows-2025 + UCRT64"}, set(statistics), "A waiting or skipped job isn't counted."
		)
		self.assertEqual((1, (3.0,), (26.0,)), (ubuntu.JobCount, ubuntu.WaitTimes, ubuntu.RunTimes))
		self.assertEqual((5.0, 35.0), (msys2.MaximumWaitTime, msys2.MaximumRunTime))

	def test_Totals(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], now=_at(50))

		self.assertEqual(2, layout.JobCount)
		self.assertEqual(61.0, layout.RunnerTime)

	def test_IndependentOfFilter(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], spanFilter=lambda span: span.Name != "Tests", now=_at(50))

		self.assertEqual(2, layout.JobCount)

	def test_MinimumAverageMaximum(self) -> None:
		trace = Trace("Pipeline", _at(0), _at(100))
		for position, (started, completed) in enumerate(((2, 12), (6, 36), (10, 30))):
			_span(f"Job {position} (queued)", 0, started, trace, "queued", f"Job {position}", "ubuntu-26.04")
			_span(f"Job {position}", started, completed, trace, "job", f"Job {position}", "ubuntu-26.04", "success")

		entry = next(GanttLayout(trace).IterateStatistics())

		self.assertEqual((2.0, 6.0, 10.0), (entry.MinimumWaitTime, entry.AverageWaitTime, entry.MaximumWaitTime))
		self.assertEqual((10.0, 20.0, 30.0), (entry.MinimumRunTime, entry.AverageRunTime, entry.MaximumRunTime))
		self.assertEqual(60.0, entry.TotalRunTime)


@skipUnless(HAS_MATPLOTLIB, "Needs matplotlib, installed by the extra 'pyTooling[diagram]'.")
class Matplotlib(Testcase):
	def test_Figure(self) -> None:
		figure = RenderGantt(GanttLayout(_pipeline()["Pipeline"], spanFilter=ciSpanFilter(), now=_at(50)))
		axes = figure.get_axes()[0]
		legend = axes.get_legend()
		title = legend.get_title().get_text()
		texts = [text.get_text() for text in legend.get_texts()]

		self.assertEqual(1, len(figure.get_axes()))
		self.assertEqual(5, len(axes.get_yticklabels()))
		self.assertEqual("Pipeline (1:40)", figure.get_suptitle())

		self.assertIn("started     2026-09-15 06:35:00 UTC", title)
		self.assertIn("finished    2026-09-15 06:36:40 UTC", title)
		self.assertIn("2 jobs", title)

		self.assertTrue(texts[0].startswith("ubuntu-26.04"))
		self.assertIn("0:03 / 0:03 / 0:03", texts[0])
		self.assertIn("waiting for a runner", texts)
		self.assertIn("pipeline, called workflow", texts)

	def test_SVG(self) -> None:
		spans = _pipeline()
		with TemporaryDirectory() as directory:
			file = Path(directory) / "report" / "Pipeline.svg"
			WriteGantt(spans["Pipeline"], file, spanFilter=ciSpanFilter(), now=_at(50))
			content = file.read_text(encoding="utf-8")

		self.assertIn(f'id="span-{spans["Build"].SpanID}"', content)
		self.assertIn(f'id="span-{spans["Build"].SpanID}-queued"', content)
		self.assertIn(f'id="span-{spans["Tests"].SpanID}"', content, "A called workflow is a line.")
		self.assertIn(f'id="span-{spans["Tests"].SpanID}-ends"', content)
		self.assertNotIn(f'id="span-{spans["Compile"].SpanID}"', content, "The step was filtered.")

	def test_PNG(self) -> None:
		with TemporaryDirectory() as directory:
			file = Path(directory) / "Pipeline.png"
			WriteGantt(_pipeline()["Pipeline"], file, now=_at(50), dpi=50)

			self.assertEqual(b"\x89PNG", file.read_bytes()[:4])

	def test_Emoji(self) -> None:
		"""A character no installed font can draw is left out of the label, instead of an empty box and a warning."""
		trace = Trace("🔁 Pipeline", _at(0), _at(10))
		Span("🐧 Unit Tests - Python 3.14", _at(1), _at(5), parent=trace)

		with catch_warnings(record=True) as warnings:
			simplefilter("always")
			figure = RenderGantt(GanttLayout(trace), fontFamilies=("DejaVu Sans",))
			figure.canvas.draw()

		self.assertEqual("Unit Tests - Python 3.14", figure.get_axes()[0].get_yticklabels()[1].get_text().strip())
		self.assertEqual("Pipeline (0:10)", figure.get_suptitle())
		self.assertListEqual([], [str(warning.message) for warning in warnings if "Glyph" in str(warning.message)])

	def test_UnsupportedFormat(self) -> None:
		with self.assertRaises(ValueError) as context:
			WriteGantt(_pipeline()["Pipeline"], Path("Pipeline.gif"))

		self.assertEqual("File 'Pipeline.gif' has an unsupported format.", str(context.exception))

	def test_FileType(self) -> None:
		with self.assertRaises(TypeError):
			WriteGantt(_pipeline()["Pipeline"], "Pipeline.svg")

	def test_Width(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RenderGantt(GanttLayout(_pipeline()["Pipeline"], now=_at(50)), width=0)

		self.assertEqual("Parameter 'width' isn't positive.", str(context.exception))

	def test_LabelIdentifiers(self) -> None:
		spans = _pipeline()
		with TemporaryDirectory() as directory:
			file = Path(directory) / "Pipeline.svg"
			WriteGantt(spans["Pipeline"], file, spanFilter=ciSpanFilter(), now=_at(50))
			content = file.read_text(encoding="utf-8")

		for name in ("Pipeline", "Build", "Tests", "Windows"):
			with self.subTest(row=name):
				self.assertIn(f'id="label-{spans[name].SpanID}"', content)
		self.assertNotIn("<script", content, "Only a collapsible file carries the script.")

	def test_CollapsibleSVG(self) -> None:
		spans = _pipeline()
		with TemporaryDirectory() as directory:
			file = Path(directory) / "Pipeline.svg"
			spanFilter = ciSpanFilter(excludeSteps=StepExclusion.Nothing)
			WriteGantt(spans["Pipeline"], file, spanFilter=spanFilter, now=_at(50), collapsible=True)
			content = file.read_text(encoding="utf-8")

		ElementTree.fromstring(content)
		data = json_loads(content.split("const data = ", 1)[1].split(";\n", 1)[0])
		rows = {row["id"]: row for row in data["rows"]}
		build = spans["Build"].SpanID
		compileStep = spans["Compile"].SpanID

		self.assertIn('<script type="text/ecmascript">', content)
		self.assertTrue(rows[build]["collapsed"], "A job starts collapsed.")
		self.assertFalse(rows[spans["Tests"].SpanID]["collapsed"], "A called workflow starts expanded.")
		self.assertEqual(build, rows[compileStep]["parent"])
		self.assertIsNone(rows[spans["Pipeline"].SpanID]["parent"])

		def barTop(spanID: str) -> float:
			"""
			Nested function reading the top edge of a timespan's bar from the SVG file.

			:param spanID: The timespan's identifier.
			:returns:      The top edge in SVG coordinates.
			"""
			return float(search(rf'<g id="span-{spanID}">\s*<path d="M [\d.]+ ([\d.]+)', content).group(1))

		self.assertAlmostEqual(barTop(compileStep) - barTop(build), data["pitch"], places=3)

	def test_CollapsibleNeedsSVG(self) -> None:
		with self.assertRaises(ValueError) as context:
			WriteGantt(_pipeline()["Pipeline"], Path("Pipeline.png"), collapsible=True)

		self.assertEqual("File 'Pipeline.png' can't be collapsible.", str(context.exception))
