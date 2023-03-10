# ==================================================================================================================== #
#             _____           _ _             _____                   _             _ _   _ ___                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _|__ _ __ _ __ ___ (_)_ __   __ _| | | | |_ _|                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |/ _ \ '__| '_ ` _ \| | '_ \ / _` | | | | || |                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  __/ |  | | | | | | | | | | (_| | | |_| || |                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|\___|_|  |_| |_| |_|_|_| |_|\__,_|_|\___/|___|                       #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
"""pyTooling.TerminalUI"""
from unittest             import TestCase

from pyTooling.TerminalUI import LineTerminal


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Application(LineTerminal):
	def __init__(self):
		super().__init__()

		LineTerminal.FATAL_EXIT_CODE = 0


class Terminal(TestCase):
	app: Application

	def setUp(self) -> None:
		self.app = Application()
		self.app.Configure(verbose=True, debug=True, quiet=False)

	def test_Version(self) -> None:
		Application.versionCheck((3, 7, 0))

	def test_Write(self) -> None:
		self.app.WriteQuiet("This is a quiet message.")
		self.app.WriteNormal("This is a normal message.")
		self.app.WriteInfo("This is an info message.")
		self.app.WriteVerbose("This is a verbose message.")
		self.app.WriteDebug("This is a debug message.")
		self.app.WriteWarning("This is a warning message.")
		self.app.WriteError("This is an error message.")
		self.app.WriteFatal("This is a fatal message.", immediateExit=False)
