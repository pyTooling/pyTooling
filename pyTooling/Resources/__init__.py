# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ ___  ___  ___  _   _ _ __ ___ ___  ___                           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) / _ \/ __|/ _ \| | | | '__/ __/ _ \/ __|                          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  _ <  __/\__ \ (_) | |_| | | | (_|  __/\__ \                          #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_| \_\___||___/\___/ \__,_|_|  \___\___||___/                          #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
"""
A resource package holding the data files shipped with pyTooling.

It is one package for the whole library rather than one per sub-package, so a consumer looking for a schema has a
single place to look and a file can be shared by more than one module.

.. rubric:: XML Schema Files

* :file:`TestReport-v0.1.xsd` - the schema of :ref:`pyTooling's own test report format <TESTING/ReportFormat>`,
  which :mod:`pyTooling.Testing.ReportWriter` writes and every generated report points at. The file name carries
  the format's version, so a later version is added beside it rather than replacing it.

.. rubric:: JSON Schema Files

* :file:`PackageOverrides-v0.1.json` - the schema of the package-override file the
  :ref:`dependency-table <DEP>` directive reads, which
  :class:`~pyTooling.Dependency.Python.LicenseOverrides` parses. Like the XSD above, the file name carries the
  structure's version, and :attr:`~pyTooling.Dependency.Python.LicenseOverrides.SCHEMA_FILES` maps a version to
  its file.

  An editor validates the file while it is being written when the YAML names the schema on its first line. In a
  checkout, a relative path needs nothing published:

  .. code-block:: YAML

     # yaml-language-server: $schema=../pyTooling/Resources/PackageOverrides-v0.1.json

  For a consumer *outside* a checkout, the schema is served at its ``$id`` under the published documentation:

  .. code-block:: YAML

     # yaml-language-server: $schema=https://pyTooling.GitHub.io/pyTooling/schema/PackageOverrides-v0.1.json

  :file:`doc/conf.py` publishes it through Sphinx' ``html_extra_path``, which copies a file to the output root
  untouched - so the URL is fixed by the schema's own name and does not move when the documentation's page
  structure does. The copy is taken from this package rather than kept beside :file:`conf.py`, so the published
  file is always the one the wheel ships.

.. rubric:: Usage

Two functions reach a resource file, and both work whether pyTooling is installed, inside a wheel, or a checkout:
:func:`~pyTooling.Common.getResourceFile` returns its **path**, for a consumer handing the file to another tool,
and :func:`~pyTooling.Common.readResourceFile` returns its **content**, for a consumer reading it directly.

.. admonition:: ``example.py``

   .. code-block:: python

      from pathlib          import Path
      from pyTooling        import Resources
      from pyTooling.Common import getResourceFile, readResourceFile

      schemaPath:    Path = getResourceFile(Resources, "TestReport-v0.1.xsd")
      schemaContent: str  = readResourceFile(Resources, "TestReport-v0.1.xsd")
"""
