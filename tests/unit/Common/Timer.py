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
"""Unit tests for TBD."""
from time               import sleep
from unittest           import TestCase

from pyTooling.Exceptions import ToolingException

from pyTooling.Platform import CurrentPlatform
from pyTooling.Timer    import Timer


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Timing(TestCase):
	DELAY = 0.5
	PAUSE = 0.9
	INACCURACY = 2.7 if CurrentPlatform.IsNativeMacOS else 1.25

	def test_StartStart(self) -> None:
		timer = Timer()
		timer.Start()
		with self.assertRaises(ToolingException):
			timer.Start()

	def test_Split(self) -> None:
		timer = Timer()
		with self.assertRaises(ToolingException):
			timer.Split()

	def test_Pause(self) -> None:
		timer = Timer()
		with self.assertRaises(ToolingException):
			timer.Pause()

	def test_Resume(self) -> None:
		timer = Timer()
		with self.assertRaises(ToolingException):
			timer.Resume()

	def test_Stop(self) -> None:
		timer = Timer()
		with self.assertRaises(ToolingException):
			timer.Stop()

	def test_StartStop(self) -> None:
		print()

		timer = Timer()

		timer.Start()
		sleep(self.DELAY)  # 100 ms
		diff = timer.Stop()

		print(f"Duration for 'sleep({self.DELAY:0.3f})': {diff:0.6f} us")
		self.assertLessEqual(diff, self.DELAY * self.INACCURACY)

		self.assertFalse(timer.HasSplitTimes)
		self.assertEqual(0, timer.SplitCount)
		self.assertEqual(1, timer.ActiveCount)
		self.assertEqual(0, timer.InactiveCount)
		self.assertEqual(0, len(timer))

	def test_StartPauseStop(self) -> None:
		print()

		timer = Timer()

		timer.Start()
		sleep(self.DELAY)  # 100 ms
		diff1 = timer.Pause()
		sleep(self.PAUSE)  # 200 ms
		diff2 = timer.Stop()
		total = timer.Duration

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {diff1:0.6f} us")
		self.assertLessEqual(diff1, self.DELAY * self.INACCURACY)

		print(f"Duration for '1st pause({self.PAUSE * 5:0.3f})': {diff2:0.6f} us")
		self.assertLessEqual(diff2, self.PAUSE * self.INACCURACY)

		print(f"Duration for '1x sleep({self.DELAY:0.3f}) + 1x pause({self.PAUSE:0.3f})': {total:0.6f} us")
		self.assertLessEqual(total, (1 * self.DELAY + 1 * self.PAUSE) * self.INACCURACY)

		self.assertTrue(timer.HasSplitTimes)
		self.assertEqual(1, timer.SplitCount)
		self.assertEqual(1, timer.ActiveCount)
		self.assertEqual(1, timer.InactiveCount)
		self.assertEqual(1, len(timer))

	def test_StartPauseResumeStop(self) -> None:
		print()

		timer = Timer()

		timer.Start()
		sleep(self.DELAY)  # 100 ms
		diff1 = timer.Pause()
		sleep(self.PAUSE)  # 200 ms
		diff2 = timer.Resume()
		sleep(self.DELAY)  # 100 ms
		diff3 = timer.Stop()
		total = timer.Duration

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {diff1:0.6f} us")
		self.assertLessEqual(diff1, self.DELAY * self.INACCURACY)

		print(f"Duration for '1st pause({self.PAUSE:0.3f})': {diff2:0.6f} us")
		self.assertLessEqual(diff2, self.PAUSE * self.INACCURACY)

		print(f"Duration for '2nd sleep({self.DELAY:0.3f})': {diff3:0.6f} us")
		self.assertLessEqual(diff3, self.DELAY * self.INACCURACY)

		print(f"Duration for '2x sleep({self.DELAY:0.3f}) + 1x pause({self.PAUSE:0.3f})': {total:0.6f} us")
		self.assertLessEqual(total, (2 * self.DELAY + 1 * self.PAUSE) * self.INACCURACY)

		seq = ((diff1, True), (diff2, False), (diff3, True))

		self.assertTrue(timer.HasSplitTimes)
		self.assertEqual(2, timer.SplitCount)
		self.assertEqual(2, timer.ActiveCount)
		self.assertEqual(1, timer.InactiveCount)
		self.assertEqual(2, len(timer))
		self.assertTupleEqual(seq[0], timer[0])
		self.assertTupleEqual(seq[1], timer[1])
		self.assertTupleEqual(seq[2], timer[2])
		self.assertTupleEqual(seq, tuple(t for t in timer))

	def test_ContextManager(self) -> None:
		print()

		with Timer() as timer:
			sleep(self.DELAY)  # 100 ms

		print(f"Duration for '1st sleep({self.DELAY:0.3f})': {timer.Duration:0.6f} us")
		self.assertLessEqual(timer.Duration, self.DELAY * self.INACCURACY)
