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
from inspect  import currentframe
from sys      import version_info
from types    import TracebackType
from typing   import List, Callable, Optional as Nullable, Type

try:
	from pyTooling.Decorators import export, readonly
	from pyTooling.Common     import getFullyQualifiedName
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Common] Could not import from 'pyTooling.*'!")

	try:
		from Decorators         import export, readonly
		from Common             import getFullyQualifiedName
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Common] Could not import directly!")
		raise ex


@export
class WarningCollector:
	"""
	A context manager to collect warnings within the call hierarchy.
	"""
	_warnings: List[_Warning]                        #: List of collected warnings.
	_handler:  Nullable[Callable[[_Warning], bool]]  #: Optional handler function, which is called per collected warning.

	def __init__(self, warnings: Nullable[List[_Warning]] = None, handler: Nullable[Callable[[_Warning], bool]] = None) -> None:
		"""
		Initializes a warning collector.

		:param warnings:   An optional reference to a list of warnings, which can be modified (appended) by this warning
		                   collector. If ``None``, an internal list is created and can be referenced by the collector's
		                   instance.
		:param handler:    An optional handler function, which processes the current warning and decides if a warning should
		                   be reraised as an exception.
		:raises TypeError: If optional parameter 'warnings' is not of type list.
		:raises TypeError: If optional parameter 'handler' is not a callable.
		"""
		if warnings is None:
			warnings = []
		elif not isinstance(warnings, list):
			ex = TypeError(f"Parameter 'warnings' is not list.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(warnings)}'.")
			raise ex

		if handler is not None and not isinstance(handler, Callable):
			ex = TypeError(f"Parameter 'handler' is not callable.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(handler)}'.")
			raise ex

		self._warnings = warnings
		self._handler = handler

	def __enter__(self) -> 'WarningCollector':  # -> Self: needs Python 3.11
		"""
		Enter the warning collector context.

		:returns: The warning collector instance.
		"""
		return self

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
		exc_val: Nullable[BaseException] = None,
		exc_tb: Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the warning collector context.

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		"""

		# outerFrame = currentframe().f_back
		# print("__exit__:")
		# for l in outerFrame.f_locals:
		# 	print(f"  {l}")
		#
		# outerFrame.f_locals.pop("ctx")

	@readonly
	def Warnings(self) -> List[_Warning]:
		"""
		Read-only property to access the list of collected warnings.

		:returns: A list of collected warnings.
		"""
		return self._warnings

	def AddWarning(self, warning: _Warning) -> bool:
		"""
		Add a warning to the list of warnings managed by this warning collector.

		:param warning:     The warning to add to the collectors internal warning list.
		:returns:           Return ``True`` if the warning collector has a local handler callback and this handler returned
		                    ``True``; otherwise ``False``.
		:raises ValueError: If parameter ``warning`` is None.
		:raises TypeError:  If parameter ``warning`` is not of type :class:`Warning`.
		"""
		if self._warnings is None:
			raise ValueError("Parameter 'warning' is None.")
		elif self._warnings is None or not isinstance(warning, _Warning):
			ex = TypeError(f"Parameter 'warning' is not of type 'Warning'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(warning)}'.")
			raise ex

		self._warnings.append(warning)

		if self._handler is not None:
			return self._handler(warning)

		return False

	@classmethod
	def Raise(cls, warning: _Warning) -> None:
		"""
		Walk the callstack frame by frame upwards and search for the first warning collector.

		:param warning:    Warning to send upwards in the call stack.
		:raises Exception: If warning should be converted to an exception.
		:raises Exception: If the call-stack walk couldn't find a warning collector.
		"""
		frame = currentframe()
		while frame := frame.f_back:
			for localValue in reversed(frame.f_locals.values()):
				if isinstance(localValue, cls):
					if localValue.AddWarning(warning):
						raise Exception(f"Warning: {warning}") from warning
					return
		else:
			raise Exception(f"Unhandled warning: {warning}") from warning
