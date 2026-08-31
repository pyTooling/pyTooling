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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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

	def test_AnEmptyConstraintIsRejected(self) -> None:
		for source in (">=1.2.0,", ",<2.0.0", ">=1.2.0,,<2.0.0"):
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
