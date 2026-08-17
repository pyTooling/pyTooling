# ==================================================================================================================== #
#             _____           _ _           __        __               _                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \      / /_ _ _ __ _ __ (_)_ __   __ _                                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ /\ / / _` | '__| '_ \| | '_ \ / _` |                                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V  V / (_| | |  | | | | | | | | (_| |                                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/\_/ \__,_|_|  |_| |_|_|_| |_|\__, |                                  #
# |_|    |___/                          |___/                                  |___/                                   #
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
"""Unit tests for :class:`pyTooling.Warning.ThreadSupervisor` and the exception it raises."""
from pyTooling.Warning    import SupervisedThreadException, ThreadSupervisor
from pyTooling.Testing    import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ReRaising(Testcase):
	"""What ThreadSupervisor.ReRaise() raises for none, one and several collected exceptions."""

	@staticmethod
	def _supervisorWith(*threadNames: str) -> ThreadSupervisor:
		supervisor = ThreadSupervisor()
		for threadName in threadNames:
			supervisor.AddException(threadName, ValueError(f"{threadName} failed"))

		return supervisor

	def test_NothingCollectedRaisesNothing(self) -> None:
		self._supervisorWith().ReRaise()

	def test_OneExceptionIsWrapped(self) -> None:
		with self.assertRaises(SupervisedThreadException) as context:
			self._supervisorWith("Worker").ReRaise()

		self.assertEqual("Worker", context.exception.ThreadName)
		self.assertIsInstance(context.exception.__cause__, ValueError)

	def test_OneExceptionIsRaisedUnwrapped(self) -> None:
		with self.assertRaises(ValueError):
			self._supervisorWith("Worker").ReRaise(unwrapped=True)

	def test_SeveralExceptionsAreGrouped(self) -> None:
		"""This raised 'TypeError: __init__() missing 1 required positional argument' before the signature change."""
		with self.assertRaises(ExceptionGroup) as context:
			self._supervisorWith("Alpha", "Beta").ReRaise()

		wrapped = context.exception.exceptions
		self.assertEqual(2, len(wrapped))
		self.assertCountEqual(["Alpha", "Beta"], [exception.ThreadName for exception in wrapped])
		for exception in wrapped:
			self.assertIsInstance(exception, SupervisedThreadException)
			self.assertIsInstance(exception.__cause__, ValueError)

	def test_SeveralExceptionsAreGroupedUnwrapped(self) -> None:
		with self.assertRaises(ExceptionGroup) as context:
			self._supervisorWith("Alpha", "Beta").ReRaise(unwrapped=True)

		self.assertTrue(all(isinstance(exception, ValueError) for exception in context.exception.exceptions))
