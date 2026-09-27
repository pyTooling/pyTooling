.. _CI/Workflow:

GitHub Actions Workflow Files
#############################

:mod:`pyTooling.CI.Workflow` models a **GitHub Actions workflow file** - the YAML file below
:file:`.github/workflows`, not a run of it (that's :ref:`CI/GitHub`):

.. code-block:: python

   from pathlib import Path
   from pyTooling.CI.Workflow import Workflow

   workflow = Workflow.FromFile(Path(".github/workflows/CompletePipeline.yml"))

   print(f"{workflow.Name}: {len(workflow.Inputs)} inputs, {len(workflow)} jobs")
   for job in workflow:
     print(f"  {job.Name:<24} {job.Uses or job.RunsOn}  needs {', '.join(job.NeedNames)}")

The file is read with ``ruamel.yaml``, so the module needs the ``yaml`` extra - see :ref:`DEP`.


.. _CI/Workflow/Tree:

The Tree
********

.. code-block:: text

   Workflow                 a workflow file
   +-- Input                an input of 'on.workflow_call'
   +-- Output               an output of 'on.workflow_call'
   +-- Secret               a secret of 'on.workflow_call'
   +-- Permission           a permission the workflow declares
   +-- Job                  a job, in file order
       +-- UsesReference    the reusable workflow the job calls
       +-- Permission       a permission the job declares
       +-- Matrix           the job's 'strategy.matrix'
       +-- Step             a step of the job
           +-- UsesReference    the action the step runs

* A workflow is named by its file's stem - ``CompletePipeline`` - because a caller names it that way in ``uses``.
  The ``name`` key is :attr:`~pyTooling.CI.Workflow.Workflow.DisplayName`.
* An input keeps the type its default is written with - ``'3.14'`` is a string, ``false`` a boolean - and a
  multi-line default keeps its line breaks.
* A job either runs steps on :attr:`~pyTooling.CI.Workflow.Job.RunsOn`, or calls the reusable workflow in
  :attr:`~pyTooling.CI.Workflow.Job.Uses`. :class:`~pyTooling.CI.Workflow.UsesReference` takes a reference apart
  into :attr:`~pyTooling.CI.Workflow.UsesReference.Repository`, :attr:`~pyTooling.CI.Workflow.UsesReference.Path`
  and :attr:`~pyTooling.CI.Workflow.UsesReference.Ref`:

  .. code-block:: text

     pyTooling/Actions/.github/workflows/Package.yml@r8   repository, path and ref
     ./.github/workflows/Package.yml                       a file of the same repository and commit

* :attr:`Matrix.IsDynamic <pyTooling.CI.Workflow.Matrix.IsDynamic>` says whether a matrix' instances are known at run
  time only, as for ``include: ${{ fromJson(inputs.jobs) }}``.
* Expressions - ``if``, ``runs-on: ${{ matrix.runs-on }}``, an output's ``value`` - are kept as written and are
  not evaluated.


.. _CI/Workflow/Lines:

Source Lines
************

Every element knows the line it starts at, so a message can say where a finding comes from:

.. code-block:: python

   job = workflow.Jobs["PublishOnPyPI"]
   print(f"{job.Location}: job '{job.Name}' has a condition")   # CompletePipeline.yml:532: ...

A file that is not a well-formed workflow - a job needing a job the workflow doesn't have, jobs needing each other
in a cycle, an input without ``type`` - raises :exc:`~pyTooling.CI.Workflow.WorkflowError`. It carries the file and
the line in :attr:`~pyTooling.CI.Workflow.WorkflowError.Path` and :attr:`~pyTooling.CI.Workflow.WorkflowError.Line`,
and names both in a note.


.. _CI/Workflow/Graph:

Dependencies Between Jobs
*************************

:attr:`Job.Needs <pyTooling.CI.Workflow.Job.Needs>` resolves the names of ``needs`` to the jobs. The pipeline they
form is built by :meth:`~pyTooling.CI.Workflow.Workflow.ToPipeline` (see :ref:`CI/Workflow/Pipeline`) and converted
into a :class:`~pyTooling.Graph.Graph` by :meth:`~pyTooling.CI.Pipeline.Workflow.ToGraph`, which by default drops a
dependency a longer path already implies:

.. code-block:: text

   Package  needs Prepare               Prepare --> Package --> Local
   Local    needs Prepare, Package
                                        (Prepare --> Local is implied)


.. _CI/Workflow/Resolver:

Called Workflows
****************

A job calling a reusable workflow names it by repository, path and ref. :class:`~pyTooling.CI.Workflow.WorkflowResolver`
reads the called file from a local directory, mapped per repository, whatever the ref:

.. code-block:: python

   from pyTooling.CI.Workflow import WorkflowResolver

   resolver = WorkflowResolver({"pyTooling/Actions": Path(".github/workflows")})
   pipeline = resolver.Load(Path(".github/workflows/CompletePipeline.yml"))

   for job in pipeline:
     if job.Uses is not None and (called := resolver.Resolve(job.Uses)) is not None:
       print(f"{job.Name} calls {called.Name} with {len(called)} jobs")

* A local reference - ``./.github/workflows/Package.yml`` - is read from the directory of the calling workflow.
* A repository without a directory answers ``None``: its files are not fetched.
* Every file is read once; resolving it again returns the same :class:`~pyTooling.CI.Workflow.Workflow`.


.. _CI/Workflow/Permissions:

Permissions
***********

A called workflow can keep or reduce the permissions of the ``GITHUB_TOKEN``, never raise them, so what its jobs
declare is what a caller has to grant. :meth:`~pyTooling.CI.Workflow.Workflow.CollectPermissions` collects the
permissions a workflow and its jobs declare, and - given a resolver - those of the workflows they call:

.. code-block:: python

   for scope, permission in pipeline.CollectPermissions(resolver).items():
     print(f"{permission}   asked for at {permission.Location}")

   # contents: write   asked for at CompletePipeline.yml:500
   # pages: write      asked for at PublishToGitHubPages.yml:67

When several elements declare a scope, the permission granting the most access is returned, so its location names
where that access is asked for.


.. _CI/Workflow/Pipeline:

Building a Pipeline
*******************

:meth:`~pyTooling.CI.Workflow.Workflow.ToPipeline` builds the pipeline a workflow defines as a
:mod:`pyTooling.CI.Pipeline` model (:ref:`CI/Pipeline`), expanding the workflows its jobs call as far as a resolver
reads them and ``depth`` allows:

.. code-block:: python

   pipeline = workflow.ToPipeline(resolver, depth=1)
   graph =    pipeline.ToGraph()                       # reduced to the transitive reduction

   for vertex in graph.IterateTopologically():
     element = vertex.Value
     print(f"{element.QualifiedName}  {element.Definition.Location}")

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Job in the workflow file
     - Element of the pipeline
   * - with ``steps``
     - :class:`~pyTooling.CI.Workflow.DefinedJob`, its steps as :class:`~pyTooling.CI.Workflow.DefinedStep`
   * - with ``uses``
     - :class:`~pyTooling.CI.Workflow.DefinedWorkflow`, the ``uses`` text as
       :attr:`~pyTooling.CI.Pipeline.Workflow.Reference`, holding the elements of the called workflow - or none, if
       the call isn't expanded
   * - with ``strategy.matrix``
     - :class:`~pyTooling.CI.Workflow.DefinedMatrix`, holding a :class:`~pyTooling.CI.Workflow.DefinedMatrixJob` - or a
       :class:`~pyTooling.CI.Workflow.DefinedMatrixWorkflow` for a job with ``uses`` - per combination
   * - ``needs``
     - :attr:`~pyTooling.CI.Pipeline.DependencyMixin.Needs` between the elements
   * - ``if``
     - :attr:`~pyTooling.CI.Pipeline.ConditionMixin.Condition`

* An element is named by its job's key, as the file names it in ``needs``. A step is named as GitHub displays it:
  by its ``name``, or ``Run`` followed by its action or the first line of its script.
* Every element links to what it was built from: :attr:`~pyTooling.CI.Workflow.DefinitionMixin.Definition` is the
  :class:`~pyTooling.CI.Workflow.Job` - with its line, its ``uses`` reference and its permissions - or the
  :class:`~pyTooling.CI.Workflow.Step`, and for the pipeline the :class:`~pyTooling.CI.Workflow.Workflow`. A called
  workflow's :attr:`~pyTooling.CI.Workflow.CallMixin.CalledWorkflow` is the file it was expanded from.
* A matrix yields its combinations as GitHub computes them from its dimensions, ``exclude`` and ``include`` -
  :attr:`Matrix.Combinations <pyTooling.CI.Workflow.Matrix.Combinations>` -, and an instance is named by its values:
  ``Test (ubuntu, 3.14)``. A **dynamic** matrix - ``include: ${{ fromJson(...) }}`` - is a
  :class:`~pyTooling.CI.Workflow.DefinedMatrix` without instances, since its combinations are known at run time only.
* A workflow calling itself, directly or through others, raises :exc:`~pyTooling.CI.Workflow.WorkflowError`.
