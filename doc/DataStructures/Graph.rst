.. _STRUCT/Graph:

Graph
#####

A **graph** data structure is represented by an instance of :py:class:`~pyTooling.Graph.Graph` holding references to all
nodes. Nodes are instances of :py:class:`~pyTooling.Graph.Vertex` classes and directed links between nodes are made of
:py:class:`~pyTooling.Graph.Edge` instances. A graph can have attached meta information as key-value pairs.

Graph algorithms using all vertexes are provided as methods on the graph instance. Whereas graph algorithms based on a
starting vertex are provided as methods on a vertex.

A **vertex** can have a unique ID, a value and attached meta information as key-value pairs. A vertex has references to
inbound and outbound edges, thus a graph can be traversed in reverse.

An **edge** can have a unique ID, a value, a weight and attached meta information as key-value pairs. All edges are
directed.

.. note::

   The data structure reaches similar performance as :gh:`NetworkX <networkx/networkx>`, while the API follows
   object-oriented-programming principles instead of procedural programming principles.


The following example code demonstrates a few features in a compact form:

.. code:: python

   # Create a new graph
   graph = Graph(name="Example Graph")



.. _STRUCT/Graph/Features:

Features
********



.. _STRUCT/Graph/MissingFeatures:

Missing Features
================



.. _STRUCT/Graph/PlannedFeatures:

Planned Features
================



.. _STRUCT/Graph/RejectedFeatures:

Out of Scope
============



.. _STRUCT/Graph/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a node is strongly not recommended for users, as it might lead to a corrupted tree data
   structure. If a power-user wants to access these fields, feel free to use them for achieving a higher performance,
   but you got warned 😉.


.. _STRUCT/Graph/ID:

Unique ID
=========




.. _STRUCT/Graph/Value:

Value
=====




.. _STRUCT/Graph/KeyValuePairs:

Key-Value-Pairs
===============


.. _STRUCT/Graph/Parent:

Parent Reference
================



.. _STRUCT/Graph/Root:

Root Reference
==============

