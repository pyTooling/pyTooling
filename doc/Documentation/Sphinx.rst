.. _DOC/Sphinx:

Sphinx Extension
################

:mod:`pyTooling.Documentation.Sphinx` is a Sphinx extension providing the roles and directives pyTooling's
documentation uses - and any other project's documentation can use. It is enabled in :file:`conf.py`:

.. code-block:: Python

   # doc/conf.py
   extensions = [
     ...,
     "pyTooling.Documentation.Sphinx",
   ]

.. attention::

   The extension needs Sphinx and docutils, which :mod:`pyTooling` itself does not depend on. Install it as
   ``pyTooling[sphinx]``, which requires **Python 3.12 or newer**.

.. contents:: Contents of this page
   :local:
   :depth: 1


.. _DOC/Sphinx/Roles:

Roles
*****

.. todo:: DOC::Sphinx - document the style roles, the ``:pycode:`` role and the ``|br|``/``|hr|`` substitutions.


.. _DOC/Sphinx/CondensedClass:

condensed-class
***************

.. rst:directive:: .. condensed-class:: <dotted name of a class>

   Renders a class' public interface from its source.

.. todo:: DOC::Sphinx - document the ``condensed-class`` directive: its argument, its options and an example.


.. _DOC/Sphinx/DependencyTable:

dependency-table
****************

.. rst:directive:: .. dependency-table::

   Renders a project's dependencies from its requirements files.

.. todo:: DOC::Sphinx - document the ``dependency-table`` directive, its options, and the configuration values it
   reads from :file:`conf.py`.


.. _DOC/Sphinx/XSDGraph:

xsd-graph
*********

.. rst:directive:: .. xsd-graph:: <path of an XML schema>

   Draws an XML schema as a Graphviz graph.

.. todo:: DOC::Sphinx - document the ``xsd-graph`` directive: its argument, its option, what the graph shows, and
   the base-class :class:`~pyTooling.Documentation.Sphinx.SchemaGraph.SchemaGraph` for another schema language.


.. _DOC/Sphinx/Shields:

shields
*******

.. grid:: 2

   .. grid-item::
      :columns: 6

      The ``shields`` directive renders a project's badges from `shields.io <https://shields.io/>`__ - where the
      project lives, how it is licensed, whether it builds, where it is published.

      The **options** state the project's coordinates: its GitHub repository, its PyPI package, its licenses, its
      workflow and its documentation's URL. The **content** names the badges and is the layout: badges appear in the
      order written, and each line is a row.

      A badge needs only the options it is made of, so a project states what its badges use and nothing else.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. shields::
            :github:                pyTooling/pyTooling
            :pypi:                  pyTooling
            :codacy:                08ef744c0b70490289712b02a7a4cebe
            :source-license:        github:LICENSE.md
            :documentation-license: CC-BY-4.0 github:doc/Doc-License.rst
            :github-action:         Pipeline.yml@main
            :documentation:         github-pages

            github, src-license, ghp-doc, doc-license
            pypi-tag, pypi-status, pypi-python
            github-action, lib-status, codacy-quality, codacy-coverage, codecov-coverage

This is how the example renders:

.. shields::
   :github:                pyTooling/pyTooling
   :pypi:                  pyTooling
   :codacy:                08ef744c0b70490289712b02a7a4cebe
   :source-license:        github:LICENSE.md
   :documentation-license: CC-BY-4.0 github:doc/Doc-License.rst
   :github-action:         Pipeline.yml@main
   :documentation:         github-pages

   github, src-license, ghp-doc, doc-license
   pypi-tag, pypi-status, pypi-python
   github-action, lib-status, codacy-quality, codacy-coverage, codecov-coverage


.. _DOC/Sphinx/Shields/Options:

Options
=======

.. rst:directive:: .. shields::

   Renders a project's badges, in rows. Each line of the content is a row of badge identifiers, separated by commas.

   .. rst:directive:option:: github: <organization>/<repository>

      The GitHub repository, for the badges showing it and for ``github:`` links.

   .. rst:directive:option:: pypi: <package>

      The package's name on PyPI.

   .. rst:directive:option:: codacy: <project ID>

      The Codacy project ID, as shown in Codacy's badge settings.

   .. rst:directive:option:: gitter: <room>

      The Gitter room, e.g. ``hdl/community``.

   .. rst:directive:option:: source-license: [<SPDX expression> ]<link>

      Where the source code's license is written. Without a license before the link, the badge shows what PyPI
      reports for the package when :rst:dir:`shields:pypi` is stated, and what GitHub reports for the repository
      otherwise.

   .. rst:directive:option:: documentation-license: <SPDX expression> <link>

      The documentation's license and where it is written. The license is required: nothing reports a
      documentation's license.

   .. rst:directive:option:: github-action: <workflow file>[@<branch>]

      The workflow whose status is shown. Without a branch, the badge shows the workflow's latest run on any branch.

   .. rst:directive:option:: documentation: github-pages | <URL>

      Where the documentation is published. ``github-pages`` is the GitHub Pages site of
      :rst:dir:`shields:github`; any other value is an ``http://`` or ``https://`` URL.

   .. rst:directive:option:: class: <CSS classes>

      Additional CSS classes on the rows.

.. rubric:: Links

:rst:dir:`shields:source-license` and :rst:dir:`shields:documentation-license` end in a link, which is one of:

``github:<path>``
  |rarr| the file at ``<path>`` on the default branch of the repository :rst:dir:`shields:github` names.
``http://…`` or ``https://…``
  |rarr| used as written.

.. rubric:: Licenses

A license is an `SPDX license expression <https://spdx.github.io/spdx-spec/v2.3/SPDX-license-expressions/>`__,
parsed by :meth:`LicenseExpression.Parse() <pyTooling.Licensing.LicenseExpression.Parse>`: ``Apache-2.0``,
``CC-BY-4.0`` or ``MIT OR Apache-2.0``. A misspelt identifier is reported. A license that isn't on the SPDX License
List is written ``LicenseRef-<name>``.


.. _DOC/Sphinx/Shields/Badges:

Badges
======

.. list-table::
   :header-rows: 1
   :widths: 20 45 35

   * - Identifier
     - Shows
     - Options
   * - ``github``
     - the repository
     - ``github``
   * - ``src-license``
     - the source code's license
     - ``source-license``
   * - ``doc-license``
     - the documentation's license
     - ``documentation-license``
   * - ``ghp-doc``
     - whether the documentation is online
     - ``documentation``
   * - ``tag``
     - the latest tag, including pre-releases
     - ``github``
   * - ``date``
     - the date of the latest release
     - ``github``
   * - ``github-action``
     - the workflow's status
     - ``github``, ``github-action``
   * - ``codacy-quality``
     - Codacy's code quality grade
     - ``github``, ``codacy``
   * - ``codacy-coverage``
     - Codacy's line coverage
     - ``github``, ``codacy``
   * - ``codecov-coverage``
     - Codecov's branch coverage
     - ``github``
   * - ``pypi-tag``
     - the latest version on PyPI
     - ``pypi``
   * - ``pypi-status``
     - the development status on PyPI
     - ``pypi``
   * - ``pypi-python``
     - the Python versions on PyPI
     - ``pypi``
   * - ``lib-status``
     - whether the dependencies are up to date, by Libraries.io
     - ``pypi``
   * - ``lib-rank``
     - the SourceRank, by Libraries.io
     - ``pypi``
   * - ``lib-dep``
     - how many repositories depend on the package
     - ``github``, ``pypi``
   * - ``gitter``
     - a link to the Gitter room
     - ``gitter``

A ``github:`` link, a license GitHub reports, and ``github-pages`` need :rst:dir:`shields:github` as well.


.. _DOC/Sphinx/Shields/Output:

HTML and LaTeX
==============

The directive emits both variants, each wrapped in an :rst:dir:`only` node: HTML embeds the SVG from
``img.shields.io``, LaTeX the PNG from ``raster.shields.io`` - a PDF cannot embed an SVG.


.. _DOC/Sphinx/Shields/Errors:

Errors
======

A mistake is reported on the page, where the badges would be, and in the build's log:

.. code-block:: text

   shields: 'gha-test' is not a known badge. Known are: codacy-coverage, codacy-quality, codecov-coverage, ...
   shields: Badge 'pypi-tag' needs option ':pypi:'.
   shields: Option ':github:' is 'pyTooling', not '<organization>/<repository>'.
   shields: Option ':source-license:' links to 'LICENSE.md', neither 'github:<path>' nor a URL.
   shields: Option ':documentation-license:' states 'CC-BY-5.0', which isn't an SPDX license expression.
