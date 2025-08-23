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
Common types, helper functions and classes.

.. hint:: See :ref:`high-level help <COMMON>` for explanations and usage examples.
"""
__author__ =        "Patrick Lehmann"
__email__ =         "Paebbels@gmail.com"
__copyright__ =     "2017-2025, Patrick Lehmann"
__license__ =       "Apache License, Version 2.0"
__version__ =       "8.7.0"
__keywords__ =      [
	"abstract", "argparse", "attributes", "bfs", "cli", "console", "data structure", "decorators", "dfs",
	"double linked list", "exceptions", "file system statistics", "generators", "generic library", "generic path",
	"geometry", "graph", "installation", "iterators", "licensing", "linked list", "message logging", "meta-classes",
	"overloading", "override", "packaging", "path", "platform", "setuptools", "shapes", "shell", "singleton", "slots",
	"terminal", "text user interface", "stopwatch", "tree", "TUI", "url", "versioning", "volumes", "wheel"
]
__issue_tracker__ = "https://GitHub.com/pyTooling/pyTooling/issues"

from collections         import deque
from importlib.resources import files
from numbers             import Number
from os                  import chdir
from pathlib             import Path
from types               import ModuleType, TracebackType
from typing              import Type, TypeVar, Callable, Generator, overload, Hashable, Optional, List
from typing              import Any, Dict, Tuple, Union, Mapping, Set, Iterable, Optional as Nullable


try:
	from pyTooling.Decorators  import export
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Common] Could not import from 'pyTooling.*'!")

	try:
		from Decorators         import export
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Common] Could not import directly!")
		raise ex


@export
def getFullyQualifiedName(obj: Any) -> str:
	"""
	Assemble the fully qualified name of a type.

	:param obj: The object for with the fully qualified type is to be assembled.
	:returns:   The fully qualified name of obj's type.
	"""
	try:
		module = obj.__module__             # for class or function
	except AttributeError:
		module = obj.__class__.__module__

	try:
		name = obj.__qualname__             # for class or function
	except AttributeError:
		name = obj.__class__.__qualname__

	# If obj is a method of builtin class, then module will be None
	if module == "builtins" or module is None:
		return name

	return f"{module}.{name}"


@export
def getResourceFile(module: Union[str, ModuleType], filename: str) -> Path:
	"""
	Compute the path to a file within a resource package.

	:param module:            The resource package.
	:param filename:          The filename.
	:returns:                 Path to the resource's file.
	:raises ToolingException: If resource file doesn't exist.
	"""
	# TODO: files() has wrong TypeHint Traversible vs. Path
	resourcePath: Path = files(module) / filename
	if not resourcePath.exists():
		from pyTooling.Exceptions import ToolingException

		raise ToolingException(f"Resource file '{filename}' not found in resource '{module}'.") from FileNotFoundError(str(resourcePath))

	return resourcePath


@export
def readResourceFile(module: Union[str, ModuleType], filename: str) -> str:
	"""
	Read a text file resource from resource package.

	:param module:   The resource package.
	:param filename: The filename.
	:returns:        File content.
	"""
	# TODO: check if resource exists.
	return files(module).joinpath(filename).read_text()


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
			items = getattr(obj, 'items')
			# Check if obj.items is a bound method.
			if hasattr(items, "__self__"):
				itemView = items()
			else:
				itemView = {}  # bind(obj, items)
			for key, value in itemView:
				size += recurse(key) + recurse(value)

		# Accumulate members from __dict__
		if hasattr(obj, '__dict__'):
			v = vars(obj)
			size += recurse(v)

		# Accumulate members from __slots__
		if hasattr(obj, '__slots__') and obj.__slots__ is not None:
			for slot in obj.__slots__:
				if hasattr(obj, slot):
					size += recurse(getattr(obj, slot))

		return size

	return recurse(obj)


def bind(instance, func, methodName: Nullable[str] = None):
	"""
	Bind the function *func* to *instance*, with either provided name *as_name*
	or the existing name of *func*. The provided *func* should accept the
	instance as the first argument, i.e. "self".

	:param instance:
	:param func:
	:param methodName:
	:return:
	"""
	if methodName is None:
		methodName = func.__name__

	boundMethod = func.__get__(instance, instance.__class__)
	setattr(instance, methodName, boundMethod)

	return boundMethod


@export
def count(iterator: Iterable) -> int:
	"""
	Returns the number of elements in an iterable.

	.. attention:: After counting the iterable's elements, the iterable is consumed.

	:param iterator: Iterable to consume and count.
	:return:         Number of elements in the iterable.
	"""
	return len(list(iterator))


_Element = TypeVar("Element")


@export
def firstElement(indexable: Union[List[_Element], Tuple[_Element, ...]]) -> _Element:
	"""
	Returns the first element from an indexable.

	:param indexable: Indexable to get the first element from.
	:return:          First element.
	"""
	return indexable[0]


@export
def lastElement(indexable: Union[List[_Element], Tuple[_Element, ...]]) -> _Element:
	"""
	Returns the last element from an indexable.

	:param indexable: Indexable to get the last element from.
	:return:          Last element.
	"""
	return indexable[-1]


@export
def firstItem(iterable: Iterable[_Element]) -> _Element:
	"""
	Returns the first item from an iterable.

	:param iterable:    Iterable to get the first item from.
	:return:            First item.
	:raises ValueError: If parameter 'iterable' contains no items.
	"""
	i = iter(iterable)
	try:
		return next(i)
	except StopIteration:
		raise ValueError(f"Iterable contains no items.")


@export
def lastItem(iterable: Iterable[_Element]) -> _Element:
	"""
	Returns the last item from an iterable.

	:param iterable:    Iterable to get the last item from.
	:return:            Last item.
	:raises ValueError: If parameter 'iterable' contains no items.
	"""
	i = iter(iterable)
	try:
		element = next(i)
	except StopIteration:
		raise ValueError(f"Iterable contains no items.")

	for element in i:
		pass
	return element


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

	:param d:           Dictionary to get the first key from.
	:returns:           The first key.
	:raises ValueError: If parameter 'd' is an empty dictionary.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.keys()))


@export
def firstValue(d: Dict[_DictKey1, _DictValue1]) -> _DictValue1:
	"""
	Retrieves the first value from a dictionary's values.

	:param d:           Dictionary to get the first value from.
	:returns:           The first value.
	:raises ValueError: If parameter 'd' is an empty dictionary.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.values()))


@export
def firstPair(d: Dict[_DictKey1, _DictValue1]) -> Tuple[_DictKey1, _DictValue1]:
	"""
	Retrieves the first key-value-pair from a dictionary.

	:param d:           Dictionary to get the first key-value-pair from.
	:returns:           The first key-value-pair as tuple.
	:raises ValueError: If parameter 'd' is an empty dictionary.
	"""
	if len(d) == 0:
		raise ValueError(f"Dictionary is empty.")

	return next(iter(d.items()))


@export
def mergedicts(*dicts: Dict, filter: Nullable[Callable[[Hashable, Any], bool]] = None) -> Dict:
	"""
	Merge multiple dictionaries into a single new dictionary.

	If parameter ``filter`` isn't ``None``, then this function is applied to every element during the merge operation. If
	it returns true, the dictionary element will be present in the resulting dictionary.

	:param dicts:       Tuple of dictionaries to merge as positional parameters.
	:param filter:      Optional filter function to apply to each dictionary element when merging.
	:returns:           A new dictionary containing the merge result.
	:raises ValueError: If 'mergedicts' got called without any dictionaries parameters.

	.. seealso::

	   `How do I merge two dictionaries in a single expression in Python? <https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python>`__
	"""
	if len(dicts) == 0:
		raise ValueError(f"Called 'mergedicts' without any dictionary parameter.")

	if filter is None:
		return {k: v for d in dicts for k, v in d.items()}
	else:
		return {k: v for d in dicts for k, v in d.items() if filter(k, v)}


@export
def zipdicts(*dicts: Dict) -> Generator[Tuple, None, None]:
	"""
	Iterate multiple dictionaries simultaneously.

	:param dicts:       Tuple of dictionaries to iterate as positional parameters.
	:returns:           A generator returning a tuple containing the key and values of each dictionary in the order of
	                    given dictionaries.
	:raises ValueError: If 'zipdicts' got called without any dictionary parameters.
	:raises ValueError: If not all dictionaries have the same length.

	.. seealso::

	   The code is based on code snippets and ideas from:

	   * `zipping together Python dicts <https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/101_zip_dict>`__ (MIT Lizense)
	"""
	if len(dicts) == 0:
		raise ValueError(f"Called 'zipdicts' without any dictionary parameter.")

	if any(len(d) != len(dicts[0]) for d in dicts):
		raise ValueError(f"All given dictionaries must have the same length.")

	def gen(ds: Tuple[Dict, ...]) -> Generator[Tuple, None, None]:
		for key, item0 in ds[0].items():
			# WORKAROUND: using redundant parenthesis for Python 3.7 and pypy-3.10
			yield key, item0, *(d[key] for d in ds[1:])

	return gen(dicts)


@export
class ChangeDirectory:
	"""
	A context manager for changing a directory.
	"""
	_oldWorkingDirectory: Path  #: Working directory before directory change.
	_newWorkingDirectory: Path  #: New working directory.

	def __init__(self, directory: Path) -> None:
		"""
		Initializes the context manager for changing directories.

		:param directory: The new working directory to change into.
		"""
		self._newWorkingDirectory = directory

	def __enter__(self) -> Path:
		"""
		Enter the context and change the working directory to the parameter given in the class initializer.

		:returns: The relative path between old and new working directories.
		"""
		self._oldWorkingDirectory = Path.cwd()
		chdir(self._newWorkingDirectory)

		if self._newWorkingDirectory.is_absolute():
			return self._newWorkingDirectory.resolve()
		else:
			return (self._oldWorkingDirectory / self._newWorkingDirectory).resolve()

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and revert any working directory changes.

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		:returns:        ``None``
		"""
		chdir(self._oldWorkingDirectory)
