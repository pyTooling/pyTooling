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
Unit tests for :mod:`pyTooling.Cartesian2D.Drawing` - colors, strokes, fills, fonts, drawable shapes and texts.
"""
from copy                          import copy, deepcopy
from math                          import isclose

from pyTooling.Cartesian2D         import Point2D, Offset2D, Size2D, BoundingBox2D, Alignment2D, Shapes, \
                                          AlreadyOwnedError, LineSegment2D as GeometricLineSegment2D
from pyTooling.Cartesian2D.Groups  import Group2D, Canvas2D, YAxisDirection
from pyTooling.Cartesian2D.Drawing import TextAlignment, VerticalAnchor, LineStyle, Color, RGBAColor, Stroke, Fill, \
                                          FontStyle, Font, StrokeMixin, StyleMixin, LineSegment2D, Polygon, Trapezium, \
                                          Rectangle, Square, Circle, Text
from pyTooling.MetaClasses         import ExtendedType, AbstractClassError
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
		self.assertFalse(font.SmallCaps)
		self.assertIs(FontStyle.Upright, font.FontStyle)

	def test_Font_Style(self) -> None:
		font = Font("DejaVu Sans", 8.5, bold=True, smallCaps=True, fontStyle=FontStyle.Italic)

		self.assertEqual(8.5, font.Size)
		self.assertTrue(font.Bold)
		self.assertTrue(font.SmallCaps)
		self.assertIs(FontStyle.Italic, font.FontStyle)

	def test_Font_Slanted(self) -> None:
		font = Font("serif", 10, fontStyle=FontStyle.Slanted)

		self.assertIs(FontStyle.Slanted, font.FontStyle)

	def test_Font_CharacterWidth(self) -> None:
		font = Font("sans-serif", 10, characterWidth=0.5)

		self.assertEqual(0.5, font.CharacterWidth)
		self.assertEqual(0.6, Font("monospace", 10).CharacterWidth)

	def test_Font_CharacterWidthNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", 10, characterWidth=None)

		self.assertEqual("Parameter 'characterWidth' is None.", str(context.exception))

	def test_Font_CharacterWidthStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10, characterWidth="0.5")

		self.assertEqual("Parameter 'characterWidth' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Font_CharacterWidthZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", 10, characterWidth=0)

		self.assertEqual("Parameter 'characterWidth' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)

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

	def test_Font_SmallCapsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", 10, smallCaps=None)

		self.assertEqual("Parameter 'smallCaps' is None.", str(context.exception))

	def test_Font_SmallCapsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10, smallCaps=1)

		self.assertEqual("Parameter 'smallCaps' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Font_FontStyleNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Font("serif", 10, fontStyle=None)

		self.assertEqual("Parameter 'fontStyle' is None.", str(context.exception))

	def test_Font_FontStyleBool(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Font("serif", 10, fontStyle=True)

		self.assertEqual("Parameter 'fontStyle' is not of type 'FontStyle'.", str(context.exception))
		self.assertListEqual(["Got type 'bool'."], context.exception.__notes__)


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
		self.assertFalse(Font("serif", 10) == Font("serif", 10, fontStyle=FontStyle.Italic))
		self.assertFalse(Font("serif", 10) == Font("serif", 10, smallCaps=True))
		self.assertTrue(Font("serif", 10, fontStyle=FontStyle.Italic) != Font("serif", 10, fontStyle=FontStyle.Slanted))
		self.assertTrue(Font("serif", 10) != Font("serif", 10, smallCaps=True))
		self.assertTrue(Font("serif", 10) != Font("serif", 10, characterWidth=0.5))
		self.assertFalse(Font("serif", 10) == Font("serif", 10, characterWidth=0.5))
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
		self.assertEqual(
			"Font('monospace', 10, bold=True, smallCaps=False, fontStyle=FontStyle.Upright, characterWidth=0.6)",
			repr(Font("monospace", 10, bold=True))
		)


STROKE = Stroke(1, RGBAColor(0, 0, 0))
"""A black outline, shared by the tests."""

FILL = Fill(RGBAColor(255, 128, 0))
"""An orange area, shared by the tests."""


class Drawables(Testcase):
	def test_LineSegment(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE)

		self.assertIsInstance(line, GeometricLineSegment2D)
		self.assertIsInstance(line, StrokeMixin)
		self.assertNotIsInstance(line, StyleMixin)
		self.assertIs(STROKE, line.Stroke)
		self.assertEqual(5.0, line.Length)

	def test_LineSegment_Default(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6))

		self.assertIsNone(line.Stroke)

	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), stroke=STROKE, fill=FILL)

		self.assertIsInstance(polygon, Shapes.Polygon)
		self.assertIsInstance(polygon, StyleMixin)
		self.assertIs(STROKE, polygon.Stroke)
		self.assertIs(FILL, polygon.Fill)
		self.assertEqual(3, len(polygon.Segments))

	def test_Polygon_Default(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		self.assertIsNone(polygon.Stroke)
		self.assertIsNone(polygon.Fill)

	def test_Trapezium(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), stroke=STROKE, fill=FILL)

		self.assertIsInstance(trapezium, Shapes.Trapezium)
		self.assertIs(STROKE, trapezium.Stroke)
		self.assertIs(FILL, trapezium.Fill)

	def test_Rectangle(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), stroke=STROKE, fill=FILL)

		self.assertIsInstance(rectangle, Shapes.Rectangle)
		self.assertIs(STROKE, rectangle.Stroke)
		self.assertIs(FILL, rectangle.Fill)

	def test_Rectangle_Parallelogram(self) -> None:
		"""The geometry is checked as for a geometric rectangle."""
		with self.assertRaises(ValueError):
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(5, 2), Point2D(1, 2), stroke=STROKE)

	def test_Square(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), stroke=STROKE, fill=FILL)

		self.assertIsInstance(square, Shapes.Square)
		self.assertNotIsInstance(square, Rectangle)
		self.assertIs(STROKE, square.Stroke)
		self.assertIs(FILL, square.Fill)

	def test_Square_Rectangle(self) -> None:
		with self.assertRaises(ValueError):
			_ = Square(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))

	def test_Circle(self) -> None:
		circle = Circle(Point2D(1, 2), 3, stroke=STROKE, fill=FILL)

		self.assertIsInstance(circle, Shapes.Circle)
		self.assertIs(STROKE, circle.Stroke)
		self.assertIs(FILL, circle.Fill)
		self.assertEqual(6, circle.Diameter)

	def test_Circle_copyPoints(self) -> None:
		center = Point2D(1, 2)
		circle = Circle(center, 3, copyPoints=False, fill=FILL)

		self.assertIs(center, circle.Center)
		self.assertIs(circle, center.Parent)

	def test_Circle_Move(self) -> None:
		"""A drawable shape moves like its geometry and keeps its styles."""
		circle = Circle(Point2D(1, 2), 3, stroke=STROKE)

		circle.Move(Offset2D(1, 1))

		self.assertTupleEqual((2, 3), circle.Center.ToTuple())
		self.assertIs(STROKE, circle.Stroke)

	def test_Slots(self) -> None:
		for drawableClass in (LineSegment2D, Polygon, Trapezium, Rectangle, Square, Circle):
			self.assertIsInstance(drawableClass, ExtendedType)
			self.assertNotIn("__dict__", dir(drawableClass))

		self.assertTupleEqual(("_stroke", ), LineSegment2D.__slots__)
		self.assertTupleEqual(("_stroke", "_fill"), Polygon.__slots__)


class StyleParameters(Testcase):
	def test_LineSegment_StrokeColor(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'stroke' is not of type 'Stroke'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'."], context.exception.__notes__)

	def test_LineSegment_Fill(self) -> None:
		"""A line has no area, so it has no parameter 'fill'."""
		with self.assertRaises(TypeError):
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), fill=FILL)

	def test_Polygon_StrokeFill(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), stroke=FILL)

		self.assertEqual("Parameter 'stroke' is not of type 'Stroke'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.Fill'."], context.exception.__notes__)

	def test_Polygon_FillColor(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'fill' is not of type 'Fill'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'."], context.exception.__notes__)

	def test_Trapezium_FillStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), fill="#ff8000")

		self.assertEqual("Parameter 'fill' is not of type 'Fill'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Rectangle_StrokeInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), stroke=1)

		self.assertEqual("Parameter 'stroke' is not of type 'Stroke'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Square_FillInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), fill=1)

		self.assertEqual("Parameter 'fill' is not of type 'Fill'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Circle_StrokeStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), 3, stroke="black")

		self.assertEqual("Parameter 'stroke' is not of type 'Stroke'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)


class StyleProperties(Testcase):
	def test_Stroke(self) -> None:
		line =   LineSegment2D(Point2D(1, 2), Point2D(4, 6))
		dashed = Stroke(2, RGBAColor(0, 0, 255), LineStyle.Dashed)

		line.Stroke = dashed

		self.assertIs(dashed, line.Stroke)

	def test_Stroke_None(self) -> None:
		circle = Circle(Point2D(1, 2), 3, stroke=STROKE)

		circle.Stroke = None

		self.assertIsNone(circle.Stroke)

	def test_Stroke_RGBAColor(self) -> None:
		circle = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError) as context:
			circle.Stroke = RGBAColor(0, 0, 0)

		self.assertEqual("Parameter 'stroke' is not of type 'Stroke'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'."], context.exception.__notes__)
		self.assertIsNone(circle.Stroke)

	def test_Fill(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		polygon.Fill = FILL

		self.assertIs(FILL, polygon.Fill)

	def test_Fill_None(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL)

		polygon.Fill = None

		self.assertIsNone(polygon.Fill)

	def test_Fill_Stroke(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL)

		with self.assertRaises(TypeError) as context:
			polygon.Fill = STROKE

		self.assertEqual("Parameter 'fill' is not of type 'Fill'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.Stroke'."], context.exception.__notes__)
		self.assertIs(FILL, polygon.Fill)

	def test_Shared(self) -> None:
		"""Styles are values, so elements share them."""
		circle1 = Circle(Point2D(1, 2), 3, stroke=STROKE, fill=FILL)
		circle2 = Circle(Point2D(9, 2), 3, stroke=STROKE, fill=FILL)

		self.assertIs(circle1.Stroke, circle2.Stroke)
		self.assertIs(circle1.Fill, circle2.Fill)


class Parents(Testcase):
	def test_LineSegment(self) -> None:
		group = Group2D()
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE, parent=group)

		self.assertIs(group, line.Parent)
		self.assertTupleEqual((line, ), group.Children)

	def test_LineSegment_Shape(self) -> None:
		"""A drawable line segment is no edge of a shape."""
		triangle = Shapes.Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), parent=triangle)

		self.assertEqual("Parameter 'parent' is not of type 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Shapes.Polygon'."], context.exception.__notes__)

	def test_Polygon(self) -> None:
		canvas =  Canvas2D()
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL, parent=canvas)

		self.assertIs(canvas, polygon.Parent)
		self.assertTupleEqual((polygon, ), canvas.Children)

	def test_Trapezium(self) -> None:
		group =     Group2D()
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), parent=group)

		self.assertTupleEqual((trapezium, ), group.Children)

	def test_Rectangle(self) -> None:
		group =     Group2D()
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=group)

		self.assertTupleEqual((rectangle, ), group.Children)

	def test_Square(self) -> None:
		group =  Group2D()
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), parent=group)

		self.assertTupleEqual((square, ), group.Children)

	def test_Circle(self) -> None:
		group =  Group2D()
		circle = Circle(Point2D(1, 2), 3, parent=group)

		self.assertTupleEqual((circle, ), group.Children)

	def test_Circle_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), 3, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_FailingStyle(self) -> None:
		"""A failing style check leaves nothing registered."""
		group =  Group2D()
		center = Point2D(1, 2)

		with self.assertRaises(TypeError):
			_ = Circle(center, 3, copyPoints=False, fill=1, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_FailingGeometry(self) -> None:
		group = Group2D()
		point = Point2D(0, 0)
		_ =     Shapes.Circle(point, 1, copyPoints=False)

		with self.assertRaises(AlreadyOwnedError):
			_ = Polygon((point, Point2D(4, 0), Point2D(2, 3)), copyPoints=False, stroke=STROKE, parent=group)

		self.assertTupleEqual((), group.Children)


class Copies(Testcase):
	def test_LineSegment(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE)

		newLine = line.Copy()

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIsNot(line.Start, newLine.Start)
		self.assertIs(STROKE, newLine.Stroke)

	def test_LineSegment_copy(self) -> None:
		line = LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE)

		newLine = copy(line)

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIs(STROKE, newLine.Stroke)

	def test_Polygon(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), stroke=STROKE, fill=FILL)

		newPolygon = polygon.Copy()

		self.assertIs(Polygon, type(newPolygon))
		self.assertIsNot(polygon.Points[0], newPolygon.Points[0])
		self.assertIs(STROKE, newPolygon.Stroke)
		self.assertIs(FILL, newPolygon.Fill)

	def test_Polygon_copy(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL)

		newPolygon = copy(polygon)

		self.assertIs(Polygon, type(newPolygon))
		self.assertIsNone(newPolygon.Stroke)
		self.assertIs(FILL, newPolygon.Fill)

	def test_Trapezium(self) -> None:
		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), stroke=STROKE, fill=FILL)

		newTrapezium = trapezium.Copy()

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIs(STROKE, newTrapezium.Stroke)
		self.assertIs(FILL, newTrapezium.Fill)

	def test_Rectangle(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), stroke=STROKE, fill=FILL)

		newRectangle = copy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIs(STROKE, newRectangle.Stroke)
		self.assertIs(FILL, newRectangle.Fill)

	def test_Square(self) -> None:
		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), stroke=STROKE, fill=FILL)

		newSquare = square.Copy()

		self.assertIs(Square, type(newSquare))
		self.assertIs(STROKE, newSquare.Stroke)
		self.assertIs(FILL, newSquare.Fill)

	def test_Circle(self) -> None:
		circle = Circle(Point2D(1, 2), 3, stroke=STROKE, fill=FILL)

		newCircle = circle.Copy()

		self.assertIs(Circle, type(newCircle))
		self.assertIsNot(circle.Center, newCircle.Center)
		self.assertIs(STROKE, newCircle.Stroke)
		self.assertIs(FILL, newCircle.Fill)

	def test_LineSegment_deepcopy(self) -> None:
		group = Group2D()
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE, value=[1, 2], parent=group)

		newLine = deepcopy(line)

		self.assertIs(LineSegment2D, type(newLine))
		self.assertIsNone(newLine.Parent)
		self.assertIs(newLine, newLine.Start.Parent)
		self.assertIs(STROKE, newLine.Stroke)
		self.assertIsNot(line.Value, newLine.Value)
		self.assertListEqual([1, 2], newLine.Value)
		self.assertTupleEqual((line, ), group.Children)

	def test_Polygon_deepcopy(self) -> None:
		group =   Group2D()
		polygon = Polygon(
			(Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)),
			stroke=STROKE,
			fill=FILL,
			value=[1, 2],
			parent=group
		)

		newPolygon = deepcopy(polygon)

		self.assertIs(Polygon, type(newPolygon))
		self.assertIsNone(newPolygon.Parent)
		self.assertIs(newPolygon, newPolygon.Points[0].Parent)
		self.assertIs(STROKE, newPolygon.Stroke)
		self.assertIs(FILL, newPolygon.Fill)
		self.assertIsNot(polygon.Value, newPolygon.Value)
		self.assertListEqual([1, 2], newPolygon.Value)
		self.assertTupleEqual((polygon, ), group.Children)

	def test_Trapezium_deepcopy(self) -> None:
		group =     Group2D()
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			stroke=STROKE,
			fill=FILL,
			value=[1, 2],
			parent=group
		)

		newTrapezium = deepcopy(trapezium)

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIsNone(newTrapezium.Parent)
		self.assertIs(newTrapezium, newTrapezium.Points[0].Parent)
		self.assertIs(STROKE, newTrapezium.Stroke)
		self.assertIs(FILL, newTrapezium.Fill)
		self.assertIsNot(trapezium.Value, newTrapezium.Value)
		self.assertListEqual([1, 2], newTrapezium.Value)
		self.assertTupleEqual((trapezium, ), group.Children)

	def test_Rectangle_deepcopy(self) -> None:
		group =     Group2D()
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			stroke=STROKE,
			fill=FILL,
			value=[1, 2],
			parent=group
		)

		newRectangle = deepcopy(rectangle)

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIsNone(newRectangle.Parent)
		self.assertIs(newRectangle, newRectangle.Points[0].Parent)
		self.assertIs(STROKE, newRectangle.Stroke)
		self.assertIs(FILL, newRectangle.Fill)
		self.assertIsNot(rectangle.Value, newRectangle.Value)
		self.assertListEqual([1, 2], newRectangle.Value)
		self.assertTupleEqual((rectangle, ), group.Children)

	def test_Square_deepcopy(self) -> None:
		group =  Group2D()
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			stroke=STROKE,
			fill=FILL,
			value=[1, 2],
			parent=group
		)

		newSquare = deepcopy(square)

		self.assertIs(Square, type(newSquare))
		self.assertIsNone(newSquare.Parent)
		self.assertIs(newSquare, newSquare.Points[0].Parent)
		self.assertIs(STROKE, newSquare.Stroke)
		self.assertIs(FILL, newSquare.Fill)
		self.assertIsNot(square.Value, newSquare.Value)
		self.assertListEqual([1, 2], newSquare.Value)
		self.assertTupleEqual((square, ), group.Children)

	def test_Circle_deepcopy(self) -> None:
		group =  Group2D()
		circle = Circle(Point2D(1, 2), 3, stroke=STROKE, fill=FILL, value=[1, 2], parent=group)

		newCircle = deepcopy(circle)

		self.assertIs(Circle, type(newCircle))
		self.assertIsNone(newCircle.Parent)
		self.assertIs(newCircle, newCircle.Center.Parent)
		self.assertIs(STROKE, newCircle.Stroke)
		self.assertIs(FILL, newCircle.Fill)
		self.assertIsNot(circle.Value, newCircle.Value)
		self.assertListEqual([1, 2], newCircle.Value)
		self.assertTupleEqual((circle, ), group.Children)

	def test_Text_deepcopy(self) -> None:
		group = Group2D()
		text =  Text(Point2D(0, 0), "clock", font=Font("monospace", 10), fill=FILL, value=[1, 2], parent=group)

		newText = deepcopy(text)

		self.assertIs(Text, type(newText))
		self.assertIsNone(newText.Parent)
		self.assertIs(newText, newText.Position.Parent)
		self.assertIs(FILL, newText.Fill)
		self.assertIs(text.Font, newText.Font)
		self.assertIsNot(text.Value, newText.Value)
		self.assertListEqual([1, 2], newText.Value)
		self.assertTupleEqual((text, ), group.Children)



class ElementData(Testcase):
	def test_LineSegment(self) -> None:
		value = object()
		pairs = {"layer": 1}
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE, value=value, keyValuePairs=pairs)

		self.assertIs(value, line.Value)
		self.assertEqual(1, line["layer"])
		self.assertIsNot(pairs, line._dict)

	def test_LineSegment_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_Copy(self) -> None:
		value = [1, 2]
		line =  LineSegment2D(Point2D(1, 2), Point2D(4, 6), stroke=STROKE, value=value, keyValuePairs={"layer": 1})

		newLineSegment =          line.Copy()
		newLineSegment["layer"] = 2

		self.assertIs(LineSegment2D, type(newLineSegment))
		self.assertIs(value, newLineSegment.Value)
		self.assertEqual(1, line["layer"])
		self.assertEqual(2, newLineSegment["layer"])

	def test_Polygon(self) -> None:
		value =   object()
		pairs =   {"layer": 1}
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL, value=value, keyValuePairs=pairs)

		self.assertIs(value, polygon.Value)
		self.assertEqual(1, polygon["layer"])
		self.assertIsNot(pairs, polygon._dict)

	def test_Polygon_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Polygon_Copy(self) -> None:
		value =   [1, 2]
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), fill=FILL, value=value, keyValuePairs={"layer": 1})

		newPolygon =          polygon.Copy()
		newPolygon["layer"] = 2

		self.assertIs(Polygon, type(newPolygon))
		self.assertIs(value, newPolygon.Value)
		self.assertEqual(1, polygon["layer"])
		self.assertEqual(2, newPolygon["layer"])

	def test_Trapezium(self) -> None:
		value = object()
		pairs = {"layer": 1}
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			fill=FILL,
			value=value,
			keyValuePairs=pairs
		)

		self.assertIs(value, trapezium.Value)
		self.assertEqual(1, trapezium["layer"])
		self.assertIsNot(pairs, trapezium._dict)

	def test_Trapezium_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Trapezium_Copy(self) -> None:
		value =     [1, 2]
		trapezium = Trapezium(
			Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3),
			fill=FILL,
			value=value,
			keyValuePairs={"layer": 1}
		)

		newTrapezium =          trapezium.Copy()
		newTrapezium["layer"] = 2

		self.assertIs(Trapezium, type(newTrapezium))
		self.assertIs(value, newTrapezium.Value)
		self.assertEqual(1, trapezium["layer"])
		self.assertEqual(2, newTrapezium["layer"])

	def test_Rectangle(self) -> None:
		value = object()
		pairs = {"layer": 1}
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			fill=FILL,
			value=value,
			keyValuePairs=pairs
		)

		self.assertIs(value, rectangle.Value)
		self.assertEqual(1, rectangle["layer"])
		self.assertIsNot(pairs, rectangle._dict)

	def test_Rectangle_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Rectangle_Copy(self) -> None:
		value =     [1, 2]
		rectangle = Rectangle(
			Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2),
			fill=FILL,
			value=value,
			keyValuePairs={"layer": 1}
		)

		newRectangle =          rectangle.Copy()
		newRectangle["layer"] = 2

		self.assertIs(Rectangle, type(newRectangle))
		self.assertIs(value, newRectangle.Value)
		self.assertEqual(1, rectangle["layer"])
		self.assertEqual(2, newRectangle["layer"])

	def test_Square(self) -> None:
		value = object()
		pairs = {"layer": 1}
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			fill=FILL,
			value=value,
			keyValuePairs=pairs
		)

		self.assertIs(value, square.Value)
		self.assertEqual(1, square["layer"])
		self.assertIsNot(pairs, square._dict)

	def test_Square_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Square_Copy(self) -> None:
		value =  [1, 2]
		square = Square(
			Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2),
			fill=FILL,
			value=value,
			keyValuePairs={"layer": 1}
		)

		newSquare =          square.Copy()
		newSquare["layer"] = 2

		self.assertIs(Square, type(newSquare))
		self.assertIs(value, newSquare.Value)
		self.assertEqual(1, square["layer"])
		self.assertEqual(2, newSquare["layer"])

	def test_Circle(self) -> None:
		value =  object()
		pairs =  {"layer": 1}
		circle = Circle(Point2D(1, 2), 3, fill=FILL, value=value, keyValuePairs=pairs)

		self.assertIs(value, circle.Value)
		self.assertEqual(1, circle["layer"])
		self.assertIsNot(pairs, circle._dict)

	def test_Circle_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Circle(Point2D(1, 2), 3, keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Circle_Copy(self) -> None:
		value =  [1, 2]
		circle = Circle(Point2D(1, 2), 3, fill=FILL, value=value, keyValuePairs={"layer": 1})

		newCircle =          circle.Copy()
		newCircle["layer"] = 2

		self.assertIs(Circle, type(newCircle))
		self.assertIs(value, newCircle.Value)
		self.assertEqual(1, circle["layer"])
		self.assertEqual(2, newCircle["layer"])

	def test_Text(self) -> None:
		value = object()
		pairs = {"pin": "clock"}
		text =  Text(Point2D(0, 0), "clock", fill=FILL, value=value, keyValuePairs=pairs)

		self.assertIs(value, text.Value)
		self.assertEqual("clock", text["pin"])
		self.assertIsNot(pairs, text._dict)

	def test_Text_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "clock", keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Text_Copy(self) -> None:
		value = [1, 2]
		text =  Text(Point2D(0, 0), "clock", fill=FILL, value=value, keyValuePairs={"layer": 1})

		newText =          text.Copy()
		newText["layer"] = 2

		self.assertIs(Text, type(newText))
		self.assertIs(value, newText.Value)
		self.assertEqual(1, text["layer"])
		self.assertEqual(2, newText["layer"])


MONOSPACE = Font("monospace", 10)
"""A 10 point monospace font: a character is 6 points wide, a line 10 points high, the next baseline 12 points below."""


class Texts(Testcase):
	def test_Text(self) -> None:
		position = Point2D(10, 20)
		text =     Text(position, "Hello", font=MONOSPACE, fill=FILL)

		self.assertIsNot(position, text.Position)
		self.assertIs(text, text.Position.Parent)
		self.assertTupleEqual((10, 20), text.Position.ToTuple())
		self.assertEqual("Hello", text.Content)
		self.assertTupleEqual(("Hello", ), text.Lines)
		self.assertEqual(1, text.LineCount)
		self.assertIs(MONOSPACE, text.Font)
		self.assertIs(FILL, text.Fill)
		self.assertIsNone(text.Stroke)

	def test_Text_Default(self) -> None:
		text = Text(Point2D(0, 0), "Hello")

		self.assertEqual(Font("sans-serif", 10), text.Font)
		self.assertIs(TextAlignment.Left, text.Alignment)
		self.assertIs(VerticalAnchor.Baseline, text.Anchor)
		self.assertEqual(1.2, text.LineHeight)

	def test_Text_MultiLine(self) -> None:
		text = Text(Point2D(0, 0), "clock\nreset\n")

		self.assertTupleEqual(("clock", "reset", ""), text.Lines)
		self.assertEqual(3, text.LineCount)

	def test_Text_copyPoints(self) -> None:
		position = Point2D(10, 20)
		text =     Text(position, "Hello", copyPoints=False)

		self.assertIs(position, text.Position)
		self.assertIs(text, position.Parent)

	def test_Text_PositionOwned(self) -> None:
		position = Point2D(10, 20)
		_ =        Text(position, "Hello", copyPoints=False)

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Text(position, "World", copyPoints=False)

		self.assertEqual("Point is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got point (10, 20) owned by Text((10, 20), 'Hello').", "Use 'copyPoints=True' to copy the point."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'position' is owned by another element.", str(context.exception.__cause__))

	def test_Text_PositionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(None, "Hello")

		self.assertEqual("Parameter 'position' is None.", str(context.exception))

	def test_Text_PositionTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text((1, 2), "Hello")

		self.assertEqual("Parameter 'position' is not of type 'Point2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Text_ContentNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), None)

		self.assertEqual("Parameter 'content' is None.", str(context.exception))

	def test_Text_ContentInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), 42)

		self.assertEqual("Parameter 'content' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Text_copyPointsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", copyPoints=None)

		self.assertEqual("Parameter 'copyPoints' is None.", str(context.exception))

	def test_Text_copyPointsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", copyPoints=1)

		self.assertEqual("Parameter 'copyPoints' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Text_FontNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", font=None)

		self.assertEqual("Parameter 'font' is None.", str(context.exception))

	def test_Text_FontStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", font="monospace")

		self.assertEqual("Parameter 'font' is not of type 'Font'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Text_AlignmentNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", alignment=None)

		self.assertEqual("Parameter 'alignment' is None.", str(context.exception))

	def test_Text_AlignmentAlignment2D(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", alignment=Alignment2D.MinX)

		self.assertEqual("Parameter 'alignment' is not of type 'TextAlignment'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Alignment2D'."], context.exception.__notes__)

	def test_Text_AnchorNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", anchor=None)

		self.assertEqual("Parameter 'anchor' is None.", str(context.exception))

	def test_Text_AnchorAlignment(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", anchor=TextAlignment.Center)

		self.assertEqual("Parameter 'anchor' is not of type 'VerticalAnchor'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.TextAlignment'."], context.exception.__notes__)

	def test_Text_LineHeightNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", lineHeight=None)

		self.assertEqual("Parameter 'lineHeight' is None.", str(context.exception))

	def test_Text_LineHeightStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", lineHeight="1.2")

		self.assertEqual("Parameter 'lineHeight' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Text_LineHeightZero(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Text(Point2D(0, 0), "Hello", lineHeight=0)

		self.assertEqual("Parameter 'lineHeight' isn't positive.", str(context.exception))
		self.assertListEqual(["Got value '0'."], context.exception.__notes__)

	def test_Text_FillColor(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", fill=RGBAColor(0, 0, 0))

		self.assertEqual("Parameter 'fill' is not of type 'Fill'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Drawing.RGBAColor'."], context.exception.__notes__)

	def test_Text_Parent(self) -> None:
		group = Group2D()
		text =  Text(Point2D(0, 0), "Hello", parent=group)

		self.assertIs(group, text.Parent)
		self.assertTupleEqual((text, ), group.Children)

	def test_Text_ParentInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Text(Point2D(0, 0), "Hello", parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group2D' or 'Canvas2D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Text_FailingCheck(self) -> None:
		"""A failing check leaves nothing registered."""
		group = Group2D()

		with self.assertRaises(ValueError):
			_ = Text(Point2D(0, 0), "Hello", lineHeight=-1, parent=group)

		self.assertTupleEqual((), group.Children)


class TextBounds(Testcase):
	def test_Baseline(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE)

		self.assertEqual(BoundingBox2D(10, 18, 40, 28), text.BoundingBox)

	def test_Top(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE, anchor=VerticalAnchor.Top)

		self.assertEqual(BoundingBox2D(10, 10, 40, 20), text.BoundingBox)

	def test_Middle(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE, anchor=VerticalAnchor.Middle)

		self.assertEqual(BoundingBox2D(10, 15, 40, 25), text.BoundingBox)

	def test_Bottom(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE, anchor=VerticalAnchor.Bottom)

		self.assertEqual(BoundingBox2D(10, 20, 40, 30), text.BoundingBox)

	def test_Center(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE, alignment=TextAlignment.Center)

		self.assertEqual(BoundingBox2D(-5, 18, 25, 28), text.BoundingBox)

	def test_Right(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE, alignment=TextAlignment.Right)

		self.assertEqual(BoundingBox2D(-20, 18, 10, 28), text.BoundingBox)

	def test_MultiLine(self) -> None:
		"""The longest line sets the width; each further line adds the line height."""
		text = Text(Point2D(0, 0), "a\nabcd\nab", font=MONOSPACE, anchor=VerticalAnchor.Top)

		box = text.BoundingBox

		self.assertTrue(isclose(24, box.Width))
		self.assertTrue(isclose(34, box.Height))
		self.assertEqual(0, box.MaxY)

	def test_MultiLine_Baseline(self) -> None:
		"""The baseline of the first line is at the position."""
		text = Text(Point2D(0, 0), "ab\nab", font=MONOSPACE)

		box = text.BoundingBox

		self.assertTrue(isclose(8, box.MaxY))
		self.assertTrue(isclose(-14, box.MinY))

	def test_LineHeight(self) -> None:
		text = Text(Point2D(0, 0), "ab\nab", font=MONOSPACE, anchor=VerticalAnchor.Top, lineHeight=2)

		self.assertTrue(isclose(30, text.BoundingBox.Height))

	def test_CharacterWidth(self) -> None:
		text = Text(Point2D(0, 0), "Hello", font=Font("sans-serif", 10, characterWidth=0.5))

		self.assertTrue(isclose(25, text.BoundingBox.Width))

	def test_Empty(self) -> None:
		text = Text(Point2D(10, 20), "", font=MONOSPACE)

		self.assertEqual(BoundingBox2D(10, 18, 10, 28), text.BoundingBox)

	def test_CanvasDown(self) -> None:
		"""On a canvas with the y-axis pointing down, the top of a text has its smallest y-coordinate."""
		canvas = Canvas2D(YAxisDirection.Down)
		text =   Text(Point2D(10, 20), "Hello", font=MONOSPACE, parent=canvas)

		self.assertEqual(BoundingBox2D(10, 12, 40, 22), text.BoundingBox)

	def test_CanvasDown_Top(self) -> None:
		canvas = Canvas2D(YAxisDirection.Down)
		group =  Group2D(parent=canvas)
		text =   Text(Point2D(10, 20), "a\nb", font=MONOSPACE, anchor=VerticalAnchor.Top, parent=group)

		self.assertEqual(BoundingBox2D(10, 20, 16, 42), text.BoundingBox)

	def test_CanvasUp(self) -> None:
		canvas = Canvas2D(YAxisDirection.Up)
		text =   Text(Point2D(10, 20), "Hello", font=MONOSPACE, anchor=VerticalAnchor.Top, parent=canvas)

		self.assertEqual(BoundingBox2D(10, 10, 40, 20), text.BoundingBox)

	def test_CanvasMirror(self) -> None:
		"""Flipping the canvas keeps the text where it is drawn."""
		canvas = Canvas2D(YAxisDirection.Down, Size2D(100, 100))
		text =   Text(Point2D(10, 20), "Hello", font=MONOSPACE, anchor=VerticalAnchor.Top, parent=canvas)

		canvas.Mirror()

		self.assertEqual(BoundingBox2D(10, 70, 40, 80), text.BoundingBox)
		self.assertEqual(80, canvas.Top(text))

	def test_Group(self) -> None:
		group = Group2D(Offset2D(100, 0))
		text =  Text(Point2D(10, 20), "Hello", font=MONOSPACE, parent=group)

		self.assertEqual(BoundingBox2D(10, 18, 40, 28), text.BoundingBox)
		self.assertEqual(BoundingBox2D(110, 18, 140, 28), text.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox2D(110, 18, 140, 28), group.BoundingBox)


class TextTransformations(Testcase):
	def test_Move(self) -> None:
		text = Text(Point2D(10, 20), "Hello")

		text.Move(Offset2D(1, 2))

		self.assertTupleEqual((11, 22), text.Position.ToTuple())

	def test_Move_None(self) -> None:
		text = Text(Point2D(10, 20), "Hello")

		with self.assertRaises(ValueError) as context:
			text.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Move_Tuple(self) -> None:
		text = Text(Point2D(10, 20), "Hello")

		with self.assertRaises(TypeError) as context:
			text.Move((1, 2))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_MirrorX(self) -> None:
		"""Mirroring moves the position; the alignment stays, so the box isn't the mirror image."""
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE)

		text.MirrorX(Alignment2D.MinX)

		self.assertTupleEqual((10, 20), text.Position.ToTuple())
		self.assertIs(TextAlignment.Left, text.Alignment)

		text.MirrorX(Alignment2D.MaxX)

		self.assertTupleEqual((70, 20), text.Position.ToTuple())
		self.assertEqual(BoundingBox2D(70, 18, 100, 28), text.BoundingBox)

	def test_MirrorY(self) -> None:
		text = Text(Point2D(10, 20), "Hello", font=MONOSPACE)

		text.MirrorY(Alignment2D.MaxY)

		self.assertTupleEqual((10, 36), text.Position.ToTuple())
		self.assertIs(VerticalAnchor.Baseline, text.Anchor)

	def test_AlignTo(self) -> None:
		box =  Rectangle(Point2D(0, 0), Point2D(40, 0), Point2D(40, 20), Point2D(0, 20))
		text = Text(Point2D(100, 100), "Hi", font=MONOSPACE, anchor=VerticalAnchor.Top)

		text.AlignTo(box, Alignment2D.MaxX)

		self.assertTupleEqual((28, 100), text.Position.ToTuple())

	def test_Copy(self) -> None:
		text = Text(
			Point2D(10, 20), "a\nb",
			font=MONOSPACE,
			alignment=TextAlignment.Right,
			anchor=VerticalAnchor.Top,
			lineHeight=1.5,
			stroke=STROKE,
			fill=FILL
		)

		newText = text.Copy()

		self.assertIs(Text, type(newText))
		self.assertIsNot(text.Position, newText.Position)
		self.assertIs(newText, newText.Position.Parent)
		self.assertTupleEqual((10, 20), newText.Position.ToTuple())
		self.assertEqual("a\nb", newText.Content)
		self.assertIs(MONOSPACE, newText.Font)
		self.assertIs(TextAlignment.Right, newText.Alignment)
		self.assertIs(VerticalAnchor.Top, newText.Anchor)
		self.assertEqual(1.5, newText.LineHeight)
		self.assertIs(STROKE, newText.Stroke)
		self.assertIs(FILL, newText.Fill)

	def test_Copy_copy(self) -> None:
		text = Text(Point2D(10, 20), "Hello", fill=FILL)

		newText = copy(text)

		self.assertIs(Text, type(newText))
		self.assertIsNot(text.Position, newText.Position)
		self.assertIs(FILL, newText.Fill)

	def test_repr(self) -> None:
		self.assertEqual("Text((10, 20), 'a\\nb')", repr(Text(Point2D(10, 20), "a\nb")))

	def test_str(self) -> None:
		self.assertEqual("a\nb", str(Text(Point2D(10, 20), "a\nb")))
