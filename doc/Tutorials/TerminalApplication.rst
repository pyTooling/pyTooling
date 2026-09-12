.. _TUTORIAL/TerminalApplication:

Terminal Application
####################

This tutorial builds a command line program step by step: a program that emits categorized messages, honors
``--verbose``, ``--debug`` and ``--quiet``, counts its own errors, prints version information, and reports an unhandled
exception instead of dumping a traceback.

See also the :ref:`reference documentation of pyTooling.TerminalUI <TERM>`.

.. hint::

   Every code example on this page is a complete, runnable program in :file:`tests/example/TerminalApplication`, and
   each one is imported and exercised by the unit tests.


.. _TUTORIAL/TerminalApplication/Step1:

Step 1 - The Application Class
******************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      An application derives from :class:`~pyTooling.TerminalUI.TerminalApplication` and writes its messages with the
      ``Write*`` method matching the message's :ref:`severity <TERM/Severity>`.

      Running it prints the normal message and the warning; the verbose message is dropped, because the default log
      level is ``Severity.Normal``. The warning is also *counted*, which
      :ref:`step 4 <TUTORIAL/TerminalApplication/Step4>` makes use of.

      .. hint::

         :class:`~pyTooling.TerminalUI.TerminalApplication` is a singleton: instantiating ``Application`` a second time
         returns the same object, including its recorded messages and counters.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step1.py
         :language: Python
         :tab-width: 2
         :caption: Step1.py
         :start-at: from typing


.. _TUTORIAL/TerminalApplication/Step2:

Step 2 - Verbosity Switches
***************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      Which severities are visible is decided by :meth:`~pyTooling.TerminalUI.TerminalApplication.Configure`, usually
      from the command line switches.

      Now ``--verbose`` shows the verbose line, ``--debug`` additionally shows every ``WriteDebug`` message (debug
      implies verbose), and ``--quiet`` reduces the output to errors and messages written with
      :meth:`~pyTooling.TerminalUI.TerminalApplication.WriteQuiet` - which is how a quiet program still prints its
      result.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step2.py
         :language: Python
         :tab-width: 2
         :caption: Step2.py
         :pyobject: main

.. grid:: 2

   .. grid-item::
      :columns: 6

      Expensive work can be skipped by asking the application whether it would print at all. ``Verbose``, ``Debug`` and
      ``Quiet`` answer without writing anything, so the statistics are only collected when they end up on screen.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step2.py
         :language: Python
         :tab-width: 2
         :caption: Step2.py
         :pyobject: Application.Run


.. _TUTORIAL/TerminalApplication/Step3:

Step 3 - A Headline and a Version Command
*****************************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      :meth:`~pyTooling.TerminalUI.TerminalApplication._PrintHeadline` prints the class variable ``HeadLine`` centered
      between two horizontal lines. :meth:`~pyTooling.TerminalUI.TerminalApplication._PrintVersion` prints copyright,
      license, authors and version - read from the dunder variables of the module handed to it, which is why an
      application overrides it with the one-liner naming its own package.

      Passing the package name (second parameter) queries PyPI for the latest release, so the version line tells the
      user whether an update is available. The query has a one second timeout and never raises - an unreachable index
      prints ``(PyPI timeout)``.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step3.py
         :language: Python
         :tab-width: 2
         :caption: Step3.py
         :pyobject: Application


.. _TUTORIAL/TerminalApplication/Step4:

Step 4 - Stopping on Errors
***************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      Errors, critical warnings and warnings are counted while they are written, even when the log level hides them. A
      processing step therefore ends by asking whether it may continue.

      :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousErrors` writes a fatal message and exits with
      :attr:`~pyTooling.TerminalUI.TerminalBaseApplication.FATAL_EXIT_CODE` if anything was counted.
      :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousCriticalWarnings` and
      :meth:`~pyTooling.TerminalUI.TerminalApplication.ExitOnPreviousWarnings` do the same for the other two counters.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step4.py
         :language: Python
         :tab-width: 2
         :caption: Step4.py
         :pyobject: Application.Run


.. _TUTORIAL/TerminalApplication/Step5:

Step 5 - Reporting Unhandled Exceptions
***************************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      A user should not see a raw traceback. The entry point catches what escaped and hands it to the matching printer,
      which formats the exception, its notes, its cause and its traceback, and then exits with a distinct exit code.

      The program's own exceptions come first and are reported as ordinary error messages - a user who passed a wrong
      option should read one line, not a traceback. Only what nobody expected reaches the printers, which is why they
      are the last three clauses.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step5.py
         :language: Python
         :tab-width: 2
         :caption: Step5.py
         :pyobject: main

.. grid:: 2

   .. grid-item::
      :columns: 6

      Set :attr:`~pyTooling.TerminalUI.TerminalBaseApplication.ISSUE_TRACKER_URL`, and each of these reports ends by
      inviting the user to file a bug, with the URL - except the missing-dependency report, which names the package and
      the command installing it instead: nothing is wrong with the program. The application connects the class variable
      to its own dunder variable, because only the application knows which of its modules carries it.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step5.py
         :language: Python
         :tab-width: 2
         :caption: Step5.py
         :pyobject: Application


.. _TUTORIAL/TerminalApplication/Step6:

Step 6 - Commands and Options
*****************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      The message handling is independent of argument parsing, but the two are designed to be combined: an application
      deriving from :class:`~pyTooling.TerminalUI.TerminalApplication` **and**
      :class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin` gets commands and options as decorated methods - and
      :meth:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin._PrintHelp` then prints the parser's help page, or
      the help page of a single command.

      A command that takes a parameter declares it: ``help`` accepts an optional command name, so
      :class:`~pyTooling.Attributes.ArgParse.Argument.StringArgument` adds it to that command's parser and
      ``args.Command`` exists when the handler runs.

      That is the full shape of a pyTooling-based command line program. See :ref:`ATTR/ArgParse` for the argument
      parsing part, and :ref:`TERM` for everything the terminal side offers.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Step6.py
         :language: Python
         :tab-width: 2
         :caption: Step6.py
         :start-at: from argparse


.. _TUTORIAL/TerminalApplication/Testing:

Testing Such an Application
***************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      Every written message is recorded as a :ref:`Line <TERM/Line>` object in
      :attr:`~pyTooling.TerminalUI.TerminalApplication.Lines`, so a testcase can check *what* an application reported
      without capturing the terminal.

      Two details make this work: a derived class per testcase, because
      :class:`~pyTooling.TerminalUI.TerminalApplication` is a singleton and would otherwise carry messages from one
      testcase into the next, and the counters, which are incremented even when the log level suppresses the message
      itself.

      The testcase derives from :class:`~pyTooling.Testing.Testcase` - see :ref:`TESTING/Testcase` - which is
      :class:`unittest.TestCase` plus the assertions newer Python versions added.

   .. grid-item::
      :columns: 6

      .. literalinclude:: ../../tests/example/TerminalApplication/Testing.py
         :language: Python
         :tab-width: 2
         :caption: Testing.py
         :start-at: from pyTooling.TerminalUI
