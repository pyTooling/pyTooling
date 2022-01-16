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
The Licensing module implements translation tables for various license names and identifiers.

List of SPDX identifiers:

* https://spdx.org/licenses/
* https://github.com/spdx/license-list-XML
"""
from typing       import Any, Dict, NamedTuple

from ..Decorators import export


@export
class PythonLicenseNames(NamedTuple):
	ShortName:  str
	Classifier: str

	def __repr__(self) -> str:
		return self.ShortName


PYTHON_LICENSE_NAMES: Dict[str, PythonLicenseNames] = {
	"Apache-2.0":       PythonLicenseNames("Apache 2.0",       "Apache Software License"),
	"BSD-3-Clause":     PythonLicenseNames("BSD",              "BSD License"),
	"MIT":              PythonLicenseNames("MIT",              "MIT License"),
	"GPL-2.0-or-later": PythonLicenseNames("GPL-2.0-or-later", "GNU General Public License v2 or later (GPLv2+)"),
}


@export
class License:
	"""Representation of a license."""

	_name: str
	_spdxIdentifier: str
	_osiApproved: bool
	_fsfApproved: bool

	def __init__(self, spdxIdentifier: str, name: str, osiApproved: bool = False, fsfApproved: bool = False):
		self._spdxIdentifier = spdxIdentifier
		self._name = name
		self._osiApproved = osiApproved
		self._fsfApproved = fsfApproved

	@property
	def Name(self) -> str:
		"""Returns the license' name."""
		return self._name

	@property
	def SPDXIdentifier(self) -> str:
		"""Returns the license' unique identifier."""
		return self._spdxIdentifier

	@property
	def OSIApproved(self) -> bool:
		"""Returns true if the license is approved by OSI (Open Source Initiative)."""
		return self._osiApproved

	@property
	def FSFApproved(self) -> bool:
		"""Returns true if the license is approved by FSF (Free Software Foundation)."""
		return self._fsfApproved

	@property
	def PythonLicenseName(self) -> str:
		"""
		Returns the Python license name for this license if it's defined.

		.. seealso::

		   List of `Python classifiers <https://pypi.org/classifiers/>`__
		"""
		try:
			item: PythonLicenseNames = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError:
			raise ValueError("License has no Python specify information.")

		return item.ShortName

	@property
	def PythonClassifier(self) -> str:
		"""
		Returns the Python classifier for this license if it's defined.

		.. seealso::

		   List of `Python classifiers <https://pypi.org/classifiers/>`__
		"""
		try:
			item: PythonLicenseNames = PYTHON_LICENSE_NAMES[self._spdxIdentifier]
		except KeyError:
			raise ValueError(f"License has no Python specify information.")

		osi = "OSI Approved :: " if self._osiApproved else ""
		return f"License :: {osi}{item.Classifier}"

	def __eq__(self, other: Any) -> bool:
		"""Returns true, if both licenses are identical (comparison based on SPDX identifiers)."""
		if isinstance(other, License):
			return self._spdxIdentifier == other._spdxIdentifier
		else:
			raise TypeError(f"Second operand of type '{other.__class__.__name__}' is not supported by equal operator.")

	def __ne__(self, other: Any) -> bool:
		"""Returns true, if both licenses are not identical (comparison based on SPDX identifiers)."""
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
		"""Returns the internal unique representation (a.k.a SPDX identifier)."""
		return self._spdxIdentifier

	def __str__(self) -> str:
		"""Returns the license' name."""
		return self._name


Apache_2_0_License =   License("Apache-2.0", "Apache License 2.0", True, True)
BSD_3_Clause_License = License("BSD-3-Clause", "BSD 3-Clause Revised License", True, True)
GPL_2_0_or_later =     License("GPL-2.0-or-later", "GNU General Public License v2.0 or later", True, True)
MIT_License =          License("MIT", "MIT License", True, True)


SPDX_INDEX: Dict[str, License] = {
	"Apache-2.0":       Apache_2_0_License,
	"BSD-3-Clause":     BSD_3_Clause_License,
	"GPL-2.0-or-later": GPL_2_0_or_later,
	"MIT":              MIT_License
}
