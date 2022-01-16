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
"""A common set of missing exceptions in Python."""
from ..Decorators import export


@export
class ExceptionBase(Exception):
	"""Base exception derived from :py:exc:`Exception <python:Exception>` for all custom exceptions."""

#	@DocumentMemberAttribute()
	def __init__(self, message: str = "") -> None:
		"""
		pyExceptions initializer.

		:param message:   The exception message.
		"""
		super().__init__()
		self.message = message

#	@DocumentMemberAttribute()
	def __str__(self) -> str:
		"""Returns the exception's message text."""
		return self.message

#	@DocumentMemberAttribute(False)
	def with_traceback(self, tb) -> None:
		super().with_traceback(tb)

	# @DocumentMemberAttribute(False)
	# @MethodAlias(pyExceptions.with_traceback)
	# def with_traceback(self): pass


@export
class EnvironmentException(ExceptionBase):
	"""``EnvironmentException`` is raised when an expected environment variable is missing."""


@export
class PlatformNotSupportedException(ExceptionBase):
	"""``PlatformNotSupportedException`` is raise if the platform is not supported."""


@export
class NotConfiguredException(ExceptionBase):
	"""``NotConfiguredException`` is raise if the requested setting is not configured."""
