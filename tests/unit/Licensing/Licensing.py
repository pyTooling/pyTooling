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
from pyTooling.Licensing import PYTHON_LICENSE_NAMES, SPDX_INDEX, License
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


class SPDXLicenses(Testcase):
	def test_Apache(self) -> None:
		self.assertIn("Apache-2.0", SPDX_INDEX)
		self.assertIn("Apache-2.0", PYTHON_LICENSE_NAMES)


# class PythonClassifiers(Testcase):
# 	def test_OSIApproved(self) -> None:
# 		for spdxId, item in PYTHON_LICENSE_NAMES.items():
# 			license = SPDX_INDEX[spdxId]
# 			self.assertEqual("OSI Approved" in item.Classifier, license.OSIApproved)


class SPDXIndex(Testcase):
	"""Every predefined license is consistent with SPDX and with PyPI's classifier list."""

	def test_TheIndexIsKeyedByTheSPDXIdentifier(self) -> None:
		from pyTooling.Licensing import SPDX_INDEX

		for spdxIdentifier, license in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertEqual(spdxIdentifier, license.SPDXIdentifier)

	def test_EveryClassifierIsARealClassifier(self) -> None:
		"""The strings are checked against PyPI's own list, not against what looked right when they were typed."""

		from trove_classifiers    import classifiers
		from pyTooling.Licensing  import SPDX_INDEX

		for spdxIdentifier, license in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertIn(license.PythonClassifier, classifiers)

	def test_OSIApprovalMatchesTheClassifier(self) -> None:
		"""PyPI puts an OSI-approved license under 'OSI Approved ::', so the flag and the string must agree."""

		from pyTooling.Licensing import SPDX_INDEX

		for spdxIdentifier, license in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertEqual(
					license.OSIApproved,
					license.PythonClassifier.startswith("License :: OSI Approved :: ")
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
		from pyTooling.Licensing import SPDX_INDEX

		for spdxIdentifier, license in SPDX_INDEX.items():
			with self.subTest(license=spdxIdentifier):
				self.assertNotEqual("", license.PythonLicenseName)

	def test_TheOriginalFourAreUnchanged(self) -> None:
		"""The licenses that existed before keep their identifiers, names and short names."""

		from pyTooling.Licensing import Apache_2_0_License, BSD_3_Clause_License, GPL_2_0_or_later, MIT_License

		self.assertEqual("Apache 2.0", Apache_2_0_License.PythonLicenseName)
		self.assertEqual("BSD", BSD_3_Clause_License.PythonLicenseName)
		self.assertEqual("MIT", MIT_License.PythonLicenseName)
		self.assertEqual("GPL-2.0-or-later", GPL_2_0_or_later.PythonLicenseName)

