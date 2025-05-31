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
# Copyright 2021-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A set of helper functions to describe a Python package for setuptools.

.. hint:: See :ref:`high-level help <PACKAGING>` for explanations and usage examples.
"""
from ast             import parse as ast_parse, iter_child_nodes, Assign, Constant, Name, List as ast_List
from collections.abc import Sized
from os              import scandir as os_scandir
from pathlib         import Path
from re              import split as re_split
from sys             import version_info
from typing          import List, Iterable, Dict, Sequence, Any, Optional as Nullable, Union, Tuple

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import __version__, getFullyQualifiedName, firstElement
	from pyTooling.Licensing   import License, Apache_2_0_License
except (ImportError, ModuleNotFoundError):                                           # pragma: no cover
	print("[pyTooling.Packaging] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from Exceptions          import ToolingException
		from MetaClasses         import ExtendedType
		from Common              import __version__, getFullyQualifiedName, firstElement
		from Licensing           import License, Apache_2_0_License
	except (ImportError, ModuleNotFoundError) as ex:                                   # pragma: no cover
		print("[pyTooling.Packaging] Could not import directly!")
		raise ex


__all__ = [
	"STATUS", "DEFAULT_LICENSE", "DEFAULT_PY_VERSIONS", "DEFAULT_CLASSIFIERS", "DEFAULT_README", "DEFAULT_REQUIREMENTS",
	"DEFAULT_DOCUMENTATION_REQUIREMENTS", "DEFAULT_TEST_REQUIREMENTS", "DEFAULT_PACKAGING_REQUIREMENTS",
	"DEFAULT_VERSION_FILE"
]


@export
class Readme:
	"""Encapsulates the READMEs file content and MIME type."""

	_content:  str   #: Content of the README file
	_mimeType: str   #: MIME type of the README content

	def __init__(self, content: str, mimeType: str) -> None:
		"""
		Initializes a README file wrapper.

		:param content:  Raw content of the README file.
		:param mimeType: MIME type of the README file.
		"""
		self._content = content
		self._mimeType = mimeType

	@readonly
	def Content(self) -> str:
		"""
		Read-only property to access the README's content.

		:returns: Raw content of the README file.
		"""
		return self._content

	@readonly
	def MimeType(self) -> str:
		"""
		Read-only property to access the README's MIME type.

		:returns: The MIME type of the README file.
		"""
		return self._mimeType


@export
def loadReadmeFile(readmeFile: Path) -> Readme:
	"""
	Read the README file (e.g. in Markdown format), so it can be used as long description for the package.

	Supported formats:

	  * Plain text (``*.txt``)
	  * Markdown (``*.md``)
	  * ReStructured Text (``*.rst``)

	:param readmeFile:         Path to the `README` file as an instance of :class:`Path`.
	:returns:                  A tuple containing the file content and the MIME type.
	:raises TypeError:         If parameter 'readmeFile' is not of type 'Path'.
	:raises ValueError:        If README file has an unsupported format.
	:raises FileNotFoundError: If README file does not exist.
	"""
	if not isinstance(readmeFile, Path):
		ex = TypeError(f"Parameter 'readmeFile' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(readmeFile)}'.")
		raise ex

	if readmeFile.suffix == ".txt":
		mimeType = "text/plain"
	elif readmeFile.suffix == ".md":
		mimeType = "text/markdown"
	elif readmeFile.suffix == ".rst":
		mimeType = "text/x-rst"
	else:                                                               # pragma: no cover
		raise ValueError("Unsupported README format.")

	try:
		with readmeFile.open("r", encoding="utf-8") as file:
			return Readme(
				content=file.read(),
				mimeType=mimeType
			)
	except FileNotFoundError as ex:
		raise FileNotFoundError(f"README file '{readmeFile}' not found in '{Path.cwd()}'.") from ex


@export
def loadRequirementsFile(requirementsFile: Path, indent: int = 0, debug: bool = False) -> List[str]:
	"""
	Reads a `requirements.txt` file (recursively) and extracts all specified dependencies into an array.

	Special dependency entries like Git repository references are translates to match the syntax expected by setuptools.

	.. hint::

	   Duplicates should be removed by converting the result to a :class:`set` and back to a :class:`list`.

	   .. code-block:: Python

	      requirements = list(set(loadRequirementsFile(requirementsFile)))

	:param requirementsFile:   Path to the ``requirements.txt`` file as an instance of :class:`Path`.
	:param debug:              If ``True``, print found dependencies and recursion.
	:returns:                  A list of dependencies.
	:raises TypeError:         If parameter 'requirementsFile' is not of type 'Path'.
	:raises FileNotFoundError: If requirements file does not exist.
	"""
	if not isinstance(requirementsFile, Path):
		ex = TypeError(f"Parameter '{requirementsFile}' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(requirementsFile)}'.")
		raise ex

	def _loadRequirementsFile(requirementsFile: Path, indent: int) -> List[str]:
		"""Recursive variant of :func:`loadRequirementsFile`."""
		requirements = []
		try:
			with requirementsFile.open("r", encoding="utf-8") as file:
				if debug:
					print(f"[pyTooling.Packaging]{'  ' * indent} Extracting requirements from '{requirementsFile}'.")
				for line in file.readlines():
					line = line.strip()
					if line.startswith("#") or line == "":
						continue
					elif line.startswith("-r"):
						# Remove the first word/argument (-r)
						filename = line[2:].lstrip()
						requirements += _loadRequirementsFile(requirementsFile.parent / filename, indent + 1)
					elif line.startswith("https"):
						if debug:
							print(f"[pyTooling.Packaging]{'  ' * indent} Found URL '{line}'.")

						# Convert 'URL#NAME' to 'NAME @ URL'
						splitItems = line.split("#")
						requirements.append(f"{splitItems[1]} @ {splitItems[0]}")
					else:
						if debug:
							print(f"[pyTooling.Packaging]{'  ' * indent} - {line}")

						requirements.append(line)
		except FileNotFoundError as ex:
			raise FileNotFoundError(f"Requirements file '{requirementsFile}' not found in '{Path.cwd()}'.") from ex

		return requirements

	return _loadRequirementsFile(requirementsFile, 0)


@export
class VersionInformation(metaclass=ExtendedType, slots=True):
	"""Encapsulates version information extracted from a Python source file."""

	_author: str          #: Author name(s).
	_copyright: str       #: Copyright information.
	_email: str           #: Author's email address.
	_keywords: List[str]  #: Keywords.
	_license: str         #: License name.
	_description: str     #: Description of the package.
	_version: str         #: Version number.

	def __init__(
		self,
		author: str,
		email: str,
		copyright: str,
		license: str,
		version: str,
		description: str,
		keywords: Iterable[str]
	) -> None:
		"""
		Initializes a Python package (version) information instance.

		:param author:      Author of the Python package.
		:param email:       The author's email address
		:param copyright:   The copyright notice of the Package.
		:param license:     The Python package's license.
		:param version:     The Python package's version.
		:param description: The Python package's short description.
		:param keywords:    The Python package's list of keywords.
		"""
		self._author =      author
		self._email =       email
		self._copyright =   copyright
		self._license =     license
		self._version =     version
		self._description = description
		self._keywords =    [k for k in keywords]

	@readonly
	def Author(self) -> str:
		"""Name(s) of the package author(s)."""
		return self._author

	@readonly
	def Copyright(self) -> str:
		"""Copyright information."""
		return self._copyright

	@readonly
	def Description(self) -> str:
		"""Package description text."""
		return self._description

	@readonly
	def Email(self) -> str:
		"""Email address of the author."""
		return self._email

	@readonly
	def Keywords(self) -> List[str]:
		"""List of keywords."""
		return self._keywords

	@readonly
	def License(self) -> str:
		"""License name."""
		return self._license

	@readonly
	def Version(self) -> str:
		"""Version number."""
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
	:returns:          An instance of :class:`VersionInformation` with gathered variable contents.
	:raises TypeError: If parameter 'sourceFile' is not of type :class:`~pathlib.Path`.

	"""
	if not isinstance(sourceFile, Path):
		ex = TypeError(f"Parameter 'sourceFile' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(sourceFile)}'.")
		raise ex

	_author =      None
	_copyright =   None
	_description = ""
	_email =       None
	_keywords =    []
	_license =     None
	_version =     None

	try:
		with sourceFile.open("r", encoding="utf-8") as file:
			content = file.read()
	except FileNotFoundError as ex:
		raise FileNotFoundError

	try:
		ast = ast_parse(content)
	except Exception as ex:                                                          # pragma: no cover
		raise ToolingException(f"Internal error when parsing '{sourceFile}'.") from ex

	for item in iter_child_nodes(ast):
		if isinstance(item, Assign) and len(item.targets) == 1:
			target = item.targets[0]
			value = item.value
			if isinstance(target, Name) and target.id == "__author__":
				if isinstance(value, Constant) and isinstance(value.value, str):
					_author = value.value
			if isinstance(target, Name) and target.id == "__copyright__":
				if isinstance(value, Constant) and isinstance(value.value, str):
					_copyright = value.value
			if isinstance(target, Name) and target.id == "__email__":
				if isinstance(value, Constant) and isinstance(value.value, str):
					_email = value.value
			if isinstance(target, Name) and target.id == "__keywords__":
				if isinstance(value, Constant) and isinstance(value.value, str):           # pragma: no cover
					raise TypeError(f"Variable '__keywords__' should be a list of strings.")
				elif isinstance(value, ast_List):
					for const in value.elts:
						if isinstance(const, Constant) and isinstance(const.value, str):
							_keywords.append(const.value)
						else:                                                                  # pragma: no cover
							raise TypeError(f"List elements in '__keywords__' should be strings.")
				else:                                                                      # pragma: no cover
					raise TypeError(f"Used unsupported type for variable '__keywords__'.")
			if isinstance(target, Name) and target.id == "__license__":
				if isinstance(value, Constant) and isinstance(value.value, str):
					_license = value.value
			if isinstance(target, Name) and target.id == "__version__":
				if isinstance(value, Constant) and isinstance(value.value, str):
					_version = value.value

	if _author is None:
		raise AssertionError(f"Could not extract '__author__' from '{sourceFile}'.")     # pragma: no cover
	if _copyright is None:
		raise AssertionError(f"Could not extract '__copyright__' from '{sourceFile}'.")  # pragma: no cover
	if _email is None:
		raise AssertionError(f"Could not extract '__email__' from '{sourceFile}'.")      # pragma: no cover
	if _license is None:
		raise AssertionError(f"Could not extract '__license__' from '{sourceFile}'.")    # pragma: no cover
	if _version is None:
		raise AssertionError(f"Could not extract '__version__' from '{sourceFile}'.")    # pragma: no cover

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
"""
A dictionary of supported development status values.

The mapping's value will be appended to ``Development Status :: `` to form a package classifier.

1. Planning
2. Pre-Alpha
3. Alpha
4. Beta
5. Production/Stable
6. Mature
7. Inactive

.. seealso::

   `Python package classifiers <https://pypi.org/classifiers/>`__
"""

DEFAULT_LICENSE = Apache_2_0_License
"""
Default license (Apache License, 2.0) used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``license`` is not assigned.
"""

DEFAULT_PY_VERSIONS = ("3.9", "3.10", "3.11", "3.12", "3.13")
"""
A tuple of supported CPython versions used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``pythonVersions`` is not assigned.

.. seealso::

   `Status of Python versions <https://devguide.python.org/versions/>`__
"""

DEFAULT_CLASSIFIERS = (
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Topic :: Utilities"
	)
"""
A list of Python package classifiers used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``classifiers`` is not assigned.

.. seealso::

   `Python package classifiers <https://pypi.org/classifiers/>`__
"""

DEFAULT_README = Path("README.md")
"""
Path to the README file used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``readmeFile`` is not assigned.
"""

DEFAULT_REQUIREMENTS = Path("requirements.txt")
"""
Path to the requirements file used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``requirementsFile`` is not assigned.
"""

DEFAULT_DOCUMENTATION_REQUIREMENTS = Path("doc/requirements.txt")
"""
Path to the README requirements file used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``documentationRequirementsFile`` is not assigned.
"""

DEFAULT_TEST_REQUIREMENTS = Path("tests/requirements.txt")
"""
Path to the README requirements file used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``unittestRequirementsFile`` is not assigned.
"""

DEFAULT_PACKAGING_REQUIREMENTS = Path("build/requirements.txt")
"""
Path to the package requirements file used by :func:`DescribePythonPackage` and :func:`DescribePythonPackageHostedOnGitHub`
if parameter ``packagingRequirementsFile`` is not assigned.
"""

DEFAULT_VERSION_FILE = Path("__init__.py")


@export
def DescribePythonPackage(
	packageName: str,
	description: str,
	projectURL: str,
	sourceCodeURL: str,
	documentationURL: str,
	issueTrackerCodeURL: str,
	keywords: Iterable[str] = None,
	license: License = DEFAULT_LICENSE,
	readmeFile: Path = DEFAULT_README,
	requirementsFile: Path = DEFAULT_REQUIREMENTS,
	documentationRequirementsFile: Path = DEFAULT_DOCUMENTATION_REQUIREMENTS,
	unittestRequirementsFile: Path = DEFAULT_TEST_REQUIREMENTS,
	packagingRequirementsFile: Path = DEFAULT_PACKAGING_REQUIREMENTS,
	additionalRequirements: Dict[str, List[str]] = None,
	sourceFileWithVersion: Nullable[Path] = DEFAULT_VERSION_FILE,
	classifiers: Iterable[str] = DEFAULT_CLASSIFIERS,
	developmentStatus: str = "stable",
	pythonVersions: Sequence[str] = DEFAULT_PY_VERSIONS,
	consoleScripts: Dict[str, str] = None,
	dataFiles: Dict[str, List[str]] = None,
	debug: bool = False
) -> Dict[str, Any]:
	"""
	Helper function to describe a Python package.

	.. hint::

	   Some information will be gathered automatically from well-known files.

	   Examples: ``README.md``, ``requirements.txt``, ``__init__.py``

	.. topic:: Handling of namespace packages

	   If parameter ``packageName`` contains a dot, a namespace package is assumed. Then
	   :func:`setuptools.find_namespace_packages` is used to discover package files. |br|
	   Otherwise, the package is considered a normal package and :func:`setuptools.find_packages` is used.

	   In both cases, the following packages (directories) are excluded from search:

	   * ``build``, ``build.*``
	   * ``dist``, ``dist.*``
	   * ``doc``, ``doc.*``
	   * ``tests``, ``tests.*``

	.. topic:: Handling of minimal Python version

	   The minimal required Python version is selected from parameter ``pythonVersions``.

	.. topic:: Handling of dunder variables

	   A Python source file specified by parameter ``sourceFileWithVersion`` will be analyzed with Pythons parser and the
	   resulting AST will be searched for the following dunder variables:

	   * ``__author__``: :class:`str`
	   * ``__copyright__``: :class:`str`
	   * ``__email__``: :class:`str`
	   * ``__keywords__``: :class:`typing.Iterable`[:class:`str`]
	   * ``__license__``: :class:`str`
	   * ``__version__``: :class:`str`

	The gathered information be used to add further mappings in the result dictionary.

	.. topic:: Handling of package classifiers

	   To reduce redundantly provided parameters to this function (e.g. supported ``pythonVersions``), only additional
	   classifiers should be provided via parameter ``classifiers``. The supported Python versions will be implicitly
	   converted to package classifiers, so no need to specify them in parameter ``classifiers``.

	   The following classifiers are implicitly handled:

	   license
	     The license specified by parameter ``license`` is translated into a classifier. |br|
	     See also :meth:`pyTooling.Licensing.License.PythonClassifier`

	   Python versions
	     Always add ``Programming Language :: Python :: 3 :: Only``. |br|
	     For each value in ``pythonVersions``, one ``Programming Language :: Python :: Major.Minor`` is added.

	   Development status
	     The development status specified by parameter ``developmentStatus`` is translated to a classifier and added.

	.. topic:: Handling of extra requirements

	   If additional requirement files are provided, e.g. requirements to build the documentation, then *extra*
	   requirements are defined. These can be installed via ``pip install packageName[extraName]``. If so, an extra called
	   ``all`` is added, so developers can install all dependencies needed for package development.

	   ``doc``
	     If parameter ``documentationRequirementsFile`` is present, an extra requirements called ``doc`` will be defined.
	   ``test``
	     If parameter ``unittestRequirementsFile`` is present, an extra requirements called ``test`` will be defined.
	   ``build``
	     If parameter ``packagingRequirementsFile`` is present, an extra requirements called ``build`` will be defined.
	   User-defined
	     If parameter ``additionalRequirements`` is present, an extra requirements for every mapping entry in the
	     dictionary will be added.
	   ``all``
	     If any of the above was added, an additional extra requirement called ``all`` will be added, summarizing all
	     extra requirements.

	.. topic:: Handling of keywords

	   If parameter ``keywords`` is not specified, the dunder variable ``__keywords__`` from ``sourceFileWithVersion``
	   will be used. Otherwise, the content of the parameter, if not None or empty.

	:param packageName:                   Name of the Python package.
	:param description:                   Short description of the package. The long description will be read from README file.
	:param projectURL:                    URL to the Python project.
	:param sourceCodeURL:                 URL to the Python source code.
	:param documentationURL:              URL to the package's documentation.
	:param issueTrackerCodeURL:           URL to the projects issue tracker (ticket system).
	:param keywords:                      A list of keywords.
	:param license:                       The package's license. (Default: ``Apache License, 2.0``, see :const:`DEFAULT_LICENSE`)
	:param readmeFile:                    The path to the README file. (Default: ``README.md``, see :const:`DEFAULT_README`)
	:param requirementsFile:              The path to the project's requirements file. (Default: ``requirements.txt``, see :const:`DEFAULT_REQUIREMENTS`)
	:param documentationRequirementsFile: The path to the project's requirements file for documentation. (Default: ``doc/requirements.txt``, see :const:`DEFAULT_DOCUMENTATION_REQUIREMENTS`)
	:param unittestRequirementsFile:      The path to the project's requirements file for unit tests. (Default: ``tests/requirements.txt``, see :const:`DEFAULT_TEST_REQUIREMENTS`)
	:param packagingRequirementsFile:     The path to the project's requirements file for packaging. (Default: ``build/requirements.txt``, see :const:`DEFAULT_PACKAGING_REQUIREMENTS`)
	:param additionalRequirements:        A dictionary of a lists with additional requirements. (default: None)
	:param sourceFileWithVersion:         The path to the project's source file containing dunder variables like ``__version__``. (Default: ``__init__.py``, see :const:`DEFAULT_VERSION_FILE`)
	:param classifiers:                   A list of package classifiers. (Default: 3 classifiers, see :const:`DEFAULT_CLASSIFIERS`)
	:param developmentStatus:             Development status of the package. (Default: stable, see :const:`STATUS` for supported status values)
	:param pythonVersions:                A list of supported Python 3 version. (Default: all currently maintained CPython versions, see :const:`DEFAULT_PY_VERSIONS`)
	:param consoleScripts:                A dictionary mapping command line names to entry points. (Default: None)
	:param dataFiles:                     A dictionary mapping package names to lists of additional data files.
	:param debug:                         Enable extended outputs for debugging.
	:returns:                             A dictionary suitable for :func:`setuptools.setup`.
	:raises ToolingException:             If package 'setuptools' is not available.
	:raises TypeError:                    If parameter 'readmeFile' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If README file doesn't exist.
	:raises TypeError:                    If parameter 'requirementsFile' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If requirements file doesn't exist.
	:raises TypeError:                    If parameter 'documentationRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'unittestRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'packagingRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'sourceFileWithVersion' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If package file with dunder variables doesn't exist.
	:raises TypeError:                    If parameter 'license' is not of type :class:`~pyTooling.Licensing.License`.
	:raises ValueError:                   If developmentStatus uses an unsupported value. (See :const:`STATUS`)
	:raises ValueError:                   If the content type of the README file is not supported. (See :func:`loadReadmeFile`)
	:raises FileNotFoundError:            If the README file doesn't exist. (See :func:`loadReadmeFile`)
	:raises FileNotFoundError:            If the requirements file doesn't exist. (See :func:`loadRequirementsFile`)
	"""
	try:
		from setuptools import find_packages, find_namespace_packages
	except ImportError as ex:
		raise ToolingException(f"Optional dependency 'setuptools' is not available.") from ex

	print(f"[pyTooling.Packaging] Python: {version_info.major}.{version_info.minor}.{version_info.micro}, pyTooling: {__version__}")

	# Read README for upload to PyPI
	if not isinstance(readmeFile, Path):
		ex = TypeError(f"Parameter 'readmeFile' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(readmeFile)}'.")
		raise ex
	elif not readmeFile.exists():
		raise FileNotFoundError(f"README file '{readmeFile}' not found in '{Path.cwd()}'.")
	else:
		readme = loadReadmeFile(readmeFile)

	# Read requirements file and add them to package dependency list (remove duplicates)
	if not isinstance(requirementsFile, Path):
		ex = TypeError(f"Parameter 'requirementsFile' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(requirementsFile)}'.")
		raise ex
	elif not requirementsFile.exists():
		raise FileNotFoundError(f"Requirements file '{requirementsFile}' not found in '{Path.cwd()}'.")
	else:
		requirements = list(set(loadRequirementsFile(requirementsFile, debug=debug)))

	extraRequirements: Dict[str, List[str]] = {}
	if documentationRequirementsFile is not None:
		if not isinstance(documentationRequirementsFile, Path):
			ex = TypeError(f"Parameter 'documentationRequirementsFile' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(documentationRequirementsFile)}'.")
			raise ex
		elif not documentationRequirementsFile.exists():
			if debug:
				print(f"[pyTooling.Packaging] Documentation requirements file '{documentationRequirementsFile}' not found in '{Path.cwd()}'.")
				print( "[pyTooling.Packaging]   No section added to 'extraRequirements'.")
		# raise FileNotFoundError(f"Documentation requirements file '{documentationRequirementsFile}' not found in '{Path.cwd()}'.")
		else:
			extraRequirements["doc"] = list(set(loadRequirementsFile(documentationRequirementsFile, debug=debug)))

	if unittestRequirementsFile is not None:
		if not isinstance(unittestRequirementsFile, Path):
			ex = TypeError(f"Parameter 'unittestRequirementsFile' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(unittestRequirementsFile)}'.")
			raise ex
		elif not unittestRequirementsFile.exists():
			if debug:
				print(f"[pyTooling.Packaging] Unit testing requirements file '{unittestRequirementsFile}' not found in '{Path.cwd()}'.")
				print( "[pyTooling.Packaging]   No section added to 'extraRequirements'.")
		# raise FileNotFoundError(f"Unit testing requirements file '{unittestRequirementsFile}' not found in '{Path.cwd()}'.")
		else:
			extraRequirements["test"] = list(set(loadRequirementsFile(unittestRequirementsFile, debug=debug)))

	if packagingRequirementsFile is not None:
		if not isinstance(packagingRequirementsFile, Path):
			ex = TypeError(f"Parameter 'packagingRequirementsFile' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(packagingRequirementsFile)}'.")
			raise ex
		elif not packagingRequirementsFile.exists():
			if debug:
				print(f"[pyTooling.Packaging] Packaging requirements file '{packagingRequirementsFile}' not found in '{Path.cwd()}'.")
				print( "[pyTooling.Packaging]   No section added to 'extraRequirements'.")
		# raise FileNotFoundError(f"Packaging requirements file '{packagingRequirementsFile}' not found in '{Path.cwd()}'.")
		else:
			extraRequirements["build"] = list(set(loadRequirementsFile(packagingRequirementsFile, debug=debug)))

	if additionalRequirements is not None:
		for key, value in additionalRequirements.items():
			extraRequirements[key] = value

	if len(extraRequirements) > 0:
		extraRequirements["all"] = list(set([dep for deps in extraRequirements.values() for dep in deps]))

	# Read __author__, __email__, __version__ from source file
	if not isinstance(sourceFileWithVersion, Path):
		ex = TypeError(f"Parameter 'sourceFileWithVersion' is not of type 'Path'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(sourceFileWithVersion)}'.")
		raise ex
	elif not sourceFileWithVersion.exists():
		raise FileNotFoundError(f"Package file '{sourceFileWithVersion}' with dunder variables not found in '{Path.cwd()}'.")
	else:
		versionInformation = extractVersionInformation(sourceFileWithVersion)

	# Scan for packages and source files
	if debug:
		print(f"[pyTooling.Packaging] Exclude list for find_(namespace_)packages:")
	exclude = []
	rootNamespace = firstElement(packageName.split("."))
	for dirName in (dirItem.name for dirItem in os_scandir(Path.cwd()) if dirItem.is_dir() and "." not in dirItem.name and dirItem.name != rootNamespace):
		exclude.append(f"{dirName}")
		exclude.append(f"{dirName}.*")
		if debug:
			print(f"[pyTooling.Packaging] - {dirName}, {dirName}.*")

	if "." in packageName:
		exclude.append(rootNamespace)
		packages = find_namespace_packages(exclude=exclude)
		if packageName.endswith(".*"):
			packageName = packageName[:-2]
	else:
		packages = find_packages(exclude=exclude)

	if debug:
		print("[pyTooling.Packaging] Found packages:")
		for package in packages:
			print(f"[pyTooling.Packaging] - {package}")

	if keywords is None or isinstance(keywords, Sized) and len(keywords) == 0:
		keywords = versionInformation.Keywords

	# Assemble classifiers
	classifiers = list(classifiers)

	# Translate license to classifier
	if not isinstance(license, License):
		ex = TypeError(f"Parameter 'license' is not of type 'License'.")
		if version_info >= (3, 11):  # pragma: no cover
			ex.add_note(f"Got type '{getFullyQualifiedName(readmeFile)}'.")
		raise ex
	classifiers.append(license.PythonClassifier)

	def _naturalSorting(array: Iterable[str]) -> List[str]:
		"""A simple natural sorting implementation."""
		# See http://nedbatchelder.com/blog/200712/human_sorting.html
		def _toInt(text: str) -> Union[str, int]:
			"""Try to convert a :class:`str` to :class:`int` if possible, otherwise preserve the string."""
			return int(text) if text.isdigit() else text

		def _createKey(text: str) -> Tuple[Union[str, float], ...]:
			"""
			Split the text into a tuple of multiple :class:`str` and :class:`int` fields, so embedded numbers can be sorted by
			their value.
			"""
			return tuple(_toInt(part) for part in re_split(r"(\d+)", text))

		sortedArray = list(array)
		sortedArray.sort(key=_createKey)
		return sortedArray

	pythonVersions = _naturalSorting(pythonVersions)

	# Translate Python versions to classifiers
	classifiers.append("Programming Language :: Python :: 3 :: Only")
	for v in pythonVersions:
		classifiers.append(f"Programming Language :: Python :: {v}")

	# Translate status to classifier
	try:
		classifiers.append(f"Development Status :: {STATUS[developmentStatus.lower()]}")
	except KeyError:                                                                   # pragma: no cover
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

	if len(extraRequirements) > 0:
		parameters["extras_require"] = extraRequirements

	if consoleScripts is not None:
		scripts = []
		for scriptName, entryPoint in consoleScripts.items():
			scripts.append(f"{scriptName} = {entryPoint}")

		parameters["entry_points"] = {
			"console_scripts": scripts
		}

	if dataFiles:
		parameters["package_data"] = dataFiles

	return parameters


@export
def DescribePythonPackageHostedOnGitHub(
	packageName: str,
	description: str,
	gitHubNamespace: str,
	gitHubRepository: str = None,
	projectURL: str = None,
	keywords: Iterable[str] = None,
	license: License = DEFAULT_LICENSE,
	readmeFile: Path = DEFAULT_README,
	requirementsFile: Path = DEFAULT_REQUIREMENTS,
	documentationRequirementsFile: Path = DEFAULT_DOCUMENTATION_REQUIREMENTS,
	unittestRequirementsFile: Path = DEFAULT_TEST_REQUIREMENTS,
	packagingRequirementsFile: Path = DEFAULT_PACKAGING_REQUIREMENTS,
	additionalRequirements: Dict[str, List[str]] = None,
	sourceFileWithVersion: Path = DEFAULT_VERSION_FILE,
	classifiers: Iterable[str] = DEFAULT_CLASSIFIERS,
	developmentStatus: str = "stable",
	pythonVersions: Sequence[str] = DEFAULT_PY_VERSIONS,
	consoleScripts: Dict[str, str] = None,
	dataFiles: Dict[str, List[str]] = None,
	debug: bool = False
) -> Dict[str, Any]:
	"""
	Helper function to describe a Python package when the source code is hosted on GitHub.

	This is a wrapper for :func:`DescribePythonPackage`, because some parameters can be simplified by knowing the GitHub
	namespace and repository name: issue tracker URL, source code URL, ...

	:param packageName:                   Name of the Python package.
	:param description:                   Short description of the package. The long description will be read from README file.
	:param gitHubNamespace:               Name of the GitHub namespace (organization or user).
	:param gitHubRepository:              Name of the GitHub repository.
	:param projectURL:                    URL to the Python project.
	:param keywords:                      A list of keywords.
	:param license:                       The package's license. (Default: ``Apache License, 2.0``, see :const:`DEFAULT_LICENSE`)
	:param readmeFile:                    The path to the README file. (Default: ``README.md``, see :const:`DEFAULT_README`)
	:param requirementsFile:              The path to the project's requirements file. (Default: ``requirements.txt``, see :const:`DEFAULT_REQUIREMENTS`)
	:param documentationRequirementsFile: The path to the project's requirements file for documentation. (Default: ``doc/requirements.txt``, see :const:`DEFAULT_DOCUMENTATION_REQUIREMENTS`)
	:param unittestRequirementsFile:      The path to the project's requirements file for unit tests. (Default: ``tests/requirements.txt``, see :const:`DEFAULT_TEST_REQUIREMENTS`)
	:param packagingRequirementsFile:     The path to the project's requirements file for packaging. (Default: ``build/requirements.txt``, see :const:`DEFAULT_PACKAGING_REQUIREMENTS`)
	:param additionalRequirements:        A dictionary of a lists with additional requirements. (default: None)
	:param sourceFileWithVersion:         The path to the project's source file containing dunder variables like ``__version__``. (Default: ``__init__.py``, see :const:`DEFAULT_VERSION_FILE`)
	:param classifiers:                   A list of package classifiers. (Default: 3 classifiers, see :const:`DEFAULT_CLASSIFIERS`)
	:param developmentStatus:             Development status of the package. (Default: stable, see :const:`STATUS` for supported status values)
	:param pythonVersions:                A list of supported Python 3 version. (Default: all currently maintained CPython versions, see :const:`DEFAULT_PY_VERSIONS`)
	:param consoleScripts:                A dictionary mapping command line names to entry points. (Default: None)
	:param dataFiles:                     A dictionary mapping package names to lists of additional data files.
	:param debug:                         Enable extended outputs for debugging.
	:returns:                             A dictionary suitable for :func:`setuptools.setup`.
	:raises ToolingException:             If package 'setuptools' is not available.
	:raises TypeError:                    If parameter 'readmeFile' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If README file doesn't exist.
	:raises TypeError:                    If parameter 'requirementsFile' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If requirements file doesn't exist.
	:raises TypeError:                    If parameter 'documentationRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'unittestRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'packagingRequirementsFile' is not of type :class:`~pathlib.Path`.
	:raises TypeError:                    If parameter 'sourceFileWithVersion' is not of type :class:`~pathlib.Path`.
	:raises FileNotFoundError:            If package file with dunder variables doesn't exist.
	:raises TypeError:                    If parameter 'license' is not of type :class:`~pyTooling.Licensing.License`.
	:raises ValueError:                   If developmentStatus uses an unsupported value. (See :const:`STATUS`)
	:raises ValueError:                   If the content type of the README file is not supported. (See :func:`loadReadmeFile`)
	:raises FileNotFoundError:            If the README file doesn't exist. (See :func:`loadReadmeFile`)
	:raises FileNotFoundError:            If the requirements file doesn't exist. (See :func:`loadRequirementsFile`)
	"""
	if gitHubRepository is None:
		# Assign GitHub repository name without '.*', if derived from Python package name.
		if packageName.endswith(".*"):
			gitHubRepository = packageName[:-2]
		else:
			gitHubRepository = packageName

	# Derive URLs
	sourceCodeURL = f"https://GitHub.com/{gitHubNamespace}/{gitHubRepository}"
	documentationURL = f"https://{gitHubNamespace}.GitHub.io/{gitHubRepository}"
	issueTrackerCodeURL = f"{sourceCodeURL}/issues"

	projectURL = projectURL if projectURL is not None else sourceCodeURL

	return DescribePythonPackage(
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
		documentationRequirementsFile=documentationRequirementsFile,
		unittestRequirementsFile=unittestRequirementsFile,
		packagingRequirementsFile=packagingRequirementsFile,
		additionalRequirements=additionalRequirements,
		sourceFileWithVersion=sourceFileWithVersion,
		classifiers=classifiers,
		developmentStatus=developmentStatus,
		pythonVersions=pythonVersions,
		consoleScripts=consoleScripts,
		dataFiles=dataFiles,
		debug=debug,
	)
