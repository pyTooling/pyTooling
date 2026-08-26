.. _TUTORIAL/ExceptionHierarchy:
.. _ExceptionHierarchies:

Exception Hierarchies
#####################

A package that raises :exc:`ValueError` and :exc:`TypeError` gives its callers nothing to aim at. ``except
ValueError`` around a call into that package catches the package's own complaint *and* a :exc:`ValueError` from a
:func:`int` conversion three frames deeper - and the caller cannot tell them apart.

An exception hierarchy is what makes ``except`` selective again. This tutorial builds one.

.. seealso::

   :ref:`EXCEPTION`
      |rarr| The exceptions pyTooling itself offers, including :exc:`~pyTooling.Exceptions.ToolingException`.


.. _TUTORIAL/ExceptionHierarchy/BaseException:

Step 1: one base exception per package
**************************************

Give the package a single base exception and derive **everything** the package raises from it. That one class is
the package's promise to its callers: *catch this, and you have caught me*.

.. code-block:: Python

   from pyTooling.Exceptions import ExceptionBase

   class MyPackageError(ExceptionBase):
     """Base-exception of all exceptions raised by 'myPackage'."""

Deriving from :exc:`~pyTooling.Exceptions.ExceptionBase` rather than from :exc:`Exception` buys two small
things: the message is kept as ``message`` rather than only in ``args``, and
:attr:`~pyTooling.Exceptions.ExceptionBase.HasNotes` and :attr:`~pyTooling.Exceptions.ExceptionBase.Notes` read
the attached notes without a handler touching the ``__notes__`` dunder.

A caller now has exactly one thing to write:

.. code-block:: Python

   try:
     result = myPackage.doSomething(path)
   except MyPackageError as ex:
     print(f"myPackage failed: {ex}")

.. hint::

   **Name it ``***Error``, not ``***Exception``.** Of the 50 builtin exception classes whose name ends in either,
   every one is ``Error`` except :exc:`BaseException` and :exc:`Exception` themselves. pyTooling follows that:
   :exc:`~pyTooling.Tracing.TracingError`, :exc:`~pyTooling.Packaging.PackagingError`,
   :exc:`~pyTooling.Documentation.DocumentationError`.

   The one deliberate exception in pyTooling is :exc:`~pyTooling.Exceptions.ToolingException`, which is the root of
   the whole library rather than one package's base - and renaming it now would break every downstream ``except``.


.. _TUTORIAL/ExceptionHierarchy/Shape:

Step 2: derive by *what went wrong*, not by *where*
***************************************************

The tempting hierarchy mirrors the module layout - ``ParserError``, ``WriterError``, ``ConfigError``. It is the
wrong axis, because a caller doesn't handle failures by the module they came out of. It handles them by **what it
can do about them**.

Ask, for each candidate class: *would a caller write a different ``except`` clause for this?* If the answer is no,
it doesn't need a class of its own - a message and a note say it better.

.. grid:: 2

   .. grid-item:: **By location - rarely useful**
      :columns: 6

      .. code-block:: Python

         class MyPackageError(ExceptionBase): ...

         class ParserError(MyPackageError): ...
         class WriterError(MyPackageError): ...
         class ModelError(MyPackageError): ...

      A caller catching ``ParserError`` still doesn't know whether the file was missing, unreadable or malformed -
      and those need three different reactions.

   .. grid-item:: **By reaction - what a caller wants**
      :columns: 6

      .. code-block:: Python

         class MyPackageError(ExceptionBase): ...

         class ResourceError(MyPackageError):
           """A file or a stream couldn't be reached."""

         class FormatError(MyPackageError):
           """The input was reached, but doesn't parse."""

         class UsageError(MyPackageError):
           """The caller asked for something impossible."""

      Retry the first, report the second, fix the third. Three clauses, three actions.

Keep it **shallow**. Two levels - the package base and a handful of kinds - cover most packages. A third level
earns its place only when a caller genuinely distinguishes it; until then it is a class nobody names in an
``except``.


.. _TUTORIAL/ExceptionHierarchy/Detail:

Step 3: put the detail in notes, not in classes
***********************************************

Everything a caller wants to *read* but doesn't want to *dispatch on* belongs in the message and in
:meth:`~BaseException.add_note`, which Python 3.11 added for exactly this. It keeps the hierarchy small while the
report stays specific.

.. code-block:: Python

   def readConfiguration(configFile: Path) -> Configuration:
     if not isinstance(configFile, Path):
       ex = TypeError("Parameter 'configFile' is not of type 'Path'.")
       ex.add_note(f"Got type '{getFullyQualifiedName(configFile)}'.")
       raise ex

     try:
       content = configFile.read_text(encoding="utf-8")
     except OSError as cause:
       raise ResourceError(f"Configuration file '{configFile}' couldn't be read.") from cause

     if (version := content.partition("\n")[0]) != EXPECTED_VERSION:
       ex = FormatError(f"Configuration file '{configFile}' has an unsupported version.")
       ex.add_note(f"Expected '{EXPECTED_VERSION}', got '{version}'.")
       ex.add_note("Re-generate the file with 'myTool config --migrate'.")
       raise ex

     return parse(content)

Three rules are at work there, and they are worth stating separately:

.. rubric:: A parameter of the wrong *type* stays a :exc:`TypeError`

:exc:`TypeError` and :exc:`ValueError` are Python's vocabulary for *the caller passed nonsense*, and every Python
programmer already catches them. Wrapping those in a package base-exception hides a programming error among the
runtime failures. pyTooling raises them directly, with a note naming the type that arrived.

.. rubric:: A failure from below is re-raised **from** its cause

``raise ResourceError(...) from cause`` keeps the :exc:`OSError` reachable as ``__cause__``. The caller sees your
vocabulary; the debugger still sees the real reason.

.. rubric:: A note that tells the user what to *do* is worth more than a class

*"Re-generate the file with 'myTool config --migrate'"* is the sentence that resolves the ticket. No exception
class conveys it.


.. _TUTORIAL/ExceptionHierarchy/Documenting:

Step 4: document every exception that escapes
*********************************************

Each function documents what it raises with ``:raises:``, including exceptions raised by something it calls and
lets through - that is what a caller reads *before* hitting the failure:

.. code-block:: Python

   def readConfiguration(configFile: Path) -> Configuration:
     """
     Read and parse a configuration file.

     :param configFile:     Path of the file to read.
     :returns:              The parsed configuration.
     :raises TypeError:     If parameter 'configFile' is not of type :class:`~pathlib.Path`.
     :raises ResourceError: If the file couldn't be read.
     :raises FormatError:   If the file's version isn't supported - re-generate it with ``myTool config --migrate``.
     """

.. hint::

   Where a note gives **advice**, repeat that advice in the ``:raises:`` description. The note is read after the
   failure; the field list is read before it, which is the cheaper of the two moments.


.. _TUTORIAL/ExceptionHierarchy/Example:

pyTooling's own hierarchy
*************************

pyTooling applies exactly this shape one level up: :exc:`~pyTooling.Exceptions.ToolingException` is the root of the
library, and each package derives its own base from it - :exc:`~pyTooling.Tracing.TracingError`,
:exc:`~pyTooling.Packaging.PackagingError`, :exc:`~pyTooling.Documentation.DocumentationError`,
:exc:`~pyTooling.CLIAbstraction.CLIAbstractionError`. So a downstream project can catch a whole library, one
package of it, or one kind of failure, depending on how much it wants to know.

.. note::

   pyTooling has **two** roots, and the distinction matters when writing your own package:
   :exc:`~pyTooling.Exceptions.ExceptionBase` is offered *to you* as the base of your hierarchy, while
   :exc:`~pyTooling.Exceptions.ToolingException` is the root of pyTooling's own. Both derive from :exc:`Exception`
   directly, so catching one does not catch the other.

:mod:`pyTooling.Exceptions` also predefines the failures that recur in every project, so a package doesn't have to
invent them:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Exception
     - Raised when
   * - :exc:`~pyTooling.Exceptions.EnvironmentVariableError`
     - an expected environment variable isn't set
   * - :exc:`~pyTooling.Exceptions.ConfigurationError`
     - a configuration value is wrong
   * - :exc:`~pyTooling.Exceptions.NotConfiguredError`
     - something has to be configured before it is used
   * - :exc:`~pyTooling.Exceptions.PlatformNotSupportedError`
     - the code doesn't run on this operating system
   * - :exc:`~pyTooling.Exceptions.MissingDependencyError`
     - an optional dependency isn't installed
   * - :exc:`~pyTooling.Exceptions.OverloadResolutionError`
     - no overload matches the given arguments

The first four derive from :exc:`~pyTooling.Exceptions.ExceptionBase`.
:exc:`~pyTooling.Exceptions.MissingDependencyError` deliberately does not - it derives from :exc:`ImportError`,
because that is what a caller already writes ``except`` for when an optional feature is unavailable. **Deriving from
the builtin a caller already catches is worth more than a tidy hierarchy**, whenever the two disagree.
