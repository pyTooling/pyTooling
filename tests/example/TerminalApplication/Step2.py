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
from sys                 import argv
from typing              import NoReturn

from pyTooling.TerminalUI import TerminalApplication


class Application(TerminalApplication):
	HeadLine = "My Application"

	def Run(self) -> None:
		self._PrintHeadline()
		self.WriteNormal("Reading the input file...")

		if self.Verbose:
			self.WriteVerbose(self._CollectStatistics())    # not computed unless it's printed

		self.WriteWarning("The input file is empty.")

	def _CollectStatistics(self) -> str:
		return "  Line 1 of 4"


def main() -> NoReturn:
	program = Application()
	program.Configure(
		verbose=("-v" in argv or "--verbose" in argv),
		debug=(  "-d" in argv or "--debug"   in argv),
		quiet=(  "-q" in argv or "--quiet"   in argv)
	)
	program.Run()
	program.Exit()


if __name__ == "__main__":
	main()
