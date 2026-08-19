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

.. seealso::

   :mod:`pyTooling.Exceptions`
      |rarr| Exceptions, which are raised instead of collected.
   :mod:`pyTooling.TerminalUI`
      |rarr| Writing the collected warnings to the terminal.
"""
from threading import local, Lock
from types     import TracebackType
from typing    import List, Callable, Optional as Nullable, Type, Iterator, Self, Iterable, Tuple, Union

from pyTooling.Decorators import export, readonly
from pyTooling.Common     import getFullyQualifiedName
from pyTooling.Exceptions import ExceptionBase


__all__ = ["_threadLocalData", "AnyWarning"]


_threadLocalData = local()
"""A reference to the thread local data needed by the pyTooling.Warning classes."""


@export
class CriticalWarning(BaseException):
	"""
	Base-exception of all critical warnings handled by :class:`WarningCollector`.

	.. tip::

	   Critical warnings must be unhandled within a call hierarchy, otherwise a :exc:`UnhandledCriticalWarningException`
	   will be raised.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> Tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


@export
class Warning(BaseException):
	"""
	Base-exception of all warnings handled by :class:`WarningCollector`.

	.. tip::

	   Warnings can be unhandled within a call hierarchy.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> Tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


AnyWarning = Union[CriticalWarning, Warning]


@export
class UnhandledCriticalWarningException(ExceptionBase):
	"""
	This exception is raised when a critical warning isn't handled by a :class:`WarningCollector` within the
	call-hierarchy.
	"""


@export
class UnhandledExceptionException(ExceptionBase):
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

	__slots__ = ("_parent", "_warnings", "_handler")

	def __init__(
		self,
		warnings: Nullable[List[BaseException]] = None,
		handler:  Nullable[Callable[[BaseException], bool]] = None
	) -> None:
		"""
		Initializes a warning collector.

		:param warnings:   An optional reference to a list of warnings, which can be modified (appended) by this warning
		                   collector. If ``None``, an internal list is created and can be referenced by the collector's
		                   instance.
		:param handler:    An optional handler function, which processes the current warning and decides if a warning should
		                   be reraised as an exception.
		:raises TypeError: If optional parameter 'warnings' is not of type :class:`list`.
		:raises TypeError: If optional parameter 'handler' is not a callable.
		"""
		if warnings is None:
			warnings = []
		elif not isinstance(warnings, list):
			ex = TypeError(f"Parameter 'warnings' is not a list.")
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

	def __iter__(self) -> Iterator[Warning | CriticalWarning | Exception]:
		"""
		Return an iterator over all collected warnings.

		:returns: Iterator over the collected warnings.
		"""
		return iter(self._warnings)

	def __getitem__(self, index: int) -> Warning | CriticalWarning | Exception:
		"""
		Access a collected warning by index.

		:param index: Index of the warning.
		:returns:     Collected warning.
		"""
		return self._warnings[index]

	def __enter__(self) -> Self:
		"""
		Enter the warning collector context.

		:returns: The warning collector instance.
		"""
		global _threadLocalData

		try:
			self._parent = _threadLocalData.warningCollector
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

		return False

	@property
	def Parent(self) -> Nullable[Self]:
		"""
		Property to access the parent warning collector.

		:returns: The parent warning collector or ``None``.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, value: Self) -> None:
		self._parent = value

	@readonly
	def Warnings(self) -> List[Warning | CriticalWarning | Exception]:
		"""
		Read-only property to access the list of collected warnings.

		:returns: A list of collected warnings.
		"""
		return self._warnings

	def AddWarning(self, warning: Warning | CriticalWarning | Exception) -> bool:
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
	def Raise(
		cls,
		warning: Warning | CriticalWarning | Exception,
		cause:   Nullable[Exception] = None,
		*,
		notes:   Nullable[str | Iterable[str]] = None
	) -> None:
		"""
		Walk the callstack frame by frame upwards and search for the first warning collector.

		:param warning:                            Warning to send upwards in the call stack.
		:param cause:                              Optional, root cause to be added to the warning.
		:param notes:                              optional, a single note or a list of notes to be added to the warning.
		:raises Exception:                         If warning should be converted to an exception.
		:raises UnhandledExceptionException:       If no warning collector was found along the call-hierarchy to collect and
		                                           handle an exception.
		:raises UnhandledCriticalWarningException:  If no warning collector was found along the call-hierarchy to collect
		                                           and handle a critical warning. |br|
		                                           Add a with-statement using :class:`WarningCollector` somewhere up the
		                                           call-hierarchy to receive and collect warnings.
		"""
		global _threadLocalData

		if cause is not None:
			warning.__cause__ = cause

		if notes is not None:
			if isinstance(notes, str):
				warning.add_note(notes)
			else:
				for note in notes:
					warning.add_note(note)

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


@export
class SupervisedWarningCollectorException(ExceptionBase):
	"""
	This exception is raised when a supervised warning collector is not the top-most collector in its thread.

	A supervised collector hands its warnings to the thread supervisor, which only works if nothing else collects them
	first.
	"""


@export
class SupervisedWarningCollector(WarningCollector):
	"""
	A context manager to collect warnings within the call hierarchy.
	"""
	_supervisor:       Nullable["ThreadSupervisor"]               #: Supervisor collecting warnings and exceptions of all threads.
	_exceptionHandler: Nullable[Callable[[BaseException], bool]]  #: Handler called for an exception escaping the thread.
	_finallyHandler:   Nullable[Callable[[], None]]               #: Handler called when the thread ends, in either case.

	__slots__ = ("_supervisor", "_exceptionHandler", "_finallyHandler")

	def __init__(
		self,
		warnings:         Nullable[List[BaseException]] =             None,
		handler:          Nullable[Callable[[BaseException], bool]] = None,
		/,
		supervisor:       Nullable["ThreadSupervisor"] =              None,
		exceptionHandler: Nullable[Callable[[BaseException], bool]] = None,
		finallyHandler:   Nullable[Callable[[], None]] =              None
	) -> None:
		"""
		Initializes a warning collector.

		:param warnings:         An optional reference to a list of warnings, which can be modified (appended) by this
		                         warning collector. If ``None``, an internal list is created and can be referenced by the
		                         collector's instance.
		:param handler:          An optional handler function, which processes the current warning and decides if a warning
		                         should be reraised as an exception.
		:param supervisor:       An optional thread supervisor. On leaving the context, the collected warnings and an
		                         exception leaving the block are handed to it, so the thread that started this one can
		                         reraise them. Without a supervisor, an exception leaves the block unchanged.
		:param exceptionHandler: An optional handler function, called with an exception leaving the block when a supervisor
		                         is set. Its result decides whether the exception is suppressed.
		:param finallyHandler:   An optional function called when the context is left, whether or not an exception left it.
		:raises TypeError:       If optional parameter 'warnings' is not of type :class:`list`.
		:raises TypeError:       If optional parameter 'handler' is not a callable.
		"""
		super().__init__(warnings, handler)

		self._supervisor =       supervisor
		self._exceptionHandler = exceptionHandler
		self._finallyHandler =   finallyHandler

	def __enter__(self) -> Self:
		"""
		Enter the warning collector context.

		:returns:                                    The warning collector instance.
		:raises SupervisedWarningCollectorException: If this collector is not the top-most warning collector of its thread.
		"""
		global _threadLocalData

		if hasattr(_threadLocalData, "warningCollector") and _threadLocalData.warningCollector is not None:
			raise SupervisedWarningCollectorException("This warning collector is not the top-most warning collector within the current thread.")

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

		_threadLocalData.warningCollector = None

		if self._supervisor is not None:
			result = True
			if len(self._warnings) > 0:
				self._supervisor.AddWarnings(self._warnings)

			if exc_val is not None:
				self._supervisor.AddException("", exc_val)

				if self._exceptionHandler is not None:
					result = self._exceptionHandler(exc_val)
		else:
			result = None

		if self._finallyHandler is not None:
			self._finallyHandler()

		return result


@export
class SupervisedThreadException(ExceptionBase):
	"""
	The exception is raise if a supervised thread received an unhandled exception which got collected by
	:class:`ExceptionCollector`.
	"""
	_threadName: Nullable[str]  #: Name of the thread the exception was raised in.

	def __init__(
		self,
		message: str,
		/,
		*,
		threadName: Nullable[str] = None,
		cause: Nullable[BaseException] = None
	) -> None:
		"""
		Initializes the exception with the name of the thread that failed.

		:param message:    The exception's message.
		:param threadName: Name of the thread that raised the collected exception.
		:param cause:      The exception collected from that thread.
		"""
		super().__init__(message)
		self._threadName = threadName
		self.__cause__ = cause

	@readonly
	def ThreadName(self) -> Nullable[str]:
		"""
		Read-only property to access the name of the thread that raised the exception (:attr:`_threadName`).

		:returns: Name of the thread, or ``None`` if it wasn't recorded.
		"""
		return self._threadName


@export
class ThreadSupervisor:
	"""
	Thread-safe collector of exceptions and warnings raised in worker threads for surfacing on another thread.

	This thread supervisor should be used in combination with :class:`WarningCollector` to accumulate exceptions
	(:class:`BaseException`) and warnings (:class:`CriticalWarning` or :class:`Warning`).

	.. code-block:: python

	   @export
	   class MyThread(Thread):
	     def __init__(
	       self,
	       threadSupervisor: ThreadSupervisor,
	       stopEvent:        Event
	     ) -> None:
	       super().__init__(name="MyThread", daemon=True)

	       self._threadSupervisor = threadSupervisor
	       self._stopEvent =        stopEvent

	     def run(self) -> None:
	       def exceptionHandler(ex: BaseException) -> None:
	         self._stopEvent.set()

	       def finallyHandler() -> None:
	         # some finally code

	       with SupervisedWarningCollector(
	         supervisor=self._threadSupervisor,
	         exceptionHandler=exceptionHandler,
	         finallyHandler=finallyHandler
	       ) as warnings:
	         # Thread body

	.. code-block:: python

	   def RunVivadoPipeline(
	     self,
	   ) -> List[AnyWarning]:
	     stopEvent =        Event()
	     threadSupervisor = ThreadSupervisor()

	     myThread = MyThread(threadSupervisor, stopEvent)
	     myThread.start()

	     try:
	       myThread.join()
	     except KeyboardInterrupt:
	       stopEvent.set()
	       myThread.join(timeout=2.0)
	       raise

	     threadSupervisor.ReRaise()

	     return threadSupervisor.Warnings
	"""

	_lock:       Lock                             #: Lock serializing the collection from multiple threads.
	_exceptions: List[Tuple[str, BaseException]]  #: Exceptions of all supervised threads, as (thread name, exception).
	_warnings:   List[Tuple[str, AnyWarning]]     #: Warnings of all supervised threads, as (thread name, warning).

	__slots__ = ("_lock", "_exceptions", "_warnings")

	def __init__(self) -> None:
		self._lock =       Lock()
		self._exceptions = []
		self._warnings =   []

	@readonly
	def HasWarning(self) -> bool:
		"""
		Check if at least one warning was collected from a supervised thread.

		:returns: ``True``, if at least one warning was collected.
		"""
		with self._lock:
			return len(self._warnings) > 0

	@readonly
	def HasExceptions(self) -> bool:
		"""
		Check if at least one exception was collected from a supervised thread.

		:returns: ``True``, if at least one exception was collected.
		"""
		with self._lock:
			return len(self._exceptions) > 0

	@readonly
	def Warnings(self) -> List[AnyWarning]:
		"""
		Read-only property to return all warnings collected from supervised threads (:attr:`_warnings`).

		:returns: List of collected warnings, without their thread names.
		"""
		with self._lock:
			return [warning for _, warning in self._warnings]

	def AddWarning(self, threadName: str, warning: AnyWarning) -> None:
		"""
		Collect a warning raised in a supervised thread.

		:param threadName: Name of the thread the warning was raised in.
		:param warning:    The warning to collect.
		"""
		with self._lock:
			self._warnings.append((threadName, warning))

	def AddWarnings(self, threadName: str, warnings: List[AnyWarning]) -> None:
		"""
		Collect several warnings raised in a supervised thread.

		:param threadName: Name of the thread the warnings were raised in.
		:param warnings:   The warnings to collect.
		"""
		with self._lock:
			self._warnings.extend((threadName, warning) for warning in warnings)

	def AddException(self, threadName: str, ex: BaseException) -> None:
		"""
		Collect an exception that escaped a supervised thread.

		:param threadName: Name of the thread the exception was raised in.
		:param ex:         The exception to collect.
		"""
		with self._lock:
			self._exceptions.append((threadName, ex))

	def ReRaise(self, unwrapped: bool = False) -> None:
		"""
		Re-raise the exceptions collected from the supervised threads in the supervising thread.

		A single exception is re-raised as itself - wrapped in a :exc:`SupervisedThreadException` naming its thread,
		unless ``unwrapped`` is set. Several exceptions are raised as an :exc:`ExceptionGroup`, so none of them is lost.

		:param unwrapped:                  If ``True``, a single exception is raised as it was, without naming its
		                                   thread.
		:raises SupervisedThreadException: If exactly one thread failed.
		:raises ExceptionGroup:            If more than one thread failed.
		"""
		with self._lock:
			if len(self._exceptions) == 0:
				return

			exceptions = list(self._exceptions)

		if len(exceptions) == 1:
			threadName, ex = exceptions[0]
			if unwrapped:
				raise ex
			else:
				raise SupervisedThreadException(f"Thread '{threadName}' failed.", threadName=threadName) from ex

		elif unwrapped:
			raise ExceptionGroup(
				"Multiple threads failed.",
				[ex for _, ex in exceptions]
			)
		else:
			raise ExceptionGroup(
				"Multiple threads failed.",
				[
					SupervisedThreadException(f"Thread '{threadName}' failed.", threadName=threadName, cause=ex)
					for threadName, ex in exceptions
				]
			)
