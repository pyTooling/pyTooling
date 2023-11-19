from argparse import ArgumentParser, Namespace
from typing import Callable, Dict, Tuple, Any, List, Mapping, Iterable

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import firstElement, firstPair

from .. import Attribute


#@abstract
@export
class ArgParseAttribute(Attribute):
	"""
	Base-class for all attributes to describe a :mod:`argparse`-base command line argument parser.
	"""

	_args:   Tuple
	_kwargs: Mapping

	def __init__(self, *args, **kwargs) -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__()
		self._args =   args
		self._kwargs = kwargs


@export
class CommandGroupAttribute(ArgParseAttribute):
	"""
	*Experimental* attribute to group sub-commands in groups for better readability in a ``prog.py --help`` call.
	"""
	__groupName: str = None

	def __init__(self, groupName: str) -> None:
		"""
		The constructor expects a 'groupName' which can be used to group sub-commands for better readability.
		"""
		super().__init__()
		self.__groupName = groupName

	@property
	def GroupName(self) -> str:
		"""Returns the name of the command group."""
		return self.__groupName


@export
class _HandlerMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class that offers a class field for a reference to a handler method and a matching property.
	"""
	_handler: Callable = None   #: Reference to a method that is called to handle e.g. a sub-command.

	@property
	def Handler(self) -> Callable:
		"""Returns the handler method."""
		return self._handler


@export
class _KwArgsMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class that offers a class field for named parameters (```**kwargs``) and a matching property.
	"""
	_kwargs: Dict        #: A dictionary of additional keyword parameters.

	@property
	def KWArgs(self) -> Dict:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._kwargs


@export
class _ArgsMixin(_KwArgsMixin, mixin=True):
	"""
	A mixin-class that offers a class field for positional parameters (```*args``) and a matching property.
	"""

	_args: Tuple  #: A tuple of additional positional parameters.

	@property
	def Args(self) -> Tuple:
		"""
		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._args


@export
class DefaultHandler(ArgParseAttribute, _HandlerMixin):
	"""
	Marks a handler method as *default* handler. This method is called if no sub-command is given.

	It's an error, if more	than one method is annotated with this attribute.
	"""

	def __call__(self, func: Callable) -> Callable:
		self._handler = func
		return super().__call__(func)


@export
class ArgParseHelperMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class to implement an :mod:`argparse`-base command line argument processor.
	"""
	_mainParser: ArgumentParser
	_formatter:  Any   # TODO: Find type
	_subParser:  Any   # TODO: Find type
	_subParsers: Dict  # TODO: Find type

	def __init__(self, **kwargs) -> None:
		"""
		The mixin-constructor expects an optional list of named parameters which are passed without modification to the
		:class:`ArgumentParser` constructor.
		"""
		from .Command  import CommandHandler
		from .Argument import CommandLineArgument

		super().__init__()

		self._subParsers = {}
		self._formatter = kwargs["formatter_class"] if "formatter_class" in kwargs else None

		if "formatter_class" in kwargs:
			self._formatter = kwargs["formatter_class"]

		# create a commandline argument parser
		self._mainParser = ArgumentParser(**kwargs)
		# TODO: only if subcommands are present
		self._subParser = self._mainParser.add_subparsers(help='sub-command help')

		# Search for 'DefaultHandler' marked method
		methods = self.GetMethodsWithAttributes(predicate=DefaultHandler)
		if (methodCount := len(methods)) == 1:
			defaultMethod, attributes = firstPair(methods)
			if len(attributes) > 1:
				raise Exception("Marked default handler multiple times with 'DefaultAttribute'.")

			# set default handler for the main parser
			self._mainParser.set_defaults(func=firstElement(attributes).Handler)

			# Add argument descriptions for the main parser
			methodAttributes = defaultMethod.GetAttributes(ArgumentAttribute)
			for methodAttribute in methodAttributes:
				self._mainParser.add_argument(*methodAttribute.Args, **methodAttribute.KWArgs)

		elif methodCount > 1:
			raise Exception("Marked more then one handler as default handler with 'DefaultAttribute'.")

		# Search for 'CommandHandler' marked methods
		methods: Dict[Callable, Tuple[CommandHandler]] = self.GetMethodsWithAttributes(predicate=CommandHandler)
		for method, attributes in methods.items():
			if len(attributes) > 1:
				raise Exception("Marked command handler multiple times with 'CommandHandler'.")

			# Add a sub parser for each command / handler pair
			attribute = firstElement(attributes)
			kwArgs = attribute.KWArgs.copy()
			if "formatter_class" not in kwArgs and self._formatter is not None:
				kwArgs["formatter_class"] = self._formatter
			subParser = self._subParser.add_parser(attribute.Command, **kwArgs)
			subParser.set_defaults(func=attribute.Handler)

			# Add arguments for the sub-parsers
			methodAttributes = method.GetAttributes(ArgumentAttribute)
			for methodAttribute in methodAttributes:
				subParser.add_argument(*methodAttribute.Args, **methodAttribute.KWArgs)

			self._subParsers[attribute.Command] = subParser

	def Run(self, enableAutoComplete: bool=True) -> None:
		if enableAutoComplete:
			self._EnabledAutoComplete()

		self._ParseArguments()

	def _EnabledAutoComplete(self) -> None:
		try:
			from argcomplete  import autocomplete
			autocomplete(self._mainParser)
		except ImportError:  # pragma: no cover
			pass

	def _ParseArguments(self) -> None:
		# parse command line options and process split arguments in callback functions
		parsed, args = self._mainParser.parse_known_args()
		self._RouteToHandler(parsed)

	def _RouteToHandler(self, args: Namespace) -> None:
		# because func is a function (unbound to an object), it MUST be called with self as a first parameter
		args.func(self, args)

	@property
	def MainParser(self) -> ArgumentParser:
		"""Returns the main parser."""
		return self._mainParser

	@property
	def SubParsers(self) -> Dict:
		"""Returns the sub-parsers."""
		return self._subParsers


# String
# StringList
# Path
# PathList
# Delimiter
# ValuedFlag --option=value
# ValuedFlagList --option=foo --option=bar
# OptionalValued --option --option=foo
# ValuedTuple


@export
class ArgumentAttribute(ArgParseAttribute, _ArgsMixin):
	"""Base-class for all attributes storing arguments."""


@export
class SwitchArgumentAttribute(ArgumentAttribute):
	"""
	Defines a switch argument like ``--help``.

	Some of the named parameters passed to :meth:`~ArgumentParser.add_argument` are predefined (or overwritten) to create
	a boolean parameter passed to the registered handler method. The boolean parameter is ``True`` if the switch argument
	is present in the commandline arguments, otherwise ``False``.
	"""

	def __init__(self, *args, dest:str, **kwargs) -> None:
		"""
		The constructor expects positional (``*args``), the destination parameter name ``dest`` and/or named parameters
		(``**kwargs``) which are passed to :meth:`~ArgumentParser.add_argument`.

		To implement a switch argument, the following named parameters are predefined:

		* ``action="store_const"``
		* ``const=True``
		* ``default=False``

		This implements a boolean parameter passed to the handler method.
		"""
		kwargs['dest'] =    dest
		kwargs['action'] =  "store_const"
		kwargs['const'] =   True
		kwargs['default'] = False
		super().__init__(*args, **kwargs)


@export
class CommonArgumentAttribute(ArgumentAttribute):
	pass


@export
class CommonSwitchArgumentAttribute(SwitchArgumentAttribute):
	pass
