.. _DEPENDENCIES:

Overview
########

The module :mod:`pyTooling.Dependency` models the dependencies between packages: which package depends on which
version of which other package, where those packages are published, and what the resulting graph looks like.

.. note::

   This is about *modelling* dependencies. The dependencies of pyTooling itself are listed in :ref:`DEP`.

.. #contents:: Table of Contents
   :depth: 2

.. _DEPENDENCIES/DataModel:

Data Model
##########

The generic data model is storage agnostic - it describes packages and versions without assuming where they come
from:

* :class:`~pyTooling.Dependency.Package` is a package by name, with the versions it has.
* :class:`~pyTooling.Dependency.PackageVersion` is one version of a package, when it was released, and which
  versions of which other packages it depends on.
* :class:`~pyTooling.Dependency.PackageStorage` is a place packages are published - an index, a registry, a
  repository.
* :class:`~pyTooling.Dependency.PackageDependencyGraph` collects the packages known from one or more storages.

.. _DEPENDENCIES/Python:

Python Packages
###############

:mod:`pyTooling.Dependency.Python` implements that model for Python packages published on
`PyPI <https://pypi.org>`__:

* :class:`~pyTooling.Dependency.Python.Project` and :class:`~pyTooling.Dependency.Python.Release` are the Python
  flavours of a package and a package version.
* :class:`~pyTooling.Dependency.Python.Distribution` describes a single distribution file of a release - a wheel or
  a source distribution.
* :class:`~pyTooling.Dependency.Python.PythonPackageIndex` queries PyPI, and
  :class:`~pyTooling.Dependency.Python.PythonPackageDependencyGraph` is the graph built from it.

Details are fetched on demand rather than up front: a project knows its releases before it knows anything about
them, and :class:`~pyTooling.Dependency.Python.LazyLoadableMixin` loads the rest when it is first asked for. A
dependency graph is otherwise thousands of HTTP requests wide.

.. attention::

   Querying PyPI needs `aiohttp <https://GitHub.com/aio-libs/aiohttp>`__, which is an optional dependency. Install
   it with the ``pypi`` extra:

   .. code-block:: shell

      pip install pyTooling[pypi]

   Without it, importing :mod:`pyTooling.Dependency.Python` raises an exception naming the extra. The generic data
   model in :mod:`pyTooling.Dependency` has no such requirement.

.. _DEPENDENCIES/Exceptions:

Exceptions and Warnings
#######################

:exc:`~pyTooling.Dependency.DependencyException` is the base of the module's exceptions:
:exc:`~pyTooling.Dependency.NoSessionAvailableException` when a query is attempted without an open session,
:exc:`~pyTooling.Dependency.ProjectNotFoundException` and
:exc:`~pyTooling.Dependency.ReleaseNotFoundException` when the index does not know what was asked for.

A malformed requirement or unreadable release metadata does not abort the traversal - it is reported as a
:class:`~pyTooling.Dependency.BrokenRequirementWarning` or
:class:`~pyTooling.Dependency.ReleaseDetailsWarning`, because one bad package should not hide the rest of the
graph.
