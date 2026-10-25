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
from __future__           import annotations

from threading            import current_thread, local, Lock
from types                import TracebackType
from typing               import Callable, Optional as Nullable, Iterator, Self, Iterable, Union

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

	.. important::

	   A critical warning must be collected by a :class:`WarningCollector` up the call-hierarchy, otherwise
	   :meth:`WarningCollector.Raise` raises an :exc:`UnhandledCriticalWarningError`.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


@export
class Warning(BaseException):
	"""
	Base-exception of all warnings handled by :class:`WarningCollector`.

	.. attention::

	   A warning doesn't need a collector: without a :class:`WarningCollector` up the call-hierarchy, it's dropped
	   silently.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


AnyWarning = Union[CriticalWarning, Warning]


@export
class UnhandledCriticalWarningError(ExceptionBase):
	"""
	This exception is raised when a critical warning isn't handled by a :class:`WarningCollector` within the
	call-hierarchy.

	:meth:`WarningCollector.Raise` raises it, if no collector is current in the calling thread. The critical warning is
	its cause (``__cause__``), and a note says how to collect it.
	"""


@export
class UnhandledExceptionError(ExceptionBase):
	"""
	This exception is raised when an exception isn't handled by a :class:`WarningCollector` within the call-hierarchy.

	:meth:`WarningCollector.Raise` raises it, if no collector is current in the calling thread. The exception is its
	cause (``__cause__``), and a note says how to collect it.
	"""


@export
class EscalatedWarningError(ExceptionBase):
	"""
	This exception is raised when a :class:`WarningCollector` decides a collected warning is escalated.

	:meth:`WarningCollector.Raise` hands a warning to the current collector, which appends it to its list and calls its
	handler. A handler returning ``True`` asks for the warning to be escalated: :meth:`~WarningCollector.Raise` raises
	this exception, and the warning becomes its cause (``__cause__``). The warning stays in the collector's list.

	Any function reporting a warning can raise it, but only when the caller installed a handler returning ``True`` for
	that warning.
	"""


@export
class WarningCollector:
	"""
	A context manager to collect warnings within the call hierarchy.

	Entering the context makes the collector the *current* one of its thread, and :meth:`Raise` hands a warning to the
	current collector. Collectors are kept per thread: a warning raised in another thread doesn't reach it, see
	:class:`SupervisedWarningCollector`.

	Collectors can be nested. The previous current collector becomes the :attr:`Parent`, and only the innermost
	collector receives a warning - the parent doesn't see it, unless it's passed on, e.g. by :meth:`AddWarning`.

	The collected warnings are accessible by :attr:`Warnings`, by iteration, by :func:`len` and by index.
	"""
	_parent:   Nullable[WarningCollector]                 #: Parent WarningCollector
	_warnings: list[BaseException]                        #: List of collected warnings (and exceptions).
	_handler:  Nullable[Callable[[BaseException], bool]]  #: Optional handler function, which is called per collected warning.

	__slots__ = ("_parent", "_warnings", "_handler")

	def __init__(
		self,
		warnings: Nullable[list[BaseException]] = None,
		handler:  Nullable[Callable[[BaseException], bool]] = None
	) -> None:
		"""
		Initializes a warning collector.

		:param warnings:   Optional, reference to a list of warnings, which can be modified (appended) by this warning
		                   collector. If ``None``, an internal list is created and can be referenced by the collector's
		                   instance.
		:param handler:    Optional, handler function, which is called with each collected warning and decides, if it's
		                   escalated. If it returns ``True``, :meth:`Raise` raises an :exc:`EscalatedWarningError`, whose
		                   cause is the warning. An exception raised by the handler propagates through :meth:`Raise`.
		:raises TypeError: If optional parameter 'warnings' is not of type list.
		:raises TypeError: If optional parameter 'handler' is not a callable.
		"""
		if warnings is None:
			warnings = []
		elif not isinstance(warnings, list):
			ex = TypeError("Parameter 'warnings' is not a list.")
			ex.add_note(f"Got type '{getFullyQualifiedName(warnings)}'.")
			raise ex

		if handler is not None and not isinstance(handler, Callable):
			ex = TypeError("Parameter 'handler' is not callable.")
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
		Enter the context and make this warning collector the current one.

		The previous current warning collector becomes its parent.

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
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and make the parent warning collector the current one again.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``False``, so an exception raised in the context propagates.
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
	def Warnings(self) -> list[Warning | CriticalWarning | Exception]:
		"""
		Read-only property to access the list of collected warnings.

		:returns: A list of collected warnings.
		"""
		return self._warnings

	def AddWarning(self, warning: Warning | CriticalWarning | Exception) -> bool:
		"""
		Add a warning to the list of warnings managed by this warning collector and call its handler.

		An exception raised by the handler propagates.

		:param warning:     The warning to add to the collector's internal warning list.
		:returns:           Return ``True`` if the warning collector has a local handler callback and this handler returned
		                    ``True``; otherwise ``False``.
		:raises ValueError: If parameter ``warning`` is None.
		:raises TypeError:  If parameter ``warning`` is not of type :class:`Warning`, :class:`CriticalWarning` or
		                    :exc:`Exception`.
		"""
		if warning is None:
			raise ValueError("Parameter 'warning' is None.")
		elif not isinstance(warning, (Warning, CriticalWarning, Exception)):
			ex = TypeError("Parameter 'warning' is not of type 'Warning', 'CriticalWarning' or 'Exception'.")
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
		Hand a warning to the current warning collector of the calling thread.

		The current collector is the innermost :class:`WarningCollector` context entered in the calling thread. It appends
		the warning to its list (:meth:`AddWarning`) and calls its handler. Without a current collector, a :class:`Warning`
		is dropped, while a :class:`CriticalWarning` or an :exc:`Exception` is wrapped in an exception and raised.

		Called inside a generator, the warning reaches the collector current when the generator is resumed, i.e. the one
		of the code consuming it. An exception raised by the collector's handler propagates.

		:param warning:                        Warning to send to the current warning collector.
		:param cause:                          Optional, root cause to be added to the warning (``__cause__``).
		:param notes:                          Optional, a single note or a list of notes to be added to the warning.
		:raises ValueError:                    If parameter ``warning`` is None and a warning collector is current.
		:raises TypeError:                     If parameter ``warning`` is not of type :class:`Warning`,
		                                       :class:`CriticalWarning` or :exc:`Exception` and a warning collector is
		                                       current.
		:raises EscalatedWarningError:         If the warning collector's handler asks for the warning to be escalated.
		:raises UnhandledExceptionError:       If no warning collector was found along the call-hierarchy to collect and
		                                       handle an exception.
		:raises UnhandledCriticalWarningError: If no warning collector was found along the call-hierarchy to collect
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

		if (warningCollector := getattr(_threadLocalData, "warningCollector", None)) is None:
			ex = None
			if isinstance(warning, Exception):
				ex = UnhandledExceptionError(f"Unhandled Exception: {warning}")
			elif isinstance(warning, CriticalWarning):
				ex = UnhandledCriticalWarningError(f"Unhandled Critical Warning: {warning}")

			if ex is not None:
				ex.add_note(f"Add a 'with'-statement using '{cls.__name__}' somewhere up the call-hierarchy to receive and collect warnings.")
				raise ex from warning
		elif warningCollector.AddWarning(warning):
			raise EscalatedWarningError(f"Warning: {warning}") from warning


@export
class SupervisedWarningCollectorError(ExceptionBase):
	"""
	This exception is raised when a supervised warning collector is not the top-most collector in its thread.

	A supervised collector hands its warnings to the thread supervisor, which only works if nothing else collects them
	first.
	"""


@export
class SupervisedWarningCollector(WarningCollector):
	"""
	A context manager to collect the warnings of a thread and hand them to a :class:`ThreadSupervisor`.

	It's the top-most warning collector of its thread. On leaving the context, the collected warnings and an exception
	leaving the block are handed to the supervisor, so the thread that started this one can read the warnings and
	re-raise the exception (:meth:`ThreadSupervisor.ReRaise`).
	"""
	_supervisor:       Nullable[ThreadSupervisor]                 #: Supervisor collecting warnings and exceptions of all threads.
	_exceptionHandler: Nullable[Callable[[BaseException], bool]]  #: Handler called for an exception escaping the thread.
	_finallyHandler:   Nullable[Callable[[], None]]               #: Handler called when the thread ends, in either case.

	__slots__ = ("_supervisor", "_exceptionHandler", "_finallyHandler")

	def __init__(
		self,
		warnings:         Nullable[list[BaseException]] =             None,
		handler:          Nullable[Callable[[BaseException], bool]] = None,
		/,
		supervisor:       Nullable[ThreadSupervisor] =              None,
		exceptionHandler: Nullable[Callable[[BaseException], bool]] = None,
		finallyHandler:   Nullable[Callable[[], None]] =              None
	) -> None:
		"""
		Initializes a warning collector.

		:param warnings:         Optional, reference to a list of warnings, which can be modified (appended) by this warning
		                         collector. If ``None``, an internal list is created and can be referenced by the
		                         collector's instance.
		:param handler:          Optional, handler function, which is called with each collected warning and decides, if
		                         it's escalated. If it returns ``True``, :meth:`Raise` raises an
		                         :exc:`EscalatedWarningError`, whose cause is the warning.
		:param supervisor:       Optional, thread supervisor. On leaving the context, the collected warnings and an
		                         exception leaving the block are handed to it, so the thread that started this one can
		                         reraise them. Without a supervisor, an exception leaves the block unchanged.
		:param exceptionHandler: Optional, handler function, called with an exception leaving the block when a supervisor is
		                         set. Its result decides whether the exception is suppressed.
		:param finallyHandler:   Optional, function called when the context is left, whether or not an exception left it.
		:raises TypeError:       If optional parameter 'warnings' is not of type list.
		:raises TypeError:       If optional parameter 'handler' is not a callable.
		"""
		super().__init__(warnings, handler)

		self._supervisor =       supervisor
		self._exceptionHandler = exceptionHandler
		self._finallyHandler =   finallyHandler

	def __enter__(self) -> Self:
		"""
		Enter the context and make this warning collector the current one of its thread.

		:returns:                                The warning collector instance.
		:raises SupervisedWarningCollectorError: If this collector is not the top-most warning collector of its thread.
		"""
		global _threadLocalData

		if hasattr(_threadLocalData, "warningCollector") and _threadLocalData.warningCollector is not None:
			raise SupervisedWarningCollectorError("This warning collector is not the top-most warning collector within the current thread.")

		_threadLocalData.warningCollector = self

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and hand the collected warnings and a raised exception to the supervisor.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``True`` to suppress a raised exception, if a supervisor is set; the exception handler's result
		                 instead, if it handled a raised exception; ``None`` without a supervisor.
		"""
		global _threadLocalData

		_threadLocalData.warningCollector = None

		if self._supervisor is not None:
			result = True
			if len(self._warnings) > 0:
				self._supervisor.AddWarnings(current_thread().name, self._warnings)

			if exc_val is not None:
				self._supervisor.AddException(current_thread().name, exc_val)

				if self._exceptionHandler is not None:
					result = self._exceptionHandler(exc_val)
		else:
			result = None

		if self._finallyHandler is not None:
			self._finallyHandler()

		return result


@export
class SupervisedThreadError(ExceptionBase):
	"""
	This exception is raised by :meth:`ThreadSupervisor.ReRaise`, if a supervised thread failed with an exception.

	A :class:`SupervisedWarningCollector` hands the exception leaving its thread to the :class:`ThreadSupervisor`; it
	becomes this exception's cause, and :attr:`~SupervisedThreadError.ThreadName` names the thread.
	"""
	_threadName: str  #: Name of the thread the exception was raised in.

	def __init__(
		self,
		message: str,
		/,
		*,
		threadName: str,
		cause: Nullable[BaseException] = None
	) -> None:
		"""
		Initializes the exception with the name of the thread that failed.

		:param message:    The exception's message.
		:param threadName: Name of the thread that raised the collected exception.
		:param cause:      Optional, the exception collected from that thread.
		"""
		super().__init__(message)
		self._threadName = threadName
		self.__cause__ = cause

	@readonly
	def ThreadName(self) -> str:
		"""
		Read-only property to access the name of the thread that raised the exception (:attr:`_threadName`).

		:returns: Name of the thread.
		"""
		return self._threadName


@export
class ThreadSupervisor:
	"""
	Thread-safe collector of exceptions and warnings raised in worker threads for surfacing on another thread.

	This thread supervisor should be used in combination with :class:`SupervisedWarningCollector` to accumulate
	exceptions (:class:`BaseException`) and warnings (:class:`CriticalWarning` or :class:`Warning`).

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
	       def exceptionHandler(ex: BaseException) -> bool:
	         self._stopEvent.set()
	         return True

	       def finallyHandler() -> None:
	         ...  # some finally code

	       with SupervisedWarningCollector(
	         supervisor=self._threadSupervisor,
	         exceptionHandler=exceptionHandler,
	         finallyHandler=finallyHandler
	       ) as warnings:
	         ...  # thread body

	.. code-block:: python

	   def RunVivadoPipeline(
	     self,
	   ) -> list[AnyWarning]:
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
	_exceptions: list[tuple[str, BaseException]]  #: Exceptions of all supervised threads, as (thread name, exception).
	_warnings:   list[tuple[str, AnyWarning]]     #: Warnings of all supervised threads, as (thread name, warning).

	__slots__ = ("_lock", "_exceptions", "_warnings")

	def __init__(self) -> None:
		"""
		Initialize a thread supervisor with empty lists of exceptions and warnings.
		"""
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
	def Warnings(self) -> list[AnyWarning]:
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

	def AddWarnings(self, threadName: str, warnings: list[AnyWarning]) -> None:
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

		A single exception is re-raised as itself - wrapped in a :exc:`SupervisedThreadError` naming its thread,
		unless ``unwrapped`` is set. Several exceptions are raised as an :exc:`ExceptionGroup`, so none of them is lost.

		:param unwrapped:              Optional, if ``True``, a single exception is raised as it was, without naming its
		                               thread.
		:raises SupervisedThreadError: If exactly one thread failed.
		:raises ExceptionGroup:        If more than one thread failed.
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
				raise SupervisedThreadError(f"Thread '{threadName}' failed.", threadName=threadName) from ex

		elif unwrapped:
			raise ExceptionGroup(
				"Multiple threads failed.",
				[ex for _, ex in exceptions]
			)
		else:
			raise ExceptionGroup(
				"Multiple threads failed.",
				[
					SupervisedThreadError(f"Thread '{threadName}' failed.", threadName=threadName, cause=ex)
					for threadName, ex in exceptions
				]
			)
