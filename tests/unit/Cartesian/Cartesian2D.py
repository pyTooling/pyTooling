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
from copy                  import copy, deepcopy
from math                  import isclose, pi, sqrt

from pyTooling.Cartesian2D import Origin2D, Point2D, Offset2D, Size2D, Segment2D, LineSegment2D
from pyTooling.Testing     import Testcase


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

		with self.assertRaises(RuntimeError):
			_ = origin.Copy()

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

		with self.assertRaises(RuntimeError):
			_ = copy(origin)

	def test_Origin_deepcopy(self) -> None:
		origin = Origin2D()

		with self.assertRaises(RuntimeError):
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

		with self.assertRaises(RuntimeError):
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
