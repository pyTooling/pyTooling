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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Performance tests for pyTooling.LinkedList."""

from pyTooling.LinkedList import LinkedList as pt_LinkedList, Node as pt_Node
from . import PerformanceTest


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Insertion(PerformanceTest):
	def test_InsertBeforeFirst(self) -> None:
		def wrapper(count: int):
			def func():
				ll = pt_LinkedList()

				for i in range(1, count):
					ll.InsertBeforeFirst(pt_Node(i))

			return func

		self.runSizedTests(wrapper, self.counts)

	def test_InsertAfterLast(self) -> None:
		def wrapper(count: int):
			def func():
				ll = pt_LinkedList()

				for i in range(1, count):
					ll.InsertAfterLast(pt_Node(i))

			return func

		self.runSizedTests(wrapper, self.counts)


class Remove(PerformanceTest):
	def test_FillBuckets(self) -> None:
		limit = 145
		def wrapper(count: int):
			def func():
				ll = pt_LinkedList(pt_Node(i) for i in self.randomArray[0:count])

				index = 0
				collected = 0
				buckets = []
				buckets.append([])
				ll.Sort(reverse=True)
				while True:
					for node in ll.IterateFromFirst():
						if collected + node.Value > limit:
							continue

						collected += node.Value
						buckets[index].append(node.Value)
						node.Remove()

						if collected == limit:
							break

					index += 1
					if not ll.IsEmpty:
						collected = 0
						buckets.append([])
					else:
						break

			return func

		self.runSizedTests(wrapper, self.counts[:-1])
