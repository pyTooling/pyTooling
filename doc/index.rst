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

**pyTooling** is a powerful collection of arbitrary useful abstract data models, classes, decorators, meta-classes and
exceptions. It also provides lots of helper functions e.g. to ease the handling of package descriptions.

It's useful for **any** Python-base project independent if it's a library, framework or CLI tool.


Introduction
************

**pyTooling** is a basic collection of powerful helpers needed by almost any Python project. More specialized helpers
can be found in sub-namespaces like:

* pyTooling.CLIAbstraction
* pyTooling.TerminalUI

In addition, pyTooling provides a collection of CI job templates for GitHub Actions. This drastically simplifies
GHA-based CI pipelines for Python projects.


Package Details
***************

Common Functions
================

This is a set of useful :ref:`helper functions <COMMON/HelperFunctions>`:

* :ref:`COMMON/Helper/getsizeof` calculates the "real" size of a data structure.
* :ref:`COMMON/Helper/isnestedclass` checks if a class is nested inside another class.
* :ref:`COMMON/Helper/mergedicts` merges multiple dictionaries into a new dictionary.
* :ref:`COMMON/Helper/zipdicts` iterate multiple dictionaries simultaneously.


Common Classes
==============

* Emulations of :ref:`Call-by-reference parameters <COMMON/CallByRef>` are provided by the :py:mod:`pyTooling.CallByRef` module.
* Classes representing :ref:`unifyed license names <LICENSING>` and mappings are provided by the :py:mod:`pyTooling.Licensing` module.
* The :ref:`current platform/environment <COMMON/Platform>` Python is running in, can be access unifying multiple platform APIs
  provided by Python and summarizing the information in a single class instance.
* :ref:`Representations of version numbers <VERSIONING>` |br|
  |rarr| Class representations of semantic version (SemVer) and calendar version (CalVer) numbers are provided by the
  :py:mod:`pyTooling.Versioning` module.


Configuration
=============

Abstraction of various configuration file formats.

* :ref:`Abstract configuration file data model <CONFIG>` |br|
  |rarr| An abstract data model of configuration files supporting sequences (lists) and key-value-pairs (dictionaries).
* :ref:`YAML configuration reader <CONFIG/FileFormat/YAML>` |br|
  |rarr| A configuration file reader for the YAML file format.


Data Structures
===============

Fast and powerful data structures.

* :ref:`Tree data structure <STRUCT/Tree>` |br|
  |rarr| A fast and simple implementation using a single :py:class:`pyTooling.Tree.Node` class.
* :ref:`Graph data structure <STRUCT/Graph>` |br|
  |rarr| A directed graph implementation using a :py:class:`pyTooling.Graph.Vertex` and :py:class:`pyTooling.Graph.Edge`
  class.
* :ref:`Path data structure <STRUCT/Path>` |br|
  |rarr| A directed graph implementation using a :py:class:`pyTooling.Graph.Vertex` and :py:class:`pyTooling.Graph.Edge`
  class.

.. #* :ref:`Scope data structure <STRUCT/Scope>` |br|
   |rarr| A fast and simple implementation using a single :py:class:`pyTooling.Tree.Node` class.


Decorators
==========

* :ref:`Documentation <DECO/Documentation>`

  * Copy the doc-string from given base-class via :py:class:`~pyTooling.Decorators.InheritDocString`.


* :ref:`Visibility <DECO/Visibility>`

  * Register the given function or class as publicly accessible in a module via :py:class:`~pyTooling.Decorators.export`.



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

* :py:class:`~pyTooling.MetaClasses.Overloading` |br|
  ``Overloading`` allows method overloading in Python classes. It dispatches method calls based on method signatures
  (type annotations).
* :py:class:`~pyTooling.MetaClasses.Singleton` |br|
  A class created from meta-class ``Singleton`` allows only a single instance to exist. If a further instance is tried
  to be created, a cached instance will be returned.
* :py:class:`~pyTooling.MetaClasses.SlottedType` |br|
  All type-annotated fields in a class get stored in a slot rather than in ``__dict__``. This improves the memory
  footprint as well as the field access performance of all class instances. The behavior is automatically inherited to
  all derived classes.


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



Contributors
************

* `Patrick Lehmann <https://GitHub.com/Paebbels>`__ (Maintainer)
* `Sven Köhler <https://GitHub.com/skoehler>`__
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

   Common/index
   Common/CallByRef
   Common/Licensing
   Common/Platform
   Common/Versioning

.. toctree::
   :caption: Configuration
   :hidden:

   Configuration/index
   Configuration/FileFormats

.. toctree::
   :caption: Data Structures
   :hidden:

   DataStructures/index
   DataStructures/Graph
   DataStructures/Path/index
   DataStructures/Tree

.. toctree::
   :caption: Decorators
   :hidden:

   Decorators

.. toctree::
   :caption: Exceptions
   :hidden:

   Exceptions

.. toctree::
   :caption: Meta Classes
   :hidden:

   MetaClasses

.. toctree::
   :caption: Packaging
   :hidden:

   Packaging

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   pyTooling/pyTooling
   Unittest Report ➚ <unittests/index>
   Coverage Report ➚ <coverage/index>
   Static Type Check Report ➚ <typing/index>

.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   License
   Doc-License
   Glossary
   genindex
   Python Module Index <modindex>
