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
"""A generic path to derive domain specific path libraries."""
from typing import List, Optional as Nullable, Type

try:
	from pyTooling.Decorators  import export
	from pyTooling.MetaClasses import ExtendedType
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.GenericPath] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export
		from MetaClasses         import ExtendedType
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.GenericPath] Could not import directly!")
		raise ex


@export
class Base(metaclass=ExtendedType, mixin=True):
	"""Base-mixin-class for all :mod:`pyTooling.GenericPath` path elements."""

	DELIMITER = "/"            #: Path element delimiter sign.

	_parent: Nullable["Base"]  #: Reference to the parent object.

	def __init__(self, parent: Nullable["Base"] = None) -> None:
		"""
		Initialize the base-mixin-class with a parent reference.

		:param parent: Optional parent reference.
		"""
		self._parent = parent


@export
class RootMixIn(Base, mixin=True):
	"""Mixin-class for root elements in a path system."""

	def __init__(self) -> None:
		"""
		Initialize the mixin-class for a root element.
		"""
		super().__init__(None)


@export
class ElementMixIn(Base, mixin=True):
	"""Mixin-class for elements in a path system."""

	_elementName: str  #: Name of the path element.

	def __init__(self, parent: Base, elementName: str) -> None:
		"""
		Initialize the mixin-class for a path element.

		:param parent:      Reference to a parent path element.
		:param elementName: Name of the path element.
		"""
		super().__init__(parent)

		self._elementName = elementName

	def __str__(self) -> str:
		return self._elementName


@export
class PathMixIn(metaclass=ExtendedType, mixin=True):
	"""Mixin-class for a path."""

	ELEMENT_DELIMITER = "/"          #: Path element delimiter sign.
	ROOT_DELIMITER =    "/"          #: Root element delimiter sign.

	_isAbsolute: bool                #: True, if the path is absolute.
	_elements:   List[ElementMixIn]  #: List of path elements.

	def __init__(self, elements: List[ElementMixIn], isAbsolute: bool) -> None:
		"""
		Initialize the mixin-class for a path.

		:param elements:   Reference to a parent path element.
		:param isAbsolute: Assign to true, if a path is absolute, otherwise false.
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
		result = self.ROOT_DELIMITER if self._isAbsolute else ""

		if len(self._elements) > 0:
			result = result + str(self._elements[0])

			for element in self._elements[1:]:
				result = result + self.ELEMENT_DELIMITER + str(element)

		return result

	@classmethod
	def Parse(
		cls,
		path: str,
		root: RootMixIn,
		pathCls: Type["PathMixIn"],
		elementCls: Type[ElementMixIn]
	) -> "PathMixIn":
		"""
		Parses a string representation of a path and returns a path instance.

		:param path:       Path to be parsed.
		:param root:
		:param pathCls:    Type used to create the path.
		:param elementCls: Type used to create the path elements.
		:return:
		"""
		if path.startswith(cls.ROOT_DELIMITER):
			isAbsolute = True
			path = path[len(cls.ELEMENT_DELIMITER):]
		else:
			isAbsolute = False

		parent = root
		elements = []
		for part in path.split(cls.ELEMENT_DELIMITER):
			element = elementCls(parent, part)
			parent = element
			elements.append(element)

		return pathCls(elements, isAbsolute)


@export
class SystemMixIn(metaclass=ExtendedType, mixin=True):
	"""Mixin-class for a path system."""
