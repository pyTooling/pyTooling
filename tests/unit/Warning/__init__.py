# ==================================================================================================================== #
#             _____           _ _           __        __               _                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \      / /_ _ _ __ _ __ (_)_ __   __ _                                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ /\ / / _` | '__| '_ \| | '_ \ / _` |                                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V  V / (_| | |  | | | | | | | | (_| |                                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/\_/ \__,_|_|  |_| |_|_|_| |_|\__, |                                  #
# |_|    |___/                          |___/                                  |___/                                   #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from typing   import List
from unittest import TestCase

from pyTooling.Warning import WarningCollector, Warning, CriticalWarning
from pyTooling.Warning import UnhandledExceptionException, UnhandledCriticalWarningException


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ClassA:
	_x: object

	def __init__(self, x: object) -> None:
		self._x = x

	def methA_RaiseWarning(self) -> None:
		WarningCollector.Raise(Warning("Warning from ClassA.methA_RaiseWarning"))

	def methA_RaiseCriticalWarning(self) -> None:
		WarningCollector.Raise(CriticalWarning("CriticalWarning from ClassA.methA_RaiseCriticalWarning"))

	def methA_RaiseException(self) -> None:
		WarningCollector.Raise(Exception("Exception from ClassA.methA_RaiseException"))


class ClassB:
	_a: ClassA

	def __init__(self, a: ClassA) -> None:
		self._a = a

	def methB(self) -> None:
		self._a.methA_RaiseException()


class ClassC:
	_b: ClassB

	def __init__(self, b: ClassB) -> None:
		self._b = b

	def methC(self) -> None:
		self._b.methB()


class Handler:
	_c: ClassC
	_warnings: List

	def __init__(self, c: ClassC) -> None:
		self._c = c
		self._warnings = []

	def meth(self) -> None:
		with WarningCollector(self._warnings) as warning:
			self._c.methC()


class NoWarningCollector(TestCase):
	def test_RaiseWarning(self) -> None:
		a = ClassA("none")
		a.methA_RaiseWarning()

	def test_RaiseCriticalWarning(self) -> None:
		a = ClassA("none")
		with self.assertRaises(UnhandledCriticalWarningException) as ex:
			a.methA_RaiseCriticalWarning()

		self.assertEqual("Unhandled Critical Warning: CriticalWarning from ClassA.methA_RaiseCriticalWarning", str(ex.exception))

	def test_RaiseException(self) -> None:
		a = ClassA("none")
		with self.assertRaises(UnhandledExceptionException) as ex:
			a.methA_RaiseException()

		self.assertEqual("Unhandled Exception: Exception from ClassA.methA_RaiseException", str(ex.exception))


class WarningCollection(TestCase):
	def test_WarningCollector_NoList(self) -> None:
		a = ClassA("list")
		with WarningCollector() as warning:
			a.methA_RaiseException()

		self.assertEqual(1, len(warning))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warning[0]))

	def test_WarningCollector_List(self) -> None:
		warnings = []

		a = ClassA("list")
		with WarningCollector(warnings) as warning:
			a.methA_RaiseException()

		self.assertEqual(1, len(warnings))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warnings[0]))

	def test_WarningCollector_Print(self) -> None:
		print()

		message = ""
		def func(warning: Warning) -> bool:
			nonlocal message
			message = str(warning)
			print(message)

			return False

		a = ClassA("print")
		with WarningCollector(handler=func) as warning:
			a.methA_RaiseException()

		self.assertEqual("Exception from ClassA.methA_RaiseException", message)

	def test_WarningCollector_Abort(self) -> None:
		print()

		message = ""
		def func(warning: Warning) -> bool:
			nonlocal message
			message = str(warning)
			print(message)

			return True

		a = ClassA("abort")
		with self.assertRaises(Exception) as ex:
			with WarningCollector(handler=func) as warning:
				a.methA_RaiseException()

		self.assertEqual("Exception from ClassA.methA_RaiseException", message)
		self.assertEqual("Warning: Exception from ClassA.methA_RaiseException", str(ex.exception))


class CallStack(TestCase):
	def test_Level_1(self) -> None:
		warnings = []

		a = ClassA(1)
		with WarningCollector(warnings) as warning:
			a.methA_RaiseException()

		self.assertEqual(1, len(warnings))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warnings[0]))

	def test_Level_2(self) -> None:
		warnings = []

		a = ClassA(2)
		b = ClassB(a)
		with WarningCollector(warnings) as warning:
			b.methB()

		self.assertEqual(1, len(warnings))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warnings[0]))

	def test_Level_3(self) -> None:
		warnings = []

		a = ClassA(3)
		b = ClassB(a)
		c = ClassC(b)
		with WarningCollector(warnings) as warning:
			c.methC()

		self.assertEqual(1, len(warnings))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warnings[0]))

	def test_Nested(self) -> None:
		a = ClassA(1)
		with WarningCollector() as warning1:
			with WarningCollector() as warning2:
				a.methA_RaiseException()

		self.assertIs(warning1, warning2.Parent)
		self.assertEqual(1, len(warning2))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(warning2[0]))


class Catch(TestCase):
	def test_Inner(self) -> None:
		warnings = []

		a = ClassA(3)
		b = ClassB(a)
		c = ClassC(b)
		h = Handler(c)
		with WarningCollector(warnings) as warning:
			h.meth()

		self.assertEqual(0, len(warnings))
		self.assertEqual(1, len(h._warnings))
		self.assertEqual("Exception from ClassA.methA_RaiseException", str(h._warnings[0]))
