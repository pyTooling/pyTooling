from pyTooling.Decorators import export

from .Argument import NamedArgument


@export
class FlagArgument(NamedArgument):
	pass


@export
class ShortFlag(FlagArgument, pattern="-{0}"):
	pass


@export
class LongFlag(FlagArgument, pattern="--{0}"):
	pass


@export
class WindowsFlag(FlagArgument, pattern="/{0}"):
	pass
