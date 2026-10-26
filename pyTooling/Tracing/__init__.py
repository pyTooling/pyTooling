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
# Copyright 2025-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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

from base64                import b64encode, b64decode
from binascii              import Error as BinAsciiError
from datetime              import datetime, timedelta
from enum                  import Enum
from json                  import dumps as json_dumps, loads as json_loads, JSONDecodeError
from math                  import isfinite
from os                    import urandom
from pathlib               import Path
from time                  import perf_counter_ns
from threading             import local
from types                 import TracebackType
from typing                import Optional as Nullable, Any, ClassVar, Iterator, Self, Iterable, TypedDict, Union

from pyTooling             import Resources
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Exceptions  import CycleError, DuplicateElementError, ElementNotFoundError, MissingDependencyError, \
                                  ToolingException
from pyTooling.Common      import __version__, getFullyQualifiedName, getTypeName, readResourceFile
from pyTooling.DataModel   import KeyValuePairsMixin
from pyTooling.Versioning  import SemanticVersion
from pyTooling.Warning     import WarningCollector, DirectoryCreatedWarning


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

DurationValue = Union[timedelta, int, float]
"""
A recorded duration, given as a :class:`~datetime.timedelta` or as a number of seconds.

An :class:`int` is whole seconds and a :class:`float` is fractional seconds, matching the unit
:attr:`Span.Duration` reports, so a source stating ``"duration": 98.0`` needs no conversion at the call site.
"""

_MAXIMUM_IDENTIFIER_ATTEMPTS = 4
"""Number of attempts to draw a non-zero random identifier before giving up."""


@export
class TracingError(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Tracing`."""


@export
class TraceNotFoundError(TracingError, ElementNotFoundError):
	"""The exception is raised when a trace identifier names no trace of a collection or a document."""


@export
class SpanNotFoundError(TracingError, ElementNotFoundError):
	"""The exception is raised when a span identifier names no timespan of a collection."""


@export
class DuplicateTraceError(TracingError, DuplicateElementError):
	"""The exception is raised when a trace has more than one root span: a timespan without a ``parentSpanId``."""


@export
class DuplicateSpanError(TracingError, DuplicateElementError):
	"""The exception is raised when two timespans carry the same span identifier."""


@export
class SpanCycleError(TracingError, CycleError):
	"""The exception is raised when timespans reference each other by their ``parentSpanId`` in a cycle."""


@export
class SpanState(Enum):
	"""An enumeration describing which of a timespan's times are filled in."""

	Empty =    0  #: Neither begin nor end time is set, so the timespan can be timed by a ``with``-statement.
	Running =  1  #: The begin time is set, but the end time isn't, so the timespan is still running.
	Complete = 2  #: Begin and end time are both set.


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
class OTLPStatus(TypedDict):
	"""OTLP's ``Status``: whether a span completed successfully."""

	code:    int  #: Status code - always ``2`` (``STATUS_CODE_ERROR``) here, as only a failed span carries a status.
	message: str  #: Description of the error.


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
	status:            OTLPStatus           #: Status of the span, present for a failed span only.


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


@export
class TraceElement(KeyValuePairsMixin, metaclass=ExtendedType, slots=True):
	"""
	Base-class of a trace's elements: a named thing within a timespan, carrying arbitrary attributes
	(key-value-pairs).

	It holds what a :class:`Span` and an :class:`Event` have in common - their name, the timespan enclosing them and
	their attributes - and validates the two parameters every element takes. **It doesn't attach the element to its
	parent**, because where it goes differs: a sub-span joins :attr:`Span._spans` and an event
	:attr:`Span._events`, and neither may happen before the derived class has validated the rest of its parameters.

	The attributes are read, written and removed like a dictionary's items
	(:class:`~pyTooling.DataModel.KeyValuePairsMixin`); :meth:`IterateAttributes` yields them as pairs.
	"""
	_name:   str             #: Name of the element.
	_parent: Nullable[Span]  #: Reference to the enclosing timespan (or trace).

	def __init__(self, name: str, parent: Nullable[Span] = None) -> None:
		"""
		Initializes a trace's element, without attaching it to its parent.

		:param name:        Name of the element.
		:param parent:      Optional, reference to the enclosing timespan.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Span`.
		"""
		super().__init__()

		if isinstance(name, str):
			if name == "":
				raise ValueError("Parameter 'name' is empty.")

			self._name = name
		else:
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		if parent is not None and not isinstance(parent, Span):
			ex = TypeError("Parameter 'parent' is not of type 'Span'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the element's name (:attr:`_name`).

		:returns: Name of the element.
		"""
		return self._name

	@readonly
	def Parent(self) -> Nullable[Span]:
		"""
		Read-only property to access the timespan enclosing this element (:attr:`_parent`).

		:returns: The enclosing timespan, or ``None`` for a trace and for an element not attached to one.
		"""
		return self._parent

	def IterateAttributes(self) -> Iterator[tuple[str, AttributeValue]]:
		"""
		Returns an iterator to iterate all attached attributes as :pycode:`(key, value)` tuples.

		:returns: Iterator to iterate all attributes.
		"""
		return iter(self._dict.items())

	@classmethod
	def _ToOTLPKeyValues(cls, keyValues: Iterable[tuple[str, AttributeValue]]) -> list[OTLPAttribute]:
		"""
		Convert key-value pairs to OTLP's list of attributes.

		:param keyValues:     The key-value pairs to convert.
		:returns:             One ``{"key": ..., "value": ...}`` mapping per pair.
		:raises TracingError: If a value is of a type OTLP's ``AnyValue`` can't carry.
		"""
		return [{"key": key, "value": cls._ToOTLPAnyValue(value)} for key, value in keyValues]

	@classmethod
	def _ToOTLPAnyValue(cls, value: AttributeValue) -> OTLPAnyValue:
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
			return {"arrayValue": {"values": [cls._ToOTLPAnyValue(element) for element in value]}}
		elif isinstance(value, dict):
			return {"kvlistValue": {"values": cls._ToOTLPKeyValues(value.items())}}

		ex = TracingError(f"Attribute value of type '{getFullyQualifiedName(value)}' can't be represented in OTLP.")
		ex.add_note("Supported are: bool, int, float, str, bytes, and a list, tuple or dict of these.")
		raise ex

	@classmethod
	def _ParseOTLPKeyValues(cls, keyValues: list[dict[str, Any]], path: str) -> dict[str, AttributeValue]:
		"""
		Convert OTLP's list of attributes, validated by the schema, to key-value pairs.

		:param keyValues:     The ``{"key": ..., "value": ...}`` mappings to convert.
		:param path:          Position of the list within the document, for the exception's message.
		:returns:             One key-value pair per entry.
		:raises TracingError: If two entries carry the same key. |br|
		                      OTLP requires the keys of an attribute list to be unique.
		:raises TracingError: If a value carries no value.
		:raises TracingError: If a byte string isn't base64-encoded.
		"""
		keyValuePairs: dict[str, AttributeValue] = {}
		for position, keyValue in enumerate(keyValues):
			key = keyValue["key"]
			if key in keyValuePairs:
				ex = TracingError(f"Field '{path}' has more than one attribute named '{key}'.")
				ex.add_note("OTLP requires the keys of an attribute list to be unique.")
				raise ex

			keyValuePairs[key] = cls._ParseOTLPAnyValue(keyValue.get("value", {}), f"{path}[{position}].value")

		return keyValuePairs

	@classmethod
	def _ParseOTLPAnyValue(cls, anyValue: dict[str, Any], path: str) -> AttributeValue:
		"""
		Unwrap a value from OTLP's ``AnyValue`` representation, validated by the schema.

		OTLP has a single ``arrayValue``, so a :class:`tuple` written by :meth:`_ToOTLPAnyValue` returns as a
		:class:`list`. A byte string may use the standard or the URL-safe base64 alphabet, padded or not.

		:param anyValue:      The mapping to unwrap.
		:param path:          Position of the value within the document, for the exception's message.
		:returns:             The Python value the mapping carries.
		:raises TracingError: If the mapping carries no value. |br|
		                      OTLP allows an empty 'AnyValue', but an attribute of a trace, a span or an event has a value.
		:raises TracingError: If a byte string isn't base64-encoded.
		:raises TracingError: If a mapping of values carries the same key twice.
		"""
		if "stringValue" in anyValue:
			return anyValue["stringValue"]
		elif "boolValue" in anyValue:
			return anyValue["boolValue"]
		elif "intValue" in anyValue:
			return int(anyValue["intValue"])
		elif "doubleValue" in anyValue:
			return float(anyValue["doubleValue"])
		elif "bytesValue" in anyValue:
			encoded = anyValue["bytesValue"].rstrip("=").translate(str.maketrans("-_", "+/"))
			try:
				return b64decode(encoded + "=" * (-len(encoded) % 4), validate=True)
			except BinAsciiError as cause:
				ex = TracingError(f"Field '{path}.bytesValue' is not base64-encoded.")
				ex.add_note(f"Got '{anyValue['bytesValue']}'.")
				raise ex from cause
		elif "arrayValue" in anyValue:
			return [
				cls._ParseOTLPAnyValue(element, f"{path}.arrayValue.values[{position}]")
				for position, element in enumerate(anyValue["arrayValue"].get("values", []))
			]
		elif "kvlistValue" in anyValue:
			return cls._ParseOTLPKeyValues(anyValue["kvlistValue"].get("values", []), f"{path}.kvlistValue.values")

		ex = TracingError(f"Field '{path}' carries no value.")
		ex.add_note("OTLP allows an empty 'AnyValue', but an attribute of a trace, a span or an event has a value.")
		raise ex

	@staticmethod
	def _ToUnixNanoseconds(timestamp: datetime) -> int:
		"""
		Compute a timestamp's distance from the Unix epoch in nanoseconds, exact to the microsecond it holds.

		A naive timestamp is local time, as for :meth:`~datetime.datetime.timestamp`.

		:param timestamp: The timestamp to convert.
		:returns:         Nanoseconds since the Unix epoch.
		"""
		return int(timestamp.replace(microsecond=0).timestamp()) * 1_000_000_000 + timestamp.microsecond * 1_000

	@staticmethod
	def _FromUnixNanoseconds(nanoseconds: int) -> datetime:
		"""
		Convert nanoseconds since the Unix epoch to a local timestamp, rounded to the nearest microsecond.

		:param nanoseconds:    Nanoseconds since the Unix epoch.
		:returns:              The timestamp, in local time - the time zone :func:`~datetime.datetime.now` stamps in.
		:raises OverflowError: If the value is outside the range :class:`~datetime.datetime` can represent.
		:raises OSError:       If the value is outside the range the platform's time functions accept.
		:raises ValueError:    If the value is outside the range :class:`~datetime.datetime` can represent.
		"""
		microseconds =       (nanoseconds + 500) // 1_000
		seconds, remainder = divmod(microseconds, 1_000_000)

		return datetime.fromtimestamp(seconds) + timedelta(microseconds=remainder)


@export
class Event(TraceElement):
	"""
	Represents a named event within a timespan (:class:`Span`) used in a software execution trace.

	It may contain arbitrary attributes (key-value pairs).
	"""
	_time:      datetime            #: Timestamp of the event.

	def __init__(self, name: str, time: Nullable[datetime] = None, *, parent: Nullable[Span] = None) -> None:
		"""
		Initializes a named event.

		:param name:        The name of the event.
		:param time:        Optional, time when the event happened. Default: the current system time.
		:param parent:      Optional, reference to the parent span.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'time' is not of type :class:`~datetime.datetime`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Span`.
		"""
		super().__init__(name, parent)

		if time is None:
			self._time = datetime.now()
		elif isinstance(time, datetime):
			self._time = time
		else:
			ex = TypeError("Parameter 'time' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(time)}'.")
			raise ex

		if parent is not None:
			parent._events.append(self)

	@readonly
	def Time(self) -> datetime:
		"""
		Read-only property to access the event's timestamp.

		:returns: Timestamp of the event.
		"""
		return self._time

	def _ToOTLPJSON(self) -> OTLPEvent:
		"""
		Convert this event to its **OTLP/JSON** representation.

		:returns:             The event as an OTLP mapping.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		converted: OTLPEvent = {
			"name":         self._name,
			"timeUnixNano": str(self._ToUnixNanoseconds(self._time)),
		}

		if len(attributes := self._ToOTLPKeyValues(self._dict.items())) != 0:
			converted["attributes"] = attributes

		return converted

	@classmethod
	def _ParseOTLPJSON(cls, otlpEvent: dict[str, Any], parent: Span, path: str) -> Self:
		"""
		Construct an event from its **OTLP/JSON** representation, validated by the schema, and attach it to a timespan.

		``timeUnixNano`` is required, although OTLP allows it to be absent, which means the Unix epoch.

		:param otlpEvent:     The event as an OTLP mapping.
		:param parent:        The timespan the event happened in.
		:param path:          Position of the mapping within the document, for the exception's message.
		:returns:             The event, appended to the timespan's events.
		:raises TracingError: If the event's name is missing or empty.
		:raises TracingError: If the event's time is missing. |br|
		                      An event without a time would be placed at the Unix epoch.
		:raises TracingError: If the event's time is outside the range a :class:`~datetime.datetime` can represent.
		:raises TracingError: If two attributes carry the same key.
		:raises TracingError: If an attribute carries no value.
		:raises TracingError: If a byte string isn't base64-encoded.
		"""
		name = otlpEvent.get("name", "")
		if name == "":
			raise TracingError(f"Field '{path}.name' is missing or empty.")
		elif "timeUnixNano" not in otlpEvent:
			ex = TracingError(f"Field '{path}.timeUnixNano' is missing.")
			ex.add_note("An event without a time would be placed at the Unix epoch.")
			raise ex

		nanoseconds = int(otlpEvent["timeUnixNano"])
		try:
			time = cls._FromUnixNanoseconds(nanoseconds)
		except (OSError, OverflowError, ValueError) as cause:
			ex = TracingError(f"Field '{path}.timeUnixNano' is not a timestamp a 'datetime' can represent.")
			ex.add_note(f"Got {nanoseconds} ns since the Unix epoch.")
			raise ex from cause

		event =       cls(name, time, parent=parent)
		event._dict = cls._ParseOTLPKeyValues(otlpEvent.get("attributes", []), f"{path}.attributes")

		return event

	def __str__(self) -> str:
		"""
		Return a string representation of the event.

		:returns: The event's name.
		"""
		return self._name


@export
class Span(TraceElement):
	"""
	Represents a timespan (span) within another timespan or trace.

	It may contain sub-spans, events and arbitrary attributes (key-value pairs).
	"""
	_trace:     Nullable[Union[_Trace, Fragment]]  #: Reference to the trace (or fragment) this timespan belongs to.
	_spanID:    str                                #: Identifier of this timespan, as 16 hex digits.

	_beginTime: Nullable[datetime]                #: Timestamp when the timespan begins.
	_endTime:   Nullable[datetime]                #: Timestamp when the timespan ends.
	_startTime: Nullable[int]                     #: Performance counter in ns when the timespan was started.
	_stopTime:  Nullable[int]                     #: Performance counter in ns when the timespan was stopped.
	_totalTime: Nullable[int]                     #: Duration of this timespan in ns.

	_spans:     list[Span]                        #: Sub-timespans
	_events:    list[Event]                       #: Events happened within this timespan
	_exception: Nullable[BaseException]           #: The exception that left the ``with``-statement timing this timespan.

	def __init__(
		self,
		name:      str,
		beginTime: Nullable[datetime] = None,
		endTime:   Nullable[datetime] = None,
		duration:  Nullable[DurationValue] = None,
		*,
		parent:    Nullable[Span] = None
	) -> None:
		"""
		Initializes a timespan as part of a software execution trace.

		A timespan is timed when it is entered and left by a ``with``-statement. A timespan that was measured elsewhere
		is constructed with its recorded times instead.

		The end of a recorded timespan is given either as ``endTime`` or as ``duration``, whichever the source reports;
		a ``duration`` is converted to ``endTime``, so both forms are stored alike.

		:param name:        Name of the timespan.
		:param beginTime:   Optional, recorded time when the timespan began. Default: the time the timespan is entered.
		:param endTime:     Optional, recorded time when the timespan ended. Requires ``beginTime``. Default: the time
		                    the timespan is left, or ``None`` for a recorded timespan, which is still running.
		:param duration:    Optional, recorded duration of the timespan, as an alternative to ``endTime``. Requires
		                    ``beginTime``. A :class:`~datetime.timedelta`, or a number of seconds as :class:`int`
		                    (whole) or :class:`float` (fractional).
		:param parent:      Optional, reference to a parent span or trace.
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'beginTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError: If parameter 'endTime' is given without parameter 'beginTime'.
		:raises TypeError:  If parameter 'endTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError: If parameter 'endTime' is before parameter 'beginTime'.
		:raises TypeError:  If parameter 'duration' is not of type :class:`~datetime.timedelta`, :class:`int` or
		                    :class:`float`.
		:raises ValueError: If parameter 'duration' is not a finite number of seconds.
		:raises ValueError: If parameter 'duration' is given without parameter 'beginTime'.
		:raises ValueError: If parameter 'duration' is negative.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Span`.
		:raises ValueError: If parameters 'endTime' and 'duration' are both given.
		:raises ValueError: If parameters 'beginTime' and 'endTime' mix a time zone aware and a naive timestamp.
		:raises ValueError: If the timespan begins before or ends after its parent.
		"""
		super().__init__(name, parent)

		if duration is not None:
			if beginTime is None:
				ex = ValueError("Parameter 'duration' is given without parameter 'beginTime'.")
				ex.add_note(f"Got duration '{duration}'.")
				raise ex
			elif endTime is not None:
				ex = ValueError("Parameters 'endTime' and 'duration' are both given.")
				ex.add_note(f"Got endTime '{endTime}' and duration '{duration}'.")
				ex.add_note("Give the end of a recorded timespan either as 'endTime' or as 'duration'.")
				raise ex

			if isinstance(duration, timedelta):
				if duration < timedelta(0):
					ex = ValueError("Parameter 'duration' is negative.")
					ex.add_note(f"Got duration '{duration}'.")
					raise ex
			elif isinstance(duration, bool) or not isinstance(duration, (int, float)):
				ex = TypeError("Parameter 'duration' is not of type 'timedelta', 'int' or 'float'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(duration)}'.")
				raise ex
			elif not isfinite(duration):
				ex = ValueError("Parameter 'duration' is not a finite number of seconds.")
				ex.add_note(f"Got duration '{duration}'.")
				raise ex
			elif duration < 0:
				ex = ValueError("Parameter 'duration' is negative.")
				ex.add_note(f"Got duration '{duration}'.")
				raise ex
			else:
				duration = timedelta(seconds=duration)

		if beginTime is None:
			if endTime is not None:
				ex = ValueError("Parameter 'endTime' is given without parameter 'beginTime'.")
				ex.add_note(f"Got endTime '{endTime}'.")
				raise ex
		elif not isinstance(beginTime, datetime):
			ex = TypeError("Parameter 'beginTime' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(beginTime)}'.")
			raise ex
		elif endTime is not None:
			if not isinstance(endTime, datetime):
				ex = TypeError("Parameter 'endTime' is not of type 'datetime'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(endTime)}'.")
				raise ex
			elif (beginTime.utcoffset() is None) != (endTime.utcoffset() is None):
				ex = ValueError("Parameters 'beginTime' and 'endTime' mix a time zone aware and a naive timestamp.")
				ex.add_note(f"Got '{beginTime}' and '{endTime}'.")
				raise ex
			elif endTime < beginTime:
				ex = ValueError("Parameter 'endTime' is before parameter 'beginTime'.")
				ex.add_note(f"Got '{beginTime}' to '{endTime}'.")
				raise ex

		if duration is not None:
			endTime = beginTime + duration

		if parent is None:
			self._trace = None
		else:
			self._CheckParentRange(parent, beginTime, endTime)

			self._trace = parent._trace
			parent._spans.append(self)

		self._spanID =    self._NewIdentifier(64)

		self._beginTime = beginTime
		self._startTime = None
		self._endTime =   endTime
		self._stopTime =  None
		if beginTime is None or endTime is None:
			self._totalTime = None
		else:
			self._totalTime = self._RangeToNanoseconds(beginTime, endTime)

		self._spans =     []
		self._events =    []
		self._exception = None

	@staticmethod
	def _NewIdentifier(bits: int) -> str:
		"""
		Generate a random trace or span identifier, which is never all zeros.

		:param bits:          Width of the identifier: 128 for a trace, 64 for a span.
		:returns:             The identifier as a lower-case hex string.
		:raises TracingError: If no non-zero identifier was drawn within :data:`_MAXIMUM_IDENTIFIER_ATTEMPTS` attempts.
		"""
		for _ in range(_MAXIMUM_IDENTIFIER_ATTEMPTS):
			if any(identifier := urandom(bits // 8)):
				return identifier.hex()
		else:
			ex = TracingError(f"Couldn't draw a non-zero {bits}-bit random identifier.")
			ex.add_note(f"Tried {_MAXIMUM_IDENTIFIER_ATTEMPTS} times.")
			raise ex

	@staticmethod
	def _RangeToNanoseconds(beginTime: datetime, endTime: datetime) -> int:
		"""
		Compute the length of a timespan in nanoseconds, exact to the microsecond both timestamps hold.

		:param beginTime: Time when the timespan began.
		:param endTime:   Time when the timespan ended.
		:returns:         Length of the timespan in nanoseconds.
		"""
		difference = endTime - beginTime
		seconds =    difference.days * 86_400 + difference.seconds

		return seconds * 1_000_000_000 + difference.microseconds * 1_000

	@readonly
	def SpanID(self) -> str:
		"""
		Read-only property to access the timespan's identifier.

		It is drawn when the timespan is constructed, so it identifies *this* timespan for as long as it exists.

		:returns: Identifier of the timespan, as 16 hex digits.
		"""
		return self._spanID

	@readonly
	def Exception(self) -> Nullable[BaseException]:
		"""
		Read-only property to access the exception that left the ``with``-statement timing this timespan
		(:attr:`_exception`).

		A timespan with an exception has failed. The exception isn't caught: it propagates out of the ``with``-statement
		as before, and is recorded only.

		:returns: The exception, or ``None`` if the timespan ended normally or wasn't timed by a ``with``-statement.
		"""
		return self._exception

	@readonly
	def Trace(self) -> Nullable[Union[Trace, Fragment]]:
		"""
		Read-only property to access the trace this timespan belongs to.

		A timespan below a :class:`Fragment` belongs to the fragment, until a :class:`TraceCollection` attaches the
		fragment to its parent.

		:returns: The enclosing trace or fragment, or ``None`` while the timespan is not part of one.
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

		:returns: The time when the span was entered, or its recorded begin time, otherwise None.
		"""
		return self._beginTime

	@property
	def StopTime(self) -> Nullable[datetime]:
		"""
		Property accessing the absolute time when the span was stopped.

		The end time of a recorded timespan can be assigned once, for a source that reports the end of a timespan later
		than its begin. A timespan timed by a ``with``-statement is stopped by leaving that block, so assigning to it
		raises.

		:returns:             The time when the span was exited, or its recorded end time, otherwise None.
		:raises TracingError: When the timespan has no begin time yet.
		:raises TracingError: When the timespan already has an end time.
		:raises TracingError: When the timespan is timed by a ``with``-statement.
		:raises TypeError:    When the assigned value is not of type :class:`~datetime.datetime`.
		:raises ValueError:   When the assigned value and the begin time mix a time zone aware and a naive timestamp.
		:raises ValueError:   When the assigned value is before the begin time.
		"""
		return self._endTime

	@StopTime.setter
	def StopTime(self, value: datetime) -> None:
		if self._beginTime is None:
			ex = TracingError(f"{getTypeName(self)} '{self._name}' has no begin time and can't be stopped.")
			ex.add_note("Construct it with a 'beginTime' to record a timespan whose end is reported later.")
			raise ex
		elif self._startTime is not None:
			ex = TracingError(f"{getTypeName(self)} '{self._name}' is timed by a with-statement.")
			ex.add_note("It is stopped by leaving that block.")
			raise ex
		elif self._endTime is not None:
			ex = TracingError(f"{getTypeName(self)} '{self._name}' already has an end time.")
			ex.add_note(f"Got '{self._endTime}'.")
			raise ex
		elif not isinstance(value, datetime):
			ex = TypeError("Parameter 'value' is not of type 'datetime'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex
		elif (self._beginTime.utcoffset() is None) != (value.utcoffset() is None):
			ex = ValueError("Parameter 'value' and the begin time mix a time zone aware and a naive timestamp.")
			ex.add_note(f"Got '{self._beginTime}' and '{value}'.")
			raise ex
		elif value < self._beginTime:
			ex = ValueError("Parameter 'value' is before the begin time.")
			ex.add_note(f"Got '{self._beginTime}' to '{value}'.")
			raise ex

		self._endTime =   value
		self._totalTime = self._RangeToNanoseconds(self._beginTime, value)

	def Stop(self) -> Self:
		"""
		Stop a running timespan now.

		A timespan that ended at a time already known is stopped by assigning that time to :attr:`StopTime` instead.

		:returns:             The timespan itself, so the call can be chained.
		:raises TracingError: When the timespan has no begin time yet. |br|
		                      Construct it with a 'beginTime' to record a timespan that is stopped later.
		:raises TracingError: When the timespan already has an end time.
		:raises TracingError: When the timespan is timed by a ``with``-statement.
		"""
		if self._beginTime is None:
			ex = TracingError(f"{getTypeName(self)} '{self._name}' has no begin time and can't be stopped.")
			ex.add_note("Construct it with a 'beginTime' to record a timespan that is stopped later.")
			raise ex

		self.StopTime = datetime.now(self._beginTime.tzinfo)

		return self

	def _CheckParentRange(self, parent: Span, beginTime: Nullable[datetime], endTime: Nullable[datetime]) -> None:
		"""
		Check that a recorded timespan lies within the range of its direct parent.

		Grandparents need no check: containment is transitive, so every ancestor's range holds once each direct
		parent-child pair is checked.

		:param parent:      The parent span or trace this timespan is attached to.
		:param beginTime:   The timespan's begin time, or ``None``.
		:param endTime:     The timespan's end time, or ``None``.
		:raises ValueError: If the timespan begins before its parent.
		:raises ValueError: If the timespan ends after its parent.
		:raises ValueError: If a timespan and its parent mix a time zone aware and a naive timestamp.
		"""
		if beginTime is None or parent._beginTime is None:
			return

		if (beginTime.utcoffset() is None) != (parent._beginTime.utcoffset() is None):
			ex = ValueError(
				f"Timespan '{self._name}' and its parent '{parent._name}' mix a time zone aware and a naive timestamp."
			)
			ex.add_note(f"Got '{beginTime}' and '{parent._beginTime}'.")
			raise ex
		elif beginTime < parent._beginTime:
			ex = ValueError(f"Timespan '{self._name}' begins before its parent '{parent._name}'.")
			ex.add_note(f"Got '{beginTime}', while the parent begins at '{parent._beginTime}'.")
			raise ex

		if endTime is not None and parent._endTime is not None and endTime > parent._endTime:
			ex = ValueError(f"Timespan '{self._name}' ends after its parent '{parent._name}'.")
			ex.add_note(f"Got '{endTime}', while the parent ends at '{parent._endTime}'.")
			raise ex

	@readonly
	def Duration(self) -> timedelta:
		"""
		Read-only property accessing the duration from start operation to stop operation.

		If the span is not yet stopped, the duration from start to now is returned. For a timespan with recorded times,
		the duration is the difference of both times, or the time since its recorded begin while it has no end. A
		:class:`~datetime.timedelta` resolves microseconds; :attr:`DurationInSeconds` keeps the nanoseconds a performance
		counter measured.

		:returns:             Duration since span was started.
		:raises TracingError: When span was never started.
		"""
		return timedelta(seconds=self.DurationInSeconds)

	@readonly
	def DurationInSeconds(self) -> float:
		"""
		Read-only property accessing the duration from start operation to stop operation in seconds.

		It is :attr:`Duration` as a number: from a performance counter's nanoseconds, or from the difference of the
		recorded times.

		:returns:             Duration since span was started in seconds.
		:raises TracingError: When span was never started.
		"""
		if self._totalTime is not None:
			return self._totalTime / 1e9
		elif self._startTime is not None:
			return (perf_counter_ns() - self._startTime) / 1e9
		elif self._beginTime is not None:
			return (datetime.now(self._beginTime.tzinfo) - self._beginTime).total_seconds()

		raise TracingError(f"{getTypeName(self)} was never started.")

	@readonly
	def State(self) -> SpanState:
		"""
		Read-only property accessing which of the timespan's times are filled in.

		The state does not say where the times came from: a timespan timed by a ``with``-statement is
		:attr:`~SpanState.Running` inside the block and :attr:`~SpanState.Complete` after it, exactly as a recorded one
		is. Only an :attr:`~SpanState.Empty` timespan can be entered.

		:returns: Which of the timespan's times are filled in.
		"""
		if self._beginTime is None:
			return SpanState.Empty
		elif self._endTime is None:
			return SpanState.Running
		else:
			return SpanState.Complete

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
		Enter the context and start the span.

		The span is added to the current span of this thread and becomes the current span.

		:returns:             The span itself.
		:raises TracingError: If the span is not :attr:`~SpanState.Empty`. |br|
		                      A timespan that was already timed can't be entered a second time.
		:raises TracingError: If no trace is active, so the span has nothing to attach to. |br|
		                      Use a with-statement on :class:`Trace` to set up software execution tracing.
		"""
		global _threadLocalData

		if self.State is not SpanState.Empty:
			ex = TracingError(f"Timespan '{self._name}' is not empty and can't be entered.")
			ex.add_note(f"Its state is '{self.State.name}'.")
			ex.add_note("A timespan that was already timed can't be entered a second time.")
			raise ex

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
		Exit the context and stop the span.

		The span's parent becomes the current span of this thread again. An exception leaving the ``with``-statement is
		recorded in :attr:`Exception`, and propagates.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``None``
		"""
		global _threadLocalData

		self._stopTime =  perf_counter_ns()
		self._endTime =   datetime.now()
		self._totalTime = self._stopTime - self._startTime
		self._exception = exc_val

		currentSpan = _threadLocalData.currentSpan
		_threadLocalData.currentSpan = currentSpan._parent

	def _ToOTLPJSON(self) -> list[OTLPSpan]:
		"""
		Convert this timespan and its sub-spans to their **OTLP/JSON** representation.

		OTLP has no nesting: the hierarchy is carried by ``parentSpanId``, so the tree is flattened into one list -
		this timespan first, then the lists its sub-spans return - and reassembled by whoever reads the document.

		Both identifiers come from the data model: ``spanId`` is this timespan's own, ``traceId`` belongs to the
		trace (or :class:`Fragment`) it is part of, and ``parentSpanId`` is read off the parent relation. A timespan
		joins a trace through a ``with``-statement, or through the ``parent`` parameter of its constructor.

		:returns:             This timespan and every timespan below it, flattened.
		:raises TracingError: If this timespan is not part of a trace. |br|
		                      A span is added to a trace by a 'with'-statement, or by the 'parent' parameter.
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
			startTimeUnixNano = self._ToUnixNanoseconds(self.StartTime)
			converted["startTimeUnixNano"] = str(startTimeUnixNano)

			# The wall clock has microsecond resolution while the duration comes from a nanosecond performance
			# counter, so the end is computed from the duration rather than read from a second wall-clock sample.
			# A finished timespan's total is already in nanoseconds; 'DurationInSeconds' of a running one is in seconds.
			totalTime = int(self.DurationInSeconds * 1_000_000_000) if self._totalTime is None else self._totalTime
			converted["endTimeUnixNano"] = str(startTimeUnixNano + totalTime)

		if len(attributes := self._ToOTLPKeyValues(self._dict.items())) != 0:
			converted["attributes"] = attributes

		if len(events := [event._ToOTLPJSON() for event in self._events]) != 0:
			converted["events"] = events

		if self._exception is not None:
			converted["status"] = {
				"code":    2,  # STATUS_CODE_ERROR
				"message": f"{getFullyQualifiedName(self._exception)}: {self._exception}"
			}

		return [converted, *(span for subSpan in self._spans for span in subSpan._ToOTLPJSON())]

	@classmethod
	def _ParseOTLPJSON(cls, otlpSpan: dict[str, Any], path: str, *, parent: Nullable[Span] = None) -> Self:
		"""
		Construct a timespan from its **OTLP/JSON** representation, validated by the schema.

		The sub-spans are not constructed here: OTLP has no nesting, and :class:`TraceCollection` creates each timespan
		with the one its ``parentSpanId`` names as ``parent``. ``kind`` and ``status`` are not read.

		A timespan that was never entered has no timestamps, so both are accepted as absent, but not one without the
		other. :attr:`Duration` is the difference of both timestamps.

		:param otlpSpan:      The timespan as an OTLP mapping.
		:param path:          Position of the mapping within the document, for the exception's message.
		:param parent:        Optional, the enclosing timespan. Default: none, for a trace or the root of a fragment.
		:returns:             The timespan, appended to its parent's sub-spans.
		:raises TracingError: If the timespan's name is missing or empty.
		:raises TracingError: If the timespan has one timestamp instead of both or neither.
		:raises TracingError: If the timespan ends before it starts.
		:raises TracingError: If a timestamp is outside the range a :class:`~datetime.datetime` can represent.
		:raises TracingError: If an event's name or time is missing.
		:raises TracingError: If two attributes carry the same key.
		:raises TracingError: If an attribute carries no value.
		:raises TracingError: If a byte string isn't base64-encoded.
		"""
		name = otlpSpan.get("name", "")
		if name == "":
			raise TracingError(f"Field '{path}.name' is missing or empty.")

		hasStartTime = "startTimeUnixNano" in otlpSpan
		hasEndTime =   "endTimeUnixNano" in otlpSpan
		if hasStartTime and not hasEndTime:
			ex = TracingError(f"Field '{path}.endTimeUnixNano' is missing.")
			ex.add_note("A timespan has both timestamps or neither, and this one has 'startTimeUnixNano'.")
			raise ex
		elif hasEndTime and not hasStartTime:
			ex = TracingError(f"Field '{path}.startTimeUnixNano' is missing.")
			ex.add_note("A timespan has both timestamps or neither, and this one has 'endTimeUnixNano'.")
			raise ex

		timespan = cls._NewFromOTLPJSON(name, otlpSpan, parent)
		timespan._spanID = otlpSpan["spanId"].lower()

		if hasStartTime:
			startTimeUnixNano = int(otlpSpan["startTimeUnixNano"])
			endTimeUnixNano =   int(otlpSpan["endTimeUnixNano"])
			if endTimeUnixNano < startTimeUnixNano:
				ex = TracingError(f"Field '{path}.endTimeUnixNano' precedes '{path}.startTimeUnixNano'.")
				ex.add_note(f"Got {startTimeUnixNano} ns to {endTimeUnixNano} ns.")
				raise ex

			try:
				timespan._beginTime = cls._FromUnixNanoseconds(startTimeUnixNano)
			except (OSError, OverflowError, ValueError) as cause:
				ex = TracingError(f"Field '{path}.startTimeUnixNano' is not a timestamp a 'datetime' can represent.")
				ex.add_note(f"Got {startTimeUnixNano} ns since the Unix epoch.")
				raise ex from cause

			try:
				timespan._endTime = cls._FromUnixNanoseconds(endTimeUnixNano)
			except (OSError, OverflowError, ValueError) as cause:
				ex = TracingError(f"Field '{path}.endTimeUnixNano' is not a timestamp a 'datetime' can represent.")
				ex.add_note(f"Got {endTimeUnixNano} ns since the Unix epoch.")
				raise ex from cause

			# both timestamps are integers, so the duration is exact even though each of them is rounded to the
			# microsecond a 'datetime' can hold.
			timespan._totalTime = endTimeUnixNano - startTimeUnixNano

		timespan._dict = cls._ParseOTLPKeyValues(otlpSpan.get("attributes", []), f"{path}.attributes")

		for position, otlpEvent in enumerate(otlpSpan.get("events", [])):
			Event._ParseOTLPJSON(otlpEvent, timespan, f"{path}.events[{position}]")

		return timespan

	@classmethod
	def _NewFromOTLPJSON(cls, name: str, otlpSpan: dict[str, Any], parent: Nullable[Span]) -> Self:
		"""
		Construct the timespan :meth:`_ParseOTLPJSON` fills from an **OTLP/JSON** mapping.

		A class taking more than a name and a parent from the mapping overrides it, see :class:`Fragment`.

		:param name:     Name of the timespan.
		:param otlpSpan: The timespan as an OTLP mapping, validated by the schema.
		:param parent:   The enclosing timespan, or ``None`` for a trace or the root of a fragment.
		:returns:        The new timespan, appended to its parent's sub-spans.
		"""
		if parent is None:
			return cls(name)
		else:
			return cls(name, parent=parent)

	def _FormatDuration(self) -> str:
		"""
		Format the duration in milliseconds, right-aligned in 8 characters, as :meth:`Format` lines show it.

		:returns: The duration with unit, or ``--`` with unit for a timespan that never started.
		"""
		if self.State is SpanState.Empty:
			return f"{'--':>8} ms"

		return f"{self.DurationInSeconds * 1e3:8.3f} ms"

	def Format(self, indent: int = 1, columnSize: int = 25) -> Iterable[str]:
		"""
		Render this timespan and its sub-spans as indented lines.

		A timespan that never started (:attr:`~SpanState.Empty`) has no duration; it shows ``--`` instead.

		:param indent:     Optional, indentation level of this timespan.
		:param columnSize: Optional, column the durations are aligned at.
		:returns:          One line per timespan, deepest last.
		"""
		result = []
		result.append(f"{'  ' * indent}🕑{self._name:<{columnSize - 2 * indent}} {self._FormatDuration()}")
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

	def __init__(
		self,
		name:      str,
		beginTime: Nullable[datetime] = None,
		endTime:   Nullable[datetime] = None,
		duration:  Nullable[DurationValue] = None
	) -> None:
		"""
		Initializes a software execution trace.

		A trace is timed when it is entered and left by a ``with``-statement. A trace that was measured elsewhere is
		constructed with its recorded times instead, and its timespans are attached with their ``parent`` parameter.

		:param name:        Name of the trace.
		:param beginTime:   Optional, recorded time when the trace began. Default: the time the trace is entered.
		:param endTime:     Optional, recorded time when the trace ended. Requires ``beginTime``. Default: the time the
		                    trace is left, or ``None`` for a recorded trace, which is still running.
		:param duration:    Optional, recorded duration of the trace, as an alternative to ``endTime``. Requires
		                    ``beginTime``. A :class:`~datetime.timedelta`, or a number of seconds as :class:`int`
		                    (whole) or :class:`float` (fractional).
		:raises TypeError:  If parameter 'name' is not of type :class:`str`.
		:raises ValueError: If parameter 'name' is empty.
		:raises TypeError:  If parameter 'beginTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError: If parameter 'endTime' is given without parameter 'beginTime'.
		:raises TypeError:  If parameter 'endTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError: If parameter 'endTime' is before parameter 'beginTime'.
		:raises TypeError:  If parameter 'duration' is not of type :class:`~datetime.timedelta`, :class:`int` or
		                    :class:`float`.
		:raises ValueError: If parameter 'duration' is not a finite number of seconds.
		:raises ValueError: If parameter 'duration' is given without parameter 'beginTime'.
		:raises ValueError: If parameter 'duration' is negative.
		:raises ValueError: If parameters 'endTime' and 'duration' are both given.
		:raises ValueError: If parameters 'beginTime' and 'endTime' mix a time zone aware and a naive timestamp.
		"""
		super().__init__(name, beginTime, endTime, duration)

		self._traceID = self._NewIdentifier(128)
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
		Enter the context and start the trace.

		The trace becomes the current trace and the current span of this thread.

		:returns:             The trace itself, so it can be named in an ``as`` clause.
		:raises TracingError: If the trace is not :attr:`~SpanState.Empty`. |br|
		                      A trace that was already timed can't be entered a second time.
		"""
		global _threadLocalData

		if self.State is not SpanState.Empty:
			ex = TracingError(f"Trace '{self._name}' is not empty and can't be entered.")
			ex.add_note(f"Its state is '{self.State.name}'.")
			ex.add_note("A trace that was already timed can't be entered a second time.")
			raise ex

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
		Exit the context and stop the trace.

		The current thread has no active trace or span afterwards. An exception leaving the ``with``-statement is
		recorded in :attr:`~Span.Exception`, and propagates.

		:param exc_type: Optional, exception type.
		:param exc_val:  Optional, exception instance.
		:param exc_tb:   Optional, exception's traceback.
		:returns:        ``None``
		"""
		global _threadLocalData

		self._stopTime =  perf_counter_ns()
		self._endTime =   datetime.now()
		self._totalTime = self._stopTime - self._startTime
		self._exception = exc_val

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

	def ToOTLPJSON(
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
					"attributes": self._ToOTLPKeyValues(
						{"service.name": self._name if serviceName is None else serviceName}.items()
					)
				},
				"scopeSpans": [{
					"scope": {"name": scopeName, "version": scopeVersion},
					"spans": self._ToOTLPJSON(),
				}],
			}]
		}

	def ToOTLPJSONString(
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
		return json_dumps(self.ToOTLPJSON(serviceName, scopeName, scopeVersion), indent=indent)

	def WriteOTLPJSONFile(
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
		``report/`` - rarely exists yet when the trace is written. Before creating them, a
		:class:`~pyTooling.Warning.DirectoryCreatedWarning` is raised to the current
		:class:`~pyTooling.Warning.WarningCollector`.

		:param jsonFile:      Path of the file to write.
		:param serviceName:   Optional, the value of the ``service.name`` resource attribute. Default: the trace's name.
		:param indent:        Optional, indentation for a human-readable file. Default: ``None``, the compact form a
		                      collector expects.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:raises ValueError:   If parameter 'jsonFile' is None.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		:raises TracingError: If the parent directories couldn't be created.
		:raises TracingError: If the file couldn't be written.
		"""
		if jsonFile is None:
			raise ValueError("Parameter 'jsonFile' is None.")
		elif not isinstance(jsonFile, Path):
			ex = TypeError("Parameter 'jsonFile' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonFile)}'.")
			raise ex

		content = self.ToOTLPJSONString(serviceName, indent, scopeName, scopeVersion)

		if not jsonFile.parent.exists():
			WarningCollector.Raise(DirectoryCreatedWarning(
				f"Directory '{jsonFile.parent}' doesn't exist and is created.",
				directory=jsonFile.parent
			))

			try:
				jsonFile.parent.mkdir(parents=True)
			except OSError as cause:
				raise TracingError(f"Directory '{jsonFile.parent}' couldn't be created.") from cause

		try:
			with jsonFile.open("w", encoding="utf-8") as file:
				file.write(content)
		except OSError as cause:
			raise TracingError(f"OTLP/JSON file '{jsonFile}' couldn't be written.") from cause

	@classmethod
	def FromOTLPJSON(cls, document: OTLPDocument, traceID: Nullable[str] = None) -> Trace:
		"""
		Construct a trace from an **OTLP/JSON** document.

		This is the inverse of :meth:`ToOTLPJSON`. The document is read into a :class:`TraceCollection` - validated
		against the schema, every trace of it, the trees reassembled from the ``parentSpanId`` references - and the
		requested trace is returned. It is a :class:`Trace` of :class:`Span` objects, also when called on a derived
		class.

		**The trace has to be complete here:** a span whose ``parentSpanId`` names a span the document doesn't carry is
		a fragment. :meth:`TraceCollection.FromOTLPJSON` keeps fragments until the document carrying their parent
		arrives.

		**What a round-trip doesn't carry back:** ``service.name`` and the instrumentation scope are parameters of
		:meth:`ToOTLPJSON`, a span's ``kind`` and ``status`` aren't read, and a :class:`tuple` attribute returns as a
		:class:`list`.

		:param document:            The OTLP/JSON document, as :func:`json.load` returns it.
		:param traceID:             Optional, identifier of the trace to read. Default: the only trace in the document.
		:returns:                   The trace, with every timespan and event below it.
		:raises TypeError:          If parameter 'traceID' is not of type :class:`str`.
		:raises TracingError:       If the document holds no spans.
		:raises TracingError:       If the document holds several traces and parameter 'traceID' names none. |br|
		                            Name the trace in parameter 'traceID', or read all with
		                            :meth:`TraceCollection.FromOTLPJSON`.
		:raises TraceNotFoundError: If the document holds no trace of identifier 'traceID'.
		:raises TracingError:       If the trace's root span is absent: the span without a 'parentSpanId' is the trace
		                            itself, and this document doesn't carry it. |br|
		                            Use :class:`TraceCollection` for a trace that isn't complete yet.
		:raises TracingError:       If a span of the trace is a fragment. |br|
		                            Use :class:`TraceCollection` to keep a fragment until its parent arrives.
		:raises TracingError:       If the document doesn't fit into a :class:`TraceCollection`, see
		                            :meth:`TraceCollection.AddOTLPJSON`.
		"""
		if traceID is not None and not isinstance(traceID, str):
			ex = TypeError("Parameter 'traceID' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(traceID)}'.")
			raise ex

		collection = TraceCollection.FromOTLPJSON(document)
		traceIDs =   list(dict.fromkeys(span._trace._traceID for span in collection._spans.values()))

		if traceID is None:
			if len(traceIDs) == 0:
				raise TracingError("OTLP/JSON document contains no spans.")
			elif len(traceIDs) > 1:
				ex = TracingError(f"OTLP/JSON document contains {len(traceIDs)} traces.")
				ex.add_note(f"Found: {', '.join(traceIDs)}.")
				ex.add_note("Name the trace in parameter 'traceID', or read all with 'TraceCollection.FromOTLPJSON()'.")
				raise ex

			traceID = traceIDs[0]
		else:
			traceID = traceID.lower()
			if traceID not in traceIDs:
				ex = TraceNotFoundError(f"OTLP/JSON document contains no trace '{traceID}'.")
				ex.add_note(f"Found: {', '.join(traceIDs)}." if len(traceIDs) > 0 else "The document contains no spans.")
				raise ex

		if (trace := collection._traces.get(traceID, None)) is None:
			ex = TracingError(f"Trace '{traceID}' has no span without a 'parentSpanId'.")
			ex.add_note("The span without a 'parentSpanId' is the trace itself, and this document doesn't carry it.")
			ex.add_note("Use 'TraceCollection.FromOTLPJSON()' to read a trace that isn't complete yet.")
			raise ex

		fragments = [fragment._spanID for fragment in collection.IterateFragmentsOf(traceID)]
		if len(fragments) > 0:
			ex = TracingError(f"{len(fragments)} span(s) of trace '{traceID}' are not part of its tree.")
			ex.add_note("A 'parentSpanId' names a span this document doesn't carry.")
			ex.add_note(f"Found: {', '.join(fragments)}.")
			ex.add_note("Use 'TraceCollection.FromOTLPJSON()' to keep such a fragment until its parent arrives.")
			raise ex

		return trace

	@classmethod
	def FromOTLPJSONString(cls, jsonString: str, traceID: Nullable[str] = None) -> Trace:
		"""
		Construct a trace from an **OTLP/JSON** document encoded as a string.

		:param jsonString:    The encoded OTLP/JSON document.
		:param traceID:       Optional, identifier of the trace to read. Default: the only trace in the document.
		:returns:             The trace, with every timespan and event below it.
		:raises ValueError:   If parameter 'jsonString' is None.
		:raises TypeError:    If parameter 'jsonString' is not of type :class:`str`.
		:raises TracingError: If the string isn't valid JSON.
		:raises TracingError: If the document isn't a trace this data model can represent, see :meth:`FromOTLPJSON`.
		"""
		if jsonString is None:
			raise ValueError("Parameter 'jsonString' is None.")
		elif not isinstance(jsonString, str):
			ex = TypeError("Parameter 'jsonString' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonString)}'.")
			raise ex

		try:
			document = json_loads(jsonString)
		except JSONDecodeError as cause:
			ex = TracingError("OTLP/JSON document isn't valid JSON.")
			ex.add_note(str(cause))
			raise ex from cause

		return cls.FromOTLPJSON(document, traceID)

	@classmethod
	def ReadOTLPJSONFile(cls, jsonFile: Path, traceID: Nullable[str] = None) -> Trace:
		"""
		Construct a trace from an **OTLP/JSON** document read from a file.

		:param jsonFile:      Path of the file to read.
		:param traceID:       Optional, identifier of the trace to read. Default: the only trace in the file.
		:returns:             The trace, with every timespan and event below it.
		:raises ValueError:   If parameter 'jsonFile' is None.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If the file couldn't be read.
		:raises TracingError: If the file isn't valid JSON.
		:raises TracingError: If the document isn't a trace this data model can represent, see :meth:`FromOTLPJSON`.
		"""
		if jsonFile is None:
			raise ValueError("Parameter 'jsonFile' is None.")
		elif not isinstance(jsonFile, Path):
			ex = TypeError("Parameter 'jsonFile' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonFile)}'.")
			raise ex

		try:
			with jsonFile.open("r", encoding="utf-8") as file:
				content = file.read()
		except OSError as cause:
			raise TracingError(f"OTLP/JSON file '{jsonFile}' couldn't be read.") from cause

		return cls.FromOTLPJSONString(content, traceID)

	def Format(self, indent: int = 0, columnSize: int = 25) -> Iterable[str]:
		"""
		Render this trace and its spans as indented lines.

		A trace or span that never started (:attr:`~SpanState.Empty`) has no duration; it shows ``--`` instead.

		:param indent:     Optional, indentation level of the trace.
		:param columnSize: Optional, column the durations are aligned at.
		:returns:          A headline, followed by one line per timespan.
		"""
		result = []
		result.append(f"{'  ' * indent}Software Execution Trace: {self._FormatDuration()}")
		result.append(f"{'  ' * indent}📉{self._name:<{columnSize - 2}} {self._FormatDuration()}")
		for span in self._spans:
			result.extend(span.Format(indent + 1, columnSize - 2))

		return result


_Trace = Trace
"""Alias of :class:`Trace` for annotations in a class with a property named ``Trace``, which the class body binds."""


@export
class Fragment(Span):
	"""
	The root of a part of a software execution trace, whose enclosing timespan hasn't arrived yet.

	OTLP exports every timespan with the identifier of its trace and of its parent, and a distributed execution is
	exported by each process separately: the timespan enclosing a span often travels in another document. While it
	hasn't arrived, neither the trace nor the parent exists as an object, so the fragment keeps both identifiers. The
	timespans below it reference the fragment as their trace (:attr:`~Span.Trace`), and its export writes the
	``parentSpanId`` it is waiting for.

	A :class:`TraceCollection` attaches a fragment to its parent as soon as that arrives; the fragment and the timespans
	below it join the parent's trace then.
	"""
	_traceID:      str  #: Identifier of the trace this fragment belongs to, as 32 hex digits.
	_parentSpanID: str  #: Identifier of the timespan this fragment is waiting for, as 16 hex digits.

	def __init__(
		self,
		name:         str,
		beginTime:    Nullable[datetime] = None,
		endTime:      Nullable[datetime] = None,
		duration:     Nullable[DurationValue] = None,
		*,
		traceID:      str,
		parentSpanID: str
	) -> None:
		"""
		Initializes the root of a fragment of a software execution trace.

		:param name:         Name of the timespan.
		:param beginTime:    Optional, recorded time when the timespan began.
		:param endTime:      Optional, recorded time when the timespan ended. Requires ``beginTime``.
		:param duration:     Optional, recorded duration of the timespan, as an alternative to ``endTime``. Requires
		                     ``beginTime``. A :class:`~datetime.timedelta`, or a number of seconds as :class:`int`
		                     (whole) or :class:`float` (fractional).
		:param traceID:      Identifier of the trace the fragment belongs to, as 32 hex digits.
		:param parentSpanID: Identifier of the timespan the fragment is waiting for, as 16 hex digits.
		:raises TypeError:   If parameter 'name' is not of type :class:`str`.
		:raises ValueError:  If parameter 'name' is empty.
		:raises TypeError:   If parameter 'beginTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError:  If parameter 'endTime' is given without parameter 'beginTime'.
		:raises TypeError:   If parameter 'endTime' is not of type :class:`~datetime.datetime`.
		:raises ValueError:  If parameter 'endTime' is before parameter 'beginTime'.
		:raises TypeError:   If parameter 'duration' is not of type :class:`~datetime.timedelta`, :class:`int` or
		                     :class:`float`.
		:raises ValueError:  If parameter 'duration' is not a finite number of seconds.
		:raises ValueError:  If parameter 'duration' is given without parameter 'beginTime'.
		:raises ValueError:  If parameter 'duration' is negative.
		:raises ValueError:  If parameter 'traceID' is None.
		:raises TypeError:   If parameter 'traceID' is not of type :class:`str`.
		:raises ValueError:  If parameter 'traceID' is not 32 hexadecimal digits.
		:raises ValueError:  If parameter 'traceID' is all zeros.
		:raises ValueError:  If parameter 'parentSpanID' is None.
		:raises TypeError:   If parameter 'parentSpanID' is not of type :class:`str`.
		:raises ValueError:  If parameter 'parentSpanID' is not 16 hexadecimal digits.
		:raises ValueError:  If parameter 'parentSpanID' is all zeros.
		:raises ValueError:  If parameters 'endTime' and 'duration' are both given.
		:raises ValueError:  If parameters 'beginTime' and 'endTime' mix a time zone aware and a naive timestamp.
		"""
		super().__init__(name, beginTime, endTime, duration)

		if traceID is None:
			raise ValueError("Parameter 'traceID' is None.")
		elif not isinstance(traceID, str):
			ex = TypeError("Parameter 'traceID' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(traceID)}'.")
			raise ex
		elif len(traceID) != 32 or traceID.strip("0123456789abcdefABCDEF") != "":
			ex = ValueError("Parameter 'traceID' is not 32 hexadecimal digits.")
			ex.add_note(f"Got '{traceID}'.")
			raise ex
		elif traceID == "0" * 32:
			raise ValueError("Parameter 'traceID' is all zeros.")

		if parentSpanID is None:
			raise ValueError("Parameter 'parentSpanID' is None.")
		elif not isinstance(parentSpanID, str):
			ex = TypeError("Parameter 'parentSpanID' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parentSpanID)}'.")
			raise ex
		elif len(parentSpanID) != 16 or parentSpanID.strip("0123456789abcdefABCDEF") != "":
			ex = ValueError("Parameter 'parentSpanID' is not 16 hexadecimal digits.")
			ex.add_note(f"Got '{parentSpanID}'.")
			raise ex
		elif parentSpanID == "0" * 16:
			raise ValueError("Parameter 'parentSpanID' is all zeros.")

		self._traceID =      traceID.lower()
		self._parentSpanID = parentSpanID.lower()
		self._trace =        self

	@readonly
	def TraceID(self) -> str:
		"""
		Read-only property to access the identifier of the trace this fragment belongs to (:attr:`_traceID`).

		:returns: Identifier of the trace, as 32 hex digits.
		"""
		return self._traceID

	@readonly
	def ParentSpanID(self) -> str:
		"""
		Read-only property to access the identifier of the timespan this fragment is waiting for (:attr:`_parentSpanID`).

		:returns: Identifier of the parent timespan, as 16 hex digits.
		"""
		return self._parentSpanID

	@classmethod
	def _NewFromOTLPJSON(cls, name: str, otlpSpan: dict[str, Any], parent: Nullable[Span]) -> Self:
		"""
		Construct the fragment :meth:`~Span._ParseOTLPJSON` fills, with the identifiers of its trace and its parent.

		:param name:     Name of the timespan.
		:param otlpSpan: The timespan as an OTLP mapping, validated by the schema.
		:param parent:   Ignored, a fragment has no parent object.
		:returns:        The new fragment.
		"""
		return cls(name, traceID=otlpSpan["traceId"], parentSpanID=otlpSpan["parentSpanId"])

	def _ToOTLPJSON(self) -> list[OTLPSpan]:
		"""
		Convert this fragment and its sub-spans to their **OTLP/JSON** representation.

		While its parent hasn't arrived, the fragment writes the ``parentSpanId`` it is waiting for, so reading the
		document back produces the same fragment rather than a second root span.

		:returns:             This fragment and every timespan below it, flattened.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		spans = super()._ToOTLPJSON()
		if self._parent is None:
			spans[0]["parentSpanId"] = self._parentSpanID

		return spans


@export
class TraceCollection(metaclass=ExtendedType, slots=True):
	"""
	A set of software execution traces, together with the timespans that haven't found their trace yet.

	It holds what **OTLP/JSON** documents carry: several traces, and parts of traces exported by different processes.

	* the **traces** whose root span has arrived, and
	* the **fragments** - timespans whose ``parentSpanId`` names a span nothing has delivered yet. A fragment has its
	  own sub-spans; only its place in the tree is unknown.

	Both are indexed by identifier. :meth:`AddOTLPJSON` attaches a fragment as soon as a document carrying its parent is
	added, in whichever order the documents arrive.
	"""
	SCHEMA_VERSION_LATEST: ClassVar[SemanticVersion] = SemanticVersion(1, 0)  #: Newest version of the OTLP/JSON schema.
	SCHEMA_FILES:          ClassVar[dict[SemanticVersion, Path]] = {
		SemanticVersion(1, 0): Path("OTLP-Traces-v1.0.schema.json"),
	}  #: JSON schema file per schema version, in :mod:`pyTooling.Resources`.

	_traces:    dict[str, Trace]     #: Traces whose root span has arrived, by trace identifier.
	_spans:     dict[str, Span]      #: Every timespan of the collection, by span identifier.
	_fragments: dict[str, Fragment]  #: Fragments waiting for their parent, by span identifier.

	def __init__(self) -> None:
		"""Initializes an empty collection of software execution traces."""
		super().__init__()

		self._traces =    {}
		self._spans =     {}
		self._fragments = {}

	@readonly
	def Traces(self) -> tuple[Trace, ...]:
		"""
		Read-only property to return the complete traces of this collection.

		:returns: The traces whose root span has arrived, in the order they were added.
		"""
		return tuple(self._traces.values())

	@readonly
	def Fragments(self) -> tuple[Fragment, ...]:
		"""
		Read-only property to return the timespans that are waiting for a parent.

		Only a fragment's **root** is listed; the sub-spans below it are part of the fragment, not fragments
		themselves.

		:returns: The root timespan of every fragment, in the order they were added.
		"""
		return tuple(self._fragments.values())

	@readonly
	def TraceCount(self) -> int:
		"""
		Return the number of complete traces in this collection.

		:returns: Number of traces.
		"""
		return len(self._traces)

	@readonly
	def SpanCount(self) -> int:
		"""
		Return the number of timespans in this collection, whether they belong to a trace or to a fragment.

		:returns: Number of timespans.
		"""
		return len(self._spans)

	@readonly
	def FragmentCount(self) -> int:
		"""
		Return the number of timespans waiting for a parent.

		:returns: Number of fragments.
		"""
		return len(self._fragments)

	@readonly
	def HasFragments(self) -> bool:
		"""
		Check if any timespan of this collection is still waiting for its parent.

		:returns: ``True``, if the collection holds at least one fragment.
		"""
		return len(self._fragments) > 0

	def TraceIDOfSpan(self, spanID: str) -> str:
		"""
		Return the identifier of the trace a timespan belongs to.

		A timespan of a fragment answers too: its trace's root span hasn't arrived, but the :class:`Fragment` keeps the
		``traceId`` the document stated.

		:param spanID:             Identifier of the timespan.
		:returns:                  Identifier of the trace the timespan belongs to.
		:raises ValueError:        If parameter 'spanID' is None.
		:raises TypeError:         If parameter 'spanID' is not of type :class:`str`.
		:raises SpanNotFoundError: If the collection contains no timespan with that identifier. |br|
		                           Add the document carrying it with :meth:`AddOTLPJSON`.
		"""
		if spanID is None:
			raise ValueError("Parameter 'spanID' is None.")
		elif not isinstance(spanID, str):
			ex = TypeError("Parameter 'spanID' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(spanID)}'.")
			raise ex

		try:
			span = self._spans[spanID.lower()]
		except KeyError as cause:
			ex = SpanNotFoundError(f"Collection contains no timespan '{spanID}'.")
			ex.add_note("Add the document carrying it with 'AddOTLPJSON'.")
			raise ex from cause

		return span._trace._traceID

	def IterateFragmentsOf(self, traceID: str) -> Iterator[Fragment]:
		"""
		Returns an iterator to iterate the fragments belonging to one trace.

		:param traceID:     Identifier of the trace.
		:returns:           Iterator to iterate the root timespan of every fragment of that trace.
		:raises ValueError: If parameter 'traceID' is None.
		:raises TypeError:  If parameter 'traceID' is not of type :class:`str`.
		"""
		if traceID is None:
			raise ValueError("Parameter 'traceID' is None.")
		elif not isinstance(traceID, str):
			ex = TypeError("Parameter 'traceID' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(traceID)}'.")
			raise ex

		wanted = traceID.lower()

		return (fragment for fragment in self._fragments.values() if fragment._traceID == wanted)

	def __getitem__(self, identifier: str) -> Union[Trace, Span]:
		"""
		Look a trace or a timespan up by its identifier.

		A trace identifier is 32 hex digits and a span identifier is 16, so which of the two indexes is searched
		follows from the length - the two can't be confused.

		:param identifier:          A trace identifier of 32, or a span identifier of 16 hex digits.
		:returns:                   The trace or the timespan registered under that identifier.
		:raises ValueError:         If parameter 'identifier' is None.
		:raises TypeError:          If parameter 'identifier' is not of type :class:`str`.
		:raises ValueError:         If parameter 'identifier' has neither 32 nor 16 digits.
		:raises TraceNotFoundError: If the collection contains no complete trace with that identifier. |br|
		                            If its root span hasn't arrived, its timespans are in :attr:`Fragments`, see
		                            :meth:`IterateFragmentsOf`. Else add the document carrying it with :meth:`AddOTLPJSON`.
		:raises SpanNotFoundError:  If the collection contains no timespan with that identifier. |br|
		                            Add the document carrying it with :meth:`AddOTLPJSON`.
		"""
		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		key = identifier.lower()
		if len(key) == 32:
			try:
				return self._traces[key]
			except KeyError as cause:
				ex = TraceNotFoundError(f"Collection contains no trace '{identifier}'.")
				if any(fragment._traceID == key for fragment in self._fragments.values()):
					ex.add_note("Its root span hasn't arrived; its timespans are in 'Fragments', see 'IterateFragmentsOf'.")
				else:
					ex.add_note("Add the document carrying it with 'AddOTLPJSON'.")
				raise ex from cause
		elif len(key) == 16:
			try:
				return self._spans[key]
			except KeyError as cause:
				ex = SpanNotFoundError(f"Collection contains no timespan '{identifier}'.")
				ex.add_note("Add the document carrying it with 'AddOTLPJSON'.")
				raise ex from cause

		ex = ValueError("Parameter 'identifier' is neither a 32 digit trace nor a 16 digit span identifier.")
		ex.add_note(f"Got '{identifier}' with {len(identifier)} digits.")
		raise ex

	def __contains__(self, identifier: str) -> bool:
		"""
		Checks if a trace or a timespan with that identifier is in this collection.

		:param identifier:  A trace identifier of 32, or a span identifier of 16 hex digits.
		:returns:           ``True``, if the collection holds it.
		:raises ValueError: If parameter 'identifier' is None.
		:raises TypeError:  If parameter 'identifier' is not of type :class:`str`.
		"""
		if identifier is None:
			raise ValueError("Parameter 'identifier' is None.")
		elif not isinstance(identifier, str):
			ex = TypeError("Parameter 'identifier' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(identifier)}'.")
			raise ex

		key = identifier.lower()

		return key in self._traces if len(key) == 32 else key in self._spans

	def __iter__(self) -> Iterator[Trace]:
		"""
		Returns an iterator to iterate the complete traces of this collection.

		:returns: Iterator to iterate all traces.
		"""
		return iter(self._traces.values())

	def __len__(self) -> int:
		"""
		Returns the number of complete traces in this collection.

		:returns: Number of traces.
		"""
		return len(self._traces)

	def AddOTLPJSON(self, document: OTLPDocument) -> Self:
		"""
		Add the traces and fragments of an **OTLP/JSON** document to this collection.

		The document is validated against the schema named by :attr:`SCHEMA_FILES` and :attr:`SCHEMA_VERSION_LATEST`,
		then read as a whole and checked against the collection **before** anything is registered, so a document that
		collides with what is already here leaves the collection as it was.

		Afterwards every fragment whose parent is now present is attached, in both directions: a fragment of this
		document finds a parent that arrived earlier, and a span of this document collects the fragments that were
		waiting for it.

		:param document:                The OTLP/JSON document, as :func:`json.load` returns it.
		:returns:                       The collection itself, so calls can be chained.
		:raises ValueError:             If parameter 'document' is None.
		:raises TypeError:              If parameter 'document' is not of type :class:`dict`.
		:raises MissingDependencyError: If package ``jsonschema`` isn't installed. |br|
		                                Install the extra ``pyTooling[tracing]``.
		:raises TracingError:           If the schema can't be read from the package resources.
		:raises TracingError:           If the document isn't valid according to the schema. |br|
		                                A note per violation names its position in the document.
		:raises DuplicateSpanError:     If two timespans of a trace carry the same ``spanId``.
		:raises DuplicateTraceError:    If more than one timespan of a trace has no ``parentSpanId``.
		:raises SpanCycleError:         If timespans of a trace reference each other in a cycle.
		:raises DuplicateSpanError:     If the collection already holds a timespan of the same identifier.
		:raises DuplicateTraceError:    If the collection already holds a trace and the document carries a second root
		                                span for it.
		:raises TracingError:           If a timespan or an event can't be read, see :meth:`Span._ParseOTLPJSON`.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")
		elif not isinstance(document, dict):
			ex = TypeError("Parameter 'document' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(document)}'.")
			raise ex

		try:
			from jsonschema import Draft202012Validator
		except ImportError as ex:  # pragma: no cover
			raise MissingDependencyError(dependency="jsonschema", extra="tracing") from ex

		schemaFile = self.SCHEMA_FILES[self.SCHEMA_VERSION_LATEST]
		try:
			schema = json_loads(readResourceFile(Resources, schemaFile))
		except (ToolingException, JSONDecodeError) as cause:
			raise TracingError(f"JSON schema '{schemaFile}' couldn't be read from the package resources.") from cause

		errors = list(Draft202012Validator(schema).iter_errors(document))
		if len(errors) > 0:
			ex = TracingError(f"OTLP/JSON document isn't valid according to JSON schema '{schemaFile}'.")
			for error in errors:
				ex.add_note(f"document/{'/'.join(str(part) for part in error.absolute_path)}: {error.message}")
			raise ex

		spansByTrace: dict[str, list[tuple[str, dict[str, Any]]]] = {}
		for resourceIndex, resourceSpans in enumerate(document.get("resourceSpans", [])):
			for scopeIndex, scopeSpans in enumerate(resourceSpans.get("scopeSpans", [])):
				for spanIndex, otlpSpan in enumerate(scopeSpans.get("spans", [])):
					path = f"document.resourceSpans[{resourceIndex}].scopeSpans[{scopeIndex}].spans[{spanIndex}]"
					spansByTrace.setdefault(otlpSpan["traceId"].lower(), []).append((path, otlpSpan))

		results = [(traceID, *self._BuildTrace(traceID, spans)) for traceID, spans in spansByTrace.items()]

		for traceID, trace, built, _ in results:
			if trace is not None and traceID in self._traces:
				ex = DuplicateTraceError(f"Collection already contains trace '{traceID}'.")
				ex.add_note("A trace has one root span, and this document carries a second one.")
				raise ex

			for spanID in built:
				if spanID in self._spans:
					ex = DuplicateSpanError(f"Collection already contains a timespan '{spanID}'.")
					ex.add_note(f"It belongs to trace '{self._spans[spanID]._trace._traceID}'.")
					raise ex

		for traceID, trace, built, fragments in results:
			if trace is not None:
				self._traces[traceID] = trace

			self._spans.update(built)
			for fragment in fragments:
				self._fragments[fragment._spanID] = fragment

		self._LinkFragments()

		return self

	def AddOTLPJSONString(self, jsonString: str) -> Self:
		"""
		Add the traces and fragments of an **OTLP/JSON** document encoded as a string to this collection.

		:param jsonString:    The encoded OTLP/JSON document.
		:returns:             The collection itself, so calls can be chained.
		:raises ValueError:   If parameter 'jsonString' is None.
		:raises TypeError:    If parameter 'jsonString' is not of type :class:`str`.
		:raises TracingError: If the string isn't valid JSON.
		:raises TracingError: If the document doesn't fit into this collection, see :meth:`AddOTLPJSON`.
		"""
		if jsonString is None:
			raise ValueError("Parameter 'jsonString' is None.")
		elif not isinstance(jsonString, str):
			ex = TypeError("Parameter 'jsonString' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonString)}'.")
			raise ex

		try:
			document = json_loads(jsonString)
		except JSONDecodeError as cause:
			ex = TracingError("OTLP/JSON document isn't valid JSON.")
			ex.add_note(str(cause))
			raise ex from cause

		return self.AddOTLPJSON(document)

	def AddOTLPJSONFile(self, jsonFile: Path) -> Self:
		"""
		Add the traces and fragments of an **OTLP/JSON** document read from a file to this collection.

		:param jsonFile:      Path of the file to read.
		:returns:             The collection itself, so calls can be chained.
		:raises ValueError:   If parameter 'jsonFile' is None.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If the file couldn't be read.
		:raises TracingError: If the file isn't valid JSON.
		:raises TracingError: If the document doesn't fit into this collection, see :meth:`AddOTLPJSON`.
		"""
		if jsonFile is None:
			raise ValueError("Parameter 'jsonFile' is None.")
		elif not isinstance(jsonFile, Path):
			ex = TypeError("Parameter 'jsonFile' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonFile)}'.")
			raise ex

		try:
			with jsonFile.open("r", encoding="utf-8") as file:
				content = file.read()
		except OSError as cause:
			raise TracingError(f"OTLP/JSON file '{jsonFile}' couldn't be read.") from cause

		return self.AddOTLPJSONString(content)

	@staticmethod
	def _BuildTrace(
		traceID: str,
		spans: list[tuple[str, dict[str, Any]]]
	) -> tuple[Nullable[Trace], dict[str, Span], list[Fragment]]:
		"""
		Build the timespans of one trace from their **OTLP/JSON** mappings.

		OTLP carries no nesting, so the tree is reassembled from the ``parentSpanId`` references. A span without a
		``parentSpanId`` is the trace itself; a span naming a span of the document becomes its sub-span; a span naming a
		span nothing delivered is the root of a **fragment**, whose own sub-spans may well be present.

		:param traceID:              Identifier of the trace.
		:param spans:                The ``(path, mapping)`` pairs of the trace's timespans, in document order.
		:returns:                    Tuple of the trace (or ``None``, if its root span is absent), every timespan built by
		                             span identifier, and the fragments.
		:raises DuplicateSpanError:  If two timespans carry the same ``spanId``.
		:raises DuplicateTraceError: If more than one timespan has no ``parentSpanId``.
		:raises SpanCycleError:      If timespans reference each other in a cycle: every other span is reachable from the
		                             trace's root span or from a fragment's root span.
		:raises TracingError:        If a timespan or an event can't be read, see :meth:`Span._ParseOTLPJSON`.
		"""
		entries:  dict[str, tuple[str, dict[str, Any]]] = {}
		parents:  dict[str, str] =                        {}
		children: dict[str, list[str]] =                  {}
		roots:    list[str] =                             []
		for path, otlpSpan in spans:
			spanID = otlpSpan["spanId"].lower()
			if spanID in entries:
				ex = DuplicateSpanError(f"Trace '{traceID}' has more than one span with identifier '{spanID}'.")
				ex.add_note(f"Found at '{entries[spanID][0]}' and at '{path}'.")
				raise ex

			entries[spanID] = (path, otlpSpan)
			if (parentSpanID := otlpSpan.get("parentSpanId", "")) == "":
				roots.append(spanID)
			else:
				parents[spanID] = parentSpanID.lower()
				children.setdefault(parentSpanID.lower(), []).append(spanID)

		if len(roots) > 1:
			ex = DuplicateTraceError(f"Trace '{traceID}' has {len(roots)} spans without a 'parentSpanId'.")
			ex.add_note("The span without a 'parentSpanId' is the trace itself, so there is at most one of them.")
			ex.add_note(f"Found: {', '.join(entries[spanID][0] for spanID in roots)}.")
			raise ex

		trace:     Nullable[Trace] =       None
		built:     dict[str, Span] =       {}
		pending:   list[Span] =            []
		fragments: list[Fragment] =         []
		if len(roots) == 1:
			path, otlpSpan = entries[roots[0]]
			trace =          Trace._ParseOTLPJSON(otlpSpan, path)
			trace._traceID = traceID
			built[trace._spanID] = trace
			pending.append(trace)

		for spanID, parentSpanID in parents.items():
			if parentSpanID not in entries:
				path, otlpSpan = entries[spanID]
				fragment =       Fragment._ParseOTLPJSON(otlpSpan, path)
				built[spanID] =  fragment
				fragments.append(fragment)
				pending.append(fragment)

		while len(pending) > 0:
			parent = pending.pop()
			for spanID in children.get(parent._spanID, []):
				path, otlpSpan = entries[spanID]
				timespan =       Span._ParseOTLPJSON(otlpSpan, path, parent=parent)
				built[spanID] =  timespan
				pending.append(timespan)

		if len(built) != len(entries):
			unreachable = [path for spanID, (path, _) in entries.items() if spanID not in built]
			ex = SpanCycleError(f"{len(unreachable)} span(s) of trace '{traceID}' reference each other in a cycle.")
			ex.add_note("Every other span is reachable from the trace's root span or from a fragment's root span.")
			ex.add_note(f"Found: {', '.join(unreachable)}.")
			raise ex

		return trace, built, fragments

	def _LinkFragments(self) -> None:
		"""
		Attach every fragment whose parent timespan is now part of this collection.

		The sub-spans of a timespan that received a fragment are sorted by start time, so a trace reassembled from
		several documents doesn't depend on the order they were added in. A timespan without a start time sorts last.
		"""
		for fragment in [fragment for fragment in self._fragments.values() if fragment._parentSpanID in self._spans]:
			parent = self._spans[fragment._parentSpanID]
			parent._AddSpan(fragment)
			del self._fragments[fragment._spanID]

			# A fragment is attached when its parent arrives, which is not the order the timespans ran in. Sorting
			# the siblings by start time makes a reassembled trace read like a local one, and makes the result
			# independent of the order the documents were added in.
			parent._spans.sort(key=lambda span: (span._beginTime is None, span._beginTime or datetime.min))

			# '_AddSpan' sets the fragment's trace; everything below it still carries the trace it had while it was
			# a fragment - which is 'None', because a fragment isn't part of a trace.
			pending = [fragment]
			while len(pending) > 0:
				current = pending.pop()
				for subSpan in current._spans:
					subSpan._trace = current._trace
					pending.append(subSpan)

	@classmethod
	def FromOTLPJSON(cls, document: OTLPDocument) -> Self:
		"""
		Construct a collection from an **OTLP/JSON** document.

		Unlike :meth:`Trace.FromOTLPJSON`, this reads *everything* the document carries: several traces, and
		timespans whose parent is missing. Nothing has to be complete.

		:param document:      The OTLP/JSON document, as :func:`json.load` returns it.
		:returns:             A collection of the document's traces and fragments.
		:raises TracingError: If the spans of a trace don't form a tree: two root spans, or a cycle.
		:raises TracingError: If a mandatory field is missing or is of the wrong type.
		"""
		return cls().AddOTLPJSON(document)

	@classmethod
	def FromOTLPJSONString(cls, jsonString: str) -> Self:
		"""
		Construct a collection from an **OTLP/JSON** document encoded as a string.

		:param jsonString:    The encoded OTLP/JSON document.
		:returns:             A collection of the document's traces and fragments.
		:raises TypeError:    If parameter 'jsonString' is not of type :class:`str`.
		:raises TracingError: If the string isn't valid JSON.
		:raises TracingError: If the document isn't a set of traces this data model can represent.
		"""
		return cls().AddOTLPJSONString(jsonString)

	@classmethod
	def ReadOTLPJSONFile(cls, jsonFile: Path) -> Self:
		"""
		Construct a collection from an **OTLP/JSON** document read from a file.

		:param jsonFile:      Path of the file to read.
		:returns:             A collection of the document's traces and fragments.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If the file couldn't be read, or isn't valid JSON.
		:raises TracingError: If the document isn't a set of traces this data model can represent.
		"""
		return cls().AddOTLPJSONFile(jsonFile)

	def _RootsByTrace(self) -> dict[str, list[Span]]:
		"""
		Group the timespans that start a subtree by the trace they belong to.

		:returns: Dictionary of a trace identifier to its root span - if it has arrived - followed by the root of
		          every fragment of that trace.
		"""
		roots: dict[str, list[Span]] = {traceID: [trace] for traceID, trace in self._traces.items()}
		for fragment in self._fragments.values():
			roots.setdefault(fragment._traceID, []).append(fragment)

		return roots

	def ToOTLPJSON(self, scopeName: str = OTLP_SCOPE_NAME, scopeVersion: str = __version__) -> OTLPDocument:
		"""
		Convert this collection to an **OTLP/JSON** document.

		Every trace becomes one ``resourceSpans`` entry, and a fragment is written into the entry of the trace it
		belongs to - with the ``parentSpanId`` it is waiting for, so reading the document back produces the same
		fragment rather than a second root span.

		A trace whose root span never arrived has no name to report, so its ``service.name`` is its trace identifier.

		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:returns:             The collection as an OTLP/JSON document, ready for :func:`json.dump`.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		resourceSpans: list[OTLPResourceSpans] = []
		for traceID, roots in self._RootsByTrace().items():
			trace =       self._traces.get(traceID, None)
			serviceName = traceID if trace is None else trace._name
			spans =       [
				span
				for root in roots
				for span in root._ToOTLPJSON()
			]

			resourceSpans.append({
				"resource":   {"attributes": TraceElement._ToOTLPKeyValues({"service.name": serviceName}.items())},
				"scopeSpans": [{"scope": {"name": scopeName, "version": scopeVersion}, "spans": spans}],
			})

		return {"resourceSpans": resourceSpans}

	def ToOTLPJSONString(
		self,
		indent: Nullable[int] = None,
		scopeName: str = OTLP_SCOPE_NAME,
		scopeVersion: str = __version__
	) -> str:
		"""
		Convert this collection to an **OTLP/JSON** document and encode it as a string.

		:param indent:        Optional, indentation for a human-readable document. Default: ``None``, the compact
		                      form a collector expects.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:returns:             The OTLP/JSON document, encoded.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		"""
		return json_dumps(self.ToOTLPJSON(scopeName, scopeVersion), indent=indent)

	def WriteOTLPJSONFile(
		self,
		jsonFile: Path,
		indent: Nullable[int] = None,
		scopeName: str = OTLP_SCOPE_NAME,
		scopeVersion: str = __version__
	) -> None:
		"""
		Write this collection to a file as an **OTLP/JSON** document.

		Missing parent directories are created. Before creating them, a
		:class:`~pyTooling.Warning.DirectoryCreatedWarning` is raised to the current
		:class:`~pyTooling.Warning.WarningCollector`.

		:param jsonFile:      Path of the file to write.
		:param indent:        Optional, indentation for a human-readable file. Default: ``None``, the compact form
		                      a collector expects.
		:param scopeName:     Optional, the instrumentation scope the spans are reported under.
		                      Default: :data:`OTLP_SCOPE_NAME`.
		:param scopeVersion:  Optional, the version of that instrumentation scope. Default: pyTooling's version.
		:raises ValueError:   If parameter 'jsonFile' is None.
		:raises TypeError:    If parameter 'jsonFile' is not of type :class:`~pathlib.Path`.
		:raises TracingError: If an attribute is of a type OTLP's ``AnyValue`` can't carry.
		:raises TracingError: If the parent directories couldn't be created.
		:raises TracingError: If the file couldn't be written.
		"""
		if jsonFile is None:
			raise ValueError("Parameter 'jsonFile' is None.")
		elif not isinstance(jsonFile, Path):
			ex = TypeError("Parameter 'jsonFile' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(jsonFile)}'.")
			raise ex

		content = self.ToOTLPJSONString(indent, scopeName, scopeVersion)

		if not jsonFile.parent.exists():
			WarningCollector.Raise(DirectoryCreatedWarning(
				f"Directory '{jsonFile.parent}' doesn't exist and is created.",
				directory=jsonFile.parent
			))

			try:
				jsonFile.parent.mkdir(parents=True)
			except OSError as cause:
				raise TracingError(f"Directory '{jsonFile.parent}' couldn't be created.") from cause

		try:
			with jsonFile.open("w", encoding="utf-8") as file:
				file.write(content)
		except OSError as cause:
			raise TracingError(f"OTLP/JSON file '{jsonFile}' couldn't be written.") from cause

	def Format(self, columnSize: int = 25) -> Iterable[str]:
		"""
		Render every trace and every fragment of this collection as indented lines.

		:param columnSize: Optional, column the durations are aligned at.
		:returns:          One block of lines per trace, followed by the fragments that are still waiting.
		"""
		result: list[str] = []
		for trace in self._traces.values():
			result.extend(trace.Format(0, columnSize))

		if len(self._fragments) > 0:
			result.append(f"Fragments: {self.FragmentCount}")
			for fragment in self._fragments.values():
				result.append(f"  ⌛ waiting for span {fragment._parentSpanID}")
				result.extend(fragment.Format(2, columnSize))

		return result

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this collection.

		:returns: The number of traces, timespans and fragments.
		"""
		return f"TraceCollection: {len(self._traces)} traces, {len(self._spans)} spans, {len(self._fragments)} fragments"

	def __str__(self) -> str:
		"""
		Return a string representation of the collection.

		:returns: The number of traces, and of fragments if it has any.
		"""
		traces = f"{len(self._traces)} traces"

		return traces if len(self._fragments) == 0 else f"{traces} + {len(self._fragments)} fragments"
