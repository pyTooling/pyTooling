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
from argparse                             import Namespace, RawDescriptionHelpFormatter
from typing                               import ClassVar, NoReturn

from pyTooling.Attributes.ArgParse          import ArgParseHelperMixin, CommandHandler, DefaultHandler
from pyTooling.Attributes.ArgParse.Argument import StringArgument
from pyTooling.Decorators                   import export
from pyTooling.TerminalUI                   import TerminalApplication

from myPackage                              import __issue_tracker_url__


@export
class Application(TerminalApplication, ArgParseHelperMixin):
	HeadLine:          ClassVar[str] = "My Application"
	ISSUE_TRACKER_URL: ClassVar[str] = __issue_tracker_url__

	def __init__(self) -> None:
		super().__init__()
		ArgParseHelperMixin.__init__(self, prog="myapp", formatter_class=RawDescriptionHelpFormatter, add_help=False)

	def Run(self) -> None:
		ArgParseHelperMixin.Run(self)

	@DefaultHandler()
	def HandleDefault(self, _: Namespace) -> None:
		self._PrintHeadline()
		self._PrintHelp()

	@CommandHandler("help", help="Display help page(s) for the given command name.")
	@StringArgument(dest="Command", metaName="Command", optional=True, help="Print help page(s) for a command.")
	def HandleHelp(self, args: Namespace) -> None:
		self._PrintHeadline()
		self._PrintHelp(args.Command)

	@CommandHandler("version", help="Display version information.")
	def HandleVersion(self, _: Namespace) -> None:
		self._PrintHeadline()
		self._PrintVersion()

	def _PrintVersion(self) -> None:
		import myPackage as DunderModule

		super()._PrintVersion(DunderModule, "myPackage")


def main() -> NoReturn:
	program = Application()
	program.Run()
	program.Exit()


if __name__ == "__main__":
	main()
