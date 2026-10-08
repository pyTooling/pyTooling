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
A data structure to describe the **control flow graph** of a function: its basic blocks and the edges between them.

A :class:`ControlFlowGraph` describes one function, e.g. a C or C++ function or a Python code object. A
:class:`BasicBlock` is a sequence of code, which control enters at its top and leaves at its bottom. An :class:`Edge`
leads from a block to a block control continues with, so a block with several outbound edges branches - a ``switch``
has an edge per target. An :class:`EdgeKind` says why control continues there.

Every graph has an entry block and an exit block. An exception is an :attr:`EdgeKind.Exception` edge: to the block of
the handler catching it - a C++ ``catch`` or a Python ``except`` clause - or, if none does, to the graph's unwind
block, through which it leaves the function.

Blocks and edges carry an optional execution count, e.g. from a code coverage report, and an optional value of any
type, e.g. the source lines of a block. :meth:`ControlFlowGraph.ToGraph` converts a control flow graph into a
:class:`~pyTooling.Graph.Graph`.

.. hint::

   See :ref:`high-level help <STRUCT/ControlFlow>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Graph`
      |rarr| The graph data structure a control flow graph is converted into.
   :mod:`pyTooling.Graph.GraphML`
      |rarr| Writing a graph as a GraphML document.
"""
from __future__            import annotations

from enum                  import Enum
from typing                import Any, Hashable, Iterator, Optional as Nullable

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.Graph       import Graph, Vertex
from pyTooling.MetaClasses import ExtendedType


@export
class BlockKind(Enum):
	"""
	Kind of a basic block.

	A :class:`ControlFlowGraph` has exactly one entry block and one exit block, and at most one unwind block. Every other
	block holds code.
	"""
	Code =   0  #: A block of code, which control enters at its top and leaves at its bottom.
	Entry =  1  #: The block control enters the function through.
	Exit =   2  #: The block control leaves the function through, when the function returns.
	Unwind = 3  #: The block an exception leaves the function through, when no handler in the function catches it.

	def __str__(self) -> str:
		"""
		Return the member's name.

		:returns: Name of the member, e.g. ``Entry``.
		"""
		return self.name


@export
class EdgeKind(Enum):
	"""
	Kind of an edge: why control continues with the edge's destination.
	"""
	Default =     0  #: The edge wasn't classified, e.g. an arc between two lines a code coverage tool reports.
	FallThrough = 1  #: Control continues with the next block in code order, e.g. the side of a condition not jumping.
	Jump =        2  #: Control jumps to the destination, e.g. a taken branch, a ``goto``, or a ``switch`` case.
	Exception =   3  #: An exception leaves the block, e.g. by a C++ ``throw``, a Python ``raise``, or from a call.
	Abnormal =    4  #: Control leaves the block without a jump or an exception, e.g. by calling ``exit()``.

	def __str__(self) -> str:
		"""
		Return the member's name.

		:returns: Name of the member, e.g. ``FallThrough``.
		"""
		return self.name


@export
class ControlFlowError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.ControlFlow`."""


@export
class DuplicateBlockError(ControlFlowError):
	"""The exception raised for a block a graph has already: one with the same ID, or a second entry, exit or unwind."""


@export
class DuplicateEdgeError(ControlFlowError):
	"""The exception raised for an edge, which connects the same two blocks as an edge of the same kind."""


@export
class Base(metaclass=ExtendedType, slots=True):
	"""
	Base-class of basic blocks and edges, which both carry an execution count and a value.
	"""
	_count: Nullable[int]  #: How often the block or edge was executed, or ``None`` if that's unknown.
	_value: Any            #: Any value attached to the block or edge.

	def __init__(self, count: Nullable[int] = None, value: Any = None) -> None:
		"""
		Initializes the execution count and the value of a block or an edge.

		:param count:       Optional, how often the block or edge was executed. Default: ``None``.
		:param value:       Optional, any value attached to the block or edge. Default: ``None``.
		:raises TypeError:  If parameter 'count' is not of type :class:`int`.
		:raises ValueError: If parameter 'count' is negative.
		"""
		self.Count =  count
		self._value = value

	@property
	def Count(self) -> Nullable[int]:
		"""
		Property to access how often the block or edge was executed (:attr:`_count`).

		:returns:           The execution count, or ``None`` if it's unknown.
		:raises TypeError:  If the assigned count is not of type :class:`int`.
		:raises ValueError: If the assigned count is negative.
		"""
		return self._count

	@Count.setter
	def Count(self, count: Nullable[int]) -> None:
		if count is not None:
			if not isinstance(count, int) or isinstance(count, bool):
				ex = TypeError("Parameter 'count' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(count)}'.")
				raise ex
			elif count < 0:
				ex = ValueError("Parameter 'count' is negative.")
				ex.add_note(f"Got value '{count}'.")
				raise ex

		self._count = count

	@property
	def Value(self) -> Any:
		"""
		Property to access the value attached to the block or edge (:attr:`_value`).

		:returns: The value, or ``None`` if none is attached.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Any) -> None:
		self._value = value


@export
class BasicBlock(Base):
	"""
	A basic block of a control flow graph: a sequence of code, which control enters at its top and leaves at its bottom.

	A block is identified by an ID unique within its graph, e.g. a compiler's block number or a line number. Its outbound
	edges lead to the blocks control continues with.
	"""
	_graph:         ControlFlowGraph  #: The graph this block belongs to.
	_id:            Hashable          #: ID of the block, unique within its graph.
	_kind:          BlockKind         #: Kind of the block.
	_inboundEdges:  list[Edge]        #: Edges leading to this block.
	_outboundEdges: list[Edge]        #: Edges leading from this block to the blocks control continues with.

	def __init__(
		self,
		graph:   ControlFlowGraph,
		blockID: Hashable,
		*,
		kind:    BlockKind     = BlockKind.Code,
		count:   Nullable[int] = None,
		value:   Any           = None
	) -> None:
		"""
		Initializes a basic block and adds it to its graph.

		A graph creates its entry and exit block itself. A block of :attr:`BlockKind.Unwind` becomes the graph's unwind
		block.

		:param graph:                The graph the block belongs to.
		:param blockID:              ID of the block, unique within its graph.
		:param kind:                 Optional, kind of the block. Default: :attr:`BlockKind.Code`.
		:param count:                Optional, how often the block was executed. Default: ``None``.
		:param value:                Optional, any value attached to the block, e.g. its source lines. Default: ``None``.
		:raises TypeError:           If parameter 'count' is not of type :class:`int`.
		:raises ValueError:          If parameter 'count' is negative.
		:raises ValueError:          If parameter 'graph' is None.
		:raises TypeError:           If parameter 'graph' is not of type :class:`ControlFlowGraph`.
		:raises ValueError:          If parameter 'blockID' is None.
		:raises TypeError:           If parameter 'blockID' is not hashable.
		:raises ValueError:          If parameter 'kind' is None.
		:raises TypeError:           If parameter 'kind' is not of type :class:`BlockKind`.
		:raises DuplicateBlockError: If the graph has a block with that ID already.
		:raises DuplicateBlockError: If the block is an entry, exit or unwind block, and the graph has one already.
		"""
		super().__init__(count, value)

		if graph is None:
			raise ValueError("Parameter 'graph' is None.")
		elif not isinstance(graph, ControlFlowGraph):
			ex = TypeError("Parameter 'graph' is not of type 'ControlFlowGraph'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(graph)}'.")
			raise ex

		if blockID is None:
			raise ValueError("Parameter 'blockID' is None.")
		elif not isinstance(blockID, Hashable):
			ex = TypeError("Parameter 'blockID' is not hashable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(blockID)}'.")
			raise ex
		elif blockID in graph._blocks:
			raise DuplicateBlockError(f"Control flow graph '{graph._name}' has a block '{blockID}' already.")

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, BlockKind):
			ex = TypeError("Parameter 'kind' is not of type 'BlockKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex
		elif kind is BlockKind.Entry and len(graph._blocks) > 0:
			raise DuplicateBlockError(f"Control flow graph '{graph._name}' has an entry block already.")
		elif kind is BlockKind.Exit and len(graph._blocks) > 1:
			raise DuplicateBlockError(f"Control flow graph '{graph._name}' has an exit block already.")
		elif kind is BlockKind.Unwind and graph._unwind is not None:
			raise DuplicateBlockError(f"Control flow graph '{graph._name}' has an unwind block already.")

		self._graph =         graph
		self._id =            blockID
		self._kind =          kind
		self._inboundEdges =  []
		self._outboundEdges = []

		graph._blocks[blockID] = self
		if kind is BlockKind.Unwind:
			graph._unwind = self

	@readonly
	def Graph(self) -> ControlFlowGraph:
		"""
		Read-only property to access the graph this block belongs to (:attr:`_graph`).

		:returns: The control flow graph.
		"""
		return self._graph

	@readonly
	def ID(self) -> Hashable:
		"""
		Read-only property to access the block's ID (:attr:`_id`).

		:returns: ID of the block, unique within its graph.
		"""
		return self._id

	@readonly
	def Kind(self) -> BlockKind:
		"""
		Read-only property to access the block's kind (:attr:`_kind`).

		:returns: Kind of the block.
		"""
		return self._kind

	@readonly
	def InboundEdges(self) -> tuple[Edge, ...]:
		"""
		Read-only property to return the edges leading to this block.

		:returns: The inbound edges, in the order they were created.
		"""
		return tuple(self._inboundEdges)

	@readonly
	def OutboundEdges(self) -> tuple[Edge, ...]:
		"""
		Read-only property to return the edges leading from this block to the blocks control continues with.

		:returns: The outbound edges, in the order they were created.
		"""
		return tuple(self._outboundEdges)


@export
class Edge(Base):
	"""
	An edge of a control flow graph, leading from a block to a block control continues with.

	The edge's :class:`EdgeKind` says why control continues there. Two blocks can be connected by edges of different
	kinds, but only by one edge of each kind.
	"""
	_source:      BasicBlock  #: The block control leaves.
	_destination: BasicBlock  #: The block control continues with.
	_kind:        EdgeKind    #: Kind of the edge.

	def __init__(
		self,
		source:      BasicBlock,
		destination: BasicBlock,
		kind:        EdgeKind      = EdgeKind.Default,
		*,
		count:       Nullable[int] = None,
		value:       Any           = None
	) -> None:
		"""
		Initializes an edge between two blocks of a graph and adds it to the graph.

		:param source:              The block control leaves.
		:param destination:         The block control continues with.
		:param kind:                Optional, kind of the edge. Default: :attr:`EdgeKind.Default`.
		:param count:               Optional, how often control took the edge. Default: ``None``.
		:param value:               Optional, any value attached to the edge, e.g. a ``case`` label. Default: ``None``.
		:raises TypeError:          If parameter 'count' is not of type :class:`int`.
		:raises ValueError:         If parameter 'count' is negative.
		:raises ValueError:         If parameter 'source' is None.
		:raises TypeError:          If parameter 'source' is not of type :class:`BasicBlock`.
		:raises ValueError:         If parameter 'source' is an exit or unwind block.
		:raises ValueError:         If parameter 'destination' is None.
		:raises TypeError:          If parameter 'destination' is not of type :class:`BasicBlock`.
		:raises ValueError:         If parameter 'destination' is an entry block.
		:raises ValueError:         If parameter 'destination' belongs to another graph than parameter 'source'.
		:raises ValueError:         If parameter 'kind' is None.
		:raises TypeError:          If parameter 'kind' is not of type :class:`EdgeKind`.
		:raises DuplicateEdgeError: If an edge of the same kind connects the two blocks already.
		"""
		super().__init__(count, value)

		if source is None:
			raise ValueError("Parameter 'source' is None.")
		elif not isinstance(source, BasicBlock):
			ex = TypeError("Parameter 'source' is not of type 'BasicBlock'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(source)}'.")
			raise ex
		elif source._kind is BlockKind.Exit or source._kind is BlockKind.Unwind:
			ex = ValueError("Parameter 'source' is an exit or unwind block.")
			ex.add_note(f"Got block '{source._id}' of kind '{source._kind}'.")
			raise ex

		if destination is None:
			raise ValueError("Parameter 'destination' is None.")
		elif not isinstance(destination, BasicBlock):
			ex = TypeError("Parameter 'destination' is not of type 'BasicBlock'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(destination)}'.")
			raise ex
		elif destination._kind is BlockKind.Entry:
			ex = ValueError("Parameter 'destination' is an entry block.")
			ex.add_note(f"Got block '{destination._id}'.")
			raise ex
		elif destination._graph is not source._graph:
			ex = ValueError("Parameter 'destination' belongs to another graph than parameter 'source'.")
			ex.add_note(f"Got graphs '{source._graph._name}' and '{destination._graph._name}'.")
			raise ex

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, EdgeKind):
			ex = TypeError("Parameter 'kind' is not of type 'EdgeKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex

		for edge in source._outboundEdges:
			if edge._destination is destination and edge._kind is kind:
				ex = DuplicateEdgeError(f"Blocks '{source._id}' and '{destination._id}' are connected by such an edge already.")
				ex.add_note(f"Got edge kind '{kind}'.")
				raise ex

		self._source =      source
		self._destination = destination
		self._kind =        kind

		source._outboundEdges.append(self)
		destination._inboundEdges.append(self)
		source._graph._edges.append(self)

	@readonly
	def Source(self) -> BasicBlock:
		"""
		Read-only property to access the block control leaves (:attr:`_source`).

		:returns: The source block.
		"""
		return self._source

	@readonly
	def Destination(self) -> BasicBlock:
		"""
		Read-only property to access the block control continues with (:attr:`_destination`).

		:returns: The destination block.
		"""
		return self._destination

	@readonly
	def Kind(self) -> EdgeKind:
		"""
		Read-only property to access the edge's kind (:attr:`_kind`).

		:returns: Kind of the edge.
		"""
		return self._kind


@export
class ControlFlowGraph(metaclass=ExtendedType, slots=True):
	"""
	The control flow graph of a function: its basic blocks, the edges between them, and its entry and exit block.

	A block is looked up by its ID: :pycode:`graph[3]` returns the block with ID ``3``, and :pycode:`3 in graph` checks
	if the graph has one. Iterating the graph yields its blocks in the order they were created.
	"""
	_name:   str                         #: Name of the function.
	_blocks: dict[Hashable, BasicBlock]  #: Blocks of the graph by ID, in the order they were created.
	_edges:  list[Edge]                  #: Edges of the graph, in the order they were created.
	_entry:  BasicBlock                  #: The block control enters the function through.
	_exit:   BasicBlock                  #: The block control leaves the function through, when the function returns.
	_unwind: Nullable[BasicBlock]        #: The block an exception leaves the function through, if the graph has one.

	def __init__(self, name: str, *, entryID: Hashable = "entry", exitID: Hashable = "exit") -> None:
		"""
		Initializes a control flow graph of a function, with an entry and an exit block.

		The entry and the exit are the graph's first two blocks. An unwind block is created like any other block, as a
		block of :attr:`BlockKind.Unwind`.

		:param name:        Name of the function.
		:param entryID:     Optional, ID of the entry block. Default: ``"entry"``.
		:param exitID:      Optional, ID of the exit block. Default: ``"exit"``.
		:raises ValueError: If parameter 'name' is None.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises ValueError: If parameter 'entryID' is None.
		:raises TypeError:  If parameter 'entryID' is not hashable.
		:raises ValueError: If parameter 'exitID' is None.
		:raises TypeError:  If parameter 'exitID' is not hashable.
		:raises ValueError: If parameter 'exitID' equals parameter 'entryID'.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		for parameterName, blockID in (
			("entryID", entryID),
			("exitID",  exitID)
		):
			if blockID is None:
				raise ValueError(f"Parameter '{parameterName}' is None.")
			elif not isinstance(blockID, Hashable):
				ex = TypeError(f"Parameter '{parameterName}' is not hashable.")
				ex.add_note(f"Got type '{getFullyQualifiedName(blockID)}'.")
				raise ex

		if exitID == entryID:
			ex = ValueError("Parameter 'exitID' equals parameter 'entryID'.")
			ex.add_note(f"Got value '{exitID}'.")
			raise ex

		self._name =   name
		self._blocks = {}
		self._edges =  []
		self._unwind = None
		self._entry =  BasicBlock(self, entryID, kind=BlockKind.Entry)
		self._exit =   BasicBlock(self, exitID, kind=BlockKind.Exit)

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name of the function (:attr:`_name`).

		:returns: Name of the function.
		"""
		return self._name

	@readonly
	def Entry(self) -> BasicBlock:
		"""
		Read-only property to access the block control enters the function through (:attr:`_entry`).

		:returns: The entry block.
		"""
		return self._entry

	@readonly
	def Exit(self) -> BasicBlock:
		"""
		Read-only property to access the block control leaves the function through, when it returns (:attr:`_exit`).

		:returns: The exit block.
		"""
		return self._exit

	@readonly
	def Unwind(self) -> Nullable[BasicBlock]:
		"""
		Read-only property to access the block an exception leaves the function through (:attr:`_unwind`).

		:returns: The unwind block, or ``None`` if the graph has none.
		"""
		return self._unwind

	@readonly
	def Blocks(self) -> dict[Hashable, BasicBlock]:
		"""
		Read-only property to access the blocks of the graph by ID (:attr:`_blocks`).

		:returns: The blocks, in the order they were created.
		"""
		return self._blocks

	@readonly
	def Edges(self) -> list[Edge]:
		"""
		Read-only property to access the edges of the graph (:attr:`_edges`).

		:returns: The edges, in the order they were created.
		"""
		return self._edges

	def __len__(self) -> int:
		"""
		Return the number of blocks in the graph, including its entry, exit and unwind block.

		:returns: Number of blocks.
		"""
		return len(self._blocks)

	def __iter__(self) -> Iterator[BasicBlock]:
		"""
		Iterate the blocks of the graph.

		:returns: An iterator over the blocks, in the order they were created.
		"""
		return iter(self._blocks.values())

	def __contains__(self, blockID: Hashable) -> bool:
		"""
		Check if the graph has a block with the given ID.

		:param blockID: ID of the block.
		:returns:       ``True``, if the graph has a block with that ID.
		"""
		return blockID in self._blocks

	def __getitem__(self, blockID: Hashable) -> BasicBlock:
		"""
		Return the block with the given ID.

		:param blockID:   ID of the block.
		:returns:         The block with that ID.
		:raises KeyError: If the graph has no block with that ID.
		"""
		return self._blocks[blockID]

	def ToGraph(self) -> Graph:
		"""
		Convert the control flow graph into a :class:`~pyTooling.Graph.Graph`.

		Every block becomes a :class:`~pyTooling.Graph.Vertex` with the block's ID as
		:attr:`~pyTooling.Graph.Vertex.ID` and the block's value as :attr:`~pyTooling.Graph.Vertex.Value`, so
		:meth:`Graph.GetVertexByID <pyTooling.Graph.Graph.GetVertexByID>` finds a block's vertex. Every edge becomes an
		:class:`~pyTooling.Graph.Edge` in the direction control flows, with the edge's kind as
		:attr:`~pyTooling.Graph.BaseEdge.Kind` and the edge's value as value.

		Vertices and edges carry two key-value-pairs, which a writer like :mod:`pyTooling.Graph.GraphML` writes out:

		* ``kind``: the block's :class:`BlockKind` or the edge's :class:`EdgeKind` member, whose :func:`str` is its name.
		* ``count``: the execution count; only if it's known.

		:returns: The graph, named like the control flow graph.
		"""
		graph = Graph(name=self._name)

		vertices: dict[Hashable, Vertex] = {}
		for block in self._blocks.values():
			keyValuePairs: dict[str, Any] = {"kind": block._kind}
			if block._count is not None:
				keyValuePairs["count"] = block._count

			vertices[block._id] = Vertex(vertexID=block._id, value=block._value, keyValuePairs=keyValuePairs, graph=graph)

		for edge in self._edges:
			keyValuePairs = {"kind": edge._kind}
			if edge._count is not None:
				keyValuePairs["count"] = edge._count

			vertices[edge._source._id].EdgeToVertex(
				vertices[edge._destination._id],
				edgeValue=edge._value,
				edgeKind=edge._kind,
				keyValuePairs=keyValuePairs
			)

		return graph
