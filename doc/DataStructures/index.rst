.. _STRUCT:

Overview
########

Currently, the following data structures are implemented:

* :ref:`STRUCT/Path/Generic`

  * :ref:`STRUCT/Path/URL`

* :ref:`STRUCT/Graph`

  +--------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
  | Python Code                                            | Diagram                                                                                                             |
  +========================================================+=====================================================================================================================+
  | .. code-block:: python                                 | .. mermaid::                                                                                                        |
  |                                                        |    :caption: A directed graph with backward-edges denoted by dotted vertex relations.                               |
  |    from pyTooling.Graph import Graph                   |                                                                                                                     |
  |                                                        |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
  |    graph = Graph(name="Example Graph")                 |    graph LR                                                                                                         |
  |    rootA = Vertex(value="A", graph=graph)              |      A(A); B(B); C(C); D(D); E(E); F(F) ; G(G); H(H); I(I)                                                          |
  |    edgeAB = rootA.EdgeToNewVertex(vertexValue="B")     |                                                                                                                     |
  |    edgeAC = rootA.EdgeToNewVertex(vertexValue="C")     |      A --> B --> E                                                                                                  |
  |    vertexB = edgeAB.Destination                        |      G --> F                                                                                                        |
  |    vertexC = edgeAC.Destination                        |      A --> C --> G --> H --> D                                                                                      |
  |    vertexD = Vertex(value="D", graph=graph)            |      D -.-> A                                                                                                       |
  |    vertexE = Vertex(value="E", graph=graph)            |      D & F -.-> B                                                                                                   |
  |    vertexF = Vertex(value="F", graph=graph)            |      I ---> E --> F --> D                                                                                           |
  |    vertexG = Vertex(value="G", graph=graph)            |                                                                                                                     |
  |    vertexB.EdgeTo(vertexE)                             |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
  |    vertexC.EdgeTo(vertexG)                             |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
  |    vertexD.LinkTo(rootA)                               |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
  +--------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+

* :ref:`STRUCT/Tree`

  +--------------------------------------------+----------------------------------------------------------------------------+
  | Python Code                                | Diagram                                                                    |
  +============================================+============================================================================+
  | .. code-block:: python                     | .. mermaid::                                                               |
  |                                            |    :caption: A tree representing a directory structure.                    |
  |    from pyTooling.Tree import Node         |                                                                            |
  |                                            |    flowchart TD                                                            |
  |    root = Node(id="Root")                  |      Root --> Dir1                                                         |
  |                                            |      Root --> Dir2                                                         |
  |    dir1 = Node(id="Dir1", parent=root)     |      Root --> File0                                                        |
  |    dir2 = Node(id="Dir2", parent=root)     |      Root --> Dir3                                                         |
  |    file0 = Node(id="File0", parent=root)   |                                                                            |
  |    dir3 = Node(id="Dir3", parent=root)     |      Dir1 --> File1                                                        |
  |                                            |      Dir1 --> File2                                                        |
  |    file1 = Node(id="File1", parent=dir1)   |      Dir1 --> File3                                                        |
  |    file2 = Node(id="File2", parent=dir1)   |                                                                            |
  |    file3 = Node(id="File3", parent=dir1)   |      Dir2 --> File4                                                        |
  |                                            |                                                                            |
  |    file4 = Node(id="File4", parent=dir2)   |      Dir3 --> File5                                                        |
  |                                            |      Dir3 --> File6                                                        |
  |    file5 = Node(id="File5", parent=dir3)   |                                                                            |
  |    file6 = Node(id="File6", parent=dir3)   |                                                                            |
  +--------------------------------------------+----------------------------------------------------------------------------+

The following data structures are planned:

* :ref:`STRUCT/StateMachine`
