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
#
"""
A pytest plugin writing a test report in :ref:`pyTooling's own format <TESTING/ReportFormat>`.

JUnit XML cannot express two things a marked test suite has: test suites **nest**, where JUnit flattens them into a
dotted ``classname``; and every item carries **four names** - an identifier, a title, a summary and a description -
where JUnit has one name and a bag of flat ``<property>`` pairs.

This writer is opt-in through ``--pytooling-xml=PATH`` and runs happily alongside ``--junit-xml``, so a pipeline
keeps the format its dashboard understands while the richer file is produced from the same reports.

The format's version is the version of its schema - :file:`TestReport-v0.1.xsd` today - so a later version is added
beside it and a reader knows from ``xsi:noNamespaceSchemaLocation`` which one it is holding.

.. todo:: TESTING::ReportWriter Name the generator in a ``<Generator>`` element

   The tool that wrote a report is not part of the format's version, so it is no longer an attribute on the root
   element. Where it belongs is an element of its own at root level, carrying the tool's name and version and
   whatever further meta information a tool wants to add.

.. todo:: TESTING::ReportWriter Add a ``<TestRun>`` level between the report and its test suites

   A run happens on one machine, in one environment, at one time - so a report can hold several of them, and the
   things that describe a run belong to the run rather than to the report:

   .. code-block:: text

      <TestReport>
        <TestRun timestamp="..." duration="...">
          <Environment>
            <Hostname>...</Hostname>
            <OperatingSystem>...</OperatingSystem>
          </Environment>
          <Summary>...</Summary>
          <Description>...</Description>
          <Testsuite ... />
        </TestRun>
      </TestReport>

   The environment is optional, which is what makes a hostname acceptable there: it is written when whoever
   generates the report decides it belongs in it, not by default.

.. hint::

   See :ref:`high-level help <TESTING/ReportFormat>` for the schema and an example.
"""
from datetime              import datetime, timezone
from pathlib               import Path
from typing                import Any, TypedDict, Optional as Nullable
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent

from pytest                  import Config, Parser, Session, StashKey
from pyTooling.Decorators    import export
from pyTooling.MetaClasses   import ExtendedType
from pyTooling.Testing.PyTest import hierarchyKey


__all__ = ["SCHEMA_VERSION_LATEST", "SCHEMA_FILES", "REPORT_WRITER_KEY"]


SCHEMA_VERSION_LATEST = "v0.1"   #: Latest version of the report format, and the one this writer produces.

SCHEMA_FILES: dict[str, str] = {
	"v0.1": "TestReport-v0.1.xsd",
}   #: Schema file per format version, so a later version is added beside the one in use, not instead of it.

REPORT_WRITER_KEY: StashKey["TestReportWriter"] = StashKey()   #: Where the writer is stashed on the configuration.


class _Result(TypedDict, total=False):
	"""What is collected per testcase, assembled from the reports of its phases."""

	nodeID:               str    #: Node ID of the testcase, whose parts name the test suite levels.
	duration:             float  #: Sum of the durations of the testcase's phases.
	message:              str    #: Text of the failure, or an empty string.
	status:               str    #: ``passed``, ``failed``, ``errored`` or ``skipped``.
	title:                str    #: Title of the testcase, if it is marked.
	summary:              str    #: Summary of the testcase, if its doc-string has one.
	description:          str    #: Description of the testcase, if its doc-string has one.


@export
class TestReportWriter(metaclass=ExtendedType, slots=True):
	"""
	Collects the reports of a session and writes them as one nested XML document.

	The nesting comes from the dotted ``classname`` pytest reports: ``tests.unit.Versioning`` becomes three levels
	of ``<Testsuite>``, so a reader sees the hierarchy the test suite actually has.
	"""

	_path:      Path                          #: Where the report is written.
	_results:   dict[str, _Result]            #: Collected results, keyed by node ID.
	_hierarchy: dict[str, dict[str, str]]     #: Names of every test suite level, keyed by its dotted path.

	def __init__(self, path: Path, hierarchy: Nullable[dict[str, dict[str, str]]] = None) -> None:
		"""
		Initializes the writer with the path it writes to.

		:param path:      Path of the report file to write.
		:param hierarchy: Optional, the names of every test suite level, keyed by its dotted path, as
		                  :mod:`pyTooling.Testing.PyTest` collects them. Without it - when the marker plugin is not
		                  registered - the test suite elements carry no names.
		"""
		self._path =      path
		self._results =   {}
		self._hierarchy = {} if hierarchy is None else hierarchy

	def pytest_runtest_logreport(self, report: Any) -> None:
		"""
		Collect one phase of one testcase.

		:param report: The report of one phase of one testcase.
		"""
		entry = self._results.setdefault(report.nodeid, {"nodeID": report.nodeid, "duration": 0.0, "message": ""})
		entry["duration"] += report.duration
		entry.update(dict(report.user_properties))

		if report.failed:
			entry["status"] = "errored" if report.when != "call" else "failed"
			entry["message"] = str(report.longrepr) if report.longrepr is not None else ""
		elif report.skipped:
			entry.setdefault("status", "skipped")
		elif report.when == "call":
			entry.setdefault("status", "passed")

	def _testsuiteFor(self, root: Element, suites: dict[str, Element], nodeID: str) -> Element:
		"""
		Return the ``<Testsuite>`` element a testcase belongs into, creating the missing levels on the way.

		:param root:    The report element every path starts at.
		:param suites:  Elements created so far, keyed by their dotted path.
		:param nodeID:  Node ID of the testcase, whose ``::``-separated parts name the levels.
		:returns:       The innermost test suite element.
		"""
		modulePath, _, remainder = nodeID.partition("::")
		levels = [*Path(modulePath).with_suffix("").parts, *remainder.split("::")[:-1]]

		parent = root
		path = ""
		for level in levels:
			path = f"{path}.{level}" if path != "" else level
			if (suite := suites.get(path)) is None:
				suite = suites[path] = SubElement(parent, "Testsuite", {"name": level})
				_addLevelNames(suite, self._hierarchy.get(path, {}))

			parent = suite

		return parent

	def pytest_sessionfinish(self, session: Session, exitstatus: int) -> None:
		"""
		Write the collected results as one XML document.

		:param session:    The finished session.
		:param exitstatus: The exit status the session ended with.
		"""
		statuses = [entry.get("status", "errored") for entry in self._results.values()]
		root = Element("TestReport", {
			"xmlns:xsi":                     "http://www.w3.org/2001/XMLSchema-instance",
			"xsi:noNamespaceSchemaLocation": SCHEMA_FILES[SCHEMA_VERSION_LATEST],
			"timestamp":                     datetime.now(timezone.utc).isoformat(),
			"duration":                      f"{sum(entry['duration'] for entry in self._results.values()):.6f}",
			"tests":                         str(len(statuses)),
			"failures":                      str(statuses.count("failed")),
			"errors":                        str(statuses.count("errored")),
			"skipped":                       str(statuses.count("skipped")),
		})

		suites: dict[str, Element] = {}
		for entry in self._results.values():
			testsuite = self._testsuiteFor(root, suites, entry["nodeID"])

			testcase = SubElement(testsuite, "Testcase", {
				"name":     entry["nodeID"].rsplit("::", 1)[-1],
				"status":   entry.get("status", "errored"),
				"duration": f"{entry['duration']:.6f}",
				"nodeID":   entry["nodeID"],
			})
			_addNames(testcase, entry)
			if entry["message"] != "":
				SubElement(testcase, "Message").text = entry["message"]

		tree = ElementTree(root)
		indent(tree, space="\t")
		self._path.parent.mkdir(parents=True, exist_ok=True)
		tree.write(self._path, encoding="utf-8", xml_declaration=True)


def _addNames(element: Element, entry: _Result) -> None:
	"""
	Add the ``Title``, ``Summary`` and ``Description`` elements a testcase carries, if it carries them.

	The elements are ordered as the schema requires, and one is written only when its value is not empty, so an
	unmarked testcase produces none of them.

	:param element: The ``Testcase`` element to add the names to.
	:param entry:   The collected result the names are read from.
	"""
	for name in ("Title", "Summary", "Description"):
		if (value := entry.get(name[0].lower() + name[1:], "")) != "":
			SubElement(element, name).text = value


def _addLevelNames(element: Element, names: dict[str, str]) -> None:
	"""
	Add the ``Title``, ``Summary`` and ``Description`` elements a test suite level carries.

	:param element: The ``Testsuite`` element to add the names to.
	:param names:   The level's names, keyed as :func:`pyTooling.Testing.PyTest.getNamesOfTestItem` returns them.
	"""
	for name in ("Title", "Summary", "Description"):
		if (value := names.get(name[0].lower() + name[1:], "")) != "":
			SubElement(element, name).text = value


@export
def pytest_addoption(parser: Parser) -> None:
	"""
	Add the ``--pytooling-xml`` option selecting the report's path.

	:param parser: The command line parser to add the option to.
	"""
	group = parser.getgroup("pyTooling")
	group.addoption(
		"--pytooling-xml", action="store", default=None, metavar="PATH",
		help="Write a pyTooling test report to PATH."
	)


@export
def pytest_configure(config: Config) -> None:
	"""
	Register the writer, if a path was given.

	:param config: The session's configuration.
	"""
	if (path := config.getoption("--pytooling-xml")) is not None:
		# 'setdefault' rather than 'get': this hook runs before collection, so the marker plugin has not filled the
		# stash yet. Creating the dictionary here hands both plugins the same object, which it then updates in place.
		writer = TestReportWriter(Path(path), config.stash.setdefault(hierarchyKey, {}))
		config.stash[REPORT_WRITER_KEY] = writer
		config.pluginmanager.register(writer, "pyTooling.Testing.TestReportWriter")
