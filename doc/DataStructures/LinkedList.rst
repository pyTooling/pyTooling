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

* PreviousNode
* NextNode
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

      The :class:`~pyTooling.LinkedList.LinkedList` can be instantiated as an empty linked list without any aditional
      parameters. It will report as empty via property :attr:`LinkedList.IsEmpty <pyTooling.LinkedList.LinkedList.IsEmpty>`
      and report zero elements via property :attr:`LinkedList.Count <pyTooling.LinkedList.LinkedList.Count>`.

      Alternatively, it can be constructed from an iterable like a :class:`tuple`, :class:`list` or any Python iterator.
      The order of the iterable is preserved.

      The time complexity is `O(n)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Empty LinkedList

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList


               ll = LinkedList()

               ll.IsEmpty
               # => True
               ll.Count
               # => 0

         .. tab-item:: LinkedList from tuple

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               ll.IsEmpty
               # => False
               ll.Count
               # => 5


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

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               ll.Clear()

               ll.IsEmpty
               # => False
               ll.Count
               # => 5

Insert
======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions into the linked list can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>` or after the last element
      using :meth:`LinkedList.InsertAfterLast <pyTooling.LinkedList.LinkedList.InsertAfterLast>`

      Additionally, if there is a reference to a specific node of the linked list, insertions before and after that node
      are also very efficient. The methods are :meth:`LinkedList.InsertNodeBefore <pyTooling.LinkedList.Node.InsertNodeBefore>`
      and :meth:`LinkedList.InsertNodeAfter <pyTooling.LinkedList.Node.InsertNodeAfter>`.

      The time complexity is `O(1)`.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Before first node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               newNode = Node(0)
               ll.InsertBeforeFirst(newNode)

         .. tab-item:: After last node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               newNode = Node(6)
               ll.InsertAfterLast(newNode)

         .. tab-item:: Before current node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               node = ll[2]

               newNode = Node(2.5)
               node.InsertNodeBefore(newNode)

         .. tab-item:: After current node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               node = ll[2]

               newNode = Node(3.5)
               node.InsertNodeAfter(newNode)


Random Access Insert
====================

.. grid:: 2

   .. grid-item::
      :columns: 6

      Inserting a new node at a random postion is less efficient then direct inserts at the first or last element of the
      linked list or before and after a specific node. The additional effort comes from walking the linked list to find
      the n-th element. Then an efficient insert is performed.

      The linked list is walked from the shorter end.

      The time complexity is `O(n/2)`.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Before first n-th node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               newNode = Node(2.5)
               ll.InsertNodeBefore(2, newNode)

         .. tab-item:: Before after n-th node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList, Node

               initTuple = (1, 2, 3, 4, 5)
               ll = LinkedList(initTuple)

               newNode = Node(3.5)
               ll.InsertNodeAfter(2, newNode)

Remove
======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: First node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Last node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Current node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: At position

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: By predicate

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Iterate
=======


.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Forward from first node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Backward from last node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Forward from current node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Backward from current node

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Sort
====


.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Ascending

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Descending

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Reverse
=======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Reverse

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

Search
======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: By predicate

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Convert
=======

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: To tuple

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: To list

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


Item Access
===========

.. grid:: 2

   .. grid-item::
      :columns: 6

      A new :class:`~pyTooling.LinkedList.Node` can be inserted into the linked list at any position.

      Very fast insertions can be achieved before the the first element using
      :meth:`LinkedList.InsertBeforeFirst <pyTooling.LinkedList.LinkedList.InsertBeforeFirst>`

      The time complexity is `O(1)`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Get value

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Set value

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()

         .. tab-item:: Delete value

            .. code-block:: Python

               from pyTooling.LinkedList import LinkedList

               ll = LinkedList()


.. _STRUCT/LinkedList/Competitors:

Competing Solutions
*******************

:mod:`pyTooling.LinkedList` is written in Python and isn't faster than a list implemented in C. Its elements are node
objects: a :class:`~pyTooling.LinkedList.Node` knows its list, its neighbours, its value and a key, and an element is
inserted or removed next to a node by a method of that node, e.g. :meth:`~pyTooling.LinkedList.Node.InsertNodeAfter`
or :meth:`~pyTooling.LinkedList.Node.Remove`. A list is searched by a predicate
(:meth:`~pyTooling.LinkedList.LinkedList.Search`), sorted stably (:meth:`~pyTooling.LinkedList.LinkedList.Sort`) and
reversed in place (:meth:`~pyTooling.LinkedList.LinkedList.Reverse`).

.. _STRUCT/LinkedList/deque:

deque and list
==============

Source: :class:`collections.deque` and :class:`list` of the standard library.

.. rubric:: Disadvantages

* There are no node objects. An element is addressed by its index or found by its value, so inserting or removing
  next to a known element first searches for it.

.. rubric:: Standoff

* Both are generic in type annotations (``deque[int]``), as :class:`~pyTooling.LinkedList.LinkedList` is.

.. rubric:: Advantages

* Implemented in C and part of Python, so nothing has to be installed.
* :class:`~collections.deque` appends and pops at both ends in constant time, can be bounded (``maxlen``) and rotated;
  a :class:`list` accesses any index in constant time.

.. _STRUCT/LinkedList/llist:

llist
=====

Source: :gh:`llist <ajakubek/python-llist>`, on PyPI as `llist <https://pypi.org/project/llist/>`__ (0.7.1,
released 2021-04-26). Its pure Python variant is :gh:`pypy-llist <rgsoda/pypy-llist>`, on PyPI as
`pyllist <https://pypi.org/project/pyllist/>`__ (0.3, released 2017-11-18).

.. rubric:: Disadvantages

* No release since 2021, and PyPI holds a source distribution only, so installing it compiles a C extension.

.. rubric:: Standoff

* Node objects, as here: a ``dllistnode`` has ``prev``, ``next``, ``value`` and its list as ``owner``, and
  ``insertbefore``/``insertafter`` insert next to a node.

.. rubric:: Advantages

* A C extension, which according to its documentation is faster than :class:`~collections.deque` and :class:`list`
  when elements are inserted and removed in the middle of a sequence.
* A singly linked list (``sllist``) as well.
