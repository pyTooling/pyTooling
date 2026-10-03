.. _COMMON/StringEnum:

StringEnum
##########

.. #contents:: Table of Contents
   :depth: 1

:class:`~pyTooling.Common.StringEnum` is a :class:`~enum.StrEnum` that converts a string to the member of that
value, and says so when it can't.

Every enumeration whose members come from the outside - a command line, a configuration file, a REST reply -
needs the same three answers: what a missing value means, what a value of the wrong type is, and what a value no
member carries is. Written per enumeration, those answers drift; written once here, an enumeration adds its
members and inherits :meth:`~pyTooling.Common.StringEnum.Parse`.


.. _COMMON/StringEnum/Default:

The default is declared as an alias
***********************************

``DEFAULT`` is an **alias** of the member that stands for *"nothing was given"*. An alias, because that keeps it
out of the enumeration's own list: it isn't iterated, and it is not a second member to compare against - it *is*
the member it aliases.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.Common import StringEnum

   class GanttFormat(StringEnum):
     MatplotlibPNG = "matplotlib-png"
     MatplotlibSVG = "matplotlib-svg"

     DEFAULT = MatplotlibPNG

   GanttFormat.Parse("matplotlib-svg")    # GanttFormat.MatplotlibSVG
   GanttFormat.Parse(None)                # GanttFormat.MatplotlibPNG
   list(GanttFormat)                      # [MatplotlibPNG, MatplotlibSVG] - no third entry

An enumeration declaring no ``DEFAULT`` answers ``None`` instead, which is what a field that may legitimately be
absent wants - a workflow run has no conclusion while it is still running:

.. code-block:: Python

   class Conclusion(StringEnum):
     Success = "success"
     Failure = "failure"

   Conclusion.Parse(None)    # None
   Conclusion.Parse("")      # None


.. _COMMON/StringEnum/Parse:

What Parse rejects
******************

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Argument
     - Answer
   * - ``None`` or ``""``
     - ``DEFAULT``, or ``None`` if the enumeration declares none.
   * - A value a member carries
     - That member.
   * - A value no member carries
     - :exc:`ValueError`, naming the enumeration; the note lists the values it accepts.
   * - Anything that isn't a :class:`str`
     - :exc:`TypeError`; the note reports the type that was given.

.. rubric:: Example:
.. code-block:: Python

   GanttFormat.Parse("matplotlib-gif")
   # ValueError: 'matplotlib-gif' is not a valid GanttFormat.
   #   Allowed values: matplotlib-png, matplotlib-svg.

   GanttFormat.Parse(5)
   # TypeError: Parameter 'value' is not of type 'str'.
   #   Got type 'int'.


.. _COMMON/StringEnum/Domain:

An enumeration with its own exception
*************************************

:meth:`~pyTooling.Common.StringEnum.Parse` raises a :exc:`ValueError`, which is what an unknown value *is*. An
enumeration belonging to a domain that has its own exception overrides ``Parse``, catches that ``ValueError``
and chains it as the cause.

The difference is visible to a user: :func:`pyTooling.CLI.main` prints a
:exc:`~pyTooling.Exceptions.ToolingException` as a message, while an unhandled :exc:`ValueError` reaches
:meth:`~pyTooling.TerminalUI.TerminalApplication.PrintException`, which prints a traceback and invites the user
to open an issue. A value a service sent that pyTooling doesn't know is that service's problem, not a bug in
pyTooling, so it wants the first.

.. rubric:: Example:
.. code-block:: Python

   class Status(StringEnum):
     Queued =     "queued"
     InProgress = "in_progress"
     Completed =  "completed"

     @classmethod
     def Parse(cls, value: Nullable[str]) -> Nullable[Self]:
       try:
         return super().Parse(value)
       except ValueError as ex:
         error = GitHubError(f"'{value}' is not a GitHub status.")
         error.add_note(f"Known: {', '.join(member.value for member in cls)}.")
         raise error from ex

The :exc:`TypeError` is deliberately **not** caught: a value of the wrong type is a defect at the call site, not
a value the service chose, and it reads better as itself.

:class:`~pyTooling.CI.GitHub.Status`, :class:`~pyTooling.CI.GitHub.Conclusion` and
:class:`~pyTooling.CI.GitHub.Event` are written that way.


.. _COMMON/StringEnum/Member:

A member is its value
*********************

Deriving from :class:`~enum.StrEnum` rather than :class:`~enum.Enum` means a member *is* a string: it goes into a
message, an HTTP header or a filename without being unwrapped, and the whole enumeration joins into the list of
values an option accepts.

.. rubric:: Example:
.. code-block:: Python

   f"Drawn as {GanttFormat.MatplotlibPNG}."      # 'Drawn as matplotlib-png.'
   ", ".join(GanttFormat)                        # 'matplotlib-png, matplotlib-svg'
