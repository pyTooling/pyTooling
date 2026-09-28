# ==================================================================================================================== #
#             _____           _ _               ____ ___                                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ _|                                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |    | |                                                               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___ | |                                                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|___|                                                              #
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
Unit tests for :mod:`pyTooling.CI.Workflow`.
"""
from pathlib               import Path
from tempfile              import TemporaryDirectory
from textwrap              import dedent, indent
from typing                import Any

from pyTooling.CI.Workflow import AccessLevel, InputType, Workflow, WorkflowError, WorkflowResolver
from pyTooling.CI.Workflow import Input, Job, Matrix, Permission, UsesReference
from pyTooling.CI.Workflow import DefinedJob, DefinedMatrix, DefinedMatrixJob, DefinedMatrixWorkflow, DefinedPipeline
from pyTooling.CI.Workflow import DefinedWorkflow
from pyTooling.CI.GitHub   import Pipeline as GitHubPipeline
from pyTooling.CI.Pipeline import Matrix as CIMatrix, NeedDependencyCycleError, Pipeline as CIPipeline
from pyTooling.Graph       import Graph
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


CALLABLE = dedent("""\
	name: Build Package

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
	        description: 'Conditions.'
	        required: false
	        default: |
	          default-branch
	          release-tag
	        type: string
	    outputs:
	      version:
	        description: "Version of the package."
	        value: ${{ jobs.Build.outputs.version }}
	    secrets:
	      PYPI_TOKEN:
	        description: "Token for PyPI."
	        required: true
	      CODECOV_TOKEN:

	permissions:
	  contents: read

	jobs:
	  Params:
	    name: Parameters
	    runs-on: ubuntu-26.04
	    outputs:
	      jobs: ${{ steps.params.outputs.jobs }}
	    steps:
	      - name: Compute
	        id: params
	        run: echo "jobs=[]" >> "${GITHUB_OUTPUT}"

	  Build:
	    runs-on: ${{ matrix.runs-on }}
	    needs: Params
	    if: inputs.dry_run == false
	    permissions:
	      contents: write
	      id-token: write
	    strategy:
	      fail-fast: false
	      matrix:
	        include: ${{ fromJson(needs.Params.outputs.jobs) }}
	    outputs:
	      version: ${{ steps.version.outputs.version }}
	    steps:
	      - name: Checkout
	        uses: actions/checkout@v6
	      - uses: actions/setup-python@v6
	        with:
	          python-version: ${{ inputs.python_version }}
	      - id: version
	        if: success()
	        run: echo "version=1.0.0" >> "${GITHUB_OUTPUT}"

	  Static:
	    runs-on: [self-hosted, linux]
	    needs: [Params, Build]
	    strategy:
	      matrix:
	        system: [ubuntu, windows]
	        python: ['3.13', '3.14']
	        exclude:
	          - system: windows
	            python: '3.13'
	    steps:
	      - uses: docker://alpine:3.22
""")


CALLER = dedent("""\
	name: Pipeline

	on:
	  push:
	  workflow_dispatch:

	jobs:
	  Prepare:
	    uses: Owner/Repo/.github/workflows/Prepare.yml@r1

	  Package:
	    uses: owner/repo/.github/workflows/Package.yml@dev
	    needs:
	      - Prepare
	    permissions:
	      contents: read
	      actions: write
	    with:
	      package_name: myPackage
	      delay:        10
	    secrets:
	      PYPI_TOKEN: ${{ secrets.PYPI_TOKEN }}

	  Local:
	    uses: ./.github/workflows/Package.yml
	    needs: [Prepare, Package]
	    secrets: inherit

	  Foreign:
	    uses: other/repo/.github/workflows/Package.yml@v1
	    needs: [Prepare, Package, Local]
""")


PREPARE = dedent("""\
	on:
	  workflow_call:

	permissions: read-all

	jobs:
	  Prepare:
	    runs-on: ubuntu-26.04
	    steps:
	      - run: echo
""")


class Fixture(Testcase):
	"""Writes workflow files into a temporary directory, removed after each test."""

	_directory: TemporaryDirectory
	_path:      Path

	def setUp(self) -> None:
		self._directory = TemporaryDirectory()
		self._path = Path(self._directory.name)

	def tearDown(self) -> None:
		self._directory.cleanup()

	def _write(self, name: str, content: str) -> Path:
		"""
		Write a workflow file.

		:param name:    Name of the file.
		:param content: Content of the file.
		:returns:       Path to the file.
		"""
		path = self._path / name
		path.write_text(content, encoding="utf-8")

		return path


class References(Testcase):
	def test_Workflow(self) -> None:
		uses = UsesReference("pyTooling/Actions/.github/workflows/Package.yml@r8", 12)

		self.assertEqual("pyTooling/Actions", uses.Repository)
		self.assertEqual(".github/workflows/Package.yml", uses.Path)
		self.assertEqual("r8", uses.Ref)
		self.assertEqual("Package.yml", uses.FileName)
		self.assertEqual("Package", uses.Stem)
		self.assertTrue(uses.IsWorkflow)
		self.assertFalse(uses.IsLocal)
		self.assertFalse(uses.IsDocker)
		self.assertEqual("pyTooling/Actions/.github/workflows/Package.yml@r8", str(uses))
		self.assertEqual(12, uses.Line)
		self.assertEqual("line 12", uses.Location)

	def test_Action(self) -> None:
		uses = UsesReference("actions/checkout@v6", 1)

		self.assertEqual("actions/checkout", uses.Repository)
		self.assertEqual("", uses.Path)
		self.assertEqual("v6", uses.Ref)
		self.assertEqual("", uses.FileName)
		self.assertFalse(uses.IsWorkflow)

	def test_Action_Path(self) -> None:
		uses = UsesReference("pyTooling/Actions/.github/actions/ComputeRequirements@dev", 1)

		self.assertEqual("pyTooling/Actions", uses.Repository)
		self.assertEqual(".github/actions/ComputeRequirements", uses.Path)
		self.assertFalse(uses.IsWorkflow)

	def test_Local(self) -> None:
		uses = UsesReference("./.github/workflows/Package.yaml", 1)

		self.assertIsNone(uses.Repository)
		self.assertIsNone(uses.Ref)
		self.assertEqual(".github/workflows/Package.yaml", uses.Path)
		self.assertTrue(uses.IsLocal)
		self.assertTrue(uses.IsWorkflow)

	def test_Docker(self) -> None:
		uses = UsesReference("docker://alpine:3.22", 1)

		self.assertIsNone(uses.Repository)
		self.assertEqual("alpine:3.22", uses.Path)
		self.assertTrue(uses.IsDocker)
		self.assertFalse(uses.IsWorkflow)
		self.assertEqual("", uses.Stem)

	def test_NoRef(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference("actions/checkout", 1)

		self.assertEqual("Parameter 'text' names a repository without a ref.", str(context.exception))
		self.assertEqual(["Got 'actions/checkout'."], context.exception.__notes__)

	def test_NoRepository(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference("checkout@v6", 1)

		self.assertEqual("Parameter 'text' names no repository as 'owner/repo'.", str(context.exception))

	def test_Empty(self) -> None:
		with self.assertRaises(ValueError):
			_ = UsesReference("", 1)

	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference(None, 1)

		self.assertEqual("Parameter 'text' is None.", str(context.exception))

	def test_Line(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference("actions/checkout@v6", 0)

		self.assertEqual("Parameter 'line' is not positive.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = UsesReference("actions/checkout@v6", "1")


class Parameters(Fixture):
	def test_Workflow(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual("Package", workflow.Name)
		self.assertEqual("Package", str(workflow))
		self.assertEqual("Build Package", workflow.DisplayName)
		self.assertEqual(self._path / "Package.yml", workflow.Path)
		self.assertEqual(("workflow_call", ), workflow.Triggers)
		self.assertTrue(workflow.IsCallable)
		self.assertIsNone(workflow.Parent)
		self.assertIs(workflow, workflow.Workflow)
		self.assertEqual("Package.yml:1", workflow.Location)

	def test_Inputs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(["package_name", "python_version", "dry_run", "pages_on"], list(workflow.Inputs))

		packageName = workflow.Inputs["package_name"]
		self.assertIsInstance(packageName, Input)
		self.assertEqual("package_name", packageName.Name)
		self.assertIs(InputType.String, packageName.Type)
		self.assertTrue(packageName.Required)
		self.assertIsNone(packageName.Default)
		self.assertEqual("Name of the package.", packageName.Description)
		self.assertEqual("Package.yml:6", packageName.Location)
		self.assertIs(workflow, packageName.Parent)

		pythonVersion = workflow.Inputs["python_version"]
		self.assertFalse(pythonVersion.Required)
		self.assertEqual("3.14", pythonVersion.Default)
		self.assertIs(str, type(pythonVersion.Default))

		dryRun = workflow.Inputs["dry_run"]
		self.assertIs(InputType.Boolean, dryRun.Type)
		self.assertIs(False, dryRun.Default)
		self.assertIsNone(dryRun.Description)

		self.assertEqual("default-branch\nrelease-tag\n", workflow.Inputs["pages_on"].Default)

	def test_Outputs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		version = workflow.Outputs["version"]
		self.assertEqual("Version of the package.", version.Description)
		self.assertEqual("${{ jobs.Build.outputs.version }}", version.Value)
		self.assertEqual(27, version.Line)

	def test_Secrets(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(["PYPI_TOKEN", "CODECOV_TOKEN"], list(workflow.Secrets))
		self.assertTrue(workflow.Secrets["PYPI_TOKEN"].Required)
		self.assertEqual("Token for PyPI.", workflow.Secrets["PYPI_TOKEN"].Description)
		self.assertFalse(workflow.Secrets["CODECOV_TOKEN"].Required)
		self.assertIsNone(workflow.Secrets["CODECOV_TOKEN"].Description)

	def test_Permissions(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(["contents"], list(workflow.Permissions))
		self.assertIs(AccessLevel.Read, workflow.Permissions["contents"].Level)
		self.assertEqual("contents: read", str(workflow.Permissions["contents"]))

	def test_Triggers(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		self.assertEqual(("push", "workflow_dispatch"), workflow.Triggers)
		self.assertFalse(workflow.IsCallable)
		self.assertEqual({}, workflow.Inputs)
		self.assertIsNone(workflow.Permissions)

	def test_Triggers_Forms(self) -> None:
		jobs = "jobs:\n  Job:\n    runs-on: ubuntu-26.04\n    steps: []\n"

		self.assertEqual(("push", ), Workflow.FromFile(self._write("A.yml", f"on: push\n{jobs}")).Triggers)
		workflow = Workflow.FromFile(self._write("B.yml", f"on: [push, workflow_call]\n{jobs}"))
		self.assertEqual(("push", "workflow_call"), workflow.Triggers)
		self.assertTrue(Workflow.FromFile(self._write("C.yml", f"on:\n  workflow_call:\n{jobs}")).IsCallable)

	def test_PermissionsShortForm(self) -> None:
		workflow = Workflow.FromFile(self._write("Prepare.yml", PREPARE))

		permission = workflow.Permissions[Permission.ALL_SCOPES]
		self.assertIs(AccessLevel.Read, permission.Level)
		self.assertEqual("read-all", str(permission))


class Jobs(Fixture):
	def test_Order(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(3, len(workflow))
		self.assertEqual(["Params", "Build", "Static"], [job.Name for job in workflow])
		self.assertIn("Build", workflow)
		self.assertNotIn("Unknown", workflow)

	def test_Steps(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		params = workflow.Jobs["Params"]

		self.assertEqual("Parameters", params.DisplayName)
		self.assertEqual(("ubuntu-26.04", ), params.RunsOn)
		self.assertIsNone(params.Uses)
		self.assertIsNone(params.Condition)
		self.assertIsNone(params.Permissions)
		self.assertEqual({"jobs": "${{ steps.params.outputs.jobs }}"}, params.Outputs)
		self.assertEqual(1, len(params))
		self.assertEqual("Compute", params.Steps[0].Name)
		self.assertEqual("params", params.Steps[0].ID)
		self.assertIn("GITHUB_OUTPUT", params.Steps[0].Run)
		self.assertEqual("Package.yml:40", params.Location)

		build = workflow.Jobs["Build"]
		self.assertEqual(3, len(build))
		steps = list(build)
		self.assertEqual("actions/checkout@v6", str(steps[0].Uses))
		self.assertIs(steps[0], steps[0].Uses.Parent)
		self.assertIs(workflow, steps[0].Uses.Workflow)
		self.assertIsNone(steps[1].Name)
		self.assertEqual("success()", steps[2].Condition)
		self.assertEqual("Package.yml:69", steps[2].Location)

	def test_Actions(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(
			["actions/checkout@v6", "actions/setup-python@v6", "docker://alpine:3.22"],
			[str(action) for action in workflow.IterateActions()]
		)

	def test_Needs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		params, build, static = workflow

		self.assertEqual((), params.Needs)
		self.assertEqual(("Params", ), build.NeedNames)
		self.assertEqual((params, ), build.Needs)
		self.assertEqual((params, build), static.Needs)

	def test_Condition(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual("inputs.dry_run == false", workflow.Jobs["Build"].Condition)

	def test_Permissions(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		permissions = workflow.Jobs["Build"].Permissions

		self.assertEqual(["contents", "id-token"], list(permissions))
		self.assertIs(AccessLevel.Write, permissions["id-token"].Level)
		self.assertIs(workflow.Jobs["Build"], permissions["id-token"].Parent)
		self.assertEqual("Package.yml:56", permissions["id-token"].Location)

	def test_Matrix(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		dynamic = workflow.Jobs["Build"].Matrix
		self.assertTrue(dynamic.IsDynamic)
		self.assertEqual("${{ fromJson(needs.Params.outputs.jobs) }}", dynamic.Include)
		self.assertEqual({}, dynamic.Dimensions)
		self.assertEqual("Package.yml:59", dynamic.Location)

		static = workflow.Jobs["Static"].Matrix
		self.assertFalse(static.IsDynamic)
		self.assertEqual({"system": ["ubuntu", "windows"], "python": ["3.13", "3.14"]}, static.Dimensions)
		self.assertEqual([{"system": "windows", "python": "3.13"}], static.Exclude)
		self.assertIsNone(static.Include)
		self.assertIsNone(static.Expression)
		self.assertEqual(("self-hosted", "linux"), workflow.Jobs["Static"].RunsOn)

		self.assertIsNone(workflow.Jobs["Params"].Matrix)

	def test_Matrix_Expression(self) -> None:
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Job:
			    runs-on: ubuntu-26.04
			    strategy:
			      matrix: ${{ fromJson(inputs.matrix) }}
			    steps: []
		""")))

		self.assertTrue(workflow.Jobs["Job"].Matrix.IsDynamic)
		self.assertEqual("${{ fromJson(inputs.matrix) }}", workflow.Jobs["Job"].Matrix.Expression)

	def test_Calls(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		package = workflow.Jobs["Package"]

		self.assertEqual("owner/repo", package.Uses.Repository)
		self.assertEqual("dev", package.Uses.Ref)
		self.assertEqual("Pipeline.yml:12", package.Uses.Location)
		self.assertEqual((), package.RunsOn)
		self.assertEqual(0, len(package))
		self.assertEqual({"package_name": "myPackage", "delay": 10}, package.With)
		self.assertEqual({"PYPI_TOKEN": "${{ secrets.PYPI_TOKEN }}"}, package.Secrets)
		self.assertFalse(package.InheritsSecrets)

		local = workflow.Jobs["Local"]
		self.assertTrue(local.InheritsSecrets)
		self.assertEqual({}, local.Secrets)
		self.assertTrue(local.Uses.IsLocal)


class Combinations(Fixture):
	def _matrix(self, matrix: str) -> Matrix:
		"""
		Read a workflow whose only job has the given matrix.

		:param matrix: The matrix' YAML, indented as the value of 'matrix'.
		:returns:      The matrix.
		"""
		workflow = Workflow.FromFile(self._write("A.yml", "on: push\njobs:\n  Job:\n    runs-on: x\n    strategy:\n"
			f"      matrix:\n{indent(dedent(matrix), '        ')}    steps: []\n"))

		return workflow.Jobs["Job"].Matrix

	def test_Product(self) -> None:
		"""The last dimension varies fastest; 'exclude' matches an entry's pairs only."""
		matrix = self._matrix("""\
			system: [ubuntu, windows]
			python: ['3.13', '3.14']
			exclude:
			  - system: windows
			    python: '3.13'
		""")

		self.assertEqual(
			[
				{"system": "ubuntu", "python": "3.13"},
				{"system": "ubuntu", "python": "3.14"},
				{"system": "windows", "python": "3.14"}
			],
			matrix.Combinations
		)

	def test_Include(self) -> None:
		"""GitHub's example: an entry extends what it doesn't change, or becomes a combination of its own."""
		matrix = self._matrix("""\
			fruit: [apple, pear]
			animal: [cat, dog]
			include:
			  - color: green
			  - color: pink
			    animal: cat
			  - fruit: apple
			    shape: circle
			  - fruit: banana
			  - fruit: banana
			    animal: cat
		""")

		self.assertEqual(
			[
				{"fruit": "apple", "animal": "cat", "color": "pink", "shape": "circle"},
				{"fruit": "apple", "animal": "dog", "color": "green", "shape": "circle"},
				{"fruit": "pear", "animal": "cat", "color": "pink"},
				{"fruit": "pear", "animal": "dog", "color": "green"},
				{"fruit": "banana"},
				{"fruit": "banana", "animal": "cat"}
			],
			matrix.Combinations
		)

	def test_IncludeOnly(self) -> None:
		matrix = self._matrix("""\
			include:
			  - {os: ubuntu, shell: bash}
			  - {os: windows, shell: pwsh}
		""")

		self.assertEqual([{"os": "ubuntu", "shell": "bash"}, {"os": "windows", "shell": "pwsh"}], matrix.Combinations)

	def test_Dynamic(self) -> None:
		matrix = self._matrix("include: ${{ fromJson(inputs.jobs) }}\n")

		with self.assertRaises(WorkflowError) as context:
			_ = matrix.Combinations

		self.assertEqual("Matrix is dynamic; its combinations are known at run time only.", str(context.exception))
		self.assertEqual(6, context.exception.Line)

	def test_NoMappings(self) -> None:
		matrix = self._matrix("os: [ubuntu]\ninclude: [ubuntu]\n")

		with self.assertRaises(WorkflowError) as context:
			_ = matrix.Combinations

		self.assertEqual("Key 'include' of the matrix is not a list of mappings.", str(context.exception))


class ToPipeline(Fixture):
	def _resolver(self) -> WorkflowResolver:
		"""
		Write the caller and the workflows it calls, and map ``owner/repo`` to their directory.

		:returns: The resolver.
		"""
		self._write("Pipeline.yml", CALLER)
		self._write("Package.yml", CALLABLE)
		self._write("Prepare.yml", PREPARE)

		return WorkflowResolver({"owner/repo": self._path})

	def test_Elements(self) -> None:
		"""A job running steps is a job, a job with a matrix a matrix; each links to its definition."""
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		pipeline = workflow.ToPipeline()

		self.assertIsInstance(pipeline, DefinedPipeline)
		self.assertIsInstance(pipeline, CIPipeline)
		self.assertEqual("Package", pipeline.Name)
		self.assertIs(workflow, pipeline.Definition)
		self.assertEqual(["Params", "Build", "Static"], [element.Name for element in pipeline.Elements])

		params = pipeline["Params"]
		self.assertIsInstance(params, DefinedJob)
		self.assertIs(workflow.Jobs["Params"], params.Definition)
		self.assertEqual(["Compute"], [str(step) for step in params.Steps])
		self.assertIs(workflow.Jobs["Params"].Steps[0], params.Steps[0].Definition)

		build = pipeline["Build"]
		self.assertIsInstance(build, DefinedMatrix)
		self.assertEqual("inputs.dry_run == false", build.Condition)
		self.assertEqual(0, len(build))

		static = pipeline["Static"]
		self.assertEqual(
			["Static (ubuntu, 3.13)", "Static (ubuntu, 3.14)", "Static (windows, 3.14)"], [str(job) for job in static]
		)
		self.assertIsInstance(static["Static (ubuntu, 3.14)"], DefinedMatrixJob)
		self.assertEqual(["Run docker://alpine:3.22"], [str(step) for step in static["Static (ubuntu, 3.14)"].Steps])

	def test_Steps(self) -> None:
		"""A step without a name is named as GitHub displays it."""
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Job:
			    runs-on: x
			    steps:
			      - name: Checkout
			        uses: actions/checkout@v6
			      - uses: actions/setup-python@v6
			      - run: |
			          echo "one"
			          echo "two"
			        if: success()
		""")))
		steps = workflow.ToPipeline()["Job"].Steps

		self.assertEqual(["Checkout", "Run actions/setup-python@v6", 'Run echo "one"'], [str(step) for step in steps])
		self.assertEqual("success()", steps[2].Condition)

	def test_Needs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		pipeline = workflow.ToPipeline()

		self.assertEqual([pipeline["Params"]], pipeline["Build"].Needs)
		self.assertEqual([pipeline["Params"], pipeline["Build"]], pipeline["Static"].Needs)
		self.assertEqual([pipeline["Build"], pipeline["Static"]], pipeline["Params"].Dependents)

	def test_Calls(self) -> None:
		"""A called workflow is expanded, if the resolver reads it; a foreign one stays empty."""
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml").ToPipeline(resolver)

		package = pipeline["Package"]
		self.assertIsInstance(package, DefinedWorkflow)
		self.assertEqual("owner/repo/.github/workflows/Package.yml@dev", package.Reference)
		self.assertIs(resolver.Load(self._path / "Package.yml"), package.CalledWorkflow)
		self.assertEqual(["Params", "Build", "Static"], [element.Name for element in package.Elements])
		self.assertEqual("Package / Params", package["Params"].QualifiedName)
		self.assertEqual([package["Params"]], package["Build"].Needs)

		local = pipeline["Local"]
		self.assertEqual(3, len(local))
		self.assertIsNot(package["Params"], local["Params"])
		self.assertEqual(["Prepare"], [element.Name for element in pipeline["Prepare"].Elements])

		foreign = pipeline["Foreign"]
		self.assertEqual("other/repo/.github/workflows/Package.yml@v1", foreign.Reference)
		self.assertIsNone(foreign.CalledWorkflow)
		self.assertEqual(0, len(foreign))

	def test_Calls_Depth(self) -> None:
		"""A depth of 0 expands no call."""
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml").ToPipeline(resolver, depth=0)

		self.assertEqual([0, 0, 0, 0], [len(element) for element in pipeline])
		self.assertIsNone(pipeline["Package"].CalledWorkflow)

	def test_Calls_WithoutResolver(self) -> None:
		pipeline = Workflow.FromFile(self._write("Pipeline.yml", CALLER)).ToPipeline()

		self.assertEqual([0, 0, 0, 0], [len(element) for element in pipeline])

	def test_Calls_Matrix(self) -> None:
		"""A matrix calling a workflow is a matrix of called workflows, each expanded."""
		self._write("Prepare.yml", PREPARE)
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Tests:
			    uses: ./.github/workflows/Prepare.yml
			    strategy:
			      matrix:
			        python: ['3.13', '3.14']
		""")))
		tests = workflow.ToPipeline(WorkflowResolver())["Tests"]

		self.assertIsInstance(tests, DefinedMatrix)
		self.assertEqual(["Tests (3.13)", "Tests (3.14)"], [str(instance) for instance in tests])
		self.assertIsInstance(tests["Tests (3.14)"], DefinedMatrixWorkflow)
		self.assertEqual("Tests (3.14) / Prepare", tests["Tests (3.14)"]["Prepare"].QualifiedName)

	def test_Recursion(self) -> None:
		workflow = Workflow.FromFile(self._write("Self.yml", dedent("""\
			on: workflow_call
			jobs:
			  Again:
			    uses: ./.github/workflows/Self.yml
		""")))

		with self.assertRaises(WorkflowError) as context:
			_ = workflow.ToPipeline(WorkflowResolver())

		self.assertEqual("Workflow 'Self' calls itself.", str(context.exception))
		self.assertIn("Calls: Self -> Self.", context.exception.__notes__)

	def test_Parameters(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		with self.assertRaises(TypeError) as context:
			_ = workflow.ToPipeline({})

		self.assertEqual("Parameter 'resolver' is not of type 'WorkflowResolver'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = workflow.ToPipeline(depth="1")

		self.assertEqual("Parameter 'depth' is not of type 'int'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = workflow.ToPipeline(depth=-1)

		self.assertEqual("Parameter 'depth' is negative.", str(context.exception))

	def test_Definition(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		with self.assertRaises(ValueError) as context:
			_ = DefinedJob(None)

		self.assertEqual("Parameter 'definition' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = DefinedJob(workflow)

		self.assertEqual("Parameter 'definition' is not of type 'Job'.", str(context.exception))

		with self.assertRaises(ValueError) as context:
			_ = DefinedMatrix(workflow.Jobs["Package"])

		self.assertEqual("Parameter 'definition' declares no matrix.", str(context.exception))

	def test_ToGraph(self) -> None:
		"""The graph of the pipeline drops a dependency a longer path implies."""
		pipeline = Workflow.FromFile(self._write("Pipeline.yml", CALLER)).ToPipeline()

		def edges(graph: Graph) -> list[tuple[str, str]]:
			"""
			Nested function returning the edges of a graph by the names of the elements they connect.

			:param graph: The graph.
			:returns:     The edges, as pairs of the source's and the destination's name.
			"""
			return [(edge.Source.Value.Name, edge.Destination.Value.Name) for edge in graph.IterateEdges()]

		self.assertEqual([("Package", "Prepare"), ("Local", "Package"), ("Foreign", "Local")], edges(pipeline.ToGraph()))
		self.assertEqual(
			[
				("Package", "Prepare"),
				("Local", "Prepare"), ("Local", "Package"),
				("Foreign", "Prepare"), ("Foreign", "Package"), ("Foreign", "Local")
			],
			edges(pipeline.ToGraph(reduce=False))
		)

	def test_ToGraph_Diamond(self) -> None:
		pipeline = Workflow.FromFile(self._write("Diamond.yml", dedent("""\
			on: push
			jobs:
			  A: {runs-on: x, steps: []}
			  B: {runs-on: x, steps: [], needs: A}
			  C: {runs-on: x, steps: [], needs: A}
			  D: {runs-on: x, steps: [], needs: [A, B, C]}
		"""))).ToPipeline()

		self.assertEqual(
			[("B", "A"), ("C", "A"), ("D", "B"), ("D", "C")],
			[(edge.Source.Value.Name, edge.Destination.Value.Name) for edge in pipeline.ToGraph().IterateEdges()]
		)


def _job(name: str, conclusion: str = "success") -> dict[str, Any]:
	"""
	Build a job of a run, as the GitHub REST API lists it.

	:param name:       The job's name, including any calling workflows' prefixes.
	:param conclusion: Optional, how the job ended. Default: ``'success'``.
	:returns:          The job.
	"""
	return {
		"id": 1, "name": name, "status": "completed", "conclusion": conclusion,
		"created_at": "2026-09-17T10:00:00Z", "started_at": "2026-09-17T10:00:10Z",
		"completed_at": "2026-09-17T10:01:00Z", "steps": []
	}


class ApplyNeeds(Fixture):
	def _run(self, *names: tuple[str, str]) -> GitHubPipeline:
		"""
		Build a run of :data:`CALLER` reporting the given jobs.

		:param names: The jobs' names and conclusions.
		:returns:     The run.
		"""
		run = {"id": 4711, "name": "Pipeline", "status": "completed", "conclusion": "success", "head_sha": "0123abcd"}

		return GitHubPipeline.FromJSON(run, [_job(name, conclusion) for name, conclusion in names])

	def test_Calls(self) -> None:
		"""The jobs of the run and of its called workflows get the dependencies of the workflow files."""
		self._write("Package.yml", CALLABLE)
		self._write("Prepare.yml", PREPARE)
		resolver = WorkflowResolver({"owner/repo": self._path})
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(
			("Prepare / Prepare", "success"),
			("Package / Parameters", "success"),
			("Package / Build (ubuntu-26.04, 3.14)", "success"),
			("Package / Static (ubuntu, 3.13)", "success"),
			("Package / Static (ubuntu, 3.14)", "success"),
			("Package / Static (windows, 3.14)", "success"),
			("Local / Parameters", "success"),
			("Local / Build", "skipped"),
			("Foreign / Publish", "success")
		)

		missing = workflow.ApplyNeeds(run, resolver)

		self.assertEqual([run["Prepare"]], run["Package"].Needs)
		self.assertEqual([run["Prepare"], run["Package"]], run["Local"].Needs)
		self.assertEqual([run["Prepare"], run["Package"], run["Local"]], run["Foreign"].Needs)

		package = run["Package"]
		self.assertIsInstance(package["Build"], CIMatrix)
		self.assertEqual([package["Parameters"]], package["Build"].Needs)
		self.assertEqual([package["Parameters"], package["Build"]], package["Static"].Needs)

		local = run["Local"]
		self.assertEqual([local["Parameters"]], local["Build"].Needs)

		self.assertEqual(["Local / Static"], missing)
		self.assertEqual([], run["Foreign"]["Publish"].Needs)

	def test_Cycle(self) -> None:
		"""A need the run had already, which closes a cycle with the needs of the file, is found by validating the run."""
		self._write("Package.yml", CALLABLE)
		self._write("Prepare.yml", PREPARE)
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(("Prepare / Prepare", "success"), ("Package / Parameters", "success"))
		run["Prepare"].AddNeed(run["Package"])

		with self.assertRaises(NeedDependencyCycleError):
			workflow.ApplyNeeds(run)

	def test_WithoutResolver(self) -> None:
		"""Without a resolver, only the jobs of the run's own workflow get dependencies."""
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(
			("Prepare / Prepare", "success"), ("Package / Parameters", "success"), ("Package / Build", "success")
		)

		missing = workflow.ApplyNeeds(run)

		self.assertEqual([run["Prepare"]], run["Package"].Needs)
		self.assertEqual([], run["Package"]["Build"].Needs)
		self.assertEqual(["Local", "Foreign"], missing)

	def test_Twice(self) -> None:
		"""Applying the dependencies again adds nothing."""
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(("Prepare / Prepare", "success"), ("Package / Parameters", "success"))

		workflow.ApplyNeeds(run)
		workflow.ApplyNeeds(run)

		self.assertEqual([run["Prepare"]], run["Package"].Needs)

	def test_Expression(self) -> None:
		"""A job named by an expression can't be looked up, and isn't reported."""
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Prepare: {runs-on: x, steps: []}
			  Test:
			    name: ${{ matrix.os }} Tests
			    runs-on: x
			    needs: Prepare
			    steps: []
		""")))
		run = self._run(("Prepare", "success"), ("ubuntu Tests", "success"))

		self.assertEqual([], workflow.ApplyNeeds(run))
		self.assertEqual([], run["ubuntu Tests"].Needs)

	def test_Parameters(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		with self.assertRaises(ValueError) as context:
			_ = workflow.ApplyNeeds(None)

		self.assertEqual("Parameter 'pipeline' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = workflow.ApplyNeeds(workflow)

		self.assertEqual("Parameter 'pipeline' is not of type 'Workflow'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = workflow.ApplyNeeds(self._run(), {})

		self.assertEqual("Parameter 'resolver' is not of type 'WorkflowResolver'.", str(context.exception))


class Resolver(Fixture):
	def _resolver(self) -> WorkflowResolver:
		"""
		Write the caller and the workflows it calls, and map ``owner/repo`` to their directory.

		:returns: The resolver.
		"""
		self._write("Pipeline.yml", CALLER)
		self._write("Package.yml", CALLABLE)
		self._write("Prepare.yml", PREPARE)

		return WorkflowResolver({"owner/repo": self._path})

	def test_Resolve(self) -> None:
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml")

		prepare = resolver.Resolve(pipeline.Jobs["Prepare"].Uses)
		package = resolver.Resolve(pipeline.Jobs["Package"].Uses)
		self.assertEqual("Prepare", prepare.Name)
		self.assertEqual("Package", package.Name)
		self.assertIs(package, resolver.Resolve(pipeline.Jobs["Local"].Uses))
		self.assertIs(package, resolver.Load(self._path / "Package.yml"))
		self.assertIsNone(resolver.Resolve(pipeline.Jobs["Foreign"].Uses))

	def test_Resolve_Action(self) -> None:
		resolver = self._resolver()
		package = resolver.Load(self._path / "Package.yml")

		self.assertIsNone(resolver.Resolve(package.Jobs["Build"].Steps[0].Uses))

	def test_Resolve_Missing(self) -> None:
		self._write("Pipeline.yml", CALLER)
		resolver = WorkflowResolver({"owner/repo": self._path})
		pipeline = resolver.Load(self._path / "Pipeline.yml")

		with self.assertRaises(WorkflowError) as context:
			_ = resolver.Resolve(pipeline.Jobs["Prepare"].Uses)

		self.assertEqual(f"Workflow 'Prepare.yml' doesn't exist in '{self._path}'.", str(context.exception))
		self.assertEqual(9, context.exception.Line)
		self.assertEqual(self._path / "Pipeline.yml", context.exception.Path)

	def test_CanResolve(self) -> None:
		resolver = WorkflowResolver({"Owner/Repo": self._path})

		for text, expected in (
			("./.github/workflows/Package.yml",             True),
			("owner/repo/.github/workflows/Package.yml@r1", True),
			("OWNER/REPO/.github/workflows/Package.yml@r1", True),
			("other/repo/.github/workflows/Package.yml@r1", False),
			("actions/checkout@v6",                         False),
			("docker://alpine:3.22",                        False)
		):
			with self.subTest(uses=text):
				self.assertIs(expected, resolver.CanResolve(UsesReference(text, 1)))

		with self.assertRaises(ValueError) as context:
			_ = resolver.CanResolve(None)

		self.assertEqual("Parameter 'uses' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = resolver.CanResolve("./.github/workflows/Package.yml")

		self.assertEqual("Parameter 'uses' is not of type 'UsesReference'.", str(context.exception))

	def test_CollectPermissions(self) -> None:
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml")

		self.assertEqual(["contents", "actions"], list(pipeline.CollectPermissions()))

		permissions = pipeline.CollectPermissions(resolver)
		self.assertEqual(["contents", "actions", Permission.ALL_SCOPES, "id-token"], list(permissions))
		self.assertEqual("Package.yml:55", permissions["contents"].Location)
		self.assertIs(AccessLevel.Write, permissions["contents"].Level)
		self.assertEqual("Pipeline.yml:17", permissions["actions"].Location)
		self.assertEqual("Prepare.yml:4", permissions[Permission.ALL_SCOPES].Location)

	def test_Repositories(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = WorkflowResolver({"owner": Path(".")})

		self.assertEqual("Key of parameter 'repositories' is not of the form 'owner/repo'.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = WorkflowResolver({"owner/repo": "."})

		self.assertEqual({"owner/repo": Path(".")}, WorkflowResolver({"Owner/Repo": Path(".")}).Repositories)


class Errors(Fixture):
	def _error(self, content: str) -> WorkflowError:
		"""
		Read a malformed workflow file.

		:param content: Content of the file.
		:returns:       The exception reading it raised.
		"""
		path = self._write("Broken.yml", content)
		with self.assertRaises(WorkflowError) as context:
			_ = Workflow.FromFile(path)

		self.assertEqual(path, context.exception.Path)

		return context.exception

	def test_NotYAML(self) -> None:
		error = self._error("on: push\njobs: [\n")

		self.assertEqual("Workflow file is not a YAML document.", str(error))

	def test_Empty(self) -> None:
		self.assertEqual("Workflow file is empty.", str(self._error("")))

	def test_NoJobs(self) -> None:
		self.assertEqual("Workflow file has no 'jobs' key.", str(self._error("on: push\n")))

	def test_NoOn(self) -> None:
		self.assertEqual("Workflow file has no 'on' key.", str(self._error("jobs: {}\n")))

	def test_UnknownNeed(self) -> None:
		error = self._error("on: push\njobs:\n  A:\n    runs-on: x\n    needs: B\n")

		self.assertEqual("Job 'A' needs job 'B', which the workflow doesn't have.", str(error))
		self.assertEqual(3, error.Line)
		self.assertEqual([f"In '{self._path / 'Broken.yml'}:3'.", "Jobs: A."], error.__notes__)

	def test_Cycle(self) -> None:
		error = self._error(dedent("""\
			on: push
			jobs:
			  A: {runs-on: x, needs: C}
			  B: {runs-on: x, needs: A}
			  C: {runs-on: x, needs: B}
		"""))

		self.assertEqual("Jobs need each other in a cycle: A -> C -> B -> A.", str(error))

	def test_RunsOnAndUses(self) -> None:
		error = self._error("on: push\njobs:\n  A:\n    steps: []\n")

		self.assertEqual("Job 'A' needs either 'runs-on' or 'uses'.", str(error))
		self.assertEqual(3, error.Line)

	def test_InputWithoutType(self) -> None:
		error = self._error("on:\n  workflow_call:\n    inputs:\n      a:\n        required: true\njobs: {}\n")

		self.assertEqual("Input 'a' has no 'type' key.", str(error))
		self.assertEqual(4, error.Line)

	def test_InputType(self) -> None:
		error = self._error("on:\n  workflow_call:\n    inputs:\n      a:\n        type: text\njobs: {}\n")

		self.assertEqual("Key 'type' of input 'a' is not an input type.", str(error))
		self.assertIn("Allowed values: string, boolean, number.", error.__notes__)

	def test_OutputWithoutValue(self) -> None:
		error = self._error("on:\n  workflow_call:\n    outputs:\n      a:\n        description: x\njobs: {}\n")

		self.assertEqual("Output 'a' has no 'value' key.", str(error))

	def test_Required(self) -> None:
		error = self._error("on:\n  workflow_call:\n    secrets:\n      a:\n        required: 'yes'\njobs: {}\n")

		self.assertEqual("Key 'required' of 'a' is not a boolean.", str(error))

	def test_PermissionLevel(self) -> None:
		error = self._error("on: push\npermissions:\n  contents: all\njobs: {}\n")

		self.assertEqual("Permission 'contents' is not an access level.", str(error))
		self.assertEqual(3, error.Line)

	def test_PermissionShortForm(self) -> None:
		error = self._error("on: push\npermissions: all\njobs: {}\n")

		self.assertEqual("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", str(error))

	def test_Uses(self) -> None:
		error = self._error("on: push\njobs:\n  A:\n    uses: owner/repo/.github/workflows/A.yml\n")

		self.assertEqual("Key 'uses' of job 'A' is not a reference.", str(error))
		self.assertEqual(4, error.Line)

	def test_Steps(self) -> None:
		error = self._error("on: push\njobs:\n  A:\n    runs-on: x\n    steps: run\n")

		self.assertEqual("Key 'steps' of job 'A' is not a list.", str(error))

	def test_Job(self) -> None:
		error = self._error("on: push\njobs:\n  A: x\n")

		self.assertEqual("Job 'A' is not a mapping.", str(error))
		self.assertEqual([f"In '{self._path / 'Broken.yml'}:3'.", "Got type 'str'."], error.__notes__)

	def test_Path(self) -> None:
		with self.assertRaises(ValueError):
			_ = Workflow.FromFile(None)

		with self.assertRaises(TypeError):
			_ = Workflow.FromFile("Pipeline.yml")

		with self.assertRaises(FileNotFoundError):
			_ = Workflow.FromFile(self._path / "Missing.yml")


class Construction(Testcase):
	def test_Workflow(self) -> None:
		workflow = Workflow(Path("Pipeline.yml"), "Pipeline", ("push", ))
		job = Job("Build", 3, runsOn=("ubuntu-26.04", ), needs=("Prepare", ), parent=workflow)

		self.assertIs(job, workflow.Jobs["Build"])
		self.assertEqual((), job.Needs)
		self.assertEqual("Pipeline.yml:3", job.Location)

	def test_Job_Name(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Job(None, 1)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = Job(1, 1)

		with self.assertRaises(ValueError):
			_ = Job("", 1)

	def test_Input_Parent(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Input("a", 1, InputType.String, parent=Job("Build", 1))

		self.assertEqual("Parameter 'parent' is not of type 'Workflow'.", str(context.exception))

	def test_Input_Type(self) -> None:
		with self.assertRaises(ValueError):
			_ = Input("a", 1, None)

		with self.assertRaises(TypeError):
			_ = Input("a", 1, "string")

	def test_Permission(self) -> None:
		with self.assertRaises(TypeError):
			_ = Permission("contents", "read", 1)

	def test_AccessLevel(self) -> None:
		self.assertLess(AccessLevel.NoAccess.Rank(), AccessLevel.Read.Rank())
		self.assertLess(AccessLevel.Read.Rank(), AccessLevel.Write.Rank())
