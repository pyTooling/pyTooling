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
from typing                        import TYPE_CHECKING, Any, Iterator, Literal, Optional as Nullable, cast

from docutils                      import nodes
from docutils.parsers.rst          import directives
from sphinx.application            import Sphinx
from sphinx.util                   import logging

from pyTooling.Decorators          import export, readonly
from pyTooling.Dependency          import UnknownLicenseWarning
from pyTooling.Exceptions          import MissingDependencyError
from pyTooling.MetaClasses         import ExtendedType
from pyTooling.Stopwatch           import Stopwatch
from pyTooling.Warning             import WarningCollector

if TYPE_CHECKING:  # pragma: no cover
	# Only this directive needs a package index, so the model is imported when the configuration declares an
	# entrypoint rather than when the extension is loaded - otherwise every documentation build using any of these
	# roles would need the 'pypi' extra.
	from sphinx.config               import Config
	from packaging.requirements      import Requirement
	from pyTooling.Dependency.Python import LicenseOverrides, Project, PythonPackageDependencyGraph
	from pyTooling.Dependency.Python import PythonPackageIndex, Release, RequirementsFile

from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip


#: URL of the package index the tables are built from, unless :file:`conf.py` names another.
DEFAULT_INDEX_URL = "https://pypi.org"

#: URL of that index's JSON API.
DEFAULT_API_URL = "https://pypi.org/pypi/"

#: Levels of sub-dependencies rendered when the document doesn't say.
DEFAULT_DEPTH = 1

#: Prefix every configuration value of this extension carries in :file:`conf.py`.
CONFIG_PREFIX = "pyTooling_dependency"

#: What Sphinx accepts as the rebuild condition of a configuration value - the one this extension uses.
_ConfigRebuild = Literal["env"]

#: The configuration values this directive adds to :file:`conf.py`, as ``name: (default, rebuild, types)``.
#:
#: ``requirements`` maps an identifier to what it names - ``{"file": <path>}`` or ``{"package": <name>[extra]}``;
#: the other three are build-wide, because one package index is queried per build and one override file answers for
#: it. All four are ``"env"``-rebuilt: changing any of them changes every table.
CONFIG_VALUES: dict[str, tuple[Any, _ConfigRebuild, Any]] = {
	f"{CONFIG_PREFIX}_requirements": ({},                 "env", dict),
	f"{CONFIG_PREFIX}_licenses":     (None,               "env", (str, Path)),
	f"{CONFIG_PREFIX}_index_url":    (DEFAULT_INDEX_URL,  "env", str),
	f"{CONFIG_PREFIX}_api_url":      (DEFAULT_API_URL,    "env", str),
}

_logger = logging.getLogger(__name__)

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

	_identifier:   str                               #: Name the documents refer to this entrypoint by.
	_files:        tuple[Path, ...]                  #: The requirements file and every file it includes, if any.
	_packageName:  Nullable[str]                     #: Name of the package to read the requirements of, if any.
	_extra:        Nullable[str]                     #: Extra of that package whose requirements are wanted.
	_requirements: Nullable[dict[str, Requirement]]  #: The resolved requirements, by canonical package name.

	def __init__(
		self,
		identifier: str,
		files: tuple[Path, ...] = (),
		packageName: Nullable[str] = None,
		extra: Nullable[str] = None,
		requirements: Nullable[dict[str, Requirement]] = None
	) -> None:
		"""
		Describe one entrypoint.

		:param identifier:   Name the documents refer to this entrypoint by.
		:param files:        The requirements file and every file it includes, for a file entrypoint.
		:param packageName:  Name of the package, for a package entrypoint.
		:param extra:        Extra of that package whose requirements are wanted.
		:param requirements: The requirements, if they are known already.
		"""
		self._identifier = identifier
		self._files = files
		self._packageName = packageName
		self._extra = extra
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
	def PackageName(self) -> Nullable[str]:
		"""
		Name of the package this entrypoint reads the requirements of.

		:returns: The package's name, or ``None`` for a file entrypoint.
		"""
		return self._packageName

	@readonly
	def Extra(self) -> Nullable[str]:
		"""
		Extra of the package whose requirements are wanted.

		:returns: The extra's name, or ``None`` if the package's own requirements are wanted.
		"""
		return self._extra

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
		source = str(self._files[0]) if len(self._files) > 0 else f"{self._packageName}[{self._extra}]"

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
	_downloads:   int                               #: Number of requests sent to the package index.
	_seconds:     float                             #: Time spent waiting for the package index, in seconds.
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
		self._downloads = 0
		self._seconds = 0.0
		self._unresolved = set()

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
	def Downloads(self) -> int:
		"""
		Number of requests sent to the package index.

		:returns: Number of requests sent.
		"""
		return self._downloads

	@readonly
	def Seconds(self) -> float:
		"""
		Time spent waiting for the package index, in seconds.

		:returns: Seconds spent on the index.
		"""
		return self._seconds

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
		from pyTooling.Dependency.Python import LazyLoaderState

		if packageName in self._projects:
			return self._projects[packageName]

		with Stopwatch() as stopwatch:
			project: Nullable[Project]
			try:
				project = self.Index.DownloadProject(packageName, LazyLoaderState.PartiallyLoaded)
			except Exception:
				project = None

		self._downloads += 1
		self._seconds += stopwatch.Duration
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
		key = f"{release.Package.Name}=={release.Version}"
		if key in self._detailed:
			return release if key not in self._undescribed else None

		with Stopwatch() as stopwatch:
			warnings: list[Any] = []
			with WarningCollector(warnings):
				try:
					release.DownloadDetails()
				except Exception:
					self._undescribed.add(key)

		self._downloads += 1
		self._seconds += stopwatch.Duration
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

	:param configuration:  Value of ``pyTooling_dependency_requirements``.
	:param confDirectory:  Directory :file:`conf.py` lives in; relative paths are resolved against it.
	:returns:              Every declared entrypoint, by its identifier.
	:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the configuration is malformed, or a
	  requirements file can't be read.
	"""
	from pyTooling.Dependency.Python import RequirementsFile

	if not isinstance(configuration, dict):
		raise SphinxExtensionError(
			f"conf.py: {CONFIG_PREFIX}_requirements: Expected a dictionary, got {type(configuration).__name__}."
		)

	entrypoints: dict[str, Entrypoint] = {}
	for identifier, declaration in configuration.items():
		location = f"conf.py: {CONFIG_PREFIX}_requirements:[{identifier}]"

		if not isinstance(declaration, dict):
			raise SphinxExtensionError(f"{location}: Expected a dictionary, got {type(declaration).__name__}.")

		if (unknown := set(declaration) - {"file", "package"}) != set():
			raise SphinxExtensionError(
				f"{location}: Unknown field(s): {', '.join(sorted(unknown))}. Known are: file, package."
			)

		if ("file" in declaration) == ("package" in declaration):
			raise SphinxExtensionError(f"{location}: Exactly one of 'file' and 'package' has to be configured.")

		if (file := declaration.get("file", None)) is not None:
			path = Path(file)
			if not path.is_absolute():
				path = confDirectory / path

			try:
				requirementsFile = RequirementsFile(path)
			except Exception as cause:
				raise SphinxExtensionError(f"{location}.file: Requirements file '{path}' can't be read: {cause}") from cause

			files = tuple(included.Path for included in _Walk(requirementsFile))
			entrypoints[identifier] = Entrypoint(identifier, files=files, requirements=requirementsFile.Flatten())
		else:
			name, _, bracket = str(declaration["package"]).partition("[")
			entrypoints[identifier] = Entrypoint(
				identifier,
				packageName=name.strip(),
				extra=bracket.rstrip("]").strip() or None
			)

	return entrypoints


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
	if len(declarations := getattr(config, f"{CONFIG_PREFIX}_requirements", {})) == 0:
		return

	confDirectory = Path(sphinx.confdir)

	try:
		from pyTooling.Dependency.Python import LicenseOverrides
	except MissingDependencyError as cause:  # pragma: no cover
		raise SphinxExtensionError(
			f"conf.py: {CONFIG_PREFIX}_requirements: Querying a package index needs the 'pypi' extra: "
			f"pip install pyTooling[pypi]"
		) from cause

	overrides = LicenseOverrides()
	if (licenseFile := getattr(config, f"{CONFIG_PREFIX}_licenses", None)) is not None:
		path = Path(licenseFile)
		if not path.is_absolute():
			path = confDirectory / path

		try:
			overrides = LicenseOverrides.FromFile(path)
		except Exception as cause:
			raise SphinxExtensionError(
				f"conf.py: {CONFIG_PREFIX}_licenses: License override file '{path}' can't be read: {cause}"
			) from cause

	_COLLECTORS[id(sphinx)] = DependencyCollector(
		readEntrypoints(declarations, confDirectory),
		getattr(config, f"{CONFIG_PREFIX}_index_url", DEFAULT_INDEX_URL),
		getattr(config, f"{CONFIG_PREFIX}_api_url", DEFAULT_API_URL),
		overrides
	)


def _Walk(requirementsFile: RequirementsFile) -> Iterator[RequirementsFile]:
	"""
	Yield a requirements file and every file it includes, depth first.

	:param requirementsFile: The file to start at.
	:returns:                A generator of requirements files.
	"""
	yield requirementsFile
	for include in requirementsFile.Includes:
		yield from _Walk(include)


@export
class DependencyTable(BaseDirective):
	"""
	The ``dependency-table`` directive: an entrypoint's dependencies, rendered from the requirements.

	One argument, the identifier of an entrypoint declared in ``pyTooling_dependency_requirements``. ``:depth:``
	says how many levels of sub-dependencies to expand and ``:caption:`` puts a caption under the table; which
	package index is queried and which licenses are stated by hand are build-wide and configured in :file:`conf.py`.
	"""

	directiveName: str = "dependency-table"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        1      #: Number of required directive arguments: the entrypoint's identifier.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"caption": strip,
		"depth":   directives.nonnegative_int,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Resolve the named entrypoint against the package index and return its requirements as a table.

		:returns: A ``table`` node, or an error node when the entrypoint couldn't be resolved.
		"""
		identifier = self.arguments[0].strip()

		with Stopwatch() as stopwatch:
			try:
				collector = self._Collector()
				downloadsBefore = collector.Downloads
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
			f"{collector.Downloads - downloadsBefore} request(s), {stopwatch.Duration:.2f} s"
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
				f"No entrypoint is configured. Declare one in conf.py: {CONFIG_PREFIX}_requirements."
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
				f"Entrypoint '{identifier}' is not configured in conf.py: {CONFIG_PREFIX}_requirements. "
				f"Known are: {known}."
			)

		for file in entrypoint.Files:
			self.env.note_dependency(str(file))

		if (requirements := entrypoint.Requirements) is not None:
			return requirements

		packageName = cast(str, entrypoint.PackageName)
		if (project := collector.Project(packageName)) is None:
			raise SphinxExtensionError(f"Package '{packageName}' is unknown to the package index.")

		if (release := collector.Details(project.LatestRelease)) is None:
			raise SphinxExtensionError(f"The package index can't describe the latest release of '{packageName}'.")

		if (published := release.Requirements.get(entrypoint.Extra, None)) is None:
			known = ", ".join(sorted(str(key) for key in release.Requirements if key is not None))
			raise SphinxExtensionError(f"Package '{packageName}' has no extra '{entrypoint.Extra}'. Known are: {known}.")

		requirements = {canonicalize_name(requirement.name): requirement for requirement in published}
		entrypoint.CacheRequirements(requirements)

		return requirements

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
			columns=[("Package", 3), ("Version", 1), ("License", 2), ("Dependencies", 4)],
			identifier=identifier,
			classes=["dependency-table"]
		)
		tableGroup += (tableBody := nodes.tbody())

		depth = self.options.get("depth", DEFAULT_DEPTH)
		for name in sorted(requirements, key=str.lower):
			tableBody += self._CreateRow(requirements[name], collector, depth)

		table = cast(nodes.table, tableGroup.parent)
		if (caption := self.options.get("caption", None)) is not None:
			table.insert(0, nodes.title(caption, caption))

		return table

	def _CreateRow(self, requirement: Requirement, collector: DependencyCollector, depth: int) -> nodes.row:
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
		tableRow += nodes.entry("", nodes.literal(text=str(requirement.specifier) or "any"))
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
	def _PackageEntry(requirement: Requirement, project: Nullable[Project]) -> nodes.entry:
		"""
		Render the package's name, linked to where its sources live.

		:param requirement: The requirement naming the package.
		:param project:     The project, or ``None`` if the index doesn't know it.
		:returns:           The table entry.
		"""
		entry = nodes.entry()
		name = project.Name if project is not None else requirement.name

		if project is not None and project.RepositoryURL is not None:
			reference = nodes.reference("", name, refuri=str(project.RepositoryURL))
			entry += nodes.paragraph("", "", reference)
		else:
			entry += nodes.paragraph(text=name)

		return entry

	@staticmethod
	def _LicenseEntry(release: Nullable[Release]) -> nodes.entry:
		"""
		Render a release's license, linked to its text where one is known.

		A license that couldn't be resolved is shown as it was published, in italics, rather than left blank - the
		reader should see that the package index said *something*.

		:param release: The release to render the license of, or ``None``.
		:returns:       The table entry.
		"""
		entry = nodes.entry()

		if release is None:
			entry += nodes.paragraph("", "", nodes.emphasis(text="unknown"))
			return entry

		if len(release.Licenses) > 0:
			text = ", ".join(license.Identifier for license in release.Licenses)
			if release.LicenseURL is not None:
				entry += nodes.paragraph("", "", nodes.reference("", text, refuri=str(release.LicenseURL)))
			else:
				entry += nodes.paragraph(text=text)
		elif release.LicenseExpression != "":
			entry += nodes.paragraph("", "", nodes.emphasis(text=release.LicenseExpression))
		else:
			entry += nodes.paragraph("", "", nodes.emphasis(text="unknown"))

		return entry

	def _DependenciesEntry(
		self,
		release: Nullable[Release],
		collector: DependencyCollector,
		depth: int,
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

		if release is None or depth <= 0:
			entry += nodes.paragraph("", "", nodes.emphasis(text="not evaluated"))
			return entry

		requirements = [
			requirement for requirement in release.Requirements.get(None, [])
			if requirement.name.lower() not in visited
		]
		if len(requirements) == 0:
			entry += nodes.paragraph("", "", nodes.emphasis(text="none"))
			return entry

		entry += self._CreateBulletList(requirements, collector, depth - 1, visited)

		return entry

	def _CreateBulletList(
		self,
		requirements: list[Requirement],
		collector: DependencyCollector,
		depth: int,
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
			specifier = str(requirement.specifier)
			item += nodes.paragraph(text=f"{requirement.name} {specifier}" if specifier != "" else requirement.name)

			if depth > 0:
				project = collector.Project(requirement.name)
				release = self._SelectRelease(project, requirement, collector)
				if release is not None:
					nested = [
						nestedRequirement for nestedRequirement in release.Requirements.get(None, [])
						if nestedRequirement.name.lower() not in visited
					]
					if len(nested) > 0:
						item += self._CreateBulletList(
							nested, collector, depth - 1, visited | {requirement.name.lower()}
						)

			bulletList += item

		return bulletList


def reportBuildTime(app: Sphinx, exception: Nullable[Exception]) -> None:
	"""
	Report what querying the package index cost this build.

	The tables are fetched live, so this is the number to look at before deciding what a cache would be worth. The
	packages whose license had to be guessed at - or couldn't be - are named too, because that is the list the
	override file has to answer for.

	:param app:       The Sphinx application that finished building.
	:param exception: The exception that ended the build, or ``None`` if it succeeded.
	"""
	if (collector := _COLLECTORS.pop(id(app), None)) is None or collector.Downloads == 0:
		return

	_logger.info(
		f"[dependency-table] {collector.Downloads} request(s) to the package index, "
		f"{collector.Seconds:.2f} s in total."
	)

	if len(unresolved := collector.UnresolvedLicenses) > 0:
		_logger.warning(
			f"[dependency-table] {len(unresolved)} package(s) need a license override: "
			f"{', '.join(sorted(unresolved))}."
		)
