# ==================================================================================================================== #
#             _____           _ _               ____           _            _             _____ ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ /|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  |_ \| | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |___) | |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|____/|____/                  #
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
"""An implementation of 3D cartesian data structures for Python."""
from sys    import version_info

from math   import sqrt, acos
from typing import Union, Generic, Any, Tuple

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import getFullyQualifiedName
	from pyTooling.Cartesian2D import Coordinate
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Cartesian2D] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
		from Cartesian2D import Coordinate
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Cartesian2D] Could not import directly!")
		raise ex


@export
class Point3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian point."""

	x: Coordinate  #: The x-direction coordinate.
	y: Coordinate  #: The y-direction coordinate.
	z: Coordinate  #: The z-direction coordinate.

	def __init__(self, x: Coordinate, y: Coordinate, z: Coordinate) -> None:
		"""
		Initializes a 3-dimensional point.

		:param x: X-coordinate.
		:param y: Y-coordinate.
		:param z: Z-coordinate.
		:raises TypeError: If x/y/z-coordinate is not of type integer or float.
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
		if not isinstance(z, (int, float)):
			ex = TypeError(f"Parameter 'z' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self.x = x
		self.y = y
		self.z = z

	def Copy(self) -> "Point3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 3D-point as a copy of this 3D point.

		:return: Copy of this 3D-point.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-point moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-point moved by a negative 3D-offset.
		"""
		return self.__class__(self.x, self.y, self.z)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-Point to a simple 3-element tuple.

		:return: ``(x, y, z)`` tuple.
		"""
		return self.x, self.y, self.z

	def __add__(self, other: Any) -> "Point3D[Coordinate]":
		"""
		Adds a 3D-offset to this 3D-point and creates a new 3D-point.

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:return:           A new 3D-point shifted by the 3D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self.x + other.xOffset,
				self.y + other.yOffset,
				self.z + other.zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.x + other[0],
				self.y + other[1],
				self.z + other[2]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> "Point3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Adds a 3D-offset to this 3D-point (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:return:           This 3D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self.x += other.xOffset
			self.y += other.yOffset
			self.z += other.zOffset
		elif isinstance(other, tuple):
			self.x += other[0]
			self.y += other[1]
			self.z += other[2]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union["Offset3D[Coordinate]", "Point3D[Coordinate]"]:
		"""
		Subtract two 3D-Points from each other and create a new 3D-offset.

		:param other:      A 3D-point as :class:`Point3D`.
		:return:           A new 3D-offset representing the distance between these two points.
		:raises TypeError: If parameter 'other' is not a :class:`Point3D`.
		"""
		if isinstance(other, Point3D):
			return Offset3D(
				self.x - other.x,
				self.y - other.y,
				self.z - other.z
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Point3D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> "Point3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Subtracts a 3D-offset to this 3D-point (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:return:           This 3D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self.x -= other.xOffset
			self.y -= other.yOffset
			self.z -= other.zOffset
		elif isinstance(other, tuple):
			self.x -= other[0]
			self.y -= other[1]
			self.z -= other[2]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		return f"Point3D({self.x}, {self.y}, {self.z})"

	def __str__(self) -> str:
		return f"({self.x}, {self.y}, {self.z})"


@export
class Origin3D(Point3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian origin."""

	def __init__(self) -> None:
		"""
		Initializes a 3-dimensional origin.
		"""
		super().__init__(0, 0, 0)

	def Copy(self) -> "Origin3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		:raises RuntimeError: Because an origin can't be copied.
		"""
		raise RuntimeError(f"An origin can't be copied.")

	def __repr__(self) -> str:
		return f"Origin3D({self.x}, {self.y}, {self.z})"


@export
class Offset3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian offset."""

	xOffset: Coordinate  #: The x-direction offset
	yOffset: Coordinate  #: The y-direction offset
	zOffset: Coordinate  #: The z-direction offset

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate, zOffset: Coordinate) -> None:
		"""
		Initializes a 3-dimensional offset.

		:param xOffset:    x-direction offset.
		:param yOffset:    y-direction offset.
		:param zOffset:    z-direction offset.
		:raises TypeError: If x/y/z-offset is not of type integer or float.
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
		if not isinstance(zOffset, (int, float)):
			ex = TypeError(f"Parameter 'zOffset' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(zOffset)}'.")
			raise ex

		self.xOffset = xOffset
		self.yOffset = yOffset
		self.zOffset = zOffset

	def Copy(self) -> "Offset3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 3D-offset as a copy of this 3D-offset.

		:returns: Copy of this 3D-offset.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-offset moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-offset moved by a negative 3D-offset.
		"""
		return self.__class__(self.xOffset, self.yOffset, self.zOffset)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-offset to a simple 3-element tuple.

		:returns: ``(x, y, z)`` tuple.
		"""
		return self.xOffset, self.yOffset, self.zOffset

	def __eq__(self, other) -> bool:
		"""
		Compare two 3D-offsets for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-offsets are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.xOffset == other.xOffset and self.yOffset == other.yOffset and self.zOffset == other.zOffset
		elif isinstance(other, tuple):
			return self.xOffset == other[0] and self.yOffset == other[1] and self.zOffset == other[2]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other) -> bool:
		"""
		Compare two 3D-offsets for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-offsets are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Offset3D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> "Offset3D[Coordinate]":
		"""
		Negate all components of this 3D-offset and create a new 3D-offset.

		:returns: 3D-offset with negated offset components.
		"""
		return self.__class__(
			-self.xOffset,
			-self.yOffset,
			-self.zOffset
		)

	def __add__(self, other: Any) -> "Offset3D[Coordinate]":
		"""
		Adds a 3D-offset to this 3D-offset and creates a new 3D-offset.

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:returns:          A new 3D-offset extended by the 3D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self.xOffset + other.xOffset,
				self.yOffset + other.yOffset,
				self.zOffset + other.zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.xOffset + other[0],
				self.yOffset + other[1],
				self.zOffset + other[2]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> "Offset3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Adds a 3D-offset to this 3D-offset (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self.xOffset += other.xOffset
			self.yOffset += other.yOffset
			self.zOffset += other.zOffset
		elif isinstance(other, tuple):
			self.xOffset += other[0]
			self.yOffset += other[1]
			self.zOffset += other[2]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> "Offset3D[Coordinate]":
		"""
		Subtracts a 3D-offset from this 3D-offset and creates a new 3D-offset.

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:returns:          A new 3D-offset reduced by the 3D-offset.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			return self.__class__(
				self.xOffset - other.xOffset,
				self.yOffset - other.yOffset,
				self.zOffset - other.zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self.xOffset - other[0],
				self.yOffset - other[1],
				self.zOffset - other[2]
			)
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> "Offset3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Subtracts a 3D-offset from this 3D-offset (inplace).

		:param other:      A 3D-offset as :class:`Offset3D` or :class:`tuple`.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not a :class:`Offset3D` or :class:`tuple`.
		"""
		if isinstance(other, Offset3D):
			self.xOffset -= other.xOffset
			self.yOffset -= other.yOffset
			self.zOffset -= other.zOffset
		elif isinstance(other, tuple):
			self.xOffset -= other[0]
			self.yOffset -= other[1]
			self.zOffset -= other[2]
		else:
			ex = TypeError(f"Parameter 'other' is not of type Offset3D or tuple.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		return f"Offset3D({self.xOffset}, {self.yOffset}, {self.zOffset})"

	def __str__(self) -> str:
		return f"({self.xOffset}, {self.yOffset}, {self.zOffset})"


@export
class Size3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian size."""

	width:  Coordinate  #: width in x-direction.
	height: Coordinate  #: height in y-direction.
	depth:  Coordinate  #: depth in z-direction.

	def __init__(self, width: Coordinate, height: Coordinate, depth: Coordinate) -> None:
		"""
		Initializes a 2-dimensional size.

		:param width:      width in x-direction.
		:param height:     height in y-direction.
		:param depth:      depth in z-direction.
		:raises TypeError: If width/height/depth is not of type integer or float.
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
		if not isinstance(depth, (int, float)):
			ex = TypeError(f"Parameter 'depth' is not of type integer or float.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex

		self.width =  width
		self.height = height
		self.depth =  depth

	def Copy(self) -> "Size3D[Coordinate]":  # TODO: Python 3.11: -> Self:
		"""
		Create a new 3D-size as a copy of this 3D-size.

		:returns: Copy of this 3D-size.
		"""
		return self.__class__(self.width, self.height, self.depth)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-size to a simple 3-element tuple.

		:return: ``(width, height, depth)`` tuple.
		"""
		return self.width, self.height, self.depth

	def __repr__(self) -> str:
		return f"Size3D({self.width}, {self.height}, {self.depth})"

	def __str__(self) -> str:
		return f"({self.width}, {self.height}, {self.depth})"


@export
class Segment3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian segment."""

	start: Point3D[Coordinate]  #: Start point of a segment.
	end:   Point3D[Coordinate]  #: End point of a segment.

	def __init__(self, start: Point3D[Coordinate], end: Point3D[Coordinate], copyPoints: bool = True) -> None:
		"""
		Initializes a 3-dimensional segment.

		:param start:      Start point of the segment.
		:param end:        End point of the segment.
		:raises TypeError: If start/end is not of type Point3D.
		"""
		if not isinstance(start, Point3D):
			ex = TypeError(f"Parameter 'start' is not of type Point3D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		if not isinstance(end, Point3D):
			ex = TypeError(f"Parameter 'end' is not of type Point3D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex

		self.start = start.Copy() if copyPoints else start
		self.end =   end.Copy()   if copyPoints else end


@export
class LineSegment3D(Segment3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian line segment."""

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean distance between start and end point.

		:return: Euclidean distance between start and end point
		"""
		return sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2 + (self.end.z - self.start.z) ** 2)

	def AngleTo(self, other: "LineSegment3D[Coordinate]") -> float:
		vectorA = self.ToOffset()
		vectorB = other.ToOffset()
		scalarProductAB = vectorA.xOffset * vectorB.xOffset + vectorA.yOffset * vectorB.yOffset + vectorA.zOffset * vectorB.zOffset

		return acos(scalarProductAB / (abs(self.Length) * abs(other.Length)))

	def ToOffset(self) -> Offset3D[Coordinate]:
		"""
		Convert this 3D line segment to a 3D-offset.

		:return: 3D-offset as :class:`Offset3D`
		"""
		return self.end - self.start

	def ToTuple(self) -> Tuple[Tuple[Coordinate, Coordinate, Coordinate], Tuple[Coordinate, Coordinate, Coordinate]]:
		"""
		Convert this 3D line segment to a simple 2-element tuple of 3D-point tuples.

		:return: ``((x1, y1, z1), (x2, y2, z2))`` tuple.
		"""
		return self.start.ToTuple(), self.end.ToTuple()

	def __repr__(self) -> str:
		return f"LineSegment3D({self.start}, {self.end})"

	def __str__(self) -> str:
		return f"({self.start} → {self.end})"
