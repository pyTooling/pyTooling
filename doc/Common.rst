.. _COMMON:

Overview
########

.. _COMMON/CurrentPlatform:

Current Platform
****************

The module variable :py:data:`~pyTooling.Common.CurrentPlatform` contains a singleton instance of
:py:class:`~pyTooling.Common.Platform.Platform`, which abstracts and unifies multiple platform APIs of Python into a
single class instance.


.. _COMMON/HelperFunctions:

Helper Functions
****************

* The :py:func:`~pyTooling.Common.isnestedclass` functions returns true if a class is a nested class.


.. # ===================================================================================================================
   # CallByRef
   # ===================================================================================================================

.. _COMMON/CallByRef:

CallByRef
#########

The :py:mod:`pyTooling.CallByRef` package contains auxiliary classes to implement call by reference emulation for
function parameter handover. The callee gets enabled to return out-parameters for simple types like :py:class:`bool` and
:py:class:`int` to the caller.

.. admonition:: Python Background

   Python does not allow a user to distinguish between *call-by-value* and *call-by-reference*
   parameter passing. Python's standard types are passed by-value to a function or method.
   Instances of a class are passed by-reference (pointer) to a function or method.

By implementing a wrapper-class :py:class:`~pyTooling.CallByRef.CallByRefParam`, any type's value can be passed
by-reference. In addition, standard types like :py:class:`int` or :py:class:`bool` can be handled
by derived wrapper-classes.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.CallByRef
   :parts: 1

.. admonition:: Example

   .. code-block:: Python

      from pyTooling.CallByRef import CallByRefIntParam

      # define a call-by-reference parameter for integer values
      myInt = CallByRefIntParam(3)

      # a function using a call-by-reference parameter
      def func(param : CallByRefIntParam):
        param <<= param * 4

      # call the function and pass the wrapper object
      func(myInt)

      print(myInt.value)


CallByRefParam
**************

:py:class:`~pyTooling.CallByRef.CallByRefParam` implements a wrapper class for an arbitrary *call-by-reference*
parameter that can be passed to a function or method.

The parameter can be initialized via the constructor. If no init-value was given,
the init value will be ``None``. The wrappers internal value can be updated by
using the inplace shift-left operator ``<=``.

In addition, operators ``=`` and ``!=`` are also implemented for any *call-by-reference*
wrapper. Calls to ``__repr__`` and ``__str__`` are passed to the internal value.

The internal value can be used via ``obj.value``.


Type-Specific *call-by-reference* Classes
*****************************************

CallByRefBoolParam
==================

This is an implementation for the boolean type (:class:`bool`).


CallByRefIntParam
=================

This is an implementation for the integer type (:class:`int`).


.. # ===================================================================================================================
   # Licensing
   # ===================================================================================================================

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


.. # ===================================================================================================================
   # Platform
   # ===================================================================================================================

.. _COMMON/Platform:

Platform
########

This class gives detailed platform information about the environment the Python program or script is running in.

.. admonition:: Background Information

   Python has several ways in finding out what platform is running underneath of Python. Some information are provided
   via function calls, others are variables in a module. The :py:class:`~pyTooling.Common.Platform.Platform` class
   unifies all these APIs into a single class instance providing access to the platform and runtime information.
   Moreover, some (older) APIs do not reflect modern platforms like Python running in a MSYS2 MinGW64 environment on a
   Windows x86-64. By combining multiple APIs, it's possible to identify also such platforms.

   The internally used APIs are:

   * :py:func:`platform.machine`
   * :py:data:`sys.platform`
   * :py:func:`sysconfig.get_platform`

   These APIs are currently unused/not needed, because their information is already provided by the ones mentioned above:

   * :py:data:`os.name`
   * :py:func:`platform.system`
   * :py:func:`platform.architecture`


.. _COMMON/Platform/Architectures:

Architectures
*************

The architectures describes the native bit-width of addresses in a system. Thus, the maximum addressable memory space of
a CPU. E.g. a 32-bit architecture can address 4 GiB of main memory without memory segmentation.

.. rubric:: Supported Architectures

* x86_32
* x86_64

.. code:: python

   from pyTooling.Common import CurrentPlatform

   #
   CurrentPlatform.Architecture


.. _COMMON/Platform/NativePlatforms:

Native Platforms
****************

The native platform describes the hosting operating system.

.. rubric:: Supported Native Platforms

* Linux
* macOS
* Windows

.. code:: python

   from pyTooling.Common import CurrentPlatform

   # Check if the platform is a native platform
   CurrentPlatform.IsNativePlatform

   # Check for native Windows
   CurrentPlatform.IsNativeWindows

   # Check for native Linux
   CurrentPlatform.IsNativeLinux

   # Check for native macOS
   CurrentPlatform.IsNativeMacOS


.. _COMMON/Platform/Environments:

Environments
************

An environment is an additional layer installed on an operating system that provides a runtime environment to execute
Python. E.g. the ``MSYS2`` environment provides ``MinGW64`` to run Python in a Linux like POSIX environment, but on top
of Windows.

.. rubric:: Supported Environments

* MSYS2
* Cygwin

.. code:: python

   from pyTooling.Common import CurrentPlatform

   # Check if the environment is MSYS2
   CurrentPlatform.IsMSYS2Environment


.. _COMMON/Platform/Runtimes:

Runtimes
********

Some environments like ``MSYS2`` provide multiple runtimes.

.. rubric:: Supported (MSYS2) Runtimes

* MSYS
* MinGW32
* MinGW64
* UCRT64
* (CLang32)
* CLang64

.. code:: python

   from pyTooling.Common import CurrentPlatform

   # Check if the runtime is MSYS2 MinGW64 on a Windows machine
   CurrentPlatform.IsMinGW64OnWindows


.. # ===================================================================================================================
   # Versioning
   # ===================================================================================================================

.. _VERSIONING:

Versioning
##########

The :py:mod:`pyTooling.Versioning` package provides auxiliary classes to implement
`semantic <https://semver.org/>`__ and `calendar <https://calver.org/>`__ versioning.


.. _VERSIONING/SemVer:

Semantic Versioning
*******************

The :py:class:`~pyTooling.Versioning.SemVersion` class represents of a version number like ``v3.7.12``.

.. admonition:: Example

   .. code:: python

      # Construct from string
      version1 = SemVersion("0.22.8")

      # Construct from numbers
      version2 = SemVersion(1, 3, 0)

      # Compare versions
      isNewer = version2 > version1


.. hint::

   Given a version number ``MAJOR.MINOR.PATCH``, increment the:

   * ``MAJOR`` version when you make incompatible API changes,
   * ``MINOR`` version when you add functionality in a backwards compatible manner, and
   * ``PATCH`` version when you make backwards compatible bug fixes.
   * Additional labels for pre-release and build metadata are available as extensions to the ``MAJOR.MINOR.PATCH``
     format.

   Summary taken from `semver.org <https://semver.org/>`__.


.. _VERSIONING/SemVer/Features:

Features
========

* Major, minor, patch, build numbers
* Comparison operators
* Construct version number object from string or numbers.


.. _VERSIONING/SemVer/MissingFeatures:

Missing Features
----------------

* preserve prefix letter like ``v``, ``r``
* pre-version and post-version
* additional labels like ``dev``, ``rc``, ``pl``, ``alpha``



.. _VERSIONING/CalVer:

Calendar Versioning
*******************

The :py:class:`~pyTooling.Versioning.CalVersion` class represents of a version number like ``2021.10``.

.. admonition:: Example

   .. code:: python

      # Construct from string
      version1 = CalVersion("2018.3")
