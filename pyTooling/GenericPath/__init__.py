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
"""A generic path to derive domain specific path libraries."""
from typing import List, Optional as Nullable

from pyTooling.Decorators import export


@export
class Base:
	"""Base-class for all pyTooling.GenericPath path elements."""

	DELIMITER = "/"

	_parent: Nullable["Base"]

	def __init__(self, parent: Nullable["Base"]):
		self._parent = parent


@export
class RootMixIn(Base):
	"""Mixin-class for root elements in a path system."""

	def __init__(self):
		super().__init__(None)


@export
class ElementMixIn(Base):
	"""Mixin-class for elements in a path system."""

	_elementName: str

	def __init__(self, parent: Base, elementName: str):
		super().__init__(parent)
		self._elementName = elementName

	def __str__(self) -> str:
		return self._elementName


@export
class PathMixIn:
	"""Mixin-class for a path."""

	ELEMENT_DELIMITER = "/"
	ROOT_DELIMITER =    "/"

	_isAbsolute: bool
	_elements:   List[ElementMixIn]

	def __init__(self, elements: List[ElementMixIn], isAbsolute: bool):
		self._isAbsolute = isAbsolute
		self._elements =   elements

	def __len__(self) -> int:
		return len(self._elements)

	def __str__(self) -> str:
		result = self.ROOT_DELIMITER if self._isAbsolute else ""

		if (len(self._elements) > 0):
			result = result + str(self._elements[0])

			for element in self._elements[1:]:
				result = result + self.ELEMENT_DELIMITER + str(element)

		return result

	@classmethod
	def Parse(cls, path: str, root, pathCls, elementCls):
		"""Parses a string representation of a path and returns a path instance."""

		parent = root

		if path.startswith(cls.ROOT_DELIMITER):
			isAbsolute = True
			path = path[len(cls.ELEMENT_DELIMITER):]
		else:
			isAbsolute = False

		parts = path.split(cls.ELEMENT_DELIMITER)
		elements = []
		for part in parts:
			element = elementCls(parent, part)
			parent =  element
			elements.append(element)

		return pathCls(elements, isAbsolute)


@export
class SystemMixIn:
	"""Mixin-class for a path system."""
