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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :func:`isnestedclass`.
"""
from unittest import TestCase

from pyTooling.Common import firstKey, firstValue, firstItem, mergedicts, zipdicts


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class First(TestCase):
	def test_FirstKey0(self):
		d = {}

		with self.assertRaises(ValueError):
			f = firstKey(d)

	def test_FirstKey1(self):
		d = {"1": 1}

		f = firstKey(d)
		self.assertEqual("1", f)

	def test_FirstKey2(self):
		d = {"1": 1, "2": 2}

		f = firstKey(d)
		self.assertEqual("1", f)

	def test_FirstValue0(self):
		d = {}

		with self.assertRaises(ValueError):
			f = firstValue(d)

	def test_FirstValue1(self):
		d = {"1": 1}

		f = firstValue(d)
		self.assertEqual(1, f)

	def test_FirstValue2(self):
		d = {"1": 1, "2": 2}

		f = firstValue(d)
		self.assertEqual(1, f)

	def test_FirstItem0(self):
		d = {}

		with self.assertRaises(ValueError):
			f = firstItem(d)

	def test_FirstItem1(self):
		d = {"1": 1}

		f = firstItem(d)
		self.assertTupleEqual(("1", 1), f)

	def test_FirstItem2(self):
		d = {"1": 1, "2": 2}

		f = firstItem(d)
		self.assertTupleEqual(("1", 1), f)


class Merge(TestCase):
	def test_NoDicts(self):
		with self.assertRaises(ValueError):
			m = mergedicts()

		with self.assertRaises(ValueError):
			m = mergedicts(func=lambda item: item)

	def test_Merge1(self):
		d1 = {"1": 1, "2": 2}

		expected = {"1": 1, "2": 2}

		m = mergedicts(d1)
		self.assertDictEqual(expected, m)

	def test_Merge2(self):
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}

		expected = {"1": 1, "2": 2, "3": 3, "4": 4}

		m = mergedicts(d1, d2)
		self.assertDictEqual(expected, m)

	def test_Merge3(self):
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}
		d3 = {"5": 5, "6": 6}

		expected = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6}

		m = mergedicts(d1, d2, d3)
		self.assertDictEqual(expected, m)

	def test_Merge2Func(self):
		d1 = {"1": 1, "2": 2}
		d2 = {"3": 3, "4": 4}

		expected = {"1": 1, "2": 2, "3": 3, "4": 4}

		m = mergedicts(d1, d2, func=lambda key, value: (key, value * 2))
		self.assertDictEqual(expected, m)


class Zip(TestCase):
	def test_NoDicts(self):
		with self.assertRaises(ValueError):
			z = zipdicts()

	def test_Zip1_2(self):
		d1 = {"a": 1}
		d2 = {"a": "1", "b": "2"}

		with self.assertRaises(ValueError):
			z = zipdicts(d1, d2)

	def test_Zip2_2(self):
		d1 = {"a": 1,   "b": 2}
		d2 = {"a": "1", "b": "2"}

		expected = (
			("a", 1, "1"),
			("b", 2, "2"),
		)

		z = zipdicts(d1, d2)
		self.assertTupleEqual(expected, tuple(z))
