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
from pathlib import Path
from statistics import mean

from pyTooling.Graph import Graph as pt_Graph, Vertex as pt_Vertex
from . import PerformanceTest


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class EdgeLinking(PerformanceTest):
	def test_LinkNewVertex_Flat(self):
		def wrapper(count: int):
			def func():
				rootVertex = pt_Vertex(0)

				for i in range(1, count):
					rootVertex.LinkToNewVertex(i)

			return func

		self.runSizedTests(wrapper, self.counts)

	def test_LinkNewVertex_Linear(self):
		def wrapper(count: int):
			def func():
				vertex = pt_Vertex(0)

				for i in range(1, count):
					vertex = vertex.LinkToNewVertex(i).Destination

			return func

		self.runSizedTests(wrapper, self.counts)


class RandomGraph(PerformanceTest):
	def ConstructGraphFromEdgeListFile(self, file: Path, vertexCount: int) -> pt_Graph:
		graph = pt_Graph(name=str(vertexCount))
		vList = [pt_Vertex(vertexID=v, graph=graph) for v in range(vertexCount)]

		with file.open("r") as f:
			for line in f.readlines():
				v, u, w = line.split(" ")
				vList[int(v)].LinkToVertex(vList[int(u)], edgeWeight=int(w))

# 		lenBFS = []
# #		lenDFS = []
# 		for v in vList:
# 			bfsList = [u for u in v.IterateVerticesBFS()]
# #			dfsList = [u for u in v.IterateVerticesDFS()]
# 			lenBFS.append(len(bfsList))
# #			lenDFS.append(len(dfsList))
# #			print(f"{v}: bfs={len(bfsList)}; dfs={len(dfsList)}")
# 		print(f"BFS: min={min(lenBFS)}  avg={mean(lenBFS)}  max={max(lenBFS)}({lenBFS.index(max(lenBFS))})")
# #		print(f"DFS: min={min(lenDFS)}  avg={mean(lenDFS)}  max={max(lenDFS)}({lenDFS.index(max(lenDFS))})")

		return graph

	def test_BFS(self):
		def wrapper(graph: pt_Graph, componentStartVertex: int, componentSize: int):
			def func():
				rootVertex = graph._verticesWithID[componentStartVertex]

				bfsList = [v for v in rootVertex.IterateVerticesBFS()]
				self.assertEqual(componentSize, len(bfsList))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_DFS(self):
		def wrapper(graph: pt_Graph, componentStartVertex: int, componentSize: int):
			def func():
				rootVertex = graph._verticesWithID[componentStartVertex]

				bfsList = [v for v in rootVertex.IterateVerticesDFS()]
				self.assertEqual(componentSize, len(bfsList))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_ShortestPathByHops(self):
		def wrapper(graph: pt_Graph, componentStartVertex: int, componentSize: int):
			def func():
				startVertex = graph._verticesWithID[49]
				destinationVertex = graph._verticesWithID[20]

				try:
					vertexPath = [v for v in startVertex.ShortestPathToByHops(destinationVertex)]
				except KeyError:
					pass

				# print(f"path length: {len(vertexPath)}")
				# self.assertEqual(6, len(vertexPath))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)

	def test_ShortestPathByWeight(self):
		def wrapper(graph: pt_Graph, componentStartVertex: int, componentSize: int):
			def func():
				startVertex = graph._verticesWithID[49]
				destinationVertex = graph._verticesWithID[20]

				try:
					vertexPath = [v for v, w in startVertex.ShortestPathToByWeight(destinationVertex)]
				except KeyError:
					pass

				# print(f"path length: {len(vertexPath)}")
				# self.assertEqual(6, len(vertexPath))

			return func

		self.runFileBasedTests(self.ConstructGraphFromEdgeListFile, wrapper, self.edgeFiles)
