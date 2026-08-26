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
Unit tests for the **OTLP/JSON** export and import of :mod:`pyTooling.Tracing`.
"""
from datetime  import datetime, timedelta
from json      import dumps as json_dumps, loads as json_loads
from math      import inf, isnan
from pathlib   import Path
from tempfile  import TemporaryDirectory
from time      import sleep
from unittest  import mock

from pyTooling.Common  import __version__
from pyTooling.Testing import Testcase
from pyTooling.Tracing import OTLP_SCOPE_NAME, Event, Span, Trace, TraceCollection, TracingError, _newIdentifier
from pyTooling.Tracing import _toAttributeValue
from pyTooling.Tracing import _fromAttributes, _fromAttributeValue, _fromUnixNano

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def _exampleTrace() -> Trace:
	"""
	Build a trace with two nested spans, attributes of every kind, and an event.

	:returns: The finished trace.
	"""
	with Trace("build") as trace:
		trace["version"] = "10.0.0"
		with Span("compile") as compileSpan:
			compileSpan["files"] = 12
			compileSpan["optimized"] = True
			compileSpan["ratio"] = 0.5
			compileSpan["targets"] = ["a", "b"]
			Event("cache miss", parent=compileSpan)
			sleep(0.001)
		with Span("link"):
			pass

	return trace


class AttributeValues(Testcase):
	"""A Python value is wrapped in the one-key mapping OTLP expects for its type."""

	def test_String(self) -> None:
		self.assertEqual({"stringValue": "text"}, _toAttributeValue("text"))

	def test_Integer(self) -> None:
		"""A 64-bit integer is a string in OTLP/JSON, because JSON numbers cannot carry 64 bits exactly."""
		self.assertEqual({"intValue": "42"}, _toAttributeValue(42))

	def test_BooleanIsNotAnInteger(self) -> None:
		"""``bool`` is a subclass of ``int``, so the order of the checks decides this one."""
		self.assertEqual({"boolValue": True}, _toAttributeValue(True))

	def test_Float(self) -> None:
		self.assertEqual({"doubleValue": 0.5}, _toAttributeValue(0.5))

	def test_List(self) -> None:
		self.assertEqual(
			{"arrayValue": {"values": [{"stringValue": "a"}, {"intValue": "1"}]}},
			_toAttributeValue(["a", 1])
		)

	def test_TupleIsAnArrayToo(self) -> None:
		self.assertEqual({"arrayValue": {"values": [{"intValue": "1"}]}}, _toAttributeValue((1,)))

	def test_Dictionary(self) -> None:
		"""OTLP's 'KeyValueList' is a mapping, and it nests - a value of it is an 'AnyValue' again."""
		self.assertEqual(
			{"kvlistValue": {"values": [
				{"key": "a", "value": {"intValue": "1"}},
				{"key": "b", "value": {"arrayValue": {"values": [{"boolValue": True}]}}},
			]}},
			_toAttributeValue({"a": 1, "b": [True]})
		)

	def test_Bytes(self) -> None:
		"""'bytesValue' is a 'bytes' field in proto3, and proto3's JSON mapping encodes those as base64."""
		self.assertEqual({"bytesValue": "AAH/"}, _toAttributeValue(b"\x00\x01\xff"))

	def test_AnUnsupportedTypeIsRejected(self) -> None:
		"""A silent 'str(value)' would put a Python repr into a document a backend then indexes."""
		with self.assertRaises(TracingError) as exceptionCapture:
			_toAttributeValue(object())

		self.assertEqual(
			"Attribute value of type 'object' can't be represented in OTLP.",
			str(exceptionCapture.exception)
		)
		self.assertEqual(
			["Supported are: bool, int, float, str, bytes, and a list, tuple or dict of these."],
			exceptionCapture.exception.__notes__
		)

	def test_AnUnsupportedTypeIsRejectedInsideAContainer(self) -> None:
		with self.assertRaises(TracingError):
			_toAttributeValue(["fine", None])


class Document(Testcase):
	"""The exported document's shape."""

	def test_TheEnvelopeNamesTheServiceAndTheScope(self) -> None:
		document = _exampleTrace().ToOTLPJSON(serviceName="myProgram")
		resourceSpans = document["resourceSpans"][0]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			resourceSpans["resource"]["attributes"]
		)
		self.assertEqual(OTLP_SCOPE_NAME, resourceSpans["scopeSpans"][0]["scope"]["name"])

	def test_TheServiceNameDefaultsToTheTracesName(self) -> None:
		document = _exampleTrace().ToOTLPJSON()

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "build"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_OnlyATraceConvertsToADocument(self) -> None:
		"""A lone span is not an OTLP document - it has no 'traceId' and no service to be reported under."""

		self.assertFalse(hasattr(Span("not a trace"), "ToOTLPJSON"))
		self.assertTrue(hasattr(Trace("a trace"), "ToOTLPJSON"))


class Spans(Testcase):
	"""OTLP has no nesting, so the tree is flattened and carried by 'parentSpanId'."""

	@staticmethod
	def _Spans(document) -> dict:
		"""
		Index the exported spans by name.

		:param document: The exported document.
		:returns:        Dictionary of a span's name to the span.
		"""
		return {span["name"]: span for span in document["resourceSpans"][0]["scopeSpans"][0]["spans"]}

	def test_EverySpanIsExported(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertEqual({"build", "compile", "link"}, set(spans))

	def test_AllSpansShareOneTraceIdentifier(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		identifiers = {span["traceId"] for span in spans.values()}

		self.assertEqual(1, len(identifiers))
		self.assertEqual(32, len(identifiers.pop()), "A trace identifier is 16 bytes, hex-encoded.")

	def test_TheHierarchyIsCarriedByParentSpanId(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertNotIn("parentSpanId", spans["build"], "The trace itself has no parent.")
		self.assertEqual(spans["build"]["spanId"], spans["compile"]["parentSpanId"])
		self.assertEqual(spans["build"]["spanId"], spans["link"]["parentSpanId"])

	def test_ASpanIdentifierIsEightBytes(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		for name, span in spans.items():
			with self.subTest(span=name):
				self.assertEqual(16, len(span["spanId"]))
				self.assertEqual(span["spanId"], span["spanId"].lower(), "OTLP/JSON uses lower-case hex.")

	def test_TheDurationSurvives(self) -> None:
		"""A span's duration is in seconds while OTLP wants nanoseconds, which is the easy factor to get wrong."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		compileSpan = spans["compile"]
		duration = int(compileSpan["endTimeUnixNano"]) - int(compileSpan["startTimeUnixNano"])

		self.assertGreater(duration, 1_000_000, "The span slept for a millisecond, so it lasted at least that.")
		self.assertLess(duration, 10_000_000_000, "A millisecond must not be reported as seconds.")

	def test_TheDurationIsWrittenAsItWasMeasured(self) -> None:
		"""'Duration' is the counter's nanoseconds divided by 1e9, and multiplying that back loses up to one of them."""
		with Trace("trace") as trace:
			with Span("span") as span:
				sleep(0.001)

		exported = self._Spans(trace.ToOTLPJSON())["span"]

		self.assertEqual(span._totalTime, int(exported["endTimeUnixNano"]) - int(exported["startTimeUnixNano"]))

	def test_TheTimestampsAreStrings(self) -> None:
		"""proto3's JSON mapping encodes a 64-bit integer as a string."""
		for span in self._Spans(_exampleTrace().ToOTLPJSON()).values():
			with self.subTest(span=span["name"]):
				self.assertIsInstance(span["startTimeUnixNano"], str)
				self.assertIsInstance(span["endTimeUnixNano"], str)

	def test_AttributesAreExported(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		attributes = {entry["key"]: entry["value"] for entry in spans["compile"]["attributes"]}

		self.assertEqual({"intValue": "12"}, attributes["files"])
		self.assertEqual({"boolValue": True}, attributes["optimized"])
		self.assertEqual({"doubleValue": 0.5}, attributes["ratio"])

	def test_ASpanWithoutAttributesHasNoAttributeKey(self) -> None:
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertNotIn("attributes", spans["link"])
		self.assertNotIn("events", spans["link"])


class Events(Testcase):
	"""An event belongs to the span it was created in."""

	def test_TheEventIsExported(self) -> None:
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}
		events = spans["compile"]["events"]

		self.assertEqual(1, len(events))
		self.assertEqual("cache miss", events[0]["name"])

	def test_ItsAttributesAreExported(self) -> None:
		with Trace("trace") as trace:
			with Span("span") as span:
				event = Event("cache miss", parent=span)
				event["key"] = "value"

		spans = {
			exported["name"]: exported
			for exported in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertListEqual(
			[{"key": "key", "value": {"stringValue": "value"}}],
			spans["span"]["events"][0]["attributes"]
		)

	def test_AnEventWithoutAttributesHasNoAttributeKey(self) -> None:
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertNotIn("attributes", spans["compile"]["events"][0])

	def test_AnEventWithoutATimeIsStampedWithTheCurrentTime(self) -> None:
		"""The constructor stamps the current time, so an event always has one - OTLP reads a missing one as the epoch."""
		# The bracket is read from the same clock as the stamp. A span's 'endTimeUnixNano' would be the wrong bound:
		# it is its wall-clock start plus a duration measured by the performance counter, so on a platform with a
		# coarse wall clock it can land before an event stamped inside the span.
		before = datetime.now()
		with Trace("trace") as trace:
			with Span("span") as span:
				event = Event("no time of its own", parent=span)
		after = datetime.now()

		spans = {
			exported["name"]: exported
			for exported in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertGreaterEqual(event.Time, before)
		self.assertLessEqual(event.Time, after)
		self.assertEqual(
			str(int(event.Time.timestamp() * 1_000_000_000)),
			spans["span"]["events"][0]["timeUnixNano"]
		)

	def test_AnEventWithATimeKeepsIt(self) -> None:
		time = datetime(2026, 8, 25, 12, 0, 0)
		with Trace("trace") as trace:
			with Span("span") as span:
				Event("stamped", time=time, parent=span)

		spans = {
			exported["name"]: exported
			for exported in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual(str(int(time.timestamp() * 1_000_000_000)), spans["span"]["events"][0]["timeUnixNano"])


class WrittenFile(Testcase):
	"""The document reaches a file as JSON."""

	def test_TheFileIsValidJSONAndRoundTrips(self) -> None:
		trace = _exampleTrace()

		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			trace.WriteOTLPJSONFile(path, serviceName="myProgram", indent=2)

			document = json_loads(path.read_text(encoding="utf-8"))

		self.assertEqual(trace.ToOTLPJSON("myProgram")["resourceSpans"][0]["scopeSpans"][0]["scope"],
		                 document["resourceSpans"][0]["scopeSpans"][0]["scope"])
		self.assertEqual(3, len(document["resourceSpans"][0]["scopeSpans"][0]["spans"]))


class Encoding(Testcase):
	"""The two ways a trace hands its document out, beside the mapping itself."""

	def test_TheStringIsTheEncodedDocument(self) -> None:
		trace = _exampleTrace()

		self.assertEqual(trace.ToOTLPJSON(), json_loads(trace.ToOTLPJSONString()))

	def test_TheCompactFormIsTheDefault(self) -> None:
		"""That is what a collector expects; an indent is for a human reading the file."""

		trace = _exampleTrace()

		self.assertNotIn("\n", trace.ToOTLPJSONString())
		self.assertIn("\n", trace.ToOTLPJSONString(indent=2))

	def test_TheServiceNameReachesTheString(self) -> None:
		document = json_loads(_exampleTrace().ToOTLPJSONString(serviceName="myProgram"))

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_TheDirectoryIsCreated(self) -> None:
		"""'report/' rarely exists when a pipeline asks for a trace inside it."""

		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			_exampleTrace().WriteOTLPJSONFile(path)

			self.assertTrue(path.exists())

	def test_APathIsAPath(self) -> None:
		with TemporaryDirectory() as directory:
			with self.assertRaises(TypeError) as exceptionCapture:
				_exampleTrace().WriteOTLPJSONFile(f"{directory}/trace.json")

		self.assertEqual("Parameter 'jsonFile' is not of type 'Path'.", str(exceptionCapture.exception))
		self.assertEqual(["Got type 'str'."], exceptionCapture.exception.__notes__)


class Identifiers(Testcase):
	"""An all-zero identifier is invalid in OTLP, so it is drawn again - but not forever."""

	def test_AZeroIsDrawnAgain(self) -> None:
		with mock.patch("pyTooling.Tracing.randbits", side_effect=(0, 0, 0x0123456789ABCDEF)):
			identifier = _newIdentifier(64)

		self.assertEqual("0123456789abcdef", identifier)

	def test_OnlyZerosRaisesATracingError(self) -> None:
		with mock.patch("pyTooling.Tracing.randbits", return_value=0):
			with self.assertRaises(TracingError) as exceptionCapture:
				_newIdentifier(64)

		self.assertEqual("Couldn't draw a non-zero 64-bit random identifier.", str(exceptionCapture.exception))
		self.assertEqual(["Tried 4 times."], exceptionCapture.exception.__notes__)


class WriteErrors(Testcase):
	"""A filesystem error is reported as a :exc:`~pyTooling.Tracing.TracingError` naming what failed."""

	def test_AnUncreatableDirectoryIsReported(self) -> None:
		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			with mock.patch("pathlib.Path.mkdir", side_effect=PermissionError("denied")):
				with self.assertRaises(TracingError) as exceptionCapture:
					_exampleTrace().WriteOTLPJSONFile(path)

		self.assertEqual(f"Directory '{path.parent}' couldn't be created.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)

	def test_AnUnwritableFileIsReported(self) -> None:
		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			with mock.patch("pathlib.Path.open", side_effect=PermissionError("denied")):
				with self.assertRaises(TracingError) as exceptionCapture:
					_exampleTrace().WriteOTLPJSONFile(path)

		self.assertEqual(f"OTLP/JSON file '{path}' couldn't be written.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)


class Identity(Testcase):
	"""The identifiers belong to the data model, not to a conversion."""

	def test_ATraceKeepsItsIdentifierAcrossConversions(self) -> None:
		"""This is what the by-call generation couldn't do: two exports describe one trace, not two."""
		trace = _exampleTrace()

		first = trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		second = trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]

		self.assertEqual(first, second)
		self.assertEqual(trace.TraceID, first[0]["traceId"])

	def test_ASpanKnowsItsOwnIdentifierAndItsTrace(self) -> None:
		with Trace("trace") as trace:
			with Span("span") as span:
				pass

		exported = {
			converted["name"]: converted
			for converted in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertIs(trace, span.Trace)
		self.assertEqual(span.SpanID, exported["span"]["spanId"])
		self.assertEqual(trace.TraceID, exported["span"]["traceId"])

	def test_TheParentSpanIdIsReadOffTheParentRelation(self) -> None:
		with Trace("trace") as trace:
			with Span("outer") as outer:
				with Span("inner") as inner:
					pass

		exported = {
			converted["name"]: converted
			for converted in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertIs(outer, inner.Parent)
		self.assertEqual(outer.SpanID, exported["inner"]["parentSpanId"])
		self.assertEqual(trace.SpanID, exported["outer"]["parentSpanId"])
		self.assertNotIn("parentSpanId", exported["trace"], "The trace itself has no parent.")

	def test_EveryIdentifierOfATraceIsDistinct(self) -> None:
		spans = _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		identifiers = [span["spanId"] for span in spans]

		self.assertEqual(len(identifiers), len(set(identifiers)))

	def test_ASpanOutsideATraceCannotBeExported(self) -> None:
		"""A lone span has no 'traceId' to carry, and OTLP has no way of saying so."""
		span = Span("orphan")

		self.assertIsNone(span.Trace)
		with self.assertRaises(TracingError) as exceptionCapture:
			span._ToOTLPJSON()

		self.assertEqual("Timespan 'orphan' is not part of a trace.", str(exceptionCapture.exception))

	def test_TheConversionReturnsTheFlattenedList(self) -> None:
		"""Every level returns its own list, so no caller passes one in to be filled."""
		trace = _exampleTrace()
		spans = trace._ToOTLPJSON()

		self.assertIsInstance(spans, list)
		self.assertListEqual(["build", "compile", "link"], [span["name"] for span in spans])


class InstrumentationScope(Testcase):
	"""Which library the spans are reported as coming from."""

	def test_ThePyToolingScopeIsTheDefault(self) -> None:
		scope = _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual(OTLP_SCOPE_NAME, scope["name"])
		self.assertEqual(__version__, scope["version"])

	def test_ItIsInjectedRatherThanPatched(self) -> None:
		"""A program wrapping pyTooling's tracing reports its own name, without touching the module."""
		scope = _exampleTrace().ToOTLPJSON(
			scopeName="myProgram.Instrumentation",
			scopeVersion="2.1.0"
		)["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual({"name": "myProgram.Instrumentation", "version": "2.1.0"}, scope)

	def test_ItReachesTheStringAndTheFile(self) -> None:
		trace = _exampleTrace()

		document = json_loads(trace.ToOTLPJSONString(scopeName="myProgram", scopeVersion="2.1.0"))
		self.assertEqual("myProgram", document["resourceSpans"][0]["scopeSpans"][0]["scope"]["name"])

		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			trace.WriteOTLPJSONFile(path, scopeName="myProgram", scopeVersion="2.1.0")
			written = json_loads(path.read_text(encoding="utf-8"))

		self.assertEqual("myProgram", written["resourceSpans"][0]["scopeSpans"][0]["scope"]["name"])


TRACE_ID = "0123456789abcdef0123456789abcdef"
"""A syntactically valid trace identifier, for the documents assembled by hand below."""


def _span(name: str, spanId: str, parentSpanId: str = None, traceId: str = TRACE_ID, **fields) -> dict:
	"""
	Assemble one OTLP span mapping.

	:param name:         Name of the timespan.
	:param spanId:       Identifier of the timespan.
	:param parentSpanId: Optional, identifier of the enclosing timespan. Default: none, which makes it the root.
	:param traceId:      Optional, identifier of the trace. Default: :data:`TRACE_ID`.
	:param fields:       Further fields to put into the mapping.
	:returns:            The span as an OTLP mapping.
	"""
	span = {"traceId": traceId, "spanId": spanId, "name": name, "kind": 1}
	if parentSpanId is not None:
		span["parentSpanId"] = parentSpanId

	span.update(fields)

	return span


def _document(*spans: dict) -> dict:
	"""
	Wrap spans in the envelope of an OTLP/JSON document.

	:param spans: The spans to wrap.
	:returns:     The document.
	"""
	return {
		"resourceSpans": [{
			"resource":   {"attributes": [{"key": "service.name", "value": {"stringValue": "test"}}]},
			"scopeSpans": [{"scope": {"name": OTLP_SCOPE_NAME, "version": __version__}, "spans": list(spans)}],
		}]
	}


class ReadAttributeValues(Testcase):
	"""An OTLP 'AnyValue' is unwrapped to the Python value it carries."""

	def test_String(self) -> None:
		self.assertEqual("text", _fromAttributeValue({"stringValue": "text"}, "value"))

	def test_Boolean(self) -> None:
		self.assertEqual(True, _fromAttributeValue({"boolValue": True}, "value"))

	def test_Integer(self) -> None:
		"""A 64-bit integer arrives as a decimal string."""
		self.assertEqual(42, _fromAttributeValue({"intValue": "42"}, "value"))

	def test_IntegerAsANumber(self) -> None:
		"""proto3 writes an integer as a string, but accepts a JSON number, so this reader accepts one too."""
		self.assertEqual(42, _fromAttributeValue({"intValue": 42}, "value"))

	def test_Float(self) -> None:
		self.assertEqual(0.5, _fromAttributeValue({"doubleValue": 0.5}, "value"))

	def test_FloatWithoutAFraction(self) -> None:
		"""A JSON number without a fraction decodes to an 'int', and that is a valid double."""
		self.assertEqual(2.0, _fromAttributeValue({"doubleValue": 2}, "value"))

	def test_FloatsWithoutANumber(self) -> None:
		"""JSON has no 'NaN' and no infinities, so proto3's JSON mapping writes them as strings."""
		self.assertTrue(isnan(_fromAttributeValue({"doubleValue": "NaN"}, "value")))
		self.assertEqual(inf, _fromAttributeValue({"doubleValue": "Infinity"}, "value"))
		self.assertEqual(-inf, _fromAttributeValue({"doubleValue": "-Infinity"}, "value"))

	def test_Bytes(self) -> None:
		self.assertEqual(b"\x00\x01\xff", _fromAttributeValue({"bytesValue": "AAH/"}, "value"))

	def test_Array(self) -> None:
		self.assertEqual(
			["a", 1],
			_fromAttributeValue({"arrayValue": {"values": [{"stringValue": "a"}, {"intValue": "1"}]}}, "value")
		)

	def test_KeyValueList(self) -> None:
		self.assertEqual(
			{"a": 1, "b": [True]},
			_fromAttributeValue({"kvlistValue": {"values": [
				{"key": "a", "value": {"intValue": "1"}},
				{"key": "b", "value": {"arrayValue": {"values": [{"boolValue": True}]}}},
			]}}, "value")
		)

	def test_ABooleanIsNoInteger(self) -> None:
		"""'bool' is a subclass of 'int' in Python, but a JSON 'true' is not a number."""
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"intValue": True}, "value")

		self.assertEqual("Field 'value.intValue' is not a number of type 'int'.", str(exceptionCapture.exception))

	def test_AnUnknownTypeIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"dateValue": "2026-08-26"}, "value")

		self.assertEqual("Field 'value' names an unknown type 'dateValue'.", str(exceptionCapture.exception))

	def test_MoreThanOneTypeIsRejected(self) -> None:
		"""An 'AnyValue' is a mapping of exactly one key, and two of them leave the type undecided."""
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"intValue": "1", "stringValue": "1"}, "value")

		self.assertEqual("Field 'value' doesn't name exactly one type.", str(exceptionCapture.exception))

	def test_NoTypeAtAllIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({}, "value")

		self.assertEqual("Field 'value' doesn't name exactly one type.", str(exceptionCapture.exception))
		self.assertIn("The mapping is empty.", exceptionCapture.exception.__notes__)

	def test_AValueThatDoesntMatchItsTypeIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"stringValue": 1}, "value")

		self.assertEqual("Field 'value.stringValue' is not of type 'str'.", str(exceptionCapture.exception))

	def test_AnIntegerThatIsNoNumberIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"intValue": "12 files"}, "value")

		self.assertEqual("Field 'value.intValue' is not a number of type 'int'.", str(exceptionCapture.exception))

	def test_BytesThatArentBase64AreRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributeValue({"bytesValue": "not base64!"}, "value")

		self.assertEqual("Field 'value.bytesValue' is not base64-encoded.", str(exceptionCapture.exception))

	def test_TheSameKeyTwiceIsRejected(self) -> None:
		"""A key-value pair holds one value, so the second one would silently replace the first."""
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributes([
				{"key": "files", "value": {"intValue": "1"}},
				{"key": "files", "value": {"intValue": "2"}},
			], "attributes")

		self.assertEqual("Field 'attributes' has more than one attribute named 'files'.", str(exceptionCapture.exception))

	def test_AnAttributeWithoutAValueIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			_fromAttributes([{"key": "files"}], "attributes")

		self.assertEqual("Field 'attributes[0].value' is missing.", str(exceptionCapture.exception))


class RoundTrip(Testcase):
	"""A trace exported and read back is the trace it started as."""

	def test_TheDocumentIsTheSameAgain(self) -> None:
		"""The strongest statement available: exporting the trace that was read produces the same document."""
		exported = _exampleTrace().ToOTLPJSONString(indent=2)

		self.assertEqual(exported, Trace.FromOTLPJSONString(exported).ToOTLPJSONString(indent=2))

	def test_TheIdentifiersSurvive(self) -> None:
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())

		self.assertEqual(trace.TraceID, read.TraceID)
		self.assertEqual(trace.SpanID, read.SpanID)
		self.assertEqual(
			[span.SpanID for span in trace.IterateSubSpans()],
			[span.SpanID for span in read.IterateSubSpans()]
		)

	def test_TheTreeSurvives(self) -> None:
		"""OTLP has no nesting, so this is the 'parentSpanId' references being resolved back into a tree."""
		read = Trace.FromOTLPJSON(_exampleTrace().ToOTLPJSON())

		self.assertEqual("build", read.Name)
		self.assertEqual(["compile", "link"], [span.Name for span in read.IterateSubSpans()])
		self.assertIs(read, next(read.IterateSubSpans()).Parent)
		self.assertIs(read, next(read.IterateSubSpans()).Trace)

	def test_TheTimestampsSurvive(self) -> None:
		"""A 'datetime' holds microseconds and the document holds nanoseconds, so the value is rounded, not cut."""
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())

		self.assertEqual(trace.StartTime, read.StartTime)
		self.assertEqual(trace.Duration, read.Duration)

	def test_TheDurationIsExactAlthoughTheCounterIsGone(self) -> None:
		"""The performance counter that measured the duration ran in another process; the difference survives."""
		document = _document(
			_span("span", "1234567890abcdef", startTimeUnixNano="1000000000", endTimeUnixNano="1000012345")
		)

		self.assertEqual(12345 / 1e9, Trace.FromOTLPJSON(document).Duration)

	def test_TheAttributesSurvive(self) -> None:
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())
		compileSpan = next(read.IterateSubSpans())

		self.assertEqual("10.0.0", read["version"])
		self.assertEqual(12, compileSpan["files"])
		self.assertEqual(True, compileSpan["optimized"])
		self.assertEqual(0.5, compileSpan["ratio"])
		self.assertEqual(["a", "b"], compileSpan["targets"])

	def test_ATupleReturnsAsAList(self) -> None:
		"""OTLP has a single 'arrayValue', so this is the one conversion a round-trip cannot undo."""
		with Trace("trace") as trace:
			trace["targets"] = ("a", "b")

		self.assertEqual(["a", "b"], Trace.FromOTLPJSON(trace.ToOTLPJSON())["targets"])

	def test_TheEventsSurvive(self) -> None:
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())
		event = next(next(read.IterateSubSpans()).IterateEvents())
		original = next(next(trace.IterateSubSpans()).IterateEvents())

		self.assertEqual("cache miss", event.Name)
		self.assertEqual(original.Time, event.Time)
		self.assertIs(next(read.IterateSubSpans()), event.Parent)

	def test_ATraceThatWasNeverEnteredHasNoTimestamps(self) -> None:
		"""Its exported mapping has none either, so both are read back as absent rather than as the Unix epoch."""
		read = Trace.FromOTLPJSON(Trace("never entered").ToOTLPJSON())

		self.assertIsNone(read.StartTime)
		self.assertIsNone(read.StopTime)

	def test_TheFileRoundTripsToo(self) -> None:
		trace = _exampleTrace()
		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "report" / "trace.json"
			trace.WriteOTLPJSONFile(jsonFile, indent=2)

			self.assertEqual(trace.TraceID, Trace.ReadOTLPJSONFile(jsonFile).TraceID)


class ReadSpans(Testcase):
	"""The flat list of spans is reassembled into the tree its 'parentSpanId' references describe."""

	def test_TheSpanWithoutAParentBecomesTheTrace(self) -> None:
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
		))

		self.assertEqual("root", trace.Name)
		self.assertEqual(TRACE_ID, trace.TraceID)
		self.assertEqual("1111111111111111", trace.SpanID)
		self.assertEqual(["child"], [span.Name for span in trace.IterateSubSpans()])

	def test_AnEmptyParentSpanIdIsNoParent(self) -> None:
		"""proto3's JSON mapping may write an unset 'bytes' field as an empty string rather than omitting it."""
		trace = Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", parentSpanId="")))

		self.assertEqual("root", trace.Name)

	def test_TheSiblingsKeepTheirOrder(self) -> None:
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("third", "4444444444444444", "1111111111111111"),
			_span("first", "2222222222222222", "1111111111111111"),
			_span("second", "3333333333333333", "1111111111111111"),
		))

		self.assertEqual(["third", "first", "second"], [span.Name for span in trace.IterateSubSpans()])

	def test_TheSpansMayBeSpreadOverSeveralEntries(self) -> None:
		"""Nothing requires a producer to put one trace into one 'resourceSpans' entry."""
		document = _document(_span("root", "1111111111111111"))
		second = _document(_span("child", "2222222222222222", "1111111111111111"))
		document["resourceSpans"].append(second["resourceSpans"][0])

		self.assertEqual(["child"], [span.Name for span in Trace.FromOTLPJSON(document).IterateSubSpans()])

	def test_ADeeplyNestedTraceIsBuiltWithoutRecursion(self) -> None:
		"""Deeper than Python's recursion limit, so a recursive descent through 'parentSpanId' would not survive it."""
		spans = [_span("span1", f"{1:016x}")]
		spans.extend(_span(f"span{depth}", f"{depth:016x}", f"{depth - 1:016x}") for depth in range(2, 2001))

		span = Trace.FromOTLPJSON(_document(*spans))
		for _ in range(2, 2001):
			span = next(span.IterateSubSpans())

		self.assertEqual("span2000", span.Name)

	def test_TheKindIsDropped(self) -> None:
		"""Every timespan of this data model is 'SPAN_KIND_INTERNAL', so another kind is accepted and forgotten."""
		trace = Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", kind=2)))

		self.assertEqual("root", trace.Name)


class ReadEvents(Testcase):
	"""An event is read back into the timespan it happened in."""

	def test_TheEventIsAttachedToItsSpan(self) -> None:
		trace = Trace.FromOTLPJSON(_document(_span(
			"root", "1111111111111111",
			events=[{"name": "cache miss", "timeUnixNano": "1787659200123456000"}]
		)))
		event = next(trace.IterateEvents())

		self.assertEqual("cache miss", event.Name)
		self.assertEqual(datetime.fromtimestamp(1787659200) + timedelta(microseconds=123456), event.Time)
		self.assertIs(trace, event.Parent)

	def test_ItsAttributesAreRead(self) -> None:
		trace = Trace.FromOTLPJSON(_document(_span(
			"root", "1111111111111111",
			events=[{
				"name":         "cache miss",
				"timeUnixNano": "1787659200000000000",
				"attributes":   [{"key": "key", "value": {"stringValue": "libghdl"}}],
			}]
		)))

		self.assertEqual("libghdl", next(trace.IterateEvents())["key"])

	def test_AnEventWithoutATimeIsRejected(self) -> None:
		"""OTLP reads a missing 'timeUnixNano' as the Unix epoch, which would place the event in 1970."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", events=[{"name": "no time"}])))

		self.assertIn("events[0].timeUnixNano' is missing.", str(exceptionCapture.exception))


class ReadIdentifiers(Testcase):
	"""A trace or span identifier is 32 or 16 hex digits, and never all zeros."""

	def test_UpperCaseIsNormalized(self) -> None:
		"""The specification says lower case, but a 'parentSpanId' reference has to resolve either way."""
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "AAAAAAAAAAAAAAAA", traceId=TRACE_ID.upper()),
			_span("child", "bbbbbbbbbbbbbbbb", "aaaaaaaaaaaaaaaa", traceId=TRACE_ID),
		))

		self.assertEqual("aaaaaaaaaaaaaaaa", trace.SpanID)
		self.assertEqual(TRACE_ID, trace.TraceID)
		self.assertEqual(["child"], [span.Name for span in trace.IterateSubSpans()])

	def test_ATooShortIdentifierIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "abcdef")))

		self.assertIn("spanId' is not 16 hexadecimal digits.", str(exceptionCapture.exception))

	def test_ANonHexadecimalIdentifierIsRejected(self) -> None:
		"""'int(..., 16)' would accept a leading sign and surrounding whitespace, so the digits are checked."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", " 111111111111111")))

		self.assertIn("spanId' is not 16 hexadecimal digits.", str(exceptionCapture.exception))

	def test_AnAllZeroIdentifierIsRejected(self) -> None:
		"""OTLP defines it as invalid, which is the rule '_newIdentifier' draws by."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "0000000000000000")))

		self.assertIn("spanId' is all zeros.", str(exceptionCapture.exception))

	def test_TheSameSpanIdentifierTwiceIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("root", "1111111111111111"),
				_span("child", "2222222222222222", "1111111111111111"),
				_span("clone", "2222222222222222", "1111111111111111"),
			))

		self.assertEqual(
			f"Trace '{TRACE_ID}' has more than one span with identifier '2222222222222222'.",
			str(exceptionCapture.exception)
		)


class ReadBrokenTrees(Testcase):
	"""The spans of a trace form a tree below exactly one root, or the document is rejected."""

	def test_TwoRootsAreRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("one", "1111111111111111"), _span("two", "2222222222222222")))

		self.assertEqual(f"Trace '{TRACE_ID}' has 2 spans without a 'parentSpanId'.", str(exceptionCapture.exception))

	def test_ACycleHasNoRootAtAll(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("one", "1111111111111111", "2222222222222222"),
				_span("two", "2222222222222222", "1111111111111111"),
			))

		self.assertEqual(
			f"2 span(s) of trace '{TRACE_ID}' reference each other in a cycle.",
			str(exceptionCapture.exception)
		)

	def test_AFragmentIsRejectedByTrace(self) -> None:
		"""Its 'parentSpanId' names a span this document doesn't carry - a 'TraceCollection' keeps it, a trace can't."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("root", "1111111111111111"),
				_span("fragment", "2222222222222222", "3333333333333333"),
			))

		self.assertEqual(
			f"1 span(s) of trace '{TRACE_ID}' are not part of its tree.",
			str(exceptionCapture.exception)
		)
		self.assertIn(
			"Use 'TraceCollection.FromOTLPJSON()' to keep such a fragment until its parent arrives.",
			exceptionCapture.exception.__notes__
		)

	def test_ATraceWithoutItsRootSpanIsRejectedByTrace(self) -> None:
		"""Every span names a parent, and the one they lead up to hasn't been delivered."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("child", "2222222222222222", "1111111111111111")))

		self.assertEqual(
			f"Trace '{TRACE_ID}' has no span without a 'parentSpanId'.",
			str(exceptionCapture.exception)
		)

	def test_ADetachedCycleIsReported(self) -> None:
		"""Two spans naming each other are not reachable from the root, although the root itself is fine."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("root", "1111111111111111"),
				_span("one", "2222222222222222", "3333333333333333"),
				_span("two", "3333333333333333", "2222222222222222"),
			))

		self.assertEqual(
			f"2 span(s) of trace '{TRACE_ID}' reference each other in a cycle.",
			str(exceptionCapture.exception)
		)


class ReadTimestamps(Testcase):
	"""A timespan carries both timestamps or neither, and the second one never precedes the first."""

	def test_OnlyAStartIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", startTimeUnixNano="1000000000")))

		self.assertIn("endTimeUnixNano' is missing.", str(exceptionCapture.exception))

	def test_OnlyAnEndIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", endTimeUnixNano="1000000000")))

		self.assertIn("startTimeUnixNano' is missing.", str(exceptionCapture.exception))

	def test_AnEndBeforeItsStartIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span(
				"root", "1111111111111111", startTimeUnixNano="2000000000", endTimeUnixNano="1000000000"
			)))

		self.assertIn("precedes", str(exceptionCapture.exception))

	def test_ATimestampOutsideTheRangeOfADatetimeIsRejected(self) -> None:
		"""A 64-bit nanosecond value reaches the year 2554, and 'datetime' stops at 9999."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span(
				"root", "1111111111111111",
				startTimeUnixNano="999999999999999999999", endTimeUnixNano="999999999999999999999"
			)))

		self.assertIn("is not a timestamp a 'datetime' can represent.", str(exceptionCapture.exception))

	def test_TheNanosecondsAreRoundedNotTruncated(self) -> None:
		"""The export scales a float, whose precision at today's epoch is about 256 ns - less than half a µs."""
		self.assertEqual(datetime.fromtimestamp(1) + timedelta(microseconds=2), _fromUnixNano(1_000_001_500, "value"))
		self.assertEqual(datetime.fromtimestamp(1) + timedelta(microseconds=1), _fromUnixNano(1_000_001_499, "value"))


class SelectATrace(Testcase):
	"""A document may hold more than one trace, and then the caller says which one to read."""

	def test_TheOnlyTraceIsTheDefault(self) -> None:
		self.assertEqual(TRACE_ID, Trace.FromOTLPJSON(_document(_span("root", "1111111111111111"))).TraceID)

	def test_SeveralTracesNeedTheTraceIDParameter(self) -> None:
		other = "fedcba9876543210fedcba9876543210"
		document = _document(_span("one", "1111111111111111"), _span("two", "2222222222222222", traceId=other))

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(document)

		self.assertEqual("The OTLP/JSON document contains 2 traces.", str(exceptionCapture.exception))
		self.assertEqual("two", Trace.FromOTLPJSON(document, other).Name)
		self.assertEqual("one", Trace.FromOTLPJSON(document, TRACE_ID).Name)

	def test_TheTraceIDIsMatchedInLowerCase(self) -> None:
		document = _document(_span("root", "1111111111111111"))

		self.assertEqual("root", Trace.FromOTLPJSON(document, TRACE_ID.upper()).Name)

	def test_AnUnknownTraceIDIsReported(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111")), "f" * 32)

		self.assertEqual(f"The OTLP/JSON document contains no trace '{'f' * 32}'.", str(exceptionCapture.exception))

	def test_ADocumentWithoutSpansIsReported(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": []})

		self.assertEqual("The OTLP/JSON document contains no spans.", str(exceptionCapture.exception))

	def test_ATraceIDIsAString(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111")), 42)

		self.assertEqual("Parameter 'traceID' is not of type 'str'.", str(exceptionCapture.exception))


class ReadMalformedDocuments(Testcase):
	"""A field that is missing or of the wrong type is named by its position in the document."""

	def test_AMissingFieldIsNamedByItsPath(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": [{"resource": {}}]})

		self.assertEqual("Field 'document.resourceSpans[0].scopeSpans' is missing.", str(exceptionCapture.exception))

	def test_AFieldOfTheWrongTypeIsNamedByItsPath(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": {}})

		self.assertEqual("Field 'document.resourceSpans' is not of type 'list'.", str(exceptionCapture.exception))

	def test_ASpanWithoutANameIsRejected(self) -> None:
		span = _span("root", "1111111111111111")
		del span["name"]

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(span))

		self.assertIn(".name' is missing.", str(exceptionCapture.exception))

	def test_ASpanWithAnEmptyNameIsRejected(self) -> None:
		"""The constructor rejects it with a 'ValueError', which is no way to report a broken document."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("root", "1111111111111111"),
				_span("", "2222222222222222", "1111111111111111"),
			))

		self.assertIn(".name' is empty.", str(exceptionCapture.exception))

	def test_ATraceWithAnEmptyNameIsRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("", "1111111111111111")))

		self.assertIn(".name' is empty.", str(exceptionCapture.exception))


class ReadErrors(Testcase):
	"""Reading a string or a file reports what went wrong with it."""

	def test_InvalidJSONIsReported(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSONString("{not json")

		self.assertEqual("The OTLP/JSON document isn't valid JSON.", str(exceptionCapture.exception))

	def test_AStringIsAString(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.FromOTLPJSONString(42)

		self.assertEqual("Parameter 'jsonString' is not of type 'str'.", str(exceptionCapture.exception))

	def test_APathIsAPath(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.ReadOTLPJSONFile("trace.json")

		self.assertEqual("Parameter 'jsonFile' is not of type 'Path'.", str(exceptionCapture.exception))

	def test_AnUnreadableFileIsReported(self) -> None:
		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "missing.json"

			with self.assertRaises(TracingError) as exceptionCapture:
				Trace.ReadOTLPJSONFile(jsonFile)

			self.assertEqual(f"OTLP/JSON file '{jsonFile}' couldn't be read.", str(exceptionCapture.exception))


OTHER_TRACE_ID = "fedcba9876543210fedcba9876543210"
"""A second syntactically valid trace identifier, for the documents holding two traces."""


def _timedSpan(name: str, spanId: str, parentSpanId: str = None, start: int = 0, duration: int = 1_000_000) -> dict:
	"""
	Assemble one OTLP span mapping carrying timestamps.

	:param name:         Name of the timespan.
	:param spanId:       Identifier of the timespan.
	:param parentSpanId: Optional, identifier of the enclosing timespan.
	:param start:        Optional, nanoseconds to add to a fixed epoch for the start timestamp.
	:param duration:     Optional, duration of the timespan in nanoseconds.
	:returns:            The span as an OTLP mapping.
	"""
	startTimeUnixNano = 1_787_659_200_000_000_000 + start

	return _span(
		name, spanId, parentSpanId,
		startTimeUnixNano=str(startTimeUnixNano),
		endTimeUnixNano=str(startTimeUnixNano + duration)
	)


def _splitExample() -> tuple[Trace, dict, dict]:
	"""
	Export a trace and cut the document in two, the way two processes would have written it.

	:returns: Tuple of the original trace, the document holding its root and one branch, and the document holding
	          the other branch - whose root is a fragment, because its parent is in the first document.
	"""
	with Trace("build") as trace:
		with Span("compile"):
			with Span("parse"):
				sleep(0.001)
		with Span("link"):
			sleep(0.001)

	spans = {span["name"]: span for span in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]}

	return trace, _document(spans["build"], spans["link"]), _document(spans["compile"], spans["parse"])


class Collections(Testcase):
	"""A collection holds what a document carries: several traces, and timespans that aren't part of one yet."""

	def test_ACompleteTraceIsATrace(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
		))

		self.assertEqual(1, collection.TraceCount)
		self.assertEqual(2, collection.SpanCount)
		self.assertEqual(0, collection.FragmentCount)
		self.assertFalse(collection.HasFragments)
		self.assertEqual("root", collection.Traces[0].Name)

	def test_SeveralTracesAreAllRead(self) -> None:
		"""This is what a collection is for - 'Trace.FromOTLPJSON' reads one of them and rejects the rest."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("one", "1111111111111111"),
			_span("two", "2222222222222222", traceId=OTHER_TRACE_ID),
		))

		self.assertEqual(2, collection.TraceCount)
		self.assertEqual(["one", "two"], [trace.Name for trace in collection])
		self.assertEqual(TRACE_ID, collection[TRACE_ID].TraceID)
		self.assertEqual(OTHER_TRACE_ID, collection[OTHER_TRACE_ID].TraceID)

	def test_ASpanWithoutItsParentIsAFragment(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("fragment", "2222222222222222", "3333333333333333"),
		))

		self.assertEqual(1, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)
		self.assertTrue(collection.HasFragments)
		self.assertEqual("fragment", collection.Fragments[0].Name)
		self.assertIsNone(collection.Fragments[0].Parent)
		self.assertIsNone(collection.Fragments[0].Trace)

	def test_AFragmentKeepsItsOwnSubSpans(self) -> None:
		"""Only the fragment's *place* is unknown; the part of the tree that came with it is built."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("fragment", "2222222222222222", "3333333333333333"),
			_span("below", "4444444444444444", "2222222222222222"),
		))

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)
		self.assertEqual(["below"], [span.Name for span in collection.Fragments[0].IterateSubSpans()])

	def test_ATraceWithoutItsRootSpanIsOnlyFragments(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(_span("child", "2222222222222222", "1111111111111111")))

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)
		self.assertEqual(TRACE_ID, collection.TraceIDOfSpan("2222222222222222"))

	def test_ACycleIsStillRejected(self) -> None:
		"""A fragment's parent is merely absent; a cycle's spans point at each other and can be placed nowhere."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceCollection.FromOTLPJSON(_document(
				_span("one", "1111111111111111", "2222222222222222"),
				_span("two", "2222222222222222", "1111111111111111"),
			))

		self.assertEqual(
			f"2 span(s) of trace '{TRACE_ID}' reference each other in a cycle.",
			str(exceptionCapture.exception)
		)

	def test_TwoRootSpansAreStillRejected(self) -> None:
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceCollection.FromOTLPJSON(_document(_span("one", "1111111111111111"), _span("two", "2222222222222222")))

		self.assertEqual(f"Trace '{TRACE_ID}' has 2 spans without a 'parentSpanId'.", str(exceptionCapture.exception))


class MergingDocuments(Testcase):
	"""A distributed execution is exported per process, so a trace arrives in pieces and is reassembled."""

	def test_TheFragmentFindsItsParent(self) -> None:
		trace, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(first).AddOTLPJSON(second)

		self.assertFalse(collection.HasFragments)
		self.assertEqual(4, collection.SpanCount)
		self.assertEqual(trace.ToOTLPJSONString(), collection.Traces[0].ToOTLPJSONString())

	def test_TheParentFindsTheFragment(self) -> None:
		"""The other order: the fragment waits, and the document carrying its parent collects it."""
		trace, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second)

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)

		collection.AddOTLPJSON(first)

		self.assertFalse(collection.HasFragments)
		self.assertEqual(trace.ToOTLPJSONString(), collection.Traces[0].ToOTLPJSONString())

	def test_TheSiblingsAreOrderedByStartTime(self) -> None:
		"""A fragment is attached when its parent arrives, which is not the order the timespans ran in."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_timedSpan("root", "1111111111111111"),
			_timedSpan("third", "4444444444444444", "1111111111111111", start=3_000_000),
		))
		collection.AddOTLPJSON(_document(
			_timedSpan("second", "3333333333333333", "1111111111111111", start=2_000_000),
			_timedSpan("first", "2222222222222222", "1111111111111111", start=1_000_000),
		))

		self.assertEqual(["first", "second", "third"], [span.Name for span in collection.Traces[0].IterateSubSpans()])

	def test_TheFragmentsSubSpansJoinTheTraceToo(self) -> None:
		"""'_AddSpan' sets the fragment's trace; everything below it was carrying 'None' and has to be updated."""
		trace, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second).AddOTLPJSON(first)
		built = collection.Traces[0]

		for span in (*built.IterateSubSpans(), *next(built.IterateSubSpans()).IterateSubSpans()):
			with self.subTest(span=span.Name):
				self.assertIs(built, span.Trace)

	def test_TheSameSpanTwiceIsRejected(self) -> None:
		"""A distributed trace is assembled from spans that were each exported once."""
		_, _, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second)

		with self.assertRaises(TracingError) as exceptionCapture:
			collection.AddOTLPJSON(second)

		self.assertIn("The collection already contains a timespan", str(exceptionCapture.exception))

	def test_ASecondRootSpanForOneTraceIsRejected(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(_span("root", "1111111111111111")))

		with self.assertRaises(TracingError) as exceptionCapture:
			collection.AddOTLPJSON(_document(_span("other root", "2222222222222222")))

		self.assertEqual(f"The collection already contains trace '{TRACE_ID}'.", str(exceptionCapture.exception))

	def test_ARejectedDocumentChangesNothing(self) -> None:
		"""The whole document is checked before anything is registered, so a collision isn't half applied."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("root", "1111111111111111")))
		colliding = _document(
			_span("fresh", "5555555555555555", traceId=OTHER_TRACE_ID),
			_span("clash", "1111111111111111", "2222222222222222"),
		)

		with self.assertRaises(TracingError):
			collection.AddOTLPJSON(colliding)

		self.assertEqual(1, collection.TraceCount)
		self.assertEqual(1, collection.SpanCount)
		self.assertNotIn("5555555555555555", collection)


class CollectionLookup(Testcase):
	"""Traces and timespans are indexed by identifier, which is what lets a fragment be linked to its parent."""

	def _Collection(self) -> TraceCollection:
		return TraceCollection.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
			_span("fragment", "3333333333333333", "4444444444444444"),
		))

	def test_TheLengthDecidesWhichIndexIsSearched(self) -> None:
		"""A trace identifier is 32 hex digits and a span identifier is 16, so the two can't be confused."""
		collection = self._Collection()

		self.assertEqual("root", collection[TRACE_ID].Name)
		self.assertEqual("child", collection["2222222222222222"].Name)

	def test_TheIdentifierIsMatchedInLowerCase(self) -> None:
		collection = self._Collection()

		self.assertEqual("root", collection[TRACE_ID.upper()].Name)
		self.assertEqual("child", collection["2222222222222222"].Name)

	def test_AnIdentifierOfAnotherLengthIsNoIdentifier(self) -> None:
		with self.assertRaises(KeyError):
			self._Collection()["abc"]

	def test_ContainsAsksTheSameIndexes(self) -> None:
		collection = self._Collection()

		self.assertIn(TRACE_ID, collection)
		self.assertIn("2222222222222222", collection)
		self.assertIn("3333333333333333", collection, "A fragment is a timespan of the collection like any other.")
		self.assertNotIn(OTHER_TRACE_ID, collection)
		self.assertNotIn("4444444444444444", collection, "The awaited parent is exactly what isn't here.")

	def test_AFragmentsTraceCanStillBeNamed(self) -> None:
		"""It has no 'Trace' to ask, but its 'traceId' was in the document all the same."""
		collection = self._Collection()

		self.assertIsNone(collection["3333333333333333"].Trace)
		self.assertEqual(TRACE_ID, collection.TraceIDOfSpan("3333333333333333"))

	def test_TheFragmentsOfOneTraceCanBeIterated(self) -> None:
		collection = self._Collection()
		collection.AddOTLPJSON(_document(
			_span("elsewhere", "5555555555555555", "6666666666666666", traceId=OTHER_TRACE_ID)
		))

		self.assertEqual(["fragment"], [span.Name for span in collection.IterateFragmentsOf(TRACE_ID)])
		self.assertEqual(["elsewhere"], [span.Name for span in collection.IterateFragmentsOf(OTHER_TRACE_ID)])

	def test_LengthAndIterationAreAboutTraces(self) -> None:
		"""A fragment is not a trace, so it is neither counted nor iterated as one."""
		collection = self._Collection()

		self.assertEqual(1, len(collection))
		self.assertEqual(["root"], [trace.Name for trace in collection])

	def test_TheRepresentationsCountWhatIsThere(self) -> None:
		collection = self._Collection()

		self.assertEqual("1 traces + 1 fragments", str(collection))
		self.assertEqual("TraceCollection: 1 traces, 3 spans, 1 fragments", repr(collection))


class CollectionDocuments(Testcase):
	"""A collection writes an OTLP/JSON document back, fragments included."""

	def test_TheDocumentIsTheSameAgain(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("one", "1111111111111111"),
			_span("two", "2222222222222222", traceId=OTHER_TRACE_ID),
		))
		encoded = collection.ToOTLPJSONString(indent=2)

		self.assertEqual(encoded, TraceCollection.FromOTLPJSONString(encoded).ToOTLPJSONString(indent=2))

	def test_AFragmentKeepsTheParentItIsWaitingFor(self) -> None:
		"""Without its 'parentSpanId' it would read back as a second root span rather than as a fragment."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("fragment", "2222222222222222", "3333333333333333")))
		written = collection.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"][0]

		self.assertEqual("3333333333333333", written["parentSpanId"])
		self.assertEqual(1, TraceCollection.FromOTLPJSON(collection.ToOTLPJSON()).FragmentCount)

	def test_ATraceWithoutARootIsNamedByItsIdentifier(self) -> None:
		"""There is no root span to take a name from, and 'service.name' has to say something."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("fragment", "2222222222222222", "3333333333333333")))
		resource = collection.ToOTLPJSON()["resourceSpans"][0]["resource"]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": TRACE_ID}}],
			resource["attributes"]
		)

	def test_EveryTraceGetsItsOwnResourceEntry(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("one", "1111111111111111"),
			_span("two", "2222222222222222", traceId=OTHER_TRACE_ID),
		))
		resourceSpans = collection.ToOTLPJSON()["resourceSpans"]

		self.assertEqual(2, len(resourceSpans))
		self.assertEqual(
			["one", "two"],
			[entry["resource"]["attributes"][0]["value"]["stringValue"] for entry in resourceSpans]
		)

	def test_TheStringAndTheFileAreReadBackToo(self) -> None:
		_, first, second = _splitExample()

		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "report" / "traces.json"
			TraceCollection.FromOTLPJSON(first).WriteOTLPJSONFile(jsonFile, indent=2)

			collection = TraceCollection.ReadOTLPJSONFile(jsonFile)
			collection.AddOTLPJSONString(json_dumps(second))

		self.assertEqual(1, collection.TraceCount)
		self.assertFalse(collection.HasFragments)

	def test_AnEmptyCollectionIsAnEmptyDocument(self) -> None:
		self.assertEqual({"resourceSpans": []}, TraceCollection().ToOTLPJSON())


class CollectionFormatting(Testcase):
	"""'Format' renders the traces, then whatever is still waiting for a parent."""

	def test_TheFragmentsAreListedWithWhatTheyWaitFor(self) -> None:
		collection = TraceCollection.FromOTLPJSON(_document(
			_timedSpan("root", "1111111111111111"),
			_timedSpan("fragment", "2222222222222222", "3333333333333333"),
		))
		lines = list(collection.Format())

		self.assertIn("Fragments: 1", lines)
		self.assertTrue(any("waiting for span 3333333333333333" in line for line in lines))
		self.assertTrue(any("fragment" in line for line in lines))

	def test_ATimespanWithoutADurationIsNotDivided(self) -> None:
		"""A trace that was never entered has no duration, and 'Format' used to divide 'None' by 1e6."""
		lines = list(Trace("never entered").Format())

		self.assertEqual(2, len(lines))
		self.assertTrue(all("-- ms" in line for line in lines), lines)
