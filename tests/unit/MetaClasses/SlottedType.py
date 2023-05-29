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
from unittest              import TestCase

from pyTooling.Common      import getsizeof, CurrentPlatform
from pyTooling.MetaClasses import ExtendedType, BaseClassIsNotAMixinError, BaseClassWithNonEmptySlotsError, \
	BaseClassWithoutSlotsError

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ObjectSizes(TestCase):
	class Normal1:
		_data_0: int

		def __init__(self, data: int):
			self._data_0 = data

	class Normal2(Normal1):
		_data_1: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data_1 = data + 1

	class Extended1(metaclass=ExtendedType):
		_data_0: int

		def __init__(self, data: int):
			self._data_0 = data

	class Extended2(Extended1):
		_data_1: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data_1 = data + 1

	class Slotted1(metaclass=ExtendedType, useSlots=True):
		_data_0: int

		def __init__(self, data: int):
			self._data_0 = data

	class Slotted2(Slotted1):
		_data_1: int

		def __init__(self, data: int):
			super().__init__(data)
			self._data_1 = data + 1

	SIZES = {
		Slotted1: {
			3: {7: 84, 8: 68, 9: 68, 10: 68, 11: 68}
		},
		Slotted2: {
			3: {7: 92, 8: 76, 9: 76, 10: 76, 11: 76}
		}
	}

	def test_SizeOfSlotted1(self):
		data = self.Slotted1(data=5)

		try:
			pv = CurrentPlatform.PythonVersion
			dataSize = getsizeof(data)
			self.assertLessEqual(
				dataSize,
				self.SIZES[self.Slotted1][pv.Major][pv.Minor]
			)
			print(f"\nsize: {dataSize} B")
		except TypeError:
			print(f"\ngetsizeof: not supported on PyPy")

	def test_SizeOfSlotted2(self):
		data = self.Slotted2(data=5)

		try:
			pv = CurrentPlatform.PythonVersion
			dataSize = getsizeof(data)
			self.assertLessEqual(
				dataSize,
				self.SIZES[self.Slotted2][pv.Major][pv.Minor]
			)
			print(f"\nsize: {dataSize} B")
		except TypeError:
			print(f"\ngetsizeof: not supported on PyPy")

	def test_ClassSizes(self):
		print()
		try:
			print(f"size of Normal1:  {getsizeof(self.Normal1)} B")
			print(f"size of Normal2:  {getsizeof(self.Normal2)} B")
			print(f"size of Extended1: {getsizeof(self.Extended1)} B")
			print(f"size of Extended2: {getsizeof(self.Extended2)} B")
			print(f"size of Slotted1:  {getsizeof(self.Slotted1)} B")
			print(f"size of Slotted2:  {getsizeof(self.Slotted2)} B")
		except TypeError:
			print(f"getsizeof: not supported on PyPy")


class AttributeErrors(TestCase):
	class Data0(metaclass=ExtendedType, useSlots=True):
		_int_0: int

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

	def test_UninitializedSlot(self):
		data = self.Data0()
		with self.assertRaises(AttributeError):
			_ = data._int_0

		data._int_0 = 1
		_ = data._int_0


class Inheritance(TestCase):
	def test_LinearInheritance_1_BaseSlotted(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Final(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseSlotted(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Parent(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_2 = data + 2

		inst = Final(1)
		self.assertEqual(1, inst._data_0)
		self.assertEqual(2, inst._data_1)
		self.assertEqual(3, inst._data_2)

	def test_LinearInheritance_1_BaseMixin(self):
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Final(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		# FIXME: why does it fail?
		# TODO: could be an instantiation error (TypeError) when collected slots (mixinSlots) are not set in __slots__
		with self.assertRaises(AttributeError):
			inst = Final(0)
			self.assertEqual(0, inst._data_0)
			self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseMixin(self):
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Parent(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_2 = data + 2

		# FIXME: why does it fail?
		# TODO: could be an instantiation error (TypeError) when collected slots (mixinSlots) are not set in __slots__
		with self.assertRaises(AttributeError):
			inst = Final(1)
			self.assertEqual(1, inst._data_0)
			self.assertEqual(2, inst._data_1)
			self.assertEqual(3, inst._data_2)

	def test_LinearInheritance_1_BaseSlottedMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Final(Base, mixin=False):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseSlottedMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Parent(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent, mixin=False):
			_data_2: int

			def __init__(self, data: int):
				bs = Base.__slots__
				bm = Base.__mixinSlots__
				ps = Parent.__slots__
				pm = Parent.__mixinSlots__
				fs = Final.__slots__
				super().__init__(data)
				self._data_2 = data + 2

		inst = Final(1)
		self.assertEqual(1, inst._data_0)
		self.assertEqual(2, inst._data_1)
		self.assertEqual(3, inst._data_2)

	def test_LinearInheritance_1_BaseMixin_FinalSlotted(self):
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Final(Base, useSlots=True, mixin=False):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseMixin_FinalSlotted(self):
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Parent(Base):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent, useSlots=True, mixin=False):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_2 = data + 2

		inst = Final(1)
		self.assertEqual(1, inst._data_0)
		self.assertEqual(2, inst._data_1)
		self.assertEqual(3, inst._data_2)

	def test_VInheritance_PrimaryExtended(self):
		class Primary(metaclass=ExtendedType, useSlots=True):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary:
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Primary, Secondary):
				_data_1: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_1 = data + 2

			# inst = Final(2)
			# self.assertEqual(2, inst._data_L0)
			# self.assertEqual(3, inst._data_R0)
			# self.assertEqual(4, inst._data_1)

	def test_VInheritance_PrimaryExtended_Mixin(self):
		class Primary(metaclass=ExtendedType, useSlots=True):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, mixin=True):
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		class Final(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		inst = Final(2)
		self.assertEqual(2, inst._data_L0)
		self.assertEqual(3, inst._data_R0)
		self.assertEqual(4, inst._data_1)

	def test_VInheritance_SecondaryExtended(self):
		class Primary:
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, useSlots=True):
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		class Final(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		inst = Final(3)
		self.assertEqual(3, inst._data_L0)
		self.assertEqual(4, inst._data_R0)
		self.assertEqual(5, inst._data_1)

	def test_YInheritance_PrimaryExtended(self):
		class Primary(metaclass=ExtendedType, useSlots=True):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary:
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Merged(Primary, Secondary):
				_data_1: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_1 = data + 2

			# class Final(Merged):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(4)
			# self.assertEqual(4, inst._data_L0)
			# self.assertEqual(5, inst._data_R0)
			# self.assertEqual(6, inst._data_1)
			# self.assertEqual(7, inst._data_2)

	def test_YInheritance_PrimaryExtended_Mixin(self):
		class Primary(metaclass=ExtendedType, useSlots=True):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, mixin=True):
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		class Merged(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		class Final(Merged):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_2 = data + 3

		inst = Final(4)
		self.assertEqual(4, inst._data_L0)
		self.assertEqual(5, inst._data_R0)
		self.assertEqual(6, inst._data_1)
		self.assertEqual(7, inst._data_2)

	def test_YInheritance_SecondaryExtended(self):
		class Primary:
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, useSlots=True):
			_data_R0: int

			def __init__(self, data: int):
				self._data_R0 = data + 1

		class Merged(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		class Final(Merged):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_2 = data + 3

		inst = Final(5)
		self.assertEqual(5, inst._data_L0)
		self.assertEqual(6, inst._data_R0)
		self.assertEqual(7, inst._data_1)
		self.assertEqual(8, inst._data_2)

	def test_OInheritance_BaseExtended(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassIsNotAMixinError):
			class Final(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# inst = Final(6)
			# for m in Final.mro():
			# 	print(m)
			# self.assertEqual(6, inst._data_0)
			# self.assertEqual(7, inst._data_L1)
			# self.assertEqual(8, inst._data_R1)
			# self.assertEqual(9, inst._data_2)

	def test_OInheritance_BaseExtended_PrimaryMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base, mixin=True):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):
			class Final(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# inst = Final(6)
			# for m in Final.mro():
			# 	print(m)
			# self.assertEqual(6, inst._data_0)
			# self.assertEqual(7, inst._data_L1)
			# self.assertEqual(8, inst._data_R1)
			# self.assertEqual(9, inst._data_2)

	def test_OInheritance_BaseExtended_SecondaryMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, mixin=True):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(6)
		for m in Final.mro():
			print(m)
		self.assertEqual(6, inst._data_0)
		self.assertEqual(7, inst._data_L1)
		self.assertEqual(8, inst._data_R1)
		self.assertEqual(9, inst._data_2)

	def test_OInheritance_PrimaryExtended(self):
		class Base:
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Primary(Base, metaclass=ExtendedType, useSlots=True):
				_data_L1: int

				def __init__(self, data: int):
					super().__init__(data)
					self._data_L1 = data + 1

			# class Secondary(Base):
			# 	_data_R1: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		self._data_R1 = data + 2
			#
			# class Final(Primary, Secondary):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		Secondary.__init__(self, data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(7)
			# self.assertEqual(7, inst._data_0)
			# self.assertEqual(8, inst._data_L1)
			# self.assertEqual(9, inst._data_R1)
			# self.assertEqual(10, inst._data_2)

	def test_OInheritance_PrimaryExtended_Slots_Mixin(self):
		class Base:
			_data_0: int
			__slots__ = ("_data_0", )

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base, metaclass=ExtendedType, useSlots=True):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, metaclass=ExtendedType, mixin=True):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(7)
		self.assertEqual(7, inst._data_0)
		self.assertEqual(8, inst._data_L1)
		self.assertEqual(9, inst._data_R1)
		self.assertEqual(10, inst._data_2)

	def test_OInheritance_SecondaryExtended(self):
		class Base:
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Secondary(Base, metaclass=ExtendedType, useSlots=True):
				_data_R1: int

				def __init__(self, data: int):
					super().__init__(data)
					self._data_R1 = data + 2

			# class Final(Primary, Secondary):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		Secondary.__init__(self, data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(8)
			# self.assertEqual(8, inst._data_0)
			# self.assertEqual(9, inst._data_L1)
			# self.assertEqual(10, inst._data_R1)
			# self.assertEqual(11, inst._data_2)

	def test_OInheritance_SecondaryExtended_Slots_Slots(self):
		class Base:
			_data_0: int
			__slots__ = ("_data_0", )

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int
			# __slots__ = ()
			# __mixinSlots__ = ("_data_L1")

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, metaclass=ExtendedType, useSlots=True):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(8)
		self.assertEqual(8, inst._data_0)
		self.assertEqual(9, inst._data_L1)
		self.assertEqual(10, inst._data_R1)
		self.assertEqual(11, inst._data_2)

	def test_OInheritance_MergedExtended(self):
		class Base:
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Primary, Secondary, metaclass=ExtendedType, useSlots=True):
				_data_2: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# inst = Final(9)
			# self.assertEqual(9, inst._data_0)
			# self.assertEqual(10, inst._data_L1)
			# self.assertEqual(11, inst._data_R1)
			# self.assertEqual(12, inst._data_2)

	def test_QInheritance_BaseExtended(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassIsNotAMixinError):
			class Merged(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# class Final(Merged):
			# 	_data_3: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		self._data_3 = data + 4
			#
			# inst = Final(10)
			# self.assertEqual(10, inst._data_0)
			# self.assertEqual(11, inst._data_L1)
			# self.assertEqual(12, inst._data_R1)
			# self.assertEqual(13, inst._data_2)
			# self.assertEqual(14, inst._data_3)

	def test_QInheritance_BaseExtended_PrimaryMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base, mixin=True):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):
			class Merged(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int):
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# class Final(Merged):
			# 	_data_3: int
			#
			# 	def __init__(self, data: int):
			# 		super().__init__(data)
			# 		self._data_3 = data + 4
			#
			# inst = Final(10)
			# self.assertEqual(10, inst._data_0)
			# self.assertEqual(11, inst._data_L1)
			# self.assertEqual(12, inst._data_R1)
			# self.assertEqual(13, inst._data_2)
			# self.assertEqual(14, inst._data_3)

	def test_QInheritance_BaseExtended_SecondaryMixin(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, mixin=True):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		class Merged(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		class Final(Merged):
			_data_3: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_3 = data + 4

		inst = Final(10)
		self.assertEqual(10, inst._data_0)
		self.assertEqual(11, inst._data_L1)
		self.assertEqual(12, inst._data_R1)
		self.assertEqual(13, inst._data_2)
		self.assertEqual(14, inst._data_3)

	def test_QInheritance_FinalExtended(self):
		class Base:
			_data_0: int

			def __init__(self, data: int):
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_R1 = data + 2

		class Merged(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Merged, metaclass=ExtendedType, useSlots=True):
				_data_3: int

				def __init__(self, data: int):
					super().__init__(data)
					self._data_3 = data + 4

			# inst = Final(14)
			# self.assertEqual(14, inst._data_0)
			# self.assertEqual(15, inst._data_L1)
			# self.assertEqual(16, inst._data_R1)
			# self.assertEqual(17, inst._data_2)
			# self.assertEqual(18, inst._data_3)


class Hierarchy(TestCase):
	def test_GraphMLInheritanceHierarchy(self):
		class Base(metaclass=ExtendedType, useSlots=True):
			_data_0: int

			def __init__(self):
				super().__init__()
				self._data_0 = 0

		class WithID(Base):
			_data_1: int

			def __init__(self):
				super().__init__()
				self._data_1 = 1

		class WithData(WithID):
			_data_2: int

			def __init__(self):
				super().__init__()
				self._data_2 = 2

		class Node(WithData):
			_data_3: int

			def __init__(self):
				super().__init__()
				self._data_3 = 3

		class BaseGraph(WithData, mixin=True):
			_data_4: int

			def __init__(self, param: str = None):
				if param is not None:
					super().__init__()

				self._data_4 = 4

			def test_BaseGraph(self):
				self._data_4 = 14

		class SubGraph(Node, BaseGraph):
			_data_5: int

			def __init__(self):
				super().__init__()
				BaseGraph.__init__(self)
				self._data_5 = 5

		sg = SubGraph()
		sg.test_BaseGraph()

	def test_YAMLConfigurationInheritanceHierarchy(self):
		class Node0(metaclass=ExtendedType, useSlots=True):
			_data_0: int

		class Dict0(Node0, mixin=True):
			_data_10: int

		class Config0(Node0, mixin=True):
			_data_11: int

		class Node(Node0, mixin=False):
			_data_2: int

		class Dict(Node, Dict0, mixin=False):
			_data_3: int

		class Config(Dict, Config0):
			_data_4: int

		c = Config()
