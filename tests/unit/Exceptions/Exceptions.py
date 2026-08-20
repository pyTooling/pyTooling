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
from pyTooling.Exceptions import EnvironmentException, PlatformNotSupportedException, NotConfiguredException
from pyTooling.Exceptions import MissingDependencyException
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def raise_EnvironmentExecption() -> None:
	raise EnvironmentException("Environment does not provide 'PATH'.")


def raise_PlatformNotSupportedException() -> None:
	raise PlatformNotSupportedException("Platform 'macOS' is not supported.")


def raise_NotConfiguredException() -> None:
	raise NotConfiguredException("Option 'WorkingDirectory' is not specified in the configuration file.")


class Exceptions(Testcase):
	def test_EnvironmentException(self) -> None:
		with self.assertRaises(EnvironmentException):
			raise_EnvironmentExecption()
		# self.assertEqual(context.exception.message, "Environment does not provide 'PATH'.")

	def test_PlatformNotSupportedException(self) -> None:
		with self.assertRaises(PlatformNotSupportedException):
			raise_PlatformNotSupportedException()
		# self.assertEqual(context.exception.message, "Platform 'OSX' is not supported.")

	def test_NotConfiguredException(self) -> None:
		with self.assertRaises(NotConfiguredException):
			raise_NotConfiguredException()
		# self.assertEqual(context.exception.message, "Option 'WorkingDirectory' is not specified in the configuration file.")


class MissingDependency(Testcase):
	"""An optional dependency that is not installed names itself and the extra installing it."""

	def test_WithExtra(self) -> None:
		with self.assertRaises(MissingDependencyException) as context:
			raise MissingDependencyException(dependency="colorama", extra="terminal")

		self.assertEqual("colorama", context.exception.Dependency)
		self.assertEqual("terminal", context.exception.Extra)
		self.assertEqual("Optional dependency 'colorama' not installed.", str(context.exception))
		self.assertIn("pyTooling[terminal]", context.exception.__notes__[0])

	def test_WithoutExtra(self) -> None:
		with self.assertRaises(MissingDependencyException) as context:
			raise MissingDependencyException(dependency="lxml")

		self.assertEqual("lxml", context.exception.Dependency)
		self.assertIsNone(context.exception.Extra)
		self.assertEqual("Install 'lxml'.", context.exception.__notes__[0])

	def test_InstallCommands_WithExtra(self) -> None:
		"""The extra comes first: it installs the package and records why it is needed."""
		ex = MissingDependencyException(dependency="ruamel.yaml", extra="yaml")

		self.assertEqual(("pip install pyTooling[yaml]", "pip install ruamel.yaml"), ex.InstallCommands)

	def test_InstallCommands_WithoutExtra(self) -> None:
		ex = MissingDependencyException(dependency="lxml")

		self.assertEqual(("pip install lxml", ), ex.InstallCommands)

	def test_WithAnExplicitMessage(self) -> None:
		with self.assertRaises(MissingDependencyException) as context:
			raise MissingDependencyException("The YAML reader needs 'ruamel.yaml'.", dependency="ruamel.yaml", extra="yaml")

		self.assertEqual("The YAML reader needs 'ruamel.yaml'.", str(context.exception))

	def test_IsAnImportError(self) -> None:
		"""A caller guarding an optional import catches :exc:`ImportError`, so the new exception has to be one."""
		with self.assertRaises(ImportError):
			raise MissingDependencyException(dependency="lxml")
