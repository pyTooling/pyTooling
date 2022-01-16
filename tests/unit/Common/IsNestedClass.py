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
"""
Unit tests for :func:`isnestedclass`.

:copyright: Copyright 2021-2022 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from unittest import TestCase

from pyTooling.Common import isnestedclass


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Class_1:
	class Class_11:
		class Class_111:
			pass


class Class_1_1(Class_1):
	pass


class Class_2:
	pass


class IsNestedClass(TestCase):
	def test_SameClass(self) -> None:
		self.assertFalse(isnestedclass(Class_1, Class_1))

	def test_NestedClass(self) -> None:
		self.assertTrue(isnestedclass(Class_1.Class_11, Class_1))

	def test_DerivedClass(self) -> None:
		self.assertTrue(isnestedclass(Class_1_1.Class_11, Class_1))
		self.assertTrue(isnestedclass(Class_1_1.Class_11, Class_1_1))

	def test_DoubleNestedClass(self) -> None:
		self.assertFalse(isnestedclass(Class_1.Class_11.Class_111, Class_1))

	def test_ParallelClass(self) -> None:
		self.assertFalse(isnestedclass(Class_2, Class_1))
