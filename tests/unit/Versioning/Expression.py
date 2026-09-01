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
#
"""
Unit tests for :class:`pyTooling.Versioning.VersionExpression`.

Covered are parsing a constraint list, matching a version against it, and the empty expression that stands for
*any version*.
"""
from pyTooling.Versioning import SemanticVersion, PythonVersion, VersionComparison, VersionConstraint
from pyTooling.Versioning import CaretVersionConstraint, CompatibleVersionConstraint, DebianVersionExpression
from pyTooling.Versioning import RangeBoundHandling, RangeVersionConstraint, VersionRange
from pyTooling.Versioning import NPMVersionExpression, PythonVersionExpression, TildeVersionConstraint
from pyTooling.Versioning import VersionExpression
from pyTooling.Testing    import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Constraints(Testcase):
	"""A single comparison of an expression."""

	def test_EveryComparison(self) -> None:
		reference = SemanticVersion.Parse("1.2.0")
		lower, equal, higher = (SemanticVersion.Parse(v) for v in ("1.1.0", "1.2.0", "1.3.0"))

		for comparison, expected in (
			(VersionComparison.Equal,              (False, True,  False)),
			(VersionComparison.Unequal,            (True,  False, True)),
			(VersionComparison.LessThan,           (True,  False, False)),
			(VersionComparison.LessThanOrEqual,    (True,  True,  False)),
			(VersionComparison.GreaterThan,        (False, False, True)),
			(VersionComparison.GreaterThanOrEqual, (False, True,  True)),
		):
			constraint = VersionConstraint(comparison, reference)
			with self.subTest(comparison=comparison.name):
				self.assertEqual(expected, (lower in constraint, equal in constraint, higher in constraint))

	def test_RendersAsItIsWritten(self) -> None:
		constraint = VersionConstraint(VersionComparison.GreaterThanOrEqual, SemanticVersion.Parse("1.2.0"))

		self.assertEqual(">=1.2.0", str(constraint))

	def test_ARejectedComparison(self) -> None:
		with self.assertRaises(TypeError):
			VersionConstraint(">=", SemanticVersion.Parse("1.2.0"))

	def test_ARejectedVersion(self) -> None:
		with self.assertRaises(TypeError):
			VersionConstraint(VersionComparison.Equal, "1.2.0")


class Parsing(Testcase):
	"""Turning an expression string into constraints."""

	def test_ARangeOfTwoConstraints(self) -> None:
		expression = VersionExpression.Parse(">=1.2.0,<2.0.0")

		self.assertEqual(2, len(expression))
		self.assertEqual(">=1.2.0,<2.0.0", str(expression))
		self.assertEqual(
			[VersionComparison.GreaterThanOrEqual, VersionComparison.LessThan],
			[constraint.Comparison for constraint in expression]
		)

	def test_AMissingOperatorIsAnEquality(self) -> None:
		"""``0.10`` and ``==0.10`` are the same statement, which is what an override file writes."""
		expression = VersionExpression.Parse("1.2.0")

		self.assertEqual(VersionComparison.Equal, expression.Constraints[0].Comparison)
		self.assertEqual("==1.2.0", str(expression))

	def test_WhitespaceIsIgnored(self) -> None:
		expression = VersionExpression.Parse("  >= 1.2.0 ,  < 2.0.0  ")

		self.assertEqual(">=1.2.0,<2.0.0", str(expression))

	def test_AnEmptyExpressionConstrainsNothing(self) -> None:
		for source in ("", "   ", None):
			with self.subTest(source=source):
				expression = VersionExpression.Parse(source)

				self.assertEqual(0, len(expression))
				self.assertTrue(expression.MatchesAnyVersion)
				self.assertEqual("", str(expression))

	def test_RedundantSeparatorsAreIgnored(self) -> None:
		"""``packaging`` and npm's ``semver`` both accept these, so rejecting them would be stricter than either."""
		for source in (">=1.2.0,", ",>=1.2.0", ">=1.2.0,,<2.0.0", ">=1.2.0 , , <2.0.0"):
			with self.subTest(source=source):
				self.assertIn(SemanticVersion.Parse("1.5.0"), VersionExpression.Parse(source))

	def test_WhitespaceSeparatesConstraintsToo(self) -> None:
		"""npm separates by whitespace, and allows it after the operator as well - both have to work."""
		for source in (">=1.2.0 <2.0.0", ">= 1.2.0 < 2.0.0", ">=1.2.0, <2.0.0"):
			with self.subTest(source=source):
				expression = VersionExpression.Parse(source)

				self.assertEqual(">=1.2.0,<2.0.0", str(expression))
				self.assertIn(SemanticVersion.Parse("1.5.0"), expression)
				self.assertNotIn(SemanticVersion.Parse("2.0.0"), expression)

	def test_ForeignSyntaxIsRejected(self) -> None:
		"""Another ecosystem's shorthand is not silently read as a version."""
		for source in ("~=1.2.3", "^1.2.3", "[1.0.0,2.0.0)", ">=1.0.0 && <2.0.0"):
			with self.subTest(source=source):
				with self.assertRaises(ValueError):
					VersionExpression.Parse(source)

	def test_AnUnparsableVersionIsRejected(self) -> None:
		with self.assertRaises(ValueError):
			VersionExpression.Parse(">=not-a-version")

	def test_ARejectedExpression(self) -> None:
		with self.assertRaises(TypeError):
			VersionExpression.Parse(42)

	def test_AnotherVersionType(self) -> None:
		expression = VersionExpression.Parse(">=3.9", versionType=PythonVersion)

		self.assertIsInstance(expression.Constraints[0].Version, PythonVersion)
		self.assertIn(PythonVersion.Parse("3.14"), expression)


class Matching(Testcase):
	"""Holding a version against every constraint of an expression."""

	def test_EveryConstraintHasToHold(self) -> None:
		expression = VersionExpression.Parse(">=1.2.0,<2.0.0")

		for version, expected in (("1.1.0", False), ("1.2.0", True), ("1.5.0", True), ("2.0.0", False)):
			with self.subTest(version=version):
				self.assertEqual(expected, SemanticVersion.Parse(version) in expression)

	def test_AnEmptyExpressionMatchesEveryVersion(self) -> None:
		expression = VersionExpression.Parse("")

		for version in ("0.0.1", "1.2.0", "42.0.0"):
			with self.subTest(version=version):
				self.assertIn(SemanticVersion.Parse(version), expression)

	def test_AnExclusionIsHonoured(self) -> None:
		"""``>=1.0.0,!=1.3.0`` is how a single broken release is skipped."""
		expression = VersionExpression.Parse(">=1.0.0,!=1.3.0")

		self.assertIn(SemanticVersion.Parse("1.2.0"), expression)
		self.assertNotIn(SemanticVersion.Parse("1.3.0"), expression)
		self.assertIn(SemanticVersion.Parse("1.4.0"), expression)

	def test_ARejectedVersion(self) -> None:
		with self.assertRaises(TypeError):
			"1.2.0" in VersionExpression.Parse(">=1.0.0")


class PythonDialect(Testcase):
	"""The PEP 440 dialect, which adds the compatible release operator."""

	def test_TheBaseDialectHasNoCompatibleRelease(self) -> None:
		""":class:`VersionExpression` is ecosystem-neutral; ``~=`` is PEP 440's."""
		with self.assertRaises(ValueError):
			VersionExpression.Parse("~=1.2.3")

	def test_CompatibleReleaseIsParsed(self) -> None:
		expression = PythonVersionExpression.Parse("~=1.2.3")

		self.assertEqual(1, len(expression))
		self.assertIsInstance(expression.Constraints[0], CompatibleVersionConstraint)
		self.assertEqual("~=1.2.3", str(expression))

	def test_CompatibleReleaseMatchesPEP440(self) -> None:
		"""The upper bound is the part left of the last one written, incremented - checked against ``packaging``."""
		for source, upperBound, matching, notMatching in (
			("~=1.2",     "2",     ("1.2.0", "1.9.9"), ("1.1.9", "2.0.0")),
			("~=1.2.3",   "1.3",   ("1.2.3", "1.2.9"), ("1.2.2", "1.3.0")),
			("~=1.2.3.4", "1.2.4", ("1.2.3.4", "1.2.3.9"), ("1.2.3.3", "1.2.4.0")),
		):
			with self.subTest(source=source):
				expression = PythonVersionExpression.Parse(source)
				constraint = expression.Constraints[0]

				self.assertEqual(upperBound, str(constraint.UpperBound))
				for version in matching:
					self.assertIn(PythonVersion.Parse(version), expression)
				for version in notMatching:
					self.assertNotIn(PythonVersion.Parse(version), expression)

	def test_CompatibleReleaseNeedsTwoParts(self) -> None:
		"""``~=1`` would say what ``>=1`` says, so PEP 440 rejects it and so do we."""
		with self.assertRaises(ValueError):
			PythonVersionExpression.Parse("~=1")

	def test_CompatibleReleaseKeepsTheVersionType(self) -> None:
		expression = PythonVersionExpression.Parse("~=3.9")

		self.assertIsInstance(expression.Constraints[0].Version, PythonVersion)
		self.assertIsInstance(expression.Constraints[0].UpperBound, PythonVersion)
		self.assertIn(PythonVersion.Parse("3.14"), expression)
		self.assertNotIn(PythonVersion.Parse("4.0"), expression)

	def test_TheOrderingComparisonsStillWork(self) -> None:
		expression = PythonVersionExpression.Parse(">=1.0,!=1.3,<2.0")

		self.assertIn(PythonVersion.Parse("1.2"), expression)
		self.assertNotIn(PythonVersion.Parse("1.3"), expression)
		self.assertNotIn(PythonVersion.Parse("2.0"), expression)

	def test_APlainConstraintRejectsCompatibleRelease(self) -> None:
		"""``VersionConstraint`` cannot express it; the dedicated class derives the upper bound."""
		with self.assertRaises(ValueError):
			VersionConstraint(VersionComparison.CompatibleRelease, SemanticVersion.Parse("1.2.3"))

	def test_ACompatibleReleaseNeedsASemanticVersion(self) -> None:
		with self.assertRaises(TypeError):
			CompatibleVersionConstraint("1.2.3")


class NPMDialect(Testcase):
	"""npm's dialect: whitespace separated, ``=`` for equality, no ``!=``, plus ``^`` and ``~``."""

	def test_WhitespaceSeparates(self) -> None:
		expression = NPMVersionExpression.Parse(">=1.2.0 <2.0.0")

		self.assertEqual(">=1.2.0 <2.0.0", str(expression))
		self.assertIn(SemanticVersion.Parse("1.5.0"), expression)
		self.assertNotIn(SemanticVersion.Parse("2.0.0"), expression)

	def test_WhatNPMRejectsIsRejected(self) -> None:
		"""A comma, ``==`` and ``!=`` are all syntax errors in npm - checked against npm's own ``semver``."""
		for source in (">=1.2.0,<2.0.0", "==1.2.3", "!=1.2.3"):
			with self.subTest(source=source):
				with self.assertRaises(ValueError):
					NPMVersionExpression.Parse(source)

	def test_EqualityIsASingleEquals(self) -> None:
		expression = NPMVersionExpression.Parse("=1.2.3")

		self.assertEqual("=1.2.3", str(expression))
		self.assertIn(SemanticVersion.Parse("1.2.3"), expression)
		self.assertNotIn(SemanticVersion.Parse("1.2.4"), expression)

	def test_CaretPivotsOnTheLeftmostNonZeroPart(self) -> None:
		"""Bounds checked against npm's ``semver.validRange``."""
		for source, upperBound in (
			("^1.2.3", "2"), ("^1.2", "2"), ("^1", "2"),
			("^0.2.3", "0.3"), ("^0.2", "0.3"),
			("^0.0.3", "0.0.4"), ("^0.0.0", "0.0.1"),
			("^0.0", "0.1"), ("^0", "1"),
		):
			with self.subTest(source=source):
				expression = NPMVersionExpression.Parse(source)

				self.assertIsInstance(expression.Constraints[0], CaretVersionConstraint)
				self.assertEqual(upperBound, str(expression.Constraints[0].UpperBound))

	def test_TildePivotsOnTheMinorPart(self) -> None:
		for source, upperBound in (("~1.2.3", "1.3"), ("~1.2", "1.3"), ("~1", "2"), ("~0.2.3", "0.3"), ("~0", "1")):
			with self.subTest(source=source):
				expression = NPMVersionExpression.Parse(source)

				self.assertIsInstance(expression.Constraints[0], TildeVersionConstraint)
				self.assertEqual(upperBound, str(expression.Constraints[0].UpperBound))

	def test_TildeIsNotPEP440sCompatibleRelease(self) -> None:
		"""They agree on three parts and disagree on two, which is why they are separate classes."""
		self.assertEqual("1.3", str(NPMVersionExpression.Parse("~1.2.3").Constraints[0].UpperBound))
		self.assertEqual("1.3", str(PythonVersionExpression.Parse("~=1.2.3").Constraints[0].UpperBound))

		self.assertEqual("1.3", str(NPMVersionExpression.Parse("~1.2").Constraints[0].UpperBound))
		self.assertEqual("2",   str(PythonVersionExpression.Parse("~=1.2").Constraints[0].UpperBound))


class DebianDialect(Testcase):
	"""Debian's dialect: ``<<`` and ``>>`` are strict, ``=`` is equality, and there is no ``!=``."""

	def test_TheStrictOperators(self) -> None:
		expression = DebianVersionExpression.Parse(">> 1.2.3")

		self.assertEqual(">>1.2.3", str(expression))
		self.assertIn(SemanticVersion.Parse("1.3.0"), expression)
		self.assertNotIn(SemanticVersion.Parse("1.2.3"), expression)

	def test_EqualityIsASingleEquals(self) -> None:
		expression = DebianVersionExpression.Parse("= 1.2.3")

		self.assertEqual("=1.2.3", str(expression))
		self.assertIn(SemanticVersion.Parse("1.2.3"), expression)

	def test_TheObsoleteSpellingsAreRejected(self) -> None:
		"""``dpkg`` still takes ``<`` and ``>`` but warns; they meant ``<=`` and ``>=``, so reading them
		as strict would invert their meaning."""
		for source in ("< 1.0", "> 1.0"):
			with self.subTest(source=source):
				with self.assertRaises(ValueError):
					DebianVersionExpression.Parse(source)

	def test_ThereIsNoNotEqual(self) -> None:
		with self.assertRaises(ValueError):
			DebianVersionExpression.Parse("!= 1.0")

	def test_NoShorthandIsAccepted(self) -> None:
		for source in ("~= 1.2", "^1.2.3", "~1.2.3"):
			with self.subTest(source=source):
				with self.assertRaises(ValueError):
					DebianVersionExpression.Parse(source)


class DialectsAreIndependent(Testcase):
	"""Each dialect accepts its own syntax and refuses the others'."""

	def test_EachDialectRefusesTheOthersShorthand(self) -> None:
		for dialect, accepted, refused in (
			(PythonVersionExpression, "~=1.2.3", ("^1.2.3", "~1.2.3")),
			(NPMVersionExpression,    "^1.2.3", ("~=1.2.3",)),
			(DebianVersionExpression, ">> 1.2", ("~=1.2.3", "^1.2.3")),
			(VersionExpression,       ">=1.2.3", ("~=1.2.3", "^1.2.3", "~1.2.3")),
		):
			with self.subTest(dialect=dialect.__name__):
				self.assertEqual(1, len(dialect.Parse(accepted)))
				for source in refused:
					with self.assertRaises(ValueError):
						dialect.Parse(source)


class ReviewFollowUps(Testcase):
	"""What the review of #369 asked for."""

	def test_AShorthandConvertsToAVersionRange(self) -> None:
		"""A shorthand knows both bounds, so the conversion is exact."""
		for source, dialect, lower, upper in (
			("~=1.2.3", PythonVersionExpression, "1.2.3", "1.3"),
			("^1.2.3",  NPMVersionExpression,    "1.2.3", "2"),
			("~1.2.3",  NPMVersionExpression,    "1.2.3", "1.3"),
		):
			with self.subTest(source=source):
				versionRange = dialect.Parse(source).Constraints[0].ToVersionRange()

				self.assertIsInstance(versionRange, VersionRange)
				self.assertEqual(lower, str(versionRange.LowerBound))
				self.assertEqual(upper, str(versionRange.UpperBound))

	def test_TheConvertedRangeAgreesWithTheConstraint(self) -> None:
		constraint = PythonVersionExpression.Parse("~=1.2.3").Constraints[0]
		versionRange = constraint.ToVersionRange()

		for version in ("1.2.2", "1.2.3", "1.2.9", "1.3.0"):
			with self.subTest(version=version):
				parsed = PythonVersion.Parse(version)

				self.assertEqual(parsed in constraint, parsed in versionRange)

	def test_TheShorthandBaseClassIsAbstract(self) -> None:
		"""``@classmethod`` around ``@abstractmethod`` hid this from ``ExtendedType``; it is an instance method now."""
		from pyTooling.MetaClasses import AbstractClassError

		with self.assertRaises(AbstractClassError):
			RangeVersionConstraint(VersionComparison.CompatibleRelease, SemanticVersion.Parse("1.2.3"))

	def test_AnUnknownComparisonIsRejectedRatherThanGuessed(self) -> None:
		"""A shorthand comparison in a plain constraint used to fall through to ``>=``."""
		constraint = VersionConstraint(VersionComparison.Equal, SemanticVersion.Parse("1.2.3"))
		constraint._comparison = VersionComparison.Caret

		with self.assertRaises(ValueError):
			SemanticVersion.Parse("1.2.3") in constraint

	def test_TheConstraintsParameterIsChecked(self) -> None:
		with self.assertRaises(ValueError):
			VersionExpression(None)

		with self.assertRaises(TypeError):
			VersionExpression(42)


class EpochsInExpressions(Testcase):
	"""How an epoch - :pep:`440`'s ``1!1.0`` and Debian's ``2:1.0`` - travels through an expression."""

	def test_TheEpochSeparatorIsNotAnOperator(self) -> None:
		"""``!`` starts ``!=`` *and* separates a :pep:`440` epoch, so it may not be excluded from a version."""
		expression = PythonVersionExpression.Parse(">=1!1.0")

		self.assertEqual(">=1!1.0", str(expression))
		self.assertEqual(1, expression.Constraints[0].Version.Epoch)

	def test_NotEqualIsStillAnOperator(self) -> None:
		"""Allowing ``!`` inside a version must not stop ``!=`` being read where a constraint begins."""
		expression = PythonVersionExpression.Parse(">=1.0,!=1.3")

		self.assertEqual(">=1.0,!=1.3", str(expression))
		self.assertEqual(VersionComparison.Unequal, expression.Constraints[1].Comparison)

	def test_AnEpochOutranksTheReleaseInAComparison(self) -> None:
		expression = PythonVersionExpression.Parse(">=1!1.0")

		self.assertIn(PythonVersion.Parse("1!2.0"), expression)
		self.assertIn(PythonVersion.Parse("2!0.1"), expression)
		self.assertNotIn(PythonVersion.Parse("99.0"), expression)

	def test_TheBaseDialectTakesDebianEpochs(self) -> None:
		expression = VersionExpression.Parse(">=2:1.0.0")

		self.assertIn(SemanticVersion.Parse("2:9.9.9"), expression)
		self.assertNotIn(SemanticVersion.Parse("99.0.0"), expression)

	def test_AShorthandBoundStaysInTheSameEpoch(self) -> None:
		"""A bound built in epoch 0 outranks nothing, so the constraint would match no version at all."""
		constraint = PythonVersionExpression.Parse("~=2!1.2.3").Constraints[0]

		self.assertEqual(2, constraint.UpperBound.Epoch)
		self.assertEqual("2!1.3", str(constraint.UpperBound))

		self.assertIn(PythonVersion.Parse("2!1.2.9"), constraint)
		self.assertNotIn(PythonVersion.Parse("2!1.3.0"), constraint)
		self.assertNotIn(PythonVersion.Parse("1!9.9.9"), constraint)

	def test_AShorthandWithoutAnEpochGainsNone(self) -> None:
		constraint = PythonVersionExpression.Parse("~=1.2.3").Constraints[0]

		self.assertEqual(0, constraint.UpperBound.Epoch)
		self.assertEqual("1.3", str(constraint.UpperBound))

	def test_EveryShorthandCarriesTheEpoch(self) -> None:
		"""All three derive a bound from the written version's parts, so all three have to keep its epoch."""
		for source, dialect, bound in (
			("~=2!1.2.3", PythonVersionExpression, "2!1.3"),
			("^2:1.2.3",  NPMVersionExpression,    "2:2"),
			("~2:1.2.3",  NPMVersionExpression,    "2:1.3"),
		):
			with self.subTest(source=source):
				self.assertEqual(bound, str(dialect.Parse(source).Constraints[0].UpperBound))


class ConvertingToVersionRanges(Testcase):
	"""Every constraint but ``!=`` is an interval, and a conjunction of them is their intersection."""

	def test_EachComparisonBecomesItsInterval(self) -> None:
		for source, lower, upper, exclusive in (
			(">=1.2.0", "1.2.0", None,    None),
			(">1.2.0",  "1.2.0", None,    RangeBoundHandling.LowerBoundExclusive),
			("<=2.0.0", None,    "2.0.0", None),
			("<2.0.0",  None,    "2.0.0", RangeBoundHandling.UpperBoundExclusive),
			("==1.2.0", "1.2.0", "1.2.0", None),
		):
			with self.subTest(source=source):
				versionRange = VersionExpression.Parse(source).ToVersionRange()

				self.assertEqual(lower, None if versionRange.LowerBound is None else str(versionRange.LowerBound))
				self.assertEqual(upper, None if versionRange.UpperBound is None else str(versionRange.UpperBound))
				if exclusive is not None:
					self.assertIn(exclusive, versionRange.BoundHandling)

	def test_AConjunctionIsTheIntersection(self) -> None:
		"""``>=1.2.0,<2.0.0`` is ``[1.2.0, 2.0.0)`` - the upper bound stays exclusive through the intersection."""
		versionRange = VersionExpression.Parse(">=1.2.0,<2.0.0").ToVersionRange()

		self.assertEqual("1.2.0", str(versionRange.LowerBound))
		self.assertEqual("2.0.0", str(versionRange.UpperBound))
		self.assertIn(RangeBoundHandling.UpperBoundExclusive, versionRange.BoundHandling)
		self.assertNotIn(SemanticVersion.Parse("2.0.0"), versionRange)

	def test_TheRangeAgreesWithTheExpression(self) -> None:
		"""The conversion is only worth anything if both answer ``in`` identically."""
		probes = ("0.9.0", "1.0.0", "1.2.0", "1.2.3", "1.5.0", "1.9.9", "2.0.0", "2.0.1", "9.9.9")

		for source, dialect, versionType in (
			(">=1.2.0",       VersionExpression,       SemanticVersion),
			(">1.2.0,<=2.0.0", VersionExpression,      SemanticVersion),
			("==1.2.0",       VersionExpression,       SemanticVersion),
			("~=1.2.3",       PythonVersionExpression, PythonVersion),
			("^1.2.3",        NPMVersionExpression,    SemanticVersion),
			("~1.2.3",        NPMVersionExpression,    SemanticVersion),
		):
			with self.subTest(source=source):
				expression = dialect.Parse(source)
				versionRange = expression.ToVersionRange()

				for probe in probes:
					version = versionType.Parse(probe)

					self.assertEqual(version in expression, version in versionRange, probe)

	def test_AnEmptyExpressionIsTheUnboundedRange(self) -> None:
		versionRange = VersionExpression.Parse("").ToVersionRange()

		self.assertIsNone(versionRange.LowerBound)
		self.assertIsNone(versionRange.UpperBound)

	def test_UnequalHasNoRange(self) -> None:
		"""The complement of a version is a union of two intervals, which a range cannot hold."""
		constraint = VersionConstraint(VersionComparison.Unequal, SemanticVersion.Parse("1.3.0"))

		with self.assertRaises(ValueError):
			constraint.ToVersionRange()

	def test_AnExpressionContainingUnequalHasNoRange(self) -> None:
		"""``>=1.0,!=1.3,<2.0`` is an ordinary requirement, and it has no single range."""
		with self.assertRaises(ValueError):
			VersionExpression.Parse(">=1.0.0,!=1.3.0,<2.0.0").ToVersionRange()

	def test_ContradictoryConstraintsHaveNoRange(self) -> None:
		with self.assertRaises(ValueError):
			VersionExpression.Parse(">=3.0.0,<2.0.0").ToVersionRange()

	def test_AShorthandKeepsItsOwnConversion(self) -> None:
		""":class:`RangeVersionConstraint` overrides it, since it already holds both bounds."""
		constraint = PythonVersionExpression.Parse("~=1.2.3").Constraints[0]

		self.assertIsInstance(constraint, RangeVersionConstraint)
		self.assertEqual("1.2.3", str(constraint.ToVersionRange().LowerBound))
		self.assertEqual("1.3", str(constraint.ToVersionRange().UpperBound))
