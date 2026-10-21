.. _WARNING:

Warnings
########

.. grid:: 2

   .. grid-item::
      :columns: 6

      A warning can be raised similar to an exception, but it doesn't interrupt execution at the position where it
      was raised. The warning travels upwards the call-stack until it's handled by a
      :class:`~pyTooling.Warning.WarningCollector` similar to a ``try .. except`` statement. A warning nobody collects
      is dropped; a :class:`~pyTooling.Warning.CriticalWarning` or an exception nobody collects raises an
      :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` or :exc:`~pyTooling.Warning.UnhandledExceptionError`.

      A warning is raised by calling the class-method
      :meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>`. It expects an instance of
      :class:`~pyTooling.Warning.Warning`, :class:`~pyTooling.Warning.CriticalWarning` or :exc:`Exception`, and
      optionally a cause and notes (see :ref:`WARNING/Raising`).

      To handle a raised warning, a ``with``-statement is used to collect raised warnings. Usually, a list is handed
      over to a :class:`~pyTooling.Warning.WarningCollector` context.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyTooling.Warning import Warning, WarningCollector

         class ClassA:
           def methA_RaiseWarning(self) -> None:
             WarningCollector.Raise(Warning("Warning from ClassA.methA_RaiseWarning"))

      .. code-block:: Python

         from pyTooling.Warning import WarningCollector

         class Caller:
           def operation(self) -> None:
             warnings = []

             a = ClassA()
             with WarningCollector(warnings):
               a.methA_RaiseWarning()

             print("Warnings:")
             for warning in warnings:
               print(f"  {warning}")


.. _WARNING/Kinds:

Kinds of Warnings
*****************

:meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>` accepts three kinds of objects. What happens
to one depends on whether a :class:`~pyTooling.Warning.WarningCollector` is current, and on what its handler returns:

.. list-table::
   :header-rows: 1
   :widths: 22 26 26 26

   * - Raised object
     - No collector
     - Collector
     - Handler returns ``True``
   * - :class:`~pyTooling.Warning.Warning`
     - dropped silently
     - collected
     - collected, then :exc:`~pyTooling.Warning.EscalatedWarningError` is raised
   * - :class:`~pyTooling.Warning.CriticalWarning`
     - :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` is raised
     - collected
     - collected, then :exc:`~pyTooling.Warning.EscalatedWarningError` is raised
   * - :exc:`Exception`
     - :exc:`~pyTooling.Warning.UnhandledExceptionError` is raised
     - collected
     - collected, then :exc:`~pyTooling.Warning.EscalatedWarningError` is raised

Each of these exceptions carries the reported object as its cause (``__cause__``). If nothing is raised, execution
continues after the call of :meth:`~pyTooling.Warning.WarningCollector.Raise`.

:class:`~pyTooling.Warning.Warning` and :class:`~pyTooling.Warning.CriticalWarning` derive from :exc:`BaseException`,
not from :exc:`Exception`, so a broad ``except Exception`` doesn't catch one by accident (see
:ref:`TUTORIAL/ExceptionHierarchy/Warnings`).


.. _WARNING/Raising:

Raising a Warning
*****************

:meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>` hands the warning to the *current* collector
of the calling thread. Two optional parameters attach information to the warning:

``cause``
  The exception, which caused the warning. It becomes the warning's ``__cause__``, as with ``raise ... from cause``.
``notes``
  A note or an iterable of notes, added by :meth:`~BaseException.add_note`. They are accessible by
  :attr:`Warning.Notes <pyTooling.Warning.Warning.Notes>`.

.. code-block:: Python

   from pathlib           import Path
   from pyTooling.Warning import Warning, WarningCollector

   def ReadConfiguration(path: Path) -> str:
     try:
       return path.read_text()
     except OSError as ex:
       WarningCollector.Raise(
         Warning(f"Configuration file '{path}' can't be read."),
         ex,
         notes="The default configuration is used."
       )
       return ""

.. rubric:: Generators

A generator's body runs when the generator is resumed - by :func:`next` or a ``for`` loop - not when it's created. So a
warning raised inside a generator reaches the collector of the code **consuming** it:

.. code-block:: Python

   from typing            import Generator
   from pyTooling.Warning import Warning, WarningCollector

   def NonEmptyLines(text: str) -> Generator[str, None, None]:
     for line in text.splitlines():
       if line.strip() == "":
         WarningCollector.Raise(Warning("An empty line is skipped."))
         continue

       yield line

   lines = NonEmptyLines("a\n\nb")  # nothing runs yet

   with WarningCollector() as warnings:
     for line in lines:              # the warning is raised here
       print(line)


.. _WARNING/Collecting:

Collecting Warnings
*******************

A :class:`~pyTooling.Warning.WarningCollector` is a context manager. Entering it makes it the current collector of its
thread, leaving it makes the previous one current again. The warnings are appended to a list:

* to the list handed over as first parameter, so the caller owns it,
* or to an internal list, accessible by :attr:`~pyTooling.Warning.WarningCollector.Warnings`.

The collector supports :func:`len`, iteration and indexing as well:

.. code-block:: Python

   with WarningCollector() as warnings:
     ReadConfiguration(Path("missing.ini"))

   print(f"{len(warnings)} warning(s)")
   for warning in warnings:
     print(f"WARNING: {warning}")
     for note in warning.Notes:
       print(f"  {note}")

.. rubric:: Nesting

Collectors can be nested. Only the **innermost** collector receives a warning, the outer one doesn't see it. The inner
collector knows the outer one as its :attr:`~pyTooling.Warning.WarningCollector.Parent`. A warning is passed on
explicitly, e.g. by :meth:`~pyTooling.Warning.WarningCollector.AddWarning`:

.. code-block:: Python

   with WarningCollector() as outer:
     with WarningCollector() as inner:
       WarningCollector.Raise(Warning("Only the inner collector receives it."))

     # len(outer) == 0, len(inner) == 1
     for warning in inner:
       outer.AddWarning(warning)

.. rubric:: Threads

The current collector is stored per thread (:class:`threading.local`). A warning raised in another thread doesn't reach
the collector of the thread, which started it (see :ref:`WARNING/Threads`). Coroutines run by :func:`asyncio.run` run
in the calling thread, so they report to its collector.


.. _WARNING/Escalation:

Escalating Warnings
*******************

A collector can be given a handler: a callable, which is called with each collected warning. If it returns ``True``,
the warning is escalated: :meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>` raises an
:exc:`~pyTooling.Warning.EscalatedWarningError`, whose cause is the warning. The warning stays in the collector's list.
An exception raised by the handler itself propagates, too.

So the caller decides per warning, whether an operation continues - e.g. a handler ``lambda warning: strict`` turns
every warning into an error in a ``--strict`` mode. This handler escalates critical warnings only:

.. code-block:: Python

   from pyTooling.Warning import CriticalWarning, EscalatedWarningError, WarningCollector

   def EscalateCriticalWarnings(warning: BaseException) -> bool:
     return isinstance(warning, CriticalWarning)

   try:
     with WarningCollector(handler=EscalateCriticalWarnings) as warnings:
       Operation()
   except EscalatedWarningError as ex:
     print(f"ERROR: {ex.__cause__}")


.. _WARNING/Documenting:

Documenting Warnings
********************

A function reporting warnings says so in its doc-string:

* The description names the warning classes it reports and what happens without a collector, e.g. "Reports a
  :exc:`~pyTooling.Filesystem.PermissionWarning` to a :class:`~pyTooling.Warning.WarningCollector`; without a
  collector, it's dropped."
* The ``:raises:`` field lists :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` for a critical warning and
  :exc:`~pyTooling.Warning.UnhandledExceptionError` for a reported exception, because these are raised without a
  collector.
* :exc:`~pyTooling.Warning.EscalatedWarningError` isn't listed: any function reporting a warning can raise it, but only
  if its caller installed a handler escalating it - and that caller knows.
* Each function up the call-hierarchy documents it the same way, up to the first public function, method, property or
  ``__init__``. It stops at a function, which installs a collector itself. For a generator, the function consuming it
  documents the warnings.
* A warning class states in its doc-string, whether it's critical: in an ``.. important::`` box for a critical warning,
  in an ``.. attention::`` box for a non-critical one.

.. code-block:: Python

   def _removeDirectReferences(requirements: Iterable[str], extra: str, source: str) -> list[str]:
     """
     Remove direct references (``name @ URL``) from the requirements of an extra.

     Each removed requirement is reported as a :exc:`DirectReferenceWarning` to a
     :class:`~pyTooling.Warning.WarningCollector`.

     :param requirements:                   Requirements of the extra.
     :param extra:                          Name of the extra.
     :param source:                         Where the requirements were read from, e.g. the requirements file.
     :returns:                              The requirements, which aren't direct references.
     :raises UnhandledCriticalWarningError: If a requirement is a direct reference and no
                                            :class:`~pyTooling.Warning.WarningCollector` collects the warning.
     """


.. _WARNING/Applications:

Collecting in Applications
**************************

A library reports warnings, the application decides what to do with them: its top level installs a collector around an
operation and writes the collected warnings.

.. rubric:: setup.py

:func:`~pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` reports a critical
:exc:`~pyTooling.Packaging.DirectReferenceWarning` for each direct reference it leaves out of an extra (see
:ref:`PACKAGING/Descriptions/Python`). A :file:`setup.py` collects and prints them:

.. code-block:: Python

   from setuptools import setup

   from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub
   from pyTooling.Warning   import WarningCollector

   with WarningCollector() as warnings:
     setup(**DescribePythonPackageHostedOnGitHub(...))

   for warning in warnings:
     print(f"[setup.py] WARNING: {warning}")

.. rubric:: Command line application

A :class:`~pyTooling.TerminalUI.TerminalApplication` writes each warning with its notes, and exits after critical
warnings:

.. code-block:: Python

   from pyTooling.TerminalUI import TerminalApplication
   from pyTooling.Warning    import CriticalWarning, WarningCollector

   class Application(TerminalApplication):
     HEADLINE = "My Application"

     def Run(self) -> None:
       with WarningCollector() as warnings:
         Operation()

       for warning in warnings:
         if isinstance(warning, CriticalWarning):
           self.WriteCritical(f"{warning}")
         else:
           self.WriteWarning(f"{warning}")

         for note in getattr(warning, "__notes__", ()):
           self.WriteWarningNote(note)

       self.ExitOnPreviousCriticalWarnings()


.. _WARNING/Threads:

Threads
*******

A thread started by another one has no collector. A :class:`~pyTooling.Warning.SupervisedWarningCollector` is the
top-most collector of a thread: on leaving it, it hands the collected warnings and an exception leaving its
``with``-block to a :class:`~pyTooling.Warning.ThreadSupervisor`. The supervising thread reads the warnings from
:attr:`~pyTooling.Warning.ThreadSupervisor.Warnings`, and :meth:`~pyTooling.Warning.ThreadSupervisor.ReRaise` raises
the exceptions - one as :exc:`~pyTooling.Warning.SupervisedThreadError`, several as an :exc:`ExceptionGroup`.

.. code-block:: Python

   from threading         import Thread
   from pyTooling.Warning import SupervisedWarningCollector, ThreadSupervisor, Warning, WarningCollector

   def Worker(supervisor: ThreadSupervisor, index: int) -> None:
     with SupervisedWarningCollector(supervisor=supervisor):
       WarningCollector.Raise(Warning(f"Warning from worker {index}."))

   supervisor = ThreadSupervisor()
   threads = [Thread(target=Worker, args=(supervisor, index)) for index in range(3)]
   for thread in threads:
     thread.start()
   for thread in threads:
     thread.join()

   supervisor.ReRaise()
   for warning in supervisor.Warnings:
     print(warning)


.. _WARNING/Design:

Designing Warning Classes
*************************

* Derive a class per situation a caller might react to, and let it carry typed data - e.g.
  :class:`~pyTooling.Filesystem.PermissionWarning` carries the directory, which couldn't be read. Carry the object
  where it exists, not its name; the name is reachable from the object. The data are keyword-only parameters after the
  message, defaulting to ``None``, and read-only properties.
* Group the situations of one kind under a common base class a caller can collect at once - e.g.
  :class:`~pyTooling.Dependency.BrokenRequirementWarning` for an unparsable requirement and for an undeclared extra.
* Make a warning **critical**, if a caller who doesn't see it gets a wrong result, e.g.
  :exc:`~pyTooling.Packaging.DirectReferenceWarning`: a requirement left out of an extra changes the package. A caller
  must collect a critical warning.
* Keep a warning non-critical, if the result stays usable without it, e.g.
  :exc:`~pyTooling.MetaClasses.UnannotatedFieldWarning`.
* Turning a non-critical warning into a critical one is a breaking change: a caller without a collector gets an
  exception.
* State the criticality in the class' doc-string (see :ref:`WARNING/Documenting`).

.. admonition:: Warning or critical warning?
   :class: hint

   Ask what happens to a caller who never sees the warning:

   * Its result is still **complete and correct**, just less detailed or less polished: derive from
     :class:`~pyTooling.Warning.Warning`. A filesystem scan skipping an unreadable directory still returns usable
     statistics (:class:`~pyTooling.Filesystem.PermissionWarning`); a license that can't be resolved is still shown as
     published (:class:`~pyTooling.Dependency.UnknownLicenseWarning`); a requirement a release states under an extra it
     doesn't declare is a defect of that release's metadata, which no installer installs either
     (:class:`~pyTooling.Dependency.UndeclaredExtraMarkerWarning`).
   * Its result **silently lacks something** it relies on: derive from :class:`~pyTooling.Warning.CriticalWarning`.
     Data must never disappear without a report. In :mod:`pyTooling.Dependency`, a requirement line that can't be
     parsed, a requirement naming an extra the release doesn't declare, or a release whose details can't be read makes
     a dependency vanish - and a suddenly missing dependency is a serious issue. So
     :class:`~pyTooling.Dependency.BrokenRequirementWarning`, :class:`~pyTooling.Dependency.ReleaseDetailsWarning`
     and :class:`~pyTooling.Packaging.DirectReferenceWarning` are critical.

   A critical warning costs nothing while everything is fine: no warning is raised, and nothing has to be handled.
   Only a caller that can run into the finding has to collect it - and then knows about it.

.. seealso::

   :ref:`TUTORIAL/ExceptionHierarchy/Warnings`
      |rarr| How a warning hierarchy is designed, compared to an exception hierarchy.


.. _WARNING/Competitors:

Competing Solutions
*******************

Python's own warnings let execution continue too, but what happens to a warning is configured for the whole process.
:meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>` hands a warning to the innermost
:class:`~pyTooling.Warning.WarningCollector` of the current thread, which keeps it in a list, and its handler decides
per warning whether it is escalated - so the caller of an operation decides.

.. _WARNING/warnings:

warnings
========

Source: :mod:`warnings` of Python's standard library.

.. rubric:: Disadvantages

* What happens to a warning is decided by a global list of filters, matched by message, category, module and line -
  e.g. ``-W error`` turns every warning into an exception, for the whole process.
* :class:`~warnings.catch_warnings` changes the module's global state, which isn't safe with several threads or
  coroutines - unless the flag :data:`sys.flags.context_aware_warnings` is set, which Python 3.14 sets by default only
  in its free-threaded build.
* A warning that can't be ignored has no form: :class:`~pyTooling.Warning.CriticalWarning` raises
  :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` if no collector receives it.

.. rubric:: Standoff

* Both let execution continue after a warning, and both escalate one to an exception: the filter action ``error``,
  or a collector's handler returning ``True``, which raises :exc:`~pyTooling.Warning.EscalatedWarningError`.
* ``catch_warnings(record=True)`` collects the warnings of a block in a list, as a collector does.

.. rubric:: Advantages

* Every library reports through it, the interpreter's deprecations too, and ``-W`` or ``PYTHONWARNINGS`` configure
  it without changing code.
* The default action shows a warning once per place it is issued from.

.. _WARNING/logging:

logging
=======

Source: :mod:`logging` of Python's standard library.

.. rubric:: Disadvantages

* A record goes to the handlers of the logger hierarchy, configured for the application. Returning the warnings of
  one operation to its caller needs a handler written for it.
* Records are selected by their level, not by the class of an exception.

.. rubric:: Standoff

* :func:`logging.captureWarnings` sends the warnings of :mod:`warnings` to the logger ``py.warnings``.

.. rubric:: Advantages

* Destinations, formats and levels of the output are configured once for an application.
