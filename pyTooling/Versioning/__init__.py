# ==================================================================================================================== #
#             _____           _ _           __     __            _             _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \   / /__ _ __ ___(_) ___  _ __ (_)_ __   __ _                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ / / _ \ '__/ __| |/ _ \| '_ \| | '_ \ / _` |                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V /  __/ |  \__ \ | (_) | | | | | | | | (_| |                          #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/ \___|_|  |___/_|\___/|_| |_|_|_| |_|\__, |                          #
# |_|    |___/                          |___/                                          |___/                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2020-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Implementation of semantic and date versioning version-numbers.

.. hint:: See :ref:`high-level help <VERSIONING>` for explanations and usage examples.
"""
from enum   import IntEnum
from sys    import version_info           # needed for versions before Python 3.11
from typing import Optional as Nullable, Any

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class Parts(IntEnum):
	"""Enumeration of parts in a version number that can be presents."""

	Unknown = 0     #: Undocumented
	Major = 1       #: Major number is present. (e.g. X in ``vX.0.0``).
	Minor = 2       #: Minor number is present. (e.g. Y in ``v0.Y.0``).
	Patch = 4       #: Patch number is present. (e.g. Z in ``v0.0.Z``).
	Build = 8       #: Build number is present. (e.g. bbbb in ``v0.0.0.bbbb``)
	Pre   = 16      #: Pre-release number is present.
	Post  = 32      #: Post-release number is present.
	Prefix = 64     #: Prefix is present.
	Postfix = 128   #: Postfix is present.
#		AHead   = 256


@export
class Flags(IntEnum):
	"""State enumeration, if a (tagged) version is build from a clean or dirty working directory."""

	Clean = 1       #: A versioned build was created from a *clean* working directory.
	Dirty = 2       #: A versioned build was created from a *dirty* working directory.


@export
class Version(metaclass=ExtendedType, slots=True):
	pass


@export
class SemanticVersion(Version):
	"""Representation of a semantic version number like ``3.7.12``."""

	_parts   : Parts = Parts.Unknown  #: Integer flag enumeration of present parts in a version number.
	_flags   : int = Flags.Clean      #: State if the version in a working directory is clean or dirty compared to a tagged version.
	_major   : int = 0                #: Major number part of the version number.
	_minor   : int = 0                #: Minor number part of the version number.
	_patch   : int = 0                #: Patch number part of the version number.
	_build   : int = 0                #: Build number part of the version number.
	_pre     : int = 0                #: Pre-release version number part.
	_post    : int = 0                #: Post-release version number part.
	_prefix  : str = ""               #: Prefix string
	_postfix : str = ""               #: Postfix string
# QUESTION: was this how many commits a version is ahead of the last tagged version?
#	ahead   : int = 0

	def __init__(self, major: int, minor: int, patch: int = 0, build: int = 0, flags: Flags = Flags.Clean) -> None:
		self._major = major
		self._minor = minor
		self._patch = patch
		self._build = build
		self._parts = Parts.Minor | Parts.Minor | Parts.Patch | Parts.Build
		self._flags = flags

	@classmethod
	def Parse(cls, versionString : str) -> "SemanticVersion":
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
		major = int(split[0])
		minor = 0
		patch = 0
		build = 0
		parts = Parts.Major
		if length >= 2:
			minor = int(split[1])
			parts |= Parts.Minor
		if length >= 3:
			patch = int(split[2])
			parts |= Parts.Patch
		if length >= 4:
			build = int(split[3])
			parts |= Parts.Build
		flags = Flags.Clean

		return cls(major, minor, patch, build, flags)

	@readonly
	def Major(self) -> int:
		return self._major

	@readonly
	def Minor(self) -> int:
		return self._minor

	@readonly
	def Patch(self) -> int:
		return self._patch

	@readonly
	def Build(self) -> int:
		return self._build

	@readonly
	def Parts(self) -> Parts:
		return self._parts

	@readonly
	def Flags(self) -> Flags:
		return self._flags

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both version numbers are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		return (
			(self._major == other._major) and
			(self._minor == other._minor) and
			(self._patch == other._patch) and
			(self._build == other._build)
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both version numbers are not equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		return not self.__eq__(other)

	@staticmethod
	def __compare(left: 'SemanticVersion', right: 'SemanticVersion') -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`SemanticVersion` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both parameters are equal).
		"""
		if left._major < right._major:
			return True
		elif left._major > right._major:
			return False

		if left._minor < right._minor:
			return True
		elif left._minor > right._minor:
			return False

		if left._patch < right._patch:
			return True
		elif left._patch > right._patch:
			return False

		if left._build < right._build:
			return True
		elif left._build > right._build:
			return False

		return None

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) if the version is less than the second operand.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if version is less than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		result = self.__compare(self, other)
		return result if result is not None else False

	def __le__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) if the version is less than or equal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if version is less than or equal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		result = self.__compare(self, other)
		return result if result is not None else True

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) if the version is greater than the second operand.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if version is greater than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		return not self.__le__(other)

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two Version instances (version numbers) if the version is greater than or equal to the second operand.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if version is greater than or equal to the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`SemanticVersion`.
		"""
		if not isinstance(other, SemanticVersion):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: SemanticVersion")
			raise ex

		return not self.__lt__(other)

	def __repr__(self) -> str:
		"""
		Return a string representation of this version number without prefix ``v``.

		:returns: Raw version number representation without a prefix.
		"""
		return f"{self._major}.{self._minor}.{self._patch}"

	def __str__(self) -> str:
		"""
		Return a string representation of this version number with prefix ``v``.

		:returns: Version number representation including a prefix.
		"""
		return f"v{self._major}.{self._minor}.{self._patch}"


@export
class CalendarVersion(Version):
	"""Representation of a calendar version number like ``2021.10``."""
