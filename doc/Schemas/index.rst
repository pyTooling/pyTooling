.. _SCHEMAS:

Overview
########

pyTooling ships the **XML schemas** of the file formats it writes, so a consumer of such a file can validate it
without owning pyTooling. Each schema is listed here with its full source, ready to read, to copy, or to download.

.. _SCHEMAS/Files:

Available schemas
*****************

.. list-table::
   :header-rows: 1
   :widths: 30 12 58

   * - Schema
     - Version
     - Written by
   * - :ref:`TestReport <SCHEMAS/TestReport-v0.1>`
     - v0.1
     - :mod:`pyTooling.Testing.ReportWriter`

.. _SCHEMAS/Versioning:

How a schema is versioned
*************************

**The file name carries the version**, so a new version of a format is added beside the old one rather than
replacing it: :file:`TestReport-v0.1.xsd` and, one day, :file:`TestReport-v0.2.xsd`. A reader of a document learns
from its ``xsi:noNamespaceSchemaLocation`` attribute which of them it needs.

.. _SCHEMAS/Programmatically:

Reaching a schema from Python
*****************************

The schemas are shipped in the resource package :mod:`pyTooling.Resources`, so a program that already depends on
pyTooling doesn't need the copy published here.

.. admonition:: ``example.py``

   .. code-block:: python

      from pathlib                        import Path
      from pyTooling                      import Resources
      from pyTooling.Common               import getResourceFile
      from pyTooling.Testing.ReportWriter import SCHEMA_FILES, SCHEMA_VERSION_LATEST

      schemaPath: Path = getResourceFile(Resources, SCHEMA_FILES[SCHEMA_VERSION_LATEST])

.. toctree::
   :hidden:

   TestReport-v0.1
