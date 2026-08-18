# ==================================================================================================================== #
#             _____           _ _               ____                           _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___  ___ ___  _ __ __ _| |_ ___  _ __ ___                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \/ __/ _ \| '__/ _` | __/ _ \| '__/ __|                      #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ (_| (_) | | | (_| | || (_) | |  \__ \                      #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___|\___\___/|_|  \__,_|\__\___/|_|  |___/                      #
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
Unit tests for :mod:`pyTooling.Decorators`: :deco:`~pyTooling.Decorators.export`,
:deco:`~pyTooling.Decorators.readonly` and :deco:`~pyTooling.Decorators.InheritDocString`.
"""
from pyTooling.Decorators import export, InheritDocString, DocStringMergeOrder, readonly
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


__all__ = []


@export
class ExportedClass:
	pass


class NotYetExportedClass:
	pass


class NotExportedClass:
	pass


@export
def ExportedFunction():
	pass


def NotYetExportedFunction():
	pass


def NotExportedFunction():
	pass


L = lambda x: x


class Export(Testcase):
	def test_ExportedClass(self) -> None:
		self.assertIn(ExportedClass.__name__, __all__)
		self.assertNotIn(NotExportedClass.__name__, __all__)

	def test_ExportedFunction(self) -> None:
		self.assertIn(ExportedFunction.__name__, __all__)
		self.assertNotIn(NotExportedFunction.__name__, __all__)

	def test_ExportTopLevelClass(self) -> None:
		export(NotYetExportedClass)

	def test_ExportTopLevelFunction(self) -> None:
		export(NotYetExportedFunction)

	def test_ExportTopLevelLambda(self) -> None:
		with self.assertRaises(TypeError):
			export(L)

	def test_ExportLocalFunction(self) -> None:
		with self.assertRaises(TypeError):
			@export
			def F():
				pass

	def test_ExportLocalClass(self) -> None:
		with self.assertRaises(TypeError):
			@export
			class C:
				pass


class ReadOnly(Testcase):
	def test_ReadOnly(self) -> None:
		class Data:
			_data: int

			def __init__(self, data: int) -> None:
				self._data = data

			@readonly
			def length(self) -> int:
				return 2 ** self._data

		d = Data(2)
		self.assertEqual(4, d.length)
		with self.assertRaises(AttributeError):
			d.length = 5
		with self.assertRaises(AttributeError):
			del d.length

	def test_Setter(self) -> None:
		"""Attaching a setter to a read-only property is rejected while the class body is executed."""
		with self.assertRaises(AttributeError) as context:
			class Data:
				_data: int

				def __init__(self, data: int) -> None:
					self._data = data

				@readonly
				def length(self) -> int:
					return 2 ** self._data

				@length.setter
				def length(self, value):
					self._data = value

		self.assertIn("Property 'length' is read-only, so it can't have a setter.", str(context.exception))

	def test_Deleter(self) -> None:
		"""Attaching a deleter to a read-only property is rejected while the class body is executed."""
		with self.assertRaises(AttributeError) as context:
			class Data:
				_data: int

				def __init__(self, data: int) -> None:
					self._data = data

				@readonly
				def length(self) -> int:
					return 2 ** self._data

				@length.deleter
				def length(self):
					del self._data

		self.assertIn("Property 'length' is read-only, so it can't have a deleter.", str(context.exception))

	def test_ReadOnlyPropertyType(self) -> None:
		class Data:
			_data: int

			@readonly
			def length(self) -> int:
				"""Doc-string of the getter."""
				return 2 ** self._data

		self.assertIsInstance(Data.length, readonly)
		self.assertIsInstance(Data.length, property)
		self.assertEqual("Doc-string of the getter.", Data.length.__doc__)


class InheritDocStrings(Testcase):
	def test_Class_Copy(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1)
		class Class2(Class1):
			pass

		self.assertEqual("Class1", Class1.__doc__)
		self.assertEqual(Class1.__doc__, Class2.__doc__)

	def test_Class_Override(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1)
		class Class2(Class1):
			"""Class2"""

		self.assertEqual("Class1", Class2.__doc__)

	def test_Class_Fallback(self) -> None:
		class Class1:
			pass

		@InheritDocString(Class1, merge=True)
		class Class2(Class1):
			"""Class2"""

		self.assertIsNone(Class1.__doc__)
		self.assertEqual("Class2", Class2.__doc__)

	def test_Class_Merge(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1, merge=True)
		class Class2(Class1):
			"""Class2"""

		self.assertEqual("Class1", Class1.__doc__)
		self.assertEqual("Class1\n\nClass2", Class2.__doc__)

	def test_Class_MergeDerivedFirst(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1, merge=True, order=DocStringMergeOrder.DerivedFirst)
		class Class2(Class1):
			"""Class2"""

		self.assertEqual("Class2\n\nClass1", Class2.__doc__)

	def test_Class_MergeAffixes(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1, merge=True, prefix="<", interfix="|", postfix=">")
		class Class2(Class1):
			"""Class2"""

		self.assertEqual("<Class1|Class2>", Class2.__doc__)

	def test_Class_MergeAffixesWithoutBaseDocString(self) -> None:
		class Class1:
			pass

		@InheritDocString(Class1, merge=True, prefix="<", interfix="|", postfix=">")
		class Class2(Class1):
			"""Class2"""

		self.assertEqual("<Class2>", Class2.__doc__)

	def test_Class_MergeAffixesWithoutDerivedDocString(self) -> None:
		class Class1:
			"""Class1"""

		@InheritDocString(Class1, merge=True, prefix="<", interfix="|", postfix=">")
		class Class2(Class1):
			pass

		self.assertEqual("<Class1>", Class2.__doc__)

	def test_Class_MergeWithoutAnyDocString(self) -> None:
		class Class1:
			pass

		@InheritDocString(Class1, merge=True, prefix="<", postfix=">")
		class Class2(Class1):
			pass

		self.assertIsNone(Class2.__doc__)

	def test_Class_MergeDedentsBothDocStrings(self) -> None:
		"""Both parts are dedented, even if they were indented differently (tabs vs. spaces)."""
		class Class1:
			pass

		class Class2(Class1):
			pass

		# Python 3.13+ strips a doc-string's indentation at compile time, so assign the raw form explicitly.
		Class1.__doc__ = "\n\tLine 1.\n\n\tLine 2.\n\t"
		Class2.__doc__ = "\n    Line 3.\n\n    Line 4.\n    "

		InheritDocString(Class1, merge=True)(Class2)

		self.assertEqual("Line 1.\n\nLine 2.\n\nLine 3.\n\nLine 4.", Class2.__doc__)

	def test_Method(self) -> None:
		class Class1:
			def method(self):
				"""Method's doc-string."""

		class Class2(Class1):
			@InheritDocString(Class1)
			def method(self):
				pass

		self.assertEqual(Class1.method.__doc__, Class2.method.__doc__)

	def test_Method_Merge(self) -> None:
		class Class1:
			def method(self):
				"""Base method's doc-string."""

		class Class2(Class1):
			@InheritDocString(Class1, merge=True, order=DocStringMergeOrder.DerivedFirst)
			def method(self):
				"""Derived method's doc-string."""

		self.assertEqual("Derived method's doc-string.\n\nBase method's doc-string.", Class2.method.__doc__)
