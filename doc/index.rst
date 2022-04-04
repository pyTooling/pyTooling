.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyTooling-github| |SHIELD:svg:pyTooling-src-license| |SHIELD:svg:pyTooling-ghp-doc| |SHIELD:svg:pyTooling-doc-license|
   |  |SHIELD:svg:pyTooling-pypi-tag| |SHIELD:svg:pyTooling-pypi-status| |SHIELD:svg:pyTooling-pypi-python|
   |  |SHIELD:svg:pyTooling-gha-test| |SHIELD:svg:pyTooling-lib-status| |SHIELD:svg:pyTooling-codacy-quality| |SHIELD:svg:pyTooling-codacy-coverage| |SHIELD:svg:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:svg:pyTooling-lib-dep| |SHIELD:svg:pyTooling-req-status| |SHIELD:svg:pyTooling-lib-rank|

.. only:: latex

   |SHIELD:png:pyTooling-github| |SHIELD:png:pyTooling-src-license| |SHIELD:png:pyTooling-ghp-doc| |SHIELD:png:pyTooling-doc-license|
   |SHIELD:png:pyTooling-pypi-tag| |SHIELD:png:pyTooling-pypi-status| |SHIELD:png:pyTooling-pypi-python|
   |SHIELD:png:pyTooling-gha-test| |SHIELD:png:pyTooling-lib-status| |SHIELD:png:pyTooling-codacy-quality| |SHIELD:png:pyTooling-codacy-coverage| |SHIELD:png:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:png:pyTooling-lib-dep| |SHIELD:png:pyTooling-req-status| |SHIELD:png:pyTooling-lib-rank|

--------------------------------------------------------------------------------

pyTooling Documentation
#######################

**pyTooling** is a powerful collection of arbitrary useful classes, decorators, meta-classes and exceptions. |br|
It's useful for any Python-base project independent if it's a library, framework or CLI tool.


Introduction
************

**pyTooling** is a basic collection of powerful helpers needed by almost any Python project. These are commonly used
classes, decorators meta-classes or exceptions. More specialized helpers can be found in sub-namespaces like:

* pyTooling.CLIAbstraction
* pyTooling.GenericPath
* pyTooling.TerminalUI

In addition, pyTooling provides a collection of CI job templates for GitHub Actions. This drastically simplifies
GHA-based CI pipelines for Python projects.


Package Details
***************

Common Classes
==============

* :py:mod:`~pyTooling.CallByRef` |br|
  Emulation of *call-by-reference* parameters.
* :py:mod:`~pyTooling.Licensing` |br|
  Class representations of licenses and conversions to various structured license names.
* :py:class:`~pyTooling.Common.Platform.Platform` |br|
  A class representing the current platform/environment.
* :py:mod:`~pyTooling.Versioning` |br|
  Class representations of semantic version (SemVer) and calendar version (CalVer) numbers.


Decorators
==========

* :py:class:`~pyTooling.Decorators.export` |br|
  Register the given function or class as publicly accessible in a module.


Exceptions
==========

* :py:exc:`~pyTooling.Exceptions.EnvironmentException` |br|
  ... is raised when an expected environment variable is missing.
* :py:exc:`~pyTooling.Exceptions.PlatformNotSupportedException` |br|
  ... is raise if the platform is not supported.
* :py:exc:`~pyTooling.Exceptions.NotConfiguredException` |br|
  ... is raise if the requested setting is not configured.


Meta-Classes
============

* :py:class:`~pyTooling.MetaClasses.Singleton` |br|
  Allow only a single instance of a class.
* :py:class:`~pyTooling.MetaClasses.Overloading` |br|
  Overloading Allow method overloading in Python classes. Dispatch method calls based on method signatures (type annotations).


Packaging
=========

A set of helper functions to describe a Python package for setuptools.

* Helper Functions:

  * :py:func:`pyTooling.Packaging.loadReadmeFile` |br|
    Load a ``README.md`` file from disk and provide the content as long description for setuptools.
  * :py:func:`pyTooling.Packaging.loadRequirementsFile` |br|
    Load a ``requirements.txt`` file from disk and provide the content for setuptools.
  * :py:func:`pyTooling.Packaging.extractVersionInformation` |br|
    Extract version information from Python source files and provide the data to setuptools.

* Package Descriptions

  * :py:func:`pyTooling.Packaging.DescribePythonPackage` |br|
    tbd
  * :py:func:`pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` |br|
    tbd


Data Structures
===============

Fast data structures.

* Trees:

  * :py:class:`pyTooling.Tree.Node` |br|
    A fast tree data structure.



Contributors
************

* `Patrick Lehmann <https://GitHub.com/pyTooling>`_ (Maintainer)
* `and more... <https://GitHub.com/pyTooling/pyTooling/graphs/contributors>`__


License
*******

.. only:: html

   This Python package (source code) is licensed under `Apache License 2.0 <Code-License.html>`__. |br|
   The accompanying documentation is licensed under `Creative Commons - Attribution 4.0 (CC-BY 4.0) <Doc-License.html>`__.

.. only:: latex

   This Python package (source code) is licensed under **Apache License 2.0**. |br|
   The accompanying documentation is licensed under **Creative Commons - Attribution 4.0 (CC-BY 4.0)**.


------------------------------------

.. |docdate| date:: %b %d, %Y - %H:%M

.. only:: html

   This document was generated on |docdate|.

.. toctree::
   :caption: Overview
   :hidden:

   Installation
   Dependency
   Tutorials/index

.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Common
   :hidden:

   CallByRef
   Platform
   Versioning
   Licensing

.. toctree::
   :caption: Data Structures
   :hidden:

   DataStructures/Tree

.. #
   DataStructures/Graph

.. toctree::
   :caption: Decorators
   :hidden:

   Decorators/Documentation
   Decorators/Visibility

.. toctree::
   :caption: Exceptions
   :hidden:

   Exceptions/BaseExceptions
   Exceptions/PredefinedExceptions

.. toctree::
   :caption: Meta Classes
   :hidden:

   MetaClasses/Overloading
   MetaClasses/Singleton

.. toctree::
   :caption: Packaging
   :hidden:

   Packaging/HelperFunctions
   Packaging/PackageDescriptions

.. raw:: latex

   \part{References}

.. toctree::
   :caption: References
   :hidden:

   pyTooling/index

.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   Coverage Report ➚ <coverage/index>
   Static Type Check Report ➚ <typing/index>
   License
   Doc-License
   Glossary
   genindex
   py-modindex
