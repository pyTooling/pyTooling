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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from pathlib import Path
from statistics import mean
from time import perf_counter_ns
from typing import Callable, Iterable, Tuple
from unittest import TestCase

from pyTooling.Graph import Graph as pt_Graph, Vertex as pt_Vertex

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class PerformanceTest(TestCase):
	counts: Iterable[int] = (10, 100, 1000)#, 10000)
	edgeFiles:  Iterable[Tuple[int, int, int, Path]] = (
		(100, 92, 72, Path("graph_n100_m150_dir_w0_100.edgelist")),
		(1000, 489, 626, Path("graph_n1000_m1500_dir_w0_100.edgelist")),
		(10000, 3056, 5741, Path("graph_n10000_m15000_dir_w0_100.edgelist"))
	)

	def runSizedTests(self, func: Callable[[int], Callable[[], None]], counts: Iterable[int]):
		print()
		print(f"         min          avg           max")
		for count in counts:
			results = timeit.repeat(func(count), repeat=20, number=50)
			norm = count / 10
			print(f"{count:>5}x: {min(results)/norm:.6f} s    {mean(results)/norm:.6f} s    {max(results)/norm:.6f} s")

	def runFileBasedTests(self, setup: Callable[[Path, int], pt_Graph], func: Callable[[pt_Graph, int, int], Callable[[], None]], edgeFiles: Iterable[Tuple[int, int, int, Path]]):
		print()
		print(f"         min          avg           max        construct")
		for vertexCount, componentStartVertex, componentSize, file in edgeFiles:
			file = Path("tests/data/Graph/EdgeLists") / file

			start = perf_counter_ns()
			graph = setup(file, vertexCount)
			construct = (perf_counter_ns() - start) / 1e9

			results = timeit.repeat(func(graph, componentStartVertex, componentSize), repeat=20, number=50)
			norm = componentSize
			print(f"{vertexCount:>5}x: {min(results)/norm:.6f} s    {mean(results)/norm:.6f} s    {max(results)/norm:.6f} s    {construct/norm:.6f} s")
