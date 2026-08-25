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
"""
Export a :class:`~pyTooling.Tracing.Trace` as **OTLP/JSON**, the OpenTelemetry Protocol's JSON encoding.

One format serves both targets named in the request: OpenTelemetry collectors accept OTLP natively, and Jaeger has
accepted OTLP since v1.35, so a trace written here can be posted to either without a translation step.

.. admonition:: ``example.py``

   .. code-block:: python

      from pyTooling.Tracing               import Trace, Span
      from pyTooling.Tracing.OpenTelemetry import WriteOTLP

      with Trace("build") as trace:
        with Span("compile"):
          ...

      WriteOTLP(trace, "trace.json", serviceName="myProgram")

   .. code-block:: bash

      curl -X POST -H "Content-Type: application/json" -d @trace.json http://localhost:4318/v1/traces

.. hint::

   See :ref:`high-level help <TRACING/OTLP>` for the mapping and its limits.
"""
from datetime  import datetime
from json      import dump as json_dump
from pathlib   import Path
from secrets   import randbits
from typing    import Any, Union, Optional as Nullable

from pyTooling.Common     import __version__
from pyTooling.Decorators import export
from pyTooling.Tracing    import Event, Span, Trace


SCOPE_NAME = "pyTooling.Tracing"   #: Instrumentation scope reported for every exported span.


@export
def toUnixNano(timestamp: datetime) -> str:
	"""
	Convert a timestamp to nanoseconds since the Unix epoch.

	OTLP/JSON encodes a 64-bit integer as a **string**, because JSON numbers cannot carry 64 bits exactly. This is
	proto3's JSON mapping, not a quirk of this exporter.

	:param timestamp: The timestamp to convert.
	:returns:         Nanoseconds since the Unix epoch, as a decimal string.
	"""
	return str(int(timestamp.timestamp() * 1_000_000_000))


@export
def toAttributeValue(value: Any) -> dict[str, Any]:
	"""
	Wrap a Python value in OTLP's ``AnyValue`` representation.

	:param value: The value to wrap.
	:returns:     The value, wrapped in the one-key mapping OTLP expects for its type.
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
	elif isinstance(value, (list, tuple)):
		return {"arrayValue": {"values": [toAttributeValue(element) for element in value]}}

	return {"stringValue": str(value)}


@export
def toAttributes(attributes: dict[str, Any]) -> list[dict[str, Any]]:
	"""
	Convert a dictionary of attributes to OTLP's list of key-value pairs.

	:param attributes: The attributes to convert.
	:returns:          One ``{"key": ..., "value": ...}`` mapping per attribute.
	"""
	return [{"key": key, "value": toAttributeValue(value)} for key, value in attributes.items()]


def _newIdentifier(bits: int) -> str:
	"""
	Generate a random trace or span identifier.

	OTLP/JSON encodes both as **hex** rather than base64, which is where it deviates from proto3's JSON mapping.
	An all-zero identifier is invalid, so it is drawn again in that case.

	:param bits: Width of the identifier: 128 for a trace, 64 for a span.
	:returns:    The identifier as a lower-case hex string.
	"""
	while (identifier := randbits(bits)) == 0:  # pragma: no cover
		pass

	return f"{identifier:0{bits // 4}x}"


def _convertEvent(event: Event, fallbackTime: Nullable[datetime]) -> dict[str, Any]:
	"""
	Convert one event to its OTLP representation.

	An :class:`~pyTooling.Tracing.Event` constructed without an explicit ``time`` has none - the constructor does not
	stamp the current time - and OTLP has no way to say *unknown*: a missing ``timeUnixNano`` reads as the Unix
	epoch. The enclosing span's start time is used instead, which places the event inside the span it belongs to.

	:param event:        The event to convert.
	:param fallbackTime: Time to use when the event carries none, usually the enclosing span's start time.
	:returns:            The event as an OTLP mapping.
	"""
	converted = {
		"name": event.Name,
	}
	if (time := event.Time if event.Time is not None else fallbackTime) is not None:
		converted["timeUnixNano"] = toUnixNano(time)
	if (attributes := toAttributes(dict(event))) != []:
		converted["attributes"] = attributes

	return converted


def _convertSpan(span: Span, traceID: str, parentSpanID: Nullable[str], spans: list[dict[str, Any]]) -> None:
	"""
	Convert one span and its sub-spans, appending each to a flat list.

	OTLP has no nesting: the hierarchy is carried by ``parentSpanId``, so the tree is flattened here and reassembled
	by the receiver.

	:param span:         The span to convert.
	:param traceID:      Identifier shared by every span of the trace.
	:param parentSpanID: Identifier of the enclosing span, or ``None`` for the trace itself.
	:param spans:        The list every converted span is appended to.
	"""
	spanID = _newIdentifier(64)

	converted: dict[str, Any] = {
		"traceId":           traceID,
		"spanId":            spanID,
		"name":              span.Name,
		"kind":              1,                # SPAN_KIND_INTERNAL
	}
	if parentSpanID is not None:
		converted["parentSpanId"] = parentSpanID

	if span.StartTime is not None:
		startTimeUnixNano = int(toUnixNano(span.StartTime))
		converted["startTimeUnixNano"] = str(startTimeUnixNano)

		# the wall clock has microsecond resolution while the duration comes from a nanosecond performance counter, so
		# the end is computed from the duration rather than read from a second wall-clock sample. 'Duration' is in
		# seconds; OTLP wants nanoseconds.
		converted["endTimeUnixNano"] = str(startTimeUnixNano + int(span.Duration * 1_000_000_000))

	if (attributes := toAttributes(dict(span))) != []:
		converted["attributes"] = attributes

	if (events := [_convertEvent(event, span.StartTime) for event in span.IterateEvents()]) != []:
		converted["events"] = events

	spans.append(converted)

	for subSpan in span.IterateSubSpans():
		_convertSpan(subSpan, traceID, spanID, spans)


@export
def ToOTLP(trace: Trace, serviceName: Nullable[str] = None) -> dict[str, Any]:
	"""
	Convert a software execution trace to an OTLP/JSON document.

	Every span of the trace shares one generated ``traceId``, and the tree is flattened into a list whose
	``parentSpanId`` references carry the structure - which is how OTLP represents a trace.

	:param trace:       The trace to convert.
	:param serviceName: Optional, the value of the ``service.name`` resource attribute, which is the name a backend
	                    shows the trace under. Default: the trace's name.
	:returns:           The trace as an OTLP/JSON document, ready for :func:`json.dump`.
	:raises TypeError:  If parameter 'trace' is not of type :class:`~pyTooling.Tracing.Trace`.
	"""
	if not isinstance(trace, Trace):
		ex = TypeError("Parameter 'trace' is not of type 'Trace'.")
		ex.add_note(f"Got type '{trace.__class__.__name__}'.")
		raise ex

	spans: list[dict[str, Any]] = []
	_convertSpan(trace, _newIdentifier(128), None, spans)

	return {
		"resourceSpans": [{
			"resource": {
				"attributes": toAttributes({"service.name": trace.Name if serviceName is None else serviceName})
			},
			"scopeSpans": [{
				"scope": {"name": SCOPE_NAME, "version": __version__},
				"spans": spans,
			}],
		}]
	}


@export
def WriteOTLP(
	trace: Trace,
	path: Union[str, Path],
	serviceName: Nullable[str] = None,
	indent: Nullable[int] = None
) -> None:
	"""
	Write a software execution trace to a file as OTLP/JSON.

	:param trace:       The trace to write.
	:param path:        Path of the file to write.
	:param serviceName: Optional, the value of the ``service.name`` resource attribute. Default: the trace's name.
	:param indent:      Optional, indentation for a human-readable file. Default: ``None``, the compact form a
	                    collector is posted.
	:raises TypeError:  If parameter 'trace' is not of type :class:`~pyTooling.Tracing.Trace`.
	"""
	document = ToOTLP(trace, serviceName)

	with Path(path).open("w", encoding="utf-8") as file:
		json_dump(document, file, indent=indent)
