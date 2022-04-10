.. _STRUCT:

Overview
########

Currently, the following data structures are implemented:

* :ref:`STRUCT/Tree`

  .. |diagram| mermaid::

     flowchart TD
       Root --> Dir1
       Root --> Dir2
       Root --> File0
       Root --> Dir3

       Dir1 --> File1
       Dir1 --> File2
       Dir1 --> File3
       Dir2 --> File4
       Dir3 --> File5
       Dir3 --> File6

  .. |code| code-block:: python

     from pyTooling.Tree import Node

     root = Node(id="Root")
     dir1 = Node(id="Dir1", parent=root)
     dir2 = Node(id="Dir2", parent=root)
     file0 = Node(id="File0", parent=root)
     dir3 = Node(id="Dir3", parent=root)
     file1 = Node(id="File1", parent=dir1)
     file2 = Node(id="File2", parent=dir1)
     file3 = Node(id="File3", parent=dir1)
     file4 = Node(id="File3", parent=dir2)
     file5 = Node(id="File3", parent=dir3)
     file6 = Node(id="File3", parent=dir3)

  +--------+-----------+
  | Code   | Diagramm  |
  +========+===========+
  | |code| | |diagram| |
  +--------+-----------+

The following data structures are planned:

* :ref:`STRUCT/Graph`
