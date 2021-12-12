# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Testing the Version module
#
# License:
# ============================================================================
# Copyright 2020-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from unittest     import TestCase

from pyTooling.Versioning import SemVersion as UUT


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Version(TestCase):
	version : UUT

	# def test_CreateFromNone(self):
	# 	with self.assertRaises(ValueError):
	# 		version = Version(versionString=None)

	def test_CreateFromEmptyString(self) -> None:
		with self.assertRaises(ValueError):
			UUT("")

	def test_CreateFromSomeString(self) -> None:
		with self.assertRaises(ValueError):
			UUT("None")

	def test_CreateFromString1(self) -> None:
		version = UUT("0.0.0")

		self.assertEqual(version.major, 0, "Major number is not 0.")
		self.assertEqual(version.minor, 0, "Minor number is not 0.")
		self.assertEqual(version.patch, 0, "Patch number is not 0.")
		self.assertEqual(version.build, 0, "Build number is not 0.")

	def test_CreateFromIntegers1(self) -> None:
		version = UUT(0, 0, 0)

		self.assertEqual(version.major, 0, "Major number is not 0.")
		self.assertEqual(version.minor, 0, "Minor number is not 0.")
		self.assertEqual(version.patch, 0, "Patch number is not 0.")
		self.assertEqual(version.build, 0, "Build number is not 0.")

	def test_CreateFromIntegers2(self) -> None:
		version = UUT(1, 2, 3, 4)

		self.assertEqual(version.major, 1, "Major number is not 1.")
		self.assertEqual(version.minor, 2, "Minor number is not 2.")
		self.assertEqual(version.patch, 3, "Patch number is not 3.")
		self.assertEqual(version.build, 4, "Build number is not 4.")

	def test_Equal(self) -> None:
		l = [
			("0.0.0", "0.0.0"),
			("0.0.1", "0.0.1"),
			("0.1.0", "0.1.0"),
			("1.0.0", "1.0.0"),
			("1.0.1", "1.0.1"),
			("1.1.0", "1.1.0"),
			("1.1.1", "1.1.1")
		]

		for t in l:
			with self.subTest(equal=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertEqual(v1, v2)

	def test_Unequal(self) -> None:
		l = [
			("0.0.0", "0.0.1"),
			("0.0.1", "0.0.0"),
			("0.0.0", "0.1.0"),
			("0.1.0", "0.0.0"),
			("0.0.0", "1.0.0"),
			("1.0.0", "0.0.0"),
			("1.0.1", "1.1.0"),
			("1.1.0", "1.0.1")
		]

		for t in l:
			with self.subTest(unequal=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertNotEqual(v1, v2)

	def test_LessThan(self) -> None:
		l = [
			("0.0.0", "0.0.1"),
			("0.0.0", "0.1.0"),
			("0.0.0", "1.0.0"),
			("0.0.1", "0.1.0"),
			("0.1.0", "1.0.0")
		]

		for t in l:
			with self.subTest(lessthan=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertLess(v1, v2)

	def test_LessEqual(self) -> None:
		l = [
			("0.0.0", "0.0.0"),
			("0.0.0", "0.0.1"),
			("0.0.0", "0.1.0"),
			("0.0.0", "1.0.0"),
			("0.0.1", "0.1.0"),
			("0.1.0", "1.0.0")
		]

		for t in l:
			with self.subTest(lessequal=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertLessEqual(v1, v2)

	def test_GreaterThan(self) -> None:
		l = [
			("0.0.1", "0.0.0"),
			("0.1.0", "0.0.0"),
			("1.0.0", "0.0.0"),
			("0.1.0", "0.0.1"),
			("1.0.0", "0.1.0")
		]

		for t in l:
			with self.subTest(greaterthan=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertGreater(v1, v2)

	def test_GreaterEqual(self) -> None:
		l = [
			("0.0.0", "0.0.0"),
			("0.0.1", "0.0.0"),
			("0.1.0", "0.0.0"),
			("1.0.0", "0.0.0"),
			("0.1.0", "0.0.1"),
			("1.0.0", "0.1.0")
		]

		for t in l:
			with self.subTest(greaterequal=t):
				v1 = UUT(t[0])
				v2 = UUT(t[1])
				self.assertGreaterEqual(v1, v2)
