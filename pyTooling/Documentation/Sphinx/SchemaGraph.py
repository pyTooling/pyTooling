# ==================================================================================================================== #
#             _____           _ _               ____                                        _        _   _             #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___   ___ _   _ _ __ ___   ___ _ __ | |_ __ _| |_(_) ___  _ __  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ / __| | | | '_ ` _ \ / _ \ '_ \| __/ _` | __| |/ _ \| '_ \ #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | (_) | (__| |_| | | | | | |  __/ | | | || (_| | |_| | (_) | | | |#
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___/ \___|\__,_|_| |_| |_|\___|_| |_|\__\__,_|\__|_|\___/|_| |_|#
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
The language-neutral half of drawing a schema as a Graphviz graph in a Sphinx document.

:class:`DotGraph` assembles the graph in the DOT language, and :class:`SchemaGraph` is the directive's base-class: its
argument becomes a path, the file becomes a build dependency, and the DOT is handed to :mod:`sphinx.ext.graphviz`. A
schema language adds a module reading its schemas into a :class:`DotGraph`, and a subclass naming the directive.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx.XSDSchemaGraph`
      |rarr| The ``xsd-graph`` directive, drawing an XML schema.
   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension this belongs to, and what else it brings.
"""
from __future__                                import annotations

from pathlib                                   import Path
from typing                                    import Any, Iterable, Sequence

from docutils                                  import nodes
from sphinx.ext.graphviz                       import figure_wrapper, graphviz

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.Documentation.Sphinx.Directives import BaseDirective, strip


__all__ = ["GRAPH_ATTRIBUTES"]

#: Attributes every schema graph is drawn with, so two diagrams in one document look alike.
GRAPH_ATTRIBUTES = (
	"rankdir=LR;",
	"nodesep=0.4;",
	'node [shape=record, fontname="sans-serif", fontsize=10];',
	'edge [fontname="sans-serif", fontsize=9];',
)


@export
class DotGraph(metaclass=ExtendedType, slots=True):
	"""
	A Graphviz graph in the DOT language, assembled statement by statement.

	A renderer states nodes and edges; where the graph flows, how a record is shaped and which fonts it uses are
	:data:`GRAPH_ATTRIBUTES` and belong to every schema graph alike. Attribute values are quoted without exception,
	which is always legal in DOT and saves a caller from deciding per value.
	"""

	_name:       str        #: Name of the graph, which Graphviz uses as the drawing's identifier.
	_statements: list[str]  #: The statements written so far, one per line, already indented.

	def __init__(self, name: str = "schema") -> None:
		"""
		Initialize an empty graph carrying the shared attributes.

		:param name:        Optional, the graph's name.
		:raises ValueError: If parameter 'name' is None.
		:raises TypeError:  If parameter 'name' is not a string.
		"""
		if name is None:
			raise ValueError("Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name = name
		self._statements = [f"\t{attribute}" for attribute in GRAPH_ATTRIBUTES]
		self.AddSeparator()

	@staticmethod
	def EscapeLabel(text: str) -> str:
		"""
		Escape the characters a Graphviz record label gives a meaning to.

		:param text: The text to escape.
		:returns:    The text, safe to put into a record label.
		"""
		for character in ("\\", "{", "}", "|", "<", ">", '"'):
			text = text.replace(character, f"\\{character}")

		return text

	@classmethod
	def _Compartment(cls, rows: Sequence[str]) -> str:
		"""
		Join the rows of one record compartment, left-aligned.

		:param rows: The rows to join, unescaped.
		:returns:    The compartment's content, or a single space when there are no rows - an empty compartment
		             collapses, which makes the records of a graph differently shaped.
		"""
		if len(rows) == 0:
			return " "

		return "".join(f"{cls.EscapeLabel(row)}\\l" for row in rows)

	@staticmethod
	def _Attributes(attributes: dict[str, str]) -> str:
		"""
		Render an attribute list, quoting every value.

		:param attributes: The attributes to render, keyed by name.
		:returns:          The attribute list in brackets, or an empty string when there are none.
		"""
		if len(attributes) == 0:
			return ""

		return "[" + ", ".join(f'{name}="{value}"' for name, value in attributes.items()) + "]"

	def AddSeparator(self) -> None:
		"""Add a blank line, so the generated DOT reads in the groups it was written in."""
		self._statements.append("")

	def AddNode(self, identifier: str, label: str, **attributes: str) -> None:
		"""
		Add a node.

		:param identifier:  Identifier of the node, which an edge names it by.
		:param label:       The node's label, already escaped.
		:param attributes:  Further attributes of the node.
		:raises ValueError: If parameter 'identifier' or 'label' is None.
		:raises TypeError:  If parameter 'identifier' or 'label' is not a string.
		"""
		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex
		if label is None:
			raise ValueError("Parameter 'label' is None.")
		elif not isinstance(label, str):
			ex = TypeError("Parameter 'label' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(label)}'.")
			raise ex

		nodeAttributes = {"label": label}
		nodeAttributes.update(attributes)

		self._statements.append(f'\t"{identifier}" {self._Attributes(nodeAttributes)};')

	def AddRecord(
		self,
		identifier: str,
		title: str,
		compartments: Iterable[Sequence[str]] = (),
		**attributes: str
	) -> None:
		"""
		Add a record node: a titled box divided into compartments.

		:param identifier:   Identifier of the node, which an edge names it by.
		:param title:        The record's title, written in guillemets.
		:param compartments: Optional, the rows of each compartment below the title.
		:param attributes:   Further attributes of the node.
		:raises ValueError:  If parameter 'identifier' or 'title' is None.
		:raises TypeError:   If parameter 'identifier' or 'title' is not a string.
		"""
		if title is None:
			raise ValueError("Parameter 'title' is None.")
		elif not isinstance(title, str):
			ex = TypeError("Parameter 'title' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(title)}'.")
			raise ex

		label = f"«{self.EscapeLabel(title)}»"
		for rows in compartments:
			label += f"|{self._Compartment(rows)}"

		self.AddNode(identifier, f"{{{label}}}", **attributes)

	def AddEdge(self, source: str, target: str, **attributes: str) -> None:
		"""
		Add an edge between two nodes.

		An attribute's value is quoted but not escaped - :meth:`AddRecord` is the only method escaping what it is
		given. A label assembled from something a schema *author* wrote, rather than from a name a schema language
		constrains, has to go through :meth:`EscapeLabel` first.

		:param source:      Identifier of the node the edge starts at.
		:param target:      Identifier of the node the edge points to.
		:param attributes:  Further attributes of the edge.
		:raises ValueError: If parameter 'source' or 'target' is None.
		:raises TypeError:  If parameter 'source' or 'target' is not a string.
		"""
		if source is None:
			raise ValueError("Parameter 'source' is None.")
		elif not isinstance(source, str):
			ex = TypeError("Parameter 'source' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(source)}'.")
			raise ex
		if target is None:
			raise ValueError("Parameter 'target' is None.")
		elif not isinstance(target, str):
			ex = TypeError("Parameter 'target' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(target)}'.")
			raise ex

		if len(attributes) == 0:
			self._statements.append(f'\t"{source}" -> "{target}";')
		else:
			self._statements.append(f'\t"{source}" -> "{target}" {self._Attributes(attributes)};')

	def __str__(self) -> str:
		"""
		Render the graph.

		:returns: The graph in the DOT language.
		"""
		statements = "\n".join(self._statements)

		return f"digraph {self._name} {{\n{statements}\n}}"


@export
class SchemaGraph(BaseDirective):
	"""
	Base-class of the directives drawing the schema file given as their argument.

	It holds everything that isn't the schema's language: the path is resolved against the document using the
	directive and registered as a dependency - so editing the schema rebuilds the page holding its diagram - and
	whatever :meth:`_RenderGraph` returns is handed to :mod:`sphinx.ext.graphviz`, wrapped in a figure when a caption
	was given. A derived class sets :attr:`~pyTooling.Documentation.Sphinx.Directives.BaseDirective.directiveName` and
	overrides :meth:`_RenderGraph`.
	"""

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        1      #: Number of required directive arguments: the schema's path.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"caption": strip,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Read the schema and hand its graph to :mod:`sphinx.ext.graphviz` for rendering.

		:returns: A ``graphviz`` node, wrapped in a figure when a caption was given, or the message of whatever went
		          wrong while reading the schema.
		"""
		relativePath, absolutePath = self.env.relfn2path(self.arguments[0])
		self.env.note_dependency(relativePath)
		schemaFile = Path(absolutePath)

		try:
			code = self._RenderGraph(schemaFile)
		except Exception as ex:
			return self._internalError(
				nodes.container(),
				__name__,
				f"{self.directiveName}: Couldn't draw schema '{schemaFile}'.",
				ex
			)

		node = graphviz()
		node["code"] = code
		node["options"] = {"docname": self.env.docname}
		node["alt"] = f"Diagram of {schemaFile.name}"

		if (caption := self.options.get("caption", None)) is not None:
			return [figure_wrapper(self, node, caption)]

		return [node]

	@classmethod
	def _RenderGraph(cls, schemaFile: Path) -> str:
		"""
		Render the schema as a graph.

		:param schemaFile:           Path of the schema to render.
		:returns:                    The graph in the DOT language.
		:raises NotImplementedError: If a derived class doesn't override it.
		"""
		raise NotImplementedError(f"{cls.directiveName}: '_RenderGraph' is not implemented.")
