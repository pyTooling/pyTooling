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
Render a software execution trace as an interactive Gantt chart with :term:`plotly`.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing.Render import ciSpanFilter
   from pyTooling.Tracing.Render.Plotly import WriteGantt

   WriteGantt(trace, Path("report/Pipeline.html"), spanFilter=ciSpanFilter())

.. hint::

   See :ref:`high-level help <TRACING/Render/Plotly>` for explanations and usage examples.
"""
from datetime                    import datetime, timedelta
from html                        import escape
from pathlib                     import Path
from typing                      import Any, Optional as Nullable, Union

from pyTooling.Decorators        import export
from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Exceptions        import MissingDependencyError
from pyTooling.Tracing           import Trace, TracingError
from pyTooling.Tracing.CI        import SPAN_KIND_PIPELINE, SPAN_KIND_WORKFLOW
from pyTooling.Tracing.Render    import GanttBar, GanttLayout, GanttRow, SpanCategory, SpanFilter, runnerCategory
from pyTooling.Tracing.Render    import LINE_LEGEND, QUEUED_LEGEND, formatDuration, formatTime, legendLabel, legendTitle

try:
	from plotly.graph_objects    import Bar, Figure, Scatter
except ImportError as ex:  # pragma: no cover
	raise MissingDependencyError(dependency="plotly", extra="diagram") from ex


__all__ = ["FORMATS", "MONOSPACE_FONT_FAMILIES", "TIME_AXIS_ORIGIN"]

FORMATS = ("html", "json")
"""The file formats :func:`WriteGantt` writes, by file suffix."""

MONOSPACE_FONT_FAMILIES = "DejaVu Sans Mono, Consolas, Menlo, monospace"
"""The CSS font families of the legend, whose statistics are aligned in columns."""

TIME_AXIS_ORIGIN = datetime(1970, 1, 1)
"""
The date the time axis starts at. The time axis is a date axis, whose ticks show the time since the trace began as
``hh:mm:ss``.
"""

_PALETTE = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#bcbd22", "#17becf")
"""Colors of the categories, in the order the categories appear."""

_NEUTRAL = "#7f7f7f"
"""Color of a bar without a category."""

_LINE = "#404040"
"""Color of the line spanning the pipeline or a called workflow."""

_QUEUED = "#d3d3d3"
"""Color of a bar showing the time a job waited for a runner."""

_HOVER_TEMPLATE = (
	"<b>%{customdata[0]}</b><br>begin %{customdata[1]}<br>end %{customdata[2]}<br>duration %{customdata[3]}"
	"<extra>%{customdata[4]}</extra>"
)
"""Hover text of a bar or line, filled from the fields composed by :func:`_hover`."""


def _text(text: str) -> str:
	"""
	Escape a text for plotly, which interprets HTML tags like ``<b>`` and entities in titles, labels and hover texts.

	:param text: The text.
	:returns:    The text with ``&``, ``<`` and ``>`` escaped.
	"""
	return escape(text, quote=False)


def _preformatted(text: str) -> str:
	"""
	Convert a text of aligned columns and lines into plotly's markup.

	:param text: The text, with lines separated by ``\\n``.
	:returns:    The escaped text with non-breaking spaces, and lines separated by ``<br>``.
	"""
	return "<br>".join(_text(line).replace(" ", " ") for line in text.split("\n"))


def _time(seconds: float) -> datetime:
	"""
	Return the position of a time on the time axis.

	:param seconds: Seconds after the trace began.
	:returns:       The position as a date after :data:`TIME_AXIS_ORIGIN`.
	"""
	return TIME_AXIS_ORIGIN + timedelta(seconds=seconds)


def _hover(layout: GanttLayout, row: GanttRow, bar: GanttBar) -> list[str]:
	"""
	Compose the fields of a bar's or line's hover text.

	:param layout: The layout of the trace.
	:param row:    The row of the bar.
	:param bar:    The bar.
	:returns:      The timespan's name, its absolute begin and end, its duration, and its category or state.
	"""
	if bar.IsQueued:
		detail = QUEUED_LEGEND
	elif bar.IsRunning:
		detail = "running" if row.Category == "" else f"{row.Category}, running"
	else:
		detail = row.Category

	return [
		_text(row.Name),
		formatTime(layout.BeginTime + timedelta(seconds=bar.Begin)),
		formatTime(layout.BeginTime + timedelta(seconds=bar.End)),
		formatDuration(bar.Duration),
		_text(detail)
	]


@export
def RenderGantt(
	layout:    GanttLayout,
	*,
	title:     Nullable[str] = None,
	width:     Nullable[int] = None,
	rowHeight: int = 20,
	fontSize:  float = 11.0
) -> Figure:
	"""
	Render the layout of a trace as an interactive Gantt chart.

	Every row shows its timespan's name, indented by its depth. The pipeline and a called workflow are a line from their
	begin to their end, dashed while running. A job's bar is colored by its row's category, a waiting bar is light gray,
	and a running bar is hatched. A bar too short to see is widened to a visible minimum.

	The chart can be zoomed and panned. Hovering a bar or line shows the timespan's name, its absolute begin and end, and
	its duration. The legend shows the same statistics as :func:`pyTooling.Tracing.Render.Matplotlib.RenderGantt`, and a
	click on a legend entry hides or shows its bars.

	:param layout:      The layout of the trace.
	:param title:       Optional, the chart's title. Default: the trace's name and wall time.
	:param width:       Optional, width of the chart in pixels. Default: the width of the page.
	:param rowHeight:   Optional, height of a row in pixels. Default: ``20``.
	:param fontSize:    Optional, font size of labels in pixels. Default: ``11.0``.
	:returns:           The chart as a plotly figure.
	:raises TypeError:  If parameter 'layout' is not of type :class:`~pyTooling.Tracing.Render.GanttLayout`.
	:raises ValueError: If parameter 'width', 'rowHeight' or 'fontSize' isn't positive.
	"""
	if not isinstance(layout, GanttLayout):
		ex = TypeError("Parameter 'layout' is not of type 'GanttLayout'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(layout)}'.")
		raise ex

	for parameter, value in (("width", width), ("rowHeight", rowHeight), ("fontSize", fontSize)):
		if parameter == "width" and value is None:
			continue
		elif not value > 0:
			ex = ValueError(f"Parameter '{parameter}' isn't positive.")
			ex.add_note(f"Got value '{value}'.")
			raise ex

	colors = {category: _PALETTE[position % len(_PALETTE)] for position, category in enumerate(layout.Categories)}
	rows = list(layout.IterateRows())
	duration = max(layout.Duration, 1.0)
	minimumWidth = duration / 1000

	bars: dict[tuple[bool, str], dict[str, list[Any]]] = {}
	lines: dict[bool, dict[str, list[Any]]] = {}
	for position, row in enumerate(rows):
		if row.Kind in (SPAN_KIND_PIPELINE, SPAN_KIND_WORKFLOW):
			for bar in row.Bars:
				line = lines.setdefault(bar.IsRunning, {"x": [], "y": [], "customdata": []})
				hover = _hover(layout, row, bar)
				line["x"].extend((_time(bar.Begin), _time(bar.End), None))
				line["y"].extend((position, position, None))
				line["customdata"].extend((hover, hover, [""] * len(hover)))
			continue

		for bar in row.Bars:
			group = bars.setdefault(
				(bar.IsQueued, "" if bar.IsQueued else row.Category),
				{"base": [], "x": [], "y": [], "customdata": [], "pattern": []}
			)
			group["base"].append(_time(bar.Begin))
			group["x"].append(max(bar.Duration, minimumWidth) * 1000)
			group["y"].append(position)
			group["customdata"].append(_hover(layout, row, bar))
			group["pattern"].append("/" if bar.IsRunning else "")

	figure = Figure()
	for queued, category in [(False, category) for category in layout.Categories] + [(False, ""), (True, "")]:
		if (group := bars.get((queued, category))) is None:
			continue
		elif queued:
			name, color = _preformatted(QUEUED_LEGEND), _QUEUED
		elif category == "":
			name, color = "", _NEUTRAL
		else:
			name, color = _preformatted(legendLabel(layout, category)), colors[category]

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
			line={"color": _LINE, "width": 1, "dash": "dash" if running else "solid"},
			marker={"color": _LINE, "symbol": "line-ns-open", "size": 10},
			name=_preformatted(LINE_LEGEND),
			legendgroup="lines",
			showlegend=not running or False not in lines
		))

	if title is None:
		title = f"{layout.Trace.Name} ({formatDuration(layout.WallTime)})"

	monospace = {"family": MONOSPACE_FONT_FAMILIES, "size": fontSize}
	figure.update_layout(
		title={"text": _text(title)},
		template="plotly_white",
		barmode="overlay",
		width=width,
		height=160 + rowHeight * max(len(rows), 12),
		font={"size": fontSize},
		hoverlabel={"align": "left"},
		legend={
			"title": {"text": _preformatted(legendTitle(layout)), "font": monospace},
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
		range=[_time(0), _time(duration)],
		title={"text": "time since the trace began"},
		showgrid=True
	)
	figure.update_yaxes(
		tickmode="array",
		tickvals=list(range(len(rows))),
		ticktext=["\u00a0" * 2 * row.Depth + _text(row.Name) for row in rows],
		range=[len(rows) - 0.5, -0.5],
		showgrid=False,
		automargin=True
	)

	return figure


@export
def WriteGantt(
	trace:           Trace,
	file:            Path,
	*,
	spanFilter:      Nullable[SpanFilter] = None,
	categorize:      SpanCategory = runnerCategory,
	now:             Nullable[datetime] = None,
	title:           Nullable[str] = None,
	width:           Nullable[int] = None,
	rowHeight:       int = 20,
	fontSize:        float = 11.0,
	includePlotlyJS: Union[bool, str] = True
) -> None:
	"""
	Lay out a trace, render it as an interactive Gantt chart, and write the chart to a file.

	The file format is chosen by the file's suffix, one of :data:`FORMATS`: an HTML page showing the chart, or the
	figure as JSON, as ``plotly.io.read_json`` reads it. Missing parent directories are created.

	:param trace:           The trace to render.
	:param file:            Path of the file to write.
	:param spanFilter:      Optional, function deciding which timespans are shown, e.g. created by
	                        :func:`~pyTooling.Tracing.Render.ciSpanFilter`. Default: all timespans.
	:param categorize:      Optional, function returning a timespan's category. Default: :func:`runnerCategory`.
	:param now:             Optional, the time a running timespan's bar ends at. Default: the current system time.
	:param title:           Optional, the chart's title. Default: the trace's name and wall time.
	:param width:           Optional, width of the chart in pixels. Default: the width of the page.
	:param rowHeight:       Optional, height of a row in pixels. Default: ``20``.
	:param fontSize:        Optional, font size of labels in pixels. Default: ``11.0``.
	:param includePlotlyJS: Optional, how an HTML page loads plotly's JavaScript library: ``True`` embeds it (about
	                        4 MiB), so the page works offline, and ``'cdn'`` loads it from plotly's CDN.
	                        Default: ``True``.
	:raises TypeError:      If parameter 'file' is not of type :class:`~pathlib.Path`.
	:raises ValueError:     If the file's suffix isn't one of :data:`FORMATS`.
	:raises TracingError:   If the parent directories couldn't be created.
	:raises TracingError:   If the file couldn't be written.
	"""
	if not isinstance(file, Path):
		ex = TypeError("Parameter 'file' is not of type 'Path'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(file)}'.")
		raise ex
	elif (fileFormat := file.suffix.lower().lstrip(".")) not in FORMATS:
		ex = ValueError(f"File '{file}' has an unsupported format.")
		ex.add_note(f"Supported file suffixes: {', '.join(f'.{suffix}' for suffix in FORMATS)}")
		raise ex

	layout = GanttLayout(trace, spanFilter=spanFilter, categorize=categorize, now=now)
	figure = RenderGantt(layout, title=title, width=width, rowHeight=rowHeight, fontSize=fontSize)

	if fileFormat == "html":
		content = figure.to_html(include_plotlyjs=includePlotlyJS, full_html=True, config={"displaylogo": False})
	else:
		content = figure.to_json()

	try:
		file.parent.mkdir(parents=True, exist_ok=True)
	except OSError as ex:
		raise TracingError(f"Directory '{file.parent}' couldn't be created.") from ex

	try:
		file.write_text(content, encoding="utf-8")
	except OSError as ex:
		raise TracingError(f"File '{file}' couldn't be written.") from ex
