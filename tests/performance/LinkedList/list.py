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
"""Performance tests for list."""
from . import PerformanceTest


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Insertion(PerformanceTest):
	def test_InsertBeforeFirst(self) -> None:
		def wrapper(count: int):
			def func():
				lst = []

				for i in range(1, count):
					lst.insert(0, i)

			return func

		self.runSizedTests(wrapper, self.counts)

	def test_InsertAfterLast(self) -> None:
		def wrapper(count: int):
			def func():
				lst = []

				for i in range(1, count):
					lst.append(i)

			return func

		self.runSizedTests(wrapper, self.counts)


class Remove(PerformanceTest):
	def test_FillBuckets_RemoveList(self) -> None:
		limit = 145
		def wrapper(count: int):
			def func():
				lst =[i for i in self.randomArray[0:count]]

				index = 0
				collected = 0
				buckets = []
				buckets.append([])
				lst.sort(reverse=True)
				while True:
					removeList = []
					for pos, value in enumerate(lst):
						if collected + value > limit:
							continue

						collected += value
						buckets[index].append(value)
						removeList.append(pos)

						# if collected == limit:
						# 	break

					index += 1
					if len(lst) > len(removeList):
						collected = 0
						buckets.append([])

						for offset, pos in enumerate(removeList):
							lst.pop(pos - offset)

					else:
						break

			return func

		self.runSizedTests(wrapper, self.counts[:-1])

	def test_FillBuckets_MoveValue(self) -> None:
		limit = 145
		def wrapper(count: int):
			def func():
				lst = [i for i in self.randomArray[0:count]]

				index = 0
				collected = 0
				buckets = []
				buckets.append([])
				lst.sort(reverse=True)
				while True:
					pos = 0
					for value in lst:
						if collected + value > limit:
							lst[pos] = value
							pos += 1
							continue

						collected += value
						buckets[index].append(value)

					lst = lst[:pos]
					index += 1
					if len(lst) > 0:
						collected = 0
						buckets.append([])
					else:
						break

			return func

		self.runSizedTests(wrapper, self.counts[:-1])

	def test_FillBuckets_NewList(self) -> None:
		limit = 145
		def wrapper(count: int):
			def func():
				lst =[i for i in self.randomArray[0:count]]

				index = 0
				collected = 0
				buckets = []
				buckets.append([])
				lst.sort(reverse=True)
				while True:
					newLst = []
					for value in lst:
						if collected + value > limit:
							newLst.append(value)
							continue

						collected += value
						buckets[index].append(value)

					lst = newLst
					index += 1
					if len(lst) > 0:
						collected = 0
						buckets.append([])

					else:
						break

			return func

		self.runSizedTests(wrapper, self.counts[:-1])
