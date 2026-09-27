.. _DOC/Sphinx/GHA:

GitHub Actions Domain
#####################

The Sphinx domain ``gha`` documents **GitHub Actions workflows** - above all reusable workflows, whose inputs, outputs
and secrets are the interface a caller uses. What the workflow file states - an input's type, whether it is required,
its default - is read from the file with :mod:`pyTooling.CI.GitHub.WorkflowFile`, so a page doesn't copy it and can't
drift from it. What the file can't say stays hand-written, as the content of a directive.

The domain is part of the :ref:`extension <DOC/Sphinx>`, and reads the files with ``ruamel.yaml``, which the
``sphinx`` extra installs: ``pyTooling[sphinx]``.

.. contents:: Contents of this page
   :local:
   :depth: 1


.. _DOC/Sphinx/GHA/Config:

Configuration
*************

.. code-block:: Python

   # doc/conf.py
   gha_repository =         "pyTooling/Actions"      # the documented repository
   gha_workflow_directory = "../.github/workflows"   # relative to the Sphinx source directory
   gha_ref =                "r8"                     # the ref the documentation describes

.. confval:: gha_workflow_directory

   The directory holding the workflow files, relative to the Sphinx source directory. A ``gha:workflow`` without
   ``:file:`` reads ``<name>.yml`` from it. Default: ``None``.

.. confval:: gha_repository

   The documented repository, as ``owner/repo``. A job calling ``owner/repo/.github/workflows/X.yml@<ref>`` is resolved
   to ``X.yml`` in :confval:`gha_workflow_directory`, whatever the ref. Default: ``None``.

.. confval:: gha_ref

   The ref - a branch or tag - of the documented repository the documentation describes, as ``r8``. A job calling a
   workflow of the documented repository at another ref is a warning. ``None`` checks nothing. Default: ``None``.

.. confval:: gha_label_prefix

   The root of the ``:ref:`` labels the directives register besides their targets - see
   :ref:`DOC/Sphinx/GHA/Labels`. ``None`` registers none. Default: ``"JOBTMPL"``.


.. _DOC/Sphinx/GHA/Workflow:

Workflows
*********

.. rst:directive:: .. gha:workflow:: <name>

   Registers the workflow ``<name>`` - its file's stem, as ``Parameters`` - with an index entry, and makes it the
   **current workflow** of the document: every ``gha:input``, ``gha:output`` and ``gha:secret`` following it belongs
   to it, and a role may name its parameters without the workflow's name.

   The directive writes no visible output. Placed above the page's title, its target is the title, as a label is.

   .. rst:directive:option:: file: <path>

      Path to the workflow file, relative to the document. Without it, the file is ``<name>.yml`` in
      :confval:`gha_workflow_directory`.

.. code-block:: ReST

   .. gha:workflow:: Parameters

   Parameters
   ##########

   The ``Parameters`` job template ...

A document using the workflow is read again, when the workflow file changed.


.. _DOC/Sphinx/GHA/Parameters:

Inputs, Outputs and Secrets
***************************

.. grid:: 2

   .. grid-item::
      :columns: 6

      Each of the three directives documents one parameter of the current workflow, as a **section** titled by the
      parameter's name - so it is listed in the page's table of contents - holding a field list:

      #. the fields read from the workflow file: *Type*, *Required* and *Default Value* for an input and a secret,
         where ``— — — —`` says there is no default, and a multi-line default is shown as a block;
      #. the fields of the directive's content, in the order written, as *Possible Values*, *Description* or
         *Example*;
      #. without a hand-written *Description*, the ``description`` of the workflow file, placed behind *Type*,
         *Required*, *Default Value* and *Possible Values*.

      Content after the field list follows it. A workflow file states no type and no default for an **output**, so
      those fields are hand-written there.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         Input Parameters
         ****************

         .. gha:input:: package_name

            :Possible Values: Any valid Python package name.
            :Example:         ``myPackage``

         Outputs
         *******

         .. gha:output:: python_jobs

            :Type:        string (JSON)
            :Description: A JSON array of job descriptions.

.. rst:directive:: .. gha:input:: <name>
.. rst:directive:: .. gha:output:: <name>
.. rst:directive:: .. gha:secret:: <name>

   Documents the input, output or secret ``<name>`` of the current workflow. Its target is ``<Workflow>.<name>``.

.. rst:directive:: .. gha:autoinputs::

   Documents every input of the current workflow the document has no ``gha:input`` for - also those whose
   ``gha:input`` follows later in the document. An entry is what a ``gha:input`` without content creates: *Type*,
   *Required*, *Default Value* and the ``description`` of the workflow file.

   .. code-block:: ReST

      Input Parameters
      ****************

      .. gha:input:: package_name

         :Possible Values: Any valid Python package name.

      .. gha:autoinputs::


.. _DOC/Sphinx/GHA/Summaries:

Summaries
*********

The directives below summarize the current workflow. Like the entries, they read the workflow file, so they can't
drift from it.


.. _DOC/Sphinx/GHA/ParameterTable:

Parameter Tables
================

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``gha:parameter-table`` renders the summary tables of the current workflow's parameters - one per kind, the
      parameters in file order, each name linked to its entry:

      * **inputs** - *Parameter Name*, *Required*, *Type* and *Default*;
      * **secrets** - *Token Name*, *Required*, *Type* and *Default*;
      * **outputs** - *Result Name* and the ``description`` of the workflow file.

      A default longer than 120 characters, or of several lines, is shortened in the table and followed by ``…``; the
      entry shows it in full.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         Parameter Summary
         *****************

         .. rubric:: Inputs

         .. gha:parameter-table::
            :kinds: inputs

         .. rubric:: Secrets

         .. gha:parameter-table::
            :kinds: secrets

.. rst:directive:: .. gha:parameter-table::

   .. rst:directive:option:: kinds: <kind> ...

      The kinds of parameters to summarize, from ``inputs``, ``secrets`` and ``outputs``, separated by spaces or
      commas. The tables are rendered in the order written. Without the option, a table is rendered for every kind the
      workflow has parameters of, in the order inputs, secrets, outputs. A kind named here, of which the workflow has
      none, is a table saying so.


.. _DOC/Sphinx/GHA/Interface:

Interface
=========

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``gha:interface`` renders the contract of the current workflow with its caller, as a field list:

      * **Required Inputs**, **Secrets** - a secret the caller has to pass is marked *required* - and **Outputs**,
        each linked to its entry;
      * **Permissions** - the permissions a caller has to grant the ``GITHUB_TOKEN``. A called workflow can keep or
        reduce them, never raise them, so these are the permissions the workflow's jobs and the jobs of the workflows
        they call declare - per scope the highest access, with the job and the line asking for it, linked to GitHub
        when :confval:`gha_ref` is configured.

      What the workflow uses is listed by ``gha:dependencies``.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. topic:: Interface

            .. gha:interface::

.. rst:directive:: .. gha:interface::

   Summarizes the contract of the current workflow with its caller.


.. _DOC/Sphinx/GHA/Dependencies:

Dependencies
============

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``gha:dependencies`` renders what the current workflow uses, as a nested bullet list. From the workflow file,
      and from the files of the templates and actions it uses, as far as they are in the documented repository:

      * the **templates** the jobs call - each once, with the jobs calling it, when several do - each with its own
        dependencies. A template of the documented repository links to its page, one of another repository to
        GitHub;
      * the **actions** the steps run, each once, linked to GitHub. A composite action is listed with the actions
        its steps run, a Docker action with its image, read from its :file:`action.yml`;
      * the **images** of the containers and service containers the jobs run in.

      What a file can't tell - packages a step installs, tools it calls - is the directive's content: a bullet list
      merged into the derived one. An item whose text is the name of a derived item adds its nested list to that
      item, recursively; any other item is appended to its list. Content after the bullet list follows the list.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. topic:: Dependencies

            .. gha:dependencies::

               * pyTooling/upload-artifact

                 * :gh:`actions/upload-artifact`

               * pip

                 * :term:`wheel`

.. rst:directive:: .. gha:dependencies::

   Lists the templates, actions and container images the current workflow uses, merged with the hand-written items of
   its content. A derived item is named by:

   ========================= ==========================================================================================
   Derived item              Names
   ========================= ==========================================================================================
   template                  the reference as written, and without its ref, the file name, the file's stem - as
                             ``UnitTesting.yml``
   action                    the reference as written, and without its ref - as ``actions/checkout``
   container                 ``container``, the image as written
   service container         ``service <name>``, the name, the image as written
   image of a Docker action  ``image``, the image as written
   ========================= ==========================================================================================

   A file of the documented repository that doesn't exist - a template or an :file:`action.yml` - is a warning of type
   ``gha.workflow``, and its item has no nested list.


.. _DOC/Sphinx/GHA/YAML:

YAML Excerpts
=============

.. grid:: 2

   .. grid-item::
      :columns: 6

      ``gha:yaml`` renders the current workflow's file, or a part of it, as a YAML code block. The lines are numbered
      as in the file, and the part is shifted left by the indentation of its first line.

      The caption names the file and the lines. When :confval:`gha_repository` and :confval:`gha_ref` are
      configured, it links to these lines on GitHub:
      ``https://github.com/<repository>/blob/<ref>/.github/workflows/<file>#L<first>-L<last>``.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. gha:yaml::
            :section: inputs

         .. gha:yaml::
            :job: Package

.. rst:directive:: .. gha:yaml::

   .. rst:directive:option:: section: inputs | outputs | secrets | jobs

      The ``inputs``, ``outputs`` or ``secrets`` of ``on.workflow_call``, or the ``jobs``.

   .. rst:directive:option:: job: <name>

      One job. Excludes ``:section:``. Without either option, the whole file is shown.

   .. rst:directive:option:: caption: <text>

      A caption replacing the file name and the lines.

   .. rst:directive:option:: name: <label>

      A label to reference the code block by.


.. _DOC/Sphinx/GHA/Roles:

Roles
*****

.. rst:role:: gha:workflow
.. rst:role:: gha:input
.. rst:role:: gha:output
.. rst:role:: gha:secret

   Refer to a workflow by its name, and to a parameter as ``<Workflow>.<name>`` - after a ``gha:workflow``, the name
   alone refers to that workflow's parameter. A leading ``~`` shows only the name:

   .. code-block:: ReST

      :gha:input:`package_name`                 in the page of workflow 'Parameters'
      :gha:input:`Parameters.package_name`      from anywhere
      :gha:input:`~Parameters.package_name`     shown as 'package_name'
      :gha:workflow:`CompletePipeline`

   A target that isn't documented is a warning.


.. _DOC/Sphinx/GHA/PipelineGraph:

Pipeline Graph
**************

.. grid:: 2

   .. grid-item::
      :columns: 6

      The ``gha:pipeline-graph`` directive draws the pipeline of a GitHub Actions workflow - its jobs and their
      ``needs`` - from the workflow file itself:

      * a job is a node labelled with its name and the file of the reusable workflow it calls;
      * a job running steps is a grey box with square corners;
      * a job with an ``if`` condition is dashed, and in HTML its tooltip is the condition;
      * a job with a ``strategy.matrix`` is a cluster of its instances, labelled with the matrix' dimensions; an
        instance calling a reusable workflow is drawn as the job calling it. A dynamic matrix - its combinations known
        at run time only - is one node with a double border;
      * a reusable workflow of another repository is a white leaf naming that repository and ref;
      * a reusable workflow of the documented repository is expanded into a cluster of its jobs, as many levels deep
        as ``:depth:`` says - the one an instance of a matrix calls as well;
      * the ``needs`` are the edges, without those a longer path implies.

      The workflow is read with :mod:`pyTooling.CI.GitHub.WorkflowFile`, converted into a :mod:`pyTooling.CI` model
      and its :class:`~pyTooling.Graph.Graph` (:ref:`CI/Workflow/Pipeline`), and drawn by :mod:`sphinx.ext.graphviz`.
      Every workflow file drawn becomes a dependency of the page.

   .. grid-item::
      :columns: 6

      .. code-block:: ReST

         .. gha:pipeline-graph:: Workflows/Pipeline.yml
            :depth: 1
            :caption: The pipeline of Pipeline.yml.

This is how the example renders, drawn from :download:`Workflows/Pipeline.yml` and
:download:`Workflows/Test.yml`:

.. gha:pipeline-graph:: Workflows/Pipeline.yml
   :depth: 1
   :caption: The pipeline of Pipeline.yml.

.. rst:directive:: .. gha:pipeline-graph:: <path of a workflow file>

   Draws the workflow the argument names, relative to the document.

   .. rst:directive:option:: depth: <levels>

      Levels of reusable workflows of the documented repository to expand into clusters. Default: 0.

   .. rst:directive:option:: direction: LR | TB

      Whether the pipeline flows from left to right or from top to bottom. Default: ``LR``.

   .. rst:directive:option:: reduce: yes | no

      Whether an edge a longer path implies is dropped. Default: ``yes``.

   .. rst:directive:option:: link: yes | no

      Whether a job links to the page documenting its reusable workflow, in HTML. Default: ``yes``.

   .. rst:directive:option:: caption: <text>

      A caption under the graph.

   .. rst:directive:option:: name: <label>

      A label to reference the graph by.

   .. rst:directive:option:: align: left | center | right

      The graph's horizontal alignment.

   .. rst:directive:option:: alt: <text>

      The graph's alternative text. Default: ``Pipeline of <file name>``.

.. rubric:: The documented repository

A reusable workflow is called by a reference like ``pyTooling/Actions/.github/workflows/Package.yml@r8``.
:file:`conf.py` says which repository the documentation describes, where its workflow files are, and at which ref:

.. code-block:: Python

   # doc/conf.py
   gha_repository =         "pyTooling/Actions"
   gha_workflow_directory = "../.github/workflows"
   gha_ref =                "r8"

The graph reads the configuration values of the domain (:ref:`DOC/Sphinx/GHA/Config`), and its workflow files
through the domain, which reads every file once per build:

* The reusable workflows of :confval:`gha_repository` are expanded and linked, whatever the ref they are called at.
  Without it, only local references like ``./.github/workflows/Test.yml`` are.
* Without :confval:`gha_workflow_directory`, they are read from the directory of the drawn workflow file.
* A job calling a reusable workflow of the documented repository at another ref than :confval:`gha_ref` is a warning
  of type ``gha.ref``. Without it, refs aren't checked.

A job links to the page the ``gha`` domain documents its reusable workflow on. Without such a page, and in a format
other than HTML, the job has no link.


.. _DOC/Sphinx/GHA/Labels:

Labels of Existing Pages
************************

Besides its target, each directive registers the ``:ref:`` label a page would have declared by hand, so existing
references keep working when a page is converted - :confval:`gha_label_prefix` is their root:

.. code-block:: text

   JOBTMPL/Parameters                          .. gha:workflow:: Parameters
   JOBTMPL/Parameters/Input/package_name       .. gha:input:: package_name
   JOBTMPL/Parameters/Output/python_jobs       .. gha:output:: python_jobs
   JOBTMPL/PublishOnPyPI/Secret/PYPI_TOKEN     .. gha:secret:: PYPI_TOKEN

A parameter's section carries the anchor of its label, and the anchor docutils derives from its title, so a link into
the hand-written page lands on the same entry. A label still declared by hand next to the directive is a duplicate.


.. _DOC/Sphinx/GHA/Warnings:

Warnings
********

The page and the workflow file are compared while the page is read. A difference is a warning of type
``gha.drift``, so ``-W`` fails the build, and ``suppress_warnings = ["gha.drift"]`` silences it. Where the problem is
in the file, the warning names the place in the file, as ``Package.yml:8``.

* An input is required and has a default, which is never used - named in the workflow file.
* A ``gha:input``, ``gha:output`` or ``gha:secret`` names a parameter the workflow doesn't have.
* A hand-written *Type*, *Required* or *Default Value* of an input or a secret repeats a fact of the workflow file.
  It is not shown; the file's value is.
* An input has no entry in the document - neither a ``gha:input`` nor a ``gha:autoinputs`` - reported at the
  ``gha:workflow`` when the whole document was read.
* A ``gha:yaml`` names a job the workflow doesn't have, or a section the workflow has nothing in.

A workflow file that can't be found or read is a warning of type ``gha.workflow``, as is a ``gha:input`` or a summary
directive without a preceding ``gha:workflow``.


.. _DOC/Sphinx/GHA/API:

Extending the Domain
********************

A directive of another module reaches the domain with ``self.env.get_domain("gha")``, a
:class:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain`:

* :meth:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.GetCurrentWorkflow` returns the model of
  the document's current workflow, a :class:`pyTooling.CI.GitHub.WorkflowFile.Workflow`;
* :attr:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.Resolver` reads the workflows a job calls,
  every file once;
* :meth:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.ResolveWorkflow` says where a workflow is
  documented;
* :meth:`ParameterDirective.CreateEntry <pyTooling.Documentation.Sphinx.GitHubActions.ParameterDirective.CreateEntry>`
  creates a parameter's entry and registers it, as ``gha:autoinputs`` does.

A directive is added to the domain with
:meth:`Sphinx.add_directive_to_domain <sphinx.application.Sphinx.add_directive_to_domain>`.
