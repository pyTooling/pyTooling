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
A data model to write Graphviz graphs in the DOT language.

The model is the counterpart of :mod:`pyTooling.Graph.GraphML`: a :class:`Graph` holds nodes, edges and subgraphs, every
element carries attributes, and the graph is written as DOT text. Nothing is laid out or drawn here - that is what
Graphviz' :program:`dot` does, or :mod:`sphinx.ext.graphviz` in a documentation.

.. rubric:: Attribute values

An attribute value is written by its type: a :class:`str` as a quoted DOT string, an :class:`int` or :class:`float` as
a number, a :class:`bool` as ``true`` or ``false``, an :class:`HTMLLabel` in angle brackets, and a :class:`RecordLabel`
as the label of a ``record`` node. Quoting and escaping happen there and nowhere else, so a caller passes plain text.

.. seealso::

   `The DOT Language <https://graphviz.org/doc/info/lang.html>`__
      |rarr| The grammar this module writes.
   `Attributes <https://graphviz.org/doc/info/attrs.html>`__
      |rarr| The attributes a graph, a node and an edge can carry.
   :mod:`pyTooling.Graph.GraphML`
      |rarr| Writing a graph as a GraphML document.
"""
from __future__            import annotations

from enum                  import Enum
from html                  import escape as html_escape
from itertools             import count
from pathlib               import Path
from typing                import Iterator, Mapping, Optional as Nullable, Sequence, Union

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Graph       import Graph as pyToolingGraph, Subgraph as pyToolingSubgraph, Vertex
from pyTooling.Graph       import Edge as pyToolingEdge, Link as pyToolingLink
from pyTooling.Tree        import Node as pyToolingNode


__all__ = ["AttributeValue", "RecordField"]


@export
def quote(text: str) -> str:
	"""
	Quote a text as a DOT string.

	A backslash, a double quote and a line break are escaped, so the drawing shows the text as it was given - a
	backslash doesn't start one of Graphviz' escape sequences like ``\\l``.

	:param text:        The text to quote.
	:returns:           The text in double quotes.
	:raises ValueError: If parameter 'text' is None.
	:raises TypeError:  If parameter 'text' is not a string.
	"""
	if text is None:
		raise ValueError("Parameter 'text' is None.")
	elif not isinstance(text, str):
		ex = TypeError("Parameter 'text' is not of type 'str'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(text)}'.")
		raise ex

	return '"' + text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


@export
class GraphKind(Enum):
	"""Enumeration of the kinds of DOT graph, by the keyword declaring the graph and the operator writing an edge."""
	Directed =   ("digraph", "->")  #: A directed graph: ``digraph``, an edge is written ``a -> b``.
	Undirected = ("graph",   "--")  #: An undirected graph: ``graph``, an edge is written ``a -- b``.

	@readonly
	def Keyword(self) -> str:
		"""
		Read-only property to return the keyword declaring a graph of this kind.

		:returns: ``digraph`` or ``graph``.
		"""
		return self.value[0]

	@readonly
	def EdgeOperator(self) -> str:
		"""
		Read-only property to return the operator connecting the two nodes of an edge in a graph of this kind.

		:returns: ``->`` or ``--``.
		"""
		return self.value[1]


@export
class HTMLLabel(metaclass=ExtendedType, slots=True):
	"""
	An HTML-like label, written in angle brackets instead of quotes.

	The markup is written as given. Text placed into it has to be escaped with :meth:`Escape` first.
	"""
	_markup: str  #: The label's markup, without the enclosing angle brackets.

	def __init__(self, markup: str) -> None:
		"""
		Initialize an HTML-like label.

		:param markup:      The label's markup, without the enclosing angle brackets.
		:raises ValueError: If parameter 'markup' is None.
		:raises TypeError:  If parameter 'markup' is not a string.
		"""
		if markup is None:
			raise ValueError("Parameter 'markup' is None.")
		elif not isinstance(markup, str):
			ex = TypeError("Parameter 'markup' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(markup)}'.")
			raise ex

		self._markup = markup

	@readonly
	def Markup(self) -> str:
		"""
		Read-only property to access the label's markup (:attr:`_markup`).

		:returns: The markup, without the enclosing angle brackets.
		"""
		return self._markup

	@staticmethod
	def Escape(text: str) -> str:
		"""
		Escape the characters HTML gives a meaning to: ``&``, ``<`` and ``>``.

		:param text:        The text to escape.
		:returns:           The text, safe to place into the label's markup.
		:raises ValueError: If parameter 'text' is None.
		:raises TypeError:  If parameter 'text' is not a string.
		"""
		if text is None:
			raise ValueError("Parameter 'text' is None.")
		elif not isinstance(text, str):
			ex = TypeError("Parameter 'text' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(text)}'.")
			raise ex

		return html_escape(text, quote=False)

	def __str__(self) -> str:
		"""
		Return the label as DOT writes it.

		:returns: The markup in angle brackets.
		"""
		return f"<{self._markup}>"


RecordField = Union[str, Sequence[str], "RecordLabel"]
"""
A field of a :class:`RecordLabel`: a text, a sequence of rows written left-aligned in one field, or a nested record
label.
"""


@export
class RecordLabel(metaclass=ExtendedType, slots=True):
	"""
	The label of a ``record`` node: fields side by side, or - flipped - one below the other.

	Graphviz lays a record's fields out horizontally if the graph flows top to bottom, and vertically if it flows left
	to right (``rankdir=LR``). :attr:`Flipped` turns the outermost direction by 90 degrees, and a nested record label
	is always turned against the fields around it.

	A field's text is escaped, and a field of rows writes every row left-aligned. An empty sequence of rows is written
	as a single space, because an empty field would collapse.
	"""
	_fields:  list[RecordField]  #: The fields, in the order they are drawn.
	_flipped: bool               #: If ``True``, the outermost fields are laid out against the graph's direction.

	def __init__(self, fields: Sequence[RecordField], flipped: bool = False) -> None:
		"""
		Initialize a record label.

		:param fields:      The fields, in the order they are drawn.
		:param flipped:     Optional, if ``True``, the outermost fields are laid out against the graph's direction.
		                    Default: ``False``.
		:raises ValueError: If parameter 'fields' is None or empty.
		:raises TypeError:  If parameter 'fields' is not a sequence, or is a string.
		:raises ValueError: If a field is None.
		:raises TypeError:  If a field is not a string, a sequence of strings or a :class:`RecordLabel`. |br|
		                    The note lists the supported types.
		:raises ValueError: If parameter 'flipped' is None.
		:raises TypeError:  If parameter 'flipped' is not a boolean.
		"""
		if fields is None:
			raise ValueError("Parameter 'fields' is None.")
		elif isinstance(fields, str) or not isinstance(fields, Sequence):
			ex = TypeError("Parameter 'fields' is not a sequence ('list', 'tuple', ...).")
			ex.add_note(f"Got type '{getFullyQualifiedName(fields)}'.")
			raise ex
		elif len(fields) == 0:
			raise ValueError("Parameter 'fields' is empty.")

		for field in fields:
			if field is None:
				raise ValueError("Parameter 'fields' contains None.")
			elif isinstance(field, (str, RecordLabel)):
				continue
			elif isinstance(field, Sequence) and all(isinstance(row, str) for row in field):
				continue

			ex = TypeError("Parameter 'fields' contains a field of an unsupported type.")
			ex.add_note(f"Got type '{getFullyQualifiedName(field)}'.")
			ex.add_note("Supported types: str, a sequence of str, RecordLabel")
			raise ex

		if flipped is None:
			raise ValueError("Parameter 'flipped' is None.")
		elif not isinstance(flipped, bool):
			ex = TypeError("Parameter 'flipped' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(flipped)}'.")
			raise ex

		self._fields  = list(fields)
		self._flipped = flipped

	@readonly
	def Fields(self) -> list[RecordField]:
		"""
		Read-only property to access the label's fields (:attr:`_fields`).

		:returns: The fields, in the order they are drawn.
		"""
		return self._fields

	@readonly
	def Flipped(self) -> bool:
		"""
		Read-only property to access whether the outermost fields are laid out against the graph's direction
		(:attr:`_flipped`).

		:returns: ``True``, if the outermost fields are turned.
		"""
		return self._flipped

	@staticmethod
	def Escape(text: str) -> str:
		"""
		Escape the characters a record label gives a meaning to: ``\\``, ``{``, ``}``, ``|``, ``<``, ``>`` and ``"``.

		:param text:        The text to escape.
		:returns:           The text, safe to place into a field.
		:raises ValueError: If parameter 'text' is None.
		:raises TypeError:  If parameter 'text' is not a string.
		"""
		if text is None:
			raise ValueError("Parameter 'text' is None.")
		elif not isinstance(text, str):
			ex = TypeError("Parameter 'text' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(text)}'.")
			raise ex

		for character in ("\\", "{", "}", "|", "<", ">", '"'):
			text = text.replace(character, f"\\{character}")

		return text

	def _Content(self) -> str:
		"""
		Return the fields separated by ``|``, each field escaped and a nested record label in braces.

		:returns: The fields as a record label writes them, without the outermost braces.
		"""
		fields = []
		for field in self._fields:
			if isinstance(field, RecordLabel):
				fields.append(f"{{{field._Content()}}}")
			elif isinstance(field, str):
				fields.append(self.Escape(field))
			elif len(field) == 0:
				fields.append(" ")
			else:
				fields.append("".join(f"{self.Escape(row)}\\l" for row in field))

		return "|".join(fields)

	def __str__(self) -> str:
		"""
		Return the label as DOT writes it.

		:returns: The fields in double quotes, in braces if the label is flipped.
		"""
		content = self._Content()
		if self._flipped:
			content = f"{{{content}}}"

		return f'"{content}"'


AttributeValue = Union[str, int, float, bool, HTMLLabel, RecordLabel]
"""The types an attribute's value can have."""


@export
class Base(metaclass=ExtendedType, slots=True):
	"""
	Base-class of every element of a DOT graph: something carrying attributes.

	Attributes are read and written with dictionary syntax, ``node["shape"] = "box"``, and a value is checked when it is
	assigned, so writing the graph can't fail on one.
	"""
	_attributes: dict[str, AttributeValue]  #: Attributes of the element, by name.

	def __init__(self, attributes: Nullable[Mapping[str, AttributeValue]] = None) -> None:
		"""
		Initialize the element's attributes.

		:param attributes:  Optional, attributes of the element, by name.
		:raises TypeError:  If parameter 'attributes' is not a mapping.
		:raises ValueError: If an attribute's name is None or empty, or its value is None.
		:raises TypeError:  If an attribute's name is not a string, or its value is not of type :data:`AttributeValue`.
		"""
		self._attributes = {}
		if attributes is not None:
			if not isinstance(attributes, Mapping):
				ex = TypeError("Parameter 'attributes' is not a mapping ('dict', ...).")
				ex.add_note(f"Got type '{getFullyQualifiedName(attributes)}'.")
				raise ex

			for name, value in attributes.items():
				try:
					self[name] = value
				except (TypeError, ValueError) as ex:
					ex.add_note(f"Raised for attribute '{name}' of parameter 'attributes'.")
					raise

	@readonly
	def Attributes(self) -> dict[str, AttributeValue]:
		"""
		Read-only property to access the element's attributes (:attr:`_attributes`).

		:returns: The attributes, by name.
		"""
		return self._attributes

	def __getitem__(self, name: str) -> AttributeValue:
		"""
		Return the value of an attribute.

		:param name:      Name of the attribute.
		:returns:         The attribute's value.
		:raises KeyError: If the element has no such attribute.
		"""
		return self._attributes[name]

	def __setitem__(self, name: str, value: AttributeValue) -> None:
		"""
		Set the value of an attribute.

		:param name:        Name of the attribute.
		:param value:       The attribute's value.
		:raises ValueError: If parameter 'name' is None or empty.
		:raises TypeError:  If parameter 'name' is not a string.
		:raises ValueError: If parameter 'value' is None.
		:raises TypeError:  If parameter 'value' is not of type :data:`AttributeValue`. |br|
		                    The note lists the supported types.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex
		elif name == "":
			raise ValueError("Parameter 'name' is empty.")

		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif not isinstance(value, (str, int, float, bool, HTMLLabel, RecordLabel)):
			ex = TypeError("Parameter 'value' is not of a supported attribute type.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			ex.add_note("Supported types: str, int, float, bool, HTMLLabel, RecordLabel")
			raise ex

		self._attributes[name] = value

	def __delitem__(self, name: str) -> None:
		"""
		Remove an attribute.

		:param name:      Name of the attribute.
		:raises KeyError: If the element has no such attribute.
		"""
		del self._attributes[name]

	def __contains__(self, name: str) -> bool:
		"""
		Check if the element has an attribute.

		:param name: Name of the attribute.
		:returns:    ``True``, if the element has an attribute of that name.
		"""
		return name in self._attributes

	def __len__(self) -> int:
		"""
		Return the number of attributes.

		:returns: Number of attributes of the element.
		"""
		return len(self._attributes)

	@staticmethod
	def _FormatValue(value: AttributeValue) -> str:
		"""
		Return an attribute's value as DOT writes it.

		:param value: The value to write.
		:returns:     The value, quoted, as a number, as ``true``/``false``, or as the label it is.
		"""
		if isinstance(value, bool):
			return "true" if value else "false"
		elif isinstance(value, (int, float)):
			return str(value)
		elif isinstance(value, str):
			return quote(value)
		else:
			return str(value)

	def _AttributeList(self) -> str:
		"""
		Return the attributes as a DOT attribute list.

		:returns: The attributes in brackets, preceded by a space, or an empty string if there are none.
		"""
		if len(self._attributes) == 0:
			return ""

		return " [" + ", ".join(f"{name}={self._FormatValue(value)}" for name, value in self._attributes.items()) + "]"


@export
class DefaultAttributes(Base):
	"""
	The attributes every node or every edge of a graph starts with: a ``node [...]`` or ``edge [...]`` statement.
	"""
	_keyword: str  #: ``node`` or ``edge``, the keyword of the statement.

	def __init__(self, keyword: str) -> None:
		"""
		Initialize empty default attributes.

		:param keyword:     ``node`` or ``edge``, the keyword of the statement.
		:raises ValueError: If parameter 'keyword' is None.
		:raises TypeError:  If parameter 'keyword' is not a string.
		:raises ValueError: If parameter 'keyword' is neither ``node`` nor ``edge``.
		"""
		super().__init__()

		if keyword is None:
			raise ValueError("Parameter 'keyword' is None.")
		elif not isinstance(keyword, str):
			ex = TypeError("Parameter 'keyword' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keyword)}'.")
			raise ex
		elif keyword not in ("node", "edge"):
			raise ValueError("Parameter 'keyword' is neither 'node' nor 'edge'.")

		self._keyword = keyword

	def ToStringLines(self, indent: int = 1) -> list[str]:
		"""
		Render the defaults as DOT lines.

		:param indent: Optional, indentation level of the statement.
		:returns:      The statement as a line, or no line if there are no default attributes.
		"""
		if len(self._attributes) == 0:
			return []

		return [f"{'  ' * indent}{self._keyword}{self._AttributeList()};\n"]


@export
class Node(Base):
	"""A node of a DOT graph."""
	_identifier: str  #: Identifier of the node, which an edge names it by.

	def __init__(
		self,
		identifier: str,
		label: Nullable[Union[str, HTMLLabel, RecordLabel]] = None,
		attributes: Nullable[Mapping[str, AttributeValue]] = None
	) -> None:
		"""
		Initialize a node.

		:param identifier:  Identifier of the node, which an edge names it by.
		:param label:       Optional, the node's label. Graphviz shows the identifier, if there is none.
		:param attributes:  Optional, further attributes of the node, by name.
		:raises ValueError: If parameter 'identifier' is None or empty.
		:raises TypeError:  If parameter 'identifier' is not a string.
		:raises TypeError:  If parameter 'label' is not a string, :class:`HTMLLabel` or :class:`RecordLabel`.
		:raises ValueError: If parameters 'label' and 'attributes' both set a label.
		"""
		super().__init__(attributes)

		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex
		elif identifier == "":
			raise ValueError("Parameter 'identifier' is empty.")

		if label is not None:
			if not isinstance(label, (str, HTMLLabel, RecordLabel)):
				ex = TypeError("Parameter 'label' is not of type 'str', 'HTMLLabel' or 'RecordLabel'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(label)}'.")
				raise ex
			elif "label" in self._attributes:
				raise ValueError("Parameters 'label' and 'attributes' both set a label.")

			self._attributes["label"] = label

		self._identifier = identifier

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the node's identifier (:attr:`_identifier`).

		:returns: The identifier, which an edge names the node by.
		"""
		return self._identifier

	def ToStringLines(self, indent: int = 1) -> list[str]:
		"""
		Render the node as DOT lines.

		:param indent: Optional, indentation level of the statement.
		:returns:      The node statement as a line.
		"""
		return [f"{'  ' * indent}{quote(self._identifier)}{self._AttributeList()};\n"]


@export
class Edge(Base):
	"""An edge of a DOT graph, connecting a source node to a target node."""
	_source: Node  #: Node the edge starts at.
	_target: Node  #: Node the edge ends at.

	def __init__(self, source: Node, target: Node, attributes: Nullable[Mapping[str, AttributeValue]] = None) -> None:
		"""
		Initialize an edge.

		:param source:      Node the edge starts at.
		:param target:      Node the edge ends at.
		:param attributes:  Optional, further attributes of the edge, by name.
		:raises ValueError: If parameter 'source' is None.
		:raises TypeError:  If parameter 'source' is not a :class:`Node`.
		:raises ValueError: If parameter 'target' is None.
		:raises TypeError:  If parameter 'target' is not a :class:`Node`.
		"""
		super().__init__(attributes)

		for parameter, node in (("source", source), ("target", target)):
			if node is None:
				raise ValueError(f"Parameter '{parameter}' is None.")
			elif not isinstance(node, Node):
				ex = TypeError(f"Parameter '{parameter}' is not of type 'Node'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(node)}'.")
				raise ex

		self._source = source
		self._target = target

	@readonly
	def Source(self) -> Node:
		"""
		Read-only property to access the node the edge starts at (:attr:`_source`).

		:returns: The source node.
		"""
		return self._source

	@readonly
	def Target(self) -> Node:
		"""
		Read-only property to access the node the edge ends at (:attr:`_target`).

		:returns: The target node.
		"""
		return self._target

	def ToStringLines(self, kind: GraphKind = GraphKind.Directed, indent: int = 1) -> list[str]:
		"""
		Render the edge as DOT lines.

		:param kind:   Optional, kind of the graph, which decides the edge operator. Default: :attr:`GraphKind.Directed`.
		:param indent: Optional, indentation level of the statement.
		:returns:      The edge statement as a line.
		"""
		source = quote(self._source._identifier)
		target = quote(self._target._identifier)

		return [f"{'  ' * indent}{source} {kind.EdgeOperator} {target}{self._AttributeList()};\n"]


@export
class BaseGraph(Base):
	"""
	Base-class for everything that contains nodes, edges and subgraphs - a graph as well as a subgraph.

	Its own attributes are the graph's attributes, written as ``name=value;`` statements, and its default attributes
	are what every node and every edge starts with. The statements are written in this order: attributes, defaults,
	subgraphs, nodes, edges.
	"""
	_nodeDefaults: DefaultAttributes    #: Attributes every node starts with.
	_edgeDefaults: DefaultAttributes    #: Attributes every edge starts with.
	_subgraphs:    dict[str, Subgraph]  #: Subgraphs, by identifier.
	_nodes:        dict[str, Node]      #: Nodes, by identifier.
	_edges:        list[Edge]           #: Edges, in the order they were added.

	def __init__(self, attributes: Nullable[Mapping[str, AttributeValue]] = None) -> None:
		"""
		Initialize an empty graph.

		:param attributes: Optional, attributes of the graph, by name.
		"""
		super().__init__(attributes)

		self._nodeDefaults = DefaultAttributes("node")
		self._edgeDefaults = DefaultAttributes("edge")
		self._subgraphs    = {}
		self._nodes        = {}
		self._edges        = []

	@readonly
	def NodeDefaults(self) -> DefaultAttributes:
		"""
		Read-only property to access the attributes every node starts with (:attr:`_nodeDefaults`).

		:returns: The node defaults.
		"""
		return self._nodeDefaults

	@readonly
	def EdgeDefaults(self) -> DefaultAttributes:
		"""
		Read-only property to access the attributes every edge starts with (:attr:`_edgeDefaults`).

		:returns: The edge defaults.
		"""
		return self._edgeDefaults

	@readonly
	def Subgraphs(self) -> dict[str, Subgraph]:
		"""
		Read-only property to access the subgraphs (:attr:`_subgraphs`).

		:returns: Dictionary of subgraph identifiers and subgraphs.
		"""
		return self._subgraphs

	@readonly
	def Nodes(self) -> dict[str, Node]:
		"""
		Read-only property to access the nodes (:attr:`_nodes`).

		:returns: Dictionary of node identifiers and nodes.
		"""
		return self._nodes

	@readonly
	def Edges(self) -> list[Edge]:
		"""
		Read-only property to access the edges (:attr:`_edges`).

		:returns: The edges, in the order they were added.
		"""
		return self._edges

	def AddSubgraph(self, subgraph: Subgraph) -> Subgraph:
		"""
		Add a subgraph.

		:param subgraph:    The subgraph to add.
		:returns:           The added subgraph, so it can be used in the calling expression.
		:raises ValueError: If parameter 'subgraph' is None.
		:raises TypeError:  If parameter 'subgraph' is not a :class:`Subgraph`.
		:raises ValueError: If a subgraph with the same identifier was added before.
		"""
		if subgraph is None:
			raise ValueError("Parameter 'subgraph' is None.")
		elif not isinstance(subgraph, Subgraph):
			ex = TypeError("Parameter 'subgraph' is not of type 'Subgraph'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(subgraph)}'.")
			raise ex
		elif subgraph._identifier in self._subgraphs:
			raise ValueError(f"A subgraph '{subgraph._identifier}' was added before.")

		self._subgraphs[subgraph._identifier] = subgraph
		return subgraph

	def AddNode(self, node: Node) -> Node:
		"""
		Add a node.

		:param node:        The node to add.
		:returns:           The added node, so it can be used in the calling expression.
		:raises ValueError: If parameter 'node' is None.
		:raises TypeError:  If parameter 'node' is not a :class:`Node`.
		:raises ValueError: If a node with the same identifier was added before.
		"""
		if node is None:
			raise ValueError("Parameter 'node' is None.")
		elif not isinstance(node, Node):
			ex = TypeError("Parameter 'node' is not of type 'Node'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(node)}'.")
			raise ex
		elif node._identifier in self._nodes:
			raise ValueError(f"A node '{node._identifier}' was added before.")

		self._nodes[node._identifier] = node
		return node

	def AddEdge(self, edge: Edge) -> Edge:
		"""
		Add an edge.

		An edge may connect nodes of different subgraphs. Graphviz places the edge with the subgraph it is written in, so
		an edge between clusters belongs to the graph containing both.

		:param edge:        The edge to add.
		:returns:           The added edge, so it can be used in the calling expression.
		:raises ValueError: If parameter 'edge' is None.
		:raises TypeError:  If parameter 'edge' is not an :class:`Edge`.
		"""
		if edge is None:
			raise ValueError("Parameter 'edge' is None.")
		elif not isinstance(edge, Edge):
			ex = TypeError("Parameter 'edge' is not of type 'Edge'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(edge)}'.")
			raise ex

		self._edges.append(edge)
		return edge

	def GetNode(self, identifier: str) -> Node:
		"""
		Return the node with the given identifier.

		:param identifier:  Identifier of the node.
		:returns:           The node with that identifier.
		:raises ValueError: If parameter 'identifier' is None.
		:raises TypeError:  If parameter 'identifier' is not a string.
		:raises KeyError:   If no node has that identifier.
		"""
		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		return self._nodes[identifier]

	def HasNode(self, identifier: str) -> bool:
		"""
		Check if a node with the given identifier was added.

		:param identifier:  Identifier of the node.
		:returns:           ``True``, if such a node exists.
		:raises ValueError: If parameter 'identifier' is None.
		:raises TypeError:  If parameter 'identifier' is not a string.
		"""
		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		return identifier in self._nodes

	def _StatementLines(self, kind: GraphKind, indent: int) -> list[str]:
		"""
		Render the graph's statements: attributes, defaults, subgraphs, nodes and edges.

		:param kind:   Kind of the graph, which decides the edge operator.
		:param indent: Indentation level of the statements.
		:returns:      The statements as lines.
		"""
		lines = [f"{'  ' * indent}{name}={self._FormatValue(value)};\n" for name, value in self._attributes.items()]
		lines.extend(self._nodeDefaults.ToStringLines(indent))
		lines.extend(self._edgeDefaults.ToStringLines(indent))
		for subgraph in self._subgraphs.values():
			lines.extend(subgraph.ToStringLines(kind, indent))

		for node in self._nodes.values():
			lines.extend(node.ToStringLines(indent))

		for edge in self._edges:
			lines.extend(edge.ToStringLines(kind, indent))

		return lines


@export
class Subgraph(BaseGraph):
	"""
	A subgraph of a DOT graph.

	A subgraph whose identifier starts with ``cluster`` is a **cluster**: Graphviz draws its nodes together, inside a
	box, and its attributes like ``label`` and ``style`` apply to that box.
	"""
	_identifier: str  #: Identifier of the subgraph.

	def __init__(self, identifier: str, attributes: Nullable[Mapping[str, AttributeValue]] = None) -> None:
		"""
		Initialize an empty subgraph.

		:param identifier:  Identifier of the subgraph. It starts with ``cluster`` for a cluster.
		:param attributes:  Optional, further attributes of the subgraph, by name.
		:raises ValueError: If parameter 'identifier' is None or empty.
		:raises TypeError:  If parameter 'identifier' is not a string.
		"""
		super().__init__(attributes)

		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex
		elif identifier == "":
			raise ValueError("Parameter 'identifier' is empty.")

		self._identifier = identifier

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the subgraph's identifier (:attr:`_identifier`).

		:returns: The identifier of the subgraph.
		"""
		return self._identifier

	@readonly
	def IsCluster(self) -> bool:
		"""
		Read-only property to return whether Graphviz draws the subgraph as a cluster.

		:returns: ``True``, if the identifier starts with ``cluster``.
		"""
		return self._identifier.startswith("cluster")

	def ToStringLines(self, kind: GraphKind = GraphKind.Directed, indent: int = 1) -> list[str]:
		"""
		Render the subgraph as DOT lines.

		:param kind:   Optional, kind of the graph, which decides the edge operator. Default: :attr:`GraphKind.Directed`.
		:param indent: Optional, indentation level of the subgraph statement.
		:returns:      The subgraph statement and its statements as lines.
		"""
		lines = [f"{'  ' * indent}subgraph {quote(self._identifier)} {{\n"]
		lines.extend(self._StatementLines(kind, indent + 1))
		lines.append(f"{'  ' * indent}}}\n")

		return lines


@export
class Graph(BaseGraph):
	"""
	A DOT graph - the document Graphviz reads.

	Its kind decides whether it is a ``digraph`` or a ``graph``, and a **strict** graph merges multiple edges between
	the same two nodes into one.
	"""
	_identifier: Nullable[str]  #: Identifier of the graph, which Graphviz uses as the drawing's name.
	_kind:       GraphKind      #: Directed or undirected.
	_strict:     bool           #: If ``True``, multiple edges between the same two nodes are merged.

	def __init__(
		self,
		identifier: Nullable[str] = None,
		kind: GraphKind = GraphKind.Directed,
		strict: bool = False,
		attributes: Nullable[Mapping[str, AttributeValue]] = None
	) -> None:
		"""
		Initialize an empty graph.

		:param identifier:  Optional, identifier of the graph, which Graphviz uses as the drawing's name.
		:param kind:        Optional, kind of the graph. Default: :attr:`GraphKind.Directed`.
		:param strict:      Optional, if ``True``, multiple edges between the same two nodes are merged. Default:
		                    ``False``.
		:param attributes:  Optional, further attributes of the graph, by name, e.g. ``{"rankdir": "LR"}``.
		:raises TypeError:  If parameter 'identifier' is not a string.
		:raises ValueError: If parameter 'kind' is None.
		:raises TypeError:  If parameter 'kind' is not a :class:`GraphKind`.
		:raises ValueError: If parameter 'strict' is None.
		:raises TypeError:  If parameter 'strict' is not a boolean.
		"""
		super().__init__(attributes)

		if identifier is not None and not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		if kind is None:
			raise ValueError("Parameter 'kind' is None.")
		elif not isinstance(kind, GraphKind):
			ex = TypeError("Parameter 'kind' is not of type 'GraphKind'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(kind)}'.")
			raise ex

		if strict is None:
			raise ValueError("Parameter 'strict' is None.")
		elif not isinstance(strict, bool):
			ex = TypeError("Parameter 'strict' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(strict)}'.")
			raise ex

		self._identifier = identifier
		self._kind       = kind
		self._strict     = strict

	@readonly
	def Identifier(self) -> Nullable[str]:
		"""
		Read-only property to access the graph's identifier (:attr:`_identifier`).

		:returns: The identifier, or ``None`` if the graph is anonymous.
		"""
		return self._identifier

	@readonly
	def Kind(self) -> GraphKind:
		"""
		Read-only property to access the graph's kind (:attr:`_kind`).

		:returns: Directed or undirected.
		"""
		return self._kind

	@readonly
	def Strict(self) -> bool:
		"""
		Read-only property to access whether multiple edges between the same two nodes are merged (:attr:`_strict`).

		:returns: ``True``, if the graph is strict.
		"""
		return self._strict

	@staticmethod
	def _Identifier(identifier: object, used: set[str], counter: Iterator[int]) -> str:
		"""
		Return an element's identifier: its ID as text, or - without an ID - a generated one no other element uses.

		:param identifier: The element's ID, or ``None``.
		:param used:       Identifiers used so far, which a generated identifier is added to.
		:param counter:    Counter numbering the generated identifiers.
		:returns:          The identifier.
		"""
		if identifier is not None:
			return str(identifier)

		while (candidate := f"vertex{next(counter)}") in used:
			pass

		used.add(candidate)
		return candidate

	def _ConvertVertex(self, vertex: Vertex, identifier: str) -> Node:
		"""
		Return the node a vertex of a :class:`pyTooling.Graph.Graph` becomes.

		The node is labelled with the vertex' value. A vertex without a value shows its ID, and one without an ID either
		gets an empty label rather than its generated identifier. A derived class overrides this method to add labels or
		attributes.

		:param vertex:     The vertex to convert.
		:param identifier: Identifier of the node: the vertex' ID, or a generated one.
		:returns:          The node.
		"""
		if vertex._value is not None:
			return Node(identifier, str(vertex._value))
		elif vertex._id is None:
			return Node(identifier, "")

		return Node(identifier)

	def _ConvertEdge(self, edge: pyToolingEdge, source: Node, target: Node) -> Edge:
		"""
		Return the edge an edge of a :class:`pyTooling.Graph.Graph` becomes, labelled with the edge's value.

		A derived class overrides this method to add labels or attributes.

		:param edge:   The edge to convert.
		:param source: Node the converted edge's source vertex became.
		:param target: Node the converted edge's destination vertex became.
		:returns:      The edge.
		"""
		if edge._value is not None:
			return Edge(source, target, {"label": str(edge._value)})

		return Edge(source, target)

	def _ConvertLink(self, link: pyToolingLink, source: Node, target: Node) -> Edge:
		"""
		Return the edge a link between two subgraphs of a :class:`pyTooling.Graph.Graph` becomes: dashed, and labelled
		with the link's value.

		A derived class overrides this method to add labels or attributes.

		:param link:   The link to convert.
		:param source: Node the link's source vertex became.
		:param target: Node the link's destination vertex became.
		:returns:      The edge.
		"""
		if link._value is not None:
			return Edge(source, target, {"style": "dashed", "label": str(link._value)})

		return Edge(source, target, {"style": "dashed"})

	def _ConvertSubgraph(self, subgraph: pyToolingSubgraph, identifier: str) -> Subgraph:
		"""
		Return the cluster a subgraph of a :class:`pyTooling.Graph.Graph` becomes, labelled with the subgraph's name.

		A derived class overrides this method to add labels or attributes.

		:param subgraph:   The subgraph to convert.
		:param identifier: Identifier of the cluster.
		:returns:          The cluster, still empty.
		"""
		if subgraph._name is not None:
			return Subgraph(identifier, {"label": subgraph._name})

		return Subgraph(identifier)

	def _ConvertTreeNode(self, node: pyToolingNode, identifier: str) -> Node:
		"""
		Return the node a node of a :class:`pyTooling.Tree.Node` tree becomes.

		The node is labelled like a vertex in :meth:`_ConvertVertex`. A derived class overrides this method to add labels
		or attributes.

		:param node:       The tree node to convert.
		:param identifier: Identifier of the node: the tree node's ID, or a generated one.
		:returns:          The node.
		"""
		if node._value is not None:
			return Node(identifier, str(node._value))
		elif node._id is None:
			return Node(identifier, "")

		return Node(identifier)

	def FromGraph(self, graph: pyToolingGraph) -> None:
		"""
		Fill this graph from a :class:`pyTooling.Graph.Graph`.

		Every subgraph becomes a cluster of its vertices, every vertex a node and every edge an edge, in the graph or in
		the cluster they belong to. A link between two subgraphs becomes an edge of this graph. A vertex without an ID
		gets a generated identifier, which no vertex with an ID has. Subgraphs are converted in the order of their names,
		so the same graph is always written the same way.

		What an element becomes is decided by :meth:`_ConvertVertex`, :meth:`_ConvertEdge`, :meth:`_ConvertLink` and
		:meth:`_ConvertSubgraph`, which a derived class overrides. Without an identifier of its own, this graph takes the
		graph's name.

		:param graph:       The graph to convert.
		:raises ValueError: If parameter 'graph' is None.
		:raises TypeError:  If parameter 'graph' is not a :class:`pyTooling.Graph.Graph`.
		"""
		if graph is None:
			raise ValueError("Parameter 'graph' is None.")
		elif not isinstance(graph, pyToolingGraph):
			ex = TypeError("Parameter 'graph' is not of type 'pyTooling.Graph.Graph'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(graph)}'.")
			raise ex

		if self._identifier is None:
			self._identifier = graph._name

		subgraphs = sorted(graph.Subgraphs, key=lambda subgraph: "" if subgraph._name is None else subgraph._name)
		vertices  = list(graph.IterateVertices())
		for subgraph in subgraphs:
			vertices += subgraph.IterateVertices()

		used    = {str(vertex._id) for vertex in vertices if vertex._id is not None}
		counter = count(1)
		nodes: dict[int, Node] = {}

		clusters = []
		for index, subgraph in enumerate(subgraphs, start=1):
			cluster = self.AddSubgraph(self._ConvertSubgraph(subgraph, f"cluster{index}"))
			clusters.append(cluster)
			for vertex in subgraph.IterateVertices():
				nodes[id(vertex)] = cluster.AddNode(self._ConvertVertex(vertex, self._Identifier(vertex._id, used, counter)))

		for vertex in graph.IterateVertices():
			nodes[id(vertex)] = self.AddNode(self._ConvertVertex(vertex, self._Identifier(vertex._id, used, counter)))

		for cluster, subgraph in zip(clusters, subgraphs):
			for edge in subgraph.IterateEdges():
				cluster.AddEdge(self._ConvertEdge(edge, nodes[id(edge._source)], nodes[id(edge._destination)]))

		for edge in graph.IterateEdges():
			self.AddEdge(self._ConvertEdge(edge, nodes[id(edge._source)], nodes[id(edge._destination)]))

		# a link is known to both subgraphs it connects
		converted: set[int] = set()
		for subgraph in subgraphs:
			for link in subgraph.IterateLinks():
				if id(link) not in converted:
					converted.add(id(link))
					self.AddEdge(self._ConvertLink(link, nodes[id(link._source)], nodes[id(link._destination)]))

	def FromTree(self, tree: pyToolingNode) -> None:
		"""
		Fill this graph from a tree of :class:`pyTooling.Tree.Node`.

		Every tree node becomes a node, connected to its parent by an edge from parent to child. A tree node without an
		ID gets a generated identifier, which no tree node with an ID has.

		What a tree node becomes is decided by :meth:`_ConvertTreeNode`, which a derived class overrides. Without an
		identifier of its own, this graph takes the root's ID.

		:param tree:        The root of the tree to convert.
		:raises ValueError: If parameter 'tree' is None.
		:raises TypeError:  If parameter 'tree' is not a :class:`pyTooling.Tree.Node`.
		"""
		if tree is None:
			raise ValueError("Parameter 'tree' is None.")
		elif not isinstance(tree, pyToolingNode):
			ex = TypeError("Parameter 'tree' is not of type 'pyTooling.Tree.Node'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(tree)}'.")
			raise ex

		if self._identifier is None and tree._id is not None:
			self._identifier = str(tree._id)

		treeNodes  = [tree]
		treeNodes += tree.GetDescendants()
		used       = {str(node._id) for node in treeNodes if node._id is not None}
		counter    = count(1)
		nodes: dict[int, Node] = {}

		for treeNode in treeNodes:
			node = self.AddNode(self._ConvertTreeNode(treeNode, self._Identifier(treeNode._id, used, counter)))
			nodes[id(treeNode)] = node
			if treeNode is not tree:
				self.AddEdge(Edge(nodes[id(treeNode._parent)], node))

	def ToStringLines(self, indent: int = 0) -> list[str]:
		"""
		Render the graph as DOT lines.

		:param indent: Optional, indentation level of the graph statement.
		:returns:      The graph and its statements as lines.
		"""
		head = f"{'strict ' if self._strict else ''}{self._kind.Keyword}"
		if self._identifier is not None:
			head += f" {quote(self._identifier)}"

		lines = [f"{'  ' * indent}{head} {{\n"]
		lines.extend(self._StatementLines(self._kind, indent + 1))
		lines.append(f"{'  ' * indent}}}\n")

		return lines

	def WriteToFile(self, file: Path) -> None:
		"""
		Write the graph as a DOT file.

		:param file:        Path of the file to write.
		:raises ValueError: If parameter 'file' is None.
		:raises TypeError:  If parameter 'file' is not a :class:`~pathlib.Path`.
		"""
		if file is None:
			raise ValueError("Parameter 'file' is None.")
		elif not isinstance(file, Path):
			ex = TypeError("Parameter 'file' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(file)}'.")
			raise ex

		with file.open("w", encoding="utf-8") as f:
			f.writelines(self.ToStringLines())

	def __str__(self) -> str:
		"""
		Return the graph as DOT text.

		:returns: The graph in the DOT language.
		"""
		return "".join(self.ToStringLines())
