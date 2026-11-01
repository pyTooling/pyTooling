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
from copy                  import copy, deepcopy
from math                  import pi, sqrt

from pyTooling.Cartesian3D import Origin3D, Point3D, Offset3D, Size3D, LineSegment3D
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Origin(self) -> None:
		origin = Origin3D()

		self.assertIsInstance(origin.x, int)
		self.assertIsInstance(origin.y, int)
		self.assertIsInstance(origin.z, int)
		self.assertEqual(0, origin.x)
		self.assertEqual(0, origin.y)
		self.assertEqual(0, origin.z)
		self.assertTupleEqual((0, 0, 0), origin.ToTuple())
		self.assertEqual("Origin3D(0, 0, 0)", repr(origin))

	def test_Point_int(self) -> None:
		point = Point3D(1, 2, 3)

		self.assertIsInstance(point.x, int)
		self.assertIsInstance(point.y, int)
		self.assertIsInstance(point.z, int)
		self.assertEqual(1, point.x)
		self.assertEqual(2, point.y)
		self.assertEqual(3, point.z)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())
		self.assertEqual("Point3D(1, 2, 3)", repr(point))

	def test_Point_float(self) -> None:
		point = Point3D(1.0, 2.0, 3.0)

		self.assertIsInstance(point.x, float)
		self.assertIsInstance(point.y, float)
		self.assertIsInstance(point.z, float)
		self.assertEqual(1.0, point.x)
		self.assertEqual(2.0, point.y)
		self.assertEqual(3.0, point.z)
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

		self.assertIsInstance(offset.xOffset, int)
		self.assertIsInstance(offset.yOffset, int)
		self.assertIsInstance(offset.zOffset, int)
		self.assertEqual(1, offset.xOffset)
		self.assertEqual(2, offset.yOffset)
		self.assertEqual(3, offset.zOffset)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())
		self.assertEqual("Offset3D(1, 2, 3)", repr(offset))

	def test_Offset_float(self) -> None:
		offset = Offset3D(1.0, 2.0, 3.0)

		self.assertIsInstance(offset.xOffset, float)
		self.assertIsInstance(offset.yOffset, float)
		self.assertIsInstance(offset.zOffset, float)
		self.assertEqual(1.0, offset.xOffset)
		self.assertEqual(2.0, offset.yOffset)
		self.assertEqual(3.0, offset.zOffset)
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

		self.assertIsInstance(size.width, int)
		self.assertIsInstance(size.height, int)
		self.assertIsInstance(size.depth, int)
		self.assertEqual(1, size.width)
		self.assertEqual(2, size.height)
		self.assertEqual(3, size.depth)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())
		self.assertEqual("Size3D(1, 2, 3)", repr(size))

	def test_Size_float(self) -> None:
		size = Size3D(1.0, 2.0, 3.0)

		self.assertIsInstance(size.width, float)
		self.assertIsInstance(size.height, float)
		self.assertIsInstance(size.depth, float)
		self.assertEqual(1.0, size.width)
		self.assertEqual(2.0, size.height)
		self.assertEqual(3.0, size.depth)
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


class Properties(Testcase):
	def test_Point_x(self) -> None:
		point = Point3D(1, 2, 3)

		point.x = 3.5

		self.assertEqual(3.5, point.x)
		self.assertTupleEqual((3.5, 2, 3), point.ToTuple())

	def test_Point_x_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.x = None

		self.assertEqual("Parameter 'x' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_x_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.x = "3.5"

		self.assertEqual("Parameter 'x' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_y(self) -> None:
		point = Point3D(1, 2, 3)

		point.y = 3.5

		self.assertEqual(3.5, point.y)
		self.assertTupleEqual((1, 3.5, 3), point.ToTuple())

	def test_Point_y_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.y = None

		self.assertEqual("Parameter 'y' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_y_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.y = "3.5"

		self.assertEqual("Parameter 'y' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_z(self) -> None:
		point = Point3D(1, 2, 3)

		point.z = 3.5

		self.assertEqual(3.5, point.z)
		self.assertTupleEqual((1, 2, 3.5), point.ToTuple())

	def test_Point_z_None(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			point.z = None

		self.assertEqual("Parameter 'z' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Point_z_str(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			point.z = "3.5"

		self.assertEqual("Parameter 'z' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), point.ToTuple())

	def test_Offset_xOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.xOffset = 3.5

		self.assertEqual(3.5, offset.xOffset)
		self.assertTupleEqual((3.5, 2, 3), offset.ToTuple())

	def test_Offset_xOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.xOffset = None

		self.assertEqual("Parameter 'xOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_xOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.xOffset = "3.5"

		self.assertEqual("Parameter 'xOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_yOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.yOffset = 3.5

		self.assertEqual(3.5, offset.yOffset)
		self.assertTupleEqual((1, 3.5, 3), offset.ToTuple())

	def test_Offset_yOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.yOffset = None

		self.assertEqual("Parameter 'yOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_yOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.yOffset = "3.5"

		self.assertEqual("Parameter 'yOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_zOffset(self) -> None:
		offset = Offset3D(1, 2, 3)

		offset.zOffset = 3.5

		self.assertEqual(3.5, offset.zOffset)
		self.assertTupleEqual((1, 2, 3.5), offset.ToTuple())

	def test_Offset_zOffset_None(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			offset.zOffset = None

		self.assertEqual("Parameter 'zOffset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Offset_zOffset_str(self) -> None:
		offset = Offset3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			offset.zOffset = "3.5"

		self.assertEqual("Parameter 'zOffset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), offset.ToTuple())

	def test_Size_width(self) -> None:
		size = Size3D(1, 2, 3)

		size.width = 3.5

		self.assertEqual(3.5, size.width)
		self.assertTupleEqual((3.5, 2, 3), size.ToTuple())

	def test_Size_width_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.width = None

		self.assertEqual("Parameter 'width' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_width_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.width = "3.5"

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_height(self) -> None:
		size = Size3D(1, 2, 3)

		size.height = 3.5

		self.assertEqual(3.5, size.height)
		self.assertTupleEqual((1, 3.5, 3), size.ToTuple())

	def test_Size_height_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.height = None

		self.assertEqual("Parameter 'height' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_height_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.height = "3.5"

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_depth(self) -> None:
		size = Size3D(1, 2, 3)

		size.depth = 3.5

		self.assertEqual(3.5, size.depth)
		self.assertTupleEqual((1, 2, 3.5), size.ToTuple())

	def test_Size_depth_None(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(ValueError) as context:
			size.depth = None

		self.assertEqual("Parameter 'depth' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_Size_depth_str(self) -> None:
		size = Size3D(1, 2, 3)

		with self.assertRaises(TypeError) as context:
			size.depth = "3.5"

		self.assertEqual("Parameter 'depth' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), size.ToTuple())

	def test_LineSegment_start(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))
		point = Point3D(7, 8, 9)

		line.start = point

		self.assertIs(point, line.start)
		self.assertTupleEqual(((7, 8, 9), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_start_None(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(ValueError) as context:
			line.start = None

		self.assertEqual("Parameter 'start' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_start_tuple(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(TypeError) as context:
			line.start = (7, 8, 9)

		self.assertEqual("Parameter 'start' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_end(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))
		point = Point3D(7, 8, 9)

		line.end = point

		self.assertIs(point, line.end)
		self.assertTupleEqual(((1, 2, 3), (7, 8, 9)), line.ToTuple())

	def test_LineSegment_end_None(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(ValueError) as context:
			line.end = None

		self.assertEqual("Parameter 'end' is None.", str(context.exception))
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())

	def test_LineSegment_end_tuple(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 5, 6))

		with self.assertRaises(TypeError) as context:
			line.end = (7, 8, 9)

		self.assertEqual("Parameter 'end' is not of type 'Point3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 2, 3), (4, 5, 6)), line.ToTuple())


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

		with self.assertRaises(RuntimeError):
			_ = origin.Copy()

	def test_Point_int(self) -> None:
		point = Point3D(1, 2, 3)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.x, int)
		self.assertIsInstance(newPoint.y, int)
		self.assertIsInstance(newPoint.z, int)
		self.assertEqual(1, newPoint.x)
		self.assertEqual(2, newPoint.y)
		self.assertEqual(3, newPoint.z)
		self.assertTupleEqual((1, 2, 3), newPoint.ToTuple())
		self.assertEqual("Point3D(1, 2, 3)", repr(newPoint))

	def test_Point_float(self) -> None:
		point = Point3D(1.0, 2.0, 3.0)

		newPoint = point.Copy()

		self.assertIsInstance(newPoint.x, float)
		self.assertIsInstance(newPoint.y, float)
		self.assertIsInstance(newPoint.z, float)
		self.assertEqual(1.0, newPoint.x)
		self.assertEqual(2.0, newPoint.y)
		self.assertEqual(3.0, newPoint.z)
		self.assertTupleEqual((1.0, 2.0, 3.0), newPoint.ToTuple())
		self.assertEqual("Point3D(1.0, 2.0, 3.0)", repr(newPoint))

	def test_Offset_int(self) -> None:
		offset = Offset3D(1, 2, 3)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.xOffset, int)
		self.assertIsInstance(newOffset.yOffset, int)
		self.assertIsInstance(newOffset.zOffset, int)
		self.assertEqual(1, newOffset.xOffset)
		self.assertEqual(2, newOffset.yOffset)
		self.assertEqual(3, newOffset.zOffset)
		self.assertTupleEqual((1, 2, 3), newOffset.ToTuple())
		self.assertEqual("Offset3D(1, 2, 3)", repr(newOffset))

	def test_Offset_float(self) -> None:
		offset = Offset3D(1.0, 2.0, 3.0)

		newOffset = offset.Copy()

		self.assertIsInstance(newOffset.xOffset, float)
		self.assertIsInstance(newOffset.yOffset, float)
		self.assertIsInstance(newOffset.zOffset, float)
		self.assertEqual(1.0, newOffset.xOffset)
		self.assertEqual(2.0, newOffset.yOffset)
		self.assertEqual(3.0, newOffset.zOffset)
		self.assertTupleEqual((1.0, 2.0, 3.0), newOffset.ToTuple())
		self.assertEqual("Offset3D(1.0, 2.0, 3.0)", repr(newOffset))

	def test_Size_int(self) -> None:
		size = Size3D(1, 2, 3)

		newSize = size.Copy()

		self.assertIsInstance(newSize.width, int)
		self.assertIsInstance(newSize.height, int)
		self.assertIsInstance(newSize.depth, int)
		self.assertEqual(1, newSize.width)
		self.assertEqual(2, newSize.height)
		self.assertEqual(3, newSize.depth)
		self.assertTupleEqual((1, 2, 3), newSize.ToTuple())
		self.assertEqual("Size3D(1, 2, 3)", repr(newSize))

	def test_Size_float(self) -> None:
		size = Size3D(1.0, 2.0, 3.0)

		newSize = size.Copy()

		self.assertIsInstance(newSize.width, float)
		self.assertIsInstance(newSize.height, float)
		self.assertIsInstance(newSize.depth, float)
		self.assertEqual(1.0, newSize.width)
		self.assertEqual(2.0, newSize.height)
		self.assertEqual(3.0, newSize.depth)
		self.assertTupleEqual((1.0, 2.0, 3.0), newSize.ToTuple())
		self.assertEqual("Size3D(1.0, 2.0, 3.0)", repr(newSize))

	def test_Origin_copy(self) -> None:
		origin = Origin3D()

		with self.assertRaises(RuntimeError):
			_ = copy(origin)

	def test_Origin_deepcopy(self) -> None:
		origin = Origin3D()

		with self.assertRaises(RuntimeError):
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
		newLine.start += (5, 5, 5)
		newLine.end +=   (5, 5, 5)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line, newLine)
		self.assertIsNot(line.start, newLine.start)
		self.assertIsNot(line.end, newLine.end)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), line.ToTuple())
		self.assertTupleEqual(((6, 7, 8), (7, 8, 9)), newLine.ToTuple())

	def test_LineSegment_copy(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))

		newLine = copy(line)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line.start, newLine.start)
		self.assertIsNot(line.end, newLine.end)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), newLine.ToTuple())

	def test_LineSegment_deepcopy(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))

		newLine = deepcopy(line)

		self.assertIs(LineSegment3D, type(newLine))
		self.assertIsNot(line.start, newLine.start)
		self.assertIsNot(line.end, newLine.end)
		self.assertTupleEqual(((1, 2, 3), (2, 3, 4)), newLine.ToTuple())

	def test_LineSegment_Origin(self) -> None:
		line = LineSegment3D(Origin3D(), Point3D(2, 3, 4), copyPoints=False)

		with self.assertRaises(RuntimeError):
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

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)
		self.assertEqual(7, newPoint.z)

	def test_Point_Plus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		newPoint = point + offset

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)
		self.assertEqual(7, newPoint.z)

	def test_Point_InplacePlus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)
		self.assertEqual(7, point.z)

	def test_Point_InplacePlus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)
		self.assertEqual(7, point.z)

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

		self.assertEqual(-1, newPoint.x)
		self.assertEqual(-1, newPoint.y)
		self.assertEqual(-1, newPoint.z)

	def test_Point_Minus_Point(self) -> None:
		point1 = Point3D(1, 2, 3)
		point2 = Point3D(2, 3, 4)

		offset = point2 - point1

		self.assertEqual(1, offset.xOffset)
		self.assertEqual(1, offset.yOffset)
		self.assertEqual(1, offset.zOffset)

	def test_Point_Minus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)

		with self.assertRaises(TypeError):
			_ = point - 2

	def test_Point_InplaceMinus_Offset(self) -> None:
		point = Point3D(1, 2, 3)
		offset = Offset3D(2, 3, 4)

		point -= offset

		self.assertEqual(-1, point.x)
		self.assertEqual(-1, point.y)
		self.assertEqual(-1, point.z)

	def test_Point_InplaceMinus_Tuple(self) -> None:
		point = Point3D(1, 2, 3)
		offset = (2, 3, 4)

		point -= offset

		self.assertEqual(-1, point.x)
		self.assertEqual(-1, point.y)
		self.assertEqual(-1, point.z)

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

		self.assertEqual(3, newOffset.xOffset)
		self.assertEqual(5, newOffset.yOffset)
		self.assertEqual(7, newOffset.zOffset)

	def test_Offset_Plus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		newOffset = offset1 + offset2

		self.assertEqual(3, newOffset.xOffset)
		self.assertEqual(5, newOffset.yOffset)
		self.assertEqual(7, newOffset.zOffset)

	def test_Offset_Plus_int(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 + offset2

	def test_Offset_InplacePlus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		offset1 += offset2

		self.assertEqual(3, offset1.xOffset)
		self.assertEqual(5, offset1.yOffset)
		self.assertEqual(7, offset1.zOffset)

	def test_Offset_InplacePlus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		offset1 += offset2

		self.assertEqual(3, offset1.xOffset)
		self.assertEqual(5, offset1.yOffset)
		self.assertEqual(7, offset1.zOffset)

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

		self.assertEqual(-1, newOffset.xOffset)
		self.assertEqual(-1, newOffset.yOffset)
		self.assertEqual(-1, newOffset.zOffset)

	def test_Offset_Minus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		newOffset = offset1 - offset2

		self.assertEqual(-1, newOffset.xOffset)
		self.assertEqual(-1, newOffset.yOffset)
		self.assertEqual(-1, newOffset.zOffset)

	def test_Offset_Minus_int(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = 2

		with self.assertRaises(TypeError):
			_ = offset1 - offset2

	def test_Offset_InplaceMinus_Offset(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = Offset3D(2, 3, 4)

		offset1 -= offset2

		self.assertEqual(-1, offset1.xOffset)
		self.assertEqual(-1, offset1.yOffset)
		self.assertEqual(-1, offset1.zOffset)

	def test_Offset_InplaceMinus_Tuple(self) -> None:
		offset1 = Offset3D(1, 2, 3)
		offset2 = (2, 3, 4)

		offset1 -= offset2

		self.assertEqual(-1, offset1.xOffset)
		self.assertEqual(-1, offset1.yOffset)
		self.assertEqual(-1, offset1.zOffset)

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
