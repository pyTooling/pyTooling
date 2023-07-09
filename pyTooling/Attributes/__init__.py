# =============================================================================
#                  _   _   _        _ _           _
#   _ __  _   _   / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___
#  | '_ \| | | | / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|
#  | |_) | |_| |/ ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \
#  | .__/ \__, /_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/
#  |_|    |___/
# =============================================================================
# Authors:
#   Patrick Lehmann
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
This Python module offers the base implementation of .NET-like attributes
realized with Python decorators. This module comes also with a mixin-class
to ease using classes having annotated methods.

The decorators in pyAttributes are implemented as class-based decorators.

The annotated data is stored in an additional ``__dict__`` entry for each
annotated method. By default the entry is called ``__pyattr__``.
"""

__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2007-2022, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "2.5.2"
__keywords__ =  ["decorators", "attributes", "argparse"]

# load dependencies
from typing import Callable, List, TypeVar, Dict, Any, Iterable, Union, Type, Tuple, Generator
from collections  import OrderedDict

from pyTooling.Common import isnestedclass
from pyTooling.Decorators import export


Entity =  TypeVar("Entity", bound=Union[Type, Callable])
"""A type variable for functions, methods or classes."""

TAttr = TypeVar("TAttr", bound='Attribute')
"""A type variable for :class:`~pyAttributes.Attribute`."""

TAttributeFilter = Union[TAttr, Iterable[TAttr], None]
"""A type hint for a predicate parameter that accepts either a single :class:`~pyAttributes.Attribute` or an iterable of those."""


@export
class Attribute:
	"""Base-class for all pyAttributes."""
	__AttributesMemberName__: str = "__pyattr__"   #: Field name on entities (function, class, method) to store pyAttributes.
	_classes: List[Any]           = []             #: List of classes, this pyAttribute was attached to.

	def __init_subclass__(cls, **kwargs):
		"""Ensure each derived class has its own instance of ``_classes`` to register the usage of that pyAttribute."""
		super().__init_subclass__(**kwargs)
		cls._classes = []

	def __call__(self, entity: Entity) -> Entity:
		"""Make all classes derived from ``Attribute`` callable, so they can be used as a decorator."""
		self._AppendAttribute(entity, self)
		return entity

	@staticmethod
	def _AppendAttribute(entity: Entity, attribute: 'Attribute') -> None:
		"""Helper method, to attach a given pyAttribute to an entity (function, class, method)."""
		if (Attribute.__AttributesMemberName__ in entity.__dict__):
			entity.__dict__[Attribute.__AttributesMemberName__].insert(0, attribute)
		else:
			setattr(entity, Attribute.__AttributesMemberName__, [attribute, ])

		if isinstance(entity, Type):
			attribute._classes.append(entity)

	@classmethod
	def GetClasses(cls, scope: Type = None, predicate: Union[Type, Tuple] = None) -> Generator[Type, None, None]:
		"""
		Return a generator for all classes, where this attribute was attached to.

		The resulting item stream can be filtered by:
		 * ``scope`` - when the item is a nested class in scope ``scope``.
		 * ``predicate`` - when the item is a subclass of ``predicate``.
		"""
		if scope is None:
			if predicate is None:
				for c in cls._classes:
					yield c
			else:
				for c in cls._classes:
					if issubclass(c, predicate):
						yield c
		else:
			if predicate is None:
				for c in cls._classes:
					if isnestedclass(c, scope):
						yield c
			else:
				for c in cls._classes:
					if isnestedclass(c, scope) and issubclass(c, predicate):
						yield c

	@classmethod
	def GetMethods(cls, inst: Any, includeDerivedAttributes: bool=True) -> Dict[Callable, List['Attribute']]:
		methods = {}
		# print("-----------------------------------")
		# print(inst)
		classOfInst = inst.__class__
		if (classOfInst is type):
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
						attributes = function.__dict__[Attribute.__AttributesMemberName__]
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
	def GetAttributes(cls, method: Callable, includeSubClasses: bool=True) -> List['Attribute']:
		"""Returns attached attributes for a given method."""
		if (Attribute.__AttributesMemberName__ in method.__dict__):
			attributes = method.__dict__[Attribute.__AttributesMemberName__]
			if isinstance(attributes, list):
				return [attribute for attribute in attributes if isinstance(attribute, cls)]
		return list()


@export
class AttributeHelperMixin:
	"""A mixin class to ease finding methods with attached pyAttributes."""

	def GetMethods(self, predicate: TAttributeFilter[TAttr]=Attribute) -> Union[Dict[Callable, List[TAttr]], bool]:
		if (predicate is Attribute):
			pass
		elif (predicate is None):
			predicate = Attribute
		elif isinstance(predicate, Iterable):
			predicate = tuple([attribute for attribute in predicate])

		# print("-----------------------------------")
		mro = self.__class__.mro()
		# print(mro)

		attributedMethods = OrderedDict()
		# search in method-resolution-order (MRO)
		for c in mro:
			for method in c.__dict__.values():
				# print(method)
				if isinstance(method, Callable):
					# print("  is callable")
					try:
						attributeList = method.__dict__[Attribute.__AttributesMemberName__]
						for attribute in attributeList:
							if isinstance(attribute, predicate):
								try:
									attributedMethods[method].append(attribute)
								except KeyError:
									attributedMethods[method] = [attribute]

					except AttributeError:
						pass
					except KeyError:
						pass

		return attributedMethods

	@staticmethod
	def HasAttribute(method: Callable, predicate: TAttributeFilter[TAttr]=Attribute) -> bool:  # TODO: add a tuple based type predicate
		"""Returns true, if the given method has pyAttributes attached."""
		try:
			attributeList = method.__dict__[Attribute.__AttributesMemberName__]
			if (len(attributeList) == 0):
				return False
			elif (predicate is not None):
				if isinstance(predicate, Attribute):
					pass
				elif isinstance(predicate, Iterable):
					predicate = tuple([attribute for attribute in predicate])

				for attribute in attributeList:
					if isinstance(attribute, predicate):
						return True
				else:
					return False
			else:
				return False
		except AttributeError:
			return False
		except KeyError:
			return False

	@staticmethod
	def GetAttributes(method: Callable, predicate: TAttributeFilter[TAttr]=Attribute) -> List[TAttr]:  # TODO: add a tuple based type predicate
		"""Returns a list of pyAttributes attached to the given method."""

		try:
			attributeList = method.__dict__[Attribute.__AttributesMemberName__]
			if (predicate is Attribute):
				pass
			elif (predicate is None):
				predicate = Attribute
			elif isinstance(predicate, Iterable):
				predicate = tuple([attribute for attribute in predicate])

			attributes = []
			for attribute in attributeList:
				if isinstance(attribute, predicate):
					attributes.append(attribute)

			return attributes

		except AttributeError:
			return list()
		except KeyError:
			return list()
