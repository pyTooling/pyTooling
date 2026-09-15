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
Backend independent layout of a software execution trace as a Gantt chart.

:class:`GanttLayout` arranges the timespans of a trace in rows, with times in seconds after the trace began. A renderer
like :mod:`pyTooling.Tracing.Render.Matplotlib` only draws these rows, so every renderer shows the same chart.

.. hint::

   See :ref:`high-level help <TRACING/Render>` for explanations and usage examples.
"""
from datetime                    import datetime
from typing                      import Callable, Iterator, Optional as Nullable

from pyTooling.Decorators        import export, readonly
from pyTooling.MetaClasses       import ExtendedType
from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import SPAN_KIND, SPAN_KIND_QUEUED, SPAN_KIND_JOB, SPAN_KIND_STEP, TASK_NAME
from pyTooling.Tracing.CI.GitHub import RUNNER_LABELS


__all__ = ["SpanFilter", "SpanCategory"]

SpanFilter = Callable[[Span], bool]
"""A function deciding whether a timespan - and with it, its sub-spans - is shown."""

SpanCategory = Callable[[Span], str]
"""A function returning the category of a timespan, e.g. the runner it ran on. The empty string means no category."""


def _kind(span: Span) -> Nullable[str]:
	"""
	Return the CI span kind of a timespan.

	:param span: The timespan.
	:returns:    The value of :data:`~pyTooling.Tracing.CI.SPAN_KIND`, or ``None`` if the timespan has none.
	"""
	return span[SPAN_KIND] if SPAN_KIND in span else None


@export
def excludeSteps(span: Span) -> bool:
	"""
	Span filter hiding the steps of CI jobs, which outnumber the jobs by far.

	:param span: The timespan.
	:returns:    ``False`` for a step, otherwise ``True``.
	"""
	return _kind(span) != SPAN_KIND_STEP


@export
def runnerCategory(span: Span) -> str:
	"""
	Span category naming the runner a timespan ran on: the first runner label of the timespan or its nearest ancestor.

	:param span: The timespan.
	:returns:    The runner label, or the empty string if neither the timespan nor an ancestor has one.
	"""
	current: Nullable[Span] = span
	while current is not None:
		if RUNNER_LABELS in current and len(labels := current[RUNNER_LABELS]) > 0:
			return str(labels[0])
		current = current.Parent

	return ""


@export
class GanttBar(metaclass=ExtendedType, slots=True):
	"""
	A bar of a Gantt chart's row: a time range in seconds after the trace began.
	"""
	_begin:   float  #: Begin of the bar in seconds after the trace began.
	_end:     float  #: End of the bar in seconds after the trace began.
	_queued:  bool   #: The bar is the time a job waited for a runner.
	_running: bool   #: The bar's timespan is still running, so the bar ends at the layout's current time.

	def __init__(self, begin: float, end: float, queued: bool, running: bool) -> None:
		"""
		Initializes a bar.

		:param begin:   Begin of the bar in seconds after the trace began.
		:param end:     End of the bar in seconds after the trace began.
		:param queued:  The bar is the time a job waited for a runner.
		:param running: The bar's timespan is still running.
		"""
		self._begin =   begin
		self._end =     end
		self._queued =  queued
		self._running = running

	@readonly
	def Begin(self) -> float:
		"""
		Read-only property to access the begin of the bar (:attr:`_begin`).

		:returns: Begin in seconds after the trace began.
		"""
		return self._begin

	@readonly
	def End(self) -> float:
		"""
		Read-only property to access the end of the bar (:attr:`_end`).

		:returns: End in seconds after the trace began.
		"""
		return self._end

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property to return the length of the bar.

		:returns: Length in seconds.
		"""
		return self._end - self._begin

	@readonly
	def IsQueued(self) -> bool:
		"""
		Read-only property to access whether the bar is the time a job waited for a runner (:attr:`_queued`).

		:returns: ``True``, if the bar shows waiting.
		"""
		return self._queued

	@readonly
	def IsRunning(self) -> bool:
		"""
		Read-only property to access whether the bar's timespan is still running (:attr:`_running`).

		:returns: ``True``, if the bar ends at the layout's current time.
		"""
		return self._running


@export
class GanttRow(metaclass=ExtendedType, slots=True):
	"""
	A row of a Gantt chart: one timespan, with the bar a job waited for a runner in front of the job's bar.
	"""
	_span:     Span            #: The timespan shown by the row.
	_depth:    int             #: Nesting depth of the timespan, where the trace is at depth 0.
	_category: str             #: Category of the timespan, or the empty string.
	_bars:     list[GanttBar]  #: The row's bars, in time order.

	def __init__(self, span: Span, depth: int, category: str, bars: list[GanttBar]) -> None:
		"""
		Initializes a row.

		:param span:     The timespan shown by the row.
		:param depth:    Nesting depth of the timespan, where the trace is at depth 0.
		:param category: Category of the timespan, or the empty string.
		:param bars:     The row's bars, in time order.
		"""
		self._span =     span
		self._depth =    depth
		self._category = category
		self._bars =     bars

	@readonly
	def Span(self) -> Span:
		"""
		Read-only property to access the timespan shown by the row (:attr:`_span`).

		:returns: The timespan.
		"""
		return self._span

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the name of the row's timespan.

		:returns: The timespan's name.
		"""
		return self._span.Name

	@readonly
	def SpanID(self) -> str:
		"""
		Read-only property to access the identifier of the row's timespan.

		:returns: The timespan's identifier, as 16 hex digits.
		"""
		return self._span.SpanID

	@readonly
	def Depth(self) -> int:
		"""
		Read-only property to access the nesting depth of the row's timespan (:attr:`_depth`).

		:returns: The depth, where the trace is at depth 0.
		"""
		return self._depth

	@readonly
	def Category(self) -> str:
		"""
		Read-only property to access the category of the row's timespan (:attr:`_category`).

		:returns: The category, or the empty string.
		"""
		return self._category

	@readonly
	def Bars(self) -> tuple[GanttBar, ...]:
		"""
		Read-only property to return the row's bars (:attr:`_bars`).

		:returns: The bars in time order. A timespan without a begin time has none.
		"""
		return tuple(self._bars)


@export
class GanttLayout(metaclass=ExtendedType, slots=True):
	"""
	The layout of a trace as a Gantt chart: one row per shown timespan, in the trace's tree order.

	A timespan of kind ``queued`` is drawn on the row of the job directly following it, if that job has the same task
	name - otherwise the job is still waiting, and the waiting timespan gets a row of its own.
	"""
	_trace:      Trace                  #: The trace laid out.
	_now:        datetime               #: The time a running timespan's bar ends at.
	_spanFilter: Nullable[SpanFilter]   #: The function deciding which timespans are shown, or ``None`` for all.
	_categorize: SpanCategory           #: The function returning a timespan's category.
	_rows:       list[GanttRow]         #: The rows in tree order.
	_categories: dict[str, None]        #: The categories of all rows, in the order they appear, as an ordered set.
	_duration:   float                  #: The end of the last bar in seconds after the trace began.

	def __init__(
		self,
		trace:      Trace,
		*,
		spanFilter: Nullable[SpanFilter] = None,
		categorize: SpanCategory = runnerCategory,
		now:        Nullable[datetime] = None
	) -> None:
		"""
		Initializes the layout of a trace.

		:param trace:         The trace to lay out.
		:param spanFilter:    Optional, function deciding which timespans are shown. A hidden timespan hides its
		                      sub-spans. Default: all timespans are shown.
		:param categorize:    Optional, function returning a timespan's category. Default: :func:`runnerCategory`.
		:param now:           Optional, the time a running timespan's bar ends at. Default: the current system time.
		:raises TypeError:    If parameter 'trace' is not of type :class:`~pyTooling.Tracing.Trace`.
		:raises TypeError:    If parameter 'now' is not of type :class:`~datetime.datetime`.
		:raises TracingError: If the trace has no begin time.
		"""
		if not isinstance(trace, Trace):
			ex = TypeError("Parameter 'trace' is not of type 'Trace'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(trace)}'.")
			raise ex
		elif (begin := trace.StartTime) is None:
			ex = TracingError(f"Trace '{trace.Name}' has no begin time, so it can't be laid out.")
			ex.add_note("Lay out a trace after it was entered, or construct it with recorded times.")
			raise ex

		if now is None:
			now = datetime.now(begin.tzinfo)
		elif not isinstance(now, datetime):
			ex = TypeError("Parameter 'now' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(now)}'.")
			raise ex

		self._trace =      trace
		self._now =        now
		self._spanFilter = spanFilter
		self._categorize = categorize
		self._rows =       []
		self._categories = {}
		self._duration =   0.0

		self._AddRow(trace, 0, None)
		self._AddSubSpans(trace, 1)

	def _Bar(self, span: Span, queued: bool) -> Nullable[GanttBar]:
		"""
		Create the bar of a timespan.

		:param span:   The timespan.
		:param queued: The timespan is the time a job waited for a runner.
		:returns:      The bar, or ``None`` if the timespan has no begin time.
		"""
		if (begin := span.StartTime) is None:
			return None

		running = span.StopTime is None
		beginOffset = (begin - self._trace.StartTime).total_seconds()
		endOffset = ((self._now if running else span.StopTime) - self._trace.StartTime).total_seconds()

		return GanttBar(beginOffset, max(endOffset, beginOffset), queued, running)

	def _AddRow(self, span: Span, depth: int, queued: Nullable[Span]) -> None:
		"""
		Add a row for a timespan, with the bar of its waiting timespan in front, if given.

		:param span:   The timespan.
		:param depth:  Nesting depth of the timespan.
		:param queued: The timespan the job waited for a runner in, or ``None``.
		"""
		bars: list[GanttBar] = []
		for barSpan, isQueued in ((queued, True), (span, _kind(span) == SPAN_KIND_QUEUED)):
			if barSpan is not None and (bar := self._Bar(barSpan, isQueued)) is not None:
				bars.append(bar)
				self._duration = max(self._duration, bar.End)

		category = self._categorize(span)
		if category != "":
			self._categories[category] = None

		self._rows.append(GanttRow(span, depth, category, bars))

	def _AddSubSpans(self, parent: Span, depth: int) -> None:
		"""
		Add rows for the shown sub-spans of a timespan, and recursively for theirs.

		:param parent: The timespan.
		:param depth:  Nesting depth of the sub-spans.
		"""
		pending: Nullable[Span] = None
		for span in parent.IterateSubSpans():
			if self._spanFilter is not None and not self._spanFilter(span):
				continue

			if _kind(span) == SPAN_KIND_QUEUED:
				if pending is not None:
					self._AddRow(pending, depth, None)
				pending = span
				continue

			queued = None
			if pending is not None:
				if _kind(span) == SPAN_KIND_JOB and TASK_NAME in span and TASK_NAME in pending and span[TASK_NAME] == pending[TASK_NAME]:
					queued = pending
				else:
					self._AddRow(pending, depth, None)
				pending = None

			self._AddRow(span, depth, queued)
			self._AddSubSpans(span, depth + 1)

		if pending is not None:
			self._AddRow(pending, depth, None)

	@readonly
	def Trace(self) -> Trace:
		"""
		Read-only property to access the trace laid out (:attr:`_trace`).

		:returns: The trace.
		"""
		return self._trace

	@readonly
	def Now(self) -> datetime:
		"""
		Read-only property to access the time a running timespan's bar ends at (:attr:`_now`).

		:returns: The current time of the layout.
		"""
		return self._now

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property to access the end of the last bar (:attr:`_duration`).

		:returns: The end in seconds after the trace began.
		"""
		return self._duration

	@readonly
	def RowCount(self) -> int:
		"""
		Read-only property to return the number of rows.

		:returns: Number of rows.
		"""
		return len(self._rows)

	def IterateRows(self) -> Iterator[GanttRow]:
		"""
		Returns an iterator to iterate all rows in tree order.

		:returns: Iterator to iterate all rows.
		"""
		return iter(self._rows)

	@readonly
	def Categories(self) -> tuple[str, ...]:
		"""
		Read-only property to return the categories of all rows (:attr:`_categories`).

		:returns: The categories in the order they first appear, without the empty string.
		"""
		return tuple(self._categories)
