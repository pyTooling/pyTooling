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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. hint:: See :ref:`high-level help <LICENSING>` for explanations and usage examples.
"""
from dataclasses  import dataclass
from typing       import Any, Dict


try:
	from ..Decorators import export
	from ..MetaClasses import ExtendedType
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Licensing] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export
		from MetaClasses import ExtendedType
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Licensing] Could not import from 'Decorators' directly!")
		raise ex


__all__ = [
	"PYTHON_LICENSE_NAMES",

	"Apache_2_0_License",
	"BSD_3_Clause_License",
	"GPL_2_0_or_later",
	"MIT_License",

	"SPDX_INDEX"
]


@export
@dataclass
class PythonLicenseNames:
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
PYTHON_LICENSE_NAMES: Dict[str, PythonLicenseNames] = {
	"Apache-2.0":       PythonLicenseNames("Apache 2.0",       "Apache Software License"),
	"BSD-3-Clause":     PythonLicenseNames("BSD",              "BSD License"),
	"MIT":              PythonLicenseNames("MIT",              "MIT License"),
	"GPL-2.0-or-later": PythonLicenseNames("GPL-2.0-or-later", "GNU General Public License v2 or later (GPLv2+)"),
}


@export
class License(metaclass=ExtendedType, useSlots=True):
	"""Representation of a license."""

	_spdxIdentifier: str  #: Unique SPDX identifier.
	_name: str            #: Name of the license.
	_osiApproved: bool    #: OSI approval status
	_fsfApproved: bool    #: FSF approval status

	def __init__(self, spdxIdentifier: str, name: str, osiApproved: bool = False, fsfApproved: bool = False):
		self._spdxIdentifier = spdxIdentifier
		self._name = name
		self._osiApproved = osiApproved
		self._fsfApproved = fsfApproved

	@property
	def Name(self) -> str:
		"""
		Returns the license' name.

		:returns: License name.
		"""
		return self._name

	@property
	def SPDXIdentifier(self) -> str:
		"""
		Returns the license' unique `SPDX identifier <https://spdx.org/licenses/>`__.

		:returns: The the unique SPDX identifier.
		"""
		return self._spdxIdentifier

	@property
	def OSIApproved(self) -> bool:
		"""
		Returns true, if the license is approved by OSI (`Open Source Initiative <https://opensource.org/>`__).

		:returns: True, if the license is approved by the Open Source Initiative.
		"""
		return self._osiApproved

	@property
	def FSFApproved(self) -> bool:
		"""
		Returns true, if the license is approved by FSF (`Free Software Foundation <https://www.fsf.org/>`__).

		:returns: True, if the license is approved by the Free Software Foundation.
		"""
		return self._fsfApproved

	@property
	def PythonLicenseName(self) -> str:
		"""
		Returns the Python license name for this license if it's defined.

		:returns: The Python license name.
		:raises ValueError: If there is no license name defined for the license. |br| (See and check :py:data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES`)
		"""
		try:
			item: PythonLicenseNames = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError as ex:
			raise ValueError("License has no Python specify information.") from ex

		return item.ShortName

	@property
	def PythonClassifier(self) -> str:
		"""
		Returns the Python package classifier for this license if it's defined.

		.. seealso::

		   List of `Python classifiers <https://pypi.org/classifiers/>`__

		:returns: The Python package classifier.
		:raises ValueError: If there is no classifier defined for the license. |br| (See and check :py:data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES`)
		"""
		try:
			item: PythonLicenseNames = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError as ex:
			raise ValueError(f"License has no Python specify information.") from ex

		osi = "OSI Approved :: " if self._osiApproved else ""
		return f"License :: {osi}{item.Classifier}"

	def __eq__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are identical (comparison based on SPDX identifiers).

		:returns: True, if both licenses are identical.
		:raises TypeError: If second operand is not of type :py:class:`License`.
		"""
		if isinstance(other, License):
			return self._spdxIdentifier == other._spdxIdentifier
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by equal operator.")

	def __ne__(self, other: Any) -> bool:
		"""
		Returns true, if both licenses are not identical (comparison based on SPDX identifiers).

		:returns: True, if both licenses are not identical.
		:raises TypeError: If second operand is not of type :py:class:`License`.
		"""
		if isinstance(other, License):
			return self._spdxIdentifier != other._spdxIdentifier
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by unequal operator.")

	def __le__(self, other: Any) -> bool:
		"""Returns true, if both licenses are compatible."""
		raise NotImplementedError("License compatibility check is not yet implemented.")

	def __ge__(self, other: Any) -> bool:
		"""Returns true, if both licenses are compatible."""
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


Apache_2_0_License =   License("Apache-2.0", "Apache License 2.0", True, True)
BSD_3_Clause_License = License("BSD-3-Clause", "BSD 3-Clause Revised License", True, True)
GPL_2_0_or_later =     License("GPL-2.0-or-later", "GNU General Public License v2.0 or later", True, True)
MIT_License =          License("MIT", "MIT License", True, True)


#: Mapping of predefined licenses
SPDX_INDEX: Dict[str, License] = {
	"Apache-2.0":       Apache_2_0_License,
	"BSD-3-Clause":     BSD_3_Clause_License,
	"GPL-2.0-or-later": GPL_2_0_or_later,
	"MIT":              MIT_License
}
