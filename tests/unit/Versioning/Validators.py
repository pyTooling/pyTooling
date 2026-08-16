# ==================================================================================================================== #
#             _____           _ _           __     __            _             _                                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ \ \   / /__ _ __ ___(_) ___  _ __ (_)_ __   __ _                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` \ \ / / _ \ '__/ __| |/ _ \| '_ \| | '_ \ / _` |                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |\ V /  __/ |  \__ \ | (_) | | | | | | | | (_| |                          #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/ \___|_|  |___/_|\___/|_| |_|_|_| |_|\__, |                          #
# |_|    |___/                          |___/                                          |___/                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2020-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Unit tests for version validators and the exception raised when one rejects a version."""
from unittest              import TestCase

from pyTooling.Exceptions  import ToolingException
from pyTooling.Versioning  import CalendarVersion, SemanticVersion, VersionValidatorException


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Validators(TestCase):
	"""A validator rejecting a parsed version raises VersionValidatorException, not a generic ValueError."""

	def test_AnAcceptedSemanticVersionIsReturned(self) -> None:
		version = SemanticVersion.Parse("1.2.3", validator=lambda v: v.Major == 1)

		self.assertEqual(1, version.Major)

	def test_ARejectedSemanticVersionRaises(self) -> None:
		with self.assertRaises(VersionValidatorException) as context:
			SemanticVersion.Parse("2.0.0", validator=lambda v: v.Major == 1)

		self.assertIn("2.0.0", str(context.exception))

	def test_TheRejectedVersionIsCarried(self) -> None:
		"""The caller gets the version object, not only the string it came from."""
		with self.assertRaises(VersionValidatorException) as context:
			SemanticVersion.Parse("2.0.0", validator=lambda v: False)

		self.assertEqual(2, context.exception.Version.Major)

	def test_ARejectedCalendarVersionRaises(self) -> None:
		with self.assertRaises(VersionValidatorException) as context:
			CalendarVersion.Parse("2026.08", validator=lambda v: False)

		self.assertIsInstance(context.exception.Version, CalendarVersion)

	def test_ItIsAToolingException(self) -> None:
		"""So a caller can catch every pyTooling error in one place."""
		with self.assertRaises(ToolingException):
			SemanticVersion.Parse("2.0.0", validator=lambda v: False)
