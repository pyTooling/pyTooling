.. _TERM:

Terminal
########

.. grid:: 2

   .. grid-item::
      :columns: 6

      A set of helpers to implement a text user interface (TUI) in a terminal.

      The package is built on the idea that a command line program emits **one line of text per message**, and that
      every message has a :ref:`severity <TERM/Severity>`: a normal message, a warning, an error, a debug message, ...
      The severity decides three things at once: whether the message is visible at the configured verbosity, how it is
      formatted and colored, and whether it is written to ``STDOUT`` or ``STDERR``.

      An application derives from :ref:`TerminalApplication <TERM/TerminalApplication>` and writes its messages with the
      matching ``Write*`` method. Coloring is provided by
      `colorama <https://GitHub.com/tartley/colorama>`__, so an application doesn't handle escape sequences itself.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         from pyTooling.TerminalUI import TerminalApplication

         class Application(TerminalApplication):
           HeadLine = "My Application"

           def Run(self) -> None:
             self._PrintHeadline()
             self.WriteQuiet("Always visible.")
             self.WriteNormal("A normal message.")
             self.WriteVerbose("Only with --verbose.")
             self.WriteDebug("Only with --debug.")
             self.WriteWarning("A warning.")
             self.ExitOnPreviousWarnings()

         def main() -> NoReturn:
           program = Application()
           program.Configure(verbose=("-v" in argv or "--verbose" in argv))

           try:
             program.Run()
           except Exception as ex:
             program.PrintException(ex)

         if __name__ == "__main__":
           main()


.. _TERM/Classes:

Classes at a Glance
*******************

+---------------------------------------------------------------+---------------------------------------------------------------------------+
| **Class**                                                     | **Purpose**                                                               |
+===============================================================+===========================================================================+
| :ref:`TerminalBaseApplication <TERM/TerminalBaseApplication>` | Colors, terminal size, low-level writing, exiting and exception printing. |
+---------------------------------------------------------------+---------------------------------------------------------------------------+
| :ref:`TerminalApplication <TERM/TerminalApplication>`         | Line-based messages with severities, verbosity handling and counters.     |
+---------------------------------------------------------------+---------------------------------------------------------------------------+
| :ref:`Severity <TERM/Severity>`                               | The severity levels a message can have.                                   |
+---------------------------------------------------------------+---------------------------------------------------------------------------+
| :ref:`Mode <TERM/Mode>`                                       | Which stream (``STDOUT``/``STDERR``) a severity is written to.            |
+---------------------------------------------------------------+---------------------------------------------------------------------------+
| :ref:`Line <TERM/Line>`                                       | A single message: text, severity, indentation and timestamp.              |
+---------------------------------------------------------------+---------------------------------------------------------------------------+
| :ref:`ILineTerminal <TERM/ILineTerminal>`                     | Mixin giving any class the ``Write*`` methods of an attached terminal.    |
+---------------------------------------------------------------+---------------------------------------------------------------------------+


.. _TERM/Terminal:
.. _TERM/TerminalBaseApplication:

TerminalBaseApplication
***********************

:class:`~pyTooling.TerminalUI.TerminalBaseApplication` is the base-class of every terminal application. It handles
color support, the terminal's size, writing to the standard streams, and leaving the program.

.. admonition:: Singleton

   The class is created with ``ExtendedType(singleton=True)``, so a class is instantiated **once**: every further
   ``Application()`` returns the same object. That is what allows helper classes to reach the terminal without it being
   passed around, but it also means state - written lines, message counters - survives. In unit tests, give every
   testcase its own derived class instead of instantiating the same class twice.


.. _TERM/Colors:

Colored Output
==============

If ``STDOUT`` is a terminal, colorama is initialized in the constructor, otherwise colors are switched off - so a
redirected output doesn't contain escape sequences. The color palette is offered as a dictionary in the class variable
:attr:`~pyTooling.TerminalUI.TerminalBaseApplication.Foreground`, which is used as the keyword arguments of a
:meth:`str.format` call:

.. code-block:: Python

   self.WriteLineToStdErr("{RED}[ERROR] {message}{NOCOLOR}".format(message="It failed.", **self.Foreground))

Besides plain colors (``RED``, ``DARK_RED``, ``GREEN``, ``YELLOW``, ``MAGENTA``, ``BLUE``, ``CYAN``, ``GRAY``,
``WHITE``, ``NOCOLOR``, ...), the palette contains the semantic entries ``HEADLINE``, ``WARNING`` and ``ERROR``. If
colorama isn't installed, every entry is an empty string, so the same code emits uncolored text.

.. hint::

   colorama is an optional dependency: install ``pyTooling[terminal]``, otherwise importing the package raises an
   exception naming that extra.


.. _TERM/Size:

Terminal Size
=============

:attr:`~pyTooling.TerminalUI.TerminalBaseApplication.Width` and
:attr:`~pyTooling.TerminalUI.TerminalBaseApplication.Height` return the terminal's size in characters, as determined
once in the constructor by :meth:`~pyTooling.TerminalUI.TerminalBaseApplication.GetTerminalSize`. That static method
supports native Windows (``kernel32.dll:GetConsoleScreenBufferInfo``) as well as Linux, macOS, FreeBSD, MinGW32/64,
UCRT64, Clang64 and Cygwin (``ioctl(TIOCGWINSZ)``, falling back to the environment variables ``COLUMNS`` and ``LINES``).
If the size can't be determined, ``(80, 25)`` is assumed; on an unsupported platform, a
:exc:`~pyTooling.Exceptions.PlatformNotSupportedError` is raised.


.. _TERM/LowLevelWriting:

Low-Level Writing
=================

Four methods write to the standard streams without any formatting, severity handling or verbosity check:
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.WriteToStdOut`,
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.WriteLineToStdOut`,
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.WriteToStdErr` and
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.WriteLineToStdErr`. They are the escape hatch for output that must
appear regardless of the configured log level - an error message from the topmost exception handler, for example.


.. _TERM/Exiting:

Exiting and Exit Codes
======================

:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.Exit` uninitializes the colors and terminates the program;
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.FatalExit` does the same, but substitutes
:attr:`~pyTooling.TerminalUI.TerminalBaseApplication.FATAL_EXIT_CODE` when the given exit code is ``0``. The reserved
exit codes are class variables, so an application can override them:

+-------------------------------------------+-----------+-------------------------------------------------------------+
| **Class variable**                        | **Value** | **Used when**                                               |
+===========================================+===========+=============================================================+
| ``NOT_IMPLEMENTED_EXCEPTION_EXIT_CODE``   | 240       | An unimplemented function or abstract method was called.    |
+-------------------------------------------+-----------+-------------------------------------------------------------+
| ``UNHANDLED_EXCEPTION_EXIT_CODE``         | 241       | An exception reached the topmost exception handler.         |
+-------------------------------------------+-----------+-------------------------------------------------------------+
| ``MISSING_DEPENDENCY_EXIT_CODE``          | 242       | An optional dependency of the application is not installed. |
+-------------------------------------------+-----------+-------------------------------------------------------------+
| ``FATAL_EXIT_CODE``                       | 255       | A fatal message was written, or ``FatalExit()`` was called. |
+-------------------------------------------+-----------+-------------------------------------------------------------+


.. _TERM/ExceptionPrinting:

Printing Exceptions
===================

Three methods render an exception for a human reader instead of a Python traceback dump. Each of them prints the
exception, its notes (:meth:`BaseException.add_note`), the causing exception if there is one, the traceback, and finally
exits:

* :meth:`~pyTooling.TerminalUI.TerminalBaseApplication.PrintException` - for any :exc:`Exception`.
* :meth:`~pyTooling.TerminalUI.TerminalBaseApplication.PrintExceptionBase` - for a
  :exc:`~pyTooling.Exceptions.ExceptionBase`, a *known* exception that was nevertheless not handled.
* :meth:`~pyTooling.TerminalUI.TerminalBaseApplication.PrintNotImplementedError` - for a :exc:`NotImplementedError`.

.. code-block:: Python

   program = Application()
   try:
     program.Run()
   except ExceptionBase as ex:
     program.PrintExceptionBase(ex)
   except NotImplementedError as ex:
     program.PrintNotImplementedError(ex)
   except Exception as ex:
     program.PrintException(ex)


.. _TERM/IssueTracker:

Reporting Bugs: ISSUE_TRACKER_URL
=================================

If the class variable :attr:`~pyTooling.TerminalUI.TerminalBaseApplication.ISSUE_TRACKER_URL` is set, every exception
printed by the methods above ends with an invitation to report the bug, followed by that URL. It is ``None`` by default,
in which case the invitation is omitted. It is independent of the ``Issue tracker:`` line of
:ref:`the version information <TERM/ProgramInformation>`, which is read from the application's dunder module.

An application connects the class variable to its own dunder variable. pyTooling can't find that variable on its own:
which module carries ``__issue_tracker_url__`` is up to the application - ``<package>/__init__.py`` for a simple
package, ``<namespace>/<package>/__init__.py`` for a namespace package.

.. code-block:: Python

   from pyTooling.TerminalUI import TerminalApplication

   from myPackage import __issue_tracker_url__

   class Application(TerminalApplication):
     ISSUE_TRACKER_URL = __issue_tracker_url__


.. _TERM/LineTerminal:
.. _TERM/TerminalApplication:

TerminalApplication
*******************

:class:`~pyTooling.TerminalUI.TerminalApplication` adds line-based messaging on top of the base-class: a family of
``Write*`` methods, a verbosity setting deciding which of them are visible, message counters, and a recorded history of
everything written.

Each ``Write*`` method takes the message and two optional keyword arguments - ``indent`` and ``appendLinebreak`` - wraps
them in a :ref:`Line <TERM/Line>` and hands it to
:meth:`~pyTooling.TerminalUI.TerminalApplication.WriteLine`. The return value tells whether the message was actually
written, or dropped because its severity is below the current log level.

+-----------------------+---------------------------+----------------------------------------------------------+
| **Method**            | **Severity**              | **Notes**                                                |
+=======================+===========================+==========================================================+
| ``WriteFatal``        | ``Severity.Fatal``        | Exits the application, unless ``immediateExit=False``.   |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteError``        | ``Severity.Error``        | Increments the error counter.                            |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteQuiet``        | ``Severity.Quiet``        | Visible even in quiet mode.                              |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteCritical``     | ``Severity.Critical``     | Increments the critical warning counter.                 |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteCriticalNote`` | ``Severity.CriticalNote`` | Follow-up line of a critical warning, rendered indented. |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteWarning``      | ``Severity.Warning``      | Increments the warning counter.                          |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteWarningNote``  | ``Severity.WarningNote``  | Follow-up line of a warning, rendered indented.          |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteInfo``         | ``Severity.Info``         | Visible at the default log level, like a normal message. |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteNormal``       | ``Severity.Normal``       | The default severity of a message.                       |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteDryRun``       | ``Severity.DryRun``       | For actions skipped in a dry-run.                        |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteVerbose``      | ``Severity.Verbose``      | Visible from ``verbose`` upwards.                        |
+-----------------------+---------------------------+----------------------------------------------------------+
| ``WriteDebug``        | ``Severity.Debug``        | Visible only in ``debug`` mode.                          |
+-----------------------+---------------------------+----------------------------------------------------------+

:meth:`~pyTooling.TerminalUI.TerminalApplication.TryWriteLine` answers whether a line *would* be written, without
writing it - useful before assembling an expensive message.

A *note* is a follow-up line belonging to the message above it, rendered with a leading ``>`` at the severity's
indentation. Only warnings and critical warnings have one, although :class:`~pyTooling.TerminalUI.Severity` also
defines ``ExceptionNote``:

.. code-block:: Python

   self.WriteWarning(f"File '{file}' was ignored.")
   self.WriteWarningNote(f"Only '.vhdl' and '.vhd' are read.")


.. _TERM/Verbosity:

Verbosity: Configure
====================

:meth:`~pyTooling.TerminalUI.TerminalApplication.Configure` translates the usual command line switches into a log level.
It takes keyword arguments only, and ``debug`` implies ``verbose``:

.. code-block:: Python

   from sys import argv

   program = Application()
   program.Configure(
     verbose=("-v" in argv or "--verbose" in argv),
     debug=(  "-d" in argv or "--debug"   in argv),
     quiet=(  "-q" in argv or "--quiet"   in argv)
   )

The resulting log level - readable and writable as
:attr:`~pyTooling.TerminalUI.TerminalApplication.LogLevel` - is the minimum severity a message needs to be written:

+-------------------+----------------------+--------------------------------------------------------------------+
| **Configuration** | **Log level**        | **Lowest severity still visible**                                  |
+===================+======================+====================================================================+
| *(default)*       | ``Severity.Normal``  | ``WriteNormal`` and above; verbose, dry-run and debug are dropped. |
+-------------------+----------------------+--------------------------------------------------------------------+
| ``verbose=True``  | ``Severity.Verbose`` | additionally ``WriteDryRun`` and ``WriteVerbose``.                 |
+-------------------+----------------------+--------------------------------------------------------------------+
| ``debug=True``    | ``Severity.Debug``   | everything, including ``WriteDebug``.                              |
+-------------------+----------------------+--------------------------------------------------------------------+
| ``silent=True``   | ``Severity.Silent``  | only warnings, errors and fatal messages.                          |
+-------------------+----------------------+--------------------------------------------------------------------+
| ``quiet=True``    | ``Severity.Quiet``   | only ``WriteQuiet``, errors and fatal messages.                    |
+-------------------+----------------------+--------------------------------------------------------------------+

The chosen mode is also readable as :attr:`~pyTooling.TerminalUI.TerminalApplication.Verbose`,
:attr:`~pyTooling.TerminalUI.TerminalApplication.Debug`,
:attr:`~pyTooling.TerminalUI.TerminalApplication.Silent` and
:attr:`~pyTooling.TerminalUI.TerminalApplication.Quiet`, so an application can skip work whose result would never be
printed.


.. _TERM/Counters:

Counters and Exit Conditions
============================

Writing a warning, a critical warning or an error increments the matching counter:
:attr:`~pyTooling.TerminalUI.TerminalApplication.WarningCount`,
:attr:`~pyTooling.TerminalUI.TerminalApplication.CriticalWarningCount` and
:attr:`~pyTooling.TerminalUI.TerminalApplication.ErrorCount`. Counting happens even when the message itself is
suppressed by the log level.

Three methods end a processing step by those counters, each writing a fatal message and exiting if anything was
counted:

* :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousErrors` - errors only.
* :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousCriticalWarnings` - critical warnings, errors
  included by default.
* :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousWarnings` - warnings, critical warnings and errors
  included by default.

.. code-block:: Python

   def Run(self) -> None:
     self.ParseInputFiles()
     self.ExitOnPreviousErrors()    # don't start processing with unreadable inputs

Every written line is also kept in :attr:`~pyTooling.TerminalUI.TerminalApplication.Lines` as a
:ref:`Line <TERM/Line>` object, which is what makes a terminal application testable: the test configures the
application, runs it and inspects the recorded messages and their severities.


.. _TERM/Severity:

Severity Levels
***************

:class:`~pyTooling.TerminalUI.Severity` is an enumeration whose values are ordered - the comparison operators are
implemented, and comparing against anything but another ``Severity`` raises a :exc:`TypeError`. A message is written
when its severity is greater than or equal to the current log level, so the numeric values are the actual policy:

+--------------------+-----------+----------------------------------------------------------------+
| **Severity**       | **Value** | **Meaning**                                                    |
+====================+===========+================================================================+
| ``Exception``      | 120       | An unhandled exception.                                        |
+--------------------+-----------+----------------------------------------------------------------+
| ``ExceptionCause`` | 115       | The exception that caused it.                                  |
+--------------------+-----------+----------------------------------------------------------------+
| ``ExceptionNote``  | 110       | A note attached to an exception.                               |
+--------------------+-----------+----------------------------------------------------------------+
| ``Fatal``          | 100       | The application cannot continue.                               |
+--------------------+-----------+----------------------------------------------------------------+
| ``Error``          | 80        | An error, counted and reported.                                |
+--------------------+-----------+----------------------------------------------------------------+
| ``Quiet``          | 70        | Always visible, even in quiet mode.                            |
+--------------------+-----------+----------------------------------------------------------------+
| ``Critical``       | 60        | A critical warning.                                            |
+--------------------+-----------+----------------------------------------------------------------+
| ``CriticalNote``   | 55        | A follow-up line of a critical warning.                        |
+--------------------+-----------+----------------------------------------------------------------+
| ``Warning``        | 50        | A warning.                                                     |
+--------------------+-----------+----------------------------------------------------------------+
| ``WarningNote``    | 45        | A follow-up line of a warning.                                 |
+--------------------+-----------+----------------------------------------------------------------+
| ``Silent``         | 40        | The threshold of silent mode - not used as a message severity. |
+--------------------+-----------+----------------------------------------------------------------+
| ``Info``           | 20        | An informative message.                                        |
+--------------------+-----------+----------------------------------------------------------------+
| ``Normal``         | 10        | The default message severity.                                  |
+--------------------+-----------+----------------------------------------------------------------+
| ``DryRun``         | 8         | An action that was skipped in a dry-run.                       |
+--------------------+-----------+----------------------------------------------------------------+
| ``Verbose``        | 5         | A verbose message.                                             |
+--------------------+-----------+----------------------------------------------------------------+
| ``Debug``          | 2         | A debug message.                                               |
+--------------------+-----------+----------------------------------------------------------------+
| ``All``            | 0         | The threshold letting every message pass.                      |
+--------------------+-----------+----------------------------------------------------------------+

``Quiet`` sitting between ``Error`` and ``Critical`` is what makes a "quiet" program still print its actual result:
in quiet mode the log level is ``Quiet``, so warnings disappear while a ``WriteQuiet`` message survives.


.. _TERM/Mode:

Message Routing (Mode)
**********************

:class:`~pyTooling.TerminalUI.Mode` decides which stream a severity is written to. It's given to the constructor of
:class:`~pyTooling.TerminalUI.TerminalApplication` and expanded into a routing table, one entry per severity:

+-----------------------------------+---------------------------------------------------------------------------------+
| **Mode**                          | **Routing**                                                                     |
+===================================+=================================================================================+
| ``AllLinearToStdOut`` *(default)* | Everything to ``STDOUT``, so the messages keep their order in a redirected log. |
+-----------------------------------+---------------------------------------------------------------------------------+
| ``TextToStdOut_ErrorsToStdErr``   | Warnings and above to ``STDERR`` - except ``Quiet``, which stays on ``STDOUT``. |
+-----------------------------------+---------------------------------------------------------------------------------+
| ``DataToStdOut_OtherToStdErr``    | Everything to ``STDERR``, leaving ``STDOUT`` free for the program's data.       |
+-----------------------------------+---------------------------------------------------------------------------------+

.. code-block:: Python

   # a program whose result is piped into another program
   app = Application(Mode.DataToStdOut_OtherToStdErr)


.. _TERM/Line:

Line
****

A :class:`~pyTooling.TerminalUI.Line` is a single message: its text
(:attr:`~pyTooling.TerminalUI.Line.Message`), its :attr:`~pyTooling.TerminalUI.Line.Severity`, its
:attr:`~pyTooling.TerminalUI.Line.Indent` level, whether a linebreak is appended
(:attr:`~pyTooling.TerminalUI.Line.AppendLinebreak`), and the timestamp of its creation. Applications rarely construct
one - the ``Write*`` methods do it - but every recorded message in
:attr:`~pyTooling.TerminalUI.TerminalApplication.Lines` is such an object.

:meth:`~pyTooling.TerminalUI.Line.IndentBy` raises the indentation level of an existing line, and ``str(line)`` renders
the message with the severity's prefix (``ERROR: ...``, ``WARNING: ...``, ``DEBUG: ...``) but without colors - the
colored format used when printing lives in ``TerminalApplication`` instead.

.. note::

   The indentation is recorded (``indent`` per message plus the application's
   :attr:`~pyTooling.TerminalUI.TerminalApplication.BaseIndent`), but it is not yet applied when a line is printed.


.. _TERM/ILineTerminal:

ILineTerminal
*************

Not every class writing messages is the application itself. :class:`~pyTooling.TerminalUI.ILineTerminal` is a
:ref:`mixin <META/Mixin>` that gives a class the same ``Write*`` methods, forwarding them to an attached terminal - or
silently doing nothing if none is attached. Every method additionally takes ``condition``, so a message can be made
dependent on a check without an ``if`` statement:

.. code-block:: Python

   from pyTooling.TerminalUI import ILineTerminal

   class Parser(ILineTerminal):
     def __init__(self, terminal) -> None:
       super().__init__(terminal)

     def Parse(self, file) -> None:
       self.WriteVerbose(f"Parsing '{file}'...")
       self.WriteWarning(f"File '{file}' is empty.", condition=file.stat().st_size == 0)


.. _TERM/ProgramInformation:

Headline, Help and Version Information
**************************************

Three helper methods print the parts of a program's user interface that look the same in every application:

:meth:`~pyTooling.TerminalUI.TerminalApplication._PrintHeadline` prints the class variable
:attr:`~pyTooling.TerminalUI.TerminalApplication.HeadLine`, centered between two horizontal lines of the given width
(``0`` meaning the terminal's width):

.. code-block::

   ================================================================
                        Report Service Program
   ================================================================

:meth:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin._PrintHelp` prints the help page of the argument parser,
or of one subcommand. It belongs to the mixin-class, which owns the parsers, and expects the ``Write***`` methods of
:class:`~pyTooling.TerminalUI.TerminalApplication` - so it is usable in an application combining both classes.

:meth:`~pyTooling.TerminalUI.TerminalApplication._PrintVersion` prints the program's meta data, read from the dunder
variables of the module handed to it:

+---------------------------+----------------------------------------------------+
| **Dunder variable**       | **Printed as**                                     |
+===========================+====================================================+
| ``__copyright__``         | ``Copyright:``, one line per line of the value.    |
+---------------------------+----------------------------------------------------+
| ``__license__``           | ``License:``                                       |
+---------------------------+----------------------------------------------------+
| ``__author__``            | ``Authors:``, one line per comma-separated author. |
+---------------------------+----------------------------------------------------+
| ``__email__``             | ``Email:``, if present.                            |
+---------------------------+----------------------------------------------------+
| ``__version__``           | ``Version:``                                       |
+---------------------------+----------------------------------------------------+
| ``__project_url__``       | ``Project:``, if present.                          |
+---------------------------+----------------------------------------------------+
| ``__documentation_url__`` | ``Documentation:``, if present.                    |
+---------------------------+----------------------------------------------------+
| ``__issue_tracker_url__`` | ``Issue tracker:``, if present.                    |
+---------------------------+----------------------------------------------------+

A missing copyright, license, author or version is printed in red rather than omitted, because those four are expected
of every program.

If a package name is passed as the second parameter, PyPI is queried for the latest release and the version line reports
whether an update is available:

.. code-block:: Python

   def _PrintVersion(self) -> None:
     import myPackage as DunderModule

     super()._PrintVersion(DunderModule, "myPackage")

.. code-block::

   Version:       v1.0.0 (Update available: v1.2.0)

The query is given a timeout (1 second by default, ``versionCheckTimeout``) and every failure is absorbed: an
unreachable index prints ``(PyPI timeout)`` instead of raising. Without a package name, no request is made at all.


.. _TERM/Example:

A Complete Application
**********************

A real command line program combines :class:`~pyTooling.TerminalUI.TerminalApplication` with
:class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin`, so commands and options are declared as decorated methods
while the messages, the verbosity and the exception reporting come from this package:

.. code-block:: Python

   @export
   class Application(TerminalApplication, ArgParseHelperMixin):
     HeadLine:          ClassVar[str] = "My Application"
     ISSUE_TRACKER_URL: ClassVar[str] = __issue_tracker_url__

     def __init__(self) -> None:
       super().__init__()
       ArgParseHelperMixin.__init__(self, prog="myapp", add_help=False)

     def Run(self) -> None:
       ArgParseHelperMixin.Run(self)

The :ref:`Terminal Application tutorial <TUTORIAL/TerminalApplication>` builds such a program step by step - from the
first message to the command handlers, the exception reporting and the unit tests.
