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
from typing                import Any, ClassVar, Iterable, Optional as Nullable

from pyTooling.CI          import JSONObject
from pyTooling.CI.GitHub   import Base, Conclusion, Job, JobGroup, Matrix, MatrixJob, Pipeline, Step
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.REST        import RESTClient, RESTError
from pyTooling.Tracing     import AttributeValue, Span, Trace, TracingError
from pyTooling.Tracing.CI  import CI, OTLP, Result, SpanKind


__all__ = ["GITHUB_API_URL"]

GITHUB_API_URL = "https://api.github.com"
"""Base URL of the GitHub REST API."""

_GITHUB_HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
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


def _result(conclusion: Nullable[Conclusion]) -> Nullable[str]:
	"""
	Map a GitHub conclusion to a CI/CD result.

	:param conclusion: Optional, the conclusion, or ``None`` while it hasn't concluded. Default: ``None``.
	:returns:          The CI/CD result, or ``None`` if there is no conclusion yet.
	"""
	if conclusion is None:
		return None

	return _CONCLUSION_TO_RESULT.get(conclusion, Result.Error)


def _setAttribute(span: Span, key: str, value: Nullable[AttributeValue]) -> None:
	"""
	Set an attribute on a timespan, unless the value is ``None`` or empty.

	:param span:  The timespan.
	:param key:   Name of the attribute.
	:param value: Optional, the value. Default: ``None``.
	"""
	if value is not None and value != "" and value != []:
		span[key] = value


def _notBefore(end: Nullable[datetime], begin: datetime) -> Nullable[datetime]:
	"""
	Clamp an end time so it doesn't precede a begin time.

	:param end:   Optional, the end time. Default: ``None``.
	:param begin: The begin time.
	:returns:     The end time, but not before the begin time.
	"""
	return None if end is None else max(end, begin)


def _contents(group: JobGroup) -> list[Base]:
	"""
	Return what a group contains, ordered by the time its elements were queued.

	:param group: The group - a workflow run, a called workflow or a matrix.
	:returns:     The jobs, matrices and called workflows one level below the group.
	"""
	def queuedAt(item: Base) -> tuple[bool, datetime]:
		"""
		Nested function sorting an element without a begin time behind every element that has one.

		:param item: The element.
		:returns:    The sort key.
		"""
		return (item.CreatedAt is None, item.CreatedAt if item.CreatedAt is not None else datetime.min)

	# a stable sort, so elements without a begin time keep the order the model reports them in
	return sorted(group, key=queuedAt)


def _jobTimes(job: Job) -> tuple[Nullable[datetime], Nullable[datetime], Nullable[datetime]]:
	"""
	Return when a job was created, started and completed, widened to hold its steps.

	A step may be reported as starting before, or completing after, the job containing it, and
	:mod:`pyTooling.Tracing` requires a timespan to lie within its parent - so the job is stretched rather than its
	steps clamped: a step really did run when it says it did.

	:param job: The job.
	:returns:   The times the job's timespans are built from.
	"""
	created =   job.CreatedAt
	started =   job.StartedAt
	completed = job.CompletedAt

	stepBegins = [step.StartedAt for step in job.Steps if step.StartedAt is not None]
	if len(stepBegins) > 0:
		started = min(stepBegins) if started is None else min(started, min(stepBegins))
		if created is not None:
			created = min(created, started)

		stepEnds = [step.CompletedAt for step in job.Steps if step.CompletedAt is not None]
		if completed is not None and len(stepEnds) > 0:
			completed = max(completed, max(stepEnds))

	return created, started, completed


def _groupTimes(group: JobGroup) -> tuple[Nullable[datetime], Nullable[datetime]]:
	"""
	Return when a group begins and ends, from the timespans its contents produce.

	The group's own :attr:`~pyTooling.CI.GitHub.JobGroup.CreatedAt` and
	:attr:`~pyTooling.CI.GitHub.JobGroup.CompletedAt` are derived from the times GitHub reports, which do not account
	for a step running outside its job - so the range is taken from the widened times instead, or a job's timespan
	would fall outside its group's.

	:param group: The group - a workflow run, a called workflow or a matrix.
	:returns:     When the group begins and ends, each ``None`` if it holds nothing respectively hasn't completed.
	"""
	begins:   list[datetime] = []
	ends:     list[datetime] = []
	complete = True

	for item in _contents(group):
		if isinstance(item, Job):
			created, started, end = _jobTimes(item)
			begin = created if created is not None else started
		else:
			begin, end = _groupTimes(item)

		if begin is not None:
			begins.append(begin)

		if end is None:
			complete = False
		else:
			ends.append(end)

	if len(begins) == 0:
		return None, None

	begin = min(begins)

	return begin, _notBefore(max(ends), begin) if complete and len(ends) > 0 else None


def _addStep(step: Step, parent: Span) -> None:
	"""
	Add a step to the timespan of its job.

	A step that never started has no timespan - there is nothing to place on a timeline.

	:param step:   The step.
	:param parent: The timespan of the job containing the step.
	"""
	if step.StartedAt is None:
		return

	span = Span(step.Name, step.StartedAt, _notBefore(step.CompletedAt, step.StartedAt), parent=parent)
	span[CI.Span.Kind] = SpanKind.Step
	span[OTLP.CICD.Pipeline.Task.Name] = step.Name
	_setAttribute(span, GitHub.Step.Number, step.Number)
	_setAttribute(span, OTLP.CICD.Pipeline.Task.Run.Result, _result(step.Conclusion))
	_setAttribute(span, GitHub.Conclusion, None if step.Conclusion is None else step.Conclusion.value)


def _addJob(job: Job, parent: Span) -> None:
	"""
	Add a job to its parent: a timespan for waiting on a runner, a timespan for the job, and one per step.

	A step may be reported as starting before, or completing after, the job containing it, so the job's timespan is
	widened to hold its steps - :mod:`pyTooling.Tracing` requires a timespan to lie within its parent.

	:param job:    The job.
	:param parent: The timespan of the trace, workflow or matrix containing the job.
	"""
	created, started, completed = _jobTimes(job)

	fullName = job.QualifiedName
	displayName = str(job)   # a matrix instance carries its dimension values, so two of them are distinguishable
	if job.Conclusion is Conclusion.Skipped:
		# A skipped job neither waited for a runner nor ran on one.
		begin = started if started is not None else created
		if begin is None:
			jobSpan = Span(displayName, parent=parent)
		else:
			end = _notBefore(completed if completed is not None else begin, begin)
			jobSpan = Span(displayName, begin, end, parent=parent)
	else:
		if created is not None and (started is None or created < started):
			queued = Span(f"{displayName} (queued)", created, _notBefore(started, created), parent=parent)
			queued[CI.Span.Kind] = SpanKind.Queued
			queued[OTLP.CICD.Pipeline.Task.Name] = fullName
			_setAttribute(queued, GitHub.Runner.Labels, list(job.Labels))

		if started is None:
			return

		jobSpan = Span(displayName, started, _notBefore(completed, started), parent=parent)

	jobSpan[CI.Span.Kind] = SpanKind.Job
	jobSpan[OTLP.CICD.Pipeline.Task.Name] = fullName
	_setAttribute(jobSpan, OTLP.CICD.Pipeline.Task.Run.ID, None if job.ID is None else str(job.ID))
	_setAttribute(jobSpan, OTLP.CICD.Pipeline.Task.Run.URL.Full, None if job.URL is None else str(job.URL))
	_setAttribute(jobSpan, OTLP.CICD.Pipeline.Task.Run.Result, _result(job.Conclusion))
	_setAttribute(jobSpan, GitHub.Conclusion, None if job.Conclusion is None else job.Conclusion.value)
	_setAttribute(jobSpan, OTLP.CICD.Worker.Name, job.RunnerName)
	_setAttribute(jobSpan, GitHub.Runner.Group, job.RunnerGroupName)
	_setAttribute(jobSpan, GitHub.Runner.Labels, list(job.Labels))
	if isinstance(job, MatrixJob) and len(job.DimensionValues) > 0:
		jobSpan[GitHub.Matrix.Dimensions] = list(job.DimensionValues)

	for step in job.Steps:
		_addStep(step, jobSpan)


def _addGroup(group: JobGroup, parent: Span) -> None:
	"""
	Add the jobs, matrices and called workflows of a group to its parent, ordered by the time they were queued.

	:param group:  The group - a trace's pipeline, a called workflow or a matrix.
	:param parent: The timespan the group's contents are added to.
	"""
	for item in _contents(group):
		if isinstance(item, Job):
			_addJob(item, parent)
			continue

		begin, end = _groupTimes(item)
		if begin is None:
			span = Span(item.Name, parent=parent)
		else:
			span = Span(item.Name, begin, end, parent=parent)

		span[CI.Span.Kind] = SpanKind.Matrix if isinstance(item, Matrix) else SpanKind.Workflow
		span[OTLP.CICD.Pipeline.Task.Name] = item.Name
		_addGroup(item, span)


@export
def ConvertPipeline(pipeline: Pipeline) -> Trace:
	"""
	Convert a workflow run, as :mod:`pyTooling.CI.GitHub` models it, into a trace.

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
	endTime =   _notBefore(pipeline.CompletedAt, beginTime) if beginTime is not None else pipeline.CompletedAt

	# a job may be queued before the run reports itself started, and may complete after the run's last update
	jobsBegin, jobsEnd = _groupTimes(pipeline)
	if jobsBegin is not None:
		beginTime = jobsBegin if beginTime is None else min(beginTime, jobsBegin)

	if endTime is not None and jobsEnd is not None:
		endTime = max(endTime, jobsEnd)

	trace = Trace(pipeline.Name, beginTime, endTime)
	trace[CI.Span.Kind] = SpanKind.Pipeline
	trace[OTLP.CICD.Pipeline.Name] = pipeline.Name
	_setAttribute(trace, OTLP.CICD.Pipeline.Run.ID, None if pipeline.ID is None else str(pipeline.ID))
	_setAttribute(trace, OTLP.CICD.Pipeline.Run.URL.Full, None if pipeline.URL is None else str(pipeline.URL))
	_setAttribute(trace, OTLP.CICD.Pipeline.Result, _result(pipeline.Conclusion))
	_setAttribute(trace, GitHub.Conclusion, None if pipeline.Conclusion is None else pipeline.Conclusion.value)
	_setAttribute(trace, GitHub.Run.Attempt, pipeline.RunAttempt)
	_setAttribute(trace, GitHub.Run.Number, pipeline.RunNumber)
	_setAttribute(trace, GitHub.Workflow.Path, pipeline.Path)
	_setAttribute(trace, GitHub.Event, None if pipeline.Event is None else pipeline.Event.value)
	_setAttribute(trace, OTLP.VCS.Ref.Head.Name, pipeline.GitReference)
	_setAttribute(trace, OTLP.VCS.Ref.Head.Revision, pipeline.SHA)

	_addGroup(pipeline, trace)

	return trace


@export
def ConvertWorkflowRun(run: JSONObject, jobs: Nullable[Iterable[JSONObject]] = None) -> Trace:
	"""
	Convert a GitHub Actions workflow run and its jobs, as the GitHub REST API returns them, into a trace.

	The payloads are read into a :class:`~pyTooling.CI.GitHub.Pipeline` first, so the tree - a called workflow, a
	matrix, the jobs and their steps - is reconstructed by the model rather than here, and :func:`ConvertPipeline`
	turns it into timespans.

	:param run:          The workflow run, as returned by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}``.
	:param jobs:         Optional, the run's jobs, as listed by ``GET .../actions/runs/{run_id}/jobs``.
	:returns:            The workflow run as a trace.
	:raises TypeError:   If parameter 'run' is not of type :class:`dict`.
	:raises GitHubError: If a mandatory field is missing, or a field holds a value GitHub doesn't document.
	"""
	return ConvertPipeline(Pipeline.FromJSON(run, jobs))



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
		apiURL:     str = GITHUB_API_URL,
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
		:raises TypeError:  If parameter 'repository' is not of type :class:`str`.
		:raises ValueError: If parameter 'repository' isn't of the form ``owner/name``.
		:raises TypeError:  If a parameter of :class:`~pyTooling.REST.RESTClient` has the wrong type.
		:raises ValueError: If a parameter of :class:`~pyTooling.REST.RESTClient` has an invalid value.
		"""
		if not isinstance(repository, str):
			ex = TypeError("Parameter 'repository' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(repository)}'.")
			raise ex
		elif len(parts := repository.split("/")) != 2 or "" in parts:
			ex = ValueError("Parameter 'repository' isn't of the form 'owner/name'.")
			ex.add_note(f"Got value '{repository}'.")
			raise ex

		super().__init__(apiURL, token, headers=_GITHUB_HEADERS, timeout=timeout, retries=retries, retryDelay=retryDelay)

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
		:returns:             The workflow run as a trace (see :func:`ConvertWorkflowRun`).
		:raises TypeError:    If parameter 'runID' is not of type :class:`int`.
		:raises ValueError:   If parameter 'runID' isn't positive.
		:raises TypeError:    If parameter 'attempt' is not of type :class:`int`.
		:raises ValueError:   If parameter 'attempt' isn't positive.
		:raises RESTError:    If a request fails, or GitHub's answer isn't a JSON object.
		:raises TracingError: If GitHub's answer lacks a mandatory field.
		"""
		for parameter, value in (("runID", runID), ("attempt", attempt)):
			if value is None and parameter == "attempt":
				continue
			elif isinstance(value, bool) or not isinstance(value, int):
				ex = TypeError(f"Parameter '{parameter}' is not of type 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex
			elif value <= 0:
				ex = ValueError(f"Parameter '{parameter}' isn't positive.")
				ex.add_note(f"Got value '{value}'.")
				raise ex

		runURL = f"{self._apiURL}/repos/{self._repository}/actions/runs/{runID}"
		if attempt is None:
			run, _ = self.GetJSONObject(runURL)
			jobsURL = f"{runURL}/jobs?filter=latest&per_page=100"
		else:
			run, _ = self.GetJSONObject(f"{runURL}/attempts/{attempt}")
			jobsURL = f"{runURL}/attempts/{attempt}/jobs?per_page=100"

		jobs: list[JSONObject] = []
		nextURL: Nullable[str] = jobsURL
		while nextURL is not None:
			page, nextURL = self.GetJSONObject(nextURL)
			if not isinstance(pageJobs := page.get("jobs", None), list):
				raise TracingError(f"Field 'jobs' is missing in the answer of '{jobsURL}'.")
			jobs.extend(pageJobs)

		return ConvertWorkflowRun(run, jobs)

	def _AddErrorNotes(self, error: RESTError, status: int) -> None:
		"""
		Add a note saying what a failing status means for the GitHub REST API.

		:param error:  The error the note is added to.
		:param status: The HTTP status the request failed with.
		"""
		if status in (401, 403, 404):
			error.add_note("Check the repository's name, and that the token may read the repository's actions.")
