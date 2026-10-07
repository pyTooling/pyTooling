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
"""Unit tests for :mod:`pyTooling.Documentation`, the doc-string helpers."""
from pyTooling.Documentation import MAXIMUM_SUMMARY_LENGTH, DocumentationError, splitDocString
from pyTooling.Testing       import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Splitting(Testcase):
	"""A doc-string is its summary - the first paragraph - followed by its body."""

	def test_NoDocStringIsTwoEmptyStrings(self) -> None:
		self.assertEqual(("", ""), splitDocString(None))

	def test_ASingleParagraphHasNoBody(self) -> None:
		summary, body = splitDocString("A single sentence.")

		self.assertEqual("A single sentence.", summary)
		self.assertEqual("", body)

	def test_TheBodyIsWhateverFollowsTheFirstBlankLine(self) -> None:
		summary, body = splitDocString("The summary.\n\nThe first paragraph.\n\nThe second paragraph.")

		self.assertEqual("The summary.", summary)
		self.assertEqual("The first paragraph.\n\nThe second paragraph.", body)

	def test_TheDocStringIsDedented(self) -> None:
		"""An indented doc-string is what 'cleandoc' sees in a source file, so both parts arrive dedented."""

		def documented() -> None:
			"""
			The summary.

			The body,
			over two lines.
			"""

		summary, body = splitDocString(documented.__doc__)

		self.assertEqual("The summary.", summary)
		self.assertEqual("The body,\nover two lines.", body)

	def test_AWrappedSummaryKeepsItsLineBreaks(self) -> None:
		"""The split doesn't fold - a caller that needs one line joins the words itself."""
		summary, _ = splitDocString("A summary wrapped\nover two lines.")

		self.assertEqual("A summary wrapped\nover two lines.", summary)


class SummaryLength(Testcase):
	"""A summary is a single sentence, so it is length-limited."""

	def test_TheDefaultIsTwoHundredCharacters(self) -> None:
		self.assertEqual(200, MAXIMUM_SUMMARY_LENGTH)

	def test_ASummaryOfExactlyTheLimitIsAccepted(self) -> None:
		summary, _ = splitDocString("x" * MAXIMUM_SUMMARY_LENGTH)

		self.assertEqual(MAXIMUM_SUMMARY_LENGTH, len(summary))

	def test_OneCharacterMoreIsRejected(self) -> None:
		with self.assertRaises(DocumentationError) as exceptionCapture:
			splitDocString("x" * (MAXIMUM_SUMMARY_LENGTH + 1))

		self.assertEqual(
			"The doc-string's summary is longer than 200 characters.",
			str(exceptionCapture.exception)
		)
		self.assertEqual("Got 201 characters.", exceptionCapture.exception.__notes__[0])

	def test_OnlyTheSummaryIsMeasuredNotTheBody(self) -> None:
		"""A long body is normal - it is the first paragraph that has to stay short."""
		summary, body = splitDocString("The summary.\n\n" + "x" * 1000)

		self.assertEqual("The summary.", summary)
		self.assertEqual(1000, len(body))

	def test_ZeroDisablesTheCheck(self) -> None:
		summary, _ = splitDocString("x" * 1000, maxSummaryLength=0)

		self.assertEqual(1000, len(summary))

	def test_TheLimitIsAParameter(self) -> None:
		summary, _ = splitDocString("x" * 30, maxSummaryLength=30)
		self.assertEqual(30, len(summary))

		with self.assertRaises(DocumentationError) as exceptionCapture:
			splitDocString("x" * 31, maxSummaryLength=30)

		self.assertEqual(
			"The doc-string's summary is longer than 30 characters.",
			str(exceptionCapture.exception)
		)
