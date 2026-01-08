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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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

from pyTooling.Versioning import SemanticVersion, PythonVersion, CalendarVersion, VersionRange, RangeBoundHandling

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_SemVer_SemVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertIs(v1, vr.LowerBound)
		self.assertIs(v2, vr.UpperBound)
		self.assertEqual(RangeBoundHandling.BothBoundsInclusive, vr.BoundHandling)

	def test_SemVer_SemVer_Reverse(self) -> None:
		v1 = SemanticVersion(2, 0, 0)
		v2 = SemanticVersion(1, 0, 0)

		with self.assertRaises(ValueError) as ex:
			_ = VersionRange(v1, v2)

	def test_SemVer_Tuple(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = (2, 0, 0)

		with self.assertRaises(TypeError) as ex:
			_ = VersionRange(v1, v2)

	def test_Tuple_SemVer(self) -> None:
		v1 = (1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		with self.assertRaises(TypeError) as ex:
			_ = VersionRange(v1, v2)

	def test_SemVer_CalVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = CalendarVersion(2, 0, 0)

		with self.assertRaises(TypeError) as ex:
			_ = VersionRange(v1, v2)

	def test_CalVer_SemVer(self) -> None:
		v1 = CalendarVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		with self.assertRaises(TypeError) as ex:
			_ = VersionRange(v1, v2)

	def test_SemVer_PyVer(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = PythonVersion(2, 0, 0)

		vr = VersionRange(v1, v2, RangeBoundHandling.LowerBoundExclusive)

		self.assertIs(v1, vr.LowerBound)
		self.assertIs(v2, vr.UpperBound)
		self.assertEqual(RangeBoundHandling.LowerBoundExclusive, vr.BoundHandling)

	def test_PyVer_SemVer(self) -> None:
		v1 = PythonVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2, RangeBoundHandling.UpperBoundExclusive)

		self.assertIs(v1, vr.LowerBound)
		self.assertIs(v2, vr.UpperBound)
		self.assertEqual(RangeBoundHandling.UpperBoundExclusive, vr.BoundHandling)


class Comparison(TestCase):
	def test_LessThan(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertTrue(SemanticVersion(0, 5, 0) < vr)
		self.assertFalse(SemanticVersion(1, 5, 0) < vr)
		self.assertFalse(SemanticVersion(2, 5, 0) < vr)

		self.assertFalse(vr < SemanticVersion(0, 5, 0))
		self.assertFalse(vr < SemanticVersion(1, 5, 0))
		self.assertTrue(vr < SemanticVersion(2, 5, 0))

	def test_LessThan_WrongType(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)
		vr = VersionRange(v1, v2)

		with self.assertRaises(TypeError) as ex:
			_ = vr < (2, 5, 0)

	def test_LessThanOrEqual(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertTrue(SemanticVersion(0, 5, 0) <= vr)
		self.assertTrue(SemanticVersion(1, 0, 0) <= vr)
		self.assertFalse(SemanticVersion(1, 5, 0) <= vr)
		self.assertFalse(SemanticVersion(2, 0, 0) <= vr)
		self.assertFalse(SemanticVersion(2, 5, 0) <= vr)

		self.assertFalse(vr <= SemanticVersion(0, 5, 0))
		self.assertFalse(vr <= SemanticVersion(1, 0, 0))
		self.assertFalse(vr <= SemanticVersion(1, 5, 0))
		self.assertTrue(vr <= SemanticVersion(2, 0, 0))
		self.assertTrue(vr <= SemanticVersion(2, 5, 0))

	def test_LessThanOrEqual_Exclusive(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2, RangeBoundHandling.BothBoundsExclusive)

		self.assertTrue(SemanticVersion(0, 5, 0) <= vr)
		self.assertFalse(SemanticVersion(1, 0, 0) <= vr)
		self.assertFalse(SemanticVersion(1, 5, 0) <= vr)
		self.assertFalse(SemanticVersion(2, 0, 0) <= vr)
		self.assertFalse(SemanticVersion(2, 5, 0) <= vr)

		self.assertFalse(vr <= SemanticVersion(0, 5, 0))
		self.assertFalse(vr <= SemanticVersion(1, 0, 0))
		self.assertFalse(vr <= SemanticVersion(1, 5, 0))
		self.assertFalse(vr <= SemanticVersion(2, 0, 0))
		self.assertTrue(vr <= SemanticVersion(2, 5, 0))

	def test_GreaterThan(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertFalse(SemanticVersion(0, 5, 0) > vr)
		self.assertFalse(SemanticVersion(1, 5, 0) > vr)
		self.assertTrue(SemanticVersion(2, 5, 0) > vr)

		self.assertTrue(vr > SemanticVersion(0, 5, 0))
		self.assertFalse(vr > SemanticVersion(1, 5, 0))
		self.assertFalse(vr > SemanticVersion(2, 5, 0))

	def test_GreaterThanOrEqual(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertFalse(SemanticVersion(0, 5, 0) >= vr)
		self.assertFalse(SemanticVersion(1, 0, 0) >= vr)
		self.assertFalse(SemanticVersion(1, 5, 0) >= vr)
		self.assertTrue(SemanticVersion(2, 0, 0) >= vr)
		self.assertTrue(SemanticVersion(2, 5, 0) >= vr)

		self.assertTrue(vr >= SemanticVersion(0, 5, 0))
		self.assertTrue(vr >= SemanticVersion(1, 0, 0))
		self.assertFalse(vr >= SemanticVersion(1, 5, 0))
		self.assertFalse(vr >= SemanticVersion(2, 0, 0))
		self.assertFalse(vr >= SemanticVersion(2, 5, 0))

	def test_In(self) -> None:
		v1 = SemanticVersion(1, 0, 0)
		v2 = SemanticVersion(2, 0, 0)

		vr = VersionRange(v1, v2)

		self.assertTrue(SemanticVersion(0, 5, 0) not in vr)
		self.assertTrue(SemanticVersion(1, 0, 0)     in vr)
		self.assertTrue(SemanticVersion(1, 5, 0)     in vr)
		self.assertTrue(SemanticVersion(2, 0, 0)     in vr)
		self.assertTrue(SemanticVersion(2, 5, 0) not in vr)


class Intersection(TestCase):
	def test_AInsideB(self) -> None:
		vA1 = SemanticVersion(2, 0, 0)
		vA2 = SemanticVersion(3, 0, 0)

		vrA = VersionRange(vA1, vA2)

		vB1 = SemanticVersion(1, 0, 0)
		vB2 = SemanticVersion(4, 0, 0)

		vrB = VersionRange(vB1, vB2)

		intersection = vrA & vrB

		self.assertEqual(vA1, intersection.LowerBound)
		self.assertEqual(vA2, intersection.UpperBound)

	def test_BInsideA(self) -> None:
		vA1 = SemanticVersion(1, 0, 0)
		vA2 = SemanticVersion(4, 0, 0)

		vrA = VersionRange(vA1, vA2)

		vB1 = SemanticVersion(2, 0, 0)
		vB2 = SemanticVersion(3, 0, 0)

		vrB = VersionRange(vB1, vB2)

		intersection = vrA & vrB

		self.assertEqual(vB1, intersection.LowerBound)
		self.assertEqual(vB2, intersection.UpperBound)

	def test_ALeftInnerB(self) -> None:
		vA1 = SemanticVersion(1, 0, 0)
		vA2 = SemanticVersion(3, 0, 0)

		vrA = VersionRange(vA1, vA2)

		vB1 = SemanticVersion(2, 0, 0)
		vB2 = SemanticVersion(4, 0, 0)

		vrB = VersionRange(vB1, vB2)

		intersection = vrA & vrB

		self.assertEqual(vB1, intersection.LowerBound)
		self.assertEqual(vA2, intersection.UpperBound)

	def test_ARightInnerB(self) -> None:
		vA1 = SemanticVersion(3, 0, 0)
		vA2 = SemanticVersion(5, 0, 0)

		vrA = VersionRange(vA1, vA2)

		vB1 = SemanticVersion(2, 0, 0)
		vB2 = SemanticVersion(4, 0, 0)

		vrB = VersionRange(vB1, vB2)

		intersection = vrA & vrB

		self.assertEqual(vA1, intersection.LowerBound)
		self.assertEqual(vB2, intersection.UpperBound)
