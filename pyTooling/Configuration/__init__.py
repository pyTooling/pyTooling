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
class KeyNotFoundError(ConfigurationError):
	"""
	The requested key or index doesn't exist in the configuration node.

	The key was neither found as a string, nor converted to an integer or float. A note lists the keys or the index
	range offered by the node.
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

		:returns: Key of the node.
		"""
		raise NotImplementedError()

	@Key.setter
	def Key(self, value: KeyT) -> None:
		raise NotImplementedError()

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

	def __init__(self, root: Nullable[Configuration] = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a dictionary.

		:param root:   Optional, reference to the root node.
		:param parent: Optional, reference to the parent node.
		"""
		Node.__init__(self, root, parent)

	def __contains__(self, key: KeyT) -> bool:  # type: ignore[empty-body]
		"""
		Check if a key exists in this dictionary node.

		:param key: The key to check for.
		:returns:   ``True``, if the key exists in this node.
		"""
		raise NotImplementedError()

	def IterateKeys(self) -> Generator[KeyT, None, None]:
		"""
		Iterate the keys of this dictionary node.

		:returns: A generator of this node's keys, in the order the document states them.
		"""
		raise NotImplementedError()

	def IterateValues(self) -> Generator[ValueT, None, None]:
		"""
		Iterate the values of this dictionary node.

		This is what :meth:`__iter__` yields, so ``for value in node`` and ``for value in node.IterateValues()`` are
		the same walk. It exists so that the three iterators can be named alike and a reader doesn't have to remember
		which of keys or values plain iteration gives.

		:returns: A generator of this node's values, in the order the document states them.
		"""
		raise NotImplementedError()

	def IterateItems(self) -> Generator[Tuple[KeyT, ValueT], None, None]:
		"""
		Iterate the key-value pairs of this dictionary node.

		:returns: A generator of this node's ``(key, value)`` pairs, in the order the document states them.
		"""
		raise NotImplementedError()


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

	def __getitem__(self, index: int) -> ValueT:  # type: ignore[empty-body]
		"""
		Read an element of this sequence node by index.

		:param index: Index of the element to read.
		:returns:     A node (sequence or dictionary) or scalar value (int, float, str).
		"""
		raise NotImplementedError()

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
