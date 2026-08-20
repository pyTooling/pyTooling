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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Unit tests for the class decorators :deco:`~pyTooling.MetaClasses.slotted`,
:deco:`~pyTooling.MetaClasses.mixin` and :deco:`~pyTooling.MetaClasses.singleton`.
"""
from pyTooling.MetaClasses import ExtendedType, IncompatibleMetaClassError, mixin, singleton, slotted
from pyTooling.MetaClasses import abstractclass, AbstractClassError
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Slotted(Testcase):
	def test_PlainClass(self) -> None:
		@slotted
		class Data:
			_data_0: int

			def __init__(self, data: int) -> None:
				self._data_0 = data

		self.assertTrue(Data.__slotted__)
		self.assertIn("_data_0", Data.__slots__)

		inst = Data(5)

		self.assertEqual(5, inst._data_0)

		with self.assertRaises(AttributeError):
			inst._data_1 = 6


class Mixin(Testcase):
	def test_PlainClass(self) -> None:
		@mixin
		class Mixed:
			_data_M1: int

		self.assertTrue(Mixed.__isMixin__)
		self.assertEqual(tuple(), Mixed.__slots__)
		self.assertIn("_data_M1", Mixed.__mixinSlots__)

	def test_MergedIntoPrimaryInheritanceLine(self) -> None:
		@mixin
		class Mixed:
			_data_M1: int

		class Primary(metaclass=ExtendedType, slots=True):
			_data_L1: int

		class Final(Primary, Mixed, metaclass=ExtendedType, slots=True):
			def __init__(self) -> None:
				self._data_L1 = 1
				self._data_M1 = 2

		inst = Final()

		self.assertEqual(1, inst._data_L1)
		self.assertEqual(2, inst._data_M1)


class Singleton(Testcase):
	def test_PlainClass(self) -> None:
		@singleton
		class App:
			_data_0: int

			def __init__(self) -> None:
				self._data_0 = 5

		self.assertIs(App(), App())


class IncompatibleMetaClass(Testcase):
	"""
	A decorated class must use :class:`type` or a meta-class derived from
	:class:`~pyTooling.MetaClasses.ExtendedType`.
	"""

	class OtherMeta(type):
		pass

	def test_Slotted(self) -> None:
		class Data(metaclass=self.OtherMeta):
			pass

		with self.assertRaises(IncompatibleMetaClassError) as context:
			_ = slotted(Data)

		self.assertIn("'@slotted'", str(context.exception))
		self.assertIn("OtherMeta", context.exception.__notes__[0])

	def test_Mixin(self) -> None:
		class Data(metaclass=self.OtherMeta):
			pass

		with self.assertRaises(IncompatibleMetaClassError) as context:
			_ = mixin(Data)

		self.assertIn("'@mixin'", str(context.exception))

	def test_Singleton(self) -> None:
		class Data(metaclass=self.OtherMeta):
			pass

		with self.assertRaises(IncompatibleMetaClassError) as context:
			_ = singleton(Data)

		self.assertIn("'@singleton'", str(context.exception))


class ClassKeywordArguments(Testcase):
	"""A class keyword the meta-class doesn't know belongs to :meth:`~object.__init_subclass__`, as with :func:`type`."""

	def test_ForwardedToInitSubclass(self) -> None:
		class Base(metaclass=ExtendedType):
			pattern: str

			def __init_subclass__(cls, *args, pattern: str = "", **kwargs) -> None:
				super().__init_subclass__(*args, **kwargs)
				cls.pattern = pattern

		class Derived(Base, pattern="-{0}"):
			pass

		self.assertEqual("-{0}", Derived.pattern)

	def test_ForwardedThroughTwoLevels(self) -> None:
		class Base(metaclass=ExtendedType):
			pattern: str

			def __init_subclass__(cls, *args, pattern: str = "", **kwargs) -> None:
				super().__init_subclass__(*args, **kwargs)
				cls.pattern = pattern

		class Middle(Base, pattern="-{0}"):
			pass

		class Leaf(Middle, pattern="--{0}"):
			pass

		self.assertEqual("-{0}", Middle.pattern)
		self.assertEqual("--{0}", Leaf.pattern)

	def test_CombinedWithAbstractClass(self) -> None:
		@abstractclass
		class Base(metaclass=ExtendedType):
			pattern: str

			def __init_subclass__(cls, *args, pattern: str = "", **kwargs) -> None:
				super().__init_subclass__(*args, **kwargs)
				cls.pattern = pattern

		@abstractclass
		class Middle(Base, pattern="-{0}"):
			pass

		class Leaf(Middle, pattern="--{0}"):
			pass

		with self.assertRaises(AbstractClassError):
			Base()

		with self.assertRaises(AbstractClassError):
			Middle()

		self.assertEqual("--{0}", Leaf().pattern)

	def test_SlotsIsStillAMetaClassOption(self) -> None:
		"""``slots``, ``mixin`` and ``singleton`` stay meta-class options, they aren't forwarded."""
		class Base(metaclass=ExtendedType, slots=True):
			pass

		self.assertTrue(Base.__slotted__)
