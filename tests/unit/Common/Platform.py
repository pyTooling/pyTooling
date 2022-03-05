# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
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
"""Unit tests for TBD."""
from os       import getenv as os_getenv
from pytest   import mark
from unittest import TestCase

from pyTooling.Common import Platform


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class AnyPlatform(TestCase):
	expected = os_getenv("EXPECTED", default="Windows (x86-64)")

	@mark.skipif(os_getenv("EXPECTED", "skip") == "skip", reason="Skipped when environment variable 'EXPECTED' isn't set.")
	def test_PlatformString(self) -> None:
		platform = Platform()

		self.assertEqual(self.expected, str(platform))

	@mark.skipif("Linux (x86-64)" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_NativeLinux(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsNativePlatform)
		self.assertTrue(platform.IsNativeLinux)

	@mark.skipif("MacOS (x86-64)" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_NativeMacOS(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsNativePlatform)
		self.assertTrue(platform.IsNativeMacOS)

	@mark.skipif("Windows (x86-64)" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_NativeWindows(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsNativePlatform)
		self.assertTrue(platform.IsNativeWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - MSYS" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_MSYS2(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsMSYSOnWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - MinGW32" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_MinGW32(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsMinGW32OnWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - MinGW64" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_MinGW64(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsMinGW64OnWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - UCRT64" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_UCRT64(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsUCRT64OnWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - Clang32" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_Clang32(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsClang32OnWindows)

	@mark.skipif("Windows+MSYS2 (x86-64) - Clang64" != os_getenv("EXPECTED", "skip"), reason="Skipped when environment variable 'EXPECTED' doesn't match.")
	def test_Clang64(self) -> None:
		platform = Platform()

		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsClang64OnWindows)
