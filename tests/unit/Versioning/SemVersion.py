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

from pyTooling.Versioning import Flags, SemanticVersion, WordSizeValidator, MaxValueValidator


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Major(self):
		version = SemanticVersion(1)

		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)
		self.assertEqual(0, version.Patch)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinor(self):
		version = SemanticVersion(1, 2)

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(0, version.Patch)
		self.assertEqual(0, version.Build)

	def test_MajorMinorPatch(self):
		version = SemanticVersion(1, 2, 3)

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Patch)
		self.assertEqual(0, version.Build)

	def test_Major_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion("1")

	def test_Major_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(-1)

	def test_Major_Minor_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, "2")

	def test_Major_Minor_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, -2)


class Parsing(TestCase):
	def test_None(self) -> None:
		with self.assertRaises(ValueError):
			SemanticVersion.Parse(None)

	def test_EmptyString(self) -> None:
		with self.assertRaises(ValueError):
			SemanticVersion.Parse("")

	def test_OtherType(self) -> None:
		with self.assertRaises(TypeError):
			SemanticVersion.Parse(1)

	def test_InvalidString(self) -> None:
		with self.assertRaises(ValueError):
			SemanticVersion.Parse("None")

	def test_String_Major(self) -> None:
		version = SemanticVersion.Parse("1")

		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)
		self.assertEqual(0, version.Patch)

	def test_String_MajorMinor(self) -> None:
		version = SemanticVersion.Parse("1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(0, version.Patch)

	def test_String_MajorMinorPatch(self) -> None:
		version = SemanticVersion.Parse("1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Patch)

	def test_vString(self) -> None:
		version = SemanticVersion.Parse("v1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Patch)

	def test_iString(self) -> None:
		version = SemanticVersion.Parse("i1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Patch)

	def test_rString(self) -> None:
		version = SemanticVersion.Parse("r1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Patch)


class CompareVersions(TestCase):
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
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
				v1 = SemanticVersion.Parse(t[0])
				v2 = SemanticVersion.Parse(t[1])
				self.assertGreaterEqual(v1, v2)


class CompareNone(TestCase):
	def test_Equal(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version == None

	def test_Unequal(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version != None

	def test_LessThan(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version < None

	def test_LessThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version <= None

	def test_GreaterThan(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version > None

	def test_GreaterThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version >= None


class CompareString(TestCase):
	def test_Equal(self):
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1.2.3", version)

	def test_Unequal(self):
		version = SemanticVersion(1, 2, 3)

		self.assertNotEqual("1.2.4", version)

	def test_LessThan(self):
		version = SemanticVersion(1, 2, 3)

		self.assertLess("1.2.2", version)

	def test_LessThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		self.assertLessEqual("1.2.3", version)

	def test_GreaterThan(self):
		version = SemanticVersion(1, 2, 3)

		self.assertGreater("1.2.4", version)

	def test_GreaterThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		self.assertGreaterEqual("1.2.3", version)


class CompareInteger(TestCase):
	def test_Equal(self):
		version = SemanticVersion(1)

		self.assertEqual(1, version)

	def test_Unequal(self):
		version = SemanticVersion(1)

		self.assertNotEqual(2, version)

	def test_LessThan(self):
		version = SemanticVersion(1, 2, 3)

		self.assertLess(0, version)

	def test_LessThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		self.assertLessEqual(1, version)

	def test_GreaterThan(self):
		version = SemanticVersion(1, 2, 3)

		self.assertGreater(3, version)

	def test_GreaterThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		self.assertGreaterEqual(2, version)


class CompareOtherType(TestCase):
	def test_Equal(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version == 1.2

	def test_Unequal(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version != 1.2

	def test_LessThan(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version < 1.2

	def test_LessThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version <= 1.2

	def test_GreaterThan(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version > 1.2

	def test_GreaterThanOrEqual(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version >= 1.2


class ValidatedWordSize(TestCase):
	def test_All8Bit_AllInRange(self) -> None:
		version = SemanticVersion.Parse("12.64.255", WordSizeValidator(8))

		self.assertEqual(12, version.Major)
		self.assertEqual(64, version.Minor)
		self.assertEqual(255, version.Patch)

	def test_All8Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("1203.64.255", WordSizeValidator(8))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All8Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.640.255", WordSizeValidator(8))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_All8Bit_PatchOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.64.256", WordSizeValidator(8))

		self.assertIn("Version.Micro", str(ex.exception))

	def test_358Bits_AllInRange(self) -> None:
		version = SemanticVersion.Parse("7.31.255", WordSizeValidator(2, majorBits=3, minorBits=5, microBits=8))

		self.assertEqual(7, version.Major)
		self.assertEqual(31, version.Minor)
		self.assertEqual(255, version.Patch)

	def test_358Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("8.31.255", WordSizeValidator(majorBits=3, minorBits=5, microBits=8))

		self.assertIn("Version.Major", str(ex.exception))

	def test_358Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("7.32.255", WordSizeValidator(8, majorBits=3, minorBits=5))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_358Bit_PatchOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("7.31.256", WordSizeValidator(8, majorBits=3, minorBits=5))

		self.assertIn("Version.Micro", str(ex.exception))


class ValidatedMaxValue(TestCase):
	def test_All255_AllInRange(self) -> None:
		version = SemanticVersion.Parse("12.64.255", MaxValueValidator(255))

		self.assertEqual(12, version.Major)
		self.assertEqual(64, version.Minor)
		self.assertEqual(255, version.Patch)

	def test_All255_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("1203.64.255", MaxValueValidator(255))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All255_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.640.255",  MaxValueValidator(255))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_All255_PatchOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.64.256",  MaxValueValidator(255))

		self.assertIn("Version.Micro", str(ex.exception))


class FormattingUsingRepr(TestCase):
	def test_Major(self) -> None:
		version = SemanticVersion(1)

		self.assertEqual("1.0.0", repr(version))

	def test_MajorPrefix(self) -> None:
		version = SemanticVersion(1)

		self.assertEqual("1.0.0", repr(version))

	def test_MajorMinor(self) -> None:
		version = SemanticVersion(1, 2)

		self.assertEqual("1.2.0", repr(version))

	def test_MajorMinorPatch(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1.2.3", repr(version))


class FormattingUsingStr(TestCase):
	def test_Major(self) -> None:
		version = SemanticVersion(1)

		self.assertEqual("1", str(version))

	def test_MajorPrefix(self) -> None:
		version = SemanticVersion(1, prefix="v")

		self.assertEqual("v1", str(version))

	def test_MajorMinor(self) -> None:
		version = SemanticVersion(1, 2)

		self.assertEqual("1.2", str(version))

	def test_MajorMinorPatch(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1.2.3", str(version))

	def test_MajorMinorPatchPrefix(self) -> None:
		version = SemanticVersion(1, 2, 3, prefix="v")

		self.assertEqual("v1.2.3", str(version))


class FormattingUsingFormat(TestCase):
	def test_Empty(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1.2.3", f"{version:}")
		self.assertEqual(str(version), f"{version:}")

	def test_OtherFormat(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("hello world", f"{version:hello world}")

	def test_Percent(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("hello%world", f"{version:hello%%world}")

	def test_Major(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1", f"{version:%M}")

	def test_Minor(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("2", f"{version:%m}")

	def test_Patch(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("3", f"{version:%u}")

	def test_Build(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("0", f"{version:%b}")

	def test_FullVersion(self) -> None:
		version = SemanticVersion(1, 2, 3, prefix="v")

		self.assertEqual("v1.2.3", f"{version:%P%M.%m.%u}")
