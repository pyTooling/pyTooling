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
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
This package provides a representation for a Uniform Resource Locator (URL).

.. code-block::

   [schema://][user[:password]@]domain.tld[:port]/path/to/file[?query][#fragment]
"""
from sys      import version_info

from enum     import IntFlag
from re       import compile as re_compile
from typing   import Dict, Optional as Nullable, Mapping

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.Common      import getFullyQualifiedName
	from pyTooling.GenericPath import RootMixIn, ElementMixIn, PathMixIn
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.GenericPath.URL] Could not import from 'pyTooling.*'!")

	try:
		from Decorators         import export, readonly
		from Exceptions         import ToolingException
		from Common             import getFullyQualifiedName
		from GenericPath        import RootMixIn, ElementMixIn, PathMixIn
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.GenericPath.URL] Could not import directly!")
		raise ex


__all__ = ["URL_PATTERN", "URL_REGEXP"]

URL_PATTERN = (
	r"""(?:(?P<scheme>\w+)://)?"""
	r"""(?:(?P<user>[-a-zA-Z0-9_]+)(?::(?P<password>[-a-zA-Z0-9_]+))?@)?"""
	r"""(?:(?P<host>(?:[-a-zA-Z0-9_]+)(?:\.[-a-zA-Z0-9_]+)*\.?)(?:\:(?P<port>\d+))?)?"""
	r"""(?P<path>[^?#]*?)"""
	r"""(?:\?(?P<query>[^#]+?))?"""
	r"""(?:#(?P<fragment>.+?))?"""
)                                                 #: Regular expression pattern for validating and splitting a URL.
URL_REGEXP = re_compile("^" + URL_PATTERN + "$")  #: Precompiled regular expression for URL validation.


@export
class Protocols(IntFlag):
	"""Enumeration of supported URL schemes."""

	TLS =   1   #: Transport Layer Security
	HTTP =  2   #: Hyper Text Transfer Protocol
	HTTPS = 4   #: SSL/TLS secured HTTP
	FTP =   8   #: File Transfer Protocol
	FTPS =  16  #: SSL/TLS secured FTP
	FILE =  32  #: Local files


@export
class Host(RootMixIn):
	"""Represents a host as either hostname, DNS or IP-address including the port number in a URL."""

	_hostname: str
	_port:     Nullable[int]

	def __init__(
		self,
		hostname: str,
		port: Nullable[int] = None
	) -> None:
		"""
		Initialize a host instance described by host name and port number.

		:param hostname: Name of the host (either IP or DNS).
		:param port:     Port number.
		"""
		super().__init__()

		if not isinstance(hostname, str):
			ex = TypeError(f"Parameter 'hostname' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(hostname)}'.")
			raise ex
		self._hostname = hostname

		if port is None:
			pass
		elif not isinstance(port, int):
			ex = TypeError(f"Parameter 'port' is not of type 'int'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(hostname)}'.")
			raise ex
		elif not (0 <= port < 65536):
			ex = ValueError(f"Parameter 'port' is out of range 0..65535.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got value '{port}'.")
			raise ex
		self._port = port

	@readonly
	def Hostname(self) -> str:
		"""Hostname or IP address as string."""
		return self._hostname

	@readonly
	def Port(self) -> Nullable[int]:
		"""Port number as integer."""
		return self._port

	def __str__(self) -> str:
		result = self._hostname
		if self._port is not None:
			result += f":{self._port}"

		return result

	def Copy(self) -> "Host":
		"""
		Create a copy of this object.

		:return: A new Host instance.
		"""
		return self.__class__(
			self._hostname,
			self._port
		)


@export
class Element(ElementMixIn):
	"""Derived class for the URL context."""


@export
class Path(PathMixIn):
	"""Represents a path in a URL."""

	ELEMENT_DELIMITER = "/"   #: Delimiter symbol in URLs between path elements.
	ROOT_DELIMITER =    "/"   #: Delimiter symbol in URLs between root element and first path element.

	@classmethod
	def Parse(cls, path: str, root: Nullable[Host] = None) -> "Path":
		return super().Parse(path, root, cls, Element)


@export
class URL:
	"""
	Represents a URL (Uniform Resource Locator) including scheme, host, credentials, path, query and fragment.

	.. code-block::

	   [schema://][user[:password]@]domain.tld[:port]/path/to/file[?query][#fragment]
	"""

	_scheme:    Protocols
	_user:      Nullable[str]
	_password:  Nullable[str]
	_host:      Nullable[Host]
	_path:      Path
	_query:     Nullable[Dict[str, str]]
	_fragment:  Nullable[str]

	def __init__(
		self,
		scheme: Protocols,
		path: Path,
		host: Nullable[Host] = None,
		user: Nullable[str] = None,
		password: Nullable[str] = None,
		query: Nullable[Mapping[str, str]] = None,
		fragment: Nullable[str] = None
	) -> None:
		"""
		Initializes a Uniform Resource Locator (URL).

		:param scheme:   Transport scheme to be used for a specified resource.
		:param path:     Path to the resource.
		:param host:     Hostname where the resource is located.
		:param user:     Username for basic authentication.
		:param password: Password for basic authentication.
		:param query:    An optional query string.
		:param fragment: An optional fragment.
		"""
		if scheme is not None and not isinstance(scheme, Protocols):
			ex = TypeError(f"Parameter 'scheme' is not of type 'Protocols'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(scheme)}'.")
			raise ex
		self._scheme = scheme

		if user is not None and not isinstance(user, str):
			ex = TypeError(f"Parameter 'user' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(user)}'.")
			raise ex
		self._user = user

		if password is not None and not isinstance(password, str):
			ex = TypeError(f"Parameter 'password' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(password)}'.")
			raise ex
		self._password = password

		if host is not None and not isinstance(host, Host):
			ex = TypeError(f"Parameter 'host' is not of type 'Host'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(host)}'.")
			raise ex
		self._host = host

		if path is not None and not isinstance(path, Path):
			ex = TypeError(f"Parameter 'path' is not of type 'Path'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex
		self._path = path

		if query is not None:
			if not isinstance(query, Mapping):
				ex = TypeError(f"Parameter 'query' is not a mapping ('dict', ...).")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(query)}'.")
				raise ex

			self._query = {keyword: value for keyword, value in query.items()}
		else:
			self._query = None

		if fragment is not None and not isinstance(fragment, str):
			ex = TypeError(f"Parameter 'fragment' is not of type 'str'.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(fragment)}'.")
			raise ex
		self._fragment = fragment

	@readonly
	def Scheme(self) -> Protocols:
		return self._scheme

	@readonly
	def User(self) -> Nullable[str]:
		return self._user

	@readonly
	def Password(self) -> Nullable[str]:
		return self._password

	@readonly
	def Host(self) -> Nullable[Host]:
		"""
		Returns the host part (host name and port number) of the URL.

		:return: The host part of the URL.
		"""
		return self._host

	@readonly
	def Path(self) -> Path:
		return self._path

	@readonly
	def Query(self) -> Nullable[Dict[str, str]]:
		"""
		Returns a dictionary of key-value pairs representing the query part in a URL.

		:returns: A dictionary representing the query.
		"""
		return self._query

	@readonly
	def Fragment(self) -> Nullable[str]:
		"""
		Returns the fragment part of the URL.

		:return: The fragment part of the URL.
		"""
		return self._fragment

	# http://semaphore.plc2.de:5000/api/v1/semaphore?name=Riviera&foo=bar#page2
	@classmethod
	def Parse(cls, url: str) -> "URL":
		"""
		Parse a URL string and returns a URL object.

		:param url:               URL as string to be parsed.
		:returns:                 A URL object.
		:raises ToolingException: When syntax does not match.
		"""
		matches = URL_REGEXP.match(url)
		if matches is not None:
			scheme =    matches.group("scheme")
			user =      matches.group("user")
			password =  matches.group("password")
			host =      matches.group("host")

			port = matches.group("port")
			if port is not None:
				port =    int(port)
			path =      matches.group("path")
			query =     matches.group("query")
			fragment =  matches.group("fragment")

			scheme =    None if scheme is None else Protocols[scheme.upper()]
			hostObj =   None if host is None   else Host(host, port)

			pathObj =   Path.Parse(path, hostObj)

			parameters = {}
			if query is not None:
				for pair in query.split("&"):
					key, value = pair.split("=")
					parameters[key] = value

			return cls(
				scheme,
				pathObj,
				hostObj,
				user,
				password,
				parameters if len(parameters) > 0 else None,
				fragment
			)

		raise ToolingException(f"Syntax error when parsing URL '{url}'.")

	def __str__(self) -> str:
		"""
		Formats the URL object as a string representation.

		:return: Formatted URL object.
		"""
		result = str(self._path)

		if self._host is not None:
			result = str(self._host) + result

		if self._user is not None:
			if self._password is not None:
				result = f"{self._user}:{self._password}@{result}"
			else:
				result = f"{self._user}@{result}"

		if self._scheme is not None:
			result = self._scheme.name.lower() + "://" + result

		if self._query is not None and len(self._query) > 0:
			result = result + "?" + "&".join([f"{key}={value}" for key, value in self._query.items()])

		if self._fragment is not None:
			result = result + "#" + self._fragment

		return result

	def WithoutCredentials(self) -> "URL":
		"""
		Returns a URL object without credentials (username and password).

		:return: New URL object without credentials.
		"""
		return self.__class__(
			scheme=self._scheme,
			path=self._path,
			host=self._host,
			query=self._query,
			fragment=self._fragment
		)
