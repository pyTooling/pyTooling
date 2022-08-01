.. _LICENSING:

Licensing
#########

The :py:mod:`pyTooling.Licensing` package provides auxiliary classes to represent commonly known licenses.

.. admonition:: Background Information

   There are several names, identifiers and (Python package) classifiers referring to the same license. E.g. package
   classifiers used by setuptools and displayed by PIP/PyPI are different from SPDX identifiers and sometimes they are
   not even identical to the official license names. Also some allegedly similar licenses got different SPDX
   identifiers.

   The package :py:mod:`pyTooling.Licensing` provides license name and identifiers mappings to unify all these names and
   classifiers to and from `SPDX identifiers <https://spdx.org/licenses/>`__.

   .. rubric:: Examples

   +------------------+------------------------------+------------------+--------------------------------------------------------+
   | SDPX Identifier  | Official License Name        | License Name     | Python package classifier                              |
   +==================+==============================+==================+========================================================+
   | ``Apache-2.0``   | Apache License, Version 2.0  | ``Apache 2.0``   | ``License :: OSI Approved :: Apache Software License`` |
   +------------------+------------------------------+------------------+--------------------------------------------------------+
   | ``BSD-3-Clause`` | The 3-Clause BSD License     | ``BSD``          | ``License :: OSI Approved :: BSD License``             |
   +------------------+------------------------------+------------------+--------------------------------------------------------+

.. _LICENSING/Mappings:

Mappings
********

:py:data:`~pyTooling.Licensing.PYTHON_LICENSE_NAMES` offers a mapping from SPDX identifier to license names used by
Python (setuptools). Each dictionary item contains a :py:class:`~pyTooling.Licensing.PythonLicenseNames` instance which
contains the license name and package classifier used by setuptools.

Currently the following licenses are listed in the mapping:

* Apache-2.0
* BSD-3-Clause
* MIT
* GPL-2.0-or-later


.. _LICENSING/License:

License
*******

The :py:class:`~pyTooling.Licensing.License` class represents of a license like *Apache License, Version 2.0*
(SPDX: ``Apache-2.0``).

The licenses supported by the package are available as individual package variables and a dictionary
(:py:data:`~pyTooling.Licensing.SPDX_INDEX`) mapping from SPDX identified to :py:class:`~pyTooling.Licensing.License`
instances.

Package variables:

* :py:data:`~pyTooling.Licensing.Apache_2_0_License`
* :py:data:`~pyTooling.Licensing.BSD_3_Clause_License`
* :py:data:`~pyTooling.Licensing.GPL_2_0_or_later`
* :py:data:`~pyTooling.Licensing.MIT_License`

.. admonition:: Usage Example

   .. code:: python

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
