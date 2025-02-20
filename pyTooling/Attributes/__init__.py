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
"""
This Python module offers the base implementation of .NET-like attributes realized with class-based Python decorators.
This module comes also with a mixin-class to ease using classes having annotated methods.

The annotated data is stored as instances of :class:`~pyTooling.Attributes.Attribute` classes in an additional field per
class, method or function. By default, this field is called ``__pyattr__``.

.. hint:: See :ref:`high-level help <ATTR>` for explanations and usage examples.
"""
from enum   import IntFlag
from sys    import version_info
from types  import MethodType, FunctionType, ModuleType
from typing import Callable, List, TypeVar, Dict, Any, Iterable, Union, Type, Tuple, Generator, ClassVar, Optional as Nullable

try:
	from pyTooling.Decorators import export, readonly
	from pyTooling.Common     import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Attributes] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export, readonly
		from Common     import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Attributes] Could not import directly!")
		raise ex


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
class AttributeScope(IntFlag):
	"""
	An enumeration of possible entities an attribute can be applied to.

	Values of this enumeration can be merged (or-ed) if an attribute can be applied to multiple language entities.
	Supported language entities are: classes, methods or functions. Class fields or module variables are not supported.
	"""
	Class =    1                     #: Attribute can be applied to classes.
	Method =   2                     #: Attribute can be applied to methods.
	Function = 4                     #: Attribute can be applied to functions.
	Any = Class + Method + Function  #: Attribute can be applied to any language entity.


@export
class Attribute:  # (metaclass=ExtendedType, slots=True):
	"""Base-class for all pyTooling attributes."""
#	__AttributesMemberName__: ClassVar[str]       = "__pyattr__"             #: Field name on entities (function, class, method) to store pyTooling.Attributes.
	_functions:               ClassVar[List[Any]] = []                       #: List of functions, this Attribute was attached to.
	_classes:                 ClassVar[List[Any]] = []                       #: List of classes, this Attribute was attached to.
	_methods:                 ClassVar[List[Any]] = []                       #: List of methods, this Attribute was attached to.
	_scope:                   ClassVar[AttributeScope] = AttributeScope.Any  #: Allowed language construct this attribute can be used with.

	# Ensure each derived class has its own instances of class variables.
	def __init_subclass__(cls, **kwargs: Any) -> None:
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
		self._AppendAttribute(entity, self)

		return entity

	@staticmethod
	def _AppendAttribute(entity: Entity, attribute: "Attribute") -> None:
		"""
		Append an attribute to a language entity (class, method, function).

		.. hint::

		   This method can be used in attribute groups to apply multiple attributes within ``__call__`` method.

		   .. code-block:: Python

		      class GroupAttribute(Attribute):
		        def __call__(self, entity: Entity) -> Entity:
		          self._AppendAttribute(entity, SimpleAttribute(...))
		          self._AppendAttribute(entity, SimpleAttribute(...))

		          return entity

		:param entity:     Entity, the attribute is attached to.
		:param attribute:  Attribute to attach.
		:raises TypeError: If parameter 'entity' is not a class, method or function.
		"""
		if isinstance(entity, MethodType):
			attribute._methods.append(entity)
		elif isinstance(entity, FunctionType):
			attribute._functions.append(entity)
		elif isinstance(entity, type):
			attribute._classes.append(entity)
		else:
			ex = TypeError(f"Parameter 'entity' is not a function, class nor method.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(entity)}'.")
			raise ex

		if hasattr(entity, ATTRIBUTES_MEMBER_NAME):
			getattr(entity, ATTRIBUTES_MEMBER_NAME).insert(0, attribute)
		else:
			setattr(entity, ATTRIBUTES_MEMBER_NAME,  [attribute, ])

	@property
	def Scope(cls) -> AttributeScope:
		return cls._scope

	@classmethod
	def GetFunctions(cls, scope: Nullable[Type] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all functions, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.

		:param scope:     Undocumented.
		:returns:         A sequence of functions where this attribute is attached to.
		"""
		if scope is None:
			for c in cls._functions:
				yield c
		elif isinstance(scope, ModuleType):
			elementsInScope = set(c for c in scope.__dict__.values() if isinstance(c, FunctionType))
			for c in cls._functions:
				if c in elementsInScope:
					yield c
		else:
			raise NotImplementedError(f"Parameter 'scope' is a class isn't supported yet.")

	@classmethod
	def GetClasses(cls, scope: Union[Type, ModuleType, None] = None, subclassOf: Nullable[Type] = None) -> Generator[TAttr, None, None]:
	# def GetClasses(cls, scope: Nullable[Type] = None, predicate: Nullable[TAttributeFilter] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all classes, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``subclassOf`` - when the item is a subclass of ``subclassOf``.

		:param scope:      Undocumented.
		:param subclassOf: An attribute class or tuple thereof, to filter for that attribute type or subtype.
		:returns:          A sequence of classes where this attribute is attached to.
		"""
		from pyTooling.Common import isnestedclass

		if scope is None:
			if subclassOf is None:
				for c in cls._classes:
					yield c
			else:
				for c in cls._classes:
					if issubclass(c, subclassOf):
						yield c
		elif subclassOf is None:
			if isinstance(scope, ModuleType):
				elementsInScope = set(c for c in scope.__dict__.values() if isinstance(c, type))
				for c in cls._classes:
					if c in elementsInScope:
						yield c
			else:
				for c in cls._classes:
					if isnestedclass(c, scope):
						yield c
		else:
			for c in cls._classes:
				if isnestedclass(c, scope) and issubclass(c, subclassOf):
					yield c

	@classmethod
	def GetMethods(cls, scope: Nullable[Type] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all methods, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.

		:param scope:     Undocumented.
		:returns:         A sequence of methods where this attribute is attached to.
		"""
		if scope is None:
			for c in cls._methods:
				yield c
		else:
			for m in cls._methods:
				if m.__classobj__ is scope:
					yield m

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


@export
class SimpleAttribute(Attribute):
	_args: Tuple[Any, ...]
	_kwargs: Dict[str, Any]

	def __init__(self, *args, **kwargs) -> None:
		self._args = args
		self._kwargs = kwargs

	@readonly
	def Args(self) -> Tuple[Any, ...]:
		return self._args

	@readonly
	def KwArgs(self) -> Dict[str, Any]:
		return self._kwargs
