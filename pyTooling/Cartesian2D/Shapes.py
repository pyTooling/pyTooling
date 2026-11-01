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
"""An implementation of 2D cartesian shapes for Python."""

from math                  import degrees, isclose, pi
from typing                import Generic, Iterable, Self

from pyTooling.Decorators  import export, readonly
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Cartesian2D import Coordinate, Point2D, LineSegment2D


@export
class Shape(Generic[Coordinate]):
	"""Base-class for all 2D cartesian shapes."""


@export
class Polygon(Shape[Coordinate], Generic[Coordinate]):
	"""
	A polygon is a closed shape, having three or more corners (vertices) connected by straight edges (sides).
	"""
	_points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the polygon's corners.
	_segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the polygon's edges.

	def __init__(self, points: Iterable[Point2D[Coordinate]], copyPoints: bool = True) -> None:
		"""
		Initializes a polygon from its corners.

		The corners are connected in the given order, the last one back to the first one.

		:param points:      Corners of the polygon.
		:param copyPoints:  Optional, if ``True``, the given points are copied instead of referenced. Default: ``True``.
		:raises ValueError: If parameter 'points' is None.
		:raises TypeError:  If parameter 'points' is not iterable.
		:raises ValueError: If an element of parameter 'points' is None.
		:raises TypeError:  If an element of parameter 'points' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'points' has fewer than 3 points.
		:raises ValueError: If parameter 'copyPoints' is None.
		:raises TypeError:  If parameter 'copyPoints' is not of type :class:`bool`.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		pointList = []
		for point in points:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			pointList.append(point.Copy() if copyPoints else point)

		if len(pointList) < 3:
			ex = ValueError("Parameter 'points' has fewer than 3 points.")
			ex.add_note(f"Got {len(pointList)} points.")
			raise ex

		self._points =   corners = tuple(pointList)
		self._segments = tuple(
			LineSegment2D(start, end, copyPoints=False) for start, end in zip(corners, (*corners[1:], corners[0]))
		)

	def Copy(self) -> Self:
		"""
		Create a new polygon as a copy of this polygon.

		The copy holds copies of the corners, shared by its edges.

		:returns: Copy of this polygon.
		"""
		return self.__class__(self._points)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this polygon for :func:`copy.copy`.

		:returns: Copy of this polygon.
		"""
		return self.Copy()

	@readonly
	def Points(self) -> tuple[Point2D[Coordinate], ...]:
		"""
		Read-only property to access the polygon's corners (:attr:`_points`).

		:returns: Tuple of corners, in drawing order.
		"""
		return self._points

	@readonly
	def Segments(self) -> tuple[LineSegment2D[Coordinate], ...]:
		"""
		Read-only property to access the polygon's edges (:attr:`_segments`).

		:returns: Tuple of edges, the last one connecting the last corner back to the first one.
		"""
		return self._segments

	def __repr__(self) -> str:
		"""
		Returns the polygon's string representation.

		:returns: The string representation of the polygon.
		"""
		return f"Polygon({', '.join(str(point) for point in self._points)})"

	def __str__(self) -> str:
		"""
		Returns the polygon's string equivalent.

		:returns: The string equivalent of the polygon, its outline from the first corner back to the first corner.
		"""
		return f"({' → '.join(str(point) for point in (*self._points, self._points[0]))})"


@export
class Trapezium(Shape[Coordinate], Generic[Coordinate]):
	"""
	A Trapezium is a four-sided polygon, having four edges (sides) and four corners (vertices).
	"""
	points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the trapezium.
	segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the trapezium.

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a trapezium with 4 corners.

		:param p00:        First corner.
		:param p01:        Second corner.
		:param p11:        Third corner.
		:param p10:        Fourth corner.
		:raises TypeError: If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError: If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError: If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError: If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		"""
		if not isinstance(p00, Point2D):
			ex = TypeError("Parameter 'p00' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p00)}'.")
			raise ex

		if not isinstance(p01, Point2D):
			ex = TypeError("Parameter 'p01' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p01)}'.")
			raise ex

		if not isinstance(p11, Point2D):
			ex = TypeError("Parameter 'p11' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p11)}'.")
			raise ex

		if not isinstance(p10, Point2D):
			ex = TypeError("Parameter 'p10' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p10)}'.")
			raise ex

		self.points = (
			_p00 := p00.Copy(),
			_p01 := p01.Copy(),
			_p11 := p11.Copy(),
			_p10 := p10.Copy(),
		)

		self.segments = (
			LineSegment2D(_p00, _p01, copyPoints=False),
			LineSegment2D(_p01, _p11, copyPoints=False),
			LineSegment2D(_p11, _p10, copyPoints=False),
			LineSegment2D(_p10, _p00, copyPoints=False)
		)

	def Copy(self) -> Self:
		"""
		Create a new trapezium as a copy of this trapezium.

		The copy holds copies of the corners, shared by its edges. A copy of a derived shape, like a
		:class:`Rectangle`, is of the same class, and its corners are checked again.

		:returns: Copy of this trapezium.
		"""
		return self.__class__(*self.points)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this trapezium for :func:`copy.copy`.

		:returns: Copy of this trapezium.
		"""
		return self.Copy()


@export
class Rectangle(Trapezium[Coordinate]):
	"""
	A rectangle is a trapezium, where opposite edges are parallel to each other and all inner angles are 90 |degree| .
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a rectangle with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:raises TypeError:  If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		"""
		super().__init__(p00, p01, p11, p10)

		for index in range(2):
			edge =         self.segments[index]
			oppositeEdge = self.segments[index + 2]
			if not isclose(edge.Length, oppositeEdge.Length):
				ex = ValueError("Opposite line segments (edges) have different lengths.")
				ex.add_note(f"Got lengths {edge.Length} and {oppositeEdge.Length}.")
				raise ex

		for edge in self.segments[:2]:
			if edge.Length == 0.0:
				ex = ValueError("Line segment (edge) has length 0.")
				ex.add_note(f"Got corners {edge.start} and {edge.end}.")
				raise ex

		for index in range(2):
			edge =     self.segments[index]
			nextEdge = self.segments[index + 1]
			angle =    pi - edge.AngleTo(nextEdge)
			if not isclose(angle, pi / 2):
				ex = ValueError("Inner angle of a rectangle is not 90°.")
				ex.add_note(f"Got {degrees(angle):.2f}° at corner {edge.end}.")
				raise ex


@export
class Square(Rectangle[Coordinate]):
	"""
	A square is a rectangle, where all edges have the same length and all inner angles are 90 |degree| .
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a square with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:raises TypeError:  If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		:raises ValueError: If adjacent edges have different lengths.
		"""
		super().__init__(p00, p01, p11, p10)

		edge =     self.segments[0]
		nextEdge = self.segments[1]
		if not isclose(edge.Length, nextEdge.Length):
			ex = ValueError("Line segments (edges) between corners have different lengths.")
			ex.add_note(f"Got lengths {edge.Length} and {nextEdge.Length}.")
			raise ex


@export
class Circle(Shape[Coordinate], Generic[Coordinate]):
	"""
	A circle is a round shape, where every point of its outline has the same distance (radius) to its center.
	"""
	_center: Point2D[Coordinate]  #: Center point of the circle.
	_radius: Coordinate           #: Radius of the circle.

	def __init__(self, center: Point2D[Coordinate], radius: Coordinate, copyPoints: bool = True) -> None:
		"""
		Initializes a circle by its center and radius.

		:param center:      Center point of the circle.
		:param radius:      Radius of the circle.
		:param copyPoints:  Optional, if ``True``, the given center is copied instead of referenced. Default: ``True``.
		:raises ValueError: If parameter 'center' is None.
		:raises TypeError:  If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'radius' is None.
		:raises TypeError:  If parameter 'radius' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'radius' isn't positive.
		:raises ValueError: If parameter 'copyPoints' is None.
		:raises TypeError:  If parameter 'copyPoints' is not of type :class:`bool`.
		"""
		if center is None:
			raise ValueError("Parameter 'center' is None.")
		elif not isinstance(center, Point2D):
			ex = TypeError("Parameter 'center' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(center)}'.")
			raise ex

		if radius is None:
			raise ValueError("Parameter 'radius' is None.")
		elif not isinstance(radius, (int, float)):
			ex = TypeError("Parameter 'radius' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(radius)}'.")
			raise ex
		elif radius <= 0:
			ex = ValueError("Parameter 'radius' isn't positive.")
			ex.add_note(f"Got value '{radius}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		self._center = center.Copy() if copyPoints else center
		self._radius = radius

	def Copy(self) -> Self:
		"""
		Create a new circle as a copy of this circle.

		The copy holds a copy of the center point.

		:returns: Copy of this circle.
		"""
		return self.__class__(self._center, self._radius)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this circle for :func:`copy.copy`.

		:returns: Copy of this circle.
		"""
		return self.Copy()

	@readonly
	def Center(self) -> Point2D[Coordinate]:
		"""
		Read-only property to access the circle's center point (:attr:`_center`).

		:returns: Center point of the circle.
		"""
		return self._center

	@readonly
	def Radius(self) -> Coordinate:
		"""
		Read-only property to access the circle's radius (:attr:`_radius`).

		:returns: Radius of the circle.
		"""
		return self._radius

	@readonly
	def Diameter(self) -> Coordinate:
		"""
		Read-only property to return the circle's diameter, twice its :attr:`Radius`.

		:returns: Diameter of the circle.
		"""
		return 2 * self._radius

	@readonly
	def Circumference(self) -> float:
		"""
		Read-only property to return the circle's circumference, the length of its outline.

		:returns: Circumference of the circle.
		"""
		return 2 * pi * self._radius

	@readonly
	def Area(self) -> float:
		"""
		Read-only property to return the circle's area.

		:returns: Area of the circle.
		"""
		return pi * self._radius ** 2

	def __repr__(self) -> str:
		"""
		Returns the circle's string representation.

		:returns: The string representation of the circle.
		"""
		return f"Circle({self._center}, {self._radius})"

	def __str__(self) -> str:
		"""
		Returns the circle's string equivalent.

		:returns: The string equivalent of the circle.
		"""
		return f"({self._center}, r={self._radius})"
