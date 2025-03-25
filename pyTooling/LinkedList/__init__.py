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
	"""Base exception of all exceptions raised by :mod:`pyTooling.LinkedList`."""


@export
class Node(Generic[_NodeValue], metaclass=ExtendedType, slots=True):
	"""A node in an object-oriented doubly linked-list."""

	_list:     Nullable["LinkedList[_NodeValue]"]
	_next:     Nullable["Node[_NodeValue]"]
	_previous: Nullable["Node[_NodeValue]"]
	_value:    _NodeValue

	def __init__(
		self,
		value: _NodeValue,
		previous: Nullable["Node[_NodeValue]"] = None,
		next: Nullable["Node[_NodeValue]"] = None
	) -> None:
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
					self._list._end = self
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
					self._list._begin = self
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
		return self._list

	@readonly
	def Next(self) -> Nullable["Node[_NodeValue]"]:
		return self._next

	@readonly
	def Previous(self) -> Nullable["Node[_NodeValue]"]:
		return self._previous

	@property
	def Value(self) -> _NodeValue:
		return self._value

	@Value.setter
	def Value(self, value: _NodeValue) -> None:
		self._value = value

	def InsertBefore(self, node: "Node[_NodeValue]"):
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
			self._list._begin = node
		else:
			self._previous._next = node
		self._previous = node
		self._list._count += 1

	def InsertAfter(self, node: "Node[_NodeValue]"):
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
			self._list._end = node
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

	def Remove(self) -> "Node[_NodeValue]":
		if self._previous is None:
			if self._list is not None:
				self._list._begin = self._next
				self._list._count -= 1

				if self._next is None:
					self._list._end = None

				self._list = None

			if self._next is not None:
				self._next._previous = None

			self._next = None
		elif self._next is None:
			if self._list is not None:
				self._list._end = self._previous
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

	def IterateToFirst(self) -> Generator["Node[_NodeValue]", None, None]:
		node = self._previous

		while node is not None:
			yield node
			node = node._previous

	def IterateToLast(self) -> Generator["Node[_NodeValue]", None, None]:
		node = self._next

		while node is not None:
			yield node
			node = node._next

	def __repr__(self) -> str:
		return f"Node: {self._value}"


@export
class LinkedList(Generic[_NodeValue], metaclass=ExtendedType, slots=True):
	"""An object-oriented doubly linked-list."""

	_begin: Nullable[Node[_NodeValue]]
	_end:   Nullable[Node[_NodeValue]]
	_count: int

	# allow iterable to initialize the list
	def __init__(self, nodes: Nullable[Iterable[Node[_NodeValue]]] = None):
		if nodes is None:
			self._begin = None
			self._end = None
			self._count = 0
		elif not isinstance(nodes, Iterable):
			ex = TypeError(f"Parameter 'nodes' is not an iterable.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(next)}'.")
			raise ex
		else:
			if isinstance(nodes, Sized) and len(nodes) == 0:
				self._begin = None
				self._end = None
				self._count = 0
				return

			try:
				first = next(iterator := iter(nodes))
			except StopIteration:
				self._begin = None
				self._end = None
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
			self._begin = previous = node = first

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

			self._end = node
			self._count = position
			node._next = None

	@readonly
	def IsEmpty(self) -> int:
		return self._count == 0

	@readonly
	def Count(self) -> int:
		return self._count

	@readonly
	def First(self) -> Nullable[Node[_NodeValue]]:
		return self._begin

	@readonly
	def Last(self) -> Nullable[Node[_NodeValue]]:
		return self._end

	def Clear(self) -> None:
		self._begin = None
		self._end = None
		self._count = 0

	def InsertAtBegin(self, node: Node[_NodeValue]):
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
		node._next = self._begin
		if self._begin is None:
			self._end = node
		else:
			self._begin._previous = node
		self._begin = node
		self._count += 1

	def InsertAtEnd(self, node: Node[_NodeValue]):
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
		node._previous = self._end
		if self._end is None:
			self._begin = node
		else:
			node._previous._next = node
		self._end = node
		self._count += 1

	def RemoveFromBegin(self) -> Node[_NodeValue]:
		if self._begin is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._begin
		self._begin = node._next
		if self._begin is None:
			self._end = None
		else:
			self._begin._previous = None
		self._count -= 1

		node._list = None
		node._next = None
		return node

	def RemoveFromEnd(self) -> Node[_NodeValue]:
		if self._end is None:
			raise LinkedListException(f"Linked list is empty.")

		node = self._end
		self._end = node._previous
		if self._end is None:
			self._begin = None
		else:
			self._end._next = None
		self._count -= 1

		node._list = None
		node._previous = None
		return node

	def Search(self, predicate: Callable[[Node], bool], reverse: bool = False) -> Node[_NodeValue]:
		if self._begin is None:
			raise LinkedListException(f"Linked list is empty.")

		if not reverse:
			node = self._begin
			while node is not None:
				if predicate(node):
					break

				node = node._next
			else:
				raise LinkedListException(f"Node not found.")
		else:
			node = self._end
			while node is not None:
				if predicate(node):
					break

				node = node._previous
			else:
				raise LinkedListException(f"Node not found.")

		return node

	def Reverse(self) -> None:
		if self._begin is None or self._begin is self._end:
			return

		node = self._end = self._begin

		while node is not None:
			last = node
			node = last._next
			last._next = last._previous

		last._previous = node
		self._begin = last

	def Sort(self, key: Nullable[Callable[[Node[_NodeValue]], Any]] = None, reverse: bool = False) -> None:
		if (self._begin is None) or (self._begin is self._end):
			return

		if key is None:
			def key(node: Node) -> Any:
				return node._value

		sequence = [n for n in self.IterateFromFirst()]
		sequence.sort(key=key, reverse=reverse)

		first = sequence[0]

		position = 1
		first._previous = None
		self._begin = previous = node = first

		for node in sequence[1:]:
			node._previous = previous
			previous._next = node

			previous = node
			position += 1

		self._end = node
		self._count = position
		node._next = None

	def IterateFromFirst(self) -> Generator[Node[_NodeValue], None, None]:
		if self._begin is None:
			return

		node = self._begin

		while node is not None:
			yield node
			node = node._next

	def IterateFromLast(self) -> Generator[Node[_NodeValue], None, None]:
		if self._end is None:
			return

		node = self._end

		while node is not None:
			yield node
			node = node._previous

	def ToList(self) -> List[Node[_NodeValue]]:
		return [n.Value for n in self.IterateFromFirst()]

	def ToTuple(self) -> Tuple[Node[_NodeValue], ...]:
		return tuple(n.Value for n in self.IterateFromFirst())

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
		return self._count

	def __getitem__(self, position: int) -> Node[_NodeValue]:
		if position == 0:
			if self._begin is None:
				ex = ValueError("Parameter 'position' is out of range.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Linked list is empty.")
				raise ex

			return self._begin
		elif position == self._count - 1:
			return self._end
		elif position >= self._count:
			ex = ValueError("Parameter 'position' is out of range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Linked list has {self._count} elements. Requested index: {position}.")
			raise ex

		# TODO: interate from shorter end
		pos = 1
		node = self._begin._next
		while node is not None:
			if pos == position:
				return node

			node = node._next
			pos += 1
		else:  # pragma: no cover
			raise LinkedListException(f"Node position not found.")
