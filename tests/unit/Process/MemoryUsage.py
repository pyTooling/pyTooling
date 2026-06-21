# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ _ __ ___   ___ ___  ___ ___                                      #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) | '__/ _ \ / __/ _ \/ __/ __|                                     #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/| | | (_) | (_|  __/\__ \__ \                                     #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   |_|  \___/ \___\___||___/___/                                     #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Unit tests for :class:`MemoryUsage`.
"""
from unittest           import TestCase

# from pytest             import mark

from pyTooling.Process  import MemoryInfo, ProcessInformation
# from pyTooling.Platform import CurrentPlatform


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
	def test_MemoryInfo(self) -> None:
		rss = 32*1024
		vms = 64*1024
		memoryInfo = MemoryInfo(rss, vms)

		self.assertEqual(rss, memoryInfo.ResidentMemory)
		self.assertEqual(vms, memoryInfo.VirtualMemory)


class ProcessInfo(TestCase):
	# @mark.skipif(not CurrentPlatform.IsNativeWindows, reason="This test only runs on Windows.")
	def test_MemoryUsage(self) -> None:
		print()
		processInfo = ProcessInformation()

		memoryInformation = processInfo.GetMemoryUsage()

		print(memoryInformation)
