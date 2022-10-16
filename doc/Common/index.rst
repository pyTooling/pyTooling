.. _COMMON:
.. _COMMON/HelperFunctions:

Common Helper Functions
#######################

The :py:mod:`pyTooling.Common` package contains several useful helper functions, which are explained in the following
sections.

.. contents:: Table of Contents
   :local:
   :depth: 1

.. _COMMON/Helper/getsizeof:

getsizeof
*********

The :py:func:`~pyTooling.Common.getsizeof` functions returns the "true" size of a Python object including auxiliary data
structures.

.. rubric:: Example:
.. code-block:: Python

   class A:
     _data : int

     def __init__(self):
       _data = 5

   from pyTooling.Common import getsizeof
   a = A()
   print(getsizeof(a))

.. rubric:: Details

In addition to :py:func:`sys.getsizeof`, the used algorithm accounts also for:

* ``__dict__``
* ``__slots__``
* iterable members made of:

  * :py:class:`tuple`
  * :py:class:`list`
  * :py:class:`typing.Set`
  * :py:class:`collection.deque`

.. admonition:: Background Information

   The function :py:func:`sys.getsizeof` only returns the raw size of a Python object and doesn't account for the
   overhead of e.g. ``_dict__`` to store dynamically allocated object members.


.. _COMMON/Helper/isnestedclass:

isnestedclass
*************

The :py:func:`~pyTooling.Common.isnestedclass` functions returns true, if a class is a nested class inside another
class.

.. rubric:: Example:
.. code-block:: Python

   class A:
     class N:
       _data : int

       def __init__(self):
         _data = 5

   N = A.N
   print(isnestedclass(N, A))

.. _COMMON/Helper/mergedicts:

mergedicts
**********

:py:func:`~pyTooling.Common.mergedicts` merges multiple dictionaries into a new single dictionary. It accepts an
arbitrary number of dictionaries to merge. Optionally, the named parameter ``func`` accepts a function that can be
applied to every element during the merge operation.

.. rubric:: Example:
.. code-block:: Python

   dictA = {11: "11", 12: "12", 13: "13"}
   dictB = {21: "21", 22: "22", 23: "23"}

   mergedDict = mergedicts(dictA, dictB)


.. _COMMON/Helper/zipdicts:

zipdicts
********

:py:func:`~pyTooling.Common.zipdicts` is a generator that iterates multiple dictionaries simultaneously.

.. rubric:: Example:
.. code-block:: Python

   dictA = {11: "11", 12: "12", 13: "13"}
   dictB = {11: "21", 12: "22", 13: "23"}

   for key, valueA, valueB in zipdicts(dictA, dictB):
     pass
