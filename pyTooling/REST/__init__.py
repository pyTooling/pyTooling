# ==================================================================================================================== #
#             _____           _ _               ____  _____ ____ _____                                                 #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \| ____/ ___|_   _|                                                #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) |  _| \___ \ | |                                                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  _ <| |___ ___) || |                                                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_| \_\_____|____/ |_|                                                  #
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
#
"""
A small client for JSON REST APIs, built on the standard library.

Every REST API is read the same way: a request carrying a bearer token, an answer that has to be a JSON object, a
transient failure that is worth another attempt, and a collection that arrives one page at a time. None of that is
knowledge about a particular service, so it lives here rather than in each reader.

.. hint::

   See :ref:`high-level help <REST>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.CI.GitHub`
      |rarr| A data model read from a REST API through this client.
"""
from enum                      import StrEnum
from http                      import HTTPMethod
from json                      import dumps as json_dumps, loads as json_loads
from re                        import compile as re_compile
from time                      import sleep
from typing                    import Any, Optional as Nullable, Union
from urllib.error              import HTTPError, URLError
from urllib.request            import Request, urlopen

from pyTooling.Common          import getFullyQualifiedName
from pyTooling.Decorators      import export, readonly
from pyTooling.Exceptions      import ToolingException
from pyTooling.GenericPath.URL import URL
from pyTooling.MetaClasses     import ExtendedType


__all__ = ["JSONObject"]

JSONObject = dict[str, Any]
"""A JSON object, as :func:`json.loads` returns it."""

TRANSIENT_HTTP_STATUS = (429, 500, 502, 503, 504)
"""HTTP status codes of a transient failure, after which a request is tried again."""

MAXIMUM_RETRY_AFTER = 60.0
"""The longest pause in seconds a ``Retry-After`` header can demand before a request is tried again."""

_NEXT_LINK = re_compile(r'<([^>]+)>;\s*rel="next"')
"""Pattern extracting the URL of the next page from a :rfc:`8288` ``Link`` header."""


@export
class MediaType(StrEnum):
	"""
	Media types a REST API sends and receives, as :rfc:`9110` calls them.

	A member is its own media type, so it is written where a header's value is expected.
	"""

	JSON =      "application/json"          #: A JSON document.
	PlainText = "text/plain"                #: Plain text.
	HTML =      "text/html"                 #: An HTML document.
	Binary =    "application/octet-stream"  #: Bytes of an unnamed type.

	def Matches(self, contentType: str) -> bool:
		"""
		Check whether a ``Content-Type`` header names this media type.

		The header's parameters are ignored, the name is compared case-insensitively - :rfc:`9110` writes a media type
		that way - and the structured syntax suffix of :rfc:`6839` counts, so ``application/vnd.github+json`` is
		``application/json``.

		:param contentType: The value of a ``Content-Type`` header.
		:returns:           ``True``, if the header names this media type.
		:raises ValueError: If parameter 'contentType' is ``None``.
		:raises TypeError:  If parameter 'contentType' is not of type :class:`str`.
		"""
		if contentType is None:
			raise ValueError("Parameter 'contentType' is None.")
		elif not isinstance(contentType, str):
			ex = TypeError("Parameter 'contentType' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(contentType)}'.")
			raise ex

		mediaType = contentType.split(";", 1)[0].strip().lower()

		return mediaType == self or mediaType.endswith(f"+{self.partition('/')[2]}")


@export
class RESTError(ToolingException):
	"""A request to a REST API failed, or its answer wasn't the JSON the caller asked for."""


@export
class RESTClient(metaclass=ExtendedType, slots=True):
	"""
	Reads and writes JSON resources of a REST API.

	The requests use only the standard library, so a package building on this client doesn't drag an HTTP stack into
	every consumer. A resource is addressed by its path below :attr:`APIURL`, not by a URL, so a client says
	``repos/owner/name`` and the API it belongs to is stated once.

	A token, when given, is sent as a bearer token - and only to the API it was given for, which is why a paginated
	answer pointing outside that API is rejected. An API authorizing differently overrides :meth:`_RequestHeaders`,
	which is where the header is built.

	A request failing transiently - a status in :data:`TRANSIENT_HTTP_STATUS`, a timeout, or an unreachable API - is
	tried again after an exponentially growing pause, or one as long as a ``Retry-After`` header demands. A request
	failing with any other HTTP status, like 401, 403 or 404, isn't tried again, because another attempt can't
	succeed. **A request that isn't idempotent is never tried again**: repeating a ``POST`` that the API did carry
	out, but whose answer was lost, creates the resource twice.

	An instance holds no state beyond what it was constructed with, and every request builds its own headers, so one
	client can serve several threads. The pause before a retry blocks only the thread waiting for that answer.
	"""
	_apiURL:     URL             #: Base URL of the REST API, without a trailing slash.
	_token:      Nullable[str]   #: Token authorizing the requests, or ``None`` for anonymous requests.
	_headers:    dict[str, str]  #: Headers sent with every request, beside the authorization.
	_timeout:    float           #: Timeout of a single request in seconds.
	_retries:    int             #: How often a transiently failing idempotent request is tried again.
	_retryDelay: float           #: Pause in seconds before a request is tried again the first time.

	def __init__(
		self,
		apiURL:     Union[str, URL],
		token:      Nullable[str] = None,
		*,
		headers:    Nullable[dict[str, str]] = None,
		timeout:    float = 30.0,
		retries:    int = 3,
		retryDelay: float = 2.0
	) -> None:
		"""
		Initializes a client for one REST API.

		:param apiURL:      Base URL of the REST API, as a string to parse or as a :class:`~pyTooling.GenericPath.URL.URL`.
		:param token:       Optional, token authorizing the requests. Default: anonymous requests.
		:param headers:     Optional, headers sent with every request. Default: no headers beside the authorization.
		:param timeout:     Optional, timeout of a single request in seconds. Default: ``30.0``.
		:param retries:     Optional, how often a transiently failing idempotent request is tried again. ``0`` tries
		                    once. Default: ``3``.
		:param retryDelay:  Optional, pause in seconds before a request is tried again the first time. The pause doubles
		                    with every further attempt. Default: ``2.0``.
		:raises ValueError: If parameter 'apiURL' is ``None``.
		:raises TypeError:  If parameter 'apiURL' is neither of type :class:`str` nor of type
		                    :class:`~pyTooling.GenericPath.URL.URL`.
		:raises ValueError: If parameter 'apiURL' names no scheme or no host.
		:raises ValueError: If parameter 'apiURL' ends in an empty path element, e.g. ``'https://example.org/api//'``.
		:raises TypeError:  If parameter 'token' is not of type :class:`str`.
		:raises TypeError:  If parameter 'headers' is not of type :class:`dict`.
		:raises ValueError: If parameter 'timeout' is ``None``.
		:raises TypeError:  If parameter 'timeout' is not a number.
		:raises ValueError: If parameter 'timeout' isn't positive.
		:raises ValueError: If parameter 'retries' is ``None``.
		:raises TypeError:  If parameter 'retries' is not of type :class:`int`.
		:raises ValueError: If parameter 'retries' is negative.
		:raises ValueError: If parameter 'retryDelay' is ``None``.
		:raises TypeError:  If parameter 'retryDelay' is not a number.
		:raises ValueError: If parameter 'retryDelay' is negative.
		"""
		if apiURL is None:
			raise ValueError("Parameter 'apiURL' is None.")
		elif isinstance(apiURL, str):
			parsedURL = URL.Parse(apiURL).WithoutTrailingSlash()
		elif isinstance(apiURL, URL):
			parsedURL = apiURL.WithoutTrailingSlash()
		else:
			ex = TypeError("Parameter 'apiURL' is neither of type 'str' nor of type 'URL'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(apiURL)}'.")
			raise ex

		if parsedURL.Scheme is None or parsedURL.Host is None:
			ex = ValueError("Parameter 'apiURL' names no scheme or no host.")
			ex.add_note(f"Got value '{apiURL}'.")
			raise ex

		# One trailing slash is what a base URL is usually written with, and it was just removed. A path still ending
		# in one named an empty element, which every request would carry as a double slash.
		if str(parsedURL.Path).endswith("/"):
			ex = ValueError("Parameter 'apiURL' ends in an empty path element.")
			ex.add_note(f"Got value '{apiURL}'.")
			raise ex

		if token is not None and not isinstance(token, str):
			ex = TypeError("Parameter 'token' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(token)}'.")
			raise ex

		if headers is not None and not isinstance(headers, dict):
			ex = TypeError("Parameter 'headers' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(headers)}'.")
			raise ex

		if timeout is None:
			raise ValueError("Parameter 'timeout' is None.")
		elif isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
			ex = TypeError("Parameter 'timeout' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(timeout)}'.")
			raise ex
		elif timeout <= 0:
			ex = ValueError("Parameter 'timeout' isn't positive.")
			ex.add_note(f"Got value '{timeout}'.")
			raise ex

		if retries is None:
			raise ValueError("Parameter 'retries' is None.")
		elif isinstance(retries, bool) or not isinstance(retries, int):
			ex = TypeError("Parameter 'retries' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retries)}'.")
			raise ex
		elif retries < 0:
			ex = ValueError("Parameter 'retries' is negative.")
			ex.add_note(f"Got value '{retries}'.")
			raise ex

		if retryDelay is None:
			raise ValueError("Parameter 'retryDelay' is None.")
		elif isinstance(retryDelay, bool) or not isinstance(retryDelay, (int, float)):
			ex = TypeError("Parameter 'retryDelay' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retryDelay)}'.")
			raise ex
		elif retryDelay < 0:
			ex = ValueError("Parameter 'retryDelay' is negative.")
			ex.add_note(f"Got value '{retryDelay}'.")
			raise ex

		self._apiURL =     parsedURL
		self._token =      token
		self._headers =    {} if headers is None else dict(headers)
		self._timeout =    float(timeout)
		self._retries =    retries
		self._retryDelay = float(retryDelay)

	@readonly
	def APIURL(self) -> URL:
		"""
		Read-only property to access the base URL of the REST API (:attr:`_apiURL`).

		:returns: The base URL, without a trailing slash.
		"""
		return self._apiURL

	@readonly
	def Headers(self) -> dict[str, str]:
		"""
		Read-only property to return the headers sent with every request (:attr:`_headers`).

		:returns: A copy of the headers, so changing it doesn't change what the client sends.
		"""
		return dict(self._headers)

	@readonly
	def Timeout(self) -> float:
		"""
		Read-only property to access the timeout of a single request (:attr:`_timeout`).

		:returns: The timeout in seconds.
		"""
		return self._timeout

	@readonly
	def Retries(self) -> int:
		"""
		Read-only property to access how often a transiently failing request is tried again (:attr:`_retries`).

		:returns: The number of further attempts.
		"""
		return self._retries

	@readonly
	def RetryDelay(self) -> float:
		"""
		Read-only property to access the pause before a request is tried again the first time (:attr:`_retryDelay`).

		:returns: The pause in seconds.
		"""
		return self._retryDelay

	def GetJSONObject(
		self,
		resourcePath: str,
		headers:      Nullable[dict[str, str]] = None
	) -> tuple[JSONObject, Nullable[str]]:
		"""
		Read a resource as a JSON object.

		:param resourcePath: Path of the resource below :attr:`APIURL`, e.g. ``'repos/owner/name'``.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:returns:            The JSON object, and the path of the next page, or ``None`` if the answer names none.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails, or the answer isn't a JSON object.
		"""
		document, nextResourcePath = self._Request(HTTPMethod.GET, resourcePath, headers=headers)
		if document is None:
			raise RESTError(f"API answered with an empty body: {self._apiURL / resourcePath.lstrip('/')}")

		return document, nextResourcePath

	def PostJSONObject(
		self,
		resourcePath: str,
		document:     JSONObject,
		headers:      Nullable[dict[str, str]] = None
	) -> Nullable[JSONObject]:
		"""
		Create a resource from a JSON object.

		A ``POST`` isn't idempotent, so a transient failure isn't tried again - the API may have created the resource
		and lost only the answer.

		:param resourcePath: Path of the collection below :attr:`APIURL`, e.g. ``'repos/owner/name/issues'``.
		:param document:     The JSON object to send.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:returns:            The answer's JSON object, or ``None`` if the API answered with no body.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises ValueError:  If parameter 'document' is ``None``.
		:raises TypeError:   If parameter 'document' is not of type :class:`dict`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails, or the answer is neither empty nor a JSON object.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")

		return self._Request(HTTPMethod.POST, resourcePath, document, headers, idempotent=False)[0]

	def PutJSONObject(
		self,
		resourcePath: str,
		document:     JSONObject,
		headers:      Nullable[dict[str, str]] = None
	) -> Nullable[JSONObject]:
		"""
		Replace a resource by a JSON object.

		:param resourcePath: Path of the resource below :attr:`APIURL`, e.g. ``'repos/owner/name/issues/1'``.
		:param document:     The JSON object to send.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:returns:            The answer's JSON object, or ``None`` if the API answered with no body.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises ValueError:  If parameter 'document' is ``None``.
		:raises TypeError:   If parameter 'document' is not of type :class:`dict`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails, or the answer is neither empty nor a JSON object.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")

		return self._Request(HTTPMethod.PUT, resourcePath, document, headers)[0]

	def PatchJSONObject(
		self,
		resourcePath: str,
		document:     JSONObject,
		headers:      Nullable[dict[str, str]] = None
	) -> Nullable[JSONObject]:
		"""
		Alter a resource by a JSON object holding the fields to change.

		:rfc:`9110` doesn't call ``PATCH`` idempotent - whether applying the same change twice is the same as applying
		it once depends on the change - so a transient failure isn't tried again.

		:param resourcePath: Path of the resource below :attr:`APIURL`, e.g. ``'repos/owner/name/issues/1'``.
		:param document:     The JSON object holding the fields to change.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:returns:            The answer's JSON object, or ``None`` if the API answered with no body.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises ValueError:  If parameter 'document' is ``None``.
		:raises TypeError:   If parameter 'document' is not of type :class:`dict`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails, or the answer is neither empty nor a JSON object.
		"""
		if document is None:
			raise ValueError("Parameter 'document' is None.")

		return self._Request(HTTPMethod.PATCH, resourcePath, document, headers, idempotent=False)[0]

	def DeleteResource(self, resourcePath: str, headers: Nullable[dict[str, str]] = None) -> Nullable[JSONObject]:
		"""
		Delete a resource.

		:param resourcePath: Path of the resource below :attr:`APIURL`, e.g. ``'repos/owner/name/issues/1'``.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:returns:            The answer's JSON object, or ``None`` if the API answered with no body, which is what a
		                     deletion usually answers with.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails, or the answer is neither empty nor a JSON object.
		"""
		return self._Request(HTTPMethod.DELETE, resourcePath, headers=headers)[0]

	def _Request(
		self,
		method:       HTTPMethod,
		resourcePath: str,
		document:     Nullable[JSONObject] = None,
		headers:      Nullable[dict[str, str]] = None,
		idempotent:   bool = True
	) -> tuple[Nullable[JSONObject], Nullable[str]]:
		"""
		Send one request to the REST API and read its answer.

		:param method:       The HTTP method.
		:param resourcePath: Path of the resource below :attr:`APIURL`.
		:param document:     Optional, the JSON object to send as the request's body. Default: no body.
		:param headers:      Optional, headers for this request, added to and overriding :attr:`Headers`.
		:param idempotent:   Optional, ``True``, if repeating the request has the same effect as sending it once, which
		                     is what makes trying it again safe. Default: ``True``.
		:returns:            The answer's JSON object or ``None`` if it had no body, and the path of the next page or
		                     ``None`` if the answer names none.
		:raises ValueError:  If parameter 'resourcePath' is ``None``.
		:raises TypeError:   If parameter 'resourcePath' is not of type :class:`str`.
		:raises TypeError:   If parameter 'document' is not of type :class:`dict`.
		:raises TypeError:   If parameter 'headers' is not of type :class:`dict`.
		:raises RESTError:   If the request fails with an HTTP error, or the API can't be reached. |br|
		                     The notes report what the API said and how often the request was tried.
		:raises RESTError:   If the answer isn't JSON, isn't valid JSON, or isn't a JSON object.
		:raises RESTError:   If the next page's URL doesn't belong to this API. |br|
		                     The note says that the token is only sent to the API itself.
		"""
		if resourcePath is None:
			raise ValueError("Parameter 'resourcePath' is None.")
		elif not isinstance(resourcePath, str):
			ex = TypeError("Parameter 'resourcePath' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(resourcePath)}'.")
			raise ex

		if document is not None and not isinstance(document, dict):
			ex = TypeError("Parameter 'document' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(document)}'.")
			raise ex

		if headers is not None and not isinstance(headers, dict):
			ex = TypeError("Parameter 'headers' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(headers)}'.")
			raise ex

		if document is None:
			data =      None
			mediaType = None
		else:
			data =      json_dumps(document).encode("utf-8")
			mediaType = MediaType.JSON

		# A resource path is always **below** the API, so a leading delimiter is removed - :meth:`URL.__truediv__
		# <pyTooling.GenericPath.URL.URL.__truediv__>` would otherwise read it as naming its own root.
		url =     self._apiURL / resourcePath.lstrip("/")
		request = Request(str(url), data=data, method=method, headers=self._RequestHeaders(mediaType, headers))
		retries = self._retries if idempotent else 0

		for attempt in range(1, retries + 2):
			try:
				with urlopen(request, timeout=self._timeout) as response:
					body =        response.read()
					contentType = response.headers.get("Content-Type", None)
					link =        response.headers.get("Link", None)
				break
			except HTTPError as ex:
				if ex.code in TRANSIENT_HTTP_STATUS and attempt <= retries:
					delay = self._RetryDelay(attempt)
					# :rfc:`9110` writes 'Retry-After' as a non-negative number of seconds or as an HTTP-date. Only the
					# first is honored, and only while it asks for longer than the backoff already waits.
					if ex.headers is not None and (pause := ex.headers.get("Retry-After", "")).strip().isdigit():
						delay = max(delay, min(float(pause), MAXIMUM_RETRY_AFTER))

					sleep(delay)
					continue

				error = RESTError(f"Request failed with HTTP {ex.code}: {url}")
				try:
					answer = json_loads(ex.read())
				except (OSError, ValueError):
					answer = None

				# A REST API reports the reason in a 'message' field. An answer that has none, or isn't JSON at all,
				# is not a second failure - it just says nothing.
				if isinstance(answer, dict) and isinstance(message := answer.get("message", None), str):
					error.add_note(f"Answer: {message}")

				self._AddErrorNotes(error, ex.code)
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")

				raise error from ex
			except OSError as ex:
				if attempt <= retries:
					sleep(self._RetryDelay(attempt))
					continue

				error = RESTError(f"API couldn't be reached: {url}")
				error.add_note(f"Reason: {ex.reason if isinstance(ex, URLError) else ex}")
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")

				raise error from ex

		return self._ProcessAnswer(body, contentType, url), self._NextResourcePath(link)

	def _RequestHeaders(self, mediaType: Nullable[MediaType], headers: Nullable[dict[str, str]]) -> dict[str, str]:
		"""
		Return the headers one request is sent with.

		The client's headers are the base, the authorization is added, and this request's own headers win, so a caller
		can state an ``Accept`` or a conditional header for a single request.

		:param mediaType: The media type of the request's body, or ``None`` for a request without one.
		:param headers:   This request's headers, or ``None``.
		:returns:         The headers of this request.
		"""
		requestHeaders = dict(self._headers)
		# The bearer scheme of :rfc:`6750` is what a token-based REST API expects, and what an OAuth 2.0 flow's access
		# token is used with once the flow handed one out. An API authorizing differently overrides this method.
		if self._token is not None:
			requestHeaders["Authorization"] = f"Bearer {self._token}"

		if mediaType is not None:
			requestHeaders["Content-Type"] = mediaType

		if headers is not None:
			requestHeaders.update(headers)

		return requestHeaders

	def _AddErrorNotes(self, error: RESTError, status: int) -> None:
		"""
		Add notes explaining what an HTTP status means for this API.

		A derived class overrides this to say what a caller can do about a status its API answers with. The default
		adds nothing, because a status alone says the same for every API.

		:param error:  The error the notes are added to.
		:param status: The HTTP status the request failed with.
		"""

	def _RetryDelay(self, attempt: int) -> float:
		"""
		Return the pause before a request is tried again.

		The pause grows exponentially: :attr:`RetryDelay` doubled for every earlier attempt.

		:param attempt: The attempt that failed, starting at 1.
		:returns:       The pause in seconds.
		"""
		return self._retryDelay * 2 ** (attempt - 1)

	def _ProcessAnswer(self, body: bytes, contentType: Nullable[str], url: URL) -> Nullable[JSONObject]:
		"""
		Read an answer's body as a JSON object.

		:param body:        The answer's body.
		:param contentType: The answer's ``Content-Type`` header, or ``None``.
		:param url:         The URL that was requested.
		:returns:           The JSON object, or ``None`` if the answer had no body.
		:raises RESTError:  If the answer's media type isn't JSON. |br|
		                    The note reports the media type that was announced.
		:raises RESTError:  If the answer isn't valid JSON.
		:raises RESTError:  If the answer is JSON, but not a JSON object.
		"""
		if len(body) == 0:
			return None

		if contentType is not None and not MediaType.JSON.Matches(contentType):
			error = RESTError(f"API didn't answer with JSON: {url}")
			error.add_note(f"Got 'Content-Type: {contentType}'.")
			raise error

		try:
			document = json_loads(body)
		except ValueError as ex:
			raise RESTError(f"API answered with invalid JSON: {url}") from ex

		if not isinstance(document, dict):
			raise RESTError(f"API didn't answer with a JSON object: {url}")

		return document

	def _NextResourcePath(self, link: Nullable[str]) -> Nullable[str]:
		"""
		Return where a paginated collection continues.

		:param link:       The answer's :rfc:`8288` ``Link`` header, or ``None``.
		:returns:          Path of the next page below :attr:`APIURL`, or ``None`` if the answer names none.
		:raises RESTError: If the next page's URL doesn't belong to this API. |br|
		                   The note says that the token is only sent to the API itself.
		"""
		if link is None:
			return None
		elif (match := _NEXT_LINK.search(link)) is None:
			return None

		nextURL = match.group(1)
		prefix =  f"{self._apiURL}/"
		if not nextURL.startswith(prefix):
			error = RESTError(f"The next page is outside the API: {nextURL}")
			error.add_note("The request's token is only sent to the API itself.")
			raise error

		return nextURL[len(prefix):]
