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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.Graph.GraphML`: constructing a GraphML document, and converting a
:mod:`pyTooling.Graph` graph or a :mod:`pyTooling.Tree` tree into one.
"""
from xml.dom.minidom         import parseString

from pyTooling.Graph         import Graph as pyTooling_Graph, Subgraph as pyTooling_Subgraph, Vertex
from pyTooling.Graph.GraphML import AttributeContext, AttributeTypes, Key, Data, Node, Edge, Graph, Subgraph, GraphMLDocument
from pyTooling.Tree          import Node as pyToolingNode
from pyTooling.Testing       import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Construction(Testcase):
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


class pyToolingGraph(Testcase):
	def test_ConvertGraph(self) -> None:
		graph = pyTooling_Graph(name="g1")

		vertex1 = Vertex(vertexID="n1", value="v1", graph=graph)
		vertex2 = Vertex(vertexID="n2", value="v2", graph=graph)
		edge = vertex1.EdgeToVertex(vertex2, edgeValue="v12", edgeWeight=1)

		doc = GraphMLDocument()
		doc.FromGraph(graph)

		self.assertEqual("g1", doc._graph.ID)
		self.assertEqual(2, len(doc._graph._nodes))
		self.assertEqual(0, len(doc._graph._edges))
		self.assertEqual(1, len(doc._graph._edgesWithoutID))

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
		self.assertEqual(0, len(doc._graph._edges))
		self.assertEqual(4, len(doc._graph._edgesWithoutID))

		print()
		for line in doc.ToStringLines():
			print(line, end="")


	def test_ConvertSubgraph_Links(self) -> None:
		"""A link between two subgraphs is written once, as an edge of the root graph, with its key-value pairs."""
		graph = pyTooling_Graph(name="g1")
		subgraph1 = pyTooling_Subgraph(name="sg1", graph=graph)
		subgraph2 = pyTooling_Subgraph(name="sg2", graph=graph)
		vertex1 = Vertex(vertexID="n1", graph=graph)
		vertex2 = Vertex(vertexID="n2", subgraph=subgraph1)
		vertex3 = Vertex(vertexID="n3", subgraph=subgraph2)
		vertex1.LinkToVertex(vertex2)
		vertex2.LinkToVertex(vertex3, linkValue="v23", keyValuePairs={"kind": "runtime"})

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		dom = parseString("".join(doc.ToStringLines()))

		rootEdges = [element for element in dom.getElementsByTagName("graph")[0].childNodes if element.nodeName == "edge"]
		self.assertSetEqual(
			{("n1", "n2"), ("n2", "n3")},
			{(edge.getAttribute("source"), edge.getAttribute("target")) for edge in rootEdges}
		)
		self.assertEqual(2, len(rootEdges))
		self.assertEqual(2, len(dom.getElementsByTagName("edge")), "No link is written a second time, in a subgraph.")
		self.assertEqual(
			{"edgeValue": "v23", "linkkind": "runtime"},
			{data.getAttribute("key"): data.firstChild.data for data in dom.getElementsByTagName("data")}
		)

	def test_ConvertSubgraph_KeyValuePairs(self) -> None:
		"""A key of the vertices and edges in subgraphs is declared once; a missing value adds no data item."""
		graph = pyTooling_Graph(name="g1")
		subgraph1 = pyTooling_Subgraph(name="sg1", graph=graph)
		subgraph2 = pyTooling_Subgraph(name="sg2", graph=graph)
		vertex1 = Vertex(vertexID="n1", subgraph=subgraph1, keyValuePairs={"license": "MIT"})
		vertex2 = Vertex(vertexID="n2", subgraph=subgraph1, keyValuePairs={"license": "BSD-3-Clause"})
		Vertex(vertexID="n3", subgraph=subgraph2, keyValuePairs={"license": "MIT"})
		vertex1.EdgeToVertex(vertex2, keyValuePairs={"kind": "runtime"})

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		text = "".join(doc.ToStringLines())

		self.assertNotIn("None", text)
		self.assertEqual(1, text.count('<key id="nodelicense"'))
		self.assertEqual(1, text.count('<key id="edgekind"'))
		self.assertEqual(3, text.count('<data key="nodelicense">'))
		self.assertNotIn('<data key="nodeValue">', text)

	def test_ConvertGraph_WithoutValues(self) -> None:
		"""A vertex or edge without a value gets no data item, and an edge without an ID no 'id' attribute."""
		graph = pyTooling_Graph(name="g1")
		vertex1 = Vertex(vertexID="n1", graph=graph)
		vertex2 = Vertex(vertexID="n2", graph=graph)
		vertex1.EdgeToVertex(vertex2)

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		text = "".join(doc.ToStringLines())

		self.assertNotIn("None", text)
		self.assertIn('<edge source="n1" target="n2" />', text)
		self.assertListEqual([], doc._graph.GetNode("n1").Data)

	def test_ConvertGraph_EdgesWithoutIDs(self) -> None:
		"""Every edge without an ID is written, before those with an ID; ``Edges`` and ``EdgesWithoutID`` split them."""
		graph = pyTooling_Graph(name="g1")
		vertex1 = Vertex(vertexID="n1", graph=graph)
		vertex2 = Vertex(vertexID="n2", graph=graph)
		vertex3 = Vertex(vertexID="n3", graph=graph)
		vertex1.EdgeToVertex(vertex2)
		vertex2.EdgeToVertex(vertex3)
		vertex3.EdgeToVertex(vertex1, edgeID="e31")

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		dom = parseString("".join(doc.ToStringLines()))

		self.assertEqual("3", dom.getElementsByTagName("graph")[0].getAttribute("parse.edges"))
		edges = dom.getElementsByTagName("edge")
		self.assertListEqual(
			[("", "n1", "n2"), ("", "n2", "n3"), ("e31", "n3", "n1")],
			[tuple(edge.getAttribute(attr) for attr in ("id", "source", "target")) for edge in edges]
		)
		self.assertNotIn(None, doc._graph._ids)
		self.assertListEqual(["e31"], list(doc._graph.Edges))
		self.assertListEqual(
			[("n1", "n2"), ("n2", "n3")],
			[(edge.Source.ID, edge.Target.ID) for edge in doc._graph.EdgesWithoutID]
		)

	def test_ConvertGraph_KeyValuePairs(self) -> None:
		"""A key is declared once, however many vertices or edges carry it."""
		graph = pyTooling_Graph(name="g1")
		vertex1 = Vertex(vertexID="n1", graph=graph, keyValuePairs={"license": "MIT"})
		vertex2 = Vertex(vertexID="n2", graph=graph, keyValuePairs={"license": "BSD-3-Clause"})
		vertex3 = Vertex(vertexID="n3", graph=graph)
		vertex1.EdgeToVertex(vertex2, keyValuePairs={"kind": "runtime"})
		vertex1.EdgeToVertex(vertex3, keyValuePairs={"kind": "test"})

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		text = "".join(doc.ToStringLines())

		self.assertEqual(1, text.count('<key id="nodelicense"'))
		self.assertEqual(1, text.count('<key id="edgekind"'))
		self.assertIn('<data key="nodelicense">BSD-3-Clause</data>', text)
		self.assertIn('<data key="edgekind">test</data>', text)

	def test_ConvertGraph_Escaping(self) -> None:
		"""IDs and values with XML's special characters give a well-formed document, which reads back unchanged."""
		graph = pyTooling_Graph(name="a & b")
		vertex1 = Vertex(vertexID='say "<hi>"', graph=graph, keyValuePairs={"url": "https://example.org/?a=1&b=2"})
		vertex2 = Vertex(vertexID="n&2", graph=graph)
		vertex1.EdgeToVertex(vertex2, edgeID="e<1>")

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		dom = parseString("".join(doc.ToStringLines()))

		self.assertEqual("a & b", dom.getElementsByTagName("graph")[0].getAttribute("id"))
		self.assertListEqual(['say "<hi>"', "n&2"], [node.getAttribute("id") for node in dom.getElementsByTagName("node")])
		edge = dom.getElementsByTagName("edge")[0]
		self.assertListEqual(
			["e<1>", 'say "<hi>"', "n&2"],
			[edge.getAttribute(name) for name in ("id", "source", "target")]
		)
		self.assertEqual("https://example.org/?a=1&b=2", dom.getElementsByTagName("data")[0].firstChild.data)


	def test_ConvertGraph_WithoutIDs(self) -> None:
		"""A vertex without an ID gets a generated one, which no vertex' ID is; a graph without a name keeps 'G'."""
		graph = pyTooling_Graph()
		vertex1 = Vertex(graph=graph)
		vertex2 = Vertex(vertexID="vertex1", graph=graph)
		vertex3 = Vertex(graph=graph)
		vertex1.EdgeToVertex(vertex2)
		vertex3.EdgeToVertex(vertex1)

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		dom = parseString("".join(doc.ToStringLines()))

		self.assertEqual("G", dom.getElementsByTagName("graph")[0].getAttribute("id"))
		self.assertSetEqual(
			{"vertex1", "vertex2", "vertex3"},
			{node.getAttribute("id") for node in dom.getElementsByTagName("node")}
		)
		self.assertSetEqual(
			{("vertex2", "vertex1"), ("vertex3", "vertex2")},
			{(edge.getAttribute("source"), edge.getAttribute("target")) for edge in dom.getElementsByTagName("edge")}
		)

	def test_ConvertSubgraph_WithoutIDs(self) -> None:
		"""Generated IDs are unique across the subgraphs and numbered by subgraph name; an edge finds its nodes."""
		graph = pyTooling_Graph(name="g1")
		subgraph2 = pyTooling_Subgraph(name="sg2", graph=graph)
		subgraph1 = pyTooling_Subgraph(name="sg1", graph=graph)
		vertex1 = Vertex(subgraph=subgraph1)
		vertex2 = Vertex(subgraph=subgraph1)
		vertex3 = Vertex(subgraph=subgraph2)
		vertex1.EdgeToVertex(vertex2)

		doc = GraphMLDocument()
		doc.FromGraph(graph)
		dom = parseString("".join(doc.ToStringLines()))

		nodeIDs = {node.getAttribute("id") for node in dom.getElementsByTagName("node")}
		self.assertSetEqual({"vertex1", "vertex2", "vertex3"}, {node for node in nodeIDs if node.startswith("vertex")})
		edge = dom.getElementsByTagName("edge")[0]
		self.assertEqual(("vertex1", "vertex2"), (edge.getAttribute("source"), edge.getAttribute("target")))


class pyToolingTree(Testcase):
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

	def test_Conversion_WithoutValues(self) -> None:
		root = pyToolingNode(nodeID="n0")
		pyToolingNode("n1", parent=root)

		doc = GraphMLDocument()
		doc.FromTree(root)

		self.assertNotIn("None", "".join(doc.ToStringLines()))

	def test_Conversion_WithoutIDs(self) -> None:
		"""A tree node without an ID gets a generated one; a root without an ID keeps the graph ID 'G'."""
		root = pyToolingNode()
		child1 = pyToolingNode(parent=root)
		pyToolingNode("vertex2", parent=root)
		pyToolingNode(parent=child1)

		doc = GraphMLDocument()
		doc.FromTree(root)
		dom = parseString("".join(doc.ToStringLines()))

		self.assertEqual("G", dom.getElementsByTagName("graph")[0].getAttribute("id"))
		self.assertSetEqual(
			{"vertex1", "vertex2", "vertex3", "vertex4"},
			{node.getAttribute("id") for node in dom.getElementsByTagName("node")}
		)
		self.assertSetEqual(
			{("vertex3", "vertex1"), ("vertex2", "vertex1"), ("vertex4", "vertex3")},
			{(edge.getAttribute("source"), edge.getAttribute("target")) for edge in dom.getElementsByTagName("edge")}
		)
