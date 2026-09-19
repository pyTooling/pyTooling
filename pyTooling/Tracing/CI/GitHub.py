# ==================================================================================================================== #
#             _____           _ _             _____               _                                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _|_   _| __ __ _  ___(_)_ __   __ _                                        #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | || '__/ _` |/ __| | '_ \ / _` |                                       #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| || | | (_| | (__| | | | | (_| |                                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_||_|  \__,_|\___|_|_| |_|\__, |                                       #
# |_|    |___/                          |___/                             |___/                                        #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Read the timing of a GitHub Actions workflow run into a software execution trace.

A workflow run becomes a :class:`~pyTooling.Tracing.Trace`, and each job a :class:`~pyTooling.Tracing.Span` with one
sub-span per step. The time a job waited for a runner is a separate timespan in front of the job. Jobs of a called
(reusable) workflow - which GitHub names ``Caller / Job`` - are grouped below a timespan named like the calling job.

.. code-block:: python

   from os import getenv
   from pyTooling.Tracing.CI.GitHub import WorkflowRunReader

   reader = WorkflowRunReader("pyTooling/Actions", token=getenv("GITHUB_TOKEN"))
   trace = reader.ReadRun(34937615362)
   print("\\n".join(trace.Format()))

.. hint::

   See :ref:`high-level help <TRACING/CI>` for explanations and usage examples.
"""
from datetime              import datetime
from typing                import Any, ClassVar, Iterable, Optional as Nullable, Self, Union

from pyTooling.CI              import JSONObject
from pyTooling.CI.GitHub       import Conclusion, GitHubError, Job, JobGroup, Matrix, MatrixJob, Pipeline, Step
from pyTooling.Common          import getFullyQualifiedName
from pyTooling.Decorators      import export, readonly
from pyTooling.GenericPath.URL import URL
from pyTooling.MetaClasses     import ExtendedType
from pyTooling.REST            import RESTClient, RESTError
from pyTooling.Tracing         import Span, Trace
from pyTooling.Tracing.CI      import Result
from pyTooling.Tracing.CI      import JobSpan as CIJobSpan, MatrixSpan as CIMatrixSpan
from pyTooling.Tracing.CI      import PipelineTrace as CIPipelineTrace, QueuedSpan as CIQueuedSpan
from pyTooling.Tracing.CI      import StepSpan as CIStepSpan, WorkflowSpan as CIWorkflowSpan


__all__ = ["GITHUB_API_URL"]

GITHUB_API_URL = URL.Parse("https://api.github.com")
"""Base URL of the GitHub REST API."""

_GITHUB_HEADERS = {
	"Accept":               "application/vnd.github+json",
	"X-GitHub-Api-Version": "2022-11-28"
}
"""Headers every request to the GitHub REST API carries."""


@export
class GitHub(metaclass=ExtendedType, slots=True):
	"""
	Attribute keys naming what only GitHub Actions reports, beside the keys of
	:class:`~pyTooling.Tracing.CI.OTLP`.

	The nesting mirrors the key itself, as it does there: :attr:`GitHub.Runner.Labels` spells
	``'github.runner.labels'``.
	"""

	Conclusion: ClassVar[str] = "github.conclusion"  #: GitHub's own conclusion, next to the result it maps to.
	Event:      ClassVar[str] = "github.event"       #: The event that started the run, e.g. ``'push'``.

	class Run(metaclass=ExtendedType, slots=True):
		"""Attribute keys naming a workflow run."""

		Attempt: ClassVar[str] = "github.run.attempt"  #: Which attempt of the run this is.
		Number:  ClassVar[str] = "github.run.number"   #: The run's number within its workflow.

	class Workflow(metaclass=ExtendedType, slots=True):
		"""Attribute keys naming the workflow a run belongs to."""

		Path: ClassVar[str] = "github.workflow.path"  #: The workflow's YAML file in the repository.

	class Matrix(metaclass=ExtendedType, slots=True):
		"""Attribute keys naming a matrix."""

		Dimensions: ClassVar[str] = "github.matrix.dimensions"  #: One instance's values, e.g. ``['ubuntu-26.04', '3.14']``.

	class Runner(metaclass=ExtendedType, slots=True):
		"""Attribute keys naming the runner a job ran on."""

		Labels: ClassVar[str] = "github.runner.labels"  #: The labels the job asked for, e.g. ``['ubuntu-26.04']``.
		Group:  ClassVar[str] = "github.runner.group"   #: The runner group the runner belongs to.

	class Step(metaclass=ExtendedType, slots=True):
		"""Attribute keys naming a step of a job."""

		Number: ClassVar[str] = "github.step.number"  #: The step's position in its job, counted from one.


_CONCLUSION_TO_RESULT = {
	Conclusion.Success:   Result.Success,
	Conclusion.Failure:   Result.Failure,
	Conclusion.TimedOut:  Result.Timeout,
	Conclusion.Skipped:   Result.Skip,
	Conclusion.Cancelled: Result.Cancellation,
}
"""GitHub's conclusions and the CI/CD results they correspond to. Any other conclusion is an error."""


@export
class GitHubTimespanMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for a timespan built from :mod:`pyTooling.CI.GitHub`'s model of a workflow run.

	It holds what every flavour needs to read that model: GitHub's conclusions, and the span a group's contents
	have. Everything else the model answers itself - the order its elements are in, and the times of a job, which
	are wider than the ones GitHub reports because a step may run outside the job containing it.
	"""

	@staticmethod
	def _Result(conclusion: Nullable[Conclusion]) -> Nullable[Result]:
		"""
		Map a GitHub conclusion to a CI/CD result.

		:param conclusion: Optional, the conclusion, or ``None`` while it hasn't concluded. Default: ``None``.
		:returns:          The CI/CD result, or ``None`` if there is no conclusion yet.
		"""
		if conclusion is None:
			return None

		return _CONCLUSION_TO_RESULT.get(conclusion, Result.Error)

	@staticmethod
	def _NotBefore(end: Nullable[datetime], begin: datetime) -> Nullable[datetime]:
		"""
		Clamp an end time so it doesn't precede a begin time.

		:param end:   Optional, the end time. Default: ``None``.
		:param begin: The begin time.
		:returns:     The end time, but not before the begin time.
		"""
		return None if end is None else max(end, begin)

	@classmethod
	def _GroupTimes(cls, group: JobGroup) -> tuple[Nullable[datetime], Nullable[datetime]]:
		"""
		Return when the contents of a group begin and end.

		The model spans them - :attr:`~pyTooling.CI.GitHub.JobGroup.ContentsCreatedAt` and its two siblings - and
		this is where the span becomes a timespan: it begins when the first element was queued, or started if it was
		never queued, and it doesn't end before it begins.

		:param group: The group - a workflow run, a called workflow or a matrix.
		:returns:     When the contents begin and end, each ``None`` if the group holds nothing respectively hasn't
		              completed.
		"""
		begin = group.ContentsCreatedAt if group.ContentsCreatedAt is not None else group.ContentsStartedAt
		if begin is None:
			return None, None

		return begin, cls._NotBefore(group.ContentsCompletedAt, begin)

	@classmethod
	def _AddContents(cls, group: JobGroup, parent: Span) -> None:
		"""
		Add the jobs, matrices and called workflows of a group to a timespan, ordered by the time they were queued.

		:param group:  The group - a workflow run, a called workflow or a matrix.
		:param parent: The timespan the group's contents are added to.
		"""
		for item in group:
			if isinstance(item, Job):
				JobSpan.FromJob(item, parent)
			elif isinstance(item, Matrix):
				MatrixSpan.FromGroup(item, parent)
			else:
				WorkflowSpan.FromGroup(item, parent)


@export
class StepSpan(CIStepSpan, GitHubTimespanMixin):
	"""The timespan of a step of a GitHub Actions job."""

	@classmethod
	def FromStep(cls, step: Step, parent: Span) -> Nullable[Self]:
		"""
		Build the timespan of a step, below the timespan of its job.

		A step that never started has no timespan - there is nothing to place on a timeline.

		:param step:   The step.
		:param parent: The timespan of the job containing the step.
		:returns:      The step's timespan, or ``None`` if the step never started.
		"""
		if step.StartedAt is None:
			return None

		return cls(
			step.Name,
			step.StartedAt,
			cls._NotBefore(step.CompletedAt, step.StartedAt),
			parent=parent,
			result=cls._Result(step.Conclusion),
			attributes={
				GitHub.Step.Number: step.Number,
				GitHub.Conclusion:  None if step.Conclusion is None else step.Conclusion.value
			}
		)


@export
class QueuedSpan(CIQueuedSpan, GitHubTimespanMixin):
	"""The timespan a GitHub Actions job waited for a runner, in front of the job's own timespan."""

	@classmethod
	def FromJob(cls, job: Job, created: datetime, started: Nullable[datetime], parent: Span) -> Self:
		"""
		Build the timespan a job waited for a runner.

		:param job:     The job that waited.
		:param created: When the job was created, which is when it started waiting.
		:param started: Optional, when the job started, or ``None`` while it is still waiting.
		:param parent:  The timespan of the trace, workflow or matrix containing the job.
		:returns:       The waiting timespan.
		"""
		return cls(
			f"{job!s} (queued)",
			created,
			cls._NotBefore(started, created),
			parent=parent,
			taskName=job.QualifiedName,
			attributes={GitHub.Runner.Labels: list(job.Labels)}
		)


@export
class JobSpan(CIJobSpan, GitHubTimespanMixin):
	"""The timespan of a GitHub Actions job, from the moment it started on a runner until it completed."""

	@classmethod
	def FromJob(cls, job: Job, parent: Span) -> Nullable[Self]:
		"""
		Build the timespans of a job: the time it waited for a runner, the job itself, and one per step.

		A step may be reported as starting before, or completing after, the job containing it, so the job's timespan is
		widened to hold its steps - :mod:`pyTooling.Tracing` requires a timespan to lie within its parent.

		:param job:    The job.
		:param parent: The timespan of the trace, workflow or matrix containing the job.
		:returns:      The job's timespan, or ``None`` if the job hasn't started and therefore only waited.
		"""
		created, started, completed = job.CreatedAt, job.StartedAt, job.CompletedAt

		# a matrix instance carries its dimension values, so two of them are distinguishable
		displayName = str(job)
		if job.Conclusion is Conclusion.Skipped:
			# A skipped job neither waited for a runner nor ran on one.
			begin = started if started is not None else created
			end =   None if begin is None else cls._NotBefore(completed if completed is not None else begin, begin)
		else:
			if created is not None and (started is None or created < started):
				QueuedSpan.FromJob(job, created, started, parent)

			if started is None:
				return None

			begin = started
			end =   cls._NotBefore(completed, started)

		attributes = {
			GitHub.Conclusion:    None if job.Conclusion is None else job.Conclusion.value,
			GitHub.Runner.Group:  job.RunnerGroupName,
			GitHub.Runner.Labels: list(job.Labels)
		}
		if isinstance(job, MatrixJob):
			attributes[GitHub.Matrix.Dimensions] = list(job.DimensionValues)

		jobSpan = cls(
			displayName,
			begin,
			end,
			parent=parent,
			taskName=job.QualifiedName,
			runID=None if job.ID is None else str(job.ID),
			runURL=None if job.URL is None else str(job.URL),
			result=cls._Result(job.Conclusion),
			workerName=job.RunnerName,
			attributes=attributes
		)

		for step in job.Steps:
			StepSpan.FromStep(step, jobSpan)

		return jobSpan


@export
class GitHubGroupMixin(metaclass=ExtendedType, mixin=True):
	"""
	Mixin-class for a timespan holding other timespans - a called workflow or a matrix.

	Both are built the same way and differ only in what they are, which their class says. Its
	:meth:`~GitHubTimespanMixin._GroupTimes` and :meth:`~GitHubTimespanMixin._AddContents` come from
	:class:`GitHubTimespanMixin`.
	"""

	@classmethod
	def FromGroup(cls, group: JobGroup, parent: Span) -> Self:
		"""
		Build the timespan of a group and everything below it.

		:param group:  The called workflow or the matrix.
		:param parent: The timespan containing the group.
		:returns:      The group's timespan.
		"""
		begin, end = cls._GroupTimes(group)
		span = cls(group.Name, begin, end, parent=parent)
		cls._AddContents(group, span)

		return span


@export
class WorkflowSpan(CIWorkflowSpan, GitHubTimespanMixin, GitHubGroupMixin):
	"""The jobs of a called workflow, grouped into one timespan."""


@export
class MatrixSpan(CIMatrixSpan, GitHubTimespanMixin, GitHubGroupMixin):
	"""The instances a matrix produced, grouped into one timespan."""


@export
class WorkflowRunTrace(CIPipelineTrace, GitHubTimespanMixin):
	"""A GitHub Actions workflow run as a trace."""

	@classmethod
	def FromJSON(cls, run: JSONObject, jobs: Nullable[Iterable[JSONObject]] = None) -> Self:
		"""
		Build the trace of a workflow run from the payloads the GitHub REST API answers with.

		The payloads are read into a :class:`~pyTooling.CI.GitHub.Pipeline` first, so the tree - a called workflow, a
		matrix, the jobs and their steps - is reconstructed by the model rather than here, and :meth:`FromPipeline`
		turns it into timespans.

		:param run:          The workflow run, as returned by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}``.
		:param jobs:         Optional, the run's jobs, as listed by ``GET .../actions/runs/{run_id}/jobs``.
		:returns:            The workflow run as a trace.
		:raises TypeError:   If parameter 'run' is not of type :class:`dict`.
		:raises GitHubError: If a mandatory field is missing, or a field holds a value GitHub doesn't document.
		"""
		return cls.FromPipeline(Pipeline.FromJSON(run, jobs))

	@classmethod
	def FromPipeline(cls, pipeline: Pipeline) -> Self:
		"""
		Build the trace of a workflow run, as :mod:`pyTooling.CI.GitHub` models it.

		* The run becomes the trace, widened where a job was queued earlier or completed later than the run reports.
		* A called workflow and a matrix become a timespan holding the jobs below them.
		* A job becomes a timespan from its start to its completion, preceded by ``<job> (queued)`` from its creation to
		  its start, if it waited. A skipped job has no waiting timespan, and a job that hasn't started yet only a running
		  waiting timespan.
		* A step that started becomes a sub-span of its job.
		* Every timespan is classified by :attr:`CI.Span.Kind <pyTooling.Tracing.CI.CI>` and carries the OpenTelemetry CI/CD
		  attributes, GitHub's conclusion (:data:`CONCLUSION`), and for jobs the runner's labels and group.

		:param pipeline:   The workflow run.
		:returns:          The workflow run as a trace.
		:raises TypeError: If parameter 'pipeline' is not of type :class:`~pyTooling.CI.GitHub.Pipeline`.
		"""
		if not isinstance(pipeline, Pipeline):
			ex = TypeError("Parameter 'pipeline' is not of type 'Pipeline'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(pipeline)}'.")
			raise ex

		beginTime = pipeline.StartedAt if pipeline.StartedAt is not None else pipeline.CreatedAt
		endTime =   cls._NotBefore(pipeline.CompletedAt, beginTime) if beginTime is not None else pipeline.CompletedAt

		# a job may be queued before the run reports itself started, and may complete after the run's last update
		jobsBegin, jobsEnd = cls._GroupTimes(pipeline)
		if jobsBegin is not None:
			beginTime = jobsBegin if beginTime is None else min(beginTime, jobsBegin)

		if endTime is not None and jobsEnd is not None:
			endTime = max(endTime, jobsEnd)

		trace = cls(
			pipeline.Name,
			beginTime,
			endTime,
			runID=None if pipeline.ID is None else str(pipeline.ID),
			runURL=None if pipeline.URL is None else str(pipeline.URL),
			result=cls._Result(pipeline.Conclusion),
			reference=pipeline.GitReference,
			revision=pipeline.SHA,
			attributes={
				GitHub.Conclusion:    None if pipeline.Conclusion is None else pipeline.Conclusion.value,
				GitHub.Run.Attempt:   pipeline.RunAttempt,
				GitHub.Run.Number:    pipeline.RunNumber,
				GitHub.Workflow.Path: pipeline.Path,
				GitHub.Event:         None if pipeline.Event is None else pipeline.Event.value
			}
		)
		cls._AddContents(pipeline, trace)

		return trace


@export
class WorkflowRunReader(RESTClient):
	"""
	Reads workflow runs of a GitHub repository through the GitHub REST API and converts them into traces.

	A token is needed for a private repository, and it raises the rate limit for a public one - inside a workflow,
	``GITHUB_TOKEN`` with the ``actions: read`` permission suffices.

	The requests themselves - the retries, the pagination and the token's boundary - are
	:class:`~pyTooling.REST.RESTClient`'s.
	"""
	_repository: str  #: Repository as ``owner/name``.

	def __init__(
		self,
		repository: str,
		token:      Nullable[str] = None,
		*,
		apiURL:     Union[str, URL] = GITHUB_API_URL,
		timeout:    float = 30.0,
		retries:    int = 3,
		retryDelay: float = 2.0
	) -> None:
		"""
		Initializes a reader for the workflow runs of a repository.

		:param repository:  The repository as ``owner/name``.
		:param token:       Optional, token authorizing the requests. Default: anonymous requests.
		:param apiURL:      Optional, base URL of the GitHub REST API, e.g. of a GitHub Enterprise Server.
		                    Default: :data:`GITHUB_API_URL`.
		:param timeout:     Optional, timeout of a single request in seconds. Default: ``30.0``.
		:param retries:     Optional, how often a transiently failing request is tried again. ``0`` tries once.
		                    Default: ``3``.
		:param retryDelay:  Optional, pause in seconds before a request is tried again the first time. The pause doubles
		                    with every further attempt. Default: ``2.0``.
		:raises ValueError: If parameter 'repository' is ``None``.
		:raises TypeError:  If parameter 'repository' is not of type :class:`str`.
		:raises ValueError: If parameter 'repository' isn't of the form ``owner/name``.
		:raises TypeError:  If a parameter of :class:`~pyTooling.REST.RESTClient` has the wrong type.
		:raises ValueError: If a parameter of :class:`~pyTooling.REST.RESTClient` has an invalid value.
		"""
		super().__init__(apiURL, token, headers=_GITHUB_HEADERS, timeout=timeout, retries=retries, retryDelay=retryDelay)

		if repository is None:
			raise ValueError("Parameter 'repository' is None.")
		elif not isinstance(repository, str):
			ex = TypeError("Parameter 'repository' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(repository)}'.")
			raise ex
		elif len(parts := repository.split("/")) != 2 or "" in parts:
			ex = ValueError("Parameter 'repository' isn't of the form 'owner/name'.")
			ex.add_note(f"Got value '{repository}'.")
			raise ex

		self._repository = repository

	@readonly
	def Repository(self) -> str:
		"""
		Read-only property to access the repository (:attr:`_repository`).

		:returns: The repository as ``owner/name``.
		"""
		return self._repository

	def ReadRun(self, runID: int, attempt: Nullable[int] = None) -> Trace:
		"""
		Read a workflow run and all its jobs, and convert them into a trace.

		:param runID:         The workflow run's identifier.
		:param attempt:       Optional, the run attempt to read. Default: the latest attempt.
		:returns:             The workflow run as a trace (see :meth:`WorkflowRunTrace.FromJSON`).
		:raises ValueError:   If parameter 'runID' is ``None``.
		:raises TypeError:    If parameter 'runID' is not of type :class:`int`.
		:raises ValueError:   If parameter 'runID' isn't positive.
		:raises TypeError:    If parameter 'attempt' is not of type :class:`int`.
		:raises ValueError:   If parameter 'attempt' isn't positive.
		:raises RESTError:    If a request fails, or GitHub's answer isn't a JSON object.
		:raises GitHubError:  If GitHub's answer lacks a mandatory field.
		"""
		if runID is None:
			raise ValueError("Parameter 'runID' is None.")
		elif isinstance(runID, bool) or not isinstance(runID, int):
			ex = TypeError("Parameter 'runID' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(runID)}'.")
			raise ex
		elif runID <= 0:
			ex = ValueError("Parameter 'runID' isn't positive.")
			ex.add_note(f"Got value '{runID}'.")
			raise ex

		if attempt is not None:
			if isinstance(attempt, bool) or not isinstance(attempt, int):
				ex = TypeError("Parameter 'attempt' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(attempt)}'.")
				raise ex
			elif attempt <= 0:
				ex = ValueError("Parameter 'attempt' isn't positive.")
				ex.add_note(f"Got value '{attempt}'.")
				raise ex

		runPath = f"repos/{self._repository}/actions/runs/{runID}"
		if attempt is None:
			run, _ =  self.GetJSONObject(runPath)
			jobsPath = f"{runPath}/jobs?filter=latest&per_page=100"
		else:
			run, _ =  self.GetJSONObject(f"{runPath}/attempts/{attempt}")
			jobsPath = f"{runPath}/attempts/{attempt}/jobs?per_page=100"

		jobs:     list[JSONObject] = []
		nextPath: Nullable[str] =    jobsPath
		while nextPath is not None:
			page, nextPath = self.GetJSONObject(nextPath)
			if not isinstance(pageJobs := page.get("jobs", None), list):
				raise GitHubError(f"Field 'jobs' is missing in the answer of '{jobsPath}'.")
			jobs.extend(pageJobs)

		return WorkflowRunTrace.FromJSON(run, jobs)

	def _AddErrorNotes(self, error: RESTError, status: int) -> None:
		"""
		Add a note saying what a failing status means for the GitHub REST API.

		:param error:  The error the note is added to.
		:param status: The HTTP status the request failed with.
		"""
		if status in (401, 403, 404):
			error.add_note("Check the repository's name, and that the token may read the repository's actions.")
