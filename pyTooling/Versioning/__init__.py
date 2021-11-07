# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     A common version class.
#
# License:
# ============================================================================
# Copyright 2020-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from enum          import IntEnum
from typing        import Optional as Nullable

from ..Decorators  import export
from ..MetaClasses import Overloading


@export
class Version(metaclass=Overloading):
	"""
	Representation of a version number.
	"""

	class Parts(IntEnum):
		Major = 1
		Minor = 2
		Patch = 4
		Build = 8
		Pre   = 16
		Post  = 32
		Prefix = 64
		Postfix = 128
		AHead   = 256

	class Flags(IntEnum):
		Clean = 1
		Dirty = 2

	parts   : Parts
	flags   : int = Flags.Clean
	major   : int = 0
	minor   : int = 0
	patch   : int = 0
	build   : int = 0
	pre     : int = 0
	post    : int = 0
	prefix  : str = ""
	postfix : str = ""
	ahead   : int = 0

	def __init__(self, versionString : str):
		if versionString == "":
			raise ValueError("Parameter 'versionString' is empty.")
		elif versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif versionString.startswith(("V", "v", "I", "i", "R", "r")):
			versionString = versionString[1:]
		elif versionString.startswith(("rev", "REV")):
			versionString = versionString[3:]

		split = versionString.split(".")
		length = len(split)
		self.major = int(split[0])
		if length >= 2:
			self.minor = int(split[1])
		if length >= 3:
			self.patch = int(split[2])
		if length >= 4:
			self.build = int(split[3])
		self.flags = self.Flags.Clean

	def __init__(self, major : int, minor : int, patch : int = 0, build : int = 0):
		self.major = major
		self.minor = minor
		self.patch = patch
		self.build = build
		self.flags = self.Flags.Clean

	def __eq__(self, other: 'Version'):
		return (
			(self.major == other.major) and
			(self.minor == other.minor) and
			(self.patch == other.patch) and
			(self.build == other.build)
		)

	def __ne__(self, other):
		return not self.__eq__(other)

	@staticmethod
	def __compare(left: 'Version', right: 'Version') -> Nullable[bool]:
		if (left.major < right.major):
			return True
		if (left.major > right.major):
			return False

		if (left.minor < right.minor):
			return True
		if (left.minor > right.minor):
			return False

		if (left.patch < right.patch):
			return True
		if (left.patch > right.patch):
			return False

		if (left.build < right.build):
			return True
		if (left.build > right.build):
			return False

		return None

	def __lt__(self, other):
		result = self.__compare(self, other)

		if result is not None:
			return result
		else:
			return False

	def __le__(self, other):
		result = self.__compare(self, other)

		if result is not None:
			return result
		else:
			return True

	def __gt__(self, other):
		return not self.__le__(other)

	def __ge__(self, other):
		return not self.__lt__(other)

	def __str__(self):
		return f"v{self.major}.{self.minor}.{self.patch}"

	def __repr__(self):
		return f"{self.major}.{self.minor}.{self.patch}"
