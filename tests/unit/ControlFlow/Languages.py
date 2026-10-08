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
Unit tests for :mod:`pyTooling.ControlFlow`: control flow graphs of C, C++ and Python functions.

Each testcase builds the graph of the function shown in its doc-string, the way a compiler or a code coverage tool
reports it, and checks the shape a language construct gives it.
"""
from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, Edge, BlockKind, EdgeKind
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class C(Testcase):
	def test_IfElseInLoop(self) -> None:
		"""
		A loop holding an ``if``/``else``, numbered like GCC numbers its blocks, with counts for ``Sum(4)``.

		.. code-block:: C

		   int Sum(int n) {
		     int s = 0;
		     for (int i = 0; i < n; i++)
		       if (i % 2) s += i; else s -= i;
		     return s;
		   }
		"""
		graph = ControlFlowGraph("Sum", entryID=0, exitID=1)

		graph.Entry.Count = 1
		graph.Exit.Count =  1

		init =      BasicBlock(graph, 2, count=1, value="int s = 0; int i = 0;")
		condition = BasicBlock(graph, 3, count=5, value="i < n")
		test =      BasicBlock(graph, 4, count=4, value="i % 2")
		then =      BasicBlock(graph, 5, count=2, value="s += i;")
		other =     BasicBlock(graph, 6, count=2, value="s -= i;")
		step =      BasicBlock(graph, 7, count=4, value="i++")
		ret =       BasicBlock(graph, 8, count=1, value="return s;")
		Edge(graph.Entry, init, EdgeKind.FallThrough, count=1)
		Edge(init, condition, EdgeKind.FallThrough, count=1)
		Edge(condition, test, EdgeKind.FallThrough, count=4)
		Edge(condition, ret, EdgeKind.Jump, count=1)
		Edge(test, then, EdgeKind.FallThrough, count=2)
		Edge(test, other, EdgeKind.Jump, count=2)
		Edge(then, step, EdgeKind.Jump, count=2)
		Edge(other, step, EdgeKind.FallThrough, count=2)
		loop = Edge(step, condition, EdgeKind.Jump, count=4)
		Edge(ret, graph.Exit, EdgeKind.FallThrough, count=1)

		self.assertEqual(9, len(graph))
		self.assertEqual(10, len(graph.Edges))
		self.assertListEqual([test, ret], [edge.Destination for edge in condition.OutboundEdges])
		self.assertIn(loop, condition.InboundEdges)

		for block in graph:
			with self.subTest(block=block.ID):
				if block.Kind is not BlockKind.Entry:
					self.assertEqual(block.Count, sum(edge.Count for edge in block.InboundEdges))

				if block.Kind is not BlockKind.Exit:
					self.assertEqual(block.Count, sum(edge.Count for edge in block.OutboundEdges))

	def test_Switch(self) -> None:
		"""
		A ``switch`` is a block with an edge per target; a ``case`` without ``break`` falls through into the next one.

		.. code-block:: C

		   int Weight(int size) {
		     int w = 0;
		     switch (size) {
		       case 2:  w += 2;
		       case 1:  w += 1; break;
		       default: w = -1;
		     }
		     return w;
		   }
		"""
		graph = ControlFlowGraph("Weight")

		switch =  BasicBlock(graph, 2, value="int w = 0; switch (size)")
		case2 =   BasicBlock(graph, 3, value="w += 2;")
		case1 =   BasicBlock(graph, 4, value="w += 1;")
		default = BasicBlock(graph, 5, value="w = -1;")
		ret =     BasicBlock(graph, 6, value="return w;")
		Edge(graph.Entry, switch, EdgeKind.FallThrough)
		Edge(switch, case2, EdgeKind.Jump, value="case 2")
		Edge(switch, case1, EdgeKind.Jump, value="case 1")
		Edge(switch, default, EdgeKind.Jump, value="default")
		Edge(case2, case1, EdgeKind.FallThrough)
		Edge(case1, ret, EdgeKind.Jump)
		Edge(default, ret, EdgeKind.FallThrough)
		Edge(ret, graph.Exit, EdgeKind.FallThrough)

		self.assertListEqual(
			[("case 2", case2), ("case 1", case1), ("default", default)],
			[(edge.Value, edge.Destination) for edge in switch.OutboundEdges]
		)
		self.assertSetEqual({EdgeKind.Jump}, {edge.Kind for edge in switch.OutboundEdges})
		self.assertListEqual(
			[(switch, EdgeKind.Jump), (case2, EdgeKind.FallThrough)],
			[(edge.Source, edge.Kind) for edge in case1.InboundEdges]
		)


class CPP(Testcase):
	def test_TryThrowCatch(self) -> None:
		"""
		A ``throw`` caught in the function is an exception edge to the ``catch`` block; an exception a call raises and no
		``catch`` handles is an exception edge to the unwind block.

		.. code-block:: C++

		   void Parse(const char* s) {
		     try {
		       if (!s) throw std::invalid_argument("s");
		       Use(s);
		     } catch (const std::invalid_argument& e) {
		       Log(e);
		     }
		   }
		"""
		graph = ControlFlowGraph("Parse")

		body =    BasicBlock(graph, "try", value="if (!s)")
		throw =   BasicBlock(graph, "throw", value="throw std::invalid_argument(\"s\");")
		call =    BasicBlock(graph, "call", value="Use(s);")
		handler = BasicBlock(graph, "catch", value="Log(e);")
		unwind =  BasicBlock(graph, "unwind", kind=BlockKind.Unwind)
		Edge(graph.Entry, body, EdgeKind.FallThrough)
		Edge(body, throw, EdgeKind.FallThrough)
		Edge(body, call, EdgeKind.Jump)
		Edge(throw, handler, EdgeKind.Exception)
		Edge(call, graph.Exit, EdgeKind.FallThrough)
		Edge(call, unwind, EdgeKind.Exception)
		Edge(handler, graph.Exit, EdgeKind.FallThrough)

		self.assertIs(unwind, graph.Unwind)
		self.assertListEqual([(throw, EdgeKind.Exception)], [(e.Source, e.Kind) for e in handler.InboundEdges])
		self.assertListEqual([(call, EdgeKind.Exception)], [(e.Source, e.Kind) for e in unwind.InboundEdges])
		self.assertSetEqual({EdgeKind.FallThrough}, {edge.Kind for edge in graph.Exit.InboundEdges})
		self.assertListEqual([graph.Exit, unwind], [edge.Destination for edge in call.OutboundEdges])

	def test_Cleanup(self) -> None:
		"""
		A destructor running while an exception passes is a cleanup block between the throwing call and the unwind block.

		.. code-block:: C++

		   void Write(File& f) {
		     Lock lock(f);
		     f.Flush();
		   }
		"""
		graph = ControlFlowGraph("Write")

		body =    BasicBlock(graph, 2, value="Lock lock(f); f.Flush();")
		release = BasicBlock(graph, 3, value="lock.~Lock();")
		cleanup = BasicBlock(graph, 4, value="lock.~Lock();  // landing pad")
		unwind =  BasicBlock(graph, 5, kind=BlockKind.Unwind)
		Edge(graph.Entry, body, EdgeKind.FallThrough)
		Edge(body, release, EdgeKind.FallThrough)
		Edge(body, cleanup, EdgeKind.Exception)
		Edge(release, graph.Exit, EdgeKind.FallThrough)
		Edge(cleanup, unwind, EdgeKind.Exception)

		self.assertListEqual([cleanup], [edge.Source for edge in unwind.InboundEdges])
		self.assertListEqual([release], [edge.Source for edge in graph.Exit.InboundEdges])


class Python(Testcase):
	def test_TryExceptFinally(self) -> None:
		"""
		The ``finally`` clause is a block on the normal and on the exceptional path; a ``return`` inside it leaves the
		function through the exit block, also on the exceptional path, which discards the pending exception.

		.. code-block:: Python

		   def Read(path):
		     try:
		       data = load(path)
		     except OSError:
		       data = None
		     finally:
		       if closing():
		         return None
		     return data
		"""
		graph = ControlFlowGraph("Read", entryID=-1, exitID=0)

		body =           BasicBlock(graph, 3, value="data = load(path)")
		handler =        BasicBlock(graph, 5, value="data = None")
		finallyNormal =  BasicBlock(graph, 7, value="if closing():")
		finallyPending = BasicBlock(graph, 107, value="if closing():")
		returnNormal =   BasicBlock(graph, 8, value="return None")
		returnPending =  BasicBlock(graph, 108, value="return None")
		returnData =     BasicBlock(graph, 9, value="return data")
		unwind =         BasicBlock(graph, "unwind", kind=BlockKind.Unwind)
		Edge(graph.Entry, body, EdgeKind.FallThrough)
		Edge(body, finallyNormal, EdgeKind.FallThrough)
		Edge(body, handler, EdgeKind.Exception, value="OSError")
		Edge(body, finallyPending, EdgeKind.Exception)
		Edge(handler, finallyNormal, EdgeKind.FallThrough)
		Edge(handler, finallyPending, EdgeKind.Exception)
		Edge(finallyNormal, returnNormal, EdgeKind.FallThrough)
		Edge(finallyNormal, returnData, EdgeKind.Jump)
		Edge(finallyPending, returnPending, EdgeKind.FallThrough)
		Edge(finallyPending, unwind, EdgeKind.Exception)
		Edge(returnNormal, graph.Exit, EdgeKind.Jump)
		Edge(returnPending, graph.Exit, EdgeKind.Jump)
		Edge(returnData, graph.Exit, EdgeKind.Jump)

		self.assertSetEqual({EdgeKind.Exception}, {edge.Kind for edge in finallyPending.InboundEdges})
		self.assertListEqual([finallyPending], [edge.Source for edge in unwind.InboundEdges])
		self.assertIn(returnPending, [edge.Source for edge in graph.Exit.InboundEdges])
		self.assertListEqual(
			[(handler, "OSError"), (finallyPending, None)],
			[(edge.Destination, edge.Value) for edge in body.OutboundEdges if edge.Kind is EdgeKind.Exception]
		)
