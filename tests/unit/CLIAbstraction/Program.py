# ==================================================================================================================== #
#             _____           _ _               ____ _     ___    _    _         _                  _   _              #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|  / \  | |__  ___| |_ _ __ __ _  ___| |_(_) ___  _ __   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |  / _ \ | '_ \/ __| __| '__/ _` |/ __| __| |/ _ \| '_ \  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | | / ___ \| |_) \__ \ |_| | | (_| | (__| |_| | (_) | | | | #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___/_/   \_\_.__/|___/\__|_|  \__,_|\___|\__|_|\___/|_| |_| #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Testcase for operating system program ``mkdir``.

:copyright: Copyright 2007-2025 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from pathlib      import Path
from typing       import Any

from pytest       import mark
from sys          import platform as sys_platform
from unittest     import TestCase

from pyTooling.CLIAbstraction import Program, CLIAbstractionException, CLIArgument
from pyTooling.CLIAbstraction.Flag import LongFlag
from .                        import Helper
from .Examples                import GitArgumentsMixin


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Git(Program, GitArgumentsMixin):
	def __new__(cls, *args: Any, **kwargs: Any):
		cls._executableNames = {
			"Darwin":  "git",
			"FreeBSD": "git",
			"Linux":   "git",
			"Windows": "git.exe"
		}
		return super().__new__(cls)


class Gitt(Program):
	_executableNames = {
		"Darwin":  "gitt",
		"FreeBSD": "gitt",
		"Linux":   "gitt",
		"Windows": "gitt.exe"
	}

	@CLIArgument()
	class FlagVersion(LongFlag, name="version"):
		...


class GitUnknownOS(Program):
	_executableNames = {
		"UnknownOS": "git"
	}


@mark.skipif(sys_platform in ("darwin", "linux", "win32"), reason="Don't run these tests on Linux, macOS and Windows.")
class ExplicitPathsOnFreeBSD(TestCase, Helper):
	_binaryDirectoryPath = Path("/usr/local/bin")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt")


@mark.skipif(sys_platform in ("freebsd", "win32"), reason="Don't run these tests on FreeBSD and Windows.")
class ExplicitPathsOnLinux(TestCase, Helper):
	_binaryDirectoryPath = Path("/usr/bin")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt")


@mark.skipif(sys_platform in ("darwin", "freebsd", "linux"), reason="Don't run these tests on FreeBSD, Linux or macOS.")
class ExplicitPathsOnWindows(TestCase, Helper):
	_binaryDirectoryPath = Path(r"C:\Program Files\Git\cmd")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git.exe")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\"]", repr(tool))
		self.assertEqual(f"\"{executable}\"", str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git.exe"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt.exe")


class CommonOptions(TestCase, Helper):
	def test_UnknownOS(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = GitUnknownOS()

	def test_BinaryDirectory_UnknownOS(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = GitUnknownOS(binaryDirectoryPath=Path(""))

	def test_NotInPath(self) -> None:
		with self.assertRaises(CLIAbstractionException):
			_ = Gitt()

	def test_SetUnknownFlag(self) -> None:
		tool = Git()
		with self.assertRaises(TypeError):
			tool["version"] = True

		with self.assertRaises(KeyError):
			tool[Gitt.FlagVersion] = True

		tool[tool.FlagVersion] = True
		with self.assertRaises(KeyError):
			tool[tool.FlagVersion] = True

	def test_GetUnknownFlag(self) -> None:
		tool = Git()
		with self.assertRaises(KeyError):
			_ = tool[tool.FlagVersion]

		tool[tool.FlagVersion] = True
		with self.assertRaises(TypeError):
			_ = tool["version"]

	def test_VersionFlag(self) -> None:
		tool = Git()
		tool[tool.FlagVersion] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "--version"], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\", \"--version\"]", repr(tool))

	def test_HelpFlag(self) -> None:
		tool = Git()
		tool[tool.FlagHelp] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "--help"], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\", \"--help\"]", repr(tool))

	def test_HelpCommand(self) -> None:
		tool = Git()
		tool[tool.CommandHelp] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "help"], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\", \"help\"]", repr(tool))


class Commit(TestCase, Helper):
	def test_CommitWithMessage(self) -> None:
		tool = Git()
		tool[tool.CommandCommit] = True
		tool[tool.ValueCommitMessage] = "Initial commit."

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "commit", "-m", "Initial commit."], tool.ToArgumentList())
		self.assertEqual(f"[\"{executable}\", \"commit\", \"-m\", \"Initial commit.\"]", repr(tool))
