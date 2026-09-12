.. _SCHEMAS:

Schema Files
############

pyTooling ships the schemas of the file formats it writes and reads, so a consumer of such a file can validate it
without owning pyTooling. Each schema is listed here with its full source, ready to read, to copy, or to download.

.. _SCHEMAS/Files:

Available schemas
*****************

Schema URL prefix: ``http://pytooling.github.io/pyTooling/Schemas/***``

.. list-table::
   :header-rows: 1
   :widths: 30 10 10 50

   * - Schema
     - Latest Version
     - Language
     - Read or Written by
   * - :ref:`TestReport <SCHEMAS/TestReport-v0.1>`
     - v0.1
     - XML
     - :mod:`pyTooling.Testing.ReportWriter`
   * - :ref:`PackageOverrides <SCHEMAS/PackageOverrides-v0.1>`
     - v0.1
     - JSON
     - :class:`pyTooling.Dependency.Python.LicenseOverrides`

.. _SCHEMAS/Versioning:

Schema Versioning
*****************

Each schema file has a major and minor version following the format ``SCHEMANAME-vXX.YY`` like ``TestReport-v0.1``.

Each schema has a dictionary in :pycode:`SCHEMA_FILES` variable, which lists available schema versions and related
schema files. In addition, the :pycode:`SCHEMA_VERSION_LATEST` variable holds the latest schema version.


.. _SCHEMAS/Access:

Schema file access
******************

The schema files are shipped in the resource package :mod:`pyTooling.Resources`, so a Python program that already
depends on pyTooling can directly access the schema file or its content.

.. grid:: 3

   .. grid-item::
      :columns: 6

      .. admonition:: Schema Path

         .. code-block:: python

            from pathlib                        import Path
            from pyTooling                      import Resources
            from pyTooling.Common               import getResourceFile
            from pyTooling.Testing.ReportWriter import SCHEMA_FILES, SCHEMA_VERSION_LATEST

            schemaPath: Path = getResourceFile(Resources, SCHEMA_FILES[SCHEMA_VERSION_LATEST])

   .. grid-item::
      :columns: 6

      .. admonition:: Schema Content

         .. code-block:: python

            from pathlib                        import Path
            from pyTooling                      import Resources
            from pyTooling.Common               import readResourceFile
            from pyTooling.Testing.ReportWriter import SCHEMA_FILES, SCHEMA_VERSION_LATEST

            schemaContent: str = readResourceFile(Resources, SCHEMA_FILES[SCHEMA_VERSION_LATEST])

.. _SCHEMAS/TestReport:

TestReport
**********

.. toctree::
   :maxdepth: 1

   TestReport-v0.1


.. _SCHEMAS/PackageOverrides:

PackageOverrides
****************

.. toctree::
   :maxdepth: 1

   PackageOverrides-v0.1
