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
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for :mod:`pyTooling.Tracing`."""
from colorama          import Fore
from time              import sleep
from unittest          import TestCase

from pyTooling.Tracing import TracingException, Trace, Span, Event

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
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

		with self.assertRaises(TracingException) as ex:
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


class Context(TestCase):
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


class Attributes(TestCase):
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
