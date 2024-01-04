.. _STRUCT/Tree:

Tree
####

The :mod:`pyTooling.Tree` package provides fast and simple tree data structure based on a single
:class:`~pyTooling.Tree.Node` class.

.. hint::

   This tree data structure outperforms :gh:`anytree <c0fec0de/anytree>` by far and even :gh:`itertree <BR1py/itertree>`
   by factor of 2.

   Further alternatives:

   **treelib**
      :gh:`treelib <caesar0301/treelib>`

.. #contents:: Table of Contents
   :local:
   :depth: 3

.. rubric:: Example Tree:
.. mermaid::
   :caption: Root of the current node are marked in blue.

   %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
   graph TD
     R(Root)
     A(...)
     BL(Node); B(GrandParent); BR(Node)
     CL(Uncle); C(Parent); CR(Aunt)
     DL(Sibling); D(Node);  DR(Sibling)
     ELN1(Niece); ELN2(Nephew)
     EL(Child);   E(Child); ER(Child);
     ERN1(Niece);ERN2(Nephew)
     F1(GrandChild); F2(GrandChild)

     R:::mark1 --> A
     A --> BL & B & BR
     B --> CL & C & CR
     C --> DL & D & DR
     DL --> ELN1 & ELN2
     D:::cur --> EL & E & ER
     DR --> ERN1 & ERN2
     E --> F1 & F2

     classDef node fill:#eee,stroke:#777,font-size:smaller;
     classDef cur fill:#9e9,stroke:#6e6;
     classDef mark1 fill:#69f,stroke:#37f,color:#eee;

.. rubric:: Comprehensive Example:

The following example code demonstrates a few features in a compact form:

.. code-block:: python

   # Create a new tree by creating a root node (no parent reference)
   root = Node(value="OSVVM Regression Tests")

   # Construct the tree top-down
   lib = Node(value="Utility Library", parent=root)

   # Another standalone node with unique ID (actually an independent tree)
   common = Node(nodeID=5, value="Common")

   # Construct bottom-up
   axi = Node(value="AXI")
   axiCommon = Node(value="AXI4 Common")
   axi.AddChild(axiCommon)

   # Group nodes and handover children at node creation time
   vcList = [common, axi]
   vcs = Node(value="Verification Components", parent=root, children=vcList)

   # Add multiple nodes at once
   axiProtocols = (
     Node(value="AXI4-Stream"),
     Node(value="AXI4-Lite"),
     Node(value="AXI4")
   )
   axi.AddChildren(axiProtocols)

   # Create another standalone node and attache it later to a tree.
   uart = Node(value="UART")
   uart.Parent = vcs

The presented code will generate this tree:

.. code-block::

   OSVVM Regression Tests
   ├── Utility Library
   ├── Verification Components
       ├── Common
       ├── AXI
       │   ├── AXI4 Common
       │   ├── AXI4-Stream
       │   ├── AXI4-Lite
       │   ├── AXI4
       ├── UART


.. _STRUCT/Tree/Features:

Features
********

* Fast and simple tree data structure based on a single :class:`~pyTooling.Tree.Node` class.
* A tree can be constructed top-down and bottom-up.
* A node can have a unique ID.
* A node knows its level (distance from root).
* A node can have a value.
* A node can store key-value-pairs via dictionary syntax.
* A node has a reference to its parent node.
* A node has a reference to the root node in a tree (representative node).
* Rendering to simple ASCII art for debugging purposes.


.. _STRUCT/Tree/MissingFeatures:

Missing Features
================

* Insert a node (currently, only add/append is supported).
* Move a node in same hierarchy level.
* Move node to a different level/node in the same tree in a single operation.
* Allow node deletion.


.. _STRUCT/Tree/PlannedFeatures:

Planned Features
================

* Allow filters (predicates) in generators to allow node filtering.
* Tree export to formats like GraphML, ...
* Export the tree data structure to file the YAML format.
* Allow nodes to have tags and group nodes by tags.
* Allow nodes to link to other nodes (implement proxy behavior?)


.. _STRUCT/Tree/RejectedFeatures:

Out of Scope
============

* Preserve or recover the tree data structure before an erroneous operation caused an exception and aborted a tree
  modification, which might leave the tree in a corrupted state.
* Export the tree data structure to various file formats like JSON, TOML, ...
* Import a tree data structure from various file formats like JSON, YAML, TOML, ...
* Tree visualization or rendering to complex formats like GraphViz, Mermaid, ...


.. _STRUCT/Tree/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a node is strongly not recommended for users, as it might lead to a corrupted tree data
   structure. If a power-user wants to access these fields, feel free to use them for achieving a higher performance,
   but you got warned 😉.


.. _STRUCT/Tree/ID:

Unique ID
=========

A node can be created with a unique ID when the object is created. Afterwards, the :attr:`~pyTooling.Tree.Node.ID` is
a readonly property. Any hashable object can be used as an ID. The ID must be unique per tree. If trees are merged or
nodes are added to an existing tree, the newly added node's ID(s) are checked and might cause an exception.

.. code-block:: python

   # Create node with unique ID 5
   node = Node(nodeID=5)

   # Read a node's ID
   nodeID = node.ID


.. _STRUCT/Tree/Level:

Level
=====

Each node has a level describing the distance from :term:`root node <root>`. It can be accessed via the read-only
property :attr:`~pyTooling.Tree.Node.Level`.

The root node has a level of ``0``, children of root have a level of ``1``, and so on.

.. code-block:: python

   # Create node
   root = Node(nodeID=0)
   node2 = Node(nodeID=1, parent=root)

   # Read a node's level
   nodeLevel = node2.Level


.. _STRUCT/Tree/Value:

Value
=====

A node's value can be given at node creating time or it can be set ant any later time via property
:attr:`~pyTooling.Tree.Node.Value`. Any data type is accepted. The internally stored value can be retrieved by the
same property. If a node's string representation is requested via :meth:`~pyTooling.Tree.Node.__str__` and a node's
value isn't None, then the value's string representation is returned.

.. code-block:: python

   # Create node with value 5
   node = Node(value=5)

   # Set or change a node's value
   node.Value = 10

   # Access a node's Value
   value = node.Value


.. _STRUCT/Tree/KeyValuePairs:

Key-Value-Pairs
===============

Besides a :ref:`unique ID <STRUCT/Tree/ID>` and a :ref:`value <STRUCT/Tree/Value>`, each node can hold an arbitrary set
of key-value-pairs.

.. code-block:: python

   # Create node
   node = Node()

   # Create or update a key-value-pair
   node["key"] = value

   # Access a value by key
   value = node["key"]

   # Delete a key-value-pair
   del node["key"]


.. _STRUCT/Tree/Parent:

Parent Reference
================

Each node has a reference to its :term:`parent node <parent>`. In case, the node is the :term:`root node <root>`, the
parent reference is :data:`None`. The parent-child relation can be set at node creation time, or a parent can be assigned to a node at any later time via
property :attr:`~pyTooling.Tree.Node.Parent`. The same property can be used to retrieve the current parent reference.

.. code-block:: python

   # Create node without parent relation ship (root node)
   root = Node(nodeID=0)

   # Create a node add directly attach it to an existing tree
   node = Node(nodeID=1, parent=root)

   # Access a node's parent
   parent = node.Parent

Merging Trees
-------------

In case, two trees were created (a single node is already a minimal tree), trees get merged if one tree's root node is
assigned a parent relationship.

.. code-block:: python

   # Create a tree with a single node
   root = Node(nodeID=0)

   # Create a second minimalistic tree
   otherTree = Node(nodeID=100)

   # Set parent relationship and merge trees
   otherTree.Parent = root

.. seealso::

   See :ref:`STRUCT/Tree/Merging` for more details.

Splitting Trees
---------------

In case, a node within a tree's hierarchy is updated with respect to it's parent relationship to :data:`None`, then
the tree gets split into 2 trees.

.. code-block:: python

   # Create a tree of 4 nodes
   root1 = Node(nodeID=0)
   node1 = Node(nodeID=1, parent=root1)

   root2 = Node(nodeID=2, parent=node1)
   node3 = Node(nodeID=3, parent=root2)

   # Split the tree between node1 and root2
   root2.Parent = None

.. seealso::

   See :ref:`STRUCT/Tree/Splitting` for more details.

Moving a branch in same tree
----------------------------

.. todo:: TREE::Parent::move-branch in same tree - needs also testcases

Moving a branch to another tree
-------------------------------

.. todo:: TREE::Parent::move-branch into another tree - needs also testcases


.. _STRUCT/Tree/Root:

Root Reference
==============

Each node has a reference to the tree's :term:`root node <root>`. The root node can also be considered the
representative node of a tree and can be accessed via read-only property :attr:`~pyTooling.Tree.Node.Root`.

When a node is assigned a new parent relation and this parent is a node in another tree, the root reference will change.
(A.k.a. moving a branch to another tree.)

The root node of a tree contains tree-wide data structures like the list of unique IDs
(:attr:`~pyTooling.Tree.Node._nodesWithID`, :attr:`~pyTooling.Tree.Node._nodesWithoutID`). By utilizing the root
reference, each node can access these data structures by just one additional reference hop.

.. code-block:: python

   # Create a simple tree
   root = Node()
   nodeA = Node(parent=root)
   nodeB = Node(parent=root)

   # Check if nodeA and nodeB are in same tree
   isSameTree = nodeA is nodeB


.. _STRUCT/Tree/Path:

Path
====

The property :attr:`~pyTooling.Tree.Node.Path` returns a tuple describing the path top-down from root node to the
current node.

.. code-block:: python

   # Create a simple tree representing directories
   root = Node(value="C:")
   dir = Node(value="temp", parent=root)
   file = Node(value="test.log", parent=dir)

   # Convert a path to string
   path = "\".join(file.Path)

While the tuple returned by :attr:`~pyTooling.Tree.Node.Path` can be used in an iteration (e.g. a for-loop), also a
generator is provided by method :meth:`~pyTooling.Tree.Node.GetPath` for iterations.

.. code-block:: python

   # Create a simple tree representing directories
   root = Node(value="C:")
   dir = Node(value="temp", parent=root)
   file = Node(value="test.log", parent=dir)

   # Render path from root to node with indentations to ASCII art
   for level, node in enumerate(file.GetPath()):
     print(f"{'  '*level}'\-'{node}")

   # \-C:
   #   \-temp
   #     \-test.log


.. _STRUCT/Tree/Ancestors:

Ancestors
=========

The method :meth:`~pyTooling.Tree.Node.GetAncestors` returns a generator to traverse bottom-up from current node to
the root node. If the top-down direction is needed, see :ref:`STRUCT/Tree/Path` for more details.

+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                         | Diagram                                                                                                             |
+=====================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                      | .. mermaid::                                                                                                        |
| .. code-block:: python                              |                                                                                                                     |
|                                                     |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                         |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                     |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)        |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)        |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)        |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)        |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent) |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent) |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent) |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)      |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)      |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)     |      R:::mark1 --> A                                                                                                |
|    niece1 =      Node(nodeID=11, parent=sibling1)   |      A:::mark2 --> BL & B & BR                                                                                      |
|    nephew1 =     Node(nodeID=12, parent=sibling1)   |      B:::mark2 --> CL & C & CR                                                                                      |
|    child1 =      Node(nodeID=13, parent=me)         |      C:::mark2 --> DL & D & DR                                                                                      |
|    child2 =      Node(nodeID=14, parent=me)         |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)         |      D:::cur --> EL & E & ER                                                                                        |
|    niece2 =      Node(nodeID=16, parent=sibling2)   |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)   |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)     |                                                                                                                     |
|    grandChild2 = Node(nodeID=19, parent=child2)     |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                     |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                   |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                              |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                     |                                                                                                                     |
|    # Walk bottom-up all the way to root             |                                                                                                                     |
|    for node in me.GetAncestors():                   |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|                                                     |                                                                                                                     |
| .. rubric:: Result                                  |                                                                                                                     |
| .. code-block::                                     |                                                                                                                     |
|                                                     |                                                                                                                     |
|    6   # parent                                     |                                                                                                                     |
|    3   # grandparent                                |                                                                                                                     |
|    1   # ...                                        |                                                                                                                     |
|    0   # root                                       |                                                                                                                     |
+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/CommonAncestors:

Common Ancestors
----------------

If needed, method :meth:`~pyTooling.Tree.Node.GetCommonAncestors` provides a generator to iterate the common
ancestors of two nodes in a tree. It iterates from root node top-down until the common branch in the tree splits of.

+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                             | Diagram                                                                                                             |
+=========================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                          | .. mermaid::                                                                                                        |
| .. code-block:: python                                  |                                                                                                                     |
|                                                         |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                             |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                         |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)            |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)            |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)            |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)            |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent)     |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent)     |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent)     |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)          |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)          |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)         |      R:::mark1 --> A                                                                                                |
|    niece1 =      Node(nodeID=11, parent=sibling1)       |      A:::mark2 --> BL & B & BR                                                                                      |
|    nephew1 =     Node(nodeID=12, parent=sibling1)       |      B:::mark2 --> CL & C & CR                                                                                      |
|    child1 =      Node(nodeID=13, parent=me)             |      C:::mark2 --> DL & D & DR                                                                                      |
|    child2 =      Node(nodeID=14, parent=me)             |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)             |      D --> EL & E & ER                                                                                              |
|    niece2 =      Node(nodeID=16, parent=sibling2)       |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)       |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)         |      ELN2:::cur; F2:::cur                                                                                           |
|    grandChild2 = Node(nodeID=19, parent=child2)         |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                         |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                       |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                                  |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                         |                                                                                                                     |
|    # Walk bottom-up all the way to root                 |                                                                                                                     |
|    for node in nephew1.GetCommonAncestors(grandChild2): |                                                                                                                     |
|      print(node.ID)                                     |                                                                                                                     |
|                                                         |                                                                                                                     |
| .. rubric:: Result                                      |                                                                                                                     |
| .. code-block::                                         |                                                                                                                     |
|                                                         |                                                                                                                     |
|    0   # root                                           |                                                                                                                     |
|    1   # ...                                            |                                                                                                                     |
|    3   # grandparent                                    |                                                                                                                     |
|    6   # parent                                         |                                                                                                                     |
+---------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/Children:

Children
========

:term:`Children <Child>` are all direct successors of a :term:`node`.

A node object supports returning children either as a tuple via a property or as a generator via a method call.

+-------------------------------+-----------------------------------------------+--------------------------------------------------+
|                               | Return a Tuple                                | Return a Generator                               |
+===============================+===============================================+==================================================+
| Children                      | :attr:`~pyTooling.Tree.Node.Children`         | :meth:`~pyTooling.Tree.Node.GetChildren`         |
+-------------------------------+-----------------------------------------------+--------------------------------------------------+
| Children and children thereof | — — — —                                       | :meth:`~pyTooling.Tree.Node.GetDescendants`      |
+-------------------------------+-----------------------------------------------+--------------------------------------------------+

+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                         | Diagram                                                                                                             |
+=====================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                      | .. mermaid::                                                                                                        |
| .. code-block:: python                              |                                                                                                                     |
|                                                     |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                         |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                     |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)        |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)        |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)        |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)        |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent) |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent) |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent) |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)      |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)      |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)     |      R --> A                                                                                                        |
|    niece1 =      Node(nodeID=11, parent=sibling1)   |      A --> BL & B & BR                                                                                              |
|    nephew1 =     Node(nodeID=12, parent=sibling1)   |      B --> CL & C & CR                                                                                              |
|    child1 =      Node(nodeID=13, parent=me)         |      C --> DL & D & DR                                                                                              |
|    child2 =      Node(nodeID=14, parent=me)         |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)         |      D:::cur --> EL & E & ER                                                                                        |
|    niece2 =      Node(nodeID=16, parent=sibling2)   |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)   |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)     |      EL:::mark2; E:::mark2; ER:::mark2                                                                              |
|    grandChild2 = Node(nodeID=19, parent=child2)     |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                     |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                   |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                              |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                     |                                                                                                                     |
|    # Walk bottom-up all the way to root             |                                                                                                                     |
|    for node in me.GetChildren():                    |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|                                                     |                                                                                                                     |
| .. rubric:: Result                                  |                                                                                                                     |
| .. code-block::                                     |                                                                                                                     |
|                                                     |                                                                                                                     |
|    13  # child1                                     |                                                                                                                     |
|    14  # child2                                     |                                                                                                                     |
|    15  # child3                                     |                                                                                                                     |
+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/Descendants:

Descendants
===========

:term:`Descendants <Descendant>` are all direct and indirect successors of a :term:`node` (:term:`child nodes <child>`
and child nodes thereof a.k.a. :term:`grandchild`, grand-grandchildren, ...).

A node object supports returning descendants as a generator via a method call to :meth:`~pyTooling.Tree.Node.GetDescendants`,
due to the recursive behavior.

.. seealso::

   See :ref:`STRUCT/Tree/Iterating` for various other forms for iterating nodes in a tree.

+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                         | Diagram                                                                                                             |
+=====================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                      | .. mermaid::                                                                                                        |
| .. code-block:: python                              |                                                                                                                     |
|                                                     |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                         |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                     |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)        |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)        |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)        |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)        |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent) |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent) |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent) |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)      |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)      |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)     |      R --> A                                                                                                        |
|    niece1 =      Node(nodeID=11, parent=sibling1)   |      A --> BL & B & BR                                                                                              |
|    nephew1 =     Node(nodeID=12, parent=sibling1)   |      B --> CL & C & CR                                                                                              |
|    child1 =      Node(nodeID=13, parent=me)         |      C --> DL & D & DR                                                                                              |
|    child2 =      Node(nodeID=14, parent=me)         |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)         |      D:::cur --> EL & E & ER                                                                                        |
|    niece2 =      Node(nodeID=16, parent=sibling2)   |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)   |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)     |      EL:::mark2; E:::mark2; ER:::mark2; F1:::mark2; F2:::mark2                                                      |
|    grandChild2 = Node(nodeID=19, parent=child2)     |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                     |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                   |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                              |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                     |                                                                                                                     |
|    # Walk bottom-up all the way to root             |                                                                                                                     |
|    for node in me.GetDescendants():                 |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|                                                     |                                                                                                                     |
| .. rubric:: Result                                  |                                                                                                                     |
| .. code-block::                                     |                                                                                                                     |
|                                                     |                                                                                                                     |
|    13  # child1                                     |                                                                                                                     |
|    14  # child2                                     |                                                                                                                     |
|    18  # grandChild1                                |                                                                                                                     |
|    19  # grandChild2                                |                                                                                                                     |
|    15  # child3                                     |                                                                                                                     |
+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/Siblings:

Siblings
========

:term:`Siblings <Sibling>` are all direct :term:`child nodes <child>` of a node's :term:`parent` node except itself.

A node object supports returning siblings either as tuples via a property or as a generator via a method call. Either
all siblings are returned or just siblings left from the current node (left siblings) or right from the current node
(right siblings). Left and right is based on the order of child references in the current node's parent.

+-------------------+-----------------------------------------------+--------------------------------------------------+
| Sibling Selection | Return a Tuple                                | Return a Generator                               |
+===================+===============================================+==================================================+
| Left Siblings     | :attr:`~pyTooling.Tree.Node.LeftSiblings`     | :meth:`~pyTooling.Tree.Node.GetLeftSiblings`     |
+-------------------+-----------------------------------------------+--------------------------------------------------+
| All Siblings      | :attr:`~pyTooling.Tree.Node.Siblings`         | :meth:`~pyTooling.Tree.Node.GetSiblings`         |
+-------------------+-----------------------------------------------+--------------------------------------------------+
| Right Siblings    | :attr:`~pyTooling.Tree.Node.RightSiblings`    | :meth:`~pyTooling.Tree.Node.GetRightSiblings`    |
+-------------------+-----------------------------------------------+--------------------------------------------------+

.. attention::

   In case a node has no parent, an exception is raised, because siblings cannot exist.

+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                         | Diagram                                                                                                             |
+=====================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                      | .. mermaid::                                                                                                        |
| .. code-block:: python                              |                                                                                                                     |
|                                                     |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                         |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                     |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)        |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)        |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)        |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)        |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent) |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent) |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent) |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)      |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)      |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)     |      R --> A                                                                                                        |
|    niece1 =      Node(nodeID=11, parent=sibling1)   |      A --> BL & B & BR                                                                                              |
|    nephew1 =     Node(nodeID=12, parent=sibling1)   |      B --> CL & C & CR                                                                                              |
|    child1 =      Node(nodeID=13, parent=me)         |      C --> DL & D & DR                                                                                              |
|    child2 =      Node(nodeID=14, parent=me)         |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)         |      D:::cur --> EL & E & ER                                                                                        |
|    niece2 =      Node(nodeID=16, parent=sibling2)   |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)   |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)     |      DL:::mark2; DR:::mark2                                                                                         |
|    grandChild2 = Node(nodeID=19, parent=child2)     |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                     |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                   |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                              |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                     |                                                                                                                     |
|    # Walk bottom-up all the way to root             |                                                                                                                     |
|    for node in me.GetLeftSiblings():                |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|    for node in me.GetRightSiblings():               |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|                                                     |                                                                                                                     |
| .. rubric:: Result                                  |                                                                                                                     |
| .. code-block::                                     |                                                                                                                     |
|                                                     |                                                                                                                     |
|    8   # sibling1                                   |                                                                                                                     |
|    10  # sibling2                                   |                                                                                                                     |
+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/Relatives:

Relatives
=========

:term:`Relatives <Relative>` are :term:`siblings <sibling>` and their :term:`descendants <descendant>`.

A node object supports returning relatives as a generator via a method call, due to the recursive behavior. Either
all relatives are returned or just relatives left from the current node (left relatives) or right from the current node
(right relatives). Left and right is based on the order of child references in the current node's parent.

+--------------------+---------------------------------------------------+
| Relative Selection | Return a Generator                                |
+====================+===================================================+
| Left Siblings      | :meth:`~pyTooling.Tree.Node.GetLeftRelatives`     |
+--------------------+---------------------------------------------------+
| All Siblings       | :meth:`~pyTooling.Tree.Node.GetRelatives`         |
+--------------------+---------------------------------------------------+
| Right Siblings     | :meth:`~pyTooling.Tree.Node.GetRightRelatives`    |
+--------------------+---------------------------------------------------+

.. attention::

   In case a node has no parent, an exception is raised, because siblings and therefore relatives cannot exist.

+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
| Python Code                                         | Diagram                                                                                                             |
+=====================================================+=====================================================================================================================+
| .. rubric:: Tree Construction:                      | .. mermaid::                                                                                                        |
| .. code-block:: python                              |                                                                                                                     |
|                                                     |    %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%  |
|    # Create an example tree                         |    graph TD                                                                                                         |
|    root =        Node(nodeID=0)                     |      R(Root)                                                                                                        |
|    dots =        Node(nodeID=1, parent=root)        |      A(...)                                                                                                         |
|    node1 =       Node(nodeID=2, parent=dots)        |      BL(Node); B(GrandParent); BR(Node)                                                                             |
|    grandParent = Node(nodeID=3, parent=dots)        |      CL(Uncle); C(Parent); CR(Aunt)                                                                                 |
|    node2 =       Node(nodeID=4, parent=dots)        |      DL(Sibling); D(Node);  DR(Sibling)                                                                             |
|    uncle =       Node(nodeID=5, parent=grandParent) |      ELN1(Niece); ELN2(Nephew)                                                                                      |
|    parent =      Node(nodeID=6, parent=grandParent) |      EL(Child);   E(Child); ER(Child);                                                                              |
|    aunt =        Node(nodeID=7, parent=grandParent) |      ERN1(Niece);ERN2(Nephew)                                                                                       |
|    sibling1 =    Node(nodeID=8, parent=parent)      |      F1(GrandChild); F2(GrandChild)                                                                                 |
|    me =          Node(nodeID=9, parent=parent)      |                                                                                                                     |
|    sibling2 =    Node(nodeID=10, parent=parent)     |      R --> A                                                                                                        |
|    niece1 =      Node(nodeID=11, parent=sibling1)   |      A --> BL & B & BR                                                                                              |
|    nephew1 =     Node(nodeID=12, parent=sibling1)   |      B --> CL & C & CR                                                                                              |
|    child1 =      Node(nodeID=13, parent=me)         |      C --> DL & D & DR                                                                                              |
|    child2 =      Node(nodeID=14, parent=me)         |      DL --> ELN1 & ELN2                                                                                             |
|    child3 =      Node(nodeID=15, parent=me)         |      D:::cur --> EL & E & ER                                                                                        |
|    niece2 =      Node(nodeID=16, parent=sibling2)   |      DR --> ERN1 & ERN2                                                                                             |
|    nephew2 =     Node(nodeID=17, parent=sibling2)   |      E --> F1 & F2                                                                                                  |
|    grandChild1 = Node(nodeID=18, parent=child2)     |      DL:::mark2; ELN1:::mark2; ELN2:::mark2; DR:::mark2; ERN1:::mark2; ERN2:::mark2                                 |
|    grandChild2 = Node(nodeID=19, parent=child2)     |      classDef node fill:#eee,stroke:#777,font-size:smaller;                                                         |
|                                                     |      classDef cur fill:#9e9,stroke:#6e6;                                                                            |
| .. rubric:: Usage                                   |      classDef mark1 fill:#69f,stroke:#37f,color:#eee;                                                               |
| .. code-block:: python                              |      classDef mark2 fill:#69f,stroke:#37f;                                                                          |
|                                                     |                                                                                                                     |
|    # Walk bottom-up all the way to root             |                                                                                                                     |
|    for node in me.GetLeftRelatives():               |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|    for node in me.GetRightRelatives():              |                                                                                                                     |
|      print(node.ID)                                 |                                                                                                                     |
|                                                     |                                                                                                                     |
| .. rubric:: Result                                  |                                                                                                                     |
| .. code-block::                                     |                                                                                                                     |
|                                                     |                                                                                                                     |
|    8   # sibling1                                   |                                                                                                                     |
|    11  # niece1                                     |                                                                                                                     |
|    12  # nephew1                                    |                                                                                                                     |
|                                                     |                                                                                                                     |
|    10  # sibling2                                   |                                                                                                                     |
|    16  # niece2                                     |                                                                                                                     |
|    17  # nephew2                                    |                                                                                                                     |
+-----------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+


.. _STRUCT/Tree/Iterating:

Iterating a Tree
================

A tree (starting at the :term:`root node <root>`) or a subtree (starting at any node in the tree) can be iterated in
various orders:

* :meth:`~pyTooling.Tree.Node.IterateLeafs` - iterates only over leafs from left to right
* :meth:`~pyTooling.Tree.Node.IterateLevelOrder` - iterates all sub nodes level by level
* :meth:`~pyTooling.Tree.Node.IteratePreOrder` - iterates left to right and returns itself before its descendants
* :meth:`~pyTooling.Tree.Node.IteratePostOrder` - iterates left to right and returns its descendants before itself


.. _STRUCT/Tree/Merging:

Merging Trees
=============

A tree **B** is merged into an existing tree **A**, when a tree **B**'s parent relation is set to a non-:data:`None`
value. Therefore use the :attr:`B.Parent <pyTooling.Tree.Node.Parent>` property and set it to **A**:
:pycode:`B.Parent = A`.

The following operations are executed on the tree **B**:

1. register all nodes of **B** with and without ID in **A**, then
2. delete the list and dictionary objects for nodes with and without IDs from **B**.

The following operations are executed on all nodes in tree **B**:

* set root reference to **A**.
* recompute the level within **A**.

.. attention::

   In case a node's ID already exists in **A**, an exception is raised, because IDs are unique.


.. _STRUCT/Tree/Splitting:

Splitting Trees
===============

.. todo:: TREE: splitting a tree


.. _STRUCT/Tree/Rendering:

Tree Rendering
==============

The tree data structure can be rendered as ASCII art. The :meth:`~pyTooling.Tree.Node.Render` method renders the tree
into a multi line string.

.. todo:: TREE:Render:: explain parameters

.. admonition:: Example

   .. code-block::

      <Root 0>
      o-- <Node 1>
      |   o-- <Node 4>
      |   |   o-- <Node 8>
      |   |       o-- <Node 9>
      |   o-- <Node 5>
      |       o-- <Node 10>
      |           o-- <Node 11>
      |           o-- <Node 12>
      |           o-- <Node 13>
      o-- <Node 2>
      o-- <Node 3>
          o-- <Node 6>
          o-- <Node 7>


.. _STRUCT/Tree/Competitors:

Competing Solutions
*******************

This tree data structure outperforms :gh:`anytree <c0fec0de/anytree>` by far and even :gh:`itertree <BR1py/itertree>`
by factor of 2.

.. _STRUCT/Tree/anytree:

anytree
=======

Source: :gh:`anytree <c0fec0de/anytree>`

.. todo:: TREE::anytree write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...

.. code-block:: python

   # add code here


.. _STRUCT/Tree/itertree:

itertree
========

Source: :gh:`itertree <BR1py/itertree>`

.. todo:: TREE::itertree write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...

.. code-block:: python

   # add code here


.. _STRUCT/Tree/treelib:

treelib
=======

Source: :gh:`treelib <caesar0301/treelib>`

.. todo:: TREE::treelib write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...

.. code-block:: python

   # add code here


