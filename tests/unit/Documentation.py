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
"""Unit tests for :mod:`pyTooling.Documentation`, the doc-string helpers and the Sphinx extension."""
from pathlib                 import Path
from tempfile                import TemporaryDirectory
from textwrap                import dedent

from sys                     import platform as sys_platform

from pytest                  import mark

from pyTooling.Documentation import MAXIMUM_SUMMARY_LENGTH, DocumentationError, splitDocString
from pyTooling.Testing       import Testcase

try:
	from pyTooling.Documentation.Sphinx.DependencyTable import readEntrypoints
	from pyTooling.Documentation.Sphinx.Directives      import SphinxExtensionError

	sphinxIsInstalled = True
except ImportError:  # pragma: no cover
	# 'pyTooling[sphinx]' requires Sphinx 9.1, which requires Python 3.12 - so on Python 3.11 the extension can't be
	# installed and its testcases can't run.
	sphinxIsInstalled = False


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


@mark.skipif(not sphinxIsInstalled, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Entrypoints(Testcase):
	"""``pyTooling_dependency_requirements`` is read while :file:`conf.py` is processed, so its errors end the build."""

	@staticmethod
	def _write(directory: Path, name: str, content: str) -> Path:
		path = directory / name
		path.write_text(dedent(content).lstrip(), encoding="utf-8")

		return path

	def test_AFileEntrypointIsReadRightAway(self) -> None:
		"""A requirements file is read here, not when a table is built."""
		with TemporaryDirectory() as directory:
			root = Path(directory).resolve()
			self._write(root, "requirements.txt", """
				pytest ~= 9.1
				colorama ~= 0.4.6
			""")

			entrypoints = readEntrypoints({"unittest": {"file": "requirements.txt"}}, root)

		self.assertEqual({"colorama", "pytest"}, set(entrypoints["unittest"].Requirements))
		self.assertEqual((root / "requirements.txt",), entrypoints["unittest"].Files)

	def test_AnIncludedFileIsListedToo(self) -> None:
		"""Every file read is remembered, so a change to an include rebuilds the document naming the entrypoint."""
		with TemporaryDirectory() as directory:
			root = Path(directory).resolve()
			self._write(root, "base.txt", "colorama ~= 0.4.6\n")
			self._write(root, "requirements.txt", """
				-r base.txt
				pytest ~= 9.1
			""")

			entrypoints = readEntrypoints({"unittest": {"file": "requirements.txt"}}, root)

		self.assertEqual([root / "requirements.txt", root / "base.txt"], list(entrypoints["unittest"].Files))

	@mark.skipif(sys_platform == "win32", reason="Creating a symbolic link needs a privilege Windows doesn't grant.")
	def test_TheWholeTreeIsSpelledOneWay(self) -> None:
		"""A directory reachable under two names must not put both spellings into the tree.

		This is what macOS (:file:`/var` is :file:`/private/var`) and Windows (:file:`RUNNER~1` is
		:file:`runneradmin`) hand a build, and it made the file and its includes disagree about their own parent.
		"""
		with TemporaryDirectory() as directory:
			real = Path(directory).resolve() / "real"
			real.mkdir()
			self._write(real, "base.txt", "colorama ~= 0.4.6\n")
			self._write(real, "requirements.txt", """
				-r base.txt
				pytest ~= 9.1
			""")

			link = Path(directory).resolve() / "link"
			link.symlink_to(real)

			files = readEntrypoints({"unittest": {"file": "requirements.txt"}}, link)["unittest"].Files

		self.assertEqual([real / "requirements.txt", real / "base.txt"], list(files))

	def test_APackageEntrypointIsNotResolvedYet(self) -> None:
		"""A package can only be resolved by asking the index, so it carries its name and extra until a table asks."""
		entrypoints = readEntrypoints({"yaml": {"package": "pyTooling[yaml]"}}, Path("."))

		self.assertEqual("pyTooling", entrypoints["yaml"].PackageName)
		self.assertEqual("yaml", entrypoints["yaml"].Extra)
		self.assertIsNone(entrypoints["yaml"].Requirements)

	def test_APackageWithoutAnExtraHasNone(self) -> None:
		entrypoints = readEntrypoints({"package": {"package": "pyTooling"}}, Path("."))

		self.assertEqual("pyTooling", entrypoints["package"].PackageName)
		self.assertIsNone(entrypoints["package"].Extra)

	def test_AMissingFileNamesTheIdentifier(self) -> None:
		"""The message has to say which entry is wrong - the path alone doesn't."""
		with TemporaryDirectory() as directory:
			with self.assertRaises(SphinxExtensionError) as exceptionCapture:
				readEntrypoints({"unittest": {"file": "nothing.txt"}}, Path(directory))

		self.assertIn("[unittest]", str(exceptionCapture.exception))

	def test_NeitherFileNorPackageIsRejected(self) -> None:
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints({"unittest": {}}, Path("."))

	def test_BothFileAndPackageIsRejected(self) -> None:
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints({"unittest": {"file": "requirements.txt", "package": "pyTooling"}}, Path("."))

	def test_AnUnknownFieldIsRejected(self) -> None:
		"""A typo is an error rather than a silently ignored key."""
		with self.assertRaises(SphinxExtensionError) as exceptionCapture:
			readEntrypoints({"unittest": {"files": "requirements.txt"}}, Path("."))

		self.assertIn("files", str(exceptionCapture.exception))

	def test_ADeclarationThatIsNoDictionaryIsRejected(self) -> None:
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints({"unittest": "requirements.txt"}, Path("."))

	def test_AConfigurationThatIsNoDictionaryIsRejected(self) -> None:
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints(["requirements.txt"], Path("."))
