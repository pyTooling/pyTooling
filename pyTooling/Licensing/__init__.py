# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python package:     Translation of license names.
#
# License:
# ============================================================================
# Copyright 2020-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
from ..Decorators  import export


PYTHON_CLASSIFIERS = {
	"Apache-2.0":       "License :: OSI Approved :: Apache Software License",
	"BSD-3-Clause":     "License :: OSI Approved :: BSD License",
	"MIT":              "License :: OSI Approved :: MIT License",
	"GPL-2.0-or-later": "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
}


@export
class License:
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
		return self._name

	@property
	def SPDXIdentifier(self) -> str:
		return self._spdxIdentifier

	@property
	def OSIApproved(self) -> bool:
		return self._osiApproved

	@property
	def FSFApproved(self) -> bool:
		return self._fsfApproved

	@property
	def PythonClassifier(self) -> str:
		try:
			return PYTHON_CLASSIFIERS[self._spdxIdentifier]
		except KeyError:
			raise ValueError(f"License has no known Python classifier.")


Apache_2_0_License =   License("Apache-2.0", "Apache License 2.0", True, True)
BSD_3_Clause_License = License("BSD-3-Clause", "BSD 3-Clause Revised License", True, True)
GPL_2_0_or_later =     License("GPL-2.0-or-later", "GNU General Public License v2.0 or later", True, True)
MIT_License =          License("MIT", "MIT License", True, True)


SPDX_INDEX = {
	"Apache-2.0":       Apache_2_0_License,
	"BSD-3-Clause":     BSD_3_Clause_License,
	"GPL-2.0-or-later": GPL_2_0_or_later,
	"MIT":              MIT_License
}
