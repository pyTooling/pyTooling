# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
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
Unit tests for class :class:`pyTooling.MetaClasses.ExtendedType`.

This test suite tests decorators:

* :func:`@abstractmethod <pyTooling.MetaClasses.abstractmethod>`
* :func:`@mustoverride <pyTooling.MetaClasses.mustoverride>`
"""
from pickle                import loads, dumps
from unittest              import TestCase

from pyTooling.MetaClasses import ExtendedType
from pyTooling.Tree        import Node


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class SimpleClass(metaclass=ExtendedType, slots=True):
	_data1: int

	def __init__(self, data: int) -> None:
		self._data1 = data


class DerivedClass(SimpleClass):
	_data2: int

	def __init__(self, data: int) -> None:
		super().__init__(data)
		self._data2 = data + 1


class MixinClass(metaclass=ExtendedType, mixin=True):
	_data3: int

	def __init__(self, data: int) -> None:
		self._data3 = data + 2


class MixedClass(DerivedClass, MixinClass):
	_data4: int

	def __init__(self, data: int) -> None:
		super().__init__(data)
		MixinClass.__init__(self, data)
		self._data4 = data + 3


class Pickleing(TestCase):
	def test_SimpleClass(self) -> None:
		rootInstance = SimpleClass(10)

		serialized = dumps(rootInstance)
		recreatedInstance = loads(serialized)

		self.assertEqual(10, recreatedInstance._data1)

	def test_DerivedClass(self) -> None:
		rootInstance = DerivedClass(10)

		serialized = dumps(rootInstance)
		recreatedInstance = loads(serialized)

		self.assertEqual(10, recreatedInstance._data1)
		self.assertEqual(11, recreatedInstance._data2)

	def test_MixedClass(self) -> None:
		rootInstance = MixedClass(10)

		serialized = dumps(rootInstance)
		recreatedInstance = loads(serialized)

		self.assertEqual(10, recreatedInstance._data1)
		self.assertEqual(11, recreatedInstance._data2)
		self.assertEqual(12, recreatedInstance._data3)
		self.assertEqual(13, recreatedInstance._data4)


def format(value: Node) -> str:
	return ""


class PickledTree(TestCase):
	def test_SimpleTree(self) -> None:
		print()
		root = Node("")

		node1 = Node(nodeID=1, value="node1", keyValuePairs=(kvp1 := {"a": 1, "b": 2}), format=format, parent=root)
		node2 = Node(nodeID=2, value="node2", keyValuePairs=(kvp2 := {"g": 1, "h": 2}), format=format, parent=root)
		node3 = Node(nodeID=3, value="node3", keyValuePairs=(kvp3 := {"x": 1, "y": 2}), format=format, parent=root)

		serialized = dumps(root)
		recreated = loads(serialized)

		self.assertEqual("node1", recreated.GetNodeByID(1).Value)
		self.assertEqual("node2", recreated.GetNodeByID(2).Value)
		self.assertEqual("node3", recreated.GetNodeByID(3).Value)

		self.assertIs(format, recreated.GetNodeByID(1)._format)

		self.assertDictEqual(kvp1, recreated.GetNodeByID(1)._dict)
		self.assertDictEqual(kvp2, recreated.GetNodeByID(2)._dict)
		self.assertDictEqual(kvp3, recreated.GetNodeByID(3)._dict)
