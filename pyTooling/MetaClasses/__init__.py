# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#   Sven Köhler                                                                                                        #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""The MetaClasses package implements Python meta-classes (classes to construct other classes in Python).

.. hint:: See :ref:`high-level help <META>` for explanations and usage examples.
"""
from inspect  import signature, Parameter
from types    import MethodType
from typing   import Any, Tuple, List, Dict, Callable, Type

from ..Decorators import export


@export
class Singleton(type):
	"""Implements a singleton pattern in form of a Python metaclass (a class constructing classes)."""

	_instanceCache: Dict[type, Any] = {}       #: Cache of all created singleton instances.

	def __call__(cls, *args, **kwargs):
		"""Overwrites the ``__call__`` method of parent class :py:class:`type` to return an object instance from an
		instances cache (see :py:attr:`_instanceCache`) if the class was already constructed before.
		"""
		if cls not in cls._instanceCache:
			cls._instanceCache[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instanceCache[cls]

	@classmethod
	def Register(cls, t, instance) -> None:
		"""Register a type,instance pair in :attr:`_instanceCache`."""
		if t not in cls._instanceCache:
			cls._instanceCache[t] = instance
		else:
			raise KeyError(f"Type '{t!s}' is already registered.")


@export
class Overloading(type):
	"""Metaclass that allows multiple dispatch of methods based on method signatures.

	.. seealso:

	   `Python Cookbook - Multiple dispatch with function annotations <https://GitHub.com/dabeaz/python-cookbook/blob/master/src/9/multiple_dispatch_with_function_annotations/example1.py?ts=2>`__
	"""

	class DispatchDictionary(dict):
		"""Special dictionary to build dispatchable methods in a metaclass."""

		class DispatchableMethod:
			"""Represents a single multimethod."""

			def __init__(self, name):
				self._methods: Dict[Tuple, Callable] = {}
				self.__name__ = name

			def register(self, method) -> None:
				"""Register a new method as a dispatchable."""

				# Build a signature from the method's type annotations
				sig = signature(method)
				types: List[Type] = []
				for name, parameter in sig.parameters.items():
					if name == "self":
						continue

					if parameter.annotation is Parameter.empty:
						raise TypeError(f"Argument {name} must be annotated with a type.")
					if not isinstance(parameter.annotation, type):
						raise TypeError(f"Argument {name} annotation must be a type.")

					if parameter.default is not Parameter.empty:
						self._methods[tuple(types)] = method
					types.append(parameter.annotation)

				self._methods[tuple(types)] = method

			def __call__(self, *args):
				"""Call a method based on type signature of the arguments."""
				types = tuple(type(arg) for arg in args[1:])
				meth = self._methods.get(types, None)
				if meth:
					return meth(*args)
				else:
					raise TypeError(f"No matching method for types {types}.")

			def __get__(self, instance, cls):
				"""Descriptor method needed to make calls work in a class."""
				if instance is not None:
					return MethodType(self, instance)
				else:
					return self

		def __setitem__(self, key, value):
			if key in self:
				# If key already exists, it must be a dispatchable method or callable
				currentValue = self[key]
				if isinstance(currentValue, self.DispatchableMethod):
					currentValue.register(value)
				else:
					dispatchable = self.DispatchableMethod(key)
					dispatchable.register(currentValue)
					dispatchable.register(value)
					super().__setitem__(key, dispatchable)
			else:
				super().__setitem__(key, value)

	def __new__(cls, className, bases, classDict):
		return type.__new__(cls, className, bases, dict(classDict))

	@classmethod
	def __prepare__(cls, classname, bases):
		return cls.DispatchDictionary()


@export
class SlottedType(type):
	"""

	.. seealso::

		`Python data model - __slots__ <https://docs.python.org/3/reference/datamodel.html#slots>`__
	"""

	def __new__(metacls, className: str, baseClasses: Tuple[type], members: Dict[str, Any]) -> type:
		annotatedFields = {}
		for baseClass in baseClasses:
			for base in reversed(baseClass.mro()[:-1]):
				if not hasattr(base, "__slots__"):
					raise TypeError(f"Base-class '{base.__name__}' has no '__slots__'.")

				for annotation in base.__slots__:
					annotatedFields[annotation] = base

		# Typehint the annotations variable, as long as TypedDict isn't supported by all supported versions.
		# (TypedDict was added in 3.8; see https://docs.python.org/3/library/typing.html#typing.TypedDict)
		annotations: Dict[str, Any] = members.get("__annotations__", {})
		for annotation in annotations:
			if annotation in annotatedFields:
				raise TypeError(f"Slot '{annotation}' already exists in base-class '{annotatedFields[annotation]}'.")

		members['__slots__'] = (*members.get('__slots__', []), *annotations)
		return type.__new__(metacls, className, baseClasses, members)
