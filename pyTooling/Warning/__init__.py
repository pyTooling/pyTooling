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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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

.. hint::

   See :ref:`high-level help <WARNING>` for explanations and usage examples.
"""
from threading import local
from types     import TracebackType
from typing    import List, Callable, Optional as Nullable, Type, Iterator, Self

try:
	from pyTooling.Decorators import export, readonly
	from pyTooling.Common     import getFullyQualifiedName
	from pyTooling.Exceptions import ExceptionBase
except ModuleNotFoundError:  # pragma: no cover
	print("[pyTooling.Warning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators         import export, readonly
		from Common             import getFullyQualifiedName
		from Exceptions         import ExceptionBase
	except ModuleNotFoundError as ex:  # pragma: no cover
		print("[pyTooling.Warning] Could not import directly!")
		raise ex


__all__ = ["_threadLocalData"]

_threadLocalData = local()
"""A reference to the thread local data needed by the pyTooling.Warning classes."""


@export
class Warning(BaseException):
	"""
	Base-exception of all warnings handled by :class:`WarningCollector`.

	.. tip::

	   Warnings can be unhandled within a call hierarchy.
	"""


@export
class CriticalWarning(BaseException):
	"""
	Base-exception of all critical warnings handled by :class:`WarningCollector`.

	.. tip::

	   Critical warnings must be unhandled within a call hierarchy, otherwise a :exc:`UnhandledCriticalWarningException`
	   will be raised.
	"""


@export
class UnhandledWarningException(ExceptionBase):   # FIXME: to be removed in v9.0.0
	"""
	Deprecated.

	.. deprecated:: v9.0.0

	   Please use :exc:`UnhandledCriticalWarningException`.
	"""


@export
class UnhandledCriticalWarningException(UnhandledWarningException):
	"""
	This exception is raised when a critical warning isn't handled by a :class:`WarningCollector` within the
	call-hierarchy.
	"""


@export
class UnhandledExceptionException(UnhandledWarningException):
	"""
	This exception is raised when an exception isn't handled by a :class:`WarningCollector` within the call-hierarchy.
	"""


@export
class WarningCollector:
	"""
	A context manager to collect warnings within the call hierarchy.
	"""
	_parent:   Nullable["WarningCollector"]               #: Parent WarningCollector
	_warnings: List[BaseException]                        #: List of collected warnings (and exceptions).
	_handler:  Nullable[Callable[[BaseException], bool]]  #: Optional handler function, which is called per collected warning.

	def __init__(
		self,
		warnings: Nullable[List[BaseException]] = None,
		handler: Nullable[Callable[[BaseException], bool]] = None
	) -> None:
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
			ex.add_note(f"Got type '{getFullyQualifiedName(warnings)}'.")
			raise ex

		if handler is not None and not isinstance(handler, Callable):
			ex = TypeError(f"Parameter 'handler' is not callable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(handler)}'.")
			raise ex

		self._parent =   None
		self._warnings = warnings
		self._handler =  handler

	def __len__(self) -> int:
		"""
		Returns the number of collected warnings.

		:returns: Number of collected warnings.
		"""
		return len(self._warnings)

	def __iter__(self) -> Iterator[BaseException]:
		return iter(self._warnings)

	def __getitem__(self, index: int) -> BaseException:
		return self._warnings[index]

	def __enter__(self) -> Self:
		"""
		Enter the warning collector context.

		:returns: The warning collector instance.
		"""
		global _threadLocalData

		try:
			self.Parent = _threadLocalData.warningCollector
		except AttributeError:
			pass

		_threadLocalData.warningCollector = self

		return self

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the warning collector context.

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		:returns:        ``None``
		"""
		global _threadLocalData

		_threadLocalData.warningCollector = self._parent

	@property
	def Parent(self) -> Nullable["WarningCollector"]:
		"""
		Property to access the parent warning collected.

		:returns: The parent warning collector or ``None``.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, value: "WarningCollector") -> None:
		self._parent = value

	@readonly
	def Warnings(self) -> List[BaseException]:
		"""
		Read-only property to access the list of collected warnings.

		:returns: A list of collected warnings.
		"""
		return self._warnings

	def AddWarning(self, warning: BaseException) -> bool:
		"""
		Add a warning to the list of warnings managed by this warning collector.

		:param warning:     The warning to add to the collectors internal warning list.
		:returns:           Return ``True`` if the warning collector has a local handler callback and this handler returned
		                    ``True``; otherwise ``False``.
		:raises ValueError: If parameter ``warning`` is None.
		:raises TypeError:  If parameter ``warning`` is not of type :class:`Warning`.
		"""
		if warning is None:
			raise ValueError("Parameter 'warning' is None.")
		elif not isinstance(warning, (Warning, CriticalWarning, Exception)):
			ex = TypeError(f"Parameter 'warning' is not of type 'Warning', 'CriticalWarning' or 'Exception'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(warning)}'.")
			raise ex

		self._warnings.append(warning)

		return False if self._handler is None else self._handler(warning)

	@classmethod
	def Raise(cls, warning: BaseException) -> None:
		"""
		Walk the callstack frame by frame upwards and search for the first warning collector.

		:param warning:    Warning to send upwards in the call stack.
		:raises Exception: If warning should be converted to an exception.
		:raises Exception: If the call-stack walk couldn't find a warning collector.
		"""
		global _threadLocalData
		try:
			warningCollector = _threadLocalData.warningCollector
			if warningCollector.AddWarning(warning):
				raise Exception(f"Warning: {warning}") from warning
		except AttributeError:
			ex = None
			if isinstance(warning, Exception):
				ex = UnhandledExceptionException(f"Unhandled Exception: {warning}")
			elif isinstance(warning, CriticalWarning):
				ex = UnhandledCriticalWarningException(f"Unhandled Critical Warning: {warning}")

			if ex is not None:
				ex.add_note(f"Add a 'with'-statement using '{cls.__name__}' somewhere up the call-hierarchy to receive and collect warnings.")
				raise ex from warning
