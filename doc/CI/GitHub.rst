.. _CI/GitHub:

GitHub Actions
##############

:mod:`pyTooling.CI.GitHub` models a **GitHub Actions workflow run**:

.. code-block:: python

   from pyTooling.CI.GitHub import Pipeline

   pipeline = Pipeline.FromJSON(run, jobs)      # the REST API's two payloads

   print(f"{pipeline.Name} #{pipeline.RunNumber}: {pipeline.Conclusion.name} in {pipeline.Duration} s")
   for job in pipeline.IterateJobs():
     print(f"  {job.Name:<20} queued {job.QueueDuration} s, ran {job.Duration} s on {job.Labels}")


.. _CI/GitHub/Tree:

The Tree
********

.. code-block:: text

   PipelineGroup            every run started for one commit
   +-- Pipeline             a workflow run
       +-- Workflow         a called (reusable) workflow
       |   +-- Workflow     a workflow called by that workflow
       |   +-- Matrix       a matrix
       |   |   +-- MatrixJob    one instance it produced
       |   +-- Job
       +-- Matrix
       +-- Job              a job that ran on a runner
           +-- Step         a step of that job

The tree is :mod:`pyTooling.CI.Pipeline`'s (see :ref:`CI/Pipeline`): a called workflow, a matrix and their
base-class are that model's :class:`~pyTooling.CI.Pipeline.Workflow`, :class:`~pyTooling.CI.Pipeline.Matrix` and
:class:`~pyTooling.CI.Pipeline.JobGroup`, which this module imports, and the pipeline group, the run, a job, a matrix
instance and a step derive from that model's classes. :class:`~pyTooling.CI.GitHub.StatusMixin` adds what GitHub
reports about a run, a job and a step - :class:`~pyTooling.CI.GitHub.Status`, :class:`~pyTooling.CI.GitHub.Conclusion`
and the URL - and the conclusion is reported as the model's :attr:`~pyTooling.CI.Pipeline.Base.Outcome` too
(:meth:`Conclusion.ToOutcome <pyTooling.CI.GitHub.Conclusion.ToOutcome>`).

Every element knows its :attr:`~pyTooling.CI.Pipeline.Base.Parent`, and holds a reference to the workflow run it
belongs to in :attr:`~pyTooling.CI.Pipeline.Base.Pipeline` - so reaching the run from any depth costs no walk.

.. note::

   **The REST API reports no dependencies.** A run's jobs, matrices and called workflows have no
   :attr:`~pyTooling.CI.Pipeline.DependencyMixin.Needs` until they are added - from the ``needs:`` of the workflow
   file :attr:`~pyTooling.CI.GitHub.Pipeline.Path` names - with :meth:`~pyTooling.CI.Pipeline.DependencyMixin.AddNeed`.

Iterating an element yields what it contains one level down: a workflow yields its jobs, its matrices and the
workflows it calls, a matrix its instances, and a job its steps. To reach every job below a workflow at once - those
of its matrices and of the workflows it calls included - use
:meth:`~pyTooling.CI.Pipeline.JobGroup.IterateJobs`:

.. code-block:: python

   for element in pipeline:           # one level: jobs, matrices, called workflows
     print(f"{type(element).__name__}: {element}")

   for job in pipeline.IterateJobs():  # every job below the run, at any depth
     print(job.QualifiedName)

An element is placed in its group **under its own name** - a called workflow and a matrix as that key of
:attr:`~pyTooling.CI.Pipeline.Workflow.Workflows` respectively :attr:`~pyTooling.CI.Pipeline.Workflow.Matrices`, a
job by the name it reports - so ``in`` is asked for that name:

.. code-block:: python

   "UnitTesting" in pipeline          # a called workflow, a matrix or a job of the run
   "Unit Tests (ubuntu-26.04)" in matrix   # an instance carries the values telling it from its siblings
   "Checkout" in job                  # a step

Which container an element really sits in is a different question, and :attr:`~pyTooling.CI.Pipeline.Base.Parent`
answers it without a search:

.. code-block:: python

   workflow.Jobs[0].Parent is workflow   # True

* **A called workflow and a matrix are not elements GitHub reports.** It encodes both in a job's name -
  ``Caller / Job`` for a called workflow, ``Job (ubuntu-26.04, 3.14)`` for a matrix instance -
  and :meth:`~pyTooling.CI.GitHub.Pipeline.FromJSON` reads the name back into the tree.
* **A matrix may call a reusable workflow**, once per combination. Its jobs are named ``Tests (3.14) / Unit``, and
  the prefix becomes a :class:`~pyTooling.CI.Pipeline.MatrixWorkflow` ``Tests (3.14)`` below a
  :class:`~pyTooling.CI.Pipeline.Matrix` ``Tests``, beside the other combinations.
* :attr:`~pyTooling.CI.GitHub.Pipeline.Path` names the workflow's YAML file and
  :attr:`~pyTooling.CI.GitHub.Pipeline.WorkflowID` the workflow it belongs to, so a run can be traced back to the
  file that started it.

.. caution::

   A **called** workflow has none of that. Its name, taken from the prefix of a job's name, is the only thing
   GitHub reports about it - not its YAML file, not the ``@ref`` the caller pinned it at, and not the repository it
   lives in when that differs from the caller's. Neither the runs nor the jobs payload holds any of it, so filling
   it in means reading the caller's workflow file and resolving its ``uses:`` entries, which is a different source
   than this model reads. `Issue #408 <https://github.com/pyTooling/pyTooling/issues/408>`__ describes what is
   missing and how it could be supplied.

* **A reusable workflow may call another**, and a job's name carries the whole caller chain, so the tree nests as
  deeply as the chain is long - to GitHub's limit of four levels and beyond, should it ever be raised. A level is
  shared rather than repeated: ``A / B / C / Deep`` and ``A / B / Other`` put ``Other`` beside ``C`` below the same
  ``B``.
* Neither level reports times, so :class:`~pyTooling.CI.Pipeline.JobGroup` derives them: a group begins with its
  earliest job and ends with its latest, and has no end while a job below it is still running.
* **A job's times contain its steps.** GitHub reports both in whole seconds and independently, so a step is
  sometimes reported as starting before, or completing after, the job holding it. The job is the timespan that
  stretches - the step really did run when it says it did - and a group's times follow, so a consumer building a
  tree never has a child outside its parent. :attr:`~pyTooling.CI.Pipeline.Base.CreatedAt`,
  :attr:`~pyTooling.CI.Pipeline.Base.StartedAt` and :attr:`~pyTooling.CI.Pipeline.Base.CompletedAt` report the
  widened times; a job that hasn't completed still reports no completion, however far its steps got.
* **A group iterates what it holds in the order it was queued** - jobs and nested groups alike, so a called
  workflow takes the place its first job was queued at rather than a place behind every job. The sort is stable,
  so elements reporting no time keep the order GitHub listed them in.
* Because the name is taken apart, :class:`~pyTooling.CI.Pipeline.QualifiedNameMixin` puts it back together - a job
  below ``Caller`` reports ``Caller / Build (ubuntu-26.04)`` as its
  :attr:`~pyTooling.CI.Pipeline.QualifiedNameMixin.QualifiedName` while :attr:`~pyTooling.CI.Pipeline.Base.Name`
  stays ``Build``, so a report can name a job the way the service does without walking the tree itself. A
  :class:`~pyTooling.CI.GitHub.Job`, a :class:`~pyTooling.CI.Pipeline.Workflow` and a
  :class:`~pyTooling.CI.Pipeline.Matrix` are named that way.
* The bracketed suffix is a convention of GitHub's own interface rather than a field, so a job genuinely named
  ``Build (fast)`` and produced by no matrix is indistinguishable from one that was - it becomes a matrix of one
  instance, and so does a calling job named that way. A job whose workflow sets its own ``name:`` carries no values
  at all, and its matrix stays invisible.


.. _CI/GitHub/Strings:

Strings Become Enumerations
***************************

``status``, ``conclusion`` and ``event`` arrive as text. :class:`~pyTooling.CI.GitHub.Status`,
:class:`~pyTooling.CI.GitHub.Conclusion` and :class:`~pyTooling.CI.GitHub.Event` turn them into members, so a value
GitHub doesn't document raises :exc:`~pyTooling.CI.GitHub.GitHubError` instead of quietly matching no comparison:

.. code-block:: python

   if job.Conclusion is Conclusion.TimedOut:   # not: job["conclusion"] == "timeout"
     ...

Timestamps are parsed once, and a timestamp without a time zone is read as UTC, so every time of a run can be
compared with every other.


.. _CI/GitHub/Commit:

Several Pipelines per Commit
****************************

A push starts one run per workflow file whose triggers match, so a commit has several pipelines -
:class:`~pyTooling.CI.GitHub.PipelineGroup` holds them.

A run started at a **tag** is in that group as well and is not the same thing: it carries the same ``head_sha``, so
the API can't separate it, but it was started later and for another reason - a release pipeline tags its own commit,
and the run at that tag publishes the release. GitHub reports the **tag's** name in ``head_branch`` -
:attr:`~pyTooling.CI.GitHub.Pipeline.GitReference` - with
no field saying it is a tag, so :meth:`~pyTooling.CI.GitHub.PipelineGroup.ByGitReference` is what separates them:

.. code-block:: python

   group = PipelineGroup.FromJSON(runs)          # GET .../actions/runs?head_sha=...

   for reference, pipelines in group.ByGitReference().items():
     print(f"{reference}: {len(pipelines)} pipeline(s)")

   # main: 6 pipeline(s)
   # v1.6.0: 1 pipeline(s)
