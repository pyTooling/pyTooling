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
"""Performance tests for pyTooling.Tree."""
import timeit
from statistics import median, mean
from typing import Callable, Iterable
from unittest import TestCase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class PerformanceTest(TestCase):
	counts: Iterable[int] = (10, 100, 1000, 10000)

	@staticmethod
	def minMaxSumMean(array):
		minimum = 1.0e9
		maximum = 0.0
		sum = 0.0
		for value in array:
			minimum = value if value < minimum else minimum
			maximum = value if value > maximum else maximum
			sum += value

		return minimum, maximum, sum, sum / len(array)

	def runTests(self, func: Callable[[int], Callable[[], None]], counts: Iterable[int]):
		print()
		print(f"         min           mean          median        max")
		for count in counts:
			results = timeit.repeat(func(count), repeat=20, number=50)
			norm = count / 10
			minimum, maximum, _, mean = self.minMaxSumMean(results)
			print(f"{count:>5}x: {minimum/norm:.6f} s    {mean/norm:.6f} s    {median(results)/norm:.6f} s    {maximum/norm:.6f} s")
