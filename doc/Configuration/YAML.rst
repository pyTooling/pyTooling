.. _CONFIG/FileFormat/YAML:

YAML
****

Module :py:mod:`~pyTooling.Configuration.YAML` provides a configuration reader implementation for the YAML format.

.. admonition:: config.yml

   .. code-block:: yaml

      version: 1
      list:
        - item_1
        - item_2
      dict:
        key_1: value_1
        key_2: value_2
      complex:
        path:
          to:
            list:
              - item_10
              - item_11
              - item_12
            dict:
              key_10: value_10
              key_11: value_11

Reading a YAML Formatted Config File
====================================

.. code-block:: python

   from pathlib import Path
   from pyTooling.Configuration.YAML import Configuration

   configFile = Path("config.yml")
   config = Configuration(configFile)


Accessing Values by Name
========================

.. code-block:: python

   # root-level scalar value
   configFileFormatVersion = config["version"]

   # value in a sequence
   firstItemInList = config["list"][0]

   # first value in dictionary
   firstItemInDict = config["dict"]["key_1"]


Store Nodes in Variables
========================

.. code-block:: python

   # store intermediate node
   node = config["complex"]["path"]["to"]

   # navigate further
   nestedList = node["list"]
   nestedDict = node["dict"]


Iterate Sequences
=================

.. code-block:: python

   # simple list
   simpleList = config["list"]
   for item in simpleList:
     pass

   # deeply nested list
   nestedList = config["complex"]["path"]["to"]["list"]
   for item in nestedList:
     pass

Iterate Dictionaries
====================

.. todo:: Needs documentation
