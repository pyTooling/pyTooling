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
A Sphinx directive drawing an XML schema as a Graphviz graph.

A schema's source says what a document may contain, in a shape that hides the structure: a reader looking for *what
contains what* has to follow named types through the file. This directive draws that structure instead:

.. code-block:: ReST

   .. xsd-graph:: ../../pyTooling/Resources/TestReport-v0.1.xsd
      :caption: The types of TestReport-v0.1.xsd.

The model comes from :mod:`xmlschema`, so the picture is the schema as a validator sees it rather than as its source
text is laid out, and it is drawn at build time from the shipped file, so it cannot drift from it.

.. attention::

   :mod:`xmlschema` is imported when the directive **runs**, not when this module is imported, so a project using the
   extension for its roles alone doesn't need it installed. It is part of the ``sphinx`` extra.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx.SchemaGraph`
      |rarr| The graph and the directive's base-class, shared by every schema language.
"""
from __future__                                 import annotations

from pathlib                                    import Path
from typing                                     import TYPE_CHECKING, Generator

from pyTooling.Decorators                       import export
from pyTooling.Exceptions                       import MissingDependencyError
from pyTooling.Documentation.Sphinx.SchemaGraph import DotGraph, SchemaGraph

if TYPE_CHECKING:  # pragma: no cover
	from xmlschema.validators                     import XsdElement, XsdGroup, XsdType


@export
class XSDSchemaGraph(SchemaGraph):
	"""
	The ``xsd-graph`` directive: an XML schema, drawn from the schema itself.

	One argument, the path of the schema relative to the document using the directive; ``:caption:`` puts a caption
	under the diagram.
	"""

	directiveName: str = "xsd-graph"  #: Name the directive is invoked by.

	@staticmethod
	def _TypeName(xsdType: XsdType) -> str:
		"""
		Return a readable name for a type.

		:param xsdType: The type to name.
		:returns:       ``xsd:string`` for a builtin type, the local name for a named one, ``(anonymous)`` otherwise.
		"""
		if (name := xsdType.name) is None:
			return "(anonymous)"

		if (localName := name.removeprefix("{http://www.w3.org/2001/XMLSchema}")) != name:
			return f"xsd:{localName}"

		return name

	@staticmethod
	def _Cardinality(element: XsdElement) -> str:
		"""
		Render an element's occurrence.

		:param element: The element to render the occurrence of.
		:returns:       ``lower..upper``, with ``*`` for an unbounded upper limit.
		"""
		lower, upper = element.occurs

		return f"{lower}..{'*' if upper is None else upper}"

	@classmethod
	def _RenderGraph(cls, schemaFile: Path) -> str:
		"""
		Render an XML schema as a Graphviz graph.

		Every complex type becomes a record of three compartments - its name, its attributes, and its simple-typed child
		elements with their cardinality - and every complex-typed child element becomes an edge, so containment and
		recursion are visible as edges rather than as repeated type names. A simple type earns a node of its own only
		when it is an enumeration, because its values are what a type name cannot say.

		:param schemaFile:              Path of the schema to render.
		:returns:                       The graph in the DOT language.
		:raises MissingDependencyError: If :mod:`xmlschema` isn't installed.
		"""
		try:
			from xmlschema            import XMLSchema
			from xmlschema.validators import XsdElement, XsdGroup
		except ImportError as ex:  # pragma: no cover
			raise MissingDependencyError(dependency="xmlschema", extra="sphinx") from ex

		def childElements(group: XsdGroup) -> Generator[XsdElement, None, None]:
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

		schema = XMLSchema(str(schemaFile))
		complexTypes = {name: xsdType for name, xsdType in schema.types.items() if xsdType.is_complex()}
		# sorted, because a set's iteration order varies between interpreter runs and a graph that is redrawn
		# identically is what lets a rebuilt page be compared to the one before it
		enumerations = sorted(
			name for name, xsdType in schema.types.items() if xsdType.is_simple() and xsdType.enumeration is not None
		)

		graph = DotGraph()

		for name, xsdType in complexTypes.items():
			attributes = [
				f"{attribute} : {cls._TypeName(xsdType.attributes[attribute].type)}" for attribute in xsdType.attributes
			]
			elements = [
				f"{child.name} : {cls._TypeName(child.type)} [{cls._Cardinality(child)}]"
				for child in childElements(xsdType.content) if child.type.is_simple()
			]
			graph.AddRecord(name, name, (attributes, elements))

		graph.AddSeparator()
		for name, xsdType in complexTypes.items():
			for child in childElements(xsdType.content):
				if child.type.is_complex():
					graph.AddEdge(name, cls._TypeName(child.type), label=f"{child.name} [{cls._Cardinality(child)}]")

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
			graph.AddEdge(f"<{name}>", cls._TypeName(element.type), label="root")

		return str(graph)
