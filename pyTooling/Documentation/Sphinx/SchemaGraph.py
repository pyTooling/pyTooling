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
A Sphinx directive drawing a schema as a Graphviz graph.

A schema's source says what a document may contain, in a shape that hides the structure: a reader looking for *what
contains what* has to follow named types through the file. This directive draws that structure instead:

.. code-block:: ReST

   .. xsd-graph:: ../../pyTooling/Resources/TestReport-v0.1.xsd
      :caption: The types of TestReport-v0.1.xsd.

The model comes from :mod:`xmlschema`, so the picture is the schema as a validator sees it rather than as its source
text is laid out, and it is drawn at build time from the shipped file, so it cannot drift from it.

The module is split where the schema language stops mattering. :class:`DotGraph` accumulates the graph,
:class:`SchemaGraph` is the directive - the argument becomes a path, the file becomes a build dependency, and the DOT
is handed to :mod:`sphinx.ext.graphviz` - and only :func:`renderXMLSchema` and :class:`XSDGraph` know about XML. A
schema in another language is a second :func:`renderXMLSchema` and a second three-line subclass.

.. attention::

   :mod:`xmlschema` is imported when the directive **runs**, not when this module is imported, so a project using the
   extension for its roles alone doesn't need it installed. It is part of the ``sphinx`` extra.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension this belongs to, and what else it brings.
"""
from pathlib                                   import Path
from types                                     import ModuleType
from typing                                    import Any, Generator, Iterable

from docutils                                  import nodes
from sphinx.ext.graphviz                       import figure_wrapper, graphviz

from pyTooling.Decorators                      import export
from pyTooling.Exceptions                      import MissingDependencyError
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.Documentation.Sphinx.Directives import BaseDirective, strip


__all__ = ["XSD_NAMESPACE", "DOT_METACHARACTERS", "GRAPH_ATTRIBUTES"]

#: Namespace prefixing every builtin type's name.
XSD_NAMESPACE = "{http://www.w3.org/2001/XMLSchema}"

#: Characters a Graphviz record label gives a meaning to, and that a name therefore has to escape.
DOT_METACHARACTERS = ("\\", "{", "}", "|", "<", ">", '"')

#: Attributes every schema graph is drawn with, so two diagrams in one document look alike.
GRAPH_ATTRIBUTES = (
	"rankdir=LR;",
	"nodesep=0.4;",
	'node [shape=record, fontname="sans-serif", fontsize=10];',
	'edge [fontname="sans-serif", fontsize=9];',
)


@export
def escapeLabel(text: str) -> str:
	"""
	Escape the characters a Graphviz record label gives a meaning to.

	:param text: The text to escape.
	:returns:    The text, safe to put into a record label.
	"""
	for character in DOT_METACHARACTERS:
		text = text.replace(character, f"\\{character}")

	return text


@export
def compartment(rows: Iterable[str]) -> str:
	"""
	Join the rows of one record compartment, left-aligned.

	:param rows: The rows to join, unescaped.
	:returns:    The compartment's content, or a single space when there are no rows - an empty compartment collapses,
	             which makes the records of a graph differently shaped.
	"""
	content = "".join(f"{escapeLabel(row)}\\l" for row in rows)

	return content if content else " "


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

		:param name: Optional, the graph's name.
		"""
		self._name = name
		self._statements = [f"\t{attribute}" for attribute in GRAPH_ATTRIBUTES]
		self.AddSeparator()

	@staticmethod
	def _Attributes(attributes: dict[str, str]) -> str:
		"""
		Render an attribute list, quoting every value.

		:param attributes: The attributes to render, keyed by name.
		:returns:          The attribute list in brackets, or an empty string when there are none.
		"""
		if not attributes:
			return ""

		return "[" + ", ".join(f'{name}="{value}"' for name, value in attributes.items()) + "]"

	def AddSeparator(self) -> None:
		"""Add a blank line, so the generated DOT reads in the groups it was written in."""
		self._statements.append("")

	def AddNode(self, identifier: str, label: str, **attributes: str) -> None:
		"""
		Add a node.

		:param identifier: Identifier of the node, which an edge names it by.
		:param label:      The node's label, already escaped.
		:param attributes: Further attributes of the node.
		"""
		self._statements.append(f'\t"{identifier}" {self._Attributes({"label": label, **attributes})};')

	def AddRecord(
		self,
		identifier: str,
		title: str,
		compartments: Iterable[Iterable[str]] = (),
		**attributes: str
	) -> None:
		"""
		Add a record node: a titled box divided into compartments.

		:param identifier:   Identifier of the node, which an edge names it by.
		:param title:        The record's title, written in guillemets.
		:param compartments: Optional, the rows of each compartment below the title.
		:param attributes:   Further attributes of the node.
		"""
		label = "|".join((f"«{escapeLabel(title)}»", *(compartment(rows) for rows in compartments)))

		self.AddNode(identifier, f"{{{label}}}", **attributes)

	def AddEdge(self, source: str, target: str, **attributes: str) -> None:
		"""
		Add an edge between two nodes.

		An attribute's value is quoted but not escaped - :meth:`AddRecord` is the only method escaping what it is
		given. A label assembled from something a schema *author* wrote, rather than from a name a schema language
		constrains, has to go through :func:`escapeLabel` first.

		:param source:     Identifier of the node the edge starts at.
		:param target:     Identifier of the node the edge points to.
		:param attributes: Further attributes of the edge.
		"""
		suffix = f" {self._Attributes(attributes)}" if attributes else ""

		self._statements.append(f'\t"{source}" -> "{target}"{suffix};')

	def __str__(self) -> str:
		"""
		Render the graph.

		:returns: The graph in the DOT language.
		"""
		return "\n".join((f"digraph {self._name} {{", *self._statements, "}"))


def _xmlschema() -> ModuleType:
	"""
	Import :mod:`xmlschema` on first use.

	The import is here rather than at the top of the module, so enabling the extension costs nothing until a document
	actually draws an XML schema.

	:returns:                       The :mod:`xmlschema` package.
	:raises MissingDependencyError: If :mod:`xmlschema` isn't installed.
	"""
	try:
		import xmlschema
	except ImportError as ex:  # pragma: no cover
		raise MissingDependencyError(dependency="xmlschema", extra="sphinx") from ex

	return xmlschema


@export
def typeName(xsdType: Any) -> str:
	"""
	Return a readable name for a type.

	:param xsdType: The type to name.
	:returns:       ``xsd:string`` for a builtin type, the local name for a named one, ``(anonymous)`` otherwise.
	"""
	name = xsdType.name
	if name is None:
		return "(anonymous)"

	return f"xsd:{name[len(XSD_NAMESPACE):]}" if name.startswith(XSD_NAMESPACE) else name


@export
def childElements(group: Any) -> Generator[Any, None, None]:
	"""
	Yield every element of a content model, flattening the sequences and choices in between.

	:param group: The content model to walk.
	:returns:     Generator of the elements it holds, at any depth.
	"""
	validators = _xmlschema().validators

	for child in group:
		if isinstance(child, validators.XsdGroup):
			yield from childElements(child)
		elif isinstance(child, validators.XsdElement):
			yield child


@export
def cardinality(element: Any) -> str:
	"""
	Render an element's occurrence.

	:param element: The element to render the occurrence of.
	:returns:       ``lower..upper``, with ``*`` for an unbounded upper limit.
	"""
	lower, upper = element.occurs

	return f"{lower}..{'*' if upper is None else upper}"


@export
def renderXMLSchema(schemaFile: Path) -> str:
	"""
	Render an XML schema as a Graphviz graph.

	Every complex type becomes a record of three compartments - its name, its attributes, and its simple-typed child
	elements with their cardinality - and every complex-typed child element becomes an edge, so containment and
	recursion are visible as edges rather than as repeated type names. A simple type earns a node of its own only when
	it is an enumeration, because its values are what a type name cannot say.

	:param schemaFile:              Path of the schema to render.
	:returns:                       The graph in the DOT language.
	:raises MissingDependencyError: If :mod:`xmlschema` isn't installed.
	"""
	schema = _xmlschema().XMLSchema(str(schemaFile))
	complexTypes = {name: xsdType for name, xsdType in schema.types.items() if xsdType.is_complex()}
	# sorted, because a set's iteration order varies between interpreter runs and a graph that is redrawn identically
	# is what lets a rebuilt page be compared to the one before it
	enumerations = sorted(
		name for name, xsdType in schema.types.items() if xsdType.is_simple() and xsdType.enumeration is not None
	)

	graph = DotGraph()

	for name, xsdType in complexTypes.items():
		attributes = [
			f"{attribute} : {typeName(xsdType.attributes[attribute].type)}" for attribute in xsdType.attributes
		]
		elements = [
			f"{child.name} : {typeName(child.type)} [{cardinality(child)}]"
			for child in childElements(xsdType.content) if child.type.is_simple()
		]
		graph.AddRecord(name, name, (attributes, elements))

	graph.AddSeparator()
	for name, xsdType in complexTypes.items():
		for child in childElements(xsdType.content):
			if child.type.is_complex():
				graph.AddEdge(name, typeName(child.type), label=f"{child.name} [{cardinality(child)}]")

	graph.AddSeparator()
	for name in enumerations:
		graph.AddRecord(name, name, (schema.types[name].enumeration,), style="filled", fillcolor="#f0f0f0")

	for name, xsdType in complexTypes.items():
		used = {xsdType.attributes[attribute].type.name for attribute in xsdType.attributes}
		used |= {child.type.name for child in childElements(xsdType.content) if child.type.is_simple()}
		for usedType in sorted(usedType for usedType in used if usedType in enumerations):
			graph.AddEdge(name, usedType, style="dashed", arrowhead="open", constraint="false")

	graph.AddSeparator()
	for name, element in schema.elements.items():
		graph.AddNode(f"<{name}>", name, shape="doublecircle", style="filled", fillcolor="#e8e8ff")
		graph.AddEdge(f"<{name}>", typeName(element.type), label="root")

	return str(graph)


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

	def _RenderGraph(self, schemaFile: Path) -> str:
		"""
		Render the schema as a graph.

		:param schemaFile:           Path of the schema to render.
		:returns:                    The graph in the DOT language.
		:raises NotImplementedError: If a derived class doesn't override it.
		"""
		raise NotImplementedError(f"{self.directiveName}: '_RenderGraph' is not implemented.")


@export
class XSDGraph(SchemaGraph):
	"""
	The ``xsd-graph`` directive: an XML schema, drawn from the schema itself.

	One argument, the path of the schema relative to the document using the directive; ``:caption:`` puts a caption
	under the diagram.
	"""

	directiveName: str = "xsd-graph"  #: Name the directive is invoked by.

	def _RenderGraph(self, schemaFile: Path) -> str:
		"""
		Render the XML schema.

		:param schemaFile:              Path of the schema to render.
		:returns:                       The graph in the DOT language.
		:raises MissingDependencyError: If :mod:`xmlschema` isn't installed.
		"""
		return renderXMLSchema(schemaFile)
