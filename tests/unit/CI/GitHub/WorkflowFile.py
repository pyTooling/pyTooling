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
Unit tests for :mod:`pyTooling.CI.GitHub.WorkflowFile`.
"""
from pathlib                          import Path
from tempfile                         import TemporaryDirectory
from textwrap                         import dedent, indent
from typing                           import Any

from pyTooling.CI                     import Matrix as CIMatrix, NeedDependencyCycleError, Pipeline as CIPipeline
from pyTooling.CI.GitHub              import Pipeline as GitHubPipeline
from pyTooling.CI.GitHub.WorkflowFile import AccessLevel, Base, InputType, Workflow, WorkflowError, WorkflowResolver
from pyTooling.CI.GitHub.WorkflowFile import Input, Job, Matrix, Output, Permission, PermissionScope, Secret
from pyTooling.CI.GitHub.WorkflowFile import UsesReference, DefinedJob, DefinedMatrix, DefinedMatrixJob
from pyTooling.CI.GitHub.WorkflowFile import DefinedMatrixWorkflow, DefinedPipeline, DefinedWorkflow, Action, Step
from pyTooling.Graph                  import Graph
from pyTooling.Testing                import Testcase

from ruamel.yaml                      import YAML


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


class ToPython(Testcase):
	"""The round-trip loader's own types become plain Python types."""

	def test_Types(self) -> None:
		document = YAML(typ="rt").load(dedent("""\
			mapping: {a: 1}
			list:    [1, 2]
			anchor:  &flag false
			alias:   *flag
			hex:     0x1F
			float:   1.50
			block: |
			  one
			  two
			plain:   text
			none:    null
		"""))
		values = {key: Base._ToPython(value) for key, value in document.items()}

		expected = {
			"mapping": (dict, {"a": 1}), "list": (list, [1, 2]), "anchor": (bool, False), "alias": (bool, False),
			"hex": (int, 31), "float": (float, 1.5), "block": (str, "one\ntwo\n"), "plain": (str, "text"),
			"none": (type(None), None)
		}
		for key, (valueType, value) in expected.items():
			with self.subTest(key=key):
				self.assertIs(valueType, type(values[key]))
				self.assertEqual(value, values[key])


class Permissions(Testcase):
	"""A ``permissions`` key, read by :meth:`Permission._FromYAML`."""

	def _error(self, value: Any) -> WorkflowError:
		"""
		Read a malformed ``permissions`` key written at line 2.

		:param value: The key's value.
		:returns:     The exception reading it raised.
		"""
		with self.assertRaises(WorkflowError) as context:
			_ = Permission._FromYAML(value, Path("A.yml"), 2)

		self.assertEqual(Path("A.yml"), context.exception.Path)

		return context.exception

	def test_Mapping(self) -> None:
		mapping = YAML(typ="rt").load("contents: read\nid-token: write\n")
		contents, idToken = Permission._FromYAML(mapping, Path("A.yml"), 1)

		self.assertIs(PermissionScope.Contents, contents.Scope)
		self.assertIs(PermissionScope.IDToken, idToken.Scope)
		self.assertIs(AccessLevel.Write, idToken.Level)
		self.assertEqual("contents: read", str(contents))
		self.assertEqual(2, idToken.Line)
		self.assertEqual("line 2", idToken.Location)
		self.assertIsNone(idToken.Parent)

	def test_ShortForm(self) -> None:
		for value, level in (("read-all", AccessLevel.Read), ("write-all", AccessLevel.Write)):
			with self.subTest(value=value):
				permission, = Permission._FromYAML(value, Path("A.yml"), 7)

				self.assertIs(level, permission.Level)
				self.assertEqual(value, str(permission))
				self.assertEqual(7, permission.Line)

	def test_Scope(self) -> None:
		error = self._error(YAML(typ="rt").load("everything: read\n"))

		self.assertEqual("Key 'everything' of 'permissions' is not a permission scope.", str(error))
		self.assertEqual(1, error.Line)
		self.assertIn("contents", error.__notes__[-1])
		self.assertNotIn("*", error.__notes__[-1])

	def test_Level(self) -> None:
		error = self._error(YAML(typ="rt").load("contents: all\n"))

		self.assertEqual("Permission 'contents' is not an access level.", str(error))
		self.assertEqual(1, error.Line)

	def test_ShortForm_Unknown(self) -> None:
		error = self._error("all")

		self.assertEqual("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", str(error))
		self.assertEqual(2, error.Line)
		self.assertIn("Got 'all'.", error.__notes__)

	def test_NotAMapping(self) -> None:
		error = self._error(YAML(typ="rt").load("[contents]\n"))

		self.assertEqual("Key 'permissions' is neither 'read-all', 'write-all' nor a mapping.", str(error))

	def test_Construction(self) -> None:
		with self.assertRaises(TypeError):
			_ = Permission("contents", AccessLevel.Read, 1)

		with self.assertRaises(TypeError):
			_ = Permission(PermissionScope.Contents, "read", 1)

		permission = Permission(PermissionScope.Contents, AccessLevel.Read, 1)
		self.assertIs(PermissionScope.Contents, permission.Scope)
		self.assertEqual("contents: read", str(permission))

	def test_AccessLevel(self) -> None:
		self.assertLess(AccessLevel.NoAccess.Rank, AccessLevel.Read.Rank)
		self.assertLess(AccessLevel.Read.Rank, AccessLevel.Write.Rank)
		self.assertEqual(2, AccessLevel.Write.Rank)
		self.assertIn("Rank", vars(AccessLevel.Write), "The rank is computed once per member.")

	def test_Parent(self) -> None:
		with self.assertRaises(TypeError):
			_ = Permission(
				PermissionScope.Contents, AccessLevel.Read, 1, parent=Permission(PermissionScope.Actions, AccessLevel.Read, 1)
			)

		workflow = Workflow(Path("Package.yml"))
		permission = Permission(PermissionScope.Contents, AccessLevel.Read, 3, parent=workflow)

		self.assertIs(permission, workflow.Permissions["contents"])

	def test_Workflow_Permissions(self) -> None:
		self.assertIsNone(Workflow(Path("Package.yml")).Permissions)
		self.assertEqual({}, Workflow(Path("Package.yml"), permissions=()).Permissions)

		contents = Permission(PermissionScope.Contents, AccessLevel.Read, 3)
		pages =    Permission(PermissionScope.Pages, AccessLevel.Write, 4)
		workflow = Workflow(Path("Package.yml"), permissions=[contents, pages])

		self.assertEqual(["contents", "pages"], list(workflow.Permissions))
		self.assertIs(workflow, pages.Parent)
		self.assertEqual("Package.yml:4", pages.Location)

		with self.assertRaises(TypeError) as context:
			_ = Workflow(Path("Package.yml"), permissions=["contents"])

		self.assertEqual("An element of parameter 'permissions' is not of type 'Permission'.", str(context.exception))


class WorkflowFile(Fixture):
	"""A workflow file, read by :meth:`Workflow.FromFile`."""

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
		self.assertEqual(self._path / "Package.yml", workflow.File)
		self.assertEqual("Package.yml:1", workflow.Location)

	def test_Permissions(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(["contents"], list(workflow.Permissions))
		self.assertIs(workflow, workflow.Permissions["contents"].Parent)
		self.assertEqual("Package.yml:37", workflow.Permissions["contents"].Location)

	def test_PermissionsShortForm(self) -> None:
		workflow = Workflow.FromFile(self._write("Prepare.yml", PREPARE))

		self.assertEqual("read-all", str(workflow.Permissions[PermissionScope.All]))

	def test_Triggers(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		self.assertEqual(("push", "workflow_dispatch"), workflow.Triggers)
		self.assertFalse(workflow.IsCallable)
		self.assertIsNone(workflow.Permissions)

	def test_Triggers_Forms(self) -> None:
		jobs = "jobs:\n  Job:\n    runs-on: ubuntu-26.04\n    steps: []\n"

		self.assertEqual(("push", ), Workflow.FromFile(self._write("A.yml", f"on: push\n{jobs}")).Triggers)
		workflow = Workflow.FromFile(self._write("B.yml", f"on: [push, workflow_call]\n{jobs}"))
		self.assertEqual(("push", "workflow_call"), workflow.Triggers)
		self.assertTrue(Workflow.FromFile(self._write("C.yml", f"on:\n  workflow_call:\n{jobs}")).IsCallable)


class Errors(Fixture):
	"""A malformed workflow file names itself and the line."""

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
		self.assertEqual("Workflow file is not a YAML document.", str(self._error("on: push\njobs: [\n")))

	def test_Empty(self) -> None:
		self.assertEqual("Workflow file is empty.", str(self._error("")))

	def test_NoJobs(self) -> None:
		self.assertEqual("Workflow file has no 'jobs' key.", str(self._error("on: push\n")))

	def test_NoOn(self) -> None:
		self.assertEqual("Workflow file has no 'on' key.", str(self._error("jobs: {}\n")))

	def test_Nested(self) -> None:
		"""An element reading its own part names the file too."""
		error = self._error("on: push\npermissions:\n  contents: all\njobs: {}\n")

		self.assertEqual("Permission 'contents' is not an access level.", str(error))
		self.assertEqual(3, error.Line)

	def test_Path(self) -> None:
		with self.assertRaises(ValueError):
			_ = Workflow.FromFile(None)

		with self.assertRaises(TypeError):
			_ = Workflow.FromFile("Pipeline.yml")

		with self.assertRaises(WorkflowError) as context:
			_ = Workflow.FromFile(self._path / "Missing.yml")

		self.assertEqual("Workflow file doesn't exist.", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, FileNotFoundError)

	def test_Unreadable(self) -> None:
		with self.assertRaises(WorkflowError) as context:
			_ = Workflow.FromFile(self._path)

		self.assertEqual("Workflow file can't be read.", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, OSError)


class Parameters(Fixture):
	"""The parameters of ``on.workflow_call``, each read by its class' ``_FromYAML()``."""

	def _read(self, section: str, parameterClass: type) -> dict[str, Any]:
		"""
		Read one section of the parameters of :data:`CALLABLE`.

		:param section:        ``inputs``, ``outputs`` or ``secrets``.
		:param parameterClass: The class reading a declaration.
		:returns:              The parameters, by name.
		"""
		parameters = YAML(typ="rt").load(CALLABLE)["on"]["workflow_call"][section]

		return {
			name: parameterClass._FromYAML(name, declaration, Path("Package.yml"), Base._KeyLine(parameters, name))
			for name, declaration in parameters.items()
		}

	def _error(self, parameterClass: type, declaration: str) -> WorkflowError:
		"""
		Read a malformed declaration of a parameter ``a`` written at line 4.

		:param parameterClass: The class reading the declaration.
		:param declaration:    The declaration's YAML.
		:returns:              The exception reading it raised.
		"""
		with self.assertRaises(WorkflowError) as context:
			_ = parameterClass._FromYAML("a", YAML(typ="rt").load(declaration), Path("A.yml"), 4)

		self.assertEqual(4, context.exception.Line)

		return context.exception

	def test_Inputs(self) -> None:
		inputs = self._read("inputs", Input)

		self.assertEqual(["package_name", "python_version", "dry_run", "pages_on"], list(inputs))

		packageName = inputs["package_name"]
		self.assertEqual("package_name", packageName.Name)
		self.assertIs(InputType.String, packageName.Type)
		self.assertTrue(packageName.Required)
		self.assertIsNone(packageName.Default)
		self.assertEqual("Name of the package.", packageName.Description)
		self.assertEqual("line 6", packageName.Location)

		pythonVersion = inputs["python_version"]
		self.assertFalse(pythonVersion.Required)
		self.assertEqual("3.14", pythonVersion.Default)
		self.assertIs(str, type(pythonVersion.Default))

		dryRun = inputs["dry_run"]
		self.assertIs(InputType.Boolean, dryRun.Type)
		self.assertIs(False, dryRun.Default)
		self.assertIsNone(dryRun.Description)

		self.assertEqual("default-branch\nrelease-tag\n", inputs["pages_on"].Default)

	def test_Input_Number(self) -> None:
		declaration = YAML(typ="rt").load("type: number\ndefault: 0x10\nrequired: true\n")
		parameter = Input._FromYAML("count", declaration, Path("A.yml"), 4)

		self.assertIs(InputType.Number, parameter.Type)
		self.assertIs(int, type(parameter.Default))
		self.assertEqual(16, parameter.Default)
		self.assertTrue(parameter.Required)

	def test_Outputs(self) -> None:
		version = self._read("outputs", Output)["version"]

		self.assertEqual("Version of the package.", version.Description)
		self.assertEqual("${{ jobs.Build.outputs.version }}", version.Value)
		self.assertEqual(27, version.Line)

	def test_Secrets(self) -> None:
		secrets = self._read("secrets", Secret)

		self.assertEqual(["PYPI_TOKEN", "CODECOV_TOKEN"], list(secrets))
		self.assertTrue(secrets["PYPI_TOKEN"].Required)
		self.assertEqual("Token for PyPI.", secrets["PYPI_TOKEN"].Description)
		self.assertFalse(secrets["CODECOV_TOKEN"].Required)
		self.assertIsNone(secrets["CODECOV_TOKEN"].Description)

	def test_InputWithoutType(self) -> None:
		self.assertEqual("Input 'a' has no 'type' key.", str(self._error(Input, "required: true\n")))
		self.assertEqual("Input 'a' has no 'type' key.", str(self._error(Input, "")))

	def test_InputType(self) -> None:
		error = self._error(Input, "type: text\n")

		self.assertEqual("Key 'type' of input 'a' is not an input type.", str(error))
		self.assertIn("Allowed values: string, boolean, number.", error.__notes__)

	def test_OutputWithoutValue(self) -> None:
		self.assertEqual("Output 'a' has no 'value' key.", str(self._error(Output, "description: x\n")))
		self.assertEqual("Output 'a' has no 'value' key.", str(self._error(Output, "")))

	def test_SecretWithoutDeclaration(self) -> None:
		secret = Secret._FromYAML("a", None, Path("A.yml"), 4)

		self.assertFalse(secret.Required)
		self.assertIsNone(secret.Description)
		self.assertIsNone(secret.Parent)

	def test_Required(self) -> None:
		self.assertEqual("Key 'required' of 'a' is not a boolean.", str(self._error(Secret, "required: 'yes'\n")))

	def test_NotAMapping(self) -> None:
		self.assertEqual("Declaration of 'a' is not a mapping.", str(self._error(Input, "number\n")))

	def test_Input_Type(self) -> None:
		with self.assertRaises(ValueError):
			_ = Input("a", 1, None)

		with self.assertRaises(TypeError):
			_ = Input("a", 1, "string")

	def test_FromFile(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(["package_name", "python_version", "dry_run", "pages_on"], list(workflow.Inputs))
		self.assertEqual(["version"], list(workflow.Outputs))
		self.assertEqual(["PYPI_TOKEN", "CODECOV_TOKEN"], list(workflow.Secrets))

		packageName = workflow.Inputs["package_name"]
		self.assertIs(workflow, packageName.Parent)
		self.assertIs(workflow, packageName.Workflow)
		self.assertEqual("Package.yml:6", packageName.Location)

	def test_NoParameters(self) -> None:
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))

		self.assertEqual({}, workflow.Inputs)
		self.assertEqual({}, workflow.Outputs)
		self.assertEqual({}, workflow.Secrets)

	def test_Workflow_Parameters(self) -> None:
		inputs =  [Input("a", 2, InputType.String), Input("b", 3, InputType.Number)]
		outputs = [Output("c", 4, "${{ jobs.Build.outputs.c }}")]
		secrets = [Secret("d", 5)]
		workflow = Workflow(Path("Package.yml"), None, ("workflow_call", ), inputs, outputs, secrets)

		self.assertEqual(["a", "b"], list(workflow.Inputs))
		self.assertEqual(["c"], list(workflow.Outputs))
		self.assertEqual(["d"], list(workflow.Secrets))
		for parameter in (*inputs, *outputs, *secrets):
			self.assertIs(workflow, parameter.Parent)
			self.assertIs(workflow, parameter.Workflow)

		self.assertEqual("Package.yml:2", inputs[0].Location)

	def test_Workflow_Defaults(self) -> None:
		workflow = Workflow(Path("Package.yml"))

		self.assertEqual((), workflow.Triggers)
		self.assertEqual({}, workflow.Inputs)
		self.assertEqual({}, workflow.Outputs)
		self.assertEqual({}, workflow.Secrets)

	def test_Workflow_ElementTypes(self) -> None:
		path = Path("Package.yml")
		for arguments, message in (
			({"triggers": ("push", 42)},                      "An element of parameter 'triggers' is not of type 'str'."),
			({"inputs":   [Secret("a", 2)]},                  "An element of parameter 'inputs' is not of type 'Input'."),
			({"outputs":  [Input("a", 2, InputType.String)]}, "An element of parameter 'outputs' is not of type 'Output'."),
			({"secrets":  ["a"]},                             "An element of parameter 'secrets' is not of type 'Secret'.")
		):
			with self.subTest(message):
				with self.assertRaises(TypeError) as context:
					_ = Workflow(path, **arguments)

				self.assertEqual(message, str(context.exception))

	def test_Input_Parent(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Input("a", 1, InputType.String, parent=Permission(PermissionScope.Contents, AccessLevel.Read, 1))

		self.assertEqual("Parameter 'parent' is not of type 'Workflow'.", str(context.exception))


class References(Testcase):
	def test_Workflow(self) -> None:
		uses = UsesReference("pyTooling/Actions/.github/workflows/Package.yml@r8", 12)

		self.assertEqual("pyTooling/Actions", uses.Repository)
		self.assertEqual(".github/workflows/Package.yml", uses.Path)
		self.assertEqual("r8", uses.Reference)
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
		self.assertEqual("v6", uses.Reference)
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
		self.assertIsNone(uses.Reference)
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

		self.assertEqual("Parameter 'rawReference' names a repository without a ref.", str(context.exception))
		self.assertEqual(["Got 'actions/checkout'."], context.exception.__notes__)

	def test_NoRepository(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference("checkout@v6", 1)

		self.assertEqual("Parameter 'rawReference' names no repository as 'owner/repo'.", str(context.exception))

	def test_Empty(self) -> None:
		with self.assertRaises(ValueError):
			_ = UsesReference("", 1)

	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference(None, 1)

		self.assertEqual("Parameter 'rawReference' is None.", str(context.exception))

	def test_Line(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = UsesReference("actions/checkout@v6", 0)

		self.assertEqual("Parameter 'line' is not positive.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = UsesReference("actions/checkout@v6", "1")


def _readJobs(document: str) -> dict[str, Job]:
	"""
	Read the jobs of a workflow's YAML with :meth:`Job._FromYAML`, without the workflow.

	:param document: The workflow's YAML.
	:returns:        The jobs, by name.
	"""
	jobs = YAML(typ="rt").load(document)["jobs"]

	return {
		name: Job._FromYAML(name, mapping, Path("Package.yml"), Base._KeyLine(jobs, name))
		for name, mapping in jobs.items()
	}


class Jobs(Testcase):
	"""A job, read by :meth:`Job._FromYAML`."""

	def _error(self, job: str) -> WorkflowError:
		"""
		Read a malformed job ``A`` written at line 2.

		:param job: The job's YAML, indented as the value of ``A``.
		:returns:   The exception reading it raised.
		"""
		with self.assertRaises(WorkflowError) as context:
			_ = _readJobs(f"jobs:\n  A:\n{indent(dedent(job), '    ')}")

		self.assertEqual(Path("Package.yml"), context.exception.Path)

		return context.exception

	def test_Job(self) -> None:
		jobs = _readJobs(CALLABLE)
		params = jobs["Params"]

		self.assertEqual("Params", params.Name)
		self.assertEqual("Parameters", params.DisplayName)
		self.assertEqual(("ubuntu-26.04", ), params.RunsOn)
		self.assertIsNone(params.Uses)
		self.assertIsNone(params.Condition)
		self.assertIsNone(params.Permissions)
		self.assertEqual({"jobs": "${{ steps.params.outputs.jobs }}"}, params.Outputs)
		self.assertEqual("line 40", params.Location)

	def test_NeedNames(self) -> None:
		jobs = _readJobs(CALLABLE)

		self.assertEqual((), jobs["Params"].NeedNames)
		self.assertEqual(("Params", ), jobs["Build"].NeedNames)
		self.assertEqual(("Params", "Build"), jobs["Static"].NeedNames)

	def test_Condition(self) -> None:
		self.assertEqual("inputs.dry_run == false", _readJobs(CALLABLE)["Build"].Condition)

	def test_Permissions(self) -> None:
		build = _readJobs(CALLABLE)["Build"]
		permissions = build.Permissions

		self.assertEqual(["contents", "id-token"], list(permissions))
		self.assertIs(AccessLevel.Write, permissions["id-token"].Level)
		self.assertIs(build, permissions["id-token"].Parent)
		self.assertEqual("line 56", permissions["id-token"].Location)

	def test_Calls(self) -> None:
		jobs = _readJobs(CALLER)
		package = jobs["Package"]

		self.assertEqual("owner/repo", package.Uses.Repository)
		self.assertEqual("dev", package.Uses.Reference)
		self.assertEqual("line 12", package.Uses.Location)
		self.assertEqual((), package.RunsOn)
		self.assertEqual({"package_name": "myPackage", "delay": 10}, package.With)
		self.assertEqual({"PYPI_TOKEN": "${{ secrets.PYPI_TOKEN }}"}, package.Secrets)
		self.assertFalse(package.InheritsSecrets)

		local = jobs["Local"]
		self.assertTrue(local.InheritsSecrets)
		self.assertEqual({}, local.Secrets)
		self.assertTrue(local.Uses.IsLocal)

	def test_RunsOnAndUses(self) -> None:
		error = self._error("steps: []\n")

		self.assertEqual("Job 'A' needs either 'runs-on' or 'uses'.", str(error))
		self.assertEqual(2, error.Line)

	def test_Uses(self) -> None:
		error = self._error("uses: owner/repo/.github/workflows/A.yml\n")

		self.assertEqual("Key 'uses' of job 'A' is not a reference.", str(error))
		self.assertEqual(3, error.Line)

	def test_Name(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Job(None, 1)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = Job(1, 1)

		with self.assertRaises(ValueError):
			_ = Job("", 1)


class JobsInFile(Fixture):
	"""The jobs of a workflow file, read by :meth:`Workflow.FromFile`."""

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

	def test_FromFile(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(3, workflow.JobCount)
		self.assertEqual(["Params", "Build", "Static"], [job.Name for job in workflow.IterateJobs()])
		self.assertTrue(workflow.ContainsJob("Build"))
		self.assertFalse(workflow.ContainsJob("Unknown"))

		build = workflow.Jobs["Build"]
		self.assertIs(workflow, build.Parent)
		self.assertEqual("Package.yml:50", build.Location)
		self.assertEqual("Package.yml:56", build.Permissions["id-token"].Location)

	def test_Needs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		params, build, static = workflow.IterateJobs()

		self.assertEqual((), params.Needs)
		self.assertEqual((params, ), build.Needs)
		self.assertEqual((params, build), static.Needs)

	def test_Construction(self) -> None:
		workflow = Workflow(Path("Pipeline.yml"), "Pipeline", ("push", ))
		job = Job("Build", 3, runsOn=("ubuntu-26.04", ), needs=("Prepare", ), parent=workflow)

		self.assertIs(job, workflow.Jobs["Build"])
		self.assertEqual((), job.Needs)
		self.assertEqual("Pipeline.yml:3", job.Location)

	def test_Construction_Jobs(self) -> None:
		prepare = Job("Prepare", 3, runsOn=("ubuntu-26.04", ))
		build =   Job("Build", 5, runsOn=("ubuntu-26.04", ), needs=("Prepare", ))
		uses =    UsesReference("./.github/workflows/Package.yml", 6, parent=build)

		self.assertIsNone(build.Workflow)
		self.assertEqual("line 6", uses.Location)

		workflow = Workflow(Path("Pipeline.yml"), "Pipeline", ("push", ), jobs=(prepare, build))

		self.assertEqual(["Prepare", "Build"], list(workflow.Jobs))
		self.assertIs(workflow, build.Parent)
		self.assertEqual((prepare, ), build.Needs)
		self.assertIs(workflow, uses.Workflow, "Attaching a job passes the workflow on to its elements.")
		self.assertEqual("Pipeline.yml:6", uses.Location)

	def test_Construction_Elements(self) -> None:
		uses =       UsesReference("pyTooling/Actions/.github/workflows/Package.yml@r8", 4)
		permission = Permission(PermissionScope.Contents, AccessLevel.Write, 6)
		job =        Job("Package", 3, uses=uses, permissions=(permission, ))
		workflow =   Workflow(Path("Pipeline.yml"), jobs=(job, ))

		self.assertIs(uses, job.Uses)
		self.assertIs(job, uses.Parent)
		self.assertEqual(["contents"], list(job.Permissions))
		self.assertIs(job, permission.Parent)
		self.assertIs(workflow, permission.Workflow)
		self.assertIsNone(Job("Build", 3).Permissions)

		called =    Job("Called", 7)
		reference = UsesReference("./.github/workflows/Package.yml", 8, parent=called)
		self.assertIs(reference, called.Uses)

		for arguments, message in (
			({"uses":        "./Package.yml"}, "Parameter 'uses' is not of type 'UsesReference'."),
			({"permissions": ("contents", )},  "An element of parameter 'permissions' is not of type 'Permission'.")
		):
			with self.subTest(message):
				with self.assertRaises(TypeError) as context:
					_ = Job("Build", 3, **arguments)

				self.assertEqual(message, str(context.exception))

	def test_Parent_Assigned(self) -> None:
		workflow = Workflow(Path("Pipeline.yml"))
		job =      Job("Build", 3, permissions=(Permission(PermissionScope.Contents, AccessLevel.Read, 4), ))
		job.Parent = workflow

		self.assertIs(workflow, job.Parent)
		self.assertIs(workflow, job.Permissions["contents"].Workflow)

		with self.assertRaises(ValueError):
			job.Parent = None

		with self.assertRaises(TypeError) as context:
			job.Parent = job

		self.assertEqual("Parameter 'value' is not of type 'Workflow'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			workflow.Parent = job

		self.assertEqual("A 'pyTooling.CI.GitHub.WorkflowFile.Workflow' has no parent.", str(context.exception))

	def test_Construction_Defaults(self) -> None:
		job = Job("Build", 3)

		self.assertEqual((), job.NeedNames)
		self.assertEqual((), job.RunsOn)

	def test_Construction_ElementTypes(self) -> None:
		for arguments, message in (
			({"needs":  ("A", 1)}, "An element of parameter 'needs' is not of type 'str'."),
			({"runsOn": (None, )}, "An element of parameter 'runsOn' is not of type 'str'.")
		):
			with self.subTest(message):
				with self.assertRaises(TypeError) as context:
					_ = Job("Build", 3, **arguments)

				self.assertEqual(message, str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Workflow(Path("Pipeline.yml"), jobs=("Build", ))

		self.assertEqual("An element of parameter 'jobs' is not of type 'Job'.", str(context.exception))

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

	def test_NotAMapping(self) -> None:
		error = self._error("on: push\njobs:\n  A: x\n")

		self.assertEqual("Job 'A' is not a mapping.", str(error))
		self.assertEqual([f"In '{self._path / 'Broken.yml'}:3'.", "Got type 'str'."], error.__notes__)


class Steps(Fixture):
	"""The steps of a job."""

	def _jobError(self, job: str) -> WorkflowError:
		"""
		Read a malformed job ``A`` written at line 2.

		:param job: The job's YAML, indented as the value of ``A``.
		:returns:   The exception reading it raised.
		"""
		with self.assertRaises(WorkflowError) as context:
			_ = _readJobs(f"jobs:\n  A:\n{indent(dedent(job), '    ')}")

		self.assertEqual(Path("Package.yml"), context.exception.Path)

		return context.exception

	def test_Steps(self) -> None:
		jobs = _readJobs(CALLABLE)
		params = jobs["Params"]

		self.assertEqual(1, params.StepCount)
		self.assertEqual("Compute", params.Steps[0].Name)
		self.assertEqual("params", params.Steps[0].ID)
		self.assertIn("GITHUB_OUTPUT", params.Steps[0].Run)
		self.assertEqual(0, _readJobs(CALLER)["Package"].StepCount)

		build = jobs["Build"]
		self.assertEqual(3, build.StepCount)
		steps = list(build.IterateSteps())
		self.assertEqual("actions/checkout@v6", str(steps[0].Uses))
		self.assertIs(steps[0], steps[0].Uses.Parent)
		self.assertIs(build, steps[0].Parent)
		self.assertIsNone(steps[1].Name)
		self.assertEqual("success()", steps[2].Condition)
		self.assertEqual("line 69", steps[2].Location)

	def test_FromFile(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		build = workflow.Jobs["Build"]

		self.assertIs(workflow, build.Steps[0].Uses.Workflow)
		self.assertEqual("Package.yml:69", build.Steps[2].Location)

	def test_Actions(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))

		self.assertEqual(
			["actions/checkout@v6", "actions/setup-python@v6", "docker://alpine:3.22"],
			[str(action) for action in workflow.IterateActions()]
		)

	def test_Construction(self) -> None:
		uses =     UsesReference("actions/checkout@v6", 5)
		checkout = Step(4, uses=uses)
		test =     Step(6, name="Test", run="pytest")
		matrix =   Matrix(3, {"python": ["3.13", "3.14"]})
		job =      Job("Build", 2, runsOn=("ubuntu-26.04", ), matrix=matrix, steps=(checkout, test))

		self.assertEqual([checkout, test], job.Steps)
		self.assertIs(job, test.Parent)
		self.assertIs(checkout, uses.Parent)
		self.assertIs(matrix, job.Matrix)
		self.assertIs(job, matrix.Parent)

		workflow = Workflow(Path("Package.yml"), jobs=(job, ))
		for element in (job, matrix, checkout, uses):
			self.assertIs(workflow, element.Workflow)

		attached = Step(8, run="make", parent=job)
		self.assertIs(attached, job.Steps[-1])
		self.assertIs(Matrix(9, parent=job), job.Matrix)

		for arguments, message in (
			({"matrix": {"python": ["3.14"]}}, "Parameter 'matrix' is not of type 'Matrix'."),
			({"steps":  ("run", )},            "An element of parameter 'steps' is not of type 'Step'.")
		):
			with self.subTest(message):
				with self.assertRaises(TypeError) as context:
					_ = Job("Build", 2, **arguments)

				self.assertEqual(message, str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = Step(4, uses="actions/checkout@v6")

		self.assertEqual("Parameter 'uses' is not of type 'UsesReference'.", str(context.exception))

	def test_Steps_NotAList(self) -> None:
		self.assertEqual("Key 'steps' of job 'A' is not a list.", str(self._jobError("runs-on: x\nsteps: run\n")))

	def test_Step_NotAMapping(self) -> None:
		error = self._jobError("runs-on: x\nsteps:\n  - run\n")

		self.assertEqual("Step 1 of job 'A' is not a mapping.", str(error))
		self.assertEqual(5, error.Line)


class Matrices(Testcase):
	"""A job's ``strategy.matrix``, read by :meth:`Matrix._FromYAML`, and the combinations it produces."""

	def _matrix(self, matrix: str) -> Matrix:
		"""
		Read a matrix written at line 6.

		:param matrix: The matrix' YAML.
		:returns:      The matrix.
		"""
		return Matrix._FromYAML(YAML(typ="rt").load(dedent(matrix)), Path("A.yml"), 6)

	def test_Static(self) -> None:
		matrix = self._matrix("""\
			system: [ubuntu, windows]
			python: ['3.13', '3.14']
			exclude:
			  - system: windows
			    python: '3.13'
		""")

		self.assertFalse(matrix.IsDynamic)
		self.assertEqual({"system": ["ubuntu", "windows"], "python": ["3.13", "3.14"]}, matrix.Dimensions)
		self.assertEqual([{"system": "windows", "python": "3.13"}], matrix.Exclude)
		self.assertIsNone(matrix.Include)
		self.assertIsNone(matrix.Expression)
		self.assertEqual("line 6", matrix.Location)

	def test_DynamicInclude(self) -> None:
		matrix = self._matrix("include: ${{ fromJson(needs.Params.outputs.jobs) }}\n")

		self.assertTrue(matrix.IsDynamic)
		self.assertEqual("${{ fromJson(needs.Params.outputs.jobs) }}", matrix.Include)
		self.assertEqual({}, matrix.Dimensions)

	def test_Expression(self) -> None:
		matrix = Matrix._FromYAML("${{ fromJson(inputs.matrix) }}", Path("A.yml"), 6)

		self.assertTrue(matrix.IsDynamic)
		self.assertEqual("${{ fromJson(inputs.matrix) }}", matrix.Expression)

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

	def test_Job(self) -> None:
		jobs = _readJobs(CALLABLE)

		self.assertTrue(jobs["Build"].Matrix.IsDynamic)
		self.assertIs(jobs["Build"], jobs["Build"].Matrix.Parent)
		self.assertEqual("line 59", jobs["Build"].Matrix.Location)
		self.assertFalse(jobs["Static"].Matrix.IsDynamic)
		self.assertEqual(("self-hosted", "linux"), jobs["Static"].RunsOn)
		self.assertIsNone(jobs["Params"].Matrix)

	def test_NotAMapping(self) -> None:
		with self.assertRaises(WorkflowError) as context:
			_ = _readJobs("jobs:\n  A:\n    runs-on: x\n    strategy:\n      matrix: [a]\n")

		self.assertEqual("Key 'strategy.matrix' is not a mapping.", str(context.exception))
		self.assertEqual(5, context.exception.Line)


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
		self.assertEqual(["contents", "actions", PermissionScope.All, "id-token"], list(permissions))
		self.assertEqual("Package.yml:55", permissions["contents"].Location)
		self.assertIs(AccessLevel.Write, permissions["contents"].Level)
		self.assertEqual("Pipeline.yml:17", permissions["actions"].Location)
		self.assertEqual("Prepare.yml:4", permissions[PermissionScope.All].Location)

	def test_Repositories(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = WorkflowResolver({"owner": Path(".")})

		self.assertEqual("Key of parameter 'repositories' is not of the form 'owner/repo'.", str(context.exception))

		with self.assertRaises(TypeError):
			_ = WorkflowResolver({"owner/repo": "."})

		self.assertEqual({"owner/repo": Path(".")}, WorkflowResolver({"Owner/Repo": Path(".")}).Repositories)


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

		params = pipeline.GetElement("Params")
		self.assertIsInstance(params, DefinedJob)
		self.assertIs(workflow.Jobs["Params"], params.Definition)
		self.assertEqual(["Compute"], [str(step) for step in params.Steps])
		self.assertIs(workflow.Jobs["Params"].Steps[0], params.Steps[0].Definition)

		build = pipeline.GetElement("Build")
		self.assertIsInstance(build, DefinedMatrix)
		self.assertEqual("inputs.dry_run == false", build.Condition)
		self.assertEqual(0, build.ElementCount)

		static = pipeline.GetElement("Static")
		self.assertEqual(
			["Static (ubuntu, 3.13)", "Static (ubuntu, 3.14)", "Static (windows, 3.14)"],
			[str(job) for job in static.IterateElements()]
		)
		self.assertIsInstance(static.GetElement("Static (ubuntu, 3.14)"), DefinedMatrixJob)
		self.assertDictEqual({"system": "ubuntu", "python": "3.14"}, static.GetElement("Static (ubuntu, 3.14)").Dimensions)
		self.assertEqual(
			["Run docker://alpine:3.22"], [str(step) for step in static.GetElement("Static (ubuntu, 3.14)").Steps]
		)

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
		steps = workflow.ToPipeline().GetElement("Job").Steps

		self.assertEqual(["Checkout", "Run actions/setup-python@v6", 'Run echo "one"'], [str(step) for step in steps])
		self.assertEqual("success()", steps[2].Condition)

	def test_Needs(self) -> None:
		workflow = Workflow.FromFile(self._write("Package.yml", CALLABLE))
		pipeline = workflow.ToPipeline()

		self.assertEqual([pipeline.GetElement("Params")], pipeline.GetElement("Build").Needs)
		self.assertEqual([pipeline.GetElement("Params"), pipeline.GetElement("Build")], pipeline.GetElement("Static").Needs)
		self.assertEqual(
			[pipeline.GetElement("Build"), pipeline.GetElement("Static")], pipeline.GetElement("Params").Dependents
		)

	def test_Calls(self) -> None:
		"""A called workflow is expanded, if the resolver reads it; a foreign one stays empty."""
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml").ToPipeline(resolver)

		package = pipeline.GetElement("Package")
		self.assertIsInstance(package, DefinedWorkflow)
		self.assertEqual("owner/repo/.github/workflows/Package.yml@dev", package.Reference)
		self.assertIs(resolver.Load(self._path / "Package.yml"), package.CalledWorkflow)
		self.assertEqual(["Params", "Build", "Static"], [element.Name for element in package.Elements])
		self.assertEqual("Package / Params", package.GetElement("Params").QualifiedName)
		self.assertEqual([package.GetElement("Params")], package.GetElement("Build").Needs)

		local = pipeline.GetElement("Local")
		self.assertEqual(3, local.ElementCount)
		self.assertIsNot(package.GetElement("Params"), local.GetElement("Params"))
		self.assertEqual(["Prepare"], [element.Name for element in pipeline.GetElement("Prepare").Elements])

		foreign = pipeline.GetElement("Foreign")
		self.assertEqual("other/repo/.github/workflows/Package.yml@v1", foreign.Reference)
		self.assertIsNone(foreign.CalledWorkflow)
		self.assertEqual(0, foreign.ElementCount)

	def test_Calls_Depth(self) -> None:
		"""A depth of 0 expands no call."""
		resolver = self._resolver()
		pipeline = resolver.Load(self._path / "Pipeline.yml").ToPipeline(resolver, depth=0)

		self.assertEqual([0, 0, 0, 0], [element.ElementCount for element in pipeline.IterateElements()])
		self.assertIsNone(pipeline.GetElement("Package").CalledWorkflow)

	def test_Calls_WithoutResolver(self) -> None:
		pipeline = Workflow.FromFile(self._write("Pipeline.yml", CALLER)).ToPipeline()

		self.assertEqual([0, 0, 0, 0], [element.ElementCount for element in pipeline.IterateElements()])

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
		tests = workflow.ToPipeline(WorkflowResolver()).GetElement("Tests")

		self.assertIsInstance(tests, DefinedMatrix)
		self.assertEqual(["Tests (3.13)", "Tests (3.14)"], [str(instance) for instance in tests.IterateElements()])
		self.assertIsInstance(tests.GetElement("Tests (3.14)"), DefinedMatrixWorkflow)
		self.assertDictEqual({"python": "3.14"}, tests.GetElement("Tests (3.14)").Dimensions)
		self.assertEqual("Tests (3.14) / Prepare", tests.GetElement("Tests (3.14)").GetElement("Prepare").QualifiedName)

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

		for cls in (DefinedMatrixJob, DefinedMatrixWorkflow):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(ValueError) as context:
					_ = cls(workflow.Jobs["Package"], None)

				self.assertEqual("Parameter 'dimensions' is None.", str(context.exception))

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

		self.assertEqual([run.GetElement("Prepare")], run.GetElement("Package").Needs)
		self.assertEqual([run.GetElement("Prepare"), run.GetElement("Package")], run.GetElement("Local").Needs)
		self.assertEqual(
			[run.GetElement("Prepare"), run.GetElement("Package"), run.GetElement("Local")], run.GetElement("Foreign").Needs
		)

		package = run.GetElement("Package")
		self.assertIsInstance(package.GetElement("Build"), CIMatrix)
		self.assertEqual([package.GetElement("Parameters")], package.GetElement("Build").Needs)
		self.assertEqual(
			[package.GetElement("Parameters"), package.GetElement("Build")], package.GetElement("Static").Needs
		)

		local = run.GetElement("Local")
		self.assertEqual([local.GetElement("Parameters")], local.GetElement("Build").Needs)

		self.assertEqual(["Local / Static"], missing)
		self.assertEqual([], run.GetElement("Foreign").GetElement("Publish").Needs)

	def test_Cycle(self) -> None:
		"""A need the run had already, which closes a cycle with the needs of the file, is found by validating the run."""
		self._write("Package.yml", CALLABLE)
		self._write("Prepare.yml", PREPARE)
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(("Prepare / Prepare", "success"), ("Package / Parameters", "success"))
		run.GetElement("Prepare").AddNeed(run.GetElement("Package"))

		with self.assertRaises(NeedDependencyCycleError):
			workflow.ApplyNeeds(run)

	def test_WithoutResolver(self) -> None:
		"""Without a resolver, only the jobs of the run's own workflow get dependencies."""
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(
			("Prepare / Prepare", "success"), ("Package / Parameters", "success"), ("Package / Build", "success")
		)

		missing = workflow.ApplyNeeds(run)

		self.assertEqual([run.GetElement("Prepare")], run.GetElement("Package").Needs)
		self.assertEqual([], run.GetElement("Package").GetElement("Build").Needs)
		self.assertEqual(["Local", "Foreign"], missing)

	def test_Twice(self) -> None:
		"""Applying the dependencies again adds nothing."""
		workflow = Workflow.FromFile(self._write("Pipeline.yml", CALLER))
		run = self._run(("Prepare / Prepare", "success"), ("Package / Parameters", "success"))

		workflow.ApplyNeeds(run)
		workflow.ApplyNeeds(run)

		self.assertEqual([run.GetElement("Prepare")], run.GetElement("Package").Needs)

	def test_Matrix(self) -> None:
		"""An instance of a static matrix gets the names of the combination its values are those of."""
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Test:
			    runs-on: x
			    strategy:
			      matrix:
			        os: [ubuntu, windows]
			        python: ['3.14']
			        include:
			          - os: macos
			            python: '3.13'
			            experimental: true
			          - os: ubuntu
			            coverage: true
			    steps: []
			  Calls:
			    uses: ./.github/workflows/Prepare.yml
			    strategy:
			      matrix:
			        python: ['3.13']
		""")))
		run = self._run(
			("Test (ubuntu, 3.14, true)", "success"),
			("Test (windows, 3.14)", "success"),
			("Test (macos, 3.13, true)", "success"),
			("Test (linux, 3.12)", "success"),
			("Calls (3.13) / Prepare", "success")
		)

		workflow.ApplyNeeds(run)

		test = run.GetElement("Test")
		self.assertDictEqual(
			{"os": "ubuntu", "python": "3.14", "coverage": "true"}, test.GetElement("Test (ubuntu, 3.14, true)").Dimensions
		)
		self.assertDictEqual({"os": "windows", "python": "3.14"}, test.GetElement("Test (windows, 3.14)").Dimensions)
		self.assertDictEqual(
			{"os": "macos", "python": "3.13", "experimental": "true"}, test.GetElement("Test (macos, 3.13, true)").Dimensions
		)
		self.assertDictEqual({"0": "linux", "1": "3.12"}, test.GetElement("Test (linux, 3.12)").Dimensions)
		self.assertDictEqual({"python": "3.13"}, run.GetElement("Calls").GetElement("Calls (3.13)").Dimensions)
		self.assertEqual("Test (ubuntu, 3.14, true)", str(test.GetElement("Test (ubuntu, 3.14, true)")))

	def test_Matrix_Dynamic(self) -> None:
		"""An instance of a dynamic matrix keeps the positions as names."""
		workflow = Workflow.FromFile(self._write("A.yml", dedent("""\
			on: push
			jobs:
			  Test:
			    runs-on: x
			    strategy:
			      matrix:
			        include: ${{ fromJson(inputs.jobs) }}
			    steps: []
		""")))
		run = self._run(("Test (ubuntu, 3.14)", "success"))

		workflow.ApplyNeeds(run)

		self.assertDictEqual(
			{"0": "ubuntu", "1": "3.14"}, run.GetElement("Test").GetElement("Test (ubuntu, 3.14)").Dimensions
		)

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
		self.assertEqual([], run.GetElement("ubuntu Tests").Needs)

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


#: A workflow of a repository, running a local action, an action of the repository and a job in containers.
REPOSITORY_WORKFLOW = dedent("""\
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
	      cache: redis:8
	    steps:
	      - uses: ./.github/actions/Composite
	      - uses: owner/repo/.github/actions/Docker@r1
	      - uses: other/repo@v1
	      - uses: ./.github/actions/Missing
""")

#: A composite action, running a local action, an action of another repository and a Docker image.
COMPOSITE = dedent("""\
	name: Composite Action
	runs:
	  using: composite
	  steps:
	    - name: Nested
	      uses: ./.github/actions/Docker
	    - uses: actions/checkout@v6
	    - run: echo
	      shell: bash
	    - uses: docker://alpine:3.22
""")

#: A Docker action.
DOCKER = dedent("""\
	runs:
	  using: docker
	  image: Dockerfile
""")


class Actions(Fixture):
	def _repository(self) -> tuple[WorkflowResolver, Workflow]:
		"""
		Write a repository with a workflow and two actions, and map ``owner/repo`` to its workflow directory.

		:returns: The resolver and the workflow.
		"""
		workflows = self._path / ".github" / "workflows"
		workflows.mkdir(parents=True)
		for name, content in (("Composite", COMPOSITE), ("Docker", DOCKER)):
			(self._path / ".github" / "actions" / name).mkdir(parents=True)
			(self._path / ".github" / "actions" / name / "action.yml").write_text(content, encoding="utf-8")
		(workflows / "Build.yml").write_text(REPOSITORY_WORKFLOW, encoding="utf-8")

		resolver = WorkflowResolver({"owner/repo": workflows})
		return resolver, resolver.Load(workflows / "Build.yml")

	def test_Composite(self) -> None:
		self._repository()
		action = Action.FromFile(self._path / ".github" / "actions" / "Composite" / "action.yml")

		self.assertEqual("Composite", action.Name)
		self.assertEqual("Composite Action", action.DisplayName)
		self.assertEqual("composite", action.Using)
		self.assertTrue(action.IsComposite)
		self.assertIsNone(action.Image)
		self.assertEqual(4, action.StepCount)
		self.assertEqual("Nested", action.Steps[0].Name)
		self.assertIs(action, action.Steps[0].Parent)
		self.assertEqual(
			["./.github/actions/Docker", "actions/checkout@v6", "docker://alpine:3.22"],
			[str(uses) for uses in action.IterateActions()]
		)
		self.assertEqual(6, action.Steps[0].Uses.Line)

	def test_Composite_Location(self) -> None:
		"""An element inside an action is located in the action's file."""
		self._repository()
		path = self._path / ".github" / "actions" / "Composite" / "action.yml"
		action = Action.FromFile(path)

		self.assertEqual(path, action.File)
		self.assertEqual("action.yml:1", action.Location)
		self.assertEqual(path, action.Steps[0].File)
		self.assertIsNone(action.Steps[0].Workflow)
		self.assertEqual(f"action.yml:{action.Steps[0].Line}", action.Steps[0].Location)
		self.assertEqual("action.yml:6", action.Steps[0].Uses.Location)

	def test_Docker(self) -> None:
		self._repository()
		action = Action.FromFile(self._path / ".github" / "actions" / "Docker" / "action.yml")

		self.assertEqual("docker", action.Using)
		self.assertFalse(action.IsComposite)
		self.assertEqual("Dockerfile", action.Image)
		self.assertEqual([], action.Steps)

	def test_Errors(self) -> None:
		path = self._write("action.yml", "name: Nothing\n")
		with self.assertRaises(WorkflowError) as context:
			_ = Action.FromFile(path)

		self.assertEqual("Action file has no 'runs' key.", str(context.exception).splitlines()[0])

		self._write("action.yml", "runs:\n  steps: []\n")
		with self.assertRaises(WorkflowError) as context:
			_ = Action.FromFile(path)

		self.assertEqual("Key 'runs' has no 'using' key.", str(context.exception).splitlines()[0])
		self.assertEqual(1, context.exception.Line)

		with self.assertRaises(ValueError):
			_ = Action(None, "composite")

		with self.assertRaises(ValueError):
			_ = Action(path, None)

		with self.assertRaises(WorkflowError) as context:
			_ = Action.FromFile(self._path / "Missing" / "action.yml")

		self.assertEqual("Action file doesn't exist.", str(context.exception))
		self.assertIsInstance(context.exception.__cause__, FileNotFoundError)

		with self.assertRaises(WorkflowError) as context:
			_ = Action.FromFile(self._path)

		self.assertEqual("Action file can't be read.", str(context.exception))

	def test_Construction(self) -> None:
		path =   Path("Setup") / "action.yml"
		step =   Step(4, run="make")
		action = Action(path, "composite", steps=(step, ))

		self.assertEqual([step], action.Steps)
		self.assertIs(action, step.Parent)
		self.assertEqual(path, step.File)
		self.assertEqual("action.yml:4", step.Location)

		with self.assertRaises(TypeError) as context:
			_ = Action(path, "composite", steps=("make", ))

		self.assertEqual("An element of parameter 'steps' is not of type 'Step'.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			action.Parent = Job("Build", 2)

		self.assertEqual("A 'pyTooling.CI.GitHub.WorkflowFile.Action' has no parent.", str(context.exception))

	def test_Step_Parent(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Step(1, parent=Workflow(Path("Build.yml")))

		self.assertEqual("Parameter 'parent' is not of type 'Job' or 'Action'.", str(context.exception))

	def test_Containers(self) -> None:
		_, workflow = self._repository()
		job = workflow.Jobs["Build"]

		self.assertEqual("${{ inputs.image }}", job.Container)
		self.assertEqual({"database": "postgres:18", "cache": "redis:8"}, job.Services)
		self.assertIsNone(Job("Test", 1).Container)
		self.assertEqual({}, Job("Test", 1).Services)

		job = Job("Test", 1, container="python:3.14", services={"cache": "redis:8"})
		self.assertEqual("python:3.14", job.Container)
		self.assertEqual({"cache": "redis:8"}, job.Services)

		with self.assertRaises(TypeError) as context:
			_ = Job("Test", 1, container=3.14)

		self.assertEqual("Parameter 'container' is not of type 'str'.", str(context.exception))

	def test_ResolveAction(self) -> None:
		"""A local action, an action of a mapped repository, and a local action called by an action are read."""
		resolver, workflow = self._repository()
		steps = workflow.Jobs["Build"].Steps

		composite = resolver.ResolveAction(steps[0].Uses)
		docker = resolver.ResolveAction(steps[1].Uses)
		self.assertEqual("Composite", composite.Name)
		self.assertEqual("Docker", docker.Name)
		self.assertIs(docker, resolver.ResolveAction(composite.Steps[0].Uses))
		self.assertIsNone(resolver.ResolveAction(steps[2].Uses))
		self.assertIsNone(resolver.ResolveAction(composite.Steps[3].Uses))

	def test_ResolveAction_Workflow(self) -> None:
		resolver = WorkflowResolver()

		self.assertIsNone(resolver.ResolveAction(UsesReference("owner/repo/.github/workflows/Build.yml@r1", 1)))
		self.assertIsNone(resolver.ResolveAction(UsesReference("./.github/actions/Composite", 1)))

	def test_ResolveAction_Outside(self) -> None:
		"""A mapped directory outside a '.github' directory has no repository root to find actions in."""
		resolver = WorkflowResolver({"owner/repo": self._path})

		self.assertIsNone(resolver.ResolveAction(UsesReference("owner/repo/.github/actions/Composite@r1", 1)))

	def test_ResolveAction_Missing(self) -> None:
		resolver, workflow = self._repository()

		with self.assertRaises(WorkflowError) as context:
			_ = resolver.ResolveAction(workflow.Jobs["Build"].Steps[3].Uses)

		directory = self._path / ".github" / "actions" / "Missing"
		self.assertEqual(
			f"Action '.github/actions/Missing' has no 'action.yml' in '{directory}'.", str(context.exception).splitlines()[0]
		)
		self.assertEqual(17, context.exception.Line)
		self.assertEqual(self._path / ".github" / "workflows" / "Build.yml", context.exception.Path)
