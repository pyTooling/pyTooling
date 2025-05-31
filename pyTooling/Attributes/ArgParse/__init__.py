# ==================================================================================================================== #
#            _   _   _        _ _           _                 _              ____                                      #
#           / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___     / \   _ __ __ _|  _ \ __ _ _ __ ___  ___                  #
#          / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|   / _ \ | '__/ _` | |_) / _` | '__/ __|/ _ \                 #
#   _ _ _ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \_ / ___ \| | | (_| |  __/ (_| | |  \__ \  __/                 #
#  (_|_|_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___(_)_/   \_\_|  \__, |_|   \__,_|_|  |___/\___|                 #
#                                                                      |___/                                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
from argparse import ArgumentParser, Namespace
from typing   import Callable, Dict, Tuple, Any, TypeVar

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import firstElement, firstPair
	from pyTooling.Attributes  import Attribute
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Attributes.ArgParse] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType
		from Exceptions          import ToolingException
		from Common              import firstElement, firstPair
		from Attributes          import Attribute
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Attributes.ArgParse] Could not import directly!")
		raise ex


M = TypeVar("M", bound=Callable)


@export
class ArgParseException(ToolingException):
	pass


#@abstract
@export
class ArgParseAttribute(Attribute):
	"""
	Base-class for all attributes to describe a :mod:`argparse`-base command line argument parser.
	"""


@export
class _HandlerMixin(metaclass=ExtendedType, mixin=True):
	"""
	A mixin-class that offers a class field for a reference to a handler method and a matching property.
	"""
	_handler: Callable = None   #: Reference to a method that is called to handle e.g. a sub-command.

	@readonly
	def Handler(self) -> Callable:
		"""Returns the handler method."""
		return self._handler


# FIXME: Is _HandlerMixin needed here, or for commands?
@export
class CommandLineArgument(ArgParseAttribute, _HandlerMixin):
	"""
	Base-class for all *Argument* classes.

	An argument instance can be converted via ``AsArgument`` to a single string value or a sequence of string values
	(tuple) usable e.g. with :class:`subprocess.Popen`. Each argument class implements at least one ``pattern`` parameter
	to specify how argument are formatted.

	There are multiple derived formats supporting:

	* commands |br|
	  |rarr| :mod:`~pyTooling.Attribute.ArgParse.Command`
	* simple names (flags) |br|
	  |rarr| :mod:`~pyTooling.Attribute.ArgParse.Flag`, :mod:`~pyTooling.Attribute.ArgParse.BooleanFlag`
	* simple values (vlaued flags) |br|
	  |rarr| :class:`~pyTooling.Attribute.ArgParse.Argument.StringArgument`, :class:`~pyTooling.Attribute.ArgParse.Argument.PathArgument`
	* names and values |br|
	  |rarr| :mod:`~pyTooling.Attribute.ArgParse.ValuedFlag`, :mod:`~pyTooling.Attribute.ArgParse.OptionalValuedFlag`
	* key-value pairs |br|
	  |rarr| :mod:`~pyTooling.Attribute.ArgParse.NamedKeyValuePair`
	"""

	# def __init__(self, args: Iterable, kwargs: Mapping) -> None:
	# 	"""
	# 	The constructor expects ``args`` for positional and/or ``kwargs`` for named parameters which are passed without
	# 	modification to :meth:`~ArgumentParser.add_argument`.
	# 	"""
	#
	# 	super().__init__(*args, **kwargs)

	_args:   Tuple
	_kwargs: Dict

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""
		The constructor expects positional (``*args``) and/or named parameters (``**kwargs``) which are passed without
		modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__()
		self._args =   args
		self._kwargs = kwargs

	@readonly
	def Args(self) -> Tuple:
		"""
		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._args

	@readonly
	def KWArgs(self) -> Dict:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._kwargs


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

	@readonly
	def GroupName(self) -> str:
		"""Returns the name of the command group."""
		return self.__groupName


# @export
# class _KwArgsMixin(metaclass=ExtendedType, mixin=True):
# 	"""
# 	A mixin-class that offers a class field for named parameters (```**kwargs``) and a matching property.
# 	"""
# 	_kwargs: Dict        #: A dictionary of additional keyword parameters.
#
# 	@readonly
# 	def KWArgs(self) -> Dict:
# 		"""
# 		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
# 		passed without modification to :class:`~ArgumentParser`.
# 		"""
# 		return self._kwargs
#
#
# @export
# class _ArgsMixin(_KwArgsMixin, mixin=True):
# 	"""
# 	A mixin-class that offers a class field for positional parameters (```*args``) and a matching property.
# 	"""
#
# 	_args: Tuple  #: A tuple of additional positional parameters.
#
# 	@readonly
# 	def Args(self) -> Tuple:
# 		"""
# 		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
# 		passed without modification to :class:`~ArgumentParser`.
# 		"""
# 		return self._args


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
class CommandHandler(ArgParseAttribute, _HandlerMixin):  #, _KwArgsMixin):
	"""Marks a handler method as responsible for the given 'command'. This constructs
	a sub-command parser using :meth:`~ArgumentParser.add_subparsers`.
	"""

	_command: str
	_help: str
	# FIXME: extract to mixin?
	_args:   Tuple
	_kwargs: Dict

	def __init__(self, command: str, help: str = "", **kwargs: Any) -> None:
		"""The constructor expects a 'command' and an optional list of named parameters
		(keyword arguments) which are passed without modification to :meth:`~ArgumentParser.add_subparsers`.
		"""
		super().__init__()
		self._command = command
		self._help = help
		self._args =   tuple()
		self._kwargs = kwargs

		self._kwargs["help"] = help

	def __call__(self, func: M) -> M:
		self._handler = func
		return super().__call__(func)

	@readonly
	def Command(self) -> str:
		"""Returns the 'command' a sub-command parser adheres to."""
		return self._command

# FIXME: extract to mixin?
	@readonly
	def Args(self) -> Tuple:
		"""
		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._args

	# FIXME: extract to mixin?
	@readonly
	def KWArgs(self) -> Dict:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.
		"""
		return self._kwargs


@export
class ArgParseHelperMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class to implement an :mod:`argparse`-base command line argument processor.
	"""
	_mainParser: ArgumentParser
	_formatter:  Any   # TODO: Find type
	_subParser:  Any   # TODO: Find type
	_subParsers: Dict  # TODO: Find type

	def __init__(self, **kwargs: Any) -> None:
		"""
		The mixin-constructor expects an optional list of named parameters which are passed without modification to the
		:class:`ArgumentParser` constructor.
		"""
		from .Argument import CommandLineArgument

		super().__init__()

		self._subParser = None
		self._subParsers = {}
		self._formatter = kwargs["formatter_class"] if "formatter_class" in kwargs else None

		if "formatter_class" in kwargs:
			self._formatter = kwargs["formatter_class"]
		if "allow_abbrev" not in kwargs:
			kwargs["allow_abbrev"] = False
		if "exit_on_error" not in kwargs:
			kwargs["exit_on_error"] = False

		# create a commandline argument parser
		self._mainParser = ArgumentParser(**kwargs)

		# Search for 'DefaultHandler' marked method
		methods = self.GetMethodsWithAttributes(predicate=DefaultHandler)
		if (methodCount := len(methods)) == 1:
			defaultMethod, attributes = firstPair(methods)
			if len(attributes) > 1:
				raise ArgParseException("Marked default handler multiple times with 'DefaultAttribute'.")

			# set default handler for the main parser
			self._mainParser.set_defaults(func=firstElement(attributes).Handler)

			# Add argument descriptions for the main parser
			methodAttributes = defaultMethod.GetAttributes(CommandLineArgument)  # ArgumentAttribute)
			for methodAttribute in methodAttributes:
				self._mainParser.add_argument(*methodAttribute.Args, **methodAttribute.KWArgs)

		elif methodCount > 1:
			raise ArgParseException("Marked more then one handler as default handler with 'DefaultAttribute'.")

		# Search for 'CommandHandler' marked methods
		methods: Dict[Callable, Tuple[CommandHandler]] = self.GetMethodsWithAttributes(predicate=CommandHandler)
		for method, attributes in methods.items():
			if self._subParser is None:
				self._subParser = self._mainParser.add_subparsers(help='sub-command help')

			if len(attributes) > 1:
				raise ArgParseException("Marked command handler multiple times with 'CommandHandler'.")

			# Add a sub parser for each command / handler pair
			attribute = firstElement(attributes)
			kwArgs = attribute.KWArgs.copy()
			if "formatter_class" not in kwArgs and self._formatter is not None:
				kwArgs["formatter_class"] = self._formatter

			kwArgs["allow_abbrev"] = False if "allow_abbrev" not in kwargs else kwargs["allow_abbrev"]

			subParser = self._subParser.add_parser(attribute.Command, **kwArgs)
			subParser.set_defaults(func=attribute.Handler)

			# Add arguments for the sub-parsers
			methodAttributes = method.GetAttributes(CommandLineArgument)  # ArgumentAttribute)
			for methodAttribute in methodAttributes:
				subParser.add_argument(*methodAttribute.Args, **methodAttribute.KWArgs)

			self._subParsers[attribute.Command] = subParser

	def Run(self, enableAutoComplete: bool = True) -> None:
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

	@readonly
	def MainParser(self) -> ArgumentParser:
		"""Returns the main parser."""
		return self._mainParser

	@readonly
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

