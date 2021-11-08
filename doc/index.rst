.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:PyTooling-github| |SHIELD:svg:PyTooling-src-license| |SHIELD:svg:PyTooling-tag| |SHIELD:svg:PyTooling-release| |SHIELD:svg:PyTooling-date| |SHIELD:svg:PyTooling-lib-dep|
   |  |SHIELD:svg:PyTooling-gha-test| |SHIELD:svg:PyTooling-codacy-quality| |SHIELD:svg:PyTooling-codacy-coverage| |SHIELD:svg:PyTooling-codecov-coverage| |SHIELD:svg:PyTooling-lib-rank|
   |  |SHIELD:svg:PyTooling-pypi-tag| |SHIELD:svg:PyTooling-pypi-status| |SHIELD:svg:PyTooling-pypi-python| |SHIELD:svg:PyTooling-lib-status| |SHIELD:svg:PyTooling-req-status|
   |  |SHIELD:svg:PyTooling-doc-license| |SHIELD:svg:PyTooling-ghp-doc|

.. only:: latex

   |SHIELD:png:PyTooling-github| |SHIELD:png:PyTooling-src-license| |SHIELD:png:PyTooling-tag| |SHIELD:png:PyTooling-release| |SHIELD:png:PyTooling-date| |SHIELD:png:PyTooling-lib-dep|
   |SHIELD:png:PyTooling-gha-test| |SHIELD:png:PyTooling-codacy-quality| |SHIELD:png:PyTooling-codacy-coverage| |SHIELD:png:PyTooling-codecov-coverage| |SHIELD:png:PyTooling-lib-rank|
   |SHIELD:png:PyTooling-pypi-tag| |SHIELD:png:PyTooling-pypi-status| |SHIELD:png:PyTooling-pypi-python| |SHIELD:png:PyTooling-lib-status| |SHIELD:png:PyTooling-req-status|
   |SHIELD:png:PyTooling-doc-license| |SHIELD:png:PyTooling-ghp-doc|

--------------------------------------------------------------------------------

pyTooling Documentation
#######################

pyTooling is a powerfull collection of decorators, meta-classes, exceptions and
common classes useful for any Python-base project independent if it's a library,
framework or CLI tool.


Introduction
************


Package Details
***************

Common
======

* :ref:`Common:CallByRef` - Handover any data as call-by reference.

A Python meta class is a class used to construct instances of other classes.
Python has one default meta class called :py:class:`type`. It's possible to
write new meta classes from scratch or to derive subclasses from :py:class:`type`.

Meta classes are used by passing a named parameter to a class definition in
addition to a list of classes for inheritance.

.. code-block:: Python

   class Foo(Bar, metaclass=type):
     pass


List of meta classes
********************

* :py:class:`pyTooling.Singleton`
* :py:class:`pyTooling.Overloading`


Contributors
************

* `Patrick Lehmann <https://github.com/PyTooling>`_ (Maintainer)
* `and more... <https://github.com/pyTooling/pyCallBy/graphs/contributors>`__



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
   Dependencies

.. toctree::
   :caption: Common
   :hidden:

   CallByRef/index
   Versioning/Version

.. toctree::
   :caption: Decorators
   :hidden:

   Decorators/index

.. toctree::
   :caption: Exceptions
   :hidden:

   Exceptions/ExceptionBase
   Exceptions/Predefined

.. toctree::
   :caption: Meta Classes
   :hidden:

   MetaClasses/Overloading
   MetaClasses/Singleton

.. toctree::
   :caption: Appendix
   :hidden:

   coverage/index
   typing/index
   ChangeLog/index
   License
   Doc-License
   Glossary
   genindex
   py-modindex
