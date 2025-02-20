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
# Copyright 2020-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from pytest               import mark

from pyTooling.Versioning import Flags, CalendarVersion, WordSizeValidator, MaxValueValidator
from pyTooling.Versioning import YearMonthVersion, YearWeekVersion, YearReleaseVersion, YearMonthDayVersion


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Major(self):
		version = CalendarVersion(1)

		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_MajorMinor(self):
		version = CalendarVersion(1, 2)

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	def test_Major_String(self):
		with self.assertRaises(TypeError):
			_ = CalendarVersion("1")

	def test_Major_Negative(self):
		with self.assertRaises(ValueError):
			_ = CalendarVersion(-1)

	def test_Major_Minor_String(self):
		with self.assertRaises(TypeError):
			_ = CalendarVersion(1, "2")

	def test_Major_Minor_Negative(self):
		with self.assertRaises(ValueError):
			_ = CalendarVersion(1, -2)


class Parsing(TestCase):
	def test_None(self) -> None:
		with self.assertRaises(ValueError):
			CalendarVersion.Parse(None)

	def test_EmptyString(self) -> None:
		with self.assertRaises(ValueError):
			CalendarVersion.Parse("")

	def test_OtherType(self) -> None:
		with self.assertRaises(TypeError):
			CalendarVersion.Parse(1)

	def test_InvalidString(self) -> None:
		with self.assertRaises(ValueError):
			CalendarVersion.Parse("None")

	def test_String_Major(self) -> None:
		version = CalendarVersion.Parse("1")

		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)

	def test_String_MajorMinor(self) -> None:
		version = CalendarVersion.Parse("1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	@mark.xfail(msg="v2024.04 not yet support")
	def test_vString(self) -> None:
		version = CalendarVersion.Parse("v1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	@mark.xfail(msg="i2024.04 not yet support")
	def test_iString(self) -> None:
		version = CalendarVersion.Parse("i1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	@mark.xfail(msg="r2024.04 not yet support")
	def test_rString(self) -> None:
		version = CalendarVersion.Parse("r1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)


# class CompareVersions(TestCase):
# 	def test_Equal(self) -> None:
# 		l = [
# 			("0.0.0", "0.0.0"),
# 			("0.0.1", "0.0.1"),
# 			("0.1.0", "0.1.0"),
# 			("1.0.0", "1.0.0"),
# 			("1.0.1", "1.0.1"),
# 			("1.1.0", "1.1.0"),
# 			("1.1.1", "1.1.1")
# 		]
#
# 		for t in l:
# 			with self.subTest(equal=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertEqual(v1, v2)
#
# 	def test_Unequal(self) -> None:
# 		l = [
# 			("0.0.0", "0.0.1"),
# 			("0.0.1", "0.0.0"),
# 			("0.0.0", "0.1.0"),
# 			("0.1.0", "0.0.0"),
# 			("0.0.0", "1.0.0"),
# 			("1.0.0", "0.0.0"),
# 			("1.0.1", "1.1.0"),
# 			("1.1.0", "1.0.1")
# 		]
#
# 		for t in l:
# 			with self.subTest(unequal=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertNotEqual(v1, v2)
#
# 	def test_LessThan(self) -> None:
# 		l = [
# 			("0.0.0", "0.0.1"),
# 			("0.0.0", "0.1.0"),
# 			("0.0.0", "1.0.0"),
# 			("0.0.1", "0.1.0"),
# 			("0.1.0", "1.0.0")
# 		]
#
# 		for t in l:
# 			with self.subTest(lessthan=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertLess(v1, v2)
#
# 	def test_LessEqual(self) -> None:
# 		l = [
# 			("0.0.0", "0.0.0"),
# 			("0.0.0", "0.0.1"),
# 			("0.0.0", "0.1.0"),
# 			("0.0.0", "1.0.0"),
# 			("0.0.1", "0.1.0"),
# 			("0.1.0", "1.0.0")
# 		]
#
# 		for t in l:
# 			with self.subTest(lessequal=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertLessEqual(v1, v2)
#
# 	def test_GreaterThan(self) -> None:
# 		l = [
# 			("0.0.1", "0.0.0"),
# 			("0.1.0", "0.0.0"),
# 			("1.0.0", "0.0.0"),
# 			("0.1.0", "0.0.1"),
# 			("1.0.0", "0.1.0")
# 		]
#
# 		for t in l:
# 			with self.subTest(greaterthan=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertGreater(v1, v2)
#
# 	def test_GreaterEqual(self) -> None:
# 		l = [
# 			("0.0.0", "0.0.0"),
# 			("0.0.1", "0.0.0"),
# 			("0.1.0", "0.0.0"),
# 			("1.0.0", "0.0.0"),
# 			("0.1.0", "0.0.1"),
# 			("1.0.0", "0.1.0")
# 		]
#
# 		for t in l:
# 			with self.subTest(greaterequal=t):
# 				v1 = CalendarVersion.Parse(t[0])
# 				v2 = CalendarVersion.Parse(t[1])
# 				self.assertGreaterEqual(v1, v2)


class HashVersions(TestCase):
	def test_CalendarVersion(self):
		version = CalendarVersion.Parse("2024.2")

		self.assertIsNotNone(version.__hash__())

	def test_YearMonthVersion(self):
		version = YearMonthVersion(2024, 2)

		self.assertIsNotNone(version.__hash__())

	def test_YearWeekVersion(self):
		version = YearWeekVersion(2024, 42)

		self.assertIsNotNone(version.__hash__())

	def test_YearReleaseVersion(self):
		version = YearReleaseVersion(2024, 25)

		self.assertIsNotNone(version.__hash__())

	def test_YearMonthDayVersion(self):
		version = YearMonthDayVersion(2024, 8, 25)

		self.assertIsNotNone(version.__hash__())


class CompareNone(TestCase):
	def test_Equal(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version == None

	def test_Unequal(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version != None

	def test_LessThan(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version < None

	def test_LessThanOrEqual(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version <= None

	def test_GreaterThan(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version > None

	def test_GreaterThanOrEqual(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version >= None


class CompareString(TestCase):
	def test_Equal(self):
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", version)

	def test_Unequal(self):
		version = CalendarVersion(1, 2)

		self.assertNotEqual("1.3", version)

	def test_LessThan(self):
		version = CalendarVersion(1, 2)

		self.assertLess("1.1", version)

	def test_LessThanOrEqual(self):
		version = CalendarVersion(1, 2)

		self.assertLessEqual("1.2", version)

	def test_GreaterThan(self):
		version = CalendarVersion(1, 2)

		self.assertGreater("1.3", version)

	def test_GreaterThanOrEqual(self):
		version = CalendarVersion(1, 2)

		self.assertGreaterEqual("1.2", version)


class CompareInteger(TestCase):
	def test_Equal(self):
		version = CalendarVersion(1)

		self.assertEqual(1, version)

	def test_Unequal(self):
		version = CalendarVersion(1)

		self.assertNotEqual(2, version)

	def test_LessThan(self):
		version = CalendarVersion(1, 2)

		self.assertLess(0, version)

	def test_LessThanOrEqual(self):
		version = CalendarVersion(1, 2)

		self.assertLessEqual(1, version)

	def test_GreaterThan(self):
		version = CalendarVersion(1, 2)

		self.assertGreater(3, version)

	def test_GreaterThanOrEqual(self):
		version = CalendarVersion(1, 2)

		self.assertGreaterEqual(2, version)


class CompareOtherType(TestCase):
	def test_Equal(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version == 1.2

	def test_Unequal(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version != 1.2

	def test_LessThan(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version < 1.2

	def test_LessThanOrEqual(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version <= 1.2

	def test_GreaterThan(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version > 1.2

	def test_GreaterThanOrEqual(self):
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version >= 1.2


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

	def test_35Bits_AllInRange(self) -> None:
		version = CalendarVersion.Parse("7.31", WordSizeValidator(2, majorBits=3, minorBits=5))

		self.assertEqual(7, version.Major)
		self.assertEqual(31, version.Minor)

	def test_35Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("8.31", WordSizeValidator(majorBits=3, minorBits=5))

		self.assertIn("Version.Major", str(ex.exception))

	def test_35Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("7.32", WordSizeValidator(8, majorBits=3, minorBits=5))

		self.assertIn("Version.Minor", str(ex.exception))


class ValidatedMaxValue(TestCase):
	def test_All63_AllInRange(self) -> None:
		version = CalendarVersion.Parse("12.63", MaxValueValidator(63))

		self.assertEqual(12, version.Major)
		self.assertEqual(63, version.Minor)

	def test_All63_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("64.12", MaxValueValidator(63))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All63_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = CalendarVersion.Parse("12.64",  MaxValueValidator(63))

		self.assertIn("Version.Minor", str(ex.exception))


class FormattingUsingRepr(TestCase):
	def test_Major(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual("1.0", repr(version))

	@mark.xfail(msg="v2024.04 not yet support")
	def test_MajorPrefix(self) -> None:
		version = CalendarVersion(1, prefix="v")

		self.assertEqual("v1.0", repr(version))

	def test_MajorMinor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", repr(version))


class FormattingUsingStr(TestCase):
	def test_Major(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual("1", str(version))

	@mark.xfail(msg="v2024.04 not yet support")
	def test_MajorPrefix(self) -> None:
		version = CalendarVersion(1, prefix="v")

		self.assertEqual("v1", str(version))

	def test_MajorMinor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", str(version))


class FormattingUsingFormat(TestCase):
	def test_Empty(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", f"{version:}")
		self.assertEqual(str(version), f"{version:}")

	def test_OtherFormat(self) -> None:
		version = CalendarVersion(1, 2, 3)

		self.assertEqual("hello world", f"{version:hello world}")

	def test_Percent(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("hello%world", f"{version:hello%%world}")

	def test_Major(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1", f"{version:%M}")

	def test_Minor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("2", f"{version:%m}")

	def test_FullVersion(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("v1.2", f"{version:v%M.%m}")


class InstantiationOfYearMonthVersion(TestCase):
	def test_Year(self):
		version = YearMonthVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonth(self):
		version = YearMonthVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearWeekVersion(TestCase):
	def test_Year(self):
		version = YearWeekVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Week)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearWeek(self):
		version = YearWeekVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Week)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearReleaseVersion(TestCase):
	def test_Year(self):
		version = YearReleaseVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Release)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearRelease(self):
		version = YearReleaseVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Release)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearMonthDayVersion(TestCase):
	def test_Year(self):
		version = YearMonthDayVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Month)
		self.assertEqual(0, version.Day)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonth(self):
		version = YearMonthDayVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonthDay(self):
		version = YearMonthDayVersion(1, 2, 3)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(3, version.Day)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)
