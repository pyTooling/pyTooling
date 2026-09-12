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
Unit tests for :mod:`pyTooling.Testing.PyTest`, exercised in-process.

The plugin's hooks read a handful of fields from the objects pytest hands them, so a testcase can hand them
stand-ins and look at what comes back - which is what a subprocess run cannot show, because coverage does not
follow a subprocess.
"""
from sys      import modules as loadedModules
from types    import ModuleType

from pyTooling.Testing import Testcase, testsuite, testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Names(Testcase):
	"""The names an item carries as a test suite level: a marked class has three, a module has its doc-string."""

	def test_AMarkedClassCarriesAllThree(self) -> None:
		from pyTooling.Testing.PyTest import getNamesOfTestItem

		@testsuite("Version comparison.")
		class Suite:
			"""
			Compare two release versions.

			Everything about comparing them.
			"""

		self.assertEqual(
			{
				"title":       "Version comparison.",
				"summary":     "Compare two release versions.",
				"description": "Compare two release versions.\n\nEverything about comparing them."
			},
			getNamesOfTestItem(Suite)
		)

	def test_AModuleHasOnlyItsDocString(self) -> None:
		"""A module cannot be marked, so its doc-string is both its summary and its description."""

		from pyTooling.Testing.PyTest import getNamesOfTestItem

		module = ModuleType("probe")
		module.__doc__ = "The version handling test suite.\n\nEverything about parsing versions."

		self.assertEqual(
			{
				"summary":     "The version handling test suite.",
				"description": "The version handling test suite.\n\nEverything about parsing versions."
			},
			getNamesOfTestItem(module)
		)

	def test_AnEmptyNameIsNotReported(self) -> None:
		"""A level contributes only the names it has, so an undocumented one contributes nothing."""

		from pyTooling.Testing.PyTest import getNamesOfTestItem

		module = ModuleType("probe")

		self.assertEqual({}, getNamesOfTestItem(module))

	def test_AMarkedClassWithoutADocString(self) -> None:
		from pyTooling.Testing.PyTest import getNamesOfTestItem

		@testsuite("A title.")
		class Suite:
			pass

		self.assertEqual({"title": "A title."}, getNamesOfTestItem(Suite))


class Levels(Testcase):
	"""Every level of a testcase's node ID, keyed by the dotted path pytest reports as its 'classname'."""

	class _Item:
		"""A stand-in for a collected item, carrying only the node ID the levels are read from."""

		def __init__(self, nodeID: str) -> None:
			self.nodeid = nodeID

	def setUp(self) -> None:
		"""Register a two-level package whose modules carry doc-strings, so the levels have names to report."""

		self._modules = {}
		for name, docString in (
			("probePackage",           "The probe package."),
			("probePackage.versions",  "The version tests.\n\nEverything about them."),
		):
			module = ModuleType(name)
			module.__doc__ = docString
			self._modules[name] = loadedModules[name] = module

	def tearDown(self) -> None:
		"""Remove the registered modules again, so no other testcase sees them."""

		for name in self._modules:
			loadedModules.pop(name, None)

	def test_EveryLevelIsKeyedByItsDottedPath(self) -> None:
		from pyTooling.Testing.PyTest import getLevelNames

		levels = getLevelNames(self._Item("probePackage/versions.py::Comparison::test_Newer"))

		self.assertEqual(
			{
				"probePackage":          {"summary": "The probe package.", "description": "The probe package."},
				"probePackage.versions": {
					"summary":     "The version tests.",
					"description": "The version tests.\n\nEverything about them."
				}
			},
			levels
		)

	def test_TheKeysArePrefixesOfTheClassname(self) -> None:
		"""That is what lets a reader join a level's names to the testcase's 'classname'."""

		from pyTooling.Testing.PyTest import getLevelNames

		classname = "probePackage.versions.Comparison"
		for path in getLevelNames(self._Item("probePackage/versions.py::Comparison::test_Newer")):
			with self.subTest(level=path):
				self.assertTrue(classname.startswith(path), f"'{path}' is not a prefix of '{classname}'.")

	def test_AnUnknownLevelIsSkipped(self) -> None:
		"""A path that names no loaded module contributes nothing rather than raising."""

		from pyTooling.Testing.PyTest import getLevelNames

		self.assertEqual({}, getLevelNames(self._Item("nothing/here.py::Suite::test_It")))


class Collection(Testcase):
	"""What the collection hooks make of a marked entity."""

	def test_AnUnmarkedObjectIsLeftToPytest(self) -> None:
		"""Returning 'None' is what keeps a test suite collecting by name beside a marked one."""

		from pyTooling.Testing.PyTest import pytest_pycollect_makeitem

		class Plain:
			pass

		self.assertIsNone(pytest_pycollect_makeitem(None, "Plain", Plain))
		self.assertIsNone(pytest_pycollect_makeitem(None, "value", 42))

	def test_AMarkedTestcaseClassIsAliasedForTheLoader(self) -> None:
		""":class:`unittest.TestCase` collects by 'testMethodPrefix', so a marked method needs a name it accepts."""

		from pyTooling.Testing.PyTest import pytest_pycollect_makeitem

		@testsuite("A suite.")
		class Suite(Testcase):
			@testcase("A case.")
			def NotNamedLikeATest(self) -> None:
				pass

		self.assertIsNone(pytest_pycollect_makeitem(None, "Suite", Suite), "The class is handed back to pytest.")
		self.assertTrue(hasattr(Suite, "test_NotNamedLikeATest"), "The loader needs a name starting with 'test'.")

	def test_TheMarkedMethodsAreFound(self) -> None:
		from pyTooling.Testing.PyTest import getTestcases

		@testsuite("A suite.")
		class Suite:
			@testcase("A case.")
			def Marked(self) -> None:
				pass

			def Unmarked(self) -> None:
				pass

		self.assertEqual(["Marked"], list(getTestcases(Suite)))


class SessionProperties(Testcase):
	"""The fixture writing the level names into the session's properties."""

	def test_EveryNameIsWrittenUnderItsDottedKey(self) -> None:
		from pyTooling.Testing.PyTest import hierarchyKey, _recordTestsuiteHierarchy

		recorded = []

		class Stash(dict):
			def get(self, key, default=None):
				return {"versions": {"summary": "The version tests."}} if key is hierarchyKey else default

		class Configuration:
			stash = Stash()

		class Request:
			config = Configuration()

		_recordTestsuiteHierarchy.__wrapped__(Request(), lambda name, value: recorded.append((name, value)))

		self.assertEqual([("versions.summary", "The version tests.")], recorded)


class CollectedItems(Testcase):
	"""What ``pytest_collection_modifyitems`` attaches to an item, and what it deliberately does not."""

	class _Item:
		"""A stand-in for a collected item, carrying the four fields the hook reads."""

		def __init__(self, nodeID: str, function=None, stash=None) -> None:
			self.nodeid = nodeID
			self.function = function
			self.user_properties = []
			self.config = type("Configuration", (), {"stash": stash if stash is not None else {}})()

	def test_TheThreeNamesTravelAsUserProperties(self) -> None:
		from pyTooling.Testing.PyTest import pytest_collection_modifyitems

		@testcase("A newer version compares greater.")
		def NewerIsGreater() -> None:
			"""
			A newer version compares greater than an older one.

			Only the minor number differs here.
			"""

		item = self._Item("probe.py::Comparison::test_NewerIsGreater", NewerIsGreater)
		pytest_collection_modifyitems([item])

		self.assertEqual(
			[
				("title",       "A newer version compares greater."),
				("summary",     "A newer version compares greater than an older one."),
				("description", "A newer version compares greater than an older one.\n\nOnly the minor number differs here.")
			],
			item.user_properties
		)

	def test_TheTestsuiteNamesAreNotRepeatedOnTheTestcase(self) -> None:
		"""They belong to the level, which is written once - not once per testcase."""

		from pyTooling.Testing.PyTest import pytest_collection_modifyitems

		@testcase("A case.")
		def Marked() -> None:
			pass

		item = self._Item("probe.py::Comparison::test_Marked", Marked)
		pytest_collection_modifyitems([item])

		self.assertNotIn("testsuiteTitle", [name for name, _ in item.user_properties])

	def test_AnUnmarkedItemIsLeftAlone(self) -> None:
		from pyTooling.Testing.PyTest import pytest_collection_modifyitems

		def plain() -> None:
			pass

		item = self._Item("probe.py::NameBased::test_plain", plain)
		pytest_collection_modifyitems([item])

		self.assertEqual([], item.user_properties)

	def test_TheNodeIDIsNeverTouched(self) -> None:
		"""It selects the testcase - on the command line, from an IDE and from '--last-failed'."""

		from pyTooling.Testing.PyTest import pytest_collection_modifyitems

		@testcase("A title with spaces and punctuation.")
		def Marked() -> None:
			pass

		nodeID = "probe.py::Comparison::test_Marked"
		item = self._Item(nodeID, Marked)
		pytest_collection_modifyitems([item])

		self.assertEqual(nodeID, item.nodeid)

	def test_TheHierarchyIsStashedOnTheConfiguration(self) -> None:
		"""That is where the report writer reads a level's names from."""

		from pyTooling.Testing.PyTest import hierarchyKey, pytest_collection_modifyitems

		module = ModuleType("probeModule")
		module.__doc__ = "A probed module."
		loadedModules["probeModule"] = module

		try:
			stash = {}
			pytest_collection_modifyitems([self._Item("probeModule.py::Suite::test_It", None, stash)])
		finally:
			loadedModules.pop("probeModule", None)

		self.assertEqual(
			{"probeModule": {"summary": "A probed module.", "description": "A probed module."}},
			stash[hierarchyKey]
		)

	def test_AnEmptySessionStashesNothing(self) -> None:
		from pyTooling.Testing.PyTest import pytest_collection_modifyitems

		pytest_collection_modifyitems([])


class PlainCollection(Testcase):
	"""A marked entity that is not a :class:`unittest.TestCase` is collected through pytest's own collectors."""

	def test_AMarkedPlainClassBecomesACollector(self) -> None:
		"""It is not a 'TestCase', so 'python_classes' would never have collected it - the marker does."""

		from pyTooling.Testing import PyTest

		@testsuite("A plain suite.")
		class Suite:
			pass

		created = []

		class ClassCollector:
			@staticmethod
			def from_parent(parent, name):
				created.append((parent, name))
				return "collector"

		# 'Class.from_parent' builds a real pytest collector, which needs a real session behind it.
		realClass, PyTest.Class = PyTest.Class, ClassCollector
		try:
			result = PyTest.pytest_pycollect_makeitem("theModuleCollector", "Suite", Suite)
		finally:
			PyTest.Class = realClass

		self.assertEqual("collector", result)
		self.assertEqual([("theModuleCollector", "Suite")], created)

	def test_AMarkedFunctionBecomesItems(self) -> None:
		from pyTooling.Testing.PyTest import pytest_pycollect_makeitem

		@testcase("A case.")
		def Marked() -> None:
			pass

		class Collector:
			@staticmethod
			def _genfunctions(name, obj):
				yield f"item:{name}"

		self.assertEqual(["item:Marked"], pytest_pycollect_makeitem(Collector(), "Marked", Marked))
