.. _STRUCT/StateMachine:

StateMachine
############

The :mod:`pyTooling.StateMachine` package

.. contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Statemachine:
.. #mermaid::
   :caption: A directed graph with backward-edges denoted by dotted vertex relations.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph LR
     A(A); B(B); C(C); D(D); E(E); F(F) ; G(G); H(H); I(I)

     A --> B --> E
     G --> F
     A --> C --> G --> H --> D
     D -.-> A
     D & F -.-> B
     I ---> E --> F --> D

     classDef node fill:#eee,stroke:#777,font-size:smaller;


.. rubric:: Statemachine Properties:



.. _STRUCT/StateMachine/Features:

Features
********

* TBD


.. _STRUCT/StateMachine/MissingFeatures:

Missing Features
================

* TBD



.. _STRUCT/StateMachine/PlannedFeatures:

Planned Features
================

* TBD



.. _STRUCT/StateMachine/RejectedFeatures:

Out of Scope
============




.. _STRUCT/StateMachine/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a statemachine, state or transition is strongly not recommended for users, as it might
   lead to a corrupted graph data structure. If a power-user wants to access these fields, feel free to use them for
   achieving a higher performance, but you got warned 😉.


.. _STRUCT/StateMachine/ID:

Unique ID
=========
