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
Unit tests for the **OTLP/JSON** export of :mod:`pyTooling.Tracing`.
"""
from datetime  import datetime
from json      import loads as json_loads
from pathlib   import Path
from tempfile  import TemporaryDirectory
from time      import sleep
from unittest  import mock

from pyTooling.Common  import __version__
from pyTooling.Testing import Testcase
from pyTooling.Tracing import OTLP_SCOPE_NAME, Event, Span, Trace, TracingError, _newIdentifier, _toAttributeValue

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
		document = _exampleTrace().ToJSON(serviceName="myProgram")
		resourceSpans = document["resourceSpans"][0]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			resourceSpans["resource"]["attributes"]
		)
		self.assertEqual(OTLP_SCOPE_NAME, resourceSpans["scopeSpans"][0]["scope"]["name"])

	def test_TheServiceNameDefaultsToTheTracesName(self) -> None:
		document = _exampleTrace().ToJSON()

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "build"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_OnlyATraceConvertsToADocument(self) -> None:
		"""A lone span is not an OTLP document - it has no 'traceId' and no service to be reported under."""

		self.assertFalse(hasattr(Span("not a trace"), "ToJSON"))
		self.assertTrue(hasattr(Trace("a trace"), "ToJSON"))


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
		spans = self._Spans(_exampleTrace().ToJSON())

		self.assertEqual({"build", "compile", "link"}, set(spans))

	def test_AllSpansShareOneTraceIdentifier(self) -> None:
		spans = self._Spans(_exampleTrace().ToJSON())
		identifiers = {span["traceId"] for span in spans.values()}

		self.assertEqual(1, len(identifiers))
		self.assertEqual(32, len(identifiers.pop()), "A trace identifier is 16 bytes, hex-encoded.")

	def test_TheHierarchyIsCarriedByParentSpanId(self) -> None:
		spans = self._Spans(_exampleTrace().ToJSON())

		self.assertNotIn("parentSpanId", spans["build"], "The trace itself has no parent.")
		self.assertEqual(spans["build"]["spanId"], spans["compile"]["parentSpanId"])
		self.assertEqual(spans["build"]["spanId"], spans["link"]["parentSpanId"])

	def test_ASpanIdentifierIsEightBytes(self) -> None:
		spans = self._Spans(_exampleTrace().ToJSON())

		for name, span in spans.items():
			with self.subTest(span=name):
				self.assertEqual(16, len(span["spanId"]))
				self.assertEqual(span["spanId"], span["spanId"].lower(), "OTLP/JSON uses lower-case hex.")

	def test_TheDurationSurvives(self) -> None:
		"""A span's duration is in seconds while OTLP wants nanoseconds, which is the easy factor to get wrong."""
		spans = self._Spans(_exampleTrace().ToJSON())
		compileSpan = spans["compile"]
		duration = int(compileSpan["endTimeUnixNano"]) - int(compileSpan["startTimeUnixNano"])

		self.assertGreater(duration, 1_000_000, "The span slept for a millisecond, so it lasted at least that.")
		self.assertLess(duration, 10_000_000_000, "A millisecond must not be reported as seconds.")

	def test_TheTimestampsAreStrings(self) -> None:
		"""proto3's JSON mapping encodes a 64-bit integer as a string."""
		for span in self._Spans(_exampleTrace().ToJSON()).values():
			with self.subTest(span=span["name"]):
				self.assertIsInstance(span["startTimeUnixNano"], str)
				self.assertIsInstance(span["endTimeUnixNano"], str)

	def test_AttributesAreExported(self) -> None:
		spans = self._Spans(_exampleTrace().ToJSON())
		attributes = {entry["key"]: entry["value"] for entry in spans["compile"]["attributes"]}

		self.assertEqual({"intValue": "12"}, attributes["files"])
		self.assertEqual({"boolValue": True}, attributes["optimized"])
		self.assertEqual({"doubleValue": 0.5}, attributes["ratio"])

	def test_ASpanWithoutAttributesHasNoAttributeKey(self) -> None:
		spans = self._Spans(_exampleTrace().ToJSON())

		self.assertNotIn("attributes", spans["link"])
		self.assertNotIn("events", spans["link"])


class Events(Testcase):
	"""An event belongs to the span it was created in."""

	def test_TheEventIsExported(self) -> None:
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
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
			for exported in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertListEqual(
			[{"key": "key", "value": {"stringValue": "value"}}],
			spans["span"]["events"][0]["attributes"]
		)

	def test_AnEventWithoutAttributesHasNoAttributeKey(self) -> None:
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
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
			for exported in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
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
			for exported in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual(str(int(time.timestamp() * 1_000_000_000)), spans["span"]["events"][0]["timeUnixNano"])


class WrittenFile(Testcase):
	"""The document reaches a file as JSON."""

	def test_TheFileIsValidJSONAndRoundTrips(self) -> None:
		trace = _exampleTrace()

		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			trace.WriteJSONFile(path, serviceName="myProgram", indent=2)

			document = json_loads(path.read_text(encoding="utf-8"))

		self.assertEqual(trace.ToJSON("myProgram")["resourceSpans"][0]["scopeSpans"][0]["scope"],
		                 document["resourceSpans"][0]["scopeSpans"][0]["scope"])
		self.assertEqual(3, len(document["resourceSpans"][0]["scopeSpans"][0]["spans"]))


class Encoding(Testcase):
	"""The two ways a trace hands its document out, beside the mapping itself."""

	def test_TheStringIsTheEncodedDocument(self) -> None:
		trace = _exampleTrace()

		self.assertEqual(trace.ToJSON(), json_loads(trace.ToJSONString()))

	def test_TheCompactFormIsTheDefault(self) -> None:
		"""That is what a collector expects; an indent is for a human reading the file."""

		trace = _exampleTrace()

		self.assertNotIn("\n", trace.ToJSONString())
		self.assertIn("\n", trace.ToJSONString(indent=2))

	def test_TheServiceNameReachesTheString(self) -> None:
		document = json_loads(_exampleTrace().ToJSONString(serviceName="myProgram"))

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_TheDirectoryIsCreated(self) -> None:
		"""'report/' rarely exists when a pipeline asks for a trace inside it."""

		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			_exampleTrace().WriteJSONFile(path)

			self.assertTrue(path.exists())

	def test_APathIsAPath(self) -> None:
		with TemporaryDirectory() as directory:
			with self.assertRaises(TypeError) as exceptionCapture:
				_exampleTrace().WriteJSONFile(f"{directory}/trace.json")

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
					_exampleTrace().WriteJSONFile(path)

		self.assertEqual(f"Directory '{path.parent}' couldn't be created.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)

	def test_AnUnwritableFileIsReported(self) -> None:
		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			with mock.patch("pathlib.Path.open", side_effect=PermissionError("denied")):
				with self.assertRaises(TracingError) as exceptionCapture:
					_exampleTrace().WriteJSONFile(path)

		self.assertEqual(f"OTLP/JSON file '{path}' couldn't be written.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)


class Identity(Testcase):
	"""The identifiers belong to the data model, not to a conversion."""

	def test_ATraceKeepsItsIdentifierAcrossConversions(self) -> None:
		"""This is what the by-call generation couldn't do: two exports describe one trace, not two."""
		trace = _exampleTrace()

		first = trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		second = trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]

		self.assertEqual(first, second)
		self.assertEqual(trace.TraceID, first[0]["traceId"])

	def test_ASpanKnowsItsOwnIdentifierAndItsTrace(self) -> None:
		with Trace("trace") as trace:
			with Span("span") as span:
				pass

		exported = {
			converted["name"]: converted
			for converted in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
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
			for converted in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertIs(outer, inner.Parent)
		self.assertEqual(outer.SpanID, exported["inner"]["parentSpanId"])
		self.assertEqual(trace.SpanID, exported["outer"]["parentSpanId"])
		self.assertNotIn("parentSpanId", exported["trace"], "The trace itself has no parent.")

	def test_EveryIdentifierOfATraceIsDistinct(self) -> None:
		spans = _exampleTrace().ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
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
		scope = _exampleTrace().ToJSON()["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual(OTLP_SCOPE_NAME, scope["name"])
		self.assertEqual(__version__, scope["version"])

	def test_ItIsInjectedRatherThanPatched(self) -> None:
		"""A program wrapping pyTooling's tracing reports its own name, without touching the module."""
		scope = _exampleTrace().ToJSON(
			scopeName="myProgram.Instrumentation",
			scopeVersion="2.1.0"
		)["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual({"name": "myProgram.Instrumentation", "version": "2.1.0"}, scope)

	def test_ItReachesTheStringAndTheFile(self) -> None:
		trace = _exampleTrace()

		document = json_loads(trace.ToJSONString(scopeName="myProgram", scopeVersion="2.1.0"))
		self.assertEqual("myProgram", document["resourceSpans"][0]["scopeSpans"][0]["scope"]["name"])

		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			trace.WriteJSONFile(path, scopeName="myProgram", scopeVersion="2.1.0")
			written = json_loads(path.read_text(encoding="utf-8"))

		self.assertEqual("myProgram", written["resourceSpans"][0]["scopeSpans"][0]["scope"]["name"])
