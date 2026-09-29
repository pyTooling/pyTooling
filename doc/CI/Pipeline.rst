.. _CI/Pipeline:

Pipeline
########

:mod:`pyTooling.CI` models a **CI pipeline independently of the service running it** - the tree of
workflows, matrices, jobs and steps, and the **dependencies** between them:

.. code-block:: python

   from pyTooling.CI import Pipeline, Job, Matrix, MatrixJob, Workflow

   pipeline = Pipeline("Pipeline")
   prepare =  Job("Prepare", parent=pipeline)
   test =     Matrix("Test", parent=pipeline)
   package =  Workflow("Package", reference="./.github/workflows/Package.yml", parent=pipeline)
   for version in ("3.13", "3.14"):
     MatrixJob("Test", {"python": version}, parent=test)

   test.AddNeed(prepare)
   package.AddNeed(test)

   graph = pipeline.ToGraph()        # a pyTooling.Graph.Graph of the elements and their dependencies

A service's model derives from these classes and adds what only that service has - identifiers, URLs, its own status
values, the interface of a reusable workflow.


.. _CI/Pipeline/Tree:

The Tree
********

.. code-block:: text

   PipelineGroup            the pipelines started for one commit
   +-- Pipeline             a pipeline
       +-- Workflow         a called workflow or a child pipeline
       |   +-- ...          the same elements a pipeline contains
       +-- Matrix           a matrix
       |   +-- MatrixJob        one job instance it produced
       |   +-- MatrixWorkflow   one instance of a called workflow it produced
       +-- Job              a job
           +-- Step         a step of that job

An element is created with its parent, which adds it to its elements: a group's
:attr:`~pyTooling.CI.JobGroup.Elements`, a job's :attr:`~pyTooling.CI.Job.Steps` or a pipeline
group's :attr:`~pyTooling.CI.PipelineGroup.Pipelines`. A group keeps one sequence of elements of every kind,
in the order they were added - for a definition, the order of its file. :attr:`~pyTooling.CI.JobGroup.Jobs`,
:attr:`~pyTooling.CI.Workflow.Workflows` and :attr:`~pyTooling.CI.Workflow.Matrices` select one
kind from it. Every element knows its :attr:`~pyTooling.CI.Base.Parent` and the
:attr:`~pyTooling.CI.Base.Pipeline` it belongs to. A wrong parent - a step below a workflow - is a
:exc:`TypeError`.

:meth:`~pyTooling.CI.JobGroup.IterateElements` yields what a group holds one level down, ordered by creation
time; elements without a time keep the order they were added in. :meth:`~pyTooling.CI.JobGroup.IterateJobs`
reaches every job below a group. An element is asked for and looked up by its name, :pycode:`str(element)` -
:pycode:`pipeline.ContainsElement("Build")`, :pycode:`pipeline.GetElement("Build")`,
:pycode:`matrix.GetElement("Test (3.14)")` - which is how a reader resolves the names a definition refers to. A job
offers the same for its steps, a pipeline group for its pipelines:

.. list-table::
   :header-rows: 1

   * - Class
     - Count
     - Check
     - Look up
     - Iterate
   * - :class:`~pyTooling.CI.PipelineGroup`
     - :attr:`~pyTooling.CI.PipelineGroup.PipelineCount`
     - :meth:`~pyTooling.CI.PipelineGroup.ContainsPipeline`
     -
     - :meth:`~pyTooling.CI.PipelineGroup.IteratePipelines`
   * - :class:`~pyTooling.CI.JobGroup`
     - :attr:`~pyTooling.CI.JobGroup.ElementCount`
     - :meth:`~pyTooling.CI.JobGroup.ContainsElement`
     - :meth:`~pyTooling.CI.JobGroup.GetElement`
     - :meth:`~pyTooling.CI.JobGroup.IterateElements`
   * - :class:`~pyTooling.CI.Job`
     - :attr:`~pyTooling.CI.Job.StepCount`
     - :meth:`~pyTooling.CI.Job.ContainsStep`
     -
     - :meth:`~pyTooling.CI.Job.IterateSteps`

:attr:`~pyTooling.CI.QualifiedNameMixin.QualifiedName` names an element by the workflows containing it -
``Package / Build``, or ``Test (3.14)`` for a matrix instance, whose name carries its matrix' name already.


.. _CI/Pipeline/Facts:

Definition and Run
******************

The model holds what a pipeline's **definition** says and what a **run** reports, as far as every service has it:

* :attr:`~pyTooling.CI.ConditionMixin.Condition` - the condition under which a workflow, a matrix, a job or
  a step runs, as written (GitHub ``if:``, GitLab ``rules:if``). It is not evaluated.
* :attr:`~pyTooling.CI.Workflow.Reference` - what a called workflow calls, as written.
* :attr:`~pyTooling.CI.Base.CreatedAt`, :attr:`~pyTooling.CI.Base.StartedAt`,
  :attr:`~pyTooling.CI.Base.CompletedAt` and :attr:`~pyTooling.CI.Base.Outcome` - the times and the
  :class:`~pyTooling.CI.Outcome` of a run.

A group the service reports as an element of its own - a pipeline, a GitLab child pipeline; one given a time or an
outcome - keeps the times and the outcome it was given. A group it doesn't report - a GitHub called workflow, a
matrix - spans what it holds: it begins with its earliest element and ends with its latest, and has no end while an
element below it is still running. The span is available for every group as
:attr:`~pyTooling.CI.JobGroup.ContentsCreatedAt`, :attr:`~pyTooling.CI.JobGroup.ContentsStartedAt`,
:attr:`~pyTooling.CI.JobGroup.ContentsCompletedAt` and :attr:`~pyTooling.CI.JobGroup.ContentsOutcome`;
:meth:`Outcome.Combine <pyTooling.CI.Outcome.Combine>` lets the worst outcome win.


.. _CI/Pipeline/KeyValuePairs:

Key-Value Pairs
***************

Every element - a pipeline group included - carries a dictionary of **arbitrary key-value-pairs**, like the elements
of :mod:`pyTooling.Graph`. A consumer attaches what the model has no field for, without deriving its own classes. The
pairs are given when an element is created, with ``keyValuePairs``, and accessed with the element's dictionary
operators:

.. code-block:: python

   from pyTooling.CI import Job

   job = Job("Build", keyValuePairs={"runner.os": "Linux"})
   job["runner.arch"] = "x64"

   "runner.os" in job           # True
   job["runner.os"]             # "Linux"
   len(job)                     # 2
   list(job)                    # ["runner.os", "runner.arch"]
   del job["runner.arch"]

The operators address the key-value-pairs only. What an element contains is reached by name - ``ContainsElement``,
``GetElement``, ``IterateElements`` - see :ref:`CI/Pipeline/Tree`.


.. _CI/Pipeline/Dependencies:

Dependencies
************

The elements one level below a workflow - jobs, matrices and called workflows - can **need** each other, and so can
the pipelines of a group. :meth:`~pyTooling.CI.DependencyMixin.AddNeed` links two of them and records the
reverse link, so :attr:`~pyTooling.CI.DependencyMixin.Needs` and
:attr:`~pyTooling.CI.DependencyMixin.Dependents` are always consistent:

.. code-block:: python

   release.AddNeed(package)

   package in release.Needs          # True
   release in package.Dependents     # True

Needs and dependents can also be given when an element is created, e.g. ``Job("Release", parent=pipeline,
needs=[package])``. A group needing another group needs everything that group contains.

* **A need is a sibling** - an element of the same group. A job can't need a job inside a called workflow; it needs
  the workflow. Anything else raises :exc:`~pyTooling.CI.NeedDependencyError` when the need is added.
* **Cycles are found once the pipeline is complete.**
  :meth:`JobGroup.Validate <pyTooling.CI.JobGroup.Validate>` searches a group and every group it contains,
  :meth:`PipelineGroup.Validate <pyTooling.CI.PipelineGroup.Validate>` also the pipelines of a group, each
  element and need once. A cycle raises :exc:`~pyTooling.CI.NeedDependencyCycleError`, whose note names it -
  ``Cycle: A -> D -> C -> A.``


.. _CI/Pipeline/Graph:

Conversion to a Graph
*********************

:meth:`~pyTooling.CI.Workflow.ToGraph` converts a pipeline or a called workflow into a
:class:`pyTooling.Graph.Graph`:

* Every element one level below becomes a **vertex**. Its :attr:`~pyTooling.Graph.Vertex.ID` and its
  :attr:`~pyTooling.Graph.Vertex.Value` are the element, so :pycode:`graph.GetVertexByID(job)` finds a job's vertex.
  A vertex has no name; label it by :pycode:`vertex.Value.QualifiedName`.
* Every dependency becomes an **edge** from the element needing to the element it needs: an edge reads *needs*.
  :meth:`~pyTooling.Graph.BaseGraph.IterateTopologically` therefore yields the elements in an order they can run in.
* A called workflow or a matrix holding elements is expanded into a :class:`~pyTooling.Graph.Subgraph`, named by its
  qualified name and built the same way. The group's vertex has a :class:`~pyTooling.Graph.Link` to each vertex of
  its subgraph. ``depth`` limits how many levels are expanded; ``0`` expands none.

Dependencies only link siblings, so every edge lies within one graph or subgraph, and the graph algorithms of
:mod:`pyTooling.Graph` apply to each of them. ``reduce`` - on by default - applies the transitive reduction
(:meth:`~pyTooling.Graph.BaseGraph.RemoveTransitiveEdges`) to the graph and every subgraph: a dependency a longer path
already implies - ``Release`` needing ``Prepare`` although it needs ``Test``, which needs ``Prepare`` - has no edge.
The model itself keeps every dependency; ``reduce=False`` gives each of them an edge.

.. code-block:: python

   graph = pipeline.ToGraph(depth=1)                 # reduced
   every = pipeline.ToGraph(depth=1, reduce=False)   # an edge per dependency

   for vertex in graph.IterateTopologically():
     print(f"{vertex.Value.QualifiedName}: {type(vertex.Value).__name__}")

.. note::

   :mod:`pyTooling.Graph` registers a subgraph's vertices and edges on the subgraph, so the graph's own
   :attr:`~pyTooling.Graph.BaseGraph.VertexCount` counts the top level only.


.. _CI/Pipeline/Services:

Services
********

A service's model derives its classes from these and adds what only the service reports. Its matrix instance
derives from its own job class and mixes in :class:`~pyTooling.CI.MatrixInstanceMixin`, which carries the
dimensions - as :class:`~pyTooling.CI.MatrixJob` does with :class:`~pyTooling.CI.Job`, and
:class:`~pyTooling.CI.MatrixWorkflow` with :class:`~pyTooling.CI.Workflow`.

A matrix instance is one combination of the matrix' variables: its
:attr:`~pyTooling.CI.MatrixInstanceMixin.Dimensions` maps each dimension's name to the value it ran with,
in the matrix' order - ``{"os": "ubuntu-26.04", "python": "3.14"}``. Its name prints the values only, as a service
does: ``Test (ubuntu-26.04, 3.14)``.

.. _CI/Pipeline/GitHub:

GitHub Actions
==============

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - GitHub Actions
     - :mod:`pyTooling.CI`
   * - Runs of one commit
     - :class:`~pyTooling.CI.PipelineGroup`
   * - Workflow run (entry-point workflow file)
     - :class:`~pyTooling.CI.Pipeline`
   * - Job with ``uses:`` (calls a reusable workflow)
     - :class:`~pyTooling.CI.Workflow`, ``uses:`` as :attr:`~pyTooling.CI.Workflow.Reference`;
       without contents, if the called file isn't read
   * - Job with ``strategy.matrix``
     - :class:`~pyTooling.CI.Matrix`, an instance per combination as
       :class:`~pyTooling.CI.MatrixJob` - or :class:`~pyTooling.CI.MatrixWorkflow`, if the job
       calls a reusable workflow
   * - Job with ``steps:``
     - :class:`~pyTooling.CI.Job`, its steps as :class:`~pyTooling.CI.Step`
   * - ``needs:``
     - :meth:`~pyTooling.CI.DependencyMixin.AddNeed`; needing a matrix job or a calling job needs the group
   * - ``if:``
     - :attr:`~pyTooling.CI.ConditionMixin.Condition`
   * - ``conclusion``
     - :attr:`~pyTooling.CI.Base.Outcome` (e.g. ``timed_out`` |rarr| ``Timeout``, ``startup_failure``
       |rarr| ``Error``)

.. _CI/Pipeline/GitLab:

GitLab CI
=========

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - GitLab CI
     - :mod:`pyTooling.CI`
   * - Pipelines of one commit (branch, merge request)
     - :class:`~pyTooling.CI.PipelineGroup`
   * - Pipeline (:file:`.gitlab-ci.yml`)
     - :class:`~pyTooling.CI.Pipeline`
   * - ``stages:``
     - No element. A job of stage *N* without ``needs:`` needs every job of the nearest earlier stage holding jobs;
       the reader adds these dependencies. The stage stays a fact of the GitLab job.
   * - ``needs:`` (DAG)
     - :meth:`~pyTooling.CI.DependencyMixin.AddNeed`, replacing the stage's implicit dependencies;
       ``needs: []`` needs nothing
   * - ``needs:parallel:matrix`` (some instances of a matrix)
     - A need of the whole :class:`~pyTooling.CI.Matrix`
   * - ``needs:pipeline``, ``needs:project`` (artifacts of another pipeline)
     - No dependency; they cross the pipeline's boundary
   * - Parent-child pipeline (``trigger:include``)
     - :class:`~pyTooling.CI.Workflow` named after the trigger job, the child pipeline's jobs below it;
       it reports its own times
   * - Multi-project pipeline (``trigger:project``)
     - :class:`~pyTooling.CI.Workflow` with the project as
       :attr:`~pyTooling.CI.Workflow.Reference` and no contents
   * - ``parallel:matrix``
     - :class:`~pyTooling.CI.Matrix`, an instance per combination (``test: [3.14, linux]``);
       :class:`~pyTooling.CI.MatrixWorkflow` instances for a trigger job
   * - ``parallel: N``
     - :class:`~pyTooling.CI.Matrix` with *N* instances (``test 1/3``)
   * - ``rules:if``
     - :attr:`~pyTooling.CI.ConditionMixin.Condition`
   * - Job ``status``
     - :attr:`~pyTooling.CI.Base.Outcome` (e.g. ``canceled`` |rarr| ``Cancellation``); ``manual`` and
       ``created`` haven't ended
