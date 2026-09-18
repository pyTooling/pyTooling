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
from pyTooling.Exceptions       import ToolingException
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

		self.assertIn("Known schemes: tls, file, http, ftp, https, ftps.", context.exception.__notes__)

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
