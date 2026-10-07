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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Unit tests for the ``weakref`` class keyword argument of :class:`pyTooling.MetaClasses.ExtendedType`.

A slotted class cannot be referenced weakly unless ``__weakref__`` is one of its slots.
"""
from gc      import collect as gc_collect
from typing  import Any
from weakref import ref as WeakReference

from pytest                import mark

from pyTooling.MetaClasses import ExtendedType, ExtendedTypeError
from pyTooling.Platform    import CurrentPlatform
from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class WeakReferences(Testcase):
	"""``weakref=True`` adds ``__weakref__`` to a slotted class' slots."""

	def test_ASlottedClassHasNoWeakrefSlotByDefault(self) -> None:
		class Slotted(metaclass=ExtendedType, slots=True):
			_field: int

		self.assertNotIn("__weakref__", Slotted.__slots__)

	@mark.skipif(CurrentPlatform.IsPyPy, reason="PyPy makes every object weak-referenceable, slots or not.")
	def test_OnCPythonThatMakesItUnreferenceable(self) -> None:
		"""The restriction this keyword lifts is CPython's: no ``__weakref__`` slot, no weak reference."""

		class Slotted(metaclass=ExtendedType, slots=True):
			_field: int

		with self.assertRaises(TypeError):
			WeakReference(Slotted())

	def test_WeakrefAddsTheSlot(self) -> None:
		class Slotted(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		self.assertIn("__weakref__", Slotted.__slots__)

	def test_AnInstanceCanBeReferencedWeakly(self) -> None:
		class Slotted(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		instance = Slotted()
		reference = WeakReference(instance)

		self.assertIs(instance, reference())

	def test_TheReferenceDiesWithTheObject(self) -> None:
		class Slotted(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		instance = Slotted()
		reference = WeakReference(instance)
		del instance
		gc_collect()   # PyPy doesn't count references, so the object is not collected at 'del'.

		self.assertIsNone(reference(), "A weak reference doesn't keep its object alive.")

	def test_TheFieldsStillWork(self) -> None:
		"""``__weakref__`` is a slot like any other, so it must not disturb the ones that carry data."""

		class Slotted(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

			def __init__(self) -> None:
				self._field = 42

		self.assertEqual(42, Slotted()._field)

	def test_ADerivedClassInheritsIt(self) -> None:
		class Base(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		class Derived(Base):
			_other: int

		self.assertNotIn("__weakref__", Derived.__slots__, "It is inherited, not repeated.")
		self.assertIsNotNone(WeakReference(Derived()))

	def test_AskingTwiceInAHierarchyIsAnError(self) -> None:
		"""``__weakref__`` is a slot like any other, so a derived class asking again declares a duplicate slot."""

		class Base(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		with self.assertRaises(AttributeError):
			class Derived(Base, weakref=True):
				_other: int

	def test_AMixinContributesItsFieldsAsUsual(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True):
			_fromMixin: int

		class Application(metaclass=ExtendedType, slots=True, weakref=True):
			_own: int

		class Combined(Application, Mixin):
			pass

		self.assertIn("_fromMixin", Combined.__slots__)
		self.assertIsNotNone(WeakReference(Combined()))

	def test_AMixinContributesIt(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True, weakref=True):
			_fromMixin: int

		class Application(metaclass=ExtendedType, slots=True):
			_own: int

		class Combined(Application, Mixin):
			pass

		self.assertIn("__weakref__", Mixin.__mixinSlots__)
		self.assertIn("__weakref__", Combined.__slots__)
		self.assertIn("_fromMixin", Combined.__slots__)
		self.assertIsNotNone(WeakReference(Combined()))

	def test_AMixinOfMixinsPassesItOn(self) -> None:
		class Mixin1(metaclass=ExtendedType, mixin=True, weakref=True):
			_fromMixin1: int

		class Mixin2(Mixin1, mixin=True):
			_fromMixin2: int

		class Application(metaclass=ExtendedType, slots=True):
			_own: int

		class Combined(Application, Mixin2):
			pass

		self.assertEqual(1, Combined.__slots__.count("__weakref__"))
		self.assertIsNotNone(WeakReference(Combined()))

	def test_AMixinAskingOnAWeakReferenceableClassIsAnError(self) -> None:
		"""Python rejects the second ``__weakref__`` when the mixin-class' slots are materialized."""

		class Mixin(metaclass=ExtendedType, mixin=True, weakref=True):
			_fromMixin: int

		class Application(metaclass=ExtendedType, slots=True, weakref=True):
			_own: int

		with self.assertRaises(TypeError):
			class Combined(Application, Mixin):
				pass


class AnnotatedWeakref(Testcase):
	"""Annotating ``__weakref__`` is rejected in favour of ``weakref=True``."""

	def test_Slotted(self) -> None:
		with self.assertRaises(ExtendedTypeError) as context:
			class Slotted(metaclass=ExtendedType, slots=True):
				__weakref__: Any

		self.assertIn("weakref=True", "\n".join(context.exception.__notes__))

	def test_Mixin(self) -> None:
		with self.assertRaises(ExtendedTypeError):
			class Mixin(metaclass=ExtendedType, mixin=True):
				__weakref__: Any

	def test_NotSlotted(self) -> None:
		with self.assertRaises(ExtendedTypeError):
			class NotSlotted(metaclass=ExtendedType):
				__weakref__: Any


class AnnotatedDict(Testcase):
	"""Annotating ``__dict__`` is rejected, as it undoes what slots save."""

	def test_Slotted(self) -> None:
		with self.assertRaises(ExtendedTypeError) as context:
			class Slotted(metaclass=ExtendedType, slots=True):
				__dict__: Any

		self.assertIn("slots=False", "\n".join(context.exception.__notes__))

	def test_Mixin(self) -> None:
		with self.assertRaises(ExtendedTypeError):
			class Mixin(metaclass=ExtendedType, mixin=True):
				__dict__: Any
