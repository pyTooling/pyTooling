# ==================================================================================================================== #
#             _____           _ _               ____                      _      ____       _   _                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| ___ _ __   ___ _ __(_) ___|  _ \ __ _| |_| |__                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |  _ / _ \ '_ \ / _ \ '__| |/ __| |_) / _` | __| '_ \                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |_| |  __/ | | |  __/ |  | | (__|  __/ (_| | |_| | | |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|\___|_| |_|\___|_|  |_|\___|_|   \__,_|\__|_| |_|                 #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for :mod:`pyTooling.GenericPath` and :mod:`pyTooling.GenericPath.URL`: parsing a URL into its
parts and rendering it back.
"""
from sys                       import modules
from unittest.mock             import patch

from pyTooling.Exceptions      import MissingDependencyError, ToolingException
from pyTooling.GenericPath.URL import Host, Path, URL, URLError, Protocols
from pyTooling.Testing         import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Schemes(Testcase):
	def test_SecuredSchemeIsTLSPlusProtocol(self) -> None:
		self.assertEqual(Protocols.TLS | Protocols.HTTP, Protocols.HTTPS)
		self.assertEqual(Protocols.TLS | Protocols.FTP, Protocols.FTPS)

	def test_SecuredSchemeContainsTLS(self) -> None:
		self.assertIn(Protocols.TLS, Protocols.HTTPS)
		self.assertIn(Protocols.TLS, Protocols.FTPS)

	def test_PlainSchemeContainsNoTLS(self) -> None:
		self.assertNotIn(Protocols.TLS, Protocols.HTTP)
		self.assertNotIn(Protocols.TLS, Protocols.FTP)
		self.assertNotIn(Protocols.TLS, Protocols.FILE)

	def test_SecuredSchemeContainsPlainScheme(self) -> None:
		self.assertIn(Protocols.HTTP, Protocols.HTTPS)
		self.assertIn(Protocols.FTP, Protocols.FTPS)

	def test_CombinationIsNamedLikeTheSecuredScheme(self) -> None:
		self.assertEqual("HTTPS", (Protocols.TLS | Protocols.HTTP).name)
		self.assertEqual("FTPS", (Protocols.TLS | Protocols.FTP).name)

	def test_SchemeByName(self) -> None:
		self.assertEqual(Protocols.HTTPS, Protocols["HTTPS"])
		self.assertEqual(Protocols.FTPS, Protocols["FTPS"])


class GenericPath(Testcase):
	url : URL = URL.Parse("https://pyTooling.GitHub.io:8080/path/to/endpoint?user=paebbels&token=1234567890")

	def test_Protocol(self) -> None:
		self.assertEqual(self.url.Scheme, Protocols.HTTPS)

	def test_Port(self) -> None:
		self.assertEqual(self.url.Host.Port, 8080)

	def test_Hostname(self) -> None:
		self.assertEqual(self.url.Host.Hostname, "pyTooling.GitHub.io")

	def test_str(self) -> None:
		self.assertEqual(str(self.url), "https://pyTooling.GitHub.io:8080/path/to/endpoint?user=paebbels&token=1234567890")


class URLs(Testcase):
	def test_Host(self) -> None:
		resource = "http://github"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_IP(self) -> None:
		resource = "http://192.168.1.1"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("192.168.1.1", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS(self) -> None:
		resource = "http://github.com."
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com.", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port(self) -> None:
		resource = "http://github.com:80"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path(self) -> None:
		resource = "http://github.com:80/entrypoint"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/entrypoint", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File(self) -> None:
		resource = "http://github.com:80/path/file.png"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_Query(self) -> None:
		resource = "http://github.com:80/path/file.png?width=1024"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024"}, url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_QueryQuery(self) -> None:
		resource = "http://github.com:80/path/file.png?width=1024&height=912"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024", "height": "912"}, url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_Fragment(self) -> None:
		resource = "http://github.com:80/entrypoint#chapter-3"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/entrypoint", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertEqual("chapter-3", url.Fragment)

		self.assertEqual(resource, str(url))

	def test_HTTP_DNS(self) -> None:
		resource = "http://github.com"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_HTTPS_DNS(self) -> None:
		resource = "https://github.com"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_HTTPS_DNS_Port(self) -> None:
		resource = "https://github.com:443"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(443, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_HTTPS_User_DNS_Port(self) -> None:
		resource = "https://paebbels@v-4.github.com:25005"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("v-4.github.com", url.Host.Hostname)
		self.assertEqual(25005, url.Host.Port)
		self.assertEqual("paebbels", url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_HTTPS_User_Pwd_DNS(self) -> None:
		resource = "https://paebbels:foobar@v4.api.github.com"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("v4.api.github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertEqual("paebbels", url.User)
		self.assertEqual("foobar", url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_GitLabCIToken(self) -> None:
		resource = "https://gitlab-ci-token:glcbt-64_2yjksyWRz6mPq57YFsvx@gitlab.company.com/path/to/resource.ext?query1=34&query2=343#ref-45"
		url = URL.Parse(resource)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("gitlab.company.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertEqual("gitlab-ci-token", url.User)
		self.assertEqual("glcbt-64_2yjksyWRz6mPq57YFsvx", url.Password)
		self.assertEqual("/path/to/resource.ext", str(url.Path))
		self.assertDictEqual({"query1": "34", "query2": "343"}, url.Query)
		self.assertEqual("ref-45", url.Fragment)

		self.assertEqual(resource, str(url))

		cleanURL = url.WithoutCredentials()

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("gitlab.company.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(cleanURL.User)
		self.assertIsNone(cleanURL.Password)
		self.assertEqual("/path/to/resource.ext", str(url.Path))
		self.assertDictEqual({"query1": "34", "query2": "343"}, url.Query)
		self.assertEqual("ref-45", url.Fragment)




class Concatenation(Testcase):
	"""What ``URL / resource`` composes, and what it takes from which side."""

	def test_AResourceBelowTheURL(self) -> None:
		base = URL.Parse("https://example.org/api/v3")

		for resource, expected in (
			("things", "https://example.org/api/v3/things"),
			("things/4711", "https://example.org/api/v3/things/4711"),
			("things?per_page=100", "https://example.org/api/v3/things?per_page=100"),
			("things#ref", "https://example.org/api/v3/things#ref"),
		):
			with self.subTest(resource=resource):
				self.assertEqual(expected, str(base / resource))

	def test_ATrailingSlashDoesNotBecomeAnEmptyElement(self) -> None:
		for base in ("https://example.org/api/", "https://example.org/api", "https://example.org/"):
			with self.subTest(base=base):
				self.assertNotIn("//", str(URL.Parse(base) / "things").removeprefix("https://"))

	def test_AnAbsolutePathNamesItsOwnRoot(self) -> None:
		"""A path starting with the delimiter says where it starts, as RFC 3986 resolves a reference."""
		self.assertEqual("https://example.org/other", str(URL.Parse("https://example.org/api/v3") / "/other"))

	def test_TheQueryComesFromTheRightSide(self) -> None:
		"""A relative reference brings its own query; the base URL's isn't carried into it."""
		composed = URL.Parse("https://example.org/api?token=abc") / "things?fields=name"

		self.assertEqual("https://example.org/api/things?fields=name", str(composed))
		self.assertDictEqual({"fields": "name"}, composed.Query)

	def test_TheHostAndCredentialsAreKept(self) -> None:
		composed = URL.Parse("https://user:pass@example.org:8443/api") / "things"

		self.assertEqual("https://user:pass@example.org:8443/api/things", str(composed))
		self.assertEqual(8443, composed.Host.Port)

	def test_APathObject(self) -> None:
		composed = URL.Parse("https://example.org/api") / URL.Parse("https://elsewhere.org/things").Path

		self.assertEqual("https://example.org/things", str(composed), "That path is absolute, so it replaces.")

	def test_SomethingElse(self) -> None:
		for left in (URL.Parse("https://example.org/api"), URL.Parse("https://example.org/api").Path):
			with self.subTest(left=left.__class__.__name__):
				with self.assertRaises(TypeError) as context:
					_ = left / 4711

				self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_ACompleteURLOnTheRightSide(self) -> None:
		"""The right side names a resource below the URL, so a scheme or an authority is refused."""
		base = URL.Parse("https://example.org/api")

		for resource in ("https://elsewhere.org/things", "//elsewhere.org/things", "elsewhere.org:8443/things"):
			with self.subTest(resource=resource):
				with self.assertRaises(URLError):
					_ = base / resource

	def test_AColonBelowTheFirstElement(self) -> None:
		"""Only the first element of a relative path may not carry a ':' - RFC 3986's 'path-noscheme'."""
		self.assertEqual("https://example.org/api/things/a:b", str(URL.Parse("https://example.org/api") / "things/a:b"))
		self.assertEqual("https://example.org/a:b", str(URL.Parse("https://example.org/api") / "/a:b"))

	def test_AForbiddenCharacterOnTheRightSide(self) -> None:
		base = URL.Parse("https://example.org/api")

		for resource in ("things/a b", "things/a<b", "things/a\tb"):
			with self.subTest(resource=resource):
				with self.assertRaises(URLError) as context:
					_ = base / resource

				self.assertTrue(any("percent-encoded" in note for note in context.exception.__notes__))

	def test_AStringOnThePath(self) -> None:
		"""A path takes a string on the right, the way :class:`pathlib.PurePath` does."""
		path = URL.Parse("https://example.org/api/v3/").Path

		self.assertEqual("/api/v3/things/4711", str(path / "things/4711"))
		self.assertEqual("/other", str(path / "/other"), "An absolute path names its own root.")


class TrailingSlash(Testcase):
	"""What :meth:`~pyTooling.GenericPath.URL.URL.WithoutTrailingSlash` removes, and what it leaves alone."""

	def test_APathEndingInASlash(self) -> None:
		for url, expected in (
			("https://example.org/api/v3/", "https://example.org/api/v3"),
			("https://example.org/", "https://example.org"),
			("https://user:pass@example.org/api/", "https://user:pass@example.org/api"),
			("https://example.org/api/?query=1#ref", "https://example.org/api?query=1#ref"),
		):
			with self.subTest(url=url):
				self.assertEqual(expected, str(URL.Parse(url).WithoutTrailingSlash()))

	def test_APathEndingInSomethingElseIsThisURL(self) -> None:
		for url in ("https://example.org/api/v3", "https://example.org", "https://example.org/api/v3?query=1"):
			with self.subTest(url=url):
				parsedURL = URL.Parse(url)

				self.assertIs(parsedURL, parsedURL.WithoutTrailingSlash())

	def test_ThePathAnswersTheGenericMethod(self) -> None:
		"""'WithoutTrailingSlash' is 'WithoutTrailingDelimiter' applied to the URL's path."""
		path = URL.Parse("https://example.org/api/v3/").Path

		self.assertEqual("/api/v3", str(path.WithoutTrailingDelimiter()))

	def test_OnlyOneSlashIsRemoved(self) -> None:
		"""A path ending in '//' names an empty element and then another, which isn't the same as naming neither."""
		self.assertEqual("https://example.org/api/", str(URL.Parse("https://example.org/api//").WithoutTrailingSlash()))

	def test_TheURLIsUnchanged(self) -> None:
		url = URL.Parse("https://user:pass@example.org/api/?query=1#ref")
		shortenedURL = url.WithoutTrailingSlash()

		self.assertEqual("https://user:pass@example.org/api/?query=1#ref", str(url))
		self.assertEqual("user", shortenedURL.User)
		self.assertEqual("pass", shortenedURL.Password)
		self.assertEqual("example.org", shortenedURL.Host.Hostname)
		self.assertDictEqual({"query": "1"}, shortenedURL.Query)
		self.assertEqual("ref", shortenedURL.Fragment)

class ParseErrors(Testcase):
	"""What :meth:`~pyTooling.GenericPath.URL.URL.Parse` rejects, and how it says so."""

	def test_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URL.Parse(None)

		self.assertEqual("Parameter 'url' is None.", str(context.exception))

	def test_WrongType(self) -> None:
		for value in (42, b"https://example.org", ["https://example.org"]):
			with self.subTest(url=value):
				with self.assertRaises(TypeError) as context:
					_ = URL.Parse(value)

				self.assertEqual("Parameter 'url' is not of type 'str'.", str(context.exception))

	def test_WrongTypeReportsTheType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = URL.Parse(42)

		self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_UnknownScheme(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("ftpx://example.org/file.txt")

		self.assertEqual("Unknown scheme 'ftpx' when parsing URL 'ftpx://example.org/file.txt'.", str(context.exception))

	def test_UnknownSchemeListsTheKnownOnes(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("ftpx://example.org")

		note = context.exception.__notes__[0]

		self.assertTrue(note.startswith("Known schemes: "))
		for scheme in Protocols.__members__:
			with self.subTest(scheme=scheme):
				self.assertIn(scheme.lower(), note)

	def test_CompositeSchemesAreKnown(self) -> None:
		for scheme, protocol in (("https", Protocols.HTTPS), ("ftps", Protocols.FTPS)):
			with self.subTest(scheme=scheme):
				self.assertEqual(protocol, URL.Parse(f"{scheme}://example.org/file.txt").Scheme)

	def test_QueryParameterWithAnEmptyValue(self) -> None:
		self.assertDictEqual({"key": ""}, URL.Parse("https://example.org/p?key=").Query)

	def test_QueryValueContainingAnEqualsSign(self) -> None:
		"""A '=' is legal inside a value; only the first one separates."""
		self.assertDictEqual({"key": "a=b"}, URL.Parse("https://example.org/p?key=a=b").Query)

	def test_URLErrorIsAToolingException(self) -> None:
		"""So a consumer catching the package's base exception still catches it."""
		self.assertTrue(issubclass(URLError, ToolingException))

		with self.assertRaises(ToolingException):
			_ = URL.Parse("ftpx://example.org")

	def test_SyntaxErrorRaisesURLError(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("http://ho!st/")

		self.assertEqual("Syntax error when parsing URL 'http://ho!st/'.", str(context.exception))

class QueriesAndFragments(Testcase):
	""":rfc:`3986` allows an empty query, an empty fragment and a query parameter without ``=``; each round-trips."""

	def test_NoQuery(self) -> None:
		url = URL.Parse("https://example.org/p")

		self.assertIsNone(url.Query)
		self.assertEqual("https://example.org/p", str(url))

	def test_EmptyQuery(self) -> None:
		url = URL.Parse("https://example.org/p?")

		self.assertDictEqual({}, url.Query)
		self.assertEqual("https://example.org/p?", str(url))

	def test_EmptyFragment(self) -> None:
		url = URL.Parse("https://example.org/p#")

		self.assertEqual("", url.Fragment)
		self.assertEqual("https://example.org/p#", str(url))

	def test_EmptyQueryAndFragment(self) -> None:
		url = URL.Parse("https://example.org/p?#")

		self.assertDictEqual({}, url.Query)
		self.assertEqual("", url.Fragment)
		self.assertEqual("https://example.org/p?#", str(url))

	def test_ParameterWithoutValue(self) -> None:
		"""A parameter without ``=`` has no value, unlike one with an empty value."""
		url = URL.Parse("https://example.org/p?flag")

		self.assertDictEqual({"flag": None}, url.Query)
		self.assertEqual("https://example.org/p?flag", str(url))

	def test_ParameterMixed(self) -> None:
		url = URL.Parse("https://example.org/p?flag&empty=&key=value")

		self.assertDictEqual({"flag": None, "empty": "", "key": "value"}, url.Query)
		self.assertEqual("https://example.org/p?flag&empty=&key=value", str(url))

	def test_Concatenation_ParameterWithoutValue(self) -> None:
		url = URL.Parse("https://example.org/api") / "things?flag"

		self.assertDictEqual({"flag": None}, url.Query)
		self.assertEqual("https://example.org/api/things?flag", str(url))

	def test_Concatenation_EmptyQueryAndFragment(self) -> None:
		url = URL.Parse("https://example.org/api") / "things?#"

		self.assertDictEqual({}, url.Query)
		self.assertEqual("", url.Fragment)
		self.assertEqual("https://example.org/api/things?#", str(url))

	def test_Construction_ParameterWithoutValue(self) -> None:
		url = URL(Protocols.HTTPS, Path.Parse("/p"), Host("example.org"), query={"flag": None, "key": "value"})

		self.assertEqual("https://example.org/p?flag&key=value", str(url))


class AddedSchemes(Testcase):
	"""Schemes written as ``scheme://``, added because an unlisted one can't be parsed."""

	def test_Parsed(self) -> None:
		for text, protocol in (
			("ws://host/socket",                 Protocols.WS),
			("wss://host/socket",                Protocols.WSS),
			("ssh://git@github.com/owner/r.git", Protocols.SSH),
			("sftp://host/file.txt",             Protocols.SFTP),
			("git://host/repository.git",        Protocols.GIT),
			("ldap://directory/o=example",       Protocols.LDAP),
			("ldaps://directory/o=example",      Protocols.LDAPS),
			("tcp://0.0.0.0:2375",               Protocols.TCP),
			("udp://collector:514",              Protocols.UDP),
			("unix:///var/run/docker.sock",      Protocols.UNIX),
			("mqtt://broker:1883",               Protocols.MQTT),
			("mqtts://broker:8883",              Protocols.MQTTS),
			("amqp://rabbit:5672",               Protocols.AMQP),
			("amqps://rabbit:5671",              Protocols.AMQPS),
			("redis://cache:6379",               Protocols.REDIS),
			("rediss://cache:6380",              Protocols.REDISS),
			("mongodb://db:27017",               Protocols.MONGODB),
			("postgres://db:5432/app",           Protocols.POSTGRES),
			("postgresql://db:5432/app",         Protocols.POSTGRES),
		):
			with self.subTest(url=text):
				self.assertEqual(protocol, URL.Parse(text).Scheme)

	def test_SecuredVariantsContainTLS(self) -> None:
		for text in ("wss://host/socket", "ldaps://directory/o=example"):
			with self.subTest(url=text):
				self.assertIn(Protocols.TLS, URL.Parse(text).Scheme)

	def test_SFTPIsCarriedBySSHAndIsNotFTP(self) -> None:
		""":attr:`Protocols.FTP` secured by TLS is :attr:`Protocols.FTPS`; SFTP is SSH's own file transfer."""
		self.assertEqual(Protocols.FTP | Protocols.TLS, Protocols.FTPS)

		self.assertIn(Protocols.SSH, Protocols.SFTP)
		self.assertNotIn(Protocols.FTP, Protocols.SFTP)
		self.assertNotIn(Protocols.TLS, Protocols.SFTP)
		self.assertNotEqual(Protocols.FTPS, Protocols.SFTP)

	def test_TCPAndUDPDoNotCombine(self) -> None:
		"""They name a scheme, not the transport another scheme runs over - ``http://`` is over TCP and says so nowhere."""
		self.assertNotIn(Protocols.TCP, Protocols.HTTP)
		self.assertNotIn(Protocols.TCP, Protocols.HTTPS)
		self.assertNotIn(Protocols.UDP, Protocols.HTTP)

	def test_RawEndpointsCarryHostAndPort(self) -> None:
		url = URL.Parse("tcp://0.0.0.0:2375")

		self.assertEqual("0.0.0.0", url.Host.Hostname)
		self.assertEqual(2375, url.Host.Port)

	def test_IsEncrypted(self) -> None:
		"""SSH and SFTP are encrypted and carry no TLS flag, which testing a single flag would miss."""
		for text in ("https://h/p", "ftps://h/f", "wss://h/s", "ldaps://d/o", "ssh://h/p", "sftp://h/f"):
			with self.subTest(url=text):
				self.assertTrue(URL.Parse(text).Scheme.IsEncrypted)

		for text in ("http://h/p", "ftp://h/f", "ws://h/s", "ldap://d/o", "git://h/r.git", "tcp://h:1", "udp://h:1"):
			with self.subTest(url=text):
				self.assertFalse(URL.Parse(text).Scheme.IsEncrypted)

	def test_IsEncryptedIsNoEnumerationMember(self) -> None:
		self.assertNotIn("IsEncrypted", Protocols.__members__)

	def test_AnOpaqueSchemeIsRejected(self) -> None:
		"""
		``URL_PATTERN`` only recognises a scheme written before ``://``.

		A URI like ``sip:alice@atlanta.com`` or ``mailto:a@b.org`` carries no ``//``, so it has no scheme a URL can
		start with. Listing such a scheme in :class:`Protocols` would change nothing; the pattern would have to.
		"""
		for text in ("sip:alice@atlanta.com", "mailto:a@b.org", "urn:isbn:0451450523"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Missing scheme when parsing URL '{text}'.", str(context.exception))


class ForbiddenCharacters(Testcase):
	"""A rejected URL holding a character :rfc:`3986` forbids says how to write it."""

	def test_Message(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://example.org/a b")

		self.assertEqual("Forbidden character when parsing URL 'https://example.org/a b'.", str(context.exception))

	def test_SpaceIsExplained(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("a b?#")

		self.assertIn(
			"Character ' ' is not allowed in a URL. Write it percent-encoded as '%20'.",
			context.exception.__notes__
		)

	def test_ControlCharacterIsExplained(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("?#\n")

		self.assertIn(
			"Character '\\n' is not allowed in a URL. Write it percent-encoded as '%0A'.",
			context.exception.__notes__
		)

	def test_TheMessageStaysOnOneLine(self) -> None:
		"""The URL is rendered with :func:`repr`, so a control character can't break the message apart."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("?#\n")

		self.assertNotIn("\n", str(context.exception))

	def test_NoNoteWhenNothingIsForbidden(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("http://ho!st/")

		self.assertEqual([], getattr(context.exception, "__notes__", []))

	def test_AnywhereInTheURL(self) -> None:
		"""A space after the host was read as the start of the path, which then didn't start with a slash."""
		for text in ("https://a b/c", "https://example.org/a b", "https://example.org/p?q=a b", "https://h/p#a b"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertIn(
					"Character ' ' is not allowed in a URL. Write it percent-encoded as '%20'.",
					context.exception.__notes__
				)

	def test_OnlySpaces(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("   ")

		self.assertEqual("Forbidden character when parsing URL '   '.", str(context.exception))

	def test_ATrailingNewline(self) -> None:
		"""A ``$`` matches before a trailing newline, so the newline was dropped from the URL instead of rejected."""
		with self.assertRaises(URLError):
			_ = URL.Parse("https://example.org/\n")

	def test_PercentEncodedIsAccepted(self) -> None:
		self.assertEqual("/a%20b", str(URL.Parse("https://example.org/a%20b").Path))


class HostParameters(Testcase):
	"""A host is constructed from a non-empty name and an optional port in range."""

	def test_Rejected(self) -> None:
		for hostname, port, exceptionType, message in (
			(None,   None,    ValueError, "Parameter 'hostname' is None."),
			(42,     None,    TypeError,  "Parameter 'hostname' is not of type 'str'."),
			("",     None,    ValueError, "Parameter 'hostname' is empty."),
			("host", "80",    TypeError,  "Parameter 'port' is not of type 'int'."),
			("host", 65536,   ValueError, "Parameter 'port' is out of range 0..65535."),
		):
			with self.subTest(hostname=hostname, port=port):
				with self.assertRaises(exceptionType) as context:
					Host(hostname, port)

				self.assertEqual(message, str(context.exception))


class IPv6Hosts(Testcase):
	"""A bracketed IPv6 literal is a host, not the start of the path."""

	def test_HostAndPort(self) -> None:
		url = URL.Parse("https://[2001:db8::1]:8080/path")

		self.assertEqual("[2001:db8::1]", url.Host.Hostname)
		self.assertEqual(8080, url.Host.Port)
		self.assertEqual("/path", str(url.Path))

	def test_WithoutPort(self) -> None:
		url = URL.Parse("https://[::1]/path")

		self.assertEqual("[::1]", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)

	def test_WithCredentialsQueryAndFragment(self) -> None:
		url = URL.Parse("https://user:pw@[fe80::1]:443/p?q=1#f")

		self.assertEqual("[fe80::1]", url.Host.Hostname)
		self.assertEqual(443, url.Host.Port)
		self.assertEqual("user", url.User)
		self.assertDictEqual({"q": "1"}, url.Query)
		self.assertEqual("f", url.Fragment)

	def test_IPv4IsUnaffected(self) -> None:
		url = URL.Parse("https://192.0.2.1:8080/path")

		self.assertEqual("192.0.2.1", url.Host.Hostname)
		self.assertEqual(8080, url.Host.Port)

	def test_TheBracketsAreKeptInTheHostname(self) -> None:
		"""
		:rfc:`3986` writes the literal in brackets, and they are kept, so the URL reassembles unchanged.

		A consumer wanting the bare address strips them itself.
		"""
		url = URL.Parse("https://[2001:db8::1]:8080/path")

		self.assertTrue(url.Host.Hostname.startswith("["))
		self.assertEqual("https://[2001:db8::1]:8080/path", str(url))


class MissingScheme(Testcase):
	"""A URL starts with a scheme followed by ``://``; without one, it's a relative reference or no URL at all."""

	def assertMissingScheme(self, text: str) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse(text)

		self.assertEqual(f"Missing scheme when parsing URL {text!r}.", str(context.exception))

	def test_EmptyString(self) -> None:
		"""An empty string was a URL without scheme, host and path; it names no scheme."""
		self.assertMissingScheme("")

	def test_AHost(self) -> None:
		"""A bare host was read as the host of a URL without scheme - :rfc:`3986` reads ``host:port`` as a scheme."""
		for text in (
			"github",
			"nonsense",
			"UNKNOWN",
			"192.168.1.1",
			"github.com",
			"github.com:80",
			"localhost:8080",
			"github.com:80/entrypoint",
			"github.com:80/path/file.png?width=1024",
			"github.com:80/entrypoint#chapter-3",
			"example.org/redirect?to=https://elsewhere.org"
		):
			with self.subTest(url=text):
				self.assertMissingScheme(text)

	def test_AReference(self) -> None:
		"""A relative reference is appended to a URL with ``/``, not parsed as one."""
		for text in ("", "?#", "//example.org/path", "/path/to/file", "things/4711", "C:/Windows"):
			with self.subTest(url=text):
				self.assertMissingScheme(text)

	def test_AMalformedSeparator(self) -> None:
		for text in ("://x", "http:/x", "http//host"):
			with self.subTest(url=text):
				self.assertMissingScheme(text)

	def test_AnSCPLikeAddress(self) -> None:
		"""Git's ``user@host:path`` is no URL; ``ssh://user@host/path`` is."""
		self.assertMissingScheme("git@github.com:org/repo.git")

	def test_AnSCPLikeAddress_Notes(self) -> None:
		"""The notes give the ``ssh://`` URL of an SCP-like address, also for an absolute path."""
		for text in ("git@github.com:org/repo.git", "git@github.com:/org/repo.git"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertListEqual(
					[
						"An SCP-like address 'user@host:path' (Git, scp) is no URL. As URL: 'ssh://git@github.com/org/repo.git'.",
						"In the URL, the path starts at the root, not in the user's home directory."
					],
					context.exception.__notes__
				)

	def test_TheNote(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("nonsense")

		self.assertEqual(["A URL starts with a scheme followed by '://', e.g. 'https://'."], context.exception.__notes__)


class MissingHost(Testcase):
	"""Only a ``file`` or a ``unix`` URL may leave its host empty, and then names an absolute path."""

	def test_Rejected(self) -> None:
		for text in ("http://", "http:///path", "http://:80", "http://user@/p", "https://?q=1", "ssh://#f"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Missing host when parsing URL {text!r}.", str(context.exception))

	def test_AUserOrAPortNeedsAHost(self) -> None:
		for text in ("file://user@/etc/hosts", "file://:80/etc/hosts", "unix://:80/var/run/docker.sock"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Missing host when parsing URL {text!r}.", str(context.exception))

	def test_TheNote(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("http:///path")

		self.assertEqual(
			["Only a 'file' or 'unix' URL may leave the host empty, e.g. 'file:///etc/hosts'."],
			context.exception.__notes__
		)

	def test_AFileURL(self) -> None:
		url = URL.Parse("file:///etc/hosts")

		self.assertEqual(Protocols.FILE, url.Scheme)
		self.assertIsNone(url.Host)
		self.assertEqual("/etc/hosts", str(url.Path))
		self.assertEqual("file:///etc/hosts", str(url))

	def test_AWindowsDriveLetter(self) -> None:
		""":rfc:`8089` writes a drive letter as the first element of an absolute path."""
		url = URL.Parse("file:///C:/Windows/System32")

		self.assertIsNone(url.Host)
		self.assertEqual("/C:/Windows/System32", str(url.Path))

	def test_ADriveLetterAsHost(self) -> None:
		"""``file://C:/...`` reads ``C`` as the host and ``:/...`` as its port."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("file://C:/Windows")

		self.assertEqual("Drive letter 'C' as host when parsing URL 'file://C:/Windows'.", str(context.exception))
		self.assertListEqual(["A drive letter belongs to the path: 'file:///C:/Windows'."], context.exception.__notes__)

	def test_AFileURLWithHost(self) -> None:
		for text, hostname in (("file://server/share/file.txt", "server"), ("file://localhost/etc/hosts", "localhost")):
			with self.subTest(url=text):
				self.assertEqual(hostname, URL.Parse(text).Host.Hostname)

	def test_AUnixSocket(self) -> None:
		url = URL.Parse("unix:///var/run/docker.sock")

		self.assertIsNone(url.Host)
		self.assertEqual("/var/run/docker.sock", str(url.Path))

	def test_MissingPath(self) -> None:
		for text in ("file://", "unix://"):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Missing path when parsing URL {text!r}.", str(context.exception))
				self.assertEqual(
					["A 'file' or 'unix' URL without a host names an absolute path, e.g. 'file:///etc/hosts'."],
					context.exception.__notes__
				)


class Ports(Testcase):
	"""A port follows the host after a ``:``, and is a number in range 0..65535."""

	def test_Boundaries(self) -> None:
		for text, port in (("https://host:0/", 0), ("https://host:65535/", 65535)):
			with self.subTest(url=text):
				self.assertEqual(port, URL.Parse(text).Host.Port)

	def test_OutOfRange(self) -> None:
		"""It was the :class:`Host` constructor's :exc:`ValueError`, naming a parameter the caller never passed."""
		for text, port in (("https://host:65536/", 65536), ("https://host:99999/", 99999)):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Port {port} is out of range 0..65535 when parsing URL {text!r}.", str(context.exception))

	def test_EmptyPort(self) -> None:
		"""A ``:`` without a number was read as the start of the path."""
		for text, url in (
			("http://host:/p",  "http://host/p"),
			("ssh://u@h:/p",    "ssh://u@h/p"),
			("http://host:",    "http://host"),
			("http://[::1]:/p", "http://[::1]/p")
		):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Missing port after ':' when parsing URL {text!r}.", str(context.exception))
				self.assertListEqual([f"Without ':', the URL is '{url}'."], context.exception.__notes__)

	def test_NotANumber(self) -> None:
		"""A path after the host's ``:`` - an SCP-like address with a scheme - was read as the port."""
		for text, port, url in (
			("http://host:abc/",                  "abc", "http://host/abc/"),
			("ssh://git@github.com:org/repo.git", "org", "ssh://git@github.com/org/repo.git"),
			("http://user:pw@host:x/",            "x",   "http://user:pw@host/x/")
		):
			with self.subTest(url=text):
				with self.assertRaises(URLError) as context:
					_ = URL.Parse(text)

				self.assertEqual(f"Port '{port}' is not a number when parsing URL {text!r}.", str(context.exception))
				self.assertListEqual([f"With a path after '/' instead, the URL is '{url}'."], context.exception.__notes__)


class UserInformation(Testcase):
	"""A user and a password are written with the characters :rfc:`3986` allows in the user information."""

	def test_ADotInTheUser(self) -> None:
		"""It was read as the host, and ``@example.org/`` as the path."""
		url = URL.Parse("https://first.last@example.org/")

		self.assertEqual("first.last", url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("example.org", url.Host.Hostname)
		self.assertEqual("/", str(url.Path))

	def test_APercentEncodedPassword(self) -> None:
		"""It was read as host ``user`` and path ``:p%40ss@example.org/``."""
		url = URL.Parse("https://user:p%40ss@example.org/")

		self.assertEqual("user", url.User)
		self.assertEqual("p%40ss", url.Password)
		self.assertEqual("example.org", url.Host.Hostname)
		self.assertEqual("https://user:p%40ss@example.org/", str(url))

	def test_AnAtInThePath(self) -> None:
		url = URL.Parse("https://hachyderm.io/@coveragepy")

		self.assertIsNone(url.User)
		self.assertEqual("hachyderm.io", url.Host.Hostname)
		self.assertEqual("/@coveragepy", str(url.Path))


class SchemeSpelling(Testcase):
	""":rfc:`3986` writes a scheme as a letter followed by letters, digits, ``+``, ``-`` and ``.``."""

	def test_UpperCase(self) -> None:
		self.assertEqual(Protocols.HTTPS, URL.Parse("HTTPS://Example.org/").Scheme)

	def test_APlusInTheScheme(self) -> None:
		"""It was read as host ``git`` and path ``+ssh://...``."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("git+ssh://git@github.com/o/r.git")

		self.assertEqual(
			"Unknown scheme 'git+ssh' when parsing URL 'git+ssh://git@github.com/o/r.git'.",
			str(context.exception)
		)


class AcceptedURLs(Testcase):
	"""What a URL looks like in the wild, read and written back unchanged."""

	def test_RoundTrip(self) -> None:
		for text in (
			"https://example.org",
			"https://example.org/",
			"https://example.org./",
			"https://example.org/path/to/file.txt",
			"https://example.org:8443/api/v3",
			"https://user@example.org/",
			"https://user:password@example.org:8443/p?q=1#frag",
			"https://example.org/p?a=1&b=2",
			"https://example.org/p#section",
			"http://192.168.1.1:80/",
			"ftp://ftp.example.org/pub/file.tar.gz",
			"ftp://anonymous:guest@ftp.example.org/pub",
			"ssh://git@github.com/owner/repo.git",
			"tcp://0.0.0.0:2375",
			"https://matrix.to/#/#aio-libs:matrix.org",
			"https://github.com/aio-libs/yarl/actions?query=branch:master",
			"https://example.org/redirect?to=https://elsewhere.org"
		):
			with self.subTest(url=text):
				self.assertEqual(text, str(URL.Parse(text)))

	def test_AColonInTheQuery(self) -> None:
		self.assertDictEqual(
			{"query": "branch:master"},
			URL.Parse("https://github.com/aio-libs/yarl/actions?query=branch:master").Query
		)

	def test_AHashInTheFragment(self) -> None:
		"""Only the first ``#`` starts the fragment."""
		url = URL.Parse("https://matrix.to/#/#aio-libs:matrix.org")

		self.assertEqual("/", str(url.Path))
		self.assertEqual("/#aio-libs:matrix.org", url.Fragment)


class IRIs(Testcase):
	"""
	An IRI (:rfc:`3987`) is read with ``iri=True`` and becomes an :rfc:`3986` URL.

	The host is converted to its A-labels by IDNA 2008 after the mapping of UTS #46, every other non-ASCII character is
	percent-encoded as UTF-8.
	"""

	def test_Strict(self) -> None:
		"""Without ``iri``, a Unicode host is rejected, and the note offers ``iri=True``."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://www.müller.de/")

		self.assertEqual("Syntax error when parsing URL 'https://www.müller.de/'.", str(context.exception))
		self.assertEqual(
			["A URL holds ASCII characters only. Read an IRI, which holds Unicode characters, with 'iri=True'."],
			context.exception.__notes__
		)

	def test_Strict_ASCII(self) -> None:
		"""An ASCII syntax error carries no note about IRIs."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("http://ho!st/")

		self.assertEqual([], getattr(context.exception, "__notes__", []))

	def test_Host(self) -> None:
		url = URL.Parse("https://www.müller.de/", iri=True)

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("www.xn--mller-kva.de", url.Host.Hostname)
		self.assertEqual("/", str(url.Path))
		self.assertEqual("https://www.xn--mller-kva.de/", str(url))

	def test_Host_Port(self) -> None:
		url = URL.Parse("https://www.müller.de:8443/api", iri=True)

		self.assertEqual("www.xn--mller-kva.de", url.Host.Hostname)
		self.assertEqual(8443, url.Host.Port)
		self.assertEqual("/api", str(url.Path))

	def test_IDNA2008(self) -> None:
		"""IDNA 2008 keeps ``ß``; IDNA 2003 and Python's built-in ``idna`` codec map it to ``ss``."""
		url = URL.Parse("https://straße.de/", iri=True)

		self.assertEqual("xn--strae-oqa.de", url.Host.Hostname)
		self.assertEqual("straße.de", url.Host.UnicodeHostname)

	def test_UTS46(self) -> None:
		"""UTS #46 maps upper case, full-width letters and the ideographic full stop before IDNA 2008, as browsers do."""
		for text in ("https://MÜLLER.de/", "https://Müller.DE/", "https://ｍüｌｌｅｒ。de/"):
			with self.subTest(iri=text):
				self.assertEqual("xn--mller-kva.de", URL.Parse(text, iri=True).Host.Hostname)

	def test_TrailingDot(self) -> None:
		self.assertEqual("www.xn--mller-kva.de.", URL.Parse("https://www.müller.de./", iri=True).Host.Hostname)

	def test_PercentEncoding(self) -> None:
		"""Path, query and fragment are percent-encoded as UTF-8."""
		url = URL.Parse("https://www.müller.de/straße?ä=ö#ü", iri=True)

		self.assertEqual("/stra%C3%9Fe", str(url.Path))
		self.assertDictEqual({"%C3%A4": "%C3%B6"}, url.Query)
		self.assertEqual("%C3%BC", url.Fragment)
		self.assertEqual("https://www.xn--mller-kva.de/stra%C3%9Fe?%C3%A4=%C3%B6#%C3%BC", str(url))

	def test_PercentEncoding_UserInformation(self) -> None:
		url = URL.Parse("https://jürgen:pä@example.org/", iri=True)

		self.assertEqual("j%C3%BCrgen", url.User)
		self.assertEqual("p%C3%A4", url.Password)
		self.assertEqual("example.org", url.Host.Hostname)

	def test_PercentEncoding_Kept(self) -> None:
		"""A character already percent-encoded stays as it is."""
		self.assertEqual("/a%20b/%C3%A4", str(URL.Parse("https://example.org/a%20b/ä", iri=True).Path))

	def test_PercentEncoding_IPv6(self) -> None:
		url = URL.Parse("https://[2001:db8::1]:8080/ä", iri=True)

		self.assertEqual("[2001:db8::1]", url.Host.Hostname)
		self.assertEqual("/%C3%A4", str(url.Path))

	def test_RoundTrip(self) -> None:
		"""The URL an IRI is read as parses without ``iri`` into the same string."""
		for text in (
			"https://www.müller.de/",
			"https://straße.de/",
			"https://user:pä@www.müller.de:8443/straße?ä=ö&b=2#ü",
			"https://example.org/wiki/Straße",
		):
			with self.subTest(iri=text):
				converted = str(URL.Parse(text, iri=True))

				self.assertTrue(converted.isascii())
				self.assertEqual(converted, str(URL.Parse(converted)))

	def test_ASCII(self) -> None:
		"""An ASCII URL is read as without ``iri``."""
		for text in (
			"https://user:password@example.org:8443/p?q=1#frag",
			"https://www.xn--mller-kva.de/",
			"file:///etc/hosts",
			"https://[2001:db8::1]:8080/path",
		):
			with self.subTest(url=text):
				self.assertEqual(str(URL.Parse(text)), str(URL.Parse(text, iri=True)))

	def test_IDNARejected(self) -> None:
		"""IDNA 2008 disallows symbols, which IDNA 2003 accepted."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://☃.net/", iri=True)

		self.assertEqual(
			"Host '☃.net' is no domain name of IDNA 2008 when parsing IRI 'https://☃.net/'.",
			str(context.exception)
		)
		self.assertEqual(["IDNA: Codepoint U+2603 at position 1 of '☃' not allowed"], context.exception.__notes__)
		self.assertIsInstance(context.exception.__cause__, UnicodeError)

	def test_IDNARejected_EmptyLabel(self) -> None:
		with self.assertRaises(URLError):
			_ = URL.Parse("https://www..müller.de/", iri=True)

	def test_ConvertedNote(self) -> None:
		"""An error found in the converted URL names it, and the note names the IRI given."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://www.müller.de:99999/", iri=True)

		self.assertEqual(
			"Port 99999 is out of range 0..65535 when parsing URL 'https://www.xn--mller-kva.de:99999/'.",
			str(context.exception)
		)
		self.assertEqual(["Converted from IRI 'https://www.müller.de:99999/'."], context.exception.__notes__)

	def test_MissingScheme(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("www.müller.de", iri=True)

		self.assertEqual("Missing scheme when parsing URL 'www.müller.de'.", str(context.exception))

	def test_ForbiddenCharacter(self) -> None:
		"""A character an IRI forbids too is rejected before the conversion, with the IRI in the message."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://www.müller.de/a b", iri=True)

		self.assertEqual("Forbidden character when parsing URL 'https://www.müller.de/a b'.", str(context.exception))
		self.assertEqual(
			["Character ' ' is not allowed in a URL. Write it percent-encoded as '%20'."],
			context.exception.__notes__
		)

	def test_ForbiddenCharacter_Unicode(self) -> None:
		"""A Unicode space is a space: :rfc:`3987` allows no space either."""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://www.müller.de/a\u3000b", iri=True)

		self.assertEqual(
			["Character '\\u3000' is not allowed in a URL. Write it percent-encoded as '%E3%80%80'."],
			context.exception.__notes__
		)

	def test_Parameter(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = URL.Parse("https://example.org/", iri=None)

		self.assertEqual("Parameter 'iri' is None.", str(context.exception))

		with self.assertRaises(TypeError) as context:
			_ = URL.Parse("https://example.org/", iri="yes")

		self.assertEqual("Parameter 'iri' is not of type 'bool'.", str(context.exception))
		self.assertEqual(["Got type 'str'."], context.exception.__notes__)

	def test_WithoutIDNA(self) -> None:
		"""Without the ``idna`` package, converting a Unicode host raises and names the extra."""
		with patch.dict(modules, {"idna": None}):
			with self.assertRaises(MissingDependencyError) as context:
				_ = URL.Parse("https://www.müller.de/", iri=True)

		self.assertEqual("idna", context.exception.Dependency)
		self.assertEqual("idna", context.exception.Extra)
		self.assertEqual(
			["Either install pyTooling with extra 'pyTooling[idna]' or install 'idna' directly."],
			context.exception.__notes__
		)

	def test_WithoutIDNA_ASCIIHost(self) -> None:
		"""Percent-encoding needs no package: an IRI whose host is ASCII is read without ``idna``."""
		with patch.dict(modules, {"idna": None}):
			url = URL.Parse("https://example.org/straße", iri=True)

		self.assertEqual("/stra%C3%9Fe", str(url.Path))


class UnicodeHostnames(Testcase):
	""":attr:`Host.UnicodeHostname` decodes the A-labels of a hostname."""

	def test_ALabel(self) -> None:
		self.assertEqual("www.müller.de", Host("www.xn--mller-kva.de").UnicodeHostname)

	def test_ALabel_UpperCase(self) -> None:
		self.assertEqual("www.müller.de", Host("www.XN--MLLER-KVA.de").UnicodeHostname)

	def test_ALabel_ASCIILabels(self) -> None:
		"""Only A-labels are decoded: an ASCII label IDNA 2008 would reject, like ``my_host``, is kept."""
		self.assertEqual("my_host.müller.de", Host("my_host.xn--mller-kva.de").UnicodeHostname)

	def test_NoALabel(self) -> None:
		for hostname in ("example.org", "192.0.2.1", "[2001:db8::1]", "my_host"):
			with self.subTest(hostname=hostname):
				self.assertEqual(hostname, Host(hostname).UnicodeHostname)

	def test_NoALabel_WithoutIDNA(self) -> None:
		with patch.dict(modules, {"idna": None}):
			self.assertEqual("example.org", Host("example.org").UnicodeHostname)

	def test_InvalidALabel(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = Host("xn--zz.de").UnicodeHostname

		self.assertEqual("Label 'xn--zz' of hostname 'xn--zz.de' is no A-label of IDNA 2008.", str(context.exception))
		self.assertEqual(["IDNA: Invalid A-label"], context.exception.__notes__)

	def test_WithoutIDNA(self) -> None:
		with patch.dict(modules, {"idna": None}):
			with self.assertRaises(MissingDependencyError) as context:
				_ = Host("www.xn--mller-kva.de").UnicodeHostname

		self.assertEqual("idna", context.exception.Extra)
