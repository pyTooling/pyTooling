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
from pathlib                     import Path
from tempfile                    import TemporaryDirectory
from unittest                    import skipUnless
from warnings                    import catch_warnings, simplefilter

from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import SPAN_KIND, TASK_NAME
from pyTooling.Tracing.CI.GitHub import RUNNER_LABELS
from pyTooling.Tracing.Render    import GanttLayout, excludeSteps, runnerCategory
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


def _span(name: str, begin: int, end: int | None, parent: Span, kind: str, task: str = "", runner: str = "") -> Span:
	"""
	Create a recorded timespan with CI attributes.

	:param name:   The timespan's name.
	:param begin:  Seconds after the pipeline began, when the timespan began.
	:param end:    Seconds after the pipeline began, when the timespan ended, or ``None`` while running.
	:param parent: The parent timespan.
	:param kind:   The CI span kind.
	:param task:   Optional, the task name.
	:param runner: Optional, the runner label.
	:returns:      The timespan.
	"""
	span = Span(name, _at(begin), None if end is None else _at(end), parent=parent)
	span[SPAN_KIND] = kind
	if task != "":
		span[TASK_NAME] = task
	if runner != "":
		span[RUNNER_LABELS] = [runner]
	return span


def _pipeline() -> dict[str, Span]:
	"""
	Build an example pipeline: a finished job with a step, and a running called workflow with a running and a waiting job.

	:returns: Dictionary of a name to its timespan, including the trace as ``Pipeline``.
	"""
	trace = Trace("Pipeline", _at(0), _at(100))
	trace[SPAN_KIND] = "pipeline"

	spans: dict[str, Span] = {"Pipeline": trace}
	spans["Build (queued)"] =   _span("Build (queued)", 1, 4, trace, "queued", "Build", "ubuntu-26.04")
	spans["Build"] =            _span("Build", 4, 30, trace, "job", "Build", "ubuntu-26.04")
	spans["Compile"] =          _span("Compile", 5, 20, spans["Build"], "step", "Compile")
	spans["Tests"] =            _span("Tests", 10, None, trace, "workflow", "Tests")
	spans["Windows (queued)"] = _span("Windows (queued)", 10, 15, spans["Tests"], "queued", "Tests / Windows", "windows-2025")
	spans["Windows"] =          _span("Windows", 15, None, spans["Tests"], "job", "Tests / Windows", "windows-2025")
	spans["macOS (queued)"] =   _span("macOS (queued)", 12, None, spans["Tests"], "queued", "Tests / macOS", "macos-15")
	return spans


class Layout(Testcase):
	def test_Rows(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], now=_at(50))

		self.assertListEqual(
			[("Pipeline", 0), ("Build", 1), ("Compile", 2), ("Tests", 1), ("Windows", 2), ("macOS (queued)", 2)],
			[(row.Name, row.Depth) for row in layout.IterateRows()]
		)
		self.assertEqual(6, layout.RowCount)

	def test_QueuedBarOnJobRow(self) -> None:
		rows = {row.Name: row for row in GanttLayout(_pipeline()["Pipeline"], now=_at(50)).IterateRows()}
		bars = rows["Build"].Bars

		self.assertListEqual([(1.0, 4.0, True), (4.0, 30.0, False)], [(bar.Begin, bar.End, bar.IsQueued) for bar in bars])
		self.assertEqual(26.0, bars[1].Duration)
		self.assertFalse(bars[1].IsRunning)

	def test_WaitingJob(self) -> None:
		"""A job that didn't start yet only has its waiting timespan, which gets a row of its own."""
		rows = {row.Name: row for row in GanttLayout(_pipeline()["Pipeline"], now=_at(50)).IterateRows()}
		bars = rows["macOS (queued)"].Bars

		self.assertEqual(1, len(bars))
		self.assertTrue(bars[0].IsQueued)
		self.assertTrue(bars[0].IsRunning)
		self.assertEqual(50.0, bars[0].End)

	def test_Running(self) -> None:
		rows = {row.Name: row for row in GanttLayout(_pipeline()["Pipeline"], now=_at(50)).IterateRows()}

		self.assertEqual((15.0, 50.0, True), (rows["Windows"].Bars[1].Begin, rows["Windows"].Bars[1].End, rows["Windows"].Bars[1].IsRunning))
		self.assertTrue(rows["Tests"].Bars[0].IsRunning)

	def test_Duration(self) -> None:
		self.assertEqual(100.0, GanttLayout(_pipeline()["Pipeline"], now=_at(50)).Duration)
		self.assertEqual(120.0, GanttLayout(_pipeline()["Pipeline"], now=_at(120)).Duration)

	def test_Categories(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], now=_at(50))
		rows = {row.Name: row for row in layout.IterateRows()}

		self.assertEqual(("ubuntu-26.04", "windows-2025", "macos-15"), layout.Categories)
		self.assertEqual("ubuntu-26.04", rows["Compile"].Category, "A step inherits its job's runner.")
		self.assertEqual("", rows["Tests"].Category)
		self.assertEqual("", runnerCategory(_pipeline()["Pipeline"]))

	def test_ExcludeSteps(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], spanFilter=excludeSteps, now=_at(50))

		self.assertNotIn("Compile", [row.Name for row in layout.IterateRows()])

	def test_FilterHidesSubSpans(self) -> None:
		layout = GanttLayout(_pipeline()["Pipeline"], spanFilter=lambda span: span.Name != "Tests", now=_at(50))

		self.assertListEqual(["Pipeline", "Build", "Compile"], [row.Name for row in layout.IterateRows()])

	def test_UnmatchedQueued(self) -> None:
		"""A waiting timespan followed by another job stays on a row of its own."""
		trace = Trace("Pipeline", _at(0), _at(10))
		_span("A (queued)", 1, None, trace, "queued", "A")
		_span("B", 2, 5, trace, "job", "B")

		self.assertListEqual(["Pipeline", "A (queued)", "B"], [row.Name for row in GanttLayout(trace, now=_at(6)).IterateRows()])

	def test_SpanWithoutTimes(self) -> None:
		trace = Trace("Pipeline", _at(0), _at(10))
		Span("Skipped", parent=trace)

		rows = list(GanttLayout(trace).IterateRows())

		self.assertEqual(0, len(rows[1].Bars))

	def test_NoBeginTime(self) -> None:
		with self.assertRaises(TracingError) as context:
			_ = GanttLayout(Trace("Pipeline"))

		self.assertEqual("Trace 'Pipeline' has no begin time, so it can't be laid out.", str(context.exception))

	def test_TraceType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = GanttLayout(Span("span", _at(0), _at(1)))

		self.assertEqual("Parameter 'trace' is not of type 'Trace'.", str(context.exception))


@skipUnless(HAS_MATPLOTLIB, "Needs matplotlib, installed by the extra 'pyTooling[matplotlib]'.")
class Matplotlib(Testcase):
	def test_Figure(self) -> None:
		figure = RenderGantt(GanttLayout(_pipeline()["Pipeline"], now=_at(50)))
		axes = figure.get_axes()[0]

		self.assertEqual(1, len(figure.get_axes()))
		self.assertEqual(6, len(axes.get_yticklabels()))
		self.assertEqual("Pipeline (1:40)", figure.get_suptitle())
		self.assertEqual(
			["ubuntu-26.04", "windows-2025", "macos-15", "waiting for a runner"],
			[text.get_text() for text in figure.legends[0].get_texts()]
		)

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

	def test_SVG(self) -> None:
		spans = _pipeline()
		with TemporaryDirectory() as directory:
			file = Path(directory) / "report" / "Pipeline.svg"
			WriteGantt(spans["Pipeline"], file, spanFilter=excludeSteps, now=_at(50))
			content = file.read_text(encoding="utf-8")

		self.assertIn(f'id="span-{spans["Build"].SpanID}"', content)
		self.assertIn(f'id="span-{spans["Build"].SpanID}-queued"', content)
		self.assertNotIn(f'id="span-{spans["Compile"].SpanID}"', content, "The step was filtered.")

	def test_PNG(self) -> None:
		with TemporaryDirectory() as directory:
			file = Path(directory) / "Pipeline.png"
			WriteGantt(_pipeline()["Pipeline"], file, now=_at(50), dpi=50)

			self.assertEqual(b"\x89PNG", file.read_bytes()[:4])

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
