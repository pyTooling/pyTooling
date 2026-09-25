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
"""
A Sphinx directive rendering a project's badges.

A landing page shows where a project lives, how it is licensed, whether it builds and where it is published, as a
few rows of `shields.io <https://shields.io/>`__ badges. The directive states the project's coordinates as options
and the badges as its content:

.. code-block:: ReST

   .. shields::
      :github:                pyTooling/pyTooling
      :pypi:                  pyTooling
      :codacy:                08ef744c0b70490289712b02a7a4cebe
      :source-license:        github:LICENSE.md
      :documentation-license: CC-BY-4.0 github:doc/License.rst
      :github-action:         Pipeline.yml@main
      :documentation:         github-pages

      github, src-license, ghp-doc, doc-license
      pypi-tag, pypi-status, pypi-python
      github-action, lib-status, codacy-quality, codacy-coverage, codecov-coverage

**The content is the layout**: badges appear in the order written, and a new line starts a new row. A badge needs
only the options its URLs are made of - :data:`SHIELDS` names them per badge - so a project states what its badges
use and nothing else.

.. rubric:: Links

``:source-license:`` and ``:documentation-license:`` link to where the license is written:

* ``github:<path>`` is a file in the repository ``:github:`` names, on its default branch.
* ``http://…`` or ``https://…`` is used as written.

.. rubric:: Licenses

PyPI reports a package's license, and GitHub a repository's, so ``:source-license:`` needs only the link - the badge
asks PyPI when ``:pypi:`` is stated, and GitHub otherwise. An SPDX expression before the link replaces what they
report. Nothing reports a documentation's license, so ``:documentation-license:`` states it
first. Both are parsed with :meth:`~pyTooling.Licensing.LicenseExpression.Parse`, so a license outside the SPDX list
is written as ``LicenseRef-<name>``.

.. rubric:: HTML and LaTeX

Both variants are emitted, each wrapped in an :rst:dir:`only` node: HTML embeds the SVG from ``img.shields.io``,
LaTeX the PNG from ``raster.shields.io``, because a PDF cannot embed an SVG.

.. seealso::

   :ref:`DOC/Sphinx/Shields`
      |rarr| The directive's options and badges, with a rendered example.
   :mod:`pyTooling.Documentation.Sphinx`
      |rarr| The extension this belongs to, and what else it brings.
"""
from typing                                    import Any, Iterable, Optional as Nullable
from urllib.parse                              import quote

from docutils                                  import nodes
from sphinx.addnodes                           import only

from pyTooling.Common                          import getFullyQualifiedName
from pyTooling.Decorators                      import export, readonly
from pyTooling.Licensing                       import BaseLicense, LicenseExpression, LicenseExpressionError
from pyTooling.MetaClasses                     import ExtendedType
from pyTooling.Documentation.Sphinx.Directives import BaseDirective, SphinxExtensionError, strip


__all__ = ["SHIELDS_SERVICE_SVG", "SHIELDS_SERVICE_PNG", "BADGE_HEIGHT", "SHIELDS"]

#: Host serving a badge as SVG, which is what an HTML build embeds.
SHIELDS_SERVICE_SVG = "https://img.shields.io"

#: Host serving the same badge rasterized, which is what a LaTeX build needs - a PDF cannot embed the SVG.
SHIELDS_SERVICE_PNG = "https://raster.shields.io"

#: Height every badge is scaled to, in pixels.
BADGE_HEIGHT = 22


@export
class Shield(metaclass=ExtendedType, slots=True):
	"""
	One badge: where its image comes from, what it links to, what a screen reader is told, and which of the
	directive's options it is made of.

	The image is stated as the part of the URL **after** the host, because the host is the only difference between
	the SVG an HTML build embeds and the PNG a LaTeX build needs. Image and target are formatted from the settings the
	directive derives from its options, so a placeholder such as ``{GitHubOrganization}`` is filled per page.
	"""

	_alternativeText: str              #: What the image says when it can't be shown.
	_path:            str              #: Path and query on the badge host, with placeholders to format.
	_target:          Nullable[str]    #: What the badge links to; ``None`` for a badge that links nowhere.
	_options:         tuple[str, ...]  #: Names of the directive's options the badge is made of.

	def __init__(
		self,
		alternativeText: str,
		path: str,
		target: Nullable[str] = None,
		options: Nullable[Iterable[str]] = None
	) -> None:
		"""
		Describe a badge.

		:param alternativeText: What the image says when it can't be shown.
		:param path:            Path and query on the badge host, with placeholders to format.
		:param target:          Optional, what the badge links to.
		:param options:         Optional, names of the directive's options the badge is made of.
		:raises ValueError:     If parameter 'alternativeText' or 'path' is None.
		:raises TypeError:      If parameter 'alternativeText', 'path' or 'target' is not a string.
		"""
		if alternativeText is None:
			raise ValueError("Parameter 'alternativeText' is None.")
		elif not isinstance(alternativeText, str):
			ex = TypeError("Parameter 'alternativeText' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alternativeText)}'.")
			raise ex

		if path is None:
			raise ValueError("Parameter 'path' is None.")
		elif not isinstance(path, str):
			ex = TypeError("Parameter 'path' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		if target is not None and not isinstance(target, str):
			ex = TypeError("Parameter 'target' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(target)}'.")
			raise ex

		self._alternativeText = alternativeText
		self._path =            path
		self._target =          target
		self._options =         () if options is None else tuple(options)

	@readonly
	def AlternativeText(self) -> str:
		"""
		Read-only property to access what the image says when it can't be shown.

		:returns: The badge's alternative text.
		"""
		return self._alternativeText

	@readonly
	def Options(self) -> tuple[str, ...]:
		"""
		Read-only property to access the names of the directive's options the badge is made of.

		:returns: The option names, without colons.
		"""
		return self._options

	def ImageURL(self, settings: dict[str, str], latex: bool) -> str:
		"""
		Format the badge's image URL.

		:param settings: The settings derived from the directive's options, which the path's placeholders name.
		:param latex:    Whether the URL is for a LaTeX build, which needs the rasterized badge.
		:returns:        The complete URL of the badge image.
		"""
		host = SHIELDS_SERVICE_PNG if latex else SHIELDS_SERVICE_SVG

		return f"{host}/{self._path.format_map(settings)}"

	def TargetURL(self, settings: dict[str, str]) -> Nullable[str]:
		"""
		Format what the badge links to.

		:param settings: The settings derived from the directive's options, which the target's placeholders name.
		:returns:        The complete target URL, or ``None`` when the badge links nowhere.
		"""
		if self._target is None:
			return None

		return self._target.format_map(settings)


#: Every badge the directive knows, keyed by the identifier its content names.
SHIELDS: dict[str, Shield] = {
	"github": Shield(
		"Sourcecode on GitHub",
		"badge/{GitHubOrganization}-{GitHubRepository}-63bf7f?longCache=true&style=flat-square&longCache=true"
		"&logo=GitHub",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}",
		("github",)
	),
	"src-license": Shield(
		"Code license",
		"{SourceLicenseImage}?longCache=true&style=flat-square&label=code",
		"{SourceLicenseURL}",
		("source-license",)
	),
	"doc-license": Shield(
		"Documentation License",
		"badge/doc-{DocumentationLicenseBadge}-green?longCache=true&style=flat-square{DocumentationLicenseLogo}",
		"{DocumentationLicenseURL}",
		("documentation-license",)
	),
	"ghp-doc": Shield(
		"Documentation - Read Now!",
		"website?longCache=true&style=flat-square&label={DocumentationLabel}{DocumentationLogo}"
		"&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url={DocumentationQuery}",
		"{DocumentationURL}",
		("documentation",)
	),
	"tag": Shield(
		"GitHub tag (latest SemVer incl. pre-release)",
		"github/v/tag/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=GitHub"
		"&include_prereleases",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/tags",
		("github",)
	),
	"date": Shield(
		"GitHub release date",
		"github/release-date/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=GitHub",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/releases",
		("github",)
	),
	"github-action": Shield(
		"GitHub Workflow - Build and Test Status",
		"github/actions/workflow/status/{GitHubOrganization}/{GitHubRepository}/{Workflow}?{WorkflowBranch}"
		"longCache=true&style=flat-square&label=Build%20and%20Test&logo=GitHub%20Actions&logoColor=FFFFFF",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/actions/workflows/{Workflow}",
		("github", "github-action")
	),
	"codacy-quality": Shield(
		"Codacy - Quality",
		"codacy/grade/{Codacy}?longCache=true&style=flat-square&logo=codacy",
		"https://app.codacy.com/gh/{GitHubOrganization}/{GitHubRepository}/dashboard",
		("github", "codacy")
	),
	"codacy-coverage": Shield(
		"Codacy - Line Coverage",
		"codacy/coverage/{Codacy}?longCache=true&style=flat-square&logo=codacy",
		"https://app.codacy.com/gh/{GitHubOrganization}/{GitHubRepository}/dashboard",
		("github", "codacy")
	),
	"codecov-coverage": Shield(
		"Codecov - Branch Coverage",
		"codecov/c/github/{GitHubOrganization}/{GitHubRepository}?longCache=true&style=flat-square&logo=Codecov",
		"https://codecov.io/gh/{GitHubOrganization}/{GitHubRepository}",
		("github",)
	),
	"lib-status": Shield(
		"Libraries.io status for latest release",
		"librariesio/release/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://libraries.io/pypi/{PyPI}",
		("pypi",)
	),
	"lib-rank": Shield(
		"Libraries.io SourceRank",
		"librariesio/sourcerank/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://libraries.io/pypi/{PyPI}/sourcerank",
		("pypi",)
	),
	"lib-dep": Shield(
		"Dependent repos (via libraries.io)",
		"librariesio/dependent-repos/pypi/{PyPI}?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff",
		"https://GitHub.com/{GitHubOrganization}/{GitHubRepository}/network/dependents",
		("github", "pypi")
	),
	"pypi-tag": Shield(
		"PyPI - Tag",
		"pypi/v/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072",
		"https://pypi.org/project/{PyPI}/",
		("pypi",)
	),
	"pypi-status": Shield(
		"PyPI - Status",
		"pypi/status/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072",
		options=("pypi",)
	),
	"pypi-python": Shield(
		"PyPI - Python Version",
		"pypi/pyversions/{PyPI}?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072",
		options=("pypi",)
	),
	"gitter": Shield(
		"Chat on gitter",
		"badge/chat-on%20gitter-4db797?longCache=true&style=flat-square&logo=gitter&logoColor=e8ecef",
		"https://gitter.im/{Gitter}",
		("gitter",)
	),
}


@export
class Shields(BaseDirective):
	"""
	The ``shields`` directive: a project's badges, in rows.

	The options state the project's coordinates, the content names the badges - one line per row, identifiers
	separated by commas - and :data:`SHIELDS` is what the identifiers name. ``:class:`` puts additional CSS classes on
	the rows.
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
		"github":                strip,
		"pypi":                  strip,
		"codacy":                strip,
		"gitter":                strip,
		"source-license":        strip,
		"documentation-license": strip,
		"github-action":         strip,
		"documentation":         strip,
		"class":                 strip,
	}

	def run(self) -> list[nodes.Node]:
		"""
		Render the badges named in the content, once for HTML and once for LaTeX.

		:returns: Two ``only`` nodes, or the message of whatever the options or the content got wrong.
		"""
		try:
			rows = self._ParseRows(self.content)
			self._CheckOptions(rows, self.options)
			settings = self._Settings(self.options)
		except SphinxExtensionError as ex:
			return [self.state.document.reporter.error(f"{self.directiveName}: {ex}", line=self.lineno)]

		classes = ["shields"] + self.options.get("class", "").split()

		return [self._Only("html", rows, settings, classes), self._Only("latex", rows, settings, classes)]

	@staticmethod
	def _ParseRows(content: Iterable[str]) -> list[list[str]]:
		"""
		Read the content: one row per line, identifiers separated by commas.

		:param content:               The directive's content, line by line.
		:returns:                     The identifiers, grouped into the rows they were written in.
		:raises SphinxExtensionError: If the content is empty, or names a badge :data:`SHIELDS` doesn't know.
		"""
		rows = []
		for line in content:
			identifiers = [identifier.strip() for identifier in line.split(",") if identifier.strip() != ""]
			if len(identifiers) > 0:
				rows.append(identifiers)

		if len(rows) == 0:
			raise SphinxExtensionError("The directive's content names no badge.")

		for row in rows:
			for identifier in row:
				if identifier not in SHIELDS:
					known = ", ".join(sorted(SHIELDS))
					raise SphinxExtensionError(f"'{identifier}' is not a known badge. Known are: {known}.")

		return rows

	@staticmethod
	def _CheckOptions(rows: list[list[str]], options: dict[str, str]) -> None:
		"""
		Check that every badge named has the options it is made of.

		:param rows:                  The identifiers, grouped into rows.
		:param options:               The directive's options.
		:raises SphinxExtensionError: If a badge needs an option the directive doesn't state.
		"""
		for row in rows:
			for identifier in row:
				for option in SHIELDS[identifier].Options:
					if option not in options:
						raise SphinxExtensionError(f"Badge '{identifier}' needs option ':{option}:'.")

	@classmethod
	def _Settings(cls, options: dict[str, str]) -> dict[str, str]:
		"""
		Derive the values the badge URLs are formatted from.

		An option that isn't stated derives nothing; :meth:`_CheckOptions` ensures that no badge needing it is drawn.

		:param options:               The directive's options.
		:returns:                     The values, keyed by the placeholders :data:`SHIELDS` names.
		:raises SphinxExtensionError: If an option's value is malformed, or refers to ``:github:`` without it.
		"""
		settings: dict[str, str] = {}

		if (gitHub := options.get("github", None)) is not None:
			if gitHub.count("/") != 1:
				raise SphinxExtensionError(f"Option ':github:' is '{gitHub}', not '<organization>/<repository>'.")

			organization, repository = gitHub.split("/")
			settings["GitHubOrganization"] = organization
			settings["GitHubRepository"] = repository

		if (pypi := options.get("pypi", None)) is not None:
			settings["PyPI"] = pypi

		if (codacy := options.get("codacy", None)) is not None:
			settings["Codacy"] = codacy

		if (gitter := options.get("gitter", None)) is not None:
			settings["Gitter"] = gitter

		if (sourceLicense := options.get("source-license", None)) is not None:
			expression, link = cls._SplitLicense("source-license", sourceLicense)
			settings["SourceLicenseURL"] = cls._ResolveLink("source-license", link, settings)
			if expression is not None:
				settings["SourceLicenseImage"] = f"badge/code-{cls._EscapeBadgeText(str(expression))}-blue"
			elif "PyPI" in settings:
				settings["SourceLicenseImage"] = f"pypi/l/{settings['PyPI']}"
			else:
				settings["SourceLicenseImage"] = f"github/license/{cls._GitHubSlug('source-license', settings)}"

		if (documentationLicense := options.get("documentation-license", None)) is not None:
			expression, link = cls._SplitLicense("documentation-license", documentationLicense)
			if expression is None:
				raise SphinxExtensionError(
					"Option ':documentation-license:' states no license. Nothing reports a documentation's license, so "
					"it is written before the link: '<SPDX expression> <link>'."
				)

			settings["DocumentationLicenseURL"] = cls._ResolveLink("documentation-license", link, settings)
			settings["DocumentationLicenseBadge"] = cls._EscapeBadgeText(str(expression))
			identifiers = [term.Identifier for term in expression.IterateExpression() if isinstance(term, BaseLicense)]
			if all(identifier.startswith("CC") for identifier in identifiers):
				settings["DocumentationLicenseLogo"] = "&logo=CreativeCommons&logoColor=fff"
			else:
				settings["DocumentationLicenseLogo"] = ""

		if (gitHubAction := options.get("github-action", None)) is not None:
			workflow, _, branch = gitHubAction.partition("@")
			settings["Workflow"] = workflow
			settings["WorkflowBranch"] = "" if branch == "" else f"branch={quote(branch, safe='')}&"

		if (documentation := options.get("documentation", None)) is not None:
			if documentation == "github-pages":
				organization, repository = cls._GitHubSlug("documentation", settings).split("/")
				url = f"https://{organization}.github.io/{repository}/"
				logo = "&logo=GitHub&logoColor=fff"
			elif documentation.startswith(("http://", "https://")):
				url = documentation
				logo = "&logo=ReadTheDocs&logoColor=fff" if ".readthedocs." in documentation else ""
			else:
				raise SphinxExtensionError(
					f"Option ':documentation:' is '{documentation}', neither 'github-pages' nor an 'http(s)://' URL."
				)

			settings["DocumentationURL"] = url
			settings["DocumentationLabel"] = quote(url.split("://", 1)[1].rstrip("/"), safe="")
			settings["DocumentationQuery"] = quote(url, safe="")
			settings["DocumentationLogo"] = logo

		return settings

	@staticmethod
	def _SplitLicense(option: str, value: str) -> tuple[Nullable[LicenseExpression], str]:
		"""
		Split a license option into the license and the link, which is its last word.

		:param option:                The option's name, for the message.
		:param value:                 The option's value, ``[<SPDX expression> ]<link>``.
		:returns:                     The parsed license expression, or ``None`` if none is stated, and the link.
		:raises SphinxExtensionError: If the license isn't an SPDX license expression.
		"""
		words = value.rsplit(maxsplit=1)
		if len(words) == 1:
			return None, words[0]

		text, link = words
		try:
			expression = LicenseExpression.Parse(text)
		except LicenseExpressionError as cause:
			ex = SphinxExtensionError(f"Option ':{option}:' states '{text}', which isn't an SPDX license expression.")
			ex.add_note(str(cause))
			raise ex from cause

		return expression, link

	@classmethod
	def _ResolveLink(cls, option: str, link: str, settings: dict[str, str]) -> str:
		"""
		Resolve a link written as ``github:<path>`` or as a URL.

		:param option:                The option's name, for the message.
		:param link:                  The link as written.
		:param settings:              The settings derived so far, which hold the repository ``:github:`` names.
		:returns:                     The link's URL.
		:raises SphinxExtensionError: If the link is neither form, or is ``github:`` without ``:github:``.
		"""
		if link.startswith("github:"):
			return f"https://GitHub.com/{cls._GitHubSlug(option, settings)}/blob/HEAD/{link.removeprefix('github:')}"
		elif link.startswith(("http://", "https://")):
			return link

		raise SphinxExtensionError(f"Option ':{option}:' links to '{link}', neither 'github:<path>' nor a URL.")

	@staticmethod
	def _GitHubSlug(option: str, settings: dict[str, str]) -> str:
		"""
		Return the repository ``:github:`` names, for an option referring to it.

		:param option:                The option's name, for the message.
		:param settings:              The settings derived so far.
		:returns:                     ``<organization>/<repository>``.
		:raises SphinxExtensionError: If ``:github:`` isn't stated.
		"""
		if "GitHubOrganization" not in settings:
			raise SphinxExtensionError(f"Option ':{option}:' refers to the repository, which needs option ':github:'.")

		return f"{settings['GitHubOrganization']}/{settings['GitHubRepository']}"

	@staticmethod
	def _EscapeBadgeText(text: str) -> str:
		"""
		Escape text for a static badge's path, where ``-`` and ``_`` separate the badge's fields.

		:param text: The text to escape.
		:returns:    The text with ``-`` and ``_`` doubled and everything else a URL path can't hold percent-encoded.
		"""
		return quote(text.replace("-", "--").replace("_", "__"), safe="")

	def _Only(self, expression: str, rows: list[list[str]], settings: dict[str, str], classes: list[str]) -> only:
		"""
		Build one builder-specific variant of the badges.

		:param expression: The ``only`` expression selecting the builder, ``html`` or ``latex``.
		:param rows:       The identifiers, grouped into rows.
		:param settings:   The settings derived from the directive's options, filling the URLs.
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
		:param settings: The settings derived from the directive's options, filling the URLs.
		:param latex:    Whether this is the LaTeX variant.
		:returns:        The image, or the reference holding it.
		"""
		image = nodes.image(
			"",
			uri=shield.ImageURL(settings, latex),
			alt=shield.AlternativeText,
			height=str(BADGE_HEIGHT)
		)

		if (target := shield.TargetURL(settings)) is None:
			return image

		reference = nodes.reference("", refuri=target)
		reference += image

		return reference
