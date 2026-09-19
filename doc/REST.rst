.. _REST:

Overview
########

:mod:`pyTooling.REST` reads **JSON objects from a REST API**, with the standard library and nothing else.

.. code-block:: python

   from pyTooling.REST import RESTClient

   client = RESTClient("https://api.example.org", token, headers={"Accept": "application/json"})

   url = "https://api.example.org/things?per_page=100"
   while url is not None:
     page, url = client.GetJSONObject(url)
     for thing in page["things"]:
       print(thing["name"])

Every REST API is read the same way, and none of that is knowledge about a particular service: a request carrying a
bearer token, an answer that has to be a JSON object, a transient failure that is worth another attempt, and a
collection that arrives one page at a time.

.. _REST/Requests:

Requests
********

:meth:`~pyTooling.REST.RESTClient.GetJSONObject` answers with the JSON object and the URL of the next page, or
``None`` when the answer names none. The next page is read from the :rfc:`8288` ``Link`` header, which is how a
paginated REST API says where its collection continues.

A token, when given, is sent as a bearer token in the ``Authorization`` header - and only to the API it was given
for. That is why a ``Link`` header pointing outside :attr:`~pyTooling.REST.RESTClient.APIURL` is rejected instead of
followed: a redirect to another host would take the token with it.

An answer that isn't a JSON object - an array, an HTML error page, a truncated body - raises a
:exc:`~pyTooling.REST.RESTError` naming the URL, rather than being handed on as something a caller has to check.

.. _REST/Retries:

Retries
*******

A request failing transiently is tried again: a status in :data:`~pyTooling.REST.TRANSIENT_HTTP_STATUS` (429, 500,
502, 503 and 504), a timeout, or an API that can't be reached. The pause before the next attempt doubles with every
attempt, starting at :attr:`~pyTooling.REST.RESTClient.RetryDelay`, or lasts as long as a ``Retry-After`` header
demands, if that is longer - but never longer than :data:`~pyTooling.REST.MAXIMUM_RETRY_AFTER`.

A request failing with any other HTTP status, like 401, 403 or 404, isn't tried again, because another attempt can't
succeed. Its error carries what the API said: the ``message`` field of the answer's body, and the number of attempts
when there was more than one.

.. _REST/Deriving:

A client for one API
********************

A derived class is what turns the generic client into a reader of one service: it fixes the base URL and the headers
that service expects, and adds the requests it offers as methods.
:meth:`~pyTooling.REST.RESTClient._AddErrorNotes` is the hook for saying what a status means there - a 404 from an
API that reads repositories is worth a different sentence than a 404 from one that reads invoices.

.. code-block:: python

   class ExampleClient(RESTClient):
     def __init__(self, token = None) -> None:
       super().__init__("https://api.example.org", token, headers={"Accept": "application/json"})

     def ReadThing(self, name: str) -> JSONObject:
       thing, _ = self.GetJSONObject(f"{self._apiURL}/things/{name}")
       return thing

     def _AddErrorNotes(self, error: RESTError, status: int) -> None:
       if status in (401, 403, 404):
         error.add_note("Check the thing's name, and that the token may read it.")

:mod:`pyTooling.CI.GitHub` is such a reader.
