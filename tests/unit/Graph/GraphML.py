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
"""Unit tests for pyTooling.Graph.GraphML."""
from unittest import TestCase

from pyTooling.Graph import Graph as pyTooling_Graph, Subgraph as pyTooling_Subgraph, Vertex
from pyTooling.Graph.GraphML import AttributeContext, AttributeTypes, Key, Data, Node, Edge, Graph, Subgraph, GraphMLDocument
from pyTooling.Tree import Node as pyToolingNode


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Construction(TestCase):
	def test_Key(self) -> None:
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		self.assertEqual("k1", key.ID)
		self.assertEqual("color", str(key.AttributeName))
		self.assertEqual("string", str(key.AttributeType))

		self.assertFalse(key.HasClosingTag)
		self.assertEqual("""<key id="k1" for="node" attr.name="color" attr.type="string" />\n""", key.Tag(0))
		self.assertListEqual([
				"""<key id="k1" for="node" attr.name="color" attr.type="string" />\n"""
			], key.ToStringLines(0))

		print()
		for line in key.ToStringLines():
			print(line, end="")

	def test_Data(self) -> None:
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)
		data = Data(key, "violet")

		self.assertEqual(key, data.Key)
		self.assertEqual("violet", data.Data)

		self.assertFalse(data.HasClosingTag)
		self.assertEqual("""<data key="k1">violet</data>\n""", data.Tag(0))
		self.assertListEqual([
				"""<data key="k1">violet</data>\n"""
			], data.ToStringLines(0))

		print()
		for line in data.ToStringLines():
			print(line, end="")

	def test_Node(self) -> None:
		node = Node("n1")

		self.assertEqual("n1", node.ID)

		self.assertFalse(node.HasClosingTag)
		self.assertEqual("""<node id="n1" />\n""", node.Tag(0))
		self.assertListEqual([
				"""<node id="n1" />\n"""
			], node.ToStringLines(0))

		print()
		for line in node.ToStringLines():
			print(line, end="")

	def test_NodeWithData(self) -> None:
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		node = Node("n1")
		node.AddData(Data(key, "violet"))

		self.assertEqual("n1", node.ID)

		self.assertTrue(node.HasClosingTag)
		self.assertEqual("""<node id="n1">\n""", node.OpeningTag(0))
		self.assertEqual("""</node>\n""", node.ClosingTag(0))
		self.assertListEqual([
				"""<node id="n1">\n""",
				"""  <data key="k1">violet</data>\n""",
				"""</node>\n"""
			], node.ToStringLines(0))

		print()
		for line in node.ToStringLines():
			print(line, end="")

	def test_Edge(self) -> None:
		node1 = Node("n1")
		node2 = Node("n2")
		edge = Edge("e1", node1, node2)

		self.assertFalse(edge.HasClosingTag)
		self.assertEqual("""<edge id="e1" source="n1" target="n2" />\n""", edge.Tag(0))
		self.assertListEqual([
				"""<edge id="e1" source="n1" target="n2" />\n"""
			], edge.ToStringLines(0))

		print()
		for line in edge.ToStringLines():
			print(line, end="")

	def test_EdgeWithData(self) -> None:
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		node1 = Node("n1")
		node2 = Node("n2")
		edge = Edge("e1", node1, node2)
		edge.AddData(Data(key, "violet"))

		self.assertEqual("e1", edge.ID)

		self.assertTrue(edge.HasClosingTag)
		self.assertEqual("""<edge id="e1" source="n1" target="n2">\n""", edge.OpeningTag(0))
		self.assertEqual("""</edge>\n""", edge.ClosingTag(0))
		self.assertListEqual([
				"""<edge id="e1" source="n1" target="n2">\n""",
				"""  <data key="k1">violet</data>\n""",
				"""</edge>\n"""
			], edge.ToStringLines(0))

		print()
		for line in edge.ToStringLines():
			print(line, end="")

	def test_Graph(self) -> None:
		graph = Graph(None, "g1")

		self.assertTrue(graph.HasClosingTag)
		self.assertEqual("""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="0"
  parse.edges="0"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">\n""", graph.OpeningTag(0))
		self.assertEqual("""</graph>\n""", graph.ClosingTag(0))
		self.assertListEqual([
			"""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="0"
  parse.edges="0"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">\n""",
				"""</graph>\n"""
			], graph.ToStringLines(0))

		print()
		for line in graph.ToStringLines():
			print(line, end="")

	def test_GraphWithNodesAndEdges(self) -> None:
		graph = Graph(None, "g1")

		graph.AddNode(Node("n1"))
		graph.AddNode(Node("n2"))
		graph.AddEdge(Edge("e1", graph.GetNode("n1"), graph.GetNode("n2")))

		self.assertTrue(graph.HasClosingTag)
		self.assertEqual("""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="2"
  parse.edges="1"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">\n""", graph.OpeningTag(0))
		self.assertEqual("""</graph>\n""", graph.ClosingTag(0))
		self.assertListEqual([
			"""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="2"
  parse.edges="1"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">\n""",
			"""  <node id="n1" />\n""",
			"""  <node id="n2" />\n""",
			"""  <edge id="e1" source="n1" target="n2" />\n""",
			"""</graph>\n"""
		], graph.ToStringLines(0))

		print()
		for line in graph.ToStringLines():
			print(line, end="")

	def test_GraphWithSubgraph(self) -> None:
		graph = Graph(None, "g1")

		graph.AddNode(Node("n1"))
		graph.AddNode(Node("n2"))
		graph.AddEdge(Edge("e1", graph.GetNode("n1"), graph.GetNode("n2")))

		sg1 = graph.AddSubgraph(Subgraph("nsg1", "sg1"))
		sg1.AddNode(Node("sg1n1"))
		sg1.AddNode(Node("sg1n2"))
		sg1.AddEdge(Edge("sg1e1", sg1.GetNode("sg1n1"), sg1.GetNode("sg1n2")))

		sg2 = graph.AddSubgraph(Subgraph("nsg2", "sg2"))
		sg2.AddNode(Node("sg2n1"))
		sg2.AddNode(Node("sg2n2"))
		sg2.AddEdge(Edge("sg2e1", sg2.GetNode("sg2n1"), sg2.GetNode("sg2n2")))

		graph.AddEdge(Edge("e2", graph.GetNode("n1"), sg1.GetNode("sg1n2")))
		graph.AddEdge(Edge("e3", graph.GetNode("n2"), sg2.GetNode("sg2n1")))
		graph.AddEdge(Edge("e4", sg1.GetNode("sg1n1"), sg2.GetNode("sg2n2")))

		self.assertTrue(graph.HasClosingTag)
		self.assertEqual(2, len(graph.Subgraphs))

		print()
		for line in graph.ToStringLines():
			print(line, end="")

	def test_GraphML(self) -> None:
		doc = GraphMLDocument("g1")

		self.assertIsInstance(doc._graph, Graph)

		print()
		for line in doc.ToStringLines():
			print(line, end="")


class pyToolingGraph(TestCase):
	def test_ConvertGraph(self) -> None:
		graph = pyTooling_Graph(name="g1")

		vertex1 = Vertex(vertexID="n1", value="v1", graph=graph)
		vertex2 = Vertex(vertexID="n2", value="v2", graph=graph)
		edge = vertex1.EdgeToVertex(vertex2, edgeValue="v12", edgeWeight=1)

		doc = GraphMLDocument()
		doc.FromGraph(graph)

		self.assertEqual("g1", doc._graph.ID)
		self.assertEqual(2, len(doc._graph._nodes))
		self.assertEqual(1, len(doc._graph._edges))

		print()
		for line in doc.ToStringLines():
			print(line, end="")

	def test_ConvertSubgraph(self) -> None:
		graph = pyTooling_Graph(name="g1")
		subgraph1 = pyTooling_Subgraph(name="sg1", graph=graph)
		subgraph2 = pyTooling_Subgraph(name="sg2", graph=graph)

		vertex1 = Vertex(vertexID="n1", value="v1", graph=graph)
		vertex2 = Vertex(vertexID="n2", value="v2", graph=graph)
		vertex3 = Vertex(vertexID="n3", value="v3", subgraph=subgraph1)
		vertex4 = Vertex(vertexID="n4", value="v4", subgraph=subgraph1)
		vertex5 = Vertex(vertexID="n5", value="v5", subgraph=subgraph2)
		vertex6 = Vertex(vertexID="n6", value="v6", subgraph=subgraph2)

		edge12 = vertex1.EdgeToVertex(vertex2, edgeValue="v12", edgeWeight=1)
		edge34 = vertex3.EdgeToVertex(vertex4, edgeValue="v34", edgeWeight=1)
		edge56 = vertex5.EdgeToVertex(vertex6, edgeValue="v56", edgeWeight=1)

		link13 = vertex1.LinkToVertex(vertex3, linkValue="v13", linkWeight=2)
		link25 = vertex2.LinkToVertex(vertex5, linkValue="v25", linkWeight=2)
		link46 = vertex4.LinkToVertex(vertex6, linkValue="v46", linkWeight=2)

		doc = GraphMLDocument()
		doc.FromGraph(graph)

		self.assertEqual("g1", doc._graph.ID)
		self.assertEqual(2, len(doc._graph._subgraphs))
		self.assertEqual(4, len(doc._graph._nodes))
		self.assertEqual(1, len(doc._graph._edges))

		print()
		for line in doc.ToStringLines():
			print(line, end="")


class pyToolingTree(TestCase):
	def test_Conversion(self) -> None:
		root = pyToolingNode(nodeID="n0", value="v0")
		child1 = pyToolingNode("n1", "v1", parent=root)
		child2 = pyToolingNode("n2", "v2", parent=root)

		doc = GraphMLDocument()
		doc.FromTree(root)

		self.assertEqual("n0", doc._graph.ID)
		self.assertEqual(3, len(doc._graph._nodes))
		self.assertEqual(2, len(doc._graph._edges))

		print()
		for line in doc.ToStringLines():
			print(line, end="")
