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
"""
A set of helpers to implement a text user interface (TUI) in a terminal.

.. seealso::

   :mod:`pyTooling.Attributes.ArgParse`
      |rarr| Declaring the commands and options the application accepts.
   :mod:`pyTooling.CLIAbstraction`
      |rarr| Calling other programs from such an application.
   :mod:`pyTooling.Warning`
      |rarr| Collecting warnings that the application then writes.
"""
from __future__              import annotations

from datetime                import datetime
from enum                    import Enum, unique
from io                      import TextIOWrapper
from sys                     import stdin, stdout, stderr
from textwrap                import dedent
from types                   import ModuleType
from typing                  import NoReturn, Any, Optional as Nullable, Callable, ClassVar
from pyTooling.Exceptions    import MissingDependencyError
from pyTooling.Versioning    import PythonVersion

try:
	from colorama import Fore as Foreground
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="colorama", extra="terminal") from ex

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, mixin
from pyTooling.Exceptions  import PlatformNotSupportedError, ExceptionBase
from pyTooling.Common      import lastItem, getFullyQualifiedName
from pyTooling.Platform    import Platform


@export
class TerminalBaseApplication(metaclass=ExtendedType, slots=True, singleton=True):
	"""
	The class offers a basic terminal application base-class.

	It offers basic colored output via `colorama <https://GitHub.com/tartley/colorama>`__ as well as retrieving the
	terminal's width.
	"""

	NOT_IMPLEMENTED_EXCEPTION_EXIT_CODE: ClassVar[int] =   240   #: Return code, if unimplemented methods or code sections were called.
	UNHANDLED_EXCEPTION_EXIT_CODE: ClassVar[int] =         241   #: Return code, if an unhandled exception reached the topmost exception handler.
	#: Return code (242), if an optional dependency is missing. The value lives on the exception, which stays
	#: importable when this module is not - see :meth:`PrintMissingDependencyException`.
	MISSING_DEPENDENCY_EXIT_CODE: ClassVar[int] =          MissingDependencyError.EXIT_CODE
	FATAL_EXIT_CODE: ClassVar[int] =                       255   #: Return code for fatal exits.
	ISSUE_TRACKER_URL: ClassVar[str] =                     None  #: URL to the issue tracker for reporting bugs.
	INDENT: ClassVar[str] =                                "  "  #: Indentation. Default: ``"  "`` (2 spaces)

	try:
		from colorama import Fore as Foreground
		Foreground: ClassVar[dict[str, str]] = {
			"RED":          Foreground.LIGHTRED_EX,
			"DARK_RED":		  Foreground.RED,
			"GREEN":        Foreground.LIGHTGREEN_EX,
			"DARK_GREEN":   Foreground.GREEN,
			"YELLOW":       Foreground.LIGHTYELLOW_EX,
			"DARK_YELLOW":  Foreground.YELLOW,
			"MAGENTA":      Foreground.LIGHTMAGENTA_EX,
			"BLUE":         Foreground.LIGHTBLUE_EX,
			"DARK_BLUE":    Foreground.BLUE,
			"CYAN":         Foreground.LIGHTCYAN_EX,
			"DARK_CYAN":    Foreground.CYAN,
			"GRAY":         Foreground.WHITE,
			"DARK_GRAY":    Foreground.LIGHTBLACK_EX,
			"WHITE":        Foreground.LIGHTWHITE_EX,
			"NOCOLOR":      Foreground.RESET,

			"HEADLINE":     Foreground.LIGHTMAGENTA_EX,
			"ERROR":        Foreground.LIGHTRED_EX,
			"WARNING":      Foreground.LIGHTYELLOW_EX
		}                 #: Terminal colors
	except ImportError:  # pragma: no cover
		Foreground: ClassVar[dict[str, str]] = {
			"RED":         "",
			"DARK_RED":    "",
			"GREEN":       "",
			"DARK_GREEN":  "",
			"YELLOW":      "",
			"DARK_YELLOW": "",
			"MAGENTA":     "",
			"BLUE":        "",
			"DARK_BLUE":   "",
			"CYAN":        "",
			"DARK_CYAN":   "",
			"GRAY":        "",
			"DARK_GRAY":   "",
			"WHITE":       "",
			"NOCOLOR":     "",

			"HEADLINE":    "",
			"ERROR":       "",
			"WARNING":     ""
		}               #: Terminal colors

	_stdin:  TextIOWrapper  #: STDIN
	_stdout: TextIOWrapper  #: STDOUT
	_stderr: TextIOWrapper  #: STDERR
	_width:  int            #: Terminal width in characters
	_height: int            #: Terminal height in characters

	def __init__(self) -> None:
		"""
		Initialize a terminal.

		If the Python package `colorama <https://pypi.org/project/colorama/>`_ [#f_colorama]_ is available, then initialize
		it for colored outputs.

		.. [#f_colorama] Colorama on Github: https://GitHub.com/tartley/colorama
		"""

		self._stdin =  stdin
		self._stdout = stdout
		self._stderr = stderr
		if stdout.isatty():
			self.InitializeColors()
		else:
			self.UninitializeColors()
		self._width, self._height = self.GetTerminalSize()

	def InitializeColors(self) -> bool:
		"""
		Initialize the terminal for color support by `colorama <https://GitHub.com/tartley/colorama>`__.

		:returns: True, if 'colorama' package could be imported and initialized.
		"""
		try:
			from colorama import init

			init()
			return True
		except ImportError:  # pragma: no cover
			return False

	def UninitializeColors(self) -> bool:
		"""
		Uninitialize the terminal for color support by `colorama <https://GitHub.com/tartley/colorama>`__.

		:returns: True, if 'colorama' package could be imported and uninitialized.
		"""
		try:
			from colorama import deinit

			deinit()
			return True
		except ImportError:  # pragma: no cover
			return False

	@readonly
	def Width(self) -> int:
		"""
		Read-only property to access the terminal's width.

		:returns: The terminal window's width in characters.
		"""
		return self._width

	@readonly
	def Height(self) -> int:
		"""
		Read-only property to access the terminal's height.

		:returns: The terminal window's height in characters.
		"""
		return self._height

	@staticmethod
	def GetTerminalSize() -> tuple[int, int]:
		"""
		Returns the terminal size as tuple (width, height) for Windows, macOS (Darwin), Linux, cygwin (Windows), MinGW32/64 (Windows).

		:returns:                          A tuple containing width and height of the terminal's size in characters.
		:raises PlatformNotSupportedError: When a platform is not yet supported.
		"""
		platform = Platform()
		if platform.IsNativeWindows:
			size = TerminalBaseApplication.__GetTerminalSizeOnWindows()
		elif (platform.IsNativeLinux or platform.IsNativeFreeBSD or platform.IsNativeMacOS or platform.IsMinGW32OnWindows or platform.IsMinGW64OnWindows
					or platform.IsUCRT64OnWindows or platform.IsCygwin32OnWindows or platform.IsClang64OnWindows):
			size = TerminalBaseApplication.__GetTerminalSizeOnLinux()
		else:  # pragma: no cover
			raise PlatformNotSupportedError(f"Platform '{platform}' not yet supported.")

		if size is None:   # pragma: no cover
			size = (80, 25)  # default size

		return size

	@staticmethod
	def __GetTerminalSizeOnWindows() -> Nullable[tuple[int, int]]:
		"""
		Returns the current terminal window's size for Windows.

		``kernel32.dll:GetConsoleScreenBufferInfo()`` is used to retrieve the information.

		:returns: A tuple containing width and height of the terminal's size in characters.
		"""
		try:
			from ctypes import windll, create_string_buffer
			from struct import unpack as struct_unpack

			hStdError =    windll.kernel32.GetStdHandle(-12)                  # stderr handle = -12
			stringBuffer = create_string_buffer(22)
			result =       windll.kernel32.GetConsoleScreenBufferInfo(hStdError, stringBuffer)
			if result:
				bufx, bufy, curx, cury, wattr, left, top, right, bottom, maxx, maxy = struct_unpack("hhhhHhhhhhh", stringBuffer.raw)
				width =  right - left + 1
				height = bottom - top + 1
				return width, height
		except ImportError:
			pass

		return None
		# return Terminal.__GetTerminalSizeWithTPut()

	# @staticmethod
	# def __GetTerminalSizeWithTPut() -> tuple[int, int]:
	# 	"""
	# 	Returns the current terminal window's size for Windows.
	#
	# 	``tput`` is used to retrieve the information.
	#
	# 	:returns: A tuple containing width and height of the terminal's size in characters.
	# 	"""
	# 	from subprocess import check_output
	#
	# 	try:
	# 		width =  int(check_output(("tput", "cols")))
	# 		height = int(check_output(("tput", "lines")))
	# 		return (width, height)
	# 	except:
	# 		pass

	@staticmethod
	def __GetTerminalSizeOfFileDescriptor(fd: int) -> Nullable[tuple[int, int]]:
		"""
		Get window size of a file descriptor.

		Call `ioctl` with ``TIOCGWINSZ`` (GetWindowsSize) for the given file descriptor.

		:param fd: File descriptor to query.
		:returns:  A 2-tuple of terminal width and height, or ``None`` if the size couldn't be determined.
		"""
		try:
			from array import array
			from fcntl import ioctl
			from termios import TIOCGWINSZ
		except ImportError:
			return None

		# Allocate an array of 4x unsigned short (C struct)
		# H = unsigned short (16-bit)
		buffer = array('H', [0, 0, 0, 0])  # rows, columns, x-pixels, y-pixels
		try:
			ioctl(fd, TIOCGWINSZ, buffer, True)
			return buffer[1], buffer[0]
		except OSError:
			return None

	@staticmethod
	def __GetTerminalSizeOnLinux() -> Nullable[tuple[int, int]]:
		"""
		Returns the current terminal window's size for Linux.

		``ioctl(TIOCGWINSZ)`` is used to retrieve the information. As a fallback, environment variables ``COLUMNS`` and
		``LINES`` are checked.

		:returns: A tuple containing width and height of the terminal's size in characters.
		"""
		# STDIN, STDOUT, STDERR
		for fd in range(3):
			if (size := TerminalBaseApplication.__GetTerminalSizeOfFileDescriptor(fd)) is not None:
				return size

		# Fallback
		fd = None
		try:
			from os import open, close, ctermid, O_RDONLY

			fd = open(ctermid(), O_RDONLY)
			if (size := TerminalBaseApplication.__GetTerminalSizeOfFileDescriptor(fd)) is not None:
				return size
		except (ImportError, OSError):
			# ImportError - If ctermid is not available (e.g. MSYS2)
			# OSError     - If ctermid() or open() fails
			pass
		finally:
			if fd is not None:
				try:
					close(fd)
				except OSError:
					pass

		# Fall-fallback
		from os import getenv

		try:
			columns = int(getenv("COLUMNS"))
			lines =   int(getenv("LINES"))
			return columns, lines
		except TypeError:
			pass

		return None

	def WriteToStdOut(self, message: str) -> int:
		"""
		Low-level method for writing to ``STDOUT``.

		:param message: Message to write to ``STDOUT``.
		:returns:       Number of written characters.
		"""
		return self._stdout.write(message)

	def WriteLineToStdOut(self, message: str, end: str = "\n") -> int:
		"""
		Low-level method for writing to ``STDOUT``.

		:param message: Message to write to ``STDOUT``.
		:param end:     Optional, use newline character. Default: ``\\n``.
		:returns:       Number of written characters.
		"""
		return self._stdout.write(message + end)

	def WriteToStdErr(self, message: str) -> int:
		"""
		Low-level method for writing to ``STDERR``.

		:param message: Message to write to ``STDERR``.
		:returns:       Number of written characters.
		"""
		return self._stderr.write(message)

	def WriteLineToStdErr(self, message: str, end: str = "\n") -> int:
		"""
		Low-level method for writing to ``STDERR``.

		:param message: Message to write to ``STDERR``.
		:param end:     Optional, use newline character. Default: ``\\n``.
		:returns:       Number of written characters.
		"""
		return self._stderr.write(message + end)

	def FatalExit(self, returnCode: int = 0) -> NoReturn:
		"""
		Exit the terminal application by uninitializing color support and returning a fatal Exit code.

		:param returnCode: Optional, return code for application exit.
		"""
		self.Exit(self.FATAL_EXIT_CODE if returnCode == 0 else returnCode)

	def Exit(self, returnCode: int = 0) -> NoReturn:
		"""
		Exit the terminal application by uninitializing color support and returning an Exit code.

		:param returnCode: Optional, return code for application exit.
		"""
		self.UninitializeColors()
		exit(returnCode)

	def PrintException(self, ex: Exception) -> NoReturn:
		"""
		Prints an exception of type :exc:`Exception` and its traceback.

		If the exception as a nested action, the cause is printed as well.

		If ``ISSUE_TRACKER_URL`` is configured, a URL to the issue tracker is added.

		:param ex: The exception to print.
		"""
		from traceback import format_tb, walk_tb

		frame, sourceLine = lastItem(walk_tb(ex.__traceback__))
		filename = frame.f_code.co_filename
		funcName = frame.f_code.co_name

		exceptionType = getFullyQualifiedName(ex)

		message  = f"{{RED}}[FATAL] An unknown or unhandled exception reached the topmost exception handler!{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Exception type:{{NOCOLOR}}       {{DARK_RED}}{exceptionType}{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Exception message:{{NOCOLOR}}    {{RED}}{ex!s}{{NOCOLOR}}\n"

		if hasattr(ex, "__notes__") and len(ex.__notes__) > 0:
			note = next(iterator := iter(ex.__notes__))
			message += f"{{indent}}{{YELLOW}}Notes:{{NOCOLOR}}                {{DARK_CYAN}}{note}{{NOCOLOR}}\n"
			for note in iterator:
				message += f"{{indent}}                      {{DARK_CYAN}}{note}{{NOCOLOR}}\n"

		message += f"{{indent}}{{YELLOW}}Caused in:{{NOCOLOR}}            {funcName}(...) in file '{filename}' at line {sourceLine}\n"

		if (ex2 := ex.__cause__) is not None:
			causeType = getFullyQualifiedName(ex2)

			message += f"{{indent2}}{{DARK_YELLOW}}Caused by ex. type:{{NOCOLOR}} {{DARK_RED}}{causeType}{{NOCOLOR}}\n"
			message += f"{{indent2}}{{DARK_YELLOW}}Caused by message:{{NOCOLOR}}  {ex2!s}{{NOCOLOR}}\n"

			if hasattr(ex2, "__notes__") and len(ex2.__notes__) > 0:
				note = next(iterator := iter(ex2.__notes__))
				message += f"{{indent2}}{{DARK_YELLOW}}Notes:{{NOCOLOR}}              {{DARK_CYAN}}{note}{{NOCOLOR}}\n"
				for note in iterator:
					message += f"{{indent2}}                    {{DARK_CYAN}}{note}{{NOCOLOR}}\n"

		message += f"{{indent}}{{RED}}{'-' * 120}{{NOCOLOR}}\n"
		for line in format_tb(ex.__traceback__):
			message += f"{line.replace('{', '{{').replace('}', '}}')}"
		message += f"{{indent}}{{RED}}{'-' * 120}{{NOCOLOR}}"

		if self.ISSUE_TRACKER_URL is not None:
			message += f"\n{{indent}}{{DARK_CYAN}}Please report this bug at GitHub: {self.ISSUE_TRACKER_URL}{{NOCOLOR}}\n"
			message += f"{{indent}}{{RED}}{'-' * 120}{{NOCOLOR}}"

		self.WriteLineToStdErr(message.format(indent=self.INDENT, indent2=self.INDENT*2, **self.Foreground))
		self.Exit(self.UNHANDLED_EXCEPTION_EXIT_CODE)

	def PrintMissingDependencyException(self, ex: MissingDependencyError) -> NoReturn:
		"""
		Print a missing optional dependency and the command lines installing it.

		Unlike the other printers, this one does **not** report a bug: there is no traceback, and no invitation to
		open an issue, because nothing is wrong with the program - a package it can use is not installed. The message
		names the missing package and every installation option the exception carries
		(:attr:`~pyTooling.Exceptions.MissingDependencyError.InstallCommands`).

		.. attention::

		   :mod:`pyTooling.TerminalUI` raises this exception **itself** when *colorama* is missing, and that happens
		   while the module is imported - long before an application object exists, so this method cannot report that
		   case. An application that wants to survive it catches the exception around its own imports and prints the
		   commands directly:

		   .. code-block:: python

		      from pyTooling.Exceptions import MissingDependencyError

		      try:
		        from pyTooling.TerminalUI import TerminalApplication
		      except MissingDependencyError as ex:
		        print(f"{ex}\n" + "\n".join(f"  {command}" for command in ex.InstallCommands))
		        raise SystemExit(MissingDependencyError.EXIT_CODE) from ex

		:param ex: The exception to print.
		:returns:  Never - the method exits the application with :attr:`MISSING_DEPENDENCY_EXIT_CODE`.

		.. seealso::

		   :meth:`PrintException`
		      |rarr| Print an unhandled exception and its traceback.
		   :meth:`PrintNotImplementedError`
		      |rarr| Print a call to an unimplemented function or abstract method.
		"""
		message  = f"{{RED}}[MISSING DEPENDENCY] An optional dependency is not installed!{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Missing package:{{NOCOLOR}}      {{DARK_RED}}{ex.Dependency}{{NOCOLOR}}\n"

		commands = iter(ex.InstallCommands)
		message += f"{{indent}}{{YELLOW}}Install it with:{{NOCOLOR}}      {{DARK_CYAN}}{next(commands)}{{NOCOLOR}}\n"
		for command in commands:
			message += f"{{indent}}                      {{DARK_CYAN}}{command}{{NOCOLOR}}\n"

		if (cause := ex.__cause__) is not None:
			message += f"{{indent}}{{YELLOW}}Caused by:{{NOCOLOR}}            {{RED}}{cause!s}{{NOCOLOR}}\n"

		self.WriteLineToStdErr(message.format(indent=self.INDENT, indent2=self.INDENT * 2, **self.Foreground))
		self.Exit(self.MISSING_DEPENDENCY_EXIT_CODE)

	def PrintNotImplementedError(self, ex: NotImplementedError) -> NoReturn:
		"""
		Prints a not-implemented exception of type :exc:`NotImplementedError`.

		If ``ISSUE_TRACKER_URL`` is configured, a URL to the issue tracker is added.

		:param ex: The exception to print.
		"""
		from traceback import walk_tb

		frame, sourceLine = lastItem(walk_tb(ex.__traceback__))
		filename = frame.f_code.co_filename
		funcName = frame.f_code.co_name

		message  = f"{{RED}}[NOT IMPLEMENTED] An unimplemented function or abstract method was called!{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Function or method:{{NOCOLOR}}   {{DARK_RED}}{funcName}(...){{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Exception message:{{NOCOLOR}}    {{RED}}{ex!s}{{NOCOLOR}}\n"

		if hasattr(ex, "__notes__") and len(ex.__notes__) > 0:
			note = next(iterator := iter(ex.__notes__))
			message += f"{{indent}}{{YELLOW}}Notes:{{NOCOLOR}}                {{DARK_CYAN}}{note}{{NOCOLOR}}\n"
			for note in iterator:
				message += f"{{indent}}                      {{DARK_CYAN}}{note}{{NOCOLOR}}\n"

		message += f"{{indent}}{{YELLOW}}Caused in:{{NOCOLOR}}            {funcName}(...) in file '{filename}' at line {sourceLine}\n"

		if self.ISSUE_TRACKER_URL is not None:
			message += f"\n{{indent}}{{DARK_CYAN}}Please report this bug at GitHub: {self.ISSUE_TRACKER_URL}{{NOCOLOR}}\n"
			message += f"{{indent}}{{RED}}{'-' * 120}{{NOCOLOR}}"

		self.WriteLineToStdErr(message.format(indent=self.INDENT, indent2=self.INDENT * 2, **self.Foreground))
		self.Exit(self.NOT_IMPLEMENTED_EXCEPTION_EXIT_CODE)

	def PrintExceptionBase(self, ex: Exception) -> NoReturn:
		"""
		Prints an exception of type :exc:`~pyTooling.Exceptions.ExceptionBase` and its traceback.

		If the exception as a nested action, the cause is printed as well.

		If ``ISSUE_TRACKER_URL`` is configured, a URL to the issue tracker is added.

		:param ex: The exception to print.
		"""
		from traceback import print_tb, walk_tb

		frame, sourceLine = lastItem(walk_tb(ex.__traceback__))
		filename = frame.f_code.co_filename
		funcName = frame.f_code.co_name

		exceptionType = getFullyQualifiedName(ex)

		self.WriteLineToStdErr(dedent(f"""\
			{{RED}}[FATAL] A known but unhandled exception reached the topmost exception handler!{{NOCOLOR}}
			{{indent}}{{YELLOW}}Exception type:{{NOCOLOR}}       {{DARK_RED}}{exceptionType}{{NOCOLOR}}
			{{indent}}{{YELLOW}}Exception message:{{NOCOLOR}}    {{RED}}{ex!s}{{NOCOLOR}}
			{{indent}}{{YELLOW}}Caused in:{{NOCOLOR}}            {funcName}(...) in file '{filename}' at line {sourceLine}\
			""").format(indent=self.INDENT, **self.Foreground))

		if ex.__cause__ is not None:
			causeType = getFullyQualifiedName(ex.__cause__)

			self.WriteLineToStdErr(dedent(f"""\
				{{indent2}}{{DARK_YELLOW}}Caused by ex. type:{{NOCOLOR}} {{DARK_RED}}{causeType}{{NOCOLOR}}
				{{indent2}}{{DARK_YELLOW}}Caused by message:{{NOCOLOR}}  {{RED}}{ex.__cause__!s}{{NOCOLOR}}\
				""").format(indent2=self.INDENT * 2, **self.Foreground))

		self.WriteLineToStdErr(f"""{{indent}}{{RED}}{'-' * 80}{{NOCOLOR}}""".format(indent=self.INDENT, **self.Foreground))
		print_tb(ex.__traceback__, file=self._stderr)
		self.WriteLineToStdErr(f"""{{indent}}{{RED}}{'-' * 80}{{NOCOLOR}}""".format(indent=self.INDENT, **self.Foreground))

		if self.ISSUE_TRACKER_URL is not None:
			self.WriteLineToStdErr(dedent(f"""\
				{{indent}}{{DARK_CYAN}}Please report this bug at GitHub: {self.ISSUE_TRACKER_URL}{{NOCOLOR}}
				{{indent}}{{RED}}{'-' * 80}{{NOCOLOR}}\
				""").format(indent=self.INDENT, **self.Foreground))

		self.Exit(self.UNHANDLED_EXCEPTION_EXIT_CODE)


@export
@unique
class Severity(Enum):
	"""Logging message severity levels."""

	Exception =      120    #: Unhandled exception messages
	ExceptionCause = 115    #: Exception cause
	ExceptionNote =  110    #: Exception notes
	Fatal =          100    #: Fatal messages
	Error =           80    #: Error messages
	Quiet =           70    #: Always visible messages, even in quiet mode.

	Critical =        60    #: Critical messages
	CriticalNote =    55    #: Critical notes
	Warning =         50    #: Warning messages
	WarningNote =     45    #: Warning notes
	Silent =          40    #: Severity level for silenced messages.

	Info =            20    #: Informative messages
	Normal =          10    #: Normal messages
	DryRun =           8    #: Messages visible in a dry-run
	Verbose =          5    #: Verbose messages
	Debug =            2    #: Debug messages
	All =              0    #: All messages

	def __hash__(self) -> int:
		"""
		Compute a hash of the severity level, so it can be used as a key in a dictionary.

		:returns: Hash of the severity level's name.
		"""
		return hash(self.name)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both severity levels are equal.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value == other.value
		else:
			ex = TypeError(f"Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both severity levels are unequal.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value != other.value
		else:
			ex = TypeError(f"Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for less-than.

		:param other:      Operand to compare against.
		:returns:          ``True``, if severity levels is less than other severity level.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value < other.value
		else:
			ex = TypeError(f"Second operand is not supported by < operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex

	def __le__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for less-than-or-equal.

		:param other:      Operand to compare against.
		:returns:          ``True``, if severity levels is less than or equal other severity level.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value <= other.value
		else:
			ex = TypeError(f"Second operand is not supported by <= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for greater-than.

		:param other:      Operand to compare against.
		:returns:          ``True``, if severity levels is greater than other severity level.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value >	other.value
		else:
			ex = TypeError(f"Second operand is not supported by > operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two Severity instances (severity level) for greater-than-or-equal.

		:param other:      Operand to compare against.
		:returns:          ``True``, if severity levels is greater than or equal other severity level.
		:raises TypeError: If operand ``other`` is not of type :class:`Severity`.
		"""
		if isinstance(other, Severity):
			return self.value >= other.value
		else:
			ex = TypeError(f"Second operand is not supported by >= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex


@export
@unique
class Mode(Enum):
	"""Routing modes deciding to which stream (``STDOUT``/``STDERR``) a message of a certain severity is written."""

	TextToStdOut_ErrorsToStdErr = 0  #: Warnings and higher severities to ``STDERR``, except :attr:`Severity.Quiet`.
	AllLinearToStdOut =           1  #: All messages to ``STDOUT``, so the message order is preserved in a log file.
	DataToStdOut_OtherToStdErr =  2  #: All messages to ``STDERR``, leaving ``STDOUT`` for the program's data.


@export
class Line(metaclass=ExtendedType, slots=True):
	"""
	Represents a single message line with a severity and indentation level.
	"""

	_LOG_MESSAGE_FORMAT__: ClassVar[dict[Severity, str]] = {
		Severity.Exception:     "EXCEPTION: {message}",
		Severity.ExceptionNote: "           > {message}",
		Severity.Fatal:         "FATAL: {message}",
		Severity.Error:         "ERROR: {message}",
		Severity.Quiet:         "{message}",
		Severity.Critical:      "CRITICAL: {message}",
		Severity.CriticalNote:  "          > {message}",
		Severity.Warning:       "WARNING: {message}",
		Severity.WarningNote:   "         > {message}",
		Severity.Info:          "INFO: {message}",
		Severity.Normal:        "{message}",
		Severity.DryRun:        "DRYRUN: {message}",
		Severity.Verbose:       "VERBOSE: {message}",
		Severity.Debug:         "DEBUG: {message}",
	}                           #: Message line formatting rules.

	_timestamp:       datetime  #: Timestamp when the line was created.
	_message:         str       #: Text message (line content).
	_severity:        Severity  #: Message severity
	_indent:          int       #: Indentation
	_appendLinebreak: bool      #: True, if a trailing linebreak should be added when printing this line object.

	def __init__(
		self,
		message:  str,
		severity: Severity = Severity.Normal,
		*,
		indent:   int = 0,
		appendLinebreak: bool = True
	) -> None:
		"""
		Initialize a line object representing the single-line message.

		:param message:         Message to display.
		:param severity:        Optional, severity level of the message.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, if ``True``, append a line break at the end of the message.
		"""
		self._timestamp =       datetime.now()
		self._severity =        severity
		self._message =         message
		self._indent =          indent
		self._appendLinebreak = appendLinebreak

	@readonly
	def Message(self) -> str:
		"""
		Read-only property to access the line's raw message.

		:returns: Raw message of the line.
		"""
		return self._message

	@readonly
	def Severity(self) -> Severity:
		"""
		Read-only property to access the line's severity level.

		:returns: Severity level of the message line.
		"""
		return self._severity

	@readonly
	def Indent(self) -> int:
		"""
		Read-only property to access the line's indentation level.

		:returns: Indentation level of the message line.
		"""
		return self._indent

	def IndentBy(self, indent: int) -> int:
		"""
		Increase a line's indentation level.

		:param indent: Optional, indentation level added to the current indentation level.
		:returns:      The new indentation level.
		"""
		self._indent = (newIndent := self._indent + indent)
		return newIndent

	@readonly
	def AppendLinebreak(self) -> bool:
		"""
		Read-only property to access if a linebreak is added after the line's message.

		:returns: True, if a linebreak should be added.
		"""
		return self._appendLinebreak

	def __str__(self) -> str:
		"""
		Returns a formatted version of a ``Line`` objects as a string.

		The formatting is defined in :attr:`_LOG_MESSAGE_FORMAT__`.

		:returns: Formatted version of a ``Line`` object.
		"""
		return self._LOG_MESSAGE_FORMAT__[self._severity].format(message=self._message)


@export
@mixin
class ILineTerminal:
	"""A mixin class (interface) to provide class-local terminal writing methods."""

	_terminal: Nullable[TerminalApplication]  #: The terminal application the messages are written to.

	def __init__(self, terminal: Nullable[TerminalApplication] = None) -> None:
		"""
		MixIn initializer.

		:param terminal: Optional, the terminal to write to. If ``None``, every writing method does nothing.
		"""
		self._terminal = terminal

		# FIXME: Alter methods if a terminal is present or set dummy methods

	@readonly
	def Terminal(self) -> Nullable[TerminalApplication]:
		"""
		Read-only property to access the local terminal instance (:attr:`_terminal`).

		:returns: The terminal instance, or ``None`` if no terminal is attached.
		"""
		return self._terminal

	def WriteLine(self, line: Line, condition: bool = True) -> bool:
		"""
		Write a line to the local terminal if ``condition`` is ``True``.

		:param line:      Line object to write.
		:param condition: Optional, write the line only if this condition is ``True``. Default: ``True``.
		:returns:         True, if the line was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteLine(line)
		return False

	# def _TryWriteLine(self, *args: Any, condition: bool = True, **kwargs: Any):
	# 	if (self._terminal is not None) and condition:
	# 		return self._terminal.TryWrite(*args, **kwargs)
	# 	return False

	def WriteFatal(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a fatal message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteFatal(*args, **kwargs)
		return False

	def WriteError(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write an error message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteError(*args, **kwargs)
		return False

	def WriteCritical(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a critical warning message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteCritical(*args, **kwargs)
		return False

	def WriteWarning(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a warning message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteWarning(*args, **kwargs)
		return False

	def WriteInfo(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write an info message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteInfo(*args, **kwargs)
		return False

	def WriteQuiet(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write an always visible message, even in quiet mode, to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteQuiet(*args, **kwargs)
		return False

	def WriteNormal(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a *normal* message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteNormal(*args, **kwargs)
		return False

	def WriteVerbose(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a verbose message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteVerbose(*args, **kwargs)
		return False

	def WriteDebug(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a debug message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteDebug(*args, **kwargs)
		return False

	def WriteDryRun(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""
		Write a dry-run message to the local terminal if ``condition`` is ``True``.

		:param args:      Positional parameters forwarded to the terminal's writing method.
		:param condition: Optional, write the message only if this condition is ``True``. Default: ``True``.
		:param kwargs:    Keyword parameters forwarded to the terminal's writing method.
		:returns:         True, if the message was actually written.
		"""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteDryRun(*args, **kwargs)
		return False


@export
class TerminalApplication(TerminalBaseApplication):  #, ILineTerminal):
	"""
	A base-class for implementation of terminal applications emitting line-by-line messages.
	"""
	_LOG_MESSAGE_FORMAT__: ClassVar[dict[Severity, str]] = {
		Severity.Exception:            "{RED}[EXCEPTION] {message}{NOCOLOR}",
		Severity.ExceptionNote:   "{DARK_RED}            > {message}{NOCOLOR}",
		Severity.Fatal:           "{DARK_RED}[FATAL]     {message}{NOCOLOR}",
		Severity.Error:                "{RED}[ERROR]     {message}{NOCOLOR}",
		Severity.Quiet:              "{WHITE}{message}{NOCOLOR}",
		Severity.Critical:     "{DARK_YELLOW}[CRITICAL]  {message}{NOCOLOR}",
		Severity.CriticalNote: "{DARK_YELLOW}            > {message}{NOCOLOR}",
		Severity.Warning:           "{YELLOW}[WARNING]   {message}{NOCOLOR}",
		Severity.WarningNote:  "{DARK_YELLOW}            > {message}{NOCOLOR}",
		Severity.Info:               "{WHITE}{message}{NOCOLOR}",
		Severity.Normal:             "{WHITE}{message}{NOCOLOR}",
		Severity.DryRun:         "{DARK_CYAN}[DRY] {message}{NOCOLOR}",
		Severity.Verbose:             "{GRAY}{message}{NOCOLOR}",
		Severity.Debug:          "{DARK_GRAY}{message}{NOCOLOR}"
	}                          #: Message formatting rules.

	_LOG_LEVEL_ROUTING__: dict[Severity, tuple[Callable[[str, str], int]]]  #: Message routing rules.
	_verbose:       bool        #: ``True``, if verbose messages are written.
	_debug:         bool        #: ``True``, if debug messages are written.
	_silent:        bool        #: ``True``, if no messages are written at all.
	_quiet:         bool        #: ``True``, if only errors and quiet messages are written.
	_writeLevel:    Severity    #: Minimal severity a message needs to be written.
	_writeToStdOut: bool        #: ``True``, if messages are written to ``STDOUT`` instead of ``STDERR``.

	_lines:         list[Line]  #: Every message written so far, in the order it was written.
	_baseIndent:    int         #: Indentation level added to every message's own indentation.

	_errorCount:           int  #: Number of errors written so far.
	_criticalWarningCount: int  #: Number of critical warnings written so far.
	_warningCount:         int  #: Number of warnings written so far.

	HeadLine:       ClassVar[str]  #: Headline of the application, printed by :meth:`_PrintHeadline`.

	def __init__(self, mode: Mode = Mode.AllLinearToStdOut) -> None:
		"""
		Initializer of a line-based terminal interface.

		:param mode: Optional, defines what output (normal, error, data) to write where. Default: a linear flow all to
		             *STDOUT*.
		"""
		TerminalBaseApplication.__init__(self)
		# ILineTerminal.__init__(self, self)

		self._LOG_LEVEL_ROUTING__ = {}
		self.__InitializeLogLevelRouting(mode)

		self._verbose =        False
		self._debug =          False
		self._silent =         False
		self._quiet =          False
		self._writeLevel =     Severity.Normal
		self._writeToStdOut =  True

		self._lines =          []
		self._baseIndent =     0

		self._errorCount =           0
		self._criticalWarningCount = 0
		self._warningCount =         0

	def __InitializeLogLevelRouting(self, mode: Mode = Mode.AllLinearToStdOut) -> None:
		"""
		Expand a routing mode into a routing table containing one writing method per severity level.

		:param mode:           Optional, routing mode to expand.
		:raises ExceptionBase: If the routing mode is not supported. |br|
		                       The note lists the modes that are supported.
		"""
		if mode is Mode.TextToStdOut_ErrorsToStdErr:
			for severity in Severity:
				if severity >= Severity.Silent and severity != Severity.Quiet:
					self._LOG_LEVEL_ROUTING__[severity] = (self.WriteLineToStdErr,)
				else:
					self._LOG_LEVEL_ROUTING__[severity] = (self.WriteLineToStdOut,)
		elif mode is Mode.AllLinearToStdOut:
			for severity in Severity:
				self._LOG_LEVEL_ROUTING__[severity] =   (self.WriteLineToStdOut, )
		elif mode is Mode.DataToStdOut_OtherToStdErr:
			for severity in Severity:
				self._LOG_LEVEL_ROUTING__[severity] =   (self.WriteLineToStdErr, )
		else:  # pragma: no cover
			ex = ExceptionBase(f"Unsupported mode '{mode}'.")
			ex.add_note(f"Unsupported modes '{', '.join(m.name for m in Mode)}'.")
			raise ex

	def _PrintHeadline(self, width: int = 80) -> None:
		"""
		Helper method to print the program headline.

		:param width: Optional, number of characters for horizontal lines.

		.. admonition:: Generated output

		   .. code-block::

		      =========================
		          centered headline
		      =========================
		"""
		if width == 0:
			width = self._width

		self.WriteNormal(f"{{HEADLINE}}{'=' * width}".format(**TerminalApplication.Foreground))
		self.WriteNormal(f"{{HEADLINE}}{{headline: ^{width}s}}".format(headline=self.HeadLine, **TerminalApplication.Foreground))
		self.WriteNormal(f"{{HEADLINE}}{'=' * width}".format(**TerminalApplication.Foreground))

	def _PrintHelp(self, command: Nullable[str] = None) -> None:
		"""
		Helper function to print the command line parsers help page(s).

		:param command: Optional, the subcommand to print the help page(s) for.
		"""
		if command is None:
			self.MainParser.print_help()
		elif command == "help":
			self.WriteWarning("This is a recursion ...")
		else:
			try:
				self.SubParsers[command].print_help()
			except KeyError:
				self.WriteError(f"Command {command} is unknown.")

	def _PrintVersion(
		self,
		dunderModule:        ModuleType,
		packageName:         Nullable[str] = None,
		versionCheckTimeout: int = 1
	) -> None:
		"""
		Helper method to print the version information.

		:param dunderModule:        The Python module containing the dunder variables for author(s), email, copyright,
		                            version, ...
		:param packageName:         Optional, name of the package on PyPI. If given, the latest released version is
		                            queried and reported as an available update. Default: ``None``.
		:param versionCheckTimeout: Optional, timeout in seconds for the PyPI request. Default: ``1``.

		.. admonition:: Example usage

		   .. code-block:: Python

		      def _PrintVersion(self):
		        import myPackage.MyModule as DunderModule

		        super()._PrintVersion(
		          DunderModule,
		          "MyModule"
		        )
		"""
		copyrights = getattr(dunderModule, "__copyright__", "{RED}Copyright not set!".format(RED=Foreground.RED)).split("\n", 1)
		self.WriteNormal(f"Copyright:     {copyrights[0]}")
		for copyright in copyrights[1:]:
			self.WriteNormal(f"               {copyright}")

		license = getattr(dunderModule, "__license__", "{RED}License not set!".format(RED=Foreground.RED))
		self.WriteNormal(f"License:       {license}")

		authors = getattr(dunderModule, "__author__", "{RED}Unknown author!".format(RED=Foreground.RED)).split(", ")
		self.WriteNormal(f"Authors:       {authors[0]}")
		for author in authors[1:]:
			self.WriteNormal(f"               {author}")

		if (email := getattr(dunderModule, "__email__", None)) is not None:
			self.WriteNormal(f"Email:         {email}")

		if (version := getattr(dunderModule, "__version__", None)) is None:
			self.WriteNormal("Version:       {RED}Version not set!".format(RED=Foreground.RED))
		else:
			currentVersion = PythonVersion.Parse(version)
			if packageName is None:
				update = ""
			elif (pypiVersion := self._GetLatestVersion(packageName, versionCheckTimeout)) is not None:
				latestVersion = PythonVersion.Parse(pypiVersion)
				update = f" (Update available: v{latestVersion})" if currentVersion < latestVersion else " (latest)"
			else:
				update = " (PyPI timeout)"
			self.WriteNormal(f"Version:       v{version}{update}")

		if (projectURL := getattr(dunderModule, "__project_url__", None)) is not None:
			self.WriteNormal(f"Project:       {projectURL}")

		if (documentationURL := getattr(dunderModule, "__documentation_url__", None)) is not None:
			self.WriteNormal(f"Documentation: {documentationURL}")

		if (issueTrackerURL := getattr(dunderModule, "__issue_tracker_url__", None)) is not None:
			self.WriteNormal(f"Issue tracker: {issueTrackerURL}")

	def _GetLatestVersion(self, packageName: str, timeout: int = 1) -> Nullable[str]:
		"""
		Query PyPI for the latest released version of a package.

		Every error - an unreachable index, a timeout, an unknown package - is answered with ``None``, because a version
		check must not fail the application it is printing the version of.

		:param packageName: Optional, name of the package on PyPI.
		:param timeout:     Optional, timeout in seconds for the request. Default: ``1``.
		:returns:           The latest version as a string, or ``None``, if it couldn't be determined.
		"""
		from json import loads
		from urllib.request import urlopen, Request

		request = Request(
			url=f"https://pypi.org/pypi/{packageName}/json",
			headers={'User-Agent': f'{packageName}-Version-Check'}
		)
		try:
			with urlopen(request, timeout=timeout) as response:
				data: dict[str, dict[str, str]] = loads(response.read().decode())
				return data["info"]["version"]
		except Exception:
			return None

	def Configure(
		self,
		*,
		verbose: bool = False,
		debug:   bool = False,
		silent:  bool = False,
		quiet:   bool = False,
		writeToStdOut: bool = True
	) -> None:
		"""
		Configure the verbosity of the application, usually from the command line switches.

		The resulting :attr:`LogLevel` is the minimum severity a message needs to be written: ``Severity.Debug`` in debug
		mode, ``Severity.Verbose`` in verbose mode, ``Severity.Silent`` in silent mode, ``Severity.Quiet`` in quiet mode,
		otherwise ``Severity.Normal``. Debug mode implies verbose mode.

		:param verbose:       Optional, write verbose messages. Default: ``False``.
		:param debug:         Optional, write debug messages, implying verbose messages. Default: ``False``.
		:param silent:        Optional, reduce the messages to warnings and higher severities. Default: ``False``.
		:param quiet:         Optional, reduce the messages to errors and always visible messages. Default: ``False``.
		:param writeToStdOut: Optional, write to ``STDOUT``. Default: ``True``.
		"""
		self._verbose =       True if debug else verbose
		self._debug =         debug
		self._silent =        silent
		self._quiet =         quiet

		if quiet:
			self._writeLevel =  Severity.Quiet
		elif silent:
			self._writeLevel =  Severity.Silent
		elif debug:
			self._writeLevel =  Severity.Debug
		elif verbose:
			self._writeLevel =  Severity.Verbose
		else:
			self._writeLevel =  Severity.Normal

		self._writeToStdOut = writeToStdOut

	@readonly
	def Verbose(self) -> bool:
		"""
		Check if verbose messages are enabled.

		:returns: ``True``, if verbose messages are written.
		"""
		return self._verbose

	@readonly
	def Debug(self) -> bool:
		"""
		Check if debug messages are enabled.

		:returns: ``True``, if debug messages are written.
		"""
		return self._debug

	@readonly
	def Silent(self) -> bool:
		"""
		Check if silent mode is enabled.

		:returns: ``True``, if silent mode is enabled.
		"""
		return self._silent

	@readonly
	def Quiet(self) -> bool:
		"""
		Check if quiet mode is enabled.

		:returns: ``True``, if quiet mode is enabled.
		"""
		return self._quiet

	@property
	def LogLevel(self) -> Severity:
		"""
		Property to access the minimal severity level a message needs to be written (:attr:`_writeLevel`).

		Assigning a level replaces what :meth:`Configure` computed from the verbosity switches.

		:returns: The current minimal severity level.
		"""
		return self._writeLevel

	@LogLevel.setter
	def LogLevel(self, value: Severity) -> None:
		self._writeLevel = value

	@property
	def BaseIndent(self) -> int:
		"""
		Property to access the base indentation level of written messages (:attr:`_baseIndent`).

		The assigned level is added to every message's own indentation.

		:returns: Base indentation level.
		"""
		return self._baseIndent

	@BaseIndent.setter
	def BaseIndent(self, value: int) -> None:
		self._baseIndent = value

	@readonly
	def WarningCount(self) -> int:
		"""
		Read-only property to access the number of counted warnings.

		:returns: Number of warnings.
		"""
		return self._warningCount

	@readonly
	def CriticalWarningCount(self) -> int:
		"""
		Read-only property to access the number of counted critical warnings.

		:returns: Number of critical warnings.
		"""
		return self._criticalWarningCount

	@readonly
	def ErrorCount(self) -> int:
		"""
		Read-only property to access the number of counted errors.

		:returns: Number of errors.
		"""
		return self._errorCount

	@readonly
	def Lines(self) -> list[Line]:
		"""
		Read-only property to access the list of printed lines (messages).

		:returns: List of lines.
		"""
		return self._lines

	def ExitOnPreviousErrors(self) -> None:
		"""
		Exit application if errors have been printed.
		"""
		if self._errorCount > 0:
			self.WriteFatal("Too many errors in previous steps.")

	def ExitOnPreviousCriticalWarnings(
		self,
		includeErrors: bool = True
	) -> None:
		"""
		Exit application if error or critical warnings have been printed.

		:param includeErrors: Optional, if ``True``, count previous errors as well as critical warnings.
		"""
		if includeErrors and (self._errorCount > 0):
			if self._criticalWarningCount > 0:
				self.WriteFatal("Too many errors and critical warnings in previous steps.")
			else:
				self.WriteFatal("Too many errors in previous steps.")
		elif self._criticalWarningCount > 0:
			self.WriteFatal("Too many critical warnings in previous steps.")

	def ExitOnPreviousWarnings(
		self,
		includeCriticalWarnings: bool = True,
		includeErrors:           bool = True
	) -> None:
		"""
		Exit application if error or (critical) warnings have been printed.

		:param includeCriticalWarnings: Optional, if ``True``, count previous critical warnings as well as warnings.
		:param includeErrors:           Optional, if ``True``, count previous errors as well.
		"""
		if includeErrors and (self._errorCount > 0):
			if includeCriticalWarnings and (self._criticalWarningCount > 0):
				if self._warningCount > 0:
					self.WriteFatal("Too many errors and (critical) warnings in previous steps.")
				else:
					self.WriteFatal("Too many errors and critical warnings in previous steps.")
			elif self._warningCount > 0:
				self.WriteFatal("Too many warnings in previous steps.")
			else:
				self.WriteFatal("Too many errors in previous steps.")
		elif includeCriticalWarnings and (self._criticalWarningCount > 0):
			if self._warningCount > 0:
				self.WriteFatal("Too many (critical) warnings in previous steps.")
			else:
				self.WriteFatal("Too many critical warnings in previous steps.")
		elif self._warningCount > 0:
			self.WriteFatal("Too many warnings in previous steps.")

	def WriteLine(self, line: Line) -> bool:
		"""
		Print a formatted line to the underlying terminal/console offered by the operating system.

		:param line: Line object to indent, format and print.
		:returns:    True, if line was actually written.
		"""
		if line.Severity < self._writeLevel:
			return False

		self._lines.append(line)
		for method in self._LOG_LEVEL_ROUTING__[line.Severity]:
			method(self._LOG_MESSAGE_FORMAT__[line.Severity].format(message=line.Message, **self.Foreground), end="\n" if line.AppendLinebreak else "")

		return True

	def TryWriteLine(self, line) -> bool:
		"""
		Check if a line object of a certain severity would be written.

		:param line: Line object to check.
		:returns:    True, if line would be written.
		"""
		severity: Severity = line.Severity     # '@readonly' hands out 'Any' until it is typed - see T75
		return severity >= self._writeLevel

	def WriteFatal(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True,
		exitCode: int = 0,
		immediateExit: bool = True
	) -> bool:
		"""
		Write a fatal message and exit.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:param exitCode:        Optional, exit application with this exit code. Default: ``0`` |br|
		                        If ``0``, use :attr:`FATAL_EXIT_CODE` as exit code.
		:param immediateExit:   Optional, exit application immediately. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		ret = self.WriteLine(Line(message, Severity.Fatal, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))
		if immediateExit:
			self.FatalExit(exitCode)
		return ret

	def WriteError(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write an error message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		self._errorCount += 1
		return self.WriteLine(Line(message, Severity.Error, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteQuiet(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write an always visible message.

		This message is even visible in quiet mode.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.Quiet, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteCritical(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a critical message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		self._criticalWarningCount += 1
		return self.WriteLine(Line(message, Severity.Critical, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteCriticalNote(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a critical note.

		Depending on internal settings and rules, a note might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the note.
		:param appendLinebreak: Optional, append a linebreak after the note. Default: ``True``
		:returns:               True, if note was actually written.
		"""
		return self.WriteLine(Line(message, Severity.CriticalNote, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteWarning(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a warning message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		self._warningCount += 1
		return self.WriteLine(Line(message, Severity.Warning, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteWarningNote(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a warning note.

		Depending on internal settings and rules, a note might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the note.
		:param appendLinebreak: Optional, append a linebreak after the note. Default: ``True``
		:returns:               True, if note was actually written.
		"""
		return self.WriteLine(Line(message, Severity.WarningNote, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteInfo(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write an info message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.Info, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteNormal(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a normal message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.Normal, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteVerbose(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a verbose message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.Verbose, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteDebug(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a debug message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.Debug, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))

	def WriteDryRun(
		self,
		message: str,
		*,
		indent: int = 0,
		appendLinebreak: bool = True
	) -> bool:
		"""
		Write a dry-run message message.

		Depending on internal settings and rules, a message might be skipped.

		:param message:         Message to write.
		:param indent:          Optional, indentation level of the message.
		:param appendLinebreak: Optional, append a linebreak after the message. Default: ``True``
		:returns:               True, if message was actually written.
		"""
		return self.WriteLine(Line(message, Severity.DryRun, indent=self._baseIndent + indent, appendLinebreak=appendLinebreak))
