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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A powerful **graph** data structure for Python.

Graph algorithms using all vertexes are provided as methods on the graph instance. Whereas graph algorithms based on a
starting vertex are provided as methods on a vertex.
"""
import heapq
from collections import deque
from typing import TypeVar, List, Generic, Union, Optional as Nullable, Iterable, Hashable, Dict, \
	Iterator as typing_Iterator, Set, Deque, Generator, Iterator

from pyTooling.Decorators import export
from pyTooling.MetaClasses import ExtendedType


VertexIDType = TypeVar("VertexIDType", bound=Hashable)
"""A type variable for a vertex's ID."""

VertexValueType = TypeVar("VertexValueType")
"""A type variable for a vertex's value."""

VertexDictKeyType = TypeVar("VertexDictKeyType", bound=Hashable)
"""A type variable for a vertex's dictionary keys."""

VertexDictValueType = TypeVar("VertexDictValueType")
"""A type variable for a vertex's dictionary values."""

EdgeIDType = TypeVar("EdgeIDType", bound=Hashable)
"""A type variable for an edge's ID."""

EdgeWeightType = TypeVar("EdgeWeightType", bound=Union[int, float])
"""A type variable for an edge's weight."""

EdgeValueType = TypeVar("EdgeValueType")
"""A type variable for a edge's value."""

EdgeDictKeyType = TypeVar("EdgeDictKeyType", bound=Hashable)
"""A type variable for a edge's dictionary keys."""

EdgeDictValueType = TypeVar("EdgeDictValueType")
"""A type variable for a edge's dictionary values."""

GraphDictKeyType = TypeVar("GraphDictKeyType", bound=Hashable)
"""A type variable for a graph's dictionary keys."""

GraphDictValueType = TypeVar("GraphDictValueType")
"""A type variable for a graph's dictionary values."""


@export
class Vertex(Generic[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType], metaclass=ExtendedType, useSlots=True):
	"""
	A **vertex** can have a unique ID, a value and attached meta information as key-value pairs. A vertex has references
	to inbound and outbound edges, thus a graph can be traversed in reverse.
	"""
	_graph:     'Graph[VertexIDType, EdgeIDType]'
	_inbound:   List['Edge']
	_outbound:  List['Edge']

	_id:        Nullable[VertexIDType]
	_value:     Nullable[VertexValueType]
	_dict:      Dict[VertexDictKeyType, VertexDictValueType]

	def __init__(self, vertexID: VertexIDType = None, data: VertexValueType = None, graph: 'Graph' = None):
		if graph is None:
			self._graph = Graph()
		else:
			self._graph = graph

		self._id = vertexID
		if vertexID is None:
			self._graph._verticesWithoutID.append(self)
		elif vertexID in self._graph._verticesWithID:
			raise ValueError(f"ID '{vertexID}' already exists in this graph.")
		else:
			self._graph._verticesWithID[vertexID] = self

		self._inbound = []
		self._outbound = []

		self._value = data
		self._dict = {}

	@property
	def Graph(self) -> 'Graph':
		return self._graph

	@property
	def ID(self) -> Nullable[VertexIDType]:
		"""
		Read-only property to access the unique ID of a vertex (:py:attr:`_id`).

		If no ID was given at vertex construction time, ID return None.

		:returns: Unique ID of a vertex, if ID was given at vertex creation time, else None.
		"""
		return self._id

	@property
	def Value(self) -> VertexValueType:
		"""
		Property to get and set the value (:py:attr:`_value`) of a vertex.

		:returns: The value of a vertex.
		"""
		return self._value

	@Value.setter
	def Value(self, value: VertexValueType) -> None:
		self._value = value

	def __getitem__(self, key: VertexDictKeyType) -> VertexDictValueType:
		""".. todo:: Needs documentation."""
		return self._dict[key]

	def __setitem__(self, key: VertexDictKeyType, value: VertexDictValueType) -> None:
		""".. todo:: Needs documentation."""
		self._dict[key] = value

	def __delitem__(self, key: VertexDictKeyType) -> None:
		""".. todo:: Needs documentation."""
		del self._dict[key]

	def __len__(self) -> int:
		"""
		Returns the number of outbound directed edges.

		:returns: Number of outbound edges.
		"""
		return len(self._outbound)

	def LinkToVertex(self, vertex: 'Vertex', edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> None:
		if not isinstance(vertex, Vertex):
			raise Exception()

		# TODO: set edgeID
		edge = Edge(self, vertex, edgeID, edgeWeight, edgeValue)
		self._outbound.append(edge)
		vertex._inbound.append(edge)

	def LinkFromVertex(self, vertex: 'Vertex', edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> None:
		if not isinstance(vertex, Vertex):
			raise Exception()

		edge = Edge(vertex, self, edgeID, edgeWeight, edgeValue)
		vertex._outbound.append(edge)
		self._inbound.append(edge)

	def LinkToNewVertex(self, vertexID: VertexIDType = None, vertexData: VertexValueType = None, edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> 'Vertex':
		vertex = Vertex(vertexID, vertexData, self._graph)

		edge = Edge(self, vertex, edgeID, edgeWeight, edgeValue)
		self._outbound.append(edge)
		vertex._inbound.append(edge)

		return vertex

	def LinkFromNewVertex(self, vertexID: VertexIDType = None, vertexData: VertexValueType = None, edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> 'Vertex':
		vertex = Vertex(vertexID, vertexData, self._graph)

		edge = Edge(vertex, self, edgeID, edgeWeight, edgeValue)
		vertex._outbound.append(edge)
		self._inbound.append(edge)

		return vertex

	def IsRoot(self):
		return len(self._inbound) == 0

	def IsLeaf(self):
		return len(self._outbound) == 0

	def IterateOutboundEdges(self):
		for edge in self._outbound:
			yield edge

	def IterateInboundEdges(self):
		for edge in self._inbound:
			yield edge

	def IterateSuccessorVertexes(self):
		for edge in self._outbound:
			yield edge.Destination

	def IteratePredecessorVertexes(self):
		for edge in self._inbound:
			yield edge.Source

	def IterateVertexesBFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertexes starting from this node in breadth-first search (BFS) order.

		.. seealso::

		   :py:meth:`IterateVertexesDFS` |br|
		      |rarr| Iterate all reachable vertexes DFS order.

		:returns: A generator to iterate vertexes traversed in BFS order.
		"""
		visited: Set[Vertex] = set()
		queue: Deque[Vertex] = deque()

		yield self
		visited.add(self)
		for edge in self._outbound:
			nextVertex = edge.Destination
			if nextVertex is not self:
				queue.appendleft(nextVertex)
				visited.add(nextVertex)

		while queue:
			vertex = queue.pop()
			yield vertex
			for edge in vertex._outbound:
				nextVertex = edge.Destination
				if nextVertex not in visited:
					queue.appendleft(nextVertex)
				visited.add(nextVertex)

	def IterateVertexesDFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertexes starting from this node in depth-first search (DFS) order.

		.. seealso::

		   :py:meth:`IterateVertexesBFS` |br|
		      |rarr| Iterate all reachable vertexes BFS order.

		   Wikipedia - https://en.wikipedia.org/wiki/Depth-first_search

		:returns: A generator to iterate vertexes traversed in DFS order.
		"""
		visited: Set[Vertex] = set()
		stack: List[typing_Iterator[Edge]] = list()

		yield self
		visited.add(self)
		stack.append(iter(self._outbound))

		while True:
			try:
				edge = next(stack[-1])
				nextVertex = edge._destination
				if nextVertex not in visited:
					visited.add(nextVertex)
					yield nextVertex
					if len(nextVertex._outbound) != 0:
						stack.append(iter(nextVertex._outbound))
			except StopIteration:
				stack.pop()

				if len(stack) == 0:
					return

	def ShortestPathToByHops(self, destination: 'Vertex') -> Generator['Vertex', None, None]:
		# BFS based algorithm

		# Trivial case if start is destination
		if self is destination:
			yield self
			return

		# Local struct to create multiple linked-lists forming a paths from current node back to the starting point
		# (actually a tree). Each node holds a reference to the vertex it represents.
		# Hint: slotted classes are faster than '@dataclasses.dataclass'.
		class Node(metaclass=ExtendedType, useSlots=True):
			parent: 'Node'
			ref: Vertex

			def __init__(self, parent: 'Node', ref: Vertex):
				self.parent = parent
				self.ref = ref

			def __str__(self):
				return f"Vertex: {self.ref.ID}"

		# Initially add all reachable vertexes to a queue if vertexes to be processed.
		startNode = Node(None, self)
		visited: Set[Vertex] = set()
		queue: Deque[Node] = deque()

		# Add starting vertex and all its children to the processing list.
		# If a child is the destination, break immediately else go into 'else' branch and use BFS algorithm.
		visited.add(self)
		for edge in self._outbound:
			nextVertex = edge.Destination
			if nextVertex is destination:
				# Child is destination, so construct the last node for path traversal and break from loop.
				destinationNode = Node(startNode, nextVertex)
				break
			if nextVertex is not self:
				# Ignore backward-edges and side-edges.
				# Here self-edges, because there is only the starting vertex in the list of visited edges.
				visited.add(nextVertex)
				queue.appendleft(Node(startNode, nextVertex))
		else:
			# Process queue until destination is found or no further vertexes are reachable.
			while queue:
				node = queue.pop()
				for edge in node.ref._outbound:
					nextVertex = edge.Destination
					# Next reachable vertex is destination, so construct the last node for path traversal and break from loop.
					if nextVertex is destination:
						destinationNode = Node(node, nextVertex)
						break
					# Ignore backward-edges and side-edges.
					if nextVertex not in visited:
						visited.add(nextVertex)
						queue.appendleft(Node(node, nextVertex))
				# Next 3 lines realize a double-break if break was called in inner loop, otherwise continue with outer loop.
				else:
					continue
				break
			else:
				# All reachable vertexes have been processed, but destination was not among them.
				raise KeyError(f"Destination is not reachable.")

		# Reverse order of linked list from destinationNode to startNode
		currentNode = destinationNode
		previousNode = destinationNode.parent
		currentNode.parent = None
		while previousNode is not None:
			node = previousNode.parent
			previousNode.parent = currentNode
			currentNode = previousNode
			previousNode = node

		# Scan reversed linked-list and yield referenced vertexes
		yield startNode.ref
		node = startNode.parent
		while node is not None:
			yield node.ref
			node = node.parent

	def ShortestPathToByWeight(self, destination: 'Vertex') -> Generator['Vertex', None, None]:
		# Dijkstra + heapq
		# Improvements: both-sided Dijkstra (search from start and destination to reduce discovered area.

		# Trivial case if start is destination
		if self is destination:
			yield self
			return

		# Local struct to create multiple-linked lists forming a paths from current node back to the starting point
		# (actually a tree). Each node holds the overall weight from start to current node and a reference to the vertex it
		# represents.
		# Hint: slotted classes are faster than '@dataclasses.dataclass'.
		class Node(metaclass=ExtendedType, useSlots=True):
			parent: 'Node'
			distance: EdgeWeightType
			ref: Vertex

			def __init__(self, parent: 'Node', distance: EdgeWeightType, ref: Vertex):
				self.parent = parent
				self.distance = distance
				self.ref = ref

			def __lt__(self, other):
				return self.distance < other.distance

			def __str__(self):
				return f"Vertex: {self.ref.ID}"

		visited: Set['Vertex'] = set()
		startNode = Node(None, 0, self)
		priorityQueue = [startNode]

		# Add starting vertex and all its children to the processing list.
		# If a child is the destination, break immediately else go into 'else' branch and use Dijkstra algorithm.
		visited.add(self)
		for edge in self._outbound:
			nextVertex = edge.Destination
			# Child is destination, so construct the last node for path traversal and break from loop.
			if nextVertex is destination:
				destinationNode = Node(startNode, edge._weight, nextVertex)
				break
			# Ignore backward-edges and side-edges.
			# Here self-edges, because there is only the starting vertex in the list of visited edges.
			if nextVertex is not self:
				visited.add(nextVertex)
				heapq.heappush(priorityQueue, Node(startNode, edge._weight, nextVertex))
		else:
			# Process priority queue until destination is found or no further vertexes are reachable.
			while priorityQueue:
				node = heapq.heappop(priorityQueue)
				for edge in node.ref._outbound:
					nextVertex = edge.Destination
					# Next reachable vertex is destination, so construct the last node for path traversal and break from loop.
					if nextVertex is destination:
						destinationNode = Node(node, node.distance + edge._weight, nextVertex)
						break
					# Ignore backward-edges and side-edges.
					if nextVertex not in visited:
						visited.add(nextVertex)
						heapq.heappush(priorityQueue, Node(node, node.distance + edge._weight, nextVertex))
				# Next 3 lines realize a double-break if break was called in inner loop, otherwise continue with outer loop.
				else:
					continue
				break
			else:
				# All reachable vertexes have been processed, but destination was not among them.
				raise KeyError(f"Destination is not reachable.")

		# Reverse order of linked-list from destinationNode to startNode
		currentNode = destinationNode
		previousNode = destinationNode.parent
		currentNode.parent = None
		while previousNode is not None:
			node = previousNode.parent
			previousNode.parent = currentNode
			currentNode = previousNode
			previousNode = node

		# Scan reversed linked-list and yield referenced vertexes
		yield (startNode.ref, startNode.distance)
		node = startNode.parent
		while node is not None:
			yield (node.ref, node.distance)
			node = node.parent

		# Other possible algorithms:
		# * Bellman-Ford
		# * Floyd-Warshall

	def PathExistsTo(self, destination: 'Vertex'):
		raise NotImplementedError()
		# DFS
		# Union find

	def MaximumFlowTo(self, destination: 'Vertex'):
		raise NotImplementedError()
		# Ford-Fulkerson algorithm
		# Edmons-Karp algorithm
		# Dinic's algorithm

	def __repr__(self) -> str:
		"""
		Returns a detailed string representation of the vertex.

		:returns: The detailed string representation of the vertex.
		"""
		vertexID = value = ""
		sep = ": "
		if self._id is not None:
			vertexID = f"{sep}vertexID='{self._id}'"
			sep = "; "
		if self._value is not None:
			value = f"{sep}value='{self._value}'"

		return f"<vertex{vertexID}{value}>"

	def __str__(self) -> str:
		"""
		Return a string representation of the vertex.

		Order of resolution:

		1. If :py:attr:`_value` is not None, return the string representation of :py:attr:`_value`.
		2. If :py:attr:`_id` is not None, return the string representation of :py:attr:`_id`.
		3. Else, return :py:meth:`__repr__`.

		:returns: The resolved string representation of the vertex.
		"""
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()


@export
class Edge(Generic[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]):
	"""
	An **edge** can have a unique ID, a value, a weight and attached meta information as key-value pairs. All edges are
	directed.
	"""
	_id:          Nullable[EdgeIDType]
	_source:      Vertex
	_destination: Vertex
	_weight:      Nullable[EdgeWeightType]
	_value:       Nullable[EdgeValueType]
	_dict:        Dict[EdgeDictKeyType, EdgeDictValueType]

	def __init__(self, source: Vertex, destination: Vertex, edgeID: EdgeIDType = None, weight: EdgeWeightType = None, value: VertexValueType = None):
		if source._graph is not destination._graph:
			raise Exception(f"Source vertex and destination vertex are not in same graph.")

		if not isinstance(source, Vertex):
			raise TypeError()
		elif not isinstance(destination, Vertex):
			raise TypeError()

		self._id = edgeID
		self._source = source
		self._destination = destination
		self._weight = weight
		self._value = value
		self._dict = {}

	@property
	def ID(self) -> Nullable[EdgeIDType]:
		return self._id

	@property
	def Source(self) -> Vertex:
		return self._source

	@property
	def Destination(self) -> Vertex:
		return self._destination

	@property
	def Weight(self) -> EdgeWeightType:
		return self._weight

	@Weight.setter
	def Weight(self, value: Nullable[EdgeWeightType]) -> None:
		self._weight = value

	@property
	def Value(self) -> VertexValueType:
		"""
		Property to get and set the value (:py:attr:`_value`) of a vertex.

		:returns: The value of a vertex.
		"""
		return self._value

	@Value.setter
	def Value(self, value: VertexValueType) -> None:
		self._value = value

	def __getitem__(self, key: VertexDictKeyType) -> VertexDictValueType:
		""".. todo:: Needs documentation."""
		return self._dict[key]

	def __setitem__(self, key: VertexDictKeyType, value: VertexDictValueType) -> None:
		""".. todo:: Needs documentation."""
		self._dict[key] = value

	def __delitem__(self, key: VertexDictKeyType) -> None:
		""".. todo:: Needs documentation."""
		del self._dict[key]


@export
class Graph(Generic[GraphDictKeyType, GraphDictValueType, VertexIDType, EdgeIDType, VertexValueType, VertexDictKeyType, VertexDictValueType], metaclass=ExtendedType, useSlots=True):
	"""
	A **graph** data structure is represented by an instance of :py:class:`~pyTooling.Graph.Graph` holding references to
	all nodes. Nodes are instances of :py:class:`~pyTooling.Graph.Vertex` classes and directed links between nodes are
	made of :py:class:`~pyTooling.Graph.Edge` instances. A graph can have attached meta information as key-value pairs.
	"""
	_name:              str
	_verticesWithID:    Dict[VertexIDType, Vertex]
	_verticesWithoutID: List[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]
	_edgesWithID:       Dict[EdgeIDType, Edge]
	_edgesWithoutID:    List[Edge]
	_dict:              Dict[GraphDictKeyType, GraphDictValueType]

	def __init__(self, name: str = None):
		self._name = name
		self._verticesWithID = {}
		self._verticesWithoutID = []
		self._edgesWithID = {}
		self._edgesWithoutID = []
		self._dict = {}

	@property
	def Name(self) -> str:
		return self._name

	@Name.setter
	def Name(self, value: str) -> None:
		if not isinstance(value, str):
			raise TypeError()

		self._name = value

	def __getitem__(self, key: VertexDictKeyType) -> VertexDictValueType:
		""".. todo:: Needs documentation."""
		return self._dict[key]

	def __setitem__(self, key: VertexDictKeyType, value: VertexDictValueType) -> None:
		""".. todo:: Needs documentation."""
		self._dict[key] = value

	def __delitem__(self, key: VertexDictKeyType) -> None:
		""".. todo:: Needs documentation."""
		del self._dict[key]

	def __len__(self) -> int:
		return len(self._verticesWithoutID) + len(self._verticesWithID)

	def __iter__(self) -> Iterator[Vertex]:
		def gen():
			yield from self._verticesWithoutID
			yield from self._verticesWithID
		return iter(gen())

	def IterateBFS(self):
		raise NotImplementedError()

	def IterateDFS(self):

		class Iterator():
			visited = [False for _ in range(self.__len__())]

	def CheckForNegativeCycles(self):
		raise NotImplementedError()
		# Bellman-Ford
		# Floyd-Warshall

	def IsStronglyConnected(self):
		raise NotImplementedError()

	def GetStronglyConnectedComponents(self):
		raise NotImplementedError()
		# Tarjan's and Kosaraju's algorithm

	def TravelingSalesmanProblem(self):
		raise NotImplementedError()
		# Held-Karp
		# branch and bound

	def GetBridges(self):
		raise NotImplementedError()

	def GetArticulationPoints(self):
		raise NotImplementedError()

	def MinimumSpanningTree(self):
		raise NotImplementedError()
		# Kruskal
		# Prim's algorithm
		# Buruvka's algorithm
