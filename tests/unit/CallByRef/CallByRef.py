# ==================================================================================================================== #
#             _____           _ _               ____      _ _ ____        ____       __                                #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _| | | __ ) _   _|  _ \ ___ / _|                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | | |  _ \| | | | |_) / _ \ |_                                #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | | | |_) | |_| |  _ <  __/  _|                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|_|____/ \__, |_| \_\___|_|                                 #
# |_|    |___/                          |___/                       |___/                                              #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`PyTooling.CallByRef`.
"""
from unittest            import TestCase

from pyTooling.CallByRef import CallByRefParam, CallByRefBoolParam, CallByRefIntParam


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def func1(param: CallByRefParam) -> None:
	param <<= (3, 4)


def func2(param: CallByRefBoolParam, value: bool = True) -> None:
	param <<= value


def assign_42(param: CallByRefIntParam, value: int = 42) -> None:
	param <<= value


class Any(TestCase):
	ref: CallByRefParam = CallByRefParam()

	def setUp(self) -> None:
		func1(self.ref)

	def test_Value(self) -> None:
		self.assertTupleEqual((3, 4), self.ref.Value)

	def test_Equal(self) -> None:
		self.assertTrue(self.ref == (3, 4))

	def test_Unequal(self) -> None:
		self.assertTrue(self.ref != (4, 3))


class Boolean(TestCase):
	ref: CallByRefBoolParam = CallByRefBoolParam()

	def setUp(self) -> None:
		func2(self.ref)

	def test_Value(self) -> None:
		self.assertTrue(self.ref.Value)

	def test_Equal(self) -> None:
		self.assertTrue(self.ref == True)

		with self.assertRaises(TypeError):
			_ = self.ref == "str"

	def test_Unequal(self) -> None:
		self.assertTrue(self.ref != False)

		with self.assertRaises(TypeError):
			_ = self.ref != "str"

	def test_TypeConvertToBool(self) -> None:
		self.assertTrue(bool(self.ref))

	def test_TypeConvertToInt(self) -> None:
		self.assertEqual(1, int(self.ref))


class Integer(TestCase):
	ref: CallByRefIntParam = CallByRefIntParam()

	def test_Value(self) -> None:
		assign_42(self.ref)
		self.assertEqual(42, self.ref.Value)

	def test_Negate(self) -> None:
		assign_42(self.ref)
		self.assertEqual(-42, -self.ref)

	def test_Positive(self) -> None:
		assign_42(self.ref, -42)
		self.assertEqual(-42, +self.ref)

	def test_Invert(self) -> None:
		assign_42(self.ref, 1)
		self.assertEqual(-2, ~self.ref)

	def test_GeaterThanOrEqual(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref >= 40)

		with self.assertRaises(TypeError):
			_ = self.ref >= "str"

	def test_GreaterThan(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref > 41)

		with self.assertRaises(TypeError):
			_ = self.ref > "str"

	def test_Equal(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref == 42)

		with self.assertRaises(TypeError):
			_ = self.ref == "str"

	def test_Unequal(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref != 43)

		with self.assertRaises(TypeError):
			_ = self.ref != "str"

	def test_LessThan(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref < 44)

		with self.assertRaises(TypeError):
			_ = self.ref < "str"

	def test_LessThanOrEqual(self) -> None:
		assign_42(self.ref)
		self.assertTrue(self.ref <= 45)

		with self.assertRaises(TypeError):
			_ = self.ref <= "str"

	def test_Addition(self) -> None:
		assign_42(self.ref)
		self.assertEqual(43, self.ref + 1)

		with self.assertRaises(TypeError):
			self.ref + "str"

	def test_Subtraction(self) -> None:
		assign_42(self.ref)
		self.assertEqual(41, self.ref - 1)

		with self.assertRaises(TypeError):
			self.ref - "str"

	def test_Multiplication(self) -> None:
		assign_42(self.ref)
		self.assertEqual(42, self.ref * 1)

		with self.assertRaises(TypeError):
			self.ref * "str"

	def test_Power(self) -> None:
		assign_42(self.ref)
		self.assertEqual(42, self.ref ** 1)

		with self.assertRaises(TypeError):
			self.ref ** "str"

	def test_Division(self) -> None:
		assign_42(self.ref)
		self.assertEqual(42, self.ref / 1)

		with self.assertRaises(TypeError):
			self.ref / "str"

	def test_FloorDivision(self) -> None:
		assign_42(self.ref)
		self.assertEqual(42, self.ref // 1)

		with self.assertRaises(TypeError):
			self.ref // "str"

	def test_Modulo(self) -> None:
		assign_42(self.ref)
		self.assertEqual(0, self.ref % 2)

		with self.assertRaises(TypeError):
			self.ref % "str"

	def test_And(self) -> None:
		assign_42(self.ref)
		self.assertEqual(2, self.ref & 2)

		with self.assertRaises(TypeError):
			self.ref & "str"

	def test_Or(self) -> None:
		assign_42(self.ref)
		self.assertEqual(43, self.ref | 1)

		with self.assertRaises(TypeError):
			self.ref | "str"

	def test_Xor(self) -> None:
		assign_42(self.ref)
		self.assertEqual(40, self.ref ^ 2)

		with self.assertRaises(TypeError):
			self.ref ^ "str"

	def test_Increment(self) -> None:
		assign_42(self.ref)
		self.ref += 1
		self.assertEqual(43, self.ref)

		with self.assertRaises(TypeError):
			self.ref += "str"

	def test_Decrement(self) -> None:
		assign_42(self.ref)
		self.ref -= 1
		self.assertEqual(41, self.ref)

		with self.assertRaises(TypeError):
			self.ref -= "str"

	def test_InplaceMultiplication(self) -> None:
		assign_42(self.ref)
		self.ref *= 1
		self.assertEqual(42, self.ref)

		with self.assertRaises(TypeError):
			self.ref *= "str"

	def test_InplacePower(self) -> None:
		assign_42(self.ref)
		self.ref **= 1
		self.assertEqual(42, self.ref)

		with self.assertRaises(TypeError):
			self.ref **= "str"

	def test_InplaceDivision(self) -> None:
		assign_42(self.ref)
		self.ref /= 1
		self.assertEqual(42, self.ref)

		with self.assertRaises(TypeError):
			self.ref /= "str"

	def test_InplaceFloorDivision(self) -> None:
		assign_42(self.ref)
		self.ref //= 1
		self.assertEqual(42, self.ref)

		with self.assertRaises(TypeError):
			self.ref //= "str"

	def test_InplaceModulo(self) -> None:
		assign_42(self.ref)
		self.ref %= 2
		self.assertEqual(0, self.ref)

		with self.assertRaises(TypeError):
			self.ref %= "str"

	def test_InplaceAnd(self) -> None:
		assign_42(self.ref)
		self.ref &= 2
		self.assertEqual(2, self.ref)

		with self.assertRaises(TypeError):
			self.ref &= "str"

	def test_InplaceOr(self) -> None:
		assign_42(self.ref)
		self.ref |= 1
		self.assertEqual(43, self.ref)

		with self.assertRaises(TypeError):
			self.ref |= "str"

	def test_InplaceXor(self) -> None:
		assign_42(self.ref)
		self.ref ^= 2
		self.assertEqual(40, self.ref)

		with self.assertRaises(TypeError):
			self.ref ^= "str"

	def test_TypeConvertToBool(self) -> None:
		self.assertTrue(bool(self.ref))

	def test_TypeConvertToInt(self) -> None:
		self.assertEqual(42, int(self.ref))
