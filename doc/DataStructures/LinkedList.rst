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



.. _STRUCT/LinkedList/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a doubly linked list or node is strongly not recommended for users, as it might lead to
   a corrupted data structure. If a power-user wants to access these fields, feel free to use them for achieving a
   higher performance, but you got warned 😉.


.. _STRUCT/LinkedList/ID:

Unique ID
=========
