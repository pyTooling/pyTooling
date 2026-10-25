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
"""
Render a software execution trace as an interactive Gantt chart with :term:`plotly`.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing.Render import GanttLayout, ciSpanFilter
   from pyTooling.Tracing.Render.Plotly import PlotlyRenderer

   layout = GanttLayout(trace, spanFilter=ciSpanFilter())
   PlotlyRenderer(layout).Write(Path("report/Pipeline.html"))

.. hint::

   See :ref:`high-level help <TRACING/Render/Plotly>` for explanations and usage examples.
"""
from datetime                 import datetime, timedelta
from pathlib                  import Path
from typing                   import Any, ClassVar, Optional as Nullable

from pyTooling.Common         import getFullyQualifiedName, StringEnum
from pyTooling.Decorators     import export, readonly
from pyTooling.Exceptions     import MissingDependencyError
from pyTooling.Tracing.CI     import SpanKind
from pyTooling.Tracing.Render import GanttBar, GanttLayout, GanttRow, LINE_LEGEND_LABEL, QUEUED_LEGEND_LABEL, Renderer

try:
	from plotly.graph_objects   import Bar, Figure, Scatter
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="plotly", extra="diagram") from ex


__all__ = ["MONOSPACE_FONT_FAMILIES", "TIME_AXIS_ORIGIN"]

MONOSPACE_FONT_FAMILIES = "DejaVu Sans Mono, Consolas, Menlo, monospace"
"""The CSS font families of the legend, whose statistics are aligned in columns."""

TIME_AXIS_ORIGIN = datetime(1970, 1, 1)
"""
The date the time axis starts at. The time axis is a date axis, whose ticks show the time since the trace began as
``hh:mm:ss``.
"""

_HOVER_TEMPLATE = (
	"<b>%{customdata[0]}</b><br>begin %{customdata[1]}<br>end %{customdata[2]}<br>duration %{customdata[3]}"
	"<extra>%{customdata[4]}</extra>"
)
"""Hover text of a bar or line, filled from the fields composed by :meth:`PlotlyRenderer._Hover`."""


@export
class PlotlyJavaScript(StringEnum):
	"""How an HTML page written by :class:`PlotlyRenderer` loads plotly's JavaScript library."""

	Embedded = "embedded"  #: The library is embedded into the page (about 4 MiB), so the page works offline.
	CDN =      "cdn"       #: The page loads the library from plotly's CDN.

	DEFAULT = Embedded     #: The way used if none is given.


@export
class PlotlyRenderer(Renderer[Figure]):
	"""
	Draws a :class:`~pyTooling.Tracing.Render.GanttLayout` as an interactive chart with :term:`plotly`.

	Every row shows its timespan's name, indented by its depth. The pipeline and a called workflow are a line from their
	begin to their end, dashed while running. A job's bar is colored by its row's category, a waiting bar is light gray,
	and a running bar is hatched. A bar too short to see is widened to a visible minimum.

	The chart can be zoomed and panned. Hovering a bar or line shows the timespan's name, its absolute begin and end, and
	its duration. The legend shows the same statistics as
	:class:`~pyTooling.Tracing.Render.Matplotlib.MatplotlibRenderer`, and a click on a legend entry hides or shows its
	bars.

	The chart is written as an HTML page showing it, or as the figure's JSON, as ``plotly.io.read_json`` reads it.
	"""
	FORMATS: ClassVar[tuple[str, ...]] = ("html", "json")  #: The file formats this renderer writes.

	_width:           Nullable[int]     #: Width of the chart in pixels, or ``None`` for the width of the page.
	_rowHeight:       int               #: Height of a row in pixels.
	_fontSize:        float             #: Font size of labels in pixels.
	_includePlotlyJS: PlotlyJavaScript  #: How an HTML page loads plotly's JavaScript library.

	def __init__(
		self,
		layout:          GanttLayout,
		*,
		title:           Nullable[str] = None,
		width:           Nullable[int] = None,
		rowHeight:       int = 20,
		fontSize:        float = 11.0,
		includePlotlyJS: PlotlyJavaScript = PlotlyJavaScript.DEFAULT
	) -> None:
		"""
		Initializes a plotly renderer for a layout.

		:param layout:          The layout to draw.
		:param title:           Optional, the chart's title. Default: the trace's name and wall time.
		:param width:           Optional, width of the chart in pixels. Default: the width of the page.
		:param rowHeight:       Optional, height of a row in pixels. Default: ``20``.
		:param fontSize:        Optional, font size of labels in pixels. Default: ``11.0``.
		:param includePlotlyJS: Optional, how an HTML page loads plotly's JavaScript library.
		                        Default: :attr:`PlotlyJavaScript.DEFAULT`.
		:raises TypeError:      If parameter 'layout' is not of type :class:`~pyTooling.Tracing.Render.GanttLayout`.
		:raises TypeError:      If parameter 'title' is not of type :class:`str`.
		:raises TypeError:      If parameter 'width' is not of type :class:`int`.
		:raises ValueError:     If parameter 'width' isn't positive.
		:raises ValueError:     If parameter 'rowHeight' is None.
		:raises TypeError:      If parameter 'rowHeight' is not of type :class:`int`.
		:raises ValueError:     If parameter 'rowHeight' isn't positive.
		:raises ValueError:     If parameter 'fontSize' is None.
		:raises TypeError:      If parameter 'fontSize' is not of type :class:`float` or :class:`int`.
		:raises ValueError:     If parameter 'fontSize' isn't positive.
		:raises ValueError:     If parameter 'includePlotlyJS' is None.
		:raises TypeError:      If parameter 'includePlotlyJS' is not of type :class:`PlotlyJavaScript`.
		"""
		super().__init__(layout, title=title)

		if width is not None and not isinstance(width, int):
			ex = TypeError("Parameter 'width' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex
		elif width is not None and width <= 0:
			ex = ValueError("Parameter 'width' isn't positive.")
			ex.add_note(f"Got value '{width}'.")
			raise ex

		if rowHeight is None:
			raise ValueError("Parameter 'rowHeight' is None.")
		elif not isinstance(rowHeight, int):
			ex = TypeError("Parameter 'rowHeight' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(rowHeight)}'.")
			raise ex
		elif rowHeight <= 0:
			ex = ValueError("Parameter 'rowHeight' isn't positive.")
			ex.add_note(f"Got value '{rowHeight}'.")
			raise ex

		if fontSize is None:
			raise ValueError("Parameter 'fontSize' is None.")
		elif not isinstance(fontSize, (float, int)):
			ex = TypeError("Parameter 'fontSize' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(fontSize)}'.")
			raise ex
		elif fontSize <= 0:
			ex = ValueError("Parameter 'fontSize' isn't positive.")
			ex.add_note(f"Got value '{fontSize}'.")
			raise ex

		if includePlotlyJS is None:
			raise ValueError("Parameter 'includePlotlyJS' is None.")
		elif not isinstance(includePlotlyJS, PlotlyJavaScript):
			ex = TypeError("Parameter 'includePlotlyJS' is not of type 'PlotlyJavaScript'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(includePlotlyJS)}'.")
			raise ex

		self._width =           width
		self._rowHeight =       rowHeight
		self._fontSize =        fontSize
		self._includePlotlyJS = includePlotlyJS

	@readonly
	def Width(self) -> Nullable[int]:
		"""
		Read-only property to access the width of the chart (:attr:`_width`).

		:returns: Width in pixels, or ``None`` for the width of the page.
		"""
		return self._width

	@readonly
	def RowHeight(self) -> int:
		"""
		Read-only property to access the height of a row (:attr:`_rowHeight`).

		:returns: Height in pixels.
		"""
		return self._rowHeight

	@readonly
	def FontSize(self) -> float:
		"""
		Read-only property to access the font size of labels (:attr:`_fontSize`).

		:returns: Font size in pixels.
		"""
		return self._fontSize

	@readonly
	def IncludePlotlyJS(self) -> PlotlyJavaScript:
		"""
		Read-only property to access how an HTML page loads plotly's JavaScript library (:attr:`_includePlotlyJS`).

		:returns: How the library is loaded.
		"""
		return self._includePlotlyJS

	def _Hover(self, row: GanttRow, bar: GanttBar) -> list[str]:
		"""
		Compose the fields of a bar's or line's hover text.

		:param row: The row of the bar.
		:param bar: The bar.
		:returns:   The timespan's name, its absolute begin and end, its duration, and its category or state.
		"""
		if bar.IsQueued:
			detail = QUEUED_LEGEND_LABEL
		elif bar.IsRunning:
			detail = "running" if row.Category == "" else f"{row.Category}, running"
		else:
			detail = row.Category

		return [
			self._EscapeText(row.Name),
			self.FormatTime(bar.Begin),
			self.FormatTime(bar.End),
			self.FormatSeconds(bar.DurationInSeconds),
			self._EscapeText(detail)
		]

	def Render(self) -> Figure:
		"""
		Draw the layout as an interactive Gantt chart.

		:returns: The chart as a plotly figure.
		"""
		layout =       self._layout
		rows =         list(layout.IterateRows())
		duration =     max(layout.DurationInSeconds, 1.0)
		minimumWidth = duration / 1000

		bars:  dict[tuple[bool, str], dict[str, list[Any]]] = {}
		lines: dict[bool, dict[str, list[Any]]] =            {}
		for position, row in enumerate(rows):
			if row.Kind in (SpanKind.Pipeline, SpanKind.Workflow):
				for bar in row.Bars:
					line = lines.setdefault(bar.IsRunning, {"x": [], "y": [], "customdata": []})
					hover = self._Hover(row, bar)
					line["x"].extend((
						self._TimeAxisPosition(bar.BeginSinceOriginInSeconds),
						self._TimeAxisPosition(bar.EndSinceOriginInSeconds),
						None
					))
					line["y"].extend((position, position, None))
					line["customdata"].extend((hover, hover, [""] * len(hover)))
				continue

			for bar in row.Bars:
				group = bars.setdefault(
					(bar.IsQueued, "" if bar.IsQueued else row.Category),
					{"base": [], "x": [], "y": [], "customdata": [], "pattern": []}
				)
				group["base"].append(self._TimeAxisPosition(bar.BeginSinceOriginInSeconds))
				group["x"].append(max(bar.DurationInSeconds, minimumWidth) * 1000)
				group["y"].append(position)
				group["customdata"].append(self._Hover(row, bar))
				group["pattern"].append("/" if bar.IsRunning else "")

		figure = Figure()
		for queued, category in [(False, category) for category in layout.Categories] + [(False, ""), (True, "")]:
			if (group := bars.get((queued, category))) is None:
				continue
			elif queued:
				name =  self._Preformatted(QUEUED_LEGEND_LABEL)
				color = self.QUEUED
			elif category == "":
				name =  ""
				color = self.NEUTRAL
			else:
				name =  self._Preformatted(self.LegendLabel(category))
				color = self.Color(category)

			figure.add_trace(Bar(
				orientation="h",
				base=group["base"],
				x=group["x"],
				y=group["y"],
				width=0.8,
				customdata=group["customdata"],
				hovertemplate=_HOVER_TEMPLATE,
				name=name,
				showlegend=name != "",
				marker={"color": color, "line": {"width": 0}, "pattern": {"shape": group["pattern"]}}
			))

		for running in (False, True):
			if (line := lines.get(running)) is None:
				continue

			figure.add_trace(Scatter(
				x=line["x"],
				y=line["y"],
				customdata=line["customdata"],
				hovertemplate=_HOVER_TEMPLATE,
				mode="lines+markers",
				line={"color": self.LINE, "width": 1, "dash": "dash" if running else "solid"},
				marker={"color": self.LINE, "symbol": "line-ns-open", "size": 10},
				name=self._Preformatted(LINE_LEGEND_LABEL),
				legendgroup="lines",
				showlegend=not running or False not in lines
			))

		monospace = {"family": MONOSPACE_FONT_FAMILIES, "size": self._fontSize}
		figure.update_layout(
			title={"text": self._EscapeText(self._title)},
			template="plotly_white",
			barmode="overlay",
			width=self._width,
			height=160 + self._rowHeight * max(len(rows), 12),
			font={"size": self._fontSize},
			hoverlabel={"align": "left"},
			legend={
				"title": {"text": self._Preformatted(self.LegendTitle()), "font": monospace},
				"font": monospace,
				"x": 1.0,
				"y": 1.0,
				"xanchor": "right",
				"yanchor": "top",
				"bgcolor": "rgba(255, 255, 255, 0.95)",
				"bordercolor": "#cccccc",
				"borderwidth": 1
			}
		)
		figure.update_xaxes(
			type="date",
			tickformat="%H:%M:%S",
			range=[self._TimeAxisPosition(0), self._TimeAxisPosition(duration)],
			title={"text": "time since the trace began"},
			showgrid=True
		)
		figure.update_yaxes(
			tickmode="array",
			tickvals=list(range(len(rows))),
			ticktext=["\u00a0" * 2 * row.Depth + self._EscapeText(row.Name) for row in rows],
			range=[len(rows) - 0.5, -0.5],
			showgrid=False,
			automargin=True
		)

		return figure

	@staticmethod
	def _EscapeText(text: str) -> str:
		"""
		Escape a text for plotly, which interprets HTML tags like ``<b>`` and entities in titles, labels and hover texts.

		:param text: The text.
		:returns:    The text with ``&``, ``<`` and ``>`` escaped.
		"""
		return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

	@classmethod
	def _Preformatted(cls, text: str) -> str:
		"""
		Convert a text of aligned columns and lines into plotly's markup.

		:param text: The text, with lines separated by ``\\n``.
		:returns:    The escaped text with non-breaking spaces, and lines separated by ``<br>``.
		"""
		return "<br>".join(cls._EscapeText(line).replace(" ", "\u00a0") for line in text.split("\n"))

	@staticmethod
	def _TimeAxisPosition(seconds: float) -> datetime:
		"""
		Return the position of a time on the time axis.

		:param seconds: Seconds after the trace began.
		:returns:       The position as a date after :data:`TIME_AXIS_ORIGIN`.
		"""
		return TIME_AXIS_ORIGIN + timedelta(seconds=seconds)

	def _Write(self, figure: Figure, file: Path, fileFormat: str) -> None:
		"""
		Write a drawn chart to a file.

		:param figure:     The chart, as :meth:`Render` returned it.
		:param file:       Path of the file to write, whose parent directories exist.
		:param fileFormat: The file format, one of :attr:`FORMATS`.
		:raises OSError:   If the file couldn't be written.
		"""
		if fileFormat == "html":
			content = figure.to_html(
				include_plotlyjs=True if self._includePlotlyJS is PlotlyJavaScript.Embedded else "cdn",
				full_html=True,
				config={"displaylogo": False}
			)
		else:
			content = figure.to_json()

		with file.open("w", encoding="utf-8") as stream:
			stream.write(content)
