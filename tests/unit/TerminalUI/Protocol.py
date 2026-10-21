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
"""
Unit tests for :data:`pyTooling.TerminalUI.TERMINAL_APPLICATION_PROTOCOL`: the members a mixin-class expects from a
terminal application.
"""
from argparse              import Namespace

from pyTooling.MetaClasses import ExtendedType, UnfulfilledExpectationError
from pyTooling.TerminalUI  import TerminalApplication, TERMINAL_APPLICATION_PROTOCOL
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Handlers(metaclass=ExtendedType, mixin=True, expects=TERMINAL_APPLICATION_PROTOCOL):
	"""A mixin-class with command handlers, like the ``*Handlers`` classes of a command line program."""

	def HandleExample(self, args: Namespace) -> None:
		self.WriteNormal("Example.")


class Protocol(Testcase):
	def test_Members(self) -> None:
		"""Every member of the protocol is a member of :class:`TerminalApplication`."""
		for memberName in TERMINAL_APPLICATION_PROTOCOL:
			with self.subTest(memberName=memberName):
				self.assertHasAttr(TerminalApplication, memberName)

	def test_TerminalApplication(self) -> None:
		class Application(TerminalApplication, Handlers):
			pass

		self.assertEqual((), Application.__missingMembers__)

	def test_NoTerminalApplication(self) -> None:
		class Application(Handlers, metaclass=ExtendedType):
			pass

		with self.assertRaises(UnfulfilledExpectationError):
			Application()
