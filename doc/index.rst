.. |img-pyTooling-github| image:: https://img.shields.io/badge/PyTooling-pyTooling-323131.svg?logo=github&longCache=true
   :alt: Sourcecode on GitHub
   :height: 22
   :target: https://github.com/PyTooling/pyTooling
.. |img-pyTooling-codelicense| image:: https://img.shields.io/pypi/l/pyTooling?logo=GitHub&label=code%20license
   :alt: Sourcecode License
   :height: 22
.. |img-pyTooling-tag| image:: https://img.shields.io/github/v/tag/PyTooling/pyTooling?logo=GitHub&include_prereleases
   :alt: GitHub tag (latest SemVer incl. pre-release)
   :height: 22
   :target: https://github.com/PyTooling/pyTooling/tags
.. |img-pyTooling-release| image:: https://img.shields.io/github/v/release/PyTooling/pyTooling?logo=GitHub&include_prereleases
   :alt: GitHub release (latest SemVer incl. including pre-releases
   :height: 22
   :target: https://github.com/PyTooling/pyTooling/releases/latest
.. |img-pyTooling-date| image:: https://img.shields.io/github/release-date/PyTooling/pyTooling?logo=GitHub
   :alt: GitHub release date
   :height: 22
   :target: https://github.com/PyTooling/pyTooling/releases
.. |img-pyTooling-lib-dep| image:: https://img.shields.io/librariesio/dependents/pypi/pyTooling?logo=librariesdotio
   :alt: Dependents (via libraries.io)
   :height: 22
   :target: https://github.com/PyTooling/pyTooling/network/dependents
.. |img-pyTooling-gha-pipeline| image:: https://img.shields.io/github/workflow/status/PyTooling/pyTooling/Unit%20Testing,%20Coverage%20Collection,%20Package,%20Release,%20Documentation%20and%20Publish?label=Pipeline&logo=GitHub%20Actions&logoColor=FFFFFF
   :alt: GitHub Workflow - Build and Test Status
   :height: 22
   :target: https://github.com/PyTooling/pyTooling/actions/workflows/Pipeline.yml
.. |img-pyTooling-codacy-quality| image:: https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?logo=Codacy
   :alt: Codacy - Quality
   :height: 22
   :target: https://www.codacy.com/manual/PyTooling/pyTooling
.. |img-pyTooling-codacy-coverage| image:: https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?logo=Codacy
   :alt: Codacy - Line Coverage
   :height: 22
   :target: https://www.codacy.com/manual/PyTooling/pyTooling
.. |img-pyTooling-codecov-coverage| image:: https://img.shields.io/codecov/c/github/PyTooling/pyTooling?logo=Codecov
   :alt: Codecov - Branch Coverage
   :height: 22
   :target: https://codecov.io/gh/PyTooling/pyTooling
.. |img-pyTooling-lib-rank| image:: https://img.shields.io/librariesio/sourcerank/pypi/pyTooling?logo=librariesdotio
   :alt: Libraries.io SourceRank
   :height: 22
   :target: https://libraries.io/github/PyTooling/pyTooling/sourcerank
.. |img-pyTooling-pypi-tag| image:: https://img.shields.io/pypi/v/pyTooling?logo=PyPI&logoColor=FBE072
   :alt: PyPI - Tag
   :height: 22
   :target: https://pypi.org/project/pyTooling/
.. |img-pyTooling-pypi-python| image:: https://img.shields.io/pypi/pyversions/pyTooling?logo=PyPI&logoColor=FBE072
   :alt: PyPI - Python Version
   :height: 22
.. |img-pyTooling-pypi-status| image:: https://img.shields.io/pypi/status/pyTooling?logo=PyPI&logoColor=FBE072
   :alt: PyPI - Status
   :height: 22
.. |img-pyTooling-lib-status| image:: https://img.shields.io/librariesio/release/pypi/pyTooling?logo=librariesdotio
   :alt: Libraries.io status for latest release
   :height: 22
   :target: https://libraries.io/github/PyTooling/pyTooling
.. |img-pyTooling-req-status| image:: https://img.shields.io/requires/github/PyTooling/pyTooling
   :alt: Requires.io
   :height: 22
   :target: https://requires.io/github/PyTooling/pyTooling/requirements/?branch=master
.. |img-pyTooling-rtd| image:: https://img.shields.io/readthedocs/pyTooling?label=ReadTheDocs&logo=readthedocs
   :alt: Read the Docs
   :height: 22
   :target: https://pyTooling.readthedocs.io/
.. |img-pyTooling-doclicense| image:: https://img.shields.io/badge/doc%20license-CC--BY%204.0-green?logo=readthedocs
   :alt: Documentation License
   :height: 22
   :target: LICENSE.md
.. |img-pyTooling-doc| image:: https://img.shields.io/badge/doc-read%20now%20%E2%9E%94-blueviolet?logo=readthedocs
   :alt: Documentation - Read Now!
   :height: 22
   :target: https://pyTooling.readthedocs.io/

|img-pyTooling-github| |img-pyTooling-codelicense| |img-pyTooling-tag| |img-pyTooling-release| |img-pyTooling-date| |img-pyTooling-lib-dep| |br|
|img-pyTooling-gha-pipeline| |img-pyTooling-codacy-quality| |img-pyTooling-codacy-coverage| |img-pyTooling-codecov-coverage| |img-pyTooling-lib-rank| |br|
|img-pyTooling-pypi-tag| |img-pyTooling-pypi-python| |img-pyTooling-pypi-status| |img-pyTooling-lib-status| |img-pyTooling-req-status| |br|
|img-pyTooling-rtd| |img-pyTooling-doclicense| |img-pyTooling-doc|

.. code-block::

                  __  __      _         ____ _
      _ __  _   _|  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___
     | '_ \| | | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|
     | |_) | |_| | |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \
     | .__/ \__, |_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/
     |_|    |___/

pyTooling Documentation
###########################

A collection of MetaClasses for Python.

Introduction
************

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

   CallBy/index
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
