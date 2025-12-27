# ==================================================================================================================== #
#             _____           _ _             _____                   _             _ _   _ ___                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__ _ __ _ __ ___ (_)_ __   __ _| | | | |_ _|                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | | | | || |                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/ |  | | | | | | | | | | (_| | | |_| || |                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|\___/|___|                       #
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
"""pyTooling.TerminalUI"""
from unittest             import TestCase

from pyTooling.TerminalUI import Severity


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Comparison(TestCase):
	def test_Normal(self) -> None:
		normal = Severity.Normal

		self.assertLess(Severity.Debug, normal)
		self.assertLessEqual(Severity.Debug, normal)
		self.assertEqual(Severity.Normal, normal)
		self.assertNotEqual(Severity.DryRun, normal)
		self.assertGreater(Severity.Warning, normal)
		self.assertGreaterEqual(Severity.Warning, normal)


class Exceptions(TestCase):
	def test_Equal(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal == 0

	def test_Unequal(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal != 0

	def test_Less(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal < 0

	def test_LessOrEqual(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal <= 0

	def test_Greater(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal > 0

	def test_GreaterOrEqual(self) -> None:
		with self.assertRaises(TypeError):
			_ = Severity.Normal >= 0
