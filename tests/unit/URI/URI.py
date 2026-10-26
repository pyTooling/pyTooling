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
Unit tests for :class:`pyTooling.URI.URI`: the generic URI, :meth:`URI.Parse` returning a URL for a URL, and
``URL.Parse(..., defaultScheme=...)``.
"""
from pyTooling.URI     import URI, URL, URLError, Protocols, Host, Path, KeyValuePair
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_URI(self) -> None:
		uri = URI("mailto", "user@example.org", (KeyValuePair("subject", "Hi"), ), "top")

		self.assertEqual("mailto", uri.Scheme)
		self.assertEqual("user@example.org", uri.SchemeSpecificPart)
		self.assertEqual("Hi", uri.Query["subject"].Value)
		self.assertEqual("top", uri.Fragment)
		self.assertEqual("mailto:user@example.org?subject=Hi#top", str(uri))

	def test_SchemeInLowerCase(self) -> None:
		""":rfc:`3986` schemes are case-insensitive; the canonical form is lower case."""
		self.assertEqual("mailto", URI("MailTo", "user@example.org").Scheme)

	def test_URL(self) -> None:
		url = URL(Protocols.HTTPS, Path.Parse("/api"), Host("example.org", 8080), "user")

		self.assertIsInstance(url, URI)
		self.assertIs(Protocols.HTTPS, url.Scheme)
		self.assertEqual("//user@example.org:8080/api", url.SchemeSpecificPart)
		self.assertEqual("https://user@example.org:8080/api", str(url))

	def test_Slots(self) -> None:
		self.assertFalse(hasattr(URI("tel", "+49-761-0"), "__dict__"))
		self.assertFalse(hasattr(URL(Protocols.HTTPS, Path.Parse("/"), Host("example.org")), "__dict__"))

	def test_Scheme_Errors(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URI(None, "x")

		self.assertEqual("Parameter 'scheme' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URI(1, "x")

		self.assertEqual("Parameter 'scheme' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

		with self.assertRaises(ValueError) as context:
			_ = URI("1x", "x")

		self.assertEqual("Parameter 'scheme' is no scheme name.", str(context.exception))
		self.assertListEqual(
			["Got value '1x'. A scheme starts with a letter, followed by letters, digits, '+', '-' or '.'."],
			context.exception.__notes__
		)

	def test_SchemeSpecificPart_Error(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = URI("tel", 49)

		self.assertEqual("Parameter 'schemeSpecificPart' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_URL_Scheme_Errors(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URL(None, Path.Parse("/"), Host("example.org"))

		self.assertEqual("Parameter 'scheme' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URL("https", Path.Parse("/"), Host("example.org"))

		self.assertEqual("Parameter 'scheme' is not of type 'Protocols'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)


class Parsing(Testcase):
	def test_OpaqueURIs(self) -> None:
		for text, scheme, schemeSpecificPart in (
			("mailto:user@example.org", "mailto", "user@example.org"),
			("tel:+49-761-123456",      "tel",    "+49-761-123456"),
			("urn:isbn:0451450523",     "urn",    "isbn:0451450523"),
			("sip:alice@example.org",   "sip",    "alice@example.org"),
			("news:comp.lang.python",   "news",   "comp.lang.python")
		):
			with self.subTest(uri=text):
				uri = URI.Parse(text)

				self.assertIs(URI, type(uri))
				self.assertEqual(scheme, uri.Scheme)
				self.assertEqual(schemeSpecificPart, uri.SchemeSpecificPart)
				self.assertEqual(text, str(uri))

	def test_QueryAndFragment(self) -> None:
		uri = URI.Parse("mailto:user@example.org?subject=Hi&cc=a@example.org&cc=b@example.org#x")

		self.assertEqual("Hi", uri.Query["subject"].Value)
		self.assertTupleEqual(("a@example.org", "b@example.org"), uri.Query["cc"].Values)
		self.assertEqual("x", uri.Fragment)
		self.assertEqual("mailto:user@example.org?subject=Hi&cc=a@example.org&cc=b@example.org#x", str(uri))

	def test_URL(self) -> None:
		"""A URI with an authority and a scheme of :class:`Protocols` is a URL."""
		for text in ("https://example.org/api?x=1#f", "file:///etc/hosts", "ssh://git@github.com/org/repo.git"):
			with self.subTest(uri=text):
				uri = URI.Parse(text)

				self.assertIsInstance(uri, URL)
				self.assertEqual(text, str(uri))

	def test_UnknownSchemeWithAuthority(self) -> None:
		"""A scheme :class:`Protocols` doesn't know stays a URI, even with an authority."""
		uri = URI.Parse("foo://example.org/path")

		self.assertIs(URI, type(uri))
		self.assertEqual("foo", uri.Scheme)
		self.assertEqual("//example.org/path", uri.SchemeSpecificPart)

	def test_URLChecks(self) -> None:
		"""A URL is read by :meth:`URL.Parse`, with its checks."""
		with self.assertRaises(URLError) as context:
			_ = URI.Parse("https://host:99999/")

		self.assertEqual(
			"Port 99999 is out of range 0..65535 when parsing URL 'https://host:99999/'.",
			str(context.exception)
		)

	def test_Errors(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URI.Parse("nonsense")

		self.assertEqual("Missing scheme when parsing URI 'nonsense'.", str(context.exception))
		self.assertListEqual(["A URI starts with a scheme followed by ':', e.g. 'mailto:'."], context.exception.__notes__)

		with self.assertRaises(URLError) as context:
			_ = URI.Parse("mailto:a b@example.org")

		self.assertEqual("Forbidden character when parsing URI 'mailto:a b@example.org'.", str(context.exception))
		self.assertListEqual(
			["Character ' ' is not allowed in a URI. Write it percent-encoded as '%20'."],
			context.exception.__notes__
		)

		with self.assertRaises(URLError) as context:
			_ = URI.Parse("mailto:müller@example.org")

		self.assertEqual("Non-ASCII character when parsing URI 'mailto:müller@example.org'.", str(context.exception))

	def test_Parameter(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URI.Parse(None)

		self.assertEqual("Parameter 'uri' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URI.Parse(1)

		self.assertEqual("Parameter 'uri' is not of type 'str'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)


class DefaultScheme(Testcase):
	"""``URL.Parse(..., defaultScheme=...)`` prepends a scheme to a URL without one, as a browser does."""

	def test_Prepended(self) -> None:
		for text, url in (
			("www.example.org/path",  "https://www.example.org/path"),
			("example.org",           "https://example.org"),
			("user@example.org:8080", "https://user@example.org:8080"),
			("//example.org/path",    "https://example.org/path")
		):
			with self.subTest(url=text):
				self.assertEqual(url, str(URL.Parse(text, defaultScheme=Protocols.HTTPS)))

	def test_SchemeGiven(self) -> None:
		self.assertIs(Protocols.FTP, URL.Parse("ftp://example.org/", defaultScheme=Protocols.HTTPS).Scheme)

	def test_Strict(self) -> None:
		"""Without ``defaultScheme``, a URL without a scheme still raises."""
		with self.assertRaises(URLError):
			_ = URL.Parse("www.example.org/path")

	def test_IRI(self) -> None:
		url = URL.Parse("www.müller.de/", iri=True, defaultScheme=Protocols.HTTPS)

		self.assertEqual("https://www.xn--mller-kva.de/", str(url))

	def test_ErrorNote(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("example.org:99999", defaultScheme=Protocols.HTTPS)

		self.assertEqual(
			"Port 99999 is out of range 0..65535 when parsing URL 'https://example.org:99999'.",
			str(context.exception)
		)
		self.assertListEqual(["Scheme 'https' was prepended to 'example.org:99999'."], context.exception.__notes__)

	def test_Parameter(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = URL.Parse("example.org", defaultScheme="https")

		self.assertEqual("Parameter 'defaultScheme' is not of type 'Protocols'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)
