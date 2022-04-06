Tree
####

:py:class:`~pyTooling.Tree.Node` implements a fast and simple tree data structure, which outperforms `anytree` and
`itertree`.

Features
********

* Fast and simple tree data structure based on a single :py:class:`~pyTooling.Tree.Node` class.
* A tree can be constructed top-down and bottom-up.
* A node can have a unique ID.
* A node can have a value.
* A node can store key-value-pairs via dictionary syntax.
* A node has a reference to its parent node.
* Each node has a reference to the root node in a tree (representative node).


Examples
********

.. todo:: TREE: Add examples


By Feature
**********

Unique ID
=========

A node can be created with a unique ID when the object is created. Afterwards, the :py:attr:`ID` is a readonly property.
Any hashable object can be used as an ID. The ID must be unique per tree. If trees are merged or nodes are added to an
existing tree, the newly added node's ID(s) are checked and might cause an exception.

.. code:: python

   # Create node with unique ID 5
   node = Node(id=5)

   # Read a node's ID
   id = node.ID


Value
=====

A node's value can be given at node creating time or it can be set ant any later time via property :py:attr:`Value`. Any
data type is accepted. The internally stored value can be retrieved via the same property. If a node's string
representation is requested via :py:meth:`__str__` and a node's value isn't None, then the value's string representation
is returned.

.. code:: python

   # Create node with value 5
   node = Node(value=5)

   # Set or change a node's value
   node.Value = 10

   # Read a node's Value
   value = node.Value


Key-Value-Pairs
===============

.. todo:: TREE: setting / getting a node's KVPs

Parent Reference
================

Each node has a reference to its parent node. In case, the node is the root node, the parent reference is None. The
parent-child relation can be set at node creation time, or a parent can be assigned to a node at any later time via
property :py:attr:`Parent`. The same property can be used to retrieve the current parent reference.

.. code:: python

   # Create node without parent relation ship (root node)
   root = Node(id=0)

   # Create a node add directly attach it to an existing tree
   node = Node(id=1, parent=root)

   # Read a node's rarent
   parent = node.Parent

In case, two trees were created (a single node is already a minimal tree), trees get merged if one tree's root node is
assigned a parent relationship.

.. code:: python

   # Create a tree with a single node
   root = Node(id=0)

   # Create a second minimalistic tree
   otherTree = Node(id=100)

   # Set parent relationship and merge trees
   otherTree.Parent = root


Root Reference
==============

Each node has a reference to the tree's root node. The root node can also be considered the representative node of a
tree and can be accessed via read-only property :py:attr:`~pyTooling.Tree.Node.Root`.

When a node is assigned a new parent relation and this parent a node in another tree, the root reference will change.

The root node of a tree contains tree-wide data structures like the list of unique IDs
(:py:attr:`~pyTooling.Tree.Node._nodesWithID`, :py:attr:`~pyTooling.Tree.Node._nodesWithoutID`). By utilizing the root
reference, each node can access these data structures by just one additional hop.

.. code:: python

   # Create a simple tree
   root = Node()
   nodeA = Node(parent=root)
   nodeB = Node(parent=root)

   # Check if nodeA and nodeB are in same tree
   inSameTree = nodeA is nodeB


Path
====

The property :py:attr:`~pyTooling.Tree.Node.Path` returns a tuple describing the path top-down from root node to the
current node.

.. code:: python

   # Create a simple tree representing directories
   root = Node(value="C:")
   dir = Node(value="temp", parent=root)
   file = Node(value="test.log", parent=dir)

   # Get path as string
   path = "\".join(file.Path)


Ancestors
=========

.. todo:: TREE: ancestors

Children
========

.. todo:: TREE: children

Siblings
========

.. todo:: TREE: siblings

Iterating a Tree
================

.. todo:: TREE: iterating a tree

Merging Trees
=============

.. todo:: TREE: merging a tree

Splitting Trees
===============

.. todo:: TREE: splitting a tree
