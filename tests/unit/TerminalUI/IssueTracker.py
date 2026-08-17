# ==================================================================================================================== #
#             _____           _ _             _____                                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ ___  ___                                                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _ \/ _ \                                                      #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | |  __/  __/                                                      #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \___|\___|                                                      #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for pyTooling.Tree."""
"""Unit tests for how a terminal application finds its issue tracker URL."""
from sys      import modules
from types    import ModuleType
from unittest import TestCase

from pyTooling.TerminalUI import TerminalBaseApplication


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class IssueTrackerURL(TestCase):
	"""The URL comes from '__issue_tracker_url__', with the class variable as the older fallback."""

	_DUNDER_URL = "https://GitHub.com/example/project/issues"

	@classmethod
	def setUpClass(cls) -> None:
		# a package with the dunder variable, and a sub-module without it
		package = ModuleType("exampleApplication")
		package.__issue_tracker_url__ = cls._DUNDER_URL
		modules["exampleApplication"] = package
		modules["exampleApplication.CLI"] = ModuleType("exampleApplication.CLI")

	@classmethod
	def tearDownClass(cls) -> None:
		for name in ("exampleApplication.CLI", "exampleApplication"):
			del modules[name]

	def test_TheDunderVariableIsUsed(self) -> None:
		class Application(TerminalBaseApplication):
			__module__ = "exampleApplication"

		self.assertEqual(self._DUNDER_URL, Application().IssueTrackerURL)

	def test_ItIsFoundInAParentPackage(self) -> None:
		"""The class lives in a sub-module; the dunder variables live in the package."""
		class Application(TerminalBaseApplication):
			__module__ = "exampleApplication.CLI"

		self.assertEqual(self._DUNDER_URL, Application().IssueTrackerURL)

	def test_TheDunderVariableWins(self) -> None:
		class Application(TerminalBaseApplication):
			__module__ = "exampleApplication"
			ISSUE_TRACKER_URL = "https://legacy/issues"

		self.assertEqual(self._DUNDER_URL, Application().IssueTrackerURL)

	def test_TheClassVariableIsTheFallback(self) -> None:
		class Application(TerminalBaseApplication):
			ISSUE_TRACKER_URL = "https://legacy/issues"

		self.assertEqual("https://legacy/issues", Application().IssueTrackerURL)

	def test_NeitherIsDeclared(self) -> None:
		self.assertIsNone(TerminalBaseApplication().IssueTrackerURL)
