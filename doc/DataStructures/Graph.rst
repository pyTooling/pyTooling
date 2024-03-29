.. _STRUCT/Graph:

Graph
#####

The :mod:`pyTooling.Graph` package provides a directed graph data structure. Compared to
:ref:`NetworkX <STRUCT/Graph/NetworkX>` and :ref:`igraph <STRUCT/Graph/igraph>`, this implementation provides an
object-oriented API.

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Graph:
.. mermaid::
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


.. rubric:: Graph Properties:

A **graph** data structure is represented by an instance of :class:`~pyTooling.Graph.Graph` holding references to all
nodes. Nodes are instances of :class:`~pyTooling.Graph.Vertex` classes and directed links between nodes are made of
:class:`~pyTooling.Graph.Edge` instances. A graph can have attached meta information as key-value pairs.

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

.. code-block:: python

   # Create a new graph
   graph = Graph(name="Example Graph")



.. _STRUCT/Graph/Features:

Features
********

* Fast and powerful graph data structure.
* Operations on vertexes following directed edges.
* Operations on whole graph.
* A vertex and an edge can have a unique ID.
* A vertex and an edge can have a value.
* A graph, vertex and an edge can store key-value-pairs via dictionary syntax.
* A vertex knows its inbound and outbound edges.
* An edge can have a weight.


.. _STRUCT/Graph/MissingFeatures:

Missing Features
================

* TBD

.. _STRUCT/Graph/PlannedFeatures:

Planned Features
================

* TBD

.. _STRUCT/Graph/RejectedFeatures:

Out of Scope
============

* Preserve or recover the graph data structure before an erroneous operation caused an exception and aborted a graph
  modification, which might leave the graph in a corrupted state.
* Export the graph data structure to various file formats like JSON, YAML, TOML, ...
* Import a graph data structure from various file formats like JSON, YAML, TOML, ...
* Graph visualization or rendering to complex formats like GraphML, GraphViz, Mermaid, ...


.. _STRUCT/Graph/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a graph, vertex or edge is strongly not recommended for users, as it might lead to a
   corrupted graph data structure. If a power-user wants to access these fields, feel free to use them for achieving a
   higher performance, but you got warned 😉.


.. _STRUCT/Graph/ID:

Unique ID
=========

A vertex can be created with a unique ID when the object is created. Afterwards, the :attr:`~pyTooling.Graph.Vertex.ID`
is a readonly property. Any hashable object can be used as an ID. The ID must be unique per graph. If graphs are merged
or vertexes are added to an existing graph, the newly added graph's ID(s) are checked and might cause an exception.

Also edges can be created with a unique ID when the object is created. Afterwards, the :attr:`~pyTooling.Graph.Edge.ID`
is a readonly property. Any hashable object can be used as an ID. The ID must be unique per graph. If graphs are merged
or vertexes are added to an existing graph, the newly added graph's ID(s) are checked and might cause an exception.

.. code-block:: python

   # Create vertex with unique ID 5
   graph = Graph()
   vertex = Vertex(vertexID=5, graph=graph)

   # Read a vertex's ID
   vertexID = vertex.ID


.. _STRUCT/Graph/Value:

Value
=====

A vertex's value can be given at vertex creating time or it can be set ant any later time via property
:attr:`~pyTooling.Graph.Vertex.Value`. Any data type is accepted. The internally stored value can be retrieved by
the same property. If a vertex's string representation is requested via :meth:`~pyTooling.Graph.Vertex.__str__` and a
vertex's value isn't None, then the value's string representation is returned.

.. todo:: GRAPH: setting / getting an edge's values

.. code-block:: python

   # Create vertex with unique ID 5
   graph = Graph()
   vertex = Vertex(value=5, graph=graph)

   # Set or change a node's value
   vertex.Value = 10

   # Access a vertex's Value
   value = vertex.Value


.. _STRUCT/Graph/KeyValuePairs:

Key-Value-Pairs
===============

.. todo:: GRAPH: setting / getting a vertex's KVPs

.. todo:: GRAPH: setting / getting an edge's KVPs

.. _STRUCT/Graph/Inbound:

Inbound Edges
=============

.. todo:: GRAPH: inbound edges


.. _STRUCT/Graph/Outbound:

Outbound Edges
==============

.. todo:: GRAPH: outbound edges



.. _STRUCT/Graph/GraphRef:

Graph Reference
===============

.. todo:: GRAPH: reference to the graph


.. _STRUCT/Graph/Competitors:

Competing Solutions
*******************

Compared to :gh:`NetworkX <networkx/networkx>` and :gh:`igraph <igraph/python-igraph>`, this implementation provides an
object-oriented API.

.. _STRUCT/Graph/NetworkX:

NetworkX
========

.. rubric:: Disadvantages

* Many operations are executed on the graph, but not on vertex/node objects or edge objects.
* Algorithms are provided as functions instead of methods.
* Vertices are created implicitly.
* ...

.. rubric:: Standoff

* Arbitrary data can be attached to edges.
* ...

.. rubric:: Advantages

* A huge variety of algorithms is provided.
* ...

.. code-block:: python

   import networkx as nx
   G = nx.Graph()
   G.add_edge("A", "B", weight=4)
   G.add_edge("B", "D", weight=2)
   G.add_edge("A", "C", weight=3)
   G.add_edge("C", "D", weight=4)
   nx.shortest_path(G, "A", "D", weight="weight")


.. _STRUCT/Graph/igraph:

igraph
======

.. todo:: GRAPH::igraph write example and demonstrate missing OOP API.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...

.. code-block:: python

   # add code here
