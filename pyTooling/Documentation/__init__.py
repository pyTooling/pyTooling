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
Helper functions to work with doc-strings.

.. hint::

   See :ref:`high-level help <DOC>` for explanations and usage examples.

.. seealso::

   :deco:`pyTooling.Decorators.InheritDocString`
      |rarr| Merges a base-class' doc-string into a derived entity, using the split offered here.
   :func:`pyTooling.Packaging.extractVersionInformation`
      |rarr| Reads a package's short description from the summary of its module doc-string.
"""
from __future__           import annotations

from inspect              import cleandoc
from typing               import Optional as Nullable

from pyTooling.Decorators import export
from pyTooling.Exceptions import ToolingException


__all__ = ["MAXIMUM_SUMMARY_LENGTH"]

MAXIMUM_SUMMARY_LENGTH = 200
"""
Number of characters a doc-string's summary may have by default.

A summary is a single sentence, so a line of the usual 120 columns plus room for an embedded link or other markup is
a generous bound. A first paragraph longer than that is a body that lost its summary.
"""


@export
class DocumentationError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Documentation`."""


@export
def splitDocString(
	docString: Nullable[str],
	maxSummaryLength: int = MAXIMUM_SUMMARY_LENGTH
) -> tuple[str, str]:
	"""
	Split a doc-string into its summary and its body.

	The doc-string is dedented with :func:`inspect.cleandoc` first. The summary is the first paragraph, the body is
	whatever follows the first blank line. Both are empty strings if the doc-string is ``None``, and the body is an
	empty string if the doc-string is a single paragraph, so a caller needs no special case for either.

	A summary is a single sentence, so its length is bounded by ``maxSummaryLength``; everything else belongs behind
	a blank line.

	:param docString:           The doc-string to split, or ``None``.
	:param maxSummaryLength:    Optional, number of characters the summary may have. Pass ``0`` for no limit.
	                            Default: :data:`DEFAULT_MAXIMUM_SUMMARY_LENGTH`.
	:returns:                   A tuple of summary and body.
	:raises DocumentationError: If the summary is longer than ``maxSummaryLength`` characters.
	"""
	if docString is None:
		return "", ""

	summary, _, body = cleandoc(docString).partition("\n\n")

	if 0 < maxSummaryLength < len(summary):
		ex = DocumentationError(f"The doc-string's summary is longer than {maxSummaryLength} characters.")
		ex.add_note(f"Got {len(summary)} characters.")
		ex.add_note("A summary is the first sentence of a doc-string; everything else belongs behind a blank line.")
		raise ex

	return summary, body
