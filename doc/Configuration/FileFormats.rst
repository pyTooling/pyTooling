.. _CONFIG/FileFormat:

File Formats
############

Currently, the following file formats are supported:

* :ref:`CONFIG/FileFormat/JSON`
* :ref:`CONFIG/FileFormat/YAML`

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

Possible future file formats:

* :ref:`CONFIG/FileFormat/TOML`
* :ref:`CONFIG/FileFormat/XML`

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


.. toctree::
   :hidden:

   JSON
   TOML
   YAML
   XML
