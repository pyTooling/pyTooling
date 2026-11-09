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
Drawable 2D cartesian shapes, texts and their styles: colors, strokes, fills and fonts.

A drawable shape is its geometry class from :mod:`pyTooling.Cartesian2D.Shapes` with a style, and has the same name:
:class:`Rectangle` is a :class:`pyTooling.Cartesian2D.Shapes.Rectangle` with a :class:`Stroke` and a :class:`Fill`.

The style classes are values: they can't be changed after creation, compare by value and can be shared by any number
of elements.

.. seealso::

   :mod:`pyTooling.Cartesian2D.Shapes`
      |rarr| The geometry of the shapes.
   :mod:`pyTooling.Cartesian2D.Groups`
      |rarr| Groups and canvases holding drawable shapes.
"""
from __future__                   import annotations

from copy                         import deepcopy
from enum                         import Enum
from typing                       import Any, ClassVar, Generic, Hashable, Iterable, Mapping, \
                                         Optional as Nullable, Self, Union

from pyTooling                    import Cartesian2D
from pyTooling.Decorators         import export, readonly
from pyTooling.MetaClasses        import ExtendedType, abstractclass, abstractmethod
from pyTooling.Common             import getFullyQualifiedName
from pyTooling.Cartesian2D        import Coordinate, Point2D, BaseVector2D, Offset2D, BoundingBox2D, Element2D, \
                                         Segment2D, Shapes, AlreadyOwnedError, SweepDirection
from pyTooling.Cartesian2D.Groups import Group2D, Canvas2D, Container2DMixin, YAxisDirection


@export
class TextAlignment(Enum):
	"""Horizontal alignment of the lines of a text at the text's position."""

	Left =   0  #: Every line starts at the position.
	Center = 1  #: Every line is centered on the position.
	Right =  2  #: Every line ends at the position.


@export
class VerticalAnchor(Enum):
	"""Vertical point of a text, which is placed at the text's position."""

	Top =      0  #: The top of the text, the top of its first line.
	Middle =   1  #: The middle of the text, halfway between its top and bottom.
	Baseline = 2  #: The baseline of the first line.
	Bottom =   3  #: The bottom of the text, the bottom of its last line.


@export
class LineStyle(Enum):
	"""Pattern of a line or an outline."""

	Solid =  0  #: A continuous line.
	Dashed = 1  #: A line of dashes.
	Dotted = 2  #: A line of dots.


@export
class FontStyle(Enum):
	"""Posture of the letters of a font."""

	Upright = 0  #: Upright letters.
	Italic =  1  #: Letters of the font's italic design.
	Slanted = 2  #: Upright letters, slanted to the right (oblique).


@export
@abstractclass
class Color(metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of all colors.

	A color is given in a color system, like red, green and blue components (:class:`RGBAColor`). A renderer converts any
	color to red, green, blue and opacity by :meth:`ToRGBA`.

	A derived class implements :meth:`ToRGBA`.
	"""

	@abstractmethod
	def ToRGBA(self) -> RGBAColor:
		"""
		Convert the color to red, green and blue components and an opacity.

		:returns: The color as an RGBA color.
		"""


@export
class RGBAColor(Color):
	"""
	A color as red, green and blue component and an opacity (alpha).

	The components are integers from 0 to 255, the opacity is a number from ``0.0`` (transparent) to ``1.0`` (opaque).
	"""

	_red:   int    #: Red component, 0 to 255.
	_green: int    #: Green component, 0 to 255.
	_blue:  int    #: Blue component, 0 to 255.
	_alpha: float  #: Opacity, 0.0 (transparent) to 1.0 (opaque).

	def __init__(self, red: int, green: int, blue: int, alpha: float = 1.0) -> None:
		"""
		Initializes an RGBA color from its components.

		:param red:         Red component, 0 to 255.
		:param green:       Green component, 0 to 255.
		:param blue:        Blue component, 0 to 255.
		:param alpha:       Optional, opacity from ``0.0`` (transparent) to ``1.0`` (opaque). Default: ``1.0``.
		:raises ValueError: If parameter 'red' is None.
		:raises TypeError:  If parameter 'red' is not of type :class:`int`.
		:raises ValueError: If parameter 'red' is out of range 0..255.
		:raises ValueError: If parameter 'green' is None.
		:raises TypeError:  If parameter 'green' is not of type :class:`int`.
		:raises ValueError: If parameter 'green' is out of range 0..255.
		:raises ValueError: If parameter 'blue' is None.
		:raises TypeError:  If parameter 'blue' is not of type :class:`int`.
		:raises ValueError: If parameter 'blue' is out of range 0..255.
		:raises ValueError: If parameter 'alpha' is None.
		:raises TypeError:  If parameter 'alpha' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'alpha' is out of range 0.0..1.0.
		"""
		super().__init__()

		for name, component in (
			("red",   red),
			("green", green),
			("blue",  blue)
		):
			if component is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(component, int):
				ex = TypeError(f"Parameter '{name}' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(component)}'.")
				raise ex
			elif not 0 <= component <= 255:
				ex = ValueError(f"Parameter '{name}' is out of range 0..255.")
				ex.add_note(f"Got value '{component}'.")
				raise ex

		if alpha is None:
			raise ValueError("Parameter 'alpha' is None.")
		elif not isinstance(alpha, (int, float)):
			ex = TypeError("Parameter 'alpha' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alpha)}'.")
			raise ex
		elif not 0.0 <= alpha <= 1.0:
			ex = ValueError("Parameter 'alpha' is out of range 0.0..1.0.")
			ex.add_note(f"Got value '{alpha}'.")
			raise ex

		self._red =   red
		self._green = green
		self._blue =  blue
		self._alpha = alpha

	@classmethod
	def Parse(cls, value: str) -> Self:
		"""
		Create an RGBA color from a hexadecimal color string.

		The string is ``#rrggbb`` or ``#rrggbbaa``, with two hexadecimal digits per component, as in CSS and SVG. The
		opacity ``aa`` is scaled from 0..255 to 0.0..1.0; without it, the color is opaque.

		:param value:       The color string.
		:returns:           A new RGBA color.
		:raises ValueError: If parameter 'value' is None.
		:raises TypeError:  If parameter 'value' is not of type :class:`str`.
		:raises ValueError: If parameter 'value' is not of the form ``#rrggbb`` or ``#rrggbbaa``.
		"""
		if value is None:
			raise ValueError("Parameter 'value' is None.")
		elif not isinstance(value, str):
			ex = TypeError("Parameter 'value' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex
		elif (l := len(value)) not in (7, 9) or value[0] != "#" or not set(value[1:]).issubset("0123456789abcdefABCDEF"):
			ex = ValueError("Parameter 'value' is not of the form '#rrggbb' or '#rrggbbaa'.")
			ex.add_note(f"Got value '{value}'.")
			raise ex

		alpha = 1.0 if l == 7 else int(value[7:9], 16) / 255
		return cls(int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16), alpha)

	@readonly
	def Red(self) -> int:
		"""
		Read-only property to access the red component (:attr:`_red`).

		:returns: The red component, 0 to 255.
		"""
		return self._red

	@readonly
	def Green(self) -> int:
		"""
		Read-only property to access the green component (:attr:`_green`).

		:returns: The green component, 0 to 255.
		"""
		return self._green

	@readonly
	def Blue(self) -> int:
		"""
		Read-only property to access the blue component (:attr:`_blue`).

		:returns: The blue component, 0 to 255.
		"""
		return self._blue

	@readonly
	def Alpha(self) -> float:
		"""
		Read-only property to access the opacity (:attr:`_alpha`).

		:returns: The opacity, 0.0 (transparent) to 1.0 (opaque).
		"""
		return self._alpha

	def ToRGBA(self) -> RGBAColor:
		"""
		Convert the color to red, green and blue components and an opacity.

		:returns: The color itself.
		"""
		return self

	def ToHex(self) -> str:
		"""
		Convert the color to a hexadecimal color string.

		The opacity is written with two hexadecimal digits, so it's rounded to a multiple of 1/255.

		:returns: ``#rrggbb`` for an opaque color, else ``#rrggbbaa`` with the opacity scaled to 0..255.
		"""
		if self._alpha == 1.0:
			return f"#{self._red:02x}{self._green:02x}{self._blue:02x}"

		return f"#{self._red:02x}{self._green:02x}{self._blue:02x}{round(self._alpha * 255):02x}"

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two RGBA colors for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both colors have the same components and opacity.
		:raises TypeError: If the second operand is not of type :class:`RGBAColor`.
		"""
		if not isinstance(other, RGBAColor):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: RGBAColor")
			raise ex

		return (
			self._red == other._red and self._green == other._green and
			self._blue == other._blue and self._alpha == other._alpha
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two RGBA colors for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the colors differ in a component or the opacity.
		:raises TypeError: If the second operand is not of type :class:`RGBAColor`.
		"""
		if not isinstance(other, RGBAColor):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: RGBAColor")
			raise ex

		return (
			self._red != other._red or self._green != other._green or
			self._blue != other._blue or self._alpha != other._alpha
		)

	def __hash__(self) -> int:
		"""
		Returns a hash of the color's components and opacity, so equal colors have the same hash.

		:returns: The hash value.
		"""
		return hash((self._red, self._green, self._blue, self._alpha))

	def __repr__(self) -> str:
		"""
		Returns the color's string representation.

		:returns: The string representation of the color.
		"""
		return f"RGBAColor({self._red}, {self._green}, {self._blue}, {self._alpha})"

	def __str__(self) -> str:
		"""
		Returns the color's string equivalent as a hexadecimal color string.

		:returns: The color as a hexadecimal color string (:meth:`ToHex`).
		"""
		return self.ToHex()


@export
class Stroke(metaclass=ExtendedType, slots=True):
	"""The style of a line or an outline: its width, color and pattern."""

	_width:     float      #: Width of the line.
	_color:     Color      #: Color of the line.
	_lineStyle: LineStyle  #: Pattern of the line.

	def __init__(self, width: float, color: Color, lineStyle: LineStyle = LineStyle.Solid) -> None:
		"""
		Initializes a stroke from its width, color and pattern.

		:param width:       Width of the line, in the unit of the coordinates.
		:param color:       Color of the line, in any color system.
		:param lineStyle:   Optional, pattern of the line. Default: ``LineStyle.Solid``.
		:raises ValueError: If parameter 'width' is None.
		:raises TypeError:  If parameter 'width' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'width' isn't positive.
		:raises ValueError: If parameter 'color' is None.
		:raises TypeError:  If parameter 'color' is not of type :class:`Color`.
		:raises ValueError: If parameter 'lineStyle' is None.
		:raises TypeError:  If parameter 'lineStyle' is not of type :class:`LineStyle`.
		"""
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex
		elif width <= 0:
			ex = ValueError("Parameter 'width' isn't positive.")
			ex.add_note(f"Got value '{width}'.")
			raise ex

		if color is None:
			raise ValueError("Parameter 'color' is None.")
		elif not isinstance(color, Color):
			ex = TypeError("Parameter 'color' is not of type 'Color'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(color)}'.")
			raise ex

		if lineStyle is None:
			raise ValueError("Parameter 'lineStyle' is None.")
		elif not isinstance(lineStyle, LineStyle):
			ex = TypeError("Parameter 'lineStyle' is not of type 'LineStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(lineStyle)}'.")
			raise ex

		self._width =     width
		self._color =     color
		self._lineStyle = lineStyle

	@readonly
	def Width(self) -> float:
		"""
		Read-only property to access the width of the line (:attr:`_width`).

		:returns: The width, in the unit of the coordinates.
		"""
		return self._width

	@readonly
	def Color(self) -> Color:
		"""
		Read-only property to access the color of the line (:attr:`_color`).

		:returns: The line's color.
		"""
		return self._color

	@readonly
	def LineStyle(self) -> LineStyle:
		"""
		Read-only property to access the pattern of the line (:attr:`_lineStyle`).

		:returns: The line's pattern.
		"""
		return self._lineStyle

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two strokes for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both strokes have the same width, color and pattern.
		:raises TypeError: If the second operand is not of type :class:`Stroke`.
		"""
		if not isinstance(other, Stroke):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Stroke")
			raise ex

		return self._width == other._width and self._color == other._color and self._lineStyle is other._lineStyle

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two strokes for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the strokes differ in width, color or pattern.
		:raises TypeError: If the second operand is not of type :class:`Stroke`.
		"""
		if not isinstance(other, Stroke):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Stroke")
			raise ex

		return self._width != other._width or self._color != other._color or self._lineStyle is not other._lineStyle

	def __hash__(self) -> int:
		"""
		Returns a hash of the stroke's width, color and pattern, so equal strokes have the same hash.

		:returns: The hash value.
		"""
		return hash((self._width, self._color, self._lineStyle))

	def __repr__(self) -> str:
		"""
		Returns the stroke's string representation.

		:returns: The string representation of the stroke.
		"""
		return f"Stroke({self._width}, {self._color!r}, {self._lineStyle})"


@export
class Fill(metaclass=ExtendedType, slots=True):
	"""The style of an area: its color."""

	_color: Color  #: Color of the area.

	def __init__(self, color: Color) -> None:
		"""
		Initializes a fill from its color.

		:param color:       Color of the area, in any color system.
		:raises ValueError: If parameter 'color' is None.
		:raises TypeError:  If parameter 'color' is not of type :class:`Color`.
		"""
		if color is None:
			raise ValueError("Parameter 'color' is None.")
		elif not isinstance(color, Color):
			ex = TypeError("Parameter 'color' is not of type 'Color'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(color)}'.")
			raise ex

		self._color = color

	@readonly
	def Color(self) -> Color:
		"""
		Read-only property to access the color of the area (:attr:`_color`).

		:returns: The area's color.
		"""
		return self._color

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two fills for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both fills have the same color.
		:raises TypeError: If the second operand is not of type :class:`Fill`.
		"""
		if not isinstance(other, Fill):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Fill")
			raise ex

		return self._color == other._color

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two fills for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the fills differ in color.
		:raises TypeError: If the second operand is not of type :class:`Fill`.
		"""
		if not isinstance(other, Fill):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Fill")
			raise ex

		return self._color != other._color

	def __hash__(self) -> int:
		"""
		Returns a hash of the fill's color, so equal fills have the same hash.

		:returns: The hash value.
		"""
		return hash(self._color)

	def __repr__(self) -> str:
		"""
		Returns the fill's string representation.

		:returns: The string representation of the fill.
		"""
		return f"Fill({self._color!r})"


@export
class Font(metaclass=ExtendedType, slots=True):
	"""
	The font of a text: its family, size and style.

	The family is a font name or a generic family, as in CSS: for example ``"DejaVu Sans Mono"`` or ``"monospace"``. A
	renderer maps it to its format.

	Bold, small caps and the posture of the letters (:class:`FontStyle`) are independent of each other, as in CSS.

	The average width of a character, :attr:`CharacterWidth`, is used to estimate the width of a text.
	"""

	_family:         str        #: Font name or generic font family.
	_size:           float      #: Font size in points.
	_bold:           bool       #: If ``True``, the font is bold.
	_smallCaps:      bool       #: If ``True``, the lower-case letters are small capitals.
	_fontStyle:      FontStyle  #: Posture of the letters.
	_characterWidth: float      #: Average advance width of a character, as a factor of the font size.

	def __init__(
		self,
		family:         str,
		size:           float,
		*,
		bold:           bool = False,
		smallCaps:      bool = False,
		fontStyle:      FontStyle = FontStyle.Upright,
		characterWidth: float = 0.6
	) -> None:
		"""
		Initializes a font from its family, size and style.

		:param family:         Font name or generic font family.
		:param size:           Font size in points.
		:param bold:           Optional, if ``True``, the font is bold. Default: ``False``.
		:param smallCaps:      Optional, if ``True``, the lower-case letters are small capitals. Default: ``False``.
		:param fontStyle:      Optional, posture of the letters. Default: ``FontStyle.Upright``.
		:param characterWidth: Optional, average advance width of a character, as a factor of the font size. Default:
		                       ``0.6``, the advance width of common monospace fonts.
		:raises ValueError:    If parameter 'family' is None.
		:raises TypeError:     If parameter 'family' is not of type :class:`str`.
		:raises ValueError:    If parameter 'family' is empty.
		:raises ValueError:    If parameter 'size' is None.
		:raises TypeError:     If parameter 'size' is not of type :class:`float` or :class:`int`.
		:raises ValueError:    If parameter 'size' isn't positive.
		:raises ValueError:    If parameter 'bold' is None.
		:raises TypeError:     If parameter 'bold' is not of type :class:`bool`.
		:raises ValueError:    If parameter 'smallCaps' is None.
		:raises TypeError:     If parameter 'smallCaps' is not of type :class:`bool`.
		:raises ValueError:    If parameter 'fontStyle' is None.
		:raises TypeError:     If parameter 'fontStyle' is not of type :class:`FontStyle`.
		:raises ValueError:    If parameter 'characterWidth' is None.
		:raises TypeError:     If parameter 'characterWidth' is not of type :class:`float` or :class:`int`.
		:raises ValueError:    If parameter 'characterWidth' isn't positive.
		"""
		if family is None:
			raise ValueError("Parameter 'family' is None.")
		elif not isinstance(family, str):
			ex = TypeError("Parameter 'family' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(family)}'.")
			raise ex
		elif family == "":
			raise ValueError("Parameter 'family' is empty.")

		if size is None:
			raise ValueError("Parameter 'size' is None.")
		elif not isinstance(size, (int, float)):
			ex = TypeError("Parameter 'size' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(size)}'.")
			raise ex
		elif size <= 0:
			ex = ValueError("Parameter 'size' isn't positive.")
			ex.add_note(f"Got value '{size}'.")
			raise ex

		for name, flag in (
			("bold",      bold),
			("smallCaps", smallCaps)
		):
			if flag is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(flag, bool):
				ex = TypeError(f"Parameter '{name}' is not of type 'bool'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(flag)}'.")
				raise ex

		if fontStyle is None:
			raise ValueError("Parameter 'fontStyle' is None.")
		elif not isinstance(fontStyle, FontStyle):
			ex = TypeError("Parameter 'fontStyle' is not of type 'FontStyle'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(fontStyle)}'.")
			raise ex

		if characterWidth is None:
			raise ValueError("Parameter 'characterWidth' is None.")
		elif not isinstance(characterWidth, (int, float)):
			ex = TypeError("Parameter 'characterWidth' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(characterWidth)}'.")
			raise ex
		elif characterWidth <= 0:
			ex = ValueError("Parameter 'characterWidth' isn't positive.")
			ex.add_note(f"Got value '{characterWidth}'.")
			raise ex

		self._family =         family
		self._size =           size
		self._bold =           bold
		self._smallCaps =      smallCaps
		self._fontStyle =      fontStyle
		self._characterWidth = characterWidth

	@readonly
	def Family(self) -> str:
		"""
		Read-only property to access the font name or generic font family (:attr:`_family`).

		:returns: The font's family.
		"""
		return self._family

	@readonly
	def Size(self) -> float:
		"""
		Read-only property to access the font size (:attr:`_size`).

		:returns: The font size in points.
		"""
		return self._size

	@readonly
	def Bold(self) -> bool:
		"""
		Read-only property to access, if the font is bold (:attr:`_bold`).

		:returns: ``True``, if the font is bold.
		"""
		return self._bold

	@readonly
	def SmallCaps(self) -> bool:
		"""
		Read-only property to access, if the lower-case letters are small capitals (:attr:`_smallCaps`).

		:returns: ``True``, if the lower-case letters are small capitals.
		"""
		return self._smallCaps

	@readonly
	def FontStyle(self) -> FontStyle:
		"""
		Read-only property to access the posture of the letters (:attr:`_fontStyle`).

		:returns: The font's posture.
		"""
		return self._fontStyle

	@readonly
	def CharacterWidth(self) -> float:
		"""
		Read-only property to access the average advance width of a character (:attr:`_characterWidth`).

		:returns: The average width of a character, as a factor of the font size.
		"""
		return self._characterWidth

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two fonts for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both fonts have the same family, size, style and character width.
		:raises TypeError: If the second operand is not of type :class:`Font`.
		"""
		if not isinstance(other, Font):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Font")
			raise ex

		return (
			self._family == other._family and self._size == other._size and self._bold is other._bold and
			self._smallCaps is other._smallCaps and self._fontStyle is other._fontStyle and
			self._characterWidth == other._characterWidth
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two fonts for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the fonts differ in family, size, style or character width.
		:raises TypeError: If the second operand is not of type :class:`Font`.
		"""
		if not isinstance(other, Font):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Font")
			raise ex

		return (
			self._family != other._family or self._size != other._size or self._bold is not other._bold or
			self._smallCaps is not other._smallCaps or self._fontStyle is not other._fontStyle or
			self._characterWidth != other._characterWidth
		)

	def __hash__(self) -> int:
		"""
		Returns a hash of the font's family, size, style and character width, so equal fonts have the same hash.

		:returns: The hash value.
		"""
		return hash((self._family, self._size, self._bold, self._smallCaps, self._fontStyle, self._characterWidth))

	def __repr__(self) -> str:
		"""
		Returns the font's string representation.

		:returns: The string representation of the font.
		"""
		return (
			f"Font({self._family!r}, {self._size}, bold={self._bold}, smallCaps={self._smallCaps}, "
			f"fontStyle={self._fontStyle}, characterWidth={self._characterWidth})"
		)


@export
class StrokeMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for drawable elements with a line or an outline, drawn with a :class:`Stroke`.

	Without a stroke, the element has no line or outline.
	"""

	_stroke: Nullable[Stroke]  #: Style of the line or outline, or ``None`` for no outline.

	def __init__(self, *, stroke: Nullable[Stroke] = None) -> None:
		"""
		Initializes the style of the line or outline.

		:param stroke:     Optional, style of the line or outline. Default: ``None``, no outline.
		:raises TypeError: If parameter 'stroke' is not of type :class:`Stroke`.
		"""
		if stroke is not None and not isinstance(stroke, Stroke):
			ex = TypeError("Parameter 'stroke' is not of type 'Stroke'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(stroke)}'.")
			raise ex

		self._stroke = stroke

	@property
	def Stroke(self) -> Nullable[Stroke]:
		"""
		Property to access the style of the line or outline (:attr:`_stroke`).

		Assigning ``None`` removes the outline.

		:returns:          The stroke, or ``None``, if the element has no outline.
		:raises TypeError: If an assigned value is not of type :class:`Stroke`.
		"""
		return self._stroke

	@Stroke.setter
	def Stroke(self, stroke: Nullable[Stroke]) -> None:
		if stroke is not None and not isinstance(stroke, Stroke):
			ex = TypeError("Parameter 'stroke' is not of type 'Stroke'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(stroke)}'.")
			raise ex

		self._stroke = stroke


@export
class StyleMixin(StrokeMixin, mixin=True):
	"""
	Mixin-class for drawable elements with an area, drawn with an outline (:class:`Stroke`) and a :class:`Fill`.

	Without a fill, the area is transparent.
	"""

	_fill: Nullable[Fill]  #: Style of the area, or ``None`` for a transparent area.

	def __init__(self, *, stroke: Nullable[Stroke] = None, fill: Nullable[Fill] = None) -> None:
		"""
		Initializes the styles of the outline and the area.

		:param stroke:     Optional, style of the outline. Default: ``None``, no outline.
		:param fill:       Optional, style of the area. Default: ``None``, transparent.
		:raises TypeError: If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError: If parameter 'fill' is not of type :class:`Fill`.
		"""
		super().__init__(stroke=stroke)

		if fill is not None and not isinstance(fill, Fill):
			ex = TypeError("Parameter 'fill' is not of type 'Fill'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(fill)}'.")
			raise ex

		self._fill = fill

	@property
	def Fill(self) -> Nullable[Fill]:
		"""
		Property to access the style of the area (:attr:`_fill`).

		Assigning ``None`` makes the area transparent.

		:returns:          The fill, or ``None``, if the area is transparent.
		:raises TypeError: If an assigned value is not of type :class:`Fill`.
		"""
		return self._fill

	@Fill.setter
	def Fill(self, fill: Nullable[Fill]) -> None:
		if fill is not None and not isinstance(fill, Fill):
			ex = TypeError("Parameter 'fill' is not of type 'Fill'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(fill)}'.")
			raise ex

		self._fill = fill


@export
class LineSegment2D(Cartesian2D.LineSegment2D[Coordinate], StrokeMixin, Generic[Coordinate]):
	"""
	A drawable line segment: a :class:`pyTooling.Cartesian2D.LineSegment2D` drawn with a :class:`Stroke`.

	A line has no area, so it has no fill.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable line segment from its start and end point and its style.

		:param start:                Start point of the line segment.
		:param end:                  End point of the line segment.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param stroke:               Optional, style of the line. Default: ``None``, no line.
		:param value:                Optional, value of the line segment. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the group or canvas the line segment is added to. Default: ``None``, no
		                             parent.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is ``False``.
		                             |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			start,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StrokeMixin.__init__(self, stroke=stroke)
		except TypeError:
			self._start._parent = None
			self._end._parent =   None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable line segment as a copy of this line segment.

		The copy holds copies of the start and end point, and the same stroke. It references the same :attr:`Value` and
		holds a shallow copy of the key-value-pairs.

		:returns: Copy of this line segment.
		"""
		return self.__class__(self._start, self._end, stroke=self._stroke, value=self._value, keyValuePairs=self._dict)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this line segment for :func:`copy.deepcopy`.

		The copy holds copies of the start and end point, and the same stroke. It holds deep copies of the :attr:`Value`
		and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this line segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			stroke=self._stroke,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


LineSegment2D._PARENT_TYPE = (Group2D, Canvas2D)


@export
class ArcSegment2D(Cartesian2D.ArcSegment2D[Coordinate], StrokeMixin, Generic[Coordinate]):
	"""
	A drawable arc segment: a :class:`pyTooling.Cartesian2D.ArcSegment2D` drawn with a :class:`Stroke`.

	An arc has no area, so it has no fill.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		center:        Nullable[Point2D[Coordinate]] = None,
		direction:     Nullable[SweepDirection] = None,
		arcPoint:      Nullable[Point2D[Coordinate]] = None,
		chordPosition: Nullable[float] = None,
		height:        Nullable[Coordinate] = None,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable arc segment from its start and end point, one group of parameters for its circle and its
		style.

		Exactly one group of parameters describes the arc's circle, as for a :class:`pyTooling.Cartesian2D.ArcSegment2D`:
		``center`` and ``direction``, or ``arcPoint``, or ``height`` and optionally ``chordPosition``.

		:param start:                Start point of the arc.
		:param end:                  End point of the arc.
		:param center:               Optional, center point of the arc's circle. Default: ``None``.
		:param direction:            Optional, direction, in which the arc sweeps from its start point to its end point.
		                             Default: ``None``.
		:param arcPoint:             Optional, a point of the arc between the start and the end point. Default: ``None``.
		:param chordPosition:        Optional, the root point's position on the chord, as a fraction from 0 (start point)
		                             to 1 (end point). Default: ``None``, which uses ``0.5``, the chord's midpoint.
		:param height:               Optional, the arc's signed distance from the chord at the root point. Default:
		                             ``None``.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param stroke:               Optional, style of the line. Default: ``None``, no line.
		:param value:                Optional, value of the arc. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the group or canvas the arc is added to. Default: ``None``, no parent.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is ``False``.
		                             |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is at the position of parameter 'start'. |br|
		                             An arc needs a chord from the start point to the end point.
		:raises ValueError:          If parameter 'center' is None, while 'direction' is given.
		:raises TypeError:           If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:          If parameter 'center' is at the position of parameter 'start'.
		:raises ValueError:          If parameter 'center' has another distance to parameter 'end' than to parameter
		                             'start'.
		:raises ValueError:          If parameter 'direction' is None, while 'center' is given.
		:raises TypeError:           If parameter 'direction' is not of type
		                             :class:`~pyTooling.Cartesian2D.SweepDirection`.
		:raises TypeError:           If parameter 'arcPoint' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:          If parameter 'arcPoint' is on the line through parameter 'start' and parameter 'end'.
		:raises TypeError:           If parameter 'chordPosition' is not of type :class:`float`.
		:raises ValueError:          If parameter 'chordPosition' is out of range 0..1.
		:raises ValueError:          If parameter 'height' is None, while 'chordPosition' is given.
		:raises TypeError:           If parameter 'height' is not of type :class:`float` or :class:`int`.
		:raises ValueError:          If parameter 'height' is 0.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:          If no group of parameters for the circle is given. |br|
		                             Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally
		                             'chordPosition'.
		:raises ValueError:          If parameters of more than one group for the circle are given. |br|
		                             Give 'center' and 'direction', or 'arcPoint', or 'height' and optionally
		                             'chordPosition'.
		"""
		super().__init__(
			start,
			end,
			center=center,
			direction=direction,
			arcPoint=arcPoint,
			chordPosition=chordPosition,
			height=height,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StrokeMixin.__init__(self, stroke=stroke)
		except TypeError:
			self._start._parent = None
			self._end._parent =   None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable arc segment as a copy of this arc segment.

		The copy holds copies of the start and end point, has the same chord position and height, and the same stroke. It
		references the same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this arc segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			chordPosition=self._chordPosition,
			height=self.Height,
			stroke=self._stroke,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this drawable arc segment for :func:`copy.deepcopy`.

		The copy holds copies of the start and end point, has the same chord position, height and stroke, and deep copies
		of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this arc segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			chordPosition=self._chordPosition,
			height=self.Height,
			stroke=self._stroke,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


ArcSegment2D._PARENT_TYPE = (Group2D, Canvas2D)


@export
class QuadraticBezierSegment2D(Cartesian2D.QuadraticBezierSegment2D[Coordinate], StrokeMixin, Generic[Coordinate]):
	"""
	A drawable quadratic Bezier curve segment: a :class:`pyTooling.Cartesian2D.QuadraticBezierSegment2D` drawn with a
	:class:`Stroke`.

	A curve has no area, so it has no fill.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		controlPoint:  Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable quadratic Bezier curve segment from its start point, control point, end point and style.

		:param start:                Start point of the curve.
		:param controlPoint:         Control point of the curve.
		:param end:                  End point of the curve.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param stroke:               Optional, style of the line. Default: ``None``, no line.
		:param value:                Optional, value of the curve. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the group or canvas the curve is added to. Default: ``None``, no parent.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is ``False``.
		                             |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'controlPoint' is None.
		:raises TypeError:           If parameter 'controlPoint' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint' is the same point as parameter 'start' or 'end', while
		                             'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			start,
			controlPoint,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StrokeMixin.__init__(self, stroke=stroke)
		except TypeError:
			for point in (self._start, *self._controlPoints, self._end):
				point._parent = None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable quadratic Bezier curve segment as a copy of this one.

		The copy holds copies of the start point, control point and end point, and the same stroke. It references the
		same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this quadratic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._end,
			stroke=self._stroke,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this drawable quadratic Bezier curve segment for :func:`copy.deepcopy`.

		The copy holds copies of the start point, control point and end point, the same stroke, and deep copies of the
		:attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this quadratic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._end,
			stroke=self._stroke,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


QuadraticBezierSegment2D._PARENT_TYPE = (Group2D, Canvas2D)


@export
class CubicBezierSegment2D(Cartesian2D.CubicBezierSegment2D[Coordinate], StrokeMixin, Generic[Coordinate]):
	"""
	A drawable cubic Bezier curve segment: a :class:`pyTooling.Cartesian2D.CubicBezierSegment2D` drawn with a
	:class:`Stroke`.

	A curve has no area, so it has no fill.
	"""

	def __init__(
		self,
		start:         Point2D[Coordinate],
		controlPoint1: Point2D[Coordinate],
		controlPoint2: Point2D[Coordinate],
		end:           Point2D[Coordinate],
		*,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable cubic Bezier curve segment from its start point, two control points, end point and style.

		:param start:                Start point of the curve.
		:param controlPoint1:        First control point of the curve, next to the start point.
		:param controlPoint2:        Second control point of the curve, next to the end point.
		:param end:                  End point of the curve.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param stroke:               Optional, style of the line. Default: ``None``, no line.
		:param value:                Optional, value of the curve. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the group or canvas the curve is added to. Default: ``None``, no parent.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is ``False``.
		                             |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'controlPoint1' is None.
		:raises TypeError:           If parameter 'controlPoint1' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint1' is the same point as parameter 'start' or 'end', while
		                             'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint1' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'controlPoint2' is None.
		:raises TypeError:           If parameter 'controlPoint2' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'controlPoint2' is the same point as parameter 'start', 'end' or
		                             'controlPoint1', while 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'controlPoint2' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                             :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			start,
			controlPoint1,
			controlPoint2,
			end,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StrokeMixin.__init__(self, stroke=stroke)
		except TypeError:
			for point in (self._start, *self._controlPoints, self._end):
				point._parent = None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable cubic Bezier curve segment as a copy of this one.

		The copy holds copies of the start point, both control points and the end point, and the same stroke. It
		references the same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this cubic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._controlPoints[1],
			self._end,
			stroke=self._stroke,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this drawable cubic Bezier curve segment for :func:`copy.deepcopy`.

		The copy holds copies of the start point, both control points and the end point, the same stroke, and deep copies
		of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this cubic Bezier curve segment.
		"""
		return self.__class__(
			self._start,
			self._controlPoints[0],
			self._controlPoints[1],
			self._end,
			stroke=self._stroke,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


CubicBezierSegment2D._PARENT_TYPE = (Group2D, Canvas2D)


@export
class Polygon(Shapes.Polygon[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable polygon: a :class:`pyTooling.Cartesian2D.Shapes.Polygon` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		points:        Iterable[Point2D[Coordinate]],
		*,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable polygon from its corners and its styles.

		:param points:                 Corners of the polygon.
		:param copyPoints:             Optional, if ``True``, the given points are copied instead of referenced. Default:
		                               ``True``.
		:param stroke:                 Optional, style of the outline. Default: ``None``, no outline.
		:param fill:                   Optional, style of the area. Default: ``None``, transparent.
		:param value:                  Optional, value of the polygon. Default: ``None``.
		:param keyValuePairs:          Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:                 Optional, the group or canvas the polygon is added to. Default: ``None``, no parent.
		:raises ValueError:            If parameter 'points' is None.
		:raises TypeError:             If parameter 'points' is not iterable.
		:raises ValueError:            If an element of parameter 'points' is None.
		:raises TypeError:             If an element of parameter 'points' is not of type
		                               :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:     If an element of parameter 'points' is owned by another element, while
		                               'copyPoints' is ``False``. |br|
		                               Use ``copyPoints=True`` to copy the point.
		:raises DuplicatePointError:   If an element of parameter 'points' is given twice, while 'copyPoints' is
		                               ``False``. |br|
		                               Use ``copyPoints=True`` to copy the points.
		:raises NotEnoughCornersError: If parameter 'points' has fewer than 3 points.
		:raises ValueError:            If parameter 'copyPoints' is None.
		:raises TypeError:             If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:             If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:             If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:             If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:             If parameter 'parent' is not of type
		                               :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                               :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			points,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StyleMixin.__init__(self, stroke=stroke, fill=fill)
		except TypeError:
			for point in self._points:
				point._parent = None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable polygon as a copy of this polygon.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. It references the same
		:attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this polygon.
		"""
		return self.__class__(
			self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this polygon for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. It holds deep copies of
		the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this polygon.
		"""
		return self.__class__(
			self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Trapezium(Shapes.Trapezium[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable trapezium: a :class:`pyTooling.Cartesian2D.Shapes.Trapezium` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable trapezium with 4 corners and its styles.

		:param p00:           First corner.
		:param p01:           Second corner.
		:param p11:           Third corner.
		:param p10:           Fourth corner.
		:param stroke:        Optional, style of the outline. Default: ``None``, no outline.
		:param fill:          Optional, style of the area. Default: ``None``, transparent.
		:param value:         Optional, value of the trapezium. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the trapezium is added to. Default: ``None``, no parent.
		:raises ValueError:   If parameter 'p00' is None.
		:raises TypeError:    If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p01' is None.
		:raises TypeError:    If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p11' is None.
		:raises TypeError:    If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p10' is None.
		:raises TypeError:    If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:    If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:    If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			p00,
			p01,
			p11,
			p10,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)
		StyleMixin.__init__(self, stroke=stroke, fill=fill)

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable trapezium as a copy of this trapezium.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. It references the same
		:attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this trapezium.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this trapezium for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. It holds deep copies of
		the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this trapezium.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Rectangle(Shapes.Rectangle[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable rectangle: a :class:`pyTooling.Cartesian2D.Shapes.Rectangle` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable rectangle with 4 corners and its styles.

		:param p00:           First corner.
		:param p01:           Second corner.
		:param p11:           Third corner.
		:param p10:           Fourth corner.
		:param stroke:        Optional, style of the outline. Default: ``None``, no outline.
		:param fill:          Optional, style of the area. Default: ``None``, transparent.
		:param value:         Optional, value of the rectangle. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the rectangle is added to. Default: ``None``, no parent.
		:raises ValueError:   If parameter 'p00' is None.
		:raises TypeError:    If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p01' is None.
		:raises TypeError:    If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p11' is None.
		:raises TypeError:    If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p10' is None.
		:raises TypeError:    If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:    If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:    If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:   If opposite edges have different lengths.
		:raises ValueError:   If two consecutive corners are the same point.
		:raises ValueError:   If an inner angle isn't 90 |degree|.
		"""
		super().__init__(
			p00,
			p01,
			p11,
			p10,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)
		StyleMixin.__init__(self, stroke=stroke, fill=fill)

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable rectangle as a copy of this rectangle.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. Its corners are checked
		again. It references the same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this rectangle.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this rectangle for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. Its corners are checked
		again. It holds deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this rectangle.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Square(Shapes.Square[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable square: a :class:`pyTooling.Cartesian2D.Shapes.Square` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		p00:           Point2D[Coordinate],
		p01:           Point2D[Coordinate],
		p11:           Point2D[Coordinate],
		p10:           Point2D[Coordinate],
		*,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable square with 4 corners and its styles.

		:param p00:           First corner.
		:param p01:           Second corner.
		:param p11:           Third corner.
		:param p10:           Fourth corner.
		:param stroke:        Optional, style of the outline. Default: ``None``, no outline.
		:param fill:          Optional, style of the area. Default: ``None``, transparent.
		:param value:         Optional, value of the square. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the square is added to. Default: ``None``, no parent.
		:raises ValueError:   If parameter 'p00' is None.
		:raises TypeError:    If parameter 'p00' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p01' is None.
		:raises TypeError:    If parameter 'p01' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p11' is None.
		:raises TypeError:    If parameter 'p11' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises ValueError:   If parameter 'p10' is None.
		:raises TypeError:    If parameter 'p10' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises TypeError:    If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:    If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		:raises ValueError:   If opposite edges have different lengths.
		:raises ValueError:   If two consecutive corners are the same point.
		:raises ValueError:   If an inner angle isn't 90 |degree|.
		:raises ValueError:   If adjacent edges have different lengths.
		"""
		super().__init__(
			p00,
			p01,
			p11,
			p10,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)
		StyleMixin.__init__(self, stroke=stroke, fill=fill)

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable square as a copy of this square.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. Its corners are checked
		again. It references the same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this square.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this square for :func:`copy.deepcopy`.

		The copy holds copies of the corners, shared by its edges, and the same stroke and fill. Its corners are checked
		again. It holds deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this square.
		"""
		return self.__class__(
			*self._points,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Circle(Shapes.Circle[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable circle: a :class:`pyTooling.Cartesian2D.Shapes.Circle` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		center:        Point2D[Coordinate],
		radius:        Coordinate,
		*,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable circle by its center, radius and styles.

		:param center:             Center point of the circle.
		:param radius:             Radius of the circle.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param stroke:             Optional, style of the outline. Default: ``None``, no outline.
		:param fill:               Optional, style of the area. Default: ``None``, transparent.
		:param value:              Optional, value of the circle. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas the circle is added to. Default: ``None``, no parent.
		:raises ValueError:        If parameter 'center' is None.
		:raises TypeError:         If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'center' is owned by another element, while 'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'radius' is None.
		:raises TypeError:         If parameter 'radius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'radius' isn't positive.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:         If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			center,
			radius,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StyleMixin.__init__(self, stroke=stroke, fill=fill)
		except TypeError:
			self._center._parent = None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable circle as a copy of this circle.

		The copy holds a copy of the center point, and the same stroke and fill. It references the same :attr:`Value` and
		holds a shallow copy of the key-value-pairs.

		:returns: Copy of this circle.
		"""
		return self.__class__(
			self._center,
			self._radius,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this circle for :func:`copy.deepcopy`.

		The copy holds a copy of the center point, and the same stroke and fill. It holds deep copies of the
		:attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this circle.
		"""
		return self.__class__(
			self._center,
			self._radius,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Ellipse(Shapes.Ellipse[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable ellipse: a :class:`pyTooling.Cartesian2D.Shapes.Ellipse` drawn with an outline and a fill.
	"""

	def __init__(
		self,
		center:        Point2D[Coordinate],
		firstRadius:   Coordinate,
		secondRadius:  Coordinate,
		*,
		direction:     Nullable[Offset2D[Coordinate]] = None,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable ellipse by its center, its two radii, the direction of its first axis and its styles.

		:param center:             Center point of the ellipse.
		:param firstRadius:        Radius of the ellipse along its first axis.
		:param secondRadius:       Radius of the ellipse along its second axis.
		:param direction:          Optional, direction of the first axis. Default: ``None``, the direction ``(1, 0)``.
		:param copyPoints:         Optional, if ``True``, the given center is copied instead of referenced. Default:
		                           ``True``.
		:param stroke:             Optional, style of the outline. Default: ``None``, no outline.
		:param fill:               Optional, style of the area. Default: ``None``, transparent.
		:param value:              Optional, value of the ellipse. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas the ellipse is added to. Default: ``None``, no parent.
		:raises ValueError:        If parameter 'center' is None.
		:raises TypeError:         If parameter 'center' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'center' is owned by another element, while 'copyPoints' is ``False``. |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'firstRadius' is None.
		:raises TypeError:         If parameter 'firstRadius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'firstRadius' isn't positive.
		:raises ValueError:        If parameter 'secondRadius' is None.
		:raises TypeError:         If parameter 'secondRadius' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'secondRadius' isn't positive.
		:raises TypeError:         If parameter 'direction' is not of type :class:`~pyTooling.Cartesian2D.Offset2D`.
		:raises ValueError:        If parameter 'direction' is a zero offset. |br|
		                           An ellipse needs a direction of its first axis.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:         If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:         If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			center,
			firstRadius,
			secondRadius,
			direction=direction,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StyleMixin.__init__(self, stroke=stroke, fill=fill)
		except TypeError:
			self._center._parent = None

			raise

		self.Parent = parent

	def Copy(self) -> Self:
		"""
		Create a new drawable ellipse as a copy of this ellipse.

		The copy holds a copy of the center point and of the direction, and the same stroke and fill. It references the
		same :attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this ellipse.
		"""
		return self.__class__(
			self._center,
			self._firstRadius,
			self._secondRadius,
			direction=self._direction,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this ellipse for :func:`copy.deepcopy`.

		The copy holds a copy of the center point and of the direction, and the same stroke and fill. It holds deep
		copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this ellipse.
		"""
		return self.__class__(
			self._center,
			self._firstRadius,
			self._secondRadius,
			direction=self._direction,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Path(Shapes.Path[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable path: a :class:`pyTooling.Cartesian2D.Shapes.Path` drawn with a :class:`Stroke`, and with a :class:`Fill`,
	if it is closed.

	An open path has no area, so it has no fill.
	"""

	def __init__(
		self,
		segments:      Iterable[Segment2D[Coordinate]],
		*,
		closed:        bool = False,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable path from its segments and its styles.

		:param segments:      Segments of the path, in drawing order.
		:param closed:        Optional, if ``True``, the last segment ends at the start point of the first segment.
		                      Default: ``False``.
		:param stroke:        Optional, style of the line or outline. Default: ``None``, no line.
		:param fill:          Optional, style of the area of a closed path. Default: ``None``, transparent.
		:param value:         Optional, value of the path. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group or canvas the path is added to. Default: ``None``, no parent.
		:raises ValueError:   If parameter 'segments' is None.
		:raises TypeError:    If parameter 'segments' is not iterable.
		:raises ValueError:   If an element of parameter 'segments' is None.
		:raises TypeError:    If an element of parameter 'segments' is not of type
		                      :class:`~pyTooling.Cartesian2D.Segment2D`.
		:raises ValueError:   If an element of parameter 'segments' doesn't start at the end point of the previous
		                      element.
		:raises ValueError:   If parameter 'segments' is empty.
		:raises ValueError:   If parameter 'closed' is None.
		:raises TypeError:    If parameter 'closed' is not of type :class:`bool`.
		:raises ValueError:   If parameter 'closed' is ``True``, while the last segment doesn't end at the start point of
		                      the first segment.
		:raises TypeError:    If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:    If parameter 'fill' is not of type :class:`Fill`.
		:raises ValueError:   If parameter 'fill' is given, while 'closed' is ``False``. |br|
		                      Only a closed path encloses an area.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                      :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			segments,
			closed=closed,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)
		StyleMixin.__init__(self, stroke=stroke, fill=fill)

		if fill is not None and not closed:
			ex = ValueError("Parameter 'fill' is given, while 'closed' is False.")
			ex.add_note("Only a closed path encloses an area.")
			raise ex

		self.Parent = parent

	@property
	def Fill(self) -> Nullable[Fill]:
		"""
		Property to access the style of the area of a closed path (:attr:`_fill`).

		Assigning ``None`` makes the area transparent.

		:returns:           The fill, or ``None``, if the area is transparent or the path is open.
		:raises TypeError:  If an assigned value is not of type :class:`Fill`.
		:raises ValueError: If a fill is assigned, while the path is open. |br|
		                    Only a closed path encloses an area.
		"""
		return self._fill

	@Fill.setter
	def Fill(self, fill: Nullable[Fill]) -> None:
		if fill is not None:
			if not isinstance(fill, Fill):
				ex = TypeError("Parameter 'fill' is not of type 'Fill'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(fill)}'.")
				raise ex
			elif not self._closed:
				ex = ValueError("Parameter 'fill' is given, while the path is open.")
				ex.add_note("Only a closed path encloses an area.")
				raise ex

		self._fill = fill

	def Copy(self) -> Self:
		"""
		Create a new drawable path as a copy of this path.

		The copy holds copies of all points, its edges share the copied joints, and it has the same stroke and fill. It
		references the same :attr:`Value` and holds a shallow copy of the key-value-pairs; so do its edges.

		:returns: Copy of this path.
		"""
		return self.__class__(
			self._segments,
			closed=self._closed,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this drawable path for :func:`copy.deepcopy`.

		The copy holds copies of all points, the same stroke and fill, and deep copies of the :attr:`Value` and the
		key-value-pairs. Its edges are copied as by :meth:`Copy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this path.
		"""
		return self.__class__(
			self._segments,
			closed=self._closed,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Polyline(Shapes.Polyline[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A drawable polyline: a :class:`pyTooling.Cartesian2D.Shapes.Polyline` drawn with a :class:`Stroke`, and with a
	:class:`Fill`, if it is closed.

	An open polyline has no area, so it has no fill.
	"""

	def __init__(
		self,
		points:        Iterable[Point2D[Coordinate]],
		*,
		closed:        bool = False,
		copyPoints:    bool = True,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = None,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a drawable polyline from its points and its styles.

		:param points:                 Points of the polyline.
		:param closed:                 Optional, if ``True``, the last point is connected back to the first point. Default:
		                               ``False``.
		:param copyPoints:             Optional, if ``True``, the given points are copied instead of referenced. Default:
		                               ``True``.
		:param stroke:                 Optional, style of the line or outline. Default: ``None``, no line.
		:param fill:                   Optional, style of the area of a closed polyline. Default: ``None``, transparent.
		:param value:                  Optional, value of the polyline. Default: ``None``.
		:param keyValuePairs:          Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:                 Optional, the group or canvas the polyline is added to. Default: ``None``, no
		                               parent.
		:raises ValueError:            If parameter 'points' is None.
		:raises TypeError:             If parameter 'points' is not iterable.
		:raises ValueError:            If an element of parameter 'points' is None.
		:raises TypeError:             If an element of parameter 'points' is not of type
		                               :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError:     If an element of parameter 'points' is owned by another element, while
		                               'copyPoints' is ``False``. |br|
		                               Use ``copyPoints=True`` to copy the point.
		:raises DuplicatePointError:   If an element of parameter 'points' is given twice, while 'copyPoints' is
		                               ``False``. |br|
		                               Use ``copyPoints=True`` to copy the points.
		:raises NotEnoughCornersError: If parameter 'points' has fewer than 2 points.
		:raises ValueError:            If parameter 'closed' is None.
		:raises TypeError:             If parameter 'closed' is not of type :class:`bool`.
		:raises NotEnoughCornersError: If parameter 'closed' is ``True``, while parameter 'points' has fewer than 3
		                               points.
		:raises ValueError:            If parameter 'copyPoints' is None.
		:raises TypeError:             If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:             If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:             If parameter 'fill' is not of type :class:`Fill`.
		:raises ValueError:            If parameter 'fill' is given, while 'closed' is ``False``. |br|
		                               Only a closed polyline encloses an area.
		:raises TypeError:             If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:             If parameter 'parent' is not of type
		                               :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                               :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(
			points,
			closed=closed,
			copyPoints=copyPoints,
			value=value,
			keyValuePairs=keyValuePairs,
			parent=None if isinstance(parent, Container2DMixin) else parent
		)

		try:
			StyleMixin.__init__(self, stroke=stroke, fill=fill)

			if fill is not None and not closed:
				ex = ValueError("Parameter 'fill' is given, while 'closed' is False.")
				ex.add_note("Only a closed polyline encloses an area.")
				raise ex
		except (TypeError, ValueError):
			for point in self._points:
				point._parent = None

			raise

		self.Parent = parent

	@property
	def Fill(self) -> Nullable[Fill]:
		"""
		Property to access the style of the area of a closed polyline (:attr:`_fill`).

		Assigning ``None`` makes the area transparent.

		:returns:           The fill, or ``None``, if the area is transparent or the polyline is open.
		:raises TypeError:  If an assigned value is not of type :class:`Fill`.
		:raises ValueError: If a fill is assigned, while the polyline is open. |br|
		                    Only a closed polyline encloses an area.
		"""
		return self._fill

	@Fill.setter
	def Fill(self, fill: Nullable[Fill]) -> None:
		if fill is not None:
			if not isinstance(fill, Fill):
				ex = TypeError("Parameter 'fill' is not of type 'Fill'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(fill)}'.")
				raise ex
			elif not self._closed:
				ex = ValueError("Parameter 'fill' is given, while the polyline is open.")
				ex.add_note("Only a closed polyline encloses an area.")
				raise ex

		self._fill = fill

	def Copy(self) -> Self:
		"""
		Create a new drawable polyline as a copy of this polyline.

		The copy holds copies of the points, shared by its edges, and the same stroke and fill. It references the same
		:attr:`Value` and holds a shallow copy of the key-value-pairs.

		:returns: Copy of this polyline.
		"""
		return self.__class__(
			self._points,
			closed=self._closed,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this drawable polyline for :func:`copy.deepcopy`.

		The copy holds copies of the points, the same stroke and fill, and deep copies of the :attr:`Value` and the
		key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this polyline.
		"""
		return self.__class__(
			self._points,
			closed=self._closed,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class Text(Element2D[Coordinate], StyleMixin, Generic[Coordinate]):
	"""
	A text of one or more lines, placed at a position.

	The lines are separated by newlines in :attr:`Content`. Each line is aligned at the position's x-coordinate by
	:attr:`Alignment`, and :attr:`Anchor` names the vertical point of the text at the position's y-coordinate.
	Consecutive baselines are :attr:`LineHeight` times the font size apart. The glyphs are drawn with :attr:`Fill`, black
	by default, an outline around them with :attr:`Stroke`.

	Top and bottom are those of the canvas holding the text: with the y-axis pointing down, the top of a text has its
	smallest y-coordinate. Without a canvas, the y-axis points up. Mirroring moves the position only: the glyphs aren't
	mirrored, and the alignment and the anchor stay.

	The text owns its position point, like a circle owns its center.
	"""

	_ASCENT: ClassVar[float] = 0.8  #: Height of a line above its baseline, as a factor of the font size.

	_position:   Point2D[Coordinate]  #: Position of the text.
	_content:    str                  #: The text, lines separated by newlines.
	_font:       Font                 #: Font of the text.
	_alignment:  TextAlignment        #: Horizontal alignment of the lines at the position.
	_anchor:     VerticalAnchor       #: Vertical point of the text at the position.
	_lineHeight: float                #: Distance of two baselines, as a factor of the font size.

	def __init__(
		self,
		position:      Point2D[Coordinate],
		content:       str,
		*,
		copyPoints:    bool = True,
		font:          Font = Font("sans-serif", 10),
		alignment:     TextAlignment = TextAlignment.Left,
		anchor:        VerticalAnchor = VerticalAnchor.Baseline,
		lineHeight:    float = 1.2,
		stroke:        Nullable[Stroke] = None,
		fill:          Nullable[Fill] = Fill(RGBAColor(0, 0, 0)),
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Union[Group2D[Coordinate], Canvas2D[Coordinate]]] = None
	) -> None:
		"""
		Initializes a text at a position.

		:param position:           Position of the text.
		:param content:            The text, lines separated by newlines.
		:param copyPoints:         Optional, if ``True``, the given position is copied instead of referenced. Default:
		                           ``True``.
		:param font:               Optional, font of the text. Default: ``Font("sans-serif", 10)``.
		:param alignment:          Optional, horizontal alignment of the lines at the position. Default:
		                           ``TextAlignment.Left``.
		:param anchor:             Optional, vertical point of the text at the position. Default:
		                           ``VerticalAnchor.Baseline``.
		:param lineHeight:         Optional, distance of two baselines, as a factor of the font size. Default: ``1.2``.
		:param stroke:             Optional, style of the glyphs' outline. Default: ``None``, no outline.
		:param fill:               Optional, style of the glyphs, or ``None`` for transparent glyphs. Default:
		                           ``Fill(RGBAColor(0, 0, 0))``, black.
		:param value:              Optional, value of the text. Default: ``None``.
		:param keyValuePairs:      Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:             Optional, the group or canvas the text is added to. Default: ``None``, no parent.
		:raises ValueError:        If parameter 'position' is None.
		:raises TypeError:         If parameter 'position' is not of type :class:`~pyTooling.Cartesian2D.Point2D`.
		:raises AlreadyOwnedError: If parameter 'position' is owned by another element, while 'copyPoints' is ``False``.
		                           |br|
		                           Use ``copyPoints=True`` to copy the point.
		:raises ValueError:        If parameter 'content' is None.
		:raises TypeError:         If parameter 'content' is not of type :class:`str`.
		:raises ValueError:        If parameter 'copyPoints' is None.
		:raises TypeError:         If parameter 'copyPoints' is not of type :class:`bool`.
		:raises ValueError:        If parameter 'font' is None.
		:raises TypeError:         If parameter 'font' is not of type :class:`Font`.
		:raises ValueError:        If parameter 'alignment' is None.
		:raises TypeError:         If parameter 'alignment' is not of type :class:`TextAlignment`.
		:raises ValueError:        If parameter 'anchor' is None.
		:raises TypeError:         If parameter 'anchor' is not of type :class:`VerticalAnchor`.
		:raises ValueError:        If parameter 'lineHeight' is None.
		:raises TypeError:         If parameter 'lineHeight' is not of type :class:`float` or :class:`int`.
		:raises ValueError:        If parameter 'lineHeight' isn't positive.
		:raises TypeError:         If parameter 'stroke' is not of type :class:`Stroke`.
		:raises TypeError:         If parameter 'fill' is not of type :class:`Fill`.
		:raises TypeError:         If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:         If parameter 'parent' is not of type :class:`~pyTooling.Cartesian2D.Groups.Group2D` or
		                           :class:`~pyTooling.Cartesian2D.Groups.Canvas2D`.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)
		StyleMixin.__init__(self, stroke=stroke, fill=fill)

		if position is None:
			raise ValueError("Parameter 'position' is None.")
		elif not isinstance(position, Point2D):
			ex = TypeError("Parameter 'position' is not of type 'Point2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(position)}'.")
			raise ex

		if content is None:
			raise ValueError("Parameter 'content' is None.")
		elif not isinstance(content, str):
			ex = TypeError("Parameter 'content' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(content)}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		if font is None:
			raise ValueError("Parameter 'font' is None.")
		elif not isinstance(font, Font):
			ex = TypeError("Parameter 'font' is not of type 'Font'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(font)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, TextAlignment):
			ex = TypeError("Parameter 'alignment' is not of type 'TextAlignment'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex

		if anchor is None:
			raise ValueError("Parameter 'anchor' is None.")
		elif not isinstance(anchor, VerticalAnchor):
			ex = TypeError("Parameter 'anchor' is not of type 'VerticalAnchor'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(anchor)}'.")
			raise ex

		if lineHeight is None:
			raise ValueError("Parameter 'lineHeight' is None.")
		elif not isinstance(lineHeight, (int, float)):
			ex = TypeError("Parameter 'lineHeight' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(lineHeight)}'.")
			raise ex
		elif lineHeight <= 0:
			ex = ValueError("Parameter 'lineHeight' isn't positive.")
			ex.add_note(f"Got value '{lineHeight}'.")
			raise ex

		if not copyPoints and position._parent is not None:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {position} owned by {position._parent!r}.")
			ex.add_note("Use 'copyPoints=True' to copy the point.")
			raise ex from ValueError("Parameter 'position' is owned by another element.")

		self._position =         position.Copy() if copyPoints else position
		self._content =          content
		self._font =             font
		self._alignment =        alignment
		self._anchor =           anchor
		self._lineHeight =       lineHeight
		self._position._parent = self

		self.Parent = parent

	@readonly
	def Position(self) -> Point2D[Coordinate]:
		"""
		Read-only property to access the text's position (:attr:`_position`).

		:returns: Position of the text.
		"""
		return self._position

	@property
	def Content(self) -> str:
		"""
		Property to access the text (:attr:`_content`).

		:returns:           The text, lines separated by newlines.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`str`.
		"""
		return self._content

	@Content.setter
	def Content(self, content: str) -> None:
		if content is None:
			raise ValueError("Parameter 'content' is None.")
		elif not isinstance(content, str):
			ex = TypeError("Parameter 'content' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(content)}'.")
			raise ex

		self._content = content

	@readonly
	def Lines(self) -> tuple[str, ...]:
		"""
		Read-only property to return the lines of the text.

		A text without a newline has one line.

		:returns: Tuple of lines, without the newlines.
		"""
		return tuple(self._content.split("\n"))

	@readonly
	def LineCount(self) -> int:
		"""
		Read-only property to return the number of lines of the text.

		:returns: Number of lines, at least 1.
		"""
		return self._content.count("\n") + 1

	@property
	def Font(self) -> Font:
		"""
		Property to access the font of the text (:attr:`_font`).

		:returns:           The text's font.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`Font`.
		"""
		return self._font

	@Font.setter
	def Font(self, font: Font) -> None:
		if font is None:
			raise ValueError("Parameter 'font' is None.")
		elif not isinstance(font, Font):
			ex = TypeError("Parameter 'font' is not of type 'Font'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(font)}'.")
			raise ex

		self._font = font

	@property
	def Alignment(self) -> TextAlignment:
		"""
		Property to access the horizontal alignment of the lines at the position (:attr:`_alignment`).

		:returns:           The lines' alignment.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`TextAlignment`.
		"""
		return self._alignment

	@Alignment.setter
	def Alignment(self, alignment: TextAlignment) -> None:
		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, TextAlignment):
			ex = TypeError("Parameter 'alignment' is not of type 'TextAlignment'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex

		self._alignment = alignment

	@property
	def Anchor(self) -> VerticalAnchor:
		"""
		Property to access the vertical point of the text at the position (:attr:`_anchor`).

		:returns:           The text's vertical anchor.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`VerticalAnchor`.
		"""
		return self._anchor

	@Anchor.setter
	def Anchor(self, anchor: VerticalAnchor) -> None:
		if anchor is None:
			raise ValueError("Parameter 'anchor' is None.")
		elif not isinstance(anchor, VerticalAnchor):
			ex = TypeError("Parameter 'anchor' is not of type 'VerticalAnchor'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(anchor)}'.")
			raise ex

		self._anchor = anchor

	@property
	def LineHeight(self) -> float:
		"""
		Property to access the distance of two baselines (:attr:`_lineHeight`).

		:returns:           The distance of two baselines, as a factor of the font size.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		:raises ValueError: If an assigned value isn't positive.
		"""
		return self._lineHeight

	@LineHeight.setter
	def LineHeight(self, lineHeight: float) -> None:
		if lineHeight is None:
			raise ValueError("Parameter 'lineHeight' is None.")
		elif not isinstance(lineHeight, (int, float)):
			ex = TypeError("Parameter 'lineHeight' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(lineHeight)}'.")
			raise ex
		elif lineHeight <= 0:
			ex = ValueError("Parameter 'lineHeight' isn't positive.")
			ex.add_note(f"Got value '{lineHeight}'.")
			raise ex

		self._lineHeight = lineHeight

	@readonly
	def BoundingBox(self) -> BoundingBox2D[float]:
		"""
		Read-only property to return an estimate of the smallest axis-aligned bounding box enclosing the text.

		The width is the number of characters of the longest line times the font's
		:attr:`~Font.CharacterWidth` and size. A line is one font size high, 0.8 of it above the baseline; the height of
		the text adds :attr:`LineHeight` times the font size for each further line. A renderer measuring the glyphs gets
		other values, for a proportional font especially.

		:returns: A new bounding box.
		"""
		size =   self._font._size
		width =  max(len(line) for line in self._content.split("\n")) * self._font._characterWidth * size
		height = size + self._content.count("\n") * self._lineHeight * size

		x = self._position._x
		if self._alignment is TextAlignment.Left:
			minX = x
		elif self._alignment is TextAlignment.Center:
			minX = x - width / 2
		else:
			minX = x - width

		if self._anchor is VerticalAnchor.Top:
			above = 0
		elif self._anchor is VerticalAnchor.Middle:
			above = height / 2
		elif self._anchor is VerticalAnchor.Baseline:
			above = self._ASCENT * size
		else:
			above = height

		frame = self.Frame
		while frame is not None and not isinstance(frame, Canvas2D):
			frame = frame.Frame

		y = self._position._y
		if frame is None or frame._direction is YAxisDirection.Up:
			return BoundingBox2D(minX, y + above - height, minX + width, y + above)

		return BoundingBox2D(minX, y - above, minX + width, y - above + height)

	def Move(self, offset: BaseVector2D[Coordinate]) -> None:
		"""
		Move the text by moving its position (inplace).

		:param offset:      The 2D-vector or 2D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`~pyTooling.Cartesian2D.BaseVector2D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, BaseVector2D):
			ex = TypeError("Parameter 'offset' is not of type 'BaseVector2D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._position += offset

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the text at a horizontal axis by mirroring its position (inplace).

		The glyphs aren't mirrored.

		:param twiceAxis: Twice the y-coordinate of the axis.
		"""
		self._position._y = twiceAxis - self._position._y

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the text at a vertical axis by mirroring its position (inplace).

		The glyphs aren't mirrored.

		:param twiceAxis: Twice the x-coordinate of the axis.
		"""
		self._position._x = twiceAxis - self._position._x

	def _MirrorAt(self, normal: Offset2D[float], distance: float) -> None:
		"""
		Mirror the text at a line by mirroring its position (inplace).

		The glyphs aren't mirrored, and the alignment and anchor stay.

		:param normal:   The normal of the line, of length 1.
		:param distance: The signed distance of the line from the frame's origin.
		"""
		self._position._MirrorAt(normal, distance)

	def Copy(self) -> Self:
		"""
		Create a new text as a copy of this text.

		The copy holds a copy of the position, and the same font and styles. It references the same :attr:`Value` and holds
		a shallow copy of the key-value-pairs.

		:returns: Copy of this text.
		"""
		return self.__class__(
			self._position,
			self._content,
			font=self._font,
			alignment=self._alignment,
			anchor=self._anchor,
			lineHeight=self._lineHeight,
			stroke=self._stroke,
			fill=self._fill,
			value=self._value,
			keyValuePairs=self._dict
		)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this text for :func:`copy.copy`.

		:returns: Copy of this text.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this text for :func:`copy.deepcopy`.

		The copy holds a copy of the position, and the same font and styles. It holds deep copies of the :attr:`Value`
		and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this text.
		"""
		return self.__class__(
			self._position,
			self._content,
			font=self._font,
			alignment=self._alignment,
			anchor=self._anchor,
			lineHeight=self._lineHeight,
			stroke=self._stroke,
			fill=self._fill,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)

	def __repr__(self) -> str:
		"""
		Returns the text's string representation.

		:returns: The string representation of the text.
		"""
		return f"Text({self._position}, {self._content!r})"

	def __str__(self) -> str:
		"""
		Returns the text's string equivalent.

		:returns: The text.
		"""
		return self._content
