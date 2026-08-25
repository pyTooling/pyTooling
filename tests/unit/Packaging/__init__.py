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
# Copyright 2021-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.Packaging`: the helper functions, the version information read from a
package, and the description assembled for setuptools.
"""
from contextlib import redirect_stdout
from io         import StringIO
from pathlib    import Path
from pytest     import mark

from pyTooling.Platform import CurrentPlatform
from pyTooling.Testing  import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class HelperFunctions(Testcase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_VersionInformation(self) -> None:
		from pyTooling.Packaging import extractVersionInformation

		versionInformation = extractVersionInformation(Path("pyTooling/Common/__init__.py"))
		self.assertIsInstance(versionInformation.Keywords, list)
		self.assertEqual(43, len(versionInformation.Keywords))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeTXT(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		readme = loadReadmeFile(Path("tests/pyPackage/README.txt"))
		self.assertIn("1. pyPackage", readme.Content)
		self.assertEqual("text/plain", readme.MimeType)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeMD(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		readme = loadReadmeFile(Path("tests/pyPackage/README.md"))
		self.assertIn("# pyPackage", readme.Content)
		self.assertEqual("text/markdown", readme.MimeType)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeReST(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		readme = loadReadmeFile(Path("tests/pyPackage/README.rst"))
		self.assertIn("pyPackage", readme.Content)
		self.assertIn("#########", readme.Content)
		self.assertEqual("text/x-rst", readme.MimeType)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadReadmeOther(self) -> None:
		from pyTooling.Packaging import loadReadmeFile

		with self.assertRaises(ValueError):
			_ = loadReadmeFile(Path("tests/pyPackage/README.ascii"))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirements(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("doc/requirements.txt"))
		self.assertEqual(12, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsGit(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.Git.txt"))
		self.assertEqual(2, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsRemoteZIP(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.HTTPS-ZIP.txt"))
		self.assertEqual(1, len(requirements))

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_loadRequirementsRecursive(self) -> None:
		from pyTooling.Packaging import loadRequirementsFile

		requirements = loadRequirementsFile(Path("tests/data/Requirements/requirements.txt"), debug=True)
		self.assertEqual(5, len(requirements))


class VersionInformation(Testcase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
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


class DescribePackage(Testcase):
	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_PythonPackage(self) -> None:
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

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_PythonPackageFromGitHub(self) -> None:
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


class EntryPoints(Testcase):
	"""A package advertises what it offers; the describe-functions know which group it is declared in."""

	def test_APackageMayAdvertiseNothing(self) -> None:
		from pyTooling.Packaging import _collectEntryPoints

		self.assertIsNone(_collectEntryPoints(None, None, None))
		self.assertIsNone(_collectEntryPoints({}, {}, {}), "An empty mapping declares nothing.")

	def test_ConsoleScripts(self) -> None:
		from pyTooling.Packaging import _collectEntryPoints

		self.assertEqual(
			{"console_scripts": ["prog = myPackage.CLI:main"]},
			_collectEntryPoints({"prog": "myPackage.CLI:main"}, None, None)
		)

	def test_GuiScripts(self) -> None:
		from pyTooling.Packaging import _collectEntryPoints

		self.assertEqual(
			{"gui_scripts": ["prog = myPackage.GUI:main"]},
			_collectEntryPoints(None, {"prog": "myPackage.GUI:main"}, None)
		)

	def test_PytestPlugins(self) -> None:
		from pyTooling.Packaging import _collectEntryPoints

		self.assertEqual(
			{"pytest11": ["myPlugin = myPackage.PyTest"]},
			_collectEntryPoints(None, None, {"myPlugin": "myPackage.PyTest"})
		)

	def test_AllThreeAtOnce(self) -> None:
		from pyTooling.Packaging import _collectEntryPoints

		self.assertEqual(
			{
				"console_scripts": ["prog = myPackage.CLI:main"],
				"gui_scripts":     ["prog-gui = myPackage.GUI:main"],
				"pytest11":        ["myPlugin = myPackage.PyTest"],
			},
			_collectEntryPoints(
				{"prog": "myPackage.CLI:main"},
				{"prog-gui": "myPackage.GUI:main"},
				{"myPlugin": "myPackage.PyTest"}
			)
		)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_APytestPluginIsClassified(self) -> None:
		"""Declaring a pytest plugin says so on PyPI too, without the caller repeating it."""

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
			keywords=("Swiss", "Knife"),
			pytestPlugins={"myPlugin": "myPackage.PyTest"}
		)

		self.assertEqual({"pytest11": ["myPlugin = myPackage.PyTest"]}, packageInformation["entry_points"])
		self.assertIn("Framework :: Pytest", packageInformation["classifiers"])

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_WithoutAPluginThereIsNoClassifier(self) -> None:
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

		self.assertNotIn("Framework :: Pytest", packageInformation["classifiers"])
		self.assertNotIn("entry_points", packageInformation)


class LicenseExpression(Testcase):
	"""A package states its license as an SPDX expression, not as a deprecated classifier."""

	@staticmethod
	def _Describe(**kwargs):
		"""
		Describe a minimal package, so a testcase can look at one field of the result.

		:param kwargs: Additional parameters forwarded to :func:`DescribePythonPackage`.
		:returns:      The package description.
		"""
		from pyTooling.Packaging import DescribePythonPackage

		packageName = "pyPackage.Tool"
		packagePath = Path("tests") / Path(packageName)

		return DescribePythonPackage(
			packageName=packageName,
			description="Swiss army knife.",
			projectURL="https://",
			sourceCodeURL="https://",
			documentationURL="https://",
			issueTrackerCodeURL="https://",
			sourceFileWithVersion=packagePath / "__init__.py",
			keywords=("Swiss", "Knife"),
			**kwargs
		)

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_TheLicenseIsAnSPDXExpression(self) -> None:
		self.assertEqual("Apache-2.0", self._Describe()["license"])

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_NoLicenseClassifierIsAdded(self) -> None:
		classifiers = self._Describe()["classifiers"]

		self.assertEqual([], [classifier for classifier in classifiers if classifier.startswith("License ::")])

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_ACallersLicenseClassifierIsReported(self) -> None:
		"""It goes to the setup.py output, where the rest of this function's messages go."""

		output = StringIO()
		with redirect_stdout(output):
			self._Describe(classifiers=("License :: OSI Approved :: MIT License", ))

		printed = output.getvalue()

		self.assertIn("License classifiers are deprecated", printed)
		self.assertIn("License :: OSI Approved :: MIT License", printed)
		self.assertIn("[pyTooling.Packaging]", printed, "It carries the prefix every other message here carries.")

	@mark.xfail(CurrentPlatform.IsMSYS2Environment, reason="Can fail on MSYS2 environment with Python 3.10+.")
	def test_WithoutOneNothingIsReported(self) -> None:
		output = StringIO()
		with redirect_stdout(output):
			self._Describe()

		self.assertNotIn("deprecated", output.getvalue())

	def test_TheLicenseStillOffersItsClassifier(self) -> None:
		"""'License.PythonClassifier' stays - it is public API, and a caller may still need it elsewhere."""

		from pyTooling.Licensing import Apache_2_0_License

		self.assertEqual("License :: OSI Approved :: Apache Software License", Apache_2_0_License.PythonClassifier)

