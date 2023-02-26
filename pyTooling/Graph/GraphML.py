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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from enum import Enum, auto
from pathlib import Path
from typing import Any, List, Dict

from pyTooling.Decorators import export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Graph import Graph as pyToolingGraph
from pyTooling.Tree import Node as pyToolingNode


@export
class AttributeContext(Enum):
	Node = auto()
	Edge = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class AttributeTypes(Enum):
	String = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class EdgeDefault(Enum):
	Undirected = auto()
	Directed = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class ParsingOrder(Enum):
	NodesFirst = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class IDStyle(Enum):
	Canonical = auto()
	Free = auto()

	def __str__(self) -> str:
		return f"{self.name.lower()}"


@export
class Base(metaclass=ExtendedType, useSlots=True):
	@property
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
class Key(Base):
	_id: str
	_context: AttributeContext
	_attributeName: str
	_attributeType: AttributeTypes

	def __init__(self, identifier: str, context: AttributeContext, name: str, type: AttributeTypes):
		self._id = identifier
		self._context = context
		self._attributeName = name
		self._attributeType = type

	@property
	def ID(self) -> str:
		return self._id

	@property
	def Context(self) -> AttributeContext:
		return self._context

	@property
	def AttributeName(self) -> str:
		return self._attributeName

	@property
	def AttributeType(self) -> AttributeTypes:
		return self._attributeType

	@property
	def HasClosingTag(self) -> bool:
		return False

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<key id="{self._id}" for="{self._context}" attr.name="{self._attributeName}" attr.type="{self._attributeType}" />"""

	def ToStringLines(self, indent: int = 0) -> List[str]:
		return [self.Tag(indent)]


@export
class Data(Base):
	_key: Key
	_data: Any

	def __init__(self, key: Key, data: Any):
		self._key = key
		self._data = data

	@property
	def Key(self) -> Key:
		return self._key

	@property
	def Data(self) -> Any:
		return self._data

	@property
	def HasClosingTag(self) -> bool:
		return False

	def Tag(self, indent: int = 1) -> str:
		return f"""{'  '*indent}<data key="{self._key._id}">{self._data!s}</data>"""

	def ToStringLines(self, indent: int = 0) -> List[str]:
		return [self.Tag(indent)]


@export
class Node(Base):
	_id: str
	_data: List[Data]

	def __init__(self, identifier: str):
		self._id = identifier
		self._data = []

	@property
	def ID(self) -> str:
		return self._id

	@property
	def Data(self) -> List[Data]:
		return self._data

	@property
	def HasClosingTag(self) -> bool:
		return len(self._data) > 0

	def AddData(self, data: Data) -> Data:
		self._data.append(data)
		return data

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<node id="{self._id}" />"""

	def OpeningTag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<node id="{self._id}">"""

	def ClosingTag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}</node>"""

	def ToStringLines(self, indent: int = 0) -> List[str]:
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class Edge(Base):
	_id: str
	_source: Node
	_target: Node
	_data: List[Data]

	def __init__(self, identifier: str, source: Node, target: Node):
		self._id = identifier
		self._source = source
		self._target = target
		self._data = []

	@property
	def ID(self) -> str:
		return self._id

	@property
	def Source(self) -> Node:
		return self._source

	@property
	def Target(self) -> Node:
		return self._target

	@property
	def Data(self) -> List[Data]:
		return self._data

	@property
	def HasClosingTag(self) -> bool:
		return len(self._data) > 0

	def AddData(self, data: Data) -> Data:
		self._data.append(data)
		return data

	def Tag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}" />"""

	def OpeningTag(self, indent: int = 2) -> str:
		return f"""{'  '*indent}<edge id="{self._id}" source="{self._source._id}" target="{self._target._id}">"""

	def ClosingTag(self, indent: int = 2) -> str:
		return f"""{'  ' * indent}</edge>"""

	def ToStringLines(self, indent: int = 0) -> List[str]:
		if not self.HasClosingTag:
			return [self.Tag(indent)]

		lines = [self.OpeningTag(indent)]
		for data in self._data:
			lines.extend(data.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines


@export
class Graph(Base):
	_id: str
	_nodes: Dict[str, Node]
	_edges: Dict[str, Edge]
	_edgeDefault: EdgeDefault
	_parseOrder: ParsingOrder
	_nodeIDStyle: IDStyle
	_edgeIDStyle: IDStyle

	def __init__(self, identifier: str = None):
		self._id = identifier
		self._nodes = {}
		self._edges = {}
		self._edgeDefault = EdgeDefault.Directed
		self._parseOrder = ParsingOrder.NodesFirst
		self._nodeIDStyle = IDStyle.Free
		self._edgeIDStyle = IDStyle.Free

	@property
	def ID(self) -> str:
		return self._id

	@property
	def Nodes(self) -> Dict[str, Node]:
		return self._nodes

	@property
	def Edges(self) -> Dict[str, Edge]:
		return self._edges

	def AddNode(self, node: Node) -> Node:
		self._nodes[node._id] = node
		return node

	def GetNode(self, nodeName: str) -> Node:
		return self._nodes[nodeName]

	def AddEdge(self, edge: Edge) -> Edge:
		self._edges[edge._id] = edge
		return edge

	def OpeningTag(self, indent: int = 1) -> str:
		return f"""\
{'  '*indent}<graph id="{self._id}"
{'  '*indent}  edgedefault="{self._edgeDefault!s}"
{'  '*indent}  parse.nodes="{len(self._nodes)}"
{'  '*indent}  parse.edges="{len(self._edges)}"
{'  '*indent}  parse.order="{self._parseOrder!s}"
{'  '*indent}  parse.nodeids="{self._nodeIDStyle!s}"
{'  '*indent}  parse.edgeids="{self._edgeIDStyle!s}">"""

	def ClosingTag(self, indent: int = 1) -> str:
		return f"{'  '*indent}</graph>"

	def ToStringLines(self, indent: int = 0) -> List[str]:
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

	def __init__(self, identifier: str = "G"):
		super().__init__()

		self._graph = Graph(identifier)
		self._keys = {}

	@property
	def Graph(self) -> Graph:
		return self._graph

	@property
	def Keys(self) -> Dict[str, Key]:
		return self._keys

	def AddKey(self, key: Key) -> Key:
		self._keys[key._id] = key
		return key

	def GetKey(self, keyName: str) -> Key:
		return self._keys[keyName]

	def FromGraph(self, graph: pyToolingGraph):
		self._graph._id = graph._name

		nodeValue = self.AddKey(Key("nodeValue", AttributeContext.Node, "value", AttributeTypes.String))
		edgeValue = self.AddKey(Key("edgeValue", AttributeContext.Edge, "value", AttributeTypes.String))

		for vertex in graph.IterateVertices():
			newNode = Node(vertex._id)
			newNode.AddData(Data(nodeValue, vertex._value))

			self._graph.AddNode(newNode)

		for edge in graph.IterateEdges():
			source = self._graph.GetNode(edge._source._id)
			target = self._graph.GetNode(edge._destination._id)

			newEdge = Edge(edge._id, source, target)
			newEdge.AddData(Data(edgeValue, edge._value))

			self._graph.AddEdge(newEdge)

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
{'  '*indent}         xsi:schemaLocation="{self.xsi["schemaLocation"]}">"""

	def ClosingTag(self, indent: int = 0) -> str:
		return f"{'  '*indent}</graphml>"

	def ToStringLines(self, indent: int = 0) -> List[str]:
		lines = [self.OpeningTag(indent)]
		for key in self._keys.values():
			lines.extend(key.ToStringLines(indent + 1))
		lines.extend(self._graph.ToStringLines(indent + 1))
		lines.append(self.ClosingTag(indent))

		return lines

	def WriteToFile(self, file: Path) -> None:
		with file.open("w") as f:
			f.write(f"""<?xml version="1.0" encoding="utf-8"?>""")
			f.writelines(self.ToStringLines())
