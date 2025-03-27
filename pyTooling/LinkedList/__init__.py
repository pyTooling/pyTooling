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
	print("[pyTooling.List] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.List] Could not import directly!")
		raise ex


_NodeValue = TypeVar("_NodeValue")


@export
class LinkedListException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.LinkedList`."""


@export
class Node(Generic[_NodeValue], metaclass=ExtendedType, slots=True):
	"""
	The node in an object-oriented doubly linked-list.

	It contains a reference to the doubly linked list (:attr:`_list`), the previous node (:attr:`_previous`), the next
	node (:attr:`_next`) and the stored data (:attr:`_value`).

	The :attr:`_previous` field of the **first node** in a doubly linked list is ``None``. Similarly, the :attr:`_next`
	field of the **last node** is ``None``. ``None`` represents the end of the linked list when iterating it node-by-node.
	"""

	_list:     Nullable["LinkedList[_NodeValue]"]  #: Reference to the doubly linked list instance.
	_previous: Nullable["Node[_NodeValue]"]        #: Reference to the previous node.
	_next:     Nullable["Node[_NodeValue]"]        #: Reference to the next node.
	_value:    _NodeValue                          #: The value of the node.

	def __init__(
		self,
		value: _NodeValue,
		previous: Nullable["Node[_NodeValue]"] = None,
		next: Nullable["Node[_NodeValue]"] = None
	) -> None:
		"""
		Initialize a linked list node.

		:param value:      Value to store in the node.
		:param previous:   Optional reference to the previous node.
		:param next:       Optional reference to the next node.
		:raises TypeError: If parameter 'previous' is not of type :class:`Node`.
		:raises TypeError: If parameter 'next' is not of type :class:`Node`.
		"""
		self._previous = previous
		self._next = next
		self._value = value

		# Attache to previous node
		if previous is not None:
			if not isinstance(previous, Node):
				ex = TypeError(f"Parameter 'previous' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(previous)}'.")
				raise ex

			# Previous is part of a list
			if previous._list is not None:
				self._list = previous._list
				self._list._count += 1

				# Check if previous was the last node
				if previous._next is None:
					self._next = None
					self._list._last = self
				else:
					self._next = previous._next
					self._next._previous = self
			else:
				self._list = None

			previous._next = self

			if next is not None:
				if not isinstance(next, Node):
					ex = TypeError(f"Parameter 'next' is not of type Node.")
					if version_info >= (3, 11):  # pragma: no cover
						ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
					raise ex

				if next._list is not None:
					if self._list is not None:
						if self._list is not previous._list:
							raise ValueError()


				previous._next = self
		elif next is not None:
			if not isinstance(next, Node):
				ex = TypeError(f"Parameter 'next' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
				raise ex

			# Next is part of a list
			if next._list is not None:
				self._list = next._list
				self._list._count += 1

				# Check if next was the first node
				if next._previous is None:
					self._previous = None
					self._list._first = self
				else:
					self._previous = next._previous
					self._previous._next = self
			else:
				self._list = None

			next._previous = self
		else:
			self._list = None

	@readonly
	def List(self) -> Nullable["LinkedList[_NodeValue]"]:
		"""
		Read-only property to access the linked list, this node belongs to.

		:return: The linked list, this node is part of, or ``None``.
		"""
		return self._list

	@readonly
	def Previous(self) -> Nullable["Node[_NodeValue]"]:
		"""
		Read-only property to access nodes predecessor.

		This reference is ``None`` if the node is the first node in the doubly linked list.

		:return: The node before the current node or ``None``.
		"""
		return self._previous

	@readonly
	def Next(self) -> Nullable["Node[_NodeValue]"]:
		"""
		Read-only property to access nodes successor.

		This reference is ``None`` if the node is the last node in the doubly linked list.

		:return: The node after the current node or ``None``.
		"""
		return self._next

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

	def InsertBefore(self, node: "Node[_NodeValue]") -> None:
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

		if node._list is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._list = self._list
		node._next = self
		node._previous = self._previous
		if self._previous is None:
			self._list._first = node
		else:
			self._previous._next = node
		self._previous = node
		self._list._count += 1

	def InsertAfter(self, node: "Node[_NodeValue]") -> None:
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

		if node._list is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._list = self._list
		node._previous = self
		node._next = self._next
		if self._next is None:
			self._list._last = node
		else:
			self._next._previous = node
		self._next = node
		self._list._count += 1

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

	def Remove(self) -> None:
		"""
		Remove this node from the linked list.
		"""
		if self._previous is None:
			if self._list is not None:
				self._list._first = self._next
				self._list._count -= 1

				if self._next is None:
					self._list._last = None

				self._list = None

			if self._next is not None:
				self._next._previous = None

			self._next = None
		elif self._next is None:
			if self._list is not None:
				self._list._last = self._previous
				self._list._count -= 1
				self._list = None

			self._previous._next = None
			self._previous = None
		else:
			self._previous._next = self._next
			self._next._previous = self._previous
			self._next = None
			self._previous = None

			if self._list is not None:
				self._list._count -= 1
				self._list = None

	def IterateToFirst(self, includeSelf: bool = False) -> Generator["Node[_NodeValue]", None, None]:
		"""
		Return a generator iterating backward from this node to the list's first node.

		Optionally, this node can be included into the generated sequence.

		:param includeSelf: If ``True``, include this node into the sequence, otherwise start at previous node.
		:return:            A sequence of nodes towards the list's first node.
		"""
		if includeSelf:
			yield self

		node = self._previous

		while node is not None:
			yield node
			node = node._previous

	def IterateToLast(self, includeSelf: bool = False) -> Generator["Node[_NodeValue]", None, None]:
		"""
		Return a generator iterating forward from this node to the list's last node.

		Optionally, this node can be included into the generated sequence by setting.

		:param includeSelf: If ``True``, include this node into the sequence, otherwise start at next node.
		:return:            A sequence of nodes towards the list's last node.
		"""
		if includeSelf:
			yield self

		node = self._next

		while node is not None:
			yield node
			node = node._next

	def __repr__(self) -> str:
		return f"Node: {self._value}"


@export
class LinkedList(Generic[_NodeValue], metaclass=ExtendedType, slots=True):
	"""An object-oriented doubly linked-list."""

	_first: Nullable[Node[_NodeValue]]  #: Reference to the first node of the linked list.
	_last:  Nullable[Node[_NodeValue]]  #: Reference to the last node of the linked list.
	_count: int                         #: Number of nodes in the linked list.

	# allow iterable to initialize the list
	def __init__(self, nodes: Nullable[Iterable[Node[_NodeValue]]] = None) -> None:
		"""
		Initialize an empty linked list.

		Optionally, an iterable can be given to initialize the linked list. The order is preserved.

		:param nodes:                Optional iterable to initialize the linked list.
		:raises TypeError:           If parameter 'nodes' is not an :class:`iterable <typing.Iterable>`.
		:raises TypeError:           If parameter 'nodes' items are not of type :class:`Node`.
		:raises LinkedListException: If parameter 'nodes' contains items which are already part of another linked list.
		"""
		if nodes is None:
			self._first = None
			self._last = None
			self._count = 0
		elif not isinstance(nodes, Iterable):
			ex = TypeError(f"Parameter 'nodes' is not an iterable.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex
		else:
			if isinstance(nodes, Sized) and len(nodes) == 0:
				self._first = None
				self._last = None
				self._count = 0
				return

			try:
				first = next(iterator := iter(nodes))
			except StopIteration:
				self._first = None
				self._last = None
				self._count = 0
				return

			if not isinstance(first, Node):
				ex = TypeError(f"First element in parameter 'nodes' is not of type Node.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(first)}'.")
				raise ex
			elif first._list is not None:
				raise LinkedListException(f"First element in parameter 'nodes' is assigned to different list.")

			position = 1
			first._list = self
			first._previous = None
			self._first = previous = node = first

			for node in iterator:
				if not isinstance(node, Node):
					ex = TypeError(f"{position}. element in parameter 'nodes' is not of type Node.")
					if version_info >= (3, 11):  # pragma: no cover
						ex.add_note(f"Got type '{getFullyQualifiedName(node)}'.")
					raise ex
				elif node._list is not None:
					raise LinkedListException(f"{position}. element in parameter 'nodes' is assigned to different list.")

				node._list = self
				node._previous = previous
				previous._next = node

				previous = node
				position += 1

			self._last = node
			self._count = position
			node._next = None

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
	def First(self) -> Nullable[Node[_NodeValue]]:
		"""
		Read-only property to access the first node in the linked list.

		In case the list is empty, ``None`` is returned.

		:return: First node.
		"""
		return self._first

	@readonly
	def Last(self) -> Nullable[Node[_NodeValue]]:
		"""
		Read-only property to access the last node in the linked list.

		In case the list is empty, ``None`` is returned.

		:return: Last node.
		"""
		return self._last

	def Clear(self) -> None:
		"""
		Clear the linked list.
		"""
		self._first = None
		self._last = None
		self._count = 0

	def InsertBeforeFirst(self, node: Node[_NodeValue]) -> None:
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

		if node._list is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._list = self
		node._previous = None
		node._next = self._first
		if self._first is None:
			self._last = node
		else:
			self._first._previous = node
		self._first = node
		self._count += 1

	def InsertAfterLast(self, node: Node[_NodeValue]) -> None:
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

		if node._list is not None:
			raise LinkedListException(f"Parameter 'node' belongs to another linked list.")

		node._list = self
		node._next = None
		node._previous = self._last
		if self._last is None:
			self._first = node
		else:
			node._previous._next = node
		self._last = node
		self._count += 1

	def RemoveFirst(self) -> Node[_NodeValue]:
		"""
		Remove first node from linked list.

		:return:                     First node.
		:raises LinkedListException: If linked list is empty.
		"""
		if self._first is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._first
		self._first = node._next
		if self._first is None:
			self._last = None
			self._count = 0
		else:
			self._first._previous = None
			self._count -= 1

		node._list = None
		node._next = None
		return node

	def RemoveLast(self) -> Node[_NodeValue]:
		"""
		Remove last node from linked list.

		:return:                     Last node.
		:raises LinkedListException: If linked list is empty.
		"""
		if self._last is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._last
		self._last = node._previous
		if self._last is None:
			self._first = None
			self._count = 0
		else:
			self._last._next = None
			self._count -= 1

		node._list = None
		node._previous = None
		return node

	def Search(self, predicate: Callable[[Node], bool], reverse: bool = False) -> Node[_NodeValue]:
		if self._first is None:
			raise LinkedListException(f"Linked list is empty.")

		if not reverse:
			node = self._first
			while node is not None:
				if predicate(node):
					break

				node = node._next
			else:
				raise LinkedListException(f"Node not found.")
		else:
			node = self._last
			while node is not None:
				if predicate(node):
					break

				node = node._previous
			else:
				raise LinkedListException(f"Node not found.")

		return node

	def Reverse(self) -> None:
		"""
		Reverse the order of nodes in the linked list.
		"""
		if self._first is None or self._first is self._last:
			return

		node = self._last = self._first

		while node is not None:
			last = node
			node = last._next
			last._next = last._previous

		last._previous = node
		self._first = last

	def Sort(self, key: Nullable[Callable[[Node[_NodeValue]], Any]] = None, reverse: bool = False) -> None:
		"""
		Sort the linked list in ascending or descending order.

		The sort operation is **stable**.

		:param key:     Optional function to access a user-defined key for sorting.
		:param reverse: Optional parameter, if ``True`` sort in descending order, otherwise in ascending order.

		.. note::

		   The linked list is converted to an array, which is sorted by quicksort using the builtin :meth:`~list.sort`.
		   Afterward, the sorted array is used to reconstruct the linked list in requested order.
		"""
		if (self._first is None) or (self._first is self._last):
			return

		if key is None:
			key = lambda node: node._value

		sequence = [n for n in self.IterateFromFirst()]
		sequence.sort(key=key, reverse=reverse)

		first = sequence[0]

		position = 1
		first._previous = None
		self._first = previous = node = first

		for node in sequence[1:]:
			node._previous = previous
			previous._next = node

			previous = node
			position += 1

		self._last = node
		self._count = position
		node._next = None

	def IterateFromFirst(self) -> Generator[Node[_NodeValue], None, None]:
		"""
		Return a generator iterating forward from list's first node to list's last node.

		:return: A sequence of nodes towards the list's last node.
		"""
		if self._first is None:
			return

		node = self._first

		while node is not None:
			yield node
			node = node._next

	def IterateFromLast(self) -> Generator[Node[_NodeValue], None, None]:
		"""
		Return a generator iterating backward from list's last node to list's first node.

		:return: A sequence of nodes towards the list's first node.
		"""
		if self._last is None:
			return

		node = self._last

		while node is not None:
			yield node
			node = node._previous

	def ToList(self, reverse: bool = False) -> List[Node[_NodeValue]]:
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

	def ToTuple(self, reverse: bool = False) -> Tuple[Node[_NodeValue], ...]:
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

	def __getitem__(self, position: int) -> Node[_NodeValue]:
		"""
		Access a node in the linked list by position.

		:param position:    Node position to access.
		:return:            Node at the given position.
		:raises ValueError: If parameter 'position' is out of range.

		.. note::

		   The algorithm starts iterating nodes from the shorter end.
		"""
		if position == 0:
			if self._first is None:
				ex = ValueError("Parameter 'position' is out of range.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Linked list is empty.")
				raise ex

			return self._first
		elif position == self._count - 1:
			return self._last
		elif position >= self._count:
			ex = ValueError("Parameter 'position' is out of range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Linked list has {self._count} elements. Requested index: {position}.")
			raise ex

		if position < self._count / 2:
			pos = 1
			node = self._first._next
			while node is not None:
				if pos == position:
					return node

				node = node._next
				pos += 1
			else:  # pragma: no cover
				raise LinkedListException(f"Node position not found.")
		else:
			pos = self._count - 2
			node = self._last._previous
			while node is not None:
				if pos == position:
					return node

				node = node._previous
				pos -= 1
			else:  # pragma: no cover
				raise LinkedListException(f"Node position not found.")

	def __setitem__(self, position: int, value: _NodeValue) -> None:
		"""
		Set the value of node at the given position.

		:param position: Position of the node to modify.
		:param value:    New value for the node addressed by position.
		"""
		node = self[position]
		node._value = value

	def __delitem__(self, position: int) -> Node[_NodeValue]:
		"""
		Remove a node at the given position.

		:param position: Position of the node to remove.
		:return:         Removed node.
		"""
		node = self[position]
		node.Remove()

		return node
