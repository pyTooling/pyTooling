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
Unit tests for ...
"""
from unittest            import TestCase

from pyTooling.Cartesian2D import Origin2D, Point2D, Offset2D, LineSegment2D


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Origin(self) -> None:
		origin = Origin2D()

		self.assertEqual(0, origin.x)
		self.assertEqual(0, origin.y)
		self.assertEqual("(0, 0)", str(origin))
		self.assertEqual("Origin2D(0, 0)", repr(origin))

	def test_Point(self) -> None:
		point = Point2D(1, 2)

		self.assertEqual(1, point.x)
		self.assertEqual(2, point.y)
		self.assertEqual("(1, 2)", str(point))
		self.assertEqual("Point2D(1, 2)", repr(point))

	def test_Offset(self) -> None:
		offset = Offset2D(1, 2)

		self.assertEqual(1, offset.xOffset)
		self.assertEqual(2, offset.yOffset)
		self.assertEqual("(1, 2)", str(offset))
		self.assertEqual("Offset2D(1, 2)", repr(offset))


class PointArithmetic(TestCase):
	def test_Point_Plus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		with self.assertRaises(TypeError):
			_ = point1 + point2

	def test_Point_Plus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)

	def test_Point_Plus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		newPoint = point + offset

		self.assertEqual(3, newPoint.x)
		self.assertEqual(5, newPoint.y)

	def test_Point_InplacePlus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)

	def test_Point_InplacePlus_Tuple(self) -> None:
		point = Point2D(1, 2)
		offset = (2, 3)

		point += offset

		self.assertEqual(3, point.x)
		self.assertEqual(5, point.y)

	def test_Point_Minus_Offset(self) -> None:
		point = Point2D(1, 2)
		offset = Offset2D(2, 3)

		newPoint = point + -offset

		self.assertEqual(-1, newPoint.x)
		self.assertEqual(-1, newPoint.y)

	def test_Point_Minus_Point(self) -> None:
		point1 = Point2D(1, 2)
		point2 = Point2D(2, 3)

		offset = point2 - point1

		self.assertEqual(1, offset.xOffset)
		self.assertEqual(1, offset.yOffset)
