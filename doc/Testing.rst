.. _TESTING:

Overview
########

The module :mod:`pyTooling.Testing` offers enhanced classes for writing unit tests with Python's :mod:`unittest`
framework, which is also what pytest runs.

.. #contents:: Table of Contents
   :depth: 2

.. _TESTING/Testcase:

Testcase
########

:class:`~pyTooling.Testing.Testcase` is the class to derive a testcase from. It *is* a
:class:`unittest.TestCase` - everything that class offers is available unchanged - and adds what pyTooling's test
suites otherwise write themselves.

.. code-block:: python

   from pyTooling.Testing import Testcase


   class Slots(Testcase):
     def test_SlotsAreDerived(self) -> None:
       self.assertHasAttr(MyClass, "__slots__")

Deriving from it rather than from :class:`unittest.TestCase` costs nothing and means a test suite picks up what is
added later without changing every class again.

.. _TESTING/Testcase/Assertions:

Assertions
==========

:meth:`~pyTooling.Testing.Testcase.assertHasAttr` and :meth:`~pyTooling.Testing.Testcase.assertNotHasAttr` check
whether an object has an attribute. They were added to :class:`unittest.TestCase` in **Python 3.14**, so a test
suite running on 3.11 to 3.13 cannot use them - :class:`~pyTooling.Testing.Testcase` provides them there.

On Python 3.14 and newer the class defines nothing of its own, so the standard library's implementations and
messages are used and the two behave identically on every supported interpreter.

.. _TESTING/Application:

Application Testing
###################

A unit test imports the code it tests. An **application test** starts the installed program the way a user does, so
the chain under test includes what importing cannot reach: the ``console_scripts`` entry point, the argument parsing
and the exit code.

:class:`~pyTooling.Testing.ApplicationTestcase` derives from :class:`~pyTooling.Testing.Testcase`. It
resolves the console script once per test class and offers two ways to start the program:

* :meth:`~pyTooling.Testing.ApplicationTestcase.RunEntrypoint` runs the installed console script - the path a
  user takes, and therefore the one covering the entry-point wiring.
* :meth:`~pyTooling.Testing.ApplicationTestcase.RunModule` runs ``python -m <module>``. When this passes while
  the entry point fails, the packaging is at fault rather than the code.

Both capture ``stdout`` and ``stderr`` as text and take a ``timeout``, so a hanging program fails the test instead
of the test suite.

.. code-block:: python

   from pyTooling.Testing import ApplicationTestcase


   class Commands(ApplicationTestcase):
     _consoleScript =  "myprogram"
     _runnableModule = "myPackage.CLI"

     def test_Version(self) -> None:
       result = self.RunEntrypoint("--version")

       self.assertExitCode(result)
       self.assertIn("myprogram", result.stdout)

Both class variables are mandatory: a test class naming neither cannot run anything, so
:meth:`~pyTooling.Testing.ApplicationTestcase.setUpClass` raises a
:exc:`~pyTooling.Testing.TestingException` instead of letting every testcase in the class fail with a less obvious
error. A console script that is not installed is reported the same way.

.. _TESTING/Application/Assertions:

Assertions
==========

:meth:`~pyTooling.Testing.ApplicationTestcase.assertExitCode` compares the exit code and, when they differ,
reports the command line together with what the program printed. That output is what explains the failure, and it
is gone once the test has finished, so it belongs in the assertion message rather than in the console.

.. _TESTING/Helpers:

Helpers
#######

:func:`~pyTooling.Testing.stripANSIColorCodes` removes ANSI escape sequences from a text. A program writing to a
terminal colors its output while the same program in a pipe usually does not - comparing the stripped text is more
robust than encoding a rule about when the codes appear.
