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
# Copyright 2021-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from pathlib       import Path
from typing        import Union, ClassVar, Iterator, Type, Optional as Nullable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType, mixin
	from pyTooling.Exceptions  import ToolingException
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Configuration] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, mixin
		from Exceptions          import ToolingException
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Configuration] Could not import directly!")
		raise ex


KeyT = Union[str, int]
NodeT = Union["Dictionary", "Sequence"]
ValueT = Union[NodeT, str, int, float]


@export
class ConfigurationException(ToolingException):
	pass


@export
class Node(metaclass=ExtendedType, slots=True):
	"""Abstract node in a configuration data structure."""

	DICT_TYPE: ClassVar[Type["Dictionary"]]  #: Type reference used when instantiating new dictionaries
	SEQ_TYPE:  ClassVar[Type["Sequence"]]    #: Type reference used when instantiating new sequences
	_root:     "Configuration"               #: Reference to the root node.
	_parent:   "Dictionary"                  #: Reference to a parent node.

	def __init__(self, root: "Configuration" = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a node.

		:param root:   Reference to the root node.
		:param parent: Reference to the parent node.
		"""
		self._root = root
		self._parent = parent

	def __len__(self) -> int:  # type: ignore[empty-body]
		"""
		Returns the number of sub-elements.

		:returns: Number of sub-elements.
		"""

	def __getitem__(self, key: KeyT) -> ValueT:  # type: ignore[empty-body]
		raise NotImplementedError()

	def __setitem__(self, key: KeyT, value: ValueT) -> None:  # type: ignore[empty-body]
		raise NotImplementedError()

	def __iter__(self) -> Iterator[ValueT]:  # type: ignore[empty-body]
		raise NotImplementedError()

	@property
	def Key(self) -> KeyT:
		raise NotImplementedError()

	@Key.setter
	def Key(self, value: KeyT):
		raise NotImplementedError()

	def QueryPath(self, query: str) -> ValueT:  # type: ignore[empty-body]
		raise NotImplementedError()


@export
@mixin
class Dictionary(Node):
	"""Abstract dictionary node in a configuration."""

	def __init__(self, root: "Configuration" = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a dictionary.

		:param root:   Reference to the root node.
		:param parent: Reference to the parent node.
		"""
		Node.__init__(self, root, parent)

	def __contains__(self, key: KeyT) -> bool:  # type: ignore[empty-body]
		raise NotImplementedError()


@export
@mixin
class Sequence(Node):
	"""Abstract sequence node in a configuration."""

	def __init__(self, root: "Configuration" = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a sequence.

		:param root:   Reference to the root node.
		:param parent: Reference to the parent node.
		"""
		Node.__init__(self, root, parent)

	def __getitem__(self, index: int) -> ValueT:  # type: ignore[empty-body]
		raise NotImplementedError()

	def __setitem__(self, index: int, value: ValueT) -> None:  # type: ignore[empty-body]
		raise NotImplementedError()


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
@mixin
class Configuration(Node):
	"""Abstract root node in a configuration."""

	_configFile:   Path

	def __init__(self, configFile: Path, root: "Configuration" = None, parent: Nullable[NodeT] = None) -> None:
		"""
		Initializes a configuration.

		:param configFile: Configuration file.
		:param root:       Reference to the root node.
		:param parent:     Reference to the parent node.
		"""
		Node.__init__(self, root, parent)
		self._configFile = configFile

	@readonly
	def ConfigFile(self) -> Path:
		return self._configFile
