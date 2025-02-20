# ==================================================================================================================== #
#             _____           _ _               ____  _       _    __                                                  #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \| | __ _| |_ / _| ___  _ __ _ __ ___                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) | |/ _` | __| |_ / _ \| '__| '_ ` _ \                             #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/| | (_| | |_|  _| (_) | |  | | | | | |                            #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   |_|\__,_|\__|_|  \___/|_|  |_| |_| |_|                            #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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

from pyTooling.Platform import Platforms, Platform, CurrentPlatform


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class AnyPlatform(TestCase):
	expected = os_getenv("ENVIRONMENT_NAME", default="Windows (x86-64)")

	@mark.skipif(os_getenv("ENVIRONMENT_NAME", "skip") == "skip", reason="Skipped, if environment variable 'ENVIRONMENT_NAME' isn't set.")
	def test_PlatformString(self) -> None:
		platform = CurrentPlatform

		self.assertEqual(self.expected, str(platform))

	@mark.skipif("Linux (x86-64)" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_NativeLinux', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_NativeLinux(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Linux), repr(platform))
		self.assertTrue(platform.IsNativePlatform)
		self.assertFalse(platform.IsNativeWindows)
		self.assertTrue(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertFalse(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("", platform.ExecutableExtension)
		self.assertEqual("a", platform.StaticLibraryExtension)
		self.assertEqual("so", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("macOS (x86-64)" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_NativeMacOS_Intel', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_NativeMacOS_Intel(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.MacOS_Intel), repr(platform))
		self.assertTrue(platform.IsNativePlatform)
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertTrue(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertFalse(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("", platform.ExecutableExtension)
		self.assertEqual("a", platform.StaticLibraryExtension)
		self.assertEqual("dylib", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("macOS (aarch64)" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_NativeMacOS_ARM', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_NativeMacOS_ARM(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.MacOS_ARM), repr(platform))
		self.assertTrue(platform.IsNativePlatform)
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertTrue(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertFalse(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("", platform.ExecutableExtension)
		self.assertEqual("a", platform.StaticLibraryExtension)
		self.assertEqual("dylib", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows (x86-64)" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_NativeWindows', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_NativeWindows(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows), repr(platform))
		self.assertTrue(platform.IsNativePlatform)
		self.assertTrue(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertFalse(platform.IsPOSIX)
		self.assertEqual("\\", platform.PathSeperator)
		self.assertEqual(";", platform.ValueSeperator)
		self.assertFalse(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - MSYS" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_MSYS', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_MSYS(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_MSYS), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertTrue(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - MinGW32" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_MinGW32', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_MinGW32(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_MinGW32), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertTrue(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - MinGW64" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_MinGW64', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_MinGW64(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_MinGW64), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertTrue(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - UCRT64" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_UCRT64', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_UCRT64(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_UCRT64), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertTrue(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - Clang32" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_Clang32', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_Clang32(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_Clang32), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertTrue(platform.IsClang32OnWindows)
		self.assertFalse(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

	@mark.skipif("Windows+MSYS2 (x86-64) - Clang64" != os_getenv("ENVIRONMENT_NAME", "skip"), reason=f"Skipped 'test_Clang64', if environment variable 'ENVIRONMENT_NAME' doesn't match. {os_getenv('ENVIRONMENT_NAME', 'skip')}")
	def test_Clang64(self) -> None:
		platform = Platform()

		self.assertEqual(str(Platforms.Windows_MSYS2_Clang64), repr(platform))
		self.assertFalse(platform.IsNativeWindows)
		self.assertFalse(platform.IsNativeLinux)
		self.assertFalse(platform.IsNativeMacOS)
		self.assertTrue(platform.IsPOSIX)
		self.assertEqual("/", platform.PathSeperator)
		self.assertEqual(":", platform.ValueSeperator)
		self.assertTrue(platform.IsMSYS2Environment)
		self.assertFalse(platform.IsMSYSOnWindows)
		self.assertFalse(platform.IsMinGW32OnWindows)
		self.assertFalse(platform.IsMinGW64OnWindows)
		self.assertFalse(platform.IsUCRT64OnWindows)
		self.assertFalse(platform.IsClang32OnWindows)
		self.assertTrue(platform.IsClang64OnWindows)
		self.assertEqual("exe", platform.ExecutableExtension)
		self.assertEqual("lib", platform.StaticLibraryExtension)
		self.assertEqual("dll", platform.DynamicLibraryExtension)
		self.assertNotIn(Platforms.MSYS2_Runtime, platform.HostOperatingSystem)

# TODO: FreeBSD
