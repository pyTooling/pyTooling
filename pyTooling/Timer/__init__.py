# ==================================================================================================================== #
#              _____           _ _             _____ _                                                                 #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _(_)_ __ ___   ___ _ __                                             #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | '_ ` _ \ / _ \ '__|                                            #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_| | | | | | | | |  __/ |                                               #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_| |_|_| |_| |_|\___|_|                                               #
#  |_|    |___/                          |___/                                                                         #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A timer and stopwatch to measure execution time.

.. hint:: See :ref:`high-level help <TIMER>` for explanations and usage examples.
"""
from datetime import datetime
from time     import perf_counter_ns
from typing   import List, Optional as Nullable, Iterator, Tuple

# Python 3.11: use Self if returning the own object: , Self

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import SlottedObject
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Platform    import CurrentPlatform
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Timer] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import SlottedObject
		from Exceptions          import ToolingException
		from Platform            import CurrentPlatform
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Timer] Could not import directly!")
		raise ex


@export
class Timer(SlottedObject):
	"""
	Undocumented.

	.. todo::TIMER::Timer Needs class documentation.
	"""

	_name:         Nullable[str]
	_beginTime:    Nullable[datetime]
	_endTime:      Nullable[datetime]
	_startTime:    Nullable[int]
	_resumeTime:   Nullable[int]
	_pauseTime:    Nullable[int]
	_stopTime:     Nullable[int]
	_totalTime:    Nullable[int]
	_splits:       List[Tuple[float, bool]]

	def __init__(self, name: str = None) -> None:
		self._name =         name
		self._beginTime =    None
		self._endTime =      None
		self._startTime =    None
		self._resumeTime =   None
		self._pauseTime =    None
		self._stopTime =     None
		self._totalTime =    None
		self._splits =       []

	def __enter__(self) -> "Timer":  # TODO: Python 3.11: -> Self:
		self.Start()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> None:
		self.Stop()

	def Start(self) -> None:
		if self._startTime is not None:
			raise ToolingException(f"Timer was already started.")

		self._beginTime = datetime.now()
		self._resumeTime = self._startTime = perf_counter_ns()

	def Split(self) -> float:
		pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise ToolingException(f"Timer was not started or resumed.")

		diff = (pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = pauseTime

		return diff

	def Pause(self) -> float:
		self._pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise ToolingException(f"Timer was not started or resumed.")

		diff = (self._pauseTime - self._resumeTime) / 1e9
		self._splits.append((diff, True))
		self._resumeTime = None

		return diff

	def Resume(self) -> float:
		self._resumeTime = perf_counter_ns()

		if self._pauseTime is None:
			raise ToolingException(f"Timer was not paused.")

		diff = (self._resumeTime - self._pauseTime) / 1e9
		self._splits.append((diff, False))
		self._pauseTime = None

		return diff

	def Stop(self):
		self._stopTime = perf_counter_ns()
		self._endTime = datetime.now()

		if self._startTime is None:
			raise ToolingException(f"Timer was never started.")
		if self._totalTime is not None:
			raise ToolingException(f"Timer was already stopped.")

		# Check is timer is currently paused
		if self._resumeTime is None:
			diff = (self._stopTime - self._pauseTime) / 1e9
			self._splits.append((diff, False))
		else:
			diff = (self._stopTime - self._resumeTime) / 1e9
			self._splits.append((diff, True))

		self._totalTime = self._stopTime - self._startTime

		beginEndDiff = self._endTime - self._beginTime

		INACCURACY = 0.09 if CurrentPlatform.IsNativeMacOS else 0.02
		assert abs(((sum(d for d, _ in self._splits)) / beginEndDiff.total_seconds()) - 1.0) < INACCURACY
		assert abs(((self._totalTime / 1e9) / beginEndDiff.total_seconds()) - 1.0) < INACCURACY

		return diff

	@readonly
	def Name(self) -> Nullable[str]:
		return self._name

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		return self._endTime

	@readonly
	def HasSplitTimes(self) -> bool:
		return len(self._splits) > 1

	@readonly
	def SplitCount(self) -> int:
		return len(self._splits) - 1

	@readonly
	def ActiveCount(self) -> int:
		return len(list(t for t, a in self._splits if a is True))

	@readonly
	def InactiveCount(self) -> int:
		return len(list(t for t, a in self._splits if a is False))

	@readonly
	def Activity(self) -> float:
		return sum(t for t, a in self._splits if a is True)

	@readonly
	def Inactivity(self) -> float:
		return sum(t for t, a in self._splits if a is False)

	@readonly
	def Duration(self) -> float:
		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e9

	@readonly
	def DurationMS(self) -> float:
		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e6

	@readonly
	def DurationUS(self) -> float:
		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e3

	def __len__(self):
		return len(self._splits) - 1

	def __getitem__(self, index: int) -> Tuple[float, bool]:
		return self._splits[index]

	def __iter__(self) -> Iterator[Tuple[float, bool]]:
		return self._splits.__iter__()
