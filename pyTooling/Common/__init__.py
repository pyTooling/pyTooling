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

from typing     import Type

from flags      import Flags


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
class Platforms(Flags):
	__no_flags_name__ =   "Unknown"

	OS_Linux =     2**0
	OS_MacOS =     2**1
	OS_Windows =   2**2

	ENV_Native =   2**5
	ENV_WSL =      2**6
	ENV_MSYS2 =    2**7
	ENV_Cygwin =   2**8

	Arch_x86_32 =  2**10
	Arch_x86_64 =  2**11
	Arch_AArch64 = 2**12

	Linux =   OS_Linux +   ENV_Native + Arch_x86_64
	MacOS =   OS_MacOS +   ENV_Native + Arch_x86_64
	Windows = OS_Windows + ENV_Native + Arch_x86_64

	MSYS =         2**20
	MinGW32 =      2**21
	MinGW64 =      2**22
	UCRT64 =       2**23
	Clang32 =      2**24
	Clang64 =      2**25

	Windows_MSYS2_MSYS =    Windows + ENV_MSYS2 + Arch_x86_64 + MSYS
	Windows_MSYS2_MinGW32 = Windows + ENV_MSYS2 + Arch_x86_64 + MinGW32
	Windows_MSYS2_MinGW64 = Windows + ENV_MSYS2 + Arch_x86_64 + MinGW64
	Windows_MSYS2_UCRT64 =  Windows + ENV_MSYS2 + Arch_x86_64 + UCRT64
	Windows_MSYS2_Clang32 = Windows + ENV_MSYS2 + Arch_x86_64 + Clang32
	Windows_MSYS2_Clang64 = Windows + ENV_MSYS2 + Arch_x86_64 + Clang64


@export
class Platform:
	"""


	.. seealso:: https://stackoverflow.com/a/54837707/3719459
	"""

	_platform: Platforms

	def __init__(self):
		import sys
		import os
		import platform
		import sysconfig

		self._platform = Platforms.Unknown

		system = platform.system()
		machine = platform.machine()
		architecture = platform.architecture()
		sys_platform = sys.platform
		sysconfig_platform = sysconfig.get_platform()

		print()
		print(os.name)
		print(system)
		print(machine)
		print(architecture)
		print(sys_platform)
		print(sysconfig_platform)

		if os.name == "nt":
			self._platform |= Platforms.OS_Windows

			if sysconfig_platform == "win32":
				self._platform |= Platforms.ENV_Native | Platforms.Arch_x86_32
			elif sysconfig_platform == "win-amd64":
				self._platform |= Platforms.ENV_Native | Platforms.Arch_x86_64
			elif sysconfig_platform.startswith("mingw"):
				if machine == "AMD64":
					self._platform |= Platforms.Arch_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for Windows.")

				if sysconfig_platform == "mingw_i686":
					self._platform |= Platforms.ENV_MSYS2 | Platforms.MinGW32
				elif sysconfig_platform == "mingw_x86_64":
					self._platform |= Platforms.ENV_MSYS2 | Platforms.MinGW64
				elif sysconfig_platform == "mingw_x86_64_ucrt":
					self._platform |= Platforms.ENV_MSYS2 | Platforms.UCRT64
				elif sysconfig_platform == "mingw_x86_64_clang":
					self._platform |= Platforms.ENV_MSYS2 | Platforms.Clang64
				else:
					raise Exception(f"Unknown MSYS2 architecture '{sysconfig_platform}'.")
			else:
				raise Exception(f"Unknown platform '{sysconfig_platform}' running on Windows.")

		elif os.name == "posix":
			if sys_platform == "linux":
				self._platform |= Platforms.OS_Linux | Platforms.ENV_Native

				if sysconfig_platform == "linux-x86_64":            # native Linux x86_64; Windows 64 + WSL
					self._platform |= Platforms.Arch_x86_64
				elif sysconfig_platform == "linux-aarch64":         # native Linux Aarch64
					self._platform |= Platforms.Arch_x86_32
				else:
					raise Exception(f"Unknown architecture '{sysconfig_platform}' for a native Linux.")

			elif sys_platform == "msys":
				self._platform |= Platforms.OS_Windows | Platforms.ENV_MSYS2 | Platforms.MSYS

				if machine == "i686":
					self._platform |= Platforms.Arch_x86_32
				elif machine == "x86_64":
					self._platform |= Platforms.Arch_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for MSYS2-MSYS on Windows.")

			elif sys_platform == "cygwin":
				self._platform |= Platforms.OS_Windows

				if sysconfig_platform.startswith("msys"):
					self._platform |= Platforms.ENV_MSYS2 | Platforms.MSYS

					if machine == "i686":
						self._platform |= Platforms.Arch_x86_32
					elif machine == "x86_64":
						self._platform |= Platforms.Arch_x86_64
					else:
						raise Exception(f"Unknown architecture '{machine}' for MSYS2 on Windows.")

				elif sysconfig_platform.startswith("mingw64"):
					self._platform |= Platforms.ENV_MSYS2 | Platforms.MinGW64 | Platforms.Arch_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for Cygwin on Windows.")

			else:
				raise Exception(f"Unknown POSIX platform '{sys_platform}'.")
		else:
			raise Exception(f"Unknown operating system '{os.name}'.")

		print(self._platform)

		# if system == "Darwin":
		# 	self._platform |= Platforms.MacOS


		# sys.version_info => 3.10.1

	@property
	def IsNativePlatform(self) -> bool:
		return self._platform & Platforms.ENV_Native

	@property
	def HostPlatform(self):
		pass

	@property
	def ExecutableExtension(self):
		return "exe"

	@property
	def SharedLibraryExtension(self):
		return "dll" # so

	def __repr__(self) -> str:
		pass

	def __str__(self) -> str:
		runtime = ""

		if self._platform.OS_MacOS:
			platform = "macOS"
		elif self._platform.OS_Linux:
			platform = "Linux"
		elif self._platform.OS_Windows:
			platform = "Windows"
		else:
			platform = "plat:dec-err"

		if self._platform.ENV_Native:
			environment = ""
		elif self._platform.ENV_WSL:
			environment = "+WSL"
		elif self._platform.ENV_MSYS2:
			environment = "+MSYS2"

			if self._platform.MSYS:
				runtime = " - MSYS"
			elif self._platform.MinGW32:
				runtime = " - MinGW32"
			elif self._platform.MinGW64:
				runtime = " - MinGW64"
			elif self._platform.UCRT64:
				runtime = " - UCRT64"
			elif self._platform.Clang64:
				runtime = " - CLANG64"
			else:
				runtime = "rt:dec-err"

		elif self._platform.ENV_Cygwin:
			environment = "+Cygwin"
		else:
			environment = "env:dec-err"

		if self._platform.Arch_x86_32:
			architecture = "x86-32"
		elif self._platform.Arch_x86_64:
			architecture = "x86-64"
		elif self._platform.Arch_AArch64:
			architecture = "amd64"
		else:
			architecture = "arch:dec-err"

		return f"{platform}{environment} ({architecture}){runtime}"
