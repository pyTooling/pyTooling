# ==================================================================================================================== #
#             _____           _ _           __     __            _             _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \   / /__ _ __ ___(_) ___  _ __ (_)_ __   __ _                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ / / _ \ '__/ __| |/ _ \| '_ \| | '_ \ / _` |                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V /  __/ |  \__ \ | (_) | | | | | | | | (_| |                          #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/ \___|_|  |___/_|\___/|_| |_|_|_| |_|\__, |                          #
# |_|    |___/                          |___/                                          |___/                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2020-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for package :mod:`pyTooling.Versioning`."""
from unittest             import TestCase

from pyTooling.Versioning import CalendarVersion, WordSizeValidator, MaxValueValidator


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Version(TestCase):
	def test_CreateFromEmptyString(self) -> None:
		with self.assertRaises(ValueError):
			CalendarVersion.Parse("")

	def test_CreateFromSomeString(self) -> None:
		with self.assertRaises(ValueError):
			CalendarVersion.Parse("None")

	def test_CreateFromString1(self) -> None:
		version = CalendarVersion.Parse("0.0")

		self.assertEqual(0, version.Major, "Major number is not 0.")
		self.assertEqual(0, version.Minor, "Minor number is not 0.")

	def test_CreateFromIntegers1(self) -> None:
		version = CalendarVersion(0, 0)

		self.assertEqual(0, version.Major, "Major number is not 0.")
		self.assertEqual(0, version.Minor, "Minor number is not 0.")

	def test_CreateFromIntegers2(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual(1, version.Major, "Major number is not 1.")
		self.assertEqual(2, version.Minor, "Minor number is not 2.")


class ValidatedWordSize(TestCase):
	def test_All8Bit_AllInRange(self) -> None:
		version = CalendarVersion.Parse("12.64", WordSizeValidator(8))

		self.assertEqual(12, version.Major)
		self.assertEqual(64, version.Minor)

	def test_All8Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("1203.64", WordSizeValidator(8))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All8Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("12.640", WordSizeValidator(8))

		self.assertIn("Version.Minor", str(ex.exception))
