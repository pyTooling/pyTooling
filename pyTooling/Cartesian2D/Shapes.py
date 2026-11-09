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

from copy                  import deepcopy
from math                  import degrees, isclose, pi, sqrt
from typing                import TYPE_CHECKING, Any, Generic, Hashable, Iterable, Mapping, Optional as Nullable, \
                                  Self, Union

from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import InvalidOperationError
from pyTooling.MetaClasses import abstractclass, abstractmethod
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Cartesian2D import Coordinate, Point2D, Offset2D, BoundingBox2D, Element2D, Segment2D, LineSegment2D, \
                                  ArcSegment2D, AlreadyOwnedError, DuplicatePointError, NotEnoughCornersError, \
                                  CrossingEdgesError, chordPoint, circumcenter

if TYPE_CHECKING:
	from pyTooling.Cartesian2D.Groups import Group2D, Canvas2D


@export
@abstractclass
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
@abstractclass
class Geometry2D(Shape[Coordinate], Generic[Coordinate]):
	"""
	Abstract base-class for all 2D cartesian geometries: closed shapes enclosing an area.

	A derived class implements :attr:`Area` and :attr:`Perimeter`, besides the abstract members of :class:`Shape`.
	"""

	@readonly
	@abstractmethod
	def Area(self) -> float:
		"""
		Read-only property to return the area enclosed by the geometry.

		:returns: Area of the geometry.
		"""

	@readonly
	@abstractmethod
	def Perimeter(self) -> float:
		"""
		Read-only property to return the perimeter of the geometry, the length of its outline.

		:returns: Perimeter of the geometry.
		"""


@export
class Polygon(Geometry2D[Coordinate], Generic[Coordinate]):
	"""
	A polygon is a closed shape, having three or more corners (vertices) connected by straight edges (sides).
	"""
	_points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the polygon's corners.
	_segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the polygon's edges.

	def __init__(
		self,
		points:        Iterable[Point2D[Coordinate]],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a polygon from its corners.

		The corners are connected in the given order, the last one back to the first one.

		The polygon owns its corners. Referenced points (``copyPoints=False``) must not be owned by another element.

		:param points:                 Corners of the polygon.
		:param copyPoints:             Optional, if ``True``, the given points are copied instead of referenced. Default:
		                               ``True``.
		:param value:                  Optional, value of the polygon. Default: ``None``.
		:param keyValuePairs:          Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
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
		:raises CrossingEdgesError:    If two edges have a point in common, which isn't their shared corner.
		:raises ValueError:            If parameter 'copyPoints' is None.
		:raises TypeError:             If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:             If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:             If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D`
		                               or :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

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

		def orientation(start: Point2D[Coordinate], end: Point2D[Coordinate], point: Point2D[Coordinate]) -> Coordinate:
			"""
			Nested function computing on which side of the line from the start point to the end point a point is.

			:param start: Start point of the line.
			:param end:   End point of the line.
			:param point: The point to check.
			:returns:     Positive, if the point is on the left, negative, if it is on the right, 0, if it is on the line.
			"""
			return (end._x - start._x) * (point._y - start._y) - (end._y - start._y) * (point._x - start._x)

		count = len(pointList)
		for index in range(count):
			start =   pointList[index]
			end =     pointList[(index + 1) % count]
			nextEnd = pointList[(index + 2) % count]
			if orientation(start, end, nextEnd) == 0 and (
				(end._x - start._x) * (nextEnd._x - end._x) + (end._y - start._y) * (nextEnd._y - end._y) < 0
			):
				ex = CrossingEdgesError("Polygon has overlapping edges.")
				ex.add_note(f"Got edges ({start} → {end}) and ({end} → {nextEnd}).")
				raise ex from ValueError("Parameter 'points' describes edges running back along each other.")

			for otherIndex in range(index + 2, count if index > 0 else count - 1):
				otherStart =     pointList[otherIndex]
				otherEnd =       pointList[(otherIndex + 1) % count]
				startSide =      orientation(start, end, otherStart)
				endSide =        orientation(start, end, otherEnd)
				otherStartSide = orientation(otherStart, otherEnd, start)
				otherEndSide =   orientation(otherStart, otherEnd, end)
				if startSide * endSide < 0 and otherStartSide * otherEndSide < 0:
					ex = CrossingEdgesError("Polygon has crossing edges.")
					ex.add_note(f"Got edges ({start} → {end}) and ({otherStart} → {otherEnd}).")
					raise ex from ValueError("Parameter 'points' describes edges crossing or touching each other.")

				for side, lineStart, lineEnd, point in (
					(startSide,      start,      end,      otherStart),
					(endSide,        start,      end,      otherEnd),
					(otherStartSide, otherStart, otherEnd, start),
					(otherEndSide,   otherStart, otherEnd, end)
				):
					if (
						side == 0 and
						min(lineStart._x, lineEnd._x) <= point._x <= max(lineStart._x, lineEnd._x) and
						min(lineStart._y, lineEnd._y) <= point._y <= max(lineStart._y, lineEnd._y)
					):
						ex = CrossingEdgesError("Polygon has crossing edges.")
						ex.add_note(f"Got edges ({start} → {end}) and ({otherStart} → {otherEnd}).")
						raise ex from ValueError("Parameter 'points' describes edges crossing or touching each other.")

		self._points = corners = tuple(pointList)
		for corner in corners:
			corner._parent = self

		self._segments = tuple(
			LineSegment2D(start, end, copyPoints=False, parent=self)
			for start, end in zip(corners, (*corners[1:], corners[0]))
		)

		self.Parent = parent

	def ToPolyline(self) -> Polyline[Coordinate]:
		"""
		Create a new closed polyline with the corners of this polygon as its points.

		The polyline holds copies of the corners. It references the same :attr:`Value` and holds a shallow copy of the
		key-value-pairs.

		:returns: A new closed polyline.
		"""
		return Polyline(self._points, closed=True, value=self._value, keyValuePairs=self._dict)

	def Copy(self) -> Self:
		"""
		Create a new polygon as a copy of this polygon.

		The copy holds copies of the corners, shared by its edges. It references the same :attr:`Value` and holds a shallow
		copy of the key-value-pairs.

		:returns: Copy of this polygon.
		"""
		return self.__class__(self._points, value=self._value, keyValuePairs=self._dict)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this polygon for :func:`copy.copy`.

		:returns: Copy of this polygon.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this polygon for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and deep copies of the :attr:`Value` and the
		key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this polygon.
		"""
		return self.__class__(
			self._points,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

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
	def Area(self) -> float:
		"""
		Read-only property to return the area enclosed by the polygon.

		The corners may be given clockwise or counterclockwise.

		:returns: Area of the polygon.
		"""
		corners =   self._points
		twiceArea = 0
		for corner, nextCorner in zip(corners, (*corners[1:], corners[0])):
			twiceArea += corner._x * nextCorner._y - nextCorner._x * corner._y

		return abs(twiceArea) / 2

	@readonly
	def Perimeter(self) -> float:
		"""
		Read-only property to return the perimeter of the polygon, the sum of its edges' lengths.

		:returns: Perimeter of the polygon.
		"""
		corners =   self._points
		perimeter = 0.0
		for corner, nextCorner in zip(corners, (*corners[1:], corners[0])):
			perimeter += sqrt((nextCorner._x - corner._x) ** 2 + (nextCorner._y - corner._y) ** 2)

		return perimeter

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the polygon's corners.

		:returns: A new bounding box.
		"""
		return BoundingBox2D.FromPoints(self._points)

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

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the polygon at a line by mirroring all its corners (inplace).

		Its edges share the corners, so they mirror along. A trapezium, rectangle or square stays one.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		for point in self._points:
			point._MirrorAt(normal, distance)

	def __repr__(self) -> str:
		"""
		Returns the polygon's string representation.

		:returns: The string representation of the polygon.
		"""
		return f"{self.__class__.__name__}({', '.join(str(point) for point in self._points)})"

	def __str__(self) -> str:
		"""
		Returns the polygon's string equivalent.

		:returns: The string equivalent of the polygon, its outline from the first corner back to the first corner.
		"""
		return f"({' → '.join(str(point) for point in (*self._points, self._points[0]))})"


@export
class Trapezium(Polygon[Coordinate], Generic[Coordinate]):
	"""
	A Trapezium is a four-sided polygon, having four edges (sides) and four corners (vertices).
	"""

	def __init__(
		self,
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a trapezium with 4 corners.

		The trapezium copies the given corners, as a :class:`Polygon` does by default.

		:param p00:                 First corner.
		:param p01:                 Second corner.
		:param p11:                 Third corner.
		:param p10:                 Fourth corner.
		:param value:               Optional, value of the trapezium. Default: ``None``.
		:param keyValuePairs:       Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:              Optional, the group or canvas the trapezium is added to. Default: ``None``, no parent.
		:raises ValueError:         If parameter 'p00' is None.
		:raises TypeError:          If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p01' is None.
		:raises TypeError:          If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p11' is None.
		:raises TypeError:          If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p10' is None.
		:raises TypeError:          If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises CrossingEdgesError: If two edges have a point in common, which isn't their shared corner.
		:raises TypeError:          If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:          If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                            :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__((p00, p01, p11, p10), value=value, keyValuePairs=keyValuePairs, parent=parent)

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

	def Copy(self) -> Self:
		"""
		Create a new trapezium as a copy of this trapezium.

		The copy holds copies of the corners, shared by its edges. A copy of a derived shape, like a
		:class:`Rectangle`, is of the same class, and its corners are checked again. It references the same :attr:`Value`
		and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this trapezium.
		"""
		return self.__class__(*self._points, value=self._value, keyValuePairs=self._dict)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this trapezium for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and deep copies of the :attr:`Value` and the
		key-value-pairs. A copy of a derived shape, like a :class:`Rectangle`, is of the same class, and its corners are
		checked again.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this trapezium.
		"""
		return self.__class__(
			*self._points,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Rectangle(Trapezium[Coordinate]):
	"""
	A rectangle is a trapezium, where opposite edges are parallel to each other and all inner angles are 90 |degree| .
	"""

	def __init__(
		self,
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a rectangle with 4 corners.

		:param p00:                 First corner.
		:param p01:                 Second corner.
		:param p11:                 Third corner.
		:param p10:                 Fourth corner.
		:param value:               Optional, value of the rectangle. Default: ``None``.
		:param keyValuePairs:       Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:              Optional, the group or canvas the rectangle is added to. Default: ``None``, no parent.
		:raises ValueError:         If parameter 'p00' is None.
		:raises TypeError:          If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p01' is None.
		:raises TypeError:          If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p11' is None.
		:raises TypeError:          If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p10' is None.
		:raises TypeError:          If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises CrossingEdgesError: If two edges have a point in common, which isn't their shared corner.
		:raises TypeError:          If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:          If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                            :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:         If opposite edges have different lengths.
		:raises ValueError:         If an inner angle isn't 90 |degree|.
		"""
		super().__init__(p00, p01, p11, p10, value=value, keyValuePairs=keyValuePairs)

		for index in range(2):
			edge =         self._segments[index]
			oppositeEdge = self._segments[index + 2]
			if not isclose(edge.Length, oppositeEdge.Length):
				ex = ValueError("Opposite line segments (edges) have different lengths.")
				ex.add_note(f"Got lengths {edge.Length} and {oppositeEdge.Length}.")
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
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a square with 4 corners.

		:param p00:                 First corner.
		:param p01:                 Second corner.
		:param p11:                 Third corner.
		:param p10:                 Fourth corner.
		:param value:               Optional, value of the square. Default: ``None``.
		:param keyValuePairs:       Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:              Optional, the group or canvas the square is added to. Default: ``None``, no parent.
		:raises ValueError:         If parameter 'p00' is None.
		:raises TypeError:          If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p01' is None.
		:raises TypeError:          If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p11' is None.
		:raises TypeError:          If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:         If parameter 'p10' is None.
		:raises TypeError:          If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises CrossingEdgesError: If two edges have a point in common, which isn't their shared corner.
		:raises TypeError:          If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:          If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                            :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:         If opposite edges have different lengths.
		:raises ValueError:         If an inner angle isn't 90 |degree|.
		:raises ValueError:         If adjacent edges have different lengths.
		"""
		super().__init__(p00, p01, p11, p10, value=value, keyValuePairs=keyValuePairs)

		edge =     self._segments[0]
		nextEdge = self._segments[1]
		if not isclose(edge.Length, nextEdge.Length):
			ex = ValueError("Line segments (edges) between corners have different lengths.")
			ex.add_note(f"Got lengths {edge.Length} and {nextEdge.Length}.")
			raise ex

		self.Parent = parent


@export
@abstractclass
class EllipticalGeometry2D(Geometry2D[Coordinate], Generic[Coordinate]):
	"""
	Abstract base-class for closed round shapes around a center point, like a circle or an ellipse.

	The shape owns its center. Moving or mirroring the shape moves or mirrors its center.

	A derived class implements :attr:`BoundingBox`, :attr:`Area` and :attr:`Perimeter`. Its initializer checks its own
	parameters, then takes ownership of the center and assigns ``parent`` to :attr:`Parent` as its last statements.
	"""
	_center: Point2D[Coordinate]  #: Center point of the shape.

	def __init__(
		self,
		center:        Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a round shape by its center and checks the group or canvas it will be registered in.

		A referenced center (``copyPoints=False``) must not be owned by another element.

		:param center:             Center point of the shape.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param value:              Optional, value of the shape. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas the derived class registers the shape in. Default:
		                           ``None``, no parent.
		:raises ValueError:        If parameter 'center' is None.
		:raises TypeError:         If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'center' is owned by another element, while 'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

		if center is None:
			raise ValueError("Parameter 'center' is None.")
		elif not isinstance(center, Point2D):
			ex = TypeError("Parameter 'center' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(center)}'.")
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

		self._center = center.Copy() if copyPoints else center

	@readonly
	def Center(self) -> Point2D[Coordinate]:
		"""
		Read-only property to access the shape's center point (:attr:`_center`).

		:returns: Center point of the shape.
		"""
		return self._center

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the shape by moving its center (inplace).

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
		Mirror the shape at a horizontal axis by mirroring its center (inplace).

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._center._y = twiceAxis - self._center._y

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the shape at a vertical axis by mirroring its center (inplace).

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._center._x = twiceAxis - self._center._x

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the shape at a line by mirroring its center (inplace).

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		self._center._MirrorAt(normal, distance)


@export
class Circle(EllipticalGeometry2D[Coordinate], Generic[Coordinate]):
	"""
	A circle is a round shape, where every point of its outline has the same distance (radius) to its center.
	"""
	_radius: Coordinate  #: Radius of the circle.

	def __init__(
		self,
		center:        Point2D[Coordinate],
		radius:        Coordinate,
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a circle by its center and radius.

		The circle owns its center. A referenced center (``copyPoints=False``) must not be owned by another element.

		:param center:             Center point of the circle.
		:param radius:             Radius of the circle.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param value:              Optional, value of the circle. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
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
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(center, copyPoints=copyPoints, value=value, keyValuePairs=keyValuePairs, parent=parent)

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

		self._radius =         radius
		self._center._parent = self

		self.Parent = parent

	@classmethod
	def FromPoints(
		cls,
		points:        Iterable[Point2D[Coordinate]],
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> Self:
		"""
		Create the circle through three or more points.

		The first three points define the circle; every further point must be on it, its distance to the center compared
		with the radius by :func:`math.isclose`. Only the points' coordinates are used: the circle owns a new center point,
		as for an :class:`~pyTooling.Cartesian2D.ArcSegment2D` given by an arc point.

		:param points:        Points of the circle.
		:param value:         Optional, value of the circle. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the circle is added to. Default: ``None``, no parent.
		:returns:             A new circle through the points.
		:raises ValueError:   If parameter 'points' is None.
		:raises TypeError:    If parameter 'points' is not iterable.
		:raises ValueError:   If an element of parameter 'points' is None.
		:raises TypeError:    If an element of parameter 'points' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'points' has fewer than 3 points.
		:raises ValueError:   If two of the first three points of parameter 'points' are at the same position.
		:raises ValueError:   If the first three points of parameter 'points' are on one line.
		:raises ValueError:   If further points of parameter 'points' aren't on the circle through the first three points.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		pointList = []
		for point in points:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			pointList.append(point)

		if len(pointList) < 3:
			ex = ValueError("Parameter 'points' has fewer than 3 points.")
			ex.add_note(f"Got {len(pointList)} points.")
			raise ex

		for index, otherIndex in (
			(0, 1),
			(0, 2),
			(1, 2)
		):
			point = pointList[index]
			other = pointList[otherIndex]
			if point._x == other._x and point._y == other._y:
				ex = ValueError("Two of the first three points of parameter 'points' are at the same position.")
				ex.add_note(f"Got point {point} at index {index} and {otherIndex}.")
				raise ex

		first =  pointList[0]
		second = pointList[1]
		third =  pointList[2]
		if (second._x - first._x) * (third._y - first._y) - (second._y - first._y) * (third._x - first._x) == 0:
			ex = ValueError("The first three points of parameter 'points' are on one line.")
			ex.add_note(f"Got points {first}, {second} and {third}.")
			raise ex

		center = circumcenter(first, second, third)
		radius = sqrt((first._x - center._x) ** 2 + (first._y - center._y) ** 2)
		notes =  []
		for index, point in enumerate(pointList[3:], start=3):
			distance = sqrt((point._x - center._x) ** 2 + (point._y - center._y) ** 2)
			if not isclose(distance, radius):
				notes.append(
					f"Got point {point} at index {index} with distance {distance} to the center, while the radius is {radius}."
				)

		if len(notes) > 0:
			ex = ValueError("Parameter 'points' has points, which aren't on the circle through the first three points.")
			for note in notes:
				ex.add_note(note)
			raise ex

		return cls(center, radius, copyPoints=False, value=value, keyValuePairs=keyValuePairs, parent=parent)

	@classmethod
	def FromChord(
		cls,
		start:         Point2D[Coordinate],
		end:           Point2D[Coordinate],
		height:        Coordinate,
		chordPosition: float = 0.5,
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> Self:
		"""
		Create the circle through the end points of a chord and a point at a height over the chord.

		The height is measured perpendicular to the chord, the line segment from the start point to the end point, at the
		root point at the fraction ``chordPosition`` of the chord from the start point. A positive height is on the left
		of the chord, seen from the start point, a negative height on the right, as for an
		:class:`~pyTooling.Cartesian2D.ArcSegment2D`. At the chord's midpoint, the height is the sagitta of the circle's
		arc on that side. Only the points' coordinates are used: the circle owns a new center point.

		:param start:         Start point of the chord.
		:param end:           End point of the chord.
		:param height:        Signed distance of a point of the circle from the chord at the root point.
		:param chordPosition: Optional, the root point's position on the chord, as a fraction from 0 (start point) to 1
		                      (end point). Default: ``0.5``, the chord's midpoint.
		:param value:         Optional, value of the circle. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the circle is added to. Default: ``None``, no parent.
		:returns:             A new circle through both end points of the chord.
		:raises ValueError:   If parameter 'start' is None.
		:raises TypeError:    If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'end' is None.
		:raises TypeError:    If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'end' is at the position of parameter 'start'.
		:raises ValueError:   If parameter 'height' is None.
		:raises TypeError:    If parameter 'height' is not of type :class:`float` or :class:`int`.
		:raises ValueError:   If parameter 'height' is 0.
		:raises ValueError:   If parameter 'chordPosition' is None.
		:raises TypeError:    If parameter 'chordPosition' is not of type :class:`float`.
		:raises ValueError:   If parameter 'chordPosition' is out of range 0..1.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		for name, point in (
			("start", start),
			("end",   end)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		if end._x == start._x and end._y == start._y:
			ex = ValueError("Parameter 'end' is at the position of parameter 'start'.")
			ex.add_note(f"Got point {end}.")
			raise ex

		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex
		elif height == 0:
			raise ValueError("Parameter 'height' is 0.")

		if chordPosition is None:
			raise ValueError("Parameter 'chordPosition' is None.")
		elif not isinstance(chordPosition, (int, float)):
			ex = TypeError("Parameter 'chordPosition' is not of type 'float'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(chordPosition)}'.")
			raise ex
		elif not 0 <= chordPosition <= 1:
			ex = ValueError("Parameter 'chordPosition' is out of range 0..1.")
			ex.add_note(f"Got value '{chordPosition}'.")
			raise ex

		relativeHeight = height / sqrt((end._x - start._x) ** 2 + (end._y - start._y) ** 2)
		arcPoint =       chordPoint(start, end, chordPosition, relativeHeight)
		center =         circumcenter(start, arcPoint, end)
		return cls(
			center,
			sqrt((start._x - center._x) ** 2 + (start._y - center._y) ** 2),
			copyPoints=False,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=parent
		)

	def Copy(self) -> Self:
		"""
		Create a new circle as a copy of this circle.

		The copy holds a copy of the center point. It references the same :attr:`Value` and holds a shallow copy of the
		key-value-pairs.

		:returns: Copy of this circle.
		"""
		return self.__class__(self._center, self._radius, value=self._value, keyValuePairs=self._dict)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this circle for :func:`copy.copy`.

		:returns: Copy of this circle.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this circle for :func:`copy.deepcopy`.

		The copy holds a copy of the center point, and deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this circle.
		"""
		return self.__class__(
			self._center,
			self._radius,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

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
	def Perimeter(self) -> float:
		"""
		Read-only property to return the circle's perimeter (circumference), the length of its outline.

		:returns: Perimeter of the circle.
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
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the circle.

		The box reaches :attr:`Radius` from the :attr:`Center` in each direction.

		:returns: A new bounding box.
		"""
		center = self._center
		radius = self._radius
		return BoundingBox2D(center._x - radius, center._y - radius, center._x + radius, center._y + radius)

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


@export
class Ellipse(EllipticalGeometry2D[Coordinate], Generic[Coordinate]):
	"""
	An ellipse is a round shape, whose outline is stretched along two perpendicular axes by two radii.

	The first axis points in the ellipse's :attr:`Direction`, the second axis is turned by +90 degrees (counterclockwise).
	An ellipse with the default direction ``(1, 0)`` is axis-aligned. An ellipse with equal radii is a circle.
	"""
	_direction:    Offset2D[Coordinate]  #: Unit direction of the first axis, first non-zero component positive.
	_firstRadius:  Coordinate            #: Radius of the ellipse along its first axis.
	_secondRadius: Coordinate            #: Radius of the ellipse along its second axis.

	def __init__(
		self,
		center:        Point2D[Coordinate],
		firstRadius:   Coordinate,
		secondRadius:  Coordinate,
		*,
		direction:     Nullable[Offset2D[Coordinate]] = None,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes an ellipse by its center, its two radii and the direction of its first axis.

		A direction of another length than 1, compared by :func:`math.isclose`, is normalized. If its first non-zero
		component is negative, the direction is reversed: ``d`` and ``-d`` describe the same ellipse. The ellipse owns its
		center. A referenced center (``copyPoints=False``) must not be owned by another element.

		:param center:             Center point of the ellipse.
		:param firstRadius:        Radius of the ellipse along its first axis.
		:param secondRadius:       Radius of the ellipse along its second axis.
		:param direction:          Optional, direction of the first axis. Default: ``None``, the direction ``(1, 0)``.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param value:              Optional, value of the ellipse. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas the ellipse is added to. Default: ``None``, no parent.
		:raises ValueError:        If parameter 'center' is None.
		:raises TypeError:         If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'center' is owned by another element, while 'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'firstRadius' is None.
		:raises TypeError:         If parameter 'firstRadius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'firstRadius' isn't positive.
		:raises ValueError:        If parameter 'secondRadius' is None.
		:raises TypeError:         If parameter 'secondRadius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'secondRadius' isn't positive.
		:raises TypeError:         If parameter 'direction' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		:raises ValueError:        If parameter 'direction' is a zero offset. |br|
		                           An ellipse needs a direction of its first axis.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(center, copyPoints=copyPoints, value=value, keyValuePairs=keyValuePairs, parent=parent)

		for name, radius in (
			("firstRadius",  firstRadius),
			("secondRadius", secondRadius)
		):
			if radius is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(radius, (int, float)):
				ex = TypeError(f"Parameter '{name}' is not of type 'float' or 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(radius)}'.")
				raise ex
			elif radius <= 0:
				ex = ValueError(f"Parameter '{name}' isn't positive.")
				ex.add_note(f"Got value '{radius}'.")
				raise ex

		if direction is None:
			directionX = 1
			directionY = 0
		elif not isinstance(direction, Offset2D):
			ex = TypeError("Parameter 'direction' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
			raise ex
		elif direction._xOffset == 0 and direction._yOffset == 0:
			ex = ValueError("Parameter 'direction' is a zero offset.")
			ex.add_note(f"Got offset {direction}.")
			ex.add_note("An ellipse needs a direction of its first axis.")
			raise ex
		else:
			directionX = direction._xOffset
			directionY = direction._yOffset

		if not isclose(squaredLength := directionX ** 2 + directionY ** 2, 1):
			length =     sqrt(squaredLength)
			directionX = directionX / length
			directionY = directionY / length

		if directionX < 0 or (directionX == 0 and directionY < 0):
			directionX = -directionX
			directionY = -directionY

		self._direction =      Offset2D(directionX + 0, directionY + 0)
		self._firstRadius =    firstRadius
		self._secondRadius =   secondRadius
		self._center._parent = self

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new ellipse as a copy of this ellipse.

		The copy holds a copy of the center point and of the direction. It references the same :attr:`Value` and holds a
		shallow copy of the key-value-pairs.

		:returns: Copy of this ellipse.
		"""
		return self.__class__(
			self._center,
			self._firstRadius,
			self._secondRadius,
			direction=self._direction,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this ellipse for :func:`copy.copy`.

		:returns: Copy of this ellipse.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this ellipse for :func:`copy.deepcopy`.

		The copy holds a copy of the center point and of the direction, and deep copies of the :attr:`Value` and the
		key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this ellipse.
		"""
		return self.__class__(
			self._center,
			self._firstRadius,
			self._secondRadius,
			direction=self._direction,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	@readonly
	def Direction(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to access the direction of the ellipse's first axis (:attr:`_direction`).

		:returns: Direction of the first axis, of length 1, its first non-zero component is positive.
		"""
		return self._direction

	@readonly
	def FirstRadius(self) -> Coordinate:
		"""
		Read-only property to access the ellipse's radius along its first axis (:attr:`_firstRadius`).

		:returns: Radius of the ellipse along its first axis.
		"""
		return self._firstRadius

	@readonly
	def SecondRadius(self) -> Coordinate:
		"""
		Read-only property to access the ellipse's radius along its second axis (:attr:`_secondRadius`).

		:returns: Radius of the ellipse along its second axis.
		"""
		return self._secondRadius

	@readonly
	def FirstAxis(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to return the ellipse's first semi-axis, the :attr:`Direction` scaled by :attr:`FirstRadius`.

		:returns: A new 2D-offset from the center to the end of the first axis.
		"""
		direction = self._direction
		return Offset2D(direction._xOffset * self._firstRadius, direction._yOffset * self._firstRadius)

	@readonly
	def SecondAxis(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to return the ellipse's second semi-axis.

		It is the :attr:`Direction` turned by +90 degrees (counterclockwise) and scaled by :attr:`SecondRadius`.

		:returns: A new 2D-offset from the center to the end of the second axis.
		"""
		direction = self._direction
		return Offset2D(-direction._yOffset * self._secondRadius, direction._xOffset * self._secondRadius)

	@readonly
	def Perimeter(self) -> float:
		"""
		Read-only property to return the ellipse's approximate perimeter (circumference), the length of its outline.

		It is Ramanujan's second approximation, which is exact for equal radii. Otherwise, it is slightly too small: the
		relative error stays below 0.04 %.

		:returns: Perimeter of the ellipse.
		"""
		firstRadius =  self._firstRadius
		secondRadius = self._secondRadius
		squaredRatio = ((firstRadius - secondRadius) / (firstRadius + secondRadius)) ** 2
		return pi * (firstRadius + secondRadius) * (1 + 3 * squaredRatio / (10 + sqrt(4 - 3 * squaredRatio)))

	@readonly
	def Area(self) -> float:
		"""
		Read-only property to return the ellipse's area.

		:returns: Area of the ellipse.
		"""
		return pi * self._firstRadius * self._secondRadius

	@readonly
	def BoundingBox(self) -> BoundingBox2D[float]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the ellipse.

		With the semi-axes :attr:`FirstAxis` ``u`` and :attr:`SecondAxis` ``v``, the box reaches
		``sqrt(ux ** 2 + vx ** 2)`` from the :attr:`Center` in x-direction and ``sqrt(uy ** 2 + vy ** 2)`` in y-direction.

		:returns: A new bounding box.
		"""
		center =       self._center
		directionX =   self._direction._xOffset
		directionY =   self._direction._yOffset
		firstRadius =  self._firstRadius
		secondRadius = self._secondRadius
		halfWidth =    sqrt((directionX * firstRadius) ** 2 + (directionY * secondRadius) ** 2)
		halfHeight =   sqrt((directionY * firstRadius) ** 2 + (directionX * secondRadius) ** 2)
		return BoundingBox2D(center._x - halfWidth, center._y - halfHeight, center._x + halfWidth, center._y + halfHeight)

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the ellipse at a horizontal axis by mirroring its center and its direction (inplace).

		A direction with a non-zero x-component negates its y-component, a direction ``(0, 1)`` stays.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		super()._MirrorY(twiceAxis)
		direction = self._direction
		if direction._xOffset != 0:
			direction._yOffset = -direction._yOffset + 0

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the ellipse at a vertical axis by mirroring its center and its direction (inplace).

		A direction with a non-zero x-component negates its y-component, a direction ``(0, 1)`` stays.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		super()._MirrorX(twiceAxis)
		direction = self._direction
		if direction._xOffset != 0:
			direction._yOffset = -direction._yOffset + 0

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the ellipse at a line by mirroring its center as a point and its direction as a vector (inplace).

		The direction ``d`` becomes ``d - 2 * (nx * dx + ny * dy) * n``, reversed if its first non-zero component is
		negative.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		super()._MirrorAt(normal, distance)
		direction =  self._direction
		factor =     2 * normal.ScalarProduct(direction)
		directionX = direction._xOffset - factor * normal._xOffset
		directionY = direction._yOffset - factor * normal._yOffset
		if directionX < 0 or (directionX == 0 and directionY < 0):
			directionX = -directionX
			directionY = -directionY

		direction._xOffset = directionX + 0
		direction._yOffset = directionY + 0

	def __repr__(self) -> str:
		"""
		Returns the ellipse's string representation.

		The direction is given, if it isn't the default direction ``(1, 0)``.

		:returns: The string representation of the ellipse.
		"""
		direction = self._direction
		if direction._xOffset == 1 and direction._yOffset == 0:
			return f"Ellipse({self._center}, {self._firstRadius}, {self._secondRadius})"

		return f"Ellipse({self._center}, {self._firstRadius}, {self._secondRadius}, direction={direction})"

	def __str__(self) -> str:
		"""
		Returns the ellipse's string equivalent.

		The direction is given, if it isn't the default direction ``(1, 0)``.

		:returns: The string equivalent of the ellipse.
		"""
		direction = self._direction
		if direction._xOffset == 1 and direction._yOffset == 0:
			return f"({self._center}, r1={self._firstRadius}, r2={self._secondRadius})"

		return f"({self._center}, r1={self._firstRadius}, r2={self._secondRadius}, direction={direction})"


@export
class Path(Shape[Coordinate], Generic[Coordinate]):
	"""
	A path is a chain of connected segments: line segments, arcs and Bezier curves.

	Each segment starts at the end point of the previous segment, and both share that point (joint). A closed path ends at
	the start point of its first segment.
	"""

	_points:   tuple[Point2D[Coordinate], ...]    #: A tuple of 2D-points describing the joints of the path's segments.
	_segments: tuple[Segment2D[Coordinate], ...]  #: A tuple of 2D segments describing the path's edges.
	_closed:   bool                               #: ``True``, if the path ends at the start point of its first segment.

	def __init__(
		self,
		segments:      Iterable[Segment2D[Coordinate]],
		*,
		closed:        bool = False,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a path from its segments.

		The path copies the segments as its edges: consecutive edges share a joint, and the path owns all their points.
		An edge references the segment's value and holds a shallow copy of its key-value-pairs. The given segments stay
		as they are.

		:param segments:      Segments of the path, in drawing order.
		:param closed:        Optional, if ``True``, the last segment ends at the start point of the first segment.
		                      Default: ``False``.
		:param value:         Optional, value of the path. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the path is added to. Default: ``None``, no parent.
		:raises ValueError:   If parameter 'segments' is None.
		:raises TypeError:    If parameter 'segments' is not iterable.
		:raises ValueError:   If an element of parameter 'segments' is None.
		:raises TypeError:    If an element of parameter 'segments' is not of type
		                      :class:`~pyTooling.Cartesian2D.Segment2D`.
		:raises TypeError:    If an element of parameter 'segments' can't be an edge of a path, like a drawable segment.
		                      |br|
		                      Build the path from geometric segments and draw it as a
		                      :class:`~pyTooling.Cartesian2D.Drawing.Path`.
		:raises ValueError:   If an element of parameter 'segments' doesn't start at the end point of the previous
		                      element.
		:raises ValueError:   If parameter 'segments' is empty.
		:raises ValueError:   If parameter 'closed' is None.
		:raises TypeError:    If parameter 'closed' is not of type :class:`bool`.
		:raises ValueError:   If parameter 'closed' is ``True``, while the last segment doesn't end at the start point of
		                      the first segment.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

		if segments is None:
			raise ValueError("Parameter 'segments' is None.")
		elif not isinstance(segments, Iterable):
			ex = TypeError("Parameter 'segments' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segments)}'.")
			raise ex

		segmentList = []
		for segment in segments:
			if segment is None:
				raise ValueError("An element of parameter 'segments' is None.")
			elif not isinstance(segment, Segment2D):
				ex = TypeError("An element of parameter 'segments' is not of type 'Segment2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
				raise ex
			elif not issubclass(self.__class__, segment._PARENT_TYPE):
				ex = TypeError("An element of parameter 'segments' can't be an edge of a path.")
				ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
				ex.add_note("Build the path from geometric segments and draw it as a Drawing.Path.")
				raise ex
			elif len(segmentList) > 0 and (
				segment._start._x != (previousEnd := segmentList[-1]._end)._x or segment._start._y != previousEnd._y
			):
				ex = ValueError("An element of parameter 'segments' doesn't start at the end point of the previous element.")
				ex.add_note(f"Got end point {previousEnd} and start point {segment._start}.")
				raise ex

			segmentList.append(segment)

		if len(segmentList) == 0:
			raise ValueError("Parameter 'segments' is empty.")

		if closed is None:
			raise ValueError("Parameter 'closed' is None.")
		elif not isinstance(closed, bool):
			ex = TypeError("Parameter 'closed' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(closed)}'.")
			raise ex
		elif closed and (
			(firstStart := segmentList[0]._start)._x != (lastEnd := segmentList[-1]._end)._x or firstStart._y != lastEnd._y
		):
			ex = ValueError("Parameter 'closed' is True, while the last segment doesn't end at the first segment's start.")
			ex.add_note(f"Got start point {firstStart} and end point {lastEnd}.")
			raise ex

		pointList = [segmentList[0]._start.Copy()]
		for segment in segmentList[:-1]:
			pointList.append(segment._end.Copy())

		if not closed:
			pointList.append(segmentList[-1]._end.Copy())

		self._points = joints = tuple(pointList)
		for joint in joints:
			joint._parent = self

		self._closed =   closed
		self._segments = tuple(
			segment._CopyAsEdge(start, end, self)
			for segment, start, end in zip(segmentList, joints, (*joints[1:], joints[0]))
		)

		self.Parent = parent

	@readonly
	def Points(self) -> tuple[Point2D[Coordinate], ...]:
		"""
		Read-only property to access the joints of the path's segments (:attr:`_points`).

		:returns: Tuple of joints, from the start point of the first segment to the end point of the last one. A closed
		          path lists its start point once.
		"""
		return self._points

	@readonly
	def Segments(self) -> tuple[Segment2D[Coordinate], ...]:
		"""
		Read-only property to access the path's edges (:attr:`_segments`).

		:returns: Tuple of edges, in drawing order.
		"""
		return self._segments

	@readonly
	def IsClosed(self) -> bool:
		"""
		Read-only property to access, if the path ends at the start point of its first segment (:attr:`_closed`).

		:returns: ``True``, if the path is closed.
		"""
		return self._closed

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the length of the path, the sum of its segments' lengths.

		:returns:                      Length of the path.
		:raises InvalidOperationError: If a segment has no length, like a Bezier curve.
		"""
		length = 0.0
		for segment in self._segments:
			if not isinstance(segment, (LineSegment2D, ArcSegment2D)):
				ex = InvalidOperationError("Path has a segment without a length.")
				ex.add_note(f"Got {segment!r}.")
				raise ex

			length += segment.Length

		return length

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the path.

		The box is the union of the segments' bounding boxes, so it encloses curves bulging past their end points.

		:returns: A new bounding box.
		"""
		box = self._segments[0].BoundingBox
		for segment in self._segments[1:]:
			box = box.Union(segment.BoundingBox)

		return box

	def AppendSegment(self, segment: Segment2D[Coordinate]) -> None:
		"""
		Append a segment at the end of the path.

		The segment must start at the path's end point. The path copies it as an edge, which starts at the path's last
		joint; the copy's end point becomes the path's new end point. Like the initializer, the edge references the
		segment's value and holds a shallow copy of its key-value-pairs. The given segment stays as it is.

		:param segment:                The segment to append.
		:raises ValueError:            If parameter 'segment' is None.
		:raises TypeError:             If parameter 'segment' is not of type :class:`~pyTooling.Cartesian2D.Segment2D`.
		:raises TypeError:             If parameter 'segment' can't be an edge of a path, like a drawable segment. |br|
		                               Build the path from geometric segments and draw it as a
		                               :class:`~pyTooling.Cartesian2D.Drawing.Path`.
		:raises ValueError:            If parameter 'segment' doesn't start at the end point of the path.
		:raises InvalidOperationError: If the path is closed. |br|
		                               A closed path doesn't get opened by appending a segment.
		"""
		if segment is None:
			raise ValueError("Parameter 'segment' is None.")
		elif not isinstance(segment, Segment2D):
			ex = TypeError("Parameter 'segment' is not of type 'Segment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
			raise ex
		elif not issubclass(self.__class__, segment._PARENT_TYPE):
			ex = TypeError("Parameter 'segment' can't be an edge of a path.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
			ex.add_note("Build the path from geometric segments and draw it as a Drawing.Path.")
			raise ex
		elif self._closed:
			ex = InvalidOperationError("Path is closed.")
			ex.add_note("A closed path doesn't get opened by appending a segment.")
			raise ex
		elif segment._start._x != (lastJoint := self._points[-1])._x or segment._start._y != lastJoint._y:
			ex = ValueError("Parameter 'segment' doesn't start at the end point of the path.")
			ex.add_note(f"Got start point {segment._start}, expected {lastJoint}.")
			raise ex

		end =         segment._end.Copy()
		end._parent = self
		edge =        segment._CopyAsEdge(lastJoint, end, self)

		self._points +=   (end, )
		self._segments += (edge, )

	def PrependSegment(self, segment: Segment2D[Coordinate]) -> None:
		"""
		Prepend a segment at the start of the path.

		The segment must end at the path's start point. The path copies it as an edge, which ends at the path's first
		joint; the copy's start point becomes the path's new start point. Like the initializer, the edge references the
		segment's value and holds a shallow copy of its key-value-pairs. The given segment stays as it is.

		:param segment:                The segment to prepend.
		:raises ValueError:            If parameter 'segment' is None.
		:raises TypeError:             If parameter 'segment' is not of type :class:`~pyTooling.Cartesian2D.Segment2D`.
		:raises TypeError:             If parameter 'segment' can't be an edge of a path, like a drawable segment. |br|
		                               Build the path from geometric segments and draw it as a
		                               :class:`~pyTooling.Cartesian2D.Drawing.Path`.
		:raises ValueError:            If parameter 'segment' doesn't end at the start point of the path.
		:raises InvalidOperationError: If the path is closed. |br|
		                               A closed path doesn't get opened by prepending a segment.
		"""
		if segment is None:
			raise ValueError("Parameter 'segment' is None.")
		elif not isinstance(segment, Segment2D):
			ex = TypeError("Parameter 'segment' is not of type 'Segment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
			raise ex
		elif not issubclass(self.__class__, segment._PARENT_TYPE):
			ex = TypeError("Parameter 'segment' can't be an edge of a path.")
			ex.add_note(f"Got type '{getFullyQualifiedName(segment)}'.")
			ex.add_note("Build the path from geometric segments and draw it as a Drawing.Path.")
			raise ex
		elif self._closed:
			ex = InvalidOperationError("Path is closed.")
			ex.add_note("A closed path doesn't get opened by prepending a segment.")
			raise ex
		elif segment._end._x != (firstJoint := self._points[0])._x or segment._end._y != firstJoint._y:
			ex = ValueError("Parameter 'segment' doesn't end at the start point of the path.")
			ex.add_note(f"Got end point {segment._end}, expected {firstJoint}.")
			raise ex

		start =         segment._start.Copy()
		start._parent = self
		edge =          segment._CopyAsEdge(start, firstJoint, self)

		self._points =   (start, ) + self._points
		self._segments = (edge, ) + self._segments

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the path by moving all its points (inplace).

		Each joint moves once, and each edge moves its other points, like a Bezier curve's control points.

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

		for segment in self._segments:
			segment._MoveInner(offset)

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the path at a horizontal axis by mirroring all its points (inplace).

		Each joint is mirrored once, and each edge mirrors its other points; an arc reverses its direction.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		for point in self._points:
			point._y = twiceAxis - point._y

		for segment in self._segments:
			segment._MirrorInnerY(twiceAxis)

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the path at a vertical axis by mirroring all its points (inplace).

		Each joint is mirrored once, and each edge mirrors its other points; an arc reverses its direction.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		for point in self._points:
			point._x = twiceAxis - point._x

		for segment in self._segments:
			segment._MirrorInnerX(twiceAxis)

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the path at a line by mirroring all its points (inplace).

		Each joint is mirrored once, and each edge mirrors its other points; an arc reverses its direction.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		for point in self._points:
			point._MirrorAt(normal, distance)

		for segment in self._segments:
			segment._MirrorInnerAt(normal, distance)

	def ToPolyline(self) -> Polyline[Coordinate]:
		"""
		Create a new polyline with the joints of this path as its points.

		An open path becomes an open polyline, a closed path a closed one. The polyline holds copies of the joints. It
		references the same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns:                      A new polyline.
		:raises InvalidOperationError: If a segment isn't a line segment. |br|
		                               A curved segment can't be converted without an approximation.
		"""
		for segment in self._segments:
			if not isinstance(segment, LineSegment2D):
				ex = InvalidOperationError(f"{self.__class__.__name__} has a segment, which isn't a line segment.")
				ex.add_note(f"Got {segment!r}.")
				ex.add_note("A curved segment can't be converted without an approximation.")
				raise ex

		return Polyline(self._points, closed=self._closed, value=self._value, keyValuePairs=self._dict)

	def ToPolygon(self) -> Polygon[Coordinate]:
		"""
		Create a new polygon with the joints of this closed path as its corners.

		The polygon holds copies of the joints. It references the same :attr:`Value` and holds a shallow copy of the
		key-value-pairs.

		:returns:                      A new polygon.
		:raises InvalidOperationError: If the path is open. |br|
		                               Only a closed path encloses an area.
		:raises InvalidOperationError: If a segment isn't a line segment. |br|
		                               A curved segment can't be converted without an approximation.
		:raises CrossingEdgesError:    If two edges have a point in common, which isn't their shared joint.
		"""
		if not self._closed:
			ex = InvalidOperationError(f"{self.__class__.__name__} is open.")
			ex.add_note("Only a closed path encloses an area.")
			raise ex

		for segment in self._segments:
			if not isinstance(segment, LineSegment2D):
				ex = InvalidOperationError(f"{self.__class__.__name__} has a segment, which isn't a line segment.")
				ex.add_note(f"Got {segment!r}.")
				ex.add_note("A curved segment can't be converted without an approximation.")
				raise ex

		return Polygon(self._points, value=self._value, keyValuePairs=self._dict)

	def Copy(self) -> Self:
		"""
		Create a new path as a copy of this path.

		The copy holds copies of all points, and its edges share the copied joints. It references the same :attr:`Value`
		and holds a shallow copy of the key-value-pairs; so do its edges.

		:returns: Copy of this path.
		"""
		return self.__class__(self._segments, closed=self._closed, value=self._value, keyValuePairs=self._dict)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this path for :func:`copy.copy`.

		:returns: Copy of this path.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this path for :func:`copy.deepcopy`.

		The copy holds copies of all points, and deep copies of the :attr:`Value` and the key-value-pairs. Its edges
		are copied as by :meth:`Copy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this path.
		"""
		return self.__class__(
			self._segments,
			closed=self._closed,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def __repr__(self) -> str:
		"""
		Returns the path's string representation.

		:returns: The string representation of the path, its segments and whether it is closed.
		"""
		return f"Path({', '.join(repr(segment) for segment in self._segments)}, closed={self._closed})"

	def __str__(self) -> str:
		"""
		Returns the path's string equivalent.

		:returns: The string equivalent of the path, its segments in drawing order.
		"""
		segments = ", ".join(str(segment) for segment in self._segments)
		return f"({segments}, closed)" if self._closed else f"({segments})"


@export
class Polyline(Path[Coordinate], Generic[Coordinate]):
	"""
	A polyline is a path of line segments, connecting two or more points (vertices) by straight edges.

	An open polyline runs from its first point to its last point. A closed polyline connects its last point back to its
	first point; it needs three or more points.
	"""

	def __init__(
		self,
		points:        Iterable[Point2D[Coordinate]],
		*,
		closed:        bool = False,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a polyline from its points.

		The points are connected in the given order, from the first one to the last one, and for a closed polyline back to
		the first one. Consecutive edges share their point.

		The polyline owns its points. Referenced points (``copyPoints=False``) must not be owned by another element.

		:param points:                 Points of the polyline.
		:param closed:                 Optional, if ``True``, the last point is connected back to the first point. Default:
		                               ``False``.
		:param copyPoints:             Optional, if ``True``, the given points are copied instead of referenced. Default:
		                               ``True``.
		:param value:                  Optional, value of the polyline. Default: ``None``.
		:param keyValuePairs:          Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:                 Optional, the group or canvas the polyline is added to. Default: ``None``, no
		                               parent.
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
		:raises NotEnoughCornersError: If parameter 'points' has fewer than 2 points.
		:raises ValueError:            If parameter 'closed' is None.
		:raises TypeError:             If parameter 'closed' is not of type :class:`bool`.
		:raises NotEnoughCornersError: If parameter 'closed' is ``True``, while parameter 'points' has fewer than 3
		                               points.
		:raises ValueError:            If parameter 'copyPoints' is None.
		:raises TypeError:             If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:             If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:             If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D`
		                               or :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		# Path's initializer takes segments; a polyline is built from its points.
		super(Path, self).__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		if closed is None:
			raise ValueError("Parameter 'closed' is None.")
		elif not isinstance(closed, bool):
			ex = TypeError("Parameter 'closed' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(closed)}'.")
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

		if len(pointList) < 2:
			ex = NotEnoughCornersError("Polyline has fewer than 2 points.")
			ex.add_note(f"Got {len(pointList)} points.")
			raise ex from ValueError("Parameter 'points' has fewer than 2 points.")
		elif closed and len(pointList) < 3:
			ex = NotEnoughCornersError("Closed polyline has fewer than 3 points.")
			ex.add_note(f"Got {len(pointList)} points.")
			raise ex from ValueError("Parameter 'points' has fewer than 3 points, while parameter 'closed' is True.")

		self._points = vertices = tuple(pointList)
		for vertex in vertices:
			vertex._parent = self

		self._closed =   closed
		self._segments = tuple(
			LineSegment2D(start, end, copyPoints=False, parent=self)
			for start, end in zip(vertices, (*vertices[1:], vertices[0]) if closed else vertices[1:])
		)

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new polyline as a copy of this polyline.

		The copy holds copies of the points, shared by its edges. It references the same :attr:`Value` and holds a shallow
		copy of the key-value-pairs.

		:returns: Copy of this polyline.
		"""
		return self.__class__(self._points, closed=self._closed, value=self._value, keyValuePairs=self._dict)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this polyline for :func:`copy.deepcopy`.

		The copy holds copies of the points, and deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this polyline.
		"""
		return self.__class__(
			self._points,
			closed=self._closed,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def __repr__(self) -> str:
		"""
		Returns the polyline's string representation.

		:returns: The string representation of the polyline, its points, and ``closed=True`` for a closed polyline.
		"""
		points = ", ".join(str(point) for point in self._points)
		return f"Polyline({points}, closed=True)" if self._closed else f"Polyline({points})"

	def __str__(self) -> str:
		"""
		Returns the polyline's string equivalent.

		:returns: The string equivalent of the polyline, its points in drawing order, for a closed polyline back to the
		          first point.
		"""
		points = (*self._points, self._points[0]) if self._closed else self._points
		return f"({' → '.join(str(point) for point in points)})"
