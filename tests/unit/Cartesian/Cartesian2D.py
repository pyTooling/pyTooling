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
Unit tests for :mod:`pyTooling.Cartesian2D`: points, offsets and sizes, their copies, comparisons and
arithmetic.
"""
from copy                         import copy, deepcopy
from math                         import isclose, pi, sqrt

from pyTooling.Cartesian2D        import Base, Element2D, Origin2D, Point2D, Offset2D, Size2D, BoundingBox, Segment2D, \
                                         LineSegment2D, Alignment, AlreadyOwnedError, DuplicatePointError, NoAreaError
from pyTooling.Cartesian2D.Shapes import Rectangle, Circle, Shape
from pyTooling.Cartesian2D.Groups import Group, Canvas
from pyTooling.Exceptions         import DuplicateElementError, InvalidOperationError
from pyTooling.MetaClasses        import AbstractClassError
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Origin(self) -> None:
		origin = Origin2D()

		self.assertIsInstance(origin.X, int)
		self.assertIsInstance(origin.Y, int)
		self.assertEqual(0, origin.X)
		self.assertEqual(0, origin.Y)
		self.assertTupleEqual((0, 0), origin.ToTuple())
		self.assertEqual("Origin2D(0, 0)", repr(origin))

	def test_Point_int(self) -> None:
		point = Point2D(1, 2)

		self.assertIsInstance(point.X, int)
		self.assertIsInstance(point.Y, int)
		self.assertEqual(1, point.X)
		self.assertEqual(2, point.Y)
		self.assertTupleEqual((1, 2), point.ToTuple())
		self.assertEqual("Point2D(1, 2)", repr(point))

	def test_Point_float(self) -> None:
		point = Point2D(1.0, 2.0)

		self.assertIsInstance(point.X, float)
		self.assertIsInstance(point.Y, float)
		self.assertEqual(1.0, point.X)
		self.assertEqual(2.0, point.Y)
		self.assertTupleEqual((1.0, 2.0), point.ToTuple())
		self.assertEqual("Point2D(1.0, 2.0)", repr(point))

	def test_Point_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point2D("1", 2)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Point_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point2D(1, "2")

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Offset_int(self) -> None:
		offset = Offset2D(1, 2)

		self.assertIsInstance(offset.XOffset, int)
		self.assertIsInstance(offset.YOffset, int)
		self.assertEqual(1, offset.XOffset)
		self.assertEqual(2, offset.YOffset)
		self.assertTupleEqual((1, 2), offset.ToTuple())
		self.assertEqual("Offset2D(1, 2)", repr(offset))

	def test_Offset_float(self) -> None:
		offset = Offset2D(1.0, 2.0)

		self.assertIsInstance(offset.XOffset, float)
		self.assertIsInstance(offset.YOffset, float)
		self.assertEqual(1.0, offset.XOffset)
		self.assertEqual(2.0, offset.YOffset)
		self.assertTupleEqual((1.0, 2.0), offset.ToTuple())
		self.assertEqual("Offset2D(1.0, 2.0)", repr(offset))

	def test_Offset_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset2D("1", 2)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Offset_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset2D(1, "2")

		self.assertEqual("Parameter 'yOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Size_int(self) -> None:
		size = Size2D(1, 2)

		self.assertIsInstance(size.Width, int)
		self.assertIsInstance(size.Height, int)
		self.assertEqual(1, size.Width)
		self.assertEqual(2, size.Height)
		self.assertTupleEqual((1, 2), size.ToTuple())
		self.assertEqual("Size2D(1, 2)", repr(size))

	def test_Size_float(self) -> None:
		size = Size2D(1.0, 2.0)

		self.assertIsInstance(size.Width, float)
		self.assertIsInstance(size.Height, float)
		self.assertEqual(1.0, size.Width)
		self.assertEqual(2.0, size.Height)
		self.assertTupleEqual((1.0, 2.0), size.ToTuple())
		self.assertEqual("Size2D(1.0, 2.0)", repr(size))

	def test_Size_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Size2D("1", 2)

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Size_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Size2D(1, "2")

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_LineSegment(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		line = LineSegment2D(point1, point2)

		offset = Offset2D(1, 1)

		self.assertEqual(sqrt(2), line.Length)
		self.assertEqual(offset, line.ToOffset())
		self.assertTupleEqual(((1, 2), (2, 3)), line.ToTuple())

	def test_Point_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Point2D(None, 2)

		self.assertEqual("Parameter 'x' is None.", str(context.exception))

	def test_Point_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Point2D(1, None)

		self.assertEqual("Parameter 'y' is None.", str(context.exception))

	def test_Offset_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Offset2D(None, 2)

		self.assertEqual("Parameter 'xOffset' is None.", str(context.exception))

	def test_Offset_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Offset2D(1, None)

		self.assertEqual("Parameter 'yOffset' is None.", str(context.exception))

	def test_Size_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Size2D(None, 2)

		self.assertEqual("Parameter 'width' is None.", str(context.exception))

	def test_Size_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Size2D(1, None)

		self.assertEqual("Parameter 'height' is None.", str(context.exception))

	def test_LineSegment_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment2D(None, Point2D(1, 2))

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_LineSegment_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment2D(Point2D(1, 2), None)

		self.assertEqual("Parameter 'end' is None.", str(context.exception))


class Properties(Testcase):
	def test_Point_X(self) -> None:
		point = Point2D(1, 2)

		point.X = 3.5

		self.assertEqual(3.5, point.X)
		self.assertTupleEqual((3.5, 2), point.ToTuple())

	def test_Point_x_None(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			point.X = None

		self.assertEqual("Parameter 'x' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), point.ToTuple())

	def test_Point_x_str(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			point.X = "3.5"

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), point.ToTuple())

	def test_Point_Y(self) -> None:
		point = Point2D(1, 2)

		point.Y = 3.5

		self.assertEqual(3.5, point.Y)
		self.assertTupleEqual((1, 3.5), point.ToTuple())

	def test_Point_y_None(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			point.Y = None

		self.assertEqual("Parameter 'y' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), point.ToTuple())

	def test_Point_y_str(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			point.Y = "3.5"

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), point.ToTuple())

	def test_Offset_XOffset(self) -> None:
		offset = Offset2D(1, 2)

		offset.XOffset = 3.5

		self.assertEqual(3.5, offset.XOffset)
		self.assertTupleEqual((3.5, 2), offset.ToTuple())

	def test_Offset_xOffset_None(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(ValueError) as context:
			offset.XOffset = None

		self.assertEqual("Parameter 'xOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), offset.ToTuple())

	def test_Offset_xOffset_str(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError) as context:
			offset.XOffset = "3.5"

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), offset.ToTuple())

	def test_Offset_YOffset(self) -> None:
		offset = Offset2D(1, 2)

		offset.YOffset = 3.5

		self.assertEqual(3.5, offset.YOffset)
		self.assertTupleEqual((1, 3.5), offset.ToTuple())

	def test_Offset_yOffset_None(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(ValueError) as context:
			offset.YOffset = None

		self.assertEqual("Parameter 'yOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), offset.ToTuple())

	def test_Offset_yOffset_str(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError) as context:
			offset.YOffset = "3.5"

		self.assertEqual("Parameter 'yOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), offset.ToTuple())

	def test_Size_Width(self) -> None:
		size = Size2D(1, 2)

		size.Width = 3.5

		self.assertEqual(3.5, size.Width)
		self.assertTupleEqual((3.5, 2), size.ToTuple())

	def test_Size_width_None(self) -> None:
		size = Size2D(1, 2)

		with self.assertRaises(ValueError) as context:
			size.Width = None

		self.assertEqual("Parameter 'width' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), size.ToTuple())

	def test_Size_width_str(self) -> None:
		size = Size2D(1, 2)

		with self.assertRaises(TypeError) as context:
			size.Width = "3.5"

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), size.ToTuple())

	def test_Size_Height(self) -> None:
		size = Size2D(1, 2)

		size.Height = 3.5

		self.assertEqual(3.5, size.Height)
		self.assertTupleEqual((1, 3.5), size.ToTuple())

	def test_Size_height_None(self) -> None:
		size = Size2D(1, 2)

		with self.assertRaises(ValueError) as context:
			size.Height = None

		self.assertEqual("Parameter 'height' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), size.ToTuple())

	def test_Size_height_str(self) -> None:
		size = Size2D(1, 2)

		with self.assertRaises(TypeError) as context:
			size.Height = "3.5"

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), size.ToTuple())

	def test_LineSegment_Start(self) -> None:
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 5))
		point = Point2D(7, 8)

		line.Start = point

		self.assertIs(point, line.Start)
		self.assertTupleEqual(((7, 8), (4, 5)), line.ToTuple())

	def test_LineSegment_start_None(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 5))

		with self.assertRaises(ValueError) as context:
			line.Start = None

		self.assertEqual("Parameter 'start' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 5)), line.ToTuple())

	def test_LineSegment_start_tuple(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 5))

		with self.assertRaises(TypeError) as context:
			line.Start = (7, 8)

		self.assertEqual("Parameter 'start' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 5)), line.ToTuple())

	def test_LineSegment_End(self) -> None:
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 5))
		point = Point2D(7, 8)

		line.End = point

		self.assertIs(point, line.End)
		self.assertTupleEqual(((1, 2), (7, 8)), line.ToTuple())

	def test_LineSegment_end_None(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 5))

		with self.assertRaises(ValueError) as context:
			line.End = None

		self.assertEqual("Parameter 'end' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 5)), line.ToTuple())

	def test_LineSegment_end_tuple(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 5))

		with self.assertRaises(TypeError) as context:
			line.End = (7, 8)

		self.assertEqual("Parameter 'end' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 5)), line.ToTuple())


class Aliases(Testcase):
	def test_Point(self) -> None:
		point = Point2D(1, 2)

		self.assertIs(Point2D.X, Point2D.x)
		self.assertIs(Point2D.Y, Point2D.y)

		point.x = 7.5
		point.y = 8.5

		self.assertEqual(7.5, point.X)
		self.assertEqual(8.5, point.Y)

	def test_Offset(self) -> None:
		offset = Offset2D(1, 2)

		self.assertIs(Offset2D.XOffset, Offset2D.xOffset)
		self.assertIs(Offset2D.YOffset, Offset2D.yOffset)

		offset.xOffset = 7.5
		offset.yOffset = 8.5

		self.assertEqual(7.5, offset.XOffset)
		self.assertEqual(8.5, offset.YOffset)

	def test_Size(self) -> None:
		size = Size2D(1, 2)

		self.assertIs(Size2D.Width, Size2D.width)
		self.assertIs(Size2D.Height, Size2D.height)

		size.width = 7.5
		size.height = 8.5

		self.assertEqual(7.5, size.Width)
		self.assertEqual(8.5, size.Height)

	def test_LineSegment(self) -> None:
		line =  LineSegment2D(Point2D(1, 2), Point2D(2, 3))
		start = Point2D(4, 5)
		end =   Point2D(7, 8)

		self.assertIs(Segment2D.Start, Segment2D.start)
		self.assertIs(Segment2D.End, Segment2D.end)

		line.start = start
		line.end =   end

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertIs(start, line.start)
		self.assertIs(end, line.end)


class LineSegment(Testcase):
	def test_Length_Horizontal(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(3, 0))

		self.assertEqual(3.0, line.Length)

	def test_Length_Vertical(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(0, 3))

		self.assertEqual(3.0, line.Length)

	def test_Length_Diagonal(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(3, 4))

		self.assertEqual(5.0, line.Length)

	def test_AngleTo_Perpendicular(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		line2 = LineSegment2D(Point2D(2, 0), Point2D(2, 2))

		self.assertTrue(isclose(pi / 2, line1.AngleTo(line2)))

	def test_AngleTo_Parallel(self) -> None:
		"""Same direction, different lengths: the cosine of the angle rounds to 0.9999999999999999."""
		line1 = LineSegment2D(Point2D(0, 0), Point2D(1, 1))
		line2 = LineSegment2D(Point2D(0, 0), Point2D(7, 7))

		self.assertEqual(0.0, line1.AngleTo(line2))

	def test_AngleTo_Opposite(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(1, 1))
		line2 = LineSegment2D(Point2D(0, 0), Point2D(-7, -7))

		self.assertEqual(pi, line1.AngleTo(line2))

	def test_AngleTo_ParallelFloat(self) -> None:
		"""Same direction: the cosine of the angle rounds to 1.0000000000000002, outside acos' domain."""
		line1 = LineSegment2D(Point2D(0.0, 0.0), Point2D(0.30000000000000004, 0.2))
		line2 = LineSegment2D(Point2D(0.0, 0.0), Point2D(0.9000000000000001, 0.6000000000000001))

		self.assertAlmostEqual(0.0, line1.AngleTo(line2), places=15)

	def test_AngleTo_None(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(2, 0))

		with self.assertRaises(ValueError) as context:
			_ = line.AngleTo(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_AngleTo_Type(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(2, 0))

		with self.assertRaises(TypeError) as context:
			_ = line.AngleTo(Point2D(2, 0))

		self.assertEqual("Parameter 'other' is not of type 'LineSegment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_AngleTo_ZeroLength(self) -> None:
		line1 = LineSegment2D(Point2D(1, 1), Point2D(1, 1))
		line2 = LineSegment2D(Point2D(0, 0), Point2D(2, 0))

		with self.assertRaises(ValueError) as context:
			_ = line1.AngleTo(line2)

		self.assertEqual("Line segment has length 0.", str(context.exception))
		self.assertListEqual([
			"Got line segment ((1, 1) → (1, 1)).",
			"Can't determine an angle between two lines if one of the lines has no direction, due to a zero-length."
		], context.exception.__notes__)

	def test_AngleTo_ZeroLengthOther(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		line2 = LineSegment2D(Point2D(1, 1), Point2D(1, 1))

		with self.assertRaises(ValueError) as context:
			_ = line1.AngleTo(line2)

		self.assertEqual("Parameter 'other' has length 0.", str(context.exception))
		self.assertListEqual([
			"Got line segment ((1, 1) → (1, 1)).",
			"Can't determine an angle between two lines if one of the lines has no direction, due to a zero-length."
		], context.exception.__notes__)


class Copy(Testcase):
	def test_Origin(self) -> None:
		origin = Origin2D()

		with self.assertRaises(InvalidOperationError) as context:
			_ = origin.Copy()

		self.assertEqual("An origin can't be copied.", str(context.exception))
		self.assertIsInstance(context.exception, RuntimeError)

	def test_Point_int(self) -> None:
		point = Point2D(1, 2)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.X, int)
		self.assertIsInstance(newPoint.Y, int)
		self.assertEqual(1, newPoint.X)
		self.assertEqual(2, newPoint.Y)
		self.assertTupleEqual((1, 2), newPoint.ToTuple())
		self.assertEqual("Point2D(1, 2)", repr(newPoint))

	def test_Point_float(self) -> None:
		point = Point2D(1.0, 2.0)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.X, float)
		self.assertIsInstance(newPoint.Y, float)
		self.assertEqual(1.0, newPoint.X)
		self.assertEqual(2.0, newPoint.Y)
		self.assertTupleEqual((1.0, 2.0), newPoint.ToTuple())
		self.assertEqual("Point2D(1.0, 2.0)", repr(newPoint))

	def test_Offset_int(self) -> None:
		offset = Offset2D(1, 2)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.XOffset, int)
		self.assertIsInstance(newOffset.YOffset, int)
		self.assertEqual(1, newOffset.XOffset)
		self.assertEqual(2, newOffset.YOffset)
		self.assertTupleEqual((1, 2), newOffset.ToTuple())
		self.assertEqual("Offset2D(1, 2)", repr(newOffset))

	def test_Offset_float(self) -> None:
		offset = Offset2D(1.0, 2.0)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.XOffset, float)
		self.assertIsInstance(newOffset.YOffset, float)
		self.assertEqual(1.0, newOffset.XOffset)
		self.assertEqual(2.0, newOffset.YOffset)
		self.assertTupleEqual((1.0, 2.0), newOffset.ToTuple())
		self.assertEqual("Offset2D(1.0, 2.0)", repr(newOffset))

	def test_Size_int(self) -> None:
		size = Size2D(1, 2)

		newSize = size.Copy()

		self.assertIsInstance(newSize.Width, int)
		self.assertIsInstance(newSize.Height, int)
		self.assertEqual(1, newSize.Width)
		self.assertEqual(2, newSize.Height)
		self.assertTupleEqual((1, 2), newSize.ToTuple())
		self.assertEqual("Size2D(1, 2)", repr(newSize))

	def test_Size_float(self) -> None:
		size = Size2D(1.0, 2.0)

		newSize = size.Copy()

		self.assertIsInstance(newSize.Width, float)
		self.assertIsInstance(newSize.Height, float)
		self.assertEqual(1.0, newSize.Width)
		self.assertEqual(2.0, newSize.Height)
		self.assertTupleEqual((1.0, 2.0), newSize.ToTuple())
		self.assertEqual("Size2D(1.0, 2.0)", repr(newSize))

	def test_Origin_copy(self) -> None:
		origin = Origin2D()

		with self.assertRaises(InvalidOperationError):
			_ = copy(origin)

	def test_Origin_deepcopy(self) -> None:
		origin = Origin2D()

		with self.assertRaises(InvalidOperationError):
			_ = deepcopy(origin)

	def test_Point_Independent(self) -> None:
		point = Point2D(1, 2)

		newPoint =  point.Copy()
		newPoint += (5, 5)

		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2), point.ToTuple())
		self.assertTupleEqual((6, 7), newPoint.ToTuple())

	def test_Point_copy(self) -> None:
		point = Point2D(1, 2)

		newPoint = copy(point)

		self.assertIs(Point2D, type(newPoint))
		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2), newPoint.ToTuple())

	def test_Point_deepcopy(self) -> None:
		point = Point2D(1, 2)

		newPoint = deepcopy(point)

		self.assertIs(Point2D, type(newPoint))
		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2), newPoint.ToTuple())

	def test_Offset_copy(self) -> None:
		offset = Offset2D(1, 2)

		newOffset = copy(offset)

		self.assertIs(Offset2D, type(newOffset))
		self.assertIsNot(offset, newOffset)
		self.assertEqual(offset, newOffset)

	def test_Offset_deepcopy(self) -> None:
		offset = Offset2D(1, 2)

		newOffset = deepcopy(offset)

		self.assertIs(Offset2D, type(newOffset))
		self.assertIsNot(offset, newOffset)
		self.assertEqual(offset, newOffset)

	def test_Size_copy(self) -> None:
		size = Size2D(1, 2)

		newSize = copy(size)

		self.assertIs(Size2D, type(newSize))
		self.assertIsNot(size, newSize)
		self.assertTupleEqual((1, 2), newSize.ToTuple())

	def test_Size_deepcopy(self) -> None:
		size = Size2D(1, 2)

		newSize = deepcopy(size)

		self.assertIs(Size2D, type(newSize))
		self.assertIsNot(size, newSize)
		self.assertTupleEqual((1, 2), newSize.ToTuple())

	def test_LineSegment(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(2, 3))

		newLine =       line.Copy()
		newLine.Start += (5, 5)
		newLine.End +=   (5, 5)

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIsNot(line, newLine)
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2), (2, 3)), line.ToTuple())
		self.assertTupleEqual(((6, 7), (7, 8)), newLine.ToTuple())

	def test_LineSegment_copy(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(2, 3))

		newLine = copy(line)

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2), (2, 3)), newLine.ToTuple())

	def test_LineSegment_deepcopy(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(2, 3))

		newLine = deepcopy(line)

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2), (2, 3)), newLine.ToTuple())

	def test_LineSegment_Origin(self) -> None:
		line = LineSegment2D(Origin2D(), Point2D(2, 3), copyPoints=False)

		with self.assertRaises(InvalidOperationError):
			_ = line.Copy()


class Comparison(Testcase):
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


class PointArithmetic(Testcase):
	def test_Point_Plus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		with self.assertRaises(TypeError):
			_ = point1 + point2

	def test_Point_Plus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.X)
		self.assertEqual(5, newPoint.Y)

	def test_Point_Plus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.X)
		self.assertEqual(5, newPoint.Y)

	def test_Point_InplacePlus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		point += offset

		self.assertEqual(3, point.X)
		self.assertEqual(5, point.Y)

	def test_Point_InplacePlus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		point += offset

		self.assertEqual(3, point.X)
		self.assertEqual(5, point.Y)

	def test_Point_InplacePlus_TupleComplex(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			point += (1j, 1)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Point_InplacePlus_Int(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			point += 2

	def test_Point_Minus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + -offset

		self.assertEqual(-1, newPoint.X)
		self.assertEqual(-1, newPoint.Y)

	def test_Point_Minus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		offset = point2 - point1

		self.assertEqual(1, offset.XOffset)
		self.assertEqual(1, offset.YOffset)

	def test_Point_Minus_Tuple(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			_ = point - 2

	def test_Point_InplaceMinus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		point -= offset

		self.assertEqual(-1, point.X)
		self.assertEqual(-1, point.Y)

	def test_Point_InplaceMinus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		point -= offset

		self.assertEqual(-1, point.X)
		self.assertEqual(-1, point.Y)

	def test_Point_InplaceMinus_TupleComplex(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			point -= (1j, 1)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Point_InplaceMinus_Int(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError):
			point -= 2


class OffsetArithmetic(Testcase):
	def test_Offset_Plus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.XOffset)
		self.assertEqual(5, newOffset.YOffset)

	def test_Offset_Plus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.XOffset)
		self.assertEqual(5, newOffset.YOffset)

	def test_Offset_Plus_int(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 + offset2

	def test_Offset_InplacePlus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		offset1 += offset2

		self.assertEqual(3, offset1.XOffset)
		self.assertEqual(5, offset1.YOffset)

	def test_Offset_InplacePlus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		offset1 += offset2

		self.assertEqual(3, offset1.XOffset)
		self.assertEqual(5, offset1.YOffset)

	def test_Offset_InplacePlus_TupleComplex(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError) as context:
			offset += (1j, 1)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Offset_InplacePlus_Int(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError):
			offset += 2

	def test_Offset_Minus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.XOffset)
		self.assertEqual(-1, newOffset.YOffset)

	def test_Offset_Minus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.XOffset)
		self.assertEqual(-1, newOffset.YOffset)

	def test_Offset_Minus_int(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 - offset2

	def test_Offset_InplaceMinus_Offset(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = Offset2D(2, 3)

		offset1 -= offset2

		self.assertEqual(-1, offset1.XOffset)
		self.assertEqual(-1, offset1.YOffset)

	def test_Offset_InplaceMinus_Tuple(self) -> None:
		offset1 = Offset2D(1, 2)
		offset2 = (2, 3)

		offset1 -= offset2

		self.assertEqual(-1, offset1.XOffset)
		self.assertEqual(-1, offset1.YOffset)

	def test_Offset_InplaceMinus_TupleComplex(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError) as context:
			offset -= (1j, 1)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Offset_InplaceMinus_Int(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError):
			offset -= 2


class Bounds(Testcase):
	def test_BoundingBox_int(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		self.assertEqual(1, box.MinX)
		self.assertEqual(2, box.MinY)
		self.assertEqual(4, box.MaxX)
		self.assertEqual(6, box.MaxY)
		self.assertEqual(3, box.Width)
		self.assertEqual(4, box.Height)
		self.assertTupleEqual((2.5, 4.0), box.Center.ToTuple())
		self.assertTupleEqual((1, 2, 4, 6), box.ToTuple())

	def test_BoundingBox_float(self) -> None:
		box = BoundingBox(-1.5, -2.5, 0.5, 0.5)

		self.assertEqual(2.0, box.Width)
		self.assertEqual(3.0, box.Height)
		self.assertTupleEqual((-0.5, -1.0), box.Center.ToTuple())

	def test_BoundingBox_Point(self) -> None:
		"""A bounding box may have no extent."""
		box = BoundingBox(1, 2, 1, 2)

		self.assertEqual(0, box.Width)
		self.assertEqual(0, box.Height)

	def test_BoundingBox_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(None, 2, 4, 6)

		self.assertEqual("Parameter 'minX' is None.", str(context.exception))

	def test_BoundingBox_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(1, None, 4, 6)

		self.assertEqual("Parameter 'minY' is None.", str(context.exception))

	def test_BoundingBox_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(1, 2, None, 6)

		self.assertEqual("Parameter 'maxX' is None.", str(context.exception))

	def test_BoundingBox_None4(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(1, 2, 4, None)

		self.assertEqual("Parameter 'maxY' is None.", str(context.exception))

	def test_BoundingBox_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox("1", 2, 4, 6)

		self.assertEqual("Parameter 'minX' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_str4(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox(1, 2, 4, "6")

		self.assertEqual("Parameter 'maxY' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_MaxXLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(4, 2, 1, 6)

		self.assertEqual("Parameter 'maxX' is less than parameter 'minX'.", str(context.exception))
		self.assertListEqual(["Got minX=4 and maxX=1."], context.exception.__notes__)

	def test_BoundingBox_MaxYLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox(1, 6, 4, 2)

		self.assertEqual("Parameter 'maxY' is less than parameter 'minY'.", str(context.exception))
		self.assertListEqual(["Got minY=6 and maxY=2."], context.exception.__notes__)

	def test_BoundingBox_ReadOnly(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		with self.assertRaises(AttributeError):
			box.MinX = 0

		self.assertEqual(1, box.MinX)

	def test_FromPoints(self) -> None:
		box = BoundingBox.FromPoints((Point2D(3, -1), Point2D(-2, 4), Point2D(1, 1)))

		self.assertIs(BoundingBox, type(box))
		self.assertTupleEqual((-2, -1, 3, 4), box.ToTuple())

	def test_FromPoints_Generator(self) -> None:
		box = BoundingBox.FromPoints(Point2D(x, 2 * x) for x in range(4))

		self.assertTupleEqual((0, 0, 3, 6), box.ToTuple())

	def test_FromPoints_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox.FromPoints(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_FromPoints_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox.FromPoints(3)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_FromPoints_NoneElement(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox.FromPoints((Point2D(0, 0), None))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_FromPoints_tupleElement(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox.FromPoints((Point2D(0, 0), (1, 1)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox.FromPoints(())

		self.assertEqual("Parameter 'points' is empty.", str(context.exception))

	def test_Union(self) -> None:
		box1 = BoundingBox(0, 0, 2, 2)
		box2 = BoundingBox(1, -1, 4, 1)

		box = box1.Union(box2)

		self.assertTupleEqual((0, -1, 4, 2), box.ToTuple())
		self.assertTupleEqual((0, 0, 2, 2), box1.ToTuple())
		self.assertTupleEqual((1, -1, 4, 1), box2.ToTuple())

	def test_Union_None(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.Union(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_Union_tuple(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.Union((1, 1, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_HasOverlap(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		self.assertTrue(box.HasOverlap(BoundingBox(1, 1, 3, 3)))
		self.assertTrue(box.HasOverlap(BoundingBox(-1, -1, 3, 3)))
		self.assertFalse(box.HasOverlap(BoundingBox(3, 0, 4, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox(0, -2, 2, -1)))

	def test_HasOverlap_Touching(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		self.assertFalse(box.HasOverlap(BoundingBox(2, 0, 4, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox(-2, 0, 0, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox(0, 2, 2, 4)))
		self.assertFalse(box.HasOverlap(BoundingBox(0, -2, 2, 0)))
		self.assertFalse(box.HasOverlap(BoundingBox(2, 2, 3, 3)))

	def test_HasOverlap_None(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.HasOverlap(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_HasOverlap_tuple(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.HasOverlap((1, 1, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_ContainsPoint(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		self.assertTrue(box.ContainsPoint(Point2D(1, 1)))
		self.assertTrue(box.ContainsPoint(Point2D(2, 0)))
		self.assertFalse(box.ContainsPoint(Point2D(3, 1)))
		self.assertFalse(box.ContainsPoint(Point2D(1, -0.5)))

	def test_ContainsPoint_None(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.ContainsPoint(None)

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_ContainsPoint_tuple(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.ContainsPoint((1, 1))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_In(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		self.assertIn(Point2D(1, 1), box)
		self.assertIn(Point2D(2, 0), box)
		self.assertNotIn(Point2D(3, 1), box)

	def test_In_tuple(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = (1, 1) in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for first operand: Point2D"],
			context.exception.__notes__
		)

	def test_In_None(self) -> None:
		box = BoundingBox(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = None in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for first operand: Point2D"],
			context.exception.__notes__
		)

	def test_ToRectangle(self) -> None:
		rectangle = BoundingBox(1, 2, 4, 6).ToRectangle()

		self.assertIsInstance(rectangle, Rectangle)
		self.assertTupleEqual(
			((1, 2), (1, 6), (4, 6), (4, 2)),
			tuple(point.ToTuple() for point in rectangle.Points)
		)
		self.assertEqual(BoundingBox(1, 2, 4, 6), rectangle.BoundingBox)

	def test_ToRectangle_NoArea(self) -> None:
		for box in (BoundingBox(1, 2, 1, 6), BoundingBox(1, 2, 4, 2)):
			with self.subTest(box=box):
				with self.assertRaises(NoAreaError) as context:
					_ = box.ToRectangle()

				self.assertEqual("Bounding box has no area.", str(context.exception))

	def test_Equal(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		self.assertTrue(box == BoundingBox(1, 2, 4, 6))
		self.assertFalse(box == BoundingBox(1, 2, 4, 7))
		self.assertFalse(box != BoundingBox(1, 2, 4, 6))
		self.assertTrue(box != BoundingBox(0, 2, 4, 6))

	def test_Equal_tuple(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box == (1, 2, 4, 6)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox"],
			context.exception.__notes__
		)

	def test_Unequal_tuple(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box != (1, 2, 4, 6)

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox"],
			context.exception.__notes__
		)

	def test_Plus_Offset(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		newBox = box + Offset2D(10, -2)

		self.assertIs(BoundingBox, type(newBox))
		self.assertTupleEqual((11, 0, 14, 4), newBox.ToTuple())
		self.assertTupleEqual((1, 2, 4, 6), box.ToTuple())

	def test_Plus_tuple(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box + (10, -2)

		self.assertEqual("Parameter 'other' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Copy(self) -> None:
		box = BoundingBox(1, 2, 4, 6)

		for newBox in (box.Copy(), copy(box), deepcopy(box)):
			self.assertIs(BoundingBox, type(newBox))
			self.assertIsNot(box, newBox)
			self.assertEqual(box, newBox)

	def test_repr(self) -> None:
		box = BoundingBox(1, 2, 4.5, 6)

		self.assertEqual("BoundingBox(1, 2, 4.5, 6)", repr(box))

	def test_str(self) -> None:
		box = BoundingBox(1, 2, 4.5, 6)

		self.assertEqual("((1, 2), (4.5, 6))", str(box))

	def test_LineSegment(self) -> None:
		line = LineSegment2D(Point2D(4, 1), Point2D(-1, 3))

		box = line.BoundingBox

		self.assertTupleEqual((-1, 1, 4, 3), box.ToTuple())

	def test_LineSegment_ReadOnly(self) -> None:
		line = LineSegment2D(Point2D(4, 1), Point2D(-1, 3))

		with self.assertRaises(AttributeError):
			line.BoundingBox = BoundingBox(0, 0, 1, 1)


class Moving(Testcase):
	def test_LineSegment(self) -> None:
		start = Point2D(1, 2)
		end =   Point2D(4, 6)
		line =  LineSegment2D(start, end, copyPoints=False)

		line.Move(Offset2D(1, -1))

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertTupleEqual(((2, 1), (5, 5)), line.ToTuple())

	def test_LineSegment_None(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_LineSegment_tuple(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.Move((1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())


class Hierarchy(Testcase):
	def test_Base(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Base()

	def test_Element2D(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Element2D()

	def test_Point(self) -> None:
		self.assertIsInstance(Point2D(1, 2), Base)
		self.assertNotIsInstance(Point2D(1, 2), Element2D)

	def test_Origin(self) -> None:
		origin = Origin2D()

		self.assertIsInstance(origin, Base)
		self.assertIsNone(origin.Parent)
		self.assertIsNone(origin.Frame)

	def test_Segment(self) -> None:
		self.assertIsInstance(Segment2D(Point2D(1, 2), Point2D(4, 6)), Element2D)
		self.assertIsInstance(LineSegment2D(Point2D(1, 2), Point2D(4, 6)), Element2D)

	def test_Shape(self) -> None:
		self.assertTrue(issubclass(Shape, Element2D))

	def test_Slots(self) -> None:
		"""The parent is a slot of the base-class only."""
		self.assertTupleEqual(("_parent", ), Base.__slots__)
		self.assertTupleEqual((), Element2D.__slots__)
		self.assertNotIn("_parent", Point2D.__slots__)
		self.assertNotIn("_parent", Segment2D.__slots__)


class Mirroring(Testcase):
	def test_MirrorHorizontally(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorHorizontally()

		self.assertTupleEqual(((1, 6), (4, 2)), line.ToTuple())

	def test_MirrorHorizontally_MinY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorHorizontally(Alignment.MinY)

		self.assertTupleEqual(((1, 2), (4, -2)), line.ToTuple())

	def test_MirrorHorizontally_MaxY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorHorizontally(Alignment.MaxY)

		self.assertTupleEqual(((1, 10), (4, 6)), line.ToTuple())

	def test_MirrorHorizontally_Offset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorHorizontally(Alignment.MinY, 1)

		self.assertTupleEqual(((1, 4), (4, 0)), line.ToTuple())

	def test_MirrorHorizontally_FloatOffset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorHorizontally(Alignment.MaxY, -0.5)

		self.assertTupleEqual(((1, 9.0), (4, 5.0)), line.ToTuple())

	def test_MirrorHorizontally_Int(self) -> None:
		"""An axis between two integer coordinates keeps integer coordinates."""
		line = LineSegment2D(Point2D(1, 1), Point2D(4, 6))

		line.MirrorHorizontally(Alignment.CenterY)

		self.assertTupleEqual(((1, 6), (4, 1)), line.ToTuple())
		self.assertIs(int, type(line.Start.Y))
		self.assertIs(int, type(line.End.Y))

	def test_MirrorHorizontally_AxisNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorHorizontally(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorHorizontally_AxisStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorHorizontally("MinY")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorHorizontally_AxisX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		for axis in (Alignment.MinX, Alignment.CenterX, Alignment.MaxX):
			with self.subTest(axis=axis):
				with self.assertRaises(ValueError) as context:
					line.MirrorHorizontally(axis)

				self.assertEqual(
					"Parameter 'axis' is not Alignment.MinY, Alignment.CenterY or Alignment.MaxY.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment.{axis.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorHorizontally_OffsetNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorHorizontally(Alignment.MinY, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorHorizontally_OffsetStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorHorizontally(Alignment.MinY, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically()

		self.assertTupleEqual(((4, 2), (1, 6)), line.ToTuple())

	def test_MirrorVertically_MinX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically(Alignment.MinX)

		self.assertTupleEqual(((1, 2), (-2, 6)), line.ToTuple())

	def test_MirrorVertically_MaxX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically(Alignment.MaxX)

		self.assertTupleEqual(((7, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically_Offset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically(Alignment.MaxX, -1)

		self.assertTupleEqual(((5, 2), (2, 6)), line.ToTuple())

	def test_MirrorVertically_FloatOffset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically(Alignment.MinX, 0.5)

		self.assertTupleEqual(((2.0, 2), (-1.0, 6)), line.ToTuple())

	def test_MirrorVertically_Int(self) -> None:
		"""An axis between two integer coordinates keeps integer coordinates."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorVertically(Alignment.CenterX)

		self.assertTupleEqual(((4, 2), (1, 6)), line.ToTuple())
		self.assertIs(int, type(line.Start.X))
		self.assertIs(int, type(line.End.X))

	def test_MirrorVertically_AxisNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorVertically(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically_AxisStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorVertically("MinX")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically_AxisY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		for axis in (Alignment.MinY, Alignment.CenterY, Alignment.MaxY):
			with self.subTest(axis=axis):
				with self.assertRaises(ValueError) as context:
					line.MirrorVertically(axis)

				self.assertEqual(
					"Parameter 'axis' is not Alignment.MinX, Alignment.CenterX or Alignment.MaxX.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment.{axis.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically_OffsetNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorVertically(Alignment.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorVertically_OffsetStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorVertically(Alignment.MinX, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())


class Ownership(Testcase):
	def test_Point(self) -> None:
		point = Point2D(1, 2)

		self.assertIsNone(point.Parent)
		self.assertIsNone(point.Frame)

	def test_Point_Parent(self) -> None:
		"""The parent parameter sets the owner, but the point isn't registered."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		start = line.Start
		end = line.End

		point = Point2D(7, 8, parent=line)

		self.assertIs(line, point.Parent)
		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertIs(line, start.Parent)

	def test_Point_ParentNone(self) -> None:
		point = Point2D(1, 2, parent=None)

		self.assertIsNone(point.Parent)

	def test_Point_ParentInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point2D(1, 2, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Point_ParentPoint(self) -> None:
		"""A point can't own another point."""
		with self.assertRaises(TypeError) as context:
			_ = Point2D(1, 2, parent=Point2D(3, 4))

		self.assertEqual("Parameter 'parent' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_Point_ParentPositional(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError):
			_ = Point2D(1, 2, line)

	def test_Point_Parent_Copy(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		point = Point2D(7, 8, parent=line)

		self.assertIsNone(point.Copy().Parent)
		self.assertIsNone(copy(point).Parent)
		self.assertIsNone(deepcopy(point).Parent)

	def test_Point_Parent_ToOtherSegment(self) -> None:
		"""A point with a parent is owned, so another segment can't take it without copying."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		point = Point2D(7, 8, parent=line)

		with self.assertRaises(AlreadyOwnedError):
			_ = LineSegment2D(point, Point2D(9, 9), copyPoints=False)

		other = LineSegment2D(point, Point2D(9, 9))

		self.assertIs(other, other.Start.Parent)
		self.assertIsNot(point, other.Start)
		self.assertIs(line, point.Parent)

	def test_Point_Parent_ToParentSegment(self) -> None:
		"""The parent segment can replace its points with a point of which it is the owner."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		start = line.Start
		end = line.End
		newStart = Point2D(7, 8, parent=line)
		newEnd = Point2D(9, 9, parent=line)

		line.Start = newStart
		line.End = newEnd

		self.assertIs(newStart, line.Start)
		self.assertIs(newEnd, line.End)
		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_Point_ReadOnly(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			point.Parent = LineSegment2D(Point2D(0, 0), Point2D(1, 1))

		self.assertEqual("The parent of a 'pyTooling.Cartesian2D.Point2D' is read-only.", str(context.exception))
		self.assertListEqual(
			[
				"Got type 'pyTooling.Cartesian2D.LineSegment2D'.",
				"A segment or shape takes ownership of a point, when it's given the point."
			],
			context.exception.__notes__
		)
		self.assertIsNone(point.Parent)

	def test_Point_Copy(self) -> None:
		"""A copy of an owned point has no owner."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		point = line.Start.Copy()

		self.assertIsNone(point.Parent)

	def test_LineSegment_Copy(self) -> None:
		"""A segment owns copies of the given points; the given points stay without owner."""
		start = Point2D(1, 2)
		end =   Point2D(4, 6)

		line = LineSegment2D(start, end)

		self.assertIsNone(line.Parent)
		self.assertIsNone(line.Frame)
		self.assertIs(line, line.Start.Parent)
		self.assertIs(line, line.End.Parent)
		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_LineSegment_Reference(self) -> None:
		start = Point2D(1, 2)
		end =   Point2D(4, 6)

		line = LineSegment2D(start, end, copyPoints=False)

		self.assertIs(line, start.Parent)
		self.assertIs(line, end.Parent)

	def test_LineSegment_OwnedStart(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = LineSegment2D(line.Start, Point2D(7, 8), copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 2) owned by LineSegment2D((1, 2), (4, 6)).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'start' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(line, line.Start.Parent)

	def test_LineSegment_OwnedEnd(self) -> None:
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		start = Point2D(7, 8)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = LineSegment2D(start, line.End, copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertEqual("Parameter 'end' is owned by another element.", str(context.exception.__cause__))
		self.assertIsNone(start.Parent)
		self.assertIs(line, line.End.Parent)

	def test_LineSegment_SamePoint(self) -> None:
		point = Point2D(1, 2)

		with self.assertRaises(DuplicatePointError) as context:
			_ = LineSegment2D(point, point, copyPoints=False)

		self.assertIsInstance(context.exception, DuplicateElementError)
		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 2).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'end' is the same point as parameter 'start'.", str(context.exception.__cause__))
		self.assertIsNone(point.Parent)

	def test_LineSegment_EqualCoordinates(self) -> None:
		"""Two different point objects with equal coordinates aren't a duplicate."""
		start = Point2D(1, 2)
		end =   Point2D(1, 2)

		line = LineSegment2D(start, end, copyPoints=False)

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertEqual(0.0, line.Length)

	def test_LineSegment_SamePoint_Copy(self) -> None:
		point = Point2D(1, 2)

		line = LineSegment2D(point, point)

		self.assertIsNot(line.Start, line.End)
		self.assertEqual(0.0, line.Length)

	def test_Segment_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Segment2D(Point2D(1, 2), Point2D(4, 6), False)

	def test_LineSegment_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), False)

	def test_LineSegment_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_LineSegment_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), copyPoints=0)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_ParentInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), copyPoints=False, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Shape' or 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_Start(self) -> None:
		"""An assigned start point is owned by the segment, the previous one is released."""
		line =     LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		previous = line.Start
		point =    Point2D(7, 8)

		line.Start = point

		self.assertIs(line, point.Parent)
		self.assertIsNone(previous.Parent)

	def test_LineSegment_Start_Same(self) -> None:
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		start = line.Start

		line.Start = start

		self.assertIs(start, line.Start)
		self.assertIs(line, start.Parent)

	def test_LineSegment_Start_Owned(self) -> None:
		line1 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		line2 = LineSegment2D(Point2D(7, 8), Point2D(9, 9))
		start = line1.Start

		with self.assertRaises(AlreadyOwnedError) as context:
			line1.Start = line2.Start

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(["Got point (7, 8) owned by LineSegment2D((7, 8), (9, 9))."], context.exception.__notes__)
		self.assertEqual("Parameter 'start' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(start, line1.Start)
		self.assertIs(line2, line2.Start.Parent)

	def test_LineSegment_Start_End(self) -> None:
		"""The segment's own end point can't become its start point."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(DuplicatePointError) as context:
			line.Start = line.End

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (4, 6)."], context.exception.__notes__)
		self.assertEqual("Parameter 'start' is the segment's end point.", str(context.exception.__cause__))

	def test_LineSegment_End(self) -> None:
		line =     LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		previous = line.End
		point =    Point2D(7, 8)

		line.End = point

		self.assertIs(line, point.Parent)
		self.assertIsNone(previous.Parent)

	def test_LineSegment_End_Start(self) -> None:
		"""The segment's own start point can't become its end point."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(DuplicatePointError) as context:
			line.End = line.Start

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (1, 2)."], context.exception.__notes__)
		self.assertEqual("Parameter 'end' is the segment's start point.", str(context.exception.__cause__))

	def test_LineSegment_End_Same(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		end =  line.End

		line.End = end

		self.assertIs(end, line.End)
		self.assertIs(line, end.Parent)

	def test_LineSegment_End_Owned(self) -> None:
		line1 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		line2 = LineSegment2D(Point2D(7, 8), Point2D(9, 9))
		end =   line1.End

		with self.assertRaises(AlreadyOwnedError) as context:
			line1.End = line2.End

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(["Got point (9, 9) owned by LineSegment2D((7, 8), (9, 9))."], context.exception.__notes__)
		self.assertEqual("Parameter 'end' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(end, line1.End)


class Node(Base):
	"""A class with a parent, using the setter of :class:`Base`."""

	_PARENT_TYPE = (Point2D, )


class ParentSetter(Testcase):
	def test_Assign(self) -> None:
		point = Point2D(1, 2)
		node =  Node()

		node.Parent = point

		self.assertIs(point, node.Parent)

	def test_AssignNone(self) -> None:
		node = Node(parent=Point2D(1, 2))

		node.Parent = None

		self.assertIsNone(node.Parent)

	def test_AssignInt(self) -> None:
		node = Node()

		with self.assertRaises(TypeError) as context:
			node.Parent = 1

		self.assertEqual("Parameter 'parent' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(node.Parent)


class ParentTypes(Testcase):
	def test_Point(self) -> None:
		self.assertTupleEqual((Element2D, ), Point2D._PARENT_TYPE)

	def test_Origin(self) -> None:
		self.assertTupleEqual((Element2D, ), Origin2D._PARENT_TYPE)

	def test_Segment(self) -> None:
		self.assertTupleEqual((Shape, Group, Canvas), Segment2D._PARENT_TYPE)

	def test_LineSegment(self) -> None:
		self.assertTupleEqual((Shape, Group, Canvas), LineSegment2D._PARENT_TYPE)

	def test_Shape(self) -> None:
		self.assertTupleEqual((Group, Canvas), Shape._PARENT_TYPE)

	def test_Rectangle(self) -> None:
		self.assertTupleEqual((Group, Canvas), Rectangle._PARENT_TYPE)

	def test_Group(self) -> None:
		self.assertTupleEqual((Group, Canvas), Group._PARENT_TYPE)


class Frames(Testcase):
	def test_Point_Minus_Point(self) -> None:
		"""Points of two standalone segments have no frame, so they can be subtracted."""
		line1 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		line2 = LineSegment2D(Point2D(7, 8), Point2D(9, 9))

		offset = line2.Start - line1.Start

		self.assertTupleEqual((6, 6), offset.ToTuple())

	def test_LineSegment_AngleTo(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(1, 0))
		line2 = LineSegment2D(Point2D(5, 5), Point2D(5, 7))

		self.assertTrue(isclose(pi / 2, line1.AngleTo(line2)))


class Aligning(Testcase):
	def test_Left(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.MinX)

		self.assertEqual(BoundingBox(0, 9, 2, 11), circle.BoundingBox)

	def test_CenterX(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.CenterX)

		self.assertEqual(BoundingBox(1, 9, 3, 11), circle.BoundingBox)

	def test_Right(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.MaxX)

		self.assertEqual(BoundingBox(2, 9, 4, 11), circle.BoundingBox)

	def test_MinY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.MinY)

		self.assertEqual(BoundingBox(9, 0, 11, 2), circle.BoundingBox)

	def test_CenterY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.CenterY)

		self.assertEqual(BoundingBox(9, 1, 11, 3), circle.BoundingBox)

	def test_MaxY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment.MaxY)

		self.assertEqual(BoundingBox(9, 0, 11, 2), circle.BoundingBox)

	def test_OtherGroup(self) -> None:
		"""Elements of different groups are aligned by their absolute bounding boxes."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(1, 1), 1)
		_ =         Group(Offset2D(10, 0), (rectangle, ))
		_ =         Group(Offset2D(0, 50), (circle, ))

		circle.AlignTo(rectangle, Alignment.MaxX)

		self.assertEqual(BoundingBox(12, 50, 14, 52), circle.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox(12, 0, 14, 2), circle.BoundingBox)

	def test_Group(self) -> None:
		"""Aligning a group changes its offset."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		group =     Group(Offset2D(10, 10), (Circle(Point2D(1, 1), 1), ))

		group.AlignTo(rectangle, Alignment.MinX)

		self.assertTupleEqual((0, 10), group.Offset.ToTuple())

	def test_ReferenceNone(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(ValueError) as context:
			circle.AlignTo(None, Alignment.MinX)

		self.assertEqual("Parameter 'reference' is None.", str(context.exception))

	def test_ReferencePoint(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(TypeError) as context:
			circle.AlignTo(Point2D(0, 0), Alignment.MinX)

		self.assertEqual("Parameter 'reference' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_AlignmentNone(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(ValueError) as context:
			circle.AlignTo(Circle(Point2D(0, 0), 1), None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_AlignmentStr(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(TypeError) as context:
			circle.AlignTo(Circle(Point2D(0, 0), 1), "Left")

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((10, 10), circle.Center.ToTuple())
