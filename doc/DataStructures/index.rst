.. _STRUCT:

Overview
########

Currently, the following data structures are implemented:

* :ref:`STRUCT/Path/Generic`

  * :ref:`STRUCT/Path/URL`

* :ref:`STRUCT/Tree`

  +--------------------------------------------+-------------------------+
  | Python Code                                | Diagram                 |
  +============================================+=========================+
  | .. code-block:: python                     | .. mermaid::            |
  |                                            |                         |
  |    from pyTooling.Tree import Node         |    flowchart TD         |
  |                                            |      Root --> Dir1      |
  |    root = Node(id="Root")                  |      Root --> Dir2      |
  |    dir1 = Node(id="Dir1", parent=root)     |      Root --> File0     |
  |    dir2 = Node(id="Dir2", parent=root)     |      Root --> Dir3      |
  |    file0 = Node(id="File0", parent=root)   |                         |
  |    dir3 = Node(id="Dir3", parent=root)     |      Dir1 --> File1     |
  |    file1 = Node(id="File1", parent=dir1)   |      Dir1 --> File2     |
  |    file2 = Node(id="File2", parent=dir1)   |      Dir1 --> File3     |
  |    file3 = Node(id="File3", parent=dir1)   |      Dir2 --> File4     |
  |    file4 = Node(id="File3", parent=dir2)   |      Dir3 --> File5     |
  |    file5 = Node(id="File3", parent=dir3)   |      Dir3 --> File6     |
  |    file6 = Node(id="File3", parent=dir3)   |                         |
  +--------------------------------------------+-------------------------+


The following data structures are planned:

* :ref:`STRUCT/Graph`
