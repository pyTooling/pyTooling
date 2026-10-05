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
Unit tests for object fields handled by :class:`pyTooling.MetaClasses.ExtendedType`, with and without slots.
"""
from types                 import MemberDescriptorType

from pyTooling.MetaClasses import ExtendedType
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class WithoutSlots(Testcase):
	def test_NoInitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

		with self.assertRaises(AttributeError, msg="Field '_data0' should not exist on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

		inst = Base()

		with self.assertRaises(AttributeError, msg="Field '_data0' shouldn't be initialized on instance."):
			_ = inst._data0

		inst._data0 = 1
		self.assertEqual(1, inst._data0)

	def test_NoInitValue_DunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		with self.assertRaises(AttributeError, msg="Field '_data0' should not exist on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

			def __init__(self) -> None:
				pass

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_InitOverwrite_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

			def __init__(self) -> None:
				self._data0 = 5

		inst = Base()

		self.assertEqual(5, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)


class WithSlots(Testcase):
	def test_NoInitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int

		inst = Base()

		with self.assertRaises(AttributeError, msg="Field '_data0' shouldn't be initialized on instance."):
			_ = inst._data0

		inst._data0 = 1
		self.assertEqual(1, inst._data0)

	def test_NoInitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_InitOverwrite_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1

			def __init__(self) -> None:
				self._data0 = 5

		inst = Base()

		self.assertEqual(5, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1

		self.assertEqual(1, Base()._data0)
		self.assertIsInstance(Base.__dict__["_data0"], MemberDescriptorType, "The class keeps the slot, not the value.")

	def test_InitValue_DunderInit_InstCheck(self) -> None:
		"""The initial value is assigned before the class' own __init__ runs, which can read it."""
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1
			_data1: int

			def __init__(self, offset: int) -> None:
				self._data1 = self._data0 + offset

		inst = Base(10)

		self.assertEqual(1, inst._data0)
		self.assertEqual(11, inst._data1)

	def test_InitValue_Derived(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1

		class Derived(Base):
			_data1: int = 2

			def __init__(self) -> None:
				super().__init__()

		inst = Derived()

		self.assertEqual(1, inst._data0)
		self.assertEqual(2, inst._data1)
		self.assertDictEqual({"_data1": 2}, Derived.__slotDefaults__)

	def test_InitValue_AssignedBeforeSuper(self) -> None:
		"""A field assigned before the base-class' __init__ runs keeps its value."""
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1

			def __init__(self) -> None:
				pass

		class Derived(Base):
			def __init__(self) -> None:
				self._data0 = 5
				super().__init__()

		self.assertEqual(5, Derived()._data0)

	def test_InitValue_Mixin(self) -> None:
		"""The class a mixin-class is mixed into assigns the mixin-class' initial values, also without calling it."""
		class Mixin(metaclass=ExtendedType, mixin=True):
			_name: str = "unnamed"

		class Primary(metaclass=ExtendedType, slots=True):
			_data0: int = 1

		class Final(Primary, Mixin):
			pass

		inst = Final()

		self.assertEqual(1, inst._data0)
		self.assertEqual("unnamed", inst._name)

	def test_InitValue_MixinInitKeepsValue(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True):
			_name: str = "unnamed"

			def __init__(self, name: str) -> None:
				self._name = name

		class Primary(metaclass=ExtendedType, slots=True):
			_data0: int = 1

		class Final(Primary, Mixin):
			def __init__(self, name: str) -> None:
				super().__init__()
				Mixin.__init__(self, name)

		self.assertEqual("named", Final("named")._name)

	def test_InitValue_Shared(self) -> None:
		"""The initial value is assigned, not copied."""
		class Base(metaclass=ExtendedType, slots=True):
			_items: list = []

		self.assertIs(Base()._items, Base()._items)

	def test_InitValue_Singleton(self) -> None:
		class Single(metaclass=ExtendedType, slots=True, singleton=True):
			_data0: int = 1

			def __init__(self) -> None:
				self._data0 += 1

		self.assertEqual(2, Single()._data0)
		self.assertEqual(2, Single()._data0, "The singleton is initialized once.")

	def test_InitValue_Pickle(self) -> None:
		from pickle import dumps, loads

		inst = _Pickled()
		inst._data0 = 7
		copy = loads(dumps(inst))

		self.assertEqual(7, copy._data0)
		self.assertEqual("x", copy._data1)

	def test_ClassVariable(self) -> None:
		"""A ClassVar keeps its initial value on the class."""
		from typing import ClassVar

		class Base(metaclass=ExtendedType, slots=True):
			_count: ClassVar[int] = 3

		self.assertEqual(3, Base._count)
		self.assertNotIn("_count", Base.__slots__)
		self.assertDictEqual({}, Base.__slotDefaults__)


class _Pickled(metaclass=ExtendedType, slots=True):
	"""A module-level slotted class with initial values, so pickle can find it."""

	_data0: int = 1
	_data1: str = "x"

