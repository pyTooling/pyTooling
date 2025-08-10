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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. hint:: See :ref:`high-level help <COMMON/Stopwatch>` for explanations and usage examples.
"""

from datetime import datetime
from inspect  import Traceback
from time     import perf_counter_ns
from types    import TracebackType
from typing   import List, Optional as Nullable, Iterator, Tuple, Type

# Python 3.11: use Self if returning the own object: , Self

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import SlottedObject
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Platform    import CurrentPlatform
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Stopwatch] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import SlottedObject
		from Exceptions          import ToolingException
		from Platform            import CurrentPlatform
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Stopwatch] Could not import directly!")
		raise ex


@export
class StopwatchException(ToolingException):
	"""This exception is caused by wrong usage of the stopwatch."""


@export
class ExcludeContextManager:
	"""
	A stopwatch context manager for excluding certain time spans from measurement.

	While a normal stopwatch's embedded context manager (re)starts the stopwatch on every *enter* event and pauses the
	stopwatch on every *exit* event, this context manager pauses on *enter* events and restarts on every *exit* event.
	"""
	_stopwatch: "Stopwatch"  #: Reference to the stopwatch.

	def __init__(self, stopwatch: "Stopwatch") -> None:
		"""
		Initializes an excluding context manager.

		:param stopwatch: Reference to the stopwatch.
		"""
		self._stopwatch = stopwatch

	def __enter__(self) -> "ExcludeContextManager":  # TODO: Python 3.11: -> Self:
		"""
		Enter the context and pause the stopwatch.

		:returns: Excluding stopwatch context manager instance.
		"""
		self._stopwatch.Pause()

		return self

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
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

	_name:         Nullable[str]
	_preferPause:  bool

	_beginTime:    Nullable[datetime]
	_endTime:      Nullable[datetime]
	_startTime:    Nullable[int]
	_resumeTime:   Nullable[int]
	_pauseTime:    Nullable[int]
	_stopTime:     Nullable[int]
	_totalTime:    Nullable[int]
	_splits:       List[Tuple[float, bool]]

	_excludeContextManager: ExcludeContextManager

	def __init__(self, name: str = None, started: bool = False, preferPause: bool = False) -> None:
		"""
		Initializes the fields of the stopwatch.

		If parameter ``started`` is set to true, the stopwatch will immediately start.

		:param name:        Optional name of the stopwatch.
		:param preferPause: Optional setting, if __exit__(...) in a contex should prefer pause or stop behavior.
		:param started:     Optional flag, if the stopwatch should be started immediately.
		"""
		self._name =         name
		self._preferPause =  preferPause

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

		:raises StopwatchException: If stopwatch was already started.
		:raises StopwatchException: If stopwatch was already started and stopped.
		"""
		if self._startTime is not None:
			raise StopwatchException("Stopwatch was already started.")
		if self._stopTime is not None:
			raise StopwatchException("Stopwatch was already used (started and stopped).")

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

		:returns:                   Duration in seconds since last stopwatch operation
		:raises StopwatchException: If stopwatch was not started or resumed.
		"""
		pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchException("Stopwatch was not started or resumed.")

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

		:returns:                   Duration in seconds since last stopwatch operation
		:raises StopwatchException: If stopwatch was not started or resumed.
		"""
		self._pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise StopwatchException("Stopwatch was not started or resumed.")

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

		:returns:                   Duration in seconds since last pause operation
		:raises StopwatchException: If stopwatch was not paused.
		"""
		self._resumeTime = perf_counter_ns()

		if self._pauseTime is None:
			raise StopwatchException("Stopwatch was not paused.")

		diff = (self._resumeTime - self._pauseTime) / 1e9
		self._splits.append((diff, False))
		self._pauseTime = None

		return diff

	def Stop(self):
		"""
		Stop the stopwatch and return the time delta to the previous stopwatch operation.

		The stopwatch needs to be started to stop it. See property :data:`IsStarted` to check if the stopwatch was started
		and the stop operation is possible. |br|
		Depending on the previous operation, the time delta will be:

		* the duration from start operation to the stop operation.
		* the duration from last resume to the stop operation.

		:returns:                   Duration in seconds since last stopwatch operation
		:raises StopwatchException: If stopwatch was not started.
		:raises StopwatchException: If stopwatch was already stopped.
		"""
		self._stopTime = perf_counter_ns()
		self._endTime =  datetime.now()

		if self._startTime is None:
			raise StopwatchException("Stopwatch was never started.")
		if self._totalTime is not None:
			raise StopwatchException("Stopwatch was already stopped.")

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

		beginEndDiff = self._endTime - self._beginTime

		return diff

	@readonly
	def Name(self) -> Nullable[str]:
		"""
		Read-only property returning the name of the stopwatch.

		:return: Name of the stopwatch.
		"""
		return self._name

	@readonly
	def IsStarted(self) -> bool:
		"""
		Read-only property returning the IsStarted state of the stopwatch.

		:return: True, if stopwatch was started.
		"""
		return self._startTime is not None and self._stopTime is None

	@readonly
	def IsRunning(self) -> bool:
		"""
		Read-only property returning the IsRunning state of the stopwatch.

		:return: True, if stopwatch was started and is currently not paused.
		"""
		return self._startTime is not None and self._resumeTime is not None

	@readonly
	def IsPaused(self) -> bool:
		"""
		Read-only property returning the IsPaused state of the stopwatch.

		:return: True, if stopwatch was started and is currently paused.
		"""
		return self._startTime is not None and self._pauseTime is not None

	@readonly
	def IsStopped(self) -> bool:
		"""
		Read-only property returning the IsStopped state of the stopwatch.

		:return: True, if stopwatch was stopped.
		"""
		return self._stopTime is not None

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was started.

		:return: The time when the stopwatch was started, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the stopwatch was stopped.

		:return: The time when the stopwatch was stopped, otherwise None.
		"""
		return self._endTime

	@readonly
	def HasSplitTimes(self) -> bool:
		"""
		Read-only property checking if split times have been taken.

		:return: True, if split times have been taken.
		"""
		return len(self._splits) > 1

	@readonly
	def SplitCount(self) -> int:
		"""
		Read-only property returning the number of split times.

		:return: Number of split times.
		"""
		return len(self._splits)

	@readonly
	def ActiveCount(self) -> int:
		"""
		Read-only property returning the number of active split times.

		:return: Number of active split times.

		.. warning::

		   This won't include all activities, unless the stopwatch got stopped.
		"""
		if self._startTime is None:
			return 0

		return len(list(t for t, a in self._splits if a is True))

	@readonly
	def InactiveCount(self) -> int:
		"""
		Read-only property returning the number of active split times.

		:return: Number of active split times.

		.. warning::

		   This won't include all inactivities, unless the stopwatch got stopped.
		"""
		if self._startTime is None:
			return 0

		return len(list(t for t, a in self._splits if a is False))

	@readonly
	def Activity(self) -> float:
		"""
		Read-only property returning the duration of all active split times.

		If the stopwatch is currently running, the duration since start or last resume operation will be included.

		:return: Duration of all active split times in seconds. If the stopwatch was never started, the return value will
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

		:return: Duration of all inactive split times in seconds. If the stopwatch was never started, the return value will
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

		:return: Duration since stopwatch was started in seconds. If the stopwatch was never started, the return value will
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
			excludeContextManager = ExcludeContextManager(self)
			self._excludeContextManager = excludeContextManager

		return excludeContextManager

	def __enter__(self) -> "Stopwatch":  # TODO: Python 3.11: -> Self:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__enter__(...)`` method.

		An unstarted stopwatch will be started. A paused stopwatch will be resumed.

		:return: The stopwatch itself.
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
			raise StopwatchException("Stopwatch is currently running and can not be started/resumed again.")
		elif self._stopTime is not None:      # is stopped?
			raise StopwatchException(f"Stopwatch was already stopped.")
		else:
			raise StopwatchException(f"Internal error.")

		return self

	def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Traceback) -> bool:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__exit__(...)`` method.

		A running stopwatch will be paused or stopped depending on the configured ``preferPause`` behavior.

		:param exc_type: Exception type, otherwise None.
		:param exc_val:  Exception object, otherwise None.
		:param exc_tb:   Exception's traceback, otherwise None.
		:returns:        True, if exceptions should be suppressed.
		"""
		if self._startTime is None:           # never started?
			raise StopwatchException("Stopwatch was never started.")
		elif self._stopTime is not None:
			raise StopwatchException("Stopwatch was already stopped.")
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
			raise StopwatchException("Stopwatch was not resumed.")


	def __len__(self):
		"""
		Implementation of ``len(...)`` to return the number of split times.

		:return: Number of split times.
		"""
		return len(self._splits)

	def __getitem__(self, index: int) -> Tuple[float, bool]:
		"""
		Implementation of ``split = object[i]`` to return the i-th split time.

		:param index:     Index to access the i-th split time.
		:return:          i-th split time as a tuple of: |br|
		                  (1) delta time to the previous stopwatch operation and |br|
		                  (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		:raises KeyError: If index *i* doesn't exist.
		"""
		return self._splits[index]

	def __iter__(self) -> Iterator[Tuple[float, bool]]:
		"""
		Return an iterator of tuples to iterate all split times.

		If the stopwatch is not stopped yet, the last split won't be included.

		:return: Iterator of split time tuples of: |br|
		         (1) delta time to the previous stopwatch operation and |br|
		         (2) a boolean indicating if the split was an activity (true) or inactivity (false).
		"""
		return self._splits.__iter__()

	def __str__(self):
		"""
		Returns the stopwatch's state and its measured time span.

		:returns: The string equivalent of the stopwatch.
		"""
		name = f" {self._name}" if self._name is not None else ""
		if self.IsStopped:
			return f"Stopwatch{name} (stopped): {self._beginTime} -> {self._endTime}: {self._totalTime}"
		elif self.IsRunning:
			return f"Stopwatch{name} (running): {self._beginTime} -> now: {self.Duration}"
		elif self.IsPaused:
			return f"Stopwatch{name} (paused): {self._beginTime} -> now: {self.Duration}"
		else:
			return f"Stopwatch{name}: not started"
