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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from unittest import TestCase

from pyTooling.Decorators import InheritDocString, OriginalFunction, classproperty

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
	def test_ClassProperty(self):
		class Content:
			_value: int

			def __init__(self, value: int):
				self._value = value

			@property
			def Value(self):
				return self._value

		class Class_1:
			_member = Content(1)

			@classproperty
			def Member(cls):
				"""Class_1.Member"""
				return cls._member

			@Member.setter
			def _Member(cls, value):
				cls._member = value

		class Class_2:
			_member = Content(2)

			@classproperty
			def Member(cls):
				return cls._member

			@Member.setter
			def Member(cls, value):
				cls._member = value

		self.assertEqual(1, Class_1.Member.Value)
		self.assertEqual(2, Class_2.Member.Value)
#		self.assertEqual("Class_1.Member", Class_1.Member.__doc__)

		Class_1.Member = 11
		Class_2.Member = 12

		self.assertEqual(11, Class_1.Member)
		self.assertEqual(12, Class_2.Member)


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
