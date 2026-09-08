.. _SCHEMAS:

Overview
########

pyTooling ships the **schemas** of the file formats it writes and reads, so a consumer of such a file can validate
it without owning pyTooling. Each schema is listed here with its full source, ready to read, to copy, or to
download.

.. _SCHEMAS/Files:

Available schemas
*****************

.. list-table::
   :header-rows: 1
   :widths: 30 10 10 50

   * - Schema
     - Version
     - Language
     - Read or written by
   * - :ref:`TestReport <SCHEMAS/TestReport-v0.1>`
     - v0.1
     - XML
     - :mod:`pyTooling.Testing.ReportWriter`
   * - :ref:`PackageOverrides <SCHEMAS/PackageOverrides-v0.1>`
     - v0.1
     - JSON
     - :class:`pyTooling.Dependency.Python.LicenseOverrides`

.. _SCHEMAS/Versioning:

How a schema is versioned
*************************

**The file name carries the version**, so a new version of a format is added beside the old one rather than
replacing it: :file:`TestReport-v0.1.xsd` and, one day, :file:`TestReport-v0.2.xsd`.

How a document says which version it is written for depends on the format: a test report names its schema in the
``xsi:noNamespaceSchemaLocation`` attribute, while a package-override file states a bare ``version`` field. Either
way, the module owning the format maps a version to its schema file in a ``SCHEMA_FILES`` dictionary, and names
the newest in ``SCHEMA_VERSION_LATEST``.

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

      schemaPath: Path = getResourceFile(Resources, SCHEMA_FILES[str(SCHEMA_VERSION_LATEST)])

.. toctree::
   :hidden:

   TestReport-v0.1
   PackageOverrides-v0.1
