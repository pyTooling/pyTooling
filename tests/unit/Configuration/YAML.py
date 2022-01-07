# ==================================================================================================================== #
#             _____           _ _               ____             __ _                       _   _                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | |         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|         #
# |_|    |___/                          |___/                         |___/                                            #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2021-2021 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for YAML based configurations."""
from pathlib import Path
from unittest import TestCase

from pyTooling.Configuration.YAML import Configuration


class ReadingValues(TestCase):
	def test_SimpleString(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		self.assertEqual("string_1", config["value_1"])

		node_1 = config["node_1"]
		self.assertEqual("string_11", node_1["value_11"])
		self.assertEqual("string_12", config["node_1"]["value_12"])

	def test_Root(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		self.assertEqual(4, len(config))
		self.assertTrue("Install" in config)

	def test_Dictionary(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		node_1 = config["node_1"]
		self.assertEqual(2, len(node_1))

		iterator = iter(node_1)
		first = next(iterator)
		self.assertEqual("string_11", first)

		second = next(iterator)
		self.assertEqual("string_12", second)

	def test_Sequence(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		node_2 = config["node_2"]
		self.assertEqual(2, len(node_2))

		iterator = iter(node_2)
		first = next(iterator)
		self.assertEqual("string_2111", node_2[0]["list_211"]["key_2111"])
		self.assertEqual("string_2111", first["list_211"]["key_2111"])

		second = next(iterator)
		self.assertEqual("string_2211", node_2[1]["list_221"]["key_2211"])
		self.assertEqual("string_2211", second["list_221"]["key_2211"])

		with self.assertRaises(StopIteration):
			_ = next(iterator)

	def test_PathExpressionToNode(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		node = config.QueryPath("Install:VendorA:ToolA:2020")
		self.assertEqual(r"C:\VendorA\ToolA\2020", node["InstallDir"])

	def test_PathExpressionToValue(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		value = config.QueryPath("Install:VendorA:ToolA:2020:InstallDir")
		self.assertEqual(r"C:\VendorA\ToolA\2020", value)

	def test_Variables(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		self.assertEqual(r"C:\VendorA\ToolA\2020", config["Install"]["VendorA"]["ToolA"]["2020"]["InstallDir"])
		self.assertEqual(r"C:\VendorA\Tool_A\2021", config["Install"]["VendorA"]["ToolA"]["2021"]["InstallDir"])

		self.assertEqual(r"C:\VendorA\ToolA\2020\bin", config["Install"]["VendorA"]["ToolA"]["2020"]["BinaryDir"])

	def test_NestedVariables(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		self.assertEqual(r"C:\VendorA\ToolA\2020", config["Install"]["VendorA"]["ToolA"]["Defaults"]["InstallDir"])
		self.assertEqual(r"C:\VendorA\ToolA\2020\bin", config["Install"]["VendorA"]["ToolA"]["Defaults"]["BinaryDir"])
