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
"""
Tools for software execution tracing.

.. seealso::

   :mod:`pyTooling.Stopwatch`
      |rarr| A single measurement instead of nested timespans.
   :mod:`pyTooling.Tree`
      |rarr| The tree data structure spans and their sub-spans form.

.. hint::

   See :ref:`high-level help <TRACING>` for explanations and usage examples.
"""
from __future__            import annotations

from base64                import b64encode
from datetime              import datetime
from json                  import dumps as json_dumps
from pathlib               import Path
from secrets               import randbits
from time                  import perf_counter_ns
from threading             import local
from types                 import TracebackType
from typing                import Optional as Nullable, Iterator, Self, Iterable, TypedDict, Union

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Exceptions  import ToolingException
from pyTooling.Common      import __version__, getFullyQualifiedName


__all__ = ["_threadLocalData", "OTLP_SCOPE_NAME"]

OTLP_SCOPE_NAME = "pyTooling.Tracing"
"""The instrumentation scope every exported span is reported under."""

_threadLocalData = local()
"""A reference to the thread local data needed by the pyTooling.Tracing classes."""

AttributeValue = Union[
	bool, int, float, str, bytes,
	list["AttributeValue"], tuple["AttributeValue", ...], dict[str, "AttributeValue"]
]
"""
A value that can be attached to a trace, a span or an event as an attribute.

These are the types OTLP's ``AnyValue`` can carry, and nothing else - a value of any other type is rejected rather
than stringified, because a silent ``str(value)`` puts a Python ``repr`` into a document a backend then indexes.
"""

_MAXIMUM_IDENTIFIER_ATTEMPTS = 4
"""Number of attempts to draw a non-zero random identifier before giving up."""


@export
class TracingError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Tracing`."""


@export
class OTLPArrayValue(TypedDict):
	"""OTLP's ``ArrayValue``: a list of values, as it is nested inside an :class:`OTLPAnyValue`."""

	values: list[OTLPAnyValue]  #: The elements of the array.


@export
class OTLPKeyValueList(TypedDict):
	"""OTLP's ``KeyValueList``: a mapping of values, as it is nested inside an :class:`OTLPAnyValue`."""

	values: list[OTLPAttribute]  #: The entries of the mapping.


@export
class OTLPAnyValue(TypedDict, total=False):
	"""
	OTLP's ``AnyValue``: a value of any supported type, carried in a mapping of exactly one key.

	The key names the type of the value. A 64-bit integer travels as a decimal **string**, because a JSON number can't
	carry 64 bits exactly. That is proto3's JSON mapping rather than a quirk of OTLP.
	"""

	boolValue:   bool              #: A boolean value.
	intValue:    str               #: A 64-bit integer, encoded as a decimal string.
	doubleValue: float             #: A floating-point value.
	stringValue: str               #: A string value.
	bytesValue:  str               #: A byte string, encoded as base64 - this field is ``bytes`` in proto3.
	arrayValue:  OTLPArrayValue    #: A list of values.
	kvlistValue: OTLPKeyValueList  #: A mapping of values.


@export
class OTLPAttribute(TypedDict):
	"""OTLP's ``KeyValue``: a single attribute of a resource, a span or an event."""

	key:   str           #: Name of the attribute.
	value: OTLPAnyValue  #: Value of the attribute.


@export
class OTLPEvent(TypedDict, total=False):
	"""OTLP's ``Span.Event``: a named point in time within a span."""

	name:         str                  #: Name of the event.
	timeUnixNano: str                  #: Time of the event in nanoseconds since the Unix epoch, as a decimal string.
	attributes:   list[OTLPAttribute]  #: Attributes attached to the event.


@export
class OTLPSpan(TypedDict, total=False):
	"""
	OTLP's ``Span``: a single timespan of a trace.

	OTLP doesn't nest spans, so the enclosing span is referenced by :attr:`parentSpanId` instead of containing this one.
	"""

	traceId:           str                  #: Identifier shared by every span of the trace, as 32 hex digits.
	spanId:            str                  #: Identifier of this span, as 16 hex digits.
	parentSpanId:      str                  #: Identifier of the enclosing span, absent for the trace's own span.
	name:              str                  #: Name of the span.
	kind:              int                  #: Kind of the span - always ``1`` (``SPAN_KIND_INTERNAL``) here.
	startTimeUnixNano: str                  #: Start in nanoseconds since the Unix epoch, as a decimal string.
	endTimeUnixNano:   str                  #: End in nanoseconds since the Unix epoch, as a decimal string.
	attributes:        list[OTLPAttribute]  #: Attributes attached to the span.
	events:            list[OTLPEvent]      #: Events that happened within the span.


@export
class OTLPScope(TypedDict):
	"""OTLP's ``InstrumentationScope``: the library the spans were produced by."""

	name:    str  #: Name of the instrumentation scope.
	version: str  #: Version of the instrumentation scope.


@export
class OTLPScopeSpans(TypedDict):
	"""OTLP's ``ScopeSpans``: the spans produced by one instrumentation scope."""

	scope: OTLPScope       #: The instrumentation scope the spans were produced by.
	spans: list[OTLPSpan]  #: The spans, flattened.


@export
class OTLPResource(TypedDict):
	"""OTLP's ``Resource``: the entity the spans were produced by."""

	attributes: list[OTLPAttribute]  #: Attributes describing the resource, e.g. ``service.name``.


@export
class OTLPResourceSpans(TypedDict):
	"""OTLP's ``ResourceSpans``: the spans produced by one resource."""

	resource:   OTLPResource          #: The resource the spans were produced by.
	scopeSpans: list[OTLPScopeSpans]  #: The spans, grouped by instrumentation scope.


@export
class OTLPDocument(TypedDict):
	"""OTLP's ``TracesData``: the root of an OTLP/JSON document."""

	resourceSpans: list[OTLPResourceSpans]  #: The spans, grouped by resource.


def _toAttributeValue(value: AttributeValue) -> OTLPAnyValue:
	"""
	Wrap a Python value in OTLP's ``AnyValue`` representation.

	Supported are :class:`bool`, :class:`int`, :class:`float`, :class:`str`, :class:`bytes`, and a :class:`list`,
	:class:`tuple` or :class:`dict` of these - see :data:`AttributeValue`.

	:param value:         The value to wrap.
	:returns:             The value, wrapped in the one-key mapping OTLP expects for its type.
	:raises TracingError: If the value is of a type OTLP's ``AnyValue`` can't carry.
	"""
	# a bool is an int in Python, so it has to be recognized first
	if isinstance(value, bool):
		return {"boolValue": value}
	elif isinstance(value, int):
		return {"intValue": str(value)}
	elif isinstance(value, float):
		return {"doubleValue": value}
	elif isinstance(value, str):
		return {"stringValue": value}
	elif isinstance(value, (bytes, bytearray)):
		return {"bytesValue": b64encode(value).decode("ascii")}
	elif isinstance(value, (list, tuple)):
		return {"arrayValue": {"values": [_toAttributeValue(element) for element in value]}}
	elif isinstance(value, dict):
		return {"kvlistValue": {"values": _toAttributes(value.items())}}

	ex = TracingError(f"Attribute value of type '{getFullyQualifiedName(value)}' can't be represented in OTLP.")
	ex.add_note("Supported are: bool, int, float, str, bytes, and a list, tuple or dict of these.")
	raise ex


def _toAttributes(attributes: Iterable[tuple[str, AttributeValue]]) -> list[OTLPAttribute]:
	"""
	Convert key-value pairs to OTLP's list of attributes.

	:param attributes:    The key-value pairs to convert.
	:returns:             One ``{"key": ..., "value": ...}`` mapping per pair.
	:raises TracingError: If a value is of a type OTLP's ``AnyValue`` can't carry.
	"""
	return [{"key": key, "value": _toAttributeValue(value)} for key, value in attributes]


def _newIdentifier(bits: int) -> str:
	"""
	Generate a random trace or span identifier.

	OTLP/JSON encodes both as **hex** rather than base64, which is where it deviates from proto3's JSON mapping. An
	all-zero identifier is invalid, so it is drawn again in that case.

	:param bits:          Width of the identifier: 128 for a trace, 64 for a span.
	:returns:             The identifier as a lower-case hex string.
	:raises TracingError: If no non-zero identifier was drawn within :data:`_MAXIMUM_IDENTIFIER_ATTEMPTS` attempts.
	"""
	for _ in range(_MAXIMUM_IDENTIFIER_ATTEMPTS):
		if (identifier := randbits(bits)) != 0:
			return f"{identifier:0{bits // 4}x}"
	else:
		ex = TracingError(f"Couldn't draw a non-zero {bits}-bit random identifier.")
		ex.add_note(f"Tried {_MAXIMUM_IDENTIFIER_ATTEMPTS} times.")
		raise ex


@export
class Event(metaclass=ExtendedType, slots=True):
	"""
	Represents a named event within a timespan (:class:`Span`) used in a software execution trace.

	It may contain arbitrary attributes (key-value pairs).
	"""
	_name:      str                 #: Name of the event.
	_parent:    Nullable[Span]      #: Reference to the parent span.
	_time:      datetime            #: Timestamp of the event.
	_dict:      dict[str, AttributeValue]  #: Dictionary of associated attributes.

	def __init__(self, name: str, time: Nullable[datetime] = None, parent: Nullable[Span] = None) -> None:
		"""
		Initializes a named event.

		:param name:        The name of the event.
		:param time:        Optional, time when the event happened. Default: the current system time.
		:param parent:      Optional, reference to the parent span.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Span`.
		"""
		if isinstance(name, str):
			if name == "":
				raise ValueError("Parameter 'name' is empty.")

			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		if time is None:
			self._time = datetime.now()
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
	def Parent(self) -> Nullable[Span]:
		"""
		Read-only property to access the event's parent span.

		:returns: Parent span.
		"""
		return self._parent

	def __getitem__(self, key: str) -> AttributeValue:
		"""
		Read an event's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: str, value: AttributeValue) -> None:
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

	def __iter__(self) -> Iterator[tuple[str, AttributeValue]]:
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

	def _ToOTLPJSON(self) -> OTLPEvent:
		"""
		Convert this event to its **OTLP/JSON** representation.

		:returns:             The event as an OTLP mapping.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		converted: OTLPEvent = {
			"name":         self._name,
			"timeUnixNano": str(int(self._time.timestamp() * 1_000_000_000)),
		}

		if len(attributes := _toAttributes(self._dict.items())) != 0:
			converted["attributes"] = attributes

		return converted

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
	_parent:    Nullable[Span]      #: Reference to the parent span (or trace).
	_trace:     Nullable[Trace]     #: Reference to the trace this timespan belongs to.
	_spanID:    str                 #: Identifier of this timespan, as 16 hex digits.

	_beginTime: Nullable[datetime]  #: Timestamp when the timespan begins.
	_endTime:   Nullable[datetime]  #: Timestamp when the timespan ends.
	_startTime: Nullable[int]       #: Performance counter in ns when the timespan was started.
	_stopTime:  Nullable[int]       #: Performance counter in ns when the timespan was stopped.
	_totalTime: Nullable[int]       #: Duration of this timespan in ns.

	_spans:     list[Span]              #: Sub-timespans
	_events:    list[Event]             #: Events happened within this timespan
	_dict:      dict[str, AttributeValue]  #: Dictionary of associated attributes.

	def __init__(self, name: str, parent: Nullable[Span] = None) -> None:
		"""
		Initializes a timespan as part of a software execution trace.

		:param name:        Name of the timespan.
		:param parent:      Optional, reference to a parent span or trace.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Span`.
		"""
		if isinstance(name, str):
			if name == "":
				raise ValueError("Parameter 'name' is empty.")

			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		if parent is None:
			self._parent = None
			self._trace =  None
		elif isinstance(parent, Span):
			self._parent = parent
			self._trace =  parent._trace
			parent._spans.append(self)
		else:
			ex = TypeError("Parameter 'parent' is not of type 'Span'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._spanID =    _newIdentifier(64)

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
	def Parent(self) -> Nullable[Span]:
		"""
		Read-only property to access the span's parent span or trace.

		:returns: Parent span.
		"""
		return self._parent

	@readonly
	def SpanID(self) -> str:
		"""
		Read-only property to access the timespan's identifier.

		It is drawn when the timespan is constructed, so it identifies *this* timespan for as long as it exists.

		:returns: Identifier of the timespan, as 16 hex digits.
		"""
		return self._spanID

	@readonly
	def Trace(self) -> Nullable[Trace]:
		"""
		Read-only property to access the trace this timespan belongs to.

		:returns: The enclosing trace, or ``None`` while the timespan is not part of one.
		"""
		return self._trace

	def _AddSpan(self, span: Span) -> Self:
		"""
		Append a sub-span to this timespan and set this timespan as its parent.

		The sub-span joins this timespan's trace, because a span entered with a ``with``-statement is constructed
		before it knows where it belongs.

		:param span: The sub-span to append.
		:returns:    The appended sub-span.
		"""
		self._spans.append(span)
		span._parent = self
		span._trace =  self._trace

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

		:returns: Number of nested spans.
		"""
		return len(self._spans)

	# iterate subspans with optional predicate
	def IterateSubSpans(self) -> Iterator[Span]:
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

		:returns: Number of events.
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

		:returns: The time when the span was entered, otherwise None.
		"""
		return self._beginTime

	@readonly
	def StopTime(self) -> Nullable[datetime]:
		"""
		Read-only property accessing the absolute time when the span was stopped.

		:returns: The time when the span was exited, otherwise None.
		"""
		return self._endTime

	@readonly
	def Duration(self) -> float:
		"""
		Read-only property accessing the duration from start operation to stop operation.

		If the span is not yet stopped, the duration from start to now is returned.

		:returns:             Duration since span was started in seconds.
		:raises TracingError: When span was never started.
		"""
		if self._startTime is None:
			raise TracingError(f"{self.__class__.__name__} was never started.")

		return ((perf_counter_ns() - self._startTime) if self._stopTime is None else self._totalTime) / 1e9

	@classmethod
	def CurrentSpan(cls) -> Span:
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

		:returns:             The span itself.
		:raises TracingError: If no trace is active, so the span has nothing to attach to. |br|
		                      Use a with-statement on :class:`Trace` to set up software execution tracing.
		"""
		global _threadLocalData

		try:
			currentSpan =  _threadLocalData.currentSpan
		except AttributeError:
			ex = TracingError("Can't setup span. No active trace.")
			ex.add_note("Use with-statement using 'Trace()' to setup software execution tracing.")
			raise ex

		_threadLocalData.currentSpan = currentSpan._AddSpan(self)

		self._beginTime = datetime.now()
		self._startTime = perf_counter_ns()

		return self

	def __exit__(
		self,
		exc_type: Nullable[type[BaseException]] = None,
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

	def __getitem__(self, key: str) -> AttributeValue:
		"""
		Read an event's attached attributes (key-value-pairs) by key.

		:param key: The key to look for.
		:returns:   The value associated to the given key.
		"""
		return self._dict[key]

	def __setitem__(self, key: str, value: AttributeValue) -> None:
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

	def __iter__(self) -> Iterator[tuple[str, AttributeValue]]:
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

	def _ToOTLPJSON(self) -> list[OTLPSpan]:
		"""
		Convert this timespan and its sub-spans to their **OTLP/JSON** representation.

		OTLP has no nesting: the hierarchy is carried by ``parentSpanId``, so the tree is flattened into one list -
		this timespan first, then the lists its sub-spans return - and reassembled by whoever reads the document.

		Both identifiers come from the data model: ``spanId`` is this timespan's own, ``traceId`` belongs to the
		trace it is part of, and ``parentSpanId`` is read off the parent relation. A timespan joins a trace through
		a ``with``-statement, or through the ``parent`` parameter of its constructor.

		:returns:             This timespan and every timespan below it, flattened.
		:raises TracingError: If this timespan is not part of a trace.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		if self._trace is None:
			ex = TracingError(f"Timespan '{self._name}' is not part of a trace.")
			ex.add_note("A span is added to a trace by a 'with'-statement, or by the 'parent' parameter.")
			raise ex

		converted: OTLPSpan = {
			"traceId": self._trace._traceID,
			"spanId":  self._spanID,
			"name":    self._name,
			"kind":    1,                # SPAN_KIND_INTERNAL
		}

		if self._parent is not None:
			converted["parentSpanId"] = self._parent._spanID

		if self.StartTime is not None:
			startTimeUnixNano = int(self.StartTime.timestamp() * 1_000_000_000)
			converted["startTimeUnixNano"] = str(startTimeUnixNano)

			# The wall clock has microsecond resolution while the duration comes from a nanosecond performance
			# counter, so the end is computed from the duration rather than read from a second wall-clock sample.
			# 'Duration' is in seconds; OTLP wants nanoseconds.
			converted["endTimeUnixNano"] = str(startTimeUnixNano + int(self.Duration * 1_000_000_000))

		if len(attributes := _toAttributes(self._dict.items())) != 0:
			converted["attributes"] = attributes

		if len(events := [event._ToOTLPJSON() for event in self._events]) != 0:
			converted["events"] = events

		return [converted, *(span for subSpan in self._spans for span in subSpan._ToOTLPJSON())]

	def Format(self, indent: int = 1, columnSize: int = 25) -> Iterable[str]:
		"""
		Render this timespan and its sub-spans as indented lines.

		:param indent:     Optional, indentation level of this timespan.
		:param columnSize: Optional, column the durations are aligned at.
		:returns:          One line per timespan, deepest last.
		"""
		result = []
		result.append(f"{'  ' * indent}🕑{self._name:<{columnSize - 2 * indent}} {self._totalTime/1e6:8.3f} ms")
		for span in self._spans:
			result.extend(span.Format(indent + 1, columnSize))

		return result

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this timespan.

		:returns: The timespan's name, followed by its parents up to the trace.
		"""
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
	_traceID: str  #: Identifier shared by every timespan of this trace, as 32 hex digits.

	def __init__(self, name: str) -> None:
		"""
		Initializes a software execution trace.

		:param name: Name of the trace.
		"""
		super().__init__(name)

		self._traceID = _newIdentifier(128)
		self._trace =   self

	@readonly
	def TraceID(self) -> str:
		"""
		Read-only property to access the trace's identifier.

		It is drawn when the trace is constructed, so exporting the same trace twice reports the same ``traceId``.

		:returns: Identifier of the trace, as 32 hex digits.
		"""
		return self._traceID

	def __enter__(self) -> Self:
		"""
		Start the trace and register it as the current trace and current span of this thread.

		:returns: The trace itself, so it can be named in an ``as`` clause.
		"""
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
		exc_type: Nullable[type[BaseException]] = None,
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
	def CurrentTrace(cls) -> Trace:
		"""
		Class-method to return the currently active trace or ``None``.

		:returns: Currently active trace or ``None``.
		"""
		try:
			currentTrace = _threadLocalData.currentTrace
		except AttributeError:
			currentTrace = None

		return currentTrace

	def ToJSON(
		self,
		serviceName: Nullable[str] = None,
		scopeName: str = OTLP_SCOPE_NAME,
		scopeVersion: str = __version__
	) -> OTLPDocument:
		"""
		Convert this trace to an **OTLP/JSON** document.

		One format reaches both destinations: an OpenTelemetry collector accepts OTLP natively, and Jaeger has
		accepted it since v1.35, so nothing has to translate between them.

		Every timespan of the trace carries this trace's ``traceId``, and the tree is flattened into a list whose
		``parentSpanId`` references carry the structure - which is how OTLP represents a trace.

		:param serviceName:   Optional, the value of the ``service.name`` resource attribute, which is the name a
		                      backend shows the trace under. Default: the trace's name.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under - the library that
		                      produced them. Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:returns:             The trace as an OTLP/JSON document, ready for :func:`json.dump`.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		return {
			"resourceSpans": [{
				"resource": {
					"attributes": _toAttributes(
						{"service.name": self._name if serviceName is None else serviceName}.items()
					)
				},
				"scopeSpans": [{
					"scope": {"name": scopeName, "version": scopeVersion},
					"spans": self._ToOTLPJSON(),
				}],
			}]
		}

	def ToJSONString(
		self,
		serviceName: Nullable[str] = None,
		indent: Nullable[int] = None,
		scopeName: str = OTLP_SCOPE_NAME,
		scopeVersion: str = __version__
	) -> str:
		"""
		Convert this trace to an **OTLP/JSON** document and encode it as a string.

		:param serviceName:   Optional, the value of the ``service.name`` resource attribute. Default: the trace's name.
		:param indent:        Optional, indentation for a human-readable document. Default: ``None``, the compact form
		                      a collector expects.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:returns:             The OTLP/JSON document, encoded.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		return json_dumps(self.ToJSON(serviceName, scopeName, scopeVersion), indent=indent)

	def WriteJSONFile(
		self,
		jsonFile: Path,
		serviceName: Nullable[str] = None,
		indent: Nullable[int] = None,
		scopeName: str = OTLP_SCOPE_NAME,
		scopeVersion: str = __version__
	) -> None:
		"""
		Write this trace to a file as an **OTLP/JSON** document.

		Missing parent directories are created, because the directory a pipeline collects its artifacts from - usually
		``report/`` - rarely exists yet when the trace is written.

		:param jsonFile:      Path of the file to write.
		:param serviceName:   Optional, the value of the ``service.name`` resource attribute. Default: the trace's name.
		:param indent:        Optional, indentation for a human-readable file. Default: ``None``, the compact form a
		                      collector expects.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If the parent directories couldn't be created.
		:raises TracingError: If the file couldn't be written.
		"""
		if not isinstance(jsonFile, Path):
			ex = TypeError("Parameter 'jsonFile' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonFile)}'.")
			raise ex

		try:
			jsonFile.parent.mkdir(parents=True, exist_ok=True)
		except OSError as ex:
			raise TracingError(f"Directory '{jsonFile.parent}' couldn't be created.") from ex

		try:
			with jsonFile.open("w", encoding="utf-8") as file:
				file.write(self.ToJSONString(serviceName, indent, scopeName, scopeVersion))
		except OSError as ex:
			raise TracingError(f"OTLP/JSON file '{jsonFile}' couldn't be written.") from ex

	def Format(self, indent: int = 0, columnSize: int = 25) -> Iterable[str]:
		"""
		Render this trace and its spans as indented lines.

		:param indent:     Optional, indentation level of the trace.
		:param columnSize: Optional, column the durations are aligned at.
		:returns:          A headline, followed by one line per timespan.
		"""
		result = []
		result.append(f"{'  ' * indent}Software Execution Trace: {self._totalTime/1e6:8.3f} ms")
		result.append(f"{'  ' * indent}📉{self._name:<{columnSize - 2}} {self._totalTime/1e6:8.3f} ms")
		for span in self._spans:
			result.extend(span.Format(indent + 1, columnSize - 2))

		return result
