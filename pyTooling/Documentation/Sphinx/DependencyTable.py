# ==================================================================================================================== #
#             _____           _ _               ____                                        _        _   _             #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___   ___ _   _ _ __ ___   ___ _ __ | |_ __ _| |_(_) ___  _ __  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ / __| | | | '_ ` _ \ / _ \ '_ \| __/ _` | __| |/ _ \| '_ \ #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | (_) | (__| |_| | | | | | |  __/ | | | || (_| | |_| | (_) | | | |#
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___/ \___|\__,_|_| |_| |_|\___|_| |_|\__\__,_|\__|_|\___/|_| |_|#
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A Sphinx directive rendering a project's dependencies as a table, from the requirements rather than by hand.

A dependency table states, per package, which version is required, what it is licensed under, and what it drags in.
Written by hand it is wrong within a release or two: pyTooling's own documentation table was missing four of the
packages :file:`doc/requirements.txt` requires, listed one that isn't required at all, and called Sphinx BSD-3-Clause
when it is BSD-2-Clause.

**The entrypoints are declared in** :file:`conf.py` **and named by the documents**, the way
:mod:`sphinx_reports` declares its reports:

.. code-block:: Python

   # doc/conf.py
   pyTooling_dependency_licenses = "dependencies.yml"
   pyTooling_dependency_requirements = {
     "package":       {"file":    "../requirements.txt"},
     "documentation": {"file":    "requirements.txt"},
     "yaml":          {"package": "pyTooling[yaml]"}
   }

.. code-block:: rest

   .. dependency-table:: documentation
      :caption: Documentation dependencies

A requirements file is read - with its ``-r`` includes followed - while :file:`conf.py` is being processed, so a
path that doesn't exist ends the build with one clear message instead of an error box in the middle of a page.

**The data is fetched live** from the package index, once per build and shared between every table of that build:
:file:`requirements.txt`, :file:`tests/requirements.txt` and :file:`doc/requirements.txt` overlap heavily, and a
package they share is downloaded once. That still costs real time, so every table reports what it spent, measured
with a :class:`~pyTooling.Stopwatch.Stopwatch`, and the build ends with the total.
"""
from __future__                    import annotations

from pathlib                       import Path
from typing                        import TYPE_CHECKING, Any, Literal, Optional as Nullable, cast

from docutils                      import nodes
from docutils.parsers.rst          import directives
from sphinx.application            import Sphinx
from sphinx.util                   import logging

from pyTooling.Common              import getFullyQualifiedName
from pyTooling.Decorators          import export, readonly
from pyTooling.Dependency          import UnknownLicenseWarning
from pyTooling.Exceptions          import ConfigurationError, MissingDependencyError
from pyTooling.MetaClasses         import ExtendedType
from pyTooling.Stopwatch           import Stopwatch
from pyTooling.Warning             import WarningCollector

if TYPE_CHECKING:  # pragma: no cover
	# Only this directive needs a package index, so the model is imported when the configuration declares an
	# entrypoint rather than when the extension is loaded - otherwise every documentation build using any of these
	# roles would need the 'pypi' extra.
	from sphinx.config               import Config
	from packaging.requirements      import Requirement
	from packaging.specifiers        import SpecifierSet
	from pyTooling.Dependency.Python import LicenseOverrides, Project, PythonPackageDependencyGraph
	from pyTooling.Dependency.Python import PythonPackageIndex, Release, RequirementsFile

from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip
from pyTooling.Documentation.Sphinx.Directives import stripAndNormalize


#: URL of the package index the tables are built from, unless :file:`conf.py` names another.
DEFAULT_INDEX_URL = "https://pypi.org"

#: URL of that index's JSON API.
DEFAULT_API_URL = "https://pypi.org/pypi/"

#: Levels of sub-dependencies rendered when nothing says otherwise; ``0`` expands until the tree ends.
DEFAULT_DEPTH = 0

#: Whether a version constraint is reduced to its lower bound when the document doesn't say.
DEFAULT_SIMPLIFIED_VERSIONS = True

#: Comparison operators as a reader writes them. Order matters - the two-character forms have to be tried first.
OPERATOR_SYMBOLS = (("<=", "≤"), (">=", "≥"), ("!=", "≠"), ("==", "="))

#: Operators a simplified constraint drops: an upper bound and an exclusion say what is *not* required.
_DROPPED_OPERATORS = ("<", "<=", "!=")

#: The table's columns, as ``(title, relative width)``.
TABLE_COLUMNS = (("Package", 3), ("Version", 1), ("License", 2), ("Dependencies", 4))

#: The fields one entrypoint may state in :file:`conf.py`, exactly one of them.
#:
#: The singular forms take a string and the plural forms an iterable of strings; they are otherwise the same
#: statement, and a project writes whichever reads better where it stands.
ENTRYPOINT_FIELDS = ("file", "files", "package", "packages")

#: Prefix every configuration value of this extension carries in :file:`conf.py`.
CONFIG_PREFIX = "pyTooling_Dependency"

#: What Sphinx accepts as the rebuild condition of a configuration value - the one this extension uses.
_ConfigRebuild = Literal["env"]

#: The configuration values this directive adds to :file:`conf.py`, as ``name: (default, rebuild, types)``.
#:
#: ``Requirements`` maps an identifier to what it names - a file, files, a package or packages. The other three are
#: build-wide, because one package index is queried per build and one override file answers for it. All four are
#: ``"env"``-rebuilt: changing any of them changes every table.
CONFIG_VALUES: dict[str, tuple[Any, _ConfigRebuild, Any]] = {
	f"{CONFIG_PREFIX}_Requirements":     ({},                "env", dict),
	f"{CONFIG_PREFIX}_PackageOverrides": (None,              "env", (str, Path)),
	f"{CONFIG_PREFIX}_IndexURL":         (DEFAULT_INDEX_URL, "env", str),
	f"{CONFIG_PREFIX}_APIURL":           (DEFAULT_API_URL,   "env", str),
}

__all__ = [
	"DEFAULT_INDEX_URL", "DEFAULT_API_URL", "DEFAULT_DEPTH", "DEFAULT_SIMPLIFIED_VERSIONS", "OPERATOR_SYMBOLS",
	"TABLE_COLUMNS", "ENTRYPOINT_FIELDS", "CONFIG_PREFIX", "CONFIG_VALUES"
]

_logger = logging.getLogger(__name__)


def _OneLevelDown(depth: Nullable[int]) -> Nullable[int]:
	"""
	Return the depth one level deeper, leaving an unlimited depth unlimited.

	:param depth: Levels still to expand, or ``None`` for unlimited.
	:returns:     One level fewer, or ``None``.
	"""
	return None if depth is None else depth - 1


#: The collector of each running build, by the id of its Sphinx application.
#:
#: It can't live on the build environment, which Sphinx pickles between runs - an open HTTP session and the locks
#: guarding lazy loading are not picklable, and a cached view of a package index would be stale anyway.
_COLLECTORS: dict[int, "DependencyCollector"] = {}


@export
class Entrypoint(metaclass=ExtendedType, slots=True):
	"""
	One entry of ``pyTooling_dependency_requirements``: an identifier and the requirements it stands for.

	A file entrypoint is read while :file:`conf.py` is being processed and carries its requirements from then on.
	A package entrypoint can only be resolved by asking the package index, so it carries the package's name and
	extra and is resolved the first time a table names it.
	"""

	_identifier:   str                                  #: Name the documents refer to this entrypoint by.
	_files:        tuple[Path, ...]                     #: Every requirements file read, references included.
	_packages:     tuple[tuple[str, Nullable[str]], ...]  #: Packages to read the requirements of, as name and extra.
	_requirements: Nullable[dict[str, Requirement]]     #: The resolved requirements, by canonical package name.

	def __init__(
		self,
		identifier: str,
		files: tuple[Path, ...] = (),
		packages: tuple[tuple[str, Nullable[str]], ...] = (),
		requirements: Nullable[dict[str, Requirement]] = None
	) -> None:
		"""
		Describe one entrypoint.

		:param identifier:   Name the documents refer to this entrypoint by.
		:param files:        Every requirements file read, for a file entrypoint.
		:param packages:     The packages and their extras, for a package entrypoint.
		:param requirements: The requirements, if they are known already.
		"""
		self._identifier = identifier
		self._files = files
		self._packages = packages
		self._requirements = requirements

	@readonly
	def Identifier(self) -> str:
		"""
		Name the documents refer to this entrypoint by.

		:returns: The identifier.
		"""
		return self._identifier

	@readonly
	def Files(self) -> tuple[Path, ...]:
		"""
		The requirements file and every file it includes.

		:returns: The files this entrypoint was read from; empty for a package entrypoint.
		"""
		return self._files

	@readonly
	def Packages(self) -> tuple[tuple[str, Nullable[str]], ...]:
		"""
		The packages this entrypoint reads the requirements of, as ``(name, extra)`` pairs.

		:returns: The packages, or an empty tuple for a file entrypoint.
		"""
		return self._packages

	@readonly
	def Requirements(self) -> Nullable[dict[str, Requirement]]:
		"""
		The requirements this entrypoint stands for.

		:returns: Every required package by its canonical name, or ``None`` if they weren't resolved yet.
		"""
		return self._requirements

	def CacheRequirements(self, requirements: dict[str, Requirement]) -> None:
		"""
		Remember the requirements the package index answered with.

		A package entrypoint can only be resolved by asking the index; remembering the answer is what keeps a second
		table naming the same entrypoint from asking again.

		:param requirements: Every required package, by its canonical name.
		"""
		self._requirements = requirements

	def __repr__(self) -> str:
		"""
		Return a representation naming what this entrypoint reads.

		:returns: The identifier and its source.
		"""
		if len(self._files) > 0:
			source = ", ".join(str(file) for file in self._files)
		else:
			source = ", ".join(name if extra is None else f"{name}[{extra}]" for name, extra in self._packages)

		return f"<Entrypoint {self._identifier}: {source}>"


@export
class DependencyCollector(metaclass=ExtendedType, slots=True):
	"""
	The entrypoints a build declared, the package index it queries, and what querying it cost.

	One collector is shared by every table of a build: a package required by two entrypoints is downloaded once, and
	the time is accumulated so the build can report a total. It exists because the alternative - a table that queries
	the index for itself - multiplies a documentation build's runtime by however many tables it has, and
	:file:`requirements.txt`, :file:`tests/requirements.txt` and :file:`doc/requirements.txt` share most of what they
	require.

	The index is opened the first time a table asks for a package, not when the collector is created: a project may
	declare its entrypoints and then build a document that shows none of them, and that build should not open an
	HTTP session.
	"""

	_entrypoints: dict[str, Entrypoint]             #: The entrypoints declared in :file:`conf.py`, by identifier.
	_indexURL:    str                               #: URL of the package index's website.
	_apiURL:      str                               #: URL of the package index's JSON API.
	_overrides:   LicenseOverrides                  #: Licenses stated by hand, for packages the index can't answer for.
	_graph:       Nullable[PythonPackageDependencyGraph]  #: Graph the downloaded packages are collected in.
	_index:       Nullable[PythonPackageIndex]      #: The package index this build queries, once it was opened.
	_projects:    dict[str, Nullable[Project]]      #: Projects downloaded so far; ``None`` for an unknown package.
	_detailed:    set[str]                          #: Releases whose details were downloaded, as ``name==version``.
	_undescribed: set[str]                          #: Releases the index lists but can't describe.
	_requestCount: int                              #: Number of requests sent to the package index.
	_stopwatch:   Stopwatch                         #: Runs only while a request to the package index is in flight.
	_unresolved:  set[str]                          #: Packages whose license the index couldn't answer for.

	def __init__(
		self,
		entrypoints: dict[str, Entrypoint],
		indexURL: str,
		apiURL: str,
		overrides: LicenseOverrides
	) -> None:
		"""
		Collect what a build declared, without opening the package index yet.

		:param entrypoints: The entrypoints declared in :file:`conf.py`, by identifier.
		:param indexURL:    URL of the package index's website.
		:param apiURL:      URL of the package index's JSON API.
		:param overrides:   Licenses stated by hand.
		"""
		self._entrypoints = entrypoints
		self._indexURL = indexURL
		self._apiURL = apiURL
		self._overrides = overrides
		self._graph = None
		self._index = None
		self._projects = {}
		self._detailed = set()
		self._undescribed = set()
		self._requestCount = 0
		self._unresolved = set()

		# started and immediately paused: it is resumed around a request and paused after, so its 'Activity' is time
		# spent waiting for the index rather than the age of the collector
		self._stopwatch = Stopwatch()
		self._stopwatch.Start()
		self._stopwatch.Pause()

	@readonly
	def Entrypoints(self) -> dict[str, Entrypoint]:
		"""
		The entrypoints declared in :file:`conf.py`.

		:returns: Every entrypoint by its identifier.
		"""
		return self._entrypoints

	@readonly
	def Index(self) -> PythonPackageIndex:
		"""
		The package index this build queries, opened the first time it is asked for.

		:returns: The package index.
		"""
		from pyTooling.Dependency.Python import PythonPackageDependencyGraph, PythonPackageIndex

		if self._index is None:
			self._graph = PythonPackageDependencyGraph("documentation")
			self._index = PythonPackageIndex("index", self._indexURL, self._apiURL, self._graph, self._overrides)

		return self._index

	@readonly
	def RequestCount(self) -> int:
		"""
		Number of requests sent to the package index.

		:returns: Number of requests sent.
		"""
		return self._requestCount

	@readonly
	def Seconds(self) -> float:
		"""
		Time spent waiting for the package index, in seconds.

		This is the stopwatch's :attr:`~pyTooling.Stopwatch.Stopwatch.Activity` - the sum of the intervals it ran -
		not its duration, because it is paused between requests and everything the build does in between is not
		time this collector spent.

		:returns: Seconds spent on the index.
		"""
		return self._stopwatch.Activity

	@readonly
	def UnresolvedLicenses(self) -> set[str]:
		"""
		Packages whose license the index couldn't answer for.

		:returns: Names of the packages needing a license override.
		"""
		return self._unresolved

	def Project(self, packageName: str) -> Nullable[Project]:
		"""
		Return a project, downloading it the first time it is asked for.

		A package the index doesn't know is remembered as unknown, so a table naming it doesn't ask again for every
		row that mentions it.

		:param packageName: Name of the package to look up.
		:returns:           The project, or ``None`` if the index doesn't know it.
		"""
		from requests                    import RequestException
		from pyTooling.Dependency        import DependencyError
		from pyTooling.Dependency.Python import LazyLoaderState

		if packageName in self._projects:
			return self._projects[packageName]

		project: Nullable[Project]
		self._stopwatch.Resume()
		try:
			project = self.Index.DownloadProject(packageName, LazyLoaderState.PartiallyLoaded)
		except (DependencyError, RequestException, ValueError, KeyError):
			project = None
		finally:
			self._stopwatch.Pause()

		self._requestCount += 1
		self._projects[packageName] = project

		return project

	def Details(self, release: Release) -> Nullable[Release]:
		"""
		Make sure a release knows its own requirements and its license.

		A release the index lists but can't describe - a yanked one, or a version its release endpoint spells
		differently - is remembered as unusable and answered with ``None``. Handing back the release itself would
		be worse than useless: its lazily loaded properties would each retry the download and raise.

		:param release: The release to fill in.
		:returns:       The release with its details downloaded, or ``None`` if the index couldn't describe it.
		"""
		from requests             import RequestException
		from pyTooling.Dependency import DependencyError

		key = f"{release.Package.Name}=={release.Version}"
		if key in self._detailed:
			return release if key not in self._undescribed else None

		warnings: list[BaseException] = []
		self._stopwatch.Resume()
		try:
			with WarningCollector(warnings):
				try:
					release.DownloadDetails()
				except (DependencyError, RequestException, ValueError, KeyError):
					self._undescribed.add(key)
		finally:
			self._stopwatch.Pause()

		self._requestCount += 1
		self._detailed.add(key)

		for warning in warnings:
			if isinstance(warning, UnknownLicenseWarning):
				self._unresolved.add(release.Package.Name)

		return None if key in self._undescribed else release


@export
def readEntrypoints(configuration: Any, confDirectory: Path) -> dict[str, Entrypoint]:
	"""
	Turn ``pyTooling_dependency_requirements`` into entrypoints, reading every requirements file it names.

	A requirements file is read here rather than when a table is built, so a path that doesn't exist ends the build
	with one message naming the identifier instead of an error box in the middle of a page - and so two tables
	naming the same file read it once.

	:param configuration:  Value of ``pyTooling_Dependency_Requirements``.
	:param confDirectory:  Directory :file:`conf.py` lives in; relative paths are resolved against it.
	:returns:              Every declared entrypoint, by its identifier.
	:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the configuration is malformed, or a
	  requirements file can't be read.
	"""
	if not isinstance(configuration, dict):
		raise SphinxExtensionError(
			f"conf.py: {CONFIG_PREFIX}_Requirements: Expected a dictionary, "
			f"got '{getFullyQualifiedName(configuration)}'."
		)

	entrypoints: dict[str, Entrypoint] = {}
	for identifier, declaration in configuration.items():
		location = f"conf.py: {CONFIG_PREFIX}_Requirements:[{identifier}]"

		if not isinstance(declaration, dict):
			raise SphinxExtensionError(
				f"{location}: Expected a dictionary, got '{getFullyQualifiedName(declaration)}'."
			)

		if (unknown := set(declaration) - set(ENTRYPOINT_FIELDS)) != set():
			raise SphinxExtensionError(
				f"{location}: Unknown field(s): {', '.join(sorted(unknown))}. "
				f"Known are: {', '.join(ENTRYPOINT_FIELDS)}."
			)

		if len(stated := [field for field in ENTRYPOINT_FIELDS if field in declaration]) != 1:
			known = ", ".join(ENTRYPOINT_FIELDS)
			raise SphinxExtensionError(
				f"{location}: Exactly one of {known} has to be configured, "
				f"{'none is' if len(stated) == 0 else f'{len(stated)} are'}."
			)

		field = stated[0]
		values = _EntrypointValues(f"{location}.{field}", field, declaration[field])

		if field in ("file", "files"):
			entrypoints[identifier] = _FileEntrypoint(identifier, f"{location}.{field}", values, confDirectory)
		else:
			entrypoints[identifier] = _PackageEntrypoint(identifier, values)

	return entrypoints


def _EntrypointValues(location: str, field: str, value: Any) -> tuple[str, ...]:
	"""
	Return an entrypoint field's value as a tuple, whichever of the two spellings was used.

	``file`` and ``package`` take one string, ``files`` and ``packages`` an iterable of them. A single string is
	*also* an iterable of strings, so the plural form has to reject one explicitly - otherwise
	``{"files": "requirements.txt"}`` would silently become sixteen one-character paths.

	:param location:                                                        Where in :file:`conf.py` this came from.
	:param field:                                                           Name of the field being read.
	:param value:                                                           Its value.
	:returns:                                                               The value(s), as a tuple.
	:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the value has the wrong shape.
	"""
	if field in ("file", "package"):
		if not isinstance(value, str):
			raise SphinxExtensionError(f"{location}: Expected a string, got '{getFullyQualifiedName(value)}'.")

		return (value,)

	if isinstance(value, str) or not isinstance(value, (tuple, list)):
		raise SphinxExtensionError(
			f"{location}: Expected a tuple or list of strings, got '{getFullyQualifiedName(value)}'. "
			f"Use '{field[:-1]}' for a single value."
		)

	for item in value:
		if not isinstance(item, str):
			raise SphinxExtensionError(f"{location}: Expected strings, got '{getFullyQualifiedName(item)}'.")

	return tuple(value)


def _FileEntrypoint(
	identifier: str,
	location: str,
	files: tuple[str, ...],
	confDirectory: Path
) -> Entrypoint:
	"""
	Read one entrypoint's requirements files.

	Several files are read as several trees and flattened in the order they are declared, so a later file's
	statement wins - the rule a single file's ``-r`` references already follow.

	:param identifier:                                                      Identifier of the entrypoint.
	:param location:                                                        Where in :file:`conf.py` this came from.
	:param files:                                                           The declared paths.
	:param confDirectory:                                                   Directory relative paths resolve against.
	:returns:                                                               The entrypoint, with its requirements read.
	:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If a file can't be read.
	"""
	from pyTooling.Dependency        import DependencyError
	from pyTooling.Dependency.Python import RequirementsFile

	readFiles: list[Path] = []
	requirements: dict[str, Requirement] = {}

	for file in files:
		path = Path(file)
		if not path.is_absolute():
			path = confDirectory / path

		try:
			requirementsFile = RequirementsFile(path)
		except (DependencyError, OSError, UnicodeDecodeError) as cause:
			raise SphinxExtensionError(f"{location}: Requirements file '{path}' can't be read: {cause}") from cause

		# the tree knows every file it was read from; walking it here would be a second answer to one question
		readFiles.extend(requirementsFile.AnalyzedRequirementFiles)
		requirements.update(requirementsFile.Flatten())

	return Entrypoint(identifier, files=tuple(readFiles), requirements=requirements)


def _PackageEntrypoint(identifier: str, packages: tuple[str, ...]) -> Entrypoint:
	"""
	Describe one entrypoint's packages, which only the package index can resolve.

	:param identifier: Identifier of the entrypoint.
	:param packages:   The declared packages, each optionally with one extra.
	:returns:          The entrypoint, with its packages recorded and its requirements still unresolved.
	"""
	requested: list[tuple[str, Nullable[str]]] = []
	for package in packages:
		name, _, bracket = package.partition("[")
		requested.append((name.strip(), bracket.rstrip("]").strip() or None))

	return Entrypoint(identifier, packages=tuple(requested))


@export
def prepareEntrypoints(sphinx: Sphinx, config: Config) -> None:
	"""
	Call-back for Sphinx' ``config-inited`` event, reading the entrypoints and the license overrides.

	A build declaring no entrypoint does nothing here - not even import :mod:`pyTooling.Dependency.Python`, so a
	project using only this extension's roles doesn't need the ``pypi`` extra.

	:param sphinx: The Sphinx application.
	:param config: The configuration, after :file:`conf.py` was read.
	:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the configuration is malformed, or a
	  requirements or license override file can't be read.
	"""
	if len(declarations := getattr(config, f"{CONFIG_PREFIX}_Requirements", {})) == 0:
		return

	confDirectory = Path(sphinx.confdir)

	try:
		from pyTooling.Dependency        import DependencyError
		from pyTooling.Dependency.Python import LicenseOverrides
	except MissingDependencyError as cause:  # pragma: no cover
		raise SphinxExtensionError(
			f"conf.py: {CONFIG_PREFIX}_Requirements: Querying a package index needs the 'pypi' extra: "
			f"pip install pyTooling[pypi]"
		) from cause

	overrides = LicenseOverrides()
	if (overrideFile := getattr(config, f"{CONFIG_PREFIX}_PackageOverrides", None)) is not None:
		path = Path(overrideFile)
		if not path.is_absolute():
			path = confDirectory / path

		try:
			overrides = LicenseOverrides.FromFile(path)
		except (DependencyError, ConfigurationError, OSError) as cause:
			raise SphinxExtensionError(
				f"conf.py: {CONFIG_PREFIX}_PackageOverrides: Override file '{path}' can't be read: {cause}"
			) from cause

	_COLLECTORS[id(sphinx)] = DependencyCollector(
		readEntrypoints(declarations, confDirectory),
		getattr(config, f"{CONFIG_PREFIX}_IndexURL", DEFAULT_INDEX_URL),
		getattr(config, f"{CONFIG_PREFIX}_APIURL", DEFAULT_API_URL),
		overrides
	)


@export
class DependencyTable(BaseDirective):
	"""
	The ``dependency-table`` directive: an entrypoint's dependencies, rendered from the requirements.

	One argument, the identifier of an entrypoint declared in ``pyTooling_dependency_requirements``. ``:depth:``
	says how many levels of sub-dependencies to expand, ``:simplified-versions:`` whether a constraint is reduced to
	its lower bound, and ``:caption:`` puts a caption under the table; which package index is queried and which
	licenses are stated by hand are build-wide and configured in :file:`conf.py`.
	"""

	directiveName: str = "dependency-table"  #: Name the directive is invoked by.

	_simplify: bool  #: Whether this table's version constraints are reduced to their lower bound.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        1      #: Number of required directive arguments: the entrypoint's identifier.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"caption":             strip,
		"depth":               directives.nonnegative_int,
		"simplified-versions": stripAndNormalize,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Resolve the named entrypoint against the package index and return its requirements as a table.

		:returns: A ``table`` node, or an error node when the entrypoint couldn't be resolved.
		"""
		identifier = self.arguments[0].strip()
		self._simplify = self._ParseBooleanOption("simplified-versions", DEFAULT_SIMPLIFIED_VERSIONS)

		with Stopwatch() as stopwatch:
			try:
				collector = self._Collector()
				requestsBefore = collector.RequestCount
				requirements = self._Resolve(identifier, collector)
				table = self._CreateTable(identifier, requirements, collector)
			except SphinxExtensionError as cause:
				return [self.state.document.reporter.error(
					f"{self.directiveName}: {cause}", line=self.lineno
				)]

		# what this table cost, not what the build has spent so far - a package another table already downloaded is
		# free here, and that is the point of sharing the collector
		_logger.info(
			f"[{self.directiveName}] {identifier}: {len(requirements)} package(s), "
			f"{collector.RequestCount - requestsBefore} request(s), {stopwatch.Duration:.2f} s"
		)

		return [table]

	def _Collector(self) -> DependencyCollector:
		"""
		Return the build's collector, which :func:`prepareEntrypoints` created when :file:`conf.py` was read.

		The collector belongs to the running application rather than to the directive, because a document with three
		tables would otherwise open three indexes and download the same packages three times. It deliberately does
		*not* live on the build environment: Sphinx pickles that between runs, and neither an open HTTP session nor a
		cached view of a package index survives being pickled - or should.

		:returns:                     The collector shared by every table of this build.
		:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If no entrypoint was configured.
		"""
		if (collector := _COLLECTORS.get(id(self.env.app), None)) is None:
			raise SphinxExtensionError(
				f"No entrypoint is configured. Declare one in conf.py: {CONFIG_PREFIX}_Requirements."
			)

		return collector

	def _Resolve(self, identifier: str, collector: DependencyCollector) -> dict[str, Requirement]:
		"""
		Return what the named entrypoint requires.

		A file entrypoint was read when :file:`conf.py` was processed and answers immediately; a package entrypoint
		is resolved against the package index the first time a table names it, and remembers the answer.

		:param identifier:            Identifier the document names.
		:param collector:             The build's collector.
		:returns:                     Every required package, by its canonical name.
		:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the identifier is unknown, or the
		  package index can't answer for the entrypoint's package.
		"""
		from packaging.utils import canonicalize_name

		if (entrypoint := collector.Entrypoints.get(identifier, None)) is None:
			known = ", ".join(sorted(collector.Entrypoints)) or "none"
			raise SphinxExtensionError(
				f"Entrypoint '{identifier}' is not configured in conf.py: {CONFIG_PREFIX}_Requirements. "
				f"Known are: {known}."
			)

		for file in entrypoint.Files:
			self.env.note_dependency(str(file))

		if (requirements := entrypoint.Requirements) is not None:
			return requirements

		# several packages flatten in the order they are declared, the rule a file's '-r' references already follow
		requirements = {}
		for packageName, extra in entrypoint.Packages:
			for requirement in self._PublishedRequirements(packageName, extra, collector):
				requirements[canonicalize_name(requirement.name)] = requirement

		entrypoint.CacheRequirements(requirements)

		return requirements

	def _PublishedRequirements(
		self,
		packageName: str,
		extra: Nullable[str],
		collector: DependencyCollector
	) -> list[Requirement]:
		"""
		Ask the package index what a package's latest release requires.

		:param packageName:           Name of the package to ask about.
		:param extra:                 Extra whose requirements are wanted, or ``None`` for the package's own.
		:param collector:             The build's collector.
		:returns:                     What that release requires.
		:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the index doesn't know the
		  package, can't describe its latest release, or the package has no such extra.
		"""
		if (project := collector.Project(packageName)) is None:
			raise SphinxExtensionError(f"Package '{packageName}' is unknown to the package index.")

		if (release := collector.Details(project.LatestRelease)) is None:
			raise SphinxExtensionError(f"The package index can't describe the latest release of '{packageName}'.")

		published: Nullable[list[Requirement]] = release.Requirements.get(extra, None)
		if published is None:
			known = ", ".join(sorted(str(key) for key in release.Requirements if key is not None))
			raise SphinxExtensionError(f"Package '{packageName}' has no extra '{extra}'. Known are: {known}.")

		return published

	def _CreateTable(
		self,
		identifier: str,
		requirements: dict[str, Requirement],
		collector: DependencyCollector
	) -> nodes.table:
		"""
		Render the requirements as a four-column table.

		:param identifier:   Identifier of the entrypoint, used as the table's identifier.
		:param requirements: Every required package, by its canonical name.
		:param collector:    The build's collector.
		:returns:            The finished table.
		"""
		tableGroup = self._CreateSingleRowTableHeader(
			columns=list(TABLE_COLUMNS),
			identifier=identifier,
			classes=["dependency-table"]
		)
		tableGroup += (tableBody := nodes.tbody())

		# ':depth: 0' - and the default - means expand until the tree ends; 'None' is that, internally, because
		# 'depth - 1' would otherwise walk 0 into negative numbers and mean two different things at once
		depth = self.options.get("depth", DEFAULT_DEPTH)
		levels: Nullable[int] = None if depth == 0 else depth

		if len(requirements) == 0:
			tableBody += self._CreateEmptyRow(len(TABLE_COLUMNS))
		else:
			for name in sorted(requirements, key=str.lower):
				tableBody += self._CreateRow(requirements[name], collector, levels)

		table = cast(nodes.table, tableGroup.parent)
		if (caption := self.options.get("caption", None)) is not None:
			# the caption is ReST, not text: it is written with markup - ``packaging`` in pyTooling's own captions -
			# and a 'title' built from a string would print the backticks
			captionNodes, messages = self.state.inline_text(caption, self.lineno)
			table.insert(0, nodes.title(caption, "", *captionNodes, *messages))

		return table

	@staticmethod
	def _CreateEmptyRow(columnCount: int) -> nodes.row:
		"""
		Render the one row a table with no requirements gets: a single cell spanning every column.

		A table showing nothing but its header reads as a defect. pyTooling's own :file:`requirements.txt` is empty
		- the package has no mandatory dependencies - and that is a statement worth printing.

		:param columnCount: Number of columns the cell has to span.
		:returns:           The table row.
		"""
		tableRow = nodes.row("", classes=["dependency-table-row"])

		entry = nodes.entry("", morecols=columnCount - 1)
		entry += nodes.paragraph("", "", nodes.emphasis(text="No dependencies"))
		tableRow += entry

		return tableRow

	def _CreateRow(
		self,
		requirement: Requirement,
		collector: DependencyCollector,
		depth: Nullable[int]
	) -> nodes.row:
		"""
		Render one required package as a table row.

		A package the index doesn't know, or one with no release matching the requirement, still gets a row - the
		specifier the entrypoint states is worth showing even when nothing else could be resolved.

		:param requirement: The requirement to render.
		:param collector:   The build's collector.
		:param depth:       Levels of sub-dependencies still to expand.
		:returns:           The table row.
		"""
		tableRow = nodes.row("", classes=["dependency-table-row"])

		project = collector.Project(requirement.name)
		release = self._SelectRelease(project, requirement, collector)

		tableRow += self._PackageEntry(requirement, project)
		tableRow += nodes.entry("", nodes.paragraph(text=self._FormatSpecifier(requirement.specifier, self._simplify)))
		tableRow += self._LicenseEntry(release)
		tableRow += self._DependenciesEntry(release, collector, depth, {requirement.name.lower()})

		return tableRow

	def _SelectRelease(
		self,
		project: Nullable[Project],
		requirement: Requirement,
		collector: DependencyCollector
	) -> Nullable[Release]:
		"""
		Return the newest release satisfying a requirement.

		Pre-releases are skipped unless the specifier asks for them, because that is what an installer would resolve
		to and the table describes what would be installed.

		:param project:     The project to pick a release of, or ``None`` if the index doesn't know it.
		:param requirement: The requirement to satisfy.
		:param collector:   The build's collector.
		:returns:           The newest matching release, or ``None`` if nothing matches.
		"""
		if project is None:
			return None

		matching = [
			release for version, release in project.Releases.items()
			if requirement.specifier.contains(str(version))
		]
		if len(matching) == 0:
			return None

		return collector.Details(max(matching, key=lambda release: release.Version))

	@staticmethod
	def _FormatSpecifier(specifier: SpecifierSet, simplify: bool) -> str:
		"""
		Render a version constraint the way a reader writes one.

		The comparison operators become their mathematical symbols. A simplified constraint keeps only what a
		package *has to be at least*: an upper bound and an exclusion say what a release must not be, which is the
		packaging problem rather than the reader's, and ``~=`` is written as the lower bound it implies. Simplifying
		everything away leaves the constraint as it was written - ``<4.0`` alone is still the whole statement.

		:param specifier: The constraint to render.
		:param simplify:  Whether to reduce the constraint to its lower bound.
		:returns:         The constraint, or ``any`` when nothing is constrained.
		"""
		def render(operator: str, version: str) -> str:
			for written, symbol in OPERATOR_SYMBOLS:
				if operator == written:
					return f"{symbol}{version}"

			return f"{operator}{version}"

		if len(specifier) == 0:
			return "any"

		specifiers = sorted(specifier, key=lambda item: (item.version, item.operator))
		if simplify:
			kept = [
				render(">=" if item.operator == "~=" else item.operator, item.version)
				for item in specifiers if item.operator not in _DROPPED_OPERATORS
			]
			if len(kept) > 0:
				return ", ".join(kept)

		return ", ".join(render(item.operator, item.version) for item in specifiers)

	@staticmethod
	def _PackageURL(project: Nullable[Project]) -> Nullable[str]:
		"""
		Return the page a package's name should link to, most useful first.

		A project states none of these reliably, so there are three chances at one: its **documentation** answers
		*what is this*, its **repository** answers *where does it come from*, and its page on the **package index**
		is what the index itself can always answer. Only a package the index doesn't know at all goes unlinked.

		:param project: The project, or ``None`` if the index doesn't know it.
		:returns:       The URL to link the name to, or ``None`` if there is nothing to link to.
		"""
		if project is None:
			return None

		for url in (project.DocumentationURL, project.RepositoryURL, project.URL):
			if url is not None:
				return str(url)

		return None

	@classmethod
	def _PackageEntry(cls, requirement: Requirement, project: Nullable[Project]) -> nodes.entry:
		"""
		Render the package's name, linked to where a reader can find out about it.

		:param requirement: The requirement naming the package.
		:param project:     The project, or ``None`` if the index doesn't know it.
		:returns:           The table entry.
		"""
		entry = nodes.entry()
		name = project.Name if project is not None else requirement.name

		if (url := cls._PackageURL(project)) is not None:
			entry += nodes.paragraph("", "", nodes.reference("", name, refuri=url))
		else:
			entry += nodes.paragraph(text=name)

		return entry

	@staticmethod
	def _LicenseEntry(release: Nullable[Release]) -> nodes.entry:
		"""
		Render a release's license, linked to its text where one is known.

		The license' **name** is shown rather than its SPDX identifier - ``Apache License 2.0``, not ``Apache-2.0`` -
		because the table is read by a person and the identifier is what an expression writes.

		A license that didn't resolve is an :class:`~pyTooling.Licensing.UnknownLicense`, never a blank cell, and it
		is shown **as the index published it** - in italics, so it reads as a quotation rather than as an identifier.
		The reader should see that the index said *something*, and what it was.

		:param release: The release to render the license of, or ``None``.
		:returns:       The table entry.
		"""
		entry = nodes.entry()

		if (text := DependencyTable._LicenseName(release)) is None:
			entry += nodes.paragraph("", "", nodes.emphasis(text=DependencyTable._PublishedLicense(release)))

			return entry

		if (url := DependencyTable._LicenseURL(release)) is not None:
			entry += nodes.paragraph("", "", nodes.reference("", text, refuri=url))
		else:
			entry += nodes.paragraph(text=text)

		return entry

	@staticmethod
	def _LicenseName(release: Nullable[Release]) -> Nullable[str]:
		"""
		Return the name(s) of the licenses a release is published under.

		:param release: The release to name the license of, or ``None``.
		:returns:       The license' name, or ``None`` if nothing resolved.
		"""
		from pyTooling.Licensing import UnknownLicense

		if release is None:
			return None

		# 'Licenses' never comes back empty: what didn't resolve is an 'UnknownLicense', which is SPDX's own way of
		# saying so and keeps the published text
		licenses = release.Licenses
		if all(isinstance(license, UnknownLicense) for license in licenses):
			return None

		return ", ".join(license.Name for license in licenses)

	@staticmethod
	def _PublishedLicense(release: Nullable[Release]) -> str:
		"""
		Return what the package index published, for a license that didn't resolve.

		:param release: The release, or ``None`` if the index couldn't describe it.
		:returns:       What was published, or ``unknown`` when that was nothing either.
		"""
		if release is None:
			return "unknown"

		published = release.LicenseExpression.OriginalText.strip()

		return published if published != "" else ", ".join(license.Name for license in release.Licenses) or "unknown"

	@staticmethod
	def _LicenseURL(release: Nullable[Release]) -> Nullable[str]:
		"""
		Return the page a license should link to, most specific first.

		**The project's own** :file:`LICENSE` **file wins**: it is the license as this project publishes it, which
		is the document a reader auditing a dependency actually wants. Most projects don't state one, though - it
		comes from ``project_urls`` or from the override file - so a license on the SPDX List falls back to its own
		published pages, in the order of who is speaking: the licensor's own page, then OSI's entry, then SPDX's.
		A ``LicenseRef-`` has none of those and stays unlinked, because nothing published it.

		:param release: The release to link the license of, or ``None``.
		:returns:       The URL to link to, or ``None`` if nothing published this license.
		"""
		from pyTooling.Licensing import SPDXLicense

		if release is None:
			return None

		if release.LicenseURL is not None:
			return str(release.LicenseURL)

		for license in release.Licenses:
			if isinstance(license, SPDXLicense):
				for url in (license.License.URL, license.License.OSIURL, license.License.SPDXURL):
					if url is not None:
						return url

		return None

	def _DependenciesEntry(
		self,
		release: Nullable[Release],
		collector: DependencyCollector,
		depth: Nullable[int],
		visited: set[str]
	) -> nodes.entry:
		"""
		Render a release's own requirements as a nested bullet list.

		Only the unconditional requirements are listed - what an extra pulls in is that extra's table, not this one.
		A package already on the path is not expanded again, so a dependency cycle terminates.

		:param release:   The release to render the dependencies of, or ``None``.
		:param collector: The build's collector.
		:param depth:     Levels still to expand; at zero nothing is expanded.
		:param visited:   Packages already on this path, lower-cased.
		:returns:         The table entry.
		"""
		entry = nodes.entry()

		if release is None or (depth is not None and depth <= 0):
			entry += nodes.paragraph("", "", nodes.emphasis(text="not evaluated"))
			return entry

		requirements = [
			requirement for requirement in release.Requirements.get(None, [])
			if requirement.name.lower() not in visited
		]
		if len(requirements) == 0:
			entry += nodes.paragraph("", "", nodes.emphasis(text="none"))
			return entry

		entry += self._CreateBulletList(requirements, collector, _OneLevelDown(depth), visited)

		return entry

	def _CreateBulletList(
		self,
		requirements: list[Requirement],
		collector: DependencyCollector,
		depth: Nullable[int],
		visited: set[str]
	) -> nodes.bullet_list:
		"""
		Render requirements as a bullet list, each item expanded by one more level.

		:param requirements: The requirements to list.
		:param collector:    The build's collector.
		:param depth:        Levels still to expand below this list.
		:param visited:      Packages already on this path, lower-cased.
		:returns:            The bullet list.
		"""
		bulletList = nodes.bullet_list()

		for requirement in sorted(requirements, key=lambda item: item.name.lower()):
			item = nodes.list_item()

			# resolved whatever the depth: a leaf still states a license, and that is the whole point of the column
			project = collector.Project(requirement.name)
			release = self._SelectRelease(project, requirement, collector)

			item += self._RequirementParagraph(requirement, project, release)

			if (depth is None or depth > 0) and release is not None:
				nested = [
					nestedRequirement for nestedRequirement in release.Requirements.get(None, [])
					if nestedRequirement.name.lower() not in visited
				]
				if len(nested) > 0:
					item += self._CreateBulletList(
						nested, collector, _OneLevelDown(depth), visited | {requirement.name.lower()}
					)

			bulletList += item

		return bulletList

	def _RequirementParagraph(
		self,
		requirement: Requirement,
		project: Nullable[Project],
		release: Nullable[Release]
	) -> nodes.paragraph:
		"""
		Render one line of a dependency tree: the package, what is required of it, and what it is licensed under.

		The license is the reason a dependency tree is in this table at all - a package pulls in what its own
		dependencies are licensed under, and reading that off the tree is the point. It is linked and parenthesised
		so the line still reads as one requirement.

		:param requirement: The requirement to render.
		:param project:     The project, or ``None`` if the index doesn't know it.
		:param release:     The release satisfying the requirement, or ``None`` if none was found.
		:returns:           The paragraph.
		"""
		paragraph = nodes.paragraph()

		specifier = self._FormatSpecifier(requirement.specifier, self._simplify)
		name = project.Name if project is not None else requirement.name
		if (url := self._PackageURL(project)) is not None:
			paragraph += nodes.reference("", name, refuri=url)
		else:
			paragraph += nodes.Text(name)

		if specifier != "any":
			paragraph += nodes.Text(f" {specifier}")

		paragraph += nodes.Text(" (")
		if (license := self._LicenseName(release)) is None:
			# the same statement the License column makes: what the index published, in italics, so it reads as a
			# quotation rather than as an identifier
			paragraph += nodes.emphasis(text=self._PublishedLicense(release))
		elif (licenseURL := self._LicenseURL(release)) is not None:
			paragraph += nodes.reference("", license, refuri=licenseURL)
		else:
			paragraph += nodes.Text(license)
		paragraph += nodes.Text(")")

		return paragraph


def reportBuildTime(app: Sphinx, exception: Nullable[Exception]) -> None:
	"""
	Report what querying the package index cost this build.

	The tables are fetched live, so this is the number to look at before deciding what a cache would be worth. The
	packages whose license had to be guessed at - or couldn't be - are named too, because that is the list the
	override file has to answer for.

	:param app:       The Sphinx application that finished building.
	:param exception: The exception that ended the build, or ``None`` if it succeeded.
	"""
	if (collector := _COLLECTORS.pop(id(app), None)) is None or collector.RequestCount == 0:
		return

	_logger.info(
		f"[dependency-table] {collector.RequestCount} request(s) to the package index, "
		f"{collector.Seconds:.2f} s in total."
	)

	if len(unresolved := collector.UnresolvedLicenses) > 0:
		_logger.warning(
			f"[dependency-table] {len(unresolved)} package(s) need a license override: "
			f"{', '.join(sorted(unresolved))}."
		)
