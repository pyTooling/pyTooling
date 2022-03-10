# ==================================================================================================================== #
#             _____           _ _             _____                                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ ___  ___                                                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _ \/ _ \                                                      #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | |  __/  __/                                                      #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \___|\___|                                                      #
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
"""A powerful tree data structure for Python."""
from collections import deque
from typing import List, Generator, Iterable, TypeVar, Generic, Dict, Optional as Nullable, Hashable, Tuple, Callable, Union

IDT = TypeVar("IDT", bound=Hashable)
ValueT = TypeVar("ValueT")
DictKeyT = TypeVar("DictKeyT")
DictValueT = TypeVar("DictValueT")


class Node(Generic[IDT, ValueT, DictKeyT, DictValueT]):
	_id: IDT
	_ids: Nullable[Dict[Nullable[IDT], Union['Node', List['Node']]]]
	_root: 'Node'
	_parent: Nullable['Node']
	_children: List['Node']
	_links: List['Node']

	_value: Nullable[ValueT]
	_dict: Dict[DictKeyT, DictValueT]

	def __init__(self, id: IDT = None, value: ValueT = None, parent: 'Node' = None, children: List['Node'] = None):
		self._id = id
		self._value = value
		self._dict = {}

		if parent is not None and not isinstance(parent, Node):
			raise TypeError(f"Parameter 'parent' is not of type 'Node'.")

		if parent is None:
			self._root = self
			self._parent = None

			self._ids = {None: []}
			if id is None:
				self._ids[None].append(self)
			else:
				self._ids[id] = self
		else:
			self._root = parent._root
			self._parent = parent
			self._ids = None

			if id is None:
				self._root._ids[None].append(self)
			else:
				self._root._ids[id] = self

			parent._children.append(self)

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

	@property
	def Parent(self) -> 'Node':
		return self._parent

	@Parent.setter
	def Parent(self, parent: 'Node') -> None:
		if parent is None:
			self._ids = {None: []}
			for sibling in self._parent.GetSiblings():
				sibling._root = self
				if sibling._id is None:
					self._ids[None].append(sibling)
				else:
					self._ids[sibling._id] = sibling

			self._parent._children.remove(self)

			self._root = self
			self._parent = None
		else:
			if parent._root is self._root:
				raise Exception(f"Parent '{parent}' is already a child node in this tree.")

			self._root = parent._root
			self._parent = parent
			self._ids = self._SetNewRoot(self._ids)
			parent._children.append(self)

	@property
	def LeftSibling(self) -> 'Node':
		pass

	@property
	def RightSibling(self) -> 'Node':
		pass

	@property
	def Path(self) -> Tuple['Node']:
		path: deque['Node'] = deque()

		def walkup(node: 'Node'):
			if node._parent is not None:
				walkup(node._parent)
			path.append(node)

		walkup(self)
		return tuple(path)

	@property
	def Level(self) -> int:
		pass

	@property
	def IsRoot(self) -> bool:
		return self._parent is None

	@property
	def IsLeaf(self) -> bool:
		return len(self._children) == 0

	@property
	def HasChildren(self) -> bool:
		return len(self._children) > 0

	def _SetNewRoot(self, ids: Dict[Nullable['Node'], Union['Node', List['Node']]]) -> type(None):
		for id, node in ids.items():
			if id is not None:
				self._root._ids[id] = node
				node._root = self._root
			else:
				nodeList: List[Node] = node
				for node in nodeList:
					self._root._ids[None].append(node)
					node._root = self._root

		return None

	def AddChild(self, child: 'Node') -> None:
		if not isinstance(child, Node):
			raise TypeError(f"Parameter 'child' is not of type 'Node'.")

		if child._root is self._root:
			raise Exception(f"Child '{child}' is already a node in this tree.")

		child._root = self._root
		child._parent = self
		child._ids = self._SetNewRoot(child._ids)
		self._children.append(child)

	def AddChildren(self, children: Iterable['Node']):
		for child in children:
			if not isinstance(child, Node):
				raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

			child._root = self._root
			child._parent = self
			child._ids = self._SetNewRoot(child._ids)
			self._children.append(child)

	def GetAncestors(self) -> Generator['Node', None, None]:
		node = self._parent
		while node is not None:
			yield node
			node = node._parent

	def GetCommonAncestors(self):
		pass

	def GetChildren(self) -> Generator['Node', None, None]:
		for child in self._children:
			yield child

	def GetSiblings(self) -> Generator['Node', None, None]:
		for child in self._children:
			yield child
			yield from child.GetSiblings()

	def GetLeftSiblings(self):
		pass

	def GetRightSiblings(self):
		pass

	def InterateLevelOrder(self):
		queue = deque([self])
		while queue:
			currentNode = queue.pop()
			yield currentNode
			for node in currentNode._children:
				queue.appendleft(node)

	def IteratePreOrder(self):
		yield self
		for child in self._children:
			yield from child.IteratePreOrder()

	def IteratePostOrder(self):
		for child in self._children:
			yield from child.IteratePostOrder()
		yield self

	def GetNodeByID(self, id: IDT) -> Union['Node', List['Node']]:
		return self._root._ids[id]

	def Find(self, filter: Callable) -> Generator['Node', None, None]:
		pass

	def __str__(self):
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()
