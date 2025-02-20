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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from collections   import deque
from sys           import version_info           # needed for versions before Python 3.11
from typing        import TypeVar, Generic, List, Tuple, Dict, Deque, Union, Optional as Nullable
from typing        import Callable, Iterator, Generator, Iterable, Mapping, Hashable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Tree] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, mixin
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Tree] Could not import directly!")
		raise ex


IDType = TypeVar("IDType", bound=Hashable)
"""A type variable for a tree's ID."""

ValueType = TypeVar("ValueType")
"""A type variable for a tree's value."""

DictKeyType = TypeVar("DictKeyType")
"""A type variable for a tree's dictionary keys."""

DictValueType = TypeVar("DictValueType")
"""A type variable for a tree's dictionary values."""


@export
class TreeException(ToolingException):
	"""Base exception of all exceptions raised by :mod:`pyTooling.Tree`."""


@export
class InternalError(TreeException):
	"""
	The exception is raised when a data structure corruption is detected.

	.. danger::

	   This exception should never be raised.

	   If so, please create an issue at GitHub so the data structure corruption can be investigated and fixed. |br|
	   `⇒ Bug Tracker at GitHub <https://github.com/pyTooling/pyTooling/issues>`__
	"""


@export
class NoSiblingsError(TreeException):
	"""
	The exception is raised when a node has no parent and thus has no siblings.

	.. hint::

	   A node with no parent is the root node of the tree.
	"""


@export
class AlreadyInTreeError(TreeException):
	"""
	The exception is raised when the current node and the other node are already in the same tree.

	.. hint::

	   A tree a an acyclic graph without cross-edges. Thus backward edges and cross edges are permitted.
	"""


@export
class NotInSameTreeError(TreeException):
	"""The exception is raised when the current node and the other node are not in the same tree."""


@export
class Node(Generic[IDType, ValueType, DictKeyType, DictValueType], metaclass=ExtendedType, slots=True):
	"""
	A **tree** data structure can be constructed of ``Node`` instances.

	Therefore, nodes can be connected to parent nodes or a parent node can add child nodes. This allows to construct a
	tree top-down or bottom-up.

	.. hint:: The top-down construction should be preferred, because it's slightly faster.

	Each tree uses the **root** node (a.k.a. tree-representative) to store some per-tree data structures. E.g. a list of
	all IDs in a tree. For easy and quick access to such data structures, each sibling node contains a reference to the
	root node (:attr:`_root`). In case of adding a tree to an existing tree, such data structures get merged and all added
	nodes get assigned with new root references. Use the read-only property :attr:`Root` to access the root reference.

	The reference to the parent node (:attr:`_parent`) can be access via property :attr:`Parent`. If the property's setter
	is used, a node and all its siblings are added to another tree or to a new position in the same tree.

	The references to all node's children is stored in a list (:attr:`_children`). Children, siblings, ancestors, can be
	accessed via various generators:

	* :meth:`GetAncestors` |rarr| iterate all ancestors bottom-up.
	* :meth:`GetChildren` |rarr| iterate all direct children.
	* :meth:`GetDescendants` |rarr| iterate all descendants.
	* :meth:`IterateLevelOrder` |rarr| IterateLevelOrder.
	* :meth:`IteratePreOrder` |rarr| iterate siblings in pre-order.
	* :meth:`IteratePostOrder` |rarr| iterate siblings in post-order.

	Each node can have a **unique ID** or no ID at all (``nodeID=None``). The root node is used to store all IDs in a
	dictionary (:attr:`_nodesWithID`). In case no ID is given, all such ID-less nodes are collected in a single bin and store as a
	list of nodes. An ID can be modified after the Node was created. Use the read-only property :attr:`ID` to access
	the ID.

	Each node can have a **value** (:attr:`_value`), which can be given at node creation time, or it can be assigned and/or
	modified later. Use the property :attr:`Value` to get or set the value.

	Moreover, each node can store various key-value-pairs (:attr:`_dict`). Use the dictionary syntax to get and set
	key-value-pairs.
	"""

	_id: Nullable[IDType]                         #: Unique identifier of a node. ``None`` if not used.
	_nodesWithID: Nullable[Dict[IDType, 'Node']]  #: Dictionary of all IDs in the tree. ``None`` if it's not the root node.
	_nodesWithoutID: Nullable[List['Node']]       #: List of all nodes without an ID in the tree. ``None`` if it's not the root node.
	_root: 'Node'                                 #: Reference to the root of a tree. ``self`` if it's the root node.
	_parent: Nullable['Node']                     #: Reference to the parent node. ``None`` if it's the root node.
	_children: List['Node']                       #: List of all children
#	_links: List['Node']

	_level: int                                   #: Level of the node (distance to the root).
	_value: Nullable[ValueType]                   #: Field to store the node's value.
	_dict: Dict[DictKeyType, DictValueType]       #: Dictionary to store key-value-pairs attached to the node.

	_format: Nullable[Callable[["Node"], str]]    #: A node formatting function returning a one-line representation for tree-rendering.

	def __init__(
		self,
		nodeID: Nullable[IDType] = None,
		value: Nullable[ValueType] = None,
		keyValuePairs: Nullable[Mapping[DictKeyType, DictValueType]] = None,
		parent: 'Node' = None,
		children: Nullable[Iterable['Node']] = None,
		format: Nullable[Callable[["Node"], str]] = None
	) -> None:
		"""
		.. todo:: TREE::Node::init Needs documentation.

		:param nodeID:        The optional unique ID of a node within the whole tree data structure.
		:param value:         The optional value of the node.
		:param keyValuePairs: The optional mapping (dictionary) of key-value-pairs.
		:param parent:        The optional parent node in the tree.
		:param children:      The optional list of child nodes.
		:param format:        The optional node formatting function returning a one-line representation for tree-rendering.

		:raises TypeError:    If parameter parent is not an instance of Node.
		:raises ValueError:   If nodeID already exists in the tree.
		:raises TypeError:    If parameter children is not iterable.
		:raises ValueError:   If an element of children is not an instance of Node.
		"""

		self._id = nodeID
		self._value = value
		self._dict = {key: value for key, value in keyValuePairs.items()} if keyValuePairs is not None else {}

		self._format = format

		if parent is not None and not isinstance(parent, Node):
			ex = TypeError(f"Parameter 'parent' is not of type 'Node'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

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
				ex = TypeError(f"Parameter 'children' is not iterable.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(children)}'.")
				raise ex

			for child in children:
				if not isinstance(child, Node):
					ex = TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")
					if version_info >= (3, 11):  # pragma: no cover
						ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
					raise ex

				child.Parent = self

	@readonly
	def ID(self) -> Nullable[IDType]:
		"""
		Read-only property to access the unique ID of a node (:attr:`_id`).

		If no ID was given at node construction time, ID return None.

		:returns: Unique ID of a node, if ID was given at node creation time, else None.
		"""
		return self._id

	@property
	def Value(self) -> Nullable[ValueType]:
		"""
		Property to get and set the value (:attr:`_value`) of a node.

		:returns: The value of a node.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Nullable[ValueType]) -> None:
		self._value = value

	def __getitem__(self, key: DictKeyType) -> DictValueType:
		"""
		Read a node's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: DictKeyType, value: DictValueType) -> None:
		"""
		Create or update a node's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key:   The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: DictKeyType) -> None:
		"""
		.. todo:: TREE::Node::__delitem__ Needs documentation.

		"""
		del self._dict[key]

	def __contains__(self, key: DictKeyType) -> bool:
		"""
		.. todo:: TREE::Node::__contains__ Needs documentation.

		"""
		return key in self._dict

	def __len__(self) -> int:
		"""
		Returns the number of attached attributes (key-value-pairs) on this node.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	@readonly
	def Root(self) -> 'Node':
		"""
		Read-only property to access the tree's root node (:attr:`_root`).

		:returns: The root node (representative node) of a tree.
		"""
		return self._root

	@property
	def Parent(self) -> Nullable['Node']:
		"""
		Property to get and set the parent (:attr:`_parent`) of a node.

		.. note::

		   As the current node might be a tree itself, appending this node to a tree can lead to a merge of trees and
		   especially to a merge of IDs. As IDs are unique, it might raise an :exc:`Exception`.

		:returns:                   The parent of a node.
		:raises TypeError:          If parameter ``parent`` is not a :class:`Node`
		:raises AlreadyInTreeError: Parent is already a child node in this tree.
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
			ex = TypeError(f"Parameter 'parent' is not of type 'Node'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		else:
			if parent._root is self._root:
				raise AlreadyInTreeError(f"Parent '{parent}' is already a child node in this tree.")

			self._root = parent._root
			self._parent = parent
			self._level = parent._level + 1
			for node in self.GetDescendants():
				node._level = node._parent._level + 1
			self._SetNewRoot(self._nodesWithID, self._nodesWithoutID)
			self._nodesWithID = self._nodesWithoutID = None
			parent._children.append(self)

	@readonly
	def Siblings(self) -> Tuple['Node', ...]:
		"""
		A read-only property to return a tuple of all siblings from the current node.

		If the current node is the only child, the tuple is empty.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A tuple of all siblings of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		return tuple([node for node in self._parent if node is not self])

	@readonly
	def LeftSiblings(self) -> Tuple['Node', ...]:
		"""
		A read-only property to return a tuple of all siblings left from the current node.

		If the current node is the only child, the tuple is empty.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A tuple of all siblings left of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		result = []
		for node in self._parent:
			if node is not self:
				result.append(node)
			else:
				break
		else:
			raise InternalError(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		return tuple(result)

	@readonly
	def RightSiblings(self) -> Tuple['Node', ...]:
		"""
		A read-only property to return a tuple of all siblings right from the current node.

		If the current node is the only child, the tuple is empty.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A tuple of all siblings right of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		result = []
		iterator = iter(self._parent)
		for node in iterator:
			if node is self:
				break
		else:
			raise InternalError(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		for node in iterator:
			result.append(node)

		return tuple(result)

	def _GetPathAsLinkedList(self) -> Deque["Node"]:
		"""
		Compute the path from current node to root node by using a linked list (:class:`deque`).

		:meta private:
		:returns: Path from node to root node as double-ended queue (deque).
		"""
		path: Deque['Node'] = deque()

		node = self
		while node is not None:
			path.appendleft(node)
			node = node._parent

		return path

	@readonly
	def Path(self) -> Tuple['Node']:
		"""
		Read-only property to return the path from root node to the node as a tuple of nodes.

		:returns: A tuple of nodes describing the path from root node to the node.
		"""
		return tuple(self._GetPathAsLinkedList())

	@readonly
	def Level(self) -> int:
		"""
		Read-only property to return a node's level in the tree.

		The level is the distance to the root node.

		:returns: The node's level.
		"""
		return self._level

	@readonly
	def Size(self) -> int:
		"""
		Read-only property to return the size of the tree.

		:returns: Count of all nodes in the tree structure.
		"""
		return len(self._root._nodesWithID) + len(self._root._nodesWithoutID)

	@readonly
	def IsRoot(self) -> bool:
		"""
		Returns true, if the node is the root node (representative node of the tree).

		:returns: ``True``, if node is the root node.
		"""
		return self._parent is None

	@readonly
	def IsLeaf(self) -> bool:
		"""
		Returns true, if the node is a leaf node (has no children).

		:returns: ``True``, if node has no children.
		"""
		return len(self._children) == 0

	@readonly
	def HasChildren(self) -> bool:
		"""
		Returns true, if the node has child nodes.

		:returns: ``True``, if node has children.
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

		If ``child`` is a subtree, both trees get merged. So all nodes in ``child`` get a new :attr:`_root` assigned and
		all IDs are merged into the node's root's ID lists (:attr:`_nodesWithID`).

		:param child:               The child node to be added to the tree.
		:raises TypeError:          If parameter ``child`` is not a :class:`Node`.
		:raises AlreadyInTreeError: If parameter ``child`` is already a node in the tree.

		.. seealso::

		   :attr:`Parent` |br|
		      |rarr| Set the parent of a node.
		   :meth:`AddChildren` |br|
		      |rarr| Add multiple children at once.
		"""
		if not isinstance(child, Node):
			ex = TypeError(f"Parameter 'child' is not of type 'Node'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
			raise ex

		if child._root is self._root:
			raise AlreadyInTreeError(f"Child '{child}' is already a node in this tree.")

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

		:param children:            The list of children nodes to be added to the tree.
		:raises TypeError:          If parameter ``children`` contains an item, which is not a :class:`Node`.
		:raises AlreadyInTreeError: If parameter ``children`` contains an item, which is already a node in the tree.

		.. seealso::

		   :attr:`Parent` |br|
		      |rarr| Set the parent of a node.
		   :meth:`AddChild` |br|
		      |rarr| Add a child node to the tree.
		"""
		for child in children:
			if not isinstance(child, Node):
				ex = TypeError(f"Item '{child}' in parameter 'children' is not of type 'Node'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(child)}'.")
				raise ex

			if child._root is self._root:
				# TODO: create a more specific exception
				raise AlreadyInTreeError(f"Child '{child}' is already a node in this tree.")

			child._root = self._root
			child._parent = self
			child._level = self._level + 1
			for node in child.GetDescendants():
				node._level = node._parent._level + 1
			self._SetNewRoot(child._nodesWithID, child._nodesWithoutID)
			child._nodesWithID = child._nodesWithoutID = None
			self._children.append(child)

	def GetPath(self) -> Generator['Node', None, None]:
		"""
		.. todo:: TREE::Node::GetPAth Needs documentation.

		"""
		for node in self._GetPathAsLinkedList():
			yield node

	def GetAncestors(self) -> Generator['Node', None, None]:
		"""
		.. todo:: TREE::Node::GetAncestors Needs documentation.

		"""
		node = self._parent
		while node is not None:
			yield node
			node = node._parent

	def GetCommonAncestors(self, others: Union['Node', Iterable['Node']]) -> Generator['Node', None, None]:
		"""
		.. todo:: TREE::Node::GetCommonAncestors Needs documentation.

		"""
		if isinstance(others, Node):
			# Check for trivial case
			if others is self:
				for node in self._GetPathAsLinkedList():
					yield node
				return

			# Check if both are in the same tree.
			if self._root is not others._root:
				raise NotInSameTreeError(f"Node 'others' is not in the same tree.")

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

		:returns: A generator to iterate all children.

		.. seealso::

		   :meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.
		"""
		for child in self._children:
			yield child

	def GetSiblings(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A generator to iterate all siblings of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		for node in self._parent:
			if node is self:
				continue

			yield node

	def GetLeftSiblings(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings left from the current node.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A generator to iterate all siblings left of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		for node in self._parent:
			if node is self:
				break

			yield node
		else:
			raise InternalError(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

	def GetRightSiblings(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings right from the current node.

		Siblings are child nodes of the current node's parent node, without the current node itself.

		:returns:                A generator to iterate all siblings right of the current node.
		:raises NoSiblingsError: If the current node has no parent node and thus no siblings.
		"""
		if self._parent is None:
			raise NoSiblingsError(f"Root node has no siblings.")

		iterator = iter(self._parent)
		for node in iterator:
			if node is self:
				break
		else:
			raise InternalError(f"Data structure corruption: Self is not part of parent's children.")  # pragma: no cover

		for node in iterator:
			yield node

	def GetDescendants(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all descendants of the current node. In contrast to `IteratePreOrder` and `IteratePostOrder`
		it doesn't include the node itself.

		:returns: A generator to iterate all descendants.

		.. seealso::

		   :meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.
		"""
		for child in self._children:
			yield child
			yield from child.GetDescendants()

	def GetRelatives(self):
		"""
		A generator to iterate all relatives (all siblings and all their descendants) of the current node.

		:returns: A generator to iterate all relatives.
		"""
		for node in self.GetSiblings():
			yield node
			yield from node.GetDescendants()

	def GetLeftRelatives(self):
		"""
		A generator to iterate all left relatives (left siblings and all their descendants) of the current node.

		:returns: A generator to iterate all left relatives.
		"""
		for node in self.GetLeftSiblings():
			yield node
			yield from node.GetDescendants()

	def GetRightRelatives(self):
		"""
		A generator to iterate all right relatives (right siblings and all their descendants) of the current node.

		:returns: A generator to iterate all right relatives.
		"""
		for node in self.GetRightSiblings():
			yield node
			yield from node.GetDescendants()

	def IterateLeafs(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all leaf-nodes in a subtree, which subtree root is the current node.

		:returns: A generator to iterate leaf-nodes reachable from current node.
		"""
		for child in self._children:
			if child.IsLeaf:
				yield child
			else:
				yield from child.IterateLeafs()

	def IterateLevelOrder(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings of the current node level-by-level top-down. In contrast to `GetDescendants`,
		this includes also the node itself as the first returned node.

		:returns: A generator to iterate all siblings level-by-level.

		.. seealso::

		   :meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		   :meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.
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

		:returns: A generator to iterate all siblings in pre-order.

		.. seealso::

		   :meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :meth:`IteratePostOrder` |br|
		      |rarr| Iterate items in post-order, which includes the node itself as a last returned node.
		"""
		yield self
		for child in self._children:
			yield from child.IteratePreOrder()

	def IteratePostOrder(self) -> Generator['Node', None, None]:
		"""
		A generator to iterate all siblings of the current node in post-order. In contrast to `GetDescendants`, this
		includes also the node itself as the last returned node.

		:returns: A generator to iterate all siblings in post-order.

		.. seealso::

		   :meth:`GetChildren` |br|
		      |rarr| Iterate all children, but no grand-children.
		   :meth:`GetDescendants` |br|
		      |rarr| Iterate all descendants.
		   :meth:`IterateLevelOrder` |br|
		      |rarr| Iterate items level-by-level, which includes the node itself as a first returned node.
		   :meth:`IteratePreOrder` |br|
		      |rarr| Iterate items in pre-order, which includes the node itself as a first returned node.
		"""
		for child in self._children:
			yield from child.IteratePostOrder()
		yield self

	def WalkTo(self, other: 'Node') -> Generator['Node', None, None]:
		"""
		Returns a generator to iterate the path from node to another node.

		:param other:               Node to walk to.
		:returns:                   Generator to iterate the path from node to other node.
		:raises NotInSameTreeError: If parameter ``other`` is not part of the same tree.
		"""
		# Check for trivial case
		if other is self:
			yield from ()

		# Check if both are in the same tree.
		if self._root is not other._root:
			raise NotInSameTreeError(f"Node 'other' is not in the same tree.")

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

		1. If :attr:`_value` is not None, return the string representation of :attr:`_value`.
		2. If :attr:`_id` is not None, return the string representation of :attr:`_id`.
		3. Else, return :meth:`__repr__`.

		:returns: The resolved string representation of the node.
		"""
		if self._value is not None:
			return str(self._value)
		elif self._id is not None:
			return str(self._id)
		else:
			return self.__repr__()

	def Render(
		self,
		prefix: str = "",
		lineend: str = "\n",
		nodeMarker: str = "├─",
		lastNodeMarker: str = "└─",
		bypassMarker: str = "│ "
	) -> str:
		"""
		Render the tree as ASCII art.

		:param prefix:         A string printed in front of every line, e.g. for indentation. Default: ``""``.
		:param lineend:        A string printed at the end of every line. Default: ``"\\n"``.
		:param nodeMarker:     A string printed before every non-last tree node. Default: ``"├─"``.
		:param lastNodeMarker: A string printed before every last tree node. Default: ``"└─"``.
		:param bypassMarker:   A string printed when there are further nodes in the parent level. Default: ``"│ "``.
		:return:               A rendered tree as multiline string.
		"""
		emptyMarker = " " * len(bypassMarker)

		def _render(node: Node, markers: str):
			result = []

			if node.HasChildren:
				for child in node._children[:-1]:
					nodeRepresentation = child._format(child) if child._format else str(child)
					result.append(f"{prefix}{markers}{nodeMarker}{nodeRepresentation}{lineend}")
					result.extend(_render(child, markers + bypassMarker))

				# last child node
				child = node._children[-1]
				nodeRepresentation = child._format(child) if child._format else str(child)
				result.append(f"{prefix}{markers}{lastNodeMarker}{nodeRepresentation}{lineend}")
				result.extend(_render(child, markers + emptyMarker))

			return result

		# Root element
		nodeRepresentation = self._format(self) if self._format else str(self)
		result = [f"{prefix}{nodeRepresentation}{lineend}"]
		result.extend(_render(self, ""))

		return "".join(result)
