.. _WARNING:

Warnings
########

.. grid:: 2

   .. grid-item::
      :columns: 6

      A warning can be raised similar to an exception, but it doesn't interrupt execution at the position where it was
      raised. The warning travels upwards the call-stack until it's handled by a :class:`~pyTooling.Warning.WarningCollector`
      similar to a `try .. except` statement. A warning nobody collects is dropped; a
      :class:`~pyTooling.Warning.CriticalWarning` or an exception nobody collects raises an
      :exc:`~pyTooling.Warning.UnhandledCriticalWarningError` or :exc:`~pyTooling.Warning.UnhandledExceptionError`.

      A warning is raised by Calling the class-method :meth:`WarningCollector.Raise <pyTooling.Warning.WarningCollector.Raise>`.
      This function expects a single parameter: an instance of :class:`Warning`.

      To handle a raised warning, a `with`-statement is used to collect raised warnings. Usually, a list is handed over
      to a :class:`~pyTooling.Warning.WarningCollector` context.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyTooling.Warning import WarningCollector

         class ClassA:
           def methA_RaiseException(self) -> None:
             WarningCollector.Raise(Warning("Warning from ClassA.methA_RaiseException"))

      .. code-block:: Python

         from pyTooling.Warning import WarningCollector

         class Caller:

           def operation(self) -> None:
             warnings = []

             a = ClassA()
             with WarningCollector(warnings) as warning:
               a.methA_RaiseException()

             print("Warnings:)
             for warning in warnings:
               print(f"  {warning}")


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
