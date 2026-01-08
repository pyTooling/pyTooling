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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :func:`firstKey`, :func:`firstValue`, :func:`firstPair`, :func:`mergedicts` and :func:`zipdicts`.
"""
from unittest           import TestCase

from pytest             import mark

from pyTooling.Common   import firstKey, firstValue, firstPair, mergedicts, zipdicts
from pyTooling.Platform import CurrentPlatform


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class First(TestCase):
	def test_FirstKey0(self) -> None:
		d = {}

		with self.assertRaises(ValueError):
			_ = firstKey(d)

	def test_FirstKey1(self) -> None:
		d = {"1": 1}

		f = firstKey(d)
		self.assertEqual("1", f)

	def test_FirstKey2(self) -> None:
		d = {"1": 1, "2": 2}

		f = firstKey(d)
		self.assertEqual("1", f)

	def test_FirstValue0(self) -> None:
		d = {}

		with self.assertRaises(ValueError):
			_ = firstValue(d)

	def test_FirstValue1(self) -> None:
		d = {"1": 1}

		f = firstValue(d)
		self.assertEqual(1, f)

	def test_FirstValue2(self) -> None:
		d = {"1": 1, "2": 2}

		f = firstValue(d)
		self.assertEqual(1, f)

	def test_FirstPair0(self) -> None:
		d = {}

		with self.assertRaises(ValueError):
			_ = firstPair(d)

	def test_FirstPair1(self) -> None:
		d = {"1": 1}

		f = firstPair(d)
		self.assertTupleEqual(("1", 1), f)

	def test_FirstPair2(self) -> None:
		d = {"1": 1, "2": 2}

		f = firstPair(d)
		self.assertTupleEqual(("1", 1), f)


class Merge(TestCase):
	def test_NoDicts(self) -> None:
		with self.assertRaises(ValueError):
			_ = mergedicts()

		with self.assertRaises(ValueError):
			_ = mergedicts(filter=lambda k, v: True)

	def test_Merge1(self) -> None:
		d1 = {"1": 1, "2": 2}

		expected = (
			("1", 1),
			("2", 2)
		)

		m = mergedicts(d1)
		self.assertTupleEqual(expected, tuple(m.items()))

	def test_Merge2(self) -> None:
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}

		expected = (
			("1", 1),
			("2", 2),
			("3", 3),
			("4", 4)
		)

		m = mergedicts(d1, d2)
		self.assertTupleEqual(expected, tuple(m.items()))

	def test_Merge3(self) -> None:
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}
		d3 = {"5": 5, "6": 6}

		expected = (
			("1", 1),
			("2", 2),
			("3", 3),
			("4", 4),
			("5", 5),
			("6", 6)
		)

		m = mergedicts(d1, d2, d3)
		self.assertTupleEqual(expected, tuple(m.items()))

	def test_Merge2Filter(self) -> None:
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}

		expected = (
			("2", 2),
			("4", 4)
		)

		m = mergedicts(d1, d2, filter=lambda key, value: value % 2 == 0)
		self.assertTupleEqual(expected, tuple(m.items()))


class Zip(TestCase):
	def test_NoDicts(self) -> None:
		with self.assertRaises(ValueError):
			_ = zipdicts()

	@mark.skipif(CurrentPlatform.IsPyPy and CurrentPlatform.PythonVersion == "3.10", reason="Tuple/list expansion with *foo is broken in pypy-3.10.")
	def test_Zip1_1(self) -> None:
		d1 = {"a": 1}
		d2 = {"b": "2"}

		with self.assertRaises(KeyError):
			for key, valueA, valueB in zipdicts(d1, d2):
				pass

	def test_Zip1_2(self) -> None:
		d1 = {"a": 1}
		d2 = {"a": "1", "b": "2"}

		with self.assertRaises(ValueError):
			_ = zipdicts(d1, d2)

	def test_Zip2_1(self) -> None:
		d1 = {"a": 1,   "b": 2}
		d2 = {"a": "1"}

		with self.assertRaises(ValueError):
			_ = zipdicts(d1, d2)

	def test_Zip2_2(self) -> None:
		d1 = {"a": 1,   "b": 2}
		d2 = {"a": "1", "b": "2"}

		expected = (
			("a", 1, "1"),
			("b", 2, "2"),
		)

		z = zipdicts(d1, d2)
		self.assertTupleEqual(expected, tuple(z))

	def test_Iterate(self) -> None:
		d1 = {"a": 1,   "b": 2}
		d2 = {"a": "1", "b": "2"}

		expected = (
			("a", 1, "1"),
			("b", 2, "2"),
		)

		i = 0
		for key, value1, value2 in zipdicts(d1, d2):
			self.assertTupleEqual(expected[i], (key, value1, value2))
			i += 1
