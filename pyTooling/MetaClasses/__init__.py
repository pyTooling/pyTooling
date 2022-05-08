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
from functools  import wraps
from inspect    import signature, Parameter
from types      import MethodType
from typing     import Any, Tuple, List, Dict, Callable, Type, TypeVar


try:
	from ..Exceptions import AbstractClassError
	from ..Decorators import export, OriginalFunction
except (ImportError, ModuleNotFoundError):
	print("[pyTooling.MetaClasses] Could not import from 'pyTooling.*'!")

	try:
		from Exceptions import AbstractClassError
		from Decorators import export, OriginalFunction
	except (ImportError, ModuleNotFoundError) as ex:
		print("[pyTooling.MetaClasses] Could not import from 'Decorators' directly!")
		raise ex


__all__ = ["M"]


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


M = TypeVar("M", bound=Callable)   #: A type variable for methods.


@export
def abstractmethod(method: M) -> M:
	@wraps(method)
	def func(self):
		raise NotImplementedError(f"Method '{method.__name__}' is abstract and needs to be overridden in a derived class.")

	func.__abstract__ = True
	return func


@export
def mustoverride(method: M) -> M:
	method.__mustOverride__ = True
	return method


@export
def overloadable(method: M) -> M:
	method.__overloadable__ = True
	return method


@export
class SuperType(type):
	"""

	Features:

	* Store object members more effectively in slots instead of ``_dict__``.
	* Allow only a single instance to be created (singleton).
	* Define methods as abstract and prohibit instantiation of abstract classes.
	* Allow method overloading and dispatch overloads based on argument signatures.

	.. seealso::

		`Python data model - __slots__ <https://docs.python.org/3/reference/datamodel.html#slots>`__
	"""

	def __new__(
		self,
		className: str,
		baseClasses: Tuple[type],
		members: Dict[str, Any],
		singleton: bool = False,
		useSlots: bool = False
	) -> type:
		"""

		:param className:
		:param baseClasses:
		:param members:
		:param singleton:
		:param useSlots:
		:raises AttributeError: If base-class has no '__slots__' attribute.
		:raises AttributeError: If slot already exists in base-class.
		"""

		# Check if members should be stored in slots. If so get these members from type annotated fields
		if useSlots:
			members['__slots__'] = self.__getSlots(baseClasses, members)

		# Create a new class
		newClass = type.__new__(self, className, baseClasses, members)
		# Search in inheritance tree for abstract methods
		newClass.__abstractMethods__ = self.__checkForAbstractMethods(baseClasses, members)
		newClass.__isSingleton__ = self.__wrapNewMethodIfSingleton(newClass, singleton)
		newClass.__isAbstract__ = self.__wrapNewMethodIfAbstract(newClass)

			# if hasattr(newClass, "__new__"):
			# 	new = getattr(newClass, "__new__")
			# 	isFromObject = new is object.__new__
			# 	print(f"__new__ of '{className}': {new} ({isFromObject})")
			# else:
			# 	print(f"Class '{className}' has no __new__.")

		return newClass

	# def __call__(metacls, *args, **kwargs) -> type:
	# 	"""Overwrites the ``__call__`` method of parent class :py:class:`type` to return an object instance from an
	# 	instances cache (see :py:attr:`__singletonInstanceCache__`) if the class was already constructed before.
	# 	"""
	# 	if metacls.__isSingleton__:
	# 		if metacls.__singletonInstanceCache__ is None:
	# 			newClass = type.__call__(metacls, *args, **kwargs)
	# 			metacls.__singletonInstanceCache__ = newClass
	# 		else:
	# 			newClass = metacls.__singletonInstanceCache__
	# 	else:
	# 		newClass = type.__call__(metacls, *args, **kwargs)
	#
	# 	return newClass

	@classmethod
	def __checkForAbstractMethods(metacls, baseClasses: Tuple[type], members: Dict[str, Any]) -> Tuple[str, ...]:
		result = set()
		for base in baseClasses:
			for cls in base.__mro__:
				if hasattr(cls, "__abstractMethods__"):
					result = result.union(cls.__abstractMethods__)

		for memberName, member in members.items():
			if hasattr(member, "__abstract__") or hasattr(member, "__mustOverride__"):
				result.add(memberName)
			elif memberName in result:
				result.remove(memberName)

		return tuple(result)

	@staticmethod
	def __wrapNewMethodIfSingleton(newClass, singleton: bool) -> bool:
		if singleton:
			@OriginalFunction(newClass.__new__)
			@wraps(newClass.__new__)
			def new(cls, *args, **kwargs):
				if cls.__singletonInstanceCache__ is None:
					obj = newClass.__new__(*args, **kwargs)
					cls.__singletonInstanceCache__ = obj
				else:
					obj = cls.__singletonInstanceCache__

				return obj

			newClass.__new__ = new
			newClass.__singletonInstanceCache__ = None
			return True

		return False

	@staticmethod
	def __wrapNewMethodIfAbstract(newClass) -> bool:
		# Replace '__new__' by a variant to through an error on not overridden methods
		if newClass.__abstractMethods__:
			@OriginalFunction(newClass.__new__)
			@wraps(newClass.__new__)
			def new(cls, *args, **kwargs):
				formattedMethodNames = "', '".join(newClass.__abstractMethods__)
				raise AbstractClassError(f"Class '{cls.__name__}' is abstract. The following methods: '{formattedMethodNames}' need to be overridden in a derived class.")

			newClass.__new__ = new
			return True

		# Handle classes which are not abstract, especially derived classes, if not abstract anymore
		else:
			# skip intermediate 'new' function if class isn't abstract anymore
			# if '__new__' is identical to the one from object, it was never wrapped -> no action needed
			if newClass.__new__ is not object.__new__:
				try:
					newClass.__new__ = newClass.__new__.__orig_func__
				except AttributeError:
					print(f"AttributeError for newClass.__new__.__orig_func__ caused by '{newClass.__new__.__name__}'")
					pass

			return False

	@staticmethod
	def __getSlots(baseClasses: Tuple[type], members: Dict[str, Any]):
		annotatedFields = {}
		for baseClass in baseClasses:
			for base in reversed(baseClass.mro()[:-1]):
				if not hasattr(base, "__slots__"):
					raise AttributeError(f"Base-class '{base.__name__}' has no '__slots__'.")

				for annotation in base.__slots__:
					annotatedFields[annotation] = base

		# Typehint the 'annotations' variable, as long as 'TypedDict' isn't supported by all target versions.
		# (TypedDict was added in 3.8; see https://docs.python.org/3/library/typing.html#typing.TypedDict)
		annotations: Dict[str, Any] = members.get("__annotations__", {})
		for annotation in annotations:
			if annotation in annotatedFields:
				raise AttributeError(f"Slot '{annotation}' already exists in base-class '{annotatedFields[annotation]}'.")

		return (*members.get('__slots__', []), *annotations)
