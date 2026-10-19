# ==================================================================================================================== #
#             _____           _ _               ____                            _                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \  ___ _ __   ___ _ __   __| | ___ _ __   ___ _   _                #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | |/ _ \ '_ \ / _ \ '_ \ / _` |/ _ \ '_ \ / __| | | |               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| |  __/ |_) |  __/ | | | (_| |  __/ | | | (__| |_| |               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \___| .__/ \___|_| |_|\__,_|\___|_| |_|\___|\__, |               #
# |_|    |___/                          |___/             |_|                                     |___/                #
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
Fake package-index sessions for the :mod:`pyTooling.Dependency` tests: they answer from JSON documents held in
memory, so no request leaves the process.
"""
from json     import dumps

from requests import Response


class DocumentSession:
	"""HTTP session answering from a dictionary of JSON documents by endpoint, so no request leaves the process."""

	def __init__(self, api: str, documents: dict[str, dict]) -> None:
		"""
		Initializes the session with the documents it answers.

		:param api:       The index's API URL, stripped from a requested URL to find its endpoint.
		:param documents: JSON documents by endpoint (``project/json``); an endpoint not listed answers 404.
		"""
		self._api =       api
		self._documents = documents
		self.Requests =   []

	def get(self, url: str) -> Response:
		"""
		Answer a GET request with the endpoint's document, or with ``404 Not Found``.

		:param url: The requested URL.
		:returns:   The response.
		"""
		endpoint = url.removeprefix(self._api)
		self.Requests.append(endpoint)

		response = Response()
		response.url = url
		if (document := self._documents.get(endpoint, None)) is None:
			response.status_code = 404
		else:
			response.status_code = 200
			response._content =    dumps(document).encode()

		return response


def ProjectDocument(name: str, *versions: str) -> dict:
	"""
	Return the JSON document a package index answers for a project.

	:param name:     The project's name.
	:param versions: The versions of its releases.
	:returns:        The document.
	"""
	releases = {}
	for version in versions:
		releases[version] = [{
			"filename":             f"{name}-{version}.tar.gz",
			"url":                  f"https://files.index.org/{name}-{version}.tar.gz",
			"upload_time_iso_8601": "2026-01-01T00:00:00.000000Z"
		}]

	return {"info": {"project_url": f"https://index.org/project/{name}/"}, "releases": releases}


class DocumentResponse:
	"""Response of a :class:`DocumentClientSession`, used as an asynchronous context manager like :mod:`aiohttp`'s."""

	def __init__(self, document: dict | None) -> None:
		"""
		Initializes the response.

		:param document: The JSON document answered, or ``None`` for ``404 Not Found``.
		"""
		self._document = document
		self.status =    404 if document is None else 200

	async def __aenter__(self) -> "DocumentResponse":
		"""
		Enter the context and hand out the response.

		:returns: The response itself.
		"""
		return self

	async def __aexit__(self, *_) -> None:
		"""
		Exit the context; nothing to release.

		:returns: ``None``
		"""
		return None

	def raise_for_status(self) -> None:
		"""Do nothing: a response with a document is ``200 OK``, and ``404 Not Found`` is checked before."""

	async def json(self) -> dict:
		"""
		Return the document.

		:returns: The JSON document.
		"""
		return self._document


class DocumentClientSession:
	"""
	Stand-in for :class:`aiohttp.ClientSession`, answering from a dictionary of JSON documents by endpoint.

	Each instance records the endpoints requested through it in :attr:`Requests`; :attr:`Sessions` of the class
	collects the instances, so a test sees which requests ran together.
	"""

	Documents: dict[str, dict]                = {}  #: JSON documents by endpoint, shared by all instances.
	Sessions:  list["DocumentClientSession"] = []  #: Every session opened, in order.

	def __init__(self, **_) -> None:
		"""Initializes a session; the arguments of :class:`aiohttp.ClientSession` are ignored."""
		self.Requests = []
		DocumentClientSession.Sessions.append(self)

	async def __aenter__(self) -> "DocumentClientSession":
		"""
		Enter the context and hand out the session.

		:returns: The session itself.
		"""
		return self

	async def __aexit__(self, *_) -> None:
		"""
		Exit the context; nothing to release.

		:returns: ``None``
		"""
		return None

	def get(self, endpoint: str) -> DocumentResponse:
		"""
		Answer a GET request with the endpoint's document, or with ``404 Not Found``.

		:param endpoint: The requested endpoint, relative to the base URL.
		:returns:        The response.
		"""
		self.Requests.append(endpoint)
		return DocumentResponse(DocumentClientSession.Documents.get(endpoint, None))
