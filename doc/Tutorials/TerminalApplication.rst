.. _TUTORIAL/TerminalApplication:

Terminal Application
####################

This tutorial builds a command line program step by step: a program that emits categorized messages, honors
``--verbose``, ``--debug`` and ``--quiet``, counts its own errors, prints version information, and reports an unhandled
exception instead of dumping a traceback.

See also the :ref:`reference documentation of pyTooling.TerminalUI <TERM>`.


.. _TUTORIAL/TerminalApplication/Step1:

Step 1 - The Application Class
******************************

An application derives from :class:`~pyTooling.TerminalUI.TerminalApplication` and writes its messages with the
``Write*`` method matching the message's :ref:`severity <TERM/Severity>`.

.. code-block:: Python

   from pyTooling.TerminalUI import TerminalApplication


   class Application(TerminalApplication):
     HeadLine = "My Application"

     def Run(self) -> None:
       self._PrintHeadline()
       self.WriteNormal("Reading the input file...")
       self.WriteVerbose("  Line 1 of 4")
       self.WriteWarning("The input file is empty.")


   def main() -> NoReturn:
     program = Application()
     program.Run()


   if __name__ == "__main__":
     main()

Running it prints the normal message and the warning; the verbose message is dropped, because the default log level is
``Severity.Normal``. The warning is also *counted*, which :ref:`step 4 <TUTORIAL/TerminalApplication/Step4>` makes use
of.

.. hint::

   :class:`~pyTooling.TerminalUI.TerminalApplication` is a singleton: instantiating ``Application`` a second time
   returns the same object, including its recorded messages and counters.


.. _TUTORIAL/TerminalApplication/Step2:

Step 2 - Verbosity Switches
***************************

Which severities are visible is decided by :meth:`~pyTooling.TerminalUI.TerminalApplication.Configure`, usually from the
command line switches:

.. code-block:: Python

   from sys import argv

   def main() -> NoReturn:
     program = Application()
     program.Configure(
       verbose=("-v" in argv or "--verbose" in argv),
       debug=(  "-d" in argv or "--debug"   in argv),
       quiet=(  "-q" in argv or "--quiet"   in argv)
     )
     program.Run()

Now ``--verbose`` shows the verbose line, ``--debug`` additionally shows every ``WriteDebug`` message (debug implies
verbose), and ``--quiet`` reduces the output to errors and messages written with
:meth:`~pyTooling.TerminalUI.TerminalApplication.WriteQuiet` - which is how a quiet program still prints its result.

Expensive work can be skipped by asking the application whether it would print at all:

.. code-block:: Python

   if self.Verbose:
     self.WriteVerbose(self._CollectStatistics())    # not computed unless it's printed


.. _TUTORIAL/TerminalApplication/Step3:

Step 3 - A Headline and a Version Command
*****************************************

:meth:`~pyTooling.TerminalUI.TerminalApplication._PrintHeadline` prints the class variable ``HeadLine`` centered between
two horizontal lines. :meth:`~pyTooling.TerminalUI.TerminalApplication._PrintVersion` prints copyright, license,
authors and version - read from the dunder variables of the module handed to it, which is why an application overrides
it with the one-liner naming its own package:

.. code-block:: Python

   class Application(TerminalApplication):
     HeadLine = "My Application"

     def _PrintVersion(self) -> None:
       import myPackage as DunderModule

       super()._PrintVersion(DunderModule, "myPackage")

Passing the package name (second parameter) queries PyPI for the latest release, so the version line tells the user
whether an update is available. The query has a one second timeout and never raises - an unreachable index prints
``(PyPI timeout)``.


.. _TUTORIAL/TerminalApplication/Step4:

Step 4 - Stopping on Errors
***************************

Errors, critical warnings and warnings are counted while they are written, even when the log level hides them. A
processing step therefore ends by asking whether it may continue:

.. code-block:: Python

   def Run(self) -> None:
     self.ReadInputFiles()
     self.ExitOnPreviousErrors()      # unreadable input: don't start processing

     self.Process()
     self.ExitOnPreviousWarnings()    # stricter: a warning is enough to stop

:meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousErrors` writes a fatal message and exits with
:attr:`~pyTooling.TerminalUI.TerminalBaseApplication.FATAL_EXIT_CODE` if anything was counted.
:meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousCriticalWarnings` and
:meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousWarnings` do the same for the other two counters.


.. _TUTORIAL/TerminalApplication/Step5:

Step 5 - Reporting Unhandled Exceptions
***************************************

A user should not see a raw traceback. The entry point catches what escaped and hands it to the matching printer, which
formats the exception, its notes, its cause and its traceback, and then exits with a distinct exit code:

.. code-block:: Python

   from pyTooling.Exceptions import ExceptionBase


   def main() -> NoReturn:
     program = Application()
     program.Configure(
       verbose=("-v" in argv or "--verbose" in argv),
       debug=(  "-d" in argv or "--debug"   in argv),
       quiet=(  "-q" in argv or "--quiet"   in argv)
     )

     try:
       program.Run()
     except MyPackageException as ex:                      # the program's own exceptions, reported as messages
       program.WriteLineToStdErr(f"{{RED}}[ERROR] {ex}{{NOCOLOR}}".format(**Application.Foreground))
     except ExceptionBase as ex:
       program.PrintExceptionBase(ex)                      # exit code 241, a known exception
     except NotImplementedError as ex:
       program.PrintNotImplementedError(ex)                # exit code 240, an unimplemented function was called
     except MissingDependencyException as ex:
       program.PrintMissingDependencyException(ex)         # exit code 242, an installation problem
     except Exception as ex:
       program.PrintException(ex)                          # exit code 241, an unexpected exception

Set :attr:`~pyTooling.TerminalUI.TerminalBaseApplication.ISSUE_TRACKER_URL`, and each of these reports ends by inviting
the user to file a bug, with the URL - except the missing-dependency report, which names the package and the command
installing it instead: nothing is wrong with the program. The application connects the class variable to its own dunder
variable, because only the application knows which of its modules carries it:

.. code-block:: Python

   from myPackage import __issue_tracker_url__


   class Application(TerminalApplication):
     ISSUE_TRACKER_URL = __issue_tracker_url__

The program's own exceptions come first and are reported as ordinary error messages - a user who passed a wrong option
should read one line, not a traceback. Only what nobody expected reaches the printers, which is why they are the last
three clauses.


.. _TUTORIAL/TerminalApplication/Step6:

Step 6 - Commands and Options
*****************************

The message handling is independent of argument parsing, but the two are designed to be combined: an application
deriving from :class:`~pyTooling.TerminalUI.TerminalApplication` **and**
:class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin` gets commands and options as decorated methods - and
:meth:`~pyTooling.TerminalUI.TerminalApplication._PrintHelp` then prints the parser's help page, or the help page of a
single command.

.. code-block:: Python

   from argparse                      import Namespace, RawDescriptionHelpFormatter
   from typing                        import ClassVar, NoReturn

   from pyTooling.Attributes.ArgParse import ArgParseHelperMixin, CommandHandler, DefaultHandler
   from pyTooling.Decorators          import export
   from pyTooling.TerminalUI          import TerminalApplication

   from myPackage                     import __issue_tracker_url__


   @export
   class Application(TerminalApplication, ArgParseHelperMixin):
     HeadLine:          ClassVar[str] = "My Application"
     ISSUE_TRACKER_URL: ClassVar[str] = __issue_tracker_url__

     def __init__(self) -> None:
       super().__init__()
       ArgParseHelperMixin.__init__(self, prog="myapp", formatter_class=RawDescriptionHelpFormatter, add_help=False)

     def Run(self) -> None:
       ArgParseHelperMixin.Run(self)

     @DefaultHandler()
     def HandleDefault(self, _: Namespace) -> None:
       self._PrintHeadline()
       self._PrintHelp()

     @CommandHandler("help", help="Display help page(s) for the given command name.")
     def HandleHelp(self, args: Namespace) -> None:
       self._PrintHeadline()
       self._PrintHelp(args.Command)

     @CommandHandler("version", help="Display version information.")
     def HandleVersion(self, _: Namespace) -> None:
       self._PrintHeadline()
       self._PrintVersion()

     def _PrintVersion(self) -> None:
       import myPackage as DunderModule

       super()._PrintVersion(DunderModule, "myPackage")

That is the full shape of a pyTooling-based command line program. See :ref:`ATTR/ArgParse` for the argument parsing
part, and :ref:`TERM` for everything the terminal side offers.


.. _TUTORIAL/TerminalApplication/Testing:

Testing Such an Application
***************************

Every written message is recorded as a :ref:`Line <TERM/Line>` object in
:attr:`~pyTooling.TerminalUI.TerminalApplication.Lines`, so a testcase can check *what* an application reported without
capturing the terminal:

.. code-block:: Python

   from pyTooling.TerminalUI import Severity
   from pyTooling.Testing    import Testcase


   class ApplicationTests(Testcase):
     def test_AnEmptyInputFileIsReported(self) -> None:
       class TestApplication(Application):    # own class: the base class is a singleton
         pass

       program = TestApplication()
       program.Run()

       self.assertEqual(1, program.WarningCount)
       self.assertIn(Severity.Warning, [line.Severity for line in program.Lines])

Two details make this work: a derived class per testcase, because
:class:`~pyTooling.TerminalUI.TerminalApplication` is a singleton and would otherwise carry messages from one testcase
into the next, and the counters, which are incremented even when the log level suppresses the message itself.

The testcase derives from :class:`~pyTooling.Testing.Testcase` - see :ref:`TESTING/Testcase` - which is
:class:`unittest.TestCase` plus the assertions newer Python versions added.
