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
# Copyright 2020-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from collections.abc import Iterable as abc_Iterable
from enum            import Flag, Enum
from re              import compile as re_compile
from sys             import version_info   # needed for versions before Python 3.11
from typing          import Optional as Nullable, Union, Callable, Any, Generic, TypeVar, Tuple, Iterable, Iterator, List

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType, abstractmethod, mustoverride
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, abstractmethod, mustoverride
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class Parts(Flag):
	"""Enumeration describing parts of a version number that can be present."""
	Unknown = 0     #: Undocumented
	Major = 1       #: Major number is present. (e.g. X in ``vX.0.0``).
	Year = 1        #: Year is present. (e.g. X in ``XXXX.10``).
	Minor = 2       #: Minor number is present. (e.g. Y in ``v0.Y.0``).
	Month = 2       #: Month is present. (e.g. X in ``2024.YY``).
	Week = 2        #: Week is present. (e.g. X in ``2024.YY``).
	Micro = 4       #: Patch number is present. (e.g. Z in ``v0.0.Z``).
	Patch = 4       #: Patch number is present. (e.g. Z in ``v0.0.Z``).
	Day = 4         #: Day is present. (e.g. X in ``2024.10.ZZ``).
	Level = 8       #: Release level is present.
	Dev = 16        #: Development part is present.
	Build = 32      #: Build number is present. (e.g. bbbb in ``v0.0.0.bbbb``)
	Post  = 64      #: Post-release number is present.
	Prefix = 128    #: Prefix is present.
	Postfix = 256   #: Postfix is present.
	Hash = 512      #: Hash is present.
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

	def __eq__(self, other: Any):
		"""
		Compare two release levels if the level is equal to the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is equal the second operand's release level.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by == operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self is other

	def __ne__(self, other: Any):
		"""
		Compare two release levels if the level is unequal to the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is unequal the second operand's release level.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by != operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self is not other

	def __lt__(self, other: Any):
		"""
		Compare two release levels if the level is less than the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is less than the second operand.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value < other.value

	def __le__(self, other: Any):
		"""
		Compare two release levels if the level is less than or equal the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is less than or equal the second operand.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <=>= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value <= other.value

	def __gt__(self, other: Any):
		"""
		Compare two release levels if the level is greater than the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is greater than the second operand.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value > other.value

	def __ge__(self, other: Any):
		"""
		Compare two release levels if the level is greater than or equal the second operand.

		:param other:       Operand to compare against.
		:returns:           ``True``, if release level is greater than or equal the second operand.
		:raises TypeError:  If parameter ``other`` is not of type :class:`ReleaseLevel` or :class:`str`.
		"""
		if isinstance(other, str):
			other = ReleaseLevel(other)

		if not isinstance(other, ReleaseLevel):
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__} or 'str'.")
			raise ex

		return self.value >= other.value

	def __hash__(self) -> int:
		return hash(self.value)

	def __str__(self) -> str:
		"""
		Returns the release level's string equivalent.

		:returns: The string equivalent of the release level.
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

	:param bits:      Number of bits to encode any positive version number part.
	:param majorBits: Number of bits to encode a positive major number in a version.
	:param minorBits: Number of bits to encode a positive minor number in a version.
	:param microBits: Number of bits to encode a positive micro number in a version.
	:param buildBits: Number of bits to encode a positive build number in a version.
	:return:          A validation function for Version instances.
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

	:param max:      The upper bound for any positive version number part.
	:param majorMax: The upper bound for the positive major number.
	:param minorMax: The upper bound for the positive minor number.
	:param microMax: The upper bound for the positive micro number.
	:param buildMax: The upper bound for the positive build number.
	:return:         A validation function for Version instances.
	"""
	if max is not None:
		majorMax = minorMax = microMax = buildMax = max

	def validator(version: SemanticVersion) -> bool:
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

	_parts:         Parts          #: Integer flag enumeration of present parts in a version number.
	_prefix:        str            #: Prefix string
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
		build:   Nullable[int] = None,
		postfix: Nullable[str] = None,
		prefix:  Nullable[str] = None,
		hash:    Nullable[str] = None,
		flags:   Flags = Flags.NoVCS
	) -> None:
		"""
		Initializes a version number representation.

		:param major:       Major number part of the version number.
		:param minor:       Minor number part of the version number.
		:param micro:       Micro (patch) number part of the version number.
		:param level:       Release level (alpha, beta, release candidate, final, ...) of the version number.
		:param number:      Release number part (in combination with release level) of the version number.
		:param post:        Post number part of the version number.
		:param dev:         Development number part of the version number.
		:param build:       Build number part of the version number.
		:param postfix:     The version number's postfix.
		:param prefix:      The version number's prefix.
		:param hash:        Postfix string.
		:param flags:       The version number's flags.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		self.__hash = None

		if not isinstance(major, int):
			raise TypeError("Parameter 'major' is not of type 'int'.")
		elif major < 0:
			raise ValueError("Parameter 'major' is negative.")

		self._parts = Parts.Major
		self._major = major

		if minor is not None:
			if not isinstance(minor, int):
				raise TypeError("Parameter 'minor' is not of type 'int'.")
			elif minor < 0:
				raise ValueError("Parameter 'minor' is negative.")

			self._parts |= Parts.Minor
			self._minor = minor
		else:
			self._minor = 0

		if micro is not None:
			if not isinstance(micro, int):
				raise TypeError("Parameter 'micro' is not of type 'int'.")
			elif micro < 0:
				raise ValueError("Parameter 'micro' is negative.")

			self._parts |= Parts.Micro
			self._micro = micro
		else:
			self._micro = 0

		if level is None:
			raise ValueError("Parameter 'level' is None.")
		elif not isinstance(level, ReleaseLevel):
			raise TypeError("Parameter 'level' is not of type 'ReleaseLevel'.")
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
					raise TypeError("Parameter 'number' is not of type 'int'.")
				elif number < 0:
					raise ValueError("Parameter 'number' is negative.")

				self._releaseNumber = number
			else:
				self._releaseNumber = 0

		if dev is not None:
			if not isinstance(dev, int):
				raise TypeError("Parameter 'dev' is not of type 'int'.")
			elif dev < 0:
				raise ValueError("Parameter 'dev' is negative.")

			self._parts |= Parts.Dev
			self._dev = dev
		else:
			self._dev = 0

		if post is not None:
			if not isinstance(post, int):
				raise TypeError("Parameter 'post' is not of type 'int'.")
			elif post < 0:
				raise ValueError("Parameter 'post' is negative.")

			self._parts |= Parts.Post
			self._post = post
		else:
			self._post = 0

		if build is not None:
			if not isinstance(build, int):
				raise TypeError("Parameter 'build' is not of type 'int'.")
			elif build < 0:
				raise ValueError("Parameter 'build' is negative.")

			self._build = build
			self._parts |= Parts.Build
		else:
			self._build = 0

		if postfix is not None:
			if not isinstance(postfix, str):
				raise TypeError("Parameter 'postfix' is not of type 'str'.")

			self._parts |= Parts.Postfix
			self._postfix = postfix
		else:
			self._postfix = ""

		if prefix is not None:
			if not isinstance(prefix, str):
				raise TypeError("Parameter 'prefix' is not of type 'str'.")

			self._parts |= Parts.Prefix
			self._prefix = prefix
		else:
			self._prefix = ""

		if hash is not None:
			if not isinstance(hash, str):
				raise TypeError("Parameter 'hash' is not of type 'str'.")

			self._parts |= Parts.Hash
			self._hash = hash
		else:
			self._hash = ""

		if flags is None:
			raise ValueError("Parameter 'flags' is None.")
		elif not isinstance(flags, Flags):
			raise TypeError("Parameter 'flags' is not of type 'Flags'.")

		self._flags = flags

	@classmethod
	@abstractmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["SemanticVersion"], bool]] = None) -> "Version":
		"""Parse a version string and return a Version instance."""

	@readonly
	def Parts(self) -> Parts:
		"""
		Read-only property to access the used parts of this version number.

		:return: A flag enumeration of used version number parts.
		"""
		return self._parts

	@readonly
	def Prefix(self) -> str:
		"""
		Read-only property to access the version number's prefix.

		:return: The prefix of the version number.
		"""
		return self._prefix

	@readonly
	def Major(self) -> int:
		"""
		Read-only property to access the major number.

		:return: The major number.
		"""
		return self._major

	@readonly
	def Minor(self) -> int:
		"""
		Read-only property to access the minor number.

		:return: The minor number.
		"""
		return self._minor

	@readonly
	def Micro(self) -> int:
		"""
		Read-only property to access the micro number.

		:return: The micro number.
		"""
		return self._micro

	@readonly
	def ReleaseLevel(self) -> ReleaseLevel:
		"""
		Read-only property to access the release level.

		:return: The release level.
		"""
		return self._releaseLevel

	@readonly
	def ReleaseNumber(self) -> int:
		"""
		Read-only property to access the release number.

		:return: The release number.
		"""
		return self._releaseNumber

	@readonly
	def Post(self) -> int:
		"""
		Read-only property to access the post number.

		:return: The post number.
		"""
		return self._post

	@readonly
	def Dev(self) -> int:
		"""
		Read-only property to access the development number.

		:return: The development number.
		"""
		return self._dev

	@readonly
	def Build(self) -> int:
		"""
		Read-only property to access the build number.

		:return: The build number.
		"""
		return self._build

	@readonly
	def Postfix(self) -> str:
		"""
		Read-only property to access the version number's postfix.

		:return: The postfix of the version number.
		"""
		return self._postfix

	@readonly
	def Hash(self) -> str:
		"""
		Read-only property to access the version number's hash.

		:return: The hash.
		"""
		return self._hash

	@readonly
	def Flags(self) -> Flags:
		"""
		Read-only property to access the version number's flags.

		:return: The flags of the version number.
		"""
		return self._flags

	def _equal(self, left: "Version", right: "Version") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`Version` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (
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

	def _compare(self, left: "Version", right: "Version") -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`Version` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both operands are equal).
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

	def _minimum(self, actual: "Version", expected: "Version") -> Nullable[bool]:
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
		:return:           Formatted version number.
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
	def __eq__(self, other: Union["Version", str, int, None]) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
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

		:param other:       Operand to compare against.
		:returns:           ``True``, if both version numbers are not equal.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif ((sC := self.__class__) is (oC := other.__class__) or issubclass(sC, oC) or issubclass(oC, sC)):
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

		The second operand should be an instance of :class:`Version`, but :class:`VersionRange`, :class:`VersionSet`,
		``str`` and ``int`` are accepted, too. |br|
		In case of ``str``, it's tried to parse the string as a version number. In case of ``int``, a single major
		number is assumed (all other parts are zero).

		``float`` is not supported, due to rounding issues when converting the fractional part of the float to a minor
		number.

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is less than the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by < operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		return self._compare(self, other) is True

	@mustoverride
	def __le__(self, other: Union["Version", str, int, None]) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, :class:`str` or :class:`ìnt`.
		"""
		equalValue = True
		if other is None:
			raise ValueError(f"Second operand is None.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by <= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		result = self._compare(self, other)
		return result if result is not None else equalValue

	@mustoverride
	def __gt__(self, other: Union["Version", str, int, None]) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, :class:`str` or :class:`ìnt`.
		"""
		if other is None:
			raise ValueError(f"Second operand is None.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by > operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		return self._compare(self, other) is False

	@mustoverride
	def __ge__(self, other: Union["Version", str, int, None]) -> bool:
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
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`, :class:`VersionRange`, :class:`VersionSet`, :class:`str` or :class:`ìnt`.
		"""
		equalValue = True
		if other is None:
			raise ValueError(f"Second operand is None.")
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
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by >= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, VersionRange, VersionSet, str, int")
			raise ex

		result = self._compare(self, other)
		return not result if result is not None else equalValue

	def __rshift__(self, other: Union["Version", str, int, None]) -> bool:
		if other is None:
			raise ValueError(f"Second operand is None.")
		elif isinstance(other, self.__class__):
			pass
		elif isinstance(other, str):
			other = self.__class__.Parse(other)
		elif isinstance(other, int):
			other = self.__class__(major=other)
		else:
			ex = TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by %= operator.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Supported types for second operand: {self.__class__.__name__}, str, int")
			raise ex

		return self._minimum(self, other)

	def __hash__(self) -> int:
		if self.__hash is None:
			self.__hash = hash((
				self._prefix,
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

	_PATTERN = re_compile(
		r"^"
		r"(?P<prefix>[a-zA-Z]*)"
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
	)
# QUESTION: was this how many commits a version is ahead of the last tagged version?
#	ahead:    int = 0

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
		build:   Nullable[int] = None,
		postfix: Nullable[str] = None,
		prefix:  Nullable[str] = None,
		hash:    Nullable[str] = None,
		flags:   Flags = Flags.NoVCS
	) -> None:
		"""
		Initializes a semantic version number representation.

		:param major:       Major number part of the version number.
		:param minor:       Minor number part of the version number.
		:param micro:       Micro (patch) number part of the version number.
		:param build:       Build number part of the version number.
		:param level:       tbd
		:param number:      tbd
		:param post:        Post number part of the version number.
		:param dev:         Development number part of the version number.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:param flags:       The version number's flags.
		:param hash:        tbd
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'post' is not of type int.
		:raises ValueError: If parameter 'post' is a negative number.
		:raises TypeError:  If parameter 'dev' is not of type int.
		:raises ValueError: If parameter 'dev' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(major, minor, micro, level, number, post, dev, build=build, postfix=postfix, prefix=prefix, hash=hash, flags=flags)

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
		if versionString is None:
			raise ValueError("Parameter 'versionString' is None.")
		elif not isinstance(versionString, str):
			ex = TypeError(f"Parameter 'versionString' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(versionString)}'.")
			raise ex

		versionString = versionString.strip()
		if versionString == "":
			raise ValueError("Parameter 'versionString' is empty.")

		match = cls._PATTERN.match(versionString)
		if match is None:
			raise ValueError(f"Syntax error in parameter 'versionString': '{versionString}'")

		def toInt(value: Nullable[str]) -> Nullable[int]:
			if value is None or value == "":
				return None
			try:
				return int(value)
			except ValueError as ex:  # pragma: no cover
				raise ValueError(f"Invalid part '{value}' in version number '{versionString}'.") from ex

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
			build=toInt(match["build"]),
			postfix=match["postfix"],
			prefix=match["prefix"],
			# hash=match["hash"],
			flags=Flags.Clean
		)
		if validator is not None and not validator(version):
			raise ValueError(f"Failed to validate version string '{versionString}'.")  # pragma: no cover

		return version

	@readonly
	def Patch(self) -> int:
		"""
		Read-only property to access the patch number.

		The patch number is identical to the micro number.

		:return: The patch number.
		"""
		return self._micro

	def _equal(self, left: "SemanticVersion", right: "SemanticVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`SemanticVersion` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return super()._equal(left, right)

	def _compare(self, left: "SemanticVersion", right: "SemanticVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the comparison of two :class:`SemanticVersion` instances.

		:param left:  Left operand.
		:param right: Right operand.
		:returns:     ``True``, if ``left`` is smaller than ``right``. |br|
		              False if ``left`` is greater than ``right``. |br|
		              Otherwise it's None (both operands are equal).
		"""
		return super()._compare(left, right)

	def __eq__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
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

		:param other:       Operand to compare against.
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

		:param other:       Operand to compare against.
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

		:param other:       Operand to compare against.
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

		:param other:       Operand to compare against.
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

		:param other:       Operand to compare against.
		:returns:           ``True``, if version is greater than or equal the second operand.
		:raises ValueError: If parameter ``other`` is None.
		:raises TypeError:  If parameter ``other`` is not of type :class:`SemanticVersion`, :class:`str` or :class:`ìnt`.
		"""
		return super().__ge__(other)

	def __rshift__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
		return super().__rshift__(other)

	def __hash__(self) -> int:
		return super().__hash__()

	def __format__(self, formatSpec: str) -> str:
		result = self._format(formatSpec)

		if (pos := result.find("%")) != -1 and result[pos + 1] != "%":  # pragma: no cover
			raise ValueError(f"Unknown format specifier '%{result[pos + 1]}' in '{formatSpec}'.")

		return result.replace("%%", "%")

	def __repr__(self) -> str:
		"""
		Return a string representation of this version number without prefix ``v``.

		:returns: Raw version number representation without a prefix.
		"""
		return f"{self._prefix if Parts.Prefix in self._parts else ''}{self._major}.{self._minor}.{self._micro}"

	def __str__(self) -> str:
		"""
		Return a string representation of this version number.

		:returns: Version number representation.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
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

	@classmethod
	def FromSysVersionInfo(cls) -> "PythonVersion":
		"""
		Create a Python version from :data:`sys.version_info`.

		:returns: A PythonVersion instance of the current Python interpreter's version.
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
		return super().__hash__()

	def __str__(self) -> str:
		"""
		Return a string representation of this version number.

		:returns: Version number representation.
		"""
		result = self._prefix if Parts.Prefix in self._parts else ""
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
		:param minor:       Minor number part of the version number.
		:param micro:       Micro (patch) number part of the version number.
		:param build:       Build number part of the version number.
		:param flags:       The version number's flags.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(major, minor, micro, build=build, postfix=postfix, prefix=prefix, flags=flags)

	@classmethod
	def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["CalendarVersion"], bool]] = None) -> "CalendarVersion":
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

		version = cls(major, minor, flags=flags)
		if validator is not None and not validator(version):
			raise ValueError(f"Failed to validate version string '{versionString}'.")  # pragma: no cover

		return version

	@property
	def Year(self) -> int:
		"""
		Read-only property to access the year part.

		:return: The year part.
		"""
		return self._major

	def _equal(self, left: "CalendarVersion", right: "CalendarVersion") -> Nullable[bool]:
		"""
		Private helper method to compute the equality of two :class:`CalendarVersion` instances.

		:param left:  Left parameter.
		:param right: Right parameter.
		:returns:     ``True``, if ``left`` is equal to ``right``, otherwise it's ``False``.
		"""
		return (left._major == right._major) and (left._minor == right._minor) and (left._micro == right._micro)

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

		if left._micro < right._micro:
			return True
		elif left._micro > right._micro:
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

	def __hash__(self) -> int:
		return super().__hash__()

	def __format__(self, formatSpec: str) -> str:
		"""
		Return a string representation of this version number according to the format specification.

		.. topic:: Format Specifiers

		   * ``%M`` - major number (year)
		   * ``%m`` - minor number (month/week)

		:param formatSpec: The format specification.
		:return:           Formatted version number.
		"""
		if formatSpec == "":
			return self.__str__()

		result = formatSpec
		# result = result.replace("%P", str(self._prefix))
		result = result.replace("%M", str(self._major))
		result = result.replace("%m", str(self._minor))
		# result = result.replace("%p", str(self._pre))

		return result.replace("%%", "%")

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


@export
class YearMonthVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and month like ``2021.10``."""

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
		:param month:       Month part of the version number.
		:param build:       Build number part of the version number.
		:param flags:       The version number's flags.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(year, month, 0, build, flags, prefix, postfix)

	@property
	def Month(self) -> int:
		"""
		Read-only property to access the month part.

		:return: The month part.
		"""
		return self._minor

	def __hash__(self) -> int:
		return super().__hash__()


@export
class YearWeekVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and week like ``2021.47``."""

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
		:param week:        Week part of the version number.
		:param build:       Build number part of the version number.
		:param flags:       The version number's flags.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(year, week, 0, build, flags, prefix, postfix)

	@property
	def Week(self) -> int:
		"""
		Read-only property to access the week part.

		:return: The week part.
		"""
		return self._minor

	def __hash__(self) -> int:
		return super().__hash__()


@export
class YearReleaseVersion(CalendarVersion):
	"""Representation of a calendar version number made of year and release per year like ``2021.2``."""

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
		:param release:     Release number of the version number.
		:param build:       Build number part of the version number.
		:param flags:       The version number's flags.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(year, release, 0, build, flags, prefix, postfix)

	@property
	def Release(self) -> int:
		"""
		Read-only property to access the release number.

		:return: The release number.
		"""
		return self._minor

	def __hash__(self) -> int:
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
		:param month:       Month part of the version number.
		:param day:         Day part of the version number.
		:param build:       Build number part of the version number.
		:param flags:       The version number's flags.
		:param prefix:      The version number's prefix.
		:param postfix:     The version number's postfix.
		:raises TypeError:  If parameter 'major' is not of type int.
		:raises ValueError: If parameter 'major' is a negative number.
		:raises TypeError:  If parameter 'minor' is not of type int.
		:raises ValueError: If parameter 'minor' is a negative number.
		:raises TypeError:  If parameter 'micro' is not of type int.
		:raises ValueError: If parameter 'micro' is a negative number.
		:raises TypeError:  If parameter 'build' is not of type int.
		:raises ValueError: If parameter 'build' is a negative number.
		:raises TypeError:  If parameter 'prefix' is not of type str.
		:raises TypeError:  If parameter 'postfix' is not of type str.
		"""
		super().__init__(year, month, day, build, flags, prefix, postfix)

	@property
	def Month(self) -> int:
		"""
		Read-only property to access the month part.

		:return: The month part.
		"""
		return self._minor

	@property
	def Day(self) -> int:
		"""
		Read-only property to access the day part.

		:return: The day part.
		"""
		return self._micro

	def __hash__(self) -> int:
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
	"""
	_lowerBound:    V
	_upperBound:    V
	_boundHandling: RangeBoundHandling

	def __init__(self, lowerBound: V, upperBound: V, boundHandling: RangeBoundHandling = RangeBoundHandling.BothBoundsInclusive) -> None:
		"""
		Initializes a version range described by a lower and upper bound.

		:param lowerBound:  lowest version (inclusive).
		:param upperBound:  hightest version (inclusive).
		:raises TypeError:  If parameter ``lowerBound`` is not of type :class:`Version`.
		:raises TypeError:  If parameter ``upperBound`` is not of type :class:`Version`.
		:raises TypeError:  If parameter ``lowerBound`` and ``upperBound`` are unrelated types.
		:raises ValueError: If parameter ``lowerBound`` isn't less than or equal to ``upperBound``.
		"""
		if not isinstance(lowerBound, Version):
			ex = TypeError(f"Parameter 'lowerBound' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(lowerBound)}'.")
			raise ex

		if not isinstance(upperBound, Version):
			ex = TypeError(f"Parameter 'upperBound' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(upperBound)}'.")
			raise ex

		if not ((lBC := lowerBound.__class__) is (uBC := upperBound.__class__) or issubclass(lBC, uBC) or issubclass(uBC, lBC)):
			ex = TypeError(f"Parameters 'lowerBound' and 'upperBound' are not compatible with each other.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(lowerBound)}' for lowerBound and type '{getFullyQualifiedName(upperBound)}' for upperBound.")
			raise ex

		if not (lowerBound <= upperBound):
			ex = ValueError(f"Parameter 'lowerBound' isn't less than parameter 'upperBound'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got '{lowerBound}' for lowerBound and '{upperBound}' for upperBound.")
			raise ex

		self._lowerBound = lowerBound
		self._upperBound = upperBound
		self._boundHandling = boundHandling

	@property
	def LowerBound(self) -> V:
		"""
		Property to access the range's lower bound.

		:return: Lower bound of the version range.
		"""
		return self._lowerBound

	@LowerBound.setter
	def LowerBound(self, value: V) -> None:
		if not isinstance(value, Version):
			ex = TypeError(f"Parameter 'value' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._lowerBound = value

	@readonly
	def UpperBound(self) -> V:
		"""
		Property to access the range's upper bound.

		:return: Upper bound of the version range.
		"""
		return self._upperBound

	@UpperBound.setter
	def UpperBound(self, value: V) -> None:
		if not isinstance(value, Version):
			ex = TypeError(f"Parameter 'value' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._upperBound = value

	@readonly
	def BoundHandling(self) -> RangeBoundHandling:
		"""
		Property to access the range's bound handling strategy.

		:return: The range's bound handling strategy.
		"""
		return self._boundHandling

	@BoundHandling.setter
	def BoundHandling(self, value: RangeBoundHandling) -> None:
		if not isinstance(value, RangeBoundHandling):
			ex = TypeError(f"Parameter 'value' is not of type 'RangeBoundHandling'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._boundHandling = value

	def __and__(self, other: Any) -> "VersionRange[T]":
		"""
		Compute the intersection of two version ranges.

		:param other:       Second version range to intersect with.
		:returns:           Intersected version range.
		:raises TypeError:  If parameter 'other' is not of type :class:`VersionRange`.
		:raises ValueError: If intersection is empty.
		"""
		if not isinstance(other, VersionRange):
			ex = TypeError(f"Parameter 'other' is not of type 'VersionRange'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not (isinstance(other._lowerBound, self._lowerBound.__class__) and isinstance(self._lowerBound, other._lowerBound.__class__)):
			ex = TypeError(f"Parameter 'other's LowerBound and this range's 'LowerBound' are not compatible with each other.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(
					f"Got type '{getFullyQualifiedName(other._lowerBound)}' for other.LowerBound and type '{getFullyQualifiedName(self._lowerBound)}' for self.LowerBound.")
			raise ex

		if other._lowerBound < self._lowerBound:
			lBound = self._lowerBound
		elif other._lowerBound in self:
			lBound = other._lowerBound
		else:
			raise ValueError()

		if other._upperBound > self._upperBound:
			uBound = self._upperBound
		elif other._upperBound in self:
			uBound = other._upperBound
		else:
			raise ValueError()

		return self.__class__(lBound, uBound)

	def __lt__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is less than the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version range is less than the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not (isinstance(other, self._lowerBound.__class__) and isinstance(self._lowerBound, other.__class__)):
			ex = TypeError(f"Parameter 'other' is not compatible with version range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._upperBound < other

	def __le__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is less than or equal the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version range is less than  or equal the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not (isinstance(other, self._lowerBound.__class__) and isinstance(self._lowerBound, other.__class__)):
			ex = TypeError(f"Parameter 'other' is not compatible with version range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if RangeBoundHandling.UpperBoundExclusive in self._boundHandling:
			return self._upperBound < other
		else:
			return self._upperBound <= other

	def __gt__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is greater than the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version range is greater than the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not (isinstance(other, self._upperBound.__class__) and isinstance(self._upperBound, other.__class__)):
			ex = TypeError(f"Parameter 'other' is not compatible with version range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._lowerBound > other

	def __ge__(self, other: Any) -> bool:
		"""
		Compare a version range and a version numbers if the version range is greater than  or equal the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version range is greater than or equal the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not (isinstance(other, self._upperBound.__class__) and isinstance(self._upperBound, other.__class__)):
			ex = TypeError(f"Parameter 'other' is not compatible with version range.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if RangeBoundHandling.LowerBoundExclusive in self._boundHandling:
			return self._lowerBound > other
		else:
			return self._lowerBound >= other

	def __contains__(self, version: Version) -> bool:
		"""
		Check if the version is in the version range.

		:param version:    Version to check.
		:returns:          ``True``, if version is in range.
		:raises TypeError: If parameter ``version`` is not of type :class:`Version`.
		"""
		if not isinstance(version, Version):
			ex = TypeError(f"Parameter 'item' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(version)}'.")
			raise ex

		if self._boundHandling is RangeBoundHandling.BothBoundsInclusive:
			return self._lowerBound <= version <= self._upperBound
		elif self._boundHandling is (RangeBoundHandling.LowerBoundInclusive | RangeBoundHandling.UpperBoundExclusive):
			return self._lowerBound <= version < self._upperBound
		elif self._boundHandling is (RangeBoundHandling.LowerBoundExclusive | RangeBoundHandling.UpperBoundInclusive):
			return self._lowerBound < version <= self._upperBound
		else:
			return self._lowerBound < version < self._upperBound


@export
class VersionSet(Generic[V], metaclass=ExtendedType, slots=True):
	"""
	Representation of an ordered set of versions.

	This version set works with :class:`SemanticVersion` and :class:`CalendarVersion` and its derived classes.
	"""
	_items: List[V]  #: An ordered list of set members.

	def __init__(self, versions: Union[Version, Iterable[V]]):
		"""
		Initializes a version set either by a single version or an iterable of versions.

		:param versions:    A single version or an iterable of versions.
		:raises ValueError: If parameter ``versions`` is None`.
		:raises TypeError:  In case of a single version, if parameter ``version`` is not of type :class:`Version`.
		:raises TypeError:  In case of an iterable, if parameter ``versions`` containes elements, which are not of type :class:`Version`.
		:raises TypeError:  If parameter ``versions`` is neither a single version nor an iterable thereof.
		"""
		if versions is None:
			raise ValueError(f"Parameter 'versions' is None.")

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
				raise TypeError(f"First element in parameter 'versions' is not of type Version.")

			baseType = firstVersion.__class__
			for version in iterator:
				if not isinstance(version, baseType):
					raise TypeError(f"Element from parameter 'versions' is not of type {baseType.__name__}")

			self._items = list(sorted(versions))
		else:
			raise TypeError(f"Parameter 'versions' is not an Iterable.")

	def __and__(self, other: "VersionSet[V]") -> "VersionSet[T]":
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

	def __or__(self, other: "VersionSet[V]") -> "VersionSet[T]":
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

		:param other:       Operand to compare against.
		:returns:           ``True``, if version set is less than the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[-1] < other

	def __le__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is less than or equal the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version set is less than or equal the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[-1] <= other

	def __gt__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is greater than the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version set is greater than the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[0] > other

	def __ge__(self, other: Any) -> bool:
		"""
		Compare a version set and a version numbers if the version set is greater than or equal the second operand (version).

		:param other:       Operand to compare against.
		:returns:           ``True``, if version set is greater than or equal the second operand (version).
		:raises TypeError:  If parameter ``other`` is not of type :class:`Version`.
		"""
		# TODO: support VersionRange < VersionRange too
		# TODO: support str, int, ... like Version ?
		if not isinstance(other, Version):
			ex = TypeError(f"Parameter 'other' is not of type 'Version'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._items[0] >= other

	def __contains__(self, version: V) -> bool:
		"""
		Checks if the version a member of the set.

		:param version: The version to check.
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

		.. hint:: Versions are ordered from lowest to highest version number.
		"""
		return self._items[index]
