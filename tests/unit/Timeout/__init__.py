# ==================================================================================================================== #
#             _____           _ _             _____ _                            _                                     #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _(_)_ __ ___   ___  ___  _   _| |_                                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | '_ ` _ \ / _ \/ _ \| | | | __|                                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| | | | | | | | |  __/ (_) | |_| | |_                                   #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_| |_|_| |_| |_|\___|\___/ \__,_|\__|                                  #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for :mod:`pyTooling.Timeout`: the current timeout of a thread, nesting, the time left and the exception
a loop raises when its timeout expired.
"""
from threading            import Thread
from time                 import sleep
from typing               import Optional as Nullable

from pyTooling.Exceptions import ToolingException
from pyTooling.Timeout    import Timeout, TimeoutExpiredError, TimeoutUsageError
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Seconds(self) -> None:
		timeout = Timeout(2.5)

		self.assertEqual(2.5, timeout.Seconds)
		self.assertIsNone(timeout.Deadline)
		self.assertIsNone(timeout.Parent)

	def test_Seconds_Int(self) -> None:
		timeout = Timeout(3)

		self.assertEqual(3.0, timeout.Seconds)
		self.assertIsInstance(timeout.Seconds, float)

	def test_Seconds_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Timeout(None)

		self.assertEqual("Parameter 'seconds' is None.", str(context.exception))

	def test_Seconds_Type(self) -> None:
		for value in ("1.0", True):
			with self.subTest(value=value):
				with self.assertRaises(TypeError) as context:
					_ = Timeout(value)

				self.assertEqual("Parameter 'seconds' is not of type 'float' or 'int'.", str(context.exception))

	def test_Seconds_NotPositive(self) -> None:
		for value in (0, -1.0):
			with self.subTest(value=value):
				with self.assertRaises(ValueError) as context:
					_ = Timeout(value)

				self.assertEqual("Parameter 'seconds' is not greater than zero.", str(context.exception))


class CurrentTimeout(Testcase):
	def test_NoTimeout(self) -> None:
		self.assertIsNone(Timeout.Remaining())
		self.assertFalse(Timeout.IsExpired())

	def test_Remaining(self) -> None:
		with Timeout(10.0) as timeout:
			first = Timeout.Remaining()
			sleep(0.05)
			second = Timeout.Remaining()

			self.assertIsNotNone(timeout.Deadline)
			self.assertGreater(first, 0.0)
			self.assertLessEqual(first, 10.0)
			self.assertLess(second, first)
			self.assertFalse(Timeout.IsExpired())

	def test_Expired(self) -> None:
		with Timeout(0.05):
			sleep(0.1)

			self.assertEqual(0.0, Timeout.Remaining())
			self.assertTrue(Timeout.IsExpired())

	def test_ExitRestores(self) -> None:
		with Timeout(10.0) as timeout:
			pass

		self.assertIsNone(timeout.Deadline)
		self.assertIsNone(Timeout.Remaining())

	def test_ExitOnException(self) -> None:
		with self.assertRaises(KeyError):
			with Timeout(10.0):
				raise KeyError("x")

		self.assertIsNone(Timeout.Remaining())


class Nesting(Testcase):
	def test_Shortens(self) -> None:
		with Timeout(10.0) as outer:
			with Timeout(1.0) as inner:
				self.assertIs(outer, inner.Parent)
				self.assertLess(inner.Deadline, outer.Deadline)
				self.assertLessEqual(Timeout.Remaining(), 1.0)

			self.assertGreater(Timeout.Remaining(), 1.0)

	def test_CantExtend(self) -> None:
		with Timeout(1.0) as outer:
			with Timeout(10.0) as inner:
				self.assertEqual(outer.Deadline, inner.Deadline)
				self.assertLessEqual(Timeout.Remaining(), 1.0)

	def test_ExpiredParent(self) -> None:
		with Timeout(0.05):
			sleep(0.1)

			with Timeout(10.0):
				self.assertTrue(Timeout.IsExpired())

	def test_ExitRestoresParent(self) -> None:
		with Timeout(10.0) as outer:
			with Timeout(1.0):
				pass

			self.assertGreater(Timeout.Remaining(), 1.0)
			self.assertIsNotNone(outer.Deadline)

	def test_Current(self) -> None:
		"""The current timeout is the innermost entered one, like the current thread."""
		self.assertIsNone(Timeout.Current())

		with Timeout(10.0) as outer:
			self.assertIs(outer, Timeout.Current())

			with Timeout(1.0) as inner:
				self.assertIs(inner, Timeout.Current())
				self.assertIs(outer, inner.Parent)

			self.assertIs(outer, Timeout.Current())

		self.assertIsNone(Timeout.Current())

	def test_ReEnter(self) -> None:
		"""A timeout is entered once at a time; after leaving it, it can be entered again."""
		timeout = Timeout(10.0)

		with timeout:
			with self.assertRaises(TimeoutUsageError) as context:
				with timeout:
					pass

			self.assertEqual("Timeout of 10.0 seconds is entered already.", str(context.exception))
			self.assertIs(timeout, Timeout.Current())

		with timeout:
			self.assertIs(timeout, Timeout.Current())


class Threads(Testcase):
	def test_OtherThread(self) -> None:
		"""A new thread starts without a current timeout."""
		seen: list[Nullable[float]] = []

		def worker() -> None:
			seen.append(Timeout.Remaining())

		with Timeout(10.0):
			thread = Thread(target=worker)
			thread.start()
			thread.join(timeout=Timeout.Remaining())

		self.assertListEqual([None], seen)

	def test_HandOver(self) -> None:
		"""The time left is handed over to a worker, which enters a timeout of its own."""
		seen: list[Nullable[float]] = []

		def worker(remaining: float) -> None:
			with Timeout(remaining):
				seen.append(Timeout.Remaining())

		with Timeout(10.0):
			thread = Thread(target=worker, args=(Timeout.Remaining(), ))
			thread.start()
			thread.join(timeout=Timeout.Remaining())

		self.assertEqual(1, len(seen))
		self.assertGreater(seen[0], 0.0)
		self.assertLessEqual(seen[0], 10.0)


class ExpiredError(Testcase):
	def test_Bases(self) -> None:
		self.assertTrue(issubclass(TimeoutExpiredError, ToolingException))
		self.assertTrue(issubclass(TimeoutExpiredError, TimeoutError))

	def test_Seconds(self) -> None:
		with self.assertRaises(TimeoutError) as context:
			raise TimeoutExpiredError("Scanning took longer than 20 seconds.", seconds=20.0)

		self.assertEqual("Scanning took longer than 20 seconds.", str(context.exception))
		self.assertEqual(20.0, context.exception.Seconds)

	def test_MessageOnly(self) -> None:
		with self.assertRaises(TimeoutExpiredError) as context:
			raise TimeoutExpiredError("Expired.")

		self.assertIsNone(context.exception.Seconds)
		self.assertIsNone(context.exception.Overrun)

	def test_RaiseIfExpired(self) -> None:
		"""A loop calls RaiseIfExpired once per iteration; the error carries the timeout and the overrun."""
		iterations = 0

		with self.assertRaises(TimeoutExpiredError) as context:
			with Timeout(0.05):
				while True:
					Timeout.RaiseIfExpired("Loop took too long.")

					iterations += 1
					sleep(0.01)

		self.assertGreater(iterations, 0)
		self.assertEqual("Loop took too long.", str(context.exception))
		self.assertEqual(0.05, context.exception.Seconds)
		self.assertGreaterEqual(context.exception.Overrun, 0.0)
		self.assertLess(context.exception.Overrun, 1.0)

	def test_RaiseIfExpired_NotExpired(self) -> None:
		Timeout.RaiseIfExpired("No timeout is current.")

		with Timeout(10.0):
			Timeout.RaiseIfExpired("Not expired yet.")

	def test_RaiseIfExpired_Message(self) -> None:
		with self.assertRaises(ValueError) as context:
			Timeout.RaiseIfExpired(None)

		self.assertEqual("Parameter 'message' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			Timeout.RaiseIfExpired(5)

		self.assertEqual("Parameter 'message' is not of type 'str'.", str(context.exception))

	def test_AbortingLoop(self) -> None:
		"""A loop checks the timeout and aborts itself."""
		iterations = 0

		with self.assertRaises(TimeoutExpiredError):
			with Timeout(0.05):
				while True:
					if Timeout.IsExpired():
						raise TimeoutExpiredError("Loop took too long.", seconds=0.05)

					iterations += 1
					sleep(0.01)

		self.assertGreater(iterations, 0)
