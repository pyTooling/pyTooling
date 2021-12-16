# =============================================================================
#             _____           _ _               ____            _               _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ __ _  ___| | ____ _  __ _(_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) / _` |/ __| |/ / _` |/ _` | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/ (_| | (__|   < (_| | (_| | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   \__,_|\___|_|\_\__,_|\__, |_|_| |_|\__, |
# |_|    |___/                          |___/                             |___/         |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Testing the pyTooling.Packaging module
#
# License:
# ============================================================================
# Copyright 2021-2021 Patrick Lehmann - Bötzingen, Germany
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
"""\
pyTooling.Packaging
###################

:copyright: Copyright 2021-2021 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from pathlib  import Path
from unittest import TestCase

from pyTooling.Packaging import loadReadmeFile, loadRequirementsFile, extractVersionInformation


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class HelperFunctions(TestCase):
	def test_VersionInformation(self) -> None:
		versionInformation =extractVersionInformation(Path("pyTooling/Common/__init__.py"))
		self.assertIsInstance(versionInformation.Keywords, list)
		self.assertEqual(11, len(versionInformation.Keywords))

	def test_loadReadme(self) -> None:
		_ = loadReadmeFile(Path("README.md"))

	def test_loadRequirements(self) -> None:
		_ = loadRequirementsFile(Path("requirements.txt"))