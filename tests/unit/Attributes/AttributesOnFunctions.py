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
from unittest     import TestCase

from pytest       import mark

from pyTooling.Attributes import Attribute


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ApplyFunctionAttributes(TestCase):
	def test_SingleFunction(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		def func1():
			pass

		foundFunctions = [c for c in AttributeA.GetFunctions()]

		self.assertListEqual(foundFunctions, [func1])

	def test_MultipleFunctions(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		def func1():
			pass

		@AttributeA()
		def func2():
			pass

		foundFunctions = [c for c in AttributeA.GetFunctions()]

		self.assertListEqual(foundFunctions, [func1, func2])


class ModuleAttribute(Attribute):
	pass


class GlobalAttribute(Attribute):
	pass


@ModuleAttribute()
@GlobalAttribute()
def ModuleFunction():
	pass

	@GlobalAttribute()
	def NestedFunction():
		pass

	return NestedFunction


moduleNestedFunction = ModuleFunction()


class Filtering(TestCase):
	def test_Scope_Module(self) -> None:
		from sys import modules

		foundFunctions = [c for c in ModuleAttribute.GetFunctions()]
		foundModuleFunctions = [c for c in ModuleAttribute.GetFunctions(scope=modules[ModuleFunction.__module__])]

		self.assertListEqual(foundFunctions, [ModuleFunction])
		self.assertListEqual(foundModuleFunctions, [ModuleFunction])

	@mark.skip(reason="Unclear how to get a local scope object.")
	def test_Scope_Local(self) -> None:
		class LocalAttribute(Attribute):
			pass

		@LocalAttribute()
		def LocalFunction():
			pass

			@LocalAttribute()
			def NestedFunction():
				pass

			return NestedFunction

		nestedFunction = LocalFunction()

		# l = locals()

		foundFunctions = [c for c in LocalAttribute.GetFunctions()]
		# foundLocalClasses = [c for c in LocalAttribute.GetClasses(scope=l)]

		self.assertListEqual(foundFunctions, [nestedFunction, LocalFunction])
		# self.assertListEqual(foundLocalClasses, [LocalClass])

	def test_Scope_Nested(self) -> None:
		@GlobalAttribute()
		def LocalFunction():
			pass

			@GlobalAttribute()
			def NestedFunction():
				pass

			return NestedFunction

		nestedFunction = LocalFunction()
		l = locals()

		foundFunctions = [c for c in GlobalAttribute.GetFunctions()]

		self.assertListEqual(foundFunctions, [ModuleFunction, moduleNestedFunction, LocalFunction, nestedFunction])

