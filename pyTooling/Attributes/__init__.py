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
This Python module offers the base implementation of .NET-like attributes realized with class-based Python decorators.
This module comes also with a mixin-class to ease using classes having annotated methods.

The annotated data is stored as instances of :class:`~pyTooling.Attributes.Attribute` classes in an additional field per
class, method or function. By default, this field is called ``__pyattr__``.

.. hint::

   See :ref:`high-level help <ATTR>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Attributes.ArgParse`
      |rarr| Attributes describing a command line interface.
   :mod:`pyTooling.MetaClasses`
      |rarr| The meta-class that collects the attributes attached to a class' methods.
   :mod:`pyTooling.Decorators`
      |rarr| Decorators that modify an entity instead of marking it.
"""
from __future__           import annotations

from enum                 import IntFlag
from types                import MethodType, FunctionType, ModuleType
from typing               import Callable, TypeVar, Any, Iterable, Union, Generator, ClassVar
from typing               import Optional as Nullable

from pyTooling.Decorators import export, readonly
from pyTooling.Common     import getFullyQualifiedName
from pyTooling.Exceptions import ToolingException


__all__ = ["Entity", "TAttr", "TAttributeFilter", "ATTRIBUTES_MEMBER_NAME"]

Entity = TypeVar("Entity", bound=Union[type, Callable[..., Any]])
"""A type variable for functions, methods or classes."""

TAttr = TypeVar("TAttr", bound='Attribute')
"""A type variable for :class:`~pyTooling.Attributes.Attribute`."""

TAttributeFilter = Union[type[TAttr], Iterable[type[TAttr]], None]
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
class AttributeScopeError(ToolingException):
	"""
	An attribute is applied to a language entity its :class:`AttributeScope` doesn't allow.
	"""


@export
class Attribute:  # (metaclass=ExtendedType, slots=True):
	"""Base-class for all pyTooling attributes."""
#	__AttributesMemberName__: ClassVar[str]       = "__pyattr__"             #: Field name on entities (function, class, method) to store pyTooling.Attributes.
	_functions:               ClassVar[list[Any]] = []                       #: List of functions, this Attribute was attached to.
	_classes:                 ClassVar[list[Any]] = []                       #: List of classes, this Attribute was attached to.
	_methods:                 ClassVar[list[Any]] = []                       #: List of methods, this Attribute was attached to.
	_scope:                   ClassVar[AttributeScope] = AttributeScope.Any  #: Allowed language construct this attribute can be used with.

	# Ensure each derived class has its own instances of class variables.
	def __init_subclass__(cls, **kwargs: Any) -> None:
		"""
		Ensure each derived attribute class gets its own registry of annotated entities.

		The registries :attr:`_functions`, :attr:`_classes` and :attr:`_methods` are class variables, so a derived
		attribute class would otherwise share the base-class' lists and report entities it was never attached to. Fresh
		lists are assigned per derived class to prevent that.

		:param kwargs: Class keyword arguments forwarded to the base-class.
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

		:param entity:               Entity (function, class, method), to attach an attribute to.
		:returns:                    Same entity, with attached attribute.
		:raises TypeError:           If parameter 'entity' is not a function, class nor method.
		:raises AttributeScopeError: If the attribute's :attr:`Scope` doesn't allow the entity's kind.
		"""
		self._AppendAttribute(entity, self)

		return entity

	@staticmethod
	def _AppendAttribute(entity: Entity, attribute: Attribute) -> None:
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

		A function defined in a class body is a method, although it is a plain function while the decorator runs: its
		qualified name is ``<Class>.<name>``, while a module's function is named ``<name>`` and a nested function
		``<function>.<locals>.<name>``.

		:param entity:               Entity, the attribute is attached to.
		:param attribute:            Attribute to attach.
		:raises TypeError:           If parameter 'entity' is not a class, method or function.
		:raises AttributeScopeError: If the attribute's :attr:`Scope` doesn't allow the entity's kind.
		"""
		if isinstance(entity, MethodType):
			kind =     AttributeScope.Method
			registry = attribute._methods
		elif isinstance(entity, FunctionType):
			names = entity.__qualname__.split(".")
			if len(names) > 1 and names[-2] != "<locals>":
				kind =     AttributeScope.Method
				registry = attribute._methods
			else:
				kind =     AttributeScope.Function
				registry = attribute._functions
		elif isinstance(entity, type):
			kind =     AttributeScope.Class
			registry = attribute._classes
		else:
			ex = TypeError("Parameter 'entity' is not a function, class nor method.")
			ex.add_note(f"Got type '{getFullyQualifiedName(entity)}'.")
			raise ex

		if kind not in attribute._scope:
			ex = AttributeScopeError(
				f"Attribute '{attribute.__class__.__name__}' can't be applied to {kind.name.lower()} '{entity.__qualname__}'."
			)
			ex.add_note(f"Its scope is '{attribute._scope.name}'.")
			raise ex

		registry.append(entity)

		if hasattr(entity, ATTRIBUTES_MEMBER_NAME):
			getattr(entity, ATTRIBUTES_MEMBER_NAME).insert(0, attribute)
		else:
			setattr(entity, ATTRIBUTES_MEMBER_NAME,  [attribute, ])

	@readonly
	def Scope(self) -> AttributeScope:
		"""
		Read-only property to access the language entities this attribute can be applied to (:attr:`_scope`).

		It is an instance property: on the attribute class, :attr:`_scope` is read directly.

		:returns: The language entities this attribute can be applied to.
		"""
		return self._scope

	@classmethod
	def GetFunctions(cls, scope: Nullable[type | ModuleType] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all functions, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.

		:param scope:                Optional, module the functions have to be defined in; ``None`` accepts every function.
		:returns:                    A sequence of functions where this attribute is attached to.
		:raises NotImplementedError: If this abstract method is not overridden by a derived class.
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
			raise NotImplementedError("Parameter 'scope' is a class isn't supported yet.")

	@classmethod
	def GetClasses(cls, scope: Nullable[type | ModuleType] = None, subclassOf: Nullable[type] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all classes, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``subclassOf`` - when the item is a subclass of ``subclassOf``.

		:param scope:      Optional, class or module the classes have to be nested in or defined in; ``None`` accepts every
		                   class.
		:param subclassOf: Optional, a class or tuple thereof; only annotated classes derived from it are returned.
		                   ``None`` accepts every class.
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
	def GetMethods(cls, scope: Nullable[type] = None) -> Generator[TAttr, None, None]:
		"""
		Return a generator for all methods, where this attribute is attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.

		:param scope: Optional, class the methods are defined in; ``None`` accepts every method. Only a class built with
		              :class:`~pyTooling.MetaClasses.ExtendedType` links its methods to it, so a method of another class
		              isn't found by scope.
		:returns:     A sequence of methods where this attribute is attached to.
		"""
		if scope is None:
			for c in cls._methods:
				yield c
		else:
			for m in cls._methods:
				if getattr(m, "__classobj__", None) is scope:
					yield m

	@classmethod
	def GetAttributes(cls, method: MethodType, includeSubClasses: bool = True) -> tuple[Attribute, ...]:
		"""
		Returns attached attributes of this kind for a given method.

		:param method:            Method to search attributes for.
		:param includeSubClasses: Optional, if ``True``, attributes of derived attribute classes are included too.
		:returns:                 Tuple of attached attributes of this kind.
		:raises TypeError:        If the method's attribute field is not a list.
		"""
		if hasattr(method, ATTRIBUTES_MEMBER_NAME):
			attributes = getattr(method, ATTRIBUTES_MEMBER_NAME)
			if isinstance(attributes, list):
				if includeSubClasses:
					return tuple(attribute for attribute in attributes if isinstance(attribute, cls))
				else:
					return tuple(attribute for attribute in attributes if type(attribute) is cls)
			else:
				methodName = getFullyQualifiedName(method)
				ex = TypeError(f"Method '{methodName}' has a '{ATTRIBUTES_MEMBER_NAME}' field, but it's no list.")
				ex.add_note(f"Got type '{getFullyQualifiedName(attributes)}'.")
				raise ex
		return tuple()


@export
class SimpleAttribute(Attribute):
	"""
	A generic attribute preserving the parameters it was applied with.

	It needs no derived class per use case: whatever is passed to it is available from :attr:`Args` and :attr:`KwArgs`,
	which makes it the quickest way to mark a class, method or function and read the marking back.
	"""
	_args:   tuple[Any, ...]  #: Positional parameters the attribute was applied with.
	_kwargs: dict[str, Any]   #: Named parameters the attribute was applied with.

	def __init__(self, *args: Any, **kwargs: Any) -> None:
		"""
		Initialize the attribute, preserving whatever parameters it was applied with.

		:param args:   Positional parameters, readable from :attr:`Args`.
		:param kwargs: Named parameters, readable from :attr:`KwArgs`.
		"""
		self._args = args
		self._kwargs = kwargs

	@readonly
	def Args(self) -> tuple[Any, ...]:
		"""
		Read-only property to access the positional parameters this attribute was created with (:attr:`_args`).

		:returns: Tuple of positional parameters.
		"""
		return self._args

	@readonly
	def KwArgs(self) -> dict[str, Any]:
		"""
		Read-only property to access the named parameters this attribute was created with (:attr:`_kwargs`).

		:returns: Dictionary of named parameters.
		"""
		return self._kwargs
