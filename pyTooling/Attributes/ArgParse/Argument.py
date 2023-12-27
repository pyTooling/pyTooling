from pathlib import Path
from typing import Type

from pyTooling.Decorators import export
from . import CommandLineArgument


@export
class DelimiterArgument(CommandLineArgument):
	"""
	Represents a delimiter symbol like ``--``.
	"""


@export
class NamedArgument(CommandLineArgument):
	"""
	Base-class for all command line arguments with a name.
	"""


@export
class ValuedArgument(CommandLineArgument):
	"""
	Base-class for all command line arguments with a value.
	"""


class NamedAndValuedArgument(NamedArgument, ValuedArgument):
	"""
	Base-class for all command line arguments with a name and a value.
	"""


class NamedTupledArgument(NamedArgument, ValuedArgument):
	"""
	Class and base-class for all TupleFlag classes, which represents an argument with separate value.

	A tuple argument is a command line argument followed by a separate value. Name and value are passed as two arguments
	to the executable.

	**Example: **

	* `width 100``
	"""


@export
class PositionalArgument(ValuedArgument):
	"""
	Represents a simple string argument containing any information encoded in a string.

	TODO

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, type: Type = str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		args = []
		kwargs = {
			"dest":    dest,
			"metavar": metaName,
			"type":    type,
			"help":    help
		}
		if optional:
			kwargs["nargs"] = "?"

		super().__init__(*args, **kwargs)


@export
class StringArgument(PositionalArgument):
	"""
	Represents a simple string argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, str, optional, help)


@export
class IntegerArgument(PositionalArgument):
	"""
	Represents an integer argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, int, optional, help)


@export
class FloatArgument(PositionalArgument):
	"""
	Represents a floating point number argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, float, optional, help)


# TODO: Add option to class if path should be checked for existence
@export
class PathArgument(PositionalArgument):
	"""
	Represents a single path argument.

	A list of paths is available as :class:`~pyTooling.Attribute.ArgParse.Argument.PathListArgument`.
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, Path, optional, help)


@export
class ListArgument(ValuedArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, type: Type = str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		args = []
		kwargs = {
			"dest":    dest,
			"metavar": metaName,
			"nargs":   "*" if optional else "+",
			"type":    type,
			"help":    help
		}
		super().__init__(*args, **kwargs)


@export
class StringListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, str, optional, help)


@export
class IntegerListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, int, optional, help)


@export
class FloatListArgument(ListArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, float, optional, help)


@export
class PathListArgument(ListArgument):
	"""
	Represents a list of path arguments  (:class:`~pyTooling.Attribute.ArgParse.Argument.PathArgument`).
	"""

	def __init__(self, dest: str, metaName: str, optional: bool = False, help: str = "") -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__(dest, metaName, Path, optional, help)
