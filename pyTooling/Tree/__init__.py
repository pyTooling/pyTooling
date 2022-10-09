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
from typing import List, Generator, Iterable, TypeVar, Generic, Dict, Optional as Nullable, Hashable, Tuple, Callable, \
	Union, Deque, Iterator

from ..Decorators import export
from ..MetaClasses import ExtendedType

IDType = TypeVar("VertexIDType", bound=Hashable)
"""A type variable for a tree's ID."""

ValueType = TypeVar("ValueType")
"""A type variable for a tree's value."""

DictKeyType = TypeVar("DictKeyType")
"""A type variable for a tree's dictionary keys."""

DictValueType = TypeVar("DictValueType")
"""A type variable for a tree's dictionary values."""


@export
class Node(Generic[IDType, ValueType, DictKeyType, DictValueType], metaclass=ExtendedType, useSlots=True):
	"""
	A **tree** data structure can be constructed of ``Node`` instances.

	Therefore, nodes can be connected to parent nodes or a parent node can add child nodes. This allows to construct a
	tree top-down or bottom-up.

	.. hint:: The top-down construction should be preferred, because it's slightly faster.

	Each tree uses the **root** node (a.k.a. tree-representative) to store some per-tree data structures. E.g. a list of
	all IDs in a tree. For easy and quick access to such data structures, each sibling node contains a reference to the
	root node (:py:attr:`_root`). In case of adding a tree to an existing tree, such data structures get merged and all added
	nodes get assigned with new root references. Use the read-only property :py:attr:`Root` to access the root reference.

	The reference to the parent node (:py:attr:`_parent`) can be access via property :py:attr:`Parent`. If the property's setter
	is used, a node and all its siblings are added to another tree or to a new position in the same tree.

	The references to all node's children is stored in a list (:py:attr:`_children`). Children, siblings, ancestors, can be
	accessed via various generators:

	* :py:meth:`GetAncestors` |rarr| iterate all ancestors bottom-up.
	* :py:meth:`GetChildren` |rarr| iterate all direct children.
	* :py:meth:`GetDescendants` |rarr| iterate all descendants.
	* :py:meth:`IterateLevelOrder` |rarr| IterateLevelOrder.
	* :py:meth:`IteratePreOrder` |rarr| iterate siblings in pre-order.
	* :py:meth:`IteratePostOrder` |rarr| iterate siblings in post-order.

	Each node can have a **unique ID** or no ID at all (``nodeID=None``). The root node is used to store all IDs in a
	dictionary (:py:attr:`_nodesWithID`). In case no ID is given, all such ID-less nodes are collected in a single bin and store as a
	list of nodes. An ID can be modified after the Node was created. Use the read-only property :py:attr:`ID` to access
	the ID.

	Each node can have a **value** (:py:attr:`_value`), which can be given at node creation time, or it can be assigned and/or
	modified later. Use the property :py:attr:`Value` to get or set the value.

	Moreover, each node can store various key-value pairs (:py:attr:`_dict`). Use the dictionary syntax to get and set
	key-value-pairs.
	"""

	_id: Nullable[IDType]                         #: Unique identifier of a node. ``None`` if not used.
	_nodesWithID: Nullable[Dict[IDType, 'Node']]  #: Dictionary of all IDs in the tree. ``None`` if it's not the root node.
	_nodesWithoutID: Nullable[List['Node']]    #: List of all nodes without an ID in the tree. ``None`` if it's not the root node.
	_root: 'Node'                              #: Reference to the root of a tree. ``self`` if it's the root node.
	_parent: Nullable['Node']                  #: Reference to the parent node. ``None`` if it's the root node.
	_children: List['Node']                    #: List of all children
#	_links: List['Node']

	_level: int                                #: Level of the node (distance to the root).
	_value: Nullable[ValueType]                   #: Field to store the node's value.
	_dict: Dict[DictKeyType, DictValueType]          #: Dictionary to store key-value-pairs attached to the node.

	def __init__(self, nodeID: IDType = None, value: ValueType = None, parent: 'Node' = None, children: List['Node'] = None):
		""".. todo:: Needs documentation."""
		self._id = nodeID
		self._value = value
		self._dict = {}

		if parent is not None and not isinstance(parent, Node):
			raise TypeError(f"Parameter 'parent' is not of type 'Node'.")

		if parent is None:
			self._root = self
			self._parent = None
			self._level = 0

			self._nodesWithID = {}
			self._nodesWithoutID = []
			if nodeID is None:
				self._nodesWithoutID.append(self)
			else:
				self._nodesWithID[nodeID] = self
		else:
			self._root = parent._root
			self._parent = parent
			self._level = parent._level + 1
			self._nodesWithID = None

			if nodeID is None:
				self._root._nodesWithoutID.append(self)
			elif nodeID in self._root._nodesWithID:
				raise ValueError(f"ID '{nodeID}' already exists in this tree.")
			else:
				self._root._nodesWithID[nodeID] = self

			parent._children.append(self)

		self._children = []

		if children is not None:
			if not isinstance(children, Iterable):
				raise TypeError(f"Parameter 'children' is not iterable.")

			for child in children:
				if not isinstance(child, Node):
					raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

				child.Parent = self

	@property
	def ID(self) -> Nullable[IDType]:
		"""
		Read-only property to access the unique ID of a node (:py:attr:`_id`).

		If no ID was given at node construction time, ID return None.

		:returns: Unique ID of a node, if ID was given at node creation time, else None.
		"""
		return self._id

	@property
	def Value(self) -> Nullable[ValueType]:
		"""
		Property to get and set the value (:py:attr:`_value`) of a node.

		:returns: The value of a node.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Nullable[ValueType]) -> None:
		self._value = value

	def __getitem__(self, key: DictKeyType) -> DictValueType:
		""".. todo:: Needs documentation."""
		return self._dict[key]

	def __setitem__(self, key: DictKeyType, value: DictValueType) -> None:
		""".. todo:: Needs documentation."""
		self._dict[key] = value

	def __delitem__(self, key: DictKeyType) -> None:
		""".. todo:: Needs documentation."""
		del self._dict[key]

	@property
	def Root(self) -> 'Node':
		"""
		Read-only property to access the tree's root node (:py:attr:`_root`).

		:returns: The root node (representative node) of a tree.
		"""
		return self._root

	@property
	def Parent(self) -> Nullable['Node']:
		"""
		Property to get and set the parent (:py:attr:`_parent`) of a node.

		.. note::

		   As the current node might be a tree itself, appending this node to a tree can lead to a merge of trees and
		   especially to a merge of IDs. As IDs are unique, it might raise an :py:exc:`Exception`.

		:returns: The parent of a node.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: Nullable['Node']) -> None:
		# TODO: is moved inside the same tree, don't move nodes in _nodesWithID and don't change _root

		if parent is None:
			self._nodesWithID = {}
			self._nodesWithoutID = []
			self._level = 0

			if self._id is None:
				self._nodesWithoutID.append(self)
				self._root._nodesWithoutID.remove(self)
			else:
				self._nodesWithID[self._id] = self
				del self._nodesWithID[self._id]

			for sibling in self.GetDescendants():
				sibling._root = self
				sibling._level = sibling._parent._level + 1
				if sibling._id is None:
					self._nodesWithoutID.append(sibling)
					self._root._nodesWithoutID.remove(sibling)
				else:
					self._nodesWithID[sibling._id] = sibling
					del self._nodesWithID[sibling._id]

			self._parent._children.remove(self)

			self._root = self
			self._parent = None
		elif not isinstance(parent, Node):
			raise TypeError(f"Parameter 'parent' is not of type 'Node'.")
		else:
			if parent._root is self._root:
				raise Exception(f"Parent '{parent}' is already a child node in this tree.")

			self._root = parent._root
			self._parent = parent
			self._level = parent._level + 1
			for node in self.GetDescendants():
				node._level = node._parent._level + 1
			self._SetNewRoot(self._nodesWithID, self._nodesWithoutID)
			self._nodesWithID = self._nodesWithoutID = None
			parent._children.append(self)

	@property
	def Siblings(self) -> Tuple['Node', ...]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		return tuple([node for node in self._parent if node is not self])

	@property
	def LeftSiblings(self) -> Tuple['Node', ...]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		result = []
		for node in self._parent:
			if node is not self:
				result.append(node)
			else:
				break
		else:
			raise Exception(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		return tuple(result)

	@property
	def RightSiblings(self) -> Tuple['Node', ...]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		result = []
		iterator = iter(self._parent)
		for node in iterator:
			if node is self:
				break
		else:
			raise Exception(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		for node in iterator:
			result.append(node)

		return tuple(result)

	def _GetPathAsLinkedList(self) -> Deque["Node"]:
		"""
		Compute the path from current node to root node by using a linked list (:py:class:`deque`).

		:meta private:
		:returns: Path from node to root node as double-ended queue (deque).
		"""
		path: Deque['Node'] = deque()

		node = self
		while node is not None:
			path.appendleft(node)
			node = node._parent

		return path

	@property
	def Path(self) -> Tuple['Node']:
		"""
		Read-only property to return the path from root node to the node as a tuple of nodes.

		:returns: A tuple of nodes describing the path from root node to the node.
		"""
		return tuple(self._GetPathAsLinkedList())

	@property
	def Level(self) -> int:
		"""
		Read-only property to return a node's level in the tree.

		The level is the distance to the root node.

		:returns: The node's level.
		"""
		return self._level

	@property
	def Size(self) -> int:
		"""
		Read-only property to return the size of the tree.

		:returns: Count of all nodes in the tree structure.
		"""
		return len(self._root._nodesWithID) + len(self._root._nodesWithoutID)

	@property
	def IsRoot(self) -> bool:
		"""
		Returns true, if the node is the root node (representative node of the tree).

		:returns: True, if node is the root node.
		"""
		return self._parent is None

	@property
	def IsLeaf(self) -> bool:
		"""
		Returns true, if the node is a leaf node (has no children).

		:returns: True, if node has no children.
		"""
		return len(self._children) == 0

	@property
	def HasChildren(self) -> bool:
		"""
		Returns true, if the node has child nodes.

		:returns: True, if node has children.
		"""
		return len(self._children) > 0

	def _SetNewRoot(self, nodesWithIDs: Dict['Node', 'Node'], nodesWithoutIDs: List['Node']) -> None:
		for nodeID, node in nodesWithIDs.items():
			if nodeID in self._root._nodesWithID:
				raise ValueError(f"ID '{nodeID}' already exists in this tree.")
			else:
				self._root._nodesWithID[nodeID] = node
				node._root = self._root

		for node in nodesWithoutIDs:
			self._root._nodesWithoutID.append(node)
			node._root = self._root

	def AddChild(self, child: 'Node'):
		"""
		Add a child node to the current node of the tree.

		If ``child`` is a subtree, both trees get merged. So all nodes in ``child`` get a new :py:attr:`_root` assigned and
		all IDs are merged into the node's root's ID lists (:py:attr:`_nodesWithID`).

		.. seealso::

		   :py:attr:`Parent` |br|
		      |rarr| Set the parent of a node.
		   :py:meth:`AddChildren` |br|
		      |rarr| Add multiple children at once.

		:param child: The child node to be added to the tree.
		:raises TypeError: If parameter ``child`` is not a :py:class:`Node`.
		:raises Exception: If parameter ``child`` is already a node in the tree.
		"""
		if not isinstance(child, Node):
			raise TypeError(f"Parameter 'child' is not of type 'Node'.")

		if child._root is self._root:
			raise Exception(f"Child '{child}' is already a node in this tree.")

		child._root = self._root
		child._parent = self
		child._level = self._level + 1
		for node in child.GetDescendants():
			node._level = node._parent._level + 1
		self._SetNewRoot(child._nodesWithID, child._nodesWithoutID)
		child._nodesWithID = child._nodesWithoutID = None
		self._children.append(child)

	def AddChildren(self, children: Iterable['Node']):
		"""
		Add multiple children nodes to the current node of the tree.

		.. seealso::

		   :py:attr:`Parent` |br|
		      |rarr| Set the parent of a node.
		   :py:meth:`AddChild` |br|
		      |rarr| Add a child node to the tree.

		:param children: The list of children nodes to be added to the tree.
		:raises TypeError: If parameter ``children`` contains an item, which is not a :py:class:`Node`.
		:raises Exception: If parameter ``children`` contains an item, which is already a node in the tree.
		"""
		for child in children:
			if not isinstance(child, Node):
				raise TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")

			if child._root is self._root:
				raise RuntimeError(f"Child '{child}' is already a node in this tree.")

			child._root = self._root
			child._parent = self
			child._level = self._level + 1
			for node in child.GetDescendants():
				node._level = node._parent._level + 1
			self._SetNewRoot(child._nodesWithID, child._nodesWithoutID)
			child._nodesWithID = child._nodesWithoutID = None
			self._children.append(child)

	def GetPath(self) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		for node in self._GetPathAsLinkedList():
			yield node

	def GetAncestors(self) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		node = self._parent
		while node is not None:
			yield node
			node = node._parent

	def GetCommonAncestors(self, others: Union['Node', Iterable['Node']]) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		if isinstance(others, Node):
			# Check for trivial case
			if others is self:
				for node in self._GetPathAsLinkedList():
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
			raise NotImplementedError(f"Generator 'GetCommonAncestors' does not yet support an iterable of siblings to compute the common ancestors.")

	def GetChildren(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all direct children of the current node.

		.. seealso::

		   :py:meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :py:meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :py:meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :py:meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.

		:returns: A generator to iterate all children.
		"""
		for child in self._children:
			yield child

	def GetSiblings(self) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		for node in self._parent:
			if node is self:
				continue

			yield node

	def GetLeftSiblings(self) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		for node in self._parent:
			if node is self:
				break

			yield node
		else:
			raise Exception(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

	def GetRightSiblings(self) -> Generator['Node', None, None]:
		""".. todo:: Needs documentation."""
		if self._parent is None:
			raise RuntimeError(f"Root node has no siblings.")

		iterator = iter(self._parent)
		for node in iterator:
			if node is self:
				break
		else:
			raise Exception(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		for node in iterator:
			yield node

	def GetDescendants(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all descendants of the current node. In contrast to `IteratePreOrder` and `IteratePostOrder`
		it doesn't include the node itself.

		.. seealso::

		   :py:meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :py:meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :py:meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :py:meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.

		:returns: A generator to iterate all siblings.
		"""
		for child in self._children:
			yield child
			yield from child.GetDescendants()

	def GetLeftRelatives(self):
		""".. todo:: Needs documentation."""
		for node in self.GetLeftSiblings():
			yield node
			yield from node.GetDescendants()

	def GetRightRelatives(self):
		""".. todo:: Needs documentation."""
		for node in self.GetRightSiblings():
			yield node
			yield from node.GetDescendants()

	def IterateLeafs(self) -> Generator['Node', None, None]:
		for child in self._children:
			if child.IsLeaf:
				yield child
			else:
				yield from child.IterateLeafs()

	def IterateLevelOrder(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings of the current node level-by-level top-down. In contrast to `GetDescendants`,
		this includes also the node itself as the first returned node.

		.. seealso::

		   :py:meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :py:meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :py:meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :py:meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.

		:returns: A generator to iterate all siblings level-by-level.
		"""
		queue = deque([self])
		while queue:
			currentNode = queue.pop()
			yield currentNode
			for node in currentNode._children:
				queue.appendleft(node)

	def IteratePreOrder(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings of the current node in pre-order. In contrast to `GetDescendants`, this includes
		also the node itself as the first returned node.

		.. seealso::

		   :py:meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :py:meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :py:meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :py:meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.

		:returns: A generator to iterate all siblings in pre-order.
		"""
		yield self
		for child in self._children:
			yield from child.IteratePreOrder()

	def IteratePostOrder(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings of the current node in post-order. In contrast to `GetDescendants`, this
		includes also the node itself as the last returned node.

		.. seealso::

		   :py:meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :py:meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :py:meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :py:meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.

		:returns: A generator to iterate all siblings in post-order.
		"""
		for child in self._children:
			yield from child.IteratePostOrder()
		yield self

	def WalkTo(self, other: 'Node') -> Generator['Node', None, None]:
		"""
		Returns a generator to iterate the path from node to another node.

		:param other:      Node to walk to.
		:returns:          Generator to iterate the path from node to other node.
		:raises Exception: If parameter ``other`` is not part of the same tree.
		"""
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

	def GetNodeByID(self, nodeID: IDType) -> 'Node':
		"""
		Lookup a node by its unique ID.

		:param nodeID:      ID of a node to lookup in the tree.
		:returns:           Node for the given ID.
		:raises ValueError: If parameter ``nodeID`` is None.
		:raises KeyError:   If parameter ``nodeID`` is not found in the tree.
		"""
		if nodeID is None:
			raise ValueError(f"'None' is not supported as an ID value.")

		return self._root._nodesWithID[nodeID]

	def Find(self, predicate: Callable) -> Generator['Node', None, None]:
		raise NotImplementedError(f"Method 'Find' is not yet implemented.")

	def __iter__(self) -> Iterator['Node']:
		"""
		Returns an iterator to iterate all child nodes.

		:returns: Children iterator.
		"""
		return iter(self._children)

	def __len__(self) -> int:
		"""
		Returns the number of children, but not including grand-children.

		:returns: Number of child nodes.
		"""
		return len(self._children)

	def __repr__(self) -> str:
		"""
		Returns a detailed string representation of the node.

		:returns: The detailed string representation of the node.
		"""
		nodeID = parent = value = ""
		if self._id is not None:
			nodeID = f"; nodeID='{self._id}'"
		if (self._parent is not None) and (self._parent._id is not None):
			parent = f"; parent='{self._parent._id}'"
		if self._value is not None:
			value = f"; value='{self._value}'"

		return f"<node{nodeID}{parent}{value}>"

	def __str__(self) -> str:
		"""
		Return a string representation of the node.

		Order of resolution:

		1. If :py:attr:`_value` is not None, return the string representation of :py:attr:`_value`.
		2. If :py:attr:`_id` is not None, return the string representation of :py:attr:`_id`.
		3. Else, return :py:meth:`__repr__`.

		:returns: The resolved string representation of the node.
		"""
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()
