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
"""Performance tests for pyTooling.Graph."""
from pathlib import Path

import networkx.exception
from networkx import DiGraph as nx_DiGraph, dfs_preorder_nodes, bfs_predecessors, shortest_path

from . import PerformanceTest


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Graph(PerformanceTest):
	def test_AddEdge_Flat(self) -> None:
		def wrapper(count: int):
			def func():
				g = nx_DiGraph()
				g.add_node(0)

				for i in range(1, count):
					g.add_edge(0, i)

			return func

		self.runSizedTests(wrapper, self.counts)

	def test_AddEdge_Linear(self) -> None:
		def wrapper(count: int):
			def func():
				g = nx_DiGraph()

				prev = 0
				g.add_node(prev)

				for i in range(1, count):
					g.add_edge(prev, i)
					prev = i

			return func

		self.runSizedTests(wrapper, self.counts)


class RandomGraph(PerformanceTest):
	def ConstructGraphFromEdgeListFile(self, file: Path, vertexCount: int) -> nx_DiGraph:
		graph = nx_DiGraph()
		for v in range(vertexCount):
			graph.add_node(v)

		with file.open("r", encoding="utf-8") as f:
			for line in f.readlines():
				v, u, w = line.split(" ")
				graph.add_edge(int(v), int(u), weight=int(w))

		return graph

	def test_BFS(self) -> None:
		def wrapper(graph: nx_DiGraph, componentStartVertex: int, componentSize: int):
			def func():
				bfsList = [v for v in bfs_predecessors(graph, componentStartVertex)]

				self.assertEqual(componentSize - 1, len(bfsList))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_DFS(self) -> None:
		def wrapper(graph: nx_DiGraph, componentStartVertex: int, componentSize: int):
			def func():
				dfsList = [v for v in dfs_preorder_nodes(graph, componentStartVertex)]

				self.assertEqual(componentSize, len(dfsList))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_ShortestPathByHops(self) -> None:
		def wrapper(graph: nx_DiGraph, componentStartVertex: int, componentSize: int):
			def func():
				try:
					vertexPath = shortest_path(graph, 49, 20)
				except networkx.exception.NetworkXNoPath:
					pass

				# print(f"path length: {len(vertexPath)}")
				# self.assertEqual(6, len(vertexPath))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_ShortestPathByWeight(self) -> None:
		def wrapper(graph: nx_DiGraph, componentStartVertex: int, componentSize: int):
			def func():
				try:
					vertexPath = shortest_path(graph, 49, 20, "weight")
				except networkx.exception.NetworkXNoPath:
					pass

				# print(f"path length: {len(vertexPath)}")
				# self.assertEqual(6, len(vertexPath))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)
