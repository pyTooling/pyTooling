# =============================================================================
#                  _   _   _        _ _           _
#   _ __  _   _   / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___
#  | '_ \| | | | / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|
#  | |_) | |_| |/ ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \
#  | .__/ \__, /_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/
#  |_|    |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python module:      pyAttribute for Python's argparse Package.
#
# License:
# ============================================================================
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
"""
This module implements attribute-classes and a mixin-class which describe
options to construct a :mod:`argparse`-based command line processor. All
attributes in this module are sub-classes of :class:`Attribute`.
"""

# load dependencies
from argparse   import ArgumentParser
from typing     import Callable, Dict, Tuple, List

from pyTooling.Decorators import export

from .          import Attribute, AttributeHelperMixin


@export
class AbstractClassError(RuntimeError):
	"""Raised when an abstract class is instantiated."""


@export
def abstract(abstract_cls):
	def new_decorator(old__new__):
		"""will decorate the __new__ method"""

		def new__new__(cls, *a, **k):
			""" will wraps (or replace) __new__ method"""
			if abstract_cls is cls:
				# if tried to directly instanciate it
				raise AbstractClassError("An abstract class can't be instantiated.")
			# else cls is a derived class
			return old__new__(cls, *a, **k)
		return new__new__

	# decorate
	abstract_cls.__new__ = new_decorator(abstract_cls.__new__)

	return abstract_cls


#@abstract
@export
class ArgParseAttribute(Attribute):
	"""
	Base-class for all attributes to describe a :mod:`argparse`-base command line
	argument parser.
	"""


@export
class CommandGroupAttribute(ArgParseAttribute):
	"""
	*Experimental* attribute to group sub-commands in groups for better readability
	in a ``prog.py --help`` call.
	"""
	__groupName: str = None

	def __init__(self, groupName: str):
		"""
		The constructor expects a 'groupName' which can be used to group sub-commands
		for better readability.
		"""
		super().__init__()
		self.__groupName = groupName

	@property
	def GroupName(self) -> str:
		"""Returns the name of the command group."""
		return self.__groupName


@export
class _HandlerMixin:
	"""
	A mixin-class that offers a class field for a reference to a handler method
	and a matching property.
	"""
	_handler: Callable = None   #: Reference to a method that is called to handle e.g. a sub-command.

	@property
	def Handler(self) -> Callable:
		"""Returns the handler method."""
		return self._handler


@export
class _KwArgsMixin:
	"""
	A mixin-class that offers a class field for named parameters (```**kwargs``)
	and a matching property.
	"""
	_kwargs: Dict = None        #: A dictionary of additional keyword parameters.

	@property
	def KWArgs(self) -> Dict:
		"""
		A dictionary of additional named parameters (``**kwargs``) passed to the
		attribute. These additional parameters are passed without modification to
		:class:`~ArgumentParser`.
		"""
		return self._kwargs


@export
class _ArgsMixin(_KwArgsMixin):
	"""
	A mixin-class that offers a class field for positional parameters (```*args``)
	and a matching property.
	"""

	_args: Tuple = None  #: A tuple of additional positional parameters.

	@property
	def Args(self) -> Tuple:
		"""
		A tuple of additional positional parameters (``*args``) passed to the
		attribute. These additional parameters are passed without modification to
		:class:`~ArgumentParser`.
		"""
		return self._args


@export
class DefaultAttribute(ArgParseAttribute, _HandlerMixin):
	"""
	Marks a handler method is *default* handler. This method is called if no
	sub-command is given. It's an error if more then one method is annotated with
	this attribute.
	"""

	def __call__(self, func: Callable) -> Callable:
		self._handler = func
		return super().__call__(func)





@export
class ArgumentAttribute(ArgParseAttribute, _ArgsMixin):
	"""Base-class for all attributes storing arguments."""

	def __init__(self, *args, **kwargs):
		"""
		The constructor expects positional (``*args``) and/or named parameters
		(``**kwargs``) which are passed without modification to :meth:`~ArgumentParser.add_argument`.
		"""
		super().__init__()
		self._args =   args
		self._kwargs = kwargs


@export
class SwitchArgumentAttribute(ArgumentAttribute):
	"""
	Defines a switch argument like ``--help``.

	Some of the named parameters passed to :meth:`~ArgumentParser.add_argument`
	are predefined (or overwritten) to create a boolean parameter passed to the
	registered handler method. The boolean parameter is ``True`` if the switch
	argument is present in the commandline arguments, otherwise ``False``.
	"""

	def __init__(self, *args, dest:str, **kwargs):
		"""
		The constructor expects positional (``*args``), the destination parameter
		name ``dest`` and/or named parameters	(``**kwargs``) which are passed to
		:meth:`~ArgumentParser.add_argument`.

		To implement a switch argument, the following named parameters are
		predefined:

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


@export
class ArgParseMixin(AttributeHelperMixin):
	"""
	Mixin-class to implement an :mod:`argparse`-base command line argument
	processor.
	"""
	__mainParser: ArgumentParser =  None
	__subParser =   None
	__formatter =   None
	__subParsers =  {}

	def __init__(self, **kwargs):
		"""
		The mixin-constructor expects an optional list of named parameters which
		are passed without modification to the :class:`ArgumentParser` constructor.
		"""
		super().__init__()

		if ("formatter_class" in kwargs):
			self.__formatter = kwargs["formatter_class"]

		# create a commandline argument parser
		self.__mainParser = ArgumentParser(**kwargs)
		self.__subParser = self.__mainParser.add_subparsers(help='sub-command help')

		methods = self.GetMethods(predicate=CommonArgumentAttribute)
		# QUESTION: should 'CommonArgumentAttribute's be limited to only one method?
		for method, attributes in methods.items():
			for attribute in attributes:
				self.__mainParser.add_argument(*(attribute.Args), **(attribute.KWArgs))

		methods = self.GetMethods(predicate=CommonSwitchArgumentAttribute)
		# QUESTION: should 'CommonSwitchArgumentAttribute's be limited to only one method?
		# QUESTION: should 'CommonSwitchArgumentAttribute's be limited to same method as 'CommonArgumentAttribute's
		for method, attributes in methods.items():
			for attribute in attributes:
				self.__mainParser.add_argument(*(attribute.Args), **(attribute.KWArgs))

		methods = self.GetMethods(predicate=DefaultAttribute)
		l = len(methods)
		if (l == 0):
			pass
		elif (l == 1):
			attribute = methods.popitem(last=False)[1][0]
			self.__mainParser.set_defaults(func=attribute.Handler)
		else:
			raise Exception("Marked more then one handler as default handler with 'DefaultAttribute'.")

		methods = self.GetMethods(predicate=CommandAttribute)
		for method, attributes in methods.items():
			if (len(attributes) == 1):
				attribute : CommandAttribute = attributes[0]
				kwArgs = attribute.KWArgs.copy()
				if ("formatter_class" not in kwArgs and self.__formatter is not None):
					kwArgs["formatter_class"] = self.__formatter
				subParser = self.__subParser.add_parser(attribute.Command, **kwArgs)
				subParser.set_defaults(func=attribute.Handler)

				attributes2: List[ArgumentAttribute] = self.GetAttributes(method, predicate=ArgumentAttribute)
				for attribute2 in attributes2:
					subParser.add_argument(*(attribute2.Args), **(attribute2.KWArgs))

				self.__subParsers[attribute.Command] = subParser
			else:
				raise Exception("Defined more then one 'CommandAttribute' per handler method.")


	def Run(self, enableAutoComplete=True) -> None:
		if enableAutoComplete:
			self._EnabledAutoComplete()

		self._ParseArguments()

	def _EnabledAutoComplete(self) -> None:
		try:
			from argcomplete  import autocomplete
			autocomplete(self.__mainParser)
		except ImportError:  # pragma: no cover
			pass

	def _ParseArguments(self) -> None:
		# parse command line options and process split arguments in callback functions
		args = self.__mainParser.parse_args()
		self._RouteToHandler(args)

	def _RouteToHandler(self, args) -> None:
		# because func is a function (unbound to an object), it MUST be called with self as a first parameter
		args.func(self, args)

	@property
	def MainParser(self) -> ArgumentParser:
		"""Returns the main parser."""
		return self.__mainParser

	@property
	def SubParsers(self):
		"""Returns the sub-parsers."""
		return self.__subParsers
