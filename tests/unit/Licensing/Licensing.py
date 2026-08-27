# ==================================================================================================================== #
#             _____           _ _               _     _                    _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | |   (_) ___ ___ _ __  ___(_)_ __   __ _                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |   | |/ __/ _ \ '_ \/ __| | '_ \ / _` |                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___| | (_|  __/ | | \__ \ | | | | (_| |                              #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____|_|\___\___|_| |_|___/_|_| |_|\__, |                              #
# |_|    |___/                          |___/                                      |___/                               #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.Licensing`: the license data class and the SPDX license mappings.
"""
from pyTooling.Licensing import Apache_2_0_License, LICENSES, PYTHON_LICENSE_NAMES, SPDX_INDEX, License
from pyTooling.Licensing import AndOperator, LicenseException, LicenseExpression, LicenseReference
from pyTooling.Licensing import MIT_License, OrLaterOperator, OrOperator, SPDXLicense, WithOperator
from pyTooling.Testing   import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class LicenseDataClass(Testcase):
	def test_Properies(self) -> None:
		license = License("spdx", "License Name", False, False)
		self.assertEqual("spdx", license.SPDXIdentifier)
		self.assertEqual("License Name", license.Name)
		self.assertEqual(False, license.OSIApproved)
		self.assertEqual(False, license.FSFApproved)

	def test_ClassifierConversion(self) -> None:
		license = License("Apache-2.0", "License Name", True, False)
		self.assertEqual("License :: OSI Approved :: Apache Software License", license.PythonClassifier)

	def test_ClassifierConversionException(self) -> None:
		license = License("spdx", "License Name", False, False)
		with self.assertRaises(ValueError):
			_ = license.PythonClassifier

	def test_Equalality(self) -> None:
		license1 = License("spdx", "License Name", False, False)
		license2 = License("spdx", "License Name", False, False)
		license3 = License("SPDX", "License Name", False, False)

		self.assertTrue(license1 == license2)
		self.assertTrue(license1 != license3)
		self.assertTrue(license1 == "spdx", "A license equals its SPDX identifier as a string.")
		self.assertTrue(license1 != "other", "A different identifier is a different license.")
		self.assertTrue("spdx" == license1, "The comparison is symmetric - 'str' defers to the reflected operand.")
		with self.assertRaises(TypeError):
			_ = license1 == 42
		with self.assertRaises(TypeError):
			_ = license1 != 42

	def test_Compatibility(self) -> None:
		license1 = License("spdx", "License Name", False, False)
		license2 = License("spdx", "License Name", False, False)
		with self.assertRaises(NotImplementedError):
			_ = license1 <= license2

		with self.assertRaises(NotImplementedError):
			_ = license1 >= license2

	def test_ToString(self) -> None:
		license = License("spdx", "License Name", False, False)

		self.assertEqual("spdx", f"{license!r}")
		self.assertEqual("License Name", f"{license!s}")


class SPDXLicenses(Testcase):
	def test_Apache(self) -> None:
		self.assertIn("Apache-2.0", SPDX_INDEX)
		self.assertIn("Apache-2.0", PYTHON_LICENSE_NAMES)


# class PythonClassifiers(Testcase):
# 	def test_OSIApproved(self) -> None:
# 		for spdxId, item in PYTHON_LICENSE_NAMES.items():
# 			license = SPDX_INDEX[spdxId]
# 			self.assertEqual("OSI Approved" in item.Classifier, license.OSIApproved)


class Hashing(Testcase):
	"""A license is hashable, so it can be a set element or a dictionary key."""

	def test_TheHashIsTheIdentifiersHash(self) -> None:
		""":meth:`~pyTooling.Licensing.License.__eq__` compares the identifier, so the hash has to follow it."""
		self.assertEqual(hash("Apache-2.0"), hash(Apache_2_0_License))

	def test_ALicenseIsFoundAmongItsIdentifiers(self) -> None:
		"""Equal to the string and hashing like it, so a set of identifiers contains the license."""
		self.assertIn(Apache_2_0_License, {"Apache-2.0", "MIT"})

	def test_EqualLicensesHashEqually(self) -> None:
		"""Two objects that compare equal must hash equally - a set and a dict rely on it."""
		other = License("Apache-2.0", "A different name for the same license")

		self.assertEqual(Apache_2_0_License, other)
		self.assertEqual(hash(Apache_2_0_License), hash(other))

	def test_ALicenseIsASetElement(self) -> None:
		self.assertSetEqual({Apache_2_0_License}, {Apache_2_0_License, License("Apache-2.0", "same identifier")})

	def test_ALicenseIsADictionaryKey(self) -> None:
		self.assertEqual("found", {Apache_2_0_License: "found"}[License("Apache-2.0", "same identifier")])

	def test_EveryPredefinedLicenseIsDistinct(self) -> None:
		self.assertEqual(len(LICENSES), len(set(LICENSES)), "Two predefined licenses share an SPDX identifier.")


class SPDXIndex(Testcase):
	"""Every predefined license is consistent with SPDX and with PyPI's classifier list."""

	def test_TheIndexIsBuiltFromTheLicenseTuple(self) -> None:
		"""'LICENSES' is the list; 'SPDX_INDEX' is that list keyed by identifier, so neither can drift."""

		self.assertEqual(len(LICENSES), len(SPDX_INDEX), "A license is listed twice under the same identifier.")
		self.assertSetEqual(set(LICENSES), set(SPDX_INDEX.values()))

	def test_TheIndexIsKeyedByTheSPDXIdentifier(self) -> None:
		for spdxIdentifier, spdxLicense in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertEqual(spdxIdentifier, spdxLicense.SPDXIdentifier)

	def test_EveryClassifierIsARealClassifier(self) -> None:
		"""The strings are checked against PyPI's own list, not against what looked right when they were typed."""

		from trove_classifiers import classifiers

		for spdxIdentifier, spdxLicense in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertIn(spdxLicense.PythonClassifier, classifiers)

	def test_OSIApprovalMatchesTheClassifier(self) -> None:
		"""PyPI puts an OSI-approved license under 'OSI Approved ::', so the flag and the string must agree."""

		for spdxIdentifier, spdxLicense in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertEqual(
					spdxLicense.OSIApproved,
					spdxLicense.PythonClassifier.startswith("License :: OSI Approved :: ")
				)

	def test_CC0IsNotOSIApproved(self) -> None:
		"""One license where the two differ, so the check above cannot pass vacuously."""

		from pyTooling.Licensing import CC0_1_0

		self.assertFalse(CC0_1_0.OSIApproved)
		self.assertTrue(CC0_1_0.FSFApproved)
		self.assertEqual(
			"License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
			CC0_1_0.PythonClassifier
		)

	def test_EveryLicenseHasAPythonName(self) -> None:
		for spdxIdentifier, spdxLicense in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertNotEqual("", spdxLicense.PythonLicenseName)

	def test_TheOriginalFourAreUnchanged(self) -> None:
		"""The licenses that existed before keep their identifiers, names and short names."""

		from pyTooling.Licensing import BSD_3_Clause_License, GPL_2_0_or_later, MIT_License

		self.assertEqual("Apache 2.0", Apache_2_0_License.PythonLicenseName)
		self.assertEqual("BSD", BSD_3_Clause_License.PythonLicenseName)
		self.assertEqual("MIT", MIT_License.PythonLicenseName)
		self.assertEqual("GPL-2.0-or-later", GPL_2_0_or_later.PythonLicenseName)



class ParsingExpressions(Testcase):
	"""Parsing SPDX license expressions into a tree."""

	def test_SingleLicense(self) -> None:
		expression = LicenseExpression.Parse("MIT")

		self.assertIsInstance(expression, SPDXLicense)
		self.assertIs(MIT_License, expression.License)
		self.assertIsNone(expression.Parent)

	def test_And(self) -> None:
		expression = LicenseExpression.Parse("Apache-2.0 AND MIT")

		self.assertIsInstance(expression, AndOperator)
		self.assertIs(Apache_2_0_License, expression.Left.License)
		self.assertIs(MIT_License, expression.Right.License)

	def test_Or(self) -> None:
		expression = LicenseExpression.Parse("Apache-2.0 OR BSD-2-Clause")

		self.assertIsInstance(expression, OrOperator)

	def test_With(self) -> None:
		expression = LicenseExpression.Parse("Apache-2.0 WITH LLVM-exception")

		self.assertIsInstance(expression, WithOperator)
		self.assertIsInstance(expression.Right, LicenseException)
		self.assertEqual("LLVM-exception", expression.Right.Identifier)

	def test_OrLater(self) -> None:
		"""``GPL-2.0-only+`` is the deprecated spelling SPDX still accepts."""
		expression = LicenseExpression.Parse("GPL-2.0-only+")

		self.assertIsInstance(expression, OrLaterOperator)
		self.assertIsInstance(expression.Operand, SPDXLicense)

	def test_Precedence(self) -> None:
		"""The spec's own example: AND is applied before OR."""
		expression = LicenseExpression.Parse("LGPL-2.1-only OR BSD-3-Clause AND MIT")

		self.assertIsInstance(expression, OrOperator)
		self.assertIsInstance(expression.Right, AndOperator)

	def test_Parentheses(self) -> None:
		expression = LicenseExpression.Parse("(LGPL-2.1-only OR BSD-3-Clause) AND MIT")

		self.assertIsInstance(expression, AndOperator)
		self.assertIsInstance(expression.Left, OrOperator)

	def test_KeywordsAreCaseInsensitive(self) -> None:
		"""Published metadata writes ``and`` as often as ``AND``."""
		expression = LicenseExpression.Parse("MIT and Apache-2.0")

		self.assertIsInstance(expression, AndOperator)

	def test_LicenseReference(self) -> None:
		expression = LicenseExpression.Parse("LicenseRef-Proprietary")

		self.assertIsInstance(expression, LicenseReference)
		self.assertEqual("Proprietary", expression.LicenseIdentifier)
		self.assertIsNone(expression.DocumentIdentifier)
		self.assertEqual((), expression.Licenses)

	def test_DocumentReference(self) -> None:
		expression = LicenseExpression.Parse("DocumentRef-spdx-tool:LicenseRef-MyLicense")

		self.assertIsInstance(expression, LicenseReference)
		self.assertEqual("MyLicense", expression.LicenseIdentifier)
		self.assertEqual("spdx-tool", expression.DocumentIdentifier)


class ExpressionTree(Testcase):
	"""What a parsed expression knows about itself."""

	def test_ParentAndRoot(self) -> None:
		expression = LicenseExpression.Parse("LGPL-2.1-only OR BSD-3-Clause AND MIT")
		leaf = expression.Right.Right

		self.assertIs(expression.Right, leaf.Parent)
		self.assertIs(expression, leaf.Root)
		self.assertIsNone(expression.Parent)

	def test_ASharedLicenseGetsItsOwnLeaf(self) -> None:
		"""
		The predefined licenses are shared objects, so they can't carry a parent.

		:class:`SPDXLicense` is the wrapper that gives one a place in a tree, and two expressions naming the same
		license get two leaves around one license.
		"""
		first = LicenseExpression.Parse("MIT AND Apache-2.0")
		second = LicenseExpression.Parse("MIT OR ISC")

		self.assertIs(first.Left.License, second.Left.License)
		self.assertIsNot(first.Left, second.Left)
		self.assertIs(first, first.Left.Parent)
		self.assertIs(second, second.Left.Parent)

	def test_Licenses(self) -> None:
		expression = LicenseExpression.Parse("LGPL-2.1-only OR BSD-3-Clause AND MIT")

		self.assertEqual(
			["LGPL-2.1-only", "BSD-3-Clause", "MIT"],
			[spdxLicense.SPDXIdentifier for spdxLicense in expression.Licenses]
		)

	def test_LicensesKeepsDuplicates(self) -> None:
		"""``MIT AND MIT`` is not the same statement as ``MIT``, so deduplicating isn't this class' decision."""
		expression = LicenseExpression.Parse("MIT AND MIT")

		self.assertEqual(2, len(expression.Licenses))


class FormattingExpressions(Testcase):
	"""Rendering an expression back to SPDX syntax."""

	def test_RoundTrip(self) -> None:
		for expression in (
			"MIT",
			"Apache-2.0 AND MIT",
			"Apache-2.0 OR BSD-2-Clause",
			"LGPL-2.1-only OR BSD-3-Clause AND MIT",
			"(LGPL-2.1-only OR BSD-3-Clause) AND MIT",
			"Apache-2.0 WITH LLVM-exception",
			"GPL-2.0-only+",
			"LicenseRef-Proprietary",
			"DocumentRef-spdx-tool:LicenseRef-MyLicense",
		):
			self.assertEqual(expression, str(LicenseExpression.Parse(expression)))

	def test_RedundantParenthesesAreDropped(self) -> None:
		"""Only the parentheses the default precedence needs are written back."""
		self.assertEqual("Apache-2.0 AND MIT", str(LicenseExpression.Parse("(Apache-2.0 AND MIT)")))
		self.assertEqual("LGPL-2.1-only OR BSD-3-Clause AND MIT",
		                 str(LicenseExpression.Parse("LGPL-2.1-only OR (BSD-3-Clause AND MIT)")))

	def test_KeywordsAreNormalized(self) -> None:
		self.assertEqual("MIT AND Apache-2.0", str(LicenseExpression.Parse("MIT and Apache-2.0")))


class MalformedExpressions(Testcase):
	"""Expressions that can't be parsed."""

	def test_Empty(self) -> None:
		for expression in ("", "   "):
			with self.assertRaises(ValueError):
				LicenseExpression.Parse(expression)

	def test_UnknownLicense(self) -> None:
		with self.assertRaises(ValueError):
			LicenseExpression.Parse("Definitely-Not-A-License")

	def test_UnbalancedParentheses(self) -> None:
		for expression in ("(MIT AND Apache-2.0", "MIT AND Apache-2.0)", ")MIT("):
			with self.assertRaises(ValueError):
				LicenseExpression.Parse(expression)

	def test_DanglingOperator(self) -> None:
		for expression in ("MIT AND", "MIT OR", "Apache-2.0 WITH"):
			with self.assertRaises(ValueError):
				LicenseExpression.Parse(expression)

	def test_TrailingInput(self) -> None:
		with self.assertRaises(ValueError):
			LicenseExpression.Parse("MIT Apache-2.0")
