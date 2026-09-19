.. _TUTORIAL/ExceptionHierarchy:

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

         class MyPackageError(ExceptionBase):
           """Base-exception of all exceptions raised by 'myPackage'."""

         class ParserError(MyPackageError):
           """The parser failed."""

         class WriterError(MyPackageError):
           """The writer failed."""

         class ModelError(MyPackageError):
           """The model failed."""

      A caller catching ``ParserError`` still doesn't know whether the file was missing, unreadable or malformed -
      and those need three different reactions.

   .. grid-item:: **By reaction - what a caller wants**
      :columns: 6

      .. code-block:: Python

         class MyPackageError(ExceptionBase):
           """Base-exception of all exceptions raised by 'myPackage'."""

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
     if configFile is None:
       raise ValueError("Parameter 'configFile' is None.")
     elif not isinstance(configFile, Path):
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

.. rubric:: A parameter of the wrong *type* stays a :exc:`TypeError`, a wrong *value* a :exc:`ValueError`

:exc:`TypeError` and :exc:`ValueError` are Python's vocabulary for *the caller passed nonsense*, and every Python
programmer already catches them. Wrapping those in a package base-exception hides a programming error among the
runtime failures. pyTooling raises them directly, with a note naming the type that arrived.

The two divide cleanly, and :pycode:`None` is where it matters most: a parameter that is :pycode:`None` has the
wrong **value**, not the wrong type, so it is a :exc:`ValueError`. Check it first and chain the type check onto it
with ``elif`` - :pycode:`isinstance(None, Path)` is :pycode:`False`, so a lone type check would report the wrong
one of the two.

.. rubric:: A failure from below is re-raised **from** its cause

:pycode:`raise ResourceError(...) from cause` keeps the :exc:`OSError` reachable as ``__cause__``. The caller sees your
vocabulary; the debugger still sees the real reason.

.. rubric:: A note that tells the user what to *do* is worth more than a class

*"Re-generate the file with 'myTool config --migrate'"* is the sentence that resolves the ticket. No exception
class conveys it.


.. _TUTORIAL/ExceptionHierarchy/TypedData:

Step 4: carry the data, not a sentence about it
***********************************************

A message is for a human. Everything a **caller** might want to react to belongs on the exception as a typed
attribute, because digging it back out of a formatted string is the one thing worse than not having it.

.. grid:: 2

   .. grid-item:: **The filename is in the prose**
      :columns: 6

      .. code-block:: Python

         raise ResourceError(
           f"Configuration file '{configFile}' couldn't be read."
         )

      A caller that wants to offer *"create it?"* has to parse the message - and the message is the one part of an
      exception that is allowed to be reworded.

   .. grid-item:: **The filename is a field**
      :columns: 6

      .. code-block:: Python

         @export
         class ResourceError(MyPackageError):
           _file: Path   #: The file that couldn't be reached.

           def __init__(self, message: str, file: Path) -> None:
             super().__init__(message)
             self._file = file

           @readonly
           def File(self) -> Path:
             return self._file

      :pycode:`except ResourceError as ex: ex.File.parent.mkdir()` - the handler works with a
      :class:`~pathlib.Path`, not with text.

The rule generalises: **an exception is a data object that happens to be raised.** Give it the object it is about -
the path, the version that didn't parse, the line number, the identifier that collided - as a read-only property,
and let the message be the sentence that explains it.

.. _TUTORIAL/ExceptionHierarchy/OneClass:

Step 5: one class per variant a caller reacts to
************************************************

The corollary of :ref:`TUTORIAL/ExceptionHierarchy/Shape`, and worth stating on its own because the alternative is
so tempting:

.. code-block:: Python

   # never this
   try:
     configuration = readConfiguration(configFile)
   except MyPackageError as ex:
     if "couldn't be read" in str(ex):
       ...
     elif "unsupported version" in str(ex):
       ...

**A message is not an API.** Reword it - fix a typo in it, translate it, add the file name to it - and every
handler that matched on it breaks silently. A separate class per variant is what makes the reaction dispatchable:

.. code-block:: Python

   try:
     configuration = readConfiguration(configFile)
   except ResourceError as ex:
     ...   # retry, or offer to create the file
   except FormatError as ex:
     ...   # report it, with ex.Line

That is also why the hierarchy stays **shallow but wide**: a new class costs nothing, while a class nobody writes
an ``except`` for costs a reader's attention. The test remains *"would a caller write a different clause for
this?"* - if two variants always get the same reaction, they are one class with two messages.

.. _TUTORIAL/ExceptionHierarchy/Documenting:

Step 6: document every exception a caller can see
*************************************************

Each function documents what it raises with ``:raises:`` - the ones it raises itself, and the ones a callee raises
that it deliberately lets through. That is what a caller reads *before* hitting the failure:

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


.. _TUTORIAL/ExceptionHierarchy/TopLevel:

Step 7: catch what is left at the top
*************************************

Every hierarchy needs one place where the exceptions that nobody handled stop, and that place is the program's
entry point. **A user should never see a raw traceback**: it is the program admitting it didn't anticipate its own
failure, and it buries the one line that would have helped.

A :class:`~pyTooling.TerminalUI.TerminalApplication` gives that place its shape. The program's **own** exceptions
come first and are reported as ordinary messages - somebody who passed a wrong option should read one sentence -
and only what nobody expected reaches the printers:

.. code-block:: Python

   def main() -> NoReturn:
     program = Application()

     try:
       program.Run()
     except MyPackageError as ex:                # our own hierarchy: a message, not a traceback
       program.WriteLineToStdErr(f"[ERROR] {ex}")
     except ExceptionBase as ex:
       program.PrintExceptionBase(ex)            # exit code 241
     except NotImplementedError as ex:
       program.PrintNotImplementedError(ex)      # exit code 240
     except MissingDependencyError as ex:
       program.PrintMissingDependencyError(ex)   # exit code 242 - an installation problem, not a bug
     except Exception as ex:
       program.PrintException(ex)                # exit code 241, the unexpected

     program.Exit()

The order is the argument. ``MyPackageError`` is caught **first** and printed as a message, because reaching it
means the program worked as designed - it found a broken configuration file and said so. Everything below it means
the program itself was surprised, and those clauses hand over to a printer.

.. important::

   The printers are why Step 3 and Step 4 pay off. :meth:`~pyTooling.TerminalUI.TerminalApplication.PrintException`
   renders the exception, **its notes, and its cause chain** - so the ``add_note`` that says *"Re-generate the file
   with 'myTool config --migrate'"* reaches the user, and the :exc:`OSError` behind a ``ResourceError`` is shown
   under it. Nothing at the call site has to walk ``__cause__`` or ``__notes__`` by hand.

   Set :attr:`~pyTooling.TerminalUI.TerminalBaseApplication.ISSUE_TRACKER_URL` and each report ends by inviting the
   user to file a bug, with the URL - except the missing-dependency report, which names the package to install
   instead, because nothing is wrong with the program.

.. seealso::

   :ref:`TUTORIAL/TerminalApplication/Step5`
      |rarr| The same handler built step by step, with the exit codes and what each printer does.


.. _TUTORIAL/ExceptionHierarchy/Warnings:

Warnings have a hierarchy too
*****************************

Everything above is about a failure that **stops** the operation. A *warning* is the other case - the operation
carried on, but something is worth saying - and :mod:`pyTooling.Warning` gives it a hierarchy of its own, built on
the same reasoning.

The design decision worth knowing is where it is rooted:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Class
     - Derives from
   * - :class:`~pyTooling.Warning.Warning`
     - :exc:`BaseException`
   * - :class:`~pyTooling.Warning.CriticalWarning`
     - :exc:`BaseException`
   * - :exc:`~pyTooling.Warning.EscalatedWarningError`
     - :exc:`~pyTooling.Exceptions.ExceptionBase`
   * - :exc:`~pyTooling.Warning.UnhandledCriticalWarningError`
     - :exc:`~pyTooling.Exceptions.ExceptionBase`

**A warning derives from** :exc:`BaseException`\ **, not from** :exc:`Exception`. That is deliberate and it is the
mirror image of Step 1: a broad ``except Exception`` around a call is supposed to catch *failures*, and a warning
travelling past it must not be swallowed by a handler that never meant to see one. The *errors* in that module -
raised when a warning is escalated, or when a critical one goes unhandled - are ordinary exceptions and derive from
:exc:`~pyTooling.Exceptions.ExceptionBase` like everything else.

The parallels to draw when designing your own:

* a warning class per **variant a collector might react to**, for the same reason as
  :ref:`TUTORIAL/ExceptionHierarchy/OneClass`;
* typed data on the warning, for the same reason as :ref:`TUTORIAL/ExceptionHierarchy/TypedData` - a
  :class:`~pyTooling.Warning.WarningCollector` gathers them and something later has to sort them;
* a **critical** warning is the one a caller may not ignore: if nothing handles it, it becomes an error.

.. seealso::

   :ref:`WARNING`
      |rarr| :class:`~pyTooling.Warning.WarningCollector`, the context manager that collects warnings across a call
      hierarchy, and what escalation does.


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
