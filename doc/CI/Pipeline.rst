.. _CI/Pipeline:

Pipeline
########

:mod:`pyTooling.CI.Pipeline` models a **CI pipeline independently of the service running it** - the tree of
workflows, matrices, jobs and steps, and the **dependencies** between them:

.. code-block:: python

   from pyTooling.CI.Pipeline import Pipeline, Job, Matrix, MatrixJob, Workflow

   pipeline = Pipeline("Pipeline")
   prepare =  Job("Prepare", parent=pipeline)
   test =     Matrix("Test", parent=pipeline)
   package =  Workflow("Package", reference="./.github/workflows/Package.yml", parent=pipeline)
   for version in ("3.13", "3.14"):
     MatrixJob("Test", [version], parent=test)

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
:attr:`~pyTooling.CI.Pipeline.JobGroup.Elements`, a job's :attr:`~pyTooling.CI.Pipeline.Job.Steps` or a pipeline
group's :attr:`~pyTooling.CI.Pipeline.PipelineGroup.Pipelines`. A group keeps one sequence of elements of every kind,
in the order they were added - for a definition, the order of its file. :attr:`~pyTooling.CI.Pipeline.JobGroup.Jobs`,
:attr:`~pyTooling.CI.Pipeline.Workflow.Workflows` and :attr:`~pyTooling.CI.Pipeline.Workflow.Matrices` select one
kind from it. Every element knows its :attr:`~pyTooling.CI.Pipeline.Base.Parent` and the
:attr:`~pyTooling.CI.Pipeline.Base.Pipeline` it belongs to. A wrong parent - a step below a workflow - is a
:exc:`TypeError`.

Iterating a group yields what it holds one level down, ordered by creation time; elements without a time keep the
order they were added in. :meth:`~pyTooling.CI.Pipeline.JobGroup.IterateJobs` reaches every job below a group.

:attr:`~pyTooling.CI.Pipeline.QualifiedNameMixin.QualifiedName` names an element by the workflows containing it -
``Package / Build``, or ``Test (3.14)`` for a matrix instance, whose name carries its matrix' name already.


.. _CI/Pipeline/Facts:

Definition and Run
******************

The model holds what a pipeline's **definition** says and what a **run** reports, as far as every service has it:

* :attr:`~pyTooling.CI.Pipeline.ConditionMixin.Condition` - the condition under which a workflow, a matrix, a job or
  a step runs, as written (GitHub ``if:``, GitLab ``rules:if``). It is not evaluated.
* :attr:`~pyTooling.CI.Pipeline.Workflow.Reference` - what a called workflow calls, as written.
* :attr:`~pyTooling.CI.Pipeline.Base.CreatedAt`, :attr:`~pyTooling.CI.Pipeline.Base.StartedAt`,
  :attr:`~pyTooling.CI.Pipeline.Base.CompletedAt` and :attr:`~pyTooling.CI.Pipeline.Base.Outcome` - the times and the
  :class:`~pyTooling.CI.Pipeline.Outcome` of a run.

A group the service reports as an element of its own - a pipeline, a GitLab child pipeline - keeps the times it was
given. A group it doesn't report - a GitHub called workflow, a matrix - spans what it holds: it begins with its
earliest element and ends with its latest, and has no end while an element below it is still running. The span is
available for every group as :attr:`~pyTooling.CI.Pipeline.JobGroup.ContentsCreatedAt`,
:attr:`~pyTooling.CI.Pipeline.JobGroup.ContentsStartedAt`, :attr:`~pyTooling.CI.Pipeline.JobGroup.ContentsCompletedAt`
and :attr:`~pyTooling.CI.Pipeline.JobGroup.ContentsOutcome`; :meth:`Outcome.Combine
<pyTooling.CI.Pipeline.Outcome.Combine>` lets the worst outcome win.


.. _CI/Pipeline/Dependencies:

Dependencies
************

The elements one level below a workflow - jobs, matrices and called workflows - can **need** each other, and so can
the pipelines of a group. :meth:`~pyTooling.CI.Pipeline.DependencyMixin.AddNeed` links two of them and records the
reverse link, so :attr:`~pyTooling.CI.Pipeline.DependencyMixin.Needs` and
:attr:`~pyTooling.CI.Pipeline.DependencyMixin.Dependents` are always consistent:

.. code-block:: python

   release.AddNeed(package)

   package in release.Needs          # True
   release in package.Dependents     # True

A group needing another group needs everything that group contains. The links are checked when they are added:

* **A need is a sibling** - an element of the same group. A job can't need a job inside a called workflow; it needs
  the workflow. Anything else raises :exc:`~pyTooling.CI.Pipeline.DependencyError`.
* **A dependency closing a cycle is rejected** with :exc:`~pyTooling.CI.Pipeline.DependencyCycleError`, whose note
  names the cycle - ``Cycle: A -> D -> C -> A.`` The dependencies of a group therefore always form a directed acyclic
  graph, and a reader reports a cycle at the dependency that closes it.


.. _CI/Pipeline/Graph:

Conversion to a Graph
*********************

:meth:`~pyTooling.CI.Pipeline.Workflow.ToGraph` converts a pipeline or a called workflow into a
:class:`pyTooling.Graph.Graph`:

* Every element one level below becomes a **vertex**. Its :attr:`~pyTooling.Graph.Vertex.ID` and its
  :attr:`~pyTooling.Graph.Vertex.Value` are the element, so :pycode:`graph.GetVertexByID(job)` finds a job's vertex.
  A vertex has no name; label it by :pycode:`vertex.Value.QualifiedName`.
* Every dependency becomes an **edge** from the needed element to the element needing it - the direction the
  pipeline runs in.
* A called workflow or a matrix holding elements is expanded into a :class:`~pyTooling.Graph.Subgraph`, named by its
  qualified name and built the same way. The group's vertex has a :class:`~pyTooling.Graph.Link` to each vertex of
  its subgraph. ``depth`` limits how many levels are expanded; ``0`` expands none.

Dependencies only link siblings, so every edge lies within one graph or subgraph, and the graph algorithms of
:mod:`pyTooling.Graph` apply to each of them - e.g. the transitive reduction, which drops a dependency a longer path
already implies:

.. code-block:: python

   graph = pipeline.ToGraph(depth=1)

   graph.RemoveTransitiveEdges()
   for subgraph in graph.Subgraphs:
     subgraph.RemoveTransitiveEdges()

   for vertex in graph.IterateTopologically():
     print(f"{vertex.Value.QualifiedName}: {type(vertex.Value).__name__}")

.. note::

   :mod:`pyTooling.Graph` registers a subgraph's vertices and edges on the subgraph, so the graph's own
   :attr:`~pyTooling.Graph.BaseGraph.VertexCount` counts the top level only.


.. _CI/Pipeline/Services:

Services
********

A service's model derives its classes from these and adds what only the service reports. Its matrix instance
derives from its own job class and mixes in :class:`~pyTooling.CI.Pipeline.MatrixInstanceMixin`, which carries the
dimension values - as :class:`~pyTooling.CI.Pipeline.MatrixJob` does with :class:`~pyTooling.CI.Pipeline.Job`, and
:class:`~pyTooling.CI.Pipeline.MatrixWorkflow` with :class:`~pyTooling.CI.Pipeline.Workflow`.

.. _CI/Pipeline/GitHub:

GitHub Actions
==============

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - GitHub Actions
     - :mod:`pyTooling.CI.Pipeline`
   * - Runs of one commit
     - :class:`~pyTooling.CI.Pipeline.PipelineGroup`
   * - Workflow run (entry-point workflow file)
     - :class:`~pyTooling.CI.Pipeline.Pipeline`
   * - Job with ``uses:`` (calls a reusable workflow)
     - :class:`~pyTooling.CI.Pipeline.Workflow`, ``uses:`` as :attr:`~pyTooling.CI.Pipeline.Workflow.Reference`;
       without contents, if the called file isn't read
   * - Job with ``strategy.matrix``
     - :class:`~pyTooling.CI.Pipeline.Matrix`, an instance per combination as
       :class:`~pyTooling.CI.Pipeline.MatrixJob` - or :class:`~pyTooling.CI.Pipeline.MatrixWorkflow`, if the job
       calls a reusable workflow
   * - Job with ``steps:``
     - :class:`~pyTooling.CI.Pipeline.Job`, its steps as :class:`~pyTooling.CI.Pipeline.Step`
   * - ``needs:``
     - :meth:`~pyTooling.CI.Pipeline.DependencyMixin.AddNeed`; needing a matrix job or a calling job needs the group
   * - ``if:``
     - :attr:`~pyTooling.CI.Pipeline.ConditionMixin.Condition`
   * - ``conclusion``
     - :attr:`~pyTooling.CI.Pipeline.Base.Outcome` (e.g. ``timed_out`` |rarr| ``Timeout``, ``startup_failure``
       |rarr| ``Error``)

.. _CI/Pipeline/GitLab:

GitLab CI
=========

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - GitLab CI
     - :mod:`pyTooling.CI.Pipeline`
   * - Pipelines of one commit (branch, merge request)
     - :class:`~pyTooling.CI.Pipeline.PipelineGroup`
   * - Pipeline (:file:`.gitlab-ci.yml`)
     - :class:`~pyTooling.CI.Pipeline.Pipeline`
   * - ``stages:``
     - No element. A job of stage *N* without ``needs:`` needs every job of the nearest earlier stage holding jobs;
       the reader adds these dependencies. The stage stays a fact of the GitLab job.
   * - ``needs:`` (DAG)
     - :meth:`~pyTooling.CI.Pipeline.DependencyMixin.AddNeed`, replacing the stage's implicit dependencies;
       ``needs: []`` needs nothing
   * - ``needs:parallel:matrix`` (some instances of a matrix)
     - A need of the whole :class:`~pyTooling.CI.Pipeline.Matrix`
   * - ``needs:pipeline``, ``needs:project`` (artifacts of another pipeline)
     - No dependency; they cross the pipeline's boundary
   * - Parent-child pipeline (``trigger:include``)
     - :class:`~pyTooling.CI.Pipeline.Workflow` named after the trigger job, the child pipeline's jobs below it;
       it reports its own times
   * - Multi-project pipeline (``trigger:project``)
     - :class:`~pyTooling.CI.Pipeline.Workflow` with the project as
       :attr:`~pyTooling.CI.Pipeline.Workflow.Reference` and no contents
   * - ``parallel:matrix``
     - :class:`~pyTooling.CI.Pipeline.Matrix`, an instance per combination (``test: [3.14, linux]``);
       :class:`~pyTooling.CI.Pipeline.MatrixWorkflow` instances for a trigger job
   * - ``parallel: N``
     - :class:`~pyTooling.CI.Pipeline.Matrix` with *N* instances (``test 1/3``)
   * - ``rules:if``
     - :attr:`~pyTooling.CI.Pipeline.ConditionMixin.Condition`
   * - Job ``status``
     - :attr:`~pyTooling.CI.Pipeline.Base.Outcome` (e.g. ``canceled`` |rarr| ``Cancellation``); ``manual`` and
       ``created`` haven't ended
