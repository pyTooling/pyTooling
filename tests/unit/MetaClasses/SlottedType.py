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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for class :class:`pyTooling.MetaClasses.ExtendedType`.
"""
from typing                import ClassVar, Optional as Nullable

from pytest                import mark

from pyTooling.MetaClasses import ExtendedType, BaseClassIsNotAMixinError, BaseClassWithNonEmptySlotsError, BaseClassWithoutSlotsError
from pyTooling.MetaClasses import DuplicateFieldInSlotsError, UnannotatedFieldWarning
from pyTooling.Decorators  import readonly
from pyTooling.Warning     import WarningCollector
from pyTooling.Common      import getsizeof
from pyTooling.Platform    import CurrentPlatform
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ObjectSizes(Testcase):
	class Normal1:
		_data_0: int

		def __init__(self, data: int) -> None:
			self._data_0 = data

	class Normal2(Normal1):
		_data_1: int

		def __init__(self, data: int) -> None:
			super().__init__(data)
			self._data_1 = data + 1

	class Extended1(metaclass=ExtendedType):
		_data_0: int

		def __init__(self, data: int) -> None:
			self._data_0 = data

	class Extended2(Extended1):
		_data_1: int

		def __init__(self, data: int) -> None:
			super().__init__(data)
			self._data_1 = data + 1

	class Slotted1(metaclass=ExtendedType, slots=True):
		_data_0: int

		def __init__(self, data: int) -> None:
			self._data_0 = data

	class Slotted2(Slotted1):
		_data_1: int

		def __init__(self, data: int) -> None:
			super().__init__(data)
			self._data_1 = data + 1

	SIZES = {
		Slotted1: {
			3: {7: 84, 8: 68, 9: 68, 10: 68, 11: 68, 12: 68, 13: 68, 14: 68}
		},
		Slotted2: {
			3: {7: 92, 8: 76, 9: 76, 10: 76, 11: 76, 12: 76, 13: 76, 14: 76}
		}
	}

	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_SizeOfSlotted1(self) -> None:
		data = self.Slotted1(data=5)

		pv = CurrentPlatform.PythonVersion
		dataSize = getsizeof(data)
		self.assertLessEqual(
			dataSize,
			self.SIZES[self.Slotted1][pv.Major][pv.Minor]
		)
		print(f"\nsize: {dataSize} B")

	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_SizeOfSlotted2(self) -> None:
		data = self.Slotted2(data=5)

		pv = CurrentPlatform.PythonVersion
		dataSize = getsizeof(data)
		self.assertLessEqual(
			dataSize,
			self.SIZES[self.Slotted2][pv.Major][pv.Minor]
		)
		print(f"\nsize: {dataSize} B")

	@mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
	def test_ClassSizes(self) -> None:
		print()
		print(f"size of Normal1:  {getsizeof(self.Normal1)} B")
		print(f"size of Normal2:  {getsizeof(self.Normal2)} B")
		print(f"size of Extended1: {getsizeof(self.Extended1)} B")
		print(f"size of Extended2: {getsizeof(self.Extended2)} B")
		print(f"size of Slotted1:  {getsizeof(self.Slotted1)} B")
		print(f"size of Slotted2:  {getsizeof(self.Slotted2)} B")


class AttributeErrors(Testcase):
	class Data0(metaclass=ExtendedType, slots=True):
		_int_0: int

	class Data1(metaclass=ExtendedType, slots=True):
		_int_1: int

		def __init__(self) -> None:
			self._int_1 = 1

		def method_11(self):
			self._str_1 = "foo"

		def method_12(self):
			_ = self._int_0

	class Data2(Data1):  #, slots=True):
		_int_2: int

		def __init__(self) -> None:
			super().__init__()
			self._int_2 = 2

		def method_21(self):
			self._str_2 = "bar"

		def method_22(self):
			_ = self._int_0

	def test_NormalField_1(self) -> None:
		data = self.Data1()
		self.assertEqual(1, data._int_1)

	def test_AddNewFieldInMethod_1(self) -> None:
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data.method_11()

	def test_AddNewFieldByCode_1(self) -> None:
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data._float1 = 3.4

	def test_NormalField_2(self) -> None:
		data = self.Data2()
		self.assertEqual(1, data._int_1)
		self.assertEqual(2, data._int_2)

	def test_AddNewFieldInMethod_2(self) -> None:
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data.method_21()

	def test_AddNewFieldByCode_2(self) -> None:
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data._float2 = 4.3

	def test_ReadNonExistingFieldInMethod_1(self) -> None:
		data = self.Data1()
		with self.assertRaises(AttributeError):
			data.method_12()

	def test_ReadNonExistingFieldInMethod_2(self) -> None:
		data = self.Data2()
		with self.assertRaises(AttributeError):
			data.method_22()

	def test_ReadNonExistingFieldByCode_1(self) -> None:
		data = self.Data1()
		with self.assertRaises(AttributeError):
			_ = data._int_0

	def test_ReadNonExistingFieldByCode_2(self) -> None:
		data = self.Data2()
		with self.assertRaises(AttributeError):
			_ = data._int_0

	def test_UninitializedSlot(self) -> None:
		data = self.Data0()
		with self.assertRaises(AttributeError):
			_ = data._int_0

		data._int_0 = 1
		_ = data._int_0


class Inheritance(Testcase):
	def test_LinearInheritance_1_BaseSlotted(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Final(Base):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseSlotted(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Parent(Base):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_2 = data + 2

		inst = Final(1)
		self.assertEqual(1, inst._data_0)
		self.assertEqual(2, inst._data_1)
		self.assertEqual(3, inst._data_2)

	def test_LinearInheritance_1_BaseMixin(self) -> None:
		print()

		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Final(Base, mixin=True):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		# FIXME: why does it fail?
		# TODO: could be an instantiation error (TypeError) when collected slots (mixinSlots) are not set in __slots__
		with self.assertRaises(AttributeError):
			inst = Final(0)
			self.assertEqual(0, inst._data_0)
			self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseMixin(self) -> None:
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Parent(Base, mixin=True):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent, mixin=True):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_2 = data + 2

		# FIXME: why does it fail?
		# TODO: could be an instantiation error (TypeError) when collected slots (mixinSlots) are not set in __slots__
		with self.assertRaises(AttributeError):
			inst = Final(1)
			self.assertEqual(1, inst._data_0)
			self.assertEqual(2, inst._data_1)
			self.assertEqual(3, inst._data_2)

	def test_LinearInheritance_1_BaseSlottedMixin(self) -> None:
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Final(Base):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseSlottedMixin(self) -> None:
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Parent(Base, mixin=True):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent):
			_data_2: int

			def __init__(self, data: int) -> None:
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

	def test_LinearInheritance_1_BaseMixin_FinalSlotted(self) -> None:
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Final(Base):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		inst = Final(0)
		self.assertEqual(0, inst._data_0)
		self.assertEqual(1, inst._data_1)

	def test_LinearInheritance_2_BaseMixin_FinalSlotted(self) -> None:
		class Base(metaclass=ExtendedType, mixin=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Parent(Base, mixin=True):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_1 = data + 1

		class Final(Parent):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_2 = data + 2

		inst = Final(1)
		self.assertEqual(1, inst._data_0)
		self.assertEqual(2, inst._data_1)
		self.assertEqual(3, inst._data_2)

	def test_VInheritance_PrimaryExtended(self) -> None:
		class Primary(metaclass=ExtendedType, slots=True):
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary:
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Primary, Secondary):
				_data_1: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_1 = data + 2

			# inst = Final(2)
			# self.assertEqual(2, inst._data_L0)
			# self.assertEqual(3, inst._data_R0)
			# self.assertEqual(4, inst._data_1)

	def test_VInheritance_PrimaryExtended_Mixin(self) -> None:
		class Primary(metaclass=ExtendedType, slots=True):
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, mixin=True):
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		class Final(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		inst = Final(2)
		self.assertEqual(2, inst._data_L0)
		self.assertEqual(3, inst._data_R0)
		self.assertEqual(4, inst._data_1)

	def test_VInheritance_SecondaryExtended(self) -> None:
		class Primary:
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, slots=True):
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		class Final(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		inst = Final(3)
		self.assertEqual(3, inst._data_L0)
		self.assertEqual(4, inst._data_R0)
		self.assertEqual(5, inst._data_1)

	def test_YInheritance_PrimaryExtended(self) -> None:
		class Primary(metaclass=ExtendedType, slots=True):
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary:
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Merged(Primary, Secondary):
				_data_1: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_1 = data + 2

			# class Final(Merged):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(4)
			# self.assertEqual(4, inst._data_L0)
			# self.assertEqual(5, inst._data_R0)
			# self.assertEqual(6, inst._data_1)
			# self.assertEqual(7, inst._data_2)

	def test_YInheritance_PrimaryExtended_Mixin(self) -> None:
		class Primary(metaclass=ExtendedType, slots=True):
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, mixin=True):
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		class Merged(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		class Final(Merged):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_2 = data + 3

		inst = Final(4)
		self.assertEqual(4, inst._data_L0)
		self.assertEqual(5, inst._data_R0)
		self.assertEqual(6, inst._data_1)
		self.assertEqual(7, inst._data_2)

	def test_YInheritance_SecondaryExtended(self) -> None:
		class Primary:
			_data_L0: int

			def __init__(self, data: int) -> None:
				self._data_L0 = data

		class Secondary(metaclass=ExtendedType, slots=True):
			_data_R0: int

			def __init__(self, data: int) -> None:
				self._data_R0 = data + 1

		class Merged(Primary, Secondary):
			_data_1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_1 = data + 2

		class Final(Merged):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_2 = data + 3

		inst = Final(5)
		self.assertEqual(5, inst._data_L0)
		self.assertEqual(6, inst._data_R0)
		self.assertEqual(7, inst._data_1)
		self.assertEqual(8, inst._data_2)

	def test_OInheritance_BaseExtended(self) -> None:
		print()

		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):  #BaseClassIsNotAMixinError):
			class Final(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int) -> None:
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

	def test_OInheritance_BaseExtended_PrimaryMixin(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base, mixin=True):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):
			class Final(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int) -> None:
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

	def test_OInheritance_BaseExtended_SecondaryMixin(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, mixin=True):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int) -> None:
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

	def test_OInheritance_PrimaryExtended(self) -> None:
		class Base:
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Primary(Base, metaclass=ExtendedType, slots=True):
				_data_L1: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					self._data_L1 = data + 1

			# class Secondary(Base):
			# 	_data_R1: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		self._data_R1 = data + 2
			#
			# class Final(Primary, Secondary):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		Secondary.__init__(self, data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(7)
			# self.assertEqual(7, inst._data_0)
			# self.assertEqual(8, inst._data_L1)
			# self.assertEqual(9, inst._data_R1)
			# self.assertEqual(10, inst._data_2)

	def test_OInheritance_PrimaryExtended_Slots_Mixin(self) -> None:
		class Base:
			_data_0: int
			__slots__ = ("_data_0", )

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base, metaclass=ExtendedType, slots=True):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, metaclass=ExtendedType, mixin=True):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(7)
		self.assertEqual(7, inst._data_0)
		self.assertEqual(8, inst._data_L1)
		self.assertEqual(9, inst._data_R1)
		self.assertEqual(10, inst._data_2)

	def test_OInheritance_SecondaryExtended(self) -> None:
		class Base:
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Secondary(Base, metaclass=ExtendedType, slots=True):
				_data_R1: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					self._data_R1 = data + 2

			# class Final(Primary, Secondary):
			# 	_data_2: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		Secondary.__init__(self, data)
			# 		self._data_2 = data + 3
			#
			# inst = Final(8)
			# self.assertEqual(8, inst._data_0)
			# self.assertEqual(9, inst._data_L1)
			# self.assertEqual(10, inst._data_R1)
			# self.assertEqual(11, inst._data_2)

	def test_OInheritance_SecondaryExtended_Slots_Slots(self) -> None:
		class Base:
			_data_0: int
			__slots__ = ("_data_0", )

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int
			# __slots__ = ()
			# __mixinSlots__ = ("_data_L1")

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, metaclass=ExtendedType, slots=True):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		class Final(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(8)
		self.assertEqual(8, inst._data_0)
		self.assertEqual(9, inst._data_L1)
		self.assertEqual(10, inst._data_R1)
		self.assertEqual(11, inst._data_2)

	def test_OInheritance_MergedExtended(self) -> None:
		class Base:
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Primary, Secondary, metaclass=ExtendedType, slots=True):
				_data_2: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# inst = Final(9)
			# self.assertEqual(9, inst._data_0)
			# self.assertEqual(10, inst._data_L1)
			# self.assertEqual(11, inst._data_R1)
			# self.assertEqual(12, inst._data_2)

	def test_QInheritance_BaseExtended(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):  #BaseClassIsNotAMixinError):
			class Merged(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# class Final(Merged):
			# 	_data_3: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		self._data_3 = data + 4
			#
			# inst = Final(10)
			# self.assertEqual(10, inst._data_0)
			# self.assertEqual(11, inst._data_L1)
			# self.assertEqual(12, inst._data_R1)
			# self.assertEqual(13, inst._data_2)
			# self.assertEqual(14, inst._data_3)

	def test_QInheritance_BaseExtended_PrimaryMixin(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base, mixin=True):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		with self.assertRaises(BaseClassWithNonEmptySlotsError):
			class Merged(Primary, Secondary):
				_data_2: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					Secondary.__init__(self, data)
					self._data_2 = data + 3

			# class Final(Merged):
			# 	_data_3: int
			#
			# 	def __init__(self, data: int) -> None:
			# 		super().__init__(data)
			# 		self._data_3 = data + 4
			#
			# inst = Final(10)
			# self.assertEqual(10, inst._data_0)
			# self.assertEqual(11, inst._data_L1)
			# self.assertEqual(12, inst._data_R1)
			# self.assertEqual(13, inst._data_2)
			# self.assertEqual(14, inst._data_3)

	def test_QInheritance_BaseExtended_SecondaryMixin(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base, mixin=True):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		class Merged(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		class Final(Merged):
			_data_3: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_3 = data + 4

		inst = Final(10)
		self.assertEqual(10, inst._data_0)
		self.assertEqual(11, inst._data_L1)
		self.assertEqual(12, inst._data_R1)
		self.assertEqual(13, inst._data_2)
		self.assertEqual(14, inst._data_3)

	def test_QInheritance_FinalExtended(self) -> None:
		class Base:
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		class Primary(Base):
			_data_L1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
			_data_R1: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				self._data_R1 = data + 2

		class Merged(Primary, Secondary):
			_data_2: int

			def __init__(self, data: int) -> None:
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		with self.assertRaises(BaseClassWithoutSlotsError):
			class Final(Merged, metaclass=ExtendedType, slots=True):
				_data_3: int

				def __init__(self, data: int) -> None:
					super().__init__(data)
					self._data_3 = data + 4

			# inst = Final(14)
			# self.assertEqual(14, inst._data_0)
			# self.assertEqual(15, inst._data_L1)
			# self.assertEqual(16, inst._data_R1)
			# self.assertEqual(17, inst._data_2)
			# self.assertEqual(18, inst._data_3)


class NonEmptySlotsOnSecondaryBaseClass(Testcase):
	"""
	Only the primary inheritance line may use non-empty ``__slots__``. Secondary base-classes must be mixin-classes,
	otherwise Python reports an instance lay-out conflict.
	"""

	def test_PlainClassWithNonEmptySlots(self) -> None:
		"""A secondary base-class not built by ExtendedType is checked as well."""
		class Plain:
			__slots__ = ("_data_R1", )

		class Primary(metaclass=ExtendedType, slots=True):
			_data_L1: int

		with self.assertRaises(BaseClassWithNonEmptySlotsError) as context:
			class Final(Primary, Plain, metaclass=ExtendedType, slots=True):
				_data_2: int

		self.assertIn("Plain", str(context.exception))

	def test_IndirectlyInheritedNonEmptySlots(self) -> None:
		"""A mixin-class may not drag in a non-mixin base-class using non-empty slots."""
		class Plain:
			__slots__ = ("_data_R1", )

		class Mixin(Plain, metaclass=ExtendedType, mixin=True):
			_data_M1: int

		class Primary(metaclass=ExtendedType, slots=True):
			_data_L1: int

		with self.assertRaises(BaseClassWithNonEmptySlotsError) as context:
			class Final(Primary, Mixin, metaclass=ExtendedType, slots=True):
				_data_2: int

		self.assertIn("Plain", str(context.exception))

	def test_ProperMixinIsAccepted(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True):
			_data_M1: int

		class Primary(metaclass=ExtendedType, slots=True):
			_data_L1: int

		class Final(Primary, Mixin, metaclass=ExtendedType, slots=True):
			_data_2: int

			def __init__(self) -> None:
				self._data_L1 = 1
				self._data_M1 = 2
				self._data_2 = 3

		inst = Final()

		self.assertEqual(1, inst._data_L1)
		self.assertEqual(2, inst._data_M1)
		self.assertEqual(3, inst._data_2)


class SlotShadowedByClassMember(Testcase):
	"""
	A class member assigned without a type annotation stays a class attribute. If it carries the name of a slot, it
	shadows the slot's descriptor and the field becomes read-only on instances - which used to surface much later as a
	bare ``AttributeError: ... is read-only`` on the first assignment.
	"""

	def test_ShadowedInheritedSlot(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self) -> None:
				self._data_0 = 1

		with self.assertRaises(DuplicateFieldInSlotsError) as context:
			class Derived(Base):
				_data_0 = 5

		self.assertIn("_data_0", str(context.exception))
		self.assertIn("Slot '_data_0' is declared in base-class", context.exception.__notes__[0])

	def test_ShadowedMixinSlot(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True):
			_data_M1: int

		class Primary(metaclass=ExtendedType, slots=True):
			_data_L1: int

		with self.assertRaises(DuplicateFieldInSlotsError) as context:
			class Final(Primary, Mixin, metaclass=ExtendedType, slots=True):
				_data_M1 = 5

		self.assertIn("Slot '_data_M1' is contributed by a mixin-class", context.exception.__notes__[0])
		self.assertIn("Python doesn't allow a name to be listed in '__slots__'", context.exception.__notes__[1])

	def test_ClassVariableIsNotShadowing(self) -> None:
		"""Annotating the assignment as a ClassVar is the documented way out."""
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: ClassVar[int]

		class Derived(Base):
			_data_0: ClassVar[int] = 5

		self.assertEqual(5, Derived._data_0)
		self.assertEqual(5, Derived()._data_0)

	def test_UnrelatedClassConstantIsAccepted(self) -> None:
		"""An un-annotated assignment that doesn't collide with a slot stays a plain class attribute."""
		class Base(metaclass=ExtendedType, slots=True):
			LIMIT = 100
			_data_0: int

			def __init__(self) -> None:
				self._data_0 = self.LIMIT

		inst = Base()

		self.assertEqual(100, Base.LIMIT)
		self.assertEqual(100, inst._data_0)


class UnannotatedFields(Testcase):
	"""
	Every field should carry type information. A field assigned in the class body without a type annotation is reported
	as a warning - it needs a :class:`WarningCollector` to be observed, so importing such a module doesn't fail.
	"""

	def _collect(self, construct) -> list:
		warnings = []
		with WarningCollector(handler=lambda warning: warnings.append(warning) or False):
			construct()

		return [warning for warning in warnings if isinstance(warning, UnannotatedFieldWarning)]

	def test_UnannotatedClassConstant(self) -> None:
		def construct() -> None:
			class Base(metaclass=ExtendedType, slots=True):
				LIMIT = 100
				_data_0: int

		warnings = self._collect(construct)

		self.assertEqual(1, len(warnings))
		self.assertIn("Class 'Base' declares 1 field(s) without a type annotation.", str(warnings[0]))
		self.assertIn("'LIMIT'", warnings[0].__notes__[0])

	def test_UnannotatedFieldWithoutSlots(self) -> None:
		"""The check doesn't depend on slots - it's about type information, not about the slot machinery."""
		def construct() -> None:
			class Base(metaclass=ExtendedType):
				LIMIT = 100

		self.assertEqual(1, len(self._collect(construct)))

	def test_ClassVarIsAnnotated(self) -> None:
		def construct() -> None:
			class Base(metaclass=ExtendedType, slots=True):
				LIMIT: ClassVar[int] = 100
				_data_0: int

		self.assertEqual(0, len(self._collect(construct)))

	def test_MethodsAndNestedClassesAreNoFields(self) -> None:
		def construct() -> None:
			class Base(metaclass=ExtendedType, slots=True):
				_data_0: int

				class Nested:
					pass

				def Method(self) -> None:
					pass

				@classmethod
				def ClassMethod(cls) -> None:
					pass

				@staticmethod
				def StaticMethod() -> None:
					pass

				@property
				def Property(self) -> int:
					return self._data_0

				@readonly
				def ReadOnly(self) -> int:
					return self._data_0

		self.assertEqual(0, len(self._collect(construct)))

	def test_MultipleUnannotatedFields(self) -> None:
		def construct() -> None:
			class Base(metaclass=ExtendedType, slots=True):
				LIMIT = 100
				NAME = "base"
				_data_0: int

		warnings = self._collect(construct)

		self.assertEqual(1, len(warnings))
		self.assertIn("declares 2 field(s)", str(warnings[0]))
		self.assertIn("'LIMIT', 'NAME'", warnings[0].__notes__[0])


class Hierarchy(Testcase):
	def test_GraphMLInheritanceHierarchy(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data_0: int

			def __init__(self) -> None:
				super().__init__()
				self._data_0 = 0

		class WithID(Base):
			_data_1: int

			def __init__(self) -> None:
				super().__init__()
				self._data_1 = 1

		class WithData(WithID):
			_data_2: int

			def __init__(self) -> None:
				super().__init__()
				self._data_2 = 2

		class Node(WithData):
			_data_3: int

			def __init__(self) -> None:
				super().__init__()
				self._data_3 = 3

		class BaseGraph(WithData, mixin=True):
			_data_4: int

			def __init__(self, param: Nullable[str] = None) -> None:
				if param is not None:
					super().__init__()

				self._data_4 = 4

			def test_BaseGraph(self) -> None:
				self._data_4 = 14

		class SubGraph(Node, BaseGraph):
			_data_5: int

			def __init__(self) -> None:
				super().__init__()
				BaseGraph.__init__(self)
				self._data_5 = 5

		sg = SubGraph()
		sg.test_BaseGraph()

	def test_YAMLConfigurationInheritanceHierarchy(self) -> None:
		class Node0(metaclass=ExtendedType, slots=True):
			_data_0: int

		class Dict0(Node0, mixin=True):
			_data_10: int

		class Config0(Node0, mixin=True):
			_data_11: int

		class Node(Node0):
			_data_2: int

		class Dict(Node, Dict0):
			_data_3: int

		class Config(Dict, Config0):
			_data_4: int

		c = Config()
