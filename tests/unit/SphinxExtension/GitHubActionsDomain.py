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
Unit tests for the Sphinx domain ``gha`` of :mod:`pyTooling.Documentation.Sphinx.GitHubActions`.

Every testcase builds a small Sphinx project in a temporary directory and checks the HTML, the domain's data and the
warnings.
"""
from io                    import StringIO
from pathlib               import Path
from sys                   import version_info
from tempfile              import TemporaryDirectory
from textwrap              import dedent
from typing                import Any

from pytest                import mark

from pyTooling.Testing     import Testcase

# 'pyTooling[sphinx]' requires Sphinx 9.1, which requires Python 3.12 - see 'tests/unit/Documentation.py'.
sphinxIsSupported = version_info >= (3, 12)

if sphinxIsSupported:
	from sphinx.testing.util                          import SphinxTestApp
	from sphinx.util.console                          import strip_colors

	from pyTooling.Documentation.Sphinx.GitHubActions import NO_DEFAULT, formatValue


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


WORKFLOW = dedent("""\
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
	      dry_run:
	        required: false
	        default: false
	        type: boolean
	      pages_on:
	        required: false
	        default: |
	          default-branch
	          release-tag
	        type: string
	    outputs:
	      version:
	        description: 'Version of the package.'
	        value: ${{ jobs.Build.outputs.version }}
	    secrets:
	      PYPI_TOKEN:
	        description: 'Token for PyPI.'
	        required: true

	jobs:
	  Build:
	    runs-on: ubuntu-26.04
	    outputs:
	      version: ${{ steps.version.outputs.version }}
	    steps:
	      - id: version
	        run: echo "version=1.0.0" >> "${GITHUB_OUTPUT}"
""")


PAGE = dedent("""\
	.. gha:workflow:: Package

	Package
	#######

	Inputs
	******

	.. gha:input:: package_name

	   :Possible Values: Any Python package name.
	   :Example:         ``myPackage``

	.. gha:input:: python_version

	   :Description: Python version used by jobs needing one.

	.. gha:input:: dry_run

	.. gha:input:: pages_on

	Secrets
	*******

	.. gha:secret:: PYPI_TOKEN

	Outputs
	*******

	.. gha:output:: version

	   :Type: string
""")


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Project(Testcase):
	"""Builds a Sphinx project in a temporary directory, removed after each test."""

	_directory: TemporaryDirectory
	_path:      Path
	_warnings:  StringIO

	def setUp(self) -> None:
		self._directory = TemporaryDirectory()
		self._path = Path(self._directory.name)
		(self._path / "workflows").mkdir()
		(self._path / "src").mkdir()

	def tearDown(self) -> None:
		self._directory.cleanup()

	def _workflow(self, name: str, content: str = WORKFLOW) -> Path:
		"""
		Write a workflow file.

		:param name:    Name of the workflow, the file's stem.
		:param content: Content of the file.
		:returns:       Path to the file.
		"""
		path = self._path / "workflows" / f"{name}.yml"
		path.write_text(content, encoding="utf-8")

		return path

	def _build(self, documents: dict[str, str], parallel: int = 0, fresh: bool = True, **config: Any) -> "SphinxTestApp":
		"""
		Write the documents and build the project as HTML.

		:param documents: Content of the documents, by name; ``index`` has a toctree of the others.
		:param parallel:  Optional, number of processes reading the documents. Default: ``0``.
		:param fresh:     Optional, ``True`` to discard a previous build's environment. Default: ``True``.
		:param config:    Configuration values overriding the defaults.
		:returns:         The Sphinx application after the build.
		"""
		source = self._path / "src"
		(source / "conf.py").write_text('extensions = ["pyTooling.Documentation.Sphinx"]\n', encoding="utf-8")
		others = "".join(f"   {name}\n" for name in documents if name != "index")
		index = documents.get("index", "Index\n#####\n")
		(source / "index.rst").write_text(f"{index}\n\n.. toctree::\n\n{others}", encoding="utf-8")
		for name, content in documents.items():
			if name != "index":
				(source / f"{name}.rst").write_text(content, encoding="utf-8")

		overrides = {"gha_repository": "owner/repo", "gha_workflow_directory": "../workflows"}
		overrides.update(config)
		self._warnings = StringIO()
		app = SphinxTestApp(
			"html", source, self._path / "build", freshenv=fresh, confoverrides=overrides, status=StringIO(),
			warning=self._warnings, parallel=parallel
		)
		try:
			app.build()
		finally:
			app.cleanup()

		return app

	def _html(self, name: str) -> str:
		"""
		Read a built page.

		:param name: Name of the document.
		:returns:    The page's HTML.
		"""
		return (self._path / "build" / "html" / f"{name}.html").read_text(encoding="utf-8")

	def _warningLines(self) -> list[str]:
		"""
		Return the warnings of the last build, without the temporary directory's path.

		:returns: One line per warning.
		"""
		return [strip_colors(line).replace(f"{self._path}/", "") for line in self._warnings.getvalue().splitlines()]


class Workflows(Project):
	def test_Target(self) -> None:
		self._workflow("Package")
		app = self._build({"Package": PAGE})

		domain = app.env.get_domain("gha")
		self.assertEqual(("Package", "gha-workflow-Package"), domain.ResolveWorkflow("Package"))
		self.assertIsNone(domain.ResolveWorkflow("Unknown"))
		self.assertEqual([], self._warningLines())

		html = self._html("Package")
		self.assertIn('id="gha-workflow-Package"', html)
		self.assertIn('id="jobtmpl-package"', html)

	def test_Target_Parameters(self) -> None:
		self._workflow("Package")
		domain = self._build({"Package": PAGE}).env.get_domain("gha")

		for arguments, exceptionType, message in (
			((None, ), ValueError, "Parameter 'name' is None."),
			((1, ),    TypeError,  "Parameter 'name' is not of type 'str'.")
		):
			with self.subTest(method="ResolveWorkflow", message=message):
				with self.assertRaises(exceptionType) as context:
					domain.ResolveWorkflow(*arguments)

				self.assertEqual(message, str(context.exception))

		for arguments, exceptionType, message in (
			((None, "Package.x", "id"),               ValueError, "Parameter 'objectType' is None."),
			(("input", 1, "id"),                      TypeError,  "Parameter 'name' is not of type 'str'."),
			(("input", "Package.x", None),            ValueError, "Parameter 'nodeID' is None."),
			(("input", "Package.x", "id", "section"), TypeError,  "Parameter 'location' is not of type 'Node'.")
		):
			with self.subTest(method="NoteObject", message=message):
				with self.assertRaises(exceptionType) as context:
					domain.NoteObject(*arguments)

				self.assertEqual(message, str(context.exception))

	def test_Index(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE})

		index = self._html("genindex")
		self.assertIn("GitHub Actions workflow", index)
		self.assertIn("package_name (input of Package)", index)

	def test_File(self) -> None:
		path = self._workflow("Other")
		(self._path / "src" / "yaml").mkdir()
		path.rename(self._path / "src" / "yaml" / "Package.yml")
		page = PAGE.replace(".. gha:workflow:: Package\n", ".. gha:workflow:: Package\n   :file: yaml/Package.yml\n")
		app = self._build({"Package": page}, gha_workflow_directory=None)

		self.assertEqual([], self._warningLines())
		self.assertIn("<p>yes</p>", self._html("Package"))
		self.assertIn(("input", "Package.package_name"), app.env.get_domain("gha").Objects)

	def test_NoFile(self) -> None:
		self._build({"Package": PAGE}, gha_workflow_directory=None)

		self.assertIn(
			"src/Package.rst:1: WARNING: gha:workflow 'Package' has no file: give option ':file:' or set "
			"'gha_workflow_directory'. [gha.workflow]",
			self._warningLines()
		)

	def test_MissingFile(self) -> None:
		self._build({"Package": PAGE})

		self.assertIn(
			"src/Package.rst:1: WARNING: gha:workflow 'Package': file 'workflows/Package.yml' doesn't exist. "
			"[gha.workflow]",
			self._warningLines()
		)

	def test_Malformed(self) -> None:
		self._workflow("Package", "on: push\njobs:\n  Build:\n    runs-on: x\n    needs: Missing\n")
		self._build({"Package": ".. gha:workflow:: Package\n\nPackage\n#######\n"})

		self.assertEqual(
			[
				"workflows/Package.yml:3: WARNING: gha:workflow 'Package': Job 'Build' needs job 'Missing', which the "
				"workflow doesn't have. [gha.workflow]"
			],
			self._warningLines()
		)

	def test_OtherName(self) -> None:
		self._workflow("Package")
		page = PAGE.replace(".. gha:workflow:: Package\n", ".. gha:workflow:: Build\n   :file: ../workflows/Package.yml\n")
		self._build({"Package": page})

		self.assertIn(
			"src/Package.rst:1: WARNING: gha:workflow 'Build' reads file 'Package.yml', which names workflow 'Package'. "
			"[gha.workflow]",
			self._warningLines()
		)

	def test_RequiredWithDefault(self) -> None:
		required = "        required: true\n        default: '3.14'"
		self._workflow("Package", WORKFLOW.replace("        required: false\n        default: '3.14'", required))
		self._build({"Package": PAGE})

		self.assertEqual(
			[
				"workflows/Package.yml:8: WARNING: Input 'python_version' of workflow 'Package' is required and has a "
				"default, which is never used. [gha.drift]"
			],
			self._warningLines()
		)

	def test_Config(self) -> None:
		self._workflow("Package")
		app = self._build({"Package": PAGE})

		self.assertIsNone(app.config.gha_ref)
		self.assertEqual("JOBTMPL", app.config.gha_label_prefix)

		app = self._build({"Package": PAGE}, gha_ref="r8")

		self.assertEqual("r8", app.config.gha_ref)

	def test_LabelPrefix(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE}, gha_label_prefix=None)

		html = self._html("Package")
		self.assertNotIn("jobtmpl-", html)


class Parameters(Project):
	def test_Input(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE})

		html = self._html("Package")
		entry = html[html.index('id="gha-input-Package.package_name"'):html.index('id="gha-input-Package.python_version"')]
		fields = [part.split("<")[0] for part in entry.split('<dt class="field-')[1:]]
		self.assertEqual(
			["odd\">Type", "even\">Required", "odd\">Default Value", "even\">Possible Values", "odd\">Description",
			 "even\">Example"],
			fields
		)
		self.assertIn("<p>string</p>", entry)
		self.assertIn("<p>yes</p>", entry)
		self.assertIn(f"<p>{NO_DEFAULT}</p>", entry)
		self.assertIn("<p>Name of the package.</p>", entry)
		self.assertIn('id="jobtmpl-package-input-package-name"', entry)
		self.assertIn('id="package-name"', entry)

	def test_Default(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE})

		html = self._html("Package")
		self.assertIn("<span class=\"pre\">'3.14'</span>", html)
		self.assertIn("<span class=\"pre\">false</span>", html)
		self.assertIn("default-branch\nrelease-tag", html)

	def test_Description(self) -> None:
		"""A hand-written description wins over the workflow file's."""
		self._workflow("Package")
		self._build({"Package": PAGE})

		html = self._html("Package")
		self.assertIn("<p>Python version used by jobs needing one.</p>", html)
		self.assertNotIn("<p>Python version.</p>", html)

	def test_Output(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE})

		html = self._html("Package")
		entry = html[html.index('id="gha-output-Package.version"'):]
		self.assertLess(entry.index(">Type<"), entry.index(">Description<"))
		self.assertIn("<p>Version of the package.</p>", entry)
		self.assertNotIn(">Required<", entry[:entry.index("</section>")])

	def test_Secret(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE})

		html = self._html("Package")
		entry = html[html.index('id="gha-secret-Package.PYPI_TOKEN"'):html.index('id="outputs"')]
		self.assertIn("<p>string</p>", entry)
		self.assertIn("<p>yes</p>", entry)
		self.assertIn(f"<p>{NO_DEFAULT}</p>", entry)

	def test_FactField(self) -> None:
		self._workflow("Package")
		page = PAGE.replace("   :Possible Values: Any", "   :Type:            number\n   :Possible Values: Any")
		self._build({"Package": page})

		self.assertEqual(
			[
				"src/Package.rst:11: WARNING: gha:input 'Package.package_name': field 'Type' is taken from the workflow "
				"file; remove it. [gha.drift]"
			],
			self._warningLines()
		)
		self.assertNotIn("<p>number</p>", self._html("Package"))

	def test_Unknown(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE + "\n.. gha:input:: unknown\n"})

		self.assertEqual(
			["src/Package.rst:34: WARNING: Workflow 'Package' has no input 'unknown' (Package.yml). [gha.drift]"],
			self._warningLines()
		)

	def test_OutsideWorkflow(self) -> None:
		self._build({"Package": "Package\n#######\n\n.. gha:input:: package_name\n"})

		self.assertEqual(
			["src/Package.rst:4: WARNING: gha:input 'package_name' is not preceded by a gha:workflow. [gha.workflow]"],
			self._warningLines()
		)

	def test_Duplicate(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE, "Again": PAGE.replace("Package\n#######", "Again\n#####")})

		self.assertTrue(any("Duplicate description of gha:workflow 'Package'" in line for line in self._warningLines()))


class References(Project):
	PAGE = PAGE + dedent("""\

		See :gha:input:`package_name`, :gha:input:`~Package.python_version`, :gha:workflow:`Package`,
		:gha:secret:`PYPI_TOKEN`, :gha:output:`version` and :ref:`JOBTMPL/Package/Input/dry_run`.
	""")

	def test_InWorkflow(self) -> None:
		self._workflow("Package")
		self._build({"Package": self.PAGE})

		html = self._html("Package")
		self.assertEqual([], self._warningLines())
		self.assertIn('href="#gha-input-Package.package_name"', html)
		self.assertIn(
			'title="Package.python_version"><code class="xref gha gha-input docutils literal notranslate">'
			'<span class="pre">python_version</span>',
			html
		)
		self.assertIn('href="#gha-workflow-Package"', html)
		self.assertIn('href="#gha-secret-Package.PYPI_TOKEN"', html)
		self.assertIn('href="#gha-output-Package.version"', html)
		self.assertIn('href="#jobtmpl-package-input-dry-run"><span class="std std-ref">dry_run</span>', html)

	def test_OtherDocument(self) -> None:
		self._workflow("Package")
		index = "Index\n#####\n\n:gha:input:`Package.package_name` and :ref:`JOBTMPL/Package`\n"
		self._build({"Package": PAGE, "index": index})

		html = self._html("index")
		self.assertEqual([], self._warningLines())
		self.assertIn('href="Package.html#gha-input-Package.package_name"', html)
		self.assertIn('href="Package.html#jobtmpl-package"><span class="std std-ref">Package</span>', html)

	def test_Unresolved(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE, "index": "Index\n#####\n\n:gha:input:`package_name`\n"})

		self.assertEqual(
			["src/index.rst:4: WARNING: gha:input reference target not found: package_name [ref.input]"],
			self._warningLines()
		)

	def test_Any(self) -> None:
		self._workflow("Package")
		self._build({"Package": PAGE, "index": "Index\n#####\n\n:any:`Package.package_name`\n"})

		self.assertEqual([], self._warningLines())
		self.assertIn('href="Package.html#gha-input-Package.package_name"', self._html("index"))


class Builds(Project):
	def test_Parallel(self) -> None:
		self._workflow("Package")
		self._workflow("Build")
		documents = {
			"Package": References.PAGE,
			"Build":   PAGE.replace("Package", "Build") + "\n:gha:input:`Package.dry_run`\n",
			"A": "A\n#\n", "B": "B\n#\n", "C": "C\n#\n",
		}
		app = self._build(documents, parallel=2)

		self.assertEqual([], self._warningLines())
		objects = app.env.get_domain("gha").Objects
		self.assertEqual(("Build", "gha-input-Build.dry_run"), objects[("input", "Build.dry_run")])
		self.assertEqual(("Package", "gha-input-Package.dry_run"), objects[("input", "Package.dry_run")])
		self.assertIn('href="Package.html#gha-input-Package.dry_run"', self._html("Build"))

	def test_Incremental(self) -> None:
		self._workflow("Package")
		index = "Index\n#####\n\n:gha:input:`Package.dry_run`\n"
		self._build({"Package": PAGE, "index": index})
		self.assertEqual([], self._warningLines())

		app = self._build({"Package": PAGE.replace(".. gha:input:: dry_run\n", ""), "index": index}, fresh=False)

		self.assertNotIn(("input", "Package.dry_run"), app.env.get_domain("gha").Objects)
		self.assertIn(("input", "Package.package_name"), app.env.get_domain("gha").Objects)
		self.assertIn(
			"src/index.rst:4: WARNING: gha:input reference target not found: Package.dry_run [ref.input]",
			self._warningLines()
		)

	def test_WorkflowChanged(self) -> None:
		"""A document is read again when its workflow file changed."""
		self._workflow("Package")
		self._build({"Package": PAGE})

		self._workflow("Package", WORKFLOW.replace("default: '3.14'", "default: '3.15'"))
		self._build({"Package": PAGE}, fresh=False)

		self.assertIn("'3.15'", self._html("Package"))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Values(Testcase):
	def test_String(self) -> None:
		self.assertEqual("'3.14'", formatValue("3.14"))
		self.assertEqual("''", formatValue(""))
		self.assertEqual("'tool''s'", formatValue("tool's"))

	def test_Boolean(self) -> None:
		self.assertEqual("true", formatValue(True))
		self.assertEqual("false", formatValue(False))

	def test_Number(self) -> None:
		self.assertEqual("0", formatValue(0))
		self.assertEqual("1.5", formatValue(1.5))

	def test_None(self) -> None:
		self.assertEqual(NO_DEFAULT, formatValue(None))
