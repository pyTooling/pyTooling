.. _CONFIG/FileFormat/JSON:

JSON
****

Module :mod:`~pyTooling.Configuration.JSON` provides a configuration reader implementation for the JSON format.

.. contents:: Table of Contents
   :local:
   :depth: 1

.. admonition:: config.json

   .. code-block:: json

      {
        "version": 1
        "list": [
          "item_1",
          "item_2"
        ],
        "dict": {
          "key_1": "value_1",
          "key_2": "value_2"
        },
        "complex": {
          "path": {
            "to": {
              "list": [
                "item_10",
                "item_11",
                "item_12"
              ],
              "dict": {
                "key_10": "value_10",
                "key_11": "value_11"
              }
            }
          }
        }
      }

.. seealso::

   ECMA Standard 404
     https://www.ecma-international.org/publications-and-standards/standards/ecma-404/
   Official JSON Website
     https://www.json.org/json-en.html
   Wikipedia
     https://en.wikipedia.org/wiki/JSON


Reading a JSON Formatted Config File
====================================

.. code-block:: python

   from pathlib import Path
   from pyTooling.Configuration.JSON import Configuration

   configFile = Path("config.json")
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

.. todo:: JSON:: Needs documentation
