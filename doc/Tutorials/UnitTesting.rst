.. _TUTORIAL/UnitTesting:

Unit Testing
############

A unit test suite has two problems that have nothing to do with each other: deciding **what to test, in which
order**, and deciding **what the report calls it**. This tutorial takes them in that order.

.. seealso::

   :ref:`TUTORIAL/ApplicationTesting`
      |rarr| The other half - testing the program the way a user starts it.


.. _TUTORIAL/UnitTesting/Levels:

Levels of testing
*****************

Tests are written in levels, each building on the one below. The point of the order is that a failure at a lower
level explains a failure at a higher one: if constructing an object is broken, every algorithm over a network of
those objects fails too, and only the first level says *why*.

.. rubric:: 1. Instantiation of (data model) classes

Construct **one** object and look at it. Nothing else is involved yet, so a failure here is unambiguous.

* Check the initializer.

  * Check the default parameters.
  * Check the parameter checkers: type checks, value range checks, and so on.
  * Check the optional parameters, one at a time.

* Check class variables, class fields and properties.

  * Also check that the optional parameters are accessible through properties.

* Check :meth:`~object.__str__`, and :meth:`~object.__repr__`.

.. rubric:: 2. Neighbouring classes and a simple network of objects

Two or three objects, wired together. This is where a data model's *relations* are tested, not its values.

* Instantiate parent and child classes and create a hierarchy.

  * A hierarchy should be constructable **top-down and bottom-up** - both orders are used by real code.

* Add further children to a parent.
* Set a child's parent relation.
* If the model supports it:

  * Remove children from a parent.
  * Set the parent relation to ``None`` and unregister the child from its parent.

.. rubric:: 3. Algorithms on multiple connected instances

Now the network is big enough for an algorithm to have something to walk.

* Test iterators and generators.

  * Check their options, such as reversing or filtering.

.. rubric:: 4. Full example testing

End to end, with real input.

* Read files, parse their content, and access the parsed data through the data model.
* Transform input data into output data, e.g. a format conversion.

.. rubric:: 5. Application testing

The program as a user starts it. That is a tutorial of its own -
see :ref:`TUTORIAL/ApplicationTesting`.

.. hint::

   The levels map onto the test suite's directory layout: a package per level or capability, a module per feature
   group, a class per feature, and a method per *variant* of it. A failure then reads as a path from the broad to
   the specific.


.. _TUTORIAL/UnitTesting/Naming:

Naming testcases
****************

A test report is read by people who did not write the test - a reviewer scanning a failure, a maintainer looking at
a nightly run, someone opening the HTML report attached to a pull-request. What they see is the name of the
testcase. The rest of this tutorial is about why that name is hard to get right with name-based collection, and
what changes when a marker takes over the job.

.. _TUTORIAL/UnitTesting/Naming/NameBased:

The name does two jobs
======================

.. grid:: 2

   .. grid-item::
      :columns: 6

      A test runner has to know which classes and functions are tests. By default it decides from the name:
      pytest's ``python_classes`` matches ``Test*`` and ``python_functions`` matches ``test_*``, and
      :mod:`unittest`'s loader takes methods starting with ``test``.

      That is a good default - it needs no configuration and no imports. But it makes the identifier carry two
      unrelated jobs: it *enables collection*, and it *describes the check*. The two pull in opposite directions.

      A Python identifier cannot contain spaces, so a description has to be squeezed into ``CamelCase`` or
      ``snake_case``. And the mandatory ``test_`` prefix says nothing to a reader - it is addressed to the runner,
      not to them - yet it is in every line of the report.

   .. grid-item::
      :columns: 6

      .. code-block:: python

         class TestVersionComparison(TestCase):
           def test_newer_version_is_greater(self):
             self.assertGreater(Version("2.0"), Version("1.9"))

      Reported as:

      .. code-block:: text

         TestVersionComparison::test_newer_version_is_greater

      Every word a reader needs is there, and every word is in the wrong shape.

Three consequences follow, and none of them is fixed by naming things more carefully:

* **The prefix is noise.** ``test_`` appears in the terminal, in the JUnit XML and in the HTML report. It carries
  no information for the reader, because *everything* in a test report is a test.
* **Renaming a testcase is dangerous.** Drop the prefix by accident - while extracting a helper, for instance - and
  the testcase silently stops running. Nothing fails, the suite still passes, and the coverage change is the only
  hint.
* **A helper needs a naming rule.** A method in a test class that is not a testcase has to *avoid* the prefix, so
  the convention has to be known and followed in both directions.

.. _TUTORIAL/UnitTesting/Naming/Markers:

Marking instead of naming
=========================

.. grid:: 2

   .. grid-item::
      :columns: 6

      :deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase` split the two jobs apart. The
      decorator says *this is a testcase* - that is the collection half - and its parameter says *this is what it
      checks* - that is the reader's half.

      The parameter is an ordinary string, so it can be a sentence: articles, spaces, punctuation, a word that
      happens to be a Python keyword. The method keeps whatever name suits the code.

   .. grid-item::
      :columns: 6

      .. code-block:: python

         @testsuite("Version comparison")
         class VersionComparison(Testcase):

           @testcase("A newer version compares greater.")
           def NewerIsGreater(self) -> None:
             self.assertGreater(Version("2.0"), Version("1.9"))

      Reported as:

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

Read the two reports next to each other:

.. code-block:: text

   test_newer_version_is_greater             # what Python needed
   A newer version compares greater.         # what the reader needed

The identifier is still there, where Python and every tool that re-runs a testcase need one. What the marker adds
is a *title* beside it - see :ref:`TESTING/Markers/Behavior` for why beside rather than instead.

The same three consequences turn around:

* **Nothing is noise.** Every word in the line was chosen for the reader.
* **Renaming is safe.** The marker enables collection, so renaming the method cannot silently remove the testcase
  from the suite. Removing the *marker* does - and that is a visible, deliberate edit.
* **A helper needs no rule.** It is simply not marked.

.. _TUTORIAL/UnitTesting/Naming/Migration:

Migrating a suite
=================

Enabling the plugin does not change an existing suite: nothing is marked yet, so nothing collects differently.

.. code-block:: python

   # conftest.py
   pytest_plugins = ["pyTooling.Testing.PyTest"]

From there, a suite can move one class at a time - the two styles run in the same session and even in the same
file. A useful intermediate step is to mark without naming:

.. code-block:: python

   @testsuite
   class VersionComparison(Testcase):

     @testcase
     def NewerIsGreater(self) -> None:
       ...

The identifiers are unchanged, the report is unchanged, but collection no longer depends on the spelling - so the
``test_`` prefixes can now be dropped in a separate commit whose diff is only renames, and a sentence can be added
per testcase whenever someone has a reason to.

.. _TUTORIAL/UnitTesting/Naming/DocString:

Letting the doc-string do it
============================

A testcase that already has a doc-string has already been described once. The markers read it: the summary becomes
the title, the body becomes a description that travels into the report as a property.

.. code-block:: python

   @testcase
   def NewerIsGreater(self) -> None:
     """
     A newer version compares greater.

     Only the minor number differs here, so this also pins that it is not a string
     comparison, where "2.0" < "1.9" would hold.
     """

Nothing is written twice, and the *why* - which rarely fits a title at all - is now in the report next to the
result, where someone reading a failure can see it.

.. topic:: When name-based collection is the better choice

   Marking costs an import and a decorator per testcase. For a small suite whose testcase names are already
   descriptive, that is a poor trade. The markers pay off where a report is *read by someone other than its
   author* - a published HTML report, a pull-request check, a nightly job - and where a testcase checks something
   that does not fit an identifier.

.. seealso::

   :ref:`TESTING/Markers`
      |rarr| The reference for both decorators and the plugin.
