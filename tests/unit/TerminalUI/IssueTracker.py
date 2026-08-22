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
"""Unit tests for how a terminal application reports its issue tracker URL."""
from io                   import StringIO

from pyTooling.Exceptions import ExceptionBase
from pyTooling.TerminalUI import TerminalApplication
from pyTooling.Exceptions import MissingDependencyError
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class IssueTrackerURL(Testcase):
	"""``ISSUE_TRACKER_URL`` is where an application connects its own dunder variable, so the exception printers can
	invite the user to report a bug."""

	_URL = "https://GitHub.com/example/project/issues"

	def _printException(self, application: TerminalApplication, method: str, ex: Exception) -> str:
		"""
		Let an application print an exception and return what it wrote to ``STDERR``.

		:param application: The application printing the exception.
		:param method:      Name of the printing method to call.
		:param ex:          The exception to print, raised beforehand so it carries a traceback.
		:returns:           Everything the application wrote to ``STDERR``.
		"""
		application._stderr = StringIO()
		with self.assertRaises(SystemExit):
			getattr(application, method)(ex)

		return application._stderr.getvalue()

	@staticmethod
	def _raised(ex: Exception) -> Exception:
		"""
		Raise and catch an exception, so it carries the traceback every printer walks.

		:param ex: The exception to raise.
		:returns:  The same exception, with a traceback.
		"""
		try:
			raise ex
		except Exception as caught:
			return caught

	def test_PrintException(self) -> None:
		"""An unhandled exception ends with the invitation to report it."""
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = self._URL

		output = self._printException(Application(), "PrintException", self._raised(ValueError("Something failed.")))

		self.assertIn("Something failed.", output)
		self.assertIn(self._URL, output)

	def test_PrintExceptionBase(self) -> None:
		"""A known exception ends with the invitation, too."""
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = self._URL

		output = self._printException(Application(), "PrintExceptionBase", self._raised(ExceptionBase("Known.")))

		self.assertIn(self._URL, output)

	def test_PrintNotImplementedError(self) -> None:
		"""An unimplemented method ends with the invitation, too."""
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = self._URL

		output = self._printException(
			Application(), "PrintNotImplementedError", self._raised(NotImplementedError("Not yet."))
		)

		self.assertIn(self._URL, output)

	def test_PrintException_NoIssueTrackerURL(self) -> None:
		"""The class variable is ``None`` by default, and then the invitation is omitted rather than printed empty."""
		class Application(TerminalApplication):
			pass

		output = self._printException(Application(), "PrintException", self._raised(ValueError("Something failed.")))

		self.assertIn("Something failed.", output)
		self.assertNotIn("Please report this bug", output)


class MissingDependency(Testcase):
	"""A missing optional dependency is a user's installation problem, not a bug - so it is reported without a
	traceback and without an invitation to open an issue."""

	def _print(self, ex: MissingDependencyError) -> str:
		"""
		Let an application print the exception and return what it wrote to ``STDERR``.

		:param ex: The exception to print.
		:returns:  Everything the application wrote to ``STDERR``.
		"""
		class Application(TerminalApplication):
			ISSUE_TRACKER_URL = "https://GitHub.com/example/project/issues"

		application = Application()
		application._stderr = StringIO()
		with self.assertRaises(SystemExit) as context:
			application.PrintMissingDependencyException(ex)

		self.assertEqual(TerminalApplication.MISSING_DEPENDENCY_EXIT_CODE, context.exception.code)
		return application._stderr.getvalue()

	def test_BothInstallCommandsArePrinted(self) -> None:
		output = self._print(MissingDependencyError(dependency="ruamel.yaml", extra="yaml"))

		self.assertIn("ruamel.yaml", output)
		self.assertIn("pip install pyTooling[yaml]", output)
		self.assertIn("pip install ruamel.yaml", output)

	def test_WithoutAnExtraOnlyTheDirectCommand(self) -> None:
		output = self._print(MissingDependencyError(dependency="lxml"))

		self.assertIn("pip install lxml", output)
		self.assertNotIn("pyTooling[", output)

	def test_NoTracebackAndNoIssueTracker(self) -> None:
		"""The application configures an issue tracker, and this printer still must not invite a bug report."""
		try:
			raise MissingDependencyError(dependency="colorama", extra="terminal")
		except MissingDependencyError as ex:
			output = self._print(ex)

		self.assertNotIn("issues", output)
		self.assertNotIn("Traceback", output)

	def test_TheCauseIsReported(self) -> None:
		try:
			try:
				raise ImportError("No module named 'colorama'")
			except ImportError as ex:
				raise MissingDependencyError(dependency="colorama", extra="terminal") from ex
		except MissingDependencyError as ex:
			output = self._print(ex)

		self.assertIn("No module named 'colorama'", output)
