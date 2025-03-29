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
		self.assertIsNone(node.PreviousNode)
		self.assertIsNone(node.NextNode)

	def test_Node_Previous(self) -> None:
		previous = Node(4)
		node = Node(5, previousNode=previous)

		self.assertEqual(4, previous.Value)
		self.assertEqual(5, node.Value)
		self.assertIsNone(previous.List)
		self.assertIsNone(node.List)
		self.assertIs(previous, node.PreviousNode)
		self.assertIs(node, previous.NextNode)
		self.assertIsNone(previous.PreviousNode)
		self.assertIsNone(node.NextNode)

	def test_Node_Previous_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			_ = Node(5, previousNode=4)

	def test_Node_Next(self) -> None:
		next = Node(6)
		node = Node(5, nextNode=next)

		self.assertEqual(5, node.Value)
		self.assertEqual(6, next.Value)
		self.assertIsNone(node.List)
		self.assertIsNone(next.List)
		self.assertIs(next, node.NextNode)
		self.assertIs(node, next.PreviousNode)
		self.assertIsNone(next.NextNode)
		self.assertIsNone(node.PreviousNode)

	def test_Node_Next_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			_ = Node(5, nextNode=6)

	def test_LinkedList(self) -> None:
		linkedList = LinkedList()

		self.assertEqual(0, len(linkedList))
		self.assertEqual(0, linkedList.Count)
		self.assertIsNone(linkedList.FirstNode)
		self.assertIsNone(linkedList.LastNode)
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
		node0._linkedList = "list"
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
		node1._linkedList = "list"
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

		ll.InsertAfterLast(Node(0))

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
		ll.InsertBeforeFirst(node)

		self.assertEqual(1, ll.Count)
		self.assertIs(node, ll.FirstNode)
		self.assertIs(node, ll.LastNode)
		self.assertIs(ll, node.List)
		self.assertIsNone(node.PreviousNode)
		self.assertIsNone(node.NextNode)

	def test_InsertFirst2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertBeforeFirst(node2)
		ll.InsertBeforeFirst(node1)

		self.assertEqual(2, ll.Count)
		self.assertIs(node1, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)
		self.assertIs(ll, node1.List)
		self.assertIs(ll, node2.List)
		self.assertIsNone(node1.PreviousNode)
		self.assertIs(node1, node2.PreviousNode)
		self.assertIs(node2, node1.NextNode)
		self.assertIsNone(node2.NextNode)

	def test_InsertFirst_None(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			ll.InsertBeforeFirst(None)

	def test_InsertFirst_WrongType(self) -> None:
		ll = LinkedList()

		with self.assertRaises(TypeError):
			ll.InsertBeforeFirst("0")

	def test_InsertFirst_UsedNode(self) -> None:
		ll = LinkedList()

		node = Node(0)
		node._linkedList = "list"
		with self.assertRaises(LinkedListException):
			ll.InsertBeforeFirst(node)

	def test_InsertLast(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAfterLast(node)

		self.assertEqual(1, ll.Count)
		self.assertIs(node, ll.FirstNode)
		self.assertIs(node, ll.LastNode)
		self.assertIs(ll, node.List)
		self.assertIsNone(node.PreviousNode)
		self.assertIsNone(node.NextNode)

	def test_InsertLast2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAfterLast(node1)
		ll.InsertAfterLast(node2)

		self.assertEqual(2, ll.Count)
		self.assertIs(node1, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)
		self.assertIs(ll, node1.List)
		self.assertIs(ll, node2.List)
		self.assertIsNone(node1.PreviousNode)
		self.assertIs(node1, node2.PreviousNode)
		self.assertIs(node2, node1.NextNode)
		self.assertIsNone(node2.NextNode)

	def test_InsertLast_None(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			ll.InsertAfterLast(None)

	def test_InsertLast_WrongType(self) -> None:
		ll = LinkedList()

		with self.assertRaises(TypeError):
			ll.InsertAfterLast("0")

	def test_InsertLast_UsedNode(self) -> None:
		ll = LinkedList()

		node = Node(0)
		node._linkedList = "list"
		with self.assertRaises(LinkedListException):
			ll.InsertAfterLast(node)

	def test_InserBefore(self) -> None:
		ll = LinkedList()

		node0 = Node(0)
		node2 = Node(2)
		ll.InsertAfterLast(node0)
		ll.InsertAfterLast(node2)

		node1 = Node(1)
		node2.InsertNodeBefore(node1)

		self.assertEqual(3, ll.Count)
		self.assertIs(node0, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)
		self.assertIsNone(node0.PreviousNode)
		self.assertIs(node1, node0.NextNode)
		self.assertIs(node0, node1.PreviousNode)
		self.assertIs(node2, node1.NextNode)
		self.assertIs(node1, node2.PreviousNode)
		self.assertIsNone(node2.NextNode)

	def test_InserBefore_First(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		node0 = Node(0)
		node1.InsertNodeBefore(node0)

		self.assertEqual(2, ll.Count)
		self.assertIs(node0, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)
		self.assertIsNone(node0.PreviousNode)
		self.assertIs(node1, node0.NextNode)
		self.assertIs(node0, node1.PreviousNode)

	def test_InserBefore_None(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		with self.assertRaises(ValueError):
			node1.InsertNodeBefore(None)

	def test_InserBefore_WrongType(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		with self.assertRaises(TypeError):
			node1.InsertNodeBefore("node")

	def test_InserBefore_UsedNode(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		node0 = Node(0)
		node0._linkedList = "list"
		with self.assertRaises(LinkedListException):
			node1.InsertNodeBefore(node0)

	def test_InserAfter(self) -> None:
		ll = LinkedList()

		node0 = Node(0)
		node2 = Node(2)
		ll.InsertAfterLast(node0)
		ll.InsertAfterLast(node2)

		node1 = Node(1)
		node0.InsertNodeAfter(node1)

		self.assertEqual(3, ll.Count)
		self.assertIs(node0, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)
		self.assertIsNone(node0.PreviousNode)
		self.assertIs(node1, node0.NextNode)
		self.assertIs(node0, node1.PreviousNode)
		self.assertIs(node2, node1.NextNode)
		self.assertIs(node1, node2.PreviousNode)
		self.assertIsNone(node2.NextNode)

	def test_InserAfter_First(self) -> None:
		ll = LinkedList()

		node0 = Node(0)
		ll.InsertAfterLast(node0)

		node1 = Node(1)
		node0.InsertNodeAfter(node1)

		self.assertEqual(2, ll.Count)
		self.assertIs(node0, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)
		self.assertIsNone(node0.PreviousNode)
		self.assertIs(node1, node0.NextNode)
		self.assertIs(node0, node1.PreviousNode)

	def test_InserAfter_None(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		with self.assertRaises(ValueError):
			node1.InsertNodeAfter(None)

	def test_InserAfter_WrongType(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		with self.assertRaises(TypeError):
			node1.InsertNodeAfter("node")

	def test_InserAfter_UsedNode(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		node0 = Node(0)
		node0._linkedList = "list"
		with self.assertRaises(LinkedListException):
			node1.InsertNodeAfter(node0)


class Remove(TestCase):
	def test_RemoveFirst_EmptyList(self) -> None:
		ll = LinkedList()

		with self.assertRaises(LinkedListException):
			ll.RemoveFirst()

	def test_RemoveFirst(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAfterLast(node)

		self.assertEqual(1, ll.Count)

		n = ll.RemoveFirst()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

		self.assertIs(node, n)
		self.assertEqual(0, n.Value)
		self.assertIsNone(n.PreviousNode)
		self.assertIsNone(n.NextNode)
		self.assertIsNone(n.List)

	def test_RemoveFirst2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAfterLast(node1)
		ll.InsertAfterLast(node2)

		self.assertEqual(2, ll.Count)

		n = ll.RemoveFirst()

		self.assertEqual(1, ll.Count)
		self.assertIs(node2, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)

		self.assertIsNone(node2.PreviousNode)
		self.assertIsNone(node2.NextNode)

		self.assertIs(node1, n)
		self.assertEqual(1, n.Value)
		self.assertIsNone(n.PreviousNode)
		self.assertIsNone(n.NextNode)
		self.assertIsNone(n.List)

	def test_RemoveLast_EmptyList(self) -> None:
		ll = LinkedList()

		with self.assertRaises(LinkedListException):
			ll.RemoveLast()

	def test_RemoveLast(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertBeforeFirst(node)

		self.assertEqual(1, ll.Count)

		n = ll.RemoveLast()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

		self.assertIs(node, n)
		self.assertEqual(0, n.Value)
		self.assertIsNone(n.PreviousNode)
		self.assertIsNone(n.NextNode)
		self.assertIsNone(n.List)

	def test_RemoveLast2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertBeforeFirst(node2)
		ll.InsertBeforeFirst(node1)

		self.assertEqual(2, ll.Count)

		n = ll.RemoveLast()

		self.assertEqual(1, ll.Count)
		self.assertIs(node1, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)

		self.assertIsNone(node1.PreviousNode)
		self.assertIsNone(node1.NextNode)

		self.assertIs(node2, n)
		self.assertEqual(2, n.Value)
		self.assertIsNone(n.PreviousNode)
		self.assertIsNone(n.NextNode)
		self.assertIsNone(n.List)

	def test_NodeRemove_One(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		self.assertEqual(1, ll.Count)

		node1.Remove()
		self.assertEqual(0, ll.Count)

		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

		self.assertIsNone(node1.PreviousNode)
		self.assertIsNone(node1.NextNode)

	def test_NodeRemove_First(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertAfterLast(node1)
		ll.InsertAfterLast(node2)

		self.assertEqual(2, ll.Count)

		node1.Remove()
		self.assertEqual(1, ll.Count)

		self.assertIs(node2, ll.FirstNode)
		self.assertIs(node2, ll.LastNode)

		self.assertIsNone(node1.PreviousNode)
		self.assertIsNone(node1.NextNode)

	def test_NodeRemove_Middle(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		node3 = Node(3)
		ll.InsertAfterLast(node1)
		ll.InsertAfterLast(node2)
		ll.InsertAfterLast(node3)

		self.assertEqual(3, ll.Count)

		node2.Remove()

		self.assertEqual(1, node1.Value)
		self.assertEqual(3, node3.Value)
		self.assertIs(node1, ll.FirstNode)
		self.assertIs(node3, ll.LastNode)
		self.assertIs(ll.FirstNode, ll.LastNode.PreviousNode)
		self.assertIs(ll.LastNode, ll.FirstNode.NextNode)

		self.assertIsNone(node2.PreviousNode)
		self.assertIsNone(node2.NextNode)

	def test_NodeRemove_Last(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		node2 = Node(2)
		ll.InsertBeforeFirst(node2)
		ll.InsertBeforeFirst(node1)

		self.assertEqual(2, ll.Count)

		node2.Remove()
		self.assertEqual(1, ll.Count)

		self.assertIs(node1, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)

		self.assertIsNone(node2.PreviousNode)
		self.assertIsNone(node2.NextNode)


class MiscOperations(TestCase):
	def test_Clear_EmptyList(self) -> None:
		ll = LinkedList()

		ll.Clear()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

	def test_Clear(self) -> None:
		ll = LinkedList()
		ll.InsertBeforeFirst(Node(0))

		ll.Clear()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

	def test_Reverse_Empty(self) -> None:
		ll = LinkedList()

		ll.Reverse()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

	def test_Reverse1(self) -> None:
		ll = LinkedList()

		node = Node(0)
		ll.InsertAfterLast(node)

		ll.Reverse()

		self.assertEqual(1, ll.Count)
		self.assertIs(ll.FirstNode, ll.LastNode)
		self.assertIsNone(node.PreviousNode)
		self.assertIsNone(node.NextNode)

	def test_Reverse2(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)

		node2 = Node(2)
		ll.InsertAfterLast(node2)

		ll.Reverse()

		self.assertEqual(2, ll.Count)
		self.assertIs(node2, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)
		self.assertIsNone(node2.PreviousNode)
		self.assertIsNone(node1.NextNode)

	def test_Reverse3(self) -> None:
		ll = LinkedList()

		node1 = Node(1)
		ll.InsertAfterLast(node1)
		node2 = Node(2)
		ll.InsertAfterLast(node2)
		node3 = Node(3)
		ll.InsertAfterLast(node3)

		ll.Reverse()

		self.assertEqual(3, ll.Count)
		self.assertIs(node3, ll.FirstNode)
		self.assertIs(node1, ll.LastNode)
		self.assertIsNone(node3.PreviousNode)
		self.assertIsNone(node1.NextNode)

	def test_Sort_Empty(self) -> None:
		ll = LinkedList()

		ll.Sort()

		self.assertEqual(0, ll.Count)
		self.assertIsNone(ll.FirstNode)
		self.assertIsNone(ll.LastNode)

	def test_Sort_Single(self) -> None:
		ll = LinkedList()
		node0 = Node(0)
		ll.InsertAfterLast(node0)

		ll.Sort()

		self.assertEqual(1, ll.Count)
		self.assertIs(node0, ll.FirstNode)
		self.assertIs(node0, ll.LastNode)
		self.assertIsNone(node0.PreviousNode)
		self.assertIsNone(node0.NextNode)

	def test_Sort(self) -> None:
		sequence = [7, 6, 4, 8, 2, 5, 3, 1, 9]
		ll = LinkedList()

		for i in sequence:
			ll.InsertAfterLast(Node(i))

		ll.Sort()

		self.assertListEqual([i for i in range(1, len(sequence) + 1)], ll.ToList())

	def test_Sort_Reverse(self) -> None:
		sequence = [7, 6, 4, 8, 2, 5, 3, 1, 9]
		ll = LinkedList()

		for i in sequence:
			ll.InsertAfterLast(Node(i))

		ll.Sort(reverse=True)

		self.assertListEqual([i for i in range(len(sequence), 0, -1)], ll.ToList())

	def test_Sort_Key(self) -> None:
		sequence = [7, 6, 4, 8, 2, 5, 3, 1, 9]
		ll = LinkedList()

		class Inner:
			_value: int

			def __init__(self, value: int):
				self._value = value

		for i in sequence:
			ll.InsertAfterLast(Node(Inner(i)))

		ll.Sort(key=lambda node: node._value._value)

		self.assertListEqual([i for i in range(1, len(sequence) + 1)], [n._value for n in ll.ToList()])


class GetNode(TestCase):
	def test_GetFirst(self) -> None:
		ll = LinkedList()

		for i in range(6):
			ll.InsertAfterLast(Node(i))

		first = ll.GetNodeByIndex(0)

		self.assertEqual(0, first.Value)
		self.assertIs(ll.FirstNode, first)
		self.assertIsNone(first.PreviousNode)

	def test_GetSecond(self) -> None:
		ll = LinkedList()

		for i in range(6):
			ll.InsertAfterLast(Node(i))

		second = ll.GetNodeByIndex(1)

		self.assertEqual(1, second.Value)
		self.assertIs(ll.FirstNode, second.PreviousNode)
		self.assertIs(ll.FirstNode.NextNode, second)

	def test_GetThird(self) -> None:
		ll = LinkedList()

		for i in range(6):
			ll.InsertAfterLast(Node(i))

		third = ll.GetNodeByIndex(2)

		self.assertEqual(2, third.Value)

	def test_GetLast(self) -> None:
		ll = LinkedList()

		for i in range(6):
			ll.InsertAfterLast(Node(i))

		last = ll.GetNodeByIndex(5)

		self.assertEqual(5, last.Value)
		self.assertIs(ll.LastNode, last)
		self.assertIsNone(last.NextNode)

	def test_Get_Empty(self) -> None:
		ll = LinkedList()

		with self.assertRaises(ValueError):
			_ = ll.GetNodeByIndex(0)

	def test_Get_OutOfRange(self) -> None:
		ll = LinkedList()
		ll.InsertAfterLast(Node(0))
		ll.InsertAfterLast(Node(1))

		with self.assertRaises(ValueError):
			_ = ll.GetNodeByIndex(2)


class Search(TestCase):
	def test_Search_Empty(self) -> None:
		ll = LinkedList()

		with self.assertRaises(LinkedListException):
			ll.Search(lambda n: n.Value == 4)

	def test_Search_NotFound(self) -> None:
		ll = LinkedList()

		for i in range(1, 6):
			ll.InsertAfterLast(Node(i))

		with self.assertRaises(LinkedListException):
			ll.Search(lambda n: n.Value == 10)

	def test_Search_NotFound_Reverse(self) -> None:
		ll = LinkedList()

		for i in range(1, 6):
			ll.InsertAfterLast(Node(i))

		with self.assertRaises(LinkedListException):
			ll.Search(lambda n: n.Value == 10, reverse=True)

	def test_Search(self) -> None:
		ll = LinkedList()

		for i in range(1, 6):
			ll.InsertAfterLast(Node(i))

		node = ll.Search(lambda n: n.Value % 2 == 0)

		self.assertEqual(2, node.Value)

	def test_Search_Reverse(self) -> None:
		ll = LinkedList()

		for i in range(1, 6):
			ll.InsertAfterLast(Node(i))

		node = ll.Search(lambda n: n.Value % 2 == 0, reverse=True)

		self.assertEqual(4, node.Value)


class Iterate(TestCase):
	def test_IterateFromFirst_Empty(self) -> None:
		ll = LinkedList()

		with self.assertRaises(StopIteration):
			iterator = iter(ll.IterateFromFirst())
			_ = next(iterator)

	def test_IterateFromFirst(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		self.assertListEqual(sequence, [n for n in ll.IterateFromFirst()])

	def test_IterateFromLast_Empty(self) -> None:
		ll = LinkedList()

		with self.assertRaises(StopIteration):
			iterator = iter(ll.IterateFromLast())
			_ = next(iterator)

	def test_IterateFromLast(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		sequence.reverse()
		self.assertListEqual(sequence, [n for n in ll.IterateFromLast()])

	def test_IterateToFirst_First(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = 0
		actual = [n for n in sequence[index].IterateToFirst()]
		self.assertEqual(0, len(actual))

	def test_IterateToFirst(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = 3
		actual = [n for n in sequence[index].IterateToFirst()]
		self.assertEqual(index, len(actual))

		expected = sequence[0:index]
		expected.reverse()
		self.assertListEqual(expected, actual)

	def test_IterateToFirst_Self(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = 3
		actual = [n for n in sequence[index].IterateToFirst(includeSelf=True)]
		self.assertEqual(index + 1, len(actual))

		expected = sequence[0:index + 1]
		expected.reverse()
		self.assertListEqual(expected, actual)

	def test_IterateToLast_Last(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = length - 1
		actual = [n for n in sequence[index].IterateToLast()]
		self.assertEqual(0, len(actual))

	def test_IterateToLast(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = 1
		actual = [n for n in sequence[index].IterateToLast()]
		self.assertEqual(length - index - 1, len(actual))

		expected = sequence[index + 1:length - index + 1]
		self.assertListEqual(expected, actual)

	def test_IterateToLast_Self(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		index = 1
		actual = [n for n in sequence[index].IterateToLast(includeSelf=True)]
		self.assertEqual(length - index, len(actual))

		expected = sequence[index:length - index + 1]
		self.assertListEqual(expected, actual)

	def test_IterateFromFirst_Remove(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		for i, node in enumerate(ll.IterateFromFirst()):
			value = node.Remove()

			self.assertIsNone(node._linkedList)
			self.assertIsNone(node._previousNode)
			self.assertIsNone(node._nextNode)
			self.assertEqual(i, value)

		self.assertEqual(0, ll.Count)

	def test_IterateFromLast_Remove(self) -> None:
		ll = LinkedList()

		length = 5
		sequence = []
		for i in range(length):
			node = Node(i)
			sequence.append(node)
			ll.InsertAfterLast(node)

		self.assertEqual(length, ll.Count)

		for i, node in enumerate(ll.IterateFromLast(), start=1):
			value = node.Remove()

			self.assertIsNone(node._linkedList)
			self.assertIsNone(node._previousNode)
			self.assertIsNone(node._nextNode)
			self.assertEqual(length - i, value)

		self.assertEqual(0, ll.Count)

	def test_IterateZigZag(self) -> None:
		print()

		ll = LinkedList()

		limit = 55
		sequence = [15, 16, 17, 9, 3, 5, 20, 8, 14, 12, 7, 1, 16, 3, 11, 16, 5, 8, 2, 12, 11, 9, 12, 7, 4, 0, 11, 17, 3, 13, 7, 11, 20, 0, 3, 17, 10, 10, 13, 3, 9, 6, 3, 0, 13, 18, 7, 15, 11, 17]
		for i in sequence:
			ll.InsertAfterLast(Node(i))

		index = 0
		collected = 0
		buckets = []
		buckets.append([])
		ll.Sort(reverse=True)
		while not ll.IsEmpty:
			for node in ll.IterateFromFirst():
				if collected + node.Value > limit:
					continue

				collected += node.Value
				buckets[index].append(node.Value)
				node.Remove()

			index += 1
			collected = 0
			buckets.append([])

		for i, bucket in enumerate(buckets):
			print(f"{i:2}: {len(bucket)} = {sum(bucket)}")


class Conversion(TestCase):
	def test_ToTuple_Empty(self) -> None:
		ll = LinkedList()

		t = ll.ToTuple()

		self.assertIsInstance(t, tuple)
		self.assertEqual(0, len(t))
		self.assertTupleEqual(tuple(), t)

	def test_ToTuple(self) -> None:
		ll = LinkedList()

		sequence = []
		for i in range(5):
			node = Node(i)
			sequence.append(i)
			ll.InsertAfterLast(node)

		t = ll.ToTuple()

		self.assertIsInstance(t, tuple)
		self.assertEqual(len(sequence), len(t))
		self.assertTupleEqual(tuple(sequence), t)

	def test_ToTuple_Reversed(self) -> None:
		ll = LinkedList()

		sequence = []
		for i in range(5):
			node = Node(i)
			sequence.append(i)
			ll.InsertAfterLast(node)

		t = ll.ToTuple(reverse=True)

		sequence.reverse()

		self.assertIsInstance(t, tuple)
		self.assertEqual(len(sequence), len(t))
		self.assertTupleEqual(tuple(sequence), t)

	def test_ToList_Empty(self) -> None:
		ll = LinkedList()

		l = ll.ToList()

		self.assertIsInstance(l, list)
		self.assertEqual(0, len(l))
		self.assertListEqual([], l)

	def test_ToList(self) -> None:
		ll = LinkedList()

		sequence = []
		for i in range(5):
			node = Node(i)
			sequence.append(i)
			ll.InsertAfterLast(node)

		l = ll.ToList()

		self.assertIsInstance(l, list)
		self.assertEqual(len(sequence), len(l))
		self.assertListEqual(sequence, l)

	def test_ToList_Reversed(self) -> None:
		ll = LinkedList()

		sequence = []
		for i in range(5):
			node = Node(i)
			sequence.append(i)
			ll.InsertAfterLast(node)

		l = ll.ToList(reverse=True)

		sequence.reverse()

		self.assertIsInstance(l, list)
		self.assertEqual(len(sequence), len(l))
		self.assertListEqual(sequence, l)
