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
"""
Unit tests for :class:`pyTooling.Versioning.VersionRange`: comparison and intersection of ranges.
"""
from pyTooling.Versioning import SemanticVersion, PythonVersion, CalendarVersion, VersionRange, RangeBoundHandling
from pyTooling.Testing    import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
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


class Comparison(Testcase):
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


class Intersection(Testcase):
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

	def test_Disjoint(self) -> None:
		"""Two ranges that don't overlap have an empty intersection, and the exception says which bound is where."""
		vrA = VersionRange(SemanticVersion(1, 0, 0), SemanticVersion(2, 0, 0))
		vrB = VersionRange(SemanticVersion(3, 0, 0), SemanticVersion(4, 0, 0))

		with self.assertRaises(ValueError) as exceptionCapture:
			vrA & vrB

		self.assertEqual("The intersection of both version ranges is empty.", str(exceptionCapture.exception))
		self.assertIn("3.0.0", exceptionCapture.exception.__notes__[0])
		self.assertIn("2.0.0", exceptionCapture.exception.__notes__[1])

	def test_DisjointIsCommutative(self) -> None:
		"""An intersection doesn't depend on operand order, so neither does the exception describing it."""
		vrA = VersionRange(SemanticVersion(1, 0, 0), SemanticVersion(2, 0, 0))
		vrB = VersionRange(SemanticVersion(3, 0, 0), SemanticVersion(4, 0, 0))

		with self.assertRaises(ValueError) as forwards:
			vrA & vrB

		with self.assertRaises(ValueError) as backwards:
			vrB & vrA

		self.assertEqual(forwards.exception.__notes__, backwards.exception.__notes__)

	def test_Disjoint_Reversed(self) -> None:
		vrA = VersionRange(SemanticVersion(3, 0, 0), SemanticVersion(4, 0, 0))
		vrB = VersionRange(SemanticVersion(1, 0, 0), SemanticVersion(2, 0, 0))

		with self.assertRaises(ValueError) as exceptionCapture:
			vrA & vrB

		self.assertEqual("The intersection of both version ranges is empty.", str(exceptionCapture.exception))
		# The notes name the highest lower bound and the lowest upper bound, whichever operand each came from, so
		# they read the same for 'vrA & vrB' and 'vrB & vrA'.
		self.assertIn("3.0.0", exceptionCapture.exception.__notes__[0])
		self.assertIn("2.0.0", exceptionCapture.exception.__notes__[1])


class OpenBounds(Testcase):
	"""A bound may be ``None``, which leaves the range unbounded in that direction."""

	@staticmethod
	def _v(version: str) -> SemanticVersion:
		return SemanticVersion.Parse(version)

	def test_ARangeCanBeOpenInEitherDirection(self) -> None:
		lower, upper = self._v("1.0.0"), self._v("2.0.0")

		self.assertIsNone(VersionRange(lower, None).UpperBound)
		self.assertIsNone(VersionRange(None, upper).LowerBound)
		self.assertIsNone(VersionRange(None, None).LowerBound)
		self.assertIsNone(VersionRange(None, None).UpperBound)

	def test_MembershipSkipsAnOpenBound(self) -> None:
		lower, upper = self._v("1.0.0"), self._v("2.0.0")

		for name, versionRange, expected in (
			("closed", VersionRange(lower, upper), (False, True, True, True, False)),
			("openUp", VersionRange(lower, None),  (False, True, True, True, True)),
			("openDown", VersionRange(None, upper), (True, True, True, True, False)),
			("unbounded", VersionRange(None, None), (True, True, True, True, True)),
		):
			with self.subTest(range=name):
				actual = tuple(self._v(v) in versionRange for v in ("0.9.0", "1.0.0", "1.5.0", "2.0.0", "9.9.9"))

				self.assertEqual(expected, actual)

	def test_BoundHandlingStillAppliesToThePresentBound(self) -> None:
		lower = self._v("1.0.0")
		versionRange = VersionRange(lower, None, RangeBoundHandling.LowerBoundExclusive)

		self.assertNotIn(lower, versionRange)
		self.assertIn(self._v("1.0.1"), versionRange)

	def test_AnUnboundedRangeContainsEveryVersion(self) -> None:
		versionRange = VersionRange(None, None)

		for version in ("0.0.1", "1.2.3", "999.0.0"):
			with self.subTest(version=version):
				self.assertIn(self._v(version), versionRange)

	def test_ARangeOpenInADirectionIsNeverBeyondAVersionThatWay(self) -> None:
		"""``[1.0.0,)`` reaches past every version, so it is never entirely below one."""
		openUp = VersionRange(self._v("1.0.0"), None)
		openDown = VersionRange(None, self._v("2.0.0"))

		self.assertFalse(openUp < self._v("9.9.9"))
		self.assertFalse(openUp <= self._v("9.9.9"))
		self.assertTrue(openUp > self._v("0.5.0"))

		self.assertFalse(openDown > self._v("0.0.1"))
		self.assertFalse(openDown >= self._v("0.0.1"))
		self.assertTrue(openDown < self._v("9.9.9"))

	def test_AnOpenBoundIsIgnoredWhenIntersecting(self) -> None:
		"""An open lower bound is the lowest of all, an open upper bound the highest."""
		for name, left, right, lower, upper in (
			("openUp & openDown", VersionRange(self._v("1.0.0"), None), VersionRange(None, self._v("3.0.0")),
			 "1.0.0", "3.0.0"),
			("openUp & openUp",   VersionRange(self._v("1.0.0"), None), VersionRange(self._v("2.0.0"), None),
			 "2.0.0", None),
			("unbounded & closed", VersionRange(None, None), VersionRange(self._v("1.0.0"), self._v("2.0.0")),
			 "1.0.0", "2.0.0"),
		):
			with self.subTest(case=name):
				intersection = left & right

				self.assertEqual(lower, None if intersection.LowerBound is None else str(intersection.LowerBound))
				self.assertEqual(upper, None if intersection.UpperBound is None else str(intersection.UpperBound))

	def test_TwoUnboundedRangesIntersectToAnUnboundedRange(self) -> None:
		intersection = VersionRange(None, None) & VersionRange(None, None)

		self.assertIsNone(intersection.LowerBound)
		self.assertIsNone(intersection.UpperBound)

	def test_ABoundCanBeOpenedAfterwards(self) -> None:
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))
		versionRange.UpperBound = None

		self.assertIsNone(versionRange.UpperBound)
		self.assertIn(self._v("9.9.9"), versionRange)

	def test_ANonVersionBoundIsStillRejected(self) -> None:
		with self.assertRaises(TypeError):
			VersionRange("1.0.0", None)

		with self.assertRaises(TypeError):
			VersionRange(None, "2.0.0")

	def test_ClosedRangeChecksStillApply(self) -> None:
		"""Relating the two bounds is only skipped when one of them is open."""
		with self.assertRaises(ValueError):
			VersionRange(self._v("2.0.0"), self._v("1.0.0"))


class BoundInvariant(Testcase):
	"""Reassigning a bound keeps the invariant the constructor establishes."""

	@staticmethod
	def _v(version: str) -> SemanticVersion:
		return SemanticVersion.Parse(version)

	def test_ALowerBoundAboveTheUpperOneIsRejected(self) -> None:
		"""``__init__`` rejects it, so the setter has to as well - otherwise the range silently contains nothing."""
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))

		with self.assertRaises(ValueError):
			versionRange.LowerBound = self._v("5.0.0")

		self.assertEqual("1.0.0", str(versionRange.LowerBound))

	def test_AnUpperBoundBelowTheLowerOneIsRejected(self) -> None:
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))

		with self.assertRaises(ValueError):
			versionRange.UpperBound = self._v("0.5.0")

		self.assertEqual("2.0.0", str(versionRange.UpperBound))

	def test_EqualBoundsAreAllowed(self) -> None:
		"""``[1.0.0, 1.0.0]`` is a range of one version, which the constructor accepts too."""
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))
		versionRange.UpperBound = self._v("1.0.0")

		self.assertIn(self._v("1.0.0"), versionRange)

	def test_AnUnboundBoundRelatesToNothing(self) -> None:
		"""With one bound unbound there is no ordering to violate, so any value is admissible."""
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))
		versionRange.UpperBound = None
		versionRange.LowerBound = self._v("5.0.0")

		self.assertEqual("5.0.0", str(versionRange.LowerBound))
		self.assertIsNone(versionRange.UpperBound)

	def test_UnboundingEitherEndIsAlwaysAllowed(self) -> None:
		versionRange = VersionRange(self._v("1.0.0"), self._v("2.0.0"))
		versionRange.LowerBound = None
		versionRange.UpperBound = None

		self.assertIn(self._v("9.9.9"), versionRange)


class TypeCompatibility(Testcase):
	"""One rule decides which versions relate to a range: the one ``__init__`` applies between its bounds."""

	@staticmethod
	def _range() -> VersionRange:
		return VersionRange(SemanticVersion.Parse("1.0.0"), SemanticVersion.Parse("2.0.0"))

	def test_TheConstructorAcceptsASubclassAsTheOtherBound(self) -> None:
		""":class:`PythonVersion` derives from :class:`SemanticVersion`, so the two relate."""
		VersionRange(SemanticVersion.Parse("1.0.0"), PythonVersion.Parse("2.0"))
		VersionRange(PythonVersion.Parse("1.0"), SemanticVersion.Parse("2.0.0"))

	def test_TheConstructorRefusesASibling(self) -> None:
		""":class:`CalendarVersion` and :class:`SemanticVersion` both derive from :class:`Version`, not each other."""
		with self.assertRaises(TypeError):
			VersionRange(SemanticVersion.Parse("1.0.0"), CalendarVersion.Parse("2024.10"))

	def test_EveryPathAcceptsASubclass(self) -> None:
		"""Membership and the comparison operators apply the same rule the constructor does."""
		versionRange = self._range()
		version = PythonVersion.Parse("1.5")

		self.assertIn(version, versionRange)
		self.assertFalse(versionRange < version)
		self.assertFalse(versionRange > version)

	def test_EveryPathRefusesASibling(self) -> None:
		versionRange = self._range()
		version = CalendarVersion.Parse("2024.10")

		with self.assertRaises(TypeError):
			version in versionRange

		with self.assertRaises(TypeError):
			versionRange < version

		with self.assertRaises(TypeError):
			versionRange >= version

	def test_AnUnboundRangeRelatesToAnything(self) -> None:
		"""With both ends unbound there is no bound type to be compatible with."""
		versionRange = VersionRange(None, None)

		self.assertIn(CalendarVersion.Parse("2024.10"), versionRange)
		self.assertIn(SemanticVersion.Parse("1.0.0"), versionRange)

	def test_TheErrorNamesBothTypes(self) -> None:
		versionRange = self._range()

		with self.assertRaises(TypeError) as capture:
			CalendarVersion.Parse("2024.10") in versionRange

		self.assertIn("CalendarVersion", capture.exception.__notes__[0])
		self.assertIn("SemanticVersion", capture.exception.__notes__[1])
