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
from textwrap                         import dedent
from typing                           import Any

from pyTooling.CI.GitHub.WorkflowFile import AccessLevel, Base, WorkflowError, Permission, PermissionScope
from pyTooling.CI.GitHub.WorkflowFile import UsesReference
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
		self.assertLess(AccessLevel.NoAccess.Rank(), AccessLevel.Read.Rank())
		self.assertLess(AccessLevel.Read.Rank(), AccessLevel.Write.Rank())
