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
"""

"""

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
class Point2D(Generic[Coordinate]):
	x: Coordinate
	y: Coordinate

	def __init__(self, x: Coordinate, y: Coordinate) -> None:
		if not isinstance(x, (int, float)):
			raise TypeError()
		if not isinstance(y, (int, float)):
			raise TypeError()

		self.x = x
		self.y = y

	def Copy(self) -> "Point2D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.x, self.y)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		return self.x, self.y

	def __add__(self, other: Any) -> "Point2D[Coordinate]":
		if isinstance(other, Offset2D):
			return Point2D(
				self.x + other.xOffset,
				self.y + other.yOffset
			)
		else:
			raise TypeError()

	def __iadd__(self, other: Any) -> "Point2D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset2D):
			self.x += other.xOffset
			self.y += other.yOffset
		else:
			raise TypeError()

		return self

	def __sub__(self, other: Any) -> Union["Offset2D[Coordinate]", "Point2D[Coordinate]"]:
		if isinstance(other, Point2D):
			return Offset2D(
				self.x - other.x,
				self.y - other.y
			)
		elif isinstance(other, Offset2D):
			return Point2D(
				self.x - other.xOffset,
				self.y - other.yOffset
			)
		else:
			raise TypeError()

	def __isub__(self, other: Any) -> "Point2D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset2D):
			self.x -= other.xOffset
			self.y -= other.yOffset
		else:
			raise TypeError()

		return self

	def __repr__(self) -> str:
		return f"Point2D({self.x}, {self.y})"

	def __str__(self) -> str:
		return f"({self.x}, {self.y})"


@export
class Origin2D(Point2D[Coordinate]):
	def __init__(self) -> None:
		super().__init__(0, 0)

	def Copy(self) -> "Origin2D":  # TODO: Python 3.11: -> Self:
		raise RuntimeError()

	def __repr__(self) -> str:
		return f"Origin2D({self.x}, {self.y})"


@export
class Offset2D(Generic[Coordinate]):
	xOffset: Coordinate
	yOffset: Coordinate

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate) -> None:
		if not isinstance(xOffset, (int, float)):
			raise TypeError()
		if not isinstance(yOffset, (int, float)):
			raise TypeError()

		self.xOffset = xOffset
		self.yOffset = yOffset

	def Copy(self) -> "Offset2D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.xOffset, self.yOffset)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		return self.xOffset, self.yOffset

	def __add__(self, other: Any) -> "Offset2D[Coordinate]":
		if isinstance(other, Offset2D):
			return Offset2D(
				self.xOffset + other.xOffset,
				self.yOffset + other.yOffset
			)
		else:
			raise TypeError()

	def __iadd__(self, other: Any) -> "Offset2D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset2D):
			self.xOffset += other.xOffset
			self.yOffset += other.yOffset
		else:
			raise TypeError()

		return self

	def __sub__(self, other: Any) -> "Offset2D[Coordinate]":
		if isinstance(other, Offset2D):
			return Offset2D(
				self.xOffset - other.xOffset,
				self.yOffset - other.yOffset
			)
		else:
			raise TypeError()

	def __isub__(self, other: Any) -> "Offset2D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset2D):
			self.xOffset -= other.xOffset
			self.yOffset -= other.yOffset
		else:
			raise TypeError()

		return self

	def __repr__(self) -> str:
		return f"Offset2D({self.xOffset}, {self.yOffset})"

	def __str__(self) -> str:
		return f"({self.xOffset}, {self.yOffset})"


@export
class Size2D:
	width: Coordinate
	height: Coordinate

	def __init__(self, width: Coordinate, height: Coordinate) -> None:
		if not isinstance(width, (int, float)):
			raise TypeError()
		if not isinstance(height, (int, float)):
			raise TypeError()

		self.width = width
		self.height = height

	def Copy(self) -> "Size2D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.width, self.height)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		return self.width, self.height

	def __repr__(self) -> str:
		return f"Size({self.width}, {self.height})"

	def __str__(self) -> str:
		return f"({self.width}, {self.height})"


@export
class Segment2D(Generic[Coordinate]):
	start: Point2D[Coordinate]
	end: Point2D[Coordinate]

	def __init__(self, start: Point2D[Coordinate], end: Point2D[Coordinate], copyPoints: bool = True) -> None:
		self.start = start.Copy() if copyPoints else start
		self.end = end.Copy() if copyPoints else end


@export
class LineSegment2D(Segment2D[Coordinate]):
	@readonly
	def Length(self) -> float:
		return sqrt((self.end.x - self.start.x) ** 2 + (self.end.x - self.start.x) ** 2)

	def AngleTo(self, other: "LineSegment2D[Coordinate]") -> float:
		vectorA = self.ToOffset()
		vectorB = other.ToOffset()
		scalarProductAB = vectorA.xOffset * vectorB.xOffset + vectorA.yOffset * vectorB.yOffset

		return acos(scalarProductAB / (abs(self.Length) * abs(other.Length)))

	def ToOffset(self) -> Offset2D[Coordinate]:
		return self.end - self.start

	def ToTuple(self) -> Tuple[Tuple[Coordinate, Coordinate], Tuple[Coordinate, Coordinate]]:
		return self.start.ToTuple(), self.end.ToTuple()

	def __repr__(self) -> str:
		return f"LineSegment2D({self.start}, {self.end})"

	def __str__(self) -> str:
		return f"({self.start} → {self.end})"
