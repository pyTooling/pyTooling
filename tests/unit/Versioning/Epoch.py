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
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for the epoch part of :class:`pyTooling.Versioning.SemanticVersion`.

An epoch outranks every other part of a version number. Debian writes it ``2:1.2.3``, PEP 440 writes it ``2!1.2.3``,
so the separator is a class variable that :class:`~pyTooling.Versioning.PythonVersion` overrides.
"""
from typing              import ClassVar

from pyTooling.Versioning import SemanticVersion, PythonVersion, CalendarVersion, Parts
from pyTooling.Testing    import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Construction(Testcase):
	"""An epoch is an optional keyword-only part."""

	def test_WithoutAnEpoch(self) -> None:
		version = SemanticVersion(1, 2, 3)

		self.assertEqual(0, version.Epoch)
		self.assertNotIn(Parts.Epoch, version._parts)

	def test_WithAnEpoch(self) -> None:
		version = SemanticVersion(1, 2, 3, epoch=2)

		self.assertEqual(2, version.Epoch)
		self.assertIn(Parts.Epoch, version._parts)

	def test_AnExplicitZeroEpochIsStillAnEpoch(self) -> None:
		"""``0:1.2.3`` states an epoch, and states the same value an absent one implies."""
		version = SemanticVersion(1, 2, 3, epoch=0)

		self.assertEqual(0, version.Epoch)
		self.assertIn(Parts.Epoch, version._parts)
		self.assertEqual(SemanticVersion(1, 2, 3), version)

	def test_ARejectedEpoch(self) -> None:
		with self.assertRaises(TypeError):
			SemanticVersion(1, 2, 3, epoch="2")

		with self.assertRaises(ValueError):
			SemanticVersion(1, 2, 3, epoch=-1)


class Parsing(Testcase):
	"""The epoch is taken off before the version pattern runs."""

	def test_DebianSpelling(self) -> None:
		version = SemanticVersion.Parse("2:1.2.3")

		self.assertEqual(2, version.Epoch)
		self.assertEqual(1, version.Major)
		self.assertEqual(3, version.Patch)

	def test_PythonSpelling(self) -> None:
		version = PythonVersion.Parse("2!1.2.3")

		self.assertEqual(2, version.Epoch)
		self.assertEqual(1, version.Major)

	def test_EachClassRejectsTheOthersSeparator(self) -> None:
		with self.assertRaises(ValueError):
			SemanticVersion.Parse("2!1.2.3")

		with self.assertRaises(ValueError):
			PythonVersion.Parse("2:1.2.3")

	def test_ThePrefixComesBeforeTheEpoch(self) -> None:
		""":pep:`440` accepts ``v1!1.0`` and rejects ``1!v1.0`` - checked against ``packaging``."""
		version = SemanticVersion.Parse("v2:1.2.3")

		self.assertEqual(2, version.Epoch)
		self.assertEqual("v2:1.2.3", str(version))

		self.assertEqual(1, PythonVersion.Parse("v1!1.0").Epoch)

		with self.assertRaises(ValueError):
			SemanticVersion.Parse("2:v1.2.3")

		with self.assertRaises(ValueError):
			PythonVersion.Parse("1!v1.0")

	def test_AMalformedEpochIsRejected(self) -> None:
		for source in ("x:1.2.3", ":1.2.3", "1.2:1.2.3", "-1:1.2.3"):
			with self.subTest(source=source):
				with self.assertRaises(ValueError):
					SemanticVersion.Parse(source)

	def test_NoEpochIsStillParsed(self) -> None:
		"""Every version without an epoch has to keep parsing exactly as before."""
		version = SemanticVersion.Parse("v1.2.3")

		self.assertEqual(0, version.Epoch)
		self.assertNotIn(Parts.Epoch, version._parts)
		self.assertEqual("v1.2.3", str(version))


class Rendering(Testcase):
	"""The epoch is part of the version's value, so it survives both representations."""

	def test_StringKeepsTheEpoch(self) -> None:
		self.assertEqual("2:1.2.3", str(SemanticVersion.Parse("2:1.2.3")))
		self.assertEqual("2!1.2.3", str(PythonVersion.Parse("2!1.2.3")))

	def test_NormalizedFormKeepsTheEpochButNotThePrefix(self) -> None:
		"""A prefix doesn't contribute to the value; an epoch does."""
		self.assertEqual("2:1.2.3", repr(SemanticVersion.Parse("v2:1.2.3")))

	def test_AVersionWithoutAnEpochRendersUnchanged(self) -> None:
		self.assertEqual("1.2.3", str(SemanticVersion.Parse("1.2.3")))
		self.assertEqual("1.2.3", repr(SemanticVersion.Parse("1.2.3")))

	def test_RoundTrip(self) -> None:
		for source in ("2:1.2.3", "0:1.2.3", "1.2.3"):
			with self.subTest(source=source):
				self.assertEqual(source, str(SemanticVersion.Parse(source)))


class Comparison(Testcase):
	"""The epoch outranks every other part - checked against ``packaging`` and ``dpkg --compare-versions``."""

	def test_AnEpochBeatsAnyReleaseNumber(self) -> None:
		"""``dpkg``: ``1:1.0 gt 2.0`` is true. ``packaging``: ``1!1.0 > 99.0`` is true."""
		self.assertGreater(SemanticVersion.Parse("1:1.0.0"), SemanticVersion.Parse("99.0.0"))
		self.assertGreater(PythonVersion.Parse("1!1.0"), PythonVersion.Parse("99.0"))

	def test_AHigherEpochWins(self) -> None:
		"""``dpkg``: ``2:1.0 gt 1:9.9`` is true."""
		self.assertGreater(SemanticVersion.Parse("2:1.0.0"), SemanticVersion.Parse("1:9.9.9"))

	def test_EqualEpochsFallThroughToTheRest(self) -> None:
		"""``dpkg``: ``2:1.0 gt 2:1.1`` is false."""
		self.assertLess(SemanticVersion.Parse("2:1.0.0"), SemanticVersion.Parse("2:1.1.0"))

	def test_EqualityIncludesTheEpoch(self) -> None:
		self.assertEqual(SemanticVersion.Parse("2:1.2.3"), SemanticVersion.Parse("2:1.2.3"))
		self.assertNotEqual(SemanticVersion.Parse("2:1.2.3"), SemanticVersion.Parse("1:1.2.3"))
		self.assertNotEqual(SemanticVersion.Parse("2:1.2.3"), SemanticVersion.Parse("1.2.3"))

	def test_AnAbsentEpochIsZero(self) -> None:
		"""That is what keeps a version without an epoch comparable with one that has it."""
		self.assertEqual(SemanticVersion.Parse("0:1.2.3"), SemanticVersion.Parse("1.2.3"))
		self.assertLess(SemanticVersion.Parse("1.2.3"), SemanticVersion.Parse("1:0.0.1"))

	def test_TheHashIncludesTheEpoch(self) -> None:
		self.assertNotEqual(hash(SemanticVersion.Parse("2:1.2.3")), hash(SemanticVersion.Parse("1.2.3")))
		self.assertEqual(hash(SemanticVersion.Parse("2:1.2.3")), hash(SemanticVersion.Parse("2:1.2.3")))


class CalendarVersionsAreUnaffected(Testcase):
	"""A calendar version models no epoch; it must keep behaving exactly as before."""

	def test_NoEpochIsParsed(self) -> None:
		version = CalendarVersion.Parse("2024.10")

		self.assertEqual(0, version.Epoch)
		self.assertNotIn(Parts.Epoch, version._parts)

	def test_ComparisonIsUnchanged(self) -> None:
		self.assertLess(CalendarVersion.Parse("2024.10"), CalendarVersion.Parse("2025.01"))


class PatternRebuilding(Testcase):
	"""How a derived class gets a pattern matching its own epoch separator."""

	def test_TheDerivedPatternUsesItsOwnSeparator(self) -> None:
		""":meth:`SemanticVersion.__init_subclass__` rebuilds it from the base class' expression."""
		self.assertIn(r"(?P<epoch>\d+)!", PythonVersion._PATTERN.pattern)
		self.assertIn(r"(?P<epoch>\d+):", SemanticVersion._PATTERN.pattern)
		self.assertNotEqual(SemanticVersion._PATTERN.pattern, PythonVersion._PATTERN.pattern)

	def test_AnAnnotatedSeparatorReachesTheRebuild(self) -> None:
		"""The separator is a ``ClassVar[str]``, and it is that value the rebuild reads - not the inherited ``:``."""
		self.assertIn("_EPOCH_SEPARATOR", PythonVersion.__annotations__)
		self.assertEqual("!", PythonVersion._EPOCH_SEPARATOR)
		self.assertEqual(1, PythonVersion.Parse("1!1.0").Epoch)

		with self.assertRaises(ValueError):
			PythonVersion.Parse("1:1.0")

	def test_ADerivedClassAnnotatingItsSeparatorGetsItsOwnPattern(self) -> None:
		"""A class declared outside this module does the same, annotation and all."""
		class AtVersion(SemanticVersion):
			_EPOCH_SEPARATOR: ClassVar[str] = "@"

		self.assertIn(r"(?P<epoch>\d+)@", AtVersion._PATTERN.pattern)
		self.assertEqual(2, AtVersion.Parse("2@1.0").Epoch)

		with self.assertRaises(ValueError):
			AtVersion.Parse("2:1.0")

	def test_ADerivedClassKeepingTheSeparatorKeepsThePattern(self) -> None:
		class Inherited(SemanticVersion):
			pass

		self.assertIs(SemanticVersion._PATTERN, Inherited._PATTERN)
