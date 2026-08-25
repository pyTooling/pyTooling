.. _SCHEMAS/TestReport-v0.1:

TestReport v0.1
###############

The schema of :ref:`pyTooling's own test report format <TESTING/ReportFormat>`, which
:mod:`pyTooling.Testing.ReportWriter` writes and every generated report points at with
``xsi:noNamespaceSchemaLocation="TestReport-v0.1.xsd"``.

It differs from JUnit XML in the two ways JUnit cannot express: **test suites nest**, instead of being flattened
into a dotted ``classname``, and every item carries **four names** - an identifier, a title, a summary and a
description - instead of one name and a bag of ``<property>`` pairs.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Download

         :download:`TestReport-v0.1.xsd <../../pyTooling/Resources/TestReport-v0.1.xsd>`

   .. grid-item::
      :columns: 6

      .. admonition:: Validate a report

         .. code-block:: bash

            xmllint --schema TestReport-v0.1.xsd --noout TestReport.xml

.. seealso::

   :ref:`TESTING/ReportFormat`
      |rarr| What the format is for, and an example document.
   :ref:`TESTING/ReportFormat/Schema`
      |rarr| Reaching the schema from Python and validating with `xmlschema <https://pypi.org/project/xmlschema/>`__.

.. _SCHEMAS/TestReport-v0.1/Diagram:

Diagram
*******

Every complex type is a record of three compartments - its name, its attributes, and its simple-typed child
elements with their cardinality. A complex-typed child element is an **edge**, so containment is visible as
structure rather than as a repeated type name, and ``testsuite``'s edge to itself is what makes a test suite
nest. A simple type gets a node of its own only when it is an enumeration, because its values are what a type
name cannot say.

.. xsd-graph:: ../../pyTooling/Resources/TestReport-v0.1.xsd
   :caption: The types of :file:`TestReport-v0.1.xsd`, drawn from the schema at documentation build time.

.. _SCHEMAS/TestReport-v0.1/Source:

Source
******

.. literalinclude:: ../../pyTooling/Resources/TestReport-v0.1.xsd
   :language: xml
   :linenos:
   :caption: TestReport-v0.1.xsd
