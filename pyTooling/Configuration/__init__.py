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
# Copyright 2021-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""\
Abstract configuration reader.

.. hint:: See :ref:`high-level help <CONFIG>` for explanations and usage examples.
"""
from typing import Union, ClassVar, Iterator

from ..Decorators import export
from ..MetaClasses import ExtendedType


KeyT = Union[str, int]
NodeT = Union["Dictionary", "Sequence"]
ValueT = Union[NodeT, str, int, float]


@export
class Node(metaclass=ExtendedType, useSlots=True):
	"""Abstract node in a configuration data structure."""

	DICT_TYPE: ClassVar["Dictionary"]
	SEQ_TYPE: ClassVar["Sequence"]
	_parent: "Dictionary"
	_root: "Configuration"

	def __init__(self, root: "Configuration" = None, parent: NodeT = None):
		self._root = root
		self._parent = parent

	def __len__(self) -> int:
		raise NotImplementedError()

	def __getitem__(self, key: KeyT) -> ValueT:
		raise NotImplementedError()

	def __setitem__(self, key: KeyT, value: ValueT) -> None:
		raise NotImplementedError()

	def __iter__(self) -> Iterator[ValueT]:
		raise NotImplementedError()

	@property
	def Key(self) -> KeyT:
		raise NotImplementedError()

	@Key.setter
	def Key(self, value: KeyT):
		raise NotImplementedError()

	def QueryPath(self, query: str) -> ValueT:
		raise NotImplementedError()


@export
class Dictionary(Node):
	"""Abstract dictionary node in a configuration."""

	def __contains__(self, key: KeyT) -> bool:
		raise NotImplementedError()


@export
class Sequence(Node):
	"""Abstract sequence node in a configuration."""

	def __getitem__(self, index: int) -> ValueT:
		raise NotImplementedError()

	def __setitem__(self, index: int, value: ValueT) -> None:
		raise NotImplementedError()


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
class Configuration(Node):
	"""Abstract root node in a configuration."""

	def __init__(self):
		Node.__init__(self)
