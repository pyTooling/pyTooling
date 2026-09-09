.. _CONFIG:

Configuration
#############

Module :mod:`~pyTooling.Configuration` provides an abstract configuration reader.

.. #contents:: Table of Contents
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

.. tab-set::

   .. tab-item:: JSON
      :sync: JSON

      .. code-block:: JSON

         // one-liner style
         {"key1": "item1", "key2": "item2", "key3": "item3"}

         // multi-line style
         {
           "key1": "item1",
           "key2": "item2",
           "key3": "item3"
         }

   .. tab-item:: TOML
      :sync: TOML

      .. code-block:: TOML

         # one-liner style
         section_1 = {key1 = "item1", key2 = "item2", key3 = "item3"}

         # section style
         [section_2]
         key1 = "item1"
         key2 = "item2"
         key3 = "item3"

   .. tab-item:: YAML
      :sync: YAML

      .. code-block:: YAML

         # one-liner style
         {key1: item1, key2: item2, key3: item3}

         # multi-line style
         key1: item1
         key2: item2
         key3: item3

   .. tab-item:: XML
      :sync: XML

      .. code-block:: XML

         <items>
           <item key="key1">item1</item>
           <item key="key2">item2</item>
           <item key="key3">item3</item>
         </items>


A :class:`~pyTooling.Configuration.Dictionary` node is read like a :class:`dict`, and it **keeps the order the
document states its keys in** - the abstract node stores those keys in a list, so a round-trip through the reader
never reorders a file.

.. code-block:: Python

   section = config["tool"]["pytest"]

   "addopts" in section          # membership
   section["addopts"]            # by key, raises KeyNotFoundError when absent
   section.get("addopts", [])    # by key, with a default
   len(section)                  # number of key-value pairs

Three iterators are named alike, so nothing has to be remembered about which one plain iteration gives:
:meth:`~pyTooling.Configuration.Dictionary.IterateKeys`,
:meth:`~pyTooling.Configuration.Dictionary.IterateValues` and
:meth:`~pyTooling.Configuration.Dictionary.IterateItems`. Iterating the node itself yields its **values**, which is
what ``IterateValues`` yields.

Their materialized counterparts are spelled the way :class:`dict` spells them -
:meth:`~pyTooling.Configuration.Dictionary.keys`, :meth:`~pyTooling.Configuration.Dictionary.values` and
:meth:`~pyTooling.Configuration.Dictionary.items` - and return tuples. The names are deliberate: :class:`dict`
looks for a ``keys`` method to decide whether an object is a mapping, so ``dict(node)`` and ``{**node}`` work
because they exist.

.. attention::

   A value is only a :class:`str`, :class:`int` or :class:`float` when the document states a scalar there. When it
   states a sub-mapping or a list, the value is another :class:`~pyTooling.Configuration.Dictionary` or
   :class:`~pyTooling.Configuration.Sequence`, not a :class:`dict` or :class:`list`.


Sequences
*********

A :class:`~pyTooling.Configuration.Sequence` represents ordered information items.

.. tab-set::

   .. tab-item:: JSON
      :sync: JSON

      .. code-block:: JSON

         // one-liner style
         ["item1", "item2", "item3"]

         // multi-line style
         [
           "item1",
           "item2",
           "item3"
         ]

   .. tab-item:: TOML
      :sync: TOML

      .. code-block:: TOML

         # one-liner style
         section_1 = ["item1", "item2", "item3"]

         # multi-line style
         section_2 = [
           "item1",
           "item2",
           "item3"
         ]

   .. tab-item:: YAML
      :sync: YAML

      .. code-block:: YAML

         # one-liner style
         [item1, item2, item3]

         # multi-line style
         - item1
         - item2
         - item3

   .. tab-item:: XML
      :sync: XML

      .. code-block:: XML

         <items>
           <item>item1</item>
           <item>item2</item>
           <item>item3</item>
         </items>

A :class:`~pyTooling.Configuration.Sequence` node is read like a :class:`list`: by index, with
:func:`len`, and by iterating it.

.. code-block:: Python

   sources = config["project"]["sources"]

   sources[0]                    # by index
   sources[-1]                   # negative indices count from the end
   len(sources)
   for source in sources:
     ...

:meth:`~pyTooling.Configuration.Sequence.index` and :meth:`~pyTooling.Configuration.Sequence.count` are provided
with :class:`list`'s signatures, so code written against a list keeps working when it is handed a sequence node.
``index`` accepts ``start`` and ``stop``, treats negative values as offsets from the end, and raises
:exc:`ValueError` when nothing in the searched range matches.


Configuration
*************

A :class:`~pyTooling.Configuration.Configuration` represents the whole configuration (file) made of sequences,
dictionaries and scalar information items.

.. tab-set::

   .. tab-item:: JSON
      :sync: JSON

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

   .. tab-item:: TOML
      :sync: TOML

      .. attention:: Not yet implemented.

      .. code-block:: TOML

         version = "1.0"

         [settings]
         key1 = "item1"
         key2 = "item2"

         files = [
           "path/to/file1.ext",
           "path/to/file2.ext",
           "path/to/file3.ext"
         ]

   .. tab-item:: YAML
      :sync: YAML

      .. code-block:: YAML

         version: "1.0"
         settings:
           key1: item1
           key2: item2
         files:
           - path/to/file1.ext
           - path/to/file2.ext
           - path/to/file3.ext

   .. tab-item:: XML
      :sync: XML

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

A :class:`~pyTooling.Configuration.Configuration` is the **root** node of a document, and it is itself a
dictionary node - so a file is read by indexing the configuration object directly. It adds the one thing a root has
that an inner node doesn't: :attr:`~pyTooling.Configuration.Configuration.ConfigFile`, the path it was read from.

.. code-block:: Python

   from pathlib                     import Path
   from pyTooling.Configuration.YAML import Configuration

   config = Configuration(Path("pyproject.yaml"))
   config.ConfigFile                 # the path it was read from
   config["tool"]["pytest"]["addopts"]

Reaching deep into a document by chained indexing is verbose, so every node also answers a **path expression**
through :meth:`~pyTooling.Configuration.Node.QueryPath`. Its elements are separated by a colon and it is resolved
relative to the node it is asked of:

.. code-block:: Python

   config.QueryPath("tool:pytest:addopts")

A key that names no element raises :exc:`~pyTooling.Configuration.KeyNotFoundError`, which derives from
:exc:`KeyError` so an ordinary ``except KeyError`` still catches it. A malformed expression raises
:exc:`~pyTooling.Configuration.PathExpressionError`, and a value the format cannot map onto the data model raises
:exc:`~pyTooling.Configuration.UnsupportedValueTypeError`.

.. attention::

   **A configuration is read-only.** Assigning to a node - ``config["key"] = value`` - raises
   :exc:`NotImplementedError`, as does renaming a key through :attr:`~pyTooling.Configuration.Node.Key`. Writing a
   configuration file back is not implemented for any format.


Data Model
**********

The data model is a **tree of three node kinds**, and the diagram below is the whole grammar: a configuration
contains dictionaries and sequences, and each of those contains dictionaries and sequences again, to any depth. The
leaves are the scalars the file format supports.

Every node derives from :class:`~pyTooling.Configuration.Node` and knows two neighbours - its ``_root`` and its
``_parent`` - so a node handed to a function on its own can still resolve a path against the document it came from.

The abstract classes are **mixins**, and a concrete format supplies the parsing. That is why
:class:`~pyTooling.Configuration.Node` carries the two class variables
:attr:`~pyTooling.Configuration.Node.DICT_TYPE` and :attr:`~pyTooling.Configuration.Node.SEQ_TYPE`: the abstract
code has to instantiate a *format's* dictionary or sequence when it descends into a document, and these are what it
instantiates. A concrete implementation sets them, which is step 5 below.

Two implementations ship with pyTooling - :mod:`pyTooling.Configuration.JSON` and
:mod:`pyTooling.Configuration.YAML` - and the YAML one additionally interpolates ``${...}`` variable references in
scalar values, raising :exc:`~pyTooling.Configuration.InterpolationError` for a dangling ``$`` or an unclosed
reference.

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
