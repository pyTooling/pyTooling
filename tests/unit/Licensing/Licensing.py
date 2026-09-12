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
from pyTooling.Licensing import CC0_1_0, GPL_2_0_only, GPL_2_0_or_later, OSI_LICENSE_URLS, PSF_2_0_License
from pyTooling.Licensing import LicenseAbsence, ProprietaryLicense, UnknownLicense
from pyTooling.Licensing import BSD_3_Clause_License, GPL_3_0_only, GPL_3_0_or_later
from pyTooling.Licensing import LICENSE_TEXT_URLS, LICENSE_URLS
from pyTooling.Licensing import AndOperator, BinaryOperator, LicenseException, LicenseExpression
from pyTooling.Licensing import ISC_License, LicenseExpressionError, LicenseReference, LicensingError
from pyTooling.Licensing import MIT_License
from pyTooling.Licensing import OrLaterOperator, OrOperator
from pyTooling.Licensing import SPDXLicense
from pyTooling.Licensing import BaseLicense, Operator, UnaryOperator, WithOperator
from pyTooling.MetaClasses import AbstractClassError
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


class IteratingExpressions(Testcase):
	"""The depth-first walk an expression offers over its own nodes."""

	@staticmethod
	def _label(node) -> str:
		if isinstance(node, (SPDXLicense, LicenseException)):
			return node.Identifier
		elif isinstance(node, OrLaterOperator):
			return "+"

		return node.KEYWORD

	def test_ALeafIsItsOwnExpression(self) -> None:
		leaf = SPDXLicense(MIT_License)

		self.assertEqual([leaf], list(leaf.IterateExpression()))

	def test_InfixOrder(self) -> None:
		"""A binary operator is yielded between its two operands, so the walk reads like the expression."""
		expression = LicenseExpression.Parse("MIT AND Apache-2.0")

		self.assertEqual(["MIT", "AND", "Apache-2.0"], [self._label(node) for node in expression.IterateExpression()])

	def test_TheSuffixOperatorComesAfterItsOperand(self) -> None:
		"""``+`` is written after the license it applies to, so it is yielded after it."""
		expression = LicenseExpression.Parse("MIT+")

		self.assertEqual(["MIT", "+"], [self._label(node) for node in expression.IterateExpression()])

	def test_ANestedExpressionReadsInWritingOrder(self) -> None:
		expression = LicenseExpression.Parse("(MIT OR ISC) AND Apache-2.0 WITH LLVM-exception")

		self.assertEqual(
			["MIT", "OR", "ISC", "AND", "Apache-2.0", "WITH", "LLVM-exception"],
			[self._label(node) for node in expression.IterateExpression()]
		)

	def test_EveryNodeIsYieldedOnce(self) -> None:
		"""The walk covers the operators too, not only the leaves - they carry a root as well."""
		expression = LicenseExpression.Parse("LGPL-2.1-only OR BSD-3-Clause AND MIT")
		nodes = list(expression.IterateExpression())

		self.assertEqual(5, len(nodes))
		self.assertEqual(5, len({id(node) for node in nodes}))
		self.assertIn(expression, nodes)
		self.assertTrue(all(node.Root is expression for node in nodes))

	def test_AnIncompleteOperatorYieldsWhatItHas(self) -> None:
		operator = AndOperator(SPDXLicense(MIT_License))

		self.assertEqual(["MIT", "AND"], [self._label(node) for node in operator.IterateExpression()])


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
		"""An empty string is a bad argument, like every other empty identifier in this module."""
		with self.assertRaises(ValueError):
			LicenseExpression.Parse("")

	def test_WhitespaceOnly(self) -> None:
		"""A non-empty string that tokenizes to nothing is a bad expression, not a bad argument."""
		with self.assertRaises(LicenseExpressionError):
			LicenseExpression.Parse("   ")

	def test_UnknownLicense(self) -> None:
		with self.assertRaises(LicenseExpressionError):
			LicenseExpression.Parse("Definitely-Not-A-License")

	def test_UnbalancedParentheses(self) -> None:
		for expression in ("(MIT AND Apache-2.0", "MIT AND Apache-2.0)", ")MIT("):
			with self.assertRaises(LicenseExpressionError):
				LicenseExpression.Parse(expression)

	def test_DanglingOperator(self) -> None:
		for expression in ("MIT AND", "MIT OR", "Apache-2.0 WITH"):
			with self.assertRaises(LicenseExpressionError):
				LicenseExpression.Parse(expression)

	def test_TrailingInput(self) -> None:
		with self.assertRaises(LicenseExpressionError):
			LicenseExpression.Parse("MIT Apache-2.0")

	def test_AMalformedExpressionIsALicensingError(self) -> None:
		"""The dedicated exception stays catchable through the module's base exception."""
		with self.assertRaises(LicensingError):
			LicenseExpression.Parse("MIT AND")


class ConstructingExpressions(Testcase):
	"""Building an expression tree by hand, top-down as well as bottom-up."""

	def test_BottomUp(self) -> None:
		expression = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))

		self.assertEqual("Apache-2.0 AND MIT", str(expression))
		self.assertIs(expression, expression.Left.Parent)
		self.assertIs(expression, expression.Right.Root)

	def test_TopDown(self) -> None:
		"""An empty operator is filled by assigning its operand slots, which links each operand back."""
		expression = AndOperator()
		expression.Left =  SPDXLicense(Apache_2_0_License)
		expression.Right = SPDXLicense(MIT_License)

		self.assertIs(expression, expression.Left.Parent)
		self.assertIs(expression, expression.Right.Parent)
		self.assertEqual("Apache-2.0 AND MIT", str(expression))

	def test_ParentRecordsWithoutFillingASlot(self) -> None:
		"""``parent=`` can't know which slot an operand belongs in, so it records the parent and nothing else."""
		expression = AndOperator()
		operand = SPDXLicense(Apache_2_0_License, parent=expression)

		self.assertIs(expression, operand.Parent)
		self.assertIsNone(expression.Left)
		self.assertIsNone(expression.Right)

	def test_OperandsAreAssignable(self) -> None:
		expression = AndOperator()
		expression.Left = SPDXLicense(Apache_2_0_License)
		expression.Right = SPDXLicense(MIT_License)

		self.assertEqual("Apache-2.0 AND MIT", str(expression))
		self.assertIs(expression, expression.Right.Parent)

	def test_UnaryOperandIsAssignable(self) -> None:
		expression = OrLaterOperator()
		expression.Operand = SPDXLicense(MIT_License)

		self.assertEqual("MIT+", str(expression))
		self.assertIs(expression, expression.Operand.Parent)

	def test_AnOperandCannotBeStolenFromItsOperator(self) -> None:
		"""An expression is an operand of one operator; moving it would leave the first one half-linked."""
		source = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))
		target = OrOperator()

		with self.assertRaises(LicensingError):
			target.Left = source.Right

	def test_AFilledSlotIsNotOverwritten(self) -> None:
		"""An operand slot is filled once; replacing it would silently orphan what it held."""
		expression = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))

		with self.assertRaises(LicensingError):
			expression.Left = SPDXLicense(ISC_License)

		with self.assertRaises(LicensingError):
			OrLaterOperator(SPDXLicense(MIT_License)).Operand = SPDXLicense(ISC_License)

	def test_DetachingIsNotSupported(self) -> None:
		"""``Parent`` records a parent; it can't be unset, because the operator would keep pointing at the node."""
		expression = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))

		with self.assertRaises(ValueError):
			expression.Left.Parent = None

	def test_TheRootOfASubtreeFollowsItsNewParent(self) -> None:
		subtree = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))
		leaf = subtree.Left
		expression = OrOperator(subtree, SPDXLicense(MIT_License))

		self.assertIs(expression, leaf.Root)
		self.assertIs(subtree, leaf.Parent)


class AbstractExpressions(Testcase):
	"""The base-classes exist to be derived from."""

	def test_TheBaseClassesCannotBeInstantiated(self) -> None:
		for cls in (LicenseExpression, Operator, UnaryOperator, BinaryOperator):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(AbstractClassError):
					cls()


class MalformedTrees(Testcase):
	"""What a node rejects when it is built by hand."""

	def test_ALeafCannotBeAParent(self) -> None:
		"""Only an :class:`Operator` is applied to operands, so only an operator can be a parent."""
		with self.assertRaises(TypeError) as context:
			SPDXLicense(MIT_License, parent=SPDXLicense(Apache_2_0_License))

		self.assertIn("is not an Operator", str(context.exception))

	def test_AnIncompleteOperatorCannotBeRendered(self) -> None:
		for expression, message in (
			(OrOperator(), "has no left operand yet"),
			(OrOperator(SPDXLicense(MIT_License)), "has no right operand yet"),
			(OrLaterOperator(), "has no operand yet"),
		):
			with self.subTest(expression=expression.__class__.__name__, message=message):
				with self.assertRaises(LicensingError) as context:
					str(expression)

				self.assertIn(message, str(context.exception))

	def test_OnlyAnExpressionCanBeAnOperand(self) -> None:
		for call in (
			lambda: AndOperator("MIT", SPDXLicense(MIT_License)),
			lambda: AndOperator(SPDXLicense(MIT_License), "MIT"),
			lambda: OrLaterOperator("MIT"),
			lambda: SPDXLicense(MIT_License, parent="MIT"),
		):
			with self.assertRaises(TypeError):
				call()

	def test_OnlyALicenseCanBeALeaf(self) -> None:
		with self.assertRaises(TypeError) as context:
			SPDXLicense("MIT")

		self.assertIn("is not a License", str(context.exception))

	def test_AnIdentifierIsANonEmptyString(self) -> None:
		for call, exception in (
			(lambda: LicenseReference(""), ValueError),
			(lambda: LicenseReference(42), TypeError),
			(lambda: LicenseReference("MyLicense", ""), ValueError),
			(lambda: LicenseReference("MyLicense", 42), TypeError),
			(lambda: LicenseException(""), ValueError),
			(lambda: LicenseException(42), TypeError),
			(lambda: LicenseExpression.Parse(42), TypeError),
		):
			with self.assertRaises(exception):
				call()


class OriginalText(Testcase):
	"""An expression keeps the text it was parsed from, because rendering it back is not the same string."""

	def test_TheRootKeepsWhatWasParsed(self) -> None:
		self.assertEqual("Apache-2.0 OR MIT", LicenseExpression.Parse("Apache-2.0 OR MIT").OriginalText)

	def test_RenderingIsNotTheSameAsWhatWasWritten(self) -> None:
		"""``or`` parses; ``__str__`` renders the canonical ``OR``. This is why the text has to be kept."""
		expression = LicenseExpression.Parse("Apache-2.0 or MIT")

		self.assertEqual("Apache-2.0 OR MIT", str(expression))
		self.assertEqual("Apache-2.0 or MIT", expression.OriginalText)

	def test_EveryNodeAnswersWithTheRoots(self) -> None:
		"""A tree comes from one string, so a leaf reports the whole expression rather than its own fragment."""
		expression = LicenseExpression.Parse("Apache-2.0 OR MIT")

		for node in expression.IterateExpression():
			with self.subTest(node=str(node)):
				self.assertEqual("Apache-2.0 OR MIT", node.OriginalText)

	def test_ATreeBuiltInCodeWasOriginalTextNothing(self) -> None:
		self.assertEqual("", SPDXLicense(Apache_2_0_License).OriginalText)


class BaseLicenses(Testcase):
	"""The intermediate base-class collecting the nodes that name a license."""

	def test_BothLeafKindsAreOne(self) -> None:
		self.assertTrue(issubclass(SPDXLicense, BaseLicense))
		self.assertTrue(issubclass(LicenseReference, BaseLicense))

	def test_AnExceptionIsNotOne(self) -> None:
		"""The right operand of ``WITH`` is granted *from* a license; it isn't one."""
		self.assertFalse(issubclass(LicenseException, BaseLicense))

	def test_AnOperatorIsNotOne(self) -> None:
		for operatorType in (AndOperator, OrOperator, WithOperator, OrLaterOperator):
			with self.subTest(operator=operatorType.__name__):
				self.assertFalse(issubclass(operatorType, BaseLicense))

	def test_ItIsAbstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			BaseLicense()

	def test_BothAnswerIdentifier(self) -> None:
		"""Which is the point: a report collects them without branching on which kind it got."""
		expression = LicenseExpression.Parse("MIT AND LicenseRef-Proprietary")

		self.assertEqual(
			["MIT", "LicenseRef-Proprietary"],
			[term.Identifier for term in expression.IterateExpression() if isinstance(term, BaseLicense)]
		)

	def test_AReferenceIdentifierCarriesItsDocument(self) -> None:
		"""``Identifier`` is the whole reference; ``LicenseIdentifier`` is the part after ``LicenseRef-``."""
		reference = LicenseExpression.Parse("DocumentRef-spdx:LicenseRef-Custom")

		self.assertEqual("DocumentRef-spdx:LicenseRef-Custom", reference.Identifier)
		self.assertEqual("Custom", reference.LicenseIdentifier)
		self.assertEqual("spdx", reference.DocumentIdentifier)

	def test_AnExceptionIsNotCollected(self) -> None:
		expression = LicenseExpression.Parse("Apache-2.0 WITH LLVM-exception")

		self.assertEqual(
			["Apache-2.0"],
			[term.Identifier for term in expression.IterateExpression() if isinstance(term, BaseLicense)]
		)


class LicenseHomepages(Testcase):
	"""Where the licensor itself publishes the license, and its text by format."""

	def test_TheLicensorsOwnPage(self) -> None:
		self.assertEqual("https://www.apache.org/licenses/LICENSE-2.0", Apache_2_0_License.URL)
		self.assertEqual("https://creativecommons.org/publicdomain/zero/1.0/", CC0_1_0.URL)

	def test_ALicenseWithNoHomeOfItsOwn(self) -> None:
		"""``MIT`` and the BSD licenses are published by OSI and nobody else, and that URL is :attr:`OSIURL`."""
		for spdxLicense in (MIT_License, BSD_3_Clause_License):
			with self.subTest(license=spdxLicense.SPDXIdentifier):
				self.assertIsNone(spdxLicense.URL)
				self.assertIsNotNone(spdxLicense.OSIURL)

	def test_TheTextByFormat(self) -> None:
		self.assertEqual(
			"https://www.apache.org/licenses/LICENSE-2.0.txt",
			Apache_2_0_License.TextURLs["txt"]
		)
		self.assertEqual(
			"https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt",
			CC0_1_0.TextURLs["txt"]
		)

	def test_ALicenseThatPublishesNoText(self) -> None:
		self.assertEqual({}, MIT_License.TextURLs)

	def test_TheReturnedMappingIsACopy(self) -> None:
		"""Editing it must not reach :data:`LICENSE_TEXT_URLS`."""
		urls = Apache_2_0_License.TextURLs
		urls["txt"] = "https://example.org/not-the-license"

		self.assertEqual("https://www.apache.org/licenses/LICENSE-2.0.txt", Apache_2_0_License.TextURLs["txt"])

	def test_BothTablesNameOnlyPredefinedLicenses(self) -> None:
		identifiers = {spdxLicense.SPDXIdentifier for spdxLicense in LICENSES}

		self.assertEqual(set(), set(LICENSE_URLS) - identifiers)
		self.assertEqual(set(), set(LICENSE_TEXT_URLS) - identifiers)

	def test_EveryFormatIsAnExtension(self) -> None:
		"""The key is a file extension without its dot, so a caller can build a filename from it."""
		for spdxIdentifier, urls in LICENSE_TEXT_URLS.items():
			for extension, url in urls.items():
				with self.subTest(license=spdxIdentifier, format=extension):
					self.assertIn(extension, ("txt", "md", "rst", "tex"))
					self.assertTrue(url.startswith("https://"))

	def test_ATextURLEndsInItsFormat(self) -> None:
		"""Except where the licensor doesn't name the file after it - which is worth seeing rather than assuming."""
		exceptions = {"https://unlicense.org/UNLICENSE", "https://www.mozilla.org/media/MPL/2.0/index.txt"}

		for spdxIdentifier, urls in LICENSE_TEXT_URLS.items():
			for extension, url in urls.items():
				with self.subTest(license=spdxIdentifier, format=extension):
					self.assertTrue(url.endswith(f".{extension}") or url in exceptions)

	def test_ALicensePublishedInSeveralFormats(self) -> None:
		"""The GNU licenses are the reason this is a mapping rather than one more URL property."""
		self.assertEqual(
			{"txt", "md", "rst", "tex"},
			set(GPL_3_0_only.TextURLs)
		)
		self.assertEqual("https://www.gnu.org/licenses/gpl-3.0.rst", GPL_3_0_only.TextURLs["rst"])

	def test_APairSharesItsPublisherURLs(self) -> None:
		"""``-only`` and ``-or-later`` are one document at GNU, as they are at OSI."""
		self.assertEqual(GPL_3_0_only.URL, GPL_3_0_or_later.URL)
		self.assertEqual(GPL_3_0_only.TextURLs, GPL_3_0_or_later.TextURLs)

	def test_TheFourURLsAreDifferentQuestions(self) -> None:
		"""Catalogue entry, OSI's entry, the licensor's page, the text - four properties, four answers."""
		self.assertEqual("https://spdx.org/licenses/Apache-2.0.html", Apache_2_0_License.SPDXURL)
		self.assertEqual("https://opensource.org/license/apache-2.0", Apache_2_0_License.OSIURL)
		self.assertEqual("https://www.apache.org/licenses/LICENSE-2.0", Apache_2_0_License.URL)
		self.assertEqual("https://www.apache.org/licenses/LICENSE-2.0.txt", Apache_2_0_License.TextURLs["txt"])


class LicenseURLs(Testcase):
	"""Where a license's text is published: derived at SPDX, looked up at OSI."""

	def test_TheSPDXURLIsDerived(self) -> None:
		self.assertEqual("https://spdx.org/licenses/MIT.html", MIT_License.SPDXURL)
		self.assertEqual("https://spdx.org/licenses/GPL-2.0-or-later.html", GPL_2_0_or_later.SPDXURL)

	def test_EveryPredefinedLicenseHasOne(self) -> None:
		for spdxLicense in LICENSES:
			with self.subTest(license=spdxLicense.SPDXIdentifier):
				self.assertEqual(f"https://spdx.org/licenses/{spdxLicense.SPDXIdentifier}.html", spdxLicense.SPDXURL)

	def test_TheOSIURLIsLookedUp(self) -> None:
		"""OSI's addresses don't follow the SPDX identifier, which is why they are a table."""
		self.assertEqual("https://opensource.org/license/mit", MIT_License.OSIURL)
		self.assertEqual("https://opensource.org/license/Python-2.0", PSF_2_0_License.OSIURL)

	def test_TwoIdentifiersCanShareOneOSIPage(self) -> None:
		"""*only* versus *or later* is SPDX's distinction, not OSI's."""
		self.assertEqual(GPL_2_0_only.OSIURL, GPL_2_0_or_later.OSIURL)
		self.assertEqual("https://opensource.org/license/gpl-2.0", GPL_2_0_only.OSIURL)

	def test_ALicenseOSIDidNotApproveHasNone(self) -> None:
		self.assertFalse(CC0_1_0.OSIApproved)
		self.assertIsNone(CC0_1_0.OSIURL)

	def test_AnOSIURLExistsExactlyWhenOSIApproved(self) -> None:
		for spdxLicense in LICENSES:
			with self.subTest(license=spdxLicense.SPDXIdentifier):
				self.assertEqual(spdxLicense.OSIApproved, spdxLicense.OSIURL is not None)

	def test_TheTableNamesOnlyPredefinedLicenses(self) -> None:
		"""An entry for an identifier no license carries would never be reached."""
		identifiers = {spdxLicense.SPDXIdentifier for spdxLicense in LICENSES}

		self.assertEqual(set(), set(OSI_LICENSE_URLS) - identifiers)

	def test_AnUnlistedLicenseHasNoOSIURL(self) -> None:
		self.assertIsNone(License("Not-A-Real-Identifier", "Not a real license").OSIURL)


class AbsentLicenses(Testcase):
	"""SPDX's ``NONE`` and ``NOASSERTION``, which are values a field holds instead of an expression."""

	def test_BothParse(self) -> None:
		for text, absence in (("NONE", LicenseAbsence.NoLicense), ("NOASSERTION", LicenseAbsence.NoAssertion)):
			with self.subTest(expression=text):
				expression = LicenseExpression.Parse(text)

				self.assertIsInstance(expression, UnknownLicense)
				self.assertIs(absence, expression.Absence)
				self.assertEqual(text, str(expression))
				self.assertEqual(text, expression.Identifier)

	def test_TheyAreTwoDifferentStatements(self) -> None:
		"""``NONE`` says no license applies; ``NOASSERTION`` says nobody claimed either way."""
		self.assertNotEqual(
			LicenseExpression.Parse("NONE").Absence,
			LicenseExpression.Parse("NOASSERTION").Absence
		)

	def test_NeitherCanBeAnOperand(self) -> None:
		"""SPDX's grammar is ``simple-expression | compound-expression``; neither value is a term inside one."""
		for text in ("MIT AND NOASSERTION", "NONE OR MIT", "NOASSERTION WITH LLVM-exception", "MIT AND (NONE)"):
			with self.subTest(expression=text):
				with self.assertRaises(LicenseExpressionError):
					LicenseExpression.Parse(text)

	def test_ItsParentIsReadOnly(self) -> None:
		"""Every other node's ``Parent`` is assignable; this one's can't be, so it is a read-only property."""
		with self.assertRaises(AttributeError):
			UnknownLicense().Parent = AndOperator(SPDXLicense(MIT_License), SPDXLicense(ISC_License))

	def test_ItRefusesToBecomeAnOperand(self) -> None:
		"""Built in code rather than parsed, the same rule has to hold - an operator assigns its operands' parent."""
		with self.assertRaises(AttributeError):
			AndOperator(SPDXLicense(MIT_License), UnknownLicense())

	def test_TheDefaultIsNoAssertion(self) -> None:
		"""Saying nothing about a license is a stronger claim than saying there is none, so it isn't the default."""
		self.assertIs(LicenseAbsence.NoAssertion, UnknownLicense().Absence)

	def test_ItIsALicenseNode(self) -> None:
		self.assertIsInstance(UnknownLicense(), BaseLicense)

	def test_TheAbsenceMustBeOne(self) -> None:
		with self.assertRaises(TypeError):
			UnknownLicense("NOASSERTION")


class ProprietaryLicenses(Testcase):
	"""A license that isn't published, which SPDX has no way to name."""

	def test_ItRendersAsALicenseRef(self) -> None:
		self.assertEqual("LicenseRef-Proprietary", str(ProprietaryLicense()))
		self.assertEqual("LicenseRef-Proprietary", ProprietaryLicense().Identifier)

	def test_ItIsALicenseReference(self) -> None:
		"""Which is what it writes, so it is what it is."""
		proprietary = ProprietaryLicense()

		self.assertIsInstance(proprietary, LicenseReference)
		self.assertIsInstance(proprietary, BaseLicense)
		self.assertEqual("Proprietary", proprietary.LicenseIdentifier)
		self.assertIsNone(proprietary.DocumentIdentifier)

	def test_ParsingItBackGivesAPlainReference(self) -> None:
		"""Deliberate: SPDX defines no convention making that identifier mean *proprietary*."""
		parsed = LicenseExpression.Parse("LicenseRef-Proprietary")

		self.assertIsInstance(parsed, LicenseReference)
		self.assertNotIsInstance(parsed, ProprietaryLicense)

	def test_ItCanBeAnOperand(self) -> None:
		"""Unlike an absent license - a proprietary license exists, it just isn't published."""
		expression = AndOperator(SPDXLicense(MIT_License), ProprietaryLicense())

		self.assertEqual("MIT AND LicenseRef-Proprietary", str(expression))
