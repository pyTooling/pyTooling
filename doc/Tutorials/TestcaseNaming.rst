.. _TUTORIAL/TestcaseNaming:

Naming Testcases
################

A test report is read by people who did not write the test - a reviewer scanning a failure, a maintainer looking at
a nightly run, someone opening the HTML report attached to a pull-request. What they see is the name of the
testcase. This tutorial is about why that name is hard to get right with name-based collection, and what changes
when a marker takes over the job.

.. _TUTORIAL/TestcaseNaming/NameBased:

The name does two jobs
**********************

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

.. _TUTORIAL/TestcaseNaming/Markers:

Marking instead of naming
*************************

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

         from pyTooling.Testing import Testcase, testsuite, testcase


         @testsuite("Version comparison")
         class VersionComparison(Testcase):
           @testcase("a newer version compares greater")
           def NewerIsGreater(self) -> None:
             self.assertGreater(Version("2.0"), Version("1.9"))

      Reported as:

      .. code-block:: text

         Version comparison::a newer version compares greater

Read the two reports next to each other:

.. code-block:: text

   TestVersionComparison::test_newer_version_is_greater      # what Python needed
   Version comparison::a newer version compares greater      # what the reader needed

The same three consequences turn around:

* **Nothing is noise.** Every word in the line was chosen for the reader.
* **Renaming is safe.** The marker enables collection, so renaming the method cannot silently remove the testcase
  from the suite. Removing the *marker* does - and that is a visible, deliberate edit.
* **A helper needs no rule.** It is simply not marked.

.. _TUTORIAL/TestcaseNaming/Migration:

Migrating a suite
*****************

Enabling the plugin does not change an existing suite: nothing is marked yet, so nothing collects differently.

.. code-block:: python

   # conftest.py
   pytest_plugins = ["pyTooling.Testing.PyTest"]

From there, a suite can move one class at a time - the two styles run in the same session and even in the same
file. A useful intermediate step is to mark without naming:

.. code-block:: python

   @testsuite()
   class VersionComparison(Testcase):
     @testcase()
     def NewerIsGreater(self) -> None:
       ...

The identifiers are unchanged, the report is unchanged, but collection no longer depends on the spelling - so the
``test_`` prefixes can now be dropped in a separate commit whose diff is only renames, and a sentence can be added
per testcase whenever someone has a reason to.

.. topic:: When name-based collection is the better choice

   Marking costs an import and a decorator per testcase. For a small suite whose testcase names are already
   descriptive, that is a poor trade. The markers pay off where a report is *read by someone other than its
   author* - a published HTML report, a pull-request check, a nightly job - and where a testcase checks something
   that does not fit an identifier.

.. seealso::

   :ref:`TESTING/Markers`
      |rarr| The reference for both decorators and the plugin.
