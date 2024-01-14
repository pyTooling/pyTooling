.. _NEWS:

News
####

See `pyTooling Release Pages <https://github.com/pyTooling/pyTooling/releases>`__ for detail release notes on every
release.

Jan. 2024 - Version 6
*********************

**Release Page:** `v6.0.0 <https://github.com/pyTooling/pyTooling/releases/v6.0.0>`__

* Integrated ``pyAttributes`` v2.5.1 as :mod:`pyTooling.Attributes`.
* Integrated :mod:`pyTooling.CLIAbstraction` v0.4.1.

Jul. 2023 - Version 5
*********************

**Release Page:** `v5.0.0 <https://github.com/pyTooling/pyTooling/releases/v5.0.0>`__

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

Mar. 2023 - Version 4
*********************

**Release Page:** `v4.0.1 <https://github.com/pyTooling/pyTooling/releases/v4.0.1>`__

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

Mar. 2023 - Version 3
*********************

**Release Page:** `v3.0.0 <https://github.com/pyTooling/pyTooling/releases/v3.0.0>`__

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
