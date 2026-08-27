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
The Licensing module implements mapping tables for various license names and identifiers.

.. seealso::

   List of SPDX identifiers:

   * https://spdx.org/licenses/
   * https://github.com/spdx/license-list-XML

   List of `Python classifiers <https://pypi.org/classifiers/>`__

.. hint::

   See :ref:`high-level help <LICENSING>` for explanations and usage examples.
"""
from dataclasses           import dataclass
from re                    import compile as re_compile
from typing                import Any, ClassVar, Optional as Nullable
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType


__all__ = [
	"PYTHON_LICENSE_NAMES",

	"Apache_2_0_License",
	"BSD_2_Clause_License",
	"BSD_3_Clause_License",
	"MIT_License",
	"ISC_License",
	"MPL_2_0_License",
	"BSL_1_0_License",
	"Zlib_License",
	"PSF_2_0_License",
	"Unlicense",
	"CC0_1_0",
	"EPL_1_0_License",
	"EPL_2_0_License",
	"LGPL_2_1_only",
	"LGPL_2_1_or_later",
	"LGPL_3_0_only",
	"LGPL_3_0_or_later",
	"GPL_2_0_only",
	"GPL_2_0_or_later",
	"GPL_3_0_only",
	"GPL_3_0_or_later",
	"AGPL_3_0_only",
	"AGPL_3_0_or_later",

	"SPDX_INDEX"
]


@export
@dataclass
class PythonLicenseName:
	"""A *data class* to represent the license's short name and the package classifier for a license."""

	ShortName: str    #: License's short name
	Classifier: str   #: Package classifier for a license.

	def __str__(self) -> str:
		"""
		The string representation of this name tuple returns the short name of the license.

		:returns: Short name of the license.
		"""
		return self.ShortName


#: Mapping of SPDX identifiers to Python license names
PYTHON_LICENSE_NAMES: dict[str, PythonLicenseName] = {
	"Apache-2.0":        PythonLicenseName("Apache 2.0",        "Apache Software License"),
	"BSD-2-Clause":      PythonLicenseName("BSD-2-Clause",      "BSD License"),
	"BSD-3-Clause":      PythonLicenseName("BSD",               "BSD License"),
	"MIT":               PythonLicenseName("MIT",               "MIT License"),
	"ISC":               PythonLicenseName("ISC",               "ISC License (ISCL)"),
	"MPL-2.0":           PythonLicenseName("MPL-2.0",           "Mozilla Public License 2.0 (MPL 2.0)"),
	"BSL-1.0":           PythonLicenseName("BSL-1.0",           "Boost Software License 1.0 (BSL-1.0)"),
	"Zlib":              PythonLicenseName("Zlib",              "zlib/libpng License"),
	"PSF-2.0":           PythonLicenseName("PSF-2.0",           "Python Software Foundation License"),
	"Unlicense":         PythonLicenseName("Unlicense",         "The Unlicense (Unlicense)"),
	"CC0-1.0":           PythonLicenseName("CC0-1.0",           "CC0 1.0 Universal (CC0 1.0) Public Domain Dedication"),
	"EPL-1.0":           PythonLicenseName("EPL-1.0",           "Eclipse Public License 1.0 (EPL-1.0)"),
	"EPL-2.0":           PythonLicenseName("EPL-2.0",           "Eclipse Public License 2.0 (EPL-2.0)"),
	"LGPL-2.1-only":     PythonLicenseName("LGPL-2.1-only",     "GNU Lesser General Public License v2 (LGPLv2)"),
	"LGPL-2.1-or-later": PythonLicenseName("LGPL-2.1-or-later", "GNU Lesser General Public License v2 or later (LGPLv2+)"),
	"LGPL-3.0-only":     PythonLicenseName("LGPL-3.0-only",     "GNU Lesser General Public License v3 (LGPLv3)"),
	"LGPL-3.0-or-later": PythonLicenseName("LGPL-3.0-or-later", "GNU Lesser General Public License v3 or later (LGPLv3+)"),
	"GPL-2.0-only":      PythonLicenseName("GPL-2.0-only",      "GNU General Public License v2 (GPLv2)"),
	"GPL-2.0-or-later":  PythonLicenseName("GPL-2.0-or-later",  "GNU General Public License v2 or later (GPLv2+)"),
	"GPL-3.0-only":      PythonLicenseName("GPL-3.0-only",      "GNU General Public License v3 (GPLv3)"),
	"GPL-3.0-or-later":  PythonLicenseName("GPL-3.0-or-later",  "GNU General Public License v3 or later (GPLv3+)"),
	"AGPL-3.0-only":     PythonLicenseName("AGPL-3.0-only",     "GNU Affero General Public License v3"),
	"AGPL-3.0-or-later": PythonLicenseName("AGPL-3.0-or-later", "GNU Affero General Public License v3 or later (AGPLv3+)"),
}


@export
class License(metaclass=ExtendedType, slots=True):
	"""Representation of a license."""

	_spdxIdentifier: str  #: Unique SPDX identifier.
	_name: str            #: Name of the license.
	_osiApproved: bool    #: OSI approval status
	_fsfApproved: bool    #: FSF approval status

	def __init__(self, spdxIdentifier: str, name: str, osiApproved: bool = False, fsfApproved: bool = False) -> None:
		"""
		Initialize a license with its SPDX identifier, its name and its approval flags.

		:param spdxIdentifier: SPDX identifier of the license.
		:param name:           Name of the license.
		:param osiApproved:    Optional, ``True``, if the license is approved by the Open Source Initiative.
		:param fsfApproved:    Optional, ``True``, if the license is approved by the Free Software Foundation.
		"""
		self._spdxIdentifier = spdxIdentifier
		self._name = name
		self._osiApproved = osiApproved
		self._fsfApproved = fsfApproved

	@readonly
	def Name(self) -> str:
		"""
		Returns the license' name.

		:returns: License name.
		"""
		return self._name

	@readonly
	def SPDXIdentifier(self) -> str:
		"""
		Returns the license' unique `SPDX identifier <https://spdx.org/licenses/>`__.

		:returns: The the unique SPDX identifier.
		"""
		return self._spdxIdentifier

	@readonly
	def OSIApproved(self) -> bool:
		"""
		Returns true, if the license is approved by OSI (`Open Source Initiative <https://opensource.org/>`__).

		:returns: ``True``, if the license is approved by the Open Source Initiative.
		"""
		return self._osiApproved

	@readonly
	def FSFApproved(self) -> bool:
		"""
		Returns true, if the license is approved by FSF (`Free Software Foundation <https://www.fsf.org/>`__).

		:returns: ``True``, if the license is approved by the Free Software Foundation.
		"""
		return self._fsfApproved

	@readonly
	def PythonLicenseName(self) -> str:
		"""
		Returns the Python license name for this license if it's defined.

		:returns:           The Python license name.
		:raises ValueError: If there is no license name defined for the license. |br| (See and check :data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES`)
		"""
		try:
			item: PythonLicenseName = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError as ex:
			raise ValueError("License has no Python specify information.") from ex

		return item.ShortName

	@readonly
	def PythonClassifier(self) -> str:
		"""
		Returns the Python package classifier for this license if it's defined.

		:returns:           The Python package classifier.
		:raises ValueError: If there is no classifier defined for the license. |br| (See and check :data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES`)

		.. seealso::

		   List of `Python classifiers <https://pypi.org/classifiers/>`__
		"""
		try:
			item: PythonLicenseName = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError as ex:
			raise ValueError("License has no Python specify information.") from ex

		osi = "OSI Approved :: " if self._osiApproved else ""
		return f"License :: {osi}{item.Classifier}"

	def __eq__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are identical (comparison based on SPDX identifiers).

		:param other:      The second operand to compare with. A :class:`License` or its SPDX identifier as a string.
		:returns:          ``True``, if both licenses are identical.
		:raises TypeError: If second operand is not of type :class:`License` or string.
		"""
		if isinstance(other, License):
			return self._spdxIdentifier == other._spdxIdentifier
		elif isinstance(other, str):
			return self._spdxIdentifier == other
		else:
			ex = TypeError("Second operand is not supported by equal operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: License, str")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are not identical (comparison based on SPDX identifiers).

		:param other:      The second operand to compare with. A :class:`License` or its SPDX identifier as a string.
		:returns:          ``True``, if both licenses are not identical.
		:raises TypeError: If second operand is not of type :class:`License` or string.
		"""
		if isinstance(other, License):
			return self._spdxIdentifier != other._spdxIdentifier
		elif isinstance(other, str):
			return self._spdxIdentifier != other
		else:
			ex = TypeError("Second operand is not supported by unequal operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: License, str")
			raise ex

	def __hash__(self) -> int:
		"""
		Compute a hash from the license's SPDX identifier, so a license can be a set element or a dictionary key.

		The identifier is what :meth:`__eq__` compares, so two licenses that compare equal hash equally - which is
		what a :class:`set` and a :class:`dict` rely on.

		A license compares equal to its identifier as a string, so the two hash equally as well - which is what lets
		``Apache_2_0_License in {"Apache-2.0"}`` answer instead of missing.

		:returns: Hash of the SPDX identifier.
		"""
		return hash(self._spdxIdentifier)

	def __le__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are compatible.

		:param other:                Second operand, the license to compare with.
		:returns:                    ``True``, if both licenses are compatible.
		:raises NotImplementedError: License compatibility is not implemented yet.
		"""
		raise NotImplementedError("License compatibility check is not yet implemented.")

	def __ge__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are compatible.

		:param other:                Second operand, the license to compare with.
		:returns:                    ``True``, if both licenses are compatible.
		:raises NotImplementedError: License compatibility is not implemented yet.
		"""
		raise NotImplementedError("License compatibility check is not yet implemented.")

	def __repr__(self) -> str:
		"""
		Returns the internal unique representation (a.k.a SPDX identifier).

		:returns: SPDX identifier of the license.
		"""
		return self._spdxIdentifier

	def __str__(self) -> str:
		"""
		Returns the license' name.

		:returns: Name of the license.
		"""
		return self._name


Apache_2_0_License =     License("Apache-2.0",        "Apache License 2.0",                              True, True)
BSD_2_Clause_License =   License("BSD-2-Clause",      "BSD 2-Clause Simplified License",                 True, True)
BSD_3_Clause_License =   License("BSD-3-Clause",      "BSD 3-Clause Revised License",                    True, True)
MIT_License =            License("MIT",               "MIT License",                                     True, True)
ISC_License =            License("ISC",               "ISC License",                                     True, True)
MPL_2_0_License =        License("MPL-2.0",           "Mozilla Public License 2.0",                      True, True)
BSL_1_0_License =        License("BSL-1.0",           "Boost Software License 1.0",                      True, True)
Zlib_License =           License("Zlib",              "zlib License",                                    True, True)
PSF_2_0_License =        License("PSF-2.0",           "Python Software Foundation License 2.0",          True, True)
Unlicense =              License("Unlicense",         "The Unlicense",                                   True, True)
CC0_1_0 =                License("CC0-1.0",           "Creative Commons Zero v1.0 Universal",            False, True)
EPL_1_0_License =        License("EPL-1.0",           "Eclipse Public License 1.0",                      True, True)
EPL_2_0_License =        License("EPL-2.0",           "Eclipse Public License 2.0",                      True, True)
LGPL_2_1_only =          License("LGPL-2.1-only",     "GNU Lesser General Public License v2.1 only",     True, True)
LGPL_2_1_or_later =      License("LGPL-2.1-or-later", "GNU Lesser General Public License v2.1 or later", True, True)
LGPL_3_0_only =          License("LGPL-3.0-only",     "GNU Lesser General Public License v3.0 only",     True, True)
LGPL_3_0_or_later =      License("LGPL-3.0-or-later", "GNU Lesser General Public License v3.0 or later", True, True)
GPL_2_0_only =           License("GPL-2.0-only",      "GNU General Public License v2.0 only",            True, True)
GPL_2_0_or_later =       License("GPL-2.0-or-later",  "GNU General Public License v2.0 or later",        True, True)
GPL_3_0_only =           License("GPL-3.0-only",      "GNU General Public License v3.0 only",            True, True)
GPL_3_0_or_later =       License("GPL-3.0-or-later",  "GNU General Public License v3.0 or later",        True, True)
AGPL_3_0_only =          License("AGPL-3.0-only",     "GNU Affero General Public License v3.0 only",     True, True)
AGPL_3_0_or_later =      License("AGPL-3.0-or-later", "GNU Affero General Public License v3.0 or later", True, True)


#: All predefined licenses, in the order they are defined above.
LICENSES: tuple[License, ...] = (
	Apache_2_0_License, BSD_2_Clause_License, BSD_3_Clause_License, MIT_License, ISC_License, MPL_2_0_License,
	BSL_1_0_License, Zlib_License, PSF_2_0_License, Unlicense, CC0_1_0, EPL_1_0_License, EPL_2_0_License,
	LGPL_2_1_only, LGPL_2_1_or_later, LGPL_3_0_only, LGPL_3_0_or_later,
	GPL_2_0_only, GPL_2_0_or_later, GPL_3_0_only, GPL_3_0_or_later,
	AGPL_3_0_only, AGPL_3_0_or_later,
)

#: Mapping of predefined licenses, indexed by their SPDX identifier.
SPDX_INDEX: dict[str, License] = {spdxLicense.SPDXIdentifier: spdxLicense for spdxLicense in LICENSES}


#: The :class:`License` class under a name no expression node shadows with a property of its own.
_LicenseType = License


@export
class LicenseExpression(metaclass=ExtendedType, slots=True):
	"""
	Base-class of every node in an `SPDX license expression`_.

	.. _SPDX license expression: https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/

	An expression is a tree: :class:`SPDXLicense` and :class:`LicenseReference` are its leaves, and
	:class:`AndOperator`, :class:`OrOperator`, :class:`WithOperator` and :class:`OrLaterOperator` combine them. The
	grammar SPDX defines is::

	   simple-expression   = license-id / license-id "+" / license-ref
	   compound-expression = ( simple-expression
	                         / simple-expression "WITH" license-exception-id
	                         / compound-expression "AND" compound-expression
	                         / compound-expression "OR" compound-expression
	                         / "(" compound-expression ")" )

	so there are three binary operators, one unary one, and parentheses. There is **no negation** - an expression
	says which licenses apply, never which don't.

	Every node knows its :attr:`Parent`, which is what a :class:`License` can't carry: the predefined licenses are
	shared objects, so :data:`MIT_License` appears in many expressions at once and belongs to none of them.
	:class:`SPDXLicense` is the wrapper that gives a license a place in one tree.
	"""

	_parent: Nullable["LicenseExpression"]  #: The expression this one is an operand of, or ``None`` at the root.

	#: Precedence of this node's operator; a lower value binds tighter, as SPDX defines it.
	_PRECEDENCE: ClassVar[int] = 0

	def __init__(self) -> None:
		"""Initialize an expression node without a parent."""
		self._parent = None

	@readonly
	def Parent(self) -> Nullable["LicenseExpression"]:
		"""
		Read-only property returning the expression this one is an operand of (:attr:`_parent`).

		:returns: The parent expression, or ``None`` if this node is the root.
		"""
		return self._parent

	@readonly
	def Root(self) -> "LicenseExpression":
		"""
		Read-only property returning the outermost expression this node belongs to.

		:returns: The root of the expression tree.
		"""
		node = self
		while node._parent is not None:
			node = node._parent

		return node

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning every license named in this expression, in the order they are written.

		A license named twice is returned twice, because ``MIT AND MIT`` is not the same statement as ``MIT`` -
		deduplicating is a decision for whoever consumes the list.

		:returns: The licenses this expression names.
		"""
		raise NotImplementedError()

	@classmethod
	def Parse(cls, expression: str) -> "LicenseExpression":
		"""
		Parse an SPDX license expression into a tree of expression nodes.

		Operator precedence is the one SPDX defines - ``+`` binds tighter than ``WITH``, which binds tighter than
		``AND``, which binds tighter than ``OR`` - and parentheses override it. ``AND`` and ``OR`` associate to the
		left.

		:param expression:  The SPDX license expression to parse.
		:returns:           The root of the parsed expression tree.
		:raises ValueError: If the expression is empty, malformed, or names a license that isn't known.
		"""
		return _LicenseExpressionParser(expression).Parse()

	def __str__(self) -> str:
		"""
		Return this expression in SPDX syntax.

		Parentheses are written only where the default precedence would otherwise read the expression differently, so
		a parsed expression renders back to its shortest correct form rather than a fully bracketed one.

		:returns: The expression in SPDX syntax.
		"""
		raise NotImplementedError()


@export
class SPDXLicense(LicenseExpression):
	"""
	A single license in an expression, by its SPDX identifier.

	This is the *literal* of an expression. It exists rather than putting a :class:`License` into the tree directly,
	because the predefined licenses are shared objects - :data:`MIT_License` is one instance used everywhere - and a
	shared object can't belong to one parent.
	"""

	_license: _LicenseType  #: The license this leaf stands for.

	def __init__(self, spdxLicense: _LicenseType) -> None:
		"""
		Initialize a license leaf.

		:param spdxLicense: The license this leaf stands for.
		:raises TypeError:  If parameter 'spdxLicense' is not of type :class:`License`.
		"""
		super().__init__()

		if not isinstance(spdxLicense, _LicenseType):
			ex = TypeError("Parameter 'spdxLicense' is not of type 'License'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(spdxLicense)}'.")
			raise ex

		self._license = spdxLicense

	@readonly
	def License(self) -> _LicenseType:
		"""
		Read-only property returning the license this leaf stands for (:attr:`_license`).

		:returns: The license.
		"""
		return self._license

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning this leaf's license.

		:returns: A tuple of one license.
		"""
		return (self._license,)

	def __str__(self) -> str:
		"""
		Return the license's SPDX identifier.

		:returns: The SPDX identifier.
		"""
		return self._license.SPDXIdentifier


@export
class LicenseReference(LicenseExpression):
	"""
	A license that isn't on the SPDX License List, written as ``LicenseRef-<id>``.

	It may name the document it is defined in, as ``DocumentRef-<id>:LicenseRef-<id>``. There is no
	:class:`License` behind it, because SPDX doesn't know what it is - only the document that declares it does.
	"""

	_licenseIdentifier:  str            #: Identifier following ``LicenseRef-``.
	_documentIdentifier: Nullable[str]  #: Identifier following ``DocumentRef-``, where the reference names one.

	def __init__(self, licenseIdentifier: str, documentIdentifier: Nullable[str] = None) -> None:
		"""
		Initialize a license reference.

		:param licenseIdentifier:  Identifier following ``LicenseRef-``.
		:param documentIdentifier: Optional, identifier following ``DocumentRef-``.
		"""
		super().__init__()

		self._licenseIdentifier = licenseIdentifier
		self._documentIdentifier = documentIdentifier

	@readonly
	def LicenseIdentifier(self) -> str:
		"""
		Read-only property returning the identifier following ``LicenseRef-`` (:attr:`_licenseIdentifier`).

		:returns: The license reference's identifier.
		"""
		return self._licenseIdentifier

	@readonly
	def DocumentIdentifier(self) -> Nullable[str]:
		"""
		Read-only property returning the identifier following ``DocumentRef-`` (:attr:`_documentIdentifier`).

		:returns: The document reference's identifier, or ``None`` if the reference names no document.
		"""
		return self._documentIdentifier

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning no licenses, because a reference names none SPDX knows.

		:returns: An empty tuple.
		"""
		return ()

	def __str__(self) -> str:
		"""
		Return the reference in SPDX syntax.

		:returns: The license reference.
		"""
		document = "" if self._documentIdentifier is None else f"DocumentRef-{self._documentIdentifier}:"

		return f"{document}LicenseRef-{self._licenseIdentifier}"


@export
class LicenseException(LicenseExpression):
	"""
	The right-hand operand of a :class:`WithOperator`, naming an exception from the SPDX exception list.

	It is a leaf like a license, but it is not one - an exception modifies a license and can't stand on its own, so
	:attr:`Licenses` is empty.
	"""

	_identifier: str  #: The exception's SPDX identifier.

	def __init__(self, identifier: str) -> None:
		"""
		Initialize a license exception.

		:param identifier: The exception's SPDX identifier.
		"""
		super().__init__()

		self._identifier = identifier

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property returning the exception's SPDX identifier (:attr:`_identifier`).

		:returns: The exception's identifier.
		"""
		return self._identifier

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning no licenses, because an exception is not one.

		:returns: An empty tuple.
		"""
		return ()

	def __str__(self) -> str:
		"""
		Return the exception's SPDX identifier.

		:returns: The identifier.
		"""
		return self._identifier


@export
class UnaryOperator(LicenseExpression):
	"""
	Base-class of the expression operators taking one operand.

	SPDX defines exactly one: the ``+`` suffix of :class:`OrLaterOperator`. The class exists anyway, so that the tree
	says *unary* where it means unary rather than leaving :class:`OrLaterOperator` a special case of nothing.
	"""

	_operand: LicenseExpression  #: The expression this operator is applied to.

	def __init__(self, operand: LicenseExpression) -> None:
		"""
		Initialize a unary operator and adopt its operand.

		:param operand:    The expression this operator is applied to.
		:raises TypeError: If parameter 'operand' is not of type :class:`LicenseExpression`.
		"""
		super().__init__()

		if not isinstance(operand, LicenseExpression):
			ex = TypeError("Parameter 'operand' is not of type 'LicenseExpression'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(operand)}'.")
			raise ex

		self._operand = operand
		operand._parent = self

	@readonly
	def Operand(self) -> LicenseExpression:
		"""
		Read-only property returning the expression this operator is applied to (:attr:`_operand`).

		:returns: The operand.
		"""
		return self._operand

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning every license named in the operand.

		:returns: The licenses the operand names.
		"""
		return self._operand.Licenses


@export
class OrLaterOperator(UnaryOperator):
	"""
	The ``+`` suffix, as in ``GPL-2.0+``: the named license *or any later version of it*.

	SPDX deprecated this in favour of identifiers like ``GPL-2.0-or-later``, but the grammar still accepts it and
	published metadata still contains it, so an expression that uses it has to parse.
	"""

	_PRECEDENCE: ClassVar[int] = 1  #: Binds tightest of all operators.

	def __str__(self) -> str:
		"""
		Return the operand followed by ``+``.

		:returns: The expression in SPDX syntax.
		"""
		return f"{self._operand}+"


@export
class BinaryOperator(LicenseExpression):
	"""
	Base-class of the expression operators taking two operands, ``left`` and ``right``.

	SPDX defines three: :class:`AndOperator`, :class:`OrOperator` and :class:`WithOperator`.
	"""

	_left:  LicenseExpression  #: The operator's left operand.
	_right: LicenseExpression  #: The operator's right operand.

	#: The operator's keyword, as it is written between the operands.
	_KEYWORD: ClassVar[str] = ""

	def __init__(self, left: LicenseExpression, right: LicenseExpression) -> None:
		"""
		Initialize a binary operator and adopt both operands.

		:param left:       The operator's left operand.
		:param right:      The operator's right operand.
		:raises TypeError: If parameter 'left' is not of type :class:`LicenseExpression`.
		:raises TypeError: If parameter 'right' is not of type :class:`LicenseExpression`.
		"""
		super().__init__()

		if not isinstance(left, LicenseExpression):
			ex = TypeError("Parameter 'left' is not of type 'LicenseExpression'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(left)}'.")
			raise ex

		if not isinstance(right, LicenseExpression):
			ex = TypeError("Parameter 'right' is not of type 'LicenseExpression'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(right)}'.")
			raise ex

		self._left = left
		self._right = right
		left._parent = self
		right._parent = self

	@readonly
	def Left(self) -> LicenseExpression:
		"""
		Read-only property returning the operator's left operand (:attr:`_left`).

		:returns: The left operand.
		"""
		return self._left

	@readonly
	def Right(self) -> LicenseExpression:
		"""
		Read-only property returning the operator's right operand (:attr:`_right`).

		:returns: The right operand.
		"""
		return self._right

	@readonly
	def Licenses(self) -> tuple[_LicenseType, ...]:
		"""
		Read-only property returning every license named in either operand, left to right.

		:returns: The licenses both operands name.
		"""
		return self._left.Licenses + self._right.Licenses

	def _operandToString(self, operand: LicenseExpression) -> str:
		"""
		Render an operand, parenthesizing it only when the default precedence would read it differently.

		:param operand: The operand to render.
		:returns:       The operand in SPDX syntax, in parentheses where they are needed.
		"""
		return f"({operand})" if operand._PRECEDENCE > self._PRECEDENCE else f"{operand}"

	def __str__(self) -> str:
		"""
		Return both operands with the operator's keyword between them.

		:returns: The expression in SPDX syntax.
		"""
		return f"{self._operandToString(self._left)} {self._KEYWORD} {self._operandToString(self._right)}"


@export
class WithOperator(BinaryOperator):
	"""
	``WITH``, as in ``Apache-2.0 WITH LLVM-exception``: a license together with an exception to it.

	It is the only operator whose operands differ in kind - the right one is a :class:`LicenseException`, never a
	license - and it binds tighter than ``AND`` and ``OR``.
	"""

	_PRECEDENCE: ClassVar[int] = 2     #: Binds tighter than ``AND`` and ``OR``.
	_KEYWORD:    ClassVar[str] = "WITH"  #: The operator's keyword.


@export
class AndOperator(BinaryOperator):
	"""
	``AND``, as in ``Apache-2.0 AND MIT``: **both** licenses apply, and both have to be complied with.
	"""

	_PRECEDENCE: ClassVar[int] = 3    #: Binds tighter than ``OR``.
	_KEYWORD:    ClassVar[str] = "AND"  #: The operator's keyword.


@export
class OrOperator(BinaryOperator):
	"""
	``OR``, as in ``Apache-2.0 OR BSD-2-Clause``: **either** license applies, and the recipient chooses which.

	Which one they chose is not something the expression records.
	"""

	_PRECEDENCE: ClassVar[int] = 4   #: Binds loosest of all operators.
	_KEYWORD:    ClassVar[str] = "OR"  #: The operator's keyword.


class _LicenseExpressionParser(metaclass=ExtendedType, slots=True):
	"""
	Recursive-descent parser for SPDX license expressions.

	One level of the descent per precedence level, lowest-binding first, which is what makes ``A OR B AND C`` parse as
	``A OR (B AND C)`` without the grammar having to say so twice.
	"""

	_TOKEN = re_compile(r"\(|\)|[^\s()]+")  #: Splits an expression into parentheses and the words between them.

	_expression: str        #: The expression being parsed, kept for the error messages.
	_tokens:     list[str]  #: The expression's tokens, in order.
	_position:   int        #: Index of the token to read next.

	def __init__(self, expression: str) -> None:
		"""
		Tokenize an expression.

		:param expression:  The SPDX license expression to parse.
		:raises ValueError: If the expression contains no tokens.
		"""
		self._expression = expression
		self._tokens = self._TOKEN.findall(expression)
		self._position = 0

		if len(self._tokens) == 0:
			raise ValueError(f"License expression '{expression}' is empty.")

	def Parse(self) -> LicenseExpression:
		"""
		Parse the whole expression.

		:returns:           The root of the expression tree.
		:raises ValueError: If the expression is malformed or names an unknown license.
		"""
		result = self._ParseOr()

		if self._position < len(self._tokens):
			raise ValueError(
				f"License expression '{self._expression}' has trailing input at '{self._tokens[self._position]}'."
			)

		return result

	def _ParseOr(self) -> LicenseExpression:
		"""
		Parse a sequence of ``OR`` operands, the loosest-binding operator.

		:returns: The parsed expression.
		"""
		left = self._ParseAnd()
		while self._Accept("OR"):
			left = OrOperator(left, self._ParseAnd())

		return left

	def _ParseAnd(self) -> LicenseExpression:
		"""
		Parse a sequence of ``AND`` operands.

		:returns: The parsed expression.
		"""
		left = self._ParseWith()
		while self._Accept("AND"):
			left = AndOperator(left, self._ParseWith())

		return left

	def _ParseWith(self) -> LicenseExpression:
		"""
		Parse a ``WITH`` clause, whose right operand is an exception rather than a license.

		:returns:           The parsed expression.
		:raises ValueError: If ``WITH`` isn't followed by an exception identifier.
		"""
		left = self._ParseSimple()
		if self._Accept("WITH"):
			if (identifier := self._Next()) is None:
				raise ValueError(f"License expression '{self._expression}' ends after 'WITH'.")

			left = WithOperator(left, LicenseException(identifier))

		return left

	def _ParseSimple(self) -> LicenseExpression:
		"""
		Parse a parenthesized expression, a license reference, or a license identifier with an optional ``+``.

		:returns:           The parsed expression.
		:raises ValueError: If the expression ends early, a parenthesis is unbalanced, or a license is unknown.
		"""
		if (token := self._Next()) is None:
			raise ValueError(f"License expression '{self._expression}' ends unexpectedly.")

		if token == "(":
			inner = self._ParseOr()
			if not self._Accept(")"):
				raise ValueError(f"License expression '{self._expression}' is missing a closing parenthesis.")

			return inner

		if token == ")":
			raise ValueError(f"License expression '{self._expression}' has an unmatched closing parenthesis.")

		# 'GPL-2.0+' is the deprecated spelling of 'GPL-2.0-or-later' and is still legal grammar
		orLater = token.endswith("+")
		identifier = token[:-1] if orLater else token

		if identifier.startswith("LicenseRef-"):
			expression: LicenseExpression = LicenseReference(identifier[len("LicenseRef-"):])
		elif identifier.startswith("DocumentRef-") and ":LicenseRef-" in identifier:
			documentIdentifier, _, licenseIdentifier = identifier.partition(":LicenseRef-")
			expression = LicenseReference(licenseIdentifier, documentIdentifier[len("DocumentRef-"):])
		elif (spdxLicense := SPDX_INDEX.get(identifier, None)) is not None:
			expression = SPDXLicense(spdxLicense)
		else:
			ex = ValueError(f"License expression '{self._expression}' names unknown license '{identifier}'.")
			ex.add_note("Known licenses are the SPDX identifiers in 'pyTooling.Licensing.SPDX_INDEX'.")
			raise ex

		return OrLaterOperator(expression) if orLater else expression

	def _Next(self) -> Nullable[str]:
		"""
		Consume and return the next token.

		:returns: The next token, or ``None`` if the expression is exhausted.
		"""
		if self._position >= len(self._tokens):
			return None

		self._position += 1

		return self._tokens[self._position - 1]

	def _Accept(self, keyword: str) -> bool:
		"""
		Consume the next token if it is the given keyword.

		Keywords are matched case-insensitively, because published metadata writes ``and`` as often as ``AND``.

		:param keyword: The keyword to look for.
		:returns:       ``True``, if the keyword was there and was consumed.
		"""
		if self._position < len(self._tokens) and self._tokens[self._position].upper() == keyword:
			self._position += 1

			return True

		return False
