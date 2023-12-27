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
pyTooling.Attributes
####################

:copyright: Copyright 2007-2023 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from typing   import Callable, Any
from unittest import TestCase

from pyTooling.Attributes.ArgParse import ArgParseHelperMixin, DefaultHandler, CommandHandler, CommandLineArgument
from pyTooling.Attributes.ArgParse.Argument import StringArgument
from pyTooling.Attributes.ArgParse.Flag import FlagArgument, ShortFlag, LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag import ValuedFlag, ShortValuedFlag, LongValuedFlag
from pyTooling.Attributes.ArgParse.KeyValueFlag import NamedKeyValuePairsArgument, ShortKeyValueFlag, LongKeyValueFlag

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class ProgramBase(ArgParseHelperMixin):
	handler: Callable
	args: Any

	def __init__(self) -> None:
		super().__init__(prog="Program.py")


class Common(TestCase):
	def test_NoArgs(self):
		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = []

		parsed = prog.MainParser.parse_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 0, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback

	def test_DefaultHelpShort(self):
		print()

		class Program(ProgramBase, ArgParseHelperMixin):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = ["-h"]

		with self.assertRaises(SystemExit) as ex:
			parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)

		self.assertEqual(0, ex.exception.code)

	def test_DefaultHelpLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = ["--help"]

		with self.assertRaises(SystemExit) as ex:
			parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)

		self.assertEqual(0, ex.exception.code)

	def test_Help(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("help", help="Display help page(s) for the given command name.")
			@CommandLineArgument(metavar="Command", dest="Command", type=str, nargs="?", help="Print help page(s) for a command.")
			def HandleHelp(self, args) -> None:
				self.handler = self.HandleHelp
				self.args = args

		prog = Program()

		arguments = ["help"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleHelp)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback

	def test_HelpPlusArgWithoutArg(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("help", help="Display help page(s) for the given command name.")
			@CommandLineArgument(metavar="Command", dest="Command", type=str, nargs="?", help="Print help page(s) for a command.")
			def HandleHelp(self, args) -> None:
				self.handler = self.HandleHelp
				self.args = args

		prog = Program()

		arguments = ["help"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleHelp)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.Command)

	def test_HelpPlusArgWithArg(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("help", help="Display help page(s) for the given command name.")
			@CommandLineArgument(metavar="Command", dest="Command", type=str, nargs="?", help="Print help page(s) for a command.")
			def HandleHelp(self, args) -> None:
				self.handler = self.HandleHelp
				self.args = args

		prog = Program()

		arguments = ["help", "info"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleHelp)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("info", prog.args.Command)

	def test_HelpShort(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			# -h and --help causes an ArgumentError: argument -h/--help: conflicting option strings: -h, --help
			# @ArgumentAttribute("-h", "--help", dest="help", action="store_const", const=True, default=False, help="Show help.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = ["-h"]

		with self.assertRaises(SystemExit) as ex:
			parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)

		self.assertEqual(0, ex.exception.code)
		# An internal help page is printed and the parser causes a SystemExit exception
		# self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")

	def test_HelpLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
#     -h and --help causes an ArgumentError: argument -h/--help: conflicting option strings: -h, --help
# 			@ArgumentAttribute("-h", "--help", dest="help", action="store_const", const=True, default=False, help="Show help.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = ["--help"]

		with self.assertRaises(SystemExit) as ex:
			parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)

		self.assertEqual(0, ex.exception.code)
		# An internal help page is printed and the parser causes a SystemExit exception
		# self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")

	def test_VerboseShortWithoutV(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@CommandLineArgument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = []

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_VerboseShortWithV(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@CommandLineArgument("-v", "--verbose", dest="verbose", action="store_const", const=True, default=False, help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		arguments = ["-v"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)


class Values(TestCase):
	def test_String(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@StringArgument(dest="username", metaName="username", help="Name of the user.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["paebbels"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("paebbels", prog.args.username)


class Flags(TestCase):
	def test_DefaultHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-v"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["-V"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

		# Checking long parameter
		arguments = ["--verbose"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["--ver"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_DefaultHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@ShortFlag("-v", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-v"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["-V"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_DefaultHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@LongFlag("--verbose", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["--verbose"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["--ver"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-v"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "-V"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

		# Checking long parameter
		arguments = ["cmd", "--verbose"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "--ver"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@ShortFlag("-v", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-v"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "-V"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@LongFlag("--verbose", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["cmd", "--verbose"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "--ver"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)


class KeyValueFlags(TestCase):
	def test_DefaultHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@NamedKeyValuePairsArgument(short="-c", long="--count", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-c", "1"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["-C", "2"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

		# Checking long parameter
		arguments = ["--count", "3"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["--cnt", "4"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_DefaultHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@ShortKeyValueFlag("-c", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-c", "6"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["-C", "7"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_DefaultHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@LongKeyValueFlag("--count", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["--count", "8"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["--cnt", "9"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@NamedKeyValuePairsArgument(short="-c", long="--count", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-c", "11"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "-C", "12"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

		# Checking long parameter
		arguments = ["cmd", "--count", "13"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "--cnt", "14"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@ShortKeyValueFlag("-c", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-c", "15"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "-C", "16"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)

	def test_CommandHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@LongKeyValueFlag("--count", dest="verbose", help="Show verbose messages.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["cmd", "--count", "17"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(True, prog.args.verbose)

		# Checking wrong parameter
		arguments = ["cmd", "--cnt", "18"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual(False, prog.args.verbose)


class ValuedFlags(TestCase):
	def test_DefaultHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@ValuedFlag(short="-c", long="--count", dest="count", help="Number of elements.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-c=1"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("1", prog.args.count)

		# Checking wrong parameter
		arguments = ["-C=2"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

		# Checking long parameter
		arguments = ["--count=3"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("3", prog.args.count)

		# Checking wrong parameter
		arguments = ["--cnt=4"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

	def test_DefaultHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@ShortValuedFlag("-c", dest="count", help="Number of elements.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["-c=5"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("5", prog.args.count)

		# Checking wrong parameter
		arguments = ["-C=6"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

	def test_DefaultHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@LongValuedFlag("--count", dest="count", help="Number of elements.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["--count=7"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("7", prog.args.count)

		# Checking wrong parameter
		arguments = ["--cnt=8"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments, nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.HandleDefault)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

	def test_CommandHandler_ShortAndLong(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@ValuedFlag(short="-c", long="--count", dest="count", help="Number of elements.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-c=11"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("11", prog.args.count)

		# Checking wrong parameter
		arguments = ["cmd", "-C=12"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

		# Checking long parameter
		arguments = ["cmd", "--count=13"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("13", prog.args.count)

		# Checking wrong parameter
		arguments = ["cmd", "--cnt=14"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

	def test_CommandHandler_Short(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@ShortValuedFlag("-c", dest="count", help="Number of elements.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking short parameter
		arguments = ["cmd", "-c=15"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("15", prog.args.count)

		# Checking wrong parameter
		arguments = ["cmd", "-C=16"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)

	def test_CommandHandler_Long(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("cmd", help="Command")
			@LongValuedFlag("--count", dest="count", help="Number of elements.")
			def CmdHandler(self, args) -> None:
				self.handler = self.CmdHandler
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["cmd", "--count=17"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("17", prog.args.count)

		# Checking wrong parameter
		arguments = ["cmd", "--cnt=18"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(1, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertListEqual(arguments[1:], nonProcessedArgs)
		self.assertIs(prog.handler.__func__, Program.CmdHandler)
		self.assertEqual(1 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertIsNone(prog.args.count)


class UserManager(TestCase):
	def test_UserManager(self):
		print()

		class Program(ProgramBase):
			@DefaultHandler()
			@FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
			def HandleDefault(self, args) -> None:
				self.handler = self.HandleDefault
				self.args = args

			@CommandHandler("new-user", help="Add a new user.")
			@StringArgument(dest="username", metaName="username", help="Name of the new user.")
			@LongValuedFlag("--quota", dest="quota", help="Max usable disk space.")
			def NewUserHandler(self, args) -> None:
				self.handler = self.NewUserHandler
				self.args = args

			@CommandHandler("delete-user", help="Delete a user.")
			# name
			@FlagArgument(short="-f", long="--force", dest="force", help="Ignore internal checks.")
			def DeleteUserHandler(self, args) -> None:
				self.handler = self.DeleteUserHandler
				self.args = args

			@CommandHandler("list-user", help="Add a new user.")
			def ListUserHandler(self, args) -> None:
				self.handler = self.ListUserHandler
				self.args = args

		prog = Program()

		# Checking long parameter
		arguments = ["new-user", "username", "--quota=17"]

		parsed, nonProcessedArgs = prog.MainParser.parse_known_args(arguments)
		prog._RouteToHandler(parsed)

		self.assertEqual(0, len(nonProcessedArgs), f"Remaining options: {nonProcessedArgs}")
		self.assertIs(prog.handler.__func__, Program.NewUserHandler)
		self.assertEqual(3 + 1, len(prog.args.__dict__), f"args: {prog.args.__dict__}")  #: 1+ for 'func' as callback
		self.assertEqual("17", prog.args.quota)
