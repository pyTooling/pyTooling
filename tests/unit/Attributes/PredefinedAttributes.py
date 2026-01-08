# ==================================================================================================================== #
#             _____           _ _                  _   _   _        _ _           _                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _     / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |   / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/                        #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
Unit tests for attributes attached to methods.
"""
from unittest              import TestCase

from pyTooling.Common      import firstItem
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Attributes  import SimpleAttribute, Attribute, Entity


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Simple(TestCase):
	def test_ClassAttribute(self) -> None:
		@SimpleAttribute(1, 2, id="my", name="Class1")
		class MyClass1(metaclass=ExtendedType):
			pass

		@SimpleAttribute(3, 4, id="my", name="Class2")
		class MyClass2(metaclass=ExtendedType):
			pass

		expectedList = [
			((1, 2), {"id": "my", "name": "Class1"}),
			((3, 4), {"id": "my", "name": "Class2"}),
		]

		for cls, expected in zip(SimpleAttribute.GetClasses(), expectedList):
			attr = firstItem(cls.__pyattr__)
			self.assertTupleEqual(expected[0], attr.Args)
			self.assertDictEqual(expected[1], attr.KwArgs)

	def test_MethodAttribute(self) -> None:
		class MyClass1(metaclass=ExtendedType):
			@SimpleAttribute(1, 2, id="my", name="Class1")
			def method(self):
				pass

		class MyClass2(metaclass=ExtendedType):
			@SimpleAttribute(3, 4, id="my", name="Class2")
			def method(self):
				pass

		expectedList = [
			((1, 2), {"id": "my", "name": "Class1"}),
			((3, 4), {"id": "my", "name": "Class2"}),
		]

		for cls, expected in zip(SimpleAttribute.GetMethods(), expectedList):
			attr = firstItem(cls.__pyattr__)
			self.assertTupleEqual(expected[0], attr.Args)
			self.assertDictEqual(expected[1], attr.KwArgs)

	def test_FunctionAttribute(self) -> None:
		@SimpleAttribute(1, 2, id="my", name="Func1")
		def function1():
			pass

		@SimpleAttribute(3, 4, id="my", name="Func2")
		def function2():
			pass

		expectedList = [
			((1, 2), {"id": "my", "name": "Func1"}),
			((3, 4), {"id": "my", "name": "Func2"}),
		]

		for cls, expected in zip(SimpleAttribute.GetFunctions(), expectedList):
			attr = firstItem(cls.__pyattr__)
			self.assertTupleEqual(expected[0], attr.Args)
			self.assertDictEqual(expected[1], attr.KwArgs)


class MySimpleAttribute(SimpleAttribute):
	pass


class GroupAttribute(Attribute):
	_id: str

	def __init__(self, identifier: str) -> None:
		self._id = identifier

	def __call__(self, entity: Entity) -> Entity:
		self._AppendAttribute(entity, MySimpleAttribute(3, 4, id=self._id, name="attr1"))
		self._AppendAttribute(entity, MySimpleAttribute(5, 6, id=self._id, name="attr2"))

		return entity


class Grouped(TestCase):
	def test_Group_Simple(self) -> None:
		@MySimpleAttribute(1, 2, id="my", name="Class1")
		@GroupAttribute("grp")
		class MyClass1:
			pass

		foundClasses = [c for c in MySimpleAttribute.GetClasses()]

		self.assertEqual(3, len(foundClasses))
		for c in foundClasses:
			self.assertIs(MyClass1, c)
