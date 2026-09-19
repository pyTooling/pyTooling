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
Unit tests for :class:`pyTooling.REST.RESTClient`.
"""
from json              import dumps as json_dumps
from typing            import Any, Optional as Nullable
from unittest          import mock
from urllib.error      import HTTPError, URLError

from pyTooling.REST    import RESTClient, RESTError
from pyTooling.Testing import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


API = "https://api.example.org"


class _Response:
	"""A fake HTTP response for :func:`urllib.request.urlopen`."""

	def __init__(self, document: Any, link: Nullable[str] = None) -> None:
		"""
		Initializes a fake response.

		:param document: The JSON document to answer with.
		:param link:     Optional, the ``Link`` header.
		"""
		self._body = document if isinstance(document, bytes) else json_dumps(document).encode()
		self.headers = {} if link is None else {"Link": link}

	def read(self) -> bytes:
		"""
		Return the response's body.

		:returns: The encoded JSON document.
		"""
		return self._body

	def close(self) -> None:
		"""
		Close the response, as :class:`~urllib.error.HTTPError` does with the response it wraps.
		"""

	def __enter__(self) -> "_Response":
		"""
		Enter the response's context.

		:returns: The response.
		"""
		return self

	def __exit__(self, *_: Any) -> None:
		"""
		Leave the response's context.

		:param _: Exception information.
		"""


class Construction(Testcase):
	def test_Defaults(self) -> None:
		client = RESTClient(f"{API}/")

		self.assertEqual(API, client.APIURL)
		self.assertEqual({}, client.Headers)
		self.assertEqual(30.0, client.Timeout)
		self.assertEqual(3, client.Retries)
		self.assertEqual(2.0, client.RetryDelay)

	def test_HeadersAreCopied(self) -> None:
		headers = {"Accept": "application/json"}
		client = RESTClient(API, headers=headers)
		headers["Accept"] = "text/plain"

		self.assertEqual({"Accept": "application/json"}, client.Headers)

		client.Headers["Accept"] = "text/plain"
		self.assertEqual({"Accept": "application/json"}, client.Headers)

	def test_WrongTypes(self) -> None:
		for parameters in ({"apiURL": 1}, {"apiURL": API, "token": 1}, {"apiURL": API, "headers": 1}):
			with self.subTest(parameters=parameters):
				with self.assertRaises(TypeError):
					_ = RESTClient(**parameters)

		for name, value in (("timeout", "1"), ("retries", 1.0), ("retryDelay", "1")):
			with self.subTest(parameter=name):
				with self.assertRaises(TypeError):
					_ = RESTClient(API, **{name: value})

	def test_WrongValues(self) -> None:
		for name, value in (("timeout", 0.0), ("retries", -1), ("retryDelay", -1.0)):
			with self.subTest(parameter=name):
				with self.assertRaises(ValueError):
					_ = RESTClient(API, **{name: value})


class Requests(Testcase):
	def test_JSONObject(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({"id": 4711})) as urlopen:
			document, nextURL = RESTClient(API).GetJSONObject(f"{API}/things/4711")

		self.assertEqual({"id": 4711}, document)
		self.assertIsNone(nextURL)
		self.assertEqual(f"{API}/things/4711", urlopen.call_args.args[0].full_url)

	def test_BearerToken(self) -> None:
		client = RESTClient(API, "s3cr3t", headers={"Accept": "application/json"})
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({})) as urlopen:
			client.GetJSONObject(f"{API}/things")

		headers = urlopen.call_args.args[0].headers
		self.assertEqual("Bearer s3cr3t", headers["Authorization"])
		self.assertEqual("application/json", headers["Accept"])

	def test_AnonymousRequestSendsNoAuthorization(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({})) as urlopen:
			RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertNotIn("Authorization", urlopen.call_args.args[0].headers)

	def test_NextPage(self) -> None:
		link = f'<{API}/things?page=2>; rel="next", <{API}/things?page=9>; rel="last"'
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({}, link)):
			_, nextURL = RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertEqual(f"{API}/things?page=2", nextURL)

	def test_LastPage(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({}, f'<{API}/things?page=1>; rel="prev"')):
			_, nextURL = RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertIsNone(nextURL)

	def test_NextPageOutsideTheAPI(self) -> None:
		link = '<https://evil.example.com/things?page=2>; rel="next"'
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response({}, link)):
			with self.assertRaises(RESTError) as context:
				RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertIn("outside the API", str(context.exception))

	def test_InvalidJSON(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response(b"<html>")):
			with self.assertRaises(RESTError) as context:
				RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertIn("invalid JSON", str(context.exception))

	def test_JSONArray(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", return_value=_Response([1, 2, 3])):
			with self.assertRaises(RESTError) as context:
				RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertIn("didn't answer with a JSON object", str(context.exception))


class Failures(Testcase):
	def _Fail(self, status: int, headers: Nullable[dict[str, str]] = None, message: str = "failure"):
		"""
		Return a ``urlopen`` replacement failing every request with an HTTP error.

		:param status:  The HTTP status to fail with.
		:param headers: Optional, the failed answer's headers.
		:param message: Optional, the ``message`` field of the failed answer's body.
		:returns:       The replacement.
		"""
		def urlopen(request, **_: Any):
			raise HTTPError(request.full_url, status, "failure", headers or {}, _Response({"message": message}))

		return urlopen

	def test_HTTPErrorIsNotRetried(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(404)) as urlopen:
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError) as context:
					RESTClient(API).GetJSONObject(f"{API}/things")

		self.assertEqual(1, urlopen.call_count)
		sleep.assert_not_called()
		self.assertIn("HTTP 404", str(context.exception))
		self.assertIn("Answer: failure", context.exception.__notes__)

	def test_TransientStatusIsRetried(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(503)) as urlopen:
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError) as context:
					RESTClient(API, retries=3, retryDelay=2.0).GetJSONObject(f"{API}/things")

		self.assertEqual(4, urlopen.call_count)
		self.assertEqual([mock.call(2.0), mock.call(4.0), mock.call(8.0)], sleep.call_args_list)
		self.assertIn("Tried 4 times.", context.exception.__notes__)

	def test_RetryAfterWinsWhenItIsLonger(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(429, {"Retry-After": "30"})):
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError):
					RESTClient(API, retries=1, retryDelay=2.0).GetJSONObject(f"{API}/things")

		self.assertEqual([mock.call(30.0)], sleep.call_args_list)

	def test_RetryAfterIsCapped(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(429, {"Retry-After": "3600"})):
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError):
					RESTClient(API, retries=1, retryDelay=2.0).GetJSONObject(f"{API}/things")

		self.assertEqual([mock.call(60.0)], sleep.call_args_list)

	def test_UnparsableRetryAfterIsIgnored(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(429, {"Retry-After": "Tue, 1 Sep 2026 12:00"})):
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError):
					RESTClient(API, retries=1, retryDelay=2.0).GetJSONObject(f"{API}/things")

		self.assertEqual([mock.call(2.0)], sleep.call_args_list)

	def test_UnreachableAPIIsRetried(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=URLError("no route to host")) as urlopen:
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError) as context:
					RESTClient(API, retries=2, retryDelay=0.5).GetJSONObject(f"{API}/things")

		self.assertEqual(3, urlopen.call_count)
		self.assertEqual([mock.call(0.5), mock.call(1.0)], sleep.call_args_list)
		self.assertIn("couldn't be reached", str(context.exception))

	def test_TimeoutIsRetried(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=TimeoutError("timed out")) as urlopen:
			with mock.patch("pyTooling.REST.sleep"):
				with self.assertRaises(RESTError):
					RESTClient(API, retries=1).GetJSONObject(f"{API}/things")

		self.assertEqual(2, urlopen.call_count)

	def test_NoRetries(self) -> None:
		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(503)) as urlopen:
			with mock.patch("pyTooling.REST.sleep") as sleep:
				with self.assertRaises(RESTError):
					RESTClient(API, retries=0).GetJSONObject(f"{API}/things")

		self.assertEqual(1, urlopen.call_count)
		sleep.assert_not_called()

	def test_DerivedClassExplainsAStatus(self) -> None:
		class _Client(RESTClient):
			"""A client explaining what a status means for its API."""

			def _AddErrorNotes(self, error: RESTError, status: int) -> None:
				"""
				Add a note for a status this API answers with.

				:param error:  The error the note is added to.
				:param status: The HTTP status the request failed with.
				"""
				if status == 404:
					error.add_note("Check the thing's name.")

		with mock.patch("pyTooling.REST.urlopen", side_effect=self._Fail(404)):
			with self.assertRaises(RESTError) as context:
				_Client(API).GetJSONObject(f"{API}/things")

		self.assertIn("Check the thing's name.", context.exception.__notes__)
