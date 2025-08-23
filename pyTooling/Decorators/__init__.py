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
"""Decorators controlling visibility of entities in a Python module.

.. hint:: See :ref:`high-level help <DECO>` for explanations and usage examples.
"""
import sys
from functools import wraps
from types     import FunctionType
from typing    import Union, Type, TypeVar, Callable, Any, Optional as Nullable

__all__ = ["export", "Param", "RetType", "Func", "T"]


try:
	# See https://stackoverflow.com/questions/47060133/python-3-type-hinting-for-decorator
	from typing import ParamSpec                     # WORKAROUND: exists since Python 3.10

	Param = ParamSpec("Param")                       #: A parameter specification for function or method
	RetType = TypeVar("RetType")                     #: Type variable for a return type
	Func = Callable[Param, RetType]                  #: Type specification for a function
except ImportError:  # pragma: no cover
	Param = ...                                      #: A parameter specification for function or method
	RetType = TypeVar("RetType")                     #: Type variable for a return type
	Func = Callable[..., RetType]                    #: Type specification for a function


T = TypeVar("T", bound=Union[Type, FunctionType])  #: A type variable for a classes or functions.
C = TypeVar("C", bound=Callable)                   #: A type variable for functions or methods.


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
		if entity.__name__ not in module.__all__:  # type: ignore
			module.__all__.append(entity.__name__)   # type: ignore
	else:
		module.__all__ = [entity.__name__]         # type: ignore

	return entity


@export
def notimplemented(message: str) -> Callable:
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

	:param method: Method that is marked as *not implemented*.
	:returns:      Replacement method, which raises a :exc:`NotImplementedError`.

	.. seealso::

	   * :func:`~pyTooling.Metaclasses.abstractmethod`
	   * :func:`~pyTooling.Metaclasses.mustoverride`
	"""

	def decorator(method: C) -> C:
		@wraps(method)
		def func(*_, **__):
			raise NotImplementedError(message)

		func.__notImplemented__ = True
		return func

	return decorator


@export
def readonly(func: Callable) -> property:
	"""
	Marks a property as *read-only*.

	The doc-string will be taken from the getter-function.

	It will remove ``<property>.setter`` and ``<property>.deleter`` from the property descriptor.

	:param func: Function to convert to a read-only property.
	:returns:    A property object with just a getter.

	.. seealso::

	   :class:`property`
	     A decorator to convert getter, setter and deleter methods into a property applying the descriptor protocol.
	"""
	prop = property(fget=func, fset=None, fdel=None, doc=func.__doc__)

	return prop


@export
def InheritDocString(baseClass: type, merge: bool = False) -> Callable[[Union[Func, type]], Union[Func, type]]:
	"""
	Copy the doc-string from given base-class to the method this decorator is applied to.

	.. admonition:: ``example.py``

	   .. code-block:: python

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
	def decorator(param: Union[Func, type]) -> Union[Func, type]:
		"""
		Decorator function, which copies the doc-string from base-class' method to method ``m``.

		:param param: Method to which the doc-string from a method in ``baseClass`` (with same className) should be copied.
		:returns: Same method, but with overwritten doc-string field (``__doc__``).
		"""
		if isinstance(param, type):
			baseDoc = baseClass.__doc__
		elif callable(param):
			baseDoc = getattr(baseClass, param.__name__).__doc__
		else:
			return param

		if merge:
			if param.__doc__ is None:
				param.__doc__ = baseDoc
			elif baseDoc is not None:
				param.__doc__ = baseDoc + "\n\n" + param.__doc__
		else:
			param.__doc__ = baseDoc

		return param

	return decorator
