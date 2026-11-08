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
from __future__            import annotations

from math                  import degrees, isclose, pi
from typing                import TYPE_CHECKING, Generic, Iterable, Optional as Nullable, Self, Union

from pyTooling.Decorators  import export, readonly
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Cartesian2D import Coordinate, Point2D, Offset2D, BoundingBox, Element2D, Segment2D, LineSegment2D, \
                                  AlreadyOwnedError, DuplicatePointError, NotEnoughCornersError

if TYPE_CHECKING:
	from pyTooling.Cartesian2D.Groups import Group, Canvas


@export
class Shape(Element2D[Coordinate], Generic[Coordinate]):
	"""
	Abstract base-class for all 2D cartesian shapes.

	A derived class declares its fields as slots, so a class derived from a shape can use slots too. It implements
	:attr:`~pyTooling.Cartesian2D.Element2D.BoundingBox` and :meth:`~pyTooling.Cartesian2D.Element2D.Move`.

	A shape owns its points. A group or canvas can hold it: given as parameter ``parent``, it registers the shape, when
	the shape is fully initialized.
	"""


Segment2D._PARENT_TYPE = (Shape, )


@export
class Polygon(Shape[Coordinate], Generic[Coordinate]):
	"""
	A polygon is a closed shape, having three or more corners (vertices) connected by straight edges (sides).
	"""
	_points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the polygon's corners.
	_segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the polygon's edges.

	def __init__(
		self,
		points:     Iterable[Point2D[Coordinate]],
		*,
		copyPoints: bool = True,
		parent:     Nullable[Union[Group[Coordinate], Canvas[Coordinate]]] = None
	) -> None:
		"""
		Initializes a polygon from its corners.

		The corners are connected in the given order, the last one back to the first one.

		The polygon owns its corners. Referenced points (``copyPoints=False``) must not be owned by another element.

		:param points:                 Corners of the polygon.
		:param copyPoints:             Optional, if ``True``, the given points are copied instead of referenced. Default:
		                               ``True``.
		:param parent:                 Optional, the group or canvas the polygon is added to. Default: ``None``, no parent.
		:raises ValueError:            If parameter 'points' is None.
		:raises TypeError:             If parameter 'points' is not iterable.
		:raises ValueError:            If an element of parameter 'points' is None.
		:raises TypeError:             If an element of parameter 'points' is not of type
		                               :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:     If an element of parameter 'points' is owned by another element, while
		                               'copyPoints' is ``False``. |br|
		                               Use ``copyPoints=True`` to copy the point.
		:raises DuplicatePointError:   If an element of parameter 'points' is given twice, while 'copyPoints' is
		                               ``False``. |br|
		                               Use ``copyPoints=True`` to copy the points.
		:raises NotEnoughCornersError: If parameter 'points' has fewer than 3 points.
		:raises ValueError:            If parameter 'copyPoints' is None.
		:raises TypeError:             If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:             If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group` or
		                               :class:`~pyTooling.Cartesian2D.Groups.Canvas`.
		"""
		super().__init__(parent=parent)

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

		pointList =  []
		seenPoints = set()
		for point in points:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex
			elif copyPoints:
				pointList.append(point.Copy())
			elif point._parent is not None:
				ex = AlreadyOwnedError("Point is owned by another element already.")
				ex.add_note(f"Got point {point} owned by {point._parent!r}.")
				ex.add_note("Use 'copyPoints=True' to copy the point.")
				raise ex from ValueError("An element of parameter 'points' is owned by another element.")
			elif point in seenPoints:
				ex = DuplicatePointError("Point is given twice.")
				ex.add_note(f"Got point {point}.")
				ex.add_note("Use 'copyPoints=True' to copy the points.")
				raise ex from ValueError("An element of parameter 'points' is given twice.")
			else:
				seenPoints.add(point)
				pointList.append(point)

		if len(pointList) < 3:
			ex = NotEnoughCornersError("Polygon has fewer than 3 corners.")
			ex.add_note(f"Got {len(pointList)} points.")
			raise ex from ValueError("Parameter 'points' has fewer than 3 points.")

		self._points = corners = tuple(pointList)
		for corner in corners:
			corner._parent = self

		self._segments = tuple(
			LineSegment2D(start, end, copyPoints=False, parent=self)
			for start, end in zip(corners, (*corners[1:], corners[0]))
		)

		self.Parent = parent

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

	@readonly
	def BoundingBox(self) -> BoundingBox[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the polygon's corners.

		:returns: A new bounding box.
		"""
		return BoundingBox.FromPoints(self._points)

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the polygon by moving all its corners (inplace).

		Its edges share the corners, so they move along.

		:param offset:      The 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		for point in self._points:
			point += offset

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the polygon at a horizontal axis by mirroring all its corners (inplace).

		Its edges share the corners, so they mirror along.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		for point in self._points:
			point._y = twiceAxis - point._y

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the polygon at a vertical axis by mirroring all its corners (inplace).

		Its edges share the corners, so they mirror along.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		for point in self._points:
			point._x = twiceAxis - point._x

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
	_points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the trapezium.
	_segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the trapezium.

	def __init__(
		self,
		p00:    Point2D[Coordinate],
		p01:    Point2D[Coordinate],
		p11:    Point2D[Coordinate],
		p10:    Point2D[Coordinate],
		*,
		parent: Nullable[Union[Group[Coordinate], Canvas[Coordinate]]] = None
	) -> None:
		"""
		Initializes a trapezium with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:param parent:      Optional, the group or canvas the trapezium is added to. Default: ``None``, no parent.
		:raises ValueError: If parameter 'p00' is None.
		:raises TypeError:  If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p01' is None.
		:raises TypeError:  If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p11' is None.
		:raises TypeError:  If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p10' is None.
		:raises TypeError:  If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group` or
		                    :class:`~pyTooling.Cartesian2D.Groups.Canvas`.
		"""
		super().__init__(parent=parent)

		if p00 is None:
			raise ValueError("Parameter 'p00' is None.")
		elif not isinstance(p00, Point2D):
			ex = TypeError("Parameter 'p00' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p00)}'.")
			raise ex

		if p01 is None:
			raise ValueError("Parameter 'p01' is None.")
		elif not isinstance(p01, Point2D):
			ex = TypeError("Parameter 'p01' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p01)}'.")
			raise ex

		if p11 is None:
			raise ValueError("Parameter 'p11' is None.")
		elif not isinstance(p11, Point2D):
			ex = TypeError("Parameter 'p11' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p11)}'.")
			raise ex

		if p10 is None:
			raise ValueError("Parameter 'p10' is None.")
		elif not isinstance(p10, Point2D):
			ex = TypeError("Parameter 'p10' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p10)}'.")
			raise ex

		self._points = corners = (
			_p00 := p00.Copy(),
			_p01 := p01.Copy(),
			_p11 := p11.Copy(),
			_p10 := p10.Copy(),
		)
		for corner in corners:
			corner._parent = self

		self._segments = (
			LineSegment2D(_p00, _p01, copyPoints=False, parent=self),
			LineSegment2D(_p01, _p11, copyPoints=False, parent=self),
			LineSegment2D(_p11, _p10, copyPoints=False, parent=self),
			LineSegment2D(_p10, _p00, copyPoints=False, parent=self)
		)

		self.Parent = parent

	@readonly
	def Points(self) -> tuple[Point2D[Coordinate], ...]:
		"""
		Read-only property to access the trapezium's corners (:attr:`_points`).

		``points`` is a deprecated, assignable alias of this property; it is removed in v11.0.0.

		:returns: Tuple of corners, in drawing order.
		"""
		return self._points

	@property
	def points(self) -> tuple[Point2D[Coordinate], ...]:
		"""
		Property to access the trapezium's corners (:attr:`_points`).

		Deprecated alias of :attr:`Points`, which is read-only; it is removed in v11.0.0.

		An assigned iterable is stored as a tuple. Its elements are referenced, not copied, and the edges in
		:attr:`Segments` aren't updated. The trapezium takes ownership of the assigned points and releases its previous
		corners.

		:returns:                    Tuple of corners, in drawing order.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not iterable.
		:raises ValueError:          If an element of an assigned iterable is None.
		:raises TypeError:           If an element of an assigned iterable is not of type
		                             :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:   If an element of an assigned iterable is owned by another element.
		:raises DuplicatePointError: If an element of an assigned iterable is given twice.
		"""
		return self._points

	@points.setter
	def points(self, points: Iterable[Point2D[Coordinate]]) -> None:
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		corners =    tuple(points)
		seenPoints = set()
		for point in corners:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex
			elif point._parent is not None and point._parent is not self:
				ex = AlreadyOwnedError("Point is owned by another element already.")
				ex.add_note(f"Got point {point} owned by {point._parent!r}.")
				raise ex from ValueError("An element of parameter 'points' is owned by another element.")
			elif point in seenPoints:
				ex = DuplicatePointError("Point is given twice.")
				ex.add_note(f"Got point {point}.")
				raise ex from ValueError("An element of parameter 'points' is given twice.")

			seenPoints.add(point)

		for corner in self._points:
			corner._parent = None

		for corner in corners:
			corner._parent = self

		self._points = corners

	@readonly
	def Segments(self) -> tuple[LineSegment2D[Coordinate], ...]:
		"""
		Read-only property to access the trapezium's edges (:attr:`_segments`).

		``segments`` is a deprecated, assignable alias of this property; it is removed in v11.0.0.

		:returns: Tuple of edges, the last one connecting the last corner back to the first one.
		"""
		return self._segments

	@property
	def segments(self) -> tuple[LineSegment2D[Coordinate], ...]:
		"""
		Property to access the trapezium's edges (:attr:`_segments`).

		Deprecated alias of :attr:`Segments`, which is read-only; it is removed in v11.0.0.

		An assigned iterable is stored as a tuple. Its elements are referenced, not copied, and the corners in
		:attr:`Points` aren't updated.

		:returns:           Tuple of edges, the last one connecting the last corner back to the first one.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not iterable.
		:raises ValueError: If an element of an assigned iterable is None.
		:raises TypeError:  If an element of an assigned iterable is not of type
		                    :class:`~pyTooling.Cartesian2D.LineSegment2D`.
		"""
		return self._segments

	@segments.setter
	def segments(self, segments: Iterable[LineSegment2D[Coordinate]]) -> None:
		if segments is None:
			raise ValueError("Parameter 'segments' is None.")
		elif not isinstance(segments, Iterable):
			ex = TypeError("Parameter 'segments' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segments)}'.")
			raise ex

		edges = tuple(segments)
		for segment in edges:
			if segment is None:
				raise ValueError("An element of parameter 'segments' is None.")
			elif not isinstance(segment, LineSegment2D):
				ex = TypeError("An element of parameter 'segments' is not of type 'LineSegment2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
				raise ex

		self._segments = edges

	@readonly
	def BoundingBox(self) -> BoundingBox[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the trapezium's corners.

		:returns: A new bounding box.
		"""
		return BoundingBox.FromPoints(self._points)

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the trapezium by moving all its corners (inplace).

		Its edges share the corners, so they move along.

		:param offset:      The 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		for point in self._points:
			point += offset

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the trapezium at a horizontal axis by mirroring all its corners (inplace).

		Its edges share the corners, so they mirror along.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		for point in self._points:
			point._y = twiceAxis - point._y

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the trapezium at a vertical axis by mirroring all its corners (inplace).

		Its edges share the corners, so they mirror along.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		for point in self._points:
			point._x = twiceAxis - point._x

	def Copy(self) -> Self:
		"""
		Create a new trapezium as a copy of this trapezium.

		The copy holds copies of the corners, shared by its edges. A copy of a derived shape, like a
		:class:`Rectangle`, is of the same class, and its corners are checked again.

		:returns: Copy of this trapezium.
		"""
		return self.__class__(*self._points)

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

	def __init__(
		self,
		p00:    Point2D[Coordinate],
		p01:    Point2D[Coordinate],
		p11:    Point2D[Coordinate],
		p10:    Point2D[Coordinate],
		*,
		parent: Nullable[Union[Group[Coordinate], Canvas[Coordinate]]] = None
	) -> None:
		"""
		Initializes a rectangle with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:param parent:      Optional, the group or canvas the rectangle is added to. Default: ``None``, no parent.
		:raises ValueError: If parameter 'p00' is None.
		:raises TypeError:  If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p01' is None.
		:raises TypeError:  If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p11' is None.
		:raises TypeError:  If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p10' is None.
		:raises TypeError:  If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group` or
		                    :class:`~pyTooling.Cartesian2D.Groups.Canvas`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		"""
		super().__init__(p00, p01, p11, p10)

		for index in range(2):
			edge =         self._segments[index]
			oppositeEdge = self._segments[index + 2]
			if not isclose(edge.Length, oppositeEdge.Length):
				ex = ValueError("Opposite line segments (edges) have different lengths.")
				ex.add_note(f"Got lengths {edge.Length} and {oppositeEdge.Length}.")
				raise ex

		for edge in self._segments[:2]:
			if edge.Length == 0.0:
				ex = ValueError("Line segment (edge) has length 0.")
				ex.add_note(f"Got corners {edge._start} and {edge._end}.")
				raise ex

		for index in range(2):
			edge =     self._segments[index]
			nextEdge = self._segments[index + 1]
			angle =    pi - edge.AngleTo(nextEdge)
			if not isclose(angle, pi / 2):
				ex = ValueError("Inner angle of a rectangle is not 90°.")
				ex.add_note(f"Got {degrees(angle):.2f}° at corner {edge._end}.")
				raise ex

		self.Parent = parent


@export
class Square(Rectangle[Coordinate]):
	"""
	A square is a rectangle, where all edges have the same length and all inner angles are 90 |degree| .
	"""

	def __init__(
		self,
		p00:    Point2D[Coordinate],
		p01:    Point2D[Coordinate],
		p11:    Point2D[Coordinate],
		p10:    Point2D[Coordinate],
		*,
		parent: Nullable[Union[Group[Coordinate], Canvas[Coordinate]]] = None
	) -> None:
		"""
		Initializes a square with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:param parent:      Optional, the group or canvas the square is added to. Default: ``None``, no parent.
		:raises ValueError: If parameter 'p00' is None.
		:raises TypeError:  If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p01' is None.
		:raises TypeError:  If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p11' is None.
		:raises TypeError:  If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If parameter 'p10' is None.
		:raises TypeError:  If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group` or
		                    :class:`~pyTooling.Cartesian2D.Groups.Canvas`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		:raises ValueError: If adjacent edges have different lengths.
		"""
		super().__init__(p00, p01, p11, p10)

		edge =     self._segments[0]
		nextEdge = self._segments[1]
		if not isclose(edge.Length, nextEdge.Length):
			ex = ValueError("Line segments (edges) between corners have different lengths.")
			ex.add_note(f"Got lengths {edge.Length} and {nextEdge.Length}.")
			raise ex

		self.Parent = parent


@export
class Circle(Shape[Coordinate], Generic[Coordinate]):
	"""
	A circle is a round shape, where every point of its outline has the same distance (radius) to its center.
	"""
	_center: Point2D[Coordinate]  #: Center point of the circle.
	_radius: Coordinate           #: Radius of the circle.

	def __init__(
		self,
		center:     Point2D[Coordinate],
		radius:     Coordinate,
		*,
		copyPoints: bool = True,
		parent:     Nullable[Union[Group[Coordinate], Canvas[Coordinate]]] = None
	) -> None:
		"""
		Initializes a circle by its center and radius.

		The circle owns its center. A referenced center (``copyPoints=False``) must not be owned by another element.

		:param center:             Center point of the circle.
		:param radius:             Radius of the circle.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param parent:             Optional, the group or canvas the circle is added to. Default: ``None``, no parent.
		:raises ValueError:        If parameter 'center' is None.
		:raises TypeError:         If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'center' is owned by another element, while 'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'radius' is None.
		:raises TypeError:         If parameter 'radius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'radius' isn't positive.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas`.
		"""
		super().__init__(parent=parent)

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

		if not copyPoints and center._parent is not None:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {center} owned by {center._parent!r}.")
			ex.add_note("Use 'copyPoints=True' to copy the point.")
			raise ex from ValueError("Parameter 'center' is owned by another element.")

		self._center =         center.Copy() if copyPoints else center
		self._radius =         radius
		self._center._parent = self

		self.Parent = parent

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

	@readonly
	def BoundingBox(self) -> BoundingBox[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the circle.

		The box reaches :attr:`Radius` from the :attr:`Center` in each direction.

		:returns: A new bounding box.
		"""
		center = self._center
		radius = self._radius
		return BoundingBox(center._x - radius, center._y - radius, center._x + radius, center._y + radius)

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the circle by moving its center (inplace).

		:param offset:      The 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._center += offset

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the circle at a horizontal axis by mirroring its center (inplace).

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._center._y = twiceAxis - self._center._y

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the circle at a vertical axis by mirroring its center (inplace).

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._center._x = twiceAxis - self._center._x

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
