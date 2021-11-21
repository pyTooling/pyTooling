.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyTooling-github| |SHIELD:svg:pyTooling-src-license| |SHIELD:svg:pyTooling-tag| |SHIELD:svg:pyTooling-release| |SHIELD:svg:pyTooling-date| |SHIELD:svg:pyTooling-lib-dep|
   |  |SHIELD:svg:pyTooling-gha-test| |SHIELD:svg:pyTooling-codacy-quality| |SHIELD:svg:pyTooling-codacy-coverage| |SHIELD:svg:pyTooling-codecov-coverage| |SHIELD:svg:pyTooling-lib-rank|
   |  |SHIELD:svg:pyTooling-pypi-tag| |SHIELD:svg:pyTooling-pypi-status| |SHIELD:svg:pyTooling-pypi-python| |SHIELD:svg:pyTooling-lib-status| |SHIELD:svg:pyTooling-req-status|
   |  |SHIELD:svg:pyTooling-doc-license| |SHIELD:svg:pyTooling-ghp-doc|

.. only:: latex

   |SHIELD:png:pyTooling-github| |SHIELD:png:pyTooling-src-license| |SHIELD:png:pyTooling-tag| |SHIELD:png:pyTooling-release| |SHIELD:png:pyTooling-date| |SHIELD:png:pyTooling-lib-dep|
   |SHIELD:png:pyTooling-gha-test| |SHIELD:png:pyTooling-codacy-quality| |SHIELD:png:pyTooling-codacy-coverage| |SHIELD:png:pyTooling-codecov-coverage| |SHIELD:png:pyTooling-lib-rank|
   |SHIELD:png:pyTooling-pypi-tag| |SHIELD:png:pyTooling-pypi-status| |SHIELD:png:pyTooling-pypi-python| |SHIELD:png:pyTooling-lib-status| |SHIELD:png:pyTooling-req-status|
   |SHIELD:png:pyTooling-doc-license| |SHIELD:png:pyTooling-ghp-doc|

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

   Coverage Report ➚ <https://pyTooling.GitHub.io/pyTooling/coverage/>
   Static Type Check Report ➚ <https://pyTooling.GitHub.io/pyTooling/typing/>
   ChangeLog/index
   License
   Doc-License
   Glossary
   genindex
   py-modindex
