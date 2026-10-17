# ==================================================================================================================== #
#             _____           _ _               ____        _        __  __           _      _                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  __ _| |_ __ _|  \/  | ___   __| | ___| |                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _` | __/ _` | |\/| |/ _ \ / _` |/ _ \ |                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | (_| | || (_| | |  | | (_) | (_| |  __/ |                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__,_|\__\__,_|_|  |_|\___/ \__,_|\___|_|                        #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Foundations of data models: building blocks the classes of a data model share.

A :class:`KeyValuePairsMixin` attaches arbitrary key-value-pairs to an element of a data model, accessed like a
dictionary: :pycode:`element["runner.os"] = "Linux"`. :data:`Predicate` is the type of a function selecting
elements, e.g. in an ``Iterate***`` method.

.. hint::

   See :ref:`high-level help <STRUCT/DataModel>` for explanations and usage examples.
"""
from __future__            import annotations

from typing                import Any, Callable, Hashable, Iterator, Mapping, Optional as Nullable, TypeVar

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType


__all__ = ["ElementType", "Predicate"]


ElementType = TypeVar("ElementType")
"""A type variable for the element a :data:`Predicate` decides on."""

Predicate = Callable[[ElementType], bool]
"""
A function deciding whether an element is selected.

``Predicate[Vertex]`` is ``Callable[[Vertex], bool]``. Methods filtering what they iterate, reverse or remove take a
predicate, e.g. :meth:`pyTooling.Graph.BaseGraph.IterateVertices`.
"""


@export
class KeyValuePairsMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class adding arbitrary key-value-pairs to an element of a data model, accessed like a dictionary.

	* :pycode:`element[key]` reads a value.
	* :pycode:`element.get(key, default)` reads a value, or a default value, if the key doesn't exist.
	* :pycode:`element[key] = value` creates or updates a pair.
	* :pycode:`del element[key]` removes a pair.
	* :pycode:`key in element` checks for a key.
	* :pycode:`len(element)` counts the pairs.
	* :pycode:`for key in element:` iterates the keys.
	"""

	_dict: dict[Hashable, Any]  #: A dictionary to store arbitrary key-value-pairs.

	def __init__(self, keyValuePairs: Nullable[Mapping[Hashable, Any]] = None) -> None:
		"""
		Initializes the key-value-pairs.

		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		"""
		if keyValuePairs is None:
			self._dict = {}
			return
		elif not isinstance(keyValuePairs, Mapping):
			ex = TypeError("Parameter 'keyValuePairs' is not a mapping ('dict', ...).")
			ex.add_note(f"Got type '{getFullyQualifiedName(keyValuePairs)}'.")
			raise ex

		self._dict = dict(keyValuePairs)

	def get(self, key: Hashable, default: Any = None) -> Any:
		"""
		Read an attached attribute (key-value-pair) by key, or a default value, if the key doesn't exist.

		This method is spelled the way :meth:`dict.get` is, because that is the behaviour it offers.

		:param key:     The key to look for.
		:param default: Optional, the value returned if the key isn't an attached attribute. Default: ``None``.
		:returns:       The value associated to the given key, otherwise the default value.
		"""
		return self._dict.get(key, default)

	def __getitem__(self, key: Hashable) -> Any:
		"""
		Read an attached attribute (key-value-pair) by key.

		:param key:       The key to look for.
		:returns:         The value associated to the given key.
		:raises KeyError: If key doesn't exist in the attached attributes.
		"""
		return self._dict[key]

	def __setitem__(self, key: Hashable, value: Any) -> None:
		"""
		Create or update an attached attribute (key-value-pair) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key:   The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: Hashable) -> None:
		"""
		Remove an attached attribute (key-value-pair) by key.

		:param key:       The key to remove.
		:raises KeyError: If key doesn't exist in the attached attributes.
		"""
		del self._dict[key]

	def __contains__(self, key: Hashable) -> bool:
		"""
		Check if the key is an attached attribute (key-value-pair).

		:param key: The key to check.
		:returns:   ``True``, if the key is an attached attribute.
		"""
		return key in self._dict

	def __len__(self) -> int:
		"""
		Return the number of attached attributes (key-value-pairs).

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	def __iter__(self) -> Iterator[Hashable]:
		"""
		Iterate the keys of the attached attributes (key-value-pairs).

		:returns: An iterator over the keys, in the order they were added.
		"""
		return iter(self._dict)
