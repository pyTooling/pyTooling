.. _PACKAGING:

Overview
########

The module :mod:`pyTooling.Packaging` provides helper functions to achieve a *single-source-of-truth* Python package
description, where (almost) no information is duplicated. The main idea is to read configuration files, READMEs, and
Python source files from ``setup.py``, so it doesn't duplicate information. This allows an easier the maintenance of
Python packages.

.. #contents:: Table of Contents
   :depth: 2

.. _PACKAGING/Helper:

Helper Functions
################

The following helper functions are used by :func:`~pyTooling.Packaging.DescribePythonPackage`, but these can also be
called individually to reuse internal features offered by that package description function.

.. _PACKAGING/Helper/loadReadmeFile:

loadReadmeFile
**************

The function :func:`~pyTooling.Packaging.loadReadmeFile` reads a ``README`` file and guesses the contents MIME type on
the file's extension. It returns an instance of :class:`~pyTooling.Packaging.Readme`.

This read text can then be used for the package's *long description*.

.. topic:: Supported file formats

   * ``*.txt`` - Plain text
   * ``*.md`` - `Markdown <https://daringfireball.net/projects/markdown/>`__ (further reading: :wiki:`Markdown`)
   * ``*.rst`` - `ReStructured Text <https://docutils.sourceforge.io/rst.html>`__ (further reading: :wiki:`ReStructuredText`)

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Usage in a ``setup.py``

         .. code-block:: Python

            from pathlib import Path
            from pyTooling.Packaging import loadReadmeFile

            readmeFile = Path("README.md")
            readme = loadReadmeFile(readmeFile)
            # print(readme.Content)
            # print(readme.MimeType)

   .. grid-item::
      :columns: 6

      .. admonition:: ``README.md``

         .. code-block:: Markdown

            # pyTooling

            **pyTooling** is a powerful collection of arbitrary useful abstract data models, missing classes,
            decorators, a new performance boosting meta-class and enhanced exceptions. It also provides lots of helper
            functions e.g. to ease the handling of package descriptions or to unify multiple existing APIs into a single
            API.


.. _PACKAGING/Helper/loadRequirementsFile:

loadRequirementsFile
********************

The function :func:`~pyTooling.Packaging.loadRequirementsFile` recursively reads a ``requirements.txt`` file and
extracts all specified dependencies. As a result, a list of requirement strings is returned.

.. topic:: Features

   * Comments are skipped.
   * Recursive references are followed.
   * Special dependency entries like Git repository references are translates to match the syntax expected by setuptools.

.. warning::

   The returned list might contain duplicates, which should be removed before further processing.

   This can be achieve by converting the result to a :class:`set` and back to a :class:`list`.

   .. code-block:: Python

      requirements = list(set(loadRequirementsFile(requirementsFile)))

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Usage in a ``setup.py``

         .. code-block:: Python

            from pathlib import Path
            from pyTooling.Packaging import loadRequirementsFile

            requirementsFile = Path("doc/requirements.txt")
            requirements = loadRequirementsFile(requirementsFile)
            # for req in requirements:
            #   print(req)

   .. grid-item::
      :columns: 6

      .. admonition:: ``requirements.txt``

         .. code-block::

            -r ../requirements.txt

            Sphinx ~= 9.1
            docutils >= 0.22.0

            sphinx_rtd_theme ~= 3.1


.. _PACKAGING/Helper/extractVersionInformation:

extractVersionInformation
*************************

The function :func:`~pyTooling.Packaging.extractVersionInformation` extracts version information from a Python source
file (module). Usually these module variables are defined in a ``__init__.py`` file.

.. rubric:: Supported fields

* Author name (``__author__``)
* Author email address (``__email__``)
* Copyright information (``__copyright_``)
* License name (``__license__``)
* Version number (``__version__``)
* Keywords (``__keywords__``)

The package's short description has no dunder variable, because a package already describes itself: it is the
**summary** of the source file's module doc-string, read with :func:`~pyTooling.Documentation.splitDocString`. It is
folded into a single line, and emphasis around the whole paragraph is removed - ``**An abstract VHDL language
model.**`` is markup for the rendered documentation, and nothing renders it where a short description is displayed.

A description longer than :data:`~pyTooling.Documentation.DEFAULT_MAXIMUM_SUMMARY_LENGTH` characters is rejected with
a :exc:`~pyTooling.Documentation.DocumentationError`: a first paragraph that long is a body that lost its summary,
and it is not a *short* description. See :ref:`DOC/SummaryLength`.

The function returns an instance of :class:`~pyTooling.Packaging.VersionInformation`, which offers the gathered
information as properties.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Usage in ``setup.py``

         .. code-block:: python

            from setuptools import setup
            from pyTooling.Packaging import extractVersionInformation

            file = Path("./pyTooling/Common/__init__.py")
            versionInfo = extractVersionInformation(file)

            setup(
              # ...
              version=versionInformation.Version,
              author=versionInformation.Author,
              author_email=versionInformation.Email,
              description=versionInformation.Description,
              keywords=versionInformation.Keywords,
              # ...
            )

   .. grid-item::
      :columns: 6

      .. admonition:: ``__init__.py``

         .. code-block:: python

            """
            Common types, helper functions and classes.

            This second paragraph is not part of the short description.
            """
            __author__ =    "Patrick Lehmann"
            __email__ =     "Paebbels@gmail.com"
            __copyright__ = "2017-2026, Patrick Lehmann"
            __license__ =   "Apache License, Version 2.0"
            __version__ =   "1.10.1"
            __keywords__ =  ["decorators", "meta classes", "exceptions", "platform", "versioning"]


.. _PACKAGING/Descriptions:

PackageDescriptions
###################

.. _PACKAGING/Descriptions/Python:

DescribePythonPackage
*********************

:func:`~pyTooling.Packaging.DescribePythonPackage` is a helper function to describe a Python package. The result is a
dictionary that can be handed over to :func:`setuptools.setup`. Some information will be gathered implicitly from
well-known files (e.g. ``README.md``, ``requirements.txt``, ``__init__.py``).

Handling of namespace packages
==============================

If parameter ``packageName`` contains a dot, a namespace package is assumed. Then
:func:`setuptools.find_namespace_packages` is used to discover package files. |br|
Otherwise, the package is considered a normal package and :func:`setuptools.find_packages` is used.

In both cases, the following packages (directories) are excluded from search:

* ``build``, ``build.*``
* ``dist``, ``dist.*``
* ``doc``, ``doc.*``
* ``tests``, ``tests.*``

Handling of minimal Python version
==================================

The minimal required Python version is selected from parameter ``pythonVersions``.

Handling of the description
===========================

If parameter ``description`` is not specified, the first paragraph of the module doc-string in
``sourceFileWithVersion`` is used, so a package is described in one place instead of two. An explicitly passed
description always wins - including an empty one.

If neither is available, a :exc:`~pyTooling.Packaging.PackagingError` is raised, because a package published
without a description is worse than a failing ``setup.py``.

.. note::

   The doc-string that is read is the one of the file named by ``sourceFileWithVersion``. For a namespace package
   whose dunder variables live in a sub-package - like ``pyTooling/Common/__init__.py`` - that doc-string describes
   the sub-package, not the distribution, so such a package passes ``description`` explicitly.

Handling of dunder variables
============================

A Python source file specified by parameter ``sourceFileWithVersion`` will be analyzed with Pythons parser and the
resulting AST will be searched for the following dunder variables:

* ``__author__``: :class:`str`
* ``__copyright__``: :class:`str`
* ``__email__``: :class:`str`
* ``__keywords__``: :class:`typing.Iterable`[:class:`str`]
* ``__license__``: :class:`str`
* ``__version__``: :class:`str`

The gathered information be used to add further mappings in the result dictionary.

Handling of package classifiers
===============================

To reduce redundantly provided parameters to this function (e.g. supported ``pythonVersions``), only additional
classifiers should be provided via parameter ``classifiers``. The supported Python versions will be implicitly
converted to package classifiers, so no need to specify them in parameter ``classifiers``.

The following classifiers are implicitly handled:

license
  The license specified by parameter ``license`` is translated into a classifier. |br|
  See also :meth:`pyTooling.Licensing.License.PythonClassifier`

Python versions
  Always add ``Programming Language :: Python :: 3 :: Only``. |br|
  For each value in ``pythonVersions``, one ``Programming Language :: Python :: Major.Minor`` is added.

Development status
  The development status specified by parameter ``developmentStatus`` is translated to a classifier and added.

.. seealso::

   `Python package classifiers <https://pypi.org/classifiers/>`__

Handling of extra requirements
==============================

If additional requirement files are provided, e.g. requirements to build the documentation, then *extra*
requirements are defined. These can be installed via ``pip install packageName[extraName]``. If so, an extra called
``all`` is added, so developers can install all dependencies needed for package development.

``doc``
  If parameter ``documentationRequirementsFile`` is present, an extra requirements called ``doc`` will be defined.
``test``
  If parameter ``unittestRequirementsFile`` is present, an extra requirements called ``test`` will be defined.
``build``
  If parameter ``packagingRequirementsFile`` is present, an extra requirements called ``build`` will be defined.
User-defined
  If parameter ``additionalRequirements`` is present, an extra requirements for every mapping entry in the
  dictionary will be added.
``all``
  If any of the above was added, an additional extra requirement called ``all`` will be added, summarizing all
  extra requirements.

.. _PACKAGING/Descriptions/License:

Handling of the license
=======================

A package states its license as an **SPDX expression** in the ``license`` field, taken from the ``license``
parameter's :attr:`~pyTooling.Licensing.License.SPDXIdentifier`:

.. code-block:: Python

   license=Apache_2_0_License      # -> license = "Apache-2.0"

A ``License ::`` classifier passed through the ``classifiers`` parameter is **kept** - it is the caller's
statement, not this function's, and dropping it silently would hide what they wrote - but it is reported in the
``setup.py`` output, where the rest of this function's messages go:

.. code-block:: text

   [pyTooling.Packaging] License classifiers are deprecated: 'License :: OSI Approved :: MIT License'.
   [pyTooling.Packaging]   Remove them; the 'license' parameter becomes the SPDX expression setuptools wants.

.. note::

   A bare license identifier **is** an SPDX expression - the simplest one the grammar allows. What cannot be
   expressed is a **compound** expression like ``MIT OR Apache-2.0`` or
   ``GPL-2.0-or-later WITH Classpath-exception-2.0``, because a :class:`~pyTooling.Licensing.License` carries one
   identifier. A package under more than one license passes the expression as a string to ``setuptools.setup()``
   itself.

.. seealso::

   :pep:`639`
      |rarr| Improving license clarity with SPDX license expressions - what the ``license`` field means and why the
      classifiers were deprecated.
   `SPDX license expressions <https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/>`__
      |rarr| The grammar: a simple expression is a license identifier, and ``AND``, ``OR`` and ``WITH`` combine
      them.
   `SPDX license list <https://spdx.org/licenses/>`__
      |rarr| The identifiers themselves. :data:`~pyTooling.Licensing.SPDX_INDEX` holds the ones pyTooling
      predefines.

:attr:`~pyTooling.Licensing.License.PythonClassifier` remains available for a caller that needs the classifier for
something else.

Handling of keywords
====================

If parameter ``keywords`` is not specified, the dunder variable ``__keywords__`` from ``sourceFileWithVersion``
will be used. Otherwise, the content of the parameter, if not None or empty.

.. _PACKAGING/Descriptions/EntryPoints:

Handling of entry points
========================

A package advertises what it offers through *entry point groups*, but a caller of these functions says **what it
provides**, not which group that is declared in:

.. code-block:: Python

   consoleScripts={"prog":     "myPackage.CLI:main"},   # -> console_scripts
   guiScripts={"prog-gui":     "myPackage.GUI:main"},   # -> gui_scripts
   pytestPlugins={"myPlugin":  "myPackage.PyTest"},     # -> pytest11

``guiScripts`` is ``consoleScripts`` for a windowed program: on Windows, such an entry point is generated against
``pythonw`` and starts without a console window.

``pytestPlugins`` also adds the classifier ``Framework :: Pytest``, so a package that ships a plugin says so on
PyPI without the caller having to repeat itself. It is not added twice if ``classifiers`` already lists it.

Any of them may be given together, and a package that advertises nothing gets no ``entry_points`` at all.

.. topic:: Why not a general parameter?

   An earlier draft took a general ``entryPoints={"pytest11": {...}}`` mapping. It was rejected deliberately: the
   point of :func:`~pyTooling.Packaging.DescribePythonPackage` is to *abstract* packaging, so knowing that a pytest
   plugin lives in a group called ``pytest11`` - and that it also wants a classifier - belongs here rather than in
   every :file:`setup.py`. A named parameter per kind of thing keeps that knowledge in one place.


.. _PACKAGING/Descriptions/GitHub:

DescribePythonPackageHostedOnGitHub
***********************************

:func:`~pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` is a helper function to describe a Python package when
the source code is hosted on GitHub.

This is a wrapper for :func:`~pyTooling.Packaging.DescribePythonPackage`, because some parameters can be simplified by
knowing the GitHub namespace and repository name: issue tracker URL, source code URL, ...

.. todo::

   normal packages
     ``PackageName``
   namespace package root package
     ``NamespacePackage.*``
   namespace package sub package
     ``NamespacePackage.PackageName``

   deriving URLs

.. admonition:: Usage in ``setup.py``

   .. code-block:: Python

      from setuptools          import setup

      from pathlib             import Path
      from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub

      packageName = "pyTooling.Packaging"

      setup(
        **DescribePythonPackageHostedOnGitHub(
          packageName=packageName,
          gitHubNamespace="pyTooling",
          keywords="Python3 setuptools package wheel installation",
          sourceFileWithVersion=Path(f"{packageName.replace('.', '/')}/__init__.py"),
          developmentStatus="beta",
          pythonVersions=("3.8", "3.9", "3.10")
        )
      )
