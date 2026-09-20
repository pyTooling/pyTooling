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

from pyTooling.Tracing import TracingError, Trace, TraceElement, Span, Event, SpanState
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

		self.assertEqual("Timespan 'span' is not empty and can't be entered.", str(context.exception))
		self.assertIn("Its state is 'Running'.", context.exception.__notes__)
		self.assertEqual(2, len(context.exception.__notes__))

	def test_EnterRecordedTrace(self) -> None:
		with self.assertRaises(TracingError) as context:
			with Trace("trace", beginTime=self._begin, endTime=self._begin):
				pass

		self.assertEqual("Trace 'trace' is not empty and can't be entered.", str(context.exception))
		self.assertIn("Its state is 'Complete'.", context.exception.__notes__)

	def test_EnterSpanTwice(self) -> None:
		with Trace("trace"):
			s = Span("span")
			with s:
				pass

			with self.assertRaises(TracingError) as context:
				with s:
					pass

		self.assertEqual("Timespan 'span' is not empty and can't be entered.", str(context.exception))
		self.assertIn("Its state is 'Complete'.", context.exception.__notes__)

	def test_EnterSpanTwiceKeepsFirstTiming(self) -> None:
		with Trace("trace") as trace:
			span = Span("span")
			with span:
				pass

			stopTime = span.StopTime
			with self.assertRaises(TracingError):
				with span:
					pass

		self.assertEqual(stopTime, span.StopTime)
		self.assertEqual(1, trace.SubSpanCount)

	def test_State(self) -> None:
		self.assertIs(SpanState.Empty, Span("span").State)
		self.assertIs(SpanState.Running, Span("span", beginTime=self._begin).State)
		self.assertIs(SpanState.Complete, Span("span", beginTime=self._begin, endTime=self._begin).State)

	def test_StateWhileTimed(self) -> None:
		with Trace("trace") as trace:
			span = Span("span")
			self.assertIs(SpanState.Empty, span.State)
			with span:
				self.assertIs(SpanState.Running, span.State)

			self.assertIs(SpanState.Complete, span.State)

		self.assertIs(SpanState.Complete, trace.State)

	def test_Duration(self) -> None:
		span = Span("span", beginTime=self._begin, duration=timedelta(seconds=90))

		self.assertEqual(self._begin + timedelta(seconds=90), span.StopTime)
		self.assertEqual(90.0, span.Duration)
		self.assertIs(SpanState.Complete, span.State)

	def test_DurationOnTrace(self) -> None:
		trace = Trace("trace", beginTime=self._begin, duration=timedelta(minutes=2))

		self.assertEqual(self._begin + timedelta(minutes=2), trace.StopTime)
		self.assertEqual(120.0, trace.Duration)

	def test_DurationWithoutBeginTime(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", duration=timedelta(seconds=5))

		self.assertEqual("Parameter 'duration' is given without parameter 'beginTime'.", str(context.exception))

	def test_DurationWithoutBeginTimeOutranksTheValue(self) -> None:
		for value in (-5, "5", float("nan")):
			with self.subTest(duration=value):
				with self.assertRaises(ValueError) as context:
					_ = Span("span", duration=value)

				self.assertEqual("Parameter 'duration' is given without parameter 'beginTime'.", str(context.exception))

	def test_DurationAndEndTime(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", beginTime=self._begin, endTime=self._begin, duration=timedelta(seconds=5))

		self.assertEqual("Parameters 'endTime' and 'duration' are both given.", str(context.exception))

	def test_NegativeDuration(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", beginTime=self._begin, duration=timedelta(seconds=-1))

		self.assertEqual("Parameter 'duration' is negative.", str(context.exception))

	def test_DurationAsSeconds(self) -> None:
		span = Span("span", beginTime=self._begin, duration=98)

		self.assertEqual(self._begin + timedelta(seconds=98), span.StopTime)
		self.assertEqual(98.0, span.Duration)

	def test_DurationAsFractionalSeconds(self) -> None:
		span = Span("span", beginTime=self._begin, duration=98.5)

		self.assertEqual(self._begin + timedelta(seconds=98.5), span.StopTime)
		self.assertEqual(98.5, span.Duration)

	def test_DurationAsSecondsOnTrace(self) -> None:
		trace = Trace("trace", beginTime=self._begin, duration=120)

		self.assertEqual(120.0, trace.Duration)

	def test_DurationType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Span("span", beginTime=self._begin, duration="98")

		self.assertEqual("Parameter 'duration' is not of type 'timedelta', 'int' or 'float'.", str(context.exception))

	def test_DurationAsBool(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Span("span", beginTime=self._begin, duration=True)

		self.assertEqual("Parameter 'duration' is not of type 'timedelta', 'int' or 'float'.", str(context.exception))
		self.assertIn("Got type 'bool'.", context.exception.__notes__)

	def test_DurationNotFinite(self) -> None:
		for value in (float("nan"), float("inf"), float("-inf")):
			with self.subTest(duration=value):
				with self.assertRaises(ValueError) as context:
					_ = Span("span", beginTime=self._begin, duration=value)

				self.assertEqual("Parameter 'duration' is not a finite number of seconds.", str(context.exception))

	def test_NegativeDurationAsSeconds(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Span("span", beginTime=self._begin, duration=-0.5)

		self.assertEqual("Parameter 'duration' is negative.", str(context.exception))

	def test_Stop(self) -> None:
		span = Span("span", beginTime=datetime.now())
		self.assertIs(SpanState.Running, span.State)

		span.Stop()

		self.assertIs(SpanState.Complete, span.State)
		self.assertGreaterEqual(span.Duration, 0.0)

	def test_StopReturnsSelf(self) -> None:
		span = Span("span", beginTime=datetime.now())

		self.assertIs(span, span.Stop())

	def test_StopTimeAssignment(self) -> None:
		span = Span("span", beginTime=self._begin)
		span.StopTime = self._begin + timedelta(seconds=3)

		self.assertEqual(3.0, span.Duration)

	def test_StopTwice(self) -> None:
		span = Span("span", beginTime=datetime.now())
		span.Stop()

		with self.assertRaises(TracingError) as context:
			span.Stop()

		self.assertEqual("Span 'span' already has an end time.", str(context.exception))

	def test_StopWithoutBeginTime(self) -> None:
		with self.assertRaises(TracingError) as context:
			Span("span").Stop()

		self.assertEqual("Span 'span' has no begin time and can't be stopped.", str(context.exception))

	def test_StopTimedSpan(self) -> None:
		with Trace("trace"):
			with Span("span") as span:
				with self.assertRaises(TracingError) as context:
					span.Stop()

		self.assertEqual("Span 'span' is timed by a with-statement.", str(context.exception))

	def test_StopTimeBeforeBeginTime(self) -> None:
		span = Span("span", beginTime=self._begin)

		with self.assertRaises(ValueError) as context:
			span.StopTime = self._begin - timedelta(microseconds=1)

		self.assertEqual("Parameter 'value' is before the begin time.", str(context.exception))

	def test_StopTimeAssignedTwice(self) -> None:
		span = Span("span", beginTime=self._begin)
		span.StopTime = self._begin + timedelta(seconds=1)

		with self.assertRaises(TracingError) as context:
			span.StopTime = self._begin + timedelta(seconds=2)

		self.assertEqual("Span 'span' already has an end time.", str(context.exception))

	def test_ChildWithinParent(self) -> None:
		parent = Span("parent", beginTime=self._begin, duration=timedelta(seconds=100))
		child =  Span("child", beginTime=self._begin + timedelta(seconds=1), duration=timedelta(seconds=8), parent=parent)

		self.assertIs(parent, child.Parent)
		self.assertEqual(1, parent.SubSpanCount)

	def test_ChildBeginsBeforeParent(self) -> None:
		parent = Span("parent", beginTime=self._begin, duration=timedelta(seconds=100))

		with self.assertRaises(ValueError) as context:
			_ = Span("child", beginTime=self._begin - timedelta(microseconds=1), parent=parent)

		self.assertEqual("Timespan 'child' begins before its parent 'parent'.", str(context.exception))
		self.assertEqual(0, parent.SubSpanCount)

	def test_ChildEndsAfterParent(self) -> None:
		parent = Span("parent", beginTime=self._begin, duration=timedelta(seconds=100))

		with self.assertRaises(ValueError) as context:
			_ = Span("child", beginTime=self._begin, duration=timedelta(seconds=101), parent=parent)

		self.assertEqual("Timespan 'child' ends after its parent 'parent'.", str(context.exception))

	def test_ChildOfRunningParent(self) -> None:
		parent = Span("parent", beginTime=self._begin)
		child =  Span("child", beginTime=self._begin + timedelta(seconds=1), parent=parent)

		self.assertIs(SpanState.Running, child.State)
		self.assertEqual(1, parent.SubSpanCount)


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


class TraceElements(Testcase):
	def test_ASpanAndAnEventAreTraceElements(self) -> None:
		trace = Trace("trace")
		span =  Span("span", parent=trace)
		event = Event("event", parent=span)

		for element, name, parent in ((trace, "trace", None), (span, "span", trace), (event, "event", span)):
			with self.subTest(element=element.__class__.__name__):
				self.assertIsInstance(element, TraceElement)
				self.assertEqual(name, element.Name)
				self.assertIs(parent, element.Parent)

	def test_TheElementIsAttachedOnlyWhenItIsValid(self) -> None:
		"""The base-class validates; the derived class attaches, so a rejected element doesn't reach its parent."""
		span = Span("span")

		with self.assertRaises(TypeError):
			_ = Event("event", "yesterday", parent=span)

		self.assertEqual(0, len(span._events))


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

	def test_Get(self) -> None:
		for element in (Trace("trace"), Span("span"), Event("event")):
			with self.subTest(element=element.__class__.__name__):
				element["id1"] = "value1"

				self.assertEqual("value1", element.get("id1"))
				self.assertIsNone(element.get("id2"))
				self.assertEqual("default", element.get("id2", "default"))
				self.assertNotIn("id2", element, "Reading a key doesn't create it.")

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
