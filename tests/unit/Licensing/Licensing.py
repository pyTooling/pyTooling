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
# Python unittest:    Testing the Licensing module
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
from unittest     import TestCase

from pyTooling.Licensing import PYTHON_CLASSIFIERS, SPDX_INDEX, License


if __name__ == "__main__":
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class LicenseDataClass(TestCase):
	def test_Properies(self):
		license = License("spdx", "License Name", True, False)
		self.assertEqual("spdx", license.SPDXIdentifier)
		self.assertEqual("License Name", license.Name)
		self.assertEqual(True, license.OSIApproved)
		self.assertEqual(False, license.FSFApproved)

	def test_ClassifierConversion(self):
		license = License("Apache-2.0", "License Name", True, False)
		self.assertEqual("License :: OSI Approved :: Apache Software License", license.PythonClassifier)

	def test_ClassifierConversionException(self):
		license = License("spdx", "License Name", True, False)
		with self.assertRaises(ValueError):
			_ = license.PythonClassifier


class SPDXLicenses(TestCase):
	def test_Apache(self) -> None:
		self.assertIn("Apache-2.0", SPDX_INDEX)
		self.assertIn("Apache-2.0", PYTHON_CLASSIFIERS)


class PythonClassifiers(TestCase):
	def test_OSIApproved(self) -> None:
		for spdxId, classifier in PYTHON_CLASSIFIERS.items():
			license = SPDX_INDEX[spdxId]
			self.assertEqual("OSI Approved" in classifier, license.OSIApproved)
