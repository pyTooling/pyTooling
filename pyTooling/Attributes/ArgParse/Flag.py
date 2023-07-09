from pyTooling.Decorators import export


@export
class FlagAttribute(ArgParseAttribute, _HandlerMixin, _KwArgsMixin):
	pass

@export
class ShortFlag(FlagAttribute):
	pass

@export
class LongFlag(FlagAttribute):
	pass

@export
class WinodwsFlag(FlagAttribute):
	pass

