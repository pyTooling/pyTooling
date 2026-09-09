.. _SCHEMAS/PackageOverrides-v0.1:

PackageOverrides v0.1
#####################

The schema of the **package-override file** the :ref:`dependency-table <DEP>` directive reads, which
:class:`~pyTooling.Dependency.Python.LicenseOverrides` parses. It states the meta-information a package index
can't answer for: a license, the URL of a project's own :file:`LICENSE` file, and a repository.

A key is a package name **optionally followed by a version expression** - the shape a requirement line has - so one
form covers both "for every version" and "for these versions". Keys are matched in the order they are written and
the first one a version satisfies wins, which is why a narrower statement goes above the bare name it refines. The
file states the structure it was written for in ``version``, and when a human last checked its statements in
``analysedAt``; both are required.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Download

         :download:`PackageOverrides-v0.1.json <../../pyTooling/Resources/PackageOverrides-v0.1.json>`

   .. grid-item::
      :columns: 6

      .. admonition:: Validate an override file

         .. code-block:: bash

            check-jsonschema --schemafile PackageOverrides-v0.1.json PackageOverrides.yaml

.. seealso::

   :ref:`DEP`
      |rarr| The directive reading the file, and what an override changes in the rendered table.

.. _SCHEMAS/PackageOverrides-v0.1/Editor:

Validating while writing
************************

An editor validates the file **as it is typed** when the YAML names the schema on its first line. In a checkout, a
relative path needs nothing published:

.. code-block:: YAML

   # yaml-language-server: $schema=../pyTooling/Resources/PackageOverrides-v0.1.json

Outside a checkout, the schema is served at its ``$id``:

.. code-block:: YAML

   # yaml-language-server: $schema=https://pyTooling.GitHub.io/pyTooling/schema/PackageOverrides-v0.1.json

.. _SCHEMAS/PackageOverrides-v0.1/Source:

Source
******

.. literalinclude:: ../../pyTooling/Resources/PackageOverrides-v0.1.json
   :caption: PackageOverrides-v0.1.json
   :language: json
   :linenos:
   :tab-width: 2
