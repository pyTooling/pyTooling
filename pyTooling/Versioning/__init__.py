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
from enum   import Flag
from sys    import version_info   # needed for versions before Python 3.11
from typing import Optional as Nullable, Union, Callable

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType, abstractmethod, mustoverride
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, abstractmethod, mustoverride
		from Common              import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class Parts(Flag):
	"""Enumeration describing parts of a version number that can be present."""

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
class Flags(Flag):
	"""State enumeration, if a (tagged) version is build from a clean or dirty working directory."""

	Clean = 1       #: A versioned build was created from a *clean* working directory.
	Dirty = 2       #: A versioned build was created from a *dirty* working directory.


def WordSizeValidator(
	bits: Nullable[int] = None,
	majorBits: Nullable[int] = None,
	minorBits: Nullable[int] = None,
	patchBits: Nullable[int] = None,
	buildBits: Nullable[int] = None
):
	majorMax = minorMax = patchMax = buildMax = -1
	if bits is not None:
		majorMax = minorMax = patchMax = buildMax = 2**bits - 1

	if majorBits is not None:
		majorMax = 2**majorBits - 1
	if minorBits is not None:
		minorMax = 2**minorBits - 1
	if patchBits is not None:
		patchMax = 2**patchBits - 1
	if buildBits is not None:
		buildMax = 2**buildBits - 1

	def validator(version: SemanticVersion) -> bool:
		if Parts.Major in version._parts and version._major > majorMax:
			raise ValueError(f"Field 'Version.Major' > {max}.")

		if Parts.Minor in version._parts and version._minor > minorMax:
			raise ValueError(f"Field 'Version.Minor' > {max}.")

		if Parts.Patch in version._parts and version._patch > patchMax:
			raise ValueError(f"Field 'Version.Patch' > {max}.")

		return True

	return validator


def MaxValueValidator(
	max: Nullable[int] = None,
	majorMax: Nullable[int] = None,
	minorMax: Nullable[int] = None,
	patchMax: Nullable[int] = None,
	buildMax: Nullable[int] = None
):
	if max is not None:
		majorMax = minorMax = patchMax = buildMax = max

	def validator(version: SemanticVersion) -> bool:
		if Parts.Major in version._parts and version._major > majorMax:
			raise ValueError(f"Field 'Version.Major' > {max}.")

		if Parts.Minor in version._parts and version._minor > minorMax:
			raise ValueError(f"Field 'Version.Minor' > {max}.")

		if Parts.Patch in version._parts and version._patch > patchMax:
			raise ValueError(f"Field 'Version.Patch' > {max}.")

		return True

	return validator


@export
class Version(metaclass=ExtendedType, slots=True):
	"""Base-class for a version representation."""

	_parts   : Parts  #: Integer flag enumeration of present parts in a version number.
	_major   : int    #: Major number part of the version number.
	_minor   : int    #: Minor number part of the version number.
	_flags   : Flags  #: State if the version in a working directory is clean or dirty compared to a tagged version.

	def __init__(
		self,
		major: int,
		minor: Nullable[int] = None,
		flags: Flags = Flags.Clean
	) -> None:
		if not isinstance(major, int):
			raise TypeError("Parameter 'major' is not of type 'int'.")
		elif major < 0:
			raise ValueError("Parameter 'major' is negative.")

		self._major = major
		self._parts = Parts.Major

		if minor is not None:
			if not isinstance(minor, int):
				raise TypeError("Parameter 'minor' is not of type 'int'.")
			elif minor < 0:
				raise ValueError("Parameter 'minor' is negative.")

			self._minor = minor
			self._parts |= Parts.Minor
		else:
			self._minor = 0

		self._flags = flags

	@classmethod
	@abstractmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["SemanticVersion"], bool]] = None) -> "Version":
		"""Parse a version string and return a Version instance."""

	@readonly
	def Parts(self) -> Parts:
		return self._parts

	@readonly
	def Major(self) -> int:
		return self._major

	@readonly
	def Minor(self) -> int:
		return self._minor

	@readonly
	def Flags(self) -> Flags:
		return self._flags

	@abstractmethod
	def _equal(self, left: "CalendarVersion", right: "CalendarVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`Version` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""

	@abstractmethod
	def _compare(self, left: "Version", right: "Version") -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`Version` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both parameters are equal).
		"""

	@mustoverride
	def __eq__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers for equality.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return self._equal(self, other)

	@mustoverride
	def __ne__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers for inequality.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return not self._equal(self, other)

	@mustoverride
	def __lt__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than the second operand.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		result = self._compare(self, other)
		return result if result is not None else False

	@mustoverride
	def __le__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than or equal the second operand.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		result = self._compare(self, other)
		return result if result is not None else True

	@mustoverride
	def __gt__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than the second operand.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return not self.__le__(other)

	@mustoverride
	def __ge__(self, other: Union["Version", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than or equal the second operand.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return not self.__lt__(other)


@export
class SemanticVersion(Version):
	"""Representation of a semantic version number like ``3.7.12``."""

	_patch   : int    #: Patch number part of the version number.
	_build   : int    #: Build number part of the version number.
	_pre     : int    #: Pre-release version number part.
	_post    : int    #: Post-release version number part.
	_prefix  : str    #: Prefix string
	_postfix : str    #: Postfix string
# QUESTION: was this how many commits a version is ahead of the last tagged version?
#	ahead   : int = 0

	def __init__(
		self,
		major: int,
		minor: Nullable[int] = None,
		patch: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None
	) -> None:
		super().__init__(major, minor, flags)

		if patch is not None:
			if not isinstance(patch, int):
				raise TypeError("Parameter 'patch' is not of type 'int'.")
			elif patch < 0:
				raise ValueError("Parameter 'patch' is negative.")

			self._patch = patch
			self._parts |= Parts.Patch
		else:
			self._patch = 0

		if build is not None:
			if not isinstance(build, int):
				raise TypeError("Parameter 'build' is not of type 'int'.")
			elif build < 0:
				raise ValueError("Parameter 'build' is negative.")

			self._build = build
			self._parts |= Parts.Build
		else:
			self._build = 0

		if prefix is not None:
			if not isinstance(prefix, str):
				raise TypeError("Parameter 'prefix' is not of type 'str'.")

			self._prefix = prefix
			self._parts |= Parts.Prefix
		else:
			self._prefix = ""

	@classmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["SemanticVersion"], bool]] = None) -> "SemanticVersion":
		"""
		Parse a version string and return a :class:`SemanticVersion` instance.

		Allowed prefix characters:

		* ``v|V`` - version, public version, public release
		* ``i|I`` - internal version, internal release
		* ``r|R`` - release, revision
		* ``rev|REV`` - revision

		:param versionString: The version string to parse.
		:returns:             An object representing a semantic version.
		:raises TypeError:    If parameter ``other`` is not a string.
		:raises ValueError:   If parameter ``other`` is None.
		:raises ValueError:   If parameter ``other`` is empty.
		"""
		parts = Parts.Unknown
		prefix = None

		if versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif not isinstance(versionString, str):
			ex = TypeError(f"Parameter 'versionString' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(versionString)}'.")
			raise ex
		elif versionString == "":
			raise ValueError("Parameter 'versionString' is empty.")

		if versionString.startswith(("V", "v", "I", "i", "R", "r")):
			parts |= Parts.Prefix
			prefix = versionString[1].lower()
			versionString = versionString[1:]
		elif versionString.startswith(("rev", "REV")):
			parts |= Parts.Prefix
			prefix = versionString[0:3].lower()
			versionString = versionString[3:]

		split = versionString.split(".")
		length = len(split)
		major = int(split[0])
		minor = 0
		patch = 0
		build = 0
		parts |= Parts.Major

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

		version = cls(major, minor, patch, build, flags, prefix)
		if validator is not None and not validator(version):
			raise ValueError(f"Failed to validate version string '{versionString}'.")  # pragma: no cover

		return version

	@readonly
	def Patch(self) -> int:
		return self._patch

	@readonly
	def Build(self) -> int:
		return self._build

	def _equal(self, left: "SemanticVersion", right: "SemanticVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`SemanticVersion` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (
			(left._major == right._major) and
			(left._minor == right._minor) and
			(left._patch == right._patch) and
			(left._build == right._build)
		)

	def _compare(self, left: "SemanticVersion", right: "SemanticVersion") -> Nullable[bool]:
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

	def __eq__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers for equality.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__eq__(other)

	def __ne__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers for inequality.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__ne__(other)

	def __lt__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__lt__(other)

	def __le__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than or equal the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__le__(other)

	def __gt__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__gt__(other)

	def __ge__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than or equal the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__ge__(other)

	def __format__(self, formatSpec: str) -> str:
		"""
		Return a string representation of this version number according to the format specification.

		.. topic:: Format Specifiers

		* ``%P`` - prefix
		* ``%M`` - major number
		* ``%m`` - minor number
		* ``%u`` - patch number
		* ``%b`` - build number

		:param formatSpec: The format specification.
		:return:           Formatted version number.
		"""
		if formatSpec == "":
			return self.__str__()

		result = formatSpec
		result = result.replace("%M", str(self._major))
		result = result.replace("%m", str(self._minor))
		result = result.replace("%u", str(self._patch))
		result = result.replace("%b", str(self._build))
		result = result.replace("%P", str(self._prefix))
		# result = result.replace("%p", str(self._pre))

		return result.replace("%%", "%")

	def __repr__(self) -> str:
		"""
		Return a string representation of this version number without prefix ``v``.

		:returns: Raw version number representation without a prefix.
		"""
		return f"{self._prefix if Parts.Prefix in self._parts else ''}{self._major}.{self._minor}.{self._patch}"

	def __str__(self) -> str:
		"""
		Return a string representation of this version number with prefix ``v``.

		:returns: Version number representation including a prefix.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
		result += f"{self._major}" if Parts.Major in self._parts else ""
		result += f".{self._minor}" if Parts.Minor in self._parts else ""
		result += f".{self._patch}" if Parts.Patch in self._parts else ""

		return result


@export
class CalendarVersion(Version):
	"""Representation of a calendar version number like ``2021.10``."""

	def __init__(
		self,
		major: int,
		minor: Nullable[int] = None,
		flags: Flags = Flags.Clean
	) -> None:
		super().__init__(major, minor, flags)

	@classmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["SemanticVersion"], bool]] = None) -> "CalendarVersion":
		"""
		Parse a version string and return a :class:`CalendarVersion` instance.

		:param versionString: The version string to parse.
		:returns:             An object representing a calendar version.
		:raises TypeError:    If parameter ``other`` is not a string.
		:raises ValueError:   If parameter ``other`` is None.
		:raises ValueError:   If parameter ``other`` is empty.
		"""
		parts = Parts.Unknown

		if versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif not isinstance(versionString, str):
			ex = TypeError(f"Parameter 'versionString' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(versionString)}'.")
			raise ex
		elif versionString == "":
			raise ValueError("Parameter 'versionString' is empty.")

		split = versionString.split(".")
		length = len(split)
		major = int(split[0])
		minor = 0
		parts |= Parts.Major

		if length >= 2:
			minor = int(split[1])
			parts |= Parts.Minor

		flags = Flags.Clean

		version = cls(major, minor, flags)
		if validator is not None and not validator(version):
			raise ValueError(f"Failed to validate version string '{versionString}'.")  # pragma: no cover

		return version

	def _equal(self, left: "CalendarVersion", right: "CalendarVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`CalendarVersion` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (
			(left._major == right._major) and
			(left._minor == right._minor)
		)

	def _compare(self, left: "CalendarVersion", right: "CalendarVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`CalendarVersion` instances.

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

		return None

	def __eq__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers for equality.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a calendar version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__eq__(other)

	def __ne__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers for inequality.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a calendar version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__ne__(other)

	def __lt__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than the second operand.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__lt__(other)

	def __le__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is less than or equal the second operand.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is less than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__le__(other)

	def __gt__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than the second operand.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__gt__(other)

	def __ge__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
		"""
		Compare two version numbers if the version is greater than or equal the second operand.

		The second operand should be an instance of :class:`CalendarVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Parameter to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__ge__(other)

	def __format__(self, formatSpec: str) -> str:
		if formatSpec == "":
			return self.__str__()

	def __repr__(self) -> str:
		"""
		Return a string representation of this version number without prefix ``v``.

		:returns: Raw version number representation without a prefix.
		"""
		return f"{self._major}.{self._minor}"

	def __str__(self) -> str:
		"""
		Return a string representation of this version number with prefix ``v``.

		:returns: Version number representation including a prefix.
		"""
		result = f"{self._major}"
		result += f".{self._minor}" if Parts.Minor in self._parts else ""

		return result
