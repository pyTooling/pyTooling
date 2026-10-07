.. _CI:

Overview
########

:mod:`pyTooling.CI` reads the payloads and files of a continuous integration service into a data model, so a
consumer works with named attributes and typed enumerations instead of nested dictionaries and magic strings.

A model carries no dependency on what is done with it. Converting a pipeline into a software execution trace, a
graph or a report is a consumer of the model, not part of it.

The package itself holds the service-independent structure - pipelines, called workflows, matrices, jobs and steps, and
the dependencies between them - which a service's model, e.g. :doc:`pyTooling.GitHub <pyToolGitHub:index>`'s, derives
from. Their exceptions derive from :exc:`~pyTooling.CI.CIError`.

.. toctree::
   :caption: Models
   :hidden:

   Pipeline

.. seealso::

   :ref:`CI/Pipeline`
      |rarr| The service-independent model of a pipeline and its dependencies.
   :doc:`pyTooling.GitHub <pyToolGitHub:index>`
      |rarr| The models of a GitHub Actions workflow run and workflow file, built on this model.
