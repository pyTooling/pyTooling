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
An implementation of 2D cartesian data structures for Python.

.. seealso::

   :mod:`pyTooling.Cartesian3D`
      |rarr| The same data structures in three dimensions.
   :mod:`pyTooling.Cartesian2D.Shapes`
      |rarr| Shapes built from these points and offsets.
"""
from __future__            import annotations

from copy                  import deepcopy
from enum                  import Enum
from math                  import atan2, isclose, pi, sqrt
from typing                import TYPE_CHECKING, Any, ClassVar, Generic, Hashable, Iterable, Mapping, \
                                  Optional as Nullable, Self, TypeVar, Union

from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType, abstractclass, abstractmethod
from pyTooling.Exceptions  import ToolingException, AlreadyInHierarchyError, CycleError, DuplicateElementError, \
                                  InvalidOperationError, NotAChildError, NotInSameHierarchyError
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.DataModel   import KeyValuePairsMixin

if TYPE_CHECKING:
	from pyTooling.Cartesian2D.Shapes import Rectangle, Shape
	from pyTooling.Cartesian2D.Groups import Group2D, Canvas2D


Coordinate = TypeVar("Coordinate", bound=Union[int, float])


@export
def chordPoint(
	start:          Point2D[Coordinate],
	end:            Point2D[Coordinate],
	chordPosition:  float,
	relativeHeight: Union[int, float]
) -> Point2D[float]:
	"""
	Compute the point at a height over a chord, perpendicular to the chord at a root point.

	:param start:          Start point of the chord.
	:param end:            End point of the chord.
	:param chordPosition:  The root point's position on the chord, as a fraction from the start point.
	:param relativeHeight: Signed distance of the point from the chord, as a fraction of the chord length. A positive
	                       height is on the left of the chord, seen from the start point.
	:returns:              A new 2D-point without owner.
	:raises ValueError:    If parameter 'start' is None.
	:raises TypeError:     If parameter 'start' is not of type :class:`Point2D`.
	:raises ValueError:    If parameter 'end' is None.
	:raises TypeError:     If parameter 'end' is not of type :class:`Point2D`.
	:raises ValueError:    If parameter 'chordPosition' is None.
	:raises TypeError:     If parameter 'chordPosition' is not of type :class:`float` or :class:`int`.
	:raises ValueError:    If parameter 'relativeHeight' is None.
	:raises TypeError:     If parameter 'relativeHeight' is not of type :class:`float` or :class:`int`.
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

	for name, value in (
		("chordPosition",  chordPosition),
		("relativeHeight", relativeHeight)
	):
		if value is None:
			raise ValueError(f"Parameter '{name}' is None.")
		elif not isinstance(value, (float, int)):
			ex = TypeError(f"Parameter '{name}' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

	chordX = end._x - start._x
	chordY = end._y - start._y
	return Point2D(
		start._x + chordPosition * chordX - relativeHeight * chordY,
		start._y + chordPosition * chordY + relativeHeight * chordX
	)


@export
def circumcenter(
	first:  Point2D[Coordinate],
	second: Point2D[Coordinate],
	third:  Point2D[Coordinate]
) -> Point2D[float]:
	"""
	Compute the center of the circle through three points, which aren't on one line.

	:param first:       First point of the circle.
	:param second:      Second point of the circle.
	:param third:       Third point of the circle.
	:returns:           A new 2D-point without owner.
	:raises ValueError: If parameter 'first' is None.
	:raises TypeError:  If parameter 'first' is not of type :class:`Point2D`.
	:raises ValueError: If parameter 'second' is None.
	:raises TypeError:  If parameter 'second' is not of type :class:`Point2D`.
	:raises ValueError: If parameter 'third' is None.
	:raises TypeError:  If parameter 'third' is not of type :class:`Point2D`.
	:raises ValueError: If the three points are on one line. |br|
	                    Three points on one line have no circle through them.
	"""
	for name, point in (
		("first",  first),
		("second", second),
		("third",  third)
	):
		if point is None:
			raise ValueError(f"Parameter '{name}' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError(f"Parameter '{name}' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

	secondX = second._x - first._x
	secondY = second._y - first._y
	thirdX =  third._x - first._x
	thirdY =  third._y - first._y
	if (cross := secondX * thirdY - secondY * thirdX) == 0:
		ex = ValueError("Parameters 'first', 'second' and 'third' are on one line.")
		ex.add_note(f"Got points {first}, {second} and {third}.")
		ex.add_note("Three points on one line have no circle through them.")
		raise ex

	secondSquare = secondX ** 2 + secondY ** 2
	thirdSquare =  thirdX ** 2 + thirdY ** 2
	return Point2D(
		first._x + (thirdY * secondSquare - secondY * thirdSquare) / (2 * cross),
		first._y + (secondX * thirdSquare - thirdX * secondSquare) / (2 * cross)
	)


@export
class Alignment2D(Enum):
	"""
	Edge or center of a bounding box, two elements are aligned at.

	The members name the smaller or larger coordinate, like :class:`BoundingBox2D`, so they don't depend on the direction
	of an axis.
	"""

	MinX =    0  #: Align the smallest x-coordinates.
	CenterX = 1  #: Align the centers in x-direction.
	MaxX =    2  #: Align the largest x-coordinates.
	MinY =    3  #: Align the smallest y-coordinates.
	CenterY = 4  #: Align the centers in y-direction.
	MaxY =    5  #: Align the largest y-coordinates.


@export
class SweepDirection(Enum):
	"""
	Direction, in which an arc sweeps from its start point to its end point.

	The names refer to a y-axis pointing up. On a canvas with the y-axis pointing down, as on a screen or in SVG, a
	counterclockwise arc appears clockwise.
	"""

	Counterclockwise = 0  #: The angle grows from the start point to the end point.
	Clockwise =        1  #: The angle shrinks from the start point to the end point.


@export
class Cartesian2DError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Cartesian2D` and :mod:`pyTooling.Cartesian3D`."""


@export
class NoAreaError(Cartesian2DError):
	"""The exception is raised when an operation needs an area, but a bounding box has no width or no height."""


@export
class AlreadyOwnedError(Cartesian2DError, AlreadyInHierarchyError):
	"""
	The exception is raised when an element is given to an element, but another element owns it already.

	For example, a point given to a shape with ``copyPoints=False`` while another shape owns it.

	:mod:`pyTooling.Cartesian3D` raises it too.
	"""


@export
class NotOwnedError(Cartesian2DError, NotAChildError):
	"""
	The exception is raised when an element replaces or removes an element it doesn't own.

	For example, an edge of a polygon references the polygon's corners, so it can't replace them.

	:mod:`pyTooling.Cartesian3D.Groups` raises it too.
	"""


@export
class DuplicatePointError(Cartesian2DError, DuplicateElementError):
	"""
	The exception is raised when the same point object is given twice to an element.

	For example, the same point as start and end point of a segment with ``copyPoints=False``. Two different point objects
	with equal coordinates aren't a duplicate.

	:mod:`pyTooling.Cartesian3D` raises it too.
	"""


@export
class NotEnoughCornersError(Cartesian2DError):
	"""
	The exception is raised when a shape is given fewer corners than it needs.

	For example, a polygon given fewer than 3 corners, or a polyline given fewer than 2 points.
	"""


@export
class CrossingEdgesError(Cartesian2DError):
	"""
	The exception is raised when edges of a polygon have a point in common, which isn't their shared corner.

	For example, two edges crossing each other, a corner on another edge, or an edge running back along the previous one.
	"""


@export
class GroupCycleError(Cartesian2DError, CycleError):
	"""
	The exception is raised when a group would become its own parent or the parent of one of its ancestors.

	:mod:`pyTooling.Cartesian3D` raises it too.
	"""


@export
class NotInSameFrameError(Cartesian2DError, NotInSameHierarchyError):
	"""
	The exception is raised when points or segments of different frames are combined in a computation.

	A frame is what the coordinates of an element are relative to. Combining coordinates of different frames would mix
	unrelated values silently.

	:mod:`pyTooling.Cartesian3D` raises it too.
	"""


@export
@abstractclass
class Base2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of everything having a parent and coordinates relative to a frame: points, segments, shapes,
	groups and canvases.

	A frame is what the coordinates are relative to, and a group or canvas is the frame of its children. Every frame is an
	instance of this class.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]]  #: Types a parent of this class can have.

	_parent: Nullable[Base2D[Coordinate]]  #: Parent of this object, or ``None``.

	def __init__(self, *, parent: Nullable[Base2D[Coordinate]] = None) -> None:
		"""
		Initializes the parent relation.

		:param parent:     Optional, the parent of this object. Default: ``None``, no parent.
		:raises TypeError: If parameter 'parent' is not of a type in :attr:`_PARENT_TYPE`.
		"""
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex = TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@property
	def Parent(self) -> Nullable[Base2D[Coordinate]]:
		"""
		Property to access the parent of this object (:attr:`_parent`).

		A point's parent is the segment or shape owning it. A segment's parent is the shape it's an edge of, or the group
		or canvas holding it. A shape's or group's parent is the group or canvas holding it.

		Only an :class:`Element2D` can be assigned a parent. Assigning a group or canvas moves the element into it,
		assigning ``None`` removes it from its parent. The element keeps its local coordinates, so its absolute position
		changes with the frame. Use :meth:`Element2D.MoveTo` to keep the absolute position.

		:returns:                  The parent, or ``None``, if this object has no parent.
		:raises TypeError:         If an assigned value is not of a type in :attr:`_PARENT_TYPE`.
		:raises TypeError:         If a parent is assigned to a :class:`Point2D`.
		:raises TypeError:         If a parent is assigned to a :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises TypeError:         If an assigned value is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`, while this object is an
		                           :class:`Element2D`.
		:raises AlreadyOwnedError: If the element is an edge of a shape.
		:raises GroupCycleError:   If an assigned group is this element or one of its descendants.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: Nullable[Base2D[Coordinate]]) -> None:
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex = TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@readonly
	def Frame(self) -> Nullable[Base2D[Coordinate]]:
		"""
		Read-only property to return the frame this object's coordinates are relative to.

		The frame comes from the parent. An object without a parent has no frame, its coordinates are relative to the
		origin.

		:returns: The frame, or ``None``, if this object has no frame.
		"""
		return None if self._parent is None else self._parent._ChildFrame

	@readonly
	def _ChildFrame(self) -> Nullable[Base2D[Coordinate]]:
		"""
		Read-only property to access the frame the coordinates of this object's children are relative to (:attr:`Frame`).

		:returns: This object's frame, or ``None``, if this object has no frame.
		"""
		return self.Frame


@export
class Point2D(Base2D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 2D cartesian point."""

	_x: Coordinate  #: The x-direction coordinate.
	_y: Coordinate  #: The y-direction coordinate.

	def __init__(self, x: Coordinate, y: Coordinate, *, parent: Nullable[Element2D[Coordinate]] = None) -> None:
		"""
		Initializes a 2-dimensional point.

		A shape or segment takes ownership of the point, when it's given the point instead of copying it.

		Parameter ``parent`` sets the owner, but doesn't register the point in it: the parent's points don't change. The
		point is in the parent's frame, so it can be combined with the parent's points.

		:param x:           X-coordinate.
		:param y:           Y-coordinate.
		:param parent:      Optional, the segment or shape owning the point. Default: ``None``, no owner.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Element2D`.
		"""
		super().__init__(parent=parent)

		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._x = x
		self._y = y

	@Base2D.Parent.setter
	def Parent(self, parent: Nullable[Element2D[Coordinate]]) -> None:
		ex = TypeError(f"The parent of a '{getFullyQualifiedName(self)}' is read-only.")
		ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
		ex.add_note("A segment or shape takes ownership of a point, when it's given the point.")
		raise ex

	@property
	def X(self) -> Coordinate:
		"""
		Property to access the x-direction coordinate (:attr:`_x`).

		``x`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._x

	@X.setter
	def X(self, x: Coordinate) -> None:
		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		self._x = x

	x = X

	@property
	def Y(self) -> Coordinate:
		"""
		Property to access the y-direction coordinate (:attr:`_y`).

		``y`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._y

	@Y.setter
	def Y(self, y: Coordinate) -> None:
		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._y = y

	y = Y

	@readonly
	def Absolute(self) -> Point2D[Coordinate]:
		"""
		Read-only property to return the point's position relative to the origin as a new 2D-point.

		The offsets of all groups up the parent chain are added to the point's coordinates. The new point has no owner.

		:returns: A new 2D-point with absolute coordinates.
		"""
		if (frame := self.Frame) is None:
			return Point2D(self._x, self._y)

		offset = frame.AbsoluteOffset
		return Point2D(self._x + offset._xOffset, self._y + offset._yOffset)

	def Copy(self) -> Self:
		"""
		Create a new 2D-point as a copy of this 2D point.

		The copy has no owner.

		:returns: Copy of this 2D-point.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 2D-point moved by a positive 2D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 2D-point moved by a negative 2D-offset.
		"""
		return self.__class__(self._x, self._y)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 2D-point for :func:`copy.copy`.

		:returns: Copy of this 2D-point.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D-point for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D-point.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-Point to a simple 2-element tuple.

		:returns: ``(x, y)`` tuple.
		"""
		return self._x, self._y

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the point at the line ``nx * x + ny * y = distance`` in the point's frame (inplace).

		The point moves by ``-2 * (nx * x + ny * y - distance)`` times the normal.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		factor = 2 * (normal._xOffset * self._x + normal._yOffset * self._y - distance)
		self._x -= factor * normal._xOffset
		self._y -= factor * normal._yOffset

	def __add__(self, other: Any) -> Point2D[Coordinate]:
		"""
		Adds a 2D-vector to this 2D-point and creates a new 2D-point.

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          A new 2D-point shifted by the 2D-vector.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			return self.__class__(
				self._x + other._xOffset,
				self._y + other._yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._x + other[0],
				self._y + other[1]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 2D-vector to this 2D-point (inplace).

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			self._x += other._xOffset
			self._y += other._yOffset
		elif isinstance(other, tuple):
			self.X += other[0]
			self.Y += other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union[Offset2D[Coordinate], Point2D[Coordinate]]:
		"""
		Subtract a 2D-point from this 2D-point and create a new 2D-offset, or a 2D-vector and create a new 2D-point.

		:param other:                The second 2D-point as :class:`Point2D`, or a 2D-vector as :class:`Vector2D` or
		                             :class:`Offset2D`.
		:returns:                    A new 2D-offset representing the distance between these two points, or a new 2D-point
		                             shifted back by the 2D-vector.
		:raises TypeError:           If parameter 'other' is not of type :class:`Point2D` or :class:`BaseVector2D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this point. |br|
		                             Subtract the points' :attr:`Absolute` positions instead.
		"""
		if isinstance(other, Point2D):
			if self.Frame is not other.Frame:
				ex = NotInSameFrameError("Points are in different frames.")
				ex.add_note(f"Got points {self} and {other}.")
				ex.add_note("Subtract the points' 'Absolute' positions instead.")
				raise ex from ValueError("Parameter 'other' is in another frame.")

			return Offset2D(
				self._x - other._x,
				self._y - other._y
			)
		elif isinstance(other, BaseVector2D):
			return Point2D(
				self._x - other._xOffset,
				self._y - other._yOffset
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Point2D' or 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 2D-vector from this 2D-point (inplace).

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			self._x -= other._xOffset
			self._y -= other._yOffset
		elif isinstance(other, tuple):
			self.X -= other[0]
			self.Y -= other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 2D point's string representation.

		:returns: The string representation of the 2D point.
		"""
		return f"Point2D({self._x}, {self._y})"

	def __str__(self) -> str:
		"""
		Returns the 2D point's string equivalent.

		:returns: The string equivalent of the 2D point.
		"""
		return f"({self._x}, {self._y})"


@export
class Origin2D(Point2D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 2D cartesian origin."""

	def __init__(self) -> None:
		"""
		Initializes a 2-dimensional origin.
		"""
		super().__init__(0, 0)

	def Copy(self) -> Self:
		"""
		An origin is a singular point, so it can't be copied.

		:raises InvalidOperationError: Always, because an origin is a singular point.
		"""
		raise InvalidOperationError("An origin can't be copied.")

	def __repr__(self) -> str:
		"""
		Returns the 2D origin's string representation.

		:returns: The string representation of the 2D origin.
		"""
		return f"Origin2D({self._x}, {self._y})"


@export
@abstractclass
class Element2D(Base2D[Coordinate], KeyValuePairsMixin, Generic[Coordinate]):
	"""
	Abstract base-class of all elements a :class:`~pyTooling.Cartesian2D.Groups.Group2D` or a
	:class:`~pyTooling.Cartesian2D.Groups.Canvas2D` can hold: shapes, segments and groups.

	An element belongs to at most one group or canvas, its :attr:`Parent`. Its coordinates are relative to its parent, an
	element without a parent is relative to the origin.

	An element carries an optional :attr:`Value` and arbitrary key-value-pairs
	(:class:`~pyTooling.DataModel.KeyValuePairsMixin`). Use the dictionary syntax to get and set key-value-pairs:
	``in``, :pycode:`len(element)` and iterating an element address the key-value-pairs, not its points or children.

	A derived class implements :attr:`BoundingBox`, :meth:`Move`, :meth:`_MirrorX`, :meth:`_MirrorY` and
	:meth:`_MirrorAt`. Its initializer takes the keyword-only parameters ``value``, ``keyValuePairs`` and ``parent``, and
	assigns ``parent`` to :attr:`Parent` as its last statement, when the element is fully initialized.
	"""

	# WORKAROUND: Python <3.13
	# A type variable with a default (PEP 696) isn't supported by Python 3.11 and 3.12. Use it when their support gets
	# dropped:
	# ValueType = TypeVar("ValueType", default=Any)
	# class Element2D(Base2D[Coordinate], KeyValuePairsMixin, Generic[Coordinate, ValueType]): ... _value: ValueType
	_value: Any  #: Value of the element.

	def __init__(
		self,
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes an element without a parent and checks the group or canvas it will be registered in.

		:param value:         Optional, value of the element. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the derived class registers the element in. Default:
		                      ``None``, no parent.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		# Imported for its side effect: it assigns '_PARENT_TYPE' of the element classes.
		from pyTooling.Cartesian2D import Groups

		super().__init__(parent=parent)
		KeyValuePairsMixin.__init__(self, keyValuePairs)

		# The derived class registers the element by assigning 'Parent' as its last statement.
		self._parent = None
		self._value =  value

	@Base2D.Parent.setter
	def Parent(self, parent: Nullable[Union[Group2D, Canvas2D]]) -> None:
		from pyTooling.Cartesian2D.Groups import Container2DMixin

		if parent is not None and not isinstance(parent, Container2DMixin):
			ex = TypeError("Parameter 'parent' is not of type 'Group2D' or 'Canvas2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		elif parent is self._parent:
			return
		elif self._parent is not None and not isinstance(self._parent, Container2DMixin):
			ex = AlreadyOwnedError("Element is owned by another element already.")
			ex.add_note(f"Got {self!r} owned by {self._parent!r}.")
			raise ex from ValueError("Parameter 'parent' can't replace the shape of an edge.")

		frame = parent
		while frame is not None:
			if frame is self:
				ex = GroupCycleError("Group2D would contain itself.")
				ex.add_note(f"Got {parent!r} as parent of {self!r}.")
				raise ex from ValueError("Parameter 'parent' is this element or one of its descendants.")

			frame = frame.Frame

		if self._parent is not None:
			self._parent._children.remove(self)

		if parent is not None:
			parent._children.append(self)

		Base2D.Parent.fset(self, parent)

	@property
	def Value(self) -> Any:
		"""
		Property to access the element's value (:attr:`_value`).

		The value is any object attached to the element, for example the model object a shape draws. It is neither checked
		nor copied.

		:returns: The element's value, or ``None``, if it has no value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Any) -> None:
		self._value = value

	@readonly
	@abstractmethod
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the element.

		The bounding box is in the element's frame.

		:returns: A new bounding box.
		"""

	@readonly
	def AbsoluteBoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the element's bounding box relative to the origin.

		The offsets of all groups up the parent chain are added to :attr:`BoundingBox`.

		:returns: A new bounding box.
		"""
		frame = self.Frame
		return self.BoundingBox if frame is None else self.BoundingBox + frame.AbsoluteOffset

	@abstractmethod
	def Move(self, offset: BaseVector2D[Coordinate]) -> None:
		"""
		Move the element by an offset in its frame (inplace).

		:param offset: The 2D-vector or 2D-offset to move by.
		"""

	def MirrorX(self, axis: Alignment2D = Alignment2D.CenterX, offset: Coordinate = 0) -> None:
		r"""
		Mirror the element vertically, at a vertical axis through its bounding box (inplace).

		The axis runs through the smallest x-coordinate (``MinX``), the center (``CenterX``) or the largest x-coordinate
		(``MaxX``) of the element's :attr:`BoundingBox`, shifted by ``offset`` in x-direction. For an axis at ``x = a``,
		every x-coordinate ``x`` becomes ``2a - x``; the y-coordinates stay. A group mirrors its offset, and its children
		at the group's origin.

		Mirrored at ``Alignment2D.MaxX``: the element on the left of the axis is mirrored to the right of it.

		.. code-block:: text

		             axis at MaxX
		             |
		        +----+----+
		        | \  |  / |
		        |  \ | /  |
		        +----+----+
		             |
		        before  after

		:param axis:        Optional, the edge or center of the bounding box the axis runs through. Default:
		                    ``Alignment2D.CenterX``.
		:param offset:      Optional, the distance of the axis from that edge or center in x-direction. Default: ``0``.
		:raises ValueError: If parameter 'axis' is None.
		:raises TypeError:  If parameter 'axis' is not of type :class:`Alignment2D`.
		:raises ValueError: If parameter 'axis' is not ``MinX``, ``CenterX`` or ``MaxX``.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`float` or :class:`int`.
		"""
		if axis is None:
			raise ValueError("Parameter 'axis' is None.")
		elif not isinstance(axis, Alignment2D):
			ex = TypeError("Parameter 'axis' is not of type 'Alignment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(axis)}'.")
			raise ex
		elif axis not in (Alignment2D.MinX, Alignment2D.CenterX, Alignment2D.MaxX):
			ex = ValueError("Parameter 'axis' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.")
			ex.add_note(f"Got value '{axis}'.")
			raise ex

		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, (int, float)):
			ex = TypeError("Parameter 'offset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		box = self.BoundingBox
		if axis is Alignment2D.MinX:
			twiceAxis = 2 * box._minX
		elif axis is Alignment2D.CenterX:
			twiceAxis = box._minX + box._maxX
		else:
			twiceAxis = 2 * box._maxX

		self._MirrorX(twiceAxis + 2 * offset)

	@abstractmethod
	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the element at a vertical axis, so every x-coordinate ``x`` becomes ``twiceAxis - x`` (inplace).

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""

	def MirrorY(self, axis: Alignment2D = Alignment2D.CenterY, offset: Coordinate = 0) -> None:
		r"""
		Mirror the element horizontally, at a horizontal axis through its bounding box (inplace).

		The axis runs through the smallest y-coordinate (``MinY``), the center (``CenterY``) or the largest y-coordinate
		(``MaxY``) of the element's :attr:`BoundingBox`, shifted by ``offset`` in y-direction. For an axis at ``y = a``,
		every y-coordinate ``y`` becomes ``2a - y``; the x-coordinates stay. A group mirrors its offset, and its children
		at the group's origin.

		Mirrored at ``Alignment2D.MinY``, with the y-axis pointing up: the element above the axis is mirrored below it.

		.. code-block:: text

		        +----+
		        |  \ |    before
		        |   \|
		     ---+----+--- axis at MinY
		        |   /|
		        |  / |    after
		        +----+

		:param axis:        Optional, the edge or center of the bounding box the axis runs through. Default:
		                    ``Alignment2D.CenterY``.
		:param offset:      Optional, the distance of the axis from that edge or center in y-direction. Default: ``0``.
		:raises ValueError: If parameter 'axis' is None.
		:raises TypeError:  If parameter 'axis' is not of type :class:`Alignment2D`.
		:raises ValueError: If parameter 'axis' is not ``MinY``, ``CenterY`` or ``MaxY``.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`float` or :class:`int`.
		"""
		if axis is None:
			raise ValueError("Parameter 'axis' is None.")
		elif not isinstance(axis, Alignment2D):
			ex = TypeError("Parameter 'axis' is not of type 'Alignment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(axis)}'.")
			raise ex
		elif axis not in (Alignment2D.MinY, Alignment2D.CenterY, Alignment2D.MaxY):
			ex = ValueError("Parameter 'axis' is not Alignment2D.MinY, Alignment2D.CenterY or Alignment2D.MaxY.")
			ex.add_note(f"Got value '{axis}'.")
			raise ex

		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, (int, float)):
			ex = TypeError("Parameter 'offset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		box = self.BoundingBox
		if axis is Alignment2D.MinY:
			twiceAxis = 2 * box._minY
		elif axis is Alignment2D.CenterY:
			twiceAxis = box._minY + box._maxY
		else:
			twiceAxis = 2 * box._maxY

		self._MirrorY(twiceAxis + 2 * offset)

	@abstractmethod
	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the element at a horizontal axis, so every y-coordinate ``y`` becomes ``twiceAxis - y`` (inplace).

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""

	@abstractmethod
	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the element at the line ``nx * x + ny * y = distance`` in the element's frame (inplace).

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""

	def MirrorAt(self, line: Line2D[Coordinate]) -> None:
		r"""
		Mirror the element at a line (inplace).

		The line is in absolute coordinates, relative to the origin, so elements of different groups can be mirrored at
		the same line. At a vertical line ``x = a``, every absolute x-coordinate ``x`` becomes ``2a - x``; at a horizontal
		line ``y = a``, every absolute y-coordinate ``y`` becomes ``2a - y``. A :class:`Line2D` with normal ``(1, 0)`` or
		``(0, 1)`` is a vertical or horizontal line too. At an oblique line ``nx * x + ny * y = d``, every absolute point
		``(x, y)`` moves by ``-2 * (nx * x + ny * y - d)`` times the normal. A group mirrors its offset, and its children at
		the line through the group's origin with the same normal.

		Mirrored at a vertical line: the element on the left of the line is mirrored to the right of it.

		.. code-block:: text

		                     x = a
		                       |
		        +----+         |         +----+
		        | \  |         |         |  / |
		        |  \ |         |         | /  |
		        +----+         |         +----+
		                       |
		        before                   after

		:param line:        The line to mirror at, like a :class:`VerticalLine2D` or a :class:`HorizontalLine2D`.
		:raises ValueError: If parameter 'line' is None.
		:raises TypeError:  If parameter 'line' is not of type :class:`Line2D`.
		"""
		if line is None:
			raise ValueError("Parameter 'line' is None.")
		elif not isinstance(line, Line2D):
			ex = TypeError("Parameter 'line' is not of type 'Line2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(line)}'.")
			raise ex

		line._MirrorElement(self)

	def MoveTo(self, parent: Nullable[Union[Group2D, Canvas2D]], keepPosition: bool = True) -> None:
		"""
		Move the element into another group or canvas.

		With ``keepPosition``, the element is moved by the difference of both frames, so its absolute position stays.
		Otherwise, it keeps its local coordinates, like an assignment to :attr:`Parent`.

		:param parent:             The new parent group or canvas, or ``None`` for no parent.
		:param keepPosition:       Optional, if ``True``, the absolute position is kept. Default: ``True``.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises GroupCycleError:   If parameter 'parent' is this element or one of its descendants.
		:raises ValueError:        If parameter 'keepPosition' is None.
		:raises TypeError:         If parameter 'keepPosition' is not of type :class:`bool`.
		:raises AlreadyOwnedError: If the element is an edge of a shape.
		"""
		if keepPosition is None:
			raise ValueError("Parameter 'keepPosition' is None.")
		elif not isinstance(keepPosition, bool):
			ex = TypeError("Parameter 'keepPosition' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keepPosition)}'.")
			raise ex

		frame =          self.Frame
		previousOffset = Offset2D(0, 0) if frame is None else frame.AbsoluteOffset

		self.Parent = parent

		if not keepPosition:
			return

		if (frame := self.Frame) is None:
			self.Move(previousOffset)
		else:
			self.Move(previousOffset - frame.AbsoluteOffset)

	def AlignTo(self, reference: Element2D[Coordinate], alignment: Alignment2D) -> None:
		"""
		Move the element, so an edge or the center of its bounding box aligns with the one of another element.

		Both elements may be in different frames: their absolute bounding boxes are compared.

		:param reference:   The element to align with. It isn't moved.
		:param alignment:   The edge or center to align.
		:raises ValueError: If parameter 'reference' is None.
		:raises TypeError:  If parameter 'reference' is not of type :class:`Element2D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment2D`.
		"""
		if reference is None:
			raise ValueError("Parameter 'reference' is None.")
		elif not isinstance(reference, Element2D):
			ex = TypeError("Parameter 'reference' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reference)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment2D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex

		box =          self.AbsoluteBoundingBox
		referenceBox = reference.AbsoluteBoundingBox
		if alignment is Alignment2D.MinX:
			offset = Offset2D(referenceBox._minX - box._minX, 0)
		elif alignment is Alignment2D.CenterX:
			offset = Offset2D((referenceBox._minX + referenceBox._maxX - box._minX - box._maxX) / 2, 0)
		elif alignment is Alignment2D.MaxX:
			offset = Offset2D(referenceBox._maxX - box._maxX, 0)
		elif alignment is Alignment2D.MinY:
			offset = Offset2D(0, referenceBox._minY - box._minY)
		elif alignment is Alignment2D.CenterY:
			offset = Offset2D(0, (referenceBox._minY + referenceBox._maxY - box._minY - box._maxY) / 2)
		else:
			offset = Offset2D(0, referenceBox._maxY - box._maxY)

		self.Move(offset)


Point2D._PARENT_TYPE = (Element2D, )


@export
@abstractclass
class BaseVector2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of 2D cartesian vectors: the immutable :class:`Vector2D` and the mutable :class:`Offset2D`.

	An operator creating a new vector returns a vector of its left operand's class; the right operand can be a vector of
	either class or a tuple. Vectors of both classes compare equal, if their components are equal.
	"""

	_xOffset: Coordinate  #: The x-direction component.
	_yOffset: Coordinate  #: The y-direction component.

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate) -> None:
		"""
		Initializes a 2-dimensional vector.

		:param xOffset:     x-direction component.
		:param yOffset:     y-direction component.
		:raises ValueError: If parameter 'xOffset' is None.
		:raises TypeError:  If parameter 'xOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'yOffset' is None.
		:raises TypeError:  If parameter 'yOffset' is not of type :class:`float` or :class:`int`.
		"""
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		self._xOffset = xOffset
		self._yOffset = yOffset

	@readonly
	def XOffset(self) -> Coordinate:
		"""
		Read-only property to access the x-direction component (:attr:`_xOffset`).

		:returns: The x-direction component.
		"""
		return self._xOffset

	@readonly
	def YOffset(self) -> Coordinate:
		"""
		Read-only property to access the y-direction component (:attr:`_yOffset`).

		:returns: The y-direction component.
		"""
		return self._yOffset

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean length of this 2D-vector.

		:returns: The Euclidean length.
		"""
		return sqrt(self._xOffset ** 2 + self._yOffset ** 2)

	def ScalarProduct(self, other: BaseVector2D[Coordinate]) -> Coordinate:
		"""
		Compute the :term:`dot product <Dot Product>` of this 2D-vector and another 2D-vector.

		The dot product ``x1 * x2 + y1 * y2`` is zero for perpendicular vectors.

		:param other:       The second 2D-vector.
		:returns:           The dot product.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BaseVector2D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BaseVector2D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._xOffset * other._xOffset + self._yOffset * other._yOffset

	def VectorProduct(self, other: BaseVector2D[Coordinate]) -> Coordinate:
		"""
		Compute the :term:`cross product <Cross Product>` of this 2D-vector and another 2D-vector.

		In 2D, the cross product is the number ``x1 * y2 - y1 * x2``: the z-component of the cross product of both vectors
		as 3D-vectors. It is zero for parallel vectors, and positive, if the other vector points counterclockwise from this
		one.

		:param other:       The second 2D-vector.
		:returns:           The cross product.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BaseVector2D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BaseVector2D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._xOffset * other._yOffset - self._yOffset * other._xOffset

	def Normalized(self) -> Self:
		"""
		Create a new 2D-vector of length 1 in the direction of this 2D-vector.

		:returns:                      A new 2D-vector of length 1, of this vector's class.
		:raises InvalidOperationError: If this 2D-vector is a zero vector. |br|
		                               A zero vector has no direction.
		"""
		if self._xOffset == 0 and self._yOffset == 0:
			ex = InvalidOperationError("A zero vector can't be normalized.")
			ex.add_note(f"Got vector {self}.")
			ex.add_note("A zero vector has no direction.")
			raise ex

		length = sqrt(self._xOffset ** 2 + self._yOffset ** 2)
		return self.__class__(
			self._xOffset / length,
			self._yOffset / length
		)

	def ToTuple(self) -> tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-vector to a simple 2-element tuple.

		:returns: ``(x, y)`` tuple.
		"""
		return self._xOffset, self._yOffset

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two 2D-vectors for equality.

		A :class:`Vector2D` and an :class:`Offset2D` are equal, if their components are equal.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-vectors are equal.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			return self._xOffset == other._xOffset and self._yOffset == other._yOffset
		elif isinstance(other, tuple):
			return self._xOffset == other[0] and self._yOffset == other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two 2D-vectors for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-vectors are unequal.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> Self:
		"""
		Negate all components of this 2D-vector and create a new 2D-vector.

		:returns: A new 2D-vector with negated components, of this vector's class.
		"""
		return self.__class__(
			-self._xOffset,
			-self._yOffset
		)

	def __add__(self, other: Any) -> Self:
		"""
		Adds a 2D-vector to this 2D-vector and creates a new 2D-vector.

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          A new 2D-vector extended by the 2D-vector, of this vector's class.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			return self.__class__(
				self._xOffset + other._xOffset,
				self._yOffset + other._yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset + other[0],
				self._yOffset + other[1]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __sub__(self, other: Any) -> Self:
		"""
		Subtracts a 2D-vector from this 2D-vector and creates a new 2D-vector.

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          A new 2D-vector reduced by the 2D-vector, of this vector's class.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			return self.__class__(
				self._xOffset - other._xOffset,
				self._yOffset - other._yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset - other[0],
				self._yOffset - other[1]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __mul__(self, other: Any) -> Self:
		"""
		Multiplies this 2D-vector by a number and creates a new 2D-vector (``vector * number``).

		:param other:      The factor.
		:returns:          A new 2D-vector scaled by the factor, of this vector's class.
		:raises TypeError: If the second operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("Second operand is not supported by * operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: float, int")
			raise ex

		return self.__class__(
			self._xOffset * other,
			self._yOffset * other
		)

	def __rmul__(self, other: Any) -> Self:
		"""
		Multiplies a number by this 2D-vector and creates a new 2D-vector (``number * vector``).

		:param other:      The factor.
		:returns:          A new 2D-vector scaled by the factor, of this vector's class.
		:raises TypeError: If the first operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("First operand is not supported by * operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for first operand: float, int")
			raise ex

		return self.__class__(
			other * self._xOffset,
			other * self._yOffset
		)

	def __repr__(self) -> str:
		"""
		Returns the 2D vector's string representation.

		:returns: The string representation of the 2D vector.
		"""
		return f"{self.__class__.__name__}({self._xOffset}, {self._yOffset})"

	def __str__(self) -> str:
		"""
		Returns the 2D vector's string equivalent.

		:returns: The string equivalent of the 2D vector.
		"""
		return f"({self._xOffset}, {self._yOffset})"


@export
class Vector2D(BaseVector2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of an immutable 2D cartesian vector.

	A vector is a value, like a direction or a normal: its components are read-only, and it is hashable, so it can be a
	dictionary key or a set member. ``vector += other`` binds a new vector to the name.
	"""

	def __hash__(self) -> int:
		"""
		Returns the hash of the 2D-vector's components.

		A vector equal to a tuple has the tuple's hash.

		:returns: The hash value.
		"""
		return hash((self._xOffset, self._yOffset))


@export
class Offset2D(BaseVector2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a mutable 2D cartesian offset.

	An offset is a displacement, like a group's offset: its components can be assigned, and it changes in place with
	``+=``, ``-=`` and ``*=``. It isn't hashable.
	"""

	@property
	def XOffset(self) -> Coordinate:
		"""
		Property to access the x-direction offset (:attr:`_xOffset`).

		``xOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._xOffset

	@XOffset.setter
	def XOffset(self, xOffset: Coordinate) -> None:
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		self._xOffset = xOffset

	xOffset = XOffset

	@property
	def YOffset(self) -> Coordinate:
		"""
		Property to access the y-direction offset (:attr:`_yOffset`).

		``yOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._yOffset

	@YOffset.setter
	def YOffset(self, yOffset: Coordinate) -> None:
		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		self._yOffset = yOffset

	yOffset = YOffset

	def Copy(self) -> Self:
		"""
		Create a new 2D-offset as a copy of this 2D-offset.

		:returns: Copy of this 2D-offset.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 2D-offset moved by a positive 2D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 2D-offset moved by a negative 2D-offset.
		"""
		return self.__class__(self._xOffset, self._yOffset)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 2D-offset for :func:`copy.copy`.

		:returns: Copy of this 2D-offset.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D-offset for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D-offset.
		"""
		return self.Copy()

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 2D-vector to this 2D-offset (inplace).

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          This 2D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			self._xOffset += other._xOffset
			self._yOffset += other._yOffset
		elif isinstance(other, tuple):
			self.XOffset += other[0]
			self.YOffset += other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 2D-vector from this 2D-offset (inplace).

		:param other:      A 2D-vector as :class:`Vector2D`, :class:`Offset2D` or tuple.
		:returns:          This 2D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector2D):
			self._xOffset -= other._xOffset
			self._yOffset -= other._yOffset
		elif isinstance(other, tuple):
			self.XOffset -= other[0]
			self.YOffset -= other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __imul__(self, other: Any) -> Self:
		"""
		Multiplies this 2D-offset by a number (inplace).

		:param other:      The factor.
		:returns:          This 2D-offset.
		:raises TypeError: If the second operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("Second operand is not supported by *= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: float, int")
			raise ex

		self._xOffset *= other
		self._yOffset *= other

		return self


@export
class Size2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian size."""

	_width:  Coordinate  #: width in x-direction.
	_height: Coordinate  #: height in y-direction.

	def __init__(self, width: Coordinate, height: Coordinate) -> None:
		"""
		Initializes a 2-dimensional size.

		:param width:       width in x-direction.
		:param height:      height in y-direction.
		:raises ValueError: If parameter 'width' is None.
		:raises TypeError:  If parameter 'width' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'height' is None.
		:raises TypeError:  If parameter 'height' is not of type :class:`float` or :class:`int`.
		"""
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		self._width =  width
		self._height = height

	@property
	def Width(self) -> Coordinate:
		"""
		Property to access the width in x-direction (:attr:`_width`).

		``width`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The width in x-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._width

	@Width.setter
	def Width(self, width: Coordinate) -> None:
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		self._width = width

	width = Width

	@property
	def Height(self) -> Coordinate:
		"""
		Property to access the height in y-direction (:attr:`_height`).

		``height`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The height in y-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._height

	@Height.setter
	def Height(self, height: Coordinate) -> None:
		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		self._height = height

	height = Height

	def Copy(self) -> Self:
		"""
		Create a new 2D-size as a copy of this 2D-size.

		:returns: Copy of this 2D-size.
		"""
		return self.__class__(self._width, self._height)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 2D-size for :func:`copy.copy`.

		:returns: Copy of this 2D-size.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D-size for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D-size.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-size to a simple 2-element tuple.

		:returns: ``(width, height)`` tuple.
		"""
		return self._width, self._height

	def __repr__(self) -> str:
		"""
		Returns the 2D size's string representation.

		:returns: The string representation of the 2D size.
		"""
		return f"Size2D({self._width}, {self._height})"

	def __str__(self) -> str:
		"""
		Returns the 2D size's string equivalent.

		:returns: The string equivalent of the 2D size.
		"""
		return f"({self._width}, {self._height})"


@export
class BoundingBox2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	An axis-aligned 2D bounding box.

	A bounding box is a computed value: shapes and segments return a new one from their ``BoundingBox`` property on
	every access. Its borders belong to the box.
	"""

	_minX: Coordinate  #: Smallest x-coordinate.
	_minY: Coordinate  #: Smallest y-coordinate.
	_maxX: Coordinate  #: Largest x-coordinate.
	_maxY: Coordinate  #: Largest y-coordinate.

	def __init__(self, minX: Coordinate, minY: Coordinate, maxX: Coordinate, maxY: Coordinate) -> None:
		"""
		Initializes a 2-dimensional bounding box from its smallest and largest coordinates.

		:param minX:        Smallest x-coordinate.
		:param minY:        Smallest y-coordinate.
		:param maxX:        Largest x-coordinate.
		:param maxY:        Largest y-coordinate.
		:raises ValueError: If parameter 'minX' is None.
		:raises TypeError:  If parameter 'minX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'minY' is None.
		:raises TypeError:  If parameter 'minY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is None.
		:raises TypeError:  If parameter 'maxX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is less than parameter 'minX'.
		:raises ValueError: If parameter 'maxY' is None.
		:raises TypeError:  If parameter 'maxY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxY' is less than parameter 'minY'.
		"""
		for name, value in (
			("minX", minX),
			("minY", minY),
			("maxX", maxX),
			("maxY", maxY)
		):
			if value is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(value, (int, float)):
				ex = TypeError(f"Parameter '{name}' is not of type 'float' or 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		if maxX < minX:
			ex = ValueError("Parameter 'maxX' is less than parameter 'minX'.")
			ex.add_note(f"Got minX={minX} and maxX={maxX}.")
			raise ex

		if maxY < minY:
			ex = ValueError("Parameter 'maxY' is less than parameter 'minY'.")
			ex.add_note(f"Got minY={minY} and maxY={maxY}.")
			raise ex

		self._minX = minX
		self._minY = minY
		self._maxX = maxX
		self._maxY = maxY

	@classmethod
	def FromPoints(cls, points: Iterable[Point2D[Coordinate]]) -> Self:
		"""
		Create the smallest bounding box enclosing all given points.

		:param points:      Points to enclose.
		:returns:           Bounding box enclosing all points.
		:raises ValueError: If parameter 'points' is None.
		:raises TypeError:  If parameter 'points' is not iterable.
		:raises ValueError: If an element of parameter 'points' is None.
		:raises TypeError:  If an element of parameter 'points' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'points' is empty.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		iterator = iter(points)
		try:
			point = next(iterator)
		except StopIteration as ex:
			raise ValueError("Parameter 'points' is empty.") from ex

		if point is None:
			raise ValueError("An element of parameter 'points' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		minX = maxX = point._x
		minY = maxY = point._y

		for point in iterator:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			x = point._x
			y = point._y
			if x < minX:
				minX = x
			elif x > maxX:
				maxX = x

			if y < minY:
				minY = y
			elif y > maxY:
				maxY = y

		return cls(minX, minY, maxX, maxY)

	@readonly
	def MinX(self) -> Coordinate:
		"""
		Read-only property to access the smallest x-coordinate (:attr:`_minX`).

		:returns: The smallest x-coordinate.
		"""
		return self._minX

	@readonly
	def MinY(self) -> Coordinate:
		"""
		Read-only property to access the smallest y-coordinate (:attr:`_minY`).

		:returns: The smallest y-coordinate.
		"""
		return self._minY

	@readonly
	def MaxX(self) -> Coordinate:
		"""
		Read-only property to access the largest x-coordinate (:attr:`_maxX`).

		:returns: The largest x-coordinate.
		"""
		return self._maxX

	@readonly
	def MaxY(self) -> Coordinate:
		"""
		Read-only property to access the largest y-coordinate (:attr:`_maxY`).

		:returns: The largest y-coordinate.
		"""
		return self._maxY

	@readonly
	def Width(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in x-direction.

		:returns: The width in x-direction.
		"""
		return self._maxX - self._minX

	@readonly
	def Height(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in y-direction.

		:returns: The height in y-direction.
		"""
		return self._maxY - self._minY

	@readonly
	def Center(self) -> Point2D[float]:
		"""
		Read-only property to return the bounding box' center as a new 2D-point.

		:returns: The center point.
		"""
		return Point2D((self._minX + self._maxX) / 2, (self._minY + self._maxY) / 2)

	def ToRectangle(self) -> Rectangle[Coordinate]:
		"""
		Create a new rectangle from this bounding box's corners.

		:returns:            A new rectangle with the size and position of this bounding box.
		:raises NoAreaError: If the bounding box has no width or no height.
		"""
		from pyTooling.Cartesian2D.Shapes import Rectangle

		if self._minX == self._maxX or self._minY == self._maxY:
			ex = NoAreaError("Bounding box has no area.")
			ex.add_note(f"Got width '{self._maxX - self._minX}' and height '{self._maxY - self._minY}'.")
			raise ex

		return Rectangle(
			Point2D(self._minX, self._minY),
			Point2D(self._minX, self._maxY),
			Point2D(self._maxX, self._maxY),
			Point2D(self._maxX, self._minY)
		)

	def Union(self, other: BoundingBox2D[Coordinate]) -> BoundingBox2D[Coordinate]:
		"""
		Create the smallest bounding box enclosing this and another bounding box.

		:param other:       The second bounding box.
		:returns:           A new bounding box enclosing both bounding boxes.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox2D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox2D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			min(self._minX, other._minX),
			min(self._minY, other._minY),
			max(self._maxX, other._maxX),
			max(self._maxY, other._maxY)
		)

	def HasOverlap(self, other: BoundingBox2D[Coordinate]) -> bool:
		"""
		Check if this bounding box and another bounding box overlap.

		Two bounding boxes touching only at a border or a corner don't overlap, so elements can be aligned next to each
		other without a distance.

		:param other:       The second bounding box.
		:returns:           ``True``, if the inner areas of both bounding boxes overlap.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox2D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox2D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return (
			self._minX < other._maxX and other._minX < self._maxX and
			self._minY < other._maxY and other._minY < self._maxY
		)

	def ContainsPoint(self, point: Point2D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box.

		A point on a border is contained.

		:param point:       The point to check.
		:returns:           ``True``, if the point lies within the bounding box or on its border.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point2D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("Parameter 'point' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		return self._ContainsPoint(point)

	def _ContainsPoint(self, point: Point2D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box, without checking the parameter.

		:param point: The point to check.
		:returns:     ``True``, if the point lies within the bounding box or on its border.
		"""
		return self._minX <= point._x <= self._maxX and self._minY <= point._y <= self._maxY

	def __contains__(self, other: Any) -> bool:
		"""
		Check if an element lies within this bounding box (``other in box``).

		:param other:      The element to check. Supported: :class:`Point2D`.
		:returns:          ``True``, if the element lies within the bounding box or on its border.
		:raises TypeError: If the first operand is not of type :class:`Point2D`.
		"""
		if isinstance(other, Point2D):
			return self._ContainsPoint(other)

		ex = TypeError("First operand is not supported by in operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for first operand: Point2D")
		raise ex

	def __add__(self, other: Any) -> BoundingBox2D[Coordinate]:
		"""
		Adds a 2D-vector to this bounding box and creates a new, shifted bounding box.

		:param other:      A 2D-vector as :class:`Vector2D` or :class:`Offset2D`.
		:returns:          A new bounding box shifted by the 2D-vector.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector2D`.
		"""
		if not isinstance(other, BaseVector2D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			self._minX + other._xOffset,
			self._minY + other._yOffset,
			self._maxX + other._xOffset,
			self._maxY + other._yOffset
		)

	def Copy(self) -> Self:
		"""
		Create a new bounding box as a copy of this bounding box.

		:returns: Copy of this bounding box.
		"""
		return self.__class__(self._minX, self._minY, self._maxX, self._maxY)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.copy`.

		:returns: Copy of this bounding box.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this bounding box.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate]:
		"""
		Convert this bounding box to a simple 4-element tuple.

		:returns: ``(minX, minY, maxX, maxY)`` tuple.
		"""
		return self._minX, self._minY, self._maxX, self._maxY

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both bounding boxes have the same coordinates.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox2D`.
		"""
		if not isinstance(other, BoundingBox2D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox2D")
			raise ex

		return (
			self._minX == other._minX and self._minY == other._minY and
			self._maxX == other._maxX and self._maxY == other._maxY
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the bounding boxes differ in at least one coordinate.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox2D`.
		"""
		if not isinstance(other, BoundingBox2D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox2D")
			raise ex

		return (
			self._minX != other._minX or self._minY != other._minY or
			self._maxX != other._maxX or self._maxY != other._maxY
		)

	def __repr__(self) -> str:
		"""
		Returns the bounding box' string representation.

		:returns: The string representation of the bounding box.
		"""
		return f"BoundingBox2D({self._minX}, {self._minY}, {self._maxX}, {self._maxY})"

	def __str__(self) -> str:
		"""
		Returns the bounding box' string equivalent.

		:returns: The string equivalent of the bounding box, its corners with the smallest and the largest coordinates.
		"""
		return f"(({self._minX}, {self._minY}), ({self._maxX}, {self._maxY}))"


@export
class Line2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	A 2D line, which is infinite in both directions, unlike a :class:`LineSegment2D`.

	The line is stored in Hesse normal form: a normal ``(nx, ny)`` of length 1 and the signed distance ``d`` of the line
	from the origin, so the line is all points ``(x, y)`` with ``nx * x + ny * y = d``. The first non-zero component of
	the normal is positive, so a line has one form only.

	A line is in absolute coordinates, relative to the origin, so elements of different groups can be mirrored at the
	same line with :meth:`Element2D.MirrorAt`. A line is a value: it compares by value and is hashable. Two lines are
	equal, if they have the same normal and distance, whatever class or constructor created them.
	"""

	_normal:   Offset2D[float]  #: The normal of length 1, its first non-zero component is positive.
	_distance: float            #: The signed distance of the line from the origin, in direction of the normal.

	def __init__(self, normal: Offset2D[Coordinate], distance: Coordinate) -> None:
		"""
		Initializes a 2D line from a normal and a distance, the line ``nx * x + ny * y = distance``.

		A normal of another length than 1 is normalized, and the distance is divided by the normal's length, so the line
		stays the same. If the first non-zero component of the normal is negative, the normal and the distance are
		negated. A normal of length 1 keeps its values, so the line with normal ``(1, 0)`` keeps an integer distance. Zeros
		are stored without sign.

		:param normal:      A normal of the line, perpendicular to it.
		:param distance:    The right-hand side of the line's equation; for a normal of length 1, the signed distance of the
		                    line from the origin.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`Offset2D`.
		:raises ValueError: If parameter 'normal' is a zero offset. |br|
		                    A line needs a normal direction.
		:raises ValueError: If parameter 'distance' is None.
		:raises TypeError:  If parameter 'distance' is not of type :class:`float` or :class:`int`.
		"""
		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, Offset2D):
			ex = TypeError("Parameter 'normal' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero offset.")
			ex.add_note(f"Got offset {normal}.")
			ex.add_note("A line needs a normal direction.")
			raise ex

		if distance is None:
			raise ValueError("Parameter 'distance' is None.")
		elif not isinstance(distance, (int, float)):
			ex = TypeError("Parameter 'distance' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(distance)}'.")
			raise ex

		normalX = normal._xOffset
		normalY = normal._yOffset
		if (squaredLength := normalX ** 2 + normalY ** 2) != 1:
			length =   sqrt(squaredLength)
			normalX =  normalX / length
			normalY =  normalY / length
			distance = distance / length

		if normalX < 0 or (normalX == 0 and normalY < 0):
			normalX =  -normalX
			normalY =  -normalY
			distance = -distance

		self._normal =   Offset2D(normalX + 0, normalY + 0)
		self._distance = distance + 0

	@classmethod
	def FromPoints(cls, first: Point2D[Coordinate], second: Point2D[Coordinate]) -> Line2D[float]:
		"""
		Create the line through two points.

		The points are taken in absolute coordinates: a point inside a group is converted.

		:param first:       A first point of the line.
		:param second:      A second point of the line.
		:returns:           A new line, a :class:`Line2D` also if called on a derived class.
		:raises ValueError: If parameter 'first' is None.
		:raises TypeError:  If parameter 'first' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'second' is None.
		:raises TypeError:  If parameter 'second' is not of type :class:`Point2D`.
		:raises ValueError: If parameters 'first' and 'second' are at the same position. |br|
		                    Two points at the same position don't define a line.
		"""
		for name, point in (
			("first",  first),
			("second", second)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point2D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		start =     first.Absolute
		direction = second.Absolute - start
		if direction._xOffset == 0 and direction._yOffset == 0:
			ex = ValueError("Parameters 'first' and 'second' are at the same position.")
			ex.add_note(f"Got points {first} and {second}, both at {start} in absolute coordinates.")
			ex.add_note("Two points at the same position don't define a line.")
			raise ex

		return Line2D(
			Offset2D(-direction._yOffset, direction._xOffset),
			direction._xOffset * start._y - direction._yOffset * start._x
		)

	@classmethod
	def FromPointAndDirection(cls, point: Point2D[Coordinate], direction: Offset2D[Coordinate]) -> Line2D[float]:
		"""
		Create the line through a point in a direction.

		The point is taken in absolute coordinates: a point inside a group is converted.

		:param point:       A point of the line.
		:param direction:   The direction of the line.
		:returns:           A new line, a :class:`Line2D` also if called on a derived class.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'direction' is None.
		:raises TypeError:  If parameter 'direction' is not of type :class:`Offset2D`.
		:raises ValueError: If parameter 'direction' is a zero offset. |br|
		                    A line needs a direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("Parameter 'point' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if direction is None:
			raise ValueError("Parameter 'direction' is None.")
		elif not isinstance(direction, Offset2D):
			ex = TypeError("Parameter 'direction' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
			raise ex
		elif direction._xOffset == 0 and direction._yOffset == 0:
			ex = ValueError("Parameter 'direction' is a zero offset.")
			ex.add_note(f"Got offset {direction}.")
			ex.add_note("A line needs a direction.")
			raise ex

		absolute = point.Absolute
		return Line2D(
			Offset2D(-direction._yOffset, direction._xOffset),
			direction._xOffset * absolute._y - direction._yOffset * absolute._x
		)

	@classmethod
	def FromPointAndNormal(cls, point: Point2D[Coordinate], normal: Offset2D[Coordinate]) -> Line2D[float]:
		"""
		Create the line through a point, perpendicular to a normal.

		The point is taken in absolute coordinates: a point inside a group is converted.

		:param point:       A point of the line.
		:param normal:      A normal of the line, perpendicular to it.
		:returns:           A new line, a :class:`Line2D` also if called on a derived class.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`Offset2D`.
		:raises ValueError: If parameter 'normal' is a zero offset. |br|
		                    A line needs a normal direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("Parameter 'point' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, Offset2D):
			ex = TypeError("Parameter 'normal' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero offset.")
			ex.add_note(f"Got offset {normal}.")
			ex.add_note("A line needs a normal direction.")
			raise ex

		absolute = point.Absolute
		return Line2D(normal, normal._xOffset * absolute._x + normal._yOffset * absolute._y)

	@readonly
	def Normal(self) -> Offset2D[float]:
		"""
		Read-only property to access the normal of the line (:attr:`_normal`).

		:returns: The normal of length 1, its first non-zero component is positive.
		"""
		return self._normal

	@readonly
	def Distance(self) -> float:
		"""
		Read-only property to access the signed distance of the line from the origin (:attr:`_distance`).

		:returns: The signed distance, positive in direction of the normal.
		"""
		return self._distance

	def SignedDistance(self, point: Point2D[Coordinate]) -> float:
		"""
		Compute the signed distance of a point from the line.

		The point is taken in absolute coordinates. The distance is positive on the side the normal points to, negative on
		the other side, and zero for a point on the line.

		:param point:       The point.
		:returns:           The signed distance ``nx * x + ny * y - d``.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point2D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("Parameter 'point' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		absolute = point.Absolute
		normal =   self._normal
		return normal._xOffset * absolute._x + normal._yOffset * absolute._y - self._distance

	def Project(self, point: Point2D[Coordinate]) -> Point2D[float]:
		"""
		Project a point onto the line, the foot of the perpendicular from the point to the line.

		The point is taken in absolute coordinates, and the projection is in absolute coordinates too.

		:param point:       The point to project.
		:returns:           A new 2D-point without owner.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point2D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point2D):
			ex = TypeError("Parameter 'point' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		absolute =       point.Absolute
		normal =         self._normal
		signedDistance = normal._xOffset * absolute._x + normal._yOffset * absolute._y - self._distance
		return Point2D(
			absolute._x - signedDistance * normal._xOffset,
			absolute._y - signedDistance * normal._yOffset
		)

	def Intersects(self, ray: Ray2D[Coordinate]) -> bool:
		"""
		Check if a ray hits the line.

		A ray starting on the line hits it, also a ray running along the line. A ray parallel to the line, or pointing away
		from it, doesn't.

		:param ray:         The ray.
		:returns:           ``True``, if the ray has a point on the line.
		:raises ValueError: If parameter 'ray' is None.
		:raises TypeError:  If parameter 'ray' is not of type :class:`Ray2D`.
		"""
		if ray is None:
			raise ValueError("Parameter 'ray' is None.")
		elif not isinstance(ray, Ray2D):
			ex = TypeError("Parameter 'ray' is not of type 'Ray2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(ray)}'.")
			raise ex

		normal =        self._normal
		start =         ray._start
		direction =     ray._direction
		startDistance = normal._xOffset * start._x + normal._yOffset * start._y - self._distance
		approach =      normal.ScalarProduct(direction)
		return startDistance == 0 or startDistance * approach < 0

	def Intersection(self, ray: Ray2D[Coordinate]) -> Point2D[float]:
		"""
		Compute the point, where a ray hits the line.

		A ray starting on the line, also one running along the line, hits it at its start point.

		:param ray:         The ray.
		:returns:           A new 2D-point without owner, in absolute coordinates.
		:raises ValueError: If parameter 'ray' is None.
		:raises TypeError:  If parameter 'ray' is not of type :class:`Ray2D`.
		:raises ValueError: If parameter 'ray' is parallel to the line, but doesn't start on it. |br|
		                    Check with :meth:`Intersects` first.
		:raises ValueError: If parameter 'ray' points away from the line. |br|
		                    Check with :meth:`Intersects` first.
		"""
		if ray is None:
			raise ValueError("Parameter 'ray' is None.")
		elif not isinstance(ray, Ray2D):
			ex = TypeError("Parameter 'ray' is not of type 'Ray2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(ray)}'.")
			raise ex

		normal =        self._normal
		start =         ray._start
		direction =     ray._direction
		startDistance = normal._xOffset * start._x + normal._yOffset * start._y - self._distance
		approach =      normal.ScalarProduct(direction)
		if startDistance == 0:
			return Point2D(start._x, start._y)
		elif approach == 0:
			ex = ValueError("Parameter 'ray' is parallel to the line.")
			ex.add_note(f"Got ray {ray!r} and line {self!r}.")
			ex.add_note("Check with 'Intersects' first.")
			raise ex
		elif startDistance * approach > 0:
			ex = ValueError("Parameter 'ray' points away from the line.")
			ex.add_note(f"Got ray {ray!r} and line {self!r}.")
			ex.add_note("Check with 'Intersects' first.")
			raise ex

		factor = -startDistance / approach
		return Point2D(
			start._x + factor * direction._xOffset,
			start._y + factor * direction._yOffset
		)

	def _MirrorElement(self, element: Element2D[Coordinate]) -> None:
		"""
		Mirror an element at this line (inplace).

		A line with normal ``(1, 0)`` or ``(0, 1)`` mirrors an element like a :class:`VerticalLine2D` or a
		:class:`HorizontalLine2D`, so integer coordinates stay integers.

		:param element: The element to mirror.
		"""
		normal = self._normal
		frame =  element.Frame
		if normal._yOffset == 0:
			x = self._distance if frame is None else self._distance - frame.AbsoluteOffset._xOffset
			element._MirrorX(2 * x)
		elif normal._xOffset == 0:
			y = self._distance if frame is None else self._distance - frame.AbsoluteOffset._yOffset
			element._MirrorY(2 * y)
		else:
			distance = self._distance if frame is None else self._distance - normal.ScalarProduct(frame.AbsoluteOffset)
			element._MirrorAt(normal, distance)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two lines for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both lines have the same normal and distance.
		:raises TypeError: If the second operand is not of type :class:`Line2D`.
		"""
		if not isinstance(other, Line2D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Line2D")
			raise ex

		normal =      self._normal
		otherNormal = other._normal
		return (
			normal._xOffset == otherNormal._xOffset
			and normal._yOffset == otherNormal._yOffset
			and self._distance == other._distance
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two lines for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the lines differ in normal or distance.
		:raises TypeError: If the second operand is not of type :class:`Line2D`.
		"""
		if not isinstance(other, Line2D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Line2D")
			raise ex

		normal =      self._normal
		otherNormal = other._normal
		return (
			normal._xOffset != otherNormal._xOffset
			or normal._yOffset != otherNormal._yOffset
			or self._distance != other._distance
		)

	def __hash__(self) -> int:
		"""
		Returns a hash of the line's normal and distance, so equal lines have the same hash.

		:returns: The hash value.
		"""
		return hash((self._normal._xOffset, self._normal._yOffset, self._distance))

	def __repr__(self) -> str:
		"""
		Returns the line's string representation.

		:returns: The string representation of the line, its normal and distance.
		"""
		return f"Line2D({self._normal}, {self._distance})"

	def __str__(self) -> str:
		"""
		Returns the line's string equivalent as an equation.

		The line with normal ``(0.6, 0.8)`` and distance ``2.0`` returns ``0.6 * x + 0.8 * y = 2.0``.

		:returns: The equation of the line.
		"""
		normal = self._normal
		if normal._yOffset < 0:
			return f"{normal._xOffset} * x - {-normal._yOffset} * y = {self._distance}"

		return f"{normal._xOffset} * x + {normal._yOffset} * y = {self._distance}"


@export
class VerticalLine2D(Line2D[Coordinate], Generic[Coordinate]):
	"""
	A vertical 2D line: all its points have the same x-coordinate, the line ``x = c``.

	Its normal is ``(1, 0)``, and its distance is the x-coordinate.
	"""

	def __init__(self, x: Coordinate) -> None:
		"""
		Initializes a vertical 2D line from the x-coordinate all its points have.

		:param x:           The x-coordinate of all points of the line.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(Offset2D(1, 0), 0)

		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		self._distance = x + 0

	@classmethod
	def FromElement(cls, element: Element2D[Coordinate], alignment: Alignment2D) -> Self:
		"""
		Create the vertical line through an edge or the center of an element's absolute bounding box.

		The x-coordinate of a center is a :class:`float`, as in :attr:`BoundingBox2D.Center`.

		:param element:     The element, whose :attr:`~Element2D.AbsoluteBoundingBox` the line runs through.
		:param alignment:   The edge or center of the bounding box: ``MinX``, ``CenterX`` or ``MaxX``.
		:returns:           A new vertical line.
		:raises ValueError: If parameter 'element' is None.
		:raises TypeError:  If parameter 'element' is not of type :class:`Element2D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment2D`.
		:raises ValueError: If parameter 'alignment' is not ``Alignment2D.MinX``, ``Alignment2D.CenterX`` or
		                    ``Alignment2D.MaxX``. |br|
		                    Use :meth:`HorizontalLine2D.FromElement` for the other alignments.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element2D):
			ex = TypeError("Parameter 'element' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment2D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex
		elif alignment not in (Alignment2D.MinX, Alignment2D.CenterX, Alignment2D.MaxX):
			ex = ValueError("Parameter 'alignment' is not Alignment2D.MinX, Alignment2D.CenterX or Alignment2D.MaxX.")
			ex.add_note(f"Got value '{alignment}'.")
			ex.add_note("Use 'HorizontalLine2D.FromElement' for the other alignments.")
			raise ex

		box = element.AbsoluteBoundingBox
		if alignment is Alignment2D.MinX:
			return cls(box._minX)
		elif alignment is Alignment2D.CenterX:
			return cls((box._minX + box._maxX) / 2)
		else:
			return cls(box._maxX)

	@readonly
	def X(self) -> Coordinate:
		"""
		Read-only property to access the x-coordinate of all points of the line (:attr:`_distance`).

		:returns: The x-coordinate of the line.
		"""
		return self._distance

	def __repr__(self) -> str:
		"""
		Returns the vertical line's string representation.

		:returns: The string representation of the line.
		"""
		return f"VerticalLine2D({self._distance})"

	def __str__(self) -> str:
		"""
		Returns the vertical line's string equivalent as an equation.

		The line at 5 returns ``x = 5``.

		:returns: The equation of the line.
		"""
		return f"x = {self._distance}"


@export
class HorizontalLine2D(Line2D[Coordinate], Generic[Coordinate]):
	"""
	A horizontal 2D line: all its points have the same y-coordinate, the line ``y = c``.

	Its normal is ``(0, 1)``, and its distance is the y-coordinate.
	"""

	def __init__(self, y: Coordinate) -> None:
		"""
		Initializes a horizontal 2D line from the y-coordinate all its points have.

		:param y:           The y-coordinate of all points of the line.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(Offset2D(0, 1), 0)

		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._distance = y + 0

	@classmethod
	def FromElement(cls, element: Element2D[Coordinate], alignment: Alignment2D) -> Self:
		"""
		Create the horizontal line through an edge or the center of an element's absolute bounding box.

		The y-coordinate of a center is a :class:`float`, as in :attr:`BoundingBox2D.Center`.

		:param element:     The element, whose :attr:`~Element2D.AbsoluteBoundingBox` the line runs through.
		:param alignment:   The edge or center of the bounding box: ``MinY``, ``CenterY`` or ``MaxY``.
		:returns:           A new horizontal line.
		:raises ValueError: If parameter 'element' is None.
		:raises TypeError:  If parameter 'element' is not of type :class:`Element2D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment2D`.
		:raises ValueError: If parameter 'alignment' is not ``Alignment2D.MinY``, ``Alignment2D.CenterY`` or
		                    ``Alignment2D.MaxY``. |br|
		                    Use :meth:`VerticalLine2D.FromElement` for the other alignments.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element2D):
			ex = TypeError("Parameter 'element' is not of type 'Element2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment2D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex
		elif alignment not in (Alignment2D.MinY, Alignment2D.CenterY, Alignment2D.MaxY):
			ex = ValueError("Parameter 'alignment' is not Alignment2D.MinY, Alignment2D.CenterY or Alignment2D.MaxY.")
			ex.add_note(f"Got value '{alignment}'.")
			ex.add_note("Use 'VerticalLine2D.FromElement' for the other alignments.")
			raise ex

		box = element.AbsoluteBoundingBox
		if alignment is Alignment2D.MinY:
			return cls(box._minY)
		elif alignment is Alignment2D.CenterY:
			return cls((box._minY + box._maxY) / 2)
		else:
			return cls(box._maxY)

	@readonly
	def Y(self) -> Coordinate:
		"""
		Read-only property to access the y-coordinate of all points of the line (:attr:`_distance`).

		:returns: The y-coordinate of the line.
		"""
		return self._distance

	def __repr__(self) -> str:
		"""
		Returns the horizontal line's string representation.

		:returns: The string representation of the line.
		"""
		return f"HorizontalLine2D({self._distance})"

	def __str__(self) -> str:
		"""
		Returns the horizontal line's string equivalent as an equation.

		The line at 5 returns ``y = 5``.

		:returns: The equation of the line.
		"""
		return f"y = {self._distance}"


@export
class Ray2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	A 2D ray: a half-line, which starts at a point and is infinite in one direction.

	The ray is in absolute coordinates, relative to the origin. Its start point is a free copy, so it owns no point of an
	element. Two rays are equal, if they start at the same point and their directions point the same way, whatever their
	lengths. A ray is unhashable, as its start point and direction can be changed.
	"""

	_start:     Point2D[Coordinate]   #: The start point of the ray, in absolute coordinates and without owner.
	_direction: Offset2D[Coordinate]  #: The direction of the ray.

	def __init__(self, start: Point2D[Coordinate], direction: Offset2D[Coordinate]) -> None:
		"""
		Initializes a 2D ray from its start point and its direction.

		The start point is taken in absolute coordinates (a point inside a group is converted), and the direction is
		copied.

		:param start:       The start point of the ray.
		:param direction:   The direction of the ray.
		:raises ValueError: If parameter 'start' is None.
		:raises TypeError:  If parameter 'start' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'direction' is None.
		:raises TypeError:  If parameter 'direction' is not of type :class:`Offset2D`.
		:raises ValueError: If parameter 'direction' is a zero offset. |br|
		                    A ray needs a direction.
		"""
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point2D):
			ex = TypeError("Parameter 'start' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex

		if direction is None:
			raise ValueError("Parameter 'direction' is None.")
		elif not isinstance(direction, Offset2D):
			ex = TypeError("Parameter 'direction' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
			raise ex
		elif direction._xOffset == 0 and direction._yOffset == 0:
			ex = ValueError("Parameter 'direction' is a zero offset.")
			ex.add_note(f"Got offset {direction}.")
			ex.add_note("A ray needs a direction.")
			raise ex

		self._start =     start.Absolute
		self._direction = direction.Copy()

	@readonly
	def Start(self) -> Point2D[Coordinate]:
		"""
		Read-only property to access the start point of the ray (:attr:`_start`).

		:returns: The start point, in absolute coordinates and without owner.
		"""
		return self._start

	@readonly
	def Direction(self) -> Offset2D[Coordinate]:
		"""
		Read-only property to access the direction of the ray (:attr:`_direction`).

		:returns: The direction.
		"""
		return self._direction

	def PointAt(self, distance: Coordinate) -> Point2D[float]:
		"""
		Compute the point of the ray at a distance from its start point.

		:param distance:    The distance from the start point along the direction.
		:returns:           A new 2D-point without owner.
		:raises ValueError: If parameter 'distance' is None.
		:raises TypeError:  If parameter 'distance' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'distance' is negative. |br|
		                    A point before the start point isn't on the ray.
		"""
		if distance is None:
			raise ValueError("Parameter 'distance' is None.")
		elif not isinstance(distance, (int, float)):
			ex = TypeError("Parameter 'distance' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(distance)}'.")
			raise ex
		elif distance < 0:
			ex = ValueError("Parameter 'distance' is negative.")
			ex.add_note(f"Got value '{distance}'.")
			ex.add_note("A point before the start point isn't on the ray.")
			raise ex

		start =     self._start
		direction = self._direction
		factor =    distance / sqrt(direction._xOffset ** 2 + direction._yOffset ** 2)
		return Point2D(
			start._x + direction._xOffset * factor,
			start._y + direction._yOffset * factor
		)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two rays for equality.

		The directions point the same way, if their cross product is zero and their dot product is positive. The lengths of
		the directions don't matter: a ray with direction ``(3, 4)`` equals the ray with direction ``(6, 8)`` from the same
		start point.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both rays have the same start point and their directions point the same way.
		:raises TypeError: If the second operand is not of type :class:`Ray2D`.
		"""
		if not isinstance(other, Ray2D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Ray2D")
			raise ex

		start =          self._start
		otherStart =     other._start
		direction =      self._direction
		otherDirection = other._direction
		return (
			start._x == otherStart._x
			and start._y == otherStart._y
			and direction._xOffset * otherDirection._yOffset - direction._yOffset * otherDirection._xOffset == 0
			and direction._xOffset * otherDirection._xOffset + direction._yOffset * otherDirection._yOffset > 0
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two rays for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the rays differ in start point or their directions point different ways.
		:raises TypeError: If the second operand is not of type :class:`Ray2D`.
		"""
		if not isinstance(other, Ray2D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Ray2D")
			raise ex

		start =          self._start
		otherStart =     other._start
		direction =      self._direction
		otherDirection = other._direction
		return (
			start._x != otherStart._x
			or start._y != otherStart._y
			or direction._xOffset * otherDirection._yOffset - direction._yOffset * otherDirection._xOffset != 0
			or direction._xOffset * otherDirection._xOffset + direction._yOffset * otherDirection._yOffset <= 0
		)

	def __repr__(self) -> str:
		"""
		Returns the ray's string representation.

		:returns: The string representation of the ray, its start point and direction.
		"""
		return f"Ray2D({self._start}, {self._direction})"

	def __str__(self) -> str:
		"""
		Returns the ray's string equivalent as a parametric equation.

		The ray from ``(1, 2)`` in direction ``(3, 4)`` returns ``(1, 2) + t * (3, 4), t >= 0``.

		:returns: The equation of the ray.
		"""
		return f"{self._start} + t * {self._direction}, t >= 0"


@export
@abstractclass
class Segment2D(Element2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 2D cartesian segment.

	A standalone segment owns its start and end point; a group or canvas can hold it. A segment with a parent shape is an
	edge of that shape: it references two of the shape's points, which stay owned by the shape.
	"""

	_start: Point2D[Coordinate]  #: Start point of a segment.
	_end:   Point2D[Coordinate]  #: End point of a segment.

	def __init__(
		self,
		start:         Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Shape, Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a 2-dimensional segment.

		:param start:                Start point of the segment.
		:param end:                  End point of the segment.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param value:                Optional, value of the segment. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the shape this segment is an edge of, or the group or canvas the segment is
		                             added to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'start' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'end' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Shapes.Shape`,
		                             :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:          If parameter 'parent' is a shape, while 'copyPoints' is ``True``. |br|
		                             An edge references the points of its parent shape: use ``copyPoints=False``.
		"""
		from pyTooling.Cartesian2D.Groups import Container2DMixin

		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point2D):
			ex = TypeError("Parameter 'start' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex

		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point2D):
			ex = TypeError("Parameter 'end' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		if parent is None or isinstance(parent, Container2DMixin):
			if copyPoints:
				start = start.Copy()
				end =   end.Copy()
			elif end is start:
				ex = DuplicatePointError("Point is given twice.")
				ex.add_note(f"Got point {start}.")
				ex.add_note("Use 'copyPoints=True' to copy the points.")
				raise ex from ValueError("Parameter 'end' is the same point as parameter 'start'.")
			else:
				for name, point in (
					("start", start),
					("end",   end)
				):
					if point._parent is not None:
						ex = AlreadyOwnedError("Point is owned by another element already.")
						ex.add_note(f"Got point {point} owned by {point._parent!r}.")
						ex.add_note("Use 'copyPoints=True' to copy the point.")
						raise ex from ValueError(f"Parameter '{name}' is owned by another element.")

			start._parent = self
			end._parent =   self
		elif copyPoints:
			ex = ValueError("Parameter 'parent' is a shape, while 'copyPoints' is True.")
			ex.add_note("An edge references the points of its parent shape: use 'copyPoints=False'.")
			raise ex
		else:
			for name, point in (
				("start", start),
				("end",   end)
			):
				if point._parent is not parent:
					ex = NotOwnedError("Point isn't owned by the parent shape.")
					ex.add_note(f"Got point {point} owned by {point._parent!r}.")
					raise ex from ValueError(f"Parameter '{name}' isn't owned by parameter 'parent'.")

			self._parent = parent

		self._start = start
		self._end =   end

		if self._parent is None:
			self.Parent = parent

	@property
	def Start(self) -> Point2D[Coordinate]:
		"""
		Property to access the segment's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous start
		point. An edge of a shape doesn't own its points, so it can't replace them.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    Start point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises NotOwnedError:       If the segment is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the segment's end point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._start

	@Start.setter
	def Start(self, start: Point2D[Coordinate]) -> None:
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point2D):
			ex = TypeError("Parameter 'start' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif start is self._start:
			return
		elif self._start._parent is not self:
			ex = NotOwnedError("Segment doesn't own its start point.")
			ex.add_note(f"The segment is an edge of {self._parent!r}, which owns the point.")
			raise ex
		elif start is self._end:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			raise ex from ValueError("Parameter 'start' is the segment's end point.")
		elif start._parent is not None and start._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {start} owned by {start._parent!r}.")
			raise ex from ValueError("Parameter 'start' is owned by another element.")

		self._start._parent = None
		start._parent =       self
		self._start =         start

	start = Start

	@property
	def End(self) -> Point2D[Coordinate]:
		"""
		Property to access the segment's end point (:attr:`_end`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous end
		point. An edge of a shape doesn't own its points, so it can't replace them.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    End point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises NotOwnedError:       If the segment is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the segment's start point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._end

	@End.setter
	def End(self, end: Point2D[Coordinate]) -> None:
		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point2D):
			ex = TypeError("Parameter 'end' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex
		elif end is self._end:
			return
		elif self._end._parent is not self:
			ex = NotOwnedError("Segment doesn't own its end point.")
			ex.add_note(f"The segment is an edge of {self._parent!r}, which owns the point.")
			raise ex
		elif end is self._start:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {end}.")
			raise ex from ValueError("Parameter 'end' is the segment's start point.")
		elif end._parent is not None and end._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {end} owned by {end._parent!r}.")
			raise ex from ValueError("Parameter 'end' is owned by another element.")

		self._end._parent = None
		end._parent =       self
		self._end =         end

	end = End

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the segment's start and end point.

		:returns: A new bounding box.
		"""
		start = self._start
		end =   self._end
		return BoundingBox2D(min(start._x, end._x), min(start._y, end._y), max(start._x, end._x), max(start._y, end._y))

	def Move(self, offset: BaseVector2D[Coordinate]) -> None:
		"""
		Move the segment by moving its start and end point and its other points (inplace).

		An edge of a shape moves the shape's corners it references.

		:param offset:      The 2D-vector or 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`BaseVector2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, BaseVector2D):
			ex = TypeError("Parameter 'offset' is not of type 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._start += offset
		self._end +=   offset
		self._MoveInner(offset)

	def _MoveInner(self, offset: BaseVector2D[Coordinate]) -> None:
		"""
		Move the segment's points other than its start and end point (inplace).

		A segment has no other points. A curved segment moves the points defining its curve.

		:param offset: The 2D-vector or 2D-offset to move by.
		"""

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment at a horizontal axis by mirroring its start and end point and its other points (inplace).

		An edge of a shape mirrors the shape's corners it references.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._start._y = twiceAxis - self._start._y
		self._end._y =   twiceAxis - self._end._y
		self._MirrorInnerY(twiceAxis)

	def _MirrorInnerY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment's points other than its start and end point at a horizontal axis (inplace).

		A segment has no other points. A curved segment mirrors the points defining its curve.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment at a vertical axis by mirroring its start and end point and its other points (inplace).

		An edge of a shape mirrors the shape's corners it references.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._start._x = twiceAxis - self._start._x
		self._end._x =   twiceAxis - self._end._x
		self._MirrorInnerX(twiceAxis)

	def _MirrorInnerX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment's points other than its start and end point at a vertical axis (inplace).

		A segment has no other points. A curved segment mirrors the points defining its curve.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the segment at a line by mirroring its start and end point and its other points (inplace).

		An edge of a shape mirrors the shape's corners it references.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		self._start._MirrorAt(normal, distance)
		self._end._MirrorAt(normal, distance)
		self._MirrorInnerAt(normal, distance)

	def _MirrorInnerAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the segment's points other than its start and end point at a line (inplace).

		A segment has no other points. A curved segment mirrors the points defining its curve.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""

	def Copy(self) -> Self:
		"""
		Create a new 2D-segment as a copy of this 2D-segment.

		The copy holds copies of the start and end point. It references the same :attr:`Value` and holds a shallow copy of
		the key-value-pairs.

		:returns: Copy of this 2D-segment.
		"""
		return self.__class__(self._start, self._end, value=self._value, keyValuePairs=self._dict)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 2D-segment for :func:`copy.copy`.

		:returns: Copy of this 2D-segment.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D-segment for :func:`copy.deepcopy`.

		The copy holds copies of the start and end point, and deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D-segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def _CopyAsEdge(self, start: Point2D[Coordinate], end: Point2D[Coordinate], shape: Shape) -> Self:
		"""
		Create a copy of this segment as an edge of a shape, between two of the shape's points.

		The copy's other points are copies owned by the shape. It references the same :attr:`Value` and holds a shallow
		copy of the key-value-pairs.

		:param start: The shape's point the edge starts at.
		:param end:   The shape's point the edge ends at.
		:param shape: The shape the edge belongs to.
		:returns:     A new edge of the shape.
		"""
		return self.__class__(start, end, copyPoints=False, value=self._value, keyValuePairs=self._dict, parent=shape)


@export
class LineSegment2D(Segment2D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 2D cartesian line segment."""

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean distance between start and end point.

		:returns: Euclidean distance between start and end point
		"""
		start = self._start
		end =   self._end
		return sqrt((end._x - start._x) ** 2 + (end._y - start._y) ** 2)

	def AngleTo(self, other: LineSegment2D[Coordinate]) -> float:
		"""
		Compute the angle between this line segment and another one.

		The angle is the one between both segments' directions, from ``0`` (same direction) to :data:`math.pi` (opposite
		directions).

		:param other:                The second line segment.
		:returns:                    The angle in radians.
		:raises ValueError:          If parameter 'other' is None.
		:raises TypeError:           If parameter 'other' is not of type :class:`LineSegment2D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this line segment.
		:raises ValueError:          If parameter 'other' has length 0.
		:raises ValueError:          If this line segment has length 0.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, LineSegment2D):
			ex = TypeError("Parameter 'other' is not of type 'LineSegment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex
		elif self.Frame is not other.Frame:
			ex = NotInSameFrameError("Line segments are in different frames.")
			ex.add_note(f"Got line segments {self} and {other}.")
			raise ex from ValueError("Parameter 'other' is in another frame.")
		elif other._start._x == other._end._x and other._start._y == other._end._y:
			ex = ValueError("Parameter 'other' has length 0.")
			ex.add_note(f"Got line segment {other}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		if self._start._x == self._end._x and self._start._y == self._end._y:
			ex = ValueError("Line segment has length 0.")
			ex.add_note(f"Got line segment {self}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		vectorA =         self.ToOffset()
		vectorB =         other.ToOffset()
		scalarProductAB = vectorA._xOffset * vectorB._xOffset + vectorA._yOffset * vectorB._yOffset
		crossProductAB =  vectorA._xOffset * vectorB._yOffset - vectorA._yOffset * vectorB._xOffset

		return atan2(abs(crossProductAB), scalarProductAB)

	def ToOffset(self) -> Offset2D[Coordinate]:
		"""
		Convert this 2D line segment to a 2D-offset.

		:returns: 2D-offset as :class:`Offset2D`
		"""
		return self._end - self._start

	def ToTuple(self) -> tuple[tuple[Coordinate, Coordinate], tuple[Coordinate, Coordinate]]:
		"""
		Convert this 2D line segment to a simple 2-element tuple of 2D-point tuples.

		:returns: ``((x1, y1), (x2, y2))`` tuple.
		"""
		return self._start.ToTuple(), self._end.ToTuple()

	def __repr__(self) -> str:
		"""
		Returns the 2D line segment's string representation.

		:returns: The string representation of the 2D line segment.
		"""
		return f"LineSegment2D({self._start}, {self._end})"

	def __str__(self) -> str:
		"""
		Returns the 2D line segment's string equivalent.

		:returns: The string equivalent of the 2D line segment.
		"""
		return f"({self._start} → {self._end})"


@export
class ArcSegment2D(Segment2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 2D cartesian circular arc segment.

	The arc is stored relative to its chord, the line segment from its start point to its end point: a root point at a
	fraction of the chord (:attr:`ChordPosition`), and the arc's signed distance from the chord at the root point
	(:attr:`Height`), stored as a fraction of the chord's length. So moving an end point keeps the arc's shape, scaled
	to the new chord. The :attr:`Center`, :attr:`Radius` and :attr:`Direction` are computed on each access.

	An end point moved in place, like ``point += offset``, isn't checked: moved onto the other end point, the arc has no
	chord and no :attr:`Center`.
	"""

	_chordPosition: float  #: Position of the root point on the chord, as a fraction from the start point.
	_height:        float  #: Signed distance of the arc from the chord at the root point, relative to the chord length.

	def __init__(
		self,
		start:         Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		center:        Nullable[Point2D[Coordinate]] = None,
		direction:     Nullable[SweepDirection] = None,
		arcPoint:      Nullable[Point2D[Coordinate]] = None,
		chordPosition: Nullable[float] = None,
		height:        Nullable[Coordinate] = None,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Shape, Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a 2-dimensional arc segment from its start and end point and one group of parameters for its circle.

		Exactly one group of parameters describes the arc's circle:

		* ``center`` and ``direction``: the center of the circle and the direction from the start point to the end point.
		  The end point must have the start point's distance to the center, compared with :func:`math.isclose`.
		* ``arcPoint``: a third point of the arc. The arc runs from the start point through this point to the end point.
		* ``height`` and optionally ``chordPosition``: the arc passes a point at the distance ``height`` from the chord,
		  the line segment from the start point to the end point. The distance is measured perpendicular to the chord, at
		  the root point at the fraction ``chordPosition`` of the chord from the start point. A positive height is on the
		  left of the chord, seen from the start point, a negative height on the right. At the chord's midpoint, the height
		  is the arc's sagitta.

		The arc keeps only its start and end point. It stores the height relative to the chord's length; a ``center`` or
		an ``arcPoint`` is converted to the sagitta, the height at the chord's midpoint. Only their coordinates are used.

		:param start:                Start point of the arc.
		:param end:                  End point of the arc.
		:param center:               Optional, center point of the arc's circle. Default: ``None``.
		:param direction:            Optional, direction, in which the arc sweeps from its start point to its end point.
		                             Default: ``None``.
		:param arcPoint:             Optional, a point of the arc between the start and the end point. Default: ``None``.
		:param chordPosition:        Optional, the root point's position on the chord, as a fraction from 0 (start point)
		                             to 1 (end point). Default: ``None``, which uses ``0.5``, the chord's midpoint.
		:param height:               Optional, the arc's signed distance from the chord at the root point. Default:
		                             ``None``.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param value:                Optional, value of the arc. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the shape this arc is an edge of, or the group or canvas the arc is added
		                             to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'start' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'end' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'end' is at the position of parameter 'start'. |br|
		                             An arc needs a chord from the start point to the end point.
		:raises ValueError:          If parameter 'center' is None, while 'direction' is given.
		:raises TypeError:           If parameter 'center' is not of type :class:`Point2D`.
		:raises ValueError:          If parameter 'center' is at the position of parameter 'start'.
		:raises ValueError:          If parameter 'center' has another distance to parameter 'end' than to parameter
		                             'start'.
		:raises ValueError:          If parameter 'direction' is None, while 'center' is given.
		:raises TypeError:           If parameter 'direction' is not of type :class:`SweepDirection`.
		:raises TypeError:           If parameter 'arcPoint' is not of type :class:`Point2D`.
		:raises ValueError:          If parameter 'arcPoint' is on the line through parameter 'start' and parameter 'end'.
		:raises TypeError:           If parameter 'chordPosition' is not of type :class:`float`.
		:raises ValueError:          If parameter 'chordPosition' is out of range 0..1.
		:raises ValueError:          If parameter 'height' is None, while 'chordPosition' is given.
		:raises TypeError:           If parameter 'height' is not of type :class:`float` or :class:`int`.
		:raises ValueError:          If parameter 'height' is 0.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Shapes.Shape`,
		                             :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:          If parameter 'parent' is a shape, while 'copyPoints' is ``True``. |br|
		                             An edge references the points of its parent shape: use ``copyPoints=False``.
		:raises ValueError:          If no group of parameters for the circle is given. |br|
		                             Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally
		                             'chordPosition'.
		:raises ValueError:          If parameters of more than one group for the circle are given. |br|
		                             Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally
		                             'chordPosition'.
		"""
		from pyTooling.Cartesian2D.Groups import Container2DMixin

		super().__init__(
			start,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		start =  self._start
		end =    self._end
		chordX = end._x - start._x
		chordY = end._y - start._y
		try:
			if chordX == 0 and chordY == 0:
				ex = ValueError("Parameter 'end' is at the position of parameter 'start'.")
				ex.add_note(f"Got point {end}.")
				ex.add_note("An arc needs a chord from the start point to the end point.")
				raise ex

			givenNames = []
			if center is not None:
				givenNames.append("'center'")
			elif direction is not None:
				givenNames.append("'direction'")

			if arcPoint is not None:
				givenNames.append("'arcPoint'")

			if height is not None:
				givenNames.append("'height'")
			elif chordPosition is not None:
				givenNames.append("'chordPosition'")

			if len(givenNames) == 0:
				ex = ValueError("Parameters 'center', 'arcPoint' and 'height' are None.")
				ex.add_note("Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally 'chordPosition'.")
				raise ex
			elif len(givenNames) > 1:
				ex = ValueError(f"Parameters {', '.join(givenNames[:-1])} and {givenNames[-1]} are given together.")
				ex.add_note("Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally 'chordPosition'.")
				raise ex

			chordLength = sqrt(chordX ** 2 + chordY ** 2)
			if height is None and chordPosition is None:
				if center is not None or direction is not None:
					if center is None:
						raise ValueError("Parameter 'center' is None, while 'direction' is given.")
					elif not isinstance(center, Point2D):
						ex = TypeError("Parameter 'center' is not of type 'Point2D'.")
						ex.add_note(f"Got type '{getFullyQualifiedName(center)}'.")
						raise ex
					elif (radius := sqrt((start._x - center._x) ** 2 + (start._y - center._y) ** 2)) == 0:
						ex = ValueError("Parameter 'center' is at the position of parameter 'start'.")
						ex.add_note(f"Got point {center}.")
						raise ex
					elif not isclose(sqrt((end._x - center._x) ** 2 + (end._y - center._y) ** 2), radius):
						ex = ValueError("Parameter 'center' has another distance to parameter 'end' than to parameter 'start'.")
						ex.add_note(
							f"Got distance {radius} to start point {start} and "
							f"{sqrt((end._x - center._x) ** 2 + (end._y - center._y) ** 2)} to end point {end}."
						)
						raise ex

					if direction is None:
						raise ValueError("Parameter 'direction' is None, while 'center' is given.")
					elif not isinstance(direction, SweepDirection):
						ex = TypeError("Parameter 'direction' is not of type 'SweepDirection'.")
						ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
						raise ex
				else:
					if not isinstance(arcPoint, Point2D):
						ex = TypeError("Parameter 'arcPoint' is not of type 'Point2D'.")
						ex.add_note(f"Got type '{getFullyQualifiedName(arcPoint)}'.")
						raise ex
					elif (cross := (arcPoint._x - start._x) * chordY - (arcPoint._y - start._y) * chordX) == 0:
						ex = ValueError("Parameter 'arcPoint' is on the line through parameter 'start' and parameter 'end'.")
						ex.add_note(f"Got points {start}, {arcPoint} and {end}.")
						raise ex

					center =    circumcenter(start, arcPoint, end)
					radius =    sqrt((start._x - center._x) ** 2 + (start._y - center._y) ** 2)
					direction = SweepDirection.Counterclockwise if cross > 0 else SweepDirection.Clockwise

				centerHeight = (
					(center._x - start._x - chordX / 2) * -chordY + (center._y - start._y - chordY / 2) * chordX
				) / chordLength ** 2
				if direction is SweepDirection.Clockwise:
					relativeHeight = centerHeight + radius / chordLength
				else:
					relativeHeight = centerHeight - radius / chordLength

				chordPosition = 0.5
			else:
				if chordPosition is None:
					chordPosition = 0.5
				elif not isinstance(chordPosition, (int, float)):
					ex = TypeError("Parameter 'chordPosition' is not of type 'float'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(chordPosition)}'.")
					raise ex
				elif not 0 <= chordPosition <= 1:
					ex = ValueError("Parameter 'chordPosition' is out of range 0..1.")
					ex.add_note(f"Got value '{chordPosition}'.")
					raise ex

				if height is None:
					raise ValueError("Parameter 'height' is None, while 'chordPosition' is given.")
				elif not isinstance(height, (int, float)):
					ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
					raise ex
				elif height == 0:
					raise ValueError("Parameter 'height' is 0.")

				relativeHeight = height / chordLength
		except (ValueError, TypeError):
			if self._parent is None:
				start._parent = None
				end._parent =   None

			raise

		self._chordPosition = chordPosition
		self._height =        relativeHeight

		if self._parent is None:
			self.Parent = parent

	@property
	def Start(self) -> Point2D[Coordinate]:
		"""
		Property to access the arc's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the arc takes ownership of it and releases the previous start point.
		A point at the position of the end point is rejected, because the arc would have no chord. An edge of a shape
		doesn't own its points, so it can't replace them.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    Start point of the arc.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises ValueError:          If an assigned point is at the position of the arc's end point. |br|
		                             An arc needs a chord from the start point to the end point.
		:raises NotOwnedError:       If the arc is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the arc's end point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._start

	@Start.setter
	def Start(self, start: Point2D[Coordinate]) -> None:
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point2D):
			ex = TypeError("Parameter 'start' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif start is not self._end and start._x == self._end._x and start._y == self._end._y:
			ex = ValueError("Parameter 'start' is at the position of the arc's end point.")
			ex.add_note(f"Got point {start}.")
			ex.add_note("An arc needs a chord from the start point to the end point.")
			raise ex

		Segment2D.Start.fset(self, start)

	start = Start

	@property
	def End(self) -> Point2D[Coordinate]:
		"""
		Property to access the arc's end point (:attr:`_end`).

		An assigned point is referenced, not copied: the arc takes ownership of it and releases the previous end point. A
		point at the position of the start point is rejected, because the arc would have no chord. An edge of a shape
		doesn't own its points, so it can't replace them.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    End point of the arc.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises ValueError:          If an assigned point is at the position of the arc's start point. |br|
		                             An arc needs a chord from the start point to the end point.
		:raises NotOwnedError:       If the arc is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the arc's start point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._end

	@End.setter
	def End(self, end: Point2D[Coordinate]) -> None:
		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point2D):
			ex = TypeError("Parameter 'end' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex
		elif end is not self._start and end._x == self._start._x and end._y == self._start._y:
			ex = ValueError("Parameter 'end' is at the position of the arc's start point.")
			ex.add_note(f"Got point {end}.")
			ex.add_note("An arc needs a chord from the start point to the end point.")
			raise ex

		Segment2D.End.fset(self, end)

	end = End

	@readonly
	def ChordPosition(self) -> float:
		"""
		Read-only property to access the root point's position on the chord (:attr:`_chordPosition`).

		The root point is where the :attr:`Height` is measured. An arc given by a center or an arc point uses ``0.5``, the
		chord's midpoint.

		:returns: The position as a fraction from 0 (start point) to 1 (end point).
		"""
		return self._chordPosition

	@readonly
	def Height(self) -> float:
		"""
		Read-only property to return the arc's signed distance from the chord at the root point.

		The arc stores the height relative to the chord's length (:attr:`_height`), so this value follows the chord. A
		positive height is on the left of the chord, seen from the start point.

		:returns: The height for the current chord.
		"""
		return self._height * sqrt((self._end._x - self._start._x) ** 2 + (self._end._y - self._start._y) ** 2)

	@readonly
	def Center(self) -> Point2D[float]:
		"""
		Read-only property to return the center point of the arc's circle.

		The center is computed from the end points, the :attr:`ChordPosition` and the :attr:`Height` on each access.
		A center given to the constructor is therefore not returned as given: it can differ in the last digits of a
		:class:`float` (e.g. ``0.9999999999999432`` for ``1``), so compare it with :func:`math.isclose`.

		:returns: A new 2D-point without owner.
		"""
		start = self._start
		end =   self._end
		return circumcenter(start, chordPoint(start, end, self._chordPosition, self._height), end)

	@readonly
	def Direction(self) -> SweepDirection:
		"""
		Read-only property to return the direction, in which the arc sweeps from its start point to its end point.

		An arc with a positive height (on the left of the chord) runs clockwise. Mirroring the arc changes it.

		:returns: The arc's sweep direction.
		"""
		return SweepDirection.Clockwise if self._height > 0 else SweepDirection.Counterclockwise

	@readonly
	def Radius(self) -> float:
		"""
		Read-only property to return the radius of the arc's circle, the distance between the start point and the center.

		:returns: Radius of the arc.
		"""
		start =  self._start
		center = self.Center
		return sqrt((start._x - center._x) ** 2 + (start._y - center._y) ** 2)

	@readonly
	def StartAngle(self) -> float:
		"""
		Read-only property to return the angle of the start point, seen from the center.

		The angle is measured from the positive x-direction towards the positive y-direction.

		:returns: The angle in radians, from -:data:`math.pi` to :data:`math.pi`.
		"""
		center = self.Center
		return atan2(self._start._y - center._y, self._start._x - center._x)

	@readonly
	def EndAngle(self) -> float:
		"""
		Read-only property to return the angle of the end point, seen from the center.

		The angle is measured from the positive x-direction towards the positive y-direction.

		:returns: The angle in radians, from -:data:`math.pi` to :data:`math.pi`.
		"""
		center = self.Center
		return atan2(self._end._y - center._y, self._end._x - center._x)

	@readonly
	def SweepAngle(self) -> float:
		"""
		Read-only property to return the angle the arc sweeps from its start point to its end point.

		The angle is positive for a counterclockwise arc and negative for a clockwise arc, so :attr:`StartAngle` plus
		this angle is :attr:`EndAngle`, up to a multiple of 2 :data:`math.pi`.

		:returns: The angle in radians, between 0 and 2 :data:`math.pi` (counterclockwise) or between -2 :data:`math.pi`
		          and 0 (clockwise).
		"""
		if self._height > 0:
			return -((self.StartAngle - self.EndAngle) % (2 * pi))
		else:
			return (self.EndAngle - self.StartAngle) % (2 * pi)

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the length of the arc, its radius times the absolute sweep angle.

		:returns: Length of the arc.
		"""
		return self.Radius * abs(self.SweepAngle)

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the arc.

		The box encloses the start and end point, and each point of the circle with the smallest or largest x- or
		y-coordinate, which the arc passes.

		:returns: A new bounding box.
		"""
		start =      self._start
		end =        self._end
		center =     self.Center
		radius =     sqrt((start._x - center._x) ** 2 + (start._y - center._y) ** 2)
		startAngle = atan2(start._y - center._y, start._x - center._x)
		sweepAngle = abs(self.SweepAngle)
		minX =       min(start._x, end._x)
		minY =       min(start._y, end._y)
		maxX =       max(start._x, end._x)
		maxY =       max(start._y, end._y)
		for angle, x, y in (
			(0.0,     center._x + radius, center._y),
			(pi / 2,  center._x,          center._y + radius),
			(pi,      center._x - radius, center._y),
			(-pi / 2, center._x,          center._y - radius)
		):
			if self._height > 0:
				distance = (startAngle - angle) % (2 * pi)
			else:
				distance = (angle - startAngle) % (2 * pi)

			if distance <= sweepAngle:
				minX = min(minX, x)
				minY = min(minY, y)
				maxX = max(maxX, x)
				maxY = max(maxY, y)

		return BoundingBox2D(minX, minY, maxX, maxY)

	def _MirrorInnerY(self, twiceAxis: Coordinate) -> None:
		"""
		Reverse the arc's direction by negating its height, as its end points are mirrored at a horizontal axis (inplace).

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._height = -self._height

	def _MirrorInnerX(self, twiceAxis: Coordinate) -> None:
		"""
		Reverse the arc's direction by negating its height, as its end points are mirrored at a vertical axis (inplace).

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._height = -self._height

	def _MirrorInnerAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Reverse the arc's direction by negating its height, as its end points are mirrored at a line (inplace).

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		self._height = -self._height

	def Copy(self) -> Self:
		"""
		Create a new 2D arc segment as a copy of this 2D arc segment.

		The copy holds copies of the start and end point, and has the same chord position and height. It references the
		same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this 2D arc segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			chordPosition=self._chordPosition,
			height=self.Height,
			value=self._value,
			keyValuePairs=self._dict
		)

	def ToChord(self) -> LineSegment2D[Coordinate]:
		"""
		Create a new line segment from the arc's start point to its end point, the arc's chord.

		The line segment holds copies of the start and end point. It has no parent, value or key-value-pairs.

		:returns: A new line segment from the start point to the end point.
		"""
		return LineSegment2D(self._start, self._end)

	def _CopyAsEdge(self, start: Point2D[Coordinate], end: Point2D[Coordinate], shape: Shape) -> Self:
		"""
		Create a copy of this arc as an edge of a shape, between two of the shape's points.

		The copy has the same chord position and relative height. It references the same :attr:`Value` and holds a shallow
		copy of the key-value-pairs.

		:param start: The shape's point the edge starts at.
		:param end:   The shape's point the edge ends at.
		:param shape: The shape the edge belongs to.
		:returns:     A new edge of the shape.
		"""
		return self.__class__(
			start,
			end,
			chordPosition=self._chordPosition,
			height=self._height * sqrt((end._x - start._x) ** 2 + (end._y - start._y) ** 2),
			copyPoints=False,
			value=self._value,
			keyValuePairs=self._dict,
			parent=shape
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D arc segment for :func:`copy.deepcopy`.

		The copy holds copies of the start and end point, has the same chord position and height, and deep copies of the
		:attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D arc segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			chordPosition=self._chordPosition,
			height=self.Height,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def __repr__(self) -> str:
		"""
		Returns the 2D arc segment's string representation.

		:returns: The string representation of the 2D arc segment.
		"""
		return f"ArcSegment2D({self._start}, {self._end}, chordPosition={self._chordPosition}, height={self.Height})"

	def __str__(self) -> str:
		"""
		Returns the 2D arc segment's string equivalent.

		:returns: The string equivalent of the 2D arc segment.
		"""
		return f"({self._start} → {self._end}, height {self.Height} at {self._chordPosition})"


@export
@abstractclass
class BezierSegment2D(Segment2D[Coordinate], Generic[Coordinate]):
	"""
	Abstract base-class of 2D cartesian Bezier curve segments.

	A Bezier curve runs from its start point to its end point and is pulled towards its control points, which it passes
	only in special cases. The control points are owned like the start and end point.
	"""

	_controlPoints: tuple[Point2D[Coordinate], ...]  #: Control points of the curve, in curve order.

	@property
	def Start(self) -> Point2D[Coordinate]:
		"""
		Property to access the curve's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the curve takes ownership of it and releases the previous start
		point. An edge of a shape doesn't own its points, so it can't replace them.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    Start point of the curve.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises DuplicatePointError: If an assigned point is a control point of the curve.
		:raises NotOwnedError:       If the curve is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the curve's end point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._start

	@Start.setter
	def Start(self, start: Point2D[Coordinate]) -> None:
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point2D):
			ex = TypeError("Parameter 'start' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif any(start is controlPoint for controlPoint in self._controlPoints):
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			raise ex from ValueError("Parameter 'start' is a control point of the curve.")

		Segment2D.Start.fset(self, start)

	start = Start

	@property
	def End(self) -> Point2D[Coordinate]:
		"""
		Property to access the curve's end point (:attr:`_end`).

		An assigned point is referenced, not copied: the curve takes ownership of it and releases the previous end point.
		An edge of a shape doesn't own its points, so it can't replace them.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    End point of the curve.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point2D`.
		:raises DuplicatePointError: If an assigned point is a control point of the curve.
		:raises NotOwnedError:       If the curve is an edge of a shape.
		:raises DuplicatePointError: If an assigned point is the curve's start point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._end

	@End.setter
	def End(self, end: Point2D[Coordinate]) -> None:
		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point2D):
			ex = TypeError("Parameter 'end' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex
		elif any(end is controlPoint for controlPoint in self._controlPoints):
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {end}.")
			raise ex from ValueError("Parameter 'end' is a control point of the curve.")

		Segment2D.End.fset(self, end)

	end = End

	@readonly
	def ControlPoints(self) -> tuple[Point2D[Coordinate], ...]:
		"""
		Read-only property to access the curve's control points (:attr:`_controlPoints`).

		:returns: Tuple of control points, in curve order.
		"""
		return self._controlPoints

	def PointAt(self, t: Union[int, float]) -> Point2D[float]:
		"""
		Compute the point of the curve at a curve parameter.

		The curve starts at ``t = 0`` and ends at ``t = 1``. The new point has no owner.

		:param t:           The curve parameter, from 0 to 1.
		:returns:           A new 2D-point on the curve.
		:raises ValueError: If parameter 't' is None.
		:raises TypeError:  If parameter 't' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 't' is out of range 0..1.
		"""
		if t is None:
			raise ValueError("Parameter 't' is None.")
		elif not isinstance(t, (int, float)):
			ex = TypeError("Parameter 't' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(t)}'.")
			raise ex
		elif not 0 <= t <= 1:
			ex = ValueError("Parameter 't' is out of range 0..1.")
			ex.add_note(f"Got value '{t}'.")
			raise ex

		return self._PointAt(t)

	@abstractmethod
	def _PointAt(self, t: Union[int, float]) -> Point2D[float]:
		"""
		Compute the point of the curve at a curve parameter, without checking the parameter.

		:param t: The curve parameter, from 0 to 1.
		:returns: A new 2D-point on the curve.
		"""

	def _MoveInner(self, offset: BaseVector2D[Coordinate]) -> None:
		"""
		Move the curve's control points (inplace).

		:param offset: The 2D-vector or 2D-offset to move by.
		"""
		for controlPoint in self._controlPoints:
			controlPoint += offset

	def _MirrorInnerY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the curve's control points at a horizontal axis (inplace).

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		for controlPoint in self._controlPoints:
			controlPoint._y = twiceAxis - controlPoint._y

	def _MirrorInnerX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the curve's control points at a vertical axis (inplace).

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		for controlPoint in self._controlPoints:
			controlPoint._x = twiceAxis - controlPoint._x

	def _MirrorInnerAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the curve's control points at a line (inplace).

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		for controlPoint in self._controlPoints:
			controlPoint._MirrorAt(normal, distance)

	def ToTuple(self) -> tuple[tuple[Coordinate, Coordinate], ...]:
		"""
		Convert this 2D Bezier curve segment to a simple tuple of 2D-point tuples, in curve order.

		:returns: ``((x0, y0), (x1, y1), ...)`` tuple, from the start point over the control points to the end point.
		"""
		return tuple(point.ToTuple() for point in (self._start, *self._controlPoints, self._end))


@export
class QuadraticBezierSegment2D(BezierSegment2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 2D cartesian quadratic Bezier curve segment, having one control point.

	The curve leaves its start point towards the control point and arrives at its end point from the control point's
	direction.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		controlPoint:  Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Shape, Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a 2-dimensional quadratic Bezier curve segment from its start point, control point and end point.

		:param start:                Start point of the curve.
		:param controlPoint:         Control point of the curve.
		:param end:                  End point of the curve.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param value:                Optional, value of the curve. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the shape this curve is an edge of, or the group or canvas the curve is
		                             added to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'start' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'controlPoint' is None.
		:raises TypeError:           If parameter 'controlPoint' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint' is the same point as parameter 'start' or 'end', while
		                             parameter 'parent' isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint' is owned by another element, while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'controlPoint' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'end' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Shapes.Shape`,
		                             :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:          If parameter 'parent' is a shape, while 'copyPoints' is ``True``. |br|
		                             An edge references the points of its parent shape: use ``copyPoints=False``.
		"""
		from pyTooling.Cartesian2D.Groups import Container2DMixin

		super().__init__(
			start,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			if controlPoint is None:
				raise ValueError("Parameter 'controlPoint' is None.")
			elif not isinstance(controlPoint, Point2D):
				ex = TypeError("Parameter 'controlPoint' is not of type 'Point2D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(controlPoint)}'.")
				raise ex

			if self._parent is None:
				if copyPoints:
					controlPoint = controlPoint.Copy()
				else:
					for name, point in (
						("start", start),
						("end",   end)
					):
						if controlPoint is point:
							ex = DuplicatePointError("Point is given twice.")
							ex.add_note(f"Got point {point}.")
							ex.add_note("Use 'copyPoints=True' to copy the points.")
							raise ex from ValueError(f"Parameter 'controlPoint' is the same point as parameter '{name}'.")

					if controlPoint._parent is not None:
						ex = AlreadyOwnedError("Point is owned by another element already.")
						ex.add_note(f"Got point {controlPoint} owned by {controlPoint._parent!r}.")
						ex.add_note("Use 'copyPoints=True' to copy the point.")
						raise ex from ValueError("Parameter 'controlPoint' is owned by another element.")

				controlPoint._parent = self
			elif controlPoint._parent is not self._parent:
				ex = NotOwnedError("Point isn't owned by the parent shape.")
				ex.add_note(f"Got point {controlPoint} owned by {controlPoint._parent!r}.")
				raise ex from ValueError("Parameter 'controlPoint' isn't owned by parameter 'parent'.")
		except (ValueError, TypeError, Cartesian2DError):
			if self._parent is None:
				self._start._parent = None
				self._end._parent =   None

			raise

		self._controlPoints = (controlPoint, )

		if self._parent is None:
			self.Parent = parent

	@readonly
	def ControlPoint(self) -> Point2D[Coordinate]:
		"""
		Read-only property to return the curve's control point.

		:returns: Control point of the curve.
		"""
		return self._controlPoints[0]

	def _PointAt(self, t: Union[int, float]) -> Point2D[float]:
		"""
		Compute the point of the curve at a curve parameter, without checking the parameter.

		:param t: The curve parameter, from 0 to 1.
		:returns: A new 2D-point on the curve.
		"""
		start =        self._start
		controlPoint = self._controlPoints[0]
		end =          self._end
		inverse =      1 - t
		return Point2D(
			inverse ** 2 * start._x + 2 * inverse * t * controlPoint._x + t ** 2 * end._x,
			inverse ** 2 * start._y + 2 * inverse * t * controlPoint._y + t ** 2 * end._y
		)

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the curve.

		The box encloses the start and end point, and the points of the curve with the smallest or largest x- or
		y-coordinate between them. The control point's box is larger, if the curve doesn't pass the control point.

		:returns: A new bounding box.
		"""
		start =        self._start
		controlPoint = self._controlPoints[0]
		end =          self._end
		parameters =   []
		for startValue, controlValue, endValue in (
			(start._x, controlPoint._x, end._x),
			(start._y, controlPoint._y, end._y)
		):
			denominator = startValue - 2 * controlValue + endValue
			if denominator != 0 and 0 < (t := (startValue - controlValue) / denominator) < 1:
				parameters.append(t)

		return BoundingBox2D.FromPoints((start, end, *(self._PointAt(t) for t in parameters)))

	def Copy(self) -> Self:
		"""
		Create a new 2D quadratic Bezier curve segment as a copy of this one.

		The copy holds copies of the start point, control point and end point. It references the same :attr:`Value` and
		holds a shallow copy of the key-value-pairs.

		:returns: Copy of this 2D quadratic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._end,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D quadratic Bezier curve segment for :func:`copy.deepcopy`.

		The copy holds copies of the start point, control point and end point, and deep copies of the :attr:`Value` and
		the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D quadratic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._end,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def _CopyAsEdge(self, start: Point2D[Coordinate], end: Point2D[Coordinate], shape: Shape) -> Self:
		"""
		Create a copy of this curve as an edge of a shape, between two of the shape's points.

		The copy's control point is a copy owned by the shape. It references the same :attr:`Value` and holds a
		shallow copy of the key-value-pairs.

		:param start: The shape's point the edge starts at.
		:param end:   The shape's point the edge ends at.
		:param shape: The shape the edge belongs to.
		:returns:     A new edge of the shape.
		"""
		controlPoint = self._controlPoints[0]
		return self.__class__(
			start,
			Point2D(controlPoint._x, controlPoint._y, parent=shape),
			end,
			copyPoints=False,
			value=self._value,
			keyValuePairs=self._dict,
			parent=shape
		)

	def __repr__(self) -> str:
		"""
		Returns the 2D quadratic Bezier curve segment's string representation.

		:returns: The string representation of the 2D quadratic Bezier curve segment.
		"""
		return f"QuadraticBezierSegment2D({self._start}, {self._controlPoints[0]}, {self._end})"

	def __str__(self) -> str:
		"""
		Returns the 2D quadratic Bezier curve segment's string equivalent.

		:returns: The string equivalent of the 2D quadratic Bezier curve segment.
		"""
		return f"({self._start} .. controls {self._controlPoints[0]} .. {self._end})"


@export
class CubicBezierSegment2D(BezierSegment2D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 2D cartesian cubic Bezier curve segment, having two control points.

	The curve leaves its start point towards the first control point and arrives at its end point from the second
	control point's direction.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		controlPoint1: Point2D[Coordinate],
		controlPoint2: Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Shape, Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a 2-dimensional cubic Bezier curve segment from its start point, two control points and end point.

		:param start:                Start point of the curve.
		:param controlPoint1:        First control point of the curve, next to the start point.
		:param controlPoint2:        Second control point of the curve, next to the end point.
		:param end:                  End point of the curve.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param value:                Optional, value of the curve. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the shape this curve is an edge of, or the group or canvas the curve is
		                             added to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'start' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'controlPoint1' is None.
		:raises TypeError:           If parameter 'controlPoint1' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint1' is the same point as parameter 'start' or 'end', while
		                             parameter 'parent' isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint1' is owned by another element, while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'controlPoint1' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'controlPoint2' is None.
		:raises TypeError:           If parameter 'controlPoint2' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint2' is the same point as parameter 'start', 'end' or
		                             'controlPoint1', while parameter 'parent' isn't a shape and 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint2' is owned by another element, while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'controlPoint2' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while parameter 'parent'
		                             isn't a shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while parameter 'parent' isn't a
		                             shape and 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:       If parameter 'end' isn't owned by parameter 'parent'.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Shapes.Shape`,
		                             :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:          If parameter 'parent' is a shape, while 'copyPoints' is ``True``. |br|
		                             An edge references the points of its parent shape: use ``copyPoints=False``.
		"""
		from pyTooling.Cartesian2D.Groups import Container2DMixin

		super().__init__(
			start,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			for name, controlPoint in (
				("controlPoint1", controlPoint1),
				("controlPoint2", controlPoint2)
			):
				if controlPoint is None:
					raise ValueError(f"Parameter '{name}' is None.")
				elif not isinstance(controlPoint, Point2D):
					ex = TypeError(f"Parameter '{name}' is not of type 'Point2D'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(controlPoint)}'.")
					raise ex

			if self._parent is None:
				if copyPoints:
					controlPoint1 = controlPoint1.Copy()
					controlPoint2 = controlPoint2.Copy()
				else:
					for name, controlPoint in (
						("controlPoint1", controlPoint1),
						("controlPoint2", controlPoint2)
					):
						for otherName, point in (
							("start", start),
							("end",   end)
						):
							if controlPoint is point:
								ex = DuplicatePointError("Point is given twice.")
								ex.add_note(f"Got point {point}.")
								ex.add_note("Use 'copyPoints=True' to copy the points.")
								raise ex from ValueError(f"Parameter '{name}' is the same point as parameter '{otherName}'.")

						if controlPoint._parent is not None:
							ex = AlreadyOwnedError("Point is owned by another element already.")
							ex.add_note(f"Got point {controlPoint} owned by {controlPoint._parent!r}.")
							ex.add_note("Use 'copyPoints=True' to copy the point.")
							raise ex from ValueError(f"Parameter '{name}' is owned by another element.")

					if controlPoint2 is controlPoint1:
						ex = DuplicatePointError("Point is given twice.")
						ex.add_note(f"Got point {controlPoint2}.")
						ex.add_note("Use 'copyPoints=True' to copy the points.")
						raise ex from ValueError("Parameter 'controlPoint2' is the same point as parameter 'controlPoint1'.")

				controlPoint1._parent = self
				controlPoint2._parent = self
			else:
				for name, controlPoint in (
					("controlPoint1", controlPoint1),
					("controlPoint2", controlPoint2)
				):
					if controlPoint._parent is not self._parent:
						ex = NotOwnedError("Point isn't owned by the parent shape.")
						ex.add_note(f"Got point {controlPoint} owned by {controlPoint._parent!r}.")
						raise ex from ValueError(f"Parameter '{name}' isn't owned by parameter 'parent'.")
		except (ValueError, TypeError, Cartesian2DError):
			if self._parent is None:
				self._start._parent = None
				self._end._parent =   None

			raise

		self._controlPoints = (controlPoint1, controlPoint2)

		if self._parent is None:
			self.Parent = parent

	@readonly
	def ControlPoint1(self) -> Point2D[Coordinate]:
		"""
		Read-only property to return the curve's first control point, next to the start point.

		:returns: First control point of the curve.
		"""
		return self._controlPoints[0]

	@readonly
	def ControlPoint2(self) -> Point2D[Coordinate]:
		"""
		Read-only property to return the curve's second control point, next to the end point.

		:returns: Second control point of the curve.
		"""
		return self._controlPoints[1]

	def _PointAt(self, t: Union[int, float]) -> Point2D[float]:
		"""
		Compute the point of the curve at a curve parameter, without checking the parameter.

		:param t: The curve parameter, from 0 to 1.
		:returns: A new 2D-point on the curve.
		"""
		start =         self._start
		controlPoint1 = self._controlPoints[0]
		controlPoint2 = self._controlPoints[1]
		end =           self._end
		inverse =       1 - t
		return Point2D(
			inverse ** 3 * start._x + 3 * inverse ** 2 * t * controlPoint1._x + 3 * inverse * t ** 2 * controlPoint2._x +
			t ** 3 * end._x,
			inverse ** 3 * start._y + 3 * inverse ** 2 * t * controlPoint1._y + 3 * inverse * t ** 2 * controlPoint2._y +
			t ** 3 * end._y
		)

	@readonly
	def BoundingBox(self) -> BoundingBox2D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the curve.

		The box encloses the start and end point, and the points of the curve with the smallest or largest x- or
		y-coordinate between them. The control points' box is larger, if the curve doesn't pass the control points.

		:returns: A new bounding box.
		"""
		start =         self._start
		controlPoint1 = self._controlPoints[0]
		controlPoint2 = self._controlPoints[1]
		end =           self._end
		parameters =    []
		for startValue, controlValue1, controlValue2, endValue in (
			(start._x, controlPoint1._x, controlPoint2._x, end._x),
			(start._y, controlPoint1._y, controlPoint2._y, end._y)
		):
			quadratic = 3 * (controlValue1 - controlValue2) + endValue - startValue
			linear =    2 * (startValue - 2 * controlValue1 + controlValue2)
			constant =  controlValue1 - startValue
			if quadratic != 0:
				discriminant = linear ** 2 - 4 * quadratic * constant
				if discriminant >= 0:
					root = sqrt(discriminant)
					for t in ((-linear + root) / (2 * quadratic), (-linear - root) / (2 * quadratic)):
						if 0 < t < 1:
							parameters.append(t)
			elif linear != 0 and 0 < (t := -constant / linear) < 1:
				parameters.append(t)

		return BoundingBox2D.FromPoints((start, end, *(self._PointAt(t) for t in parameters)))

	def Copy(self) -> Self:
		"""
		Create a new 2D cubic Bezier curve segment as a copy of this one.

		The copy holds copies of the start point, both control points and the end point. It references the same
		:attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this 2D cubic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._controlPoints[1],
			self._end,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 2D cubic Bezier curve segment for :func:`copy.deepcopy`.

		The copy holds copies of the start point, both control points and the end point, and deep copies of the
		:attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 2D cubic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._controlPoints[1],
			self._end,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def _CopyAsEdge(self, start: Point2D[Coordinate], end: Point2D[Coordinate], shape: Shape) -> Self:
		"""
		Create a copy of this curve as an edge of a shape, between two of the shape's points.

		The copy's control points are copies owned by the shape. It references the same :attr:`Value` and holds a
		shallow copy of the key-value-pairs.

		:param start: The shape's point the edge starts at.
		:param end:   The shape's point the edge ends at.
		:param shape: The shape the edge belongs to.
		:returns:     A new edge of the shape.
		"""
		controlPoint1 = self._controlPoints[0]
		controlPoint2 = self._controlPoints[1]
		return self.__class__(
			start,
			Point2D(controlPoint1._x, controlPoint1._y, parent=shape),
			Point2D(controlPoint2._x, controlPoint2._y, parent=shape),
			end,
			copyPoints=False,
			value=self._value,
			keyValuePairs=self._dict,
			parent=shape
		)

	def __repr__(self) -> str:
		"""
		Returns the 2D cubic Bezier curve segment's string representation.

		:returns: The string representation of the 2D cubic Bezier curve segment.
		"""
		return f"CubicBezierSegment2D({self._start}, {self._controlPoints[0]}, {self._controlPoints[1]}, {self._end})"

	def __str__(self) -> str:
		"""
		Returns the 2D cubic Bezier curve segment's string equivalent.

		:returns: The string equivalent of the 2D cubic Bezier curve segment.
		"""
		return f"({self._start} .. controls {self._controlPoints[0]} and {self._controlPoints[1]} .. {self._end})"
