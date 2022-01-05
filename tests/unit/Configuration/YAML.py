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

	def test_List(self):
		config = Configuration(Path("tests/unit/Configuration/config.yml"))

		node_2 = config["node_2"]
		for item in node_2:
			print(item)

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

		self.assertEqual(r"C:\VendorA\ToolA\2020", config["Install"]["VendorA"]["ToolA"][2020]["InstallDir"])
		self.assertEqual(r"C:\VendorA\Tool_A\2021", config["Install"]["VendorA"]["ToolA"][2021]["InstallDir"])
