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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from time import perf_counter_ns
from typing import List, Optional as Nullable, Dict

from pyTooling.Decorators import export
from pyTooling.MetaClasses import ObjectWithSlots


@export
class Timer(ObjectWithSlots):
	"""
	Undocumented.

	.. todo::

	   Class:Timer Needs class documentation.
	"""

	_timers: Dict[str, 'Timer'] = {}

	_startTime: Nullable[int]
	_resumeTime: Nullable[int]
	_pauseTime: int
	_stopTime: int
	_diffTime: int
	_diffTimes: List[int]

	def __init__(self):
		self._startTime = None
		self._resumeTime = None
		self._diffTimes = []

	def __enter__(self):
		self.Start()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.Stop()

	def Start(self):
		self._startTime = perf_counter_ns()
		self._resumeTime = self._startTime

	def Stop(self):
		if self._startTime is None:
			raise Exception(f"Timer was never started.")

		self._stopTime = perf_counter_ns()
		self._diffTime = self._stopTime - self._startTime

		return self._diffTime / 1e9

	def Pause(self):
		self._pauseTime = perf_counter_ns()

		if self._resumeTime is None:
			raise Exception(f"Timer was not (re-)started.")

		diff = self._pauseTime - self._resumeTime
		self._diffTimes.append(diff)
		self._resumeTime = None

		return diff / 1e9

	def Continue(self):
		self._resumeTime = perf_counter_ns()

	@property
	def Duration(self) -> float:
		return self._diffTime / 1e9

	@property
	def DurationMS(self) -> float:
		return self._diffTime / 1e6

	@property
	def DurationUS(self) -> float:
		return self._diffTime / 1e3
