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
Unit tests for :mod:`pyTooling.Cartesian2D.Shapes` - trapezium, rectangle and square.
"""
from math                         import isclose, sqrt

from pyTooling.Cartesian2D        import Point2D, LineSegment2D
from pyTooling.Cartesian2D.Shapes import Shape, Trapezium, Rectangle, Square
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
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

		self.assertEqual("Parameter 'p00' is not of type Point2D.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str2(self) -> None:
		point00 = Point2D(1, 1)
		point11 = Point2D(3, 3)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, "3, 1", point11, point10)

		self.assertEqual("Parameter 'p01' is not of type Point2D.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str3(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point10 = Point2D(1, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, "3, 3", point10)

		self.assertEqual("Parameter 'p11' is not of type Point2D.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Trapezium_str4(self) -> None:
		point00 = Point2D(1, 1)
		point01 = Point2D(3, 1)
		point11 = Point2D(3, 3)

		with self.assertRaises(TypeError) as context:
			_ = Trapezium(point00, point01, point11, "1, 3")

		self.assertEqual("Parameter 'p10' is not of type Point2D.", str(context.exception))
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

		self.assertEqual("Line segments (edges) of opposite edges different lengths.", str(context.exception))

	def test_Rectangle_str(self) -> None:
		point00 = Point2D(0, 0)
		point01 = Point2D(4, 2)
		point11 = Point2D(3, 4)

		with self.assertRaises(TypeError) as context:
			_ = Rectangle(point00, point01, point11, "-1, 2")

		self.assertEqual("Parameter 'p10' is not of type Point2D.", str(context.exception))
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

	def test_Square_str(self) -> None:
		point01 = Point2D(1, 1)
		point11 = Point2D(0, 2)
		point10 = Point2D(-1, 1)

		with self.assertRaises(TypeError) as context:
			_ = Square("0, 0", point01, point11, point10)

		self.assertEqual("Parameter 'p00' is not of type Point2D.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)


class Corners(Testcase):
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
