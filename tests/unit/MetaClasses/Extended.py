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

from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Normal(TestCase):
	def test_LinearInheritance_1(self):
		class Base(metaclass=ExtendedType):
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

	def test_LinearInheritance_2(self):
		class Base(metaclass=ExtendedType):
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

	def test_VInheritance_PrimaryExtended(self):
		class Primary(metaclass=ExtendedType):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary:
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

		class Secondary(metaclass=ExtendedType):
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
		class Primary(metaclass=ExtendedType):
			_data_L0: int

			def __init__(self, data: int):
				self._data_L0 = data

		class Secondary:
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

		class Secondary(metaclass=ExtendedType):
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
		class Base(metaclass=ExtendedType):
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

		class Primary(Base, metaclass=ExtendedType):
			_data_L1: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_L1 = data + 1

		class Secondary(Base):
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

		class Secondary(Base, metaclass=ExtendedType):
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

		class Final(Primary, Secondary, metaclass=ExtendedType):
			_data_2: int

			def __init__(self, data: int):
				super().__init__(data)
				Secondary.__init__(self, data)
				self._data_2 = data + 3

		inst = Final(9)
		self.assertEqual(9, inst._data_0)
		self.assertEqual(10, inst._data_L1)
		self.assertEqual(11, inst._data_R1)
		self.assertEqual(12, inst._data_2)

	def test_QInheritance_BaseExtended(self):
		class Base(metaclass=ExtendedType):
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

		class Final(Merged, metaclass=ExtendedType):
			_data_3: int

			def __init__(self, data: int):
				super().__init__(data)
				self._data_3 = data + 4

		inst = Final(14)
		self.assertEqual(14, inst._data_0)
		self.assertEqual(15, inst._data_L1)
		self.assertEqual(16, inst._data_R1)
		self.assertEqual(17, inst._data_2)
		self.assertEqual(18, inst._data_3)
