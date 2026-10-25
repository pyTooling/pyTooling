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


.. _STRUCT/Path/URL/IRI:

Internationalized Resource Identifiers (IRI)
********************************************

A URL of :rfc:`3986` holds ASCII characters only. An *Internationalized Resource Identifier* (IRI, :rfc:`3987`) is
the same syntax with Unicode characters allowed, and an internationalized domain name (IDN) in its host is carried as
*A-labels*, the ASCII form IDNA 2008 defines: ``xn--`` followed by the Punycode of the label.
:meth:`URL.Parse(url, iri=True) <pyTooling.GenericPath.URL.URL.Parse>` reads an IRI and maps it to a URL, as
:rfc:`RFC 3987, section 3.1 <3987#section-3.1>` describes:

* A Unicode host is converted to its A-labels by IDNA 2008 (:rfc:`5890`, :rfc:`5891`), after the mapping of
  `UTS #46 <https://www.unicode.org/reports/tr46/>`__.
* Every other non-ASCII character - in the user information, the path, the query and the fragment - is percent-encoded
  as UTF-8.

So the parsed :class:`~pyTooling.GenericPath.URL.URL` is an :rfc:`3986` URL either way, and :func:`str` renders it in
ASCII. :attr:`Host.UnicodeHostname <pyTooling.GenericPath.URL.Host.UnicodeHostname>` decodes the A-labels again, for a
user to read.

.. admonition:: Example

   .. code-block:: Python

      from pyTooling.GenericPath.URL import URL

      url = URL.Parse("https://www.müller.de/", iri=True)
      print(url)                       # https://www.xn--mller-kva.de/
      print(url.Host.Hostname)         # www.xn--mller-kva.de
      print(url.Host.UnicodeHostname)  # www.müller.de

      url = URL.Parse("https://de.wikipedia.org/wiki/Straße", iri=True)
      print(url)                       # https://de.wikipedia.org/wiki/Stra%C3%9Fe

      url = URL.Parse("https://www.müller.de/")
      # URLError: Syntax error when parsing URL 'https://www.müller.de/'.
      #   A URL holds ASCII characters only. Read an IRI, which holds Unicode characters, with 'iri=True'.

The host is mapped the way browsers map it. The `WHATWG URL Standard <https://url.spec.whatwg.org/#host-parsing>`__
converts a host with *domain to ASCII*, which is UTS #46 processing: case folding (``MÜLLER.de`` |rarr|
``xn--mller-kva.de``), width mapping of full-width letters and the ideographic full stop (``。``) as a dot, then IDNA
2008. It processes *non-transitionally*, as IDNA 2008 does: ``ß`` stays ``ß``, so ``straße.de`` is
``xn--strae-oqa.de`` - the domain DENIC registers -, where IDNA 2003 and Python's built-in ``idna`` codec map it to
``strasse.de``, a different domain. A character IDNA 2008 disallows, e.g. a symbol as in ``☃.net`` which IDNA 2003
accepted, raises :exc:`~pyTooling.GenericPath.URL.URLError` with IDNA's reason as note.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Specification
     - What it decides here
   * - :rfc:`3986`
     - The syntax of a URL (URI), in ASCII. :meth:`~pyTooling.GenericPath.URL.URL.Parse` reads it by default.
   * - :rfc:`3987`
     - The IRI and its mapping to a URI: percent-encode UTF-8, convert the host with IDNA.
   * - :rfc:`5890`, :rfc:`5891`
     - IDNA 2008: A-labels and U-labels, and which characters a label may hold.
   * - `UTS #46 <https://www.unicode.org/reports/tr46/>`__
     - The mapping before IDNA 2008: case folding, width mapping, label separators; non-transitional.
   * - `WHATWG URL Standard <https://url.spec.whatwg.org/>`__
     - What browsers do: *domain to ASCII* with UTS #46, which :meth:`~pyTooling.GenericPath.URL.URL.Parse` follows.

The conversion needs the `idna <https://pypi.org/project/idna/>`__ package, installed by the extra ``idna``
(``pip install pyTooling[idna]``). Without it, converting a Unicode host or decoding an A-label raises
:exc:`~pyTooling.Exceptions.MissingDependencyError`; an IRI whose host is ASCII, and an ASCII host without A-labels,
need no package.


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
