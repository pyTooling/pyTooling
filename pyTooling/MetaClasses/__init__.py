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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
# from inspect    import signature, Parameter
from threading  import Condition
from types      import FunctionType  #, MethodType
from typing     import Any, Tuple, List, Dict, Callable, Generator, Set, Iterator, Iterable, Union
from typing     import Type, TypeVar, Generic, _GenericAlias, ClassVar, Optional as Nullable

try:
	from pyTooling.Exceptions import ToolingException
	from pyTooling.Decorators import export, readonly
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.MetaClasses] Could not import from 'pyTooling.*'!")

	try:
		from Exceptions import ToolingException
		from Decorators import export, readonly
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.MetaClasses] Could not import directly!")
		raise ex


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
	The exception is raised when a class using ``__slots__`` inherits from at-least one base-class not using ``__slots__``.

	.. seealso::

	   * :ref:`Python data model for slots <slots>`
	   * :term:`Glossary entry __slots__ <__slots__>`
	"""


@export
class BaseClassWithNonEmptySlotsError(ExtendedTypeError):
	pass


@export
class BaseClassIsNotAMixinError(ExtendedTypeError):
	pass


@export
class DuplicateFieldInSlotsError(ExtendedTypeError):
	pass


@export
class AbstractClassError(ExtendedTypeError):
	"""
	The exception is raised, when a class contains methods marked with *abstractmethod* or *mustoverride*.

	.. seealso::

	   :func:`@abstractmethod <pyTooling.MetaClasses.abstractmethod>`
	      |rarr| Mark a method as *abstract*.
	   :func:`@mustoverride <pyTooling.MetaClasses.mustoverride>`
	      |rarr| Mark a method as *must overrride*.
	   :exc:`~MustOverrideClassError`
	      |rarr| Exception raised, if a method is marked as *must-override*.
	"""


@export
class MustOverrideClassError(AbstractClassError):
	"""
	The exception is raised, when a class contains methods marked with *must-override*.

	.. seealso::

	   :func:`@abstractmethod <pyTooling.MetaClasses.abstractmethod>`
	      |rarr| Mark a method as *abstract*.
	   :func:`@mustoverride <pyTooling.MetaClasses.mustoverride>`
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


@export
def slotted(cls):
	if cls.__class__ is type:
		metacls = ExtendedType
	elif issubclass(cls.__class__, ExtendedType):
		metacls = cls.__class__
		for method in cls.__methods__:
			delattr(method, "__classobj__")
	else:
		raise ExtendedTypeError(f"Class uses an incompatible meta-class.")  # FIXME: create exception for it?

	bases = tuple(base for base in cls.__bases__ if base is not object)
	slots = cls.__dict__["__slots__"] if "__slots__" in cls.__dict__ else tuple()
	members = {
		"__qualname__": cls.__qualname__
	}
	for key, value in cls.__dict__.items():
		if key not in slots:
			members[key] = value

	return metacls(cls.__name__, bases, members, slots=True)


@export
def mixin(cls):
	if cls.__class__ is type:
		metacls = ExtendedType
	elif issubclass(cls.__class__, ExtendedType):
		metacls = cls.__class__
		for method in cls.__methods__:
			delattr(method, "__classobj__")
	else:
		raise ExtendedTypeError(f"Class uses an incompatible meta-class.")  # FIXME: create exception for it?

	bases = tuple(base for base in cls.__bases__ if base is not object)
	slots = cls.__dict__["__slots__"] if "__slots__" in cls.__dict__ else tuple()
	members = {
		"__qualname__": cls.__qualname__
	}
	for key, value in cls.__dict__.items():
		if key not in slots:
			members[key] = value

	return metacls(cls.__name__, bases, members, mixin=True)


@export
def singleton(cls):
	if cls.__class__ is type:
		metacls = ExtendedType
	elif issubclass(cls.__class__, ExtendedType):
		metacls = cls.__class__
		for method in cls.__methods__:
			delattr(method, "__classobj__")
	else:
		raise ExtendedTypeError(f"Class uses an incompatible meta-class.")  # FIXME: create exception for it?

	bases = tuple(base for base in cls.__bases__ if base is not object)
	slots = cls.__dict__["__slots__"] if "__slots__" in cls.__dict__ else tuple()
	members = {
		"__qualname__": cls.__qualname__
	}
	for key, value in cls.__dict__.items():
		if key not in slots:
			members[key] = value

	return metacls(cls.__name__, bases, members, singleton=True)


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
	          '''This method needs to be implemented'''

	:param method: Method that is marked as *abstract*.
	:returns:      Replacement method, which raises a :exc:`NotImplementedError`.

	.. seealso::

	   * :exc:`~pyTooling.Exceptions.AbstractClassError`
	   * :func:`~pyTooling.Metaclasses.mustoverride`
	   * :func:`~pyTooling.Metaclasses.notimplemented`
	"""
	@wraps(method)
	def func(self):
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
	          '''This is a very basic implementation'''

	:param method: Method that is marked as *must-override*.
	:returns:      Same method, but with additional ``<method>.__mustOverride__`` field.

	.. seealso::

	   * :exc:`~pyTooling.Exceptions.MustOverrideClassError`
	   * :func:`~pyTooling.Metaclasses.abstractmethod`
	   * :func:`~pyTooling.Metaclasses.notimplemented`
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
# 	def __get__(self, instance, cls):  # Starting with Python 3.11+, use typing.Self as return type
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

	Features:

	* Store object members more efficiently in ``__slots__`` instead of ``_dict__``.
	* Allow only a single instance to be created (:term:`singleton`).
	* Define methods as :term:`abstract <abstract method>` or :term:`must-override <mustoverride method>` and prohibit
	  instantiation of :term:`abstract classes <abstract class>`.

	.. #* Allow method overloading and dispatch overloads based on argument signatures.
	"""

	# @classmethod
	# def __prepare__(cls, className, baseClasses, slots: bool = False, mixin: bool = False, singleton: bool = False):
	# 	return DispatchDictionary()

	def __new__(self, className: str, baseClasses: Tuple[type], members: Dict[str, Any],
							slots: bool = False, mixin: bool = False, singleton: bool = False) -> "ExtendedType":
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
		try:
			from pyTooling.Attributes import ATTRIBUTES_MEMBER_NAME, AttributeScope
		except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
			from Attributes import ATTRIBUTES_MEMBER_NAME, AttributeScope

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
		newClass.__isAbstract__ = self._wrapNewMethodIfAbstract(newClass)
		newClass.__isSingleton__ = self._wrapNewMethodIfSingleton(newClass, singleton)

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

			:param predicate:
			:return:
			:raises ValueError:
			:raises ValueError:
			"""
			try:
				from ..Attributes import Attribute
			except (ImportError, ModuleNotFoundError):  # pragma: no cover
				try:
					from Attributes import Attribute
				except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
					raise ex

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
	def _findMethods(self, newClass: "ExtendedType", baseClasses: Tuple[type], members: Dict[str, Any]):
		try:
			from ..Attributes import Attribute
		except (ImportError, ModuleNotFoundError):  # pragma: no cover
			try:
				from Attributes import Attribute
			except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
				raise ex

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
	def _computeSlots(self, className, baseClasses, members, slots, mixin):
		# Compute which field are listed in __slots__ and which need to be initialized in an instance or class.
		slottedFields = []
		objectFields = {}
		classFields = {}
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

			# FIXME: should have a check for non-empty slots on secondary base-classes too

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
			annotations: Dict[str, Any] = members.get("__annotations__", {})
			for fieldName, typeAnnotation in annotations.items():
				if fieldName in inheritedSlottedFields:
					cls = inheritedSlottedFields[fieldName]
					raise AttributeError(f"Slot '{fieldName}' already exists in base-class '{cls.__module__}.{cls.__name__}'.")

				# If annotated field is a ClassVar, and it has an initial value
				# * copy field and initial value to classFields dictionary
				# * remove field from members
				if isinstance(typeAnnotation, _GenericAlias) and typeAnnotation.__origin__ is ClassVar and fieldName in members:
					classFields[fieldName] = members[fieldName]
					del members[fieldName]

				# If an annotated field has an initial value
				# * copy field and initial value to objectFields dictionary
				# * remove field from members
				elif fieldName in members:
					slottedFields.append(fieldName)
					objectFields[fieldName] = members[fieldName]
					del members[fieldName]
				else:
					slottedFields.append(fieldName)

			mixinSlots = self._aggregateMixinSlots(className, baseClasses)
		else:
			# When adding annotated fields to slottedFields, check if name was not used in inheritance hierarchy.
			annotations: Dict[str, Any] = members.get("__annotations__", {})
			for fieldName, typeAnnotation in annotations.items():
				# If annotated field is a ClassVar, and it has an initial value
				# * copy field and initial value to classFields dictionary
				# * remove field from members
				if isinstance(typeAnnotation, _GenericAlias) and typeAnnotation.__origin__ is ClassVar and fieldName in members:
					classFields[fieldName] = members[fieldName]
					del members[fieldName]

		# FIXME: search for fields without annotation
		if mixin:
			mixinSlots.extend(slottedFields)
			members["__slotted__"] = True
			members["__slots__"] = tuple()
			members["__isMixin__"] = True
			members["__mixinSlots__"] = tuple(mixinSlots)
		elif slots:
			slottedFields.extend(mixinSlots)
			members["__slotted__"] = True
			members["__slots__"] = tuple(slottedFields)
			members["__isMixin__"] = False
			members["__mixinSlots__"] = tuple()
		else:
			members["__slotted__"] = False
			# NO     __slots__
			members["__isMixin__"] = False
			members["__mixinSlots__"] = tuple()
		return classFields, objectFields

	@classmethod
	def _aggregateMixinSlots(self, className, baseClasses):
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
			# Aggregate all abstract methods from all base-classes.
			for baseClass in baseClasses:
				if hasattr(baseClass, "__abstractMethods__"):
					abstractMethods.update(baseClass.__abstractMethods__)

			for base in baseClasses:
				for key, value in base.__dict__.items():
					if (key in abstractMethods and isinstance(value, FunctionType) and
						not (hasattr(value, "__abstract__") or hasattr(value, "__mustOverride__"))):
						def outer(method):
							@wraps(method)
							def inner(cls, *args: Any, **kwargs: Any):
								return method(cls, *args, **kwargs)

							return inner

						members[key] = outer(value)

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
		If the class has abstract methods, replace the ``_new__`` method, so it raises an exception.

		:param newClass:            The newly constructed class for further modifications.
		:returns:                   ``True``, if the class is abstract.
		:raises AbstractClassError: If the class is abstract and can't be instantiated.
		"""
		# Replace '__new__' by a variant to throw an error on not overridden methods
		if len(newClass.__abstractMethods__) > 0:
			oldnew = newClass.__new__
			if hasattr(oldnew, "__raises_abstract_class_error__"):
				oldnew = oldnew.__wrapped__

			@wraps(oldnew)
			def abstract_new(cls, *_, **__):
				raise AbstractClassError(f"""Class '{cls.__name__}' is abstract. The following methods: '{"', '".join(newClass.__abstractMethods__)}' need to be overridden in a derived class.""")

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
				# WORKAROUND:
				#   AttributeError.name was added in Python 3.10. For version <3.10 use a string contains operation.
				try:
					if ex.name != "__raises_abstract_class_error__":
						raise ex
				except AttributeError:
					if "__raises_abstract_class_error__" not in str(ex):
						raise ex

			return False

	# Additional properties and methods on a class
	@property
	def HasClassAttributes(self) -> bool:
		"""
		Read-only property to check if the class has Attributes (:attr:`__pyattr__`).

		:returns: ``True``, if the class has Attributes.
		"""
		try:
			return len(self.__pyattr__) > 0
		except AttributeError:
			return False

	@property
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
