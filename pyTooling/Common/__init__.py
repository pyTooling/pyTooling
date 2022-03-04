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

	Native =       2**0
	WSL =          2**1
	MSYS2 =        2**2
	Cygwin =       2**3

	OS_Linux =     2**5
	OS_MacOS =     2**6
	OS_Windows =   2**7

	Arch_x86_32 =  2**10
	Arch_x86_64 =  2**11
	Arch_AArch64 = 2**12

	Linux =        Arch_x86_64 + OS_Linux + Native
	MacOS =        Arch_x86_64 + OS_MacOS + Native
	Windows =      Arch_x86_64 + OS_Windows + Native

	MSYS =         2**20
	MinGW32 =      2**21
	MinGW64 =      2**22
	UCRT64 =       2**23
	Clang32 =      2**24
	Clang64 =      2**25

	Windows_MSYS2_MSYS =    Arch_x86_64 + Windows + MSYS2 + MSYS
	Windows_MSYS2_MinGW32 = Arch_x86_64 + Windows + MSYS2 + MinGW32
	Windows_MSYS2_MinGW64 = Arch_x86_64 + Windows + MSYS2 + MinGW64
	Windows_MSYS2_UCRT64 =  Arch_x86_64 + Windows + MSYS2 + UCRT64
	Windows_MSYS2_Clang32 = Arch_x86_64 + Windows + MSYS2 + Clang32
	Windows_MSYS2_Clang64 = Arch_x86_64 + Windows + MSYS2 + Clang64


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
		if os.name == "nt":
			self._platform |= Platforms.Windows

			if sysconfig_platform == "win32":
				self._platform |= Platforms.Native | Platforms.Arch_x86_32
			elif sysconfig_platform == "win-amd64":
				self._platform |= Platforms.Native | Platforms.Arch_x86_64
			elif sysconfig_platform == "mingw":
				self._platform |= Platforms.MSYS2

				if architecture[0] == "32bit":
					self._platform |= Platforms.MinGW32
				elif architecture[0] == "64bit":
					self._platform |= Platforms.MinGW64
				else:
					raise Exception(f"Unknown MSYS2 MinGW architecture '{architecture[0]}'.")
			else:
				raise Exception(f"Unknown platform '{sysconfig_platform}' running on Windows.")

		elif os.name == "posix":
			if sys_platform == "linux":
				self._platform |= Platforms.Linux | Platforms.Native

				if sysconfig_platform == "linux-x86_64":            # native Linux x86_64; Windows 64 + WSL
					self._platform |= Platforms.Arch_x86_64
				elif sysconfig_platform == "linux-aarch64":         # native Linux Aarch64
					self._platform |= Platforms.Arch_x86_32
				else:
					raise Exception(f"Unknown architecture '{sysconfig_platform}' for a native Linux.")

			elif sys_platform == "msys":
				self._platform |= Platforms.Windows | Platforms.MSYS2 | Platforms.MSYS

				if machine == "i686":
					self._platform |= Platforms.Arch_x86_32
				elif machine == "x86_64":
					self._platform |= Platforms.Arch_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for MSYS2-MSYS on Windows.")

			elif sys_platform == "cygwin":
				self._platform |= Platforms.Windows | Platforms.Cygwin

				if machine == "i686":
					self._platform |= Platforms.Arch_x86_32
				elif machine == "x86_64":
					self._platform |= Platforms.Arch_x86_64
				else:
					raise Exception(f"Unknown architecture '{machine}' for Cygwin on Windows.")
			else:
				raise Exception(f"Unknown POSIX platform '{platform}'.")
		else:
			raise Exception(f"Unknown operating system '{os.name}'.")

		# if system == "Darwin":
		# 	self._platform |= Platforms.MacOS


		# sys.version_info => 3.10.1

	@property
	def IsNativePlatform(self) -> bool:
		return self._platform & Platforms.Native

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
		if Platforms.OS_MacOS & self._platform:
			platform = "macOS"
		elif Platforms.OS_Linux & self._platform:
			platform = "Linux"
		elif Platforms.OS_Windows & self._platform:
			platform = "Windows"

		if Platforms.Native & self._platform:
			environment = ""
		elif Platforms.WSL & self._platform:
			environment = "+WSL"
		elif Platforms.MSYS2 & self._platform:
			environment = "+MSYS2"
		elif Platforms.Cygwin & self._platform:
			environment = "+Cygwin"

		if Platforms.Arch_x86_32 & self._platform:
			architecture = "x86-32"
		elif Platforms.Arch_x86_64 & self._platform:
			architecture = "x86-64"
		elif Platforms.Arch_AArch64 & self._platform:
			architecture = "amd64"

		if not (Platforms.Native & self._platform):
			if Platforms.MSYS & self._platform:
				runtime = " - MSYS"
			elif Platforms.MinGW32 & self._platform:
				runtime = " - MinGW32"
			elif Platforms.MinGW64 & self._platform:
				runtime = " - MinGW64"
			elif Platforms.UCRT64 & self._platform:
				runtime = " - UCRT64"
			elif Platforms.Clang64 & self._platform:
				runtime = " - CLANG64"
		else:
			runtime = ""

		return f"{platform}{environment} ({architecture}){runtime}"
