.. _STRUCT/ControlFlow:

Control Flow Graph
##################

The :mod:`pyTooling.ControlFlow` package describes the **control flow graph** of a function: its basic blocks and the
edges control takes between them. A :class:`~pyTooling.ControlFlow.ControlFlowGraph` describes one function - a C or
C++ function, or a Python code object. A call graph, connecting the graphs of several functions, is not part of it.

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Control Flow Graph:
.. mermaid::
   :caption: The control flow graph of a loop holding an ``if``/``else``, numbered like GCC numbers its blocks.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph TD
     E(["entry"]); X(["exit"])
     B2["2: s = 0; i = 0"]; B3{"3: i < n"}; B4{"4: i % 2"}
     B5["5: s += i"]; B6["6: s -= i"]; B7["7: i++"]; B8["8: return s"]

     E --> B2 --> B3
     B3 -->|FallThrough| B4
     B3 -->|Jump| B8 --> X
     B4 -->|FallThrough| B5 -->|Jump| B7
     B4 -->|Jump| B6 --> B7
     B7 -->|Jump| B3

     classDef node fill:#eee,stroke:#777,font-size:smaller;

.. code-block:: C

   int Sum(int n) {
     int s = 0;
     for (int i = 0; i < n; i++)
       if (i % 2) s += i; else s -= i;
     return s;
   }


.. _STRUCT/ControlFlow/Features:

Features
********

* A graph has an entry and an exit block, and optionally an unwind block, through which an exception leaves the
  function.
* A block is looked up by its ID: :pycode:`graph[3]` and :pycode:`3 in graph`.
* Every edge has a kind, given as an :class:`~pyTooling.ControlFlow.EdgeKind` member.
* Blocks and edges carry an optional execution count and an optional value of any type, e.g. source lines or a
  ``case`` label.
* :meth:`~pyTooling.ControlFlow.ControlFlowGraph.ToGraph` converts a control flow graph into a
  :class:`~pyTooling.Graph.Graph`, so it can be written as GraphML or Graphviz DOT, or analysed by the graph
  algorithms.


.. _STRUCT/ControlFlow/RejectedFeatures:

Out of Scope
============

* Call graphs and interprocedural edges from a call to the callee's entry: a call is part of a block.
* Parsing source code or byte code into a control flow graph.


.. _STRUCT/ControlFlow/Blocks:

Basic Blocks
************

A :class:`~pyTooling.ControlFlow.BasicBlock` is a sequence of code, which control enters at its top and leaves at its
bottom. Its ID is unique within its graph, e.g. a compiler's block number or a line number. A graph creates its entry
and exit block, with the IDs ``"entry"`` and ``"exit"`` unless others are given. Every further block is created with
the graph it belongs to:

.. code-block:: Python

   from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, BlockKind

   graph =  ControlFlowGraph("Sum", entryID=0, exitID=1)
   init =   BasicBlock(graph, 2, count=1, value="int s = 0;")
   unwind = BasicBlock(graph, "unwind", kind=BlockKind.Unwind)

.. rubric:: Block kinds

+---------------------------------------------------+--------------------------------------------------------------+
| :class:`~pyTooling.ControlFlow.BlockKind`         | Meaning                                                      |
+===================================================+==============================================================+
| ``Code``                                          | A block of code.                                             |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Entry``                                         | Control enters the function here. A graph has exactly one.   |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Exit``                                          | Control leaves the function here when it returns. A graph    |
|                                                   | has exactly one.                                             |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Unwind``                                        | An exception no handler of the function catches leaves the   |
|                                                   | function here. A graph has at most one.                      |
+---------------------------------------------------+--------------------------------------------------------------+


.. _STRUCT/ControlFlow/Edges:

Edges
*****

An :class:`~pyTooling.ControlFlow.Edge` leads from a block to a block control continues with. A block with several
outbound edges branches; a ``switch`` has an edge per target. Two blocks can be connected by edges of different kinds,
but only by one edge of each kind. No edge leads to the entry block, and none leaves the exit or unwind block.

.. rubric:: Edge kinds

+---------------------------------------------------+--------------------------------------------------------------+
| :class:`~pyTooling.ControlFlow.EdgeKind`          | Meaning                                                      |
+===================================================+==============================================================+
| ``Default``                                       | Not classified, e.g. an arc between two lines a code         |
|                                                   | coverage tool reports.                                       |
+---------------------------------------------------+--------------------------------------------------------------+
| ``FallThrough``                                   | Control continues with the next block in code order.         |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Jump``                                          | Control jumps: a taken branch, a ``goto``, ``break`` or      |
|                                                   | ``continue``, or a ``switch`` case.                          |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Exception``                                     | An exception leaves the block, to a handler or to the        |
|                                                   | unwind block.                                                |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Abnormal``                                      | Control leaves the block without a jump or an exception,     |
|                                                   | e.g. by calling ``exit()`` or ``longjmp()``.                 |
+---------------------------------------------------+--------------------------------------------------------------+


.. _STRUCT/ControlFlow/Exceptions:

Exceptions
==========

An exception is an ``Exception`` edge: to the block of the handler catching it, or - if no handler in the function
does - to the unwind block. A Python ``finally`` clause is a block on both paths: on the exceptional path, it ends with
an ``Exception`` edge, and a ``return`` inside it is an edge to the exit block.

.. code-block:: Python

   from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock, Edge, BlockKind, EdgeKind

   # def Read(path):
   #   try:
   #     data = load(path)
   #   except OSError:
   #     data = None
   #   finally:
   #     close()
   #   return data
   graph =   ControlFlowGraph("Read")
   body =    BasicBlock(graph, 3, value="data = load(path)")
   handler = BasicBlock(graph, 5, value="data = None")
   normal =  BasicBlock(graph, 7, value="close()")
   pending = BasicBlock(graph, 107, value="close()")
   ret =     BasicBlock(graph, 8, value="return data")
   unwind =  BasicBlock(graph, "unwind", kind=BlockKind.Unwind)

   Edge(graph.Entry, body, EdgeKind.FallThrough)
   Edge(body, normal, EdgeKind.FallThrough)
   Edge(body, handler, EdgeKind.Exception, value="OSError")
   Edge(body, pending, EdgeKind.Exception)
   Edge(handler, normal, EdgeKind.FallThrough)
   Edge(normal, ret, EdgeKind.FallThrough)
   Edge(ret, graph.Exit, EdgeKind.Jump)
   Edge(pending, unwind, EdgeKind.Exception)

A C++ ``throw`` is modelled the same way: an ``Exception`` edge to the ``catch`` block, or to the unwind block. A
destructor running while an exception passes is a cleanup block between the two.


.. _STRUCT/ControlFlow/Conversion:

Conversion to a Graph
*********************

:meth:`~pyTooling.ControlFlow.ControlFlowGraph.ToGraph` returns a :class:`~pyTooling.Graph.Graph` named like the
function. A block becomes a vertex, whose ID and value are the block's; an edge becomes an edge in the direction
control flows, whose kind and value are the edge's. Vertices and edges carry these key-value pairs:

+---------------------------------------------------+--------------------------------------------------------------+
| Key                                               | Value                                                        |
+===================================================+==============================================================+
| ``kind``                                          | The block's :class:`~pyTooling.ControlFlow.BlockKind` or the |
|                                                   | edge's :class:`~pyTooling.ControlFlow.EdgeKind` member.      |
+---------------------------------------------------+--------------------------------------------------------------+
| ``count``                                         | The execution count; only if it is known.                    |
+---------------------------------------------------+--------------------------------------------------------------+

:mod:`pyTooling.Graph.GraphML` writes them as ``<data>`` elements; a kind is written by its name:

.. code-block:: Python

   from pathlib import Path
   from pyTooling.Graph.GraphML import GraphMLDocument

   document = GraphMLDocument()
   document.FromGraph(graph.ToGraph())
   document.WriteToFile(Path("Read.graphml"))

.. code-block:: XML

   <node id="3">
     <data key="nodeValue">data = load(path)</data>
     <data key="nodekind">Code</data>
   </node>
   <edge source="3" target="5">
     <data key="edgeValue">OSError</data>
     <data key="edgekind">Exception</data>
   </edge>
