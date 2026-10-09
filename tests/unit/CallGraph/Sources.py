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
Unit tests for :mod:`pyTooling.CallGraph`: call graphs as compilers and profilers report them.

Each testcase builds the call graph a source reports for the program shown in its doc-string, and checks the shape the
source gives it. The C program is the same in all C testcases:

.. code-block:: C

   static int Leaf(int x) { return x * 2; }
   int Fib(int n) { return n < 2 ? n : Fib(n - 1) + Fib(n - 2); }
   typedef int (*Op)(int);
   int Apply(Op f, int x) { return f(x); }
   int Sum(int n) { int s = 0; for (int i = 0; i < n; i++) s += Leaf(i); return s; }
   int main(void) {
     printf("%d\\n", Sum(4));
     printf("%d\\n", Fib(5));
     printf("%d\\n", Apply(Leaf, 3));
     return 0;
   }
"""
from cProfile              import Profile
from pstats                import Stats
from typing                import Callable

from pyTooling.CallGraph   import CallGraph, Function, Call, FunctionKind, CallKind
from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, Edge, EdgeKind
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def Leaf(x: int) -> int:
	"""
	Return the double of a number.

	:param x: The number.
	:returns: The double of ``x``.
	"""
	return x * 2


def Fib(n: int) -> int:
	"""
	Return a Fibonacci number, computed recursively.

	:param n: Index of the Fibonacci number.
	:returns: The ``n``-th Fibonacci number.
	"""
	return n if n < 2 else Fib(n - 1) + Fib(n - 2)


def Apply(function: Callable[[int], int], x: int) -> int:
	"""
	Call a function through a reference, like C calls through a function pointer.

	:param function: The function to call.
	:param x:        The argument.
	:returns:        The function's result.
	"""
	return function(x)


def Run() -> int:
	"""
	Call the functions above; the function :class:`CProfile` profiles.

	:returns: A sum of the results.
	"""
	total = 0
	for i in range(3):
		total += Leaf(i)

	return Fib(4) + Apply(Leaf, total) + len("ab")


class GCC(Testcase):
	def test_CallGraphInfo(self) -> None:
		"""
		The static call graph of a translation unit, as GCC's ``-fcallgraph-info`` writes it into :file:`prog.ci`.

		A static function's ID is prefixed by the file name. ``printf`` is declared, but not defined in the translation
		unit. The call through a function pointer leads to GCC's placeholder ``__indirect_call``. Every call site is an
		edge, labeled with its location.
		"""
		graph = CallGraph("prog.c")

		leaf =      Function(graph, "prog.c:Leaf", value="prog.c:3:12")
		fib =       Function(graph, "Fib", value="prog.c:4:5")
		apply =     Function(graph, "Apply", value="prog.c:6:5")
		indirect =  Function(graph, "__indirect_call", kind=FunctionKind.Unknown)
		summation = Function(graph, "Sum", value="prog.c:7:5")
		main =      Function(graph, "main", value="prog.c:8:5")
		printf =    Function(graph, "printf", kind=FunctionKind.External, value="/usr/include/stdio.h:363:12")
		Call(fib, fib, CallKind.Direct, value="prog.c:4:37")
		Call(fib, fib, CallKind.Direct, value="prog.c:4:50")
		Call(apply, indirect, CallKind.Indirect, value="prog.c:6:33")
		Call(summation, leaf, CallKind.Direct, value="prog.c:7:62")
		Call(main, summation, CallKind.Direct, value="prog.c:9:3")
		Call(main, printf, CallKind.Direct, value="prog.c:9:3")
		Call(main, fib, CallKind.Direct, value="prog.c:10:3")
		Call(main, printf, CallKind.Direct, value="prog.c:10:3")
		Call(main, apply, CallKind.Direct, value="prog.c:11:3")
		Call(main, printf, CallKind.Direct, value="prog.c:11:3")

		self.assertEqual(7, len(graph))
		self.assertEqual(10, len(graph.Calls))
		self.assertListEqual(["prog.c:4:37", "prog.c:4:50"], [call.Value for call in fib.OutboundCalls])
		self.assertListEqual([main, main, main], [call.Caller for call in printf.InboundCalls])
		self.assertListEqual([(apply, CallKind.Indirect)], [(c.Caller, c.Kind) for c in indirect.InboundCalls])
		self.assertListEqual(
			[summation, printf, fib, printf, apply, printf],
			[call.Callee for call in main.OutboundCalls]
		)
		self.assertTupleEqual((), main.InboundCalls)
		self.assertSetEqual({None}, {call.Count for call in graph.Calls})


class GProf(Testcase):
	def test_CallGraph(self) -> None:
		"""
		The dynamic call graph of a run, as ``gprof -q`` prints it for a program compiled with ``-pg``.

		gprof reports how often a function was called (``Fib``: ``1+14``, non-recursive and recursive calls) and how often
		along each arc. It doesn't classify calls: the call through a function pointer is an arc ``Apply`` |rarr| ``Leaf``.
		``printf`` isn't compiled with ``-pg``, so gprof doesn't see it.
		"""
		graph = CallGraph("prog")

		main =      Function(graph, "main", count=1)
		summation = Function(graph, "Sum", count=1)
		leaf =      Function(graph, "Leaf", count=5)
		fib =       Function(graph, "Fib", count=15)
		apply =     Function(graph, "Apply", count=1)
		Call(main, summation, count=1)
		Call(main, fib, count=1)
		Call(main, apply, count=1)
		Call(summation, leaf, count=4)
		Call(apply, leaf, count=1)
		recursion = Call(fib, fib, count=14)

		self.assertIn(recursion, fib.OutboundCalls)
		self.assertIn(recursion, fib.InboundCalls)
		self.assertSetEqual({CallKind.Default}, {call.Kind for call in graph.Calls})

		for function in graph:
			with self.subTest(function=function.ID):
				if function is not main:
					self.assertEqual(function.Count, sum(call.Count for call in function.InboundCalls))


class CProfile(Testcase):
	def test_Profile(self) -> None:
		"""
		The call graph of a run profiled by :mod:`cProfile`, built from its :class:`pstats.Stats`.

		A function's statistics count all calls and the primitive calls, which recursion didn't induce; a call graph's
		function counts all calls and keeps the primitive ones as its value. A built-in function's file name is ``~``. The
		function names are unique in this run, so they are the IDs.
		"""
		profile = Profile()
		profile.runcall(Run)
		stats = Stats(profile).stats

		graph = CallGraph("Run")
		for (fileName, _, functionName), (primitiveCalls, calls, *_) in stats.items():
			Function(
				graph,
				functionName,
				kind=FunctionKind.External if fileName == "~" else FunctionKind.Defined,
				count=calls,
				value=primitiveCalls
			)

		for (_, _, functionName), (*_, callers) in stats.items():
			for (_, _, callerName), (calls, *_) in callers.items():
				Call(graph[callerName], graph[functionName], count=calls)

		run =   graph["Run"]
		leaf =  graph["Leaf"]
		fib =   graph["Fib"]
		apply = graph["Apply"]

		self.assertListEqual([1, 4, 9, 1], [function.Count for function in (run, leaf, fib, apply)])
		self.assertEqual(1, fib.Value)
		self.assertDictEqual(
			{"Leaf": 3, "Fib": 1, "Apply": 1},
			{call.Callee.ID: call.Count for call in run.OutboundCalls if call.Callee.Kind is FunctionKind.Defined}
		)
		self.assertListEqual([(leaf, 1)], [(call.Callee, call.Count) for call in apply.OutboundCalls])
		self.assertListEqual([(fib, 8)], [(call.Callee, call.Count) for call in fib.OutboundCalls])

		for function in graph:
			with self.subTest(function=function.ID):
				if function.Kind is FunctionKind.External:
					self.assertEqual("~", next(key[0] for key in stats if key[2] == function.ID))

				if len(function.InboundCalls) > 0:
					self.assertEqual(function.Count, sum(call.Count for call in function.InboundCalls))


class ControlFlow(Testcase):
	def test_CallSites(self) -> None:
		"""
		Functions refer to their control flow graphs, numbered like GCC numbers the blocks, with counts of the run; a call
		refers to the block it's made from. Both recursive calls of ``Fib`` are made from block 3.
		"""
		sumCFG =  ControlFlowGraph("Sum", entryID=0, exitID=1)
		sumInit = BasicBlock(sumCFG, 2, count=1, value="s = 0; i = 0;")
		sumBody = BasicBlock(sumCFG, 3, count=4, value="s += Leaf(i); i++;")
		sumTest = BasicBlock(sumCFG, 4, count=5, value="i < n")
		sumRet =  BasicBlock(sumCFG, 5, count=1, value="return s;")
		Edge(sumCFG.Entry, sumInit, EdgeKind.FallThrough, count=1)
		Edge(sumInit, sumTest, EdgeKind.Jump, count=1)
		Edge(sumBody, sumTest, EdgeKind.FallThrough, count=4)
		Edge(sumTest, sumBody, EdgeKind.Jump, count=4)
		Edge(sumTest, sumRet, EdgeKind.Jump, count=1)
		Edge(sumRet, sumCFG.Exit, EdgeKind.FallThrough, count=1)

		fibCFG =  ControlFlowGraph("Fib", entryID=0, exitID=1)
		fibTest = BasicBlock(fibCFG, 2, count=15, value="n > 1")
		fibCall = BasicBlock(fibCFG, 3, count=7, value="Fib(n - 1) + Fib(n - 2)")
		fibLeaf = BasicBlock(fibCFG, 4, count=8, value="n")
		fibRet =  BasicBlock(fibCFG, 5, count=15, value="return")
		Edge(fibCFG.Entry, fibTest, EdgeKind.FallThrough, count=15)
		Edge(fibTest, fibCall, EdgeKind.Jump, count=7)
		Edge(fibTest, fibLeaf, EdgeKind.Jump, count=8)
		Edge(fibCall, fibRet, EdgeKind.Jump, count=7)
		Edge(fibLeaf, fibRet, EdgeKind.FallThrough, count=8)
		Edge(fibRet, fibCFG.Exit, EdgeKind.FallThrough, count=15)

		graph =     CallGraph("prog")
		main =      Function(graph, "main", count=1)
		summation = Function(graph, "Sum", controlFlowGraph=sumCFG, count=1)
		leaf =      Function(graph, "Leaf", count=5)
		fib =       Function(graph, "Fib", controlFlowGraph=fibCFG, count=15)
		Call(main, summation, CallKind.Direct, count=1)
		Call(main, fib, CallKind.Direct, count=1)
		Call(summation, leaf, CallKind.Direct, callSite=sumBody, count=4)
		Call(fib, fib, CallKind.Direct, callSite=fibCall, count=7, value="Fib(n - 1)")
		Call(fib, fib, CallKind.Direct, callSite=fibCall, count=7, value="Fib(n - 2)")

		self.assertListEqual([fibCall, fibCall], [call.CallSite for call in fib.OutboundCalls])

		for call in graph.Calls:
			with self.subTest(caller=call.Caller.ID, callee=call.Callee.ID, value=call.Value):
				if call.CallSite is None:
					self.assertIsNone(call.Caller.ControlFlowGraph)
				else:
					self.assertIs(call.Caller.ControlFlowGraph, call.CallSite.Graph)
					self.assertEqual(call.CallSite.Count, call.Count)

		for function in (summation, fib):
			with self.subTest(function=function.ID):
				self.assertEqual(function.Count, function.ControlFlowGraph.Entry.OutboundEdges[0].Count)
