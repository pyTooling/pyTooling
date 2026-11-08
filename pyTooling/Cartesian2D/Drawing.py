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
Styles for drawing 2D cartesian shapes: colors, strokes, fills and fonts.

The style classes are values: they can't be changed after creation, compare by value and can be shared by any number
of elements.

.. seealso::

   :mod:`pyTooling.Cartesian2D.Shapes`
      |rarr| The geometry of the shapes.
"""
from __future__            import annotations

from enum                  import Enum
from typing                import Any, Self

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName


@export
class LineStyle(Enum):
	"""Pattern of a line or an outline."""

	Solid =  0  #: A continuous line.
	Dashed = 1  #: A line of dashes.
	Dotted = 2  #: A line of dots.


@export
class Color(metaclass=ExtendedType, slots=True):
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
		Initializes a color from its components.

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
		Create a color from a hexadecimal color string.

		The string is ``#rrggbb`` or ``#rrggbbaa``, with two hexadecimal digits per component, as in CSS and SVG. The
		opacity ``aa`` is scaled from 0..255 to 0.0..1.0; without it, the color is opaque.

		:param value:       The color string.
		:returns:           A new color.
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
		elif len(value) not in (7, 9) or value[0] != "#" or not set(value[1:]).issubset("0123456789abcdefABCDEF"):
			ex = ValueError("Parameter 'value' is not of the form '#rrggbb' or '#rrggbbaa'.")
			ex.add_note(f"Got value '{value}'.")
			raise ex

		alpha = 1.0 if len(value) == 7 else int(value[7:9], 16) / 255
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

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two colors for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both colors have the same components and opacity.
		:raises TypeError: If the second operand is not of type :class:`Color`.
		"""
		if not isinstance(other, Color):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Color")
			raise ex

		return (
			self._red == other._red and self._green == other._green and
			self._blue == other._blue and self._alpha == other._alpha
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two colors for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the colors differ in a component or the opacity.
		:raises TypeError: If the second operand is not of type :class:`Color`.
		"""
		if not isinstance(other, Color):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Color")
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
		return f"Color({self._red}, {self._green}, {self._blue}, {self._alpha})"

	def __str__(self) -> str:
		"""
		Returns the color's string equivalent as a hexadecimal color string.

		:returns: ``#rrggbb`` for an opaque color, else ``#rrggbbaa`` with the opacity scaled to 0..255.
		"""
		if self._alpha == 1.0:
			return f"#{self._red:02x}{self._green:02x}{self._blue:02x}"

		return f"#{self._red:02x}{self._green:02x}{self._blue:02x}{round(self._alpha * 255):02x}"


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
		:param color:       Color of the line.
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

		:param color:       Color of the area.
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
	"""

	_family: str    #: Font name or generic font family.
	_size:   float  #: Font size in points.
	_bold:   bool   #: If ``True``, the font is bold.
	_italic: bool   #: If ``True``, the font is italic.

	def __init__(self, family: str, size: float, *, bold: bool = False, italic: bool = False) -> None:
		"""
		Initializes a font from its family, size and style.

		:param family:      Font name or generic font family.
		:param size:        Font size in points.
		:param bold:        Optional, if ``True``, the font is bold. Default: ``False``.
		:param italic:      Optional, if ``True``, the font is italic. Default: ``False``.
		:raises ValueError: If parameter 'family' is None.
		:raises TypeError:  If parameter 'family' is not of type :class:`str`.
		:raises ValueError: If parameter 'family' is empty.
		:raises ValueError: If parameter 'size' is None.
		:raises TypeError:  If parameter 'size' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'size' isn't positive.
		:raises ValueError: If parameter 'bold' is None.
		:raises TypeError:  If parameter 'bold' is not of type :class:`bool`.
		:raises ValueError: If parameter 'italic' is None.
		:raises TypeError:  If parameter 'italic' is not of type :class:`bool`.
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
			("bold",   bold),
			("italic", italic)
		):
			if flag is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(flag, bool):
				ex = TypeError(f"Parameter '{name}' is not of type 'bool'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(flag)}'.")
				raise ex

		self._family = family
		self._size =   size
		self._bold =   bold
		self._italic = italic

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
	def Italic(self) -> bool:
		"""
		Read-only property to access, if the font is italic (:attr:`_italic`).

		:returns: ``True``, if the font is italic.
		"""
		return self._italic

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two fonts for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both fonts have the same family, size and style.
		:raises TypeError: If the second operand is not of type :class:`Font`.
		"""
		if not isinstance(other, Font):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Font")
			raise ex

		return (
			self._family == other._family and self._size == other._size and
			self._bold is other._bold and self._italic is other._italic
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two fonts for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the fonts differ in family, size or style.
		:raises TypeError: If the second operand is not of type :class:`Font`.
		"""
		if not isinstance(other, Font):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Font")
			raise ex

		return (
			self._family != other._family or self._size != other._size or
			self._bold is not other._bold or self._italic is not other._italic
		)

	def __hash__(self) -> int:
		"""
		Returns a hash of the font's family, size and style, so equal fonts have the same hash.

		:returns: The hash value.
		"""
		return hash((self._family, self._size, self._bold, self._italic))

	def __repr__(self) -> str:
		"""
		Returns the font's string representation.

		:returns: The string representation of the font.
		"""
		return f"Font({self._family!r}, {self._size}, bold={self._bold}, italic={self._italic})"
