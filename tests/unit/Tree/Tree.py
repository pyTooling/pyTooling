# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
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
"""Unit tests for Tree."""
from typing import Any, Optional as Nullable
from unittest import TestCase

from pyTooling.Tree import Node

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Tree(TestCase):
	def test_SingleNode(self):
		root: Node[Nullable[Any], int, str, Any] = Node(1)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.IsLeaf)
		self.assertIs(root, root.GetNodeByID(1))

	def test_Children(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertIs(root, child.Root)
			self.assertFalse(child.IsRoot)
			self.assertTrue(child.IsLeaf)
			self.assertFalse(child.HasChildren)
			self.assertListEqual([root, child], list(child.Path))
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])
		self.assertListEqual(children, [child for child in root.GetSiblings()])

	def test_GrandChildren(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]
		grandChildren = [Node(4, parent=children[0]), Node(5, parent=children[0]), Node(6, parent=children[1]), Node(7, parent=children[1])]

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertIs(root, child.Root)
			self.assertFalse(child.IsRoot)
			self.assertFalse(child.IsLeaf)
			self.assertTrue(child.HasChildren)
			self.assertListEqual([root, child], list(child.Path))
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])

		for grandChild in grandChildren:
			self.assertIs(root, grandChild.Root)
			self.assertFalse(grandChild.IsRoot)
			self.assertTrue(grandChild.IsLeaf)
			self.assertFalse(grandChild.HasChildren)
			self.assertListEqual([root, grandChild.Parent, grandChild], list(grandChild.Path))
			self.assertListEqual([grandChild.Parent, root], [ancestor for ancestor in grandChild.GetAncestors()])

		self.assertListEqual(
			[children[0], grandChildren[0], grandChildren[1], children[1], grandChildren[2], grandChildren[3]],
			[child for child in root.GetSiblings()]
		)

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

	def test_AddChild(self):
		root = Node(1)
		child = Node(2)

		root.AddChild(child)

		self.assertIs(root, root.Root)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual([child], [child for child in root.GetChildren()])

		self.assertIs(root, child.Root)
		self.assertFalse(child.IsRoot)
		self.assertTrue(child.IsLeaf)
		self.assertFalse(child.HasChildren)
		self.assertIs(root, child.Parent)

	def test_AddChildren(self):
		root = Node(1)
		children = [Node(2), Node(3)]

		root.AddChildren(children)

		self.assertIs(root, root.Root)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual(children, [child for child in root.GetChildren()])

		for child in children:
			self.assertIs(root, child.Root)
			self.assertFalse(child.IsRoot)
			self.assertTrue(child.IsLeaf)
			self.assertFalse(child.HasChildren)
			self.assertIs(root, child.Parent)

	def test_SetParent(self):
		root = Node(1)
		child = Node(2)

		child.Parent = root

		self.assertIs(root, root.Root)
		self.assertTrue(root.IsRoot)
		self.assertTrue(root.HasChildren)
		self.assertFalse(root.IsLeaf)
		self.assertListEqual([child], [child for child in root.GetChildren()])

		self.assertIs(root, child.Root)
		self.assertFalse(child.IsRoot)
		self.assertTrue(child.IsLeaf)
		self.assertFalse(child.HasChildren)
		self.assertIs(root, child.Parent)

	def test_NodeWithValue(self):
		root = Node(1, "1")

		self.assertIs(1, root.ID)
		self.assertIs("1", root.Value)

		root.Value = "2"

		self.assertIs("2", root.Value)

	def test_NodeWithDictionary(self):
		root = Node(1)

		root["key1"] = "value1"

		self.assertIs("value1", root["key1"])

	def test_Iterate(self):
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

		self.assertListEqual([1, 2, 4, 8, 5, 9, 10, 3, 6, 7, 11], [node.ID for node in root.IteratePreOrder()])
		self.assertListEqual([8, 4, 9, 10, 5, 2, 6, 11, 7, 3, 1], [node.ID for node in root.IteratePostOrder()])
		self.assertListEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], [node.ID for node in root.InterateLevelOrder()])
