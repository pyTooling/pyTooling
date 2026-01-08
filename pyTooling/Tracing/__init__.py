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


__all__ = ["_threadLocalData"]

_threadLocalData = local()
"""A reference to the thread local data needed by the pyTooling.Tracing classes."""


@export
class TracingException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Tracing`."""


@export
class Event(metaclass=ExtendedType, slots=True):
	"""
	Represents a named event within a timespan (:class:`Span`) used in a software execution trace.

	It may contain arbitrary attributes (key-value pairs).
	"""
	_name:      str                 #: Name of the event.
	_parent:    Nullable["Span"]    #: Reference to the parent span.
	_time:      Nullable[datetime]  #: Timestamp of the event.
	_dict:      Dict[str, Any]			#: Dictionary of associated attributes.

	def __init__(self, name: str, time: Nullable[datetime] = None, parent: Nullable["Span"] = None) -> None:
		"""
		Initializes a named event.

		:param name:   The name of the event.
		:param time:   The optional time when the event happened.
		:param parent: Reference to the parent span.
		"""
		if isinstance(name, str):
			if name == "":
				raise ValueError(f"Parameter 'name' is empty.")

			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		if time is None:
			self._time = None
		elif isinstance(time, datetime):
			self._time = time
		else:
			ex = TypeError("Parameter 'time' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(time)}'.")
			raise ex

		if parent is None:
			self._parent = None
		elif isinstance(parent, Span):
			self._parent = parent
			parent._events.append(self)
		else:
			ex = TypeError("Parameter 'parent' is not of type 'Span'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._dict =   {}

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the event's name.

		:returns: Name of the event.
		"""
		return self._name

	@readonly
	def Time(self) -> datetime:
		"""
		Read-only property to access the event's timestamp.

		:returns: Timestamp of the event.
		"""
		return self._time

	@readonly
	def Parent(self) -> Nullable["Span"]:
		"""
		Read-only property to access the event's parent span.

		:returns: Parent span.
		"""
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

	def __iter__(self) -> Iterator[Tuple[str, Any]]:
		"""
		Returns an iterator to iterate all associated attributes of this event as :pycode:`(key, value)` tuples.

		:returns: Iterator to iterate all attributes.
		"""
		return iter(self._dict.items())

	def __len__(self) -> int:
		"""
		Returns the number of attached attributes (key-value-pairs) on this event.

		:returns: Number of attached attributes.
		"""
		return len(self._dict)

	def __str__(self) -> str:
		"""
		Return a string representation of the event.

		:returns: The event's name.
		"""
		return self._name


@export
class Span(metaclass=ExtendedType, slots=True):
	"""
	Represents a timespan (span) within another timespan or trace.

	It may contain sub-spans, events and arbitrary attributes (key-value pairs).
	"""
	_name:      str                 #: Name of the timespan
	_parent:    Nullable["Span"]    #: Reference to the parent span (or trace).

	_beginTime: Nullable[datetime]  #: Timestamp when the timespan begins.
	_endTime:   Nullable[datetime]  #: Timestamp when the timespan ends.
	_startTime: Nullable[int]
	_stopTime:  Nullable[int]
	_totalTime: Nullable[int]       #: Duration of this timespan in ns.

	_spans:     List["Span"]        #: Sub-timespans
	_events:    List[Event]         #: Events happened within this timespan
	_dict:      Dict[str, Any]      #: Dictionary of associated attributes.

	def __init__(self, name: str, parent: Nullable["Span"] = None) -> None:
		"""
		Initializes a timespan as part of a software execution trace.

		:param name:   Name of the timespan.
		:param parent: Reference to a parent span or trace.
		"""
		if isinstance(name, str):
			if name == "":
				raise ValueError(f"Parameter 'name' is empty.")

			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if parent is None:
			self._parent = None
		elif isinstance(parent, Span):
			self._parent = parent
			parent._spans.append(self)
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
		"""
		Read-only property to access the timespan's name.

		:returns: Name of the timespan.
		"""
		return self._name

	@readonly
	def Parent(self) -> Nullable["Span"]:
		"""
		Read-only property to access the span's parent span or trace.

		:returns: Parent span.
		"""
		return self._parent

	def _AddSpan(self, span: "Span") -> Self:
		self._spans.append(span)
		span._parent = self

		return span

	@readonly
	def HasSubSpans(self) -> bool:
		"""
		Check if this timespan contains nested sub-spans.

		:returns: ``True``, if the span has nested spans.
		"""
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
		"""
		Returns an iterator to iterate all nested sub-spans.

		:returns: Iterator to iterate all sub-spans.
		"""
		return iter(self._spans)

	@readonly
	def HasEvents(self) -> bool:
		"""
		Check if this timespan contains events.

		:returns: ``True``, if the span has events.
		"""
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
		"""
		Returns an iterator to iterate all embedded events.

		:returns: Iterator to iterate all events.
		"""
		return iter(self._events)

	@readonly
	def StartTime(self) -> Nullable[datetime]:
		"""
		Read-only property accessing the absolute time when the span was started.

		:return: The time when the span was entered, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property accessing the absolute time when the span was stopped.

		:return: The time when the span was exited, otherwise None.
		"""
		return self._endTime

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property accessing the duration from start operation to stop operation.

		If the span is not yet stopped, the duration from start to now is returned.

		:return:                  Duration since span was started in seconds.
		:raises TracingException: When span was never started.
		"""
		if self._startTime is None:
			raise TracingException(f"{self.__class__.__name__} was never started.")

		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e9

	@classmethod
	def CurrentSpan(cls) -> "Span":
		"""
		Class-method to return the currently active timespan (span) or ``None``.

		:returns: Currently active span or ``None``.
		"""
		global _threadLocalData

		try:
			currentSpan = _threadLocalData.currentSpan
		except AttributeError:
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
		"""
		Returns an iterator to iterate all associated attributes of this timespan as :pycode:`(key, value)` tuples.

		:returns: Iterator to iterate all attributes.
		"""
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
		"""
		Return a string representation of the timespan.

		:returns: The span's name.
		"""
		return self._name


@export
class Trace(Span):
	"""
	Represents a software execution trace made up of timespans (:class:`Span`).

	The trace is the top-most element in a tree of timespans. All timespans share the same *TraceID*, thus even in a
	distributed software execution, timespans can be aggregated with delay in a centralized database and the flow of
	execution can be reassembled by grouping all timespans with same *TraceID*. Execution order can be derived from
	timestamps and parallel execution is represented by overlapping timespans sharing the same parent *SpanID*. Thus, the
	tree structure can be reassembled by inspecting the parent *SpanID* relations within the same *TraceID*.

	A trace may contain sub-spans, events and arbitrary attributes (key-value pairs).
	"""

	def __init__(self, name: str) -> None:
		"""
		Initializes a software execution trace.

		:param name:   Name of the trace.
		"""
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
		"""
		Class-method to return the currently active trace or ``None``.

		:returns: Currently active trace or ``None``.
		"""
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
