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
from unittest import TestCase

from pyTooling.Tree import Node

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Tree(TestCase):
	def test_SingleNode(self):
		node = Node(1)

		self.assertIs(node, node.Root)
		self.assertIsNone(node.Parent)
		self.assertTrue(node.IsRoot)
		self.assertTrue(node.IsLeaf)

	def test_Children(self):
		root = Node(1)
		children = [Node(2, parent=root), Node(3, parent=root)]

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertTrue(root.IsRoot)
		self.assertFalse(root.IsLeaf)
		self.assertTrue(root.HasChildren)

		for child in children:
			self.assertFalse(child.IsRoot)
			self.assertTrue(child.IsLeaf)
			self.assertFalse(child.HasChildren)
			self.assertListEqual([root, child], child.Path)
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])

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
			self.assertFalse(child.IsRoot)
			self.assertFalse(child.IsLeaf)
			self.assertTrue(child.HasChildren)
			self.assertListEqual([root, child], child.Path)
			self.assertListEqual([root], [ancestor for ancestor in child.GetAncestors()])

		self.assertListEqual(children, [child for child in root.GetChildren()])

		for grandChild in grandChildren:
			self.assertFalse(grandChild.IsRoot)
			self.assertTrue(grandChild.IsLeaf)
			self.assertFalse(grandChild.HasChildren)
			self.assertListEqual([root, grandChild.Parent, grandChild], grandChild.Path)
			self.assertListEqual([grandChild.Parent, root], [ancestor for ancestor in grandChild.GetAncestors()])

		for sibling in root.GetChildren():
			print(sibling)

