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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for Decorators."""
from typing import Union
from unittest import TestCase

from pyTooling.Decorators import InheritDocString, OriginalFunction, classproperty, myproperty


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class InheritDocStrings(TestCase):
	def test_InheritDocString(self) -> None:
		class Class1:
			def method(self):
				"""Method's doc-string."""

		class Class2(Class1):
			@InheritDocString(Class1)
			def method(self):
				pass

		self.assertEqual(Class1.method.__doc__, Class2.method.__doc__)


class Descriptors(TestCase):
	def test_Property(self):
		class Class_1:
			_member: int

			def __init__(self):
				self._member = 1

			@myproperty
			def Member(self) -> int:
				return self._member

			@Member.setter
			def Member(self, value: int) -> None:
				self._member = value

		c = Class_1()

		self.assertEqual(1, c.Member)
		c.Member = "2"
		self.assertEqual("2", c.Member)

	def test_ClassProperty(self):
		class Content:
			_value: int

			def __init__(self, value: int):
				self._value = value

			@property
			def Value(self) -> int:
				return self._value

			@Value.setter
			def Value(self, value: int) -> None:
				self._value = value

		class Class_1:
			_member: int = 1

			@classproperty
			def Member(cls) -> int:
				"""Class_1.Member"""
				return cls._member

			@Member.setter
			def Member(cls, value: int) -> None:
				cls._member = value

		class Class_2:
			_member: Union[Content, int] = Content(2)

			@classproperty
			def Member(cls) -> Union[Content, int]:
				"""Class_2.Member"""
				return cls._member

			@Member.setter
			def Member(cls, value: int):
				cls._member.Value = value

		c = Class_1()
		a = c.Member

		self.assertEqual(1, Class_1.Member)
		Class_1.Member = 11
		self.assertEqual(11, Class_1.Member)
		self.assertEqual(11, Class_1._member)
#		self.assertEqual("Class_1.Member", Class_1.Member.__doc__)

		self.assertEqual(2, Class_2.Member.Value)
		Class_2.Member = 12
		self.assertEqual(12, Class_2.Member)
		self.assertEqual(12, Class_2._member.Value)


class Original(TestCase):
	def test_OriginalFunction(self) -> None:
		def func():
			return 0

		oldfunc = func
		@OriginalFunction(oldfunc)
		def wrapper():
			return oldfunc() + 1

		func = wrapper

		self.assertEqual(1, func())
		self.assertEqual(0, func.__orig_func__())
