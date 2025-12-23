# ==================================================================================================================== #
#             _____           _ _             _____               _                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ __ _  ___(_)_ __   __ _                                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _` |/ __| | '_ \ / _` |                                       #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | | (_| | (__| | | | | (_| |                                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \__,_|\___|_|_| |_|\__, |                                       #
# |_|    |___/                          |___/                             |___/                                        #
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
"""Tools for software execution tracing."""
from datetime  import datetime
from time      import perf_counter_ns
from threading import local
from types     import TracebackType
from typing import Optional as Nullable, List, Iterator, Type, Self, Iterable, Dict, Any, Tuple


try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Tracing] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType
		from Exceptions          import ToolingException
		from Common              import getFullyQualifiedName
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Tracing] Could not import directly!")
		raise ex


_threadLocalData = local()


@export
class TracingException(ToolingException):
	"""This exception is caused by wrong usage of the stopwatch."""


@export
class Event(metaclass=ExtendedType, slots=True):
	_name:      str
	_parent:    Nullable["Span"]
	_time:      Nullable[datetime]
	_dict:      Dict[str, Any]

	def __init__(self, name: str, parent: Nullable["Span"] = None) -> None:
		if isinstance(name, str):
			self._name =   name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if parent is None:
			self._parent = None
		elif isinstance(parent, Span):
			self._parent = parent
			parent._events[name] = self
		else:
			ex = TypeError("Parameter 'parent' is not of type 'Span'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._dict =   {}

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Parent(self) -> Nullable["Span"]:
		return self._parent

	def __getitem__(self, key: str) -> Any:
		"""
		Read an event's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: str, value: Any) -> None:
		"""
		Create or update an event's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key:   The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: str) -> None:
		"""
		Remove an entry from event's attached attributes (key-value-pairs) by key.

		:param key:       The key to remove.
		:raises KeyError: If key doesn't exist in the event's attributes.
		"""
		del self._dict[key]

	def __contains__(self, key: str) -> bool:
		"""
		Checks if the key is an attached attribute (key-value-pairs) on this event.

		:param key: The key to check.
		:returns:   ``True``, if the key is an attached attribute.
		"""
		return key in self._dict

	def __len__(self) -> int:
		"""
		Returns the number of attached attributes (key-value-pairs) on this event.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	def __str__(self) -> str:
		return self._name


@export
class Span(metaclass=ExtendedType, slots=True):
	_name:      str
	_parent:    Nullable["Span"]

	_beginTime: Nullable[datetime]
	_endTime:   Nullable[datetime]
	_startTime: Nullable[int]
	_stopTime:  Nullable[int]
	_totalTime: Nullable[int]

	_spans:     List["Span"]
	_events:    List[Event]
	_dict:      Dict[str, Any]

	def __init__(self, name: str, parent: Nullable["Span"] = None) -> None:
		if isinstance(name, str):
			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if parent is None:
			self._parent = None
		elif isinstance(parent, Span):
			self._parent = parent
			parent._events[name] = self
		else:
			ex = TypeError("Parameter 'parent' is not of type 'Span'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._beginTime = None
		self._startTime = None
		self._endTime =   None
		self._stopTime =  None
		self._totalTime = None

		self._spans =     []
		self._events =    []
		self._dict =      {}

	@readonly
	def Name(self) -> str:
		return self._name

	@readonly
	def Parent(self) -> Nullable["Span"]:
		return self._parent

	def _AddSpan(self, span: "Span") -> Self:
		self._spans.append(span)
		span._parent = self

		return span

	@readonly
	def HasSubSpans(self) -> bool:
		return len(self._spans) > 0

	@readonly
	def SubSpanCount(self) -> int:
		"""
		Return the number of sub-spans within this span.

		:return: Number of nested spans.
		"""
		return len(self._spans)

	# iterate subspans with optional predicate
	def IterateSubSpans(self) -> Iterator["Span"]:
		return iter(self._spans)

	@readonly
	def HasEvents(self) -> bool:
		return len(self._events) > 0

	@readonly
	def EventCount(self) -> int:
		"""
		Return the number of events within this span.

		:return: Number of events.
		"""
		return len(self._events)

	# iterate events with optional predicate
	def IterateEvents(self) -> Iterator[Event]:
		return iter(self._events)

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the span was started.

		:return: The time when the span was entered, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property returning the absolute time when the span was stopped.

		:return: The time when the span was exited, otherwise None.
		"""
		return self._endTime

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property returning the duration from start operation to stop operation.

		If the stopwatch is not yet stopped, the duration from start to now is returned.

		:return: Duration since stopwatch was started in seconds. If the stopwatch was never started, the return value will
		         be 0.0.
		"""
		if self._startTime is None:
			raise TracingException(f"{self.__class__.__name__} was never started.")

		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e9

	@classmethod
	def CurrentSpan(cls) -> "Span":
		global _threadLocalData

		try:
			currentSpan = _threadLocalData.currentSpan
		except AttributeError as ex:
			currentSpan = None

		return currentSpan

	def __enter__(self) -> Self:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__enter__(...)`` method.

		A span will be started.

		:return: The span itself.
		"""
		global _threadLocalData

		try:
			currentSpan =  _threadLocalData.currentSpan
		except AttributeError:
			ex = TracingException("Can't setup span. No active trace.")
			ex.add_note("Use with-statement using 'Trace()' to setup software execution tracing.")
			raise ex

		_threadLocalData.currentSpan = currentSpan._AddSpan(self)

		self._beginTime = datetime.now()
		self._startTime = perf_counter_ns()

		return self

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Implementation of the :ref:`context manager protocol's <context-managers>` ``__exit__(...)`` method.

		An active span will be stopped.

		Exit the context and ......

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		:returns:        ``None``
		"""
		global _threadLocalData

		self._stopTime =  perf_counter_ns()
		self._endTime =   datetime.now()
		self._totalTime = self._stopTime - self._startTime

		currentSpan = _threadLocalData.currentSpan
		_threadLocalData.currentSpan = currentSpan._parent

	def __getitem__(self, key: str) -> Any:
		"""
		Read an event's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: str, value: Any) -> None:
		"""
		Create or update an event's attached attributes (key-value-pairs) by key.

		If a key doesn't exist yet, a new key-value-pair is created.

		:param key:   The key to create or update.
		:param value: The value to associate to the given key.
		"""
		self._dict[key] = value

	def __delitem__(self, key: str) -> None:
		"""
		Remove an entry from event's attached attributes (key-value-pairs) by key.

		:param key:       The key to remove.
		:raises KeyError: If key doesn't exist in the event's attributes.
		"""
		del self._dict[key]

	def __contains__(self, key: str) -> bool:
		"""
		Checks if the key is an attached attribute (key-value-pairs) on this event.

		:param key: The key to check.
		:returns:   ``True``, if the key is an attached attribute.
		"""
		return key in self._dict

	def __iter__(self) -> Iterator[Tuple[str, Any]]:
		return iter(self._dict.items())

	def __len__(self) -> int:
		"""
		Returns the number of attached attributes (key-value-pairs) on this event.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	def Format(self, indent: int = 1, columnSize: int = 25) -> Iterable[str]:
		result = []
		result.append(f"{'  ' * indent}🕑{self._name:<{columnSize - 2 * indent}} {self._totalTime/1e6:8.3f} ms")
		for span in self._spans:
			result.extend(span.Format(indent + 1, columnSize))

		return result

	def __repr__(self) -> str:
		return f"{self._name} -> {self._parent!r}"

	def __str__(self) -> str:
		return self._name


@export
class Trace(Span):
	def __init__(self, name: str) -> None:
		super().__init__(name)

	def __enter__(self) -> Self:
		global _threadLocalData

		# TODO: check if a trace is already setup
		# try:
		# 	currentTrace = _threadLocalData.currentTrace
		# except AttributeError:
		# 	pass

		_threadLocalData.currentTrace = self
		_threadLocalData.currentSpan = self

		self._beginTime = datetime.now()
		self._startTime = perf_counter_ns()

		return self

	def __exit__(
		self,
		exc_type: Nullable[Type[BaseException]] = None,
		exc_val:  Nullable[BaseException] = None,
		exc_tb:   Nullable[TracebackType] = None
	) -> Nullable[bool]:
		"""
		Exit the context and ......

		:param exc_type: Exception type
		:param exc_val:  Exception instance
		:param exc_tb:   Exception's traceback.
		:returns:        ``None``
		"""
		global _threadLocalData

		self._stopTime =  perf_counter_ns()
		self._endTime =   datetime.now()
		self._totalTime = self._stopTime - self._startTime

		del _threadLocalData.currentTrace
		del _threadLocalData.currentSpan

		return None

	@classmethod
	def CurrentTrace(cls) -> "Trace":
		try:
			currentTrace = _threadLocalData.currentTrace
		except AttributeError:
			currentTrace = None

		return currentTrace

	def Format(self, indent: int = 0, columnSize: int = 25) -> Iterable[str]:
		result = []
		result.append(f"{'  ' * indent}Software Execution Trace: {self._totalTime/1e6:8.3f} ms")
		result.append(f"{'  ' * indent}📉{self._name:<{columnSize - 2}} {self._totalTime/1e6:8.3f} ms")
		for span in self._spans:
			result.extend(span.Format(indent + 1, columnSize - 2))

		return result
