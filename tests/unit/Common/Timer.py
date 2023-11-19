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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from time import sleep
from unittest import TestCase

from pyTooling.Common import CurrentPlatform
from pyTooling.Timer import Timer


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Timing(TestCase):
	def test_StartStop(self) -> None:
		delay = 0.1
		inaccuracy = 3.0 if CurrentPlatform.IsNativeMacOS else 0.5

		timer = Timer()

		timer.Start()
		sleep(delay)  # 100 ms
		diff = timer.Stop()

		print(f"Duration for 'sleep({delay:0.3f})': {diff:0.6f} us")
		self.assertLessEqual(diff, delay + (delay * inaccuracy))

	def test_PauseResume(self) -> None:
		delay = 0.1
		inaccuracy = 4.0 if CurrentPlatform.IsNativeMacOS else 0.5

		timer = Timer()

		timer.Start()
		sleep(delay)  # 100 ms
		diff = timer.Pause()
		print(f"Duration for '1st sleep({delay:0.3f})': {diff:0.6f} us")
		self.assertLessEqual(diff, delay + (delay * inaccuracy))

		sleep(delay * 5)  # 500 ms

		timer.Continue()
		sleep(delay)  # 100 ms
		diff = timer.Pause()
		print(f"Duration for '2nd sleep({delay:0.3f})': {diff:0.6f} us")
		self.assertLessEqual(diff, delay + (delay * inaccuracy))

		total = timer.Stop()
		print(f"Duration for '2x sleep({delay:0.3f}) + 1x pause({delay * 5:0.3f})': {total:0.6f} us")
		self.assertLessEqual(total, (7 * delay) + (delay * inaccuracy))

	def test_ContextManager(self) -> None:
		delay = 0.1
		inaccuracy = 3.0 if CurrentPlatform.IsNativeMacOS else 0.5

		with Timer() as timer:
			sleep(delay)  # 100 ms

		print(f"Duration for '2nd sleep({delay:0.3f})': {timer.Duration:0.6f} us")
		self.assertLessEqual(timer.Duration, delay + (delay * inaccuracy))
