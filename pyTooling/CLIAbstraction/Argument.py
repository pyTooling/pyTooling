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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
This module implements command line arguments without prefix character(s).


"""
from abc     import abstractmethod
from pathlib import Path
from sys     import version_info           # needed for versions before Python 3.11
from typing  import ClassVar, List, Union, Iterable, TypeVar, Generic, Any, Optional as Nullable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from Common              import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


__all__ = ["ValueT"]


ValueT = TypeVar("ValueT")   #: The type of value in a valued argument.


@export
class CommandLineArgument:
	"""
	Base-class for all *Argument* classes.

	An argument instance can be converted via ``AsArgument`` to a single string value or a sequence of string values
	(tuple) usable e.g. with :class:`subprocess.Popen`. Each argument class implements at least one ``pattern`` parameter
	to specify how argument are formatted.

	There are multiple derived formats supporting:

	* commands |br|
	  |rarr| :mod:`~pyTooling.CLIAbstraction.Command`
	* simple names (flags) |br|
	  |rarr| :mod:`~pyTooling.CLIAbstraction.Flag`, :mod:`~pyTooling.CLIAbstraction.BooleanFlag`
	* simple values (vlaued flags) |br|
	  |rarr| :class:`~pyTooling.CLIAbstraction.Argument.StringArgument`, :class:`~pyTooling.CLIAbstraction.Argument.PathArgument`
	* names and values |br|
	  |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlag`, :mod:`~pyTooling.CLIAbstraction.OptionalValuedFlag`
	* key-value pairs |br|
	  |rarr| :mod:`~pyTooling.CLIAbstraction.NamedKeyValuePair`
	"""

	_pattern: ClassVar[str]

	def __init_subclass__(cls, *args: Any, pattern: Nullable[str] = None, **kwargs: Any):
		"""This method is called when a class is derived.

		:param args: Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs: Any keyword argument.
		"""
		super().__init_subclass__(*args, **kwargs)
		cls._pattern = pattern

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is CommandLineArgument:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")

		# TODO: not sure why parameters meant for __init__ do reach this level and distract __new__ from it's work
		return super().__new__(cls)

	# TODO: Add property to read pattern

	@abstractmethod
	def AsArgument(self) -> Union[str, Iterable[str]]:  # type: ignore[empty-body]
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name and value.

		:return:                     Formatted argument.
		:raises NotImplementedError: This is an abstract method and must be overwritten by a subclass.
		"""
		raise NotImplementedError(f"Method 'AsArgument' is an abstract method and must be implemented by a subclass.")

	@abstractmethod
	def __str__(self) -> str:  # type: ignore[empty-body]
		"""
		Return a string representation of this argument instance.

		:return:                     Argument formatted and enclosed in double quotes.
		:raises NotImplementedError: This is an abstract method and must be overwritten by a subclass.
		"""
		raise NotImplementedError(f"Method '__str__' is an abstract method and must be implemented by a subclass.")

	@abstractmethod
	def __repr__(self) -> str:  # type: ignore[empty-body]
		"""
		Return a string representation of this argument instance.

		.. note:: By default, this method is identical to :meth:`__str__`.

		:return:                     Argument formatted and enclosed in double quotes.
		:raises NotImplementedError: This is an abstract method and must be overwritten by a subclass.
		"""
		raise NotImplementedError(f"Method '__repr__' is an abstract method and must be implemented by a subclass.")


@export
class ExecutableArgument(CommandLineArgument):
	"""
	Represents the executable.
	"""

	_executable: Path

	def __init__(self, executable: Path) -> None:
		"""
		Initializes a ExecutableArgument instance.

		:param executable: Path to the executable.
		:raises TypeError: If parameter 'executable' is not of type :class:`~pathlib.Path`.
		"""
		if not isinstance(executable, Path):
			ex = TypeError("Parameter 'executable' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(executable)}'.")
			raise ex

		self._executable = executable

	@property
	def Executable(self) -> Path:
		"""
		Get the internal path to the wrapped executable.

		:return: Internal path to the executable.
		"""
		return self._executable

	@Executable.setter
	def Executable(self, value):
		"""
		Set the internal path to the wrapped executable.

		:param value:      Value to path to the executable.
		:raises TypeError: If value is not of type :class:`~pathlib.Path`.
		"""
		if not isinstance(value, Path):
			ex = TypeError("Parameter 'value' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._executable = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal path to the wrapped executable.

		:return: Formatted argument.
		"""
		return f"{self._executable}"

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self._executable}\""

	__repr__ = __str__


@export
class DelimiterArgument(CommandLineArgument, pattern="--"):
	"""
	Represents a delimiter symbol like ``--``.
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "--", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument. Default: ``"--"``.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern.

		:return: Formatted argument.
		"""
		return self._pattern

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self._pattern}\""

	__repr__ = __str__


@export
class NamedArgument(CommandLineArgument, pattern="{0}"):
	"""
	Base-class for all command line arguments with a name.
	"""

	_name: ClassVar[str]

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Name of the argument.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		cls._name = name

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is NamedArgument:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	@readonly
	def Name(self) -> str:
		"""
		Get the internal name.

		:return: Internal name.
		"""
		return self._name

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name.

		:return:            Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		return self._pattern.format(self._name)

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self.AsArgument()}\""

	__repr__ = __str__


@export
class ValuedArgument(CommandLineArgument, Generic[ValueT], pattern="{0}"):
	"""
	Base-class for all command line arguments with a value.
	"""

	_value: ValueT

	def __init_subclass__(cls, *args: Any, pattern: str = "{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __init__(self, value: ValueT) -> None:
		"""
		Initializes a ValuedArgument instance.

		:param value:      Value to be stored internally.
		:raises TypeError: If parameter 'value' is None.
		"""
		if value is None:
			raise ValueError("Parameter 'value' is None.")

		self._value = value

	@property
	def Value(self) -> ValueT:
		"""
		Get the internal value.

		:return: Internal value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: ValueT) -> None:
		"""
		Set the internal value.

		:param value:       Value to set.
		:raises ValueError: If value to set is None.
		"""
		if value is None:
			raise ValueError(f"Value to set is None.")

		self._value = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal value.

		:return: Formatted argument.
		"""
		return self._pattern.format(self._value)

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self.AsArgument()}\""

	__repr__ = __str__


class NamedAndValuedArgument(NamedArgument, ValuedArgument, Generic[ValueT], pattern="{0}={1}"):
	"""
	Base-class for all command line arguments with a name and a value.
	"""

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "{0}={1}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param name:    Name of the argument.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		del kwargs["name"]
		del kwargs["pattern"]
		ValuedArgument.__init_subclass__(*args, **kwargs)

	def __init__(self, value: ValueT) -> None:
		ValuedArgument.__init__(self, value)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal name and value.

		:return:            Formatted argument.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		return self._pattern.format(self._name, self._value)

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self.AsArgument()}\""

	__repr__ = __str__


class NamedTupledArgument(NamedArgument, ValuedArgument, Generic[ValueT], pattern="{0}"):
	"""
	Class and base-class for all TupleFlag classes, which represents an argument with separate value.

	A tuple argument is a command line argument followed by a separate value. Name and value are passed as two arguments
	to the executable.

	**Example: **

	* `width 100``
	"""

	_valuePattern: ClassVar[str]

	def __init_subclass__(cls, *args: Any, name: Nullable[str] = None, pattern: str = "{0}", valuePattern: str = "{0}", **kwargs: Any):
		kwargs["name"] = name
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)
		cls._valuePattern = valuePattern

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is NamedTupledArgument:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, value: ValueT) -> None:
		ValuedArgument.__init__(self, value)

	# TODO: Add property to read value pattern

	# @property
	# def ValuePattern(self) -> str:
	# 	if self._valuePattern is None:
	# 		raise ValueError(f"")  # XXX: add message
	#
	# 	return self._valuePattern

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a sequence of string representations with proper escaping using the matching
		pattern based on the internal name and value.

		:return:            Formatted argument as tuple of strings.
		:raises ValueError: If internal name is None.
		"""
		if self._name is None:
			raise ValueError(f"Internal value '_name' is None.")

		return (
			self._pattern.format(self._name),
			self._valuePattern.format(self._value)
		)

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Space separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return " ".join([f"\"{item}\"" for item in self.AsArgument()])

	def __repr__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Comma separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return ", ".join([f"\"{item}\"" for item in self.AsArgument()])


@export
class StringArgument(ValuedArgument, pattern="{0}"):
	"""
	Represents a simple string argument.

	A list of strings is available as :class:`~pyTooling.CLIAbstraction.Argument.StringListArgument`.
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "{0}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)


@export
class StringListArgument(ValuedArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.CLIAbstraction.Argument.StringArgument`)."""

	def __init__(self, values: Iterable[str]) -> None:
		"""
		Initializes a StringListArgument instance.

		:param values:     An iterable of str instances.
		:raises TypeError: If iterable parameter 'values' contains elements not of type :class:`str`.
		"""
		self._values = []
		for value in values:
			if not isinstance(value, str):
				ex = TypeError(f"Parameter 'values' contains elements which are not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(values)}'.")
				raise ex

			self._values.append(value)

	@property
	def Value(self) -> List[str]:
		"""
		Get the internal list of str objects.

		:return: Reference to the internal list of str objects.
		"""
		return self._values

	@Value.setter
	def Value(self, value: Iterable[str]):
		"""
		Overwrite all elements in the internal list of str objects.

		.. note:: The list object is not replaced, but cleared and then reused by adding the given elements in the iterable.

		:param value:      List of str objects to set.
		:raises TypeError: If value contains elements, which are not of type :class:`str`.
		"""
		self._values.clear()
		for value in value:
			if not isinstance(value, str):
				ex = TypeError(f"Value contains elements which are not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex
			self._values.append(value)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal value.

		:return: Sequence of formatted arguments.
		"""
		return [f"{value}" for value in self._values]

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Space separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return " ".join([f"\"{value}\"" for value in self.AsArgument()])

	def __repr__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Comma separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return ", ".join([f"\"{value}\"" for value in self.AsArgument()])


# TODO: Add option to class if path should be checked for existence
@export
class PathArgument(CommandLineArgument):
	"""
	Represents a single path argument.

	A list of paths is available as :class:`~pyTooling.CLIAbstraction.Argument.PathListArgument`.
	"""
	# The output format can be forced to the POSIX format with :py:data:`_PosixFormat`.
	_path: Path

	def __init__(self, path: Path) -> None:
		"""
		Initializes a PathArgument instance.

		:param path:       Path to a filesystem object.
		:raises TypeError: If parameter 'path' is not of type :class:`~pathlib.Path`.
		"""
		if not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex
		self._path = path

	@property
	def Value(self) -> Path:
		"""
		Get the internal path object.

		:return: Internal path object.
		"""
		return self._path

	@Value.setter
	def Value(self, value: Path):
		"""
		Set the internal path object.

		:param value:      Value to set.
		:raises TypeError: If value is not of type :class:`~pathlib.Path`.
		"""
		if not isinstance(value, Path):
			ex = TypeError("Value is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._path = value

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal value.

		:return: Formatted argument.
		"""
		return f"{self._path}"

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Argument formatted and enclosed in double quotes.
		"""
		return f"\"{self._path}\""

	__repr__ = __str__


@export
class PathListArgument(CommandLineArgument):
	"""
	Represents a list of path arguments  (:class:`~pyTooling.CLIAbstraction.Argument.PathArgument`).
	"""
	# The output format can be forced to the POSIX format with :py:data:`_PosixFormat`.
	_paths: List[Path]

	def __init__(self, paths: Iterable[Path]) -> None:
		"""
		Initializes a PathListArgument instance.

		:param paths:      An iterable os Path instances.
		:raises TypeError: If iterable parameter 'paths' contains elements not of type :class:`~pathlib.Path`.
		"""
		self._paths = []
		for path in paths:
			if not isinstance(path, Path):
				ex = TypeError(f"Parameter 'paths' contains elements which are not of type 'Path'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
				raise ex

			self._paths.append(path)

	@property
	def Value(self) -> List[Path]:
		"""
		Get the internal list of path objects.

		:return: Reference to the internal list of path objects.
		"""
		return self._paths

	@Value.setter
	def Value(self, value: Iterable[Path]):
		"""
		Overwrite all elements in the internal list of path objects.

		.. note:: The list object is not replaced, but cleared and then reused by adding the given elements in the iterable.

		:param value:      List of path objects to set.
		:raises TypeError: If value contains elements, which are not of type :class:`~pathlib.Path`.
		"""
		self._paths.clear()
		for path in value:
			if not isinstance(path, Path):
				ex = TypeError(f"Value contains elements which are not of type 'Path'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
				raise ex
			self._paths.append(path)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		"""
		Convert this argument instance to a string representation with proper escaping using the matching pattern based on
		the internal value.

		:return: Sequence of formatted arguments.
		"""
		return [f"{path}" for path in self._paths]

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Space separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return " ".join([f"\"{value}\"" for value in self.AsArgument()])

	def __repr__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Comma separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return ", ".join([f"\"{value}\"" for value in self.AsArgument()])
