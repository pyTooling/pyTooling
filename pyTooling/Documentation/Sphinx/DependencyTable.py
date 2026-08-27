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
packages ``doc/requirements.txt`` requires, listed one that isn't required at all, and called Sphinx BSD-3-Clause
when it is BSD-2-Clause.

.. code-block:: rest

   .. dependency-table:: doc/requirements.txt
      :caption: Documentation dependencies

The argument is an **entrypoint** - a requirements file, or a package with an extra:

.. code-block:: rest

   .. dependency-table:: pyTooling[yaml]

**The data is fetched live** from the package index, once per build and shared between the tables of a build. That
costs real time, so every table reports what it spent, measured with a :class:`~pyTooling.Stopwatch.Stopwatch`, and
the build ends with the total - which is the number to look at before deciding what to cache.
"""
from pathlib                       import Path
from typing                        import Any, Iterator, Optional as Nullable, cast

from docutils                      import nodes
from docutils.parsers.rst          import directives
from sphinx.application            import Sphinx
from sphinx.util                   import logging

from packaging.requirements        import Requirement
from packaging.utils               import canonicalize_name

from pyTooling.Decorators          import export, readonly
from pyTooling.Dependency          import UnknownLicenseWarning
from pyTooling.Dependency.Python   import LazyLoaderState, LicenseOverrides, Project, PythonPackageDependencyGraph
from pyTooling.Dependency.Python   import PythonPackageIndex, Release, RequirementsFile
from pyTooling.MetaClasses         import ExtendedType
from pyTooling.Stopwatch           import Stopwatch
from pyTooling.Warning             import WarningCollector

from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip


#: URL of the package index a table is built from, unless the document names another.
DEFAULT_INDEX_URL = "https://pypi.org"

#: URL of that index's JSON API.
DEFAULT_API_URL = "https://pypi.org/pypi/"

#: Levels of sub-dependencies rendered when the document doesn't say.
DEFAULT_DEPTH = 1

_logger = logging.getLogger(__name__)

#: The collector of each running build, by the id of its Sphinx application.
#:
#: It can't live on the build environment, which Sphinx pickles between runs - an open HTTP session and the locks
#: guarding lazy loading are not picklable, and a cached view of a package index would be stale anyway.
_COLLECTORS: dict[int, "DependencyCollector"] = {}


@export
class DependencyCollector(metaclass=ExtendedType, slots=True):
	"""
	The package index a build queries, and what querying it cost.

	One collector is shared by every table of a build: a package required by two entrypoints is downloaded once, and
	the time is accumulated so the build can report a total. It exists because the alternative - a table that queries
	the index for itself - multiplies a documentation build's runtime by however many tables it has.
	"""

	_graph:      PythonPackageDependencyGraph      #: Graph the downloaded packages are collected in.
	_index:      PythonPackageIndex                #: The package index this build queries.
	_projects:   dict[str, Nullable[Project]]      #: Projects downloaded so far; ``None`` for an unknown package.
	_detailed:   set[str]                          #: Releases whose details were downloaded, as ``name==version``.
	_undescribed: set[str]                         #: Releases the index lists but can't describe.
	_downloads:  int                               #: Number of requests sent to the package index.
	_seconds:    float                             #: Time spent waiting for the package index, in seconds.
	_unresolved: set[str]                          #: Packages whose license the index couldn't answer for.

	def __init__(self, indexURL: str, apiURL: str, overrides: LicenseOverrides) -> None:
		"""
		Open a package index for this build.

		:param indexURL:  URL of the package index's website.
		:param apiURL:    URL of the package index's JSON API.
		:param overrides: Licenses stated by hand.
		"""
		self._graph = PythonPackageDependencyGraph("documentation")
		self._index = PythonPackageIndex("index", indexURL, apiURL, self._graph, overrides)
		self._projects = {}
		self._detailed = set()
		self._undescribed = set()
		self._downloads = 0
		self._seconds = 0.0
		self._unresolved = set()

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
		if packageName in self._projects:
			return self._projects[packageName]

		with Stopwatch() as stopwatch:
			try:
				project = self._index.DownloadProject(packageName, LazyLoaderState.PartiallyLoaded)
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
class DependencyTable(BaseDirective):
	"""
	The ``dependency-table`` directive: an entrypoint's dependencies, rendered from the requirements.

	One argument, the entrypoint - a path to a requirements file, relative to the documentation's source directory,
	or a package name with an optional extra. ``:depth:`` says how many levels of sub-dependencies to expand,
	``:licenses:`` names the override file, and ``:caption:`` puts a caption under the table.
	"""

	directiveName: str = "dependency-table"  #: Name the directive is invoked by.

	has_content =               False  #: A boolean; ``True`` if content is allowed.
	required_arguments =        1      #: Number of required directive arguments: the entrypoint.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"caption":   strip,
		"depth":     directives.nonnegative_int,
		"licenses":  strip,
		"index-url": strip,
		"api-url":   strip,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Resolve the entrypoint's requirements against the package index and return them as a table.

		:returns: A ``table`` node, or an error node when the entrypoint couldn't be read.
		"""
		entrypoint = self.arguments[0].strip()

		with Stopwatch() as stopwatch:
			try:
				collector = self._Collector()
				downloadsBefore = collector.Downloads
				requirements = self._ReadEntrypoint(entrypoint, collector)
				table = self._CreateTable(entrypoint, requirements, collector)
			except SphinxExtensionError as cause:
				return [self.state.document.reporter.error(
					f"{self.directiveName}: {cause}", line=self.lineno
				)]

		# what this table cost, not what the build has spent so far - a package another table already downloaded is
		# free here, and that is the point of sharing the collector
		_logger.info(
			f"[{self.directiveName}] {entrypoint}: {len(requirements)} package(s), "
			f"{collector.Downloads - downloadsBefore} request(s), {stopwatch.Duration:.2f} s"
		)

		return [table]

	def _Collector(self) -> DependencyCollector:
		"""
		Return the build's collector, opening the package index the first time a table asks for it.

		The collector belongs to the running application rather than to the directive, because a document with three
		tables would otherwise open three indexes and download the same packages three times. It deliberately does
		*not* live on the build environment: Sphinx pickles that between runs, and neither an open HTTP session nor a
		cached view of a package index survives being pickled - or should.

		:returns:                     The collector shared by every table of this build.
		:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the override file can't be read.
		"""
		if (collector := _COLLECTORS.get(id(self.env.app), None)) is not None:
			return collector

		overrides = LicenseOverrides()
		if (licenseFile := self.options.get("licenses", None)) is not None:
			path = Path(self.env.srcdir) / licenseFile
			try:
				overrides = LicenseOverrides.FromFile(path)
			except Exception as cause:
				raise SphinxExtensionError(f"License override file '{path}' can't be read: {cause}") from cause

		collector = DependencyCollector(
			self.options.get("index-url", DEFAULT_INDEX_URL),
			self.options.get("api-url", DEFAULT_API_URL),
			overrides
		)
		_COLLECTORS[id(self.env.app)] = collector

		return collector

	def _ReadEntrypoint(self, entrypoint: str, collector: DependencyCollector) -> dict[str, Requirement]:
		"""
		Read what an entrypoint requires.

		An entrypoint is either a requirements file - read with its ``-r`` includes followed - or a package with an
		optional extra, whose requirements are read from the index.

		:param entrypoint:            The entrypoint, as written in the document.
		:param collector:             The build's collector.
		:returns:                     Every required package, by its canonical name.
		:raises ~pyTooling.Documentation.Sphinx.Directives.SphinxExtensionError: If the entrypoint can't be read.
		"""
		if entrypoint.endswith(".txt"):
			path = Path(self.env.srcdir) / entrypoint
			if not path.exists():
				path = Path(self.env.srcdir).parent / entrypoint

			try:
				requirementsFile = RequirementsFile(path)
			except FileNotFoundError as cause:
				raise SphinxExtensionError(f"Requirements file '{entrypoint}' not found.") from cause

			self.env.note_dependency(str(path))
			for include in self._Walk(requirementsFile):
				self.env.note_dependency(str(include.Path))

			return requirementsFile.Flatten()

		name, _, bracket = entrypoint.partition("[")
		packageName = name.strip()
		extra: Nullable[str] = bracket.rstrip("]") or None

		if (project := collector.Project(packageName)) is None:
			raise SphinxExtensionError(f"Package '{packageName}' is unknown to the package index.")

		if (release := collector.Details(project.LatestRelease)) is None:
			raise SphinxExtensionError(f"The package index can't describe the latest release of '{packageName}'.")

		if (requirements := release.Requirements.get(extra, None)) is None:
			known = ", ".join(sorted(str(key) for key in release.Requirements if key is not None))
			raise SphinxExtensionError(f"Package '{packageName}' has no extra '{extra}'. Known are: {known}.")

		return {canonicalize_name(requirement.name): requirement for requirement in requirements}

	@staticmethod
	def _Walk(requirementsFile: RequirementsFile) -> Iterator[RequirementsFile]:
		"""
		Yield a requirements file and every file it includes, depth first.

		:param requirementsFile: The file to start at.
		:returns:                A generator of requirements files.
		"""
		yield requirementsFile
		for include in requirementsFile.Includes:
			yield from DependencyTable._Walk(include)

	def _CreateTable(
		self,
		entrypoint: str,
		requirements: dict[str, Requirement],
		collector: DependencyCollector
	) -> nodes.table:
		"""
		Render the requirements as a four-column table.

		:param entrypoint:   The entrypoint, used as the table's identifier.
		:param requirements: Every required package, by its canonical name.
		:param collector:    The build's collector.
		:returns:            The finished table.
		"""
		tableGroup = self._CreateSingleTableHeader(
			columns=[("Package", 3), ("Version", 1), ("License", 2), ("Dependencies", 4)],
			identifier=entrypoint,
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
			text = ", ".join(spdxLicense.SPDXIdentifier for spdxLicense in release.Licenses)
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
	if (collector := _COLLECTORS.pop(id(app), None)) is None:
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
