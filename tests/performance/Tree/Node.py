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
"""Performance tests for Tree."""
import timeit
from statistics import mean
from typing import Callable, Iterable
from unittest import TestCase


from pyTooling.Tree import Node


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Tree(TestCase):
	counts: Iterable[int] = (10, 100, 1000, 10000)

	def runTests(self, func: Callable[[int], Callable[[], None]], counts: Iterable[int]):
		print()
		print(f"         min          avg           max")
		for count in counts:
			results = timeit.repeat(func(count), repeat=20, number=50)
			norm = count / 10
			print(f"{count:>5}x: {min(results)/norm:.6f} s    {mean(results)/norm:.6f} s    {max(results)/norm:.6f} s")

	def test_AddChildren(self):
		def wrapper(count: int):
			def func():
				rootNode = Node(0)

				for i in range(count):
					rootNode.AddChild(Node(i))

			return func

		self.runTests(wrapper, self.counts)

	def test_SetParent(self):
		def wrapper(count: int):
			def func():
				rootNode = Node(0)

				for i in range(count):
					Node(i, parent=rootNode)

			return func

		self.runTests(wrapper, self.counts)

	def test_AddLongAncestorChain(self):
		def wrapper(count: int):
			def func():
				parentNode = Node(0)
				for i in range(count - 1):
					parentNode = Node(i, parent=parentNode)

			return func

		self.runTests(wrapper, self.counts)

	def test_AddLongChildBranch(self):
		def wrapper(count: int):
			def func():
				parentNode = Node(0)
				for i in range(count):
					node = Node(i)
					parentNode.AddChild(node)
					parentNode = node

			return func

		self.runTests(wrapper, self.counts)

	def test_Path(self):
		def wrapper(count: int):
			def func():
				parentNode = Node(0)
				for i in range(count - 1):
					parentNode = Node(i, parent=parentNode)

				leaf = parentNode
				_ = leaf.Path

			return func

		self.runTests(wrapper, self.counts)

	def test_GetPath(self):
		def wrapper(count: int):
			def func():
				parentNode = Node(0)
				for i in range(count - 1):
					parentNode = Node(i, parent=parentNode)

				leaf = parentNode
				_ = [node for node in leaf.GetPath()]

			return func

		self.runTests(wrapper, self.counts)
