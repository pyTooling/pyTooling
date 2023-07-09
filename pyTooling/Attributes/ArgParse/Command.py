from typing import Callable, TypeVar

from pyTooling.Decorators import export
from . import ArgParseAttribute


M = TypeVar("M", bound=Callable)


@export
class CommandAttribute(ArgParseAttribute, _HandlerMixin, _KwArgsMixin):
	"""Marks a handler method as responsible for the given 'command'. This constructs
	a sub-command parser using :meth:`~ArgumentParser.add_subparsers`.
	"""

	_command: str

	def __init__(self, command: str, **kwargs):
		"""The constructor expects a 'command' and an optional list of named parameters
		(keyword arguments) which are passed without modification to :meth:`~ArgumentParser.add_subparsers`.
		"""
		super().__init__()
		self._command = command
		self._kwargs = kwargs

	def __call__(self, func: M) -> M:
		self._handler = func
		return super().__call__(func)

	@property
	def Command(self) -> str:
		"""Returns the 'command' a sub-command parser adheres to."""
		return self._command
