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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from unittest     import TestCase

from pytest       import mark

from pyTooling.Attributes import Attribute


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ApplyClassAttributes(TestCase):
	def test_SingleClass(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		class Class1:
			pass

		foundClasses = [c for c in AttributeA.GetClasses()]

		self.assertListEqual(foundClasses, [Class1])

	def test_MultipleClasses(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		class Class1:
			pass

		@AttributeA()
		class Class2:
			pass

		foundClasses = [c for c in AttributeA.GetClasses()]

		self.assertListEqual(foundClasses, [Class1, Class2])

	def test_MultipleAttributes(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		@AttributeA()
		@AttributeB()
		class Class1:
			pass

		foundClassesForA = [c for c in AttributeA.GetClasses()]
		foundClassesForB = [c for c in AttributeB.GetClasses()]

		self.assertListEqual(foundClassesForA, [Class1])
		self.assertListEqual(foundClassesForB, [Class1])

	def test_MultipleClassesAndAttributes(self) -> None:
		class AttributeA(Attribute):
			pass

		class AttributeB(Attribute):
			pass

		@AttributeA()
		class Class1:
			pass

		@AttributeA()
		@AttributeB()
		class Class2:
			pass

		@AttributeB()
		@AttributeA()
		class Class3:
			pass

		@AttributeB()
		class Class4:
			pass

		foundClassesForA = [c for c in AttributeA.GetClasses()]
		foundClassesForB = [c for c in AttributeB.GetClasses()]

		self.assertListEqual(foundClassesForA, [Class1, Class2, Class3])
		self.assertListEqual(foundClassesForB, [Class2, Class3, Class4])

	def test_DerivedAttributes(self) -> None:
		class AttributeA1(Attribute):
			pass

		class AttributeA2(AttributeA1):
			pass

		@AttributeA1()
		class Class1:
			pass

		@AttributeA2()
		class Class2:
			pass

		foundClassesForA1 = [c for c in AttributeA1.GetClasses()]
		foundClassesForA2 = [c for c in AttributeA2.GetClasses()]

		self.assertListEqual(foundClassesForA1, [Class1])
		self.assertListEqual(foundClassesForA2, [Class2])

	def test_DoubleAppliedAttribute(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		@AttributeA()
		class Class1:
			pass

		foundClasses = [c for c in AttributeA.GetClasses()]

		self.assertListEqual(foundClasses, [Class1, Class1])

	def test_AttributeAndDerivedAttribute(self) -> None:
		class AttributeA1(Attribute):
			pass

		class AttributeA2(AttributeA1):
			pass

		@AttributeA1()
		@AttributeA2()
		class Class1:
			pass

		foundClassesForA1 = [c for c in AttributeA1.GetClasses()]
		foundClassesForA2 = [c for c in AttributeA2.GetClasses()]

		self.assertListEqual(foundClassesForA1, [Class1])
		self.assertListEqual(foundClassesForA2, [Class1])


class Filtering(TestCase):
	def test_NoFilter(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		class Class1:
			pass

		foundClasses = [c for c in AttributeA.GetClasses()]

		self.assertListEqual(foundClasses, [Class1])

	@mark.xfail(reason="Attributes are not inherited (yet)")
	def test_Predicate(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		class Class1:
			pass

		class Class2(Class1):
			pass

		class Class3(Class2):
			pass

		foundClasses = [c for c in AttributeA.GetClasses()]
		foundClassesForC1 = [c for c in AttributeA.GetClasses(predicate=Class1)]
		foundClassesForC2 = [c for c in AttributeA.GetClasses(predicate=Class2)]
		foundClassesForC3 = [c for c in AttributeA.GetClasses(predicate=Class3)]

		self.assertListEqual(foundClasses, [Class1, Class2, Class3])
		self.assertListEqual(foundClassesForC1, [Class1, Class2, Class3])
		self.assertListEqual(foundClassesForC2, [Class2, Class3])
		self.assertListEqual(foundClassesForC3, [Class3])
