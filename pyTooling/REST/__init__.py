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
from json                  import loads as json_loads
from re                    import compile as re_compile
from time                  import sleep
from typing                import Any, Optional as Nullable
from urllib.error          import HTTPError
from urllib.request        import Request, urlopen

from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.Exceptions  import ToolingException
from pyTooling.MetaClasses import ExtendedType


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
class RESTError(ToolingException):
	"""A request to a REST API failed, or its answer wasn't the JSON object the caller asked for."""


@export
class RESTClient(metaclass=ExtendedType, slots=True):
	"""
	Reads JSON objects from a REST API.

	The requests use only the standard library, so a package building on this client doesn't drag an HTTP stack into
	every consumer. A token, when given, is sent as a bearer token - and only to the API it was given for, which is
	why a paginated answer pointing outside that API is rejected.

	A request failing transiently - a status in :data:`TRANSIENT_HTTP_STATUS`, a timeout, or an unreachable API - is
	tried again after a pause, which doubles with every attempt, or lasts as long as a ``Retry-After`` header demands.
	A request failing with any other HTTP status, like 401, 403 or 404, isn't tried again, because another attempt
	can't succeed.
	"""
	_apiURL:     str             #: Base URL of the REST API, without a trailing slash.
	_token:      Nullable[str]   #: Token authorizing the requests, or ``None`` for anonymous requests.
	_headers:    dict[str, str]  #: Headers sent with every request, beside the authorization.
	_timeout:    float           #: Timeout of a single request in seconds.
	_retries:    int             #: How often a transiently failing request is tried again.
	_retryDelay: float           #: Pause in seconds before a request is tried again the first time.

	def __init__(
		self,
		apiURL:     str,
		token:      Nullable[str] = None,
		*,
		headers:    Nullable[dict[str, str]] = None,
		timeout:    float = 30.0,
		retries:    int = 3,
		retryDelay: float = 2.0
	) -> None:
		"""
		Initializes a client for one REST API.

		:param apiURL:      Base URL of the REST API.
		:param token:       Optional, token authorizing the requests. Default: anonymous requests.
		:param headers:     Optional, headers sent with every request. Default: no headers beside the authorization.
		:param timeout:     Optional, timeout of a single request in seconds. Default: ``30.0``.
		:param retries:     Optional, how often a transiently failing request is tried again. ``0`` tries once.
		                    Default: ``3``.
		:param retryDelay:  Optional, pause in seconds before a request is tried again the first time. The pause doubles
		                    with every further attempt. Default: ``2.0``.
		:raises TypeError:  If parameter 'apiURL' is not of type :class:`str`.
		:raises TypeError:  If parameter 'token' is not of type :class:`str`.
		:raises TypeError:  If parameter 'headers' is not of type :class:`dict`.
		:raises TypeError:  If parameter 'timeout' is not a number.
		:raises ValueError: If parameter 'timeout' isn't positive.
		:raises TypeError:  If parameter 'retries' is not of type :class:`int`.
		:raises ValueError: If parameter 'retries' is negative.
		:raises TypeError:  If parameter 'retryDelay' is not a number.
		:raises ValueError: If parameter 'retryDelay' is negative.
		"""
		if not isinstance(apiURL, str):
			ex = TypeError("Parameter 'apiURL' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(apiURL)}'.")
			raise ex

		if token is not None and not isinstance(token, str):
			ex = TypeError("Parameter 'token' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(token)}'.")
			raise ex

		if headers is not None and not isinstance(headers, dict):
			ex = TypeError("Parameter 'headers' is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(headers)}'.")
			raise ex

		if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
			ex = TypeError("Parameter 'timeout' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(timeout)}'.")
			raise ex
		elif timeout <= 0:
			ex = ValueError("Parameter 'timeout' isn't positive.")
			ex.add_note(f"Got value '{timeout}'.")
			raise ex

		if isinstance(retries, bool) or not isinstance(retries, int):
			ex = TypeError("Parameter 'retries' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retries)}'.")
			raise ex
		elif retries < 0:
			ex = ValueError("Parameter 'retries' is negative.")
			ex.add_note(f"Got value '{retries}'.")
			raise ex

		if isinstance(retryDelay, bool) or not isinstance(retryDelay, (int, float)):
			ex = TypeError("Parameter 'retryDelay' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retryDelay)}'.")
			raise ex
		elif retryDelay < 0:
			ex = ValueError("Parameter 'retryDelay' is negative.")
			ex.add_note(f"Got value '{retryDelay}'.")
			raise ex

		self._apiURL =     apiURL.rstrip("/")
		self._token =      token
		self._headers =    {} if headers is None else dict(headers)
		self._timeout =    float(timeout)
		self._retries =    retries
		self._retryDelay = float(retryDelay)

	@readonly
	def APIURL(self) -> str:
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

	def GetJSONObject(self, url: str) -> tuple[JSONObject, Nullable[str]]:
		"""
		Request a JSON object from the REST API.

		A transiently failing request is tried again up to :attr:`Retries` times.

		:param url:        The URL to request.
		:returns:          The JSON object, and the URL of the next page, or ``None`` if the answer names none.
		:raises RESTError: If the request fails with an HTTP error, or the API can't be reached.
		:raises RESTError: If the answer isn't a JSON object.
		:raises RESTError: If the next page's URL doesn't belong to this API. |br|
		                   The note says that the token is only sent to the API itself.
		"""
		headers = dict(self._headers)
		if self._token is not None:
			headers["Authorization"] = f"Bearer {self._token}"

		for attempt in range(1, self._retries + 2):
			try:
				with urlopen(Request(url, headers=headers), timeout=self._timeout) as response:
					body = response.read()
					link = response.headers.get("Link", None)
				break
			except HTTPError as ex:
				if ex.code in TRANSIENT_HTTP_STATUS and attempt <= self._retries:
					sleep(self._RetryDelay(attempt, None if ex.headers is None else ex.headers.get("Retry-After", None)))
					continue

				error = RESTError(f"Request failed with HTTP {ex.code}: {url}")
				try:
					error.add_note(f"Answer: {json_loads(ex.read())['message']}")
				except Exception:  # pragma: no cover - the answer's body is optional and may be anything
					pass
				self._AddErrorNotes(error, ex.code)
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")
				raise error from ex
			except OSError as ex:
				if attempt <= self._retries:
					sleep(self._RetryDelay(attempt, None))
					continue

				error = RESTError(f"API couldn't be reached: {url}")
				error.add_note(f"Reason: {getattr(ex, 'reason', ex)}")
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")
				raise error from ex

		try:
			document = json_loads(body)
		except ValueError as ex:
			raise RESTError(f"API answered with invalid JSON: {url}") from ex

		if not isinstance(document, dict):
			raise RESTError(f"API didn't answer with a JSON object: {url}")

		nextURL = None if link is None or (match := _NEXT_LINK.search(link)) is None else match.group(1)
		if nextURL is not None and not nextURL.startswith(f"{self._apiURL}/"):
			ex = RESTError(f"The next page is outside the API: {nextURL}")
			ex.add_note("The request's token is only sent to the API itself.")
			raise ex

		return document, nextURL

	def _AddErrorNotes(self, error: RESTError, status: int) -> None:
		"""
		Add notes explaining what an HTTP status means for this API.

		A derived class overrides this to say what a caller can do about a status its API answers with. The default
		adds nothing, because a status alone says the same for every API.

		:param error:  The error the notes are added to.
		:param status: The HTTP status the request failed with.
		"""

	def _RetryDelay(self, attempt: int, retryAfter: Nullable[str]) -> float:
		"""
		Return the pause before a request is tried again.

		:param attempt:    The attempt that failed, starting at 1.
		:param retryAfter: The value of the failed answer's ``Retry-After`` header, or ``None``.
		:returns:          The pause in seconds: the retry delay doubled for every earlier attempt, or the pause the
		                   ``Retry-After`` header demands, if that is longer - but not longer than
		                   :data:`MAXIMUM_RETRY_AFTER`.
		"""
		delay = self._retryDelay * 2 ** (attempt - 1)
		try:
			return max(delay, min(float(retryAfter), MAXIMUM_RETRY_AFTER))
		except (TypeError, ValueError):
			return delay
