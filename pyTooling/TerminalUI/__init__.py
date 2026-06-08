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
"""A set of helpers to implement a text user interface (TUI) in a terminal."""
from datetime                import datetime
from enum                    import Enum, unique
from io                      import TextIOWrapper
from sys                     import stdin, stdout, stderr
from textwrap                import dedent
from typing                  import NoReturn, Tuple, Any, List, Optional as Nullable, Dict, Callable, ClassVar

try:
	from colorama import Fore as Foreground
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'colorama' not installed. Either install pyTooling with extra dependencies 'pyTooling[terminal]' or install 'colorama' directly.") from ex

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, mixin
from pyTooling.Exceptions  import PlatformNotSupportedException, ExceptionBase
from pyTooling.Common      import lastItem
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
	PYTHON_VERSION_CHECK_FAILED_EXIT_CODE: ClassVar[int] = 254   #: Return code, if version check was not successful.
	FATAL_EXIT_CODE: ClassVar[int] =                       255   #: Return code for fatal exits.
	ISSUE_TRACKER_URL: ClassVar[str] =                     None  #: URL to the issue tracker for reporting bugs.
	INDENT: ClassVar[str] =                                "  "  #: Indentation. Default: ``"  "`` (2 spaces)

	try:
		from colorama import Fore as Foreground
		Foreground = {
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
		Foreground = {
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
	def GetTerminalSize() -> Tuple[int, int]:
		"""
		Returns the terminal size as tuple (width, height) for Windows, macOS (Darwin), Linux, cygwin (Windows), MinGW32/64 (Windows).

		:returns: A tuple containing width and height of the terminal's size in characters.
		:raises PlatformNotSupportedException: When a platform is not yet supported.
		"""
		platform = Platform()
		if platform.IsNativeWindows:
			size = TerminalBaseApplication.__GetTerminalSizeOnWindows()
		elif (platform.IsNativeLinux or platform.IsNativeFreeBSD or platform.IsNativeMacOS or platform.IsMinGW32OnWindows or platform.IsMinGW64OnWindows
					or platform.IsUCRT64OnWindows or platform.IsCygwin32OnWindows or platform.IsClang64OnWindows):
			size = TerminalBaseApplication.__GetTerminalSizeOnLinux()
		else:  # pragma: no cover
			raise PlatformNotSupportedException(f"Platform '{platform}' not yet supported.")

		if size is None:   # pragma: no cover
			size = (80, 25)  # default size

		return size

	@staticmethod
	def __GetTerminalSizeOnWindows() -> Nullable[Tuple[int, int]]:
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
	# def __GetTerminalSizeWithTPut() -> Tuple[int, int]:
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
	def __GetTerminalSizeOfFileDescriptor(fd: int) -> Nullable[Tuple[int, int]]:  # Python 3.10: Use bitwise-or for union type: | None:
		"""
		Get window size of a file descriptor.

		Call `ioctl` with ``TIOCGWINSZ`` (GetWindowsSize) for the given file descriptor.

		:param fd: File descriptor
		:return:
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
	def __GetTerminalSizeOnLinux() -> Nullable[Tuple[int, int]]:  # Python 3.10: Use bitwise-or for union type: | None:
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
		:param end:     Use newline character. Default: ``\\n``.
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
		:param end:     Use newline character. Default: ``\\n``.
		:returns:       Number of written characters.
		"""
		return self._stderr.write(message + end)

	def FatalExit(self, returnCode: int = 0) -> NoReturn:
		"""
		Exit the terminal application by uninitializing color support and returning a fatal Exit code.

		:param returnCode:  Return code for application exit.
		"""
		self.Exit(self.FATAL_EXIT_CODE if returnCode == 0 else returnCode)

	def Exit(self, returnCode: int = 0) -> NoReturn:
		"""
		Exit the terminal application by uninitializing color support and returning an Exit code.

		:param returnCode: Return code for application exit.
		"""
		self.UninitializeColors()
		exit(returnCode)

	def CheckPythonVersion(self, version: Tuple[int, ...]) -> None:
		"""
		Check if the used Python interpreter fulfills the minimum version requirements.
		"""
		from sys import version_info as info

		if info < version:
			self.InitializeColors()

			self.WriteLineToStdErr(dedent(f"""\
				{{RED}}[ERROR]{{NOCOLOR}} Used Python interpreter ({info.major}.{info.minor}.{info.micro}-{info.releaselevel}) is to old.
				{{indent}}{{YELLOW}}Minimal required Python version is {version[0]}.{version[1]}.{version[2]}{{NOCOLOR}}\
				""").format(indent=self.INDENT, **self.Foreground))

			self.Exit(self.PYTHON_VERSION_CHECK_FAILED_EXIT_CODE)

	def PrintException(self, ex: Exception) -> NoReturn:
		"""
		Prints an exception of type :exc:`Exception` and its traceback.

		If the exception as a nested action, the cause is printed as well.

		If ``ISSUE_TRACKER_URL`` is configured, a URL to the issue tracker is added.
		"""
		from traceback import format_tb, walk_tb

		frame, sourceLine = lastItem(walk_tb(ex.__traceback__))
		filename = frame.f_code.co_filename
		funcName = frame.f_code.co_name

		message  = f"{{RED}}[FATAL] An unknown or unhandled exception reached the topmost exception handler!{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Exception type:{{NOCOLOR}}       {{DARK_RED}}{ex.__class__.__name__}{{NOCOLOR}}\n"
		message += f"{{indent}}{{YELLOW}}Exception message:{{NOCOLOR}}    {{RED}}{ex!s}{{NOCOLOR}}\n"

		if hasattr(ex, "__notes__") and len(ex.__notes__) > 0:
			note = next(iterator := iter(ex.__notes__))
			message += f"{{indent}}{{YELLOW}}Notes:{{NOCOLOR}}                {{DARK_CYAN}}{note}{{NOCOLOR}}\n"
			for note in iterator:
				message += f"{{indent}}                      {{DARK_CYAN}}{note}{{NOCOLOR}}\n"

		message += f"{{indent}}{{YELLOW}}Caused in:{{NOCOLOR}}            {funcName}(...) in file '{filename}' at line {sourceLine}\n"

		if (ex2 := ex.__cause__) is not None:
			message += f"{{indent2}}{{DARK_YELLOW}}Caused by ex. type:{{NOCOLOR}} {{DARK_RED}}{ex2.__class__.__name__}{{NOCOLOR}}\n"
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

	def PrintNotImplementedError(self, ex: NotImplementedError) -> NoReturn:
		"""Prints a not-implemented exception of type :exc:`NotImplementedError`."""
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
		Prints an exception of type :exc:`ExceptionBase` and its traceback.

		If the exception as a nested action, the cause is printed as well.

		If ``ISSUE_TRACKER_URL`` is configured, a URL to the issue tracker is added.
		"""
		from traceback import print_tb, walk_tb

		frame, sourceLine = lastItem(walk_tb(ex.__traceback__))
		filename = frame.f_code.co_filename
		funcName = frame.f_code.co_name

		self.WriteLineToStdErr(dedent(f"""\
			{{RED}}[FATAL] A known but unhandled exception reached the topmost exception handler!{{NOCOLOR}}
			{{indent}}{{YELLOW}}Exception type:{{NOCOLOR}}       {{DARK_RED}}{ex.__class__.__name__}{{NOCOLOR}}
			{{indent}}{{YELLOW}}Exception message:{{NOCOLOR}}    {{RED}}{ex!s}{{NOCOLOR}}
			{{indent}}{{YELLOW}}Caused in:{{NOCOLOR}}            {funcName}(...) in file '{filename}' at line {sourceLine}\
			""").format(indent=self.INDENT, **self.Foreground))

		if ex.__cause__ is not None:
			self.WriteLineToStdErr(dedent(f"""\
				{{indent2}}{{DARK_YELLOW}}Caused by ex. type:{{NOCOLOR}} {{DARK_RED}}{ex.__cause__.__class__.__name__}{{NOCOLOR}}
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			ex.add_note(f"Supported types for second operand: Severity")
			raise ex


@export
@unique
class Mode(Enum):
	TextToStdOut_ErrorsToStdErr = 0
	AllLinearToStdOut =           1
	DataToStdOut_OtherToStdErr =  2


@export
class Line(metaclass=ExtendedType, slots=True):
	"""
	Represents a single message line with a severity and indentation level.
	"""

	_LOG_MESSAGE_FORMAT__ = {
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
		:param appendLinebreak: Optional, append a line break at the end of the message.
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

		:param indent: Indentation level added to the current indentation level.
		"""
		self._indent = (newIndent := self._indent + indent)
		return newIndent

	@readonly
	def AppendLinebreak(self) -> bool:
		"""
		Read-only property to return if a linebreak is added after the line's message.

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

	_terminal: TerminalBaseApplication

	def __init__(self, terminal: Nullable[TerminalBaseApplication] = None) -> None:
		"""MixIn initializer."""
		self._terminal = terminal

		# FIXME: Alter methods if a terminal is present or set dummy methods

	@readonly
	def Terminal(self) -> TerminalBaseApplication:
		"""Return the local terminal instance."""
		return self._terminal

	def WriteLine(self, line: Line, condition: bool = True) -> bool:
		"""Write an entry to the local terminal."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteLine(line)
		return False

	# def _TryWriteLine(self, *args: Any, condition: bool = True, **kwargs: Any):
	# 	if (self._terminal is not None) and condition:
	# 		return self._terminal.TryWrite(*args, **kwargs)
	# 	return False

	def WriteFatal(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a fatal message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteFatal(*args, **kwargs)
		return False

	def WriteError(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write an error message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteError(*args, **kwargs)
		return False

	def WriteCritical(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a warning message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteCritical(*args, **kwargs)
		return False

	def WriteWarning(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a warning message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteWarning(*args, **kwargs)
		return False

	def WriteInfo(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write an info message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteInfo(*args, **kwargs)
		return False

	def WriteQuiet(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a message even in quiet mode if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteQuiet(*args, **kwargs)
		return False

	def WriteNormal(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a *normal* message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteNormal(*args, **kwargs)
		return False

	def WriteVerbose(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a verbose message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteVerbose(*args, **kwargs)
		return False

	def WriteDebug(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a debug message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteDebug(*args, **kwargs)
		return False

	def WriteDryRun(self, *args: Any, condition: bool = True, **kwargs: Any) -> bool:
		"""Write a dry-run message if ``condition`` is true."""
		if (self._terminal is not None) and condition:
			return self._terminal.WriteDryRun(*args, **kwargs)
		return False


@export
class TerminalApplication(TerminalBaseApplication):  #, ILineTerminal):
	"""
	A base-class for implementation of terminal applications emitting line-by-line messages.
	"""
	_LOG_MESSAGE_FORMAT__ = {
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

	_LOG_LEVEL_ROUTING__: Dict[Severity, Tuple[Callable[[str, str], int]]]  #: Message routing rules.
	_verbose:       bool
	_debug:         bool
	_silent:        bool
	_quiet:         bool
	_writeLevel:    Severity
	_writeToStdOut: bool

	_lines:         List[Line]
	_baseIndent:    int

	_errorCount:    int
	_criticalWarningCount: int
	_warningCount:  int

	HeadLine:       ClassVar[str]

	def __init__(self, mode: Mode = Mode.AllLinearToStdOut) -> None:
		"""
		Initializer of a line-based terminal interface.

		:param mode: Defines what output (normal, error, data) to write where. Default: a linear flow all to *STDOUT*.
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

		:param width: Number of characters for horizontal lines.

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

	def _PrintVersion(self, author: str, email: str, copyright: str, license: str, version: str) -> None:
		"""
		Helper method to print the version information.

		:param author:    Author of the application.
		:param email:     The author's email address.
		:param copyright: The copyright information.
		:param license:   The license.
		:param version:   The application's version.

		.. admonition:: Example usage

		   .. code-block:: Python

		      def _PrintVersion(self):
		        from MyModule import __author__, __email__, __copyright__, __license__, __version__

		        super()._PrintVersion(__author__, __email__, __copyright__, __license__, __version__)
		"""
		self.WriteNormal(f"Author:    {author} ({email})")
		self.WriteNormal(f"Copyright: {copyright}")
		self.WriteNormal(f"License:   {license}")
		self.WriteNormal(f"Version:   {version}")

	def Configure(
		self,
		*,
		verbose: bool = False,
		debug:   bool = False,
		silent:  bool = False,
		quiet:   bool = False,
		writeToStdOut: bool = True
	) -> None:
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
		"""Returns true, if verbose messages are enabled."""
		return self._verbose

	@readonly
	def Debug(self) -> bool:
		"""Returns true, if debug messages are enabled."""
		return self._debug

	@readonly
	def Silent(self) -> bool:
		"""Returns true, if silent mode is enabled."""
		return self._silent

	@readonly
	def Quiet(self) -> bool:
		"""Returns true, if quiet mode is enabled."""
		return self._quiet

	@property
	def LogLevel(self) -> Severity:
		"""Return the current minimal severity level for writing."""
		return self._writeLevel

	@LogLevel.setter
	def LogLevel(self, value: Severity) -> None:
		"""Set the minimal severity level for writing."""
		self._writeLevel = value

	@property
	def BaseIndent(self) -> int:
		return self._baseIndent

	@BaseIndent.setter
	def BaseIndent(self, value: int) -> None:
		self._baseIndent = value

	@readonly
	def WarningCount(self) -> int:
		"""
		Read-only property to access the number of counted warnings.

		:return: Number of warnings.
		"""
		return self._warningCount

	@readonly
	def CriticalWarningCount(self) -> int:
		"""
		Read-only property to access the number of counted critical warnings.

		:return: Number of critical warnings.
		"""
		return self._criticalWarningCount

	@readonly
	def ErrorCount(self) -> int:
		"""
		Read-only property to access the number of counted errors.

		:return: Number of errors.
		"""
		return self._errorCount

	@readonly
	def Lines(self) -> List[Line]:
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

		:param includeErrors: Include critical warning counts.
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

		:param includeCriticalWarnings: Include critical warning counts.
		:param includeErrors:           Include error counts.
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
		return line.Severity >= self._writeLevel

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
