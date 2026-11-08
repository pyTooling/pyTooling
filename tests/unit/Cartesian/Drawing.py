# ==================================================================================================================== #
#             _____           _ _               ____           _            _             ____  ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ \|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  __) | | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |/ __/| |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|_____|____/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Unit tests for :mod:`pyTooling.Cartesian2D.Drawing` - colors, strokes, fills and fonts.
"""
from pyTooling.Cartesian2D.Drawing import LineStyle, Color, RGBAColor, Stroke, Fill, Font
from pyTooling.MetaClasses         import AbstractClassError
from pyTooling.Testing             import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class GrayColor(Color):
	"""A color of another color system: a gray level from 0 to 255."""

	_level: int  #: Gray level, 0 to 255.

	def __init__(self, level: int) -> None:
		super().__init__()

		self._level = level

	def ToRGBA(self) -> RGBAColor:
		return RGBAColor(self._level, self._level, self._level)


class Colors(Testcase):
	def test_Color(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Color()

		self.assertEqual(
			"Class 'Color' is abstract. The following methods: 'ToRGBA' need to be overridden in a derived class.",
			str(context.exception)
		)

	def test_Color_Derived(self) -> None:
		color = GrayColor(128)

		self.assertIsInstance(color, Color)
		self.assertEqual(RGBAColor(128, 128, 128), color.ToRGBA())

	def test_RGBAColor(self) -> None:
		color = RGBAColor(255, 128, 0)

		self.assertEqual(255, color.Red)
		self.assertEqual(128, color.Green)
		self.assertEqual(0, color.Blue)
		self.assertEqual(1.0, color.Alpha)
		self.assertIsInstance(color, Color)

	def test_RGBAColor_ToRGBA(self) -> None:
		color = RGBAColor(255, 128, 0)

		self.assertIs(color, color.ToRGBA())

	def test_RGBAColor_Alpha(self) -> None:
		color = RGBAColor(0, 0, 0, 0.25)

		self.assertEqual(0.25, color.Alpha)

	def test_RGBAColor_Transparent(self) -> None:
		color = RGBAColor(0, 0, 0, 0)

		self.assertEqual(0, color.Alpha)

	def test_RGBAColor_RedNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor(None, 0, 0)

		self.assertEqual("Parameter 'red' is None.", str(context.exception))

	def test_RGBAColor_GreenFloat(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor(0, 0.5, 0)

		self.assertEqual("Parameter 'green' is not of type 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'float'."], context.exception.__notes__)

	def test_RGBAColor_BlueRange(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor(0, 0, 256)

		self.assertEqual("Parameter 'blue' is out of range 0..255.", str(context.exception))
		self.assertListEqual(["Got value '256'."], context.exception.__notes__)

	def test_RGBAColor_RedNegative(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor(-1, 0, 0)

		self.assertEqual("Parameter 'red' is out of range 0..255.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)

	def test_RGBAColor_AlphaNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor(0, 0, 0, None)

		self.assertEqual("Parameter 'alpha' is None.", str(context.exception))

	def test_RGBAColor_AlphaStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor(0, 0, 0, "0.5")

		self.assertEqual("Parameter 'alpha' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_RGBAColor_AlphaRange(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor(0, 0, 0, 1.5)

		self.assertEqual("Parameter 'alpha' is out of range 0.0..1.0.", str(context.exception))
		self.assertListEqual(["Got value '1.5'."], context.exception.__notes__)


class ColorParsing(Testcase):
	def test_RGB(self) -> None:
		color = RGBAColor.Parse("#ff8000")

		self.assertEqual(RGBAColor(255, 128, 0), color)

	def test_RGB_UpperCase(self) -> None:
		color = RGBAColor.Parse("#FF8000")

		self.assertEqual(RGBAColor(255, 128, 0), color)

	def test_RGBA(self) -> None:
		color = RGBAColor.Parse("#ff800000")

		self.assertEqual(RGBAColor(255, 128, 0, 0.0), color)

	def test_RGBA_Opaque(self) -> None:
		color = RGBAColor.Parse("#ff8000ff")

		self.assertEqual(1.0, color.Alpha)

	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor.Parse(None)

		self.assertEqual("Parameter 'value' is None.", str(context.exception))

	def test_int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor.Parse(0xff8000)

		self.assertEqual("Parameter 'value' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_NoHash(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor.Parse("ff8000a")

		self.assertEqual("Parameter 'value' is not of the form '#rrggbb' or '#rrggbbaa'.", str(context.exception))
		self.assertListEqual(["Got value 'ff8000a'."], context.exception.__notes__)

	def test_Short(self) -> None:
		"""The 3-digit form of CSS isn't supported."""
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor.Parse("#f80")

		self.assertEqual("Parameter 'value' is not of the form '#rrggbb' or '#rrggbbaa'.", str(context.exception))
		self.assertListEqual(["Got value '#f80'."], context.exception.__notes__)

	def test_NotHexadecimal(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = RGBAColor.Parse("#ff800g")

		self.assertEqual("Parameter 'value' is not of the form '#rrggbb' or '#rrggbbaa'.", str(context.exception))
		self.assertListEqual(["Got value '#ff800g'."], context.exception.__notes__)

	def test_Underscore(self) -> None:
		"""Digit separators, which :func:`int` accepts, aren't hexadecimal digits."""
		with self.assertRaises(ValueError):
			_ = RGBAColor.Parse("#f_8000")

	def test_RoundTrip(self) -> None:
		for value in ("#000000", "#ffffff", "#1a2b3c", "#1a2b3c80", "#1a2b3c00"):
			with self.subTest(value=value):
				self.assertEqual(value, str(RGBAColor.Parse(value)))


class Strokes(Testcase):
	def test_Stroke(self) -> None:
		color =  RGBAColor(0, 0, 0)
		stroke = Stroke(1.5, color)

		self.assertEqual(1.5, stroke.Width)
		self.assertIs(color, stroke.Color)
		self.assertIs(LineStyle.Solid, stroke.LineStyle)

	def test_Stroke_Dashed(self) -> None:
		stroke = Stroke(1, RGBAColor(0, 0, 0), LineStyle.Dashed)

		self.assertIs(LineStyle.Dashed, stroke.LineStyle)

	def test_Stroke_GrayColor(self) -> None:
		color =  GrayColor(64)
		stroke = Stroke(1, color)

		self.assertIs(color, stroke.Color)

	def test_Stroke_WidthNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Stroke(None, RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'width' is None.", str(context.exception))

	def test_Stroke_WidthStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Stroke("1", RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'width' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Stroke_WidthZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Stroke(0, RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'width' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)

	def test_Stroke_ColorNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Stroke(1, None)

		self.assertEqual("Parameter 'color' is None.", str(context.exception))

	def test_Stroke_ColorStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Stroke(1, "#000000")

		self.assertEqual("Parameter 'color' is not of type 'Color'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Stroke_LineStyleNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Stroke(1, RGBAColor(0, 0, 0), None)

		self.assertEqual("Parameter 'lineStyle' is None.", str(context.exception))

	def test_Stroke_LineStyleInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Stroke(1, RGBAColor(0, 0, 0), 1)

		self.assertEqual("Parameter 'lineStyle' is not of type 'LineStyle'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Fill(self) -> None:
		color = RGBAColor(0, 0, 255)
		fill =  Fill(color)

		self.assertIs(color, fill.Color)

	def test_Fill_GrayColor(self) -> None:
		color = GrayColor(64)
		fill =  Fill(color)

		self.assertIs(color, fill.Color)

	def test_Fill_ColorNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Fill(None)

		self.assertEqual("Parameter 'color' is None.", str(context.exception))

	def test_Fill_ColorTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Fill((0, 0, 255))

		self.assertEqual("Parameter 'color' is not of type 'Color'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)


class Fonts(Testcase):
	def test_Font(self) -> None:
		font = Font("monospace", 10)

		self.assertEqual("monospace", font.Family)
		self.assertEqual(10, font.Size)
		self.assertFalse(font.Bold)
		self.assertFalse(font.Italic)

	def test_Font_Style(self) -> None:
		font = Font("DejaVu Sans", 8.5, bold=True, italic=True)

		self.assertEqual(8.5, font.Size)
		self.assertTrue(font.Bold)
		self.assertTrue(font.Italic)

	def test_Font_FamilyNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font(None, 10)

		self.assertEqual("Parameter 'family' is None.", str(context.exception))

	def test_Font_FamilyInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font(1, 10)

		self.assertEqual("Parameter 'family' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Font_FamilyEmpty(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("", 10)

		self.assertEqual("Parameter 'family' is empty.", str(context.exception))

	def test_Font_SizeNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", None)

		self.assertEqual("Parameter 'size' is None.", str(context.exception))

	def test_Font_SizeStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", "10pt")

		self.assertEqual("Parameter 'size' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Font_SizeNegative(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", -1)

		self.assertEqual("Parameter 'size' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)

	def test_Font_BoldNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", 10, bold=None)

		self.assertEqual("Parameter 'bold' is None.", str(context.exception))

	def test_Font_ItalicInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10, italic=1)

		self.assertEqual("Parameter 'italic' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class Comparison(Testcase):
	def test_RGBAColor(self) -> None:
		self.assertTrue(RGBAColor(1, 2, 3) == RGBAColor(1, 2, 3, 1.0))
		self.assertFalse(RGBAColor(1, 2, 3) == RGBAColor(1, 2, 3, 0.5))
		self.assertTrue(RGBAColor(1, 2, 3) != RGBAColor(1, 2, 4))
		self.assertFalse(RGBAColor(1, 2, 3) != RGBAColor(1, 2, 3))

	def test_RGBAColor_Hash(self) -> None:
		self.assertEqual(1, len({RGBAColor(1, 2, 3), RGBAColor(1, 2, 3), RGBAColor.Parse("#010203")}))

	def test_RGBAColor_EqualStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor(0, 0, 0) == "#000000"

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for second operand: RGBAColor"],
			context.exception.__notes__
		)

	def test_RGBAColor_UnequalStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor(0, 0, 0) != "#000000"

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for second operand: RGBAColor"],
			context.exception.__notes__
		)

	def test_RGBAColor_EqualGrayColor(self) -> None:
		"""Colors of different color systems aren't compared."""
		with self.assertRaises(TypeError) as context:
			_ = RGBAColor(64, 64, 64) == GrayColor(64)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			[f"Got type '{GrayColor.__module__}.GrayColor'.", "Supported types for second operand: RGBAColor"],
			context.exception.__notes__
		)

	def test_Stroke(self) -> None:
		self.assertTrue(Stroke(1, RGBAColor(0, 0, 0)) == Stroke(1.0, RGBAColor(0, 0, 0), LineStyle.Solid))
		self.assertFalse(Stroke(1, RGBAColor(0, 0, 0)) == Stroke(1, RGBAColor(0, 0, 0), LineStyle.Dotted))
		self.assertTrue(Stroke(1, RGBAColor(0, 0, 0)) != Stroke(2, RGBAColor(0, 0, 0)))
		self.assertTrue(Stroke(1, RGBAColor(0, 0, 0)) != Stroke(1, RGBAColor(0, 0, 1)))
		self.assertFalse(Stroke(1, RGBAColor(0, 0, 0)) != Stroke(1, RGBAColor(0, 0, 0)))

	def test_Stroke_Hash(self) -> None:
		self.assertEqual(1, len({Stroke(1, RGBAColor(0, 0, 0)), Stroke(1, RGBAColor(0, 0, 0))}))

	def test_Stroke_EqualFill(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Stroke(1, RGBAColor(0, 0, 0)) == Fill(RGBAColor(0, 0, 0))

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.Drawing.Fill'.", "Supported types for second operand: Stroke"],
			context.exception.__notes__
		)

	def test_Stroke_UnequalNone(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Stroke(1, RGBAColor(0, 0, 0)) != None

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'NoneType'.", "Supported types for second operand: Stroke"],
			context.exception.__notes__
		)

	def test_Fill(self) -> None:
		self.assertTrue(Fill(RGBAColor(0, 0, 255)) == Fill(RGBAColor(0, 0, 255)))
		self.assertFalse(Fill(RGBAColor(0, 0, 255)) == Fill(RGBAColor(0, 0, 254)))
		self.assertTrue(Fill(RGBAColor(0, 0, 255)) != Fill(RGBAColor(0, 0, 255, 0.5)))
		self.assertFalse(Fill(RGBAColor(0, 0, 255)) != Fill(RGBAColor(0, 0, 255)))

	def test_Fill_Hash(self) -> None:
		self.assertEqual(1, len({Fill(RGBAColor(0, 0, 255)), Fill(RGBAColor(0, 0, 255))}))

	def test_Fill_EqualRGBAColor(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Fill(RGBAColor(0, 0, 255)) == RGBAColor(0, 0, 255)

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'.", "Supported types for second operand: Fill"],
			context.exception.__notes__
		)

	def test_Fill_UnequalRGBAColor(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Fill(RGBAColor(0, 0, 255)) != RGBAColor(0, 0, 255)

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'.", "Supported types for second operand: Fill"],
			context.exception.__notes__
		)

	def test_Font(self) -> None:
		self.assertTrue(Font("serif", 10) == Font("serif", 10.0, bold=False))
		self.assertFalse(Font("serif", 10) == Font("serif", 10, italic=True))
		self.assertTrue(Font("serif", 10) != Font("sans-serif", 10))
		self.assertTrue(Font("serif", 10) != Font("serif", 10, bold=True))
		self.assertFalse(Font("serif", 10) != Font("serif", 10))

	def test_Font_Hash(self) -> None:
		self.assertEqual(1, len({Font("serif", 10), Font("serif", 10)}))

	def test_Font_EqualStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10) == "serif"

		self.assertEqual("Second operand is not supported by == operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for second operand: Font"],
			context.exception.__notes__
		)

	def test_Font_UnequalStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10) != "serif"

		self.assertEqual("Second operand is not supported by != operator.", str(context.exception))
		self.assertListEqual(
			["Got type 'str'.", "Supported types for second operand: Font"],
			context.exception.__notes__
		)


class Immutability(Testcase):
	def test_RGBAColor(self) -> None:
		with self.assertRaises(AttributeError):
			RGBAColor(0, 0, 0).Red = 1

	def test_Stroke(self) -> None:
		with self.assertRaises(AttributeError):
			Stroke(1, RGBAColor(0, 0, 0)).Width = 2

	def test_Fill(self) -> None:
		with self.assertRaises(AttributeError):
			Fill(RGBAColor(0, 0, 0)).Color = RGBAColor(1, 1, 1)

	def test_Font(self) -> None:
		with self.assertRaises(AttributeError):
			Font("serif", 10).Size = 12


class Representation(Testcase):
	def test_RGBAColor_repr(self) -> None:
		self.assertEqual("RGBAColor(255, 128, 0, 1.0)", repr(RGBAColor(255, 128, 0)))

	def test_RGBAColor_str(self) -> None:
		self.assertEqual("#ff8000", str(RGBAColor(255, 128, 0)))

	def test_RGBAColor_str_Alpha(self) -> None:
		self.assertEqual("#ff800080", str(RGBAColor(255, 128, 0, 0.5)))

	def test_RGBAColor_ToHex(self) -> None:
		self.assertEqual("#ff8000", RGBAColor(255, 128, 0).ToHex())

	def test_RGBAColor_ToHex_Alpha(self) -> None:
		self.assertEqual("#ff800080", RGBAColor(255, 128, 0, 0.5).ToHex())

	def test_Stroke_repr(self) -> None:
		stroke = Stroke(2, RGBAColor(0, 0, 0), LineStyle.Dashed)

		self.assertEqual("Stroke(2, RGBAColor(0, 0, 0, 1.0), LineStyle.Dashed)", repr(stroke))

	def test_Fill_repr(self) -> None:
		self.assertEqual("Fill(RGBAColor(0, 0, 255, 0.5))", repr(Fill(RGBAColor(0, 0, 255, 0.5))))

	def test_Font_repr(self) -> None:
		self.assertEqual("Font('monospace', 10, bold=True, italic=False)", repr(Font("monospace", 10, bold=True)))
