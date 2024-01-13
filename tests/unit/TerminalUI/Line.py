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
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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

from pyTooling.TerminalUI import Line, Severity


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Default(self) -> None:
		line = Line("Message")

		self.assertEqual("Message", line.Message)
		self.assertEqual(Severity.Normal, line.Severity)
		self.assertEqual(0, line.Indent)
		self.assertEqual("Message", str(line))

	def test_Severity(self) -> None:
		line = Line("Message", Severity.Debug)

		self.assertEqual(Severity.Debug, line.Severity)

	def test_Indentation(self) -> None:
		line = Line("Message", indent=2)

		self.assertEqual(2, line.Indent)


class Indentation(TestCase):
	def test_IndentationChange(self) -> None:
		lines = [
			Line("Line 1"),
			Line("Line 1.1", indent=1),
			Line("Line 2"),
		]

		for line in lines:
			line.IndentBy(1)

		self.assertListEqual([1,2,1], [line.Indent for line in lines])
