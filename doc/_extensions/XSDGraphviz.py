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
"""
A Sphinx directive rendering an XML schema as a Graphviz graph.

An XSD's source says what is allowed; it says it in a shape that hides the structure. A reader looking for *what
contains what* has to follow named types through the document. This directive draws that structure instead:

.. code-block:: rest

   .. xsd-graph:: ../../pyTooling/Resources/TestReport-v0.1.xsd
      :caption: The types of TestReport-v0.1.xsd.

The model comes from :mod:`xmlschema`, so the picture is the schema as a validator sees it, not as its source
text is laid out - and it is generated at build time from the shipped file, so it cannot drift from it.
"""
from pathlib   import Path
from typing    import Any, ClassVar

from docutils             import nodes
from docutils.parsers.rst import directives
from sphinx.application   import Sphinx
from sphinx.ext.graphviz  import graphviz, figure_wrapper
from sphinx.util.docutils import SphinxDirective
from xmlschema            import XMLSchema
from xmlschema.validators import XsdElement, XsdGroup


XSD_NAMESPACE = "{http://www.w3.org/2001/XMLSchema}"   #: Namespace prefixing every builtin type's name.


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


def escape(text: str) -> str:
	"""
	Escape the characters a Graphviz record label gives a meaning to.

	:param text: The text to escape.
	:returns:    The text, safe to put into a record label.
	"""
	for character in ("\\", "{", "}", "|", "<", ">", '"'):
		text = text.replace(character, f"\\{character}")

	return text


def compartment(rows: list[str]) -> str:
	"""
	Join the rows of one record compartment, left-aligned.

	:param rows: The rows to join, unescaped.
	:returns:    The compartment's content, or a single space when there are no rows - an empty compartment
	             collapses, which makes the records of a graph differently shaped.
	"""
	return "".join(f"{escape(row)}\\l" for row in rows) if rows else " "


def childElements(group: Any) -> Any:
	"""
	Yield every element of a content model, flattening the sequences and choices in between.

	:param group: The content model to walk.
	:returns:     Generator of the elements it holds, at any depth.
	"""
	for child in group:
		if isinstance(child, XsdGroup):
			yield from childElements(child)
		elif isinstance(child, XsdElement):
			yield child


def cardinality(element: XsdElement) -> str:
	"""
	Render an element's occurrence.

	:param element: The element to render the occurrence of.
	:returns:       ``lower..upper``, with ``*`` for an unbounded upper limit.
	"""
	lower, upper = element.occurs

	return f"{lower}..{'*' if upper is None else upper}"


def renderSchema(schemaFile: Path) -> str:
	"""
	Render an XML schema as a Graphviz graph.

	Every complex type becomes a record of three compartments - its name, its attributes, and its simple-typed
	child elements with their cardinality - and every complex-typed child element becomes an edge, so containment
	and recursion are visible as edges rather than as repeated type names. A simple type earns a node of its own
	only when it is an enumeration, because its values are what a type name cannot say.

	:param schemaFile: Path of the schema to render.
	:returns:          The graph in the DOT language.
	"""
	schema = XMLSchema(str(schemaFile))
	complexTypes = {name: xsdType for name, xsdType in schema.types.items() if xsdType.is_complex()}
	enumerations = {
		name for name, xsdType in schema.types.items() if xsdType.is_simple() and xsdType.enumeration is not None
	}

	lines = [
		"digraph schema {",
		"\trankdir=LR;",
		"\tnodesep=0.4;",
		'\tnode [shape=record, fontname="sans-serif", fontsize=10];',
		'\tedge [fontname="sans-serif", fontsize=9];',
		"",
	]

	for name, xsdType in complexTypes.items():
		attributes = [
			f"{attribute} : {typeName(xsdType.attributes[attribute].type)}" for attribute in xsdType.attributes
		]
		elements = [
			f"{child.name} : {typeName(child.type)} [{cardinality(child)}]"
			for child in childElements(xsdType.content) if child.type.is_simple()
		]
		label = "|".join((f"«{name}»", compartment(attributes), compartment(elements)))
		lines.append(f'\t"{name}" [label="{{{label}}}"];')

	lines.append("")
	for name, xsdType in complexTypes.items():
		for child in childElements(xsdType.content):
			if child.type.is_complex():
				lines.append(f'\t"{name}" -> "{typeName(child.type)}" [label="{child.name} [{cardinality(child)}]"];')

	lines.append("")
	for name in enumerations:
		values = compartment(list(schema.types[name].enumeration))
		lines.append(f'\t"{name}" [style=filled, fillcolor="#f0f0f0", label="{{«{name}»|{values}}}"];')

	for name, xsdType in complexTypes.items():
		used = {xsdType.attributes[attribute].type.name for attribute in xsdType.attributes}
		used |= {child.type.name for child in childElements(xsdType.content) if child.type.is_simple()}
		for usedType in sorted(usedType for usedType in used if usedType in enumerations):
			lines.append(f'\t"{name}" -> "{usedType}" [style=dashed, arrowhead=open, constraint=false];')

	lines.append("")
	for name, element in schema.elements.items():
		lines.append(f'\t"<{name}>" [shape=doublecircle, style=filled, fillcolor="#e8e8ff", label="{name}"];')
		lines.append(f'\t"<{name}>" -> "{typeName(element.type)}" [label="root"];')

	lines.append("}")

	return "\n".join(lines)


class XSDGraph(SphinxDirective):
	"""
	Directive rendering the XML schema given as its argument.

	The schema's path is relative to the document using the directive, and the file is registered as a dependency,
	so editing the schema rebuilds the page holding its diagram.
	"""

	has_content:        ClassVar[bool] = False
	required_arguments: ClassVar[int] = 1
	optional_arguments: ClassVar[int] = 0
	final_argument_whitespace: ClassVar[bool] = False
	option_spec:        ClassVar[dict] = {
		"caption": directives.unchanged,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Read the schema and hand its graph to :mod:`sphinx.ext.graphviz` for rendering.

		:returns: A ``graphviz`` node, wrapped in a figure when a caption was given.
		"""
		relativePath, absolutePath = self.env.relfn2path(self.arguments[0])
		self.env.note_dependency(relativePath)

		node = graphviz()
		node["code"] = renderSchema(Path(absolutePath))
		node["options"] = {"docname": self.env.docname}
		node["alt"] = f"Diagram of {Path(absolutePath).name}"

		if (caption := self.options.get("caption")) is not None:
			return [figure_wrapper(self, node, caption)]

		return [node]


def setup(sphinx: Sphinx) -> dict[str, Any]:
	"""
	Register the directive with Sphinx.

	:param sphinx: The Sphinx application to register with.
	:returns:      The extension's metadata.
	"""
	sphinx.add_directive("xsd-graph", XSDGraph)

	return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
