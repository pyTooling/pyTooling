from pathlib import Path
from typing import ClassVar, Dict, List, Union

from pyTooling.Decorators import export
from ruamel.yaml import YAML, CommentedMap, CommentedSeq

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
	_cache: Dict[KeyT, ValueT]
	_length: int

	def __init__(self, root: "Configuration", parent: NodeT, yamlNode: Union[CommentedMap, CommentedSeq]):
		super().__init__(root, parent)
		self._yamlNode = yamlNode
		self._cache = {}
		self._length = len(yamlNode)

	def __len__(self) -> int:
		return self._length

	def QueryPath(self, query: str) -> ValueT:
		path = self._ToPath(query)
		return self._GetNodeOrValueByPathExpression(path)

	def _ToPath(self, query: str) -> List[Union[str, int]]:
		path: List[Union[str, int]] = []
		for p in query.split(":"):
			if p.isnumeric():
				path.append(int(p))
			else:
				path.append(p)

		return path

	def _GetNodeOrValue(self, key: KeyT) -> ValueT:
		try:
			value = self._cache[key]
		except KeyError:
			value = self._yamlNode[key]

			if isinstance(value, str):
				value = self._ResolveVariables(value)
			elif isinstance(value, int):
				pass
			elif isinstance(value, CommentedMap):
				value = self.DICT_TYPE(self, self, value)
			elif isinstance(value, CommentedSeq):
				value = self.SEQ_TYPE(self, self, value)
			else:
				raise Exception(f"") from TypeError(f"Unknown type '{value.__class__.__name__}' returned from ruamel.yaml.") # XXX: error message

			self._cache[key] = value

		return value

	def _ResolveVariables(self, value: str):
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
						raise Exception()  # InterpolationSyntaxError(option, section, f"Bad interpolation variable reference {rest!r}")
					if ((nextPos > 0) and (nextPos < endPos)):  # an embedded $-sign
						path = rawValue[nextPos+2:endPos]
#						print(f"_ResolveVariables: path='{path}'")
						innervalue = self._GetValueByPathExpression(path.split(":"))
						# innervalue = self.interpolate(parser, section, option, path, map, depth + 1)
#						print(f"_ResolveVariables: innervalue='{innervalue}'")
						rawValue = rawValue[beginPos:nextPos] + innervalue + rawValue[endPos + 1:]
#						print(f"_ResolveVariables: new rawValue='{rawValue}'")
					else:
						path = rawValue[beginPos+2:endPos]
						rawValue = rawValue[endPos+1:]
						result  += self._GetValueByPathExpression(path.split(":"))

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
	_keys: List[KeyT]

	def __init__(self, root: "Configuration", parent: NodeT, yamlNode: CommentedMap):
		Node.__init__(self, root, parent, yamlNode)
		self._keys = [k for k in yamlNode.keys()]

	def __contains__(self, key: KeyT) -> bool:
		return key in self._keys

	def __getitem__(self, key: KeyT) -> ValueT:
		return self._GetNodeOrValue(key)

	def __iter__(self):
		class iterator:
			def __init__(self, obj: Dictionary):
				self._iter = iter(obj._keys)
				self._obj = obj

			def __iter__(self):
				return self

			def __next__(self):
				key = next(self._iter)
				return self._obj[key]

		return iterator(self)


class Sequence(Abstract_Seq, Node):
	def __init__(self, root: "Configuration", parent: NodeT, yamlNode: CommentedSeq):
		Node.__init__(self, root, parent, yamlNode)
		self._length = len(yamlNode)

	def __getitem__(self, key: int) -> ValueT:
		value = self._yamlNode[key]
		return value

	def __iter__(self):
		class iterator:
			def __init__(self, obj: Sequence):
				self._i = 0
				self._obj = obj

			def __iter__(self):
				return self

			def __next__(self):
				try:
					result = self._obj[self._i]
					self._i += 1
					return result
				except IndexError:
					raise StopIteration

		return iterator(self)


setattr(Abstract_Node, "DICT_TYPE", Dictionary)
setattr(Abstract_Node, "SEQ_TYPE", Sequence)


@export
class Configuration(Abstract_Configuration, Dictionary):
	_yamlConfig: YAML

	def __init__(self, configFile: Path):
		Abstract_Configuration.__init__(self)

		with configFile.open() as file:
			self._yamlConfig = YAML().load(file)

		Dictionary.__init__(self, self, self, self._yamlConfig)

	def __getitem__(self, key: KeyT) -> ValueT:
		return self._GetNodeOrValue(key)

	def __setitem__(self, key: KeyT, value: ValueT) -> None:
		pass
