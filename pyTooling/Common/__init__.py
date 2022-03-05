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
"""Common types, helper functions and classes."""
__author__ =    "Patrick Lehmann"
__email__ =     "Paebbels@gmail.com"
__copyright__ = "2017-2022, Patrick Lehmann"
__license__ =   "Apache License, Version 2.0"
__version__ =   "1.9.6"
__keywords__ =  ["decorators", "meta classes", "exceptions", "versioning", "licensing", "overloading", "singleton", "setuptools", "wheel", "installation", "packaging"]

from enum     import Flag, auto
from typing   import Type


try:
	from pyTooling.Decorators import export
except ModuleNotFoundError:
	print("[pyTooling.Packaging] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export
	except ModuleNotFoundError as ex:
		print("[pyTooling.Packaging] Could not import from 'Decorators' or 'Licensing' directly!")
		raise ex


@export
def isnestedclass(cls: Type, scope: Type) -> bool:
	"""Returns true, if the given class ``cls`` is a member on an outer class ``scope``."""
	for mroClass in scope.mro():
		for memberName in mroClass.__dict__:
			member = getattr(mroClass, memberName)
			if isinstance(member, Type):
				if cls is member:
					return True

	return False


@export
class Platform:
	"""


	.. seealso:: https://stackoverflow.com/a/54837707/3719459
	"""

	class Platforms(Flag):
		Unknown = 0

		OS_Linux = auto()
		OS_MacOS = auto()
		OS_Windows = auto()

		OperatingSystem = OS_Linux | OS_MacOS | OS_Windows

		ENV_Native = auto()
		ENV_WSL = auto()
		ENV_MSYS2 = auto()
		ENV_Cygwin = auto()

		Environment = ENV_Native | ENV_WSL | ENV_MSYS2 | ENV_Cygwin

		ARCH_x86_32 = auto()
		ARCH_x86_64 = auto()
		ARCH_AArch64 = auto()

		Arch_x86 = ARCH_x86_32 | ARCH_x86_64
		Arch_Arm = ARCH_AArch64
		Architecture = Arch_x86 | Arch_Arm

		Linux = OS_Linux + ENV_Native + ARCH_x86_64
		MacOS = OS_MacOS + ENV_Native + ARCH_x86_64
		Windows = OS_Windows + ENV_Native + ARCH_x86_64

		MSYS = auto()
		MinGW32 = auto()
		MinGW64 = auto()
		UCRT64 = auto()
		Clang32 = auto()
		Clang64 = auto()

		Windows_MSYS2_MSYS = Windows + ENV_MSYS2 + ARCH_x86_64 + MSYS
		Windows_MSYS2_MinGW32 = Windows + ENV_MSYS2 + ARCH_x86_64 + MinGW32
		Windows_MSYS2_MinGW64 = Windows + ENV_MSYS2 + ARCH_x86_64 + MinGW64
		Windows_MSYS2_UCRT64 = Windows + ENV_MSYS2 + ARCH_x86_64 + UCRT64
		Windows_MSYS2_Clang32 = Windows + ENV_MSYS2 + ARCH_x86_64 + Clang32
		Windows_MSYS2_Clang64 = Windows + ENV_MSYS2 + ARCH_x86_64 + Clang64

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

		print(self._platform)

		# if system == "Darwin":
		# 	self._platform |= self.Platforms.MacOS
		# sys.version_info => 3.10.1

	@property
	def HostOperatingSystem(self) -> Platforms:
		return self._platform & self.Platforms.OperatingSystem

	@property
	def IsNativePlatform(self) -> bool:
		return self.Platforms.ENV_Native in self._platform

	@property
	def IsNativeWindows(self) -> bool:
		return self.Platforms.Windows in self._platform

	@property
	def IsNativeLinux(self) -> bool:
		return self.Platforms.Linux

	@property
	def IsNativeMacOS(self) -> bool:
		return self.Platforms.MacOS in self._platform

	@property
	def IsMSYS2Environment(self) -> bool:
		return self.Platforms.ENV_MSYS2 in self._platform

	@property
	def IsMSYSOnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_MSYS in self._platform

	@property
	def IsMinGW32OnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_MinGW32 in self._platform

	@property
	def IsMinGW64OnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_MinGW64 in self._platform

	@property
	def IsUCRT64OnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_UCRT64 in self._platform

	@property
	def IsClang32OnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_Clang32 in self._platform

	@property
	def IsClang64OnWindows(self) -> bool:
		return self.Platforms.Windows_MSYS2_Clang64 in self._platform

	@property
	def ExecutableExtension(self) -> str:
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
			platform = "macOS"
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
