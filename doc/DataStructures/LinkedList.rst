.. _STRUCT/LinkedList:

LinkedList
##########

The :mod:`pyTooling.List` package

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Doubly Linked List:
.. mermaid::
   :caption: A linked list graph.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph TD
     A(Idle); B(Check); C(Prepare); D(Read); E(Finished); F(Write) ; G(Retry); H(WriteWait); I(ReadWait)

     A:::mark1 --> B --> C --> F
     F --> H --> E:::cur
     B --> G --> B
     G -.-> A --> C
     D -.-> A
     C ---> D --> I --> E -.-> A

     classDef node fill:#eee,stroke:#777,font-size:smaller;
     classDef cur fill:#9e9,stroke:#6e6;
     classDef mark1 fill:#69f,stroke:#37f,color:#eee;


.. rubric:: Doubly Linked List Properties:



.. _STRUCT/LinkedList/Features:

Features
********

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
