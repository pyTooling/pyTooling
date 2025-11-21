.. _WARNING:

Warnings
########

.. grid:: 2

   .. grid-item::
      :columns: 6

      A warning can be raised similar to an exception, but it doesn't interrupt execution at the position where it was
      raised. The warning travels upwards the call-stack until it's handled by a :class:`~pyTooling.Warning.WarningCollector`
      similar to a `try .. except` statement. If a warning isn't handled within the call-stack, it raises an exception.

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
