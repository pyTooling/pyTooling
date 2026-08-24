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
``test_*``. The identifier therefore has to enable collection as well as describe the check, and ``test_`` reaches
the JUnit report. This plugin adds a second route in - a class or method carrying a marker is collected whatever it
is called, and it is reported under the name the marker gives it.

The plugin is inert until something is marked, so enabling it changes nothing for a name-based test suite. Both
styles can live in the same run, and even in the same file.

.. hint::

   See :ref:`high-level help <TESTING/Markers>` for explanations and usage examples.
"""
from typing   import Any, Optional as Nullable
from unittest import TestCase

import pytest


__all__ = ["pytest_pycollect_makeitem", "pytest_collection_modifyitems"]


def _markedMethods(cls: type) -> dict[str, Any]:
	"""
	Return the marked methods a class declares itself.

	:param cls: Class to search for marked methods.
	:returns:   Dictionary of a method's name to the method, for every method carrying ``__testcase__``.
	"""
	return {name: member for name, member in vars(cls).items() if callable(member) and hasattr(member, "__testcase__")}


def pytest_pycollect_makeitem(collector, name: str, obj: Any) -> Nullable[Any]:
	"""
	Collect a marked class or a marked method, whatever it is named.

	A marked :class:`unittest.TestCase` is a special case: such a class is collected by pytest's :mod:`unittest`
	support, which asks :mod:`unittest`'s own loader for the test methods, and that loader finds them by the
	``test`` prefix alone. Each marked method is therefore aliased under a name the loader accepts, and the class is
	handed back to pytest - which collects a :class:`~unittest.TestCase` subclass regardless of ``python_classes``.
	The alias never reaches the report, because the item is renamed afterwards.

	:param collector: The module collector asking about the object.
	:param name:      Name the object is bound to in the module.
	:param obj:       The object to decide about.
	:returns:         A collector or a list of items for a marked entity, otherwise ``None`` to let pytest decide.
	"""
	if isinstance(obj, type) and hasattr(obj, "__testsuite__"):
		if issubclass(obj, TestCase):
			for methodName, method in _markedMethods(obj).items():
				if not methodName.startswith("test"):
					setattr(obj, f"test_{methodName}", method)

			return None

		return pytest.Class.from_parent(collector, name=name)

	if callable(obj) and hasattr(obj, "__testcase__"):
		return list(collector._genfunctions(name, obj))

	return None


def pytest_collection_modifyitems(items: list) -> None:
	"""
	Report every marked item under the name its marker gives it.

	The name a testcase is reported under - in the terminal, in the JUnit report and in a failure - comes from the
	item, so renaming it here is what makes the marker's name visible. An unmarked item is left alone.

	:param items: The collected items, modified in place.
	"""
	for item in items:
		function = getattr(item, "function", None)
		declaredCase = getattr(function, "__testcase__", None)
		if declaredCase is None:
			continue

		declaredSuite = getattr(getattr(item, "cls", None), "__testsuite__", None)
		if declaredSuite is None:
			continue

		modulePath = item.nodeid.rsplit("::", 2)[0]
		item._nodeid = f"{modulePath}::{declaredSuite}::{declaredCase}"
		item.name = declaredCase
