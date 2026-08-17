# ==================================================================================================================== #
#             _____           _ _             _____                   _             _ _   _ ___                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__ _ __ _ __ ___ (_)_ __   __ _| | | | |_ _|                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | | | | || |                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/ |  | | | | | | | | | | (_| | | |_| || |                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|\___/|___|                       #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
"""Unit tests for how a terminal application reports its issue tracker URL."""
from io       import StringIO
from types    import ModuleType
from unittest import TestCase

from pyTooling.TerminalUI import TerminalApplication


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class IssueTrackerURL(TestCase):
	"""ISSUE_TRACKER_URL is the well-known member; an application assigns it from its own dunder variable."""

	_DUNDER_URL = "https://GitHub.com/example/project/issues"

	@staticmethod
	def _dunderModule(issueTrackerURL=None) -> ModuleType:
		module = ModuleType("exampleApplication")
		module.__version__ = "1.0.0"
		if issueTrackerURL is not None:
			module.__issue_tracker_url__ = issueTrackerURL

		return module

	def _printVersion(self, application: TerminalApplication, dunderModule: ModuleType) -> str:
		"""
		Print the version information of an application and return what it wrote.

		:param application:  The application printing its version information.
		:param dunderModule: The module carrying the application's dunder variables.
		:returns:            Everything the application wrote to its standard output.
		"""
		application._stdout = StringIO()
		application._PrintVersion(dunderModule)

		return application._stdout.getvalue()

	def test_TheClassVariableIsPrinted(self) -> None:
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = self._DUNDER_URL

		output = self._printVersion(Application(), self._dunderModule())

		self.assertIn(self._DUNDER_URL, output)

	def test_TheClassVariableWinsOverTheDunderVariable(self) -> None:
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = "https://GitHub.com/example/project/issues"

		output = self._printVersion(Application(), self._dunderModule("https://other/issues"))

		self.assertIn("https://GitHub.com/example/project/issues", output)
		self.assertNotIn("https://other/issues", output)

	def test_TheDunderVariableIsStillRead(self) -> None:
		"""An application that only declares the dunder variable keeps its issue tracker line."""
		class Application(TerminalApplication):
			pass

		output = self._printVersion(Application(), self._dunderModule(self._DUNDER_URL))

		self.assertIn(self._DUNDER_URL, output)

	def test_NeitherIsDeclared(self) -> None:
		class Application(TerminalApplication):
			pass

		output = self._printVersion(Application(), self._dunderModule())

		self.assertNotIn("Issue tracker:", output)
