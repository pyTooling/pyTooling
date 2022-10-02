.. _CONFIG:

Configuration
#############

Module :py:mod:`~pyTooling.Configuration` provides an abstract configuration reader.

.. contents:: Table of Contents
   :local:
   :depth: 1

It supports any configuration file syntax, which provides:

* scalar elements (integer, string, ...),
* sequences (ordered lists), and
* dictionaries (key-value-pairs).

The abstracted data model is based on a common :py:class:`~pyTooling.Configuration.Node` class, which is derived to a
:py:class:`~pyTooling.Configuration.Sequence`, :py:class:`~pyTooling.Configuration.Dictionary` and
:py:class:`~pyTooling.Configuration.Configuration` class.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.Configuration
   :parts: 1

Sequences
*********

A :py:class:`~pyTooling.Configuration.Sequence` represents ordered information items.

Dictionary
**********

A :py:class:`~pyTooling.Configuration.Dictionary` represents key-value-pairs of information.

Configuration
*************

A :py:class:`~pyTooling.Configuration.Configuration` represents the whole configuration (file) made of sequences,
dictionaries and scalar information items.

Data Model
**********

.. #rubric:: Data model

.. mermaid::

   flowchart TD
     Configuration --> Dictionary
     Configuration --> Sequence
     Dictionary --> Dictionary
     Sequence --> Sequence
     Dictionary --> Sequence
     Sequence --> Dictionary


Creating a Concrete Implementation
**********************************

Follow these steps to derive a concrete implementation of the abstract configuration data model.

1. Import classes from abstract data model

   .. code-block:: python

      from . import (
        Node as Abstract_Node,
        Dictionary as Abstract_Dict,
        Sequence as Abstract_Seq,
        Configuration as Abstract_Configuration,
        KeyT, NodeT, ValueT
      )

2. Derive a node, which might hold references to nodes in the source file's parser for later usage.

   .. code-block:: python

      @export
      class Node(Abstract_Node):
        _configNode: Union[CommentedMap, CommentedSeq]

        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: Union[CommentedMap, CommentedSeq]):
          super().__init__(root, parent)
          self._configNode = configNode

3. Derive a dictionary class:

   .. code-block:: python

      @export
      class Dictionary(Abstract_Dict, Node):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedMap):
          Node.__init__(self, root, parent, key, configNode)

4. Derive a sequence class:

   .. code-block:: python

      @export
      class Sequence(Abstract_Seq, Node):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedSeq):
          Node.__init__(self, root, parent, key, configNode)

5. Set new dictionary and sequence classes as types in the abstract node class.

   .. code-block:: python

      setattr(Abstract_Node, "DICT_TYPE", Dictionary)
      setattr(Abstract_Node, "SEQ_TYPE", Sequence)

6. Derive a configuration class:

   .. code-block:: python

      @export
      class Configuration(Abstract_Configuration, Dictionary):
        def __init__(self, configFile: Path):
          Abstract_Configuration.__init__(self)

          with configFile.open() as file:
            self._config = ...

          Dictionary.__init__(self, self, self, None, self._config)
