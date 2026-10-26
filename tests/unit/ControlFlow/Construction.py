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
Unit tests for :mod:`pyTooling.ControlFlow`: constructing blocks, edges and graphs, and the checks of their parameters.
"""
from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, Edge, BlockKind, EdgeKind, ControlFlowError, \
                                  DuplicateBlockError, DuplicateEdgeError
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Construction(Testcase):
	def test_ControlFlowGraph(self) -> None:
		graph = ControlFlowGraph("main")

		self.assertEqual("main", graph.Name)
		self.assertEqual("entry", graph.Entry.ID)
		self.assertIs(BlockKind.Entry, graph.Entry.Kind)
		self.assertEqual("exit", graph.Exit.ID)
		self.assertIs(BlockKind.Exit, graph.Exit.Kind)
		self.assertIsNone(graph.Unwind)
		self.assertEqual(2, graph.BlockCount)
		self.assertListEqual([graph.Entry, graph.Exit], list(graph.IterateBlocks()))
		self.assertEqual(0, len(graph), "A new graph has no key-value-pairs.")
		self.assertDictEqual({"entry": graph.Entry, "exit": graph.Exit}, graph.Blocks)
		self.assertListEqual([], graph.Edges)

	def test_ControlFlowGraph_IDs(self) -> None:
		graph = ControlFlowGraph("main", entryID=0, exitID=1)

		self.assertIs(graph.Entry, graph.GetBlock(0))
		self.assertIs(graph.Exit, graph.GetBlock(1))
		self.assertTrue(graph.ContainsBlock(0))
		self.assertFalse(graph.ContainsBlock("entry"))

		with self.assertRaises(KeyError):
			_ = graph.GetBlock(2)

	def test_BasicBlock(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)

		self.assertIs(graph, block.ControlFlowGraph)
		self.assertEqual(2, block.ID)
		self.assertIs(BlockKind.Code, block.Kind)
		self.assertIsNone(block.Count)
		self.assertIsNone(block.Value)
		self.assertTupleEqual((), block.InboundEdges)
		self.assertTupleEqual((), block.OutboundEdges)
		self.assertIs(block, graph.GetBlock(2))
		self.assertTrue(graph.ContainsBlock(2))
		self.assertEqual(3, graph.BlockCount)

	def test_BasicBlock_CountAndValue(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2, count=5, value=(3, 4))

		self.assertEqual(5, block.Count)
		self.assertTupleEqual((3, 4), block.Value)

		block.Count = 0
		block.Value = "line 3"
		self.assertEqual(0, block.Count)
		self.assertEqual("line 3", block.Value)

		block.Count = None
		self.assertIsNone(block.Count)

	def test_BasicBlock_Unwind(self) -> None:
		graph =  ControlFlowGraph("main")
		unwind = BasicBlock(graph, "unwind", kind=BlockKind.Unwind)

		self.assertIs(unwind, graph.Unwind)
		self.assertIs(BlockKind.Unwind, unwind.Kind)
		self.assertEqual(3, graph.BlockCount)

	def test_Edge(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)
		edge1 = Edge(graph.Entry, block)
		edge2 = Edge(block, graph.Exit, EdgeKind.Jump, count=7, value="return")

		self.assertIs(graph.Entry, edge1.Source)
		self.assertIs(block, edge1.Destination)
		self.assertIs(EdgeKind.Default, edge1.Kind)
		self.assertIsNone(edge1.Count)
		self.assertIsNone(edge1.Value)
		self.assertIs(EdgeKind.Jump, edge2.Kind)
		self.assertEqual(7, edge2.Count)
		self.assertEqual("return", edge2.Value)

		self.assertTupleEqual((edge1,), graph.Entry.OutboundEdges)
		self.assertTupleEqual((edge1,), block.InboundEdges)
		self.assertTupleEqual((edge2,), block.OutboundEdges)
		self.assertTupleEqual((edge2,), graph.Exit.InboundEdges)
		self.assertListEqual([edge1, edge2], graph.Edges)

	def test_EdgeTo(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)

		edge = graph.Entry.EdgeTo(block, 3, "start", EdgeKind.FallThrough, {"label": "start"})

		self.assertIs(graph.Entry, edge.Source)
		self.assertIs(block, edge.Destination)
		self.assertEqual(3, edge.Count)
		self.assertEqual("start", edge.Value)
		self.assertIs(EdgeKind.FallThrough, edge.Kind)
		self.assertEqual("start", edge["label"])
		self.assertTupleEqual((edge, ), graph.Entry.OutboundEdges)
		self.assertTupleEqual((edge, ), block.InboundEdges)
		self.assertListEqual([edge], graph.Edges)

	def test_EdgeFrom(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)

		edge = graph.Exit.EdgeFrom(block, edgeKind=EdgeKind.Jump)

		self.assertIs(block, edge.Source)
		self.assertIs(graph.Exit, edge.Destination)
		self.assertIsNone(edge.Count)
		self.assertIsNone(edge.Value)
		self.assertIs(EdgeKind.Jump, edge.Kind)
		self.assertEqual(0, len(edge))
		self.assertTupleEqual((edge, ), graph.Exit.InboundEdges)

	def test_EdgeTo_Checks(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)
		graph.Entry.EdgeTo(block)

		with self.assertRaises(DuplicateEdgeError):
			graph.Entry.EdgeTo(block)

		with self.assertRaises(ValueError):
			graph.Exit.EdgeTo(block)

		with self.assertRaises(ValueError):
			block.EdgeFrom(graph.Exit)

		with self.assertRaises(ValueError):
			block.EdgeTo(graph.Entry)

		with self.assertRaises(ValueError):
			block.EdgeTo(BasicBlock(ControlFlowGraph("other"), 3))

	def test_Edge_Kinds(self) -> None:
		"""Two blocks can be connected by one edge of each kind."""
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)
		edges = [Edge(graph.Entry, block, kind) for kind in EdgeKind]

		self.assertListEqual(edges, list(block.InboundEdges))

	def test_Kind_Str(self) -> None:
		self.assertEqual("Unwind", str(BlockKind.Unwind))
		self.assertEqual("FallThrough", str(EdgeKind.FallThrough))

	def test_Exceptions(self) -> None:
		self.assertTrue(issubclass(DuplicateBlockError, ControlFlowError))
		self.assertTrue(issubclass(DuplicateEdgeError, ControlFlowError))


class KeyValuePairs(Testcase):
	def test_ControlFlowGraph(self) -> None:
		graph = ControlFlowGraph("main", keyValuePairs={"file": "main.c"})

		self.assertEqual(1, len(graph))
		self.assertIn("file", graph)
		self.assertEqual("main.c", graph["file"])
		self.assertNotIn("entry", graph, "A block ID is no key-value-pair.")

	def test_BasicBlock(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2, keyValuePairs={"lines": (3, 4)})

		self.assertEqual((3, 4), block["lines"])
		self.assertEqual(1, len(block))

	def test_Edge(self) -> None:
		graph = ControlFlowGraph("main")
		edge =  Edge(graph.Entry, graph.Exit, keyValuePairs={"label": "return"})

		self.assertEqual("return", edge["label"])
		self.assertEqual(1, len(edge))

	def test_IterateBlocks(self) -> None:
		graph = ControlFlowGraph("main", entryID=0, exitID=1)
		BasicBlock(graph, 2)
		BasicBlock(graph, 3, kind=BlockKind.Unwind)

		self.assertListEqual([0, 1, 2, 3], [block.ID for block in graph.IterateBlocks()])
		self.assertListEqual(
			[2, 3],
			[block.ID for block in graph.IterateBlocks(lambda block: block.Kind not in (BlockKind.Entry, BlockKind.Exit))]
		)


class Checks(Testcase):
	def test_ControlFlowGraph_Name(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ControlFlowGraph(None)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = ControlFlowGraph(42)

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = ControlFlowGraph("")

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_ControlFlowGraph_IDs(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = ControlFlowGraph("main", entryID=None)

		self.assertEqual("Parameter 'entryID' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = ControlFlowGraph("main", exitID=[1])

		self.assertEqual("Parameter 'exitID' is not hashable.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = ControlFlowGraph("main", entryID=0, exitID=0)

		self.assertEqual("Parameter 'exitID' equals parameter 'entryID'.", str(context.exception))

	def test_BasicBlock_ControlFlowGraph(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = BasicBlock(None, 2)

		self.assertEqual("Parameter 'controlFlowGraph' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = BasicBlock("main", 2)

		self.assertEqual("Parameter 'controlFlowGraph' is not of type 'ControlFlowGraph'.", str(context.exception))

	def test_BasicBlock_ID(self) -> None:
		graph = ControlFlowGraph("main")
		_ =     BasicBlock(graph, 2)

		with self.assertRaises(ValueError) as context:
			_ = BasicBlock(graph, None)

		self.assertEqual("Parameter 'blockID' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = BasicBlock(graph, {2})

		self.assertEqual("Parameter 'blockID' is not hashable.", str(context.exception))

		with self.assertRaises(DuplicateBlockError) as context:
			_ = BasicBlock(graph, 2)

		self.assertEqual("Control flow graph 'main' has a block '2' already.", str(context.exception))
		self.assertEqual(2, context.exception.BlockID)
		self.assertIsNone(context.exception.Kind)
		self.assertEqual(3, graph.BlockCount)

	def test_BasicBlock_Kind(self) -> None:
		graph = ControlFlowGraph("main")
		_ =     BasicBlock(graph, "unwind", kind=BlockKind.Unwind)

		with self.assertRaises(ValueError) as context:
			_ = BasicBlock(graph, 2, kind=None)

		self.assertEqual("Parameter 'kind' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = BasicBlock(graph, 2, kind=EdgeKind.Jump)

		self.assertEqual("Parameter 'kind' is not of type 'BlockKind'.", str(context.exception))

		for kind, message in (
			(BlockKind.Entry,  "Control flow graph 'main' has an entry block already."),
			(BlockKind.Exit,   "Control flow graph 'main' has an exit block already."),
			(BlockKind.Unwind, "Control flow graph 'main' has an unwind block already.")
		):
			with self.subTest(kind=kind):
				with self.assertRaises(DuplicateBlockError) as context:
					_ = BasicBlock(graph, 2, kind=kind)

				self.assertEqual(message, str(context.exception))
				self.assertEqual(2, context.exception.BlockID)
				self.assertIs(kind, context.exception.Kind)

		self.assertEqual(3, graph.BlockCount)

	def test_DuplicateErrors_MessageOnly(self) -> None:
		"""The block's ID and the existing edge are required: raising an exception with a message only is a 'TypeError'."""
		with self.assertRaises(TypeError) as blockCapture:
			raise DuplicateBlockError("Duplicate block.")

		self.assertIn("'blockID'", str(blockCapture.exception))

		with self.assertRaises(TypeError) as edgeCapture:
			raise DuplicateEdgeError("Duplicate edge.")

		self.assertIn("'existingEdge'", str(edgeCapture.exception))

	def test_Count(self) -> None:
		graph = ControlFlowGraph("main")
		block = BasicBlock(graph, 2)

		for count in ("1", 1.0, True):
			with self.subTest(count=count):
				with self.assertRaises(TypeError) as context:
					_ = BasicBlock(graph, 3, count=count)

				self.assertEqual("Parameter 'count' is not of type 'int'.", str(context.exception))

				with self.assertRaises(TypeError):
					block.Count = count

		with self.assertRaises(ValueError) as context:
			_ = Edge(graph.Entry, block, count=-1)

		self.assertEqual("Parameter 'count' is negative.", str(context.exception))

		with self.assertRaises(ValueError):
			graph.Entry.Count = -1

		self.assertIsNone(block.Count)
		self.assertIsNone(graph.Entry.Count)
		self.assertNotIn(3, graph)
		self.assertListEqual([], graph.Edges)

	def test_Edge_Source(self) -> None:
		graph =  ControlFlowGraph("main")
		unwind = BasicBlock(graph, "unwind", kind=BlockKind.Unwind)
		block =  BasicBlock(graph, 2)

		with self.assertRaises(ValueError) as context:
			_ = Edge(None, block)

		self.assertEqual("Parameter 'source' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Edge(2, block)

		self.assertEqual("Parameter 'source' is not of type 'BasicBlock'.", str(context.exception))

		for source in (graph.Exit, unwind):
			with self.subTest(source=source.ID):
				with self.assertRaises(ValueError) as context:
					_ = Edge(source, block)

				self.assertEqual("Parameter 'source' is an exit or unwind block.", str(context.exception))

	def test_Edge_Destination(self) -> None:
		graph = ControlFlowGraph("main")
		other = ControlFlowGraph("other")
		block = BasicBlock(graph, 2)

		with self.assertRaises(ValueError) as context:
			_ = Edge(block, None)

		self.assertEqual("Parameter 'destination' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Edge(block, "exit")

		self.assertEqual("Parameter 'destination' is not of type 'BasicBlock'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = Edge(block, graph.Entry)

		self.assertEqual("Parameter 'destination' is an entry block.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = Edge(block, other.Exit)

		self.assertEqual(
			"Parameter 'destination' belongs to another graph than parameter 'source'.",
			str(context.exception)
		)
		self.assertListEqual([], graph.Edges)
		self.assertListEqual([], other.Edges)

	def test_Edge_Kind(self) -> None:
		graph = ControlFlowGraph("main")
		_ =     Edge(graph.Entry, graph.Exit, EdgeKind.FallThrough)

		with self.assertRaises(ValueError) as context:
			_ = Edge(graph.Entry, graph.Exit, None)

		self.assertEqual("Parameter 'kind' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Edge(graph.Entry, graph.Exit, BlockKind.Code)

		self.assertEqual("Parameter 'kind' is not of type 'EdgeKind'.", str(context.exception))

		with self.assertRaises(DuplicateEdgeError) as context:
			_ = Edge(graph.Entry, graph.Exit, EdgeKind.FallThrough)

		self.assertEqual("Blocks 'entry' and 'exit' are connected by such an edge already.", str(context.exception))
		self.assertEqual(1, len(graph.Edges))
		self.assertEqual(1, len(graph.Exit.InboundEdges))
		self.assertIs(graph.Exit.InboundEdges[0], context.exception.ExistingEdge)
