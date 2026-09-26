.. _CI:

Overview
########

:mod:`pyTooling.CI` reads the payloads of a continuous integration service into a data model, so a consumer works
with named attributes and typed enumerations instead of nested dictionaries and magic strings.

A model carries no dependency on what is done with it. Converting a pipeline into a software execution trace, a
graph or a report is a consumer of the model, not part of it.

.. toctree::
   :caption: Services
   :hidden:

   GitHub

.. seealso::

   :ref:`CI/GitHub`
      |rarr| The model of a GitHub Actions workflow run.
