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
from typing                import Any, Iterable, Optional as Nullable
from urllib.error          import HTTPError
from urllib.request        import Request, urlopen

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Tracing     import AttributeValue, Span, Trace, TracingError
from pyTooling.Tracing.CI  import SPAN_KIND, SPAN_KIND_PIPELINE, SPAN_KIND_WORKFLOW, SPAN_KIND_QUEUED, SPAN_KIND_JOB
from pyTooling.Tracing.CI  import SPAN_KIND_STEP, PIPELINE_NAME, PIPELINE_RUN_ID, PIPELINE_RUN_URL, PIPELINE_RESULT
from pyTooling.Tracing.CI  import TASK_NAME, TASK_RUN_ID, TASK_RUN_URL, TASK_RUN_RESULT, WORKER_NAME
from pyTooling.Tracing.CI  import RESULT_SUCCESS, RESULT_FAILURE, RESULT_TIMEOUT, RESULT_SKIP, RESULT_CANCELLATION
from pyTooling.Tracing.CI  import RESULT_ERROR, parseTimestamp


__all__ = ["GITHUB_API_URL", "RUNNER_LABELS", "RUNNER_GROUP", "CONCLUSION", "JSONObject"]

GITHUB_API_URL = "https://api.github.com"
"""Base URL of the GitHub REST API."""

RUNNER_LABELS = "github.runner.labels"
"""Attribute: the labels a job requested its runner by, e.g. ``['ubuntu-26.04']``."""

RUNNER_GROUP = "github.runner.group"
"""Attribute: the runner group the job's runner belongs to."""

CONCLUSION = "github.conclusion"
"""Attribute: GitHub's own conclusion of a run, job or step, next to the CI/CD result it was mapped to."""

JSONObject = dict[str, Any]
"""A JSON object, as the GitHub REST API returns it."""

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


def _result(conclusion: Nullable[str]) -> Nullable[str]:
	"""
	Map a GitHub conclusion to a CI/CD result.

	:param conclusion: GitHub's conclusion, or ``None`` while the run, job or step hasn't concluded.
	:returns:          The CI/CD result, or ``None`` if there is no conclusion yet.
	"""
	if conclusion is None or conclusion == "":
		return None

	return _CONCLUSION_TO_RESULT.get(conclusion, RESULT_ERROR)


def _field(mapping: JSONObject, key: str, path: str) -> Any:
	"""
	Read a mandatory field of a JSON object.

	:param mapping:       The JSON object.
	:param key:           The field's name.
	:param path:          Position of the JSON object, for the exception's message.
	:returns:             The field's value.
	:raises TracingError: If the field is missing or ``None``.
	"""
	if (value := mapping.get(key, None)) is None:
		raise TracingError(f"Field '{path}.{key}' is missing.")

	return value


def _setAttribute(span: Span, key: str, value: Nullable[AttributeValue]) -> None:
	"""
	Attach an attribute to a timespan, unless the value is ``None`` or empty.

	:param span:  The timespan.
	:param key:   The attribute's key.
	:param value: The attribute's value.
	"""
	if value is not None and value != "" and value != []:
		span[key] = value


def _notBefore(end: Nullable[datetime], begin: datetime) -> Nullable[datetime]:
	"""
	Clamp an end time to a begin time.

	GitHub reports timestamps in whole seconds and occasionally an end a second before the begin, which a timespan
	doesn't accept.

	:param end:   The end time, or ``None`` while still running.
	:param begin: The begin time.
	:returns:     The end time, but not before the begin time.
	"""
	return None if end is None else max(end, begin)


def _endTime(mapping: JSONObject, key: str) -> Nullable[datetime]:
	"""
	Read the end time of a run, job or step, which only counts once its status is ``completed``.

	:param mapping: The run, job or step.
	:param key:     The field holding the end time.
	:returns:       The end time, or ``None`` while not completed.
	"""
	return parseTimestamp(mapping.get(key, None)) if mapping.get("status", None) == "completed" else None


def _jobTimes(job: JSONObject) -> tuple[Nullable[datetime], Nullable[datetime]]:
	"""
	Return the time range a job occupies, from being queued to being completed.

	:param job: The job.
	:returns:   The time the job was created (or started), and the time it completed or ``None`` while not completed.
	"""
	begin = parseTimestamp(job.get("created_at", None)) or parseTimestamp(job.get("started_at", None))
	return begin, _endTime(job, "completed_at")


def _groupTimes(group: JSONObject) -> tuple[Nullable[datetime], Nullable[datetime]]:
	"""
	Return the time range of a group of jobs - from the first job being queued to the last job being completed.

	:param group: The group, as built by :func:`ConvertWorkflowRun`.
	:returns:     The begin time, and the end time or ``None`` while a job of the group isn't completed.
	"""
	times = [_jobTimes(job) for job in group["jobs"]] + [_groupTimes(subGroup) for subGroup in group["groups"].values()]
	begins = [begin for begin, _ in times if begin is not None]
	if len(begins) == 0:
		return None, None

	begin = min(begins)
	if any(end is None for _, end in times):
		return begin, None

	return begin, max(max(end for _, end in times), begin)


def _addJob(job: JSONObject, parent: Span) -> None:
	"""
	Add a job to its parent: a timespan for waiting on a runner, a timespan for the job, and one per step.

	:param job:    The job.
	:param parent: The trace or the timespan of the calling job.
	"""
	fullName =   job["name"]
	name =       fullName.rsplit(" / ", 1)[-1]
	created =    parseTimestamp(job.get("created_at", None))
	started =    parseTimestamp(job.get("started_at", None))
	completed =  _endTime(job, "completed_at")
	conclusion = job.get("conclusion", None)
	labels =     list(job.get("labels", None) or [])

	if conclusion == "skipped":
		# A skipped job neither waited for a runner nor ran on one.
		begin = started or created
		jobSpan = Span(name, parent=parent) if begin is None else Span(name, begin, _notBefore(completed or begin, begin), parent=parent)
	else:
		if created is not None and (started is None or created < started):
			queued = Span(f"{name} (queued)", created, _notBefore(started, created), parent=parent)
			queued[SPAN_KIND] = SPAN_KIND_QUEUED
			queued[TASK_NAME] = fullName
			_setAttribute(queued, RUNNER_LABELS, labels)

		if started is None:
			return

		jobSpan = Span(name, started, _notBefore(completed, started), parent=parent)

	jobSpan[SPAN_KIND] = SPAN_KIND_JOB
	jobSpan[TASK_NAME] = fullName
	_setAttribute(jobSpan, TASK_RUN_ID, None if job.get("id", None) is None else str(job["id"]))
	_setAttribute(jobSpan, TASK_RUN_URL, job.get("html_url", None))
	_setAttribute(jobSpan, TASK_RUN_RESULT, _result(conclusion))
	_setAttribute(jobSpan, CONCLUSION, conclusion)
	_setAttribute(jobSpan, WORKER_NAME, job.get("runner_name", None))
	_setAttribute(jobSpan, RUNNER_GROUP, job.get("runner_group_name", None))
	_setAttribute(jobSpan, RUNNER_LABELS, labels)

	for position, step in enumerate(job.get("steps", None) or []):
		if (stepBegin := parseTimestamp(step.get("started_at", None))) is None:
			continue

		stepName = _field(step, "name", f"{fullName}.steps[{position}]")
		stepSpan = Span(stepName, stepBegin, _notBefore(_endTime(step, "completed_at"), stepBegin), parent=jobSpan)
		stepSpan[SPAN_KIND] = SPAN_KIND_STEP
		stepSpan[TASK_NAME] = stepName
		_setAttribute(stepSpan, "github.step.number", step.get("number", None))
		_setAttribute(stepSpan, TASK_RUN_RESULT, _result(step.get("conclusion", None)))
		_setAttribute(stepSpan, CONCLUSION, step.get("conclusion", None))


def _addGroup(group: JSONObject, parent: Span) -> None:
	"""
	Add the jobs and called workflows of a group to its parent, ordered by the time they were queued.

	:param group:  The group, as built by :func:`ConvertWorkflowRun`.
	:param parent: The trace or the timespan of the calling job.
	"""
	items: list[tuple[Nullable[datetime], bool, str, JSONObject]] = []
	for name, subGroup in group["groups"].items():
		items.append((_groupTimes(subGroup)[0], True, name, subGroup))
	for job in group["jobs"]:
		items.append((_jobTimes(job)[0], False, "", job))

	# stable sort: timespans without a begin time keep their order at the end
	items.sort(key=lambda item: (item[0] is None, item[0] or datetime.min))

	for begin, isGroup, name, item in items:
		if not isGroup:
			_addJob(item, parent)
			continue

		_, end = _groupTimes(item)
		groupSpan = Span(name, parent=parent) if begin is None else Span(name, begin, end, parent=parent)
		groupSpan[SPAN_KIND] = SPAN_KIND_WORKFLOW
		groupSpan[TASK_NAME] = name
		_addGroup(item, groupSpan)


@export
def ConvertWorkflowRun(run: JSONObject, jobs: Iterable[JSONObject]) -> Trace:
	"""
	Convert a GitHub Actions workflow run and its jobs, as the GitHub REST API returns them, into a trace.

	* The run becomes the trace. It begins when the run started, and ends at its last update once it is completed.
	* A job becomes a timespan from its start to its completion, preceded by a timespan named ``<job> (queued)`` from
	  its creation to its start, if it waited. A skipped job has no waiting timespan, and a job that didn't start yet
	  only a running waiting timespan.
	* A step that started becomes a sub-span of its job.
	* Jobs named ``Caller / Job`` are grouped below a timespan ``Caller``, which spans all of them.
	* Every timespan is classified by :data:`~pyTooling.Tracing.CI.SPAN_KIND` and carries the OpenTelemetry CI/CD
	  attributes, GitHub's conclusion (:data:`CONCLUSION`), and for jobs the runner's labels and group.

	:param run:           The workflow run, as returned by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}``.
	:param jobs:          The run's jobs, as listed by ``GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs``.
	:returns:             The workflow run as a trace.
	:raises TypeError:    If parameter 'run' is not of type :class:`dict`.
	:raises TypeError:    If a job is not of type :class:`dict`.
	:raises TracingError: If a mandatory field of the run, a job or a step is missing.
	:raises TracingError: If a timestamp isn't an ISO 8601 timestamp.
	"""
	if not isinstance(run, dict):
		ex = TypeError("Parameter 'run' is not of type 'dict'.")
		ex.add_note(f"Got type '{getFullyQualifiedName(run)}'.")
		raise ex

	name =      _field(run, "name", "run")
	beginTime = parseTimestamp(run.get("run_started_at", None)) or parseTimestamp(_field(run, "created_at", "run"))

	trace = Trace(name, beginTime, _notBefore(_endTime(run, "updated_at"), beginTime))
	trace[SPAN_KIND] =       SPAN_KIND_PIPELINE
	trace[PIPELINE_NAME] =   name
	trace[PIPELINE_RUN_ID] = str(_field(run, "id", "run"))
	_setAttribute(trace, PIPELINE_RUN_URL, run.get("html_url", None))
	_setAttribute(trace, PIPELINE_RESULT, _result(run.get("conclusion", None)))
	_setAttribute(trace, CONCLUSION, run.get("conclusion", None))
	_setAttribute(trace, "github.run.attempt", run.get("run_attempt", None))
	_setAttribute(trace, "github.run.number", run.get("run_number", None))
	_setAttribute(trace, "github.event", run.get("event", None))
	_setAttribute(trace, "vcs.ref.head.name", run.get("head_branch", None))
	_setAttribute(trace, "vcs.ref.head.revision", run.get("head_sha", None))

	root: JSONObject = {"groups": {}, "jobs": []}
	for position, job in enumerate(jobs):
		if not isinstance(job, dict):
			ex = TypeError(f"Job {position} is not of type 'dict'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(job)}'.")
			raise ex

		group = root
		for caller in _field(job, "name", f"jobs[{position}]").split(" / ")[:-1]:
			group = group["groups"].setdefault(caller, {"groups": {}, "jobs": []})
		group["jobs"].append(job)

	_addGroup(root, trace)

	return trace


@export
class WorkflowRunReader(metaclass=ExtendedType, slots=True):
	"""
	Reads workflow runs of a GitHub repository through the GitHub REST API and converts them into traces.

	The requests use only the standard library. A token is needed for a private repository, and raises the rate limit
	for a public one - inside a workflow, ``GITHUB_TOKEN`` with the ``actions: read`` permission suffices.
	"""
	_repository: str            #: Repository as ``owner/name``.
	_token:      Nullable[str]  #: Token authorizing the requests, or ``None`` for anonymous requests.
	_apiURL:     str            #: Base URL of the GitHub REST API, without a trailing slash.
	_timeout:    float          #: Timeout of a single request in seconds.

	def __init__(
		self,
		repository: str,
		token:      Nullable[str] = None,
		*,
		apiURL:     str = GITHUB_API_URL,
		timeout:    float = 30.0
	) -> None:
		"""
		Initializes a reader for the workflow runs of a repository.

		:param repository:  The repository as ``owner/name``.
		:param token:       Optional, token authorizing the requests. Default: anonymous requests.
		:param apiURL:      Optional, base URL of the GitHub REST API, e.g. of a GitHub Enterprise Server.
		                    Default: :data:`GITHUB_API_URL`.
		:param timeout:     Optional, timeout of a single request in seconds. Default: ``30.0``.
		:raises TypeError:  If parameter 'repository' is not of type :class:`str`.
		:raises ValueError: If parameter 'repository' isn't of the form ``owner/name``.
		:raises TypeError:  If parameter 'token' is not of type :class:`str`.
		:raises TypeError:  If parameter 'apiURL' is not of type :class:`str`.
		:raises TypeError:  If parameter 'timeout' is not a number.
		:raises ValueError: If parameter 'timeout' isn't positive.
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

		self._repository = repository
		self._token =      token
		self._apiURL =     apiURL.rstrip("/")
		self._timeout =    float(timeout)

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

	def _Request(self, url: str) -> tuple[JSONObject, Nullable[str]]:
		"""
		Request a JSON object from the GitHub REST API.

		:param url:           The URL to request.
		:returns:             The JSON object, and the URL of the next page or ``None`` on the last page.
		:raises TracingError: If the request fails with an HTTP error, or GitHub can't be reached.
		:raises TracingError: If the answer isn't a JSON object.
		:raises TracingError: If the next page's URL doesn't belong to the GitHub REST API.
		"""
		headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
		if self._token is not None:
			headers["Authorization"] = f"Bearer {self._token}"

		try:
			with urlopen(Request(url, headers=headers), timeout=self._timeout) as response:
				body = response.read()
				link = response.headers.get("Link", None)
		except HTTPError as ex:
			error = TracingError(f"GitHub API request failed with HTTP {ex.code}: {url}")
			try:
				error.add_note(f"GitHub: {json_loads(ex.read())['message']}")
			except Exception:
				pass
			if ex.code in (401, 403, 404):
				error.add_note("Check the repository's name, and that the token may read the repository's actions.")
			raise error from ex
		except OSError as ex:
			error = TracingError(f"GitHub API couldn't be reached: {url}")
			error.add_note(f"Reason: {getattr(ex, 'reason', ex)}")
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
