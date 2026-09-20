# ==================================================================================================================== #
#             _____           _ _             _____               _                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ __ _  ___(_)_ __   __ _                                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _` |/ __| | '_ \ / _` |                                       #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | | (_| | (__| | | | | (_| |                                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \__,_|\___|_|_| |_|\__, |                                       #
# |_|    |___/                          |___/                             |___/                                        #
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
Render a software execution trace as a Gantt chart with :term:`matplotlib`.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing.Render import GanttLayout, ciSpanFilter
   from pyTooling.Tracing.Render.Matplotlib import MatplotlibRenderer

   layout = GanttLayout(trace, spanFilter=ciSpanFilter())
   MatplotlibRenderer(layout).Write(Path("report/Pipeline.svg"))

Every bar or line of a timespan in an SVG file is a group with the identifier ``span-<SpanID>``, a waiting bar
``span-<SpanID>-queued`` and the end marks of a line ``span-<SpanID>-ends``, so a script can find the elements of a
timespan.

.. hint::

   See :ref:`high-level help <TRACING/Render>` for explanations and usage examples.
"""
from pathlib                     import Path
from typing                      import ClassVar, Iterable, Optional as Nullable, Union

from pyTooling.Decorators        import export, readonly
from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Exceptions        import MissingDependencyError
from pyTooling.Tracing.CI        import SpanKind
from pyTooling.Tracing.Render    import GanttLayout, LINE_LEGEND_LABEL, Renderer

try:
	from matplotlib              import rc_context
	from matplotlib.figure       import Figure
	from matplotlib.font_manager import FontProperties, findfont, fontManager
	from matplotlib.ft2font      import FT2Font
	from matplotlib.lines        import Line2D
	from matplotlib.patches      import Patch
	from matplotlib.ticker       import FuncFormatter
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="matplotlib", extra="diagram") from ex


__all__ = ["FONT_FAMILIES", "MONOSPACE_FONT_FAMILY"]

FONT_FAMILIES = ("DejaVu Sans", "Noto Emoji", "Symbola")
"""The font families tried in order for a character - a later emoji font supplies the emoji of job names."""

MONOSPACE_FONT_FAMILY = "DejaVu Sans Mono"
"""The font family of the legend, whose statistics are aligned in columns. matplotlib ships it."""


@export
class MatplotlibRenderer(Renderer[Figure]):
	"""
	Draws a :class:`~pyTooling.Tracing.Render.GanttLayout` with :term:`matplotlib`.

	Every row shows its timespan's name, indented by its depth. The pipeline and a called workflow are a line from
	their begin to their end; a job is a bar, colored by its row's category, a waiting bar light gray and a running
	bar hatched. A bar too short to see is widened to a visible minimum.

	matplotlib's object API is used throughout, so no global :mod:`~matplotlib.pyplot` state is touched and no
	display is needed.
	"""
	FORMATS: ClassVar[tuple[str, ...]] = ("svg", "png", "pdf")  #: The file formats this renderer writes.

	_width:          float          #: Width of the figure in inches.
	_rowHeight:      float          #: Height of a row in inches.
	_fontSize:       float          #: Font size of labels in points.
	_legendLocation: str            #: The legend's location, as matplotlib's ``loc`` names it.
	_dpi:            int            #: Resolution of a PNG file in dots per inch.
	_families:       list[str]      #: The installed font families of ``fontFamilies``, in their order.
	_fonts:          list[FT2Font]  #: The fonts of those families, to ask whether they can draw a character.

	def __init__(
		self,
		layout:         GanttLayout,
		*,
		title:          Nullable[str] = None,
		width:          float = 16.0,
		rowHeight:      float = 0.22,
		fontSize:       float = 7.0,
		fontFamilies:   Iterable[str] = FONT_FAMILIES,
		legendLocation: str = "upper right",
		dpi:            int = 150
	) -> None:
		"""
		Initializes a matplotlib renderer for a layout.

		:param layout:         The layout to draw.
		:param title:          Optional, the chart's title. Default: the trace's name and wall time.
		:param width:          Optional, width of the figure in inches. Default: ``16.0``.
		:param rowHeight:      Optional, height of a row in inches. Default: ``0.22``.
		:param fontSize:       Optional, font size of labels in points. Default: ``7.0``.
		:param fontFamilies:   Optional, font families tried in order for every character. Families that aren't
		                       installed are skipped. Default: :data:`FONT_FAMILIES`.
		:param legendLocation: Optional, the legend's location, as matplotlib's ``loc`` names it, e.g.
		                       ``'lower right'`` or ``'outside right upper'``. Default: ``'upper right'``.
		:param dpi:            Optional, resolution of a PNG file in dots per inch. Default: ``150``.
		:raises TypeError:     If parameter 'layout' is not of type :class:`~pyTooling.Tracing.Render.GanttLayout`.
		:raises TypeError:     If parameter 'title' is not of type :class:`str`.
		:raises ValueError:    If parameter 'width', 'rowHeight', 'fontSize' or 'dpi' isn't positive.
		"""
		super().__init__(layout, title=title)

		for parameter, value in (("width", width), ("rowHeight", rowHeight), ("fontSize", fontSize), ("dpi", dpi)):
			if not value > 0:
				ex = ValueError(f"Parameter '{parameter}' isn't positive.")
				ex.add_note(f"Got value '{value}'.")
				raise ex

		self._width =          width
		self._rowHeight =      rowHeight
		self._fontSize =       fontSize
		self._legendLocation = legendLocation
		self._dpi =            dpi
		self._families, self._fonts = self._LoadFonts(fontFamilies)

	@readonly
	def Width(self) -> float:
		"""
		Read-only property to access the width of the figure (:attr:`_width`).

		:returns: Width in inches.
		"""
		return self._width

	@readonly
	def RowHeight(self) -> float:
		"""
		Read-only property to access the height of a row (:attr:`_rowHeight`).

		:returns: Height in inches.
		"""
		return self._rowHeight

	@readonly
	def FontSize(self) -> float:
		"""
		Read-only property to access the font size of labels (:attr:`_fontSize`).

		:returns: Font size in points.
		"""
		return self._fontSize

	@readonly
	def FontFamilies(self) -> tuple[str, ...]:
		"""
		Read-only property to return the font families that are installed (:attr:`_families`).

		:returns: The families the chart is drawn with, in the order they are tried.
		"""
		return tuple(self._families)

	@staticmethod
	def _LoadFonts(fontFamilies: Iterable[str]) -> tuple[list[str], list[FT2Font]]:
		"""
		Load the fonts of the font families, which are installed.

		Installation is checked against matplotlib's font list first, because looking up a missing family logs a
		warning.

		:param fontFamilies: The font families.
		:returns:            The installed families and their fonts, in the order of the families.
		"""
		installed = {font.name for font in fontManager.ttflist}
		families: list[str] = []
		fonts: list[FT2Font] = []
		for family in fontFamilies:
			if family not in installed:
				continue

			try:
				fonts.append(FT2Font(findfont(FontProperties(family=family), fallback_to_default=False)))
				families.append(family)
			except (ValueError, OSError):
				pass

		return families, fonts

	def _Renderable(self, text: str) -> str:
		"""
		Remove the characters none of the loaded fonts has a glyph for, like emoji without an emoji font.

		matplotlib would draw an empty box for each of them and warn about every one.

		:param text: The text.
		:returns:    The text without characters that can't be drawn, and without the whitespace left behind.
		"""
		if len(self._fonts) == 0:
			return text

		characters = (
			character for character in text
			if character.isspace() or any(font.get_char_index(ord(character)) != 0 for font in self._fonts)
		)
		return " ".join("".join(characters).split())

	def Render(self) -> Figure:
		"""
		Draw the layout as a Gantt chart.

		The legend's title shows when the trace began and ended, its wall time, the runner time - the time all jobs
		ran, added up - and the number of jobs. Every category shows the number of its jobs, and their minimum,
		average and maximum waiting and running times.

		:returns: The chart as a matplotlib figure, which isn't registered with :mod:`matplotlib.pyplot`.
		"""
		layout = self._layout
		rows = list(layout.IterateRows())
		duration = max(layout.Duration, 1.0)
		minimumWidth = duration / 1000
		rcParameters = {"font.size": self._fontSize}
		if len(self._families) > 0:
			rcParameters["font.family"] = self._families

		with rc_context(rcParameters):
			figure = Figure(figsize=(self._width, 1.6 + self._rowHeight * max(len(rows), 12)), layout="constrained")
			axes = figure.add_subplot()

			hasQueued = False
			hasLines = False
			for position, row in enumerate(rows):
				if row.Kind in (SpanKind.Pipeline, SpanKind.Workflow):
					for bar in row.Bars:
						hasLines = True
						style = "dashed" if bar.IsRunning else "solid"
						begin = bar.BeginSinceOriginInSeconds
						end =   bar.EndSinceOriginInSeconds
						line = axes.hlines(position, begin, end, colors=self.LINE, linewidth=1.0, linestyles=style)
						ends = axes.vlines([begin, end], position - 0.3, position + 0.3, colors=self.LINE, linewidth=1.0)
						line.set_gid(f"span-{row.SpanID}")
						ends.set_gid(f"span-{row.SpanID}-ends")
					continue

				color = self.Color(row.Category)
				for bar in row.Bars:
					hasQueued |= bar.IsQueued
					collection = axes.broken_barh(
						[(bar.BeginSinceOriginInSeconds, max(bar.DurationInSeconds, minimumWidth))],
						(position - 0.4, 0.8),
						facecolors=self.QUEUED if bar.IsQueued else color,
						hatch="///" if bar.IsRunning else None,
						linewidth=0
					)
					collection.set_gid(f"span-{row.SpanID}-queued" if bar.IsQueued else f"span-{row.SpanID}")

			labels = [f"{'  ' * row.Depth}{self._Renderable(row.Name)}" for row in rows]
			axes.set_yticks(range(len(rows)), labels=labels)
			axes.set_ylim(len(rows) - 0.5, -0.5)
			axes.set_xlim(0, duration)
			axes.xaxis.set_major_formatter(FuncFormatter(lambda value, position: self.FormatSeconds(value)))
			axes.set_xlabel("time since the trace began")
			axes.grid(axis="x", linewidth=0.3, alpha=0.5)

			handles: list[Union[Patch, Line2D]] = [
				Patch(facecolor=self.Color(category), label=self.LegendLabel(category))
				for category in layout.Categories
			]
			if hasQueued:
				handles.append(Patch(facecolor=self.QUEUED, label="waiting for a runner"))
			if hasLines:
				handles.append(Line2D(
					[], [], color=self.LINE, linewidth=1.0, marker="|", markersize=6, label=LINE_LEGEND_LABEL
				))

			monospace = {"family": MONOSPACE_FONT_FAMILY, "size": self._fontSize}
			axes.legend(
				handles=handles,
				title=self.LegendTitle(),
				loc=self._legendLocation,
				prop=monospace,
				title_fontproperties=monospace,
				alignment="left",
				framealpha=0.95
			)

			figure.suptitle(self._Renderable(self._title), fontsize=self._fontSize + 2)

		return figure

	def _Write(self, figure: Figure, file: Path, fileFormat: str) -> None:
		"""
		Write a drawn chart to a file.

		:param figure:     The chart, as :meth:`Render` returned it.
		:param file:       Path of the file to write, whose parent directories exist.
		:param fileFormat: The file format, one of :attr:`FORMATS`.
		:raises OSError:   If the file couldn't be written.
		"""
		with rc_context({} if len(self._families) == 0 else {"font.family": self._families}):
			figure.savefig(file, format=fileFormat, dpi=self._dpi)
