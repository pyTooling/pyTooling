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
# Copyright 2017-2024 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""Uni tests for :mod:`pyTooling.GenericPath.URL`."""
from unittest import TestCase
from pyTooling.GenericPath.URL import URL, Protocols


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class GenericPath(TestCase):
	url : URL = URL.Parse("https://pyTooling.GitHub.io:8080/path/to/endpoint?user=paebbels&token=1234567890")

	def test_Protocol(self) -> None:
		self.assertEqual(self.url.Scheme, Protocols.HTTPS)

	def test_Port(self) -> None:
		self.assertEqual(self.url.Host.Port, 8080)

	def test_Hostname(self) -> None:
		self.assertEqual(self.url.Host.Hostname, "pyTooling.GitHub.io")

	def test_str(self) -> None:
		self.assertEqual(str(self.url), "https://pyTooling.GitHub.io:8080/path/to/endpoint?user=paebbels&token=1234567890")

class URLs(TestCase):
	def test_Host(self):
		url = URL.Parse("github")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_IP(self):
		url = URL.Parse("192.168.1.1")

		self.assertIsNone(url.Scheme)
		self.assertEqual("192.168.1.1", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS(self):
		url = URL.Parse("github.com")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port(self):
		url = URL.Parse("github.com:80")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port_Path(self):
		url = URL.Parse("github.com:80/entrypoint")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/entrypoint", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port_Path_File(self):
		url = URL.Parse("github.com:80/path/file.png")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port_Path_File_Query(self):
		url = URL.Parse("github.com:80/path/file.png?width=1024")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024"}, url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port_Path_File_QueryQuery(self):
		url = URL.Parse("github.com:80/path/file.png?width=1024&height=912")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/path/file.png", str(url.Path))
		self.assertDictEqual({"width": "1024", "height": "912"}, url.Query)
		self.assertIsNone(url.Fragment)

	def test_DNS_Port_Path_File_Fragment(self):
		url = URL.Parse("github.com:80/entrypoint#chapter-3")

		self.assertIsNone(url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(80, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("/entrypoint", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertEqual("chapter-3", url.Fragment)

	def test_HTTP_DNS(self):
		url = URL.Parse("http://github.com")

		self.assertEqual(Protocols.HTTP, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_HTTPS_DNS(self):
		url = URL.Parse("https://github.com")

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_HTTPS_DNS_Port(self):
		url = URL.Parse("https://github.com:443")

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("github.com", url.Host.Hostname)
		self.assertEqual(443, url.Host.Port)
		self.assertIsNone(url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_HTTPS_User_DNS_Port(self):
		url = URL.Parse("https://paebbels@v-4.github.com:25005")

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("v-4.github.com", url.Host.Hostname)
		self.assertEqual(25005, url.Host.Port)
		self.assertEqual("paebbels", url.User)
		self.assertIsNone(url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_HTTPS_User_Pwd_DNS(self):
		url = URL.Parse("https://paebbels:foobar@v4.api.github.com")

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("v4.api.github.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertEqual("paebbels", url.User)
		self.assertEqual("foobar", url.Password)
		self.assertEqual("", str(url.Path))
		self.assertIsNone(url.Query)
		self.assertIsNone(url.Fragment)

	def test_GitLabCIToken(self):
		url = URL.Parse("https://gitlab-ci-token:glcbt-64_2yjksyWRz6mPq57YFsvx@gitlab.company.com/path/to/resource.ext?query1=34&query2=343#ref-45")

		self.assertEqual(Protocols.HTTPS, url.Scheme)
		self.assertEqual("gitlab.company.com", url.Host.Hostname)
		self.assertIsNone(url.Host.Port)
		self.assertEqual("gitlab-ci-token", url.User)
		self.assertEqual("glcbt-64_2yjksyWRz6mPq57YFsvx", url.Password)
		self.assertEqual("/path/to/resource.ext", str(url.Path))
		self.assertDictEqual({"query1": "34", "query2": "343"}, url.Query)
		self.assertEqual("ref-45", url.Fragment)
