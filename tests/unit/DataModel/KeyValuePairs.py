# ==================================================================================================================== #
#                                                                                                                      #
#             _____           _ _               _____                    _   _                                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/                        #
# |_|    |___/                          |___/                     |_|                                                  #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :class:`pyTooling.DataModel.KeyValuePairsMixin` and :class:`pyTooling.DataModel.BaseWithKeyValuePairs`.
"""
from pyTooling.DataModel   import BaseWithKeyValuePairs, KeyValuePairsMixin
from pyTooling.MetaClasses import AbstractClassError, ExtendedType
from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Element(BaseWithKeyValuePairs):
	"""A data model element carrying key-value-pairs."""


class SlottedRoot(metaclass=ExtendedType, slots=True):
	"""A slotted class of another primary inheritance line."""

	_name: str


class MixedElement(SlottedRoot, KeyValuePairsMixin):
	"""A slotted class adding the key-value-pairs by mixin."""

	def __init__(self, name: str) -> None:
		KeyValuePairsMixin.__init__(self)
		self._name = name


class KeyValuePairs(Testcase):
	def test_Empty(self) -> None:
		element = Element()

		self.assertEqual(0, len(element))
		self.assertListEqual([], list(element))
		self.assertNotIn("key", element)
		self.assertFalse(hasattr(element, "__dict__"))

	def test_Mapping(self) -> None:
		pairs =   {"runner.os": "Linux", 42: True}
		element = Element(pairs)
		pairs["later"] = 1

		self.assertEqual(2, len(element))
		self.assertEqual("Linux", element["runner.os"])
		self.assertTrue(element[42])
		self.assertNotIn("later", element)

	def test_MappingType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Element([("runner.os", "Linux")])

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))

	def test_Operators(self) -> None:
		element = Element()
		element["first"] =  1
		element["second"] = 2
		element["first"] =  3

		self.assertEqual(3, element["first"])
		self.assertListEqual(["first", "second"], list(element))

		del element["first"]
		self.assertNotIn("first", element)
		self.assertIn("second", element)
		self.assertEqual(1, len(element))

	def test_MissingKey(self) -> None:
		element = Element()

		with self.assertRaises(KeyError):
			_ = element["missing"]

		with self.assertRaises(KeyError):
			del element["missing"]

	def test_Mixin(self) -> None:
		element = MixedElement("Build")
		element["runner.os"] = "Linux"

		self.assertEqual("Linux", element["runner.os"])
		self.assertFalse(hasattr(element, "__dict__"))

	def test_Abstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = BaseWithKeyValuePairs()
