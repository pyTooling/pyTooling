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
"""Unit tests for Tree."""
import timeit
from statistics import mean
from unittest import TestCase

from pyTooling.Tree import Node


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Tree(TestCase):
	def test_AddChildren(self):
		def func(count: int):
			rootNode = Node(0)

			for i in range(1, count):
				rootNode.AddChild(Node(i))

		def func10():
			func(10)

		def func100():
			func(100)

		def func1000():
			func(1000)

		def func10000():
			func(10000)

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")

	def test_SetParent(self):
		def func(count: int):
			rootNode = Node(0)

			for i in range(1, count):
				Node(i, parent=rootNode)

		def func10():
			func(10)

		def func100():
			func(100)

		def func1000():
			func(1000)

		def func10000():
			func(10000)

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")

	def test_AddLongAncestorChain(self):
		def func(count: int):
			parentNode = Node(0)
			for i in range(1, count):
				parentNode = Node(i, parent=parentNode)

		def func10():
			func(10)

		def func100():
			func(100)

		def func1000():
			func(1000)

		def func10000():
			func(10000)

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")

	def test_AddLongChildBranch(self):
		def func(count: int):
			parentNode = Node(0)
			for i in range(1, count):
				node = Node(i)
				parentNode.AddChild(node)
				parentNode = node

		def func10():
			func(10)

		def func100():
			func(100)

		def func1000():
			func(1000)

		def func10000():
			func(10000)

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")

	def test_Path(self):
		def func(count: int):
			parentNode = Node(0)
			for i in range(1, count):
				parentNode = Node(i, parent=parentNode)

			return parentNode

		def func10():
			leaf = func(10)
			self.assertEqual(10, len(leaf.Path))

		def func100():
			leaf = func(100)
			self.assertEqual(100, len(leaf.Path))

		def func1000():
			leaf = func(1000)
			self.assertEqual(1000, len(leaf.Path))

		def func10000():
			leaf = func(10000)
			self.assertEqual(10000, len(leaf.Path))

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")

	def test_GetPath(self):
		def func(count: int):
			parentNode = Node(0)
			for i in range(1, count):
				parentNode = Node(i, parent=parentNode)

			return parentNode

		def func10():
			leaf = func(10)
			self.assertEqual(10, len(list(leaf.GetPath())))

		def func100():
			leaf = func(100)
			self.assertEqual(100, len(list(leaf.GetPath())))

		def func1000():
			leaf = func(1000)
			self.assertEqual(1000, len(list(leaf.GetPath())))

		def func10000():
			leaf = func(10000)
			self.assertEqual(10000, len(list(leaf.GetPath())))

		print()
		print(f"         min          avg           max")
		results = timeit.repeat(func10, repeat=5, number=100)
		print(f"    10x: {min(results)/10:.6f} s    {mean(results)/10:.6f} s    {max(results)/10:.6f} s")
		results = timeit.repeat(func100, repeat=5, number=100)
		print(f"   100x: {min(results)/100:.6f} s    {mean(results)/100:.6f} s    {max(results)/100:.6f} s")
		results = timeit.repeat(func1000, repeat=5, number=100)
		print(f" 1,000x: {min(results)/1000:.6f} s    {mean(results)/1000:.6f} s    {max(results)/1000:.6f} s")
		results = timeit.repeat(func10000, repeat=5, number=100)
		print(f"10,000x: {min(results)/10000:.6f} s    {mean(results)/10000:.6f} s    {max(results)/10000:.6f} s")
