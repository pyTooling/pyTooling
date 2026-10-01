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
from textwrap                         import dedent
from typing                           import Any

from pyTooling.CI.GitHub.WorkflowFile import AccessLevel, Base, InputType, Workflow, WorkflowError, Input, Output
from pyTooling.CI.GitHub.WorkflowFile import Permission, PermissionScope, Secret
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
			_ = Permission._FromYAML(value, Path("A.yml"), 2, None)

		self.assertEqual(Path("A.yml"), context.exception.Path)

		return context.exception

	def test_Mapping(self) -> None:
		mapping = YAML(typ="rt").load("contents: read\nid-token: write\n")
		permissions = Permission._FromYAML(mapping, Path("A.yml"), 1, None)

		self.assertEqual([PermissionScope.Contents, PermissionScope.IDToken], list(permissions))
		self.assertEqual(["contents", "id-token"], list(permissions))
		self.assertIs(AccessLevel.Write, permissions["id-token"].Level)
		self.assertEqual("contents: read", str(permissions["contents"]))
		self.assertEqual(2, permissions["id-token"].Line)
		self.assertEqual("line 2", permissions["id-token"].Location)

	def test_ShortForm(self) -> None:
		for value, level in (("read-all", AccessLevel.Read), ("write-all", AccessLevel.Write)):
			with self.subTest(value=value):
				permission = Permission._FromYAML(value, Path("A.yml"), 7, None)[PermissionScope.All]

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

		with self.assertRaises(FileNotFoundError):
			_ = Workflow.FromFile(self._path / "Missing.yml")


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
