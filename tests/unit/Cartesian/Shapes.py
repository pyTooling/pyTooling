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
Unit tests for :mod:`pyTooling.Cartesian2D.Shapes` - polygon, trapezium, rectangle, square and circle.
"""
from math                         import cos, isclose, pi, radians, sin, sqrt

from pyTooling.Cartesian2D        import Point2D, LineSegment2D
from pyTooling.Cartesian2D.Shapes import Shape, Polygon, Trapezium, Rectangle, Square, Circle
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Polygon(self) -> None:
		point0 = Point2D(0, 0)
		point1 = Point2D(4, 0)
		point2 = Point2D(2, 3)

		polygon = Polygon((point0, point1, point2))

		self.assertIsInstance(polygon, Shape)
		self.assertEqual(3, len(polygon.Points))
		self.assertEqual(3, len(polygon.Segments))

	def test_Polygon_Pentagon(self) -> None:
		points = [Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5), Point2D(-1, 3)]

		polygon = Polygon(points)

		self.assertEqual(5, len(polygon.Points))
		self.assertEqual(5, len(polygon.Segments))

	def test_Polygon_Generator(self) -> None:
		"""The corners are consumed from any iterable, also from a generator."""
		polygon = Polygon(Point2D(x, y) for x, y in ((0, 0), (4, 0), (2, 3)))

		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Polygon_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Polygon(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_Polygon_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon(3)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Polygon_NoneElement(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Polygon((Point2D(0, 0), None, Point2D(2, 3)))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_Polygon_strElement(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), "4, 0", Point2D(2, 3)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Polygon_TwoPoints(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0)))

		self.assertEqual("Parameter 'points' has fewer than 3 points.", str(context.exception))
		self.assertListEqual(["Got 2 points."], context.exception.__notes__)

	def test_Polygon_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_Polygon_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		self.assertIsInstance(trapezium, Shape)
		self.assertEqual(4, len(trapezium.points))
		self.assertEqual(4, len(trapezium.segments))

	def test_Trapezium_str1(self) -> None:
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium("1, 1", point01, point11, point10)

		self.assertEqual("Parameter 'p00' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str2(self) -> None:
		point00 = Point2D(1, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, "3, 1", point11, point10)

		self.assertEqual("Parameter 'p01' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str3(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, "3, 3", point10)

		self.assertEqual("Parameter 'p11' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str4(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, point11, "1, 3")

		self.assertEqual("Parameter 'p10' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Rectangle(self) -> None:
		"""A rectangle rotated against the axes: edges 4/2 and -1/2 are perpendicular."""
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 2)
		point11 = Point2D(3, 4)
		point10 = Point2D(-1, 2)

		rectangle = Rectangle(point00, point01, point11, point10)

		self.assertIsInstance(rectangle, Trapezium)
		self.assertTupleEqual(
			((0, 0), (4, 2), (3, 4), (-1, 2)),
			tuple(point.ToTuple() for point in rectangle.points)
		)

	def test_Rectangle_AxisAligned(self) -> None:
		"""Two edges are parallel to the y-axis."""
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 0)
		point11 = Point2D(4, 2)
		point10 = Point2D(0, 2)

		rectangle = Rectangle(point00, point01, point11, point10)

		self.assertEqual(4, len(rectangle.segments))
		self.assertTupleEqual((4.0, 2.0, 4.0, 2.0), tuple(segment.Length for segment in rectangle.segments))

	def test_Rectangle_OppositeEdges(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 0)
		point11 = Point2D(5, 3)
		point10 = Point2D(0, 3)

		with self.assertRaises(ValueError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Opposite line segments (edges) have different lengths.", str(context.exception))
		self.assertListEqual(["Got lengths 4.0 and 5.0."], context.exception.__notes__)

	def test_Rectangle_Float(self) -> None:
		"""A rectangle rotated by 3 degrees: the lengths of opposite edges differ in the last digit."""
		angle = radians(3)
		point00 = Point2D(0.0, 0.0)
		point01 = Point2D(4 * cos(angle), 4 * sin(angle))
		point11 = Point2D(4 * cos(angle) - 2 * sin(angle), 4 * sin(angle) + 2 * cos(angle))
		point10 = Point2D(-2 * sin(angle), 2 * cos(angle))

		rectangle = Rectangle(point00, point01, point11, point10)

		self.assertEqual(4, len(rectangle.segments))
		for segment, length in zip(rectangle.segments, (4.0, 2.0, 4.0, 2.0)):
			self.assertTrue(isclose(length, segment.Length))

	def test_Rectangle_Parallelogram(self) -> None:
		"""Opposite edges are parallel and equally long, but no angle is 90 degrees."""
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 0)
		point11 = Point2D(5, 2)
		point10 = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Inner angle of a rectangle is not 90°.", str(context.exception))
		self.assertListEqual(["Got 116.57° at corner (4, 0)."], context.exception.__notes__)

	def test_Rectangle_Crossed(self) -> None:
		"""Opposite edges are equally long and two opposite angles are 90 degrees, but the edges cross each other."""
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 0)
		point11 = Point2D(4, 3)
		point10 = Point2D(2.88, -0.84)

		with self.assertRaises(ValueError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Inner angle of a rectangle is not 90°.", str(context.exception))
		self.assertListEqual(["Got 16.26° at corner (4, 3)."], context.exception.__notes__)

	def test_Rectangle_SameCorners(self) -> None:
		"""Two pairs of consecutive corners are the same point: opposite edges are equally long, both 0."""
		point00 = Point2D(0, 0)
		point01 = Point2D(0, 0)
		point11 = Point2D(4, 2)
		point10 = Point2D(4, 2)

		with self.assertRaises(ValueError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Line segment (edge) has length 0.", str(context.exception))
		self.assertListEqual(["Got corners (0, 0) and (0, 0)."], context.exception.__notes__)

	def test_Rectangle_str(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 2)
		point11 = Point2D(3, 4)

		with self.assertRaises(TypeError) as context:
			_ = Rectangle(point00, point01, point11, "-1, 2")

		self.assertEqual("Parameter 'p10' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Square(self) -> None:
		"""A square rotated by 45 degrees: all edges are sqrt(2) long."""
		point00 = Point2D(0, 0)
		point01 = Point2D(1, 1)
		point11 = Point2D(0, 2)
		point10 = Point2D(-1, 1)

		square = Square(point00, point01, point11, point10)

		self.assertIsInstance(square, Rectangle)
		self.assertTupleEqual(
			((0, 0), (1, 1), (0, 2), (-1, 1)),
			tuple(point.ToTuple() for point in square.points)
		)

	def test_Square_AxisAligned(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		square = Square(point00, point01, point11, point10)

		self.assertEqual(4, len(square.segments))
		self.assertTupleEqual((2.0, 2.0, 2.0, 2.0), tuple(segment.Length for segment in square.segments))

	def test_Square_Rotated(self) -> None:
		"""A square rotated against the axes: all edges are sqrt(5) long, their x-differences are 2 and 1."""
		point00 = Point2D(0, 0)
		point01 = Point2D(2, 1)
		point11 = Point2D(1, 3)
		point10 = Point2D(-1, 2)

		square = Square(point00, point01, point11, point10)

		self.assertEqual(4, len(square.segments))
		for segment in square.segments:
			self.assertTrue(isclose(sqrt(5), segment.Length))

	def test_Square_Rectangle(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 2)
		point11 = Point2D(3, 4)
		point10 = Point2D(-1, 2)

		with self.assertRaises(ValueError) as context:
			_ = Square(point00, point01, point11, point10)

		self.assertEqual("Line segments (edges) between corners have different lengths.", str(context.exception))
		self.assertListEqual([f"Got lengths {sqrt(20)} and {sqrt(5)}."], context.exception.__notes__)

	def test_Square_Rhombus(self) -> None:
		"""All edges are sqrt(5) long, but no angle is 90 degrees."""
		point00 = Point2D(0, 0)
		point01 = Point2D(2, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			_ = Square(point00, point01, point11, point10)

		self.assertEqual("Inner angle of a rectangle is not 90°.", str(context.exception))
		self.assertListEqual(["Got 143.13° at corner (2, 1)."], context.exception.__notes__)

	def test_Square_str(self) -> None:
		point01 = Point2D(1, 1)
		point11 = Point2D(0, 2)
		point10 = Point2D(-1, 1)

		with self.assertRaises(TypeError) as context:
			_ = Square("0, 0", point01, point11, point10)

		self.assertEqual("Parameter 'p00' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Circle_int(self) -> None:
		center = Point2D(1, 2)

		circle = Circle(center, 3)

		self.assertIsInstance(circle, Shape)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())
		self.assertEqual(3, circle.Radius)

	def test_Circle_float(self) -> None:
		center = Point2D(1.5, 2.5)

		circle = Circle(center, 0.5)

		self.assertTupleEqual((1.5, 2.5), circle.Center.ToTuple())
		self.assertEqual(0.5, circle.Radius)

	def test_Circle_CenterNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle(None, 3)

		self.assertEqual("Parameter 'center' is None.", str(context.exception))

	def test_Circle_CenterStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle("1, 2", 3)

		self.assertEqual("Parameter 'center' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Circle_RadiusNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle(Point2D(1, 2), None)

		self.assertEqual("Parameter 'radius' is None.", str(context.exception))

	def test_Circle_RadiusStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), "3")

		self.assertEqual("Parameter 'radius' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Circle_RadiusZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle(Point2D(1, 2), 0)

		self.assertEqual("Parameter 'radius' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)

	def test_Circle_RadiusNegative(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle(Point2D(1, 2), -1.5)

		self.assertEqual("Parameter 'radius' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '-1.5'."], context.exception.__notes__)

	def test_Circle_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle(Point2D(1, 2), 3, copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_Circle_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), 3, copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class Corners(Testcase):
	def test_Polygon(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5), Point2D(-1, 3))

		polygon = Polygon(points)

		for point in polygon.Points:
			self.assertIsInstance(point, Point2D)

		self.assertTupleEqual(
			((0, 0), (4, 0), (5, 3), (2, 5), (-1, 3)),
			tuple(point.ToTuple() for point in polygon.Points)
		)

	def test_Polygon_Copy(self) -> None:
		"""The corners are copies: moving a given point afterwards doesn't change the shape."""
		point0 = Point2D(0, 0)
		point1 = Point2D(4, 0)
		point2 = Point2D(2, 3)

		polygon = Polygon((point0, point1, point2))
		point0 += (5, 5)

		for given, corner in zip((point0, point1, point2), polygon.Points):
			self.assertIsNot(given, corner)

		self.assertTupleEqual((5, 5), point0.ToTuple())
		self.assertTupleEqual((0, 0), polygon.Points[0].ToTuple())

	def test_Polygon_Reference(self) -> None:
		"""With ``copyPoints=False``, the corners are the given points."""
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polygon = Polygon(points, copyPoints=False)

		for given, corner in zip(points, polygon.Points):
			self.assertIs(given, corner)

	def test_Circle_Copy(self) -> None:
		"""The center is a copy: moving the given point afterwards doesn't change the circle."""
		center = Point2D(1, 2)

		circle = Circle(center, 3)
		center += (5, 5)

		self.assertIsNot(center, circle.Center)
		self.assertTupleEqual((6, 7), center.ToTuple())
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Circle_Reference(self) -> None:
		"""With ``copyPoints=False``, the center is the given point."""
		center = Point2D(1, 2)

		circle = Circle(center, 3, copyPoints=False)

		self.assertIs(center, circle.Center)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for point in trapezium.points:
			self.assertIsInstance(point, Point2D)

		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in trapezium.points))

	def test_Trapezium_Copy(self) -> None:
		"""The corners are copies: moving a given point afterwards doesn't change the shape."""
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)
		point00 += (5, 5)

		for given, corner in zip((point00, point01, point11, point10), trapezium.points):
			self.assertIsNot(given, corner)

		self.assertTupleEqual((6, 6), point00.ToTuple())
		self.assertTupleEqual((1, 1), trapezium.points[0].ToTuple())


class Edges(Testcase):
	def test_Polygon(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5), Point2D(-1, 3))

		polygon = Polygon(points)

		for segment in polygon.Segments:
			self.assertIsInstance(segment, LineSegment2D)

		self.assertTupleEqual(
			(
				((0, 0), (4, 0)),
				((4, 0), (5, 3)),
				((5, 3), (2, 5)),
				((2, 5), (-1, 3)),
				((-1, 3), (0, 0))
			),
			tuple(segment.ToTuple() for segment in polygon.Segments)
		)

	def test_Polygon_SharedCorners(self) -> None:
		"""Each edge ends in the corner the next edge starts in, and both are the shape's corner object."""
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5))

		polygon = Polygon(points)

		for index, segment in enumerate(polygon.Segments):
			self.assertIs(polygon.Points[index], segment.start)
			self.assertIs(polygon.Points[(index + 1) % 4], segment.end)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for segment in trapezium.segments:
			self.assertIsInstance(segment, LineSegment2D)

		self.assertTupleEqual(
			(
				((1, 1), (3, 1)),
				((3, 1), (4, 3)),
				((4, 3), (0, 3)),
				((0, 3), (1, 1))
			),
			tuple(segment.ToTuple() for segment in trapezium.segments)
		)

	def test_Trapezium_SharedCorners(self) -> None:
		"""Each edge ends in the corner the next edge starts in, and both are the shape's corner object."""
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for index, segment in enumerate(trapezium.segments):
			self.assertIs(trapezium.points[index], segment.start)
			self.assertIs(trapezium.points[(index + 1) % 4], segment.end)


class Measurements(Testcase):
	def test_Circle_Diameter(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertEqual(6, circle.Diameter)
		self.assertIsInstance(circle.Diameter, int)

	def test_Circle_Diameter_float(self) -> None:
		circle = Circle(Point2D(1.0, 2.0), 1.25)

		self.assertEqual(2.5, circle.Diameter)

	def test_Circle_Circumference(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertTrue(isclose(6 * pi, circle.Circumference))

	def test_Circle_Area(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertTrue(isclose(9 * pi, circle.Area))


class Representation(Testcase):
	def test_Polygon_repr(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("Polygon((0, 0), (4, 0), (2, 3))", repr(polygon))

	def test_Polygon_str(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("((0, 0) → (4, 0) → (2, 3) → (0, 0))", str(polygon))

	def test_Circle_repr(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertEqual("Circle((1, 2), 3)", repr(circle))

	def test_Circle_str(self) -> None:
		circle = Circle(Point2D(1.5, 2), 0.5)

		self.assertEqual("((1.5, 2), r=0.5)", str(circle))
