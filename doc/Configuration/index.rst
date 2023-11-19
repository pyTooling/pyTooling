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

      // one-liner style
      {"key1": "item1", "key2": "item2", "key3": "item3"}

      // multi-line style
      {
        "key1": "item1",
        "key2": "item2",
        "key3": "item3"
      }

.. tab:: TOML

   .. code-block:: TOML

      # one-liner style
      section_2 = {key1 = item1, key2 = item2, key3 = item3}

      # multi-line style
      section_3 = {
        key1 = item1,
        key2 = item2,
        key3 = item3
      }

      # section style
      [section_1]
      key1 = item1
      key2 = item2
      key3 = item3

.. tab:: YAML

   .. code-block:: YAML

      # one-liner style
      {key1: item1, key2: item2, key3: item3}

      # multi-line style
      key1: item1
      key2: item2
      key3: item3

.. tab:: XML

   .. code-block:: XML

      <items>
        <item key="key1">item1</item>
        <item key="key2">item2</item>
        <item key="key3">item3</item>
      </items>


.. todo:: CONFIG:: Needs documentation for Dictionary


Sequences
*********

A :class:`~pyTooling.Configuration.Sequence` represents ordered information items.

.. tab:: JSON

   .. code-block:: JSON

      // one-liner style
      ["item1", "item2", "item3"]

      // multi-line style
      [
        "item1",
        "item2",
        "item3"
      ]

.. tab:: TOML

   .. code-block:: TOML

      # one-liner style
      section_2 = [item1, item2, item3]

      # multi-line style
      section_3 = [
        item1,
        item2,
        item3
      ]

.. tab:: YAML

   .. code-block:: YAML

      # one-liner style
      [item1, item2, item3]

      # multi-line style
      - item1
      - item2
      - item3

.. tab:: XML

   .. code-block:: XML

      <items>
        <item>item1</item>
        <item>item2</item>
        <item>item3</item>
      </items>

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

.. tab:: TOML

   .. attention:: Not yet implemented.

   .. code-block:: TOML

      version = "1.0"

      settings = {
        key1 = "item1",
        key2 = "item2"
      }

      files = [
        "path/to/file1.ext",
        "path/to/file2.ext",
        "path/to/file3.ext"
      ]

.. tab:: YAML

   .. code-block:: YAML

      version: "1.0"
      settings:
        key1: item1
        key2: item2
      files:
        - path/to/file1.ext
        - path/to/file2.ext
        - path/to/file3.ext

.. tab:: XML

   .. attention:: Not yet implemented.

   .. code-block:: XML

      <?xml version="1.0" encoding="UTF-8" standalone="yes" ?>
      <configuration version="1.0">
        <settings>
          <setting key="key1">item1</setting>
          <setting key="key2">item2</setting>
        </settings>
        <files>
          <file>path/to/file1.ext</file>
          <file>path/to/file2.ext</file>
          <file>path/to/file3.ext</file>
        </files>
      </configuration>

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

        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: Union[CommentedMap, CommentedSeq]) -> None:
          Abstract_Node.__init__(self, root, parent)

          self._configNode = configNode

        # Implement mandatory methods and properties

3. Derive a dictionary class:

   .. code-block:: python

      @export
      class Dictionary(Node, Abstract_Dict):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedMap) -> None:
          Node.__init__(self, root, parent, key, configNode)

        # Implement mandatory methods and properties

4. Derive a sequence class:

   .. code-block:: python

      @export
      class Sequence(Node, Abstract_Seq):
        def __init__(self, root: "Configuration", parent: NodeT, key: KeyT, configNode: CommentedSeq) -> None:
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
        def __init__(self, configFile: Path) -> None:
          with configFile.open() as file:
            self._config = ...

          Dictionary.__init__(self, self, self, None, self._config)

        # Implement mandatory methods and properties
