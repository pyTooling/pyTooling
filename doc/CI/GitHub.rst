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

Every element knows its :attr:`~pyTooling.CI.GitHub.Base.Parent`, and holds a reference to the workflow run it
belongs to in :attr:`~pyTooling.CI.GitHub.Base.Pipeline` - so reaching the run from any depth costs no walk.

Iterating an element yields what it contains one level down: a workflow yields its jobs, its matrices and the
workflows it calls, a matrix its instances, and a job its steps. To reach every job below a workflow at once - those
of its matrices and of the workflows it calls included - use
:meth:`~pyTooling.CI.GitHub.Workflow.IterateJobs`:

.. code-block:: python

   for element in pipeline:           # one level: jobs, matrices, called workflows
     print(f"{type(element).__name__}: {element}")

   for job in pipeline.IterateJobs():  # every job below the run, at any depth
     print(job.QualifiedName)

* **A called workflow and a matrix are not elements GitHub reports.** It encodes both in a job's name -
  ``Caller / Job`` for a called workflow, ``Job (ubuntu-26.04, 3.14)`` for a matrix instance -
  and :meth:`~pyTooling.CI.GitHub.Pipeline.FromJSON` reads the name back into the tree.
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
* Neither level reports times, so :class:`~pyTooling.CI.GitHub.JobGroup` derives them: a group begins with its
  earliest job and ends with its latest, and has no end while a job below it is still running.
* Because the name is taken apart, :class:`~pyTooling.CI.GitHub.QualifiedNameMixin` puts it back together - a job
  below ``Caller`` reports ``Caller / Build (ubuntu-26.04)`` as its
  :attr:`~pyTooling.CI.GitHub.QualifiedNameMixin.QualifiedName` while :attr:`~pyTooling.CI.GitHub.Base.Name` stays
  ``Build``, so a report can name a job the way the service does without walking the tree itself. A
  :class:`~pyTooling.CI.GitHub.Job` and a :class:`~pyTooling.CI.GitHub.Workflow` are named that way; a
  :class:`~pyTooling.CI.GitHub.Matrix` isn't, since GitHub reports no name for it.
* The bracketed suffix is a convention of GitHub's own interface rather than a field, so a job genuinely named
  ``Build (fast)`` and produced by no matrix is indistinguishable from one that was - it becomes a matrix of one
  instance. A job whose workflow sets its own ``name:`` carries no values at all, and its matrix stays invisible.


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
