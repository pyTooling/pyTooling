# ==================================================================================================================== #
#             _____           _ _              _   _ ____  ___                                                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _ | | | |  _ \|_ _|                                                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || | | | |_) || |                                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |_| |  _ < | |                                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)___/|_| \_\___|                                                        #
# |_|    |___/                          |___/                                                                          #
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
#
"""
Unit tests for :class:`pyTooling.URI.URN`: a Uniform Resource Name of :rfc:`8141`, read by :meth:`URN.Parse` and by
:meth:`URI.Parse`.
"""
from pyTooling.URI     import URI, URN, URLError, KeyValuePair
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_URN(self) -> None:
		urn = URN("isbn", "0451450523")

		self.assertIsInstance(urn, URI)
		self.assertEqual("urn", urn.Scheme)
		self.assertEqual("isbn", urn.NamespaceID)
		self.assertEqual("0451450523", urn.NamespaceSpecificString)
		self.assertEqual("isbn:0451450523", urn.SchemeSpecificPart)
		self.assertIsNone(urn.Resolution)
		self.assertIsNone(urn.Query)
		self.assertIsNone(urn.Fragment)
		self.assertEqual("urn:isbn:0451450523", str(urn))

	def test_Components(self) -> None:
		urn = URN("example", "a/b", "resolver", (KeyValuePair("k", "v"), ), "part")

		self.assertEqual("resolver", urn.Resolution)
		self.assertEqual("v", urn.Query["k"].Value)
		self.assertEqual("part", urn.Fragment)
		self.assertEqual("urn:example:a/b?+resolver?=k=v#part", str(urn))

	def test_Slots(self) -> None:
		self.assertFalse(hasattr(URN("isbn", "0451450523"), "__dict__"))

	def test_NamespaceID_Errors(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URN(None, "x")

		self.assertEqual("Parameter 'namespaceID' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URN(1, "x")

		self.assertEqual("Parameter 'namespaceID' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

		for namespaceID in ("x", "-ab", "ab-", "a_b", "a" * 33):
			with self.subTest(namespaceID=namespaceID):
				with self.assertRaises(ValueError) as context:
					_ = URN(namespaceID, "x")

				self.assertEqual("Parameter 'namespaceID' is no namespace identifier.", str(context.exception))

	def test_NamespaceSpecificString_Errors(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URN("isbn", None)

		self.assertEqual("Parameter 'namespaceSpecificString' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URN("isbn", 451)

		self.assertEqual("Parameter 'namespaceSpecificString' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

		with self.assertRaises(ValueError) as context:
			_ = URN("isbn", "")

		self.assertEqual("Parameter 'namespaceSpecificString' is empty.", str(context.exception))

	def test_Resolution_Error(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = URN("isbn", "0451450523", 1)

		self.assertEqual("Parameter 'resolution' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class Parsing(Testcase):
	def test_URNs(self) -> None:
		for text, namespaceID, namespaceSpecificString in (
			("urn:isbn:0451450523",                           "isbn",    "0451450523"),
			("urn:ietf:rfc:3986",                             "ietf",    "rfc:3986"),
			("urn:uuid:6e8bc430-9c3a-11d9-9669-0800200c9a66", "uuid",    "6e8bc430-9c3a-11d9-9669-0800200c9a66"),
			("urn:example:a/b/c",                             "example", "a/b/c"),
			("urn:example:%41b",                              "example", "%41b")
		):
			with self.subTest(urn=text):
				urn = URN.Parse(text)

				self.assertEqual(namespaceID, urn.NamespaceID)
				self.assertEqual(namespaceSpecificString, urn.NamespaceSpecificString)
				self.assertEqual(text, str(urn))

	def test_SchemeInAnyCase(self) -> None:
		""":rfc:`8141`: ``urn`` is case-insensitive; it is written in lower case."""
		urn = URN.Parse("URN:ISBN:0451450523")

		self.assertEqual("ISBN", urn.NamespaceID)
		self.assertEqual("urn:ISBN:0451450523", str(urn))

	def test_Components(self) -> None:
		urn = URN.Parse("urn:example:a?+resolve?with?marks?=k=v&k=w#f")

		self.assertEqual("resolve?with?marks", urn.Resolution)
		self.assertTupleEqual(("v", "w"), urn.Query["k"].Values)
		self.assertEqual("f", urn.Fragment)
		self.assertEqual("urn:example:a?+resolve?with?marks?=k=v&k=w#f", str(urn))

	def test_QueryComponentOnly(self) -> None:
		urn = URN.Parse("urn:example:a?=k=v")

		self.assertIsNone(urn.Resolution)
		self.assertEqual("v", urn.Query["k"].Value)

	def test_ByURIParse(self) -> None:
		urn = URI.Parse("urn:isbn:0451450523")

		self.assertIs(URN, type(urn))
		self.assertEqual("0451450523", urn.NamespaceSpecificString)

	def test_Errors(self) -> None:
		for text, message in (
			("isbn:0451450523",   "Missing 'urn:' when parsing URN 'isbn:0451450523'."),
			("urn:isbn",          "Missing namespace-specific string when parsing URN 'urn:isbn'."),
			("urn:isbn:",         "Missing namespace-specific string when parsing URN 'urn:isbn:'."),
			("urn:isbn:/0451",    "Syntax error when parsing URN 'urn:isbn:/0451'."),
			("urn:isbn:04?x",     "Syntax error when parsing URN 'urn:isbn:04?x'.")
		):
			with self.subTest(urn=text):
				with self.assertRaises(URLError) as context:
					_ = URN.Parse(text)

				self.assertEqual(message, str(context.exception))

	def test_NamespaceID_Error(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URN.Parse("urn:x:abc")

		self.assertEqual("Invalid namespace identifier 'x' when parsing URN 'urn:x:abc'.", str(context.exception))
		self.assertListEqual(
			["A namespace identifier has 2 to 32 letters, digits or '-', and neither starts nor ends with '-'."],
			context.exception.__notes__
		)

	def test_ForbiddenCharacter(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URN.Parse("urn:isbn:04 51")

		self.assertEqual("Forbidden character when parsing URN 'urn:isbn:04 51'.", str(context.exception))
		self.assertListEqual(
			["Character ' ' is not allowed in a URN. Write it percent-encoded as '%20'."],
			context.exception.__notes__
		)

	def test_Parameter(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URN.Parse(None)

		self.assertEqual("Parameter 'urn' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URN.Parse(1)

		self.assertEqual("Parameter 'urn' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
