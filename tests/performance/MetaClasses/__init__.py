# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
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
"""Performance tests for MetaClasses."""
import timeit
from statistics import mean
from typing import Callable, Iterable
from unittest import TestCase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class PerformanceTest(TestCase):
	counts: Iterable[int] = (100, 1000, 10000)

	def runTests(
		self,
		funcNormal: Callable[[int], Callable[[], None]],
		funcSlotted: Callable[[int], Callable[[], None]],
		counts: Iterable[int]
	):
		print()
		print(f"        normal                                    | slotted                                   |")
		print(f"        min           avg           max           | min           avg           max           | improvemnt")
		print(f"----------------------------------------------------------------------------------------------------------")
		for count in counts:
			norm = count / 10

			resultsNormal = timeit.repeat(funcNormal(count), repeat=20, number=100)
			resultsSlotted = timeit.repeat(funcSlotted(count), repeat=20, number=100)
			print(f"{count:>5}x: {min(resultsNormal)/norm:.6f} s    {mean(resultsNormal)/norm:.6f} s    {max(resultsNormal)/norm:.6f} s    | {min(resultsSlotted)/norm:.6f} s    {mean(resultsSlotted)/norm:.6f} s    {max(resultsSlotted)/norm:.6f} s    | {(1-mean(resultsSlotted)/mean(resultsNormal))*100:.0f} %")
