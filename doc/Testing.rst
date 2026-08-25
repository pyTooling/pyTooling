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
report as a **property** - see :ref:`TESTING/Markers/Names`.

.. important::

   ``classname`` and ``name`` keep the **identifiers** and are not replaced by the titles, for two reasons.

   They are the testcase's **node ID**, which is what *selects* a test: on the command line, from an IDE's *run
   this test*, and from the cache ``--last-failed`` reads. And a post-processing tool may reasonably expect them to
   be identifiers - free of spaces and punctuation - so a title in that position could break it.

   A title is additional information, so it is reported as additional information.

.. _TESTING/Markers/Names:

The four names of a test item
=============================

A test item - a test suite or a testcase - has **four** names, and only the first is what Python calls it:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Name
     - Where it comes from
   * - **ID**
     - the module, class or method name. It is the item's ``classname``/``name``, and what selects the test.
   * - **title**
     - what the marker was given. Defaults to the ID.
   * - **summary**
     - the first paragraph of the doc-string.
   * - **description**
     - the doc-string.

They are four values, not a fallback chain: a title never replaces a summary, and a summary never becomes a title.
A testcase can therefore carry a short label *and* a sentence *and* the full prose, and a report can show whichever
of them it has room for.

.. code-block:: python

   @testsuite("Version comparison.")
   class VersionComparison(Testcase):
     """
     Compare two release versions.

     Everything about comparing them.
     """

     @testcase("A newer version compares greater.")
     def NewerIsGreater(self) -> None:
       """
       A newer version compares greater than an older one.

       Only the minor number differs here.
       """

All of them except the ID reach the report as properties:

.. code-block:: xml

   <testsuites name="pytest tests">
     <testsuite name="pytest" errors="0" failures="0" skipped="0"
                tests="1" time="0.016" timestamp="2026-08-24T23:55:41+00:00" hostname="build-01">
       <testcase classname="tests.unit.Versioning.Comparison.VersionComparison"
                 name="test_NewerIsGreater" time="0.001">
         <properties>
           <property name="title" value="A newer version compares greater." />
           <property name="summary" value="A newer version compares greater than an older one." />
           <property name="description"
                     value="A newer version compares greater than an older one.&#10;&#10;Only the minor ..." />
           <property name="testsuiteTitle" value="Version comparison." />
           <property name="testsuiteSummary" value="Compare two release versions." />
           <property name="testsuiteDescription"
                     value="Compare two release versions.&#10;&#10;Everything about comparing them." />
         </properties>
       </testcase>
     </testsuite>
   </testsuites>

``classname`` is the testcase's **package path** - the directories below the root, then the module, then the class
- so a testcase in :file:`tests/unit/Versioning/Comparison.py` is reported as
``tests.unit.Versioning.Comparison.VersionComparison``. Its **ID**, in the table above, is the last part of that.

.. hint::

   Because the title defaults to the ID, a marker can be added to an existing testcase without changing anything a
   report says about it - which is what makes a suite migratable one class at a time.

.. note::

   The test suite's names are reported per testcase, prefixed with ``testsuite``, rather than on the surrounding
   ``<testsuite>`` element. pytest's JUnit writer emits exactly **one** ``<testsuite name="pytest">`` for the whole
   session, not one per class, so a per-class name has no element of its own to sit on. The
   `PyTest-JUnit schema <https://github.com/edaa-org/pyEDAA.Reports>`__ does allow ``<properties>`` there - it is
   pytest that has nowhere to put them.

.. _TESTING/Markers/Enabling:

Enabling the plugin
===================

The collection itself is a pytest plugin, :mod:`pyTooling.Testing.PyTest`. pyTooling declares it as a ``pytest11``
entry point, so **an installed pyTooling registers it automatically** and a test suite only has to mark something.

The plugin is inert until something is marked, so its presence changes nothing for a test suite that collects by
name. Both styles work in one session and even in one file, which is what makes a gradual migration possible.

Two cases still name it explicitly:

.. code-block:: bash

   pytest -p pyTooling.Testing.PyTest tests/unit      # a checkout that is not installed
   pytest -p no:pyTooling.Testing.PyTest tests/unit   # switch the plugin off

The entry point's name **is** the module's name, so both spellings address the same plugin, and passing ``-p`` for
an already registered plugin does nothing rather than registering it twice.

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

.. _TESTING/ReportFormat:

A Report Format of One's Own
############################

JUnit XML cannot express two things a marked test suite has.

**Test suites do not nest.** A JUnit document holds one flat list of ``<testcase>`` elements, and the hierarchy is
squeezed into a dotted ``classname`` - ``tests.unit.Versioning.VersionComparison``. Every level between the root
and the class is a substring, so nothing can be said *about* a level: it has no element to carry a title or a
description.

**An item has one name.** :ref:`TESTING/Markers/Names` gives it four, and JUnit's only place for the other three is
a flat ``<property name= value=>`` pair, whose value is an attribute and therefore a single line.

:mod:`pyTooling.Testing.ReportWriter` writes a format that has both. It is a ``pytest11`` entry point as well, so
it needs no registration either - only the switch that turns it on:

.. code-block:: bash

   pytest --pytooling-xml=report/unit/TestReport.xml --junit-xml=report/unit/unittest.xml

Both files are written in one session from the same reports, so a pipeline keeps the format its dashboard
understands while the richer file is produced beside it.

.. code-block:: xml

   <?xml version='1.0' encoding='utf-8'?>
   <TestReport xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:noNamespaceSchemaLocation="TestReport-v0.1.xsd"
               timestamp="2026-08-25T18:15:26.819107+00:00"
               duration="0.000671" tests="2" failures="0" errors="0" skipped="0">
     <Testsuite name="test_versioning">
       <Testsuite name="VersionComparison">
         <Title>Version comparison.</Title>
         <Summary>Compare two release versions.</Summary>
         <Description>Compare two release versions.

   Everything about comparing them.</Description>
         <Testcase name="test_NewerIsGreater" status="passed" duration="0.000428"
                   nodeID="test_versioning.py::VersionComparison::test_NewerIsGreater">
           <Title>A newer version compares greater.</Title>
           <Summary>A newer version compares greater than an older one.</Summary>
           <Description>A newer version compares greater than an older one.

   Only the minor number differs here.</Description>
         </Testcase>
       </Testsuite>
     </Testsuite>
   </TestReport>

.. _TESTING/ReportFormat/Schema:

The schema
==========

The schema lives in the resource package :mod:`pyTooling.Resources` and is shipped with the distribution.
Every generated file points at it with ``xsi:noNamespaceSchemaLocation``, so a reader can validate without being
told where it lives. :func:`~pyTooling.Common.getResourceFile` returns its path, whether pyTooling is installed,
inside a wheel, or a checkout:

.. code-block:: python

   from pathlib                        import Path
   from xmlschema                      import XMLSchema
   from pyTooling                      import Resources
   from pyTooling.Common               import getResourceFile
   from pyTooling.Testing.ReportWriter import SCHEMA_FILES, SCHEMA_VERSION

   schemaPath: Path = getResourceFile(Resources, SCHEMA_FILES[SCHEMA_VERSION])
   XMLSchema(schemaPath).validate("report/unit/TestReport.xml")

Validating needs an XML schema library such as `xmlschema <https://pypi.org/project/xmlschema/>`__. **pyTooling
does not depend on one**: writing a report uses :mod:`xml.etree.ElementTree` from the standard library, so the
schema is there for whoever reads the file.

**The file name carries the format's version.** :data:`~pyTooling.Testing.ReportWriter.SCHEMA_FILES` maps a version
to its schema file, so a later version of the format is added beside the current one rather than replacing it, and
a reader learns from a report's ``xsi:noNamespaceSchemaLocation`` which version it is holding. The format states
its own version this way; the report does **not** name the tool that wrote it, nor the machine it ran on.

* ``name`` is an **attribute** on every item, because it is an identifier. ``Title``, ``Summary`` and
  ``Description`` are **elements**, because they are prose - ``Description`` is typed ``preservingstring``, so its
  line breaks survive.
* ``<Testsuite>`` is recursive, so the hierarchy is as deep as the test suite is.
* ``<Testcase>`` carries ``status`` from a fixed list, ``duration``, and a ``nodeID`` - the test runner's own
  identifier, so a reader of the report can re-run exactly that testcase.
* An item writes only the names it has, so an unmarked testcase produces a ``<Testcase>`` element with no children.

.. _TESTING/ReportFormat/Nesting:

Where the nesting comes from
============================

The levels are the node ID's own parts: the module path, then each class between it and the testcase. So
``tests/unit/Versioning.py::VersionComparison::test_NewerIsGreater`` becomes ``tests`` → ``unit`` → ``Versioning``
→ ``VersionComparison``, and a title or description attaches to whichever level declared one.

.. seealso::

   :ref:`TESTING/Markers`
      |rarr| Where the titles, summaries and descriptions come from.
