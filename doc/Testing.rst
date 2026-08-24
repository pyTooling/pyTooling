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
:exc:`~pyTooling.Testing.TestingError` instead of letting every testcase in the class fail with a less obvious
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

.. _TESTING/Markers:

Marker-based Collection
#######################

A test runner has to decide what a test is, and by default it decides from a **name**: pytest collects classes
matching ``python_classes`` (``Test*``) and functions matching ``python_functions`` (``test_*``), and
:mod:`unittest`'s loader collects methods starting with ``test``. The identifier therefore does two jobs at once -
it names the entity *and* it enables collection.

:deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase` separate them.

.. code-block:: python

   from pyTooling.Testing import Testcase, testsuite, testcase


   @testsuite("Version comparison")
   class VersionComparison(Testcase):
     @testcase("a newer version compares greater")
     def NewerIsGreater(self) -> None:
       self.assertGreater(Version("2.0"), Version("1.9"))

The class is collected because it is *marked*, not because of how it is spelled, and the **report** shows the name
the marker gives it:

.. code-block:: xml

   <testcase classname="Version comparison" name="a newer version compares greater">
     <properties>
       <property name="testcase" value="a newer version compares greater" />
       <property name="testsuite" value="Version comparison" />
     </properties>
   </testcase>

.. important::

   Only the report is renamed. The testcase keeps its **node ID** -
   ``test_versioning.py::VersionComparison::test_NewerIsGreater`` - because that is what *selects* a test: on the
   command line, from an IDE's *run this test*, and from the cache ``--last-failed`` reads. A plugin that renamed
   the item would produce a name nothing can be re-run by.

Both decorators take an optional name. Without one, the identifier is used, so a marker can be added to an existing
testcase without changing what a report says about it.

.. _TESTING/Markers/Enabling:

Enabling the plugin
===================

The collection itself is a pytest plugin, :mod:`pyTooling.Testing.PyTest`. It is **not** registered automatically -
add it in the root :file:`conftest.py`

.. code-block:: python

   pytest_plugins = ["pyTooling.Testing.PyTest"]

or pass it per run:

.. code-block:: bash

   pytest -p pyTooling.Testing.PyTest tests/unit

The plugin is inert until something is marked, so enabling it changes nothing for a test suite that collects by
name. Both styles work in one session and even in one file, which is what makes a gradual migration possible.

.. _TESTING/Markers/Behavior:

What the plugin does
====================

* :func:`~pyTooling.Testing.PyTest.pytest_pycollect_makeitem` turns a marked class into a collector and a marked
  method into a test item, so neither has to match ``python_classes`` or ``python_functions``.
* :func:`~pyTooling.Testing.PyTest.pytest_collection_modifyitems` attaches the declared names to the item as
  :attr:`~_pytest.nodes.Item.user_properties` - the channel the :func:`record_property` fixture uses. They are part
  of the test report, so they survive a ``pytest-xdist`` worker and reach the JUnit report as ``<property>``
  elements.
* :class:`~pyTooling.Testing.PyTest.JUnitReportRenamer` overwrites the ``name`` and ``classname`` attributes of the
  ``<testcase>`` entry, which are derived from the node ID and therefore cannot be set through a property. It runs
  after pytest's JUnit writer and looks the entry up rather than creating one - creating one would emit a second
  ``<testcase>`` per testcase, because the writer opens an entry only for the phase it reports.
* **Node IDs are never touched**, so selection, ``pytest-xdist``, ``--last-failed`` and IDE integration work exactly
  as they do without the plugin. The terminal keeps showing the identifier; it is the report that is written for
  someone else to read.
* An **unmarked** method in a marked class is not collected. Marking is the whole statement of intent, so a helper
  method needs no naming convention to stay out of the report.
* A marked :class:`unittest.TestCase` is a special case. Such a class is collected by pytest's :mod:`unittest`
  support, which asks :mod:`unittest`'s own loader for the test methods, and that loader recognises the ``test``
  prefix only. The plugin therefore aliases each marked method under a name the loader accepts and lets pytest
  collect the class as usual; the alias never reaches the report, because the item is renamed afterwards.

.. seealso::

   :ref:`Tutorial: naming testcases <TUTORIAL/TestcaseNaming>`
      |rarr| Why the name a report shows and the name Python needs are different problems.
