# ==================================================================================================================== #
#              _____           _ _             _____ _                            _                                    #
#   _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _(_)_ __ ___   ___  ___  _   _| |_                                  #
#  | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | '_ ` _ \ / _ \/ _ \| | | | __|                                 #
#  | |_) | |_| || | (_) | (_) | | | | | | (_| |_| | | | | | | | |  __/ (_) | |_| | |_                                  #
#  | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_| |_|_| |_| |_|\___|\___/ \__,_|\__|                                 #
#  |_|    |___/                          |___/                                                                         #
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
"""
A cooperative timeout for loops and blocking calls, valid for a ``with`` block.

.. hint::

   See :ref:`high-level help <COMMON/Timeout>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Stopwatch`
      |rarr| Measuring how long something took, instead of limiting it.
   :mod:`pyTooling.Warning`
      |rarr| The warning collector, which is made current for a ``with`` block the same way.
"""
from __future__            import annotations

from threading             import local
from time                  import monotonic
from types                 import TracebackType
from typing                import Optional as Nullable, Self

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.MetaClasses import ExtendedType


_threadLocalData = local()
"""A reference to the thread local data holding the current :class:`Timeout` of a thread."""


@export
class TimeoutExpiredError(ToolingException, TimeoutError):
	"""
	The exception is raised by a loop or an operation, which aborts itself because its :class:`Timeout` expired.

	It is a :exc:`TimeoutError` as well (and so an :exc:`OSError`), because the operation timed out; catching
	:exc:`~pyTooling.Exceptions.ToolingException` still catches it.
	"""

	_seconds: Nullable[float]  #: The configured timeout in seconds.

	def __init__(self, message: str, /, *, seconds: Nullable[float] = None) -> None:
		"""
		Initializes the exception with the timeout, which expired.

		:param message: The exception's message.
		:param seconds: Optional, the configured timeout in seconds.
		"""
		super().__init__(message)
		self._seconds = seconds

	@readonly
	def Seconds(self) -> Nullable[float]:
		"""
		Read-only property to access the configured timeout in seconds (:attr:`_seconds`).

		:returns: The timeout in seconds, or ``None`` if it wasn't recorded.
		"""
		return self._seconds


@export
class Timeout(metaclass=ExtendedType, slots=True):
	"""
	A timeout, which is current for the thread while its ``with`` block runs.

	Entering the context makes the timeout the current one of the calling thread; the previous current timeout becomes
	its parent, and leaving the context restores it - as a :class:`~pyTooling.Warning.WarningCollector` is made current.
	Code inside the block, how deep down the call hierarchy it may be, asks the classmethods :meth:`Remaining` and
	:meth:`IsExpired` without the timeout being passed along.

	A nested timeout can only shorten the time left, never extend it: its deadline is the earlier of its own and the
	parent's.

	.. code-block:: Python

	   with Timeout(20.0):
	     for package in packages:
	       if Timeout.IsExpired():
	         raise TimeoutExpiredError("Scanning the dependencies took longer than 20 seconds.", seconds=20.0)

	       response = session.get(package.URL, timeout=Timeout.Remaining())

	.. important::

	   The timeout is **cooperative**. Python can't stop a running thread from outside, so nothing interrupts the code in
	   the ``with`` block when the deadline passes. A timeout takes effect where the code checks it - a loop aborting
	   itself when :meth:`IsExpired` turns ``True`` - and where the time left is handed to a blocking call as its own
	   timeout: ``requests`` and ``aiohttp`` requests, :meth:`threading.Thread.join`,
	   :meth:`concurrent.futures.Future.result`, :func:`asyncio.timeout` or :func:`asyncio.wait_for`.

	.. rubric:: Threads and tasks

	The current timeout is stored per thread. :mod:`asyncio` tasks run in the thread of their event loop, so they see
	the timeout of that thread. A new thread starts without a current timeout; hand the time left over to it - either
	as the timeout of waiting for it (``thread.join(timeout=Timeout.Remaining())``), or by entering a timeout in the
	thread itself (``with Timeout(remaining):``, with ``remaining`` read before starting the thread).
	"""

	_seconds:  float              #: The timeout in seconds.
	_deadline: Nullable[float]    #: Effective deadline (:func:`time.monotonic`) while the context is entered.
	_parent:   Nullable[Timeout]  #: The timeout, which was current when this one was entered.

	def __init__(self, seconds: float) -> None:
		"""
		Initializes a timeout of the given number of seconds.

		The time starts running when the context is entered.

		:param seconds:     The timeout in seconds.
		:raises ValueError: If parameter 'seconds' is ``None``.
		:raises TypeError:  If parameter 'seconds' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'seconds' is not greater than zero.
		"""
		if seconds is None:
			raise ValueError("Parameter 'seconds' is None.")
		elif isinstance(seconds, bool) or not isinstance(seconds, (float, int)):
			ex = TypeError("Parameter 'seconds' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(seconds)}'.")
			raise ex
		elif not seconds > 0:
			ex = ValueError("Parameter 'seconds' is not greater than zero.")
			ex.add_note(f"Got value '{seconds}'.")
			raise ex

		self._seconds =  float(seconds)
		self._deadline = None
		self._parent =   None

	@readonly
	def Seconds(self) -> float:
		"""
		Read-only property to access the timeout in seconds (:attr:`_seconds`).

		:returns: The timeout in seconds.
		"""
		return self._seconds

	@readonly
	def Deadline(self) -> Nullable[float]:
		"""
		Read-only property to access the effective deadline (:attr:`_deadline`).

		The deadline is a :func:`time.monotonic` value: the earlier of this timeout's own deadline and its parent's.

		:returns: The deadline while the context is entered, otherwise ``None``.
		"""
		return self._deadline

	@readonly
	def Parent(self) -> Nullable[Timeout]:
		"""
		Read-only property to access the timeout, which was current when this one was entered (:attr:`_parent`).

		:returns: The parent timeout, or ``None``.
		"""
		return self._parent

	@classmethod
	def Remaining(cls) -> Nullable[float]:
		"""
		Return the seconds left of the current timeout of the calling thread.

		:returns: The seconds left, ``0.0`` when the timeout expired; ``None`` if no timeout is current.
		"""
		if (timeout := getattr(_threadLocalData, "timeout", None)) is None:
			return None

		return max(0.0, timeout._deadline - monotonic())

	@classmethod
	def IsExpired(cls) -> bool:
		"""
		Return if the current timeout of the calling thread has expired.

		:returns: ``True``, if the current timeout expired; ``False`` if it didn't, or no timeout is current.
		"""
		if (timeout := getattr(_threadLocalData, "timeout", None)) is None:
			return False

		return monotonic() >= timeout._deadline

	def __enter__(self) -> Self:
		"""
		Enter the context, start the timeout and make it the current one of the calling thread.

		The previous current timeout becomes its parent. The deadline is the earlier of this timeout's own and the
		parent's.

		:returns: The timeout instance.
		"""
		self._parent = getattr(_threadLocalData, "timeout", None)

		deadline = monotonic() + self._seconds
		if self._parent is not None and self._parent._deadline < deadline:
			deadline = self._parent._deadline

		self._deadline =          deadline
		_threadLocalData.timeout = self

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and make the parent timeout the current one again.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``False``, so an exception raised in the context propagates.
		"""
		_threadLocalData.timeout = self._parent
		self._deadline =          None

		return False
