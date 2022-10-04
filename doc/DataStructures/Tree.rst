.. _STRUCT/Tree:

Tree
####

The :py:mod:`pyTooling.Tree` package provides fast and simple tree data structure based on a single
:py:class:`~pyTooling.Tree.Node` class, which outperforms :gh:`anytree <c0fec0de/anytree>` and
:gh:`itertree <BR1py/itertree>`.

.. contents:: Table of Contents
   :local:
   :depth: 2

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

* Fast and simple tree data structure based on a single :py:class:`~pyTooling.Tree.Node` class.
* A tree can be constructed top-down and bottom-up.
* A node can have a unique ID.
* A node can have a value.
* A node can store key-value-pairs via dictionary syntax.
* A node has a reference to its parent node.
* Each node has a reference to the root node in a tree (representative node).

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

* Rendering to simple ASCII art for debugging purposes.
* Allow filters (predicates) in generators to allow node filtering.
* Allow nodes to have tags and group nodes by tags.
* Allow nodes to link to other nodes (implement proxy behavior?)


.. _STRUCT/Tree/RejectedFeatures:

Out of Scope
============

* Preserve or recover the tree data structure before an erroneous operation caused an exception and aborted a tree
  modification, which might leave the tree in a corrupted state.
* Export the tree data structure to various file formats like JSON, YAML, TOML, ...
* Import a tree data structure from various file formats like JSON, YAML, TOML, ...
* Tree visualization or rendering to complex formats like GraphML, GraphViz, Mermaid, ...


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

A node can be created with a unique ID when the object is created. Afterwards, the :py:attr:`~pyTooling.Tree.Node.ID` is
a readonly property. Any hashable object can be used as an ID. The ID must be unique per tree. If trees are merged or
nodes are added to an existing tree, the newly added node's ID(s) are checked and might cause an exception.

.. code-block:: python

   # Create node with unique ID 5
   node = Node(nodeID=5)

   # Read a node's ID
   nodeID = node.ID


.. _STRUCT/Tree/Value:

Value
=====

A node's value can be given at node creating time or it can be set ant any later time via property
:py:attr:`~pyTooling.Tree.Node.Value`. Any data type is accepted. The internally stored value can be retrieved by the
same property. If a node's string representation is requested via :py:meth:`~pyTooling.Tree.Node.__str__` and a node's
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

.. todo:: TREE: setting / getting a node's KVPs

.. _STRUCT/Tree/Parent:

Parent Reference
================

Each node has a reference to its parent node. In case, the node is the root node, the parent reference is None. The
parent-child relation can be set at node creation time, or a parent can be assigned to a node at any later time via
property :py:attr:`~pyTooling.Tree.Node.Parent`. The same property can be used to retrieve the current parent reference.

.. code-block:: python

   # Create node without parent relation ship (root node)
   root = Node(nodeID=0)

   # Create a node add directly attach it to an existing tree
   node = Node(nodeID=1, parent=root)

   # Access a node's parent
   parent = node.Parent

In case, two trees were created (a single node is already a minimal tree), trees get merged if one tree's root node is
assigned a parent relationship.

.. code-block:: python

   # Create a tree with a single node
   root = Node(nodeID=0)

   # Create a second minimalistic tree
   otherTree = Node(nodeID=100)

   # Set parent relationship and merge trees
   otherTree.Parent = root


.. _STRUCT/Tree/Root:

Root Reference
==============

Each node has a reference to the tree's root node. The root node can also be considered the representative node of a
tree and can be accessed via read-only property :py:attr:`~pyTooling.Tree.Node.Root`.

When a node is assigned a new parent relation and this parent a node in another tree, the root reference will change.

The root node of a tree contains tree-wide data structures like the list of unique IDs
(:py:attr:`~pyTooling.Tree.Node._nodesWithID`, :py:attr:`~pyTooling.Tree.Node._nodesWithoutID`). By utilizing the root
reference, each node can access these data structures by just one additional hop.

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

The property :py:attr:`~pyTooling.Tree.Node.Path` returns a tuple describing the path top-down from root node to the
current node.

.. code-block:: python

   # Create a simple tree representing directories
   root = Node(value="C:")
   dir = Node(value="temp", parent=root)
   file = Node(value="test.log", parent=dir)

   # Convert a path to string
   path = "\".join(file.Path)

While the tuple returned by :py:attr:`~pyTooling.Tree.Node.Path` can be used in an iteration (e.g. a for-loop), also a
generator is provided by method :py:meth:`~pyTooling.Tree.Node.GetPath` for iterations.

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

The method :py:meth:`~pyTooling.Tree.Node.GetAncestors` returns a generator to traverse bottom-up from current node to
the root node. If the top-down direction is needed, see :ref:`STRUCT/Tree/Path` for more details.

.. todo:: TREE: ancestors example

If needed, method :py:meth:`~pyTooling.Tree.Node.GetCommonAncestors` provides a generator to iterate the common
ancestors of two nodes in a tree.

.. todo:: TREE: common ancestors example


.. _STRUCT/Tree/Children:

Children
========

.. todo:: TREE: children

.. _STRUCT/Tree/Siblings:

Siblings
========

.. todo:: TREE: siblings

.. _STRUCT/Tree/Iterating:

Iterating a Tree
================

.. todo:: TREE: iterating a tree

.. _STRUCT/Tree/Merging:

Merging Trees
=============

.. todo:: TREE: merging a tree

.. _STRUCT/Tree/Splitting:

Splitting Trees
===============

.. todo:: TREE: splitting a tree
