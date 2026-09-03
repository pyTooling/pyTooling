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
# Copyright 2021-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.Configuration.JSON`: reading values through the node API and the errors
raised for a missing key or a wrong type.
"""
from pathlib  import Path

from pyTooling.Configuration      import InterpolationError, KeyNotFoundError, PathExpressionError
from pyTooling.Configuration      import UnsupportedValueTypeError
from pyTooling.Exceptions         import ConfigurationError
from pyTooling.Configuration.JSON import Configuration
from pyTooling.Testing            import Testcase


class ReadingValues(Testcase):
	def test_SimpleString(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual("string_1", config["value_1"])

		node_1 = config["node_1"]
		self.assertEqual("string_11", node_1["value_11"])
		self.assertEqual("string_12", config["node_1"]["value_12"])

	def test_Root(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(4, len(config))
		self.assertTrue("Install" in config)

	def test_Dictionary(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		node_1 = config["node_1"]
		self.assertEqual(2, len(node_1))

		iterator = iter(node_1)
		first = next(iterator)
		self.assertEqual("string_11", first)

		second = next(iterator)
		self.assertEqual("string_12", second)

	def test_Sequence(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

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

	def test_PathExpressionToNode(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		node = config.QueryPath("Install:VendorA:ToolA:2020")
		self.assertEqual(r"C:\VendorA\ToolA\2020", node["InstallDir"])

	def test_PathExpressionToValue(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		value = config.QueryPath("Install:VendorA:ToolA:2020:InstallDir")
		self.assertEqual(r"C:\VendorA\ToolA\2020", value)

	def test_Variables(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(r"C:\VendorA\ToolA\2020", config["Install"]["VendorA"]["ToolA"]["2020"]["InstallDir"])
		self.assertEqual(r"C:\VendorA\Tool_A\2021.10", config["Install"]["VendorA"]["ToolA"]["2021.10"]["InstallDir"])

		self.assertEqual(r"C:\VendorA\ToolA\2020\bin", config["Install"]["VendorA"]["ToolA"]["2020"]["BinaryDir"])

	def test_NestedVariables(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(r"C:\VendorA\ToolA\2020", config["Install"]["VendorA"]["ToolA"]["Defaults"]["InstallDir"])
		self.assertEqual(r"C:\VendorA\ToolA\2020\bin", config["Install"]["VendorA"]["ToolA"]["Defaults"]["BinaryDir"])


class Errors(Testcase):
	_configFile = Path("tests/data/Configuration/errors.json")

	def test_UnknownKeyInDictionary(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(KeyNotFoundError) as context:
			_ = config["dictionary"]["key_3"]

		self.assertIn("Key 'key_3' not found in node 'dictionary'.", str(context.exception))
		self.assertIn("Available keys: 'key_1', 'key_2'.", context.exception.__notes__)

	def test_IndexOutOfRangeInSequence(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(KeyNotFoundError) as context:
			_ = config["sequence"][2]

		self.assertIn("Key '2' not found in node 'sequence'.", str(context.exception))
		self.assertIn("Node 'sequence' is a sequence with indices 0..1.", context.exception.__notes__)

	def test_UnknownKeyInEmptyDictionary(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(KeyNotFoundError) as context:
			_ = config["emptyDictionary"]["key_1"]

		self.assertIn("Node 'emptyDictionary' is an empty dictionary.", context.exception.__notes__)

	def test_IndexInEmptySequence(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(KeyNotFoundError) as context:
			_ = config["emptySequence"][0]

		self.assertIn("Node 'emptySequence' is an empty sequence.", context.exception.__notes__)

	def test_UnsupportedValueType(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(UnsupportedValueTypeError) as context:
			_ = config["nullValue"]

		self.assertIn("Unsupported type 'NoneType' for key 'nullValue'", str(context.exception))

	def test_UnclosedVariableReference(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(InterpolationError) as context:
			_ = config["unclosedVariable"]

		self.assertIn("Unclosed variable reference in value '${unclosed'.", str(context.exception))

	def test_DanglingDollarSign(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(InterpolationError) as context:
			_ = config["danglingDollar"]

		self.assertIn("Dangling '$' at the end of value 'prefix$'.", str(context.exception))

	def test_PathExpressionResolvingToDictionary(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(PathExpressionError) as context:
			_ = config["dictionaryReference"]

		self.assertIn("resolves to a dictionary, not to a value", str(context.exception))

	def test_PathExpressionAboveRoot(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(PathExpressionError) as context:
			_ = config["aboveRoot"]

		self.assertIn("Path expression '..:dictionary' navigates beyond the root node.", str(context.exception))
		self.assertIn("Element '..' was applied to the root node, which has no parent node.", context.exception.__notes__)

	def test_QueryPathAboveRoot(self) -> None:
		config = Configuration(self._configFile)

		with self.assertRaises(PathExpressionError) as context:
			_ = config.QueryPath("..:dictionary")

		self.assertIn("Path expression '..:dictionary' navigates beyond the root node.", str(context.exception))


class RootNode(Testcase):
	"""The root node is its own root and its own parent, and every node below it points at that same root."""

	_configFile = Path("tests/data/Configuration/config.json")

	def test_RootIsItsOwnRootAndParent(self) -> None:
		config = Configuration(self._configFile)

		self.assertIs(config, config._root)
		self.assertIs(config, config._parent)

	def test_NestedNodesReferenceTheRealRoot(self) -> None:
		config = Configuration(self._configFile)

		node = config["Install"]["VendorA"]["ToolA"]

		self.assertIs(config, node._root)
		self.assertIs(config["Install"]["VendorA"], node._parent)

	def test_ConfigFileIsPreserved(self) -> None:
		config = Configuration(self._configFile)

		self.assertEqual(self._configFile, config.ConfigFile)


class IteratingDictionaries(Testcase):
	"""Iterating a dictionary node by keys, by values and by pairs."""

	def test_IterateKeys(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(["value_11", "value_12"], list(config["node_1"].IterateKeys()))

	def test_IterateValues(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(["string_11", "string_12"], list(config["node_1"].IterateValues()))

	def test_IterateItems(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(
			[("value_11", "string_11"), ("value_12", "string_12")],
			list(config["node_1"].IterateItems())
		)

	def test_IterateValuesMatchesPlainIteration(self) -> None:
		"""``for value in node`` was the only walk before, and it still yields the same values."""
		config = Configuration(Path("tests/data/Configuration/config.json"))
		node = config["node_1"]

		self.assertEqual(list(node), list(node.IterateValues()))

	def test_KeysOfAScalarMapping(self) -> None:
		"""
		The keys of a mapping of scalars were unreachable before.

		Plain iteration yields child nodes for mapping values but bare values for scalar ones, so a table keyed by
		something meaningful - a version specifier, a package name - could not be read back.
		"""
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(["value_11", "value_12"], [key for key, _ in config["node_1"].IterateItems()])

	def test_NestedNodesAreStillNodes(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		for key, value in config["Install"].IterateItems():
			self.assertIsInstance(key, str)
			self.assertEqual(value, config["Install"][key])


class MappingProtocol(Testcase):
	"""A dictionary node answers the methods :class:`dict` answers."""

	def test_Keys(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(("value_11", "value_12"), config["node_1"].keys())

	def test_Values(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(("string_11", "string_12"), config["node_1"].values())

	def test_Items(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual(
			(("value_11", "string_11"), ("value_12", "string_12")),
			config["node_1"].items()
		)

	def test_TheyMatchTheIterators(self) -> None:
		""":meth:`keys`, :meth:`values` and :meth:`items` are their ``Iterate***`` counterparts, materialized."""
		node = Configuration(Path("tests/data/Configuration/config.json"))["node_1"]

		self.assertEqual(tuple(node.IterateKeys()), node.keys())
		self.assertEqual(tuple(node.IterateValues()), node.values())
		self.assertEqual(tuple(node.IterateItems()), node.items())

	def test_Get(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual("string_11", config["node_1"].get("value_11"))

	def test_GetReturnsTheDefaultForAnAbsentKey(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertIsNone(config["node_1"].get("value_13"))
		self.assertEqual("fallback", config["node_1"].get("value_13", "fallback"))

	def test_GetDoesNotRaiseWhereGetitemDoes(self) -> None:
		"""``node[absent]`` raises; ``node.get(absent)`` is the way to ask without handling it."""
		config = Configuration(Path("tests/data/Configuration/config.json"))

		with self.assertRaises(KeyError):
			config["node_1"]["value_13"]

		self.assertIsNone(config["node_1"].get("value_13"))

	def test_ANodeConvertsToADict(self) -> None:
		"""``dict()`` looks for a ``keys`` method to decide something is a mapping, which is why this works."""
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual({"value_11": "string_11", "value_12": "string_12"}, dict(config["node_1"]))

	def test_ANodeUnpacksIntoADict(self) -> None:
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertEqual({"value_11": "string_11", "value_12": "string_12"}, {**config["node_1"]})

	def test_TheRootNodeIsAMappingToo(self) -> None:
		"""The root derives from the dictionary node, so a whole document reads like one."""
		config = Configuration(Path("tests/data/Configuration/config.json"))

		self.assertIn("node_1", config.keys())
		self.assertEqual("string_1", config.get("value_1"))
		self.assertEqual("fallback", config.get("absent", "fallback"))


class SequenceProtocol(Testcase):
	"""A sequence node answers the methods :class:`list` answers."""

	def test_Index(self) -> None:
		sequence = Configuration(Path("tests/data/Configuration/config.json"))["node_2"]

		self.assertEqual(0, sequence.index(sequence[0]))
		self.assertEqual(1, sequence.index(sequence[1]))

	def test_IndexHonoursStartAndStop(self) -> None:
		sequence = Configuration(Path("tests/data/Configuration/config.json"))["node_2"]

		self.assertEqual(1, sequence.index(sequence[1], 1))

		with self.assertRaises(ValueError):
			sequence.index(sequence[1], 0, 1)

	def test_IndexRaisesForAnAbsentValue(self) -> None:
		sequence = Configuration(Path("tests/data/Configuration/config.json"))["node_2"]

		with self.assertRaises(ValueError):
			sequence.index("not in this sequence")

	def test_Count(self) -> None:
		sequence = Configuration(Path("tests/data/Configuration/config.json"))["node_2"]

		self.assertEqual(1, sequence.count(sequence[0]))
		self.assertEqual(0, sequence.count("not in this sequence"))

class DocumentRoot(Testcase):
	"""What a configuration accepts as a document, which both backends answer alike."""

	def test_AnEmptyFileIsAnEmptyConfiguration(self) -> None:
		"""A file with no content states no settings. It is valid YAML; in JSON it is not, and it answers the same."""
		config = Configuration(Path("tests/data/Configuration/empty.json"))

		self.assertEqual(0, len(config))
		self.assertEqual((), config.keys())
		self.assertEqual({}, dict(config))

	def test_ANullDocumentIsAnEmptyConfiguration(self) -> None:
		config = Configuration(Path("tests/data/Configuration/null.json"))

		self.assertEqual(0, len(config))

	def test_AnAbsentKeyReadsAsAbsentOnAnEmptyConfiguration(self) -> None:
		"""Which is the point - every node used to fail on 'NoneType has no attribute keys'."""
		config = Configuration(Path("tests/data/Configuration/empty.json"))

		self.assertIsNone(config.get("packages", None))
		self.assertEqual("fallback", config.get("packages", "fallback"))
		self.assertNotIn("packages", config)

	def test_AScalarRootIsRejected(self) -> None:
		"""A configuration's root is a mapping. This used to leak an 'AttributeError' from inside a node."""
		with self.assertRaises(ConfigurationError) as context:
			Configuration(Path("tests/data/Configuration/scalar.json"))

		self.assertIn("doesn't describe a mapping", str(context.exception))

	def test_ASequenceRootIsRejected(self) -> None:
		with self.assertRaises(ConfigurationError):
			Configuration(Path("tests/data/Configuration/sequence.json"))

	def test_AMissingFileNamesTheRightFormat(self) -> None:
		with self.assertRaises(ConfigurationError) as context:
			Configuration(Path("tests/data/Configuration/does-not-exist.json"))

		self.assertIn("JSON", str(context.exception))
		self.assertNotIn("YAML", str(context.exception))

	def test_AMalformedDocumentIsAConfigurationError(self) -> None:
		"""It used to leak 'json.JSONDecodeError' from the constructor."""
		with self.assertRaises(ConfigurationError) as context:
			Configuration(Path("tests/data/Configuration/malformed.json"))

		self.assertIn("can't be parsed", str(context.exception))
