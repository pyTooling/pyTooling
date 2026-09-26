# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for :func:`pyTooling.Common.parseISO8601Timestamp`.
"""
from datetime          import datetime, timedelta, timezone

from pyTooling.Common  import parseISO8601Timestamp
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Timestamps(Testcase):
	def test_UTC(self) -> None:
		self.assertEqual(
			datetime(2026, 9, 15, 6, 35, 24, tzinfo=timezone.utc),
			parseISO8601Timestamp("2026-09-15T06:35:24Z")
		)

	def test_Offset(self) -> None:
		timestamp = parseISO8601Timestamp("2026-09-15T08:35:24+02:00")

		self.assertEqual(datetime(2026, 9, 15, 6, 35, 24, tzinfo=timezone.utc), timestamp)
		self.assertEqual(timedelta(hours=2), timestamp.utcoffset())

	def test_Naive(self) -> None:
		self.assertIsNone(parseISO8601Timestamp("2026-09-15T06:35:24").tzinfo)

	def test_NaiveWithDefaultTimeZone(self) -> None:
		self.assertEqual(timezone.utc, parseISO8601Timestamp("2026-09-15T06:35:24", timezone.utc).tzinfo)

	def test_AwareKeepsItsOffset(self) -> None:
		timestamp = parseISO8601Timestamp("2026-09-15T08:35:24+02:00", timezone.utc)

		self.assertEqual(timedelta(hours=2), timestamp.utcoffset())

	def test_None(self) -> None:
		self.assertIsNone(parseISO8601Timestamp(None))
		self.assertIsNone(parseISO8601Timestamp(""))

	def test_Invalid(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = parseISO8601Timestamp("yesterday")

		self.assertEqual("'yesterday' isn't an ISO 8601 timestamp.", str(context.exception))
