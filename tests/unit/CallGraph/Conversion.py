# ==================================================================================================================== #
#             _____           _ _               ____      _ _  ____                 _                                  #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _| | |/ ___|_ __ __ _ _ __ | |__                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | | | |  _| '__/ _` | '_ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | | | |_| | | | (_| | |_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|_|\____|_|  \__,_| .__/|_| |_|                             #
# |_|    |___/                          |___/                                |_|                                       #
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
Unit tests for :mod:`pyTooling.CallGraph`: converting a call graph into a :class:`~pyTooling.Graph.Graph`, and writing
that as a GraphML document.
"""
from xml.dom.minidom         import parseString

from pyTooling.CallGraph     import CallGraph, Function, Call, FunctionKind, CallKind
from pyTooling.ControlFlow   import ControlFlowGraph, BasicBlock
from pyTooling.Graph         import Graph
from pyTooling.Graph.GraphML import GraphMLDocument
from pyTooling.Testing       import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ToGraph(Testcase):
	def test_Empty(self) -> None:
		graph = CallGraph("prog").ToGraph()

		self.assertIsInstance(graph, Graph)
		self.assertEqual("prog", graph.Name)
		self.assertEqual(0, graph.VertexCount)
		self.assertEqual(0, graph.EdgeCount)

	def test_Vertices(self) -> None:
		callGraph = CallGraph("prog")
		Function(callGraph, "main", count=1)
		Function(callGraph, "Sum", controlFlowGraph=ControlFlowGraph("Sum"), value="prog.c:7")
		Function(callGraph, "printf", kind=FunctionKind.External)
		Function(callGraph, "__indirect_call", kind=FunctionKind.Unknown)

		graph = callGraph.ToGraph()

		self.assertListEqual(
			["main", "Sum", "printf", "__indirect_call"],
			[vertex.ID for vertex in graph.IterateVertices()]
		)

		main = graph.GetVertexByID("main")
		self.assertIsNone(main.Value)
		self.assertDictEqual({"kind": FunctionKind.Defined, "count": 1}, main._dict)

		summation = graph.GetVertexByID("Sum")
		self.assertEqual("prog.c:7", summation.Value)
		self.assertDictEqual({"kind": FunctionKind.Defined}, summation._dict)

		self.assertDictEqual({"kind": FunctionKind.External}, graph.GetVertexByID("printf")._dict)
		self.assertDictEqual({"kind": FunctionKind.Unknown}, graph.GetVertexByID("__indirect_call")._dict)

	def test_Edges(self) -> None:
		cfg =       ControlFlowGraph("Apply")
		block =     BasicBlock(cfg, 2)
		callGraph = CallGraph("prog")
		main =      Function(callGraph, "main")
		apply =     Function(callGraph, "Apply", controlFlowGraph=cfg)
		indirect =  Function(callGraph, "__indirect_call", kind=FunctionKind.Unknown)
		Call(main, apply, CallKind.Direct, count=1, value="prog.c:11:3")
		Call(main, apply)
		Call(apply, indirect, CallKind.Indirect, callSite=block, count=1)

		graph = callGraph.ToGraph()
		edges = list(graph.IterateEdges())

		self.assertEqual(3, graph.EdgeCount)
		self.assertListEqual(
			[("main", "Apply"), ("main", "Apply"), ("Apply", "__indirect_call")],
			[(edge.Source.ID, edge.Destination.ID) for edge in edges]
		)
		self.assertListEqual([CallKind.Direct, CallKind.Default, CallKind.Indirect], [edge.Kind for edge in edges])
		self.assertListEqual(["prog.c:11:3", None, None], [edge.Value for edge in edges])
		self.assertListEqual(
			[
				{"kind": CallKind.Direct, "count": 1},
				{"kind": CallKind.Default},
				{"kind": CallKind.Indirect, "count": 1, "callsite": 2}
			],
			[edge._dict for edge in edges]
		)

	def test_Recursion(self) -> None:
		"""A call points from the caller to the callee, so a recursion is a cycle of the graph."""
		callGraph = CallGraph("prog")
		main =      Function(callGraph, "main")
		even =      Function(callGraph, "IsEven")
		odd =       Function(callGraph, "IsOdd")
		Call(main, even)
		Call(even, odd)
		Call(odd, even)

		graph = callGraph.ToGraph()

		self.assertTrue(graph.HasCycle())
		self.assertListEqual(["IsEven"], [vertex.ID for vertex in graph.GetVertexByID("IsOdd").Successors])
		self.assertListEqual(["main", "IsOdd"], [vertex.ID for vertex in graph.GetVertexByID("IsEven").Predecessors])


class GraphML(Testcase):
	def test_Document(self) -> None:
		cfg =       ControlFlowGraph("Fib", entryID=0, exitID=1)
		block =     BasicBlock(cfg, 3, count=7)
		callGraph = CallGraph("prog")
		main =      Function(callGraph, "main", count=1)
		fib =       Function(callGraph, "Fib", controlFlowGraph=cfg, count=15, value="prog.c:4")
		printf =    Function(callGraph, "printf", kind=FunctionKind.External)
		Call(main, fib, CallKind.Direct, count=1)
		Call(main, printf, CallKind.Direct)
		Call(fib, fib, CallKind.Direct, callSite=block, count=7, value="Fib(n - 1)")

		document = GraphMLDocument()
		document.FromGraph(callGraph.ToGraph())
		dom = parseString("".join(document.ToStringLines()))

		keys = {
			key.getAttribute("id"): (key.getAttribute("for"), key.getAttribute("attr.name"))
			for key in dom.getElementsByTagName("key")
		}
		self.assertDictEqual(
			{
				"nodeValue":    ("node", "value"),
				"edgeValue":    ("edge", "value"),
				"nodekind":     ("node", "kind"),
				"nodecount":    ("node", "count"),
				"edgekind":     ("edge", "kind"),
				"edgecount":    ("edge", "count"),
				"edgecallsite": ("edge", "callsite")
			},
			keys
		)

		graph = dom.getElementsByTagName("graph")[0]
		self.assertEqual("prog", graph.getAttribute("id"))

		nodes = {
			node.getAttribute("id"): {
				data.getAttribute("key"): data.firstChild.data for data in node.getElementsByTagName("data")
			}
			for node in graph.getElementsByTagName("node")
		}
		self.assertDictEqual(
			{
				"main":   {"nodekind": "Defined", "nodecount": "1"},
				"Fib":    {"nodeValue": "prog.c:4", "nodekind": "Defined", "nodecount": "15"},
				"printf": {"nodekind": "External"}
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
				("main", "Fib", {"edgekind": "Direct", "edgecount": "1"}),
				("main", "printf", {"edgekind": "Direct"}),
				("Fib", "Fib", {"edgeValue": "Fib(n - 1)", "edgekind": "Direct", "edgecount": "7", "edgecallsite": "3"})
			],
			edges
		)
