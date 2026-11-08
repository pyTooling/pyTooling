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

from pyTooling.Cartesian2D        import Base2D, Element2D, Origin2D, Point2D, Offset2D, Size2D, BoundingBox2D, \
                                         Segment2D, LineSegment2D, ArcSegment2D, BezierSegment2D, \
                                         QuadraticBezierSegment2D, CubicBezierSegment2D, Alignment2D, Line2D, \
                                         VerticalLine2D, HorizontalLine2D, Ray2D, SweepDirection, AlreadyOwnedError, \
                                         DuplicatePointError, NoAreaError, NotOwnedError, chordPoint, circumcenter
from pyTooling.Cartesian2D.Shapes import Polygon, Rectangle, Circle, Path, Shape
from pyTooling.Cartesian2D.Groups import Group2D, Canvas2D, YAxisDirection
from pyTooling.Cartesian3D        import Point3D, Offset3D
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


class GeometryFunctions(Testcase):
	def test_chordPoint(self) -> None:
		point = chordPoint(Point2D(0, 0), Point2D(4, 0), 0.5, 0.25)

		self.assertTupleEqual((2.0, 1.0), point.ToTuple())
		self.assertIsNone(point.Parent)

	def test_chordPoint_Right(self) -> None:
		"""A negative height is on the right of the chord."""
		point = chordPoint(Point2D(0, 0), Point2D(0, 4), 0.25, -0.5)

		self.assertTupleEqual((2.0, 1.0), point.ToTuple())

	def test_chordPoint_StartNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			chordPoint(None, Point2D(4, 0), 0.5, 0.25)

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_chordPoint_EndTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			chordPoint(Point2D(0, 0), (4, 0), 0.5, 0.25)

		self.assertEqual("Parameter 'end' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_chordPoint_ChordPositionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			chordPoint(Point2D(0, 0), Point2D(4, 0), None, 0.25)

		self.assertEqual("Parameter 'chordPosition' is None.", str(context.exception))

	def test_chordPoint_RelativeHeightStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			chordPoint(Point2D(0, 0), Point2D(4, 0), 0.5, "1")

		self.assertEqual("Parameter 'relativeHeight' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_circumcenter(self) -> None:
		center = circumcenter(Point2D(0, 0), Point2D(4, 0), Point2D(0, 2))

		self.assertTupleEqual((2.0, 1.0), center.ToTuple())
		self.assertIsNone(center.Parent)

	def test_circumcenter_FirstNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			circumcenter(None, Point2D(4, 0), Point2D(0, 2))

		self.assertEqual("Parameter 'first' is None.", str(context.exception))

	def test_circumcenter_ThirdTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			circumcenter(Point2D(0, 0), Point2D(4, 0), (0, 2))

		self.assertEqual("Parameter 'third' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_circumcenter_OnOneLine(self) -> None:
		with self.assertRaises(ValueError) as context:
			circumcenter(Point2D(0, 0), Point2D(2, 1), Point2D(4, 2))

		self.assertEqual("Parameters 'first', 'second' and 'third' are on one line.", str(context.exception))
		self.assertListEqual(
			["Got points (0, 0), (2, 1) and (4, 2).", "Three points on one line have no circle through them."],
			context.exception.__notes__
		)


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

	def test_LineSegment_deepcopy_Group(self) -> None:
		"""A deep copy owns its points and isn't in the group of the original."""
		group = Group2D()
		line =  LineSegment2D(Point2D(1, 2), Point2D(2, 3), parent=group)

		newLine = deepcopy(line)

		self.assertIsNone(newLine.Parent)
		self.assertIs(newLine, newLine.Start.Parent)
		self.assertIs(newLine, newLine.End.Parent)
		self.assertTupleEqual((line, ), group.Children)

	def test_LineSegment_deepcopy_Edge(self) -> None:
		"""A deep copy of an edge owns copies of the shape's corners and isn't an edge of the shape."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		edge =    polygon.Segments[0]

		newLine = deepcopy(edge)

		self.assertIsNone(newLine.Parent)
		self.assertIs(newLine, newLine.Start.Parent)
		self.assertIsNot(polygon.Points[0], newLine.Start)
		self.assertIs(polygon, polygon.Points[0].Parent)
		self.assertTupleEqual(((0, 0), (4, 0)), newLine.ToTuple())

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


class OffsetVectors(Testcase):
	def test_Length_int(self) -> None:
		offset = Offset2D(3, 4)

		self.assertIsInstance(offset.Length, float)
		self.assertEqual(5.0, offset.Length)

	def test_Length_Zero(self) -> None:
		self.assertEqual(0.0, Offset2D(0, 0).Length)

	def test_Length_ReadOnly(self) -> None:
		offset = Offset2D(3, 4)

		with self.assertRaises(AttributeError):
			offset.Length = 1

	def test_ScalarProduct(self) -> None:
		dot = Offset2D(1, 2).ScalarProduct(Offset2D(3, 4))

		self.assertIsInstance(dot, int)
		self.assertEqual(11, dot)

	def test_ScalarProduct_Perpendicular(self) -> None:
		self.assertEqual(0, Offset2D(1, 2).ScalarProduct(Offset2D(-2, 1)))

	def test_ScalarProduct_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Offset2D(1, 2).ScalarProduct(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_ScalarProduct_Offset3D(self) -> None:
		with self.assertRaises(TypeError) as context:
			Offset2D(1, 2).ScalarProduct(Offset3D(1, 2, 3))

		self.assertEqual("Parameter 'other' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Offset3D'."], context.exception.__notes__)

	def test_VectorProduct(self) -> None:
		cross = Offset2D(1, 2).VectorProduct(Offset2D(3, 4))

		self.assertIsInstance(cross, int)
		self.assertEqual(-2, cross)

	def test_VectorProduct_Counterclockwise(self) -> None:
		self.assertEqual(1, Offset2D(1, 0).VectorProduct(Offset2D(0, 1)))
		self.assertEqual(-1, Offset2D(0, 1).VectorProduct(Offset2D(1, 0)))

	def test_VectorProduct_Parallel(self) -> None:
		self.assertEqual(0, Offset2D(1, 2).VectorProduct(Offset2D(-2, -4)))

	def test_VectorProduct_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Offset2D(1, 2).VectorProduct(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_VectorProduct_Tuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			Offset2D(1, 2).VectorProduct((3, 4))

		self.assertEqual("Parameter 'other' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Normalized(self) -> None:
		offset = Offset2D(3, 4)

		normalized = offset.Normalized()

		self.assertIsNot(offset, normalized)
		self.assertIsInstance(normalized, Offset2D)
		self.assertIsInstance(normalized.XOffset, float)
		self.assertIsInstance(normalized.YOffset, float)
		self.assertEqual(Offset2D(0.6, 0.8), normalized)
		self.assertEqual(Offset2D(3, 4), offset)

	def test_Normalized_Length(self) -> None:
		self.assertTrue(isclose(1.0, Offset2D(-2, 7).Normalized().Length))

	def test_Normalized_Zero(self) -> None:
		with self.assertRaises(InvalidOperationError) as context:
			Offset2D(0, 0).Normalized()

		self.assertEqual("A zero offset can't be normalized.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0).", "A zero offset has no direction."], context.exception.__notes__)

	def test_Multiply_int(self) -> None:
		offset = Offset2D(1, 2)

		product = offset * 3

		self.assertIsNot(offset, product)
		self.assertIsInstance(product, Offset2D)
		self.assertIsInstance(product.XOffset, int)
		self.assertEqual(Offset2D(3, 6), product)
		self.assertEqual(Offset2D(1, 2), offset)

	def test_Multiply_float(self) -> None:
		product = Offset2D(1, 2) * 0.5

		self.assertIsInstance(product.XOffset, float)
		self.assertEqual(Offset2D(0.5, 1.0), product)

	def test_Multiply_Offset(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset2D(1, 2) * Offset2D(3, 4)

		self.assertEqual("Second operand is not supported by * operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.Offset2D'.", "Supported types for second operand: float, int"],
			context.exception.__notes__
		)

	def test_Multiply_str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset2D(1, 2) * "2"

		self.assertEqual("Second operand is not supported by * operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for second operand: float, int"],
			context.exception.__notes__
		)

	def test_ReflectedMultiply_int(self) -> None:
		offset = Offset2D(1, 2)

		product = 3 * offset

		self.assertIsNot(offset, product)
		self.assertIsInstance(product, Offset2D)
		self.assertEqual(Offset2D(3, 6), product)
		self.assertEqual(Offset2D(1, 2), offset)

	def test_ReflectedMultiply_float(self) -> None:
		self.assertEqual(Offset2D(-0.5, -1.0), -0.5 * Offset2D(1, 2))

	def test_ReflectedMultiply_str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = "2" * Offset2D(1, 2)

		self.assertEqual("First operand is not supported by * operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for first operand: float, int"],
			context.exception.__notes__
		)

	def test_InplaceMultiply_int(self) -> None:
		offset =   Offset2D(1, 2)
		original = offset

		offset *= 3

		self.assertIs(original, offset)
		self.assertEqual(Offset2D(3, 6), offset)

	def test_InplaceMultiply_float(self) -> None:
		offset = Offset2D(1, 2)

		offset *= 1.5

		self.assertIsInstance(offset.XOffset, float)
		self.assertEqual(Offset2D(1.5, 3.0), offset)

	def test_InplaceMultiply_Tuple(self) -> None:
		offset = Offset2D(1, 2)

		with self.assertRaises(TypeError) as context:
			offset *= (2, 3)

		self.assertEqual("Second operand is not supported by *= operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: float, int"],
			context.exception.__notes__
		)
		self.assertEqual(Offset2D(1, 2), offset)


class Bounds(Testcase):
	def test_BoundingBox_int(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		self.assertEqual(1, box.MinX)
		self.assertEqual(2, box.MinY)
		self.assertEqual(4, box.MaxX)
		self.assertEqual(6, box.MaxY)
		self.assertEqual(3, box.Width)
		self.assertEqual(4, box.Height)
		self.assertTupleEqual((2.5, 4.0), box.Center.ToTuple())
		self.assertTupleEqual((1, 2, 4, 6), box.ToTuple())

	def test_BoundingBox_float(self) -> None:
		box = BoundingBox2D(-1.5, -2.5, 0.5, 0.5)

		self.assertEqual(2.0, box.Width)
		self.assertEqual(3.0, box.Height)
		self.assertTupleEqual((-0.5, -1.0), box.Center.ToTuple())

	def test_BoundingBox_Point(self) -> None:
		"""A bounding box may have no extent."""
		box = BoundingBox2D(1, 2, 1, 2)

		self.assertEqual(0, box.Width)
		self.assertEqual(0, box.Height)

	def test_BoundingBox_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(None, 2, 4, 6)

		self.assertEqual("Parameter 'minX' is None.", str(context.exception))

	def test_BoundingBox_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(1, None, 4, 6)

		self.assertEqual("Parameter 'minY' is None.", str(context.exception))

	def test_BoundingBox_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(1, 2, None, 6)

		self.assertEqual("Parameter 'maxX' is None.", str(context.exception))

	def test_BoundingBox_None4(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(1, 2, 4, None)

		self.assertEqual("Parameter 'maxY' is None.", str(context.exception))

	def test_BoundingBox_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox2D("1", 2, 4, 6)

		self.assertEqual("Parameter 'minX' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_str4(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox2D(1, 2, 4, "6")

		self.assertEqual("Parameter 'maxY' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_MaxXLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(4, 2, 1, 6)

		self.assertEqual("Parameter 'maxX' is less than parameter 'minX'.", str(context.exception))
		self.assertListEqual(["Got minX=4 and maxX=1."], context.exception.__notes__)

	def test_BoundingBox_MaxYLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D(1, 6, 4, 2)

		self.assertEqual("Parameter 'maxY' is less than parameter 'minY'.", str(context.exception))
		self.assertListEqual(["Got minY=6 and maxY=2."], context.exception.__notes__)

	def test_BoundingBox_ReadOnly(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		with self.assertRaises(AttributeError):
			box.MinX = 0

		self.assertEqual(1, box.MinX)

	def test_FromPoints(self) -> None:
		box = BoundingBox2D.FromPoints((Point2D(3, -1), Point2D(-2, 4), Point2D(1, 1)))

		self.assertIs(BoundingBox2D, type(box))
		self.assertTupleEqual((-2, -1, 3, 4), box.ToTuple())

	def test_FromPoints_Generator(self) -> None:
		box = BoundingBox2D.FromPoints(Point2D(x, 2 * x) for x in range(4))

		self.assertTupleEqual((0, 0, 3, 6), box.ToTuple())

	def test_FromPoints_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D.FromPoints(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_FromPoints_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox2D.FromPoints(3)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_FromPoints_NoneElement(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D.FromPoints((Point2D(0, 0), None))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_FromPoints_tupleElement(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox2D.FromPoints((Point2D(0, 0), (1, 1)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox2D.FromPoints(())

		self.assertEqual("Parameter 'points' is empty.", str(context.exception))

	def test_Union(self) -> None:
		box1 = BoundingBox2D(0, 0, 2, 2)
		box2 = BoundingBox2D(1, -1, 4, 1)

		box = box1.Union(box2)

		self.assertTupleEqual((0, -1, 4, 2), box.ToTuple())
		self.assertTupleEqual((0, 0, 2, 2), box1.ToTuple())
		self.assertTupleEqual((1, -1, 4, 1), box2.ToTuple())

	def test_Union_None(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.Union(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_Union_tuple(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.Union((1, 1, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_HasOverlap(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		self.assertTrue(box.HasOverlap(BoundingBox2D(1, 1, 3, 3)))
		self.assertTrue(box.HasOverlap(BoundingBox2D(-1, -1, 3, 3)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(3, 0, 4, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(0, -2, 2, -1)))

	def test_HasOverlap_Touching(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		self.assertFalse(box.HasOverlap(BoundingBox2D(2, 0, 4, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(-2, 0, 0, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(0, 2, 2, 4)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(0, -2, 2, 0)))
		self.assertFalse(box.HasOverlap(BoundingBox2D(2, 2, 3, 3)))

	def test_HasOverlap_None(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.HasOverlap(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_HasOverlap_tuple(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.HasOverlap((1, 1, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_ContainsPoint(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		self.assertTrue(box.ContainsPoint(Point2D(1, 1)))
		self.assertTrue(box.ContainsPoint(Point2D(2, 0)))
		self.assertFalse(box.ContainsPoint(Point2D(3, 1)))
		self.assertFalse(box.ContainsPoint(Point2D(1, -0.5)))

	def test_ContainsPoint_None(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.ContainsPoint(None)

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_ContainsPoint_tuple(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.ContainsPoint((1, 1))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_In(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		self.assertIn(Point2D(1, 1), box)
		self.assertIn(Point2D(2, 0), box)
		self.assertNotIn(Point2D(3, 1), box)

	def test_In_tuple(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = (1, 1) in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for first operand: Point2D"],
			context.exception.__notes__
		)

	def test_In_None(self) -> None:
		box = BoundingBox2D(0, 0, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = None in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for first operand: Point2D"],
			context.exception.__notes__
		)

	def test_ToRectangle(self) -> None:
		rectangle = BoundingBox2D(1, 2, 4, 6).ToRectangle()

		self.assertIsInstance(rectangle, Rectangle)
		self.assertTupleEqual(
			((1, 2), (1, 6), (4, 6), (4, 2)),
			tuple(point.ToTuple() for point in rectangle.Points)
		)
		self.assertEqual(BoundingBox2D(1, 2, 4, 6), rectangle.BoundingBox)

	def test_ToRectangle_NoArea(self) -> None:
		for box in (BoundingBox2D(1, 2, 1, 6), BoundingBox2D(1, 2, 4, 2)):
			with self.subTest(box=box):
				with self.assertRaises(NoAreaError) as context:
					_ = box.ToRectangle()

				self.assertEqual("Bounding box has no area.", str(context.exception))

	def test_Equal(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		self.assertTrue(box == BoundingBox2D(1, 2, 4, 6))
		self.assertFalse(box == BoundingBox2D(1, 2, 4, 7))
		self.assertFalse(box != BoundingBox2D(1, 2, 4, 6))
		self.assertTrue(box != BoundingBox2D(0, 2, 4, 6))

	def test_Equal_tuple(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box == (1, 2, 4, 6)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox2D"],
			context.exception.__notes__
		)

	def test_Unequal_tuple(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box != (1, 2, 4, 6)

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox2D"],
			context.exception.__notes__
		)

	def test_Plus_Offset(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		newBox = box + Offset2D(10, -2)

		self.assertIs(BoundingBox2D, type(newBox))
		self.assertTupleEqual((11, 0, 14, 4), newBox.ToTuple())
		self.assertTupleEqual((1, 2, 4, 6), box.ToTuple())

	def test_Plus_tuple(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		with self.assertRaises(TypeError) as context:
			_ = box + (10, -2)

		self.assertEqual("Parameter 'other' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Copy(self) -> None:
		box = BoundingBox2D(1, 2, 4, 6)

		for newBox in (box.Copy(), copy(box), deepcopy(box)):
			self.assertIs(BoundingBox2D, type(newBox))
			self.assertIsNot(box, newBox)
			self.assertEqual(box, newBox)

	def test_repr(self) -> None:
		box = BoundingBox2D(1, 2, 4.5, 6)

		self.assertEqual("BoundingBox2D(1, 2, 4.5, 6)", repr(box))

	def test_str(self) -> None:
		box = BoundingBox2D(1, 2, 4.5, 6)

		self.assertEqual("((1, 2), (4.5, 6))", str(box))

	def test_LineSegment(self) -> None:
		line = LineSegment2D(Point2D(4, 1), Point2D(-1, 3))

		box = line.BoundingBox

		self.assertTupleEqual((-1, 1, 4, 3), box.ToTuple())

	def test_LineSegment_ReadOnly(self) -> None:
		line = LineSegment2D(Point2D(4, 1), Point2D(-1, 3))

		with self.assertRaises(AttributeError):
			line.BoundingBox = BoundingBox2D(0, 0, 1, 1)


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
			_ = Base2D()

	def test_Element2D(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Element2D()

	def test_Point(self) -> None:
		self.assertIsInstance(Point2D(1, 2), Base2D)
		self.assertNotIsInstance(Point2D(1, 2), Element2D)

	def test_Origin(self) -> None:
		origin = Origin2D()

		self.assertIsInstance(origin, Base2D)
		self.assertIsNone(origin.Parent)
		self.assertIsNone(origin.Frame)

	def test_Segment(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Segment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertEqual("Class 'Segment2D' is abstract and needs to be derived.", str(context.exception))

	def test_LineSegment(self) -> None:
		self.assertIsInstance(LineSegment2D(Point2D(1, 2), Point2D(4, 6)), Segment2D)
		self.assertIsInstance(LineSegment2D(Point2D(1, 2), Point2D(4, 6)), Element2D)

	def test_Shape(self) -> None:
		self.assertTrue(issubclass(Shape, Element2D))

	def test_Slots(self) -> None:
		"""The parent is a slot of the base-class only, value and key-value-pairs are slots of elements only."""
		self.assertTupleEqual(("_parent", ), Base2D.__slots__)
		self.assertTupleEqual(("_value", "_dict"), Element2D.__slots__)
		self.assertTupleEqual(("_x", "_y"), Point2D.__slots__)
		self.assertNotIn("_parent", Segment2D.__slots__)
		self.assertNotIn("_value", Segment2D.__slots__)


class Mirroring(Testcase):
	def test_MirrorY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorY()

		self.assertTupleEqual(((1, 6), (4, 2)), line.ToTuple())

	def test_MirrorY_MinY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorY(Alignment2D.MinY)

		self.assertTupleEqual(((1, 2), (4, -2)), line.ToTuple())

	def test_MirrorY_MaxY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual(((1, 10), (4, 6)), line.ToTuple())

	def test_MirrorY_Offset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorY(Alignment2D.MinY, 1)

		self.assertTupleEqual(((1, 4), (4, 0)), line.ToTuple())

	def test_MirrorY_FloatOffset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorY(Alignment2D.MaxY, -0.5)

		self.assertTupleEqual(((1, 9.0), (4, 5.0)), line.ToTuple())

	def test_MirrorY_Int(self) -> None:
		"""An axis between two integer coordinates keeps integer coordinates."""
		line = LineSegment2D(Point2D(1, 1), Point2D(4, 6))

		line.MirrorY(Alignment2D.CenterY)

		self.assertTupleEqual(((1, 6), (4, 1)), line.ToTuple())
		self.assertIs(int, type(line.Start.Y))
		self.assertIs(int, type(line.End.Y))

	def test_MirrorY_AxisNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorY(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorY_AxisStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorY("MinY")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorY_AxisX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		for axis in (Alignment2D.MinX, Alignment2D.CenterX, Alignment2D.MaxX):
			with self.subTest(axis=axis):
				with self.assertRaises(ValueError) as context:
					line.MirrorY(axis)

				self.assertEqual(
					"Parameter 'axis' is not Alignment2D.MinY, Alignment2D.CenterY or Alignment2D.MaxY.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment2D.{axis.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorY_OffsetNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorY(Alignment2D.MinY, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorY_OffsetStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorY(Alignment2D.MinY, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX()

		self.assertTupleEqual(((4, 2), (1, 6)), line.ToTuple())

	def test_MirrorX_MinX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual(((1, 2), (-2, 6)), line.ToTuple())

	def test_MirrorX_MaxX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual(((7, 2), (4, 6)), line.ToTuple())

	def test_MirrorX_Offset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX(Alignment2D.MaxX, -1)

		self.assertTupleEqual(((5, 2), (2, 6)), line.ToTuple())

	def test_MirrorX_FloatOffset(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX(Alignment2D.MinX, 0.5)

		self.assertTupleEqual(((2.0, 2), (-1.0, 6)), line.ToTuple())

	def test_MirrorX_Int(self) -> None:
		"""An axis between two integer coordinates keeps integer coordinates."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorX(Alignment2D.CenterX)

		self.assertTupleEqual(((4, 2), (1, 6)), line.ToTuple())
		self.assertIs(int, type(line.Start.X))
		self.assertIs(int, type(line.End.X))

	def test_MirrorX_AxisNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorX(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX_AxisStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorX("MinX")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX_AxisY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		for axis in (Alignment2D.MinY, Alignment2D.CenterY, Alignment2D.MaxY):
			with self.subTest(axis=axis):
				with self.assertRaises(ValueError) as context:
					line.MirrorX(axis)

				self.assertEqual(
					"Parameter 'axis' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment2D.{axis.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX_OffsetNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorX(Alignment2D.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX_OffsetStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorX(Alignment2D.MinX, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())


class Lines(Testcase):
	def test_Line2D(self) -> None:
		line = Line2D(Offset2D(0.6, 0.8), 2.0)

		self.assertEqual(Offset2D(0.6, 0.8), line.Normal)
		self.assertEqual(2.0, line.Distance)

	def test_Normalize(self) -> None:
		"""A normal of another length is normalized, and the distance is divided by its length."""
		line = Line2D(Offset2D(3, 4), 10)

		self.assertIsInstance(line.Normal.XOffset, float)
		self.assertEqual(Offset2D(0.6, 0.8), line.Normal)
		self.assertEqual(2.0, line.Distance)

	def test_Normalize_Copy(self) -> None:
		"""The line stores its own normal, the given one is unchanged."""
		normal = Offset2D(3, 4)

		line = Line2D(normal, 10)

		self.assertIsNot(normal, line.Normal)
		self.assertEqual(Offset2D(3, 4), normal)

	def test_UnitNormal_Int(self) -> None:
		"""A normal of length 1 keeps its values, so integers stay integers."""
		line = Line2D(Offset2D(0, 1), 5)

		self.assertIs(int, type(line.Normal.XOffset))
		self.assertIs(int, type(line.Normal.YOffset))
		self.assertIs(int, type(line.Distance))

	def test_SignRule(self) -> None:
		"""The first non-zero component of the normal is positive: normal and distance are negated otherwise."""
		line = Line2D(Offset2D(-3, 4), 10)

		self.assertEqual(Offset2D(0.6, -0.8), line.Normal)
		self.assertEqual(-2.0, line.Distance)

	def test_SignRule_SecondComponent(self) -> None:
		line = Line2D(Offset2D(0, -2), 4)

		self.assertEqual(Offset2D(0, 1), line.Normal)
		self.assertEqual(-2.0, line.Distance)

	def test_SignRule_NoNegativeZero(self) -> None:
		line = Line2D(Offset2D(-1.0, 0.0), 0.0)

		self.assertEqual("Line2D((1.0, 0.0), 0.0)", repr(line))

	def test_NormalNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D(None, 1)

		self.assertEqual("Parameter 'normal' is None.", str(context.exception))

	def test_NormalTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D((1, 0), 1)

		self.assertEqual("Parameter 'normal' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_NormalZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D(Offset2D(0, 0), 1)

		self.assertEqual("Parameter 'normal' is a zero offset.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0).", "A line needs a normal direction."], context.exception.__notes__)

	def test_DistanceNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D(Offset2D(1, 0), None)

		self.assertEqual("Parameter 'distance' is None.", str(context.exception))

	def test_DistanceStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D(Offset2D(1, 0), "1")

		self.assertEqual("Parameter 'distance' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Immutable(self) -> None:
		line = Line2D(Offset2D(3, 4), 10)

		with self.assertRaises(AttributeError):
			line.Normal = Offset2D(1, 0)

		with self.assertRaises(AttributeError):
			line.Distance = 1

	def test_Derived(self) -> None:
		self.assertIsInstance(VerticalLine2D(5), Line2D)
		self.assertIsInstance(HorizontalLine2D(5), Line2D)

	def test_FromPoints(self) -> None:
		line = Line2D.FromPoints(Point2D(0, 1), Point2D(4, -2))

		self.assertIs(Line2D, type(line))
		self.assertEqual(Offset2D(0.6, 0.8), line.Normal)
		self.assertEqual(0.8, line.Distance)

	def test_FromPoints_Group(self) -> None:
		"""The points are taken in absolute coordinates."""
		segment = LineSegment2D(Point2D(0, 0), Point2D(0, 3))
		Group2D(Offset2D(5, 0), (segment, ))

		line = Line2D.FromPoints(segment.Start, segment.End)

		self.assertEqual(VerticalLine2D(5), line)

	def test_FromPoints_Derived(self) -> None:
		"""A derived class creates a general line."""
		line = VerticalLine2D.FromPoints(Point2D(5, 0), Point2D(5, 3))

		self.assertIs(Line2D, type(line))
		self.assertEqual(VerticalLine2D(5), line)

	def test_FromPoints_FirstNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPoints(None, Point2D(1, 2))

		self.assertEqual("Parameter 'first' is None.", str(context.exception))

	def test_FromPoints_SecondTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D.FromPoints(Point2D(1, 2), (3, 4))

		self.assertEqual("Parameter 'second' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_SamePosition(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPoints(Point2D(1, 2), Point2D(1, 2))

		self.assertEqual("Parameters 'first' and 'second' are at the same position.", str(context.exception))
		self.assertListEqual(
			[
				"Got points (1, 2) and (1, 2), both at (1, 2) in absolute coordinates.",
				"Two points at the same position don't define a line."
			],
			context.exception.__notes__
		)

	def test_FromPoints_SamePosition_Group(self) -> None:
		"""Two points at the same absolute position, but in different frames."""
		segment = LineSegment2D(Point2D(0, 0), Point2D(0, 3))
		Group2D(Offset2D(5, 0), (segment, ))

		with self.assertRaises(ValueError) as context:
			Line2D.FromPoints(segment.Start, Point2D(5, 0))

		self.assertEqual("Parameters 'first' and 'second' are at the same position.", str(context.exception))
		self.assertListEqual(
			[
				"Got points (0, 0) and (5, 0), both at (5, 0) in absolute coordinates.",
				"Two points at the same position don't define a line."
			],
			context.exception.__notes__
		)

	def test_FromPointAndDirection(self) -> None:
		line = Line2D.FromPointAndDirection(Point2D(0, 1), Offset2D(4, -3))

		self.assertIs(Line2D, type(line))
		self.assertEqual(Line2D.FromPoints(Point2D(0, 1), Point2D(4, -2)), line)

	def test_FromPointAndDirection_Horizontal(self) -> None:
		self.assertEqual(HorizontalLine2D(2), Line2D.FromPointAndDirection(Point2D(1, 2), Offset2D(-3, 0)))

	def test_FromPointAndDirection_PointNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndDirection(None, Offset2D(1, 0))

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_FromPointAndDirection_PointOffset(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D.FromPointAndDirection(Offset2D(1, 2), Offset2D(1, 0))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Offset2D'."], context.exception.__notes__)

	def test_FromPointAndDirection_DirectionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndDirection(Point2D(1, 2), None)

		self.assertEqual("Parameter 'direction' is None.", str(context.exception))

	def test_FromPointAndDirection_DirectionPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D.FromPointAndDirection(Point2D(1, 2), Point2D(1, 0))

		self.assertEqual("Parameter 'direction' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_FromPointAndDirection_DirectionZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndDirection(Point2D(1, 2), Offset2D(0, 0))

		self.assertEqual("Parameter 'direction' is a zero offset.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0).", "A line needs a direction."], context.exception.__notes__)

	def test_FromPointAndNormal(self) -> None:
		line = Line2D.FromPointAndNormal(Point2D(6, 8), Offset2D(-3, -4))

		self.assertIs(Line2D, type(line))
		self.assertEqual(Offset2D(0.6, 0.8), line.Normal)
		self.assertEqual(10.0, line.Distance)

	def test_FromPointAndNormal_Group(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		Group2D(Offset2D(10, 20), (circle, ))

		line = Line2D.FromPointAndNormal(circle.Center, Offset2D(0, 1))

		self.assertEqual(HorizontalLine2D(22), line)

	def test_FromPointAndNormal_PointNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndNormal(None, Offset2D(1, 0))

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_FromPointAndNormal_PointTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D.FromPointAndNormal((1, 2), Offset2D(1, 0))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPointAndNormal_NormalNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndNormal(Point2D(1, 2), None)

		self.assertEqual("Parameter 'normal' is None.", str(context.exception))

	def test_FromPointAndNormal_NormalTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			Line2D.FromPointAndNormal(Point2D(1, 2), (1, 0))

		self.assertEqual("Parameter 'normal' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPointAndNormal_NormalZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			Line2D.FromPointAndNormal(Point2D(1, 2), Offset2D(0, 0))

		self.assertEqual("Parameter 'normal' is a zero offset.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0).", "A line needs a normal direction."], context.exception.__notes__)

	def test_SignedDistance(self) -> None:
		line = Line2D(Offset2D(3, 4), 10)

		self.assertEqual(-2.0, line.SignedDistance(Point2D(0, 0)))
		self.assertEqual(3.0, line.SignedDistance(Point2D(3, 4)))
		self.assertEqual(0.0, line.SignedDistance(Point2D(2, 1)))

	def test_SignedDistance_Int(self) -> None:
		distance = VerticalLine2D(5).SignedDistance(Point2D(2, 7))

		self.assertIs(int, type(distance))
		self.assertEqual(-3, distance)

	def test_SignedDistance_Group(self) -> None:
		"""The point is taken in absolute coordinates."""
		circle = Circle(Point2D(1, 2), 1)
		Group2D(Offset2D(10, 20), (circle, ))

		self.assertEqual(6, VerticalLine2D(5).SignedDistance(circle.Center))

	def test_SignedDistance_PointNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D(5).SignedDistance(None)

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_SignedDistance_PointTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D(5).SignedDistance((1, 2))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Project(self) -> None:
		line =  Line2D(Offset2D(3, 4), 10)
		point = Point2D(3, 4)

		projection = line.Project(point)

		self.assertIsNot(point, projection)
		self.assertIsNone(projection.Parent)
		self.assertTrue(isclose(1.2, projection.X))
		self.assertTrue(isclose(1.6, projection.Y))
		self.assertTrue(isclose(0.0, line.SignedDistance(projection), abs_tol=1e-12))

	def test_Project_Group(self) -> None:
		"""The point is taken in absolute coordinates, the projection is in absolute coordinates."""
		circle = Circle(Point2D(1, 2), 1)
		Group2D(Offset2D(10, 20), (circle, ))

		projection = HorizontalLine2D(0).Project(circle.Center)

		self.assertTupleEqual((11, 0), projection.ToTuple())

	def test_Project_PointNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D(5).Project(None)

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_Project_PointOffset(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D(5).Project(Offset2D(1, 2))

		self.assertEqual("Parameter 'point' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Offset2D'."], context.exception.__notes__)

	def test_Intersection(self) -> None:
		line = Line2D(Offset2D(1, 1), 4)
		ray =  Ray2D(Point2D(0, 0), Offset2D(1, 3))

		self.assertTrue(line.Intersects(ray))
		intersection = line.Intersection(ray)
		self.assertIsNone(intersection.Parent)
		self.assertTrue(isclose(1.0, intersection.X))
		self.assertTrue(isclose(3.0, intersection.Y))

	def test_Intersection_Int(self) -> None:
		line = VerticalLine2D(4)
		ray =  Ray2D(Point2D(0, 1), Offset2D(2, 1))

		self.assertTrue(line.Intersects(ray))
		self.assertTupleEqual((4.0, 3.0), line.Intersection(ray).ToTuple())

	def test_Intersection_StartOnLine(self) -> None:
		line = VerticalLine2D(4)
		ray =  Ray2D(Point2D(4, 1), Offset2D(-2, 1))

		self.assertTrue(line.Intersects(ray))
		intersection = line.Intersection(ray)
		self.assertIsNot(ray.Start, intersection)
		self.assertTupleEqual((4, 1), intersection.ToTuple())

	def test_Intersection_AlongLine(self) -> None:
		"""A ray running along the line hits it at its start point."""
		line = HorizontalLine2D(1)
		ray =  Ray2D(Point2D(4, 1), Offset2D(-2, 0))

		self.assertTrue(line.Intersects(ray))
		self.assertTupleEqual((4, 1), line.Intersection(ray).ToTuple())

	def test_Intersection_Parallel(self) -> None:
		line = HorizontalLine2D(1)
		ray =  Ray2D(Point2D(4, 2), Offset2D(-2, 0))

		self.assertFalse(line.Intersects(ray))
		with self.assertRaises(ValueError) as context:
			line.Intersection(ray)

		self.assertEqual("Parameter 'ray' is parallel to the line.", str(context.exception))
		self.assertListEqual(
			["Got ray Ray2D((4, 2), (-2, 0)) and line HorizontalLine2D(1).", "Check with 'Intersects' first."],
			context.exception.__notes__
		)

	def test_Intersection_Behind(self) -> None:
		line = Line2D(Offset2D(1, 1), 4)
		ray =  Ray2D(Point2D(0, 0), Offset2D(-1, 0))

		self.assertFalse(line.Intersects(ray))
		with self.assertRaises(ValueError) as context:
			line.Intersection(ray)

		self.assertEqual("Parameter 'ray' points away from the line.", str(context.exception))
		self.assertListEqual(
			[
				"Got ray Ray2D((0, 0), (-1, 0)) and line Line2D((0.7071067811865475, 0.7071067811865475), "
				"2.82842712474619).",
				"Check with 'Intersects' first."
			],
			context.exception.__notes__
		)

	def test_Intersects_RayNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D(5).Intersects(None)

		self.assertEqual("Parameter 'ray' is None.", str(context.exception))

	def test_Intersects_RayLine(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D(5).Intersects(VerticalLine2D(6))

		self.assertEqual("Parameter 'ray' is not of type 'Ray2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.VerticalLine2D'."], context.exception.__notes__)

	def test_Intersection_RayNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D(5).Intersection(None)

		self.assertEqual("Parameter 'ray' is None.", str(context.exception))

	def test_Intersection_RayLine(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D(5).Intersection(VerticalLine2D(6))

		self.assertEqual("Parameter 'ray' is not of type 'Ray2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.VerticalLine2D'."], context.exception.__notes__)

	def test_Equal(self) -> None:
		"""Equality is geometric: lines created by different classes and constructors are equal."""
		self.assertTrue(VerticalLine2D(5) == Line2D(Offset2D(1, 0), 5))
		self.assertTrue(Line2D(Offset2D(1, 0), 5) == Line2D.FromPoints(Point2D(5, 0), Point2D(5, 3)))
		self.assertTrue(VerticalLine2D(5) == Line2D.FromPoints(Point2D(5, 0), Point2D(5, 3)))
		self.assertTrue(Line2D(Offset2D(3, 4), 10) == Line2D(Offset2D(-6, -8), -20))
		self.assertFalse(Line2D(Offset2D(3, 4), 10) == Line2D(Offset2D(3, 4), -10))

	def test_Unequal(self) -> None:
		self.assertTrue(Line2D(Offset2D(3, 4), 10) != Line2D(Offset2D(3, 4), -10))
		self.assertTrue(Line2D(Offset2D(3, 4), 10) != Line2D(Offset2D(4, 3), 10))
		self.assertFalse(VerticalLine2D(5) != Line2D(Offset2D(2, 0), 10))

	def test_EqualRay(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Line2D(Offset2D(3, 4), 10) == Ray2D(Point2D(1, 2), Offset2D(3, 4))

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.Ray2D'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Line2D(Offset2D(3, 4), 10) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		"""Equal lines hash alike, also across the hierarchy and for 1 and 1.0."""
		lines = {
			VerticalLine2D(5),
			Line2D(Offset2D(1, 0), 5),
			Line2D.FromPoints(Point2D(5, 0), Point2D(5, 3)),
			VerticalLine2D(5.0),
			HorizontalLine2D(5)
		}

		self.assertEqual(2, len(lines))

	def test_repr(self) -> None:
		self.assertEqual("Line2D((0.6, 0.8), 2.0)", repr(Line2D(Offset2D(3, 4), 10)))

	def test_str(self) -> None:
		self.assertEqual("0.6 * x + 0.8 * y = 2.0", str(Line2D(Offset2D(3, 4), 10)))

	def test_str_NegativeY(self) -> None:
		self.assertEqual("0.6 * x - 0.8 * y = -2.0", str(Line2D(Offset2D(-3, 4), 10)))


class VerticalLines(Testcase):
	def test_VerticalLine2D(self) -> None:
		line = VerticalLine2D(5)

		self.assertEqual(5, line.X)

	def test_VerticalLine2D_Float(self) -> None:
		line = VerticalLine2D(-2.5)

		self.assertEqual(-2.5, line.X)

	def test_XNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D(None)

		self.assertEqual("Parameter 'x' is None.", str(context.exception))

	def test_XStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D("5")

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Immutable(self) -> None:
		line = VerticalLine2D(5)

		with self.assertRaises(AttributeError):
			line.X = 6

		self.assertEqual(VerticalLine2D(5), line)

	def test_Equal(self) -> None:
		self.assertTrue(VerticalLine2D(5) == VerticalLine2D(5.0))
		self.assertFalse(VerticalLine2D(5) == VerticalLine2D(6))
		self.assertFalse(VerticalLine2D(5) == HorizontalLine2D(5))

	def test_Unequal(self) -> None:
		self.assertTrue(VerticalLine2D(5) != VerticalLine2D(6))
		self.assertTrue(VerticalLine2D(5) != HorizontalLine2D(5))
		self.assertFalse(VerticalLine2D(5) != VerticalLine2D(5))

	def test_EqualTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = VerticalLine2D(5) == (5, )

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = VerticalLine2D(5) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		lines = {VerticalLine2D(5), VerticalLine2D(5.0), VerticalLine2D(6)}

		self.assertEqual(2, len(lines))

	def test_repr(self) -> None:
		self.assertEqual("VerticalLine2D(5)", repr(VerticalLine2D(5)))

	def test_str(self) -> None:
		self.assertEqual("x = -2.5", str(VerticalLine2D(-2.5)))

	def test_FromElement_MinX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertEqual(VerticalLine2D(1), VerticalLine2D.FromElement(line, Alignment2D.MinX))

	def test_FromElement_CenterX(self) -> None:
		"""The coordinate of a center is a float, as the center of a bounding box."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		center = VerticalLine2D.FromElement(line, Alignment2D.CenterX)

		self.assertEqual(VerticalLine2D(2.5), center)
		self.assertIs(float, type(center.X))

	def test_FromElement_MaxX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertEqual(VerticalLine2D(4), VerticalLine2D.FromElement(line, Alignment2D.MaxX))

	def test_FromElement_Group(self) -> None:
		"""The line runs through the absolute bounding box of an element inside a group."""
		circle = Circle(Point2D(1, 2), 1)
		_ =      Group2D(Offset2D(10, 20), (circle, ))

		self.assertEqual(VerticalLine2D(12), VerticalLine2D.FromElement(circle, Alignment2D.MaxX))

	def test_FromElement_ElementNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			VerticalLine2D.FromElement(None, Alignment2D.MinX)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_FromElement_ElementPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			VerticalLine2D.FromElement(Point2D(1, 2), Alignment2D.MinX)

		self.assertEqual("Parameter 'element' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_FromElement_AlignmentNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			VerticalLine2D.FromElement(line, None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_FromElement_AlignmentStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			VerticalLine2D.FromElement(line, "MinX")

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_FromElement_AlignmentMinY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			VerticalLine2D.FromElement(line, Alignment2D.MinY)

		self.assertEqual(
			"Parameter 'alignment' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got value 'Alignment2D.MinY'.", "Use 'HorizontalLine2D.FromElement' for the other alignments."],
			context.exception.__notes__
		)


class HorizontalLines(Testcase):
	def test_HorizontalLine2D(self) -> None:
		line = HorizontalLine2D(5)

		self.assertEqual(5, line.Y)

	def test_HorizontalLine2D_Float(self) -> None:
		line = HorizontalLine2D(-2.5)

		self.assertEqual(-2.5, line.Y)

	def test_YNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			HorizontalLine2D(None)

		self.assertEqual("Parameter 'y' is None.", str(context.exception))

	def test_YStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			HorizontalLine2D("5")

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Immutable(self) -> None:
		line = HorizontalLine2D(5)

		with self.assertRaises(AttributeError):
			line.Y = 6

		self.assertEqual(HorizontalLine2D(5), line)

	def test_Equal(self) -> None:
		self.assertTrue(HorizontalLine2D(5) == HorizontalLine2D(5.0))
		self.assertFalse(HorizontalLine2D(5) == HorizontalLine2D(6))
		self.assertFalse(HorizontalLine2D(5) == VerticalLine2D(5))

	def test_Unequal(self) -> None:
		self.assertTrue(HorizontalLine2D(5) != HorizontalLine2D(6))
		self.assertTrue(HorizontalLine2D(5) != VerticalLine2D(5))
		self.assertFalse(HorizontalLine2D(5) != HorizontalLine2D(5))

	def test_EqualTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = HorizontalLine2D(5) == (5, )

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = HorizontalLine2D(5) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Line2D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		lines = {HorizontalLine2D(5), HorizontalLine2D(5.0), HorizontalLine2D(6)}

		self.assertEqual(2, len(lines))

	def test_repr(self) -> None:
		self.assertEqual("HorizontalLine2D(5)", repr(HorizontalLine2D(5)))

	def test_str(self) -> None:
		self.assertEqual("y = -2.5", str(HorizontalLine2D(-2.5)))

	def test_FromElement_MinY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertEqual(HorizontalLine2D(2), HorizontalLine2D.FromElement(line, Alignment2D.MinY))

	def test_FromElement_CenterY(self) -> None:
		"""The coordinate of a center is a float, as the center of a bounding box."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		center = HorizontalLine2D.FromElement(line, Alignment2D.CenterY)

		self.assertEqual(HorizontalLine2D(4), center)
		self.assertIs(float, type(center.Y))

	def test_FromElement_MaxY(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertEqual(HorizontalLine2D(6), HorizontalLine2D.FromElement(line, Alignment2D.MaxY))

	def test_FromElement_Group(self) -> None:
		"""The line runs through the absolute bounding box of an element inside a group."""
		circle = Circle(Point2D(1, 2), 1)
		_ =      Group2D(Offset2D(10, 20), (circle, ))

		self.assertEqual(HorizontalLine2D(23), HorizontalLine2D.FromElement(circle, Alignment2D.MaxY))

	def test_FromElement_ElementNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			HorizontalLine2D.FromElement(None, Alignment2D.MinY)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_FromElement_ElementPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			HorizontalLine2D.FromElement(Point2D(1, 2), Alignment2D.MinY)

		self.assertEqual("Parameter 'element' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_FromElement_AlignmentNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			HorizontalLine2D.FromElement(line, None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_FromElement_AlignmentStr(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			HorizontalLine2D.FromElement(line, "MinY")

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_FromElement_AlignmentMinX(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			HorizontalLine2D.FromElement(line, Alignment2D.MinX)

		self.assertEqual(
			"Parameter 'alignment' is not Alignment2D.MinY, Alignment2D.CenterY or Alignment2D.MaxY.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got value 'Alignment2D.MinX'.", "Use 'VerticalLine2D.FromElement' for the other alignments."],
			context.exception.__notes__
		)


class Rays(Testcase):
	def test_Ray2D(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		self.assertTupleEqual((1, 2), ray.Start.ToTuple())
		self.assertTupleEqual((3, 4), ray.Direction.ToTuple())

	def test_Copies(self) -> None:
		"""The ray copies the given point and offset; its properties return the stored objects."""
		start =     Point2D(1, 2)
		direction = Offset2D(3, 4)
		ray =       Ray2D(start, direction)

		start += Offset2D(3, 4)
		direction.XOffset = 7

		self.assertTupleEqual((1, 2), ray.Start.ToTuple())
		self.assertTupleEqual((3, 4), ray.Direction.ToTuple())
		self.assertIsNone(ray.Start.Parent)
		self.assertIs(ray.Start, ray.Start)
		self.assertIs(ray.Direction, ray.Direction)

	def test_StartInGroup(self) -> None:
		"""A start point inside a group is taken in absolute coordinates."""
		group = Group2D(Offset2D(10, 20))
		start = Point2D(1, 2, parent=group)

		ray = Ray2D(start, Offset2D(3, 4))

		self.assertTupleEqual((11, 22), ray.Start.ToTuple())
		self.assertIs(group, start.Parent)

	def test_StartNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray2D(None, Offset2D(3, 4))

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_StartOffset(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray2D(Offset2D(1, 2), Offset2D(3, 4))

		self.assertEqual("Parameter 'start' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Offset2D'."], context.exception.__notes__)

	def test_Start3D(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray2D(Point3D(1, 2, 3), Offset2D(3, 4))

		self.assertEqual("Parameter 'start' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_DirectionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray2D(Point2D(1, 2), None)

		self.assertEqual("Parameter 'direction' is None.", str(context.exception))

	def test_Direction3D(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray2D(Point2D(1, 2), Offset3D(3, 4, 0))

		self.assertEqual("Parameter 'direction' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Offset3D'."], context.exception.__notes__)

	def test_DirectionZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray2D(Point2D(1, 2), Offset2D(0, 0))

		self.assertEqual("Parameter 'direction' is a zero offset.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0).", "A ray needs a direction."], context.exception.__notes__)

	def test_Immutable(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		with self.assertRaises(AttributeError):
			ray.Start = Point2D(0, 0)

		with self.assertRaises(AttributeError):
			ray.Direction = Offset2D(6, 8)

		self.assertEqual(Ray2D(Point2D(1, 2), Offset2D(3, 4)), ray)

	def test_PointAt(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		point = ray.PointAt(5)

		self.assertTupleEqual((4.0, 6.0), point.ToTuple())
		self.assertIsNone(point.Parent)

	def test_PointAt_Zero(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		self.assertTupleEqual((1, 2), ray.PointAt(0).ToTuple())

	def test_PointAt_DirectionLength(self) -> None:
		"""The distance doesn't depend on the length of the direction."""
		ray1 = Ray2D(Point2D(1, 2), Offset2D(3, 4))
		ray2 = Ray2D(Point2D(1, 2), Offset2D(6, 8))

		self.assertTupleEqual(ray1.PointAt(10).ToTuple(), ray2.PointAt(10).ToTuple())

	def test_PointAt_DistanceNone(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		with self.assertRaises(ValueError) as context:
			ray.PointAt(None)

		self.assertEqual("Parameter 'distance' is None.", str(context.exception))

	def test_PointAt_DistanceStr(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		with self.assertRaises(TypeError) as context:
			ray.PointAt("5")

		self.assertEqual("Parameter 'distance' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_PointAt_DistanceNegative(self) -> None:
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		with self.assertRaises(ValueError) as context:
			ray.PointAt(-1)

		self.assertEqual("Parameter 'distance' is negative.", str(context.exception))
		self.assertListEqual(
			["Got value '-1'.", "A point before the start point isn't on the ray."],
			context.exception.__notes__
		)

	def test_Equal(self) -> None:
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(3, 4)))
		self.assertFalse(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(3, 4), Offset2D(3, 4)))

	def test_Equal_Scaled(self) -> None:
		"""Directions pointing the same way are equal, whatever their lengths."""
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(6, 8)))
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(1.5, 2.0)))

	def test_Equal_Opposite(self) -> None:
		self.assertFalse(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(-3, -4)))

	def test_Equal_OtherDirection(self) -> None:
		self.assertFalse(Ray2D(Point2D(1, 2), Offset2D(3, 4)) == Ray2D(Point2D(1, 2), Offset2D(4, 3)))

	def test_Unequal(self) -> None:
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) != Ray2D(Point2D(3, 4), Offset2D(3, 4)))
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) != Ray2D(Point2D(1, 2), Offset2D(-3, -4)))
		self.assertTrue(Ray2D(Point2D(1, 2), Offset2D(3, 4)) != Ray2D(Point2D(1, 2), Offset2D(4, 3)))
		self.assertFalse(Ray2D(Point2D(1, 2), Offset2D(3, 4)) != Ray2D(Point2D(1, 2), Offset2D(3, 4)))
		self.assertFalse(Ray2D(Point2D(1, 2), Offset2D(3, 4)) != Ray2D(Point2D(1, 2), Offset2D(6, 8)))

	def test_EqualTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ray2D(Point2D(1, 2), Offset2D(3, 4)) == ((1, 2), (3, 4))

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: Ray2D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ray2D(Point2D(1, 2), Offset2D(3, 4)) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Ray2D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		"""A ray is unhashable, as its start point and direction can be changed."""
		ray = Ray2D(Point2D(1, 2), Offset2D(3, 4))

		with self.assertRaises(TypeError) as context:
			hash(ray)

		self.assertEqual("unhashable type: 'Ray2D'", str(context.exception))

	def test_repr(self) -> None:
		self.assertEqual("Ray2D((1, 2), (3, 4))", repr(Ray2D(Point2D(1, 2), Offset2D(3, 4))))

	def test_str(self) -> None:
		self.assertEqual("(1, 2) + t * (3, 4), t >= 0", str(Ray2D(Point2D(1, 2), Offset2D(3, 4))))


class MirroringAtLine(Testcase):
	def test_Vertical(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(VerticalLine2D(10))

		self.assertTupleEqual(((19, 2), (16, 6)), line.ToTuple())

	def test_Horizontal(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(HorizontalLine2D(0))

		self.assertTupleEqual(((1, -2), (4, -6)), line.ToTuple())

	def test_Float(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(VerticalLine2D(0.5))

		self.assertTupleEqual(((0.0, 2), (-3.0, 6)), line.ToTuple())

	def test_Int(self) -> None:
		"""A line at an integer coordinate keeps integer coordinates."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(HorizontalLine2D(3))

		self.assertTupleEqual(((1, 4), (4, 0)), line.ToTuple())
		self.assertIs(int, type(line.Start.Y))
		self.assertIs(int, type(line.End.Y))

	def test_Twice(self) -> None:
		line =   LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		mirror = VerticalLine2D(-3)

		line.MirrorAt(mirror)
		line.MirrorAt(mirror)

		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_MirrorX(self) -> None:
		"""Mirroring at the line through an edge of the element equals mirroring at that edge."""
		line1 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		line2 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line1.MirrorAt(VerticalLine2D.FromElement(line1, Alignment2D.MaxX))
		line2.MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual(line2.ToTuple(), line1.ToTuple())

	def test_SameLine(self) -> None:
		"""Several elements mirrored at the same line keep their distances to each other."""
		left =   LineSegment2D(Point2D(0, 0), Point2D(1, 1))
		right =  LineSegment2D(Point2D(3, 0), Point2D(4, 1))
		mirror = VerticalLine2D.FromElement(right, Alignment2D.MaxX)

		left.MirrorAt(mirror)
		right.MirrorAt(mirror)

		self.assertTupleEqual(((8, 0), (7, 1)), left.ToTuple())
		self.assertTupleEqual(((5, 0), (4, 1)), right.ToTuple())

	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.MirrorAt(HorizontalLine2D(5))

		self.assertTupleEqual(((0, 10), (4, 9), (2, 7)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertTupleEqual(((0, 10), (4, 9)), polygon.Segments[0].ToTuple())

	def test_Edge(self) -> None:
		"""An edge mirrors the polygon's corners it references."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.Segments[0].MirrorAt(VerticalLine2D(2))

		self.assertTupleEqual(((4, 0), (0, 1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Arc(self) -> None:
		"""Mirroring reverses the direction of an arc."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		arc.MirrorAt(VerticalLine2D(2))

		self.assertTupleEqual((3, 0), arc.Start.ToTuple())
		self.assertTupleEqual((4, 1), arc.End.ToTuple())
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)

	def test_Line2D_Vertical(self) -> None:
		"""A general line with normal (1, 0) mirrors like a vertical line."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(Line2D.FromPoints(Point2D(10, 0), Point2D(10, -7)))

		self.assertTupleEqual(((19.0, 2), (16.0, 6)), line.ToTuple())

	def test_Line2D_Horizontal(self) -> None:
		"""A general line with normal (0, 1) mirrors like a horizontal line, keeping integers for a unit normal."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(Line2D(Offset2D(0, -1), -3))

		self.assertTupleEqual(((1, 4), (4, 0)), line.ToTuple())
		self.assertIs(int, type(line.Start.Y))

	def test_Line2D_Group(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		Group2D(Offset2D(10, 0), (circle, ))

		circle.MirrorAt(Line2D(Offset2D(1, 0), 20))

		self.assertTupleEqual((19, 2), circle.Center.ToTuple())
		self.assertTupleEqual((29, 2), circle.Center.Absolute.ToTuple())

	def test_LineNone(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(ValueError) as context:
			line.MirrorAt(None)

		self.assertEqual("Parameter 'line' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())

	def test_LineAlignment(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		with self.assertRaises(TypeError) as context:
			line.MirrorAt(Alignment2D.MaxX)

		self.assertEqual("Parameter 'line' is not of type 'Line2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2), (4, 6)), line.ToTuple())


class MirroringAtObliqueLine(Testcase):
	def test_Diagonal(self) -> None:
		"""Mirroring at the line x = y swaps the coordinates."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line.MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(2, line.Start.X)
		self.assertAlmostEqual(1, line.Start.Y)
		self.assertAlmostEqual(6, line.End.X)
		self.assertAlmostEqual(4, line.End.Y)

	def test_OffsetLine(self) -> None:
		"""Mirroring at the line 3x + 4y = 25, which doesn't run through the origin."""
		line = LineSegment2D(Point2D(0, 0), Point2D(3, 4))

		line.MirrorAt(Line2D(Offset2D(3, 4), 25))

		self.assertAlmostEqual(6, line.Start.X)
		self.assertAlmostEqual(8, line.Start.Y)
		self.assertAlmostEqual(3, line.End.X)
		self.assertAlmostEqual(4, line.End.Y)

	def test_Twice(self) -> None:
		line =   LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		mirror = Line2D(Offset2D(1, 2), 3)

		line.MirrorAt(mirror)
		line.MirrorAt(mirror)

		self.assertAlmostEqual(1, line.Start.X)
		self.assertAlmostEqual(2, line.Start.Y)
		self.assertAlmostEqual(4, line.End.X)
		self.assertAlmostEqual(6, line.End.Y)

	def test_TwoDiagonals(self) -> None:
		"""Mirroring at x = y and at x = -y equals mirroring at both axes."""
		line1 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		line2 = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line1.MirrorAt(Line2D(Offset2D(1, -1), 0))
		line1.MirrorAt(Line2D(Offset2D(1, 1), 0))
		line2.MirrorAt(VerticalLine2D(0))
		line2.MirrorAt(HorizontalLine2D(0))

		self.assertTupleEqual(((-1, -2), (-4, -6)), line2.ToTuple())
		self.assertAlmostEqual(-1, line1.Start.X)
		self.assertAlmostEqual(-2, line1.Start.Y)
		self.assertAlmostEqual(-4, line1.End.X)
		self.assertAlmostEqual(-6, line1.End.Y)

	def test_SignedDistance(self) -> None:
		"""A mirrored point has the negated signed distance, and both have the same projection."""
		mirror = Line2D(Offset2D(1, 2), 3)
		line =   LineSegment2D(Point2D(4, 1), Point2D(-2, 5))
		start =  line.Start.Copy()

		line.MirrorAt(mirror)

		self.assertAlmostEqual(-mirror.SignedDistance(start), mirror.SignedDistance(line.Start))
		self.assertAlmostEqual(mirror.Project(start).X, mirror.Project(line.Start).X)
		self.assertAlmostEqual(mirror.Project(start).Y, mirror.Project(line.Start).Y)

	def test_Arc(self) -> None:
		"""Mirroring reverses the direction of an arc and mirrors its center."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		arc.MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(0, arc.Start.X)
		self.assertAlmostEqual(1, arc.Start.Y)
		self.assertAlmostEqual(1, arc.End.X)
		self.assertAlmostEqual(0, arc.End.Y)
		self.assertAlmostEqual(0, arc.Center.X)
		self.assertAlmostEqual(0, arc.Center.Y)
		self.assertIs(SweepDirection.Clockwise, arc.Direction)

	def test_QuadraticBezier(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(1, 0), Point2D(3, 1), Point2D(2, 4))

		curve.MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(0, curve.Start.X)
		self.assertAlmostEqual(1, curve.Start.Y)
		self.assertAlmostEqual(1, curve.ControlPoint.X)
		self.assertAlmostEqual(3, curve.ControlPoint.Y)
		self.assertAlmostEqual(4, curve.End.X)
		self.assertAlmostEqual(2, curve.End.Y)

	def test_CubicBezier(self) -> None:
		curve = CubicBezierSegment2D(Point2D(1, 0), Point2D(3, 1), Point2D(5, 2), Point2D(2, 4))

		curve.MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(1, curve.ControlPoint1.X)
		self.assertAlmostEqual(3, curve.ControlPoint1.Y)
		self.assertAlmostEqual(2, curve.ControlPoint2.X)
		self.assertAlmostEqual(5, curve.ControlPoint2.Y)

	def test_Edge(self) -> None:
		"""An edge mirrors the polygon's corners it references."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.Segments[0].MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(0, polygon.Points[0].X)
		self.assertAlmostEqual(0, polygon.Points[0].Y)
		self.assertAlmostEqual(1, polygon.Points[1].X)
		self.assertAlmostEqual(4, polygon.Points[1].Y)
		self.assertTupleEqual((2, 3), polygon.Points[2].ToTuple())

	def test_Group(self) -> None:
		"""The line is in absolute coordinates, an element in a group is mirrored in its frame."""
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		Group2D(Offset2D(10, 20), (line, ))

		line.MirrorAt(Line2D.FromPoints(Point2D(0, 0), Point2D(1, 1)))

		self.assertAlmostEqual(22, line.Start.Absolute.X)
		self.assertAlmostEqual(11, line.Start.Absolute.Y)
		self.assertAlmostEqual(26, line.End.Absolute.X)
		self.assertAlmostEqual(14, line.End.Absolute.Y)
		self.assertAlmostEqual(12, line.Start.X)
		self.assertAlmostEqual(-9, line.Start.Y)


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
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), False)

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

		self.assertEqual("Parameter 'parent' is not of type 'Shape' or 'Group2D' or 'Canvas2D'.", str(context.exception))
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


class Node(Base2D):
	"""A class with a parent, using the setter of :class:`Base2D`."""

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
		self.assertTupleEqual((Shape, Group2D, Canvas2D), Segment2D._PARENT_TYPE)

	def test_LineSegment(self) -> None:
		self.assertTupleEqual((Shape, Group2D, Canvas2D), LineSegment2D._PARENT_TYPE)

	def test_ArcSegment(self) -> None:
		self.assertTupleEqual((Shape, Group2D, Canvas2D), ArcSegment2D._PARENT_TYPE)

	def test_QuadraticBezierSegment(self) -> None:
		self.assertTupleEqual((Shape, Group2D, Canvas2D), QuadraticBezierSegment2D._PARENT_TYPE)

	def test_CubicBezierSegment(self) -> None:
		self.assertTupleEqual((Shape, Group2D, Canvas2D), CubicBezierSegment2D._PARENT_TYPE)

	def test_Shape(self) -> None:
		self.assertTupleEqual((Group2D, Canvas2D), Shape._PARENT_TYPE)

	def test_Rectangle(self) -> None:
		self.assertTupleEqual((Group2D, Canvas2D), Rectangle._PARENT_TYPE)

	def test_Group(self) -> None:
		self.assertTupleEqual((Group2D, Canvas2D), Group2D._PARENT_TYPE)


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

		circle.AlignTo(rectangle, Alignment2D.MinX)

		self.assertEqual(BoundingBox2D(0, 9, 2, 11), circle.BoundingBox)

	def test_CenterX(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment2D.CenterX)

		self.assertEqual(BoundingBox2D(1, 9, 3, 11), circle.BoundingBox)

	def test_Right(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment2D.MaxX)

		self.assertEqual(BoundingBox2D(2, 9, 4, 11), circle.BoundingBox)

	def test_MinY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment2D.MinY)

		self.assertEqual(BoundingBox2D(9, 0, 11, 2), circle.BoundingBox)

	def test_CenterY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 4), Point2D(0, 4))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment2D.CenterY)

		self.assertEqual(BoundingBox2D(9, 1, 11, 3), circle.BoundingBox)

	def test_MaxY(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)

		circle.AlignTo(rectangle, Alignment2D.MaxY)

		self.assertEqual(BoundingBox2D(9, 0, 11, 2), circle.BoundingBox)

	def test_OtherGroup(self) -> None:
		"""Elements of different groups are aligned by their absolute bounding boxes."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(1, 1), 1)
		_ =         Group2D(Offset2D(10, 0), (rectangle, ))
		_ =         Group2D(Offset2D(0, 50), (circle, ))

		circle.AlignTo(rectangle, Alignment2D.MaxX)

		self.assertEqual(BoundingBox2D(12, 50, 14, 52), circle.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox2D(12, 0, 14, 2), circle.BoundingBox)

	def test_Group(self) -> None:
		"""Aligning a group changes its offset."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		group =     Group2D(Offset2D(10, 10), (Circle(Point2D(1, 1), 1), ))

		group.AlignTo(rectangle, Alignment2D.MinX)

		self.assertTupleEqual((0, 10), group.Offset.ToTuple())

	def test_ReferenceNone(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(ValueError) as context:
			circle.AlignTo(None, Alignment2D.MinX)

		self.assertEqual("Parameter 'reference' is None.", str(context.exception))

	def test_ReferencePoint(self) -> None:
		circle = Circle(Point2D(10, 10), 1)

		with self.assertRaises(TypeError) as context:
			circle.AlignTo(Point2D(0, 0), Alignment2D.MinX)

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

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((10, 10), circle.Center.ToTuple())


class ElementData(Testcase):
	def test_Segment(self) -> None:
		value =   object()
		pairs =   {"layer": 1}
		segment = LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=value, keyValuePairs=pairs)

		self.assertIs(value, segment.Value)
		self.assertEqual(1, segment["layer"])
		self.assertIsNot(pairs, segment._dict)

	def test_Segment_Default(self) -> None:
		segment = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertIsNone(segment.Value)
		self.assertEqual(0, len(segment))

	def test_Segment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment(self) -> None:
		value = object()
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=value, keyValuePairs={"layer": 1})

		self.assertIs(value, line.Value)
		self.assertEqual(1, line["layer"])

	def test_LineSegment_Value(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=1)

		line.Value = "wire"

		self.assertEqual("wire", line.Value)

	def test_LineSegment_Pairs(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		line["layer"] = 1
		line["net"] =   "clock"

		self.assertEqual(2, len(line))
		self.assertIn("layer", line)
		self.assertEqual("clock", line["net"])
		self.assertEqual("clock", line.get("net"))
		self.assertIsNone(line.get("width"))
		self.assertEqual(1.0, line.get("width", 1.0))
		self.assertListEqual(["layer", "net"], list(line))

		del line["layer"]

		self.assertNotIn("layer", line)
		self.assertEqual(1, len(line))

	def test_LineSegment_Edge(self) -> None:
		"""Edges of a shape are elements too, but have no value or key-value-pairs of their own."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), value=1, keyValuePairs={"a": 1})

		for edge in rectangle.Segments:
			self.assertIsNone(edge.Value)
			self.assertEqual(0, len(edge))

	def test_LineSegment_Copy(self) -> None:
		value = [1, 2]
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=value, keyValuePairs={"layer": 1, "nets": ["a"]})

		newLine =          line.Copy()
		newLine["layer"] = 2

		self.assertIs(value, newLine.Value)
		self.assertEqual(1, line["layer"])
		self.assertEqual(2, newLine["layer"])
		self.assertIs(line["nets"], newLine["nets"])

	def test_LineSegment_copy(self) -> None:
		value = [1, 2]
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=value, keyValuePairs={"layer": 1})

		newLine = copy(line)

		self.assertIs(value, newLine.Value)
		self.assertEqual(1, newLine["layer"])
		self.assertIsNot(line._dict, newLine._dict)

	def test_LineSegment_deepcopy(self) -> None:
		"""A deep copy copies the value and the values of the key-value-pairs too."""
		value = [1, 2]
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), value=value, keyValuePairs={"nets": ["a"]})

		newLine = deepcopy(line)

		self.assertIsNot(value, newLine.Value)
		self.assertListEqual([1, 2], newLine.Value)
		self.assertIsNot(line["nets"], newLine["nets"])
		self.assertListEqual(["a"], newLine["nets"])

	def test_ArcSegment(self) -> None:
		value = object()
		pairs = {"layer": 1}
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, value=value, keyValuePairs=pairs)

		self.assertIs(value, arc.Value)
		self.assertEqual(1, arc["layer"])
		self.assertIsNot(pairs, arc._dict)

	def test_ArcSegment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_ArcSegment_Copy(self) -> None:
		value = [1, 2]
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, value=value, keyValuePairs={"layer": 1})

		newArc =          arc.Copy()
		newArc["layer"] = 2

		self.assertIs(value, newArc.Value)
		self.assertEqual(1, arc["layer"])
		self.assertEqual(2, newArc["layer"])
		self.assertIs(value, copy(arc).Value)

	def test_ArcSegment_deepcopy(self) -> None:
		value = [1, 2]
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, value=value, keyValuePairs={"nets": ["a"]})

		newArc = deepcopy(arc)

		self.assertIsNot(value, newArc.Value)
		self.assertListEqual([1, 2], newArc.Value)
		self.assertIsNot(arc["nets"], newArc["nets"])
		self.assertIs(newArc, newArc.Start.Parent)

	def test_ArcSegment_ToChord(self) -> None:
		"""The chord is a new line segment without value or key-value-pairs."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, value=1, keyValuePairs={"layer": 1})

		chord = arc.ToChord()

		self.assertIsNone(chord.Value)
		self.assertEqual(0, len(chord))

	def test_QuadraticBezierSegment(self) -> None:
		value = object()
		pairs = {"layer": 1}
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), value=value, keyValuePairs=pairs)

		self.assertIs(value, curve.Value)
		self.assertEqual(1, curve["layer"])
		self.assertIsNot(pairs, curve._dict)

	def test_QuadraticBezierSegment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_QuadraticBezierSegment_Copy(self) -> None:
		value = [1, 2]
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), value=value, keyValuePairs={"a": 1})

		newCurve =      curve.Copy()
		newCurve["a"] = 2

		self.assertIs(value, newCurve.Value)
		self.assertEqual(1, curve["a"])
		self.assertIs(value, copy(curve).Value)

	def test_QuadraticBezierSegment_deepcopy(self) -> None:
		value = [1, 2]
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), value=value, keyValuePairs={"a": [1]})

		newCurve = deepcopy(curve)

		self.assertIsNot(value, newCurve.Value)
		self.assertListEqual([1, 2], newCurve.Value)
		self.assertIsNot(curve["a"], newCurve["a"])
		self.assertIs(newCurve, newCurve.ControlPoint.Parent)

	def test_CubicBezierSegment(self) -> None:
		value = object()
		curve = CubicBezierSegment2D(
			Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0), value=value, keyValuePairs={"layer": 1}
		)

		self.assertIs(value, curve.Value)
		self.assertEqual(1, curve["layer"])

	def test_CubicBezierSegment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_CubicBezierSegment_Copy(self) -> None:
		value = [1, 2]
		curve = CubicBezierSegment2D(
			Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0), value=value, keyValuePairs={"a": [1]}
		)

		newCurve =  curve.Copy()
		deepCurve = deepcopy(curve)

		self.assertIs(value, newCurve.Value)
		self.assertIs(curve["a"], newCurve["a"])
		self.assertIsNot(curve._dict, newCurve._dict)
		self.assertIsNot(value, deepCurve.Value)
		self.assertIsNot(curve["a"], deepCurve["a"])
		self.assertIs(deepCurve, deepCurve.ControlPoint2.Parent)


class ArcInstantiation(Testcase):
	def test_Counterclockwise(self) -> None:
		"""The center is converted to the sagitta: the arc bulges 1 - sqrt(2) / 2 to the right of its chord."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertIsInstance(arc, Segment2D)
		self.assertTupleEqual((1, 0), arc.Start.ToTuple())
		self.assertTupleEqual((0, 1), arc.End.ToTuple())
		self.assertAlmostEqual(0, arc.Center.X)
		self.assertAlmostEqual(0, arc.Center.Y)
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertAlmostEqual(1, arc.Radius)
		self.assertEqual(0.5, arc.ChordPosition)
		self.assertAlmostEqual(sqrt(2) / 2 - 1, arc.Height)

	def test_Float(self) -> None:
		arc = ArcSegment2D(
			Point2D(1.5, 2.0), Point2D(-0.5, 2.0), center=Point2D(0.5, 2.0), direction=SweepDirection.Clockwise
		)

		self.assertTupleEqual((0.5, 2.0), arc.Center.ToTuple())
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(1.0, arc.Radius)

	def test_EndOnCircle_Close(self) -> None:
		"""The distances to the center are compared with math.isclose."""
		arc = ArcSegment2D(
			Point2D(1, 0), Point2D(0.0, 1.0000000001), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise
		)

		self.assertTrue(isclose(1, arc.Radius))

	def test_StartNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(None, Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_EndStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(1, 0), "0, 1", center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual("Parameter 'end' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_CenterNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=None, direction=SweepDirection.Counterclockwise)

		self.assertEqual("Parameter 'center' is None, while 'direction' is given.", str(context.exception))

	def test_CenterStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center="0, 0", direction=SweepDirection.Counterclockwise)

		self.assertEqual("Parameter 'center' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_CenterAtStart(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(1, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual("Parameter 'center' is at the position of parameter 'start'.", str(context.exception))
		self.assertListEqual(["Got point (1, 0)."], context.exception.__notes__)

	def test_EndNotOnCircle(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 2), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual(
			"Parameter 'center' has another distance to parameter 'end' than to parameter 'start'.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got distance 1.0 to start point (1, 0) and 2.0 to end point (0, 2)."],
			context.exception.__notes__
		)

	def test_DirectionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=None)

		self.assertEqual("Parameter 'direction' is None, while 'center' is given.", str(context.exception))

	def test_DirectionBool(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=True)

		self.assertEqual("Parameter 'direction' is not of type 'SweepDirection'.", str(context.exception))
		self.assertListEqual(["Got type 'bool'."], context.exception.__notes__)

	def test_CenterPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), Point2D(0, 0), SweepDirection.Counterclockwise)

	def test_Failing_ReleasesPoints(self) -> None:
		"""A failing check of the arc leaves the referenced start and end point free."""
		start = Point2D(1, 0)
		end =   Point2D(0, 2)

		with self.assertRaises(ValueError):
			_ = ArcSegment2D(start, end, center=Point2D(0, 0), direction=SweepDirection.Counterclockwise, copyPoints=False)

		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_Center_NoChord(self) -> None:
		"""An arc isn't a circle: a center can't make a full circle."""
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(1, 0), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		self.assertEqual("Parameter 'end' is at the position of parameter 'start'.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 0).", "An arc needs a chord from the start point to the end point."],
			context.exception.__notes__
		)


class ArcCircleParameters(Testcase):
	def test_ArcPoint(self) -> None:
		"""Start, arc point and end turn left, so the arc runs counterclockwise."""
		arcPoint = Point2D(1, -1)

		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), arcPoint=arcPoint)

		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())
		self.assertEqual(1.0, arc.Radius)
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, -1, 2, 0), arc.BoundingBox)
		self.assertEqual(-1.0, arc.Height)
		self.assertIsNone(arc.Center.Parent)
		self.assertIsNone(arcPoint.Parent)

	def test_ArcPoint_Clockwise(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), arcPoint=Point2D(1, 1))

		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 0, 2, 1), arc.BoundingBox)

	def test_ArcPoint_Large(self) -> None:
		"""The center (1, 4/3) is above the chord: the arc sweeps more than half the circle with radius 5/3."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), arcPoint=Point2D(1, 3))

		box = arc.BoundingBox

		self.assertTrue(isclose(4 / 3, arc.Center.Y))
		self.assertTrue(isclose(5 / 3, arc.Radius))
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertTrue(isclose(-2 / 3, box.MinX))
		self.assertTrue(isclose(8 / 3, box.MaxX))
		self.assertEqual(0, box.MinY)
		self.assertTrue(isclose(3, box.MaxY))

	def test_ArcPoint_Reference(self) -> None:
		"""Only the arc point's coordinates are used, so it isn't taken."""
		start =    Point2D(0, 0)
		arcPoint = Point2D(1, -1)

		arc = ArcSegment2D(start, Point2D(2, 0), arcPoint=arcPoint, copyPoints=False)

		self.assertIs(arc, start.Parent)
		self.assertIsNone(arcPoint.Parent)

	def test_ArcPoint_Str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), arcPoint="1, 1")

		self.assertEqual("Parameter 'arcPoint' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_ArcPoint_NoChord(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(0, 0), arcPoint=Point2D(1, 1))

		self.assertEqual("Parameter 'end' is at the position of parameter 'start'.", str(context.exception))
		self.assertListEqual(
			["Got point (0, 0).", "An arc needs a chord from the start point to the end point."],
			context.exception.__notes__
		)

	def test_ArcPoint_Collinear(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(2, 2), arcPoint=Point2D(3, 3))

		self.assertEqual(
			"Parameter 'arcPoint' is on the line through parameter 'start' and parameter 'end'.",
			str(context.exception)
		)
		self.assertListEqual(["Got points (0, 0), (3, 3) and (2, 2)."], context.exception.__notes__)

	def test_Height(self) -> None:
		"""A positive height is on the left of the chord, so the arc runs clockwise; here it is the sagitta."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)

		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())
		self.assertEqual(1.0, arc.Radius)
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 0, 2, 1), arc.BoundingBox)
		self.assertEqual(1, arc.Height)

	def test_Height_Negative(self) -> None:
		"""The arc passes (2, -1): center (2, 1.5), radius 2.5."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), height=-1)

		self.assertTupleEqual((2.0, 1.5), arc.Center.ToTuple())
		self.assertEqual(2.5, arc.Radius)
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, -1, 4, 0), arc.BoundingBox)

	def test_Height_Diagonal(self) -> None:
		"""The left normal of the chord from (0, 0) to (2, 2) points to (0, 2)."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 2), height=sqrt(2))

		self.assertTrue(isclose(1, arc.Center.X))
		self.assertTrue(isclose(1, arc.Center.Y))
		self.assertTrue(isclose(sqrt(2), arc.Radius))
		self.assertIs(SweepDirection.Clockwise, arc.Direction)

	def test_ChordPosition(self) -> None:
		"""The root point (1, 0) at a quarter of the chord, the arc passes (1, 1): center (2, -1)."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), chordPosition=0.25, height=1)

		self.assertTupleEqual((2.0, -1.0), arc.Center.ToTuple())
		self.assertTrue(isclose(sqrt(5), arc.Radius))
		self.assertIs(SweepDirection.Clockwise, arc.Direction)

	def test_ChordPosition_End(self) -> None:
		"""The root point at the end point, the arc passes (4, 1): center (2, 0.5)."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), chordPosition=1, height=1)

		self.assertTupleEqual((2.0, 0.5), arc.Center.ToTuple())

	def test_ChordPosition_Str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), chordPosition="0.5", height=1)

		self.assertEqual("Parameter 'chordPosition' is not of type 'float'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_ChordPosition_Range(self) -> None:
		for chordPosition in (-0.25, 1.5):
			with self.subTest(chordPosition=chordPosition):
				with self.assertRaises(ValueError) as context:
					_ = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), chordPosition=chordPosition, height=1)

				self.assertEqual("Parameter 'chordPosition' is out of range 0..1.", str(context.exception))
				self.assertListEqual([f"Got value '{chordPosition}'."], context.exception.__notes__)

	def test_ChordPosition_WithoutHeight(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), chordPosition=0.5)

		self.assertEqual("Parameter 'height' is None, while 'chordPosition' is given.", str(context.exception))

	def test_Height_Str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), height="1")

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Height_Zero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(4, 0), height=0.0)

		self.assertEqual("Parameter 'height' is 0.", str(context.exception))

	def test_Height_NoChord(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(1, 2), Point2D(1, 2), height=1)

		self.assertEqual("Parameter 'end' is at the position of parameter 'start'.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 2).", "An arc needs a chord from the start point to the end point."],
			context.exception.__notes__
		)

	def test_NoGroup(self) -> None:
		start = Point2D(0, 0)

		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(start, Point2D(2, 0), copyPoints=False)

		self.assertEqual("Parameters 'center', 'arcPoint' and 'height' are None.", str(context.exception))
		self.assertListEqual(
			["Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally 'chordPosition'."],
			context.exception.__notes__
		)
		self.assertIsNone(start.Parent)

	def test_TwoGroups(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=Point2D(1, 0), arcPoint=Point2D(1, 1))

		self.assertEqual("Parameters 'center' and 'arcPoint' are given together.", str(context.exception))
		self.assertListEqual(
			["Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally 'chordPosition'."],
			context.exception.__notes__
		)

	def test_ThreeGroups(self) -> None:
		"""The message names the given parameters of each group."""
		with self.assertRaises(ValueError) as context:
			_ = ArcSegment2D(
				Point2D(0, 0), Point2D(2, 0), direction=SweepDirection.Clockwise, arcPoint=Point2D(1, 1), chordPosition=0.5
			)

		self.assertEqual(
			"Parameters 'direction', 'arcPoint' and 'chordPosition' are given together.",
			str(context.exception)
		)

	def test_Edge(self) -> None:
		"""An edge references the shape's end points; its center is computed."""
		polygon = Polygon((Point2D(0, 0), Point2D(2, 0), Point2D(1, 5)))
		start, end, _ = polygon.Points

		edge = ArcSegment2D(start, end, height=1, copyPoints=False, parent=polygon)

		self.assertIs(polygon, edge.Parent)
		self.assertIs(polygon, edge.End.Parent)
		self.assertIsNone(edge.Center.Parent)


class ArcChord(Testcase):
	def test_ToChord(self) -> None:
		group = Group2D()
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1, parent=group)

		chord = arc.ToChord()

		self.assertIs(LineSegment2D, type(chord))
		self.assertTupleEqual(((0, 0), (2, 0)), chord.ToTuple())
		self.assertIsNone(chord.Parent)
		self.assertIsNot(arc.Start, chord.Start)
		self.assertIs(chord, chord.Start.Parent)
		self.assertIs(arc, arc.Start.Parent)
		self.assertEqual(2.0, chord.Length)


class ArcGeometry(Testcase):
	def test_QuarterCounterclockwise(self) -> None:
		arc = ArcSegment2D(Point2D(2, 0), Point2D(0, 2), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertAlmostEqual(0, arc.StartAngle)
		self.assertTrue(isclose(pi / 2, arc.EndAngle))
		self.assertTrue(isclose(pi / 2, arc.SweepAngle))
		self.assertTrue(isclose(pi, arc.Length))

	def test_QuarterClockwise(self) -> None:
		"""The same points clockwise: the arc takes the long way round."""
		arc = ArcSegment2D(Point2D(2, 0), Point2D(0, 2), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		self.assertEqual(-3 * pi / 2, arc.SweepAngle)
		self.assertEqual(3 * pi, arc.Length)

	def test_StartAngle_Negative(self) -> None:
		arc = ArcSegment2D(Point2D(0, -1), Point2D(-1, 0), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		self.assertTrue(isclose(-pi / 2, arc.StartAngle))
		self.assertTrue(isclose(pi, arc.EndAngle))
		self.assertTrue(isclose(-pi / 2, arc.SweepAngle))

	def test_Semicircle(self) -> None:
		arc = ArcSegment2D(Point2D(3, 4), Point2D(-3, -4), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual(5.0, arc.Radius)
		self.assertTrue(isclose(pi, arc.SweepAngle))
		self.assertTrue(isclose(5 * pi, arc.Length))

	def test_Length_Center(self) -> None:
		arc = ArcSegment2D(Point2D(6, 5), Point2D(5, 6), center=Point2D(5, 5), direction=SweepDirection.Counterclockwise)

		self.assertTrue(isclose(pi / 2, arc.Length))


class ArcBounds(Testcase):
	def test_Quarter(self) -> None:
		"""A quarter arc between two extreme points of its circle is enclosed by its end points."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual(BoundingBox2D(0, 0, 1, 1), arc.BoundingBox)

	def test_ThreeQuarters(self) -> None:
		"""The clockwise arc bulges past its end points at the bottom and on the left."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		self.assertEqual(BoundingBox2D(-1, -1, 1, 1), arc.BoundingBox)

	def test_SemicircleUpper(self) -> None:
		arc = ArcSegment2D(Point2D(2, 0), Point2D(-2, 0), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual(BoundingBox2D(-2, 0, 2, 2), arc.BoundingBox)

	def test_SemicircleLower(self) -> None:
		arc = ArcSegment2D(Point2D(2, 0), Point2D(-2, 0), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		self.assertEqual(BoundingBox2D(-2, -2, 2, 0), arc.BoundingBox)

	def test_Top(self) -> None:
		"""A flat arc above its center bulges past its end points at the top only."""
		arc = ArcSegment2D(Point2D(6, 6), Point2D(4, 6), center=Point2D(5, 5), direction=SweepDirection.Counterclockwise)

		self.assertEqual(BoundingBox2D(4, 6, 6, 5 + sqrt(2)), arc.BoundingBox)

	def test_InsideQuadrant(self) -> None:
		"""An arc passing no extreme point is enclosed by its end points."""
		arc = ArcSegment2D(Point2D(4, 3), Point2D(3, 4), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual(BoundingBox2D(3, 3, 4, 4), arc.BoundingBox)

	def test_ReadOnly(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(AttributeError):
			arc.BoundingBox = BoundingBox2D(0, 0, 1, 1)


class ArcEndPoints(Testcase):
	def test_Start(self) -> None:
		"""An assigned start point keeps the arc's relative height over the new chord."""
		arc =      ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		previous = arc.Start
		point =    Point2D(-2, 0)

		arc.Start = point

		self.assertIs(point, arc.Start)
		self.assertIs(arc, point.Parent)
		self.assertIsNone(previous.Parent)
		self.assertEqual(2, arc.Height)
		self.assertTupleEqual((0.0, 0.0), arc.Center.ToTuple())
		self.assertEqual(2, arc.Radius)

	def test_Start_None(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(ValueError) as context:
			arc.Start = None

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_Start_Tuple(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(TypeError) as context:
			arc.Start = (1, 0)

		self.assertEqual("Parameter 'start' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Start_End(self) -> None:
		"""The arc's end point is on the circle, but can't become its start point."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(DuplicatePointError) as context:
			arc.Start = arc.End

		self.assertEqual("Point is given twice.", str(context.exception))

	def test_Start_AtEnd(self) -> None:
		"""A start point at the position of the end point leaves no chord."""
		arc =      ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		previous = arc.Start
		point =    Point2D(2, 0)

		with self.assertRaises(ValueError) as context:
			arc.Start = point

		self.assertEqual("Parameter 'start' is at the position of the arc's end point.", str(context.exception))
		self.assertListEqual(
			["Got point (2, 0).", "An arc needs a chord from the start point to the end point."],
			context.exception.__notes__
		)
		self.assertIs(previous, arc.Start)
		self.assertIs(arc, previous.Parent)
		self.assertIsNone(point.Parent)
		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())

	def test_Start_Alias(self) -> None:
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		point = Point2D(-2, 0)

		arc.start = point

		self.assertIs(point, arc.Start)

	def test_End(self) -> None:
		"""The arc turns with its chord: the end point above the start point puts the bulge on the left."""
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		point = Point2D(0, 2)

		arc.End = point

		self.assertIs(point, arc.End)
		self.assertIs(arc, point.Parent)
		self.assertAlmostEqual(0, arc.Center.X)
		self.assertAlmostEqual(1, arc.Center.Y)
		self.assertEqual(BoundingBox2D(-1, 0, 0, 2), arc.BoundingBox)

	def test_End_AtStart(self) -> None:
		"""An end point at the position of the start point leaves no chord."""
		arc =      ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		previous = arc.End
		point =    Point2D(0, 0)

		with self.assertRaises(ValueError) as context:
			arc.End = point

		self.assertEqual("Parameter 'end' is at the position of the arc's start point.", str(context.exception))
		self.assertListEqual(
			["Got point (0, 0).", "An arc needs a chord from the start point to the end point."],
			context.exception.__notes__
		)
		self.assertIs(previous, arc.End)
		self.assertIs(arc, previous.Parent)
		self.assertIsNone(point.Parent)
		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())

	def test_End_Start(self) -> None:
		"""The arc's start point is on the circle, but can't become its end point."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(DuplicatePointError) as context:
			arc.End = arc.Start

		self.assertEqual("Point is given twice.", str(context.exception))

	def test_End_AtStart_Edge(self) -> None:
		"""An edge of a path checks the position before its ownership."""
		path = Path((ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1), ))

		with self.assertRaises(ValueError) as context:
			path.Segments[0].End = Point2D(0, 0)

		self.assertEqual("Parameter 'end' is at the position of the arc's start point.", str(context.exception))

	def test_End_Alias(self) -> None:
		arc =   ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		point = Point2D(0, 2)

		arc.end = point

		self.assertIs(point, arc.End)

	def test_Center_ReadOnly(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(AttributeError):
			arc.Center = Point2D(1, 1)

	def test_Direction_ReadOnly(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(AttributeError):
			arc.Direction = SweepDirection.Clockwise


class ArcOwnership(Testcase):
	def test_Center(self) -> None:
		"""A given center is only read; the arc's center is a new point on each access."""
		center = Point2D(1, 0)

		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=center, direction=SweepDirection.Clockwise)

		self.assertIsNone(center.Parent)
		self.assertIsNot(center, arc.Center)
		self.assertIsNot(arc.Center, arc.Center)
		self.assertIsNone(arc.Center.Parent)
		self.assertIs(arc, arc.Start.Parent)

	def test_Reference(self) -> None:
		start =  Point2D(0, 0)
		end =    Point2D(2, 0)
		center = Point2D(1, 0)

		arc = ArcSegment2D(start, end, center=center, direction=SweepDirection.Clockwise, copyPoints=False)

		self.assertIs(start, arc.Start)
		self.assertIs(arc, start.Parent)
		self.assertIs(arc, end.Parent)
		self.assertIsNone(center.Parent)

	def test_OwnedCenter(self) -> None:
		"""A center owned by another element is only read, so it stays with its owner."""
		line = LineSegment2D(Point2D(1, 0), Point2D(4, 6))

		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=line.Start, direction=SweepDirection.Clockwise)

		self.assertIs(line, line.Start.Parent)
		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())

	def test_Edge(self) -> None:
		"""An arc with a shape as parent references the shape's end points; a center needn't belong to the shape."""
		polygon = Polygon((Point2D(0, 0), Point2D(2, 0), Point2D(1, 5)))
		start, end, _ = polygon.Points

		edge = ArcSegment2D(
			start, end, center=Point2D(1, 0), direction=SweepDirection.Clockwise, copyPoints=False, parent=polygon
		)

		self.assertIs(polygon, edge.Parent)
		self.assertIs(start, edge.Start)
		self.assertIs(polygon, edge.Start.Parent)
		self.assertTupleEqual((1.0, 0.0), edge.Center.ToTuple())

	def test_Edge_Start(self) -> None:
		"""An edge can't replace its points."""
		polygon = Polygon((Point2D(1, 0), Point2D(0, 1), Point2D(0, 0)))
		start, end, center = polygon.Points
		edge = ArcSegment2D(
			start, end, center=center, direction=SweepDirection.Counterclockwise, copyPoints=False, parent=polygon
		)

		with self.assertRaises(NotOwnedError):
			edge.Start = Point2D(-1, 0)

		self.assertIs(start, edge.Start)


class ArcCopy(Testcase):
	def test_Copy(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=Point2D(1, 0), direction=SweepDirection.Clockwise)

		newArc = arc.Copy()
		newArc.Move(Offset2D(5, 5))

		self.assertIs(ArcSegment2D, type(newArc))
		self.assertIsNot(arc.Start, newArc.Start)
		self.assertIs(newArc, newArc.Start.Parent)
		self.assertIs(SweepDirection.Clockwise, newArc.Direction)
		self.assertEqual(1, newArc.Height)
		self.assertTupleEqual((1.0, 0.0), arc.Center.ToTuple())
		self.assertTupleEqual((6.0, 5.0), newArc.Center.ToTuple())

	def test_copy(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=Point2D(1, 0), direction=SweepDirection.Clockwise)

		newArc = copy(arc)

		self.assertIs(ArcSegment2D, type(newArc))
		self.assertIsNot(arc.Start, newArc.Start)
		self.assertTupleEqual((1.0, 0.0), newArc.Center.ToTuple())

	def test_deepcopy(self) -> None:
		"""A deep copy owns its points and isn't in the group of the original."""
		group = Group2D()
		arc =   ArcSegment2D(
			Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise, parent=group
		)

		newArc = deepcopy(arc)

		self.assertIs(ArcSegment2D, type(newArc))
		self.assertIsNone(newArc.Parent)
		self.assertIs(newArc, newArc.Start.Parent)
		self.assertIs(newArc, newArc.End.Parent)
		self.assertTupleEqual((arc, ), group.Children)


class ArcMoving(Testcase):
	def test_Move(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=Point2D(1, 0), direction=SweepDirection.Clockwise)

		arc.Move(Offset2D(2, 3))

		self.assertTupleEqual((2, 3), arc.Start.ToTuple())
		self.assertTupleEqual((4, 3), arc.End.ToTuple())
		self.assertTupleEqual((3.0, 3.0), arc.Center.ToTuple())
		self.assertEqual(BoundingBox2D(2, 3, 4, 4), arc.BoundingBox)

	def test_MoveEnd(self) -> None:
		"""Moving an end point keeps the arc's shape: its height scales with the chord, its circle follows."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		end = arc.End

		end += Offset2D(2, 0)

		self.assertEqual(2, arc.Height)
		self.assertTupleEqual((2.0, 0.0), arc.Center.ToTuple())
		self.assertEqual(2, arc.Radius)
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 0, 4, 2), arc.BoundingBox)

	def test_Move_None(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		with self.assertRaises(ValueError) as context:
			arc.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 0), arc.Start.ToTuple())


class ArcMirroring(Testcase):
	def test_MirrorX(self) -> None:
		"""Mirroring reverses the direction, so the mirrored arc bulges to the other side."""
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise)

		arc.MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual((1, 0), arc.Start.ToTuple())
		self.assertTupleEqual((2, 1), arc.End.ToTuple())
		self.assertTupleEqual((2, 0), arc.Center.ToTuple())
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(1, -1, 3, 1), arc.BoundingBox)

	def test_MirrorY(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		arc.MirrorY(Alignment2D.MinY)

		self.assertTupleEqual((1, 0), arc.Start.ToTuple())
		self.assertTupleEqual((0, -1), arc.End.ToTuple())
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, -1, 1, 0), arc.BoundingBox)

	def test_Twice(self) -> None:
		arc = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)

		arc.MirrorX()
		arc.MirrorX()

		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 0, 1, 1), arc.BoundingBox)

	def test_Canvas(self) -> None:
		"""Flipping a canvas keeps the arc's appearance: its bounding box stays at the same distance from the top."""
		arc =    ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)
		canvas = Canvas2D(YAxisDirection.Up, Size2D(10, 10), (arc, ))

		canvas.Mirror()

		self.assertTupleEqual((1.0, 10.0), arc.Center.ToTuple())
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 9, 2, 10), arc.BoundingBox)


class ArcGroups(Testcase):
	def test_Parent(self) -> None:
		group = Group2D(Offset2D(10, 20))

		arc = ArcSegment2D(
			Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise, parent=group
		)

		self.assertIs(group, arc.Parent)
		self.assertTupleEqual((arc, ), group.Children)
		self.assertIs(group, arc.Start.Frame)
		self.assertEqual(BoundingBox2D(9, 19, 11, 21), arc.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox2D(9, 19, 11, 21), group.BoundingBox)

	def test_Parent_Failing(self) -> None:
		"""A failing check leaves nothing in the group."""
		group = Group2D()

		with self.assertRaises(ValueError):
			_ = ArcSegment2D(
				Point2D(1, 0), Point2D(0, 2), center=Point2D(0, 0), direction=SweepDirection.Clockwise, parent=group
			)

		self.assertTupleEqual((), group.Children)

	def test_Parent_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Clockwise, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Shape' or 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Mirror(self) -> None:
		"""A group mirrors its children at its origin, so the arc's direction reverses."""
		arc =   ArcSegment2D(Point2D(1, 0), Point2D(0, 1), center=Point2D(0, 0), direction=SweepDirection.Counterclockwise)
		group = Group2D(Offset2D(10, 20), (arc, ))

		group.MirrorX()

		self.assertTupleEqual((-1, 0), arc.Start.ToTuple())
		self.assertIs(SweepDirection.Clockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(10, 20, 11, 21), group.BoundingBox)


class ArcRepresentation(Testcase):
	def test_repr(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), center=Point2D(1, 0), direction=SweepDirection.Counterclockwise)

		self.assertEqual("ArcSegment2D((0, 0), (2, 0), chordPosition=0.5, height=-1.0)", repr(arc))

	def test_str(self) -> None:
		arc = ArcSegment2D(Point2D(0, 0), Point2D(2, 0), height=1)

		self.assertEqual("((0, 0) → (2, 0), height 1.0 at 0.5)", str(arc))


class BezierInstantiation(Testcase):
	def test_Abstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = BezierSegment2D(Point2D(0, 0), Point2D(4, 0))

	def test_Quadratic(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertIsInstance(curve, BezierSegment2D)
		self.assertIsInstance(curve, Segment2D)
		self.assertTupleEqual((2, 4), curve.ControlPoint.ToTuple())
		self.assertTupleEqual((curve.ControlPoint, ), curve.ControlPoints)
		self.assertTupleEqual(((0, 0), (2, 4), (4, 0)), curve.ToTuple())

	def test_Cubic(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4.5), Point2D(4, 0))

		self.assertTupleEqual((0, 4), curve.ControlPoint1.ToTuple())
		self.assertTupleEqual((4, 4.5), curve.ControlPoint2.ToTuple())
		self.assertTupleEqual((curve.ControlPoint1, curve.ControlPoint2), curve.ControlPoints)
		self.assertTupleEqual(((0, 0), (0, 4), (4, 4.5), (4, 0)), curve.ToTuple())

	def test_Quadratic_ControlPointNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = QuadraticBezierSegment2D(Point2D(0, 0), None, Point2D(4, 0))

		self.assertEqual("Parameter 'controlPoint' is None.", str(context.exception))

	def test_Quadratic_ControlPointTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = QuadraticBezierSegment2D(Point2D(0, 0), (2, 4), Point2D(4, 0))

		self.assertEqual("Parameter 'controlPoint' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Quadratic_EndNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), None)

		self.assertEqual("Parameter 'end' is None.", str(context.exception))

	def test_Cubic_ControlPoint1None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = CubicBezierSegment2D(Point2D(0, 0), None, Point2D(4, 4), Point2D(4, 0))

		self.assertEqual("Parameter 'controlPoint1' is None.", str(context.exception))

	def test_Cubic_ControlPoint2Str(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), "4, 4", Point2D(4, 0))

		self.assertEqual("Parameter 'controlPoint2' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Cubic_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0), False)


class BezierGeometry(Testcase):
	def test_Quadratic_PointAt(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertTupleEqual((0, 0), curve.PointAt(0).ToTuple())
		self.assertTupleEqual((2.0, 2.0), curve.PointAt(0.5).ToTuple())
		self.assertTupleEqual((4, 0), curve.PointAt(1).ToTuple())
		self.assertTupleEqual((1.0, 1.5), curve.PointAt(0.25).ToTuple())

	def test_Cubic_PointAt(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		self.assertTupleEqual((0, 0), curve.PointAt(0).ToTuple())
		self.assertTupleEqual((2.0, 3.0), curve.PointAt(0.5).ToTuple())
		self.assertTupleEqual((4, 0), curve.PointAt(1).ToTuple())

	def test_PointAt_NoOwner(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertIsNone(curve.PointAt(0.5).Parent)
		self.assertIsNot(curve.Start, curve.PointAt(0))

	def test_PointAt_None(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		with self.assertRaises(ValueError) as context:
			_ = curve.PointAt(None)

		self.assertEqual("Parameter 't' is None.", str(context.exception))

	def test_PointAt_Str(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		with self.assertRaises(TypeError) as context:
			_ = curve.PointAt("0.5")

		self.assertEqual("Parameter 't' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_PointAt_Range(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		for t in (-0.5, 1.5):
			with self.subTest(t=t):
				with self.assertRaises(ValueError) as context:
					_ = curve.PointAt(t)

				self.assertEqual("Parameter 't' is out of range 0..1.", str(context.exception))
				self.assertListEqual([f"Got value '{t}'."], context.exception.__notes__)


class BezierBounds(Testcase):
	def test_Quadratic(self) -> None:
		"""The curve reaches half the height of its control point."""
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertEqual(BoundingBox2D(0, 0, 4, 2), curve.BoundingBox)

	def test_Quadratic_Bulging(self) -> None:
		"""The curve bulges past both end points in x-direction."""
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(4, 4), Point2D(0, 8))

		self.assertEqual(BoundingBox2D(0, 0, 2, 8), curve.BoundingBox)

	def test_Quadratic_Straight(self) -> None:
		"""A control point between the end points adds no extreme point."""
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(1, 1), Point2D(4, 4))

		self.assertEqual(BoundingBox2D(0, 0, 4, 4), curve.BoundingBox)

	def test_Cubic(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		self.assertEqual(BoundingBox2D(0, 0, 4, 3), curve.BoundingBox)

	def test_Cubic_Bulging(self) -> None:
		"""x(t) = 18 t (1 - t) is largest at t = 0.5; the control points' box would reach 6."""
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6))

		self.assertEqual(BoundingBox2D(0, 0, 4.5, 6), curve.BoundingBox)

	def test_Cubic_SCurve(self) -> None:
		"""x(t) = 9 t (1 - t) (1 - 2 t) has its extremes at t = (3 -+ sqrt(3)) / 6, with x = +-sqrt(3) / 2."""
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(3, 1), Point2D(-3, 2), Point2D(0, 3))

		box = curve.BoundingBox

		self.assertTrue(isclose(-sqrt(3) / 2, box.MinX))
		self.assertTrue(isclose(sqrt(3) / 2, box.MaxX))
		self.assertEqual(0, box.MinY)
		self.assertEqual(3, box.MaxY)

	def test_Cubic_QuadraticDerivativeZero(self) -> None:
		"""Evenly spaced control points make a straight line: the derivative has no root."""
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(1, 2), Point2D(2, 4), Point2D(3, 6))

		self.assertEqual(BoundingBox2D(0, 0, 3, 6), curve.BoundingBox)

	def test_ReadOnly(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		with self.assertRaises(AttributeError):
			curve.BoundingBox = BoundingBox2D(0, 0, 1, 1)

		with self.assertRaises(AttributeError):
			curve.ControlPoint = Point2D(1, 1)


class BezierOwnership(Testcase):
	def test_Copy(self) -> None:
		controlPoint = Point2D(2, 4)

		curve = QuadraticBezierSegment2D(Point2D(0, 0), controlPoint, Point2D(4, 0))

		self.assertIsNot(controlPoint, curve.ControlPoint)
		self.assertIsNone(controlPoint.Parent)
		self.assertIs(curve, curve.ControlPoint.Parent)

	def test_Reference(self) -> None:
		start =         Point2D(0, 0)
		controlPoint1 = Point2D(0, 4)
		controlPoint2 = Point2D(4, 4)
		end =           Point2D(4, 0)

		curve = CubicBezierSegment2D(start, controlPoint1, controlPoint2, end, copyPoints=False)

		self.assertIs(controlPoint1, curve.ControlPoint1)
		self.assertIs(controlPoint2, curve.ControlPoint2)
		self.assertIs(curve, start.Parent)
		self.assertIs(curve, controlPoint1.Parent)
		self.assertIs(curve, controlPoint2.Parent)

	def test_Quadratic_ControlPointIsStart(self) -> None:
		start = Point2D(0, 0)
		end =   Point2D(4, 0)

		with self.assertRaises(DuplicatePointError) as context:
			_ = QuadraticBezierSegment2D(start, start, end, copyPoints=False)

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(
			["Got point (0, 0).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertEqual(
			"Parameter 'controlPoint' is the same point as parameter 'start'.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_Quadratic_ControlPointOwned(self) -> None:
		line =  LineSegment2D(Point2D(2, 4), Point2D(4, 6))
		start = Point2D(0, 0)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = QuadraticBezierSegment2D(start, line.Start, Point2D(4, 0), copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (2, 4) owned by LineSegment2D((2, 4), (4, 6)).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'controlPoint' is owned by another element.", str(context.exception.__cause__))
		self.assertIsNone(start.Parent)

	def test_Cubic_ControlPoint2IsEnd(self) -> None:
		end = Point2D(4, 0)

		with self.assertRaises(DuplicatePointError) as context:
			_ = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), end, end, copyPoints=False)

		self.assertEqual(
			"Parameter 'controlPoint2' is the same point as parameter 'end'.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(end.Parent)

	def test_Cubic_SameControlPoints(self) -> None:
		controlPoint = Point2D(2, 4)

		with self.assertRaises(DuplicatePointError) as context:
			_ = CubicBezierSegment2D(Point2D(0, 0), controlPoint, controlPoint, Point2D(4, 0), copyPoints=False)

		self.assertListEqual(
			["Got point (2, 4).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertEqual(
			"Parameter 'controlPoint2' is the same point as parameter 'controlPoint1'.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(controlPoint.Parent)

	def test_Cubic_SameControlPoints_Copy(self) -> None:
		controlPoint = Point2D(2, 4)

		curve = CubicBezierSegment2D(Point2D(0, 0), controlPoint, controlPoint, Point2D(4, 0))

		self.assertIsNot(curve.ControlPoint1, curve.ControlPoint2)

	def test_Edge(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(2, 4), Point2D(4, 0)))
		start, controlPoint, end = polygon.Points

		edge = QuadraticBezierSegment2D(start, controlPoint, end, copyPoints=False, parent=polygon)

		self.assertIs(polygon, edge.Parent)
		self.assertIs(polygon, edge.ControlPoint.Parent)

	def test_Edge_ControlPointNotOwned(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(2, 4), Point2D(4, 0)))
		start, controlPoint, end = polygon.Points

		with self.assertRaises(NotOwnedError) as context:
			_ = CubicBezierSegment2D(start, controlPoint, Point2D(3, 3), end, copyPoints=False, parent=polygon)

		self.assertEqual("Point isn't owned by the parent shape.", str(context.exception))
		self.assertListEqual(["Got point (3, 3) owned by None."], context.exception.__notes__)
		self.assertEqual("Parameter 'controlPoint2' isn't owned by parameter 'parent'.", str(context.exception.__cause__))

	def test_Start(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))
		point = Point2D(-1, -1)

		curve.Start = point

		self.assertIs(point, curve.Start)
		self.assertIs(curve, point.Parent)

	def test_Start_ControlPoint(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))
		start = curve.Start

		with self.assertRaises(DuplicatePointError) as context:
			curve.Start = curve.ControlPoint

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (2, 4)."], context.exception.__notes__)
		self.assertEqual("Parameter 'start' is a control point of the curve.", str(context.exception.__cause__))
		self.assertIs(start, curve.Start)

	def test_End_ControlPoint(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		with self.assertRaises(DuplicatePointError) as context:
			curve.end = curve.ControlPoint2

		self.assertEqual("Parameter 'end' is a control point of the curve.", str(context.exception.__cause__))

	def test_End_None(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		with self.assertRaises(ValueError) as context:
			curve.End = None

		self.assertEqual("Parameter 'end' is None.", str(context.exception))


class BezierCopy(Testcase):
	def test_Quadratic(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		for newCurve in (curve.Copy(), copy(curve), deepcopy(curve)):
			self.assertIs(QuadraticBezierSegment2D, type(newCurve))
			self.assertIsNot(curve.ControlPoint, newCurve.ControlPoint)
			self.assertIs(newCurve, newCurve.ControlPoint.Parent)
			self.assertTupleEqual(((0, 0), (2, 4), (4, 0)), newCurve.ToTuple())

	def test_Cubic(self) -> None:
		group = Group2D()
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0), parent=group)

		for newCurve in (curve.Copy(), copy(curve), deepcopy(curve)):
			self.assertIs(CubicBezierSegment2D, type(newCurve))
			self.assertIsNone(newCurve.Parent)
			self.assertIsNot(curve.ControlPoint2, newCurve.ControlPoint2)
			self.assertIs(newCurve, newCurve.ControlPoint2.Parent)
			self.assertTupleEqual(((0, 0), (0, 4), (4, 4), (4, 0)), newCurve.ToTuple())

		self.assertTupleEqual((curve, ), group.Children)


class BezierMoving(Testcase):
	def test_Quadratic(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		curve.Move(Offset2D(1, -1))

		self.assertTupleEqual(((1, -1), (3, 3), (5, -1)), curve.ToTuple())
		self.assertEqual(BoundingBox2D(1, -1, 5, 1), curve.BoundingBox)

	def test_Cubic(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		curve.Move(Offset2D(10, 0))

		self.assertTupleEqual(((10, 0), (10, 4), (14, 4), (14, 0)), curve.ToTuple())

	def test_Tuple(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		with self.assertRaises(TypeError) as context:
			curve.Move((1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertTupleEqual(((0, 0), (0, 4), (4, 4), (4, 0)), curve.ToTuple())


class BezierMirroring(Testcase):
	def test_Quadratic_MirrorY(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		curve.MirrorY(Alignment2D.MinY)

		self.assertTupleEqual(((0, 0), (2, -4), (4, 0)), curve.ToTuple())
		self.assertEqual(BoundingBox2D(0, -2, 4, 0), curve.BoundingBox)

	def test_Cubic_MirrorX(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6))

		curve.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual(((0, 0), (-6, 0), (-6, 6), (0, 6)), curve.ToTuple())
		self.assertEqual(BoundingBox2D(-4.5, 0, 0, 6), curve.BoundingBox)

	def test_Group(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))
		group = Group2D(Offset2D(10, 20), (curve, ))

		group.MirrorY()

		self.assertTupleEqual(((0, 0), (2, -4), (4, 0)), curve.ToTuple())
		self.assertEqual(BoundingBox2D(10, 20, 14, 22), group.BoundingBox)


class BezierGroups(Testcase):
	def test_Parent(self) -> None:
		group = Group2D(Offset2D(10, 20))

		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), parent=group)

		self.assertIs(group, curve.Parent)
		self.assertTupleEqual((curve, ), group.Children)
		self.assertIs(group, curve.ControlPoint.Frame)
		self.assertEqual(BoundingBox2D(10, 20, 14, 22), curve.AbsoluteBoundingBox)

	def test_Parent_Failing(self) -> None:
		group = Group2D()
		point = Point2D(2, 4)

		with self.assertRaises(DuplicatePointError):
			_ = CubicBezierSegment2D(Point2D(0, 0), point, point, Point2D(4, 0), copyPoints=False, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Parent_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Shape' or 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class BezierRepresentation(Testcase):
	def test_Quadratic_repr(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertEqual("QuadraticBezierSegment2D((0, 0), (2, 4), (4, 0))", repr(curve))

	def test_Quadratic_str(self) -> None:
		curve = QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0))

		self.assertEqual("((0, 0) .. controls (2, 4) .. (4, 0))", str(curve))

	def test_Cubic_repr(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		self.assertEqual("CubicBezierSegment2D((0, 0), (0, 4), (4, 4), (4, 0))", repr(curve))

	def test_Cubic_str(self) -> None:
		curve = CubicBezierSegment2D(Point2D(0, 0), Point2D(0, 4), Point2D(4, 4), Point2D(4, 0))

		self.assertEqual("((0, 0) .. controls (0, 4) and (4, 4) .. (4, 0))", str(curve))
