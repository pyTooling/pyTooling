.. _CI:

Overview
########

:mod:`pyTooling.CI` reads the payloads of a continuous integration service into a data model, so a consumer works
with named attributes and typed enumerations instead of nested dictionaries and magic strings.

A model carries no dependency on what is done with it. Converting a pipeline into a software execution trace, a
graph or a report is a consumer of the model, not part of it.

:mod:`pyTooling.CI.Pipeline` is the service-independent structure - pipelines, called workflows, matrices, jobs and
steps, and the dependencies between them - which a service's model derives from.

.. toctree::
   :caption: Models
   :hidden:

   Pipeline
   GitHub

.. seealso::

   :ref:`CI/Pipeline`
      |rarr| The service-independent model of a pipeline and its dependencies.
   :ref:`CI/GitHub`
      |rarr| The model of a GitHub Actions workflow run.
