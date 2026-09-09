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
A Sphinx directive rendering a project's badges.

A landing page states which badges it shows; **where they come from is not a per-project decision**, and today it is
written out as one anyway. Every project carries a :file:`doc/shields.inc` of some 170 lines declaring the same 17
badges twice - once as SVG for HTML and once as PNG for LaTeX - and every :file:`index.rst` repeats the list twice
more, in an ``.. only:: html`` block and an ``.. only:: latex`` block. The URLs differ between the projects in an
organization, a repository and a package name; nothing else.

This directive says the same thing in the lines that actually differ:

.. code-block:: ReST

   .. shields::

      github, src-license, ghp-doc, doc-license
      pypi-tag, pypi-status, pypi-python
      gha-test, lib-status, codacy-quality, codacy-coverage, codecov-coverage

**The content is the layout**: badges appear in the order written, and a new line starts a new row. The identifiers
that fill the URLs are stated once in :file:`conf.py` under :data:`CONFIG_NAME`, because they are the same on every
page of a project.

.. rubric:: HTML and LaTeX

Both variants are emitted, each wrapped in the same :rst:dir:`only` node the hand-written blocks used - so the
builder selects between them exactly as before, and no custom writer is involved. What a document no longer has to
know is that HTML wants ``img.shields.io`` and LaTeX wants ``raster.shields.io``, which is the one thing the
hand-written pairs get wrong: an SVG reaching a LaTeX build is an image the PDF cannot embed.

.. seealso::

   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension this belongs to, and what else it brings.
"""
from typing                                    import Any, Optional as Nullable
from urllib.parse                              import quote

from docutils                                  import nodes
from sphinx.addnodes                           import only
from sphinx.application                        import Sphinx
from sphinx.config                             import Config

from pyTooling.Decorators                      import export, readonly
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip


__all__ = [
	"SVG_HOST", "RASTER_HOST", "BADGE_HEIGHT", "CONFIG_NAME", "CONFIG_VALUES", "DEFAULT_SETTINGS", "SHIELDS"
]

#: Host serving a badge as SVG, which is what an HTML build embeds.
SVG_HOST = "https://img.shields.io"

#: Host serving the same badge rasterized, which is what a LaTeX build needs - a PDF cannot embed the SVG.
RASTER_HOST = "https://raster.shields.io"

#: Height every badge is scaled to. Unitless, which docutils reads as pixels - written the way the hand-made
#: ``:height: 22`` was, so the rendered HTML is the same attribute rather than an equivalent ``style``.
BADGE_HEIGHT = 22

#: Name of the configuration value holding a project's identifiers, read from :file:`conf.py`.
CONFIG_NAME = "pyTooling_Shields"

#: Settings that are the same in every project, or that follow from another one, and that :file:`conf.py` may omit.
DEFAULT_SETTINGS = {
	"Workflow":            "Pipeline.yml",
	"Branch":              "main",
	"DocumentationLicense": "CC-BY 4.0",
	"Gitter":              "hdl/community",
}

#: The configuration value this module registers with Sphinx.
CONFIG_VALUES: dict[str, tuple[Any, str, Any]] = {
	CONFIG_NAME: ({}, "env", dict),
}


@export
class Shield(metaclass=ExtendedType, slots=True):
	"""
	One badge: where its image comes from, what it links to, and what a screen reader is told.

	The image is stated as the part of the URL **after** the host, because the host is the only difference between
	the SVG an HTML build embeds and the PNG a LaTeX build needs. Both URLs and both targets are formatted from the
	project's settings, so a placeholder such as ``{GitHubOrganization}`` is filled per project rather than per
	document.
	"""

	_alternativeText: str            #: What the image says when it can't be shown.
	_path:            str            #: Path and query on the badge host, with placeholders to format.
	_target:          Nullable[str]  #: What the badge links to; ``None`` for a badge that links nowhere.
	_latexTarget:     Nullable[str]  #: Target for a LaTeX build, where a link relative to the HTML output is useless.

	def __init__(
		self,
		alternativeText: str,
		path: str,
		target: Nullable[str] = None,
		latexTarget: Nullable[str] = None
	) -> None:
		"""
		Describe a badge.

		:param alternativeText: What the image says when it can't be shown.
		:param path:            Path and query on the badge host, with placeholders to format.
		:param target:          Optional, what the badge links to.
		:param latexTarget:     Optional, a target replacing :paramref:`target` in a LaTeX build - a page-relative
		                        link resolves against the HTML output and means nothing in a PDF.
		"""
		self._alternativeText = alternativeText
		self._path = path
		self._target = target
		self._latexTarget = latexTarget

	@readonly
	def AlternativeText(self) -> str:
		"""
		Read-only property to access what the image says when it can't be shown.

		:returns: The badge's alternative text.
		"""
		return self._alternativeText

	def ImageURL(self, settings: dict[str, str], latex: bool) -> str:
		"""
		Format the badge's image URL.

		:param settings: The project's identifiers, which the path's placeholders name.
		:param latex:    Whether the URL is for a LaTeX build, which needs the rasterized badge.
		:returns:        The complete URL of the badge image.
		"""
		return f"{RASTER_HOST if latex else SVG_HOST}/{self._path.format(**settings)}"

	def TargetURL(self, settings: dict[str, str], latex: bool) -> Nullable[str]:
		"""
		Format what the badge links to.

		:param settings: The project's identifiers, which the target's placeholders name.
		:param latex:    Whether the target is for a LaTeX build.
		:returns:        The complete target URL, or ``None`` when the badge links nowhere.
		"""
		target = (self._latexTarget or self._target) if latex else self._target

		return target.format(**settings) if target is not None else None


#: Every badge this directive knows, keyed by the identifier a document writes.
#:
#: The placeholders are the keys of the project's settings, plus the three derived in
#: :func:`prepareSettings`. ``GitHub`` is written ``GitHub.com`` in a target and ``github`` inside a shields.io path,
#: which is why the literal appears in both spellings rather than as a setting.
SHIELDS: dict[str, Shield] = {
	"github": Shield(
		"Sourcecode on GitHub",
		"badge/{GitHubOrganization}-{GitHubRepository}-63bf7f?longCache=true&style=flat-square&longCache=true"
		"&logo=GitHub",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}"
	),
	"src-license": Shield(
		"Code license",
		"pypi/l/{PyPI}?longCache=true&style=flat-square&logo=Apache&label=code",
		"Code-License.html",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/blob/{Branch}/LICENSE.md"
	),
	"doc-license": Shield(
		"Documentation License",
		"badge/doc-{DocumentationLicenseBadge}-green?longCache=true&style=flat-square&logo=CreativeCommons"
		"&logoColor=fff",
		"License.html",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/blob/{Branch}/doc/License.rst"
	),
	"ghp-doc": Shield(
		"Documentation - Read Now!",
		"website?longCache=true&style=flat-square&label={PagesLabel}&logo=GitHub&logoColor=fff"
		"&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url={PagesURL}",
		"https://{GitHubOrganization}.github.io/{GitHubRepository}/"
	),
	"tag": Shield(
		"GitHub tag (latest SemVer incl. pre-release)",
		"github/v/tag/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=GitHub"
		"&include_prereleases",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/tags"
	),
	"date": Shield(
		"GitHub release date",
		"github/release-date/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=GitHub",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/releases"
	),
	"gha-test": Shield(
		"GitHub Workflow - Build and Test Status",
		"github/actions/workflow/status/{GitHubOrganization}/{GitHubRepository}/{Workflow}?branch={Branch}"
		"&longCache=true&style=flat-square&label=Build%20and%20Test&logo=GitHub%20Actions&logoColor=FFFFFF",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/actions/workflows/{Workflow}"
	),
	"codacy-quality": Shield(
		"Codacy - Quality",
		"codacy/grade/{Codacy}?longCache=true&style=flat-square&logo=codacy",
		"https://www.codacy.com/gh/{GitHubOrganization}/{GitHubRepository}"
	),
	"codacy-coverage": Shield(
		"Codacy - Line Coverage",
		"codacy/coverage/{Codacy}?longCache=true&style=flat-square&logo=codacy",
		"https://www.codacy.com/gh/{GitHubOrganization}/{GitHubRepository}"
	),
	"codecov-coverage": Shield(
		"Codecov - Branch Coverage",
		"codecov/c/github/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=Codecov",
		"https://codecov.io/gh/{GitHubOrganization}/{GitHubRepository}"
	),
	"lib-status": Shield(
		"Libraries.io status for latest release",
		"librariesio/release/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://libraries.io/github/{GitHubOrganization}/{GitHubRepository}"
	),
	"lib-rank": Shield(
		"Libraries.io SourceRank",
		"librariesio/sourcerank/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://libraries.io/github/{GitHubOrganization}/{GitHubRepository}/sourcerank"
	),
	"lib-dep": Shield(
		"Dependent repos (via libraries.io)",
		"librariesio/dependent-repos/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/network/dependents"
	),
	"pypi-tag": Shield(
		"PyPI - Tag",
		"pypi/v/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072",
		"https://pypi.org/project/{PyPI}/"
	),
	"pypi-status": Shield(
		"PyPI - Status",
		"pypi/status/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072"
	),
	"pypi-python": Shield(
		"PyPI - Python Version",
		"pypi/pyversions/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072"
	),
	"gitter": Shield(
		"Chat on gitter",
		"badge/chat-on%20gitter-4db797?longCache=true&style=flat-square&logo=gitter&logoColor=e8ecef",
		"https://gitter.im/{Gitter}"
	),
}


@export
def prepareSettings(sphinx: Sphinx, config: Config) -> None:
	"""
	Call-back for Sphinx' ``config-inited`` event, completing the settings a project stated.

	``GitHub`` is written as ``<organization>/<repository>`` and split here, ``PyPI`` defaults to the repository's
	name, and the three values the badge URLs need percent-encoded are derived rather than asked for.

	A project that states nothing is left alone: the configuration value exists for every project enabling the
	extension, and only the ones actually writing :rst:dir:`shields` have to fill it. Such a project is reported by
	the directive, on the page that used it, rather than by a build that fails before reading a document.

	:param sphinx:                The Sphinx application.
	:param config:                The configuration, after :file:`conf.py` was read.
	:raises SphinxExtensionError: If ``GitHub`` is stated but isn't ``<organization>/<repository>``.
	"""
	if not (stated := dict(getattr(config, CONFIG_NAME, None) or {})):
		return

	settings = dict(DEFAULT_SETTINGS) | stated

	if (gitHub := settings.get("GitHub", None)) is None:
		raise SphinxExtensionError(f"shields: '{CONFIG_NAME}' states no 'GitHub' as '<organization>/<repository>'.")
	elif gitHub.count("/") != 1:
		raise SphinxExtensionError(
			f"shields: '{CONFIG_NAME}[\"GitHub\"]' is '{gitHub}', not '<organization>/<repository>'."
		)

	settings["GitHubOrganization"], settings["GitHubRepository"] = gitHub.split("/")
	settings.setdefault("PyPI", settings["GitHubRepository"])

	organization, repository = settings["GitHubOrganization"], settings["GitHubRepository"]
	settings["PagesLabel"] = quote(f"{organization}.github.io/{repository}", safe="")
	settings["PagesURL"] = quote(f"https://{organization}.github.io/{repository}/index.html", safe="")
	settings["DocumentationLicenseBadge"] = settings["DocumentationLicense"].replace("-", "--").replace(" ", "%20")

	setattr(config, CONFIG_NAME, settings)


@export
class Shields(BaseDirective):
	"""
	The ``shields`` directive: a project's badges, in rows.

	The content is the layout - one line per row, identifiers separated by commas - and
	:data:`SHIELDS` is what the identifiers name. ``:class:`` puts additional CSS classes on the rows.
	"""

	directiveName: str = "shields"  #: Name the directive is invoked by.

	has_content =               True   #: A boolean; ``True`` if content is allowed.
	required_arguments =        0      #: Number of required directive arguments.
	optional_arguments =        0      #: Number of optional arguments after the required ones.
	final_argument_whitespace = False  #: A boolean; ``True`` if the last argument may contain spaces.
	# docutils declares 'option_spec' on 'Directive' and 'BaseDirective' assigns it, so mypy calls every
	# spelling of this override a conflict with one of them
	#: Mapping of option names to validator functions.
	option_spec: dict[str, Any] = {  # type: ignore[misc]
		"class": strip,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Render the badges named in the content, once for HTML and once for LaTeX.

		:returns: Two ``only`` nodes, or the message of whatever the content got wrong.
		"""
		try:
			rows = self._ParseRows()
			settings = self._Settings()
		except SphinxExtensionError as cause:
			return [self.state.document.reporter.error(f"{self.directiveName}: {cause}", line=self.lineno)]

		classes = ["shields"] + self.options.get("class", "").split()

		return [self._Only("html", rows, settings, classes), self._Only("latex", rows, settings, classes)]

	def _Settings(self) -> dict[str, str]:
		"""
		Return the project's identifiers, as :func:`prepareSettings` completed them.

		:returns:                     The settings filling the badge URLs.
		:raises SphinxExtensionError: If :file:`conf.py` states none - which is only an error here, where a document
		                              asked for a badge that cannot be addressed without them.
		"""
		settings: dict[str, str] = getattr(self.env.config, CONFIG_NAME, None) or {}
		if "GitHubOrganization" not in settings:
			raise SphinxExtensionError(
				f"'{CONFIG_NAME}' isn't set in 'conf.py'. It needs at least "
				f"{CONFIG_NAME} = {{\"GitHub\": \"<organization>/<repository>\"}}."
			)

		return settings

	def _ParseRows(self) -> list[list[str]]:
		"""
		Read the content: one row per line, identifiers separated by commas.

		:returns:                     The identifiers, grouped into the rows they were written in.
		:raises SphinxExtensionError: If the content is empty, or names a badge :data:`SHIELDS` doesn't know.
		"""
		rows = []
		for line in self.content:
			if (identifiers := [identifier.strip() for identifier in line.split(",") if identifier.strip()]):
				rows.append(identifiers)

		if not rows:
			raise SphinxExtensionError("The directive's content names no badge.")

		for identifier in (identifier for row in rows for identifier in row):
			if identifier not in SHIELDS:
				known = ", ".join(sorted(SHIELDS))
				raise SphinxExtensionError(f"'{identifier}' is not a known badge. Known are: {known}.")

		return rows

	def _Only(self, expression: str, rows: list[list[str]], settings: dict[str, str], classes: list[str]) -> only:
		"""
		Build one builder-specific variant of the badges.

		:param expression: The ``only`` expression selecting the builder, ``html`` or ``latex``.
		:param rows:       The identifiers, grouped into rows.
		:param settings:   The project's identifiers, filling the URLs.
		:param classes:    CSS classes to put on the block.
		:returns:          An ``only`` node holding a line per row.
		"""
		latex = expression == "latex"
		node = only("", expr=expression)
		node += (block := nodes.line_block(classes=classes))

		for row in rows:
			block += (line := nodes.line())
			for identifier in row:
				line += self._Badge(SHIELDS[identifier], settings, latex)

		return node

	@staticmethod
	def _Badge(shield: Shield, settings: dict[str, str], latex: bool) -> nodes.Node:
		"""
		Build one badge: an image, wrapped in a reference when it links somewhere.

		:param shield:   The badge to build.
		:param settings: The project's identifiers, filling the URLs.
		:param latex:    Whether this is the LaTeX variant.
		:returns:        The image, or the reference holding it.
		"""
		image = nodes.image(
			"",
			uri=shield.ImageURL(settings, latex),
			alt=shield.AlternativeText,
			height=str(BADGE_HEIGHT)
		)

		if (target := shield.TargetURL(settings, latex)) is None:
			return image

		reference = nodes.reference("", refuri=target)
		reference += image

		return reference
