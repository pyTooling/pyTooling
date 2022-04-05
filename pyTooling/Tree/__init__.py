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

from ..Decorators import export

IDT = TypeVar("IDT", bound=Hashable)
ValueT = TypeVar("ValueT")
DictKeyT = TypeVar("DictKeyT")
DictValueT = TypeVar("DictValueT")


@export
class Node(Generic[IDT, ValueT, DictKeyT, DictValueT]):
	"""A **tree** data structure can be constructed of ``Node`` instances.

	Therefore, nodes can be connected to parent nodes or a parent node can add child nodes. This allows to construct a
	tree top-down or bottom-up.

	.. hint:: The top-down construction should be preferred, because it's slightly faster.

	Each tree uses the **root** node (a.k.a. tree-representative) to store some per-tree data structures. E.g. a list of
	all IDs in a tree. For easy and quick access to such data structures, each sibling node contains a reference to the
	root node (``_root``). In case of adding a tree to an existing tree, such data structures get merged and all added
	nodes get assigned with new root references. Use the read-only property :py:attr:`Root` to access the root reference.

	The reference to the parent node (``_parent``) can be access via property :py:attr:`Parent`. If the property's setter
	is used, a node and all its siblings are added to another tree or to a new position in the same tree.

	The references to all node's children is stored in a list (``_children``). Children, siblings, ancestors, can be
	accessed via various generators:

	* :py:meth:`GetChildren` |rarr| iterate all direct children.

	Each node can have a **unique ID** or no ID at all (``id=None``). The root node is used to store all IDs in a
	dictionary (``_nodesWithID``). In case no ID is given, all such ID-less nodes are collected in a single bin and store as a
	list of nodes. An ID can be modified after the Node was created. Use the read-only property :py:attr:`ID` to access
	the ID.

	Each node can have a **value** (``_value``), which can be given at node creation time, or it can be assigned and/or
	modified later. Use the property :py:attr:`Value` to get or set the value.

	Moreover, each node can store various key-value pairs (``_dict``). Use the dictionary syntax to get and set
	key-value-pairs.
	"""

	_id: Nullable[IDT]                         #: Unique identifier of a node. ``None`` if not used.
	_nodesWithID: Nullable[Dict[IDT, 'Node']]  #: Dictionary of all IDs in the tree. ``None`` if it's not the root node.
	_nodesWithoutID: Nullable[List['Node']]    #: List of all nodes without an ID in the tree. ``None`` if it's not the root node.
	_root: 'Node'                              #: Reference to the root of a tree. ``self`` if it's the root node.
	_parent: Nullable['Node']                  #: Reference to the parent node. ``None`` if it's the root node.
	_children: List['Node']                    #: List of all children
#	_links: List['Node']

	_value: Nullable[ValueT]                   #: Field to store the node's value.
	_dict: Dict[DictKeyT, DictValueT]          #: Dictionary to store key-value-pairs attached to the node.

	__slots__ = ("_id", "_nodesWithID", "_nodesWithoutID", "_root", "_parent", "_children", "_value", "_dict")

	def __init__(self, id: IDT = None, value: ValueT = None, parent: 'Node' = None, children: List['Node'] = None):
		self._id = id
		self._value = value
		self._dict = {}

		if parent is not None and not isinstance(parent, Node):
			raise TypeError(f"Parameter 'parent' is not of type 'Node'.")

		if parent is None:
			self._root = self
			self._parent = None

			self._nodesWithID = {}
			self._nodesWithoutID = []
			if id is None:
				self._nodesWithoutID.append(self)
			else:
				self._nodesWithID[id] = self
		else:
			self._root = parent._root
			self._parent = parent
			self._nodesWithID = None

			if id is None:
				self._root._nodesWithoutID.append(self)
			elif id in self._root._nodesWithID:
				raise ValueError(f"ID '{id}' already exists in this tree.")
			else:
				self._root._nodesWithID[id] = self

			parent._children.append(self)

		self._children = []

		if children is not None:
			for child in children:
				if not isinstance(child, Node):
					raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

				child.Parent = self

	@property
	def ID(self) -> IDT:
		"""Read-only property to access the unique ID of a node. If no ID was given at node construction time, ID is None."""
		return self._id

	@property
	def Value(self) -> ValueT:
		"""Property to get and set the value (``_value``) of a node."""
		return self._value

	@Value.setter
	def Value(self, value: ValueT) -> None:
		self._value = value

	def __getitem__(self, key: DictKeyT) -> DictValueT:
		return self._dict[key]

	def __setitem__(self, key: DictKeyT, value: DictValueT) -> None:
		self._dict[key] = value

	def __delitem__(self, key: DictKeyT) -> None:
		del self._dict[key]

	@property
	def Root(self) -> 'Node':
		"""Read-only property to access the tree's root node (representative node)."""
		return self._root

	@property
	def Parent(self) -> 'Node':
		return self._parent

	@Parent.setter
	def Parent(self, parent: 'Node') -> None:
		# TODO: is moved inside the same tree, don't move nodes in _nodesWithID and don't change _root

		if parent is None:
			self._nodesWithID = {}
			self._nodesWithoutID = []
			for sibling in self._parent.GetSiblings():
				sibling._root = self
				if sibling._id is None:
					self._nodesWithoutID.append(sibling)
				else:
					self._nodesWithID[sibling._id] = sibling

			self._parent._children.remove(self)

			self._root = self
			self._parent = None
		else:
			if parent._root is self._root:
				raise Exception(f"Parent '{parent}' is already a child node in this tree.")

			self._root = parent._root
			self._parent = parent
			self._SetNewRoot(self._nodesWithID, self._nodesWithoutID)
			self._nodesWithID = self._nodesWithoutID = None
			parent._children.append(self)

	@property
	def LeftSibling(self) -> 'Node':
		raise NotImplementedError(f"Property 'LeftSibling' is not yet implemented.")

	@property
	def RightSibling(self) -> 'Node':
		raise NotImplementedError(f"Property 'RightSibling' is not yet implemented.")

	def _GetPathAsLinkedList(self) -> deque["Node"]:
		path: deque['Node'] = deque()

		node = self
		while node is not None:
			path.appendleft(node)
			node = node._parent

		return path

	@property
	def Path(self) -> Tuple['Node']:
		return tuple(self._GetPathAsLinkedList())

	@property
	def Level(self) -> int:
		raise NotImplementedError(f"Property 'Level' is not yet implemented.")

	@property
	def IsRoot(self) -> bool:
		return self._parent is None

	@property
	def IsLeaf(self) -> bool:
		return len(self._children) == 0

	@property
	def HasChildren(self) -> bool:
		return len(self._children) > 0

	def _SetNewRoot(self, nodesWithIDs: Dict['Node', 'Node'], nodesWithoutIDs: List['Node']) -> None:
		for id, node in nodesWithIDs.items():
			if id in self._root._nodesWithID:
				raise ValueError(f"ID '{id}' already exists in this tree.")
			else:
				self._root._nodesWithID[id] = node
				node._root = self._root

		for node in nodesWithoutIDs:
			self._root._nodesWithoutID.append(node)
			node._root = self._root

	def AddChild(self, child: 'Node') -> None:
		if not isinstance(child, Node):
			raise TypeError(f"Parameter 'child' is not of type 'Node'.")

		if child._root is self._root:
			raise Exception(f"Child '{child}' is already a node in this tree.")

		child._root = self._root
		child._parent = self
		self._SetNewRoot(child._nodesWithID, child._nodesWithoutID)
		child._nodesWithID = child._nodesWithoutID = None
		self._children.append(child)

	def AddChildren(self, children: Iterable['Node']):
		for child in children:
			if not isinstance(child, Node):
				raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

			if child._root is self._root:
				raise Exception(f"Child '{child}' is already a node in this tree.")

			child._root = self._root
			child._parent = self
			self._SetNewRoot(child._nodesWithID, child._nodesWithoutID)
			child._nodesWithID = child._nodesWithoutID = None
			self._children.append(child)

	def GetPath(self) -> Generator['Node', None, None]:
		for node in self._GetPathAsLinkedList():
			yield node

	def GetAncestors(self) -> Generator['Node', None, None]:
		node = self._parent
		while node is not None:
			yield node
			node = node._parent

	def GetCommonAncestors(self, others: Union['Node', Iterable['Node']]) -> Generator["Node", None, None]:
		if isinstance(others, Node):
			# Check for trivial case
			if others is self:
				for node in self.Path:		# TODO: Path generates a list and a tuple. Provide a generator for such a walk.
					yield node
				return

			# Check if both are in the same tree.
			if self._root is not others._root:
				raise Exception(f"Node 'others' is not in the same tree.")

			# Compute paths top-down and walk both paths until they deviate
			for left, right in zip(self.Path, others.Path):
				if left is right:
					yield left
				else:
					return
		elif isinstance(others, Iterable):
			raise NotImplemented(f"Generator 'GetCommonAncestors' does not yet support an iterable of siblings to compute the common ancestors.")

	def GetChildren(self) -> Generator['Node', None, None]:
		"""A generator to iterate all direct children of the current node."""
		for child in self._children:
			yield child

	def GetSiblings(self) -> Generator['Node', None, None]:
		"""A generator to iterate all siblings of the current node. In contrast to `IteratePreOrder` and `IteratePostOrder`
		it doesn't include the node itself.

		.. seealso::

		   :py:meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :py:meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :py:meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.
		"""
		for child in self._children:
			yield child
			yield from child.GetSiblings()

	def GetLeftSiblings(self):
		raise NotImplementedError(f"Method 'GetLeftSiblings' is not yet implemented.")

	def GetRightSiblings(self):
		raise NotImplementedError(f"Method 'GetRightSiblings' is not yet implemented.")

	def InterateLevelOrder(self):
		queue = deque([self])
		while queue:
			currentNode = queue.pop()
			yield currentNode
			for node in currentNode._children:
				queue.appendleft(node)

	def IteratePreOrder(self):
		"""A generator to iterate all siblings of the current node in pre-order. In contrast to `GetSiblings`, this includes
		also the node itself as the first returned node.
		"""
		yield self
		for child in self._children:
			yield from child.IteratePreOrder()

	def IteratePostOrder(self):
		"""A generator to iterate all siblings of the current node in post-order. In contrast to `GetSiblings`, this
		includes also the node itself as the last returned node.
		"""
		for child in self._children:
			yield from child.IteratePostOrder()
		yield self

	def WalkTo(self, other: 'Node') -> Generator['Node', None, None]:
		# Check for trivial case
		if other is self:
			yield from ()

		# Check if both are in the same tree.
		if self._root is not other._root:
			raise Exception(f"Node 'other' is not in the same tree.")

		# Compute both paths to the root.
		# 1. Walk from self to root, until a first common ancestor is found.
		# 2. Walk from there to other (reverse paths)
		otherPath = other.Path		# TODO: Path generates a list and a tuple. Provide a generator for such a walk.
		index = len(otherPath)
		for node in self.GetAncestors():
			try:
				index = otherPath.index(node)
				break
			except ValueError:
				yield node

		for i in range(index, len(otherPath)):
			yield otherPath[i]

	def GetNodeByID(self, id: IDT) -> 'Node':
		"""Lookup a node by its unique ID."""
		if id is None:
			raise ValueError(f"'None' is not supported as an ID value.")

		return self._root._nodesWithID[id]

	def Find(self, filter: Callable) -> Generator['Node', None, None]:
		raise NotImplementedError(f"Method 'Find' is not yet implemented.")

	def __str__(self) -> str:
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()
