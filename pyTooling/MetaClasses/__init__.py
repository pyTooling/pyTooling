# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     A collection of MetaClasses for Python.
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from inspect  import signature, Parameter
from types    import MethodType

from ..Decorators import export


@export
class Singleton(type):
	"""Implements a singleton pattern in form of a Python metaclass (a class constructing classes)."""

	_instanceCache = {}       #: Cache of all created singleton instances.

	def __call__(cls, *args, **kwargs):
		"""
		Overwrites the ``__call__`` method of parent class :py:class:`type` to return
		an object instance from an instances cache (see :attr:`_instanceCache`) if
		the class was already constructed before.
		"""
		if cls not in cls._instanceCache:
			cls._instanceCache[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instanceCache[cls]

	@classmethod
	def Register(cls, t, instance):
		"""Register a type,instance pair in :attr:`_instanceCache`."""

		if t not in cls._instanceCache:
			cls._instanceCache[t] = instance
		else:
			raise KeyError("Type '{type!s}' is already registered.".format(type=t))


# https://github.com/dabeaz/python-cookbook/blob/master/src/9/multiple_dispatch_with_function_annotations/example1.py?ts=2

@export
class Overloading(type):
	"""Metaclass that allows multiple dispatch of methods based on method signatures."""

	class DispatchDictionary(dict):
		"""Special dictionary to build dispatchable methods in a metaclass."""

		class DispatchableMethod:
			"""Represents a single multimethod."""

			def __init__(self, name):
				self._methods = {}
				self.__name__ = name

			def register(self, method):
				"""Register a new method as a dispatchable."""

				# Build a signature from the method's type annotations
				sig = signature(method)
				types = []
				for name, parameter in sig.parameters.items():
					if name == "self":
						continue

					if parameter.annotation is Parameter.empty:
						raise TypeError("Argument {} must be annotated with a type.".format(name))
					if not isinstance(parameter.annotation, type):
						raise TypeError("Argument {} annotation must be a type.".format(name))

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
					raise TypeError("No matching method for types {}.".format(types))

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
