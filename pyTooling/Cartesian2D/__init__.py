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

from math                  import atan2, sqrt
from typing                import TYPE_CHECKING, Any, Generic, Iterable, Optional as Nullable, Self, TypeVar, Union

from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Exceptions  import ToolingException, AlreadyInHierarchyError, NotAChildError, NotInSameHierarchyError
from pyTooling.Common      import getFullyQualifiedName

if TYPE_CHECKING:
	from pyTooling.Cartesian2D.Shapes import Rectangle, Shape


Coordinate = TypeVar("Coordinate", bound=Union[int, float])


@export
class Cartesian2DError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Cartesian2D`."""


@export
class NoAreaError(Cartesian2DError):
	"""The exception is raised when an operation needs an area, but a bounding box has no width or no height."""


@export
class AlreadyOwnedError(Cartesian2DError, AlreadyInHierarchyError):
	"""
	The exception is raised when an element is given to an element, but another element owns it already.

	For example, a point given to a shape with ``copyPoints=False`` while another shape owns it.
	"""


@export
class NotOwnedError(Cartesian2DError, NotAChildError):
	"""
	The exception is raised when an element replaces or removes an element it doesn't own.

	For example, an edge of a polygon references the polygon's corners, so it can't replace them.
	"""


@export
class NotInSameFrameError(Cartesian2DError, NotInSameHierarchyError):
	"""
	The exception is raised when points or segments of different frames are combined in a computation.

	A frame is what the coordinates of an element are relative to. Combining coordinates of different frames would mix
	unrelated values silently.
	"""


@export
class Point2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian point."""

	_x:      Coordinate                         #: The x-direction coordinate.
	_y:      Coordinate                         #: The y-direction coordinate.
	_parent: Nullable[Union[Segment2D, Shape]]  #: Segment or shape owning the point, or ``None``.

	def __init__(self, x: Coordinate, y: Coordinate, *, parent: Nullable[Union[Segment2D, Shape]] = None) -> None:
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
		:raises TypeError:  If parameter 'parent' is not of type :class:`Segment2D` or
		                    :class:`~pyTooling.Cartesian2D.Shapes.Shape`.
		"""
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

		if parent is not None:
			from pyTooling.Cartesian2D.Shapes import Shape

			if not isinstance(parent, (Segment2D, Shape)):
				ex = TypeError("Parameter 'parent' is not of type 'Segment2D' or 'Shape'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex

		self._x =      x
		self._y =      y
		self._parent = parent

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
	def Parent(self) -> Nullable[Union[Segment2D, Shape]]:
		"""
		Read-only property to access the segment or shape owning the point (:attr:`_parent`).

		:returns: The owning segment or shape, or ``None``, if no element owns the point.
		"""
		return self._parent

	@readonly
	def Frame(self) -> Any:
		"""
		Read-only property to return the frame the point's coordinates are relative to.

		The frame is the owning element's frame. A point without an owner has no frame.

		:returns: The frame, or ``None``, if the point has no frame.
		"""
		return None if self._parent is None else self._parent.Frame

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

	def __add__(self, other: Any) -> Point2D[Coordinate]:
		"""
		Adds a 2D-offset to this 2D-point and creates a new 2D-point.

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          A new 2D-point shifted by the 2D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
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
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 2D-offset to this 2D-point (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self._x += other._xOffset
			self._y += other._yOffset
		elif isinstance(other, tuple):
			self.X += other[0]
			self.Y += other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union[Offset2D[Coordinate], Point2D[Coordinate]]:
		"""
		Subtract two 2D-Points from each other and create a new 2D-offset.

		:param other:                The second 2D-point as :class:`Point2D`.
		:returns:                    A new 2D-offset representing the distance between these two points.
		:raises TypeError:           If parameter 'other' is not of type :class:`Point2D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this point.
		"""
		if isinstance(other, Point2D):
			if self.Frame is not other.Frame:
				ex = NotInSameFrameError("Points are in different frames.")
				ex.add_note(f"Got points {self} and {other}.")
				raise ex from ValueError("Parameter 'other' is in another frame.")

			return Offset2D(
				self._x - other._x,
				self._y - other._y
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 2D-offset to this 2D-point (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self._x -= other._xOffset
			self._y -= other._yOffset
		elif isinstance(other, tuple):
			self.X -= other[0]
			self.Y -= other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
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

		:raises RuntimeError: Because an origin can't be copied.
		"""
		raise RuntimeError("An origin can't be copied.")

	def __repr__(self) -> str:
		"""
		Returns the 2D origin's string representation.

		:returns: The string representation of the 2D origin.
		"""
		return f"Origin2D({self._x}, {self._y})"


@export
class Offset2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian offset."""

	_xOffset: Coordinate  #: The x-direction offset
	_yOffset: Coordinate  #: The y-direction offset

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate) -> None:
		"""
		Initializes a 2-dimensional offset.

		:param xOffset:     x-direction offset.
		:param yOffset:     y-direction offset.
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

	def ToTuple(self) -> tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-offset to a simple 2-element tuple.

		:returns: ``(x, y)`` tuple.
		"""
		return self._xOffset, self._yOffset

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two 2D-offsets for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-offsets are equal.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			return self._xOffset == other._xOffset and self._yOffset == other._yOffset
		elif isinstance(other, tuple):
			return self._xOffset == other[0] and self._yOffset == other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two 2D-offsets for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-offsets are unequal.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> Offset2D[Coordinate]:
		"""
		Negate all components of this 2D-offset and create a new 2D-offset.

		:returns: 2D-offset with negated offset components.
		"""
		return self.__class__(
			-self._xOffset,
			-self._yOffset
		)

	def __add__(self, other: Any) -> Offset2D[Coordinate]:
		"""
		Adds a 2D-offset to this 2D-offset and creates a new 2D-offset.

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          A new 2D-offset extended by the 2D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
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
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 2D-offset to this 2D-offset (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self._xOffset += other._xOffset
			self._yOffset += other._yOffset
		elif isinstance(other, tuple):
			self.XOffset += other[0]
			self.YOffset += other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Offset2D[Coordinate]:
		"""
		Subtracts a 2D-offset from this 2D-offset and creates a new 2D-offset.

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          A new 2D-offset reduced by the 2D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
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
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 2D-offset from this 2D-offset (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or tuple.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self._xOffset -= other._xOffset
			self._yOffset -= other._yOffset
		elif isinstance(other, tuple):
			self.XOffset -= other[0]
			self.YOffset -= other[1]
		else:
			ex = TypeError("Parameter 'other' is not of type 'Offset2D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 2D offset's string representation.

		:returns: The string representation of the 2D offset.
		"""
		return f"Offset2D({self._xOffset}, {self._yOffset})"

	def __str__(self) -> str:
		"""
		Returns the 2D offset's string equivalent.

		:returns: The string equivalent of the 2D offset.
		"""
		return f"({self._xOffset}, {self._yOffset})"


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
class BoundingBox(Generic[Coordinate], metaclass=ExtendedType, slots=True):
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

	def Union(self, other: BoundingBox[Coordinate]) -> BoundingBox[Coordinate]:
		"""
		Create the smallest bounding box enclosing this and another bounding box.

		:param other:       The second bounding box.
		:returns:           A new bounding box enclosing both bounding boxes.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			min(self._minX, other._minX),
			min(self._minY, other._minY),
			max(self._maxX, other._maxX),
			max(self._maxY, other._maxY)
		)

	def HasOverlap(self, other: BoundingBox[Coordinate]) -> bool:
		"""
		Check if this bounding box and another bounding box overlap.

		Two bounding boxes touching only at a border or a corner don't overlap, so elements can be aligned next to each
		other without a distance.

		:param other:       The second bounding box.
		:returns:           ``True``, if the inner areas of both bounding boxes overlap.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox'.")
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
		:raises TypeError: If the second operand is not of type :class:`BoundingBox`.
		"""
		if not isinstance(other, BoundingBox):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox")
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
		:raises TypeError: If the second operand is not of type :class:`BoundingBox`.
		"""
		if not isinstance(other, BoundingBox):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox")
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
		return f"BoundingBox({self._minX}, {self._minY}, {self._maxX}, {self._maxY})"

	def __str__(self) -> str:
		"""
		Returns the bounding box' string equivalent.

		:returns: The string equivalent of the bounding box, its corners with the smallest and the largest coordinates.
		"""
		return f"(({self._minX}, {self._minY}), ({self._maxX}, {self._maxY}))"


@export
class Segment2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	An implementation of a 2D cartesian segment.

	A standalone segment owns its start and end point. A segment with a parent shape is an edge of that shape: it
	references two of the shape's points, which stay owned by the shape.
	"""

	_parent: Nullable[Shape]      #: Shape, whose edge this segment is, or ``None`` for a standalone segment.
	_start:  Point2D[Coordinate]  #: Start point of a segment.
	_end:    Point2D[Coordinate]  #: End point of a segment.

	def __init__(
		self,
		start:      Point2D[Coordinate],
		end:        Point2D[Coordinate],
		copyPoints: bool = True,
		*,
		parent:     Nullable[Shape] = None
	) -> None:
		"""
		Initializes a 2-dimensional segment.

		:param start:              Start point of the segment.
		:param end:                End point of the segment.
		:param copyPoints:         Optional, if ``True``, the given points are copied instead of referenced. Default:
		                           ``True``.
		:param parent:             Optional, the shape this segment is an edge of. Default: ``None``.
		:raises ValueError:        If parameter 'start' is None.
		:raises TypeError:         If parameter 'start' is not of type :class:`Point2D`.
		:raises AlreadyOwnedError: If parameter 'start' is owned by another element, while no parent is given and
		                           'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:     If parameter 'start' isn't owned by parameter 'parent'.
		:raises ValueError:        If parameter 'end' is None.
		:raises TypeError:         If parameter 'end' is not of type :class:`Point2D`.
		:raises ValueError:        If parameter 'end' is the same point as parameter 'start', while no parent is given and
		                           'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError: If parameter 'end' is owned by another element, while no parent is given and
		                           'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises NotOwnedError:     If parameter 'end' isn't owned by parameter 'parent'.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Shapes.Shape`.
		:raises ValueError:        If parameter 'parent' is given, while 'copyPoints' is ``True``. |br|
		                           An edge references the points of its parent shape: use ``copyPoints=False``.
		"""
		from pyTooling.Cartesian2D.Shapes import Shape

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

		if parent is None:
			if copyPoints:
				start = start.Copy()
				end =   end.Copy()
			elif end is start:
				ex = ValueError("Parameter 'end' is the same point as parameter 'start'.")
				ex.add_note(f"Got point {start}.")
				ex.add_note("Use 'copyPoints=True' to copy the points.")
				raise ex
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
		elif not isinstance(parent, Shape):
			ex = TypeError("Parameter 'parent' is not of type 'Shape'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		elif copyPoints:
			ex = ValueError("Parameter 'parent' is given, while 'copyPoints' is True.")
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
		self._start =  start
		self._end =    end

	@readonly
	def Parent(self) -> Nullable[Shape]:
		"""
		Read-only property to access the shape this segment is an edge of (:attr:`_parent`).

		:returns: The parent shape, or ``None`` for a standalone segment.
		"""
		return self._parent

	@readonly
	def Frame(self) -> Any:
		"""
		Read-only property to return the frame the segment's coordinates are relative to.

		An edge is in its shape's frame. A standalone segment has no frame.

		:returns: The frame, or ``None``, if the segment has no frame.
		"""
		return None if self._parent is None else self._parent.Frame

	@property
	def Start(self) -> Point2D[Coordinate]:
		"""
		Property to access the segment's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous start
		point. An edge of a shape doesn't own its points, so it can't replace them.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                  Start point of the segment.
		:raises ValueError:        If ``None`` is assigned.
		:raises TypeError:         If an assigned value is not of type :class:`Point2D`.
		:raises NotOwnedError:     If the segment is an edge of a shape.
		:raises AlreadyOwnedError: If an assigned point is owned by another element.
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
		elif self._parent is not None:
			ex = NotOwnedError("Segment doesn't own its start point.")
			ex.add_note(f"The segment is an edge of {self._parent!r}, which owns the point.")
			raise ex
		elif start._parent is not None and (start._parent is not self or start is self._end):
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

		:returns:                  End point of the segment.
		:raises ValueError:        If ``None`` is assigned.
		:raises TypeError:         If an assigned value is not of type :class:`Point2D`.
		:raises NotOwnedError:     If the segment is an edge of a shape.
		:raises AlreadyOwnedError: If an assigned point is owned by another element.
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
		elif self._parent is not None:
			ex = NotOwnedError("Segment doesn't own its end point.")
			ex.add_note(f"The segment is an edge of {self._parent!r}, which owns the point.")
			raise ex
		elif end._parent is not None and (end._parent is not self or end is self._start):
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {end} owned by {end._parent!r}.")
			raise ex from ValueError("Parameter 'end' is owned by another element.")

		self._end._parent = None
		end._parent =       self
		self._end =         end

	end = End

	@readonly
	def BoundingBox(self) -> BoundingBox[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the segment's start and end point.

		:returns: A new bounding box.
		"""
		start = self._start
		end =   self._end
		return BoundingBox(min(start._x, end._x), min(start._y, end._y), max(start._x, end._x), max(start._y, end._y))

	def Move(self, offset: Offset2D[Coordinate]) -> None:
		"""
		Move the segment by moving its start and end point (inplace).

		An edge of a shape moves the shape's corners it references.

		:param offset:      The 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`Offset2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, Offset2D):
			ex = TypeError("Parameter 'offset' is not of type 'Offset2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._start += offset
		self._end +=   offset

	def Copy(self) -> Self:
		"""
		Create a new 2D-segment as a copy of this 2D-segment.

		The copy holds copies of the start and end point.

		:returns: Copy of this 2D-segment.
		"""
		return self.__class__(self._start, self._end)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 2D-segment for :func:`copy.copy`.

		:returns: Copy of this 2D-segment.
		"""
		return self.Copy()


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
