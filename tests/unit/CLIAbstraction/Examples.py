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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Abstracted CLI programs as examples for unit tests.

:copyright: Copyright 2007-2023 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""

from pyTooling.CLIAbstraction          import CLIArgument, Executable
from pyTooling.CLIAbstraction.ValuedTupleFlag import ShortTupleFlag
from pyTooling.CLIAbstraction.Flag import LongFlag
from pyTooling.CLIAbstraction.Command import CommandArgument

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class GitArguments:
	_executableNames = {
		"Darwin":  "git",
		"Linux":   "git",
		"Windows": "git.exe"
	}

	@CLIArgument()
	class FlagVersion(LongFlag, name="version"): ...

	@CLIArgument()
	class FlagHelp(LongFlag, name="help"): ...

	@CLIArgument()
	class CommandHelp(CommandArgument, name="help"): ...

	@CLIArgument()
	class CommandInit(CommandArgument, name="init"): ...

	@CLIArgument()
	class CommandStage(CommandArgument, name="add"): ...

	@CLIArgument()
	class CommandCommit(CommandArgument, name="commit"): ...

	@CLIArgument()
	class ValueCommitMessage(ShortTupleFlag, name="m"): ...
