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
"""Unit tests for TBD."""
from time                 import sleep
from unittest             import TestCase

from pyTooling.Exceptions import ToolingException

from pyTooling.Platform   import CurrentPlatform
from pyTooling.Stopwatch import Stopwatch, StopwatchException

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Operations(TestCase):
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


class Formatting(TestCase):
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


class ContextManagerProtocol(TestCase):
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

		with self.assertRaises(StopwatchException):
			with sw:
				sleep(self.DELAY)  # 500 ms

	def test_ReuseContext_ResumePause(self) -> None:
		print()

		sw = Stopwatch(preferPause=True)

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertEqual(1, sw.ActiveCount)
		self.assertEqual(0, sw.InactiveCount)
		self.assertLessEqual(sw.Activity, self.DELAY * self.INACCURACY)
		self.assertLessEqual(sw.Duration, self.DELAY * self.INACCURACY)

		with sw:
			sleep(self.DELAY)  # 500 ms

		print(f"Duration for '2st sleep({self.DELAY:0.3f})': {sw.Duration:0.6f} us")
		self.assertEqual(3, len(sw))
		self.assertEqual(2, sw.ActiveCount)
		self.assertEqual(1, sw.InactiveCount)
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
