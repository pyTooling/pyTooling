.. _DEPENDENCIES:

Overview
########

The module :mod:`pyTooling.Dependency` models the dependencies between packages: which package depends on which
version of which other package, where those packages are published, and what the resulting graph looks like.

.. seealso::

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

.. _DEPENDENCIES/Graph:

Conversion to a Graph
#####################

:meth:`~pyTooling.Dependency.PackageDependencyGraph.ToGraph` converts a dependency graph into a
:class:`pyTooling.Graph.Graph`. The algorithms of :mod:`pyTooling.Graph` then apply -
:meth:`~pyTooling.Graph.BaseGraph.IterateTopologically` yields the versions dependencies first,
:meth:`~pyTooling.Graph.BaseGraph.HasCycle` finds a circular dependency, and :mod:`pyTooling.Graph.GraphViz` or
:mod:`pyTooling.Graph.GraphML` write it for a viewer.

Every package version of every storage becomes a :class:`~pyTooling.Graph.Vertex`:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Vertex member
     - Content
   * - :attr:`~pyTooling.Graph.Vertex.ID`
     - the :class:`~pyTooling.Dependency.PackageVersion`, so
       :meth:`Graph.GetVertexByID <pyTooling.Graph.Graph.GetVertexByID>` finds a version's vertex. Written by a
       graph writer as ``<package> - <version>``.
   * - :attr:`~pyTooling.Graph.Vertex.Value`
     - empty (``None``) - the ID already references the version.
   * - key ``license``
     - the license as SPDX expression, e.g. ``BSD-3-Clause``; ``NOASSERTION`` if it's unknown. Always set.
   * - key ``releasedAt``
     - the release time in ISO 8601, e.g. ``2022-10-25T02:30:23``.
   * - keys ``licenseURL``, ``repositoryURL``, ``documentationURL``, ``issueTrackerURL``, ``projectURL`` and
       ``changelogURL``
     - the URL of the license text, the source repository, the documentation, the issue tracker, the project's
       homepage and the changelog.

Every key-value pair is a string. All but ``license`` are set only if the version knows the value - for a Python
package, after its details were loaded; converting a graph doesn't load them.

Every dependency becomes an :class:`~pyTooling.Graph.Edge` from the version needing to the version it needs, so an
edge reads *needs*. An edge has no ID, value or key-value pairs.

.. code-block:: Python

   from pyTooling.Graph.GraphViz import Graph as DotGraph

   graph = dependencyGraph.ToGraph()
   for vertex in graph.IterateTopologically():
     print(vertex.ID, vertex["license"])

   dot = DotGraph("Example")
   dot.FromGraph(graph)
   print(dot)

For a graph in which ``myApp 1.0.0`` depends on ``colorama 0.4.6``, Graphviz' DOT language reads:

.. code-block:: text

   digraph "Example" {
     "myApp - 1.0.0";
     "colorama - 0.4.6";
     "myApp - 1.0.0" -> "colorama - 0.4.6";
   }

:mod:`pyTooling.Graph.GraphML` writes each key-value pair as a ``<data>`` element of the node, declared by a key
named ``node<key>``, e.g. ``<data key="nodelicense">BSD-3-Clause</data>``.

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

   Querying PyPI needs :gh:`aiohttp <aio-libs/aiohttp>`, :gh:`requests <psf/requests>`
   and :gh:`packaging <pypa/packaging>`, which are optional dependencies. Install them with the
   ``pypi`` extra:

   .. code-block:: shell

      pip install pyTooling[pypi]

   Without it, importing :mod:`pyTooling.Dependency.Python` raises an exception naming the extra. The generic data
   model in :mod:`pyTooling.Dependency` has no such requirement.

.. _DEPENDENCIES/Exceptions:

Exceptions and Warnings
#######################

:exc:`~pyTooling.Dependency.DependencyError` is the base of the module's exceptions:
:exc:`~pyTooling.Dependency.NoSessionAvailableError` when a query is attempted without an open session,
:exc:`~pyTooling.Dependency.ProjectNotFoundError` and
:exc:`~pyTooling.Dependency.ReleaseNotFoundError` when the index does not know what was asked for.

A malformed requirement or unreadable release metadata does not abort the traversal - it is reported as a
:class:`~pyTooling.Dependency.BrokenRequirementWarning` or
:class:`~pyTooling.Dependency.ReleaseDetailsWarning`, because one bad package should not hide the rest of the
graph.


.. _DEPENDENCIES/Competitors:

Competing Solutions
###################

:mod:`pyTooling.Dependency` is a library: a data model of packages, their versions and dependencies, read from PyPI's
JSON API without installing anything, with the license of every release and hand-written
:class:`~pyTooling.Dependency.Python.LicenseOverrides` for packages whose metadata states none. The tools below are
command-line tools first, or parse a requirements file only.

.. _DEPENDENCIES/pipdeptree:

pipdeptree
==========

Source: :gh:`pipdeptree <tox-dev/pipdeptree>`, on PyPI as `pipdeptree <https://pypi.org/project/pipdeptree/>`__.

.. rubric:: Disadvantages

* A command-line tool: a program receives its tree as text, JSON, Mermaid or Graphviz, not as objects.

.. rubric:: Advantages

* Shows the installed environment, and reports conflicting requirements and cycles.
* ``from-index`` resolves a package or a requirements file against an index without installing it, and
  ``from-lock`` reads a resolved :pep:`751` lock file.
* ``--summary`` reports package counts, depth, conflicts, cycles, licenses and size.

.. _DEPENDENCIES/pipgrip:

pipgrip
=======

Source: :gh:`pipgrip <ddelange/pipgrip>`, on PyPI as `pipgrip <https://pypi.org/project/pipgrip/>`__.

.. rubric:: Disadvantages

* A command-line tool: its result is a list of pins or a tree, as text or JSON.

.. rubric:: Standoff

* Both select the latest versions satisfying every constraint: pipgrip with the PubGrub algorithm, which poetry
  uses too, :meth:`PackageVersion.SolveLatest <pyTooling.Dependency.PackageVersion.SolveLatest>` by backtracking over
  the versions in the graph.

.. rubric:: Advantages

* Installs the resolved tree, and combines the trees of several packages into one set of pins.

.. _DEPENDENCIES/johnnydep:

johnnydep
=========

Source: :gh:`johnnydep <wimglenn/johnnydep>`, on PyPI as `johnnydep <https://pypi.org/project/johnnydep/>`__.

.. rubric:: Disadvantages

* A command-line tool printing a tree of names and summaries.

.. rubric:: Standoff

* Both read a package's dependencies from the index, not from the installed environment.

.. rubric:: Advantages

* Resolves a package's tree into pinned versions (``--output-format pinned``).

.. _DEPENDENCIES/requirements-parser:

requirements-parser
===================

Source: :gh:`requirements-parser <madpah/requirements-parser>`, on PyPI as
`requirements-parser <https://pypi.org/project/requirements-parser/>`__.

.. rubric:: Disadvantages

* Options traversing the local file system are not handled, so a ``-r`` reference to another file isn't followed.
  :class:`~pyTooling.Dependency.Python.RequirementsFile` reads the referenced files as a tree, keeps which file a
  requirement was stated in, and raises a :exc:`~pyTooling.Dependency.CircularRequirementsFileError` for a cycle.

.. rubric:: Advantages

* Parses editables, version control URIs, hashes and URLs, which
  :class:`~pyTooling.Dependency.Python.RequirementsFile` skips as instructions to the installer.
