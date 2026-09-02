.. _LICENSING:

Licensing
#########

The :mod:`pyTooling.Licensing` package provides auxiliary classes to represent commonly known licenses and mappings
of their names, because some tools use differing names for the same license.

.. #contents:: Table of Contents
   :local:
   :depth: 1

.. admonition:: Background Information

   There are several names, identifiers and (Python package) classifiers referring to the same license. E.g. package
   classifiers used by setuptools and displayed by PIP/PyPI are different from SPDX identifiers and sometimes they are
   not even identical to the official license names. Also some allegedly similar licenses got different SPDX
   identifiers.

   The package :mod:`pyTooling.Licensing` provides license name and identifiers mappings to unify all these names and
   classifiers to and from `SPDX identifiers <https://spdx.org/licenses/>`__.

   .. rubric:: Examples:

   +------------------+------------------------------+--------------------------+--------------------------------------------------------+
   | SDPX Identifier  | Official License Name        | License (short) Name     | Python package classifier                              |
   +==================+==============================+==========================+========================================================+
   | ``Apache-2.0``   | Apache License, Version 2.0  | ``Apache 2.0``           | ``License :: OSI Approved :: Apache Software License`` |
   +------------------+------------------------------+--------------------------+--------------------------------------------------------+
   | ``BSD-3-Clause`` | The 3-Clause BSD License     | ``BSD``                  | ``License :: OSI Approved :: BSD License``             |
   +------------------+------------------------------+--------------------------+--------------------------------------------------------+

.. _LICENSING/License:

Licenses
********

The :class:`~pyTooling.Licensing.License` class represents of a license like *Apache License, Version 2.0*
(SPDX: ``Apache-2.0``). It offers several information about a license as properties. Licenses can be compared for
equality (``==``, ``!=``) based on there SPDX identifier.

**Condensed definition of class** :class:`~pyTooling.Licensing.License`:

.. condensed-class:: pyTooling.Licensing.License


The licenses supported by this package are available as individual package variables.

Package variables of predefined licenses, grouped by family:

.. list-table::
   :header-rows: 1
   :widths: 30 30 40

   * - Permissive
     - Weak copyleft
     - Strong copyleft
   * - | :data:`~pyTooling.Licensing.Apache_2_0_License`
       | :data:`~pyTooling.Licensing.BSD_2_Clause_License`
       | :data:`~pyTooling.Licensing.BSD_3_Clause_License`
       | :data:`~pyTooling.Licensing.MIT_License`
       | :data:`~pyTooling.Licensing.ISC_License`
       | :data:`~pyTooling.Licensing.BSL_1_0_License`
       | :data:`~pyTooling.Licensing.Zlib_License`
       | :data:`~pyTooling.Licensing.PSF_2_0_License`
     - | :data:`~pyTooling.Licensing.MPL_2_0_License`
       | :data:`~pyTooling.Licensing.EPL_1_0_License`
       | :data:`~pyTooling.Licensing.EPL_2_0_License`
       | :data:`~pyTooling.Licensing.LGPL_2_1_only`
       | :data:`~pyTooling.Licensing.LGPL_2_1_or_later`
       | :data:`~pyTooling.Licensing.LGPL_3_0_only`
       | :data:`~pyTooling.Licensing.LGPL_3_0_or_later`
     - | :data:`~pyTooling.Licensing.GPL_2_0_only`
       | :data:`~pyTooling.Licensing.GPL_2_0_or_later`
       | :data:`~pyTooling.Licensing.GPL_3_0_only`
       | :data:`~pyTooling.Licensing.GPL_3_0_or_later`
       | :data:`~pyTooling.Licensing.AGPL_3_0_only`
       | :data:`~pyTooling.Licensing.AGPL_3_0_or_later`

Public domain dedications and waivers: :data:`~pyTooling.Licensing.Unlicense` and
:data:`~pyTooling.Licensing.CC0_1_0`.

.. note::

   :data:`~pyTooling.Licensing.CC0_1_0` is the one predefined license that is **not** OSI-approved, so its
   classifier is ``License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication`` without the
   ``OSI Approved ::`` prefix. :attr:`~pyTooling.Licensing.License.OSIApproved` says so.

.. hint::

   The ``-only`` and ``-or-later`` pairs are SPDX's replacement for the old ``+`` suffix, and PyPI has a separate
   classifier for each - ``GNU General Public License v3 (GPLv3)`` versus ``... v3 or later (GPLv3+)``. Picking the
   wrong one of a pair states a different license, so they are separate variables rather than one with a flag.

:data:`~pyTooling.Licensing.SPDX_INDEX` maps every SPDX identifier above to its license.

.. code-block:: python

   from pyTooling.Licensing import Apache_2_0_License

   license = Apache_2_0_License
   print(f"Python classifier: {license.PythonClassifier}")
   print(f"SPDX:              {license.SPDXIdentifier}")
   # Python classifier: License :: OSI Approved :: Apache Software License
   # SPDX:              Apache-2.0

.. #
   * :data:`~pyTooling.Licensing.Apache_2_0_License`
   * :data:`~pyTooling.Licensing.Artistic_License`
   * :data:`~pyTooling.Licensing.BSD_3_Clause_License`
   * :data:`~pyTooling.Licensing.BSD_4_Clause_License`
   * :data:`~pyTooling.Licensing.CreativeCommons_CC0_1_0`
   * :data:`~pyTooling.Licensing.CreativeCommons_CCBY_4_0`
   * :data:`~pyTooling.Licensing.CreativeCommons_CCBYSA_4_0`
   * :data:`~pyTooling.Licensing.EclipsePublicLicense_2_0`
   * :data:`~pyTooling.Licensing.GNU_AfferoGeneralPublicLicense_3_0`
   * :data:`~pyTooling.Licensing.GNU_GeneralPublicLicense_2_0_or_later`
   * :data:`~pyTooling.Licensing.GNU_GeneralPublicLicense_3_0_or_later`
   * :data:`~pyTooling.Licensing.GNU_LesserGeneralPublicLicense_3_0_or_later`
   * :data:`~pyTooling.Licensing.MicrosoftPublicLicense`
   * :data:`~pyTooling.Licensing.MIT_License`
   * :data:`~pyTooling.Licensing.MozillaPublicLicense_2_0`

In addition a dictionary (:data:`~pyTooling.Licensing.SPDX_INDEX`) maps from SPDX identified to
:class:`~pyTooling.Licensing.License` instances.

.. code-block:: python

   from pyTooling.License import SPDX_INDEX

   licenseName = "MIT"
   license = SPDX_INDEX[licenseName]
   print(f"Python classifier: {license.PythonClassifier}")
   print(f"SPDX:              {license.SPDXIdentifier}")
   # Python classifier: License :: OSI Approved :: MIT License
   # SPDX:              MIT


.. _LICENSING/URLs:

Where a license is published
****************************

Every license carries two links to its text, so a report can point at the wording rather than only naming it.

:attr:`~pyTooling.Licensing.License.SPDXURL` is **derived** from the SPDX identifier, because SPDX publishes one page
per identifier at a fixed address. :attr:`~pyTooling.Licensing.License.OSIURL` is **looked up** in
:data:`~pyTooling.Licensing.OSI_LICENSE_URLS`, because OSI's addresses don't follow the identifier.

.. code-block:: python

   from pyTooling.Licensing import MIT_License, GPL_2_0_only, CC0_1_0

   print(MIT_License.SPDXURL)     # https://spdx.org/licenses/MIT.html
   print(MIT_License.OSIURL)      # https://opensource.org/license/mit
   print(GPL_2_0_only.OSIURL)     # https://opensource.org/license/gpl-2.0
   print(CC0_1_0.OSIURL)          # None - not OSI-approved

.. note::

   Two identifiers can share one OSI page. ``GPL-2.0-only`` and ``GPL-2.0-or-later`` both point at
   ``gpl-2.0``, because *only* versus *or later* is SPDX's distinction and not OSI's. ``PSF-2.0`` is published by OSI
   as ``Python-2.0``, which is why the addresses are a table and not a rule.

   :attr:`~pyTooling.Licensing.License.OSIURL` is ``None`` exactly when
   :attr:`~pyTooling.Licensing.License.OSIApproved` is ``False``.

.. seealso::

   `SPDX License List <https://spdx.org/licenses/>`__
      |rarr| Every SPDX identifier, with its full name and license text.
   `OSI License List <https://opensource.org/licenses>`__
      |rarr| Every license the Open Source Initiative has approved.

.. _LICENSING/Mappings:

Mappings
********

:data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES` offers a Python specific mapping from SPDX identifier to license
names used by Python (setuptools). Each dictionary item contains a :class:`~pyTooling.Licensing.PythonLicenseNames`
instance which contains the license name and package classifier used by setuptools.

Every predefined license is listed in that mapping - the same 23 SPDX identifiers
:data:`~pyTooling.Licensing.LICENSES` holds. :data:`~pyTooling.Licensing.LICENSES_BY_CLASSIFIER` is the inverse, from
a Python classifier back to the licenses it can mean; it is one-to-one except for
``License :: OSI Approved :: BSD License``, which names either
:data:`~pyTooling.Licensing.BSD_2_Clause_License` or :data:`~pyTooling.Licensing.BSD_3_Clause_License`.

.. _LICENSING/Usage:

Usage with Setuptools
*********************

The following examples demonstrates the usage with setuptools in a ``setup.py``.

.. admonition:: Usage Example

   .. code-block:: python

      from setuptools import setup
      from pyTooling.Licensing import Apache_2_0_License

      classifiers = [
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only"
      ]

      license = Apache_2_0_License
      classifiers.append(license.PythonClassifier)

      # Assemble other parameters
      # ...

      # Handover to setuptools
      setup(
        # ...
        license=license.SPDXIdentifier,
        # ...
        classifiers=classifiers,
        # ...
      )
