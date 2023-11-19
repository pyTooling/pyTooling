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

from pyTooling.Attributes import Attribute


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
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


class ApplyFunctionAttributes_1(TestCase):
	def test_SingleFunction(self) -> None:
		class AttributeA(Attribute):
			pass

		@AttributeA()
		def func1():
			pass

		foundFunctions = [c for c in AttributeA.GetFunctions()]

		self.assertListEqual(foundFunctions, [func1])


class ApplyFunctionAttributes_2(TestCase):
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
