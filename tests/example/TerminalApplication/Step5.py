# ==================================================================================================================== #
#             _____           _ _                                                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _                                                                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |                                                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |                                                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |                                                                         #
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
from sys                  import argv
from typing               import ClassVar, NoReturn

from pyTooling.Exceptions import ExceptionBase, MissingDependencyException
from pyTooling.TerminalUI import TerminalApplication

from myPackage            import MyPackageException, __issue_tracker_url__


class Application(TerminalApplication):
	HeadLine:          ClassVar[str] = "My Application"
	ISSUE_TRACKER_URL: ClassVar[str] = __issue_tracker_url__

	def Run(self) -> None:
		self._PrintHeadline()
		self.WriteNormal("Reading the input file...")


def main() -> NoReturn:
	program = Application()
	program.Configure(
		verbose=("-v" in argv or "--verbose" in argv),
		debug=(  "-d" in argv or "--debug"   in argv),
		quiet=(  "-q" in argv or "--quiet"   in argv)
	)

	try:
		program.Run()
	except MyPackageException as ex:                      # the program's own exceptions, reported as messages
		program.WriteLineToStdErr(f"{{RED}}[ERROR] {ex}{{NOCOLOR}}".format(**Application.Foreground))
	except ExceptionBase as ex:
		program.PrintExceptionBase(ex)                      # exit code 241, a known exception
	except NotImplementedError as ex:
		program.PrintNotImplementedError(ex)                # exit code 240, an unimplemented function was called
	except MissingDependencyException as ex:
		program.PrintMissingDependencyException(ex)         # exit code 242, an installation problem
	except Exception as ex:
		program.PrintException(ex)                          # exit code 241, an unexpected exception

	program.Exit()


if __name__ == "__main__":
	main()
