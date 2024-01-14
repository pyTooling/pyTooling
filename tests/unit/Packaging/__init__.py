# ==================================================================================================================== #
#             _____           _ _               ____            _               _                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ __ _  ___| | ____ _  __ _(_)_ __   __ _                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) / _` |/ __| |/ / _` |/ _` | | '_ \ / _` |                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/ (_| | (__|   < (_| | (_| | | | | | (_| |                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   \__,_|\___|_|\_\__,_|\__, |_|_| |_|\__, |                         #
# |_|    |___/                          |___/                             |___/         |___/                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2021-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for the packaging helper functions.
"""
from pathlib  import Path
from unittest import TestCase
from pytest   import mark
from sys      import version_info

from pyTooling.Common import CurrentPlatform


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class HelperFunctions(TestCase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_VersionInformation(self) -> None:
		from pyTooling.Packaging import extractVersionInformation

		versionInformation = extractVersionInformation(Path("pyTooling/Common/__init__.py"))
		self.assertIsInstance(versionInformation.Keywords, list)
		self.assertEqual(36, len(versionInformation.Keywords))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeMD(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		readme = loadReadmeFile(Path("README.md"))
		self.assertIn("# pyTooling", readme.Content)
		self.assertEqual("text/markdown", readme.MimeType)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeReST(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		with self.assertRaises(ValueError):
			_ = loadReadmeFile(Path("README.rst"))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirements(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("doc/requirements.txt"))
		self.assertEqual(13, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsGit(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.Git.txt"))
		self.assertEqual(2, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsRemoteZIP(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.HTTPS-ZIP.txt"))
		self.assertEqual(1, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsRecursive(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.txt"), debug=True)
		self.assertEqual(5, len(requirements))


class VersionInformation(TestCase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_VersionInformation(self) -> None:
		from pyTooling.Packaging import VersionInformation

		versionInfo = VersionInformation(
			author="Author",
			email="email",
			copyright="copyright",
			license="license",
			version="0.0.1",
			description="description",
			keywords=["keyword1", "keyword2"]
		)

		self.assertEqual("Author", versionInfo.Author)
		self.assertEqual("email", versionInfo.Email)
		self.assertEqual("copyright", versionInfo.Copyright)
		self.assertEqual("license", versionInfo.License)
		self.assertEqual("0.0.1", versionInfo.Version)
		self.assertEqual("description", versionInfo.Description)
		self.assertListEqual(["keyword1", "keyword2"], versionInfo.Keywords)


class DescribePackage(TestCase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_PythonPackage(self):
		print()

		from pyTooling.Packaging import DescribePythonPackage

		packageName = "pyPackage.Tool"
		packagePath = Path("tests") / Path(packageName)

		packageInformation = DescribePythonPackage(
			packageName=packageName,
			description="Swiss army knife.",
			projectURL="https://",
			sourceCodeURL="https://",
			documentationURL="https://",
			issueTrackerCodeURL="https://",
			sourceFileWithVersion=packagePath / "__init__.py",
			keywords=("Swiss", "Knife")
		)

		self.assertEqual(16, len(packageInformation))
		self.assertEqual(packageName, packageInformation["name"])
		# TODO: more checks

	@mark.xfail(CurrentPlatform.IsMSYS2Environment and version_info > (3, 9), reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_PythonPackageFromGitHub(self):
		print()

		from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub

		packageName = "pyPackage"
		packagePath = Path("tests") / Path(packageName)

		packageInformation = DescribePythonPackageHostedOnGitHub(
			packageName=packageName,
			description="Swiss army knife.",
			gitHubNamespace=packageName,
			gitHubRepository=packageName,
			sourceFileWithVersion=packagePath / "__init__.py",
			requirementsFile=packagePath / "requirements.txt",
			documentationRequirementsFile=packagePath / "requirements.Doc.txt",
			unittestRequirementsFile=packagePath / "requirements.Test.txt",
			packagingRequirementsFile=packagePath / "requirements.Build.txt",
			additionalRequirements={
				"dist": ["Wheel"],
			}
		)

		self.assertEqual(16, len(packageInformation))
		self.assertEqual(packageName, packageInformation["name"])
		# TODO: more checks
