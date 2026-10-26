.. _STRUCT/Path/URL:

Unified Resource Locator (URL)
##############################

Implements a *Unified Resource Locator* (URL).

.. code-block:: Python

   url = URL.Parse("http://paebbels:xxx@semaphore.plc2.de:5000/api/v1/semaphore?name=Riviera&foo=bar#page2")
   print(url.Scheme)                # Protocols.HTTP
   print(url.User)                  # paebbels
   print(url.Password)              # xxx
   print(url.Host)                  # semaphore.plc2.de:5000
   print(url.Path)                  # /api/v1/semaphore
   print(url.Query["name"].Value)   # Riviera
   print(url.Fragment)              # page2


.. _STRUCT/Path/URL/Parse:

Parsing
*******

:meth:`URL.Parse <pyTooling.URI.URL.Parse>` reads a URL as :rfc:`3986` writes an absolute URI with an
authority: a scheme followed by ``://``, a host with an optional user, password and port, then a path starting with a
slash, a query and a fragment. Only a ``file`` or ``unix`` URL may leave the host empty, and then names an absolute
path, e.g. ``file:///etc/hosts``.

.. code-block::

   scheme://[user[:password]@]host[:port][/path/to/file][?query][#fragment]

A string that isn't such a URL raises :exc:`~pyTooling.URI.URLError`: ``github.com`` names no scheme,
``http:///path`` no host. A relative reference like ``things/4711`` is no URL either; it is appended to one with
:meth:`URL.__truediv__ <pyTooling.URI.URL.__truediv__>`.

A port is a number after the host's ``:``. ``http://host:/x`` (no port) and ``ssh://git@github.com:org/repo.git`` (a
path instead of a port) raise :exc:`~pyTooling.URI.URLError`, and its note gives the URL as it was
probably meant: ``http://host/x``, ``ssh://git@github.com/org/repo.git``. Git's and scp's SCP-like address
``git@github.com:org/repo.git`` names no scheme; the notes offer :ref:`SCPAddress <STRUCT/Path/URL/SCP>` and give
its URL ``ssh://git@github.com/~/org/repo.git``. In ``file://C:/Windows``, the drive letter stands where
the host is; the note gives ``file:///C:/Windows``.


.. _STRUCT/Path/URL/IRI:

Internationalized Resource Identifiers (IRI)
********************************************

A URL of :rfc:`3986` holds ASCII characters only. An *Internationalized Resource Identifier* (IRI, :rfc:`3987`) is
the same syntax with Unicode characters allowed, and an internationalized domain name (IDN) in its host is carried as
*A-labels*, the ASCII form IDNA 2008 defines: ``xn--`` followed by the Punycode of the label.
:meth:`URL.Parse(url, iri=True) <pyTooling.URI.URL.Parse>` reads an IRI and maps it to a URL, as
:rfc:`RFC 3987, section 3.1 <3987#section-3.1>` describes:

* A Unicode host is converted to its A-labels by IDNA 2008 (:rfc:`5890`, :rfc:`5891`), after the mapping of
  `UTS #46 <https://www.unicode.org/reports/tr46/>`__.
* Every other non-ASCII character - in the user information, the path, the query and the fragment - is percent-encoded
  as UTF-8.

So the parsed :class:`~pyTooling.URI.URL` is an :rfc:`3986` URL either way, and :func:`str` renders it in
ASCII. :attr:`Host.UnicodeHostname <pyTooling.URI.Host.UnicodeHostname>` decodes the A-labels again, for a
user to read.

.. admonition:: Example

   .. code-block:: Python

      from pyTooling.URI import URL

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
accepted, raises :exc:`~pyTooling.URI.URLError` with IDNA's reason as note.

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Specification
     - What it decides here
   * - :rfc:`3986`
     - The syntax of a URL (URI), in ASCII. :meth:`~pyTooling.URI.URL.Parse` reads it by default.
   * - :rfc:`3987`
     - The IRI and its mapping to a URI: percent-encode UTF-8, convert the host with IDNA.
   * - :rfc:`5890`, :rfc:`5891`
     - IDNA 2008: A-labels and U-labels, and which characters a label may hold.
   * - `UTS #46 <https://www.unicode.org/reports/tr46/>`__
     - The mapping before IDNA 2008: case folding, width mapping, label separators; non-transitional.
   * - `WHATWG URL Standard <https://url.spec.whatwg.org/>`__
     - What browsers do: *domain to ASCII* with UTS #46, which :meth:`~pyTooling.URI.URL.Parse` follows.

The conversion needs the `idna <https://pypi.org/project/idna/>`__ package, installed by the extra ``idna``
(``pip install pyTooling[idna]``). Without it, converting a Unicode host or decoding an A-label raises
:exc:`~pyTooling.Exceptions.MissingDependencyError`; an IRI whose host is ASCII, and an ASCII host without A-labels,
need no package.


.. _STRUCT/Path/URL/Query:

Query
*****

:rfc:`3986` puts no structure into a query. The common form are ``key=value`` pairs separated by ``&``, and a key may
repeat: a form with a multi-select or a group of checkboxes sends ``tag=a&tag=b``.
:attr:`URL.Query <pyTooling.URI.URL.Query>` holds the parameters by key, each a
:class:`~pyTooling.URI.QueryParameter`:

* A key written once is a :class:`~pyTooling.URI.KeyValuePair`.
* A key written several times is a :class:`~pyTooling.URI.KeySequencePair` holding every value in order.

Both answer :attr:`~pyTooling.URI.QueryParameter.Value` and
:attr:`~pyTooling.URI.QueryParameter.Values`, so a reader needn't know which one it got.
:attr:`~pyTooling.URI.QueryParameter.Value` of a repeated key is its **last** value - what a dictionary
of the pairs would keep -, and :attr:`~pyTooling.URI.QueryParameter.Values` holds all of them; for a key
written once, it holds the one value.

.. code-block:: python

   url = URL.Parse("https://example.org/search?tag=python&tag=vhdl&page=2&verbose")

   url.Query["page"].Value      # '2'
   url.Query["tag"].Value       # 'vhdl'
   url.Query["tag"].Values      # ('python', 'vhdl')
   url.Query["verbose"].Value   # None - a parameter without '='

A parameter written without ``=`` has the value ``None``, one with an empty value (``?verbose=``) the value ``""``. A
URL with an empty query (``https://example.org/?``) has an empty dictionary, a URL without a query ``None``.

:meth:`str() <pyTooling.URI.URL.__str__>` writes every value back. The values of a key are written
together, at the position of the key's first occurrence: ``?tag=a&page=2&tag=b`` is written
``?tag=a&tag=b&page=2``. A URL built by hand takes its parameters as an iterable; a key may occur once:

.. code-block:: python

   url = URL(
     Protocols.HTTPS,
     Path.Parse("/search"),
     Host("example.org"),
     query=(KeySequencePair("tag", ("python", "vhdl")), KeyValuePair("page", "2"))
   )
   # https://example.org/search?tag=python&tag=vhdl&page=2


.. _STRUCT/Path/URL/SCP:

SCP-like Addresses
******************

scp, rsync and Git also write a remote file or repository as ``[user@]host:[path]``, e.g.
``git@github.com:org/repo.git`` (`scp(1) <https://man.openbsd.org/scp.1>`__, Git's *scp-like syntax*). That is no URL:
it names no scheme, no port, no query and no fragment, and a **relative** path starts in the user's home directory,
where a URL's path starts at the root.

:meth:`SCPAddress.Parse <pyTooling.URI.SCPAddress.Parse>` reads it into an
:class:`~pyTooling.URI.SCPAddress` - :attr:`~pyTooling.URI.SCPAddress.User`,
:attr:`~pyTooling.URI.SCPAddress.Host` and :attr:`~pyTooling.URI.SCPAddress.Path` -, and
:meth:`~pyTooling.URI.SCPAddress.ToURL` converts it to the ``ssh://`` URL naming the same location.

.. code-block:: python

   address = SCPAddress.Parse("git@github.com:org/repo.git")
   address.User               # 'git'
   str(address.Host)          # 'github.com'
   str(address.Path)          # 'org/repo.git' - relative: in the home directory
   str(address.ToURL())       # 'ssh://git@github.com/~/org/repo.git'

   str(SCPAddress.Parse("deploy@server:/srv/www").ToURL())   # 'ssh://deploy@server/srv/www'

A URL can't express a path in the home directory; :meth:`~pyTooling.URI.SCPAddress.ToURL` writes it the way
Git does, as ``/~/``, and a path starting with ``~user`` keeps it. Not every SSH server expands ``~``; Git does.

As in Git, the first ``:`` separates the host, so the part before it holds no ``/``: ``./a:b`` is no SCP-like address.
A single letter before the ``:`` is a Windows drive letter (``C:/Windows``) and raises
:exc:`~pyTooling.URI.URLError`, as does an address with a scheme - a URL is read by
:meth:`URL.Parse <pyTooling.URI.URL.Parse>`.


.. _STRUCT/Path/URL/Protocols:

Protocols
*********

.. #autoclass:: pyTooling.URI.Protocols
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Host:

Host
****

.. #autoclass:: pyTooling.URI.Host
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Element:

Element
*******

.. #autoclass:: pyTooling.URI.Element
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/Path:

Path
****

.. #autoclass:: pyTooling.URI.Path
   :show-inheritance:
   :members:
   :private-members:


.. _STRUCT/Path/URL/URL:

URL
***

.. #autoclass:: pyTooling.URI.URL
   :show-inheritance:
   :members:
   :private-members:
