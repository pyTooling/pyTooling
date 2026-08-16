.. _TESTING:

Overview
########

The module :mod:`pyTooling.Testing` offers enhanced classes for writing unit tests with Python's :mod:`unittest`
framework, which is also what pytest runs.

.. #contents:: Table of Contents
   :depth: 2

.. _TESTING/Application:

Application Testing
###################

A unit test imports the code it tests. An **application test** starts the installed program the way a user does, so
the chain under test includes what importing cannot reach: the ``console_scripts`` entry point, the argument parsing
and the exit code.

:class:`~pyTooling.Testing.ApplicationTestcaseMixin` is a classic mixin for :class:`unittest.TestCase` classes. It
resolves the console script once per test class and offers two ways to start the program:

* :meth:`~pyTooling.Testing.ApplicationTestcaseMixin.RunEntrypoint` runs the installed console script - the path a
  user takes, and therefore the one covering the entry-point wiring.
* :meth:`~pyTooling.Testing.ApplicationTestcaseMixin.RunModule` runs ``python -m <module>``. When this passes while
  the entry point fails, the packaging is at fault rather than the code.

Both capture ``stdout`` and ``stderr`` as text and take a ``timeout``, so a hanging program fails the test instead
of the test suite.

.. code-block:: python

   from unittest import TestCase

   from pyTooling.Testing import ApplicationTestcaseMixin


   class Commands(ApplicationTestcaseMixin, TestCase):
     _consoleScript =  "myprogram"
     _runnableModule = "myPackage.CLI"

     def test_Version(self) -> None:
       result = self.RunEntrypoint("--version")

       self.assertExitCode(result)
       self.assertIn("myprogram", result.stdout)

Both class variables are mandatory: a test class naming neither cannot run anything, so
:meth:`~pyTooling.Testing.ApplicationTestcaseMixin.setUpClass` raises a
:exc:`~pyTooling.Testing.TestingException` instead of letting every testcase in the class fail with a less obvious
error. A console script that is not installed is reported the same way.

.. _TESTING/Assertions:

Assertions
##########

:meth:`~pyTooling.Testing.ApplicationTestcaseMixin.assertExitCode` compares the exit code and, when they differ,
reports the command line together with what the program printed. That output is what explains the failure, and it
is gone once the test has finished, so it belongs in the assertion message rather than in the console.

:class:`~pyTooling.Testing.AssertionMixin` provides assertions that :mod:`unittest` gained later than the oldest
Python version pyTooling supports, so a test suite can use them whichever interpreter runs it:

.. code-block:: python

   class Slots(AssertionMixin, TestCase):
     def test_SlotsAreDerived(self) -> None:
       self.assertHasAttr(MyClass, "__slots__")

:meth:`~pyTooling.Testing.AssertionMixin.assertHasAttr` and
:meth:`~pyTooling.Testing.AssertionMixin.assertNotHasAttr` were added to :class:`unittest.TestCase` in Python 3.14.
On 3.14 and newer the mixin defines nothing, so the standard library's implementations and messages are used.

.. _TESTING/Helpers:

Helpers
#######

:func:`~pyTooling.Testing.stripANSIColorCodes` removes ANSI escape sequences from a text. A program writing to a
terminal colors its output while the same program in a pipe usually does not - comparing the stripped text is more
robust than encoding a rule about when the codes appear.
