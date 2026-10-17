.. _STRUCT/DataModel:

Data Model Foundations
######################

The :mod:`pyTooling.DataModel` package holds building blocks the classes of a data model share.

.. contents:: Table of Contents
   :local:
   :depth: 2


.. _STRUCT/DataModel/KeyValuePairs:

Key-Value-Pairs
***************

An element of a data model often carries data its model doesn't know: the results of an analysis, or what only one
service reports. :class:`~pyTooling.DataModel.KeyValuePairsMixin` attaches arbitrary key-value-pairs to an element,
accessed like a dictionary. A key is any :class:`~typing.Hashable` object.

.. code-block:: Python

   element["runner.os"] = "Linux"   # create or update a pair
   os = element["runner.os"]        # read a value; KeyError if the key doesn't exist
   del element["runner.os"]         # remove a pair; KeyError if the key doesn't exist
   if "runner.os" in element: ...   # check for a key
   count = len(element)             # number of pairs
   for key in element: ...          # the keys, in the order they were added

The constructor takes the initial pairs as a mapping and copies them. Anything but a mapping - e.g. a list of pairs -
is rejected with a :exc:`TypeError`.

The mixin is used in one of two ways:

* :class:`~pyTooling.DataModel.BaseWithKeyValuePairs` is the slotted, abstract base-class of a data model, whose
  elements all carry key-value-pairs. The mixin's field becomes a slot of this class.

  .. code-block:: Python

     from pyTooling.DataModel import BaseWithKeyValuePairs

     class Element(BaseWithKeyValuePairs):
       _name: str

       def __init__(self, name: str, keyValuePairs: Nullable[Mapping[Hashable, Any]] = None) -> None:
         super().__init__(keyValuePairs)
         self._name = name

* A class with a base-class of its own adds the :class:`~pyTooling.DataModel.KeyValuePairsMixin` as a further
  base-class and calls its initializer.

  .. code-block:: Python

     from pyTooling.DataModel import KeyValuePairsMixin

     class Node(Base, KeyValuePairsMixin):
       def __init__(self, keyValuePairs: Nullable[Mapping[Hashable, Any]] = None) -> None:
         super().__init__()
         KeyValuePairsMixin.__init__(self, keyValuePairs)

The elements of :mod:`pyTooling.CI` and :mod:`pyTooling.ControlFlow` derive from
:class:`~pyTooling.DataModel.BaseWithKeyValuePairs`.
