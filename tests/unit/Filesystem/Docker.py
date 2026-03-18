# ==================================================================================================================== #
#             _____           _ _               _____ _ _                     _                                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  ___(_) | ___  ___ _   _ ___| |_ ___ _ __ ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_  | | |/ _ \/ __| | | / __| __/ _ \ '_ ` _ \                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  _| | | |  __/\__ \ |_| \__ \ ||  __/ | | | | |                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   |_|_|\___||___/\__, |___/\__\___|_| |_| |_|                       #
# |_|    |___/                          |___/                       |___/                                              #
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
"""Unit tests for pyTooling.Filesystem.Docker."""
from pathlib import Path

from unittest import TestCase

from pyTooling.Exceptions import ToolingException
from pyTooling.Filesystem import Root, Directory, Filename, File, SymbolicLink
from pyTooling.Filesystem.Docker import LayerCake, Layer


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_LayerCake(self) -> None:
		cake = LayerCake(None)

		self.assertEqual(0, cake.TotalFileCount)
		self.assertEqual(0, len(cake.Layers))
		self.assertListEqual(cake.Layers, [])
		self.assertEqual(0, cake.LayerCount)

	def test_Layer(self) -> None:
		layer = Layer(None)

		self.assertIsNone(layer.Parent)
		self.assertIsNone(layer.PreviousLayer)
		self.assertIsNone(layer.NextLayer)
		self.assertEqual(0, layer.Size)
		self.assertEqual(0, len(layer.Files))
		self.assertListEqual(layer.Files, [])
		self.assertEqual(0, layer.FileCount)

	def test_Layer3(self) -> None:
		firstLayer = Layer(None)

		self.assertIsNone(firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIsNone(firstLayer.NextLayer)

		secondLayer = Layer(None, firstLayer)

		self.assertIsNone(firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIs(secondLayer, firstLayer.NextLayer)

		self.assertIsNone(secondLayer.Parent)
		self.assertIs(firstLayer, secondLayer.PreviousLayer)
		self.assertIsNone(secondLayer.NextLayer)

		thirdLayer = Layer(None, secondLayer)

		self.assertIsNone(firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIs(secondLayer, firstLayer.NextLayer)

		self.assertIsNone(secondLayer.Parent)
		self.assertIs(firstLayer, secondLayer.PreviousLayer)
		self.assertIs(thirdLayer, secondLayer.NextLayer)

		self.assertIsNone(thirdLayer.Parent)
		self.assertIs(secondLayer, thirdLayer.PreviousLayer)
		self.assertIsNone(thirdLayer.NextLayer)

	def test_LayerCake_Layer3(self) -> None:
		cake = LayerCake(None)
		firstLayer = Layer(cake)

		self.assertEqual(1, cake.LayerCount)
		self.assertEqual(1, len(cake.Layers))
		self.assertListEqual(cake.Layers, [firstLayer])
		self.assertIs(cake, firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIsNone(firstLayer.NextLayer)

		secondLayer = Layer(cake, firstLayer)

		self.assertEqual(2, cake.LayerCount)
		self.assertEqual(2, len(cake.Layers))
		self.assertListEqual(cake.Layers, [firstLayer, secondLayer])

		self.assertIs(cake, firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIs(secondLayer, firstLayer.NextLayer)

		self.assertIs(cake, secondLayer.Parent)
		self.assertIs(firstLayer, secondLayer.PreviousLayer)
		self.assertIsNone(secondLayer.NextLayer)

		thirdLayer = Layer(cake, secondLayer)

		self.assertEqual(3, cake.LayerCount)
		self.assertEqual(3, len(cake.Layers))
		self.assertListEqual(cake.Layers, [firstLayer, secondLayer, thirdLayer])

		self.assertIs(cake, firstLayer.Parent)
		self.assertIsNone(firstLayer.PreviousLayer)
		self.assertIs(secondLayer, firstLayer.NextLayer)

		self.assertIs(cake, secondLayer.Parent)
		self.assertIs(firstLayer, secondLayer.PreviousLayer)
		self.assertIs(thirdLayer, secondLayer.NextLayer)

		self.assertIs(cake, thirdLayer.Parent)
		self.assertIs(secondLayer, thirdLayer.PreviousLayer)
		self.assertIsNone(thirdLayer.NextLayer)
