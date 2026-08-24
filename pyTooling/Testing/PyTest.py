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
A pytest plugin collecting what :deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase` mark.

pytest decides what a test is from a *name*: ``python_classes`` matches ``Test*`` and ``python_functions`` matches
``test_*``. The identifier therefore has to enable collection as well as describe the check. This plugin adds a
second route in - a class or method carrying a marker is collected whatever it is called - and reports the title
its marker gives it as a JUnit property.

The plugin is inert until something is marked, so enabling it changes nothing for a name-based test suite. Both
styles can live in the same run, and even in the same file.

.. hint::

   See :ref:`high-level help <TESTING/Markers>` for explanations and usage examples.
"""
from typing   import Any, Optional as Nullable
from unittest import TestCase

from pytest               import Class, Collector, Item
from pyTooling.Decorators import export


@export
def getTestcases(cls: type) -> dict[str, Any]:
	"""
	Return the methods marked as testcases.

	:param cls: Class to search for marked methods.
	:returns:   Dictionary of a method's name to the method, for every method carrying ``__testcase_title__``.
	"""
	return {
		name: member
		for name, member in vars(cls).items()
		if callable(member) and hasattr(member, "__testcase_title__")
	}


@export
def pytest_pycollect_makeitem(collector: Collector, name: str, obj: Any) -> Nullable[Any]:
	"""
	Collect a marked class or a marked method, whatever it is named.

	A marked :class:`unittest.TestCase` is a special case: such a class is collected by pytest's :mod:`unittest`
	support, which asks :meth:`unittest.TestLoader.getTestCaseNames` for the test methods - and that loader matches
	:attr:`~unittest.TestLoader.testMethodPrefix`, which is ``"test"`` and is *not* the ``python_functions`` setting.
	Each marked method is therefore aliased under a name that loader accepts, and the class is handed back to pytest,
	which collects a :class:`~unittest.TestCase` subclass regardless of ``python_classes``. The alias reaches no
	report, because the entry is titled from the marker.

	:param collector: The module collector asking about the object.
	:param name:      Name the object is bound to in the module.
	:param obj:       The object to decide about.
	:returns:         A collector or a list of items for a marked entity, otherwise ``None`` to let pytest decide.
	"""
	if isinstance(obj, type) and hasattr(obj, "__testsuite_title__"):
		if issubclass(obj, TestCase):
			for methodName, method in getTestcases(obj).items():
				if not methodName.startswith("test"):
					setattr(obj, f"test_{methodName}", method)

			return None

		return Class.from_parent(collector, name=name)

	if callable(obj) and hasattr(obj, "__testcase_title__"):
		return list(collector._genfunctions(name, obj))

	return None


@export
def pytest_collection_modifyitems(items: list[Item]) -> None:
	"""
	Attach the names of every marked item to the item, for the report to pick up.

	A test item has four names, and only the first of them is what Python calls it:

	* the **ID** - the module, class or method name, which is the item's ``classname``/``name``,
	* the **title** - what the marker was given,
	* the **summary** - the first paragraph of the doc-string,
	* the **description** - the doc-string.

	They travel as :attr:`~_pytest.nodes.Item.user_properties`, which is the channel the
	:func:`~_pytest.python_api.record_property` fixture writes to: they are part of the test report, so they survive
	being sent from a ``pytest-xdist`` worker, and they reach the JUnit report as ``<property>`` elements.

	**The item's own name and node ID are deliberately left alone.** They are what selects a test - on the command
	line, from an IDE, and from ``--last-failed``'s cache - and post-processing tools expect them to be identifiers,
	free of spaces and punctuation. The title is additional information, not a replacement.

	:param items: The collected items, modified in place.
	"""
	for item in items:
		testcaseTitle = getattr(getattr(item, "function", None), "__testcase_title__", None)
		if testcaseTitle is None:
			continue

		function = item.function
		cls = getattr(item, "cls", None)

		# an item has four names: the ID (its 'classname'/'name'), a title, a summary and a description
		for propertyName, value in (
			("title",                 testcaseTitle),
			("summary",               getattr(function, "__testcase_summary__", "")),
			("description",           getattr(function, "__testcase_description__", "")),
			("testsuiteTitle",        getattr(cls, "__testsuite_title__", "")),
			("testsuiteSummary",      getattr(cls, "__testsuite_summary__", "")),
			("testsuiteDescription",  getattr(cls, "__testsuite_description__", "")),
		):
			if value != "":
				item.user_properties.append((propertyName, value))
