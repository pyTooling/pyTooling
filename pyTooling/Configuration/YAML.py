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
"""
Configuration reader for YAML files.

.. hint:: See :ref:`high-level help <CONFIG/FileFormat/YAML>` for explanations and usage examples.
"""
from pathlib import Path
from typing import Dict, List, Union, Iterator as typing_Iterator

from ..Decorators import export
from ..MetaClasses import ExtendedType

try:
	from ruamel.yaml import YAML, CommentedMap, CommentedSeq
except ImportError as ex:  # pragma: no cover
	raise Exception(f"Optional dependency 'ruamel.yaml' not installed. Either install pyTooling with extra dependencies 'pyTooling[yaml]' or install 'ruamel.yaml' directly.") from ex

from . import (
	Node as Abstract_Node,
	Dictionary as Abstract_Dict,
	Sequence as Abstract_Seq,
	Configuration as Abstract_Configuration,
	KeyT, NodeT, ValueT
)


@export
class Node(Abstract_Node):
	_yamlNode: Union[CommentedMap, CommentedSeq]
	_cache: Dict[str, ValueT]
	_key: KeyT
	_length: int

	def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, yamlNode: Union[CommentedMap, CommentedSeq]):
		super().__init__(root, parent)
		self._yamlNode = yamlNode
		self._cache = {}
		self._key = key
		self._length = len(yamlNode)

	def __len__(self) -> int:
		return self._length

	def __getitem__(self, key: KeyT) -> ValueT:
		return self._GetNodeOrValue(str(key))

	@property
	def Key(self) -> KeyT:
		return self._key

	@Key.setter
	def Key(self, value: KeyT) -> None:
		raise NotImplementedError()

	def QueryPath(self, query: str) -> ValueT:
		path = self._ToPath(query)
		return self._GetNodeOrValueByPathExpression(path)

	@staticmethod
	def _ToPath(query: str) -> List[Union[str, int]]:
		return query.split(":")

	def _GetNodeOrValue(self, key: str) -> ValueT:
		try:
			value = self._cache[key]
		except KeyError:
			try:
				value = self._yamlNode[key]
			except (KeyError, TypeError):
				try:
					value = self._yamlNode[int(key)]
				except KeyError:
					try:
						value = self._yamlNode[float(key)]
					except KeyError as ex:
						raise Exception(f"") from ex         # XXX: needs error message

			if isinstance(value, str):
				value = self._ResolveVariables(value)
			elif isinstance(value, (int, float)):
				value = str(value)
			elif isinstance(value, CommentedMap):
				value = self.DICT_TYPE(self, self, key, value)
			elif isinstance(value, CommentedSeq):
				value = self.SEQ_TYPE(self, self, key, value)
			else:
				raise Exception(f"") from TypeError(f"Unknown type '{value.__class__.__name__}' returned from ruamel.yaml.") # XXX: error message

			self._cache[key] = value

		return value

	def _ResolveVariables(self, value: str) -> str:
		if value == "":
			return ""
		elif "$" not in value:
			return value

		rawValue = value
		result = ""

		while (len(rawValue) > 0):
#			print(f"_ResolveVariables: LOOP    rawValue='{rawValue}'")
			beginPos = rawValue.find("$")
			if (beginPos < 0):
				result  += rawValue
				rawValue = ""
			else:
				result += rawValue[:beginPos]
				if (rawValue[beginPos + 1] == "$"):
					result  += "$"
					rawValue = rawValue[1:]
				elif (rawValue[beginPos + 1] == "{"):
					endPos =  rawValue.find("}", beginPos)
					nextPos =  rawValue.rfind("$", beginPos, endPos)
					if (endPos < 0):
						raise Exception(f"")  # XXX: InterpolationSyntaxError(option, section, f"Bad interpolation variable reference {rest!r}")
					if ((nextPos > 0) and (nextPos < endPos)):  # an embedded $-sign
						path = rawValue[nextPos+2:endPos]
#						print(f"_ResolveVariables: path='{path}'")
						innervalue = self._GetValueByPathExpression(self._ToPath(path))
#						print(f"_ResolveVariables: innervalue='{innervalue}'")
						rawValue = rawValue[beginPos:nextPos] + str(innervalue) + rawValue[endPos + 1:]
#						print(f"_ResolveVariables: new rawValue='{rawValue}'")
					else:
						path = rawValue[beginPos+2:endPos]
						rawValue = rawValue[endPos+1:]
						result  += str(self._GetValueByPathExpression(self._ToPath(path)))

		return result

	def _GetValueByPathExpression(self, path: List[KeyT]) -> ValueT:
		node = self
		for p in path:
			if p == "..":
				node = node._parent
			else:
				node = node._GetNodeOrValue(p)

		if isinstance(node, Dictionary):
			raise Exception(f"Error when resolving path expression '{':'.join(path)}' at '{p}'.") from TypeError(f"")     # XXX: needs error messages

		return node

	def _GetNodeOrValueByPathExpression(self, path: List[KeyT]) -> ValueT:
		node = self
		for p in path:
			if p == "..":
				node = node._parent
			else:
				node = node._GetNodeOrValue(p)

		return node


@export
class Dictionary(Abstract_Dict, Node):
	"""A dictionary node in a YAML data file."""

	_keys: List[KeyT]

	def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, yamlNode: CommentedMap):
		Node.__init__(self, root, parent, key, yamlNode)
		self._keys = [str(k) for k in yamlNode.keys()]

	def __contains__(self, key: KeyT) -> bool:
		return key in self._keys

	def __iter__(self) -> typing_Iterator[ValueT]:
		class Iterator(metaclass=ExtendedType, useSlots=True):
			_iter: typing_Iterator
			_obj: Dictionary

			def __init__(self, obj: Dictionary):
				self._iter = iter(obj._keys)
				self._obj = obj

			def __iter__(self) -> "Iterator":
				"""
				Return itself to fulfil the iterator protocol.

				:returns: Itself.
				"""
				return self

			def __next__(self) -> ValueT:
				"""
				Returns the next item in the dictionary.

				:returns:              Next item.
				"""
				key = next(self._iter)
				return self._obj[key]

		return Iterator(self)


@export
class Sequence(Abstract_Seq, Node):
	"""A sequence node (ordered list) in a YAML data file."""

	def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, yamlNode: CommentedSeq):
		Node.__init__(self, root, parent, key, yamlNode)
		self._length = len(yamlNode)

	__getitem__ = Node.__getitem__

	def __iter__(self) -> typing_Iterator[ValueT]:
		"""
		Returns an iterator to iterate items in the sequence of sub-nodes.

		:returns: Iterator to iterate items in a sequence.
		"""
		class Iterator(metaclass=ExtendedType, useSlots=True):
			"""Iterator to iterate sequence items."""

			_i: int         #: internal iterator position
			_obj: Sequence  #: Sequence object to iterate

			def __init__(self, obj: Sequence):
				self._i = 0
				self._obj = obj

			def __iter__(self) -> "Iterator":
				"""
				Return itself to fulfil the iterator protocol.

				:returns: Itself.
				"""
				return self

			def __next__(self) -> ValueT:
				"""
				Returns the next item in the sequence.

				:returns:              Next item.
				:raises StopIteration: If end of sequence is reached.
				"""
				try:
					result = self._obj[str(self._i)]
					self._i += 1
					return result
				except IndexError:
					raise StopIteration

		return Iterator(self)


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
class Configuration(Abstract_Configuration, Dictionary):
	"""A configuration read from a YAML file."""

	_yamlConfig: YAML

	def __init__(self, configFile: Path):
		"""
		Initializes a configuration instance that reads a YAML file as input.

		All sequence items or dictionaries key-value-pairs in the YAML file are accessible via Python's dictionary syntax.

		:param configFile: Configuration file to read and parse.
		"""
		Abstract_Configuration.__init__(self)

		with configFile.open() as file:
			self._yamlConfig = YAML().load(file)

		Dictionary.__init__(self, self, self, None, self._yamlConfig)

	def __getitem__(self, key: str) -> ValueT:
		"""
		Access a configuration node by key.

		:param key: The key to look for.
		:returns:   A node (seuqence or dictionary) or scalar value (int, float, str).
		"""
		return self._GetNodeOrValue(str(key))

	def __setitem__(self, key: str, value: ValueT) -> None:
		raise NotImplementedError()
