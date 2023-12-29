# ==================================================================================================================== #
#             _____           _ _               ____                 _                                                 #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ __ __ _ _ __ | |__                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |  _| '__/ _` | '_ \| '_ \                                             #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |_| | | | (_| | |_) | | | |                                            #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_|  \__,_| .__/|_| |_|                                            #
# |_|    |___/                          |___/                 |_|                                                      #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Performance tests for pyTooling.Graph."""
import timeit
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from time import perf_counter_ns
from typing import Callable, Iterable
from unittest import TestCase

from pyTooling.Graph import Graph as pt_Graph


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


@dataclass
class BiggestNetwork:
	startNodeID: int
	size: int


@dataclass
class EdgeFile:
	vertexCount: int
	edgeCount: int
	biggestNetwork: BiggestNetwork
	file: Path


class PerformanceTest(TestCase):
	counts: Iterable[int] = (10, 100, 1000, 10000)
	edgeFiles:  Iterable[EdgeFile] = (
		EdgeFile(   100,    150, BiggestNetwork(  92,    72), Path("graph_n100_m150_dir_w0_100.edgelist")),
		EdgeFile(  1000,   1500, BiggestNetwork( 489,   626), Path("graph_n1000_m1500_dir_w0_100.edgelist")),
		EdgeFile( 10000,  15000, BiggestNetwork(3056,  5741), Path("graph_n10000_m15000_dir_w0_100.edgelist")),
#		EdgeFile(100000, 150000, BiggestNetwork(9671, 58243), Path("graph_n100000_m150000_dir_w0_100.edgelist")),
	)

	@staticmethod
	def minMaxSumMean(array):
		minimum = 1.0e9
		maximum = 0.0
		sum = 0.0
		for value in array:
			minimum = value if value < minimum else minimum
			maximum = value if value > maximum else maximum
			sum += value

		return minimum, maximum, sum, sum/len(array)

	def runSizedTests(self, func: Callable[[int], Callable[[], None]], counts: Iterable[int]):
		print()
		print(f"         min           mean          median        max")
		for count in counts:
			results = timeit.repeat(func(count), repeat=20, number=50)
			norm = count / 10

			minimum, maximum, _, mean = self.minMaxSumMean(results)
			print(f"{count:>6}x: {minimum/norm:.6f} s    {mean/norm:.6f} s    {median(results)/norm:.6f} s    {maximum/norm:.6f} s")

	def runFileBasedTests(self, setup: Callable[[Path, int], pt_Graph], func: Callable[[pt_Graph, int, int], Callable[[], None]], edgeFiles: Iterable[EdgeFile]):
		print()
		print(f"         min           mean          median        max           construct")
		for edgeFile in edgeFiles:
			file = Path("tests/data/Graph/EdgeLists") / edgeFile.file

			start = perf_counter_ns()
			graph = setup(file, edgeFile.vertexCount)
			construct = (perf_counter_ns() - start) / 1e9

			results = timeit.repeat(func(graph, edgeFile.biggestNetwork.startNodeID, edgeFile.biggestNetwork.size), repeat=20, number=50)
			norm = edgeFile.biggestNetwork.size
			minimum, maximum, _, mean = self.minMaxSumMean(results)
			print(f"{edgeFile.vertexCount:>6}x: {minimum/norm:.6f} s    {mean/norm:.6f} s    {median(results)/norm:.6f} s    {maximum/norm:.6f} s    {construct/norm:.6f} s")
