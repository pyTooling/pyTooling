.. _COMMON/Platform:

Platform
########

The :class:`~pyTooling.Common.Platform.Platform` class gives detailed platform information about the environment the
Python program or script is running in.

.. contents:: Table of Contents
   :local:
   :depth: 1

.. admonition:: Background Information

   Python has several ways in finding out what platform is running underneath of Python. Some information are provided
   via function calls, others are variables in a module. The :class:`~pyTooling.Common.Platform.Platform` class
   unifies all these APIs into a single class instance providing access to the platform and runtime information.
   Moreover, some (older) APIs do not reflect modern platforms like Python running in a MSYS2 MinGW64 environment on a
   Windows x86-64. By combining multiple APIs, it's possible to identify also such platforms.

   The internally used APIs are:

   * :func:`platform.machine`
   * :data:`sys.platform`
   * :func:`sysconfig.get_platform`

   These APIs are currently unused/not needed, because their information is already provided by the ones mentioned above:

   * :data:`os.name`
   * :func:`platform.system`
   * :func:`platform.architecture`


.. _COMMON/CurrentPlatform:

Current Platform
****************

The module variable :data:`pyTooling.Common.CurrentPlatform` contains a singleton instance of
:class:`~pyTooling.Common.Platform.Platform`, which abstracts and unifies multiple platform APIs of Python into a
single class instance.

.. rubric:: Supported platforms

* Native

  * Linux (x86-64)
  * macOS (x86-64)
  * Windows (x86-64)

* MSYS2 (on Windows)

  * MSYS
  * Clang64
  * MinGW32
  * MinGW64
  * UCRT64

* Cygwin

.. seealso::

   :class:`~pyTooling.Common.Platform.Platform`
     |rarr| ``Is...`` properties describing a platform (and environment) the current Python program is running on.


.. _COMMON/CurrentPlatform/Usecases:

Usecase: Platform Specific Code
===============================

.. rubric:: Example:

.. admonition:: example.py

   .. code-block:: python

      from pyTooling.Common import CurrentPlatform

      # Check for a native Linux platform
      if CurrentPlatform.IsNativeLinux:
        pass

Usecase: Platform Specific Tests
================================

.. admonition:: unittest.py

   .. code-block:: python

      from pyTooling.Common import CurrentPlatform

      class MyTestCase(TestCase):
        @mark.skipif(not CurrentPlatform.IsMinGW64OnWindows, reason="Skipped when platform isn't MinGW64.")
        def test_OnMinGW64(self) -> None:
          pass


.. _COMMON/Platform/Architectures:

Architectures
*************

The architectures describes the native bit-width of addresses in a system. Thus, the maximum addressable memory space of
a CPU. E.g. a 32-bit architecture can address 4 GiB of main memory without memory segmentation.

.. rubric:: Supported Architectures

* x86_32
* x86_64

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

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

.. code-block:: python

   from pyTooling.Common import CurrentPlatform

   # Check if the runtime is MSYS2 MinGW64 on a Windows machine
   CurrentPlatform.IsMinGW64OnWindows
