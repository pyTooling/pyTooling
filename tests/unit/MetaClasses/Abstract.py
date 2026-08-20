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

This test suite tests decorators:

* :deco:`~pyTooling.MetaClasses.abstractmethod`
* :deco:`~pyTooling.MetaClasses.mustoverride`
"""
from typing import Tuple

from pyTooling.Decorators  import notimplemented
from pyTooling.MetaClasses import ExtendedType, abstractclass, abstractmethod, mustoverride, AbstractClassError
from pyTooling.MetaClasses import mixin
from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class AbstractClasses(Testcase):
	"""A class can be abstract by declaration, not only by containing an abstract method."""

	def test_NoMetaclass(self) -> None:
		"""Nothing would compute abstractness, so the decorator says so instead of silently doing nothing."""

		with self.assertRaises(AttributeError):
			@abstractclass
			class Plain:
				pass

	def test_AbstractClass(self) -> None:
		@abstractclass
		class Base(metaclass=ExtendedType):
			pass

		self.assertTrue(Base.__abstractClass__)
		self.assertTrue(Base.__isAbstract__)
		with self.assertRaises(AbstractClassError) as exceptionCapture:
			Base()

		self.assertEqual("Class 'Base' is abstract and needs to be derived.", str(exceptionCapture.exception))

	def test_AbstractClass_Derived(self) -> None:
		@abstractclass
		class Base(metaclass=ExtendedType):
			def Method(self) -> int:
				return 1

		class Derived(Base):
			pass

		self.assertFalse(Derived.__abstractClass__)
		self.assertFalse(Derived.__isAbstract__)
		self.assertEqual(1, Derived().Method())

	def test_AbstractClass_AbstractClass(self) -> None:
		@abstractclass
		class Base(metaclass=ExtendedType):
			pass

		@abstractclass
		class Derived(Base):
			pass

		self.assertTrue(Derived.__abstractClass__)
		self.assertTrue(Derived.__isAbstract__)
		with self.assertRaises(AbstractClassError):
			Derived()


class AbstractMethod(Testcase):
	def test_AbstractBase(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		with self.assertRaises(AbstractClassError) as exceptionCapture:
			AbstractBase(1)

		self.assertIn("AbstractBase", str(exceptionCapture.exception))
		self.assertIn("AbstractMethod", str(exceptionCapture.exception))

	def test_AbstractClass(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		class AbstractClass(AbstractBase):
			pass

		with self.assertRaises(AbstractClassError) as exceptionCapture:
			AbstractClass(2)

		self.assertIn("AbstractClass", str(exceptionCapture.exception))
		self.assertIn("AbstractMethod", str(exceptionCapture.exception))

	def test_DerivedAbstractBase(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		class DerivedAbstractBase(AbstractBase):
			def AbstractMethod(self) -> bool:
				return super().AbstractMethod()

		derived = DerivedAbstractBase(3)

		with self.assertRaises(NotImplementedError) as exceptionCapture:
			derived.AbstractMethod()

		self.assertEqual("Method 'AbstractMethod' is abstract and needs to be overridden in a derived class.", str(exceptionCapture.exception))

	def test_DoubleDerivedAbstractBase(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		class DerivedAbstractBase(AbstractBase):
			def AbstractMethod(self) -> bool:
				return super().AbstractMethod()

		class DoubleDerivedAbstractBase(DerivedAbstractBase):
			pass

		derived = DoubleDerivedAbstractBase(4)

		with self.assertRaises(NotImplementedError) as exceptionCapture:
			derived.AbstractMethod()

		self.assertEqual("Method 'AbstractMethod' is abstract and needs to be overridden in a derived class.", str(exceptionCapture.exception))

	def test_DerivedAbstractClass(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		class AbstractClass(AbstractBase):
			pass

		class DerivedAbstractClass(AbstractClass):
			def AbstractMethod(self) -> bool:
				return super().AbstractMethod()

		derived = DerivedAbstractClass(5)

		with self.assertRaises(NotImplementedError) as exceptionCapture:
			derived.AbstractMethod()

		self.assertEqual("Method 'AbstractMethod' is abstract and needs to be overridden in a derived class.", str(exceptionCapture.exception))

	def test_MultipleInheritance(self) -> None:
		class AbstractBase(metaclass=ExtendedType):
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@abstractmethod
			def AbstractMethod(self) -> bool:
				return False

		class Mixin:
			def AbstractMethod(self) -> bool:
				return True

		class MultipleInheritance(AbstractBase, Mixin):
			pass

		derived = MultipleInheritance(6)
		derived.AbstractMethod()


class MustOverride(Testcase):
	def test_MustOverrideBase(self) -> None:
		class MustOverrideBase(metaclass=ExtendedType):
			@mustoverride
			def MustOverrideMethod(self) -> bool:
				return False

		with self.assertRaises(AbstractClassError) as exceptionCapture:
			MustOverrideBase()

		self.assertIn("MustOverrideBase", str(exceptionCapture.exception))
		self.assertIn("MustOverrideMethod", str(exceptionCapture.exception))

	def test_MustOverrideClass(self) -> None:
		class MustOverrideBase(metaclass=ExtendedType):
			@mustoverride
			def MustOverrideMethod(self) -> bool:
				return False

		class MustOverrideClass(MustOverrideBase):
			pass

		with self.assertRaises(AbstractClassError) as exceptionCapture:
			MustOverrideClass()

		self.assertIn("MustOverrideClass", str(exceptionCapture.exception))
		self.assertIn("MustOverrideMethod", str(exceptionCapture.exception))

	def test_DerivedMustOverride(self) -> None:
		class MustOverrideBase(metaclass=ExtendedType):
			@mustoverride
			def MustOverrideMethod(self) -> bool:
				return False

		class DerivedMustOverrideClass(MustOverrideBase):
			def MustOverrideMethod(self) -> bool:
				return super().MustOverrideMethod()

		DerivedMustOverrideClass()


class NotImplemented(Testcase):
	def test_NotImplementedBase(self) -> None:
		class NotImplementedBase(metaclass=ExtendedType):
			@notimplemented("It's not working.")
			def NotYetFinished(self, param: int) -> bool:
				"""Documentation is unfinished."""
				return False

		c = NotImplementedBase()

		self.assertEqual("Documentation is unfinished.", c.NotYetFinished.__doc__)
		self.assertEqual("NotYetFinished", c.NotYetFinished.__name__)

		with self.assertRaises(NotImplementedError) as exceptionCapture:
			c.NotYetFinished(4)

		self.assertEqual("It's not working.", str(exceptionCapture.exception))


class AbstractMethodInADiamond(Testcase):
	"""An abstract method reached through a normal base-class *and* through a mixin-class."""

	@staticmethod
	def _Hierarchy() -> Tuple[type, type, type]:
		"""
		Build the inheritance diamond both testcases share.

		:returns: A 3-tuple of the abstract base-class, the implementing class and the mixin-class.
		"""
		class Base(metaclass=ExtendedType, slots=True):
			@abstractmethod
			def Render(self) -> str:
				"""Render this element."""

		class Element(Base):
			def Render(self) -> str:
				return "element"

		@mixin
		class Container(Base):
			pass

		return Base, Element, Container

	def test_ClassOverridesTheMethod(self) -> None:
		_, Element, Container = self._Hierarchy()

		class Both(Element, Container):
			def Render(self) -> str:
				return "both"

		self.assertEqual("both", Both().Render())

	def test_ClassInheritsTheImplementation(self) -> None:
		_, Element, Container = self._Hierarchy()

		class Both(Element, Container):
			pass

		self.assertEqual("element", Both().Render())

	def test_TheMixinCarriesTheImplementation(self) -> None:
		Base, _, _ = self._Hierarchy()

		@mixin
		class Implementing(Base):
			def Render(self) -> str:
				return "mixin"

		class Primary(Base):
			pass

		class Derived(Primary, Implementing):
			pass

		self.assertEqual("mixin", Derived().Render())

	def test_NobodyImplementsIt(self) -> None:
		Base, _, Container = self._Hierarchy()

		class Primary(Base):
			pass

		class Derived(Primary, Container):
			pass

		with self.assertRaises(AbstractClassError) as exceptionCapture:
			Derived()

		self.assertIn("Derived", str(exceptionCapture.exception))
		self.assertIn("Render", str(exceptionCapture.exception))
