from pyTooling.Decorators import export
from . import CommandLineArgument


@export
class DelimiterArgument(CommandLineArgument):  # , pattern="--"):
	"""
	Represents a delimiter symbol like ``--``.
	"""


@export
class NamedArgument(CommandLineArgument):  # , pattern="{0}"):
	"""
	Base-class for all command line arguments with a name.
	"""


@export
class ValuedArgument(CommandLineArgument):  # , pattern="{0}"):
	"""
	Base-class for all command line arguments with a value.
	"""


class NamedAndValuedArgument(NamedArgument, ValuedArgument):  # , pattern="{0}={1}"):
	"""
	Base-class for all command line arguments with a name and a value.
	"""


class NamedTupledArgument(NamedArgument, ValuedArgument):  # , pattern="{0}"):
	"""
	Class and base-class for all TupleFlag classes, which represents an argument with separate value.

	A tuple argument is a command line argument followed by a separate value. Name and value are passed as two arguments
	to the executable.

	**Example: **

	* `width 100``
	"""


@export
class StringArgument(ValuedArgument):  # , pattern="{0}"):
	"""
	Represents a simple string argument.

	A list of strings is available as :class:`~pyTooling.Attribute.ArgParse.Argument.StringListArgument`.
	"""

	def __init__(self, name: str, metaName: str, help: str = "", optional: bool = False) -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		args = []
		kwargs = {
			"metavar": metaName,
			"dest":    name,
			"type":    str,
			"nargs":   "?" if optional else "1",
			"help":    help
		}

		super().__init__(args, kwargs)


@export
class StringListArgument(ValuedArgument):
	"""
	Represents a list of string argument (:class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`)."""


# TODO: Add option to class if path should be checked for existence
@export
class PathArgument(CommandLineArgument):
	"""
	Represents a single path argument.

	A list of paths is available as :class:`~pyTooling.Attribute.ArgParse.Argument.PathListArgument`.
	"""


@export
class PathListArgument(CommandLineArgument):
	"""
	Represents a list of path arguments  (:class:`~pyTooling.Attribute.ArgParse.Argument.PathArgument`).
	"""
