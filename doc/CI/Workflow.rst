.. _CI/Workflow:

GitHub Actions Workflow Files
#############################

:mod:`pyTooling.CI.GitHub.WorkflowFile` models a **GitHub Actions workflow file** - the YAML file below
:file:`.github/workflows`, not a run of it (that's :ref:`CI/GitHub`):

.. code-block:: python

   from pathlib import Path
   from pyTooling.CI.GitHub.WorkflowFile import Workflow

   workflow = Workflow.FromFile(Path(".github/workflows/CompletePipeline.yml"))

   print(f"{workflow.Name}: {len(workflow.Inputs)} inputs, {workflow.JobCount} jobs")
   for job in workflow.IterateJobs():
     print(f"  {job.Name:<24} {job.Uses or job.RunsOn}  needs {', '.join(job.NeedNames)}")

The file is read with ``ruamel.yaml``, so the module needs the ``github`` extra - see :ref:`DEP`.


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
  The ``name`` key is :attr:`~pyTooling.CI.GitHub.WorkflowFile.Workflow.DisplayName`.
* An input keeps the type its default is written with - ``'3.14'`` is a string, ``false`` a boolean - and a
  multi-line default keeps its line breaks.
* A job either runs steps on :attr:`~pyTooling.CI.GitHub.WorkflowFile.Job.RunsOn`, or calls the reusable workflow in
  :attr:`~pyTooling.CI.GitHub.WorkflowFile.Job.Uses`. :class:`~pyTooling.CI.GitHub.WorkflowFile.UsesReference` takes a
  reference apart into :attr:`~pyTooling.CI.GitHub.WorkflowFile.UsesReference.Repository`,
  :attr:`~pyTooling.CI.GitHub.WorkflowFile.UsesReference.Path` and
  :attr:`~pyTooling.CI.GitHub.WorkflowFile.UsesReference.Reference`:

  .. code-block:: text

     pyTooling/Actions/.github/workflows/Package.yml@r8   repository, path and ref
     ./.github/workflows/Package.yml                       a file of the same repository and commit

* :attr:`Matrix.IsDynamic <pyTooling.CI.GitHub.WorkflowFile.Matrix.IsDynamic>` says whether a matrix' instances are
  known at run time only, as for ``include: ${{ fromJson(inputs.jobs) }}``.
* Expressions - ``if``, ``runs-on: ${{ matrix.runs-on }}``, an output's ``value`` - are kept as written and are
  not evaluated.


.. _CI/Workflow/Lines:

Source Lines
************

Every element knows the line it starts at, so a message can say where a finding comes from:

.. code-block:: python

   job = workflow.Jobs["PublishOnPyPI"]
   print(f"{job.Location}: job '{job.Name}' has a condition")   # CompletePipeline.yml:532: ...

A file that is not a well-formed workflow - a job needing a job the workflow doesn't have, jobs needing each other in a
cycle, an input without ``type`` - raises :exc:`~pyTooling.CI.GitHub.WorkflowFile.WorkflowError`. It carries the file
and the line in :attr:`~pyTooling.CI.GitHub.WorkflowFile.WorkflowError.Path` and
:attr:`~pyTooling.CI.GitHub.WorkflowFile.WorkflowError.Line`, and names both in a note.


.. _CI/Workflow/Graph:

Dependencies Between Jobs
*************************

:attr:`Job.Needs <pyTooling.CI.GitHub.WorkflowFile.Job.Needs>` resolves the names of ``needs`` to the jobs.
:meth:`Workflow.FromFile <pyTooling.CI.GitHub.WorkflowFile.Workflow.FromFile>` checks them when it reads the file: a
job needing a job the workflow doesn't have, and jobs needing each other in a cycle, raise a
:exc:`~pyTooling.CI.GitHub.WorkflowFile.WorkflowError`.


.. _CI/Workflow/Resolver:

Called Workflows
****************

A job calling a reusable workflow names it by repository, path and ref.
:class:`~pyTooling.CI.GitHub.WorkflowFile.WorkflowResolver` reads the called file from a local directory, mapped per
repository, whatever the ref:

.. code-block:: python

   from pyTooling.CI.GitHub.WorkflowFile import WorkflowResolver

   resolver = WorkflowResolver({"pyTooling/Actions": Path(".github/workflows")})
   pipeline = resolver.Load(Path(".github/workflows/CompletePipeline.yml"))

   for job in pipeline.IterateJobs():
     if job.Uses is not None and (called := resolver.Resolve(job.Uses)) is not None:
       print(f"{job.Name} calls {called.Name} with {called.JobCount} jobs")

* A local reference - ``./.github/workflows/Package.yml`` - is read from the directory of the calling workflow.
* A repository without a directory answers ``None``: its files are not fetched.
* Every file is read once; resolving it again returns the same :class:`~pyTooling.CI.GitHub.WorkflowFile.Workflow`.


.. _CI/Workflow/Permissions:

Permissions
***********

A called workflow can keep or reduce the permissions of the ``GITHUB_TOKEN``, never raise them, so what its jobs declare
is what a caller has to grant. :meth:`~pyTooling.CI.GitHub.WorkflowFile.Workflow.CollectPermissions` collects the
permissions a workflow and its jobs declare, and - given a resolver - those of the workflows they call:

.. code-block:: python

   for scope, permission in pipeline.CollectPermissions(resolver).items():
     print(f"{permission}   asked for at {permission.Location}")

   # contents: write   asked for at CompletePipeline.yml:500
   # pages: write      asked for at PublishToGitHubPages.yml:67

When several elements declare a scope, the permission granting the most access is returned, so its location names
where that access is asked for.
