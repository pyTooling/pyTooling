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
# Copyright 2007-2016 Technische Universität Dresden - Germany, Chair of VLSI-Design, Diagnostics and Architecture     #
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

from pyTooling.CLIAbstraction import Executable, Environment
from .                        import Helper
from .Examples                import GitArgumentsMixin


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Git(Executable, GitArgumentsMixin):
	def __new__(cls, *args: Any, **kwargs: Any):
		cls._executableNames = {
			"Darwin":  "git",
			"FreeBSD": "git",
			"Linux":   "git",
			"Windows": "git.exe"
		}
		return super().__new__(cls)


@mark.skipif(sys_platform in ("darwin", "linux", "win32"), reason="Don't run these tests on Linux, macOS and Windows.")
class ExplicitBinaryDirectoryOnFreeBSD(TestCase, Helper):
	_binaryDirectoryPath = Path("/usr/local/bin")

	def test_VersionFlag(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)
		tool[tool.FlagVersion] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"git version \d+.\d+.\d+")


@mark.skipif(sys_platform in ("freebsd", "win32"), reason="Don't run these tests on FreeBSD and Windows.")
class ExplicitBinaryDirectoryOnLinux(TestCase, Helper):
	_binaryDirectoryPath = Path("/usr/bin")

	def test_VersionFlag(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)
		tool[tool.FlagVersion] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"git version \d+.\d+.\d+")


@mark.skipif(sys_platform in ("darwin", "freebsd", "linux"), reason="Don't run these tests on FreeBSD, Linux or macOS.")
class ExplicitBinaryDirectoryOnWindows(TestCase, Helper):
	_binaryDirectoryPath = Path(r"C:\Program Files\Git\cmd")

	def test_VersionFlag(self) -> None:
		tool = Git(binaryDirectoryPath=self._binaryDirectoryPath)
		tool[tool.FlagVersion] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"git version \d+.\d+.\d+.windows.\d+")


class CommonOptions(TestCase, Helper):
	def test_VersionFlag(self) -> None:
		print()
		tool = Git()
		tool[tool.FlagVersion] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"git version \d+.\d+.\d+(.windows.\d+)?")

		print(output)

	def test_HelpFlag(self) -> None:
		print()
		tool = Git()
		tool[tool.FlagHelp] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"^usage: git")

		print(output)

	def test_HelpCommand(self) -> None:
		print()
		tool = Git()
		tool[tool.CommandHelp] = True

		tool.StartProcess(environment=Environment(addVariables={"LANGUAGE": "C"}))
		output = "\n".join(tool.GetLineReader())
		self.assertRegex(output, r"^usage: git")

		print(output)

# class Commit(TestCase, Helper):
# 	def test_CommitWithMessage(self) -> None:
# 		tool = Git()
# 		tool[tool.CommandCommit] = True
# 		tool[tool.ValueCommitMessage] = "Initial commit."
#
# 		executable = self.GetExecutablePath("git")
# 		tool.StartProcess()
