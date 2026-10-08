.. _STRUCT/CallGraph:

Call Graph
##########

The :mod:`pyTooling.CallGraph` package describes the **call graph** of a program: its functions and the calls between
them. A :class:`~pyTooling.CallGraph.CallGraph` describes e.g. a program, a translation unit or a profiled run. A call
leads from the calling function to the called function, so a recursion is a cycle of the graph.

.. seealso::

   :ref:`STRUCT/ControlFlow`
      |rarr| The basic blocks of a function and the edges between them; a call is made from one of these blocks.

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: Example Call Graph:
.. mermaid::
   :caption: The call graph of a C program with the counts of a run. The call through a function pointer (dotted) is
             indirect, ``printf`` (rounded) is defined in a library.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph LR
     M["main"]; S["Sum"]; L["Leaf"]; F["Fib"]; A["Apply"]; P(["printf"])

     M -->|1| S -->|4| L
     M -->|1| F -->|14| F
     M -->|1| A -.->|1| L
     M -->|3| P

     classDef node fill:#eee,stroke:#777,font-size:smaller;

.. code-block:: C

   static int Leaf(int x) { return x * 2; }
   int Fib(int n) { return n < 2 ? n : Fib(n - 1) + Fib(n - 2); }
   typedef int (*Op)(int);
   int Apply(Op f, int x) { return f(x); }
   int Sum(int n) { int s = 0; for (int i = 0; i < n; i++) s += Leaf(i); return s; }
   int main(void) {
     printf("%d\n", Sum(4));
     printf("%d\n", Fib(5));
     printf("%d\n", Apply(Leaf, 3));
     return 0;
   }


.. _STRUCT/CallGraph/Features:

Features
********

* A function is looked up by its ID: :pycode:`graph["main"]` and :pycode:`"main" in graph`.
* Every function and every call has a kind, given as a :class:`~pyTooling.CallGraph.FunctionKind` or
  :class:`~pyTooling.CallGraph.CallKind` member.
* Functions and calls carry an optional execution count and an optional value of any type, e.g. a source location.
* A function can refer to its control flow graph, and a call to its call site: the block of that graph the call is made
  from.
* :meth:`~pyTooling.CallGraph.CallGraph.ToGraph` converts a call graph into a :class:`~pyTooling.Graph.Graph`, so it
  can be written as GraphML or Graphviz DOT, or analysed by the graph algorithms.


.. _STRUCT/CallGraph/RejectedFeatures:

Out of Scope
============

* Call paths and calling contexts: a call graph has one vertex per function, not one per path the function is reached
  through.
* Reading the output of compilers and profilers, and parsing source code or byte code into a call graph.


.. _STRUCT/CallGraph/Functions:

Functions
*********

A :class:`~pyTooling.CallGraph.Function` is identified by an ID unique within its graph, e.g. a qualified or a mangled
name. A function is created with the graph it belongs to:

.. code-block:: Python

   from pyTooling.CallGraph import CallGraph, Function, FunctionKind

   graph =    CallGraph("prog")
   main =     Function(graph, "main", count=1)
   apply =    Function(graph, "Apply", count=1)
   printf =   Function(graph, "printf", kind=FunctionKind.External)
   indirect = Function(graph, "__indirect_call", kind=FunctionKind.Unknown)

.. rubric:: Function kinds

+---------------------------------------------------+--------------------------------------------------------------+
| :class:`~pyTooling.CallGraph.FunctionKind`        | Meaning                                                      |
+===================================================+==============================================================+
| ``Defined``                                       | The function is defined in the described code, e.g. in the   |
|                                                   | translation unit or the profiled program.                    |
+---------------------------------------------------+--------------------------------------------------------------+
| ``External``                                      | The function is defined elsewhere, e.g. a library function   |
|                                                   | or a Python built-in function.                               |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Unknown``                                       | A placeholder for functions the source doesn't know, e.g.    |
|                                                   | the targets of an indirect call it couldn't resolve, or the  |
|                                                   | caller of a function called from outside.                    |
+---------------------------------------------------+--------------------------------------------------------------+


.. _STRUCT/CallGraph/Calls:

Calls
*****

A :class:`~pyTooling.CallGraph.Call` leads from the calling function to the called function. A function calling itself
is a call from and to the same function. Two functions can be connected by several calls, also of the same kind: a
compiler reports one per call site, a profiler one per pair of caller and callee.

.. code-block:: Python

   from pyTooling.CallGraph import Call, CallKind

   Call(main, printf, CallKind.Direct, value="prog.c:9:3")
   Call(main, printf, CallKind.Direct, value="prog.c:10:3")
   Call(main, apply, count=1)
   Call(apply, indirect, CallKind.Indirect)

.. rubric:: Call kinds

+---------------------------------------------------+--------------------------------------------------------------+
| :class:`~pyTooling.CallGraph.CallKind`            | Meaning                                                      |
+===================================================+==============================================================+
| ``Default``                                       | Not classified, e.g. a pair of caller and callee a profiler  |
|                                                   | reports.                                                     |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Direct``                                        | The call names its callee, e.g. a C function called by name. |
+---------------------------------------------------+--------------------------------------------------------------+
| ``Indirect``                                      | The callee is determined at run time, e.g. through a         |
|                                                   | function pointer or a virtual method.                        |
+---------------------------------------------------+--------------------------------------------------------------+


.. _STRUCT/CallGraph/CallSites:

Call Sites
==========

A function can refer to its :class:`~pyTooling.ControlFlow.ControlFlowGraph`. A call made by such a function can refer
to its call site: the :class:`~pyTooling.ControlFlow.BasicBlock` of the caller's control flow graph, which holds the
call. A block can hold several calls, e.g. both recursive calls of ``Fib``.

.. code-block:: Python

   from pyTooling.ControlFlow import ControlFlowGraph, BasicBlock

   cfg =   ControlFlowGraph("Fib", entryID=0, exitID=1)
   block = BasicBlock(cfg, 3, count=7, value="Fib(n - 1) + Fib(n - 2)")
   fib =   Function(graph, "Fib", controlFlow=cfg, count=15)

   Call(fib, fib, CallKind.Direct, callSite=block, count=7, value="Fib(n - 1)")
   Call(fib, fib, CallKind.Direct, callSite=block, count=7, value="Fib(n - 2)")


.. _STRUCT/CallGraph/Sources:

Sources
*******

* Profilers report the calls of a run with counts: Python's :mod:`cProfile` per function and per pair of caller and
  callee, gprof the same for a C program compiled with ``-pg``, valgrind's callgrind per call site.
* :mod:`sys.monitoring` reports every call with the caller's code object and the offset of the calling instruction,
  which lies in a block of the caller's control flow graph.
* Compilers report the calls a translation unit contains, without counts: GCC's ``-fcallgraph-info`` writes an edge per
  call site, declares functions defined elsewhere, and leads indirect calls to a placeholder.
* Code coverage reports, e.g. from gcov, count how often a function was called, but not by which caller.


.. _STRUCT/CallGraph/Conversion:

Conversion to a Graph
*********************

:meth:`~pyTooling.CallGraph.CallGraph.ToGraph` returns a :class:`~pyTooling.Graph.Graph` named like the call graph. A
function becomes a vertex, whose ID and value are the function's; a call becomes an edge from the caller to the callee,
whose kind and value are the call's. Vertices and edges carry these key-value pairs:

+---------------------------------------------------+--------------------------------------------------------------+
| Key                                               | Value                                                        |
+===================================================+==============================================================+
| ``kind``                                          | The function's :class:`~pyTooling.CallGraph.FunctionKind` or |
|                                                   | the call's :class:`~pyTooling.CallGraph.CallKind` member.    |
+---------------------------------------------------+--------------------------------------------------------------+
| ``count``                                         | The execution count; only if it is known.                    |
+---------------------------------------------------+--------------------------------------------------------------+
| ``callsite``                                      | On an edge, the ID of the call site's block; only if the     |
|                                                   | call site is known.                                          |
+---------------------------------------------------+--------------------------------------------------------------+

:mod:`pyTooling.Graph.GraphML` writes them as ``<data>`` elements; a kind is written by its name:

.. code-block:: Python

   from pathlib import Path
   from pyTooling.Graph.GraphML import GraphMLDocument

   document = GraphMLDocument()
   document.FromGraph(graph.ToGraph())
   document.WriteToFile(Path("prog.graphml"))

.. code-block:: XML

   <node id="printf">
     <data key="nodekind">External</data>
   </node>
   <edge source="Apply" target="Leaf">
     <data key="edgekind">Indirect</data>
     <data key="edgecount">1</data>
     <data key="edgecallsite">2</data>
   </edge>
