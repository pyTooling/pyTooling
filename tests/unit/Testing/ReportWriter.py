# ==================================================================================================================== #
#             _____           _ _             _____         _   _                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__  ___| |_(_)_ __   __ _                                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \/ __| __| | '_ \ / _` |                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/\__ \ |_| | | | | (_| |                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___||___/\__|_|_| |_|\__, |                                         #
# |_|    |___/                          |___/                           |___/                                          #
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
Unit tests for :mod:`pyTooling.Testing.ReportWriter`, which writes a session's results as a nested XML document.

The writer reads a handful of fields from each pytest report, so a testcase can hand it stand-ins and look at the
document it produces - without starting pytest in a subprocess, where nothing measures what was executed.
"""
from pathlib               import Path
from tempfile              import TemporaryDirectory
from xml.etree.ElementTree import Element, parse as xml_parse

from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Report:
	"""
	A stand-in for pytest's ``TestReport``, carrying only the fields the writer reads.

	Building one is how a testcase states a situation - a failure in the setup phase, a testcase carrying titles -
	that a real session would need a fixture, a plugin and a subprocess to produce.
	"""

	def __init__(
		self,
		nodeID: str,
		status: str = "passed",
		when: str = "call",
		duration: float = 0.25,
		message: str = "",
		**names: str
	) -> None:
		"""
		Initializes a stand-in report.

		:param nodeID:   Node ID of the testcase, whose parts name the test suite levels.
		:param status:   One of ``passed``, ``failed`` or ``skipped``.
		:param when:     Phase the report belongs to: ``setup``, ``call`` or ``teardown``.
		:param duration: Duration of that phase in seconds.
		:param message:  Text of the failure, if it failed.
		:param names:    Names the item carries, as the plugin attaches them: ``title``, ``summary``,
		                 ``description``, ``testsuiteTitle``, ...
		"""
		self.nodeid =          nodeID
		self.when =            when
		self.duration =        duration
		self.user_properties = list(names.items())
		self.longrepr =        message if message != "" else None
		self.failed =          status == "failed"
		self.skipped =         status == "skipped"


class Document(Testcase):
	"""The document the writer assembles from the reports it collects."""
	@staticmethod
	def _Write(*reports: Report) -> Element:
		"""
		Hand the reports to a writer and return the root of the document it wrote.

		:param reports: The reports to collect, in the order a session would produce them.
		:returns:       Root element of the written document.
		"""
		from pyTooling.Testing.ReportWriter import TestReportWriter

		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "TestReport.xml"
			writer = TestReportWriter(path)

			for report in reports:
				writer.pytest_runtest_logreport(report)

			writer.pytest_sessionfinish(None, 0)

			return xml_parse(path).getroot()

	def test_TheDirectoryIsCreated(self) -> None:
		"""'report/unit/' rarely exists when a pipeline asks for a report in it."""
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))

		self.assertEqual("TestReport", root.tag)

	def test_TheReportNamesNeitherItsGeneratorNorItsHost(self) -> None:
		"""The version is the schema's, and a hostname is private information a consumer has no use for."""
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))

		self.assertIsNone(root.get("tool"))
		self.assertIsNone(root.get("version"))
		self.assertIsNone(root.get("hostname"))

	def test_TheReportPointsAtItsSchema(self) -> None:
		"""So a reader can validate the file without being told where the schema is."""
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))

		# The document is written with the 'xsi:' prefix; parsing it expands the prefix to the namespace URI.
		schemaLocation = "{http://www.w3.org/2001/XMLSchema-instance}noNamespaceSchemaLocation"

		self.assertEqual("TestReport-v0.1.xsd", root.get(schemaLocation))

	def test_TestsuitesNest(self) -> None:
		"""What a dotted 'classname' cannot express: one element per level."""
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))

		tests = root.find("Testsuite")
		unit = tests.find("Testsuite")
		versioning = unit.find("Testsuite")
		comparison = versioning.find("Testsuite")

		self.assertEqual("tests", tests.get("name"))
		self.assertEqual("unit", unit.get("name"))
		self.assertEqual("Versioning", versioning.get("name"), "The module keeps its name, without the suffix.")
		self.assertEqual("Comparison", comparison.get("name"))
		self.assertEqual("test_Newer", comparison.find("Testcase").get("name"))

	def test_TwoTestcasesOfOneClassShareTheirLevels(self) -> None:
		root = self._Write(
			Report("tests/unit/Versioning.py::Comparison::test_Newer"),
			Report("tests/unit/Versioning.py::Comparison::test_Older")
		)

		comparison = root.find("Testsuite/Testsuite/Testsuite/Testsuite")

		self.assertEqual(1, len(root.findall("Testsuite")), "The root level was created twice.")
		self.assertEqual(2, len(comparison.findall("Testcase")))

	def test_ATestcaseCarriesItsNodeID(self) -> None:
		"""The ID selects the testcase, so it is in the document even though the levels repeat it."""
		nodeID = "tests/unit/Versioning.py::Comparison::test_Newer"
		root = self._Write(Report(nodeID))

		self.assertEqual(nodeID, root.find(".//Testcase").get("nodeID"))

	def test_TheDurationIsTheSumOfThePhases(self) -> None:
		nodeID = "tests/unit/Versioning.py::Comparison::test_Newer"
		root = self._Write(
			Report(nodeID, when="setup", duration=0.5),
			Report(nodeID, when="call", duration=0.25),
			Report(nodeID, when="teardown", duration=0.125)
		)

		self.assertEqual("0.875000", root.find(".//Testcase").get("duration"))
		self.assertEqual("0.875000", root.get("duration"))

	def test_TheNamesBecomeElements(self) -> None:
		"""A title is prose, so it is an element rather than an attribute."""
		root = self._Write(Report(
			"tests/unit/Versioning.py::Comparison::test_Newer",
			title="A newer version compares greater.",
			summary="Compare two versions.",
			description="Compare two versions.\n\nOnly the minor number differs.",
			testsuiteTitle="Version comparison."
		))

		testcase = root.find(".//Testcase")
		comparison = root.find("Testsuite/Testsuite/Testsuite/Testsuite")

		self.assertEqual("A newer version compares greater.", testcase.find("Title").text)
		self.assertEqual("Compare two versions.", testcase.find("Summary").text)
		self.assertEqual("Compare two versions.\n\nOnly the minor number differs.", testcase.find("Description").text)
		self.assertEqual("Version comparison.", comparison.find("Title").text)

	def test_AnUnmarkedTestcaseCarriesNoNames(self) -> None:
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))
		testcase = root.find(".//Testcase")

		self.assertIsNone(testcase.find("Title"))
		self.assertIsNone(testcase.find("Summary"))
		self.assertIsNone(testcase.find("Description"))

	def test_ATestsuiteIsTitledOnce(self) -> None:
		"""Every testcase of a class repeats its test suite's names; the element must not."""
		root = self._Write(
			Report("tests/unit/Versioning.py::Comparison::test_Newer", testsuiteTitle="Version comparison."),
			Report("tests/unit/Versioning.py::Comparison::test_Older", testsuiteTitle="Version comparison.")
		)

		comparison = root.find("Testsuite/Testsuite/Testsuite/Testsuite")

		self.assertEqual(1, len(comparison.findall("Title")))


class Statuses(Testcase):
	"""A phase decides what a testcase's status is, and the root counts them."""
	@staticmethod
	def _Write(*reports: Report) -> Element:
		"""
		Hand the reports to a writer and return the root of the document it wrote.

		:param reports: The reports to collect.
		:returns:       Root element of the written document.
		"""
		return Document._Write(*reports)

	def test_APassingTestcase(self) -> None:
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer"))

		self.assertEqual("passed", root.find(".//Testcase").get("status"))
		self.assertEqual("1", root.get("tests"))
		self.assertEqual("0", root.get("failures"))

	def test_AFailingTestcaseCarriesItsMessage(self) -> None:
		root = self._Write(Report(
			"tests/unit/Versioning.py::Comparison::test_Newer",
			status="failed",
			message="assert 1 > 2"
		))
		testcase = root.find(".//Testcase")

		self.assertEqual("failed", testcase.get("status"))
		self.assertEqual("assert 1 > 2", testcase.find("Message").text)
		self.assertEqual("1", root.get("failures"))

	def test_AFailureOutsideTheCallPhaseIsAnError(self) -> None:
		"""A testcase that never ran didn't fail - its fixture did."""
		root = self._Write(Report(
			"tests/unit/Versioning.py::Comparison::test_Newer",
			status="failed",
			when="setup",
			message="fixture 'database' not found"
		))

		self.assertEqual("errored", root.find(".//Testcase").get("status"))
		self.assertEqual("1", root.get("errors"))
		self.assertEqual("0", root.get("failures"))

	def test_ASkippedTestcase(self) -> None:
		root = self._Write(Report("tests/unit/Versioning.py::Comparison::test_Newer", status="skipped"))

		self.assertEqual("skipped", root.find(".//Testcase").get("status"))
		self.assertEqual("1", root.get("skipped"))

	def test_TheCountsAddUp(self) -> None:
		root = self._Write(
			Report("tests/unit/A.py::S::test_1"),
			Report("tests/unit/A.py::S::test_2", status="failed", message="boom"),
			Report("tests/unit/A.py::S::test_3", status="skipped"),
			Report("tests/unit/A.py::S::test_4", status="failed", when="teardown", message="boom")
		)

		self.assertEqual("4", root.get("tests"))
		self.assertEqual("1", root.get("failures"))
		self.assertEqual("1", root.get("errors"))
		self.assertEqual("1", root.get("skipped"))


class PluginWiring(Testcase):
	"""The two hooks that connect the writer to a session: the switch, and what the switch turns on."""
	def test_TheOptionIsOffered(self) -> None:
		from pyTooling.Testing.ReportWriter import pytest_addoption

		added = []

		class Group:
			@staticmethod
			def addoption(*arguments: str, **keywordArguments: object) -> None:
				added.append((arguments, keywordArguments))

		class Parser:
			@staticmethod
			def getgroup(name: str) -> Group:
				self.assertEqual("pyTooling", name)
				return Group()

		pytest_addoption(Parser())

		self.assertEqual(1, len(added))
		self.assertIn("--pytooling-xml", added[0][0])
		self.assertIsNone(added[0][1]["default"], "Without the switch, no report is written.")

	def test_WithoutThePathNothingIsRegistered(self) -> None:
		from pyTooling.Testing.ReportWriter import pytest_configure

		configuration = self._Configuration(None)
		pytest_configure(configuration)

		self.assertEqual([], configuration.pluginmanager.registered)
		self.assertEqual({}, configuration.stash)

	def test_WithThePathTheWriterIsRegistered(self) -> None:
		from pyTooling.Testing.ReportWriter import TestReportWriter, pytest_configure, REPORT_WRITER_KEY

		configuration = self._Configuration("report/unit/TestReport.xml")
		pytest_configure(configuration)

		self.assertEqual(1, len(configuration.pluginmanager.registered))
		self.assertIsInstance(configuration.stash[REPORT_WRITER_KEY], TestReportWriter)
		self.assertIs(configuration.stash[REPORT_WRITER_KEY], configuration.pluginmanager.registered[0][0])

	@staticmethod
	def _Configuration(path: str) -> object:
		"""
		A stand-in for pytest's ``Config``, offering the option and the two registries the hook writes to.

		:param path: What ``--pytooling-xml`` was set to, or ``None`` if it wasn't.
		:returns:    The stand-in configuration.
		"""
		class PluginManager:
			def __init__(self) -> None:
				self.registered = []

			def register(self, plugin: object, name: str) -> None:
				self.registered.append((plugin, name))

		class Configuration:
			def __init__(self) -> None:
				self.stash = {}
				self.pluginmanager = PluginManager()

			@staticmethod
			def getoption(name: str) -> str:
				return path if name == "--pytooling-xml" else None

		return Configuration()
