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
This package provides a representation for a Uniform Resource Locator (URL).

.. code-block::

   scheme://[user[:password]@]domain.tld[:port][/path/to/file][?query][#fragment]

The syntax is the one of :rfc:`3986` (an absolute URI with an authority); ``file`` URLs follow :rfc:`8089`. An IRI
(:rfc:`3987`), which may hold Unicode characters, is read with ``URL.Parse(..., iri=True)``.
"""
from __future__            import annotations

from enum                  import Flag
from re                    import compile as re_compile
from string                import punctuation
from urllib.parse          import quote as urlQuote
from typing                import ClassVar, Optional as Nullable, Mapping, Union

from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import MissingDependencyError, ToolingException
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.GenericPath import RootMixin, ElementMixin, PathMixin


__all__ = ["URL_PATTERN", "URL_REGEXP"]

URL_PATTERN = (
	r"""(?P<scheme>[a-zA-Z][-a-zA-Z0-9+.]*)://"""
	r"""(?:(?P<user>(?:[-a-zA-Z0-9._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})+)"""
	r"""(?::(?P<password>(?:[-a-zA-Z0-9._~!$&'()*+,;=]|%[0-9A-Fa-f]{2})+))?@)?"""
	r"""(?P<host>\[[0-9A-Fa-f:.]+\]|(?:[-a-zA-Z0-9_]+)(?:\.[-a-zA-Z0-9_]+)*\.?)?"""
	r"""(?:\:(?P<port>\d+))?"""
	r"""(?P<path>(?:/[^?#]*)?)"""
	r"""(?:\?(?P<query>[^#]+?))?"""
	r"""(?:#(?P<fragment>.+?))?"""
)                                                   #: Regular expression pattern for validating and splitting a URL.
URL_REGEXP = re_compile("^" + URL_PATTERN + r"\Z")  #: Precompiled regular expression for URL validation.

_SCHEME_PREFIX = re_compile(r"[a-zA-Z][-a-zA-Z0-9+.]*://")  #: Precompiled regular expression for the leading scheme.
_IRI_HOST =      re_compile(
	r"""(?P<prefix>[a-zA-Z][-a-zA-Z0-9+.]*://(?:[^/?#@]*@)?)"""
	r"""(?P<host>[^/?#:@\[\]]*)"""
	r"""(?P<rest>.*)"""
)  #: Precompiled regular expression splitting an IRI into scheme and user information, host, and the rest.

FORBIDDEN_CHARACTERS = " <>\"{}|\\^`"  #: Characters :rfc:`3986` forbids in a URL unless they are percent-encoded.


@export
class URLError(ToolingException):
	"""
	Raised when a URL can't be parsed, or a hostname's A-label can't be decoded.

	.. note::

	   :class:`urllib.error.URLError` from the standard library carries the same name and a different meaning - it
	   reports that a *request* failed. A module using both imports one of them under another name.
	"""


@export
class Protocols(Flag):
	"""
	Enumeration of supported URL schemes.

	The members are flags, so a scheme secured by a transport is the combination of that transport and the plain
	protocol: :attr:`HTTPS` is :attr:`TLS` with :attr:`HTTP`, and :attr:`SFTP` is :attr:`SSH` carrying its own file
	transfer. A scheme can therefore be asked which transport secures it, without enumerating every variant:

	.. code-block:: Python

	   if Protocols.TLS in url.Scheme:
	     print(f"'{url}' is secured by TLS.")

	   if url.Scheme.IsEncrypted:
	     print(f"'{url}' is encrypted.")

	.. attention::

	   :attr:`TLS` answers *"is this TLS"*, not *"is this encrypted"* - :attr:`SSH` and :attr:`SFTP` are encrypted
	   and carry no :attr:`TLS` flag. Use :attr:`IsEncrypted`, which asks for both.

	   :attr:`SFTP` is **not** :attr:`FTP` carried by :attr:`SSH`: it is a protocol of its own, defined as an SSH
	   subsystem and sharing nothing with FTP but its purpose. :attr:`FTP` secured by :attr:`TLS` is :attr:`FTPS`.

	.. note::

	   :attr:`TCP` and :attr:`UDP` name a scheme written as ``tcp://host:port``, which is what ZeroMQ, the Docker
	   daemon and syslog configurations use. They do **not** combine with the other members the way :attr:`TLS` and
	   :attr:`SSH` do: ``http://`` runs over TCP without saying so, so :attr:`HTTP` carries no :attr:`TCP` flag.
	   ``tcp`` is not registered with IANA - ``udp`` is registered provisionally - but both appear often enough that
	   refusing them would be unhelpful.

	.. caution::

	   The enumeration lists the schemes written as ``scheme://``, and :meth:`URL.Parse` raises
	   :exc:`URLError` for one it doesn't know - so a scheme missing here makes a URL unparseable. Schemes are added
	   as they are needed.

	   An **opaque** scheme - ``mailto:a@b.org``, ``urn:isbn:…``, and ``sip:alice@atlanta.com``, whose URI carries no
	   ``//`` - is a different matter: :data:`URL_PATTERN` only recognises a scheme before ``://``, so
	   :meth:`URL.Parse` rejects such a URI for its missing scheme. Listing it here would change nothing.
	"""

	TLS      = 1      #: Transport Layer Security
	FILE     = 2      #: Local files
	HTTP     = 4      #: Hyper Text Transfer Protocol
	FTP      = 8      #: File Transfer Protocol
	WS       = 16     #: WebSocket
	SSH      = 32     #: Secure Shell
	GIT      = 64     #: Git's own transport
	LDAP     = 128    #: Lightweight Directory Access Protocol
	TCP      = 512    #: A raw TCP endpoint, the higher protocol unspecified - as ZeroMQ and Docker write it.
	UDP      = 1024   #: A raw UDP endpoint of an unspecified higher protocol.
	UNIX     = 2048   #: A local Unix domain socket, addressed by a file system path.
	MQTT     = 4096   #: Message Queuing Telemetry Transport
	AMQP     = 8192   #: Advanced Message Queuing Protocol - the protocol RabbitMQ speaks.
	REDIS    = 16384  #: Redis
	MONGODB  = 32768  #: MongoDB
	POSTGRES = 65536  #: PostgreSQL

	HTTPS  = TLS | HTTP   #: SSL/TLS secured HTTP: combination of :attr:`TLS` and :attr:`HTTP`.
	FTPS   = TLS | FTP    #: SSL/TLS secured FTP: combination of :attr:`TLS` and :attr:`FTP`.
	WSS    = TLS | WS     #: SSL/TLS secured WebSocket: combination of :attr:`TLS` and :attr:`WS`.
	LDAPS  = TLS | LDAP   #: SSL/TLS secured LDAP: combination of :attr:`TLS` and :attr:`LDAP`.
	SFTP   = SSH | 256    #: SSH File Transfer Protocol, carried by :attr:`SSH`.
	MQTTS  = TLS | MQTT   #: SSL/TLS secured MQTT: combination of :attr:`TLS` and :attr:`MQTT`.
	AMQPS  = TLS | AMQP   #: SSL/TLS secured AMQP: combination of :attr:`TLS` and :attr:`AMQP`.
	REDISS = TLS | REDIS  #: SSL/TLS secured Redis: combination of :attr:`TLS` and :attr:`REDIS`.

	POSTGRESQL = POSTGRES  #: Alias of :attr:`POSTGRES`, the spelling ``libpq`` documents.

	@readonly
	def IsEncrypted(self) -> bool:
		"""
		Read-only property to return whether the scheme is encrypted.

		A scheme is encrypted when it is secured by :attr:`TLS` or carried by :attr:`SSH`, so this answers e.g.
		for :attr:`HTTPS` or :attr:`SFTP` alike - which testing a single flag doesn't.

		:returns: ``True``, if the scheme is secured by TLS or carried by SSH.
		"""
		return bool(self & (Protocols.TLS | Protocols.SSH))


@export
class Host(RootMixin):
	"""Represents a host as either hostname, DNS or IP-address including the port number in a URL."""

	_hostname: str            #: Name of the host (DNS name or IP address).
	_port:     Nullable[int]  #: Optional port number.

	def __init__(
		self,
		hostname: str,
		port:     Nullable[int] = None
	) -> None:
		"""
		Initialize a host instance described by host name and port number.

		:param hostname:    Name of the host (either IP address or DNS).
		:param port:        Optional, port number.
		:raises ValueError: If parameter 'hostname' is None or empty.
		:raises TypeError:  If parameter 'hostname' is not of type :class:`str`.
		:raises TypeError:  If parameter 'port' is not of type :class:`int`.
		:raises ValueError: If parameter 'port' is out of range 0..65535.
		"""
		super().__init__()

		if hostname is None:
			raise ValueError("Parameter 'hostname' is None.")
		elif not isinstance(hostname, str):
			ex = TypeError("Parameter 'hostname' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(hostname)}'.")
			raise ex
		elif hostname == "":
			raise ValueError("Parameter 'hostname' is empty.")

		self._hostname = hostname

		if port is None:
			pass
		elif not isinstance(port, int):
			ex = TypeError("Parameter 'port' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(port)}'.")
			raise ex
		elif not (0 <= port < 65536):
			ex = ValueError("Parameter 'port' is out of range 0..65535.")
			ex.add_note(f"Got value '{port}'.")
			raise ex

		self._port = port

	@readonly
	def Hostname(self) -> str:
		"""
		Read-only property to access the hostname.

		:returns: Hostname as DNS name or IP address.
		"""
		return self._hostname

	@readonly
	def UnicodeHostname(self) -> str:
		"""
		Read-only property to return the hostname with its A-labels decoded to Unicode.

		A URL carries an internationalized domain name (IDN) as A-labels, the ASCII form of IDNA 2008 (:rfc:`5890`), and
		this property returns the Unicode form a user reads: ``www.xn--mller-kva.de`` |rarr| ``www.müller.de``. A label
		that is no A-label - an ASCII label, an IP address - is returned unchanged. Only decoding an A-label needs the
		``idna`` package.

		:returns:                       Hostname with its A-labels decoded to Unicode.
		:raises MissingDependencyError: If the hostname holds an A-label and the ``idna`` extra isn't installed.
		:raises URLError:               If a label starts with ``xn--`` and is no A-label of IDNA 2008. |br|
		                                The note gives the reason of the ``idna`` package.
		"""
		if "xn--" not in self._hostname.lower():
			return self._hostname

		try:
			from idna import IDNAError, decode as idnaDecode
		except ImportError as ex:
			raise MissingDependencyError(dependency="idna", extra="idna") from ex

		labels = []
		for label in self._hostname.split("."):
			if label[:4].lower() == "xn--":
				try:
					labels.append(idnaDecode(label))
				except IDNAError as cause:
					ex = URLError(f"Label {label!r} of hostname {self._hostname!r} is no A-label of IDNA 2008.")
					ex.add_note(f"IDNA: {cause}")
					raise ex from cause
			else:
				labels.append(label)

		return ".".join(labels)

	@readonly
	def Port(self) -> Nullable[int]:
		"""
		Read-only property to access the optional port number.

		:returns: Optional port number.
		"""
		return self._port

	def __str__(self) -> str:
		"""
		Return a string representation of this host.

		:returns: Hostname, followed by ``:port`` if a port is specified.
		"""
		result = self._hostname
		if self._port is not None:
			result += f":{self._port}"

		return result

	def Copy(self) -> Host:
		"""
		Create a copy of this object.

		:returns: A new :class:`Host` instance.
		"""
		return self.__class__(
			self._hostname,
			self._port
		)


@export
class Element(ElementMixin):
	"""Derived class for the URL context."""


@export
class Path(PathMixin):
	"""Represents a path in a URL."""

	ELEMENT_DELIMITER: ClassVar[str] = "/"                #: Delimiter symbol in URLs between path elements.
	ROOT_DELIMITER:    ClassVar[str] = "/"                #: Delimiter symbol in URLs between root and first element.
	ELEMENT_TYPE:      ClassVar[type[Element]] = Element  #: Type an element of a URL's path has.


@export
class URL:
	"""
	Represents a URL (Uniform Resource Locator) including scheme, host, credentials, path, query and fragment.

	.. code-block::

	   scheme://[user[:password]@]domain.tld[:port][/path/to/file][?query][#fragment]

	The syntax is the one of :rfc:`3986` (an absolute URI with an authority); ``file`` URLs follow :rfc:`8089`.
	"""

	_scheme:    Nullable[Protocols]       #: Protocol (scheme) of the URL, ``None`` if the URL carries none.
	_user:      Nullable[str]             #: User name of the URL's authority part.
	_password:  Nullable[str]             #: Password of the URL's authority part.
	_host:      Nullable[Host]            #: Host name and port of the URL's authority part.
	_path:      Path                      #: Path part of the URL.
	_query:     Nullable[dict[str, str]]  #: Query parameters of the URL, by parameter name.
	_fragment:  Nullable[str]             #: Fragment (anchor) of the URL.

	def __init__(
		self,
		scheme:   Nullable[Protocols],
		path:     Path,
		host:     Nullable[Host] = None,
		user:     Nullable[str] = None,
		password: Nullable[str] = None,
		query:    Nullable[Mapping[str, str]] = None,
		fragment: Nullable[str] = None
	) -> None:
		"""
		Initializes a Uniform Resource Locator (URL).

		:param scheme:     Transport scheme to be used for a specified resource.
		:param path:       Path to the resource.
		:param host:       Optional, hostname where the resource is located.
		:param user:       Optional, username for basic authentication.
		:param password:   Optional, password for basic authentication.
		:param query:      Optional, query string.
		:param fragment:   Optional, fragment.
		:raises TypeError: If parameter 'host' is not of type :class:`Host`.
		"""
		if scheme is not None and not isinstance(scheme, Protocols):
			ex = TypeError("Parameter 'scheme' is not of type 'Protocols'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(scheme)}'.")
			raise ex

		self._scheme = scheme

		if user is not None and not isinstance(user, str):
			ex = TypeError("Parameter 'user' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(user)}'.")
			raise ex

		self._user = user

		if password is not None and not isinstance(password, str):
			ex = TypeError("Parameter 'password' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(password)}'.")
			raise ex

		self._password = password

		if host is not None and not isinstance(host, Host):
			ex = TypeError("Parameter 'host' is not of type 'Host'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(host)}'.")
			raise ex
		self._host = host

		if path is not None and not isinstance(path, Path):
			ex = TypeError("Parameter 'path' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(path)}'.")
			raise ex

		self._path = path

		if query is not None:
			if not isinstance(query, Mapping):
				ex = TypeError("Parameter 'query' is not a mapping ('dict', ...).")
				ex.add_note(f"Got type '{getFullyQualifiedName(query)}'.")
				raise ex

			self._query = dict(query)
		else:
			self._query = None

		if fragment is not None and not isinstance(fragment, str):
			ex = TypeError("Parameter 'fragment' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(fragment)}'.")
			raise ex

		self._fragment = fragment

	@readonly
	def Scheme(self) -> Nullable[Protocols]:
		"""
		Read-only property to access the URL scheme.

		:returns: URL scheme of the URL, ``None`` if it carries none.
		"""
		return self._scheme

	@readonly
	def User(self) -> Nullable[str]:
		"""
		Read-only property to access the optional username.

		:returns: Optional username within the URL.
		"""
		return self._user

	@readonly
	def Password(self) -> Nullable[str]:
		"""
		Read-only property to access the optional password.

		:returns: Optional password within a URL.
		"""
		return self._password

	@readonly
	def Host(self) -> Nullable[Host]:
		"""
		Read-only property to access the host part (hostname and port number) of the URL.

		:returns: The host part of the URL.
		"""
		return self._host

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the path part of the URL.

		:returns: Path part of the URL.
		"""
		return self._path

	@readonly
	def Query(self) -> Nullable[dict[str, str]]:
		"""
		Read-only property to access the dictionary of key-value pairs representing the query part in the URL.

		:returns: A dictionary representing the query as key-value pairs.
		"""
		return self._query

	@readonly
	def Fragment(self) -> Nullable[str]:
		"""
		Read-only property to access the fragment part of the URL.

		:returns: The fragment part of the URL.
		"""
		return self._fragment

	# http://semaphore.plc2.de:5000/api/v1/semaphore?name=Riviera&foo=bar#page2
	@classmethod
	def Parse(cls, url: str, *, iri: bool = False) -> URL:
		"""
		Parse a URL string and returns the URL object.

		A URL starts with a scheme followed by ``://`` and a host, as :rfc:`3986` writes an absolute URI with an
		authority: ``https://example.org/path``. After the host and port, a path starts with a slash. Only a ``file`` or
		``unix`` URL may leave the host empty, and then names an absolute path: ``file:///etc/hosts``.

		With ``iri``, the string is read as an IRI (Internationalized Resource Identifier, :rfc:`3987`), which may hold
		Unicode characters. A Unicode host is converted to its A-labels by IDNA 2008 (:rfc:`5891`) after the mapping of
		`UTS #46 <https://www.unicode.org/reports/tr46/>`__, and every other non-ASCII character is percent-encoded as
		UTF-8 (:rfc:`RFC 3987, section 3.1 <3987#section-3.1>`). The URL object is an :rfc:`3986` URL either way:
		``https://www.müller.de/`` is read as ``https://www.xn--mller-kva.de/``. An error found in the converted URL
		names that URL, and a note names the IRI it was converted from.

		:param url:                     URL as string to be parsed.
		:param iri:                     Optional, read ``url`` as an IRI (Internationalized Resource Identifier,
		                                :rfc:`3987`) instead of a URL. Default: ``False``.
		:returns:                       A URL object.
		:raises ValueError:             If parameter 'url' is ``None``.
		:raises TypeError:              If parameter 'url' is not of type :class:`str`.
		:raises ValueError:             If parameter 'iri' is ``None``.
		:raises TypeError:              If parameter 'iri' is not of type :class:`bool`.
		:raises URLError:               When the URL holds a character :rfc:`3986` forbids. |br|
		                                The note names the character and how to percent-encode it.
		:raises MissingDependencyError: When ``iri`` is set, the host holds a Unicode character, and the ``idna`` extra
		                                isn't installed.
		:raises URLError:               When ``iri`` is set and IDNA 2008 rejects the host. |br|
		                                The note gives the reason of the ``idna`` package.
		:raises URLError:               When the URL doesn't start with a scheme followed by ``://``.
		:raises URLError:               When syntax does not match. |br|
		                                If the URL holds a Unicode character, the note offers ``iri=True``.
		:raises URLError:               When the URL names a scheme that is not in :class:`Protocols`. |br|
		                                The note lists the known schemes.
		:raises URLError:               When the URL names no host, and isn't a ``file`` or ``unix`` URL without user and
		                                port.
		:raises URLError:               When a ``file`` or ``unix`` URL names neither a host nor a path.
		:raises URLError:               When the port is out of range 0..65535.
		:raises URLError:               When a parameter of the query is not a ``key=value`` pair.
		"""
		if url is None:
			raise ValueError("Parameter 'url' is None.")
		elif not isinstance(url, str):
			ex = TypeError("Parameter 'url' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(url)}'.")
			raise ex

		if iri is None:
			raise ValueError("Parameter 'iri' is None.")
		elif not isinstance(iri, bool):
			ex = TypeError("Parameter 'iri' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(iri)}'.")
			raise ex

		for character in url:
			if character in FORBIDDEN_CHARACTERS or character.isspace() or not character.isprintable():
				ex = URLError(f"Forbidden character when parsing URL {url!r}.")
				ex.add_note(
					f"Character {character!r} is not allowed in a URL. Write it percent-encoded as "
					f"'{urlQuote(character, safe='')}'."
				)
				raise ex

		if iri and not url.isascii() and (parts := _IRI_HOST.match(url)) is not None:
			host = parts["host"]
			if not host.isascii():
				try:
					from idna import IDNAError, encode as idnaEncode
				except ImportError as ex:
					raise MissingDependencyError(dependency="idna", extra="idna") from ex

				try:
					host = idnaEncode(host, uts46=True).decode("ascii")
				except IDNAError as cause:
					ex = URLError(f"Host {host!r} is no domain name of IDNA 2008 when parsing IRI {url!r}.")
					ex.add_note(f"IDNA: {cause}")
					raise ex from cause

			prefix = urlQuote(parts["prefix"], safe=punctuation)
			rest =   urlQuote(parts["rest"], safe=punctuation)
			try:
				return cls.Parse(prefix + host + rest)
			except URLError as ex:
				ex.add_note(f"Converted from IRI {url!r}.")
				raise

		if (matches := URL_REGEXP.match(url)) is not None:
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

			try:
				scheme = Protocols[scheme.upper()]
			except KeyError as ex:
				error = URLError(f"Unknown scheme '{scheme}' when parsing URL '{url}'.")
				error.add_note(f"Known schemes: {', '.join(name.lower() for name in Protocols.__members__)}.")
				raise error from ex

			if host is None:
				if user is not None or port is not None or scheme not in (Protocols.FILE, Protocols.UNIX):
					ex = URLError(f"Missing host when parsing URL {url!r}.")
					ex.add_note("Only a 'file' or 'unix' URL may leave the host empty, e.g. 'file:///etc/hosts'.")
					raise ex
				elif path == "":
					ex = URLError(f"Missing path when parsing URL {url!r}.")
					ex.add_note("A 'file' or 'unix' URL without a host names an absolute path, e.g. 'file:///etc/hosts'.")
					raise ex

			if port is not None and port > 65535:
				raise URLError(f"Port {port} is out of range 0..65535 when parsing URL {url!r}.")

			hostObj =    None if host is None else Host(host, port)
			pathObj =    Path.Parse(path, hostObj)
			parameters = None if query is None else cls._ParseQuery(query, url)

			return cls(
				scheme,
				pathObj,
				hostObj,
				user,
				password,
				parameters,
				fragment
			)

		if _SCHEME_PREFIX.match(url) is None:
			ex = URLError(f"Missing scheme when parsing URL {url!r}.")
			ex.add_note("A URL starts with a scheme followed by '://', e.g. 'https://'.")
			raise ex

		ex = URLError(f"Syntax error when parsing URL {url!r}.")
		if not url.isascii():
			ex.add_note("A URL holds ASCII characters only. Read an IRI, which holds Unicode characters, with 'iri=True'.")
		raise ex

	@classmethod
	def _ParseQuery(cls, query: str, url: str) -> dict[str, str]:
		"""
		Parse a URL's query into its parameters.

		:param query:     The query, without the leading ``?``. It is not empty - a URL carrying no query has none.
		:param url:       The URL the query came from, for the exception's message.
		:returns:         The parameters by name.
		:raises URLError: When a parameter of the query is not a ``key=value`` pair.
		"""
		parameters = {}
		for pair in query.split("&"):
			key, separator, value = pair.partition("=")
			if separator == "":
				error = URLError(f"Query parameter '{pair}' is no 'key=value' pair in URL '{url}'.")
				error.add_note("Every parameter of a query needs a '=', even when its value is empty.")
				raise error

			parameters[key] = value

		return parameters

	@classmethod
	def _CheckRelativeReference(cls, reference: str) -> None:
		"""
		Check a string names a resource below a URL.

		A relative reference of :rfc:`3986` names no scheme and no authority: it starts with no ``//``, and the first
		segment of its path holds no ``:``, which is the ``path-noscheme`` rule. A complete URL is read by
		:meth:`Parse` instead of being appended to another.

		:param reference: The right side of the ``/`` operator.
		:raises URLError: When the reference names a scheme or an authority.
		:raises URLError: When the reference holds a character :rfc:`3986` forbids. |br|
		                  The note names the character and how to percent-encode it.
		"""
		path = reference.partition("#")[0].partition("?")[0]
		if path.startswith("//"):
			error = URLError(f"Relative reference '{reference}' names an authority.")
			error.add_note("A reference below a URL carries no host, user, password or port.")
			error.add_note("Read a complete URL with 'URL.Parse' instead of appending it.")
			raise error
		elif ":" in path.split(Path.ELEMENT_DELIMITER, 1)[0]:
			error = URLError(f"Relative reference '{reference}' names a scheme.")
			error.add_note("The first element of a relative path carries no ':' - it would read as a scheme.")
			error.add_note("Read a complete URL with 'URL.Parse' instead of appending it. Write a ':' further down "
			               "the path percent-encoded as '%3A'.")
			raise error

		for character in reference:
			if character in FORBIDDEN_CHARACTERS or character.isspace() or not character.isprintable():
				error = URLError(f"Relative reference '{reference}' holds a forbidden character.")
				error.add_note(
					f"Character {character!r} is not allowed in a URL. Write it percent-encoded as "
					f"'{urlQuote(character, safe='')}'."
				)
				raise error

	def __truediv__(self, other: Union[str, Path]) -> URL:
		"""
		Return this URL with a resource below it.

		The right side is a **relative reference**: its path is appended below this URL's, and it brings its own query
		and fragment, which this URL's are not carried into - :rfc:`3986` resolves a reference the same way. A path
		that starts with a slash names where it starts itself and replaces this URL's path.

		.. code-block:: python

		   URL.Parse("https://example.org/api/v3") / "things/4711?fields=name"
		   # https://example.org/api/v3/things/4711?fields=name

		:param other:      The resource below this URL, as a string to parse or as a :class:`Path`.
		:returns:          A new URL naming that resource.
		:raises TypeError: If parameter 'other' is neither of type :class:`str` nor of type :class:`Path`.
		:raises URLError:  When the right side names a scheme or an authority instead of a resource.
		:raises URLError:  When the right side holds a character :rfc:`3986` forbids. |br|
		                   The note names the character and how to percent-encode it.
		:raises URLError:  When a parameter of the right side's query is not a ``key=value`` pair.
		"""
		if isinstance(other, str):
			self._CheckRelativeReference(other)

			resource, _, fragment = other.partition("#")
			resource, _, query =    resource.partition("?")
			parameters = None if query == "" else self._ParseQuery(query, other)
			fragment =   fragment if fragment != "" else None
		elif isinstance(other, Path):
			resource =   other
			parameters = None
			fragment =   None
		else:
			ex = TypeError("Second operand is not supported by / operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: 'str' or 'Path'.")
			raise ex

		return self.__class__(
			scheme=self._scheme,
			path=self._path / resource,
			host=self._host,
			user=self._user,
			password=self._password,
			query=parameters,
			fragment=fragment
		)

	def __str__(self) -> str:
		"""
		Formats the URL object as a string representation.

		:returns: Formatted URL object.
		"""
		result = str(self._path)

		if self._host is not None:
			result = str(self._host) + result

		if self._user is not None:
			if self._password is not None:
				result = f"{self._user}:{self._password}@{result}"
			else:
				result = f"{self._user}@{result}"

		# 'Protocols' is a 'Flag', so a single member and a combination both have a name; only 'Protocols(0)' has
		# none - and a scheme without any flag is no scheme, so it renders nothing either way.
		if self._scheme is not None and (scheme := self._scheme.name) is not None:
			result = scheme.lower() + "://" + result

		if self._query is not None and len(self._query) > 0:
			result = result + "?" + "&".join([f"{key}={value}" for key, value in self._query.items()])

		if self._fragment is not None:
			result = result + "#" + self._fragment

		return result

	def WithoutCredentials(self) -> URL:
		"""
		Returns a URL object without credentials (username and password).

		:returns: New URL object without credentials.
		"""
		return self.__class__(
			scheme=self._scheme,
			path=self._path,
			host=self._host,
			query=self._query,
			fragment=self._fragment
		)

	def WithoutTrailingSlash(self) -> URL:
		"""
		Returns a URL object whose path doesn't end in a slash.

		A URL's element delimiter is the slash, so this is :meth:`~pyTooling.GenericPath.PathMixin.WithoutTrailingDelimiter`
		applied to the URL's path. A trailing slash is an empty last element, so ``https://example.org/api/v3/`` and
		``https://example.org/api/v3`` differ although they usually address the same resource. A URL that is composed
		with a path below it wants the latter, or the composition yields a double slash.

		:returns: New URL object without a trailing slash, or this URL, if its path has none.

		.. seealso::

		   :meth:`~pyTooling.GenericPath.PathMixin.WithoutTrailingDelimiter`
		      |rarr| What it does to the path, and what it leaves alone.
		"""
		if (path := self._path.WithoutTrailingDelimiter()) is self._path:
			return self

		return self.__class__(
			scheme=self._scheme,
			path=path,
			host=self._host,
			user=self._user,
			password=self._password,
			query=self._query,
			fragment=self._fragment
		)
