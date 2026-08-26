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
The ReST roles shared by pyTooling's documentation and its sibling projects.

Every project used to declare these in its own :file:`doc/prolog.inc`, as ReST source re-parsed into every document
of every project - and eighteen hand-copied files had already drifted apart. Registering them from an extension
makes one declaration serve all of them, and puts the styling in a stylesheet instead of a ``raw:: html`` block.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension registering these, and what else it brings.
"""
from typing                     import Any, Optional as Nullable

from docutils                   import nodes
from docutils.parsers.rst.roles import code_role
from docutils.parsers.rst.states import Inliner
from docutils.utils             import unescape

from pyTooling.Decorators       import export


__all__ = ["STYLE_ROLES", "PYTHON_CODE_ROLE"]

#: The style roles, mapping a role's name to the CSS classes it applies.
STYLE_ROLES = {
	"bolditalic": ("bolditalic", ),
	"underline":  ("underline", ),
	"strike":     ("strike", ),
	"xlarge":     ("xlarge", ),
	"red":        ("colorred", ),
	"green":      ("colorgreen", ),
	"blue":       ("colorblue", ),
	"purple":     ("colorpurple", ),
	"deletion":   ("colorred", "strike"),
	"addition":   ("colorgreen", ),
}

#: Name of the role rendering inline Python code.
PYTHON_CODE_ROLE = "pycode"


@export
def styleRole(
	name: str,
	rawText: str,
	text: str,
	lineNumber: int,
	inliner: Inliner,
	options: Nullable[dict[str, Any]] = None,
	content: Nullable[list[str]] = None
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
	"""
	Render inline text with the CSS classes registered for the role's name.

	This is what ``.. role:: red`` with ``:class: colorred`` does in a prolog, without the prolog: the role's name is
	looked up in :data:`STYLE_ROLES` and the classes it maps to are put on an :class:`~docutils.nodes.inline` node.

	:param name:       Name the role was invoked by, which is what selects the classes.
	:param rawText:    The role's text including its markup.
	:param text:       The role's text with the markup removed.
	:param lineNumber: Line the role was used on.
	:param inliner:    The inliner that called this role.
	:param options:    Options given to the role; unused, because the classes come from the role's name.
	:param content:    Content given to the role; unused.
	:returns:          Tuple of the produced nodes and the system messages, as a docutils role returns.
	"""
	classes = STYLE_ROLES.get(name, (name, ))

	return [nodes.inline(rawText, unescape(text), classes=list(classes))], []


@export
def pythonCodeRole(
	name: str,
	rawText: str,
	text: str,
	lineNumber: int,
	inliner: Inliner,
	options: Nullable[dict[str, Any]] = None,
	content: Nullable[list[str]] = None
) -> tuple[list[nodes.Node], list[nodes.system_message]]:
	r"""
	Render inline Python code, syntax-highlighted.

	The docutils ``code`` role does the work; this fixes its language to Python and adds the ``highlight`` class, so
	a page writes ``:pycode:`isinstance(x, int)``` instead of repeating the options at every use.

	:param name:       Name the role was invoked by; unused, because the language is fixed.
	:param rawText:    The role's text including its markup.
	:param text:       The role's text with the markup removed.
	:param lineNumber: Line the role was used on.
	:param inliner:    The inliner that called this role.
	:param options:    Options given to the role; replaced by the fixed ones.
	:param content:    Content given to the role, handed to the ``code`` role unchanged.
	:returns:          Tuple of the produced nodes and the system messages, as a docutils role returns.
	"""
	options = {"language": "python", "classes": ["highlight"]}

	return code_role(name, rawText, text, lineNumber, inliner, options, [] if content is None else content)
