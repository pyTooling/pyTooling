# ==================================================================================================================== #
#               _____           _ _               ____  _                                   ____             _   _     #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \(_) __ _  __ _ _ __ __ _ _ __ ___   / ___| __ _ _ __ | |_| |_   #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | |/ _` |/ _` | '__/ _` | '_ ` _ \ | |  _ / _` | '_ \| __| __|  #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | | (_| | (_| | | | (_| | | | | | || |_| | (_| | | | | |_| |_   #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/|_|\__,_|\__, |_|  \__,_|_| |_| |_(_)____|\__,_|_| |_|\__|\__|  #
#   |_|    |___/                          |___/                 |___/                                                  #
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
Unit tests for :mod:`pyTooling.Diagram.Gantt`: bars, rows, a diagram and the offsets they answer.
"""
from datetime                import datetime, timedelta, timezone

from pyTooling.Diagram        import DiagramError
from pyTooling.Diagram.Gantt  import Bar, Diagram, Row
from pyTooling.Testing        import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


_ORIGIN = datetime(2026, 9, 15, 6, 35, 0, tzinfo=timezone.utc)
"""The origin of the example diagram."""


def _at(seconds: int) -> datetime:
	"""
	Return the time the given number of seconds after the example diagram's origin.

	:param seconds: Seconds after the origin.
	:returns:       The time.
	"""
	return _ORIGIN + timedelta(seconds=seconds)


def _diagram() -> Diagram:
	"""
	Build an example diagram: one row of two bars, and one row of a single bar.

	:returns: The diagram.
	"""
	diagram = Diagram("Pipeline", _ORIGIN)

	build = Row("Build", parent=diagram)
	Bar(_at(10), _at(30), parent=build)
	Bar(_at(40), _at(90), parent=build)

	tests = Row("Tests", parent=diagram)
	Bar(_at(50), _at(100), parent=tests)

	return diagram


class Instantiation(Testcase):
	def test_Diagram(self) -> None:
		diagram = Diagram("Pipeline", _ORIGIN)

		self.assertEqual("Pipeline", diagram.Title)
		self.assertEqual(_ORIGIN, diagram.Origin)
		self.assertEqual(0, diagram.RowCount)
		self.assertEqual(0, len(diagram))
		self.assertTupleEqual((), diagram.Rows)

	def test_RowIsAppendedToItsDiagram(self) -> None:
		diagram = Diagram("Pipeline", _ORIGIN)
		row = Row("Build", parent=diagram)

		self.assertEqual("Build", row.Name)
		self.assertEqual(1, diagram.RowCount)
		self.assertTupleEqual((row,), diagram.Rows)
		self.assertIs(diagram, row.Parent)
		self.assertIs(diagram, row.Diagram)
		self.assertEqual(0, row.BarCount)
		self.assertEqual(0, len(row))

	def test_BarIsAppendedToItsRow(self) -> None:
		diagram = Diagram("Pipeline", _ORIGIN)
		row = Row("Build", parent=diagram)
		bar = Bar(_at(10), _at(30), parent=row)

		self.assertTupleEqual((bar,), row.Bars)
		self.assertEqual(1, row.BarCount)
		self.assertEqual(1, len(row))
		self.assertIs(row, bar.Parent)
		self.assertIs(diagram, bar.Diagram)

	def test_AnEmptyBarIsAllowed(self) -> None:
		"""A timespan too short for the reporting service's resolution is a bar of no length, not an error."""
		row = Row("Build", parent=Diagram("Pipeline", _ORIGIN))
		bar = Bar(_at(10), _at(10), parent=row)

		self.assertEqual(timedelta(), bar.Duration)
		self.assertEqual(0.0, bar.DurationInSeconds)


class Iteration(Testcase):
	def test_DiagramYieldsItsRows(self) -> None:
		diagram = _diagram()

		self.assertListEqual(["Build", "Tests"], [row.Name for row in diagram])
		self.assertListEqual(["Build", "Tests"], [row.Name for row in diagram.IterateRows()])
		self.assertEqual(2, len(diagram))

	def test_RowYieldsItsBars(self) -> None:
		row = _diagram().Rows[0]

		self.assertListEqual([_at(10), _at(40)], [bar.Begin for bar in row])
		self.assertListEqual([_at(10), _at(40)], [bar.Begin for bar in row.IterateBars()])
		self.assertEqual(2, row.BarCount)
		self.assertEqual(2, len(row))


class Offsets(Testcase):
	def test_BarTimes(self) -> None:
		bar = _diagram().Rows[0].Bars[1]

		self.assertEqual((_at(40), _at(90)), (bar.Begin, bar.End))
		self.assertEqual(timedelta(seconds=50), bar.Duration)
		self.assertEqual(50.0, bar.DurationInSeconds)

	def test_BarSinceOrigin(self) -> None:
		bar = _diagram().Rows[0].Bars[1]

		self.assertEqual(timedelta(seconds=40), bar.BeginSinceOrigin)
		self.assertEqual(timedelta(seconds=90), bar.EndSinceOrigin)
		self.assertEqual(40.0, bar.BeginSinceOriginInSeconds)
		self.assertEqual(90.0, bar.EndSinceOriginInSeconds)

	def test_BarSinceParent(self) -> None:
		"""A bar is placed against its row, which begins with the row's earliest bar."""
		first, second = _diagram().Rows[0].Bars

		self.assertEqual(timedelta(), first.BeginSinceParent)
		self.assertEqual(timedelta(seconds=20), first.EndSinceParent)
		self.assertEqual(timedelta(seconds=30), second.BeginSinceParent)
		self.assertEqual(timedelta(seconds=80), second.EndSinceParent)

	def test_RowSpansItsBars(self) -> None:
		"""A row begins with its earliest bar and ends with its latest, gaps between them included."""
		row = _diagram().Rows[0]

		self.assertEqual((_at(10), _at(90)), (row.Begin, row.End))
		self.assertEqual(timedelta(seconds=80), row.Duration)
		self.assertEqual(80.0, row.DurationInSeconds)
		self.assertEqual(timedelta(seconds=10), row.BeginSinceOrigin)
		self.assertEqual(timedelta(seconds=90), row.EndSinceOrigin)

	def test_TheOriginPrecedesTheFirstBar(self) -> None:
		"""The origin is stated, not derived, so a diagram may begin before anything is drawn on it."""
		diagram = _diagram()

		self.assertEqual(_ORIGIN, diagram.Origin)
		self.assertLess(diagram.Origin, diagram.Rows[0].Begin)


class EmptyRow(Testcase):
	def test_Begin(self) -> None:
		row = Row("Skipped", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(DiagramError) as context:
			_ = row.Begin

		self.assertEqual("Row 'Skipped' has no bars, so it has no begin.", str(context.exception))

	def test_End(self) -> None:
		row = Row("Skipped", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(DiagramError) as context:
			_ = row.End

		self.assertEqual("Row 'Skipped' has no bars, so it has no end.", str(context.exception))

	def test_Duration(self) -> None:
		row = Row("Skipped", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(DiagramError):
			_ = row.Duration


class ParameterChecks(Testcase):
	def test_DiagramTitleIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Diagram(None, _ORIGIN)

		self.assertEqual("Parameter 'title' is None.", str(context.exception))

	def test_DiagramTitleType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Diagram(5, _ORIGIN)

		self.assertEqual("Parameter 'title' is not of type 'str'.", str(context.exception))

	def test_DiagramOriginIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Diagram("Pipeline", None)

		self.assertEqual("Parameter 'origin' is None.", str(context.exception))

	def test_DiagramOriginType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Diagram("Pipeline", "2026-09-15")

		self.assertEqual("Parameter 'origin' is not of type 'datetime'.", str(context.exception))

	def test_RowNameIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Row(None, parent=Diagram("Pipeline", _ORIGIN))

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

	def test_RowNameType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Row(5, parent=Diagram("Pipeline", _ORIGIN))

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))

	def test_RowParentIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Row("Build", parent=None)

		self.assertEqual("Parameter 'parent' is None.", str(context.exception))

	def test_RowParentType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Row("Build", parent="Pipeline")

		self.assertEqual("Parameter 'parent' is not of type 'Diagram'.", str(context.exception))

	def test_BarBeginIsNone(self) -> None:
		row = Row("Build", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(ValueError) as context:
			_ = Bar(None, _at(30), parent=row)

		self.assertEqual("Parameter 'begin' is None.", str(context.exception))

	def test_BarEndType(self) -> None:
		row = Row("Build", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(TypeError) as context:
			_ = Bar(_at(10), 30, parent=row)

		self.assertEqual("Parameter 'end' is not of type 'datetime'.", str(context.exception))

	def test_BarParentType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Bar(_at(10), _at(30), parent=Diagram("Pipeline", _ORIGIN))

		self.assertEqual("Parameter 'parent' is not of type 'Row'.", str(context.exception))

	def test_BarEndsBeforeItBegins(self) -> None:
		row = Row("Build", parent=Diagram("Pipeline", _ORIGIN))

		with self.assertRaises(ValueError) as context:
			_ = Bar(_at(30), _at(10), parent=row)

		self.assertEqual("A bar's end precedes its begin.", str(context.exception))
