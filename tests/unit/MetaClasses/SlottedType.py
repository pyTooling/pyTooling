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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
from unittest       import TestCase

from pyTooling.Common import getsizeof, CurrentPlatform, Platform
from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Slotted(TestCase):
	class Data1(metaclass=ExtendedType, useSlots=True):
		_data1: int

		def __init__(self, data: int):
			self._data1 = data

	class Data2(Data1):  #, useSlots=True):
		_data2: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data2 = data + 1

	SIZES = {
		Data1: {
			3: {7: 84, 8: 68, 9: 68, 10: 68, 11: 68}
		},
		Data2: {
			3: {7: 92, 8: 76, 9: 76, 10: 76, 11: 76}
		}
	}

	def test_Slots1(self):
		data = self.Data1(data=5)

		self.assertListEqual(["_data1"], list(data.__slots__))
		self.assertEqual(5, data._data1)
		data._data1 = 6
		self.assertEqual(6, data._data1)

		try:
			pv = CurrentPlatform.PythonVersion
			self.assertLessEqual(
				getsizeof(data),
				self.SIZES[self.Data1][pv.Major][pv.Minor]
			)
		except TypeError:
			print(f"getsizeof: not supported on PyPy")

		print()
		try:
			print(f"size: {getsizeof(data)}")
		except TypeError:
			print(f"size: not supported on PyPy")

	def test_Slots2(self):
		data = self.Data2(data=10)

		self.assertListEqual(["_data2"], list(data.__slots__))
		self.assertEqual(10, data._data1)
		data._data1 = 12
		self.assertEqual(12, data._data1)

		try:
			pv = CurrentPlatform.PythonVersion
			self.assertLessEqual(
				getsizeof(data),
				self.SIZES[self.Data2][pv.Major][pv.Minor]
			)
		except TypeError:
			print(f"getsizeof: not supported on PyPy")

		print()
		try:
			print(f"getsizeof: {getsizeof(data)}")
		except TypeError:
			print(f"getsizeof: not supported on PyPy")


class AttributeErrors(TestCase):
	class Data1(metaclass=ExtendedType, useSlots=True):
		_int_1: int

		def __init__(self):
			self._int_1 = 1

		def method_11(self):
			self._str_1 = "foo"

		def method_12(self):
			_ = self._int_0

	class Data2(Data1):  #, useSlots=True):
		_int_2: int

		def __init__(self):
			super().__init__()
			self._int_2 = 2

		def method_21(self):
			self._str_2 = "bar"

		def method_22(self):
			_ = self._int_0

	def test_NormalField_1(self):
		data = self.Data1()
		self.assertEqual(1, data._int_1)

	def test_AddNewFieldInMethod_1(self):
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data.method_11()

	def test_AddNewFieldByCode_1(self):
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data._float1 = 3.4

	def test_NormalField_2(self):
		data = self.Data2()
		self.assertEqual(1, data._int_1)
		self.assertEqual(2, data._int_2)

	def test_AddNewFieldInMethod_2(self):
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data.method_21()

	def test_AddNewFieldByCode_2(self):
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data._float2 = 4.3

	def test_ReadNonExistingFieldInMethod_1(self):
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data.method_12()

	def test_ReadNonExistingFieldInMethod_2(self):
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data.method_22()

	def test_ReadNonExistingFieldByCode_1(self):
		data = self.Data1()
		with self.assertRaises(AttributeError):
			_ = data._int_0

	def test_ReadNonExistingFieldByCode_2(self):
		data = self.Data2()
		with self.assertRaises(AttributeError):
			_ = data._int_0


	def test_NonSlottedBaseClass(self):
		class Base:
			_baseData: int

		with self.assertRaises(AttributeError):
			class SlottedData(Base, metaclass=ExtendedType, useSlots=True):
				_data: int


class ObjectSizes(TestCase):
	class Normal1:
		_data1: int

		def __init__(self, data: int):
			self._data1 = data

	class Normal2(Normal1):
		_data2: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data2 = data + 1

	class Extended1(metaclass=ExtendedType):
		_data1: int

		def __init__(self, data: int):
			self._data1 = data

	class Extended2(Extended1):
		_data2: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data2 = data + 1

	class Slotted1(metaclass=ExtendedType, useSlots=True):
		_data1: int

		def __init__(self, data: int):
			self._data1 = data

	class Slotted2(Slotted1):  #, useSlots=True):
		_data2: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data2 = data + 1

	def test_NormalType(self):
		data1 = self.Normal1(10)
		data2 = self.Normal2(15)

		print()
		try:
			print(f"size of Normal1: {getsizeof(data1)}")
			print(f"size of Normal2: {getsizeof(data2)}")
		except TypeError:
			print(f"getsizeof: not supported on PyPy")

	def test_ExtendedType(self):
		data1 = self.Extended1(20)
		data2 = self.Extended2(25)

		print()
		try:
			print(f"size of Extended1: {getsizeof(data1)}")
			print(f"size of Extended2: {getsizeof(data2)}")
		except TypeError:
			print(f"getsizeof: not supported on PyPy")

	def test_SlottedType(self):
		data1 = self.Slotted1(30)
		data2 = self.Slotted2(35)

		print()
		try:
			print(f"size of Slotted1: {getsizeof(data1)}")
			print(f"size of Slotted2: {getsizeof(data2)}")
		except TypeError:
			print(f"getsizeof: not supported on PyPy")
