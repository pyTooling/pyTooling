.. _COMMON:

Overview
########

.. _COMMON/CurrentPlatform:

Current Platform
****************

The module variable :py:data:`~pyTooling.Common.CurrentPlatform` contains a singleton instance of
:py:class:`~pyTooling.Common.Platform.Platform`, which abstracts and unifies multiple platform APIs of Python into a
single class instance.

.. rubric:: Example

.. admonition:: example.py

   .. code-block:: python

      from pyTooling.Common import CurrentPlatform

      # Check for a native Linux platform
      if CurrentPlatform.IsNativeLinux:
        pass

.. admonition:: unittest.py

   .. code-block:: python

      from pyTooling.Common import CurrentPlatform

      class MyTestCase(TestCase):
        @mark.skipif(not CurrentPlatform.IsMinGW64OnWindows, reason="Skipped when platform isn't MinGW64.")
        def test_OnMinGW64(self) -> None:
          pass

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

   :py:class:`~pyTooling.Common.Platform.Platform`
     |rarr| ``Is...`` properties describing a platform (and environment) the current Python program is running on.


.. _COMMON/HelperFunctions:

Helper Functions
****************

* The :py:func:`~pyTooling.Common.isnestedclass` functions returns true, if a class is a nested class inside another
  class.
* The :py:func:`~pyTooling.Common.getsizeof` functions returns the "true" size of a Python object including auxillary
  data structures like ``_dict__``.
