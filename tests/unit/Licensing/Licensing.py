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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from unittest     import TestCase

from pyTooling.Licensing import PYTHON_LICENSE_NAMES, SPDX_INDEX, License


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class LicenseDataClass(TestCase):
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
		with self.assertRaises(TypeError):
			_ = license1 == "spdx"
		with self.assertRaises(TypeError):
			_ = license1 != "spdx"

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


class SPDXLicenses(TestCase):
	def test_Apache(self) -> None:
		self.assertIn("Apache-2.0", SPDX_INDEX)
		self.assertIn("Apache-2.0", PYTHON_LICENSE_NAMES)


# class PythonClassifiers(TestCase):
# 	def test_OSIApproved(self) -> None:
# 		for spdxId, item in PYTHON_LICENSE_NAMES.items():
# 			license = SPDX_INDEX[spdxId]
# 			self.assertEqual("OSI Approved" in item.Classifier, license.OSIApproved)
