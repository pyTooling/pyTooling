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
from pyTooling.Exceptions      import ToolingException
from pyTooling.GenericPath.URL import URL, URLError, Protocols
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
		resource = "github"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_IP(self) -> None:
		resource = "192.168.1.1"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("192.168.1.1", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS(self) -> None:
		resource = "github.com"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port(self) -> None:
		resource = "github.com:80"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path(self) -> None:
		resource = "github.com:80/entrypoint"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/entrypoint", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File(self) -> None:
		resource = "github.com:80/path/file.png"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_Query(self) -> None:
		resource = "github.com:80/path/file.png?width=1024"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024"}, url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_QueryQuery(self) -> None:
		resource = "github.com:80/path/file.png?width=1024&height=912"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024", "height": "912"}, url.Query)
		self.assertIsNone(url.Fragment)

		self.assertEqual(resource, str(url))

	def test_DNS_Port_Path_File_Fragment(self) -> None:
		resource = "github.com:80/entrypoint#chapter-3"
		url = URL.Parse(resource)

		self.assertIsNone(url.Scheme)
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

	def test_QueryParameterWithoutValue(self) -> None:
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("https://example.org/p?flag")

		self.assertEqual(
			"Query parameter 'flag' is no 'key=value' pair in URL 'https://example.org/p?flag'.",
			str(context.exception)
		)

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
		"""
		``'?#'`` is one of the few strings ``URL_PATTERN`` rejects.

		Every group of the pattern is optional, so almost nothing fails it - ``'https://a b/c'`` and even a string
		holding a newline are accepted. See the pull-request's *Known Issues*.
		"""
		with self.assertRaises(URLError) as context:
			_ = URL.Parse("?#")

		self.assertEqual("Syntax error when parsing URL '?#'.", str(context.exception))


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

	def test_AnOpaqueSchemeIsMisparsedAsCredentials(self) -> None:
		"""
		``URL_PATTERN`` only recognises a scheme written before ``://``.

		A URI like ``sip:alice@atlanta.com`` or ``mailto:a@b.org`` carries no ``//``, so the scheme is not recognised
		and the ``scheme:user`` part is taken for ``user:password`` instead - it parses wrongly rather than raising.
		Listing such a scheme in :class:`Protocols` would change nothing; the pattern would have to.
		"""
		url = URL.Parse("sip:alice@atlanta.com")

		self.assertIsNone(url.Scheme)
		self.assertEqual("sip", url.User)
		self.assertEqual("alice", url.Password)
		self.assertEqual("atlanta.com", url.Host.Hostname)


class ForbiddenCharacters(Testcase):
	"""A rejected URL holding a character :rfc:`3986` forbids says how to write it."""

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
			_ = URL.Parse("?#")

		self.assertEqual([], getattr(context.exception, "__notes__", []))

	def test_AnAcceptedURLIsUnaffected(self) -> None:
		"""A space is accepted today, so the note never fires for one - see the pull-request's Known Issues."""
		self.assertEqual("https://a b/c", str(URL.Parse("https://a b/c")))


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
