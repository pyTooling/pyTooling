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

The extension registers roles for styling inline text, one for inline Python code, and two for breaks - and a
stylesheet for the styles, linked into every HTML page.

.. _DOC/Sphinx/Roles/Style:

Style roles
===========

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. list-table::
         :header-rows: 1
         :widths: 35 65

         * - Role
           - Renders
         * - ``:bolditalic:``
           - :bolditalic:`bold and italic`
         * - ``:underline:``
           - :underline:`underlined`
         * - ``:strike:``
           - :strike:`struck through`
         * - ``:xlarge:``
           - :xlarge:`extra large`
         * - ``:red:``
           - :red:`red`
         * - ``:green:``
           - :green:`green`
         * - ``:blue:``
           - :blue:`blue`
         * - ``:purple:``
           - :purple:`purple`
         * - ``:deletion:``
           - :deletion:`deleted`
         * - ``:addition:``
           - :addition:`added`

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         A :red:`warning` and a :deletion:`removed` word.

      A style role puts CSS classes on the text; the stylesheet gives them their meaning. ``:deletion:`` and
      ``:addition:`` are the two a diff needs.

      Every colour and size is a CSS custom property, so a project changes it without replacing the stylesheet - in
      a stylesheet of its own, listed in ``html_css_files``:

      .. code-block:: CSS

         :root {
           --pyTooling-color-red: #b00020;
         }

      The properties are ``--pyTooling-color-red``, ``-green``, ``-blue``, ``-purple`` and
      ``--pyTooling-xlarge-size``.


.. _DOC/Sphinx/Roles/pycode:

Inline Python code
==================

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``:pycode:`` renders inline Python code, syntax-highlighted: :pycode:`isinstance(value, int)`.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         :pycode:`isinstance(value, int)`


.. _DOC/Sphinx/Roles/Breaks:

Breaks
======

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``|br|`` breaks a line, ``|hr|`` draws a horizontal line - in HTML **and** in LaTeX. They are substitutions,
      appended to ``rst_prolog``, and delegate to the roles ``:br:`` and ``:hr:``. ``|degree|`` writes a degree sign.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         :param value: The first line. |br|
                       The second line.


.. _DOC/Sphinx/CondensedClass:

condensed-class
***************

.. grid:: 2

   .. grid-item::
      :columns: 6

      The ``condensed-class`` directive renders a class' **public interface** as a code block: the class line, its
      class variables, its methods and its properties, each with the signature it is declared with, and ``...`` for
      a body.

      **The source is parsed, not imported.** Annotations appear as they are written - ``Nullable[str]``, not the
      ``Optional[str]`` an import resolves it to - members appear in the order of the file, and the file becomes a
      dependency of the page, so editing the class rebuilds the page.

      Left out is what the surrounding text is for: bodies, doc-strings, private members (one leading underscore),
      and the annotated fields of a slotted class.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. condensed-class:: pyTooling.Stopwatch.Stopwatch
            :members: Methods, Properties

This is how the example renders:

.. condensed-class:: pyTooling.Stopwatch.Stopwatch
   :members: Methods, Properties

.. rst:directive:: .. condensed-class:: <dotted name of a class>

   Renders the interface of the class the argument names. The longest prefix of the name that is a module is
   the module; the rest is the class, and may name a class nested in a class.

   .. rst:directive:option:: members: <kinds>

      The kinds of member to render, separated by commas, in any case: ``ClassVariables``, ``Dunders``,
      ``Methods``, ``Properties`` or ``All``. Default: ``All``.

      A property is a method decorated with ``@property``, ``@readonly``, ``@cached_property`` or as a setter or
      deleter; a dunder is a method named ``__<name>__``.

   .. rst:directive:option:: exclude-members: <names>

      Names of methods not to render, separated by commas.

   .. rst:directive:option:: indent: <columns>

      Width of one indentation level. Default: 2.

   .. rst:directive:option:: width: <columns>

      Column a signature is wrapped at, one parameter per line. Default: 100.

   .. rst:directive:option:: caption: <text>

      A caption for the code block.


.. _DOC/Sphinx/DependencyTable:

dependency-table
****************

The ``dependency-table`` directive renders a project's dependencies as a table - per package the version
required, its license and what it requires in turn - from the requirements themselves rather than by hand. The data
is fetched from the package index while the documentation is built.

.. attention::

   The directive needs the ``pypi`` extra as well: ``pyTooling[sphinx,pypi]``.

.. rubric:: Configuration

A table names an **entrypoint**, which :file:`conf.py` declares:

.. code-block:: Python

   # doc/conf.py
   pyTooling_Dependency_Requirements = {
     "package":       {"file":    "../requirements.txt"},
     "documentation": {"file":    "requirements.txt"},
     "yaml":          {"package": "pyTooling[yaml]"},
   }

Each entrypoint states exactly one of:

``file`` / ``files``
  |rarr| a requirements file, or several, read relative to :file:`conf.py` with their ``-r`` includes followed.
  They are read while :file:`conf.py` is processed, so a path that doesn't exist ends the build with one message.
``package`` / ``packages``
  |rarr| a package, or several, as the package index publishes its **latest release**: ``pyTooling`` for its own
  requirements, ``pyTooling[yaml]`` for what the extra ``yaml`` adds.

.. list-table:: Configuration values in :file:`conf.py`
   :header-rows: 1
   :widths: 40 60

   * - Name
     - Value
   * - ``pyTooling_Dependency_Requirements``
     - The entrypoints, by identifier.
   * - ``pyTooling_Dependency_PackageOverrides``
     - Optional, a YAML file stating the license of a package the index can't answer for, relative to
       :file:`conf.py`.
   * - ``pyTooling_Dependency_IndexURL``
     - Optional, the package index. Default: ``https://pypi.org``.
   * - ``pyTooling_Dependency_APIURL``
     - Optional, the index's JSON API. Default: ``https://pypi.org/pypi/``.

The tables of a build share one view of the index, so a package several tables require is downloaded once. Each
table logs what it cost, and the build ends with the total and the packages whose license couldn't be resolved -
the list the override file answers.

.. rst:directive:: .. dependency-table:: <entrypoint>

   Renders the dependencies of the entrypoint the argument names.

   .. rst:directive:option:: depth: <levels>

      Levels of sub-dependencies to expand. Default: 0, which expands until the tree ends.

   .. rst:directive:option:: simplified-versions: yes | no

      Whether a version constraint is reduced to its lower bound: ``≥9.1`` instead of ``≥9.1, <10``. Default: ``yes``.

   .. rst:directive:option:: version-format: Major | MajorMinor | MajorMinorPatch | All

      How many parts of a version number are printed. Default: ``MajorMinor``.

   .. rst:directive:option:: dependency-format: Package | PackageVersion | PackageLicense | PackageVersionLicense

      What a line of a dependency tree states. Default: ``PackageVersionLicense``.

   .. rst:directive:option:: caption: <text>

      A caption for the table.

.. code-block:: ReST

   .. dependency-table:: package
      :caption: Mandatory dependencies of the pyTooling package.
      :depth: 4

:ref:`DEP` shows the tables pyTooling's own documentation renders.


.. _DOC/Sphinx/XSDGraph:

xsd-graph
*********

.. grid:: 2

   .. grid-item::
      :columns: 6

      The ``xsd-graph`` directive draws an XML schema as a Graphviz graph, from the schema file itself:

      * every complex type is a record of its name, its attributes, and its simple-typed child elements with their
        cardinality;
      * every complex-typed child element is an edge, labelled with its name and cardinality - so containment and
        recursion are edges rather than repeated type names;
      * an enumeration is a node of its own, listing its values;
      * a root element is a double circle.

      The schema is read with :mod:`xmlschema`, part of the ``sphinx`` extra, and drawn by
      :mod:`sphinx.ext.graphviz`, which the extension sets up itself. The schema file becomes a dependency of the
      page.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. xsd-graph:: ../../pyTooling/Resources/TestReport-v0.1.xsd
            :caption: The types of TestReport-v0.1.xsd.

.. rst:directive:: .. xsd-graph:: <path of an XML schema>

   Draws the schema the argument names, relative to the document.

   .. rst:directive:option:: caption: <text>

      A caption under the graph.

:ref:`SCHEMAS` shows the graphs of the schemas pyTooling ships.

.. rubric:: Another schema language

:class:`~pyTooling.Documentation.Sphinx.SchemaGraph.SchemaGraph` is the directive's language-neutral base-class,
and :class:`~pyTooling.Documentation.Sphinx.SchemaGraph.DotGraph` assembles the graph. A directive for another schema
language derives from the base-class, names itself, and overrides ``_RenderGraph()``:

.. code-block:: Python

   class JSONSchemaGraph(SchemaGraph):
     directiveName: str = "json-schema-graph"

     @classmethod
     def _RenderGraph(cls, schemaFile: Path) -> str:
       graph = DotGraph()
       ...
       return str(graph)


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
