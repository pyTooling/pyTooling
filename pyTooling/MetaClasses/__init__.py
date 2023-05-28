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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from functools  import wraps
from inspect    import signature, Parameter
from sys        import version_info
from threading  import Condition
from types      import MethodType, FunctionType
from typing     import Any, Tuple, List, Dict, Callable, Type, TypeVar, Generic, Generator, Set, Iterator

try:
	from ..Exceptions import ToolingException
	from ..Decorators import export, OriginalFunction
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.MetaClasses] Could not import from 'pyTooling.*'!")

	try:
		from Exceptions import ToolingException
		from Decorators import export, OriginalFunction
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.MetaClasses] Could not import from 'Decorators' directly!")
		raise ex


__all__ = ["M"]


@export
class ExtendedTypeError(ToolingException):
	pass


@export
class BaseClassWithoutSlotsError(ExtendedTypeError):
	pass


@export
class DuplicateFieldInSlotsError(ExtendedTypeError):
	pass


@export
class AbstractClassError(ExtendedTypeError):
	"""
	The exception is raised, when a class contains methods marked with *abstractmethod* or *mustoverride*.

	.. seealso::

	   :py:func:`@abstractmethod <pyTooling.MetaClasses.abstractmethod>`
	      |rarr| Mark a method as *abstract*.
	   :py:func:`@mustoverride <pyTooling.MetaClasses.mustoverride>`
	      |rarr| Mark a method as *must overrride*.
	   :py:exc:`~MustOverrideClassError`
	      |rarr| Exception raised, if a method is marked as *must-override*.
	"""
	# WORKAROUND: for Python <3.10
	# Implementing a dummy method for Python versions before
	if version_info < (3, 11):
		def add_note(self, message: str):
			try:
				self.__notes__.append(message)
			except AttributeError:
				self.__notes__ = [message]


@export
class MustOverrideClassError(AbstractClassError):
	"""
	The exception is raised, when a class contains methods marked with *must-override*.

	.. seealso::

	   :py:func:`@abstractmethod <pyTooling.MetaClasses.abstractmethod>`
	      |rarr| Mark a method as *abstract*.
	   :py:func:`@mustoverride <pyTooling.MetaClasses.mustoverride>`
	      |rarr| Mark a method as *must overrride*.
	   :py:exc:`~AbstractClassError`
	      |rarr| Exception raised, if a method is marked as *abstract*.
	"""
	# WORKAROUND: for Python <3.10
	# Implementing a dummy method for Python versions before
	if version_info < (3, 11):
		def add_note(self, message: str):
			try:
				self.__notes__.append(message)
			except AttributeError:
				self.__notes__ = [message]


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

	   .. code-block:: python

	      class Data(mataclass=ExtendedType):
	        @abstractmethod
	        def method(self):
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

	Such methods can offer a partial implementation, which is called via ``super()...``.

	.. warning::

	   This decorator needs to be used in combination with meta-class :py:class:`~pyTooling.Metaclasses.ExtendedType`.
	   Otherwise, an abstract class itself doesn't throw a :py:exc:`~pyTooling.Exceptions.MustOverrideClassError` at
	   instantiation.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      class Data(mataclass=ExtendedType):
	        @mustoverride
	        def method(self):
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


@export
class ExtendedType(type):
	"""
	.. todo:: META::ExtendedType Needs documentation.
	.. todo:: META::ExtendedType allow __dict__ and __weakref__ if slotted is enabled

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
		mixin: bool = None,
		singleton: bool = False,
		useSlots: bool = False
	) -> type:
		"""
		Construct a new class using this :term:`meta-class`.

		:param className:       The name of the class to construct.
		:param baseClasses:     The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:         The dictionary of members for the constructed class.
		:param mixin:           If true, make the class a :term:`Mixin`.
		                        If false, create slots if ``useSlots`` is true.
		                        If none, preserve behavior of primary base-class.
		:param singleton:       If true, make the class a :term:`Singleton`.
		:param useSlots:        If true, store object attributes in :term:`__slots__ <slots>` instead of ``__dict__``.
		:returns:               The new class.
		:raises AttributeError: If base-class has no '__slots__' attribute.
		:raises AttributeError: If slot already exists in base-class.
		"""
		mixinSlots = []
		# If mixin isn't set explicitly (None), then check if primary base-class is a mixin.
		#   If so, inherit that behavior.
		#   If it's a mixin, then aggregate all mixinSlots in a list (mixinSlots)
		if mixin is None:
			mixin = False
			if len(baseClasses) > 0:
				primaryBaseClass = baseClasses[0]
				if isinstance(primaryBaseClass, self) and primaryBaseClass.__isMixin__:
					# mixinSlots.extend(primaryBaseClass.__mixinSlots__)
					mixin = True

		# Inherit 'useSlots' feature from primary base-class
		if len(baseClasses) > 0:
			primaryBaseClass = baseClasses[0]
			if isinstance(primaryBaseClass, self):
				useSlots = primaryBaseClass.__usesSlots__

		if mixin:
			if len(baseClasses) > 0:
				inheritancePaths = [path for path in self._iterateBaseClassPaths(baseClasses)]
				primaryInharitancePath: Set[type] = set(inheritancePaths[0])
				for typePath in inheritancePaths[1:]:
					for t in typePath:
						if hasattr(t, "__slots__") and len(t.__slots__) != 0 and t not in primaryInharitancePath:
							ex = TypeError(f"Base-class '{t.__name__}' has non-empty __slots__ and can't be used as a direct or indirect base-class for '{className}'.")
							ex.add_note(f"In Python, only one inheritance branch can use non-empty __slots__.")
							# ex.add_note(f"With ExtendedType, only the primary base-class can use non-empty __slots__.")
							# ex.add_note(f"Secondary base-classes should be marked as mixin-classes.")
							raise ex

				# If current class is set to be a mixin, then aggregate all mixinSlots in a list.
				#   Ensure all base-classes are either constructed
				#     * by meta-class ExtendedType, or
				#     * use no slots, or
				#     * are typing.Generic
				#   If it was constructed by ExtendedType, then ensure this class itself is a mixin-class.
				for baseClass in baseClasses:  # type: ExtendedType
					if baseClass.__class__ is self:
						if baseClass.__isMixin__:
							mixinSlots.extend(baseClass.__mixinSlots__)
		elif useSlots:
			if len(baseClasses) > 0:
				primaryBaseClass = baseClasses[0]
				if type(primaryBaseClass) is self:
					mixinSlots.extend(primaryBaseClass.__mixinSlots__)

				# Not a mixin, because it's a normal class in the primary inheritance path or the end (final) of a mixin hierarchy.
				for secondaryBaseClass in baseClasses[1:]:
					if isinstance(secondaryBaseClass, self):
						if secondaryBaseClass.__isMixin__:
							mixinSlots.extend(secondaryBaseClass.__mixinSlots__)
						else:
							ex = TypeError(f"Base-class '{secondaryBaseClass.__name__}' is not a mixin-class.")
							ex.add_note(f"All secondary base-classes must be mixin-classes.")
							raise ex
					elif isinstance(secondaryBaseClass, type):
						if issubclass(secondaryBaseClass, Generic):
							pass
						elif hasattr(secondaryBaseClass, "__slots__") and len(secondaryBaseClass.__slots__) != 0:
							ex = TypeError(f"Secondary base-class '{secondaryBaseClass.__name__}' has non-empty __slots__.")
							ex.add_note(f"In Python, only one inheritance branch can use non-empty __slots__.")
							ex.add_note(f"With ExtendedType, only the primary base-class can use non-empty __slots__.")
							ex.add_note(f"Secondary base-classes should be marked as mixin-classes.")
							raise ex
					else:
						ex = TypeError(f"Meta-class of '{secondaryBaseClass.__name__}' must be 'ExtendedType' or secondary base-class is 'typing.Generic'.")
						ex.add_note(f"Type (meta-class) of '{secondaryBaseClass.__name__}' is '{secondaryBaseClass.__class__}'.")
						raise ex

		if mixin:
			# If it's a mixin, __slots__ must be an empty tuple.
			#   Collect further fields (listed in members) in the mixinSlots list
			mixinSlots.extend(self.__getSlots(baseClasses, members))
			members["__slots__"] = tuple()
		# Check if members should be stored in slots. If so get these members from type annotated fields
		elif useSlots:
			# If slots are used, all base classes must use slots.
			for baseClass in self._iterateBaseClasses(baseClasses):
				if baseClass is object:
					pass
				elif not hasattr(baseClass, "__slots__"):
					ex = BaseClassWithoutSlotsError(f"Base-classes '{baseClass.__name__}' doesn't use '__slots__'.")
					ex.add_note(f"All base-classes of a class using '__slots__' must use '__slots__' itself.")
					raise ex

			mixinSlots.extend(self.__getSlots(baseClasses, members))
			if len(set(mixinSlots)) != len(mixinSlots):
				from collections import Counter
				duplicates = [field for field, count in Counter(mixinSlots).items() if count > 1]

				raise DuplicateFieldInSlotsError(f"Duplicate fields in __slots__: {', '.join(duplicates)}")

			members["__slots__"] = tuple(mixinSlots)
			mixinSlots.clear()

		# Compute abstract methods
		abstractMethods, members = self._checkForAbstractMethods(baseClasses, members)

		# Create a new class
		newClass = type.__new__(self, className, baseClasses, members)
		newClass.__usesSlots__ = useSlots
		newClass.__isMixin__ = mixin
		newClass.__mixinSlots__ = (*mixinSlots, )

		# Search in inheritance tree for abstract methods
		newClass.__abstractMethods__ = abstractMethods
		newClass.__isAbstract__ = self._wrapNewMethodIfAbstract(newClass)
		newClass.__isSingleton__ = self._wrapNewMethodIfSingleton(newClass, singleton)

		return newClass

	@classmethod
	def _iterateBaseClasses(metacls, baseClasses: Tuple[type]) -> Generator[type, None, None]:
		if len(baseClasses) == 0:
			return

		visited:       Set[type] =            set()
		iteratorStack: List[Iterator[type]] = list()

		for baseClass in baseClasses:
			yield baseClass
			visited.add(baseClass)
			iteratorStack.append(iter(baseClass.__bases__))

			while True:
				try:
					base = next(iteratorStack[-1])  # type: type
					if base not in visited:
						yield base
						if len(base.__bases__) > 0:
							iteratorStack.append(iter(base.__bases__))
					else:
						continue

				except StopIteration:
					iteratorStack.pop()

					if len(iteratorStack) == 0:
						break

	@classmethod
	def _iterateBaseClassPaths(metacls, baseClasses: Tuple[type]) -> Generator[Tuple[type, ...], None, None]:
		"""
		Return a generator to iterate all possible inheritance paths for a given list of base-classes.

		An inheritance path is expressed as a tuple of base-classes from current base-class (left-most item) to
		:class:`object` (right-most item).

		:param baseClasses: List (tuple) of base-classes.
		:returns:           Generator to iterate all inheritance paths. An inheritance path is a tuple of types (base-classes).
		"""
		if len(baseClasses) == 0:
			return

		typeStack:   List[type] =           list()
		iteratorStack: List[Iterator[type]] = list()

		for baseClass in baseClasses:
			typeStack.append(baseClass)
			iteratorStack.append(iter(baseClass.__bases__))

			while True:
				try:
					base = next(iteratorStack[-1])  # type: type
					typeStack.append(base)
					if len(base.__bases__) == 0:
						yield tuple(typeStack)
						typeStack.pop()
					else:
						iteratorStack.append(iter(base.__bases__))

				except StopIteration:
					typeStack.pop()
					iteratorStack.pop()

					if len(typeStack) == 0:
						break

	@classmethod
	def _checkForAbstractMethods(metacls, baseClasses: Tuple[type], members: Dict[str, Any]) -> Tuple[Dict[str, Callable], Dict[str, Any]]:
		"""
		Check if the current class contains abstract methods and return a tuple of them.

		These abstract methods might be inherited from any base-class. If there are inherited abstract methods, check if
		they are now implemented (overridden) by the current class that's right now constructed.

		:param baseClasses: The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:     The dictionary of members for the constructed class.
		:returns:           A tuple of abstract method's names.
		"""
		abstractMethods = {}
		if baseClasses:
			for baseClass in baseClasses:
				if hasattr(baseClass, "__abstractMethods__"):
					for key, value in baseClass.__abstractMethods__.items():
						abstractMethods[key] = value

			for base in baseClasses:
				for key, value in base.__dict__.items():
					if (key in abstractMethods and isinstance(value, FunctionType) and
						not (hasattr(value, "__abstract__") or hasattr(value, "__mustOverride__"))):
						def outer(method):
							@wraps(method)
							def inner(cls, *args, **kwargs):
								return method(cls, *args, **kwargs)

							return inner

						members[key] = outer(value)

		for memberName, member in members.items():
			if ((hasattr(member, "__abstract__") and member.__abstract__) or
					(hasattr(member, "__mustOverride__") and member.__mustOverride__)):
				abstractMethods[memberName] = member
			elif memberName in abstractMethods:
				del abstractMethods[memberName]

		return abstractMethods, members

	@staticmethod
	def _wrapNewMethodIfSingleton(newClass, singleton: bool) -> bool:
		"""
		If a class is a singleton, wrap the ``_new__`` method, so it returns a cached object, if a first object was created.

		Only the first object creation initializes the object.

		This implementation is threadsafe.

		:param newClass:  The newly constructed class for further modifications.
		:param singleton: If ``True``, the class allows only a single instance to exist.
		:returns:         ``True``, if the class is a singleton.
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
			newClass.__singletonInstanceCond__ = Condition()
			newClass.__singletonInstanceInit__ = True
			newClass.__singletonInstanceCache__ = None
			return True

		return False

	@staticmethod
	def _wrapNewMethodIfAbstract(newClass) -> bool:
		"""
		If the class has abstract methods, replace the ``_new__`` method, so it raises an exception.

		:param newClass:            The newly constructed class for further modifications.
		:returns:                   ``True``, if the class is abstract.
		:raises AbstractClassError: If the class is abstract and can't be instantiated.
		"""
		# Replace '__new__' by a variant to throw an error on not overridden methods
		if newClass.__abstractMethods__:
			oldnew = newClass.__new__
			if hasattr(oldnew, "__raises_abstract_class_error__"):
				oldnew = oldnew.__orig_func__

			@OriginalFunction(oldnew)
			@wraps(oldnew)
			def new(cls, *_, **__):
				raise AbstractClassError(f"""Class '{cls.__name__}' is abstract. The following methods: '{"', '".join(newClass.__abstractMethods__)}' need to be overridden in a derived class.""")

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
