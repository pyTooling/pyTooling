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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
from datetime             import datetime, timedelta, timezone
from json                 import dumps as json_dumps, loads as json_loads
from math                 import inf, isnan
from pathlib              import Path
from tempfile             import TemporaryDirectory
from time                 import sleep
from unittest             import mock

from pytest               import mark

from pyTooling.Tracing    import OTLP_SCOPE_NAME, Event, Span, Trace, TraceCollection, TraceElement, TracingError
from pyTooling            import Resources
from pyTooling.Common     import __version__, getResourceFile, readResourceFile
from pyTooling.Exceptions import MissingDependencyError
from pyTooling.Warning    import DirectoryCreatedWarning, WarningCollector
from pyTooling.Testing    import Testcase

# 'jsonschema' needs 'rpds-py', a Rust extension without a PyPy wheel for Windows; its source build fails to link there.
try:
	from jsonschema         import Draft202012Validator
	HAS_JSONSCHEMA = True
except ImportError:  # pragma: no cover
	HAS_JSONSCHEMA = False

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


skipWithoutJSONSchema = mark.skipif(
	not HAS_JSONSCHEMA,
	reason="Needs 'jsonschema', which can't be installed on PyPy for Windows."
)
"""Skip a testcase reading OTLP/JSON, which validates against a JSON schema, where 'jsonschema' isn't installed."""


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
		self.assertEqual({"stringValue": "text"}, TraceElement._ToOTLPAnyValue("text"))

	def test_Integer(self) -> None:
		"""A 64-bit integer is a string in OTLP/JSON, because JSON numbers cannot carry 64 bits exactly."""
		self.assertEqual({"intValue": "42"}, TraceElement._ToOTLPAnyValue(42))

	def test_Boolean(self) -> None:
		"""``bool`` is a subclass of ``int``, so the order of the checks decides this one."""
		self.assertEqual({"boolValue": True}, TraceElement._ToOTLPAnyValue(True))

	def test_Float(self) -> None:
		self.assertEqual({"doubleValue": 0.5}, TraceElement._ToOTLPAnyValue(0.5))

	def test_List(self) -> None:
		self.assertEqual(
			{"arrayValue": {"values": [{"stringValue": "a"}, {"intValue": "1"}]}},
			TraceElement._ToOTLPAnyValue(["a", 1])
		)

	def test_Tuple(self) -> None:
		"""Tuple is an array too."""
		self.assertEqual({"arrayValue": {"values": [{"intValue": "1"}]}}, TraceElement._ToOTLPAnyValue((1,)))

	def test_Dictionary(self) -> None:
		"""OTLP's 'KeyValueList' is a mapping, and it nests - a value of it is an 'AnyValue' again."""
		self.assertEqual(
			{"kvlistValue": {"values": [
				{"key": "a", "value": {"intValue": "1"}},
				{"key": "b", "value": {"arrayValue": {"values": [{"boolValue": True}]}}},
			]}},
			TraceElement._ToOTLPAnyValue({"a": 1, "b": [True]})
		)

	def test_Bytes(self) -> None:
		"""'bytesValue' is a 'bytes' field in proto3, and proto3's JSON mapping encodes those as base64."""
		self.assertEqual({"bytesValue": "AAH/"}, TraceElement._ToOTLPAnyValue(b"\x00\x01\xff"))

	def test_UnsupportedType(self) -> None:
		"""A silent 'str(value)' would put a Python repr into a document a backend then indexes."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceElement._ToOTLPAnyValue(object())

		self.assertEqual(
			"Attribute value of type 'object' can't be represented in OTLP.",
			str(exceptionCapture.exception)
		)
		self.assertEqual(
			["Supported are: bool, int, float, str, bytes, and a list, tuple or dict of these."],
			exceptionCapture.exception.__notes__
		)

	def test_UnsupportedType_Nested(self) -> None:
		"""An unsupported type is rejected inside a container."""
		with self.assertRaises(TracingError):
			TraceElement._ToOTLPAnyValue(["fine", None])


class Document(Testcase):
	"""The exported document's shape."""

	def test_Envelope(self) -> None:
		"""The envelope names the service and the scope."""
		document = _exampleTrace().ToOTLPJSON(serviceName="myProgram")
		resourceSpans = document["resourceSpans"][0]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			resourceSpans["resource"]["attributes"]
		)
		self.assertEqual(OTLP_SCOPE_NAME, resourceSpans["scopeSpans"][0]["scope"]["name"])

	def test_ServiceName_Default(self) -> None:
		"""The service name defaults to the trace's name."""
		document = _exampleTrace().ToOTLPJSON()

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "build"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_OnlyTrace(self) -> None:
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

	def test_AllSpans(self) -> None:
		"""Every span is exported."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertEqual({"build", "compile", "link"}, set(spans))

	def test_TraceID(self) -> None:
		"""All spans share one trace identifier."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		identifiers = {span["traceId"] for span in spans.values()}

		self.assertEqual(1, len(identifiers))
		self.assertEqual(32, len(identifiers.pop()), "A trace identifier is 16 bytes, hex-encoded.")

	def test_ParentSpanID(self) -> None:
		"""The hierarchy is carried by 'parentSpanId'."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertNotIn("parentSpanId", spans["build"], "The trace itself has no parent.")
		self.assertEqual(spans["build"]["spanId"], spans["compile"]["parentSpanId"])
		self.assertEqual(spans["build"]["spanId"], spans["link"]["parentSpanId"])

	def test_SpanID(self) -> None:
		"""A span identifier is eight bytes."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		for name, span in spans.items():
			with self.subTest(span=name):
				self.assertEqual(16, len(span["spanId"]))
				self.assertEqual(span["spanId"], span["spanId"].lower(), "OTLP/JSON uses lower-case hex.")

	def test_Duration(self) -> None:
		"""A span's duration is in seconds while OTLP wants nanoseconds, which is the easy factor to get wrong."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		compileSpan = spans["compile"]
		duration = int(compileSpan["endTimeUnixNano"]) - int(compileSpan["startTimeUnixNano"])

		self.assertGreater(duration, 1_000_000, "The span slept for a millisecond, so it lasted at least that.")
		self.assertLess(duration, 10_000_000_000, "A millisecond must not be reported as seconds.")

	def test_Duration_Measured(self) -> None:
		"""The counter's nanoseconds are what 'DurationInSeconds' divides by 1e9, and multiplying that back loses one."""
		with Trace("trace") as trace:
			with Span("span") as span:
				sleep(0.001)

		exported = self._Spans(trace.ToOTLPJSON())["span"]

		self.assertEqual(span._totalTime, int(exported["endTimeUnixNano"]) - int(exported["startTimeUnixNano"]))

	def test_Timestamps(self) -> None:
		"""proto3's JSON mapping encodes a 64-bit integer as a string."""
		for span in self._Spans(_exampleTrace().ToOTLPJSON()).values():
			with self.subTest(span=span["name"]):
				self.assertIsInstance(span["startTimeUnixNano"], str)
				self.assertIsInstance(span["endTimeUnixNano"], str)

	def test_Attributes(self) -> None:
		"""Attributes are exported."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())
		attributes = {entry["key"]: entry["value"] for entry in spans["compile"]["attributes"]}

		self.assertEqual({"intValue": "12"}, attributes["files"])
		self.assertEqual({"boolValue": True}, attributes["optimized"])
		self.assertEqual({"doubleValue": 0.5}, attributes["ratio"])

	def test_Attributes_None(self) -> None:
		"""A span without attributes has no attribute key."""
		spans = self._Spans(_exampleTrace().ToOTLPJSON())

		self.assertNotIn("attributes", spans["link"])
		self.assertNotIn("events", spans["link"])

	def test_Status_Success(self) -> None:
		"""A successful span has no status."""
		for name, span in self._Spans(_exampleTrace().ToOTLPJSON()).items():
			with self.subTest(span=name):
				self.assertNotIn("status", span)

	def test_Status_Error(self) -> None:
		"""A span left by an exception reports ``STATUS_CODE_ERROR`` with the exception as message."""
		try:
			with Trace("build") as trace:
				with Span("compile"):
					raise ValueError("Syntax error in 'a.c'.")
		except ValueError:
			pass

		spans = self._Spans(trace.ToOTLPJSON())

		self.assertEqual({"code": 2, "message": "ValueError: Syntax error in 'a.c'."}, spans["compile"]["status"])
		self.assertEqual(spans["compile"]["status"], spans["build"]["status"])


class Events(Testcase):
	"""An event belongs to the span it was created in."""

	def test_Event(self) -> None:
		"""The event is exported."""
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}
		events = spans["compile"]["events"]

		self.assertEqual(1, len(events))
		self.assertEqual("cache miss", events[0]["name"])

	def test_Attributes(self) -> None:
		"""Its attributes are exported."""
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

	def test_Attributes_None(self) -> None:
		"""An event without attributes has no attribute key."""
		spans = {
			span["name"]: span
			for span in _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertNotIn("attributes", spans["compile"]["events"][0])

	def test_Time_Default(self) -> None:
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
		sinceEpoch = event.Time.astimezone(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
		self.assertEqual(
			str(sinceEpoch // timedelta(microseconds=1) * 1_000),
			spans["span"]["events"][0]["timeUnixNano"]
		)

	def test_Time_Given(self) -> None:
		"""An event with a time keeps it."""
		time = datetime(2026, 8, 25, 12, 0, 0)
		with Trace("trace") as trace:
			with Span("span") as span:
				Event("stamped", time=time, parent=span)

		spans = {
			exported["name"]: exported
			for exported in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual(str(int(time.timestamp()) * 1_000_000_000), spans["span"]["events"][0]["timeUnixNano"])

	def test_Time_Microseconds(self) -> None:
		"""Converted through float seconds, this timestamp's nanoseconds would end in 024 instead of 000."""
		time = datetime(2026, 10, 5, 12, 34, 56, 123457, tzinfo=timezone.utc)
		with Trace("trace") as trace:
			with Span("span") as span:
				Event("stamped", time=time, parent=span)

		spans = {
			exported["name"]: exported
			for exported in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual("1791203696123457000", spans["span"]["events"][0]["timeUnixNano"])


class WrittenFile(Testcase):
	"""The document reaches a file as JSON."""

	def test_File(self) -> None:
		"""The file is valid JSON and round trips."""
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

	def test_String(self) -> None:
		"""The string is the encoded document."""
		trace = _exampleTrace()

		self.assertEqual(trace.ToOTLPJSON(), json_loads(trace.ToOTLPJSONString()))

	def test_String_Compact(self) -> None:
		"""That is what a collector expects; an indent is for a human reading the file."""

		trace = _exampleTrace()

		self.assertNotIn("\n", trace.ToOTLPJSONString())
		self.assertIn("\n", trace.ToOTLPJSONString(indent=2))

	def test_String_ServiceName(self) -> None:
		"""The service name reaches the string."""
		document = json_loads(_exampleTrace().ToOTLPJSONString(serviceName="myProgram"))

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_File_Directory(self) -> None:
		"""'report/' rarely exists when a pipeline asks for a trace inside it."""

		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			with WarningCollector() as warnings:
				_exampleTrace().WriteOTLPJSONFile(path)

			self.assertTrue(path.exists())

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], DirectoryCreatedWarning)
		self.assertEqual(f"Directory '{path.parent}' doesn't exist and is created.", str(warnings[0]))
		self.assertEqual(path.parent, warnings[0].Directory)

	def test_File_DirectoryExists(self) -> None:
		"""An existing directory is used without a warning."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			with WarningCollector() as warnings:
				_exampleTrace().WriteOTLPJSONFile(path)

			self.assertTrue(path.exists())

		self.assertEqual(0, len(warnings))

	def test_File_DirectoryWithoutCollector(self) -> None:
		"""Without a collector, the warning is dropped and the directory is created."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			_exampleTrace().WriteOTLPJSONFile(path)

			self.assertTrue(path.exists())

	def test_File_PathType(self) -> None:
		"""A path is a path."""
		with TemporaryDirectory() as directory:
			with self.assertRaises(TypeError) as exceptionCapture:
				_exampleTrace().WriteOTLPJSONFile(f"{directory}/trace.json")

		self.assertEqual("Parameter 'jsonFile' is not of type 'Path'.", str(exceptionCapture.exception))
		self.assertEqual(["Got type 'str'."], exceptionCapture.exception.__notes__)


class Identifiers(Testcase):
	"""An all-zero identifier is invalid in OTLP, so it is drawn again - but not forever."""

	def test_TraceID(self) -> None:
		"""A trace identifier is 16 bytes, written as 32 lower-case hex digits."""
		identifier = Span._NewIdentifier(128)

		self.assertEqual(32, len(identifier))
		self.assertEqual(identifier, f"{int(identifier, 16):032x}")

	def test_SpanID(self) -> None:
		"""A span identifier is 8 bytes, written as 16 lower-case hex digits."""
		identifier = Span._NewIdentifier(64)

		self.assertEqual(16, len(identifier))
		self.assertEqual(identifier, f"{int(identifier, 16):016x}")

	def test_Zero_DrawnAgain(self) -> None:
		"""A zero is drawn again."""
		with mock.patch("pyTooling.Tracing.urandom", side_effect=(bytes(8), bytes(8), bytes.fromhex("0123456789abcdef"))):
			identifier = Span._NewIdentifier(64)

		self.assertEqual("0123456789abcdef", identifier)

	def test_Zero_Exhausted(self) -> None:
		"""Only zeros raise a 'TracingError'."""
		with mock.patch("pyTooling.Tracing.urandom", return_value=bytes(8)):
			with self.assertRaises(TracingError) as exceptionCapture:
				Span._NewIdentifier(64)

		self.assertEqual("Couldn't draw a non-zero 64-bit random identifier.", str(exceptionCapture.exception))
		self.assertEqual(["Tried 4 times."], exceptionCapture.exception.__notes__)


class WriteErrors(Testcase):
	"""A filesystem error is reported as a :exc:`~pyTooling.Tracing.TracingError` naming what failed."""

	def test_Directory(self) -> None:
		"""An uncreatable directory is reported."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "report" / "trace.json"
			with mock.patch("pathlib.Path.mkdir", side_effect=PermissionError("denied")):
				with self.assertRaises(TracingError) as exceptionCapture:
					_exampleTrace().WriteOTLPJSONFile(path)

		self.assertEqual(f"Directory '{path.parent}' couldn't be created.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)

	def test_File(self) -> None:
		"""An unwritable file is reported."""
		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			with mock.patch("pathlib.Path.open", side_effect=PermissionError("denied")):
				with self.assertRaises(TracingError) as exceptionCapture:
					_exampleTrace().WriteOTLPJSONFile(path)

		self.assertEqual(f"OTLP/JSON file '{path}' couldn't be written.", str(exceptionCapture.exception))
		self.assertIsInstance(exceptionCapture.exception.__cause__, PermissionError)


class Identity(Testcase):
	"""The identifiers belong to the data model, not to a conversion."""

	def test_TraceID_Stable(self) -> None:
		"""This is what the by-call generation couldn't do: two exports describe one trace, not two."""
		trace = _exampleTrace()

		first = trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		second = trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]

		self.assertEqual(first, second)
		self.assertEqual(trace.TraceID, first[0]["traceId"])

	def test_SpanID(self) -> None:
		"""A span knows its own identifier and its trace."""
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

	def test_ParentSpanID(self) -> None:
		"""'parentSpanId' is read off the parent relation."""
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

	def test_SpanID_Distinct(self) -> None:
		"""Every identifier of a trace is distinct."""
		spans = _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]
		identifiers = [span["spanId"] for span in spans]

		self.assertEqual(len(identifiers), len(set(identifiers)))

	def test_SpanWithoutTrace(self) -> None:
		"""A lone span has no 'traceId' to carry, and OTLP has no way of saying so."""
		span = Span("orphan")

		self.assertIsNone(span.Trace)
		with self.assertRaises(TracingError) as exceptionCapture:
			span._ToOTLPJSON()

		self.assertEqual("Timespan 'orphan' is not part of a trace.", str(exceptionCapture.exception))

	def test_Flattened(self) -> None:
		"""Every level returns its own list, so no caller passes one in to be filled."""
		trace = _exampleTrace()
		spans = trace._ToOTLPJSON()

		self.assertIsInstance(spans, list)
		self.assertListEqual(["build", "compile", "link"], [span["name"] for span in spans])


class InstrumentationScope(Testcase):
	"""Which library the spans are reported as coming from."""

	def test_Default(self) -> None:
		"""The pyTooling scope is the default."""
		scope = _exampleTrace().ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual(OTLP_SCOPE_NAME, scope["name"])
		self.assertEqual(__version__, scope["version"])

	def test_Parameters(self) -> None:
		"""A program wrapping pyTooling's tracing reports its own name, without touching the module."""
		scope = _exampleTrace().ToOTLPJSON(
			scopeName="myProgram.Instrumentation",
			scopeVersion="2.1.0"
		)["resourceSpans"][0]["scopeSpans"][0]["scope"]

		self.assertEqual({"name": "myProgram.Instrumentation", "version": "2.1.0"}, scope)

	def test_StringAndFile(self) -> None:
		"""It reaches the string and the file."""
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

INVALID_DOCUMENT = "OTLP/JSON document isn't valid according to JSON schema 'OTLP-Traces-v1.0.schema.json'."
"""Message of the error raised for a document the schema rejects."""

FIRST_SPAN = "document/resourceSpans/0/scopeSpans/0/spans/0"
"""Position of the first span of a document assembled by :func:`_document`, as a schema violation names it."""

SPAN_ID_PATTERN = "'^(?!0{16}$)[0-9a-fA-F]{16}$'"
"""The schema's pattern of a span identifier, as a violation quotes it."""

TRACE_ID_PATTERN = "'^(?!0{32}$)[0-9a-fA-F]{32}$'"
"""The schema's pattern of a trace identifier, as a violation quotes it."""


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


def _attributeDocument(value: dict) -> dict:
	"""
	Wrap an OTLP 'AnyValue' as the only attribute of the only span of a document.

	:param value: The 'AnyValue' mapping.
	:returns:     The document.
	"""
	return _document(_span("root", "1111111111111111", attributes=[{"key": "key", "value": value}]))


@skipWithoutJSONSchema
class ReadAttributeValues(Testcase):
	"""An OTLP 'AnyValue' is unwrapped to the Python value it carries."""

	def test_String(self) -> None:
		self.assertEqual("text", TraceElement._ParseOTLPAnyValue({"stringValue": "text"}, "value"))

	def test_Boolean(self) -> None:
		self.assertEqual(True, TraceElement._ParseOTLPAnyValue({"boolValue": True}, "value"))

	def test_Integer(self) -> None:
		"""A 64-bit integer arrives as a decimal string."""
		self.assertEqual(42, TraceElement._ParseOTLPAnyValue({"intValue": "42"}, "value"))

	def test_Integer_Number(self) -> None:
		"""proto3 writes an integer as a string, but accepts a JSON number, so this reader accepts one too."""
		self.assertEqual(42, TraceElement._ParseOTLPAnyValue({"intValue": 42}, "value"))

	def test_Float(self) -> None:
		self.assertEqual(0.5, TraceElement._ParseOTLPAnyValue({"doubleValue": 0.5}, "value"))

	def test_Float_Integer(self) -> None:
		"""A JSON number without a fraction decodes to an 'int', and that is a valid double."""
		self.assertEqual(2.0, TraceElement._ParseOTLPAnyValue({"doubleValue": 2}, "value"))

	def test_Float_Special(self) -> None:
		"""JSON has no 'NaN' and no infinities, so proto3's JSON mapping writes them as strings."""
		self.assertTrue(isnan(TraceElement._ParseOTLPAnyValue({"doubleValue": "NaN"}, "value")))
		self.assertEqual(inf, TraceElement._ParseOTLPAnyValue({"doubleValue": "Infinity"}, "value"))
		self.assertEqual(-inf, TraceElement._ParseOTLPAnyValue({"doubleValue": "-Infinity"}, "value"))

	def test_Bytes(self) -> None:
		self.assertEqual(b"\x00\x01\xff", TraceElement._ParseOTLPAnyValue({"bytesValue": "AAH/"}, "value"))

	def test_Bytes_URLSafe(self) -> None:
		"""proto3's JSON mapping accepts the URL-safe base64 alphabet too."""
		self.assertEqual(b"\x00\x01\xff", TraceElement._ParseOTLPAnyValue({"bytesValue": "AAH_"}, "value"))

	def test_Bytes_Unpadded(self) -> None:
		"""proto3's JSON mapping accepts base64 without its padding."""
		self.assertEqual(b"\x00\x01", TraceElement._ParseOTLPAnyValue({"bytesValue": "AAE"}, "value"))
	def test_Array(self) -> None:
		self.assertEqual(
			["a", 1],
			TraceElement._ParseOTLPAnyValue({"arrayValue": {"values": [{"stringValue": "a"}, {"intValue": "1"}]}}, "value")
		)

	def test_KeyValueList(self) -> None:
		self.assertEqual(
			{"a": 1, "b": [True]},
			TraceElement._ParseOTLPAnyValue({"kvlistValue": {"values": [
				{"key": "a", "value": {"intValue": "1"}},
				{"key": "b", "value": {"arrayValue": {"values": [{"boolValue": True}]}}},
			]}}, "value")
		)

	def test_Integer_Boolean(self) -> None:
		"""'bool' is a subclass of 'int' in Python, but a JSON 'true' is not a number."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"intValue": True}))

		self.assertEqual(INVALID_DOCUMENT, str(exceptionCapture.exception))
		self.assertEqual(
			[f"{FIRST_SPAN}/attributes/0/value/intValue: True is not of type 'string', 'integer'"],
			exceptionCapture.exception.__notes__
		)
	def test_UnknownField(self) -> None:
		"""A receiver ignores a field it doesn't know, so an 'AnyValue' of only that field carries no value."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"dateValue": "2026-08-26"}))

		self.assertEqual(
			"Field 'document.resourceSpans[0].scopeSpans[0].spans[0].attributes[0].value' carries no value.",
			str(exceptionCapture.exception)
		)
	def test_TwoValues(self) -> None:
		"""An 'AnyValue' names at most one value, and two of them leave the type undecided."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"intValue": "1", "stringValue": "1"}))

		self.assertEqual(INVALID_DOCUMENT, str(exceptionCapture.exception))
		self.assertEqual(
			[
				f"{FIRST_SPAN}/attributes/0/value: {{'intValue': '1', 'stringValue': '1'}} is valid under each of "
				"{'required': ['intValue']}, {'required': ['stringValue']}"
			],
			exceptionCapture.exception.__notes__
		)
	def test_Empty(self) -> None:
		"""OTLP allows an empty 'AnyValue', but an attribute of this data model has a value."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceElement._ParseOTLPAnyValue({}, "value")

		self.assertEqual("Field 'value' carries no value.", str(exceptionCapture.exception))
		self.assertEqual(
			["OTLP allows an empty 'AnyValue', but an attribute of a trace, a span or an event has a value."],
			exceptionCapture.exception.__notes__
		)
	def test_String_WrongType(self) -> None:
		"""A value that doesn't match its type is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"stringValue": 1}))

		self.assertEqual(
			[f"{FIRST_SPAN}/attributes/0/value/stringValue: 1 is not of type 'string'"],
			exceptionCapture.exception.__notes__
		)
	def test_Integer_Text(self) -> None:
		"""An integer that is no number is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"intValue": "12 files"}))

		self.assertEqual(
			[f"{FIRST_SPAN}/attributes/0/value/intValue: '12 files' does not match '^-?[0-9]+$'"],
			exceptionCapture.exception.__notes__
		)
	def test_Bytes_Invalid(self) -> None:
		"""Characters outside both base64 alphabets are rejected by the schema."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_attributeDocument({"bytesValue": "not base64!"}))

		self.assertEqual(
			[f"{FIRST_SPAN}/attributes/0/value/bytesValue: 'not base64!' does not match '^[A-Za-z0-9+/_-]*={{0,2}}$'"],
			exceptionCapture.exception.__notes__
		)

	def test_Bytes_Length(self) -> None:
		"""A length the schema can't check: five base64 characters can't be a whole number of bytes."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceElement._ParseOTLPAnyValue({"bytesValue": "AAAAA"}, "value")

		self.assertEqual("Field 'value.bytesValue' is not base64-encoded.", str(exceptionCapture.exception))
		self.assertEqual(["Got 'AAAAA'."], exceptionCapture.exception.__notes__)
	def test_DuplicateKey(self) -> None:
		"""A key-value pair holds one value, so the second one would silently replace the first."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceElement._ParseOTLPKeyValues([
				{"key": "files", "value": {"intValue": "1"}},
				{"key": "files", "value": {"intValue": "2"}},
			], "attributes")

		self.assertEqual("Field 'attributes' has more than one attribute named 'files'.", str(exceptionCapture.exception))
		self.assertEqual(
			["OTLP requires the keys of an attribute list to be unique."],
			exceptionCapture.exception.__notes__
		)

	def test_MissingValue(self) -> None:
		"""An attribute without a value carries an empty 'AnyValue'."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceElement._ParseOTLPKeyValues([{"key": "files"}], "attributes")

		self.assertEqual("Field 'attributes[0].value' carries no value.", str(exceptionCapture.exception))

	def test_EmptyKey(self) -> None:
		"""OpenTelemetry requires an attribute key to be a non-empty string."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span(
				"root", "1111111111111111", attributes=[{"key": "", "value": {"intValue": "1"}}]
			)))

		self.assertEqual(
			[f"{FIRST_SPAN}/attributes/0/key: '' should be non-empty"],
			exceptionCapture.exception.__notes__
		)


@skipWithoutJSONSchema
class RoundTrip(Testcase):
	"""A trace exported and read back is the trace it started as."""

	def test_Document(self) -> None:
		"""The strongest statement available: exporting the trace that was read produces the same document."""
		exported = _exampleTrace().ToOTLPJSONString(indent=2)

		self.assertEqual(exported, Trace.FromOTLPJSONString(exported).ToOTLPJSONString(indent=2))

	def test_Identifiers(self) -> None:
		"""The identifiers survive."""
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())

		self.assertEqual(trace.TraceID, read.TraceID)
		self.assertEqual(trace.SpanID, read.SpanID)
		self.assertEqual(
			[span.SpanID for span in trace.IterateSubSpans()],
			[span.SpanID for span in read.IterateSubSpans()]
		)

	def test_Tree(self) -> None:
		"""OTLP has no nesting, so this is the 'parentSpanId' references being resolved back into a tree."""
		read = Trace.FromOTLPJSON(_exampleTrace().ToOTLPJSON())

		self.assertEqual("build", read.Name)
		self.assertEqual(["compile", "link"], [span.Name for span in read.IterateSubSpans()])
		self.assertIs(read, next(read.IterateSubSpans()).Parent)
		self.assertIs(read, next(read.IterateSubSpans()).Trace)

	def test_Timestamps(self) -> None:
		"""A 'datetime' holds microseconds and the document holds nanoseconds, so the value is rounded, not cut."""
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())

		self.assertEqual(trace.StartTime, read.StartTime)
		self.assertEqual(trace.DurationInSeconds, read.DurationInSeconds)

	def test_Duration(self) -> None:
		"""The performance counter that measured the duration ran in another process; the difference survives."""
		document = _document(
			_span("span", "1234567890abcdef", startTimeUnixNano="1000000000", endTimeUnixNano="1000012345")
		)

		self.assertEqual(12345 / 1e9, Trace.FromOTLPJSON(document).DurationInSeconds)

	def test_Attributes(self) -> None:
		"""The attributes survive."""
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())
		compileSpan = next(read.IterateSubSpans())

		self.assertEqual("10.0.0", read["version"])
		self.assertEqual(12, compileSpan["files"])
		self.assertEqual(True, compileSpan["optimized"])
		self.assertEqual(0.5, compileSpan["ratio"])
		self.assertEqual(["a", "b"], compileSpan["targets"])

	def test_Tuple(self) -> None:
		"""OTLP has a single 'arrayValue', so this is the one conversion a round-trip cannot undo."""
		with Trace("trace") as trace:
			trace["targets"] = ("a", "b")

		self.assertEqual(["a", "b"], Trace.FromOTLPJSON(trace.ToOTLPJSON())["targets"])

	def test_Status(self) -> None:
		"""An exception can't be rebuilt from its type name and message, so the read timespan has none to export."""
		with self.assertRaises(ValueError):
			with Trace("trace") as trace:
				raise ValueError("Broken.")

		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())

		self.assertIsNone(read.Exception)
		self.assertNotIn("status", read.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"][0])

	def test_Events(self) -> None:
		"""The events survive."""
		trace = _exampleTrace()
		read = Trace.FromOTLPJSON(trace.ToOTLPJSON())
		event = next(next(read.IterateSubSpans()).IterateEvents())
		original = next(next(trace.IterateSubSpans()).IterateEvents())

		self.assertEqual("cache miss", event.Name)
		self.assertEqual(original.Time, event.Time)
		self.assertIs(next(read.IterateSubSpans()), event.Parent)

	def test_Timestamps_None(self) -> None:
		"""Its exported mapping has none either, so both are read back as absent rather than as the Unix epoch."""
		read = Trace.FromOTLPJSON(Trace("never entered").ToOTLPJSON())

		self.assertIsNone(read.StartTime)
		self.assertIsNone(read.StopTime)

	def test_File(self) -> None:
		"""The file round trips too."""
		trace = _exampleTrace()
		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "report" / "trace.json"
			trace.WriteOTLPJSONFile(jsonFile, indent=2)

			self.assertEqual(trace.TraceID, Trace.ReadOTLPJSONFile(jsonFile).TraceID)


@skipWithoutJSONSchema
class ReadSpans(Testcase):
	"""The flat list of spans is reassembled into the tree its 'parentSpanId' references describe."""

	def test_Root(self) -> None:
		"""The span without a parent becomes the trace."""
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
		))

		self.assertEqual("root", trace.Name)
		self.assertEqual(TRACE_ID, trace.TraceID)
		self.assertEqual("1111111111111111", trace.SpanID)
		self.assertEqual(["child"], [span.Name for span in trace.IterateSubSpans()])

	def test_ParentSpanID_Empty(self) -> None:
		"""proto3's JSON mapping may write an unset 'bytes' field as an empty string rather than omitting it."""
		trace = Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", parentSpanId="")))

		self.assertEqual("root", trace.Name)

	def test_SiblingOrder(self) -> None:
		"""The siblings keep their order."""
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("third", "4444444444444444", "1111111111111111"),
			_span("first", "2222222222222222", "1111111111111111"),
			_span("second", "3333333333333333", "1111111111111111"),
		))

		self.assertEqual(["third", "first", "second"], [span.Name for span in trace.IterateSubSpans()])

	def test_SeveralEntries(self) -> None:
		"""Nothing requires a producer to put one trace into one 'resourceSpans' entry."""
		document = _document(_span("root", "1111111111111111"))
		second = _document(_span("child", "2222222222222222", "1111111111111111"))
		document["resourceSpans"].append(second["resourceSpans"][0])

		self.assertEqual(["child"], [span.Name for span in Trace.FromOTLPJSON(document).IterateSubSpans()])

	def test_DeepNesting(self) -> None:
		"""Deeper than Python's recursion limit, so a recursive descent through 'parentSpanId' would not survive it."""
		spans = [_span("span1", f"{1:016x}")]
		spans.extend(_span(f"span{depth}", f"{depth:016x}", f"{depth - 1:016x}") for depth in range(2, 2001))

		span = Trace.FromOTLPJSON(_document(*spans))
		for _ in range(2, 2001):
			span = next(span.IterateSubSpans())

		self.assertEqual("span2000", span.Name)

	def test_Kind(self) -> None:
		"""Every timespan of this data model is 'SPAN_KIND_INTERNAL', so another kind is accepted and forgotten."""
		trace = Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", kind=2)))

		self.assertEqual("root", trace.Name)

	def test_Kind_Name(self) -> None:
		"""OTLP/JSON writes an enumeration value as its integer; the name is not allowed."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", kind="SPAN_KIND_SERVER")))

		self.assertEqual(
			[f"{FIRST_SPAN}/kind: 'SPAN_KIND_SERVER' is not of type 'integer'"],
			exceptionCapture.exception.__notes__
		)

	def test_UnknownField(self) -> None:
		"""An OTLP/JSON receiver ignores a field it doesn't know."""
		trace = Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", futureField={"value": 1})))

		self.assertEqual("root", trace.Name)


@skipWithoutJSONSchema
class ReadEvents(Testcase):
	"""An event is read back into the timespan it happened in."""

	def test_Event(self) -> None:
		"""The event is attached to its span."""
		trace = Trace.FromOTLPJSON(_document(_span(
			"root", "1111111111111111",
			events=[{"name": "cache miss", "timeUnixNano": "1787659200123456000"}]
		)))
		event = next(trace.IterateEvents())

		self.assertEqual("cache miss", event.Name)
		self.assertEqual(datetime.fromtimestamp(1787659200) + timedelta(microseconds=123456), event.Time)
		self.assertIs(trace, event.Parent)

	def test_Attributes(self) -> None:
		"""Its attributes are read."""
		trace = Trace.FromOTLPJSON(_document(_span(
			"root", "1111111111111111",
			events=[{
				"name":         "cache miss",
				"timeUnixNano": "1787659200000000000",
				"attributes":   [{"key": "key", "value": {"stringValue": "libghdl"}}],
			}]
		)))

		self.assertEqual("libghdl", next(trace.IterateEvents())["key"])

	def test_Time_Missing(self) -> None:
		"""OTLP reads a missing 'timeUnixNano' as the Unix epoch, which would place the event in 1970."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", events=[{"name": "no time"}])))

		self.assertIn("events[0].timeUnixNano' is missing.", str(exceptionCapture.exception))


@skipWithoutJSONSchema
class ReadIdentifiers(Testcase):
	"""A trace or span identifier is 32 or 16 hex digits, and never all zeros."""

	def test_UpperCase(self) -> None:
		"""The specification says lower case, but a 'parentSpanId' reference has to resolve either way."""
		trace = Trace.FromOTLPJSON(_document(
			_span("root", "AAAAAAAAAAAAAAAA", traceId=TRACE_ID.upper()),
			_span("child", "bbbbbbbbbbbbbbbb", "aaaaaaaaaaaaaaaa", traceId=TRACE_ID),
		))

		self.assertEqual("aaaaaaaaaaaaaaaa", trace.SpanID)
		self.assertEqual(TRACE_ID, trace.TraceID)
		self.assertEqual(["child"], [span.Name for span in trace.IterateSubSpans()])

	def test_Length(self) -> None:
		"""A too short identifier is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "abcdef")))

		self.assertEqual(INVALID_DOCUMENT, str(exceptionCapture.exception))
		self.assertEqual(
			[f"{FIRST_SPAN}/spanId: 'abcdef' does not match {SPAN_ID_PATTERN}"],
			exceptionCapture.exception.__notes__
		)
	def test_NonHexadecimal(self) -> None:
		"""'int(..., 16)' would accept a leading sign and surrounding whitespace, so the digits are checked."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", " 111111111111111")))

		self.assertEqual(
			[f"{FIRST_SPAN}/spanId: ' 111111111111111' does not match {SPAN_ID_PATTERN}"],
			exceptionCapture.exception.__notes__
		)

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "11111111g1111111")))

		self.assertEqual(
			[f"{FIRST_SPAN}/spanId: '11111111g1111111' does not match {SPAN_ID_PATTERN}"],
			exceptionCapture.exception.__notes__
		)
	def test_Zero(self) -> None:
		"""OTLP defines it as invalid, which is the rule 'Span._NewIdentifier' draws by."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "0000000000000000", traceId="0" * 32)))

		self.assertEqual(
			[
				f"{FIRST_SPAN}/spanId: '0000000000000000' does not match {SPAN_ID_PATTERN}",
				f"{FIRST_SPAN}/traceId: '00000000000000000000000000000000' does not match {TRACE_ID_PATTERN}"
			],
			exceptionCapture.exception.__notes__
		)
	def test_Duplicate(self) -> None:
		"""The same span identifier twice is rejected."""
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


@skipWithoutJSONSchema
class ReadBrokenTrees(Testcase):
	"""The spans of a trace form a tree below exactly one root, or the document is rejected."""

	def test_TwoRoots(self) -> None:
		"""Two roots are rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("one", "1111111111111111"), _span("two", "2222222222222222")))

		self.assertEqual(f"Trace '{TRACE_ID}' has 2 spans without a 'parentSpanId'.", str(exceptionCapture.exception))

	def test_Cycle(self) -> None:
		"""A cycle has no root at all."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("one", "1111111111111111", "2222222222222222"),
				_span("two", "2222222222222222", "1111111111111111"),
			))

		self.assertEqual(
			f"2 span(s) of trace '{TRACE_ID}' reference each other in a cycle.",
			str(exceptionCapture.exception)
		)

	def test_Fragment(self) -> None:
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

	def test_MissingRoot(self) -> None:
		"""Every span names a parent, and the one they lead up to hasn't been delivered."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("child", "2222222222222222", "1111111111111111")))

		self.assertEqual(
			f"Trace '{TRACE_ID}' has no span without a 'parentSpanId'.",
			str(exceptionCapture.exception)
		)

	def test_Cycle_Detached(self) -> None:
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


@skipWithoutJSONSchema
class ReadTimestamps(Testcase):
	"""A timespan carries both timestamps or neither, and the second one never precedes the first."""

	def test_StartOnly(self) -> None:
		"""Only a start is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", startTimeUnixNano="1000000000")))

		self.assertIn("endTimeUnixNano' is missing.", str(exceptionCapture.exception))

	def test_EndOnly(self) -> None:
		"""Only an end is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111", endTimeUnixNano="1000000000")))

		self.assertIn("startTimeUnixNano' is missing.", str(exceptionCapture.exception))

	def test_EndBeforeStart(self) -> None:
		"""An end before its start is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span(
				"root", "1111111111111111", startTimeUnixNano="2000000000", endTimeUnixNano="1000000000"
			)))

		self.assertIn("precedes", str(exceptionCapture.exception))

	def test_OutOfRange(self) -> None:
		"""A 64-bit nanosecond value reaches the year 2554, and 'datetime' stops at 9999."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span(
				"root", "1111111111111111",
				startTimeUnixNano="999999999999999999999", endTimeUnixNano="999999999999999999999"
			)))

		self.assertIn("is not a timestamp a 'datetime' can represent.", str(exceptionCapture.exception))

	def test_Rounding(self) -> None:
		"""The export scales a float, whose precision at today's epoch is about 256 ns - less than half a µs."""
		second = datetime.fromtimestamp(1)

		self.assertEqual(second + timedelta(microseconds=2), TraceElement._FromUnixNanoseconds(1_000_001_500))
		self.assertEqual(second + timedelta(microseconds=1), TraceElement._FromUnixNanoseconds(1_000_001_499))


@skipWithoutJSONSchema
class SelectATrace(Testcase):
	"""A document may hold more than one trace, and then the caller says which one to read."""

	def test_Default(self) -> None:
		"""The only trace is the default."""
		self.assertEqual(TRACE_ID, Trace.FromOTLPJSON(_document(_span("root", "1111111111111111"))).TraceID)

	def test_SeveralTraces(self) -> None:
		"""Several traces need parameter 'traceID'."""
		other = "fedcba9876543210fedcba9876543210"
		document = _document(_span("one", "1111111111111111"), _span("two", "2222222222222222", traceId=other))

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(document)

		self.assertEqual("OTLP/JSON document contains 2 traces.", str(exceptionCapture.exception))
		self.assertEqual("two", Trace.FromOTLPJSON(document, other).Name)
		self.assertEqual("one", Trace.FromOTLPJSON(document, TRACE_ID).Name)

	def test_UpperCase(self) -> None:
		"""The trace ID is matched in lower case."""
		document = _document(_span("root", "1111111111111111"))

		self.assertEqual("root", Trace.FromOTLPJSON(document, TRACE_ID.upper()).Name)

	def test_Unknown(self) -> None:
		"""An unknown trace ID is reported."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111")), "f" * 32)

		self.assertEqual(f"OTLP/JSON document contains no trace '{'f' * 32}'.", str(exceptionCapture.exception))

	def test_NoSpans(self) -> None:
		"""A document without spans is reported."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": []})

		self.assertEqual("OTLP/JSON document contains no spans.", str(exceptionCapture.exception))

	def test_TraceIDType(self) -> None:
		"""A trace ID is a string."""
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "1111111111111111")), 42)

		self.assertEqual("Parameter 'traceID' is not of type 'str'.", str(exceptionCapture.exception))


@skipWithoutJSONSchema
class ReadMalformedDocuments(Testcase):
	"""A field that is missing or of the wrong type is named by its position in the document."""

	def test_MissingField(self) -> None:
		"""A missing field is named by its path."""
		span = _span("root", "1111111111111111")
		del span["traceId"]

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(span))

		self.assertEqual(INVALID_DOCUMENT, str(exceptionCapture.exception))
		self.assertEqual([f"{FIRST_SPAN}: 'traceId' is a required property"], exceptionCapture.exception.__notes__)

	def test_MissingList(self) -> None:
		"""proto3's JSON mapping omits an empty list, so a missing 'scopeSpans' is no spans."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": [{"resource": {}}]})

		self.assertEqual("OTLP/JSON document contains no spans.", str(exceptionCapture.exception))
	def test_WrongType(self) -> None:
		"""A field of the wrong type is named by its path."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON({"resourceSpans": {}})

		self.assertEqual(["document/resourceSpans: {} is not of type 'array'"], exceptionCapture.exception.__notes__)

	def test_AllViolations(self) -> None:
		"""Every violation of the schema is a note of its own, ordered by its position."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("root", "abc", kind="internal")))

		self.assertEqual(
			[
				f"{FIRST_SPAN}/kind: 'internal' is not of type 'integer'",
				f"{FIRST_SPAN}/spanId: 'abc' does not match {SPAN_ID_PATTERN}"
			],
			exceptionCapture.exception.__notes__
		)

	def test_Document_None(self) -> None:
		with self.assertRaises(ValueError) as exceptionCapture:
			TraceCollection.FromOTLPJSON(None)

		self.assertEqual("Parameter 'document' is None.", str(exceptionCapture.exception))

	def test_Document_Type(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			TraceCollection.FromOTLPJSON([])

		self.assertEqual("Parameter 'document' is not of type 'dict'.", str(exceptionCapture.exception))
		self.assertEqual(["Got type 'list'."], exceptionCapture.exception.__notes__)

	def test_MissingJSONSchema(self) -> None:
		"""Writing needs no extra; reading validates with 'jsonschema', which is installed by 'pyTooling[tracing]'."""
		with mock.patch.dict("sys.modules", {"jsonschema": None}):
			with self.assertRaises(MissingDependencyError) as exceptionCapture:
				TraceCollection.FromOTLPJSON(_document(_span("root", "1111111111111111")))

		self.assertIsInstance(exceptionCapture.exception.__cause__, ImportError)
	def test_Name_Missing(self) -> None:
		"""A span without a name is rejected."""
		span = _span("root", "1111111111111111")
		del span["name"]

		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(span))

		self.assertEqual(
			"Field 'document.resourceSpans[0].scopeSpans[0].spans[0].name' is missing or empty.",
			str(exceptionCapture.exception)
		)

	def test_Name_Empty(self) -> None:
		"""A span with an empty name is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(
				_span("root", "1111111111111111"),
				_span("", "2222222222222222", "1111111111111111"),
			))

		self.assertEqual(
			"Field 'document.resourceSpans[0].scopeSpans[0].spans[1].name' is missing or empty.",
			str(exceptionCapture.exception)
		)

	def test_Name_Empty_Trace(self) -> None:
		"""A trace with an empty name is rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSON(_document(_span("", "1111111111111111")))

		self.assertEqual(
			"Field 'document.resourceSpans[0].scopeSpans[0].spans[0].name' is missing or empty.",
			str(exceptionCapture.exception)
		)


@skipWithoutJSONSchema
class ReadErrors(Testcase):
	"""Reading a string or a file reports what went wrong with it."""

	def test_InvalidJSON(self) -> None:
		"""Invalid JSON is reported."""
		with self.assertRaises(TracingError) as exceptionCapture:
			Trace.FromOTLPJSONString("{not json")

		self.assertEqual("OTLP/JSON document isn't valid JSON.", str(exceptionCapture.exception))

	def test_StringType(self) -> None:
		"""A string is a string."""
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.FromOTLPJSONString(42)

		self.assertEqual("Parameter 'jsonString' is not of type 'str'.", str(exceptionCapture.exception))

	def test_PathType(self) -> None:
		"""A path is a path."""
		with self.assertRaises(TypeError) as exceptionCapture:
			Trace.ReadOTLPJSONFile("trace.json")

		self.assertEqual("Parameter 'jsonFile' is not of type 'Path'.", str(exceptionCapture.exception))

	def test_UnreadableFile(self) -> None:
		"""An unreadable file is reported."""
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

	The second document's root span is a fragment, because the span enclosing it is in the first document.

	:returns: The original trace, the document holding its root and one branch, and the document holding the other.
	"""
	with Trace("build") as trace:
		with Span("compile"):
			with Span("parse"):
				sleep(0.001)

		with Span("link"):
			sleep(0.001)

	spans = {span["name"]: span for span in trace.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]}

	return trace, _document(spans["build"], spans["link"]), _document(spans["compile"], spans["parse"])


@skipWithoutJSONSchema
class Collections(Testcase):
	"""A collection holds what a document carries: several traces, and timespans that aren't part of one yet."""

	def test_CompleteTrace(self) -> None:
		"""A complete trace is a trace."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
		))

		self.assertEqual(1, collection.TraceCount)
		self.assertEqual(2, collection.SpanCount)
		self.assertEqual(0, collection.FragmentCount)
		self.assertFalse(collection.HasFragments)
		self.assertEqual("root", collection.Traces[0].Name)

	def test_SeveralTraces(self) -> None:
		"""A collection is for exactly this - 'Trace.FromOTLPJSON' reads one of them and rejects the rest."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("one", "1111111111111111"),
			_span("two", "2222222222222222", traceId=OTHER_TRACE_ID),
		))

		self.assertEqual(2, collection.TraceCount)
		self.assertEqual(["one", "two"], [trace.Name for trace in collection])
		self.assertEqual(TRACE_ID, collection[TRACE_ID].TraceID)
		self.assertEqual(OTHER_TRACE_ID, collection[OTHER_TRACE_ID].TraceID)

	def test_Fragment(self) -> None:
		"""A span without its parent is a fragment."""
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

	def test_Fragment_SubSpans(self) -> None:
		"""Only the fragment's *place* is unknown; the part of the tree that came with it is built."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("fragment", "2222222222222222", "3333333333333333"),
			_span("below", "4444444444444444", "2222222222222222"),
		))

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)
		self.assertEqual(["below"], [span.Name for span in collection.Fragments[0].IterateSubSpans()])

	def test_MissingRoot(self) -> None:
		"""A trace without its root span is only fragments."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("child", "2222222222222222", "1111111111111111")))

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)
		self.assertEqual(TRACE_ID, collection.TraceIDOfSpan("2222222222222222"))

	def test_Cycle(self) -> None:
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

	def test_TwoRoots(self) -> None:
		"""Two root spans are still rejected."""
		with self.assertRaises(TracingError) as exceptionCapture:
			TraceCollection.FromOTLPJSON(_document(_span("one", "1111111111111111"), _span("two", "2222222222222222")))

		self.assertEqual(f"Trace '{TRACE_ID}' has 2 spans without a 'parentSpanId'.", str(exceptionCapture.exception))

	def test_Schema(self) -> None:
		"""The shipped schema is itself a valid Draft 2020-12 schema."""
		schemaFile = TraceCollection.SCHEMA_FILES[TraceCollection.SCHEMA_VERSION_LATEST]

		Draft202012Validator.check_schema(json_loads(readResourceFile(Resources, schemaFile)))

	def test_SchemaFiles(self) -> None:
		"""Every schema version has a file in the package resources."""
		for version, schemaFile in TraceCollection.SCHEMA_FILES.items():
			with self.subTest(version=str(version)):
				self.assertTrue(getResourceFile(Resources, schemaFile).exists())


@skipWithoutJSONSchema
class MergingDocuments(Testcase):
	"""A distributed execution is exported per process, so a trace arrives in pieces and is reassembled."""

	def test_ParentFirst(self) -> None:
		"""The fragment finds its parent."""
		trace, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(first).AddOTLPJSON(second)

		self.assertFalse(collection.HasFragments)
		self.assertEqual(4, collection.SpanCount)
		self.assertEqual(trace.ToOTLPJSONString(), collection.Traces[0].ToOTLPJSONString())

	def test_FragmentFirst(self) -> None:
		"""The other order: the fragment waits, and the document carrying its parent collects it."""
		trace, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second)

		self.assertEqual(0, collection.TraceCount)
		self.assertEqual(1, collection.FragmentCount)

		collection.AddOTLPJSON(first)

		self.assertFalse(collection.HasFragments)
		self.assertEqual(trace.ToOTLPJSONString(), collection.Traces[0].ToOTLPJSONString())

	def test_SiblingOrder(self) -> None:
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

	def test_SubSpansJoinTrace(self) -> None:
		"""'_AddSpan' sets the fragment's trace; everything below it was carrying 'None' and has to be updated."""
		_, first, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second).AddOTLPJSON(first)
		built = collection.Traces[0]

		for span in (*built.IterateSubSpans(), *next(built.IterateSubSpans()).IterateSubSpans()):
			with self.subTest(span=span.Name):
				self.assertIs(built, span.Trace)

	def test_DuplicateSpan(self) -> None:
		"""A distributed trace is assembled from spans that were each exported once."""
		_, _, second = _splitExample()
		collection = TraceCollection.FromOTLPJSON(second)

		with self.assertRaises(TracingError) as exceptionCapture:
			collection.AddOTLPJSON(second)

		self.assertIn("Collection already contains a timespan", str(exceptionCapture.exception))

	def test_SecondRoot(self) -> None:
		"""A second root span for one trace is rejected."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("root", "1111111111111111")))

		with self.assertRaises(TracingError) as exceptionCapture:
			collection.AddOTLPJSON(_document(_span("other root", "2222222222222222")))

		self.assertEqual(f"Collection already contains trace '{TRACE_ID}'.", str(exceptionCapture.exception))

	def test_Atomic(self) -> None:
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


@skipWithoutJSONSchema
class CollectionLookup(Testcase):
	"""Traces and timespans are indexed by identifier, which is what lets a fragment be linked to its parent."""

	def _Collection(self) -> TraceCollection:
		return TraceCollection.FromOTLPJSON(_document(
			_span("root", "1111111111111111"),
			_span("child", "2222222222222222", "1111111111111111"),
			_span("fragment", "3333333333333333", "4444444444444444"),
		))

	def test_GetItem(self) -> None:
		"""A trace identifier is 32 hex digits and a span identifier is 16, so the two can't be confused."""
		collection = self._Collection()

		self.assertEqual("root", collection[TRACE_ID].Name)
		self.assertEqual("child", collection["2222222222222222"].Name)

	def test_GetItem_UpperCase(self) -> None:
		"""The identifier is matched in lower case."""
		collection = self._Collection()

		self.assertEqual("root", collection[TRACE_ID.upper()].Name)
		self.assertEqual("child", collection["2222222222222222"].Name)

	def test_GetItem_Length(self) -> None:
		"""An identifier of another length is no identifier."""
		collection = self._Collection()

		with self.assertRaises(KeyError):
			_ = collection["abc"]

	def test_Contains(self) -> None:
		"""Contains asks the same indexes."""
		collection = self._Collection()

		self.assertIn(TRACE_ID, collection)
		self.assertIn("2222222222222222", collection)
		self.assertIn("3333333333333333", collection, "A fragment is a timespan of the collection like any other.")
		self.assertNotIn(OTHER_TRACE_ID, collection)
		self.assertNotIn("4444444444444444", collection, "The awaited parent is exactly what isn't here.")

	def test_TraceIDOfSpan(self) -> None:
		"""It has no 'Trace' to ask, but its 'traceId' was in the document all the same."""
		collection = self._Collection()

		self.assertIsNone(collection["3333333333333333"].Trace)
		self.assertEqual(TRACE_ID, collection.TraceIDOfSpan("3333333333333333"))

	def test_IterateFragmentsOf(self) -> None:
		"""The fragments of one trace can be iterated."""
		collection = self._Collection()
		collection.AddOTLPJSON(_document(
			_span("elsewhere", "5555555555555555", "6666666666666666", traceId=OTHER_TRACE_ID)
		))

		self.assertEqual(["fragment"], [span.Name for span in collection.IterateFragmentsOf(TRACE_ID)])
		self.assertEqual(["elsewhere"], [span.Name for span in collection.IterateFragmentsOf(OTHER_TRACE_ID)])

	def test_LenAndIter(self) -> None:
		"""A fragment is not a trace, so it is neither counted nor iterated as one."""
		collection = self._Collection()

		self.assertEqual(1, len(collection))
		self.assertEqual(["root"], [trace.Name for trace in collection])

	def test_StrAndRepr(self) -> None:
		"""The representations count what is there."""
		collection = self._Collection()

		self.assertEqual("1 traces + 1 fragments", str(collection))
		self.assertEqual("TraceCollection: 1 traces, 3 spans, 1 fragments", repr(collection))

	def test_TraceIDOfSpan_Parameter(self) -> None:
		collection = self._Collection()

		with self.assertRaises(ValueError) as exceptionCapture:
			collection.TraceIDOfSpan(None)

		self.assertEqual("Parameter 'spanID' is None.", str(exceptionCapture.exception))

		with self.assertRaises(TypeError) as exceptionCapture:
			collection.TraceIDOfSpan(42)

		self.assertEqual("Parameter 'spanID' is not of type 'str'.", str(exceptionCapture.exception))

	def test_IterateFragmentsOf_Parameter(self) -> None:
		collection = self._Collection()

		with self.assertRaises(ValueError) as exceptionCapture:
			collection.IterateFragmentsOf(None)

		self.assertEqual("Parameter 'traceID' is None.", str(exceptionCapture.exception))

		with self.assertRaises(TypeError) as exceptionCapture:
			collection.IterateFragmentsOf(42)

		self.assertEqual("Parameter 'traceID' is not of type 'str'.", str(exceptionCapture.exception))

	def test_GetItem_Parameter(self) -> None:
		collection = self._Collection()

		with self.assertRaises(ValueError) as exceptionCapture:
			_ = collection[None]

		self.assertEqual("Parameter 'identifier' is None.", str(exceptionCapture.exception))

		with self.assertRaises(TypeError) as exceptionCapture:
			_ = collection[42]

		self.assertEqual("Parameter 'identifier' is not of type 'str'.", str(exceptionCapture.exception))

	def test_Contains_Parameter(self) -> None:
		collection = self._Collection()

		with self.assertRaises(ValueError) as exceptionCapture:
			_ = None in collection

		self.assertEqual("Parameter 'identifier' is None.", str(exceptionCapture.exception))

		with self.assertRaises(TypeError) as exceptionCapture:
			_ = 42 in collection

		self.assertEqual("Parameter 'identifier' is not of type 'str'.", str(exceptionCapture.exception))


@skipWithoutJSONSchema
class CollectionDocuments(Testcase):
	"""A collection writes an OTLP/JSON document back, fragments included."""

	def test_Document(self) -> None:
		"""The document is the same again."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_span("one", "1111111111111111"),
			_span("two", "2222222222222222", traceId=OTHER_TRACE_ID),
		))
		encoded = collection.ToOTLPJSONString(indent=2)

		self.assertEqual(encoded, TraceCollection.FromOTLPJSONString(encoded).ToOTLPJSONString(indent=2))

	def test_Fragment_ParentSpanID(self) -> None:
		"""Without its 'parentSpanId' it would read back as a second root span rather than as a fragment."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("fragment", "2222222222222222", "3333333333333333")))
		written = collection.ToOTLPJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"][0]

		self.assertEqual("3333333333333333", written["parentSpanId"])
		self.assertEqual(1, TraceCollection.FromOTLPJSON(collection.ToOTLPJSON()).FragmentCount)

	def test_ServiceName_NoRoot(self) -> None:
		"""There is no root span to take a name from, and 'service.name' has to say something."""
		collection = TraceCollection.FromOTLPJSON(_document(_span("fragment", "2222222222222222", "3333333333333333")))
		resource = collection.ToOTLPJSON()["resourceSpans"][0]["resource"]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": TRACE_ID}}],
			resource["attributes"]
		)

	def test_ResourceSpans(self) -> None:
		"""Every trace gets its own resource entry."""
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

	def test_StringAndFile(self) -> None:
		"""The string and the file are read back too."""
		_, first, second = _splitExample()

		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "report" / "traces.json"
			TraceCollection.FromOTLPJSON(first).WriteOTLPJSONFile(jsonFile, indent=2)

			collection = TraceCollection.ReadOTLPJSONFile(jsonFile)
			collection.AddOTLPJSONString(json_dumps(second))

		self.assertEqual(1, collection.TraceCount)
		self.assertFalse(collection.HasFragments)

	def test_File_Directory(self) -> None:
		"""A missing directory is created after a warning."""
		_, first, _ = _splitExample()

		with TemporaryDirectory() as directory:
			jsonFile = Path(directory) / "report" / "traces.json"
			with WarningCollector() as warnings:
				TraceCollection.FromOTLPJSON(first).WriteOTLPJSONFile(jsonFile)

			self.assertTrue(jsonFile.exists())

		self.assertEqual(1, len(warnings))
		self.assertIsInstance(warnings[0], DirectoryCreatedWarning)
		self.assertEqual(jsonFile.parent, warnings[0].Directory)

	def test_Empty(self) -> None:
		"""An empty collection is an empty document."""
		self.assertEqual({"resourceSpans": []}, TraceCollection().ToOTLPJSON())


@skipWithoutJSONSchema
class CollectionFormatting(Testcase):
	"""'Format' renders the traces, then whatever is still waiting for a parent."""

	def test_Fragments(self) -> None:
		"""The fragments are listed with what they wait for."""
		collection = TraceCollection.FromOTLPJSON(_document(
			_timedSpan("root", "1111111111111111"),
			_timedSpan("fragment", "2222222222222222", "3333333333333333"),
		))
		lines = list(collection.Format())

		self.assertIn("Fragments: 1", lines)
		self.assertTrue(any("waiting for span 3333333333333333" in line for line in lines))
		self.assertTrue(any("fragment" in line for line in lines))

	def test_NoTimestamps(self) -> None:
		"""A trace read from a document without timestamps has no duration, so 'Format' shows '--' for it."""
		lines = list(Trace.FromOTLPJSON(_document(_span("never entered", "1234567890abcdef"))).Format())

		self.assertEqual(2, len(lines))
		self.assertTrue(all("-- ms" in line for line in lines), lines)
