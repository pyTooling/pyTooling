# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
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
Unit tests for :class:`pyTooling.Common.StringEnum`.
"""
from pyTooling.Common  import StringEnum
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Format(StringEnum):
	"""An enumeration declaring which member stands for 'nothing was given'."""

	PNG = "png"
	SVG = "svg"

	Default = PNG


class Level(StringEnum):
	"""An enumeration without a default, because the field it reads may legitimately be absent."""

	Low =  "low"
	High = "high"


class Members(Testcase):
	def test_ItIsAString(self) -> None:
		"""A member is its value, so it needs no unwrapping to be written."""
		self.assertEqual("png", f"{Format.PNG}")
		self.assertEqual("png, svg", ", ".join(Format))

	def test_Default(self) -> None:
		self.assertIs(Format.PNG, Format.Default)

	def test_Default_IsAnAlias(self) -> None:
		"""The default is an alias, so it is neither iterated nor a second member to compare against."""
		self.assertEqual(["PNG", "SVG"], [member.name for member in Format])
		self.assertIn("Default", Format.__members__)


class Parse(Testcase):
	def test_Value(self) -> None:
		self.assertIs(Format.SVG, Format.Parse("svg"))

	def test_NoValue(self) -> None:
		"""Nothing given is the declared default."""
		self.assertIs(Format.PNG, Format.Parse(None))
		self.assertIs(Format.PNG, Format.Parse(""))

	def test_NoValue_NoDefault(self) -> None:
		"""An enumeration declaring no default answers None, for a field that may be absent."""
		self.assertIsNone(Level.Parse(None))
		self.assertIsNone(Level.Parse(""))

	def test_UnknownValue(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Format.Parse("gif")

		self.assertEqual("'gif' is not a valid Format.", str(context.exception))
		self.assertIn("Allowed values: png, svg.", context.exception.__notes__)

	def test_WrongType(self) -> None:
		"""A value that isn't a string is a TypeError, and the note reports what was given."""
		with self.assertRaises(TypeError) as context:
			_ = Format.Parse(5)

		self.assertEqual("Parameter 'value' is not of type 'str'.", str(context.exception))
		self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_WrongType_Enumeration(self) -> None:
		"""A member of another enumeration is not a value of this one, however it prints."""
		with self.assertRaises(ValueError) as context:
			_ = Format.Parse(Level.Low)

		self.assertEqual("'low' is not a valid Format.", str(context.exception))
