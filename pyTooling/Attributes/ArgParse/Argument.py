from pyTooling.Decorators import export

from . import ArgParseAttribute


@export
class StringArgument(ArgParseAttribute, _HandlerMixin):
	pass


@export
class PathArgument(ArgParseAttribute, _HandlerMixin):
	pass
