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
# Copyright 2020-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :class:`pyTooling.Versioning.CalendarVersion` and its year-based variants: parsing,
comparing, validating and formatting.
"""
from pyTooling.Versioning import Flags, Parts, ReleaseLevel, CalendarVersion, WordSizeValidator, MaxValueValidator, \
                                 YearMonthVersion, YearWeekVersion, YearReleaseVersion, YearMonthDayVersion, \
                                 RangeBoundHandling, VersionRange, VersionSet
from pyTooling.Testing    import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Major(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_MajorMinor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	def test_Major_String(self) -> None:
		with self.assertRaises(TypeError):
			_ = CalendarVersion("1")

	def test_Major_Negative(self) -> None:
		with self.assertRaises(ValueError):
			_ = CalendarVersion(-1)

	def test_Major_Minor_String(self) -> None:
		with self.assertRaises(TypeError):
			_ = CalendarVersion(1, "2")

	def test_Major_Minor_Negative(self) -> None:
		with self.assertRaises(ValueError):
			_ = CalendarVersion(1, -2)


class Parsing(Testcase):
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

	def test_vString(self) -> None:
		version = CalendarVersion.Parse("v1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	def test_iString(self) -> None:
		version = CalendarVersion.Parse("i1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	def test_rString(self) -> None:
		version = CalendarVersion.Parse("r1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)

	def test_PrefixIsPreserved(self) -> None:
		version = CalendarVersion.Parse("v2024.04")

		self.assertEqual("v", version.Prefix)
		self.assertIn(Parts.Prefix, version.Parts)
		self.assertEqual("v2024.4", str(version))

	def test_NoPrefix(self) -> None:
		version = CalendarVersion.Parse("2024.04")

		self.assertEqual("", version.Prefix)
		self.assertNotIn(Parts.Prefix, version.Parts)

	def test_MultiCharacterPrefix(self) -> None:
		version = CalendarVersion.Parse("rev2024.04")

		self.assertEqual("rev", version.Prefix)
		self.assertEqual(2024, version.Major)
		self.assertEqual(4, version.Minor)

	def test_String_MajorMinorMicro(self) -> None:
		version = CalendarVersion.Parse("2024.10.15")

		self.assertEqual(2024, version.Major)
		self.assertEqual(10, version.Minor)
		self.assertEqual(15, version.Micro)
		self.assertEqual("2024.10.15", str(version))

	def test_MicroWithPrefix(self) -> None:
		version = CalendarVersion.Parse("v2024.10.15")

		self.assertEqual("v", version.Prefix)
		self.assertEqual("v2024.10.15", str(version))
		self.assertEqual("2024.10.15", repr(version))

	def test_TooManyParts(self) -> None:
		with self.assertRaises(ValueError) as context:
			CalendarVersion.Parse("2024.04.1.7.8")

		self.assertIn("Syntax error", str(context.exception))

	def test_FourthPartIsBuild(self) -> None:
		for cls in (CalendarVersion, YearMonthDayVersion):
			with self.subTest(versionClass=cls.__name__):
				version = cls.Parse("2024.10.15.7")

				self.assertEqual(15, version.Micro)
				self.assertEqual(7, version.Build)
				self.assertIn(Parts.Build, version.Parts)
				self.assertEqual("2024.10.15.7", str(version))

	def test_ThirdPartOnTwoPartClass(self) -> None:
		"""A two-part class describes no micro number, so the third numeric part can only be a build number."""
		for cls in (YearMonthVersion, YearWeekVersion, YearReleaseVersion):
			with self.subTest(versionClass=cls.__name__):
				version = cls.Parse("2024.10.15")

				self.assertEqual(10, version.Minor)
				self.assertEqual(0, version.Micro)
				self.assertNotIn(Parts.Micro, version.Parts)
				self.assertEqual(15, version.Build)
				self.assertIn(Parts.Build, version.Parts)
				self.assertEqual("2024.10.15", str(version))

	def test_FourthPartOnTwoPartClass(self) -> None:
		for cls in (YearMonthVersion, YearWeekVersion, YearReleaseVersion):
			with self.subTest(versionClass=cls.__name__):
				with self.assertRaises(ValueError) as context:
					cls.Parse("2024.10.15.7")

				self.assertEqual(
					f"Version number '2024.10.15.7' has 4 numeric parts, but '{cls.__name__}' describes 2 and a build number.",
					str(context.exception)
				)

	def test_ThirdPartOnYearMonthDay(self) -> None:
		version = YearMonthDayVersion.Parse("2024.10.15")

		self.assertEqual(2024, version.Year)
		self.assertEqual(10, version.Month)
		self.assertEqual(15, version.Day)
		self.assertEqual("2024.10.15", str(version))


# class CompareVersions(Testcase):
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


class HashVersions(Testcase):
	def test_CalendarVersion(self) -> None:
		version = CalendarVersion.Parse("2024.2")

		self.assertIsNotNone(version.__hash__())

	def test_YearMonthVersion(self) -> None:
		version = YearMonthVersion(2024, 2)

		self.assertIsNotNone(version.__hash__())

	def test_YearWeekVersion(self) -> None:
		version = YearWeekVersion(2024, 42)

		self.assertIsNotNone(version.__hash__())

	def test_YearReleaseVersion(self) -> None:
		version = YearReleaseVersion(2024, 25)

		self.assertIsNotNone(version.__hash__())

	def test_YearMonthDayVersion(self) -> None:
		version = YearMonthDayVersion(2024, 8, 25)

		self.assertIsNotNone(version.__hash__())


class CompareNone(Testcase):
	def test_Equal(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version == None

	def test_Unequal(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version != None

	def test_LessThan(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version < None

	def test_LessThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version <= None

	def test_GreaterThan(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version > None

	def test_GreaterThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(ValueError):
			_ = version >= None


class CompareString(Testcase):
	def test_Equal(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", version)

	def test_Unequal(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertNotEqual("1.3", version)

	def test_LessThan(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertLess("1.1", version)

	def test_LessThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertLessEqual("1.2", version)

	def test_GreaterThan(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertGreater("1.3", version)

	def test_GreaterThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertGreaterEqual("1.2", version)


class CompareInteger(Testcase):
	def test_Equal(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual(1, version)

	def test_Unequal(self) -> None:
		version = CalendarVersion(1)

		self.assertNotEqual(2, version)

	def test_LessThan(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertLess(0, version)

	def test_LessThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertLessEqual(1, version)

	def test_GreaterThan(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertGreater(3, version)

	def test_GreaterThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertGreaterEqual(2, version)

	def test_DerivedClasses(self) -> None:
		"""An integer is the year of a derived calendar version; it was passed as ``major``, which they don't take."""
		for version in (YearMonthVersion(2024, 3), YearWeekVersion(2024, 3), YearReleaseVersion(2024, 3)):
			with self.subTest(version=repr(version)):
				self.assertNotEqual(2024, version)
				self.assertLess(2024, version)
				self.assertGreater(2025, version)
				self.assertEqual(version.__class__(2024), 2024)

		self.assertGreater(2025, YearMonthDayVersion(2024, 3, 14))


class CompareOtherType(Testcase):
	def test_Equal(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version == 1.2

	def test_Unequal(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version != 1.2

	def test_LessThan(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version < 1.2

	def test_LessThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version <= 1.2

	def test_GreaterThan(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version > 1.2

	def test_GreaterThanOrEqual(self) -> None:
		version = CalendarVersion(1, 2)

		with self.assertRaises(TypeError):
			_ = version >= 1.2


class ValidatedWordSize(Testcase):
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


class ValidatedMaxValue(Testcase):
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


class FormattingUsingRepr(Testcase):
	def test_Major(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual("1.0", repr(version))

	def test_MajorPrefix(self) -> None:
		"""A prefix doesn't contribute to the version's value, so repr - the normalized form - omits it."""
		version = CalendarVersion(1, prefix="v")

		self.assertEqual("1.0", repr(version))

	def test_MajorMinor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", repr(version))


class FormattingUsingStr(Testcase):
	def test_Major(self) -> None:
		version = CalendarVersion(1)

		self.assertEqual("1", str(version))

	def test_MajorPrefix(self) -> None:
		version = CalendarVersion(1, prefix="v")

		self.assertEqual("v1", str(version))

	def test_MajorMinor(self) -> None:
		version = CalendarVersion(1, 2)

		self.assertEqual("1.2", str(version))


class FormattingUsingFormat(Testcase):
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


class InstantiationOfYearMonthVersion(Testcase):
	def test_Year(self) -> None:
		version = YearMonthVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonth(self) -> None:
		version = YearMonthVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearWeekVersion(Testcase):
	def test_Year(self) -> None:
		version = YearWeekVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Week)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearWeek(self) -> None:
		version = YearWeekVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Week)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearReleaseVersion(Testcase):
	def test_Year(self) -> None:
		version = YearReleaseVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Release)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearRelease(self) -> None:
		version = YearReleaseVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Release)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class InstantiationOfYearMonthDayVersion(Testcase):
	def test_Year(self) -> None:
		version = YearMonthDayVersion(1)

		self.assertEqual(1, version.Year)
		self.assertEqual(0, version.Month)
		self.assertEqual(0, version.Day)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonth(self) -> None:
		version = YearMonthDayVersion(1, 2)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)

	def test_YearMonthDay(self) -> None:
		version = YearMonthDayVersion(1, 2, 3)

		self.assertEqual(1, version.Year)
		self.assertEqual(2, version.Month)
		self.assertEqual(3, version.Day)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.Clean, version.Flags)


class RenderingIsConsistent(Testcase):
	"""Parsing a version and constructing the same version must render the same string - finding T28."""

	def test_ParsedAndConstructedAgree(self) -> None:
		for text, numbers in (("2024", (2024, )), ("2024.10", (2024, 10)), ("2024.10.15", (2024, 10, 15))):
			with self.subTest(version=text):
				self.assertEqual(str(CalendarVersion(*numbers)), str(CalendarVersion.Parse(text)))
				self.assertEqual(text, str(CalendarVersion.Parse(text)))

	def test_AnAbsentPartIsNotInvented(self) -> None:
		"""A missing part must not set its 'Parts' flag - that is what rendered '2024' as '2024.0'."""
		version = CalendarVersion.Parse("2024")

		self.assertEqual(Parts.Major | Parts.Level, version.Parts)
		self.assertNotIn(Parts.Minor, version.Parts)

	def test_ATwoPartVersionRendersTwoParts(self) -> None:
		"""The year-month, year-week and year-release classes describe two parts, so a third must not appear."""
		self.assertEqual("2024.10", str(YearMonthVersion(2024, 10)))
		self.assertEqual("2024.42", str(YearWeekVersion(2024, 42)))
		self.assertEqual("2024.3", str(YearReleaseVersion(2024, 3)))

	def test_AThreePartVersionIsUnaffected(self) -> None:
		self.assertEqual("2024.10.15", str(YearMonthDayVersion(2024, 10, 15)))
		self.assertEqual("2024.10.15", str(YearMonthDayVersion.Parse("2024.10.15")))



class InstantiationWithReleaseLevel(Testcase):
	def test_CalendarVersion(self) -> None:
		version = CalendarVersion(2024, 10, level=ReleaseLevel.ReleaseCandidate, number=2, post=3, dev=4, hash="abc")

		self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
		self.assertEqual(2, version.ReleaseNumber)
		self.assertEqual(3, version.Post)
		self.assertEqual(4, version.Dev)
		self.assertEqual("abc", version.Hash)
		self.assertIn(Parts.Post, version.Parts)
		self.assertIn(Parts.Dev, version.Parts)
		self.assertIn(Parts.Hash, version.Parts)

	def test_YearMonthVersion(self) -> None:
		version = YearMonthVersion(2024, 10, level=ReleaseLevel.Alpha, number=1)

		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)

	def test_YearWeekVersion(self) -> None:
		version = YearWeekVersion(2024, 42, level=ReleaseLevel.Beta, number=1)

		self.assertEqual(ReleaseLevel.Beta, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)

	def test_YearReleaseVersion(self) -> None:
		version = YearReleaseVersion(2024, 2, post=1)

		self.assertEqual(1, version.Post)

	def test_YearMonthDayVersion(self) -> None:
		version = YearMonthDayVersion(2024, 10, 15, level=ReleaseLevel.Development)

		self.assertEqual(ReleaseLevel.Development, version.ReleaseLevel)

	def test_NumberOnFinal(self) -> None:
		with self.assertRaises(ValueError):
			_ = YearMonthVersion(2024, 10, number=1)

	def test_LevelNotAReleaseLevel(self) -> None:
		with self.assertRaises(TypeError):
			_ = YearMonthVersion(2024, 10, level="rc")


class ParsingReleaseLevel(Testcase):
	def test_Separators(self) -> None:
		"""The release level may follow the numbers directly, or after a '.' or '-'."""
		for versionString in ("2024.01a1", "2024.01.a1", "2024.01-a1", "2024.01-a.1", "2024.01alpha1", "2024.01.alpha-1"):
			with self.subTest(versionString=versionString):
				version = CalendarVersion.Parse(versionString)

				self.assertEqual(2024, version.Year)
				self.assertEqual(1, version.Minor)
				self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
				self.assertEqual(1, version.ReleaseNumber)
				self.assertNotIn(Parts.Postfix, version.Parts)

	def test_Levels(self) -> None:
		for versionString, level, number in (
			("2024.01b2",     ReleaseLevel.Beta,             2),
			("2024.01c3",     ReleaseLevel.Gamma,            3),
			("2024.01rc4",    ReleaseLevel.ReleaseCandidate, 4),
			("2024.01-pre5",  ReleaseLevel.ReleaseCandidate, 5),
			("2024.01-rc",    ReleaseLevel.ReleaseCandidate, 0),
			("2024.01-alpha", ReleaseLevel.Alpha,            0),
			("2024.01-dev",   ReleaseLevel.Development,      0),
			("2024.01final",  ReleaseLevel.Final,            0)
		):
			with self.subTest(versionString=versionString):
				version = CalendarVersion.Parse(versionString)

				self.assertEqual(level, version.ReleaseLevel)
				self.assertEqual(number, version.ReleaseNumber)
				self.assertNotIn(Parts.Postfix, version.Parts)

	def test_PostAndDev(self) -> None:
		version = CalendarVersion.Parse("2024.01rc1.post2.dev3")

		self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)
		self.assertEqual(2, version.Post)
		self.assertEqual(3, version.Dev)

	def test_EveryClass(self) -> None:
		for cls, versionString in (
			(YearMonthVersion,    "2024.10-rc1"),
			(YearWeekVersion,     "2024.42-rc1"),
			(YearReleaseVersion,  "2024.2-rc1"),
			(YearMonthDayVersion, "2024.10.15-rc1")
		):
			with self.subTest(versionClass=cls.__name__):
				version = cls.Parse(versionString)

				self.assertIs(cls, version.__class__)
				self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
				self.assertEqual(1, version.ReleaseNumber)

	def test_BuildAndReleaseLevel(self) -> None:
		version = YearMonthVersion.Parse("2024.10.3rc1")

		self.assertEqual(3, version.Build)
		self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)


class ParsingPostfix(Testcase):
	def test_OSVVM(self) -> None:
		"""OSVVM appends a letter to a year-month version for the next release, e.g. '2025.06a'."""
		version = YearMonthVersion.Parse("2025.06a")

		self.assertEqual(2025, version.Year)
		self.assertEqual(6, version.Month)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual("a", version.Postfix)
		self.assertIn(Parts.Postfix, version.Parts)
		self.assertEqual("2025.6a", str(version))
		self.assertEqual("", version.PostfixSeparator)

	def test_Delimiters(self) -> None:
		for versionString in ("2025.06a", "2025.06.a", "2025.06-a", "2025.06+a"):
			with self.subTest(versionString=versionString):
				version = YearMonthVersion.Parse(versionString)

				self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
				self.assertEqual("a", version.Postfix)

	def test_Hash(self) -> None:
		version = CalendarVersion.Parse("2024.10.15+deadbeef")

		self.assertEqual(15, version.Micro)
		self.assertEqual("deadbeef", version.Postfix)
		self.assertEqual("2024.10.15+deadbeef", str(version))

	def test_WordStartingWithALevel(self) -> None:
		for versionString, postfix in (
			("2024.01-alphabet", "alphabet"),
			("2024.01-precise1", "precise1"),
			("2024.01-devel",    "devel"),
			("2024.01ab",        "ab")
		):
			with self.subTest(versionString=versionString):
				version = CalendarVersion.Parse(versionString)

				self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
				self.assertEqual(postfix, version.Postfix)

	def test_ReleaseLevelAndPostfix(self) -> None:
		version = CalendarVersion.Parse("2024.01rc1+deb.3")

		self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)
		self.assertEqual("deb.3", version.Postfix)

	def test_Invalid(self) -> None:
		for versionString in ("2024.01+", "2024.01-", "2024.01a1a1+", "2024.01..a1"):
			with self.subTest(versionString=versionString):
				with self.assertRaises(ValueError):
					CalendarVersion.Parse(versionString)


class RoundTrip(Testcase):
	"""The string of a version parses back into an equal version, which is written alike."""

	def test_Parse2Str2Parse(self) -> None:
		for cls, versionString in (
			(CalendarVersion,     "2024.01a1"),
			(CalendarVersion,     "2024.01-dev"),
			(CalendarVersion,     "2024.01.post2"),
			(CalendarVersion,     "2024.01.dev3"),
			(CalendarVersion,     "2024.10.15+deadbeef"),
			(CalendarVersion,     "2024.10.15.7rc1"),
			(CalendarVersion,     "v2024.01c3.post2.dev3+deb.3"),
			(YearMonthVersion,    "2025.06a"),
			(YearMonthVersion,    "2024.10.3rc1"),
			(YearWeekVersion,     "2024.42-rc1"),
			(YearReleaseVersion,  "2024.2.1"),
			(YearMonthDayVersion, "2024.10.15-dev")
		):
			with self.subTest(versionClass=cls.__name__, versionString=versionString):
				version = cls.Parse(versionString)
				reparsed = cls.Parse(str(version))

				self.assertEqual(version, reparsed)
				self.assertEqual(str(version), str(reparsed))
				self.assertEqual(hash(version), hash(reparsed))

	def test_Str(self) -> None:
		for cls, versionString, expected in (
			(CalendarVersion,     "2024.01a1",          "2024.1.alpha1"),
			(CalendarVersion,     "2024.01-pre5",       "2024.1.rc5"),
			(CalendarVersion,     "v2024.01c3",         "v2024.1.gamma3"),
			(CalendarVersion,     "2024.01-dev",        "2024.1-dev"),
			(CalendarVersion,     "2024.01.post2.dev3", "2024.1.post2.dev3"),
			(YearMonthVersion,    "v2025.06a",          "v2025.6a"),
			(YearMonthVersion,    "2024.10.3",          "2024.10.3")
		):
			with self.subTest(versionClass=cls.__name__, versionString=versionString):
				self.assertEqual(expected, str(cls.Parse(versionString)))

	def test_Constructed(self) -> None:
		"""A part is written at its position, so a build number isn't read back as a micro number."""
		for version, expected in (
			(CalendarVersion(2024, 10, build=3),           "2024.10.0.3"),
			(CalendarVersion(2024, build=3),               "2024.0.0.3"),
			(YearMonthVersion(2024, build=3),              "2024.0.3"),
			(YearMonthVersion(2024, 10, postfix="a"),      "2024.10+a"),
			(YearMonthDayVersion(2024, 10, 15, postfix="x"), "2024.10.15+x")
		):
			with self.subTest(version=expected):
				self.assertEqual(expected, str(version))
				self.assertEqual(version, version.__class__.Parse(expected))

	def test_Repr(self) -> None:
		"""A prefix isn't part of the normalized form; the release level, post, dev, build and postfix are."""
		for cls, versionString, expected in (
			(CalendarVersion,  "v2024",                 "2024.0"),
			(CalendarVersion,  "v2024.01rc1.post2+abc", "2024.1.rc1.post2+abc"),
			(YearMonthVersion, "v2025.06a",             "2025.6a"),
			(YearMonthVersion, "2024.10.3",             "2024.10.3")
		):
			with self.subTest(versionClass=cls.__name__, versionString=versionString):
				self.assertEqual(expected, repr(cls.Parse(versionString)))


class FormattingParts(Testcase):
	def test_Format(self) -> None:
		version = YearMonthVersion(2025, 6, 7, prefix="v", postfix="a", level=ReleaseLevel.ReleaseCandidate, number=2)

		self.assertEqual("v2025.6.7-rc2+a", f"{version:%p%M.%m.%b-%R%n+%P}")
		self.assertEqual("r", f"{version:%r}")

	def test_Percent(self) -> None:
		self.assertEqual("100%", f"{YearMonthVersion(2025, 6):100%%}")


class Ordering(Testcase):
	def test_Equal(self) -> None:
		self.assertEqual(YearMonthVersion.Parse("2025.06a"), YearMonthVersion(2025, 6, postfix="a"))
		self.assertEqual(YearMonthVersion.Parse("v2025.06a"), YearMonthVersion.Parse("2025.6+a"))
		self.assertEqual(CalendarVersion.Parse("2024.01a1"), CalendarVersion.Parse("2024.01-alpha.1"))

	def test_Unequal(self) -> None:
		for left, right in (
			("2025.06a",    "2025.06"),
			("2025.06a",    "2025.06b"),
			("2025.06rc1",  "2025.06"),
			("2025.06-dev", "2025.06"),
			("2025.06.3",   "2025.06")
		):
			with self.subTest(left=left, right=right):
				self.assertNotEqual(YearMonthVersion.Parse(left), YearMonthVersion.Parse(right))

	def test_Sorted(self) -> None:
		"""Pre-releases sort before the release, a postfix and a build number after it."""
		expected = [YearMonthVersion.Parse(v) for v in (
			"2025.06a1",
			"2025.06-dev",
			"2025.06rc1",
			"2025.06.dev1",
			"2025.06",
			"2025.06a",
			"2025.06b",
			"2025.06.1",
			"2025.06.post1",
			"2025.07-rc1",
			"2025.07"
		)]

		for smaller, greater in zip(expected, expected[1:]):
			with self.subTest(smaller=str(smaller), greater=str(greater)):
				self.assertLess(smaller, greater)
				self.assertLessEqual(smaller, greater)
				self.assertGreater(greater, smaller)
				self.assertGreaterEqual(greater, smaller)
				self.assertNotEqual(smaller, greater)
				self.assertFalse(greater <= smaller)

		self.assertEqual(expected, sorted(reversed(expected)))

	def test_String(self) -> None:
		version = YearMonthVersion.Parse("2025.06a")

		self.assertGreater(version, "2025.06")
		self.assertLess(version, "2025.06b")
		self.assertEqual(version, "2025.06-a")


class Hashing(Testcase):
	def test_EqualVersionsHashAlike(self) -> None:
		"""A prefix and the flags aren't compared, so they don't change the hash."""
		constructed = YearMonthVersion(2025, 6, postfix="a", flags=Flags.Dirty)
		parsed = YearMonthVersion.Parse("v2025.06a")

		self.assertEqual(constructed, parsed)
		self.assertEqual(hash(constructed), hash(parsed))
		self.assertIn(parsed, {constructed})

	def test_PartsChangeTheHash(self) -> None:
		versions = {YearMonthVersion.Parse(v) for v in ("2025.06", "2025.06a", "2025.06rc1", "2025.06.1", "2025.06+a")}

		self.assertEqual(4, len(versions))


class RangesAndSets(Testcase):
	def test_VersionRange(self) -> None:
		versionRange = VersionRange(
			YearMonthVersion.Parse("2025.06"),
			YearMonthVersion.Parse("2025.07"),
			RangeBoundHandling.UpperBoundExclusive
		)

		self.assertIn(YearMonthVersion.Parse("2025.06"), versionRange)
		self.assertIn(YearMonthVersion.Parse("2025.06a"), versionRange)
		self.assertIn(YearMonthVersion.Parse("2025.07-rc1"), versionRange)
		self.assertNotIn(YearMonthVersion.Parse("2025.06rc1"), versionRange)
		self.assertNotIn(YearMonthVersion.Parse("2025.07"), versionRange)

	def test_VersionSet(self) -> None:
		versions = [YearMonthVersion.Parse(v) for v in ("2025.06b", "2025.06", "2025.07", "2025.06a", "2025.06rc1")]
		versionSet = VersionSet(versions)

		self.assertEqual(["2025.6.rc1", "2025.6", "2025.6a", "2025.6b", "2025.7"], [str(v) for v in versionSet])
		self.assertIn(YearMonthVersion.Parse("2025.06a"), versionSet)
		self.assertNotIn(YearMonthVersion.Parse("2025.06c"), versionSet)


class PostfixSeparator(Testcase):
	"""A parsed version keeps the separator in front of its postfix; comparison and hash ignore it."""

	def test_Parse_None(self) -> None:
		version = YearMonthVersion.Parse("2025.06a")

		self.assertEqual("", version.PostfixSeparator)
		self.assertEqual("2025.6a", str(version))

	def test_Parse_Plus(self) -> None:
		version = YearMonthVersion.Parse("2025.06+build.5")

		self.assertEqual("+", version.PostfixSeparator)
		self.assertEqual("2025.6+build.5", str(version))

	def test_Parse_Dash(self) -> None:
		version = YearMonthVersion.Parse("2025.06-foo")

		self.assertEqual("-", version.PostfixSeparator)
		self.assertEqual("2025.6-foo", str(version))

	def test_Parse_Dot(self) -> None:
		version = CalendarVersion.Parse("2025.06.foo")

		self.assertEqual(".", version.PostfixSeparator)
		self.assertEqual("2025.6.foo", str(version))

	def test_Default(self) -> None:
		version = YearMonthVersion(2025, 6, postfix="a")

		self.assertEqual("+", version.PostfixSeparator)
		self.assertEqual("2025.6+a", str(version))

	def test_Construction(self) -> None:
		self.assertEqual("2025.6a", str(YearMonthVersion(2025, 6, postfix="a", postfixSeparator="")))

	def test_Equality(self) -> None:
		self.assertEqual(YearMonthVersion.Parse("2025.06a"), YearMonthVersion.Parse("2025.06+a"))
		self.assertEqual(hash(YearMonthVersion.Parse("2025.06a")), hash(YearMonthVersion.Parse("2025.06+a")))

	def test_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = YearMonthVersion(2025, 6, postfix="a", postfixSeparator=1)

		self.assertEqual("Parameter 'postfixSeparator' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Value(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = YearMonthVersion(2025, 6, postfix="a", postfixSeparator="/")

		self.assertEqual("Parameter 'postfixSeparator' is none of '+', '.', '-' and ''.", str(context.exception))
		self.assertListEqual(["Got value '/'."], context.exception.__notes__)

	def test_NotReadBack_Digit(self) -> None:
		"""A postfix starting with a digit would continue the month."""
		with self.assertRaises(ValueError) as context:
			_ = YearMonthVersion(2025, 6, postfix="5", postfixSeparator="")

		self.assertEqual(
			"Parameter 'postfixSeparator' is '', but the postfix wouldn't be read back.",
			str(context.exception)
		)

	def test_NotReadBack_ReleaseLevel(self) -> None:
		"""Without a ``+``, the postfix ``a1`` reads as alpha release 1."""
		with self.assertRaises(ValueError):
			_ = YearMonthVersion(2025, 6, postfix="a1", postfixSeparator="")

	def test_NotReadBack_Development(self) -> None:
		"""After a ``-``, the postfix ``dev`` reads as a development release."""
		with self.assertRaises(ValueError):
			_ = YearMonthVersion(2025, 6, postfix="dev", postfixSeparator="-")

