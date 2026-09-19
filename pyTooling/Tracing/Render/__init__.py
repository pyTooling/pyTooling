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

:class:`GanttLayout` arranges the timespans of a trace in rows, with times in seconds after the trace began, and
summarizes the jobs of a CI pipeline per runner category. A renderer like :mod:`pyTooling.Tracing.Render.Matplotlib`
only draws these rows and statistics, so every renderer shows the same chart.

.. hint::

   See :ref:`high-level help <TRACING/Render>` for explanations and usage examples.
"""
from datetime                    import datetime
from enum                        import Enum
from re                          import IGNORECASE, compile as re_compile
from statistics                  import fmean
from typing                      import Callable, Iterator, Optional as Nullable, Union

from pyTooling.Decorators        import export, readonly
from pyTooling.MetaClasses       import ExtendedType
from pyTooling.Common            import getFullyQualifiedName
from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import CI, OTLP, Result, SpanKind
from pyTooling.Tracing.CI.GitHub import GitHub


__all__ = ["SpanFilter", "SpanCategory", "MSYS2_SETUP_STEP", "QUEUED_LEGEND", "LINE_LEGEND"]

SpanFilter = Callable[[Span], bool]
"""A function deciding whether a timespan - and with it, its sub-spans - is shown."""

SpanCategory = Callable[[Span], str]
"""A function returning the category of a timespan, e.g. the runner it ran on. The empty string means no category."""

MSYS2_SETUP_STEP = re_compile(r"Setup MSYS2 for (\w+)", IGNORECASE)
"""Pattern of the step name setting up MSYS2 in a CI job, capturing the MSYS2 environment, e.g. ``UCRT64``."""

QUEUED_LEGEND = "waiting for a runner"
"""Legend entry of the bars showing the time a job waited for a runner."""

LINE_LEGEND = "pipeline, called workflow"
"""Legend entry of the lines spanning the pipeline or a called workflow."""


def _kind(span: Span) -> Nullable[str]:
	"""
	Return the CI span kind of a timespan.

	:param span: The timespan.
	:returns:    What the timespan represents, or ``None`` if the timespan doesn't say.
	"""
	return span[CI.Span.Kind] if CI.Span.Kind in span else None


def _result(span: Span) -> Nullable[str]:
	"""
	Return the CI result of a timespan.

	:param span: The timespan.
	:returns:    The task run's result, or ``None`` if the timespan has none.
	"""
	return span[OTLP.CICD.Pipeline.Task.Run.Result] if OTLP.CICD.Pipeline.Task.Run.Result in span else None


def _taskName(span: Span) -> Nullable[str]:
	"""
	Return the name of the task a timespan belongs to.

	:param span: The timespan.
	:returns:    The task's name, or ``None`` if the timespan doesn't carry one.
	"""
	return span[OTLP.CICD.Pipeline.Task.Name] if OTLP.CICD.Pipeline.Task.Name in span else None


@export
class StepExclusion(Enum):
	"""
	Which steps of CI jobs a filter created by :func:`ciSpanFilter` hides.
	"""
	Nothing = 0  #: Show every step.
	Skipped = 1  #: Hide the steps that were skipped.
	All =     2  #: Hide every step.


@export
def ciSpanFilter(
	excludeSteps:       Union[bool, StepExclusion] = StepExclusion.All,
	excludeSkippedJobs: bool = True
) -> SpanFilter:
	"""
	Create a span filter for the trace of a CI pipeline.

	Steps outnumber jobs by far - a pipeline of 74 jobs has more than 1600 steps, of which a third were skipped - and a
	skipped job has neither waited nor run.

	:param excludeSteps:       Optional, which steps to hide: ``True`` or :attr:`StepExclusion.All` hides every step,
	                           ``False`` or :attr:`StepExclusion.Nothing` none, and :attr:`StepExclusion.Skipped` the
	                           skipped ones. Default: :attr:`StepExclusion.All`.
	:param excludeSkippedJobs: Optional, hide the jobs that were skipped. Default: ``True``.
	:returns:                  The span filter.
	:raises TypeError:         If parameter 'excludeSteps' is neither of type :class:`bool` nor :class:`StepExclusion`.
	"""
	if isinstance(excludeSteps, bool):
		excludeSteps = StepExclusion.All if excludeSteps else StepExclusion.Nothing
	elif not isinstance(excludeSteps, StepExclusion):
		ex = TypeError("Parameter 'excludeSteps' is neither of type 'bool' nor 'StepExclusion'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(excludeSteps)}'.")
		raise ex

	def spanFilter(span: Span) -> bool:
		"""
		Nested function hiding steps and skipped jobs as configured.

		:param span: The timespan.
		:returns:    ``False``, if the timespan is hidden.
		"""
		kind = _kind(span)
		if kind == SpanKind.Step:
			if excludeSteps is StepExclusion.All:
				return False
			return excludeSteps is StepExclusion.Nothing or _result(span) != Result.Skip
		elif kind == SpanKind.Job and excludeSkippedJobs:
			return _result(span) != Result.Skip

		return True

	return spanFilter


@export
def msys2Environment(job: Span) -> Nullable[str]:
	"""
	Return the MSYS2 environment a CI job used.

	The environment is taken from a step of the job, which matches :data:`MSYS2_SETUP_STEP` and succeeded. A job running
	natively on Windows skips that step or sets up the environment ``native``.

	:param job: The job's timespan.
	:returns:   The environment in upper case, e.g. ``UCRT64``, or ``None`` if the job didn't use an MSYS2 environment.
	"""
	for step in job.IterateSubSpans():
		if (match := MSYS2_SETUP_STEP.search(step.Name)) is None or _result(step) != Result.Success:
			continue
		elif (environment := match.group(1).upper()) != "NATIVE":
			return environment

	return None


@export
def runnerCategory(span: Span) -> str:
	"""
	Span category naming the runner a timespan ran on, and the MSYS2 environment of a job using MSYS2.

	The runner is the first runner label of the timespan or its nearest ancestor. A job using an MSYS2 environment
	(see :func:`msys2Environment`) is a category of its own, e.g. ``windows-2025 + UCRT64``, because it takes
	significantly longer than a native job on the same runner.

	:param span: The timespan.
	:returns:    The category, or the empty string if neither the timespan nor an ancestor has a runner label.
	"""
	label = ""
	job: Nullable[Span] = None
	current: Nullable[Span] = span
	while current is not None:
		if job is None and _kind(current) == SpanKind.Job:
			job = current
		if label == "" and GitHub.Runner.Labels in current and len(labels := current[GitHub.Runner.Labels]) > 0:
			label = str(labels[0])
		current = current.Parent

	if label != "" and job is not None and (environment := msys2Environment(job)) is not None:
		return f"{label} + {environment}"

	return label


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
	def ParentSpanID(self) -> Nullable[str]:
		"""
		Read-only property to return the identifier of the row's parent timespan.

		:returns: The parent's identifier, as 16 hex digits, or ``None`` for the trace.
		"""
		return None if self._span.Parent is None else self._span.Parent.SpanID

	@readonly
	def Kind(self) -> Nullable[str]:
		"""
		Read-only property to return the CI span kind of the row's timespan.

		:returns: The value of :data:`~pyTooling.Tracing.CI.CI.Span.Kind`, or ``None`` if the timespan has none.
		"""
		return _kind(self._span)

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
class CategoryStatistics(metaclass=ExtendedType, slots=True):
	"""
	The waiting and running times of the jobs of one category, e.g. of one runner image.
	"""
	_category:  str          #: The category.
	_waitTimes: list[float]  #: Seconds each job waited for a runner.
	_runTimes:  list[float]  #: Seconds each job ran.

	def __init__(self, category: str) -> None:
		"""
		Initializes the statistics of a category without jobs.

		:param category: The category.
		"""
		self._category =  category
		self._waitTimes = []
		self._runTimes =  []

	def _AddJob(self, waitTime: float, runTime: float) -> None:
		"""
		Add a job's times to the statistics.

		:param waitTime: Seconds the job waited for a runner.
		:param runTime:  Seconds the job ran.
		"""
		self._waitTimes.append(waitTime)
		self._runTimes.append(runTime)

	@readonly
	def Category(self) -> str:
		"""
		Read-only property to access the category (:attr:`_category`).

		:returns: The category.
		"""
		return self._category

	@readonly
	def JobCount(self) -> int:
		"""
		Read-only property to return the number of jobs.

		:returns: Number of jobs.
		"""
		return len(self._runTimes)

	@readonly
	def WaitTimes(self) -> tuple[float, ...]:
		"""
		Read-only property to return the waiting times of all jobs (:attr:`_waitTimes`).

		:returns: Seconds each job waited for a runner.
		"""
		return tuple(self._waitTimes)

	@readonly
	def RunTimes(self) -> tuple[float, ...]:
		"""
		Read-only property to return the running times of all jobs (:attr:`_runTimes`).

		:returns: Seconds each job ran.
		"""
		return tuple(self._runTimes)

	@readonly
	def MinimumWaitTime(self) -> float:
		"""
		Read-only property to return the shortest time a job waited for a runner.

		:returns: Seconds.
		"""
		return min(self._waitTimes)

	@readonly
	def AverageWaitTime(self) -> float:
		"""
		Read-only property to return the average time a job waited for a runner.

		:returns: Seconds.
		"""
		return fmean(self._waitTimes)

	@readonly
	def MaximumWaitTime(self) -> float:
		"""
		Read-only property to return the longest time a job waited for a runner.

		:returns: Seconds.
		"""
		return max(self._waitTimes)

	@readonly
	def MinimumRunTime(self) -> float:
		"""
		Read-only property to return the shortest time a job ran.

		:returns: Seconds.
		"""
		return min(self._runTimes)

	@readonly
	def AverageRunTime(self) -> float:
		"""
		Read-only property to return the average time a job ran.

		:returns: Seconds.
		"""
		return fmean(self._runTimes)

	@readonly
	def MaximumRunTime(self) -> float:
		"""
		Read-only property to return the longest time a job ran.

		:returns: Seconds.
		"""
		return max(self._runTimes)

	@readonly
	def TotalRunTime(self) -> float:
		"""
		Read-only property to return the time all jobs ran, added up.

		:returns: Seconds.
		"""
		return sum(self._runTimes)


@export
class GanttLayout(metaclass=ExtendedType, slots=True):
	"""
	The layout of a trace as a Gantt chart: one row per shown timespan, in the trace's tree order, and the statistics of
	the trace's jobs per category.

	A timespan of kind ``queued`` is drawn on the row of the job directly following it, if that job has the same task
	name - otherwise the job is still waiting, and the waiting timespan gets a row of its own.

	The statistics count every job of the trace, which wasn't skipped and has a category - independently of the filter
	deciding which rows are shown.
	"""
	_trace:      Trace                          #: The trace laid out.
	_now:        datetime                       #: The time a running timespan's bar ends at.
	_spanFilter: Nullable[SpanFilter]           #: The function deciding which timespans are shown, or ``None`` for all.
	_categorize: SpanCategory                   #: The function returning a timespan's category.
	_rows:       list[GanttRow]                 #: The rows in tree order.
	_categories: dict[str, None]                #: The categories of rows and statistics, as an ordered set.
	_statistics: dict[str, CategoryStatistics]  #: The statistics of the jobs per category.
	_duration:   float                          #: The end of the last bar in seconds after the trace began.

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
		self._statistics = {}
		self._duration =   0.0

		self._AddRow(trace, 0, None)
		self._AddSubSpans(trace, 1)
		self._CollectStatistics(trace)

	def _Offset(self, time: datetime) -> float:
		"""
		Convert a time into seconds after the trace began.

		:param time: The time.
		:returns:    Seconds after the trace began.
		"""
		return (time - self._trace.StartTime).total_seconds()

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
		beginOffset = self._Offset(begin)
		endOffset = self._Offset(self._now if running else span.StopTime)

		return GanttBar(beginOffset, max(endOffset, beginOffset), queued, running)

	def _AddRow(self, span: Span, depth: int, queued: Nullable[Span]) -> None:
		"""
		Add a row for a timespan, with the bar of its waiting timespan in front, if given.

		:param span:   The timespan.
		:param depth:  Nesting depth of the timespan.
		:param queued: The timespan the job waited for a runner in, or ``None``.
		"""
		bars: list[GanttBar] = []
		for barSpan, isQueued in ((queued, True), (span, _kind(span) == SpanKind.Queued)):
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

			if _kind(span) == SpanKind.Queued:
				if pending is not None:
					self._AddRow(pending, depth, None)
				pending = span
				continue

			queued = None
			if pending is not None:
				taskName = _taskName(span)
				if _kind(span) == SpanKind.Job and taskName is not None and taskName == _taskName(pending):
					queued = pending
				else:
					self._AddRow(pending, depth, None)
				pending = None

			self._AddRow(span, depth, queued)
			self._AddSubSpans(span, depth + 1)

		if pending is not None:
			self._AddRow(pending, depth, None)

	def _CollectStatistics(self, parent: Span) -> None:
		"""
		Add the waiting and running times of the jobs below a timespan to the statistics of their categories.

		:param parent: The timespan.
		"""
		queued: dict[str, Span] = {}
		for span in parent.IterateSubSpans():
			kind = _kind(span)
			if kind == SpanKind.Queued and (taskName := _taskName(span)) is not None:
				queued[taskName] = span
			elif kind == SpanKind.Job and _result(span) != Result.Skip and span.StartTime is not None:
				if (category := self._categorize(span)) != "":
					waiting = queued.get(_taskName(span), None)
					waitTime = 0.0
					if waiting is not None and waiting.StartTime is not None:
						waitTime = self._Offset(span.StartTime) - self._Offset(waiting.StartTime)
					runTime = self._Offset(self._now if span.StopTime is None else span.StopTime) - self._Offset(span.StartTime)

					if category not in self._statistics:
						self._statistics[category] = CategoryStatistics(category)
						self._categories[category] = None
					self._statistics[category]._AddJob(max(waitTime, 0.0), max(runTime, 0.0))

			self._CollectStatistics(span)

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
	def BeginTime(self) -> datetime:
		"""
		Read-only property to access the time the trace began.

		:returns: The begin time, with the trace's time zone.
		"""
		return self._trace.StartTime

	@readonly
	def EndTime(self) -> datetime:
		"""
		Read-only property to return the time the trace ended, or the layout's current time while it is running.

		:returns: The end time, with the trace's time zone.
		"""
		return self._now if self._trace.StopTime is None else self._trace.StopTime

	@readonly
	def IsRunning(self) -> bool:
		"""
		Read-only property to return whether the trace is still running.

		:returns: ``True``, if the trace has no end time.
		"""
		return self._trace.StopTime is None

	@readonly
	def WallTime(self) -> float:
		"""
		Read-only property to return the time from the trace's begin to its end.

		:returns: Seconds.
		"""
		return self._Offset(self.EndTime)

	@readonly
	def RunnerTime(self) -> float:
		"""
		Read-only property to return the time all counted jobs ran, added up - the time runners were occupied.

		:returns: Seconds.
		"""
		return sum(statistics.TotalRunTime for statistics in self._statistics.values())

	@readonly
	def JobCount(self) -> int:
		"""
		Read-only property to return the number of counted jobs.

		:returns: Number of jobs, which weren't skipped and have a category.
		"""
		return sum(statistics.JobCount for statistics in self._statistics.values())

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

	def IterateStatistics(self) -> Iterator[CategoryStatistics]:
		"""
		Returns an iterator to iterate the statistics of all categories with counted jobs, in the order of
		:attr:`Categories`.

		:returns: Iterator to iterate the statistics.
		"""
		return (self._statistics[category] for category in self._categories if category in self._statistics)

	@readonly
	def Categories(self) -> tuple[str, ...]:
		"""
		Read-only property to return the categories of all rows and statistics (:attr:`_categories`).

		:returns: The categories in the order they first appear, without the empty string.
		"""
		return tuple(self._categories)


@export
def formatDuration(seconds: float) -> str:
	"""
	Format a duration as minutes and seconds, or as hours, minutes and seconds from one hour on.

	:param seconds: The duration in seconds.
	:returns:       The duration as ``m:ss`` or ``h:mm:ss``.
	"""
	minutes, rest = divmod(int(round(seconds)), 60)
	if minutes < 60:
		return f"{minutes}:{rest:02d}"

	hours, minutes = divmod(minutes, 60)
	return f"{hours}:{minutes:02d}:{rest:02d}"


@export
def formatTime(time: datetime) -> str:
	"""
	Format an absolute time with its time zone.

	:param time: The time.
	:returns:    The time as ``YYYY-MM-DD hh:mm:ss <zone>``.
	"""
	return f"{time:%Y-%m-%d %H:%M:%S} {time.tzname() or 'local time'}"


def _categoryWidth(layout: GanttLayout) -> int:
	"""
	Return the width of a legend's category column.

	:param layout: The layout of the trace.
	:returns:      Width in characters, fitting every category and :data:`LINE_LEGEND`.
	"""
	return max([len(category) for category in layout.Categories] + [len(LINE_LEGEND)])


@export
def legendTitle(layout: GanttLayout) -> str:
	"""
	Compose a legend's title: the trace's times and totals, and the header of the statistics' columns.

	The columns align with the labels of :func:`legendLabel` in a monospace font.

	:param layout: The layout of the trace.
	:returns:      The title's lines, separated by ``\\n``.
	"""
	lines = [
		f"started     {formatTime(layout.BeginTime)}",
		f"{'running at' if layout.IsRunning else 'finished':<11} {formatTime(layout.EndTime)}",
		f"wall time   {formatDuration(layout.WallTime)}   runner time {formatDuration(layout.RunnerTime)}   "
		f"{layout.JobCount} jobs",
	]
	if layout.JobCount > 0:
		lines.append("")
		lines.append(f"{'':<{_categoryWidth(layout)}}  jobs    wait min /  avg /  max       run min /  avg /  max")

	return "\n".join(lines)


@export
def legendLabel(layout: GanttLayout, category: str) -> str:
	"""
	Compose a legend's label of a category: the category and the statistics of its jobs.

	:param layout:   The layout of the trace.
	:param category: The category.
	:returns:        The label, whose columns align with the header of :func:`legendTitle` in a monospace font.
	"""
	label = f"{category:<{_categoryWidth(layout)}}"
	for entry in layout.IterateStatistics():
		if entry.Category != category:
			continue

		label += (
			f"  {entry.JobCount:>4}   "
			f"{formatDuration(entry.MinimumWaitTime):>9} /{formatDuration(entry.AverageWaitTime):>5} /"
			f"{formatDuration(entry.MaximumWaitTime):>5}   "
			f"{formatDuration(entry.MinimumRunTime):>11} /{formatDuration(entry.AverageRunTime):>5} /"
			f"{formatDuration(entry.MaximumRunTime):>5}"
		)

	return label
