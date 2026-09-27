.. _DOC/Sphinx/GHA:

GitHub Actions Domain
#####################

The Sphinx domain ``gha`` documents **GitHub Actions workflows** - above all reusable workflows, whose inputs,
outputs and secrets are the interface a caller uses. What the workflow file states - an input's type, whether it is
required, its default - is read from the file with :mod:`pyTooling.CI.Workflow`, so a page doesn't copy it and can't
drift from it. What the file can't say stays hand-written, as the content of a directive.

The domain is part of the :ref:`extension <DOC/Sphinx>`, and reads the files with ``ruamel.yaml``, so a project using
it needs the ``yaml`` extra as well: ``pyTooling[sphinx,yaml]``.

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

.. confval:: gha_workflow_directory

   The directory holding the workflow files, relative to the Sphinx source directory. A ``gha:workflow`` without
   ``:file:`` reads ``<name>.yml`` from it. Default: ``None``.

.. confval:: gha_repository

   The documented repository, as ``owner/repo``. A job calling ``owner/repo/.github/workflows/X.yml@<ref>`` is resolved
   to ``X.yml`` in :confval:`gha_workflow_directory`, whatever the ref. Default: ``None``.

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


.. _DOC/Sphinx/GHA/Labels:

Labels of Existing Pages
************************

Beside its target, each directive registers the ``:ref:`` label a page would have declared by hand, so existing
references keep working when a page is converted - :confval:`gha_label_prefix` is their root:

.. code-block:: text

   JOBTMPL/Parameters                          .. gha:workflow:: Parameters
   JOBTMPL/Parameters/Input/package_name       .. gha:input:: package_name
   JOBTMPL/Parameters/Output/python_jobs       .. gha:output:: python_jobs
   JOBTMPL/PublishOnPyPI/Secret/PYPI_TOKEN     .. gha:secret:: PYPI_TOKEN

A parameter's section carries the anchor of its label, and the anchor docutils derives from its title, so a link into
today's page lands on the same entry. A label still declared by hand next to the directive is a duplicate.


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

A workflow file that can't be found or read is a warning of type ``gha.workflow``, as is a ``gha:input`` without a
preceding ``gha:workflow``.


.. _DOC/Sphinx/GHA/API:

Extending the Domain
********************

A directive of another module reaches the domain with ``self.env.get_domain("gha")``, a
:class:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain`:

* :meth:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.GetCurrentWorkflow` returns the model of
  the document's current workflow, a :class:`pyTooling.CI.Workflow.Workflow`;
* :attr:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.Resolver` reads the workflows a job calls,
  every file once;
* :meth:`~pyTooling.Documentation.Sphinx.GitHubActions.GitHubActionsDomain.ResolveWorkflow` says where a workflow is
  documented.

A directive is added to the domain with
:meth:`Sphinx.add_directive_to_domain <sphinx.application.Sphinx.add_directive_to_domain>`.
