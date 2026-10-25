# ==================================================================================================================== #
#                                                                                                                      #
#             _____           _ _               _____                    _   _                                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/                        #
# |_|    |___/                          |___/                     |_|                                                  #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.Exceptions`.
"""
from pickle                import dumps, loads

from pyTooling.CallGraph   import DuplicateFunctionError
from pyTooling.CI          import NeedDependencyCycleError
from pyTooling.ControlFlow import DuplicateBlockError, DuplicateEdgeError as ControlFlowDuplicateEdgeError
from pyTooling.Dependency  import CircularRequirementsFileError
from pyTooling.Exceptions  import AlreadyInHierarchyError, CycleError, DuplicateElementError, \
                                  EnvironmentVariableError, ExceptionBase, InUseError, MissingDependencyError, \
                                  NotAChildError, NotConfiguredError, NotInSameHierarchyError, \
                                  PlatformNotSupportedError, ToolingException
from pyTooling.Graph       import CycleError as GraphCycleError, DuplicateEdgeError, DuplicateVertexError, \
                                  NotInSameGraph
from pyTooling.LinkedList  import NotInSameListError
from pyTooling.Testing     import Testcase
from pyTooling.Tracing     import SpanCycleError
from pyTooling.Tree        import AlreadyInTreeError, NotAChildError as TreeNotAChildError, NotInSameTreeError


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def raise_EnvironmentExecption() -> None:
	raise EnvironmentVariableError("Environment does not provide 'PATH'.")


def raise_PlatformNotSupportedError() -> None:
	raise PlatformNotSupportedError("Platform 'macOS' is not supported.")


def raise_NotConfiguredError() -> None:
	raise NotConfiguredError("Option 'WorkingDirectory' is not specified in the configuration file.")


class Exceptions(Testcase):
	def test_EnvironmentVariableError(self) -> None:
		with self.assertRaises(EnvironmentVariableError):
			raise_EnvironmentExecption()
		# self.assertEqual(context.exception.message, "Environment does not provide 'PATH'.")

	def test_PlatformNotSupportedError(self) -> None:
		with self.assertRaises(PlatformNotSupportedError):
			raise_PlatformNotSupportedError()
		# self.assertEqual(context.exception.message, "Platform 'OSX' is not supported.")

	def test_NotConfiguredError(self) -> None:
		with self.assertRaises(NotConfiguredError):
			raise_NotConfiguredError()
		# self.assertEqual(context.exception.message, "Option 'WorkingDirectory' is not specified in the configuration file.")


class CommonBases(Testcase):
	def test_DuplicateElementError(self) -> None:
		for exception in (DuplicateVertexError, DuplicateEdgeError, DuplicateBlockError, ControlFlowDuplicateEdgeError,
		                  DuplicateFunctionError):
			with self.subTest(exception=exception.__name__):
				self.assertTrue(issubclass(exception, DuplicateElementError))
				self.assertTrue(issubclass(exception, ToolingException))

	def test_CycleError(self) -> None:
		for exception in (GraphCycleError, NeedDependencyCycleError, CircularRequirementsFileError, SpanCycleError):
			with self.subTest(exception=exception.__name__):
				self.assertTrue(issubclass(exception, CycleError))
				self.assertTrue(issubclass(exception, ToolingException))

	def test_AlreadyInHierarchyError(self) -> None:
		self.assertTrue(issubclass(AlreadyInTreeError, AlreadyInHierarchyError))
		self.assertTrue(issubclass(AlreadyInTreeError, ToolingException))

	def test_NotInSameHierarchyError(self) -> None:
		for exception in (NotInSameGraph, NotInSameTreeError, NotInSameListError):
			with self.subTest(exception=exception.__name__):
				self.assertTrue(issubclass(exception, NotInSameHierarchyError))
				self.assertTrue(issubclass(exception, ToolingException))

	def test_NotAChildError(self) -> None:
		self.assertTrue(issubclass(TreeNotAChildError, NotAChildError))
		self.assertTrue(issubclass(TreeNotAChildError, ToolingException))

	def test_InUseError(self) -> None:
		"""A package's own error derives from its base-exception and 'InUseError'; both catch it."""
		class ElementInUseError(ToolingException, InUseError):
			pass

		with self.assertRaises(InUseError) as context:
			raise ElementInUseError("Element 'a' is still used by 'b'.")

		self.assertIsInstance(context.exception, ToolingException)
		self.assertEqual("Element 'a' is still used by 'b'.", str(context.exception))

	def test_ToolingExceptionMessage(self) -> None:
		"""A common base doesn't change how a 'ToolingException' stores its message."""
		ex = DuplicateVertexError("Vertex ID '1' already exists in this graph.", vertexID=1)

		self.assertEqual("Vertex ID '1' already exists in this graph.", str(ex))
		self.assertEqual(("Vertex ID '1' already exists in this graph.", ), ex.args)
		self.assertEqual(1, ex.VertexID)

	def test_ExceptionBaseArgs(self) -> None:
		"""The message is the exception's only argument, like any Python exception's."""
		ex = EnvironmentVariableError("Environment does not provide 'PATH'.")

		self.assertEqual(("Environment does not provide 'PATH'.", ), ex.args)
		self.assertEqual("EnvironmentVariableError(\"Environment does not provide 'PATH'.\")", repr(ex))

	def test_ExceptionBasePickle(self) -> None:
		"""A pickled exception keeps its message and its arguments."""
		ex = EnvironmentVariableError("Environment does not provide 'PATH'.")
		copy = loads(dumps(ex))

		self.assertEqual("Environment does not provide 'PATH'.", copy.Message)
		self.assertEqual(ex.args, copy.args)

	def test_ExceptionBaseMessage(self) -> None:
		"""A common base combined with 'ExceptionBase' keeps its message."""
		class DuplicateItemError(ExceptionBase, DuplicateElementError):
			"""Nested exception class of a package deriving from 'ExceptionBase'."""

		with self.assertRaises(DuplicateElementError) as context:
			raise DuplicateItemError("Item 'A' already exists.")

		self.assertEqual("Item 'A' already exists.", str(context.exception))
		self.assertEqual("Item 'A' already exists.", context.exception.Message)


class MissingDependency(Testcase):
	"""An optional dependency that is not installed names itself and the extra installing it."""

	def test_WithExtra(self) -> None:
		with self.assertRaises(MissingDependencyError) as context:
			raise MissingDependencyError(dependency="colorama", extra="terminal")

		self.assertEqual("colorama", context.exception.Dependency)
		self.assertEqual("terminal", context.exception.Extra)
		self.assertEqual("Optional dependency 'colorama' not installed.", str(context.exception))
		self.assertIn("pyTooling[terminal]", context.exception.__notes__[0])

	def test_WithoutExtra(self) -> None:
		with self.assertRaises(MissingDependencyError) as context:
			raise MissingDependencyError(dependency="lxml")

		self.assertEqual("lxml", context.exception.Dependency)
		self.assertIsNone(context.exception.Extra)
		self.assertEqual("Install 'lxml'.", context.exception.__notes__[0])

	def test_InstallCommands_WithExtra(self) -> None:
		"""The extra comes first: it installs the package and records why it is needed."""
		ex = MissingDependencyError(dependency="ruamel.yaml", extra="yaml")

		self.assertEqual(("pip install pyTooling[yaml]", "pip install ruamel.yaml"), ex.InstallCommands)

	def test_InstallCommands_WithoutExtra(self) -> None:
		ex = MissingDependencyError(dependency="lxml")

		self.assertEqual(("pip install lxml", ), ex.InstallCommands)

	def test_WithAnExplicitMessage(self) -> None:
		with self.assertRaises(MissingDependencyError) as context:
			raise MissingDependencyError("The YAML reader needs 'ruamel.yaml'.", dependency="ruamel.yaml", extra="yaml")

		self.assertEqual("The YAML reader needs 'ruamel.yaml'.", str(context.exception))

	def test_IsAnImportError(self) -> None:
		"""A caller guarding an optional import catches :exc:`ImportError`, so the new exception has to be one."""
		with self.assertRaises(ImportError):
			raise MissingDependencyError(dependency="lxml")

	def test_IsAToolingException(self) -> None:
		"""A caller handling pyTooling's own errors catches :exc:`ToolingException`; it isn't an :exc:`ExceptionBase`."""
		with self.assertRaises(ToolingException) as context:
			raise MissingDependencyError(dependency="lxml")

		self.assertNotIsInstance(context.exception, ExceptionBase)

	def test_ImportErrorName(self) -> None:
		""":attr:`ImportError.name` is the missing package, as for Python's own import errors."""
		ex = MissingDependencyError(dependency="ruamel.yaml", extra="yaml")

		self.assertEqual("ruamel.yaml", ex.name)
		self.assertEqual("Optional dependency 'ruamel.yaml' not installed.", ex.msg)
