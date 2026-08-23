# ==================================================================================================================== #
#             _____           _ _               ____                           _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___  ___ ___  _ __ __ _| |_ ___  _ __ ___                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \/ __/ _ \| '__/ _` | __/ _ \| '__/ __|                      #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ (_| (_) | | | (_| | || (_) | |  \__ \                      #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___|\___\___/|_|  \__,_|\__\___/|_|  |___/                      #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
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
"""Decorators controlling visibility of entities in a Python module.

.. hint::

   See :ref:`high-level help <DECO>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.MetaClasses`
      |rarr| The meta-class offering the same features as class options.
   :mod:`pyTooling.Attributes`
      |rarr| Attributes, which mark an entity instead of modifying it.
"""
from __future__ import annotations

from enum       import Enum, unique
from functools  import wraps
from inspect    import cleandoc
from sys        import modules
from types      import FunctionType
from typing     import Any, Union, TypeVar, Callable, Generic, NoReturn, ParamSpec, overload
from typing     import Optional as Nullable

__all__ = ["export", "Param", "RetType", "Func", "T"]


# See https://stackoverflow.com/questions/47060133/python-3-type-hinting-for-decorator
Param = ParamSpec("Param")                         #: A parameter specification for function or method
RetType = TypeVar("RetType")                       #: Type variable for a return type
Func = Callable[Param, RetType]                    #: Type specification for a function


T = TypeVar("T", bound=Union[type, FunctionType])  #: A type variable for a classes or functions.
C = TypeVar("C", bound=Callable[..., Any])                   #: A type variable for functions or methods.


def export(entity: T) -> T:
	"""
	Register the given function or class as publicly accessible in a module.

	Creates or updates the ``__all__`` attribute in the module in which the decorated entity is defined to include the
	name of the decorated entity.

	+---------------------------------------------+------------------------------------------------+
	| ``to_export.py``                            | ``another_file.py``                            |
	+=============================================+================================================+
	| .. code-block:: python                      | .. code-block:: python                         |
	|                                             |                                                |
	|    from pyTooling.Decorators import export  |    from .to_export import *                    |
	|                                             |                                                |
	|    @export                                  |                                                |
	|    def exported():                          |    # 'exported' will be listed in __all__      |
	|      pass                                   |    assert "exported"         in globals()      |
	|                                             |                                                |
	|    def not_exported():                      |    # 'not_exported' won't be listed in __all__ |
	|      pass                                   |    assert "not_exported" not in globals()      |
	|                                             |                                                |
	+---------------------------------------------+------------------------------------------------+

	:param entity:          The function or class to include in `__all__`.
	:returns:               The unmodified function or class.
	:raises AttributeError: If parameter ``entity`` has no ``__module__`` member.
	:raises TypeError:      If parameter ``entity`` is not a top-level entity in a module.
	:raises TypeError:      If parameter ``entity`` has no ``__name__``.
	:raises ValueError:     If the decorated entity has no ``__module__`` attribute, so it can't be added to ``__all__``.
	"""
	# * Based on an idea by Duncan Booth:
	#	  http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
	# * Improved via a suggestion by Dave Angel:
	#	  http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

	if not hasattr(entity, "__module__"):
		raise AttributeError(f"{entity} has no __module__ attribute. Please ensure it is a top-level function or class reference defined in a module.")

	if hasattr(entity, "__qualname__"):
		if any(i in entity.__qualname__ for i in (".", "<locals>", "<lambda>")):
			raise TypeError(f"Only named top-level functions and classes may be exported, not {entity}")

	if not hasattr(entity, "__name__") or entity.__name__ == "<lambda>":
		raise TypeError(f"Entity must be a named top-level function or class, not {entity.__class__}")

	try:
		module = modules[entity.__module__]
	except KeyError:
		raise ValueError(f"Module {entity.__module__} is not present in sys.modules. Please ensure it is in the import path before calling export().")

	if hasattr(module, "__all__"):
		if entity.__name__ not in module.__all__:  # type: ignore
			module.__all__.append(entity.__name__)   # type: ignore
	else:
		module.__all__ = [entity.__name__]         # type: ignore

	return entity


@export
def notimplemented(message: str) -> Callable[..., Any]:
	"""
	Mark a method as *not implemented* and replace the implementation with a new method raising a :exc:`NotImplementedError`.

	The original method is stored in ``<method>.__wrapped__`` and it's doc-string is copied to the replacing method. In
	additional the field ``<method>.__notImplemented__`` is added.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      class Data:
	        @notimplemented
	        def method(self) -> bool:
	          '''This method needs to be implemented'''
	          return True

	:param message: Text of the :exc:`NotImplementedError` raised by the replacement method.
	:returns:       Decorator function that replaces the decorated method.

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.abstractmethod`
	      |rarr| Mark a method as *abstract* and raise a :exc:`NotImplementedError` when called.
	   :deco:`~pyTooling.MetaClasses.mustoverride`
	      |rarr| Mark a method as *mustoverride* (minimal implementation, but can be called).
	"""

	def decorator(method: C) -> C:
		"""
		Decorator function, which replaces the decorated method by one raising a :exc:`NotImplementedError`.

		:param method: Method to be replaced.
		:returns:      Replacement method, carrying the field ``__notImplemented__``.
		"""
		@wraps(method)
		def func(*_: Any, **__: Any) -> NoReturn:
			"""
			Replacement method, which raises a :exc:`NotImplementedError` when called.

			:raises NotImplementedError: Always, with the message given to :deco:`notimplemented`.
			"""
			raise NotImplementedError(message)

		func.__notImplemented__ = True
		return func

	return decorator


_ReturnType = TypeVar("_ReturnType")
"""A type variable for the value a read-only property hands out."""


@export
class readonly(property, Generic[_ReturnType]):
	"""
	Marks a property as *read-only*.

	The doc-string is taken from the getter-method, like :class:`property` does.

	A plain :class:`property` hands out ``<property>.setter`` and ``<property>.deleter``, so a property declared as
	read-only could be made writable again further down the class body. Both methods therefore raise an
	:exc:`AttributeError` instead.

	.. seealso::

	   :class:`property`
	     A decorator to convert getter, setter and deleter methods into a property applying the descriptor protocol.
	"""

	fget: Callable[[Any], _ReturnType]   #: The getter-method; a read-only property is always constructed from one.

	def __init__(self, fget: Callable[[Any], _ReturnType], doc: Nullable[str] = None) -> None:
		"""
		Create a read-only property from a getter-method.

		:class:`property` accepts a setter and a deleter here as well; this class does not, because it exists to
		reject them. Narrowing the signature to the getter is also what binds the type variable, so that reading the
		property hands out the getter's return type instead of :data:`~typing.Any`.

		:param fget: The getter-method the property is constructed from.
		:param doc:  Optional, doc-string of the property. If ``None``, the getter-method's doc-string is used.
		"""
		super().__init__(fget, None, None, doc)

	def getter(self, fget: Callable[[Any], _ReturnType], /) -> readonly[_ReturnType]:
		"""
		Derive a read-only property with another getter-method from this one.

		:class:`property` implements this by reconstructing itself as ``type(self)(fget, fset, fdel, doc)``, which is
		the only reason a setter and a deleter would have to be accepted by :meth:`__init__`. Constructing the
		property here instead keeps that signature down to what a read-only property actually has.

		:param fget: The getter-method of the derived property.
		:returns:    A new read-only property using the given getter-method, and its doc-string.
		"""
		return type(self)(fget)

	@overload
	def __get__(self, instance: None, owner: type, /) -> readonly[_ReturnType]:
		...     # pragma: no cover - an overload carries no implementation

	@overload
	def __get__(self, instance: Any, owner: Nullable[type] = None, /) -> _ReturnType:
		...     # pragma: no cover - an overload carries no implementation

	def __get__(self, instance: Any, owner: Nullable[type] = None, /) -> Union[readonly[_ReturnType], _ReturnType]:
		"""
		Return the value of the property, or the property itself when it is read from the class.

		Declaring this - :class:`property` implements it already - is what tells a type checker that the value has
		the getter's return type. Without it, every read of a ``@readonly`` property is :data:`~typing.Any`, and that
		spreads: a comparison of two such values, or a method returning one, becomes ``Any`` as well.

		:param instance: The object the property is read from, or ``None`` when it is read from the class.
		:param owner:    Optional, the class the property is defined in.
		:returns:        The value the getter returns, or this property when read from the class.
		"""
		return super().__get__(instance, owner)     # type: ignore[no-any-return]

	def setter(self, fset: Callable[..., Any]) -> NoReturn:
		"""
		Reject attaching a setter to a read-only property.

		:param fset:            The setter-method that was to be attached.
		:raises AttributeError: Always, because a read-only property can't have a setter. |br|
		                        Use :deco:`property` instead of :deco:`readonly`, if the property should be writable.
		"""
		ex = AttributeError(f"Property '{self.fget.__name__}' is read-only, so it can't have a setter.")
		ex.add_note(f"Use '@property' instead of '@readonly', if the property should be writable.")
		raise ex

	def deleter(self, fdel: Callable[..., Any]) -> NoReturn:
		"""
		Reject attaching a deleter to a read-only property.

		:param fdel:            The deleter-method that was to be attached.
		:raises AttributeError: Always, because a read-only property can't have a deleter. |br|
		                        Use :deco:`property` instead of :deco:`readonly`, if the property should be deletable.
		"""
		ex = AttributeError(f"Property '{self.fget.__name__}' is read-only, so it can't have a deleter.")
		ex.add_note(f"Use '@property' instead of '@readonly', if the property should be deletable.")
		raise ex


@export
@unique
class DocStringMergeStrategy(Enum):
	"""
	Strategy :func:`InheritDocString` follows when it combines the base-class' and the derived entity's doc-strings.

	A doc-string's **summary** is its first paragraph - the text up to the first blank line. Whatever follows is its
	**body**. A strategy naming *WithoutSummary* drops the summary of the doc-string it is applied to, because the other
	doc-string already provides one.

	.. seealso::

	   :deco:`InheritDocString`
	      |rarr| Copy or merge a base-class' doc-string into the derived entity.
	"""

	SummaryOnly =                 0  #: The base-class' summary, then the derived entity's doc-string.
	BaseLast =                    1  #: The derived entity's doc-string, then the base-class' doc-string.
	BaseLastWithoutSummary =      2  #: The derived entity's doc-string, then the base-class' body.
	BaseFirst =                   3  #: The base-class' doc-string, then the derived entity's doc-string.
	BaseInBetweenWithoutSummary = 4  #: The derived entity's summary, the base-class' body, then the derived body.


def _SplitDocString(docString: Nullable[str]) -> tuple[str, str]:
	"""
	Split a doc-string into its summary and its body.

	The doc-string is dedented with :func:`inspect.cleandoc` first. The summary is the first paragraph, the body is
	whatever follows the first blank line. Both are empty strings if the doc-string is ``None``, and the body is an empty
	string if the doc-string is a single paragraph.

	:param docString: The doc-string to split, or ``None``.
	:returns:         A tuple of summary and body.
	"""
	if docString is None:
		return "", ""

	summary, _, body = cleandoc(docString).partition("\n\n")
	return summary, body


@export
def InheritDocString(
	baseClass: type,
	strategy: DocStringMergeStrategy = DocStringMergeStrategy.BaseLast,
	prefix: str = "",
	interfix: str = "\n\n",
	postfix: str = ""
) -> Callable[[Func | type], Func | type]:
	"""
	Merge the doc-string from given base-class into the class or method this decorator is applied to.

	The decorated entity keeps what is specific to it and inherits the rest, so a description doesn't have to be
	repeated. Which parts are taken from which doc-string, and in which order they are arranged, is selected with
	``strategy``; by default the base-class' doc-string is appended to the derived entity's doc-string
	(:attr:`~DocStringMergeStrategy.BaseLast`).

	A derived entity without a doc-string of its own inherits the base-class' doc-string unchanged - that is the plain
	copy this decorator started out as, and it needs no special strategy.

	Both doc-strings are dedented with :func:`inspect.cleandoc` before they are combined. This matters for Python
	versions before 3.13, where the compiler does not strip a doc-string's indentation: combining a tab-indented
	base-class doc-string with a space-indented derived doc-string would otherwise leave the first part indented relative
	to the second, which renders as a block quote.

	The result is assembled as ``prefix + part + interfix + part ... + postfix``. Parts that are empty - a missing
	doc-string, or a body the strategy asked for that doesn't exist - are omitted together with their ``interfix``. If
	nothing remains, the decorated entity's doc-string is left unchanged.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      from pyTooling.Decorators import InheritDocString, DocStringMergeStrategy

	      class Class1:
	        def method(self):
	          '''Method's doc-string.'''

	      class Class2(Class1):
	        @InheritDocString(Class1)
	        def method(self):
	          super().method()

	.. admonition:: ``merging.py``

	   .. code-block:: python

	      @InheritDocString(
	        Class1,
	        DocStringMergeStrategy.BaseLastWithoutSummary,
	        interfix="\\n\\n**Inherited:**\\n\\n"
	      )
	      class Class2(Class1):
	        '''What is specific to Class2.'''

	:param baseClass: Base-class to copy the doc-string from to the class or method being decorated.
	:param strategy:  Optional, which parts of both doc-strings are used and in which order they are arranged; defaults
	                  to :attr:`~DocStringMergeStrategy.BaseLast`.
	:param prefix:    Optional, text inserted in front of the merged doc-string; defaults to an empty string.
	:param interfix:  Optional, text inserted between the parts; defaults to a blank line (``"\\n\\n"``).
	:param postfix:   Optional, text appended to the merged doc-string; defaults to an empty string.
	:returns:         Decorator function that merges the doc-string.

	.. seealso::

	   :class:`DocStringMergeStrategy`
	      |rarr| Selects which parts of both doc-strings are merged, and in which order.
	"""
	def decorator(param: Func | type) -> Func | type:
		"""
		Decorator function, which merges the doc-string from base-class' method into method ``m``.

		:param param: Method to which the doc-string from a method in ``baseClass`` (with same className) should be merged.
		:returns:     Same method, but with overwritten doc-string field (``__doc__``).
		"""
		if isinstance(param, type):
			baseDoc = baseClass.__doc__
		elif callable(param):
			baseDoc = getattr(baseClass, param.__name__).__doc__
		else:
			return param

		derivedDoc = param.__doc__
		baseSummary, baseBody = _SplitDocString(baseDoc)
		derivedSummary, derivedBody = _SplitDocString(derivedDoc)
		base = cleandoc(baseDoc) if baseDoc is not None else ""
		derived = cleandoc(derivedDoc) if derivedDoc is not None else ""

		parts: tuple[str, ...]
		if strategy is DocStringMergeStrategy.SummaryOnly:
			parts = (baseSummary, derived)
		elif strategy is DocStringMergeStrategy.BaseLast:
			parts = (derived, base)
		elif strategy is DocStringMergeStrategy.BaseLastWithoutSummary:
			parts = (derived, baseBody)
		elif strategy is DocStringMergeStrategy.BaseFirst:
			parts = (base, derived)
		else:
			parts = (derivedSummary, baseBody, derivedBody)

		merged = interfix.join(part for part in parts if part != "")
		if merged != "":
			param.__doc__ = f"{prefix}{merged}{postfix}"

		return param

	return decorator
