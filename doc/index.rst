.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyTooling-github| |SHIELD:svg:pyTooling-src-license| |SHIELD:svg:pyTooling-ghp-doc| |SHIELD:svg:pyTooling-doc-license|
   |  |SHIELD:svg:pyTooling-pypi-tag| |SHIELD:svg:pyTooling-pypi-status| |SHIELD:svg:pyTooling-pypi-python|
   |  |SHIELD:svg:pyTooling-gha-test| |SHIELD:svg:pyTooling-lib-status| |SHIELD:svg:pyTooling-codacy-quality| |SHIELD:svg:pyTooling-codacy-coverage| |SHIELD:svg:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:svg:pyTooling-lib-dep| |SHIELD:svg:pyTooling-lib-rank|

.. only:: latex

   |SHIELD:png:pyTooling-github| |SHIELD:png:pyTooling-src-license| |SHIELD:png:pyTooling-ghp-doc| |SHIELD:png:pyTooling-doc-license|
   |SHIELD:png:pyTooling-pypi-tag| |SHIELD:png:pyTooling-pypi-status| |SHIELD:png:pyTooling-pypi-python|
   |SHIELD:png:pyTooling-gha-test| |SHIELD:png:pyTooling-lib-status| |SHIELD:png:pyTooling-codacy-quality| |SHIELD:png:pyTooling-codacy-coverage| |SHIELD:png:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:png:pyTooling-lib-dep| |SHIELD:png:pyTooling-lib-rank|

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

* `pyTooling.CLIAbstraction <https://github.com/pyTooling/pyTooling.CLIAbstraction>`__

In addition, pyTooling provides a collection of `CI job templates for GitHub Actions <https://github.com/pyTooling/Actions>`__.
This drastically simplifies GHA-based CI pipelines for Python projects.


Package Details
***************

Common Helper Functions
=======================

This is a set of useful :ref:`helper functions <COMMON/HelperFunctions>`:

* :ref:`COMMON/Helper/getsizeof` calculates the "real" size of a data structure.
* :ref:`COMMON/Helper/isnestedclass` checks if a class is nested inside another class.
* :ref:`COMMON/Helper/firstKey`, :ref:`COMMON/Helper/firstValue`, :ref:`COMMON/Helper/firstItem` get the first
  key/value/item from an ordered dictionary.
* :ref:`COMMON/Helper/mergedicts` merges multiple dictionaries into a new dictionary.
* :ref:`COMMON/Helper/zipdicts` iterate multiple dictionaries simultaneously.


Common Classes
==============

* Python doesn't provide :ref:`call-by-reference parameters <COMMON/CallByRef>` for simple types. This behavior can be
  emulated with classes provided by the :mod:`pyTooling.CallByRef` module.
* Setuptools, PyPI, and others have a varying understanding of license names. The :mod:`pyTooling.Licensing` module
  provides :ref:`unified license names <LICENSING>` as well as license name mappings or translations.
* Python has many ways in figuring out the current platform using APIs from ``sys``, ``platform``, ``os``, ….
  Unfortunately, none of the provided standard APIs offers a comprehensive answer. pyTooling provides a
  :ref:`unified platform and environment description <COMMON/Platform>` by summarizing multiple platform APIs into a
  single class instance.
* While Python itself has a good versioning schema, there are no classes provided to abstract version numbers. pyTooling
  provides such a :ref:`representations of version numbers <VERSIONING>` following semantic versioning (SemVer) and
  calendar versioning (CalVer) schemes. It's provided by the :mod:`pyTooling.Versioning` module.


Configuration
=============

Various file formats suitable for configuration information share the same features supporting: key-value pairs
(dictionaries), sequences (lists), and simple types like string, integer and float. pyTooling provides an
:ref:`abstract configuration file data model <CONFIG>` supporting these features. Moreover, concrete
:ref:`configuration file format reader <CONFIG/FileFormat>` implementations are provided as well.

* :ref:`JSON configuration reader <CONFIG/FileFormat/JSON>` for the JSON file format.
* :ref:`TOML configuration reader <CONFIG/FileFormat/TOML>`  |rarr| To be implemented.
* :ref:`YAML configuration reader <CONFIG/FileFormat/YAML>` for the YAML file format.


Data Structures
===============

pyTooling also provides fast and powerful data structures offering object-oriented APIs:

* :ref:`Graph data structure <STRUCT/Graph>` |br|
  |rarr| A directed graph implementation using a :class:`pyTooling.Graph.Vertex` and :class:`pyTooling.Graph.Edge`
  class.
* :ref:`Path data structure <STRUCT/Path>` |br|
  |rarr| To be documented.
* :ref:`Finite State Machine data structure <STRUCT/StateMachine>` |br|
  |rarr| A data model for state machines using :class:`pyTooling.StateMachine.State` and
  :class:`pyTooling.StateMachine.Transition` classes.
* :ref:`Tree data structure <STRUCT/Tree>` |br|
  |rarr| A fast and simple implementation using a single :class:`pyTooling.Tree.Node` class.

.. #* :ref:`Scope data structure <STRUCT/Scope>` |br|
   |rarr| A fast and simple implementation using a single :class:`pyTooling.Tree.Node` class.


Decorators
==========

* :ref:`META/Abstract`

  * Methods marked with :ref:`DECO/AbstractMethod` are abstract and need to be overwritten in a
    derived class. |br|
    An *abstract method* might be called from the overwriting method.
  * Methods marked with :ref:`DECO/MustOverride` are abstract and need to be overridden in a
    derived class. |br|
    It's not allowed to call a *mustoverride method*.

* :ref:`DECO/DataAccess`

  * Methods with :ref:`DECO/readonly` decorator transform a method into a read-only property.
  * ⚠BROKEN⚠: Methods with :ref:`DECO/classproperty` decorator transform methods to class-properties.

* :ref:`DECO/Documentation`

  * Register the given function or class as publicly accessible in a module via :ref:`DECO/export`. |br|
    This is also used by Sphinx extensions to (auto-)document public module members.
  * Copy the doc-string from given base-class via :ref:`DECO/InheritDocString`.

* :ref:`DECO/Misc`

  * The :ref:`DECO/notimplemented` decorator replaces a callable (function or method) with a callable raising a
    :exc:`NotImplementedError`. The original code gets unreachable.
  * If a callable gets replaced or wrapped by a e.g. a decorator, the :ref:`DECO/OriginalFunction` decorator can be used
    to preserve a reference to the original callable.


Exceptions
==========

* :exc:`~pyTooling.Exceptions.EnvironmentException` |br|
  ... is raised when an expected environment variable is missing.
* :exc:`~pyTooling.Exceptions.PlatformNotSupportedException` |br|
  ... is raise if the platform is not supported.
* :exc:`~pyTooling.Exceptions.NotConfiguredException` |br|
  ... is raise if the requested setting is not configured.


Meta-Classes
============

pyTooling provides an :ref:`enhanced meta-class <META>` called :class:`~pyTooling.MetaClasses.ExtendedType`.
This meta-classes allows to implement :ref:`abstract methods <META/Abstract>`, :ref:`singletons <META/Singleton>`,
:ref:`slotted types <META/Slotted>` and combinations thereof.

:pycode:`class MyClass(metaclass=ExtendedType):`
  A class definition using that meta-class can implement :ref:`abstract methods <META/Abstract>` using decorators
  :ref:`DECO/AbstractMethod` or :ref:`DECO/MustOverride`.

:pycode:`class MyClass(metaclass=ExtendedType, singleton=True):`
  A class defined with enabled :ref:`singleton <META/Singleton>` behavior allows only a single instance of that class to
  exist. If another instance is going to be created, a previously cached instance of that class will be returned.

:pycode:`class MyClass(metaclass=ExtendedType, useSlots=True):`
  A class defined with enabled :ref:`useSlots <META/Slotted>` behavior stores instance fields in slots. The meta-class,
  translates all type-annotated fields in a class definition into slots. Slots allow a more efficient field storage and
  access compared to dynamically stored and accessed fields hosted by ``__dict__``. This improves the memory footprint
  as well as the field access performance of all class instances. This behavior is automatically inherited to all
  derived classes.

:pycode:`class MyClass(metaclass=ExtendedType, useSlots=True, mixin=True):`
  A class defined with enabled :ref:`mixin <META/Mixin>` behavior collects instance fields so they can be added to
  slots in a derived class.

:pycode:`class MyClass(SlottedObject):`
  A class definition deriving from :class:`~pyTooling.MetaClasses.SlottedObject` will bring the slotted type behavior to
  that class and all derived classes.


Packaging
=========

A set of helper functions to describe a Python package for setuptools.

* Helper Functions:

  * :func:`pyTooling.Packaging.loadReadmeFile` |br|
    Load a ``README.md`` file from disk and provide the content as long description for setuptools.
  * :func:`pyTooling.Packaging.loadRequirementsFile` |br|
    Load a ``requirements.txt`` file from disk and provide the content for setuptools.
  * :func:`pyTooling.Packaging.extractVersionInformation` |br|
    Extract version information from Python source files and provide the data to setuptools.

* Package Descriptions

  * :func:`pyTooling.Packaging.DescribePythonPackage` |br|
    tbd
  * :func:`pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` |br|
    tbd


Terminal
========

*tbd*

Timer
=====

A :class:`~pyTooling.Timer.Timer` class to measure and accumulate code execution times.


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
   DataStructures/StateMachine
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

.. toctree::
   :caption: Terminal
   :hidden:

   Terminal/index

.. toctree::
   :caption: Timer
   :hidden:

   Timer

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
   TODO
