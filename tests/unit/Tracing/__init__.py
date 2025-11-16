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
"""Unit tests for :mod:`pyTooling.GenericPath.URL`."""
from time import sleep
from unittest import TestCase
from pyTooling.Tracing import Trace, Span


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
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
		self.assertEqual(0, len(t))
		self.assertFalse(t.HasNestedSpans)

		self.assertEqual(0, len([s for s in t]))

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

		self.assertEqual(1, len(t))
		self.assertTrue(t.HasNestedSpans)

		self.assertEqual(1, len([s for s in t]))

		self.assertFalse(s.HasNestedSpans)
		self.assertIs(t, s.Parent)

		print(f"Duration: {t.Duration*1e3:.3f} ms")
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

		self.assertEqual(4, len(t))

		print(f"Duration: {t.Duration*1e3:.3f} ms")
		print()
		for line in t.Format():
			print(line)
