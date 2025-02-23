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
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A solution to send warnings like exceptions to a handler in the upper part of the call-stack.

.. hint:: See :ref:`high-level help <WARNING>` for explanations and usage examples.
"""
from builtins import Warning as _Warning

from inspect import currentframe
from typing import List, Callable, Optional as Nullable

try:
	from pyTooling.Decorators import export
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Common] Could not import from 'pyTooling.*'!")

	try:
		from Decorators         import export
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Common] Could not import directly!")
		raise ex


@export
class WarningCollector:
	_warnings: Nullable[List]
	_handler:  Nullable[Callable[[_Warning], bool]]

	def __init__(self, warnings: Nullable[List] = None, handler: Nullable[Callable[[_Warning], bool]] = None):
		self._warnings = warnings
		self._handler = handler

	def __enter__(self) -> 'WarningCollector':  # -> Self: needs Python 3.11
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass

	def AddWarning(self, warning: _Warning) -> bool:
		if self._warnings is not None:
			self._warnings.append(warning)
		if self._handler is not None:
			return self._handler(warning)

		return False

	@classmethod
	def Raise(cls, warning: _Warning) -> None:
		frame = currentframe()
		while frame := frame.f_back:
			for localValue in reversed(frame.f_locals.values()):
				if isinstance(localValue, cls):
					if localValue.AddWarning(warning):
						raise Exception(f"Warning: {warning}") from warning
					return
		else:
			raise Exception(f"Unhandled warning: {warning}") from warning
