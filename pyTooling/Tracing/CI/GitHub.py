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
from json                  import loads as json_loads
from re                    import compile as re_compile
from time                  import sleep
from typing                import Any, Iterable, Optional as Nullable
from urllib.error          import HTTPError
from urllib.request        import Request, urlopen

from pyTooling.CI          import JSONObject
from pyTooling.CI.GitHub   import Base, Conclusion, Job, JobGroup, Matrix, MatrixJob, Pipeline, Step, Workflow
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Tracing     import AttributeValue, Span, Trace, TracingError
from pyTooling.Tracing.CI  import SPAN_KIND, SPAN_KIND_PIPELINE, SPAN_KIND_WORKFLOW, SPAN_KIND_MATRIX
from pyTooling.Tracing.CI  import SPAN_KIND_QUEUED, SPAN_KIND_JOB
from pyTooling.Tracing.CI  import SPAN_KIND_STEP, PIPELINE_NAME, PIPELINE_RUN_ID, PIPELINE_RUN_URL, PIPELINE_RESULT
from pyTooling.Tracing.CI  import TASK_NAME, TASK_RUN_ID, TASK_RUN_URL, TASK_RUN_RESULT, WORKER_NAME
from pyTooling.Tracing.CI  import RESULT_SUCCESS, RESULT_FAILURE, RESULT_TIMEOUT, RESULT_SKIP, RESULT_CANCELLATION
from pyTooling.Tracing.CI  import RESULT_ERROR


__all__ = ["GITHUB_API_URL", "MATRIX_DIMENSIONS", "RUNNER_LABELS", "RUNNER_GROUP", "CONCLUSION"]

GITHUB_API_URL = "https://api.github.com"
"""Base URL of the GitHub REST API."""

RUNNER_LABELS = "github.runner.labels"
"""Attribute: the labels a job requested its runner by, e.g. ``['ubuntu-26.04']``."""

MATRIX_DIMENSIONS = "github.matrix.dimensions"
"""Attribute: the values of the matrix' dimensions a job instance ran with, e.g. ``['ubuntu-26.04', '3.14']``."""

RUNNER_GROUP = "github.runner.group"
"""Attribute: the runner group the job's runner belongs to."""

CONCLUSION = "github.conclusion"
"""Attribute: GitHub's own conclusion of a run, job or step, next to the CI/CD result it was mapped to."""

_CONCLUSION_TO_RESULT: dict[str, str] = {
	"success":   RESULT_SUCCESS,
	"failure":   RESULT_FAILURE,
	"timed_out": RESULT_TIMEOUT,
	"skipped":   RESULT_SKIP,
	"cancelled": RESULT_CANCELLATION,
}
"""GitHub's conclusions and the CI/CD results they correspond to. Any other conclusion is an error."""

_NEXT_LINK = re_compile(r'<([^>]+)>;\s*rel="next"')
"""Pattern extracting the URL of the next page from a ``Link`` header."""

_TRANSIENT_HTTP_STATUS = (429, 500, 502, 503, 504)
"""HTTP status codes of a transient failure, after which a request is tried again."""

_MAXIMUM_RETRY_AFTER = 60.0
"""The longest pause in seconds a ``Retry-After`` header can demand before a request is tried again."""


_CONCLUSION_TO_RESULT = {
	Conclusion.Success:   RESULT_SUCCESS,
	Conclusion.Failure:   RESULT_FAILURE,
	Conclusion.TimedOut:  RESULT_TIMEOUT,
	Conclusion.Skipped:   RESULT_SKIP,
	Conclusion.Cancelled: RESULT_CANCELLATION,
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

	return _CONCLUSION_TO_RESULT.get(conclusion, RESULT_ERROR)


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


def _fullName(job: Job) -> str:
	"""
	Return a job's name as GitHub reports it, with the names of the workflows calling it.

	The model keeps the parts apart - a job named ``Caller / Build`` is a :class:`~pyTooling.CI.GitHub.Job` called
	``Build`` below a :class:`~pyTooling.CI.GitHub.Workflow` called ``Caller`` - while the attribute names the task the
	way the service does.

	:param job: The job.
	:returns:   The job's name, prefixed by the workflows calling it.
	"""
	callers = []
	element = job.Parent
	while element is not None and not isinstance(element, Pipeline):
		# a matrix is walked through rather than named: its name is the one the job already carries
		if isinstance(element, Workflow):
			callers.append(element.Name)

		element = element.Parent

	return " / ".join([*reversed(callers), str(job)])


def _contents(group: JobGroup) -> list[Base]:
	"""
	Return what a group contains, ordered by the time its elements were queued.

	:param group: The group - a workflow run, a called workflow or a matrix.
	:returns:     The jobs, matrices and called workflows one level below the group.
	"""
	items: list[Base] = list(group.Jobs)
	if isinstance(group, Workflow):
		items.extend(group.Matrices.values())
		items.extend(group.Workflows.values())

	# stable sort: elements without a begin time keep their order at the end
	items.sort(key=lambda item: (item.CreatedAt is None, item.CreatedAt if item.CreatedAt is not None else datetime.min))

	return items


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
	span[SPAN_KIND] = SPAN_KIND_STEP
	span[TASK_NAME] = step.Name
	_setAttribute(span, "github.step.number", step.Number)
	_setAttribute(span, TASK_RUN_RESULT, _result(step.Conclusion))
	_setAttribute(span, CONCLUSION, None if step.Conclusion is None else step.Conclusion.value)


def _addJob(job: Job, parent: Span) -> None:
	"""
	Add a job to its parent: a timespan for waiting on a runner, a timespan for the job, and one per step.

	A step may be reported as starting before, or completing after, the job containing it, so the job's timespan is
	widened to hold its steps - :mod:`pyTooling.Tracing` requires a timespan to lie within its parent.

	:param job:    The job.
	:param parent: The timespan of the trace, workflow or matrix containing the job.
	"""
	created, started, completed = _jobTimes(job)

	fullName = _fullName(job)
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
			queued[SPAN_KIND] = SPAN_KIND_QUEUED
			queued[TASK_NAME] = fullName
			_setAttribute(queued, RUNNER_LABELS, list(job.Labels))

		if started is None:
			return

		jobSpan = Span(displayName, started, _notBefore(completed, started), parent=parent)

	jobSpan[SPAN_KIND] = SPAN_KIND_JOB
	jobSpan[TASK_NAME] = fullName
	_setAttribute(jobSpan, TASK_RUN_ID, None if job.ID is None else str(job.ID))
	_setAttribute(jobSpan, TASK_RUN_URL, None if job.URL is None else str(job.URL))
	_setAttribute(jobSpan, TASK_RUN_RESULT, _result(job.Conclusion))
	_setAttribute(jobSpan, CONCLUSION, None if job.Conclusion is None else job.Conclusion.value)
	_setAttribute(jobSpan, WORKER_NAME, job.RunnerName)
	_setAttribute(jobSpan, RUNNER_GROUP, job.RunnerGroupName)
	_setAttribute(jobSpan, RUNNER_LABELS, list(job.Labels))
	if isinstance(job, MatrixJob) and len(job.DimensionValues) > 0:
		jobSpan[MATRIX_DIMENSIONS] = list(job.DimensionValues)

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

		span[SPAN_KIND] = SPAN_KIND_MATRIX if isinstance(item, Matrix) else SPAN_KIND_WORKFLOW
		span[TASK_NAME] = item.Name
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
	* Every timespan is classified by :data:`~pyTooling.Tracing.CI.SPAN_KIND` and carries the OpenTelemetry CI/CD
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
	trace[SPAN_KIND] =     SPAN_KIND_PIPELINE
	trace[PIPELINE_NAME] = pipeline.Name
	_setAttribute(trace, PIPELINE_RUN_ID, None if pipeline.ID is None else str(pipeline.ID))
	_setAttribute(trace, PIPELINE_RUN_URL, None if pipeline.URL is None else str(pipeline.URL))
	_setAttribute(trace, PIPELINE_RESULT, _result(pipeline.Conclusion))
	_setAttribute(trace, CONCLUSION, None if pipeline.Conclusion is None else pipeline.Conclusion.value)
	_setAttribute(trace, "github.run.attempt", pipeline.RunAttempt)
	_setAttribute(trace, "github.run.number", pipeline.RunNumber)
	_setAttribute(trace, "github.workflow.path", pipeline.Path)
	_setAttribute(trace, "github.event", None if pipeline.Event is None else pipeline.Event.value)
	_setAttribute(trace, "vcs.ref.head.name", pipeline.GitReference)
	_setAttribute(trace, "vcs.ref.head.revision", pipeline.SHA)

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
class WorkflowRunReader(metaclass=ExtendedType, slots=True):
	"""
	Reads workflow runs of a GitHub repository through the GitHub REST API and converts them into traces.

	The requests use only the standard library. A token is needed for a private repository, and raises the rate limit
	for a public one - inside a workflow, ``GITHUB_TOKEN`` with the ``actions: read`` permission suffices.

	A request failing transiently - HTTP 429, 500, 502, 503 or 504, a timeout, or an unreachable API - is tried again
	after a pause, which doubles with every attempt, or lasts as long as a ``Retry-After`` header demands. A request
	failing with any other HTTP status, like 401, 403 or 404, isn't tried again, because another attempt can't succeed.
	"""
	_repository: str            #: Repository as ``owner/name``.
	_token:      Nullable[str]  #: Token authorizing the requests, or ``None`` for anonymous requests.
	_apiURL:     str            #: Base URL of the GitHub REST API, without a trailing slash.
	_timeout:    float          #: Timeout of a single request in seconds.
	_retries:    int            #: How often a transiently failing request is tried again.
	_retryDelay: float          #: Pause in seconds before a request is tried again the first time.

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
		:raises TypeError:  If parameter 'token' is not of type :class:`str`.
		:raises TypeError:  If parameter 'apiURL' is not of type :class:`str`.
		:raises TypeError:  If parameter 'timeout' is not a number.
		:raises ValueError: If parameter 'timeout' isn't positive.
		:raises TypeError:  If parameter 'retries' is not of type :class:`int`.
		:raises ValueError: If parameter 'retries' is negative.
		:raises TypeError:  If parameter 'retryDelay' is not a number.
		:raises ValueError: If parameter 'retryDelay' is negative.
		"""
		if not isinstance(repository, str):
			ex = TypeError("Parameter 'repository' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(repository)}'.")
			raise ex
		elif len(parts := repository.split("/")) != 2 or "" in parts:
			ex = ValueError("Parameter 'repository' isn't of the form 'owner/name'.")
			ex.add_note(f"Got value '{repository}'.")
			raise ex

		if token is not None and not isinstance(token, str):
			ex = TypeError("Parameter 'token' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(token)}'.")
			raise ex

		if not isinstance(apiURL, str):
			ex = TypeError("Parameter 'apiURL' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(apiURL)}'.")
			raise ex

		if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
			ex = TypeError("Parameter 'timeout' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(timeout)}'.")
			raise ex
		elif timeout <= 0:
			ex = ValueError("Parameter 'timeout' isn't positive.")
			ex.add_note(f"Got value '{timeout}'.")
			raise ex

		if isinstance(retries, bool) or not isinstance(retries, int):
			ex = TypeError("Parameter 'retries' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retries)}'.")
			raise ex
		elif retries < 0:
			ex = ValueError("Parameter 'retries' is negative.")
			ex.add_note(f"Got value '{retries}'.")
			raise ex

		if isinstance(retryDelay, bool) or not isinstance(retryDelay, (int, float)):
			ex = TypeError("Parameter 'retryDelay' is not a number.")
			ex.add_note(f"Got type '{getFullyQualifiedName(retryDelay)}'.")
			raise ex
		elif retryDelay < 0:
			ex = ValueError("Parameter 'retryDelay' is negative.")
			ex.add_note(f"Got value '{retryDelay}'.")
			raise ex

		self._repository = repository
		self._token =      token
		self._apiURL =     apiURL.rstrip("/")
		self._timeout =    float(timeout)
		self._retries =    retries
		self._retryDelay = float(retryDelay)

	@readonly
	def Repository(self) -> str:
		"""
		Read-only property to access the repository (:attr:`_repository`).

		:returns: The repository as ``owner/name``.
		"""
		return self._repository

	@readonly
	def APIURL(self) -> str:
		"""
		Read-only property to access the base URL of the GitHub REST API (:attr:`_apiURL`).

		:returns: The base URL, without a trailing slash.
		"""
		return self._apiURL

	@readonly
	def Retries(self) -> int:
		"""
		Read-only property to access how often a transiently failing request is tried again (:attr:`_retries`).

		:returns: The number of further attempts.
		"""
		return self._retries

	@readonly
	def RetryDelay(self) -> float:
		"""
		Read-only property to access the pause before a request is tried again the first time (:attr:`_retryDelay`).

		:returns: The pause in seconds.
		"""
		return self._retryDelay

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
		:raises TracingError: If a request fails, or GitHub's answer isn't a JSON object.
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
			run, _ = self._Request(runURL)
			jobsURL = f"{runURL}/jobs?filter=latest&per_page=100"
		else:
			run, _ = self._Request(f"{runURL}/attempts/{attempt}")
			jobsURL = f"{runURL}/attempts/{attempt}/jobs?per_page=100"

		jobs: list[JSONObject] = []
		nextURL: Nullable[str] = jobsURL
		while nextURL is not None:
			page, nextURL = self._Request(nextURL)
			if not isinstance(pageJobs := page.get("jobs", None), list):
				raise TracingError(f"Field 'jobs' is missing in the answer of '{jobsURL}'.")
			jobs.extend(pageJobs)

		return ConvertWorkflowRun(run, jobs)

	def _RetryDelay(self, attempt: int, retryAfter: Nullable[str]) -> float:
		"""
		Return the pause before a request is tried again.

		:param attempt:    The attempt that failed, starting at 1.
		:param retryAfter: The value of the failed answer's ``Retry-After`` header, or ``None``.
		:returns:          The pause in seconds: the retry delay doubled for every earlier attempt, or the pause the
		                   ``Retry-After`` header demands, if that is longer - but not longer than 60 seconds.
		"""
		delay = self._retryDelay * 2 ** (attempt - 1)
		try:
			return max(delay, min(float(retryAfter), _MAXIMUM_RETRY_AFTER))
		except (TypeError, ValueError):
			return delay

	def _Request(self, url: str) -> tuple[JSONObject, Nullable[str]]:
		"""
		Request a JSON object from the GitHub REST API.

		A transient failure - see :class:`WorkflowRunReader` - is tried again up to :attr:`Retries` times.

		:param url:           The URL to request.
		:returns:             The JSON object, and the URL of the next page or ``None`` on the last page.
		:raises TracingError: If the request fails with an HTTP error, or GitHub can't be reached.
		:raises TracingError: If the answer isn't a JSON object.
		:raises TracingError: If the next page's URL doesn't belong to the GitHub REST API.
		"""
		headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
		if self._token is not None:
			headers["Authorization"] = f"Bearer {self._token}"

		for attempt in range(1, self._retries + 2):
			try:
				with urlopen(Request(url, headers=headers), timeout=self._timeout) as response:
					body = response.read()
					link = response.headers.get("Link", None)
				break
			except HTTPError as ex:
				if ex.code in _TRANSIENT_HTTP_STATUS and attempt <= self._retries:
					sleep(self._RetryDelay(attempt, None if ex.headers is None else ex.headers.get("Retry-After", None)))
					continue

				error = TracingError(f"GitHub API request failed with HTTP {ex.code}: {url}")
				try:
					error.add_note(f"GitHub: {json_loads(ex.read())['message']}")
				except Exception:
					pass
				if ex.code in (401, 403, 404):
					error.add_note("Check the repository's name, and that the token may read the repository's actions.")
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")
				raise error from ex
			except OSError as ex:
				if attempt <= self._retries:
					sleep(self._RetryDelay(attempt, None))
					continue

				error = TracingError(f"GitHub API couldn't be reached: {url}")
				error.add_note(f"Reason: {getattr(ex, 'reason', ex)}")
				if attempt > 1:
					error.add_note(f"Tried {attempt} times.")
				raise error from ex

		try:
			document = json_loads(body)
		except ValueError as ex:
			raise TracingError(f"GitHub API answered with invalid JSON: {url}") from ex

		if not isinstance(document, dict):
			raise TracingError(f"GitHub API didn't answer with a JSON object: {url}")

		nextURL = None if link is None or (match := _NEXT_LINK.search(link)) is None else match.group(1)
		if nextURL is not None and not nextURL.startswith(f"{self._apiURL}/"):
			ex = TracingError(f"GitHub API's next page is outside the API: {nextURL}")
			ex.add_note("The request's token is only sent to the API itself.")
			raise ex

		return document, nextURL
