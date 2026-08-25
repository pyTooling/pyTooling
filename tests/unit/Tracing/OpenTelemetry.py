# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for :mod:`pyTooling.Tracing.OpenTelemetry`, which exports a software execution trace as OTLP/JSON.
"""
from json     import loads as json_loads
from pathlib  import Path
from tempfile import TemporaryDirectory
from time     import sleep

from pyTooling.Testing                import Testcase
from pyTooling.Tracing                import Event, Span, Trace
from pyTooling.Tracing.OpenTelemetry  import SCOPE_NAME, ToOTLP, WriteOTLP, toAttributeValue, toUnixNano

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
		self.assertEqual({"stringValue": "text"}, toAttributeValue("text"))

	def test_Integer(self) -> None:
		"""A 64-bit integer is a string in OTLP/JSON, because JSON numbers cannot carry 64 bits exactly."""
		self.assertEqual({"intValue": "42"}, toAttributeValue(42))

	def test_BooleanIsNotAnInteger(self) -> None:
		"""``bool`` is a subclass of ``int``, so the order of the checks decides this one."""
		self.assertEqual({"boolValue": True}, toAttributeValue(True))

	def test_Float(self) -> None:
		self.assertEqual({"doubleValue": 0.5}, toAttributeValue(0.5))

	def test_List(self) -> None:
		self.assertEqual(
			{"arrayValue": {"values": [{"stringValue": "a"}, {"intValue": "1"}]}},
			toAttributeValue(["a", 1])
		)

	def test_AnythingElseBecomesAString(self) -> None:
		self.assertEqual({"stringValue": "None"}, toAttributeValue(None))


class Document(Testcase):
	"""The exported document's shape."""
	def test_TheEnvelopeNamesTheServiceAndTheScope(self) -> None:
		document = ToOTLP(_exampleTrace(), serviceName="myProgram")
		resourceSpans = document["resourceSpans"][0]

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "myProgram"}}],
			resourceSpans["resource"]["attributes"]
		)
		self.assertEqual(SCOPE_NAME, resourceSpans["scopeSpans"][0]["scope"]["name"])

	def test_TheServiceNameDefaultsToTheTracesName(self) -> None:
		document = ToOTLP(_exampleTrace())

		self.assertEqual(
			[{"key": "service.name", "value": {"stringValue": "build"}}],
			document["resourceSpans"][0]["resource"]["attributes"]
		)

	def test_ATraceIsNotASpan(self) -> None:
		with self.assertRaises(TypeError) as exceptionCapture:
			ToOTLP(Span("not a trace"))

		self.assertEqual("Parameter 'trace' is not of type 'Trace'.", str(exceptionCapture.exception))


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
		spans = self._Spans(ToOTLP(_exampleTrace()))

		self.assertEqual({"build", "compile", "link"}, set(spans))

	def test_AllSpansShareOneTraceIdentifier(self) -> None:
		spans = self._Spans(ToOTLP(_exampleTrace()))
		identifiers = {span["traceId"] for span in spans.values()}

		self.assertEqual(1, len(identifiers))
		self.assertEqual(32, len(identifiers.pop()), "A trace identifier is 16 bytes, hex-encoded.")

	def test_TheHierarchyIsCarriedByParentSpanId(self) -> None:
		spans = self._Spans(ToOTLP(_exampleTrace()))

		self.assertNotIn("parentSpanId", spans["build"], "The trace itself has no parent.")
		self.assertEqual(spans["build"]["spanId"], spans["compile"]["parentSpanId"])
		self.assertEqual(spans["build"]["spanId"], spans["link"]["parentSpanId"])

	def test_ASpanIdentifierIsEightBytes(self) -> None:
		spans = self._Spans(ToOTLP(_exampleTrace()))

		for name, span in spans.items():
			with self.subTest(span=name):
				self.assertEqual(16, len(span["spanId"]))
				self.assertEqual(span["spanId"], span["spanId"].lower(), "OTLP/JSON uses lower-case hex.")

	def test_TheDurationSurvives(self) -> None:
		"""A span's duration is in seconds while OTLP wants nanoseconds, which is the easy factor to get wrong."""
		spans = self._Spans(ToOTLP(_exampleTrace()))
		compileSpan = spans["compile"]
		duration = int(compileSpan["endTimeUnixNano"]) - int(compileSpan["startTimeUnixNano"])

		self.assertGreater(duration, 1_000_000, "The span slept for a millisecond, so it lasted at least that.")
		self.assertLess(duration, 10_000_000_000, "A millisecond must not be reported as seconds.")

	def test_TheTimestampsAreStrings(self) -> None:
		"""proto3's JSON mapping encodes a 64-bit integer as a string."""
		for span in self._Spans(ToOTLP(_exampleTrace())).values():
			with self.subTest(span=span["name"]):
				self.assertIsInstance(span["startTimeUnixNano"], str)
				self.assertIsInstance(span["endTimeUnixNano"], str)

	def test_AttributesAreExported(self) -> None:
		spans = self._Spans(ToOTLP(_exampleTrace()))
		attributes = {entry["key"]: entry["value"] for entry in spans["compile"]["attributes"]}

		self.assertEqual({"intValue": "12"}, attributes["files"])
		self.assertEqual({"boolValue": True}, attributes["optimized"])
		self.assertEqual({"doubleValue": 0.5}, attributes["ratio"])

	def test_ASpanWithoutAttributesHasNoAttributeKey(self) -> None:
		spans = self._Spans(ToOTLP(_exampleTrace()))

		self.assertNotIn("attributes", spans["link"])
		self.assertNotIn("events", spans["link"])


class Events(Testcase):
	"""An event belongs to the span it was created in."""
	def test_TheEventIsExported(self) -> None:
		spans = {
			span["name"]: span
			for span in ToOTLP(_exampleTrace())["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}
		events = spans["compile"]["events"]

		self.assertEqual(1, len(events))
		self.assertEqual("cache miss", events[0]["name"])

	def test_AnEventWithoutATimeFallsBackToItsSpan(self) -> None:
		"""An event doesn't stamp the current time, and OTLP reads a missing one as the Unix epoch."""
		with Trace("trace") as trace:
			with Span("span") as span:
				Event("no time of its own", parent=span)

		spans = {
			exported["name"]: exported
			for exported in ToOTLP(trace)["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual(spans["span"]["startTimeUnixNano"], spans["span"]["events"][0]["timeUnixNano"])

	def test_AnEventWithATimeKeepsIt(self) -> None:
		from datetime import datetime

		time = datetime(2026, 8, 25, 12, 0, 0)
		with Trace("trace") as trace:
			with Span("span") as span:
				Event("stamped", time=time, parent=span)

		spans = {
			exported["name"]: exported
			for exported in ToOTLP(trace)["resourceSpans"][0]["scopeSpans"][0]["spans"]
		}

		self.assertEqual(toUnixNano(time), spans["span"]["events"][0]["timeUnixNano"])


class WrittenFile(Testcase):
	"""The document reaches a file as JSON."""
	def test_TheFileIsValidJSONAndRoundTrips(self) -> None:
		trace = _exampleTrace()

		with TemporaryDirectory() as directory:
			path = Path(directory) / "trace.json"
			WriteOTLP(trace, path, serviceName="myProgram", indent="\t")

			document = json_loads(path.read_text(encoding="utf-8"))

		self.assertEqual(ToOTLP(trace, "myProgram")["resourceSpans"][0]["scopeSpans"][0]["scope"],
		                 document["resourceSpans"][0]["scopeSpans"][0]["scope"])
		self.assertEqual(3, len(document["resourceSpans"][0]["scopeSpans"][0]["spans"]))
