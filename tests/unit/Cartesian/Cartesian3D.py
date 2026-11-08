# ==================================================================================================================== #
#             _____           _ _               ____           _            _             _____ ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ /|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  |_ \| | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |___) | |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|____/|____/                  #
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
Unit tests for :mod:`pyTooling.Cartesian3D`: points, offsets and sizes, their copies, comparisons and
arithmetic.
"""
from copy                         import copy, deepcopy
from math                         import isclose, pi, sqrt

from pyTooling.Cartesian3D        import Base3D, Element3D, Origin3D, Point3D, Offset3D, Size3D, BoundingBox3D, \
                                         Segment3D, LineSegment3D, Alignment3D, Plane3D, YZPlane3D, XZPlane3D, \
                                         XYPlane3D, Ray3D
from pyTooling.Cartesian3D.Groups import Group3D
from pyTooling.Cartesian2D        import Point2D, Offset2D, Alignment2D, VerticalLine2D, AlreadyOwnedError, \
                                         DuplicatePointError
from pyTooling.Exceptions         import AlreadyInHierarchyError, DuplicateElementError, InvalidOperationError
from pyTooling.MetaClasses        import AbstractClassError
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Origin(self) -> None:
		origin = Origin3D()

		self.assertIsInstance(origin.X, int)
		self.assertIsInstance(origin.Y, int)
		self.assertIsInstance(origin.Z, int)
		self.assertEqual(0, origin.X)
		self.assertEqual(0, origin.Y)
		self.assertEqual(0, origin.Z)
		self.assertTupleEqual((0, 0, 0), origin.ToTuple())
		self.assertEqual("Origin3D(0, 0, 0)", repr(origin))

	def test_Point_int(self) -> None:
		point = Point3D(1, 2, 3)

		self.assertIsInstance(point.X, int)
		self.assertIsInstance(point.Y, int)
		self.assertIsInstance(point.Z, int)
		self.assertEqual(1, point.X)
		self.assertEqual(2, point.Y)
		self.assertEqual(3, point.Z)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())
		self.assertEqual("Point3D(1, 2, 3)", repr(point))

	def test_Point_float(self) -> None:
		point = Point3D(1.0, 2.0, 3.0)

		self.assertIsInstance(point.X, float)
		self.assertIsInstance(point.Y, float)
		self.assertIsInstance(point.Z, float)
		self.assertEqual(1.0, point.X)
		self.assertEqual(2.0, point.Y)
		self.assertEqual(3.0, point.Z)
		self.assertTupleEqual((1.0, 2.0, 3.0), point.ToTuple())
		self.assertEqual("Point3D(1.0, 2.0, 3.0)", repr(point))

	def test_Point_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point3D("1", 2, 3)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Point_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point3D(1, "2", 3)

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Point_str3(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point3D(1, 2, "3")

		self.assertEqual("Parameter 'z' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Offset_int(self) -> None:
		offset = Offset3D(1, 2, 3)

		self.assertIsInstance(offset.XOffset, int)
		self.assertIsInstance(offset.YOffset, int)
		self.assertIsInstance(offset.ZOffset, int)
		self.assertEqual(1, offset.XOffset)
		self.assertEqual(2, offset.YOffset)
		self.assertEqual(3, offset.ZOffset)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())
		self.assertEqual("Offset3D(1, 2, 3)", repr(offset))

	def test_Offset_float(self) -> None:
		offset = Offset3D(1.0, 2.0, 3.0)

		self.assertIsInstance(offset.XOffset, float)
		self.assertIsInstance(offset.YOffset, float)
		self.assertIsInstance(offset.ZOffset, float)
		self.assertEqual(1.0, offset.XOffset)
		self.assertEqual(2.0, offset.YOffset)
		self.assertEqual(3.0, offset.ZOffset)
		self.assertTupleEqual((1.0, 2.0, 3.0), offset.ToTuple())
		self.assertEqual("Offset3D(1.0, 2.0, 3.0)", repr(offset))

	def test_Offset_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset3D("1", 2, 3)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Offset_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset3D(1, "2", 3)

		self.assertEqual("Parameter 'yOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Offset_str3(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Offset3D(1, 2, "3")

		self.assertEqual("Parameter 'zOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Size_int(self) -> None:
		size = Size3D(1, 2, 3)

		self.assertIsInstance(size.Width, int)
		self.assertIsInstance(size.Height, int)
		self.assertIsInstance(size.Depth, int)
		self.assertEqual(1, size.Width)
		self.assertEqual(2, size.Height)
		self.assertEqual(3, size.Depth)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())
		self.assertEqual("Size3D(1, 2, 3)", repr(size))

	def test_Size_float(self) -> None:
		size = Size3D(1.0, 2.0, 3.0)

		self.assertIsInstance(size.Width, float)
		self.assertIsInstance(size.Height, float)
		self.assertIsInstance(size.Depth, float)
		self.assertEqual(1.0, size.Width)
		self.assertEqual(2.0, size.Height)
		self.assertEqual(3.0, size.Depth)
		self.assertTupleEqual((1.0, 2.0, 3.0), size.ToTuple())
		self.assertEqual("Size3D(1.0, 2.0, 3.0)", repr(size))

	def test_Size_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Size3D("1", 2, 3)

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Size_str2(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Size3D(1, "2", 3)

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Size_str3(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Size3D(1, 2, "3")

		self.assertEqual("Parameter 'depth' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_LineSegment(self) -> None:
		point1 = Point3D(1, 2, 3)
		point2 = Point3D(2, 3, 4)

		line = LineSegment3D(point1, point2)

		offset = Offset3D(1, 1, 1)

		self.assertEqual(sqrt(3), line.Length)
		self.assertEqual(offset, line.ToOffset())
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), line.ToTuple())

	def test_Point_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Point3D(None, 2, 3)

		self.assertEqual("Parameter 'x' is None.", str(context.exception))

	def test_Point_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Point3D(1, None, 3)

		self.assertEqual("Parameter 'y' is None.", str(context.exception))

	def test_Point_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Point3D(1, 2, None)

		self.assertEqual("Parameter 'z' is None.", str(context.exception))

	def test_Offset_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Offset3D(None, 2, 3)

		self.assertEqual("Parameter 'xOffset' is None.", str(context.exception))

	def test_Offset_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Offset3D(1, None, 3)

		self.assertEqual("Parameter 'yOffset' is None.", str(context.exception))

	def test_Offset_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Offset3D(1, 2, None)

		self.assertEqual("Parameter 'zOffset' is None.", str(context.exception))

	def test_Size_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Size3D(None, 2, 3)

		self.assertEqual("Parameter 'width' is None.", str(context.exception))

	def test_Size_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Size3D(1, None, 3)

		self.assertEqual("Parameter 'height' is None.", str(context.exception))

	def test_Size_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Size3D(1, 2, None)

		self.assertEqual("Parameter 'depth' is None.", str(context.exception))

	def test_LineSegment_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment3D(None, Point3D(1, 2, 3))

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_LineSegment_None2(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment3D(Point3D(1, 2, 3), None)

		self.assertEqual("Parameter 'end' is None.", str(context.exception))


class Properties(Testcase):
	def test_Point_X(self) -> None:
		point = Point3D(1, 2, 3)

		point.X = 3.5

		self.assertEqual(3.5, point.X)
		self.assertTupleEqual((3.5, 2, 3), point.ToTuple())

	def test_Point_x_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.X = None

		self.assertEqual("Parameter 'x' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_x_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.X = "3.5"

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_Y(self) -> None:
		point = Point3D(1, 2, 3)

		point.Y = 3.5

		self.assertEqual(3.5, point.Y)
		self.assertTupleEqual((1, 3.5, 3), point.ToTuple())

	def test_Point_y_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.Y = None

		self.assertEqual("Parameter 'y' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_y_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.Y = "3.5"

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_Z(self) -> None:
		point = Point3D(1, 2, 3)

		point.Z = 3.5

		self.assertEqual(3.5, point.Z)
		self.assertTupleEqual((1, 2, 3.5), point.ToTuple())

	def test_Point_z_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.Z = None

		self.assertEqual("Parameter 'z' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_z_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.Z = "3.5"

		self.assertEqual("Parameter 'z' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Offset_XOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.XOffset = 3.5

		self.assertEqual(3.5, offset.XOffset)
		self.assertTupleEqual((3.5, 2, 3), offset.ToTuple())

	def test_Offset_xOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.XOffset = None

		self.assertEqual("Parameter 'xOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_xOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.XOffset = "3.5"

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_YOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.YOffset = 3.5

		self.assertEqual(3.5, offset.YOffset)
		self.assertTupleEqual((1, 3.5, 3), offset.ToTuple())

	def test_Offset_yOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.YOffset = None

		self.assertEqual("Parameter 'yOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_yOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.YOffset = "3.5"

		self.assertEqual("Parameter 'yOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_ZOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.ZOffset = 3.5

		self.assertEqual(3.5, offset.ZOffset)
		self.assertTupleEqual((1, 2, 3.5), offset.ToTuple())

	def test_Offset_zOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.ZOffset = None

		self.assertEqual("Parameter 'zOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_zOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.ZOffset = "3.5"

		self.assertEqual("Parameter 'zOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Size_Width(self) -> None:
		size = Size3D(1, 2, 3)

		size.Width = 3.5

		self.assertEqual(3.5, size.Width)
		self.assertTupleEqual((3.5, 2, 3), size.ToTuple())

	def test_Size_width_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.Width = None

		self.assertEqual("Parameter 'width' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_width_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.Width = "3.5"

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_Height(self) -> None:
		size = Size3D(1, 2, 3)

		size.Height = 3.5

		self.assertEqual(3.5, size.Height)
		self.assertTupleEqual((1, 3.5, 3), size.ToTuple())

	def test_Size_height_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.Height = None

		self.assertEqual("Parameter 'height' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_height_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.Height = "3.5"

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_Depth(self) -> None:
		size = Size3D(1, 2, 3)

		size.Depth = 3.5

		self.assertEqual(3.5, size.Depth)
		self.assertTupleEqual((1, 2, 3.5), size.ToTuple())

	def test_Size_depth_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.Depth = None

		self.assertEqual("Parameter 'depth' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_depth_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.Depth = "3.5"

		self.assertEqual("Parameter 'depth' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_LineSegment_Start(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))
		point = Point3D(7, 8, 9)

		line.Start = point

		self.assertIs(point, line.Start)
		self.assertTupleEqual(((7, 8, 9), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_start_None(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(ValueError) as context:
			line.Start = None

		self.assertEqual("Parameter 'start' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_start_tuple(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(TypeError) as context:
			line.Start = (7, 8, 9)

		self.assertEqual("Parameter 'start' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_End(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))
		point = Point3D(7, 8, 9)

		line.End = point

		self.assertIs(point, line.End)
		self.assertTupleEqual(((1, 2, 3), (7, 8, 9)), line.ToTuple())

	def test_LineSegment_end_None(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(ValueError) as context:
			line.End = None

		self.assertEqual("Parameter 'end' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_end_tuple(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(TypeError) as context:
			line.End = (7, 8, 9)

		self.assertEqual("Parameter 'end' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())


class Aliases(Testcase):
	def test_Point(self) -> None:
		point = Point3D(1, 2, 3)

		self.assertIs(Point3D.X, Point3D.x)
		self.assertIs(Point3D.Y, Point3D.y)
		self.assertIs(Point3D.Z, Point3D.z)

		point.x = 7.5
		point.y = 8.5
		point.z = 9.5

		self.assertEqual(7.5, point.X)
		self.assertEqual(8.5, point.Y)
		self.assertEqual(9.5, point.Z)

	def test_Offset(self) -> None:
		offset = Offset3D(1, 2, 3)

		self.assertIs(Offset3D.XOffset, Offset3D.xOffset)
		self.assertIs(Offset3D.YOffset, Offset3D.yOffset)
		self.assertIs(Offset3D.ZOffset, Offset3D.zOffset)

		offset.xOffset = 7.5
		offset.yOffset = 8.5
		offset.zOffset = 9.5

		self.assertEqual(7.5, offset.XOffset)
		self.assertEqual(8.5, offset.YOffset)
		self.assertEqual(9.5, offset.ZOffset)

	def test_Size(self) -> None:
		size = Size3D(1, 2, 3)

		self.assertIs(Size3D.Width, Size3D.width)
		self.assertIs(Size3D.Height, Size3D.height)
		self.assertIs(Size3D.Depth, Size3D.depth)

		size.width = 7.5
		size.height = 8.5
		size.depth = 9.5

		self.assertEqual(7.5, size.Width)
		self.assertEqual(8.5, size.Height)
		self.assertEqual(9.5, size.Depth)

	def test_LineSegment(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))
		start = Point3D(4, 5, 6)
		end =   Point3D(7, 8, 9)

		self.assertIs(Segment3D.Start, Segment3D.start)
		self.assertIs(Segment3D.End, Segment3D.end)

		line.start = start
		line.end =   end

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertIs(start, line.start)
		self.assertIs(end, line.end)


class LineSegment(Testcase):
	def test_Length(self) -> None:
		"""Every axis contributes its own difference: 2² + 3² + 6² = 7²."""
		line = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 3, 6))

		self.assertEqual(7.0, line.Length)

	def test_AngleTo_Perpendicular(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		line2 = LineSegment3D(Point3D(2, 0, 0), Point3D(2, 0, 2))

		self.assertEqual(pi / 2, line1.AngleTo(line2))

	def test_AngleTo_Parallel(self) -> None:
		"""Same direction, different lengths: the cosine of the angle rounds to 1.0000000000000002, outside acos' domain."""
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 2, 2))

		self.assertEqual(0.0, line1.AngleTo(line2))

	def test_AngleTo_Opposite(self) -> None:
		"""Opposite directions: the cosine of the angle rounds to -1.0000000000000002, outside acos' domain."""
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(-2, -2, -2))

		self.assertEqual(pi, line1.AngleTo(line2))

	def test_AngleTo_None(self) -> None:
		line = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))

		with self.assertRaises(ValueError) as context:
			_ = line.AngleTo(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_AngleTo_Type(self) -> None:
		line = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))

		with self.assertRaises(TypeError) as context:
			_ = line.AngleTo(Point3D(2, 0, 0))

		self.assertEqual("Parameter 'other' is not of type 'LineSegment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_AngleTo_ZeroLength(self) -> None:
		line1 = LineSegment3D(Point3D(1, 1, 1), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))

		with self.assertRaises(ValueError) as context:
			_ = line1.AngleTo(line2)

		self.assertEqual("Line segment has length 0.", str(context.exception))
		self.assertListEqual([
			"Got line segment ((1, 1, 1) → (1, 1, 1)).",
			"Can't determine an angle between two lines if one of the lines has no direction, due to a zero-length."
		], context.exception.__notes__)

	def test_AngleTo_ZeroLengthOther(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		line2 = LineSegment3D(Point3D(1, 1, 1), Point3D(1, 1, 1))

		with self.assertRaises(ValueError) as context:
			_ = line1.AngleTo(line2)

		self.assertEqual("Parameter 'other' has length 0.", str(context.exception))
		self.assertListEqual([
			"Got line segment ((1, 1, 1) → (1, 1, 1)).",
			"Can't determine an angle between two lines if one of the lines has no direction, due to a zero-length."
		], context.exception.__notes__)


class Copy(Testcase):
	def test_Origin(self) -> None:
		origin = Origin3D()

		with self.assertRaises(InvalidOperationError) as context:
			_ = origin.Copy()

		self.assertEqual("An origin can't be copied.", str(context.exception))
		self.assertIsInstance(context.exception, RuntimeError)

	def test_Point_int(self) -> None:
		point = Point3D(1, 2, 3)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.X, int)
		self.assertIsInstance(newPoint.Y, int)
		self.assertIsInstance(newPoint.Z, int)
		self.assertEqual(1, newPoint.X)
		self.assertEqual(2, newPoint.Y)
		self.assertEqual(3, newPoint.Z)
		self.assertTupleEqual((1, 2, 3), newPoint.ToTuple())
		self.assertEqual("Point3D(1, 2, 3)", repr(newPoint))

	def test_Point_float(self) -> None:
		point = Point3D(1.0, 2.0, 3.0)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.X, float)
		self.assertIsInstance(newPoint.Y, float)
		self.assertIsInstance(newPoint.Z, float)
		self.assertEqual(1.0, newPoint.X)
		self.assertEqual(2.0, newPoint.Y)
		self.assertEqual(3.0, newPoint.Z)
		self.assertTupleEqual((1.0, 2.0, 3.0), newPoint.ToTuple())
		self.assertEqual("Point3D(1.0, 2.0, 3.0)", repr(newPoint))

	def test_Offset_int(self) -> None:
		offset = Offset3D(1, 2, 3)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.XOffset, int)
		self.assertIsInstance(newOffset.YOffset, int)
		self.assertIsInstance(newOffset.ZOffset, int)
		self.assertEqual(1, newOffset.XOffset)
		self.assertEqual(2, newOffset.YOffset)
		self.assertEqual(3, newOffset.ZOffset)
		self.assertTupleEqual((1, 2, 3), newOffset.ToTuple())
		self.assertEqual("Offset3D(1, 2, 3)", repr(newOffset))

	def test_Offset_float(self) -> None:
		offset = Offset3D(1.0, 2.0, 3.0)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.XOffset, float)
		self.assertIsInstance(newOffset.YOffset, float)
		self.assertIsInstance(newOffset.ZOffset, float)
		self.assertEqual(1.0, newOffset.XOffset)
		self.assertEqual(2.0, newOffset.YOffset)
		self.assertEqual(3.0, newOffset.ZOffset)
		self.assertTupleEqual((1.0, 2.0, 3.0), newOffset.ToTuple())
		self.assertEqual("Offset3D(1.0, 2.0, 3.0)", repr(newOffset))

	def test_Size_int(self) -> None:
		size = Size3D(1, 2, 3)

		newSize = size.Copy()

		self.assertIsInstance(newSize.Width, int)
		self.assertIsInstance(newSize.Height, int)
		self.assertIsInstance(newSize.Depth, int)
		self.assertEqual(1, newSize.Width)
		self.assertEqual(2, newSize.Height)
		self.assertEqual(3, newSize.Depth)
		self.assertTupleEqual((1, 2, 3), newSize.ToTuple())
		self.assertEqual("Size3D(1, 2, 3)", repr(newSize))

	def test_Size_float(self) -> None:
		size = Size3D(1.0, 2.0, 3.0)

		newSize = size.Copy()

		self.assertIsInstance(newSize.Width, float)
		self.assertIsInstance(newSize.Height, float)
		self.assertIsInstance(newSize.Depth, float)
		self.assertEqual(1.0, newSize.Width)
		self.assertEqual(2.0, newSize.Height)
		self.assertEqual(3.0, newSize.Depth)
		self.assertTupleEqual((1.0, 2.0, 3.0), newSize.ToTuple())
		self.assertEqual("Size3D(1.0, 2.0, 3.0)", repr(newSize))

	def test_Origin_copy(self) -> None:
		origin = Origin3D()

		with self.assertRaises(InvalidOperationError):
			_ = copy(origin)

	def test_Origin_deepcopy(self) -> None:
		origin = Origin3D()

		with self.assertRaises(InvalidOperationError):
			_ = deepcopy(origin)

	def test_Point_Independent(self) -> None:
		point = Point3D(1, 2, 3)

		newPoint =  point.Copy()
		newPoint += (5, 5, 5)

		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())
		self.assertTupleEqual((6, 7, 8), newPoint.ToTuple())

	def test_Point_copy(self) -> None:
		point = Point3D(1, 2, 3)

		newPoint = copy(point)

		self.assertIs(Point3D, type(newPoint))
		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2, 3), newPoint.ToTuple())

	def test_Point_deepcopy(self) -> None:
		point = Point3D(1, 2, 3)

		newPoint = deepcopy(point)

		self.assertIs(Point3D, type(newPoint))
		self.assertIsNot(point, newPoint)
		self.assertTupleEqual((1, 2, 3), newPoint.ToTuple())

	def test_Offset_copy(self) -> None:
		offset = Offset3D(1, 2, 3)

		newOffset = copy(offset)

		self.assertIs(Offset3D, type(newOffset))
		self.assertIsNot(offset, newOffset)
		self.assertEqual(offset, newOffset)

	def test_Offset_deepcopy(self) -> None:
		offset = Offset3D(1, 2, 3)

		newOffset = deepcopy(offset)

		self.assertIs(Offset3D, type(newOffset))
		self.assertIsNot(offset, newOffset)
		self.assertEqual(offset, newOffset)

	def test_Size_copy(self) -> None:
		size = Size3D(1, 2, 3)

		newSize = copy(size)

		self.assertIs(Size3D, type(newSize))
		self.assertIsNot(size, newSize)
		self.assertTupleEqual((1, 2, 3), newSize.ToTuple())

	def test_Size_deepcopy(self) -> None:
		size = Size3D(1, 2, 3)

		newSize = deepcopy(size)

		self.assertIs(Size3D, type(newSize))
		self.assertIsNot(size, newSize)
		self.assertTupleEqual((1, 2, 3), newSize.ToTuple())

	def test_LineSegment(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))

		newLine =       line.Copy()
		newLine.Start += (5, 5, 5)
		newLine.End +=   (5, 5, 5)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line, newLine)
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), line.ToTuple())
		self.assertTupleEqual(((6, 7, 8), (7, 8, 9)), newLine.ToTuple())

	def test_LineSegment_copy(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))

		newLine = copy(line)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), newLine.ToTuple())

	def test_LineSegment_deepcopy(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))

		newLine = deepcopy(line)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIsNot(line.End, newLine.End)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), newLine.ToTuple())

	def test_LineSegment_deepcopy_Group(self) -> None:
		"""A deep copy owns its points and isn't in the group of the original."""
		group = Group3D()
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4), parent=group)

		newLine = deepcopy(line)

		self.assertIsNone(newLine.Parent)
		self.assertIs(newLine, newLine.Start.Parent)
		self.assertIs(newLine, newLine.End.Parent)
		self.assertTupleEqual((line, ), group.Children)

	def test_LineSegment_Origin(self) -> None:
		line = LineSegment3D(Origin3D(), Point3D(2, 3, 4), copyPoints=False)

		with self.assertRaises(InvalidOperationError):
			_ = line.Copy()


class Comparison(Testcase):
	def test_Offset_Equal_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(1, 2, 3)

		self.assertEqual(offset1, offset2)

	def test_Offset_Equal_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (1, 2, 3)

		self.assertEqual(offset1, offset2)

	def test_Offset_Equal_int(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 == offset2

	def test_Offset_Unequal_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		self.assertTrue(offset1 != offset2)


class PointArithmetic(Testcase):
	def test_Point_Plus_Point(self) -> None:
		point1 = Point3D(1, 2, 3)
		point2 = Point3D(2, 3, 4)

		with self.assertRaises(TypeError):
			_ = point1 + point2

	def test_Point_Plus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		newPoint = point + offset

		self.assertEqual(3, newPoint.X)
		self.assertEqual(5, newPoint.Y)
		self.assertEqual(7, newPoint.Z)

	def test_Point_Plus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		newPoint = point + offset

		self.assertEqual(3, newPoint.X)
		self.assertEqual(5, newPoint.Y)
		self.assertEqual(7, newPoint.Z)

	def test_Point_InplacePlus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		point += offset

		self.assertEqual(3, point.X)
		self.assertEqual(5, point.Y)
		self.assertEqual(7, point.Z)

	def test_Point_InplacePlus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		point += offset

		self.assertEqual(3, point.X)
		self.assertEqual(5, point.Y)
		self.assertEqual(7, point.Z)

	def test_Point_InplacePlus_TupleComplex(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point += (1j, 1, 1)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Point_InplacePlus_Int(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError):
			point += 2

	def test_Point_Minus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		newPoint = point + -offset

		self.assertEqual(-1, newPoint.X)
		self.assertEqual(-1, newPoint.Y)
		self.assertEqual(-1, newPoint.Z)

	def test_Point_Minus_Point(self) -> None:
		point1 = Point3D(1, 2, 3)
		point2 = Point3D(2, 3, 4)

		offset = point2 - point1

		self.assertEqual(1, offset.XOffset)
		self.assertEqual(1, offset.YOffset)
		self.assertEqual(1, offset.ZOffset)

	def test_Point_Minus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = point - 2

	def test_Point_InplaceMinus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		point -= offset

		self.assertEqual(-1, point.X)
		self.assertEqual(-1, point.Y)
		self.assertEqual(-1, point.Z)

	def test_Point_InplaceMinus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		point -= offset

		self.assertEqual(-1, point.X)
		self.assertEqual(-1, point.Y)
		self.assertEqual(-1, point.Z)

	def test_Point_InplaceMinus_TupleComplex(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point -= (1j, 1, 1)

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Point_InplaceMinus_Int(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError):
			point -= 2


class OffsetArithmetic(Testcase):
	def test_Offset_Plus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.XOffset)
		self.assertEqual(5, newOffset.YOffset)
		self.assertEqual(7, newOffset.ZOffset)

	def test_Offset_Plus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.XOffset)
		self.assertEqual(5, newOffset.YOffset)
		self.assertEqual(7, newOffset.ZOffset)

	def test_Offset_Plus_int(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 + offset2

	def test_Offset_InplacePlus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		offset1 += offset2

		self.assertEqual(3, offset1.XOffset)
		self.assertEqual(5, offset1.YOffset)
		self.assertEqual(7, offset1.ZOffset)

	def test_Offset_InplacePlus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		offset1 += offset2

		self.assertEqual(3, offset1.XOffset)
		self.assertEqual(5, offset1.YOffset)
		self.assertEqual(7, offset1.ZOffset)

	def test_Offset_InplacePlus_TupleComplex(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset += (1j, 1, 1)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Offset_InplacePlus_Int(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError):
			offset += 2

	def test_Offset_Minus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.XOffset)
		self.assertEqual(-1, newOffset.YOffset)
		self.assertEqual(-1, newOffset.ZOffset)

	def test_Offset_Minus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.XOffset)
		self.assertEqual(-1, newOffset.YOffset)
		self.assertEqual(-1, newOffset.ZOffset)

	def test_Offset_Minus_int(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 - offset2

	def test_Offset_InplaceMinus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		offset1 -= offset2

		self.assertEqual(-1, offset1.XOffset)
		self.assertEqual(-1, offset1.YOffset)
		self.assertEqual(-1, offset1.ZOffset)

	def test_Offset_InplaceMinus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		offset1 -= offset2

		self.assertEqual(-1, offset1.XOffset)
		self.assertEqual(-1, offset1.YOffset)
		self.assertEqual(-1, offset1.ZOffset)

	def test_Offset_InplaceMinus_TupleComplex(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset -= (1j, 1, 1)

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'complex'."], context.exception.__notes__)

	def test_Offset_InplaceMinus_Int(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError):
			offset -= 2


class Bounds(Testcase):
	def test_BoundingBox_int(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		self.assertEqual(1, box.MinX)
		self.assertEqual(2, box.MinY)
		self.assertEqual(3, box.MinZ)
		self.assertEqual(4, box.MaxX)
		self.assertEqual(6, box.MaxY)
		self.assertEqual(8, box.MaxZ)
		self.assertEqual(3, box.Width)
		self.assertEqual(4, box.Height)
		self.assertEqual(5, box.Depth)
		self.assertTupleEqual((2.5, 4.0, 5.5), box.Center.ToTuple())
		self.assertTupleEqual((1, 2, 3, 4, 6, 8), box.ToTuple())

	def test_BoundingBox_float(self) -> None:
		box = BoundingBox3D(-1.5, -2.5, -3.5, 0.5, 0.5, 0.5)

		self.assertEqual(2.0, box.Width)
		self.assertEqual(3.0, box.Height)
		self.assertEqual(4.0, box.Depth)
		self.assertTupleEqual((-0.5, -1.0, -1.5), box.Center.ToTuple())

	def test_BoundingBox_Point(self) -> None:
		"""A bounding box may have no extent."""
		box = BoundingBox3D(1, 2, 3, 1, 2, 3)

		self.assertEqual(0, box.Width)
		self.assertEqual(0, box.Height)
		self.assertEqual(0, box.Depth)

	def test_BoundingBox_None1(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(None, 2, 3, 4, 6, 8)

		self.assertEqual("Parameter 'minX' is None.", str(context.exception))

	def test_BoundingBox_None3(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(1, 2, None, 4, 6, 8)

		self.assertEqual("Parameter 'minZ' is None.", str(context.exception))

	def test_BoundingBox_None6(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(1, 2, 3, 4, 6, None)

		self.assertEqual("Parameter 'maxZ' is None.", str(context.exception))

	def test_BoundingBox_str1(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox3D("1", 2, 3, 4, 6, 8)

		self.assertEqual("Parameter 'minX' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_str6(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox3D(1, 2, 3, 4, 6, "8")

		self.assertEqual("Parameter 'maxZ' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_BoundingBox_MaxXLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(4, 2, 3, 1, 6, 8)

		self.assertEqual("Parameter 'maxX' is less than parameter 'minX'.", str(context.exception))
		self.assertListEqual(["Got minX=4 and maxX=1."], context.exception.__notes__)

	def test_BoundingBox_MaxYLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(1, 6, 3, 4, 2, 8)

		self.assertEqual("Parameter 'maxY' is less than parameter 'minY'.", str(context.exception))
		self.assertListEqual(["Got minY=6 and maxY=2."], context.exception.__notes__)

	def test_BoundingBox_MaxZLess(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D(1, 2, 8, 4, 6, 3)

		self.assertEqual("Parameter 'maxZ' is less than parameter 'minZ'.", str(context.exception))
		self.assertListEqual(["Got minZ=8 and maxZ=3."], context.exception.__notes__)

	def test_BoundingBox_ReadOnly(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		with self.assertRaises(AttributeError):
			box.MinZ = 0

		self.assertEqual(3, box.MinZ)

	def test_FromPoints(self) -> None:
		box = BoundingBox3D.FromPoints((Point3D(3, -1, 0), Point3D(-2, 4, 5), Point3D(1, 1, -6)))

		self.assertIs(BoundingBox3D, type(box))
		self.assertTupleEqual((-2, -1, -6, 3, 4, 5), box.ToTuple())

	def test_FromPoints_Generator(self) -> None:
		box = BoundingBox3D.FromPoints(Point3D(x, 2 * x, 3 * x) for x in range(4))

		self.assertTupleEqual((0, 0, 0, 3, 6, 9), box.ToTuple())

	def test_FromPoints_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D.FromPoints(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_FromPoints_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox3D.FromPoints(3)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_FromPoints_NoneFirst(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D.FromPoints((None, Point3D(0, 0, 0)))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_FromPoints_NoneElement(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D.FromPoints((Point3D(0, 0, 0), None))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_FromPoints_tupleFirst(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox3D.FromPoints(((1, 1, 1), Point3D(0, 0, 0)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_tupleElement(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = BoundingBox3D.FromPoints((Point3D(0, 0, 0), (1, 1, 1)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BoundingBox3D.FromPoints(())

		self.assertEqual("Parameter 'points' is empty.", str(context.exception))

	def test_Union(self) -> None:
		box1 = BoundingBox3D(0, 0, 0, 2, 2, 2)
		box2 = BoundingBox3D(1, -1, 1, 4, 1, 5)

		box = box1.Union(box2)

		self.assertTupleEqual((0, -1, 0, 4, 2, 5), box.ToTuple())
		self.assertTupleEqual((0, 0, 0, 2, 2, 2), box1.ToTuple())
		self.assertTupleEqual((1, -1, 1, 4, 1, 5), box2.ToTuple())

	def test_Union_None(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.Union(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_Union_tuple(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.Union((1, 1, 1, 3, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_HasOverlap(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		self.assertTrue(box.HasOverlap(BoundingBox3D(1, 1, 1, 3, 3, 3)))
		self.assertTrue(box.HasOverlap(BoundingBox3D(-1, -1, -1, 3, 3, 3)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(3, 0, 0, 4, 2, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(0, -2, 0, 2, -1, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(0, 0, 3, 2, 2, 4)))

	def test_HasOverlap_Touching(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		self.assertFalse(box.HasOverlap(BoundingBox3D(2, 0, 0, 4, 2, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(0, -2, 0, 2, 0, 2)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(0, 0, 2, 2, 2, 4)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(0, 0, -2, 2, 2, 0)))
		self.assertFalse(box.HasOverlap(BoundingBox3D(2, 2, 2, 3, 3, 3)))

	def test_HasOverlap_None(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.HasOverlap(None)

		self.assertEqual("Parameter 'other' is None.", str(context.exception))

	def test_HasOverlap_tuple(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.HasOverlap((1, 1, 1, 3, 3, 3))

		self.assertEqual("Parameter 'other' is not of type 'BoundingBox3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_ContainsPoint(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		self.assertTrue(box.ContainsPoint(Point3D(1, 1, 1)))
		self.assertTrue(box.ContainsPoint(Point3D(2, 0, 2)))
		self.assertFalse(box.ContainsPoint(Point3D(3, 1, 1)))
		self.assertFalse(box.ContainsPoint(Point3D(1, -0.5, 1)))
		self.assertFalse(box.ContainsPoint(Point3D(1, 1, 2.5)))

	def test_ContainsPoint_None(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(ValueError) as context:
			_ = box.ContainsPoint(None)

		self.assertEqual("Parameter 'point' is None.", str(context.exception))

	def test_ContainsPoint_tuple(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = box.ContainsPoint((1, 1, 1))

		self.assertEqual("Parameter 'point' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_In(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		self.assertIn(Point3D(1, 1, 1), box)
		self.assertIn(Point3D(2, 0, 2), box)
		self.assertNotIn(Point3D(1, 1, 3), box)

	def test_In_tuple(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = (1, 1, 1) in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for first operand: Point3D"],
			context.exception.__notes__
		)

	def test_In_None(self) -> None:
		box = BoundingBox3D(0, 0, 0, 2, 2, 2)

		with self.assertRaises(TypeError) as context:
			_ = None in box

		self.assertEqual("First operand is not supported by in operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for first operand: Point3D"],
			context.exception.__notes__
		)

	def test_Equal(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		self.assertTrue(box == BoundingBox3D(1, 2, 3, 4, 6, 8))
		self.assertFalse(box == BoundingBox3D(1, 2, 3, 4, 6, 9))
		self.assertFalse(box != BoundingBox3D(1, 2, 3, 4, 6, 8))
		self.assertTrue(box != BoundingBox3D(1, 2, 0, 4, 6, 8))

	def test_Equal_tuple(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		with self.assertRaises(TypeError) as context:
			_ = box == (1, 2, 3, 4, 6, 8)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox3D"],
			context.exception.__notes__
		)

	def test_Unequal_tuple(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		with self.assertRaises(TypeError) as context:
			_ = box != (1, 2, 3, 4, 6, 8)

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: BoundingBox3D"],
			context.exception.__notes__
		)

	def test_Plus_Offset(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		newBox = box + Offset3D(10, -2, 1)

		self.assertIs(BoundingBox3D, type(newBox))
		self.assertTupleEqual((11, 0, 4, 14, 4, 9), newBox.ToTuple())
		self.assertTupleEqual((1, 2, 3, 4, 6, 8), box.ToTuple())

	def test_Plus_tuple(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		with self.assertRaises(TypeError) as context:
			_ = box + (10, -2, 1)

		self.assertEqual("Parameter 'other' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Copy(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4, 6, 8)

		for newBox in (box.Copy(), copy(box), deepcopy(box)):
			self.assertIs(BoundingBox3D, type(newBox))
			self.assertIsNot(box, newBox)
			self.assertEqual(box, newBox)

	def test_repr(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4.5, 6, 8)

		self.assertEqual("BoundingBox3D(1, 2, 3, 4.5, 6, 8)", repr(box))

	def test_str(self) -> None:
		box = BoundingBox3D(1, 2, 3, 4.5, 6, 8)

		self.assertEqual("((1, 2, 3), (4.5, 6, 8))", str(box))

	def test_LineSegment(self) -> None:
		line = LineSegment3D(Point3D(4, 1, -2), Point3D(-1, 3, 5))

		box = line.BoundingBox

		self.assertTupleEqual((-1, 1, -2, 4, 3, 5), box.ToTuple())

	def test_LineSegment_ReadOnly(self) -> None:
		line = LineSegment3D(Point3D(4, 1, -2), Point3D(-1, 3, 5))

		with self.assertRaises(AttributeError):
			line.BoundingBox = BoundingBox3D(0, 0, 0, 1, 1, 1)


class Moving(Testcase):
	def test_LineSegment(self) -> None:
		start = Point3D(1, 2, 3)
		end =   Point3D(4, 6, 8)
		line =  LineSegment3D(start, end, copyPoints=False)

		line.Move(Offset3D(1, -1, 2))

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertTupleEqual(((2, 1, 5), (5, 5, 10)), line.ToTuple())

	def test_LineSegment_None(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_LineSegment_tuple(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.Move((1, 1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())


class Hierarchy(Testcase):
	def test_Base(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Base3D()

	def test_Element3D(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Element3D()

	def test_Point(self) -> None:
		self.assertIsInstance(Point3D(1, 2, 3), Base3D)
		self.assertNotIsInstance(Point3D(1, 2, 3), Element3D)

	def test_Origin(self) -> None:
		origin = Origin3D()

		self.assertIsInstance(origin, Base3D)
		self.assertIsNone(origin.Parent)
		self.assertIsNone(origin.Frame)

	def test_Segment(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Segment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual("Class 'Segment3D' is abstract and needs to be derived.", str(context.exception))

	def test_LineSegment(self) -> None:
		self.assertIsInstance(LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8)), Segment3D)
		self.assertIsInstance(LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8)), Element3D)

	def test_Slots(self) -> None:
		"""The parent is a slot of the base-class only, value and key-value-pairs are slots of elements only."""
		self.assertTupleEqual(("_parent", ), Base3D.__slots__)
		self.assertTupleEqual(("_value", "_dict"), Element3D.__slots__)
		self.assertTupleEqual(("_x", "_y", "_z"), Point3D.__slots__)
		self.assertNotIn("_parent", Segment3D.__slots__)
		self.assertNotIn("_value", Segment3D.__slots__)


class Ownership(Testcase):
	def test_Point(self) -> None:
		point = Point3D(1, 2, 3)

		self.assertIsNone(point.Parent)
		self.assertIsNone(point.Frame)

	def test_Point_Parent(self) -> None:
		"""The parent parameter sets the owner, but the point isn't registered."""
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		start = line.Start
		end =   line.End

		point = Point3D(7, 8, 9, parent=line)

		self.assertIs(line, point.Parent)
		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertIs(line, start.Parent)

	def test_Point_ParentNone(self) -> None:
		point = Point3D(1, 2, 3, parent=None)

		self.assertIsNone(point.Parent)

	def test_Point_ParentInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Point3D(1, 2, 3, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Point_ParentPoint(self) -> None:
		"""A point can't own another point."""
		with self.assertRaises(TypeError) as context:
			_ = Point3D(1, 2, 3, parent=Point3D(4, 5, 6))

		self.assertEqual("Parameter 'parent' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_Point_ParentPositional(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError):
			_ = Point3D(1, 2, 3, line)

	def test_Point_Parent_Copy(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		point = Point3D(7, 8, 9, parent=line)

		self.assertIsNone(point.Copy().Parent)
		self.assertIsNone(copy(point).Parent)
		self.assertIsNone(deepcopy(point).Parent)

	def test_Point_Parent_ToOtherSegment(self) -> None:
		"""A point with a parent is owned, so another segment can't take it without copying."""
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		point = Point3D(7, 8, 9, parent=line)

		with self.assertRaises(AlreadyOwnedError):
			_ = LineSegment3D(point, Point3D(9, 9, 9), copyPoints=False)

		other = LineSegment3D(point, Point3D(9, 9, 9))

		self.assertIs(other, other.Start.Parent)
		self.assertIsNot(point, other.Start)
		self.assertIs(line, point.Parent)

	def test_Point_Parent_ToParentSegment(self) -> None:
		"""The parent segment can replace its points with a point of which it is the owner."""
		line =     LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		start =    line.Start
		end =      line.End
		newStart = Point3D(7, 8, 9, parent=line)
		newEnd =   Point3D(9, 9, 9, parent=line)

		line.Start = newStart
		line.End =   newEnd

		self.assertIs(newStart, line.Start)
		self.assertIs(newEnd, line.End)
		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_Point_ReadOnly(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.Parent = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))

		self.assertEqual("The parent of a 'pyTooling.Cartesian3D.Point3D' is read-only.", str(context.exception))
		self.assertListEqual(
			[
				"Got type 'pyTooling.Cartesian3D.LineSegment3D'.",
				"A segment takes ownership of a point, when it's given the point."
			],
			context.exception.__notes__
		)
		self.assertIsNone(point.Parent)

	def test_Point_Copy(self) -> None:
		"""A copy of an owned point has no owner."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		point = line.Start.Copy()

		self.assertIsNone(point.Parent)

	def test_LineSegment_Copy(self) -> None:
		"""A segment owns copies of the given points; the given points stay without owner."""
		start = Point3D(1, 2, 3)
		end =   Point3D(4, 6, 8)

		line = LineSegment3D(start, end)

		self.assertIsNone(line.Parent)
		self.assertIsNone(line.Frame)
		self.assertIs(line, line.Start.Parent)
		self.assertIs(line, line.End.Parent)
		self.assertIsNone(start.Parent)
		self.assertIsNone(end.Parent)

	def test_LineSegment_Reference(self) -> None:
		start = Point3D(1, 2, 3)
		end =   Point3D(4, 6, 8)

		line = LineSegment3D(start, end, copyPoints=False)

		self.assertIs(line, start.Parent)
		self.assertIs(line, end.Parent)

	def test_LineSegment_OwnedStart(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = LineSegment3D(line.Start, Point3D(7, 8, 9), copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			[
				"Got point (1, 2, 3) owned by LineSegment3D((1, 2, 3), (4, 6, 8)).",
				"Use 'copyPoints=True' to copy the point."
			],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception, AlreadyInHierarchyError)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'start' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(line, line.Start.Parent)

	def test_LineSegment_OwnedEnd(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		start = Point3D(7, 8, 9)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = LineSegment3D(start, line.End, copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertEqual("Parameter 'end' is owned by another element.", str(context.exception.__cause__))
		self.assertIsNone(start.Parent)
		self.assertIs(line, line.End.Parent)

	def test_LineSegment_SamePoint(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(DuplicatePointError) as context:
			_ = LineSegment3D(point, point, copyPoints=False)

		self.assertIsInstance(context.exception, DuplicateElementError)
		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 2, 3).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'end' is the same point as parameter 'start'.", str(context.exception.__cause__))
		self.assertIsNone(point.Parent)

	def test_LineSegment_EqualCoordinates(self) -> None:
		"""Two different point objects with equal coordinates aren't a duplicate."""
		start = Point3D(1, 2, 3)
		end =   Point3D(1, 2, 3)

		line = LineSegment3D(start, end, copyPoints=False)

		self.assertIs(start, line.Start)
		self.assertIs(end, line.End)
		self.assertEqual(0.0, line.Length)

	def test_LineSegment_SamePoint_Copy(self) -> None:
		point = Point3D(1, 2, 3)

		line = LineSegment3D(point, point)

		self.assertIsNot(line.Start, line.End)
		self.assertEqual(0.0, line.Length)

	def test_Segment_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), False)

	def test_LineSegment_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), False)

	def test_LineSegment_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_LineSegment_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), copyPoints=0)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_Start(self) -> None:
		"""An assigned start point is owned by the segment, the previous one is released."""
		line =     LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		previous = line.Start
		point =    Point3D(7, 8, 9)

		line.Start = point

		self.assertIs(line, point.Parent)
		self.assertIsNone(previous.Parent)

	def test_LineSegment_Start_Same(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		start = line.Start

		line.Start = start

		self.assertIs(start, line.Start)
		self.assertIs(line, start.Parent)

	def test_LineSegment_Start_Owned(self) -> None:
		line1 = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		line2 = LineSegment3D(Point3D(7, 8, 9), Point3D(9, 9, 9))
		start = line1.Start

		with self.assertRaises(AlreadyOwnedError) as context:
			line1.Start = line2.Start

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (7, 8, 9) owned by LineSegment3D((7, 8, 9), (9, 9, 9))."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'start' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(start, line1.Start)
		self.assertIs(line2, line2.Start.Parent)

	def test_LineSegment_Start_End(self) -> None:
		"""The segment's own end point can't become its start point."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(DuplicatePointError) as context:
			line.Start = line.End

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (4, 6, 8)."], context.exception.__notes__)
		self.assertEqual("Parameter 'start' is the segment's end point.", str(context.exception.__cause__))

	def test_LineSegment_End(self) -> None:
		line =     LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		previous = line.End
		point =    Point3D(7, 8, 9)

		line.End = point

		self.assertIs(line, point.Parent)
		self.assertIsNone(previous.Parent)

	def test_LineSegment_End_Start(self) -> None:
		"""The segment's own start point can't become its end point."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(DuplicatePointError) as context:
			line.End = line.Start

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (1, 2, 3)."], context.exception.__notes__)
		self.assertEqual("Parameter 'end' is the segment's start point.", str(context.exception.__cause__))

	def test_LineSegment_End_Same(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		end =  line.End

		line.End = end

		self.assertIs(end, line.End)
		self.assertIs(line, end.Parent)

	def test_LineSegment_End_Owned(self) -> None:
		line1 = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		line2 = LineSegment3D(Point3D(7, 8, 9), Point3D(9, 9, 9))
		end =   line1.End

		with self.assertRaises(AlreadyOwnedError) as context:
			line1.End = line2.End

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (9, 9, 9) owned by LineSegment3D((7, 8, 9), (9, 9, 9))."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'end' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(end, line1.End)


class Node(Base3D):
	"""A class with a parent, using the setter of :class:`Base3D`."""

	_PARENT_TYPE = (Point3D, )


class ParentSetter(Testcase):
	def test_Assign(self) -> None:
		point = Point3D(1, 2, 3)
		node =  Node()

		node.Parent = point

		self.assertIs(point, node.Parent)

	def test_AssignNone(self) -> None:
		node = Node(parent=Point3D(1, 2, 3))

		node.Parent = None

		self.assertIsNone(node.Parent)

	def test_AssignInt(self) -> None:
		node = Node()

		with self.assertRaises(TypeError) as context:
			node.Parent = 1

		self.assertEqual("Parameter 'parent' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(node.Parent)


class ParentTypes(Testcase):
	def test_Point(self) -> None:
		self.assertTupleEqual((Element3D, ), Point3D._PARENT_TYPE)

	def test_Origin(self) -> None:
		self.assertTupleEqual((Element3D, ), Origin3D._PARENT_TYPE)

	def test_Segment(self) -> None:
		self.assertTupleEqual((Group3D, ), Segment3D._PARENT_TYPE)

	def test_LineSegment(self) -> None:
		self.assertTupleEqual((Group3D, ), LineSegment3D._PARENT_TYPE)

	def test_Group(self) -> None:
		self.assertTupleEqual((Group3D, ), Group3D._PARENT_TYPE)


class Frames(Testcase):
	def test_Point_Minus_Point(self) -> None:
		"""Points of two standalone segments have no frame, so they can be subtracted."""
		line1 = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		line2 = LineSegment3D(Point3D(7, 8, 9), Point3D(9, 9, 9))

		offset = line2.Start - line1.Start

		self.assertTupleEqual((6, 6, 6), offset.ToTuple())

	def test_LineSegment_AngleTo(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(5, 5, 5), Point3D(5, 5, 7))

		self.assertTrue(isclose(pi / 2, line1.AngleTo(line2)))


class Aligning(Testcase):
	def test_MinX(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MinX)

		self.assertEqual(BoundingBox3D(0, 9, 9, 2, 11, 11), line.BoundingBox)

	def test_CenterX(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.CenterX)

		self.assertEqual(BoundingBox3D(1, 9, 9, 3, 11, 11), line.BoundingBox)

	def test_MaxX(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MaxX)

		self.assertEqual(BoundingBox3D(2, 9, 9, 4, 11, 11), line.BoundingBox)

	def test_MinY(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MinY)

		self.assertEqual(BoundingBox3D(9, 0, 9, 11, 2, 11), line.BoundingBox)

	def test_CenterY(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 4, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.CenterY)

		self.assertEqual(BoundingBox3D(9, 1, 9, 11, 3, 11), line.BoundingBox)

	def test_MaxY(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MaxY)

		self.assertEqual(BoundingBox3D(9, 0, 9, 11, 2, 11), line.BoundingBox)

	def test_MinZ(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MinZ)

		self.assertEqual(BoundingBox3D(9, 9, 0, 11, 11, 2), line.BoundingBox)

	def test_CenterZ(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.CenterZ)

		self.assertEqual(BoundingBox3D(9, 9, 2, 11, 11, 4), line.BoundingBox)

	def test_MaxZ(self) -> None:
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		line.AlignTo(reference, Alignment3D.MaxZ)

		self.assertEqual(BoundingBox3D(9, 9, 4, 11, 11, 6), line.BoundingBox)

	def test_OtherGroup(self) -> None:
		"""Elements of different groups are aligned by their absolute bounding boxes."""
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		line =      LineSegment3D(Point3D(0, 0, 0), Point3D(2, 2, 2))
		_ =         Group3D(Offset3D(10, 0, 0), (reference, ))
		_ =         Group3D(Offset3D(0, 50, 0), (line, ))

		line.AlignTo(reference, Alignment3D.MaxX)

		self.assertEqual(BoundingBox3D(12, 50, 0, 14, 52, 2), line.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox3D(12, 0, 0, 14, 2, 2), line.BoundingBox)

	def test_Group(self) -> None:
		"""Aligning a group changes its offset."""
		reference = LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		group =     Group3D(Offset3D(10, 10, 10), (LineSegment3D(Point3D(0, 0, 0), Point3D(2, 2, 2)), ))

		group.AlignTo(reference, Alignment3D.MaxZ)

		self.assertTupleEqual((10, 10, 4), group.Offset.ToTuple())

	def test_ReferenceNone(self) -> None:
		line = LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		with self.assertRaises(ValueError) as context:
			line.AlignTo(None, Alignment3D.MinX)

		self.assertEqual("Parameter 'reference' is None.", str(context.exception))

	def test_ReferencePoint(self) -> None:
		line = LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		with self.assertRaises(TypeError) as context:
			line.AlignTo(Point3D(0, 0, 0), Alignment3D.MinX)

		self.assertEqual("Parameter 'reference' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_AlignmentNone(self) -> None:
		line = LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		with self.assertRaises(ValueError) as context:
			line.AlignTo(LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_AlignmentStr(self) -> None:
		line = LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		with self.assertRaises(TypeError) as context:
			line.AlignTo(LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), "MinX")

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((9, 9, 9), (11, 11, 11)), line.ToTuple())

	def test_Alignment2D(self) -> None:
		"""The 2D alignment isn't accepted."""
		line = LineSegment3D(Point3D(9, 9, 9), Point3D(11, 11, 11))

		with self.assertRaises(TypeError) as context:
			line.AlignTo(LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), Alignment2D.MinX)

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)


class Mirroring(Testcase):
	def test_MirrorX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorX()

		self.assertTupleEqual(((4, 2, 3), (1, 6, 8)), line.ToTuple())

	def test_MirrorX_MinX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorX(Alignment3D.MinX)

		self.assertTupleEqual(((1, 2, 3), (-2, 6, 8)), line.ToTuple())

	def test_MirrorX_MaxX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorX(Alignment3D.MaxX)

		self.assertTupleEqual(((7, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_Offset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorX(Alignment3D.MinX, 1)

		self.assertTupleEqual(((3, 2, 3), (0, 6, 8)), line.ToTuple())

	def test_MirrorX_FloatOffset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorX(Alignment3D.MaxX, -0.5)

		self.assertTupleEqual(((6.0, 2, 3), (3.0, 6, 8)), line.ToTuple())

	def test_MirrorX_Int(self) -> None:
		"""A plane between two integer coordinates keeps integer coordinates."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(6, 6, 8))

		line.MirrorX(Alignment3D.CenterX)

		self.assertTupleEqual(((6, 2, 3), (1, 6, 8)), line.ToTuple())
		self.assertIs(int, type(line.Start.X))
		self.assertIs(int, type(line.End.X))

	def test_MirrorX_PlaneNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorX(None)

		self.assertEqual("Parameter 'plane' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_PlaneStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorX("MinX")

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_Plane2D(self) -> None:
		"""The 2D alignment isn't accepted."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorX(Alignment2D.MinX)

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_PlaneYZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		for plane in (
			Alignment3D.MinY,
			Alignment3D.CenterY,
			Alignment3D.MaxY,
			Alignment3D.MinZ,
			Alignment3D.CenterZ,
			Alignment3D.MaxZ
		):
			with self.subTest(plane=plane):
				with self.assertRaises(ValueError) as context:
					line.MirrorX(plane)

				self.assertEqual(
					"Parameter 'plane' is not Alignment3D.MinX, Alignment3D.CenterX or Alignment3D.MaxX.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment3D.{plane.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_OffsetNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorX(Alignment3D.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorX_OffsetStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorX(Alignment3D.MinX, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorY()

		self.assertTupleEqual(((1, 6, 3), (4, 2, 8)), line.ToTuple())

	def test_MirrorY_MinY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorY(Alignment3D.MinY)

		self.assertTupleEqual(((1, 2, 3), (4, -2, 8)), line.ToTuple())

	def test_MirrorY_MaxY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorY(Alignment3D.MaxY)

		self.assertTupleEqual(((1, 10, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_Offset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorY(Alignment3D.MinY, 1)

		self.assertTupleEqual(((1, 4, 3), (4, 0, 8)), line.ToTuple())

	def test_MirrorY_FloatOffset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorY(Alignment3D.MaxY, -0.5)

		self.assertTupleEqual(((1, 9.0, 3), (4, 5.0, 8)), line.ToTuple())

	def test_MirrorY_Int(self) -> None:
		"""A plane between two integer coordinates keeps integer coordinates."""
		line = LineSegment3D(Point3D(1, 1, 3), Point3D(4, 6, 8))

		line.MirrorY(Alignment3D.CenterY)

		self.assertTupleEqual(((1, 6, 3), (4, 1, 8)), line.ToTuple())
		self.assertIs(int, type(line.Start.Y))
		self.assertIs(int, type(line.End.Y))

	def test_MirrorY_PlaneNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorY(None)

		self.assertEqual("Parameter 'plane' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_PlaneStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorY("MinY")

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_Plane2D(self) -> None:
		"""The 2D alignment isn't accepted."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorY(Alignment2D.MinY)

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_PlaneXZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		for plane in (
			Alignment3D.MinX,
			Alignment3D.CenterX,
			Alignment3D.MaxX,
			Alignment3D.MinZ,
			Alignment3D.CenterZ,
			Alignment3D.MaxZ
		):
			with self.subTest(plane=plane):
				with self.assertRaises(ValueError) as context:
					line.MirrorY(plane)

				self.assertEqual(
					"Parameter 'plane' is not Alignment3D.MinY, Alignment3D.CenterY or Alignment3D.MaxY.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment3D.{plane.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_OffsetNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorY(Alignment3D.MinY, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorY_OffsetStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorY(Alignment3D.MinY, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorZ()

		self.assertTupleEqual(((1, 2, 8), (4, 6, 3)), line.ToTuple())

	def test_MirrorZ_MinZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorZ(Alignment3D.MinZ)

		self.assertTupleEqual(((1, 2, 3), (4, 6, -2)), line.ToTuple())

	def test_MirrorZ_MaxZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorZ(Alignment3D.MaxZ)

		self.assertTupleEqual(((1, 2, 13), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_Offset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorZ(Alignment3D.MinZ, 1)

		self.assertTupleEqual(((1, 2, 5), (4, 6, 0)), line.ToTuple())

	def test_MirrorZ_FloatOffset(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorZ(Alignment3D.MaxZ, -0.5)

		self.assertTupleEqual(((1, 2, 12.0), (4, 6, 7.0)), line.ToTuple())

	def test_MirrorZ_Int(self) -> None:
		"""A plane between two integer coordinates keeps integer coordinates."""
		line = LineSegment3D(Point3D(1, 2, 1), Point3D(4, 6, 6))

		line.MirrorZ(Alignment3D.CenterZ)

		self.assertTupleEqual(((1, 2, 6), (4, 6, 1)), line.ToTuple())
		self.assertIs(int, type(line.Start.Z))
		self.assertIs(int, type(line.End.Z))

	def test_MirrorZ_PlaneNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorZ(None)

		self.assertEqual("Parameter 'plane' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_PlaneStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorZ("MinZ")

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_Plane2D(self) -> None:
		"""The 2D alignment isn't accepted."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorZ(Alignment2D.MinX)

		self.assertEqual("Parameter 'plane' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_PlaneXY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		for plane in (
			Alignment3D.MinX,
			Alignment3D.CenterX,
			Alignment3D.MaxX,
			Alignment3D.MinY,
			Alignment3D.CenterY,
			Alignment3D.MaxY
		):
			with self.subTest(plane=plane):
				with self.assertRaises(ValueError) as context:
					line.MirrorZ(plane)

				self.assertEqual(
					"Parameter 'plane' is not Alignment3D.MinZ, Alignment3D.CenterZ or Alignment3D.MaxZ.",
					str(context.exception)
				)
				self.assertListEqual([f"Got value 'Alignment3D.{plane.name}'."], context.exception.__notes__)

		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_OffsetNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorZ(Alignment3D.MinZ, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ_OffsetStr(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorZ(Alignment3D.MinZ, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())


class Planes(Testcase):
	def test_Plane3D(self) -> None:
		"""A plane is parallel to a coordinate plane; the base class can't be instantiated."""
		with self.assertRaises(AbstractClassError) as context:
			Plane3D()

		self.assertEqual(
			"Class 'Plane3D' is abstract. The following methods: '_MirrorElement' need to be overridden in a derived class.",
			str(context.exception)
		)

	def test_Derived(self) -> None:
		self.assertIsInstance(YZPlane3D(5), Plane3D)
		self.assertIsInstance(XZPlane3D(5), Plane3D)
		self.assertIsInstance(XYPlane3D(5), Plane3D)


class YZPlanes(Testcase):
	def test_YZPlane3D(self) -> None:
		plane = YZPlane3D(5)

		self.assertEqual(5, plane.X)

	def test_YZPlane3D_Float(self) -> None:
		plane = YZPlane3D(-2.5)

		self.assertEqual(-2.5, plane.X)

	def test_XNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			YZPlane3D(None)

		self.assertEqual("Parameter 'x' is None.", str(context.exception))

	def test_XStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			YZPlane3D("5")

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Equal(self) -> None:
		self.assertTrue(YZPlane3D(5) == YZPlane3D(5.0))
		self.assertFalse(YZPlane3D(5) == YZPlane3D(6))
		self.assertFalse(YZPlane3D(5) == XZPlane3D(5))
		self.assertFalse(YZPlane3D(5) == XYPlane3D(5))

	def test_Unequal(self) -> None:
		self.assertTrue(YZPlane3D(5) != YZPlane3D(6))
		self.assertTrue(YZPlane3D(5) != XZPlane3D(5))
		self.assertTrue(YZPlane3D(5) != XYPlane3D(5))
		self.assertFalse(YZPlane3D(5) != YZPlane3D(5))

	def test_repr(self) -> None:
		self.assertEqual("YZPlane3D(5)", repr(YZPlane3D(5)))

	def test_str(self) -> None:
		self.assertEqual("x = -2.5", str(YZPlane3D(-2.5)))

	def test_FromElement_MinX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(YZPlane3D(1), YZPlane3D.FromElement(line, Alignment3D.MinX))

	def test_FromElement_CenterX(self) -> None:
		"""The coordinate of a center is a float, as the center of a bounding box."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		center = YZPlane3D.FromElement(line, Alignment3D.CenterX)

		self.assertEqual(YZPlane3D(2.5), center)
		self.assertIs(float, type(center.X))

	def test_FromElement_MaxX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(YZPlane3D(4), YZPlane3D.FromElement(line, Alignment3D.MaxX))

	def test_FromElement_Group(self) -> None:
		"""The plane runs through the absolute bounding box of an element inside a group."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		_ =    Group3D(Offset3D(10, 20, 30), (line, ))

		self.assertEqual(YZPlane3D(14), YZPlane3D.FromElement(line, Alignment3D.MaxX))

	def test_FromElement_AlignmentMinY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			YZPlane3D.FromElement(line, Alignment3D.MinY)

		self.assertEqual(
			"Parameter 'alignment' is not Alignment3D.MinX, Alignment3D.CenterX or Alignment3D.MaxX.",
			str(context.exception)
		)
		self.assertListEqual(
			[
				"Got value 'Alignment3D.MinY'.",
				"Use 'XZPlane3D.FromElement' or 'XYPlane3D.FromElement' for the other alignments."
			],
			context.exception.__notes__
		)

	def test_Immutable(self) -> None:
		plane = YZPlane3D(5)

		with self.assertRaises(AttributeError):
			plane.X = 6

		self.assertEqual(YZPlane3D(5), plane)

	def test_EqualLine(self) -> None:
		"""A 2D line isn't a 3D plane."""
		with self.assertRaises(TypeError) as context:
			_ = YZPlane3D(5) == VerticalLine2D(5)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.VerticalLine2D'.", "Supported types for second operand: Plane3D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = YZPlane3D(5) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Plane3D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		planes = {YZPlane3D(5), YZPlane3D(5.0), YZPlane3D(6)}

		self.assertEqual(2, len(planes))

	def test_FromElement_ElementNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			YZPlane3D.FromElement(None, Alignment3D.MinX)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_FromElement_ElementPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			YZPlane3D.FromElement(Point3D(1, 2, 3), Alignment3D.MinX)

		self.assertEqual("Parameter 'element' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_FromElement_AlignmentNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			YZPlane3D.FromElement(line, None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_FromElement_Alignment2D(self) -> None:
		"""A 2D alignment isn't a 3D alignment."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			YZPlane3D.FromElement(line, Alignment2D.MinX)

		self.assertEqual("Parameter 'alignment' is not of type 'Alignment3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)


class XZPlanes(Testcase):
	def test_XZPlane3D(self) -> None:
		plane = XZPlane3D(5)

		self.assertEqual(5, plane.Y)

	def test_XZPlane3D_Float(self) -> None:
		plane = XZPlane3D(-2.5)

		self.assertEqual(-2.5, plane.Y)

	def test_YNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			XZPlane3D(None)

		self.assertEqual("Parameter 'y' is None.", str(context.exception))

	def test_YStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			XZPlane3D("5")

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Equal(self) -> None:
		self.assertTrue(XZPlane3D(5) == XZPlane3D(5.0))
		self.assertFalse(XZPlane3D(5) == XZPlane3D(6))
		self.assertFalse(XZPlane3D(5) == YZPlane3D(5))
		self.assertFalse(XZPlane3D(5) == XYPlane3D(5))

	def test_Unequal(self) -> None:
		self.assertTrue(XZPlane3D(5) != XZPlane3D(6))
		self.assertTrue(XZPlane3D(5) != YZPlane3D(5))
		self.assertTrue(XZPlane3D(5) != XYPlane3D(5))
		self.assertFalse(XZPlane3D(5) != XZPlane3D(5))

	def test_repr(self) -> None:
		self.assertEqual("XZPlane3D(5)", repr(XZPlane3D(5)))

	def test_str(self) -> None:
		self.assertEqual("y = -2.5", str(XZPlane3D(-2.5)))

	def test_FromElement_MinY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(XZPlane3D(2), XZPlane3D.FromElement(line, Alignment3D.MinY))

	def test_FromElement_CenterY(self) -> None:
		"""The coordinate of a center is a float, as the center of a bounding box."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		center = XZPlane3D.FromElement(line, Alignment3D.CenterY)

		self.assertEqual(XZPlane3D(4), center)
		self.assertIs(float, type(center.Y))

	def test_FromElement_MaxY(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(XZPlane3D(6), XZPlane3D.FromElement(line, Alignment3D.MaxY))

	def test_FromElement_Group(self) -> None:
		"""The plane runs through the absolute bounding box of an element inside a group."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		_ =    Group3D(Offset3D(10, 20, 30), (line, ))

		self.assertEqual(XZPlane3D(26), XZPlane3D.FromElement(line, Alignment3D.MaxY))

	def test_FromElement_AlignmentMinZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			XZPlane3D.FromElement(line, Alignment3D.MinZ)

		self.assertEqual(
			"Parameter 'alignment' is not Alignment3D.MinY, Alignment3D.CenterY or Alignment3D.MaxY.",
			str(context.exception)
		)
		self.assertListEqual(
			[
				"Got value 'Alignment3D.MinZ'.",
				"Use 'YZPlane3D.FromElement' or 'XYPlane3D.FromElement' for the other alignments."
			],
			context.exception.__notes__
		)


class XYPlanes(Testcase):
	def test_XYPlane3D(self) -> None:
		plane = XYPlane3D(5)

		self.assertEqual(5, plane.Z)

	def test_XYPlane3D_Float(self) -> None:
		plane = XYPlane3D(-2.5)

		self.assertEqual(-2.5, plane.Z)

	def test_ZNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			XYPlane3D(None)

		self.assertEqual("Parameter 'z' is None.", str(context.exception))

	def test_ZStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			XYPlane3D("5")

		self.assertEqual("Parameter 'z' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Equal(self) -> None:
		self.assertTrue(XYPlane3D(5) == XYPlane3D(5.0))
		self.assertFalse(XYPlane3D(5) == XYPlane3D(6))
		self.assertFalse(XYPlane3D(5) == YZPlane3D(5))
		self.assertFalse(XYPlane3D(5) == XZPlane3D(5))

	def test_Unequal(self) -> None:
		self.assertTrue(XYPlane3D(5) != XYPlane3D(6))
		self.assertTrue(XYPlane3D(5) != YZPlane3D(5))
		self.assertTrue(XYPlane3D(5) != XZPlane3D(5))
		self.assertFalse(XYPlane3D(5) != XYPlane3D(5))

	def test_repr(self) -> None:
		self.assertEqual("XYPlane3D(5)", repr(XYPlane3D(5)))

	def test_str(self) -> None:
		self.assertEqual("z = -2.5", str(XYPlane3D(-2.5)))

	def test_FromElement_MinZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(XYPlane3D(3), XYPlane3D.FromElement(line, Alignment3D.MinZ))

	def test_FromElement_CenterZ(self) -> None:
		"""The coordinate of a center is a float, as the center of a bounding box."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		center = XYPlane3D.FromElement(line, Alignment3D.CenterZ)

		self.assertEqual(XYPlane3D(5.5), center)
		self.assertIs(float, type(center.Z))

	def test_FromElement_MaxZ(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertEqual(XYPlane3D(8), XYPlane3D.FromElement(line, Alignment3D.MaxZ))

	def test_FromElement_Group(self) -> None:
		"""The plane runs through the absolute bounding box of an element inside a group."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		_ =    Group3D(Offset3D(10, 20, 30), (line, ))

		self.assertEqual(XYPlane3D(38), XYPlane3D.FromElement(line, Alignment3D.MaxZ))

	def test_FromElement_AlignmentMinX(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			XYPlane3D.FromElement(line, Alignment3D.MinX)

		self.assertEqual(
			"Parameter 'alignment' is not Alignment3D.MinZ, Alignment3D.CenterZ or Alignment3D.MaxZ.",
			str(context.exception)
		)
		self.assertListEqual(
			[
				"Got value 'Alignment3D.MinX'.",
				"Use 'YZPlane3D.FromElement' or 'XZPlane3D.FromElement' for the other alignments."
			],
			context.exception.__notes__
		)


class Rays(Testcase):
	def test_Ray3D(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		self.assertTupleEqual((1, 2, 3), ray.Start.ToTuple())
		self.assertTupleEqual((0, 3, 4), ray.Direction.ToTuple())

	def test_Copies(self) -> None:
		"""The ray copies the given point and offset; its properties return new copies."""
		start =     Point3D(1, 2, 3)
		direction = Offset3D(0, 3, 4)
		ray =       Ray3D(start, direction)

		start += Offset3D(0, 3, 4)
		direction.XOffset = 7

		self.assertTupleEqual((1, 2, 3), ray.Start.ToTuple())
		self.assertTupleEqual((0, 3, 4), ray.Direction.ToTuple())
		self.assertIsNone(ray.Start.Parent)
		self.assertIsNot(ray.Start, ray.Start)
		self.assertIsNot(ray.Direction, ray.Direction)

		returned =   ray.Start
		returned.X = 9

		self.assertEqual(1, ray.Start.X)

	def test_StartInGroup(self) -> None:
		"""A start point inside a group is taken in absolute coordinates."""
		group = Group3D(Offset3D(10, 20, 30))
		start = Point3D(1, 2, 3, parent=group)

		ray = Ray3D(start, Offset3D(0, 3, 4))

		self.assertTupleEqual((11, 22, 33), ray.Start.ToTuple())
		self.assertIs(group, start.Parent)

	def test_StartNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray3D(None, Offset3D(0, 3, 4))

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_StartOffset(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray3D(Offset3D(1, 2, 3), Offset3D(0, 3, 4))

		self.assertEqual("Parameter 'start' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Offset3D'."], context.exception.__notes__)

	def test_Start2D(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray3D(Point2D(1, 2), Offset3D(0, 3, 4))

		self.assertEqual("Parameter 'start' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_DirectionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray3D(Point3D(1, 2, 3), None)

		self.assertEqual("Parameter 'direction' is None.", str(context.exception))

	def test_Direction2D(self) -> None:
		with self.assertRaises(TypeError) as context:
			Ray3D(Point3D(1, 2, 3), Offset2D(3, 4))

		self.assertEqual("Parameter 'direction' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Offset2D'."], context.exception.__notes__)

	def test_DirectionZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			Ray3D(Point3D(1, 2, 3), Offset3D(0, 0, 0))

		self.assertEqual("Parameter 'direction' is a zero offset.", str(context.exception))
		self.assertListEqual(["Got offset (0, 0, 0).", "A ray needs a direction."], context.exception.__notes__)

	def test_Immutable(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		with self.assertRaises(AttributeError):
			ray.Start = Point3D(0, 0, 0)

		with self.assertRaises(AttributeError):
			ray.Direction = Offset3D(0, 6, 8)

		self.assertEqual(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)), ray)

	def test_PointAt(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		point = ray.PointAt(5)

		self.assertTupleEqual((1.0, 5.0, 7.0), point.ToTuple())
		self.assertIsNone(point.Parent)

	def test_PointAt_Zero(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		self.assertTupleEqual((1, 2, 3), ray.PointAt(0).ToTuple())

	def test_PointAt_DirectionLength(self) -> None:
		"""The distance doesn't depend on the length of the direction."""
		ray1 = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))
		ray2 = Ray3D(Point3D(1, 2, 3), Offset3D(0, 6, 8))

		self.assertTupleEqual(ray1.PointAt(10).ToTuple(), ray2.PointAt(10).ToTuple())

	def test_PointAt_DistanceNone(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		with self.assertRaises(ValueError) as context:
			ray.PointAt(None)

		self.assertEqual("Parameter 'distance' is None.", str(context.exception))

	def test_PointAt_DistanceStr(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		with self.assertRaises(TypeError) as context:
			ray.PointAt("5")

		self.assertEqual("Parameter 'distance' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_PointAt_DistanceNegative(self) -> None:
		ray = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))

		with self.assertRaises(ValueError) as context:
			ray.PointAt(-1)

		self.assertEqual("Parameter 'distance' is negative.", str(context.exception))
		self.assertListEqual(
			["Got value '-1'.", "A point before the start point isn't on the ray."],
			context.exception.__notes__
		)

	def test_Equal(self) -> None:
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)))
		self.assertFalse(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(0, 3, 4), Offset3D(0, 3, 4)))

	def test_Equal_Scaled(self) -> None:
		"""Directions pointing the same way are equal, whatever their lengths."""
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(1, 2, 3), Offset3D(0, 6, 8)))
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(1, 2, 3), Offset3D(0, 1.5, 2.0)))

	def test_Equal_Opposite(self) -> None:
		self.assertFalse(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(1, 2, 3), Offset3D(0, -3, -4)))

	def test_Equal_OtherDirection(self) -> None:
		self.assertFalse(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 5)))

	def test_Unequal(self) -> None:
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != Ray3D(Point3D(0, 3, 4), Offset3D(0, 3, 4)))
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != Ray3D(Point3D(1, 2, 3), Offset3D(0, -3, -4)))
		self.assertTrue(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 5)))
		self.assertFalse(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)))
		self.assertFalse(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != Ray3D(Point3D(1, 2, 3), Offset3D(0, 6, 8)))

	def test_EqualTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) == ((1, 2, 3), (0, 3, 4))

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'tuple'.", "Supported types for second operand: Ray3D"],
			context.exception.__notes__
		)

	def test_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Ray3D"],
			context.exception.__notes__
		)

	def test_Hash(self) -> None:
		"""Equal rays hash alike; a ray in the opposite direction is another element of a set."""
		rays = {
			Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4)),
			Ray3D(Point3D(1, 2, 3), Offset3D(0, 6, 8)),
			Ray3D(Point3D(1, 2, 3), Offset3D(0, -3, -4))
		}

		self.assertEqual(2, len(rays))
		self.assertEqual(hash(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))), hash(Ray3D(Point3D(1, 2, 3), Offset3D(0, 6, 8))))

	def test_repr(self) -> None:
		self.assertEqual("Ray3D((1, 2, 3), (0, 3, 4))", repr(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))))

	def test_str(self) -> None:
		self.assertEqual("(1, 2, 3) + t * (0, 3, 4), t >= 0", str(Ray3D(Point3D(1, 2, 3), Offset3D(0, 3, 4))))


class MirroringAtPlane(Testcase):
	def test_X(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorAt(YZPlane3D(10))

		self.assertTupleEqual(((19, 2, 3), (16, 6, 8)), line.ToTuple())

	def test_Y(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorAt(XZPlane3D(0))

		self.assertTupleEqual(((1, -2, 3), (4, -6, 8)), line.ToTuple())

	def test_Z(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorAt(XYPlane3D(5))

		self.assertTupleEqual(((1, 2, 7), (4, 6, 2)), line.ToTuple())

	def test_Float(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorAt(XYPlane3D(0.5))

		self.assertTupleEqual(((1, 2, -2.0), (4, 6, -7.0)), line.ToTuple())

	def test_Int(self) -> None:
		"""A plane at an integer coordinate keeps integer coordinates."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line.MirrorAt(YZPlane3D(3))

		self.assertTupleEqual(((5, 2, 3), (2, 6, 8)), line.ToTuple())
		self.assertIs(int, type(line.Start.X))
		self.assertIs(int, type(line.End.X))

	def test_Twice(self) -> None:
		line =   LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		mirror = XZPlane3D(-3)

		line.MirrorAt(mirror)
		line.MirrorAt(mirror)

		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_MirrorZ(self) -> None:
		"""Mirroring at the plane through a face of the element equals mirroring at that face."""
		line1 = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		line2 = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		line1.MirrorAt(XYPlane3D.FromElement(line1, Alignment3D.MinZ))
		line2.MirrorZ(Alignment3D.MinZ)

		self.assertTupleEqual(line2.ToTuple(), line1.ToTuple())

	def test_PlaneNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MirrorAt(None)

		self.assertEqual("Parameter 'plane' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())

	def test_PlaneLine(self) -> None:
		"""A 2D line isn't a 3D plane."""
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MirrorAt(VerticalLine2D(5))

		self.assertEqual("Parameter 'plane' is not of type 'Plane3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.VerticalLine2D'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 6, 8)), line.ToTuple())


class ElementData(Testcase):
	def test_Segment(self) -> None:
		value =   object()
		pairs =   {"layer": 1}
		segment = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=value, keyValuePairs=pairs)

		self.assertIs(value, segment.Value)
		self.assertEqual(1, segment["layer"])
		self.assertIsNot(pairs, segment._dict)

	def test_Segment_Default(self) -> None:
		segment = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		self.assertIsNone(segment.Value)
		self.assertEqual(0, len(segment))

	def test_Segment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment(self) -> None:
		value = object()
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=value, keyValuePairs={"layer": 1})

		self.assertIs(value, line.Value)
		self.assertEqual(1, line["layer"])

	def test_LineSegment_Value(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=1)

		line.Value = "wire"

		self.assertEqual("wire", line.Value)

	def test_LineSegment_Pairs(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

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

	def test_LineSegment_Copy(self) -> None:
		value = [1, 2]
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=value, keyValuePairs={"layer": 1, "nets": ["a"]})

		newLine =          line.Copy()
		newLine["layer"] = 2

		self.assertIs(value, newLine.Value)
		self.assertEqual(1, line["layer"])
		self.assertEqual(2, newLine["layer"])
		self.assertIs(line["nets"], newLine["nets"])

	def test_LineSegment_copy(self) -> None:
		value = [1, 2]
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=value, keyValuePairs={"layer": 1})

		newLine = copy(line)

		self.assertIs(value, newLine.Value)
		self.assertEqual(1, newLine["layer"])
		self.assertIsNot(line._dict, newLine._dict)

	def test_LineSegment_deepcopy(self) -> None:
		"""A deep copy copies the value and the values of the key-value-pairs too."""
		value = [1, 2]
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), value=value, keyValuePairs={"nets": ["a"]})

		newLine = deepcopy(line)

		self.assertIsNot(value, newLine.Value)
		self.assertListEqual([1, 2], newLine.Value)
		self.assertIsNot(line["nets"], newLine["nets"])
		self.assertListEqual(["a"], newLine["nets"])
