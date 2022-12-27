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

Graph algorithms using all vertices are provided as methods on the graph instance. Whereas graph algorithms based on a
starting vertex are provided as methods on a vertex.
"""
import heapq
from collections import deque
from typing import TypeVar, List, Generic, Union, Optional as Nullable, Iterable, Hashable, Dict, Iterator as typing_Iterator, Set, Deque, Generator, Iterator

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
"""A type variable for an edge's value."""

EdgeDictKeyType = TypeVar("EdgeDictKeyType", bound=Hashable)
"""A type variable for an edge's dictionary keys."""

EdgeDictValueType = TypeVar("EdgeDictValueType")
"""A type variable for an edge's dictionary values."""

ComponentDictKeyType = TypeVar("ComponentDictKeyType", bound=Hashable)
"""A type variable for a component's dictionary keys."""

ComponentDictValueType = TypeVar("ComponentDictValueType")
"""A type variable for a component's dictionary values."""

GraphDictKeyType = TypeVar("GraphDictKeyType", bound=Hashable)
"""A type variable for a graph's dictionary keys."""

GraphDictValueType = TypeVar("GraphDictValueType")
"""A type variable for a graph's dictionary values."""


@export
class Vertex(
	Generic[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType],
	metaclass=ExtendedType, useSlots=True
):
	"""
	A **vertex** can have a unique ID, a value and attached meta information as key-value-pairs. A vertex has references
	to inbound and outbound edges, thus a graph can be traversed in reverse.
	"""
	_graph:     'Graph[VertexIDType, EdgeIDType]'
	_component: 'Component'
	_inbound:   List['Edge']
	_outbound:  List['Edge']

	_id:        Nullable[VertexIDType]
	_value:     Nullable[VertexValueType]
	_dict:      Dict[VertexDictKeyType, VertexDictValueType]

	def __init__(self, vertexID: VertexIDType = None, value: VertexValueType = None, component: 'Component' = None, graph: 'Graph' = None):
		""".. todo:: GRAPH::Vertex::init Needs documentation."""
		if component is None:
			self._graph = graph if graph is not None else Graph()
			self._component = Component(self._graph, vertices=(self,))
		else:
			self._graph = component._graph
			self._component = component

		self._id = vertexID
		if vertexID is None:
			self._graph._verticesWithoutID.append(self)
		elif vertexID in self._graph._verticesWithID:
			raise ValueError(f"ID '{vertexID}' already exists in this graph.")
		else:
			self._graph._verticesWithID[vertexID] = self

		self._inbound = []
		self._outbound = []

		self._value = value
		self._dict = {}

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
		"""
		Read a vertex's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: VertexDictKeyType, value: VertexDictValueType) -> None:
		"""
		Create or update a vertex's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key: The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: VertexDictKeyType) -> None:
		""".. todo:: GRAPH::Vertex::__delitem__ Needs documentation."""
		del self._dict[key]

	def __len__(self) -> int:
		"""
		Returns the number of outbound directed edges.

		:returns: Number of outbound edges.
		"""
		return len(self._outbound)

	@property
	def Graph(self) -> 'Graph':
		"""
		Read-only property to access the graph, this vertex is associated to (:py:attr:`_graph`).

		:returns: The graph this vertex is associated to.
		"""
		return self._graph

	@property
	def Component(self) -> 'Component':
		"""
		Read-only property to access the component, this vertex is associated to (:py:attr:`_component`).

		:returns: The component this vertex is associated to.
		"""
		return self._component

	def LinkToVertex(self, vertex: 'Vertex', edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> None:
		# TODO: set edgeID
		edge = Edge(self, vertex, edgeID, edgeWeight, edgeValue)

		self._outbound.append(edge)
		vertex._inbound.append(edge)

		# TODO: move into Edge?
		# TODO: keep _graph pointer in edge and then register edge on graph?
		if edgeID is None:
			self._graph._edgesWithoutID.append(edge)
		elif edgeID not in self._graph._edgesWithID:
			self._graph._edgesWithID[edgeID] = edge
		else:
			raise Exception()

	def LinkFromVertex(self, vertex: 'Vertex', edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> None:
		edge = Edge(vertex, self, edgeID, edgeWeight, edgeValue)

		vertex._outbound.append(edge)
		self._inbound.append(edge)

		# TODO: move into Edge?
		# TODO: keep _graph pointer in edge and then register edge on graph?
		if edgeID is None:
			self._graph._edgesWithoutID.append(edge)
		elif edgeID not in self._graph._edgesWithID:
			self._graph._edgesWithID[edgeID] = edge
		else:
			raise Exception()

	def LinkToNewVertex(self, vertexID: VertexIDType = None, vertexValue: VertexValueType = None, edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> 'Vertex':
		vertex = Vertex(vertexID, vertexValue, component=self._component)

		edge = Edge(self, vertex, edgeID, edgeWeight, edgeValue)

		self._outbound.append(edge)
		vertex._inbound.append(edge)

		# TODO: move into Edge?
		# TODO: keep _graph pointer in edge and then register edge on graph?
		if edgeID is None:
			self._graph._edgesWithoutID.append(edge)
		elif edgeID not in self._graph._edgesWithID:
			self._graph._edgesWithID[edgeID] = edge
		else:
			raise Exception()

		return vertex

	def LinkFromNewVertex(self, vertexID: VertexIDType = None, vertexValue: VertexValueType = None, edgeID: EdgeIDType = None, edgeWeight: EdgeWeightType = None, edgeValue: VertexValueType = None) -> 'Vertex':
		vertex = Vertex(vertexID, vertexValue, component=self._component)

		edge = Edge(vertex, self, edgeID, edgeWeight, edgeValue)

		vertex._outbound.append(edge)
		self._inbound.append(edge)

		# TODO: move into Edge?
		# TODO: keep _graph pointer in edge and then register edge on graph?
		if edgeID is None:
			self._graph._edgesWithoutID.append(edge)
		elif edgeID not in self._graph._edgesWithID:
			self._graph._edgesWithID[edgeID] = edge
		else:
			raise Exception()

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

	def IterateSuccessorVertices(self):
		for edge in self._outbound:
			yield edge.Destination

	def IteratePredecessorVertices(self):
		for edge in self._inbound:
			yield edge.Source

	def IterateVerticesBFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertices starting from this node in breadth-first search (BFS) order.

		:returns: A generator to iterate vertices traversed in BFS order.

		.. seealso::

		   :py:meth:`IterateVerticesDFS` |br|
		      |rarr| Iterate all reachable vertices **depth-first search** order.
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

	def IterateVerticesDFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertices starting from this node in depth-first search (DFS) order.

		:returns: A generator to iterate vertices traversed in DFS order.

		.. seealso::

		   :py:meth:`IterateVerticesBFS` |br|
		      |rarr| Iterate all reachable vertices **breadth-first search** order.

		   Wikipedia - https://en.wikipedia.org/wiki/Depth-first_search
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

		# Initially add all reachable vertices to a queue if vertices to be processed.
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
			# Process queue until destination is found or no further vertices are reachable.
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
				# All reachable vertices have been processed, but destination was not among them.
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

		# Scan reversed linked-list and yield referenced vertices
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
			# Process priority queue until destination is found or no further vertices are reachable.
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
				# All reachable vertices have been processed, but destination was not among them.
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

		# Scan reversed linked-list and yield referenced vertices
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
class Edge(
	Generic[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType],
	metaclass=ExtendedType, useSlots=True
):
	"""
	An **edge** can have a unique ID, a value, a weight and attached meta information as key-value-pairs. All edges are
	directed.
	"""
	_id:          Nullable[EdgeIDType]
	_source:      Vertex
	_destination: Vertex
	_weight:      Nullable[EdgeWeightType]
	_value:       Nullable[EdgeValueType]
	_dict:        Dict[EdgeDictKeyType, EdgeDictValueType]

	def __init__(
		self,
		source: Vertex,
		destination: Vertex,
		edgeID: EdgeIDType = None,
		weight: EdgeWeightType = None,
		value: EdgeValueType = None
	):
		""".. todo:: GRAPH::Edge::init Needs documentation."""
		if not isinstance(source, Vertex):
			raise TypeError("Parameter 'source' is not of type 'Vertex'.")
		if not isinstance(destination, Vertex):
			raise TypeError("Parameter 'destination' is not of type 'Vertex'.")
		if edgeID is not None and not isinstance(edgeID, Hashable):
			raise TypeError("Parameter 'edgeID' is not of type 'EdgeIDType'.")
		if weight is not None and  not isinstance(weight, (int, float)):
			raise TypeError("Parameter 'weight' is not of type 'EdgeWeightType'.")
		# if value is not None and  not isinstance(value, Vertex):
		# 	raise TypeError("Parameter 'value' is not of type 'EdgeValueType'.")
		if source._graph is not destination._graph:
			raise Exception(f"Source vertex and destination vertex are not in same graph.")

		if source._component is not destination._component:
			# TODO: should it be divided into with/without ID?
			for vertex in destination._component._vertices:
				component = source._component
				component._vertices.add(vertex)
				vertex._component = component

		self._id = edgeID
		self._source = source
		self._destination = destination
		self._weight = weight
		self._value = value
		self._dict = {}

	@property
	def ID(self) -> Nullable[EdgeIDType]:
		"""
		Read-only property to access the unique ID of an edge (:py:attr:`_id`).

		If no ID was given at edge construction time, ID return None.

		:returns: Unique ID of an edge, if ID was given at edge creation time, else None.
		"""
		return self._id

	@property
	def Source(self) -> Vertex:
		"""
		Read-only property to get the source (:py:attr:`_source`) of an edge.

		:returns: The source of an edge.
		"""
		return self._source

	@property
	def Destination(self) -> Vertex:
		"""
		Read-only property to get the destination (:py:attr:`_destination`) of an edge.

		:returns: The destination of an edge.
		"""
		return self._destination

	@property
	def Weight(self) -> Nullable[EdgeWeightType]:
		"""
		Property to get and set the weight (:py:attr:`_weight`) of an edge.

		:returns: The weight of an edge.
		"""
		return self._weight

	@Weight.setter
	def Weight(self, value: Nullable[EdgeWeightType]) -> None:
		self._weight = value

	@property
	def Value(self) -> Nullable[VertexValueType]:
		"""
		Property to get and set the value (:py:attr:`_value`) of an edge.

		:returns: The value of an edge.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Nullable[VertexValueType]) -> None:
		self._value = value

	def __getitem__(self, key: VertexDictKeyType) -> VertexDictValueType:
		"""
		Read an edge's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: VertexDictKeyType, value: VertexDictValueType) -> None:
		"""
		Create or update an edge's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key: The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: VertexDictKeyType) -> None:
		""".. todo:: GRAPH::Edge::__delitem__ Needs documentation."""
		del self._dict[key]


@export
class Component(
	Generic[
		ComponentDictKeyType, ComponentDictValueType,
		VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType
	],
	metaclass=ExtendedType, useSlots=True
):
	_graph:    'Graph'
	_name:     str
	_vertices: Set[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]
	_dict:     Dict[ComponentDictKeyType, ComponentDictValueType]

	def __init__(self, graph: 'Graph', name: str = None, vertices: Iterable[Vertex] = None):
		""".. todo:: GRAPH::Graph::init Needs documentation."""
		if graph is None:
			raise ValueError("Parameter 'graph' is None.")
		if not isinstance(graph, Graph):
			raise TypeError("Parameter 'graph' is not of type 'Graph'.")
		if name is not None and not isinstance(name, str):
			raise TypeError("Parameter 'name' is not of type 'str'.")

		graph._components.add(self)

		self._graph = graph
		self._name = name
		self._vertices = set() if vertices is None else {v for v in vertices}
		self._dict = {}

	@property
	def Graph(self) -> 'Graph':
		"""
		Read-only property to access the graph, this component is associated to (:py:attr:`_graph`).

		:returns: The graph this component is associated to.
		"""
		return self._graph

	@property
	def Name(self) -> str:
		"""
		Property to get and set the name (:py:attr:`_name`) of the component.

		:returns: The value of a component.
		"""
		return self._name

	@Name.setter
	def Name(self, value: str) -> None:
		if not isinstance(value, str):
			raise TypeError()

		self._name = value

	@property
	def Vertices(self) -> Set[Vertex]:
		"""
		Read-only property to access the vertices in this component (:py:attr:`_vertices`).

		:returns: The set of vertices in this component.
		"""
		return self._vertices

	def __getitem__(self, key: ComponentDictKeyType) -> ComponentDictValueType:
		"""
		Read a component's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: ComponentDictKeyType, value: ComponentDictValueType) -> None:
		"""
		Create or update a component's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key: The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: ComponentDictKeyType) -> None:
		""".. todo:: GRAPH::Component::__delitem__ Needs documentation."""
		del self._dict[key]

	def __len__(self) -> int:
		"""
		Returns the number of vertices in this component.

		:returns: Number of vertices.
		"""
		return len(self._vertices)

	def __str__(self):
		return self._name if self._name is not None else "Unnamed component"


@export
class Graph(
	Generic[
		GraphDictKeyType, GraphDictValueType,
		ComponentDictKeyType, ComponentDictValueType,
		VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType
	],
	metaclass=ExtendedType, useSlots=True
):
	"""
	A **graph** data structure is represented by an instance of :py:class:`~pyTooling.Graph.Graph` holding references to
	all nodes. Nodes are instances of :py:class:`~pyTooling.Graph.Vertex` classes and directed links between nodes are
	made of :py:class:`~pyTooling.Graph.Edge` instances. A graph can have attached meta information as key-value-pairs.
	"""
	_name:              str
	_components:        Set[Component[ComponentDictKeyType, ComponentDictValueType, VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]
	_verticesWithID:    Dict[VertexIDType, Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]
	_verticesWithoutID: List[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]
	_edgesWithID:       Dict[EdgeIDType, Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]]
	_edgesWithoutID:    List[Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]]
	_dict:              Dict[GraphDictKeyType, GraphDictValueType]

	def __init__(self, name: str = None):
		""".. todo:: GRAPH::Graph::init Needs documentation."""
		self._name = name
		self._components = set()
		self._verticesWithID = {}
		self._verticesWithoutID = []
		self._edgesWithID = {}
		self._edgesWithoutID = []
		self._dict = {}

	@property
	def Name(self) -> str:
		"""
		Property to get and set the name (:py:attr:`_name`) of the graph.

		:returns: The value of a graph.
		"""
		return self._name

	@Name.setter
	def Name(self, value: str) -> None:
		if not isinstance(value, str):
			raise TypeError()

		self._name = value

	@property
	def Components(self) -> Set[Component]:
		"""Read-only property to access the components of this graph (:py:attr:`_components`).

		:returns: The set of components in this graph."""
		return self._components

	def __getitem__(self, key: GraphDictKeyType) -> GraphDictValueType:
		"""
		Read a graph's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: GraphDictKeyType, value: GraphDictValueType) -> None:
		"""
		Create or update a graph's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key: The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: GraphDictKeyType) -> None:
		""".. todo:: GRAPH::Graph::__delitem__ Needs documentation."""
		del self._dict[key]

	def __len__(self) -> int:
		"""
		Returns the number of vertices in this graph.

		:returns: Number of vertices.
		"""
		return len(self._verticesWithoutID) + len(self._verticesWithID)

	def __iter__(self) -> Iterator[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType]]:
		def gen():
			yield from self._verticesWithoutID
			yield from self._verticesWithID
		return iter(gen())

	def IterateRoots(self) -> Generator[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType], None, None]:
		"""
		Iterate all roots (vertices without inbound edges / without predecessors) of a graph.

		:return: A generator to iterate vertices without inbound edges.

		.. seealso::

		   :py:meth:`IterateLeafs` |br|
		      |rarr| Iterate leafs of a graph.
		"""
		for vertex in self._verticesWithID.values():
			if len(vertex._inbound) == 0:
				yield vertex

		for vertex in self._verticesWithoutID:
			if len(vertex._inbound) == 0:
				yield vertex

	def IterateLeafs(self) -> Generator[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType], None, None]:
		"""
		Iterate all leafs (vertices without outbound edges / without successors) of a graph.

		:return: A generator to iterate vertices without outbound edges.

		.. seealso::

		   :py:meth:`IterateRoots` |br|
		      |rarr| Iterate roots of a graph.
		"""
		for vertex in self._verticesWithID.values():
			if len(vertex._outbound) == 0:
				yield vertex

		for vertex in self._verticesWithoutID:
			if len(vertex._outbound) == 0:
				yield vertex

	def IterateTopologically(self) -> Generator[Vertex[VertexIDType, VertexValueType, VertexDictKeyType, VertexDictValueType], None, None]:
		"""
		Iterate all vertices in topological order.

		:return:           A generator to iterate vertices in topological order.
		:except Exception: Raised if graph is cyclic, thus topological sorting isn't possible.
		"""
		outboundEdgeCounts = {}
		leafVertices = []

		for vertex in self._verticesWithID.values():
			count = len(vertex._outbound)
			if count == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count
		for vertex in self._verticesWithoutID:
			count = len(vertex._outbound)
			if count == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		if not leafVertices:
			raise Exception(f"Graph has no leafs. Thus, no topological sorting exists.")

		overallCount = len(outboundEdgeCounts) + len(leafVertices)

		for vertex in leafVertices:
			yield vertex
			overallCount -= 1
			for inboundEdge in vertex._inbound:
				sourceVertex = inboundEdge.Source
				count = outboundEdgeCounts[sourceVertex] - 1
				outboundEdgeCounts[sourceVertex] = count
				if count == 0:
					leafVertices.append(sourceVertex)

		if overallCount == 0:
			return
		elif overallCount > 0:
			raise Exception(f"Graph has remaining vertices. Thus, the graph has at least one cycle.")

		raise Exception(f"Graph data structure is corrupted.")  # pragma: no cover

	def HasCycle(self) -> bool:
		# IsAcyclic ?

		# Handle trivial case if graph is empty
		if len(self._verticesWithID) + len(self._verticesWithoutID) == 0:
			return False

		outboundEdgeCounts = {}
		leafVertices = []

		for vertex in self._verticesWithID.values():
			count = len(vertex._outbound)
			if count == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count
		for vertex in self._verticesWithoutID:
			count = len(vertex._outbound)
			if count == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		# If there are no leafs, then each vertex has at least one inbound and one outbound edges. Thus, there is a cycle.
		if not leafVertices:
			return True

		overallCount = len(outboundEdgeCounts) + len(leafVertices)

		for vertex in leafVertices:
			overallCount -= 1
			for inboundEdge in vertex._inbound:
				sourceVertex = inboundEdge.Source
				count = outboundEdgeCounts[sourceVertex] - 1
				outboundEdgeCounts[sourceVertex] = count
				if count == 0:
					leafVertices.append(sourceVertex)

		# If all vertices were processed, no cycle exists.
		if overallCount == 0:
			return False
		# If there are remaining vertices, then a cycle exists.
		elif overallCount > 0:
			return True

		raise Exception(f"Graph data structure is corrupted.")  # pragma: no cover

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
