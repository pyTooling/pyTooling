# ==================================================================================================================== #
#                  _   _   _        _ _           _                                                                    #
#   _ __  _   _   / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___                                                         #
#  | '_ \| | | | / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|                                                        #
#  | |_) | |_| |/ ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \                                                        #
#  | .__/ \__, /_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/                                                        #
#  |_|    |___/                                                                                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from sys                   import version_info
from unittest              import TestCase

from pytest                import mark

from pyTooling.MetaClasses import ExtendedType
from pyTooling.Attributes  import Attribute


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ApplyMethodAttributes_NoMetaClass(TestCase):
	def test_NoAttribute(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth0)]

		self.assertEqual(0, len(foundMethodsOnAttributeA))
		self.assertEqual(0, len(foundAttributesAOnClass1Meth1))

	def test_SingleAttribute_SingleClass_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]

		self.assertEqual(1, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)

	def test_SingleAttribute_SingleClass_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]

		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		for a in foundAttributesAOnClass1Meth2:
			self.assertIsInstance(a, AttributeA)

	def test_SingleAttribute_MultipleClasses_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		class Class2:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass2Meth0 = [a for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [a for a in AttributeA.GetAttributes(Class2.meth1)]

		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class2.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		for a in foundAttributesAOnClass2Meth1:
			self.assertIsInstance(a, AttributeA)

	def test_SingleAttribute_MultipleClasses_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		class Class2:
			@AttributeA()
			def meth1(self):
				pass

			def meth2(self):
				pass

			@AttributeA()
			def meth3(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth1 = [a for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesAOnClass2Meth2 = [a for a in AttributeA.GetAttributes(Class2.meth2)]
		foundAttributesAOnClass2Meth3 = [a for a in AttributeA.GetAttributes(Class2.meth3)]

		self.assertEqual(4, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2, Class2.meth1, Class2.meth3])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		for a in foundAttributesAOnClass1Meth2:
			self.assertIsInstance(a, AttributeA)

		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		for a in foundAttributesAOnClass2Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(0, len(foundAttributesAOnClass2Meth2))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth3))
		for a in foundAttributesAOnClass2Meth3:
			self.assertIsInstance(a, AttributeA)

	def test_MultipleAttributes_SingleClass_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeB()
			def meth2(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth1 = [b for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [b for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth3 = [b for b in AttributeB.GetAttributes(Class1.meth0)]

		self.assertEqual(1, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(0, len(foundAttributesAOnClass1Meth2))

		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		for b in foundAttributesBOnClass1Meth1:
			self.assertIsInstance(b, AttributeB)
		self.assertEqual(1, len(foundAttributesBOnClass1Meth2))
		for b in foundAttributesBOnClass1Meth2:
			self.assertIsInstance(b, AttributeB)
		self.assertEqual(0, len(foundAttributesBOnClass1Meth3))

	def test_MultipleAttributes_SingleClass_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

			@AttributeB()
			def meth3(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass1Meth3 = [a for a in AttributeA.GetAttributes(Class1.meth3)]
		foundAttributesBOnClass1Meth0 = [b for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [b for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [b for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth3 = [b for b in AttributeB.GetAttributes(Class1.meth3)]

		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth3])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		for a in foundAttributesAOnClass1Meth2:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(0, len(foundAttributesAOnClass1Meth3))

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		for b in foundAttributesBOnClass1Meth1:
			self.assertIsInstance(b, AttributeB)
		self.assertEqual(0, len(foundAttributesBOnClass1Meth2))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth3))
		for b in foundAttributesBOnClass1Meth3:
			self.assertIsInstance(b, AttributeB)

	def test_MultipleAttributes_MultipleClasses_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeB()
			def meth2(self):
				pass

		class Class2:
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth0 = [a for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [a for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesBOnClass1Meth0 = [b for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [b for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [b for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass2Meth0 = [b for b in AttributeB.GetAttributes(Class2.meth0)]
		foundAttributesBOnClass2Meth1 = [b for b in AttributeB.GetAttributes(Class2.meth1)]

		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertEqual(3, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class2.meth1])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth2, Class2.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(0, len(foundAttributesAOnClass1Meth2))

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		for a in foundAttributesAOnClass2Meth1:
			self.assertIsInstance(a, AttributeA)

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		for b in foundAttributesBOnClass1Meth1:
			self.assertIsInstance(b, AttributeB)
		self.assertEqual(1, len(foundAttributesBOnClass1Meth2))
		for b in foundAttributesBOnClass1Meth2:
			self.assertIsInstance(b, AttributeB)

		self.assertEqual(0, len(foundAttributesBOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass2Meth1))
		for b in foundAttributesBOnClass2Meth1:
			self.assertIsInstance(b, AttributeB)

	def test_MultipleAttributes_MultipleClasses_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1:
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		class Class2:
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth3(self):
				pass

		foundMethodsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundAttributesAOnClass1Meth0 = [a for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [a for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [a for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth0 = [a for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [a for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesAOnClass2Meth2 = [a for a in AttributeA.GetAttributes(Class2.meth2)]
		foundAttributesAOnClass2Meth3 = [a for a in AttributeA.GetAttributes(Class2.meth3)]
		foundAttributesBOnClass1Meth0 = [a for a in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [a for a in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [a for a in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass2Meth0 = [a for a in AttributeB.GetAttributes(Class2.meth0)]
		foundAttributesBOnClass2Meth1 = [a for a in AttributeB.GetAttributes(Class2.meth1)]
		foundAttributesBOnClass2Meth2 = [a for a in AttributeB.GetAttributes(Class2.meth2)]
		foundAttributesBOnClass2Meth3 = [a for a in AttributeB.GetAttributes(Class2.meth3)]

		self.assertEqual(5, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2, Class2.meth1, Class2.meth2, Class2.meth3])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class2.meth3])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		for a in foundAttributesAOnClass1Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		for a in foundAttributesAOnClass1Meth2:
			self.assertIsInstance(a, AttributeA)

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		for a in foundAttributesAOnClass2Meth1:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass2Meth2))
		for a in foundAttributesAOnClass2Meth2:
			self.assertIsInstance(a, AttributeA)
		self.assertEqual(1, len(foundAttributesAOnClass2Meth3))
		for a in foundAttributesAOnClass2Meth3:
			self.assertIsInstance(a, AttributeA)

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		for b in foundAttributesBOnClass1Meth1:
			self.assertIsInstance(b, AttributeB)
		self.assertEqual(0, len(foundAttributesBOnClass1Meth2))

		self.assertEqual(0, len(foundAttributesBOnClass2Meth0))
		self.assertEqual(0, len(foundAttributesBOnClass2Meth1))
		self.assertEqual(0, len(foundAttributesBOnClass2Meth2))
		self.assertEqual(1, len(foundAttributesBOnClass2Meth3))
		for b in foundAttributesBOnClass2Meth3:
			self.assertIsInstance(b, AttributeB)


class ApplyMethodAttributes_WithMetaClass(TestCase):
	@mark.skipif(version_info < (3, 9), reason="Disabled on Python 3.8.")
	def test_NoAttribute(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundMethodsOnClass1 = [m for m in Class1.GetMethodsWithAttributes()]
		# foundAttributesOnClass1Meth1 = Class1.GetAttributes(Class1.meth0)

		self.assertFalse(Class1.HasClassAttributes)
		self.assertFalse(Class1.HasMethodAttributes)
		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(0, len(foundMethodsOnAttributeA))
		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		# self.assertFalse(Class1.HasAttributes())
		# self.assertFalse(Class1.HasAttribute(Class1.meth0))
		self.assertEqual(0, len(foundMethodsOnClass1))
		# self.assertEqual(0, len(foundAttributesOnClass1Meth1))

	def test_SingleAttribute_SingleClass_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(1, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])

	def test_SingleAttribute_SingleClass_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		self.assertListEqual(foundAttributesAOnClass1Meth2, [AttributeA])

	def test_SingleAttribute_MultipleClasses_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		class Class2(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass2Meth0 = [type(a) for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [type(a) for a in AttributeA.GetAttributes(Class2.meth1)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class2.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		self.assertListEqual(foundAttributesAOnClass2Meth1, [AttributeA])

	def test_SingleAttribute_MultipleClasses_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		class Class2(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth0 = [type(a) for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [type(a) for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesAOnClass2Meth2 = [type(a) for a in AttributeA.GetAttributes(Class2.meth2)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(4, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2, Class2.meth1, Class2.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		self.assertListEqual(foundAttributesAOnClass1Meth2, [AttributeA])

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		self.assertListEqual(foundAttributesAOnClass2Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass2Meth2))
		self.assertListEqual(foundAttributesAOnClass2Meth2, [AttributeA])

	def test_MultipleAttributes_SingleClass_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeB()
			def meth2(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundFunctionsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth0 = [type(b) for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [type(b) for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [type(b) for b in AttributeB.GetAttributes(Class1.meth2)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(0, len(foundFunctionsOnAttributeB))
		self.assertEqual(1, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(0, len(foundAttributesAOnClass1Meth2))

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		self.assertListEqual(foundAttributesBOnClass1Meth1, [AttributeB])
		self.assertEqual(1, len(foundAttributesBOnClass1Meth2))
		self.assertListEqual(foundAttributesBOnClass1Meth2, [AttributeB])

	def test_MultipleAttributes_SingleClass_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

			@AttributeB()
			def meth3(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundFunctionsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass1Meth3 = [type(a) for a in AttributeA.GetAttributes(Class1.meth3)]
		foundAttributesBOnClass1Meth0 = [type(b) for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [type(b) for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [type(b) for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth3 = [type(b) for b in AttributeB.GetAttributes(Class1.meth3)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(0, len(foundFunctionsOnAttributeB))
		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth3])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		self.assertListEqual(foundAttributesAOnClass1Meth2, [AttributeA])
		self.assertEqual(0, len(foundAttributesAOnClass1Meth3))

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		self.assertListEqual(foundAttributesBOnClass1Meth1, [AttributeB])
		self.assertEqual(0, len(foundAttributesBOnClass1Meth2))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth3))
		self.assertListEqual(foundAttributesBOnClass1Meth3, [AttributeB])

	def test_MultipleAttributes_MultipleClasses_SingleMethod(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeB()
			def meth2(self):
				pass

		class Class2(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass


		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundFunctionsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth0 = [type(a) for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [type(a) for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesBOnClass1Meth0 = [type(b) for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [type(b) for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [type(b) for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass2Meth0 = [type(b) for b in AttributeB.GetAttributes(Class2.meth0)]
		foundAttributesBOnClass2Meth1 = [type(b) for b in AttributeB.GetAttributes(Class2.meth1)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(0, len(foundFunctionsOnAttributeB))
		self.assertEqual(2, len(foundMethodsOnAttributeA))
		self.assertEqual(3, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class2.meth1])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class1.meth2, Class2.meth1])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(0, len(foundAttributesAOnClass1Meth2))

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		self.assertListEqual(foundAttributesAOnClass2Meth1, [AttributeA])

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		self.assertListEqual(foundAttributesBOnClass1Meth1, [AttributeB])
		self.assertEqual(1, len(foundAttributesBOnClass1Meth2))
		self.assertListEqual(foundAttributesBOnClass1Meth2, [AttributeB])

		self.assertEqual(0, len(foundAttributesBOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass2Meth1))
		self.assertListEqual(foundAttributesBOnClass2Meth1, [AttributeB])

	def test_MultipleAttributes_MultipleClasses_MultipleMethods(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth1(self):
				pass

			@AttributeA()
			def meth2(self):
				pass

		class Class2(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth2(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundFunctionsOnAttributeB = [f for f in AttributeB.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]
		foundAttributesAOnClass1Meth0 = [type(a) for a in AttributeA.GetAttributes(Class1.meth0)]
		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass2Meth0 = [type(a) for a in AttributeA.GetAttributes(Class2.meth0)]
		foundAttributesAOnClass2Meth1 = [type(a) for a in AttributeA.GetAttributes(Class2.meth1)]
		foundAttributesAOnClass2Meth2 = [type(a) for a in AttributeA.GetAttributes(Class2.meth2)]
		foundAttributesBOnClass1Meth0 = [type(b) for b in AttributeB.GetAttributes(Class1.meth0)]
		foundAttributesBOnClass1Meth1 = [type(b) for b in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [type(b) for b in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass2Meth0 = [type(b) for b in AttributeB.GetAttributes(Class2.meth0)]
		foundAttributesBOnClass2Meth1 = [type(b) for b in AttributeB.GetAttributes(Class2.meth1)]
		foundAttributesBOnClass2Meth2 = [type(b) for b in AttributeB.GetAttributes(Class2.meth2)]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(0, len(foundFunctionsOnAttributeB))
		self.assertEqual(4, len(foundMethodsOnAttributeA))
		self.assertEqual(2, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth2, Class2.meth1, Class2.meth2])
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth1, Class2.meth2])

		self.assertEqual(0, len(foundAttributesAOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		self.assertListEqual(foundAttributesAOnClass1Meth2, [AttributeA])

		self.assertEqual(0, len(foundAttributesAOnClass2Meth0))
		self.assertEqual(1, len(foundAttributesAOnClass2Meth1))
		self.assertListEqual(foundAttributesAOnClass2Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass2Meth2))
		self.assertListEqual(foundAttributesAOnClass2Meth2, [AttributeA])

		self.assertEqual(0, len(foundAttributesBOnClass1Meth0))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth1))
		self.assertListEqual(foundAttributesBOnClass1Meth1, [AttributeB])
		self.assertEqual(0, len(foundAttributesBOnClass1Meth2))

		self.assertEqual(0, len(foundAttributesBOnClass2Meth0))
		self.assertEqual(0, len(foundAttributesBOnClass2Meth1))
		self.assertEqual(1, len(foundAttributesBOnClass2Meth2))
		self.assertListEqual(foundAttributesBOnClass2Meth2, [AttributeB])


class MetaTesting(TestCase):
	def test_Meta(self):
		print()

		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeB()
			def meth2(self):
				pass

			@AttributeA()
			@AttributeB()
			def meth3(self):
				pass

			@AttributeA()
			@AttributeB()
			@AttributeB()
			def meth4(self):
				pass

		foundFunctionsOnAttributeA = [f for f in AttributeA.GetFunctions()]
		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]

		self.assertEqual(0, len(foundFunctionsOnAttributeA))
		self.assertEqual(3, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1, Class1.meth3, Class1.meth4])
		self.assertEqual(4, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth2, Class1.meth3, Class1.meth4, Class1.meth4])


class GetAttributesFiltering(TestCase):
	pass

	# default filter
	# no filter
	# subclasses
	# tuple filter (or)


class GetFunctionsFiltering(TestCase):
	pass

	# default filter
	# no filter
	# subclasses
	# tuple filter (or)


class GetClassesFiltering(TestCase):
	pass

	# default filter
	# no filter
	# subclasses
	# tuple filter (or)


class Attribute_GetMethods_Filtering(TestCase):
	def test_1(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeAA(AttributeA):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			def meth0(self):
				pass

			@AttributeA()
			def meth1(self):
				pass

			@AttributeAA()
			def meth2(self):
				pass

			@AttributeB()
			def meth3(self):
				pass

		foundMethodsOnAttributeA = [m for m in AttributeA.GetMethods()]
		foundMethodsOnAttributeAA = [m for m in AttributeAA.GetMethods()]
		foundMethodsOnAttributeB = [m for m in AttributeB.GetMethods()]

		self.assertEqual(1, len(foundMethodsOnAttributeA))
		self.assertListEqual(foundMethodsOnAttributeA, [Class1.meth1])
		self.assertEqual(1, len(foundMethodsOnAttributeAA))
		self.assertListEqual(foundMethodsOnAttributeAA, [Class1.meth2])
		self.assertEqual(1, len(foundMethodsOnAttributeB))
		self.assertListEqual(foundMethodsOnAttributeB, [Class1.meth3])


class Attribute_GetAttributes_Filtering(TestCase):
	def test_1(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeAA(AttributeA):
			pass

		class AttributeB(Attribute):
			pass

		class Class1(metaclass=ExtendedType):
			@AttributeA()
			def meth1(self):
				pass

			@AttributeAA()
			def meth2(self):
				pass

			@AttributeB()
			def meth3(self):
				pass

		foundAttributesAOnClass1Meth1 = [type(a) for a in AttributeA.GetAttributes(Class1.meth1)]
		foundAttributesAOnClass1Meth2 = [type(a) for a in AttributeA.GetAttributes(Class1.meth2)]
		foundAttributesAOnClass1Meth3 = [type(a) for a in AttributeA.GetAttributes(Class1.meth3)]
		foundAttributesAAOnClass1Meth1 = [type(a) for a in AttributeAA.GetAttributes(Class1.meth1)]
		foundAttributesAAOnClass1Meth2 = [type(a) for a in AttributeAA.GetAttributes(Class1.meth2)]
		foundAttributesAAOnClass1Meth3 = [type(a) for a in AttributeAA.GetAttributes(Class1.meth3)]
		foundAttributesBOnClass1Meth1 = [type(a) for a in AttributeB.GetAttributes(Class1.meth1)]
		foundAttributesBOnClass1Meth2 = [type(a) for a in AttributeB.GetAttributes(Class1.meth2)]
		foundAttributesBOnClass1Meth3 = [type(a) for a in AttributeB.GetAttributes(Class1.meth3)]

		self.assertEqual(1, len(foundAttributesAOnClass1Meth1))
		self.assertListEqual(foundAttributesAOnClass1Meth1, [AttributeA])
		self.assertEqual(1, len(foundAttributesAOnClass1Meth2))
		self.assertListEqual(foundAttributesAOnClass1Meth2, [AttributeAA])
		self.assertEqual(0, len(foundAttributesAOnClass1Meth3))

		self.assertEqual(0, len(foundAttributesAAOnClass1Meth1))
		self.assertEqual(1, len(foundAttributesAAOnClass1Meth2))
		self.assertListEqual(foundAttributesAAOnClass1Meth2, [AttributeAA])
		self.assertEqual(0, len(foundAttributesAAOnClass1Meth3))

		self.assertEqual(0, len(foundAttributesBOnClass1Meth1))
		self.assertEqual(0, len(foundAttributesBOnClass1Meth2))
		self.assertEqual(1, len(foundAttributesBOnClass1Meth3))
		self.assertListEqual(foundAttributesBOnClass1Meth3, [AttributeB])

	# default filter
	# no filter
	# subclasses
	# tuple filter (or)
