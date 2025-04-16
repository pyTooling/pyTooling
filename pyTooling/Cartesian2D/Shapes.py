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
"""An implementation of 2D cartesian shapes for Python."""
from sys import version_info

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
	"""Base-class for all 2D cartesian shapes."""


@export
class Trapezium(Shape[Coordinate], Generic[Coordinate]):
	"""
	A Trapezium is a four-sided polygon, having four edges (sides) and four corners (vertices).
	"""
	points:   Tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the trapezium.
	segments: Tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the trapezium.

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a trapezium with 4 corners.

		:param p00: First corner.
		:param p01: Second corner.
		:param p11: Third corner.
		:param p10: Forth corner
		"""
		if not isinstance(p00, Point2D):
			ex = TypeError(f"Parameter 'p00' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(p00)}'.")
			raise ex
		if not isinstance(p01, Point2D):
			ex = TypeError(f"Parameter 'p01' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(p01)}'.")
			raise ex
		if not isinstance(p11, Point2D):
			ex = TypeError(f"Parameter 'p11' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(p11)}'.")
			raise ex
		if not isinstance(p10, Point2D):
			ex = TypeError(f"Parameter 'p10' is not of type Point2D.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(p10)}'.")
			raise ex

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
	"""
	A rectangle is a trapezium, where opposite edges a parallel to each other and all inner angels are 90°.
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a rectangle with 4 corners.

		:param p00: First corner.
		:param p01: Second corner.
		:param p11: Third corner.
		:param p10: Forth corner
		"""
		super().__init__(p00, p01, p11, p10)

		if self.segments[0].Length != self.segments[2].Length or self.segments[1].Length != self.segments[3].Length:
			raise ValueError(f"Line segments (edges) of opposite edges different lengths.")

		if (self.segments[0].AngleTo(self.segments[1]) == 0.0 and self.segments[1].AngleTo(self.segments[2]) == 0.0
			and self.segments[2].AngleTo(self.segments[3]) == 0.0 and self.segments[3].AngleTo(self.segments[0]) == 0.0):
			raise ValueError(f"Line segments (edges) have no 90° angles.")


@export
class Square(Rectangle[Coordinate]):
	"""
	A square is a rectangle, where all edges have the same length and all inner angels are 90°.
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a square with 4 corners.

		:param p00: First corner.
		:param p01: Second corner.
		:param p11: Third corner.
		:param p10: Forth corner
		"""
		super().__init__(p00, p01, p11, p10)

		if self.segments[0].Length != self.segments[1].Length:
			raise ValueError(f"Line segments (edges) between corners have different lengths.")
