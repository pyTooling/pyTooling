from typing import TypeVar, Union, ClassVar

from pyTooling.Decorators import export

KeyT = TypeVar("KeyT", bound=Union[str, int])
NodeT = Union["Dictionary", "Sequence"]
ValueT = TypeVar("ValueT", bound=Union[NodeT, str, int, float])


@export
class Node:
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

	def __iter__(self):
		raise NotImplementedError()

	def __next__(self):
		raise NotImplementedError()

	def QueryPath(self, query: str) -> ValueT:
		raise NotImplementedError()


@export
class Dictionary(Node):
	pass


@export
class Sequence(Node):
	def __getitem__(self, index: int) -> ValueT:
		raise NotImplementedError()

	def __setitem__(self, index: int, value: ValueT) -> None:
		raise NotImplementedError()

	def __iter__(self):
		raise NotImplementedError()

	def __next__(self):
		raise NotImplementedError()


setattr(Node, "DICT_TYPE", Dictionary)
setattr(Node, "SEQ_TYPE", Sequence)


@export
class Configuration(Node):
	def __init__(self):
		Node.__init__(self)
