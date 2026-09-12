.. _TUTORIAL/ApplicationTesting:

Application Testing
###################

The levels in :ref:`TUTORIAL/UnitTesting` all reach the code by *importing* it. That leaves a layer untested, and
it is the layer a user actually meets: the console script, the argument parser, what is written to ``STDOUT``
versus ``STDERR``, and the exit code. None of it runs when a test does ``from myPackage import Thing``.

Application testing starts the program the way a user does and looks at what came back.

.. seealso::

   :ref:`TUTORIAL/UnitTesting`
      |rarr| The four levels below this one.
   :ref:`TESTING/Application`
      |rarr| The reference for :class:`~pyTooling.Testing.ApplicationTestcase`.


.. _TUTORIAL/ApplicationTesting/Why:

What only a subprocess can tell you
***********************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      Calling a program's ``main()`` from a test is not the same as running it. Four things differ, and each has
      been a real bug:

      * **The console script.** ``pip install`` generates it from an entry point. A typo there ships a package
        whose command does not exist, and every import-based test still passes.
      * **The argument parser.** It is built when the program starts, not when a module is imported.
      * **The exit code.** ``main()`` returning ``2`` and the process exiting with ``2`` are different claims.
      * **The streams.** Which messages go to ``STDOUT`` and which to ``STDERR`` is only observable from outside.

   .. grid-item::
      :columns: 6

      .. code-block:: python

         from pyTooling.Testing import ApplicationTestcase


         class Version(ApplicationTestcase):
           _consoleScript  = "myprogram"
           _runnableModule = "myPackage"

           def test_Version(self) -> None:
             result = self.RunEntrypoint("--version")

             self.assertExitCode(result)
             self.assertIn("myprogram", result.stdout)

Both class variables are mandatory. A class naming neither can run nothing, so
:meth:`~pyTooling.Testing.ApplicationTestcase.setUpClass` says so once instead of letting every testcase in the
class fail with a less obvious error.


.. _TUTORIAL/ApplicationTesting/TwoWays:

Two ways to start the program
*****************************

:meth:`~pyTooling.Testing.ApplicationTestcase.RunEntrypoint` runs the **installed console script**, resolved on
``PATH``. :meth:`~pyTooling.Testing.ApplicationTestcase.RunModule` runs ``python -m <module>``, bypassing it.

Having both is a diagnosis, not a convenience: if ``RunModule`` passes while ``RunEntrypoint`` fails, the packaging
is at fault and the code is fine. That distinction is invisible from a single test.

.. code-block:: python

   def test_TheEntryPointIsWiredUp(self) -> None:
     viaScript = self.RunEntrypoint("--version")
     viaModule = self.RunModule("--version")

     self.assertExitCode(viaScript)
     self.assertEqual(viaModule.stdout, viaScript.stdout)


.. _TUTORIAL/ApplicationTesting/Assertions:

Reading the result
******************

:meth:`~pyTooling.Testing.ApplicationTestcase.assertExitCode` compares the exit code and, when it differs, reports
the command line together with everything the program printed. That output is what explains the failure, and it is
gone once the test has finished - so it belongs in the assertion message, not in the console.

A program writing to a terminal colors its output; the same program in a pipe usually does not, but that depends on
the program. :func:`~pyTooling.Testing.stripANSIColorCodes` removes the escape sequences, which is more robust than
encoding a rule about when they appear:

.. code-block:: python

   self.assertIn("ERROR", stripANSIColorCodes(result.stderr))


.. _TUTORIAL/ApplicationTesting/Writing:

What to test at this level
**************************

Application testing is expensive - every testcase is a process - so it tests the *wiring*, not the logic. The logic
belongs to the levels below, where a failure is cheaper to read.

* The program starts at all, and ``--version`` and ``--help`` work.
* Every sub-command is reachable and its arguments parse.
* Each documented exit code is actually produced.
* An error message reaches ``STDERR`` rather than ``STDOUT``.
* A file the program writes exists afterwards and has the expected content.

.. topic:: A test suite of one's own

   ``pyTooling``'s own :file:`tests/app` directory is exactly this: a package of ``ApplicationTestcase`` classes
   run separately from :file:`tests/unit`, because they need the package installed. Keeping them apart means the
   unit tests stay runnable from a checkout with nothing installed.
