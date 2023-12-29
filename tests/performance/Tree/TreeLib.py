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
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Performance tests for treelib."""
from treelib import Tree as treelib_Tree

from . import PerformanceTest


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Tree(PerformanceTest):
	def test_AddChildren(self) -> None:
		def wrapper(count: int):
			def func():
				tree = treelib_Tree()
				rootNode = tree.create_node("root", identifier=0, data=0)

				for i in range(1, count):
					tree.create_node("child", parent=rootNode, data=i)

			return func

		self.runTests(wrapper, self.counts)

	def test_SetParent(self) -> None:
		def wrapper(count: int):
			def func():
				tree = treelib_Tree()
				rootNode = tree.create_node(identifier=0)

				for i in range(1, count):
					tree.create_node(identifier=i, parent=0)

			return func

		self.runTests(wrapper, self.counts)

	def test_AddFlatTree(self) -> None:
		def run(count: int):
			def func():
				tree = treelib_Tree()
				rootNode = tree.create_node(identifier=0)

				for i in range(1, 10):
					newTree = treelib_Tree()
					parentNode = newTree.create_node(identifier=count * i)
					for j in range(1, count):
						newTree.create_node(identifier=count * i + j, parent=parentNode)

					tree.paste(0, newTree)

			return func

		self.runTests(run, self.counts[:-1])
