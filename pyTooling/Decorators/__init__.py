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
"""Decorators controlling visibility of entities in a Python module.

.. hint:: See :ref:`high-level help <DECO>` for explanations and usage examples.
"""
import sys
from types     import FunctionType
from typing import Union, Type, TypeVar, Callable, Any

__all__ = ["export", "Param", "RetType", "Func", "T"]


try:
	# See https://stackoverflow.com/questions/47060133/python-3-type-hinting-for-decorator
	from typing import ParamSpec    # exists since Python 3.10

	Param = ParamSpec("Param")                       #: A parameter specification for function or method
	RetType = TypeVar("RetType")                     #: Type variable for a return type
	Func = Callable[Param, RetType]                  #: Type specification for a function
except ImportError:  # pragma: no cover
	Param = ...                                      #: A parameter specification for function or method
	RetType = TypeVar("RetType")                     #: Type variable for a return type
	Func = Callable[..., RetType]                    #: Type specification for a function


T = TypeVar("T", bound=Union[Type, FunctionType])  #: Type variable for a class or function


def export(entity: T) -> T:
	"""
	Register the given function or class as publicly accessible in a module.

	Creates or updates the ``__all__`` attribute in the module in which the decorated entity is defined to include the
	name of the decorated entity.

	.. admonition:: ``to_export.py``

	   .. code:: python

	      from pyTooling.Decorators import export

	      @export
	      def exported():
	        pass

	      def not_exported():
	        pass

	.. admonition:: ``another_file.py``

	   .. code:: python

	      from .to_export import *

	      assert "exported" in globals()
	      assert "not_exported" not in globals()

	:param entity:          The function or class to include in `__all__`.
	:returns:               The unmodified function or class.
	:raises AttributeError: If parameter ``entity`` has no ``__module__`` member.
	:raises TypeError:      If parameter ``entity`` is not a top-level entity in a module.
	:raises TypeError:      If parameter ``entity`` has no ``__name__``.
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
		module = sys.modules[entity.__module__]
	except KeyError:
		raise ValueError(f"Module {entity.__module__} is not present in sys.modules. Please ensure it is in the import path before calling export().")

	if hasattr(module, "__all__"):
		if entity.__name__ not in module.__all__:	# type: ignore
			module.__all__.append(entity.__name__)	# type: ignore
	else:
		module.__all__ = [entity.__name__]	      # type: ignore

	return entity


@export
def classproperty(method):

	class Descriptor:
		"""A decorator adding properties to classes."""
		_getter: Callable
		_setter: Callable

		def __init__(self, getter: Callable = None, setter: Callable = None):
			self._getter = getter
			self._setter = setter
			self.__doc__ = getter.__doc__

		def __get__(self, instance: Any, owner: type = None) -> Any:
			return self._getter(owner)

		def __set__(self, instance: Any, value: Any) -> None:
			self._setter(instance.__class__, value)

		def setter(self, setter: Callable):
			return self.__class__(self._getter, setter)

	descriptor = Descriptor(method)
	return descriptor


@export
def OriginalFunction(func: FunctionType) -> Callable[[Func], Func]:
	"""
	Store a reference to the original function/method on a new, wrapper or replacement function/method.

	The function or method reference is stored in ``__orig_func__``.

	.. admonition:: ``metaclass.py``

	   .. code:: python

	      from functools import wraps
	      from pyTooling.Decorators import OriginalFunction

	      class Meta(type):
	        def __new__(self, className: str, baseClasses: Tuple[type], members: Dict[str, Any]) -> type:
	          # Create a new class
	          newClass = type.__new__(self, className, baseClasses, members)

	          @OriginalFunction(newClass.__new__)
	          @wraps(newClass.__new__)
	          def new(cls, *args, **kwargs):
	            # ...
	            obj = newClass.__new__(*args, **kwargs)
	            # ...
	            return obj

	          newClass.__new__ = new

	          return newClass

	:param func: Function or method reference to be store on the decorated function or method.
	:returns:    Decorator function that stores the function or method reference on the decorated object.
	"""
	def decorator(f: Func) -> Func:
		"""
		Decorator function, which stores a reference to a function or method in a new field called ``__orig_func__``.

		:param f:          Function or method, where the original function or method reference is attached to.
		:returns:          Same method, but with new field ``__orig_func__`` set to the original function or method.
		:raises TypeError: If decorated object is not callable.
		"""
		if not isinstance(f, Callable):
			raise TypeError(f"Decorated object is not callable.")

		f.__orig_func__ = func
		return f

	return decorator


@export
def InheritDocString(baseClass: type) -> Callable[[Func], Func]:
	"""
	Copy the doc-string from given base-class to the method this decorator is applied to.

	.. admonition:: ``example.py``

	   .. code:: python

	      from pyTooling.Decorators import InheritDocString

	      class Class1:
	        def method(self):
	          '''Method's doc-string.'''

	      class Class2(Class1):
	        @InheritDocString(Class1)
	        def method(self):
	          super().method()

	:param baseClass: Base-class to copy the doc-string from to the new method being decorated.
	:returns:         Decorator function that copies the doc-string.
	"""
	def decorator(m: Func) -> Func:
		"""
		Decorator function, which copies the doc-string from base-class' method to method ``m``.

		:param m: Method to which the doc-string from a method in ``baseClass`` (with same className) should be copied.
		:returns: Same method, but with overwritten doc-string field (``__doc__``).
		"""
		m.__doc__ = getattr(baseClass, m.__name__).__doc__
		return m

	return decorator
