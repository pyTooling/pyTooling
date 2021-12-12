# =============================================================================
#             _____           _ _
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |
# | |_) | |_| || | (_) | (_) | | | | | | (_| |
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |
# |_|    |___/                          |___/
# =============================================================================
# Authors:            Patrick Lehmann
#
# Python unittest:    Testing the pyExceptions module
#
# License:
# ============================================================================
# Copyright 2017-2021 Patrick Lehmann - Bötzingen, Germany
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0
# ============================================================================
#
"""
pyTooling.Exceptions
####################

:copyright: Copyright 2007-2021 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from unittest     import TestCase

from pyTooling.Exceptions import EnvironmentException, PlatformNotSupportedException, NotConfiguredException


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)

def raise_EnvironmentExecption():
	raise EnvironmentException("Environment does not provide 'PATH'.")

def raise_PlatformNotSupportedException():
	raise PlatformNotSupportedException("Platform 'OSX' is not supported.")

def raise_NotConfiguredException():
	raise NotConfiguredException("Option 'WorkingDirectory' is not specified in the configuration file.")


class Exceptions(TestCase):
	def test_EnvironmentException(self) -> None:
		with self.assertRaises(EnvironmentException) as context:
			raise_EnvironmentExecption()
		# self.assertEqual(context.exception.message, "Environment does not provide 'PATH'.")

	def test_PlatformNotSupportedException(self) -> None:
		with self.assertRaises(PlatformNotSupportedException) as context:
			raise_PlatformNotSupportedException()
		# self.assertEqual(context.exception.message, "Platform 'OSX' is not supported.")

	def test_NotConfiguredException(self) -> None:
		with self.assertRaises(NotConfiguredException) as context:
			raise_NotConfiguredException()
		# self.assertEqual(context.exception.message, "Option 'WorkingDirectory' is not specified in the configuration file.")
