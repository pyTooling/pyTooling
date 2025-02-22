# ==================================================================================================================== #
#                                                                                                                      #
#             _____           _ _               _____                    _   _                                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/                        #
# |_|    |___/                          |___/                     |_|                                                  #
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
Unit tests for :mod:`pyTooling.Exceptions`.
"""
from unittest     import TestCase

from pyTooling.Exceptions import EnvironmentException, PlatformNotSupportedException, NotConfiguredException


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def raise_EnvironmentExecption() -> None:
	raise EnvironmentException("Environment does not provide 'PATH'.")


def raise_PlatformNotSupportedException() -> None:
	raise PlatformNotSupportedException("Platform 'macOS' is not supported.")


def raise_NotConfiguredException() -> None:
	raise NotConfiguredException("Option 'WorkingDirectory' is not specified in the configuration file.")


class Exceptions(TestCase):
	def test_EnvironmentException(self) -> None:
		with self.assertRaises(EnvironmentException):
			raise_EnvironmentExecption()
		# self.assertEqual(context.exception.message, "Environment does not provide 'PATH'.")

	def test_PlatformNotSupportedException(self) -> None:
		with self.assertRaises(PlatformNotSupportedException):
			raise_PlatformNotSupportedException()
		# self.assertEqual(context.exception.message, "Platform 'OSX' is not supported.")

	def test_NotConfiguredException(self) -> None:
		with self.assertRaises(NotConfiguredException):
			raise_NotConfiguredException()
		# self.assertEqual(context.exception.message, "Option 'WorkingDirectory' is not specified in the configuration file.")
