# ==================================================================================================================== #
#             _____           _ _                  _   _   _        _ _           _                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _     / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |   / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/                        #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
This Python module offers the base implementation of .NET-like attributes realized with class-based Python decorators.
This module comes also with a mixin-class to ease using classes having annotated methods.

The annotated data is stored as instances of :class:`~pyTooling.Attributes.Attribute` classes in an additional field per
class, method or function. By default, this field is called ``__pyattr__``.

.. hint:: See :ref:`high-level help <ATTR>` for explanations and usage examples.
"""

# load dependencies
from types  import MethodType, FunctionType
from typing import Callable, List, TypeVar, Dict, Any, Iterable, Union, Type, Tuple, Generator, ClassVar

from pyTooling.Decorators import export


__all__ = ["Entity", "TAttr", "TAttributeFilter", "ATTRIBUTES_MEMBER_NAME"]

Entity = TypeVar("Entity", bound=Union[Type, Callable])
"""A type variable for functions, methods or classes."""

TAttr = TypeVar("TAttr", bound='Attribute')
"""A type variable for :class:`~pyTooling.Attributes.Attribute`."""

TAttributeFilter = Union[Type[TAttr], Iterable[Type[TAttr]], None]
"""A type hint for a predicate parameter that accepts either a single :class:`~pyTooling.Attributes.Attribute` or an
iterable of those."""

ATTRIBUTES_MEMBER_NAME: str = "__pyattr__"
"""Field name on entities (function, class, method) to store pyTooling.Attributes."""


@export
class Attribute:  # (metaclass=ExtendedType, slots=True):
	"""Base-class for all pyTooling attributes."""
#	__AttributesMemberName__: ClassVar[str]       = "__pyattr__"    #: Field name on entities (function, class, method) to store pyTooling.Attributes.
	_functions:               ClassVar[List[Any]] = []              #: List of functions, this Attribute was attached to.
	_classes:                 ClassVar[List[Any]] = []              #: List of classes, this Attribute was attached to.
	_methods:                 ClassVar[List[Any]] = []              #: List of methods, this Attribute was attached to.

	def __init_subclass__(cls, **kwargs: Dict[str, Any]):
		"""
		Ensure each derived class has its own instance of ``_functions``, ``_classes`` and ``_methods`` to register the
		usage of that Attribute.
		"""
		super().__init_subclass__(**kwargs)
		cls._functions = []
		cls._classes = []
		cls._methods = []

	# Make all classes derived from Attribute callable, so they can be used as a decorator.
	def __call__(self, entity: Entity) -> Entity:
		"""
		Attributes get attached to an entity (function, class, method) and an index is updated at the attribute for reverse
		lookups.

		:param entity:     Entity (function, class, method), to attach an attribute to.
		:returns:          Same entity, with attached attribute.
		:raises TypeError: If parameter 'entity' is not a function, class nor method.
		"""
		if isinstance(entity, MethodType):
			self._methods.append(entity)
		elif isinstance(entity, FunctionType):
			self._functions.append(entity)
		elif isinstance(entity, type):
			self._classes.append(entity)
		else:
			raise TypeError(f"Parameter 'entity' is not a function, class nor method.")

		if hasattr(entity, ATTRIBUTES_MEMBER_NAME):
			getattr(entity, ATTRIBUTES_MEMBER_NAME).insert(0, self)
		else:
			setattr(entity, ATTRIBUTES_MEMBER_NAME,  [self, ])

		return entity

	@classmethod
	def GetFunctions(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all functions, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``predicate`` - when the item is a subclass of ``predicate``.

		:param scope:     Undocumented.
		:param predicate: An attribute class or tuple thereof, to filter for that attribute type or subtype.
		:returns:         A sequence of functions where this attribute is attached to.
		"""
		if scope is None:
			if predicate is None:
				for c in cls._functions:
					yield c
			elif issubclass(predicate, Attribute):
				for c in cls._functions:
					if issubclass(c, predicate):
						yield c
			else:
				raise TypeError(f"Parameter 'predicate' is not an Attribute or derived class.")
		elif predicate is None:
			raise NotImplementedError(f"Parameter 'scope' isn't supported yet.")
			# for c in cls._functions:
			# 	if isnestedclass(c, scope):
			# 		yield c
		else:
			for c in cls._functions:
				# if isnestedclass(c, scope) and issubclass(c, predicate):
				if issubclass(c, predicate):
					yield c

	@classmethod
	def GetClasses(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all classes, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``predicate`` - when the item is a subclass of ``predicate``.

		:param scope:     Undocumented.
		:param predicate: An attribute class or tuple thereof, to filter for that attribute type or subtype.
		:returns:         A sequence of classes where this attribute is attached to.
		"""
		from pyTooling.Common import isnestedclass

		if scope is None:
			if predicate is None:
				for c in cls._classes:
					yield c
			else:
				for c in cls._classes:
					if issubclass(c, predicate):
						yield c
		elif predicate is None:
			for c in cls._classes:
				if isnestedclass(c, scope):
					yield c
		else:
			for c in cls._classes:
				if isnestedclass(c, scope) and issubclass(c, predicate):
					yield c

	@classmethod
	def GetMethods(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all methods, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``predicate`` - when the item is a subclass of ``predicate``.

		:param scope:     Undocumented.
		:param predicate: An attribute class or tuple thereof, to filter for that attribute type or subtype.
		:returns:         A sequence of methods where this attribute is attached to.
		"""
		from pyTooling.Common import isnestedclass

		if scope is None:
			if predicate is None:
				for c in cls._methods:
					yield c
			else:
				for c in cls._classes:
					if issubclass(c, predicate):
						yield c
		elif predicate is None:
			for c in cls._classes:
				if isnestedclass(c, scope):
					yield c
		else:
			for c in cls._classes:
				if isnestedclass(c, scope) and issubclass(c, predicate):
					yield c

	@classmethod
	def GetMethods2(cls, inst: Any, includeDerivedAttributes: bool = True) -> Dict[Callable, List['Attribute']]:
		methods = {}
		# print("-----------------------------------")
		# print(inst)
		classOfInst = inst.__class__
		if classOfInst is type:
			classOfInst = inst

		mro = classOfInst.mro()

		# print(mro)

		# search in method-resolution-order (MRO)
		for c in mro:
			for function in c.__dict__.values():
				# print(functionName, function)
				if callable(function):
					# try to read '__pyattr__'
					try:
						attributes = getattr(function, ATTRIBUTES_MEMBER_NAME)
						# print(attributes)
						if includeDerivedAttributes:
							for attribute in attributes:
								if isinstance(attribute, cls):
									try:
										methods[function].append(attribute)
									except KeyError:
										methods[function] = [attribute]
						else:
							for attribute in attributes:
								if type(attribute) is cls:
									try:
										methods[function].append(attribute)
									except KeyError:
										methods[function] = [attribute]

					except AttributeError:
						pass
					except KeyError:
						pass

		return methods

	@classmethod
	def GetAttributes(cls, method: MethodType, includeSubClasses: bool = True) -> Tuple['Attribute', ...]:
		"""
		Returns attached attributes of this kind for a given method.

		:param method:
		:param includeSubClasses:
		:return:
		:raises TypeError:
		"""
		if hasattr(method, ATTRIBUTES_MEMBER_NAME):
			attributes = getattr(method, ATTRIBUTES_MEMBER_NAME)
			if isinstance(attributes, list):
				return tuple(attribute for attribute in attributes if isinstance(attribute, cls))
			else:
				raise TypeError(f"Method '{method.__class__.__name__}{method.__name__}' has a '{ATTRIBUTES_MEMBER_NAME}' field, but it's not a list of Attributes.")
		return tuple()
