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
     """
     This is a testsuite summary.
     
     Here follows a multiline
     testsuite description.
     """
   
     @testcase("A newer version compares greater")
     def NewerIsGreater(self) -> None:
       """
       This is a testcase summary.
       
       This can describe a testcase with more details
       using multiple lines.
       """
       self.assertGreater(Version("2.0"), Version("1.9"))

The class is collected because it is *marked*, not because of how it is spelled, and the title travels into the
report as a **property**:

.. code-block:: xml

   <testsuites name="pytest tests">
     <testsuite name="pytest" errors="0" failures="0" skipped="0"
                tests="1" time="0.016" timestamp="2026-08-24T23:55:41+00:00" hostname="build-01">
       <testcase classname="tests.unit.Versioning.Comparison.VersionComparison"
                 name="test_NewerIsGreater" time="0.001">
         <properties>
           <property name="title" value="A newer version compares greater." />
           <property name="testsuiteTitle" value="Version comparison" />
         </properties>
       </testcase>
     </testsuite>
   </testsuites>

``classname`` is the testcase's **package path** - the directories below the root, then the module, then the class
- so a testcase in :file:`tests/unit/Versioning/Comparison.py` is reported as
``tests.unit.Versioning.Comparison.VersionComparison``.

.. important::

   ``classname`` and ``name`` keep the **identifiers** and are not replaced by the titles, for two reasons.

   They are the testcase's **node ID**, which is what *selects* a test: on the command line, from an IDE's *run
   this test*, and from the cache ``--last-failed`` reads. And a post-processing tool may reasonably expect them to
   be identifiers - free of spaces and punctuation - so a title in that position could break it.

   A title is additional information, so it is reported as additional information.

.. note::

   The title of the *test suite* is reported per testcase, as ``testsuiteTitle``, rather than on a surrounding
   element. pytest's JUnit writer emits exactly **one** ``<testsuite name="pytest">`` for the whole session, not
   one per class, so a per-class title has no element of its own to sit on.

.. _TESTING/Markers/Descriptions:

Titles and descriptions
=======================

Both decorators take an optional ``title`` and ``description``, and both fall back to the **doc-string**: its
summary becomes the title, its body becomes the description.

.. code-block:: python

   @testsuite
   class VersionComparison(Testcase):
     """
     Version comparison.

     Everything about comparing two release versions.
     """

     @testcase
     def NewerIsGreater(self) -> None:
       """
       A newer version compares greater.

       Only the minor number differs here, so this also pins that it is not a string
       comparison, where "2.0" < "1.9" would hold.
       """

All four reach the report as properties:

.. code-block:: xml

   <testcase classname="test_versioning.VersionComparison" name="test_NewerIsGreater">
     <properties>
       <property name="title" value="A newer version compares greater." />
       <property name="description" value="Only the minor number differs here, ..." />
       <property name="testsuiteTitle" value="Version comparison." />
       <property name="testsuiteDescription" value="Everything about comparing two release versions." />
     </properties>
   </testcase>

Three sources can title a testcase, tried in this order:

1. the decorator's ``title`` argument,
2. the doc-string's summary - a summary spanning several lines is joined into one,
3. the identifier, when there is no doc-string.

The same order applies to ``description`` with the doc-string's body. An explicit argument replaces *its own* part
only: giving a ``title`` discards the summary but keeps the body as the description.

.. hint::

   Because the identifier is the last fallback, a marker can be added to an existing testcase without changing
   anything a report says about it - which is what makes a suite migratable one class at a time.

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
* :func:`~pyTooling.Testing.PyTest.pytest_collection_modifyitems` attaches the titles to the item as
  :attr:`~_pytest.nodes.Item.user_properties` - the channel the :func:`record_property` fixture uses. They are part
  of the test report, so they survive a ``pytest-xdist`` worker and reach the JUnit report as ``<property>``
  elements.
* **Node IDs are never touched**, so selection, ``pytest-xdist``, ``--last-failed`` and IDE integration work exactly
  as they do without the plugin.
* An **unmarked** method in a marked class is not collected. Marking is the whole statement of intent, so a helper
  method needs no naming convention to stay out of the report.
* A marked :class:`unittest.TestCase` is a special case. Such a class is collected by pytest's :mod:`unittest`
  support, which asks :meth:`unittest.TestLoader.getTestCaseNames` for the test methods - and that loader matches
  :attr:`~unittest.TestLoader.testMethodPrefix`, which is ``"test"``. It is **not** the ``python_functions``
  setting: with ``python_functions = check_*``, a plain class collects ``check_*`` methods while a
  :class:`~unittest.TestCase` still collects ``test_*`` ones. The plugin therefore aliases each marked method under
  a name that loader accepts and lets pytest collect the class as usual.

.. seealso::

   :ref:`Tutorial: unit testing <TUTORIAL/UnitTesting>`
      |rarr| The levels a test suite is written in, and why the title a report shows and the name Python needs are
      different problems.
