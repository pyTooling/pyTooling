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
A data structure to describe the **call graph** of a program: its functions and the calls between them.

A :class:`CallGraph` describes the functions of e.g. a program, a translation unit or a profiled run. A
:class:`Function` is identified by an ID unique within its graph, e.g. a qualified or a mangled name. A :class:`Call`
leads from the calling function to the called function, so a recursion is a cycle of the graph. A :class:`CallKind`
says how the callee was determined, and a :class:`FunctionKind` if a function is defined in the described code, defined
elsewhere, or a placeholder for unknown functions, e.g. the targets of an indirect call.

Functions and calls carry an optional execution count, e.g. from a profiler, and an optional value of any type. A
function can refer to its control flow graph, and a call to its call site: the basic block of the caller's control flow
graph the call is made from. Call graphs, functions and calls carry key-value-pairs, e.g. the results of an analysis.
:meth:`CallGraph.ToGraph` converts a call graph into a :class:`~pyTooling.Graph.Graph`.

.. hint::

   See :ref:`high-level help <STRUCT/CallGraph>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.ControlFlow`
      |rarr| The control flow graph of a function, whose blocks are the call sites.
   :mod:`pyTooling.Graph`
      |rarr| The graph data structure a call graph is converted into.
   :mod:`pyTooling.Graph.GraphML`
      |rarr| Writing a graph as a GraphML document.
"""
from __future__            import annotations

from enum                  import Enum
from typing                import Any, Generator, Hashable, Mapping, Optional as Nullable

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.DataModel   import Predicate
from pyTooling.ControlFlow import Base, BaseWithCountAndValue, BasicBlock, BlockKind, ControlFlowGraph
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import DuplicateElementError, ToolingException
from pyTooling.Graph       import Graph, Vertex


# A class with a property named like a class - ``ControlFlowGraph`` - can't name that class in the annotation of a
# field: the class body's namespace, where annotations are evaluated, binds the name to the property.
_ControlFlowGraph = ControlFlowGraph


@export
class FunctionKind(Enum):
	"""
	Kind of a function: whether the call graph describes its code.
	"""
	Defined =  0  #: The function is defined in the described code, e.g. in the translation unit or the profiled program.
	External = 1  #: The function is defined elsewhere, e.g. a library function or a Python built-in function.
	Unknown =  2  #: A placeholder for functions the source doesn't know, e.g. the targets of an unresolved indirect call.

	def __str__(self) -> str:
		"""
		Return the member's name.

		:returns: Name of the member, e.g. ``External``.
		"""
		return self.name


@export
class CallKind(Enum):
	"""
	Kind of a call: how the callee is determined.
	"""
	Default =  0  #: The call wasn't classified, e.g. a pair of caller and callee a profiler reports.
	Direct =   1  #: The call names its callee, e.g. a C function called by name.
	Indirect = 2  #: The callee is determined at run time, e.g. through a function pointer or a virtual method.

	def __str__(self) -> str:
		"""
		Return the member's name.

		:returns: Name of the member, e.g. ``Indirect``.
		"""
		return self.name


@export
class CallGraphError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.CallGraph`."""


@export
class DuplicateFunctionError(CallGraphError, DuplicateElementError):
	"""The exception raised for a function with an ID, which the graph has already."""

	_functionID: Nullable[Hashable]  #: ID of the function the graph has already.

	def __init__(self, message: str, /, *, functionID: Nullable[Hashable] = None) -> None:
		"""
		Initializes the exception with the ID of the function the graph has already.

		:param message:    The exception's message.
		:param functionID: Optional, the ID of the function the graph has already.
		"""
		super().__init__(message)
		self._functionID = functionID

	@readonly
	def FunctionID(self) -> Nullable[Hashable]:
		"""
		Read-only property to access the ID of the function the graph has already (:attr:`_functionID`).

		:returns: The function's ID, or ``None`` if it wasn't recorded.
		"""
		return self._functionID


@export
class Function(BaseWithCountAndValue):
	"""
	A function of a call graph.

	A function is identified by an ID unique within its graph, e.g. a qualified or a mangled name. Its outbound calls lead
	to the functions it calls, its inbound calls come from the functions calling it. It can refer to its control flow
	graph, whose blocks are the call sites of its outbound calls.
	"""
	_callGraph:        _CallGraph                   #: The call graph this function belongs to.
	_id:               Hashable                     #: ID of the function, unique within its graph.
	_kind:             FunctionKind                 #: Kind of the function.
	_controlFlowGraph: Nullable[_ControlFlowGraph]  #: The function's control flow graph, if it's known.
	_inboundCalls:     list[Call]                   #: Calls of this function.
	_outboundCalls:    list[Call]                   #: Calls this function makes.

	def __init__(
		self,
		callGraph:        _CallGraph,
		functionID:       Hashable,
		*,
		kind:             FunctionKind                     = FunctionKind.Defined,
		controlFlowGraph: Nullable[_ControlFlowGraph]      = None,
		count:            Nullable[int]                    = None,
		value:            Nullable[Any]                    = None,
		keyValuePairs:    Nullable[Mapping[Hashable, Any]] = None
	) -> None:
		"""
		Initializes a function and adds it to its graph.

		:param callGraph:               The call graph the function belongs to.
		:param functionID:              ID of the function, unique within its graph.
		:param kind:                    Optional, kind of the function. Default: :attr:`FunctionKind.Defined`.
		:param controlFlowGraph:        Optional, the function's control flow graph. Default: ``None``.
		:param count:                   Optional, how often the function was called. Default: ``None``.
		:param value:                   Optional, any value attached to the function, e.g. its location. Default: ``None``.
		:param keyValuePairs:           Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:raises TypeError:              If parameter 'count' is not of type :class:`int`.
		:raises ValueError:             If parameter 'count' is negative.
		:raises ValueError:             If parameter 'callGraph' is None.
		:raises TypeError:              If parameter 'callGraph' is not of type :class:`CallGraph`.
		:raises ValueError:             If parameter 'functionID' is None.
		:raises TypeError:              If parameter 'functionID' is not hashable.
		:raises DuplicateFunctionError: If the graph has a function with that ID already.
		:raises ValueError:             If parameter 'kind' is None.
		:raises TypeError:              If parameter 'kind' is not of type :class:`FunctionKind`.
		:raises TypeError:              If parameter 'controlFlowGraph' is not of type
		                                :class:`~pyTooling.ControlFlow.ControlFlowGraph`.
		:raises ValueError:             If parameter 'controlFlowGraph' is given for a function of kind
		                                :attr:`FunctionKind.Unknown`.
		"""
		super().__init__(count, value, keyValuePairs)

		if callGraph is None:
			raise ValueError("Parameter 'callGraph' is None.")
		elif not isinstance(callGraph, _CallGraph):
			ex = TypeError("Parameter 'callGraph' is not of type 'CallGraph'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(callGraph)}'.")
			raise ex

		if functionID is None:
			raise ValueError("Parameter 'functionID' is None.")
		elif not isinstance(functionID, Hashable):
			ex = TypeError("Parameter 'functionID' is not hashable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(functionID)}'.")
			raise ex
		elif functionID in callGraph._functions:
			raise DuplicateFunctionError(
				f"Call graph '{callGraph._name}' has a function '{functionID}' already.",
				functionID=functionID
			)

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, FunctionKind):
			ex = TypeError("Parameter 'kind' is not of type 'FunctionKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex

		if controlFlowGraph is not None:
			if not isinstance(controlFlowGraph, _ControlFlowGraph):
				ex = TypeError("Parameter 'controlFlowGraph' is not of type 'ControlFlowGraph'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(controlFlowGraph)}'.")
				raise ex
			elif kind is FunctionKind.Unknown:
				ex = ValueError("Parameter 'controlFlowGraph' is given for a function of kind 'Unknown'.")
				ex.add_note(f"Got function '{functionID}'.")
				raise ex

		self._callGraph =        callGraph
		self._id =               functionID
		self._kind =             kind
		self._controlFlowGraph = controlFlowGraph
		self._inboundCalls =     []
		self._outboundCalls =    []

		callGraph._functions[functionID] = self

	@readonly
	def CallGraph(self) -> _CallGraph:
		"""
		Read-only property to access the call graph this function belongs to (:attr:`_callGraph`).

		:returns: The call graph.
		"""
		return self._callGraph

	@readonly
	def ID(self) -> Hashable:
		"""
		Read-only property to access the function's ID (:attr:`_id`).

		:returns: ID of the function, unique within its graph.
		"""
		return self._id

	@readonly
	def Kind(self) -> FunctionKind:
		"""
		Read-only property to access the function's kind (:attr:`_kind`).

		:returns: Kind of the function.
		"""
		return self._kind

	@readonly
	def ControlFlowGraph(self) -> Nullable[_ControlFlowGraph]:
		"""
		Read-only property to access the function's control flow graph (:attr:`_controlFlowGraph`).

		:returns: The control flow graph, or ``None`` if it's unknown.
		"""
		return self._controlFlowGraph

	@readonly
	def InboundCalls(self) -> tuple[Call, ...]:
		"""
		Read-only property to return the calls of this function.

		:returns: The inbound calls, in the order they were created.
		"""
		return tuple(self._inboundCalls)

	@readonly
	def OutboundCalls(self) -> tuple[Call, ...]:
		"""
		Read-only property to return the calls this function makes.

		:returns: The outbound calls, in the order they were created.
		"""
		return tuple(self._outboundCalls)

	def CallTo(
		self,
		callee:        Function,
		callCount:     Nullable[int]                    = None,
		callValue:     Nullable[Any]                    = None,
		callKind:      CallKind                         = CallKind.Default,
		callSite:      Nullable[BasicBlock]             = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None
	) -> Call:
		"""
		Create an outbound call from this function to the called function.

		:param callee:        The called function.
		:param callCount:     Optional, how often the call was made. Default: ``None``.
		:param callValue:     Optional, any value attached to the call, e.g. the call's source line. Default: ``None``.
		:param callKind:      Optional, kind of the call. Default: :attr:`CallKind.Default`.
		:param callSite:      Optional, the block of the caller's control flow graph the call is made from.
		                      Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs for the call. Default: ``None``.
		:returns:             The call from this function to the callee.
		:raises ValueError:   If parameter 'callee' is None.
		:raises TypeError:    If parameter 'callee' is not of type :class:`Function`.
		:raises ValueError:   If parameter 'callee' belongs to another graph than this function.
		:raises TypeError:    If parameter 'callCount' is not of type :class:`int`.
		:raises ValueError:   If parameter 'callCount' is negative.
		:raises ValueError:   If parameter 'callKind' is None.
		:raises TypeError:    If parameter 'callKind' is not of type :class:`CallKind`.
		:raises TypeError:    If parameter 'callSite' is not of type :class:`~pyTooling.ControlFlow.BasicBlock`.
		:raises ValueError:   If parameter 'callSite' is given, but the caller has no control flow graph.
		:raises ValueError:   If parameter 'callSite' belongs to another control flow graph than the caller's.
		:raises ValueError:   If parameter 'callSite' is not a block of :attr:`~pyTooling.ControlFlow.BlockKind.Code`.

		.. seealso::

		   :meth:`CallFrom`
		      |rarr| Create an inbound call from a calling function to this function.
		"""
		return Call(
			self, callee, callKind, callSite=callSite, count=callCount, value=callValue, keyValuePairs=keyValuePairs
		)

	def CallFrom(
		self,
		caller:        Function,
		callCount:     Nullable[int]                    = None,
		callValue:     Nullable[Any]                    = None,
		callKind:      CallKind                         = CallKind.Default,
		callSite:      Nullable[BasicBlock]             = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None
	) -> Call:
		"""
		Create an inbound call from the calling function to this function.

		:param caller:        The calling function.
		:param callCount:     Optional, how often the call was made. Default: ``None``.
		:param callValue:     Optional, any value attached to the call, e.g. the call's source line. Default: ``None``.
		:param callKind:      Optional, kind of the call. Default: :attr:`CallKind.Default`.
		:param callSite:      Optional, the block of the caller's control flow graph the call is made from.
		                      Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs for the call. Default: ``None``.
		:returns:             The call from the caller to this function.
		:raises ValueError:   If parameter 'caller' is None.
		:raises TypeError:    If parameter 'caller' is not of type :class:`Function`.
		:raises ValueError:   If this function belongs to another graph than parameter 'caller'.
		:raises TypeError:    If parameter 'callCount' is not of type :class:`int`.
		:raises ValueError:   If parameter 'callCount' is negative.
		:raises ValueError:   If parameter 'callKind' is None.
		:raises TypeError:    If parameter 'callKind' is not of type :class:`CallKind`.
		:raises TypeError:    If parameter 'callSite' is not of type :class:`~pyTooling.ControlFlow.BasicBlock`.
		:raises ValueError:   If parameter 'callSite' is given, but the caller has no control flow graph.
		:raises ValueError:   If parameter 'callSite' belongs to another control flow graph than the caller's.
		:raises ValueError:   If parameter 'callSite' is not a block of :attr:`~pyTooling.ControlFlow.BlockKind.Code`.

		.. seealso::

		   :meth:`CallTo`
		      |rarr| Create an outbound call from this function to a called function.
		"""
		return Call(
			caller, self, callKind, callSite=callSite, count=callCount, value=callValue, keyValuePairs=keyValuePairs
		)


@export
class Call(BaseWithCountAndValue):
	"""
	A call in a call graph, leading from the calling function to the called function.

	The call's :class:`CallKind` says how the callee is determined. A function calling itself is a call from and to the
	same function. Two functions can be connected by several calls, e.g. one per call site.
	"""
	_caller:   Function              #: The calling function.
	_callee:   Function              #: The called function.
	_kind:     CallKind              #: Kind of the call.
	_callSite: Nullable[BasicBlock]  #: The block of the caller's control flow graph the call is made from, if it's known.

	def __init__(
		self,
		caller:        Function,
		callee:        Function,
		kind:          CallKind                         = CallKind.Default,
		*,
		callSite:      Nullable[BasicBlock]             = None,
		count:         Nullable[int]                    = None,
		value:         Nullable[Any]                    = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None
	) -> None:
		"""
		Initializes a call between two functions of a graph and adds it to the graph.

		:param caller:        The calling function.
		:param callee:        The called function.
		:param kind:          Optional, kind of the call. Default: :attr:`CallKind.Default`.
		:param callSite:      Optional, the block of the caller's control flow graph the call is made from.
		                      Default: ``None``.
		:param count:         Optional, how often the call was made. Default: ``None``.
		:param value:         Optional, any value attached to the call, e.g. the source line of the call. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:raises TypeError:    If parameter 'count' is not of type :class:`int`.
		:raises ValueError:   If parameter 'count' is negative.
		:raises ValueError:   If parameter 'caller' is None.
		:raises TypeError:    If parameter 'caller' is not of type :class:`Function`.
		:raises ValueError:   If parameter 'callee' is None.
		:raises TypeError:    If parameter 'callee' is not of type :class:`Function`.
		:raises ValueError:   If parameter 'callee' belongs to another graph than parameter 'caller'.
		:raises ValueError:   If parameter 'kind' is None.
		:raises TypeError:    If parameter 'kind' is not of type :class:`CallKind`.
		:raises TypeError:    If parameter 'callSite' is not of type :class:`~pyTooling.ControlFlow.BasicBlock`.
		:raises ValueError:   If parameter 'callSite' is given, but the caller has no control flow graph.
		:raises ValueError:   If parameter 'callSite' belongs to another control flow graph than the caller's.
		:raises ValueError:   If parameter 'callSite' is not a block of :attr:`~pyTooling.ControlFlow.BlockKind.Code`.
		"""
		super().__init__(count, value, keyValuePairs)

		if caller is None:
			raise ValueError("Parameter 'caller' is None.")
		elif not isinstance(caller, Function):
			ex = TypeError("Parameter 'caller' is not of type 'Function'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(caller)}'.")
			raise ex

		if callee is None:
			raise ValueError("Parameter 'callee' is None.")
		elif not isinstance(callee, Function):
			ex = TypeError("Parameter 'callee' is not of type 'Function'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(callee)}'.")
			raise ex
		elif callee._callGraph is not caller._callGraph:
			ex = ValueError("Parameter 'callee' belongs to another graph than parameter 'caller'.")
			ex.add_note(f"Got graphs '{caller._callGraph._name}' and '{callee._callGraph._name}'.")
			raise ex

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, CallKind):
			ex = TypeError("Parameter 'kind' is not of type 'CallKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex

		if callSite is not None:
			if not isinstance(callSite, BasicBlock):
				ex = TypeError("Parameter 'callSite' is not of type 'BasicBlock'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(callSite)}'.")
				raise ex
			elif caller._controlFlowGraph is None:
				ex = ValueError("Parameter 'callSite' is given, but the caller has no control flow graph.")
				ex.add_note(f"Got caller '{caller._id}'.")
				raise ex
			elif callSite._controlFlowGraph is not caller._controlFlowGraph:
				ex = ValueError("Parameter 'callSite' belongs to another control flow graph than the caller's.")
				ex.add_note(f"Got graphs '{callSite._controlFlowGraph._name}' and '{caller._controlFlowGraph._name}'.")
				raise ex
			elif callSite._kind is not BlockKind.Code:
				ex = ValueError("Parameter 'callSite' is not a block of code.")
				ex.add_note(f"Got block '{callSite._id}' of kind '{callSite._kind}'.")
				raise ex

		self._caller =   caller
		self._callee =   callee
		self._kind =     kind
		self._callSite = callSite

		caller._outboundCalls.append(self)
		callee._inboundCalls.append(self)
		caller._callGraph._calls.append(self)

	@readonly
	def Caller(self) -> Function:
		"""
		Read-only property to access the calling function (:attr:`_caller`).

		:returns: The caller.
		"""
		return self._caller

	@readonly
	def Callee(self) -> Function:
		"""
		Read-only property to access the called function (:attr:`_callee`).

		:returns: The callee.
		"""
		return self._callee

	@readonly
	def Kind(self) -> CallKind:
		"""
		Read-only property to access the call's kind (:attr:`_kind`).

		:returns: Kind of the call.
		"""
		return self._kind

	@readonly
	def CallSite(self) -> Nullable[BasicBlock]:
		"""
		Read-only property to access the block of the caller's control flow graph the call is made from (:attr:`_callSite`).

		:returns: The call site, or ``None`` if it's unknown.
		"""
		return self._callSite


@export
class CallGraph(Base):
	"""
	The call graph of a program: its functions and the calls between them.

	A function is looked up by its ID: :pycode:`graph.GetFunction("main")` returns the function with ID ``main``, and
	:pycode:`graph.ContainsFunction("main")` checks if the graph has one. :meth:`IterateFunctions` yields the functions in
	the order they were created. The graph's dunder methods serve its key-value-pairs, like a function's or a call's.
	"""
	_name:      str                       #: Name of the graph, e.g. of the program or the translation unit.
	_functions: dict[Hashable, Function]  #: Functions of the graph by ID, in the order they were created.
	_calls:     list[Call]                #: Calls of the graph, in the order they were created.

	def __init__(self, name: str, *, keyValuePairs: Nullable[Mapping[Hashable, Any]] = None) -> None:
		"""
		Initializes an empty call graph.

		:param name:          Name of the graph, e.g. of the program or the translation unit.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:raises ValueError:   If parameter 'name' is None.
		:raises TypeError:    If parameter 'name' is not of type :class:`str`.
		:raises ValueError:   If parameter 'name' is empty.
		"""
		super().__init__(keyValuePairs)

		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		self._name =      name
		self._functions = {}
		self._calls =     []

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name of the graph (:attr:`_name`).

		:returns: Name of the graph.
		"""
		return self._name

	@readonly
	def Functions(self) -> dict[Hashable, Function]:
		"""
		Read-only property to access the functions of the graph by ID (:attr:`_functions`).

		:returns: The functions, in the order they were created.
		"""
		return self._functions

	@readonly
	def Calls(self) -> list[Call]:
		"""
		Read-only property to access the calls of the graph (:attr:`_calls`).

		:returns: The calls, in the order they were created.
		"""
		return self._calls

	@readonly
	def FunctionCount(self) -> int:
		"""
		Read-only property to return the number of functions in the graph.

		:returns: Number of functions.
		"""
		return len(self._functions)

	def ContainsFunction(self, functionID: Hashable) -> bool:
		"""
		Check if the graph has a function with the given ID.

		:param functionID: ID of the function.
		:returns:          ``True``, if the graph has a function with that ID.
		"""
		return functionID in self._functions

	def GetFunction(self, functionID: Hashable) -> Function:
		"""
		Return the function with the given ID.

		:param functionID: ID of the function.
		:returns:          The function with that ID.
		:raises KeyError:  If the graph has no function with that ID.
		"""
		return self._functions[functionID]

	def IterateFunctions(
		self,
		predicate: Nullable[Predicate[Function]] = None
	) -> Generator[Function, None, None]:
		"""
		Iterate all or selected functions of the graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip functions in the generator.

		:param predicate: Optional, filter function accepting any function and returning a boolean.
		:returns:         A generator to iterate the functions, in the order they were created.
		"""
		if predicate is None:
			yield from self._functions.values()
		else:
			for function in self._functions.values():
				if predicate(function):
					yield function

	def ToGraph(self) -> Graph:
		"""
		Convert the call graph into a :class:`~pyTooling.Graph.Graph`.

		Every function becomes a :class:`~pyTooling.Graph.Vertex` with the function's ID as
		:attr:`~pyTooling.Graph.Vertex.ID` and the function's value as :attr:`~pyTooling.Graph.Vertex.Value`, so
		:meth:`Graph.GetVertexByID <pyTooling.Graph.Graph.GetVertexByID>` finds a function's vertex. Every call becomes an
		:class:`~pyTooling.Graph.Edge` from the caller to the callee, with the call's kind as
		:attr:`~pyTooling.Graph.BaseEdge.Kind` and the call's value as value.

		The graph, its vertices and its edges carry a copy of the key-value-pairs of the call graph, its functions and its
		calls. Vertices and edges carry these key-value-pairs more, which a writer like :mod:`pyTooling.Graph.GraphML`
		writes out:

		* ``kind``: the function's :class:`FunctionKind` or the call's :class:`CallKind` member, whose :func:`str` is its
		  name.
		* ``count``: the execution count; only if it's known.
		* ``callsite``: on an edge, the ID of the call site's block; only if the call site is known.

		:returns: The graph, named like the call graph.
		"""
		graph = Graph(name=self._name, keyValuePairs=self._dict)

		vertices: dict[Hashable, Vertex] = {}
		for function in self._functions.values():
			keyValuePairs: dict[Hashable, Any] = {**function._dict, "kind": function._kind}
			if function._count is not None:
				keyValuePairs["count"] = function._count

			vertices[function._id] = Vertex(
				vertexID=function._id,
				value=function._value,
				keyValuePairs=keyValuePairs,
				graph=graph
			)

		for call in self._calls:
			keyValuePairs = {**call._dict, "kind": call._kind}
			if call._count is not None:
				keyValuePairs["count"] = call._count

			if call._callSite is not None:
				keyValuePairs["callsite"] = call._callSite._id

			vertices[call._caller._id].EdgeToVertex(
				vertices[call._callee._id],
				edgeValue=call._value,
				edgeKind=call._kind,
				keyValuePairs=keyValuePairs
			)

		return graph


# ``Function`` has a property named like the class ``CallGraph``, so it annotates its field with this alias.
_CallGraph = CallGraph
