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
Unit tests for :mod:`pyTooling.Documentation.Sphinx.GitHubActions.Graph`, the ``gha:pipeline-graph`` directive.

A graph is checked as DOT source, not as a picture: every testcase builds a small Sphinx project around three workflow
files and reads the code handed to :mod:`sphinx.ext.graphviz`.
"""
from io                      import StringIO
from pathlib                 import Path
from shutil                  import which
from subprocess              import run as subprocess_run
from sys                     import version_info
from tempfile                import TemporaryDirectory
from textwrap                import dedent

from pytest                  import mark

from pyTooling.Testing       import Testcase

# 'pyTooling[sphinx]' requires Sphinx 9.1, which requires Python 3.12 - see tests/unit/Documentation.py. No signature
# below may name one of these imports.
sphinxIsSupported = version_info >= (3, 12)

if sphinxIsSupported:
	from docutils.nodes                                     import document
	from sphinx.application                                 import Sphinx
	from sphinx.ext.graphviz                                import graphviz
	from sphinx.util.console                                import strip_escape_sequences
	from sphinx.util.docutils                               import docutils_namespace

	from pyTooling.CI.Workflow                              import Workflow, WorkflowResolver
	from pyTooling.Documentation.Sphinx.GitHubActions.Graph import CSS_CLASS, PipelineDotGraph


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


#: The entry-point workflow: a template of the documented repository, a job running steps with a matrix, a template
#: called at another ref, a conditional template of another repository, and a local template.
PIPELINE = dedent("""\
	name: Pipeline

	on:
	  push:

	jobs:
	  Prepare:
	    uses: Owner/Repo/.github/workflows/Prepare.yml@r1

	  Build:
	    runs-on: ubuntu-24.04
	    needs:
	      - Prepare
	    strategy:
	      matrix:
	        python: ['3.13', '3.14']
	        system: [ubuntu, windows]
	    steps:
	      - run: make

	  Test:
	    uses: Owner/Repo/.github/workflows/Test.yml@dev
	    needs:
	      - Prepare
	      - Build

	  Publish:
	    uses: Other/Tools/.github/workflows/Publish.yml@v2
	    needs:
	      - Test
	    if: github.ref == 'refs/heads/main'

	  Local:
	    uses: ./.github/workflows/Prepare.yml
	""")

#: A template running one job.
PREPARE = dedent("""\
	name: Prepare

	on:
	  workflow_call:

	jobs:
	  Prepare:
	    runs-on: ubuntu-24.04
	    steps:
	      - run: echo
	""")

#: A template running two independent jobs and one needing both.
TEST = dedent("""\
	name: Test

	on:
	  workflow_call:

	jobs:
	  Unit:
	    runs-on: ubuntu-24.04
	    steps:
	      - run: pytest

	  Lint:
	    runs-on: ubuntu-24.04
	    steps:
	      - run: pylint

	  Report:
	    runs-on: ubuntu-24.04
	    needs:
	      - Unit
	      - Lint
	    steps:
	      - run: echo
	""")

#: A configuration registering a stub of the 'gha' domain, which knows a page for 'Test.yml' only.
CONFIGURATION = dedent("""\
	from sphinx.domains import Domain

	from pyTooling.Documentation.Sphinx.GitHubActions.Graph import PipelineGraph, resolveLinks

	class GitHubActionsDomain(Domain):
	    name = "gha"
	    label = "GitHub Actions"
	    directives = {"pipeline-graph": PipelineGraph}

	    def ResolveWorkflow(self, name):
	        return {"Test": ("templates", "gha-workflow-Test")}.get(name, None)

	def setup(app):
	    app.add_domain(GitHubActionsDomain)
	    app.add_config_value("gha_repository", None, "env")
	    app.add_config_value("gha_workflow_directory", None, "env")
	    app.add_config_value("gha_ref", None, "env")
	    app.connect("doctree-resolved", resolveLinks)

	extensions = ["sphinx.ext.graphviz"]
	gha_repository = "Owner/Repo"
	""")

#: A configuration without the domain, registering the directive under a plain name.
CONFIGURATION_WITHOUT_DOMAIN = dedent("""\
	from pyTooling.Documentation.Sphinx.GitHubActions.Graph import PipelineGraph, resolveLinks

	def setup(app):
	    app.add_directive("pipeline-graph", PipelineGraph)
	    app.connect("doctree-resolved", resolveLinks)

	extensions = ["sphinx.ext.graphviz"]
	""")

#: A configuration loading pyTooling's extension, which registers the real 'gha' domain and the directive.
CONFIGURATION_EXTENSION = dedent("""\
	extensions = ["pyTooling.Documentation.Sphinx"]
	gha_repository = "Owner/Repo"
	gha_workflow_directory = "../.github/workflows"
	""")


def build(
	directory: str,
	options: str = "",
	configuration: str = CONFIGURATION,
	directive: str = "gha:pipeline-graph",
	path: str = "../.github/workflows/Pipeline.yml",
	templates: str = "Templates\n#########\n"
) -> tuple[list[str], list[str]]:
	"""
	Build a project drawing :data:`PIPELINE`, and return the DOT of its graphs and the build's warnings.

	:param directory:     Directory to create the project in.
	:param options:       Optional, lines of options of the directive, unindented. Default: none.
	:param configuration: Optional, content of :file:`conf.py`. Default: :data:`CONFIGURATION`.
	:param directive:     Optional, name of the directive. Default: ``gha:pipeline-graph``.
	:param path:          Optional, argument of the directive. Default: the path of :data:`PIPELINE`.
	:param templates:     Optional, content of the page :file:`templates.rst`. Default: a title only.
	:returns:             The DOT of every pipeline graph after its links are resolved, and the warnings without
	                      colours, one per line.
	"""
	root = Path(directory)
	workflows = root / ".github" / "workflows"
	workflows.mkdir(parents=True)
	(workflows / "Pipeline.yml").write_text(PIPELINE, encoding="utf-8")
	(workflows / "Prepare.yml").write_text(PREPARE, encoding="utf-8")
	(workflows / "Test.yml").write_text(TEST, encoding="utf-8")

	source = root / "doc"
	source.mkdir()
	(source / "conf.py").write_text(configuration, encoding="utf-8")
	(source / "templates.rst").write_text(templates, encoding="utf-8")
	indentedOptions = "".join(f"   {line}\n" for line in dedent(options).splitlines())
	(source / "index.rst").write_text(
		f"Pipeline\n########\n\n.. toctree::\n   :hidden:\n\n   templates\n\n.. {directive}:: {path}\n{indentedOptions}",
		encoding="utf-8"
	)

	codes = []

	def capture(_: Sphinx, doctree: document, __: str) -> None:
		"""
		Nested function collecting the DOT of the pipeline graphs of a resolved document.

		:param _:       The Sphinx application.
		:param doctree: The resolved document.
		:param __:      Name of the document.
		"""
		codes.extend(node["code"] for node in doctree.findall(graphviz) if CSS_CLASS in node["classes"])

	warnings = StringIO()
	with docutils_namespace():
		application = Sphinx(
			str(source), str(source), str(root / "build"), str(root / "doctrees"), "html",
			status=None, warning=warnings, freshenv=True
		)
		application.connect("doctree-resolved", capture, priority=900)
		application.build()

	return codes, strip_escape_sequences(warnings.getvalue()).splitlines()


def load(directory: str, depth: int = 0) -> str:
	"""
	Write :data:`PIPELINE` and its templates into a directory and draw it without Sphinx.

	:param directory: Directory to write the workflow files into.
	:param depth:     Optional, levels of templates to expand. Default: ``0``.
	:returns:         The graph in the DOT language.
	"""
	workflows = Path(directory)
	(workflows / "Pipeline.yml").write_text(PIPELINE, encoding="utf-8")
	(workflows / "Prepare.yml").write_text(PREPARE, encoding="utf-8")
	(workflows / "Test.yml").write_text(TEST, encoding="utf-8")

	resolver = WorkflowResolver({"Owner/Repo": workflows})

	return str(PipelineDotGraph(resolver.Load(workflows / "Pipeline.yml"), resolver, depth=depth))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Nodes(Testcase):
	"""A job is a node; its shape and style say what kind of job it is."""

	def test_Template(self) -> None:
		"""A job calling a template of the documented repository is a rounded box naming the template's file."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		self.assertIn(
			'"Prepare" [label=<Prepare<BR/><FONT POINT-SIZE="8" COLOR="#3d4652">Prepare.yml</FONT>>, '
			'style="rounded,filled", tooltip="uses: Owner/Repo/.github/workflows/Prepare.yml@r1"];',
			code
		)

	def test_Steps(self) -> None:
		"""A job running steps is a grey box with square corners; a matrix doubles the border and names its dimensions."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		self.assertIn(
			'"Build" [label=<Build<BR/><FONT POINT-SIZE="8" COLOR="#3d4652">matrix: python, system</FONT>>, '
			'style="filled", fillcolor="#f2f2f2", peripheries="2"];',
			code
		)

	def test_Conditional(self) -> None:
		"""A job with a condition is dashed, and the condition is its tooltip."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		publish = next(line for line in code.splitlines() if line.startswith('\t"Publish" ['))
		self.assertIn('style="rounded,filled,dashed"', publish)
		self.assertIn(
			'tooltip="uses: Other/Tools/.github/workflows/Publish.yml@v2\\nif: github.ref == \'refs/heads/main\'"', publish
		)

	def test_ForeignRepository(self) -> None:
		"""A template of another repository is a white leaf naming the repository and ref, and it is never linked."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 3")

		publish = next(line for line in code.splitlines() if line.startswith('\t"Publish" ['))
		self.assertIn("Publish.yml</FONT>", publish)
		self.assertIn("Other/Tools@v2</FONT>", publish)
		self.assertIn('fillcolor="#ffffff"', publish)
		self.assertNotIn("URL=", publish)
		self.assertNotIn("cluster_Publish", code)

	def test_Stable(self) -> None:
		"""The same workflow is always drawn as the same DOT."""
		with TemporaryDirectory() as directory:
			first = load(directory, 1)
			second = load(directory, 1)

		self.assertEqual(first, second)


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Edges(Testcase):
	"""The 'needs' of the jobs are the edges."""

	def test_Reduced(self) -> None:
		"""By default, an edge a longer path implies is dropped: Test needs Prepare through Build already."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		self.assertIn('\t"Prepare" -> "Build";', code)
		self.assertIn('\t"Build" -> "Test";', code)
		self.assertIn('\t"Test" -> "Publish";', code)
		self.assertNotIn('"Prepare" -> "Test"', code)

	def test_Reduced_No(self) -> None:
		"""':reduce: no' draws every 'needs'."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":reduce: no")

		self.assertIn('\t"Prepare" -> "Test";', code)

	def test_Roots(self) -> None:
		"""The jobs needing none start in the first rank."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		self.assertIn('\t{rank=min; "Prepare"; "Local";}', code)

	def test_Direction(self) -> None:
		"""The pipeline flows left to right, unless ':direction:' says top to bottom."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)
		with TemporaryDirectory() as directory:
			(codeTB, ), _ = build(directory, ":direction: tb")

		self.assertIn("\trankdir=LR;", code)
		self.assertIn("\trankdir=TB;", codeTB)


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Clusters(Testcase):
	"""':depth:' expands the templates of the documented repository into clusters of their jobs."""

	def test_Depth0(self) -> None:
		"""By default, nothing is expanded."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		self.assertNotIn("subgraph", code)

	def test_Depth1(self) -> None:
		"""A template is a cluster of its jobs; the local reference is expanded, the foreign one is not."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 1")

		self.assertIn('\tsubgraph "cluster_Test" {', code)
		self.assertIn('\tsubgraph "cluster_Prepare" {', code)
		self.assertIn('\tsubgraph "cluster_Local" {', code)
		self.assertIn('\t\t"Test/Unit" [label=<Unit>, style="filled", fillcolor="#f2f2f2"];', code)
		self.assertIn('\t\t"Test/Unit" -> "Test/Report";', code)
		self.assertIn('\t\t{rank=same; "Test/Unit"; "Test/Lint";}', code)
		self.assertNotIn("cluster_Publish", code)

	def test_Depth1_Edges(self) -> None:
		"""An edge to a cluster ends at its border, pointing at the first job needing none."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 1")

		self.assertIn('\t"Prepare/Prepare" -> "Build" [ltail="cluster_Prepare"];', code)
		self.assertIn('\t"Build" -> "Test/Unit" [lhead="cluster_Test"];', code)
		self.assertIn('\t"Test/Report" -> "Publish" [ltail="cluster_Test"];', code)

	def test_Matrix(self) -> None:
		"""A matrix is one node, although the pipeline holds an instance per combination."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 1")

		self.assertIn(
			'\t"Build" [label=<Build<BR/><FONT POINT-SIZE="8" COLOR="#3d4652">matrix: python, system</FONT>>, '
			'style="filled", fillcolor="#f2f2f2", peripheries="2"];',
			code
		)
		self.assertNotIn("cluster_Build", code)

	def test_Matrix_Calls(self) -> None:
		"""A matrix calling a template is one node too; its instances aren't expanded."""
		with TemporaryDirectory() as directory:
			(Path(directory) / "Test.yml").write_text(TEST, encoding="utf-8")
			(Path(directory) / "Matrix.yml").write_text(dedent("""\
				on: push
				jobs:
				  Tests:
				    uses: ./.github/workflows/Test.yml
				    strategy:
				      matrix:
				        python: ['3.13', '3.14']
			"""), encoding="utf-8")
			code = str(PipelineDotGraph(Workflow.FromFile(Path(directory) / "Matrix.yml"), depth=1))

		self.assertNotIn("subgraph", code)
		self.assertIn('style="rounded,filled", peripheries="2", tooltip="uses: ./.github/workflows/Test.yml"', code)

	def test_Drawn(self) -> None:
		"""The jobs and workflows drawn are listed once each."""
		with TemporaryDirectory() as directory:
			workflows = Path(directory)
			(workflows / "Pipeline.yml").write_text(PIPELINE, encoding="utf-8")
			(workflows / "Prepare.yml").write_text(PREPARE, encoding="utf-8")
			(workflows / "Test.yml").write_text(TEST, encoding="utf-8")
			resolver = WorkflowResolver({"Owner/Repo": workflows})
			graph = PipelineDotGraph(resolver.Load(workflows / "Pipeline.yml"), resolver, depth=1)

		self.assertEqual(["Pipeline", "Prepare", "Test"], [workflow.Name for workflow in graph.Workflows])
		self.assertEqual(
			["Prepare", "Prepare", "Build", "Test", "Unit", "Lint", "Report", "Publish", "Local"],
			[job.Name for job in graph.Jobs]
		)
		self.assertEqual("Pipeline.yml:7", graph.Jobs[0].Location)
		self.assertEqual("Prepare.yml:7", graph.Jobs[1].Location)

	@mark.skipif(which("dot") is None, reason="Graphviz isn't installed.")
	def test_Syntax(self) -> None:
		"""Graphviz accepts the graph."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 1")

		result = subprocess_run(["dot", "-Tsvg"], input=code, capture_output=True, text=True, check=False)

		self.assertEqual(0, result.returncode, result.stderr)
		self.assertEqual("", result.stderr)


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Links(Testcase):
	"""In HTML, a job links to the page the 'gha' domain resolves its template to."""

	def test_Node(self) -> None:
		"""Test.yml has a page; Prepare.yml has none."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory)

		test = next(line for line in code.splitlines() if line.startswith('\t"Test" ['))
		prepare = next(line for line in code.splitlines() if line.startswith('\t"Prepare" ['))
		self.assertIn(' URL="templates.html#gha-workflow-Test" target="_top"];', test)
		self.assertNotIn("URL=", prepare)
		self.assertNotIn("gha-link", code)

	def test_Cluster(self) -> None:
		"""An expanded template links its cluster."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":depth: 1")

		self.assertIn('\t\tURL="templates.html#gha-workflow-Test" target="_top"\n', code)

	def test_Disabled(self) -> None:
		"""':link: no' links nothing."""
		with TemporaryDirectory() as directory:
			(code, ), _ = build(directory, ":link: no")

		self.assertNotIn("URL=", code)

	def test_WithoutDomain(self) -> None:
		"""Without the 'gha' domain, nothing is linked, and nothing of the marker remains."""
		with TemporaryDirectory() as directory:
			(code, ), warnings = build(directory, configuration=CONFIGURATION_WITHOUT_DOMAIN, directive="pipeline-graph")

		self.assertNotIn("URL=", code)
		self.assertNotIn("gha-link", code)
		self.assertEqual([], [warning for warning in warnings if "pipeline-graph" in warning])

	def test_Extension(self) -> None:
		"""With pyTooling's extension, a job links to the page a 'gha:workflow' directive documents its template on."""
		with TemporaryDirectory() as directory:
			(code, ), warnings = build(
				directory,
				configuration=CONFIGURATION_EXTENSION,
				templates=".. gha:workflow:: Test\n\nTemplates\n#########\n"
			)

		test = next(line for line in code.splitlines() if line.startswith('\t"Test" ['))
		prepare = next(line for line in code.splitlines() if line.startswith('\t"Prepare" ['))
		self.assertIn(' URL="templates.html#', test)
		self.assertNotIn("URL=", prepare)
		self.assertNotIn("gha-link", code)
		self.assertEqual([], [warning for warning in warnings if "gha" in warning])


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class RefCheck(Testcase):
	"""A job calling a template of the documented repository at another ref than 'gha_ref' is reported."""

	def test_Drift(self) -> None:
		"""Test.yml is called at 'dev' while the documentation describes 'r1'; a foreign template isn't checked."""
		with TemporaryDirectory() as directory:
			_, warnings = build(directory, configuration=CONFIGURATION + 'gha_ref = "r1"\n')

		drifts = [warning for warning in warnings if "[gha.ref]" in warning]
		self.assertEqual(1, len(drifts))
		self.assertTrue(drifts[0].endswith(
			"index.rst:9: WARNING: gha:pipeline-graph: Job 'Test' calls 'Test.yml' at ref 'dev', but the documentation "
			"describes ref 'r1' (Pipeline.yml:22). [gha.ref]"
		), drifts[0])

	def test_Unconfigured(self) -> None:
		"""Without 'gha_ref', refs aren't checked."""
		with TemporaryDirectory() as directory:
			_, warnings = build(directory)

		self.assertEqual([], [warning for warning in warnings if "gha" in warning])


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Errors(Testcase):
	"""A mistake is reported where the graph would be."""

	def test_MissingFile(self) -> None:
		"""A workflow file that doesn't exist."""
		with TemporaryDirectory() as directory:
			codes, warnings = build(directory, path="../.github/workflows/Missing.yml")

		self.assertEqual([], codes)
		self.assertTrue(any("ERROR: gha:pipeline-graph: Couldn't draw '../.github/workflows/Missing.yml'" in warning
			for warning in warnings), warnings)

	def test_Direction(self) -> None:
		"""A direction other than LR or TB."""
		with TemporaryDirectory() as directory:
			codes, warnings = build(directory, ":direction: RL")

		self.assertEqual([], codes)
		self.assertTrue(any("gha:pipeline-graph::direction: 'RL' not an accepted value" in warning
			for warning in warnings), warnings)

	def test_Boolean(self) -> None:
		"""A boolean option that is neither yes nor no."""
		with TemporaryDirectory() as directory:
			codes, warnings = build(directory, ":reduce: maybe")

		self.assertEqual([], codes)
		self.assertTrue(any("gha:pipeline-graph::reduce: 'maybe' not supported" in warning for warning in warnings))


@mark.skipif(not sphinxIsSupported, reason="Sphinx 9.1 needs Python 3.12 or newer.")
class Parameters(Testcase):
	"""The parameters of :class:`PipelineDotGraph`."""

	def test_Workflow(self) -> None:
		with self.assertRaises(ValueError) as context:
			PipelineDotGraph(None)

		self.assertEqual("Parameter 'workflow' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			PipelineDotGraph("Pipeline.yml")

		self.assertEqual("Parameter 'workflow' is not of type 'Workflow'.", str(context.exception))

	def test_Others(self) -> None:
		with TemporaryDirectory() as directory:
			(Path(directory) / "Pipeline.yml").write_text(PIPELINE, encoding="utf-8")
			workflow = Workflow.FromFile(Path(directory) / "Pipeline.yml")

		with self.assertRaises(TypeError) as context:
			PipelineDotGraph(workflow, resolver={})
		self.assertEqual("Parameter 'resolver' is not of type 'WorkflowResolver'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			PipelineDotGraph(workflow, direction="RL")
		self.assertEqual("Parameter 'direction' is neither 'LR' nor 'TB'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			PipelineDotGraph(workflow, depth="1")
		self.assertEqual("Parameter 'depth' is not of type 'int'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			PipelineDotGraph(workflow, depth=-1)
		self.assertEqual("Parameter 'depth' is negative.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			PipelineDotGraph(workflow, reduce="yes")
		self.assertEqual("Parameter 'reduce' is not of type 'bool'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			PipelineDotGraph(workflow, link=1)
		self.assertEqual("Parameter 'link' is not of type 'bool'.", str(context.exception))

	def test_Resolver(self) -> None:
		"""Without a resolver, only local references are expanded."""
		with TemporaryDirectory() as directory:
			(Path(directory) / "Pipeline.yml").write_text(PIPELINE, encoding="utf-8")
			(Path(directory) / "Prepare.yml").write_text(PREPARE, encoding="utf-8")
			code = str(PipelineDotGraph(Workflow.FromFile(Path(directory) / "Pipeline.yml"), depth=1))

		self.assertIn('subgraph "cluster_Local"', code)
		self.assertNotIn('subgraph "cluster_Test"', code)
		self.assertIn("Owner/Repo@dev</FONT>", code)
