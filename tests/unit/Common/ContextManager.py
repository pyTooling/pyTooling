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
Unit tests for :class:`~pyTooling.Common.ChangeDirectory`.
"""
from pathlib  import Path
from unittest import TestCase

from pyTooling.Common import ChangeDirectory as ChangeDir

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ChangeDirectory(TestCase):
	def test_ChangeDirectory(self) -> None:
		before = Path.cwd()
		path = Path("tests/unit/Common")

		with ChangeDir(path) as p:
			self.assertEqual(before / path, Path.cwd())
			self.assertEqual(before / path, p)

		self.assertEqual(before, Path.cwd())

	def test_DoubleChangeDirectory(self) -> None:
		before = Path.cwd()
		outerPath = Path("tests/unit/Common")
		innerPath = Path("../Attributes")

		with ChangeDir(outerPath) as op:
			self.assertEqual((before / outerPath).resolve(), Path.cwd())
			self.assertEqual((before / outerPath).resolve(), op)

			with ChangeDir(innerPath) as ip:
				self.assertEqual((before / outerPath / innerPath).resolve(), Path.cwd())
				self.assertEqual((before / outerPath / innerPath).resolve(), ip)

			self.assertEqual((before / outerPath).resolve(), Path.cwd())

		self.assertEqual(before, Path.cwd())
