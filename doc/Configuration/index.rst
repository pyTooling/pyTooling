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

   settings = config["settings"]

   hasKey1 =   "key1" in settings        # membership
   item1 =     settings["key1"]          # by key, raises KeyNotFoundError when absent
   item3 =     settings.get("key3", "")  # by key, with a default
   pairCount = len(settings)             # number of key-value pairs

A key the document states without a value - ``key:`` in YAML, ``null`` in JSON - reads as ``None``, and
:meth:`~pyTooling.Configuration.Dictionary.get` returns its default only for a key that is absent. A variable
``${...}`` referencing such a key raises :exc:`~pyTooling.Configuration.PathExpressionError`.

Three iterators are named alike, so nothing has to be remembered about which one plain iteration gives:
:meth:`~pyTooling.Configuration.Dictionary.IterateKeys`,
:meth:`~pyTooling.Configuration.Dictionary.IterateValues` and
:meth:`~pyTooling.Configuration.Dictionary.IterateItems`. Iterating the node itself yields its **values**, which is
what ``IterateValues`` yields.

.. code-block:: Python

   for key in settings.IterateKeys():
     print(key)

   for value in settings:                     # the node itself yields its values
     print(value)

   for key, value in settings.IterateItems():
     print(f"{key}: {value}")

Their materialized counterparts are spelled the way :class:`dict` spells them -
:meth:`~pyTooling.Configuration.Dictionary.keys`, :meth:`~pyTooling.Configuration.Dictionary.values` and
:meth:`~pyTooling.Configuration.Dictionary.items` - and return tuples. The names are deliberate: :class:`dict`
looks for a ``keys`` method to decide whether an object is a mapping, so ``dict(node)`` and ``{**node}`` work
because they exist.

.. attention::

   A scalar is returned as a :class:`str`, whatever the document writes: ``42`` is ``"42"``, ``1.5`` is ``"1.5"`` and
   ``true`` is ``"True"``. Only a key stated without a value reads as ``None``. When the document states a sub-mapping
   or a list, the value is another :class:`~pyTooling.Configuration.Dictionary` or
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

A :class:`~pyTooling.Configuration.Sequence` node is read like a :class:`list`: by index, with :func:`len`, and by
iterating it. An index is the position the document states an item at, and a negative index counts from the end. An
element is a scalar or another node, just as a dictionary node's value is, so a sequence of mappings is iterated and
each element indexed by key. Because iteration yields the elements themselves, ``in`` asks whether an element is in
the sequence - a sequence has no keys to ask for.

.. code-block:: Python

   files = config["files"]

   firstFile = files[0]                 # by index
   lastFile =  files[-1]                # negative indices count from the end
   fileCount = len(files)               # number of elements
   hasFile1 =  "path/to/file1.ext" in files

   for file in files:
     print(file)

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

   from pathlib                      import Path
   from pyTooling.Configuration.YAML import Configuration

   config =  Configuration(Path("settings.yml"))
   version = config["version"]

Reaching deep into a document by chained indexing is verbose, so every node also answers a **path expression**
through :meth:`~pyTooling.Configuration.Node.QueryPath`. Its elements are separated by a colon and it is resolved
relative to the node it is asked of:

.. code-block:: Python

   item1 = config.QueryPath("settings:key1")

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
:mod:`pyTooling.Configuration.YAML` - and both interpolate ``${...}`` variable references in scalar values, raising
:exc:`~pyTooling.Configuration.InterpolationError` for a dangling ``$`` or an unclosed reference.

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


.. _CONFIG/Competitors:

Competing Solutions
*******************

:mod:`pyTooling.Configuration` reads a JSON or YAML file into one read-only tree of nodes, addressed by path
expressions with ``${...}`` references between values. The packages below manage the settings of an application -
layering, merging, overriding, validating and writing them - which this package doesn't.

.. _CONFIG/OmegaConf:

OmegaConf
=========

Source: :gh:`omegaconf <omry/omegaconf>`, on PyPI as `omegaconf <https://pypi.org/project/omegaconf/>`__.

.. rubric:: Disadvantages

* Files are read and written as YAML only.
* Depends on ``PyYAML`` and on the ANTLR runtime, pinned to version 4.9.

.. rubric:: Standoff

* Both resolve ``${...}`` references to other values. OmegaConf resolves ``${a.b}`` from the root and ``${..b}``
  from the parent; pyTooling resolves every reference from the node holding the value, ``${..:b}`` from its parent.

.. rubric:: Advantages

* Configurations are merged, can be changed and set read-only on demand, and are saved back to a file.
* A configuration can be typed by a :mod:`dataclass <dataclasses>` ("structured config"), and created from
  ``key=value`` arguments of a command line.
* A scalar keeps its type; pyTooling returns a number as :class:`str`.

.. _CONFIG/Hydra:

Hydra
=====

Source: :gh:`hydra <facebookresearch/hydra>`, on PyPI as `hydra-core <https://pypi.org/project/hydra-core/>`__.

.. rubric:: Disadvantages

* A framework around an application's ``main`` function, built on OmegaConf, rather than a reader for a document.

.. rubric:: Advantages

* Composes a configuration from groups of files, overrides any value from the command line, and runs an application
  once per combination of values.

.. _CONFIG/Dynaconf:

Dynaconf
========

Source: :gh:`dynaconf <dynaconf/dynaconf>`, on PyPI as `dynaconf <https://pypi.org/project/dynaconf/>`__.

.. rubric:: Disadvantages

* It manages the settings of an application - files and sources merged into one settings object - rather than
  reading a given document as a tree.

.. rubric:: Advantages

* Reads TOML, YAML, JSON, INI and Python files, and lets environment variables override every value.
* Switches between environments, e.g. ``development`` and ``production``, validates settings, and loads them from
  Vault or Redis.
* Has no third-party dependency.

.. _CONFIG/Box:

python-box
==========

Source: :gh:`Box <cdgriffith/Box>`, on PyPI as `python-box <https://pypi.org/project/python-box/>`__.

.. rubric:: Standoff

* A dictionary with attribute access - ``box.a.b`` - rather than a configuration reader. With ``box_dots``, a dotted
  key ``box["a.b"]`` is a path.

.. rubric:: Advantages

* Converts from and to JSON, YAML and TOML, and can be frozen to stay unchanged.

.. _CONFIG/Confuse:

Confuse
=======

Source: :gh:`confuse <beetbox/confuse>`, on PyPI as `confuse <https://pypi.org/project/confuse/>`__.

.. rubric:: Disadvantages

* Reads YAML only.

.. rubric:: Advantages

* Layers a default file, the user's file from the platform's configuration directory, environment variables and
  command-line arguments, and checks a value's type when it is read.
