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
from typing                import TypeVar, Union, Generic, Any, Self

from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName


Coordinate = TypeVar("Coordinate", bound=Union[int, float])


@export
class Point2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian point."""

	_x: Coordinate  #: The x-direction coordinate.
	_y: Coordinate  #: The y-direction coordinate.

	def __init__(self, x: Coordinate, y: Coordinate) -> None:
		"""
		Initializes a 2-dimensional point.

		:param x:           X-coordinate.
		:param y:           Y-coordinate.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
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

		self._x = x
		self._y = y

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

	def Copy(self) -> Self:
		"""
		Create a new 2D-point as a copy of this 2D point.

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

		:param other:      A 2D-point as :class:`Point2D`.
		:returns:          A new 2D-offset representing the distance between these two points.
		:raises TypeError: If parameter 'other' is not of type :class:`Point2D`.
		"""
		if isinstance(other, Point2D):
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
class Segment2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian segment."""

	_start: Point2D[Coordinate]  #: Start point of a segment.
	_end:   Point2D[Coordinate]  #: End point of a segment.

	def __init__(self, start: Point2D[Coordinate], end: Point2D[Coordinate], copyPoints: bool = True) -> None:
		"""
		Initializes a 2-dimensional segment.

		:param start:       Start point of the segment.
		:param end:         End point of the segment.
		:param copyPoints:  Optional, if ``True``, the given points are copied instead of referenced.
		:raises ValueError: If parameter 'start' is None.
		:raises TypeError:  If parameter 'start' is not of type :class:`Point2D`.
		:raises ValueError: If parameter 'end' is None.
		:raises TypeError:  If parameter 'end' is not of type :class:`Point2D`.
		"""
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

		self._start = start.Copy() if copyPoints else start
		self._end =   end.Copy()   if copyPoints else end

	@property
	def Start(self) -> Point2D[Coordinate]:
		"""
		Property to access the segment's start point (:attr:`_start`).

		An assigned point is referenced, not copied.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           Start point of the segment.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`Point2D`.
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

		self._start = start

	start = Start

	@property
	def End(self) -> Point2D[Coordinate]:
		"""
		Property to access the segment's end point (:attr:`_end`).

		An assigned point is referenced, not copied.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           End point of the segment.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`Point2D`.
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

		self._end = end

	end = End

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

		:param other:       The second line segment.
		:returns:           The angle in radians.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`LineSegment2D`.
		:raises ValueError: If parameter 'other' has length 0.
		:raises ValueError: If this line segment has length 0.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, LineSegment2D):
			ex = TypeError("Parameter 'other' is not of type 'LineSegment2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex
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
