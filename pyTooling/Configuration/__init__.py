# ==================================================================================================================== #
#             _____           _ _               ____             __ _                       _   _                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | |         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|         #
# |_|    |___/                          |___/                         |___/                                            #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2021-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Abstract configuration reader.

.. hint::

   See :ref:`high-level help <CONFIG>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Configuration.JSON`
      |rarr| A configuration read from a JSON file.
   :mod:`pyTooling.Configuration.YAML`
      |rarr| A configuration read from a YAML file.
   :mod:`pyTooling.GenericPath`
      |rarr| The path expressions a configuration is queried with.
"""
from __future__            import annotations

from pathlib               import Path
from typing                import Union, ClassVar, Generator, Iterator, Optional as Nullable, Tuple

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod, mixin
from pyTooling.Exceptions  import ConfigurationError


__all__ = ["KeyT", "NodeT", "ValueT"]


KeyT =   Union[str, int]                  #: Type variable for keys.
NodeT =  Union["Dictionary", "Sequence"]  #: Type variable for nodes.
ValueT = Union[NodeT, str, int, float]    #: Type variable for values.


@export
class KeyNotFoundError(ConfigurationError, KeyError):
	"""
	The requested key or index doesn't exist in the configuration node.

	The key was neither found as a string, nor converted to an integer or float. A note lists the keys or the index
	range offered by the node.

	It is a :exc:`KeyError` as well, because a dictionary node answers the mapping protocol and the code reading it
	writes ``except KeyError``. Catching :exc:`~pyTooling.Exceptions.ConfigurationError` still catches it.
	"""


@export
class UnsupportedValueTypeError(ConfigurationError):
	"""
	The configuration file parser returned a value of a type that isn't supported by :mod:`pyTooling.Configuration`.

	Supported are scalars (:class:`str`, :class:`int`, :class:`float`) and the parser's dictionary and sequence types.
	"""


@export
class InterpolationError(ConfigurationError):
	"""A variable reference (``${...}``) in a configuration value is malformed or can't be resolved."""


@export
class PathExpressionError(ConfigurationError):
	"""A path expression (``a:b:c``) doesn't describe a valid node or value in the configuration."""


@export
class Node(metaclass=ExtendedType, slots=True):
	"""Abstract node in a configuration data structure."""

	DICT_TYPE: ClassVar[type[Dictionary]]  #: Type reference used when instantiating new dictionaries
	SEQ_TYPE:  ClassVar[type[Sequence]]    #: Type reference used when instantiating new sequences
	_root:     Configuration               #: Reference to the root node.
	_parent:   Dictionary                  #: Reference to a parent node.

	def __init__(self, root: Nullable[Configuration] = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a node.

		:param root:   Optional, reference to the root node.
		:param parent: Optional, reference to the parent node.
		"""
		self._root = root
		self._parent = parent

	@abstractmethod
	def __len__(self) -> int:  # type: ignore[empty-body]
		"""
		Returns the number of sub-elements.

		:returns: Number of sub-elements.
		"""

	@abstractmethod
	def __getitem__(self, key: KeyT) -> ValueT:  # type: ignore[empty-body]
		"""
		Access an element in the node by index or key.

		:param key: Index or key of the element.
		:returns:   A node (sequence or dictionary) or scalar value (int, float, str).
		"""

	def __setitem__(self, key: KeyT, value: ValueT) -> None:
		"""
		Set an element in the node by index or key.

		.. attention::

		   A configuration is **read-only**: the file format doesn't implements writing.

		:param key:                  Index or key of the element.
		:param value:                The new value of that element.
		:raises NotImplementedError: Always - a configuration is read-only.
		"""
		raise NotImplementedError("Currently, the configuration is read-only. Writing isn't implemented.")

	@abstractmethod
	def __iter__(self) -> Iterator[ValueT]:  # type: ignore[empty-body]
		"""
		Returns an iterator to iterate a node.

		:returns: Node iterator.
		"""

	@property
	def Key(self) -> KeyT:
		"""
		Property to access the node's key.

		:returns:                    Key of the node.
		:raises NotImplementedError: If a deriving class doesn't implement this property.
		"""
		raise NotImplementedError(f"Property 'Key' is abstract and not implemented by '{self.__class__.__name__}'.")

	@Key.setter
	def Key(self, value: KeyT) -> None:
		raise NotImplementedError("Renaming a key isn't supported by a configuration.")

	@abstractmethod
	def QueryPath(self, query: str) -> ValueT:  # type: ignore[empty-body]
		"""
		Return a node or value based on a path description to that node or value.

		:param query: String describing the path to the node or value.
		:returns:     A node (sequence or dictionary) or scalar value (int, float, str).
		"""


@export
@mixin
class Dictionary(Node):
	"""Abstract dictionary node in a configuration."""

	_keys: list[KeyT]  #: Keys of this dictionary node, in the order the document states them.

	def __init__(self, keys: list[KeyT]) -> None:
		"""
		Initializes the dictionary's keys.

		A deriving class reads the keys from whatever it parsed and hands them over, so this node is never left
		without them. Being a mixin's constructor, it initializes only the field this mixin adds.

		:param keys: Keys of this dictionary node, in the order the document states them.
		"""
		self._keys = keys

	def __contains__(self, key: KeyT) -> bool:
		"""
		Check if a key exists in this dictionary node.

		:param key: The key to check for.
		:returns:   ``True``, if the key exists in this node.
		"""
		return key in self._keys

	def IterateKeys(self) -> Generator[KeyT, None, None]:
		"""
		Iterate the keys of this dictionary node.

		:returns: A generator of this node's keys, in the order the document states them.
		"""
		yield from self._keys

	def IterateValues(self) -> Generator[ValueT, None, None]:
		"""
		Iterate the values of this dictionary node.

		This is what :meth:`__iter__` yields, so ``for value in node`` and ``for value in node.IterateValues()`` are
		the same walk. It exists so that the three iterators can be named alike and a reader doesn't have to remember
		which of keys or values plain iteration gives.

		:returns: A generator of this node's values, in the order the document states them.
		"""
		for key in self._keys:
			yield self[key]

	def IterateItems(self) -> Generator[Tuple[KeyT, ValueT], None, None]:
		"""
		Iterate the key-value pairs of this dictionary node.

		:returns: A generator of this node's ``(key, value)`` pairs, in the order the document states them.
		"""
		for key in self._keys:
			yield key, self[key]

	def keys(self) -> Tuple[KeyT, ...]:
		"""
		Return this node's keys, so a dictionary node can be handed to code expecting a mapping.

		This is :meth:`IterateKeys` materialized. The name is :class:`dict`'s, deliberately: :class:`dict` itself
		looks for a ``keys`` method to decide whether an object is a mapping, so ``dict(node)`` and ``{**node}``
		work because this exists.

		:returns: This node's keys, in the order the document states them.
		"""
		return tuple(self._keys)

	def values(self) -> Tuple[ValueT, ...]:
		"""
		Return this node's values, so a dictionary node can be handed to code expecting a mapping.

		This is :meth:`IterateValues` materialized.

		:returns: This node's values, in the order the document states them.
		"""
		return tuple([self[key] for key in self._keys])

	def items(self) -> Tuple[Tuple[KeyT, ValueT], ...]:
		"""
		Return this node's key-value pairs, so a dictionary node can be handed to code expecting a mapping.

		This is :meth:`IterateItems` materialized.

		:returns: This node's ``(key, value)`` pairs, in the order the document states them.
		"""
		return tuple([(key, self[key]) for key in self._keys])

	def get(self, key: KeyT, default: Nullable[ValueT] = None) -> Nullable[ValueT]:
		"""
		Return the value a key names, or a default when this node doesn't state that key.

		:param key:     The key to read.
		:param default: Optional, what to return when the key isn't stated. Defaults to ``None``.
		:returns:       The value the key names, or ``default``.
		"""
		return self[key] if key in self else default


@export
@mixin
class Sequence(Node):
	"""Abstract sequence node in a configuration."""

	def __init__(self, root: Nullable[Configuration] = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a sequence.

		:param root:   Optional, reference to the root node.
		:param parent: Optional, reference to the parent node.
		"""
		Node.__init__(self, root, parent)

	@abstractmethod
	def __getitem__(self, index: int) -> ValueT:  # type: ignore[empty-body]
		"""
		Read an element of this sequence node by index.

		:param index: Index of the element to read.
		:returns:     A node (sequence or dictionary) or scalar value (int, float, str).
		"""

	def __setitem__(self, index: int, value: ValueT) -> None:
		"""
		Write an element of this sequence node by index.

		.. attention::

		   A configuration is **read-only** - see :meth:`Node.__setitem__`.

		:param index:                Index of the element to write.
		:param value:                The new value of that element.
		:raises NotImplementedError: Always - a configuration is read-only.
		"""
		raise NotImplementedError("Currently, the configuration is read-only. Writing isn't implemented.")

	def index(self, value: ValueT, start: int = 0, stop: Nullable[int] = None) -> int:
		"""
		Return the index of the first element equal to a value, so a sequence node reads like a :class:`list`.

		:param value:       The value to search for.
		:param start:       Optional, index to start searching at. Defaults to ``0``.
		:param stop:        Optional, index to stop searching before. Defaults to the end of this node.
		:returns:           Index of the first matching element.
		:raises ValueError: If no element in the searched range equals the value.
		"""
		length = len(self)
		start =  max(0, length + start if start < 0 else start)
		stop =   length if stop is None else min(length, length + stop if stop < 0 else stop)

		for index in range(start, stop):
			if self[index] == value:
				return index

		raise ValueError(f"'{value}' is not in this sequence node.")

	def count(self, value: ValueT) -> int:
		"""
		Return how many elements of this node equal a value, so a sequence node reads like a :class:`list`.

		:param value: The value to count.
		:returns:     Number of matching elements.
		"""
		return sum(1 for element in self if element == value)


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
@mixin
class Configuration(Node):
	"""Abstract root node in a configuration."""

	_configFile: Path  #: Path to the configuration file.

	def __init__(self, configFile: Path, root: Nullable[Configuration] = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a configuration.

		:param configFile: Configuration file.
		:param root:       Optional, reference to the root node.
		:param parent:     Optional, reference to the parent node.
		"""
		Node.__init__(self, root, parent)
		self._configFile = configFile

	@readonly
	def ConfigFile(self) -> Path:
		"""
		Read-only property to access the configuration file's path.

		:returns: Path to the configuration file.
		"""
		return self._configFile
