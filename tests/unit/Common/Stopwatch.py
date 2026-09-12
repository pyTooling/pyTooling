# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __ ___  _ __ ___   ___  _ __                               #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ ` _ \| '_ ` _ \ / _ \| '_ \                              #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | | | | | | | | | (_) | | | |                             #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_| |_|_| |_| |_|\___/|_| |_|                             #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for :class:`pyTooling.Stopwatch.Stopwatch`: starting, pausing, resuming, splitting and stopping,
the formatting of the results, and its use as a context manager.
"""
from time                 import sleep

from pyTooling.Exceptions import ToolingException

from pyTooling.Platform   import CurrentPlatform
from pyTooling.Stopwatch  import Stopwatch, StopwatchError
from pyTooling.Testing    import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Operations(Testcase):
	DELAY = 0.5
	PAUSE = 0.9
	INACCURACY = 2.7 if CurrentPlatform.IsNativeMacOS else 1.25

	def test_StartStart(self) -> None:
		sw = Stopwatch()
		sw.Start()
		with self.assertRaises(ToolingException):
			sw.Start()

	def test_Split(self) -> None:
		sw = Stopwatch()
		with self.assertRaises(ToolingException):
			sw.Split()

	def test_Pause(self) -> None:
		sw = Stopwatch()
		with self.assertRaises(ToolingException):
			sw.Pause()

	def test_Resume(self) -> None:
		sw = Stopwatch()
		with self.assertRaises(ToolingException):
			sw.Resume()

	def test_Stop(self) -> None:
		sw = Stopwatch()
		with self.assertRaises(ToolingException):
			sw.Stop()

	def test_StartStop(self) -> None:
		print()

		sw = Stopwatch()

		sw.Start()
		sleep(self.DELAY)  # 500 ms
		diff = sw.Stop()

		print(f"Duration for 'sleep({self.DELAY:0.3f})': {diff:0.6f} us")
		self.assertLessEqual(diff, self.DELAY * self.INACCURACY)

		self.assertFalse(sw.HasSplitTimes)
		self.assertFalse(sw.IsStarted)
		self.assertFalse(sw.IsPaused)
		self.assertFalse(sw.IsRunning)
		self.assertTrue(sw.IsStopped)
		self.assertEqual(0, sw.SplitCount)
		self.assertEqual(0, sw.ActiveCount)
		self.assertEqual(0, sw.InactiveCount)
		self.assertEqual(0, len(sw))

	def test_StartPauseStop(self) -> None:
		print()

		sw = Stopwatch()

		sw.Start()
		sleep(self.DELAY)  # 500 ms
		diff1 = sw.Pause()
		sleep(self.PAUSE)  # 200 ms
		diff2 = sw.Stop()
		total = sw.Duration

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {diff1:0.6f} us")
		self.assertLessEqual(diff1, self.DELAY * self.INACCURACY)

		print(f"Duration for '1st pause({self.PAUSE:0.3f})': {diff2:0.6f} us")
		self.assertLessEqual(diff2, self.PAUSE * self.INACCURACY)

		print(f"Duration for '1x sleep({self.DELAY:0.3f}) + 1x pause({self.PAUSE:0.3f})': {total:0.6f} us")
		self.assertLessEqual(total, (1 * self.DELAY + 1 * self.PAUSE) * self.INACCURACY)

		self.assertTrue(sw.HasSplitTimes)
		self.assertEqual(2, sw.SplitCount)
		self.assertEqual(1, sw.ActiveCount)
		self.assertEqual(1, sw.InactiveCount)
		self.assertEqual(2, len(sw))

	def test_StartPauseResumeStop(self) -> None:
		print()

		sw = Stopwatch()

		sw.Start()
		sleep(self.DELAY)  # 500 ms
		diff1 = sw.Pause()
		sleep(self.PAUSE)  # 200 ms
		diff2 = sw.Resume()
		sleep(self.DELAY)  # 500 ms
		diff3 = sw.Stop()
		total = sw.Duration

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {diff1:0.6f} us")
		self.assertLessEqual(diff1, self.DELAY * self.INACCURACY)

		print(f"Duration for '1st pause({self.PAUSE:0.3f})': {diff2:0.6f} us")
		self.assertLessEqual(diff2, self.PAUSE * self.INACCURACY)

		print(f"Duration for '2nd sleep({self.DELAY:0.3f})': {diff3:0.6f} us")
		self.assertLessEqual(diff3, self.DELAY * self.INACCURACY)

		print(f"Duration for '2x sleep({self.DELAY:0.3f}) + 1x pause({self.PAUSE:0.3f})': {total:0.6f} us")
		self.assertLessEqual(total, (2 * self.DELAY + 1 * self.PAUSE) * self.INACCURACY)

		seq = ((diff1, True), (diff2, False), (diff3, True))

		self.assertTrue(sw.HasSplitTimes)
		self.assertEqual(3, sw.SplitCount)
		self.assertEqual(2, sw.ActiveCount)
		self.assertEqual(1, sw.InactiveCount)
		self.assertEqual(3, len(sw))
		self.assertTupleEqual(seq[0], sw[0])
		self.assertTupleEqual(seq[1], sw[1])
		self.assertTupleEqual(seq[2], sw[2])
		self.assertTupleEqual(seq, tuple(t for t in sw))


class Formatting(Testcase):
	def test_NoName(self) -> None:
		print()
		sw = Stopwatch()

		result = str(sw)

		print(result)
		self.assertEqual("Stopwatch: not started", result)

	def test_WithName(self) -> None:
		print()
		sw = Stopwatch("foo")

		result = str(sw)

		print(result)
		self.assertEqual("Stopwatch foo: not started", result)

	def test_WithName_Running(self) -> None:
		print()
		sw = Stopwatch("foo")
		sw.Start()

		result = str(sw)

		sw.Stop()

		print(result)
		self.assertRegex(result, r"Stopwatch foo \(running\): ")

	def test_WithName_Paused(self) -> None:
		print()
		sw = Stopwatch("foo")
		sw.Start()
		sw.Pause()

		result = str(sw)

		sw.Stop()

		print(result)
		self.assertRegex(result, r"Stopwatch foo \(paused\): ")

	def test_WithName_Resumed(self) -> None:
		print()
		sw = Stopwatch("foo")
		sw.Start()
		sw.Pause()
		sw.Resume()

		result = str(sw)

		sw.Stop()

		print(result)
		self.assertRegex(result, r"Stopwatch foo \(running\): ")

	def test_WithName_Stopped(self) -> None:
		print()
		sw = Stopwatch("foo")
		sw.Start()
		sw.Stop()

		result = str(sw)

		print(result)
		self.assertRegex(result, r"Stopwatch foo \(stopped\): ")


class ContextManagerProtocol(Testcase):
	DELAY = 0.5
	PAUSE = 0.9
	INACCURACY = 2.7 if CurrentPlatform.IsNativeMacOS else 1.25

	def test_OneLiner(self) -> None:
		print()

		with Stopwatch() as sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertLessEqual(sw.Duration, self.DELAY * self.INACCURACY)

	def test_PreCreated(self) -> None:
		print()

		sw = Stopwatch()

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertLessEqual(sw.Duration, self.DELAY * self.INACCURACY)

	def test_ReuseContext_StartStop(self) -> None:
		print()

		sw = Stopwatch()

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertEqual(1, sw.ActiveCount)
		self.assertLessEqual(sw.Activity, self.DELAY * self.INACCURACY)
		self.assertLessEqual(sw.Duration, self.DELAY * self.INACCURACY)

		with self.assertRaises(StopwatchError):
			with sw:
				sleep(self.DELAY)  # 500 ms

	def test_ReuseContext_ResumePause(self) -> None:
		print()

		sw = Stopwatch(preferPause=True)

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertEqual(1, sw.ActiveCount)
		# the stopwatch is paused, so it is inside an inactive span that would be recorded if it stopped now
		self.assertEqual(1, sw.InactiveCount)
		self.assertLessEqual(sw.Activity, self.DELAY * self.INACCURACY)
		self.assertLessEqual(sw.Duration, self.DELAY * self.INACCURACY)

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '2st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertEqual(3, len(sw))
		self.assertEqual(2, sw.ActiveCount)
		self.assertEqual(2, sw.InactiveCount)
		self.assertLessEqual(sw.Activity, 2 * self.DELAY * self.INACCURACY)

	def test_ReuseContext_Loop(self) -> None:
		print()

		sw = Stopwatch(preferPause=True)
		for i in range(5):
			with sw:
				sleep(self.DELAY / 5)  # 100 ms

			sleep(self.PAUSE / 2)  # 450 ms
		sw.Stop()

		print(f"Start/Stop/Diff: {sw.StartTime}/{sw.StopTime}/{sw.StopTime - sw.StartTime}/{sw.Duration}")
		print(f"Activity/Inactivity: {sw.Activity}/{sw.Inactivity}")
		print("Iterator: __iter__")
		for duration, activity in sw:
			print(f"  {duration} {'running' if activity else 'paused'}")

		self.assertEqual(5, sw.ActiveCount)
		self.assertEqual(5, sw.InactiveCount)

	def test_Splits(self) -> None:
		print()

		with Stopwatch() as sw:
			sleep(self.DELAY)  # 500 ms
			sw.Split()
			sleep(self.DELAY)  # 500 ms
			sw.Split()
			sleep(self.DELAY)  # 500 ms

		print(f"Start/Stop/Diff: {sw.StartTime}/{sw.StopTime}/{sw.StopTime - sw.StartTime}/{sw.Duration}")
		print(f"Activity/Inactivity: {sw.Activity}/{sw.Inactivity}")
		print("Iterator: __iter__")
		for duration, activity in sw:
			print(f"  {duration} {'running' if activity else 'paused'}")

		self.assertAlmostEqual(sw.Duration, sw.Activity)
		self.assertEqual(0, sw.Inactivity)
		self.assertEqual(0, sw.InactiveCount)


class Excluding(Testcase):
	"""Excluding time spans from the measurement with :attr:`~pyTooling.Stopwatch.Stopwatch.Exclude`."""

	DELAY = 0.5
	INACCURACY = 2.7 if CurrentPlatform.IsNativeMacOS else 1.25

	def test_ExcludedSpanCountsAsInactivity(self) -> None:
		sw = Stopwatch(started=True)
		sleep(self.DELAY)
		with sw.Exclude:
			sleep(self.DELAY)
		sleep(self.DELAY)
		sw.Stop()

		self.assertEqual(3, sw.SplitCount)
		self.assertEqual(2, sw.ActiveCount)
		self.assertEqual(1, sw.InactiveCount)

		# a sleep lasts at least as long as asked, and on a loaded runner considerably longer
		self.assertGreaterEqual(sw.Activity, 2 * self.DELAY)
		self.assertLessEqual(sw.Activity, 2 * self.DELAY * self.INACCURACY)
		self.assertGreaterEqual(sw.Inactivity, self.DELAY)
		self.assertLessEqual(sw.Inactivity, self.DELAY * self.INACCURACY)

	def test_ExcludeIsReusable(self) -> None:
		"""
		The exclude context manager is cached, and using it a second time has to work.

		It used to return an unbound local on every access after the first, so a stopwatch could exclude exactly one
		span and the loop below raised :exc:`UnboundLocalError` on its second iteration.
		"""
		sw = Stopwatch(started=True)
		for _ in range(3):
			with sw.Exclude:
				sleep(0.01)

		sw.Stop()

		self.assertEqual(3, sw.InactiveCount)

	def test_ExcludeReturnsTheSameContextManager(self) -> None:
		sw = Stopwatch(started=True)

		self.assertIs(sw.Exclude, sw.Exclude)

		sw.Stop()

	def test_ExcludeNeedsARunningStopwatch(self) -> None:
		sw = Stopwatch()

		with self.assertRaises(StopwatchError):
			with sw.Exclude:
				pass


class Counting(Testcase):
	"""Counting split times, including the span that hasn't been recorded yet."""

	DELAY = 0.1

	def test_NeverStarted(self) -> None:
		sw = Stopwatch()

		self.assertEqual(0, sw.SplitCount)
		self.assertEqual(0, sw.ActiveCount)
		self.assertEqual(0, sw.InactiveCount)
		self.assertFalse(sw.HasSplitTimes)

	def test_RunningCountsTheSpanInProgress(self) -> None:
		"""A running stopwatch is inside an active span, so it is counted as if the stopwatch stopped now."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)

		self.assertEqual(0, sw.SplitCount)
		self.assertEqual(1, sw.ActiveCount)
		self.assertEqual(0, sw.InactiveCount)

		sw.Stop()

	def test_PausedCountsTheSpanInProgress(self) -> None:
		"""A paused stopwatch is inside an inactive span, so it is counted as if the stopwatch stopped now."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)
		sw.Pause()

		self.assertEqual(1, sw.SplitCount)
		self.assertEqual(1, sw.ActiveCount)
		self.assertEqual(1, sw.InactiveCount)

		sw.Stop()

	def test_StoppedCountsOnlyRecordedSpans(self) -> None:
		"""A stopped stopwatch has no span in progress, so nothing is added."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)
		sw.Split()
		sleep(self.DELAY)
		sw.Stop()

		self.assertEqual(2, sw.SplitCount)
		self.assertEqual(2, sw.ActiveCount)
		self.assertEqual(0, sw.InactiveCount)

	def test_CountsMatchTheDurations(self) -> None:
		"""The counts and the durations describe the same spans, so they agree while the stopwatch runs."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)

		self.assertEqual(1, sw.ActiveCount)
		self.assertGreater(sw.Activity, 0.0)
		self.assertEqual(0, sw.InactiveCount)
		self.assertEqual(0.0, sw.Inactivity)

		sw.Pause()
		sleep(self.DELAY)

		self.assertEqual(1, sw.InactiveCount)
		self.assertGreater(sw.Inactivity, 0.0)

		sw.Stop()

	def test_HasSplitTimes(self) -> None:
		"""One split time is enough for :attr:`HasSplitTimes`."""
		sw = Stopwatch(started=True)

		self.assertFalse(sw.HasSplitTimes)

		sw.Split()

		self.assertEqual(1, sw.SplitCount)
		self.assertTrue(sw.HasSplitTimes)

		sw.Stop()

	def test_HasSplitTimes_StartStopRecordsNone(self) -> None:
		"""A stopwatch that was only started and stopped records no split time at all."""
		sw = Stopwatch(started=True)
		sw.Stop()

		self.assertEqual(0, sw.SplitCount)
		self.assertFalse(sw.HasSplitTimes)


class Durations(Testcase):
	"""The duration in seconds and in whole nanoseconds."""

	DELAY = 0.25

	def test_NeverStarted(self) -> None:
		sw = Stopwatch()

		self.assertEqual(0, sw.DurationInNanoseconds)
		self.assertEqual(0.0, sw.Duration)

	def test_Running(self) -> None:
		sw = Stopwatch(started=True)
		sleep(self.DELAY)

		self.assertGreater(sw.DurationInNanoseconds, 0)
		self.assertIsInstance(sw.DurationInNanoseconds, int)

		sw.Stop()

	def test_StoppedIsFinal(self) -> None:
		"""Once stopped, the duration doesn't move any more."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)
		sw.Stop()

		first = sw.DurationInNanoseconds
		sleep(0.05)

		self.assertEqual(first, sw.DurationInNanoseconds)

	def test_SecondsAreTheNanosecondsScaled(self) -> None:
		"""``Duration`` is the same measurement, so the two can't disagree."""
		sw = Stopwatch(started=True)
		sleep(self.DELAY)
		sw.Stop()

		self.assertEqual(sw.DurationInNanoseconds / 1e9, sw.Duration)
		self.assertEqual(sw.DurationInNanoseconds, round(sw.Duration * 1e9))


class Digits(Testcase):
	"""The number of fractional digits :meth:`__str__` renders the duration with."""

	DELAY = 0.05

	def test_Default(self) -> None:
		self.assertEqual(3, Stopwatch().Digits)

	def test_GivenAtCreationTime(self) -> None:
		self.assertEqual(6, Stopwatch(digits=6).Digits)

	def test_Changeable(self) -> None:
		sw = Stopwatch()
		sw.Digits = 9

		self.assertEqual(9, sw.Digits)

	def test_WrongType(self) -> None:
		with self.assertRaises(TypeError):
			Stopwatch(digits=3.5)

	def test_OutOfRange(self) -> None:
		for digits in (-1, 10):
			with self.assertRaises(ValueError):
				Stopwatch(digits=digits)

	def test_WrongType_Assigned(self) -> None:
		sw = Stopwatch()

		with self.assertRaises(TypeError):
			sw.Digits = 3.5

		self.assertEqual(3, sw.Digits)

	def test_OutOfRange_Assigned(self) -> None:
		sw = Stopwatch()

		for digits in (-1, 10):
			with self.assertRaises(ValueError):
				sw.Digits = digits

		self.assertEqual(3, sw.Digits)

	def test_SameResolutionWhileRunningAndWhenStopped(self) -> None:
		"""A running and a stopped stopwatch report the duration in the same unit at the same resolution."""
		sw = Stopwatch("measure", started=True)
		sleep(self.DELAY)
		running = str(sw)
		sw.Stop()
		stopped = str(sw)

		self.assertIn("(running)", running)
		self.assertIn("(stopped)", stopped)

		# both end in a duration in seconds with three fractional digits; how many seconds is not the point, and a
		# loaded runner sleeps longer than it was asked to
		self.assertRegex(running, r": \d+\.\d{3}$")
		self.assertRegex(stopped, r": \d+\.\d{3}$")

	def test_DigitsAreUsed(self) -> None:
		sw = Stopwatch("measure", started=True)
		sleep(self.DELAY)
		sw.Stop()

		sw.Digits = 6
		self.assertRegex(str(sw), r": \d+\.\d{6}$")

		sw.Digits = 0
		self.assertRegex(str(sw), r": \d+$")


class DurationFormatting(Testcase):
	"""The ``%``-placeholders of :meth:`__format__`."""

	@staticmethod
	def _stopwatch(nanoseconds: int) -> Stopwatch:
		sw = Stopwatch("formatted", started=True)
		sw.Stop()
		sw._totalTime = nanoseconds

		return sw

	def test_Fields(self) -> None:
		# 26 hours, 3 minutes, 4.123456789 seconds
		sw = self._stopwatch(93_784_123_456_789)

		self.assertEqual("26:03:04", f"{sw:%H:%M:%S}")
		self.assertEqual("03:04", f"{sw:%M:%S}")

	def test_HoursAreNotCapped(self) -> None:
		"""``%H`` must not wrap, or ``%H:%M:%S`` would silently drop a day."""
		sw = self._stopwatch(93_784_123_456_789)

		self.assertEqual("26", f"{sw:%H}")

	def test_FieldsArePadded(self) -> None:
		sw = self._stopwatch(3_601_002_003_004)  # 1 h, 0 min, 1 s, 2 ms, 3 us, 4 ns

		self.assertEqual("01:00:01.002", f"{sw:%H:%M:%S.%L}")
		self.assertEqual("01:00:01.002003004", f"{sw:%H:%M:%S.%N}")

	def test_FractionsAreTruncationsOfEachOther(self) -> None:
		"""``%L``, ``%U`` and ``%N`` render the same fraction at three precisions, so they don't have to be combined."""
		sw = self._stopwatch(93_784_123_456_789)

		self.assertEqual("123", f"{sw:%L}")
		self.assertEqual("123456", f"{sw:%U}")
		self.assertEqual("123456789", f"{sw:%N}")

	def test_Totals(self) -> None:
		sw = self._stopwatch(93_784_123_456_789)

		self.assertEqual("93784", f"{sw:%s}")
		self.assertEqual("93784123", f"{sw:%m}")
		self.assertEqual("93784123456", f"{sw:%u}")
		self.assertEqual("93784123456789", f"{sw:%n}")

	def test_ShortMeasurement(self) -> None:
		sw = self._stopwatch(1_500_000_000)

		self.assertEqual("00:00:01.500", f"{sw:%H:%M:%S.%L}")
		self.assertEqual("1500", f"{sw:%m}")

	def test_EmptySpecification(self) -> None:
		sw = self._stopwatch(1_000_000_000)

		self.assertEqual(str(sw), f"{sw}")

	def test_EscapedPercent(self) -> None:
		sw = self._stopwatch(1_000_000_000)

		self.assertEqual("100% of 1 s", f"{sw:100%% of %s s}")

	def test_UnknownSpecifier(self) -> None:
		sw = self._stopwatch(1_000_000_000)

		# a stopwatch measures code execution, so totals for days, hours and minutes were dropped
		for specification in ("%Q", "%d", "%h", "%D", "%l"):
			with self.assertRaises(ValueError):
				format(sw, specification)

	def test_TrailingPercent(self) -> None:
		"""A specification ending in a lone ``%`` has no character to check, and must not index past the end."""
		sw = self._stopwatch(1_000_000_000)

		with self.assertRaises(ValueError):
			format(sw, "%s%")

	def test_NeverStarted(self) -> None:
		sw = Stopwatch()

		self.assertEqual("00:00:00.000", f"{sw:%H:%M:%S.%L}")
		self.assertEqual("0", f"{sw:%n}")
