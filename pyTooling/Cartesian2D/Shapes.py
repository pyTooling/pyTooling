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

from typing import Generic, Tuple, Optional as Nullable

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import getFullyQualifiedName
	from pyTooling.Cartesian2D import Coordinate, Point2D, LineSegment2D
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Cartesian2D] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
		from Cartesian2D import Coordinate, Point2D, LineSegment2D
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Cartesian2D] Could not import directly!")
		raise ex


@export
class Shape(Generic[Coordinate]):
	pass


@export
class Trapezium(Shape[Coordinate]):
	points: Tuple[Point2D[Coordinate], ...]
	segments: Tuple[LineSegment2D[Coordinate], ...]

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]):
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


@export
class Rectangle(Trapezium[Coordinate]):
	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]):
		super().__init__(p00, p01, p11, p10)

		if self.segments[0].Length != self.segments[2].Length or self.segments[1].Length != self.segments[3].Length:
			raise ValueError()

		if (self.segments[0].AngleTo(self.segments[1]) == 0.0 and self.segments[1].AngleTo(self.segments[2]) == 0.0
			and self.segments[2].AngleTo(self.segments[3]) == 0.0 and self.segments[3].AngleTo(self.segments[0]) == 0.0):
			raise ValueError()


@export
class Square(Rectangle[Coordinate]):
	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]):
		super().__init__(p00, p01, p11, p10)

		if self.segments[0].Length != self.segments[1].Length:
			raise ValueError()
