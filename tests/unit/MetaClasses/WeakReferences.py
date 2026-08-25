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
from weakref import ref as WeakReference

from pyTooling.MetaClasses import ExtendedType
from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class WeakReferences(Testcase):
	"""``weakref=True`` adds ``__weakref__`` to a slotted class' slots."""

	def test_ASlottedClassIsNotWeakReferenceableByDefault(self) -> None:
		class Slotted(metaclass=ExtendedType, slots=True):
			_field: int

		self.assertNotIn("__weakref__", Slotted.__slots__)
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

	def test_ItIsNotDeclaredTwiceInAHierarchy(self) -> None:
		"""Python rejects a second ``__weakref__`` in one hierarchy, so asking again must be a no-op."""

		class Base(metaclass=ExtendedType, slots=True, weakref=True):
			_field: int

		class Derived(Base, metaclass=ExtendedType, slots=True, weakref=True):
			_other: int

		self.assertNotIn("__weakref__", Derived.__slots__)
		self.assertIsNotNone(WeakReference(Derived()))

	def test_AMixinContributesItsFieldsAsUsual(self) -> None:
		class Mixin(metaclass=ExtendedType, mixin=True):
			_fromMixin: int

		class Application(metaclass=ExtendedType, slots=True, weakref=True):
			_own: int

		class Combined(Application, Mixin):
			pass

		self.assertIn("_fromMixin", Combined.__slots__)
		self.assertIsNotNone(WeakReference(Combined()))
