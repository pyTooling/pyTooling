# ==================================================================================================================== #
#              _____           _ _               ____  _                           _       _                           #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ ___  _ ____      ____ _| |_ ___| |__                        #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __/ _ \| '_ \ \ /\ / / _` | __/ __| '_ \                       #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | || (_) | |_) \ V  V / (_| | || (__| | | |                      #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__\___/| .__/ \_/\_/ \__,_|\__\___|_| |_|                      #
#  |_|    |___/                          |___/                 |_|                                                     #
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
"""
Helpers for testing an application: run its entry point in a subprocess and assert on the result.

Unit tests import the code they test; an application test has to start the installed program the way a user does,
because that is the only way to cover the console-script wiring, argument parsing and exit codes. This module
provides the piece every such test suite otherwise rewrites: resolving the executable, running it with a timeout
and captured output, and failing with the output attached.

.. hint::

   See :ref:`high-level help <TESTING>` for explanations and usage examples.
"""
from pathlib    import Path
from re         import compile as re_compile
from shutil     import which
from subprocess import CompletedProcess, run as subprocess_run
from sys        import executable as PythonExecutable
from typing     import ClassVar, Dict, Optional as Nullable

from pyTooling.Decorators import export


__all__ = ["stripANSIColorCodes"]

_ANSI_COLOR_CODES = re_compile(r"\x1B\[[0-9;]*m")


def stripANSIColorCodes(text: str) -> str:
	"""
	Remove ANSI color codes from a text, so it can be compared to an expected output.

	A program writing to a terminal colors its output; the same program in a pipe usually does not, but that depends
	on the program. Comparing against an expectation is more robust with the codes removed than with a rule about
	when they appear.

	:param text: The text to remove the color codes from.
	:returns:    The text without ANSI color codes.
	"""
	return _ANSI_COLOR_CODES.sub("", text)


@export
class ApplicationTestcaseMixin:
	"""
	A mixin for :class:`unittest.TestCase` classes testing an application through its command line.

	It resolves the installed console script once per test class, offers two ways to run the program - through the
	installed entry point and through ``python -m <module>`` - and an assertion that reports the exit code together
	with what the program printed.

	Derive from this mixin *and* :class:`~unittest.TestCase`, and name what is being tested:

	.. code-block:: python

	   class Commands(ApplicationTestcaseMixin, TestCase):
	     _consoleScript =  "myprogram"
	     _runnableModule = "myPackage.CLI"

	     def test_Version(self) -> None:
	       result = self.RunEntrypoint("--version")

	       self.assertExitCode(result, 0)
	       self.assertIn("myprogram", result.stdout)

	.. note::

	   This is a classic mixin - no :class:`~pyTooling.MetaClasses.ExtendedType`. :class:`unittest.TestCase` is not
	   created by that meta-class and has no ``__slots__``, so a mixin created by it cannot be combined with it.
	"""

	_consoleScript:  ClassVar[Nullable[str]] = None   #: Name of the installed console script, resolved on ``PATH``.
	_runnableModule: ClassVar[Nullable[str]] = None   #: Dotted name of the module to run with ``python -m``.
	_executable:     ClassVar[Nullable[str]] = None   #: The resolved console script, set by :meth:`setUpClass`.

	@classmethod
	def setUpClass(cls) -> None:
		"""
		Resolve the console script on ``PATH``, once per test class.

		:raises FileNotFoundError: If a console script was named but is not installed, because every test in the class
		                           would otherwise fail with the same unhelpful error.
		"""
		super().setUpClass()

		if cls._consoleScript is None:
			return

		if (resolved := which(cls._consoleScript)) is None:
			raise FileNotFoundError(
				f"Console script '{cls._consoleScript}' was not found on PATH. Is the package installed in this "
				f"environment, and does its entry point name match?"
			)

		cls._executable = resolved

	def RunEntrypoint(
		self,
		*arguments:       str,
		timeout:          float = 10.0,
		stdInput:         Nullable[str] = None,
		environment:      Nullable[Dict[str, str]] = None,
		workingDirectory: Nullable[Path] = None
	) -> CompletedProcess:
		"""
		Run the installed console script.

		This is the path a user takes, so it covers the entry-point wiring as well as the program itself.

		:param arguments:            Command line arguments to pass to the program.
		:param timeout:              Seconds to wait before the program is killed and :exc:`subprocess.TimeoutExpired`
		                             is raised. A test should fail rather than hang.
		:param stdInput:             Text to send to the program's standard input.
		:param environment:          The environment to run in, or ``None`` to inherit this process's environment.
		:param workingDirectory:     Directory to run in, or ``None`` for the current one.
		:returns:                    The completed process, with ``stdout`` and ``stderr`` captured as text.
		:raises NotImplementedError: If the class did not name a console script.
		"""
		if self._executable is None:
			raise NotImplementedError(
				f"'{self.__class__.__name__}' has no console script. Set '_consoleScript' to run the installed "
				f"program, or use 'RunModule' to run the module directly."
			)

		return self._run([self._executable, *arguments], timeout, stdInput, environment, workingDirectory)

	def RunModule(
		self,
		*arguments:       str,
		timeout:          float = 10.0,
		stdInput:         Nullable[str] = None,
		environment:      Nullable[Dict[str, str]] = None,
		workingDirectory: Nullable[Path] = None
	) -> CompletedProcess:
		"""
		Run the program as ``python -m <module>``, bypassing the console script.

		Use it to tell a broken entry point apart from a broken program: if this passes while
		:meth:`RunEntrypoint` fails, the packaging is at fault, not the code.

		:param arguments:            Command line arguments to pass to the program.
		:param timeout:              Seconds to wait before the program is killed.
		:param stdInput:             Text to send to the program's standard input.
		:param environment:          The environment to run in, or ``None`` to inherit this process's environment.
		:param workingDirectory:     Directory to run in, or ``None`` for the current one.
		:returns:                    The completed process, with ``stdout`` and ``stderr`` captured as text.
		:raises NotImplementedError: If the class did not name a runnable module.
		"""
		if self._runnableModule is None:
			raise NotImplementedError(
				f"'{self.__class__.__name__}' has no runnable module. Set '_runnableModule' to run the program with "
				f"'python -m'."
			)

		return self._run(
			[PythonExecutable, "-m", self._runnableModule, *arguments], timeout, stdInput, environment, workingDirectory
		)

	@staticmethod
	def _run(
		commandLine:      list,
		timeout:          float,
		stdInput:         Nullable[str],
		environment:      Nullable[Dict[str, str]],
		workingDirectory: Nullable[Path]
	) -> CompletedProcess:
		"""
		Run a command line with captured text output.

		:param commandLine:      The program and its arguments.
		:param timeout:          Seconds to wait before the program is killed.
		:param stdInput:         Text to send to the program's standard input.
		:param environment:      The environment to run in, or ``None`` to inherit this process's environment.
		:param workingDirectory: Directory to run in, or ``None`` for the current one.
		:returns:                The completed process.
		"""
		return subprocess_run(
			commandLine,
			capture_output=True,
			text=True,
			timeout=timeout,
			input=stdInput,
			env=environment,
			cwd=None if workingDirectory is None else str(workingDirectory)
		)

	def assertExitCode(self, result: CompletedProcess, expected: int = 0) -> None:
		"""
		Check the exit code of a completed process, reporting what the program printed when it doesn't match.

		The output is what explains the failure, and it is gone once the test has finished, so it goes into the
		assertion message rather than into the console.

		:param result:   The completed process to check.
		:param expected: The expected exit code, zero by default.
		"""
		self.assertEqual(
			expected,
			result.returncode,
			msg=(
				f"Expected exit code {expected}, got {result.returncode} from: {result.args!r}\n"
				f"--- stdout ---\n{result.stdout}\n"
				f"--- stderr ---\n{result.stderr}"
			)
		)
