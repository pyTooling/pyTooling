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
"""Benchmark tests for pyTooling.MetaClasses.ExtendedType."""
from pytest import mark

from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class NormalNode_1:
	_data_0: int

	def __init__(self, data):
		self._data_0 = data

	def inc(self, add: int):
		self._data_0 = self._data_0 + add


class SlottedNode_1(metaclass=ExtendedType, slots=True):
	_data_0: int

	def __init__(self, data):
		self._data_0 = data

	def inc(self, add: int):
		self._data_0 = self._data_0 + add


class NormalNode_10:
	_data_0: int
	_data_1: int
	_data_2: int
	_data_3: int
	_data_4: int
	_data_5: int
	_data_6: int
	_data_7: int
	_data_8: int
	_data_9: int

	def __init__(self, data):
		self._data_0 = data
		self._data_1 = data
		self._data_2 = data
		self._data_3 = data
		self._data_4 = data
		self._data_5 = data
		self._data_6 = data
		self._data_7 = data
		self._data_8 = data
		self._data_9 = data

	def inc(self, add: int):
		self._data_1 = self._data_0 + add
		self._data_2 = self._data_1 + add
		self._data_3 = self._data_2 + add
		self._data_4 = self._data_3 + add
		self._data_5 = self._data_4 + add
		self._data_6 = self._data_5 + add
		self._data_7 = self._data_6 + add
		self._data_8 = self._data_7 + add
		self._data_9 = self._data_8 + add


class SlottedNode_10(metaclass=ExtendedType, slots=True):
	_data_0: int
	_data_1: int
	_data_2: int
	_data_3: int
	_data_4: int
	_data_5: int
	_data_6: int
	_data_7: int
	_data_8: int
	_data_9: int

	def __init__(self, data):
		self._data_0 = data
		self._data_1 = data
		self._data_2 = data
		self._data_3 = data
		self._data_4 = data
		self._data_5 = data
		self._data_6 = data
		self._data_7 = data
		self._data_8 = data
		self._data_9 = data

	def inc(self, add: int):
		self._data_1 = self._data_0 + add
		self._data_2 = self._data_1 + add
		self._data_3 = self._data_2 + add
		self._data_4 = self._data_3 + add
		self._data_5 = self._data_4 + add
		self._data_6 = self._data_5 + add
		self._data_7 = self._data_6 + add
		self._data_8 = self._data_7 + add
		self._data_9 = self._data_8 + add


@mark.benchmark(group="B0: Create Objects with 1 slot")
def test_CreateNormalObjects_1(benchmark):
	@benchmark
	def func():
		[NormalNode_1(i) for i in range(1000)]


@mark.benchmark(group="B0: Create Objects with 1 slot")
def test_CreateSlottedObjects_1(benchmark):
	@benchmark
	def func():
		[SlottedNode_1(i) for i in range(1000)]


@mark.benchmark(group="B1: Create Objects with 10 slots")
def test_CreateObjects_10(benchmark):
	@benchmark
	def func():
		[NormalNode_10(i) for i in range(1000)]


@mark.benchmark(group="B1: Create Objects with 10 slots")
def test_CreateSlottedObjects_10(benchmark):
	@benchmark
	def func():
		[SlottedNode_10(i) for i in range(1000)]


@mark.benchmark(group="B2: Accumulate a single integer slot")
def test_Accumulate_1(benchmark):
	@benchmark
	def func():
		node = NormalNode_1(0)
		for i in range(1000):
			node.inc(i)


@mark.benchmark(group="B2: Accumulate a single integer slot")
def test_SlottedAccumulate_1(benchmark):
	@benchmark
	def func():
		node = SlottedNode_1(0)
		for i in range(1000):
			node.inc(i)


@mark.benchmark(group="B3: Accumulate 10 integer slots")
def test_Accumulate_10(benchmark):
	@benchmark
	def func():
		node = NormalNode_10(0)
		for i in range(1000):
			node.inc(i)


@mark.benchmark(group="B3: Accumulate 10 integer slots")
def test_SlottedAccumulate_10(benchmark):
	@benchmark
	def func():
		node = SlottedNode_10(0)
		for i in range(1000):
			node.inc(i)
