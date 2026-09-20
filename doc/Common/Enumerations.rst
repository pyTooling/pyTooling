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

``Default`` is an **alias** of the member that stands for *"nothing was given"*. An alias, because that keeps it
out of the enumeration's own list: it isn't iterated, and it is not a second member to compare against - it *is*
the member it aliases.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.Common import StringEnum

   class GanttFormat(StringEnum):
     MatplotlibPNG = "matplotlib-png"
     MatplotlibSVG = "matplotlib-svg"

     Default = MatplotlibPNG

   GanttFormat.Parse("matplotlib-svg")    # GanttFormat.MatplotlibSVG
   GanttFormat.Parse(None)                # GanttFormat.MatplotlibPNG
   list(GanttFormat)                      # [MatplotlibPNG, MatplotlibSVG] - no third entry

An enumeration declaring no ``Default`` answers ``None`` instead, which is what a field that may legitimately be
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
     - ``Default``, or ``None`` if the enumeration declares none.
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
