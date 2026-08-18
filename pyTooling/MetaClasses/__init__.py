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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. hint::

   See :ref:`high-level help <META>` for explanations and usage examples.
"""
from functools  import wraps
from itertools  import chain
from sys        import version_info
from threading  import Condition
from types      import BuiltinFunctionType, FunctionType, MethodType
from typing     import Any, Tuple, List, Dict, Callable, Generator, Set, Iterator, Iterable, Union, NoReturn, Self
from typing     import Type, TypeVar, Generic, _GenericAlias, ClassVar, Optional as Nullable

from pyTooling.Exceptions import ToolingException
from pyTooling.Decorators import export, readonly
from pyTooling.Warning    import Warning, WarningCollector


__all__ = ["M"]

TAttr = TypeVar("TAttr")  # , bound='Attribute')
"""A type variable for :class:`~pyTooling.Attributes.Attribute`."""

TAttributeFilter = Union[TAttr, Iterable[TAttr], None]
"""A type hint for a predicate parameter that accepts either a single :class:`~pyTooling.Attributes.Attribute` or an
iterable of those."""


@export
class ExtendedTypeError(ToolingException):
	"""The exception is raised by the meta-class :class:`~pyTooling.Metaclasses.ExtendedType`."""


@export
class BaseClassWithoutSlotsError(ExtendedTypeError):
	"""
	This exception is raised when a class using ``__slots__`` inherits from at-least one base-class not using ``__slots__``.

	.. seealso::

	   * :ref:`Python data model for slots <slots>`
	   * :term:`Glossary entry __slots__ <__slots__>`
	"""


@export
class BaseClassWithNonEmptySlotsError(ExtendedTypeError):
	"""
	This exception is raised when a mixin-class uses slots, but Python prohibits slots.

	.. important::

	   To fulfill Python's requirements on slots, pyTooling uses slots only on the prinmary inheritance line.
	   Mixin-classes collect slots, which get materialized when the mixin-class (secondary inheritance lines) gets merged
	   into the primary inheritance line.
	"""


@export
class BaseClassIsNotAMixinError(ExtendedTypeError):
	"""
	This exception is raised when a class inherits from a secondary base-class that is not declared as a mixin.

	Only the primary inheritance line may carry a normal class; every further base-class needs ``mixin=True`` (or the
	:deco:`~pyTooling.MetaClasses.mixin` decorator), because that is what allows their slots to be merged.
	"""


@export
class DuplicateFieldInSlotsError(ExtendedTypeError):
	"""
	This exception is raised when a slot name is used multiple times within the inheritance hierarchy.
	"""


@export
class UnannotatedFieldWarning(Warning):
	"""
	A class declares a field that was assigned in the class body without a type annotation.

	An object field is annotated with its type, a class variable with :class:`~typing.ClassVar`. Without an annotation,
	:class:`ExtendedType` can't tell the two apart, and the field never becomes a slot.
	"""


@export
class IncompatibleMetaClassError(ExtendedTypeError):
	"""
	This exception is raised when a class decorated with :deco:`slotted`, :deco:`mixin` or :deco:`singleton` uses a
	meta-class that is neither :class:`type` nor derived from :class:`~pyTooling.MetaClasses.ExtendedType`.
	"""


@export
class AbstractClassError(ExtendedTypeError):
	"""
	This exception is raised, when a class contains methods marked with *abstractmethod* or *must-override*.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.abstractmethod`
	      |rarr| Mark a method as *abstract*.
	   :deco:`~pyTooling.MetaClasses.mustoverride`
	      |rarr| Mark a method as *must overrride*.
	   :exc:`~MustOverrideClassError`
	      |rarr| Exception raised, if a method is marked as *must-override*.
	"""


@export
class MustOverrideClassError(AbstractClassError):
	"""
	This exception is raised, when a class contains methods marked with *must-override*.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.abstractmethod`
	      |rarr| Mark a method as *abstract*.
	   :deco:`~pyTooling.MetaClasses.mustoverride`
	      |rarr| Mark a method as *must overrride*.
	   :exc:`~AbstractClassError`
	      |rarr| Exception raised, if a method is marked as *abstract*.
	"""


# """
# Metaclass that allows multiple dispatch of methods based on method signatures.
#
# .. seealso:
#
#    `Python Cookbook - Multiple dispatch with function annotations <https://GitHub.com/dabeaz/python-cookbook/blob/master/src/9/multiple_dispatch_with_function_annotations/example1.py?ts=2>`__
# """


M = TypeVar("M", bound=Callable)   #: A type variable for methods.
C = TypeVar("C", bound=type)       #: A type variable for classes.


def _recreateClass(cls: type, decoratorName: str, **options: bool) -> type:
	"""
	Recreate a class with :class:`ExtendedType` (or the class' own compatible meta-class) applying the given options.

	:param cls:                         Class to recreate.
	:param decoratorName:               Name of the calling decorator. It's used in the error message.
	:param options:                     Meta-class options like ``slots``, ``mixin`` or ``singleton``.
	:returns:                           The recreated class.
	:raises IncompatibleMetaClassError: If the class' meta-class is neither :class:`type`, nor derived from
	                                    :class:`ExtendedType`.
	"""
	if cls.__class__ is type:
		metacls = ExtendedType
	elif issubclass(cls.__class__, ExtendedType):
		metacls = cls.__class__
		for method in cls.__methods__:
			delattr(method, "__classobj__")
	else:
		metaClass = cls.__class__
		ex = IncompatibleMetaClassError(f"Class '{cls.__name__}' decorated with '@{decoratorName}' uses an incompatible meta-class.")
		ex.add_note(f"Meta-class is '{metaClass.__module__}.{metaClass.__name__}'.")
		ex.add_note(f"A decorated class must use 'type' or a meta-class derived from 'pyTooling.MetaClasses.ExtendedType'.")
		raise ex

	bases = tuple(base for base in cls.__bases__ if base is not object)
	slots = cls.__dict__["__slots__"] if "__slots__" in cls.__dict__ else tuple()
	members = {
		"__qualname__": cls.__qualname__
	}
	for key, value in cls.__dict__.items():
		if key not in slots:
			members[key] = value

	return metacls(cls.__name__, bases, members, **options)


@export
def slotted(cls):
	"""
	Class decorator recreating a class with slots derived from its annotated fields.

	It is the decorator form of ``metaclass=ExtendedType, slots=True``, for a class that shouldn't name the
	meta-class explicitly.

	:param cls:  The class to recreate.
	:returns:    The recreated class, using ``__slots__``.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.mixin`
	      |rarr| Recreate a class as a mixin-class.
	   :deco:`~pyTooling.MetaClasses.singleton`
	      |rarr| Recreate a class as a singleton.
	"""
	return _recreateClass(cls, "slotted", slots=True)


@export
def mixin(cls):
	"""
	Class decorator recreating a class as a mixin-class.

	A mixin-class collects its slots instead of materializing them; they are merged when the mixin joins a primary
	inheritance line.

	:param cls:  The class to recreate.
	:returns:    The recreated class, marked as a mixin.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.slotted`
	      |rarr| Recreate a class with slots.
	   :deco:`~pyTooling.MetaClasses.singleton`
	      |rarr| Recreate a class as a singleton.
	"""
	return _recreateClass(cls, "mixin", mixin=True)


@export
def singleton(cls):
	"""
	Class decorator recreating a class as a singleton.

	Every instantiation of the decorated class returns the same object, including its state.

	:param cls:  The class to recreate.
	:returns:    The recreated class, marked as a singleton.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.slotted`
	      |rarr| Recreate a class with slots.
	   :deco:`~pyTooling.MetaClasses.mixin`
	      |rarr| Recreate a class as a mixin-class.
	"""
	return _recreateClass(cls, "singleton", singleton=True)


@export
def abstractclass(cls: C) -> C:
	"""
	Mark a class as *abstract*, so it cannot be instantiated, although it has no abstract method.

	Some classes exist only to be derived from - a base-class collecting shared infrastructure, for instance - and
	have nothing to mark with :deco:`abstractmethod`. This decorator says so directly: it sets ``__abstractClass__``
	on the class and recomputes ``__isAbstract__``, which replaces ``__new__`` by a method raising an
	:exc:`~pyTooling.Exceptions.AbstractClassError`.

	The marker belongs to the decorated class alone. :class:`ExtendedType` clears it on every class it creates, so a
	derived class is concrete again unless it is decorated itself or inherits an abstract method.

	.. warning::

	   This decorator needs meta-class :class:`~pyTooling.MetaClasses.ExtendedType`, which does the computation.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      @abstractclass
	      class Base(metaclass=ExtendedType):
	        '''This class needs to be inherited.'''

	:param cls:             Class that is marked as *abstract*.
	:returns:               The same class, marked and with its abstractness recomputed.
	:raises AttributeError: If the class was not created by :class:`ExtendedType`, because nothing would compute it.

	.. seealso::

	   :exc:`~pyTooling.Exceptions.AbstractClassError`
	      |rarr| The exception raised when a still abstract class gets instantiated.
	   :deco:`~pyTooling.MetaClasses.abstractmethod`
	      |rarr| Mark a method as *abstract* and raise a :exc:`NotImplementedError` when called.
	   :deco:`~pyTooling.MetaClasses.mustoverride`
	      |rarr| Mark a method as *mustoverride* (minimal implementation, but can be called).
	   :deco:`~pyTooling.Decorators.notimplemented`
	      |rarr| Mark a *method* as not implemented and raise a :exc:`NotImplementedError`.
	"""
	if not isinstance(cls, ExtendedType):
		ex = AttributeError(f"Class '{cls.__name__}' is not created by meta-class 'ExtendedType'.")
		ex.add_note(f"Add 'metaclass=ExtendedType' to the class definition, so abstractness is computed.")
		raise ex

	cls.__abstractClass__ = True

	if not cls.__isAbstract__:
		cls.__isAbstract__ = ExtendedType._wrapNewMethodIfAbstract(cls)

	return cls


@export
def abstractmethod(method: M) -> M:
	"""
	Mark a method as *abstract* and replace the implementation with a new method raising a :exc:`NotImplementedError`.

	The original method is stored in ``<method>.__wrapped__`` and it's doc-string is copied to the replacing method. In
	additional field ``<method>.__abstract__`` is added.

	.. warning::

	   This decorator should be used in combination with meta-class :class:`~pyTooling.Metaclasses.ExtendedType`.
	   Otherwise, an abstract class itself doesn't throw a :exc:`~pyTooling.Exceptions.AbstractClassError` at
	   instantiation.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      class Data(mataclass=ExtendedType):
	        @abstractmethod
	        def method(self) -> bool:
	          '''This method needs to be implemented.'''

	:param method: Method that is marked as *abstract*.
	:returns:      Replacement method, which raises a :exc:`NotImplementedError`.

	.. seealso::

	   :exc:`~pyTooling.Exceptions.AbstractClassError`
	      |rarr| The exception raised when a still abstract class gets instantiated.
	   :deco:`~pyTooling.MetaClasses.abstractclass`
	      |rarr| Mark a class as *abstract*.
	   :deco:`~pyTooling.MetaClasses.mustoverride`
	      |rarr| Mark a method as *mustoverride* (minimal implementation, but can be called).
	   :deco:`~pyTooling.Decorators.notimplemented`
	      |rarr| Mark a *method* as not implemented and raise a :exc:`NotImplementedError`.
	"""
	@wraps(method)
	def func(self) -> NoReturn:
		raise NotImplementedError(f"Method '{method.__name__}' is abstract and needs to be overridden in a derived class.")

	func.__abstract__ = True
	return func


@export
def mustoverride(method: M) -> M:
	"""
	Mark a method as *must-override*.

	The returned function is the original function, but with an additional field ``<method>.____mustOverride__``, so a
	meta-class can identify a *must-override* method and raise an error. Such an error is not raised if the method is
	overridden by an inheriting class.

	A *must-override* methods can offer a partial implementation, which is called via ``super()...``.

	.. warning::

	   This decorator needs to be used in combination with meta-class :class:`~pyTooling.Metaclasses.ExtendedType`.
	   Otherwise, an abstract class itself doesn't throw a :exc:`~pyTooling.Exceptions.MustOverrideClassError` at
	   instantiation.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      class Data(mataclass=ExtendedType):
	        @mustoverride
	        def method(self):
	          '''This is a very basic implementation.'''

	:param method: Method that is marked as *must-override*.
	:returns:      Same method, but with additional ``<method>.__mustOverride__`` field.

	.. seealso::

	   :exc:`~pyTooling.Exceptions.MustOverrideClassError`
	      |rarr| The exception raised when a class gets instantiated still containing *mustoverride* methods.
	   :deco:`~pyTooling.MetaClasses.abstractclass`
	      |rarr| Mark a class as *abstract*.
	   :deco:`~pyTooling.MetaClasses.abstractmethod`
	      |rarr| Mark a method as *abstract* and raise a :exc:`NotImplementedError` when called.
	   :deco:`~pyTooling.Decorators.notimplemented`
	      |rarr| Mark a *method* as not implemented and raise a :exc:`NotImplementedError`.
	"""
	method.__mustOverride__ = True
	return method


# @export
# def overloadable(method: M) -> M:
# 	method.__overloadable__ = True
# 	return method


# @export
# class DispatchableMethod:
# 	"""Represents a single multimethod."""
#
# 	_methods: Dict[Tuple, Callable]
# 	__name__: str
# 	__slots__ = ("_methods", "__name__")
#
# 	def __init__(self, name: str) -> None:
# 		self.__name__ = name
# 		self._methods = {}
#
# 	def __call__(self, *args: Any):
# 		"""Call a method based on type signature of the arguments."""
# 		types = tuple(type(arg) for arg in args[1:])
# 		meth = self._methods.get(types, None)
# 		if meth:
# 			return meth(*args)
# 		else:
# 			raise TypeError(f"No matching method for types {types}.")
#
# 	def __get__(self, instance, cls) -> Self:
# 		"""Descriptor method needed to make calls work in a class."""
# 		if instance is not None:
# 			return MethodType(self, instance)
# 		else:
# 			return self
#
# 	def register(self, method: Callable) -> None:
# 		"""Register a new method as a dispatchable."""
#
# 		# Build a signature from the method's type annotations
# 		sig = signature(method)
# 		types: List[Type] = []
#
# 		for name, parameter in sig.parameters.items():
# 			if name == "self":
# 				continue
#
# 			if parameter.annotation is Parameter.empty:
# 				raise TypeError(f"Parameter '{name}' in method '{method.__name__}' must be annotated with a type.")
#
# 			if not isinstance(parameter.annotation, type):
# 				raise TypeError(f"Parameter '{name}' in method '{method.__name__}' annotation must be a type.")
#
# 			if parameter.default is not Parameter.empty:
# 				self._methods[tuple(types)] = method
#
# 			types.append(parameter.annotation)
#
# 		self._methods[tuple(types)] = method


# @export
# class DispatchDictionary(dict):
# 	"""Special dictionary to build dispatchable methods in a metaclass."""
#
# 	def __setitem__(self, key: str, value: Any):
# 		if callable(value) and key in self:
# 			# If key already exists, it must be a dispatchable method or callable
# 			currentValue = self[key]
# 			if isinstance(currentValue, DispatchableMethod):
# 				currentValue.register(value)
# 			else:
# 				dispatchable = DispatchableMethod(key)
# 				dispatchable.register(currentValue)
# 				dispatchable.register(value)
#
# 				super().__setitem__(key, dispatchable)
# 		else:
# 			super().__setitem__(key, value)


@export
class ExtendedType(type):
	"""
	An updates meta-class to construct new classes with an extended feature set.

	.. todo:: META::ExtendedType Needs documentation.
	.. todo:: META::ExtendedType allow __dict__ and __weakref__ if slotted is enabled

	.. rubric:: Features:

	* Store object members more efficiently in ``__slots__`` instead of ``_dict__``.

	  * Implement ``__slots__`` only on primary inheritance line.
	  * Collect class variables on secondary inheritance lines (mixin-classes) and defer implementation as ``__slots__``.
	  * Handle object state exporting and importing for slots (:mod:`pickle` support) via ``__getstate__``/``__setstate__``.

	* Allow only a single instance to be created (:term:`singleton`). |br|
	  Further instantiations will return the previously create instance (identical object).
	* Define methods as :term:`abstract <abstract method>` or :term:`must-override <mustoverride method>` and prohibit
	  instantiation of :term:`abstract classes <abstract class>`.

	.. #* Allow method overloading and dispatch overloads based on argument signatures.

	.. rubric:: Added class fields:

	:__slotted__:                True, if class uses `__slots__`.
	:__allSlots__:               Set of class fields stored in slots for all classes in the inheritance hierarchy.
	:__slots__:                  Tuple of class fields stored in slots for current class in the inheritance hierarchy. |br|
	                             See :pep:`253` for details.
	:__isMixin__:                True, if class is a mixin-class
	:__mixinSlots__:             List of collected slots from secondary inheritance hierarchy (mixin hierarchy).
	:__methods__:                List of methods.
	:__methodsWithAttributes__:  List of methods with pyTooling attributes.
	:__abstractMethods__:        List of abstract methods, which need to be implemented in the next class hierarchy levels.
	:__abstractClass__:          True, if this class was decorated with :deco:`abstractclass`.
	:__isAbstract__:             True, if class is abstract.
	:__isSingleton__:            True, if class is a singleton
	:__singletonInstanceCond__:  Condition variable to protect the singleton creation.
	:__singletonInstanceInit__:  Singleton is initialized.
	:__singletonInstanceCache__: The singleton object, once created.
	:__pyattr__:                 List of class attributes.

	.. rubric:: Added class properties:

	:HasClassAttributes:  Read-only property to check if the class has Attributes.
	:HasMethodAttributes: Read-only property to check if the class has methods with Attributes.

	.. rubric:: Added methods:

	If slots are used, the following methods are added to support :mod:`pickle`:

	:__getstate__: Export an object's state for serialization. |br|
	               See :pep:`307` for details.
	:__setstate__: Import an object's state for deserialization. |br|
	               See :pep:`307` for details.

	.. rubric:: Modified ``__new__`` method:

	If class is a singleton, ``__new__`` will be replaced by a wrapper method. This wrapper is marked with ``__singleton_wrapper__``.

	If class is abstract, ``__new__`` will be replaced by a method raising an exception. This replacement is marked with ``__raises_abstract_class_error__``.

	.. rubric:: Modified ``__init__`` method:

	If class is a singleton, ``__init__`` will be replaced by a wrapper method. This wrapper is marked by ``__singleton_wrapper__``.

	.. rubric:: Modified abstract methods:

	If a method is abstract, its marked with ``__abstract__``. |br|
	If a method is must override, its marked with ``__mustOverride__``.
	"""

	# @classmethod
	# def __prepare__(cls, className, baseClasses, slots: bool = False, mixin: bool = False, singleton: bool = False):
	# 	return DispatchDictionary()

	def __new__(
		self,
		className: str,
		baseClasses: Tuple[type],
		members: Dict[str, Any],
		slots: bool = False,
		mixin: bool = False,
		singleton: bool = False
	) -> Self:
		"""
		Construct a new class using this :term:`meta-class`.

		:param className:       The name of the class to construct.
		:param baseClasses:     The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:         The dictionary of members for the constructed class.
		:param slots:           If true, store object attributes in :term:`__slots__ <slots>` instead of ``__dict__``.
		:param mixin:           If true, make the class a :term:`Mixin-Class`.
		                        If false, create slots if ``slots`` is true.
		                        If none, preserve behavior of primary base-class.
		:param singleton:       If true, make the class a :term:`Singleton`.
		:returns:               The new class.
		:raises AttributeError: If base-class has no '__slots__' attribute.
		:raises AttributeError: If slot already exists in base-class.
		"""
		from pyTooling.Attributes import ATTRIBUTES_MEMBER_NAME, AttributeScope

		# Inherit 'slots' feature from primary base-class
		if len(baseClasses) > 0:
			primaryBaseClass = baseClasses[0]
			if isinstance(primaryBaseClass, self):
				slots = primaryBaseClass.__slotted__

		# Compute slots and mixin-slots from annotated fields as well as class- and object-fields with initial values.
		classFields, objectFields = self._computeSlots(className, baseClasses, members, slots, mixin)

		# Compute abstract methods
		abstractMethods, members = self._checkForAbstractMethods(baseClasses, members)

		# Create a new class
		newClass = type.__new__(self, className, baseClasses, members)

		# Apply class fields
		for fieldName, typeAnnotation in classFields.items():
			setattr(newClass, fieldName, typeAnnotation)

		# Search in inheritance tree for abstract methods
		newClass.__abstractMethods__ = abstractMethods

		newClass.__abstractClass__ = False
		newClass.__isAbstract__ =    self._wrapNewMethodIfAbstract(newClass)
		newClass.__isSingleton__ =   self._wrapNewMethodIfSingleton(newClass, singleton)

		if slots:
			# If slots are used, implement __getstate__/__setstate__ API to support serialization using pickle.
			if "__getstate__" not in members:
				def __getstate__(self) -> Dict[str, Any]:
					try:
						return {slotName: getattr(self, slotName) for slotName in self.__allSlots__}
					except AttributeError as ex:
						raise ExtendedTypeError(f"Unassigned field '{ex.name}' in object '{self}' of type '{self.__class__.__name__}'.") from ex

				newClass.__getstate__ = __getstate__

			if "__setstate__" not in members:
				def __setstate__(self, state: Dict[str, Any]) -> None:
					if self.__allSlots__ !=  (slots := set(state.keys())):
						if len(diff := self.__allSlots__.difference(slots)) > 0:
							raise ExtendedTypeError(f"""Missing fields in parameter 'state': '{"', '".join(diff)}'""")     # WORKAROUND: Python <3.12
						else:
							diff = slots.difference(self.__allSlots__)
							raise ExtendedTypeError(f"""Unexpected fields in parameter 'state': '{"', '".join(diff)}'""")  # WORKAROUND: Python <3.12

					for slotName, value in state.items():
						setattr(self, slotName, value)

				newClass.__setstate__ = __setstate__

		# Check for inherited class attributes
		attributes = []
		setattr(newClass, ATTRIBUTES_MEMBER_NAME, attributes)
		for base in baseClasses:
			if hasattr(base, ATTRIBUTES_MEMBER_NAME):
				pyAttr = getattr(base, ATTRIBUTES_MEMBER_NAME)
				for att in pyAttr:
					if AttributeScope.Class in att.Scope:
						attributes.append(att)
						att.__class__._classes.append(newClass)

		# Check methods for attributes
		methods, methodsWithAttributes = self._findMethods(newClass, baseClasses, members)

		# Add new fields for found methods
		newClass.__methods__ = tuple(methods)
		newClass.__methodsWithAttributes__ = tuple(methodsWithAttributes)

		# Additional methods on a class
		def GetMethodsWithAttributes(self, predicate: Nullable[TAttributeFilter[TAttr]] = None) -> Dict[Callable, Tuple["Attribute", ...]]:
			"""
			Return the class' methods that carry at least one matching attribute.

			:param predicate:   An attribute class, an iterable of attribute classes, or ``None`` to accept every attribute.
			:returns:           Dictionary of methods and the matching attributes attached to them.
			:raises ValueError: If an element of parameter 'predicate' is not a sub-class of :class:`~pyTooling.Attributes.Attribute`.
			:raises ValueError: If parameter 'predicate' is neither an attribute class nor an iterable of those.
			"""
			from pyTooling.Attributes import Attribute

			if predicate is None:
				predicate = Attribute
			elif isinstance(predicate, Iterable):
				for attribute in predicate:
					if not issubclass(attribute, Attribute):
						raise ValueError(f"Parameter 'predicate' contains an element which is not a sub-class of 'Attribute'.")

				predicate = tuple(predicate)
			elif not issubclass(predicate, Attribute):
				raise ValueError(f"Parameter 'predicate' is not a sub-class of 'Attribute'.")

			methodAttributePairs = {}
			for method in newClass.__methodsWithAttributes__:
				matchingAttributes = []
				for attribute in method.__pyattr__:
					if isinstance(attribute, predicate):
						matchingAttributes.append(attribute)

				if len(matchingAttributes) > 0:
					methodAttributePairs[method] = tuple(matchingAttributes)

			return methodAttributePairs

		newClass.GetMethodsWithAttributes = classmethod(GetMethodsWithAttributes)
		GetMethodsWithAttributes.__qualname__ = f"{className}.{GetMethodsWithAttributes.__name__}"

		# GetMethods(predicate) -> dict[method, list[attribute]] / generator
		# GetClassAtrributes -> list[attributes] / generator
		# MethodHasAttributes(predicate) -> bool
		# GetAttribute

		return newClass

	@classmethod
	def _findMethods(
		self,
		newClass:    "ExtendedType",
		baseClasses: Tuple[type],
		members:     Dict[str, Any]
	) -> Tuple[List[MethodType], List[MethodType]]:
		"""
		Find methods and methods with :mod:`pyTooling.Attributes`.

		.. todo::

		   Describe algorithm.

		:param newClass:    Newly created class instance.
		:param baseClasses: The tuple of :term:`base-classes <base-class>` the class is derived from.
		:param members:     Members of the new class.
		:returns:           A 2-tuple of all methods and those methods carrying at least one attribute.
		:raises TypeError:  If a member is neither a method nor a class, so it can't be searched for methods.
		"""
		from pyTooling.Attributes import Attribute

		# Embedded bind function due to circular dependencies.
		def bind(instance: object, func: FunctionType, methodName: Nullable[str] = None):
			if methodName is None:
				methodName = func.__name__

			boundMethod = func.__get__(instance, instance.__class__)
			setattr(instance, methodName, boundMethod)

			return boundMethod

		methods = []
		methodsWithAttributes = []
		attributeIndex = {}

		for base in baseClasses:
			if hasattr(base, "__methodsWithAttributes__"):
				methodsWithAttributes.extend(base.__methodsWithAttributes__)

		for memberName, member in members.items():
			if isinstance(member, FunctionType):
				method = newClass.__dict__[memberName]
				if hasattr(method, "__classobj__") and getattr(method, "__classobj__") is not newClass:
					raise TypeError(f"Method '{memberName}' is used by multiple classes: {method.__classobj__} and {newClass}.")
				else:
					setattr(method, "__classobj__", newClass)

				def GetAttributes(inst: Any, predicate: Nullable[Type[Attribute]] = None) -> Tuple[Attribute, ...]:
					results = []
					try:
						for attribute in inst.__pyattr__:  # type: Attribute
							if isinstance(attribute, predicate):
								results.append(attribute)
						return tuple(results)
					except AttributeError:
						return tuple()

				method.GetAttributes = bind(method, GetAttributes)
				methods.append(method)

				# print(f"  convert function: '{memberName}' to method")
				# print(f"    {member}")
				if "__pyattr__" in member.__dict__:
					attributes = member.__pyattr__           # type: List[Attribute]
					if isinstance(attributes, list) and len(attributes) > 0:
						methodsWithAttributes.append(member)
						for attribute in attributes:
							attribute._functions.remove(method)
							attribute._methods.append(method)

							# print(f"    attributes: {attribute.__class__.__name__}")
							if attribute not in attributeIndex:
								attributeIndex[attribute] = [member]
							else:
								attributeIndex[attribute].append(member)
				# else:
				# 	print(f"    But has no attributes.")
			# else:
			# 	print(f"  ??        {memberName}")
		return methods, methodsWithAttributes

	@classmethod
	def _getAnnotations(metacls, members: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Return the type annotations declared in a class body.

		.. important::

		   Python 3.14 (:pep:`649`) no longer fills ``__annotations__`` while the class body is executed, but installs an
		   ``__annotate_func__`` instead. The :mod:`annotationlib` module needed to evaluate that function doesn't exist on
		   older Python versions, therefore both mechanisms are supported.

		:param members: Dictionary of class members.
		:returns:       Dictionary of annotated field names and their type annotations. Empty, if the class body declared
		                no annotations.
		"""
		if "__annotations__" in members:
			# WORKAROUND: LEGACY SUPPORT Python <= 3.13
			#   Accessing annotations was changed in Python 3.14.
			#   The necessary 'annotationlib' is not available for older Python versions.
			return members["__annotations__"]
		elif version_info >= (3, 14) and (annotate := members.get("__annotate_func__", None)) is not None:
			from annotationlib import Format
			return annotate(Format.VALUE)
		else:
			return {}

	@classmethod
	def _isClassVariable(metacls, typeAnnotation: Any) -> bool:
		"""
		Check if a type annotation declares a class variable.

		:param typeAnnotation: The type annotation to check.
		:returns:              ``True``, if the annotation is a :class:`~typing.ClassVar`.
		"""
		return isinstance(typeAnnotation, _GenericAlias) and typeAnnotation.__origin__ is ClassVar

	@classmethod
	def _isField(metacls, member: Any) -> bool:
		"""
		Check if a class member is a field, so a type annotation is expected for it.

		Methods, nested classes, properties and any other descriptor carry their type information in their signature or
		in their own declaration, therefore they aren't fields.

		:param member: The class member to check.
		:returns:      ``True``, if the member is a field.
		"""
		if isinstance(member, (FunctionType, MethodType, BuiltinFunctionType, classmethod, staticmethod, property, type)):
			return False

		# Any descriptor (e.g. a custom property implementation) declares its own type information.
		return not (hasattr(member, "__get__") or hasattr(member, "__set__"))

	@classmethod
	def _checkForUnannotatedFields(metacls, className: str, members: Dict[str, Any], annotations: Dict[str, Any]) -> None:
		"""
		Report fields that were assigned in the class body without a type annotation.

		Every field should carry type information: an object field is annotated with its type, a class variable with
		``ClassVar[...]``. Without an annotation, :class:`ExtendedType` can't tell the two apart - an un-annotated
		assignment never becomes a slot and silently stays a class attribute.

		.. important::

		   This is reported as a :class:`~pyTooling.Warning.Warning`, so it needs a
		   :class:`~pyTooling.Warning.WarningCollector` somewhere up the call-hierarchy to be observed. Importing a module
		   with un-annotated fields doesn't fail.

		:param className:   The name of the class to construct.
		:param members:     Dictionary of class members.
		:param annotations: Dictionary of annotated field names and their type annotations.
		"""
		unannotatedFields = [
			fieldName
			for fieldName, member in members.items()
			if not (fieldName.startswith("__") and fieldName.endswith("__"))
				and fieldName not in annotations
				and metacls._isField(member)
		]

		if len(unannotatedFields) > 0:
			fieldNames = "', '".join(unannotatedFields)
			WarningCollector.Raise(
				UnannotatedFieldWarning(f"Class '{className}' declares {len(unannotatedFields)} field(s) without a type annotation."),
				notes=(
					f"Field(s) without a type annotation: '{fieldNames}'.",
					f"Annotate a class variable as 'ClassVar[...]' or an object field with its type.",
				)
			)

	@classmethod
	def _computeSlots(
		self,
		className:   str,
		baseClasses: Tuple[type],
		members:     Dict[str, Any],
		slots:       bool,
		mixin:       bool
	) -> Tuple[Dict[str, Any], Dict[str, Any]]:
		"""
		Compute which field are listed in __slots__ and which need to be initialized in an instance or class.

		.. todo::

		   Describe algorithm.

		:param className:                   The name of the class to construct.
		:param baseClasses:                 Tuple of base-classes.
		:param members:                     Dictionary of class members.
		:param slots:                       True, if the class should setup ``__slots__``.
		:param mixin:                       True, if the class should behave as a mixin-class.
		:returns:                           A 2-tuple with a dictionary of class members and object members.
		:raises AttributeError:             If a field's annotation refers to a name that can't be resolved.
		:raises BaseClassWithoutSlotsError: If a base-class doesn't use slots, which Python requires for a slotted class.
		"""
		# Compute which field are listed in __slots__ and which need to be initialized in an instance or class.
		slottedFields = []
		classFields =   {}
		objectFields =  {}
		annotations: Dict[str, Any] = self._getAnnotations(members)
		if slots or mixin:
			# If slots are used, all base classes must use __slots__.
			for baseClass in self._iterateBaseClasses(baseClasses):
				# Exclude object as a special case
				if baseClass is object or baseClass is Generic:
					continue

				if not hasattr(baseClass, "__slots__"):
					ex = BaseClassWithoutSlotsError(f"Base-classes '{baseClass.__name__}' doesn't use '__slots__'.")
					ex.add_note(f"All base-classes of a class using '__slots__' must use '__slots__' itself.")
					raise ex

			# Non-empty __slots__ on secondary base-classes are rejected by _aggregateMixinSlots below.

			# Copy all field names from primary base-class' __slots__, which are later needed for error checking.
			inheritedSlottedFields = {}
			if len(baseClasses) > 0:
				for base in reversed(baseClasses[0].mro()):
					# Exclude object as a special case
					if base is object or base is Generic:
						continue

					for annotation in base.__slots__:
						inheritedSlottedFields[annotation] = base

			# When adding annotated fields to slottedFields, check if name was not used in inheritance hierarchy.
			for fieldName, typeAnnotation in annotations.items():
				if fieldName in inheritedSlottedFields:
					cls = inheritedSlottedFields[fieldName]
					raise AttributeError(f"Slot '{fieldName}' declared in class '{className}' already exists in base-class '{cls.__module__}.{cls.__name__}'.")

				# A ClassVar is never a slot, with or without an initial value.
				# * If it has an initial value, copy field and initial value to classFields dictionary and remove field from members.
				# * Otherwise it's a forward declaration and derived classes assign the actual value.
				isClassVariable = self._isClassVariable(typeAnnotation)
				hasInitialValue = fieldName in members
				if isClassVariable:
					if hasInitialValue:
						classFields[fieldName] = members[fieldName]
						del members[fieldName]

				# If an annotated field has an initial value
				# * copy field and initial value to objectFields dictionary
				# * remove field from members
				elif hasInitialValue:
					slottedFields.append(fieldName)
					objectFields[fieldName] = members[fieldName]
					del members[fieldName]
				else:
					slottedFields.append(fieldName)

			mixinSlots = self._aggregateMixinSlots(className, baseClasses)

			# A member assigned in the class body without a type annotation stays a class attribute. If it carries the name
			# of a slot, that class attribute shadows the slot's descriptor and the field becomes read-only on instances.
			# Report it here instead of letting the first assignment fail with a bare AttributeError.
			shadowedSlots = {**inheritedSlottedFields, **{fieldName: None for fieldName in mixinSlots}}
			for fieldName in shadowedSlots.keys() & members.keys():
				ex = DuplicateFieldInSlotsError(f"Slot '{fieldName}' is shadowed by a class member in class '{className}'.")
				if (baseClass := shadowedSlots[fieldName]) is not None:
					ex.add_note(f"Slot '{fieldName}' is declared in base-class '{baseClass.__module__}.{baseClass.__name__}'.")
					ex.add_note(f"An assignment without a type annotation creates a class attribute, which hides the slot's descriptor.")
					ex.add_note(f"Reading the field works, but assigning it on an instance raises an AttributeError.")
				else:
					ex.add_note(f"Slot '{fieldName}' is contributed by a mixin-class and materialized in this class' '__slots__'.")
					ex.add_note(f"Python doesn't allow a name to be listed in '__slots__' and assigned in the class body.")
				ex.add_note(f"Annotate it as 'ClassVar[...]' to declare a class variable, or remove the assignment.")
				raise ex
		else:
			# When adding annotated fields to slottedFields, check if name was not used in inheritance hierarchy.
			for fieldName, typeAnnotation in annotations.items():
				# If annotated field is a ClassVar, and it has an initial value
				# * copy field and initial value to classFields dictionary
				# * remove field from members
				if self._isClassVariable(typeAnnotation) and fieldName in members:
					classFields[fieldName] = members[fieldName]
					del members[fieldName]

		self._checkForUnannotatedFields(className, members, annotations)

		if mixin:
			mixinSlots.extend(slottedFields)
			members["__slotted__"] = True
			members["__slots__"] = tuple()
			members["__allSlots__"] = set()
			members["__isMixin__"] = True
			members["__mixinSlots__"] = tuple(mixinSlots)
		elif slots:
			slottedFields.extend(mixinSlots)
			members["__slotted__"] = True
			members["__slots__"] = tuple(slottedFields)
			members["__allSlots__"] = set(chain(slottedFields, inheritedSlottedFields.keys()))
			members["__isMixin__"] = False
			members["__mixinSlots__"] = tuple()
		else:
			members["__slotted__"] = False
			# NO     __slots__
			# members["__allSlots__"] = set()
			members["__isMixin__"] = False
			members["__mixinSlots__"] = tuple()
		return classFields, objectFields

	@classmethod
	def _aggregateMixinSlots(self, className: str, baseClasses: Tuple[type]) -> List[str]:
		"""
		Aggregate slot names requested by mixin-base-classes.

		.. todo::

		   Describe algorithm.

		:param className:                        The name of the class to construct.
		:param baseClasses:                      The tuple of :term:`base-classes <base-class>` the class is derived from.
		:returns:                                A list of slot names.
		:raises BaseClassWithNonEmptySlotsError: If a mixin-class uses non-empty slots, which Python doesn't allow on a
		                                         secondary inheritance line.
		"""
		mixinSlots = []
		if len(baseClasses) > 0:
			# If class has base-classes ensure only the primary inheritance path uses slots and all secondary inheritance
			# paths have an empty slots tuple. Otherwise, raise a BaseClassWithNonEmptySlotsError.
			inheritancePaths = [path for path in self._iterateBaseClassPaths(baseClasses)]
			primaryInharitancePath: Set[type] = set(inheritancePaths[0])
			for typePath in inheritancePaths[1:]:
				for t in typePath:
					if hasattr(t, "__slots__") and len(t.__slots__) != 0 and t not in primaryInharitancePath:
						ex = BaseClassWithNonEmptySlotsError(f"Base-class '{t.__name__}' has non-empty __slots__ and can't be used as a direct or indirect base-class for '{className}'.")
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
				if isinstance(baseClass, _GenericAlias) and baseClass.__origin__ is Generic:
					pass
				elif baseClass.__class__ is self and baseClass.__isMixin__:
					mixinSlots.extend(baseClass.__mixinSlots__)
				elif hasattr(baseClass, "__mixinSlots__"):
					mixinSlots.extend(baseClass.__mixinSlots__)

		return mixinSlots

	@classmethod
	def _iterateBaseClasses(metacls, baseClasses: Tuple[type]) -> Generator[type, None, None]:
		"""
		Return a generator to iterate (visit) all base-classes ...

		.. todo::

		   Describe iteration order.

		:param baseClasses: The tuple of :term:`base-classes <base-class>` the class is derived from.
		:returns:           Generator to iterate all base-classes.
		"""
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

		:param baseClasses: The tuple of :term:`base-classes <base-class>` the class is derived from.
		:returns:           Generator to iterate all inheritance paths. |br|
		                    An inheritance path is a tuple of types (base-classes).
		"""
		if len(baseClasses) == 0:
			return

		typeStack:     List[type] =           list()
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
			# Aggregate all abstract methods from all base-classes.
			for baseClass in baseClasses:
				if hasattr(baseClass, "__abstractMethods__"):
					abstractMethods.update(baseClass.__abstractMethods__)

			for base in baseClasses:
				for memberName, member in base.__dict__.items():
					if (memberName in abstractMethods and isinstance(member, FunctionType) and
						not (hasattr(member, "__abstract__") or hasattr(member, "__mustOverride__"))):
						def outer(method):
							@wraps(method)
							def inner(cls, *args: Any, **kwargs: Any):
								return method(cls, *args, **kwargs)

							return inner

						members[memberName] = outer(member)

		# Check if methods are marked:
		# * If so, add them to list of abstract methods
		# * If not, method is now implemented and removed from list
		for memberName, member in members.items():
			if callable(member):
				if ((hasattr(member, "__abstract__") and member.__abstract__) or
						(hasattr(member, "__mustOverride__") and member.__mustOverride__)):
					abstractMethods[memberName] = member
				elif memberName in abstractMethods:
					del abstractMethods[memberName]

		return abstractMethods, members

	@classmethod
	def _wrapNewMethodIfSingleton(metacls, newClass, singleton: bool) -> bool:
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
				oldnew = oldnew.__wrapped__

			oldinit = newClass.__init__
			if hasattr(oldinit, "__singleton_wrapper__"):
				oldinit = oldinit.__wrapped__

			@wraps(oldnew)
			def singleton_new(cls, *args: Any, **kwargs: Any):
				with cls.__singletonInstanceCond__:
					if cls.__singletonInstanceCache__ is None:
						obj = oldnew(cls, *args, **kwargs)
						cls.__singletonInstanceCache__ = obj
					else:
						obj = cls.__singletonInstanceCache__

				return obj

			@wraps(oldinit)
			def singleton_init(self, *args: Any, **kwargs: Any):
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

			singleton_new.__singleton_wrapper__ = True
			singleton_init.__singleton_wrapper__ = True

			newClass.__new__ = singleton_new
			newClass.__init__ = singleton_init
			newClass.__singletonInstanceCond__ = Condition()
			newClass.__singletonInstanceInit__ = True
			newClass.__singletonInstanceCache__ = None
			return True

		return False

	@classmethod
	def _wrapNewMethodIfAbstract(metacls, newClass) -> bool:
		"""
		If the class is marked ``__abstractClass__`` or has abstract methods, replace the ``_new__`` method, so it
		raises an exception.

		:param newClass:            The newly constructed class for further modifications.
		:returns:                   ``True``, if the class is abstract.
		:raises AbstractClassError: If the class is abstract and can't be instantiated.
		:raises Exception:          If a singleton wrapper was found around a method raising
		                            :exc:`AbstractClassError`, which is not handled yet.
		"""
		# Replace '__new__' by a variant to throw an error on not overridden methods
		if newClass.__abstractClass__ or len(newClass.__abstractMethods__) > 0:
			oldnew = newClass.__new__
			if hasattr(oldnew, "__raises_abstract_class_error__"):
				oldnew = oldnew.__wrapped__

			@wraps(oldnew)
			def abstract_new(cls, *_, **__):
				if len(newClass.__abstractMethods__) > 0:
					raise AbstractClassError(f"""Class '{cls.__name__}' is abstract. The following methods: '{"', '".join(newClass.__abstractMethods__)}' need to be overridden in a derived class.""")
				else:
					raise AbstractClassError(f"Class '{cls.__name__}' is abstract and needs to be derived.")

			abstract_new.__raises_abstract_class_error__ = True

			newClass.__new__ = abstract_new
			return True

		# Handle classes which are not abstract, especially derived classes, if not abstract anymore
		else:
			# skip intermediate 'new' function if class isn't abstract anymore
			try:
				if newClass.__new__.__raises_abstract_class_error__:
					origNew = newClass.__new__.__wrapped__

					# WORKAROUND: __new__ checks tp_new and implements different behavior
					#  Bugreport: https://github.com/python/cpython/issues/105888
					if origNew is object.__new__:
						@wraps(object.__new__)
						def wrapped_new(inst, *_, **__):
							return object.__new__(inst)

						newClass.__new__ = wrapped_new
					else:
						newClass.__new__ = origNew
				elif newClass.__new__.__isSingleton__:
					raise Exception(f"Found a singleton wrapper around an AbstractError raising method. This case is not handled yet.")
			except AttributeError as ex:
				if ex.name != "__raises_abstract_class_error__":
					raise ex

			return False

	# Additional properties and methods on a class
	@readonly
	def HasClassAttributes(self) -> bool:
		"""
		Read-only property to check if the class has Attributes (:attr:`__pyattr__`).

		:returns: ``True``, if the class has Attributes.
		"""
		try:
			return len(self.__pyattr__) > 0
		except AttributeError:
			return False

	@readonly
	def HasMethodAttributes(self) -> bool:
		"""
		Read-only property to check if the class has methods with Attributes (:attr:`__methodsWithAttributes__`).

		:returns: ``True``, if the class has any method with Attributes.
		"""
		try:
			return len(self.__methodsWithAttributes__) > 0
		except AttributeError:
			return False


@export
class SlottedObject(metaclass=ExtendedType, slots=True):
	"""Classes derived from this class will store all members in ``__slots__``."""
