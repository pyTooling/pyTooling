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
from pathlib               import Path
from typing                import Mapping, Optional as Nullable, Sequence, Union

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType


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
