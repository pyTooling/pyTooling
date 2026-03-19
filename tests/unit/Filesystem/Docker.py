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
from pathlib  import Path
from random   import randint

from unittest import TestCase

from pyTooling.Filesystem        import Root, Directory, Filename, File
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


class Slicing(TestCase):
	def test_LayerCake(self) -> None:
		print()
		fileSizes = [
			3091, 2638, 1742, 1607, 3668, 2613, 2967, 1892, 471, 2024, 2054, 4086, 4101, 3501, 3440, 2529, 2918, 2428, 2088,
			3684, 3339, 2119, 4291, 3977, 2508, 2814, 3345, 427, 2099, 3755, 876, 2691, 1609, 2827, 686, 388, 1214, 110, 3013,
			1556, 4210, 1092, 594, 1277, 1950, 3524, 1574, 1412, 310, 298, 2756, 3706, 2503, 1606, 1764, 1344, 3580, 3782,
			2219, 3480, 2929, 2227, 3467, 3891, 3158, 2802, 2534, 933, 3575, 2619, 1981, 1781, 2943, 2797, 1518, 1226, 1144,
			3554, 2773, 914, 3245, 1426, 2988, 2357, 1419, 3682, 1662, 701, 131, 1450, 3478, 3571, 4084, 3198, 1694, 3388,
			3092, 3203, 2900, 292, 2227, 1227, 3315, 3992, 2628, 2563, 2225, 4012, 1930, 2532, 4238, 1130, 1714, 1992, 1648,
			332, 428, 2515, 2284, 649, 513, 3081, 2410, 3241, 2927, 985, 2804, 4040, 729, 3185, 1221, 2440, 3886, 4069, 1040,
			1709, 3573, 840, 3455, 123, 294, 106, 308, 2920, 2590, 1104, 933, 945, 1659, 3339, 733, 3347, 826, 638, 2687,
			1773, 668, 3627, 2580, 143, 351, 1828, 1956, 2873, 352, 1065, 2610, 1100, 4242, 1930, 4023, 367, 3974, 230, 2137,
			280, 1096, 2197, 4174, 2607, 956, 3409, 2110, 1888, 3573, 2879, 2700, 2396, 445, 225, 1323, 1906, 824, 1630, 2417,
			3182, 522, 2122, 1748, 3991, 2659, 1109, 3126, 2583, 2586, 1684, 3994, 2906, 2560, 1486, 2743, 3038, 3553, 2644,
			541, 1334, 3068, 397, 3462, 1624, 754, 3504, 404, 4134, 3410, 2821, 3975, 2303, 117, 3126, 2521, 695, 3408, 4007,
			1101, 3469, 240, 800, 178, 1442, 4033, 1965, 1042, 1015, 3354, 1840, 3389, 1877, 306, 517, 489, 3317, 1558, 965,
			2943, 3024, 231, 1478, 2586, 1873, 3314, 2326, 2001, 3401, 1909, 2715, 2226, 3903, 3152, 4096, 3372, 2199, 1560,
			3374, 1133, 4147, 2927, 1014, 2718, 1110, 1089, 3362, 520, 1585, 3729, 1796, 542, 4265, 1800, 4173, 1917, 2269,
			4086, 422, 3505, 4094, 2748, 1674, 2886, 3025, 2431, 791, 2920, 259, 2404, 2916, 3227, 1736, 2534, 2593, 1174,
			2408, 1687, 458, 4133, 2603, 759, 3471, 463, 704, 3147, 3786, 2174, 4180, 1042, 1217, 3580, 455, 2106, 573, 1011,
			3224, 653, 2554, 1835, 1716, 4052, 2733, 1960, 1802, 2914, 3738, 2195, 2491, 1312, 3689, 3384, 2502, 529, 1372,
			2080, 3859, 2580, 1120, 4257, 1133, 887, 2889, 2337, 1498, 3182, 1250, 963, 2094, 1890, 1321, 1154, 3264, 3270,
			441, 1532, 259, 1310, 3617, 2774, 1354, 1320, 1203, 900, 4045, 583, 1030, 408, 3610, 684, 3486, 2073, 195, 1791,
			1587, 3854, 2066, 1834, 880, 3457, 837, 1203, 1790, 448, 2452, 4099, 4282, 3355, 2562, 1535, 3820, 559, 135, 3583,
			1496, 3320, 2204, 235, 1429, 3307, 1531, 488, 1535, 1029, 111, 3169, 2250, 390, 715, 2903, 1300, 557, 2825, 1034,
			3268, 3560, 3619, 3660, 3509, 455, 2964, 4033, 385, 1249, 4039, 810, 668, 2413, 3509, 2055, 3811, 2494, 881, 3204,
			3667, 1688, 735, 2736, 1691, 2238, 1146, 1551, 3525, 2887, 2127, 2303, 2573, 1603, 1659, 192, 3671, 381, 1538,
			1944, 3767, 169, 1035, 4089, 1551, 1799, 949, 2787, 2334, 4248, 2565, 3274, 1256, 3016, 1700, 2888, 2627, 4053,
			707, 1178, 1219, 2355, 3402, 1600, 1104, 2907, 3967, 3844, 1124, 2357, 205
		]
		fileCount = len(fileSizes)

		rootPath = Path("tests/data")
		root = Root(rootPath, collectSubdirectories=False)
		directory = Directory("directory", parent=root)

		for i, fileSize in enumerate(fileSizes):
			filename = Filename(f"filename_{i}", parent=directory)
			_ = File(10 + i, fileSize, parent=filename)

		root.AggregateSizes()
		root.ResolveSymbolicLinks()
		cake = LayerCake(root)

		self.assertIs(root, cake.Root)

		cake.CreateDockerLayers(32768, 128456, 2048)

		self.assertEqual(fileCount, root.TotalFileCount)
		self.assertEqual(fileCount, cake.TotalFileCount)

		for i, layer in enumerate(cake.Layers, start=1):
			print(f"{i:>2}: {layer.Size / 2**10:5.1f} MiB  files={layer.FileCount:>3}")
			self.assertGreater(layer.Size, 0)
			self.assertGreater(layer.FileCount, 0)

		self.assertEqual(10, cake.LayerCount)
		self.assertListEqual([l.FileCount for l in cake.Layers], [31, 33, 35, 37, 41, 45, 52, 67, 120, 39])
