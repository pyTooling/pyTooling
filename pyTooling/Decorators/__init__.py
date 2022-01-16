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
"""Decorators controlling visibility of entities in a Python module."""
import sys
from types  import FunctionType
from typing import Union, Type, TypeVar


__all__ = ["export"]
__api__ = __all__


T = TypeVar("T", bound=Union[Type, FunctionType])


def export(entity: T) -> T:
	"""
	Register the given function or class as publicly accessible in a module.

	Creates or updates the ``__all__`` attribute in the module in which the
	decorated entity is defined to include the name of the decorated entity.

	**Example:**

	``to_export.py``:

	.. code:: python

	   from pyTooling.Decorators import export

	   @export
	   def exported():
	     pass

	   def not_exported():
	     pass


	``another_file.py``

	.. code:: python

	   from .to_export import *

	   assert "exported" in globals()
	   assert "not_exported" not in globals()


	:param entity: the function or class to include in `__all__`
	"""
	# * Based on an idea by Duncan Booth:
	#	  http://groups.google.com/group/comp.lang.python/msg/11cbb03e09611b8a
	# * Improved via a suggestion by Dave Angel:
	#	  http://groups.google.com/group/comp.lang.python/msg/3d400fb22d8a42e1

	if not hasattr(entity, "__module__"):
		raise TypeError(f"{entity} has no __module__ attribute. Please ensure it is a top-level function or class reference defined in a module.")

	if hasattr(entity, "__qualname__"):
		if any(i in entity.__qualname__ for i in (".", "<locals>", "<lambda>")):
			raise TypeError(f"Only named top-level functions and classes may be exported, not {entity}")

	if not hasattr(entity, "__name__") or entity.__name__ == "<lambda>":
		raise TypeError(f"Entity must be a named top-level funcion or class, not {entity.__class__}")

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
