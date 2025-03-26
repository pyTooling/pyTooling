.. _STRUCT/LinkedList:

Doubly Linked List
##################

The :mod:`pyTooling.LinkedList` package ...

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Doubly Linked List:
.. mermaid::
   :caption: A linked list graph.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph LR
     LL(LinkedList); A(Node 0); B(Node 1); C(Node 2); D(Node 3); E(Node 4)

     LL:::mark1 --> A
     LL --> E
     A <--> B <--> C <--> D <--> E

     classDef node fill:#eee,stroke:#777,font-size:smaller;
     classDef cur fill:#9e9,stroke:#6e6;
     classDef mark1 fill:#69f,stroke:#37f,color:#eee;


.. rubric:: Doubly Linked List Properties:

* The LinkedList counts the number of elements.
* The LinkedList has a reference to the first and last element in the doubly linked list.
* Each Node has a linked to its previous Node and its next Node (doubly linked).
* Each Node has a link to its LinkedList.
* Each Node has a value.
* Operations can be performed in the LinkedList or on any Node.
* The LinkedList can be iterated in ascending and descending order.
* The list can be iterated starting from any Node.

.. _STRUCT/LinkedList/Features:

Features
********

* Insert operations can be performed in the LinkedList or on any Node.
* Remove operations can be performed in the LinkedList or on any Node.
* The LinkedList can be iterated in ascending and descending order.
* The LinkedList can be cleared.


* TBD



.. _STRUCT/LinkedList/MissingFeatures:

Missing Features
================

* TBD



.. _STRUCT/LinkedList/PlannedFeatures:

Planned Features
================

* TBD



.. _STRUCT/LinkedList/RejectedFeatures:

Out of Scope
============

* TBD



.. _STRUCT/LinkedList/ByProperty:

By Property
***********

Linked List Properties
======================

* is empty
* count
* first
* last

Node Properties
===============

* Previous
* Next
* Value
* List


.. _STRUCT/LinkedList/ByOperation:

By Operation
************

.. danger::

   Accessing internal fields of a doubly linked list or node is strongly not recommended for users, as it might lead to
   a corrupted data structure. If a power-user wants to access these fields, feel free to use them for achieving a
   higher performance, but you got warned 😉.


.. _STRUCT/LinkedList/Instantiation:

Instantiation
=============

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyTooling.LinkedList.LinkedList` can be instantiated as an empty list without any aditional parameters.
      It will report via property :attr:`LinkedList.IsEmpty <pyTooling.LinkedList.LinkedList.IsEmpty>` as empty and
      report zero elements via property :attr:`LinkedList.Count <pyTooling.LinkedList.LinkedList.Count>`.

      Alternatively, it can be constructed from an iterable like a :class:`tuple`, :class:`list` or any Python iterator.
      The order of the iterable is preserved.

      The time complexity is `O(n)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Initialize an empty LinkedList

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Inititialize LinkedList from tuple

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               initTuple = (1, 2, 3, 4, 5)

               ll = LinkedList(initTuple)


Clear
=====

.. grid:: 2

   .. grid-item::
      :columns: 6

      The :class:`~pyTooling.LinkedList.LinkedList` can be cleared by calling the
      :meth:`LinkedList.Clear <pyTooling.LinkedList.LinkedList.Clear>` method. Afterwards, the linked list reports as
      empty and a count of zero.

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Clearing a LinkedList

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

Insert
======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertAtBegin <pyTooling.LinkedList.LinkedList.InsertAtBegin>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Insert before first element

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Insert after last element

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Insert before current element

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Insert after current element

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Insert at position

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Remove
======

* at begin
* at end
* current node

Iterate
=======

* from begin
* from end
* from node forward
* from node backward

Sort
====

* sort ascending
* sort descending

Reverse
=======

Search
======

search node with value

Convert
=======

* to tuple
* to list

Item Access
===========

* get value
* set value
* del value
