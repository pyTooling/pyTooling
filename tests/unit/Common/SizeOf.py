# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :func:`isnestedclass`.
"""
from unittest           import TestCase

from pytest             import mark

from pyTooling.Common   import getsizeof
from pyTooling.Platform import CurrentPlatform


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ObjectSizes(TestCase):
	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_EmptyClass(self) -> None:
		class C:
			pass

		c = C()

		self.assertLessEqual(getsizeof(c), 360)

	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_ClassWith2DictMembers(self) -> None:
		class C:
			def __init__(self) -> None:
				self._a = 1
				self._b = 2

		c = C()

		self.assertLessEqual(getsizeof(c), 520)

	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_ClassWith2SlotMembers(self) -> None:
		class C:
			__slots__ = ("_a", "_b")

			def __init__(self) -> None:
				self._a = 1
				self._b = 2

		c = C()

		self.assertLessEqual(getsizeof(c), 128)
