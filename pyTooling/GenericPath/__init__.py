# ==================================================================================================================== #
#             _____           _ _               ____                      _      ____       _   _                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| ___ _ __   ___ _ __(_) ___|  _ \ __ _| |_| |__                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |  _ / _ \ '_ \ / _ \ '__| |/ __| |_) / _` | __| '_ \                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |_| |  __/ | | |  __/ |  | | (__|  __/ (_| | |_| | | |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|\___|_| |_|\___|_|  |_|\___|_|   \__,_|\__|_| |_|                 #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A generic path to derive domain specific path libraries.

.. seealso::

   :mod:`pyTooling.GenericPath.URL`
      |rarr| A URL as a domain-specific path.
   :mod:`pyTooling.Configuration`
      |rarr| Path expressions addressing a node in a configuration.
"""
from __future__            import annotations

from typing                import ClassVar, Optional as Nullable, Union

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType


@export
class Base(metaclass=ExtendedType, mixin=True):
	"""Base-mixin-class for all :mod:`pyTooling.GenericPath` path elements."""

	DELIMITER: ClassVar[str] = "/"  #: Path element delimiter sign.

	_parent: Nullable[Base]         #: Reference to the parent object.

	def __init__(self, parent: Nullable[Base] = None) -> None:
		"""
		Initialize the base-mixin-class with a parent reference.

		:param parent: Optional, parent reference.
		"""
		self._parent = parent


@export
class RootMixin(Base, mixin=True):
	"""Mixin-class for root elements in a path system."""

	def __init__(self) -> None:
		"""
		Initialize the mixin-class for a root element.
		"""
		super().__init__(None)


@export
class ElementMixin(Base, mixin=True):
	"""Mixin-class for elements in a path system."""

	_elementName: str  #: Name of the path element.

	def __init__(self, parent: Base, elementName: str) -> None:
		"""
		Initialize the mixin-class for a path element.

		:param parent:      Optional, reference to a parent path element.
		:param elementName: Name of the path element.
		"""
		super().__init__(parent)

		self._elementName = elementName

	def __str__(self) -> str:
		"""
		Return a string representation of this path element.

		:returns: The element's name.
		"""
		return self._elementName


@export
class PathMixin(metaclass=ExtendedType, mixin=True):
	"""Mixin-class for a path."""

	ELEMENT_DELIMITER: ClassVar[str] = "/"           #: Path element delimiter sign.
	ROOT_DELIMITER:    ClassVar[str] = "/"           #: Root element delimiter sign.
	ELEMENT_TYPE:      ClassVar[type[ElementMixin]]  #: Type an element of this path flavour has. Every flavour names it.

	_isAbsolute: bool                       #: True, if the path is absolute.
	_elements:   list[ElementMixin]         #: List of path elements.

	def __init__(self, elements: list[ElementMixin], isAbsolute: bool) -> None:
		"""
		Initialize the mixin-class for a path.

		:param elements:   Reference to a parent path element.
		:param isAbsolute: ``True``, if the path is absolute, otherwise ``False``.
		"""
		self._isAbsolute = isAbsolute
		self._elements =   elements

	def __len__(self) -> int:
		"""
		Returns the number of path elements.

		:returns: Number of path elements.
		"""
		return len(self._elements)

	def __str__(self) -> str:
		"""
		Return a string representation of this path.

		:returns: The path's elements, joined by the delimiter, prefixed by the root delimiter if the path is absolute.
		"""
		result = self.ROOT_DELIMITER if self._isAbsolute else ""

		if len(self._elements) > 0:
			result = result + str(self._elements[0])

			for element in self._elements[1:]:
				result = result + self.ELEMENT_DELIMITER + str(element)

		return result

	def __truediv__(self, other: Union[str, PathMixin]) -> PathMixin:
		"""
		Return this path with another path below it.

		A trailing delimiter is dropped before appending, so composing ``/api/`` with ``things`` names
		``/api/things`` and not an empty element between them. An absolute path names where it starts itself, so it
		replaces this one rather than being appended - as :rfc:`3986` resolves a reference and :mod:`pathlib` joins a
		path.

		:param other:      The path to append, as a string to parse or as a path.
		:returns:          A new path, or ``other``, if that one is absolute.
		:raises TypeError: If parameter 'other' is neither of type :class:`str` nor of type :class:`PathMixin`.
		"""
		if isinstance(other, str):
			isAbsolute = other.startswith(self.ROOT_DELIMITER)
			names =      (other[len(self.ROOT_DELIMITER):] if isAbsolute else other).split(self.ELEMENT_DELIMITER)
		elif isinstance(other, PathMixin):
			isAbsolute = other._isAbsolute
			names =      [str(element) for element in other._elements]
		else:
			ex = TypeError("Second operand is not supported by / operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: 'str' or '{getFullyQualifiedName(self)}'.")
			raise ex

		if isAbsolute:
			path =     self
			elements = []
		else:
			path =     self.WithoutTrailingDelimiter()
			elements = list(path._elements)

		parent =   elements[-1] if len(elements) > 0 else None
		for name in names:
			elements.append(parent := self.ELEMENT_TYPE(parent, name))

		return self.__class__(elements, isAbsolute or path._isAbsolute)

	def WithoutTrailingDelimiter(self) -> PathMixin:
		"""
		Return a path that doesn't end in :attr:`ELEMENT_DELIMITER`.

		A trailing delimiter is an empty last element, so ``/api/v3/`` and ``/api/v3`` are different paths although
		they usually name the same thing. A path that something is appended to wants the latter, or the composition
		yields two delimiters in a row.

		Only one trailing delimiter is removed: a path ending in two of them names an empty element and then another,
		which isn't the same as naming neither.

		:returns: A new path without a trailing delimiter, or this path, if it has none.
		"""
		if (elementCount := len(self._elements)) == 0 or str(self._elements[-1]) != "":
			return self
		elif elementCount > 1:
			return self.__class__(self._elements[:-1], self._isAbsolute)

		# A path of nothing but the empty element is the root: it has no element to drop, so it stops being absolute.
		# The same path that isn't absolute is the empty path, which has no trailing delimiter to begin with.
		return self if not self._isAbsolute else self.__class__(self._elements, False)

	@classmethod
	def Parse(cls, path: str, root: Nullable[RootMixin] = None) -> PathMixin:
		"""
		Parses a string representation of a path and returns a path instance.

		The path and its elements are of this flavour's types - the class this is called on, and the
		:attr:`ELEMENT_TYPE` it names.

		:param path: Path to be parsed.
		:param root: Optional, root element the parsed path is relative to. Default: no root.
		:returns:    A path instance of this class.
		"""
		if path.startswith(cls.ROOT_DELIMITER):
			isAbsolute = True
			path =       path[len(cls.ROOT_DELIMITER):]
		else:
			isAbsolute = False

		parent =   root
		elements = []
		for part in path.split(cls.ELEMENT_DELIMITER):
			elements.append(parent := cls.ELEMENT_TYPE(parent, part))

		return cls(elements, isAbsolute)


@export
class SystemMixin(metaclass=ExtendedType, mixin=True):
	"""Mixin-class for a path system."""
