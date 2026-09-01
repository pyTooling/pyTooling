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
# Copyright 2020-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. hint::

   See :ref:`high-level help <VERSIONING>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Packaging`
      |rarr| Reading a package's version from its dunder variables.
   :mod:`pyTooling.Dependency`
      |rarr| Resolving requirements against these version numbers.
"""
from __future__            import annotations

from collections.abc       import Iterable as abc_Iterable
from enum                  import Flag, Enum
from re                    import compile as re_compile, escape as re_escape, Pattern
from typing                import Optional as Nullable, Union, Callable, Any, ClassVar, Generic, TypeVar, Iterable
from typing                import Iterator, Self

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType, abstractmethod, mustoverride
from pyTooling.Exceptions  import ToolingException
from pyTooling.Common      import getFullyQualifiedName


@export
class VersionValidatorError(ToolingException):
	"""
	Raised when a parsed version is rejected by the validator it was parsed with.

	The version string itself was well-formed - it parsed - so this is not a :exc:`ValueError` about the input, but
	a statement that the resulting version is not acceptable to the caller. The version that failed is carried in
	:attr:`Version`, so a caller can report what was wrong with it.
	"""

	_version: Nullable[Version]  #: The version rejected by a validator.

	def __init__(self, message: str, /, *, version: Nullable[Version] = None) -> None:
		"""
		Initializes the exception with the rejected version.

		:param message: The exception's message.
		:param version: Optional, the version the validator rejected.
		"""
		super().__init__(message)
		self._version = version

	@readonly
	def Version(self) -> Nullable[Version]:
		"""
		Read-only property to access the version the validator rejected (:attr:`_version`).

		:returns: The rejected version, or ``None`` if it wasn't recorded.
		"""
		return self._version


@export
class Parts(Flag):
	"""Enumeration describing parts of a version number that can be present."""
	Unknown = 0     #: Undocumented
	Epoch = 1       #: Epoch is present. (e.g. E in ``E:1.2.3`` or ``vE!1.2.3``)
	Major = 2       #: Major number is present. (e.g. X in ``vX.0.0``).
	Year = 2        #: Year is present. (e.g. X in ``XXXX.10``).
	Minor = 4       #: Minor number is present. (e.g. Y in ``v0.Y.0``).
	Month = 4       #: Month is present. (e.g. X in ``2024.YY``).
	Week = 4        #: Week is present. (e.g. X in ``2024.YY``).
	Micro = 8       #: Patch number is present. (e.g. Z in ``v0.0.Z``).
	Patch = 8       #: Patch number is present. (e.g. Z in ``v0.0.Z``).
	Day = 8         #: Day is present. (e.g. X in ``2024.10.ZZ``).
	Level = 16      #: Release level is present.
	Dev = 32        #: Development part is present.
	Build = 64      #: Build number is present. (e.g. bbbb in ``v0.0.0.bbbb``)
	Post  = 128     #: Post-release number is present.
	Prefix = 256    #: Prefix is present.
	Postfix = 512   #: Postfix is present.
	Hash = 1024     #: Hash is present.
#		AHead   = 256


@export
class ReleaseLevel(Enum):
	"""Enumeration describing the version's maturity level."""
	Final =              0  #:
	ReleaseCandidate = -10  #:
	Development =      -20  #:
	Gamma =            -30  #:
	Beta =             -40  #:
	Alpha =            -50  #:

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is equal to the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is equal the second operand's release level.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self is other

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is unequal to the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is unequal the second operand's release level.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self is not other

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is less than the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is less than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by < operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value < other.value

	def __le__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is less than or equal the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is less than or equal the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by <=>= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value <= other.value

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is greater than the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is greater than the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by > operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value > other.value

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two release levels if the level is greater than or equal the second operand.

		:param other:      Operand to compare against.
		:returns:          ``True``, if release level is greater than or equal the second operand.
		:raises TypeError: If parameter ``other`` is not of type :class:`ReleaseLevel` or string.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError("Second operand is not supported by >= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value >= other.value

	def __hash__(self) -> int:
		"""
		Compute a hash for this release level, so it can be used as a key in a dictionary or an element of a set.

		The hash is derived from the release level's value, so two release levels compare and hash alike.

		:returns: Hash of the release level's value.
		"""
		return hash(self.value)

	def __str__(self) -> str:
		"""
		Returns the release level's string equivalent.

		:returns:                 The string equivalent of the release level.
		:raises ToolingException: If the release level is unknown, so it has no string equivalent.
		"""
		if self is ReleaseLevel.Final:
			return "final"
		elif self is ReleaseLevel.ReleaseCandidate:
			return "rc"
		elif self is ReleaseLevel.Development:
			return "dev"
		elif self is ReleaseLevel.Beta:
			return "beta"
		elif self is ReleaseLevel.Alpha:
			return "alpha"

		raise ToolingException(f"Unknown ReleaseLevel '{self.name}'.")


@export
class Flags(Flag):
	"""State enumeration, if a (tagged) version is build from a clean or dirty working directory."""
	NoVCS = 0       #: No Version Control System VCS
	Clean = 1       #: A versioned build was created from a *clean* working directory.
	Dirty = 2       #: A versioned build was created from a *dirty* working directory.

	CVS = 16        #: Concurrent Versions System (CVS)
	SVN = 32        #: Subversion (SVN)
	Git = 64        #: Git
	Hg = 128        #: Mercurial (Hg)


@export
def WordSizeValidator(
	bits: Nullable[int] = None,
	majorBits: Nullable[int] = None,
	minorBits: Nullable[int] = None,
	microBits: Nullable[int] = None,
	buildBits: Nullable[int] = None
):
	"""
	A factory function to return a validator for Version instances for a positive integer range based on word-sizes in bits.

	:param bits:      Optional, number of bits to encode any positive version number part.
	:param majorBits: Optional, number of bits to encode a positive major number in a version.
	:param minorBits: Optional, number of bits to encode a positive minor number in a version.
	:param microBits: Optional, number of bits to encode a positive micro number in a version.
	:param buildBits: Optional, number of bits to encode a positive build number in a version.
	:returns:         A validation function for Version instances.
	"""
	majorMax = minorMax = microMax = buildMax = -1
	if bits is not None:
		majorMax = minorMax = microMax = buildMax = 2**bits - 1

	if majorBits is not None:
		majorMax = 2**majorBits - 1
	if minorBits is not None:
		minorMax = 2**minorBits - 1
	if microBits is not None:
		microMax = 2 ** microBits - 1
	if buildBits is not None:
		buildMax = 2**buildBits - 1

	def validator(version: SemanticVersion) -> bool:
		"""
		Validator function, which checks each version part against the maximum its word size allows.

		:param version:     Optional, the version to validate.
		:returns:           ``True``, if every part fits into its word size.
		:raises ValueError: If a part exceeds the maximum value of its word size.
		"""
		if Parts.Major in version._parts and version._major > majorMax:
			raise ValueError(f"Field 'Version.Major' > {majorMax}.")

		if Parts.Minor in version._parts and version._minor > minorMax:
			raise ValueError(f"Field 'Version.Minor' > {minorMax}.")

		if Parts.Micro in version._parts and version._micro > microMax:
			raise ValueError(f"Field 'Version.Micro' > {microMax}.")

		if Parts.Build in version._parts and version._build > buildMax:
			raise ValueError(f"Field 'Version.Build' > {buildMax}.")

		return True

	return validator


@export
def MaxValueValidator(
	max: Nullable[int] = None,
	majorMax: Nullable[int] = None,
	minorMax: Nullable[int] = None,
	microMax: Nullable[int] = None,
	buildMax: Nullable[int] = None
):
	"""
	A factory function to return a validator for Version instances checking for a positive integer range [0..max].

	:param max:      Optional, the upper bound for any positive version number part.
	:param majorMax: Optional, the upper bound for the positive major number.
	:param minorMax: Optional, the upper bound for the positive minor number.
	:param microMax: Optional, the upper bound for the positive micro number.
	:param buildMax: Optional, the upper bound for the positive build number.
	:returns:        A validation function for Version instances.
	"""
	if max is not None:
		majorMax = minorMax = microMax = buildMax = max

	def validator(version: SemanticVersion) -> bool:
		"""
		Validator function, which checks each version part against its maximum value.

		:param version:     Optional, the version to validate.
		:returns:           ``True``, if every part is within its maximum.
		:raises ValueError: If a part exceeds its maximum value.
		"""
		if Parts.Major in version._parts and version._major > majorMax:
			raise ValueError(f"Field 'Version.Major' > {majorMax}.")

		if Parts.Minor in version._parts and version._minor > minorMax:
			raise ValueError(f"Field 'Version.Minor' > {minorMax}.")

		if Parts.Micro in version._parts and version._micro > microMax:
			raise ValueError(f"Field 'Version.Micro' > {microMax}.")

		if Parts.Build in version._parts and version._build > buildMax:
			raise ValueError(f"Field 'Version.Build' > {buildMax}.")

		return True

	return validator


@export
class Version(metaclass=ExtendedType, slots=True):
	"""Base-class for a version representation."""

	__hash:         Nullable[int]  #: once computed hash of the object

	#: Separator between an epoch and the rest of the version number. Debian writes ``2:1.2.3``; PEP 440 writes
	#: ``2!1.2.3``, so :class:`PythonVersion` overrides this.
	_EPOCH_SEPARATOR: ClassVar[str] = ":"

	_parts:         Parts          #: Integer flag enumeration of present parts in a version number.
	_prefix:        str            #: Prefix string
	_epoch:         int            #: Epoch, which outranks every other part of the version number.
	_major:         int            #: Major number part of the version number.
	_minor:         int            #: Minor number part of the version number.
	_micro:         int            #: Micro number part of the version number.
	_releaseLevel:  ReleaseLevel   #: Release level (alpha, beta, rc, final, ...).
	_releaseNumber: int            #: Release number (Python calls this a serial).
	_post:          int            #: Post-release version number part.
	_dev:           int            #: Development number
	_build:         int            #: Build number part of the version number.
	_postfix:       str            #: Postfix string
	_hash:          str            #: Hash from version control system.
	_flags:         Flags          #: State if the version in a working directory is clean or dirty compared to a tagged version.

	def __init__(
		self,
		major:   int,
		minor:   Nullable[int] = None,
		micro:   Nullable[int] = None,
		level:   Nullable[ReleaseLevel] = ReleaseLevel.Final,
		number:  Nullable[int] = None,
		post:    Nullable[int] = None,
		dev:     Nullable[int] = None,
		*,
		epoch:   Nullable[int] = None,
		build:   Nullable[int] = None,
		postfix: Nullable[str] = None,
		prefix:  Nullable[str] = None,
		hash:    Nullable[str] = None,
		flags:   Flags = Flags.NoVCS
	) -> None:
		"""
		Initializes a version number representation.

		:param major:       Major number part of the version number.
		:param minor:       Optional, minor number part of the version number.
		:param micro:       Optional, micro (patch) number part of the version number.
		:param level:       Optional, release level (alpha, beta, release candidate, final, ...) of the version number.
		:param number:      Optional, release number part (in combination with release level) of the version number.
		:param post:        Optional, post number part of the version number.
		:param dev:         Optional, development number part of the version number.
		:param epoch:       Optional, the version number's epoch, which outranks every other part.
		:param build:       Optional, build number part of the version number.
		:param postfix:     Optional, the version number's postfix.
		:param prefix:      Optional, the version number's prefix.
		:param hash:        Optional, postfix string.
		:param flags:       Optional, the version number's flags.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'epoch' is not of type integer.
		:raises ValueError: If parameter 'epoch' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		self.__hash = None

		if not isinstance(major, int):
			ex = TypeError("Parameter 'major' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(major)}'.")
			raise ex
		elif major < 0:
			raise ValueError("Parameter 'major' is negative.")

		self._parts = Parts.Major
		self._major = major

		if epoch is not None:
			if not isinstance(epoch, int):
				ex = TypeError("Parameter 'epoch' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(epoch)}'.")
				raise ex
			elif epoch < 0:
				raise ValueError("Parameter 'epoch' is negative.")

			self._parts |= Parts.Epoch
			self._epoch = epoch
		else:
			self._epoch = 0

		if minor is not None:
			if not isinstance(minor, int):
				ex = TypeError("Parameter 'minor' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(minor)}'.")
				raise ex
			elif minor < 0:
				raise ValueError("Parameter 'minor' is negative.")

			self._parts |= Parts.Minor
			self._minor = minor
		else:
			self._minor = 0

		if micro is not None:
			if not isinstance(micro, int):
				ex = TypeError("Parameter 'micro' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(micro)}'.")
				raise ex
			elif micro < 0:
				raise ValueError("Parameter 'micro' is negative.")

			self._parts |= Parts.Micro
			self._micro = micro
		else:
			self._micro = 0

		if level is None:
			raise ValueError("Parameter 'level' is None.")
		elif not isinstance(level, ReleaseLevel):
			ex = TypeError("Parameter 'level' is not of type 'ReleaseLevel'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(level)}'.")
			raise ex
		elif level is ReleaseLevel.Final:
			if number is not None:
				raise ValueError("Parameter 'number' must be None, if parameter 'level' is 'Final'.")

			self._parts |= Parts.Level
			self._releaseLevel = level
			self._releaseNumber = 0
		else:
			self._parts |= Parts.Level
			self._releaseLevel = level

			if number is not None:
				if not isinstance(number, int):
					ex = TypeError("Parameter 'number' is not of type 'int'.")
					ex.add_note(f"Got type '{getFullyQualifiedName(number)}'.")
					raise ex
				elif number < 0:
					raise ValueError("Parameter 'number' is negative.")

				self._releaseNumber = number
			else:
				self._releaseNumber = 0

		if dev is not None:
			if not isinstance(dev, int):
				ex = TypeError("Parameter 'dev' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(dev)}'.")
				raise ex
			elif dev < 0:
				raise ValueError("Parameter 'dev' is negative.")

			self._parts |= Parts.Dev
			self._dev = dev
		else:
			self._dev = 0

		if post is not None:
			if not isinstance(post, int):
				ex = TypeError("Parameter 'post' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(post)}'.")
				raise ex
			elif post < 0:
				raise ValueError("Parameter 'post' is negative.")

			self._parts |= Parts.Post
			self._post = post
		else:
			self._post = 0

		if build is not None:
			if not isinstance(build, int):
				ex = TypeError("Parameter 'build' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(build)}'.")
				raise ex
			elif build < 0:
				raise ValueError("Parameter 'build' is negative.")

			self._build = build
			self._parts |= Parts.Build
		else:
			self._build = 0

		if postfix is not None:
			if not isinstance(postfix, str):
				ex = TypeError("Parameter 'postfix' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(postfix)}'.")
				raise ex

			self._parts |= Parts.Postfix
			self._postfix = postfix
		else:
			self._postfix = ""

		if prefix is not None:
			if not isinstance(prefix, str):
				ex = TypeError("Parameter 'prefix' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(prefix)}'.")
				raise ex

			self._parts |= Parts.Prefix
			self._prefix = prefix
		else:
			self._prefix = ""

		if hash is not None:
			if not isinstance(hash, str):
				ex = TypeError("Parameter 'hash' is not of type 'str'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(hash)}'.")
				raise ex

			self._parts |= Parts.Hash
			self._hash = hash
		else:
			self._hash = ""

		if flags is None:
			raise ValueError("Parameter 'flags' is None.")
		elif not isinstance(flags, Flags):
			ex = TypeError("Parameter 'flags' is not of type 'Flags'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(flags)}'.")
			raise ex

		self._flags = flags

	@classmethod
	@abstractmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[[SemanticVersion], bool]] = None) -> Version:
		"""
		Parse a version string and return a Version instance.

		:param versionString: The version string to parse.
		:param validator:     Optional, validator rejecting a parsed version, e.g. by word size or maximum value.
		:returns:             The parsed version number.
		"""

	@readonly
	def Parts(self) -> Parts:
		"""
		Read-only property to access the used parts of this version number.

		:returns: A flag enumeration of used version number parts.
		"""
		return self._parts

	@readonly
	def Prefix(self) -> str:
		"""
		Read-only property to access the version number's prefix.

		:returns: The prefix of the version number.
		"""
		return self._prefix

	@readonly
	def Epoch(self) -> int:
		"""
		Read-only property to access the epoch (:attr:`_epoch`).

		An epoch outranks every other part, so a version carrying one is newer than any version with a lower epoch
		however high the rest of its numbers are. It exists so a project can *lower* its version number - change
		scheme, or recover from a bad release - without every later version comparing as older. A version without one
		has epoch ``0``, which is what keeps it comparable with a version that has one.

		:returns: The epoch, or ``0`` if the version carries none.
		"""
		return self._epoch

	@readonly
	def Major(self) -> int:
		"""
		Read-only property to access the major number.

		:returns: The major number.
		"""
		return self._major

	@readonly
	def Minor(self) -> int:
		"""
		Read-only property to access the minor number.

		:returns: The minor number.
		"""
		return self._minor

	@readonly
	def Micro(self) -> int:
		"""
		Read-only property to access the micro number.

		:returns: The micro number.
		"""
		return self._micro

	@readonly
	def ReleaseLevel(self) -> ReleaseLevel:
		"""
		Read-only property to access the release level.

		:returns: The release level.
		"""
		return self._releaseLevel

	@readonly
	def ReleaseNumber(self) -> int:
		"""
		Read-only property to access the release number.

		:returns: The release number.
		"""
		return self._releaseNumber

	@readonly
	def Post(self) -> int:
		"""
		Read-only property to access the post number.

		:returns: The post number.
		"""
		return self._post

	@readonly
	def Dev(self) -> int:
		"""
		Read-only property to access the development number.

		:returns: The development number.
		"""
		return self._dev

	@readonly
	def Build(self) -> int:
		"""
		Read-only property to access the build number.

		:returns: The build number.
		"""
		return self._build

	@readonly
	def Postfix(self) -> str:
		"""
		Read-only property to access the version number's postfix.

		:returns: The postfix of the version number.
		"""
		return self._postfix

	@readonly
	def Hash(self) -> str:
		"""
		Read-only property to access the version number's hash.

		:returns: The hash.
		"""
		return self._hash

	@readonly
	def Flags(self) -> Flags:
		"""
		Read-only property to access the version number's flags.

		:returns: The flags of the version number.
		"""
		return self._flags

	def _equal(self, left: Version, right: Version) -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`Version` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (
			(left._epoch == right._epoch) and
			(left._major == right._major) and
			(left._minor == right._minor) and
			(left._micro == right._micro) and
			(left._releaseLevel == right._releaseLevel) and
			(left._releaseNumber == right._releaseNumber) and
			(left._post == right._post) and
			(left._dev == right._dev) and
			(left._build == right._build) and
			(left._postfix == right._postfix)
		)

	def _compare(self, left: Version, right: Version) -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`Version` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both operands are equal).
		"""
		if left._epoch < right._epoch:
			return True
		elif left._epoch > right._epoch:
			return False

		if left._major < right._major:
			return True
		elif left._major > right._major:
			return False

		if left._minor < right._minor:
			return True
		elif left._minor > right._minor:
			return False

		if left._micro < right._micro:
			return True
		elif left._micro > right._micro:
			return False

		if left._releaseLevel < right._releaseLevel:
			return True
		elif left._releaseLevel > right._releaseLevel:
			return False

		if left._releaseNumber < right._releaseNumber:
			return True
		elif left._releaseNumber > right._releaseNumber:
			return False

		if left._post < right._post:
			return True
		elif left._post > right._post:
			return False

		if left._dev < right._dev:
			return True
		elif left._dev > right._dev:
			return False

		if left._build < right._build:
			return True
		elif left._build > right._build:
			return False

		return None

	def _minimum(self, actual: Version, expected: Version) -> Nullable[bool]:
		"""
		Check if a version fulfills a minimum requirement.

		How exact the comparison is depends on how detailed the expected version is: a minor number in the expectation
		requires an exact major number, and a micro number requires an exact minor number.

		:param actual:   The version to check.
		:param expected: The minimum version, whose parts decide how exact the comparison is.
		:returns:        ``True``, if the actual version fulfills the expectation.
		"""
		exactMajor = Parts.Minor in expected._parts
		exactMinor = Parts.Micro in expected._parts

		if exactMajor and actual._major != expected._major:
			return False
		elif not exactMajor and actual._major < expected._major:
			return False

		if exactMinor and actual._minor != expected._minor:
			return False
		elif not exactMinor and actual._minor < expected._minor:
			return False

		if Parts.Micro in expected._parts:
			return actual._micro >= expected._micro

		return True

	def _format(self, formatSpec: str) -> str:
		"""
		Return a string representation of this version number according to the format specification.

		.. topic:: Format Specifiers

		   * ``%p`` - prefix
		   * ``%M`` - major number
		   * ``%m`` - minor number
		   * ``%u`` - micro number
		   * ``%b`` - build number

		:param formatSpec: The format specification.
		:returns:          Formatted version number.
		"""
		if formatSpec == "":
			return self.__str__()

		result = formatSpec
		result = result.replace("%p", str(self._prefix))
		result = result.replace("%M", str(self._major))
		result = result.replace("%m", str(self._minor))
		result = result.replace("%u", str(self._micro))
		result = result.replace("%b", str(self._build))
		result = result.replace("%r", str(self._releaseLevel)[0])
		result = result.replace("%R", str(self._releaseLevel))
		result = result.replace("%n", str(self._releaseNumber))
		result = result.replace("%d", str(self._dev))
		result = result.replace("%P", str(self._postfix))

		return result

	@mustoverride
	def __eq__(self, other: Any) -> bool:
		"""
		Compare two version numbers for equality.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if both version numbers are equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, string or integer.
		"""
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return self._equal(self, other)

	@mustoverride
	def __ne__(self, other: Any) -> bool:
		"""
		Compare two version numbers for inequality.

		The second operand should be an instance of :class:`Version`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, string or integer.
		"""
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return not self._equal(self, other)

	@mustoverride
	def __lt__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is less than the second operand.

		The second operand should be an instance of :class:`Version`, but :class:`VersionRange`, :class:`VersionSet`,
		``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`,
		                    :class:`VersionSet`, string or integer.
		"""
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, VersionRange):
			other = other._lowerBound
		elif isinstance(other, VersionSet):
			other = other._items[0]
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by < operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		return self._compare(self, other) is True

	@mustoverride
	def __le__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is less than or equal the second operand.

		The second operand should be an instance of :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, but
		``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is less than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`,
		                    :class:`VersionSet`, string or integer.
		"""
		equalValue = True
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, VersionRange):
			equalValue = RangeBoundHandling.LowerBoundExclusive not in other._boundHandling
			other = other._lowerBound
		elif isinstance(other, VersionSet):
			other = other._items[0]
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by <= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		result = self._compare(self, other)
		return result if result is not None else equalValue

	@mustoverride
	def __gt__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is greater than the second operand.

		The second operand should be an instance of :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, but
		``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is greater than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`,
		                    :class:`VersionSet`, string or integer.
		"""
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, VersionRange):
			other = other._upperBound
		elif isinstance(other, VersionSet):
			other = other._items[-1]
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by > operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		return self._compare(self, other) is False

	@mustoverride
	def __ge__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is greater than or equal the second operand.

		The second operand should be an instance of :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, but
		``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`,
		                    :class:`VersionSet`, string or integer.
		"""
		equalValue = True
		if other is None:
			raise ValueError("Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
			pass
		elif isinstance(other, VersionRange):
			equalValue = RangeBoundHandling.UpperBoundExclusive not in other._boundHandling
			other = other._upperBound
		elif isinstance(other, VersionSet):
			other = other._items[-1]
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by >= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		result = self._compare(self, other)
		return not result if result is not None else equalValue

	def __rshift__(self, other: Union[Version, str, int, None]) -> bool:
		"""
		Return the minimum of this version and a second operand.

		:param other:       Second operand, a version, a version string or a major version number.
		:returns:           ``True``, if this version is the minimum of both operands.
		:raises ValueError: If the second operand is ``None``.
		:raises TypeError:  If the second operand is not a version, a string or an integer.
		"""
		if other is None:
			raise ValueError("Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError("Second operand is not supported by >> operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return self._minimum(self, other)

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number and cache it.

		All parts of the version are part of the hash, so two versions differing in a postfix or a build number don't
		collide.

		:returns: Hash of this version number.
		"""
		if self.__hash is None:
			self.__hash = hash((
				self._prefix,
				self._epoch,
				self._major,
				self._minor,
				self._micro,
				self._releaseLevel,
				self._releaseNumber,
				self._post,
				self._dev,
				self._build,
				self._postfix,
				self._hash,
				self._flags
			))
		return self.__hash


@export
class SemanticVersion(Version):
	"""Representation of a semantic version number like ``3.7.12``."""

	_PATTERN: ClassVar[Pattern] = re_compile(
		r"^"
		r"(?P<prefix>rev|REV|[vViIrR])?"
		r"(?:(?P<epoch>\d+):)?"
		r"(?P<major>\d+)"
		r"(?:\.(?P<minor>\d+))?"
		r"(?:\.(?P<micro>\d+))?"
		r"(?:"
			r"(?:\.(?P<build>\d+))"
		r"|"
			r"(?:[-](?P<release>dev|final))"
		r"|"
			r"(?:(?P<delim1>[\.\-]?)(?P<level>alpha|beta|gamma|a|b|c|rc|pl)(?P<number>\d+))"
		r")?"
		r"(?:(?P<delim2>[\.\-]post)(?P<post>\d+))?"
		r"(?:(?P<delim3>[\.\-]dev)(?P<dev>\d+))?"
		r"(?:(?P<delim4>[\.\-\+])(?P<postfix>\w+))?"
		r"$"
	)  #: Regular expression to parse a semantic version from a string.
# QUESTION: was this how many commits a version is ahead of the last tagged version?
#	ahead:    int = 0

	def __init_subclass__(cls, **kwargs: Any) -> None:
		"""
		Rebuild the pattern when a derived class spells the epoch separator differently.

		A compiled pattern still carries the expression it was built from, so the base class' one is taken apart and
		put back together with this class' separator. Only the epoch's separator is substituted, and only when the
		class states no pattern of its own - a class replacing the whole expression means it.

		:param kwargs: Keyword arguments passed on to the base implementation.
		"""
		super().__init_subclass__(**kwargs)

		if "_PATTERN" in cls.__dict__ or cls._EPOCH_SEPARATOR == SemanticVersion._EPOCH_SEPARATOR:
			return

		cls._PATTERN = re_compile(SemanticVersion._PATTERN.pattern.replace(
			f"(?P<epoch>\\d+){re_escape(SemanticVersion._EPOCH_SEPARATOR)}",
			f"(?P<epoch>\\d+){re_escape(cls._EPOCH_SEPARATOR)}"
		))

	def __init__(
		self,
		major:   int,
		minor:   Nullable[int] = None,
		micro:   Nullable[int] = None,
		level:   Nullable[ReleaseLevel] = ReleaseLevel.Final,
		number:  Nullable[int] = None,
		post:    Nullable[int] = None,
		dev:     Nullable[int] = None,
		*,
		epoch:   Nullable[int] = None,
		build:   Nullable[int] = None,
		postfix: Nullable[str] = None,
		prefix:  Nullable[str] = None,
		hash:    Nullable[str] = None,
		flags:   Flags = Flags.NoVCS
	) -> None:
		"""
		Initializes a semantic version number representation.

		:param major:       Major number part of the version number.
		:param minor:       Optional, minor number part of the version number.
		:param micro:       Optional, micro (patch) number part of the version number.
		:param level:       Optional, release level of the version number (alpha, beta, release candidate, final, ...).
		:param number:      Optional, number within the release level, e.g. ``2`` in ``rc2``.
		:param post:        Optional, post number part of the version number.
		:param dev:         Optional, development number part of the version number.
		:param epoch:       Optional, the version number's epoch, which outranks every other part.
		:param build:       Optional, build number part of the version number.
		:param postfix:     Optional, the version number's postfix.
		:param prefix:      Optional, the version number's prefix.
		:param hash:        Optional, hash of the version control system's commit this version was built from.
		:param flags:       Optional, the version number's flags.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'post' is not of type integer.
		:raises ValueError: If parameter 'post' is a negative number.
		:raises TypeError:  If parameter 'dev' is not of type integer.
		:raises ValueError: If parameter 'dev' is a negative number.
		:raises TypeError:  If parameter 'epoch' is not of type integer.
		:raises ValueError: If parameter 'epoch' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(major, minor, micro, level, number, post, dev, epoch=epoch, build=build, postfix=postfix,
		                 prefix=prefix, hash=hash, flags=flags)

	@classmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[[SemanticVersion], bool]] = None) -> SemanticVersion:
		"""
		Parse a version string and return a :class:`SemanticVersion` instance.

		Allowed prefix characters:

		* ``v|V`` - version, public version, public release
		* ``i|I`` - internal version, internal release
		* ``r|R`` - release, revision
		* ``rev|REV`` - revision

		:param versionString:          The version string to parse.
		:param validator:              Optional, a validation function.
		:returns:                      An object representing a semantic version.
		:raises TypeError:             When parameter ``versionString`` is not a string.
		:raises ValueError:            When parameter ``versionString`` is None or empty.
		:raises ValueError:            When parameter ``versionString`` isn't a semantic version number. |br|
		                               It may carry one of the prefixes ``v``, ``i``, ``r`` or ``rev``, e.g. ``v1.2.3``.
		:raises ValueError:            When the epoch is malformed. |br|
		                               An epoch is a number followed by the separator and comes after any prefix,
		                               e.g. ``2:1.2.3`` or ``v2!1.2.3``.
		:raises VersionValidatorError: When the parsed version is rejected by ``validator``.
		"""
		if versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif not isinstance(versionString, str):
			ex = TypeError("Parameter 'versionString' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(versionString)}'.")
			raise ex
		elif (versionString := versionString.strip()) == "":
			raise ValueError("Parameter 'versionString' is empty.")

		if (match := cls._PATTERN.match(versionString)) is None:
			ex = ValueError(f"Syntax error in parameter 'versionString': '{versionString}'")
			ex.add_note("It may carry one of the prefixes 'v', 'i', 'r' or 'rev', e.g. 'v1.2.3'.")
			raise ex

		def toInt(value: Nullable[str]) -> Nullable[int]:
			"""
			Nested function converting an optional part of a version string to an integer.

			:param value:       The matched part, or ``None`` if the pattern didn't match it.
			:returns:           The part as an integer, or ``None`` if it wasn't present.
			:raises ValueError: If the part isn't a number.
			"""
			if value is None or value == "":
				return None

			try:
				return int(value)
			except ValueError as ex:  # pragma: no cover
				raise ValueError(f"Invalid part '{value}' in version number '{versionString}'.") from ex

		prefix = match["prefix"]

		release = match["release"]
		if release is not None:
			if release == "dev":
				releaseLevel = ReleaseLevel.Development
			elif release == "final":
				releaseLevel = ReleaseLevel.Final
			else:  # pragma: no cover
				raise ValueError(f"Unknown release level '{release}' in version number '{versionString}'.")
		else:
			level = match["level"]
			if level is not None:
				level = level.lower()
				if level == "a" or level == "alpha":
					releaseLevel = ReleaseLevel.Alpha
				elif level == "b" or level == "beta":
					releaseLevel = ReleaseLevel.Beta
				elif level == "c" or level == "gamma":
					releaseLevel = ReleaseLevel.Gamma
				elif level == "rc":
					releaseLevel = ReleaseLevel.ReleaseCandidate
				else:  # pragma: no cover
					raise ValueError(f"Unknown release level '{level}' in version number '{versionString}'.")
			else:
				releaseLevel = ReleaseLevel.Final

		version = cls(
			major=toInt(match["major"]),
			minor=toInt(match["minor"]),
			micro=toInt(match["micro"]),
			level=releaseLevel,
			number=toInt(match["number"]),
			post=toInt(match["post"]),
			dev=toInt(match["dev"]),
			epoch=toInt(match["epoch"]),
			build=toInt(match["build"]),
			postfix=match["postfix"],
			prefix=prefix if prefix != "" else None,
			# hash=match["hash"],
			flags=Flags.Clean
		)

		if validator is not None and not validator(version):
			raise VersionValidatorError(f"Failed to validate version string '{versionString}'.", version=version)

		return version

	@readonly
	def Patch(self) -> int:
		"""
		Read-only property to access the patch number.

		The patch number is identical to the micro number.

		:returns: The patch number.
		"""
		return self._micro

	def _equal(self, left: SemanticVersion, right: SemanticVersion) -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`SemanticVersion` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return super()._equal(left, right)

	def _compare(self, left: SemanticVersion, right: SemanticVersion) -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`SemanticVersion` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both operands are equal).
		"""
		return super()._compare(left, right)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two version numbers for equality.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if both version numbers are equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__eq__(other)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two version numbers for inequality.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__ne__(other)

	def __lt__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is less than the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__lt__(other)

	def __le__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is less than or equal the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is less than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__le__(other)

	def __gt__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is greater than the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is greater than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__gt__(other)

	def __ge__(self, other: Any) -> bool:
		"""
		Compare two version numbers if the version is greater than or equal the second operand.

		The second operand should be an instance of :class:`SemanticVersion`, but ``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a semantic version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, string or integer.
		"""
		return super().__ge__(other)

	def __rshift__(self, other: Union[SemanticVersion, str, int, None]) -> bool:
		"""
		Return the minimum of this semantic version and a second operand.

		:param other:       Second operand, a version, a version string or a major version number.
		:returns:           ``True``, if this version is the minimum of both operands.
		:raises ValueError: If the second operand is ``None``.
		:raises TypeError:  If the second operand is not a version, a string or an integer.
		"""
		return super().__rshift__(other)

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()

	def __format__(self, formatSpec: str) -> str:
		"""
		Return a string representation of this version number according to the format specification.

		:param formatSpec:  The format specification, using ``%``-placeholders for the version's parts.
		:returns:           Formatted version number.
		:raises ValueError: If the format specification contains an unknown placeholder.
		"""
		result = self._format(formatSpec)

		if (pos := result.find("%")) != -1 and result[pos + 1] != "%":  # pragma: no cover
			raise ValueError(f"Unknown format specifier '%{result[pos + 1]}' in '{formatSpec}'.")

		return result.replace("%%", "%")

	def __repr__(self) -> str:
		"""
		Return a normalized string representation of this version number.

		.. note::

		   A prefix doesn't contribute to the version number's value, therefore it's not part of the normalized form. Use
		   :meth:`__str__` to render a version number including its prefix.

		:returns: Raw version number representation without a prefix.
		"""
		epoch = f"{self._epoch}{self._EPOCH_SEPARATOR}" if Parts.Epoch in self._parts else ""

		return f"{epoch}{self._major}.{self._minor}.{self._micro}"

	def __str__(self) -> str:
		"""
		Return a string representation of this version number.

		:returns: Version number representation.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
		result += f"{self._epoch}{self._EPOCH_SEPARATOR}" if Parts.Epoch in self._parts else ""
		result += f"{self._major}"  # major is always present
		result += f".{self._minor}" if Parts.Minor in self._parts else ""
		result += f".{self._micro}" if Parts.Micro in self._parts else ""
		result += f".{self._build}" if Parts.Build in self._parts else ""
		if self._releaseLevel is ReleaseLevel.Development:
			result += "-dev"
		elif self._releaseLevel is ReleaseLevel.Alpha:
			result += f".alpha{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.Beta:
			result += f".beta{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.Gamma:
			result += f".gamma{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.ReleaseCandidate:
			result += f".rc{self._releaseNumber}"
		result += f".post{self._post}" if Parts.Post in self._parts else ""
		result += f".dev{self._dev}" if Parts.Dev in self._parts else ""
		result += f"+{self._postfix}" if Parts.Postfix in self._parts else ""

		return result


@export
class PythonVersion(SemanticVersion):
	"""
	Represents a Python version.
	"""

	#: :pep:`440` writes an epoch ``v2!1.2.3``, where Debian and the default write ``2:1.2.3``.
	#:
	#: Deliberately **not** annotated: :class:`~pyTooling.MetaClasses.ExtendedType` applies an annotated class
	#: attribute *after* ``__init_subclass__`` has run, so an annotation here would hide the separator from
	#: :meth:`SemanticVersion.__init_subclass__` and leave this class parsing ``:``. A testcase pins that the
	#: pattern really was rebuilt.
	_EPOCH_SEPARATOR = "!"

	@classmethod
	def FromSysVersionInfo(cls) -> PythonVersion:
		"""
		Create a Python version from :data:`sys.version_info`.

		:returns:                 A PythonVersion instance of the current Python interpreter's version.
		:raises ToolingException: If the interpreter reports a release level this class doesn't know.
		"""
		from sys import version_info

		if version_info.releaselevel == "final":
			rl = ReleaseLevel.Final
			number = None
		else:  # pragma: no cover
			number = version_info.serial

			if version_info.releaselevel == "alpha":
				rl = ReleaseLevel.Alpha
			elif version_info.releaselevel == "beta":
				rl = ReleaseLevel.Beta
			elif version_info.releaselevel == "candidate":
				rl = ReleaseLevel.ReleaseCandidate
			else:  # pragma: no cover
				raise ToolingException(f"Unsupported release level '{version_info.releaselevel}'.")

		return cls(version_info.major, version_info.minor, version_info.micro, level=rl, number=number)

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()

	def __str__(self) -> str:
		"""
		Return a string representation of this version number.

		:returns: Version number representation.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
		result += f"{self._epoch}{self._EPOCH_SEPARATOR}" if Parts.Epoch in self._parts else ""
		result += f"{self._major}"  # major is always present
		result += f".{self._minor}" if Parts.Minor in self._parts else ""
		result += f".{self._micro}" if Parts.Micro in self._parts else ""
		if self._releaseLevel is ReleaseLevel.Alpha:
			result += f"a{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.Beta:
			result += f"b{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.Gamma:
			result += f"c{self._releaseNumber}"
		elif self._releaseLevel is ReleaseLevel.ReleaseCandidate:
			result += f"rc{self._releaseNumber}"
		result += f".post{self._post}" if Parts.Post in self._parts else ""
		result += f".dev{self._dev}" if Parts.Dev in self._parts else ""
		result += f"+{self._postfix}" if Parts.Postfix in self._parts else ""

		return result


@export
class CalendarVersion(Version):
	"""Representation of a calendar version number like ``2021.10``."""

	_PARTCOUNT: ClassVar[int] = 3   #: Number of numeric parts a version number of this class can carry.

	_PATTERN: ClassVar[Pattern] = re_compile(
		r"^"
		r"(?P<prefix>rev|REV|[vViIrR])?"
		r"(?P<major>\d+)"
		r"(?:\.(?P<minor>\d+))?"
		r"(?:\.(?P<micro>\d+))?"
		r"$"
	)  #: Regular expression to parse a calendar version from a string.

	def __init__(
		self,
		major: int,
		minor: Nullable[int] = None,
		micro: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None,
		postfix: Nullable[str] = None
	) -> None:
		"""
		Initializes a calendar version number representation.

		:param major:       Major number part of the version number.
		:param minor:       Optional, minor number part of the version number.
		:param micro:       Optional, micro (patch) number part of the version number.
		:param build:       Optional, build number part of the version number.
		:param flags:       Optional, the version number's flags.
		:param prefix:      Optional, the version number's prefix.
		:param postfix:     Optional, the version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(major, minor, micro, build=build, postfix=postfix, prefix=prefix, flags=flags)

	@classmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[[CalendarVersion], bool]] = None) -> CalendarVersion:
		"""
		Parse a version string and return a :class:`CalendarVersion` instance.

		Allowed prefix characters:

		* ``v|V`` - version, public version, public release
		* ``i|I`` - internal version, internal release
		* ``r|R`` - release, revision
		* ``rev|REV`` - revision

		A version number carries up to :attr:`_PARTCOUNT` numeric parts. :class:`YearMonthVersion`,
		:class:`YearWeekVersion` and :class:`YearReleaseVersion` describe two parts, so a third part is rejected for
		them.

		:param versionString:          The version string to parse.
		:param validator:              Optional, a validation function.
		:returns:                      An object representing a calendar version.
		:raises TypeError:             If parameter ``versionString`` is not a string.
		:raises ValueError:            If parameter ``versionString`` is None or empty.
		:raises ValueError:            If parameter ``versionString`` isn't a calendar version number. |br|
		                               It may carry one of the prefixes ``v``, ``i``, ``r`` or ``rev``, e.g.
		                               ``v2024.04``.
		:raises ValueError:            If parameter ``versionString`` has more parts than the class describes. |br|
		                               Use :class:`CalendarVersion` or :class:`YearMonthDayVersion` to parse a
		                               three-part calendar version number.
		:raises VersionValidatorError: If the parsed version is rejected by ``validator``.
		"""
		if versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif not isinstance(versionString, str):
			ex = TypeError("Parameter 'versionString' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(versionString)}'.")
			raise ex
		elif (versionString := versionString.strip()) == "":
			raise ValueError("Parameter 'versionString' is empty.")

		if (match := cls._PATTERN.match(versionString)) is None:
			ex = ValueError(f"Syntax error in parameter 'versionString': '{versionString}'")
			ex.add_note(f"A calendar version number is made of up to {cls._PARTCOUNT} numeric parts, e.g. '2024.04'.")
			ex.add_note("It may carry one of the prefixes 'v', 'i', 'r' or 'rev', e.g. 'v2024.04'.")
			raise ex

		prefix = match["prefix"]
		minor = match["minor"]
		micro = match["micro"]

		if micro is not None and cls._PARTCOUNT < 3:
			ex = ValueError(f"Version number '{versionString}' has 3 parts, but '{cls.__name__}' describes {cls._PARTCOUNT}.")
			ex.add_note("Use 'CalendarVersion' or 'YearMonthDayVersion' to parse a 3-part calendar version number.")
			raise ex

		numbers = [int(match["major"])]
		if minor is not None:
			numbers.append(int(minor))
			if micro is not None:
				numbers.append(int(micro))

		version = cls(*numbers, flags=Flags.Clean, prefix=prefix if prefix != "" else None)

		if validator is not None and not validator(version):
			raise VersionValidatorError(f"Failed to validate version string '{versionString}'.", version=version)

		return version

	@readonly
	def Year(self) -> int:
		"""
		Read-only property to access the year part.

		:returns: The year part.
		"""
		return self._major

	def _equal(self, left: CalendarVersion, right: CalendarVersion) -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`CalendarVersion` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (left._major == right._major) and (left._minor == right._minor) and (left._micro == right._micro)

	def _compare(self, left: CalendarVersion, right: CalendarVersion) -> Nullable[bool]:
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

		if left._micro < right._micro:
			return True
		elif left._micro > right._micro:
			return False

		return None

	def __eq__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__eq__(other)

	def __ne__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__ne__(other)

	def __lt__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__lt__(other)

	def __le__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__le__(other)

	def __gt__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__gt__(other)

	def __ge__(self, other: Any) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`CalendarVersion`, string or integer.
		"""
		return super().__ge__(other)

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()

	def __format__(self, formatSpec: str) -> str:
		"""
		Return a string representation of this version number according to the format specification.

		.. topic:: Format Specifiers

		   * ``%M`` - major number (year)
		   * ``%m`` - minor number (month/week)
		   * ``%u`` - micro number (day)

		:param formatSpec: The format specification.
		:returns:          Formatted version number.
		"""
		if formatSpec == "":
			return self.__str__()

		result = formatSpec
		# result = result.replace("%P", str(self._prefix))
		result = result.replace("%M", str(self._major))
		result = result.replace("%m", str(self._minor))
		result = result.replace("%u", str(self._micro))
		# result = result.replace("%p", str(self._pre))

		return result.replace("%%", "%")

	def __repr__(self) -> str:
		"""
		Return a normalized string representation of this version number.

		.. note::

		   A prefix doesn't contribute to the version number's value, therefore it's not part of the normalized form. Use
		   :meth:`__str__` to render a version number including its prefix.

		:returns: Raw version number representation without a prefix.
		"""
		result = f"{self._major}.{self._minor}"
		result += f".{self._micro}" if Parts.Micro in self._parts else ""

		return result

	def __str__(self) -> str:
		"""
		Return a string representation of this version number with only the present parts.

		:returns: Version number representation including a prefix.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
		result += f"{self._major}"
		result += f".{self._minor}" if Parts.Minor in self._parts else ""
		result += f".{self._micro}" if Parts.Micro in self._parts else ""

		return result


@export
class YearMonthVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and month like ``2021.10``."""

	_PARTCOUNT: ClassVar[int] = 2   #: A version number of this class carries year and month.

	def __init__(
		self,
		year: int,
		month: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None,
		postfix: Nullable[str] = None
	) -> None:
		"""
		Initializes a year-month version number representation.

		:param year:        Year part of the version number.
		:param month:       Optional, month part of the version number.
		:param build:       Optional, build number part of the version number.
		:param flags:       Optional, the version number's flags.
		:param prefix:      Optional, the version number's prefix.
		:param postfix:     Optional, the version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(year, month, None, build, flags, prefix, postfix)

	@readonly
	def Month(self) -> int:
		"""
		Read-only property to access the month part.

		:returns: The month part.
		"""
		return self._minor

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()


@export
class YearWeekVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and week like ``2021.47``."""

	_PARTCOUNT: ClassVar[int] = 2   #: A version number of this class carries year and week.

	def __init__(
		self,
		year: int,
		week: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None,
		postfix: Nullable[str] = None
	) -> None:
		"""
		Initializes a year-week version number representation.

		:param year:        Year part of the version number.
		:param week:        Optional, week part of the version number.
		:param build:       Optional, build number part of the version number.
		:param flags:       Optional, the version number's flags.
		:param prefix:      Optional, the version number's prefix.
		:param postfix:     Optional, the version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(year, week, None, build, flags, prefix, postfix)

	@readonly
	def Week(self) -> int:
		"""
		Read-only property to access the week part.

		:returns: The week part.
		"""
		return self._minor

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()


@export
class YearReleaseVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and release per year like ``2021.2``."""

	_PARTCOUNT: ClassVar[int] = 2   #: A version number of this class carries year and release.

	def __init__(
		self,
		year: int,
		release: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None,
		postfix: Nullable[str] = None
	) -> None:
		"""
		Initializes a year-release version number representation.

		:param year:        Year part of the version number.
		:param release:     Optional, release number of the version number.
		:param build:       Optional, build number part of the version number.
		:param flags:       Optional, the version number's flags.
		:param prefix:      Optional, the version number's prefix.
		:param postfix:     Optional, the version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(year, release, None, build, flags, prefix, postfix)

	@readonly
	def Release(self) -> int:
		"""
		Read-only property to access the release number.

		:returns: The release number.
		"""
		return self._minor

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()


@export
class YearMonthDayVersion(CalendarVersion):
	"""Representation of a calendar version number made of year, month and day like ``2021.10.15``."""

	def __init__(
		self,
		year: int,
		month: Nullable[int] = None,
		day: Nullable[int] = None,
		build: Nullable[int] = None,
		flags: Flags = Flags.Clean,
		prefix: Nullable[str] = None,
		postfix: Nullable[str] = None
	) -> None:
		"""
		Initializes a year-month-day version number representation.

		:param year:        Year part of the version number.
		:param month:       Optional, month part of the version number.
		:param day:         Optional, day part of the version number.
		:param build:       Optional, build number part of the version number.
		:param flags:       Optional, the version number's flags.
		:param prefix:      Optional, the version number's prefix.
		:param postfix:     Optional, the version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type integer.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type integer.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type integer.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type integer.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type string.
		:raises TypeError:  If parameter 'postfix' is not of type string.
		"""
		super().__init__(year, month, day, build, flags, prefix, postfix)

	@readonly
	def Month(self) -> int:
		"""
		Read-only property to access the month part.

		:returns: The month part.
		"""
		return self._minor

	@readonly
	def Day(self) -> int:
		"""
		Read-only property to access the day part.

		:returns: The day part.
		"""
		return self._micro

	def __hash__(self) -> int:
		"""
		Compute a hash for this version number.

		The derived class re-implements :meth:`__eq__`, so Python would otherwise drop the inherited hash and make the
		version unhashable.

		:returns: Hash of this version number.
		"""
		return super().__hash__()


V = TypeVar("V", bound=Version)

@export
class RangeBoundHandling(Flag):
	"""
	A flag defining how to handle bounds in a range.

	If a bound is inclusive, the bound's value is within the range. If a bound is exclusive, the bound's value is the
	first value outside the range. Inclusive and exclusive behavior can be mixed for lower and upper bounds.
	"""
	BothBoundsInclusive = 0  #: Lower and upper bound are inclusive.
	LowerBoundInclusive = 0  #: Lower bound is inclusive.
	UpperBoundInclusive = 0  #: Upper bound is inclusive.
	LowerBoundExclusive = 1  #: Lower bound is exclusive.
	UpperBoundExclusive = 2  #: Upper bound is exclusive.
	BothBoundsExclusive = 3  #: Lower and upper bound are exclusive.


@export
class VersionRange(Generic[V], metaclass=ExtendedType, slots=True):
	"""
	Representation of a version range described by a lower bound and upper bound version.

	This version range works with :class:`SemanticVersion` and :class:`CalendarVersion` and its derived classes.

	A bound may be **unbound**, written as ``None``, meaning the range is open in that direction. That is how a
	dependency range like Maven's ``[1.0,)`` - *1.0 and everything after it* - is expressed, and it is what makes a
	single comparison such as ``>=1.0`` a range at all. A range unbound at both ends contains every version.

	Whether the bound itself belongs to the range is :class:`RangeBoundHandling`'s business, not the bound's, so
	each example names the comparison it stands for:

	.. code-block:: python

	   VersionRange(SemanticVersion.Parse("1.0.0"), None)   # >=1.0.0 ⟶ 1.0.0 and everything above it
	   VersionRange(None, SemanticVersion.Parse("2.0.0"))   # <=2.0.0 ⟶ everything up to 2.0.0
	   VersionRange(None, None)                             # every version
	"""
	_lowerBound:    Nullable[V]         #: Lower bound of the version range, or ``None`` if it is unbound.
	_upperBound:    Nullable[V]         #: Upper bound of the version range, or ``None`` if it is unbound.
	_boundHandling: RangeBoundHandling  #: Strategy deciding whether the bounds are part of the range.

	def __init__(
		self,
		lowerBound: Nullable[V],
		upperBound: Nullable[V],
		boundHandling: RangeBoundHandling = RangeBoundHandling.BothBoundsInclusive
	) -> None:
		"""
		Initializes a version range described by a lower and upper bound.

		Either bound may be ``None``, which leaves the range open in that direction. The checks that relate the two
		bounds - that they are compatible types, and that the lower one isn't above the upper one - can only be made
		when both are present, so they are skipped for an open bound rather than failing on it.

		:param lowerBound:    Lowest version (inclusive), or ``None`` to leave the range open downwards.
		:param upperBound:    Highest version (inclusive), or ``None`` to leave the range open upwards.
		:param boundHandling: Optional, strategy deciding whether the bounds are part of the range.
		:raises TypeError:    If parameter ``lowerBound`` is neither ``None`` nor of type :class:`Version`.
		:raises TypeError:    If parameter ``upperBound`` is neither ``None`` nor of type :class:`Version`.
		:raises TypeError:    If parameter ``lowerBound`` and ``upperBound`` are unrelated types.
		:raises ValueError:   If parameter ``lowerBound`` isn't less than or equal to ``upperBound``.
		"""
		if lowerBound is not None and not isinstance(lowerBound, Version):
			ex = TypeError("Parameter 'lowerBound' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(lowerBound)}'.")
			raise ex

		if upperBound is not None and not isinstance(upperBound, Version):
			ex = TypeError("Parameter 'upperBound' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(upperBound)}'.")
			raise ex

		if lowerBound is not None and upperBound is not None:
			if not self._AreCompatible(lowerBound, upperBound):
				ex = TypeError("Parameters 'lowerBound' and 'upperBound' are not compatible with each other.")
				ex.add_note(f"Got type '{getFullyQualifiedName(lowerBound)}' for lowerBound and "
				            f"type '{getFullyQualifiedName(upperBound)}' for upperBound.")
				raise ex

			if not (lowerBound <= upperBound):
				ex = ValueError("Parameter 'lowerBound' isn't less than parameter 'upperBound'.")
				ex.add_note(f"Got '{lowerBound}' for lowerBound and '{upperBound}' for upperBound.")
				raise ex

		self._lowerBound = lowerBound
		self._upperBound = upperBound
		self._boundHandling = boundHandling

	@property
	def LowerBound(self) -> Nullable[V]:
		"""
		Property to access the range's lower bound.

		Assigning ``None`` leaves the bound unbound, opening the range in that direction.

		:returns:           Lower bound of the version range, or ``None`` if it is unbound.
		:raises TypeError:  If an assigned value is neither ``None`` nor of type :class:`Version`.
		:raises TypeError:  If an assigned value's type is unrelated to the range's upper bound.
		:raises ValueError: If an assigned value is above the range's upper bound. |br|
		                    The bounds are only related when both are present.
		"""
		return self._lowerBound

	@LowerBound.setter
	def LowerBound(self, value: Nullable[V]) -> None:
		if value is not None and not isinstance(value, Version):
			ex = TypeError("Parameter 'value' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		if value is not None and self._upperBound is not None:
			if not self._AreCompatible(value, self._upperBound):
				ex = TypeError("Parameter 'value' is not compatible with the range's upper bound.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				ex.add_note(f"The upper bound is of type '{getFullyQualifiedName(self._upperBound)}'.")
				raise ex

			if not (value <= self._upperBound):
				ex = ValueError("Parameter 'value' isn't less than or equal to the range's upper bound.")
				ex.add_note(f"Got '{value}' for the lower bound; the upper bound is '{self._upperBound}'.")
				raise ex

		self._lowerBound = value

	@property
	def UpperBound(self) -> Nullable[V]:
		"""
		Property to access the range's upper bound.

		Assigning ``None`` leaves the bound unbound, opening the range in that direction.

		:returns:           Upper bound of the version range, or ``None`` if it is unbound.
		:raises TypeError:  If an assigned value is neither ``None`` nor of type :class:`Version`.
		:raises TypeError:  If an assigned value's type is unrelated to the range's lower bound.
		:raises ValueError: If an assigned value is below the range's lower bound. |br|
		                    The bounds are only related when both are present.
		"""
		return self._upperBound

	@UpperBound.setter
	def UpperBound(self, value: Nullable[V]) -> None:
		if value is not None and not isinstance(value, Version):
			ex = TypeError("Parameter 'value' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		if value is not None and self._lowerBound is not None:
			if not self._AreCompatible(value, self._lowerBound):
				ex = TypeError("Parameter 'value' is not compatible with the range's lower bound.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				ex.add_note(f"The lower bound is of type '{getFullyQualifiedName(self._lowerBound)}'.")
				raise ex

			if not (self._lowerBound <= value):
				ex = ValueError("Parameter 'value' isn't greater than or equal to the range's lower bound.")
				ex.add_note(f"Got '{value}' for the upper bound; the lower bound is '{self._lowerBound}'.")
				raise ex

		self._upperBound = value

	@property
	def BoundHandling(self) -> RangeBoundHandling:
		"""
		Property to access the range's bound handling strategy.

		:returns:          The range's bound handling strategy.
		:raises TypeError: If an assigned value is not of type :class:`RangeBoundHandling`.
		"""
		return self._boundHandling

	@BoundHandling.setter
	def BoundHandling(self, value: RangeBoundHandling) -> None:
		if not isinstance(value, RangeBoundHandling):
			ex = TypeError("Parameter 'value' is not of type 'RangeBoundHandling'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._boundHandling = value

	@staticmethod
	def _AreCompatible(left: Version, right: Version) -> bool:
		"""
		Check whether two versions' types can be related to each other.

		Two versions relate when they are of the same class, or when one's class derives from the other's. So a
		:class:`SemanticVersion` relates to a :class:`PythonVersion`, which derives from it, and not to a
		:class:`CalendarVersion`, which is a sibling under :class:`Version`.

		This is the single rule every part of a range applies: to its two bounds against each other, to a version
		held against them, and to a bound assigned after construction.

		:param left:  The first version.
		:param right: The second version.
		:returns:     ``True``, if the two versions' types are related.
		"""
		leftType = left.__class__
		rightType = right.__class__

		return leftType is rightType or issubclass(leftType, rightType) or issubclass(rightType, leftType)

	def _CheckCompatibility(self, other: Version) -> None:
		"""
		Check that a version can be related to this range's bounds.

		The rule is the one :meth:`__init__` applies *between* the two bounds: the same class, or one deriving from
		the other. So a range bounded by :class:`SemanticVersion` accepts a :class:`PythonVersion`, because that
		derives from it, and refuses a :class:`CalendarVersion`, which is a sibling. A range whose bounds are both
		unbound carries no type to check against, so it accepts any version.

		:param other:      The version to check against this range's bounds.
		:raises TypeError: If the version's type is unrelated to this range's bounds.
		"""
		reference = self._lowerBound if self._lowerBound is not None else self._upperBound
		if reference is None:
			return

		if not self._AreCompatible(other, reference):
			ex = TypeError("Parameter 'other' is not compatible with version range.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note(f"This range is bounded by type '{getFullyQualifiedName(reference)}'.")
			raise ex

	def __and__(self, other: Any) -> VersionRange[T]:
		"""
		Compute the intersection of two version ranges.

		Each bound of the result comes from whichever range constrains it more tightly, and is inclusive only if it
		is inclusive in *that* range. Where both ranges name the same bound value, it is inclusive only when **both**
		include it - the intersection cannot admit a version one of its operands excludes.

		:param other:       Second version range to intersect with.
		:returns:           Intersected version range.
		:raises TypeError:  If parameter 'other' is not of type :class:`VersionRange`.
		:raises TypeError:  If the two ranges' bounds are of unrelated types.
		:raises ValueError: If intersection is empty.
		"""
		if not isinstance(other, VersionRange):
			ex = TypeError("Parameter 'other' is not of type 'VersionRange'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if self._lowerBound is not None and other._lowerBound is not None:
			if not self._AreCompatible(self._lowerBound, other._lowerBound):
				ex = TypeError("Parameter 'other's LowerBound and this range's 'LowerBound' are not compatible "
				               "with each other.")
				ex.add_note(f"Got type '{getFullyQualifiedName(other._lowerBound)}' for other.LowerBound and "
				            f"type '{getFullyQualifiedName(self._lowerBound)}' for self.LowerBound.")
				raise ex

		ownLowerExclusive =     RangeBoundHandling.LowerBoundExclusive in self._boundHandling
		otherLowerExclusive =   RangeBoundHandling.LowerBoundExclusive in other._boundHandling
		ownUpperExclusive =     RangeBoundHandling.UpperBoundExclusive in self._boundHandling
		otherUpperExclusive =   RangeBoundHandling.UpperBoundExclusive in other._boundHandling

		# An unbound lower end is the lowest of all, so the other range's bound wins; likewise the highest upper one.
		# Each bound keeps the handling of the range it came from; a shared value keeps the stricter of the two.
		if self._lowerBound is None:
			lBound = other._lowerBound
			lowerExclusive = otherLowerExclusive
		elif other._lowerBound is None:
			lBound = self._lowerBound
			lowerExclusive = ownLowerExclusive
		elif self._lowerBound > other._lowerBound:
			lBound = self._lowerBound
			lowerExclusive = ownLowerExclusive
		elif other._lowerBound > self._lowerBound:
			lBound = other._lowerBound
			lowerExclusive = otherLowerExclusive
		else:
			lBound = self._lowerBound
			lowerExclusive = ownLowerExclusive or otherLowerExclusive

		if self._upperBound is None:
			uBound = other._upperBound
			upperExclusive = otherUpperExclusive
		elif other._upperBound is None:
			uBound = self._upperBound
			upperExclusive = ownUpperExclusive
		elif self._upperBound < other._upperBound:
			uBound = self._upperBound
			upperExclusive = ownUpperExclusive
		elif other._upperBound < self._upperBound:
			uBound = other._upperBound
			upperExclusive = otherUpperExclusive
		else:
			uBound = self._upperBound
			upperExclusive = ownUpperExclusive or otherUpperExclusive

		if lBound is not None and uBound is not None and not (lBound <= uBound):
			ex = ValueError("The intersection of both version ranges is empty.")
			ex.add_note(f"Got value '{lBound}' for the highest lower bound.")
			ex.add_note(f"The lowest upper bound is '{uBound}'.")
			raise ex

		boundHandling = RangeBoundHandling.BothBoundsInclusive
		if lowerExclusive:
			boundHandling |= RangeBoundHandling.LowerBoundExclusive
		if upperExclusive:
			boundHandling |= RangeBoundHandling.UpperBoundExclusive

		return self.__class__(lBound, uBound, boundHandling)

	def __lt__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is less than the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version range is less than the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		self._CheckCompatibility(other)

		if self._upperBound is None:
			return False

		return self._upperBound < other

	def __le__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is less than or equal the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version range is less than  or equal the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		self._CheckCompatibility(other)

		if self._upperBound is None:
			return False

		if RangeBoundHandling.UpperBoundExclusive in self._boundHandling:
			return self._upperBound < other

		return self._upperBound <= other

	def __gt__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is greater than the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version range is greater than the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		self._CheckCompatibility(other)

		if self._lowerBound is None:
			return False

		return self._lowerBound > other

	def __ge__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is greater than  or equal the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version range is greater than or equal the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		self._CheckCompatibility(other)

		if self._lowerBound is None:
			return False

		if RangeBoundHandling.LowerBoundExclusive in self._boundHandling:
			return self._lowerBound > other

		return self._lowerBound >= other

	def __contains__(self, version: Version) -> bool:
		"""
		Check if the version is in the version range.

		:param version:    Optional, version to check.
		:returns:          ``True``, if version is in range.
		:raises TypeError: If parameter ``version`` is not of type :class:`Version`.
		:raises TypeError: If parameter ``version``'s type is unrelated to this range's bounds. |br|
		                   The rule is the one :meth:`__init__` applies between the bounds.
		"""
		if not isinstance(version, Version):
			ex = TypeError("Parameter 'item' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		self._CheckCompatibility(version)

		# An unbound end excludes nothing, so its half of the comparison is simply not made.
		if self._lowerBound is not None:
			if RangeBoundHandling.LowerBoundExclusive in self._boundHandling:
				if not (self._lowerBound < version):
					return False
			elif not (self._lowerBound <= version):
				return False

		if self._upperBound is not None:
			if RangeBoundHandling.UpperBoundExclusive in self._boundHandling:
				if not (version < self._upperBound):
					return False
			elif not (version <= self._upperBound):
				return False

		return True


@export
class VersionSet(Generic[V], metaclass=ExtendedType, slots=True):
	"""
	Representation of an ordered set of versions.

	This version set works with :class:`SemanticVersion` and :class:`CalendarVersion` and its derived classes.
	"""
	_items: list[V]  #: An ordered list of set members.

	def __init__(self, versions: Union[Version, Iterable[V]]) -> None:
		"""
		Initializes a version set either by a single version or an iterable of versions.

		:param versions:    A single version or an iterable of versions.
		:raises ValueError: If parameter ``versions`` is None`.
		:raises TypeError:  In case of a single version, if parameter ``version`` is not of type :class:`Version`.
		:raises TypeError:  In case of an iterable, if parameter ``versions`` containes elements, which are not of type :class:`Version`.
		:raises TypeError:  If parameter ``versions`` is neither a single version nor an iterable thereof.
		"""
		if versions is None:
			raise ValueError("Parameter 'versions' is None.")

		if isinstance(versions, Version):
			self._items = [versions]
		elif isinstance(versions, abc_Iterable):
			iterator = iter(versions)
			try:
				firstVersion = next(iterator)
			except StopIteration:
				self._items = []
				return

			if not isinstance(firstVersion, Version):
				raise TypeError("First element in parameter 'versions' is not of type Version.")

			baseType = firstVersion.__class__
			for version in iterator:
				if not isinstance(version, baseType):
					raise TypeError(f"Element from parameter 'versions' is not of type {baseType.__name__}")

			self._items = list(sorted(versions))
		else:
			raise TypeError("Parameter 'versions' is not an Iterable.")

	def __and__(self, other: VersionSet[V]) -> VersionSet[T]:
		"""
		Compute intersection of two version sets.

		:param other: Second set of versions.
		:returns:     Intersection of two version sets.
		"""
		selfIterator = self.__iter__()
		otherIterator = other.__iter__()

		result = []
		try:
			selfValue = next(selfIterator)
			otherValue = next(otherIterator)

			while True:
				if selfValue < otherValue:
					selfValue = next(selfIterator)
				elif otherValue < selfValue:
					otherValue = next(otherIterator)
				else:
					result.append(selfValue)
					selfValue = next(selfIterator)
					otherValue = next(otherIterator)

		except StopIteration:
			pass

		return VersionSet(result)

	def __or__(self, other: VersionSet[V]) -> VersionSet[T]:
		"""
		Compute union of two version sets.

		:param other: Second set of versions.
		:returns:     Union of two version sets.
		"""
		selfIterator = self.__iter__()
		otherIterator = other.__iter__()

		result = []
		try:
			selfValue = next(selfIterator)
		except StopIteration:
			for otherValue in otherIterator:
				result.append(otherValue)

		try:
			otherValue = next(otherIterator)
		except StopIteration:
			for selfValue in selfIterator:
				result.append(selfValue)

		while True:
			if selfValue < otherValue:
				result.append(selfValue)
				try:
					selfValue = next(selfIterator)
				except StopIteration:
					result.append(otherValue)
					for otherValue in otherIterator:
						result.append(otherValue)

					break
			elif otherValue < selfValue:
				result.append(otherValue)
				try:
					otherValue = next(otherIterator)
				except StopIteration:
					result.append(selfValue)
					for selfValue in selfIterator:
						result.append(selfValue)

					break
			else:
				result.append(selfValue)
				try:
					selfValue = next(selfIterator)
				except StopIteration:
					for otherValue in otherIterator:
						result.append(otherValue)

					break

				try:
					otherValue = next(otherIterator)
				except StopIteration:
					for selfValue in selfIterator:
						result.append(selfValue)

					break

		return VersionSet(result)

	def __lt__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is less than the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version set is less than the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[-1] < other

	def __le__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is less than or equal the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version set is less than or equal the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[-1] <= other

	def __gt__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is greater than the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version set is greater than the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[0] > other

	def __ge__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is greater than or equal the second operand (version).

		:param other:      Operand to compare against.
		:returns:          ``True``, if version set is greater than or equal the second operand (version).
		:raises TypeError: If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError("Parameter 'other' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[0] >= other

	def __contains__(self, version: V) -> bool:
		"""
		Checks if the version a member of the set.

		:param version: Optional, the version to check.
		:returns:       ``True``, if the version is a member of the set.
		"""
		return version in self._items

	def __len__(self) -> int:
		"""
		Returns the number of members in the set.

		:returns: Number of set members.
		"""
		return len(self._items)

	def __iter__(self) -> Iterator[V]:
		"""
		Returns an iterator to iterate all versions of this set from lowest to highest.

		:returns: Iterator to iterate versions.
		"""
		return self._items.__iter__()

	def __getitem__(self, index: int) -> V:
		"""
		Access to a version of a set by index.

		:param index: The index of the version to access.
		:returns:     The indexed version.

		.. hint::

		   Versions are ordered from lowest to highest version number.
		"""
		return self._items[index]


#: The :class:`Version` class under a name no constraint shadows with a property of its own.
_VersionType = Version


@export
class VersionComparison(Enum):
	"""
	The comparison one constraint of a :class:`VersionExpression` applies to a version.

	The six ordering comparisons mean the same thing in every packaging ecosystem, even where the spelling differs -
	Debian writes ``<<`` for :attr:`LessThan` and npm writes ``=`` for :attr:`Equal`. Each member's value is its
	*canonical* spelling, which is what a constraint renders as; a dialect maps its own spellings onto these members
	while parsing.
	"""

	Equal              = "=="  #: The version has to be equal to the constraint's version.
	Unequal            = "!="  #: The version must not be the constraint's version.
	LessThan           = "<"   #: The version has to be lower than the constraint's version.
	LessThanOrEqual    = "<="  #: The version must not be higher than the constraint's version.
	GreaterThan        = ">"   #: The version has to be higher than the constraint's version.
	GreaterThanOrEqual = ">="  #: The version must not be lower than the constraint's version.
	CompatibleRelease  = "~="  #: The version has to be compatible with the constraint's version (:pep:`440`).
	Caret              = "^"   #: The version must not change the constraint's leftmost non-zero part (npm).
	Tilde              = "~"   #: The version must not change the constraint's minor part (npm).

	def __str__(self) -> str:
		"""
		Return the operator in its canonical spelling.

		:returns: The comparison's operator.
		"""
		return self.value


@export
class VersionConstraint(Generic[V], metaclass=ExtendedType, slots=True):
	"""
	One comparison of a :class:`VersionExpression`, such as ``>=1.2.0``.

	A constraint is a container of the versions satisfying it, so membership is asked with ``in``:

	.. code-block:: python

	   constraint = VersionConstraint(VersionComparison.GreaterThanOrEqual, SemanticVersion.Parse("1.2.0"))  # >=1.2.0
	   SemanticVersion.Parse("1.5.0") in constraint   # True

	.. seealso::

	   :class:`CompatibleVersionConstraint`
	      |rarr| The constraint implementing :attr:`~VersionComparison.CompatibleRelease`.
	"""

	_comparison: VersionComparison  #: The comparison this constraint applies.
	_version:    V                  #: The version the compared version is held against.

	def __init__(self, comparison: VersionComparison, version: V) -> None:
		"""
		Initialize a constraint from a comparison and the version it compares against.

		:param comparison:  The comparison to apply.
		:param version:     The version to compare against.
		:raises TypeError:  If parameter 'comparison' is not of type :class:`VersionComparison`.
		:raises TypeError:  If parameter 'version' is not of type :class:`Version`.
		:raises ValueError: If parameter 'comparison' is a shorthand like
		                    :attr:`~VersionComparison.CompatibleRelease`. |br|
		                    Use the matching :class:`RangeVersionConstraint`, which derives an upper bound from the
		                    version.
		"""
		if not isinstance(comparison, VersionComparison):
			ex = TypeError("Parameter 'comparison' is not of type 'VersionComparison'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(comparison)}'.")
			raise ex

		if not isinstance(version, Version):
			ex = TypeError("Parameter 'version' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		if comparison in _SHORTHAND_COMPARISONS and not isinstance(self, RangeVersionConstraint):
			ex = ValueError(f"Comparison '{comparison.name}' is not a plain comparison.")
			ex.add_note("Use the matching 'RangeVersionConstraint', which derives an upper bound from the version.")
			raise ex

		self._comparison = comparison
		self._version =    version

	@readonly
	def Comparison(self) -> VersionComparison:
		"""
		Read-only property to access the comparison this constraint applies (:attr:`_comparison`).

		:returns: The comparison.
		"""
		return self._comparison

	@readonly
	def Version(self) -> V:
		"""
		Read-only property to access the version this constraint compares against (:attr:`_version`).

		:returns: The version.
		"""
		return self._version

	def __contains__(self, version: V) -> bool:
		"""
		Check if a version satisfies this constraint.

		:param version:     The version to check.
		:returns:           ``True``, if the version satisfies the constraint.
		:raises TypeError:  If parameter 'version' is not of type :class:`Version`.
		:raises ValueError: If this constraint carries a comparison a plain constraint cannot apply. |br|
		                    A shorthand is implemented by a :class:`RangeVersionConstraint`.
		"""
		if not isinstance(version, Version):
			ex = TypeError("Parameter 'version' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		if self._comparison is VersionComparison.Equal:
			return version == self._version
		elif self._comparison is VersionComparison.Unequal:
			return version != self._version
		elif self._comparison is VersionComparison.LessThan:
			return version < self._version
		elif self._comparison is VersionComparison.LessThanOrEqual:
			return version <= self._version
		elif self._comparison is VersionComparison.GreaterThan:
			return version > self._version
		elif self._comparison is VersionComparison.GreaterThanOrEqual:
			return version >= self._version

		ex = ValueError(f"Comparison '{self._comparison.name}' cannot be applied by a plain constraint.")
		ex.add_note("A shorthand is implemented by a 'RangeVersionConstraint'.")
		raise ex

	def ToVersionRange(self) -> VersionRange[_VersionType]:
		"""
		Convert this constraint into the :class:`VersionRange` it describes.

		Five of the six comparisons are intervals once a bound may be unbound:

		* ``>=1.2.0`` is ``[1.2.0, )``,
		* ``>1.2.0`` is ``(1.2.0, )``,
		* ``<=2.0.0`` is ``( , 2.0.0]``,
		* ``<2.0.0`` is ``( , 2.0.0)``,
		* ``==1.2.0`` is ``[1.2.0, 1.2.0]``, a range of exactly one version.

		:attr:`~VersionComparison.Unequal` is the exception and has no range: the complement of a single version is
		not an interval but a *union* of two, one below it and one above. That is why an expression keeps both
		representations rather than being replaced by a range.

		:returns:           The range of versions satisfying this constraint.
		:raises ValueError: If this constraint is an :attr:`~VersionComparison.Unequal`, which no single range
		                    describes. |br|
		                    The complement of a version is a union of two intervals.
		"""
		if self._comparison is VersionComparison.Equal:
			return VersionRange(self._version, self._version)
		elif self._comparison is VersionComparison.GreaterThanOrEqual:
			return VersionRange(self._version, None)
		elif self._comparison is VersionComparison.GreaterThan:
			return VersionRange(self._version, None, RangeBoundHandling.LowerBoundExclusive)
		elif self._comparison is VersionComparison.LessThanOrEqual:
			return VersionRange(None, self._version)
		elif self._comparison is VersionComparison.LessThan:
			return VersionRange(None, self._version, RangeBoundHandling.UpperBoundExclusive)

		ex = ValueError(f"Comparison '{self._comparison.name}' describes no single version range.")
		ex.add_note("The complement of a version is a union of two intervals, which a 'VersionRange' cannot hold.")
		raise ex

	def __str__(self) -> str:
		"""
		Return the constraint in its canonical spelling.

		:returns: The operator followed by the version.
		"""
		return f"{self._comparison}{self._version}"


#: The comparisons a plain :class:`VersionConstraint` cannot express, because each derives an upper bound.
_SHORTHAND_COMPARISONS = (
	VersionComparison.CompatibleRelease,
	VersionComparison.Caret,
	VersionComparison.Tilde,
)


@export
class RangeVersionConstraint(VersionConstraint[V]):
	"""
	Base-class of the shorthand constraints meaning *at least this version, and below a derived bound*.

	Every packaging ecosystem has one of these, spells it differently, and derives its upper bound by a **different**
	rule:

	* :pep:`440` writes ``~=``,
	* npm writes ``^`` and ``~``,
	* RubyGems writes ``~>``.

	The rule is the only thing that differs, so it is what a derived class supplies in :meth:`_DeriveUpperBound`.

	.. seealso::

	   :class:`CompatibleVersionConstraint`
	      |rarr| :pep:`440`'s ``~=``.
	   :class:`CaretVersionConstraint`
	      |rarr| npm's ``^``.
	   :class:`TildeVersionConstraint`
	      |rarr| npm's ``~``.
	"""

	_upperBound: SemanticVersion  #: The first version outside the constraint, derived from the written version.

	def __init__(self, comparison: VersionComparison, version: V) -> None:
		"""
		Initialize a shorthand constraint and derive its upper bound.

		:param comparison:  The shorthand comparison this constraint applies.
		:param version:     The version the shorthand is written with.
		:raises TypeError:  If parameter 'version' is not of type :class:`SemanticVersion`. |br|
		                    An upper bound is derived from the version's parts, which only a semantic version has.
		:raises ValueError: If the version has too few parts for this shorthand.
		"""
		if not isinstance(version, SemanticVersion):
			ex = TypeError("Parameter 'version' is not of type 'SemanticVersion'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		super().__init__(comparison, version)

		self._upperBound = self._DeriveUpperBound(version)

	@abstractmethod
	def _DeriveUpperBound(self, version: SemanticVersion) -> SemanticVersion:  # type: ignore[empty-body]
		"""
		Derive the first version outside this constraint from the version it is written with.

		The bound has to be built in the written version's **epoch**. A bound left in epoch 0 outranks nothing, so
		the constraint would match no version at all - not even the one it was written with.

		:param version:     The version the shorthand is written with, always a semantic version.
		:returns:           The exclusive upper bound, in the same epoch as ``version``.
		:raises ValueError: If the version has too few parts for this shorthand.
		"""

	@readonly
	def UpperBound(self) -> SemanticVersion:
		"""
		Read-only property to access the first version outside this constraint (:attr:`_upperBound`).

		:returns: The exclusive upper bound derived from the written version.
		"""
		return self._upperBound

	def __contains__(self, version: V) -> bool:
		"""
		Check if a version is within this constraint.

		:param version:    The version to check.
		:returns:          ``True``, if the version is at least the written one and below the derived upper bound.
		:raises TypeError: If parameter 'version' is not of type :class:`Version`.
		"""
		if not isinstance(version, Version):
			ex = TypeError("Parameter 'version' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		return self._version <= version < self._upperBound

	def ToVersionRange(self) -> VersionRange[_VersionType]:
		"""
		Convert this constraint into the :class:`VersionRange` it describes.

		A shorthand constraint knows both of its bounds - the written version is the inclusive lower one, the derived
		bound the exclusive upper one - so the conversion is exact and loses nothing.

		:returns: The range of versions satisfying this constraint.
		"""
		return VersionRange(
			self._version,
			self._upperBound,
			RangeBoundHandling.LowerBoundInclusive | RangeBoundHandling.UpperBoundExclusive
		)


@export
class CompatibleVersionConstraint(RangeVersionConstraint[V]):
	"""
	The *compatible release* constraint, written ``~=`` by :pep:`440`.

	The last part written may move, the one to its left may not: ``~=1.2.3`` is ``<1.3``, ``~=1.2`` is ``<2`` and
	``~=1.2.3.4`` is ``<1.2.4``. The written version therefore needs at least two parts - ``~=1`` would say nothing
	that ``>=1`` doesn't, and :pep:`440` rejects it for that reason.

	.. code-block:: python

	   constraint = CompatibleVersionConstraint(PythonVersion.Parse("1.2.3"))
	   PythonVersion.Parse("1.2.9") in constraint   # True
	   PythonVersion.Parse("1.3.0") in constraint   # False
	"""

	def __init__(self, version: V) -> None:
		"""
		Initialize a compatible-release constraint from the version it is written with.

		:param version: The version to be compatible with, with at least two parts.
		"""
		super().__init__(VersionComparison.CompatibleRelease, version)

	def _DeriveUpperBound(self, version: SemanticVersion) -> SemanticVersion:
		"""
		Drop the last part written and increment the one that becomes the last.

		:param version:     The version the shorthand is written with.
		:returns:           The exclusive upper bound.
		:raises ValueError: If the version has fewer than two parts.
		"""
		versionType = version.__class__
		epoch =       version.Epoch if Parts.Epoch in version._parts else None
		if Parts.Build in version._parts:
			return versionType(version.Major, version.Minor, version.Patch + 1, epoch=epoch)
		elif Parts.Micro in version._parts:
			return versionType(version.Major, version.Minor + 1, epoch=epoch)
		elif Parts.Minor in version._parts:
			return versionType(version.Major + 1, epoch=epoch)

		ex = ValueError(f"Version '{version}' has too few parts for a compatible release.")
		ex.add_note("'~=1' would mean the same as '>=1'; write at least a major and a minor part.")
		raise ex


@export
class CaretVersionConstraint(RangeVersionConstraint[V]):
	"""
	npm's ``^``: the version must not change the **leftmost non-zero** part of the one written.

	``^1.2.3`` is ``<2.0.0``, but ``^0.2.3`` is ``<0.3.0`` and ``^0.0.3`` is ``<0.0.4`` - below 1.0.0 npm treats
	each part as breaking, which is what makes this different from :class:`TildeVersionConstraint`. A part that was
	not written cannot be the pivot, so ``^0`` is ``<1.0.0`` while ``^0.0`` is ``<0.1.0``.

	.. note::

	   npm excludes pre-releases of the upper bound by writing it ``<2.0.0-0``. That distinction is not modelled
	   here; a pre-release of the bound is compared by :class:`SemanticVersion`'s own ordering.
	"""

	def __init__(self, version: V) -> None:
		"""
		Initialize a caret constraint from the version it is written with.

		:param version: The version to be compatible with.
		"""
		super().__init__(VersionComparison.Caret, version)

	def _DeriveUpperBound(self, version: SemanticVersion) -> SemanticVersion:
		"""
		Increment the leftmost non-zero part that was actually written.

		:param version: The version the shorthand is written with.
		:returns:       The exclusive upper bound.
		"""
		versionType = version.__class__
		epoch =       version.Epoch if Parts.Epoch in version._parts else None
		if version.Major != 0 or Parts.Minor not in version._parts:
			return versionType(version.Major + 1, epoch=epoch)
		elif version.Minor != 0 or Parts.Micro not in version._parts:
			return versionType(0, version.Minor + 1, epoch=epoch)

		return versionType(0, 0, version.Patch + 1, epoch=epoch)


@export
class TildeVersionConstraint(RangeVersionConstraint[V]):
	"""
	npm's ``~``: the version must not change the minor part of the one written.

	``~1.2.3`` and ``~1.2`` are both ``<1.3.0``. Only when no minor part was written does the major one become the
	pivot, so ``~1`` is ``<2.0.0``.

	This is **not** :pep:`440`'s ``~=``: the two agree on ``~1.2.3`` and disagree on ``~1.2``, which npm reads as
	``<1.3.0`` and :pep:`440` as ``<2``.
	"""

	def __init__(self, version: V) -> None:
		"""
		Initialize a tilde constraint from the version it is written with.

		:param version: The version to be compatible with.
		"""
		super().__init__(VersionComparison.Tilde, version)

	def _DeriveUpperBound(self, version: SemanticVersion) -> SemanticVersion:
		"""
		Increment the minor part, or the major one when no minor part was written.

		:param version: The version the shorthand is written with.
		:returns:       The exclusive upper bound.
		"""
		versionType = version.__class__
		epoch =       version.Epoch if Parts.Epoch in version._parts else None
		if Parts.Minor in version._parts:
			return versionType(version.Major, version.Minor + 1, epoch=epoch)

		return versionType(version.Major + 1, epoch=epoch)



def _BuildConstraintPattern(
	operators:   dict[str, VersionComparison],
	separators:  str,
	versionType: type[Version]
) -> Pattern[str]:
	"""
	Build the pattern matching one constraint of a :class:`VersionExpression` dialect.

	The operators are alternated longest-first, so ``>=`` wins over ``>`` and ``~=`` over any single character. The
	operator and its version are matched *together*, with whitespace allowed between them, which is what lets
	whitespace separate constraints without splitting ``>= 1.2.0`` in half.

	A version may hold none of the characters the dialect's operators are built from, and none of its separators, so
	those are excluded from it. Without that the optional operator group would let ``>=1.2.0 <2.0.0`` read its second
	constraint as the *version* ``<2.0.0``.

	The **epoch separator is the exception** and stays allowed: :pep:`440` writes an epoch ``1!1.0``, and ``!`` is
	also the first character of ``!=``. Excluding it would cut ``>=1!1.0`` short at the epoch. The operator
	alternation is tried before the version at every position, so ``!=`` is still read as an operator wherever a
	constraint can begin.

	This is a function rather than a method, so :class:`VersionExpression` can call it in its own class body. A
	dialect derived from it is served by :meth:`VersionExpression.__init_subclass__`.

	:param operators:   The dialect's operator spellings.
	:param separators:  The dialect's constraint separators.
	:param versionType: The dialect's version class, which names the epoch separator to keep.
	:returns:           The pattern, with the operator as group 1 and the version as group 2.
	"""
	alternation = "|".join(re_escape(operator) for operator in sorted(operators, key=len, reverse=True))
	excluded =    (set("".join(operators)) | set(separators)) - set(versionType._EPOCH_SEPARATOR)

	return re_compile(rf"({alternation})?\s*([^\s{re_escape("".join(sorted(excluded)))}]+)")


@export
class VersionExpression(Generic[V], metaclass=ExtendedType, slots=True):
	"""
	A conjunction of :class:`VersionConstraint`\\ s, such as ``>=1.2.0,<2.0.0``.

	Every constraint has to be satisfied, which is what separating them means in every packaging ecosystem that has
	the notion. An expression with **no** constraints matches every version, so *no version restriction* can be
	represented rather than special-cased by its callers.

	.. code-block:: python

	   expression = VersionExpression.Parse(">=1.2.0,<2.0.0")
	   SemanticVersion.Parse("1.5.0") in expression   # True
	   SemanticVersion.Parse("2.0.0") in expression   # False

	   SemanticVersion.Parse("4.2.0") in VersionExpression.Parse("")   # True - no constraints matches anything

	This class is the **ecosystem-neutral** dialect: the six ordering comparisons in their canonical spelling,
	separated by commas or whitespace. An ecosystem that spells its operators differently, or adds a shorthand,
	derives from it and overrides :attr:`_OPERATORS`, :attr:`_SEPARATORS`, :attr:`_VERSION_TYPE` or
	:attr:`_SHORTHANDS`. A dialect is data, not behaviour.

	.. seealso::

	   :class:`PythonVersionExpression`
	      |rarr| The dialect :pep:`440` defines, which a Python requirement file writes.
	"""

	#: Operator spellings this dialect accepts, mapped onto the comparison they mean.
	_OPERATORS: ClassVar[dict[str, VersionComparison]] = {
		"==": VersionComparison.Equal,
		"!=": VersionComparison.Unequal,
		"<=": VersionComparison.LessThanOrEqual,
		">=": VersionComparison.GreaterThanOrEqual,
		"<":  VersionComparison.LessThan,
		">":  VersionComparison.GreaterThan,
	}

	#: Characters separating one constraint from the next. Whitespace always separates as well.
	_SEPARATORS: ClassVar[str] = ","

	#: The :class:`Version` class this dialect parses its versions as, unless a caller names another.
	_VERSION_TYPE: ClassVar[type[Version]] = SemanticVersion

	#: The class each shorthand comparison is built as. A comparison absent here is a plain
	#: :class:`VersionConstraint`; the neutral dialect has no shorthand at all.
	_SHORTHANDS: ClassVar[dict[VersionComparison, type]] = {}

	#: This dialect's compiled constraint pattern, built from the three tables above. A derived dialect gets its own
	#: in :meth:`__init_subclass__`.
	_CONSTRAINT_PATTERN: ClassVar[Pattern[str]] = _BuildConstraintPattern(_OPERATORS, _SEPARATORS, _VERSION_TYPE)

	_constraints: tuple[VersionConstraint[V], ...]  #: The constraints a version has to satisfy, all of them.

	def __init__(self, constraints: Iterable[VersionConstraint[V]] = ()) -> None:
		"""
		Initialize an expression from its constraints.

		:param constraints: Optional, the constraints a version has to satisfy. None of them means *any version*.
		:raises ValueError: If parameter 'constraints' is None.
		:raises TypeError:  If parameter 'constraints' is not iterable.
		:raises TypeError:  If parameter 'constraints' contains an item that is not a :class:`VersionConstraint`.
		"""
		if constraints is None:
			raise ValueError("Parameter 'constraints' is None.")
		elif not isinstance(constraints, abc_Iterable):
			ex = TypeError("Parameter 'constraints' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(constraints)}'.")
			raise ex

		items = tuple(constraints)
		for constraint in items:
			if not isinstance(constraint, VersionConstraint):
				ex = TypeError("Parameter 'constraints' contains an item that is not of type 'VersionConstraint'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(constraint)}'.")
				raise ex

		self._constraints = items

	def __init_subclass__(cls, **kwargs: Any) -> None:
		"""
		Compile the constraint pattern of a newly defined dialect.

		A dialect is data: its operators, its separators and its version type are class variables, so its pattern is
		settled once the class body has been read and is built here instead of on every :meth:`Parse`.

		:param kwargs: Keyword arguments passed on to the base implementation.
		"""
		super().__init_subclass__(**kwargs)

		cls._CONSTRAINT_PATTERN = _BuildConstraintPattern(cls._OPERATORS, cls._SEPARATORS, cls._VERSION_TYPE)

	@classmethod
	def Parse(cls, expression: Nullable[str], versionType: Nullable[type[Version]] = None) -> Self:
		"""
		Parse an expression such as ``>=1.2.0,<2.0.0`` into its constraints.

		A constraint without an operator is an equality, so ``1.2.0`` and ``==1.2.0`` are the same statement. An
		empty expression yields an expression with no constraints, which every version satisfies - that is how *no
		version restriction* is written.

		The expression is *scanned* rather than split, so a dialect separating constraints by whitespace does not
		break a constraint that has whitespace after its operator.

		:param expression:  The expression to parse, or ``None`` for *any version*.
		:param versionType: Optional, the :class:`Version` class the versions are parsed as. Defaults to the
		                    dialect's :attr:`_VERSION_TYPE`.
		:returns:           The parsed expression.
		:raises TypeError:  If parameter 'expression' is not a string.
		:raises ValueError: If the expression holds input this dialect doesn't accept. |br|
		                    The note names the operators this dialect accepts.
		:raises ValueError: If a version in the expression can't be parsed. |br|
		                    The note names the operators this dialect accepts, because an operator another
		                    ecosystem spells differently is read as part of the version.
		"""
		if expression is None:
			return cls()
		elif not isinstance(expression, str):
			ex = TypeError("Parameter 'expression' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(expression)}'.")
			raise ex
		elif (expression := expression.strip()) == "":
			return cls()

		versionType = cls._VERSION_TYPE if versionType is None else versionType
		skippable =   cls._SEPARATORS + " \t"
		# 'V' is unbound here - the version class comes from the dialect or the parameter, not from the type variable.
		constraints: list[VersionConstraint[Any]] = []
		position =    0

		for match in cls._CONSTRAINT_PATTERN.finditer(expression):
			if (skipped := expression[position:match.start()].strip(skippable)) != "":
				ex = ValueError(f"Expression '{expression}' has unexpected input at '{skipped}'.")
				ex.add_note(f"This dialect accepts the operators {', '.join(sorted(cls._OPERATORS))}.")
				raise ex

			operator = match.group(1)
			comparison = VersionComparison.Equal if operator is None else cls._OPERATORS[operator]
			try:
				version = versionType.Parse(match.group(2))
			except ValueError as cause:
				# An operator this dialect doesn't know is not recognised as one, so it lands in the version instead.
				ex = ValueError(f"Expression '{expression}' has unexpected input at '{match.group(0).strip()}'.")
				ex.add_note(f"This dialect accepts the operators {', '.join(sorted(cls._OPERATORS))}.")
				raise ex from cause

			if (shorthand := cls._SHORTHANDS.get(comparison, None)) is not None:
				constraints.append(shorthand(version))
			else:
				constraints.append(VersionConstraint(comparison, version))
			position = match.end()

		if (skipped := expression[position:].strip(skippable)) != "":
			ex = ValueError(f"Expression '{expression}' has unexpected input at '{skipped}'.")
			ex.add_note(f"This dialect accepts the operators {', '.join(sorted(cls._OPERATORS))}.")
			raise ex

		return cls(constraints)

	@readonly
	def Constraints(self) -> tuple[VersionConstraint[V], ...]:
		"""
		Read-only property to access the constraints a version has to satisfy (:attr:`_constraints`).

		:returns: The constraints, empty if the expression matches every version.
		"""
		return self._constraints

	@readonly
	def MatchesAnyVersion(self) -> bool:
		"""
		Read-only property to return whether this expression constrains nothing.

		:returns: ``True``, if the expression has no constraints and every version satisfies it.
		"""
		return len(self._constraints) == 0

	def __contains__(self, version: V) -> bool:
		"""
		Check if a version satisfies every constraint of this expression.

		:param version:    The version to check.
		:returns:          ``True``, if the version satisfies all constraints. An expression without constraints is
		                   satisfied by every version.
		:raises TypeError: If parameter 'version' is not of type :class:`Version`.
		"""
		if not isinstance(version, Version):
			ex = TypeError("Parameter 'version' is not of type 'Version'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		return all(version in constraint for constraint in self._constraints)

	def ToVersionRange(self) -> VersionRange[Version]:
		"""
		Convert this expression into the single :class:`VersionRange` it describes.

		An expression is a conjunction, so its range is the **intersection** of its constraints' ranges, which
		:meth:`VersionRange.__and__` computes. An expression with no constraints is the range unbound at both ends,
		since both match every version.

		Not every expression has a range. One containing an :attr:`~VersionComparison.Unequal` does not, because the
		complement of a version is a union of two intervals - ``>=1.0,!=1.3,<2.0`` is an ordinary requirement with
		no single range. That is why :class:`VersionExpression` is not replaced by :class:`VersionRange`: a range is
		one interval, an expression is any conjunction, and the second is strictly more expressive.

		:returns:           The range of versions satisfying every constraint.
		:raises ValueError: If a constraint describes no range, which an :attr:`~VersionComparison.Unequal` never
		                    does.
		:raises ValueError: If the constraints have no version in common.
		"""
		versionRange: VersionRange[_VersionType] = VersionRange(None, None)
		for constraint in self._constraints:
			versionRange = versionRange & constraint.ToVersionRange()

		return versionRange

	def __len__(self) -> int:
		"""
		Return the number of constraints in this expression.

		:returns: Number of constraints.
		"""
		return len(self._constraints)

	def __iter__(self) -> Iterator[VersionConstraint[V]]:
		"""
		Iterate the constraints of this expression, in the order they were written.

		:returns: An iterator over the constraints.
		"""
		return iter(self._constraints)

	def __str__(self) -> str:
		"""
		Return the expression in this dialect's spelling.

		A :class:`VersionConstraint` renders itself canonically, which is not what every dialect writes - Debian
		spells :attr:`~VersionComparison.Equal` ``=`` and :attr:`~VersionComparison.LessThan` ``<<``. The dialect's
		own operator table answers what it writes; where a dialect has several spellings for one comparison, the
		first one wins.

		:returns: The constraints, joined by this dialect's separator, or an empty string if it constrains nothing.
		"""
		separator =         self._SEPARATORS[0] if len(self._SEPARATORS) > 0 else " "
		spelled: list[str] = []

		for constraint in self._constraints:
			for spelling, comparison in self._OPERATORS.items():
				if comparison is constraint.Comparison:
					spelled.append(f"{spelling}{constraint.Version}")
					break
			else:
				spelled.append(str(constraint))

		return separator.join(spelled)


@export
class PythonVersionExpression(VersionExpression[V]):
	"""
	A version expression in the dialect :pep:`440` defines, which is what a Python requirement file writes.

	It adds the compatible release operator ``~=`` to the six ordering comparisons and parses its versions as
	:class:`PythonVersion`:

	.. code-block:: python

	   expression = PythonVersionExpression.Parse("~=1.2.3")
	   PythonVersion.Parse("1.2.9") in expression   # True
	   PythonVersion.Parse("1.3.0") in expression   # False

	.. seealso::

	   :class:`CompatibleVersionConstraint`
	      |rarr| What ``~=`` is parsed into, and how its upper bound is derived.
	"""

	#: The neutral dialect's operators, plus the compatible release operator :pep:`440` defines.
	_OPERATORS: ClassVar[dict[str, VersionComparison]] = {
		**VersionExpression._OPERATORS,
		"~=": VersionComparison.CompatibleRelease,
	}

	#: :pep:`440` versions, so an epoch, a release candidate or a post-release parses.
	_VERSION_TYPE: ClassVar[type[Version]] = PythonVersion

	#: ``~=`` derives an upper bound, so it is not a plain comparison.
	_SHORTHANDS: ClassVar[dict[VersionComparison, type]] = {
		VersionComparison.CompatibleRelease: CompatibleVersionConstraint,
	}


@export
class NPMVersionExpression(VersionExpression[V]):
	"""
	A version expression in npm's dialect, which is what a ``package.json`` dependency writes.

	npm differs from :pep:`440` in three ways that matter to a parser:

	* constraints are separated by **whitespace**, and a comma is a syntax error;
	* equality is written ``=``, never ``==``;
	* there is **no** ``!=`` - npm cannot exclude a single version this way.

	It adds ``^`` and ``~``, which are not :pep:`440`'s ``~=``:

	.. code-block:: python

	   expression = NPMVersionExpression.Parse("^1.2.3")
	   SemanticVersion.Parse("1.9.0") in expression   # True
	   SemanticVersion.Parse("2.0.0") in expression   # False

	.. note::

	   The shorthands ``1.2.x``, ``*``, the hyphen range ``1.2.3 - 2.3.4`` and the alternative ``||`` are **not**
	   parsed. The first three are further rewriting rules; ``||`` is a disjunction, which this class cannot hold
	   because every constraint of an expression has to be satisfied.

	.. seealso::

	   :class:`CaretVersionConstraint` |br|
	   :class:`TildeVersionConstraint`
	"""

	#: npm's operators. No ``==`` and no ``!=``; ``^`` and ``~`` are npm's own shorthands.
	_OPERATORS: ClassVar[dict[str, VersionComparison]] = {
		"<=": VersionComparison.LessThanOrEqual,
		">=": VersionComparison.GreaterThanOrEqual,
		"<":  VersionComparison.LessThan,
		">":  VersionComparison.GreaterThan,
		"=":  VersionComparison.Equal,
		"^":  VersionComparison.Caret,
		"~":  VersionComparison.Tilde,
	}

	#: npm separates constraints by whitespace alone; a comma is a syntax error there.
	_SEPARATORS: ClassVar[str] = ""

	#: npm is strict semantic versioning.
	_VERSION_TYPE: ClassVar[type[Version]] = SemanticVersion

	#: ``^`` and ``~`` each derive an upper bound, by different rules.
	_SHORTHANDS: ClassVar[dict[VersionComparison, type]] = {
		VersionComparison.Caret: CaretVersionConstraint,
		VersionComparison.Tilde: TildeVersionConstraint,
	}


@export
class DebianVersionExpression(VersionExpression[V]):
	"""
	A version expression in Debian's dialect, as a ``debian/control`` dependency writes it inside its parentheses.

	Debian spells the strict comparisons ``<<`` and ``>>``, equality ``=``, and has **no** ``!=``. The obsolete
	spellings ``<`` and ``>`` are deliberately **not** accepted: ``dpkg`` still takes them but warns, because they
	historically meant ``<=`` and ``>=`` - reading them silently as the strict operators would invert their meaning.

	.. code-block:: python

	   expression = DebianVersionExpression.Parse(">> 1.2.3")
	   SemanticVersion.Parse("1.3.0") in expression   # True

	.. note::

	   A Debian dependency states **one** constraint per package mention - ``pkg (>= 1.0), pkg (<< 2.0)`` - so an
	   expression here usually holds a single constraint. The comma is Debian's *dependency* separator, not a
	   constraint separator.

	.. attention::

	   Debian version strings are ``epoch:upstream-revision``. :class:`SemanticVersion` reads the revision as a
	   postfix, but an **epoch** (``2:1.2.3-1``) does not parse, and ``1.2.3-1`` renders back as ``1.2.3+1``.
	   Matching Debian versions faithfully needs a ``DebianVersion`` class, which pyTooling does not have.
	"""

	#: Debian's operators. ``<<`` and ``>>`` are the strict ones; there is no ``!=``.
	_OPERATORS: ClassVar[dict[str, VersionComparison]] = {
		"<<": VersionComparison.LessThan,
		">>": VersionComparison.GreaterThan,
		"<=": VersionComparison.LessThanOrEqual,
		">=": VersionComparison.GreaterThanOrEqual,
		"=":  VersionComparison.Equal,
	}

	#: Debian's comma separates dependencies rather than constraints, but accepting it costs nothing.
	_SEPARATORS: ClassVar[str] = ","

	#: The closest pyTooling has to a Debian version - see the class doc-string's caveat.
	_VERSION_TYPE: ClassVar[type[Version]] = SemanticVersion
