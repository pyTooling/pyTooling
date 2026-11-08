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
Unit tests for :mod:`pyTooling.Cartesian2D.Shapes` - polygon, polyline, trapezium, rectangle, square, circle, ellipse
and path.
"""
from copy                         import copy, deepcopy
from math                         import cos, isclose, pi, radians, sin, sqrt

from pyTooling.Cartesian2D        import Point2D, Offset2D, Size2D, BoundingBox2D, LineSegment2D, ArcSegment2D, \
                                         QuadraticBezierSegment2D, CubicBezierSegment2D, Alignment2D, SweepDirection, \
                                         AlreadyOwnedError, DuplicatePointError, NotEnoughCornersError, NotOwnedError, \
                                         NotInSameFrameError, CrossingEdgesError, Cartesian2DError
from pyTooling.Cartesian2D.Shapes import Shape, Geometry2D, EllipticalGeometry2D, Polygon, PolyLine, Trapezium, \
                                         Rectangle, Square, Circle, Ellipse, Path
from pyTooling.Cartesian2D.Groups import Group2D, Canvas2D, YAxisDirection
from pyTooling.Exceptions         import InvalidOperationError
from pyTooling.MetaClasses        import ExtendedType, AbstractClassError
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Shape(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Shape()

		self.assertEqual(
			"Class 'Shape' is abstract. The following methods: 'BoundingBox', 'Move', '_MirrorX', "
			"'_MirrorY' need to be overridden in a derived class.",
			str(context.exception)
		)

	def test_Geometry2D(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Geometry2D()

		self.assertEqual(
			"Class 'Geometry2D' is abstract. The following methods: 'BoundingBox', 'Move', '_MirrorX', "
			"'_MirrorY', 'Area', 'Perimeter' need to be overridden in a derived class.",
			str(context.exception)
		)

	def test_EllipticalGeometry2D(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = EllipticalGeometry2D(Point2D(1, 2))

		self.assertEqual(
			"Class 'EllipticalGeometry2D' is abstract. The following methods: 'BoundingBox', 'Area', 'Perimeter' need to "
			"be overridden in a derived class.",
			str(context.exception)
		)

	def test_Hierarchy(self) -> None:
		"""Closed shapes are geometries; a path is a shape only."""
		self.assertTrue(issubclass(Geometry2D, Shape))
		for geometry in (Polygon, Trapezium, Rectangle, Square, Circle, Ellipse):
			with self.subTest(geometry=geometry):
				self.assertTrue(issubclass(geometry, Geometry2D))

		self.assertTrue(issubclass(Trapezium, Polygon))
		self.assertIsInstance(Square(Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3)), Polygon)
		self.assertFalse(issubclass(Path, Geometry2D))
		self.assertTrue(issubclass(Path, Shape))
		self.assertTrue(issubclass(PolyLine, Path))
		self.assertFalse(issubclass(PolyLine, Geometry2D))
		self.assertIsInstance(Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))), Geometry2D)
		self.assertIsInstance(Circle(Point2D(1, 2), 3), Geometry2D)
		self.assertIsInstance(Ellipse(Point2D(1, 2), 3, 2), Geometry2D)
		self.assertFalse(issubclass(Circle, Ellipse))

	def test_Hierarchy_Elliptical(self) -> None:
		"""A circle and an ellipse share their base-class, but neither is the other."""
		self.assertTrue(issubclass(EllipticalGeometry2D, Geometry2D))
		self.assertTrue(issubclass(Circle, EllipticalGeometry2D))
		self.assertTrue(issubclass(Ellipse, EllipticalGeometry2D))
		self.assertIsInstance(Circle(Point2D(1, 2), 3), EllipticalGeometry2D)
		self.assertIsInstance(Ellipse(Point2D(1, 2), 3, 2), EllipticalGeometry2D)
		self.assertNotIsInstance(Circle(Point2D(1, 2), 3), Ellipse)
		self.assertNotIsInstance(Ellipse(Point2D(1, 2), 3, 3), Circle)
		self.assertFalse(issubclass(Ellipse, Circle))
		self.assertFalse(issubclass(Polygon, EllipticalGeometry2D))
		self.assertFalse(hasattr(Circle, "RadiusX"))
		self.assertFalse(hasattr(Circle, "RadiusY"))
		self.assertFalse(hasattr(Ellipse, "Radius"))

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
		with self.assertRaises(NotEnoughCornersError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0)))

		self.assertEqual("Polygon has fewer than 3 corners.", str(context.exception))
		self.assertListEqual(["Got 2 points."], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'points' has fewer than 3 points.", str(context.exception.__cause__))

	def test_Polygon_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_Polygon_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_PolyLine(self) -> None:
		point0 = Point2D(0, 0)
		point1 = Point2D(4, 0)
		point2 = Point2D(2, 3)

		polyline = PolyLine((point0, point1, point2))

		self.assertIsInstance(polyline, Shape)
		self.assertEqual(3, len(polyline.Points))
		self.assertEqual(2, len(polyline.Segments))

	def test_PolyLine_TwoPoints(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))

		self.assertEqual(2, len(polyline.Points))
		self.assertEqual(1, len(polyline.Segments))

	def test_PolyLine_Generator(self) -> None:
		"""The points are consumed from any iterable, also from a generator."""
		polyline = PolyLine(Point2D(x, y) for x, y in ((0, 0), (4, 0), (2, 3)))

		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))

	def test_PolyLine_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = PolyLine(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_PolyLine_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PolyLine(2)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_PolyLine_NoneElement(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = PolyLine((Point2D(0, 0), None))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_PolyLine_strElement(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PolyLine((Point2D(0, 0), "4, 0"))

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_PolyLine_OnePoint(self) -> None:
		with self.assertRaises(NotEnoughCornersError) as context:
			_ = PolyLine((Point2D(0, 0), ))

		self.assertEqual("PolyLine has fewer than 2 points.", str(context.exception))
		self.assertListEqual(["Got 1 points."], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'points' has fewer than 2 points.", str(context.exception.__cause__))

	def test_PolyLine_Empty(self) -> None:
		with self.assertRaises(NotEnoughCornersError) as context:
			_ = PolyLine(())

		self.assertEqual("PolyLine has fewer than 2 points.", str(context.exception))
		self.assertListEqual(["Got 0 points."], context.exception.__notes__)

	def test_PolyLine_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_PolyLine_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		self.assertIsInstance(trapezium, Shape)
		self.assertEqual(4, len(trapezium.Points))
		self.assertEqual(4, len(trapezium.Segments))

	def test_Trapezium_str1(self) -> None:
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium("1, 1", point01, point11, point10)

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str2(self) -> None:
		point00 = Point2D(1, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, "3, 1", point11, point10)

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str3(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, "3, 3", point10)

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str4(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, point11, "1, 3")

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_None1(self) -> None:
		point01 = Point2D(1, 1)
		point11 = Point2D(2, 2)
		point10 = Point2D(3, 3)

		with self.assertRaises(ValueError) as context:
			_ = Trapezium(None, point01, point11, point10)

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_Trapezium_None2(self) -> None:
		point00 = Point2D(0, 0)
		point11 = Point2D(2, 2)
		point10 = Point2D(3, 3)

		with self.assertRaises(ValueError) as context:
			_ = Trapezium(point00, None, point11, point10)

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_Trapezium_None3(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(1, 1)
		point10 = Point2D(3, 3)

		with self.assertRaises(ValueError) as context:
			_ = Trapezium(point00, point01, None, point10)

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_Trapezium_None4(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(1, 1)
		point11 = Point2D(2, 2)

		with self.assertRaises(ValueError) as context:
			_ = Trapezium(point00, point01, point11, None)

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

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
			tuple(point.ToTuple() for point in rectangle.Points)
		)

	def test_Rectangle_AxisAligned(self) -> None:
		"""Two edges are parallel to the y-axis."""
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 0)
		point11 = Point2D(4, 2)
		point10 = Point2D(0, 2)

		rectangle = Rectangle(point00, point01, point11, point10)

		self.assertEqual(4, len(rectangle.Segments))
		self.assertTupleEqual((4.0, 2.0, 4.0, 2.0), tuple(segment.Length for segment in rectangle.Segments))

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

		self.assertEqual(4, len(rectangle.Segments))
		for segment, length in zip(rectangle.Segments, (4.0, 2.0, 4.0, 2.0)):
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

		with self.assertRaises(CrossingEdgesError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (4, 0)) and ((4, 3) → (2.88, -0.84))."], context.exception.__notes__)

	def test_Rectangle_SameCorners(self) -> None:
		"""Two pairs of consecutive corners are the same point: the edges between them touch each other."""
		point00 = Point2D(0, 0)
		point01 = Point2D(0, 0)
		point11 = Point2D(4, 2)
		point10 = Point2D(4, 2)

		with self.assertRaises(CrossingEdgesError) as context:
			_ = Rectangle(point00, point01, point11, point10)

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (4, 2)) and ((4, 2) → (0, 0))."], context.exception.__notes__)

	def test_Rectangle_str(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 2)
		point11 = Point2D(3, 4)

		with self.assertRaises(TypeError) as context:
			_ = Rectangle(point00, point01, point11, "-1, 2")

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
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
			tuple(point.ToTuple() for point in square.Points)
		)

	def test_Square_AxisAligned(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		square = Square(point00, point01, point11, point10)

		self.assertEqual(4, len(square.Segments))
		self.assertTupleEqual((2.0, 2.0, 2.0, 2.0), tuple(segment.Length for segment in square.Segments))

	def test_Square_Rotated(self) -> None:
		"""A square rotated against the axes: all edges are sqrt(5) long, their x-differences are 2 and 1."""
		point00 = Point2D(0, 0)
		point01 = Point2D(2, 1)
		point11 = Point2D(1, 3)
		point10 = Point2D(-1, 2)

		square = Square(point00, point01, point11, point10)

		self.assertEqual(4, len(square.Segments))
		for segment in square.Segments:
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

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
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

	def test_Ellipse_int(self) -> None:
		center = Point2D(1, 2)

		ellipse = Ellipse(center, 3, 2)

		self.assertIsInstance(ellipse, Shape)
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())
		self.assertEqual(3, ellipse.RadiusX)
		self.assertEqual(2, ellipse.RadiusY)

	def test_Ellipse_float(self) -> None:
		ellipse = Ellipse(Point2D(1.5, 2.5), 0.5, 1.25)

		self.assertTupleEqual((1.5, 2.5), ellipse.Center.ToTuple())
		self.assertEqual(0.5, ellipse.RadiusX)
		self.assertEqual(1.25, ellipse.RadiusY)

	def test_Ellipse_EqualRadii(self) -> None:
		"""An ellipse with equal radii is allowed, it is a circle."""
		ellipse = Ellipse(Point2D(1, 2), 3, 3)

		self.assertEqual(ellipse.RadiusX, ellipse.RadiusY)

	def test_Ellipse_CenterNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(None, 3, 2)

		self.assertEqual("Parameter 'center' is None.", str(context.exception))

	def test_Ellipse_CenterStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ellipse("1, 2", 3, 2)

		self.assertEqual("Parameter 'center' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Ellipse_RadiusXNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(Point2D(1, 2), None, 2)

		self.assertEqual("Parameter 'radiusX' is None.", str(context.exception))

	def test_Ellipse_RadiusXStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ellipse(Point2D(1, 2), "3", 2)

		self.assertEqual("Parameter 'radiusX' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Ellipse_RadiusXZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(Point2D(1, 2), 0, 2)

		self.assertEqual("Parameter 'radiusX' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)

	def test_Ellipse_RadiusYNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(Point2D(1, 2), 3, None)

		self.assertEqual("Parameter 'radiusY' is None.", str(context.exception))

	def test_Ellipse_RadiusYStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ellipse(Point2D(1, 2), 3, "2")

		self.assertEqual("Parameter 'radiusY' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Ellipse_RadiusYNegative(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(Point2D(1, 2), 3, -1.5)

		self.assertEqual("Parameter 'radiusY' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '-1.5'."], context.exception.__notes__)

	def test_Ellipse_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Ellipse(Point2D(1, 2), 3, 2, copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_Ellipse_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ellipse(Point2D(1, 2), 3, 2, copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class CrossingEdges(Testcase):
	def test_BowTie(self) -> None:
		corners = (Point2D(0, 0), Point2D(2, 2), Point2D(2, 0), Point2D(0, 2))

		with self.assertRaises(CrossingEdgesError) as context:
			_ = Polygon(corners, copyPoints=False)

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (2, 2)) and ((2, 0) → (0, 2))."], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual(
			"Parameter 'points' describes edges crossing or touching each other.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(corners[0].Parent)

	def test_TouchingCorner(self) -> None:
		"""The corner (3, 0) lies on the first edge."""
		with self.assertRaises(CrossingEdgesError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(6, 0), Point2D(6, 4), Point2D(3, 0), Point2D(0, 4)))

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (6, 0)) and ((6, 4) → (3, 0))."], context.exception.__notes__)

	def test_SamePosition(self) -> None:
		"""A figure eight with its crossing given twice: two corners at the same position touch each other."""
		with self.assertRaises(CrossingEdgesError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(2, 2), Point2D(4, 0), Point2D(4, 4), Point2D(2, 2), Point2D(0, 4)))

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (2, 2)) and ((4, 4) → (2, 2))."], context.exception.__notes__)

	def test_BackTracking(self) -> None:
		"""The second edge runs back along the first one."""
		with self.assertRaises(CrossingEdgesError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 0), Point2D(2, 3)))

		self.assertEqual("Polygon has overlapping edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (4, 0)) and ((4, 0) → (2, 0))."], context.exception.__notes__)
		self.assertEqual(
			"Parameter 'points' describes edges running back along each other.",
			str(context.exception.__cause__)
		)

	def test_Collinear(self) -> None:
		"""Three corners on one line: the closing edge runs back along the others."""
		with self.assertRaises(CrossingEdgesError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(2, 0), Point2D(4, 0)))

		self.assertEqual("Polygon has overlapping edges.", str(context.exception))
		self.assertListEqual(["Got edges ((2, 0) → (4, 0)) and ((4, 0) → (0, 0))."], context.exception.__notes__)

	def test_Concave(self) -> None:
		"""A concave polygon has no crossing edges."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(1, 1), Point2D(1, 3), Point2D(0, 3)))

		self.assertEqual(6, len(polygon.Segments))

	def test_Trapezium(self) -> None:
		"""A trapezium is a polygon, so its edges must not cross either."""
		with self.assertRaises(CrossingEdgesError) as context:
			_ = Trapezium(Point2D(0, 0), Point2D(4, 4), Point2D(4, 0), Point2D(0, 4))

		self.assertEqual("Polygon has crossing edges.", str(context.exception))
		self.assertListEqual(["Got edges ((0, 0) → (4, 4)) and ((4, 0) → (0, 4))."], context.exception.__notes__)

	def test_Error(self) -> None:
		self.assertTrue(issubclass(CrossingEdgesError, Cartesian2DError))


class CircleConstructors(Testcase):
	def test_FromPoints(self) -> None:
		first = Point2D(0, 0)

		circle = Circle.FromPoints((first, Point2D(2, 0), Point2D(1, 1)))

		self.assertIs(Circle, type(circle))
		self.assertTupleEqual((1.0, 0.0), circle.Center.ToTuple())
		self.assertEqual(1.0, circle.Radius)
		self.assertIs(circle, circle.Center.Parent)
		self.assertIsNone(first.Parent)

	def test_FromPoints_RightTriangle(self) -> None:
		"""The center of a right triangle's circumcircle is the midpoint of its hypotenuse."""
		circle = Circle.FromPoints((Point2D(0, 0), Point2D(4, 0), Point2D(0, 3)))

		self.assertTupleEqual((2.0, 1.5), circle.Center.ToTuple())
		self.assertEqual(2.5, circle.Radius)

	def test_FromPoints_FourPoints(self) -> None:
		circle = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(1, -1)))

		self.assertTupleEqual((1.0, 0.0), circle.Center.ToTuple())
		self.assertEqual(1.0, circle.Radius)

	def test_FromPoints_FivePoints(self) -> None:
		circle = Circle.FromPoints((Point2D(5, 0), Point2D(0, 5), Point2D(-5, 0), Point2D(3, 4), Point2D(-4, -3)))

		self.assertAlmostEqual(0, circle.Center.X)
		self.assertAlmostEqual(0, circle.Center.Y)
		self.assertEqual(5.0, circle.Radius)

	def test_FromPoints_Generator(self) -> None:
		circle = Circle.FromPoints(Point2D(x, y) for x, y in ((0, 0), (4, 0), (0, 3)))

		self.assertTupleEqual((2.0, 1.5), circle.Center.ToTuple())

	def test_FromPoints_Data(self) -> None:
		group = Group2D()
		value = object()

		circle = Circle.FromPoints(
			(Point2D(0, 0), Point2D(2, 0), Point2D(1, 1)), value=value, keyValuePairs={"layer": 1}, parent=group
		)

		self.assertIs(value, circle.Value)
		self.assertEqual(1, circle["layer"])
		self.assertTupleEqual((circle, ), group.Children)

	def test_FromPoints_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints(None)

		self.assertEqual("Parameter 'points' is None.", str(context.exception))

	def test_FromPoints_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle.FromPoints(3)

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_FromPoints_ElementNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), None, Point2D(1, 1)))

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))

	def test_FromPoints_ElementTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0), (1, 1)))

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_FromPoints_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints(())

		self.assertEqual("Parameter 'points' has fewer than 3 points.", str(context.exception))
		self.assertListEqual(["Got 0 points."], context.exception.__notes__)

	def test_FromPoints_TwoPoints(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0)))

		self.assertEqual("Parameter 'points' has fewer than 3 points.", str(context.exception))
		self.assertListEqual(["Got 2 points."], context.exception.__notes__)

	def test_FromPoints_SamePosition01(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(0, 0), Point2D(1, 1)))

		self.assertEqual(
			"Two of the first three points of parameter 'points' are at the same position.",
			str(context.exception)
		)
		self.assertListEqual(["Got point (0, 0) at index 0 and 1."], context.exception.__notes__)

	def test_FromPoints_SamePosition12(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0), Point2D(2, 0)))

		self.assertEqual(
			"Two of the first three points of parameter 'points' are at the same position.",
			str(context.exception)
		)
		self.assertListEqual(["Got point (2, 0) at index 1 and 2."], context.exception.__notes__)

	def test_FromPoints_Collinear(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(1, 1), Point2D(3, 3), Point2D(4, 4)))

		self.assertEqual("The first three points of parameter 'points' are on one line.", str(context.exception))
		self.assertListEqual(["Got points (0, 0), (1, 1) and (3, 3)."], context.exception.__notes__)

	def test_FromPoints_OffCircle(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(3, 0)))

		self.assertEqual(
			"Parameter 'points' has points, which aren't on the circle through the first three points.",
			str(context.exception)
		)
		self.assertListEqual(
			["Got point (3, 0) at index 3 with distance 2.0 to the center, while the radius is 1.0."],
			context.exception.__notes__
		)

	def test_FromPoints_OffCircle_Several(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromPoints((Point2D(0, 0), Point2D(2, 0), Point2D(1, 1), Point2D(3, 0), Point2D(1, -1), Point2D(1, 3)))

		self.assertEqual(
			"Parameter 'points' has points, which aren't on the circle through the first three points.",
			str(context.exception)
		)
		self.assertListEqual(
			[
				"Got point (3, 0) at index 3 with distance 2.0 to the center, while the radius is 1.0.",
				"Got point (1, 3) at index 5 with distance 3.0 to the center, while the radius is 1.0."
			],
			context.exception.__notes__
		)

	def test_FromChord(self) -> None:
		"""The circle passes (2, 1) above the chord's midpoint: center (2, -1.5), radius 2.5."""
		start = Point2D(0, 0)

		circle = Circle.FromChord(start, Point2D(4, 0), 1)

		self.assertIs(Circle, type(circle))
		self.assertTupleEqual((2.0, -1.5), circle.Center.ToTuple())
		self.assertEqual(2.5, circle.Radius)
		self.assertIs(circle, circle.Center.Parent)
		self.assertIsNone(start.Parent)

	def test_FromChord_Negative(self) -> None:
		"""A negative height is on the right of the chord: the circle passes (2, -1)."""
		circle = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), -1)

		self.assertTupleEqual((2.0, 1.5), circle.Center.ToTuple())
		self.assertEqual(2.5, circle.Radius)

	def test_FromChord_ChordPosition(self) -> None:
		"""The root point (1, 0) at a quarter of the chord; the circle passes (1, 1): center (2, -1)."""
		circle = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1, 0.25)

		self.assertTupleEqual((2.0, -1.0), circle.Center.ToTuple())
		self.assertTrue(isclose(sqrt(5), circle.Radius))

	def test_FromChord_Arc(self) -> None:
		"""The circle of an arc with the same chord and height."""
		arc = ArcSegment2D(Point2D(0, 0), Point2D(4, 2), chordPosition=0.3, height=1.5)

		circle = Circle.FromChord(Point2D(0, 0), Point2D(4, 2), 1.5, 0.3)

		self.assertTupleEqual(arc.Center.ToTuple(), circle.Center.ToTuple())
		self.assertEqual(arc.Radius, circle.Radius)

	def test_FromChord_Data(self) -> None:
		group = Group2D()

		circle = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1, value=1, keyValuePairs={"layer": 1}, parent=group)

		self.assertEqual(1, circle.Value)
		self.assertEqual(1, circle["layer"])
		self.assertIs(group, circle.Parent)

	def test_FromChord_StartNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromChord(None, Point2D(4, 0), 1)

		self.assertEqual("Parameter 'start' is None.", str(context.exception))

	def test_FromChord_EndStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle.FromChord(Point2D(0, 0), "4, 0", 1)

		self.assertEqual("Parameter 'end' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_FromChord_NoChord(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromChord(Point2D(1, 2), Point2D(1, 2), 1)

		self.assertEqual("Parameter 'end' is at the position of parameter 'start'.", str(context.exception))
		self.assertListEqual(["Got point (1, 2)."], context.exception.__notes__)

	def test_FromChord_HeightNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), None)

		self.assertEqual("Parameter 'height' is None.", str(context.exception))

	def test_FromChord_HeightStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), "1")

		self.assertEqual("Parameter 'height' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_FromChord_HeightZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 0)

		self.assertEqual("Parameter 'height' is 0.", str(context.exception))

	def test_FromChord_ChordPositionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1, None)

		self.assertEqual("Parameter 'chordPosition' is None.", str(context.exception))

	def test_FromChord_ChordPositionStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1, "0.5")

		self.assertEqual("Parameter 'chordPosition' is not of type 'float'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_FromChord_ChordPositionRange(self) -> None:
		for chordPosition in (-0.25, 1.5):
			with self.subTest(chordPosition=chordPosition):
				with self.assertRaises(ValueError) as context:
					_ = Circle.FromChord(Point2D(0, 0), Point2D(4, 0), 1, chordPosition)

				self.assertEqual("Parameter 'chordPosition' is out of range 0..1.", str(context.exception))
				self.assertListEqual([f"Got value '{chordPosition}'."], context.exception.__notes__)


class Slots(Testcase):
	"""A class derived from a shape with ``slots=True`` gets its own slots and no instance dictionary."""

	def test_Shapes(self) -> None:
		for shapeClass in (Shape, Polygon, PolyLine, Trapezium, Rectangle, Square, EllipticalGeometry2D, Circle, Ellipse):
			self.assertIsInstance(shapeClass, ExtendedType)
			self.assertNotIn("__dict__", dir(shapeClass))

	def test_EllipticalGeometry2D(self) -> None:
		"""The center is a slot of the base-class, the radii are slots of the derived classes."""
		self.assertTupleEqual(("_center", ), EllipticalGeometry2D.__slots__)
		self.assertTupleEqual(("_radius", ), Circle.__slots__)
		self.assertTupleEqual(("_radiusX", "_radiusY"), Ellipse.__slots__)

	def test_Polygon(self) -> None:
		class LabeledPolygon(Polygon, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, points: tuple[Point2D, ...], label: str) -> None:
				super().__init__(points)
				self._label = label

		polygon = LabeledPolygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), "triangle")

		self.assertTupleEqual(("_label", ), LabeledPolygon.__slots__)
		self.assertFalse(hasattr(polygon, "__dict__"))
		self.assertEqual("triangle", polygon._label)

	def test_PolyLine(self) -> None:
		class LabeledPolyLine(PolyLine, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, points: tuple[Point2D, ...], label: str) -> None:
				super().__init__(points)
				self._label = label

		polyline = LabeledPolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), "path")

		self.assertTupleEqual(("_label", ), LabeledPolyLine.__slots__)
		self.assertFalse(hasattr(polyline, "__dict__"))
		self.assertEqual("path", polyline._label)

	def test_Trapezium(self) -> None:
		class LabeledTrapezium(Trapezium, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, p00: Point2D, p01: Point2D, p11: Point2D, p10: Point2D, label: str) -> None:
				super().__init__(p00, p01, p11, p10)
				self._label = label

		trapezium = LabeledTrapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), "trapezium")

		self.assertTupleEqual(("_label", ), LabeledTrapezium.__slots__)
		self.assertFalse(hasattr(trapezium, "__dict__"))
		self.assertEqual("trapezium", trapezium._label)

	def test_Rectangle(self) -> None:
		class LabeledRectangle(Rectangle, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, p00: Point2D, p01: Point2D, p11: Point2D, p10: Point2D, label: str) -> None:
				super().__init__(p00, p01, p11, p10)
				self._label = label

		rectangle = LabeledRectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), "rectangle")

		self.assertTupleEqual(("_label", ), LabeledRectangle.__slots__)
		self.assertFalse(hasattr(rectangle, "__dict__"))
		self.assertEqual("rectangle", rectangle._label)

	def test_Square(self) -> None:
		class LabeledSquare(Square, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, p00: Point2D, p01: Point2D, p11: Point2D, p10: Point2D, label: str) -> None:
				super().__init__(p00, p01, p11, p10)
				self._label = label

		square = LabeledSquare(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), "square")

		self.assertTupleEqual(("_label", ), LabeledSquare.__slots__)
		self.assertFalse(hasattr(square, "__dict__"))
		self.assertEqual("square", square._label)

	def test_Circle(self) -> None:
		class LabeledCircle(Circle, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, center: Point2D, radius: int, label: str) -> None:
				super().__init__(center, radius)
				self._label = label

		circle = LabeledCircle(Point2D(1, 2), 3, "circle")

		self.assertTupleEqual(("_label", ), LabeledCircle.__slots__)
		self.assertFalse(hasattr(circle, "__dict__"))
		self.assertEqual("circle", circle._label)

	def test_Ellipse(self) -> None:
		class LabeledEllipse(Ellipse, metaclass=ExtendedType, slots=True):
			_label: str

			def __init__(self, center: Point2D, radiusX: int, radiusY: int, label: str) -> None:
				super().__init__(center, radiusX, radiusY)
				self._label = label

		ellipse = LabeledEllipse(Point2D(1, 2), 3, 2, "ellipse")

		self.assertTupleEqual(("_label", ), LabeledEllipse.__slots__)
		self.assertFalse(hasattr(ellipse, "__dict__"))
		self.assertEqual("ellipse", ellipse._label)


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

	def test_PolyLine(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5))

		polyline = PolyLine(points)

		for point in polyline.Points:
			self.assertIsInstance(point, Point2D)

		self.assertTupleEqual(((0, 0), (4, 0), (5, 3), (2, 5)), tuple(point.ToTuple() for point in polyline.Points))

	def test_PolyLine_Copy(self) -> None:
		"""The points are copies: moving a given point afterwards doesn't change the polyline."""
		point0 = Point2D(0, 0)
		point1 = Point2D(4, 0)

		polyline = PolyLine((point0, point1))
		point0 += (5, 5)

		for given, vertex in zip((point0, point1), polyline.Points):
			self.assertIsNot(given, vertex)

		self.assertTupleEqual((5, 5), point0.ToTuple())
		self.assertTupleEqual((0, 0), polyline.Points[0].ToTuple())

	def test_PolyLine_Reference(self) -> None:
		"""With ``copyPoints=False``, the points are the given points."""
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polyline = PolyLine(points, copyPoints=False)

		for given, vertex in zip(points, polyline.Points):
			self.assertIs(given, vertex)

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

	def test_Ellipse_Copy(self) -> None:
		"""The center is a copy: moving the given point afterwards doesn't change the ellipse."""
		center = Point2D(1, 2)

		ellipse = Ellipse(center, 3, 2)
		center += (5, 5)

		self.assertIsNot(center, ellipse.Center)
		self.assertTupleEqual((6, 7), center.ToTuple())
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())

	def test_Ellipse_Reference(self) -> None:
		"""With ``copyPoints=False``, the center is the given point."""
		center = Point2D(1, 2)

		ellipse = Ellipse(center, 3, 2, copyPoints=False)

		self.assertIs(center, ellipse.Center)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for point in trapezium.Points:
			self.assertIsInstance(point, Point2D)

		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in trapezium.Points))

	def test_Trapezium_Copy(self) -> None:
		"""The corners are copies: moving a given point afterwards doesn't change the shape."""
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)
		point00 += (5, 5)

		for given, corner in zip((point00, point01, point11, point10), trapezium.Points):
			self.assertIsNot(given, corner)

		self.assertTupleEqual((6, 6), point00.ToTuple())
		self.assertTupleEqual((1, 1), trapezium.Points[0].ToTuple())


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
			self.assertIs(polygon.Points[index], segment.Start)
			self.assertIs(polygon.Points[(index + 1) % 4], segment.End)

	def test_PolyLine(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5))

		polyline = PolyLine(points)

		for segment in polyline.Segments:
			self.assertIsInstance(segment, LineSegment2D)

		self.assertTupleEqual(
			(
				((0, 0), (4, 0)),
				((4, 0), (5, 3)),
				((5, 3), (2, 5))
			),
			tuple(segment.ToTuple() for segment in polyline.Segments)
		)

	def test_PolyLine_SharedPoints(self) -> None:
		"""Each edge ends in the point the next edge starts in, and both are the polyline's point object."""
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5))

		polyline = PolyLine(points)

		for index, segment in enumerate(polyline.Segments):
			self.assertIs(polyline.Points[index], segment.Start)
			self.assertIs(polyline.Points[index + 1], segment.End)

	def test_PolyLine_Open(self) -> None:
		"""No edge connects the last point back to the first one."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertIs(polyline.Points[0], polyline.Segments[0].Start)
		self.assertIs(polyline.Points[-1], polyline.Segments[-1].End)
		for segment in polyline.Segments:
			self.assertIsNot(polyline.Points[0], segment.End)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for segment in trapezium.Segments:
			self.assertIsInstance(segment, LineSegment2D)

		self.assertTupleEqual(
			(
				((1, 1), (3, 1)),
				((3, 1), (4, 3)),
				((4, 3), (0, 3)),
				((0, 3), (1, 1))
			),
			tuple(segment.ToTuple() for segment in trapezium.Segments)
		)

	def test_Trapezium_SharedCorners(self) -> None:
		"""Each edge ends in the corner the next edge starts in, and both are the shape's corner object."""
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(4, 3)
		point10 = Point2D(0, 3)

		trapezium = Trapezium(point00, point01, point11, point10)

		for index, segment in enumerate(trapezium.Segments):
			self.assertIs(trapezium.Points[index], segment.Start)
			self.assertIs(trapezium.Points[(index + 1) % 4], segment.End)


class Properties(Testcase):
	def test_Trapezium_Points(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		with self.assertRaises(AttributeError):
			trapezium.Points = (Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in trapezium.Points))

	def test_Trapezium_Segments(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		segments =  trapezium.Segments

		with self.assertRaises(AttributeError):
			trapezium.Segments = ()

		self.assertIs(segments, trapezium.Segments)

	def test_PolyLine_Points(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))
		points =   polyline.Points

		with self.assertRaises(AttributeError):
			polyline.Points = (Point2D(1, 1), Point2D(2, 2))

		self.assertIs(points, polyline.Points)

	def test_PolyLine_Segments(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))
		segments = polyline.Segments

		with self.assertRaises(AttributeError):
			polyline.Segments = ()

		self.assertIs(segments, polyline.Segments)

	def test_Ellipse_Radii(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		with self.assertRaises(AttributeError):
			ellipse.RadiusX = 4

		with self.assertRaises(AttributeError):
			ellipse.RadiusY = 4

		self.assertEqual(3, ellipse.RadiusX)
		self.assertEqual(2, ellipse.RadiusY)


class Aliases(Testcase):
	def test_Trapezium_SameValue(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		self.assertIs(trapezium.Points, trapezium.points)
		self.assertIs(trapezium.Segments, trapezium.segments)

	def test_Trapezium_points(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		corners =   [Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)]

		trapezium.points = corners

		self.assertIsInstance(trapezium.points, tuple)
		self.assertEqual(4, len(trapezium.points))
		for given, corner in zip(corners, trapezium.points):
			self.assertIs(given, corner)

	def test_Trapezium_points_None(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		points =    trapezium.points

		with self.assertRaises(ValueError) as context:
			trapezium.points = None

		self.assertEqual("Parameter 'points' is None.", str(context.exception))
		self.assertIs(points, trapezium.points)

	def test_Trapezium_points_int(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		points =    trapezium.points

		with self.assertRaises(TypeError) as context:
			trapezium.points = 4

		self.assertEqual("Parameter 'points' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIs(points, trapezium.points)

	def test_Trapezium_points_NoneElement(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		points =    trapezium.points

		with self.assertRaises(ValueError) as context:
			trapezium.points = (points[0], None, points[2], points[3])

		self.assertEqual("An element of parameter 'points' is None.", str(context.exception))
		self.assertIs(points, trapezium.points)

	def test_Trapezium_points_strElement(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		points =    trapezium.points

		with self.assertRaises(TypeError) as context:
			trapezium.points = (points[0], "3, 1", points[2], points[3])

		self.assertEqual("An element of parameter 'points' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIs(points, trapezium.points)

	def test_Trapezium_segments(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		edges =     [LineSegment2D(Point2D(0, 0), Point2D(2, 0)), LineSegment2D(Point2D(2, 0), Point2D(2, 2)),
		             LineSegment2D(Point2D(2, 2), Point2D(0, 2)), LineSegment2D(Point2D(0, 2), Point2D(0, 0))]

		trapezium.segments = edges

		self.assertIsInstance(trapezium.segments, tuple)
		self.assertEqual(4, len(trapezium.segments))
		for given, edge in zip(edges, trapezium.segments):
			self.assertIs(given, edge)

	def test_Trapezium_segments_None(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		segments =    trapezium.segments

		with self.assertRaises(ValueError) as context:
			trapezium.segments = None

		self.assertEqual("Parameter 'segments' is None.", str(context.exception))
		self.assertIs(segments, trapezium.segments)

	def test_Trapezium_segments_int(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		segments =    trapezium.segments

		with self.assertRaises(TypeError) as context:
			trapezium.segments = 4

		self.assertEqual("Parameter 'segments' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIs(segments, trapezium.segments)

	def test_Trapezium_segments_NoneElement(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		segments =    trapezium.segments

		with self.assertRaises(ValueError) as context:
			trapezium.segments = (segments[0], None, segments[2], segments[3])

		self.assertEqual("An element of parameter 'segments' is None.", str(context.exception))
		self.assertIs(segments, trapezium.segments)

	def test_Trapezium_segments_strElement(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		segments =    trapezium.segments

		with self.assertRaises(TypeError) as context:
			trapezium.segments = (segments[0], "(3, 1) → (4, 3)", segments[2], segments[3])

		self.assertEqual("An element of parameter 'segments' is not of type 'LineSegment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertIs(segments, trapezium.segments)


class Measurements(Testcase):
	def test_Circle_Diameter(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertEqual(6, circle.Diameter)
		self.assertIsInstance(circle.Diameter, int)

	def test_Circle_Diameter_float(self) -> None:
		circle = Circle(Point2D(1.0, 2.0), 1.25)

		self.assertEqual(2.5, circle.Diameter)

	def test_Circle_Perimeter(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertTrue(isclose(6 * pi, circle.Perimeter))

	def test_Circle_Area(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertTrue(isclose(9 * pi, circle.Area))

	def test_Polygon_Triangle(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual(6.0, polygon.Area)
		self.assertTrue(isclose(4 + 2 * sqrt(13), polygon.Perimeter))

	def test_Polygon_Clockwise(self) -> None:
		"""The corners in clockwise order enclose the same area."""
		polygon = Polygon((Point2D(0, 0), Point2D(2, 3), Point2D(4, 0)))

		self.assertEqual(6.0, polygon.Area)

	def test_Polygon_Concave(self) -> None:
		"""An L-shape: a 4 x 1 bar and a 1 x 2 bar on top of it."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(4, 1), Point2D(1, 1), Point2D(1, 3), Point2D(0, 3)))

		self.assertEqual(6.0, polygon.Area)
		self.assertEqual(14.0, polygon.Perimeter)

	def test_Polygon_Float(self) -> None:
		polygon = Polygon((Point2D(0.5, 0.5), Point2D(2.5, 0.5), Point2D(2.5, 1.5), Point2D(0.5, 1.5)))

		self.assertEqual(2.0, polygon.Area)
		self.assertEqual(6.0, polygon.Perimeter)

	def test_Polygon_StraightCorner(self) -> None:
		"""A corner in the middle of a straight side is allowed."""
		polygon = Polygon((Point2D(0, 0), Point2D(2, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2)))

		self.assertEqual(8.0, polygon.Area)
		self.assertEqual(12.0, polygon.Perimeter)

	def test_Trapezium(self) -> None:
		"""Parallel sides 6 and 3, height 2; the legs are sqrt(8) and sqrt(5) long."""
		trapezium = Trapezium(Point2D(0, 0), Point2D(6, 0), Point2D(4, 2), Point2D(1, 2))

		self.assertEqual(9.0, trapezium.Area)
		self.assertTrue(isclose(9 + sqrt(8) + sqrt(5), trapezium.Perimeter))

	def test_Trapezium_Clockwise(self) -> None:
		trapezium = Trapezium(Point2D(1, 2), Point2D(4, 2), Point2D(6, 0), Point2D(0, 0))

		self.assertEqual(9.0, trapezium.Area)

	def test_Rectangle(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		self.assertEqual(8.0, rectangle.Area)
		self.assertEqual(12.0, rectangle.Perimeter)

	def test_Rectangle_Rotated(self) -> None:
		"""A 2 x 1 rectangle rotated by 45 degrees."""
		rectangle = Rectangle(
			Point2D(0, 0),
			Point2D(sqrt(2), sqrt(2)),
			Point2D(sqrt(2) / 2, 3 * sqrt(2) / 2),
			Point2D(-sqrt(2) / 2, sqrt(2) / 2)
		)

		self.assertTrue(isclose(2, rectangle.Area))
		self.assertTrue(isclose(6, rectangle.Perimeter))

	def test_Square(self) -> None:
		square = Square(Point2D(1, 1), Point2D(3, 1), Point2D(3, 3), Point2D(1, 3))

		self.assertEqual(4.0, square.Area)
		self.assertEqual(8.0, square.Perimeter)

	def test_PolyLine_Length(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(3, 4), Point2D(3, 0), Point2D(1, 0)))

		self.assertEqual(11.0, polyline.Length)
		self.assertIsInstance(polyline.Length, float)

	def test_PolyLine_Length_Moved(self) -> None:
		"""The length is computed on every access: it follows a moved point."""
		polyline = PolyLine((Point2D(0, 0), Point2D(3, 0)))
		vertex =   polyline.Points[1]

		vertex += (0, 4)

		self.assertEqual(5.0, polyline.Length)

	def test_Ellipse_Area(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		self.assertTrue(isclose(6 * pi, ellipse.Area))

	def test_Ellipse_Perimeter(self) -> None:
		"""Ramanujan's approximation, compared with the exact value of the elliptic integral."""
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		self.assertTrue(isclose(15.865439589290589, ellipse.Perimeter, rel_tol=1e-9))

	def test_Ellipse_Perimeter_Flat(self) -> None:
		"""The approximation is slightly too small, at most by 0.04 %, for a very flat ellipse."""
		ellipse = Ellipse(Point2D(0, 0), 1, 0.000001)

		self.assertLess(ellipse.Perimeter, 4.0)
		self.assertTrue(isclose(4.0, ellipse.Perimeter, rel_tol=4.1e-4))

	def test_Ellipse_Perimeter_Circle(self) -> None:
		"""With equal radii, the approximation is the circle's perimeter."""
		ellipse = Ellipse(Point2D(1, 2), 3, 3)
		circle =  Circle(Point2D(1, 2), 3)

		self.assertTrue(isclose(circle.Perimeter, ellipse.Perimeter))
		self.assertTrue(isclose(circle.Area, ellipse.Area))


class Bounds(Testcase):
	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, -1), Point2D(5, 3), Point2D(-2, 5)))

		box = polygon.BoundingBox

		self.assertIs(BoundingBox2D, type(box))
		self.assertTupleEqual((-2, -1, 5, 5), box.ToTuple())

	def test_Polygon_Moved(self) -> None:
		"""The bounding box is computed on every access: it follows a moved corner."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		corner =  polygon.Points[2]

		corner += (0, 2)

		self.assertTupleEqual((0, 0, 4, 5), polygon.BoundingBox.ToTuple())

	def test_PolyLine(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, -1), Point2D(5, 3), Point2D(-2, 5)))

		box = polyline.BoundingBox

		self.assertIs(BoundingBox2D, type(box))
		self.assertTupleEqual((-2, -1, 5, 5), box.ToTuple())

	def test_PolyLine_Line(self) -> None:
		"""A horizontal polyline has a bounding box without height."""
		polyline = PolyLine((Point2D(0, 1), Point2D(4, 1)))

		self.assertTupleEqual((0, 1, 4, 1), polyline.BoundingBox.ToTuple())

	def test_Trapezium(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		self.assertTupleEqual((0, 1, 4, 3), trapezium.BoundingBox.ToTuple())

	def test_Rectangle(self) -> None:
		"""A rectangle rotated against the axes: its bounding box is larger than the rectangle."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 2), Point2D(3, 4), Point2D(-1, 2))

		self.assertTupleEqual((-1, 0, 4, 4), rectangle.BoundingBox.ToTuple())

	def test_Circle(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertTupleEqual((-2, -1, 4, 5), circle.BoundingBox.ToTuple())

	def test_Ellipse(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		self.assertTupleEqual((-2, 0, 4, 4), ellipse.BoundingBox.ToTuple())

	def test_ReadOnly(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(AttributeError):
			circle.BoundingBox = BoundingBox2D(0, 0, 1, 1)


class Moving(Testcase):
	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		corners = polygon.Points

		polygon.Move(Offset2D(1, 2))

		for corner, newCorner in zip(corners, polygon.Points):
			self.assertIs(corner, newCorner)

		self.assertTupleEqual(((1, 2), (5, 2), (3, 5)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertTupleEqual(((1, 2), (5, 2)), polygon.Segments[0].ToTuple())

	def test_Polygon_None(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			polygon.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Polygon_tuple(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(TypeError) as context:
			polygon.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_PolyLine(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		vertices = polyline.Points

		polyline.Move(Offset2D(1, 2))

		for vertex, newVertex in zip(vertices, polyline.Points):
			self.assertIs(vertex, newVertex)

		self.assertTupleEqual(((1, 2), (5, 2), (3, 5)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertTupleEqual(((5, 2), (3, 5)), polyline.Segments[1].ToTuple())

	def test_PolyLine_None(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))

		with self.assertRaises(ValueError) as context:
			polyline.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_PolyLine_tuple(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))

		with self.assertRaises(TypeError) as context:
			polyline.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual(((0, 0), (4, 0)), tuple(point.ToTuple() for point in polyline.Points))

	def test_PolyLine_Edge(self) -> None:
		"""Moving an edge moves the polyline's points it references."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		polyline.Segments[1].Move(Offset2D(0, -1))

		self.assertTupleEqual(((0, 0), (4, -1), (2, 2)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertTupleEqual(((0, 0), (4, -1)), polyline.Segments[0].ToTuple())

	def test_Trapezium(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		trapezium.Move(Offset2D(-1, -1))

		self.assertTupleEqual(((0, 0), (2, 0), (3, 2), (-1, 2)), tuple(point.ToTuple() for point in trapezium.Points))
		self.assertTupleEqual(((-1, 2), (0, 0)), trapezium.Segments[3].ToTuple())

	def test_Trapezium_None(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		with self.assertRaises(ValueError) as context:
			trapezium.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Trapezium_tuple(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		with self.assertRaises(TypeError) as context:
			trapezium.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Square(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		square.Move(Offset2D(0.5, 1))

		self.assertTupleEqual((0.5, 1, 2.5, 3), square.BoundingBox.ToTuple())

	def test_Circle(self) -> None:
		circle = Circle(Point2D(1, 2), 3)
		center = circle.Center

		circle.Move(Offset2D(2, -2))

		self.assertIs(center, circle.Center)
		self.assertTupleEqual((3, 0), circle.Center.ToTuple())
		self.assertEqual(3, circle.Radius)

	def test_Circle_None(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(ValueError) as context:
			circle.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Circle_tuple(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError) as context:
			circle.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Ellipse(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)
		center =  ellipse.Center

		ellipse.Move(Offset2D(2, -2))

		self.assertIs(center, ellipse.Center)
		self.assertTupleEqual((3, 0), ellipse.Center.ToTuple())
		self.assertEqual(3, ellipse.RadiusX)
		self.assertEqual(2, ellipse.RadiusY)

	def test_Ellipse_None(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		with self.assertRaises(ValueError) as context:
			ellipse.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Ellipse_tuple(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		with self.assertRaises(TypeError) as context:
			ellipse.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())


class Mirroring(Testcase):
	def test_Polygon_MirrorY(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual(((0, 6), (4, 5), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertTupleEqual(((0, 6), (4, 5)), polygon.Segments[0].ToTuple())

	def test_Polygon_MirrorY_Default(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.MirrorY()

		self.assertTupleEqual(((0, 3), (4, 2), (2, 0)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertEqual(BoundingBox2D(0, 0, 4, 3), polygon.BoundingBox)

	def test_Polygon_MirrorY_Edge(self) -> None:
		"""An edge mirrors the polygon's corners it references."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.Segments[0].MirrorY(Alignment2D.MinY)

		self.assertTupleEqual(((0, 0), (4, -1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Polygon_MirrorY_AxisNone(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			polygon.MirrorY(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((0, 0), (4, 1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Polygon_MirrorX(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual(((0, 0), (-4, 1), (-2, 3)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertTupleEqual(((0, 0), (-4, 1)), polygon.Segments[0].ToTuple())

	def test_Polygon_MirrorX_Default(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.MirrorX()

		self.assertTupleEqual(((4, 0), (0, 1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertEqual(BoundingBox2D(0, 0, 4, 3), polygon.BoundingBox)

	def test_Polygon_MirrorX_Edge(self) -> None:
		"""An edge mirrors the polygon's corners it references."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polygon.Segments[1].MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual(((0, 0), (4, 1), (6, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Polygon_MirrorX_AxisMinY(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			polygon.MirrorX(Alignment2D.MinY)

		self.assertEqual(
			"Parameter 'axis' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.",
			str(context.exception)
		)
		self.assertListEqual(["Got value 'Alignment2D.MinY'."], context.exception.__notes__)
		self.assertTupleEqual(((0, 0), (4, 1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_PolyLine_MirrorY(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polyline.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual(((0, 6), (4, 5), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertTupleEqual(((0, 6), (4, 5)), polyline.Segments[0].ToTuple())

	def test_PolyLine_MirrorY_Default(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polyline.MirrorY()

		self.assertTupleEqual(((0, 3), (4, 2), (2, 0)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertEqual(BoundingBox2D(0, 0, 4, 3), polyline.BoundingBox)

	def test_PolyLine_MirrorY_AxisNone(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			polyline.MirrorY(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))
		self.assertTupleEqual(((0, 0), (4, 1), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))

	def test_PolyLine_MirrorX(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polyline.MirrorX(Alignment2D.MinX, 1)

		self.assertTupleEqual(((2, 0), (-2, 1), (0, 3)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertTupleEqual(((-2, 1), (0, 3)), polyline.Segments[1].ToTuple())

	def test_PolyLine_MirrorX_Default(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polyline.MirrorX()

		self.assertTupleEqual(((4, 0), (0, 1), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertEqual(BoundingBox2D(0, 0, 4, 3), polyline.BoundingBox)

	def test_PolyLine_MirrorX_Edge(self) -> None:
		"""An edge mirrors the polyline's points it references."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		polyline.Segments[1].MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual(((0, 0), (4, 1), (6, 3)), tuple(point.ToTuple() for point in polyline.Points))

	def test_PolyLine_MirrorX_AxisMinY(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			polyline.MirrorX(Alignment2D.MinY)

		self.assertEqual(
			"Parameter 'axis' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.",
			str(context.exception)
		)
		self.assertListEqual(["Got value 'Alignment2D.MinY'."], context.exception.__notes__)
		self.assertTupleEqual(((0, 0), (4, 1), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))

	def test_Trapezium_MirrorY(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		trapezium.MirrorY(Alignment2D.MinY, 1)

		self.assertTupleEqual(((1, 3), (3, 3), (4, 1), (0, 1)), tuple(point.ToTuple() for point in trapezium.Points))

	def test_Trapezium_MirrorY_OffsetStr(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		with self.assertRaises(TypeError) as context:
			trapezium.MirrorY(Alignment2D.MinY, "1")

		self.assertEqual("Parameter 'offset' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in trapezium.Points))

	def test_Trapezium_MirrorX(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		trapezium.MirrorX(Alignment2D.CenterX)

		self.assertTupleEqual(((3, 1), (1, 1), (0, 3), (4, 3)), tuple(point.ToTuple() for point in trapezium.Points))
		self.assertTupleEqual(((3, 1), (1, 1)), trapezium.Segments[0].ToTuple())

	def test_Trapezium_MirrorX_OffsetNone(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		with self.assertRaises(ValueError) as context:
			trapezium.MirrorX(Alignment2D.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in trapezium.Points))

	def test_Circle_MirrorY(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		circle.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual((1, 8), circle.Center.ToTuple())
		self.assertEqual(3, circle.Radius)

	def test_Circle_MirrorY_Default(self) -> None:
		"""A circle mirrored at its center stays in place."""
		circle = Circle(Point2D(1, 2), 3)

		circle.MirrorY()

		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Circle_MirrorY_AxisStr(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError) as context:
			circle.MirrorY("MaxY")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Circle_MirrorX(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		circle.MirrorX(Alignment2D.MaxX, 1)

		self.assertTupleEqual((9, 2), circle.Center.ToTuple())
		self.assertEqual(3, circle.Radius)

	def test_Circle_MirrorX_MinX(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		circle.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual((-5, 2), circle.Center.ToTuple())

	def test_Circle_MirrorX_AxisMaxY(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(ValueError) as context:
			circle.MirrorX(Alignment2D.MaxY)

		self.assertEqual(
			"Parameter 'axis' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.",
			str(context.exception)
		)
		self.assertListEqual(["Got value 'Alignment2D.MaxY'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Ellipse_MirrorY(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		ellipse.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual((1, 6), ellipse.Center.ToTuple())
		self.assertEqual(3, ellipse.RadiusX)
		self.assertEqual(2, ellipse.RadiusY)

	def test_Ellipse_MirrorY_Default(self) -> None:
		"""An ellipse mirrored at its center stays in place."""
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		ellipse.MirrorY()

		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())

	def test_Ellipse_MirrorY_AxisStr(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		with self.assertRaises(TypeError) as context:
			ellipse.MirrorY("MaxY")

		self.assertEqual("Parameter 'axis' is not of type 'Alignment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())

	def test_Ellipse_MirrorX(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		ellipse.MirrorX(Alignment2D.MaxX, 1)

		self.assertTupleEqual((9, 2), ellipse.Center.ToTuple())
		self.assertEqual(3, ellipse.RadiusX)
		self.assertEqual(2, ellipse.RadiusY)

	def test_Ellipse_MirrorX_MinX(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		ellipse.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual((-5, 2), ellipse.Center.ToTuple())

	def test_Ellipse_MirrorX_OffsetNone(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		with self.assertRaises(ValueError) as context:
			ellipse.MirrorX(Alignment2D.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())


class Ownership(Testcase):
	def test_Polygon(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polygon = Polygon(points)

		self.assertIsNone(polygon.Frame)
		for point in points:
			self.assertIsNone(point.Parent)

		for corner in polygon.Points:
			self.assertIs(polygon, corner.Parent)

	def test_Polygon_Edges(self) -> None:
		"""The edges are views: their parent is the polygon, which owns the corners."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		for segment in polygon.Segments:
			self.assertIs(polygon, segment.Parent)
			self.assertIs(polygon, segment.Start.Parent)
			self.assertIs(polygon, segment.End.Parent)

	def test_Polygon_Reference(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polygon = Polygon(points, copyPoints=False)

		for point in points:
			self.assertIs(polygon, point.Parent)

	def test_Polygon_Owned(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		point0 = Point2D(4, 0)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Polygon((point0, circle.Center, Point2D(2, 3)), copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 1) owned by Circle((1, 1), 1).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("An element of parameter 'points' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(circle, circle.Center.Parent)
		self.assertIsNone(point0.Parent)

	def test_Polygon_Owned_Copy(self) -> None:
		"""Owned points are fine to copy."""
		circle = Circle(Point2D(1, 1), 1)

		polygon = Polygon((Point2D(4, 0), circle.Center, Point2D(2, 3)))

		self.assertIs(circle, circle.Center.Parent)
		self.assertIs(polygon, polygon.Points[1].Parent)

	def test_Polygon_Twice(self) -> None:
		point = Point2D(0, 0)

		with self.assertRaises(DuplicatePointError) as context:
			_ = Polygon((point, Point2D(4, 0), point), copyPoints=False)

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(
			["Got point (0, 0).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("An element of parameter 'points' is given twice.", str(context.exception.__cause__))
		self.assertIsNone(point.Parent)

	def test_PolyLine(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polyline = PolyLine(points)

		self.assertIsNone(polyline.Frame)
		for point in points:
			self.assertIsNone(point.Parent)

		for vertex in polyline.Points:
			self.assertIs(polyline, vertex.Parent)

	def test_PolyLine_Edges(self) -> None:
		"""The edges are views: their parent is the polyline, which owns the points."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		for segment in polyline.Segments:
			self.assertIs(polyline, segment.Parent)
			self.assertIs(polyline, segment.Start.Parent)
			self.assertIs(polyline, segment.End.Parent)

	def test_PolyLine_Reference(self) -> None:
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		polyline = PolyLine(points, copyPoints=False)

		for point in points:
			self.assertIs(polyline, point.Parent)

	def test_PolyLine_Owned(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		point0 =  Point2D(5, 5)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = PolyLine((point0, polygon.Points[1]), copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (4, 0) owned by Polygon((0, 0), (4, 0), (2, 3)).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("An element of parameter 'points' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(polygon, polygon.Points[1].Parent)
		self.assertIsNone(point0.Parent)

	def test_PolyLine_Owned_Copy(self) -> None:
		"""Owned points are fine to copy."""
		circle = Circle(Point2D(1, 1), 1)

		polyline = PolyLine((Point2D(4, 0), circle.Center))

		self.assertIs(circle, circle.Center.Parent)
		self.assertIs(polyline, polyline.Points[1].Parent)

	def test_PolyLine_Twice(self) -> None:
		point = Point2D(0, 0)

		with self.assertRaises(DuplicatePointError) as context:
			_ = PolyLine((point, Point2D(4, 0), point), copyPoints=False)

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(
			["Got point (0, 0).", "Use 'copyPoints=True' to copy the points."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("An element of parameter 'points' is given twice.", str(context.exception.__cause__))
		self.assertIsNone(point.Parent)

	def test_PolyLine_Copy(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolyLine = polyline.Copy()

		for vertex in newPolyLine.Points:
			self.assertIs(newPolyLine, vertex.Parent)

		for vertex in polyline.Points:
			self.assertIs(polyline, vertex.Parent)

	def test_PolyLine_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), False)

	def test_PolyLine_Edge_Start(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))
		edge =     polyline.Segments[0]
		start =    edge.Start

		with self.assertRaises(NotOwnedError) as context:
			edge.Start = Point2D(1, 1)

		self.assertEqual("Segment doesn't own its start point.", str(context.exception))
		self.assertListEqual(
			["The segment is an edge of PolyLine((0, 0), (4, 0)), which owns the point."],
			context.exception.__notes__
		)
		self.assertIs(start, edge.Start)

	def test_Trapezium(self) -> None:
		point00 = Point2D(1, 1)

		trapezium = Trapezium(point00, Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		self.assertIsNone(point00.Parent)
		for corner in trapezium.Points:
			self.assertIs(trapezium, corner.Parent)

		for segment in trapezium.Segments:
			self.assertIs(trapezium, segment.Parent)

	def test_Trapezium_points(self) -> None:
		"""The deprecated setter takes ownership of the assigned points and releases the previous corners."""
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		previous =  trapezium.Points
		corners =   (Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		trapezium.points = corners

		for corner in corners:
			self.assertIs(trapezium, corner.Parent)

		for corner in previous:
			self.assertIsNone(corner.Parent)

	def test_Trapezium_points_Reordered(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		corners =   tuple(reversed(trapezium.Points))

		trapezium.points = corners

		self.assertTupleEqual(((0, 3), (4, 3), (3, 1), (1, 1)), tuple(point.ToTuple() for point in trapezium.Points))
		for corner in corners:
			self.assertIs(trapezium, corner.Parent)

	def test_Trapezium_points_Owned(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		circle =    Circle(Point2D(1, 1), 1)
		previous =  trapezium.Points

		with self.assertRaises(AlreadyOwnedError) as context:
			trapezium.points = (Point2D(0, 0), circle.Center, Point2D(2, 2), Point2D(0, 2))

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(["Got point (1, 1) owned by Circle((1, 1), 1)."], context.exception.__notes__)
		self.assertEqual("An element of parameter 'points' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(previous, trapezium.Points)

	def test_Trapezium_points_Twice(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		point =     Point2D(0, 0)

		with self.assertRaises(DuplicatePointError) as context:
			trapezium.points = (point, Point2D(2, 0), point, Point2D(0, 2))

		self.assertEqual("Point is given twice.", str(context.exception))
		self.assertListEqual(["Got point (0, 0)."], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("An element of parameter 'points' is given twice.", str(context.exception.__cause__))
		self.assertIsNone(point.Parent)

	def test_Circle(self) -> None:
		center = Point2D(1, 2)

		circle = Circle(center, 3)

		self.assertIsNone(center.Parent)
		self.assertIs(circle, circle.Center.Parent)

	def test_Circle_Reference(self) -> None:
		center = Point2D(1, 2)

		circle = Circle(center, 3, copyPoints=False)

		self.assertIs(circle, center.Parent)

	def test_Circle_Reference_Failing(self) -> None:
		"""A failing radius check doesn't take ownership of the given center."""
		center = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			_ = Circle(center, 0, copyPoints=False)

		self.assertEqual("Parameter 'radius' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)
		self.assertIsNone(center.Parent)

	def test_Circle_Owned(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Circle(polygon.Points[2], 1, copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (2, 3) owned by Polygon((0, 0), (4, 0), (2, 3)).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'center' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(polygon, polygon.Points[2].Parent)

	def test_Ellipse(self) -> None:
		center = Point2D(1, 2)

		ellipse = Ellipse(center, 3, 2)

		self.assertIsNone(center.Parent)
		self.assertIs(ellipse, ellipse.Center.Parent)

	def test_Ellipse_Reference(self) -> None:
		center = Point2D(1, 2)

		ellipse = Ellipse(center, 3, 2, copyPoints=False)

		self.assertIs(ellipse, center.Parent)

	def test_Ellipse_Reference_Failing(self) -> None:
		"""A failing radius check doesn't take ownership of the given center."""
		center = Point2D(1, 2)

		with self.assertRaises(ValueError) as context:
			_ = Ellipse(center, 3, 0, copyPoints=False)

		self.assertEqual("Parameter 'radiusY' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)
		self.assertIsNone(center.Parent)

	def test_Ellipse_Owned(self) -> None:
		circle = Circle(Point2D(1, 1), 1)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Ellipse(circle.Center, 3, 2, copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (1, 1) owned by Circle((1, 1), 1).", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'center' is owned by another element.", str(context.exception.__cause__))
		self.assertIs(circle, circle.Center.Parent)

	def test_Ellipse_Owned_Copy(self) -> None:
		"""An owned center is fine to copy."""
		circle = Circle(Point2D(1, 1), 1)

		ellipse = Ellipse(circle.Center, 3, 2)

		self.assertIs(circle, circle.Center.Parent)
		self.assertIs(ellipse, ellipse.Center.Parent)

	def test_Copy(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolygon = polygon.Copy()

		for corner in newPolygon.Points:
			self.assertIs(newPolygon, corner.Parent)

		for corner in polygon.Points:
			self.assertIs(polygon, corner.Parent)

	def test_Edge(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		edge = LineSegment2D(polygon.Points[0], polygon.Points[2], copyPoints=False, parent=polygon)

		self.assertIs(polygon, edge.Parent)
		self.assertIs(polygon, edge.Start.Parent)
		self.assertEqual(3, len(polygon.Segments))

	def test_Polygon_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), False)

	def test_Circle_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Circle(Point2D(1, 2), 3, False)

	def test_Ellipse_copyPointsPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Ellipse(Point2D(1, 2), 3, 2, False)

	def test_Edge_copyPoints(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(ValueError) as context:
			_ = LineSegment2D(polygon.Points[0], polygon.Points[2], parent=polygon)

		self.assertEqual("Parameter 'parent' is a shape, while 'copyPoints' is True.", str(context.exception))
		self.assertListEqual(
			["An edge references the points of its parent shape: use 'copyPoints=False'."],
			context.exception.__notes__
		)

	def test_Edge_NotOwned(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		start =   Point2D(0, 0)

		with self.assertRaises(NotOwnedError) as context:
			_ = LineSegment2D(start, polygon.Points[2], copyPoints=False, parent=polygon)

		self.assertEqual("Point isn't owned by the parent shape.", str(context.exception))
		self.assertListEqual(["Got point (0, 0) owned by None."], context.exception.__notes__)
		self.assertEqual("Parameter 'start' isn't owned by parameter 'parent'.", str(context.exception.__cause__))
		self.assertIsNone(start.Parent)

	def test_Edge_Start(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		edge =    polygon.Segments[0]
		start =   edge.Start

		with self.assertRaises(NotOwnedError) as context:
			edge.Start = Point2D(1, 1)

		self.assertEqual("Segment doesn't own its start point.", str(context.exception))
		self.assertListEqual(
			["The segment is an edge of Polygon((0, 0), (4, 0), (2, 3)), which owns the point."],
			context.exception.__notes__
		)
		self.assertIs(start, edge.Start)

	def test_Edge_End(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		edge =    polygon.Segments[0]
		end =     edge.End

		with self.assertRaises(NotOwnedError) as context:
			edge.End = Point2D(1, 1)

		self.assertEqual("Segment doesn't own its end point.", str(context.exception))
		self.assertIs(end, edge.End)

	def test_Edge_Move(self) -> None:
		"""Moving an edge moves the polygon's corners it references."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		polygon.Segments[0].Move(Offset2D(0, -1))

		self.assertTupleEqual(((0, -1), (4, -1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))


class Hashing(Testcase):
	"""Points, segments and shapes define no ``__eq__``: they hash by identity."""

	def test_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(1, 2)

		points = {point1, point2}

		self.assertEqual(2, len(points))
		self.assertIn(point1, points)
		self.assertIn(point2, points)

	def test_LineSegment(self) -> None:
		self.assertEqual(2, len({
			LineSegment2D(Point2D(1, 2), Point2D(4, 6)),
			LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		}))

	def test_Polygon(self) -> None:
		self.assertEqual(2, len({
			Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))),
			Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		}))

	def test_PolyLine(self) -> None:
		self.assertEqual(2, len({
			PolyLine((Point2D(0, 0), Point2D(4, 0))),
			PolyLine((Point2D(0, 0), Point2D(4, 0)))
		}))

	def test_Trapezium(self) -> None:
		self.assertEqual(2, len({
			Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3)),
			Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))
		}))

	def test_Rectangle(self) -> None:
		self.assertEqual(2, len({
			Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2)),
			Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		}))

	def test_Square(self) -> None:
		self.assertEqual(2, len({
			Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2)),
			Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))
		}))

	def test_Circle(self) -> None:
		self.assertEqual(2, len({Circle(Point2D(1, 2), 3), Circle(Point2D(1, 2), 3)}))

	def test_Ellipse(self) -> None:
		self.assertEqual(2, len({Ellipse(Point2D(1, 2), 3, 2), Ellipse(Point2D(1, 2), 3, 2)}))

	def test_Offset2D(self) -> None:
		"""An offset compares by value, so it isn't hashable."""
		with self.assertRaises(TypeError):
			_ = hash(Offset2D(1, 2))

	def test_BoundingBox(self) -> None:
		"""A bounding box compares by value, so it isn't hashable."""
		with self.assertRaises(TypeError):
			_ = hash(BoundingBox2D(0, 0, 1, 1))


class Frames(Testcase):
	def test_Point(self) -> None:
		frame =   Group2D()
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=frame)

		for corner in polygon.Points:
			self.assertIs(frame, corner.Frame)

		for segment in polygon.Segments:
			self.assertIs(frame, segment.Frame)

	def test_Point_Minus_Point(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=Group2D())

		offset = polygon.Points[2] - polygon.Points[0]

		self.assertTupleEqual((2, 3), offset.ToTuple())

	def test_Point_Minus_Point_OtherFrame(self) -> None:
		polygon1 = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=Group2D())
		polygon2 = Polygon((Point2D(1, 1), Point2D(5, 1), Point2D(3, 4)), parent=Group2D())

		with self.assertRaises(NotInSameFrameError) as context:
			_ = polygon2.Points[0] - polygon1.Points[0]

		self.assertEqual("Points are in different frames.", str(context.exception))
		self.assertListEqual(
			["Got points (1, 1) and (0, 0).", "Subtract the points' 'Absolute' positions instead."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual("Parameter 'other' is in another frame.", str(context.exception.__cause__))

	def test_Point_Minus_Point_NoFrame(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=Group2D())

		with self.assertRaises(NotInSameFrameError):
			_ = polygon.Points[0] - Point2D(1, 1)

	def test_AngleTo_OtherFrame(self) -> None:
		polygon1 = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=Group2D())
		polygon2 = Polygon((Point2D(1, 1), Point2D(5, 1), Point2D(3, 4)), parent=Group2D())

		with self.assertRaises(NotInSameFrameError) as context:
			_ = polygon1.Segments[0].AngleTo(polygon2.Segments[0])

		self.assertEqual("Line segments are in different frames.", str(context.exception))
		self.assertListEqual(["Got line segments ((0, 0) → (4, 0)) and ((1, 1) → (5, 1))."], context.exception.__notes__)
		self.assertEqual("Parameter 'other' is in another frame.", str(context.exception.__cause__))

	def test_AngleTo_SameFrame(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), parent=Group2D())

		angle = polygon.Segments[0].AngleTo(polygon.Segments[1])

		self.assertTrue(isclose(pi / 2, angle))


class FramedPoints(Testcase):
	def test_Parent(self) -> None:
		"""A point with a shape as parent is in the shape's frame, but not one of its points."""
		frame =   Group2D()
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=frame)

		point = Point2D(1, 1, parent=polygon)

		self.assertIs(polygon, point.Parent)
		self.assertIs(frame, point.Frame)
		self.assertEqual(3, len(polygon.Points))
		self.assertTupleEqual((1, 1), (point - polygon.Points[0]).ToTuple())


class Copy(Testcase):
	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5), Point2D(-1, 3)))

		newPolygon =   polygon.Copy()
		movedCorner =  newPolygon.Points[0]
		movedCorner += (1, 1)

		self.assertIs(Polygon, type(newPolygon))
		self.assertIsNot(polygon, newPolygon)
		for corner, newCorner in zip(polygon.Points, newPolygon.Points):
			self.assertIsNot(corner, newCorner)

		self.assertTupleEqual((0, 0), polygon.Points[0].ToTuple())
		self.assertTupleEqual((1, 1), newPolygon.Points[0].ToTuple())

	def test_Polygon_SharedCorners(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5), Point2D(-1, 3)))

		newPolygon = polygon.Copy()

		points = newPolygon.Points
		for index, segment in enumerate(newPolygon.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[(index + 1) % len(points)], segment.End)

	def test_Polygon_copy(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolygon = copy(polygon)

		self.assertIs(Polygon, type(newPolygon))
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in newPolygon.Points))
		for corner, newCorner in zip(polygon.Points, newPolygon.Points):
			self.assertIsNot(corner, newCorner)

	def test_Polygon_deepcopy(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolygon = deepcopy(polygon)

		self.assertIs(Polygon, type(newPolygon))
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in newPolygon.Points))
		for corner, newCorner in zip(polygon.Points, newPolygon.Points):
			self.assertIsNot(corner, newCorner)

		points = newPolygon.Points
		for index, segment in enumerate(newPolygon.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[(index + 1) % len(points)], segment.End)

	def test_Polygon_deepcopy_Group(self) -> None:
		"""A deep copy owns its corners and isn't in the group of the original."""
		group =   Group2D()
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=group)

		newPolygon = deepcopy(polygon)

		self.assertIs(Polygon, type(newPolygon))
		self.assertIsNone(newPolygon.Parent)
		for corner in newPolygon.Points:
			self.assertIs(newPolygon, corner.Parent)

		for segment in newPolygon.Segments:
			self.assertIs(newPolygon, segment.Parent)

		self.assertTupleEqual((polygon, ), group.Children)

	def test_PolyLine(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5)))

		newPolyLine = polyline.Copy()
		movedVertex = newPolyLine.Points[0]
		movedVertex += (1, 1)

		self.assertIs(PolyLine, type(newPolyLine))
		self.assertIsNot(polyline, newPolyLine)
		for vertex, newVertex in zip(polyline.Points, newPolyLine.Points):
			self.assertIsNot(vertex, newVertex)

		self.assertEqual(3, len(newPolyLine.Segments))
		self.assertTupleEqual((0, 0), polyline.Points[0].ToTuple())
		self.assertTupleEqual((1, 1), newPolyLine.Points[0].ToTuple())

	def test_PolyLine_SharedPoints(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(5, 3), Point2D(2, 5)))

		newPolyLine = polyline.Copy()

		points = newPolyLine.Points
		for index, segment in enumerate(newPolyLine.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[index + 1], segment.End)

	def test_PolyLine_copy(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolyLine = copy(polyline)

		self.assertIs(PolyLine, type(newPolyLine))
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in newPolyLine.Points))
		for vertex, newVertex in zip(polyline.Points, newPolyLine.Points):
			self.assertIsNot(vertex, newVertex)

	def test_PolyLine_deepcopy(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		newPolyLine = deepcopy(polyline)

		self.assertIs(PolyLine, type(newPolyLine))
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in newPolyLine.Points))
		for vertex, newVertex in zip(polyline.Points, newPolyLine.Points):
			self.assertIsNot(vertex, newVertex)

		points = newPolyLine.Points
		for index, segment in enumerate(newPolyLine.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[index + 1], segment.End)

	def test_Trapezium(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		newTrapezium = trapezium.Copy()
		movedCorner =  newTrapezium.Points[0]
		movedCorner += (1, 1)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIsNot(trapezium, newTrapezium)
		for corner, newCorner in zip(trapezium.Points, newTrapezium.Points):
			self.assertIsNot(corner, newCorner)

		self.assertTupleEqual((1, 1), trapezium.Points[0].ToTuple())
		self.assertTupleEqual((2, 2), newTrapezium.Points[0].ToTuple())

	def test_Trapezium_SharedCorners(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		newTrapezium = trapezium.Copy()

		points = newTrapezium.Points
		for index, segment in enumerate(newTrapezium.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[(index + 1) % 4], segment.End)

	def test_Trapezium_copy(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		newTrapezium = copy(trapezium)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in newTrapezium.Points))
		for corner, newCorner in zip(trapezium.Points, newTrapezium.Points):
			self.assertIsNot(corner, newCorner)

	def test_Trapezium_deepcopy(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		newTrapezium = deepcopy(trapezium)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertTupleEqual(((1, 1), (3, 1), (4, 3), (0, 3)), tuple(point.ToTuple() for point in newTrapezium.Points))
		for corner, newCorner in zip(trapezium.Points, newTrapezium.Points):
			self.assertIsNot(corner, newCorner)

		points = newTrapezium.Points
		for index, segment in enumerate(newTrapezium.Segments):
			self.assertIs(points[index], segment.Start)
			self.assertIs(points[(index + 1) % 4], segment.End)

	def test_Trapezium_deepcopy_Group(self) -> None:
		"""A deep copy owns its corners and isn't in the group of the original."""
		group =     Group2D()
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), parent=group)

		newTrapezium = deepcopy(trapezium)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIsNone(newTrapezium.Parent)
		for corner in newTrapezium.Points:
			self.assertIs(newTrapezium, corner.Parent)

		self.assertTupleEqual((trapezium, ), group.Children)

	def test_Rectangle(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		newRectangle = rectangle.Copy()

		self.assertIs(Rectangle, type(newRectangle))
		self.assertTupleEqual(((0, 0), (4, 0), (4, 2), (0, 2)), tuple(point.ToTuple() for point in newRectangle.Points))

	def test_Rectangle_copy(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		newRectangle = copy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertTupleEqual(((0, 0), (4, 0), (4, 2), (0, 2)), tuple(point.ToTuple() for point in newRectangle.Points))

	def test_Rectangle_deepcopy(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		newRectangle = deepcopy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertTupleEqual(((0, 0), (4, 0), (4, 2), (0, 2)), tuple(point.ToTuple() for point in newRectangle.Points))

	def test_Rectangle_deepcopy_Group(self) -> None:
		"""A deep copy owns its corners and isn't in the group of the original."""
		group =     Group2D()
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=group)

		newRectangle = deepcopy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIsNone(newRectangle.Parent)
		for corner in newRectangle.Points:
			self.assertIs(newRectangle, corner.Parent)

		self.assertTupleEqual((rectangle, ), group.Children)

	def test_Rectangle_MovedCorner(self) -> None:
		"""A copy checks the corners again: a rectangle whose corner was moved isn't a rectangle anymore."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		corner =    rectangle.Points[2]
		corner +=   (1, 0)

		with self.assertRaises(ValueError):
			_ = rectangle.Copy()

	def test_Square(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		newSquare = square.Copy()

		self.assertIs(Square, type(newSquare))
		self.assertTupleEqual(((0, 0), (2, 0), (2, 2), (0, 2)), tuple(point.ToTuple() for point in newSquare.Points))

	def test_Square_copy(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		newSquare = copy(square)

		self.assertIs(Square, type(newSquare))
		self.assertTupleEqual(((0, 0), (2, 0), (2, 2), (0, 2)), tuple(point.ToTuple() for point in newSquare.Points))

	def test_Square_deepcopy(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		newSquare = deepcopy(square)

		self.assertIs(Square, type(newSquare))
		self.assertTupleEqual(((0, 0), (2, 0), (2, 2), (0, 2)), tuple(point.ToTuple() for point in newSquare.Points))

	def test_Square_deepcopy_Group(self) -> None:
		"""A deep copy owns its corners and isn't in the group of the original."""
		group =  Group2D()
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), parent=group)

		newSquare = deepcopy(square)

		self.assertIs(Square, type(newSquare))
		self.assertIsNone(newSquare.Parent)
		for corner in newSquare.Points:
			self.assertIs(newSquare, corner.Parent)

		self.assertTupleEqual((square, ), group.Children)

	def test_Circle(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		newCircle =  circle.Copy()
		newCenter =  newCircle.Center
		newCenter += (1, 1)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNot(circle, newCircle)
		self.assertIsNot(circle.Center, newCircle.Center)
		self.assertEqual(3, newCircle.Radius)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())
		self.assertTupleEqual((2, 3), newCircle.Center.ToTuple())

	def test_Circle_copy(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		newCircle = copy(circle)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNot(circle.Center, newCircle.Center)
		self.assertEqual(3, newCircle.Radius)
		self.assertTupleEqual((1, 2), newCircle.Center.ToTuple())

	def test_Circle_deepcopy(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		newCircle = deepcopy(circle)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNot(circle.Center, newCircle.Center)
		self.assertEqual(3, newCircle.Radius)
		self.assertTupleEqual((1, 2), newCircle.Center.ToTuple())

	def test_Circle_deepcopy_Group(self) -> None:
		"""A deep copy owns its center and isn't in the group of the original."""
		group =  Group2D()
		circle = Circle(Point2D(1, 2), 3, parent=group)

		newCircle = deepcopy(circle)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNone(newCircle.Parent)
		self.assertIs(newCircle, newCircle.Center.Parent)
		self.assertTupleEqual((circle, ), group.Children)

	def test_Ellipse(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		newEllipse = ellipse.Copy()
		newCenter =  newEllipse.Center
		newCenter += (1, 1)

		self.assertIs(Ellipse, type(newEllipse))
		self.assertIsNot(ellipse, newEllipse)
		self.assertIsNot(ellipse.Center, newEllipse.Center)
		self.assertIs(newEllipse, newEllipse.Center.Parent)
		self.assertEqual(3, newEllipse.RadiusX)
		self.assertEqual(2, newEllipse.RadiusY)
		self.assertTupleEqual((1, 2), ellipse.Center.ToTuple())
		self.assertTupleEqual((2, 3), newEllipse.Center.ToTuple())

	def test_Ellipse_copy(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		newEllipse = copy(ellipse)

		self.assertIs(Ellipse, type(newEllipse))
		self.assertIsNot(ellipse.Center, newEllipse.Center)
		self.assertEqual(3, newEllipse.RadiusX)
		self.assertEqual(2, newEllipse.RadiusY)
		self.assertTupleEqual((1, 2), newEllipse.Center.ToTuple())

	def test_Ellipse_deepcopy(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		newEllipse = deepcopy(ellipse)

		self.assertIs(Ellipse, type(newEllipse))
		self.assertIsNot(ellipse.Center, newEllipse.Center)
		self.assertEqual(3, newEllipse.RadiusX)
		self.assertEqual(2, newEllipse.RadiusY)
		self.assertTupleEqual((1, 2), newEllipse.Center.ToTuple())

	def test_Ellipse_deepcopy_Group(self) -> None:
		"""A deep copy owns its center and isn't in the group of the original."""
		group =   Group2D()
		ellipse = Ellipse(Point2D(1, 2), 3, 2, parent=group)

		newEllipse = deepcopy(ellipse)

		self.assertIs(Ellipse, type(newEllipse))
		self.assertIsNone(newEllipse.Parent)
		self.assertIs(newEllipse, newEllipse.Center.Parent)
		self.assertTupleEqual((ellipse, ), group.Children)


class Representation(Testcase):
	def test_Trapezium_repr(self) -> None:
		trapezium = Trapezium(Point2D(0, 0), Point2D(6, 0), Point2D(4, 2), Point2D(1, 2))

		self.assertEqual("Trapezium((0, 0), (6, 0), (4, 2), (1, 2))", repr(trapezium))

	def test_Rectangle_str(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		self.assertEqual("((0, 0) → (4, 0) → (4, 2) → (0, 2) → (0, 0))", str(rectangle))

	def test_Polygon_repr(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("Polygon((0, 0), (4, 0), (2, 3))", repr(polygon))

	def test_Polygon_str(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("((0, 0) → (4, 0) → (2, 3) → (0, 0))", str(polygon))

	def test_PolyLine_repr(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("PolyLine((0, 0), (4, 0), (2, 3))", repr(polyline))

	def test_PolyLine_str(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertEqual("((0, 0) → (4, 0) → (2, 3))", str(polyline))

	def test_Circle_repr(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		self.assertEqual("Circle((1, 2), 3)", repr(circle))

	def test_Circle_str(self) -> None:
		circle = Circle(Point2D(1.5, 2), 0.5)

		self.assertEqual("((1.5, 2), r=0.5)", str(circle))

	def test_Ellipse_repr(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		self.assertEqual("Ellipse((1, 2), 3, 2)", repr(ellipse))

	def test_Ellipse_str(self) -> None:
		ellipse = Ellipse(Point2D(1.5, 2), 0.5, 1.25)

		self.assertEqual("((1.5, 2), rx=0.5, ry=1.25)", str(ellipse))


class ElementData(Testcase):
	def test_Polygon(self) -> None:
		value =   object()
		pairs =   {"layer": 1}
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=value, keyValuePairs=pairs)

		self.assertIs(value, polygon.Value)
		self.assertEqual(1, polygon["layer"])
		self.assertIsNot(pairs, polygon._dict)

	def test_Polygon_Default(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertIsNone(polygon.Value)
		self.assertEqual(0, len(polygon))

	def test_Polygon_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Polygon_Value(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=1)

		polygon.Value = "triangle"

		self.assertEqual("triangle", polygon.Value)

	def test_Polygon_Pairs(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		polygon["layer"] = 1

		self.assertEqual(1, len(polygon))
		self.assertIn("layer", polygon)
		self.assertEqual(1, polygon.get("layer"))
		self.assertListEqual(["layer"], list(polygon))

		del polygon["layer"]

		self.assertNotIn("layer", polygon)

	def test_Polygon_Copy(self) -> None:
		value =   [1, 2]
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=value, keyValuePairs={"layer": 1})

		newPolygon =          polygon.Copy()
		newPolygon["layer"] = 2

		self.assertIs(value, newPolygon.Value)
		self.assertEqual(1, polygon["layer"])
		self.assertEqual(2, newPolygon["layer"])

	def test_Polygon_copy(self) -> None:
		value =   [1, 2]
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=value, keyValuePairs={"layer": 1})

		newPolygon = copy(polygon)

		self.assertIs(value, newPolygon.Value)
		self.assertEqual(1, newPolygon["layer"])
		self.assertIsNot(polygon._dict, newPolygon._dict)

	def test_Polygon_deepcopy(self) -> None:
		value =   [1, 2]
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=value, keyValuePairs={"nets": ["a"]})

		newPolygon = deepcopy(polygon)

		self.assertIsNot(value, newPolygon.Value)
		self.assertListEqual([1, 2], newPolygon.Value)
		self.assertIsNot(polygon["nets"], newPolygon["nets"])

	def test_PolyLine(self) -> None:
		value =    object()
		pairs =    {"layer": 1}
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=value, keyValuePairs=pairs)

		self.assertIs(value, polyline.Value)
		self.assertEqual(1, polyline["layer"])
		self.assertIsNot(pairs, polyline._dict)

	def test_PolyLine_Default(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)))

		self.assertIsNone(polyline.Value)
		self.assertEqual(0, len(polyline))

	def test_PolyLine_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_PolyLine_Value(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)), value=1)

		polyline.Value = "wire"

		self.assertEqual("wire", polyline.Value)

	def test_PolyLine_Pairs(self) -> None:
		"""The dictionary syntax addresses the key-value-pairs, not the points."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		polyline["layer"] = 1

		self.assertEqual(1, len(polyline))
		self.assertIn("layer", polyline)
		self.assertListEqual(["layer"], list(polyline))
		self.assertEqual(3, len(polyline.Points))

		del polyline["layer"]

		self.assertNotIn("layer", polyline)

	def test_PolyLine_Copy(self) -> None:
		value =    [1, 2]
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)), value=value, keyValuePairs={"layer": 1})

		newPolyLine =          polyline.Copy()
		newPolyLine["layer"] = 2

		self.assertIs(value, newPolyLine.Value)
		self.assertEqual(1, polyline["layer"])
		self.assertEqual(2, newPolyLine["layer"])

	def test_PolyLine_copy(self) -> None:
		value =    [1, 2]
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)), value=value, keyValuePairs={"layer": 1})

		newPolyLine = copy(polyline)

		self.assertIs(value, newPolyLine.Value)
		self.assertEqual(1, newPolyLine["layer"])
		self.assertIsNot(polyline._dict, newPolyLine._dict)

	def test_PolyLine_deepcopy(self) -> None:
		value =    [1, 2]
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0)), value=value, keyValuePairs={"nets": ["a"]})

		newPolyLine = deepcopy(polyline)

		self.assertIsNot(value, newPolyLine.Value)
		self.assertListEqual([1, 2], newPolyLine.Value)
		self.assertIsNot(polyline["nets"], newPolyLine["nets"])

	def test_PolyLine_Edges(self) -> None:
		"""The edges of a polyline carry no value and no key-value-pairs of their own."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=1, keyValuePairs={"layer": 1})

		for segment in polyline.Segments:
			self.assertIsNone(segment.Value)
			self.assertEqual(0, len(segment))

	def test_Trapezium(self) -> None:
		value =     object()
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			value=value,
			keyValuePairs={"layer": 1}
		)

		self.assertIs(value, trapezium.Value)
		self.assertEqual(1, trapezium["layer"])

	def test_Trapezium_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Trapezium_Value(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3))

		trapezium.Value =    "trapezium"
		trapezium["layer"] = 1

		self.assertEqual("trapezium", trapezium.Value)
		self.assertEqual(1, len(trapezium))

	def test_Trapezium_Copy(self) -> None:
		value =     [1, 2]
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			value=value,
			keyValuePairs={"layer": 1}
		)

		newTrapezium =          trapezium.Copy()
		newTrapezium["layer"] = 2

		self.assertIs(value, newTrapezium.Value)
		self.assertEqual(1, trapezium["layer"])
		self.assertEqual(2, newTrapezium["layer"])

	def test_Trapezium_deepcopy(self) -> None:
		value =     [1, 2]
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			value=value,
			keyValuePairs={"nets": ["a"]}
		)

		newTrapezium = deepcopy(trapezium)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIsNot(value, newTrapezium.Value)
		self.assertListEqual([1, 2], newTrapezium.Value)
		self.assertIsNot(trapezium["nets"], newTrapezium["nets"])
		self.assertListEqual(["a"], newTrapezium["nets"])

	def test_Rectangle(self) -> None:
		value =     object()
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"layer": 1}
		)

		self.assertIs(value, rectangle.Value)
		self.assertEqual(1, rectangle["layer"])

	def test_Rectangle_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Rectangle_Value(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		rectangle.Value =    "rectangle"
		rectangle["layer"] = 1

		self.assertEqual("rectangle", rectangle.Value)
		self.assertEqual(1, len(rectangle))

	def test_Rectangle_Copy(self) -> None:
		value =     [1, 2]
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"layer": 1}
		)

		newRectangle =          rectangle.Copy()
		newRectangle["layer"] = 2

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIs(value, newRectangle.Value)
		self.assertEqual(1, rectangle["layer"])
		self.assertEqual(2, newRectangle["layer"])

	def test_Rectangle_deepcopy(self) -> None:
		value =     [1, 2]
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"nets": ["a"]}
		)

		newRectangle = deepcopy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIsNot(value, newRectangle.Value)
		self.assertListEqual([1, 2], newRectangle.Value)
		self.assertIsNot(rectangle["nets"], newRectangle["nets"])
		self.assertListEqual(["a"], newRectangle["nets"])

	def test_Square(self) -> None:
		value =  object()
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"layer": 1}
		)

		self.assertIs(value, square.Value)
		self.assertEqual(1, square["layer"])

	def test_Square_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Square_Value(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2))

		square.Value =    "square"
		square["layer"] = 1

		self.assertEqual("square", square.Value)
		self.assertEqual(1, len(square))

	def test_Square_Copy(self) -> None:
		value =  [1, 2]
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"layer": 1}
		)

		newSquare =          square.Copy()
		newSquare["layer"] = 2

		self.assertIs(Square, type(newSquare))
		self.assertIs(value, newSquare.Value)
		self.assertEqual(1, square["layer"])
		self.assertEqual(2, newSquare["layer"])

	def test_Square_deepcopy(self) -> None:
		value =  [1, 2]
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			value=value,
			keyValuePairs={"nets": ["a"]}
		)

		newSquare = deepcopy(square)

		self.assertIs(Square, type(newSquare))
		self.assertIsNot(value, newSquare.Value)
		self.assertListEqual([1, 2], newSquare.Value)
		self.assertIsNot(square["nets"], newSquare["nets"])
		self.assertListEqual(["a"], newSquare["nets"])

	def test_Circle(self) -> None:
		value =  object()
		circle = Circle(Point2D(1, 2), 3, value=value, keyValuePairs={"layer": 1})

		self.assertIs(value, circle.Value)
		self.assertEqual(1, circle["layer"])

	def test_Circle_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), 3, keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Circle_Value(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		circle.Value =    "circle"
		circle["layer"] = 1

		self.assertEqual("circle", circle.Value)
		self.assertEqual(1, len(circle))

	def test_Circle_Copy(self) -> None:
		value =  [1, 2]
		circle = Circle(Point2D(1, 2), 3, value=value, keyValuePairs={"layer": 1})

		newCircle =          circle.Copy()
		newCircle["layer"] = 2

		self.assertIs(value, newCircle.Value)
		self.assertEqual(1, circle["layer"])
		self.assertEqual(2, newCircle["layer"])

	def test_Circle_copy(self) -> None:
		value =  [1, 2]
		circle = Circle(Point2D(1, 2), 3, value=value, keyValuePairs={"layer": 1})

		newCircle = copy(circle)

		self.assertIs(value, newCircle.Value)
		self.assertIsNot(circle._dict, newCircle._dict)

	def test_Circle_deepcopy(self) -> None:
		value =  [1, 2]
		circle = Circle(Point2D(1, 2), 3, value=value, keyValuePairs={"nets": ["a"]})

		newCircle = deepcopy(circle)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNot(value, newCircle.Value)
		self.assertListEqual([1, 2], newCircle.Value)
		self.assertIsNot(circle["nets"], newCircle["nets"])
		self.assertListEqual(["a"], newCircle["nets"])

	def test_Ellipse(self) -> None:
		value =   object()
		ellipse = Ellipse(Point2D(1, 2), 3, 2, value=value, keyValuePairs={"layer": 1})

		self.assertIs(value, ellipse.Value)
		self.assertEqual(1, ellipse["layer"])

	def test_Ellipse_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Ellipse(Point2D(1, 2), 3, 2, keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Ellipse_Value(self) -> None:
		ellipse = Ellipse(Point2D(1, 2), 3, 2)

		ellipse.Value =    "ellipse"
		ellipse["layer"] = 1

		self.assertEqual("ellipse", ellipse.Value)
		self.assertEqual(1, len(ellipse))

	def test_Ellipse_Copy(self) -> None:
		value =   [1, 2]
		ellipse = Ellipse(Point2D(1, 2), 3, 2, value=value, keyValuePairs={"layer": 1})

		newEllipse =          ellipse.Copy()
		newEllipse["layer"] = 2

		self.assertIs(value, newEllipse.Value)
		self.assertEqual(1, ellipse["layer"])
		self.assertEqual(2, newEllipse["layer"])

	def test_Ellipse_copy(self) -> None:
		value =   [1, 2]
		ellipse = Ellipse(Point2D(1, 2), 3, 2, value=value, keyValuePairs={"layer": 1})

		newEllipse = copy(ellipse)

		self.assertIs(value, newEllipse.Value)
		self.assertIsNot(ellipse._dict, newEllipse._dict)

	def test_Ellipse_deepcopy(self) -> None:
		value =   [1, 2]
		ellipse = Ellipse(Point2D(1, 2), 3, 2, value=value, keyValuePairs={"nets": ["a"]})

		newEllipse = deepcopy(ellipse)

		self.assertIs(Ellipse, type(newEllipse))
		self.assertIsNot(value, newEllipse.Value)
		self.assertListEqual([1, 2], newEllipse.Value)
		self.assertIsNot(ellipse["nets"], newEllipse["nets"])
		self.assertListEqual(["a"], newEllipse["nets"])

	def test_Path(self) -> None:
		value = object()
		pairs = {"layer": 1}
		path =  Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), value=value, keyValuePairs=pairs)

		self.assertIs(value, path.Value)
		self.assertEqual(1, path["layer"])
		self.assertIsNot(pairs, path._dict)

	def test_Path_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Path_Edges(self) -> None:
		"""An edge references the given segment's value and holds a shallow copy of its key-value-pairs."""
		value = object()
		line =  LineSegment2D(Point2D(0, 0), Point2D(4, 0), value=value, keyValuePairs={"net": "a"})
		arc =   ArcSegment2D(Point2D(4, 0), Point2D(0, 0), height=2, value=2, keyValuePairs={"net": "b"})

		path = Path((line, arc), closed=True)
		path.Segments[0]["net"] = "c"

		self.assertIs(value, path.Segments[0].Value)
		self.assertEqual(2, path.Segments[1].Value)
		self.assertEqual("b", path.Segments[1]["net"])
		self.assertEqual("a", line["net"])
		self.assertEqual(0, len(path))

	def test_Path_Copy(self) -> None:
		value = [1, 2]
		path =  Path(
			(QuadraticBezierSegment2D(Point2D(0, 0), Point2D(2, 4), Point2D(4, 0), value=3, keyValuePairs={"a": 1}), ),
			value=value,
			keyValuePairs={"layer": 1}
		)

		newPath =          path.Copy()
		newPath["layer"] = 2

		self.assertIs(value, newPath.Value)
		self.assertEqual(1, path["layer"])
		self.assertEqual(2, newPath["layer"])
		self.assertEqual(3, newPath.Segments[0].Value)
		self.assertEqual(1, newPath.Segments[0]["a"])
		self.assertIs(value, copy(path).Value)

	def test_Path_deepcopy(self) -> None:
		value = [1, 2]
		path =  Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), value=value, keyValuePairs={"nets": ["a"]})

		newPath = deepcopy(path)

		self.assertIsNot(value, newPath.Value)
		self.assertListEqual([1, 2], newPath.Value)
		self.assertIsNot(path["nets"], newPath["nets"])
		self.assertIs(newPath, newPath.Points[0].Parent)


def openPath() -> Path:
	"""A line, a semicircle bulging to the right and a quadratic curve bulging upwards."""
	return Path((
		LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
		ArcSegment2D(Point2D(4, 0), Point2D(4, 4), center=Point2D(4, 2), direction=SweepDirection.Counterclockwise),
		QuadraticBezierSegment2D(Point2D(4, 4), Point2D(2, 6), Point2D(0, 4))
	))


def closedPath() -> Path:
	"""A line and the upper semicircle back to its start."""
	return Path((
		LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
		ArcSegment2D(Point2D(4, 0), Point2D(0, 0), center=Point2D(2, 0), direction=SweepDirection.Counterclockwise)
	), closed=True)


class PathInstantiation(Testcase):
	def test_Open(self) -> None:
		path = openPath()

		self.assertIsInstance(path, Shape)
		self.assertFalse(path.IsClosed)
		self.assertTupleEqual(((0, 0), (4, 0), (4, 4), (0, 4)), tuple(point.ToTuple() for point in path.Points))
		self.assertIs(LineSegment2D, type(path.Segments[0]))
		self.assertIs(ArcSegment2D, type(path.Segments[1]))
		self.assertIs(QuadraticBezierSegment2D, type(path.Segments[2]))

	def test_Open_Joints(self) -> None:
		"""Consecutive edges share their joint; the path owns every point."""
		path = openPath()
		line, arc, curve = path.Segments

		self.assertIs(path.Points[0], line.Start)
		self.assertIs(line.End, arc.Start)
		self.assertIs(arc.End, curve.Start)
		self.assertIs(path.Points[3], curve.End)
		for point in path.Points:
			self.assertIs(path, point.Parent)

		self.assertIsNone(arc.Center.Parent)
		self.assertIs(path, curve.ControlPoint.Parent)

	def test_Closed(self) -> None:
		path = closedPath()
		line, arc = path.Segments

		self.assertTrue(path.IsClosed)
		self.assertTupleEqual(((0, 0), (4, 0)), tuple(point.ToTuple() for point in path.Points))
		self.assertIs(line.Start, arc.End)
		self.assertIs(line.End, arc.Start)

	def test_Closed_Circle(self) -> None:
		"""Two semicircles close a path to a full circle."""
		path = Path((
			ArcSegment2D(Point2D(1, 0), Point2D(-1, 0), height=1),
			ArcSegment2D(Point2D(-1, 0), Point2D(1, 0), height=1)
		), closed=True)

		self.assertEqual(2, len(path.Points))
		self.assertIs(path.Segments[0].Start, path.Segments[1].End)
		self.assertEqual(BoundingBox2D(-1, -1, 1, 1), path.BoundingBox)

	def test_Segments_Copied(self) -> None:
		"""The given segments keep their points."""
		line = LineSegment2D(Point2D(0, 0), Point2D(4, 0))
		arc =  ArcSegment2D(Point2D(4, 0), Point2D(0, 0), center=Point2D(2, 0), direction=SweepDirection.Counterclockwise)

		path = Path((line, arc), closed=True)

		self.assertIsNot(line, path.Segments[0])
		self.assertIs(line, line.End.Parent)
		self.assertIs(arc, arc.End.Parent)
		self.assertIsNot(arc.End, path.Segments[1].End)

	def test_SegmentsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path(None)

		self.assertEqual("Parameter 'segments' is None.", str(context.exception))

	def test_SegmentsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Path(1)

		self.assertEqual("Parameter 'segments' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_SegmentNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), None))

		self.assertEqual("An element of parameter 'segments' is None.", str(context.exception))

	def test_SegmentPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Path((Point2D(0, 0), ))

		self.assertEqual("An element of parameter 'segments' is not of type 'Segment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_Gap(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), LineSegment2D(Point2D(4, 1), Point2D(4, 4))))

		self.assertEqual(
			"An element of parameter 'segments' doesn't start at the end point of the previous element.",
			str(context.exception)
		)
		self.assertListEqual(["Got end point (4, 0) and start point (4, 1)."], context.exception.__notes__)

	def test_Empty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path(())

		self.assertEqual("Parameter 'segments' is empty.", str(context.exception))

	def test_ClosedNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), closed=None)

		self.assertEqual("Parameter 'closed' is None.", str(context.exception))

	def test_ClosedInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), closed=1)

		self.assertEqual("Parameter 'closed' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Closed_Open(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), LineSegment2D(Point2D(4, 0), Point2D(4, 4))), closed=True)

		self.assertEqual(
			"Parameter 'closed' is True, while the last segment doesn't end at the first segment's start.",
			str(context.exception)
		)
		self.assertListEqual(["Got start point (0, 0) and end point (4, 4)."], context.exception.__notes__)

	def test_ClosedPositional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), True)

	def test_Open_EndAtStart(self) -> None:
		"""An open path ending at its start keeps two joints at that position."""
		path = Path((
			LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
			ArcSegment2D(Point2D(4, 0), Point2D(0, 0), center=Point2D(2, 0), direction=SweepDirection.Counterclockwise)
		))

		self.assertEqual(3, len(path.Points))
		self.assertIsNot(path.Segments[0].Start, path.Segments[1].End)


class PathAppending(Testcase):
	def test_Append(self) -> None:
		"""The new edge starts at the path's last joint; the given segment stays as it is."""
		path =    Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))
		arc =     ArcSegment2D(Point2D(4, 0), Point2D(4, 4), height=-2)
		lastEnd = path.Points[-1]

		path.AppendSegment(arc)

		line, edge = path.Segments

		self.assertIs(ArcSegment2D, type(edge))
		self.assertIsNot(arc, edge)
		self.assertIs(path, edge.Parent)
		self.assertIs(lastEnd, edge.Start)
		self.assertIs(line.End, edge.Start)
		self.assertTupleEqual(((0, 0), (4, 0), (4, 4)), tuple(point.ToTuple() for point in path.Points))
		self.assertIs(edge.End, path.Points[-1])
		self.assertIs(path, edge.End.Parent)
		self.assertIsNone(edge.Center.Parent)
		self.assertIs(arc, arc.Start.Parent)
		self.assertEqual(BoundingBox2D(0, 0, 6, 4), path.BoundingBox)

	def test_Append_Data(self) -> None:
		value = object()
		path =  Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		path.AppendSegment(LineSegment2D(Point2D(4, 0), Point2D(4, 4), value=value, keyValuePairs={"net": "a"}))

		self.assertIs(value, path.Segments[1].Value)
		self.assertEqual("a", path.Segments[1]["net"])

	def test_Append_Edge(self) -> None:
		"""A segment owned by another element is copied, as by the initializer."""
		polygon = Polygon((Point2D(4, 0), Point2D(4, 4), Point2D(8, 0)))
		path =    Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		path.AppendSegment(polygon.Segments[0])

		self.assertIs(path, path.Segments[1].Parent)
		self.assertIs(polygon, polygon.Segments[0].Parent)
		self.assertIs(polygon, polygon.Points[0].Parent)

	def test_Append_Move(self) -> None:
		"""The new joint is moved once."""
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))
		path.AppendSegment(QuadraticBezierSegment2D(Point2D(4, 0), Point2D(6, 2), Point2D(4, 4)))

		path.Move(Offset2D(1, 1))

		self.assertTupleEqual(((1, 1), (5, 1), (5, 5)), tuple(point.ToTuple() for point in path.Points))
		self.assertTupleEqual((7, 3), path.Segments[1].ControlPoint.ToTuple())

	def test_Append_None(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(ValueError) as context:
			path.AppendSegment(None)

		self.assertEqual("Parameter 'segment' is None.", str(context.exception))

	def test_Append_Point(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(TypeError) as context:
			path.AppendSegment(Point2D(4, 4))

		self.assertEqual("Parameter 'segment' is not of type 'Segment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_Append_Gap(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(ValueError) as context:
			path.AppendSegment(LineSegment2D(Point2D(4, 1), Point2D(4, 4)))

		self.assertEqual("Parameter 'segment' doesn't start at the end point of the path.", str(context.exception))
		self.assertListEqual(["Got start point (4, 1), expected (4, 0)."], context.exception.__notes__)
		self.assertEqual(1, len(path.Segments))
		self.assertEqual(2, len(path.Points))

	def test_Append_Closed(self) -> None:
		path = closedPath()

		with self.assertRaises(InvalidOperationError) as context:
			path.AppendSegment(LineSegment2D(Point2D(0, 0), Point2D(-4, 0)))

		self.assertEqual("Path is closed.", str(context.exception))
		self.assertListEqual(["A closed path doesn't get opened by appending a segment."], context.exception.__notes__)
		self.assertEqual(2, len(path.Segments))

	def test_Prepend(self) -> None:
		"""The new edge ends at the path's first joint."""
		path =       Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))
		firstStart = path.Points[0]

		path.PrependSegment(CubicBezierSegment2D(Point2D(-4, 0), Point2D(-4, 2), Point2D(0, 2), Point2D(0, 0)))

		edge, line = path.Segments

		self.assertIs(CubicBezierSegment2D, type(edge))
		self.assertIs(firstStart, edge.End)
		self.assertIs(line.Start, edge.End)
		self.assertTupleEqual(((-4, 0), (0, 0), (4, 0)), tuple(point.ToTuple() for point in path.Points))
		self.assertIs(edge.Start, path.Points[0])
		self.assertIs(path, edge.Start.Parent)
		self.assertIs(path, edge.ControlPoint1.Parent)

	def test_Prepend_None(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(ValueError) as context:
			path.PrependSegment(None)

		self.assertEqual("Parameter 'segment' is None.", str(context.exception))

	def test_Prepend_Tuple(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(TypeError) as context:
			path.PrependSegment((Point2D(-4, 0), Point2D(0, 0)))

		self.assertEqual("Parameter 'segment' is not of type 'Segment2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Prepend_Gap(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(ValueError) as context:
			path.PrependSegment(LineSegment2D(Point2D(-4, 0), Point2D(0, 1)))

		self.assertEqual("Parameter 'segment' doesn't end at the start point of the path.", str(context.exception))
		self.assertListEqual(["Got end point (0, 1), expected (0, 0)."], context.exception.__notes__)
		self.assertEqual(1, len(path.Segments))

	def test_Prepend_Closed(self) -> None:
		path = closedPath()

		with self.assertRaises(InvalidOperationError) as context:
			path.PrependSegment(LineSegment2D(Point2D(-4, 0), Point2D(0, 0)))

		self.assertEqual("Path is closed.", str(context.exception))
		self.assertListEqual(["A closed path doesn't get opened by prepending a segment."], context.exception.__notes__)


class PathGeometry(Testcase):
	def test_Length(self) -> None:
		self.assertEqual(4 + 2 * pi, closedPath().Length)

	def test_Length_Bezier(self) -> None:
		path = openPath()

		with self.assertRaises(InvalidOperationError) as context:
			_ = path.Length

		self.assertEqual("Path has a segment without a length.", str(context.exception))
		self.assertListEqual(["Got QuadraticBezierSegment2D((4, 4), (2, 6), (0, 4))."], context.exception.__notes__)

	def test_BoundingBox_Open(self) -> None:
		"""The arc bulges to x = 6, the curve to y = 5."""
		self.assertEqual(BoundingBox2D(0, 0, 6, 5), openPath().BoundingBox)

	def test_BoundingBox_Closed(self) -> None:
		self.assertEqual(BoundingBox2D(0, 0, 4, 2), closedPath().BoundingBox)

	def test_BoundingBox_Cubic(self) -> None:
		path = Path((
			CubicBezierSegment2D(Point2D(0, 0), Point2D(6, 0), Point2D(6, 6), Point2D(0, 6)),
			LineSegment2D(Point2D(0, 6), Point2D(0, 0))
		), closed=True)

		self.assertEqual(BoundingBox2D(0, 0, 4.5, 6), path.BoundingBox)

	def test_ReadOnly(self) -> None:
		path = closedPath()

		with self.assertRaises(AttributeError):
			path.Segments = ()

		with self.assertRaises(AttributeError):
			path.IsClosed = False


class PathOwnership(Testcase):
	def test_MoveJoint(self) -> None:
		"""Moving a joint moves the arc's start point; the arc keeps its relative height, so its circle follows."""
		path =  closedPath()
		line, arc = path.Segments
		joint = line.End

		joint += Offset2D(4, 0)

		self.assertIs(joint, arc.Start)
		self.assertEqual(-4, arc.Height)
		self.assertTupleEqual((4.0, 0.0), arc.Center.ToTuple())
		self.assertEqual(4, arc.Radius)
		self.assertIs(SweepDirection.Counterclockwise, arc.Direction)
		self.assertEqual(BoundingBox2D(0, 0, 8, 4), path.BoundingBox)

	def test_Edge_ToGroup(self) -> None:
		path = closedPath()

		with self.assertRaises(AlreadyOwnedError):
			path.Segments[0].Parent = Group2D()

		self.assertIs(path, path.Segments[0].Parent)

	def test_Edge_Start(self) -> None:
		"""An edge doesn't own its points, so it can't replace them."""
		path = openPath()
		line = path.Segments[0]

		with self.assertRaises(NotOwnedError):
			line.Start = Point2D(-1, 0)

		self.assertIs(path.Points[0], line.Start)

	def test_Edge_Arc_End(self) -> None:
		path = openPath()
		arc =  path.Segments[1]

		with self.assertRaises(NotOwnedError):
			arc.End = Point2D(6, 2)

	def test_Edge_Move(self) -> None:
		"""Moving an edge moves the joints it shares with its neighbours."""
		path = openPath()

		path.Segments[0].Move(Offset2D(0, -1))

		self.assertTupleEqual((4, -1), path.Segments[1].Start.ToTuple())


class PathMoving(Testcase):
	def test_Move(self) -> None:
		"""Each joint moves once, the arc's center and the curve's control point move along."""
		path = openPath()

		path.Move(Offset2D(10, 20))

		self.assertTupleEqual(((10, 20), (14, 20), (14, 24), (10, 24)), tuple(point.ToTuple() for point in path.Points))
		self.assertTupleEqual((14, 22), path.Segments[1].Center.ToTuple())
		self.assertTupleEqual((12, 26), path.Segments[2].ControlPoint.ToTuple())
		self.assertEqual(BoundingBox2D(10, 20, 16, 25), path.BoundingBox)

	def test_Move_None(self) -> None:
		path = openPath()

		with self.assertRaises(ValueError) as context:
			path.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Move_Tuple(self) -> None:
		path = openPath()

		with self.assertRaises(TypeError) as context:
			path.Move((1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)


class PathMirroring(Testcase):
	def test_MirrorX(self) -> None:
		"""Each joint is mirrored once; the arc reverses its direction and bulges to the left."""
		path = openPath()

		path.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual(((0, 0), (-4, 0), (-4, 4), (0, 4)), tuple(point.ToTuple() for point in path.Points))
		self.assertTupleEqual((-4, 2), path.Segments[1].Center.ToTuple())
		self.assertIs(SweepDirection.Clockwise, path.Segments[1].Direction)
		self.assertTupleEqual((-2, 6), path.Segments[2].ControlPoint.ToTuple())
		self.assertEqual(BoundingBox2D(-6, 0, 0, 5), path.BoundingBox)

	def test_MirrorY(self) -> None:
		path = closedPath()

		path.MirrorY(Alignment2D.MinY)

		self.assertTupleEqual(((0, 0), (4, 0)), tuple(point.ToTuple() for point in path.Points))
		self.assertIs(SweepDirection.Clockwise, path.Segments[1].Direction)
		self.assertEqual(BoundingBox2D(0, -2, 4, 0), path.BoundingBox)

	def test_Canvas(self) -> None:
		path =   closedPath()
		canvas = Canvas2D(YAxisDirection.Up, Size2D(10, 10), (path, ))

		canvas.Mirror()

		self.assertTupleEqual(((0, 10), (4, 10)), tuple(point.ToTuple() for point in path.Points))
		self.assertEqual(BoundingBox2D(0, 8, 4, 10), path.BoundingBox)


class PathCopy(Testcase):
	def test_Copy(self) -> None:
		path = closedPath()

		for newPath in (path.Copy(), copy(path), deepcopy(path)):
			self.assertIs(Path, type(newPath))
			self.assertTrue(newPath.IsClosed)
			self.assertIsNot(path.Points[0], newPath.Points[0])
			self.assertIs(newPath.Segments[0].Start, newPath.Segments[1].End)
			self.assertIs(newPath, newPath.Segments[1].Start.Parent)
			self.assertEqual(path.BoundingBox, newPath.BoundingBox)

	def test_Copy_Independent(self) -> None:
		path =    openPath()
		newPath = path.Copy()

		newPath.Move(Offset2D(1, 1))

		self.assertEqual(BoundingBox2D(0, 0, 6, 5), path.BoundingBox)
		self.assertEqual(BoundingBox2D(1, 1, 7, 6), newPath.BoundingBox)

	def test_deepcopy_Group(self) -> None:
		group = Group2D()
		path =  Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), parent=group)

		newPath = deepcopy(path)

		self.assertIsNone(newPath.Parent)
		self.assertTupleEqual((path, ), group.Children)


class PathGroups(Testcase):
	def test_Parent(self) -> None:
		group = Group2D(Offset2D(10, 20))

		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), parent=group)

		self.assertIs(group, path.Parent)
		self.assertTupleEqual((path, ), group.Children)
		self.assertIs(group, path.Segments[0].Frame)
		self.assertEqual(BoundingBox2D(10, 20, 14, 20), path.AbsoluteBoundingBox)

	def test_Parent_Failing(self) -> None:
		group = Group2D()

		with self.assertRaises(ValueError):
			_ = Path((), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Parent_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class PathRepresentation(Testcase):
	def test_repr(self) -> None:
		path = closedPath()

		self.assertEqual(
			"Path(LineSegment2D((0, 0), (4, 0)), ArcSegment2D((4, 0), (0, 0), chordPosition=0.5, height=-2.0), closed=True)",
			repr(path)
		)

	def test_str_Open(self) -> None:
		path = Path((
			LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
			QuadraticBezierSegment2D(Point2D(4, 0), Point2D(6, 2), Point2D(4, 4))
		))

		self.assertEqual("(((0, 0) → (4, 0)), ((4, 0) .. controls (6, 2) .. (4, 4)))", str(path))

	def test_str_Closed(self) -> None:
		path = closedPath()

		self.assertEqual(
			"(((0, 0) → (4, 0)), ((4, 0) → (0, 0), height -2.0 at 0.5), closed)",
			str(path)
		)


class ClosedPolyLine(Testcase):
	def test_Closed(self) -> None:
		"""The last point connects back to the first one; the first and last edge share it."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True)

		self.assertTrue(polyline.IsClosed)
		self.assertEqual(3, len(polyline.Points))
		self.assertEqual(3, len(polyline.Segments))
		self.assertIs(polyline.Points[0], polyline.Segments[2].End)
		self.assertIs(polyline.Segments[0].Start, polyline.Segments[2].End)
		self.assertEqual(12.0, polyline.Length)
		self.assertEqual(BoundingBox2D(0, 0, 4, 3), polyline.BoundingBox)

	def test_Open(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)))

		self.assertFalse(polyline.IsClosed)
		self.assertEqual(2, len(polyline.Segments))
		self.assertEqual(7.0, polyline.Length)

	def test_Closed_TwoPoints(self) -> None:
		with self.assertRaises(NotEnoughCornersError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), closed=True)

		self.assertEqual("Closed polyline has fewer than 3 points.", str(context.exception))
		self.assertListEqual(["Got 2 points."], context.exception.__notes__)
		self.assertEqual(
			"Parameter 'points' has fewer than 3 points, while parameter 'closed' is True.",
			str(context.exception.__cause__)
		)

	def test_ClosedNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), closed=None)

		self.assertEqual("Parameter 'closed' is None.", str(context.exception))

	def test_ClosedInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PolyLine((Point2D(0, 0), Point2D(4, 0)), closed=1)

		self.assertEqual("Parameter 'closed' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Move(self) -> None:
		"""The shared point moves once."""
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True)

		polyline.Move(Offset2D(1, 1))

		self.assertTupleEqual(((1, 1), (5, 1), (5, 4)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertTupleEqual(((5, 4), (1, 1)), polyline.Segments[2].ToTuple())

	def test_MirrorX(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True)

		polyline.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual(((0, 0), (-4, 0), (-4, 3)), tuple(point.ToTuple() for point in polyline.Points))

	def test_Copy(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True, value=1, keyValuePairs={"a": 1})

		for newPolyLine in (polyline.Copy(), copy(polyline), deepcopy(polyline)):
			self.assertIs(PolyLine, type(newPolyLine))
			self.assertTrue(newPolyLine.IsClosed)
			self.assertIsNot(polyline.Points[0], newPolyLine.Points[0])
			self.assertIs(newPolyLine.Points[0], newPolyLine.Segments[2].End)
			self.assertEqual(1, newPolyLine.Value)
			self.assertEqual(1, newPolyLine["a"])

	def test_repr(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True)

		self.assertEqual("PolyLine((0, 0), (4, 0), (4, 3), closed=True)", repr(polyline))

	def test_str(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True)

		self.assertEqual("((0, 0) → (4, 0) → (4, 3) → (0, 0))", str(polyline))


class Conversions(Testcase):
	def test_PolyLine_ToPolygon(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)), closed=True, value=1, keyValuePairs={"a": 1})

		polygon = polyline.ToPolygon()

		self.assertIs(Polygon, type(polygon))
		self.assertTupleEqual(((0, 0), (4, 0), (4, 3)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertIsNot(polyline.Points[0], polygon.Points[0])
		self.assertIs(polygon, polygon.Points[0].Parent)
		self.assertEqual(1, polygon.Value)
		self.assertEqual(1, polygon["a"])
		self.assertEqual(6.0, polygon.Area)

	def test_PolyLine_ToPolygon_Open(self) -> None:
		polyline = PolyLine((Point2D(0, 0), Point2D(4, 0), Point2D(4, 3)))

		with self.assertRaises(InvalidOperationError) as context:
			_ = polyline.ToPolygon()

		self.assertEqual("PolyLine is open.", str(context.exception))
		self.assertListEqual(["Only a closed path encloses an area."], context.exception.__notes__)

	def test_PolyLine_ToPolygon_Crossing(self) -> None:
		"""A polyline may cross itself, a polygon may not."""
		polyline = PolyLine((Point2D(0, 0), Point2D(2, 2), Point2D(2, 0), Point2D(0, 2)), closed=True)

		with self.assertRaises(CrossingEdgesError):
			_ = polyline.ToPolygon()

	def test_Polygon_ToPolyLine(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), value=1)

		polyline = polygon.ToPolyLine()

		self.assertIs(PolyLine, type(polyline))
		self.assertTrue(polyline.IsClosed)
		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertIsNot(polygon.Points[0], polyline.Points[0])
		self.assertEqual(1, polyline.Value)
		self.assertTrue(isclose(polygon.Perimeter, polyline.Length))

	def test_Rectangle_ToPolyLine(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

		polyline = rectangle.ToPolyLine()

		self.assertEqual("PolyLine((0, 0), (4, 0), (4, 2), (0, 2), closed=True)", repr(polyline))

	def test_Path_ToPolyLine(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), LineSegment2D(Point2D(4, 0), Point2D(4, 3))), value=1)

		polyline = path.ToPolyLine()

		self.assertIs(PolyLine, type(polyline))
		self.assertFalse(polyline.IsClosed)
		self.assertTupleEqual(((0, 0), (4, 0), (4, 3)), tuple(point.ToTuple() for point in polyline.Points))
		self.assertEqual(1, polyline.Value)

	def test_Path_ToPolyLine_Closed(self) -> None:
		path = Path((
			LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
			LineSegment2D(Point2D(4, 0), Point2D(4, 3)),
			LineSegment2D(Point2D(4, 3), Point2D(0, 0))
		), closed=True)

		polyline = path.ToPolyLine()

		self.assertTrue(polyline.IsClosed)
		self.assertEqual(3, len(polyline.Points))

	def test_Path_ToPolyLine_Curve(self) -> None:
		path = openPath()

		with self.assertRaises(InvalidOperationError) as context:
			_ = path.ToPolyLine()

		self.assertEqual("Path has a segment, which isn't a line segment.", str(context.exception))
		self.assertListEqual(
			[f"Got {path.Segments[1]!r}.", "A curved segment can't be converted without an approximation."],
			context.exception.__notes__
		)

	def test_Path_ToPolygon(self) -> None:
		path = Path((
			LineSegment2D(Point2D(0, 0), Point2D(4, 0)),
			LineSegment2D(Point2D(4, 0), Point2D(4, 3)),
			LineSegment2D(Point2D(4, 3), Point2D(0, 0))
		), closed=True, keyValuePairs={"a": 1})

		polygon = path.ToPolygon()

		self.assertIs(Polygon, type(polygon))
		self.assertTupleEqual(((0, 0), (4, 0), (4, 3)), tuple(point.ToTuple() for point in polygon.Points))
		self.assertEqual(1, polygon["a"])

	def test_Path_ToPolygon_Open(self) -> None:
		path = Path((LineSegment2D(Point2D(0, 0), Point2D(4, 0)), ))

		with self.assertRaises(InvalidOperationError) as context:
			_ = path.ToPolygon()

		self.assertEqual("Path is open.", str(context.exception))
		self.assertListEqual(["Only a closed path encloses an area."], context.exception.__notes__)

	def test_Path_ToPolygon_Curve(self) -> None:
		path = closedPath()

		with self.assertRaises(InvalidOperationError) as context:
			_ = path.ToPolygon()

		self.assertEqual("Path has a segment, which isn't a line segment.", str(context.exception))
