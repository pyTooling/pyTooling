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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. admonition:: Example Graph

	.. mermaid::
		 :caption: A directed graph with backward-edges denoted by dotted vertex relations.

		 %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
		 graph LR
			 A(A); B(B); C(C); D(D); E(E); F(F) ; G(G); H(H); I(I)

			 A --> B --> E
			 G --> F
			 A --> C --> G --> H --> D
			 D -.-> A
			 D & F -.-> B
			 I ---> E --> F --> D

			 classDef node fill:#eee,stroke:#777,font-size:smaller;
"""
import heapq
from collections import deque
from itertools   import chain
from sys         import version_info           # needed for versions before Python 3.11
from typing      import TypeVar, Generic, List, Tuple, Dict, Set, Deque, Union, Optional as Nullable
from typing      import Callable, Iterator as typing_Iterator, Generator, Iterable, Mapping, Hashable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName
	from pyTooling.Tree        import Node
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Graph] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, mixin
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName
		from Tree                import Node
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Graph] Could not import directly!")
		raise ex


DictKeyType = TypeVar("DictKeyType", bound=Hashable)
"""A type variable for dictionary keys."""

DictValueType = TypeVar("DictValueType")
"""A type variable for dictionary values."""

IDType = TypeVar("IDType", bound=Hashable)
"""A type variable for an ID."""

WeightType = TypeVar("WeightType", bound=Union[int, float])
"""A type variable for a weight."""

ValueType = TypeVar("ValueType")
"""A type variable for a value."""

VertexIDType = TypeVar("VertexIDType", bound=Hashable)
"""A type variable for a vertex's ID."""

VertexWeightType = TypeVar("VertexWeightType", bound=Union[int, float])
"""A type variable for a vertex's weight."""

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

LinkIDType = TypeVar("LinkIDType", bound=Hashable)
"""A type variable for an link's ID."""

LinkWeightType = TypeVar("LinkWeightType", bound=Union[int, float])
"""A type variable for an link's weight."""

LinkValueType = TypeVar("LinkValueType")
"""A type variable for an link's value."""

LinkDictKeyType = TypeVar("LinkDictKeyType", bound=Hashable)
"""A type variable for an link's dictionary keys."""

LinkDictValueType = TypeVar("LinkDictValueType")
"""A type variable for an link's dictionary values."""

ComponentDictKeyType = TypeVar("ComponentDictKeyType", bound=Hashable)
"""A type variable for a component's dictionary keys."""

ComponentDictValueType = TypeVar("ComponentDictValueType")
"""A type variable for a component's dictionary values."""

SubgraphDictKeyType = TypeVar("SubgraphDictKeyType", bound=Hashable)
"""A type variable for a component's dictionary keys."""

SubgraphDictValueType = TypeVar("SubgraphDictValueType")
"""A type variable for a component's dictionary values."""

ViewDictKeyType = TypeVar("ViewDictKeyType", bound=Hashable)
"""A type variable for a component's dictionary keys."""

ViewDictValueType = TypeVar("ViewDictValueType")
"""A type variable for a component's dictionary values."""

GraphDictKeyType = TypeVar("GraphDictKeyType", bound=Hashable)
"""A type variable for a graph's dictionary keys."""

GraphDictValueType = TypeVar("GraphDictValueType")
"""A type variable for a graph's dictionary values."""


@export
class GraphException(ToolingException):
	"""Base exception of all exceptions raised by :mod:`pyTooling.Graph`."""


@export
class InternalError(GraphException):
	"""
	The exception is raised when a data structure corruption is detected.

	.. danger::

	   This exception should never be raised.

	   If so, please create an issue at GitHub so the data structure corruption can be investigated and fixed. |br|
	   `⇒ Bug Tracker at GitHub <https://github.com/pyTooling/pyTooling/issues>`__
	"""


@export
class NotInSameGraph(GraphException):
	"""The exception is raised when creating an edge between two vertices, but these are not in the same graph."""


@export
class DuplicateVertexError(GraphException):
	"""The exception is raised when the vertex already exists in the graph."""


@export
class DuplicateEdgeError(GraphException):
	"""The exception is raised when the edge already exists in the graph."""


@export
class DestinationNotReachable(GraphException):
	"""The exception is raised when a destination vertex is not reachable."""


@export
class NotATreeError(GraphException):
	"""
	The exception is raised when a subgraph is not a tree.

	Either the subgraph has a cycle (backward edge) or links between branches (cross-edge).
	"""


@export
class CycleError(GraphException):
	"""The exception is raised when a not permitted cycle is found."""


@export
class Base(
	Generic[DictKeyType, DictValueType],
	metaclass=ExtendedType, slots=True
):
	_dict: Dict[DictKeyType, DictValueType]  #: A dictionary to store arbitrary key-value-pairs.

	def __init__(
		self,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Base::init Needs documentation.

		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		self._dict = {key: value for key, value in keyValuePairs.items()} if keyValuePairs is not None else {}

	def __del__(self):
		"""
		.. todo:: GRAPH::Base::del Needs documentation.

		"""
		try:
			del self._dict
		except AttributeError:
			pass

	def Delete(self) -> None:
		self._dict = None

	def __getitem__(self, key: DictKeyType) -> DictValueType:
		"""
		Read a vertex's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: DictKeyType, value: DictValueType) -> None:
		"""
		Create or update a vertex's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key: The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: DictKeyType) -> None:
		"""
		Remove an entry from vertex's attached attributes (key-value-pairs) by key.

		:param key:       The key to remove.
		:raises KeyError: If key doesn't exist in the vertex's attributes.
		"""
		del self._dict[key]

	def __contains__(self, key: DictKeyType) -> bool:
		"""
		Returns if the key is an attached attribute (key-value-pairs) on this vertex.

		:param key: The key to check.
		:returns:   ``True``, if the key is an attached attribute.
		"""
		return key in self._dict

	def __len__(self) -> int:
		"""
		Returns the number of attached attributes (key-value-pairs) on this vertex.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)


@export
class BaseWithIDValueAndWeight(
	Base[DictKeyType, DictValueType],
	Generic[IDType, ValueType, WeightType, DictKeyType, DictValueType]
):
	_id:        Nullable[IDType]      #: Field storing the object's Identifier.
	_value:     Nullable[ValueType]   #: Field storing the object's value of any type.
	_weight:    Nullable[WeightType]  #: Field storing the object's weight.

	def __init__(
		self,
		identifier: Nullable[IDType] = None,
		value: Nullable[ValueType] = None,
		weight: Nullable[WeightType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Vertex::init Needs documentation.

		:param identifier:    The optional unique ID.
		:param value:         The optional value.
		:param weight:        The optional weight.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		super().__init__(keyValuePairs)

		self._id = identifier
		self._value = value
		self._weight = weight

	@readonly
	def ID(self) -> Nullable[IDType]:
		"""
		Read-only property to access the unique ID (:attr:`_id`).

		If no ID was given at creation time, ID returns ``None``.

		:returns: Unique ID, if ID was given at creation time, else ``None``.
		"""
		return self._id

	@property
	def Value(self) -> ValueType:
		"""
		Property to get and set the value (:attr:`_value`).

		:returns: The value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: ValueType) -> None:
		self._value = value

	@property
	def Weight(self) -> Nullable[EdgeWeightType]:
		"""
		Property to get and set the weight (:attr:`_weight`) of an edge.

		:returns: The weight of an edge.
		"""
		return self._weight

	@Weight.setter
	def Weight(self, value: Nullable[EdgeWeightType]) -> None:
		self._weight = value


@export
class BaseWithName(
	Base[DictKeyType, DictValueType],
	Generic[DictKeyType, DictValueType]
):
	_name: Nullable[str]  #: Field storing the object's name.

	def __init__(
		self,
		name: Nullable[str] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
	) -> None:
		"""
		.. todo:: GRAPH::BaseWithName::init Needs documentation.

		:param name:          The optional name.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		if name is not None and not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		super().__init__(keyValuePairs)

		self._name = name

	@property
	def Name(self) -> Nullable[str]:
		"""
		Property to get and set the name (:attr:`_name`).

		:returns: The value of a component.
		"""
		return self._name

	@Name.setter
	def Name(self, value: str) -> None:
		if not isinstance(value, str):
			ex = TypeError("Name is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._name = value


@export
class BaseWithVertices(
	BaseWithName[DictKeyType, DictValueType],
	Generic[
		DictKeyType, DictValueType,
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	_graph:    'Graph[GraphDictKeyType, GraphDictValueType,' \
								'VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,' \
								'EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,' \
								'LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType' \
								']'   #: Field storing a reference to the graph.
	_vertices: Set['Vertex[GraphDictKeyType, GraphDictValueType,'
								'VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,'
								'EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,'
								'LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType'
								']']  #: Field storing a set of vertices.

	def __init__(
		self,
		graph: 'Graph',
		name: Nullable[str] = None,
		vertices: Nullable[Iterable['Vertex']] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Component::init Needs documentation.

		:param graph:         The reference to the graph.
		:param name:          The optional name.
		:param vertices:      The optional list of vertices.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		if graph is None:
			raise ValueError("Parameter 'graph' is None.")
		elif not isinstance(graph, Graph):
			ex = TypeError("Parameter 'graph' is not of type 'Graph'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(graph)}'.")
			raise ex

		super().__init__(name, keyValuePairs)

		self._graph = graph
		self._vertices = set() if vertices is None else {v for v in vertices}

	def __del__(self):
		"""
		.. todo:: GRAPH::BaseWithVertices::del Needs documentation.

		"""
		try:
			del self._vertices
		except AttributeError:
			pass

		super().__del__()

	@readonly
	def Graph(self) -> 'Graph':
		"""
		Read-only property to access the graph, this object is associated to (:attr:`_graph`).

		:returns: The graph this object is associated to.
		"""
		return self._graph

	@readonly
	def Vertices(self) -> Set['Vertex']:
		"""
		Read-only property to access the vertices in this component (:attr:`_vertices`).

		:returns: The set of vertices in this component.
		"""
		return self._vertices

	@readonly
	def VertexCount(self) -> int:
		"""
		Read-only property to access the number of vertices referenced by this object.

		:returns: The number of vertices this object references.
		"""
		return len(self._vertices)


@export
class Vertex(
	BaseWithIDValueAndWeight[VertexIDType, VertexValueType, VertexWeightType, VertexDictKeyType, VertexDictValueType],
	Generic[
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	A **vertex** can have a unique ID, a value and attached meta information as key-value-pairs. A vertex has references
	to inbound and outbound edges, thus a graph can be traversed in reverse.
	"""
	_graph:     'BaseGraph[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]'  #: Field storing a reference to the graph.
	_subgraph:  'Subgraph[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]'   #: Field storing a reference to the subgraph.
	_component: 'Component'
	_views:     Dict[Hashable, 'View']
	_inboundEdges:   List['Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]']  #: Field storing a list of inbound edges.
	_outboundEdges:  List['Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]']  #: Field storing a list of outbound edges.
	_inboundLinks:   List['Link[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]']  #: Field storing a list of inbound links.
	_outboundLinks:  List['Link[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]']  #: Field storing a list of outbound links.

	def __init__(
		self,
		vertexID: Nullable[VertexIDType] = None,
		value: Nullable[VertexValueType] = None,
		weight: Nullable[VertexWeightType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
		graph: Nullable['Graph'] = None,
		subgraph: Nullable['Subgraph'] = None
	) -> None:
		"""
		.. todo:: GRAPH::Vertex::init Needs documentation.

		:param vertexID:      The optional ID for the new vertex.
		:param value:         The optional value for the new vertex.
		:param weight:        The optional weight for the new vertex.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		:param graph:         The optional reference to the graph.
		:param subgraph:      undocumented
		"""
		if vertexID is not None and not isinstance(vertexID, Hashable):
			ex = TypeError("Parameter 'vertexID' is not of type 'VertexIDType'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(vertexID)}'.")
			raise ex

		super().__init__(vertexID, value, weight, keyValuePairs)

		if subgraph is None:
			self._graph = graph if graph is not None else Graph()
			self._subgraph = None
			self._component = Component(self._graph, vertices=(self,))

			if vertexID is None:
				self._graph._verticesWithoutID.append(self)
			elif vertexID not in self._graph._verticesWithID:
				self._graph._verticesWithID[vertexID] = self
			else:
				raise DuplicateVertexError(f"Vertex ID '{vertexID}' already exists in this graph.")
		else:
			self._graph = subgraph._graph
			self._subgraph = subgraph
			self._component = Component(self._graph, vertices=(self,))

			if vertexID is None:
				subgraph._verticesWithoutID.append(self)
			elif vertexID not in subgraph._verticesWithID:
				subgraph._verticesWithID[vertexID] = self
			else:
				raise DuplicateVertexError(f"Vertex ID '{vertexID}' already exists in this subgraph.")

		self._views =         {}
		self._inboundEdges =  []
		self._outboundEdges = []
		self._inboundLinks =  []
		self._outboundLinks = []

	def __del__(self):
		"""
		.. todo:: GRAPH::BaseEdge::del Needs documentation.

		"""
		try:
			del self._views
			del self._inboundEdges
			del self._outboundEdges
			del self._inboundLinks
			del self._outboundLinks
		except AttributeError:
			pass

		super().__del__()

	def Delete(self) -> None:
		for edge in self._outboundEdges:
			edge._destination._inboundEdges.remove(edge)
			edge._Delete()
		for edge in self._inboundEdges:
			edge._source._outboundEdges.remove(edge)
			edge._Delete()
		for link in self._outboundLinks:
			link._destination._inboundLinks.remove(link)
			link._Delete()
		for link in self._inboundLinks:
			link._source._outboundLinks.remove(link)
			link._Delete()

		if self._id is None:
			self._graph._verticesWithoutID.remove(self)
		else:
			del self._graph._verticesWithID[self._id]

		# subgraph

		# component

		# views
		self._views =         None
		self._inboundEdges =  None
		self._outboundEdges = None
		self._inboundLinks =  None
		self._outboundLinks = None

		super().Delete()
		assert getrefcount(self) == 1

	@readonly
	def Graph(self) -> 'Graph':
		"""
		Read-only property to access the graph, this vertex is associated to (:attr:`_graph`).

		:returns: The graph this vertex is associated to.
		"""
		return self._graph

	@readonly
	def Component(self) -> 'Component':
		"""
		Read-only property to access the component, this vertex is associated to (:attr:`_component`).

		:returns: The component this vertex is associated to.
		"""
		return self._component

	@readonly
	def InboundEdges(self) -> Tuple['Edge', ...]:
		"""
		Read-only property to get a tuple of inbound edges (:attr:`_inboundEdges`).

		:returns: Tuple of inbound edges.
		"""
		return tuple(self._inboundEdges)

	@readonly
	def OutboundEdges(self) -> Tuple['Edge', ...]:
		"""
		Read-only property to get a tuple of outbound edges (:attr:`_outboundEdges`).

		:returns: Tuple of outbound edges.
		"""
		return tuple(self._outboundEdges)

	@readonly
	def InboundLinks(self) -> Tuple['Link', ...]:
		"""
		Read-only property to get a tuple of inbound links (:attr:`_inboundLinks`).

		:returns: Tuple of inbound links.
		"""
		return tuple(self._inboundLinks)

	@readonly
	def OutboundLinks(self) -> Tuple['Link', ...]:
		"""
		Read-only property to get a tuple of outbound links (:attr:`_outboundLinks`).

		:returns: Tuple of outbound links.
		"""
		return tuple(self._outboundLinks)

	@readonly
	def EdgeCount(self) -> int:
		"""
		Read-only property to get the number of all edges (inbound and outbound).

		:returns: Number of inbound and outbound edges.
		"""
		return len(self._inboundEdges) + len(self._outboundEdges)

	@readonly
	def InboundEdgeCount(self) -> int:
		"""
		Read-only property to get the number of inbound edges.

		:returns: Number of inbound edges.
		"""
		return len(self._inboundEdges)

	@readonly
	def OutboundEdgeCount(self) -> int:
		"""
		Read-only property to get the number of outbound edges.

		:returns: Number of outbound edges.
		"""
		return len(self._outboundEdges)

	@readonly
	def LinkCount(self) -> int:
		"""
		Read-only property to get the number of all links (inbound and outbound).

		:returns: Number of inbound and outbound links.
		"""
		return len(self._inboundLinks) + len(self._outboundLinks)

	@readonly
	def InboundLinkCount(self) -> int:
		"""
		Read-only property to get the number of inbound links.

		:returns: Number of inbound links.
		"""
		return len(self._inboundLinks)

	@readonly
	def OutboundLinkCount(self) -> int:
		"""
		Read-only property to get the number of outbound links.

		:returns: Number of outbound links.
		"""
		return len(self._outboundLinks)

	@readonly
	def IsRoot(self) -> bool:
		"""
		Read-only property to check if this vertex is a root vertex in the graph.

		A root has no inbound edges (no predecessor vertices).

		:returns: ``True``, if this vertex is a root.

		.. seealso::

		   :meth:`IsLeaf` |br|
		      |rarr| Check if a vertex is a leaf vertex in the graph.
		   :meth:`Graph.IterateRoots <pyTooling.Graph.Graph.IterateRoots>` |br|
		      |rarr| Iterate all roots of a graph.
		   :meth:`Graph.IterateLeafs <pyTooling.Graph.Graph.IterateLeafs>` |br|
		      |rarr| Iterate all leafs of a graph.
		"""
		return len(self._inboundEdges) == 0

	@readonly
	def IsLeaf(self) -> bool:
		"""
		Read-only property to check if this vertex is a leaf vertex in the graph.

		A leaf has no outbound edges (no successor vertices).

		:returns: ``True``, if this vertex is a leaf.

		.. seealso::

		   :meth:`IsRoot` |br|
		      |rarr| Check if a vertex is a root vertex in the graph.
		   :meth:`Graph.IterateRoots <pyTooling.Graph.Graph.IterateRoots>` |br|
		      |rarr| Iterate all roots of a graph.
		   :meth:`Graph.IterateLeafs <pyTooling.Graph.Graph.IterateLeafs>` |br|
		      |rarr| Iterate all leafs of a graph.
		"""
		return len(self._outboundEdges) == 0

	@readonly
	def Predecessors(self) -> Tuple['Vertex', ...]:
		"""
		Read-only property to get a tuple of predecessor vertices.

		:returns: Tuple of predecessor vertices.
		"""
		return tuple([edge.Source for edge in self._inboundEdges])

	@readonly
	def Successors(self) -> Tuple['Vertex', ...]:
		"""
		Read-only property to get a tuple of successor vertices.

		:returns: Tuple of successor vertices.
		"""
		return tuple([edge.Destination for edge in self._outboundEdges])

	def EdgeToVertex(
		self,
		vertex: 'Vertex',
		edgeID: Nullable[EdgeIDType] = None,
		edgeWeight: Nullable[EdgeWeightType] = None,
		edgeValue: Nullable[VertexValueType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> 'Edge':
		"""
		Create an outbound edge from this vertex to the referenced vertex.

		:param vertex:        The vertex to be linked to.
		:param edgeID:        The edge's optional ID for the new edge object.
		:param edgeWeight:    The edge's optional weight for the new edge object.
		:param edgeValue:     The edge's optional value for the new edge object.
		:param keyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new edge object.
		:returns:             The edge object linking this vertex and the referenced vertex.

		.. seealso::

		   :meth:`EdgeFromVertex` |br|
		      |rarr| Create an inbound edge from the referenced vertex to this vertex.
		   :meth:`EdgeToNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an outbound edge from this vertex.
		   :meth:`EdgeFromNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an inbound edge to this vertex.
		   :meth:`LinkToVertex` |br|
		      |rarr| Create an outbound link from this vertex to the referenced vertex.
		   :meth:`LinkFromVertex` |br|
		      |rarr| Create an inbound link from the referenced vertex to this vertex.

		.. todo:: GRAPH::Vertex::EdgeToVertex Needs possible exceptions to be documented.
		"""
		if self._subgraph is vertex._subgraph:
			edge = Edge(self, vertex, edgeID, edgeValue, edgeWeight, keyValuePairs)

			self._outboundEdges.append(edge)
			vertex._inboundEdges.append(edge)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._graph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._graph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._subgraph._edgesWithoutID.append(edge)
				elif edgeID not in self._subgraph._edgesWithID:
					self._subgraph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this subgraph.")
		else:
			# FIXME: needs an error message
			raise GraphException()

		return edge

	def EdgeFromVertex(
		self,
		vertex: 'Vertex',
		edgeID: Nullable[EdgeIDType] = None,
		edgeWeight: Nullable[EdgeWeightType] = None,
		edgeValue: Nullable[VertexValueType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> 'Edge':
		"""
		Create an inbound edge from the referenced vertex to this vertex.

		:param vertex:        The vertex to be linked from.
		:param edgeID:        The edge's optional ID for the new edge object.
		:param edgeWeight:    The edge's optional weight for the new edge object.
		:param edgeValue:     The edge's optional value for the new edge object.
		:param keyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new edge object.
		:returns:             The edge object linking the referenced vertex and this vertex.

		.. seealso::

		   :meth:`EdgeToVertex` |br|
		      |rarr| Create an outbound edge from this vertex to the referenced vertex.
		   :meth:`EdgeToNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an outbound edge from this vertex.
		   :meth:`EdgeFromNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an inbound edge to this vertex.
		   :meth:`LinkToVertex` |br|
		      |rarr| Create an outbound link from this vertex to the referenced vertex.
		   :meth:`LinkFromVertex` |br|
		      |rarr| Create an inbound link from the referenced vertex to this vertex.

		.. todo:: GRAPH::Vertex::EdgeFromVertex Needs possible exceptions to be documented.
		"""
		if self._subgraph is vertex._subgraph:
			edge = Edge(vertex, self, edgeID, edgeValue, edgeWeight, keyValuePairs)

			vertex._outboundEdges.append(edge)
			self._inboundEdges.append(edge)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._graph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._graph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._subgraph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._subgraph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
		else:
			# FIXME: needs an error message
			raise GraphException()

		return edge

	def EdgeToNewVertex(
		self,
		vertexID: Nullable[VertexIDType] = None,
		vertexValue: Nullable[VertexValueType] = None,
		vertexWeight: Nullable[VertexWeightType] = None,
		vertexKeyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
		edgeID: Nullable[EdgeIDType] = None,
		edgeWeight: Nullable[EdgeWeightType] = None,
		edgeValue: Nullable[VertexValueType] = None,
		edgeKeyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> 'Edge':
		"""
		Create a new vertex and link that vertex by an outbound edge from this vertex.

		:param vertexID:            The new vertex' optional ID.
		:param vertexValue:         The new vertex' optional value.
		:param vertexWeight:        The new vertex' optional weight.
		:param vertexKeyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new vertex.
		:param edgeID:              The edge's optional ID for the new edge object.
		:param edgeWeight:          The edge's optional weight for the new edge object.
		:param edgeValue:           The edge's optional value for the new edge object.
		:param edgeKeyValuePairs:   An optional mapping (dictionary) of key-value-pairs for the new edge object.
		:returns:                   The edge object linking this vertex and the created vertex.

		.. seealso::

		   :meth:`EdgeToVertex` |br|
		      |rarr| Create an outbound edge from this vertex to the referenced vertex.
		   :meth:`EdgeFromVertex` |br|
		      |rarr| Create an inbound edge from the referenced vertex to this vertex.
		   :meth:`EdgeFromNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an inbound edge to this vertex.
		   :meth:`LinkToVertex` |br|
		      |rarr| Create an outbound link from this vertex to the referenced vertex.
		   :meth:`LinkFromVertex` |br|
		      |rarr| Create an inbound link from the referenced vertex to this vertex.

		.. todo:: GRAPH::Vertex::EdgeToNewVertex Needs possible exceptions to be documented.
		"""
		vertex = Vertex(vertexID, vertexValue, vertexWeight, vertexKeyValuePairs, graph=self._graph)  # , component=self._component)

		if self._subgraph is vertex._subgraph:
			edge = Edge(self, vertex, edgeID, edgeValue, edgeWeight, edgeKeyValuePairs)

			self._outboundEdges.append(edge)
			vertex._inboundEdges.append(edge)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._graph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._graph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._subgraph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._subgraph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
		else:
			# FIXME: needs an error message
			raise GraphException()

		return edge

	def EdgeFromNewVertex(
		self,
		vertexID: Nullable[VertexIDType] = None,
		vertexValue: Nullable[VertexValueType] = None,
		vertexWeight: Nullable[VertexWeightType] = None,
		vertexKeyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
		edgeID: Nullable[EdgeIDType] = None,
		edgeWeight: Nullable[EdgeWeightType] = None,
		edgeValue: Nullable[VertexValueType] = None,
		edgeKeyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> 'Edge':
		"""
		Create a new vertex and link that vertex by an inbound edge to this vertex.

		:param vertexID:            The new vertex' optional ID.
		:param vertexValue:         The new vertex' optional value.
		:param vertexWeight:        The new vertex' optional weight.
		:param vertexKeyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new vertex.
		:param edgeID:              The edge's optional ID for the new edge object.
		:param edgeWeight:          The edge's optional weight for the new edge object.
		:param edgeValue:           The edge's optional value for the new edge object.
		:param edgeKeyValuePairs:   An optional mapping (dictionary) of key-value-pairs for the new edge object.
		:returns:                   The edge object linking this vertex and the created vertex.

		.. seealso::

		   :meth:`EdgeToVertex` |br|
		      |rarr| Create an outbound edge from this vertex to the referenced vertex.
		   :meth:`EdgeFromVertex` |br|
		      |rarr| Create an inbound edge from the referenced vertex to this vertex.
		   :meth:`EdgeToNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an outbound edge from this vertex.
		   :meth:`LinkToVertex` |br|
		      |rarr| Create an outbound link from this vertex to the referenced vertex.
		   :meth:`LinkFromVertex` |br|
		      |rarr| Create an inbound link from the referenced vertex to this vertex.

		.. todo:: GRAPH::Vertex::EdgeFromNewVertex Needs possible exceptions to be documented.
		"""
		vertex = Vertex(vertexID, vertexValue, vertexWeight, vertexKeyValuePairs, graph=self._graph)  # , component=self._component)

		if self._subgraph is vertex._subgraph:
			edge = Edge(vertex, self, edgeID, edgeValue, edgeWeight, edgeKeyValuePairs)

			vertex._outboundEdges.append(edge)
			self._inboundEdges.append(edge)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._graph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._graph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in edge and then register edge on graph?
				if edgeID is None:
					self._subgraph._edgesWithoutID.append(edge)
				elif edgeID not in self._graph._edgesWithID:
					self._subgraph._edgesWithID[edgeID] = edge
				else:
					raise DuplicateEdgeError(f"Edge ID '{edgeID}' already exists in this graph.")
		else:
			# FIXME: needs an error message
			raise GraphException()

		return edge

	def LinkToVertex(
		self,
		vertex: 'Vertex',
		linkID: Nullable[EdgeIDType] = None,
		linkWeight: Nullable[EdgeWeightType] = None,
		linkValue: Nullable[VertexValueType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
	) -> 'Link':
		"""
		Create an outbound link from this vertex to the referenced vertex.

		:param vertex:        The vertex to be linked to.
		:param edgeID:        The edge's optional ID for the new link object.
		:param edgeWeight:    The edge's optional weight for the new link object.
		:param edgeValue:     The edge's optional value for the new link object.
		:param keyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new link object.
		:returns:             The link object linking this vertex and the referenced vertex.

		.. seealso::

		   :meth:`EdgeToVertex` |br|
		      |rarr| Create an outbound edge from this vertex to the referenced vertex.
		   :meth:`EdgeFromVertex` |br|
		      |rarr| Create an inbound edge from the referenced vertex to this vertex.
		   :meth:`EdgeToNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an outbound edge from this vertex.
		   :meth:`EdgeFromNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an inbound edge to this vertex.
		   :meth:`LinkFromVertex` |br|
		      |rarr| Create an inbound link from the referenced vertex to this vertex.

		.. todo:: GRAPH::Vertex::LinkToVertex Needs possible exceptions to be documented.
		"""
		if self._subgraph is vertex._subgraph:
			# FIXME: needs an error message
			raise GraphException()
		else:
			link = Link(self, vertex, linkID, linkValue, linkWeight, keyValuePairs)

			self._outboundLinks.append(link)
			vertex._inboundLinks.append(link)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in link and then register link on graph?
				if linkID is None:
					self._graph._linksWithoutID.append(link)
				elif linkID not in self._graph._linksWithID:
					self._graph._linksWithID[linkID] = link
				else:
					raise DuplicateEdgeError(f"Link ID '{linkID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in link and then register link on graph?
				if linkID is None:
					self._subgraph._linksWithoutID.append(link)
					vertex._subgraph._linksWithoutID.append(link)
				elif linkID not in self._graph._linksWithID:
					self._subgraph._linksWithID[linkID] = link
					vertex._subgraph._linksWithID[linkID] = link
				else:
					raise DuplicateEdgeError(f"Link ID '{linkID}' already exists in this graph.")

		return link

	def LinkFromVertex(
		self,
		vertex: 'Vertex',
		linkID: Nullable[EdgeIDType] = None,
		linkWeight: Nullable[EdgeWeightType] = None,
		linkValue: Nullable[VertexValueType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> 'Edge':
		"""
		Create an inbound link from the referenced vertex to this vertex.

		:param vertex:        The vertex to be linked from.
		:param edgeID:        The edge's optional ID for the new link object.
		:param edgeWeight:    The edge's optional weight for the new link object.
		:param edgeValue:     The edge's optional value for the new link object.
		:param keyValuePairs: An optional mapping (dictionary) of key-value-pairs for the new link object.
		:returns:             The link object linking the referenced vertex and this vertex.

		.. seealso::

		   :meth:`EdgeToVertex` |br|
		      |rarr| Create an outbound edge from this vertex to the referenced vertex.
		   :meth:`EdgeFromVertex` |br|
		      |rarr| Create an inbound edge from the referenced vertex to this vertex.
		   :meth:`EdgeToNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an outbound edge from this vertex.
		   :meth:`EdgeFromNewVertex` |br|
		      |rarr| Create a new vertex and link that vertex by an inbound edge to this vertex.
		   :meth:`LinkToVertex` |br|
		      |rarr| Create an outbound link from this vertex to the referenced vertex.

		.. todo:: GRAPH::Vertex::LinkFromVertex Needs possible exceptions to be documented.
		"""
		if self._subgraph is vertex._subgraph:
			# FIXME: needs an error message
			raise GraphException()
		else:
			link = Link(vertex, self, linkID, linkValue, linkWeight, keyValuePairs)

			vertex._outboundLinks.append(link)
			self._inboundLinks.append(link)

			if self._subgraph is None:
				# TODO: move into Edge?
				# TODO: keep _graph pointer in link and then register link on graph?
				if linkID is None:
					self._graph._linksWithoutID.append(link)
				elif linkID not in self._graph._linksWithID:
					self._graph._linksWithID[linkID] = link
				else:
					raise DuplicateEdgeError(f"Link ID '{linkID}' already exists in this graph.")
			else:
				# TODO: keep _graph pointer in link and then register link on graph?
				if linkID is None:
					self._subgraph._linksWithoutID.append(link)
					vertex._subgraph._linksWithoutID.append(link)
				elif linkID not in self._graph._linksWithID:
					self._subgraph._linksWithID[linkID] = link
					vertex._subgraph._linksWithID[linkID] = link
				else:
					raise DuplicateEdgeError(f"Link ID '{linkID}' already exists in this graph.")

		return link

	def HasEdgeToDestination(self, destination: 'Vertex') -> bool:
		"""
		Check if this vertex is linked to another vertex by any outbound edge.

		:param destination: Destination vertex to check.
		:returns:           ``True``, if the destination vertex is a destination on any outbound edge.

		.. seealso::

		   :meth:`HasEdgeFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound edge.
		   :meth:`HasLinkToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound link.
		   :meth:`HasLinkFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound link.
		"""
		for edge in self._outboundEdges:
			if destination is edge.Destination:
				return True

		return False

	def HasEdgeFromSource(self, source: 'Vertex') -> bool:
		"""
		Check if this vertex is linked to another vertex by any inbound edge.

		:param source: Source vertex to check.
		:returns:      ``True``, if the source vertex is a source on any inbound edge.

		.. seealso::

		   :meth:`HasEdgeToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound edge.
		   :meth:`HasLinkToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound link.
		   :meth:`HasLinkFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound link.
		"""
		for edge in self._inboundEdges:
			if source is edge.Source:
				return True

		return False

	def HasLinkToDestination(self, destination: 'Vertex') -> bool:
		"""
		Check if this vertex is linked to another vertex by any outbound link.

		:param destination: Destination vertex to check.
		:returns:           ``True``, if the destination vertex is a destination on any outbound link.

		.. seealso::

		   :meth:`HasEdgeToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound edge.
		   :meth:`HasEdgeFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound edge.
		   :meth:`HasLinkFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound link.
		"""
		for link in self._outboundLinks:
			if destination is link.Destination:
				return True

		return False

	def HasLinkFromSource(self, source: 'Vertex') -> bool:
		"""
		Check if this vertex is linked to another vertex by any inbound link.

		:param source: Source vertex to check.
		:returns:      ``True``, if the source vertex is a source on any inbound link.

		.. seealso::

		   :meth:`HasEdgeToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound edge.
		   :meth:`HasEdgeFromSource` |br|
		      |rarr| Check if this vertex is linked to another vertex by any inbound edge.
		   :meth:`HasLinkToDestination` |br|
		      |rarr| Check if this vertex is linked to another vertex by any outbound link.
		"""
		for link in self._inboundLinks:
			if source is link.Source:
				return True

		return False

	def DeleteEdgeTo(self, destination: 'Vertex'):
		for edge in self._outboundEdges:
			if edge._destination is destination:
				break
		else:
			raise GraphException(f"No outbound edge found to '{destination!r}'.")

		edge.Delete()

	def DeleteEdgeFrom(self, source: 'Vertex'):
		for edge in self._inboundEdges:
			if edge._source is source:
				break
		else:
			raise GraphException(f"No inbound edge found to '{source!r}'.")

		edge.Delete()

	def DeleteLinkTo(self, destination: 'Vertex'):
		for link in self._outboundLinks:
			if link._destination is destination:
				break
		else:
			raise GraphException(f"No outbound link found to '{destination!r}'.")

		link.Delete()

	def DeleteLinkFrom(self, source: 'Vertex'):
		for link in self._inboundLinks:
			if link._source is source:
				break
		else:
			raise GraphException(f"No inbound link found to '{source!r}'.")

		link.Delete()

	def Copy(self, graph: Graph, copyDict: bool = False, linkingKeyToOriginalVertex: Nullable[str] = None, linkingKeyFromOriginalVertex: Nullable[str] = None) -> 'Vertex':
		"""
		Creates a copy of this vertex in another graph.

		Optionally, the vertex's attached attributes (key-value-pairs) can be copied and a linkage between both vertices
		can be established.

		:param graph:                        The graph, the vertex is created in.
		:param copyDict:                     If ``True``, copy all attached attributes into the new vertex.
		:param linkingKeyToOriginalVertex:   If not ``None``, add a key-value-pair using this parameter as key from new vertex to the original vertex.
		:param linkingKeyFromOriginalVertex: If not ``None``, add a key-value-pair using this parameter as key from original vertex to the new vertex.
		:returns:                            The newly created vertex.
		:raises GraphException:              If source graph and destination graph are the same.
		"""
		if graph is self._graph:
			raise GraphException("Graph to copy this vertex to, is the same graph.")

		vertex = Vertex(self._id, self._value, self._weight, graph=graph)
		if copyDict:
			vertex._dict = self._dict.copy()

		if linkingKeyToOriginalVertex is not None:
			vertex._dict[linkingKeyToOriginalVertex] = self
		if linkingKeyFromOriginalVertex is not None:
			self._dict[linkingKeyFromOriginalVertex] = vertex

		return vertex

	def IterateOutboundEdges(self, predicate: Nullable[Callable[['Edge'], bool]] = None) -> Generator['Edge', None, None]:
		"""
		Iterate all or selected outbound edges of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip edges in the generator.

		:param predicate: Filter function accepting any edge and returning a boolean.
		:returns:         A generator to iterate all outbound edges.
		"""
		if predicate is None:
			for edge in self._outboundEdges:
				yield edge
		else:
			for edge in self._outboundEdges:
				if predicate(edge):
					yield edge

	def IterateInboundEdges(self, predicate: Nullable[Callable[['Edge'], bool]] = None) -> Generator['Edge', None, None]:
		"""
		Iterate all or selected inbound edges of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip edges in the generator.

		:param predicate: Filter function accepting any edge and returning a boolean.
		:returns:         A generator to iterate all inbound edges.
		"""
		if predicate is None:
			for edge in self._inboundEdges:
				yield edge
		else:
			for edge in self._inboundEdges:
				if predicate(edge):
					yield edge

	def IterateOutboundLinks(self, predicate: Nullable[Callable[['Link'], bool]] = None) -> Generator['Link', None, None]:
		"""
		Iterate all or selected outbound links of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip links in the generator.

		:param predicate: Filter function accepting any link and returning a boolean.
		:returns:         A generator to iterate all outbound links.
		"""
		if predicate is None:
			for link in self._outboundLinks:
				yield link
		else:
			for link in self._outboundLinks:
				if predicate(link):
					yield link

	def IterateInboundLinks(self, predicate: Nullable[Callable[['Link'], bool]] = None) -> Generator['Link', None, None]:
		"""
		Iterate all or selected inbound links of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip links in the generator.

		:param predicate: Filter function accepting any link and returning a boolean.
		:returns:         A generator to iterate all inbound links.
		"""
		if predicate is None:
			for link in self._inboundLinks:
				yield link
		else:
			for link in self._inboundLinks:
				if predicate(link):
					yield link

	def IterateSuccessorVertices(self, predicate: Nullable[Callable[['Edge'], bool]] = None) -> Generator['Vertex', None, None]:
		"""
		Iterate all or selected successor vertices of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip successors in the generator.

		:param predicate: Filter function accepting any edge and returning a boolean.
		:returns:         A generator to iterate all successor vertices.
		"""
		if predicate is None:
			for edge in self._outboundEdges:
				yield edge.Destination
		else:
			for edge in self._outboundEdges:
				if predicate(edge):
					yield edge.Destination

	def IteratePredecessorVertices(self, predicate: Nullable[Callable[['Edge'], bool]] = None) -> Generator['Vertex', None, None]:
		"""
		Iterate all or selected predecessor vertices of this vertex.

		If parameter ``predicate`` is not None, the given filter function is used to skip predecessors in the generator.

		:param predicate: Filter function accepting any edge and returning a boolean.
		:returns:         A generator to iterate all predecessor vertices.
		"""
		if predicate is None:
			for edge in self._inboundEdges:
				yield edge.Source
		else:
			for edge in self._inboundEdges:
				if predicate(edge):
					yield edge.Source

	def IterateVerticesBFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertices starting from this node in breadth-first search (BFS) order.

		:returns: A generator to iterate vertices traversed in BFS order.

		.. seealso::

		   :meth:`IterateVerticesDFS` |br|
		      |rarr| Iterate all reachable vertices **depth-first search** order.
		"""
		visited: Set[Vertex] = set()
		queue: Deque[Vertex] = deque()

		yield self
		visited.add(self)
		for edge in self._outboundEdges:
			nextVertex = edge.Destination
			if nextVertex is not self:
				queue.appendleft(nextVertex)
				visited.add(nextVertex)

		while queue:
			vertex = queue.pop()
			yield vertex
			for edge in vertex._outboundEdges:
				nextVertex = edge.Destination
				if nextVertex not in visited:
					queue.appendleft(nextVertex)
					visited.add(nextVertex)

	def IterateVerticesDFS(self) -> Generator['Vertex', None, None]:
		"""
		A generator to iterate all reachable vertices starting from this node in depth-first search (DFS) order.

		:returns: A generator to iterate vertices traversed in DFS order.

		.. seealso::

		   :meth:`IterateVerticesBFS` |br|
		      |rarr| Iterate all reachable vertices **breadth-first search** order.

		   Wikipedia - https://en.wikipedia.org/wiki/Depth-first_search
		"""
		visited: Set[Vertex] = set()
		stack: List[typing_Iterator[Edge]] = list()

		yield self
		visited.add(self)
		stack.append(iter(self._outboundEdges))

		while True:
			try:
				edge = next(stack[-1])
				nextVertex = edge._destination
				if nextVertex not in visited:
					visited.add(nextVertex)
					yield nextVertex
					if len(nextVertex._outboundEdges) != 0:
						stack.append(iter(nextVertex._outboundEdges))
			except StopIteration:
				stack.pop()

				if len(stack) == 0:
					return

	def IterateAllOutboundPathsAsVertexList(self) -> Generator[Tuple['Vertex', ...], None, None]:
		if len(self._outboundEdges) == 0:
			yield (self, )
			return

		visited:       Set[Vertex] =                 set()
		vertexStack:   List[Vertex] =                list()
		iteratorStack: List[typing_Iterator[Edge]] = list()

		visited.add(self)
		vertexStack.append(self)
		iteratorStack.append(iter(self._outboundEdges))

		while True:
			try:
				edge = next(iteratorStack[-1])
				nextVertex = edge._destination
				if nextVertex in visited:
					ex = CycleError(f"Loop detected.")
					ex.add_note(f"First loop is:")
					for i, vertex in enumerate(vertexStack):
						ex.add_note(f"  {i}: {vertex!r}")
					raise ex

				vertexStack.append(nextVertex)
				if len(nextVertex._outboundEdges) == 0:
					yield tuple(vertexStack)
					vertexStack.pop()
				else:
					iteratorStack.append(iter(nextVertex._outboundEdges))

			except StopIteration:
				vertexStack.pop()
				iteratorStack.pop()

				if len(vertexStack) == 0:
					return

	def ShortestPathToByHops(self, destination: 'Vertex') -> Generator['Vertex', None, None]:
		"""
		Compute the shortest path (by hops) between this vertex and the destination vertex.

		A generator is return to iterate all vertices along the path including source and destination vertex.

		The search algorithm is breadth-first search (BFS) based. The found solution, if any, is not unique but deterministic
		as long as the graph was not modified (e.g. ordering of edges on vertices).

		:param destination: The destination vertex to reach.
		:returns:           A generator to iterate all vertices on the path found between this vertex and the destination vertex.
		"""
		# Trivial case if start is destination
		if self is destination:
			yield self
			return

		# Local struct to create multiple linked-lists forming a paths from current node back to the starting point
		# (actually a tree). Each node holds a reference to the vertex it represents.
		# Hint: slotted classes are faster than '@dataclasses.dataclass'.
		class Node(metaclass=ExtendedType, slots=True):
			parent: 'Node'
			ref: Vertex

			def __init__(self, parent: 'Node', ref: Vertex) -> None:
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
		for edge in self._outboundEdges:
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
				for edge in node.ref._outboundEdges:
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
				raise DestinationNotReachable(f"Destination is not reachable.")

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
		"""
		Compute the shortest path (by edge weight) between this vertex and the destination vertex.

		A generator is return to iterate all vertices along the path including source and destination vertex.

		The search algorithm is based on Dijkstra algorithm and using :mod:`heapq`. The found solution, if any, is not
		unique but deterministic as long as the graph was not modified (e.g. ordering of edges on vertices).

		:param destination: The destination vertex to reach.
		:returns:           A generator to iterate all vertices on the path found between this vertex and the destination vertex.
		"""
		# Improvements: both-sided Dijkstra (search from start and destination to reduce discovered area.

		# Trivial case if start is destination
		if self is destination:
			yield self
			return

		# Local struct to create multiple-linked lists forming a paths from current node back to the starting point
		# (actually a tree). Each node holds the overall weight from start to current node and a reference to the vertex it
		# represents.
		# Hint: slotted classes are faster than '@dataclasses.dataclass'.
		class Node(metaclass=ExtendedType, slots=True):
			parent: 'Node'
			distance: EdgeWeightType
			ref: Vertex

			def __init__(self, parent: 'Node', distance: EdgeWeightType, ref: Vertex) -> None:
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
		for edge in self._outboundEdges:
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
				for edge in node.ref._outboundEdges:
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
				raise DestinationNotReachable(f"Destination is not reachable.")

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
		yield startNode.ref, startNode.distance
		node = startNode.parent
		while node is not None:
			yield node.ref, node.distance
			node = node.parent

		# Other possible algorithms:
		# * Bellman-Ford
		# * Floyd-Warshall

	# def PathExistsTo(self, destination: 'Vertex'):
	# 	raise NotImplementedError()
	# 	# DFS
	# 	# Union find
	#
	# def MaximumFlowTo(self, destination: 'Vertex'):
	# 	raise NotImplementedError()
	# 	# Ford-Fulkerson algorithm
	# 	# Edmons-Karp algorithm
	# 	# Dinic's algorithm

	def ConvertToTree(self) -> Node:
		"""
		Converts all reachable vertices from this starting vertex to a tree of :class:`~pyTooling.Tree.Node` instances.

		The tree is traversed using depths-first-search.

		:returns:
		"""
		visited: Set[Vertex] = set()
		stack: List[Tuple[Node, typing_Iterator[Edge]]] = list()

		root = Node(nodeID=self._id, value=self._value)
		root._dict = self._dict.copy()

		visited.add(self)
		stack.append((root, iter(self._outboundEdges)))

		while True:
			try:
				edge = next(stack[-1][1])
				nextVertex = edge._destination
				if nextVertex not in visited:
					node = Node(nextVertex._id, nextVertex._value, parent=stack[-1][0])
					visited.add(nextVertex)
					if len(nextVertex._outboundEdges) != 0:
						stack.append((node, iter(nextVertex._outboundEdges)))
				else:
					raise NotATreeError(f"The directed subgraph is not a tree.")
					# TODO: compute cycle:
					#       a) branch 1 is described in stack
					#       b) branch 2 can be found by walking from joint to root in the tree
			except StopIteration:
				stack.pop()

				if len(stack) == 0:
					return root

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

		1. If :attr:`_value` is not None, return the string representation of :attr:`_value`.
		2. If :attr:`_id` is not None, return the string representation of :attr:`_id`.
		3. Else, return :meth:`__repr__`.

		:returns: The resolved string representation of the vertex.
		"""
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()


@export
class BaseEdge(
	BaseWithIDValueAndWeight[EdgeIDType, EdgeValueType, EdgeWeightType, EdgeDictKeyType, EdgeDictValueType],
	Generic[EdgeIDType, EdgeValueType, EdgeWeightType, EdgeDictKeyType, EdgeDictValueType]
):
	"""
	An **edge** can have a unique ID, a value, a weight and attached meta information as key-value-pairs. All edges are
	directed.
	"""
	_source:      Vertex
	_destination: Vertex

	def __init__(
		self,
		source: Vertex,
		destination: Vertex,
		edgeID: Nullable[EdgeIDType] = None,
		value: Nullable[EdgeValueType] = None,
		weight: Nullable[EdgeWeightType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::BaseEdge::init Needs documentation.

		:param source:        The source of the new edge.
		:param destination:   The destination of the new edge.
		:param edgeID:        The optional unique ID for the new edge.
		:param value:         The optional value for the new edge.
		:param weight:        The optional weight for the new edge.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		super().__init__(edgeID, value, weight, keyValuePairs)

		self._source = source
		self._destination = destination

		component = source._component
		if component is not destination._component:
			# TODO: should it be divided into with/without ID?
			oldComponent = destination._component
			for vertex in oldComponent._vertices:
				vertex._component = component
				component._vertices.add(vertex)
			component._graph._components.remove(oldComponent)
			del oldComponent

	@readonly
	def Source(self) -> Vertex:
		"""
		Read-only property to get the source (:attr:`_source`) of an edge.

		:returns: The source of an edge.
		"""
		return self._source

	@readonly
	def Destination(self) -> Vertex:
		"""
		Read-only property to get the destination (:attr:`_destination`) of an edge.

		:returns: The destination of an edge.
		"""
		return self._destination

	def Reverse(self) -> None:
		"""Reverse the direction of this edge."""
		swap = self._source
		self._source = self._destination
		self._destination = swap


@export
class Edge(
	BaseEdge[EdgeIDType, EdgeValueType, EdgeWeightType, EdgeDictKeyType, EdgeDictValueType],
	Generic[EdgeIDType, EdgeValueType, EdgeWeightType, EdgeDictKeyType, EdgeDictValueType]
):
	"""
	An **edge** can have a unique ID, a value, a weight and attached meta information as key-value-pairs. All edges are
	directed.
	"""

	def __init__(
		self,
		source: Vertex,
		destination: Vertex,
		edgeID: Nullable[EdgeIDType] = None,
		value: Nullable[EdgeValueType] = None,
		weight: Nullable[EdgeWeightType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Edge::init Needs documentation.

		:param source:        The source of the new edge.
		:param destination:   The destination of the new edge.
		:param edgeID:        The optional unique ID for the new edge.
		:param value:         The optional value for the new edge.
		:param weight:        The optional weight for the new edge.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		if not isinstance(source, Vertex):
			ex = TypeError("Parameter 'source' is not of type 'Vertex'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(source)}'.")
			raise ex
		if not isinstance(destination, Vertex):
			ex = TypeError("Parameter 'destination' is not of type 'Vertex'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(destination)}'.")
			raise ex
		if edgeID is not None and not isinstance(edgeID, Hashable):
			ex = TypeError("Parameter 'edgeID' is not of type 'EdgeIDType'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(edgeID)}'.")
			raise ex
		# if value is not None and  not isinstance(value, Vertex):
		# 	raise TypeError("Parameter 'value' is not of type 'EdgeValueType'.")
		if weight is not None and not isinstance(weight, (int, float)):
			ex = TypeError("Parameter 'weight' is not of type 'EdgeWeightType'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(weight)}'.")
			raise ex
		if source._graph is not destination._graph:
			raise NotInSameGraph(f"Source vertex and destination vertex are not in same graph.")

		super().__init__(source, destination, edgeID, value, weight, keyValuePairs)

	def Delete(self) -> None:
		# Remove from Source and Destination
		self._source._outboundEdges.remove(self)
		self._destination._inboundEdges.remove(self)

		# Remove from Graph and Subgraph
		if self._id is None:
			self._source._graph._edgesWithoutID.remove(self)
			if self._source._subgraph is not None:
				self._source._subgraph._edgesWithoutID.remove(self)
		else:
			del self._source._graph._edgesWithID[self._id]
			if self._source._subgraph is not None:
				del self._source._subgraph._edgesWithID[self]

		self._Delete()

	def _Delete(self) -> None:
		super().Delete()

	def Reverse(self) -> None:
		"""Reverse the direction of this edge."""
		self._source._outboundEdges.remove(self)
		self._source._inboundEdges.append(self)
		self._destination._inboundEdges.remove(self)
		self._destination._outboundEdges.append(self)

		super().Reverse()


@export
class Link(
	BaseEdge[LinkIDType, LinkValueType, LinkWeightType, LinkDictKeyType, LinkDictValueType],
	Generic[LinkIDType, LinkValueType, LinkWeightType, LinkDictKeyType, LinkDictValueType]
):
	"""
	A **link** can have a unique ID, a value, a weight and attached meta information as key-value-pairs. All links are
	directed.
	"""

	def __init__(
		self,
		source: Vertex,
		destination: Vertex,
		linkID: LinkIDType = None,
		value: LinkValueType = None,
		weight: Nullable[LinkWeightType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Edge::init Needs documentation.

		:param source:        The source of the new link.
		:param destination:   The destination of the new link.
		:param linkID:        The optional unique ID for the new link.
		:param value:         The optional value for the new v.
		:param weight:        The optional weight for the new link.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		if not isinstance(source, Vertex):
			ex = TypeError("Parameter 'source' is not of type 'Vertex'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(source)}'.")
			raise ex
		if not isinstance(destination, Vertex):
			ex = TypeError("Parameter 'destination' is not of type 'Vertex'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(destination)}'.")
			raise ex
		if linkID is not None and not isinstance(linkID, Hashable):
			ex = TypeError("Parameter 'linkID' is not of type 'LinkIDType'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(linkID)}'.")
			raise ex
		# if value is not None and  not isinstance(value, Vertex):
		# 	raise TypeError("Parameter 'value' is not of type 'EdgeValueType'.")
		if weight is not None and not isinstance(weight, (int, float)):
			ex = TypeError("Parameter 'weight' is not of type 'EdgeWeightType'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(weight)}'.")
			raise ex
		if source._graph is not destination._graph:
			raise NotInSameGraph(f"Source vertex and destination vertex are not in same graph.")

		super().__init__(source, destination, linkID, value, weight, keyValuePairs)

	def Delete(self) -> None:
		self._source._outboundEdges.remove(self)
		self._destination._inboundEdges.remove(self)

		if self._id is None:
			self._source._graph._linksWithoutID.remove(self)
		else:
			del self._source._graph._linksWithID[self._id]

		self._Delete()
		assert getrefcount(self) == 1

	def _Delete(self) -> None:
		super().Delete()

	def Reverse(self) -> None:
		"""Reverse the direction of this link."""
		self._source._outboundEdges.remove(self)
		self._source._inboundEdges.append(self)
		self._destination._inboundEdges.remove(self)
		self._destination._outboundEdges.append(self)

		super().Reverse()


@export
class BaseGraph(
	BaseWithName[GraphDictKeyType, GraphDictValueType],
	Generic[
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	.. todo:: GRAPH::BaseGraph Needs documentation.

	"""

	_verticesWithID:    Dict[VertexIDType, Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]
	_verticesWithoutID: List[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]
	_edgesWithID:       Dict[EdgeIDType, Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]]
	_edgesWithoutID:    List[Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType]]
	_linksWithID:       Dict[EdgeIDType, Link[LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]
	_linksWithoutID:    List[Link[LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]

	def __init__(
		self,
		name: Nullable[str] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
		#, vertices: Nullable[Iterable[Vertex]] = None) -> None:
	):
		"""
		.. todo:: GRAPH::BaseGraph::init Needs documentation.

		:param name:          The optional name of the graph.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		super().__init__(name, keyValuePairs)

		self._verticesWithoutID = []
		self._verticesWithID = {}
		self._edgesWithoutID = []
		self._edgesWithID = {}
		self._linksWithoutID = []
		self._linksWithID = {}

	def __del__(self):
		"""
		.. todo:: GRAPH::BaseGraph::del Needs documentation.

		"""
		try:
			del self._verticesWithoutID
			del self._verticesWithID
			del self._edgesWithoutID
			del self._edgesWithID
			del self._linksWithoutID
			del self._linksWithID
		except AttributeError:
			pass

		super().__del__()

	@readonly
	def VertexCount(self) -> int:
		"""Read-only property to access the number of vertices in this graph.

		:returns: The number of vertices in this graph."""
		return len(self._verticesWithoutID) + len(self._verticesWithID)

	@readonly
	def EdgeCount(self) -> int:
		"""Read-only property to access the number of edges in this graph.

		:returns: The number of edges in this graph."""
		return len(self._edgesWithoutID) + len(self._edgesWithID)

	@readonly
	def LinkCount(self) -> int:
		"""Read-only property to access the number of links in this graph.

		:returns: The number of links in this graph."""
		return len(self._linksWithoutID) + len(self._linksWithID)

	def IterateVertices(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
		"""
		Iterate all or selected vertices of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip vertices in the generator.

		:param predicate: Filter function accepting any vertex and returning a boolean.
		:returns:         A generator to iterate all vertices.
		"""
		if predicate is None:
			yield from self._verticesWithoutID
			yield from self._verticesWithID.values()

		else:
			for vertex in self._verticesWithoutID:
				if predicate(vertex):
					yield vertex

			for vertex in self._verticesWithID.values():
				if predicate(vertex):
					yield vertex

	def IterateRoots(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
		"""
		Iterate all or selected roots (vertices without inbound edges / without predecessors) of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip vertices in the generator.

		:param predicate: Filter function accepting any vertex and returning a boolean.
		:returns:         A generator to iterate all vertices without inbound edges.

		.. seealso::

		   :meth:`IterateLeafs` |br|
		      |rarr| Iterate leafs of a graph.
		   :meth:`Vertex.IsRoot <pyTooling.Graph.Vertex.IsRoot>` |br|
		      |rarr| Check if a vertex is a root vertex in the graph.
		   :meth:`Vertex.IsLeaf <pyTooling.Graph.Vertex.IsLeaf>` |br|
		      |rarr| Check if a vertex is a leaf vertex in the graph.
		"""
		if predicate is None:
			for vertex in self._verticesWithoutID:
				if len(vertex._inboundEdges) == 0:
					yield vertex

			for vertex in self._verticesWithID.values():
				if len(vertex._inboundEdges) == 0:
					yield vertex
		else:
			for vertex in self._verticesWithoutID:
				if len(vertex._inboundEdges) == 0 and predicate(vertex):
					yield vertex

			for vertex in self._verticesWithID.values():
				if len(vertex._inboundEdges) == 0 and predicate(vertex):
					yield vertex

	def IterateLeafs(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
		"""
		Iterate all or selected leafs (vertices without outbound edges / without successors) of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip vertices in the generator.

		:param predicate: Filter function accepting any vertex and returning a boolean.
		:returns:         A generator to iterate all vertices without outbound edges.

		.. seealso::

		   :meth:`IterateRoots` |br|
		      |rarr| Iterate roots of a graph.
		   :meth:`Vertex.IsRoot <pyTooling.Graph.Vertex.IsRoot>` |br|
		      |rarr| Check if a vertex is a root vertex in the graph.
		   :meth:`Vertex.IsLeaf <pyTooling.Graph.Vertex.IsLeaf>` |br|
		      |rarr| Check if a vertex is a leaf vertex in the graph.
		"""
		if predicate is None:
			for vertex in self._verticesWithoutID:
				if len(vertex._outboundEdges) == 0:
					yield vertex

			for vertex in self._verticesWithID.values():
				if len(vertex._outboundEdges) == 0:
					yield vertex
		else:
			for vertex in self._verticesWithoutID:
				if len(vertex._outboundEdges) == 0 and predicate(vertex):
					yield vertex

			for vertex in self._verticesWithID.values():
				if len(vertex._outboundEdges) == 0 and predicate(vertex):
					yield vertex

	# def IterateBFS(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
	# 	raise NotImplementedError()
	#
	# def IterateDFS(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
	# 	raise NotImplementedError()

	def IterateTopologically(self, predicate: Nullable[Callable[[Vertex], bool]] = None) -> Generator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
		"""
		Iterate all or selected vertices in topological order.

		If parameter ``predicate`` is not None, the given filter function is used to skip vertices in the generator.

		:param predicate:   Filter function accepting any vertex and returning a boolean.
		:returns:           A generator to iterate all vertices in topological order.
		:except CycleError: Raised if graph is cyclic, thus topological sorting isn't possible.
		"""
		outboundEdgeCounts = {}
		leafVertices = []

		for vertex in self._verticesWithoutID:
			if (count := len(vertex._outboundEdges)) == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		for vertex in self._verticesWithID.values():
			if (count := len(vertex._outboundEdges)) == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		if not leafVertices:
			raise CycleError(f"Graph has no leafs. Thus, no topological sorting exists.")

		overallCount = len(outboundEdgeCounts) + len(leafVertices)

		def removeVertex(vertex: Vertex):
			nonlocal overallCount
			overallCount -= 1
			for inboundEdge in vertex._inboundEdges:
				sourceVertex = inboundEdge.Source
				count = outboundEdgeCounts[sourceVertex] - 1
				outboundEdgeCounts[sourceVertex] = count
				if count == 0:
					leafVertices.append(sourceVertex)

		if predicate is None:
			for vertex in leafVertices:
				yield vertex

				removeVertex(vertex)
		else:
			for vertex in leafVertices:
				if predicate(vertex):
					yield vertex

				removeVertex(vertex)

		if overallCount == 0:
			return
		elif overallCount > 0:
			raise CycleError(f"Graph has remaining vertices. Thus, the graph has at least one cycle.")

		raise InternalError(f"Graph data structure is corrupted.")  # pragma: no cover

	def IterateEdges(self, predicate: Nullable[Callable[[Edge], bool]] = None) -> Generator[Edge[EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType], None, None]:
		"""
		Iterate all or selected edges of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip edges in the generator.

		:param predicate: Filter function accepting any edge and returning a boolean.
		:returns:         A generator to iterate all edges.
		"""
		if predicate is None:
			yield from self._edgesWithoutID
			yield from self._edgesWithID.values()

		else:
			for edge in self._edgesWithoutID:
				if predicate(edge):
					yield edge

			for edge in self._edgesWithID.values():
				if predicate(edge):
					yield edge

	def IterateLinks(self, predicate: Nullable[Callable[[Link], bool]] = None) -> Generator[Link[LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType], None, None]:
		"""
		Iterate all or selected links of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip links in the generator.

		:param predicate: Filter function accepting any link and returning a boolean.
		:returns:         A generator to iterate all links.
		"""
		if predicate is None:
			yield from self._linksWithoutID
			yield from self._linksWithID.values()

		else:
			for link in self._linksWithoutID:
				if predicate(link):
					yield link

			for link in self._linksWithID.values():
				if predicate(link):
					yield link

	def ReverseEdges(self, predicate: Nullable[Callable[[Edge], bool]] = None) -> None:
		"""
		Reverse all or selected edges of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip edges.

		:param predicate: Filter function accepting any edge and returning a boolean.
		"""
		if predicate is None:
			for edge in self._edgesWithoutID:
				swap = edge._source
				edge._source = edge._destination
				edge._destination = swap

			for edge in self._edgesWithID.values():
				swap = edge._source
				edge._source = edge._destination
				edge._destination = swap

			for vertex in self._verticesWithoutID:
				swap = vertex._inboundEdges
				vertex._inboundEdges = vertex._outboundEdges
				vertex._outboundEdges = swap

			for vertex in self._verticesWithID.values():
				swap = vertex._inboundEdges
				vertex._inboundEdges = vertex._outboundEdges
				vertex._outboundEdges = swap
		else:
			for edge in self._edgesWithoutID:
				if predicate(edge):
					edge.Reverse()

			for edge in self._edgesWithID.values():
				if predicate(edge):
					edge.Reverse()

	def ReverseLinks(self, predicate: Nullable[Callable[[Link], bool]] = None) -> None:
		"""
		Reverse all or selected links of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip links.

		:param predicate: Filter function accepting any link and returning a boolean.
		"""
		if predicate is None:
			for link in self._linksWithoutID:
				swap = link._source
				link._source = link._destination
				link._destination = swap

			for link in self._linksWithID.values():
				swap = link._source
				link._source = link._destination
				link._destination = swap

			for vertex in self._verticesWithoutID:
				swap = vertex._inboundLinks
				vertex._inboundLinks = vertex._outboundLinks
				vertex._outboundLinks = swap

			for vertex in self._verticesWithID.values():
				swap = vertex._inboundLinks
				vertex._inboundLinks = vertex._outboundLinks
				vertex._outboundLinks = swap
		else:
			for link in self._linksWithoutID:
				if predicate(link):
					link.Reverse()

			for link in self._linksWithID.values():
				if predicate(link):
					link.Reverse()

	def RemoveEdges(self, predicate: Nullable[Callable[[Edge], bool]] = None):
		"""
		Remove all or selected edges of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip edges.

		:param predicate: Filter function accepting any edge and returning a boolean.
		"""
		if predicate is None:
			for edge in self._edgesWithoutID:
				edge._Delete()

			for edge in self._edgesWithID.values():
				edge._Delete()

			self._edgesWithoutID = []
			self._edgesWithID = {}

			for vertex in self._verticesWithoutID:
				vertex._inboundEdges = []
				vertex._outboundEdges = []

			for vertex in self._verticesWithID.values():
				vertex._inboundEdges = []
				vertex._outboundEdges = []

		else:
			delEdges = [edge for edge in self._edgesWithID.values() if predicate(edge)]
			for edge in delEdges:
				del self._edgesWithID[edge._id]

				edge._source._outboundEdges.remove(edge)
				edge._destination._inboundEdges.remove(edge)
				edge._Delete()

			for edge in self._edgesWithoutID:
				if predicate(edge):
					self._edgesWithoutID.remove(edge)

					edge._source._outboundEdges.remove(edge)
					edge._destination._inboundEdges.remove(edge)
					edge._Delete()

	def RemoveLinks(self, predicate: Nullable[Callable[[Link], bool]] = None):
		"""
		Remove all or selected links of a graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip links.

		:param predicate: Filter function accepting any link and returning a boolean.
		"""
		if predicate is None:
			for link in self._linksWithoutID:
				link._Delete()

			for link in self._linksWithID.values():
				link._Delete()

			self._linksWithoutID = []
			self._linksWithID = {}

			for vertex in self._verticesWithoutID:
				vertex._inboundLinks = []
				vertex._outboundLinks = []

			for vertex in self._verticesWithID.values():
				vertex._inboundLinks = []
				vertex._outboundLinks = []

		else:
			delLinks = [link for link in self._linksWithID.values() if predicate(link)]
			for link in delLinks:
				del self._linksWithID[link._id]

				link._source._outboundLinks.remove(link)
				link._destination._inboundLinks.remove(link)
				link._Delete()

			for link in self._linksWithoutID:
				if predicate(link):
					self._linksWithoutID.remove(link)

					link._source._outboundLinks.remove(link)
					link._destination._inboundLinks.remove(link)
					link._Delete()

	def HasCycle(self) -> bool:
		"""
		.. todo:: GRAPH::BaseGraph::HasCycle Needs documentation.

		"""
		# IsAcyclic ?

		# Handle trivial case if graph is empty
		if len(self._verticesWithID) + len(self._verticesWithoutID) == 0:
			return False

		outboundEdgeCounts = {}
		leafVertices = []

		for vertex in self._verticesWithoutID:
			if (count := len(vertex._outboundEdges)) == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		for vertex in self._verticesWithID.values():
			if (count := len(vertex._outboundEdges)) == 0:
				leafVertices.append(vertex)
			else:
				outboundEdgeCounts[vertex] = count

		# If there are no leafs, then each vertex has at least one inbound and one outbound edges. Thus, there is a cycle.
		if not leafVertices:
			return True

		overallCount = len(outboundEdgeCounts) + len(leafVertices)

		for vertex in leafVertices:
			overallCount -= 1
			for inboundEdge in vertex._inboundEdges:
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

		raise InternalError(f"Graph data structure is corrupted.")  # pragma: no cover


@export
class Subgraph(
	BaseGraph[
		SubgraphDictKeyType, SubgraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	],
	Generic[
		SubgraphDictKeyType, SubgraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	.. todo:: GRAPH::Subgraph Needs documentation.

	"""

	_graph:    'Graph'

	def __init__(
		self,
		graph: 'Graph',
		name: Nullable[str] = None,
		# vertices: Nullable[Iterable[Vertex]] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Subgraph::init Needs documentation.

		:param graph:         The reference to the graph.
		:param name:          The optional name of the new sub-graph.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		if graph is None:
			raise ValueError("Parameter 'graph' is None.")
		if not isinstance(graph, Graph):
			ex = TypeError("Parameter 'graph' is not of type 'Graph'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(graph)}'.")
			raise ex

		super().__init__(name, keyValuePairs)

		graph._subgraphs.add(self)

		self._graph = graph

	def __del__(self):
		"""
		.. todo:: GRAPH::Subgraph::del Needs documentation.

		"""
		super().__del__()

	@readonly
	def Graph(self) -> 'Graph':
		"""
		Read-only property to access the graph, this subgraph is associated to (:attr:`_graph`).

		:returns: The graph this subgraph is associated to.
		"""
		return self._graph

	def __str__(self) -> str:
		"""
		.. todo:: GRAPH::Subgraph::str Needs documentation.

		"""
		return self._name if self._name is not None else "Unnamed subgraph"


@export
class View(
	BaseWithVertices[
		ViewDictKeyType, ViewDictValueType,
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	],
	Generic[
		ViewDictKeyType, ViewDictValueType,
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	.. todo:: GRAPH::View Needs documentation.

	"""

	def __init__(
		self,
		graph: 'Graph',
		name: Nullable[str] = None,
		vertices: Nullable[Iterable[Vertex]] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::View::init Needs documentation.

		:param graph:         The reference to the graph.
		:param name:          The optional name of the new view.
		:param vertices:      The optional list of vertices in the new view.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		super().__init__(graph, name, vertices, keyValuePairs)

		graph._views.add(self)

	def __del__(self):
		"""
		.. todo:: GRAPH::View::del Needs documentation.

		"""
		super().__del__()

	def __str__(self) -> str:
		"""
		.. todo:: GRAPH::View::str Needs documentation.

		"""
		return self._name if self._name is not None else "Unnamed view"


@export
class Component(
	BaseWithVertices[
		ComponentDictKeyType, ComponentDictValueType,
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	],
	Generic[
		ComponentDictKeyType, ComponentDictValueType,
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	.. todo:: GRAPH::Component Needs documentation.

	"""

	def __init__(
		self,
		graph: 'Graph',
		name: Nullable[str] = None,
		vertices: Nullable[Iterable[Vertex]] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Component::init Needs documentation.

		:param graph:         The reference to the graph.
		:param name:          The optional name of the new component.
		:param vertices:      The optional list of vertices in the new component.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		"""
		super().__init__(graph, name, vertices, keyValuePairs)

		graph._components.add(self)

	def __del__(self):
		"""
		.. todo:: GRAPH::Component::del Needs documentation.

		"""
		super().__del__()

	def __str__(self) -> str:
		"""
		.. todo:: GRAPH::Component::str Needs documentation.

		"""
		return self._name if self._name is not None else "Unnamed component"


@export
class Graph(
	BaseGraph[
		GraphDictKeyType, GraphDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	],
	Generic[
		GraphDictKeyType, GraphDictValueType,
		ComponentDictKeyType, ComponentDictValueType,
		SubgraphDictKeyType, SubgraphDictValueType,
		ViewDictKeyType, ViewDictValueType,
		VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType,
		EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType,
		LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType
	]
):
	"""
	A **graph** data structure is represented by an instance of :class:`~pyTooling.Graph.Graph` holding references to
	all nodes. Nodes are instances of :class:`~pyTooling.Graph.Vertex` classes and directed links between nodes are
	made of :class:`~pyTooling.Graph.Edge` instances. A graph can have attached meta information as key-value-pairs.
	"""
	_subgraphs:         Set[Subgraph[SubgraphDictKeyType, SubgraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]
	_views:             Set[View[ViewDictKeyType, ViewDictValueType, GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]
	_components:        Set[Component[ComponentDictKeyType, ComponentDictValueType, GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]

	def __init__(
		self,
		name: Nullable[str] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None
	) -> None:
		"""
		.. todo:: GRAPH::Graph::init Needs documentation.

		:param name:          The optional name of the new graph.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.#
		"""
		super().__init__(name, keyValuePairs)

		self._subgraphs = set()
		self._views = set()
		self._components = set()

	def __del__(self):
		"""
		.. todo:: GRAPH::Graph::del Needs documentation.

		"""
		try:
			del self._subgraphs
			del self._views
			del self._components
		except AttributeError:
			pass

		super().__del__()

	@readonly
	def Subgraphs(self) -> Set[Subgraph]:
		"""Read-only property to access the subgraphs in this graph (:attr:`_subgraphs`).

		:returns: The set of subgraphs in this graph."""
		return self._subgraphs

	@readonly
	def Views(self) -> Set[View]:
		"""Read-only property to access the views in this graph (:attr:`_views`).

		:returns: The set of views in this graph."""
		return self._views

	@readonly
	def Components(self) -> Set[Component]:
		"""Read-only property to access the components in this graph (:attr:`_components`).

		:returns: The set of components in this graph."""
		return self._components

	@readonly
	def SubgraphCount(self) -> int:
		"""Read-only property to access the number of subgraphs in this graph.

		:returns: The number of subgraphs in this graph."""
		return len(self._subgraphs)

	@readonly
	def ViewCount(self) -> int:
		"""Read-only property to access the number of views in this graph.

		:returns: The number of views in this graph."""
		return len(self._views)

	@readonly
	def ComponentCount(self) -> int:
		"""Read-only property to access the number of components in this graph.

		:returns: The number of components in this graph."""
		return len(self._components)

	def __iter__(self) -> typing_Iterator[Vertex[GraphDictKeyType, GraphDictValueType, VertexIDType, VertexWeightType, VertexValueType, VertexDictKeyType, VertexDictValueType, EdgeIDType, EdgeWeightType, EdgeValueType, EdgeDictKeyType, EdgeDictValueType, LinkIDType, LinkWeightType, LinkValueType, LinkDictKeyType, LinkDictValueType]]:
		"""
		.. todo:: GRAPH::Graph::iter Needs documentation.

		"""
		def gen():
			yield from self._verticesWithoutID
			yield from self._verticesWithID
		return iter(gen())

	def HasVertexByID(self, vertexID: Nullable[VertexIDType]) -> bool:
		"""
		.. todo:: GRAPH::Graph::HasVertexByID Needs documentation.

		"""
		if vertexID is None:
			return len(self._verticesWithoutID) >= 1
		else:
			return vertexID in self._verticesWithID

	def HasVertexByValue(self, value: Nullable[VertexValueType]) -> bool:
		"""
		.. todo:: GRAPH::Graph::HasVertexByValue Needs documentation.

		"""
		return any(vertex._value == value for vertex in chain(self._verticesWithoutID, self._verticesWithID.values()))

	def GetVertexByID(self, vertexID: Nullable[VertexIDType]) -> Vertex:
		"""
		.. todo:: GRAPH::Graph::GetVertexByID Needs documentation.

		"""
		if vertexID is None:
			if (l := len(self._verticesWithoutID)) == 1:
				return self._verticesWithoutID[0]
			elif l == 0:
				raise KeyError(f"Found no vertex with ID `None`.")
			else:
				raise KeyError(f"Found multiple vertices with ID `None`.")
		else:
			return self._verticesWithID[vertexID]

	def GetVertexByValue(self, value: Nullable[VertexValueType]) -> Vertex:
		"""
		.. todo:: GRAPH::Graph::GetVertexByValue Needs documentation.

		"""
		# FIXME: optimize: iterate only until first item is found and check for a second to produce error
		vertices = [vertex for vertex in chain(self._verticesWithoutID, self._verticesWithID.values()) if vertex._value == value]
		if (l := len(vertices)) == 1:
			return vertices[0]
		elif l == 0:
			raise KeyError(f"Found no vertex with Value == `{value}`.")
		else:
			raise KeyError(f"Found multiple vertices with Value == `{value}`.")

	def CopyGraph(self) -> 'Graph':
		raise NotImplementedError()

	def CopyVertices(self, predicate: Nullable[Callable[[Vertex], bool]] = None, copyGraphDict: bool = True, copyVertexDict: bool = True) -> 'Graph':
		"""
		Create a new graph and copy all or selected vertices of the original graph.

		If parameter ``predicate`` is not None, the given filter function is used to skip vertices.

		:param predicate:      Filter function accepting any vertex and returning a boolean.
		:param copyGraphDict:  If ``True``, copy all graph attached attributes into the new graph.
		:param copyVertexDict: If ``True``, copy all vertex attached attributes into the new vertices.
		"""
		graph = Graph(self._name)
		if copyGraphDict:
			graph._dict = self._dict.copy()

		if predicate is None:
			for vertex in self._verticesWithoutID:
				v = Vertex(None, vertex._value, graph=graph)
				if copyVertexDict:
					v._dict = vertex._dict.copy()

			for vertexID, vertex in self._verticesWithID.items():
				v = Vertex(vertexID, vertex._value, graph=graph)
				if copyVertexDict:
					v._dict = vertex._dict.copy()
		else:
			for vertex in self._verticesWithoutID:
				if predicate(vertex):
					v = Vertex(None, vertex._value, graph=graph)
					if copyVertexDict:
						v._dict = vertex._dict.copy()

			for vertexID, vertex in self._verticesWithID.items():
				if predicate(vertex):
					v = Vertex(vertexID, vertex._value, graph=graph)
					if copyVertexDict:
						v._dict = vertex._dict.copy()

		return graph

		# class Iterator():
		# 	visited = [False for _ in range(self.__len__())]

	# def CheckForNegativeCycles(self):
	# 	raise NotImplementedError()
	# 	# Bellman-Ford
	# 	# Floyd-Warshall
	#
	# def IsStronglyConnected(self):
	# 	raise NotImplementedError()
	#
	# def GetStronglyConnectedComponents(self):
	# 	raise NotImplementedError()
	# 	# Tarjan's and Kosaraju's algorithm
	#
	# def TravelingSalesmanProblem(self):
	# 	raise NotImplementedError()
	# 	# Held-Karp
	# 	# branch and bound
	#
	# def GetBridges(self):
	# 	raise NotImplementedError()
	#
	# def GetArticulationPoints(self):
	# 	raise NotImplementedError()
	#
	# def MinimumSpanningTree(self):
	# 	raise NotImplementedError()
	# 	# Kruskal
	# 	# Prim's algorithm
	# 	# Buruvka's algorithm

	def __repr__(self) -> str:
		"""
		.. todo:: GRAPH::Graph::repr Needs documentation.

		"""
		statistics = f", vertices: {self.VertexCount}, edges: {self.EdgeCount}"
		if self._name is None:
			return f"<graph: unnamed graph{statistics}>"
		else:
			return f"<graph: '{self._name}'{statistics}>"

	def __str__(self) -> str:
		"""
		.. todo:: GRAPH::Graph::str Needs documentation.

		"""
		if self._name is None:
			return f"Graph: unnamed graph"
		else:
			return f"Graph: '{self._name}'"
