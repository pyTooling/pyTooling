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
Unit tests for :func:`firstItem` and :func:`lastItem`.
"""
from unittest import TestCase

from pyTooling.Common import firstItem, lastItem, count

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Count(TestCase):
	def test_count_empty(self) -> None:
		c = count(range(0))

		self.assertEqual(0, c)

	def test_count_1(self) -> None:
		c = count(range(1))

		self.assertEqual(1, c)

	def test_count_5(self) -> None:
		c = count(range(5))

		self.assertEqual(5, c)

	def test_count_10(self) -> None:
		length = 10

		l = [i for i in range(length)]
		g = (i for i in l)
		c = count(g)

		self.assertEqual(length, c)

class First(TestCase):
	def test_FirstItem0(self) -> None:
		d = []

		with self.assertRaises(ValueError):
			_ = firstItem(d)

	def test_FirstItem1(self) -> None:
		d = [1]

		f = firstItem(d)
		self.assertEqual(1, f)

	def test_FirstItem2(self) -> None:
		d = [1, 2]

		f = firstItem(d)
		self.assertEqual(1, f)


class Last(TestCase):
	def test_LastItem0(self) -> None:
		d = []

		with self.assertRaises(ValueError):
			_ = lastItem(d)

	def test_LastItem1(self) -> None:
		d = [1]

		l = lastItem(d)
		self.assertEqual(1, l)

	def test_LastItem2(self) -> None:
		d = [1, 2]

		l = lastItem(d)
		self.assertEqual(2, l)
