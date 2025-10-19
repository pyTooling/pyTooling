.. _NEWS:

News
####

See `pyTooling Release Pages <https://github.com/pyTooling/pyTooling/releases>`__ for detail release notes on every
release.


Version 8.x (2025)
******************

.. topic:: `v8.7.3 - 21.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.3>`__

   tbd


.. topic:: `v8.7.2 - 04.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.2>`__

   tbd


.. topic:: `v8.7.1 - 04.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.1>`__

   tbd


.. topic:: `v8.7.0 - 24.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.0>`__

   tbd

.. topic:: `v8.6.0 - 12.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.6.0>`__

   tbd

.. topic:: `v8.5.1 - 14.06.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.1>`__

   tbd

.. topic:: `v8.5.0 - 31.05.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.0>`__

   tbd

.. topic:: `v8.4.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.4.0>`__

   tbd

.. topic:: `v8.3.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.3.0>`__

   * New count function to count the number of elements in an iterator/generator.
   * Added __setitem__ on pyTooling.CLIAbstraction.Environment.
   * Added __delitem__ on pyTooling.CLIAbstraction.Environment.

.. topic:: `v8.2.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.2.0>`__

   * Add WarningCollector to handle warnings similar to exceptions and send them along the call stack.

.. topic:: `v8.1.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.1.0>`__

   * Graph

     * Added methods HasVertexByID, HasVertexByValue.
     * Added method GetVertexByValue.

   * Versioning

     * Version classes are now hashable.
     * Added gamma release level.

   * Stopwatch

     * Added Exclude context manager

.. topic:: `v8.0.0 - 09.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.0>`__

   * Reworked semantic and calendar version classes:

     * Moved common implementations to Version base-type.

       * Moved major, minor, micro, build, post, dev, release level, release number, hash, prefix, postfix parts to the base-type.
       * Moved implementations of comparison operators to the base-type: __eq__, __ne__, __lt__, __le__, __gt__, __ge__.
       * Implemented minimum comparison operator using __rshift__ (>>) for PIP's ~= operator.
       * Implemented a formatting helper method _format.

     * Reworked SemanticVersion.

       * Additionally allow comparisons with string and integer types.
       * Enhanced SemanticVersion.Parse() class-method:

         * Raise exceptions on invalid inputs.
         * Use a regular expression to check and split the input.

     * Implemented CalendarVersion (previously a dummy).

       * Added CalendarVersion.Parse() class-method: raise exceptions on invalid inputs.
       * Implemented comparison operators.

     * Added validator classes WordSizeValidator and MaxValueValidator.
     * Added doc-strings.
     * Improved __str__() method to return only used version parts.
     * Added __format__() for user defined formatting specifications.

Version 7.x (2024)
******************

.. topic:: `v7.0.0 - 27.10.2024 <https://github.com/pyTooling/pyTooling/releases/v7.0.0>`__

   * Added support for Python 3.13 (and dropped 3.8).

     * Changed DEFAULT_PY_VERSIONS in pyTooling.Packaging to 3.9...3.13.

   * Reworked faulty Timer class and renamed it to StopWatch.

     * Support start, pause, resume, split and stop operations.
     * Collect active and inactive split times.
     * Accept a name at instantiation.
     * Take absolute time at start and stop via datetime.now().
     * Can be used in a with-statement.

   * @InheritDocString can be applied to classes too.

Version 6.x (2024)
******************

.. topic:: `v6.7.0 - 29.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.7.0>`__

   * :mod:`pyTooling.Terminal`

     * Added TerminalApplication.WriteCritical
     * Added TerminalApplication.ExitOnPreviousCriticalWarnings

.. topic:: `v6.6.0 - 18.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.6.0>`__

   * :mod:`pyTooling.Graph`

     * Allow setting key-value-pairs for a graph when creating a new graph.
     * Allow setting key-value-pairs for vertices when creating a new vertex.
     * Allow setting key-value-pairs for edges when creating a new edge.
     * Allow setting key-value-pairs for links when creating a new link.

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.loadReadmeFile` now supports new content formats:

       * plain text
       * ReStructured Text

   * :mod:`pyTooling.Platform`

     * Added :attr:`~pyTooling.Platform.Platform.StaticLibraryExtension`.

.. topic:: `v6.5.0 - 15.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.5.0>`__

   * :mod:`pyTooling.GenericPath`

     * :class:`pyTooling.GenericPath.URL.URL`:

       * Added support for basic authentication credentials (username and password).
       * Added :meth:`pyTooling.GenericPath.URL.URL.WithoutCredentials` method.

.. topic:: `v6.4.0 - 04.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.4.0>`__

   * :mod:`pyTooling.Platform`

     * Added readonly property :attr:`~pyTooling.Platform.Platform.IsNativeFreeBSD` to class Platform.

.. topic:: `v6.3.0 - 02.06.2024 <https://github.com/pyTooling/pyTooling/releases/v6.3.0>`__

   * :mod:`pyTooling.Tree`

     * Accept a custom formatting function per node to return a one-liner representation of a node for tree rendering.
     * Accept a key-value-pair mapping (dictionary) for nodes in a tree in the initializer.

   * :mod:`pyTooling.Graph`

     * Accept a key-value-pair mapping (dictionary) for all data structures (graph, edges, links, vertices, views, ...) in a graph in their initializers.

.. topic:: `v6.2.0 - 30.05.2024 <https://github.com/pyTooling/pyTooling/releases/v6.2.0>`__

   * :mod:`pyTooling.Common`

     * New helper function :func:`pyTooling.Common.getFullyQualifiedName`.
     * Python 3.8+: New helper functions :func:`pyTooling.Common.getResourceFile` and :func:`pyTooling.Common.readResourceFile`.
     * Python 3.11+: In case of :class:`TypeError` add a note to the exception describing the parameter/member type.

.. topic:: `v6.1.0 - 09.04.2024 <https://github.com/pyTooling/pyTooling/releases/v6.1.0>`__

   .. #empty

.. topic:: `v6.0.0 - 14.01.2024 <https://github.com/pyTooling/pyTooling/releases/v6.0.0>`__

   * Integrated ``pyAttributes`` v2.5.1 as :mod:`pyTooling.Attributes`.
   * Integrated :mod:`pyTooling.CLIAbstraction` v0.4.1.

Version 5.x (2023)
******************

.. topic:: `v5.0.0 - 02.07.2023 <https://github.com/pyTooling/pyTooling/releases/v5.0.0>`__

   * New ``ExtendedType`` features:

     * Added support for mixin-classes and delayed creation of slots.
     * Added automatic initializers for annotated fields (previously causing an exception due to slots).
     * Added automatic initializers for annotated class fields (previously causing an exception due to slots).

   * Added new decorators: ``@slotted``, ``@mixin``, ``@singleton``, ``@readonly``, and ``@notimplemented``.

   * Added JSON support for ``pyTooling.Configuration``.
   * New ``Platform`` features:

     * Added ``PythonVersion`` to ``Platform`` to distinguish Python versions.
     * Added ``PythonImplementation`` to ``Platform`` to distinguish CPython and PyPy.

   * New graph features:

     * ``GetVertexByID``
     * ``GetVertexByValue``
     * New vertex operations: ``IterateAllOutboundPathsAsVertexList``, ``Delete`` (itself), ``DeleteEdgeTo``, ``DeleteEdgeFrom``, ``DeleteLinkTo``, ``DeleteLinkFrom``.
     * New edge operations: ``Delete`` (itself)
     * New link operations: ``Delete`` (itself)

   * ``pyToolong.StateMachine`` package (alpha version).

Version 4.x (2023)
******************

.. topic:: `v4.0.1 - 26.03.2023 <https://github.com/pyTooling/pyTooling/releases/v4.0.1>`__

   * Graphs are now supporting subgraphs and exporting subgraphs to GraphML.

     * New ``SubGraph`` class.
     * New ``Link`` class.
     * New ``View`` class.

   * Added ``Vertex.Link***Vertex`` methods to link vertices from disjunctive subgraphs.
   * Added ``Vertex.HasLink***Vertex`` methods check if two vertices from disjunctive subgraphs are connected.
   * Added ``Vertex.Iterate***boundLinks`` to iterate links.
   * Added ``Graph.IterateLinks`` to iterate all links.
   * Added ``Graph.ReverseLinks``, ``Graph.RemoveLinks``.
   * Applied generic types when deriving from subclasses.
   * Added ``in`` operator for key-value

Version 3.x (2023)
******************

.. topic:: `v3.0.0 - 10.03.2023 <https://github.com/pyTooling/pyTooling/releases/v3.0.0>`__

   * Integrated :mod:`pyTooling.TerminalUI`.
   * Support for FreeBSD in ``Platform``.
   * A data model for GraphML (graph, node, edge, key, data and subgraph).
   * A conversion from pyTooling's graph data structure to GraphML XML files.
   * A conversion from pyTooling's tree data structure to GraphML XML files.

Jan. 2023 - Graph enhancements
******************************

* Improved exceptions.
* Added ``ConvertToTree`` method to ``Vertex``.
* Added ``Render`` method to ``Node``.

Nov. 2023 - Graph implementation
********************************

* Added an object-oriented graph implementation.

Archive
*******

Attributes
==========

.. only:: html

   Jan. 2024 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Jan. 2024 - Direct integration into pyTooling

* The standalone package ``pyAttributes`` v2.5.1 has been integrated as :mod:`pyTooling.Attributes` into pyTooling
  v6.0.0.


.. only:: html

   Nov. 2021 - Moved to pyTooling
   ------------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Moved to pyTooling

* Changed repository location from ``Paebbels/pyAttributes`` to ``pyTooling/pyAttributes``.


.. only:: html

   Jan. 2020 - Enhancements
   ------------------------

.. only:: latex

   .. rubric:: Jan. 2020 - Enhancements

* ``GetMethods`` and ``GetAttributes`` adhere to method resolution order (MRO) to find attributes annotated to methods
  from base-classes.
* An ``AttributeHelperMixinclass`` to ease the usage of attributes on a class' methods.


.. only:: html

   Dec. 2019 - Merge from IPCMI
   ----------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Merge from IPCMI

* Merged latest implementation updates from pyIPCMI.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* Basic attribute class.
* Attribute helper classes.
* Package for handling Python's argparse as declarative code.


CallByRef
=========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.CallByRef`` v1.2.1 has been integrated as :mod:`pyTooling.CallByRef` into pyTooling
  vX.X.X.


.. only:: html

   Sep. 2020 - Bug Fixes
   ---------------------

.. only:: latex

   .. rubric:: Sep. 2020 - IBug Fixes

* Some bugfixes.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* Call-by-reference implementation for Python.


CLIAbstraction
==============

.. only:: html

   Jan. 2024 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Jan. 2024 - Direct integration into pyTooling

* The namespace package ``pyTooling.CLIAbstraction`` v0.4.1 has been integrated as :mod:`pyTooling.CLIAbstraction` into
  pyTooling v6.0.0.


.. only:: html

   Feb. 2022 - Major Update
   ------------------------

.. only:: latex

   .. rubric:: Major Update

* Reworked names of Argument classes.
* Added missing argument formats like PathArgument.
* Added more unit tests and improved code-coverage.
* Added doc-strings and extended documentation pages.


.. only:: html

   Dec. 2021 - Extracted CLIAbstraction from pyIPCMI
   -------------------------------------------------

.. only:: latex

   .. rubric:: Extracted CLIAbstraction from pyIPCMI

* The CLI abstraction has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


CommonClasses
=============

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.CommonClasses`` v0.2.3 has been integrated as :mod:`pyTooling.CommonClasses` into
  pyTooling vX.X.X.


.. only:: html

   Feb. 2021 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Feb. 2021 - Initial Release

* Added ``Version`` class.


Exceptions
==========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.Exceptions`` v1.1.1 has been integrated as :mod:`pyTooling.Exceptions` into
  pyTooling vX.X.X.


.. only:: html

   Sep. 2020 - Unit tests
   ----------------------

.. only:: latex

   .. rubric:: Sep. 2020 - Unit tests

* Added unit tests.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* An initial set of exceptions has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


GenericPath
===========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.GenericPath`` v0.2.5 has been integrated as :mod:`pyTooling.GenericPath` into
  pyTooling vX.X.X.

.. only:: html

   Dec. 2021 - Namespace package
   -----------------------------

.. only:: latex

   .. rubric:: Dec. 2021 - Namespace package

* Renamed ``pyGenericPath`` to :mod:`pyTooling.GenericPath`.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* An initial set of exceptions has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


MetaClasses
===========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.MetaClasses`` v1.3.1 has been integrated as :mod:`pyTooling.MetaClasses` into
  pyTooling vX.X.X.


.. only:: html

   Aug. 2020 - Overloading
   -----------------------

.. only:: latex

   .. rubric:: Aug. 2020 - Overloading

* First implementation of method overloading via a meta-class.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* First singleton metaclass to implement the singleton pattern in Python.


Packaging
=========

.. only:: html

   Dec. 2021 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Dec. 2021 - Direct integration into pyTooling

* The namespace package ``pyTooling.Packaging`` v0.5.0 has been integrated as :mod:`pyTooling.Packaging` into
  pyTooling vX.X.X.


.. only:: html

   Nov. 2021 - Major enhancements
   ------------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Major enhancements

* Reading package information from Python source code via Python's AST.
* Support more licenses.


.. only:: html

   Nov. 2021 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Initial Release

* Abstract setuptools.setup to ease handling of Python package descriptions.
* Read long description from README.md
* Read package dependencies from requirements.txt
* Construct classifiers
* Construct URLs for packages hosted on GitHub.


TerminalUI
==========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.TerminalUI`` v1.5.9 has been integrated as :mod:`pyTooling.TerminalUI` into pyTooling
  vX.X.X.


.. only:: html

   Nov. 2021 - Namespace package
   -----------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Namespace package

* Renamed ``pyTerminalUI`` to :mod:`pyTooling.TerminalUI`.


.. only:: html

   Aug. 2020 - Enhancements
   ------------------------

.. only:: latex

   .. rubric:: Aug. 2020 - Enhancements

* New ``ExitOnPrevious***`` methods.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* TerminalUI has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.
* Basic functionality to use a text based application in a terminal window.
