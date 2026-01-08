# ==================================================================================================================== #
#             _____           _ _               ____ _     ___    _    _         _                  _   _              #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|  / \  | |__  ___| |_ _ __ __ _  ___| |_(_) ___  _ __   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |  / _ \ | '_ \/ __| __| '__/ _` |/ __| __| |/ _ \| '_ \  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | | / ___ \| |_) \__ \ |_| | | (_| | (__| |_| | (_) | | | | #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___/_/   \_\_.__/|___/\__|_|  \__,_|\___|\__|_|\___/|_| |_| #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2014-2016 Technische Universität Dresden - Germany, Chair of VLSI-Design, Diagnostics and Architecture     #
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
"""Basic abstraction layer for executables."""

# __keywords__ =  ["abstract", "executable", "cli", "cli arguments"]

from os         import environ as os_environ
from pathlib    import Path
from platform   import system
from shutil     import which as shutil_which
from subprocess import Popen as Subprocess_Popen, PIPE as Subprocess_Pipe, STDOUT as Subprocess_StdOut
from typing     import Dict, Optional as Nullable, ClassVar, Type, List, Tuple, Iterator, Generator, Any, Mapping, Iterable


try:
	from pyTooling.Decorators                import export, readonly
	from pyTooling.MetaClasses               import ExtendedType
	from pyTooling.Exceptions                import ToolingException, PlatformNotSupportedException
	from pyTooling.Common                    import getFullyQualifiedName
	from pyTooling.Attributes                import Attribute
	from pyTooling.CLIAbstraction.Argument   import CommandLineArgument, ExecutableArgument
	from pyTooling.CLIAbstraction.Argument   import NamedAndValuedArgument, ValuedArgument, PathArgument, PathListArgument, NamedTupledArgument
	from pyTooling.CLIAbstraction.ValuedFlag import ValuedFlag
	from pyTooling.Platform                  import Platform
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.CLIAbstraction] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                import export, readonly
		from MetaClasses               import ExtendedType
		from Exceptions                import ToolingException, PlatformNotSupportedException
		from Common                    import getFullyQualifiedName
		from Attributes                import Attribute
		from CLIAbstraction.Argument   import CommandLineArgument, ExecutableArgument
		from CLIAbstraction.Argument   import NamedAndValuedArgument, ValuedArgument, PathArgument, PathListArgument, NamedTupledArgument
		from CLIAbstraction.ValuedFlag import ValuedFlag
		from Platform                  import Platform
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.CLIAbstraction] Could not import directly!")
		raise ex


@export
class CLIAbstractionException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.CLIAbstraction`."""


@export
class DryRunException(CLIAbstractionException):
	"""This exception is raised if an executable is launched while in dry-run mode."""


@export
class CLIArgument(Attribute):
	"""An attribute to annotate nested classes as an CLI argument."""


@export
class Environment(metaclass=ExtendedType, slots=True):
	"""
	A class describing the environment of an executable.

	.. topic:: Content of the environment

	   * Environment variables
	"""
	_variables: Dict[str, str]  #: Dictionary of active environment variables.

	# TODO: derive environment from existing environment object.
	def __init__(
		self, *,
		environment:  Nullable["Environment"] = None,
		newVariables: Nullable[Mapping[str, str]] = None,
		addVariables: Nullable[Mapping[str, str]] = None,
		delVariables: Nullable[Iterable[str]] = None
	) -> None:
		"""
		Initializes an environment class managing.

		.. topic:: Algorithm

			 1. Create a new dictionary of environment variables (name-value pairs) from either:

			    * an existing :class:`Environment` instance.
			    * current executable's environment by reading environment variables from :func:`os.environ`.
			    * a dictionary of name-value pairs.

			 2. Remove variables from environment.
			 3. Add new or update existing variables.

		:param environment:  Optional existing Environment instance to derive a new environment.
		:param newVariables: Optional dictionary of new environment variables. |br|
		                     If ``None``, read current environment variables from :func:`os.environ`.
		:param addVariables: Optional dictionary of variables to be added or modified in the environment.
		:param delVariables: Optional list of variable names to be removed from the environment.
		"""
		if environment is not None:
			newVariables = environment._variables
		elif newVariables is None:
			newVariables = os_environ

		self._variables = {name: value for name, value in newVariables.items()}

		if delVariables is not None:
			for variableName in delVariables:
				del self._variables[variableName]

		if addVariables is not None:
			self._variables.update(addVariables)

	def __len__(self) -> len:
		"""
		Returns the number of set environment variables.

		:returns: Number of environment variables.
		"""
		return len(self._variables)

	def __contains__(self, name: str) -> bool:
		"""
		Checks if the variable is set in the environment.

		:param key: The variable name to check.
		:returns:   ``True``, if the variable is set in the environment.
		"""
		return name in self._variables

	def __getitem__(self, name: str) -> str:
		"""
		Access an environment variable in the environment by name.

		:param name:      Name of the environment variable.
		:returns:         The environment variable's value.
		:raises KeyError: If Variable name is not set in the environment.
		"""
		return self._variables[name]

	def __setitem__(self, name: str, value: str) -> None:
		"""
		Add or set an environment variable in the environment by name.

		:param name:  Name of the environment variable.
		:param value: Value of the environment variable to be set.
		"""
		self._variables[name] = value

	def __delitem__(self, name: str) -> None:
		"""
		Remove an environment variable from the environment by name.

		:param name:      The name of the environment variable to remove.
		:raises KeyError: If name doesn't exist in the environment.
		"""
		del self._variables[name]


@export
class Program(metaclass=ExtendedType, slots=True):
	"""
	Represent a simple command line interface (CLI) executable (program or script).

	CLI options are collected in a ``__cliOptions__`` dictionary.
	"""

	_platform:         str                                                            #: Current platform the executable runs on (Linux, Windows, ...)
	_executableNames:  ClassVar[Dict[str, str]]                                       #: Dictionary of platform specific executable names.
	_executablePath:   Path                                                           #: The path to the executable (binary, script, ...).
	_dryRun:           bool                                                           #: True, if program shall run in *dry-run mode*.
	__cliOptions__:    ClassVar[Dict[Type[CommandLineArgument], int]]                 #: List of all possible CLI options.
	__cliParameters__: Dict[Type[CommandLineArgument], Nullable[CommandLineArgument]] #: List of all CLI parameters (used CLI options).

	def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
		"""
		Whenever a subclass is derived from :class:``Program``, all nested classes declared within ``Program`` and which are
		marked with attribute ``CLIArgument`` are collected and then listed in the ``__cliOptions__`` dictionary.

		:param args:   Any positional arguments.
		:param kwargs: Any keyword arguments.
		"""
		super().__init_subclass__(*args, **kwargs)

		# register all available CLI options (nested classes marked with attribute 'CLIArgument')
		cls.__cliOptions__ = {option: order for order, option in enumerate(CLIArgument.GetClasses(scope=cls))}

	def __init__(
		self,
		executablePath: Nullable[Path] = None,
		binaryDirectoryPath: Nullable[Path] = None,
		dryRun: bool = False
	) -> None:
		"""
		Initializes a program instance.

		.. todo:: Document algorithm

		:param executablePath:      Path to the executable.
		:param binaryDirectoryPath: Path to the executable's directory.
		:param dryRun:              True, when the program should run in dryrun mode.
		"""
		self._platform =    system()
		self._dryRun =      dryRun

		if executablePath is not None:
			if isinstance(executablePath, Path):
				if not executablePath.exists():
					if dryRun:
						self.LogDryRun(f"File check for '{executablePath}' failed. [SKIPPING]")
					else:
						raise CLIAbstractionException(f"Program '{executablePath}' not found.") from FileNotFoundError(executablePath)
			else:
				ex = TypeError(f"Parameter 'executablePath' is not of type 'Path'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(executablePath)}'.")
				raise ex
		elif binaryDirectoryPath is not None:
			if isinstance(binaryDirectoryPath, Path):
				if not binaryDirectoryPath.exists():
					if dryRun:
						self.LogDryRun(f"Directory check for '{binaryDirectoryPath}' failed. [SKIPPING]")
					else:
						raise CLIAbstractionException(f"Binary directory '{binaryDirectoryPath}' not found.") from FileNotFoundError(binaryDirectoryPath)

				try:
					executablePath = binaryDirectoryPath / self.__class__._executableNames[self._platform]
				except KeyError:
					raise CLIAbstractionException(f"Program is not supported on platform '{self._platform}'.") from PlatformNotSupportedException(self._platform)

				if not executablePath.exists():
					if dryRun:
						self.LogDryRun(f"File check for '{executablePath}' failed. [SKIPPING]")
					else:
						raise CLIAbstractionException(f"Program '{executablePath}' not found.") from FileNotFoundError(executablePath)
			else:
				ex = TypeError(f"Parameter 'binaryDirectoryPath' is not of type 'Path'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(binaryDirectoryPath)}'.")
				raise ex
		else:
			try:
				executablePath = Path(self._executableNames[self._platform])
			except KeyError:
				raise CLIAbstractionException(f"Program is not supported on platform '{self._platform}'.") from PlatformNotSupportedException(self._platform)

			resolvedExecutable = shutil_which(str(executablePath))
			if dryRun:
				if resolvedExecutable is None:
					pass
					# XXX: log executable not found in PATH
					# self.LogDryRun(f"Which '{executablePath}' failed. [SKIPPING]")
				else:
					fullExecutablePath = Path(resolvedExecutable)
					if not fullExecutablePath.exists():
						pass
						# XXX: log executable not found
						# self.LogDryRun(f"File check for '{fullExecutablePath}' failed. [SKIPPING]")
			else:
				if resolvedExecutable is None:
					raise CLIAbstractionException(f"Program could not be found in PATH.") from FileNotFoundError(executablePath)

				fullExecutablePath = Path(resolvedExecutable)
				if not fullExecutablePath.exists():
					raise CLIAbstractionException(f"Program '{fullExecutablePath}' not found.") from FileNotFoundError(fullExecutablePath)

			# TODO: log found executable in PATH
			# TODO: check if found executable has execute permissions
			# raise ValueError(f"Neither parameter 'executablePath' nor 'binaryDirectoryPath' was set.")

		self._executablePath = executablePath
		self.__cliParameters__ = {}

	@staticmethod
	def _NeedsParameterInitialization(key) -> bool:
		return issubclass(key, (ValuedFlag, ValuedArgument, NamedAndValuedArgument, NamedTupledArgument, PathArgument, PathListArgument))

	def __getitem__(self, key: Type[CommandLineArgument]) -> CommandLineArgument:
		"""Access to a CLI parameter by CLI option (key must be of type :class:`CommandLineArgument`), which is already used."""
		if not issubclass(key, CommandLineArgument):
			ex = TypeError(f"Key '{key}' is not a subclass of 'CommandLineArgument'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex

		# TODO: is nested check
		return self.__cliParameters__[key]

	def __setitem__(self, key: Type[CommandLineArgument], value: CommandLineArgument) -> None:
		if not issubclass(key, CommandLineArgument):
			ex = TypeError(f"Key '{key}' is not a subclass of 'CommandLineArgument'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(key)}'.")
			raise ex
		elif key not in self.__cliOptions__:
			raise KeyError(f"Option '{key}' is not allowed on executable '{self.__class__.__name__}'")
		elif key in self.__cliParameters__:
			raise KeyError(f"Option '{key}' is already set to a value.")

		if self._NeedsParameterInitialization(key):
			self.__cliParameters__[key] = key(value)
		else:
			self.__cliParameters__[key] = key()

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the program's path.

		:returns: The program's path.
		"""
		return self._executablePath

	def ToArgumentList(self) -> List[str]:
		"""
		Convert a program and used CLI options to a list of CLI argument strings in correct order and with escaping.

		:returns: List of CLI arguments
		"""
		result: List[str] = []

		result.append(str(self._executablePath))

		def predicate(item: Tuple[Type[CommandLineArgument], int]) -> int:
			return self.__cliOptions__[item[0]]

		for key, value in sorted(self.__cliParameters__.items(), key=predicate):
			param = value.AsArgument()
			if isinstance(param, str):
				result.append(param)
			elif isinstance(param, (Tuple, List)):
				result += param
			else:
				raise TypeError(f"")  # XXX: needs error message

		return result

	def __repr__(self) -> str:
		"""
		Returns the string representation as coma-separated list of double-quoted CLI argument strings within square brackets.

		Example: :pycode:`["arg1", "arg2"]`

		:returns: Coma-separated list of CLI arguments with double-quotes.
		"""
		return "[" + ", ".join([f"\"{item}\"" for item in self.ToArgumentList()]) + "]"  # WORKAROUND: Python <3.12
		# return f"[{", ".join([f"\"{item}\"" for item in self.ToArgumentList()])}]"

	def __str__(self) -> str:
		"""
		Returns the string representation as space-separated list of double-quoted CLI argument strings.

		Example: :pycode:`"arg1" "arg2"`

		:returns: Space-separated list of CLI arguments with double-quotes.
		"""
		return " ".join([f"\"{item}\"" for item in self.ToArgumentList()])


@export
class Executable(Program):  # (ILogable):
	"""Represent a CLI executable derived from :class:`Program`, that adds an abstraction of :class:`subprocess.Popen`."""

	_BOUNDARY:         ClassVar[str] = "====== BOUNDARY pyTooling.CLIAbstraction BOUNDARY ======"

	_workingDirectory: Nullable[Path]              #: Path to the working directory
	_environment:      Nullable[Environment]       #: Environment to use when executing.
	_process:          Nullable[Subprocess_Popen]  #: Reference to the running process.
	_iterator:         Nullable[Iterator]          #: Iterator for reading STDOUT.

	def __init__(
		self,
		executablePath:      Nullable[Path] = None,
		binaryDirectoryPath: Nullable[Path] = None,
		workingDirectory:    Nullable[Path] = None,
		environment:         Nullable[Environment] = None,
		dryRun:              bool = False
	):
		"""
		Initializes an executable instance.

		:param executablePath:      Path to the executable.
		:param binaryDirectoryPath: Path to the executable's directory.
		:param workingDirectory:    Path to the working directory.
		:param environment:         Optional environment that should be setup when launching the executable.
		:param dryRun:              True, when the program should run in dryrun mode.
		"""
		super().__init__(executablePath, binaryDirectoryPath, dryRun)

		self._workingDirectory = None
		self._environment = environment
		self._process = None
		self._iterator = None

	def StartProcess(self, environment: Nullable[Environment] = None) -> None:
		"""
		Start the executable as a child-process.

		:param environment:              Optional environment that should be setup when launching the executable. |br|
		                                 If ``None``, the :attr:`_environment` is used.
		:raises CLIAbstractionException: When an :exc:`OSError` occurs while launching the child-process.
		"""
		if self._dryRun:
			self.LogDryRun(f"Start process: {self!r}")
			return

		if environment is not None:
			envVariables = environment._variables
		elif self._environment is not None:
			envVariables = self._environment._variables
		else:
			envVariables = None

		# FIXME: verbose log start process
		# FIXME: debug log - parameter list
		try:
			self._process = Subprocess_Popen(
				self.ToArgumentList(),
				stdin=Subprocess_Pipe,
				stdout=Subprocess_Pipe,
				stderr=Subprocess_StdOut,
				cwd=self._workingDirectory,
				env=envVariables,
				universal_newlines=True,
				bufsize=256
			)

		except OSError as ex:
			raise CLIAbstractionException(f"Error while launching a process for '{self._executablePath}'.") from ex

	def Send(self, line: str, end: str = "\n") -> None:
		"""
		Send a string to STDIN of the running child-process.

		:param line:                     Line to send.
		:param end:                      Line end character.
		:raises CLIAbstractionException: When any error occurs while sending data to the child-process.
		"""
		try:
			self._process.stdin.write(line + end)
			self._process.stdin.flush()
		except Exception as ex:
			raise CLIAbstractionException(f"") from ex     # XXX: need error message

	# This is TCL specific ...
	# def SendBoundary(self):
	# 	self.Send("puts \"{0}\"".format(self._pyIPCMI_BOUNDARY))

	def GetLineReader(self) -> Generator[str, None, None]:
		"""
		Return a line-reader for STDOUT.

		:returns:                        A generator object to read from STDOUT line-by-line.
		:raises DryRunException:         In case dryrun mode is active.
		:raises CLIAbstractionException: When any error occurs while reading outputs from the child-process.
		"""
		if self._dryRun:
			raise DryRunException()  # XXX: needs a message

		try:
			for line in iter(self._process.stdout.readline, ""):     # FIXME: can it be improved?
				yield line[:-1]
		except Exception as ex:
			raise CLIAbstractionException() from ex     # XXX: need error message
		# finally:
			# self._process.terminate()

	def Terminate(self) -> None:
		"""
		Terminate the child-process.
		"""
		self._process.terminate()

	@readonly
	def ExitCode(self) -> int:
		"""
		Read-only property returning the child-process' exit code.

		:returns:                        Child-process' exit code.
		:raises CLIAbstractionException: When the child-process was not started.
		"""
		if self._process is None:
			raise CLIAbstractionException(f"Process not yet started, thus no exit code.")

		# FIXME: check if process is still running

		return self._process.returncode

	# This is TCL specific
	# def ReadUntilBoundary(self, indent=0):
	# 	__indent = "  " * indent
	# 	if self._iterator is None:
	# 		self._iterator = iter(self.GetReader())
	#
	# 	for line in self._iterator:
	# 		print(__indent + line)
	# 		if self._pyIPCMI_BOUNDARY in line:
	# 			break
	# 	self.LogDebug("Quartus II is ready")


@export
class OutputFilteredExecutable(Executable):
	"""Represent a CLI executable derived from :class:`Executable`, whose outputs are filtered."""
	_hasOutput:   bool
	_hasWarnings: bool
	_hasErrors:   bool
	_hasFatals:   bool

	def __init__(self, platform: Platform, dryrun: bool, executablePath: Path) -> None: #, environment=None, logger=None) -> None:
		super().__init__(platform, dryrun, executablePath)  #, environment=environment, logger=logger)

		self._hasOutput =   False
		self._hasWarnings = False
		self._hasErrors =   False
		self._hasFatals =   False

	@readonly
	def HasWarnings(self) -> bool:
		# TODO: update doc-string
		"""True if warnings were found while processing the output stream."""
		return self._hasWarnings

	@readonly
	def HasErrors(self) -> bool:
		# TODO: update doc-string
		"""True if errors were found while processing the output stream."""
		return self._hasErrors

	@readonly
	def HasFatals(self) -> bool:
		# TODO: update doc-string
		"""True if fatals were found while processing the output stream."""
		return self._hasErrors
