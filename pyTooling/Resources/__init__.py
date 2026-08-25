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

* :file:`TestReport.xsd` - the schema of :ref:`pyTooling's own test report format <TESTING/ReportFormat>`, which
  :mod:`pyTooling.Testing.ReportWriter` writes and every generated report points at.

.. rubric:: Usage

Two functions reach a resource file, and both work whether pyTooling is installed, inside a wheel, or a checkout:
:func:`~pyTooling.Common.getResourceFile` returns its **path**, for a consumer handing the file to another tool,
and :func:`~pyTooling.Common.readResourceFile` returns its **content**, for a consumer reading it directly.

.. admonition:: ``example.py``

   .. code-block:: python

      from pathlib          import Path
      from pyTooling        import Resources
      from pyTooling.Common import getResourceFile, readResourceFile

      schemaPath: Path = getResourceFile(Resources, "TestReport.xsd")
      schema:     str  = readResourceFile(Resources, "TestReport.xsd")
"""
