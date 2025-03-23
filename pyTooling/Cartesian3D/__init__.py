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
"""

"""

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
class Point3D(Generic[Coordinate]):
	x: Coordinate
	y: Coordinate
	z: Coordinate

	def __init__(self, x: Coordinate, y: Coordinate, z: Coordinate) -> None:
		if not isinstance(x, (int, float)):
			raise TypeError()
		if not isinstance(y, (int, float)):
			raise TypeError()
		if not isinstance(z, (int, float)):
			raise TypeError()

		self.x = x
		self.y = y
		self.z = z

	def Copy(self) -> "Point3D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.x, self.y, self.z)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate, Coordinate]:
		return self.x, self.y, self.z

	def __add__(self, other: Any) -> "Point3D[Coordinate]":
		if isinstance(other, Offset3D):
			return Point3D(
				self.x + other.xOffset,
				self.y + other.yOffset,
				self.z + other.zOffset
			)
		else:
			raise TypeError()

	def __iadd__(self, other: Any) -> "Point3D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset3D):
			self.x += other.xOffset
			self.y += other.yOffset
			self.z += other.zOffset
		else:
			raise TypeError()

		return self

	def __sub__(self, other: Any) -> Union["Offset3D[Coordinate]", "Point3D[Coordinate]"]:
		if isinstance(other, Point3D):
			return Offset3D(
				self.x - other.x,
				self.y - other.y,
				self.z - other.z
			)
		elif isinstance(other, Offset3D):
			return Point3D(
				self.x - other.xOffset,
				self.y - other.yOffset,
				self.z - other.zOffset
			)
		else:
			raise TypeError()

	def __isub__(self, other: Any) -> "Point3D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset3D):
			self.x -= other.xOffset
			self.y -= other.yOffset
			self.z -= other.zOffset
		else:
			raise TypeError()

		return self

	def __repr__(self) -> str:
		return f"Point3D({self.x}, {self.y}, {self.z})"

	def __str__(self) -> str:
		return f"({self.x}, {self.y}, {self.z})"


@export
class Origin3D(Point3D[Coordinate]):
	def __init__(self) -> None:
		super().__init__(0, 0, 0)

	def Copy(self) -> "Origin3D":  # TODO: Python 3.11: -> Self:
		raise RuntimeError()

	def __repr__(self) -> str:
		return f"Origin3D({self.x}, {self.y}, {self.z})"


@export
class Offset3D(Generic[Coordinate]):
	xOffset: Coordinate
	yOffset: Coordinate
	zOffset: Coordinate

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate, zOffset: Coordinate) -> None:
		if not isinstance(xOffset, (int, float)):
			raise TypeError()
		if not isinstance(yOffset, (int, float)):
			raise TypeError()
		if not isinstance(zOffset, (int, float)):
			raise TypeError()

		self.xOffset = xOffset
		self.yOffset = yOffset
		self.zOffset = zOffset

	def Copy(self) -> "Offset3D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.xOffset, self.yOffset, self.zOffset)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate]:
		return self.xOffset, self.yOffset, self.zOffset

	def __add__(self, other: Any) -> "Offset3D[Coordinate]":
		if isinstance(other, Offset3D):
			return Offset3D(
				self.xOffset + other.xOffset,
				self.yOffset + other.yOffset,
				self.zOffset + other.zOffset
			)
		else:
			raise TypeError()

	def __iadd__(self, other: Any) -> "Offset3D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset3D):
			self.xOffset += other.xOffset
			self.yOffset += other.yOffset
			self.zOffset += other.zOffset
		else:
			raise TypeError()

		return self

	def __sub__(self, other: Any) -> "Offset3D[Coordinate]":
		if isinstance(other, Offset3D):
			return Offset3D(
				self.xOffset - other.xOffset,
				self.yOffset - other.yOffset,
				self.zOffset - other.zOffset
			)
		else:
			raise TypeError()

	def __isub__(self, other: Any) -> "Offset3D":  # TODO: Python 3.11: -> Self:
		if isinstance(other, Offset3D):
			self.xOffset -= other.xOffset
			self.yOffset -= other.yOffset
			self.zOffset -= other.zOffset
		else:
			raise TypeError()

		return self

	def __repr__(self) -> str:
		return f"Offset3D({self.xOffset}, {self.yOffset}, {self.zOffset})"

	def __str__(self) -> str:
		return f"({self.xOffset}, {self.yOffset}, {self.zOffset})"


@export
class Size3D:
	width: Coordinate
	height: Coordinate
	depth: Coordinate

	def __init__(self, width: Coordinate, height: Coordinate, depth: Coordinate) -> None:
		if not isinstance(width, (int, float)):
			raise TypeError()
		if not isinstance(height, (int, float)):
			raise TypeError()
		if not isinstance(depth, (int, float)):
			raise TypeError()

		self.width = width
		self.height = height
		self.depth = depth

	def Copy(self) -> "Size3D":  # TODO: Python 3.11: -> Self:
		return self.__class__(self.width, self.height, self.depth)

	def ToTuple(self) -> Tuple[Coordinate, Coordinate, Coordinate]:
		return self.width, self.height, self.depth

	def __repr__(self) -> str:
		return f"Size({self.width}, {self.height}, {self.depth})"

	def __str__(self) -> str:
		return f"({self.width}, {self.height}, {self.depth})"


@export
class Segment3D(Generic[Coordinate]):
	start: Point3D[Coordinate]
	end: Point3D[Coordinate]

	def __init__(self, start: Point3D[Coordinate], end: Point3D[Coordinate], copyPoints: bool = True) -> None:
		self.start = start.Copy() if copyPoints else start
		self.end = end.Copy() if copyPoints else end


@export
class LineSegment3D(Segment3D[Coordinate]):
	@readonly
	def Length(self) -> float:
		return sqrt((self.end.x - self.start.x) ** 2 + (self.end.y - self.start.y) ** 2 + (self.end.z - self.start.z) ** 2)

	def AngleTo(self, other: "LineSegment3D[Coordinate]") -> float:
		vectorA = self.ToOffset()
		vectorB = other.ToOffset()
		scalarProductAB = vectorA.xOffset * vectorB.xOffset + vectorA.yOffset * vectorB.yOffset + vectorA.zOffset * vectorB.zOffset

		return acos(scalarProductAB / (abs(self.Length) * abs(other.Length)))

	def ToOffset(self) -> Offset3D[Coordinate]:
		return self.end - self.start

	def ToTuple(self) -> Tuple[Tuple[Coordinate, Coordinate, Coordinate], Tuple[Coordinate, Coordinate, Coordinate]]:
		return self.start.ToTuple(), self.end.ToTuple()

	def __repr__(self) -> str:
		return f"LineSegment3D({self.start}, {self.end})"

	def __str__(self) -> str:
		return f"({self.start} → {self.end})"
