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
"""Unit tests for pyTooling.Graph."""
from typing import Any, Optional as Nullable, List, Tuple
from unittest import TestCase

from pyTooling.Graph import Vertex, Graph

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Construction(TestCase):
	def test_GraphName(self):
		g = Graph("myGraph")

		self.assertEqual("myGraph", g.Name)

	def test_SingleVertex(self):
		root: Vertex[Nullable[Any], int, str, Any] = Vertex()

		self.assertIsNone(root.ID)
		self.assertIsNone(root.Value)
		self.assertEqual(1, len(root.Graph))

	def test_SingleVertexInEmptyGraph(self):
		graph = Graph()

		root: Vertex[Nullable[Any], int, str, Any] = Vertex(graph=graph)

		self.assertIsNone(root.ID)
		self.assertIsNone(root.Value)
		self.assertEqual(1, len(root.Graph))
		self.assertIsNone(root.Graph.Name)

	def test_SingleVertexInEmptyGraphWithName(self):
		graph = Graph("test")

		root = Vertex(graph=graph)

		self.assertIsNone(root.ID)
		self.assertIsNone(root.Value)
		self.assertEqual(1, len(root.Graph))
		self.assertEqual("test", root.Graph.Name)

	def test_SimpleTree(self):
		v1 = Vertex()
		v11 = v1.LinkToNewVertex().Destination
		v111 = v11.LinkToNewVertex().Destination
		v112 = v11.LinkToNewVertex().Destination
		v12 = v1.LinkToNewVertex().Destination
		v121 = v12.LinkToNewVertex().Destination
		v1211 = v121.LinkToNewVertex().Destination

		self.assertEqual(2, len(v1))
		self.assertEqual(2, len(v11))
		self.assertEqual(0, len(v111))
		self.assertEqual(0, len(v112))
		self.assertEqual(1, len(v12))
		self.assertEqual(1, len(v121))
		self.assertEqual(0, len(v1211))
		self.assertEqual(7, len(v1.Graph))


class Dicts(TestCase):
	def test_GraphDict(self):
		g = Graph()
		g["key"] = 1

		self.assertEqual(1, g["key"])

		del g["key"]
		with self.assertRaises(KeyError):
			_ = g["key"]

	def test_VertexDict(self):
		g = Graph()
		v = Vertex(graph=g)
		v["key"] = 2

		self.assertEqual(2, v["key"])

		del v["key"]
		with self.assertRaises(KeyError):
			_ = v["key"]

	def test_EdgeDict(self):
		g = Graph()
		v1 = Vertex(graph=g)
		v1["key"] = 3

		v2 = Vertex(graph=g)
		v2["key"] = 4

		e12 = v1.LinkToVertex(v2)
		e12["key"] = 5

		self.assertEqual(3, v1["key"])
		self.assertEqual(4, v2["key"])
		self.assertEqual(5, e12["key"])

		del e12["key"]
		with self.assertRaises(KeyError):
			_ = e12["key"]


class Iterate(TestCase):
	class TestGraph:
		_vertexCount: int
		_edgeCount:   int
		_edges:       List[Tuple[int, int, int]]

		def __init__(self, edges: List[Tuple[int, int, int]]):
			self._vertexCount = max([max(e[0], e[1]) for e in edges]) + 1
			self._edgeCount = len(edges)
			self._edges = edges

		@property
		def VertexCount(self) -> int:
			return self._vertexCount

		@property
		def EdgeCount(self) -> int:
			return self._edgeCount

		@property
		def Edges(self) -> List[Tuple[int, int, int]]:
			return self._edges

	_graph0 = TestGraph([
		(0, 3, 1),
		(1, 3, 2),
		(2, 0, 3), (2, 1, 4),             # root
		(3, 6, 5), (3, 7, 6),
		(4, 0, 7), (4, 3, 8), (4, 5, 9),  # root
		(5, 9, 10), (5, 10, 11),
		(6, 8, 12),
		(7, 8, 13), (7, 9, 14),
		(8, 11, 15),
		(9, 11, 16), (9, 12, 17),
		(10, 9, 18),
		# 11                                leaf
		# 12                                leaf
		(13, 14, 19),                      # root
		# 14                                leaf
	])

	_graph1 = TestGraph([
		(0, 1, 0), (0, 9, 0),
		(1, 8, 0),
		(2, 8, 0),
		(3, 2, 0), (3, 4, 0), (3, 5, 0),
		(6, 5, 0),
		(7, 3, 0), (7, 6, 0), (7, 10, 0), (7, 11, 0),
		(8, 7, 0),
		(9, 1, 0), (9, 8, 0),
		(10, 9, 0), (10, 11, 0),
		(11, 7, 0),
		(12, 2, 0), (12, 8, 0),
		(13, 14, 0),
	])

	_graph2 = TestGraph([
		(0, 1, 1), (0, 2, 2), (0, 3, 3),
		(1, 2, 3), (1, 10, 3),
		(2, 7, 20), (2, 8, 6),
		(3, 2, 1), (3, 4, 1),
		(4, 5, 1), (4, 7, 1),
		(5, 6, 1), (5, 7, 1),
		(6, 0, 4), (6, 3, 2), (6, 7, 5), (6, 13, 8),
		(7, 11, 6), (7, 12, 1),
		(8, 1, 5), (8, 10, 1), (8, 11, 16),
		(9, 3, 4), (9, 6, 1),
		(11, 4, 4), (11, 10, 4), (11, 14, 1),
		(13, 14, 3),
		(14, 10, 9),
	])


class IterateOnGraph(Iterate):
	def test_Roots(self):
		g = Graph()
		vList = [Vertex(value=i, graph=g) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertSetEqual({2, 4, 13}, set(v.Value for v in g.IterateRoots()))
		self.assertSetEqual({2, 4},     set(v.Value for v in g.IterateRoots(predicate=lambda v: v.Value % 2 == 0)))

	def test_Leafs(self):
		g = Graph()
		vList = [Vertex(value=i, graph=g) if i % 2 == 0 else Vertex(vertexID=i, value=i, graph=g) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertSetEqual({11, 12, 14}, set(v.Value for v in g.IterateLeafs()))
		self.assertSetEqual({12, 14},     set(v.Value for v in g.IterateLeafs(predicate=lambda v: v.Value % 2 == 0)))

	def test_Vertices(self):
		gID =    Graph()
		gValue = Graph()
		gMixed = Graph()
		vListID =    [Vertex(vertexID=i, value=i, graph=gID)                                                     for i in range(0, self._graph0.VertexCount)]
		vListValue = [Vertex(value=i, graph=gValue)                                                              for i in range(0, self._graph0.VertexCount)]
		vListMixed = [Vertex(value=i, graph=gMixed) if i % 2 == 0 else Vertex(vertexID=i, value=i, graph=gMixed) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vListID[u].LinkToVertex(vListID[v], edgeWeight=w)
			vListValue[u].LinkToVertex(vListValue[v], edgeWeight=w)
			vListMixed[u].LinkToVertex(vListMixed[v], edgeWeight=w)

		self.assertListEqual([i for i in range(0, 15, 1)], [v.Value for v in gID.IterateVertices()])
		self.assertListEqual([i for i in range(0, 15, 2)], [v.Value for v in gID.IterateVertices(predicate=lambda v: v.Value % 2 == 0)])

		self.assertListEqual([i for i in range(0, 15, 1)], [v.Value for v in gValue.IterateVertices()])
		self.assertListEqual([i for i in range(0, 15, 2)], [v.Value for v in gValue.IterateVertices(predicate=lambda v: v.Value % 2 == 0)])

		self.assertListEqual([i for i in range(0, 15, 2)] + [i for i in range(1, 15, 2)], [v.Value for v in gMixed.IterateVertices()])
		self.assertListEqual([i for i in range(0, 15, 2)],                                [v.Value for v in gMixed.IterateVertices(predicate=lambda v: v.Value % 2 == 0)])

	def test_Topologically(self):
		g = Graph()
		vList = [Vertex(value=i, graph=g) if i % 2 == 0 else Vertex(vertexID=i, value=i, graph=g) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([11, 12, 14, 8, 9, 13, 6, 7, 10, 3, 5, 0, 1, 4, 2], [v.Value for v in g.IterateTopologically()])
		self.assertListEqual([12, 14, 8, 6, 10, 0, 4, 2],                        [v.Value for v in g.IterateTopologically(predicate=lambda v: v.Value % 2 == 0)])
		self.assertListEqual([11, 9, 13, 7, 3, 5, 1],                            [v.Value for v in g.IterateTopologically(predicate=lambda v: v.Value % 2 == 1)])

	def test_Edges(self):
		g = Graph()
		vList = [Vertex(value=i, graph=g) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)
			vList[v].LinkToVertex(vList[u], edgeWeight=self._graph0.EdgeCount + w, edgeID=v*20+u)

		for i, edge in enumerate(g.IterateEdges()):
			if i < self._graph0.EdgeCount:
				u, v, w = self._graph0.Edges[i % self._graph0.EdgeCount]
			else:
				v, u, w = self._graph0.Edges[i % self._graph0.EdgeCount]
				w += self._graph0.EdgeCount

			self.assertEqual(vList[u], edge.Source)
			self.assertEqual(vList[v], edge.Destination)
			self.assertEqual(w, edge.Weight)

		for i, edge in enumerate(g.IterateEdges(predicate=lambda v: v.Weight % 2 == 0), start=1):
			self.assertEqual(i * 2, edge.Weight)


class GraphOperations(Iterate):
	def test_ReverseEdges(self):
		g = Graph()
		vList = [Vertex(value=i, graph=g) if i % 2 == 0 else Vertex(vertexID=i, value=i, graph=g) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			if w % 2 == 0:
				vList[u].LinkToVertex(vList[v], edgeWeight=w)
			else:
				vList[u].LinkToVertex(vList[v], edgeWeight=w, edgeID=w)

		g.ReverseEdges()

		for i, edge in enumerate(g.IterateEdges()):
			u, v, w = self._graph0.Edges[i]

			self.assertEqual(vList[v], edge.Source)
			self.assertEqual(vList[u], edge.Destination)
			self.assertEqual(w, edge.Weight)


class GraphProperties(Iterate):
	def test_HasCycle(self):
		g0 = Graph()
		vList0 = [Vertex(value=i, graph=g0) if i % 2 == 0 else Vertex(vertexID=i, value=i, graph=g0) for i in range(0, self._graph0.VertexCount)]

		for u, v, w in self._graph0.Edges:
			vList0[u].LinkToVertex(vList0[v], edgeWeight=w)

		self.assertFalse(g0.HasCycle())

		g1 = Graph()
		vList1 = [Vertex(vertexID=i, graph=g1) for i in range(0, self._graph1.VertexCount)]

		for u, v, w in self._graph1.Edges:
			vList1[u].LinkToVertex(vList1[v], edgeWeight=w)

		self.assertTrue(g1.HasCycle())


class IterateStartingFromVertex(Iterate):
	def test_DFS(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(0, self._graph1.VertexCount)]
		v0 = vList[0]

		for u, v, w in self._graph1.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 1, 8, 7, 3, 2, 4, 5, 6, 10, 9, 11], [v.ID for v in v0.IterateVerticesDFS()])

	def test_BFS(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(0, self._graph1.VertexCount)]
		v0 = vList[0]

		for u, v, w in self._graph1.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 1, 9, 8, 7, 3, 6, 10, 11, 2, 4, 5], [v.ID for v in v0.IterateVerticesBFS()])

	def test_ShortestPathByHops(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(0, self._graph2.VertexCount)]
		v0 = vList[0]

		for u, v, w in self._graph2.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 2, 7, 11, 14], [v.ID for v in v0.ShortestPathToByHops(vList[14])])
		with self.assertRaises(KeyError):
			print([v.ID for v in v0.ShortestPathToByHops(vList[9])])

	def test_ShortestPathByFixedWeight(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(0, self._graph2.VertexCount)]
		v0 = vList[0]

		for u, v, _ in self._graph2.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=1)

		self.assertListEqual([0, 2, 7, 11, 14], [v.ID for v, w in v0.ShortestPathToByWeight(vList[14])])
		with self.assertRaises(KeyError):
			print([v.ID for v in v0.ShortestPathToByHops(vList[9])])

	def test_ShortestPathByWeight(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(0, self._graph2.VertexCount)]
		v0 = vList[0]

		for u, v, w in self._graph2.Edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 3, 4, 5, 6, 13, 14], [v.ID for v, w in v0.ShortestPathToByWeight(vList[14])])
		with self.assertRaises(KeyError):
			print([v.ID for v in v0.ShortestPathToByHops(vList[9])])
