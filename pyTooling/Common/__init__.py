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
Common types, helper functions and classes.

.. hint:: See :ref:`high-level help <COMMON>` for explanations and usage examples.
"""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2017-2023, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "5.0.0"
__keywords__ =  ["decorators", "meta-classes", "exceptions", "platform", "versioning", "licensing", "overloading",
								"singleton", "tree", "graph", "timer", "data structure", "setuptools", "wheel", "installation",
								"packaging", "path", "generic path", "generic library", "url", "terminal", "shell", "TUI", "console",
								"text user interface", "message logging", "abstract", "override"]

from collections import deque
from numbers     import Number
from typing      import Type, Any, Callable, Dict, Generator, Tuple, TypeVar, overload, Union, Mapping, Set, Hashable, Optional

try:
	from pyTooling.Decorators import export
	from pyTooling.Platform   import Platform
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Packaging] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export
		from Platform   import Platform
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Packaging] Could not import from 'Decorators' or 'Licensing' directly!")
		raise ex


__all__ = ["CurrentPlatform"]

CurrentPlatform = Platform()     #: Gathered information for the current platform.


@export
def isnestedclass(cls: Type, scope: Type) -> bool:
	"""
	Returns true, if the given class ``cls`` is a member on an outer class ``scope``.

	:param cls:   Class to check, if it's a nested class.
	:param scope: Outer class which is the outer scope of ``cls``.
	:returns:     ``True``, if ``cls`` is a nested class within ``scope``.
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

	:param obj: Object to calculate the size of.
	:returns:   True size of an object in bytes.

	.. admonition:: Background Information

	   The function :func:`sys.getsizeof` only returns the raw size of a Python object and doesn't account for the
	   overhead of e.g. ``_dict__`` to store dynamically allocated object members.

	.. seealso::

	   The code is based on code snippets and ideas from:

	   * `Compute Memory Footprint of an Object and its Contents <https://code.activestate.com/recipes/577504/>`__ (MIT Lizense)
	   * `How do I determine the size of an object in Python? <https://stackoverflow.com/a/30316760/3719459>`__ (CC BY-SA 4.0)
	   * `Python __slots__, slots, and object layout <https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/080_python_slots>`__ (MIT Lizense)
	"""
	from sys import getsizeof as sys_getsizeof

	visitedIDs = set()  #: A set to track visited objects, so memory consumption isn't counted multiple times.

	def recurse(obj: Any) -> int:
		"""
		Nested function for recursion.

		:param obj: Subobject to calculate the size of.
		:returns:   Size of a subobject in bytes.
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


_DictKey = TypeVar("_DictKey")
_DictKey1 = TypeVar("_DictKey1")
_DictKey2 = TypeVar("_DictKey2")
_DictKey3 = TypeVar("_DictKey3")
_DictValue1 = TypeVar("_DictValue1")
_DictValue2 = TypeVar("_DictValue2")
_DictValue3 = TypeVar("_DictValue3")


@export
def firstKey(d: Dict[_DictKey1, _DictValue1]) -> _DictKey1:
	"""
	Retrieves the first key from a dictionary's keys.

	:param d: Dictionary to get the first key from.
	:returns: The first key.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.keys()))


@export
def firstValue(d: Dict[_DictKey1, _DictValue1]) -> _DictValue1:
	"""
	Retrieves the first value from a dictionary's values.

	:param d: Dictionary to get the first value from.
	:returns: The first value.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.values()))


@export
def firstItem(d: Dict[_DictKey1, _DictValue1]) -> Tuple[_DictKey1, _DictValue1]:
	"""
	Retrieves the first key-value-pair from a dictionary.

	:param d: Dictionary to get the first key-value-pair from.
	:returns: The first key-value-pair as tuple.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.items()))


@overload
def mergedicts(
	m1: Mapping[_DictKey1, _DictValue1],
	filter: Optional[Callable[[Hashable, Any], bool]]
) -> Dict[Union[_DictKey1], Union[_DictValue1]]:
#) -> Generator[Tuple[Union[_DictKey1], Union[_DictValue1]], None, None]:
	...  # pragma: no cover


@overload
def mergedicts(
	m1: Mapping[_DictKey1, _DictValue1],
	m2: Mapping[_DictKey2, _DictValue2],
	filter: Optional[Callable[[Hashable, Any], bool]]
) -> Dict[Union[_DictKey1, _DictKey2], Union[_DictValue1, _DictValue2]]:
# ) -> Generator[Tuple[Union[_DictKey1, _DictKey2], Union[_DictValue1, _DictValue2]], None, None]:
	...  # pragma: no cover


@overload
def mergedicts(
	m1: Mapping[_DictKey1, _DictValue1],
	m2: Mapping[_DictKey2, _DictValue2],
	m3: Mapping[_DictKey3, _DictValue3],
	filter: Optional[Callable[[Hashable, Any], bool]]
) -> Dict[Union[_DictKey1, _DictKey2, _DictKey3], Union[_DictValue1, _DictValue2, _DictValue3]]:
#) -> Generator[Tuple[Union[_DictKey1, _DictKey2, _DictKey3], Union[_DictValue1, _DictValue2, _DictValue3]], None, None]:
	...  # pragma: no cover


@export
def mergedicts(*dicts: Tuple[Dict, ...], filter: Callable[[Hashable, Any], bool] = None) -> Dict:
	"""
	Merge multiple dictionaries into a single new dictionary.

	If parameter ``filter`` isn't ``None``, then this function is applied to every element during the merge operation. If
	it returns true, the dictionary element will be present in the resulting dictionary.

	:param dicts:  Tuple of dictionaries to merge as positional parameters.
	:param filter: Optional filter function to apply to each dictionary element when merging.
	:returns:      A new dictionary containing the merge result.

	.. seealso::

	   `How do I merge two dictionaries in a single expression in Python? <https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python>`__
	"""
	if len(dicts) == 0:
		raise ValueError(f"Called 'mergedicts' without any dictionary parameter.")

	if filter is None:
		return {k: v for d in dicts for k, v in d.items()}
	else:
		return {k: v for d in dicts for k, v in d.items() if filter(k, v)}


@overload
def zipdicts(
	m1: Mapping[_DictKey, _DictValue1]
) -> Generator[Tuple[_DictKey, _DictValue1], None, None]:
	...  # pragma: no cover


@overload
def zipdicts(
	m1: Mapping[_DictKey, _DictValue1],
	m2: Mapping[_DictKey, _DictValue2]
) -> Generator[Tuple[_DictKey, _DictValue1, _DictValue2], None, None]:
	...  # pragma: no cover


@overload
def zipdicts(
	m1: Mapping[_DictKey, _DictValue1],
	m2: Mapping[_DictKey, _DictValue2],
	m3: Mapping[_DictKey, _DictValue3]
) -> Generator[Tuple[_DictKey, _DictValue1, _DictValue2, _DictValue3], None, None]:
	...  # pragma: no cover


@export
def zipdicts(*dicts: Tuple[Dict, ...]) -> Generator[Tuple, None, None]:
	"""
	Iterate multiple dictionaries simultaneously.

	:param dicts: Tuple of dictionaries to iterate as positional parameters.
	:returns:     A generator returning a tuple containing the key and values of each dictionary in the order of given
	              dictionaries.

	.. seealso::

	   The code is based on code snippets and ideas from:

	   * `zipping together Python dicts <https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/101_zip_dict>`__ (MIT Lizense)
	"""
	if len(dicts) == 0:
		raise ValueError(f"Called 'zipdicts' without any dictionary parameter.")

	length = len(dicts[0])
	if any(len(d) != length for d in dicts):
		raise ValueError(f"All given dictionaries must have the same length.")

	def gen(ds: Tuple[Dict, ...]) -> Generator[Tuple, None, None]:
		for key, item0 in ds[0].items():
			# WORKAROUND: using redundant parenthesis for Python 3.7
			yield (key, item0, *(d[key] for d in ds[1:]))

	return gen(dicts)
