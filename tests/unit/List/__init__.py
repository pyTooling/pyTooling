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
"""Unit tests for pyTooling.LinkedList."""

from unittest import TestCase

from pyTooling.LinkedList import Node, LinkedList, LinkedListException


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_Node(self) -> None:
		node = Node(5)

		self.assertEqual(5, node.Value)
		self.assertIsNone(node.List)
		self.assertIsNone(node.Previous)
		self.assertIsNone(node.Next)

	def test_Node_Previous(self) -> None:
		previous = Node(4)
		node = Node(5, previous=previous)

		self.assertEqual(4, previous.Value)
		self.assertEqual(5, node.Value)
		self.assertIsNone(previous.List)
		self.assertIsNone(node.List)
		self.assertIs(previous, node.Previous)
		self.assertIs(node, previous.Next)
		self.assertIsNone(previous.Previous)
		self.assertIsNone(node.Next)

	def test_Node_Previous_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			_ = Node(5, previous=4)

	def test_Node_Next(self) -> None:
		next = Node(6)
		node = Node(5, next=next)

		self.assertEqual(5, node.Value)
		self.assertEqual(6, next.Value)
		self.assertIsNone(node.List)
		self.assertIsNone(next.List)
		self.assertIs(next, node.Next)
		self.assertIs(node, next.Previous)
		self.assertIsNone(next.Next)
		self.assertIsNone(node.Previous)

	def test_Node_Next_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			_ = Node(5, next=6)

	def test_LinkedList(self) -> None:
		linkedList = LinkedList()

		self.assertEqual(0, len(linkedList))
		self.assertEqual(0, linkedList.Count)
		self.assertIsNone(linkedList.First)
		self.assertIsNone(linkedList.Last)
		self.assertTrue(linkedList.IsEmpty)

	def test_LinkedList_EmptyTuple(self) -> None:
		linkedList = LinkedList(tuple())

		self.assertEqual(0, linkedList.Count)

	def test_LinkedList_EmptyGenerator(self) -> None:
		nodes = tuple()
		linkedList = LinkedList(n for n in nodes)

		self.assertEqual(0, linkedList.Count)

	def test_LinkedList_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			_ = LinkedList(42)

	def test_LinkedList_Tuple1(self) -> None:
		nodes = (Node(0), )
		linkedList = LinkedList(nodes)

		self.assertEqual(1, linkedList.Count)

	def test_LinkedList_Tuple1_WrongType(self) -> None:
		nodes = (0, )
		with self.assertRaises(TypeError):
			_ = LinkedList(nodes)

	def test_LinkedList_Tuple1_UsedNode(self) -> None:
		node0 = Node(0)
		node0._list = "list"
		nodes = (node0, )

		with self.assertRaises(LinkedListException):
			_ = LinkedList(nodes)

	def test_LinkedList_Tuple2(self) -> None:
		nodes = (Node(0), Node(1))
		linkedList = LinkedList(nodes)

		self.assertEqual(2, linkedList.Count)

	def test_LinkedList_Tuple2_WrongType(self) -> None:
		nodes = (Node(0), 1)
		with self.assertRaises(TypeError):
			_ = LinkedList(nodes)

	def test_LinkedList_Tuple2_UsedNode(self) -> None:
		node0 = Node(0)
		node1 = Node(1)
		node1._list = "list"
		nodes = (node0, node1)

		with self.assertRaises(LinkedListException):
			_ = LinkedList(nodes)

	def test_LinkedList_Tuple3(self) -> None:
		nodes = (Node(0), Node(1), Node(2))
		linkedList = LinkedList(nodes)

		self.assertEqual(3, linkedList.Count)


class Properties(TestCase):
	def test_Count(self) -> None:
		ll = LinkedList()

		self.assertEqual(0, ll.Count)
		self.assertEqual(0, len(ll))

		ll.InsertAtEnd(Node(0))

		self.assertEqual(1, ll.Count)
		self.assertEqual(1, len(ll))

	def test_Value(self) -> None:
		node = Node(5)

		self.assertEqual(5, node.Value)

		node.Value = "5"
		self.assertEqual("5", node.Value)


class Insert(TestCase):
	def test_InsertFirst(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAtBegin(node)

		self.assertEqual(1, ll.Count)
		self.assertIs(node, ll.First)
		self.assertIs(node, ll.Last)
		self.assertIs(ll, node.List)
		self.assertIsNone(node.Previous)
		self.assertIsNone(node.Next)

	def test_InsertFirst2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtBegin(node2)
		ll.InsertAtBegin(node1)

		self.assertEqual(2, ll.Count)
		self.assertIs(node1, ll.First)
		self.assertIs(node2, ll.Last)
		self.assertIs(ll, node1.List)
		self.assertIs(ll, node2.List)
		self.assertIsNone(node1.Previous)
		self.assertIs(node1, node2.Previous)
		self.assertIs(node2, node1.Next)
		self.assertIsNone(node2.Next)

	def test_InsertFirst_None(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			ll.InsertAtBegin(None)

	def test_InsertFirst_WrongType(self) -> None:
		ll = LinkedList()

		with self.assertRaises(TypeError):
			ll.InsertAtBegin("0")

	def test_InsertFirst_UsedNode(self) -> None:
		ll = LinkedList()

		node = Node(0)
		node._list = "list"
		with self.assertRaises(LinkedListException):
			ll.InsertAtBegin(node)

	def test_InsertLast(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAtEnd(node)

		self.assertEqual(1, ll.Count)
		self.assertIs(node, ll.First)
		self.assertIs(node, ll.Last)
		self.assertIs(ll, node.List)
		self.assertIsNone(node.Previous)
		self.assertIsNone(node.Next)

	def test_InsertLast2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtEnd(node1)
		ll.InsertAtEnd(node2)

		self.assertEqual(2, ll.Count)
		self.assertIs(node1, ll.First)
		self.assertIs(node2, ll.Last)
		self.assertIs(ll, node1.List)
		self.assertIs(ll, node2.List)
		self.assertIsNone(node1.Previous)
		self.assertIs(node1, node2.Previous)
		self.assertIs(node2, node1.Next)
		self.assertIsNone(node2.Next)

	def test_InsertLast_None(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			ll.InsertAtEnd(None)

	def test_InsertLast_WrongType(self) -> None:
		ll = LinkedList()

		with self.assertRaises(TypeError):
			ll.InsertAtEnd("0")

	def test_InsertLast_UsedNode(self) -> None:
		ll = LinkedList()

		node = Node(0)
		node._list = "list"
		with self.assertRaises(LinkedListException):
			ll.InsertAtEnd(node)


class Remove(TestCase):
	def test_RemoveFirst_EmptyList(self) -> None:
		ll = LinkedList()

		with self.assertRaises(LinkedListException):
			ll.RemoveFromBegin()

	def test_RemoveFirst(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAtEnd(node)

		self.assertEqual(1, ll.Count)

		n = ll.RemoveFromBegin()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.First)
		self.assertIsNone(ll.Last)

		self.assertIs(node, n)
		self.assertEqual(0, n.Value)
		self.assertIsNone(n.Previous)
		self.assertIsNone(n.Next)
		self.assertIsNone(n.List)

	def test_RemoveFirst2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtEnd(node1)
		ll.InsertAtEnd(node2)

		self.assertEqual(2, ll.Count)

		n = ll.RemoveFromBegin()

		self.assertEqual(1, ll.Count)
		self.assertIs(node2, ll.First)
		self.assertIs(node2, ll.Last)

		self.assertIsNone(node2.Previous)
		self.assertIsNone(node2.Next)

		self.assertIs(node1, n)
		self.assertEqual(1, n.Value)
		self.assertIsNone(n.Previous)
		self.assertIsNone(n.Next)
		self.assertIsNone(n.List)

	def test_RemoveLast_EmptyList(self) -> None:
		ll = LinkedList()

		with self.assertRaises(LinkedListException):
			ll.RemoveFromEnd()

	def test_RemoveLast(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAtBegin(node)

		self.assertEqual(1, ll.Count)

		n = ll.RemoveFromEnd()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.First)
		self.assertIsNone(ll.Last)

		self.assertIs(node, n)
		self.assertEqual(0, n.Value)
		self.assertIsNone(n.Previous)
		self.assertIsNone(n.Next)
		self.assertIsNone(n.List)

	def test_RemoveLast2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtBegin(node2)
		ll.InsertAtBegin(node1)

		self.assertEqual(2, ll.Count)

		n = ll.RemoveFromEnd()

		self.assertEqual(1, ll.Count)
		self.assertIs(node1, ll.First)
		self.assertIs(node1, ll.Last)

		self.assertIsNone(node1.Previous)
		self.assertIsNone(node1.Next)

		self.assertIs(node2, n)
		self.assertEqual(2, n.Value)
		self.assertIsNone(n.Previous)
		self.assertIsNone(n.Next)
		self.assertIsNone(n.List)

	def test_NodeRemove_One(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAtEnd(node1)

		self.assertEqual(1, ll.Count)

		node1.Remove()
		self.assertEqual(0, ll.Count)

		self.assertIsNone(ll.First)
		self.assertIsNone(ll.Last)

		self.assertIsNone(node1.Previous)
		self.assertIsNone(node1.Next)

	def test_NodeRemove_First(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtEnd(node1)
		ll.InsertAtEnd(node2)

		self.assertEqual(2, ll.Count)

		node1.Remove()
		self.assertEqual(1, ll.Count)

		self.assertIs(node2, ll.First)
		self.assertIs(node2, ll.Last)

		self.assertIsNone(node1.Previous)
		self.assertIsNone(node1.Next)

	def test_NodeRemove_Middle(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		node3 = Node(3)
		ll.InsertAtEnd(node1)
		ll.InsertAtEnd(node2)
		ll.InsertAtEnd(node3)

		self.assertEqual(3, ll.Count)

		node2.Remove()

		self.assertEqual(1, node1.Value)
		self.assertEqual(3, node3.Value)
		self.assertIs(node1, ll.First)
		self.assertIs(node3, ll.Last)
		self.assertIs(ll.First, ll.Last.Previous)
		self.assertIs(ll.Last, ll.First.Next)

		self.assertIsNone(node2.Previous)
		self.assertIsNone(node2.Next)

	def test_NodeRemove_Last(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAtBegin(node2)
		ll.InsertAtBegin(node1)

		self.assertEqual(2, ll.Count)

		node2.Remove()
		self.assertEqual(1, ll.Count)

		self.assertIs(node1, ll.First)
		self.assertIs(node1, ll.Last)

		self.assertIsNone(node2.Previous)
		self.assertIsNone(node2.Next)


class Clear(TestCase):
	def test_Clear_EmptyList(self) -> None:
		ll = LinkedList()

		ll.Clear()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.First)
		self.assertIsNone(ll.Last)

	def test_Clear(self) -> None:
		ll = LinkedList()
		ll.InsertAtBegin(Node(0))

		ll.Clear()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.First)
		self.assertIsNone(ll.Last)


class GetItem(TestCase):
	def test_GetFirst(self) -> None:
		ll = LinkedList()
		ll.InsertAtEnd(Node(0))
		ll.InsertAtEnd(Node(1))
		ll.InsertAtEnd(Node(2))
		ll.InsertAtEnd(Node(3))
		ll.InsertAtEnd(Node(4))
		ll.InsertAtEnd(Node(5))

		self.assertEqual(6, ll.Count)

		first = ll[0]

		self.assertEqual(0, first.Value)
		self.assertIs(ll.First, first)
		self.assertIsNone(first.Previous)

	def test_GetSecond(self) -> None:
		ll = LinkedList()
		ll.InsertAtEnd(Node(0))
		ll.InsertAtEnd(Node(1))
		ll.InsertAtEnd(Node(2))
		ll.InsertAtEnd(Node(3))
		ll.InsertAtEnd(Node(4))
		ll.InsertAtEnd(Node(5))

		self.assertEqual(6, ll.Count)

		second = ll[1]

		self.assertEqual(1, second.Value)
		self.assertIs(ll.First, second.Previous)
		self.assertIs(ll.First.Next, second)

	def test_GetThird(self) -> None:
		ll = LinkedList()
		ll.InsertAtEnd(Node(0))
		ll.InsertAtEnd(Node(1))
		ll.InsertAtEnd(Node(2))
		ll.InsertAtEnd(Node(3))
		ll.InsertAtEnd(Node(4))
		ll.InsertAtEnd(Node(5))

		self.assertEqual(6, ll.Count)

		third = ll[2]

		self.assertEqual(2, third.Value)

	def test_GetLast(self) -> None:
		ll = LinkedList()
		ll.InsertAtEnd(Node(0))
		ll.InsertAtEnd(Node(1))
		ll.InsertAtEnd(Node(2))
		ll.InsertAtEnd(Node(3))
		ll.InsertAtEnd(Node(4))
		ll.InsertAtEnd(Node(5))

		self.assertEqual(6, ll.Count)

		last = ll[5]

		self.assertEqual(5, last.Value)
		self.assertIs(ll.Last, last)
		self.assertIsNone(last.Next)

	def test_Get_Empty(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			_ = ll[0]

	def test_Get_OutOfRange(self) -> None:
		ll = LinkedList()
		ll.InsertAtEnd(Node(0))
		ll.InsertAtEnd(Node(1))

		with self.assertRaises(ValueError):
			_ = ll[2]
