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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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

from pyTooling.Graph.GraphML import AttributeContext, AttributeTypes, Key, Data, Node, Edge, Graph, GraphMLDocument


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Construction(TestCase):
	def test_Key(self):
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		self.assertEqual("k1", key.ID)
		self.assertEqual("color", str(key.AttributeName))
		self.assertEqual("string", str(key.AttributeType))

		self.assertFalse(key.HasClosingTag)
		self.assertEqual("""<key id="k1" for="node" attr.name="color" attr.type="string" />""", key.Tag(0))
		self.assertListEqual([
				"""<key id="k1" for="node" attr.name="color" attr.type="string" />"""
			], key.ToStringLines(0))

	def test_Data(self):
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)
		data = Data(key, "violet")

		self.assertEqual(key, data.Key)
		self.assertEqual("violet", data.Data)

		self.assertFalse(data.HasClosingTag)
		self.assertEqual("""<data key="k1">violet</data>""", data.Tag(0))
		self.assertListEqual([
				"""<data key="k1">violet</data>"""
			], data.ToStringLines(0))

	def test_Node(self):
		node = Node("n1")

		self.assertEqual("n1", node.ID)

		self.assertFalse(node.HasClosingTag)
		self.assertEqual("""<node id="n1" />""", node.Tag(0))
		self.assertListEqual([
				"""<node id="n1" />"""
			], node.ToStringLines(0))

	def test_NodeWithData(self):
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		node = Node("n1")
		node.AddData(Data(key, "violet"))

		self.assertEqual("n1", node.ID)

		self.assertTrue(node.HasClosingTag)
		self.assertEqual("""<node id="n1">""", node.OpeningTag(0))
		self.assertEqual("""</node>""", node.ClosingTag(0))
		self.assertListEqual([
				"""<node id="n1">""",
				"""  <data key="k1">violet</data>""",
				"""</node>"""
			], node.ToStringLines(0))

	def test_Edge(self):
		node1 = Node("n1")
		node2 = Node("n2")
		edge = Edge("e1", node1, node2)

		self.assertFalse(edge.HasClosingTag)
		self.assertEqual("""<edge id="e1" source="n1" target="n2" />""", edge.Tag(0))
		self.assertListEqual([
				"""<edge id="e1" source="n1" target="n2" />"""
			], edge.ToStringLines(0))

	def test_EdgeWithData(self):
		key = Key("k1", AttributeContext.Node, "color", AttributeTypes.String)

		node1 = Node("n1")
		node2 = Node("n2")
		edge = Edge("e1", node1, node2)
		edge.AddData(Data(key, "violet"))

		self.assertEqual("e1", edge.ID)

		self.assertTrue(edge.HasClosingTag)
		self.assertEqual("""<edge id="e1" source="n1" target="n2">""", edge.OpeningTag(0))
		self.assertEqual("""</edge>""", edge.ClosingTag(0))
		self.assertListEqual([
				"""<edge id="e1" source="n1" target="n2">""",
				"""  <data key="k1">violet</data>""",
				"""</edge>"""
			], edge.ToStringLines(0))

	def test_Graph(self):
		graph = Graph("g1")

		self.assertTrue(graph.HasClosingTag)
		self.assertEqual("""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="0"
  parse.edges="0"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">""", graph.OpeningTag(0))
		self.assertEqual("""</graph>""", graph.ClosingTag(0))
		self.assertListEqual([
			"""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="0"
  parse.edges="0"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">""",
				"""</graph>"""
			], graph.ToStringLines(0))

	def test_GraphWithNodesAndEdges(self):
		graph = Graph("g1")

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
  parse.edgeids="free">""", graph.OpeningTag(0))
		self.assertEqual("""</graph>""", graph.ClosingTag(0))
		self.assertListEqual([
			"""\
<graph id="g1"
  edgedefault="directed"
  parse.nodes="2"
  parse.edges="1"
  parse.order="nodesfirst"
  parse.nodeids="free"
  parse.edgeids="free">""",
			"""  <node id="n1" />""",
			"""  <node id="n2" />""",
			"""  <edge id="e1" source="n1" target="n2" />""",
			"""</graph>"""
		], graph.ToStringLines(0))
