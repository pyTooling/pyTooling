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
"""Benchmark tests for :func:`pyTooling.Common.mergedicts`."""
from pytest import mark

from pyTooling.Common import mergedicts


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


dictA_10 = {str(i): i for i in range(0, 10)}
dictB_10 = {str(i): i for i in range(10, 10)}
dictC_10 = {str(i): i for i in range(20, 10)}
dictD_10 = {str(i): i for i in range(30, 10)}

dictA_100 = {str(i): i for i in range(0, 100)}
dictB_100 = {str(i): i for i in range(100, 100)}
dictC_100 = {str(i): i for i in range(200, 100)}
dictD_100 = {str(i): i for i in range(300, 100)}

dictA_1000 = {str(i): i for i in range(0, 1000)}
dictB_1000 = {str(i): i for i in range(1000, 1000)}
dictC_1000 = {str(i): i for i in range(2000, 1000)}
dictD_1000 = {str(i): i for i in range(3000, 1000)}


@mark.benchmark(group="E0: Merge dictionaries with 10 items")
def test_Merge1x10(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_10)


@mark.benchmark(group="E0: Merge dictionaries with 10 items")
def test_Merge2x10(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_10, dictB_10)


@mark.benchmark(group="E0: Merge dictionaries with 10 items")
def test_Merge3x10(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_10, dictB_10, dictC_10)


@mark.benchmark(group="E0: Merge dictionaries with 10 items")
def test_Merge4x10(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_10, dictB_10, dictC_10, dictD_10)


@mark.benchmark(group="E1: Merge dictionaries with 100 items")
def test_Merge2x100(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_100, dictB_100)


@mark.benchmark(group="E1: Merge dictionaries with 100 items")
def test_Merge4x100(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_100, dictB_100, dictC_100, dictD_100)


@mark.benchmark(group="E2: Merge dictionaries with 1000 items")
def test_Merge2x1000(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_1000, dictB_1000)


@mark.benchmark(group="E2: Merge dictionaries with 1000 items")
def test_Merge4x1000(benchmark) -> None:
	@benchmark
	def func():
		z = mergedicts(dictA_1000, dictB_1000, dictC_1000, dictD_1000)
