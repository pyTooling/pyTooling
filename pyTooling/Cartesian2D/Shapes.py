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

from math                  import degrees, isclose, pi
from typing                import Generic

from pyTooling.Decorators  import export
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Cartesian2D import Coordinate, Point2D, LineSegment2D


@export
class Shape(Generic[Coordinate]):
	"""Base-class for all 2D cartesian shapes."""


@export
class Trapezium(Shape[Coordinate], Generic[Coordinate]):
	"""
	A Trapezium is a four-sided polygon, having four edges (sides) and four corners (vertices).
	"""
	points:   tuple[Point2D[Coordinate], ...]        #: A tuple of 2D-points describing the trapezium.
	segments: tuple[LineSegment2D[Coordinate], ...]  #: A tuple of 2D line segments describing the trapezium.

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a trapezium with 4 corners.

		:param p00:        First corner.
		:param p01:        Second corner.
		:param p11:        Third corner.
		:param p10:        Fourth corner.
		:raises TypeError: If a given point is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		"""
		if not isinstance(p00, Point2D):
			ex = TypeError("Parameter 'p00' is not of type Point2D.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p00)}'.")
			raise ex

		if not isinstance(p01, Point2D):
			ex = TypeError("Parameter 'p01' is not of type Point2D.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p01)}'.")
			raise ex

		if not isinstance(p11, Point2D):
			ex = TypeError("Parameter 'p11' is not of type Point2D.")
			ex.add_note(f"Got type '{getFullyQualifiedName(p11)}'.")
			raise ex

		if not isinstance(p10, Point2D):
			ex = TypeError("Parameter 'p10' is not of type Point2D.")
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
	A rectangle is a trapezium, where opposite edges are parallel to each other and all inner angles are 90 |degree| .
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a rectangle with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:raises TypeError:  If a given point is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		"""
		super().__init__(p00, p01, p11, p10)

		for index in range(2):
			edge =         self.segments[index]
			oppositeEdge = self.segments[index + 2]
			if not isclose(edge.Length, oppositeEdge.Length):
				ex = ValueError("Opposite line segments (edges) have different lengths.")
				ex.add_note(f"Got lengths {edge.Length} and {oppositeEdge.Length}.")
				raise ex

		for edge in self.segments[:2]:
			if edge.Length == 0.0:
				ex = ValueError("Line segment (edge) has length 0.")
				ex.add_note(f"Got corners {edge.start} and {edge.end}.")
				raise ex

		for index in range(2):
			edge =     self.segments[index]
			nextEdge = self.segments[index + 1]
			angle =    pi - edge.AngleTo(nextEdge)
			if not isclose(angle, pi / 2):
				ex = ValueError("Inner angle of a rectangle is not 90°.")
				ex.add_note(f"Got {degrees(angle):.2f}° at corner {edge.end}.")
				raise ex


@export
class Square(Rectangle[Coordinate]):
	"""
	A square is a rectangle, where all edges have the same length and all inner angles are 90 |degree| .
	"""

	def __init__(self, p00: Point2D[Coordinate], p01: Point2D[Coordinate], p11: Point2D[Coordinate], p10: Point2D[Coordinate]) -> None:
		"""
		Initializes a square with 4 corners.

		:param p00:         First corner.
		:param p01:         Second corner.
		:param p11:         Third corner.
		:param p10:         Fourth corner.
		:raises TypeError:  If a given point is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError: If opposite edges have different lengths.
		:raises ValueError: If two consecutive corners are the same point.
		:raises ValueError: If an inner angle isn't 90 |degree|.
		:raises ValueError: If adjacent edges have different lengths.
		"""
		super().__init__(p00, p01, p11, p10)

		edge =     self.segments[0]
		nextEdge = self.segments[1]
		if not isclose(edge.Length, nextEdge.Length):
			ex = ValueError("Line segments (edges) between corners have different lengths.")
			ex.add_note(f"Got lengths {edge.Length} and {nextEdge.Length}.")
			raise ex
