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
"""
Common platform information gathered from various sources.

.. hint:: See :ref:`high-level help <COMMON/Platform>` for explanations and usage examples.
"""
from enum import Flag, auto

from pyTooling.Decorators import export
from pyTooling.MetaClasses import ExtendedType


@export
class Platform(metaclass=ExtendedType, singleton=True):
	"""An instance of this class contains all gathered information available from various sources.

	.. seealso::

	   StackOverflow question: `Python: What OS am I running on? <https://stackoverflow.com/a/54837707/3719459>`__
	"""

	class Platforms(Flag):
		Unknown = 0

		OS_Linux =   auto()     #: Operating System: Linux.
		OS_MacOS =   auto()     #: Operating System: macOS.
		OS_Windows = auto()     #: Operating System: Windows.

		OperatingSystem = OS_Linux | OS_MacOS | OS_Windows  #: Mask: Any operating system.

		ENV_Native = auto()     #: Environment: :term:`native`.
		ENV_WSL =    auto()     #: Environment: :term:`Windows System for Linux <WSL>`.
		ENV_MSYS2 =  auto()     #: Environment: :term:`MSYS2`.
		ENV_Cygwin = auto()     #: Environment: :term:`Cygwin`.

		Environment = ENV_Native | ENV_WSL | ENV_MSYS2 | ENV_Cygwin  #: Mask: Any environment.

		ARCH_x86_32 =  auto()   #: Architecture: x86-32 (IA32).
		ARCH_x86_64 =  auto()   #: Architecture: x86-64 (AMD64).
		ARCH_AArch64 = auto()   #: Architecture: AArch64.

		Arch_x86 =     ARCH_x86_32 | ARCH_x86_64  #: Mask: Any x86 architecture.
		Arch_Arm =     ARCH_AArch64               #: Mask: Any Arm architecture.
		Architecture = Arch_x86 | Arch_Arm        #: Mask: Any architecture.

		Linux =   OS_Linux   | ENV_Native | ARCH_x86_64    #: Group: native Linux on x86-64.
		MacOS =   OS_MacOS   | ENV_Native | ARCH_x86_64    #: Group: native macOS on x86-64.
		Windows = OS_Windows | ENV_Native | ARCH_x86_64    #: Group: native Windows on x86-64.

		MSYS =    auto()     #: MSYS2 Runtime: MSYS.
		MinGW32 = auto()     #: MSYS2 Runtime: :term:`MinGW32 <MinGW>`.
		MinGW64 = auto()     #: MSYS2 Runtime: :term:`MinGW64 <MinGW>`.
		UCRT64 =  auto()     #: MSYS2 Runtime: :term:`UCRT64 <UCRT>`.
		Clang32 = auto()     #: MSYS2 Runtime: Clang32.
		Clang64 = auto()     #: MSYS2 Runtime: Clang64.

		MSYS2_Runtime = MSYS | MinGW32 | MinGW64 | UCRT64 | Clang32 | Clang64  #: Mask: Any MSYS2 runtime environment.

		Windows_MSYS2_MSYS =    OS_Windows | ENV_MSYS2 | ARCH_x86_64 | MSYS      #: Group: MSYS runtime running on Windows x86-64
		Windows_MSYS2_MinGW32 = OS_Windows | ENV_MSYS2 | ARCH_x86_64 | MinGW32   #: Group: MinGW32 runtime running on Windows x86-64
		Windows_MSYS2_MinGW64 = OS_Windows | ENV_MSYS2 | ARCH_x86_64 | MinGW64   #: Group: MinGW64 runtime running on Windows x86-64
		Windows_MSYS2_UCRT64 =  OS_Windows | ENV_MSYS2 | ARCH_x86_64 | UCRT64    #: Group: UCRT64 runtime running on Windows x86-64
		Windows_MSYS2_Clang32 = OS_Windows | ENV_MSYS2 | ARCH_x86_64 | Clang32   #: Group: Clang32 runtime running on Windows x86-64
		Windows_MSYS2_Clang64 = OS_Windows | ENV_MSYS2 | ARCH_x86_64 | Clang64   #: Group: Clang64 runtime running on Windows x86-64

	_platform: Platforms

	def __init__(self):
		import sys
		import os
		import platform
		import sysconfig

		self._platform = self.Platforms.Unknown

		# system = platform.system()
		machine = platform.machine()
		# architecture = platform.architecture()
		sys_platform = sys.platform
		sysconfig_platform = sysconfig.get_platform()

		# print()
		# print(os.name)
		# print(system)
		# print(machine)
		# print(architecture)
		# print(sys_platform)
		# print(sysconfig_platform)

		if os.name == "nt":
			self._platform |= self.Platforms.OS_Windows

			if sysconfig_platform == "win32":
				self._platform |= self.Platforms.ENV_Native | self.Platforms.ARCH_x86_32
			elif sysconfig_platform == "win-amd64":
				self._platform |= self.Platforms.ENV_Native | self.Platforms.ARCH_x86_64
			elif sysconfig_platform.startswith("mingw"):
				if machine == "AMD64":
					self._platform |= self.Platforms.ARCH_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for Windows.")

				if sysconfig_platform == "mingw_i686":
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.MinGW32
				elif sysconfig_platform == "mingw_x86_64":
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.MinGW64
				elif sysconfig_platform == "mingw_x86_64_ucrt":
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.UCRT64
				elif sysconfig_platform == "mingw_x86_64_clang":
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.Clang64
				else:
					raise Exception(f"Unknown MSYS2 architecture '{sysconfig_platform}'.")
			else:
				raise Exception(f"Unknown platform '{sysconfig_platform}' running on Windows.")

		elif os.name == "posix":
			if sys_platform == "linux":
				self._platform |= self.Platforms.OS_Linux | self.Platforms.ENV_Native

				if sysconfig_platform == "linux-x86_64":            # native Linux x86_64; Windows 64 + WSL
					self._platform |= self.Platforms.ARCH_x86_64
				elif sysconfig_platform == "linux-aarch64":         # native Linux Aarch64
					self._platform |= self.Platforms.ARCH_x86_32
				else:
					raise Exception(f"Unknown architecture '{sysconfig_platform}' for a native Linux.")

			elif sys_platform == "darwin":
				self._platform |= self.Platforms.OS_MacOS | self.Platforms.ENV_Native | self.Platforms.ARCH_x86_64

				# print()
				# print(os.name)
				# print(system)
				# print(machine)
				# print(architecture)
				# print(sys_platform)
				# print(sysconfig_platform)
			elif sys_platform == "msys":
				self._platform |= self.Platforms.OS_Windows | self.Platforms.ENV_MSYS2 | self.Platforms.MSYS

				if machine == "i686":
					self._platform |= self.Platforms.ARCH_x86_32
				elif machine == "x86_64":
					self._platform |= self.Platforms.ARCH_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for MSYS2-MSYS on Windows.")

			elif sys_platform == "cygwin":
				self._platform |= self.Platforms.OS_Windows

				if sysconfig_platform.startswith("msys"):
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.MSYS

					if machine == "i686":
						self._platform |= self.Platforms.ARCH_x86_32
					elif machine == "x86_64":
						self._platform |= self.Platforms.ARCH_x86_64
					else:
						raise Exception(f"Unknown architecture '{machine}' for MSYS2 on Windows.")

				elif sysconfig_platform.startswith("mingw64"):
					self._platform |= self.Platforms.ENV_MSYS2 | self.Platforms.MinGW64 | self.Platforms.ARCH_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for Cygwin on Windows.")

			else:
				raise Exception(f"Unknown POSIX platform '{sys_platform}'.")
		else:
			raise Exception(f"Unknown operating system '{os.name}'.")

		# print(self._platform)

	@property
	def HostOperatingSystem(self) -> Platforms:
		return self._platform & self.Platforms.OperatingSystem

	@property
	def IsNativePlatform(self) -> bool:
		"""Returns true, if the platform is a :term:`native` platform.

		:returns: ``True``, if the platform is a native platform.
		"""
		return self.Platforms.ENV_Native in self._platform

	@property
	def IsNativeWindows(self) -> bool:
		"""Returns true, if the platform is a :term:`native` Windows x86-64 platform.

		:returns: ``True``, if the platform is a native Windows x86-64 platform.
		"""
		return self.Platforms.Windows in self._platform

	@property
	def IsNativeLinux(self) -> bool:
		"""Returns true, if the platform is a :term:`native` Linux x86-64 platform.

		:returns: ``True``, if the platform is a native Linux x86-64 platform.
		"""
		return self.Platforms.Linux in self._platform

	@property
	def IsNativeMacOS(self) -> bool:
		"""Returns true, if the platform is a :term:`native` macOS x86-64 platform.

		:returns: ``True``, if the platform is a native macOS x86-64 platform.
		"""
		return self.Platforms.MacOS in self._platform

	@property
	def IsMSYS2Environment(self) -> bool:
		"""Returns true, if the platform is a :term:`MSYS2` environment on Windows.

		:returns: ``True``, if the platform is a MSYS2 environment on Windows.
		"""
		return self.Platforms.ENV_MSYS2 in self._platform

	@property
	def IsMSYSOnWindows(self) -> bool:
		"""Returns true, if the platform is a MSYS runtime on Windows.

		:returns: ``True``, if the platform is a MSYS runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_MSYS in self._platform

	@property
	def IsMinGW32OnWindows(self) -> bool:
		"""Returns true, if the platform is a :term:`MinGW32 <MinGW>` runtime on Windows.

		:returns: ``True``, if the platform is a MINGW32 runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_MinGW32 in self._platform

	@property
	def IsMinGW64OnWindows(self) -> bool:
		"""Returns true, if the platform is a :term:`MinGW64 <MinGW>` runtime on Windows.

		:returns: ``True``, if the platform is a MINGW64 runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_MinGW64 in self._platform

	@property
	def IsUCRT64OnWindows(self) -> bool:
		"""Returns true, if the platform is a :term:`UCRT64 <UCRT>` runtime on Windows.

		:returns: ``True``, if the platform is a UCRT64 runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_UCRT64 in self._platform

	@property
	def IsClang32OnWindows(self) -> bool:
		"""Returns true, if the platform is a Clang32 runtime on Windows.

		:returns: ``True``, if the platform is a Clang32 runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_Clang32 in self._platform

	@property
	def IsClang64OnWindows(self) -> bool:
		"""Returns true, if the platform is a Clang64 runtime on Windows.

		:returns: ``True``, if the platform is a Clang64 runtime on Windows.
		"""
		return self.Platforms.Windows_MSYS2_Clang64 in self._platform

	@property
	def ExecutableExtension(self) -> str:
		"""
		Returns the file extension for an executable.

		* Linux: ``""`` (empty string)
		* macOS: ``""`` (empty string)
		* Windows: ``"exe"``
		"""
		if self.Platforms.OS_Windows in self._platform:
			return "exe"
		elif self.Platforms.OS_Linux in self._platform:
			return ""
		elif self.Platforms.OS_MacOS in self._platform:
			return ""
		else:
			raise Exception(f"Unknown operating system.")

	@property
	def SharedLibraryExtension(self) -> str:
		"""
		Returns the file extension for a shared library.

		* Linux: ``"so"``
		* macOS: ``"lib"``
		* Windows: ``"dll"``
		"""
		if self.Platforms.OS_Windows in self._platform:
			return "dll"
		elif self.Platforms.OS_Linux in self._platform:
			return "so"
		elif self.Platforms.OS_MacOS in self._platform:
			return "lib"
		else:
			raise Exception(f"Unknown operating system.")

	def __repr__(self) -> str:
		return str(self._platform)

	def __str__(self) -> str:
		runtime = ""

		if self.Platforms.OS_MacOS in self._platform:
			platform = "MacOS"
		elif self.Platforms.OS_Linux in self._platform:
			platform = "Linux"
		elif self.Platforms.OS_Windows in self._platform:
			platform = "Windows"
		else:
			platform = "plat:dec-err"

		if self.Platforms.ENV_Native in self._platform:
			environment = ""
		elif self.Platforms.ENV_WSL in self._platform:
			environment = "+WSL"
		elif self.Platforms.ENV_MSYS2 in self._platform:
			environment = "+MSYS2"

			if self.Platforms.MSYS in self._platform:
				runtime = " - MSYS"
			elif self.Platforms.MinGW32 in self._platform:
				runtime = " - MinGW32"
			elif self.Platforms.MinGW64 in self._platform:
				runtime = " - MinGW64"
			elif self.Platforms.UCRT64 in self._platform:
				runtime = " - UCRT64"
			elif self.Platforms.Clang32 in self._platform:
				runtime = " - Clang32"
			elif self.Platforms.Clang64 in self._platform:
				runtime = " - Clang64"
			else:
				runtime = "rt:dec-err"

		elif self.Platforms.ENV_Cygwin in self._platform:
			environment = "+Cygwin"
		else:
			environment = "env:dec-err"

		if self.Platforms.ARCH_x86_32 in self._platform:
			architecture = "x86-32"
		elif self.Platforms.ARCH_x86_64 in self._platform:
			architecture = "x86-64"
		elif self.Platforms.ARCH_AArch64 in self._platform:
			architecture = "amd64"
		else:
			architecture = "arch:dec-err"

		return f"{platform}{environment} ({architecture}){runtime}"
