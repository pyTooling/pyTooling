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
Enhanced classes for writing unit tests with Python's :mod:`unittest` framework, which pytest runs as well.

The pieces here are the ones every test suite otherwise rewrites. Currently that is application testing: starting
the program under test the way a user does, because importing it cannot cover the console-script wiring, the
argument parsing or the exit codes.

.. hint::

   See :ref:`high-level help <TESTING>` for explanations and usage examples.
"""
from pathlib    import Path
from re         import compile as re_compile
from shutil     import which
from subprocess import CompletedProcess, run as subprocess_run
from unittest   import TestCase
from sys        import executable as PythonExecutable, version_info
from typing     import Any, ClassVar, Dict, Optional as Nullable

from pyTooling.Decorators import export
from pyTooling.Exceptions import ToolingException


_ANSI_COLOR_CODES = re_compile(r"\x1B\[[0-9;]*m")   #: Pattern matching an ANSI escape sequence selecting a color.


@export
class TestingException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Testing`."""


@export
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
class Testcase(TestCase):
	"""
	The base class for pyTooling's testcases, deriving from :class:`unittest.TestCase`.

	It adds the assertions Python's :mod:`unittest` gained later than the oldest Python version pyTooling supports,
	so a test suite can use them whichever interpreter runs it:

	.. code-block:: python

	   class Slots(Testcase):
	     def test_SlotsAreDerived(self) -> None:
	       self.assertHasAttr(MyClass, "__slots__")

	On Python 3.14 and newer, :class:`unittest.TestCase` implements them and this class defines nothing, so the
	standard library's implementations and messages are used.
	"""

	if version_info < (3, 14):  # pragma: no cover
		def assertHasAttr(self, obj: Any, name: str, msg: Nullable[str] = None) -> None:
			"""
			Assert an object has an attribute of the given name.

			Available in :class:`unittest.TestCase` from Python 3.14 on.

			:param obj:  The object to check.
			:param name: Name of the attribute the object is expected to have.
			:param msg:  An optional message replacing the generated one.
			"""
			if not hasattr(obj, name):
				self.fail(msg or f"{type(obj).__name__!r} object has no attribute {name!r}")

		def assertNotHasAttr(self, obj: Any, name: str, msg: Nullable[str] = None) -> None:
			"""
			Assert an object has no attribute of the given name.

			Available in :class:`unittest.TestCase` from Python 3.14 on.

			:param obj:  The object to check.
			:param name: Name of the attribute the object is expected not to have.
			:param msg:  An optional message replacing the generated one.
			"""
			if hasattr(obj, name):
				self.fail(msg or f"{type(obj).__name__!r} object has unexpected attribute {name!r}")


@export
class ApplicationTestcase(Testcase):
	"""
	The base class for testcases exercising an application through its command line.

	It resolves the installed console script once per test class, offers two ways to run the program - through the
	installed entry point and through ``python -m <module>`` - and an assertion that reports the exit code together
	with what the program printed.

	Derive from it and name what is being tested:

	.. code-block:: python

	   class Commands(ApplicationTestcase):
	     _consoleScript =  "myprogram"
	     _runnableModule = "myPackage.CLI"

	     def test_Version(self) -> None:
	       result = self.RunEntrypoint("--version")

	       self.assertExitCode(result, 0)
	       self.assertIn("myprogram", result.stdout)
	"""

	_consoleScript:  ClassVar[Nullable[str]] = None   #: Name of the installed console script, resolved on ``PATH``.
	_runnableModule: ClassVar[Nullable[str]] = None   #: Dotted name of the module to run with ``python -m``.
	_executable:     ClassVar[Nullable[str]] = None   #: The resolved console script, set by :meth:`setUpClass`.

	@classmethod
	def setUpClass(cls) -> None:
		"""
		Check the test class is set up, and resolve the console script on ``PATH``, once per class.

		:raises TestingException: If the test class named neither a console script nor a runnable module, or if the
		                          console script it named is not installed. Every testcase in the class would
		                          otherwise fail, each with a less obvious error.
		"""
		super().setUpClass()

		if cls._consoleScript is None:
			raise TestingException(f"Testcase '{cls.__name__}' has no console script. Set '_consoleScript'.")

		if cls._runnableModule is None:
			raise TestingException(f"Testcase '{cls.__name__}' has no runnable module. Set '_runnableModule'.")

		if (resolved := which(cls._consoleScript)) is None:
			ex = TestingException(f"Console script '{cls._consoleScript}' was not found in PATH.")
			raise ex from FileNotFoundError(str(cls._consoleScript))

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

		:param arguments:        Command line arguments to pass to the program.
		:param timeout:          Seconds to wait before the program is killed and :exc:`subprocess.TimeoutExpired` is
		                         raised. A test should fail rather than hang.
		:param stdInput:         Text to send to the program's standard input.
		:param environment:      The environment to run in, or ``None`` to inherit this process's environment.
		:param workingDirectory: Directory to run in, or ``None`` for the current one.
		:returns:                The completed process, with ``stdout`` and ``stderr`` captured as text.
		"""
		return subprocess_run(
			[self._executable, *arguments],
			capture_output=True,
			text=True,
			timeout=timeout,
			input=stdInput,
			env=environment,
			cwd=None if workingDirectory is None else str(workingDirectory)
		)

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

		:param arguments:        Command line arguments to pass to the program.
		:param timeout:          Seconds to wait before the program is killed.
		:param stdInput:         Text to send to the program's standard input.
		:param environment:      The environment to run in, or ``None`` to inherit this process's environment.
		:param workingDirectory: Directory to run in, or ``None`` for the current one.
		:returns:                The completed process, with ``stdout`` and ``stderr`` captured as text.
		"""
		return subprocess_run(
			[PythonExecutable, "-m", self._runnableModule, *arguments],
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
