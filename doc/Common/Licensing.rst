.. _LICENSING:

Licensing
#########

The :mod:`pyTooling.Licensing` package provides auxiliary classes to represent commonly known licenses and mappings
of their names, because some tools use differing names for the same license.

.. contents:: Table of Contents
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

.. code-block:: python

   @export
   class License(metaclass=ExtendedType, slots=True):
     def __init__(self, spdxIdentifier: str, name: str, osiApproved: bool = False, fsfApproved: bool = False) -> None:

      @property
      def Name(self) -> str:

      @property
      def SPDXIdentifier(self) -> str:

      @property
      def OSIApproved(self) -> bool:

      @property
      def FSFApproved(self) -> bool:

      @property
      def PythonLicenseName(self) -> str:

      @property
      def PythonClassifier(self) -> str:

      def __eq__(self, other: Any) -> bool:
      def __ne__(self, other: Any) -> bool:
      # def __le__(self, other: Any) -> bool:
      # def __ge__(self, other: Any) -> bool:

      def __repr__(self) -> str:
      def __str__(self) -> str:


The licenses supported by this package are available as individual package variables.

Package variables of predefined licenses:

* :data:`~pyTooling.Licensing.Apache_2_0_License`
* :data:`~pyTooling.Licensing.BSD_3_Clause_License`
* :data:`~pyTooling.Licensing.GPL_2_0_or_later`
* :data:`~pyTooling.Licensing.MIT_License`

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


.. _LICENSING/Mappings:

Mappings
********

:data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES` offers a Python specific mapping from SPDX identifier to license
names used by Python (setuptools). Each dictionary item contains a :class:`~pyTooling.Licensing.PythonLicenseNames`
instance which contains the license name and package classifier used by setuptools.

Currently the following licenses are listed in the Python specific name mapping:

* Apache-2.0
* BSD-3-Clause
* MIT
* GPL-2.0-or-later

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
