# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :func:`pyTooling.Common.getFullyQualifiedName` and :func:`pyTooling.Common.getTypeName`.
"""
from pyTooling.Common  import getFullyQualifiedName, getTypeName
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Outer:
	class Inner:
		pass

	def Method(self) -> None:
		"""Method for name tests."""


def function() -> None:
	"""Function for name tests."""


class FullyQualifiedName(Testcase):
	def test_Instance(self) -> None:
		self.assertEqual(f"{__name__}.Outer", getFullyQualifiedName(Outer()))

	def test_Class(self) -> None:
		self.assertEqual(f"{__name__}.Outer", getFullyQualifiedName(Outer))

	def test_NestedClass(self) -> None:
		self.assertEqual(f"{__name__}.Outer.Inner", getFullyQualifiedName(Outer.Inner))
		self.assertEqual(f"{__name__}.Outer.Inner", getFullyQualifiedName(Outer.Inner()))

	def test_Function(self) -> None:
		self.assertEqual(f"{__name__}.function", getFullyQualifiedName(function))
		self.assertEqual(f"{__name__}.Outer.Method", getFullyQualifiedName(Outer.Method))

	def test_Builtin(self) -> None:
		self.assertEqual("int", getFullyQualifiedName(5))
		self.assertEqual("int", getFullyQualifiedName(int))
		self.assertEqual("NoneType", getFullyQualifiedName(None))


class TypeName(Testcase):
	def test_Instance(self) -> None:
		self.assertEqual("Outer", getTypeName(Outer()))

	def test_Class(self) -> None:
		self.assertEqual("Outer", getTypeName(Outer))

	def test_NestedClass(self) -> None:
		self.assertEqual("Inner", getTypeName(Outer.Inner))
		self.assertEqual("Inner", getTypeName(Outer.Inner()))

	def test_Function(self) -> None:
		self.assertEqual("function", getTypeName(function))
		self.assertEqual("Method", getTypeName(Outer.Method))

	def test_Builtin(self) -> None:
		self.assertEqual("int", getTypeName(5))
		self.assertEqual("int", getTypeName(int))
		self.assertEqual("NoneType", getTypeName(None))
