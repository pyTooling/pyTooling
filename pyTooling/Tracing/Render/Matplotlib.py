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
   from pyTooling.Tracing.Render import ciSpanFilter
   from pyTooling.Tracing.Render.Matplotlib import WriteGantt

   WriteGantt(trace, Path("report/Pipeline.svg"), spanFilter=ciSpanFilter())

Every bar or line of a timespan in an SVG file is a group with the identifier ``span-<SpanID>``, a waiting bar
``span-<SpanID>-queued`` and the end marks of a line ``span-<SpanID>-ends``, so a script can find the elements of a
timespan.

.. hint::

   See :ref:`high-level help <TRACING/Render>` for explanations and usage examples.
"""
from datetime                    import datetime
from io                          import StringIO
from json                        import dumps as json_dumps
from pathlib                     import Path
from typing                      import Iterable, Optional as Nullable, Union

from pyTooling.Decorators        import export
from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Exceptions        import MissingDependencyError
from pyTooling.Tracing           import Trace, TracingError
from pyTooling.Tracing.CI        import SpanKind
from pyTooling.Tracing.Render    import GanttLayout, SpanCategory, SpanFilter, runnerCategory

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


__all__ = ["FORMATS", "FONT_FAMILIES", "MONOSPACE_FONT_FAMILY"]

FORMATS = ("svg", "png", "pdf")
"""The file formats :func:`WriteGantt` writes, by file suffix."""

FONT_FAMILIES = ("DejaVu Sans", "Noto Emoji", "Symbola")
"""The font families tried in order for a character - a later emoji font supplies the emoji of job names."""

MONOSPACE_FONT_FAMILY = "DejaVu Sans Mono"
"""The font family of the legend, whose statistics are aligned in columns. matplotlib ships it."""

_PALETTE = ("#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#bcbd22", "#17becf")
"""Colors of the categories, in the order the categories appear."""

_NEUTRAL = "#7f7f7f"
"""Color of a bar without a category."""

_LINE = "#404040"
"""Color of the line spanning the pipeline or a called workflow."""

_QUEUED = "#d3d3d3"
"""Color of a bar showing the time a job waited for a runner."""

_COLLAPSE_STYLE = """
.gantt-marker { fill: #404040; font-family: sans-serif; cursor: pointer; user-select: none; }
"""
"""Style of the markers a collapsible SVG file shows in front of the labels of expandable rows."""

_COLLAPSE_SCRIPT = """
(function () {
  "use strict";
  const data = /*DATA*/;
  const rows = data.rows;
  const byID = new Map();
  for (const row of rows) { row.children = []; byID.set(row.id, row); }
  for (const row of rows) {
    if (row.parent !== null && byID.has(row.parent)) { byID.get(row.parent).children.push(row); }
  }
  const collapsed = new Set(rows.filter(row => row.collapsed && row.children.length > 0).map(row => row.id));
  const markers = new Map();

  function elementsOf(row) {
    return ["span-" + row.id, "span-" + row.id + "-queued", "span-" + row.id + "-ends", "label-" + row.id]
      .map(id => document.getElementById(id))
      .filter(element => element !== null);
  }

  function isHidden(row) {
    for (let parent = byID.get(row.parent); parent !== undefined; parent = byID.get(parent.parent)) {
      if (collapsed.has(parent.id)) { return true; }
    }
    return false;
  }

  function update() {
    let shift = 0;
    for (const row of rows) {
      const hidden = isHidden(row);
      const marker = markers.get(row.id);
      const shown = marker === undefined ? elementsOf(row) : elementsOf(row).concat([marker]);
      for (const element of shown) {
        element.style.display = hidden ? "none" : "";
        element.setAttribute("transform", "translate(0," + (-shift) + ")");
      }
      if (marker !== undefined) { marker.textContent = collapsed.has(row.id) ? "\\u25B8" : "\\u25BE"; }
      if (hidden) { shift += data.pitch; }
    }
  }

  function toggle(row) {
    if (collapsed.has(row.id)) { collapsed.delete(row.id); } else { collapsed.add(row.id); }
    update();
  }

  for (const row of rows) {
    if (row.children.length === 0) { continue; }
    for (const element of elementsOf(row)) {
      element.style.cursor = "pointer";
      element.addEventListener("click", () => toggle(row));
    }
    const label = document.getElementById("label-" + row.id);
    if (label !== null && typeof label.getBBox === "function") {
      const box = label.getBBox();
      const marker = document.createElementNS("http://www.w3.org/2000/svg", "text");
      marker.setAttribute("class", "gantt-marker");
      marker.setAttribute("x", box.x - 2);
      marker.setAttribute("y", box.y + box.height * 0.85);
      marker.setAttribute("text-anchor", "end");
      marker.setAttribute("font-size", box.height);
      marker.addEventListener("click", () => toggle(row));
      label.parentNode.insertBefore(marker, label.nextSibling);
      markers.set(row.id, marker);
    }
  }
  update();
})();
"""
"""Script of a collapsible SVG file. ``/*DATA*/`` is replaced by the rows and the distance between two rows."""


def _formatSeconds(seconds: float, position: int = 0) -> str:
	"""
	Format seconds as minutes and seconds, or as hours, minutes and seconds from one hour on.

	:param seconds:  The seconds.
	:param position: The tick's position, which matplotlib passes to every tick formatter. It isn't used.
	:returns:        The time as ``m:ss`` or ``h:mm:ss``.
	"""
	minutes, rest = divmod(int(round(seconds)), 60)
	if minutes < 60:
		return f"{minutes}:{rest:02d}"

	hours, minutes = divmod(minutes, 60)
	return f"{hours}:{minutes:02d}:{rest:02d}"


def _formatTime(time: datetime) -> str:
	"""
	Format an absolute time with its time zone.

	:param time: The time.
	:returns:    The time as ``YYYY-MM-DD hh:mm:ss <zone>``.
	"""
	return f"{time:%Y-%m-%d %H:%M:%S} {time.tzname() or 'local time'}"


def _fonts(fontFamilies: Iterable[str]) -> tuple[list[str], list[FT2Font]]:
	"""
	Load the fonts of the font families, which are installed.

	Installation is checked against matplotlib's font list first, because looking up a missing family logs a warning.

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


def _renderable(text: str, fonts: list[FT2Font]) -> str:
	"""
	Remove the characters none of the fonts has a glyph for, like emoji without an emoji font.

	matplotlib would draw an empty box for each of them and warn about every one.

	:param text:  The text.
	:param fonts: The fonts tried for a character.
	:returns:     The text without characters that can't be drawn, and without the whitespace left behind.
	"""
	if len(fonts) == 0:
		return text

	characters = (char for char in text if char.isspace() or any(font.get_char_index(ord(char)) != 0 for font in fonts))
	return " ".join("".join(characters).split())


def _legendTitle(layout: GanttLayout, categoryWidth: int) -> str:
	"""
	Compose the legend's title: the trace's times and totals, and the header of the statistics' columns.

	:param layout:        The layout of the trace.
	:param categoryWidth: Width of the category column in characters.
	:returns:             The title's lines.
	"""
	lines = [
		f"started     {_formatTime(layout.BeginTime)}",
		f"{'running at' if layout.IsRunning else 'finished':<11} {_formatTime(layout.EndTime)}",
		f"wall time   {_formatSeconds(layout.WallTime)}   runner time {_formatSeconds(layout.RunnerTime)}   "
		f"{layout.JobCount} jobs",
	]
	if layout.JobCount > 0:
		lines.append("")
		lines.append(f"{'':<{categoryWidth}}  jobs    wait min /  avg /  max       run min /  avg /  max")

	return "\n".join(lines)


def _legendLabel(layout: GanttLayout, category: str, categoryWidth: int) -> str:
	"""
	Compose the legend's label of a category: the category and the statistics of its jobs.

	:param layout:        The layout of the trace.
	:param category:      The category.
	:param categoryWidth: Width of the category column in characters.
	:returns:             The label.
	"""
	label = f"{category:<{categoryWidth}}"
	for entry in layout.IterateStatistics():
		if entry.Category != category:
			continue

		label += (
			f"  {entry.JobCount:>4}   "
			f"{_formatSeconds(entry.MinimumWaitTime):>9} /{_formatSeconds(entry.AverageWaitTime):>5} /"
			f"{_formatSeconds(entry.MaximumWaitTime):>5}   "
			f"{_formatSeconds(entry.MinimumRunTime):>11} /{_formatSeconds(entry.AverageRunTime):>5} /"
			f"{_formatSeconds(entry.MaximumRunTime):>5}"
		)

	return label


@export
def RenderGantt(
	layout:         GanttLayout,
	*,
	title:          Nullable[str] = None,
	width:          float = 16.0,
	rowHeight:      float = 0.22,
	fontSize:       float = 7.0,
	fontFamilies:   Iterable[str] = FONT_FAMILIES,
	legendLocation: str = "upper right"
) -> Figure:
	"""
	Render the layout of a trace as a Gantt chart.

	Every row shows its timespan's name, indented by its depth. The pipeline and a called workflow are a line from their
	begin to their end. A job's bar is colored by its row's category, a waiting bar is light gray, and a running bar is
	hatched. A bar too short to see is widened to a visible minimum. A character none of the installed fonts of
	``fontFamilies`` can draw - usually an emoji in a job's name - is left out of a label.

	The legend's title shows when the trace began and ended, its wall time, the runner time - the time all jobs ran,
	added up - and the number of jobs. Every category shows the number of its jobs, and their minimum, average and
	maximum waiting and running times.

	:param layout:         The layout of the trace.
	:param title:          Optional, the chart's title. Default: the trace's name and wall time.
	:param width:          Optional, width of the figure in inches. Default: ``16.0``.
	:param rowHeight:      Optional, height of a row in inches. Default: ``0.22``.
	:param fontSize:       Optional, font size of labels in points. Default: ``7.0``.
	:param fontFamilies:   Optional, font families tried in order for every character. Families that aren't installed
	                       are skipped. Default: :data:`FONT_FAMILIES`.
	:param legendLocation: Optional, the legend's location, as matplotlib's ``loc`` names it, e.g. ``'lower right'`` or
	                       ``'outside right upper'``. Default: ``'upper right'``.
	:returns:              The chart as a matplotlib figure, which isn't registered with :mod:`matplotlib.pyplot`.
	:raises TypeError:     If parameter 'layout' is not of type :class:`~pyTooling.Tracing.Render.GanttLayout`.
	:raises ValueError:    If parameter 'width', 'rowHeight' or 'fontSize' isn't positive.
	"""
	if not isinstance(layout, GanttLayout):
		ex = TypeError("Parameter 'layout' is not of type 'GanttLayout'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(layout)}'.")
		raise ex

	for parameter, value in (("width", width), ("rowHeight", rowHeight), ("fontSize", fontSize)):
		if not value > 0:
			ex = ValueError(f"Parameter '{parameter}' isn't positive.")
			ex.add_note(f"Got value '{value}'.")
			raise ex

	colors = {category: _PALETTE[position % len(_PALETTE)] for position, category in enumerate(layout.Categories)}
	rows = list(layout.IterateRows())
	duration = max(layout.Duration, 1.0)
	minimumWidth = duration / 1000
	families, fonts = _fonts(fontFamilies)
	rcParameters = {"font.size": fontSize} if len(families) == 0 else {"font.family": families, "font.size": fontSize}

	with rc_context(rcParameters):
		figure = Figure(figsize=(width, 1.6 + rowHeight * max(len(rows), 12)), layout="constrained")
		axes = figure.add_subplot()

		hasQueued = False
		hasLines = False
		for position, row in enumerate(rows):
			if row.Kind in (SpanKind.Pipeline, SpanKind.Workflow):
				for bar in row.Bars:
					hasLines = True
					style = "dashed" if bar.IsRunning else "solid"
					line = axes.hlines(position, bar.Begin, bar.End, colors=_LINE, linewidth=1.0, linestyles=style)
					ends = axes.vlines([bar.Begin, bar.End], position - 0.3, position + 0.3, colors=_LINE, linewidth=1.0)
					line.set_gid(f"span-{row.SpanID}")
					ends.set_gid(f"span-{row.SpanID}-ends")
				continue

			color = colors.get(row.Category, _NEUTRAL)
			for bar in row.Bars:
				hasQueued |= bar.IsQueued
				collection = axes.broken_barh(
					[(bar.Begin, max(bar.Duration, minimumWidth))],
					(position - 0.4, 0.8),
					facecolors=_QUEUED if bar.IsQueued else color,
					hatch="///" if bar.IsRunning else None,
					linewidth=0
				)
				collection.set_gid(f"span-{row.SpanID}-queued" if bar.IsQueued else f"span-{row.SpanID}")

		labels = [f"{'  ' * row.Depth}{_renderable(row.Name, fonts)}" for row in rows]
		axes.set_yticks(range(len(rows)), labels=labels)
		axes.tick_params(axis="y", length=0)
		for label, row in zip(axes.get_yticklabels(), rows):
			label.set_gid(f"label-{row.SpanID}")
		axes.set_ylim(len(rows) - 0.5, -0.5)
		axes.set_xlim(0, duration)
		axes.xaxis.set_major_formatter(FuncFormatter(_formatSeconds))
		axes.set_xlabel("time since the trace began")
		axes.grid(axis="x", linewidth=0.3, alpha=0.5)

		categoryWidth = max([len(category) for category in layout.Categories] + [len("pipeline, called workflow")])
		handles: list[Union[Patch, Line2D]] = [
			Patch(facecolor=colors[category], label=_legendLabel(layout, category, categoryWidth))
			for category in layout.Categories
		]
		if hasQueued:
			handles.append(Patch(facecolor=_QUEUED, label="waiting for a runner"))
		if hasLines:
			handles.append(
				Line2D([], [], color=_LINE, linewidth=1.0, marker="|", markersize=6, label="pipeline, called workflow")
			)

		monospace = {"family": MONOSPACE_FONT_FAMILY, "size": fontSize}
		axes.legend(
			handles=handles,
			title=_legendTitle(layout, categoryWidth),
			loc=legendLocation,
			prop=monospace,
			title_fontproperties=monospace,
			alignment="left",
			framealpha=0.95
		)

		if title is None:
			title = f"{layout.Trace.Name} ({_formatSeconds(layout.WallTime)})"
		figure.suptitle(_renderable(title, fonts), fontsize=fontSize + 2)

	return figure


def _collapsibleSVG(svg: str, layout: GanttLayout, figure: Figure, collapsedKinds: Iterable[str]) -> str:
	"""
	Add the script collapsing and expanding rows to an SVG file.

	The script knows every row's identifier, its parent among the shown rows, and whether it starts collapsed. The
	distance between two rows is converted from matplotlib's display coordinates into the SVG file's coordinates, which
	have 72 units per inch.

	:param svg:            The SVG file written by matplotlib.
	:param layout:         The layout of the rendered trace.
	:param figure:         The rendered figure, after it was written.
	:param collapsedKinds: The CI span kinds of rows, which start collapsed.
	:returns:              The SVG file with the style and script.
	"""
	axes = figure.get_axes()[0]
	pitch = abs(axes.transData.transform((0, 1))[1] - axes.transData.transform((0, 0))[1]) * 72 / figure.dpi

	rows = list(layout.IterateRows())
	shown = {row.SpanID for row in rows}
	kinds = set(collapsedKinds)
	data = {
		"pitch": round(pitch, 6),
		"rows": [
			{
				"id":        row.SpanID,
				"parent":    row.ParentSpanID if row.ParentSpanID in shown else None,
				"collapsed": row.Kind in kinds
			} for row in rows
		]
	}

	script = _COLLAPSE_SCRIPT.replace("/*DATA*/", json_dumps(data))
	addition = (
		f'<style type="text/css">{_COLLAPSE_STYLE}</style>\n'
		f'<script type="text/ecmascript"><![CDATA[{script}]]></script>\n'
	)
	position = svg.rindex("</svg>")
	return svg[:position] + addition + svg[position:]


@export
def WriteGantt(
	trace:          Trace,
	file:           Path,
	*,
	spanFilter:     Nullable[SpanFilter] = None,
	categorize:     SpanCategory = runnerCategory,
	now:            Nullable[datetime] = None,
	title:          Nullable[str] = None,
	width:          float = 16.0,
	rowHeight:      float = 0.22,
	fontSize:       float = 7.0,
	fontFamilies:   Iterable[str] = FONT_FAMILIES,
	legendLocation: str = "upper right",
	collapsible:    bool = False,
	collapsedKinds: Iterable[str] = (SpanKind.Job,),
	dpi:            int = 150
) -> None:
	"""
	Lay out a trace, render it as a Gantt chart, and write the chart to a file.

	The file format is chosen by the file's suffix, one of :data:`FORMATS`. Missing parent directories are created.

	A **collapsible** SVG file carries a script: a click on the label, bar or line of a row with sub-rows hides the rows
	below it and moves the following rows up, and a second click shows them again. A marker in front of the label shows
	the state. The script runs when the file is opened in a browser, or embedded with ``<object>`` or inline - not when
	it is shown as an image, e.g. by ``<img>`` or in Markdown.

	:param trace:          The trace to render.
	:param file:           Path of the file to write.
	:param spanFilter:     Optional, function deciding which timespans are shown, e.g. created by
	                       :func:`~pyTooling.Tracing.Render.ciSpanFilter`. Default: all timespans.
	:param categorize:     Optional, function returning a timespan's category. Default: :func:`runnerCategory`.
	:param now:            Optional, the time a running timespan's bar ends at. Default: the current system time.
	:param title:          Optional, the chart's title. Default: the trace's name and wall time.
	:param width:          Optional, width of the figure in inches. Default: ``16.0``.
	:param rowHeight:      Optional, height of a row in inches. Default: ``0.22``.
	:param fontSize:       Optional, font size of labels in points. Default: ``7.0``.
	:param fontFamilies:   Optional, font families tried in order for every character. Default: :data:`FONT_FAMILIES`.
	:param legendLocation: Optional, the legend's location, as matplotlib's ``loc`` names it. Default: ``'upper right'``.
	:param collapsible:    Optional, add the script collapsing and expanding rows to an SVG file. Default: ``False``.
	:param collapsedKinds: Optional, the CI span kinds of rows, which start collapsed in a collapsible SVG file.
	                       Default: jobs, so their steps are hidden until a job is expanded.
	:param dpi:            Optional, resolution of a PNG file in dots per inch. Default: ``150``.
	:raises TypeError:     If parameter 'file' is not of type :class:`~pathlib.Path`.
	:raises ValueError:    If the file's suffix isn't one of :data:`FORMATS`.
	:raises ValueError:    If parameter 'collapsible' is ``True``, but the file isn't an SVG file.
	:raises TracingError:  If the parent directories couldn't be created.
	:raises TracingError:  If the file couldn't be written.
	"""
	if not isinstance(file, Path):
		ex = TypeError("Parameter 'file' is not of type 'Path'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(file)}'.")
		raise ex
	elif (fileFormat := file.suffix.lower().lstrip(".")) not in FORMATS:
		ex = ValueError(f"File '{file}' has an unsupported format.")
		ex.add_note(f"Supported file suffixes: {', '.join(f'.{suffix}' for suffix in FORMATS)}")
		raise ex
	elif collapsible and fileFormat != "svg":
		ex = ValueError(f"File '{file}' can't be collapsible.")
		ex.add_note("Only an SVG file can carry the script collapsing rows.")
		raise ex

	layout = GanttLayout(trace, spanFilter=spanFilter, categorize=categorize, now=now)
	figure = RenderGantt(
		layout, title=title, width=width, rowHeight=rowHeight, fontSize=fontSize, fontFamilies=fontFamilies,
		legendLocation=legendLocation
	)

	try:
		file.parent.mkdir(parents=True, exist_ok=True)
	except OSError as ex:
		raise TracingError(f"Directory '{file.parent}' couldn't be created.") from ex

	families, _ = _fonts(fontFamilies)
	try:
		with rc_context({} if len(families) == 0 else {"font.family": families}):
			if not collapsible:
				figure.savefig(file, format=fileFormat, dpi=dpi)
			else:
				buffer = StringIO()
				figure.savefig(buffer, format="svg")
				file.write_text(_collapsibleSVG(buffer.getvalue(), layout, figure, collapsedKinds), encoding="utf-8")
	except OSError as ex:
		raise TracingError(f"File '{file}' couldn't be written.") from ex
