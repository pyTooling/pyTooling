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
A base-class for Sphinx directives, wrapping the parts of docutils a directive keeps re-deriving.

Sphinx and docutils present their options as an untyped mapping and their tables as a tree of nodes assembled by
hand. :class:`BaseDirective` puts a typed, validating layer over both: an option is *read* with a method that
returns the type asked for and raises :exc:`SphinxExtensionError` naming the directive and the option when it
can't, and a table header is *described* by its columns rather than built node by node.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension this belongs to, and what else it brings.
"""
from enum                 import Enum
from re                   import match as re_match
from typing               import Any, Optional as Nullable, TypeVar

from docutils             import nodes
from sphinx.directives    import ObjectDescription
from sphinx.errors        import ExtensionError
from sphinx.util.logging  import getLogger

from pyTooling.Decorators import export
from pyTooling.Documentation import DocumentationError


__all__ = ["strip", "stripAndNormalize"]

_EnumType = TypeVar("_EnumType", bound=Enum)
"""Type of an enumeration read from a directive's options."""


@export
class SphinxExtensionError(ExtensionError, DocumentationError):
	"""
	Base-exception of all exceptions raised by :mod:`pyTooling.Documentation.Sphinx`.

	It derives from **both** hierarchies on purpose: :exc:`~sphinx.errors.ExtensionError` is what Sphinx catches and
	reports with the position of the directive, and :exc:`~pyTooling.Documentation.DocumentationError` is what a
	caller of pyTooling catches. Neither would be enough alone.
	"""


@export
def strip(option: str) -> str:
	"""
	Option converter removing surrounding whitespace.

	:param option: The option's value as it was written.
	:returns:      The value without surrounding whitespace.
	"""
	return option.strip()


@export
def stripAndNormalize(option: str) -> str:
	"""
	Option converter removing surrounding whitespace and lowering the case.

	:param option: The option's value as it was written.
	:returns:      The value without surrounding whitespace, in lower case.
	"""
	return option.strip().lower()


@export
class BaseDirective(ObjectDescription[str]):
	"""
	Base-class for a directive, offering typed option access and table construction.

	A derived class sets :attr:`directiveName` - which is what the error messages name - and declares
	``option_spec`` as any directive does. What it gets in return is a ``_Parse***Option`` per type instead of
	reaching into :attr:`options` and validating by hand, and a ``_Create***TableHeader`` per table shape instead of
	assembling :class:`~docutils.nodes.tgroup`, :class:`~docutils.nodes.colspec`, :class:`~docutils.nodes.thead`
	and :class:`~docutils.nodes.row` in the right order.
	"""

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	option_spec =               {}     #: Mapping of option names to validator functions.

	directiveName: str  #: Name the directive is invoked by, used in every error message.

	def _ParseBooleanOption(self, optionName: str, default: Nullable[bool] = None) -> bool:
		"""
		Read an option written as ``yes``/``true`` or ``no``/``false``.

		:param optionName:             Name of the option to read.
		:param default:                Optional, the value to return when the option wasn't given.
		:returns:                      The option's value.
		:raises SphinxExtensionError:  If the option wasn't given and has no default.
		:raises SphinxExtensionError:  If the option's value is neither of the two accepted spellings.
		"""
		try:
			option = self.options[optionName]
		except KeyError as cause:
			if default is not None:
				return default

			raise SphinxExtensionError(
				f"{self.directiveName}: Required option '{optionName}' not found for directive."
			) from cause

		if option in ("yes", "true"):
			return True
		elif option in ("no", "false"):
			return False

		raise SphinxExtensionError(
			f"{self.directiveName}::{optionName}: '{option}' not supported for a boolean value (yes/true, no/false)."
		)

	def _ParseStringOption(self, optionName: str, default: Nullable[str] = None, regexp: str = "\\w+") -> str:
		"""
		Read an option that has to match a regular expression.

		:param optionName:             Name of the option to read.
		:param default:                Optional, the value to return when the option wasn't given.
		:param regexp:                 Optional, the pattern the value has to match. Default: one or more word
		                               characters.
		:returns:                      The option's value.
		:raises SphinxExtensionError:  If the option wasn't given and has no default.
		:raises SphinxExtensionError:  If the option's value doesn't match the pattern.
		"""
		try:
			option: str = self.options[optionName]
		except KeyError as cause:
			if default is not None:
				return default

			raise SphinxExtensionError(
				f"{self.directiveName}: Required option '{optionName}' not found for directive."
			) from cause

		if re_match(regexp, option):
			return option

		raise SphinxExtensionError(
			f"{self.directiveName}::{optionName}: '{option}' not an accepted value for regexp '{regexp}'."
		)

	def _ParseEnumOption(
		self,
		optionName: str,
		enumType: type[_EnumType],
		default: Nullable[_EnumType] = None
	) -> _EnumType:
		"""
		Read an option naming a member of an enumeration.

		The written value is lowered and its dashes become underscores, so ``horizontal-table`` in a document selects
		the ``horizontal_table`` member - a document reads in the spelling documents use, and the enumeration keeps
		the spelling Python uses.

		:param optionName:             Name of the option to read.
		:param enumType:               The enumeration whose members the value is looked up in.
		:param default:                Optional, the member to return when the option wasn't given.
		:returns:                      The named member of the enumeration.
		:raises SphinxExtensionError:  If the option wasn't given and has no default.
		:raises SphinxExtensionError:  If the value names no member of the enumeration.
		"""
		try:
			option: str = self.options[optionName]
		except KeyError as cause:
			if default is not None:
				return default

			raise SphinxExtensionError(
				f"{self.directiveName}: Required option '{optionName}' not found for directive."
			) from cause

		identifier = option.lower().replace("-", "_")

		try:
			return enumType[identifier]
		except KeyError as cause:
			raise SphinxExtensionError(
				f"{self.directiveName}::{optionName}: Value '{option}' (transformed: '{identifier}') is not a valid "
				f"member of '{enumType.__name__}'."
			) from cause

	def _CreateSingleTableHeader(
		self,
		columns: list[tuple[str, Nullable[int]]],
		identifier: str,
		classes: list[str]
	) -> nodes.tgroup:
		"""
		Create a table with a single header row.

		:param columns:    One ``(title, width)`` pair per column; a width of ``None`` leaves it to the writer.
		:param identifier: Identifier of the table.
		:param classes:    CSS classes to put on the table.
		:returns:          The table's column group, with the header row already in it.
		"""
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=(len(columns))))

		# Setup column specifications
		for _, width in columns:
			tableGroup += nodes.colspec(colwidth=width)

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow := nodes.row())

		# Setup header row
		for columnTitle, _ in columns:
			headerRow += nodes.entry("", nodes.Text(columnTitle))

		return tableGroup

	def _CreateDoubleRowTableHeader(
		self,
		columns: list[tuple[str, Nullable[list[tuple[str, int]]], Nullable[int]]],
		identifier: str,
		classes: list[str]
	) -> nodes.tgroup:
		"""
		Create a table whose header spans two rows, so a column can group sub-columns.

		:param columns:    One ``(title, subColumns, width)`` triple per column. ``subColumns`` is ``None`` for a
		                   column spanning both header rows, otherwise the ``(title, width)`` pairs below it.
		:param identifier: Identifier of the table.
		:param classes:    CSS classes to put on the table.
		:returns:          The table's column group, with both header rows already in it.
		"""
		columnCount = sum(len(groupColumn[1]) if groupColumn[1] is not None else 1 for groupColumn in columns)

		# Create table with N columns
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=columnCount))

		# Setup column specifications
		for _, more, width in columns:
			if more is None:
				tableGroup += nodes.colspec(colwidth=width)
			else:
				for _, width in more:
					tableGroup += nodes.colspec(colwidth=width)

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow1 := nodes.row())

		# Setup primary header row
		for columnTitle, more, _ in columns:
			if more is None:
				headerRow1 += nodes.entry("", nodes.Text(columnTitle), morerows=1)
			else:
				headerRow1 += nodes.entry("", nodes.Text(columnTitle), morecols=(morecols := len(more) - 1))
				for _ in range(morecols):
					headerRow1 += None

		# Setup secondary header row
		tableHeader += (headerRow2 := nodes.row())
		for columnTitle, more, _ in columns:
			if more is None:
				headerRow2 += None
			else:
				for columnTitle, _ in more:
					headerRow2 += nodes.entry("", nodes.Text(columnTitle))

		return tableGroup

	def _CreateRotatedTableHeader(
		self,
		columns: list[tuple[str, Nullable[list[str]]]],
		identifier: str,
		classes: list[str]
	) -> nodes.tgroup:
		"""
		Create a table whose header titles are rotated, for many narrow columns.

		:param columns:    One ``(title, classes)`` pair per column; the classes are put on the header cell.
		:param identifier: Identifier of the table.
		:param classes:    CSS classes to put on the table.
		:returns:          The table's column group, with the header row already in it.
		"""
		table = nodes.table("", identifier=identifier, classes=classes)
		table += (tableGroup := nodes.tgroup(cols=len(columns)))

		# Setup column specifications
		for i, (_, width) in enumerate(columns):
			tableGroup += nodes.colspec(classes=[f"col-{i}"])

		tableGroup += (tableHeader := nodes.thead())
		tableHeader += (headerRow := nodes.row())

		# Setup header row
		for columnTitle, columnClasses in columns:
			span = nodes.inline("", text=columnTitle)
			div = nodes.container("", span)
			headerRow += nodes.entry("", div, classes=[] if columnClasses is None else columnClasses)

		return tableGroup

	def _internalError(
		self,
		container: nodes.container,
		location: str,
		message: str,
		exception: Exception
	) -> list[nodes.Node]:
		"""
		Report an exception a directive couldn't recover from, in the log **and** on the page.

		A directive that fails silently leaves a hole in the documentation that nobody notices. This puts the message
		where a reader sees it and the traceback where a maintainer does.

		:param container: The container the message is put into.
		:param location:  Name of the logger, which is what the log line is attributed to.
		:param message:   What went wrong, in one sentence.
		:param exception: The exception that was caught.
		:returns:         The container, as the list a directive's ``run`` returns.
		"""
		logger = getLogger(location)
		logger.error(f"{message}")
		logger.error(f"  {exception.__class__.__name__}: {exception}")
		if exception.__cause__ is not None:
			logger.error(f"    {exception.__cause__.__class__.__name__}: {exception.__cause__}")
		logger.exception(exception)

		container += nodes.paragraph(text=message)

		return [container]
