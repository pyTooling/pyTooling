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
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
from enum     import IntFlag
from re       import compile as re_compile
from typing   import Dict, Optional as Nullable

from pyTooling.Decorators import export

from .        import RootMixIn, ElementMixIn, PathMixIn


regExp = re_compile(r"^(?:(?P<scheme>\w+)://)?(?:(?P<host>(?:\w+|\.)+)(?:\:(?P<port>\d+))?)?(?P<path>[^?#]*)(?:\?(?P<query>[^#]+))?(?:#(?P<fragment>.+))?$")


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
	"""Represents a hostname (including the port number) in a URL."""

	_hostname : str
	_port :     Nullable[int]

	def __init__(self, hostname: str, port: int = None):
		super().__init__()
		self._hostname = hostname
		self._port =     port

	@property
	def Hostname(self) -> str:
		"""Hostname or IP address as string."""
		return self._hostname

	@property
	def Port(self) -> Nullable[int]:
		"""Port number as integer."""
		return self._port

	def __str__(self) -> str:
		result = self._hostname
		if self._port is not None:
			result += f":{self._port}"

		return result


@export
class Element(ElementMixIn):
	"""Derived class for the URL context."""


@export
class Path(PathMixIn):
	"""Represents a path in a URL."""

	ELEMENT_DELIMITER = "/"   #: Delimiter symbol in URLs between path elements.
	ROOT_DELIMITER =    "/"   #: Delimiter symbol in URLs between root element and first path element.

	@classmethod
	def Parse(cls, path: str, root: Host = None) -> "Path":
		return super().Parse(path, root, cls, Element)


@export
class URL:
	"""Represents a URL including scheme, host, credentials, path, query and fragment."""

	_scheme:    Protocols
	_user:      Nullable[str]
	_password:  Nullable[str]
	_host:      Nullable[Host]
	_path:      Path
	_query:     Nullable[Dict[str, str]]
	_fragment:  Nullable[str]

	def __init__(self, scheme: Protocols, path: Path, host: Host = None, user: str = None, password: str = None, query: Dict[str, str] = None, fragment: str = None):
		self._scheme =    scheme
		self._user =      user
		self._password =  password
		self._host =      host
		self._path =      path
		self._query =     query
		self._fragment =  fragment

	def __str__(self) -> str:
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

		if len(self._query) != 0:
			result = result + "?" + "&".join([f"{key}={value}" for key, value in self._query.items()])

		if self._fragment is not None:
			result = result + "#" + self._fragment

		return result

	@property
	def Scheme(self) -> Protocols:
		return self._scheme

	@property
	def User(self) -> Nullable[str]:
		return self._user

	@property
	def Password(self) -> Nullable[str]:
		return self._password

	@property
	def Host(self) -> Nullable[Host]:
		return self._host

	@property
	def Path(self) -> Path:
		return self._path

	@property
	def Query(self) -> Nullable[Dict[str, str]]:
		return self._query

	@property
	def Fragment(self) -> Nullable[str]:
		return self._fragment

	# http://semaphore.plc2.de:5000/api/v1/semaphore?name=Riviera&foo=bar#page2
	@classmethod
	def Parse(cls, path: str) -> "URL":
		matches = regExp.match(path)
		if (matches is not None):
			scheme =    matches.group("scheme")
			user =      None # matches.group("user")
			password =  None # matches.group("password")
			host =      matches.group("host")

			port = matches.group("port")
			if (port is not None):
				port =      int(port)
			path =      matches.group("path")
			query =     matches.group("query")
			fragment =  matches.group("fragment")

			scheme =    None if (scheme is None) else Protocols[scheme.upper()]
			hostObj =   None if (host is None)   else Host(host, port)

			pathObj =   Path.Parse(path, hostObj)

			parameters = {}
			if (query is not None):
				for pair in query.split("&"):
					key, value = pair.split("=")
					parameters[key] = value

			return cls(scheme, pathObj, hostObj, user, password, parameters, fragment)

		else:
			pass
