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
"""Testcases for arguments without a prefix."""
from pathlib import Path
from unittest import TestCase

from pyTooling.CLIAbstraction.Argument import StringArgument, DelimiterArgument, CommandLineArgument, NamedArgument, \
	ValuedArgument, NamedAndValuedArgument, PathArgument, StringListArgument, PathListArgument, ExecutableArgument, \
	NamedTupledArgument
from pyTooling.CLIAbstraction.BooleanFlag import BooleanFlag, ShortBooleanFlag, LongBooleanFlag, WindowsBooleanFlag
from pyTooling.CLIAbstraction.Command import CommandArgument, ShortCommand, WindowsCommand, LongCommand
from pyTooling.CLIAbstraction.Flag import FlagArgument, ShortFlag, WindowsFlag, LongFlag
from pyTooling.CLIAbstraction.KeyValueFlag import NamedKeyValuePairsArgument, ShortKeyValueFlag, LongKeyValueFlag, \
	WindowsKeyValueFlag
from pyTooling.CLIAbstraction.OptionalValuedFlag import OptionalValuedFlag, ShortOptionalValuedFlag, \
	WindowsOptionalValuedFlag, LongOptionalValuedFlag
from pyTooling.CLIAbstraction.ValuedFlag import ShortValuedFlag, WindowsValuedFlag, LongValuedFlag, ValuedFlag
from pyTooling.CLIAbstraction.ValuedFlagList import ShortValuedFlagList, ValuedFlagList, WindowsValuedFlagList, \
	LongValuedFlagList
from pyTooling.CLIAbstraction.ValuedTupleFlag import ShortTupleFlag, WindowsTupleFlag, LongTupleFlag

if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class WithoutPrefix(TestCase):
	def test_CommandLineArgument(self):
		with self.assertRaises(TypeError):
			_ = CommandLineArgument()

	def test_ExecutableArgument(self):
		with self.assertRaises(TypeError):
			_ = ExecutableArgument("program.exe")

		executablePath = Path("program.exe")
		argument = ExecutableArgument(executablePath)

		self.assertIs(executablePath, argument.Executable)
		self.assertEqual(f"{executablePath}", argument.AsArgument())
		self.assertEqual(f"\"{executablePath}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(TypeError):
			argument.Executable = "script.sh"

		executablePath2 = Path("script.sh")
		argument.Executable = executablePath2
		self.assertIs(executablePath2, argument.Executable)


	def test_DelimiterArgument(self):
		pattern = "--"
		argument = DelimiterArgument()

		self.assertEqual(f"{pattern}", argument.AsArgument())
		self.assertEqual(f"\"{pattern}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

	def test_DerivedDelimiterArgument(self):
		pattern = "++"

		class Delimiter(DelimiterArgument, pattern=pattern):
			pass

		argument = Delimiter()

		self.assertEqual(f"{pattern}", argument.AsArgument())
		self.assertEqual(f"\"{pattern}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

	def test_AbstractCommandArgument(self):
		with self.assertRaises(TypeError):
			_ = CommandArgument()

	def test_CommandArgument(self):
		name = "command"

		class Command(CommandArgument, name=name):
			pass

		argument = Command()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"{name}", argument.AsArgument())
		self.assertEqual(f"\"{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_NamedArgument(self):
		with self.assertRaises(TypeError):
			_ = NamedArgument()

	def test_DerivedNamedArgument(self):
		name = "command"

		class Command(CommandArgument, name=name):
			pass

		argument = Command()
		self.assertIs(name, argument.Name)
		self.assertEqual(f"{name}", argument.AsArgument())
		self.assertEqual(f"\"{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))


		with self.assertRaises(AttributeError):
			argument.Name = "command2"

	def test_ValuedArgument(self):
		value = "value"
		argument = ValuedArgument(value)

		self.assertIs(value, argument.Value)
		self.assertEqual(f"{value}", argument.AsArgument())
		self.assertEqual(f"\"{value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

	def test_NamedAndValuedArgument(self):
		with self.assertRaises(TypeError):
			_ = NamedAndValuedArgument()

	def test_DerivedNamedAndValuedArgument(self):
		name = "flag"
		value = "value"

		class Flag(NamedAndValuedArgument, name=name):
			pass

		argument = Flag(value)
		self.assertIs(name, argument.Name)
		self.assertEqual(f"{name}={value}", argument.AsArgument())
		self.assertEqual(f"\"{name}={value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_StringArgument(self):
		value = "value"
		argument = StringArgument(value)

		self.assertIs(value, argument.Value)
		self.assertEqual(f"{value}", argument.AsArgument())
		self.assertEqual(f"\"{value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "value2"
		argument.Value = value2
		self.assertIs(value2, argument.Value)

	def test_StringListArgument(self):
		values = ("value1", "value2")
		argument = StringListArgument(values)

		self.assertListEqual(list(values), argument.Value)
		self.assertEqual([f"{value}" for value in values], argument.AsArgument())
		self.assertEqual(f"\"{values[0]}\" \"{values[1]}\"", str(argument))
		self.assertEqual(f"\"{values[0]}\", \"{values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, "bar")

		values2 = ("631", "527")

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"{value}" for value in values2], argument.AsArgument())
		self.assertEqual(f"\"{values2[0]}\" \"{values2[1]}\"", str(argument))
		self.assertEqual(f"\"{values2[0]}\", \"{values2[1]}\"", repr(argument))

	def test_PathArgument(self):
		path = Path("file1.txt")
		argument = PathArgument(path)

		self.assertIs(path, argument.Value)
		self.assertEqual(f"{path}", argument.AsArgument())
		self.assertEqual(f"\"{path}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		path2 = Path("file2.txt")
		argument.Value = path2
		self.assertIs(path2, argument.Value)

	def test_PathListArgument(self):
		values = (Path("file1.txt"), Path("file2.txt"))
		argument = PathListArgument(values)

		self.assertListEqual(list(values), argument.Value)
		self.assertEqual([f"{value}" for value in values], argument.AsArgument())
		self.assertEqual(f"\"{values[0]}\" \"{values[1]}\"", str(argument))
		self.assertEqual(f"\"{values[0]}\", \"{values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, Path("file3.txt"))

		values2 = (Path("file1.log"), Path("file2.log"))

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"{value}" for value in values2], argument.AsArgument())
		self.assertEqual(f"\"{values2[0]}\" \"{values2[1]}\"", str(argument))
		self.assertEqual(f"\"{values2[0]}\", \"{values2[1]}\"", repr(argument))


class Commands(TestCase):
	def test_ShortCommand(self):
		with self.assertRaises(TypeError):
			_ = ShortCommand()

	def test_DerivedShortCommand(self):
		name = "command"

		class Command(ShortCommand, name=name):
			pass

		argument = Command()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"-{name}", argument.AsArgument())
		self.assertEqual(f"\"-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "command2"

	def test_LongCommand(self):
		with self.assertRaises(TypeError):
			_ = LongCommand()

	def test_DerivedLongCommand(self):
		name = "command"

		class Command(LongCommand, name=name):
			pass

		argument = Command()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"--{name}", argument.AsArgument())
		self.assertEqual(f"\"--{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "command2"

	def test_WindowsCommand(self):
		with self.assertRaises(TypeError):
			_ = WindowsCommand()

	def test_DerivedWindowsCommand(self):
		name = "command"

		class Command(WindowsCommand, name=name):
			pass

		argument = Command()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"/{name}", argument.AsArgument())
		self.assertEqual(f"\"/{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "command2"


class Flags(TestCase):
	def test_FlagArgument(self):
		with self.assertRaises(TypeError):
			_ = FlagArgument()

	def test_DerivedFlagArgument(self):
		name = "flag"

		class Flag(FlagArgument, name=name):
			pass

		argument = Flag()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"{name}", argument.AsArgument())
		self.assertEqual(f"\"{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = ShortFlag()

	def test_DerivedShortFlagArgument(self):
		name = "flag"

		class Flag(ShortFlag, name=name):
			pass

		argument = Flag()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"-{name}", argument.AsArgument())
		self.assertEqual(f"\"-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = LongFlag()

	def test_DerivedLongFlagArgument(self):
		name = "flag"

		class Flag(LongFlag, name=name):
			pass

		argument = Flag()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"--{name}", argument.AsArgument())
		self.assertEqual(f"\"--{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_WindowsFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = WindowsFlag()

	def test_DerivedWindowsFlagArgument(self):
		name = "flag"

		class Flag(WindowsFlag, name=name):
			pass

		argument = Flag()

		self.assertIs(name, argument.Name)
		self.assertEqual(f"/{name}", argument.AsArgument())
		self.assertEqual(f"\"/{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class BooleanFlags(TestCase):
	def test_BooleanFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = BooleanFlag()

	def test_DerivedBooleanFlagArgument(self):
		name = "flag"

		class Flag(BooleanFlag, name=name):
			pass

		argument = Flag(True)

		self.assertIs(name, argument.Name)
		self.assertTrue(argument.Value)
		self.assertEqual(f"with-{name}", argument.AsArgument())
		self.assertEqual(f"\"with-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		argument.Value = False
		self.assertFalse(argument.Value)
		self.assertEqual(f"without-{name}", argument.AsArgument())
		self.assertEqual(f"\"without-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortBooleanFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = ShortBooleanFlag()

	def test_DerivedShortBooleanFlagArgument(self):
		name = "flag"

		class Flag(ShortBooleanFlag, name=name):
			pass

		argument = Flag(True)

		self.assertIs(name, argument.Name)
		self.assertTrue(argument.Value)
		self.assertEqual(f"-with-{name}", argument.AsArgument())
		self.assertEqual(f"\"-with-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		argument.Value = False
		self.assertFalse(argument.Value)
		self.assertEqual(f"-without-{name}", argument.AsArgument())
		self.assertEqual(f"\"-without-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongBooleanFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = LongBooleanFlag()

	def test_DerivedLongBooleanFlagArgument(self):
		name = "flag"

		class Flag(LongBooleanFlag, name=name):
			pass

		argument = Flag(True)

		self.assertIs(name, argument.Name)
		self.assertTrue(argument.Value)
		self.assertEqual(f"--with-{name}", argument.AsArgument())
		self.assertEqual(f"\"--with-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		argument.Value = False
		self.assertFalse(argument.Value)
		self.assertEqual(f"--without-{name}", argument.AsArgument())
		self.assertEqual(f"\"--without-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_WindowsBooleanFlagArgument(self):
		with self.assertRaises(TypeError):
			_ = WindowsBooleanFlag()

	def test_DerivedWindowsBooleanFlagArgument(self):
		name = "flag"

		class Flag(WindowsBooleanFlag, name=name):
			pass

		argument = Flag(True)

		self.assertIs(name, argument.Name)
		self.assertTrue(argument.Value)
		self.assertEqual(f"/with-{name}", argument.AsArgument())
		self.assertEqual(f"\"/with-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		argument.Value = False
		self.assertFalse(argument.Value)
		self.assertEqual(f"/without-{name}", argument.AsArgument())
		self.assertEqual(f"\"/without-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class OptionalValuedFlags(TestCase):
	def test_OptionalValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = OptionalValuedFlag()

	def test_DerivedOptionalValuedFlag(self):
		name = "flag"
		value = None

		class Flag(OptionalValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIsNone(argument.Value)
		self.assertEqual(f"{name}", argument.AsArgument())
		self.assertEqual(f"\"{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "42"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortOptionalValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = ShortOptionalValuedFlag()

	def test_DerivedShortOptionalValuedFlag(self):
		name = "flag"
		value = None

		class Flag(ShortOptionalValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIsNone(argument.Value)
		self.assertEqual(f"-{name}", argument.AsArgument())
		self.assertEqual(f"\"-{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "42"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"-{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"-{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongOptionalValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = LongOptionalValuedFlag()

	def test_DerivedLongOptionalValuedFlag(self):
		name = "flag"
		value = None

		class Flag(LongOptionalValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIsNone(argument.Value)
		self.assertEqual(f"--{name}", argument.AsArgument())
		self.assertEqual(f"\"--{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "42"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"--{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"--{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_WindowsOptionalValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = WindowsOptionalValuedFlag()

	def test_DerivedWindowsOptionalValuedFlag(self):
		name = "flag"
		value = None

		class Flag(WindowsOptionalValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIsNone(argument.Value)
		self.assertEqual(f"/{name}", argument.AsArgument())
		self.assertEqual(f"\"/{name}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "42"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"/{name}:{value2}", argument.AsArgument())
		self.assertEqual(f"\"/{name}:{value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class ValuedFlags(TestCase):
	def test_ValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = ValuedFlag()

	def test_DerivedValuedFlag(self):
		name = "flag"
		value = "42"

		class Flag(ValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIs(value, argument.Value)
		self.assertEqual(f"{name}={value}", argument.AsArgument())
		self.assertEqual(f"\"{name}={value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "84"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = ShortValuedFlag()

	def test_DerivedShortValuedFlag(self):
		name = "flag"
		value = "42"

		class Flag(ShortValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIs(value, argument.Value)
		self.assertEqual(f"-{name}={value}", argument.AsArgument())
		self.assertEqual(f"\"-{name}={value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "84"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"-{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"-{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = LongValuedFlag()

	def test_DerivedLongValuedFlag(self):
		name = "flag"
		value = "42"

		class Flag(LongValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIs(value, argument.Value)
		self.assertEqual(f"--{name}={value}", argument.AsArgument())
		self.assertEqual(f"\"--{name}={value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "84"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"--{name}={value2}", argument.AsArgument())
		self.assertEqual(f"\"--{name}={value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_WindowsValuedFlag(self):
		with self.assertRaises(TypeError):
			_ = WindowsValuedFlag()

	def test_DerivedWindowsValuedFlag(self):
		name = "flag"
		value = "42"

		class Flag(WindowsValuedFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertIs(value, argument.Value)
		self.assertEqual(f"/{name}:{value}", argument.AsArgument())
		self.assertEqual(f"\"/{name}:{value}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		value2 = "84"

		argument.Value = value2
		self.assertIs(value2, argument.Value)
		self.assertEqual(f"/{name}:{value2}", argument.AsArgument())
		self.assertEqual(f"\"/{name}:{value2}\"", str(argument))
		self.assertEqual(str(argument), repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class ValuedFlagLists(TestCase):
	def test_ValuedFlagList(self):
		with self.assertRaises(TypeError):
			_ = ValuedFlagList()

	def test_DerivedValuedFlagList(self):
		name = "flag"
		values = ("42", "84")

		class Flag(ValuedFlagList, name=name):
			pass

		argument = Flag(values)

		self.assertIs(name, argument.Name)
		self.assertListEqual(list(values), argument.Value)
		self.assertListEqual([f"{name}={val}" for val in values], argument.AsArgument())
		self.assertEqual(f"\"{name}={values[0]}\" \"{name}={values[1]}\"", str(argument))
		self.assertEqual(f"\"{name}={values[0]}\", \"{name}={values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, "bar")

		values2 = ("631", "527")

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"{name}={val}" for val in values2], argument.AsArgument())
		self.assertEqual(f"\"{name}={values2[0]}\" \"{name}={values2[1]}\"", str(argument))
		self.assertEqual(f"\"{name}={values2[0]}\", \"{name}={values2[1]}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortValuedFlagList(self):
		with self.assertRaises(TypeError):
			_ = ShortValuedFlagList()

	def test_DerivedShortValuedFlagList(self):
		name = "flag"
		values = ("42", "84")

		class Flag(ShortValuedFlagList, name=name):
			pass

		argument = Flag(values)

		self.assertIs(name, argument.Name)
		self.assertListEqual(list(values), argument.Value)
		self.assertListEqual([f"-{name}={val}" for val in values], argument.AsArgument())
		self.assertEqual(f"\"-{name}={values[0]}\" \"-{name}={values[1]}\"", str(argument))
		self.assertEqual(f"\"-{name}={values[0]}\", \"-{name}={values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, "bar")

		values2 = ("631", "527")

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"-{name}={val}" for val in values2], argument.AsArgument())
		self.assertEqual(f"\"-{name}={values2[0]}\" \"-{name}={values2[1]}\"", str(argument))
		self.assertEqual(f"\"-{name}={values2[0]}\", \"-{name}={values2[1]}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongValuedFlagList(self):
		with self.assertRaises(TypeError):
			_ = LongValuedFlagList()

	def test_DerivedLongValuedFlagList(self):
		name = "flag"
		values = ("42", "84")

		class Flag(LongValuedFlagList, name=name):
			pass

		argument = Flag(values)

		self.assertIs(name, argument.Name)
		self.assertListEqual(list(values), argument.Value)
		self.assertListEqual([f"--{name}={val}" for val in values], argument.AsArgument())
		self.assertEqual(f"\"--{name}={values[0]}\" \"--{name}={values[1]}\"", str(argument))
		self.assertEqual(f"\"--{name}={values[0]}\", \"--{name}={values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, "bar")

		values2 = ("631", "527")

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"--{name}={val}" for val in values2], argument.AsArgument())
		self.assertEqual(f"\"--{name}={values2[0]}\" \"--{name}={values2[1]}\"", str(argument))
		self.assertEqual(f"\"--{name}={values2[0]}\", \"--{name}={values2[1]}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


	def test_WindowsValuedFlagList(self):
		with self.assertRaises(TypeError):
			_ = WindowsValuedFlagList()

	def test_DerivedWindowsValuedFlagList(self):
		name = "flag"
		values = ("42", "84")

		class Flag(WindowsValuedFlagList, name=name):
			pass

		argument = Flag(values)

		self.assertIs(name, argument.Name)
		self.assertListEqual(list(values), argument.Value)
		self.assertListEqual([f"/{name}:{val}" for val in values], argument.AsArgument())
		self.assertEqual(f"\"/{name}:{values[0]}\" \"/{name}:{values[1]}\"", str(argument))
		self.assertEqual(f"\"/{name}:{values[0]}\", \"/{name}:{values[1]}\"", repr(argument))

		with self.assertRaises(TypeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = (42, "bar")

		values2 = ("631", "527")

		argument.Value = values2
		self.assertListEqual(list(values2), argument.Value)
		self.assertListEqual([f"/{name}:{val}" for val in values2], argument.AsArgument())
		self.assertEqual(f"\"/{name}:{values2[0]}\" \"/{name}:{values2[1]}\"", str(argument))
		self.assertEqual(f"\"/{name}:{values2[0]}\", \"/{name}:{values2[1]}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class ValuedTupleFlags(TestCase):
	def test_ValuedTupleArgument(self):
		with self.assertRaises(TypeError):
			_ = NamedTupledArgument()

	def test_DerivedValuedTupleArgument(self):
		name = "flag"
		value = "42"

		class Flag(NamedTupledArgument, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertEqual(value, argument.Value)
		self.assertListEqual([f"{name}", f"{value}"], list(argument.AsArgument()))
		self.assertEqual(f"\"{name}\" \"{value}\"", str(argument))
		self.assertEqual(f"\"{name}\", \"{value}\"", repr(argument))

		# with self.assertRaises(TypeError):
		# 	argument.Value = 42

		value2 = "84"

		argument.Value = value2
		self.assertEqual(value2, argument.Value)
		self.assertListEqual([f"{name}", f"{value2}"], list(argument.AsArgument()))
		self.assertEqual(f"\"{name}\" \"{value2}\"", str(argument))
		self.assertEqual(f"\"{name}\", \"{value2}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_ShortTupleFlag(self):
		with self.assertRaises(TypeError):
			_ = ShortTupleFlag()

	def test_DerivedShortTupleFlag(self):
		name = "flag"
		value = "42"

		class Flag(ShortTupleFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertEqual(value, argument.Value)
		self.assertListEqual([f"-{name}", f"{value}"], list(argument.AsArgument()))
		self.assertEqual(f"\"-{name}\" \"{value}\"", str(argument))
		self.assertEqual(f"\"-{name}\", \"{value}\"", repr(argument))

		# with self.assertRaises(TypeError):
		# 	argument.Value = 42

		value2 = "84"

		argument.Value = value2
		self.assertEqual(value2, argument.Value)
		self.assertListEqual([f"-{name}", f"{value2}"], list(argument.AsArgument()))
		self.assertEqual(f"\"-{name}\" \"{value2}\"", str(argument))
		self.assertEqual(f"\"-{name}\", \"{value2}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"

	def test_LongTupleFlag(self):
		with self.assertRaises(TypeError):
			_ = LongTupleFlag()

	def test_DerivedLongTupleFlag(self):
		name = "flag"
		value = "42"

		class Flag(LongTupleFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertEqual(value, argument.Value)
		self.assertListEqual([f"--{name}", f"{value}"], list(argument.AsArgument()))
		self.assertEqual(f"\"--{name}\" \"{value}\"", str(argument))
		self.assertEqual(f"\"--{name}\", \"{value}\"", repr(argument))

		# with self.assertRaises(TypeError):
		# 	argument.Value = 42

		value2 = "84"

		argument.Value = value2
		self.assertEqual(value2, argument.Value)
		self.assertListEqual([f"--{name}", f"{value2}"], list(argument.AsArgument()))
		self.assertEqual(f"\"--{name}\" \"{value2}\"", str(argument))
		self.assertEqual(f"\"--{name}\", \"{value2}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


	def test_WindowsTupleFlag(self):
		with self.assertRaises(TypeError):
			_ = WindowsTupleFlag()

	def test_DerivedWindowsTupleFlag(self):
		name = "flag"
		value = "42"

		class Flag(WindowsTupleFlag, name=name):
			pass

		argument = Flag(value)

		self.assertIs(name, argument.Name)
		self.assertEqual(value, argument.Value)
		self.assertListEqual([f"/{name}", f"{value}"], list(argument.AsArgument()))
		self.assertEqual(f"\"/{name}\" \"{value}\"", str(argument))
		self.assertEqual(f"\"/{name}\", \"{value}\"", repr(argument))

		# with self.assertRaises(TypeError):
		# 	argument.Value = 42

		value2 = "84"

		argument.Value = value2
		self.assertEqual(value2, argument.Value)
		self.assertListEqual([f"/{name}", f"{value2}"], list(argument.AsArgument()))
		self.assertEqual(f"\"/{name}\" \"{value2}\"", str(argument))
		self.assertEqual(f"\"/{name}\", \"{value2}\"", repr(argument))

		with self.assertRaises(AttributeError):
			argument.Name = "flag2"


class KeyValueFlags(TestCase):
	def test_KeyValueFlag(self):
		with self.assertRaises(TypeError):
			_ = NamedKeyValuePairsArgument()

	def test_DerivedNamedKeyValuePairsArgument(self):
		name = "g"
		pairs = {"key1": "value1", "key2": "value2"}

		class Flag(NamedKeyValuePairsArgument, name=name):
			pass

		argument = Flag(pairs)

		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs, argument.Value)
		self.assertListEqual([f"{name}{key}={value}" for key, value in pairs.items()], list(argument.AsArgument()))

		# TODO: should property Value check for a dictionary type and raise a TypeError?
		with self.assertRaises(AttributeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = {42: "value42"}

		with self.assertRaises(TypeError):
			argument.Value = {"key84": 84}

		pairs2 = {"key3": "value3", "key4": "value4"}

		argument.Value = pairs2
		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs2, argument.Value)
		self.assertListEqual([f"{name}{key}={value}" for key, value in pairs2.items()], list(argument.AsArgument()))

		with self.assertRaises(AttributeError):
			argument.Name = "G"

	def test_ShortKeyValueFlag(self):
		with self.assertRaises(TypeError):
			_ = ShortKeyValueFlag()

	def test_DerivedShortKeyValueFlag(self):
		name = "g"
		pairs = {"key1": "value1", "key2": "value2"}

		class Flag(ShortKeyValueFlag, name=name):
			pass

		argument = Flag(pairs)

		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs, argument.Value)
		self.assertListEqual([f"-{name}{key}={value}" for key, value in pairs.items()], list(argument.AsArgument()))

		# TODO: should property Value check for a dictionary type and raise a TypeError?
		with self.assertRaises(AttributeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = {42: "value42"}

		with self.assertRaises(TypeError):
			argument.Value = {"key84": 84}

		pairs2 = {"key3": "value3", "key4": "value4"}

		argument.Value = pairs2
		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs2, argument.Value)
		self.assertListEqual([f"-{name}{key}={value}" for key, value in pairs2.items()], list(argument.AsArgument()))

		with self.assertRaises(AttributeError):
			argument.Name = "G"

	def test_LongKeyValueFlag(self):
		with self.assertRaises(TypeError):
			_ = LongKeyValueFlag()

	def test_DerivedLongKeyValueFlag(self):
		name = "g"
		pairs = {"key1": "value1", "key2": "value2"}

		class Flag(LongKeyValueFlag, name=name):
			pass

		argument = Flag(pairs)

		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs, argument.Value)
		self.assertListEqual([f"--{name}{key}={value}" for key, value in pairs.items()], list(argument.AsArgument()))

		# TODO: should property Value check for a dictionary type and raise a TypeError?
		with self.assertRaises(AttributeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = {42: "value42"}

		with self.assertRaises(TypeError):
			argument.Value = {"key84": 84}

		pairs2 = {"key3": "value3", "key4": "value4"}

		argument.Value = pairs2
		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs2, argument.Value)
		self.assertListEqual([f"--{name}{key}={value}" for key, value in pairs2.items()], list(argument.AsArgument()))

		with self.assertRaises(AttributeError):
			argument.Name = "G"

	def test_WindowsKeyValueFlag(self):
		with self.assertRaises(TypeError):
			_ = WindowsKeyValueFlag()

	def test_DerivedWindowsKeyValueFlag(self):
		name = "g"
		pairs = {"key1": "value1", "key2": "value2"}

		class Flag(WindowsKeyValueFlag, name=name):
			pass

		argument = Flag(pairs)

		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs, argument.Value)
		self.assertListEqual([f"/{name}:{key}={value}" for key, value in pairs.items()], list(argument.AsArgument()))

		# TODO: should property Value check for a dictionary type and raise a TypeError?
		with self.assertRaises(AttributeError):
			argument.Value = 42

		with self.assertRaises(TypeError):
			argument.Value = {42: "value42"}

		with self.assertRaises(TypeError):
			argument.Value = {"key84": 84}

		pairs2 = {"key3": "value3", "key4": "value4"}

		argument.Value = pairs2
		self.assertIs(name, argument.Name)
		self.assertDictEqual(pairs2, argument.Value)
		self.assertListEqual([f"/{name}:{key}={value}" for key, value in pairs2.items()], list(argument.AsArgument()))

		with self.assertRaises(AttributeError):
			argument.Name = "G"
