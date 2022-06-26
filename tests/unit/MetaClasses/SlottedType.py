# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for class :py:class:`pyTooling.MetaClasses.ExtendedType`.

:copyright: Copyright 2007-2022 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from unittest       import TestCase

from pyTooling.Common import getsizeof
from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Slotted(TestCase):
	def test_Data(self):
		class Data:
			_data: int

		data = Data()

		print()
		print()
		try:
			print(f"size: {getsizeof(data)}")
		except TypeError:
			print(f"size: not supported on PyPy")

	def test_SlottedData(self):
		class SlottedData(metaclass=ExtendedType, useSlots=True):
			_data: int

			def __init__(self, data: int):
				self._data = data

			def raiseError(self):
				self._x = 5

		data = SlottedData(data=5)

		self.assertListEqual(["_data"], list(data.__slots__))
		self.assertEqual(5, data._data)
		with self.assertRaises(AttributeError):
			data.raiseError()
		with self.assertRaises(AttributeError):
			data._y = 2
		with self.assertRaises(AttributeError):
			_ = data._z

		print()
		try:
			print(f"size: {getsizeof(data)}")
		except TypeError:
			print(f"size: not supported on PyPy")

	def test_NonSlottedBaseClass(self):
		class Base:
			_baseData: int

		with self.assertRaises(AttributeError):
			class SlottedData(Base, metaclass=ExtendedType, useSlots=True):
				_data: int

				def __init__(self, data: int):
					self._data = data

				def raiseError(self):
					self._x = 5
