.. _REST:

Overview
########

:mod:`pyTooling.REST` reads and writes **JSON resources of a REST API**, with the standard library and nothing else.

.. code-block:: python

   from pyTooling.REST import RESTClient

   client = RESTClient("https://api.example.org", token, headers={"Accept": "application/json"})

   thing = client.GetJSONObject("things/4711")[0]
   client.PatchJSONObject("things/4711", {"state": "closed"})

Every REST API is read the same way, and none of that is knowledge about a particular service: a request carrying a
bearer token, an answer that has to be a JSON object, a transient failure that is worth another attempt, and a
collection that arrives one page at a time.

.. _REST/Resources:

Resources
*********

A client is constructed with the API's base URL, and every request names a **resource path** below it - the API is
stated once, not in every call. The two are composed by
:meth:`URL.__truediv__ <pyTooling.GenericPath.URL.URL.__truediv__>`, which puts a query the resource path carries
where a query belongs instead of leaving it inside a path element.

The base URL is a :class:`~pyTooling.GenericPath.URL.URL`, so a value that names no
scheme or no host is refused where it is given rather than where it is requested. It may be given as a ``URL``, which
is then kept as it is, or as a string, which is parsed once; either way a trailing slash is removed, so
``https://example.org/api/v3/`` and ``https://example.org/api/v3`` are the same client.

``https://example.org/api//`` is refused, though. :rfc:`3986` allows an empty path element - ``segment = *pchar`` -
so it is a valid URL and :meth:`~pyTooling.GenericPath.URL.URL.Parse` reads it, and normalization doesn't collapse
one either. As a *base* URL it is a typo, and every request would carry it as a double slash.

+----------------------------------------------------------+-------------------------------------------------------+
| Method                                                    | What it does                                          |
+==========================================================+=======================================================+
| :meth:`~pyTooling.REST.RESTClient.GetJSONObject`          | Read a resource, and say where its next page is.      |
+----------------------------------------------------------+-------------------------------------------------------+
| :meth:`~pyTooling.REST.RESTClient.PostJSONObject`         | Create a resource in a collection.                    |
+----------------------------------------------------------+-------------------------------------------------------+
| :meth:`~pyTooling.REST.RESTClient.PutJSONObject`          | Replace a resource.                                   |
+----------------------------------------------------------+-------------------------------------------------------+
| :meth:`~pyTooling.REST.RESTClient.PatchJSONObject`        | Change some fields of a resource.                     |
+----------------------------------------------------------+-------------------------------------------------------+
| :meth:`~pyTooling.REST.RESTClient.DeleteResource`         | Delete a resource.                                    |
+----------------------------------------------------------+-------------------------------------------------------+

A write sends its JSON object as the body and answers with the API's answer, or ``None`` where the API answers with
no body - which is what a deletion usually does. The body's ``Content-Type`` is a member of
:class:`~pyTooling.REST.MediaType`, which is its own media type, so it is written where a header's value is expected.
The method itself is a member of :class:`http.HTTPMethod`, the standard library's own enumeration of what :rfc:`9110`
defines.

An answer that isn't a JSON object - an array, an HTML error page, a truncated body - raises a
:exc:`~pyTooling.REST.RESTError` naming the URL, rather than being handed on as something a caller has to check. The
answer's media type is checked first, by :meth:`MediaType.Matches <pyTooling.REST.MediaType.Matches>`: it ignores the
header's parameters, compares the name case-insensitively, and counts the :rfc:`6839` structured syntax suffix, so
``application/vnd.github+json`` is ``application/json``.

.. _REST/Pagination:

Pagination
**********

:meth:`~pyTooling.REST.RESTClient.GetJSONObject` answers with the resource path of the next page, or ``None`` when
the answer names none, so a collection is read by a loop that ends by itself:

.. code-block:: python

   resourcePath = "things?per_page=100"
   while resourcePath is not None:
     page, resourcePath = client.GetJSONObject(resourcePath)
     for thing in page["things"]:
       print(thing["name"])

The next page is read from the :rfc:`8288` ``Link`` header, which is how a paginated REST API says where its
collection continues. A ``Link`` header pointing outside :attr:`~pyTooling.REST.RESTClient.APIURL` is rejected
instead of followed: a token is only sent to the API it was given for, and a next page elsewhere would take it along.

.. _REST/Retries:

Retries
*******

A request failing transiently is tried again: a status in :data:`~pyTooling.REST.TRANSIENT_HTTP_STATUS` (429, 500,
502, 503 and 504), a timeout, or an API that can't be reached. The pause grows exponentially -
:attr:`~pyTooling.REST.RESTClient.RetryDelay` doubled for every earlier attempt - or lasts as long as a
``Retry-After`` header demands, if that is longer, but never longer than
:data:`~pyTooling.REST.MAXIMUM_RETRY_AFTER`. :rfc:`9110` writes that header as a non-negative number of seconds or as
an HTTP-date; only the first is honored, because a date says when to try again and not how long a backoff should be.

A request failing with any other HTTP status, like 401, 403 or 404, isn't tried again, because another attempt can't
succeed. Its error carries what the API said: the ``message`` field of the answer's body, and the number of attempts
when there was more than one.

.. important::

   **A request that isn't idempotent is never tried again.** A ``POST`` the API did carry out, but whose answer was
   lost on the way back, would create the resource a second time; :rfc:`9110` doesn't call ``PATCH`` idempotent
   either. ``GET``, ``PUT`` and ``DELETE`` are retried, ``POST`` and ``PATCH`` are sent once.

An instance holds no state beyond what it was constructed with, and every request builds its own headers, so one
client can serve several threads. A pause before a retry blocks only the thread waiting for that answer.

.. _REST/Deriving:

A client for one API
********************

A derived class is what turns the generic client into a reader of one service: it fixes the base URL and the headers
that service expects, and adds the requests it offers as methods.

:meth:`~pyTooling.REST.RESTClient._AddErrorNotes` is the hook for what an API states about itself: what a status
means there - a 404 from an API that reads repositories is worth a different sentence than a 404 from one that reads
invoices.

The ``Authorization`` header carries the bearer scheme of :rfc:`6750`, which is what a token-based API expects and
what an OAuth 2.0 flow's access token is used with once the flow handed one out. An API expecting something else -
the basic scheme of :rfc:`7617`, say - overrides :meth:`~pyTooling.REST.RESTClient._RequestHeaders`, which is where
every header of a request is decided.

.. code-block:: python

   class ExampleClient(RESTClient):
     def __init__(self, token = None) -> None:
       super().__init__("https://api.example.org", token, headers={"Accept": "application/json"})

     def ReadThing(self, name: str) -> JSONObject:
       return self.GetJSONObject(f"things/{name}")[0]

     def _AddErrorNotes(self, error: RESTError, status: int) -> None:
       if status in (401, 403, 404):
         error.add_note("Check the thing's name, and that the token may read it.")

:mod:`pyTooling.CI.GitHub` is such a reader.
