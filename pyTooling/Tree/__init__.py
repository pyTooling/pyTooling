from collections import deque
from typing import List, Generator, Iterable, TypeVar, Generic, Dict, Optional as Nullable, Hashable, ClassVar, Any

IDT = TypeVar("IDT", bound=Hashable)
ValueT = TypeVar("ValueT")
DictKeyT = TypeVar("DictKeyT")
DictValueT = TypeVar("DictValueT")


class Node(Generic[ValueT, DictKeyT, DictValueT]):
	_id: IDT
	_ids: ClassVar[Dict[Nullable[IDT], 'Node']] = {}
	_root: 'Node'
	_parent: 'Node'
	_children: List['Node']
	_links: List['Node']

	_value: Nullable[ValueT]
	_dict: Dict[DictKeyT, DictValueT]

	def __init__(self, id: IDT = None, value: ValueT = None, parent: 'Node' = None, children: List['Node'] = None):
		self._id = id
		self._value = value

		if parent is not None and not isinstance(parent, Node):
			raise TypeError(f"Parameter 'parent' is not of type 'Node'.")

		if parent is None:
			self._root = self
			self._parent = None
		else:
			self._root = parent._root
			self._parent = parent
			parent._children.append(self)

		if id is None:
			self._ids[None] = [self]
		else:
			self._ids[id] = self
		self._children = []

		if children is not None:
			for child in children:
				if not isinstance(child, Node):
					raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

				child.Parent = self

	@property
	def ID(self) -> IDT:
		return self._id

	@property
	def Value(self) -> ValueT:
		return self._value

	@Value.setter
	def Value(self, value: ValueT) -> None:
		self._value = value

	def __getitem__(self, key: DictKeyT) -> DictValueT:
		return self._dict[key]

	def __setitem__(self, key: DictKeyT, value: DictValueT) -> None:
		self._dict[key] = value

	@property
	def Root(self) -> 'Node':
		return self._root

	@Root.setter
	def Root(self, root: 'Node') -> None:
		self._root = root

	@property
	def Parent(self) -> 'Node':
		return self._parent

	@Parent.setter
	def Parent(self, parent: 'Node') -> None:
		if parent is None:
			self._parent._children.remove(self)
			self._parent = None
		else:
			self._parent = parent
			parent._children.append(self)

	@property
	def Path(self) -> List['Node']:
		path: deque['Node'] = deque()

		def walkup(node: 'Node'):
			if node._parent is not None:
				walkup(node._parent)
			path.append(node)

		walkup(self)
		return tuple(path)

	@property
	def IsRoot(self) -> bool:
		return self._root is self

	@property
	def IsLeaf(self) -> bool:
		return len(self._children) == 0

	@property
	def HasChildren(self) -> bool:
		return len(self._children) > 0

	def AddChild(self, child: 'Node') -> None:
		if not isinstance(child, Node):
			raise TypeError(f"Parameter 'child' is not of type 'Node'.")

		self._children.append(child)

	def AddChildren(self, children: Iterable['Node']):
		for child in children:
			if not isinstance(child, Node):
				raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

			self._children.append(child)

	def GetAncestors(self) -> Generator['Node', None, None]:
		node = self._parent
		while node is not None:
			yield node
			node = node._parent

	def GetChildren(self) -> Generator['Node', None, None]:
		for child in self._children:
			yield child

	def GetSiblings(self) -> Generator['Node', None, None]:
		for child in self._children:
			yield child
			yield from child.GetSiblings()

	def __str__(self):
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()
