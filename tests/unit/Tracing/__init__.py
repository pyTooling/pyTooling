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
Unit tests for :mod:`pyTooling.Tracing`: traces, spans and the attributes attached to them.
"""
from datetime          import datetime, timedelta, timezone
from time              import sleep

from pyTooling.Tracing import TracingError, Trace, Span, Event
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Trace(self) -> None:
		t = Trace("trace")

		self.assertIsNone(t.Parent)
		self.assertEqual("trace", t.Name)
		self.assertEqual("trace", str(t))
		self.assertFalse(t.HasSubSpans)
		self.assertEqual(0, t.SubSpanCount)
		self.assertEqual(0, len([s for s in t.IterateSubSpans()]))

		self.assertFalse(t.HasEvents)
		self.assertEqual(0, t.EventCount)
		self.assertEqual(0, len([e for e in t.IterateEvents()]))

		self.assertEqual(0, len(t))
		self.assertEqual(0, len([a for a in t]))

		with self.assertRaises(TracingError) as ex:
			_ = t.Duration

	def test_Span(self) -> None:
		s = Span("span")

		self.assertIsNone(s.Parent)
		self.assertEqual("span", s.Name)
		self.assertEqual("span", str(s))
		self.assertFalse(s.HasSubSpans)
		self.assertEqual(0, s.SubSpanCount)
		self.assertEqual(0, len([ss for ss in s.IterateSubSpans()]))

		self.assertFalse(s.HasEvents)
		self.assertEqual(0, s.EventCount)
		self.assertEqual(0, len([e for e in s.IterateEvents()]))

		self.assertEqual(0, len(s))
		self.assertEqual(0, len([a for a in s]))

	def test_SubSpan(self) -> None:
		s = Span("span")

		ss = Span("subspan", parent=s)

		self.assertIsNone(s.Parent)
		self.assertTrue(s.HasSubSpans)
		self.assertEqual(1, s.SubSpanCount)
		self.assertListEqual([ss], [ss for ss in s.IterateSubSpans()])

		self.assertIs(s, ss.Parent)
		self.assertFalse(ss.HasSubSpans)
		self.assertEqual(0, ss.SubSpanCount)

	def test_Event(self) -> None:
		e = Event("event")

		self.assertIsNone(e.Parent)
		self.assertEqual("event", e.Name)
		self.assertEqual("event", str(e))
		self.assertEqual(0, len(e))
		self.assertEqual(0, len([a for a in e]))


class RecordedTimes(Testcase):
	"""Timespans measured elsewhere - by a CI service, or read from a log - are constructed with their times."""

	_begin = datetime(2026, 9, 15, 6, 35, 24, tzinfo=timezone.utc)

	def test_Span(self) -> None:
		s = Span("span", beginTime=self._begin, endTime=self._begin + timedelta(seconds=1, microseconds=500_000))

		self.assertEqual(self._begin, s.StartTime)
		self.assertEqual(self._begin + timedelta(seconds=1.5), s.StopTime)
		self.assertEqual(1.5, s.Duration)

	def test_Span_Microsecond(self) -> None:
		s = Span("span", beginTime=self._begin, endTime=self._begin + timedelta(microseconds=1))

		self.assertEqual(1e-6, s.Duration)

	def test_Span_Days(self) -> None:
		s = Span("span", beginTime=self._begin, endTime=self._begin + timedelta(days=2, seconds=3))

		self.assertEqual(2 * 86_400 + 3, s.Duration)

	def test_Span_Running(self) -> None:
		"""A recorded timespan without an end is still running, so its duration grows until now."""
		begin = datetime.now(timezone.utc) - timedelta(seconds=2)
		s = Span("span", beginTime=begin)

		self.assertIsNone(s.StopTime)
		self.assertGreaterEqual(s.Duration, 2.0)

	def test_Span_Naive(self) -> None:
		begin = datetime(2026, 9, 15, 8, 35, 24)
		s = Span("span", beginTime=begin, endTime=begin + timedelta(seconds=3))

		self.assertEqual(3.0, s.Duration)

	def test_Trace(self) -> None:
		begin = self._begin

		t =    Trace("pipeline", beginTime=begin, endTime=begin + timedelta(minutes=9))
		job =  Span("job", parent=t, beginTime=begin + timedelta(seconds=11), endTime=begin + timedelta(minutes=2))
		step = Span("step", parent=job, beginTime=begin + timedelta(seconds=12), endTime=begin + timedelta(seconds=20))

		self.assertEqual(540.0, t.Duration)
		self.assertIs(t, job.Trace)
		self.assertIs(t, step.Trace)
		self.assertListEqual([job], [s for s in t.IterateSubSpans()])
		self.assertListEqual([step], [s for s in job.IterateSubSpans()])
		self.assertEqual(8.0, step.Duration)

	def test_Trace_Format(self) -> None:
		t = Trace("pipeline", beginTime=self._begin, endTime=self._begin + timedelta(seconds=2))
		Span("job", parent=t, beginTime=self._begin, endTime=self._begin + timedelta(milliseconds=250))

		lines = t.Format()

		self.assertEqual(3, len(lines), "A headline, the trace and its timespan.")
		self.assertIn("2000.000 ms", lines[0])
		self.assertIn("2000.000 ms", lines[1])
		self.assertIn("250.000 ms", lines[2])

	def test_Trace_OTLPDuration(self) -> None:
		"""The exported end is the start plus the exact recorded duration, not a duration rounded through seconds."""
		t = Trace("pipeline", beginTime=self._begin, endTime=self._begin + timedelta(seconds=7, microseconds=1))
		Span("job", parent=t, beginTime=self._begin, endTime=self._begin + timedelta(microseconds=123_457))

		spans = {s["name"]: s for s in t.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]}

		for name, expected in (("pipeline", 7_000_001_000), ("job", 123_457_000)):
			with self.subTest(span=name):
				span = spans[name]
				self.assertEqual(expected, int(span["endTimeUnixNano"]) - int(span["startTimeUnixNano"]))
				self.assertAlmostEqual(
					int(self._begin.timestamp()) * 1_000_000_000, int(span["startTimeUnixNano"]), delta=1_000
				)

	def test_EndTimeWithoutBeginTime(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", endTime=self._begin)

		self.assertEqual("Parameter 'endTime' is given without parameter 'beginTime'.", str(context.exception))

	def test_EndTimeBeforeBeginTime(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", beginTime=self._begin, endTime=self._begin - timedelta(microseconds=1))

		self.assertEqual("Parameter 'endTime' is before parameter 'beginTime'.", str(context.exception))

	def test_BeginTimeType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Span("span", beginTime="2026-09-15T06:35:24Z")

		self.assertEqual("Parameter 'beginTime' is not of type 'datetime'.", str(context.exception))

	def test_EndTimeType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Trace("trace", beginTime=self._begin, endTime=1789454124)

		self.assertEqual("Parameter 'endTime' is not of type 'datetime'.", str(context.exception))

	def test_MixedTimeZones(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", beginTime=self._begin, endTime=datetime(2026, 9, 15, 8, 36, 0))

		self.assertEqual(
			"Parameters 'beginTime' and 'endTime' mix a time zone aware and a naive timestamp.",
			str(context.exception)
		)

	def test_NameType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Span(42)

		self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_EnterRecordedSpan(self) -> None:
		with Trace("trace"):
			s = Span("span", beginTime=self._begin)
			with self.assertRaises(TracingError) as context:
				with s:
					pass

		self.assertEqual("Timespan 'span' has recorded times and can't be entered.", str(context.exception))

	def test_EnterRecordedTrace(self) -> None:
		with self.assertRaises(TracingError) as context:
			with Trace("trace", beginTime=self._begin, endTime=self._begin):
				pass

		self.assertEqual("Trace 'trace' has recorded times and can't be entered.", str(context.exception))

	def test_EnterSpanTwice(self) -> None:
		"""A span timed by a 'with'-statement can be entered again, as before."""
		with Trace("trace"):
			s = Span("span")
			with s:
				pass
			with s:
				pass

		self.assertIsNotNone(s.StopTime)


class Context(Testcase):
	def test_Trace(self) -> None:
		print()
		self.assertIsNone(Trace.CurrentTrace())
		self.assertIsNone(Trace.CurrentSpan())

		with Trace("trace") as t:
			self.assertIs(Trace.CurrentTrace(), t)
			self.assertIs(Trace.CurrentSpan(), t)

			sleep(0.001)

		self.assertIsNone(Trace.CurrentTrace())
		self.assertIsNone(Trace.CurrentSpan())

		self.assertIsNone(t.Parent)
		self.assertFalse(t.HasSubSpans)
		self.assertEqual(0, t.SubSpanCount)
		self.assertEqual(0, len([s for s in t.IterateSubSpans()]))

		self.assertEqual(0, t.EventCount)
		self.assertEqual(0, len([e for e in t.IterateEvents()]))

		self.assertEqual(0, len(t))
		self.assertEqual(0, len([a for a in t]))

		print(f"Duration: {t.Duration*1e3:.3f} ms")
		for line in t.Format():
			print(line)

	def test_Span(self) -> None:
		print()
		self.assertIsNone(Trace.CurrentTrace())

		with Trace("trace") as t:
			sleep(0.001)

			with Span("span") as s:
				sleep(0.001)

			sleep(0.001)

		self.assertIsNone(t.Parent)
		self.assertTrue(t.HasSubSpans)
		self.assertEqual(1, t.SubSpanCount)
		self.assertEqual(1, len([s for s in t.IterateSubSpans()]))

		self.assertEqual(0, t.EventCount)
		self.assertEqual(0, len([e for e in t.IterateEvents()]))

		self.assertEqual(0, len(t))
		self.assertEqual(0, len([a for a in t]))

		self.assertIs(t, s.Parent)
		self.assertFalse(s.HasSubSpans)
		self.assertEqual(0, s.SubSpanCount)

		for line in t.Format():
			print(line)

	def test_Event(self) -> None:
		print()
		self.assertIsNone(Trace.CurrentTrace())

		with Trace("trace") as t:
			sleep(0.001)

			with Span("span") as s:
				sleep(0.001)

				e = Event("event", parent=s)

			sleep(0.001)

		self.assertIsNone(t.Parent)
		self.assertTrue(t.HasSubSpans)
		self.assertEqual(1, t.SubSpanCount)
		self.assertEqual(1, len([s for s in t.IterateSubSpans()]))

		self.assertEqual(0, t.EventCount)
		self.assertEqual(0, len([e for e in t.IterateEvents()]))

		self.assertEqual(0, len(t))
		self.assertEqual(0, len([a for a in t]))

		self.assertIs(t, s.Parent)
		self.assertFalse(s.HasSubSpans)
		self.assertEqual(0, s.SubSpanCount)

		for line in t.Format():
			print(line)

	def test_Spans(self) -> None:
		print()
		self.assertIsNone(Trace.CurrentTrace())

		with Trace("trace") as t:
			sleep(0.001)

			with Span("span 1") as s:
				sleep(0.001)

				with Span("span 1.1") as s:
					sleep(0.001)

					with Span("span 1.1.1") as s:
						sleep(0.001)

				with Span("span 1.2") as s:
					sleep(0.001)

				with Span("span 1.3") as s:
					sleep(0.001)

					with Span("span 1.3.1") as s:
						sleep(0.001)

				with Span("span 1.4") as s:
					sleep(0.001)

			with Span("span 2") as s:
				sleep(0.001)

			with Span("span 3") as s:
				sleep(0.001)

				with Span("span 3.1") as s:
					sleep(0.001)

					with Span("span 3.1.1") as s:
						sleep(0.001)

					with Span("span 3.1.2") as s:
						sleep(0.001)

			with Span("span 4") as s:
				sleep(0.001)

			sleep(0.001)

		self.assertEqual(4, t.SubSpanCount)
		self.assertEqual(4, len([s for s in t.IterateSubSpans()]))

		for line in t.Format():
			print(line)


class Attributes(Testcase):
	def test_Trace(self) -> None:
		t = Trace("trace")

		self.assertEqual(0, len(t))
		self.assertEqual(0, len([a for a in t]))

		t["id1"] = "value"

		self.assertEqual(1, len(t))
		self.assertEqual(1, len([a for a in t]))
		self.assertIn("id1", t)

		self.assertEqual("value", t["id1"])

		t["id1"] = "value1"

		self.assertEqual(1, len(t))
		self.assertListEqual([("id1", "value1")], [a for a in t])

		t["id2"] = "value2"

		self.assertEqual(2, len(t))
		self.assertIn("id2", t)
		self.assertListEqual([("id1", "value1"), ("id2", "value2")], [a for a in t])

		del t["id1"]

		self.assertEqual(1, len(t))
		self.assertListEqual([("id2", "value2")], [a for a in t])
		self.assertIn("id2", t)

	def test_Span(self) -> None:
		s = Span("span")

		self.assertEqual(0, len(s))
		self.assertEqual(0, len([a for a in s]))

		s["id1"] = "value"

		self.assertEqual(1, len(s))
		self.assertEqual(1, len([a for a in s]))
		self.assertIn("id1", s)

		self.assertEqual("value", s["id1"])

		s["id1"] = "value1"

		self.assertEqual(1, len(s))
		self.assertListEqual([("id1", "value1")], [a for a in s])

		s["id2"] = "value2"

		self.assertEqual(2, len(s))
		self.assertIn("id2", s)
		self.assertListEqual([("id1", "value1"), ("id2", "value2")], [a for a in s])

		del s["id1"]

		self.assertEqual(1, len(s))
		self.assertListEqual([("id2", "value2")], [a for a in s])
		self.assertIn("id2", s)

	def test_Event(self) -> None:
		e = Event("event")

		self.assertEqual(0, len(e))
		self.assertEqual(0, len([a for a in e]))

		e["id1"] = "value"

		self.assertEqual(1, len(e))
		self.assertEqual(1, len([a for a in e]))
		self.assertIn("id1", e)

		self.assertEqual("value", e["id1"])

		e["id1"] = "value1"

		self.assertEqual(1, len(e))
		self.assertListEqual([("id1", "value1")], [a for a in e])

		e["id2"] = "value2"

		self.assertEqual(2, len(e))
		self.assertIn("id2", e)
		self.assertListEqual([("id1", "value1"), ("id2", "value2")], [a for a in e])

		del e["id1"]

		self.assertEqual(1, len(e))
		self.assertListEqual([("id2", "value2")], [a for a in e])
		self.assertIn("id2", e)
