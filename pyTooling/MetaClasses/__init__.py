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
"""
The MetaClasses package implements Python meta-classes (classes to construct other classes in Python).

.. hint:: See :ref:`high-level help <META>` for explanations and usage examples.
"""
import threading
from functools  import wraps
from inspect    import signature, Parameter
from types      import MethodType
from typing     import Any, Tuple, List, Dict, Callable, Type, TypeVar


try:
	from ..Exceptions import AbstractClassError
	from ..Decorators import export, OriginalFunction
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.MetaClasses] Could not import from 'pyTooling.*'!")

	try:
		from Exceptions import AbstractClassError
		from Decorators import export, OriginalFunction
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.MetaClasses] Could not import from 'Decorators' directly!")
		raise ex


__all__ = ["M"]


@export
class Overloading(type):
	"""
	Metaclass that allows multiple dispatch of methods based on method signatures.

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
	"""
	Mark a method as *abstract* and replace the implementation with a new method raising a :py:exc:`NotImplementedError`.

	The original method is stored in ``<method>.__orig_func__`` and it's doc-string is copied to the replacement method.

	.. warning::

	   This decorator should be used in combination with meta-class :py:class:`~pyTooling.Metaclasses.ExtendedType`.
	   Otherwise, an abstract class itself doesn't throw a :py:exc:`~pyTooling.Exceptions.AbstractClassError` at
	   instantiation.

	.. admonition:: ``example.py``

	   .. code:: python

	      class Data(mataclass=ExtendedType):
	        @abstractmethod
	        def method:
	          '''This method needs to be implemented'''

	:param method: Method that is marked as *abstract*.
	:returns:      Replacement method, which raises a :py:exc:`NotImplementedError`. In additional field ``__abstract__``
	               is added.
	"""
	@OriginalFunction(method)
	@wraps(method)
	def func(self):
		raise NotImplementedError(f"Method '{method.__name__}' is abstract and needs to be overridden in a derived class.")

	func.__abstract__ = True
	return func


@export
def mustoverride(method: M) -> M:
	"""
	Mark a method as *must-override*.

	.. warning::

	   This decorator needs to be used in combination with meta-class :py:class:`~pyTooling.Metaclasses.ExtendedType`.
	   Otherwise, an abstract class itself doesn't throw a :py:exc:`~pyTooling.Exceptions.MustOverrideClassError` at
	   instantiation.

	.. admonition:: ``example.py``

	   .. code:: python

	      class Data(mataclass=ExtendedType):
	        @mustoverride
	        def method:
	          '''This is a very basic implementation'''

	:param method: Method that is marked as *must-override*.
	:returns:      Same method, but with additional ``__mustOverride__`` field.
	"""
	method.__mustOverride__ = True
	return method


@export
def overloadable(method: M) -> M:
	method.__overloadable__ = True
	return method


# TODO: allow __dict__ and __weakref__ if slotted is enabled

@export
class ExtendedType(type):
	"""
  .. todo:: Needs documentation.

	Features:

	* Store object members more efficiently in ``__slots__`` instead of ``_dict__``.
	* Allow only a single instance to be created (:term:`singleton`).
	* Define methods as :term:`abstract <abstract method>` or :term:`must-override <mustoverride method>` and prohibit
	  instantiation of :term:`abstract classes <abstract class>`.

	.. #* Allow method overloading and dispatch overloads based on argument signatures.
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
		Construct a new class using this :term:`meta-class`.

		:param className:       The name of the class to construct.
		:param baseClasses:     The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:         The dictionary of members for the constructed class.
		:param singleton:       If true, make the class a :term:`Singleton`.
		:param useSlots:        If true, store object attributes in :term:`__slots__ <slots>` instead of ``__dict__``.
		:returns:               The new class.
		:raises AttributeError: If base-class has no '__slots__' attribute.
		:raises AttributeError: If slot already exists in base-class.
		"""
		# Check if members should be stored in slots. If so get these members from type annotated fields
		if useSlots:
			members['__slots__'] = self.__getSlots(baseClasses, members)

		# Create a new class
		newClass = type.__new__(self, className, baseClasses, members)
		# Search in inheritance tree for abstract methods
		newClass.__abstractMethods__ = self._checkForAbstractMethods(baseClasses, members)
		newClass.__isAbstract__ = self._wrapNewMethodIfAbstract(newClass)
		newClass.__isSingleton__ = self._wrapNewMethodIfSingleton(newClass, singleton)

		return newClass

	@classmethod
	def _checkForAbstractMethods(metacls, baseClasses: Tuple[type], members: Dict[str, Any]) -> Tuple[str, ...]:
		"""
		Check if the current class contains abstract methods and return a tuple of them.

		These abstract methods might be inherited from any base-class. If there are inherited abstract methods, check if
		they are now implemented (overridden) by the current class that's right now constructed.

		:param baseClasses: The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:     The dictionary of members for the constructed class.
		:returns:           A tuple of abstract method's names.
		"""
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
	def _wrapNewMethodIfSingleton(newClass, singleton: bool) -> bool:
		"""
		If a class is a singleton, wrap the ``_new__`` method, so it returns a cached object, if a first object was created.

		Only the first object creation initializes the object.

		This implementation is threadsafe.

		:param newClass:  The newly constructed class for further modifications.
		:param singleton: If true, the class allows only a single instance to exist.
		:returns:         True, if the class is a singleton.
		"""
		if hasattr(newClass, "__isSingleton__"):
			singleton = newClass.__isSingleton__

		if singleton:
			oldnew = newClass.__new__
			if hasattr(oldnew, "__singleton_wrapper__"):
				oldnew = oldnew.__orig_func__

			oldinit = newClass.__init__
			if hasattr(oldinit, "__singleton_wrapper__"):
				oldinit = oldinit.__orig_func__

			@OriginalFunction(oldnew)
			@wraps(oldnew)
			def new(cls, *args, **kwargs):
				with cls.__singletonInstanceCond__:
					if cls.__singletonInstanceCache__ is None:
						obj = oldnew(cls, *args, **kwargs)
						cls.__singletonInstanceCache__ = obj
					else:
						obj = cls.__singletonInstanceCache__

				return obj

			@OriginalFunction(oldinit)
			@wraps(oldinit)
			def init(self, *args, **kwargs):
				cls = self.__class__
				cv = cls.__singletonInstanceCond__
				with cv:
					if cls.__singletonInstanceInit__:
						oldinit(self, *args, **kwargs)
						cls.__singletonInstanceInit__ = False
						cv.notify_all()
					elif args or kwargs:
						raise ValueError(f"A further instance of a singleton can't be reinitialized with parameters.")
					else:
						while cls.__singletonInstanceInit__:
							cv.wait()

			new.__singleton_wrapper__ = True
			init.__singleton_wrapper__ = True

			newClass.__new__ = new
			newClass.__init__ = init
			newClass.__singletonInstanceCond__ = threading.Condition()
			newClass.__singletonInstanceInit__ = True
			newClass.__singletonInstanceCache__ = None
			return True

		return False

	@staticmethod
	def _wrapNewMethodIfAbstract(newClass) -> bool:
		"""
		If the class has abstract methods, replace the ``_new__`` method, so it raises an exception.

		:param newClass:            The newly constructed class for further modifications.
		:returns:                   True, if the class is abstract.
		:raises AbstractClassError: If the class is abstract and can't be instantiated.
		"""
		# Replace '__new__' by a variant to throw an error on not overridden methods
		if newClass.__abstractMethods__:
			oldnew = newClass.__new__
			@OriginalFunction(oldnew)
			@wraps(oldnew)
			def new(cls, *args, **kwargs):
				formattedMethodNames = "', '".join(newClass.__abstractMethods__)
				raise AbstractClassError(f"Class '{cls.__name__}' is abstract. The following methods: '{formattedMethodNames}' need to be overridden in a derived class.")

			new.__raises_abstract_class_error__ = True

			newClass.__new__ = new
			return True

		# Handle classes which are not abstract, especially derived classes, if not abstract anymore
		else:
			# skip intermediate 'new' function if class isn't abstract anymore
			try:
				if newClass.__new__.__raises_abstract_class_error__:
					newClass.__new__ = newClass.__new__.__orig_func__
				elif newClass.__new__.__isSingleton__:
					raise Exception(f"Found a singleton wrapper around an AbstractError raising method. This case is not handled yet.")
			except AttributeError as ex:
				# WORKAROUND:
				#   AttributeError.name was added in Python 3.10. For version <3.10 use a string contains operation.
				try:
					if ex.name != "__raises_abstract_class_error__":
						raise ex
				except AttributeError:
					if "__raises_abstract_class_error__" not in str(ex):
						raise ex

			return False

	@staticmethod
	def __getSlots(baseClasses: Tuple[type], members: Dict[str, Any]) -> Tuple[str, ...]:
		"""
		Get all object attributes, that should be stored in a slot.

		:param baseClasses:     The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:         The dictionary of members for the constructed class.
		:returns:               A tuple of member names to be stored in slots.
		:raises AttributeError: If the current class will use slots, but a base-class isn't using slots.
		:raises AttributeError: If the class redefines a slotted attribute already defined in a base-class.
		"""
		annotatedFields = {}
		for baseClass in baseClasses:
			for base in reversed(baseClass.mro()[:-1]):
				if not hasattr(base, "__slots__"):
					raise AttributeError(f"Base-class '{base.__name__}' has no '__slots__'.")

				for annotation in base.__slots__:
					annotatedFields[annotation] = base

		# WORKAROUND:
		#   Typehint the 'annotations' variable, as long as 'TypedDict' isn't supported by all target versions.
		#   (TypedDict was added in 3.8; see https://docs.python.org/3/library/typing.html#typing.TypedDict)
		annotations: Dict[str, Any] = members.get("__annotations__", {})
		for annotation in annotations:
			if annotation in annotatedFields:
				raise AttributeError(f"Slot '{annotation}' already exists in base-class '{annotatedFields[annotation]}'.")

		return (*members.get('__slots__', []), *annotations)


@export
class ObjectWithSlots(metaclass=ExtendedType, useSlots=True):
	"""Classes derived from this class will store all members in ``__slots__``."""
