# ==================================================================================================================== #
#             _____           _ _               _     _       _            _ _     _     _                             #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | |   (_)_ __ | | _____  __| | |   (_)___| |_                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |   | | '_ \| |/ / _ \/ _` | |   | / __| __|                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___| | | | |   <  __/ (_| | |___| \__ \ |_                           #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____|_|_| |_|_|\_\___|\__,_|_____|_|___/\__|                          #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""An object-oriented doubly linked-list data structure for Python."""

from collections.abc import Sized
from sys             import version_info
from typing          import Generic, TypeVar, Optional as Nullable, Callable, Iterable, Generator, Tuple, List, Any

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.LinkedList] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.LinkedList] Could not import directly!")
		raise ex


_NodeKey =   TypeVar("_NodeKey")
_NodeValue = TypeVar("_NodeValue")


@export
class LinkedListException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.LinkedList`."""


@export
class Node(Generic[_NodeKey, _NodeValue], metaclass=ExtendedType, slots=True):
	"""
	The node in an object-oriented doubly linked-list.

	It contains a reference to the doubly linked list (:attr:`_list`), the previous node (:attr:`_previous`), the next
	node (:attr:`_next`) and the data (:attr:`_value`). Optionally, a key (:attr:`_key`) can be stored for sorting
	purposes.

	The :attr:`_previous` field of the **first node** in a doubly linked list is ``None``. Similarly, the :attr:`_next`
	field of the **last node** is ``None``. ``None`` represents the end of the linked list when iterating it node-by-node.
	"""

	_linkedList:   Nullable["LinkedList[_NodeValue]"]      #: Reference to the doubly linked list instance.
	_previousNode: Nullable["Node[_NodeKey, _NodeValue]"]  #: Reference to the previous node.
	_nextNode:     Nullable["Node[_NodeKey, _NodeValue]"]  #: Reference to the next node.
	_key:          Nullable[_NodeKey]                      #: The sortable key of the node.
	_value:        _NodeValue                              #: The value of the node.

	def __init__(
		self,
		value:        _NodeValue,
		key:          Nullable[_NodeKey] = None,
		previousNode: Nullable["Node[_NodeKey, _NodeValue]"] = None,
		nextNode:     Nullable["Node[_NodeKey, _NodeValue]"] = None
	) -> None:
		"""
		Initialize a linked list node.

		:param value:        Value to store in the node.
		:param key:          Optional sortable key to store in the node.
		:param previousNode: Optional reference to the previous node.
		:param nextNode:     Optional reference to the next node.
		:raises TypeError:   If parameter 'previous' is not of type :class:`Node`.
		:raises TypeError:   If parameter 'next' is not of type :class:`Node`.
		"""
		self._previousNode = previousNode
		self._nextNode = nextNode
		self._value = value
		self._key = value

		# Attache to previous node
		if previousNode is not None:
			if not isinstance(previousNode, Node):
				ex = TypeError(f"Parameter 'previous' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(previousNode)}'.")
				raise ex

			# PreviousNode is part of a list
			if previousNode._linkedList is not None:
				self._linkedList = previousNode._linkedList
				self._linkedList._count += 1

				# Check if previous was the last node
				if previousNode._nextNode is None:
					self._nextNode = None
					self._linkedList._lastNode = self
				else:
					self._nextNode = previousNode._nextNode
					self._nextNode._previousNode = self
			else:
				self._linkedList = None

			previousNode._nextNode = self

			if nextNode is not None:
				if not isinstance(nextNode, Node):
					ex = TypeError(f"Parameter 'next' is not of type Node.")
					if version_info >= (3, 11):  # pragma: no cover
						ex.add_note(f"Got type '{getFullyQualifiedName(nextNode)}'.")
					raise ex

				if nextNode._linkedList is not None:
					if self._linkedList is not None:
						if self._linkedList is not previousNode._linkedList:
							raise ValueError()

				previousNode._nextNode = self
		elif nextNode is not None:
			if not isinstance(nextNode, Node):
				ex = TypeError(f"Parameter 'next' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(nextNode)}'.")
				raise ex

			# NextNode is part of a list
			if nextNode._linkedList is not None:
				self._linkedList = nextNode._linkedList
				self._linkedList._count += 1

				# Check if next was the first node
				if nextNode._previousNode is None:
					self._previousNode = None
					self._linkedList._firstNode = self
				else:
					self._previousNode = nextNode._previousNode
					self._previousNode._nextNode = self
			else:
				self._linkedList = None

			nextNode._previousNode = self
		else:
			self._linkedList = None

	@readonly
	def List(self) -> Nullable["LinkedList[_NodeValue]"]:
		"""
		Read-only property to access the linked list, this node belongs to.

		:return: The linked list, this node is part of, or ``None``.
		"""
		return self._linkedList

	@readonly
	def PreviousNode(self) -> Nullable["Node[_NodeKey, _NodeValue]"]:
		"""
		Read-only property to access nodes predecessor.

		This reference is ``None`` if the node is the first node in the doubly linked list.

		:return: The node before the current node or ``None``.
		"""
		return self._previousNode

	@readonly
	def NextNode(self) -> Nullable["Node[_NodeKey, _NodeValue]"]:
		"""
		Read-only property to access nodes successor.

		This reference is ``None`` if the node is the last node in the doubly linked list.

		:return: The node after the current node or ``None``.
		"""
		return self._nextNode

	@property
	def Key(self) -> _NodeKey:
		"""
		Property to access the node's internal key.

		The key can be a scalar or a reference to an object.

		:return: The node's key.
		"""
		return self._key

	@Key.setter
	def Key(self, key: _NodeKey) -> None:
		self._key = key

	@property
	def Value(self) -> _NodeValue:
		"""
		Property to access the node's internal data.

		The data can be a scalar or a reference to an object.

		:return: The node's value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: _NodeValue) -> None:
		self._value = value

	def InsertNodeBefore(self, node: "Node[_NodeKey, _NodeValue]") -> None:
		"""
		Insert a node before this node.

		:param node:                 Node to insert.
		:raises ValueError:          If parameter 'node' is ``None``.
		:raises TypeError:           If parameter 'node' is not of type :class:`Node`.
		:raises LinkedListException: If parameter 'node' is already part of another linked list.
		"""
		if node is None:
			raise ValueError(f"Parameter 'node' is None.")

		if not isinstance(node, Node):
			ex = TypeError(f"Parameter 'node' is not of type Node.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex

		if node._linkedList is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._linkedList = self._linkedList
		node._nextNode = self
		node._previousNode = self._previousNode
		if self._previousNode is None:
			self._linkedList._firstNode = node
		else:
			self._previousNode._nextNode = node
		self._previousNode = node
		self._linkedList._count += 1

	def InsertNodeAfter(self, node: "Node[_NodeKey, _NodeValue]") -> None:
		"""
		Insert a node after this node.

		:param node:                 Node to insert.
		:raises ValueError:          If parameter 'node' is ``None``.
		:raises TypeError:           If parameter 'node' is not of type :class:`Node`.
		:raises LinkedListException: If parameter 'node' is already part of another linked list.
		"""
		if node is None:
			raise ValueError(f"Parameter 'node' is None.")

		if not isinstance(node, Node):
			ex = TypeError(f"Parameter 'node' is not of type Node.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex

		if node._linkedList is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._linkedList = self._linkedList
		node._previousNode = self
		node._nextNode = self._nextNode
		if self._nextNode is None:
			self._linkedList._lastNode = node
		else:
			self._nextNode._previousNode = node
		self._nextNode = node
		self._linkedList._count += 1

	# move forward
	# move backward
	# move by relative pos
	# move to position
	# move to begin
	# move to end

	# insert tuple/list/linkedlist before
	# insert tuple/list/linkedlist after

	# iterate forward for n
	# iterate backward for n

	# slice to tuple / list starting from that node

	# swap left by n
	# swap right by n

	def Remove(self) -> _NodeValue:
		"""
		Remove this node from the linked list.
		"""
		if self._previousNode is None:
			if self._linkedList is not None:
				self._linkedList._firstNode = self._nextNode
				self._linkedList._count -= 1

				if self._nextNode is None:
					self._linkedList._lastNode = None

				self._linkedList = None

			if self._nextNode is not None:
				self._nextNode._previousNode = None

			self._nextNode = None
		elif self._nextNode is None:
			if self._linkedList is not None:
				self._linkedList._lastNode = self._previousNode
				self._linkedList._count -= 1
				self._linkedList = None

			self._previousNode._nextNode = None
			self._previousNode = None
		else:
			self._previousNode._nextNode = self._nextNode
			self._nextNode._previousNode = self._previousNode
			self._nextNode = None
			self._previousNode = None

			if self._linkedList is not None:
				self._linkedList._count -= 1
				self._linkedList = None

		return self._value

	def IterateToFirst(self, includeSelf: bool = False) -> Generator["Node[_NodeKey, _NodeValue]", None, None]:
		"""
		Return a generator iterating backward from this node to the list's first node.

		Optionally, this node can be included into the generated sequence.

		:param includeSelf: If ``True``, include this node into the sequence, otherwise start at previous node.
		:return:            A sequence of nodes towards the list's first node.
		"""
		previousNode = self._previousNode

		if includeSelf:
			yield self

		node = previousNode
		while node is not None:
			previousNode = node._previousNode
			yield node
			node = previousNode

	def IterateToLast(self, includeSelf: bool = False) -> Generator["Node[_NodeKey, _NodeValue]", None, None]:
		"""
		Return a generator iterating forward from this node to the list's last node.

		Optionally, this node can be included into the generated sequence by setting.

		:param includeSelf: If ``True``, include this node into the sequence, otherwise start at next node.
		:return:            A sequence of nodes towards the list's last node.
		"""
		nextNode = self._nextNode

		if includeSelf:
			yield self

		node = nextNode
		while node is not None:
			nextNode = node._nextNode
			yield node
			node = nextNode

	def __repr__(self) -> str:
		return f"Node: {self._value}"


@export
class LinkedList(Generic[_NodeKey, _NodeValue], metaclass=ExtendedType, slots=True):
	"""An object-oriented doubly linked-list."""

	_firstNode: Nullable[Node[_NodeKey, _NodeValue]]  #: Reference to the first node of the linked list.
	_lastNode:  Nullable[Node[_NodeKey, _NodeValue]]  #: Reference to the last node of the linked list.
	_count:     int                                   #: Number of nodes in the linked list.

	# allow iterable to initialize the list
	def __init__(self, nodes: Nullable[Iterable[Node[_NodeKey, _NodeValue]]] = None) -> None:
		"""
		Initialize an empty linked list.

		Optionally, an iterable can be given to initialize the linked list. The order is preserved.

		:param nodes:                Optional iterable to initialize the linked list.
		:raises TypeError:           If parameter 'nodes' is not an :class:`iterable <typing.Iterable>`.
		:raises TypeError:           If parameter 'nodes' items are not of type :class:`Node`.
		:raises LinkedListException: If parameter 'nodes' contains items which are already part of another linked list.
		"""
		if nodes is None:
			self._firstNode = None
			self._lastNode = None
			self._count = 0
		elif not isinstance(nodes, Iterable):
			ex = TypeError(f"Parameter 'nodes' is not an iterable.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex
		else:
			if isinstance(nodes, Sized) and len(nodes) == 0:
				self._firstNode = None
				self._lastNode = None
				self._count = 0
				return

			try:
				first = next(iterator := iter(nodes))
			except StopIteration:
				self._firstNode = None
				self._lastNode = None
				self._count = 0
				return

			if not isinstance(first, Node):
				ex = TypeError(f"First element in parameter 'nodes' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(first)}'.")
				raise ex
			elif first._linkedList is not None:
				raise LinkedListException(f"First element in parameter 'nodes' is assigned to different list.")

			position = 1
			first._linkedList = self
			first._previousNode = None
			self._firstNode = previous = node = first

			for node in iterator:
				if not isinstance(node, Node):
					ex = TypeError(f"{position}. element in parameter 'nodes' is not of type Node.")
					if version_info >= (3, 11):  # pragma: no cover
						ex.add_note(f"Got type '{getFullyQualifiedName(node)}'.")
					raise ex
				elif node._linkedList is not None:
					raise LinkedListException(f"{position}. element in parameter 'nodes' is assigned to different list.")

				node._linkedList = self
				node._previousNode = previous
				previous._nextNode = node

				previous = node
				position += 1

			self._lastNode = node
			self._count = position
			node._nextNode = None

	@readonly
	def IsEmpty(self) -> int:
		"""
		Read-only property to access the number of .

		This reference is ``None`` if the node is the last node in the doubly linked list.

		:return: ``True`` if linked list is empty, otherwise ``False``
		"""
		return self._count == 0

	@readonly
	def Count(self) -> int:
		"""
		Read-only property to access the number of nodes in the linked list.

		:return: Number of nodes.
		"""
		return self._count

	@readonly
	def FirstNode(self) -> Nullable[Node[_NodeKey, _NodeValue]]:
		"""
		Read-only property to access the first node in the linked list.

		In case the list is empty, ``None`` is returned.

		:return: First node.
		"""
		return self._firstNode

	@readonly
	def LastNode(self) -> Nullable[Node[_NodeKey, _NodeValue]]:
		"""
		Read-only property to access the last node in the linked list.

		In case the list is empty, ``None`` is returned.

		:return: Last node.
		"""
		return self._lastNode

	def Clear(self) -> None:
		"""
		Clear the linked list.
		"""
		self._firstNode = None
		self._lastNode = None
		self._count = 0

	def InsertBeforeFirst(self, node: Node[_NodeKey, _NodeValue]) -> None:
		"""
		Insert a node before the first node.

		:param node:                 Node to insert.
		:raises ValueError:          If parameter 'node' is ``None``.
		:raises TypeError:           If parameter 'node' is not of type :class:`Node`.
		:raises LinkedListException: If parameter 'node' is already part of another linked list.
		"""
		if node is None:
			raise ValueError(f"Parameter 'node' is None.")

		if not isinstance(node, Node):
			ex = TypeError(f"Parameter 'node' is not of type Node.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex

		if node._linkedList is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._linkedList = self
		node._previousNode = None
		node._nextNode = self._firstNode
		if self._firstNode is None:
			self._lastNode = node
		else:
			self._firstNode._previousNode = node
		self._firstNode = node
		self._count += 1

	def InsertAfterLast(self, node: Node[_NodeKey, _NodeValue]) -> None:
		"""
		Insert a node after the last node.

		:param node:                 Node to insert.
		:raises ValueError:          If parameter 'node' is ``None``.
		:raises TypeError:           If parameter 'node' is not of type :class:`Node`.
		:raises LinkedListException: If parameter 'node' is already part of another linked list.
		"""
		if node is None:
			raise ValueError(f"Parameter 'node' is None.")

		if not isinstance(node, Node):
			ex = TypeError(f"Parameter 'node' is not of type Node.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex

		if node._linkedList is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._linkedList = self
		node._nextNode = None
		node._previousNode = self._lastNode
		if self._lastNode is None:
			self._firstNode = node
		else:
			node._previousNode._nextNode = node
		self._lastNode = node
		self._count += 1

	def RemoveFirst(self) -> Node[_NodeKey, _NodeValue]:
		"""
		Remove first node from linked list.

		:return:                     First node.
		:raises LinkedListException: If linked list is empty.
		"""
		if self._firstNode is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._firstNode
		self._firstNode = node._nextNode
		if self._firstNode is None:
			self._lastNode = None
			self._count = 0
		else:
			self._firstNode._previousNode = None
			self._count -= 1

		node._linkedList = None
		node._nextNode = None
		return node

	def RemoveLast(self) -> Node[_NodeKey, _NodeValue]:
		"""
		Remove last node from linked list.

		:return:                     Last node.
		:raises LinkedListException: If linked list is empty.
		"""
		if self._lastNode is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._lastNode
		self._lastNode = node._previousNode
		if self._lastNode is None:
			self._firstNode = None
			self._count = 0
		else:
			self._lastNode._nextNode = None
			self._count -= 1

		node._linkedList = None
		node._previousNode = None
		return node


	def GetNodeByIndex(self, index: int) -> Node[_NodeKey, _NodeValue]:
		"""
		Access a node in the linked list by position.

		:param index:       Node position to access.
		:return:            Node at the given position.
		:raises ValueError: If parameter 'position' is out of range.

		.. note::

		   The algorithm starts iterating nodes from the shorter end.
		"""
		if index == 0:
			if self._firstNode is None:
				ex = ValueError("Parameter 'position' is out of range.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Linked list is empty.")
				raise ex

			return self._firstNode
		elif index == self._count - 1:
			return self._lastNode
		elif index >= self._count:
			ex = ValueError("Parameter 'position' is out of range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Linked list has {self._count} elements. Requested index: {index}.")
			raise ex

		if index < self._count / 2:
			pos = 1
			node = self._firstNode._nextNode
			while node is not None:
				if pos == index:
					return node

				node = node._nextNode
				pos += 1
			else:  # pragma: no cover
				raise LinkedListException(f"Node position not found.")
		else:
			pos = self._count - 2
			node = self._lastNode._previousNode
			while node is not None:
				if pos == index:
					return node

				node = node._previousNode
				pos -= 1
			else:  # pragma: no cover
				raise LinkedListException(f"Node position not found.")

	def Search(self, predicate: Callable[[Node], bool], reverse: bool = False) -> Node[_NodeKey, _NodeValue]:
		if self._firstNode is None:
			raise LinkedListException(f"Linked list is empty.")

		if not reverse:
			node = self._firstNode
			while node is not None:
				if predicate(node):
					break

				node = node._nextNode
			else:
				raise LinkedListException(f"Node not found.")
		else:
			node = self._lastNode
			while node is not None:
				if predicate(node):
					break

				node = node._previousNode
			else:
				raise LinkedListException(f"Node not found.")

		return node

	def Reverse(self) -> None:
		"""
		Reverse the order of nodes in the linked list.
		"""
		if self._firstNode is None or self._firstNode is self._lastNode:
			return

		node = self._lastNode = self._firstNode

		while node is not None:
			last = node
			node = last._nextNode
			last._nextNode = last._previousNode

		last._previousNode = node
		self._firstNode = last

	def Sort(self, key: Nullable[Callable[[Node[_NodeKey, _NodeValue]], Any]] = None, reverse: bool = False) -> None:
		"""
		Sort the linked list in ascending or descending order.

		The sort operation is **stable**.

		:param key:     Optional function to access a user-defined key for sorting.
		:param reverse: Optional parameter, if ``True`` sort in descending order, otherwise in ascending order.

		.. note::

		   The linked list is converted to an array, which is sorted by quicksort using the builtin :meth:`~list.sort`.
		   Afterward, the sorted array is used to reconstruct the linked list in requested order.
		"""
		if (self._firstNode is None) or (self._firstNode is self._lastNode):
			return

		if key is None:
			key = lambda node: node._value

		sequence = [n for n in self.IterateFromFirst()]
		sequence.sort(key=key, reverse=reverse)

		first = sequence[0]

		position = 1
		first._previousNode = None
		self._firstNode = previous = node = first

		for node in sequence[1:]:
			node._previousNode = previous
			previous._nextNode = node

			previous = node
			position += 1

		self._lastNode = node
		self._count = position
		node._nextNode = None

	def IterateFromFirst(self) -> Generator[Node[_NodeKey, _NodeValue], None, None]:
		"""
		Return a generator iterating forward from list's first node to list's last node.

		:return: A sequence of nodes towards the list's last node.
		"""
		if self._firstNode is None:
			return

		node = self._firstNode
		while node is not None:
			nextNode = node._nextNode
			yield node
			node = nextNode

	def IterateFromLast(self) -> Generator[Node[_NodeKey, _NodeValue], None, None]:
		"""
		Return a generator iterating backward from list's last node to list's first node.

		:return: A sequence of nodes towards the list's first node.
		"""
		if self._lastNode is None:
			return

		node = self._lastNode
		while node is not None:
			previousNode = node._previousNode
			yield node
			node = previousNode

	def ToList(self, reverse: bool = False) -> List[Node[_NodeKey, _NodeValue]]:
		"""
		Convert the linked list to a :class:`list`.

		Optionally, the resulting list can be constructed in reverse order.

		:param reverse: Optional parameter, if ``True`` return in reversed order, otherwise in normal order.
		:return:        A list (array) of this linked list's values.
		"""
		if self._count == 0:
			return []
		elif reverse:
			return [n._value for n in self.IterateFromLast()]
		else:
			return [n._value for n in self.IterateFromFirst()]

	def ToTuple(self, reverse: bool = False) -> Tuple[Node[_NodeKey, _NodeValue], ...]:
		"""
		Convert the linked list to a :class:`tuple`.

		Optionally, the resulting tuple can be constructed in reverse order.

		:param reverse: Optional parameter, if ``True`` return in reversed order, otherwise in normal order.
		:return:        A tuple of this linked list's values.
		"""
		if self._count == 0:
			return tuple()
		elif reverse:
			return tuple(n._value for n in self.IterateFromLast())
		else:
			return tuple(n._value for n in self.IterateFromFirst())

	# Copy
	# Sort

  # merge lists
	# append / prepend lists
	# split list

	# Remove at position (= __delitem__)
	# Remove by predicate (n times)

	# Insert at position (= __setitem__)

  # insert tuple/list/linkedlist at begin
	# insert tuple/list/linkedlist at end

	# Find by position (= __getitem__)
	# Find by predicate from left (n times)
	# Find by predicate from right (n times)

	# Count by predicate

	# slice by start, length from right -> new list
	# slice by start, length from left
	# Slice by predicate

	# iterate start, length from right
	# iterate start, length from left
	# iterate by predicate

	def __len__(self) -> int:
		"""
		Returns the number of nodes in the linked list.

		:returns: Number of nodes.
		"""
		return self._count

	def __getitem__(self, index: int) -> _NodeValue:
		"""
		Access a node's value by its index.

		:param index:       Node index to access.
		:return:            Node's value at the given index.
		:raises ValueError: If parameter 'index' is out of range.

		.. note::

		   The algorithm starts iterating nodes from the shorter end.
		"""
		return self.GetNodeByIndex(index)._value

	def __setitem__(self, index: int, value: _NodeValue) -> None:
		"""
		Set the value of node at the given position.

		:param index: Index of the node to modify.
		:param value: New value for the node's value addressed by index.
		"""
		self.GetNodeByIndex(index)._value = value

	def __delitem__(self, index: int) -> Node[_NodeKey, _NodeValue]:
		"""
		Remove a node at the given index.

		:param index: Index of the node to remove.
		:return:      Removed node.
		"""
		node = self.GetNodeByIndex(index)
		node.Remove()
		return node._value
