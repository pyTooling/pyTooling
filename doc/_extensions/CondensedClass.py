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
A Sphinx directive rendering a class' **public interface** as a condensed code block.

A reader arriving at a page wants to see the shape of a type before reading about it: what it is derived from, what
can be called on it, and what can be read from it. The API reference answers that in several screens of prose; a
hand-written summary answers it in one - and drifts from the code the day the class changes.

.. code-block:: rest

   .. condensed-class:: pyTooling.Stopwatch.Stopwatch
      :caption: The interface of a stopwatch.

renders the class line, its class variables, its methods and its properties, each with the signature it is declared
with and ``...`` for a body:

.. code-block:: python

   @export
   class Stopwatch(SlottedObject):
     def __init__(self, name: Nullable[str] = None, started: bool = False) -> None:
       ...

     def Start(self) -> None:
       ...

     @readonly
     def Duration(self) -> float:
       ...

**The source is parsed, not imported.** Three things follow from that: the annotations appear as they are *written*
(``Nullable[str]``, not the ``Optional[str]`` an import would resolve it to), the declaration order is the order in
the file, and a metaclass such as :class:`~pyTooling.MetaClasses.ExtendedType` can't hide a member behind a
descriptor it installed. The file is registered as a dependency of the page, so editing the class rebuilds the page.

**What is left out** is what the surrounding text is for: bodies, doc-strings, and the annotated attributes that
make up a slotted class' fields - those are implementation. Class *variables* are kept, because a name with a value
at class level is part of what a caller may read.
"""
from ast                  import AST, AnnAssign, Assign, AsyncFunctionDef, ClassDef, FunctionDef, Module, Name
from ast                  import get_source_segment, parse, unparse
from re                   import sub as re_sub
from importlib.util       import find_spec
from pathlib              import Path
from typing               import Any, ClassVar, Optional as Nullable, Union

from docutils             import nodes
from docutils.parsers.rst import directives
from sphinx.application   import Sphinx
from sphinx.util.docutils import SphinxDirective


#: The kinds of member this directive can render, in the order they are documented.
MEMBER_KINDS = ("classvars", "dunders", "methods", "properties")

#: Decorators marking a function as a property getter.
PROPERTY_DECORATORS = ("property", "readonly", "cached_property")

#: Definition of a function or a method.
Function = Union[FunctionDef, AsyncFunctionDef]


def splitDottedName(dottedName: str) -> tuple[Path, list[str]]:
	"""
	Split a dotted name into the file its module lives in and the path of class names within it.

	The longest prefix that names a module wins, so a class nested in a class is reachable and a module named like a
	class is not mistaken for one.

	:param dottedName: Dotted name of the class, e.g. ``pyTooling.Stopwatch.Stopwatch``.
	:returns:          Tuple of the module's source file and the class names leading to the class.
	:raises ValueError: If no prefix of the name is an importable module with a source file.
	"""
	parts = dottedName.split(".")
	for position in range(len(parts) - 1, 0, -1):
		moduleName = ".".join(parts[:position])
		try:
			spec = find_spec(moduleName)
		except (ImportError, ValueError):
			continue

		if spec is not None and spec.origin is not None and spec.origin.endswith(".py"):
			return Path(spec.origin), parts[position:]

	raise ValueError(f"No module of '{dottedName}' could be found.")


def findClass(tree: Module, classPath: list[str]) -> ClassDef:
	"""
	Find a class definition in a parsed module, descending into nested classes.

	:param tree:        The parsed module.
	:param classPath:   The class names leading to the class, outermost first.
	:returns:           The class definition.
	:raises ValueError: If a name of the path is not a class of its parent.
	"""
	body: list[AST] = tree.body
	definition: Nullable[ClassDef] = None

	for name in classPath:
		for statement in body:
			if isinstance(statement, ClassDef) and statement.name == name:
				definition = statement
				body = statement.body
				break
		else:
			raise ValueError(f"'{name}' is no class of the module or of the class containing it.")

	if definition is None:
		raise ValueError("No class was named.")

	return definition


def render(node: AST, source: str) -> str:
	"""
	Render an expression the way it is **written**, not the way :func:`ast.unparse` would spell it.

	:func:`ast.unparse` normalizes as it goes: ``1.5e-3`` comes back as ``0.0015`` and a double-quoted string comes
	back single-quoted. Reading the source segment instead keeps the literal a reader would find in the file, which
	is the point of rendering from the source at all. An expression spanning several lines is folded onto one.

	:param node:   The expression to render.
	:param source: The source text the expression was parsed from.
	:returns:      The expression as it is written, or :func:`ast.unparse`'s spelling if the segment can't be read.
	"""
	segment = get_source_segment(source, node)

	return unparse(node) if segment is None else re_sub(r"\s*\n\s*", " ", segment).strip()


def decoratorName(decorator: AST) -> str:
	"""
	Return the name a decorator expression ends in.

	``@readonly`` is a :class:`~ast.Name`, ``@functools.cached_property`` an :class:`~ast.Attribute` and
	``@Duration.setter`` an attribute of a name - all three are answered by their last component.

	:param decorator: The decorator expression.
	:returns:         The name the expression ends in, or an empty string for anything else.
	"""
	return getattr(decorator, "id", None) or getattr(decorator, "attr", None) or ""


def formatArguments(function: Function, source: str) -> list[str]:
	"""
	Render a function's parameters the way they are declared, one string each.

	The parameters are returned **as a list** rather than joined: an annotation may contain a comma of its own -
	``dict[str, int]``, ``tuple[int, ...]``, ``Union[int, str]`` - so a joined string cannot be split back into
	parameters, which is what wrapping a long signature needs to do.

	:class:`ast.unparse` also writes ``name: str=None`` for an annotated parameter with a default; PEP 8 spaces that
	as ``name: str = None``, which is how the sources are written, so the parts are assembled here instead.

	:param function: The function or method to render the parameters of.
	:param source:   The source text the function was parsed from.
	:returns:        One string per parameter, without the enclosing parentheses.
	"""
	arguments = function.args
	positional = [*arguments.posonlyargs, *arguments.args]
	# a default belongs to the *last* parameters, so the list is padded at the front
	defaults = [None] * (len(positional) - len(arguments.defaults)) + list(arguments.defaults)

	rendered = []
	for position, (argument, default) in enumerate(zip(positional, defaults)):
		rendered.append(formatArgument(argument, default, source))
		if len(arguments.posonlyargs) > 0 and position == len(arguments.posonlyargs) - 1:
			rendered.append("/")

	if arguments.vararg is not None:
		rendered.append(f"*{formatArgument(arguments.vararg, None, source)}")
	elif len(arguments.kwonlyargs) > 0:
		rendered.append("*")

	for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
		rendered.append(formatArgument(argument, default, source))

	if arguments.kwarg is not None:
		rendered.append(f"**{formatArgument(arguments.kwarg, None, source)}")

	return rendered


def formatArgument(argument: Any, default: Nullable[AST], source: str) -> str:
	"""
	Render one parameter with its annotation and its default value.

	:param argument: The parameter to render.
	:param default:  The parameter's default value, or ``None`` if it has none.
	:param source:   The source text the parameter was parsed from.
	:returns:        The parameter as it is declared.
	"""
	if argument.annotation is None:
		return argument.arg if default is None else f"{argument.arg}={render(default, source)}"

	annotated = f"{argument.arg}: {render(argument.annotation, source)}"

	return annotated if default is None else f"{annotated} = {render(default, source)}"


def formatFunction(function: Function, indent: str, width: int, source: str) -> list[str]:
	"""
	Render a method as its decorators, its signature and an elided body.

	A signature longer than ``width`` is broken after each parameter, the way it would be written by hand - a
	``__exit__`` with three annotated parameters doesn't fit on any page.

	:param function: The method to render.
	:param indent:   Indentation of one level.
	:param width:    Column the signature is wrapped at.
	:param source:   The source text the method was parsed from.
	:returns:        The lines the method is rendered as.
	"""
	lines = [f"{indent}@{render(decorator, source)}" for decorator in function.decorator_list]
	prefix =    "async def" if isinstance(function, AsyncFunctionDef) else "def"
	returns =   "" if function.returns is None else f" -> {render(function.returns, source)}"
	arguments = formatArguments(function, source)
	signature = f"{indent}{prefix} {function.name}({', '.join(arguments)}){returns}:"

	if len(signature) <= width or len(arguments) == 0:
		lines.append(signature)
	else:
		lines.append(f"{indent}{prefix} {function.name}(")
		lines.extend(f"{indent}{indent}{argument}," for argument in arguments)
		lines.append(f"{indent}){returns}:")

	lines.append(f"{indent}{indent}...")

	return lines


def isClassVariable(statement: AST) -> bool:
	"""
	Check if a statement declares a public class variable rather than a field.

	A class' **fields** are annotated without a value - that is what ``ExtendedType(slots=True)`` reads them from -
	and are implementation. A name that is *assigned* at class level is a class variable, and a public one is part
	of what a caller may read.

	:param statement: The statement to classify.
	:returns:         ``True``, if the statement assigns a public name at class level.
	"""
	if isinstance(statement, AnnAssign):
		target, hasValue = statement.target, statement.value is not None
	elif isinstance(statement, Assign) and len(statement.targets) == 1:
		target, hasValue = statement.targets[0], True
	else:
		return False

	return hasValue and isinstance(target, Name) and not target.id.startswith("_")


def formatClassVariable(statement: Union[AnnAssign, Assign], indent: str, source: str) -> str:
	"""
	Render a class variable with its annotation and its value.

	:param statement: The assignment to render.
	:param indent:    Indentation of one level.
	:param source:    The source text the assignment was parsed from.
	:returns:         The class variable as it is declared.
	"""
	return f"{indent}{render(statement, source)}"


def selectedKinds(members: Nullable[str]) -> frozenset[str]:
	"""
	Read the ``:members:`` option.

	:param members:     The option's value, or ``None`` if it wasn't given.
	:returns:           The kinds of member to render.
	:raises ValueError: If a name is not one of :data:`MEMBER_KINDS`.
	"""
	if members is None:
		return frozenset(MEMBER_KINDS)

	kinds = frozenset(kind.strip() for kind in members.split(",") if kind.strip() != "")
	if len(unknown := kinds - frozenset(MEMBER_KINDS)) > 0:
		raise ValueError(f"Unknown member kind(s): {', '.join(sorted(unknown))}. Known are: {', '.join(MEMBER_KINDS)}.")

	return kinds


def renderClass(
	definition: ClassDef,
	kinds: frozenset[str],
	excluded: frozenset[str],
	indent: str,
	width: int,
	source: str
) -> str:
	"""
	Render a class' public interface as Python source.

	:param definition: The class to render.
	:param kinds:      The kinds of member to render.
	:param excluded:   Names not to render.
	:param indent:     Indentation of one level.
	:param width:      Column a signature is wrapped at.
	:param source:     The source text the class was parsed from.
	:returns:          The condensed class, ready for a literal block.
	"""
	lines = [f"@{render(decorator, source)}" for decorator in definition.decorator_list]
	inheritance = ", ".join((
		*(render(base, source) for base in definition.bases),
		*(f"{keyword.arg}={render(keyword.value, source)}" for keyword in definition.keywords),
	))

	lines.append(f"class {definition.name}({inheritance}):" if inheritance != "" else f"class {definition.name}:")

	members: list[list[str]] = []
	variables: list[str] = []
	for statement in definition.body:
		if "classvars" in kinds and isClassVariable(statement):
			variables.append(formatClassVariable(statement, indent, source))
		elif isinstance(statement, (FunctionDef, AsyncFunctionDef)):
			if statement.name in excluded or not isSelected(statement, kinds):
				continue

			members.append(formatFunction(statement, indent, width, source))

	if len(variables) > 0:
		members.insert(0, variables)

	if len(members) == 0:
		lines.append(f"{indent}...")
	else:
		for member in members:
			lines.append("")
			lines.extend(member)

	return "\n".join(lines)


def isSelected(function: Function, kinds: frozenset[str]) -> bool:
	"""
	Check if a method is one of the selected kinds and is public.

	A property is decided by its decorators - ``@property``, ``@readonly`` or a ``@<name>.setter`` - and everything
	else is a method. A name with one leading underscore is implementation and is never rendered; a dunder is not.

	:param function: The method to classify.
	:param kinds:    The kinds of member to render.
	:returns:        ``True``, if the method is to be rendered.
	"""
	decorators = [decoratorName(decorator) for decorator in function.decorator_list]
	isProperty = (
		any(decorator in PROPERTY_DECORATORS for decorator in decorators)
		or any(decorator in ("setter", "deleter") for decorator in decorators)
	)

	if isProperty:
		return "properties" in kinds

	if function.name.startswith("__") and function.name.endswith("__"):
		return "dunders" in kinds

	return "methods" in kinds and not function.name.startswith("_")


class CondensedClass(SphinxDirective):
	"""
	The ``condensed-class`` directive: a class' public interface, rendered from its source.

	One argument, the dotted name of the class. ``:members:`` selects the kinds to render, ``:exclude-members:``
	drops names by name, ``:indent:`` sets the width of one indentation level, ``:width:`` the column a long
	signature is wrapped at, and ``:caption:`` puts a caption under the block.
	"""

	has_content:        ClassVar[bool] = False
	required_arguments: ClassVar[int] = 1
	optional_arguments: ClassVar[int] = 0
	final_argument_whitespace: ClassVar[bool] = False
	option_spec:        ClassVar[dict] = {
		"members":         directives.unchanged,
		"exclude-members": directives.unchanged,
		"indent":          directives.positive_int,
		"width":           directives.positive_int,
		"caption":         directives.unchanged,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Parse the class' module, render its interface and return it as a literal block.

		:returns: A ``literal_block`` node, or an error node when the class couldn't be found.
		"""
		dottedName = self.arguments[0].strip()

		try:
			sourceFile, classPath = splitDottedName(dottedName)
			kinds =    selectedKinds(self.options.get("members", None))
			excluded = frozenset(
				name.strip() for name in self.options.get("exclude-members", "").split(",") if name.strip() != ""
			)
			source = sourceFile.read_text(encoding="utf-8")
			definition = findClass(parse(source), classPath)
		except (OSError, SyntaxError, ValueError) as cause:
			return [self.state.document.reporter.error(
				f"condensed-class: {cause}", line=self.lineno
			)]

		self.env.note_dependency(str(sourceFile))

		code = renderClass(
			definition, kinds, excluded, " " * self.options.get("indent", 2), self.options.get("width", 100), source
		)
		node = nodes.literal_block(code, code)
		node["language"] = "Python"

		if (caption := self.options.get("caption")) is not None:
			node["caption"] = caption

		return [node]


def setup(sphinx: Sphinx) -> dict[str, Any]:
	"""
	Register the directive with Sphinx.

	:param sphinx: The Sphinx application to register with.
	:returns:      The extension's metadata.
	"""
	sphinx.add_directive("condensed-class", CondensedClass)

	return {"version": "0.1.0", "parallel_read_safe": True, "parallel_write_safe": True}
