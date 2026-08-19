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
Configuration reader for YAML files.

.. hint::

   See :ref:`high-level help <CONFIG/FileFormat/YAML>` for explanations and usage examples.
"""
from pathlib       import Path
from typing        import Any, Dict, List, Union, Iterator as typing_Iterator, Self

from pyTooling.Exceptions import MissingDependencyError

try:
	from ruamel.yaml import YAML, CommentedMap, CommentedSeq
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex

from pyTooling.Common          import getFullyQualifiedName
from pyTooling.Decorators      import export, InheritDocString
from pyTooling.MetaClasses     import ExtendedType
from pyTooling.Configuration   import ConfigurationException, KeyT, NodeT, ValueT
from pyTooling.Configuration   import InterpolationException, KeyNotFoundException, PathExpressionException
from pyTooling.Configuration   import UnsupportedValueTypeException
from pyTooling.Configuration   import Node as Abstract_Node
from pyTooling.Configuration   import Dictionary as Abstract_Dict
from pyTooling.Configuration   import Sequence as Abstract_Seq
from pyTooling.Configuration   import Configuration as Abstract_Configuration


@export
class Node(Abstract_Node):
	"""
	Node in a YAML configuration data structure.
	"""

	_yamlNode: Union[CommentedMap, CommentedSeq]  #: Reference to the associated YAML node.
	_cache:    Dict[str, ValueT]                  #: Cache of already converted sub-nodes and values, by key.
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
		:param key:      Key of the node within its parent.
		:param yamlNode: Reference to the YAML node.
		"""
		Abstract_Node.__init__(self, root, parent)

		self._yamlNode = yamlNode
		self._cache = {}
		self._key = key
		self._length = len(yamlNode)

	@InheritDocString(Abstract_Node)
	def __len__(self) -> int:
		return self._length

	@InheritDocString(Abstract_Node)
	def __getitem__(self, key: KeyT) -> ValueT:
		return self._GetNodeOrValue(str(key))

	@property
	def Key(self) -> KeyT:
		"""
		Property to access the node's key.

		:returns:                    Key of the node.
		:raises NotImplementedError: If a new key is assigned; renaming a key is not supported by this configuration
		                             implementation.
		"""
		return self._key

	@Key.setter
	def Key(self, value: KeyT) -> None:
		raise NotImplementedError()

	@InheritDocString(Abstract_Node)
	def QueryPath(self, query: str) -> ValueT:
		path = self._ToPath(query)
		return self._GetNodeOrValueByPathExpression(path)

	@staticmethod
	def _ToPath(query: str) -> List[Union[str, int]]:
		"""
		Split a path expression into its elements.

		:param query: Path expression, with its elements separated by ``:``.
		:returns:     List of keys and indices.
		"""
		return query.split(":")

	def _LookupKey(self, key: str) -> Any:
		"""
		Look up a key in the YAML node, trying it as string, integer and float.

		:param key:                   Key or index to look up.
		:returns:                     The raw value as returned by the YAML parser.
		:raises KeyNotFoundException: If the key exists neither as string, nor as integer or float.
		"""
		try:
			return self._yamlNode[key]
		except (KeyError, TypeError):
			pass

		for conversion in (int, float):
			try:
				convertedKey = conversion(key)
			except ValueError:
				continue

			try:
				return self._yamlNode[convertedKey]
			except (KeyError, IndexError, TypeError):
				pass

		ex = KeyNotFoundException(f"Key '{key}' not found in node '{self._key}'.")
		ex.add_note(self._DescribeKeys())
		raise ex

	def _DescribeKeys(self) -> str:
		"""
		Describe the keys or indices offered by this node, so it can be used as an exception note.

		:returns: A one-line description of the node's keys or index range.
		"""
		if isinstance(self._yamlNode, CommentedMap):
			if self._length == 0:
				return f"Node '{self._key}' is an empty dictionary."

			keys = "', '".join(str(key) for key in self._yamlNode)
			return f"Available keys: '{keys}'."
		else:
			if self._length == 0:
				return f"Node '{self._key}' is an empty sequence."

			return f"Node '{self._key}' is a sequence with indices 0..{self._length - 1}."

	def _GetNodeOrValue(self, key: str) -> ValueT:
		"""
		Return a sub-node or a value by key, converting it on first access.

		The converted object is cached, so a second access returns the same node object rather than a new one.

		:param key:                            Key or index to look up.
		:returns:                              A dictionary node, a sequence node, or a scalar value with its variables
		                                       resolved.
		:raises KeyNotFoundException:          If the key doesn't exist in this node.
		:raises UnsupportedValueTypeException: If the YAML parser returned a value that is neither a scalar, nor a
		                                       node.
		"""
		try:
			value = self._cache[key]
		except KeyError:
			value = self._LookupKey(key)

			if isinstance(value, str):
				value = self._ResolveVariables(value)
			elif isinstance(value, (int, float)):
				value = str(value)
			elif isinstance(value, CommentedMap):
				value = self.DICT_TYPE(self, self, key, value)
			elif isinstance(value, CommentedSeq):
				value = self.SEQ_TYPE(self, self, key, value)
			else:
				typeName = getFullyQualifiedName(value)
				ex = UnsupportedValueTypeException(f"Unsupported type '{typeName}' for key '{key}' in node '{self._key}'.")
				ex.add_note(f"The YAML parser returned a value that is neither a scalar (str, int, float), nor a map or sequence.")
				raise ex

			self._cache[key] = value

		return value

	def _ResolveVariables(self, value: str) -> str:
		"""
		Resolve the ``${...}`` variables inside a value.

		A variable references another node by a path expression, so a value can be composed from other values of the
		same configuration.

		:param value:                   The raw value, possibly containing variables.
		:returns:                       The value with every variable replaced by what it references.
		:raises InterpolationException: If a variable is malformed - a dangling ``$`` at the end of the value, or a
		                                missing closing ``}`` for a ``${`` at some position. |br|
		                                Use ``$$`` to escape a literal dollar sign.
		:raises KeyNotFoundException:   If a referenced key doesn't exist.
		"""
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
				if beginPos + 1 >= len(rawValue):
					ex = InterpolationException(f"Dangling '$' at the end of value '{value}'.")
					ex.add_note(f"Use '$$' to escape a literal dollar sign.")
					raise ex
				elif rawValue[beginPos + 1] == "$":
					result  += "$"
					rawValue = rawValue[1:]
				elif rawValue[beginPos + 1] == "{":
					endPos =  rawValue.find("}", beginPos)
					nextPos =  rawValue.rfind("$", beginPos, endPos)
					if endPos < 0:
						ex = InterpolationException(f"Unclosed variable reference in value '{value}'.")
						ex.add_note(f"Missing closing '}}' for the '${{' at position {beginPos}.")
						raise ex
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
		"""
		Return the value the given path refers to.

		:param path:                     Path elements, where ``..`` selects the parent node.
		:returns:                        The scalar value at that path.
		:raises KeyNotFoundException:    If a path element doesn't exist.
		:raises PathExpressionException: If the path resolves to a node instead of a value. Extend the path expression
		                                 to address a scalar value.
		"""
		node = self
		for p in path:
			if p == "..":
				node = node._parent
			else:
				node = node._GetNodeOrValue(p)

		if isinstance(node, Dictionary):
			pathExpression = ":".join(str(element) for element in path)
			ex = PathExpressionException(f"Path expression '{pathExpression}' resolves to a dictionary, not to a value.")
			ex.add_note(f"Element '{p}' is a dictionary. Extend the path expression to address a scalar value.")
			raise ex

		return node

	def _GetNodeOrValueByPathExpression(self, path: List[KeyT]) -> ValueT:
		"""
		Return the node or value the given path refers to.

		:param path:                  Path elements, where ``..`` selects the parent node.
		:returns:                     A node or a scalar value at that path.
		:raises KeyNotFoundException: If a path element doesn't exist.
		"""
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
		:param key:      Key of the node within its parent.
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

			_iter: typing_Iterator[ValueT]  #: Iterator over the underlying dictionary's keys.
			_obj:  Dictionary               #: The dictionary being iterated.

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
		:param key:      Key of the node within its parent.
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
				if self._i >= len(self._obj):
					raise StopIteration

				result = self._obj[str(self._i)]
				self._i += 1
				return result

		return Iterator(self)


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
class Configuration(Dictionary, Abstract_Configuration):
	"""A configuration read from a YAML file."""

	_yamlConfig: YAML  #: The parsed YAML document this configuration is based on.

	def __init__(self, configFile: Path) -> None:
		"""
		Initializes a configuration instance that reads a YAML file as input.

		All sequence items or dictionaries key-value-pairs in the YAML file are accessible via Python's dictionary syntax.

		:param configFile:              Configuration file to read and parse.
		:raises ConfigurationException: If the YAML file doesn't exist or can't be parsed.
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
