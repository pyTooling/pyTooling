.. _STRUCT/Path/URL:

Unified Resource Locator (URL)
##############################

Implements a *Unified Resource Locator* (URL).

.. code-block:: Python

   url = URL.Parse("http://paebbels:xxx@semaphore.plc2.de:5000/api/v1/semaphore?name=Riviera&foo=bar#page2")
   print(url.Scheme())      # HTTP
   print(url.User())        # paebbels
   print(url.Password())    # xxx
   print(url.Host())        # semaphore.plc2.de:5000
   print(url.Path())        # /api/v1/semaphore
   print(url.Query())       # name=Riviera&foo=bar
   print(url.Fragment())    # page2


.. _STRUCT/Path/URL/Parse:

Parsing
*******

:meth:`URL.Parse <pyTooling.GenericPath.URL.URL.Parse>` reads a URL as :rfc:`3986` writes an absolute URI with an
authority: a scheme followed by ``://``, a host with an optional user, password and port, then a path starting with a
slash, a query and a fragment. Only a ``file`` or ``unix`` URL may leave the host empty, and then names an absolute
path, e.g. ``file:///etc/hosts``.

.. code-block::

   scheme://[user[:password]@]host[:port][/path/to/file][?query][#fragment]

A string that isn't such a URL raises :exc:`~pyTooling.GenericPath.URL.URLError`: ``github.com`` names no scheme,
``http:///path`` no host. A relative reference like ``things/4711`` is no URL either; it is appended to one with
:meth:`URL.__truediv__ <pyTooling.GenericPath.URL.URL.__truediv__>`.


.. _STRUCT/Path/URL/Protocols:

Protocols
*********

.. #autoclass:: pyTooling.GenericPath.URL.Protocols
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Host:

Host
****

.. #autoclass:: pyTooling.GenericPath.URL.Host
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Element:

Element
*******

.. #autoclass:: pyTooling.GenericPath.URL.Element
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Path:

Path
****

.. #autoclass:: pyTooling.GenericPath.URL.Path
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/URL:

URL
***

.. #autoclass:: pyTooling.GenericPath.URL.URL
   :show-inheritance:
   :members:
   :private-members:
