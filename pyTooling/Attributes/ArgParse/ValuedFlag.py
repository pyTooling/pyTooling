from pyTooling.Decorators import export

from .Argument import NamedAndValuedArgument


@export
class ValuedFlag(NamedAndValuedArgument):
	"""
	Defines a switch argument like ``--help``.

	Some of the named parameters passed to :meth:`~ArgumentParser.add_argument` are predefined (or overwritten) to create
	a boolean parameter passed to the registered handler method. The boolean parameter is ``True`` if the switch argument
	is present in the commandline arguments, otherwise ``False``.
	"""

	def __init__(self, short: str = None, long: str = None, dest: str = None, metavar: str = None, help: str = None):
		"""
		The constructor expects positional (``*args``), the destination parameter name ``dest`` and/or named parameters
		(``**kwargs``) which are passed to :meth:`~ArgumentParser.add_argument`.

		To implement a switch argument, the following named parameters are predefined:

		* ``action="store_const"``
		* ``const=True``
		* ``default=False``

		This implements a boolean parameter passed to the handler method.
		"""
		args = []
		if short is not None:
			args.append(short)
		if long is not None:
			args.append(long)

		kwargs = {
			"dest":    dest,
			"metavar": metavar,
			"default": None,
			"help":    help,
		}
		super().__init__(*args, **kwargs)


@export
class ShortValuedFlag(ValuedFlag):
	def __init__(self, short: str = None, dest: str = None, help: str = None):
		super().__init__(short=short, dest=dest, help=help)


@export
class LongValuedFlag(ValuedFlag):
	def __init__(self, long: str = None, dest: str = None, help: str = None):
		super().__init__(long=long, dest=dest, help=help)