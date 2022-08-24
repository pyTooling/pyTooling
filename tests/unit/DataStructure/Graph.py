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
from typing import Any, Optional as Nullable
from unittest import TestCase

from pyTooling.Graph import Vertex, Graph

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Construction(TestCase):
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
		v11 = v1.LinkToNewVertex()
		v111 = v11.LinkToNewVertex()
		v112 = v11.LinkToNewVertex()
		v12 = v1.LinkToNewVertex()
		v121 = v12.LinkToNewVertex()
		v1211 = v121.LinkToNewVertex()

		self.assertEqual(2, len(v1))
		self.assertEqual(2, len(v11))
		self.assertEqual(0, len(v111))
		self.assertEqual(0, len(v112))
		self.assertEqual(1, len(v12))
		self.assertEqual(1, len(v121))
		self.assertEqual(0, len(v1211))
		self.assertEqual(7, len(v1.Graph))


class Iterate(TestCase):
	_edges = [
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
	]

	def test_DFS(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(15)]
		v0 = vList[0]

		for u, v, w in self._edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 1, 8, 7, 3, 2, 4, 5, 6, 10, 9, 11], [v.ID for v in v0.IterateVertexesDFS()])

	def test_BFS(self):
		g = Graph()
		vList = [Vertex(vertexID=i, graph=g) for i in range(15)]
		v0 = vList[0]

		for u, v, w in self._edges:
			vList[u].LinkToVertex(vList[v], edgeWeight=w)

		self.assertListEqual([0, 1, 9, 8, 7, 3, 6, 10, 11, 2, 4, 5], [v.ID for v in v0.IterateVertexesBFS()])
