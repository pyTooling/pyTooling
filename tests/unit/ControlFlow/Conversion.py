# ==================================================================================================================== #
#             _____           _ _               ____            _             _ _____ _                                #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ | |_ _ __ ___ | |  ___| | _____      __                 #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ \| __| '__/ _ \| | |_  | |/ _ \ \ /\ / /                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | |_| | | (_) | |  _| | | (_) \ V  V /                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_|\__|_|  \___/|_|_|   |_|\___/ \_/\_/                   #
# |_|    |___/                          |___/                                                                          #
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
"""
Unit tests for :mod:`pyTooling.ControlFlow`: converting a control flow graph into a :class:`~pyTooling.Graph.Graph`,
and writing that as a GraphML document.
"""
from xml.dom.minidom         import parseString

from pyTooling.ControlFlow   import ControlFlowGraph, BasicBlock, Edge, BlockKind, EdgeKind
from pyTooling.Graph         import Graph
from pyTooling.Graph.GraphML import GraphMLDocument
from pyTooling.Testing       import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ToGraph(Testcase):
	def test_Empty(self) -> None:
		graph = ControlFlowGraph("main").ToGraph()

		self.assertIsInstance(graph, Graph)
		self.assertEqual("main", graph.Name)
		self.assertEqual(2, graph.VertexCount)
		self.assertEqual(0, graph.EdgeCount)
		self.assertEqual(BlockKind.Entry, graph.GetVertexByID("entry")["kind"])
		self.assertEqual(BlockKind.Exit, graph.GetVertexByID("exit")["kind"])

	def test_Vertices(self) -> None:
		cfg = ControlFlowGraph("main", entryID=0, exitID=1)

		cfg.Entry.Count = 3
		BasicBlock(cfg, 2, count=3, value="x = 1;")
		BasicBlock(cfg, 3)
		BasicBlock(cfg, 4, kind=BlockKind.Unwind)

		graph = cfg.ToGraph()

		self.assertListEqual([0, 1, 2, 3, 4], [vertex.ID for vertex in graph.IterateVertices()])

		entry = graph.GetVertexByID(0)
		self.assertIsNone(entry.Value)
		self.assertDictEqual({"kind": BlockKind.Entry, "count": 3}, entry._dict)

		code = graph.GetVertexByID(2)
		self.assertEqual("x = 1;", code.Value)
		self.assertDictEqual({"kind": BlockKind.Code, "count": 3}, code._dict)

		self.assertDictEqual({"kind": BlockKind.Code}, graph.GetVertexByID(3)._dict)
		self.assertDictEqual({"kind": BlockKind.Unwind}, graph.GetVertexByID(4)._dict)

	def test_Edges(self) -> None:
		cfg =   ControlFlowGraph("main")
		block = BasicBlock(cfg, 2)
		Edge(cfg.Entry, block, EdgeKind.FallThrough, count=5)
		Edge(block, cfg.Exit, EdgeKind.Jump, value="return")
		Edge(block, cfg.Exit, EdgeKind.Abnormal, count=1)

		graph = cfg.ToGraph()
		edges = list(graph.IterateEdges())

		self.assertEqual(3, graph.EdgeCount)
		self.assertListEqual(
			[("entry", 2), (2, "exit"), (2, "exit")],
			[(edge.Source.ID, edge.Destination.ID) for edge in edges]
		)
		self.assertListEqual([EdgeKind.FallThrough, EdgeKind.Jump, EdgeKind.Abnormal], [edge.Kind for edge in edges])
		self.assertListEqual([None, "return", None], [edge.Value for edge in edges])
		self.assertListEqual(
			[
				{"kind": EdgeKind.FallThrough, "count": 5},
				{"kind": EdgeKind.Jump},
				{"kind": EdgeKind.Abnormal, "count": 1}
			],
			[edge._dict for edge in edges]
		)

	def test_Loop(self) -> None:
		"""An edge points in the direction control flows, so a loop is a cycle of the graph."""
		cfg =       ControlFlowGraph("main")
		condition = BasicBlock(cfg, "while")
		body =      BasicBlock(cfg, "body")
		Edge(cfg.Entry, condition, EdgeKind.FallThrough)
		Edge(condition, body, EdgeKind.FallThrough)
		Edge(body, condition, EdgeKind.Jump)
		Edge(condition, cfg.Exit, EdgeKind.Jump)

		graph = cfg.ToGraph()

		self.assertTrue(graph.HasCycle())
		self.assertListEqual(["body", "exit"], [vertex.ID for vertex in graph.GetVertexByID("while").Successors])


class GraphML(Testcase):
	def test_Document(self) -> None:
		cfg =    ControlFlowGraph("Parse", entryID=0, exitID=1)
		block =  BasicBlock(cfg, 2, count=2, value="if (x < 0)")
		unwind = BasicBlock(cfg, 3, kind=BlockKind.Unwind)

		cfg.Entry.Count = 2
		Edge(cfg.Entry, block, EdgeKind.FallThrough, count=2)
		Edge(block, cfg.Exit, EdgeKind.Jump, count=1)
		Edge(block, unwind, EdgeKind.Exception, count=1)

		document = GraphMLDocument()
		document.FromGraph(cfg.ToGraph())
		dom = parseString("".join(document.ToStringLines()))

		keys = {
			key.getAttribute("id"): (key.getAttribute("for"), key.getAttribute("attr.name"))
			for key in dom.getElementsByTagName("key")
		}
		self.assertDictEqual(
			{
				"nodeValue": ("node", "value"),
				"edgeValue": ("edge", "value"),
				"nodekind":  ("node", "kind"),
				"nodecount": ("node", "count"),
				"edgekind":  ("edge", "kind"),
				"edgecount": ("edge", "count")
			},
			keys
		)

		graph = dom.getElementsByTagName("graph")[0]
		self.assertEqual("Parse", graph.getAttribute("id"))

		nodes = {
			node.getAttribute("id"): {
				data.getAttribute("key"): data.firstChild.data for data in node.getElementsByTagName("data")
			}
			for node in graph.getElementsByTagName("node")
		}
		self.assertDictEqual(
			{
				"0": {"nodekind": "Entry", "nodecount": "2"},
				"1": {"nodekind": "Exit"},
				"2": {"nodeValue": "if (x < 0)", "nodekind": "Code", "nodecount": "2"},
				"3": {"nodekind": "Unwind"}
			},
			nodes
		)

		edges = [
			(
				edge.getAttribute("source"),
				edge.getAttribute("target"),
				{data.getAttribute("key"): data.firstChild.data for data in edge.getElementsByTagName("data")}
			)
			for edge in graph.getElementsByTagName("edge")
		]
		self.assertListEqual(
			[
				("0", "2", {"edgekind": "FallThrough", "edgecount": "2"}),
				("2", "1", {"edgekind": "Jump", "edgecount": "1"}),
				("2", "3", {"edgekind": "Exception", "edgecount": "1"})
			],
			edges
		)
