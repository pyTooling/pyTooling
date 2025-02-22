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
A data model to write out GraphML XML files.

.. seealso::

   * http://graphml.graphdrawing.org/primer/graphml-primer.html
"""
from enum    import Enum, auto
from pathlib import Path
from typing  import Any, List, Dict, Union, Optional as Nullable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Graph       import Graph as pyToolingGraph, Subgraph as pyToolingSubgraph
	from pyTooling.Tree        import Node as pyToolingNode
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Graph.GraphML] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, mixin
		from Graph               import Graph as pyToolingGraph, Subgraph as pyToolingSubgraph
		from Tree                import Node as pyToolingNode
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Graph.GraphML] Could not import directly!")
		raise ex


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
		return f"{self.name.lower()}"


@export
class EdgeDefault(Enum):
	"""An enumeration describing the default edge direction."""
	Undirected = auto()
	Directed = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class ParsingOrder(Enum):
	"""An enumeration describing the parsing order of the graph's representation."""
	NodesFirst = auto()     #: First, all nodes are given, then followed by all edges.
	AdjacencyList = auto()
	Free = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class IDStyle(Enum):
	"""An enumeration describing the style of identifiers (IDs)."""
	Canonical = auto()
	Free = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class Base(metaclass=ExtendedType, slots=True):
	"""
	Base-class for all GraphML data model classes.
	"""
	@readonly
	def HasClosingTag(self) -> bool:
		return True

	def Tag(self, indent: int = 0) -> str:
		raise NotImplementedError()

	def OpeningTag(self, indent: int = 0) -> str:
		raise NotImplementedError()

	def ClosingTag(self, indent: int = 0) -> str:
		raise NotImplementedError()

	def ToStringLines(self, indent: int = 0) -> List[str]:
		raise NotImplementedError()


@export
class BaseWithID(Base):
	_id: str

	def __init__(self, identifier: str) -> None:
		super().__init__()
		self._id = identifier

	@readonly
	def ID(self) -> str:
		return self._id


@export
class BaseWithData(BaseWithID):
	_data: List['Data']

	def __init__(self, identifier: str) -> None:
		super().__init__(identifier)

		self._data = []

	@readonly
	def Data(self) -> List['Data']:
		return self._data

	def AddData(self, data: Data) -> Data:
		self._data.append(data)
		return data


@export
class Key(BaseWithID):
	_context: AttributeContext
	_attributeName: str
	_attributeType: AttributeTypes

	def __init__(self, identifier: str, context: AttributeContext, name: str, type: AttributeTypes) -> None:
		super().__init__(identifier)

		self._context = context
		self._attributeName = name
		self._attributeType = type

	@readonly
	def Context(self) -> AttributeContext:
		return self._context

	@readonly
	def AttributeName(self) -> str:
		return self._attributeName

	@readonly
	def AttributeType(self) -> AttributeTypes:
		return self._attributeType

	@readonly
	def HasClosingTag(self) -> bool:
		return False

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<key id="{self._id}" for="{self._context}" attr.name="{self._attributeName}" attr.type="{self._attributeType}" />\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		return [self.Tag(indent)]


@export
class Data(Base):
	_key: Key
	_data: Any

	def __init__(self, key: Key, data: Any) -> None:
		super().__init__()

		self._key = key
		self._data = data

	@readonly
	def Key(self) -> Key:
		return self._key

	@readonly
	def Data(self) -> Any:
		return self._data

	@readonly
	def HasClosingTag(self) -> bool:
		return False

	def Tag(self, indent: int = 2) -> str:
		data = str(self._data)
		data = data.replace("&", "&amp;")
		data = data.replace("<", "&lt;")
		data = data.replace(">", "&gt;")
		data = data.replace("\n", "\\n")
		return f"""{'  '*indent}<data key="{self._key._id}">{data}</data>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		return [self.Tag(indent)]


@export
class Node(BaseWithData):
	def __init__(self, identifier: str) -> None:
		super().__init__(identifier)

	@readonly
	def HasClosingTag(self) -> bool:
		return len(self._data) > 0

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<node id="{self._id}" />\n"""

	def OpeningTag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<node id="{self._id}">\n"""

	def ClosingTag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}</node>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class Edge(BaseWithData):
	_source: Node
	_target: Node

	def __init__(self, identifier: str, source: Node, target: Node) -> None:
		super().__init__(identifier)

		self._source = source
		self._target = target

	@readonly
	def Source(self) -> Node:
		return self._source

	@readonly
	def Target(self) -> Node:
		return self._target

	@readonly
	def HasClosingTag(self) -> bool:
		return len(self._data) > 0

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}" />\n"""

	def OpeningTag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}">\n"""

	def ClosingTag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}</edge>\n"""

	def ToStringLines(self, indent: int = 2) -> List[str]:
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class BaseGraph(BaseWithData, mixin=True):
	_subgraphs: Dict[str, 'Subgraph']
	_nodes: Dict[str, Node]
	_edges: Dict[str, Edge]
	_edgeDefault: EdgeDefault
	_parseOrder: ParsingOrder
	_nodeIDStyle: IDStyle
	_edgeIDStyle: IDStyle

	def __init__(self, identifier: Nullable[str] = None) -> None:
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
		return self._subgraphs

	@readonly
	def Nodes(self) -> Dict[str, Node]:
		return self._nodes

	@readonly
	def Edges(self) -> Dict[str, Edge]:
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
	_document: 'GraphMLDocument'
	_ids: Dict[str, Union[Node, Edge, 'Subgraph']]

	def __init__(self, document: 'GraphMLDocument', identifier: str) -> None:
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
	_subgraphID: str
	_root:       Nullable[Graph]

	def __init__(self, nodeIdentifier: str, graphIdentifier: str) -> None:
		super().__init__(nodeIdentifier)
		BaseGraph.__init__(self, nodeIdentifier)

		self._subgraphID = graphIdentifier
		self._root = None

	@readonly
	def RootGraph(self) -> Graph:
		return self._root

	@readonly
	def SubgraphID(self) -> str:
		return self._subgraphID

	@readonly
	def HasClosingTag(self) -> bool:
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
	xmlNS = {
		None:  "http://graphml.graphdrawing.org/xmlns",
		"xsi": "http://www.w3.org/2001/XMLSchema-instance"
	}
	xsi = {
		"schemaLocation": "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
	}

	_graph: Graph
	_keys: Dict[str, Key]

	def __init__(self, identifier: str = "G") -> None:
		super().__init__()

		self._graph = Graph(self, identifier)
		self._keys = {}

	@readonly
	def Graph(self) -> BaseGraph:
		return self._graph

	@readonly
	def Keys(self) -> Dict[str, Key]:
		return self._keys

	def AddKey(self, key: Key) -> Key:
		self._keys[key._id] = key
		return key

	def GetKey(self, keyName: str) -> Key:
		return self._keys[keyName]

	def HasKey(self, keyName: str) -> bool:
		return keyName in self._keys

	def FromGraph(self, graph: pyToolingGraph):
		document = self
		self._graph._id = graph._name

		nodeValue = self.AddKey(Key("nodeValue", AttributeContext.Node, "value", AttributeTypes.String))
		edgeValue = self.AddKey(Key("edgeValue", AttributeContext.Edge, "value", AttributeTypes.String))

		def translateGraph(rootGraph: Graph, pyTGraph: pyToolingGraph):
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

	def FromTree(self, tree: pyToolingNode):
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
