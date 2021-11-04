# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Testing the pyCallBy module
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
"""
pyTooling.CallBy
################

:copyright: Copyright 2007-2021 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from unittest     import TestCase

from pyTooling.CallBy import CallByRefParam, CallByRefBoolParam, CallByRefIntParam


if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)

def func1(param : CallByRefParam):
	param <<= (3, 4)

def func2(param : CallByRefBoolParam, value : bool = True):
	param <<= value

def assign_42(param : CallByRefIntParam, value : int = 42):
	param <<= value

class CallByReference_AnyParam(TestCase):
	ref : CallByRefParam = CallByRefParam()

	def setUp(self) -> None:
		func1(self.ref)

	def test_Value(self):
		self.assertTupleEqual(self.ref.value, (3, 4))

	def test_Equal(self):
		self.assertTrue(self.ref == (3, 4))

	def test_Unequal(self):
		self.assertTrue(self.ref != (4, 3))


class CallByReference_BoolParam(TestCase):
	ref : CallByRefBoolParam = CallByRefBoolParam()

	def setUp(self) -> None:
		func2(self.ref)

	def test_Value(self):
		self.assertTrue(self.ref.value)

	def test_Equal(self):
		self.assertTrue(self.ref == True)

	def test_Unequal(self):
		self.assertTrue(self.ref != False)


	def test_TypeConvertToBool(self):
		self.assertTrue(bool(self.ref))

	def test_TypeConvertToInt(self):
		self.assertEqual(int(self.ref), 1)


class CallByReference_IntParam(TestCase):
	ref : CallByRefIntParam = CallByRefIntParam()

	def test_Value(self):
		assign_42(self.ref)
		self.assertEqual(self.ref.value, 42)

	def test_Negate(self):
		assign_42(self.ref)
		self.assertEqual(-self.ref, -42)

	def test_Positive(self):
		assign_42(self.ref, -42)
		self.assertEqual(+self.ref, -42)

	def test_Invert(self):
		assign_42(self.ref, 1)
		self.assertEqual(~self.ref, -2)


	def test_GeaterThanOrEqual(self):
		assign_42(self.ref)
		self.assertTrue(self.ref >= 40)

	def test_GreaterThan(self):
		assign_42(self.ref)
		self.assertTrue(self.ref >  41)

	def test_Equal(self):
		assign_42(self.ref)
		self.assertTrue(self.ref == 42)

	def test_Unequal(self):
		assign_42(self.ref)
		self.assertTrue(self.ref != 43)

	def test_LessThan(self):
		assign_42(self.ref)
		self.assertTrue(self.ref <  44)

	def test_LessThanOrEqual(self):
		assign_42(self.ref)
		self.assertTrue(self.ref <= 45)


	def test_Addition(self):
		assign_42(self.ref)
		self.assertEqual(self.ref + 1, 43)

	def test_Subtraction(self):
		assign_42(self.ref)
		self.assertEqual(self.ref - 1, 41)

	def test_Multiplication(self):
		assign_42(self.ref)
		self.assertEqual(self.ref * 1, 42)

	def test_Power(self):
		assign_42(self.ref)
		self.assertEqual(self.ref ** 1, 42)

	def test_Division(self):
		assign_42(self.ref)
		self.assertEqual(self.ref / 1, 42)

	def test_FloorDivision(self):
		assign_42(self.ref)
		self.assertEqual(self.ref // 1, 42)

	def test_Modulo(self):
		assign_42(self.ref)
		self.assertEqual(self.ref % 2, 0)


	def test_Increment(self):
		assign_42(self.ref)
		self.ref += 1
		self.assertEqual(self.ref, 43)

	def test_Decrement(self):
		assign_42(self.ref)
		self.ref -= 1
		self.assertEqual(self.ref, 41)

	def test_InplaceMultiplication(self):
		assign_42(self.ref)
		self.ref *= 1
		self.assertEqual(self.ref, 42)

	def test_InplacePower(self):
		assign_42(self.ref)
		self.ref **= 1
		self.assertEqual(self.ref, 42)

	def test_InplaceDivision(self):
		assign_42(self.ref)
		self.ref /= 1
		self.assertEqual(self.ref, 42)

	def test_InplaceFloorDivision(self):
		assign_42(self.ref)
		self.ref //= 1
		self.assertEqual(self.ref, 42)

	def test_InplaceModulo(self):
		assign_42(self.ref)
		self.ref %= 2
		self.assertEqual(self.ref, 0)


	def test_TypeConvertToBool(self):
		self.assertTrue(bool(self.ref))

	def test_TypeConvertToInt(self):
		self.assertEqual(int(self.ref), 42)
