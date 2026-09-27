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

:attr:`Job.Needs <pyTooling.CI.Workflow.Job.Needs>` resolves the names of ``needs`` to the jobs, and
:attr:`Workflow.Edges <pyTooling.CI.Workflow.Workflow.Edges>` lists every dependency as a pair, the needed job first.

:attr:`Workflow.ReducedEdges <pyTooling.CI.Workflow.Workflow.ReducedEdges>` is their transitive reduction: a
dependency is dropped, if a longer path already implies it. A pipeline graph drawn from it shows each job once below
the last job it waits for, instead of an edge from every job it waits for:

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
