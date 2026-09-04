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
Unit tests for class variables handled by :class:`pyTooling.MetaClasses.ExtendedType`, with and without
slots, and through inheritance.
"""
from typing                import ClassVar

from pyTooling.MetaClasses import ExtendedType, DuplicateFieldInSlotsError
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class WithoutSlots(Testcase):
	def test_NoInitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: ClassVar[int]

		with self.assertRaises(AttributeError, msg="Class field '_data0' shouldn't be initialized on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: ClassVar[int]

		inst = Base()

		with self.assertRaises(AttributeError, msg="Field '_data0' should not exist on instance."):
			_ = inst._data0

	def test_InitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: ClassVar[int] = 1

		self.assertEqual(1, Base._data0)

	def test_InitValue_DunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: ClassVar[int] = 1

			def __init__(self) -> None:
				pass

		self.assertEqual(1, Base._data0)


class WithSlots(Testcase):
	def test_NoInitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int]

		self.assertNotIn("_data0", Base.__slots__, "Class field '_data0' shouldn't become a slot on class 'Base'.")

		with self.assertRaises(AttributeError, msg="Class field '_data0' shouldn't be initialized on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_DerivedAssigned_ClassCheck(self) -> None:
		"""
		A ``ClassVar`` without an initial value is a forward declaration: derived classes assign the value.

		If the base turned it into a slot, the derived class' assignment would shadow the slot descriptor and
		make the field read-only on instances.
		"""
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int]
			_data1: ClassVar[int] = 1

		class Derived(Base):
			_data0: ClassVar[int] = 2
			_data1: ClassVar[int] = 3

		self.assertEqual(1, Base._data1)
		self.assertEqual(2, Derived._data0)
		self.assertEqual(3, Derived._data1)

		derived = Derived()

		self.assertEqual(2, derived._data0)
		self.assertEqual(3, derived._data1)

	def test_InitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1

		self.assertEqual(1, Base._data0)

	def test_InitValue_DunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1

			def __init__(self) -> None:
				pass

		self.assertEqual(1, Base._data0)

	def test_InitValue_InitOverwrite_InstantiationCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1

			def __init__(self) -> None:
				self._data0 = 5

		with self.assertRaises(AttributeError, msg="Class field '_data0' should not be accessible from within instance."):
			_ = Base()

	def test_InitValue_InitReadValue_InstantiationCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1
			_data1: int

			def __init__(self) -> None:
				self._data1 = self._data0 + 5

		self.assertEqual(1, Base._data0)

		inst = Base()

		self.assertEqual(6, inst._data1)


class Inheritance_WithSlots(Testcase):
	def test_BaseAssigned(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1

		class Parent(Base):
			pass

		self.assertEqual(1, Base._data0)
		self.assertEqual(1, Parent._data0)

		base = Base()

		self.assertEqual(1, base._data0)

		parent = Parent()

		self.assertEqual(1, parent._data0)

	def test_BaseAssigned_ParentAssigned(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: ClassVar[int] = 1

		class Parent(Base):
			_data0: ClassVar[int] = 2

		self.assertEqual(1, Base._data0)
		self.assertEqual(2, Parent._data0)

		base = Base()

		self.assertEqual(1, base._data0)

		parent = Parent()

		self.assertEqual(2, parent._data0)


class ClassVariablesInInitSubclass(Testcase):
	"""A derived class' class variable is visible to ``__init_subclass__``."""

	def test_AnAnnotatedOverrideIsVisible(self) -> None:
		"""
		It was not: the value was removed from the namespace and assigned after ``type.__new__``, so the hook read
		the base class' value and any pattern, table or key derived from it was silently built from the wrong one.
		"""
		seen = []

		class Base(metaclass=ExtendedType, slots=True):
			Separator: ClassVar[str] = ":"

			def __init_subclass__(cls, **kwargs) -> None:
				super().__init_subclass__(**kwargs)
				seen.append(cls.Separator)

		class Annotated(Base):
			Separator: ClassVar[str] = "!"

		self.assertEqual(["!"], seen)
		self.assertEqual("!", Annotated.Separator)

	def test_AnUnannotatedOverrideIsVisibleToo(self) -> None:
		"""This always worked; it must keep working."""
		seen = []

		class Base(metaclass=ExtendedType, slots=True):
			Separator: ClassVar[str] = ":"

			def __init_subclass__(cls, **kwargs) -> None:
				super().__init_subclass__(**kwargs)
				seen.append(cls.Separator)

		class Unannotated(Base):
			Separator = "!"

		self.assertEqual(["!"], seen)

	def test_TheHookMayDeriveFromTheValue(self) -> None:
		"""The point of seeing it: computing something per class from it, once, at class creation."""
		class Base(metaclass=ExtendedType, slots=True):
			Separator: ClassVar[str] = ":"
			Pattern:   ClassVar[str] = "<none>"

			def __init_subclass__(cls, **kwargs) -> None:
				super().__init_subclass__(**kwargs)
				cls.Pattern = f"epoch{cls.Separator}version"

		class Derived(Base):
			Separator: ClassVar[str] = "!"

		self.assertEqual("epoch!version", Derived.Pattern)

	def test_WhatTheHookAssignsIsNotOverwritten(self) -> None:
		"""The class fields used to be re-assigned after the hook ran, undoing whatever it had computed."""
		class Base(metaclass=ExtendedType, slots=True):
			Value: ClassVar[int] = 0

			def __init_subclass__(cls, **kwargs) -> None:
				super().__init_subclass__(**kwargs)
				cls.Value = cls.Value * 10

		class Derived(Base):
			Value: ClassVar[int] = 7

		self.assertEqual(70, Derived.Value)

	def test_AClassVariableStillShadowsNoSlot(self) -> None:
		"""A name that is both a mixin's slot and a class variable is rejected, with advice that fits the case."""
		class Mixin(metaclass=ExtendedType, mixin=True):
			_field: int

		with self.assertRaises(DuplicateFieldInSlotsError) as capture:
			class Host(Mixin, metaclass=ExtendedType, slots=True):
				_field: ClassVar[int] = 1

		self.assertIn("Rename the class variable", capture.exception.__notes__[-1])
