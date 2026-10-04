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
Unit tests for :class:`pyTooling.CLIAbstraction.Program`, using ``git`` as the abstracted program: path
resolution per platform, common options, and a sub-command with its own options.
"""
from pathlib      import Path
from typing       import Any, Self

from pytest       import mark
from sys          import platform as sys_platform

from pyTooling.CLIAbstraction          import Executable, Program, CLIAbstractionError, CLIArgument
from pyTooling.CLIAbstraction.Argument import formatCommandLine
from pyTooling.CLIAbstraction.Flag     import LongFlag
from pyTooling.Testing                 import Testcase
from .                                 import Helper
from .Examples                         import GitArgumentsMixin


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Git(Program, GitArgumentsMixin):
	def __new__(cls, *args: Any, **kwargs: Any) -> Self:
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


class GitWithoutArguments(Program):
	_executableNames = {
		"Darwin":  "git",
		"FreeBSD": "git",
		"Linux":   "git",
		"Windows": "git.exe"
	}


@mark.skipif(sys_platform in ("darwin", "linux", "win32"), reason="Don't run these tests on Linux, macOS and Windows.")
class ExplicitPathsOnFreeBSD(Testcase, Helper):
	_binaryDirectoryPath = Path("/usr/local/bin")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt")


@mark.skipif(sys_platform in ("freebsd", "win32"), reason="Don't run these tests on FreeBSD and Windows.")
class ExplicitPathsOnLinux(Testcase, Helper):
	_binaryDirectoryPath = Path("/usr/bin")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt")


@mark.skipif(sys_platform in ("darwin", "freebsd", "linux"), reason="Don't run these tests on FreeBSD, Linux or macOS.")
class ExplicitPathsOnWindows(Testcase, Helper):
	_binaryDirectoryPath = Path(r"C:\Program Files\Git\cmd")

	def test_BinaryDirectory(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_BinaryDirectory_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(binaryDirectoryPath=str(self._binaryDirectoryPath))

	def test_BinaryDirectory_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(binaryDirectoryPath=self._binaryDirectoryPath / "git")

	def test_ExecutablePath(self) -> None:
		tool = Git(executablePath=self._binaryDirectoryPath / "git.exe")

		executable = self.GetExecutablePath("git", self._binaryDirectoryPath)
		self.assertEqual(Path(executable), tool.Path)
		self.assertListEqual([executable], tool.ToArgumentList())
		self.assertEqual(repr([executable]), repr(tool))
		self.assertEqual(formatCommandLine([executable]), str(tool))

	def test_ExecutablePath_NotAPath(self) -> None:
		with self.assertRaises(TypeError):
			_ = Git(executablePath=str(self._binaryDirectoryPath / "git.exe"))

	def test_ExecutablePath_DoesNotExist(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Git(executablePath=self._binaryDirectoryPath / "gitt.exe")


class CommonOptions(Testcase, Helper):
	def test_UnknownOS(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = GitUnknownOS()

	def test_BinaryDirectory_UnknownOS(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = GitUnknownOS(binaryDirectoryPath=Path(""))

	def test_NotInPath(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			_ = Gitt()

	def test_SearchedInPath(self) -> None:
		"""A program searched in PATH keeps the path it was found at, so a variant can be built from it."""
		tool = Git()

		self.assertTrue(tool.Path.is_absolute())
		self.assertEqual(Path(self.GetExecutablePath("git")), tool.Path)

		variant = Git(executablePath=tool.Path)
		self.assertEqual(tool.Path, variant.Path)

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
		self.assertEqual(repr([executable, "--version"]), repr(tool))
		self.assertEqual(formatCommandLine([executable, "--version"]), str(tool))

	def test_HelpFlag(self) -> None:
		tool = Git()
		tool[tool.FlagHelp] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "--help"], tool.ToArgumentList())
		self.assertEqual(repr([executable, "--help"]), repr(tool))
		self.assertEqual(formatCommandLine([executable, "--help"]), str(tool))

	def test_HelpCommand(self) -> None:
		tool = Git()
		tool[tool.CommandHelp] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "help"], tool.ToArgumentList())
		self.assertEqual(repr([executable, "help"]), repr(tool))
		self.assertEqual(formatCommandLine([executable, "help"]), str(tool))


class Commit(Testcase, Helper):
	def test_CommitWithMessage(self) -> None:
		tool = Git()
		tool[tool.CommandCommit] = True
		tool[tool.ValueCommitMessage] = "Initial commit."

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "commit", "-m", "Initial commit."], tool.ToArgumentList())
		self.assertEqual(repr([executable, "commit", "-m", "Initial commit."]), repr(tool))
		self.assertEqual(formatCommandLine([executable, "commit", "-m", "Initial commit."]), str(tool))


class DryRun(Testcase):
	"""In dry-run mode, a missing program or a started process is recorded instead of raising or running."""

	def test_AMissingExecutableIsRecorded(self) -> None:
		gitt = Gitt(executablePath=Path("does/not/exist/gitt"), dryRun=True)

		self.assertEqual(["File check for 'does/not/exist/gitt' failed. [SKIPPING]"], [
			message.replace("\\", "/") for message in gitt.DryRunMessages
		])

	def test_AMissingBinaryDirectoryIsRecorded(self) -> None:
		gitt = Gitt(binaryDirectoryPath=Path("does/not/exist"), dryRun=True)

		self.assertEqual(2, len(gitt.DryRunMessages))
		self.assertIn("Directory check", gitt.DryRunMessages[0])

	def test_AProgramNotInPathIsRecorded(self) -> None:
		gitt = Gitt(dryRun=True)

		self.assertEqual(1, len(gitt.DryRunMessages))
		self.assertIn("in PATH failed", gitt.DryRunMessages[0])

	def test_StartingAProcessIsRecorded(self) -> None:
		class Gittex(Executable):
			_executableNames = Gitt._executableNames

		gittex = Gittex(executablePath=Path("does/not/exist/gitt"), dryRun=True)
		gittex.StartProcess()

		self.assertIsNone(gittex._process)
		self.assertEqual(f"Start process: {formatCommandLine(gittex.ToArgumentList())}", gittex.DryRunMessages[-1])

	def test_WithoutDryRunAMissingExecutableRaises(self) -> None:
		with self.assertRaises(CLIAbstractionError):
			Gitt(executablePath=Path("does/not/exist/gitt"))


class Derive(Testcase, Helper):
	def test_CopyParameters(self) -> None:
		tool = Git()
		tool[tool.CommandCommit] = True
		tool[tool.ValueCommitMessage] = "Initial commit."

		variant = Git()
		tool._CopyParameters(variant)

		self.assertListEqual(tool.ToArgumentList(), variant.ToArgumentList())
		self.assertIsNot(tool[tool.ValueCommitMessage], variant[variant.ValueCommitMessage])

	def test_CopyParameters_ThenSetExplicitly(self) -> None:
		tool = Git()
		tool[tool.FlagVersion] = True

		variant = Git()
		tool._CopyParameters(variant)
		variant[variant.CommandCommit] = True

		executable = self.GetExecutablePath("git")
		self.assertListEqual([executable, "--version"], tool.ToArgumentList())
		self.assertListEqual([executable, "--version", "commit"], variant.ToArgumentList())

	def test_CopyParameters_SetAlready(self) -> None:
		tool = Git()
		tool[tool.FlagVersion] = True

		variant = Git()
		variant[variant.FlagVersion] = True

		with self.assertRaises(KeyError):
			tool._CopyParameters(variant)

	def test_CopyParameters_NotDeclared(self) -> None:
		tool = Git()
		tool[tool.FlagVersion] = True

		with self.assertRaises(KeyError):
			tool._CopyParameters(GitWithoutArguments())

	def test_CopyParameters_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Git()._CopyParameters(None)

		self.assertEqual("Parameter 'tool' is None.", str(context.exception))

	def test_CopyParameters_NotAProgram(self) -> None:
		with self.assertRaises(TypeError) as context:
			Git()._CopyParameters("git")

		self.assertEqual("Parameter 'tool' is not of type 'Program'.", str(context.exception))
