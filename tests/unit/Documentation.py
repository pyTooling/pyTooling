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

from sys                     import platform as sys_platform, version_info
from typing                  import Optional as Nullable

from pytest                  import mark

from pyTooling.Documentation import MAXIMUM_SUMMARY_LENGTH, DocumentationError, splitDocString
from pyTooling.Testing       import Testcase

# 'pyTooling[sphinx]' requires Sphinx 9.1, which requires Python 3.12 - so on Python 3.11 the extension can't be
# installed and its testcases can't run. Keyed on the interpreter rather than on an ImportError: from 3.12 on, a
# failed import is a broken test environment and has to fail loudly instead of quietly skipping the testcases -
# and when 3.11 is dropped, this condition is constant and visibly removable.
sphinxIsSupported = version_info >= (3, 12)

if sphinxIsSupported:
	# 'skipif' skips the testcases, but the class bodies below still run when this module is imported, and a
	# signature is evaluated then: its annotations on Python 3.11-3.13, its default values on every version. So no
	# signature may name one of these imports - they are quoted, and a default is a sentinel resolved in the body.
	from packaging.specifiers                          import SpecifierSet

	from pyTooling.Documentation.Sphinx.DependencyTable import DependencyFormat, DependencyTable
	from pyTooling.Documentation.Sphinx.DependencyTable import VersionFormat, formatUnresolvedLicenses
	from pyTooling.Documentation.Sphinx.DependencyTable import readEntrypoints
	from pyTooling.Documentation.Sphinx.Directives      import SphinxExtensionError
	from pyTooling.Documentation.Sphinx.SchemaGraph     import DotGraph, cardinality, compartment
	from pyTooling.Documentation.Sphinx.SchemaGraph     import escapeLabel, renderXMLSchema, typeName


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


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
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

		self.assertEqual((("pyTooling", "yaml"),), entrypoints["yaml"].Packages)
		self.assertIsNone(entrypoints["yaml"].Requirements)

	def test_APackageWithoutAnExtraHasNone(self) -> None:
		entrypoints = readEntrypoints({"package": {"package": "pyTooling"}}, Path("."))

		self.assertEqual((("pyTooling", None),), entrypoints["package"].Packages)

	def test_SeveralPackagesAreDeclaredWithThePluralForm(self) -> None:
		"""``packages`` takes an iterable; ``package`` takes one string. Both are the same statement."""
		entrypoints = readEntrypoints({
			"tuple": {"packages": ("pyTooling[yaml]", "pyTooling[terminal]")},
			"list":  {"packages": ["pyTooling", ]}
		}, Path("."))

		self.assertEqual((("pyTooling", "yaml"), ("pyTooling", "terminal")), entrypoints["tuple"].Packages)
		self.assertEqual((("pyTooling", None),), entrypoints["list"].Packages)

	def test_APluralFieldTakesAnyIterable(self) -> None:
		"""The field is documented as an iterable, so a generator or a set is as good as a tuple or a list."""
		entrypoints = readEntrypoints({
			"generator": {"packages": (name for name in ("pyTooling[yaml]", "pyTooling[terminal]"))},
			"set":       {"packages": {"pyTooling"}}
		}, Path("."))

		self.assertEqual((("pyTooling", "yaml"), ("pyTooling", "terminal")), entrypoints["generator"].Packages)
		self.assertEqual((("pyTooling", None),), entrypoints["set"].Packages)

	def test_SeveralFilesFlattenInTheOrderDeclared(self) -> None:
		"""``files`` reads several trees; a later file's statement wins, as a later ``-r`` reference does."""
		with TemporaryDirectory() as directory:
			root = Path(directory).resolve()
			self._write(root, "first.txt", "pytest ~= 8.0\ncolorama ~= 0.4.6\n")
			self._write(root, "second.txt", "pytest ~= 9.1\n")

			entrypoints = readEntrypoints({"both": {"files": ["first.txt", "second.txt"]}}, root)

		requirements = entrypoints["both"].Requirements
		self.assertEqual({"colorama", "pytest"}, set(requirements))
		self.assertEqual("~=9.1", str(requirements["pytest"].specifier))
		self.assertEqual([root / "first.txt", root / "second.txt"], list(entrypoints["both"].Files))

	def test_APluralFieldRejectsABareString(self) -> None:
		"""A string is an iterable of strings, so 'files': 'requirements.txt' would silently become 16 paths."""
		with self.assertRaises(SphinxExtensionError) as exceptionCapture:
			readEntrypoints({"unittest": {"files": "requirements.txt"}}, Path("."))

		self.assertIn("Use 'file'", str(exceptionCapture.exception))

	def test_ASingularFieldRejectsAnIterable(self) -> None:
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints({"unittest": {"file": ["requirements.txt"]}}, Path("."))

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

	def test_ASingularAndItsPluralTogetherIsRejected(self) -> None:
		"""Exactly one field, so which of the two would win is never a question."""
		with self.assertRaises(SphinxExtensionError):
			readEntrypoints({"unittest": {"file": "a.txt", "files": ["b.txt"]}}, Path("."))

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


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class VersionConstraints(Testcase):
	"""A dependency table prints a constraint for a reader, not for an installer."""

	@staticmethod
	def _format(specifier: str, simplify: bool = True, versionFormat: Nullable["VersionFormat"] = None) -> str:
		if versionFormat is None:
			versionFormat = VersionFormat.All

		return DependencyTable._FormatSpecifier(SpecifierSet(specifier), simplify, versionFormat)

	def test_NoConstraintIsAny(self) -> None:
		self.assertEqual("any", self._format(""))

	def test_OperatorsBecomeTheirSymbols(self) -> None:
		"""'>=' is typography, not syntax, once it is printed in a table."""
		self.assertEqual("≥3.12", self._format(">=3.12"))
		self.assertEqual("≤2.0", self._format("<=2.0", simplify=False))
		self.assertEqual("≠2.0", self._format("!=2.0", simplify=False))
		self.assertEqual("=1.2.3", self._format("==1.2.3"))

	def test_ACompatibleReleaseBecomesItsLowerBound(self) -> None:
		"""'~=0.4.6' says at least 0.4.6; the upper half is the installer's business."""
		self.assertEqual("≥0.4.6", self._format("~=0.4.6"))

	def test_AnUpperBoundIsDropped(self) -> None:
		self.assertEqual("≥3.0", self._format("<4.0,>=3.0"))

	def test_AnExclusionIsDropped(self) -> None:
		self.assertEqual("≥1.0", self._format("!=2.0,>=1.0"))

	def test_AnUpperBoundAloneSurvives(self) -> None:
		"""Simplifying everything away would print nothing, so the constraint stays as it was written."""
		self.assertEqual("<4.0", self._format("<4.0"))

	def test_TheFullFormKeepsEveryPart(self) -> None:
		self.assertEqual("≥3.0, <4.0", self._format("<4.0,>=3.0", simplify=False))
		self.assertEqual("~=0.4.6", self._format("~=0.4.6", simplify=False))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class VersionFormats(Testcase):
	"""A dependency table prints as much of a version as a reader needs, which is rarely all of it."""

	@staticmethod
	def _format(specifier: str, versionFormat: "VersionFormat") -> str:
		return DependencyTable._FormatSpecifier(SpecifierSet(specifier), True, versionFormat)

	def test_TheDefaultIsMajorMinor(self) -> None:
		from pyTooling.Documentation.Sphinx.DependencyTable import DEFAULT_VERSION_FORMAT

		self.assertIs(VersionFormat.MajorMinor, DEFAULT_VERSION_FORMAT)

	def test_EachFormatKeepsItsParts(self) -> None:
		self.assertEqual("≥0", self._format("~=0.4.6", VersionFormat.Major))
		self.assertEqual("≥0.4", self._format("~=0.4.6", VersionFormat.MajorMinor))
		self.assertEqual("≥0.4.6", self._format("~=0.4.6", VersionFormat.MajorMinorPatch))
		self.assertEqual("≥0.4.6", self._format("~=0.4.6", VersionFormat.All))

	def test_AllKeepsWhatTheOthersDrop(self) -> None:
		self.assertEqual("=9.1.2.dev3", self._format("==9.1.2.dev3", VersionFormat.All))
		self.assertEqual("=9.1.2", self._format("==9.1.2.dev3", VersionFormat.MajorMinorPatch))

	def test_AShortVersionIsNotPaddedOut(self) -> None:
		"""'≥9' must not become '≥9.0' - that states a precision the requirement didn't."""
		self.assertEqual("≥9", self._format(">=9", VersionFormat.MajorMinorPatch))

	def test_ShorteningNeverPrintsOneStatementTwice(self) -> None:
		"""'>=1.2.3, >=1.2.9' is one statement at MajorMinor, and a table saying it twice reads as a defect."""
		self.assertEqual("≥1.2", self._format(">=1.2.3,>=1.2.9", VersionFormat.MajorMinor))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class DependencyFormats(Testcase):
	"""What a line of a dependency tree states is the document's choice."""

	def test_TheDefaultStatesEverything(self) -> None:
		from pyTooling.Documentation.Sphinx.DependencyTable import DEFAULT_DEPENDENCY_FORMAT

		self.assertIs(DependencyFormat.PackageVersionLicense, DEFAULT_DEPENDENCY_FORMAT)

	def test_EachFormatSaysWhatItShows(self) -> None:
		self.assertEqual(
			[(False, False), (True, False), (False, True), (True, True)],
			[(member.ShowsVersion, member.ShowsLicense) for member in DependencyFormat]
		)

	def test_TheMembersAreWrittenAsTheyAreSpelled(self) -> None:
		"""A document writes ':dependency-format: PackageVersionLicense', not 'package_version_license'."""
		self.assertEqual("PackageVersionLicense", str(DependencyFormat.PackageVersionLicense))
		self.assertEqual("MajorMinor", str(VersionFormat.MajorMinor))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class UnresolvedLicenseReport(Testcase):
	"""A package needing a license override is reported with what the index published, because that is the reason."""

	def test_OnePackageNamesWhatWasPublished(self) -> None:
		"""The published field is the answer to 'why does this need an override', so it is in the message."""
		message = formatUnresolvedLicenses({"multidict": ("license: Apache License 2.0",)})

		self.assertIn("1 package(s) need a license override", message)
		self.assertIn("license: Apache License 2.0", message)
		self.assertIn("multidict", message)

	def test_PackagesSharingAReasonAreOneGroup(self) -> None:
		"""An ambiguous classifier usually accounts for most of the list, so it is stated once, not per package."""
		classifier = "classifier: License :: OSI Approved :: BSD License"
		message = formatUnresolvedLicenses({"Jinja2": (classifier,), "alabaster": (classifier,), "colorama": (classifier,)})

		self.assertEqual(1, message.count(classifier))
		self.assertIn("Jinja2, alabaster, colorama", message)

	def test_TheBiggestGroupComesFirst(self) -> None:
		"""The statement worth fixing first is the one accounting for the most packages."""
		classifier = "classifier: License :: OSI Approved :: BSD License"
		message = formatUnresolvedLicenses({
			"multidict": ("license: Apache License 2.0",),
			"Jinja2":    (classifier,),
			"alabaster": (classifier,),
		})
		lines = message.splitlines()

		self.assertEqual(f"  {classifier}", lines[1])
		self.assertEqual("    Jinja2, alabaster", lines[2])
		self.assertEqual("  license: Apache License 2.0", lines[3])

	def test_APackageWithoutAnyLicenseInformationSaysSo(self) -> None:
		"""An index publishing nothing at all must not render as an empty reason."""
		message = formatUnresolvedLicenses({"mystery": ()})

		self.assertIn("the index published no license information", message)

	def test_SeveralPublishedFieldsAreJoined(self) -> None:
		"""A release can publish both a 'license' field and a classifier, and neither of them resolved."""
		message = formatUnresolvedLicenses({
			"sphinxcontrib-jsmath": ("license: BSD", "classifier: License :: OSI Approved :: BSD License")
		})

		self.assertIn("license: BSD; classifier: License :: OSI Approved :: BSD License", message)


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class RecordLabels(Testcase):
	"""A Graphviz record label is assembled as text, so escaping and grouping are what keep it legal."""

	def test_EveryMetacharacterIsEscaped(self) -> None:
		"""A name containing record syntax must not be read as record syntax."""
		self.assertEqual("\\{a\\|b\\}", escapeLabel("{a|b}"))

	def test_TheBackslashIsEscapedFirst(self) -> None:
		"""Escaping the backslash last would escape the backslashes the other characters just gained."""
		self.assertEqual("\\\\", escapeLabel("\\"))

	def test_TextWithoutMetacharactersIsUnchanged(self) -> None:
		"""A type name is text, and the common case must not be rewritten."""
		self.assertEqual("xsd:string", escapeLabel("xsd:string"))

	def test_EveryRowEndsLeftAligned(self) -> None:
		"""Rows centre themselves without the '\\l', which makes a record's compartments ragged."""
		self.assertEqual("a\\lb\\l", compartment(("a", "b")))

	def test_AnEmptyCompartmentIsASpace(self) -> None:
		"""An empty compartment collapses, which makes the records of a graph differently shaped."""
		self.assertEqual(" ", compartment(()))

	def test_ACompartmentEscapesItsRows(self) -> None:
		"""The rows arrive unescaped, so the compartment is where they are made safe."""
		self.assertEqual("a\\|b\\l", compartment(("a|b",)))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Graphs(Testcase):
	"""The DOT a renderer states node by node."""

	def test_AnEmptyGraphCarriesTheSharedAttributes(self) -> None:
		"""Where the graph flows and how a record is shaped belongs to every schema graph alike."""
		dot = str(DotGraph())

		self.assertTrue(dot.startswith("digraph schema {"))
		self.assertIn("rankdir=LR;", dot)
		self.assertIn("node [shape=record", dot)
		self.assertTrue(dot.endswith("}"))

	def test_ANodeQuotesItsIdentifierAndEveryAttributeValue(self) -> None:
		"""Quoting without exception is always legal in DOT and saves a caller from deciding per value."""
		graph = DotGraph()
		graph.AddNode("a", "A", shape="doublecircle")

		self.assertIn('\t"a" [label="A", shape="doublecircle"];', str(graph))

	def test_AnEdgeWithoutAttributesHasNoBrackets(self) -> None:
		"""An empty attribute list is not written at all, rather than written empty."""
		graph = DotGraph()
		graph.AddEdge("a", "b")

		self.assertIn('\t"a" -> "b";', str(graph))

	def test_AnEdgeStatesItsAttributes(self) -> None:
		"""An edge's label is what carries the cardinality."""
		graph = DotGraph()
		graph.AddEdge("a", "b", label="x [0..*]")

		self.assertIn('\t"a" -> "b" [label="x [0..*]"];', str(graph))

	def test_ARecordIsATitleAndItsCompartments(self) -> None:
		"""The title is written in guillemets, and every compartment follows it behind a bar."""
		graph = DotGraph()
		graph.AddRecord("t", "t", (("a", "b"), ()))

		self.assertIn('\t"t" [label="{«t»|a\\lb\\l| }"];', str(graph))

	def test_AGraphIsNamed(self) -> None:
		"""Graphviz uses the name as the drawing's identifier."""
		self.assertTrue(str(DotGraph("other")).startswith("digraph other {"))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class XMLSchemaGraphs(Testcase):
	"""The XML schema pyTooling ships, drawn as the 'xsd-graph' directive draws it."""

	@staticmethod
	def _Schema() -> Path:
		"""
		Locate the shipped test-report schema.

		It is read from the resource package rather than from a relative path, so the testcases don't depend on the
		directory pytest was started in.

		:returns: Path of :file:`TestReport-v0.1.xsd` in :mod:`pyTooling.Resources`.
		"""
		from pyTooling        import Resources
		from pyTooling.Common import getResourceFile

		return getResourceFile(Resources, "TestReport-v0.1.xsd")

	def test_EveryComplexTypeIsARecord(self) -> None:
		"""A complex type is a box; its attributes and simple-typed children are its compartments."""
		dot = renderXMLSchema(self._Schema())

		for typeIdentifier in ("testreport", "testsuite", "testcase"):
			self.assertIn(f'"{typeIdentifier}" [label="{{«{typeIdentifier}»|', dot)

	def test_AnAttributeIsNamedWithItsType(self) -> None:
		"""A builtin type keeps the 'xsd:' prefix its namespace stands for."""
		self.assertIn("duration : xsd:float", renderXMLSchema(self._Schema()))

	def test_ContainmentIsAnEdgeCarryingTheCardinality(self) -> None:
		"""A complex-typed child is an edge, so containment is structure rather than a repeated type name."""
		self.assertIn('"testreport" -> "testsuite" [label="Testsuite [0..*]"];', renderXMLSchema(self._Schema()))

	def test_ATestSuiteNestsInItself(self) -> None:
		"""The edge to itself is what the format has over JUnit XML, and what the diagram exists to show."""
		self.assertIn('"testsuite" -> "testsuite" [label="Testsuite [0..*]"];', renderXMLSchema(self._Schema()))

	def test_TheRootElementIsADoubleCircle(self) -> None:
		"""A document starts somewhere, and the picture has to say where."""
		dot = renderXMLSchema(self._Schema())

		self.assertIn('"<TestReport>" [label="TestReport", shape="doublecircle"', dot)
		self.assertIn('"<TestReport>" -> "testreport" [label="root"];', dot)

	def test_AnEnumerationBecomesItsOwnNode(self) -> None:
		"""A simple type earns a node only when it has values a type name cannot say."""
		dot = renderXMLSchema(self._Schema())

		self.assertIn('"status" [label="{«status»|passed\\lfailed\\l', dot)
		self.assertIn('"testcase" -> "status" [style="dashed"', dot)

	def test_ASimpleTypeThatIsNoEnumerationGetsNoNode(self) -> None:
		"""'preservingstring' is named in the compartments and drawn nowhere - it has nothing to show."""
		dot = renderXMLSchema(self._Schema())

		self.assertIn("Description : preservingstring", dot)
		self.assertNotIn('"preservingstring" [', dot)

	def test_TheSameSchemaAlwaysDrawsTheSameGraph(self) -> None:
		"""A rebuilt page is only comparable to the one before it when the drawing doesn't reshuffle."""
		self.assertEqual(renderXMLSchema(self._Schema()), renderXMLSchema(self._Schema()))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class SchemaGraphDetails(Testcase):
	"""The parts of an XML schema graph that the shipped schema doesn't exercise."""

	_SCHEMA = dedent("""\
		<?xml version="1.0" encoding="UTF-8"?>
		<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
			<xs:simpleType name="charlie">
				<xs:restriction base="xs:string"><xs:enumeration value="c"/></xs:restriction>
			</xs:simpleType>
			<xs:simpleType name="alpha">
				<xs:restriction base="xs:string"><xs:enumeration value="a"/></xs:restriction>
			</xs:simpleType>
			<xs:simpleType name="bravo">
				<xs:restriction base="xs:string"><xs:enumeration value="b"/></xs:restriction>
			</xs:simpleType>
			<xs:complexType name="root">
				<xs:sequence>
					<xs:element name="One" type="alpha"/>
					<xs:element name="Two" type="bravo" maxOccurs="unbounded"/>
					<xs:element name="Three" type="charlie"/>
				</xs:sequence>
			</xs:complexType>
			<xs:element name="Root" type="root"/>
		</xs:schema>
		""")

	def _Render(self, directory: str) -> str:
		"""
		Write the schema above into a directory and render it.

		:param directory: Directory to write the schema into.
		:returns:         The graph in the DOT language.
		"""
		schema = Path(directory) / "Ordering.xsd"
		schema.write_text(self._SCHEMA, encoding="utf-8")

		return renderXMLSchema(schema)

	def test_EnumerationsAreDrawnInAStableOrder(self) -> None:
		"""They are collected in a set, whose iteration order varies between interpreter runs unless it is sorted."""
		with TemporaryDirectory() as directory:
			dot = self._Render(directory)

		positions = [dot.index(f'"{name}" [label="{{«{name}»') for name in ("alpha", "bravo", "charlie")]

		self.assertEqual(sorted(positions), positions)

	def test_AnUnboundedUpperLimitIsAStar(self) -> None:
		"""'maxOccurs="unbounded"' has no number to print."""
		with TemporaryDirectory() as directory:
			dot = self._Render(directory)

		self.assertIn("Two : bravo [1..*]", dot)


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class TypeNames(Testcase):
	"""What a type is called in a record, which is not always what it is called in the schema."""

	class _Type:
		"""A stand-in for an 'xmlschema' type, which only has to answer for its name."""

		def __init__(self, name: Nullable[str]) -> None:
			self.name = name

	def test_ABuiltinTypeKeepsTheShortPrefix(self) -> None:
		"""The namespace it is spelled with is 40 characters that say nothing in a diagram."""
		builtin = self._Type("{http://www.w3.org/2001/XMLSchema}string")

		self.assertEqual("xsd:string", typeName(builtin))

	def test_ANamedTypeIsItsName(self) -> None:
		"""A type declared by the schema is already short."""
		self.assertEqual("status", typeName(self._Type("status")))

	def test_AnAnonymousTypeSaysSo(self) -> None:
		"""An inline type has no name, and an empty label would be read as a missing one."""
		self.assertEqual("(anonymous)", typeName(self._Type(None)))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Cardinalities(Testcase):
	"""How often an element may occur, as a record row states it."""

	class _Element:
		"""A stand-in for an 'xmlschema' element, which only has to answer for its occurrence."""

		def __init__(self, lower: int, upper: Nullable[int]) -> None:
			self.occurs = (lower, upper)

	def test_ABoundedOccurrenceIsTwoNumbers(self) -> None:
		"""The common case, and the one an optional element is spelled with."""
		self.assertEqual("0..1", cardinality(self._Element(0, 1)))

	def test_AnUnboundedOccurrenceIsAStar(self) -> None:
		"""'None' is what 'unbounded' arrives as, and it has no number to print."""
		self.assertEqual("1..*", cardinality(self._Element(1, None)))
