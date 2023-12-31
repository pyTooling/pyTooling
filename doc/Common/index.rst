.. _COMMON:
.. _COMMON/HelperFunctions:

Common Helper Functions
#######################

The :mod:`pyTooling.Common` package contains several useful helper functions, which are explained in the following
sections.

.. contents:: Table of Contents
   :local:
   :depth: 1

.. _COMMON/Helper/getsizeof:

getsizeof
*********

The :func:`~pyTooling.Common.getsizeof` functions returns the "true" size of a Python object including auxiliary data
structures.

.. rubric:: Example:
.. code-block:: Python

   class A:
     _data : int

     def __init__(self) -> None:
       _data = 5

   from pyTooling.Common import getsizeof
   a = A()
   print(getsizeof(a))

.. rubric:: Details

In addition to :func:`sys.getsizeof`, the used algorithm accounts also for:

* ``__dict__``
* ``__slots__``
* iterable members made of:

  * :class:`tuple`
  * :class:`list`
  * :class:`typing.Set`
  * :class:`collection.deque`

.. admonition:: Background Information

   The function :func:`sys.getsizeof` only returns the raw size of a Python object and doesn't account for the
   overhead of e.g. ``_dict__`` to store dynamically allocated object members.


.. _COMMON/Helper/isnestedclass:

isnestedclass
*************

The :func:`~pyTooling.Common.isnestedclass` functions returns true, if a class is a nested class inside another
class.

.. rubric:: Example:
.. code-block:: Python

   class A:
     class N:
       _data : int

       def __init__(self) -> None:
         _data = 5

   N = A.N
   print(isnestedclass(N, A))


.. _COMMON/Helper/firstElement:

firstElement
************

:func:`~pyTooling.Common.firstElement` returns the first element from an iterable.

.. code-block:: Python

   lst = [1, 2, 3]

   f = firstElement(lst)
   # 1


.. _COMMON/Helper/lastElement:

lastElement
***********

:func:`~pyTooling.Common.lastElement` returns the last element from an iterable.

.. code-block:: Python

   lst = [1, 2, 3]

   l = lastElement(lst)
   # 3




.. _COMMON/Helper/firstItem:

firstItem
*********

:func:`~pyTooling.Common.firstItem` returns the first item from an iterable.

.. code-block:: Python

   lst = [1, 2, 3]

   f = firstItem(lst)
   # 1


.. _COMMON/Helper/lastItem:

lastItem
********

:func:`~pyTooling.Common.lastItem` returns the last item from an iterable.

.. code-block:: Python

   lst = [1, 2, 3]

   l = lastItem(lst)
   # 3


.. _COMMON/Helper/firstKey:

firstKey
********

:func:`~pyTooling.Common.firstKey` returns the first key from a dictionary.

.. code-block:: Python

   d = {}
   d["a"] = 1
   d["b"] = 2

   k = firstKey(d)
   # "a"

.. hint:: The dictionary should be an order preserving dictionary, otherwise the "first" item is not defined and can
   return any key.


.. _COMMON/Helper/firstValue:

firstValue
**********

:func:`~pyTooling.Common.firstValue` returns the first value from a dictionary.

.. code-block:: Python

   d = {}
   d["a"] = 1
   d["b"] = 2

   k = firstValue(d)
   # 1

.. hint:: The dictionary should be an order preserving dictionary, otherwise the "first" item is not defined and can
   return any value.


.. _COMMON/Helper/firstPair:

firstPair
*********

:func:`~pyTooling.Common.firstPair` returns the first pair (key-value-pair tuple) from a dictionary.

.. code-block:: Python

   d = {}
   d["a"] = 1
   d["b"] = 2

   k = firstPair(d)
   # ("a", 1)

.. hint:: The dictionary should be an order preserving dictionary, otherwise the "first" item is not defined and can
   return any pair.


.. _COMMON/Helper/mergedicts:

mergedicts
**********

:func:`~pyTooling.Common.mergedicts` merges multiple dictionaries into a new single dictionary. It accepts an
arbitrary number of dictionaries to merge. Optionally, the named parameter ``func`` accepts a function that can be
applied to every element during the merge operation.

.. rubric:: Example:
.. code-block:: Python

   dictA = {11: "11", 12: "12", 13: "13"}
   dictB = {21: "21", 22: "22", 23: "23"}

   mergedDict = mergedicts(dictA, dictB)
   # {11: "11", 12: "12", 13: "13", 21: "21", 22: "22", 23: "23"}

.. _COMMON/Helper/zipdicts:

zipdicts
********

:func:`~pyTooling.Common.zipdicts` is a generator that iterates multiple dictionaries simultaneously. It expects
multiple dictionary objects (fulfilling the mapping protocol) as positional parameters.

An exception is raised, if not all dictionary objects have the same number of items. Also an exception is raised, if a
key doesn't exist in all dictionaries.

.. rubric:: Example:
.. code-block:: Python

   dictA = {11: "11", 12: "12", 13: "13"}
   dictB = {11: "21", 12: "22", 13: "23"}

   for key, valueA, valueB in zipdicts(dictA, dictB):
     pass
