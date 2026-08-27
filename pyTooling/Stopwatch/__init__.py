# ==================================================================================================================== #
#              _____           _ _               ____  _                           _       _                           #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ ___  _ ____      ____ _| |_ ___| |__                        #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __/ _ \| '_ \ \ /\ / / _` | __/ __| '_ \                       #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | || (_) | |_) \ V  V / (_| | || (__| | | |                      #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__\___/| .__/ \_/\_/ \__,_|\__\___|_| |_|                      #
#  |_|    |___/                          |___/                 |_|                                                     #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A stopwatch to measure execution times.

.. hint::

   See :ref:`high-level help <COMMON/Stopwatch>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Tracing`
      |rarr| Nested timespans instead of a single measurement, for tracing an execution.
   :mod:`pyTooling.Process`
      |rarr| The process' memory usage, next to its runtime.
"""
from __future__            import annotations

from datetime              import datetime
from time                  import perf_counter_ns
from types                 import TracebackType
from typing                import Optional as Nullable, Iterator, Self

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import SlottedObject
from pyTooling.Exceptions  import ToolingException


@export
class StopwatchError(ToolingException):
	"""This exception is caused by wrong usage of the stopwatch."""


@export
class ExcludeContextManager:
	"""
	A stopwatch context manager for excluding certain time spans from measurement.

	While a normal stopwatch's embedded context manager (re)starts the stopwatch on every *enter* event and pauses the
	stopwatch on every *exit* event, this context manager pauses on *enter* events and restarts on every *exit* event.
	"""
	_stopwatch: Stopwatch  #: Reference to the stopwatch.

	def __init__(self, stopwatch: Stopwatch) -> None:
		"""
		Initializes an excluding context manager.

		:param stopwatch: Reference to the stopwatch.
		"""
		self._stopwatch = stopwatch

	def __enter__(self) -> Self:
		"""
		Enter the context and pause the stopwatch.

		:returns: Excluding stopwatch context manager instance.
		"""
		self._stopwatch.Pause()

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and restart stopwatch.

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		:returns:        ``None``
		"""
		self._stopwatch.Resume()


@export
class Stopwatch(SlottedObject):
	"""
	The stopwatch implements a solution to measure and collect timings.

	The time measurement can be started, paused, resumed and stopped. More over, split times can be taken too. The
	measurement is based on :func:`time.perf_counter_ns`. Additionally, starting and stopping is preserved as absolute
	time via :meth:`datetime.datetime.now`.

	Every split time taken is a time delta to the previous operation. These are preserved in an internal sequence of
	splits. This sequence includes time deltas of activity and inactivity. Thus, a running stopwatch can be split as well
	as a paused stopwatch.

	The stopwatch can also be used in a :ref:`with-statement <with>`, because it implements the :ref:`context manager protocol <context-managers>`.
	"""

	_name:         Nullable[str]  #: Optional name of the stopwatch.
	_preferPause:  bool           #: If ``True``, the context manager pauses instead of stopping on exit.
	_digits:       int            #: Number of fractional digits ``__str__`` renders the duration with.

	_beginTime:    Nullable[datetime]        #: Absolute time when the stopwatch was started.
	_endTime:      Nullable[datetime]        #: Absolute time when the stopwatch was stopped.
	_startTime:    Nullable[int]             #: Performance counter in ns when the stopwatch was started.
	_resumeTime:   Nullable[int]             #: Performance counter in ns of the latest resume operation.
	_pauseTime:    Nullable[int]             #: Performance counter in ns of the latest pause operation.
	_stopTime:     Nullable[int]             #: Performance counter in ns when the stopwatch was stopped.
	_totalTime:    Nullable[int]             #: Duration in ns from starting to stopping, activity and inactivity.
	_splits:       list[tuple[float, bool]]  #: Split times as (duration, is-active) pairs, in the order they were taken.

	_excludeContextManager: ExcludeContextManager  #: The nested context manager excluding time spans from measurement.

	def __init__(
		self,
		name: Nullable[str] = None,
		started: bool = False,
		preferPause: bool = False,
		digits: int = 3
	) -> None:
		"""
		Initializes the fields of the stopwatch.

		If parameter ``started`` is set to true, the stopwatch will immediately start.

		:param name:        Optional, name of the stopwatch.
		:param started:     Optional, if ``True``, start the stopwatch immediately.
		:param preferPause: Optional, if ``True``, ``__exit__(...)`` prefers pause over stop behavior.
		:param digits:      Optional, number of fractional digits :meth:`__str__` renders the duration with.
		:raises TypeError:  If parameter 'digits' is not of type :class:`int`.
		:raises ValueError: If parameter 'digits' is negative or greater than 9.
		"""
		if not isinstance(digits, int):
			ex = TypeError("Parameter 'digits' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(digits)}'.")
			raise ex
		elif not 0 <= digits <= 9:
			ex = ValueError(f"Parameter 'digits' is out of range 0..9. Got {digits}.")
			ex.add_note("A duration in seconds has at most 9 digits (nanoseconds).")
			raise ex

		self._name =         name
		self._preferPause =  preferPause
		self._digits =       digits

		self._endTime =      None
		self._pauseTime =    None
		self._stopTime =     None
		self._totalTime =    None
		self._splits =       []

		self._excludeContextManager = None

		if started is False:
			self._beginTime =  None
			self._startTime =  None
			self._resumeTime = None
		else:
			self._beginTime =  datetime.now()
			self._resumeTime = self._startTime = perf_counter_ns()

	def Start(self) -> None:
		"""
		Start the stopwatch.

		A stopwatch can only be started once. There is no restart or reset operation provided.

		:raises StopwatchError: If stopwatch was already started.
		:raises StopwatchError: If stopwatch was already started and stopped.
		"""
		if self._startTime is not None:
			raise StopwatchError("Stopwatch was already started.")
		if self._stopTime is not None:
			raise StopwatchError("Stopwatch was already used (started and stopped).")

		self._beginTime = datetime.now()
		self._resumeTime = self._startTime = perf_counter_ns()

	def Split(self) -> float:
		"""
		Take a split time and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be running to take a split time. See property :data:`IsRunning` to check if the stopwatch
		is running and the split operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the first split.
		* the duration from last resume to this split.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started or resumed.
		"""
		pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchError("Stopwatch was not started or resumed.")

		diff = (pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = pauseTime

		return diff

	def Pause(self) -> float:
		"""
		Pause the stopwatch and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be running to pause it. See property :data:`IsRunning` to check if the stopwatch is running
		and the pause operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the first pause.
		* the duration from last resume to this pause.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started or resumed.
		"""
		self._pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchError("Stopwatch was not started or resumed.")

		diff = (self._pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = None

		return diff

	def Resume(self) -> float:
		"""
		Resume the stopwatch and return the time delta to the previous pause operation.

		The stopwatch needs to be paused to resume it. See property :data:`IsPaused` to check if the stopwatch is paused
		and the resume operation is possible. |br|
		The time delta will be the duration from last pause to this resume.

		:returns:               Duration in seconds since last pause operation
		:raises StopwatchError: If stopwatch was not paused.
		"""
		self._resumeTime = perf_counter_ns()

		if self._pauseTime is None:
			raise StopwatchError("Stopwatch was not paused.")

		diff = (self._resumeTime - self._pauseTime) / 1e9
		self._splits.append((diff, False))
		self._pauseTime = None

		return diff

	def Stop(self) -> float:
		"""
		Stop the stopwatch and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be started to stop it. See property :data:`IsStarted` to check if the stopwatch was started
		and the stop operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the stop operation.
		* the duration from last resume to the stop operation.

		:returns:               Duration in seconds since last stopwatch operation
		:raises StopwatchError: If stopwatch was not started.
		:raises StopwatchError: If stopwatch was already stopped.
		"""
		self._stopTime = perf_counter_ns()
		self._endTime =  datetime.now()

		if self._startTime is None:
			raise StopwatchError("Stopwatch was never started.")
		if self._totalTime is not None:
			raise StopwatchError("Stopwatch was already stopped.")

		if len(self._splits) == 0:    # was never paused
			diff = (self._stopTime - self._startTime) / 1e9
		elif self._resumeTime is None:    # is paused
			diff = (self._stopTime - self._pauseTime) / 1e9
			self._splits.append((diff, False))
		else:                           # is running
			diff = (self._stopTime - self._resumeTime) / 1e9
			self._splits.append((diff, True))

		self._pauseTime =  None
		self._resumeTime = None
		self._totalTime =  self._stopTime - self._startTime

		# FIXME: why is this unused?
		beginEndDiff = self._endTime - self._beginTime

		return diff

	@property
	def Digits(self) -> int:
		"""
		Property to get and set the number of fractional digits (:attr:`_digits`) used by :meth:`__str__`.

		The measurement itself is unaffected - this only decides how many digits of the duration in seconds are
		rendered. It defaults to ``3``, which is milliseconds.

		:returns:           Number of fractional digits.
		:raises TypeError:  If the assigned value is not of type :class:`int`.
		:raises ValueError: If the assigned value is negative or greater than 9.
		"""
		return self._digits

	@Digits.setter
	def Digits(self, digits: int) -> None:
		if not isinstance(digits, int):
			ex = TypeError("Parameter 'digits' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(digits)}'.")
			raise ex
		elif not 0 <= digits <= 9:
			ex = ValueError(f"Parameter 'digits' is out of range 0..9. Got {digits}.")
			ex.add_note("A duration in seconds has at most 9 digits (nanoseconds).")
			raise ex

		self._digits = digits

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property returning the name of the stopwatch.

		:returns: Name of the stopwatch.
		"""
		return self._name

	@readonly
	def IsStarted(self) -> bool:
		"""
		Read-only property returning the IsStarted state of the stopwatch.

		:returns: True, if stopwatch was started.
		"""
		return self._startTime is not None and self._stopTime is None

	@readonly
	def IsRunning(self) -> bool:
		"""
		Read-only property returning the IsRunning state of the stopwatch.

		:returns: True, if stopwatch was started and is currently not paused.
		"""
		return self._startTime is not None and self._resumeTime is not None

	@readonly
	def IsPaused(self) -> bool:
		"""
		Read-only property returning the IsPaused state of the stopwatch.

		:returns: True, if stopwatch was started and is currently paused.
		"""
		return self._startTime is not None and self._pauseTime is not None

	@readonly
	def IsStopped(self) -> bool:
		"""
		Read-only property returning the IsStopped state of the stopwatch.

		:returns: True, if stopwatch was stopped.
		"""
		return self._stopTime is not None

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was started.

		:returns: The time when the stopwatch was started, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was stopped.

		:returns: The time when the stopwatch was stopped, otherwise None.
		"""
		return self._endTime

	@readonly
	def HasSplitTimes(self) -> bool:
		"""
		Read-only property checking if split times have been taken.

		:returns: True, if at least one split time has been taken.
		"""
		return len(self._splits) > 0

	@readonly
	def SplitCount(self) -> int:
		"""
		Read-only property returning the number of split times.

		:returns: Number of split times.
		"""
		return len(self._splits)

	@readonly
	def ActiveCount(self) -> int:
		"""
		Read-only property returning the number of active split times.

		A running stopwatch is inside an active span that hasn't been recorded yet, and that span is counted here -
		the result is what the stopwatch would report if it were stopped right now. This matches
		:attr:`Activity`, which includes the running span's duration.

		:returns: Number of active split times, including the one in progress.
		"""
		if self._startTime is None:
			return 0

		return len([t for t, a in self._splits if a is True]) + (1 if self._resumeTime is not None else 0)

	@readonly
	def InactiveCount(self) -> int:
		"""
		Read-only property returning the number of inactive split times.

		A paused stopwatch is inside an inactive span that hasn't been recorded yet, and that span is counted here -
		the result is what the stopwatch would report if it were stopped right now. This matches
		:attr:`Inactivity`, which includes the paused span's duration.

		:returns: Number of inactive split times, including the one in progress.
		"""
		if self._startTime is None:
			return 0

		return len([t for t, a in self._splits if a is False]) + (1 if self._pauseTime is not None else 0)

	@readonly
	def Activity(self) -> float:
		"""
		Read-only property returning the duration of all active split times.

		If the stopwatch is currently running, the duration since start or last resume operation will be included.

		:returns: Duration of all active split times in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		if self._startTime is None:
			return 0.0

		currentDiff = 0.0 if self._resumeTime is None else ((perf_counter_ns() - self._resumeTime) / 1e9)
		return sum(t for t, a in self._splits if a is True) + currentDiff

	@readonly
	def Inactivity(self) -> float:
		"""
		Read-only property returning the duration of all inactive split times.

		If the stopwatch is currently paused, the duration since last pause operation will be included.

		:returns: Duration of all inactive split times in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		if self._startTime is None:
			return 0.0

		currentDiff = 0.0 if self._pauseTime is None else ((perf_counter_ns() - self._pauseTime) / 1e9)
		return sum(t for t, a in self._splits if a is False) + currentDiff

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property returning the duration from start operation to stop operation.

		If the stopwatch is not yet stopped, the duration from start to now is returned.

		:returns: Duration since stopwatch was started in seconds. If the stopwatch was never started, the return value will
		          be 0.0.
		"""
		if self._startTime is None:
			return 0.0

		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e9

	@readonly
	def Exclude(self) -> ExcludeContextManager:
		"""
		Return an *exclude* context manager for the stopwatch instance.

		:returns: An excluding context manager.
		"""
		if self._excludeContextManager is None:
			self._excludeContextManager = ExcludeContextManager(self)

		return self._excludeContextManager

	def __enter__(self) -> Self:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__enter__(...)`` method.

		An unstarted stopwatch will be started. A paused stopwatch will be resumed.

		:returns:               The stopwatch itself.
		:raises StopwatchError: If the stopwatch was already started.
		"""
		if self._startTime is None:           # start stopwatch
			self._beginTime = datetime.now()
			self._resumeTime = self._startTime = perf_counter_ns()
		elif self._pauseTime is not None:     # resume after pause
			self._resumeTime = perf_counter_ns()

			diff = (self._resumeTime - self._pauseTime) / 1e9
			self._splits.append((diff, False))
			self._pauseTime = None
		elif self._resumeTime is not None:    # is running?
			raise StopwatchError("Stopwatch is currently running and can not be started/resumed again.")
		elif self._stopTime is not None:      # is stopped?
			raise StopwatchError("Stopwatch was already stopped.")
		else:
			raise StopwatchError("Internal error.")

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__exit__(...)`` method.

		A running stopwatch will be paused or stopped depending on the configured ``preferPause`` behavior.

		:param exc_type:        Exception type, otherwise None.
		:param exc_val:         Exception object, otherwise None.
		:param exc_tb:          Exception's traceback, otherwise None.
		:returns:               True, if exceptions should be suppressed.
		:raises StopwatchError: If the stopwatch was already stopped.
		"""
		if self._startTime is None:           # never started?
			raise StopwatchError("Stopwatch was never started.")
		elif self._stopTime is not None:
			raise StopwatchError("Stopwatch was already stopped.")
		elif self._resumeTime is not None:    # pause or stop
			if self._preferPause:
				self._pauseTime = perf_counter_ns()
				diff = (self._pauseTime - self._resumeTime) / 1e9
				self._splits.append((diff, True))
				self._resumeTime = None
			else:
				self._stopTime = perf_counter_ns()
				self._endTime =  datetime.now()

				diff = (self._stopTime - self._resumeTime) / 1e9
				self._splits.append((diff, True))

				self._pauseTime =  None
				self._resumeTime = None
				self._totalTime =  self._stopTime - self._startTime
		else:
			raise StopwatchError("Stopwatch was not resumed.")

	def __len__(self) -> int:
		"""
		Implementation of ``len(...)`` to return the number of split times.

		:returns: Number of split times.
		"""
		return len(self._splits)

	def __getitem__(self, index: int) -> tuple[float, bool]:
		"""
		Implementation of ``split = object[i]`` to return the i-th split time.

		:param index:     Index to access the i-th split time.
		:returns:         i-th split time as a tuple of: |br|
		                  (1) delta time to the previous stopwatch operation and |br|
		                  (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		:raises KeyError: If index *i* doesn't exist.
		"""
		return self._splits[index]

	def __iter__(self) -> Iterator[tuple[float, bool]]:
		"""
		Return an iterator of tuples to iterate all split times.

		If the stopwatch is not stopped yet, the last split won't be included.

		:returns: Iterator of split time tuples of: |br|
		          (1) delta time to the previous stopwatch operation and |br|
		          (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		"""
		return self._splits.__iter__()

	def _durationInNanoseconds(self) -> int:
		"""
		Return the measured duration in nanoseconds.

		:meth:`__format__` needs whole nanoseconds to split into fields, and :attr:`Duration` offers only seconds as a
		float, so this reads the counter directly rather than multiplying that back up.

		Precision is not the reason. A float holds a duration in seconds exactly, to the nanosecond, up to
		:math:`2^{53}` ns - a little over 104 days - which no stopwatch will ever reach.

		:returns: Duration from start to stop in nanoseconds, or from start to now while the stopwatch runs. Zero, if
		          the stopwatch was never started.
		"""
		if self._startTime is None:
			return 0
		elif self._totalTime is not None:    # was stopped, so the total is final
			return self._totalTime

		return perf_counter_ns() - self._startTime

	def __format__(self, formatSpec: str) -> str:
		"""
		Return the measured duration according to the format specification.

		.. topic:: Format Specifiers

		   An **uppercase** specifier is a field of the duration as it would be displayed. A **lowercase** specifier is
		   the whole duration expressed in one unit, which is what a report or a comparison wants.

		   +-----------+--------------------------------------------------------+
		   | Specifier | Meaning                                                |
		   +===========+========================================================+
		   | ``%H``    | hours, not capped - a 26 hour measurement shows ``26`` |
		   +-----------+--------------------------------------------------------+
		   | ``%M``    | minutes, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%S``    | seconds, ``00`` to ``59``                              |
		   +-----------+--------------------------------------------------------+
		   | ``%L``    | fractional seconds, 3 digits (milliseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%U``    | fractional seconds, 6 digits (microseconds)            |
		   +-----------+--------------------------------------------------------+
		   | ``%N``    | fractional seconds, 9 digits (nanoseconds)             |
		   +-----------+--------------------------------------------------------+
		   | ``%s``    | the whole duration in seconds                          |
		   +-----------+--------------------------------------------------------+
		   | ``%m``    | the whole duration in milliseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%u``    | the whole duration in microseconds                     |
		   +-----------+--------------------------------------------------------+
		   | ``%n``    | the whole duration in nanoseconds                      |
		   +-----------+--------------------------------------------------------+

		   The fractional specifiers are truncations of the same fraction, so ``%S.%U`` renders ``04.123456`` without
		   having to be combined with anything. ``%H`` is not capped, so ``%H:%M:%S`` never silently drops a day.

		   ``%%`` renders a literal percent sign. An empty format specification returns :meth:`__str__`.

		:param formatSpec:  The format specification, using ``%``-placeholders for the duration's parts.
		:returns:           The formatted duration.
		:raises ValueError: If the format specification contains an unknown placeholder.
		"""
		if formatSpec == "":
			return self.__str__()

		nanoseconds = self._durationInNanoseconds()
		seconds, fraction = divmod(nanoseconds, 1_000_000_000)
		minutes, secondField = divmod(seconds, 60)
		hours, minuteField = divmod(minutes, 60)

		result = formatSpec
		for placeholder, value in (
			("%H", f"{hours:02}"),
			("%M", f"{minuteField:02}"),
			("%S", f"{secondField:02}"),
			("%L", f"{fraction // 1_000_000:03}"),
			("%U", f"{fraction // 1_000:06}"),
			("%N", f"{fraction:09}"),
			("%s", f"{nanoseconds // 1_000_000_000}"),
			("%m", f"{nanoseconds // 1_000_000}"),
			("%u", f"{nanoseconds // 1_000}"),
			("%n", f"{nanoseconds}"),
		):
			result = result.replace(placeholder, value)

		if (position := result.find("%")) != -1:
			following = result[position + 1] if position + 1 < len(result) else ""
			if following != "%":
				raise ValueError(f"Unknown format specifier '%{following}' in '{formatSpec}'.")

		return result.replace("%%", "%")

	def __str__(self) -> str:
		"""
		Returns the stopwatch's state and its measured time span.

		The duration is rendered in seconds with :attr:`Digits` fractional digits, in every state - a running and a
		stopped stopwatch report the same unit at the same resolution.

		:returns: The string equivalent of the stopwatch.
		"""
		name = f" {self._name}" if self._name is not None else ""
		duration = f"{self._durationInNanoseconds() / 1e9:.{self._digits}f}"

		if self.IsStopped:
			return f"Stopwatch{name} (stopped): {self._beginTime} -> {self._endTime}: {duration}"
		elif self.IsRunning:
			return f"Stopwatch{name} (running): {self._beginTime} -> now: {duration}"
		elif self.IsPaused:
			return f"Stopwatch{name} (paused): {self._beginTime} -> now: {duration}"
		else:
			return f"Stopwatch{name}: not started"
