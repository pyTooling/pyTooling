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
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""An implementation of 2D cartesian data structures for Python."""
from sys    import version_info

from math   import sqrt, acos
from typing import TypeVar, Union, Generic, Any, Tuple

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Cartesian2D] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Cartesian2D] Could not import directly!")
		raise ex


Coordinate = TypeVar("Coordinate", bound=Union[int, float])


@export
class Point2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian point."""

	x: Coordinate  #: The x-direction coordinate.
	y: Coordinate  #: The y-direction coordinate.

	def __init__(self, x: Coordinate, y: Coordinate) -> None:
		"""
		Initializes a 2-dimensional point.

		:param x: X-coordinate.
		:param y: Y-coordinate.
		:raises TypeError: If x/y-coordinate is not of type integer or float.
		"""
		if not isinstance(x, (int, float)):
			ex = TypeError(f"Parameter 'x' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex
		if not isinstance(y, (int, float)):
			ex = TypeError(f"Parameter 'y' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self.x = x
		self.y = y

	def Copy(self) -> "Point2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 2D-point as a copy of this 2D point.

		:returns: Copy of this 2D-point.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 2D-point moved by a positive 2D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 2D-point moved by a negative 2D-offset.
		"""
		return self.__class__(self.x, self.y)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-Point to a simple 2-element tuple.

		:returns: ``(x, y)`` tuple.
		"""
		return self.x, self.y

	def __add__(self, other: Any) -> "Point2D[Coordinate]":
		"""
		Adds a 2D-offset to this 2D-point and creates a new 2D-point.

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          A new 2D-point shifted by the 2D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			return self.__class__(
				self.x + other.xOffset,
				self.y + other.yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.x + other[0],
				self.y + other[1]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> "Point2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Adds a 2D-offset to this 2D-point (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self.x += other.xOffset
			self.y += other.yOffset
		elif isinstance(other, tuple):
			self.x += other[0]
			self.y += other[1]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union["Offset2D[Coordinate]", "Point2D[Coordinate]"]:
		"""
		Subtract two 2D-Points from each other and create a new 2D-offset.

		:param other:      A 2D-point as :class:`Point2D`.
		:returns:          A new 2D-offset representing the distance between these two points.
		:raises TypeError: If parameter 'other' is not a :class:`Point2D`.
		"""
		if isinstance(other, Point2D):
			return Offset2D(
				self.x - other.x,
				self.y - other.y
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> "Point2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Subtracts a 2D-offset to this 2D-point (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self.x -= other.xOffset
			self.y -= other.yOffset
		elif isinstance(other, tuple):
			self.x -= other[0]
			self.y -= other[1]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 2D point's string representation.

		:returns: The string representation of the 2D point.
		"""
		return f"Point2D({self.x}, {self.y})"

	def __str__(self) -> str:
		"""
		Returns the 2D point's string equivalent.

		:returns: The string equivalent of the 2D point.
		"""
		return f"({self.x}, {self.y})"


@export
class Origin2D(Point2D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 2D cartesian origin."""

	def __init__(self) -> None:
		"""
		Initializes a 2-dimensional origin.
		"""
		super().__init__(0, 0)

	def Copy(self) -> "Origin2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		:raises RuntimeError: Because an origin can't be copied.
		"""
		raise RuntimeError(f"An origin can't be copied.")

	def __repr__(self) -> str:
		"""
		Returns the 2D origin's string representation.

		:returns: The string representation of the 2D origin.
		"""
		return f"Origin2D({self.x}, {self.y})"


@export
class Offset2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian offset."""

	xOffset: Coordinate  #: The x-direction offset
	yOffset: Coordinate  #: The y-direction offset

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate) -> None:
		"""
		Initializes a 2-dimensional offset.

		:param xOffset:    x-direction offset.
		:param yOffset:    y-direction offset.
		:raises TypeError: If x/y-offset is not of type integer or float.
		"""
		if not isinstance(xOffset, (int, float)):
			ex = TypeError(f"Parameter 'xOffset' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex
		if not isinstance(yOffset, (int, float)):
			ex = TypeError(f"Parameter 'yOffset' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		self.xOffset = xOffset
		self.yOffset = yOffset

	def Copy(self) -> "Offset2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 2D-offset as a copy of this 2D-offset.

		:returns: Copy of this 2D-offset.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 2D-offset moved by a positive 2D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 2D-offset moved by a negative 2D-offset.
		"""
		return self.__class__(self.xOffset, self.yOffset)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-offset to a simple 2-element tuple.

		:returns: ``(x, y)`` tuple.
		"""
		return self.xOffset, self.yOffset

	def __eq__(self, other) -> bool:
		"""
		Compare two 2D-offsets for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-offsets are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			return self.xOffset == other.xOffset and self.yOffset == other.yOffset
		elif isinstance(other, tuple):
			return self.xOffset == other[0] and self.yOffset == other[1]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other) -> bool:
		"""
		Compare two 2D-offsets for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 2D-offsets are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Offset2D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> "Offset2D[Coordinate]":
		"""
		Negate all components of this 2D-offset and create a new 2D-offset.

		:returns: 2D-offset with negated offset components.
		"""
		return self.__class__(
			-self.xOffset,
			-self.yOffset
		)

	def __add__(self, other: Any) -> "Offset2D[Coordinate]":
		"""
		Adds a 2D-offset to this 2D-offset and creates a new 2D-offset.

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          A new 2D-offset extended by the 2D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			return self.__class__(
				self.xOffset + other.xOffset,
				self.yOffset + other.yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.xOffset + other[0],
				self.yOffset + other[1]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> "Offset2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Adds a 2D-offset to this 2D-offset (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self.xOffset += other.xOffset
			self.yOffset += other.yOffset
		elif isinstance(other, tuple):
			self.xOffset += other[0]
			self.yOffset += other[1]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> "Offset2D[Coordinate]":
		"""
		Subtracts a 2D-offset from this 2D-offset and creates a new 2D-offset.

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          A new 2D-offset reduced by the 2D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			return self.__class__(
				self.xOffset - other.xOffset,
				self.yOffset - other.yOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.xOffset - other[0],
				self.yOffset - other[1]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> "Offset2D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Subtracts a 2D-offset from this 2D-offset (inplace).

		:param other:      A 2D-offset as :class:`Offset2D` or :class:`tuple`.
		:returns:          This 2D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset2D` or :class:`tuple`.
		"""
		if isinstance(other, Offset2D):
			self.xOffset -= other.xOffset
			self.yOffset -= other.yOffset
		elif isinstance(other, tuple):
			self.xOffset -= other[0]
			self.yOffset -= other[1]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset2D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 2D offset's string representation.

		:returns: The string representation of the 2D offset.
		"""
		return f"Offset2D({self.xOffset}, {self.yOffset})"

	def __str__(self) -> str:
		"""
		Returns the 2D offset's string equivalent.

		:returns: The string equivalent of the 2D offset.
		"""
		return f"({self.xOffset}, {self.yOffset})"


@export
class Size2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian size."""

	width:  Coordinate  #: width in x-direction.
	height: Coordinate  #: height in y-direction.

	def __init__(self, width: Coordinate, height: Coordinate) -> None:
		"""
		Initializes a 2-dimensional size.

		:param width:      width in x-direction.
		:param height:     height in y-direction.
		:raises TypeError: If width/height is not of type integer or float.
		"""
		if not isinstance(width, (int, float)):
			ex = TypeError(f"Parameter 'width' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex
		if not isinstance(height, (int, float)):
			ex = TypeError(f"Parameter 'height' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		self.width = width
		self.height = height

	def Copy(self) -> "Size2D":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 2D-size as a copy of this 2D-size.

		:returns: Copy of this 2D-size.
		"""
		return self.__class__(self.width, self.height)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		"""
		Convert this 2D-size to a simple 2-element tuple.

		:return: ``(width, height)`` tuple.
		"""
		return self.width, self.height

	def __repr__(self) -> str:
		"""
		Returns the 2D size's string representation.

		:returns: The string representation of the 2D size.
		"""
		return f"Size2D({self.width}, {self.height})"

	def __str__(self) -> str:
		"""
		Returns the 2D size's string equivalent.

		:returns: The string equivalent of the 2D size.
		"""
		return f"({self.width}, {self.height})"


@export
class Segment2D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 2D cartesian segment."""

	start: Point2D[Coordinate]  #: Start point of a segment.
	end:   Point2D[Coordinate]  #: End point of a segment.

	def __init__(self, start: Point2D[Coordinate], end: Point2D[Coordinate], copyPoints: bool = True) -> None:
		"""
		Initializes a 2-dimensional segment.

		:param start:      Start point of the segment.
		:param end:        End point of the segment.
		:raises TypeError: If start/end is not of type Point2D.
		"""
		if not isinstance(start, Point2D):
			ex = TypeError(f"Parameter 'start' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		if not isinstance(end, Point2D):
			ex = TypeError(f"Parameter 'end' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex

		self.start = start.Copy() if copyPoints else start
		self.end =   end.Copy()   if copyPoints else end


@export
class LineSegment2D(Segment2D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 2D cartesian line segment."""

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean distance between start and end point.

		:return: Euclidean distance between start and end point
		"""
		return sqrt((self.end.x - self.start.x) ** 2 + (self.end.x - self.start.x) ** 2)

	def AngleTo(self, other: "LineSegment2D[Coordinate]") -> float:
		vectorA = self.ToOffset()
		vectorB = other.ToOffset()
		scalarProductAB = vectorA.xOffset * vectorB.xOffset + vectorA.yOffset * vectorB.yOffset

		return acos(scalarProductAB / (abs(self.Length) * abs(other.Length)))

	def ToOffset(self) -> Offset2D[Coordinate]:
		"""
		Convert this 2D line segment to a 2D-offset.

		:return: 2D-offset as :class:`Offset2D`
		"""
		return self.end - self.start

	def ToTuple(self) -> Tuple[Tuple[Coordinate, Coordinate], Tuple[Coordinate, Coordinate]]:
		"""
		Convert this 2D line segment to a simple 2-element tuple of 2D-point tuples.

		:return: ``((x1, y1), (x2, y2))`` tuple.
		"""
		return self.start.ToTuple(), self.end.ToTuple()

	def __repr__(self) -> str:
		"""
		Returns the 2D line segment's string representation.

		:returns: The string representation of the 2D line segment.
		"""
		return f"LineSegment2D({self.start}, {self.end})"

	def __str__(self) -> str:
		"""
		Returns the 2D line segment's string equivalent.

		:returns: The string equivalent of the 2D line segment.
		"""
		return f"({self.start} → {self.end})"
