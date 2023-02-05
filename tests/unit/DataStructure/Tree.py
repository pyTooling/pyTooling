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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for pyTooling.Tree."""
from typing import Any, Optional as Nullable, List
from unittest import TestCase

from pytest import mark

from pyTooling.Tree import Node, AlreadyInTreeError, NoSiblingsError

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Construction(TestCase):
	def test_SingleNode(self):
		root: Node[Nullable[Any], int, str, Any] = Node()

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertIsNone(root.ID)
		self.assertEqual(0, root.Level)
		self.assertEqual(0, len(root))
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.IsLeaf)

	def test_NewNodeWithParent(self):
		root = Node()
		children = [Node(parent=root), Node(parent=root)]

		self.assertIs(root, root.Root)
		self.assertIsNone(root.ID)
		self.assertIsNone(root.Parent)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertIs(root, child.Root)
			self.assertIsNone(child.ID)
			self.assertEqual(1, child.Level)
			self.assertFalse(child.IsRoot)
			self.assertTrue(child.IsLeaf)
			self.assertFalse(child.HasChildren)
			self.assertListEqual([root, child], list(child.Path))
			self.assertListEqual([root, child], list(child.GetPath()))
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])
#		self.assertListEqual(children, [child for child in root.GetSiblings()])

	def test_NewNodeWithChildren(self):
		children = [Node(), Node()]
		root = Node(children=children)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.ID)
		self.assertIsNone(root.Parent)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertIs(root, child.Root)
			self.assertIsNone(child.ID)
			self.assertEqual(1, child.Level)
			self.assertFalse(child.IsRoot)
			self.assertTrue(child.IsLeaf)
			self.assertFalse(child.HasChildren)
			self.assertListEqual([root, child], list(child.Path))
			self.assertListEqual([root, child], list(child.GetPath()))
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])
		self.assertListEqual(children, [child for child in root.GetDescendants()])

	def test_GrandChildren(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]
		grandChildren = [Node(4, parent=children[0]), Node(5, parent=children[0]), Node(6, parent=children[1]), Node(7, parent=children[1])]

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertIs(root, child.Root)
			self.assertEqual(1, child.Level)
			self.assertFalse(child.IsRoot)
			self.assertFalse(child.IsLeaf)
			self.assertTrue(child.HasChildren)
			self.assertListEqual([root, child], list(child.Path))
			self.assertListEqual([root, child], list(child.GetPath()))
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])

		for grandChild in grandChildren:
			self.assertIs(root, grandChild.Root)
			self.assertEqual(2, grandChild.Level)
			self.assertFalse(grandChild.IsRoot)
			self.assertTrue(grandChild.IsLeaf)
			self.assertFalse(grandChild.HasChildren)
			self.assertListEqual([root, grandChild.Parent, grandChild], list(grandChild.Path))
			self.assertListEqual([root, grandChild.Parent, grandChild], list(grandChild.GetPath()))
			self.assertListEqual([grandChild.Parent, root], [ancestor for ancestor in grandChild.GetAncestors()])

		self.assertListEqual(
			[children[0], grandChildren[0], grandChildren[1], children[1], grandChildren[2], grandChildren[3]],
			[child for child in root.GetDescendants()]
		)

	def test_AddChild(self):
		root = Node(1)
		child = Node(2)

		root.AddChild(child)

		self.assertIs(root, root.Root)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual([child], [child for child in root.GetChildren()])

		self.assertIs(root, child.Root)
		self.assertEqual(1, child.Level)
		self.assertFalse(child.IsRoot)
		self.assertTrue(child.IsLeaf)
		self.assertFalse(child.HasChildren)
		self.assertIs(root, child.Parent)

	def test_AddChildTree(self):
		root = Node(1)
		child = Node(2)
		grandChild = Node(3, parent=child)

		root.AddChild(child)

		self.assertIs(root, root.Root)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual([child], [child for child in root.GetChildren()])

		self.assertIs(root, child.Root)
		self.assertEqual(1, child.Level)
		self.assertFalse(child.IsRoot)
		self.assertFalse(child.IsLeaf)
		self.assertTrue(child.HasChildren)
		self.assertIs(root, child.Parent)

		self.assertIs(root, grandChild.Root)
		self.assertEqual(2, grandChild.Level)
		self.assertFalse(grandChild.IsRoot)
		self.assertTrue(grandChild.IsLeaf)
		self.assertFalse(grandChild.HasChildren)
		self.assertIs(child, grandChild.Parent)

	def test_AddChildren(self):
		root = Node(1)
		children = [Node(11), Node(12)]
		grandChildren = [
			Node(111, parent=children[0]), Node(112, parent=children[0]),
			Node(121, parent=children[1]), Node(122, parent=children[1])
		]

		root.AddChildren(children)

		self.assertIs(root, root.Root)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual(children, [child for child in root.GetChildren()])

		for child in children:
			self.assertIs(root, child.Root)
			self.assertEqual(1, child.Level)
			self.assertFalse(child.IsRoot)
			self.assertFalse(child.IsLeaf)
			self.assertTrue(child.HasChildren)
			self.assertIs(root, child.Parent)

		for grandChild in grandChildren:
			self.assertIs(root, grandChild.Root)
			self.assertEqual(2, grandChild.Level)
			self.assertFalse(grandChild.IsRoot)
			self.assertTrue(grandChild.IsLeaf)
			self.assertFalse(grandChild.HasChildren)

	def test_SetParent(self):
		root = Node(1)
		child = Node(2)

		child.Parent = root

		self.assertIs(root, root.Root)
		self.assertEqual(0, root.Level)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual([child], [child for child in root.GetChildren()])

		self.assertIs(root, child.Root)
		self.assertEqual(1, child.Level)
		self.assertFalse(child.IsRoot)
		self.assertTrue(child.IsLeaf)
		self.assertFalse(child.HasChildren)
		self.assertIs(root, child.Parent)


class MergeTree(TestCase):
	def test_SetParent(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		root1 = Node(11)
		children1 = [Node(12, parent=root1), Node(13, parent=root1)]

		root2 = Node(21)
		children2 = [Node(22, parent=root2), Node(23, parent=root2)]

		root1.Parent = children[0]
		root2.Parent = children[1]

		nodes = [root1, root2] + children1 + children2
		for child in children:
			self.assertFalse(child.IsLeaf)

		for node in nodes:
			self.assertFalse(node.IsRoot)
			self.assertIs(root, node.Root)

		# check if sub trees IDs are now in main tree

	def test_AddChild(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		root1 = Node(11)
		children1 = [Node(12, parent=root1), Node(13, parent=root1)]

		root2 = Node(21)
		children2 = [Node(22, parent=root2), Node(23, parent=root2)]

		children[0].AddChild(root1)
		children[1].AddChild(root2)

		nodes = [root1, root2] + children1 + children2
		for child in children:
			self.assertFalse(child.IsLeaf)

		for node in nodes:
			self.assertFalse(node.IsRoot)
			self.assertIs(root, node.Root)

	@mark.skip(reason="Not yet implemented!")
	def test_AddChildren(self):
		pass


class SplitTree(TestCase):
	def test_SplitTreeWithoutIDs(self):
		root = Node()
		children = [Node(parent=root), Node(parent=root)]

		root1 = Node(parent=children[0])
		children1 = [Node(parent=root1), Node(parent=root1)]

		oldSize = root.Size

		root1.Parent = None

		self.assertTrue(children[0].IsLeaf)
		self.assertEqual(0, len(children[0]))

		self.assertEqual(oldSize, root.Size + root1.Size)
		self.assertEqual(len(children), len(root))
		self.assertEqual(len(children1), len(root1))

		self.assertIsNone(root1.Parent)
		self.assertTrue(root1.IsRoot)
		self.assertIs(root1, root1.Root)
		self.assertEqual(0, root1.Level)
		for node in children1:
			self.assertIs(root1, node.Root)
			self.assertEqual(1, node.Level)

	def test_SplitTreeWithIDs(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		root1 = Node(11, parent=children[0])
		children1 = [Node(12, parent=root1), Node(13, parent=root1)]

		oldSize = root.Size

		root1.Parent = None

		self.assertTrue(children[0].IsLeaf)
		self.assertEqual(0, len(children[0]))

		self.assertEqual(oldSize, root.Size + root1.Size)
		self.assertEqual(len(children), len(root))
		self.assertEqual(len(children1), len(root1))

		self.assertIsNone(root1.Parent)
		self.assertTrue(root1.IsRoot)
		self.assertIs(root1, root1.Root)
		self.assertEqual(0, root1.Level)
		for node in children1:
			self.assertIs(root1, node.Root)
			self.assertEqual(1, node.Level)

		# check if subtree's IDs are not in main tree anymore

	@mark.skip(reason="Not yet implemented!")
	def test_DeleteChild(self):
		pass


class Loops(TestCase):
	def test_SelfLoop(self):
		root = Node(1)

		with self.assertRaises(Exception):
			root.AddChild(root)

		with self.assertRaises(Exception):
			root.Parent = root

	def test_MinimalLoop(self):
		root = Node(1)
		child = Node(2, parent=root)

		with self.assertRaises(Exception):
			child.AddChild(root)

		with self.assertRaises(Exception):
			root.Parent = child

	def test_InternalLoop(self):
		root = Node(1)
		child = Node(2, parent=root)
		grandchild = Node(3, parent=child)

		with self.assertRaises(Exception):
			grandchild.AddChild(root)

		with self.assertRaises(Exception):
			grandchild.AddChild(child)

		with self.assertRaises(Exception):
			root.Parent = grandchild

		with self.assertRaises(Exception):
			child.Parent = grandchild

	def test_SideLoop(self):
		root = Node(1)
		child = Node(2, parent=root)
		grandchild = [Node(3, parent=child), Node(4, parent=child)]

		with self.assertRaises(Exception):
			grandchild[1].AddChild(grandchild[0])

		with self.assertRaises(Exception):
			grandchild[0].Parent = grandchild[1]


class Features(TestCase):
	def test_NodeWithID(self):
		root = Node(nodeID=1)

		self.assertIs(1, root.ID)
		self.assertIs(root, root.GetNodeByID(1))
		with self.assertRaises(AttributeError):
			root.ID = "2"

	def test_NodeWithValue(self):
		root = Node(value="1")

		self.assertIs("1", root.Value)

		root.Value = "2"
		self.assertIs("2", root.Value)

	def test_NodeWithDictionary(self):
		root = Node()

		# set value
		root["key1"] = "value1"

		# get value
		self.assertIs("value1", root["key1"])

		# del value
		del root["key1"]

		with self.assertRaises(KeyError):
			_ = root["key1"]

	def test_Length(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		self.assertEqual(len(children), len(root))

	def test_Size(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]
		grandChildren = [
			Node(4, parent=children[0]), Node(5, parent=children[0]),
			Node(6, parent=children[1]), Node(7, parent=children[1])
		]
		grandGrandChildren = [
			Node(8, parent=grandChildren[0]),
			Node(9, parent=grandChildren[1]), Node(10, parent=grandChildren[1]),
			Node(11, parent=grandChildren[3])
		]

		size = 1 + len(children) + len(grandChildren) + len(grandGrandChildren)
		self.assertEqual(size, root.Size)

	def test_Iterator(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		self.assertListEqual(children, [node for node in root])

	def test_Siblings(self):
		root = Node(1)
		children = [
			Node(11, parent=root),
			Node(12, parent=root),
			Node(13, parent=root),
			Node(14, parent=root),
			Node(15, parent=root)
		]

		self.assertListEqual(children[:2] + children[3:], list(children[2].Siblings))

	def test_LeftSiblings(self):
		root = Node(1)
		children = [
			Node(11, parent=root),
			Node(12, parent=root),
			Node(13, parent=root),
			Node(14, parent=root),
			Node(15, parent=root)
		]

		self.assertListEqual(children[:2], list(children[2].LeftSiblings))

	def test_RightSiblings(self):
		root = Node(1)
		children = [
			Node(11, parent=root),
			Node(12, parent=root),
			Node(13, parent=root),
			Node(14, parent=root),
			Node(15, parent=root)
		]

		self.assertListEqual(children[3:], list(children[2].RightSiblings))

	def test_Repr(self):
		node = Node()
		nodeID = Node(nodeID=2)
		nodeValue = Node(value="2")
		nodeIDValue = Node(nodeID=2, value="2")

		_ = repr(node)
		_ = repr(nodeID)
		_ = repr(nodeValue)
		_ = repr(nodeIDValue)

		root = Node()
		node = Node(parent=root)
		nodeID = Node(nodeID=31, parent=root)
		nodeValue = Node(value="32", parent=root)
		nodeIDValue = Node(nodeID=33, value="33", parent=root)

		_ = repr(node)
		_ = repr(nodeID)
		_ = repr(nodeValue)
		_ = repr(nodeIDValue)

		root = Node(1)
		node = Node(parent=root)
		nodeID = Node(nodeID=41, parent=root)
		nodeValue = Node(value="42", parent=root)
		nodeIDValue = Node(nodeID=43, value="43", parent=root)

		_ = repr(node)
		_ = repr(nodeID)
		_ = repr(nodeValue)
		_ = repr(nodeIDValue)

	def test_Str(self):
		node = Node()
		nodeID = Node(nodeID=1)
		nodeValue = Node(value="1")
		nodeIDValue = Node(nodeID=1, value="1")

		_ = str(node)
		_ = str(nodeID)
		_ = str(nodeValue)
		_ = str(nodeIDValue)


class Iteration(TestCase):
	_root: Node
	_children: List[Node]

	def setUp(self) -> None:
		root = Node(1)
		children = [
			Node(11, parent=root),
			Node(12, parent=root),
			Node(13, parent=root),
			Node(14, parent=root),
			Node(15, parent=root)
		]
		grandChildren = [
			Node(111, parent=children[0]),
			Node(112, parent=children[0]),
			Node(121, parent=children[1]),
			Node(131, parent=children[2]),
			Node(132, parent=children[2]),
			Node(133, parent=children[2]),
			Node(141, parent=children[3]),
			Node(142, parent=children[3]),
			Node(151, parent=children[4])
		]
		grandGrandChildren = [
			Node(1111, parent=grandChildren[0]),
			Node(1121, parent=grandChildren[1]),
			Node(1122, parent=grandChildren[1]),
			Node(1311, parent=grandChildren[3]),
			Node(1312, parent=grandChildren[3]),
			Node(1321, parent=grandChildren[4]),
			Node(1331, parent=grandChildren[5]),
			Node(1421, parent=grandChildren[7]),
			Node(1422, parent=grandChildren[7]),
			Node(1511, parent=grandChildren[8])
		]
		grandGrandGrandChildren = [
			Node(13211, parent=grandGrandChildren[5]),
			Node(13212, parent=grandGrandChildren[5]),
			Node(14221, parent=grandGrandChildren[8]),
			Node(14222, parent=grandGrandChildren[8])
		]

		self._root = root
		self._children = children

	def test_Siblings(self):
		self.assertListEqual([11, 12, 14, 15], [node.ID for node in self._children[2].Siblings])

	def test_LeftSiblings(self):
		self.assertListEqual([11, 12], [node.ID for node in self._children[2].LeftSiblings])

	def test_RightSiblings(self):
		self.assertListEqual([14, 15], [node.ID for node in self._children[2].RightSiblings])

	def test_GetSiblings(self):
		self.assertListEqual([11, 12, 14, 15], [node.ID for node in self._children[2].GetSiblings()])

	def test_GetLeftSiblings(self):
		self.assertListEqual([11, 12], [node.ID for node in self._children[2].GetLeftSiblings()])

	def test_GetRightSiblings(self):
		self.assertListEqual([14, 15], [node.ID for node in self._children[2].GetRightSiblings()])

	def test_GetLeftRelatives(self):
		self.assertListEqual([
			11, 111, 1111, 112, 1121, 1122,
			12, 121,
		], [node.ID for node in self._children[2].GetLeftRelatives()])

	def test_GetRightRelatives(self):
		self.assertListEqual([
			14, 141, 142, 1421, 1422, 14221, 14222,
			15, 151, 1511
		], [node.ID for node in self._children[2].GetRightRelatives()])

	def test_IteratePreOrder(self):
		self.assertListEqual([
			1,
			11, 111, 1111, 112, 1121, 1122,
			12, 121,
			13, 131, 1311, 1312, 132, 1321, 13211, 13212, 133, 1331,
			14, 141, 142, 1421, 1422, 14221, 14222,
			15, 151, 1511
		], [node.ID for node in self._root.IteratePreOrder()])

	def test_IteratePostOrder(self):
		self.assertListEqual([
			1111, 111, 1121, 1122, 112, 11,
			121, 12,
			1311, 1312, 131, 13211, 13212, 1321, 132, 1331, 133, 13,
			141, 1421, 14221, 14222, 1422, 142, 14,
			1511, 151, 15,
			1
		], [node.ID for node in self._root.IteratePostOrder()])

	def test_IterateLevelOrder(self):
		self.assertListEqual([
			1,
			11, 12, 13, 14, 15,
			111, 112, 121, 131, 132, 133, 141, 142, 151,
			1111, 1121, 1122, 1311, 1312, 1321, 1331, 1421, 1422, 1511,
			13211, 13212, 14221, 14222,
		], [node.ID for node in self._root.IterateLevelOrder()])

	def test_IterateLeafs(self):
		self.assertListEqual([
			1111, 1121, 1122, 121, 1311, 1312, 13211, 13212, 1331, 141, 1421, 14221, 14222, 1511
		], [node.ID for node in self._root.IterateLeafs()])


class Exceptions(TestCase):
	def test_NewNodeWithWrongParent(self):
		with self.assertRaises(TypeError):
			_ = Node(parent=1)

	def test_NewNodeWithDuplicateID(self):
		root = Node(1)

		with self.assertRaises(ValueError):
			_ = Node(1, parent=root)

	def test_NewNodeWithNonIterableChildren(self):
		with self.assertRaises(TypeError):
			_ = Node(children=0)

	def test_NewNodeWithWrongChildInChildren(self):
		children = [Node(), None, Node()]
		with self.assertRaises(TypeError):
			_ = Node(children=children)

	def test_SetWrongParent(self):
		root = Node()
		child = Node(parent=root)

		with self.assertRaises(TypeError):
			child.Parent = 2

	def test_AddWrongChild(self):
		root = Node()

		with self.assertRaises(TypeError):
			root.AddChild(2)

	def test_AddWrongChildInChildren(self):
		root = Node()
		children = [Node(), None, Node()]

		with self.assertRaises(TypeError):
			root.AddChildren(children)

	def test_AddExistingChildInChildren(self):
		root = Node()
		children = [Node(), Node(parent=root), Node()]

		with self.assertRaises(AlreadyInTreeError):
			root.AddChildren(children)

	def test_SetParentWithDuplicateIDs(self):
		root = Node(1)
		root1 = Node(1)

		with self.assertRaises(ValueError):
			root1.Parent = root

	def test_GetNodeByIDNone(self):
		root = Node(1)

		with self.assertRaises(ValueError):
			root.GetNodeByID(None)

	def test_GetSiblingsOfRoot(self):
		root = Node(1)

		self.assertIsNone(root.Parent)

		with self.assertRaises(NoSiblingsError):
			_ = root.Siblings

		with self.assertRaises(NoSiblingsError):
			for _ in root.GetSiblings():
				pass

	def test_GetLeftSiblingsOfRoot(self):
		root = Node(1)

		self.assertIsNone(root.Parent)

		with self.assertRaises(NoSiblingsError):
			_ = root.LeftSiblings

		with self.assertRaises(NoSiblingsError):
			for _ in root.GetLeftSiblings():
				pass

	def test_GetRightSiblingsOfRoot(self):
		root = Node(1)

		self.assertIsNone(root.Parent)

		with self.assertRaises(NoSiblingsError):
			_ = root.RightSiblings

		with self.assertRaises(NoSiblingsError):
			for _ in root.GetRightSiblings():
				pass


class Rendering(TestCase):
	_tree = (
		(0, 1), (0, 2), (0, 3),
		(1, 4), (1, 5),
		# 2
		(3, 6), (3, 7),
		(4, 8),
		(5, 10),
		# 6
		# 7
		(8, 9),
		# 9
		(10, 11), (10, 12), (10, 13),
		# 11
		# 12
		# 13
	)

	def test_Render(self):
		root = Node(nodeID=0, value="<Root 0>")

		for parentID, childID in self._tree:
			Node(nodeID=childID, value=f"<Node {childID}>", parent=root.GetNodeByID(parentID))

		rendering = root.Render()

		self.assertEqual(len(self._tree) + 2, len(rendering.split("\n")))
