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
# Python package:     A set of helper functions to describe a Python package for setuptools.
#
# License:
# ============================================================================
# Copyright 2021-2021 Patrick Lehmann - Bötzingen, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#		http://www.apache.org/licenses/LICENSE-2.0
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
A set of helper functions to describe a Python package for setuptools.
"""
from dataclasses  import dataclass
from ast          import parse as ast_parse, iter_child_nodes, Assign, Constant, Name, List as ast_List
from pathlib      import Path
from textwrap import dedent

from setuptools   import (
	setup as setuptools_setup,
	find_packages as setuptools_find_packages,
	find_namespace_packages as setuptools_find_namespace_packages
)
from typing       import List, Iterable, Dict, Sequence

try:
	from pyTooling.Decorators import export
	from pyTooling.Licensing  import License, Apache_2_0_License
except ModuleNotFoundError:
	print("[pyTooling.Packaging] Could not import from 'pyTooling.*'!")

	try:
		from Decorators import export
		from Licensing import License, Apache_2_0_License
	except ModuleNotFoundError as ex:
		print("[pyTooling.Packaging] Could not import from 'Decorators' or 'Licensing' directly!")
		raise ex


@export
@dataclass
class Readme:
	"""Encapsulates the READMEs file content and MIME type."""
	Content:  str
	MimeType: str


@export
def loadReadmeFile(readmeFile: Path) -> Readme:
	"""
	Read the README file (e.g. in Markdown format), so it can be used as long description for the package.

	Supported formats:

	  * Markdown (``*.md``)

	:param readmeFile: Path to the `README` file as an instance of :class:`Path`.
	:return:           A tuple containing the file content and the MIME type.
	"""
	if readmeFile.suffix == ".md":
		with readmeFile.open("r") as file:
			return Readme(
				Content=file.read(),
				MimeType="text/markdown"
			)
	else:
		raise ValueError("Unsupported README format.")


@export
def loadRequirementsFile(requirementsFile: Path, indent: int = 0, debug: bool = False) -> List[str]:
	"""
	Reads a `requirements.txt` file and extracts all specified dependencies into an array.

	Special dependency entries like Git repository references are translates to match the syntax expected by setuptools.

	:param requirementsFile: Path to the `requirements.txt` file as an instance of :class:`Path`.
	:return:                 A list of dependencies.
	"""

	indentation = "  " * indent
	requirements = []
	with requirementsFile.open("r") as file:
		if debug:
			print(f"[pyTooling.Packaging]{indentation} Extracting requirements from '{requirementsFile}'.")
		for line in file.readlines():
			line = line.strip()
			if line.startswith("#") or line == "":
				continue
			elif line.startswith("-r"):
				# Remove the first word/argument (-r)
				filename = line[2:].lstrip()
				requirements += loadRequirementsFile(requirementsFile.parent / filename, indent + 1, debug)
			elif line.startswith("https"):
				if debug:
					print(f"[pyTooling.Packaging]{indentation} Found URL '{line}'.")

				# Convert 'URL#NAME' to 'NAME @ URL'
				splitItems = line.split("#")
				requirements.append(f"{splitItems[1]} @ {splitItems[0]}")
			else:
				if debug:
					print(f"[pyTooling.Packaging]{indentation} - {line}")

				requirements.append(line)

	return requirements


@export
class VersionInformation:
	"""Encapsulates version information extracted from a Python source file."""
	_author:      str
	_copyright:   str
	_email:       str
	_keywords:    List[str]
	_licenses:    str
	_description: str
	_version:     str

	def __init__(self, author: str, email: str, copyright: str, license: str, version: str, description: str, keywords: List[str]):
		self._author =      author
		self._email =       email
		self._copyright =   copyright
		self._license =     license
		self._version =     version
		self._description = description
		self._keywords =    keywords

	@property
	def Author(self) -> str:
		return self._author

	@property
	def Copyright(self) -> str:
		return self._copyright

	@property
	def Email(self) -> str:
		return self._email

	@property
	def Keywords(self) -> List[str]:
		return self._keywords

	@property
	def Licenses(self) -> str:
		return self._license

	@property
	def Version(self) -> str:
		return self._version


@export
def extractVersionInformation(sourceFile: Path) -> VersionInformation:
	"""
	Extract double underscored variables from a Python source file, so these can be used for single-sourcing information.

	Supported variables:

	  * ``__author__``
	  * ``__copyright__``
	  * ``__email__``
	  * ``__keywords__``
	  * ``__license__``
	  * ``__version__``

	:param sourceFile: Path to a Python source file as an instance of :class:`Path`.
	:return:
	"""
	_author =      None
	_copyright =   None
	_description = ""
	_email =       None
	_keywords =    []
	_license =     None
	_version =     None

	with sourceFile.open("r") as file:
		for item in iter_child_nodes(ast_parse(file.read())):
			if isinstance(item, Assign) and len(item.targets) == 1:
				target = item.targets[0]
				value = item.value
				if isinstance(target, Name) and target.id == "__author__" and isinstance(value, Constant) and isinstance(value.value, str):
					_author = value.value
				if isinstance(target, Name) and target.id == "__copyright__" and isinstance(value, Constant) and isinstance(value.value, str):
					_copyright = value.value
				if isinstance(target, Name) and target.id == "__email__" and isinstance(value, Constant) and isinstance(value.value, str):
					_email = value.value
				if isinstance(target, Name) and target.id == "__keywords__":
					if isinstance(value, Constant) and isinstance(value.value, str):
						raise TypeError(f"Variable '__keywords__' shouldn't be a string.")
					elif isinstance(value, ast_List):
						for const in value.elts:
							if isinstance(const, Constant) and isinstance(const.value, str):
								_keywords.append(const.value)
							else:
								raise TypeError
					else:
						raise TypeError
				if isinstance(target, Name) and target.id == "__license__" and isinstance(value, Constant) and isinstance(value.value, str):
					_license = value.value
				if isinstance(target, Name) and target.id == "__version__" and isinstance(value, Constant) and isinstance(value.value, str):
					_version = value.value

	if _author is None:
		raise AssertionError(f"Could not extract '__author__' from '{sourceFile}'.")
	if _copyright is None:
		raise AssertionError(f"Could not extract '__copyright__' from '{sourceFile}'.")
	if _email is None:
		raise AssertionError(f"Could not extract '__email__' from '{sourceFile}'.")
	if _license is None:
		raise AssertionError(f"Could not extract '__license__' from '{sourceFile}'.")
	if _version is None:
		raise AssertionError(f"Could not extract '__version__' from '{sourceFile}'.")

	return VersionInformation(_author, _email, _copyright, _license, _version, _description, _keywords)


STATUS: Dict[str, str] = {
	"planning":  "1 - Planning",
	"pre-alpha": "2 - Pre-Alpha",
	"alpha":     "3 - Alpha",
	"beta":      "4 - Beta",
	"stable":    "5 - Production/Stable",
	"mature":    "6 - Mature",
	"inactive":  "7 - Inactive"
}

DEFAULT_LICENSE =     Apache_2_0_License
DEFAULT_PY_VERSIONS = ("3.6", "3.7", "3.8", "3.9", "3.10")
DEFAULT_CLASSIFIERS = (
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	)

@export
def DescribePythonPackage(
	packageName: str,
	description: str,
	projectURL: str,
	sourceCodeURL: str,
	documentationURL: str,
	issueTrackerCodeURL: str,
	keywords: str = None,
	license: License = DEFAULT_LICENSE,
	readmeFile: Path = Path("README.md"),
	requirementsFile: Path = Path("requirements.txt"),
	sourceFileWithVersion: Path = Path("__init__.py"),
	classifiers: Iterable[str] = DEFAULT_CLASSIFIERS,
	developmentStatus: str = "stable",
	pythonVersions: Sequence[str] = DEFAULT_PY_VERSIONS,
	consoleScripts: Dict[str, str] = None
) -> None:
	# Read README for upload to PyPI
	readme = loadReadmeFile(readmeFile)

	# Read requirements file and add them to package dependency list (remove duplicates)
	requirements = list(set(loadRequirementsFile(requirementsFile, debug=True)))

	# Read __author__, __email__, __version__ from source file
	versionInformation = extractVersionInformation(sourceFileWithVersion)

	# Scan for packages and source files
	exclude = ["build", "build.*", "dist", "dist.*", "doc", "doc.*", "tests", "tests.*"]
	if "." in packageName:
		packages = setuptools_find_namespace_packages(exclude=exclude)
		if packageName.endswith(".*"):
			packageName = packageName[:-2]
	else:
		packages = setuptools_find_packages(exclude=exclude)

	if keywords is None:
		keywords = versionInformation.Keywords

	# Assemble classifiers
	classifiers = list(classifiers)

	# Translate license to classifier
	classifiers.append(license.PythonClassifier)

	# Translate Python versions to classifiers
	classifiers.append("Programming Language :: Python :: 3 :: Only")
	for v in pythonVersions:
		classifiers.append(f"Programming Language :: Python :: {v}")

	# Translate status to classifier
	try:
		classifiers.append(f"Development Status :: {STATUS[developmentStatus]}")
	except KeyError:
		raise ValueError(f"Unsupported development status '{developmentStatus}'.")

	# Assemble all package information
	parameters = {
		"name": packageName,
		"version": versionInformation.Version,
		"author": versionInformation.Author,
		"author_email": versionInformation.Email,
		"license": license.SPDXIdentifier,
		"description": description,
		"long_description": readme.Content,
		"long_description_content_type": readme.MimeType,
		"url": projectURL,
		"project_urls": {
			'Documentation': documentationURL,
			'Source Code':   sourceCodeURL,
			'Issue Tracker': issueTrackerCodeURL
		},
		"packages": packages,
		"classifiers": classifiers,
		"keywords": keywords,
		"python_requires": f">={pythonVersions[0]}",
	  "install_requires": requirements,
	}

	if consoleScripts is not None:
		scripts = []
		for scriptName, entryPoint in consoleScripts.items():
			scripts.append(f"{scriptName} = {entryPoint}")

		parameters["entry_points"] = {
			"console_scripts": scripts
		}

	setuptools_setup(**parameters)

@export
def DescribePythonPackageHostedOnGitHub(
	packageName: str,
	description: str,
	gitHubNamespace: str,
	gitHubRepository: str = None,
	projectURL: str = None,
	keywords: str = None,
	license: License = DEFAULT_LICENSE,
	readmeFile: Path = Path("README.md"),
	requirementsFile: Path = Path("requirements.txt"),
	sourceFileWithVersion: Path = Path("__init__.py"),
	classifiers: Iterable[str] = DEFAULT_CLASSIFIERS,
	developmentStatus: str = "stable",
	pythonVersions: Sequence[str] = DEFAULT_PY_VERSIONS,
	consoleScripts: Dict[str, str] = None
):
	gitHubRepository = gitHubRepository if gitHubRepository is not None else packageName

	# Derive URLs
	sourceCodeURL = f"https://GitHub.com/{gitHubNamespace}/{gitHubRepository}"
	documentationURL = f"https://{gitHubNamespace}.GitHub.io/{gitHubRepository}"
	issueTrackerCodeURL = f"{sourceCodeURL}/issues"

	projectURL = projectURL if projectURL is not None else sourceCodeURL

	DescribePythonPackage(
		packageName=packageName,
		description=description,
		keywords=keywords,
		projectURL=projectURL,
		sourceCodeURL=sourceCodeURL,
		documentationURL=documentationURL,
		issueTrackerCodeURL=issueTrackerCodeURL,
		license=license,
		readmeFile=readmeFile,
		requirementsFile=requirementsFile,
		sourceFileWithVersion=sourceFileWithVersion,
		classifiers=classifiers,
		developmentStatus=developmentStatus,
		pythonVersions=pythonVersions,
		consoleScripts=consoleScripts
	)