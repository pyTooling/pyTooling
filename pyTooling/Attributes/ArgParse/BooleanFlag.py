from pyTooling.Decorators import export
from .Argument import NamedArgument, ValuedArgument


@export
class BooleanFlag(NamedArgument, ValuedArgument):
	pass


@export
class ShortBooleanFlag(BooleanFlag, pattern="-with-{0}", falsePattern="-without-{0}"):
	pass


@export
class LongBooleanFlag(BooleanFlag, pattern="--with-{0}", falsePattern="--without-{0}"):
	pass


@export
class WindowsBooleanFlag(BooleanFlag, pattern="/with-{0}", falsePattern="/without-{0}"):
	pass
