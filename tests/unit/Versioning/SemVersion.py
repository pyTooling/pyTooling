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

from pyTooling.Versioning import Flags, ReleaseLevel, SemanticVersion, WordSizeValidator, MaxValueValidator


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Major(self):
		version = SemanticVersion(1)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(0, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(0, version.Patch)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual(0, version.ReleaseNumber)
		self.assertEqual(0, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinor(self):
		version = SemanticVersion(1, 2)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(0, version.Patch)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual(0, version.ReleaseNumber)
		self.assertEqual(0, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicro(self):
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual(0, version.ReleaseNumber)
		self.assertEqual(0, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevel(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(0, version.ReleaseNumber)
		self.assertEqual(0, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumber(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(0, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPost(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(0, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDev(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(0, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDevBuild(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7)

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(7, version.Build)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDevBuildPostfix(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p")

		self.assertEqual("", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(7, version.Build)
		self.assertEqual("p", version.Postfix)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDevBuildPostfixPrefix(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v")

		self.assertEqual("v", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(7, version.Build)
		self.assertEqual("p", version.Postfix)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDevBuildPostfixPrefixHash(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v", hash="abcdef")

		self.assertEqual("v", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(7, version.Build)
		self.assertEqual("p", version.Postfix)
		self.assertEqual(Flags.NoVCS, version.Flags)

	def test_MajorMinorMicroReleaseLevelNumberPostDevBuildPostfixPrefixHashFlags(self):
		version = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v", hash="abcdef", flags=Flags.Git)

		self.assertEqual("v", version.Prefix)
		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(3, version.Patch)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(4, version.ReleaseNumber)
		self.assertEqual(5, version.Post)
		self.assertEqual(6, version.Dev)
		self.assertEqual(7, version.Build)
		self.assertEqual("p", version.Postfix)
		self.assertEqual("abcdef", version.Hash)
		self.assertEqual(Flags.Git, version.Flags)

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

	def test_Major_Micro_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, "3")

	def test_Major_Micro_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2,-3)

	def test_Major_ReleaseLevel_None(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, None)

	def test_Major_ReleaseLevel_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, "RL")

	def test_Major_ReleaseLevel_Final(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Final, 1)

	def test_Major_Number_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, "4")

	def test_Major_Number_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, -4)

	def test_Major_Postv_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, "5")

	def test_Major_Post_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, -5)

	def test_Major_Dev_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, "6")

	def test_Major_Dev_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, -6)

	def test_Major_Build_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build="7")

	def test_Major_Build_Negative(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=-7)

	def test_Major_Postfix_Integer(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix=8)

	def test_Major_Prefix_Integer(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix=9)

	def test_Major_Hash_Integer(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v", hash=10)

	def test_Major_Flags_None(self):
		with self.assertRaises(ValueError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v", hash="ab", flags=None)

	def test_Major_Flags_String(self):
		with self.assertRaises(TypeError):
			_ = SemanticVersion(1, 2, 3, ReleaseLevel.Alpha, 4, 5, 6, build=7, postfix="p", prefix="v", hash="ab", flags="d")


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
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_String_MajorMinor(self) -> None:
		version = SemanticVersion.Parse("1.2")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_String_MajorMinorMicro(self) -> None:
		version = SemanticVersion.Parse("1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_vString(self) -> None:
		version = SemanticVersion.Parse("v1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_iString(self) -> None:
		version = SemanticVersion.Parse("i1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_rString(self) -> None:
		version = SemanticVersion.Parse("r1.2.3")

		self.assertEqual(1, version.Major)
		self.assertEqual(2, version.Minor)
		self.assertEqual(3, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)

	def test_MajorMinorDev(self) -> None:
		version = SemanticVersion.Parse("0.6-dev")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Development, version.ReleaseLevel)
		self.assertEqual(0, version.ReleaseNumber)

	def test_MajorMinorDevelopment(self) -> None:
		version = SemanticVersion.Parse("0.6.dev10")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Final, version.ReleaseLevel)
		self.assertEqual(10, version.Dev)

	def test_MajorMinorAlpha(self) -> None:
		version = SemanticVersion.Parse("0.6a1")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Alpha, version.ReleaseLevel)
		self.assertEqual(1, version.ReleaseNumber)

	def test_MajorMinorBeta(self) -> None:
		version = SemanticVersion.Parse("0.6b5")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Beta, version.ReleaseLevel)
		self.assertEqual(5, version.ReleaseNumber)

	def test_MajorMinorGamma(self) -> None:
		version = SemanticVersion.Parse("0.6c3")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.Gamma, version.ReleaseLevel)
		self.assertEqual(3, version.ReleaseNumber)

	def test_MajorMinorReleaseCandidate(self) -> None:
		version = SemanticVersion.Parse("0.6rc2")

		self.assertEqual(0, version.Major)
		self.assertEqual(6, version.Minor)
		self.assertEqual(0, version.Micro)
		self.assertEqual(ReleaseLevel.ReleaseCandidate, version.ReleaseLevel)
		self.assertEqual(2, version.ReleaseNumber)


class HashVersions(TestCase):
	def test_SemanticVersion(self):
		version = SemanticVersion.Parse("v1.2.3")

		self.assertIsNotNone(version.__hash__())


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

	def test_Minimum(self) -> None:
		l = [
			# ver      req     exp
			("0.0.1", "0.0.0", True),
			("0.0.1", "0.0.1", True),
			("0.0.1", "0.0.2", False),
			("0.1.0", "0.0", True),
			("0.1.0", "0.1", True),
			("0.1.0", "0.2", False),
			("1.0.0", "0", True),
			("1.0.0", "1", True),
			("1.0.0", "2", False),
		]

		for ver, req, exp in l:
			with self.subTest(minimum=(ver, req)):
				version = SemanticVersion.Parse(ver)
				requirement = SemanticVersion.Parse(req)
				self.assertEqual(exp, version >> requirement, f"{version} ~= {requirement}")


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

	def test_Minimum(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(ValueError):
			_ = version >> None


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

	def test_Minimum(self):
		version = SemanticVersion(1, 2, 3)

		self.assertTrue(version >> "1.2.3")


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

	def test_Minimum(self):
		version = SemanticVersion(1, 2, 3)

		self.assertTrue(version >> 1)


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

	def test_Minimum(self):
		version = SemanticVersion(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = version >> 1.2


class ValidatedWordSize(TestCase):
	def test_All8Bit_AllInRange(self) -> None:
		version = SemanticVersion.Parse("12.64.255", WordSizeValidator(8))

		self.assertEqual(12, version.Major)
		self.assertEqual(64, version.Minor)
		self.assertEqual(255, version.Micro)

	def test_All8Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("1203.64.255", WordSizeValidator(8))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All8Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.640.255", WordSizeValidator(8))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_All8Bit_MicroOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.64.256", WordSizeValidator(8))

		self.assertIn("Version.Micro", str(ex.exception))

	def test_358Bits_AllInRange(self) -> None:
		version = SemanticVersion.Parse("7.31.255", WordSizeValidator(2, majorBits=3, minorBits=5, microBits=8))

		self.assertEqual(7, version.Major)
		self.assertEqual(31, version.Minor)
		self.assertEqual(255, version.Micro)

	def test_358Bit_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("8.31.255", WordSizeValidator(majorBits=3, minorBits=5, microBits=8))

		self.assertIn("Version.Major", str(ex.exception))

	def test_358Bit_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("7.32.255", WordSizeValidator(8, majorBits=3, minorBits=5))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_358Bit_MicroOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("7.31.256", WordSizeValidator(8, majorBits=3, minorBits=5))

		self.assertIn("Version.Micro", str(ex.exception))


class ValidatedMaxValue(TestCase):
	def test_All255_AllInRange(self) -> None:
		version = SemanticVersion.Parse("12.64.255", MaxValueValidator(255))

		self.assertEqual(12, version.Major)
		self.assertEqual(64, version.Minor)
		self.assertEqual(255, version.Micro)

	def test_All255_MajorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("1203.64.255", MaxValueValidator(255))

		self.assertIn("Version.Major", str(ex.exception))

	def test_All255_MinorOutOfRange(self) -> None:
		with self.assertRaises(ValueError) as ex:
			_ = SemanticVersion.Parse("12.640.255",  MaxValueValidator(255))

		self.assertIn("Version.Minor", str(ex.exception))

	def test_All255_MicroOutOfRange(self) -> None:
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

	def test_MajorMinorMicro(self) -> None:
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

	def test_MajorMinorMicro(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("1.2.3", str(version))

	def test_MajorMinorMicroPrefix(self) -> None:
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

	def test_Major_Prefix(self) -> None:
		version = SemanticVersion(1, prefix="i")

		self.assertEqual("i", f"{version:%p}")

	def test_Minor(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("2", f"{version:%m}")

	def test_Micro(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("3", f"{version:%u}")

	def test_Build(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual("0", f"{version:%b}")

	def test_ReleaseLevel_Short(self) -> None:
		version = SemanticVersion(1, 2, 3, level=ReleaseLevel.Alpha)

		self.assertEqual("a", f"{version:%r}")

	def test_ReleaseLevel_Short_Number(self) -> None:
		version = SemanticVersion(1, 2, 3, level=ReleaseLevel.Alpha)

		self.assertEqual("a0", f"{version:%r%n}")

	def test_ReleaseLevel_Long(self) -> None:
		version = SemanticVersion(1, 2, 3, level=ReleaseLevel.Alpha)

		self.assertEqual("alpha", f"{version:%R}")

	def test_ReleaseLevel_Long_Number(self) -> None:
		version = SemanticVersion(1, 2, 3, level=ReleaseLevel.Alpha, number=4)

		self.assertEqual("alpha-4", f"{version:%R-%n}")

	def test_FullVersion1(self) -> None:
		version = SemanticVersion(1, 2, 3, build=0, prefix="v")

		self.assertEqual("v1.2.3.0", f"{version:%p%M.%m.%u.%b}")

	def test_FullVersion2(self) -> None:
		version = SemanticVersion(1, 2, 3, ReleaseLevel.ReleaseCandidate, 3, prefix="r")

		self.assertEqual("r1.2.3.rc3", f"{version:%p%M.%m.%u.%R%n}")

	def test_FullVersion3(self) -> None:
		version = SemanticVersion(1, 2, 3, ReleaseLevel.ReleaseCandidate, 3, prefix="v", postfix="deb25")

		self.assertEqual("v1.2.3-rc3+deb25", f"{version:%p%M.%m.%u-%R%n+%P}")


class RoundTrip(TestCase):
	def test_Parse2Str(self) -> None:
		l = [
			"1",
			"11.2",
			"11.12.3",
			"11.12.13.4",
			"v1",
			"v1.12",
			"v1.2.13",
			"v1.2.3.14",
			"r1.0",
			"i1.0",
			"i1.0+deb3",
			"rev1.2",
			"rev1.2+deb3",
			"v1.2.3-dev",
			"v1.2.3.dev23",
			"v1.2.3.alpha1",
			"v1.2.3.beta1",
			"v1.2.3.rc1",
			"v1.2.3.rc1+deb25",
			"1.2.rc3.post2",
			"1.2.rc3.post2.dev4",
			"v1.2.3.alpha4.post5.dev6+deb11u3"
		]

		for ver in l:
			with self.subTest(version=ver):
				version = SemanticVersion.Parse(ver)
				self.assertEqual(ver, str(version), ver)

	def test_Parse2Str_Normalizing(self) -> None:
		ver = "01.02.03.04"
		version = SemanticVersion.Parse(ver)
		self.assertEqual(ver.replace("0", ""), str(version), ver)

		ver = "v01.02.03.rc04.post05.dev06+deb07"
		version = SemanticVersion.Parse(ver)
		self.assertEqual(ver.replace("0", "", 6), str(version), ver)
