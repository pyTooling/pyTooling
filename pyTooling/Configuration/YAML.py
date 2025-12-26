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
"""
Configuration reader for YAML files.

.. hint::

   See :ref:`high-level help <CONFIG/FileFormat/YAML>` for explanations and usage examples.
"""
from pathlib       import Path
from typing        import Dict, List, Union, Iterator as typing_Iterator, Self

try:
	from ruamel.yaml import YAML, CommentedMap, CommentedSeq
except ImportError as ex:  # pragma: no cover
	raise Exception("Optional dependency 'ruamel.yaml' not installed. Either install pyTooling with extra dependencies 'pyTooling[yaml]' or install 'ruamel.yaml' directly.") from ex

try:
	from pyTooling.Decorators      import export
	from pyTooling.MetaClasses     import ExtendedType
	from pyTooling.Configuration   import ConfigurationException, KeyT, NodeT, ValueT
	from pyTooling.Configuration   import Node as Abstract_Node
	from pyTooling.Configuration   import Dictionary as Abstract_Dict
	from pyTooling.Configuration   import Sequence as Abstract_Seq
	from pyTooling.Configuration   import Configuration as Abstract_Configuration
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Configuration.YAML] Could not import from 'pyTooling.*'!")

	try:
		from Decorators              import export
		from MetaClasses             import ExtendedType
		from pyTooling.Configuration import ConfigurationException, KeyT, NodeT, ValueT
		from pyTooling.Configuration import Node as Abstract_Node
		from pyTooling.Configuration import Dictionary as Abstract_Dict
		from pyTooling.Configuration import Sequence as Abstract_Seq
		from pyTooling.Configuration import Configuration as Abstract_Configuration
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Configuration.YAML] Could not import directly!")
		raise ex


@export
class Node(Abstract_Node):
	"""
	Node in a YAML configuration data structure.
	"""

	_yamlNode: Union[CommentedMap, CommentedSeq]  #: Reference to the associated YAML node.
	_cache:    Dict[str, ValueT]
	_key:      KeyT                               #: Key of this node.
	_length:   int                                #: Number of sub-elements.

	def __init__(
		self,
		root:     "Configuration",
		parent:   NodeT,
		key:      KeyT,
		yamlNode: Union[CommentedMap, CommentedSeq]
	) -> None:
		"""
		Initializes a YAML node.

		:param root:     Reference to the root node.
		:param parent:   Reference to the parent node.
		:param key:
		:param yamlNode: Reference to the YAML node.
		"""
		Abstract_Node.__init__(self, root, parent)

		self._yamlNode = yamlNode
		self._cache = {}
		self._key = key
		self._length = len(yamlNode)

	def __len__(self) -> int:
		"""
		Returns the number of sub-elements.

		:returns: Number of sub-elements.
		"""
		return self._length

	def __getitem__(self, key: KeyT) -> ValueT:
		"""
		Access an element in the node by index or key.

		:param key: Index or key of the element.
		:returns:   A node (sequence or dictionary) or scalar value (int, float, str).
		"""
		return self._GetNodeOrValue(str(key))

	@property
	def Key(self) -> KeyT:
		"""
		Property to access the node's key.

		:returns: Key of the node.
		"""
		return self._key

	@Key.setter
	def Key(self, value: KeyT) -> None:
		raise NotImplementedError()

	def QueryPath(self, query: str) -> ValueT:
		"""
		Return a node or value based on a path description to that node or value.

		:param query: String describing the path to the node or value.
		:returns:     A node (sequence or dictionary) or scalar value (int, float, str).
		"""
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
			if beginPos < 0:
				result  += rawValue
				rawValue = ""
			else:
				result += rawValue[:beginPos]
				if rawValue[beginPos + 1] == "$":
					result  += "$"
					rawValue = rawValue[1:]
				elif rawValue[beginPos + 1] == "{":
					endPos =  rawValue.find("}", beginPos)
					nextPos =  rawValue.rfind("$", beginPos, endPos)
					if endPos < 0:
						raise Exception(f"")  # XXX: InterpolationSyntaxError(option, section, f"Bad interpolation variable reference {rest!r}")
					if (nextPos > 0) and (nextPos < endPos):  # an embedded $-sign
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
class Dictionary(Node, Abstract_Dict):
	"""A dictionary node in a YAML data file."""

	_keys: List[KeyT]  #: List of keys in this dictionary.

	def __init__(
		self,
		root:     "Configuration",
		parent:   NodeT,
		key:      KeyT,
		yamlNode: CommentedMap
	) -> None:
		"""
		Initializes a YAML dictionary.

		:param root:     Reference to the root node.
		:param parent:   Reference to the parent node.
		:param key:
		:param yamlNode: Reference to the YAML node.
		"""
		Node.__init__(self, root, parent, key, yamlNode)

		self._keys = [str(k) for k in yamlNode.keys()]

	def __contains__(self, key: KeyT) -> bool:
		"""
		Checks if the key is in this dictionary.

		:param key: The key to check.
		:returns:   ``True``, if the key is in the dictionary.
		"""
		return key in self._keys

	def __iter__(self) -> typing_Iterator[ValueT]:
		"""
		Returns an iterator to iterate dictionary keys.

		:returns: Dictionary key iterator.
		"""

		class Iterator(metaclass=ExtendedType, slots=True):
			"""Iterator to iterate dictionary items."""

			_iter: typing_Iterator[ValueT]
			_obj:  Dictionary

			def __init__(self, obj: Dictionary) -> None:
				"""
				Initializes an iterator for a YAML dictionary node.

				:param obj: YAML dictionary to iterate.
				"""
				self._iter = iter(obj._keys)
				self._obj = obj

			def __iter__(self) -> Self:
				"""
				Return itself to fulfil the iterator protocol.

				:returns: Itself.
				"""
				return self  # pragma: no cover

			def __next__(self) -> ValueT:
				"""
				Returns the next item in the dictionary.

				:returns: Next item.
				"""
				key = next(self._iter)
				return self._obj[key]

		return Iterator(self)


@export
class Sequence(Node, Abstract_Seq):
	"""A sequence node (ordered list) in a YAML data file."""

	def __init__(
		self,
		root:     "Configuration",
		parent:   NodeT,
		key:      KeyT,
		yamlNode: CommentedSeq
	) -> None:
		"""
		Initializes a YAML sequence (list).

		:param root:     Reference to the root node.
		:param parent:   Reference to the parent node.
		:param key:
		:param yamlNode: Reference to the YAML node.
		"""
		Node.__init__(self, root, parent, key, yamlNode)

		self._length = len(yamlNode)

	def __iter__(self) -> typing_Iterator[ValueT]:
		"""
		Returns an iterator to iterate items in the sequence of sub-nodes.

		:returns: Iterator to iterate items in a sequence.
		"""
		class Iterator(metaclass=ExtendedType, slots=True):
			"""Iterator to iterate sequence items."""

			_i:   int       #: internal iterator position
			_obj: Sequence  #: Sequence object to iterate

			def __init__(self, obj: Sequence) -> None:
				"""
				Initializes an iterator for a YAML sequence node.

				:param obj: YAML sequence to iterate.
				"""
				self._i = 0
				self._obj = obj

			def __iter__(self) -> Self:
				"""
				Return itself to fulfil the iterator protocol.

				:returns: Itself.
				"""
				return self  # pragma: no cover

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
class Configuration(Dictionary, Abstract_Configuration):
	"""A configuration read from a YAML file."""

	_yamlConfig: YAML

	def __init__(self, configFile: Path) -> None:
		"""
		Initializes a configuration instance that reads a YAML file as input.

		All sequence items or dictionaries key-value-pairs in the YAML file are accessible via Python's dictionary syntax.

		:param configFile: Configuration file to read and parse.
		"""
		if not configFile.exists():
			raise ConfigurationException(f"JSON configuration file '{configFile}' not found.") from FileNotFoundError(configFile)

		with configFile.open("r", encoding="utf-8") as file:
			self._yamlConfig = YAML().load(file)

		Dictionary.__init__(self, self, self, None, self._yamlConfig)
		Abstract_Configuration.__init__(self, configFile)

	def __getitem__(self, key: str) -> ValueT:
		"""
		Access a configuration node by key.

		:param key: The key to look for.
		:returns:   A node (sequence or dictionary) or scalar value (int, float, str).
		"""
		return self._GetNodeOrValue(str(key))

	def __setitem__(self, key: str, value: ValueT) -> None:
		raise NotImplementedError()
