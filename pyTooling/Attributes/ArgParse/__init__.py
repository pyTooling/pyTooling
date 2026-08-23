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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Attributes to describe a command line interface as decorated methods.

An application deriving from :class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin` declares its commands and
options as attributes on its handler methods. The mixin translates them into an :mod:`argparse` parser hierarchy, so
the command line's structure is written down once - next to the code implementing it - instead of twice.

.. seealso::

   :class:`~pyTooling.Attributes.ArgParse.DefaultHandler`
      |rarr| Marks the method called when no sub-command was given.
   :class:`~pyTooling.Attributes.ArgParse.CommandHandler`
      |rarr| Marks the method implementing a sub-command.
"""
from argparse              import ArgumentParser, Namespace
from typing                import Callable, Any, TypeVar
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Exceptions  import ToolingException
from pyTooling.Common      import firstElement, firstPair
from pyTooling.Attributes  import Attribute


M = TypeVar("M", bound=Callable[..., Any])


@export
class ArgParseError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Attributes.ArgParse`."""


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
	_handler: Callable[..., Any] = None   #: Reference to a method that is called to handle e.g. a sub-command.

	@readonly
	def Handler(self) -> Callable[..., Any]:
		"""
		Read-only property to access the handler method (:attr:`_handler`).

		:returns: The method called to handle the command.
		"""
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
	  |rarr| :class:`~pyTooling.Attributes.ArgParse.CommandHandler`
	* simple names (flags) |br|
	  |rarr| :class:`~pyTooling.Attributes.ArgParse.Flag.FlagArgument`,
	  :class:`~pyTooling.Attributes.ArgParse.BooleanFlag.BooleanFlag`
	* simple values (valued flags) |br|
	  |rarr| :class:`~pyTooling.Attributes.ArgParse.Argument.StringArgument`,
	  :class:`~pyTooling.Attributes.ArgParse.Argument.PathArgument`
	* names and values |br|
	  |rarr| :class:`~pyTooling.Attributes.ArgParse.ValuedFlag.ValuedFlag`,
	  :class:`~pyTooling.Attributes.ArgParse.OptionalValuedFlag.OptionalValuedFlag`
	* key-value pairs |br|
	  |rarr| :class:`~pyTooling.Attributes.ArgParse.KeyValueFlag.NamedKeyValuePairsArgument`
	"""

	# def __init__(self, args: Iterable, kwargs: Mapping) -> None:
	# 	"""
	# 	The constructor expects ``args`` for positional and/or ``kwargs`` for named parameters which are passed without
	# 	modification to :meth:`~ArgumentParser.add_argument`.
	# 	"""
	#
	# 	super().__init__(*args, **kwargs)

	_args:   tuple[Any, ...]  #: Positional parameters forwarded to :meth:`~argparse.ArgumentParser.add_argument`.
	_kwargs: dict[str, Any]   #: Named parameters forwarded to :meth:`~argparse.ArgumentParser.add_argument`.

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""
		Initializes a command line argument.

		This base-class collects the parameters :meth:`~argparse.ArgumentParser.add_argument` will be called with; the
		derived classes assemble them from named parameters instead.

		:param args:   Positional parameters forwarded to :meth:`~argparse.ArgumentParser.add_argument`.
		:param kwargs: Named parameters forwarded to :meth:`~argparse.ArgumentParser.add_argument`.
		"""
		super().__init__()
		self._args =   args
		self._kwargs = kwargs

	@readonly
	def Args(self) -> tuple[Any, ...]:
		"""
		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.

		:returns: Tuple of positional parameters.
		"""
		return self._args

	@readonly
	def KWArgs(self) -> dict[str, Any]:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.

		:returns: Dictionary of named parameters.
		"""
		return self._kwargs


@export
class CommandGroupAttribute(ArgParseAttribute):
	"""
	*Experimental* attribute to group sub-commands in groups for better readability in a ``prog.py --help`` call.
	"""
	__groupName: str = None  #: Name of the group the sub-commands are collected in.

	def __init__(self, groupName: str) -> None:
		"""
		Initializes a command group attribute.

		:param groupName: Name of the group the annotated commands are listed under in the help page.
		"""
		super().__init__()
		self.__groupName = groupName

	@readonly
	def GroupName(self) -> str:
		"""
		Read-only property to access the name of the command group (:attr:`_groupName`).

		:returns: Name of the command group.
		"""
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

	.. attention::

	   It's an error, if more than one method is annotated with this attribute.
	"""

	def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
		"""
		Apply this attribute to the handler method.

		The handler method is stored in :attr:`_handler`.

		:param func: The method handling the case that no sub-command was given.
		:returns:    The same method, now carrying this attribute.
		"""
		self._handler = func
		return super().__call__(func)


@export
class CommandHandler(ArgParseAttribute, _HandlerMixin):  #, _KwArgsMixin):
	"""
	Marks a handler method as responsible for the given command.

	A sub-command parser is constructed for it with :meth:`~argparse.ArgumentParser.add_subparsers`.
	"""

	_command: str    #: Name of the sub-command this handler is responsible for.
	_help:    str    #: Help text of the sub-command, displayed in the help page.
	# FIXME: extract to mixin?
	_args:    tuple[Any, ...]  #: Positional parameters forwarded to :meth:`~argparse.ArgumentParser.add_subparsers`.
	_kwargs:  dict[str, Any]   #: Named parameters forwarded to :meth:`~argparse.ArgumentParser.add_subparsers`.

	def __init__(self, command: str, help: str = "", **kwargs: Any) -> None:
		"""
		Initializes a command handler attribute.

		:param command: Name of the sub-command on the command line.
		:param help:    Optional, help text shown for the sub-command. Default: ``""``.
		:param kwargs:  Named parameters forwarded to :meth:`~argparse.ArgumentParser.add_subparsers`.
		"""
		super().__init__()
		self._command = command
		self._help = help
		self._args =   tuple()
		self._kwargs = kwargs

		self._kwargs["help"] = help

	def __call__(self, func: M) -> M:
		"""
		Apply this attribute to the handler method.

		The handler method is stored in :attr:`_handler`.

		:param func: The method handling the sub-command.
		:returns:    The same method, now carrying this attribute.
		"""
		self._handler = func
		return super().__call__(func)

	@readonly
	def Command(self) -> str:
		"""
		Read-only property to access the command a sub-command parser adheres to (:attr:`_command`).

		:returns: Name of the command.
		"""
		return self._command

# FIXME: extract to mixin?
	@readonly
	def Args(self) -> tuple[Any, ...]:
		"""
		A tuple of additional positional parameters (``*args``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.

		:returns: Tuple of positional parameters.
		"""
		return self._args

	# FIXME: extract to mixin?
	@readonly
	def KWArgs(self) -> dict[str, Any]:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the attribute. These additional parameters are
		passed without modification to :class:`~ArgumentParser`.

		:returns: Dictionary of named parameters.
		"""
		return self._kwargs


@export
class ArgParseHelperMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class to implement an :mod:`argparse`-base command line argument processor.
	"""
	_mainParser: ArgumentParser             #: The main argument parser of the application.
	# TODO: Find type
	_formatter:  Any                        #: Help page formatter class used by every parser.
	# TODO: Find type
	_subParser:  Any                        #: The sub-parser action the sub-commands are registered at.
	_subParsers: dict[str, ArgumentParser]  #: Sub-command name to its argument parser.

	def __init__(self, **kwargs: Any) -> None:
		"""
		The mixin-constructor expects an optional list of named parameters which are passed without modification to the
		:class:`ArgumentParser` constructor.

		:param kwargs:         Named parameters forwarded to the :class:`~argparse.ArgumentParser` constructor.
		:raises ArgParseError: If more than one method is marked as the default handler.
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
				raise ArgParseError("Marked default handler multiple times with 'DefaultAttribute'.")

			# set default handler for the main parser
			self._mainParser.set_defaults(func=firstElement(attributes).Handler)

			# Add argument descriptions for the main parser
			methodAttributes = defaultMethod.GetAttributes(CommandLineArgument)  # ArgumentAttribute)
			for methodAttribute in methodAttributes:
				self._mainParser.add_argument(*methodAttribute.Args, **methodAttribute.KWArgs)

		elif methodCount > 1:
			raise ArgParseError("Marked more then one handler as default handler with 'DefaultAttribute'.")

		# Search for 'CommandHandler' marked methods
		methods: dict[Callable[..., Any], tuple[CommandHandler]] = self.GetMethodsWithAttributes(predicate=CommandHandler)
		for method, attributes in methods.items():
			if self._subParser is None:
				self._subParser = self._mainParser.add_subparsers(help='sub-command help')

			if len(attributes) > 1:
				raise ArgParseError("Marked command handler multiple times with 'CommandHandler'.")

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
		"""
		Parse the command line arguments and call the handler method the command selects.

		:param enableAutoComplete: Optional, if ``True``, register the parser with ``argcomplete``, if that package is
		                           installed.
		"""
		if enableAutoComplete:
			self._EnabledAutoComplete()

		self._ParseArguments()

	def _EnabledAutoComplete(self) -> None:
		"""
		Register the main parser with ``argcomplete`` for shell completion.

		The package is optional: when it isn't installed, completion is silently unavailable.
		"""
		try:
			from argcomplete  import autocomplete
			autocomplete(self._mainParser)
		except ImportError:  # pragma: no cover
			pass

	def _ParseArguments(self) -> None:
		"""
		Parse the command line arguments and route them to the selected handler method.
		"""
		# parse command line options and process split arguments in callback functions
		parsed, args = self._mainParser.parse_known_args()
		self._RouteToHandler(parsed)

	def _RouteToHandler(self, args: Namespace) -> None:
		"""
		Call the handler method the parsed arguments select.

		The handler is stored as an unbound function, so it is called with the application object as first parameter.

		:param args: The parsed command line arguments.
		"""
		# because func is a function (unbound to an object), it MUST be called with self as a first parameter
		args.func(self, args)

	@readonly
	def MainParser(self) -> ArgumentParser:
		"""
		Read-only property to access the main argument parser (:attr:`_mainParser`).

		:returns: The main argument parser.
		"""
		return self._mainParser

	@readonly
	def SubParsers(self) -> dict[str, ArgumentParser]:
		"""
		Read-only property to access the sub-parsers (:attr:`_subParser`).

		:returns: Dictionary of command names and their sub-parsers.
		"""
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


# ==================================================================================================================== #
# Deprecated names, kept for backwards compatibility. Removed in v11.0.0.
# ==================================================================================================================== #
ArgParseException = ArgParseError
