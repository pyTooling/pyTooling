# ==================================================================================================================== #
#             _____           _ _               ____           _            _             ____  ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ \|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  __) | | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |/ __/| |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|_____|____/                  #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for ...
"""
from math                  import sqrt
from unittest              import TestCase

from pyTooling.Cartesian2D import Origin2D, Point2D, Offset2D, Size2D, LineSegment2D


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Origin(self) -> None:
		origin = Origin2D()

		self.assertIsInstance(origin.x, int)
		self.assertIsInstance(origin.y, int)
		self.assertEqual(0, origin.x)
		self.assertEqual(0, origin.y)
		self.assertTupleEqual((0, 0), origin.ToTuple())
		self.assertEqual("Origin2D(0, 0)", repr(origin))

	def test_Point_int(self) -> None:
		point = Point2D(1, 2)

		self.assertIsInstance(point.x, int)
		self.assertIsInstance(point.y, int)
		self.assertEqual(1, point.x)
		self.assertEqual(2, point.y)
		self.assertTupleEqual((1, 2), point.ToTuple())
		self.assertEqual("Point2D(1, 2)", repr(point))

	def test_Point_float(self) -> None:
		point = Point2D(1.0, 2.0)

		self.assertIsInstance(point.x, float)
		self.assertIsInstance(point.y, float)
		self.assertEqual(1.0, point.x)
		self.assertEqual(2.0, point.y)
		self.assertTupleEqual((1.0, 2.0), point.ToTuple())
		self.assertEqual("Point2D(1.0, 2.0)", repr(point))

	def test_Point_str1(self) -> None:
		with self.assertRaises(TypeError):
			_ =Point2D("1", 2)

	def test_Point_str2(self) -> None:
		with self.assertRaises(TypeError):
			_ =Point2D(1, "2")

	def test_Offset_int(self) -> None:
		offset = Offset2D(1, 2)

		self.assertIsInstance(offset.xOffset, int)
		self.assertIsInstance(offset.yOffset, int)
		self.assertEqual(1, offset.xOffset)
		self.assertEqual(2, offset.yOffset)
		self.assertTupleEqual((1, 2), offset.ToTuple())
		self.assertEqual("Offset2D(1, 2)", repr(offset))

	def test_Offset_float(self) -> None:
		offset = Offset2D(1.0, 2.0)

		self.assertIsInstance(offset.xOffset, float)
		self.assertIsInstance(offset.yOffset, float)
		self.assertEqual(1.0, offset.xOffset)
		self.assertEqual(2.0, offset.yOffset)
		self.assertTupleEqual((1.0, 2.0), offset.ToTuple())
		self.assertEqual("Offset2D(1.0, 2.0)", repr(offset))

	def test_Offset_str1(self) -> None:
		with self.assertRaises(TypeError):
			_ = Offset2D("1", 2)

	def test_Offset_str2(self) -> None:
		with self.assertRaises(TypeError):
			_ = Offset2D(1, "2")

	def test_Size_int(self) -> None:
		size = Size2D(1, 2)

		self.assertIsInstance(size.width, int)
		self.assertIsInstance(size.height, int)
		self.assertEqual(1, size.width)
		self.assertEqual(2, size.height)
		self.assertTupleEqual((1, 2), size.ToTuple())
		self.assertEqual("Size2D(1, 2)", repr(size))

	def test_Size_float(self) -> None:
		size = Size2D(1.0, 2.0)

		self.assertIsInstance(size.width, float)
		self.assertIsInstance(size.height, float)
		self.assertEqual(1.0, size.width)
		self.assertEqual(2.0, size.height)
		self.assertTupleEqual((1.0, 2.0), size.ToTuple())
		self.assertEqual("Size2D(1.0, 2.0)", repr(size))

	def test_Size_str1(self) -> None:
		with self.assertRaises(TypeError):
			_ = Size2D("1", 2)

	def test_Size_str2(self) -> None:
		with self.assertRaises(TypeError):
			_ = Size2D(1, "2")

	def test_LineSegment(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		line = LineSegment2D(point1, point2)

		offset = Offset2D(1, 1)

		self.assertEqual(sqrt(2), line.Length)
		self.assertEqual(offset, line.ToOffset())
		self.assertTupleEqual(((1, 2), (2, 3)), line.ToTuple())


class Copy(TestCase):
	def test_Origin(self) -> None:
		origin = Origin2D()

		with self.assertRaises(RuntimeError):
			_ = origin.Copy()

	def test_Point_int(self) -> None:
		point = Point2D(1, 2)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.x, int)
		self.assertIsInstance(newPoint.y, int)
		self.assertEqual(1, newPoint.x)
		self.assertEqual(2, newPoint.y)
		self.assertTupleEqual((1, 2), newPoint.ToTuple())
		self.assertEqual("Point2D(1, 2)", repr(newPoint))

	def test_Point_float(self) -> None:
		point = Point2D(1.0, 2.0)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.x, float)
		self.assertIsInstance(newPoint.y, float)
		self.assertEqual(1.0, newPoint.x)
		self.assertEqual(2.0, newPoint.y)
		self.assertTupleEqual((1.0, 2.0), newPoint.ToTuple())
		self.assertEqual("Point2D(1.0, 2.0)", repr(newPoint))

	def test_Offset_int(self) -> None:
		offset = Offset2D(1, 2)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.xOffset, int)
		self.assertIsInstance(newOffset.yOffset, int)
		self.assertEqual(1, newOffset.xOffset)
		self.assertEqual(2, newOffset.yOffset)
		self.assertTupleEqual((1, 2), newOffset.ToTuple())
		self.assertEqual("Offset2D(1, 2)", repr(newOffset))

	def test_Offset_float(self) -> None:
		offset = Offset2D(1.0, 2.0)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.xOffset, float)
		self.assertIsInstance(newOffset.yOffset, float)
		self.assertEqual(1.0, newOffset.xOffset)
		self.assertEqual(2.0, newOffset.yOffset)
		self.assertTupleEqual((1.0, 2.0), newOffset.ToTuple())
		self.assertEqual("Offset2D(1.0, 2.0)", repr(newOffset))

	def test_Size_int(self) -> None:
		size = Size2D(1, 2)

		newSize = size.Copy()

		self.assertIsInstance(newSize.width, int)
		self.assertIsInstance(newSize.height, int)
		self.assertEqual(1, newSize.width)
		self.assertEqual(2, newSize.height)
		self.assertTupleEqual((1, 2), newSize.ToTuple())
		self.assertEqual("Size2D(1, 2)", repr(newSize))

	def test_Size_float(self) -> None:
		size = Size2D(1.0, 2.0)

		newSize = size.Copy()

		self.assertIsInstance(newSize.width, float)
		self.assertIsInstance(newSize.height, float)
		self.assertEqual(1.0, newSize.width)
		self.assertEqual(2.0, newSize.height)
		self.assertTupleEqual((1.0, 2.0), newSize.ToTuple())
		self.assertEqual("Size2D(1.0, 2.0)", repr(newSize))


class Comparison(TestCase):
	def test_Offset_Equal_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(1, 2)

		self.assertEqual(offset1, offset2)

	def test_Offset_Equal_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (1, 2)

		self.assertEqual(offset1, offset2)

	def test_Offset_Equal_int(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 == offset2

	def test_Offset_Unequal_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		self.assertTrue(offset1 != offset2)


class PointArithmetic(TestCase):
	def test_Point_Plus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		with self.assertRaises(TypeError):
			_ = point1 + point2

	def test_Point_Plus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)

	def test_Point_Plus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)

	def test_Point_InplacePlus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)

	def test_Point_InplacePlus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)

	def test_Point_InplacePlus_Int(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			point += 2

	def test_Point_Minus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + -offset

		self.assertEqual(-1, newPoint.x)
		self.assertEqual(-1, newPoint.y)

	def test_Point_Minus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		offset = point2 - point1

		self.assertEqual(1, offset.xOffset)
		self.assertEqual(1, offset.yOffset)

	def test_Point_Minus_Tuple(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			_ = point - 2

	def test_Point_InplaceMinus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		point -= offset

		self.assertEqual(-1, point.x)
		self.assertEqual(-1, point.y)

	def test_Point_InplaceMinus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		point -= offset

		self.assertEqual(-1, point.x)
		self.assertEqual(-1, point.y)

	def test_Point_InplaceMinus_Int(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			point -= 2


class OffsetArithmetic(TestCase):
	def test_Offset_Plus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.xOffset)
		self.assertEqual(5, newOffset.yOffset)

	def test_Offset_Plus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.xOffset)
		self.assertEqual(5, newOffset.yOffset)

	def test_Offset_Plus_int(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 + offset2

	def test_Offset_InplacePlus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		offset1 += offset2

		self.assertEqual(3, offset1.xOffset)
		self.assertEqual(5, offset1.yOffset)

	def test_Offset_InplacePlus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		offset1 += offset2

		self.assertEqual(3, offset1.xOffset)
		self.assertEqual(5, offset1.yOffset)

	def test_Offset_InplacePlus_Int(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError):
			offset += 2

	def test_Offset_Minus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.xOffset)
		self.assertEqual(-1, newOffset.yOffset)

	def test_Offset_Minus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.xOffset)
		self.assertEqual(-1, newOffset.yOffset)

	def test_Offset_Minus_int(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 - offset2

	def test_Offset_InplaceMinus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		offset1 -= offset2

		self.assertEqual(-1, offset1.xOffset)
		self.assertEqual(-1, offset1.yOffset)

	def test_Offset_InplaceMinus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		offset1 -= offset2

		self.assertEqual(-1, offset1.xOffset)
		self.assertEqual(-1, offset1.yOffset)

	def test_Offset_InplaceMinus_Int(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError):
			offset -= 2
