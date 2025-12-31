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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for class :class:`pyTooling.MetaClasses.ExtendedType`.
"""
from unittest              import TestCase

from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class WithoutSlots(TestCase):
	def test_NoInitValue_NoDunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

		with self.assertRaises(AttributeError, msg="Field '_data0' should not exist on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

		inst = Base()

		with self.assertRaises(AttributeError, msg="Field '_data0' shouldn't be initialized on instance."):
			_ = inst._data0

		inst._data0 = 1
		self.assertEqual(1, inst._data0)

	def test_NoInitValue_DunderInit_ClassCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		with self.assertRaises(AttributeError, msg="Field '_data0' should not exist on class 'Base'."):
			_ = Base._data0

	def test_NoInitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

			def __init__(self) -> None:
				pass

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_InitOverwrite_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType):
			_data0: int = 1

			def __init__(self) -> None:
				self._data0 = 5

		inst = Base()

		self.assertEqual(5, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)


class WithSlots(TestCase):
	def test_NoInitValue_NoDunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int

		inst = Base()

		with self.assertRaises(AttributeError, msg="Field '_data0' shouldn't be initialized on instance."):
			_ = inst._data0

		inst._data0 = 1
		self.assertEqual(1, inst._data0)

	def test_NoInitValue_DunderInit_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int

			def __init__(self) -> None:
				self._data0 = 1

		inst = Base()

		self.assertEqual(1, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)

	def test_InitValue_InitOverwrite_InstCheck(self) -> None:
		class Base(metaclass=ExtendedType, slots=True):
			_data0: int = 1

			def __init__(self) -> None:
				self._data0 = 5

		inst = Base()

		self.assertEqual(5, inst._data0)
		inst._data0 = 2
		self.assertEqual(2, inst._data0)
