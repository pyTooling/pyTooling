.. _CONFIG:

Configuration
#############

Module :mod:`~pyTooling.Configuration` provides an abstract configuration reader.

.. contents:: Table of Contents
   :local:
   :depth: 1

It supports any configuration file syntax, which provides:

* scalar elements (integer, string, ...),
* sequences (ordered lists), and
* dictionaries (key-value-pairs).

The abstracted data model is based on a common :class:`~pyTooling.Configuration.Node` class, which is derived to a
:class:`~pyTooling.Configuration.Sequence`, :class:`~pyTooling.Configuration.Dictionary` and
:class:`~pyTooling.Configuration.Configuration` class.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.Configuration
   :parts: 1

Dictionary
**********

A :class:`~pyTooling.Configuration.Dictionary` represents key-value-pairs of information.

.. tab:: JSON

   .. code-block:: JSON

      {"key1": "item1", "key2": "item2", "key3": "item3"}

.. tab:: YAML

   .. code-block:: JSON

      key1: item1
      key2: item2
      key3: item3

.. todo:: CONFIG:: Needs documentation for Dictionary

Sequences
*********

A :class:`~pyTooling.Configuration.Sequence` represents ordered information items.

.. tab:: JSON

   .. code-block:: JSON

      ["item1", "item2", "item3"]

.. tab:: YAML

   .. code-block:: JSON

      - item1
      - item2
      - item3

.. todo:: CONFIG:: Needs documentation for Sequences

Configuration
*************

A :class:`~pyTooling.Configuration.Configuration` represents the whole configuration (file) made of sequences,
dictionaries and scalar information items.

.. tab:: JSON

   .. code-block:: JSON

      { "version": "1.0",
        "settings": {
          "key1": "item1",
          "key2": "item2"
        },
        "files": [
          "path/to/file1.ext",
          "path/to/file2.ext",
          "path/to/file3.ext"
        ]
      }

.. tab:: YAML

   .. code-block:: JSON

      version: "1.0"
      settings:
        key1: item1
        key2: item2
      files:
        - path/to/file1.ext
        - path/to/file2.ext
        - path/to/file3.ext

.. todo:: CONFIG:: Needs documentation for Configuration

Data Model
**********

.. todo:: CONFIG:: Needs documentation for Data Model

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
        # further local fields

        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: Union[CommentedMap, CommentedSeq]):
          Abstract_Node.__init__(self, root, parent)

          self._configNode = configNode

        # Implement mandatory methods and properties

3. Derive a dictionary class:

   .. code-block:: python

      @export
      class Dictionary(Node, Abstract_Dict):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedMap):
          Node.__init__(self, root, parent, key, configNode)

        # Implement mandatory methods and properties

4. Derive a sequence class:

   .. code-block:: python

      @export
      class Sequence(Node, Abstract_Seq):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedSeq):
          Node.__init__(self, root, parent, key, configNode)

        # Implement mandatory methods and properties

5. Set new dictionary and sequence classes as types in the abstract node class.

   .. code-block:: python

      setattr(Abstract_Node, "DICT_TYPE", Dictionary)
      setattr(Abstract_Node, "SEQ_TYPE", Sequence)

6. Derive a configuration class:

   .. code-block:: python

      @export
      class Configuration(Dictionary, Abstract_Configuration):
        def __init__(self, configFile: Path):
          with configFile.open() as file:
            self._config = ...

          Dictionary.__init__(self, self, self, None, self._config)

        # Implement mandatory methods and properties
