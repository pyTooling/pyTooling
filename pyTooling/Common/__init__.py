# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
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
"""
Common types, helper functions and classes.

.. hint:: See :ref:`high-level help <COMMON>` for explanations and usage examples.
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2017-2022, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "2.2.0"
__keywords__ =  ["decorators", "meta classes", "exceptions", "platform", "versioning", "licensing", "overloading", "singleton", "tree", "data structure", "setuptools", "wheel", "installation", "packaging", "path", "generic path", "generic library", "url"]

from collections import deque
from collections.abc import Set, Mapping
from numbers import Number
from typing import Type, Any

try:
	from pyTooling.Decorators import export
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Packaging] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Packaging] Could not import from 'Decorators' or 'Licensing' directly!")
		raise ex

from pyTooling.Common.Platform import Platform

__all__ = ["CurrentPlatform"]

CurrentPlatform = Platform()     #: Gathered information for the current platform.


@export
def isnestedclass(cls: Type, scope: Type) -> bool:
	"""
	Returns true, if the given class ``cls`` is a member on an outer class ``scope``.

	:param cls:   Class to check, if it's a nested class.
	:param scope: Outer class which is the outer scope of ``cls``.
	:returns:     True, if ``cls`` is a nested class within ``scope``.
	"""
	for mroClass in scope.mro():
		for memberName in mroClass.__dict__:
			member = getattr(mroClass, memberName)
			if isinstance(member, Type):
				if cls is member:
					return True

	return False


@export
def getsizeof(obj: Any) -> int:
	"""
	Recursively calculate the "true" size of an object including complex members like ``__dict__``.

	.. admonition:: Background Information

	   The function :py:func:`sys.getsizeof` only returns the raw size of a Python object and doesn't account for the
	   overhead of e.g. ``_dict__`` to store dynamically allocated object members.

	.. seealso::

	   The code ise based on code snippets and ideas from:

	   * `Compute Memory Footprint of an Object and its Contents <https://code.activestate.com/recipes/577504/>`__ (MIT Lizense)
	   * `How do I determine the size of an object in Python? <https://stackoverflow.com/a/30316760/3719459>`__ (CC BY-SA 4.0)
	   * `Python __slots__, slots, and object layout <https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/080_python_slots>`__ (MIT Lizense)

	:param obj: Object to calculate the size of.
	:return:    True size of an object in bytes.
	"""
	from sys import getsizeof as sys_getsizeof

	visitedIDs = set()  #: A set to track visited objects, so memory consumption isn't counted multiple times.

	def recurse(obj: Any) -> int:
		"""
		Nested function for recursion.

		:param obj: Subobject to calculate the size of.
		:return:    Size of a subobject in bytes.
		"""
		# If already visited, return 0 bytes, so no additional bytes are accumulated
		objectID = id(obj)
		if objectID in visitedIDs:
			return 0
		else:
			visitedIDs.add(objectID)

		# Get objects raw size
		size: int = sys_getsizeof(obj)

		# Skip elementary types
		if isinstance(obj, (str, bytes, bytearray, range, Number)):
			pass
		# Handle iterables
		elif isinstance(obj, (tuple, list, Set, deque)):      # TODO: What about builtin "set", "frozenset" and "dict"?
			for item in obj:
				size += recurse(item)
		# Handle mappings
		elif isinstance(obj, Mapping) or hasattr(obj, 'items'):
			for key, value in getattr(obj, 'items')():
				size += recurse(key) + recurse(value)

		# Accumulate members from __dict__
		if hasattr(obj, '__dict__'):
			size += recurse(vars(obj))

		# Accumulate members from __slots__
		if hasattr(obj, '__slots__'):
			for slot in obj.__slots__:
				if hasattr(obj, slot):
					size += recurse(getattr(obj, slot))

		return size

	return recurse(obj)
