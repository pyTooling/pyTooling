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

**pyTooling** is a powerful collection of arbitrary useful classes, decorators,
meta-classes and exceptions. It's useful for any Python-base project independent
if it's a library, framework or CLI tool.


Introduction
************


Package Details
***************

Common Classes
==============

* :mod:`~pyTooling.CallByRef` |br|
  Emulation of *call-by-reference* parameters.
* :mod:`~pyTooling.Versioning` |br|
  Class representations of semantic version (SemVer) and calendar version (CalVer) numbers.


Decorators
==========

* :class:`~pyTooling.Decorators.export` |br|
  Register the given function or class as publicly accessible in a module.


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

* :class:`~pyTooling.MetaClasses.Singleton` |br|
  Allow only a single instance of a class.
* :class:`~pyTooling.MetaClasses.Overloading` |br|
  Overloading Allow method overloading in Python classes. Dispatch method calls based on method signatures (type annotations).



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
   Tutorials/index

.. toctree::
   :caption: Common
   :hidden:

   CallByRef/index
   Versioning/index

.. toctree::
   :caption: Decorators
   :hidden:

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
   :caption: Appendix
   :hidden:

   Coverage Report ➚ <https://pyTooling.github.io/pyTooling/coverage/>
   Static Type Check Report ➚ <https://pyTooling.github.io/pyTooling/typing/>
   ChangeLog/index
   License
   Doc-License
   Glossary
   genindex
   py-modindex
