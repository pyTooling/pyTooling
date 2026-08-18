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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A data model to write out GraphML XML files.

.. seealso::

   `GraphML Primer <http://graphml.graphdrawing.org/primer/graphml-primer.html>`__
      |rarr| The format's own introduction, describing the elements this module writes.
"""
from enum    import Enum, auto
from pathlib import Path
from typing  import Any, ClassVar, List, Dict, Union, Optional as Nullable

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Graph       import Graph as pyToolingGraph, Subgraph as pyToolingSubgraph
from pyTooling.Tree        import Node as pyToolingNode


@export
class AttributeContext(Enum):
	"""
	Enumeration of all attribute contexts.

	An attribute context describes to what kind of GraphML node an attribute can be applied.
	"""
	GraphML = auto()
	Graph = auto()
	Node = auto()
	Edge = auto()
	Port = auto()

	def __str__(self) -> str:
		"""
		Return the enumeration value's name as it is written in a GraphML document.

		:returns: Name of the enumeration value in lower case.
		"""
		return f"{self.name.lower()}"


@export
class AttributeTypes(Enum):
	"""
	Enumeration of all attribute types.

	An attribute type describes what datatype can be applied to an attribute.
	"""
	Boolean = auto()
	Int = auto()
	Long = auto()
	Float = auto()
	Double = auto()
	String = auto()

	def __str__(self) -> str:
		"""
		Return the enumeration value's name as it is written in a GraphML document.

		:returns: Name of the enumeration value in lower case.
		"""
		return f"{self.name.lower()}"


@export
class EdgeDefault(Enum):
	"""An enumeration describing the default edge direction."""
	Undirected = auto()
	Directed = auto()

	def __str__(self) -> str:
		"""
		Return the enumeration value's name as it is written in a GraphML document.

		:returns: Name of the enumeration value in lower case.
		"""
		return f"{self.name.lower()}"


@export
class ParsingOrder(Enum):
	"""An enumeration describing the parsing order of the graph's representation."""
	NodesFirst = auto()     #: First, all nodes are given, then followed by all edges.
	AdjacencyList = auto()
	Free = auto()

	def __str__(self) -> str:
		"""
		Return the enumeration value's name as it is written in a GraphML document.

		:returns: Name of the enumeration value in lower case.
		"""
		return f"{self.name.lower()}"


@export
class IDStyle(Enum):
	"""An enumeration describing the style of identifiers (IDs)."""
	Canonical = auto()
	Free = auto()

	def __str__(self) -> str:
		"""
		Return the enumeration value's name as it is written in a GraphML document.

		:returns: Name of the enumeration value in lower case.
		"""
		return f"{self.name.lower()}"


@export
class Base(metaclass=ExtendedType, slots=True):
	"""
	Base-class for all GraphML data model classes.
	"""
	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		:returns: ``True``, if the element needs a closing tag.
		"""
		return True

	def Tag(self, indent: int = 0) -> str:
		"""
		Return this element as a self-closing XML tag.

		:param indent:               Indentation level of the XML element.
		:returns:                    The XML tag, indented and terminated by a newline.
		:raises NotImplementedError: If this abstract method is not overridden by a derived class.
		"""
		raise NotImplementedError()

	def OpeningTag(self, indent: int = 0) -> str:
		"""
		Return the opening XML tag of this element.

		:param indent:               Indentation level of the XML element.
		:returns:                    The opening XML tag, indented and terminated by a newline.
		:raises NotImplementedError: If this abstract method is not overridden by a derived class.
		"""
		raise NotImplementedError()

	def ClosingTag(self, indent: int = 0) -> str:
		"""
		Return the closing XML tag of this element.

		:param indent:               Indentation level of the XML element.
		:returns:                    The closing XML tag, indented and terminated by a newline.
		:raises NotImplementedError: If this abstract method is not overridden by a derived class.
		"""
		raise NotImplementedError()

	def ToStringLines(self, indent: int = 0) -> List[str]:
		"""
		Render this element as a list of XML lines.

		:param indent:               Indentation level of the XML element.
		:returns:                    List of XML lines describing this element.
		:raises NotImplementedError: If this abstract method is not overridden by a derived class.
		"""
		raise NotImplementedError()


@export
class BaseWithID(Base):
	"""Base-class for all GraphML elements carrying a document-wide unique ID."""
	_id: str  #: Unique identifier of this GraphML element.

	def __init__(self, identifier: str) -> None:
		"""
		Initialize a GraphML element with its unique ID.

		:param identifier: Unique ID of the element within the GraphML document.
		"""
		super().__init__()
		self._id = identifier

	@readonly
	def ID(self) -> str:
		"""
		Read-only property to access the element's unique ID (:attr:`_id`).

		:returns: Unique ID of the element.
		"""
		return self._id


@export
class BaseWithData(BaseWithID):
	"""Base-class for all GraphML elements that can carry attached data items (key-value-pairs)."""
	_data: List['Data']  #: Data items (key-value-pairs) attached to this GraphML element.

	def __init__(self, identifier: str) -> None:
		"""
		Initialize a GraphML element with its unique ID and an empty list of data items.

		:param identifier: Unique ID of the element within the GraphML document.
		"""
		super().__init__(identifier)

		self._data = []

	@readonly
	def Data(self) -> List['Data']:
		"""
		Read-only property to access the data elements attached to this element (:attr:`_data`).

		:returns: List of data elements.
		"""
		return self._data

	def AddData(self, data: Data) -> Data:
		"""
		Attach a data item (key-value-pair) to this element.

		:param data: The data item to attach.
		:returns:    The attached data item, so it can be used in the calling expression.
		"""
		self._data.append(data)
		return data


@export
class Key(BaseWithID):
	"""
	Declares an attribute that data items can refer to.

	A GraphML document declares its attributes once - name, data type, and the element kind they apply to - and every
	:class:`Data` item then references such a key by ID.
	"""
	_context:       AttributeContext  #: GraphML element kind this key can be used on.
	_attributeName: str               #: Name of the attribute described by this key.
	_attributeType: AttributeTypes    #: Data type of the attribute described by this key.

	def __init__(self, identifier: str, context: AttributeContext, name: str, type: AttributeTypes) -> None:
		"""
		Initialize a key declaring an attribute.

		:param identifier: Unique ID of the key within the GraphML document.
		:param context:    GraphML element kind this key can be used on.
		:param name:       Name of the declared attribute.
		:param type:       Data type of the declared attribute.
		"""
		super().__init__(identifier)

		self._context = context
		self._attributeName = name
		self._attributeType = type

	@readonly
	def Context(self) -> AttributeContext:
		"""
		Read-only property to access the context this key applies to (:attr:`_context`).

		:returns: The attribute's context (graph, node, edge, ...).
		"""
		return self._context

	@readonly
	def AttributeName(self) -> str:
		"""
		Read-only property to access the name of the described attribute (:attr:`_attributeName`).

		:returns: Name of the attribute.
		"""
		return self._attributeName

	@readonly
	def AttributeType(self) -> AttributeTypes:
		"""
		Read-only property to access the type of the described attribute (:attr:`_attributeType`).

		:returns: Type of the attribute.
		"""
		return self._attributeType

	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		A key is always written as a self-closing tag.

		:returns: ``False``, because a key never has a closing tag.
		"""
		return False

	def Tag(self, indent: int = 2) -> str:
		"""
		Return this key as a self-closing XML tag.

		:param indent: Indentation level of the XML element.
		:returns:      The XML tag, indented and terminated by a newline.
		"""
		return f"""{'  '*indent}<key id="{self._id}" for="{self._context}" attr.name="{self._attributeName}" attr.type="{self._attributeType}" />\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		"""
		Render this key as a list of XML lines.

		:param indent: Indentation level of the XML element.
		:returns:      List of XML lines describing this key and everything attached to it.
		"""
		return [self.Tag(indent)]


@export
class Data(Base):
	"""A single attached attribute: a value and the :class:`Key` describing it."""
	_key:  Key  #: Key describing name and type of this data item.
	_data: Any  #: Value of this data item.

	def __init__(self, key: Key, data: Any) -> None:
		"""
		Initialize a data item with the key describing it and its value.

		:param key:  Key declaring name and type of this attribute.
		:param data: Value of this attribute.
		"""
		super().__init__()

		self._key = key
		self._data = data

	@readonly
	def Key(self) -> Key:
		"""
		Read-only property to access the key describing this data element (:attr:`_key`).

		:returns: The key this data element refers to.
		"""
		return self._key

	@readonly
	def Data(self) -> Any:
		"""
		Read-only property to access the data element's value (:attr:`_data`).

		:returns: Value of the data element.
		"""
		return self._data

	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		:returns: ``False``, because a data element is written inline.
		"""
		return False

	def Tag(self, indent: int = 2) -> str:
		"""
		Return this data item as a self-closing XML tag.

		:param indent: Indentation level of the XML element.
		:returns:      The XML tag, indented and terminated by a newline.
		"""
		data = str(self._data)
		data = data.replace("&", "&amp;")
		data = data.replace("<", "&lt;")
		data = data.replace(">", "&gt;")
		data = data.replace("\n", "\\n")
		return f"""{'  '*indent}<data key="{self._key._id}">{data}</data>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		"""
		Render this data item as a list of XML lines.

		:param indent: Indentation level of the XML element.
		:returns:      List of XML lines describing this data item and everything attached to it.
		"""
		return [self.Tag(indent)]


@export
class Node(BaseWithData):
	"""A node (vertex) of a GraphML graph."""

	def __init__(self, identifier: str) -> None:
		"""
		Initialize a node.

		:param identifier: Unique ID of the node within the GraphML document.
		"""
		super().__init__(identifier)

	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		:returns: ``True``, if the node carries data elements, otherwise ``False``.
		"""
		return len(self._data) > 0

	def Tag(self, indent: int = 2) -> str:
		"""
		Return this node as a self-closing XML tag.

		:param indent: Indentation level of the XML element.
		:returns:      The XML tag, indented and terminated by a newline.
		"""
		return f"""{'  '*indent}<node id="{self._id}" />\n"""

	def OpeningTag(self, indent: int = 2) -> str:
		"""
		Return the opening XML tag of this node.

		:param indent: Indentation level of the XML element.
		:returns:      The opening XML tag, indented and terminated by a newline.
		"""
		return f"""{'  '*indent}<node id="{self._id}">\n"""

	def ClosingTag(self, indent: int = 2) -> str:
		"""
		Return the closing XML tag of this node.

		:param indent: Indentation level of the XML element.
		:returns:      The closing XML tag, indented and terminated by a newline.
		"""
		return f"""{'  ' * indent}</node>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		"""
		Render this node as a list of XML lines.

		:param indent: Indentation level of the XML element.
		:returns:      List of XML lines describing this node and everything attached to it.
		"""
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class Edge(BaseWithData):
	"""An edge of a GraphML graph, connecting a source node to a target node."""
	_source: Node  #: Node the edge starts at.
	_target: Node  #: Node the edge ends at.

	def __init__(self, identifier: str, source: Node, target: Node) -> None:
		"""
		Initialize an edge between two nodes.

		:param identifier: Unique ID of the edge within the GraphML document.
		:param source:     Node the edge starts at.
		:param target:     Node the edge ends at.
		"""
		super().__init__(identifier)

		self._source = source
		self._target = target

	@readonly
	def Source(self) -> Node:
		"""
		Read-only property to access the edge's source node (:attr:`_source`).

		:returns: Source node of the edge.
		"""
		return self._source

	@readonly
	def Target(self) -> Node:
		"""
		Read-only property to access the edge's target node (:attr:`_target`).

		:returns: Target node of the edge.
		"""
		return self._target

	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		:returns: ``True``, if the edge carries data elements, otherwise ``False``.
		"""
		return len(self._data) > 0

	def Tag(self, indent: int = 2) -> str:
		"""
		Return this edge as a self-closing XML tag.

		:param indent: Indentation level of the XML element.
		:returns:      The XML tag, indented and terminated by a newline.
		"""
		return f"""{'  ' * indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}" />\n"""

	def OpeningTag(self, indent: int = 2) -> str:
		"""
		Return the opening XML tag of this edge.

		:param indent: Indentation level of the XML element.
		:returns:      The opening XML tag, indented and terminated by a newline.
		"""
		return f"""{'  '*indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}">\n"""

	def ClosingTag(self, indent: int = 2) -> str:
		"""
		Return the closing XML tag of this edge.

		:param indent: Indentation level of the XML element.
		:returns:      The closing XML tag, indented and terminated by a newline.
		"""
		return f"""{'  ' * indent}</edge>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		"""
		Render this edge as a list of XML lines.

		:param indent: Indentation level of the XML element.
		:returns:      List of XML lines describing this edge and everything attached to it.
		"""
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class BaseGraph(BaseWithData, mixin=True):
	"""
	Mixin-class for everything that contains nodes, edges and subgraphs - a graph as well as a subgraph.

	Beside the elements themselves, it carries the document-level settings applied while writing them: the default edge
	direction, the parsing order, and the ID styles for nodes and edges.
	"""
	_subgraphs:   Dict[str, 'Subgraph']  #: Subgraphs of this graph, by ID.
	_nodes:       Dict[str, Node]        #: Nodes of this graph, by ID.
	_edges:       Dict[str, Edge]        #: Edges of this graph, by ID.
	_edgeDefault: EdgeDefault            #: Direction applied to edges that don't specify one.
	_parseOrder:  ParsingOrder           #: Order in which nodes and edges may appear in the XML document.
	_nodeIDStyle: IDStyle                #: Whether node IDs are free-form or canonical.
	_edgeIDStyle: IDStyle                #: Whether edge IDs are free-form or canonical.

	def __init__(self, identifier: Nullable[str] = None) -> None:
		"""
		Initialize an empty graph with the default document settings.

		Edges are directed, nodes are written before edges, and both ID styles are free-form until they are changed.

		:param identifier: Unique ID of the graph within the GraphML document.
		"""
		super().__init__(identifier)

		self._subgraphs = {}
		self._nodes = {}
		self._edges = {}
		self._edgeDefault = EdgeDefault.Directed
		self._parseOrder = ParsingOrder.NodesFirst
		self._nodeIDStyle = IDStyle.Free
		self._edgeIDStyle = IDStyle.Free

	@readonly
	def Subgraphs(self) -> Dict[str, 'Subgraph']:
		"""
		Read-only property to access the graph's subgraphs (:attr:`_subgraphs`).

		:returns: Dictionary of subgraph IDs and subgraphs.
		"""
		return self._subgraphs

	@readonly
	def Nodes(self) -> Dict[str, Node]:
		"""
		Read-only property to access the graph's nodes (:attr:`_nodes`).

		:returns: Dictionary of node IDs and nodes.
		"""
		return self._nodes

	@readonly
	def Edges(self) -> Dict[str, Edge]:
		"""
		Read-only property to access the graph's edges (:attr:`_edges`).

		:returns: Dictionary of edge IDs and edges.
		"""
		return self._edges

	def AddSubgraph(self, subgraph: 'Subgraph') -> 'Subgraph':
		self._subgraphs[subgraph._subgraphID] = subgraph
		self._nodes[subgraph._id] = subgraph
		return subgraph

	def GetSubgraph(self, subgraphName: str) -> 'Subgraph':
		return self._subgraphs[subgraphName]

	def AddNode(self, node: Node) -> Node:
		self._nodes[node._id] = node
		return node

	def GetNode(self, nodeName: str) -> Node:
		return self._nodes[nodeName]

	def AddEdge(self, edge: Edge) -> Edge:
		self._edges[edge._id] = edge
		return edge

	def GetEdge(self, edgeName: str) -> Edge:
		return self._edges[edgeName]

	def OpeningTag(self, indent: int = 1) -> str:
		return f"""\
{'  '*indent}<graph id="{self._id}"
{'  '*indent}  edgedefault="{self._edgeDefault!s}"
{'  '*indent}  parse.nodes="{len(self._nodes)}"
{'  '*indent}  parse.edges="{len(self._edges)}"
{'  '*indent}  parse.order="{self._parseOrder!s}"
{'  '*indent}  parse.nodeids="{self._nodeIDStyle!s}"
{'  '*indent}  parse.edgeids="{self._edgeIDStyle!s}">
"""

	def ClosingTag(self, indent: int = 1) -> str:
		return f"{'  '*indent}</graph>\n"

	def ToStringLines(self, indent: int = 1) -> List[str]:
		lines = [self.OpeningTag(indent)]
		for node in self._nodes.values():
			lines.extend(node.ToStringLines(indent + 1))
		for edge in self._edges.values():
			lines.extend(edge.ToStringLines(indent + 1))
		# for data in self._data:
		# 	lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class Graph(BaseGraph):
	"""
	The root graph of a GraphML document.

	It owns the ID space: every node, edge and subgraph registers itself here, so an ID is used only once per document.
	"""
	_document: 'GraphMLDocument'                         #: The GraphML document this graph belongs to.
	_ids:      Dict[str, Union[Node, Edge, 'Subgraph']]  #: Every element of this graph by ID, used to keep IDs unique.

	def __init__(self, document: 'GraphMLDocument', identifier: str) -> None:
		"""
		Initialize the root graph of a GraphML document.

		:param document:   The GraphML document this graph belongs to.
		:param identifier: Unique ID of the graph within the GraphML document.
		"""
		super().__init__(identifier)
		self._document = document
		self._ids = {}

	def GetByID(self, identifier: str) -> Union[Node, Edge, 'Subgraph']:
		return self._ids[identifier]

	def AddSubgraph(self, subgraph: 'Subgraph') -> 'Subgraph':
		result = super().AddSubgraph(subgraph)
		self._ids[subgraph._subgraphID] = subgraph
		subgraph._root = self
		return result

	def AddNode(self, node: Node) -> Node:
		result = super().AddNode(node)
		self._ids[node._id] = node
		return result

	def AddEdge(self, edge: Edge) -> Edge:
		result = super().AddEdge(edge)
		self._ids[edge._id] = edge
		return result


@export
class Subgraph(Node, BaseGraph):
	"""
	A nested graph, which is a node of its parent graph and a graph of its own.

	It therefore carries two identifiers: the node's ID it is referenced by, and :attr:`_subgraphID` for the graph it
	contains.
	"""
	_subgraphID: str              #: ID of the subgraph, which is distinct from the node's own ID.
	_root:       Nullable[Graph]  #: The graph this subgraph is nested in.

	def __init__(self, nodeIdentifier: str, graphIdentifier: str) -> None:
		"""
		Initialize a subgraph, which is a node in its parent graph and a graph of its own.

		:param nodeIdentifier:  Unique ID of the node representing the subgraph.
		:param graphIdentifier: Unique ID of the graph contained in that node.
		"""
		super().__init__(nodeIdentifier)
		BaseGraph.__init__(self, nodeIdentifier)

		self._subgraphID = graphIdentifier
		self._root = None

	@readonly
	def RootGraph(self) -> Graph:
		"""
		Read-only property to access the graph this subgraph is embedded in (:attr:`_root`).

		:returns: The root graph.
		"""
		return self._root

	@readonly
	def SubgraphID(self) -> str:
		"""
		Read-only property to access the subgraph's ID (:attr:`_subgraphID`).

		:returns: ID of the subgraph.
		"""
		return self._subgraphID

	@readonly
	def HasClosingTag(self) -> bool:
		"""
		Check if this XML element is written with a separate closing tag.

		:returns: ``True``, because a subgraph always has a closing tag.
		"""
		return True

	def AddNode(self, node: Node) -> Node:
		result = super().AddNode(node)
		self._root._ids[node._id] = node
		return result

	def AddEdge(self, edge: Edge) -> Edge:
		result = super().AddEdge(edge)
		self._root._ids[edge._id] = edge
		return result

	def Tag(self, indent: int = 2) -> str:
		raise NotImplementedError()

	def OpeningTag(self, indent: int = 1) -> str:
		return f"""\
{'  ' * indent}<graph id="{self._subgraphID}"
{'  ' * indent}  edgedefault="{self._edgeDefault!s}"
{'  ' * indent}  parse.nodes="{len(self._nodes)}"
{'  ' * indent}  parse.edges="{len(self._edges)}"
{'  ' * indent}  parse.order="{self._parseOrder!s}"
{'  ' * indent}  parse.nodeids="{self._nodeIDStyle!s}"
{'  ' * indent}  parse.edgeids="{self._edgeIDStyle!s}">
"""

	def ClosingTag(self, indent: int = 2) -> str:
		return BaseGraph.ClosingTag(self, indent)

	def ToStringLines(self, indent: int = 2) -> List[str]:
		lines = [super().OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		# lines.extend(Graph.ToStringLines(self, indent + 1))
		lines.append(self.OpeningTag(indent + 1))
		for node in self._nodes.values():
			lines.extend(node.ToStringLines(indent + 2))
		for edge in self._edges.values():
			lines.extend(edge.ToStringLines(indent + 2))
		# for data in self._data:
		# 	lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent + 1))
		lines.append(super().ClosingTag(indent))

		return lines


@export
class GraphMLDocument(Base):
	"""
	A GraphML document: the root graph, the keys it declares, and the XML boilerplate to write it out.
	"""

	xmlNS: ClassVar[Dict[Nullable[str], str]] = {
		None:  "http://graphml.graphdrawing.org/xmlns",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance"
	}  #: XML namespaces of a GraphML document.
	xsi: ClassVar[Dict[str, str]] = {
		"schemaLocation": "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
	}  #: XML schema instance attributes of a GraphML document.

	_graph: Graph           #: The document's root graph.
	_keys:  Dict[str, Key]  #: Keys declared by this document, by ID.

	def __init__(self, identifier: str = "G") -> None:
		"""
		Initialize a GraphML document with an empty root graph.

		:param identifier: Unique ID of the root graph.
		"""
		super().__init__()

		self._graph = Graph(self, identifier)
		self._keys = {}

	@readonly
	def Graph(self) -> BaseGraph:
		"""
		Read-only property to access the document's graph (:attr:`_graph`).

		:returns: The graph described by this document.
		"""
		return self._graph

	@readonly
	def Keys(self) -> Dict[str, Key]:
		"""
		Read-only property to access the attribute keys declared in this document (:attr:`_keys`).

		:returns: Dictionary of key IDs and keys.
		"""
		return self._keys

	def AddKey(self, key: Key) -> Key:
		self._keys[key._id] = key
		return key

	def GetKey(self, keyName: str) -> Key:
		return self._keys[keyName]

	def HasKey(self, keyName: str) -> bool:
		return keyName in self._keys

	def FromGraph(self, graph: pyToolingGraph) -> None:
		document = self
		self._graph._id = graph._name

		nodeValue = self.AddKey(Key("nodeValue", AttributeContext.Node, "value", AttributeTypes.String))
		edgeValue = self.AddKey(Key("edgeValue", AttributeContext.Edge, "value", AttributeTypes.String))

		def translateGraph(rootGraph: Graph, pyTGraph: pyToolingGraph):
			"""
			Nested function for recursion.

			It translates the vertices and edges of one pyTooling graph into GraphML nodes and edges, and recurses into the
			subgraphs it finds.

			:param rootGraph: The GraphML graph the elements are added to.
			:param pyTGraph:  The pyTooling graph to translate.
			"""
			for vertex in pyTGraph.IterateVertices():
				newNode = Node(vertex._id)
				newNode.AddData(Data(nodeValue, vertex._value))
				for key, value in vertex._dict.items():
					if document.HasKey(str(key)):
						nodeKey = document.GetKey(f"node{key!s}")
					else:
						nodeKey = document.AddKey(Key(f"node{key!s}", AttributeContext.Node, str(key), AttributeTypes.String))
					newNode.AddData(Data(nodeKey, value))

				rootGraph.AddNode(newNode)

			for edge in pyTGraph.IterateEdges():
				source = rootGraph.GetByID(edge._source._id)
				target = rootGraph.GetByID(edge._destination._id)

				newEdge = Edge(edge._id, source, target)
				newEdge.AddData(Data(edgeValue, edge._value))
				for key, value in edge._dict.items():
					if self.HasKey(str(key)):
						edgeKey = self.GetBy(f"edge{key!s}")
					else:
						edgeKey = self.AddKey(Key(f"edge{key!s}", AttributeContext.Edge, str(key), AttributeTypes.String))
					newEdge.AddData(Data(edgeKey, value))

				rootGraph.AddEdge(newEdge)

			for link in pyTGraph.IterateLinks():
				source = rootGraph.GetByID(link._source._id)
				target = rootGraph.GetByID(link._destination._id)

				newEdge = Edge(link._id, source, target)
				newEdge.AddData(Data(edgeValue, link._value))
				for key, value in link._dict.items():
					if self.HasKey(str(key)):
						edgeKey = self.GetKey(f"link{key!s}")
					else:
						edgeKey = self.AddKey(Key(f"link{key!s}", AttributeContext.Edge, str(key), AttributeTypes.String))
					newEdge.AddData(Data(edgeKey, value))

				rootGraph.AddEdge(newEdge)

		def translateSubgraph(nodeGraph: Subgraph, pyTSubgraph: pyToolingSubgraph):
			"""
			Nested function for recursion.

			It translates one pyTooling subgraph into a GraphML subgraph.

			:param nodeGraph:   The GraphML subgraph the elements are added to.
			:param pyTSubgraph: The pyTooling subgraph to translate.
			"""
			rootGraph = nodeGraph.RootGraph

			for vertex in pyTSubgraph.IterateVertices():
				newNode = Node(vertex._id)
				newNode.AddData(Data(nodeValue, vertex._value))
				for key, value in vertex._dict.items():
					if self.HasKey(str(key)):
						nodeKey = self.GetKey(f"node{key!s}")
					else:
						nodeKey = self.AddKey(Key(f"node{key!s}", AttributeContext.Node, str(key), AttributeTypes.String))
					newNode.AddData(Data(nodeKey, value))

				nodeGraph.AddNode(newNode)

			for edge in pyTSubgraph.IterateEdges():
				source = nodeGraph.GetNode(edge._source._id)
				target = nodeGraph.GetNode(edge._destination._id)

				newEdge = Edge(edge._id, source, target)
				newEdge.AddData(Data(edgeValue, edge._value))
				for key, value in edge._dict.items():
					if self.HasKey(str(key)):
						edgeKey = self.GetKey(f"edge{key!s}")
					else:
						edgeKey = self.AddKey(Key(f"edge{key!s}", AttributeContext.Edge, str(key), AttributeTypes.String))
					newEdge.AddData(Data(edgeKey, value))

				nodeGraph.AddEdge(newEdge)

		for subgraph in graph.Subgraphs:
			nodeGraph = Subgraph(subgraph.Name, "sg" + subgraph.Name)
			self._graph.AddSubgraph(nodeGraph)
			translateSubgraph(nodeGraph, subgraph)

		translateGraph(self._graph, graph)

	def FromTree(self, tree: pyToolingNode) -> None:
		self._graph._id = tree._id

		nodeValue = self.AddKey(Key("nodeValue", AttributeContext.Node, "value", AttributeTypes.String))

		rootNode = self._graph.AddNode(Node(tree._id))
		rootNode.AddData(Data(nodeValue, tree._value))

		for i, node in enumerate(tree.GetDescendants()):
			newNode = self._graph.AddNode(Node(node._id))
			newNode.AddData(Data(nodeValue, node._value))

			newEdge = self._graph.AddEdge(Edge(f"e{i}", newNode, self._graph.GetNode(node._parent._id)))

	def OpeningTag(self, indent: int = 0) -> str:
		return f"""\
{'  '*indent}<graphml xmlns="{self.xmlNS[None]}"
{'  '*indent}         xmlns:xsi="{self.xmlNS["xsi"]}"
{'  '*indent}         xsi:schemaLocation="{self.xsi["schemaLocation"]}">
"""

	def ClosingTag(self, indent: int = 0) -> str:
		return f"{'  '*indent}</graphml>\n"

	def ToStringLines(self, indent: int = 0) -> List[str]:
		lines = [self.OpeningTag(indent)]
		for key in self._keys.values():
			lines.extend(key.ToStringLines(indent + 1))
		lines.extend(self._graph.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines

	def WriteToFile(self, file: Path) -> None:
		with file.open("w", encoding="utf-8") as f:
			f.write(f"""<?xml version="1.0" encoding="utf-8"?>""")
			f.writelines(self.ToStringLines())
