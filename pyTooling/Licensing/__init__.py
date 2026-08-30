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
from typing                import Any, ClassVar, Generator, Optional as Nullable
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.MetaClasses import ExtendedType, abstractclass, abstractmethod


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
class LicensingError(ToolingException):
	"""Base exception of all exceptions raised by :mod:`pyTooling.Licensing`."""


@export
class LicenseExpressionError(LicensingError):
	"""
	The exception is raised when an SPDX license expression is malformed or names a license SPDX doesn't define.
	"""


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

		:returns: The unique SPDX identifier.
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
		Compute a hash from the license's SPDX identifier.

		A license compares equal to its identifier as a string, so the two hash equally as well.

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
		Returns the internal unique representation (:attr:`spdxIdentifier`).

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
@abstractclass
class LicenseExpression(metaclass=ExtendedType, slots=True):
	"""
	Base-class of every node in an `SPDX license expression`_ tree.

	.. _SPDX license expression: https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/

	An expression is a tree. Its operators - every node that is applied to operands, and the only kind of node that
	can be a :attr:`Parent` - derive from :class:`Operator`:

	:class:`OrLaterOperator`
	  |rarr| the ``+`` suffix: the named license or any later version of it.
	:class:`WithOperator`
	  |rarr| ``WITH``: a license together with an exception to it.
	:class:`AndOperator`
	  |rarr| ``AND``: both licenses apply.
	:class:`OrOperator`
	  |rarr| ``OR``: either license applies.

	Its leaves are:

	:class:`SPDXLicense`
	  |rarr| a license on the SPDX License List, named by its identifier.
	:class:`LicenseReference`
	  |rarr| a license that is *not* on that list, written as ``LicenseRef-<id>``.
	:class:`LicenseException`
	  |rarr| an exception from the SPDX exception list, the right operand of ``WITH``.

	The SPDX grammar defines:

	.. code-block:: text

	   simple-expression   = license-id | license-id "+" | license-ref
	   compound-expression = ( simple-expression
	                         | simple-expression "WITH" license-exception-id
	                         | compound-expression "AND" compound-expression
	                         | compound-expression "OR" compound-expression
	                         | "(" compound-expression ")" )

	There are three binary operators, one unary one, and parentheses. There is **no negation** - an expression
	says which licenses apply, never which don't.

	Every node knows its :attr:`Parent` and its :attr:`Root`, which is what a :class:`License` can't carry: the
	predefined licenses are shared objects, so :data:`MIT_License` appears in many expressions at once and belongs to
	none of them. :class:`SPDXLicense` is the wrapper that gives a license object a placeholder in the expression tree.

	A tree is built bottom-up by handing the operands to an operator, or by assigning them to the operator's operand
	slots afterwards. Both link the operand back to its operator:

	.. code-block:: python

	   bottomUp = AndOperator(SPDXLicense(Apache_2_0_License), SPDXLicense(MIT_License))

	   assembled = AndOperator()
	   assembled.Left =  SPDXLicense(Apache_2_0_License)
	   assembled.Right = SPDXLicense(MIT_License)

	The ``parent`` parameter only *records* a parent - it can't know which slot the operand belongs in, so it never
	fills one.
	"""

	PRECEDENCE: ClassVar[int] = 0  #: Precedence of this node's operator; a lower value binds tighter.

	_parent: Nullable["Operator"]  #: The operator this expression is an operand of, or ``None`` at the root.
	_root:   "LicenseExpression"   #: The outermost expression this node belongs to; ``self`` at the root.

	def __init__(self, parent: Nullable["Operator"] = None) -> None:
		"""
		Initialize an expression node.

		:param parent:     Optional, the operator this node becomes an operand of.
		:raises TypeError: If parameter 'parent' is not of type :class:`Operator`.
		"""
		if parent is None:
			self._parent = None
			self._root =   self
		elif not isinstance(parent, Operator):
			ex = TypeError("Parameter 'parent' is not an Operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		else:
			self._parent = parent
			self._root =   parent._root

	@property
	def Parent(self) -> Nullable["Operator"]:
		"""
		Property to access the operator this expression is an operand of (:attr:`_parent`).

		Assigning an operator records it as this node's parent and re-roots this node and everything below it to that
		operator's :attr:`Root`. The operator's operands are not changed by the assignment.

		:returns:           The parent operator, or ``None`` if this node is the root.
		:raises ValueError: If ``None`` is assigned. |br|
		                    A node that is an operand of an operator can't be detached from it.
		:raises TypeError:  If an object that is not an :class:`Operator` is assigned. |br|
		                    A leaf is applied to nothing, so it can never be a parent.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: Nullable["Operator"]) -> None:
		if parent is None:
			raise ValueError("Parameter 'parent' is None.")
		elif not isinstance(parent, Operator):
			ex = TypeError("Parameter 'parent' is not an Operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

		for expression in self.IterateExpression():
			expression._root = parent._root

	@readonly
	def Root(self) -> "LicenseExpression":
		"""
		Read-only property to access the outermost expression this node belongs to (:attr:`_root`).

		The root is maintained by :attr:`Parent`: adopting a node re-roots it and everything below it, so the field
		can't fall behind the tree it describes.

		:returns: The root of the expression tree, which is the node itself if it has no parent.
		"""
		return self._root

	def IterateExpression(self) -> Generator["LicenseExpression", None, None]:
		"""
		Iterate this expression depth-first, in the order its nodes are written.

		A leaf is the expression itself. The operators override this to yield their operands around themselves, so an
		infix operator comes between its two operands and the ``+`` suffix comes after the expression it applies to.

		:returns: A generator of every node in this expression, this node included.
		"""
		yield self

	@classmethod
	def Parse(cls, expression: str) -> "LicenseExpression":
		"""
		Parse an SPDX license expression into a tree of expression nodes.

		Operator precedence is the one SPDX defines - ``+`` binds tighter than ``WITH``, which binds tighter than
		``AND``, which binds tighter than ``OR`` - and parentheses override it. ``AND`` and ``OR`` associate to the
		left.

		:param expression:              The SPDX license expression to parse.
		:returns:                       The root of the parsed expression tree.
		:raises LicenseExpressionError: If the expression is empty, malformed, or names a license that isn't known.
		"""
		parser = _LicenseExpressionParser(expression)
		return parser.Parse()

	@abstractmethod
	def __str__(self) -> str:  # type: ignore[empty-body]
		"""
		Return this expression in SPDX syntax.

		Parentheses are written only where the default precedence would otherwise read the expression differently, so
		a parsed expression renders back to its shortest correct form rather than a fully bracketed one.

		:returns: The expression in SPDX syntax.
		"""


@export
@abstractclass
class Operator(LicenseExpression):
	"""
	Base-class of every expression node that is applied to operands.

	Operator kinds:

	* :class:`UnaryOperator` takes one operand
	* :class:`BinaryOperator` takes two operands.

	Only an operator can be an operand's :attr:`~LicenseExpression.Parent`.
	"""


@export
class SPDXLicense(LicenseExpression):
	"""
	A single license in an expression, named by its SPDX identifier.
	"""

	_license: _LicenseType  #: The well-known license this node refers to.

	def __init__(self, spdxLicense: _LicenseType, parent: Nullable[Operator] = None) -> None:
		"""
		Initialize a reference to an SPDX license.

		:param spdxLicense: The license this node stands for.
		:param parent:      Optional, the operator this node becomes an operand of.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Operator`.
		:raises ValueError: If parameter 'spdxLicense' is None.
		:raises TypeError:  If parameter 'spdxLicense' is not of type :class:`License`.
		"""
		super().__init__(parent)

		if spdxLicense is None:
			raise ValueError("Parameter 'spdxLicense' is None.")
		elif not isinstance(spdxLicense, _LicenseType):
			ex = TypeError("Parameter 'spdxLicense' is not a License.")
			ex.add_note(f"Got type '{getFullyQualifiedName(spdxLicense)}'.")
			raise ex

		self._license = spdxLicense

	@readonly
	def License(self) -> _LicenseType:
		"""
		Read-only property to access the license this node stands for (:attr:`_license`).

		:returns: The license.
		"""
		return self._license

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the license' SPDX identifier (:pycode:`_license._spdxIdentifier`).

		:returns: The license's SPDX identifier.
		"""
		return self._license._spdxIdentifier

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

	It may name the document it is defined in, as ``DocumentRef-<id>:LicenseRef-<id>``.

	There is no predefined :class:`License` object, because SPDX doesn't know the license - only the document declaring it
	does.
	"""

	_licenseIdentifier:  str            #: Identifier following ``LicenseRef-``.
	_documentIdentifier: Nullable[str]  #: Identifier following ``DocumentRef-``, if the reference names one.

	def __init__(
		self,
		licenseIdentifier:  str,
		documentIdentifier: Nullable[str] =      None,
		parent:             Nullable[Operator] = None
	) -> None:
		"""
		Initialize a license reference.

		:param licenseIdentifier:  Identifier following ``LicenseRef-``.
		:param documentIdentifier: Optional, identifier following ``DocumentRef-``.
		:param parent:             Optional, the operator this node becomes an operand of.
		:raises TypeError:         If parameter 'parent' is not of type :class:`Operator`.
		:raises ValueError:        If parameter 'licenseIdentifier' is None.
		:raises TypeError:         If parameter 'licenseIdentifier' is not of type :class:`str`.
		:raises ValueError:        If parameter 'licenseIdentifier' is empty.
		:raises TypeError:         If parameter 'documentIdentifier' is not of type :class:`str`.
		:raises ValueError:        If parameter 'documentIdentifier' is empty.
		"""
		super().__init__(parent)

		if licenseIdentifier is None:
			raise ValueError("Parameter 'licenseIdentifier' is None.")
		elif not isinstance(licenseIdentifier, str):
			ex = TypeError("Parameter 'licenseIdentifier' is not a string.")
			ex.add_note(f"Got type '{getFullyQualifiedName(licenseIdentifier)}'.")
			raise ex
		elif len(licenseIdentifier) == 0:
			raise ValueError("Parameter 'licenseIdentifier' is empty.")

		if documentIdentifier is not None:
			if not isinstance(documentIdentifier, str):
				ex = TypeError("Parameter 'documentIdentifier' is not a string.")
				ex.add_note(f"Got type '{getFullyQualifiedName(documentIdentifier)}'.")
				raise ex
			elif len(documentIdentifier) == 0:
				raise ValueError("Parameter 'documentIdentifier' is empty.")

		self._licenseIdentifier =  licenseIdentifier
		self._documentIdentifier = documentIdentifier

	@readonly
	def LicenseIdentifier(self) -> str:
		"""
		Read-only property to access the identifier following ``LicenseRef-`` (:attr:`_licenseIdentifier`).

		:returns: The license reference's identifier.
		"""
		return self._licenseIdentifier

	@readonly
	def DocumentIdentifier(self) -> Nullable[str]:
		"""
		Read-only property to access the identifier following ``DocumentRef-`` (:attr:`_documentIdentifier`).

		:returns: The document reference's identifier, or ``None`` if the reference names no document.
		"""
		return self._documentIdentifier

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
	The right operand of a :class:`WithOperator`, naming an exception from the SPDX exception list.

	It is a leaf node in the expression tree like a license, but it is not one. An exception modifies a license and can't
	stand on its own.
	"""

	_identifier: str  #: The exception's SPDX identifier.

	def __init__(self, identifier: str, parent: Nullable[Operator] = None) -> None:
		"""
		Initialize a license exception.

		:param identifier:  The exception's SPDX identifier.
		:param parent:      Optional, the operator this node becomes an operand of.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Operator`.
		:raises ValueError: If parameter 'identifier' is None.
		:raises TypeError:  If parameter 'identifier' is not of type :class:`str`.
		:raises ValueError: If parameter 'identifier' is empty.
		"""
		super().__init__(parent)

		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not a string.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex
		elif len(identifier) == 0:
			raise ValueError("Parameter 'identifier' is empty.")

		self._identifier = identifier

	@readonly
	def Identifier(self) -> str:
		"""
		Read-only property to access the exception's SPDX identifier (:attr:`_identifier`).

		:returns: The exception's identifier.
		"""
		return self._identifier

	def __str__(self) -> str:
		"""
		Return the exception's SPDX identifier.

		:returns: The identifier.
		"""
		return self._identifier


@export
@abstractclass
class UnaryOperator(Operator):
	"""
	Base-class of the expression operators taking one operand.

	SPDX defines exactly one unary operator:

	* the ``+`` suffix of :class:`OrLaterOperator`.

	The operand is reachable as :attr:`Operand` and is assignable, so an operator can be filled after it was created.
	"""

	_operand: Nullable[LicenseExpression]  #: The expression this operator is applied to.

	def __init__(
		self,
		operand: Nullable[LicenseExpression] = None,
		parent:  Nullable[Operator] =          None
	) -> None:
		"""
		Initialize a unary operator with its operand.

		:param operand:    Optional, the expression this operator is applied to.
		:param parent:     Optional, the operator this node becomes an operand of.
		:raises TypeError: If parameter 'parent' is not of type :class:`Operator`.
		:raises TypeError: If parameter 'operand' is not of type :class:`LicenseExpression`.
		"""
		super().__init__(parent)

		if operand is not None:
			self._operand = operand

			if not isinstance(operand, LicenseExpression):
				ex = TypeError("Parameter 'operand' is not a LicenseExpression.")
				ex.add_note(f"Got type '{getFullyQualifiedName(operand)}'.")
				raise ex

			operand.Parent = self
		else:
			self._operand = None

	def IterateExpression(self) -> Generator[LicenseExpression, None, None]:
		"""
		Iterate this operator depth-first, its operand first, because ``+`` is written after the expression it suffixes.

		:returns: A generator of every node in this expression, this operator included.
		"""
		if self._operand is not None:
			yield from self._operand.IterateExpression()

		yield self

	@property
	def Operand(self) -> Nullable[LicenseExpression]:
		"""
		Property to access the expression this operator is applied to (:attr:`_operand`).

		A slot is filled once. Assigning an expression makes this operator its :attr:`~LicenseExpression.Parent`,
		which puts it - and everything below it - into this tree.

		:returns:               The operand, or ``None`` if the operator wasn't assigned yet.
		:raises ValueError:     If ``None`` is assigned.
		:raises TypeError:      If an object that is not a :class:`LicenseExpression` is assigned.
		:raises LicensingError: If this operator has an operand already.
		:raises LicensingError: If the assigned expression is already an operand of another operator.
		"""
		return self._operand

	@Operand.setter
	def Operand(self, operand: LicenseExpression) -> None:
		if operand is None:
			raise ValueError("Parameter 'operand' is None.")
		elif not isinstance(operand, LicenseExpression):
			ex = TypeError("Parameter 'operand' is not a LicenseExpression.")
			ex.add_note(f"Got type '{getFullyQualifiedName(operand)}'.")
			raise ex
		elif self._operand is not None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has an operand already.")
		elif operand._parent is not None:
			raise LicensingError("Parameter 'operand' is already an operand of another operator.")

		self._operand = operand
		operand.Parent = self


@export
class OrLaterOperator(UnaryOperator):
	"""
	The ``+`` suffix, as in ``GPL-2.0+``: the named license *or any later version of it*.

	.. attention::

	   The operator itself is not deprecated - Annex D.3 of the SPDX specification defines it and uses ``CDDL-1.0+``
	   as its example. Its combination with the GNU licenses is: `SPDX License List 3.0
	   <https://spdx.org/licenses/>`__ (2017-12-28) introduced ``GPL-2.0-only`` and ``GPL-2.0-or-later`` and
	   deprecated the ``GPL-2.0``, ``LGPL-2.1`` and ``AGPL-3.0`` identifiers that ``+`` was applied to. Published
	   metadata still contains ``GPL-2.0+``, so an expression using it has to parse.
	"""

	PRECEDENCE: ClassVar[int] = 1  #: Binds tighter than every binary operator, looser than a bare license.

	def __str__(self) -> str:
		"""
		Return the operand followed by ``+``.

		:returns:               The expression in SPDX syntax.
		:raises LicensingError: If the operator has no operand yet.
		"""
		if self._operand is None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has no operand yet.")

		return f"{self._operand}+"


@export
@abstractclass
class BinaryOperator(Operator):
	"""
	Base-class of the expression operators taking two operands.

	SPDX defines three binary operators:

	* :class:`WithOperator`,
	* :class:`AndOperator` and
	* :class:`OrOperator`.

	The operands are reachable as :attr:`Left` and :attr:`Right`. :attr:`KEYWORD` is the operator keyword between the
	operands.
	"""

	KEYWORD: ClassVar[str]                #: The operator's keyword, as it is written between the operands.

	_left:   Nullable[LicenseExpression]  #: The operator's left operand.
	_right:  Nullable[LicenseExpression]  #: The operator's right operand.

	def __init__(
		self,
		left:   Nullable[LicenseExpression] = None,
		right:  Nullable[LicenseExpression] = None,
		parent: Nullable[Operator] =          None
	) -> None:
		"""
		Initialize a binary operator with both operands.

		:param left:       Optional, the operator's left operand.
		:param right:      Optional, the operator's right operand.
		:param parent:     Optional, the operator this node becomes an operand of.
		:raises TypeError: If parameter 'parent' is not of type :class:`Operator`.
		:raises TypeError: If parameter 'left' is not of type :class:`LicenseExpression`.
		:raises TypeError: If parameter 'right' is not of type :class:`LicenseExpression`.
		"""
		super().__init__(parent)

		if left is not None:
			self._left = left

			if not isinstance(left, LicenseExpression):
				ex = TypeError("Parameter 'left' is not a LicenseExpression.")
				ex.add_note(f"Got type '{getFullyQualifiedName(left)}'.")
				raise ex

			left.Parent = self
		else:
			self._left = None

		if right is not None:
			self._right = right

			if not isinstance(right, LicenseExpression):
				ex = TypeError("Parameter 'right' is not a LicenseExpression.")
				ex.add_note(f"Got type '{getFullyQualifiedName(right)}'.")
				raise ex

			right.Parent = self
		else:
			self._right = None

	def IterateExpression(self) -> Generator[LicenseExpression, None, None]:
		"""
		Iterate this operator depth-first in infix order: left operand, this operator, right operand.

		:returns: A generator of every node in this expression, this operator included.
		"""
		if self._left is not None:
			yield from self._left.IterateExpression()

		yield self

		if self._right is not None:
			yield from self._right.IterateExpression()

	@property
	def Left(self) -> Nullable[LicenseExpression]:
		"""
		Property to access the operator's left operand (:attr:`_left`).

		A slot is filled once. Assigning an expression makes this operator its :attr:`~LicenseExpression.Parent`,
		which puts it - and everything below it - into this tree.

		:returns:               The left operand, or ``None`` if it wasn't assigned yet.
		:raises ValueError:     If ``None`` is assigned.
		:raises TypeError:      If an object that is not a :class:`LicenseExpression` is assigned.
		:raises LicensingError: If this operator has a left operand already.
		:raises LicensingError: If the assigned expression is already an operand of another operator.
		"""
		return self._left

	@Left.setter
	def Left(self, operand: LicenseExpression) -> None:
		if operand is None:
			raise ValueError("Parameter 'operand' is None.")
		elif not isinstance(operand, LicenseExpression):
			ex = TypeError("Parameter 'operand' is not a LicenseExpression.")
			ex.add_note(f"Got type '{getFullyQualifiedName(operand)}'.")
			raise ex
		elif self._left is not None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has a left operand already.")
		elif operand._parent is not None:
			raise LicensingError("Parameter 'operand' is already an operand of another operator.")

		self._left = operand
		operand.Parent = self

	@property
	def Right(self) -> Nullable[LicenseExpression]:
		"""
		Property to access the operator's right operand (:attr:`_right`).

		A slot is filled once. Assigning an expression makes this operator its :attr:`~LicenseExpression.Parent`,
		which puts it - and everything below it - into this tree.

		:returns:               The right operand, or ``None`` if it wasn't assigned yet.
		:raises ValueError:     If ``None`` is assigned.
		:raises TypeError:      If an object that is not a :class:`LicenseExpression` is assigned.
		:raises LicensingError: If this operator has a right operand already.
		:raises LicensingError: If the assigned expression is already an operand of another operator.
		"""
		return self._right

	@Right.setter
	def Right(self, operand: LicenseExpression) -> None:
		if operand is None:
			raise ValueError("Parameter 'operand' is None.")
		elif not isinstance(operand, LicenseExpression):
			ex = TypeError("Parameter 'operand' is not a LicenseExpression.")
			ex.add_note(f"Got type '{getFullyQualifiedName(operand)}'.")
			raise ex
		elif self._right is not None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has a right operand already.")
		elif operand._parent is not None:
			raise LicensingError("Parameter 'operand' is already an operand of another operator.")

		self._right = operand
		operand.Parent = self

	def __str__(self) -> str:
		"""
		Return both operands with the operator's keyword between them.

		:returns:               The expression in SPDX syntax.
		:raises LicensingError: If one of the operator's operands wasn't assigned yet.
		"""
		if self._left is None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has no left operand yet.")
		elif self._right is None:
			raise LicensingError(f"Operator '{getFullyQualifiedName(self)}' has no right operand yet.")

		left =  f"({self._left})"  if self._left.PRECEDENCE  > self.PRECEDENCE else f"{self._left}"
		right = f"({self._right})" if self._right.PRECEDENCE > self.PRECEDENCE else f"{self._right}"

		return f"{left} {self.KEYWORD} {right}"


@export
class WithOperator(BinaryOperator):
	"""
	``WITH``, as in ``Apache-2.0 WITH LLVM-exception``: a license together with an exception to it.

	It is the only operator whose operands differ in kind - the right one is a :class:`LicenseException`, never a
	license - and it binds tighter than ``AND`` and ``OR``.
	"""

	PRECEDENCE: ClassVar[int] = 2       #: Binds tighter than ``AND`` and ``OR``.
	KEYWORD:    ClassVar[str] = "WITH"  #: The operator's keyword.


@export
class AndOperator(BinaryOperator):
	"""``AND``, as in ``Apache-2.0 AND MIT``: **both** licenses apply, and both have to be complied with."""

	PRECEDENCE: ClassVar[int] = 3      #: Binds tighter than ``OR``.
	KEYWORD:    ClassVar[str] = "AND"  #: The operator's keyword.


@export
class OrOperator(BinaryOperator):
	"""
	``OR``, as in ``Apache-2.0 OR BSD-2-Clause``: **either** license applies, and the recipient chooses which.

	Which one they chose is not something the expression records.
	"""

	PRECEDENCE: ClassVar[int] = 4     #: Binds loosest of all operators.
	KEYWORD:    ClassVar[str] = "OR"  #: The operator's keyword.


class _LicenseExpressionParser(metaclass=ExtendedType, slots=True):
	"""
	Recursive-descent parser for SPDX license expressions.

	One level of the descent per precedence level, lowest-binding first, which is what makes ``A OR B AND C`` parse as
	``A OR (B AND C)`` without the grammar having to say so twice. The descent is a class rather than a function
	because every level reads and advances the same token position, and that position is state the levels share.
	"""

	_TOKEN = re_compile(r"\(|\)|[^\s()]+")  #: Splits an expression into parentheses and the words between them.

	_expression: str        #: The expression being parsed, kept for the error messages.
	_tokens:     list[str]  #: The expression's tokens, in order.
	_position:   int        #: Index of the token to read next.

	def __init__(self, expression: str) -> None:
		"""
		Tokenize an expression.

		:param expression:              The SPDX license expression to parse.
		:raises TypeError:              If parameter 'expression' is not of type :class:`str`.
		:raises ValueError:             If parameter 'expression' is empty.
		:raises LicenseExpressionError: If the expression holds nothing but whitespace.
		"""
		if not isinstance(expression, str):
			ex = TypeError("Parameter 'expression' is not a string.")
			ex.add_note(f"Got type '{getFullyQualifiedName(expression)}'.")
			raise ex
		elif expression == "":
			raise ValueError("Parameter 'expression' is empty.")

		self._expression = expression
		self._tokens = self._TOKEN.findall(expression)
		self._position = 0

		if len(self._tokens) == 0:
			raise LicenseExpressionError(f"License expression '{expression}' is empty.")

	def Parse(self) -> LicenseExpression:
		"""
		Parse the whole expression.

		:returns:                       The root of the expression tree.
		:raises LicenseExpressionError: If the expression is malformed or names an unknown license.
		"""
		result = self._ParseOr()

		if self._position < len(self._tokens):
			raise LicenseExpressionError(
				f"License expression '{self._expression}' has trailing input at '{self._tokens[self._position]}'."
			)

		return result

	def _ParseOr(self) -> LicenseExpression:
		"""
		Parse a sequence of ``OR`` operands, the loosest-binding operator.

		:returns: The parsed expression.
		"""
		left = self._ParseAnd()
		while self._Accept(OrOperator.KEYWORD):
			left = OrOperator(left, self._ParseAnd())

		return left

	def _ParseAnd(self) -> LicenseExpression:
		"""
		Parse a sequence of ``AND`` operands.

		:returns: The parsed expression.
		"""
		left = self._ParseWith()
		while self._Accept(AndOperator.KEYWORD):
			left = AndOperator(left, self._ParseWith())

		return left

	def _ParseWith(self) -> LicenseExpression:
		"""
		Parse a ``WITH`` clause, whose right operand is an exception rather than a license.

		:returns:                       The parsed expression.
		:raises LicenseExpressionError: If ``WITH`` isn't followed by an exception identifier.
		"""
		left = self._ParseSimple()
		if self._Accept(WithOperator.KEYWORD):
			if (identifier := self._Next()) is None:
				raise LicenseExpressionError(f"License expression '{self._expression}' ends after 'WITH'.")

			left = WithOperator(left, LicenseException(identifier))

		return left

	def _ParseSimple(self) -> LicenseExpression:
		"""
		Parse a parenthesized expression, a license reference, or a license identifier with an optional ``+``.

		:returns:                       The parsed expression.
		:raises LicenseExpressionError: If the expression ends early, a parenthesis is unbalanced, or a license is unknown.
		"""
		if (token := self._Next()) is None:
			raise LicenseExpressionError(f"License expression '{self._expression}' ends unexpectedly.")

		if token == "(":
			inner = self._ParseOr()
			if not self._Accept(")"):
				raise LicenseExpressionError(f"License expression '{self._expression}' is missing a closing parenthesis.")

			return inner

		if token == ")":
			raise LicenseExpressionError(f"License expression '{self._expression}' has an unmatched closing parenthesis.")

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
			ex = LicenseExpressionError(f"License expression '{self._expression}' names unknown license '{identifier}'.")
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
