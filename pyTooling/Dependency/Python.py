# ==================================================================================================================== #
#             _____           _ _               ____                            _                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___ _ __   ___ _ __   __| | ___ _ __   ___ _   _                #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ '_ \ / _ \ '_ \ / _` |/ _ \ '_ \ / __| | | |               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ |_) |  __/ | | | (_| |  __/ | | | (__| |_| |               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___| .__/ \___|_| |_|\__,_|\___|_| |_|\___|\__, |               #
# |_|    |___/                          |___/             |_|                                     |___/                #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Implementation of package dependencies.

.. hint::

   See :ref:`high-level help <DEPENDENCIES>` for explanations and usage examples.
"""
from __future__           import annotations

from asyncio              import run as asyncio_run, gather as asyncio_gather
from datetime             import date, datetime
from enum                 import IntEnum
from functools            import wraps, update_wrapper
from pathlib              import Path
from re                   import compile as re_compile, Pattern
from threading            import RLock
from typing               import Any, ClassVar, Optional as Nullable, Union, Iterable, Iterator, Mapping, Self

from pyTooling.Configuration import Dictionary
from pyTooling.Exceptions import MissingDependencyError

try:
	from aiohttp import ClientSession
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="aiohttp", extra="pypi") from ex

try:
	from packaging.requirements import InvalidRequirement, Requirement
	from packaging.utils        import canonicalize_name
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="packaging", extra="pypi") from ex

try:
	from requests import Session, HTTPError
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="requests", extra="pypi") from ex

from pyTooling.Decorators      import export, readonly
from pyTooling.MetaClasses     import ExtendedType, abstractmethod
from pyTooling.Common          import getFullyQualifiedName, firstValue
from pyTooling.Dependency      import Package, PackageStorage, PackageVersion, PackageDependencyGraph
from pyTooling.Dependency      import BrokenRequirementWarning, DependencyError, NoSessionAvailableError
from pyTooling.Dependency      import ProjectNotFoundError
from pyTooling.Dependency      import ReleaseDetailsWarning, ReleaseNotFoundError, UnknownLicenseWarning
from pyTooling.Licensing       import LicenseExpression, LicenseExpressionError, LICENSES_BY_CLASSIFIER
from pyTooling.Licensing       import LicenseAbsence, ProprietaryLicense, UnknownLicense
from pyTooling.Warning         import WarningCollector
from pyTooling.GenericPath.URL import URL
from pyTooling.Versioning      import Parts, PythonVersion, PythonVersionExpression, SemanticVersion


#: Longest prefix of a free-text ``license`` field quoted in a warning note, so a full license text doesn't flood it.
_LICENSE_NOTE_LENGTH = 64

#: PyPI's classifier for a license that isn't open source. SPDX can't name one, so it becomes a
#: :class:`~pyTooling.Licensing.ProprietaryLicense` rather than an expression to parse.
_PROPRIETARY_CLASSIFIER = "License :: Other/Proprietary License"


#: Aliases matched against the free-text keys of ``project_urls``, lower-cased, most specific first.
_REPOSITORY_URL_ALIASES    = ("source code", "source", "code", "repository", "github", "gitlab")
_DOCUMENTATION_URL_ALIASES = ("documentation", "docs", "read the docs")
_ISSUE_TRACKER_URL_ALIASES = ("bug tracker", "issue tracker", "issues", "bug reports", "tracker")
_PROJECT_URL_ALIASES       = ("homepage", "home page", "home")
_CHANGELOG_URL_ALIASES     = ("changelog", "changes", "release notes", "whatsnew", "what's new")

#: Pattern of an ``extra == "<name>"`` comparison in a requirement's marker.
_EXTRA_MARKER = re_compile(r'''extra\s*==\s*["']([^"']+)["']''')


@export
class RequirementsFile(metaclass=ExtendedType, slots=True):
	"""
	A ``requirements.txt`` file, together with the files it includes.

	A ``-r other.txt`` line includes another file, and the tree of those includes is kept rather than flattened:
	``tests/requirements.txt`` is nothing but four ``-r`` lines, so a flattened list would say nothing about which of
	them a package came from - which is exactly what a table per entrypoint has to show.

	A file including itself, directly or through a cycle, is read once.
	"""

	_path:         Path                 #: Path of this requirements file.
	_requirements: list[Requirement]    #: Requirements stated in this file, in the order they are written.
	_includes:     list[RequirementsFile]  #: Files included with ``-r``, in the order they are included.

	def __init__(self, path: Path, _visited: Nullable[set[Path]] = None) -> None:
		"""
		Read a requirements file and the files it includes.

		:param path:               Path of the requirements file to read.
		:param _visited:           Internal, the files already read, so a cycle of includes terminates.
		:raises TypeError:         If parameter 'path' is not of type :class:`~pathlib.Path`.
		:raises FileNotFoundError: If the requirements file doesn't exist.
		"""
		if not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		if not path.exists():
			raise FileNotFoundError(f"Requirements file '{path}' not found.")

		# resolved, so the whole tree spells one file one way: an include is resolved to be compared against
		# 'visited', and on Windows and macOS the path handed in is spelled differently from its resolution
		# ('C:/Users/RUNNER~1/...' vs. 'C:/Users/runneradmin/...', '/var/...' vs. '/private/var/...')
		self._path = path.resolve()
		self._requirements = []
		self._includes = []

		visited = _visited if _visited is not None else set()
		visited.add(self._path)

		for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
			if (line := line.split("#")[0].strip()) == "":
				continue

			if line.startswith("-r"):
				included = (path.parent / line[2:].strip()).resolve()
				if included not in visited:
					self._includes.append(RequirementsFile(included, visited))
				continue

			# '--index-url', '-e' and a bare URL are instructions to the installer, not requirements
			if line.startswith("-") or line.startswith("http"):
				continue

			try:
				self._requirements.append(Requirement(line))
			except InvalidRequirement:
				WarningCollector.Raise(
					BrokenRequirementWarning(f"Requirement '{line}' in '{path}' line {number} can't be parsed.")
				)

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access this file's path (:attr:`_path`).

		:returns: Resolved path of the requirements file.
		"""
		return self._path

	@readonly
	def Requirements(self) -> list[Requirement]:
		"""
		Read-only property to access the requirements stated in this file (:attr:`_requirements`).

		This is what *this* file states; what the files it includes state is reachable through :attr:`Includes`.

		:returns: Requirements stated in this file, in the order they are written.
		"""
		return self._requirements

	@readonly
	def Includes(self) -> list[RequirementsFile]:
		"""
		Read-only property to access the files included with ``-r`` (:attr:`_includes`).

		:returns: Included files, in the order they are included.
		"""
		return self._includes

	def Flatten(self) -> dict[str, Requirement]:
		"""
		Collect the requirements of this file and of every file it includes.

		The nearer statement wins: a requirement stated in this file overrides the same package required by an
		included file, because that is the constraint the entrypoint was written for.

		:returns: Every required package, by its canonical name.
		"""
		requirements: dict[str, Requirement] = {}
		for include in self._includes:
			requirements.update(include.Flatten())

		for requirement in self._requirements:
			requirements[canonicalize_name(requirement.name)] = requirement

		return requirements

	def __len__(self) -> int:
		"""
		Return the number of requirements this file states, not counting the files it includes.

		:returns: Number of requirements stated in this file.
		"""
		return len(self._requirements)

	def __iter__(self) -> Iterator[Requirement]:
		"""
		Iterate the requirements this file states, not the ones it includes.

		:returns: An iterator of this file's requirements.
		"""
		return iter(self._requirements)

	def __str__(self) -> str:
		"""
		Return this file's path and how much it states.

		:returns: A string representation of this requirements file.
		"""
		return f"{self._path}: {len(self._requirements)} requirement(s), {len(self._includes)} include(s)"


@export
class LicenseOverrides(metaclass=ExtendedType, slots=True):
	"""
	Licenses stated by hand, for the packages a package index can't answer for.

	A package index is not a reliable source of license information: roughly half of a typical dependency set
	publishes a PEP 639 ``license_expression``, some state a license *name* where an identifier is expected, and the
	classifier ``License :: OSI Approved :: BSD License`` means either ``BSD-2-Clause`` or ``BSD-3-Clause`` with no
	way to tell which. Those packages are answered here instead of guessed at.

	The file is YAML, and a license may be stated for the package as a whole or per version - a package that
	relicensed has one license before the switch and another after it:

	.. code-block:: yaml

	   version:    "0.1"
	   analysedAt: 2026-09-02

	   packages:
	     colorama:
	       license:    BSD-3-Clause
	       licenseURL: https://GitHub.com/tartley/colorama/blob/master/LICENSE.txt
	       repository: https://GitHub.com/tartley/colorama
	     "igraph >=0.10":
	       license: GPL-2.0-or-later
	     "igraph <0.10":
	       license: GPL-2.0-only
	     "igraph 0.9.10":
	       license: GPL-2.0-only

	``version`` states the structure this file is written for and is checked against
	:attr:`SCHEMA_VERSION`; ``analysedAt`` is the day a human last checked the statements - see :attr:`AnalysedAt`.

	**A key is a package name, optionally followed by a version expression** - the shape a requirement line has.
	The expression is read by :class:`~pyTooling.Versioning.PythonVersionExpression`, so it is the same language a
	requirement file writes, and two of its rules are what make one key form enough:

	* **a bare version is an equality**, so ``igraph 0.9.10`` and ``igraph ==0.9.10`` state the same thing, and
	* **an expression with no constraints matches every version**, so ``igraph`` on its own is the statement for
	  every version rather than a special case.

	Keys are matched in the order the file writes them and the first one a version satisfies wins, so a narrower
	statement goes above the bare name it refines. Asking without a version answers from the bare-name key only.

	A key states a whole entry, so ``licenseURL`` and ``repository`` can differ per version too - a project that
	moved forge between releases has two ``repository`` statements and no special case for it.
	"""

	#: Structure this parser reads. A file states the one it was written for as its ``version`` field, and a file
	#: stating a different one is rejected rather than read on the chance that it still fits.
	SCHEMA_VERSION: ClassVar[SemanticVersion] = SemanticVersion(0, 1)

	#: Splits a key into the package name and whatever follows it. A name stops at the first character an operator
	#: can start with, so ``igraph>=0.10`` splits the same way ``igraph >=0.10`` does.
	_PACKAGE_KEY:  ClassVar[Pattern[str]] = re_compile(r"^\s*(?P<name>[^\s<>=!~]+)\s*(?P<expression>.*?)\s*$")

	_analysedAt:   Nullable[date]                             #: Day the statements were last checked by a human.
	#: License expression per package, by the version expression its key states, in the file's order.
	_licenses:     dict[str, list[tuple[PythonVersionExpression[SemanticVersion], str]]]
	#: URL of the license's text per package, by the version expression its key states, in the file's order.
	_licenseURLs:  dict[str, list[tuple[PythonVersionExpression[SemanticVersion], str]]]
	#: URL of the source repository per package, by the version expression its key states, in the file's order.
	_repositories: dict[str, list[tuple[PythonVersionExpression[SemanticVersion], str]]]

	def __init__(self, analysedAt: Nullable[date] = None) -> None:
		"""
		Initialize an empty set of overrides.

		:param analysedAt: Optional, the day these statements were last checked by a human.
		"""
		self._analysedAt   = analysedAt
		self._licenses     = {}
		self._licenseURLs  = {}
		self._repositories = {}

	@readonly
	def AnalysedAt(self) -> Nullable[date]:
		"""
		Read-only property to access the day these statements were last checked (:attr:`_analysedAt`).

		A package index answers for itself every time it is asked, so what it says is as old as the request. These
		statements are written by hand and are as old as whoever last looked, which nothing else records - so a
		report can mark an entry *overridden*, and *stale* once this date is far enough back.

		:meth:`FromFile` requires it; :meth:`FromDictionary` doesn't, because overrides assembled in code are as old
		as the code.

		:returns: The day of the last analysis, or ``None`` if the overrides were built without one.
		"""
		return self._analysedAt

	@classmethod
	def FromFile(cls, path: Path) -> Self:
		"""
		Read overrides from a YAML file.

		The file is read through :class:`pyTooling.Configuration.YAML.Configuration`, and the ``packages`` node is
		handed to :meth:`FromDictionary` **as it is** - a configuration node answers ``items()`` and ``get()``, so
		there is nothing to convert and no second constructor for the node tree.

		``version`` is **required** and is the first thing checked: it states which structure the file was written
		for, and is compared against :attr:`SCHEMA_VERSION`. **Quote it** - unquoted, YAML reads ``0.1`` as a float,
		and a float loses a trailing zero, so ``1.10`` would arrive as ``1.1``.

		``analysedAt`` is **required** too, and is the day a human last checked these statements. It is an ISO-8601
		date, written either way round - ``analysedAt: 2026-09-02`` reads as YAML's own date type, and
		``analysedAt: "2026-09-02"`` as a string. A configuration hands both over in the same ISO-8601 spelling.

		:param path:                    Path of the YAML file to read.
		:returns:                       The overrides the file states.
		:raises MissingDependencyError: If ``ruamel.yaml`` isn't installed.
		:raises FileNotFoundError:      If the file doesn't exist.
		:raises ConfigurationError:     If the file isn't a YAML document describing a mapping. |br|
		                                An empty file is one, and states no overrides - but it states no
		                                ``version`` either, so it is rejected by the next check.
		:raises DependencyError:        If ``version`` is missing, isn't a version, or isn't
		                                :attr:`SCHEMA_VERSION`.
		:raises DependencyError:        If ``analysedAt`` is missing or isn't an ISO-8601 date.
		:raises DependencyError:        If ``packages`` isn't a mapping. |br|
		                                A file stating no packages is fine and gives no overrides.
		:raises DependencyError:        If a version expression in the file can't be parsed.
		"""
		# Imported here rather than at module level, so a missing 'ruamel.yaml' is reported when the overrides are
		# read instead of when 'pyTooling.Dependency.Python' is imported.
		from pyTooling.Configuration.YAML import Configuration

		# 'Configuration' reports a missing file too, as a 'ConfigurationError' naming the *format*. This says which
		# file of ours is missing, and is what the signature promises, so it stays.
		if not path.exists():
			raise FileNotFoundError(f"License override file '{path}' not found.")

		configuration = Configuration(path)

		if (schemaVersion := configuration.get("version", None)) is None:
			ex = DependencyError(f"License override file '{path}' states no 'version'.")
			ex.add_note("It says which structure the file is written for, so a later one can be told apart.")
			ex.add_note(f'Add it as the first field: version: "{cls.SCHEMA_VERSION}"')
			raise ex

		try:
			fileVersion = SemanticVersion.Parse(str(schemaVersion))
		except ValueError as cause:
			ex = DependencyError(f"License override file '{path}' states a 'version' that isn't a version number.")
			ex.add_note(f"Got '{schemaVersion}'.")
			raise ex from cause

		if fileVersion != cls.SCHEMA_VERSION:
			ex = DependencyError(f"License override file '{path}' is written for structure '{fileVersion}'.")
			ex.add_note(f"This reads '{cls.SCHEMA_VERSION}'.")
			raise ex

		if (analysedDay := configuration.get("analysedAt", None)) is None:
			ex = DependencyError(f"License override file '{path}' states no 'analysedAt' date.")
			ex.add_note("These statements are written by hand, so nothing else records how old they are.")
			ex.add_note("Add an ISO-8601 date, for example: analysedAt: 2026-09-02")
			raise ex

		try:
			analysedAt = date.fromisoformat(str(analysedDay))
		except ValueError as cause:
			ex = DependencyError(f"License override file '{path}' states an 'analysedAt' that isn't an ISO-8601 date.")
			ex.add_note(f"Got '{analysedDay}'.")
			ex.add_note("Write it as an ISO-8601 date: analysedAt: 2026-09-02")
			raise ex from cause

		packages = configuration.get("packages", None)
		if packages is None:
			return cls(analysedAt)
		elif not isinstance(packages, Dictionary):
			ex = DependencyError(f"License override file '{path}' states a 'packages' node that isn't a mapping.")
			ex.add_note(f"Got '{packages}'.")
			raise ex

		return cls.FromDictionary(packages, analysedAt)

	@classmethod
	def FromDictionary(cls, packages: Union[Mapping[str, Any], Dictionary], analysedAt: Nullable[date] = None) -> Self:
		"""
		Build overrides from an already parsed mapping.

		Keeping this apart from :meth:`FromFile` is what lets the overrides be assembled in code, and tested, without
		a file and without YAML.

		A :class:`~pyTooling.Configuration.Dictionary` is accepted beside a plain :class:`dict`, which is what lets
		:meth:`FromFile` hand over a configuration node without flattening it first. Only ``items()`` and ``get()``
		are read, so a configuration node of either backend fits - it is **not** a :class:`~typing.Mapping`, because
		its bare iteration yields values rather than keys.

		:param packages:         Mapping of a package's name to what is stated for it.
		:param analysedAt:       Optional, the day these statements were last checked. :meth:`FromFile` requires one;
		                         overrides assembled in code are as old as the code and need none.
		:returns:                The overrides the mapping states.
		:raises DependencyError: If a version specifier can't be parsed.
		"""
		overrides = cls(analysedAt)

		# A configuration node types its values as the whole 'ValueT' union, which every '.get' below would then
		# have to be narrowed against. What is read here is a document either way, so it is read as one.
		statement: Any
		for packageKey, statement in packages.items():
			name, versionExpression = cls._SplitKey(str(packageKey))

			for field, table in (
				("license",    overrides._licenses),
				("licenseURL", overrides._licenseURLs),
				("repository", overrides._repositories),
			):
				if (value := statement.get(field, None)) is not None:
					table.setdefault(name, []).append((versionExpression, str(value)))

		return overrides

	@classmethod
	def _SplitKey(cls, packageKey: str) -> tuple[str, PythonVersionExpression[SemanticVersion]]:
		"""
		Split a key into the package it names and the version expression it restricts that package to.

		A key is the shape a requirement line has - a name, then optionally a version expression, with or without a
		space between them. A key naming only a package gives an expression with no constraints, which matches every
		version.

		:param packageKey:       The key as the file writes it.
		:returns:                The canonical package name, and the version expression.
		:raises DependencyError: If what follows the name isn't a version expression.
		"""
		match = cls._PACKAGE_KEY.match(packageKey)
		if match is None:                                              # pragma: no cover
			ex = DependencyError(f"Key '{packageKey}' doesn't name a package.")
			raise ex

		try:
			versionExpression: PythonVersionExpression[SemanticVersion] = PythonVersionExpression.Parse(match["expression"])
		except (LicenseExpressionError, ValueError) as cause:
			ex = DependencyError(f"Key '{packageKey}' states a version expression that can't be parsed.")
			ex.add_note(f"Got '{match['expression']}'.")
			ex.add_note("A bare version is an equality, so 'igraph 0.10' and 'igraph ==0.10' state the same thing.")
			raise ex from cause

		return canonicalize_name(match["name"]), versionExpression

	def LicenseOf(self, packageName: str, version: Nullable[SemanticVersion] = None) -> Nullable[str]:
		"""
		Return the license expression stated for a package, or for one of its versions.

		Keys are tried in the order the file writes them and the first one this version satisfies wins, so a
		narrower statement answers before the bare name it refines.

		:param packageName: Name of the package.
		:param version:     Optional, the version to answer for. Without one, only a key naming no version answers.
		:returns:           The license expression stated, or ``None`` if the package isn't overridden.
		"""
		return self._Lookup(self._licenses, packageName, version)

	def LicenseURLOf(self, packageName: str, version: Nullable[SemanticVersion] = None) -> Nullable[str]:
		"""
		Return the URL of a package's license text, where one was stated.

		:param packageName: Name of the package.
		:param version:     Optional, the version to answer for. Without one, only a key naming no version answers.
		:returns:           The URL stated, or ``None``.
		"""
		return self._Lookup(self._licenseURLs, packageName, version)

	@staticmethod
	def _Lookup(
		table:       dict[str, list[tuple[PythonVersionExpression[SemanticVersion], str]]],
		packageName: str,
		version:     Nullable[SemanticVersion]
	) -> Nullable[str]:
		"""
		Return the first statement in one table whose key applies to a version.

		:param table:       One of the per-package tables.
		:param packageName: Name of the package.
		:param version:     Optional, the version to answer for. Without one, only an unrestricted key answers.
		:returns:           What that key states, or ``None`` if none applies.
		"""
		if (entries := table.get(canonicalize_name(packageName), None)) is None:
			return None

		for versionExpression, value in entries:
			# Without a version, only a key that restricts nothing can be said to apply.
			if version in versionExpression if version is not None else len(versionExpression) == 0:
				return value

		return None

	def RepositoryOf(self, packageName: str, version: Nullable[SemanticVersion] = None) -> Nullable[str]:
		"""
		Return the URL of a package's source repository, where one was stated.

		:param packageName: Name of the package.
		:param version:     Optional, the version to answer for. Without one, only a key naming no version answers.
		:returns:           The URL stated, or ``None``.
		"""
		return self._Lookup(self._repositories, packageName, version)

	def __len__(self) -> int:
		"""
		Return the number of packages that are overridden.

		:returns: Number of overridden packages.
		"""
		return len(set(self._licenses) | set(self._licenseURLs) | set(self._repositories))

	def __str__(self) -> str:
		"""
		Return a string representation of these overrides.

		:returns: The number of packages that are overridden.
		"""
		return f"LicenseOverrides({len(self)} packages)"


@export
class LazyLoaderState(IntEnum):
	"""
	Loading states of a lazy-loadable object, in the order they are reached.

	The states are ordered, so a loader can be asked for *at least* a given state and does nothing when the object is
	already loaded that far.
	"""
	Uninitialized =   0  #: No data or minimal data like ID or name.
	Initialized =     1  #: Initialized by some __init__ parameters.
	PartiallyLoaded = 2  #: Some additional data was loaded.
	FullyLoaded =     3  #: All data is loaded.
	PostProcessed =   4  #: Loaded data triggered further processing.


@export
class lazy:
	"""
	Unified decorator that supports:
	1. @lazy(state) def method()
	2. @lazy(state) @property def prop()
	"""

	def __init__(self, _requiredState: LazyLoaderState = LazyLoaderState.PartiallyLoaded):
		"""
		Initialize the decorator with the loading state its member needs.

		:param _requiredState: Optional, state the object has to be loaded to before the decorated member is used.
		"""
		self._requiredState = _requiredState
		self._wrapped = None

	def __call__(self, wrapped):
		"""
		Apply the decorator to a method or property.

		:param wrapped: The method or property to load lazily.
		:returns:       The decorator itself, which acts as the descriptor of the decorated member.
		"""
		self._wrapped = wrapped
		# If it's a function, we update metadata.
		# If it's a property, it doesn't support update_wrapper directly.
		if hasattr(wrapped, "__name__"):
			update_wrapper(self, wrapped)

		return self

	def __get__(self, obj, objtype=None):
		"""
		Load the object far enough, then hand out the decorated property's value or a bound method.

		:param obj:     The object the decorated member is accessed on, or ``None`` for a class access.
		:param objtype: Optional, the class the decorated member is accessed on.
		:returns:       The property's value, a bound wrapper around the method, or the decorator itself.
		"""
		if obj is None:
			return self

		# 1. Thread-safe state check
		with obj.__lazy_lock__:
			if obj.__lazy_state__ < self._requiredState:
				obj.__lazy_loader__(self._requiredState)

		# 2. Determine if we are wrapping a property or a method
		if isinstance(self._wrapped, property):
			# If it's a property, call its __get__ to return the value
			return self._wrapped.__get__(obj, objtype)

		# 3. Otherwise, treat as a method and return a bound wrapper
		@wraps(self._wrapped)
		def wrapper(*args, **kwargs):
			"""
			Nested function binding the decorated method to the object it was accessed on.

			:param args:   Positional parameters passed to the decorated method.
			:param kwargs: Named parameters passed to the decorated method.
			:returns:      Whatever the decorated method returns.
			"""
			return self._wrapped(obj, *args, **kwargs)

		return wrapper


@export
class LazyLoadableMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for objects whose details are fetched on first use.

	The object is created from what its creator knows - often little more than a name - and everything else is loaded
	when it is needed. The mixin records how far the object is loaded (:attr:`__lazy_state__`) and serializes
	concurrent loading (:attr:`__lazy_lock__`); the deriving class implements a ``__lazy_loader__`` method and decides what
	loading means.
	"""
	__lazy_state__: LazyLoaderState  #: State of the lazy loading process for this object.
	__lazy_lock__:  RLock            #: Lock serializing concurrent lazy loading of this object.

	def __init__(self, targetLevel: LazyLoaderState = LazyLoaderState.Initialized) -> None:
		"""
		Initialize the lazy-loading state of an object.

		:param targetLevel: Optional, state the object should be loaded to immediately; by default nothing is loaded.
		"""
		self.__lazy_state__ = LazyLoaderState.Initialized
		self.__lazy_lock__ = RLock()

		if targetLevel > self.__lazy_state__:
			with self.__lazy_lock__:
				self.__lazy_loader__(targetLevel)

	@abstractmethod
	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Load the object's details up to the given state.

		:param targetLevel: Optional, state the object needs to be loaded to.
		"""
		pass


@export
class Distribution(metaclass=ExtendedType, slots=True):
	"""
	A single downloadable file of a release - a wheel or a source archive.
	"""
	_filename:   str       #: Filename of the distribution's file.
	_url:        URL       #: URL to download the distribution's file from.
	_uploadTime: datetime  #: Time when the distribution was uploaded to the package index.

	def __init__(self, filename: str, url: Union[str, URL], uploadTime: datetime) -> None:
		"""
		Initialize a distribution with the data the package index reports for it.

		:param filename:   Filename of the distribution's file.
		:param url:        URL to download the file from, as a string or a parsed URL.
		:param uploadTime: Time the distribution was uploaded to the package index.
		:raises TypeError: If a parameter is not of the expected type.
		"""
		if not isinstance(filename, str):
			ex = TypeError("Parameter 'filename' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(filename)}'.")
			raise ex

		self._filename = filename

		if isinstance(url, str):
			url = URL.Parse(url)
		elif not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		self._url = url

		if not isinstance(uploadTime, datetime):
			ex = TypeError("Parameter 'uploadTime' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(uploadTime)}'.")
			raise ex

		self._uploadTime = uploadTime

	@readonly
	def Filename(self) -> str:
		"""
		Read-only property to access the distribution's filename (:attr:`_filename`).

		:returns: Filename of the distribution.
		"""
		return self._filename

	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the URL this distribution can be downloaded from (:attr:`_url`).

		:returns: Download URL of the distribution.
		"""
		return self._url

	@readonly
	def UploadTime(self) -> datetime:
		"""
		Read-only property to access the time this distribution was uploaded (:attr:`_uploadTime`).

		:returns: Upload time of the distribution.
		"""
		return self._uploadTime

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this distribution.

		:returns: The distribution's filename, prefixed by its kind.
		"""
		return f"Distribution: {self._filename}"

	def __str__(self) -> str:
		"""
		Return a string representation of this distribution.

		:returns: The distribution's filename.
		"""
		return f"{self._filename}"


@export
class Release(PackageVersion, LazyLoadableMixin):
	"""
	One released version of a project on a Python package index.

	A release knows its distributions (the files that can be downloaded) and its requirements, sorted into the extras
	they belong to. Both are fetched from the index on first use.
	"""
	_files:        list[Distribution]                         #: Distributions (wheels, source archives) of this release.
	_requirements: dict[Union[str, None], list[Requirement]]  #: Requirements per extra; ``None`` collects the unconditional ones.

	_api:          Nullable[URL]                              #: URL of the package index's API, used to load the release's details.
	_session:      Nullable[Session]                          #: HTTP session reused for the API requests.

	def __init__(
		self,
		version:      PythonVersion,
		timestamp:    datetime,
		files:        Nullable[Iterable[Distribution]] = None,
		requirements: Nullable[Mapping[str, list[Requirement]]] = None,
		project:      Nullable[Project] = None,
		lazy:         LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
		"""
		Initialize a release of a project.

		The API endpoint and the HTTP session are taken from the project's package index, so a release created from a
		project can fetch its own details.

		:param version:      Version number of this release.
		:param timestamp:    Time this version was released.
		:param files:        Optional, distributions of this release.
		:param requirements: Optional, requirements of this release, by extra.
		:param project:      Optional, project this release belongs to.
		:param lazy:         Optional, state the release should be loaded to immediately.
		"""
		if project is not None and (storage := project._storage) is not None:
			self._api =     storage._api
			self._session = storage._session
		else:
			self._api =     None
			self._session = None

		super().__init__(version, project, timestamp)
		LazyLoadableMixin.__init__(self, lazy)

		self._files = [file for file in files] if files is not None else []
		self._requirements = {k: v for k, v in requirements} if requirements is not None else {None: []}

	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Download the release's details and post-process them, as far as the target state demands.

		:param targetLevel: Optional, state the release needs to be loaded to.
		"""
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.PostProcess()

	@lazy(LazyLoaderState.PostProcessed)
	@PackageVersion.DependsOn.getter
	def DependsOn(self) -> dict[Package, dict[SemanticVersion, PackageVersion]]:
		"""
		Read-only property to access the packages this release depends on.

		:returns: Dictionary of packages and their versions this release depends on.
		"""
		return super().DependsOn

	@readonly
	def Project(self) -> Project:
		"""
		Read-only property to access the project this release belongs to (:attr:`_package`).

		:returns: The project this release belongs to.
		"""
		return self._package

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Files(self) -> list[Distribution]:
		"""
		Read-only property to access the distributions published for this release (:attr:`_files`).

		:returns: List of distributions.
		"""
		return self._files

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Requirements(self) -> dict[str, list[Requirement]]:
		"""
		Read-only property to access the release's requirements, grouped by extra (:attr:`_requirements`).

		:returns: Dictionary of extras and their requirements. Requirements without an extra are stored under ``None``.
		"""
		return self._requirements

	def _GetPyPIEndpoint(self) -> str:
		"""
		Return the API endpoint describing this release.

		:returns: The endpoint's path, relative to the index's API URL.
		"""
		return f"{self._package._name.lower()}/{self._version}/json"

	def DownloadDetails(self) -> None:
		"""
		Download this release's details from the package index and load the projects it requires.

		:raises NoSessionAvailableError: If the release wasn't created by a package index, so it has no session. |br|
		                                 A session is opened by the package index and handed to the objects it
		                                 creates.
		:raises ReleaseNotFoundError:    If the index doesn't know this release.
		"""
		if self._session is None:
			ex = NoSessionAvailableError(f"No session available to download release '{self._version}' of package '{self._package._name}'.")
			ex.add_note("A session is opened by the package index and handed to the objects it creates.")
			raise ex

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response is not None and ex.response.status_code == 404:
				raise ReleaseNotFoundError(f"Release '{self._version}' of package '{self._package._name}' not found.") from ex

			raise

		self.UpdateDetailsFromPyPIJSON(response.json())

		index: PythonPackageIndex = self._package._storage
		for requirement in self._requirements[None]:
			packageName = requirement.name
			index.DownloadProject(packageName, True)

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
		"""
		Fill this release from the JSON document the package index returned.

		The requirements are sorted into the extras they belong to. A requirement lands under ``None`` when it has no
		marker at all, and also when its marker conditions it on the *environment* rather than on an extra -
		``importlib-resources; python_version < "3.7"`` is required unconditionally, just not everywhere. A
		requirement naming an extra the release does not declare is reported as a :class:`BrokenRequirementWarning`.

		Metadata older than core-metadata 2.1 has no ``provides_extra`` field. Its extras are recovered from the
		markers naming them, because dropping every conditional requirement of an old release would empty exactly the
		releases a version-aware dependency graph is built to look at. A declared extra keeps the spelling it was
		declared with; a recovered one has no such spelling, so it keeps the canonical one - ``theme_furo`` written in
		a marker is recovered as ``theme-furo``.

		:param json: The parsed JSON document describing this release.
		"""
		infoNode = json["info"]
		self._ResolveLicense(infoNode)
		self._ResolveURLs(infoNode)

		requirements = [Requirement(requirement) for requirement in (infoNode["requires_dist"] or ())]

		# The declared spelling is kept as the key, while the canonical one - 'code_style' and 'code-style' are the
		# same extra - is what a marker is matched against.
		if (declaredExtras := infoNode["provides_extra"]) is not None:
			extras = {canonicalize_name(extra): extra for extra in declaredExtras}
		else:
			extras = {}
			for requirement in requirements:
				if requirement.marker is not None:
					for name in _EXTRA_MARKER.findall(str(requirement.marker)):
						extras.setdefault(canonicalize_name(name), name)

		self._requirements = {extra: [] for extra in extras.values()}
		self._requirements[None] = []

		if len(requirements) > 0:
			brokenRequirements = []
			for req in requirements:
				# A marker naming no extra conditions the requirement on the interpreter or the platform, so the
				# requirement is unconditional as far as the extras are concerned.
				if req.marker is None or len(namedExtras := _EXTRA_MARKER.findall(str(req.marker))) == 0:
					self._requirements[None].append(req)
					continue

				for name in namedExtras:
					if (extra := extras.get(canonicalize_name(name))) is not None:
						self._requirements[extra].append(req)
						break
				else:
					brokenRequirements.append(req)

			if len(brokenRequirements) > 0:
				WarningCollector.Raise(
					BrokenRequirementWarning(f"Package '{self._package._name}' has {len(brokenRequirements)} requirement(s) whose marker matches no declared extra."),
					notes=[f"Broken requirement: {req}" for req in brokenRequirements]
				)
				# Preserving the broken requirements under the special index 0 makes 'Requirements' a dictionary of mixed
				# key types (str, None and int), which no consumer expects.
				# self._requirements[0] = brokenRequirements

		self.__lazy_state__ = LazyLoaderState.FullyLoaded

	def _ResolveLicense(self, infoNode: Mapping[str, Any]) -> None:
		"""
		Resolve this release's license from what was published, and from what was stated by hand.

		The sources are consulted in order of how much they can be trusted, and the first one that answers wins:

		1. the :class:`LicenseOverrides` of the package index - an explicit statement always wins,
		2. ``license_expression``, the PEP 639 field, which is an SPDX expression by definition,
		3. ``license``, the legacy free-text field - it is handed to the parser like any other candidate, and a field
		   holding the license's full text simply doesn't parse,
		4. a license classifier, but only when it means exactly one license - ``License :: OSI Approved :: BSD
		   License`` means either ``BSD-2-Clause`` or ``BSD-3-Clause`` and is never guessed at.

		``License :: Other/Proprietary License`` is the classifier that resolves without parsing anything: SPDX has
		no identifier for a license that isn't published, so it becomes a
		:class:`~pyTooling.Licensing.ProprietaryLicense` and the classifier itself is what
		:attr:`~pyTooling.Dependency.PackageVersion.PublishedLicense` reports.

		Whatever was found is parsed into a :class:`~pyTooling.Licensing.LicenseExpression` and kept verbatim in
		:attr:`~pyTooling.Dependency.PackageVersion.PublishedLicense`, even when it doesn't parse. A release whose
		license stays unresolved is reported as an
		:class:`~pyTooling.Dependency.UnknownLicenseWarning` naming what was published, because that is the list of
		packages the override file has to answer for. A release publishing ``NOASSERTION`` or ``NONE`` is on that
		list too - the *statement* resolved, the license is still unknown.

		:param infoNode: The ``info`` node of the JSON document describing this release.
		"""
		index: PythonPackageIndex = self._package._storage
		overrides = index._licenseOverrides
		published = []
		candidates = []
		proprietaryClassifier = None

		if (override := overrides.LicenseOf(self._package._name, self._version)) is not None:
			candidates.append(override)
		else:
			if (licenseExpression := infoNode.get("license_expression", None)) is not None:
				published.append(f"license_expression: {licenseExpression}")
				candidates.append(licenseExpression)
			elif (licenseText := (infoNode.get("license", None) or "").strip()) != "":
				published.append(f"license: {licenseText[:_LICENSE_NOTE_LENGTH]}")
				candidates.append(licenseText)

			for classifier in infoNode.get("classifiers", None) or ():
				if not classifier.startswith("License ::"):
					continue

				published.append(f"classifier: {classifier}")
				if classifier == _PROPRIETARY_CLASSIFIER:
					proprietaryClassifier = classifier
				elif len(matches := LICENSES_BY_CLASSIFIER.get(classifier, ())) == 1:
					candidates.append(matches[0].SPDXIdentifier)

				break

		for candidate in candidates:
			try:
				self._licenseExpression = LicenseExpression.Parse(candidate)
			except (LicenseExpressionError, ValueError):
				continue

			# The expression keeps the candidate as its 'OriginalText', which is the only place it is held.
			break
		else:
			if proprietaryClassifier is not None:
				# SPDX has no identifier for a proprietary license, so there is nothing to parse - the node is built,
				# and it carries the classifier it was built from.
				self._licenseExpression = ProprietaryLicense(originalText=proprietaryClassifier)
			else:
				# Nothing resolved. 'NOASSERTION' is what SPDX says for that, and the node keeps what was published.
				self._licenseExpression = UnknownLicense(
					LicenseAbsence.NoAssertion,
					candidates[0] if len(candidates) > 0 else ""
				)

		if (licenseURL := overrides.LicenseURLOf(self._package._name)) is not None:
			self._licenseURL = URL.Parse(licenseURL)

		# 'UnknownLicense' covers both: the index said 'NOASSERTION' itself, and nothing resolved at all. Either way
		# the license is unknown, which is what this list is for.
		if isinstance(self._licenseExpression, UnknownLicense):
			WarningCollector.Raise(
				UnknownLicenseWarning(
					f"License of '{self._package._name}' {self._version} couldn't be resolved."
				),
				notes=published if len(published) > 0 else ["The package index published no license information."]
			)

	def _ResolveURLs(self, infoNode: Mapping[str, Any]) -> None:
		"""
		Resolve this release's project URLs from what the package index published.

		``project_urls`` is a free-text mapping - one project writes ``Source``, another ``Source Code``,
		``Repository`` or ``GitHub`` for the same thing - so its keys are matched case-insensitively against a list of
		aliases per URL and the first alias present wins. ``home_page`` is the fallback for the homepage, and the
		homepage is the last resort for the repository, which is what the project-level resolver used to do.

		These are resolved per release rather than per package because they move: a project migrating from Google
		Code or SourceForge to GitHub has one repository URL before the migration and another after it.
		:attr:`~pyTooling.Dependency.Package.RepositoryURL` and its siblings mirror the latest release, so the
		package still answers for the current state.

		:param infoNode: The ``info`` node of the JSON document describing this release.
		"""
		projectURLs = {
			str(key).strip().lower(): value
			for key, value in (infoNode.get("project_urls", None) or {}).items()
			if value is not None
		}

		def urlFor(aliases: tuple[str, ...]) -> Nullable[URL]:
			"""
			Return the first of the given aliases the package index published a URL for.

			:param aliases: The keys to look for, most specific first.
			:returns:       The URL of the first alias that is present, or ``None`` if none of them is.
			"""
			for alias in aliases:
				if (url := projectURLs.get(alias, None)) is not None:
					return URL.Parse(url)

			return None

		self._documentationURL = urlFor(_DOCUMENTATION_URL_ALIASES)
		self._issueTrackerURL  = urlFor(_ISSUE_TRACKER_URL_ALIASES)
		self._changelogURL     = urlFor(_CHANGELOG_URL_ALIASES)
		self._projectURL      = urlFor(_PROJECT_URL_ALIASES)

		if self._projectURL is None and (homePage := infoNode.get("home_page", None)) is not None:
			self._projectURL = URL.Parse(homePage)

		index: PythonPackageIndex = self._package._storage
		if (repository := index._licenseOverrides.RepositoryOf(self._package._name)) is not None:
			self._repositoryURL = URL.Parse(repository)
		elif (repositoryURL := urlFor(_REPOSITORY_URL_ALIASES)) is not None:
			self._repositoryURL = repositoryURL
		else:
			self._repositoryURL = self._projectURL

	def PostProcess(self) -> None:
		"""
		Resolve this release's requirements into dependencies on concrete releases.

		Every required project is downloaded and the releases matching the requirement's specifier are attached as
		dependencies of this release.
		"""
		index: PythonPackageIndex = self._package._storage
		for requirement in self._requirements[None]:
			package = index.DownloadProject(requirement.name)

			for release in package:
				if str(release._version) in requirement.specifier:
					self.AddDependencyToPackageVersion(release)

		self.SortDependencies()
		self.__lazy_state__ = LazyLoaderState.PostProcessed

	@lazy(LazyLoaderState.PartiallyLoaded)
	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this release, loading its details if needed.

		:returns: Package name, version and the number of distributions.
		"""
		return f"Release: {self._package._name}:{self._version} Files: {len(self._files)}"

	def __str__(self) -> str:
		"""
		Return a string representation of this release.

		:returns: The release's version number.
		"""
		return f"{self._version}"


@export
class Project(Package, LazyLoadableMixin):
	"""
	A project (package) on a Python package index, with its releases.

	The list of releases and the project's details are fetched from the index on first use.
	"""
	_url:         Nullable[URL]      #: URL of the project's page on the package index.

	_api:         Nullable[URL]      #: URL of the package index's API, used to load the project's details.
	_session:     Nullable[Session]  #: HTTP session reused for the API requests.

	def __init__(
		self,
		name:     str,
		url:      Union[str, URL],
		releases: Nullable[Iterable[Release]] = None,
		index:    Nullable[PythonPackageIndex] = None,
		lazy:     LazyLoaderState = LazyLoaderState.Initialized
	) -> None:
		"""
		Initialize a project on a package index.

		The API endpoint and the HTTP session are taken from the index, so the project can fetch its own details.

		:param name:     Name of the project on the package index.
		:param url:      URL of the project's page, as a string or a parsed URL.
		:param releases: Optional, releases of this project.
		:param index:    Optional, package index this project is hosted on.
		:param lazy:     Optional, state the project should be loaded to immediately.
		"""
		if index is not None:
			self._api =     index._api
			self._session = index._session
		else:
			self._api =     None
			self._session = None

		super().__init__(name, storage=index)
		LazyLoadableMixin.__init__(self, lazy)

		# if isinstance(url, str):
		# 	url = URL.Parse(url)
		# elif not isinstance(url, URL):
		# 	ex = TypeError("Parameter 'url' is not of type 'URL'.")
		# 	ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
		# 	raise ex
		#
		# self._url = url
		# self._releases = {release.Version: release for release in sorted(releases, key=lambda r: r.Version)} if releases is not None else {}

	def __lazy_loader__(self, targetLevel: LazyLoaderState) -> None:
		"""
		Download the project's details and its releases' details, as far as the target state demands.

		:param targetLevel: Optional, state the project needs to be loaded to.
		"""
		if targetLevel >= LazyLoaderState.PartiallyLoaded:
			self.DownloadDetails()
		if targetLevel >= LazyLoaderState.PostProcessed:
			self.DownloadReleaseDetails()

	@readonly
	def PackageIndex(self) -> PythonPackageIndex:
		"""
		Read-only property to access the package index this project was read from (:attr:`_storage`).

		:returns: The package index this project belongs to.
		"""
		return self._storage

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the project's URL in the package index (:attr:`_url`).

		:returns: URL of the project.
		"""
		return self._url

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def Releases(self) -> dict[PythonVersion, Release]:
		"""
		Read-only property to access all known releases of this project (:attr:`_versions`).

		:returns: Dictionary of versions and their releases.
		"""
		return self._versions

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def ReleaseCount(self) -> int:
		"""
		Read-only property to return the number of known releases.

		:returns: Number of releases.
		"""
		return len(self._versions)

	@lazy(LazyLoaderState.PartiallyLoaded)
	@readonly
	def LatestRelease(self) -> Release:
		"""
		Read-only property to return the most recent release of this project.

		:returns: The latest release.
		"""
		return firstValue(self._versions)

	def _GetPyPIEndpoint(self) -> str:
		"""
		Return the API endpoint describing this project.

		:returns: The endpoint's path, relative to the index's API URL.
		"""
		return f"{self._name.lower()}/json"

	def DownloadDetails(self) -> None:
		"""
		Download this project's details and its list of releases from the package index.

		:raises NoSessionAvailableError: If the project wasn't created by a package index, so it has no session. |br|
		                                 A session is opened by the package index and handed to the objects it
		                                 creates.
		:raises ProjectNotFoundError:    If the index doesn't know this project.
		"""
		if self._session is None:
			ex = NoSessionAvailableError(f"No session available to download details of package '{self._name}'.")
			ex.add_note("A session is opened by the package index and handed to the objects it creates.")
			raise ex

		response = self._session.get(url=f"{self._api}{self._GetPyPIEndpoint()}")
		try:
			response.raise_for_status()
		except HTTPError as ex:
			if ex.response is not None and ex.response.status_code == 404:
				raise ProjectNotFoundError(f"Package '{self._name}' not found.") from ex

		self.UpdateDetailsFromPyPIJSON(response.json())

	def UpdateDetailsFromPyPIJSON(self, json) -> None:
		"""
		Fill this project from the JSON document the package index returned.

		Releases without a distribution are skipped, and a version the parser doesn't understand is reported as a
		warning rather than failing the whole project.

		:param json: The parsed JSON document describing this project.
		"""
		infoNode = json["info"]
		releasesNode = json["releases"]

		# Update project/package URL
		self._url = URL.Parse(infoNode["project_url"])

		# Convert key to Version number, skip empty releases
		convertedReleasesNode = {}
		for k, v in releasesNode.items():
			if len(v) == 0:
				continue

			try:
				version = PythonVersion.Parse(k)
				convertedReleasesNode[version] = v
			except ValueError as ex:
				print(f"Unsupported version format '{k}' - {ex}")

		for version, releaseNode in sorted(convertedReleasesNode.items(), key=lambda t: t[0]):
			if Parts.Postfix in version._parts:
				pass

			files = [Distribution(file["filename"], file["url"], datetime.fromisoformat(file["upload_time_iso_8601"]), ) for
							 file in releaseNode]
			lazy = LazyLoaderState.PartiallyLoaded if LazyLoaderState.PartiallyLoaded <= self.__lazy_state__ <= LazyLoaderState.FullyLoaded else LazyLoaderState.Initialized
			Release(
				version,
				files[0]._uploadTime,
				files,
				project=self,
				lazy=lazy
			)

		self.SortVersions()
		self.__lazy_state__ = LazyLoaderState.FullyLoaded

	def DownloadReleaseDetails(self) -> None:
		"""
		Download the details of every release of this project, in parallel.

		The requests run in one :mod:`asyncio` event loop over a shared session, because a project can easily have
		hundreds of releases.
		"""
		async def ParallelDownloadReleaseDetails():
			"""
			Nested coroutine downloading the details of every release over one shared session.
			"""
			async def routine(session, release: Release):
				"""
				Nested coroutine downloading the details of a single release.

				:param session: The HTTP session shared by all requests of this download.
				:param release: The release to download the details for.
				"""
				if Parts.Postfix in release._version._parts:
					pass

				async with session.get(release._GetPyPIEndpoint()) as response:
					json = await response.json()
					response.raise_for_status()

					release.UpdateDetailsFromPyPIJSON(json)

			async with ClientSession(base_url=str(self._api), headers={"accept": "application/json"}) as session:
				tasks = []
				for release in self._versions.values():  # type: Release
					tasks.append(routine(session, release))

				results = await asyncio_gather(*tasks, return_exceptions=True)
				delList = []
				for release, result in zip(self.Releases.values(), results):
					if isinstance(result, Exception):
						delList.append((release, result))

				for release, ex in delList:
					WarningCollector.Raise(
						ReleaseDetailsWarning(f"Dropping release '{release.Version}' of package '{release.Project._name}': details couldn't be downloaded."),
						ex
					)
					del self.Releases[release.Version]

		asyncio_run(ParallelDownloadReleaseDetails())
		self.__lazy_state__ = LazyLoaderState.PostProcessed

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this project.

		:returns: The project's name and its latest release's version.
		"""
		return f"Project: {self._name} latest: {self.LatestRelease._version}"

	def __str__(self) -> str:
		"""
		Return a string representation of this project.

		:returns: The project's name.
		"""
		return f"{self._name}"


@export
class PythonPackageIndex(PackageStorage):
	"""
	A Python package index like PyPI, addressed through its JSON API.

	It is the entry point of the dependency graph: projects are looked up here, and every request to the index reuses
	the same HTTP session.
	"""
	_url:              URL               #: URL of the package index's website.
	_api:              URL               #: URL of the package index's API.
	_session:          Session           #: HTTP session reused for every request to this index.
	_licenseOverrides: LicenseOverrides  #: Licenses stated by hand, for what this index can't answer for.

	def __init__(
		self,
		name: str,
		url: Union[str, URL],
		api: Union[str, URL],
		graph: PackageDependencyGraph,
		licenseOverrides: Nullable[LicenseOverrides] = None
	) -> None:
		"""
		Initialize a package index and open the HTTP session used for every request to it.

		:param name:             Name of the package index.
		:param url:              URL of the index's website, as a string or a parsed URL.
		:param api:              URL of the index's JSON API, as a string or a parsed URL.
		:param graph:            Dependency graph this index belongs to.
		:param licenseOverrides: Optional, licenses stated by hand; an empty set of overrides if not given.
		:raises TypeError:       If parameter 'url' is neither a string nor a :class:`~pyTooling.GenericPath.URL.URL`.
		:raises TypeError:       If parameter 'api' is neither a string nor a :class:`~pyTooling.GenericPath.URL.URL`.
		"""
		super().__init__(name, graph)

		self._licenseOverrides = licenseOverrides if licenseOverrides is not None else LicenseOverrides()

		if isinstance(url, str):
			url = URL.Parse(url)
		elif not isinstance(url, URL):
			ex = TypeError("Parameter 'url' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		self._url = url

		if isinstance(api, str):
			api = URL.Parse(api)
		elif not isinstance(api, URL):
			ex = TypeError("Parameter 'api' is not of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(api)}'.")
			raise ex

		self._api = api

		self._session = Session()
		self._session.headers["accept"] = "application/json"

	@readonly
	def URL(self) -> URL:
		"""
		Read-only property to access the package index' base URL (:attr:`_url`).

		:returns: Base URL of the package index.
		"""
		return self._url

	@readonly
	def LicenseOverrides(self) -> LicenseOverrides:
		"""
		Read-only property to access the licenses stated by hand for this index (:attr:`_licenseOverrides`).

		:returns: The index's license overrides.
		"""
		return self._licenseOverrides

	@readonly
	def API(self) -> URL:
		"""
		Read-only property to access the package index' API URL (:attr:`_api`).

		:returns: API URL of the package index.
		"""
		return self._api

	@readonly
	def Projects(self) -> dict[str, Project]:
		"""
		Read-only property to access all projects known to this package index (:attr:`_packages`).

		:returns: Dictionary of project names and projects.
		"""
		return self._packages

	@readonly
	def ProjectCount(self) -> int:
		"""
		Read-only property to return the number of known projects.

		:returns: Number of projects.
		"""
		return len(self._packages)

	def _GetPyPIEndpoint(self, projectName: str) -> str:
		"""
		Return the API endpoint describing a project.

		:param projectName: Name of the project on the package index.
		:returns:           The endpoint's URL.
		"""
		return f"{self._api}{projectName.lower()}/json"

	def DownloadProject(self, projectName: str, lazy: LazyLoaderState = LazyLoaderState.PartiallyLoaded) -> Project:
		"""
		Look up a project on this package index.

		:param projectName: Name of the project on the package index.
		:param lazy:        Optional, state the project should be loaded to immediately.
		:returns:           The project, loaded as far as ``lazy`` demands.
		"""
		project = Project(projectName, "", index=self, lazy=lazy)

		return project

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this package index.

		:returns: The index's name.
		"""
		return f"{self._name}"

	def __str__(self) -> str:
		"""
		Return a string representation of this package index.

		:returns: The index's name.
		"""
		return f"{self._name}"


@export
class PythonPackageDependencyGraph(PackageDependencyGraph):
	"""
	A dependency graph of Python packages, whose vertices are projects and whose edges are requirements.
	"""

	def __init__(self, name: str) -> None:
		"""
		Initialize an empty dependency graph of Python packages.

		:param name: Name of the dependency graph.
		"""
		super().__init__(name)
