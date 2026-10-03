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
Unit tests for :mod:`pyTooling.Documentation.Sphinx.GitHubActions.Reference`, the directives summarizing a workflow.

Every testcase builds a small Sphinx project in a temporary directory - see
:class:`~tests.unit.SphinxExtension.GitHubActionsDomain.Project` - and checks the HTML and the warnings.
"""
from html                  import unescape
from re                    import findall, sub
from textwrap              import dedent, indent

from .GitHubActionsDomain  import Project


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


#: A reusable workflow: inputs with every kind of default, secrets, an output, a job asking for a permission and
#: running actions, a template of the documented repository, and a template of another repository.
PACKAGE = dedent("""\
	name: Package

	on:
	  workflow_call:
	    inputs:
	      package_name:
	        description: 'Name of the package.'
	        required: true
	        type: string
	      python_version:
	        description: 'Python version.'
	        required: false
	        default: '3.14'
	        type: string
	      pages_on:
	        description: 'Conditions.'
	        required: false
	        default: |
	          default-branch
	          release-tag
	        type: string
	      system_list:
	        required: false
	        default: 'ubuntu ubuntu-arm windows windows-arm macos macos-arm mingw64 ucrt64 clang64 mingw32 ucrt32 msys
	          ubuntu-24.04 windows-2025 macos-26'
	        type: string
	      dry_run:
	        required: false
	        default: false
	        type: boolean
	    outputs:
	      version:
	        description: 'Version of the package.'
	        value: ${{ jobs.Build.outputs.version }}
	    secrets:
	      PYPI_TOKEN:
	        description: 'Token for PyPI.'
	        required: true
	      CODECOV_TOKEN:
	        required: false

	jobs:
	  Build:
	    runs-on: ubuntu-26.04
	    permissions:
	      contents: read
	    outputs:
	      version: ${{ steps.version.outputs.version }}
	    steps:
	      - uses: actions/checkout@v6
	      - id: version
	        run: echo "version=1.0.0" >> "${GITHUB_OUTPUT}"
	# a comment at the start of a line, inside job 'Build'
	      - uses: actions/checkout@v6
	      - uses: ./.github/actions/Local

	  # the release
	  Release:
	    uses: owner/repo/.github/workflows/Tag.yml@r1
	    needs:
	      - Build

	  Notify:
	    uses: other/tools/.github/workflows/Notify.yml@v2
	    needs:
	      - Release
	""")

#: A template of the documented repository, asking for a higher permission than the calling workflow.
TAG = dedent("""\
	name: Tag

	on:
	  workflow_call:

	jobs:
	  Tag:
	    runs-on: ubuntu-26.04
	    permissions:
	      contents: write
	      actions:  read
	    steps:
	      - uses: actions/github-script@v8
	""")

#: A workflow without outputs and secrets, and no job asking for a permission.
MINIMAL = dedent("""\
	on:
	  workflow_call:
	    inputs:
	      name:
	        required: false
	        default: ''
	        type: string

	jobs:
	  Run:
	    runs-on: ubuntu-26.04
	    steps:
	      - run: echo
	""")

#: The start of a page documenting workflow 'Package'.
HEADER = ".. gha:workflow:: Package\n\nPackage\n#######\n\n"

#: The entries of every input of workflow 'Package' but 'dry_run'.
ENTRIES = dedent("""\
	.. gha:input:: package_name

	.. gha:input:: python_version

	.. gha:input:: pages_on

	.. gha:input:: system_list
""")


class ParameterTables(Project):
	PAGE = f"{HEADER}.. gha:parameter-table::\n\n.. gha:autoinputs::\n"

	def _table(self, html: str, kind: str) -> str:
		"""
		Cut a table out of a page.

		:param html: The page's HTML.
		:param kind: The kind of the table, as ``inputs``.
		:returns:    The table's HTML.
		"""
		start = html.index(f'gha-parameter-table gha-{kind}')
		return html[start:html.index("</table>", start)]

	def test_Inputs(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		self.assertEqual([], self._warningLines())
		table = self._table(self._html("Package"), "inputs")
		self.assertIn("<th class=\"head\">Parameter Name</th>", table)
		rows = table.split("<tr")[2:]
		self.assertEqual(5, len(rows))
		self.assertIn('href="#gha-input-Package.package_name"', rows[0])
		self.assertIn("<p>yes</p>", rows[0])
		self.assertIn("<p>— — — —</p>", rows[0])
		self.assertIn("<p>no</p>", rows[1])
		self.assertIn("<p>string</p>", rows[1])
		self.assertIn("<span class=\"pre\">'3.14'</span>", rows[1])
		self.assertIn("<p>boolean</p>", rows[4])
		self.assertIn("<span class=\"pre\">false</span>", rows[4])

	def test_ShortDefault(self) -> None:
		"""A multi-line default is shortened to its first line, a long default to 120 characters."""
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		table = self._table(self._html("Package"), "inputs")
		self.assertIn("<span class=\"pre\">'default-branch…'</span>", table)
		self.assertIn("<span class=\"pre\">ubuntu-24.04</span> <span class=\"pre\">windows-20…'</span>", table)

	def test_Secrets(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		table = self._table(self._html("Package"), "secrets")
		self.assertIn("<th class=\"head\">Token Name</th>", table)
		rows = table.split("<tr")[2:]
		self.assertEqual(2, len(rows))
		self.assertIn("<span class=\"pre\">PYPI_TOKEN</span>", rows[0])
		self.assertIn("<p>yes</p>", rows[0])
		self.assertIn("<p>string</p>", rows[0])
		self.assertIn("<p>no</p>", rows[1])

	def test_Outputs(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		table = self._table(self._html("Package"), "outputs")
		self.assertIn("<th class=\"head\">Result Name</th>", table)
		self.assertIn("<p>Version of the package.</p>", table)

	def test_Order(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		self.assertLess(html.index("gha-inputs"), html.index("gha-secrets"))
		self.assertLess(html.index("gha-secrets"), html.index("gha-outputs"))

	def test_Kinds(self) -> None:
		self._workflow("Package", PACKAGE)
		kinds = "parameter-table::\n   :kinds: outputs, inputs outputs\n"
		self._build({"Package": self.PAGE.replace("parameter-table::\n", kinds)})

		html = self._html("Package")
		self.assertEqual([], self._warningLines())
		self.assertEqual(1, html.count("gha-outputs"))
		self.assertLess(html.index("gha-outputs"), html.index("gha-inputs"))
		self.assertNotIn("gha-secrets", html)

	def test_KindsWithoutParameters(self) -> None:
		"""Only a kind named explicitly is shown when the workflow has none of it."""
		self._workflow("Package", MINIMAL)
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		self.assertIn("gha-inputs", html)
		self.assertNotIn("gha-outputs", html)

		self._build({"Package": self.PAGE.replace("parameter-table::\n", "parameter-table::\n   :kinds: outputs\n")})

		self.assertIn("<em>No outputs</em>", self._table(self._html("Package"), "outputs"))

	def test_UnknownKind(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE.replace("parameter-table::\n", "parameter-table::\n   :kinds: inputs results\n")})

		self.assertEqual(
			[
				"src/Package.rst:6: ERROR: gha:parameter-table::kinds: 'results' is not one of inputs, secrets, outputs. "
				"[docutils]"
			],
			self._warningLines()
		)

	def test_NoWorkflow(self) -> None:
		self._build({"Package": "Package\n#######\n\n.. gha:parameter-table::\n"})

		self.assertEqual(
			["src/Package.rst:4: WARNING: gha:parameter-table is not preceded by a gha:workflow. [gha.workflow]"],
			self._warningLines()
		)


class Interfaces(Project):
	PAGE = f"{HEADER}.. gha:interface::\n\n.. gha:autoinputs::\n"

	def _field(self, html: str, name: str) -> str:
		"""
		Cut a field's body out of a page.

		:param html: The page's HTML.
		:param name: The field's name.
		:returns:    The body's HTML.
		"""
		start = html.index(f">{name}<")
		return html[start:html.index("</dd>", start)]

	def test_Parameters(self) -> None:
		self._workflow("Package", PACKAGE)
		self._workflow("Tag", TAG)
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		self.assertEqual([], self._warningLines())
		required = self._field(html, "Required Inputs")
		self.assertIn('href="#gha-input-Package.package_name"', required)
		self.assertNotIn("python_version", required)
		secrets = self._field(html, "Secrets")
		self.assertIn("<span class=\"pre\">PYPI_TOKEN</span></code> (required), ", secrets)
		self.assertIn("<span class=\"pre\">CODECOV_TOKEN</span></code></p>", secrets)
		self.assertIn("<span class=\"pre\">version</span>", self._field(html, "Outputs"))

	def test_None(self) -> None:
		self._workflow("Package", MINIMAL)
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		for name in ("Required Inputs", "Secrets", "Outputs", "Permissions"):
			self.assertIn("<em>none</em>", self._field(html, name))

	def test_Permissions(self) -> None:
		"""The highest access per scope is listed, with the job asking for it, through called templates."""
		self._workflow("Package", PACKAGE)
		self._workflow("Tag", TAG)
		self._build({"Package": self.PAGE})

		permissions = self._field(self._html("Package"), "Permissions").split("<li>")[1:]
		self.assertEqual(2, len(permissions))
		self.assertIn("<span class=\"pre\">write</span></code> - job <em>Tag</em> (Tag.yml:10)", permissions[0])
		self.assertIn("<span class=\"pre\">contents:</span>", permissions[0])
		self.assertIn("<span class=\"pre\">read</span></code> - job <em>Tag</em> (Tag.yml:11)", permissions[1])
		self.assertIn("<span class=\"pre\">actions:</span>", permissions[1])

	def test_PermissionLink(self) -> None:
		self._workflow("Package", PACKAGE)
		self._workflow("Tag", TAG)
		self._build({"Package": self.PAGE}, gha_ref="r1")

		self.assertIn(
			'href="https://github.com/owner/repo/blob/r1/.github/workflows/Tag.yml#L10">Tag.yml:10</a>',
			self._field(self._html("Package"), "Permissions")
		)

	def test_Contract(self) -> None:
		"""The templates and actions are left to gha:dependencies."""
		self._workflow("Package", PACKAGE)
		self._workflow("Tag", TAG)
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		self.assertNotIn(">Templates<", html)
		self.assertNotIn(">Actions<", html)

	def test_MissingTemplate(self) -> None:
		"""A missing template is reported once, and the workflow's own permissions are listed."""
		self._workflow("Package", PACKAGE)
		self._build({"Package": self.PAGE})

		self.assertIn(" - job <em>Build</em> (Package.yml:46)", self._field(self._html("Package"), "Permissions"))
		self.assertEqual(
			["src/Package.rst:6: WARNING: gha:interface: Workflow 'Tag.yml' doesn't exist in 'workflows'. [gha.workflow]"],
			self._warningLines()
		)


#: A pipeline calling a template of the documented repository once, another twice, and one of another repository.
PIPELINE = dedent("""\
	on:
	  workflow_call:

	jobs:
	  Build:
	    uses: owner/repo/.github/workflows/Build.yml@r1

	  Cleanup:
	    uses: owner/repo/.github/workflows/Cleanup.yml@r1
	    needs: Build

	  FinalCleanup:
	    uses: owner/repo/.github/workflows/Cleanup.yml@r1
	    needs: Cleanup

	  Notify:
	    uses: other/tools/.github/workflows/Notify.yml@v2
""")

#: A template running in a container, with a service, a local composite action and an action of another repository.
BUILD = dedent("""\
	on:
	  workflow_call:

	jobs:
	  Build:
	    runs-on: ubuntu-26.04
	    container:
	      image: ${{ inputs.image }}
	    services:
	      database:
	        image: postgres:18
	    steps:
	      - uses: actions/checkout@v6
	      - uses: ./.github/actions/Composite
	      - uses: actions/checkout@v6
""")

#: A template running one action.
CLEANUP = dedent("""\
	on:
	  workflow_call:

	jobs:
	  Cleanup:
	    runs-on: ubuntu-26.04
	    steps:
	      - uses: geekyeggo/delete-artifact@v6
""")

#: A composite action, running a Docker action of the repository, an action of another repository and an image.
COMPOSITE = dedent("""\
	runs:
	  using: composite
	  steps:
	    - uses: owner/repo/.github/actions/Docker@r1
	    - uses: pyTooling/upload-artifact@v7
	    - uses: docker://alpine:3.22
""")

#: A Docker action.
DOCKER = "runs:\n  using: docker\n  image: Dockerfile\n"


class DependencyLists(Project):
	def _repository(self) -> None:
		"""Write a repository's workflows and actions into ``.github``."""
		github = self._path / ".github"
		(github / "workflows").mkdir(parents=True)
		for name, content in (("Pipeline", PIPELINE), ("Build", BUILD), ("Cleanup", CLEANUP)):
			(github / "workflows" / f"{name}.yml").write_text(content, encoding="utf-8")

		for name, content in (("Composite", COMPOSITE), ("Docker", DOCKER)):
			(github / "actions" / name).mkdir(parents=True)
			(github / "actions" / name / "action.yml").write_text(content, encoding="utf-8")

	def _items(self, content: str = "", **config: str) -> list[str]:
		"""
		Build a page with ``gha:dependencies`` for workflow 'Pipeline', and return the list as indented lines of text.

		:param content: The directive's content.
		:param config:  Configuration values overriding the defaults.
		:returns:       One line per list item, indented by two spaces per level.
		"""
		self._repository()
		page = f".. gha:workflow:: Pipeline\n\nPipeline\n########\n\n.. gha:dependencies::\n\n{indent(content, '   ')}"
		self._build({"Pipeline": page}, gha_workflow_directory="../.github/workflows", **config)

		html = self._html("Pipeline")
		start = html.rindex("<ul", 0, html.index("gha-dependencies"))
		lines = []
		level = 0
		for tag, text in findall(r"<(/?\w+)[^>]*>|([^<]+)", html[start:]):
			if tag == "ul":
				level += 1
			elif tag == "/ul":
				level -= 1
				if level == 0:
					break
			elif tag == "li":
				lines.append("  " * (level - 1))
			elif len(lines) > 0:
				lines[-1] += unescape(text)

		return [line[:len(line) - len(line.lstrip())] + " ".join(line.split()) for line in lines]

	def test_Derived(self) -> None:
		self.assertEqual(
			[
				"owner/repo/.github/workflows/Build.yml@r1",
				"  actions/checkout@v6",
				"  ./.github/actions/Composite",
				"    owner/repo/.github/actions/Docker@r1",
				"      image Dockerfile",
				"    pyTooling/upload-artifact@v7",
				"    docker://alpine:3.22",
				"  container ${{ inputs.image }}",
				"  service database: postgres:18",
				"owner/repo/.github/workflows/Cleanup.yml@r1 (called by 2 jobs: Cleanup, FinalCleanup)",
				"  geekyeggo/delete-artifact@v6",
				"other/tools/.github/workflows/Notify.yml@v2",
			],
			self._items()
		)
		self.assertEqual([], self._warningLines())

	def test_Links(self) -> None:
		self._items(gha_ref="r1")

		html = self._html("Pipeline")
		self.assertIn('href="https://github.com/actions/checkout"', html)
		self.assertIn('href="https://github.com/owner/repo/tree/r1/.github/actions/Composite"', html)
		self.assertIn('href="https://github.com/owner/repo/tree/r1/.github/actions/Docker"', html)
		self.assertIn('href="https://github.com/other/tools/blob/v2/.github/workflows/Notify.yml"', html)

	def test_Links_Server(self) -> None:
		self._items(gha_ref="r1", gha_server="https://github.example.com/")

		html = self._html("Pipeline")
		self.assertIn('href="https://github.example.com/actions/checkout"', html)
		self.assertIn('href="https://github.example.com/owner/repo/tree/r1/.github/actions/Composite"', html)
		self.assertNotIn('href="https://github.com/', html)

	def test_Merge(self) -> None:
		"""Hand-written items join the derived ones they name, at every level; the others are appended."""
		content = dedent("""\
			* Build.yml

			  * ./.github/actions/Composite

			    * pyTooling/upload-artifact

			      * ``actions/upload-artifact``

			  * container

			    * provides ``latexmk``

			  * apt: ``make``

			* pip

			  * ``wheel``

			* owner/repo/.github/workflows/Cleanup.yml@r1

			  * ``gh``

			Packages are installed in every job.
		""")
		self.assertEqual(
			[
				"owner/repo/.github/workflows/Build.yml@r1",
				"  actions/checkout@v6",
				"  ./.github/actions/Composite",
				"    owner/repo/.github/actions/Docker@r1",
				"      image Dockerfile",
				"    pyTooling/upload-artifact@v7",
				"      actions/upload-artifact",
				"    docker://alpine:3.22",
				"  container ${{ inputs.image }}",
				"    provides latexmk",
				"  service database: postgres:18",
				"  apt: make",
				"owner/repo/.github/workflows/Cleanup.yml@r1 (called by 2 jobs: Cleanup, FinalCleanup)",
				"  geekyeggo/delete-artifact@v6",
				"  gh",
				"other/tools/.github/workflows/Notify.yml@v2",
				"pip",
				"  wheel",
			],
			self._items(content)
		)
		self.assertIn("<p>Packages are installed in every job.</p>", self._html("Pipeline"))

	def test_None(self) -> None:
		self._workflow("Package", MINIMAL)
		self._build({"Package": f"{HEADER}.. gha:dependencies::\n\n.. gha:autoinputs::\n"})

		self.assertEqual([], self._warningLines())
		self.assertIn("<p><em>none</em></p>", self._html("Package"))

	def test_MissingAction(self) -> None:
		self._repository()
		(self._path / ".github" / "actions" / "Docker" / "action.yml").unlink()
		page = ".. gha:workflow:: Pipeline\n\nPipeline\n########\n\n.. gha:dependencies::\n"
		self._build({"Pipeline": page}, gha_workflow_directory="../.github/workflows")

		self.assertEqual(
			[
				"src/Pipeline.rst:6: WARNING: gha:dependencies: Action '.github/actions/Docker' has no 'action.yml' in "
				"'.github/actions/Docker'. [gha.workflow]"
			],
			self._warningLines()
		)


class YAMLExcerpts(Project):
	def _code(self, html: str) -> str:
		"""
		Cut the first code block out of a page, without its markup.

		:param html: The page's HTML.
		:returns:    The code block's text.
		"""
		start = html.index('<div class="highlight-yaml')
		return unescape(sub(r"<[^>]+>", "", html[start:html.index("</pre>", start)]))

	def _page(self, options: str = "") -> str:
		"""
		Create a page showing workflow 'Package' by ``gha:yaml``.

		:param options: The options of ``gha:yaml``, one per line, indented.
		:returns:       The page.
		"""
		return f"{HEADER}.. gha:yaml::\n{options}\n.. gha:autoinputs::\n"

	def test_Section(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :section: secrets\n")})

		html = self._html("Package")
		self.assertEqual([], self._warningLines())
		self.assertIn("Package.yml, lines 35-40", html)
		code = self._code(html)
		self.assertTrue(code.startswith("35secrets:\n36  PYPI_TOKEN:\n"), code)
		self.assertTrue(code.endswith("40    required: false\n"), code)

	def test_Jobs(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :section: jobs\n")})

		code = self._code(self._html("Package"))
		self.assertTrue(code.startswith("42jobs:\n"), code)
		self.assertTrue(code.endswith("66      - Release\n"), code)

	def test_Job(self) -> None:
		"""A comment at the start of a line inside the job is kept; a comment before the next job is not."""
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :job: Build\n")})

		html = self._html("Package")
		self.assertIn("Package.yml, lines 43-55", html)
		code = self._code(html)
		self.assertTrue(code.startswith("43Build:\n44  runs-on: ubuntu-26.04\n"), code)
		self.assertIn("53# a comment at the start of a line, inside job 'Build'\n", code)
		self.assertTrue(code.endswith("55    - uses: ./.github/actions/Local\n"), code)

	def test_File(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page()})

		code = self._code(self._html("Package"))
		self.assertTrue(code.startswith(" 1name: Package\n"), code)
		self.assertTrue(code.endswith("66      - Release\n"), code)

	def test_Link(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :job: Build\n")}, gha_ref="r1")

		self.assertIn(
			'href="https://github.com/owner/repo/blob/r1/.github/workflows/Package.yml#L43-L55">Package.yml, lines 43-55</a>',
			self._html("Package")
		)

	def test_Caption(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :job: Build\n   :caption: The *Build* job.\n   :name: build\n")})

		html = self._html("Package")
		self.assertIn("The <em>Build</em> job.", html)
		self.assertIn('id="build"', html)

	def test_UnknownJob(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :job: Test\n")})

		self.assertEqual(
			["src/Package.rst:6: WARNING: gha:yaml: Workflow 'Package' has no job 'Test'. [gha.drift]"],
			self._warningLines()
		)

	def test_EmptySection(self) -> None:
		self._workflow("Package", MINIMAL)
		self._build({"Package": self._page("   :section: outputs\n")})

		self.assertEqual(
			["src/Package.rst:6: WARNING: gha:yaml: Workflow 'Package' has no outputs. [gha.drift]"],
			self._warningLines()
		)

	def test_WrongOptions(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": self._page("   :job: Build\n   :section: jobs\n")})
		self.assertEqual(
			["src/Package.rst:6: ERROR: gha:yaml: Options ':section:' and ':job:' exclude each other. [docutils]"],
			self._warningLines()
		)

		self._build({"Package": self._page("   :section: steps\n")})
		self.assertEqual(
			["src/Package.rst:6: ERROR: gha:yaml::section: 'steps' is not one of inputs, outputs, secrets, jobs. [docutils]"],
			self._warningLines()
		)


class AutoInputs(Project):
	def test_Entries(self) -> None:
		"""An input documented after gha:autoinputs gets no second entry."""
		self._workflow("Package", PACKAGE)
		page = f"{HEADER}.. gha:input:: package_name\n\n.. gha:autoinputs::\n\n{ENTRIES}"
		page = page.replace(".. gha:input:: package_name\n\n.. gha:input:: python_version\n", "")
		app = self._build({"Package": page, "index": "Index\n#####\n\n:gha:input:`Package.dry_run`\n"})

		self.assertEqual([], self._warningLines())
		html = self._html("Package")
		self.assertEqual(1, html.count('id="gha-input-Package.package_name"'))
		self.assertEqual(1, html.count('id="gha-input-Package.pages_on"'))
		self.assertLess(html.index('id="gha-input-Package.python_version"'), html.index('id="gha-input-Package.pages_on"'))
		self.assertLess(html.index('id="gha-input-Package.dry_run"'), html.index('id="gha-input-Package.pages_on"'))
		objects = app.env.get_domain("gha").Objects
		self.assertEqual(("Package", "gha-input-Package.dry_run"), objects[("input", "Package.dry_run")])
		self.assertIn('href="Package.html#gha-input-Package.dry_run"', self._html("index"))

	def test_Entry(self) -> None:
		"""An entry has the facts and the description of the workflow file, the anchors and the index entry."""
		self._workflow("Package", PACKAGE)
		self._build({"Package": f"{HEADER}.. gha:autoinputs::\n"})

		html = self._html("Package")
		entry = html[html.index('id="gha-input-Package.python_version"'):html.index('id="gha-input-Package.pages_on"')]
		fields = [part.split("<")[0] for part in entry.split('<dt class="field-')[1:]]
		self.assertEqual(["odd\">Type", "even\">Required", "odd\">Default Value", "even\">Description"], fields)
		self.assertIn("<p>Python version.</p>", entry)
		self.assertIn('id="jobtmpl-package-input-python-version"', entry)
		self.assertIn('<span id="python-version"></span>', entry)
		self.assertIn("python_version (input of Package)", self._html("genindex"))

	def test_Label(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({
			"Package": f"{HEADER}.. gha:autoinputs::\n",
			"index": "Index\n#####\n\n:ref:`JOBTMPL/Package/Input/dry_run`\n"
		})

		self.assertEqual([], self._warningLines())
		self.assertIn('href="Package.html#jobtmpl-package-input-dry-run"', self._html("index"))

	def test_Parallel(self) -> None:
		self._workflow("Package", PACKAGE)
		documents = {
			"Package": f"{HEADER}.. gha:autoinputs::\n",
			"index": "Index\n#####\n\n:gha:input:`Package.dry_run`\n",
			"A": "A\n#\n", "B": "B\n#\n", "C": "C\n#\n",
		}
		app = self._build(documents, parallel=2)

		self.assertEqual([], self._warningLines())
		objects = app.env.get_domain("gha").Objects
		self.assertEqual(("Package", "gha-input-Package.dry_run"), objects[("input", "Package.dry_run")])
		self.assertIn('href="Package.html#gha-input-Package.dry_run"', self._html("index"))

	def test_NoWorkflow(self) -> None:
		self._build({"Package": "Package\n#######\n\n.. gha:autoinputs::\n"})

		self.assertEqual(
			["src/Package.rst:4: WARNING: gha:autoinputs is not preceded by a gha:workflow. [gha.workflow]"],
			self._warningLines()
		)


class Drift(Project):
	def test_Undocumented(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": f"{HEADER}{ENTRIES}"})

		self.assertEqual(
			[
				"src/Package.rst:1: WARNING: Input 'dry_run' of workflow 'Package' has no entry: add a gha:input or a "
				"gha:autoinputs. [gha.drift]"
			],
			self._warningLines()
		)

	def test_Workflows(self) -> None:
		"""Each workflow of a document is checked, and reported at its own gha:workflow."""
		self._workflow("Package", PACKAGE)
		self._workflow("Minimal", MINIMAL)
		page = f".. gha:workflow:: Minimal\n\nMinimal\n#######\n\n.. gha:workflow:: Package\n\n{ENTRIES}"
		self._build({"Package": page})

		self.assertEqual(
			[
				"src/Package.rst:1: WARNING: Input 'name' of workflow 'Minimal' has no entry: add a gha:input or a "
				"gha:autoinputs. [gha.drift]",
				"src/Package.rst:6: WARNING: Input 'dry_run' of workflow 'Package' has no entry: add a gha:input or a "
				"gha:autoinputs. [gha.drift]"
			],
			self._warningLines()
		)

	def test_OtherDocument(self) -> None:
		"""An input documented only in another document has no entry in this one."""
		self._workflow("Package", PACKAGE)
		page = f"{HEADER}{ENTRIES}"
		other = ".. gha:workflow:: Package\n\nOther\n#####\n\n.. gha:input:: dry_run\n"
		self._build({"Package": page, "Other": other}, suppress_warnings=["gha.duplicate"])

		self.assertIn(
			"src/Package.rst:1: WARNING: Input 'dry_run' of workflow 'Package' has no entry: add a gha:input or a "
			"gha:autoinputs. [gha.drift]",
			self._warningLines()
		)

	def test_Suppressed(self) -> None:
		self._workflow("Package", PACKAGE)
		self._build({"Package": f"{HEADER}{ENTRIES}"}, suppress_warnings=["gha.drift"])

		self.assertEqual([], self._warningLines())
