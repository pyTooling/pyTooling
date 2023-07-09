# =============================================================================
#                  _   _   _        _ _           _
#   _ __  _   _   / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___
#  | '_ \| | | | / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|
#  | |_) | |_| |/ ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \
#  | .__/ \__, /_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/
#  |_|    |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Testing the ArgParse module
#
# License:
# ============================================================================
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
"""
pyAttributes
############

:copyright: Copyright 2007-2023 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from typing import Callable, Any
from unittest     import TestCase

from pyAttributes.ArgParseAttributes import ArgParseMixin, DefaultAttribute, CommandAttribute, ArgumentAttribute, SwitchArgumentAttribute, CommonSwitchArgumentAttribute

from . import CapturePrintContext


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ProgramBase():
	def __init__(self):
		pass


class Program(ProgramBase, ArgParseMixin):
	handler: Callable = None
	args:    Any =      None

	def __init__(self):
		import argparse
		import textwrap

		# call constructor of the main interitance tree
		super().__init__()

		# Call the constructor of the ArgParseMixin
		ArgParseMixin.__init__(
			self,
		  # prog =	self.program,
		  # usage =	"Usage?",			# override usage string
		  description=textwrap.dedent('''\
				This is the test program.
				'''),
		  epilog=textwrap.fill("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam."),
		  formatter_class=argparse.RawDescriptionHelpFormatter,
		  add_help=False
		)


	@CommonSwitchArgumentAttribute("-q", "--quiet",   dest="quiet",   help="Reduce messages to a minimum.")
	@CommonSwitchArgumentAttribute("-v", "--verbose", dest="verbose", help="Print out detailed messages.")
	@CommonSwitchArgumentAttribute("-d", "--debug",   dest="debug",   help="Enable debug mode.")
	def Run(self, testVector) -> None:
		ArgParseMixin.Run(self)


	@DefaultAttribute()
	def HandleDefault(self, args) -> None:
		self.handler = self.HandleDefault
		self.args =    args


	@CommandAttribute("help", help="Display help page(s) for the given command name.")
	@ArgumentAttribute(metavar="Command", dest="Command", type=str, nargs="?", help="Print help page(s) for a command.")
	def HandleHelp(self, args) -> None:
		self.handler = self.HandleHelp
		self.args =    args


	@CommandAttribute("new-user", help="Create a new user.")
	@ArgumentAttribute(metavar='<UserID>', dest="UserID", type=int, help="UserID - unique identifier")
	@ArgumentAttribute(metavar='<Name>', dest="Name", type=str, help="The user's display name.")
	def HandleNewUser(self, args) -> None:
		self.handler = self.HandleNewUser
		self.args =    args


	@CommandAttribute("delete-user", help="Delete a user.")
	@ArgumentAttribute(metavar='<UserID>', dest="UserID", type=str, help="UserID - unique identifier")
	def HandleDeleteUser(self, args) -> None:
		self.handler = self.HandleDeleteUser
		self.args =    args


	@CommandAttribute("list-user", help="List users.")
	@SwitchArgumentAttribute('--all', dest="all", help='List all users.')
	def HandleListUser(self, args) -> None:
		self.handler = self.HandleListUser
		self.args =    args


class Test(TestCase):
	prog: Program

	def setUp(self) -> None:
		self.prog = Program()

	def test_DefaultAttribute_NoArguments(self) -> None:
		arguments = []

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleDefault)
		self.assertFalse(self.prog.args.quiet)
		self.assertFalse(self.prog.args.verbose)
		self.assertFalse(self.prog.args.debug)

	def test_HelpCommand_NoArguments(self) -> None:
		arguments = ["help"]

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleHelp)
		self.assertFalse(self.prog.args.quiet)
		self.assertFalse(self.prog.args.verbose)
		self.assertFalse(self.prog.args.debug)

	def test_HelpCommand_ShortQuiet(self) -> None:
		arguments = ["-q", "help"]

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleHelp)
		self.assertTrue(self.prog.args.quiet)
		self.assertFalse(self.prog.args.verbose)
		self.assertFalse(self.prog.args.debug)

	def test_HelpCommand_ShortVerbose(self) -> None:
		arguments = ["-v", "help"]

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleHelp)
		self.assertFalse(self.prog.args.quiet)
		self.assertTrue(self.prog.args.verbose)
		self.assertFalse(self.prog.args.debug)

	def test_HelpCommand_ShortDebug(self) -> None:
		arguments = ["-d", "help"]

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleHelp)
		self.assertFalse(self.prog.args.quiet)
		self.assertFalse(self.prog.args.verbose)
		self.assertTrue(self.prog.args.debug)

	def test_NewUserCommand_NoArguments(self) -> None:
		arguments = ["new-user"]

		with CapturePrintContext() as (_, ErrorCapture):
			with self.assertRaises(SystemExit) as ExceptionCapture:
				_ = self.prog.MainParser.parse_args(arguments)

			self.assertEqual(2, ExceptionCapture.exception.code)

		#output = OutputCapture.getvalue().strip()
		error = ErrorCapture.getvalue().strip()
		self.assertTrue("the following arguments are required: <UserID>, <Name>" in error)

	def test_NewUserCommand_UserID(self) -> None:
		arguments = ["new-user", "25", "argparse"]

		parsed = self.prog.MainParser.parse_args(arguments)
		self.prog._RouteToHandler(parsed)

		self.assertIs(self.prog.handler.__func__, Program.HandleNewUser)
		self.assertFalse(self.prog.args.quiet)
		self.assertFalse(self.prog.args.verbose)
		self.assertFalse(self.prog.args.debug)
		self.assertEqual(self.prog.args.UserID, 25)
		self.assertEqual(self.prog.args.Name, "argparse")
