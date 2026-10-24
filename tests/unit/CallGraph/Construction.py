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
Unit tests for :mod:`pyTooling.CallGraph`: constructing functions, calls and graphs, and the checks of their parameters.
"""
from pyTooling.CallGraph   import CallGraph, Function, Call, FunctionKind, CallKind, CallGraphError, \
                                  DuplicateFunctionError
from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, BlockKind
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Construction(Testcase):
	def test_CallGraph(self) -> None:
		graph = CallGraph("prog")

		self.assertEqual("prog", graph.Name)
		self.assertEqual(0, graph.FunctionCount)
		self.assertListEqual([], list(graph.IterateFunctions()))
		self.assertEqual(0, len(graph), "A new graph has no key-value-pairs.")
		self.assertDictEqual({}, graph.Functions)
		self.assertListEqual([], graph.Calls)

	def test_Function(self) -> None:
		graph =    CallGraph("prog")
		function = Function(graph, "main")

		self.assertIs(graph, function.CallGraph)
		self.assertEqual("main", function.ID)
		self.assertIs(FunctionKind.Defined, function.Kind)
		self.assertIsNone(function.ControlFlowGraph)
		self.assertIsNone(function.Count)
		self.assertIsNone(function.Value)
		self.assertTupleEqual((), function.InboundCalls)
		self.assertTupleEqual((), function.OutboundCalls)
		self.assertIs(function, graph.GetFunction("main"))
		self.assertTrue(graph.ContainsFunction("main"))
		self.assertFalse(graph.ContainsFunction("Sum"))
		self.assertEqual(1, graph.FunctionCount)

		with self.assertRaises(KeyError):
			_ = graph.GetFunction("Sum")

	def test_Function_CountAndValue(self) -> None:
		graph =    CallGraph("prog")
		function = Function(graph, "Sum", count=5, value=("prog.c", 7))

		self.assertEqual(5, function.Count)
		self.assertTupleEqual(("prog.c", 7), function.Value)

		function.Count = 0
		function.Value = "prog.c:7"
		self.assertEqual(0, function.Count)
		self.assertEqual("prog.c:7", function.Value)

	def test_Function_Kinds(self) -> None:
		graph =     CallGraph("prog")
		functions = [Function(graph, kind.name, kind=kind) for kind in FunctionKind]

		self.assertListEqual(functions, list(graph.IterateFunctions()))
		self.assertListEqual(list(FunctionKind), [function.Kind for function in graph.IterateFunctions()])

	def test_Function_ControlFlowGraph(self) -> None:
		cfg =      ControlFlowGraph("Sum")
		graph =    CallGraph("prog")
		function = Function(graph, "Sum", controlFlowGraph=cfg)
		external = Function(graph, "printf", kind=FunctionKind.External, controlFlowGraph=ControlFlowGraph("printf"))

		self.assertIs(cfg, function.ControlFlowGraph)
		self.assertEqual("printf", external.ControlFlowGraph.Name)

	def test_Call(self) -> None:
		graph =     CallGraph("prog")
		main =      Function(graph, "main")
		summation = Function(graph, "Sum")
		printf =    Function(graph, "printf", kind=FunctionKind.External)
		call1 =     Call(main, summation)
		call2 =     Call(main, printf, CallKind.Direct, count=3, value="prog.c:9:3")

		self.assertIs(main, call1.Caller)
		self.assertIs(summation, call1.Callee)
		self.assertIs(CallKind.Default, call1.Kind)
		self.assertIsNone(call1.CallSite)
		self.assertIsNone(call1.Count)
		self.assertIsNone(call1.Value)
		self.assertIs(CallKind.Direct, call2.Kind)
		self.assertEqual(3, call2.Count)
		self.assertEqual("prog.c:9:3", call2.Value)

		self.assertTupleEqual((call1, call2), main.OutboundCalls)
		self.assertTupleEqual((), main.InboundCalls)
		self.assertTupleEqual((call1,), summation.InboundCalls)
		self.assertTupleEqual((call2,), printf.InboundCalls)
		self.assertListEqual([call1, call2], graph.Calls)

	def test_Call_Parallel(self) -> None:
		"""
		Two functions can be connected by several calls of the same kind.

		Each call site is a call of its own.
		"""
		graph =     CallGraph("prog")
		main =      Function(graph, "main")
		summation = Function(graph, "Sum")
		calls =     [Call(main, summation, CallKind.Direct, value=line) for line in (9, 10, 11)]

		self.assertTupleEqual(tuple(calls), summation.InboundCalls)
		self.assertListEqual([9, 10, 11], [call.Value for call in main.OutboundCalls])

	def test_Call_Recursion(self) -> None:
		"""A function calling itself is a call from and to the same function."""
		graph = CallGraph("prog")
		fib =   Function(graph, "Fib")
		call =  Call(fib, fib, CallKind.Direct)

		self.assertIs(fib, call.Caller)
		self.assertIs(fib, call.Callee)
		self.assertTupleEqual((call,), fib.InboundCalls)
		self.assertTupleEqual((call,), fib.OutboundCalls)

	def test_Call_CallSite(self) -> None:
		cfg =       ControlFlowGraph("main")
		block =     BasicBlock(cfg, 2)
		graph =     CallGraph("prog")
		main =      Function(graph, "main", controlFlowGraph=cfg)
		summation = Function(graph, "Sum")
		call =      Call(main, summation, CallKind.Direct, callSite=block)

		self.assertIs(block, call.CallSite)
		self.assertIs(main.ControlFlowGraph, call.CallSite.ControlFlowGraph)

	def test_CallTo(self) -> None:
		cfg =       ControlFlowGraph("main")
		block =     BasicBlock(cfg, 2)
		graph =     CallGraph("prog")
		main =      Function(graph, "main", controlFlowGraph=cfg)
		summation = Function(graph, "Sum")

		call = main.CallTo(summation, 3, "prog.c:7", CallKind.Direct, block, {"line": 7})

		self.assertIs(main, call.Caller)
		self.assertIs(summation, call.Callee)
		self.assertEqual(3, call.Count)
		self.assertEqual("prog.c:7", call.Value)
		self.assertIs(CallKind.Direct, call.Kind)
		self.assertIs(block, call.CallSite)
		self.assertEqual(7, call["line"])
		self.assertTupleEqual((call, ), main.OutboundCalls)
		self.assertTupleEqual((call, ), summation.InboundCalls)
		self.assertListEqual([call], graph.Calls)

	def test_CallFrom(self) -> None:
		graph =     CallGraph("prog")
		main =      Function(graph, "main")
		summation = Function(graph, "Sum")

		call = summation.CallFrom(main, callKind=CallKind.Indirect)

		self.assertIs(main, call.Caller)
		self.assertIs(summation, call.Callee)
		self.assertIsNone(call.Count)
		self.assertIsNone(call.CallSite)
		self.assertIs(CallKind.Indirect, call.Kind)
		self.assertEqual(0, len(call))

	def test_CallTo_Checks(self) -> None:
		graph = CallGraph("prog")
		main =  Function(graph, "main")

		with self.assertRaises(ValueError):
			main.CallTo(None)

		with self.assertRaises(ValueError):
			main.CallTo(Function(CallGraph("other"), "Sum"))

		with self.assertRaises(ValueError):
			main.CallTo(main, callSite=BasicBlock(ControlFlowGraph("main"), 2))

	def test_Kind_Str(self) -> None:
		self.assertEqual("External", str(FunctionKind.External))
		self.assertEqual("Indirect", str(CallKind.Indirect))

	def test_Exceptions(self) -> None:
		self.assertTrue(issubclass(DuplicateFunctionError, CallGraphError))


class KeyValuePairs(Testcase):
	def test_CallGraph(self) -> None:
		graph = CallGraph("prog", keyValuePairs={"tool": "gprof"})

		self.assertEqual(1, len(graph))
		self.assertEqual("gprof", graph["tool"])
		self.assertNotIn("main", graph, "A function ID is no key-value-pair.")

	def test_Function(self) -> None:
		function = Function(CallGraph("prog"), "main", keyValuePairs={"file": "main.c"})

		self.assertEqual("main.c", function["file"])
		self.assertEqual(1, len(function))

	def test_Call(self) -> None:
		graph = CallGraph("prog")
		call =  Call(Function(graph, "main"), Function(graph, "Sum"), keyValuePairs={"line": 12})

		self.assertEqual(12, call["line"])
		self.assertEqual(1, len(call))

	def test_IterateFunctions(self) -> None:
		graph = CallGraph("prog")
		Function(graph, "main")
		Function(graph, "printf", kind=FunctionKind.External)
		Function(graph, "Sum")

		self.assertListEqual(["main", "printf", "Sum"], [function.ID for function in graph.IterateFunctions()])
		self.assertListEqual(
			["printf"],
			[function.ID for function in graph.IterateFunctions(lambda function: function.Kind is FunctionKind.External)]
		)


class Checks(Testcase):
	def test_CallGraph_Name(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = CallGraph(None)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = CallGraph(42)

		self.assertEqual("Parameter 'name' is not of type 'str'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = CallGraph("")

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_Function_CallGraph(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Function(None, "main")

		self.assertEqual("Parameter 'callGraph' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Function(ControlFlowGraph("main"), "main")

		self.assertEqual("Parameter 'callGraph' is not of type 'CallGraph'.", str(context.exception))

	def test_Function_ID(self) -> None:
		graph = CallGraph("prog")
		_ =     Function(graph, "main")

		with self.assertRaises(ValueError) as context:
			_ = Function(graph, None)

		self.assertEqual("Parameter 'functionID' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Function(graph, ["main"])

		self.assertEqual("Parameter 'functionID' is not hashable.", str(context.exception))

		with self.assertRaises(DuplicateFunctionError) as context:
			_ = Function(graph, "main", kind=FunctionKind.External)

		self.assertEqual("Call graph 'prog' has a function 'main' already.", str(context.exception))
		self.assertEqual("main", context.exception.FunctionID)
		self.assertEqual(1, graph.FunctionCount)
		self.assertIs(FunctionKind.Defined, graph.GetFunction("main").Kind)

	def test_DuplicateFunctionError_MessageOnly(self) -> None:
		"""An exception raised with a message only carries no function ID."""
		with self.assertRaises(DuplicateFunctionError) as context:
			raise DuplicateFunctionError("Duplicate function.")

		self.assertIsNone(context.exception.FunctionID)

	def test_Function_Kind(self) -> None:
		graph = CallGraph("prog")

		with self.assertRaises(ValueError) as context:
			_ = Function(graph, "main", kind=None)

		self.assertEqual("Parameter 'kind' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Function(graph, "main", kind=CallKind.Direct)

		self.assertEqual("Parameter 'kind' is not of type 'FunctionKind'.", str(context.exception))
		self.assertEqual(0, graph.FunctionCount)

	def test_Function_ControlFlowGraph(self) -> None:
		graph = CallGraph("prog")

		with self.assertRaises(TypeError) as context:
			_ = Function(graph, "main", controlFlowGraph="main")

		self.assertEqual("Parameter 'controlFlowGraph' is not of type 'ControlFlowGraph'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = Function(graph, "__indirect_call", kind=FunctionKind.Unknown, controlFlowGraph=ControlFlowGraph("main"))

		self.assertEqual(
			"Parameter 'controlFlowGraph' is given for a function of kind 'Unknown'.",
			str(context.exception)
		)
		self.assertEqual(0, graph.FunctionCount)

	def test_Count(self) -> None:
		graph =    CallGraph("prog")
		function = Function(graph, "main")

		for count in ("1", 1.0, True):
			with self.subTest(count=count):
				with self.assertRaises(TypeError) as context:
					_ = Function(graph, "Sum", count=count)

				self.assertEqual("Parameter 'count' is not of type 'int'.", str(context.exception))

				with self.assertRaises(TypeError):
					function.Count = count

		with self.assertRaises(ValueError) as context:
			_ = Call(function, function, count=-1)

		self.assertEqual("Parameter 'count' is negative.", str(context.exception))
		self.assertIsNone(function.Count)
		self.assertNotIn("Sum", graph)
		self.assertListEqual([], graph.Calls)

	def test_Call_Caller(self) -> None:
		graph =     CallGraph("prog")
		summation = Function(graph, "Sum")

		with self.assertRaises(ValueError) as context:
			_ = Call(None, summation)

		self.assertEqual("Parameter 'caller' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Call("main", summation)

		self.assertEqual("Parameter 'caller' is not of type 'Function'.", str(context.exception))

	def test_Call_Callee(self) -> None:
		graph =     CallGraph("prog")
		other =     CallGraph("lib")
		main =      Function(graph, "main")
		summation = Function(other, "Sum")

		with self.assertRaises(ValueError) as context:
			_ = Call(main, None)

		self.assertEqual("Parameter 'callee' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Call(main, "Sum")

		self.assertEqual("Parameter 'callee' is not of type 'Function'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = Call(main, summation)

		self.assertEqual("Parameter 'callee' belongs to another graph than parameter 'caller'.", str(context.exception))
		self.assertListEqual([], graph.Calls)
		self.assertListEqual([], other.Calls)

	def test_Call_Kind(self) -> None:
		graph = CallGraph("prog")
		main =  Function(graph, "main")

		with self.assertRaises(ValueError) as context:
			_ = Call(main, main, None)

		self.assertEqual("Parameter 'kind' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Call(main, main, FunctionKind.Defined)

		self.assertEqual("Parameter 'kind' is not of type 'CallKind'.", str(context.exception))
		self.assertListEqual([], graph.Calls)

	def test_Call_CallSite(self) -> None:
		mainCFG =   ControlFlowGraph("main")
		sumCFG =    ControlFlowGraph("Sum")
		graph =     CallGraph("prog")
		main =      Function(graph, "main", controlFlowGraph=mainCFG)
		summation = Function(graph, "Sum", controlFlowGraph=sumCFG)
		leaf =      Function(graph, "Leaf")
		block =     BasicBlock(sumCFG, 3)

		with self.assertRaises(TypeError) as context:
			_ = Call(summation, leaf, callSite=3)

		self.assertEqual("Parameter 'callSite' is not of type 'BasicBlock'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = Call(leaf, summation, callSite=block)

		self.assertEqual(
			"Parameter 'callSite' is given, but the caller has no control flow graph.",
			str(context.exception)
		)

		with self.assertRaises(ValueError) as context:
			_ = Call(main, summation, callSite=block)

		self.assertEqual(
			"Parameter 'callSite' belongs to another control flow graph than the caller's.",
			str(context.exception)
		)

		unwind = BasicBlock(sumCFG, "unwind", kind=BlockKind.Unwind)
		for site in (sumCFG.Entry, sumCFG.Exit, unwind):
			with self.subTest(callSite=site.ID):
				with self.assertRaises(ValueError) as context:
					_ = Call(summation, leaf, callSite=site)

				self.assertEqual("Parameter 'callSite' is not a block of code.", str(context.exception))

		self.assertListEqual([], graph.Calls)
		self.assertTupleEqual((), leaf.InboundCalls)
