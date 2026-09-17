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
Unit tests for :mod:`pyTooling.Tracing.CI` and :mod:`pyTooling.Tracing.CI.GitHub`.
"""
from datetime                    import datetime, timedelta, timezone
from json                        import dumps as json_dumps
from typing                      import Any, Optional as Nullable
from unittest                    import mock
from urllib.error                import HTTPError, URLError

from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import SPAN_KIND, parseISO8601Timestamp
from pyTooling.Tracing.CI.GitHub import ConvertWorkflowRun, WorkflowRunReader
from pyTooling.Testing           import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def _time(seconds: int) -> str:
	"""
	Return a GitHub timestamp the given number of seconds after the run was created.

	:param seconds: Seconds after 2026-09-15T06:35:00Z.
	:returns:       The timestamp as GitHub formats it.
	"""
	return (datetime(2026, 9, 15, 6, 35, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(**fields: Any) -> dict[str, Any]:
	"""
	Build a completed workflow run.

	:param fields: Fields overriding the defaults.
	:returns:      The run, as the GitHub REST API returns it.
	"""
	run = {
		"id": 4711, "name": "Pipeline", "run_attempt": 1, "run_number": 42, "event": "push", "status": "completed",
		"conclusion": "success", "created_at": _time(0), "run_started_at": _time(0), "updated_at": _time(600),
		"head_branch": "dev", "head_sha": "0123abcd", "html_url": "https://github.com/owner/repo/actions/runs/4711",
	}
	run.update(fields)
	return run


def _job(name: str, created: Nullable[int], started: Nullable[int], completed: Nullable[int], **fields: Any) -> dict[str, Any]:
	"""
	Build a job.

	:param name:      The job's name.
	:param created:   Seconds after the run was created, when the job was created.
	:param started:   Seconds after the run was created, when the job started, or ``None``.
	:param completed: Seconds after the run was created, when the job completed, or ``None``.
	:param fields:    Fields overriding the defaults.
	:returns:         The job, as the GitHub REST API returns it.
	"""
	job = {
		"id": abs(hash(name)) % 1_000_000, "name": name, "status": "completed" if completed is not None else "in_progress",
		"conclusion": "success" if completed is not None else None,
		"created_at": None if created is None else _time(created), "started_at": None if started is None else _time(started),
		"completed_at": None if completed is None else _time(completed), "labels": ["ubuntu-26.04"],
		"runner_name": "GitHub Actions 1000184490", "runner_group_name": "GitHub Actions",
		"html_url": f"https://github.com/owner/repo/actions/runs/4711/job/{name}", "steps": [],
	}
	job.update(fields)
	return job


def _children(span: Span) -> dict[str, Span]:
	"""
	Index a timespan's sub-spans by name.

	:param span: The timespan.
	:returns:    Dictionary of a sub-span's name to the sub-span.
	"""
	return {subSpan.Name: subSpan for subSpan in span.IterateSubSpans()}


class Timestamps(Testcase):
	def test_UTC(self) -> None:
		self.assertEqual(
			datetime(2026, 9, 15, 6, 35, 24, tzinfo=timezone.utc),
			parseISO8601Timestamp("2026-09-15T06:35:24Z")
		)

	def test_Offset(self) -> None:
		timestamp = parseISO8601Timestamp("2026-09-15T08:35:24+02:00")

		self.assertEqual(datetime(2026, 9, 15, 6, 35, 24, tzinfo=timezone.utc), timestamp)
		self.assertEqual(timedelta(hours=2), timestamp.utcoffset())

	def test_Naive(self) -> None:
		self.assertEqual(timezone.utc, parseISO8601Timestamp("2026-09-15T06:35:24").tzinfo)

	def test_None(self) -> None:
		self.assertIsNone(parseISO8601Timestamp(None))
		self.assertIsNone(parseISO8601Timestamp(""))

	def test_Invalid(self) -> None:
		with self.assertRaises(TracingError) as context:
			_ = parseISO8601Timestamp("yesterday")

		self.assertEqual("'yesterday' isn't an ISO 8601 timestamp.", str(context.exception))


class Conversion(Testcase):
	def test_Trace(self) -> None:
		trace = ConvertWorkflowRun(_run(), [])

		self.assertEqual("Pipeline", trace.Name)
		self.assertEqual(600.0, trace.Duration)
		self.assertEqual("pipeline", trace[SPAN_KIND])
		self.assertEqual("Pipeline", trace["cicd.pipeline.name"])
		self.assertEqual("4711", trace["cicd.pipeline.run.id"])
		self.assertEqual("success", trace["cicd.pipeline.result"])
		self.assertEqual(1, trace["github.run.attempt"])
		self.assertEqual("dev", trace["vcs.ref.head.name"])
		self.assertEqual("0123abcd", trace["vcs.ref.head.revision"])

	def test_Trace_Running(self) -> None:
		trace = ConvertWorkflowRun(_run(status="in_progress", conclusion=None), [])

		self.assertIsNone(trace.StopTime)
		self.assertNotIn("cicd.pipeline.result", trace)

	def test_Job(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Build", 1, 4, 10)])
		children = _children(trace)

		self.assertListEqual(["Build (queued)", "Build"], [span.Name for span in trace.IterateSubSpans()])

		queued = children["Build (queued)"]
		self.assertEqual("queued", queued[SPAN_KIND])
		self.assertEqual(3.0, queued.Duration)
		self.assertListEqual(["ubuntu-26.04"], queued["github.runner.labels"])

		job = children["Build"]
		self.assertEqual("job", job[SPAN_KIND])
		self.assertEqual(6.0, job.Duration)
		self.assertEqual("Build", job["cicd.pipeline.task.name"])
		self.assertEqual("success", job["cicd.pipeline.task.run.result"])
		self.assertEqual("GitHub Actions 1000184490", job["cicd.worker.name"])
		self.assertEqual("GitHub Actions", job["github.runner.group"])
		self.assertListEqual(["ubuntu-26.04"], job["github.runner.labels"])

	def test_Job_NoWait(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Build", 4, 4, 10)])

		self.assertListEqual(["Build"], [span.Name for span in trace.IterateSubSpans()])

	def test_Job_Waiting(self) -> None:
		"""A job that didn't start yet is only waiting."""
		trace = ConvertWorkflowRun(_run(), [_job("Build", 1, None, None, status="queued")])
		spans = list(trace.IterateSubSpans())

		self.assertListEqual(["Build (queued)"], [span.Name for span in spans])
		self.assertIsNone(spans[0].StopTime)

	def test_Job_Running(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Build", 1, 4, None)])
		job = _children(trace)["Build"]

		self.assertIsNone(job.StopTime)
		self.assertNotIn("cicd.pipeline.task.run.result", job)

	def test_Job_Skipped(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Release", 3, 3, 3, conclusion="skipped", runner_name="", labels=[])])
		spans = list(trace.IterateSubSpans())

		self.assertListEqual(["Release"], [span.Name for span in spans])
		self.assertEqual(0.0, spans[0].Duration)
		self.assertEqual("skip", spans[0]["cicd.pipeline.task.run.result"])
		self.assertNotIn("cicd.worker.name", spans[0])
		self.assertNotIn("github.runner.labels", spans[0])

	def test_Job_EndBeforeBegin(self) -> None:
		"""GitHub's whole-second timestamps occasionally put the end a second before the begin."""
		trace = ConvertWorkflowRun(_run(), [_job("Build", 4, 5, 4)])

		self.assertEqual(0.0, _children(trace)["Build"].Duration)

	def test_Steps(self) -> None:
		steps = [
			{"name": "Set up job", "number": 1, "status": "completed", "conclusion": "success", "started_at": _time(5), "completed_at": _time(6)},
			{"name": "Compile", "number": 2, "status": "completed", "conclusion": "failure", "started_at": _time(6), "completed_at": _time(9)},
			{"name": "Upload", "number": 3, "status": "completed", "conclusion": "skipped", "started_at": None, "completed_at": None},
		]
		trace = ConvertWorkflowRun(_run(), [_job("Build", 4, 5, 10, steps=steps)])
		job = _children(trace)["Build"]
		stepSpans = list(job.IterateSubSpans())

		self.assertListEqual(["Set up job", "Compile"], [span.Name for span in stepSpans])
		self.assertEqual("step", stepSpans[1][SPAN_KIND])
		self.assertEqual(3.0, stepSpans[1].Duration)
		self.assertEqual(2, stepSpans[1]["github.step.number"])
		self.assertEqual("failure", stepSpans[1]["cicd.pipeline.task.run.result"])

	def test_Results(self) -> None:
		conclusions = {"cancelled": "cancellation", "timed_out": "timeout", "action_required": "error", "neutral": "error"}
		jobs = [_job(conclusion, 1, 2, 3, conclusion=conclusion) for conclusion in conclusions]
		children = _children(ConvertWorkflowRun(_run(), jobs))

		for conclusion, result in conclusions.items():
			with self.subTest(conclusion=conclusion):
				self.assertEqual(result, children[conclusion]["cicd.pipeline.task.run.result"])
				self.assertEqual(conclusion, children[conclusion]["github.conclusion"])

	def test_ReusableWorkflow(self) -> None:
		jobs = [_job("Prepare", 0, 2, 8), _job("UnitTesting / Linux", 10, 12, 60), _job("UnitTesting / Windows", 10, 30, 90)]
		trace = ConvertWorkflowRun(_run(), jobs)
		children = _children(trace)

		self.assertListEqual(["Prepare (queued)", "Prepare", "UnitTesting"], [span.Name for span in trace.IterateSubSpans()])

		group = children["UnitTesting"]
		self.assertEqual("workflow", group[SPAN_KIND])
		self.assertEqual(parseISO8601Timestamp(_time(10)), group.StartTime)
		self.assertEqual(80.0, group.Duration)
		self.assertListEqual(
			["Linux (queued)", "Linux", "Windows (queued)", "Windows"], [span.Name for span in group.IterateSubSpans()]
		)
		self.assertEqual("UnitTesting / Linux", _children(group)["Linux"]["cicd.pipeline.task.name"])

	def test_ReusableWorkflow_Nested(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Release / Publish / PyPI", 100, 101, 120)])
		release = _children(trace)["Release"]
		publish = _children(release)["Publish"]

		self.assertEqual("workflow", publish[SPAN_KIND])
		self.assertIn("PyPI", _children(publish))

	def test_ReusableWorkflow_Running(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Tests / Linux", 10, 12, 60), _job("Tests / Windows", 10, 30, None)])

		self.assertIsNone(_children(trace)["Tests"].StopTime)

	def test_Order(self) -> None:
		"""Jobs and called workflows are ordered by the time they were queued, not by the API's order."""
		trace = ConvertWorkflowRun(_run(), [_job("Late", 50, 50, 60), _job("Group / Early", 5, 5, 9), _job("Middle", 20, 20, 30)])

		self.assertListEqual(["Group", "Middle", "Late"], [span.Name for span in trace.IterateSubSpans()])

	def test_OTLPExport(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Tests / Linux", 1, 4, 10), _job("Build", 1, 1, 5)])
		spans = trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"]

		self.assertEqual(5, len(spans), "The trace, a group, a waiting and a running job, and a job without waiting.")

	def test_RunType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = ConvertWorkflowRun([], [])

		self.assertEqual("Parameter 'run' is not of type 'dict'.", str(context.exception))

	def test_MissingField(self) -> None:
		job = _job("Build", 1, 2, 3)
		del job["name"]

		with self.assertRaises(TracingError) as context:
			_ = ConvertWorkflowRun(_run(), [job])

		self.assertEqual("Field 'jobs[0].name' is missing.", str(context.exception))


class _Response:
	"""A fake HTTP response for :func:`urllib.request.urlopen`."""

	def __init__(self, document: Any, link: Nullable[str] = None) -> None:
		"""
		Initializes a fake response.

		:param document: The JSON document to answer with.
		:param link:     Optional, the ``Link`` header.
		"""
		self._body = json_dumps(document).encode()
		self.headers = {} if link is None else {"Link": link}

	def read(self) -> bytes:
		"""
		Return the response's body.

		:returns: The encoded JSON document.
		"""
		return self._body

	def close(self) -> None:
		"""
		Close the response, as :class:`~urllib.error.HTTPError` does with the response it wraps.
		"""

	def __enter__(self) -> "_Response":
		"""
		Enter the response's context.

		:returns: The response.
		"""
		return self

	def __exit__(self, *_: Any) -> None:
		"""
		Leave the response's context.

		:param _: Exception information.
		"""


class Reader(Testcase):
	_api = "https://api.github.com/repos/owner/repo/actions/runs/4711"

	def _Serve(self, answers: dict[str, _Response]) -> tuple[mock.MagicMock, list]:
		"""
		Patch :func:`urlopen` to answer requests from a dictionary of URLs.

		:param answers: Dictionary of a URL to its response.
		:returns:       The patcher, and the list collecting the requests.
		"""
		requests = []

		def urlopen(request, timeout):
			"""
			Nested function answering a request.

			:param request: The request.
			:param timeout: The request's timeout.
			:returns:       The response for the request's URL.
			"""
			requests.append(request)
			return answers[request.full_url]

		return mock.patch("pyTooling.Tracing.CI.GitHub.urlopen", side_effect=urlopen), requests

	def test_ReadRun(self) -> None:
		patcher, requests = self._Serve({
			self._api:                                          _Response(_run()),
			f"{self._api}/jobs?filter=latest&per_page=100":      _Response(
				{"jobs": [_job("A", 1, 2, 3)]}, f'<{self._api}/jobs?filter=latest&per_page=100&page=2>; rel="next"'
			),
			f"{self._api}/jobs?filter=latest&per_page=100&page=2": _Response({"jobs": [_job("B", 1, 2, 3)]}),
		})
		with patcher:
			trace = WorkflowRunReader("owner/repo", token="secret").ReadRun(4711)

		self.assertEqual({"A", "A (queued)", "B", "B (queued)"}, set(_children(trace)))
		self.assertEqual(3, len(requests))
		self.assertEqual("Bearer secret", requests[0].get_header("Authorization"))
		self.assertEqual("application/vnd.github+json", requests[0].get_header("Accept"))

	def test_ReadRun_Attempt(self) -> None:
		patcher, requests = self._Serve({
			f"{self._api}/attempts/2":                    _Response(_run(run_attempt=2)),
			f"{self._api}/attempts/2/jobs?per_page=100": _Response({"jobs": []}),
		})
		with patcher:
			trace = WorkflowRunReader("owner/repo").ReadRun(4711, attempt=2)

		self.assertEqual(2, trace["github.run.attempt"])
		self.assertIsNone(requests[0].get_header("Authorization"), "Without a token, the request is anonymous.")

	def test_HTTPError(self) -> None:
		def urlopen(request, timeout):
			"""
			Nested function failing a request.

			:param request: The request.
			:param timeout: The request's timeout.
			"""
			raise HTTPError(request.full_url, 404, "Not Found", {}, _Response({"message": "Not Found"}))

		with mock.patch("pyTooling.Tracing.CI.GitHub.urlopen", side_effect=urlopen):
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo", token="secret").ReadRun(4711)

		self.assertEqual(f"GitHub API request failed with HTTP 404: {self._api}", str(context.exception))
		self.assertIn("GitHub: Not Found", context.exception.__notes__)
		self.assertNotIn("secret", str(context.exception) + "".join(context.exception.__notes__))

	def test_Unreachable(self) -> None:
		with mock.patch("pyTooling.Tracing.CI.GitHub.urlopen", side_effect=URLError("no route to host")):
			with mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
				with self.assertRaises(TracingError) as context:
					_ = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertEqual(f"GitHub API couldn't be reached: {self._api}", str(context.exception))
		self.assertIn("Reason: no route to host", context.exception.__notes__)
		self.assertIn("Tried 4 times.", context.exception.__notes__)
		self.assertEqual(3, sleep.call_count)

	def _Failing(self, statuses: list, answers: dict[str, "_Response"], headers: Nullable[dict] = None):
		"""
		Patch :func:`urlopen` to fail with the given HTTP statuses first, then to answer from a dictionary of URLs.

		:param statuses: HTTP status codes, or exceptions, to fail the first requests with, in order.
		:param answers:  Dictionary of a URL to its response, for the requests after the failures.
		:param headers:  Optional, the headers of a failing answer.
		:returns:        The patcher, and the list collecting the requests.
		"""
		requests = []
		failures = list(statuses)

		def urlopen(request, timeout):
			"""
			Nested function failing or answering a request.

			:param request: The request.
			:param timeout: The request's timeout.
			:returns:       The response for the request's URL.
			"""
			requests.append(request)
			if len(failures) > 0:
				failure = failures.pop(0)
				if isinstance(failure, int):
					raise HTTPError(request.full_url, failure, "failure", headers or {}, _Response({"message": "failure"}))
				raise failure
			return answers[request.full_url]

		return mock.patch("pyTooling.Tracing.CI.GitHub.urlopen", side_effect=urlopen), requests

	def _Answers(self) -> dict[str, "_Response"]:
		"""
		Return the answers for a run without jobs.

		:returns: Dictionary of a URL to its response.
		"""
		return {self._api: _Response(_run()), f"{self._api}/jobs?filter=latest&per_page=100": _Response({"jobs": []})}

	def test_RetryTransient(self) -> None:
		patcher, requests = self._Failing([504], self._Answers())
		with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
			trace = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertEqual("Pipeline", trace.Name)
		self.assertEqual(3, len(requests), "The run was requested twice, then its jobs.")
		sleep.assert_called_once_with(2.0)

	def test_RetriesExhausted(self) -> None:
		patcher, requests = self._Failing([503, 503, 503, 503], self._Answers())
		with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo", token="secret").ReadRun(4711)

		self.assertEqual(f"GitHub API request failed with HTTP 503: {self._api}", str(context.exception))
		self.assertIn("Tried 4 times.", context.exception.__notes__)
		self.assertEqual([mock.call(2.0), mock.call(4.0), mock.call(8.0)], sleep.call_args_list)
		self.assertEqual(4, len(requests))

	def test_NoRetryForNotFound(self) -> None:
		patcher, requests = self._Failing([404], self._Answers())
		with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertEqual(f"GitHub API request failed with HTTP 404: {self._api}", str(context.exception))
		self.assertNotIn("Tried 1 times.", context.exception.__notes__)
		self.assertEqual(1, len(requests))
		sleep.assert_not_called()

	def test_NoRetries(self) -> None:
		patcher, requests = self._Failing([504], self._Answers())
		with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
			with self.assertRaises(TracingError):
				_ = WorkflowRunReader("owner/repo", retries=0).ReadRun(4711)

		self.assertEqual(1, len(requests))
		sleep.assert_not_called()

	def test_RetryAfter(self) -> None:
		"""A 'Retry-After' header demanding a longer pause is respected, but not beyond a minute."""
		for retryAfter, expected in (("10", 10.0), ("1", 2.0), ("3600", 60.0), ("Wed, 21 Oct 2026 07:28:00 GMT", 2.0)):
			with self.subTest(retryAfter=retryAfter):
				patcher, _ = self._Failing([429], self._Answers(), headers={"Retry-After": retryAfter})
				with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
					_ = WorkflowRunReader("owner/repo").ReadRun(4711)

				sleep.assert_called_once_with(expected)

	def test_RetryUnreachable(self) -> None:
		patcher, requests = self._Failing([URLError("timed out"), TimeoutError("timed out")], self._Answers())
		with patcher, mock.patch("pyTooling.Tracing.CI.GitHub.sleep") as sleep:
			trace = WorkflowRunReader("owner/repo", retryDelay=0.5).ReadRun(4711)

		self.assertEqual("Pipeline", trace.Name)
		self.assertEqual([mock.call(0.5), mock.call(1.0)], sleep.call_args_list)

	def test_RetryParameters(self) -> None:
		reader = WorkflowRunReader("owner/repo", retries=5, retryDelay=1)

		self.assertEqual((5, 1.0), (reader.Retries, reader.RetryDelay))
		self.assertEqual((3, 2.0), (WorkflowRunReader("owner/repo").Retries, WorkflowRunReader("owner/repo").RetryDelay))
		with self.assertRaises(TypeError):
			_ = WorkflowRunReader("owner/repo", retries="3")
		with self.assertRaises(ValueError):
			_ = WorkflowRunReader("owner/repo", retries=-1)
		with self.assertRaises(TypeError):
			_ = WorkflowRunReader("owner/repo", retryDelay=True)
		with self.assertRaises(ValueError):
			_ = WorkflowRunReader("owner/repo", retryDelay=-0.1)

	def test_ForeignNextPage(self) -> None:
		"""A token is only sent to the API, so a next page elsewhere is refused."""
		patcher, requests = self._Serve({
			self._api:                                     _Response(_run()),
			f"{self._api}/jobs?filter=latest&per_page=100": _Response({"jobs": []}, '<https://example.com/jobs>; rel="next"'),
		})
		with patcher:
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo", token="secret").ReadRun(4711)

		self.assertEqual("GitHub API's next page is outside the API: https://example.com/jobs", str(context.exception))
		self.assertEqual(2, len(requests))

	def test_InvalidJSON(self) -> None:
		response = _Response(None)
		response._body = b"<html>"

		with mock.patch("pyTooling.Tracing.CI.GitHub.urlopen", return_value=response):
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertEqual(f"GitHub API answered with invalid JSON: {self._api}", str(context.exception))

	def test_Repository(self) -> None:
		for repository in ("repo", "owner/", "owner/repo/extra"):
			with self.subTest(repository=repository):
				with self.assertRaises(ValueError):
					_ = WorkflowRunReader(repository)

		self.assertEqual("owner/repo", WorkflowRunReader("owner/repo").Repository)
		self.assertEqual("https://ghe.example.com/api/v3", WorkflowRunReader("owner/repo", apiURL="https://ghe.example.com/api/v3/").APIURL)

	def test_RunID(self) -> None:
		reader = WorkflowRunReader("owner/repo")

		with self.assertRaises(TypeError):
			_ = reader.ReadRun("4711")
		with self.assertRaises(ValueError):
			_ = reader.ReadRun(0)
		with self.assertRaises(ValueError):
			_ = reader.ReadRun(4711, attempt=0)


class Containment(Testcase):
	"""A timespan has to lie within its parent, which GitHub's timestamps don't guarantee."""

	_RUN = {
		"id":             1,
		"name":           "Pipeline",
		"status":         "completed",
		"run_started_at": "2026-09-17T10:00:10Z",
		"created_at":     "2026-09-17T10:00:05Z",
		"updated_at":     "2026-09-17T10:05:00Z",
		"conclusion":     "success",
	}

	@staticmethod
	def _Job(**fields: Any) -> dict[str, Any]:
		job = {"id": 11, "name": "Build", "status": "completed", "conclusion": "success", "steps": []}
		job.update(fields)

		return job

	@staticmethod
	def _SubSpan(parent: Span, name: str) -> Span:
		for span in parent.IterateSubSpans():
			if span.Name == name:
				return span

		raise AssertionError(f"No sub-span '{name}' in '{parent.Name}'.")

	@staticmethod
	def _Step(**fields: Any) -> dict[str, Any]:
		step = {"name": "Compile", "number": 1, "status": "completed", "conclusion": "success"}
		step.update(fields)

		return step

	def test_JobQueuedBeforeTheRunStarted(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:00Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:04:00Z"
		)])

		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:00Z"), trace.StartTime)

	def test_JobCompletedAfterTheRunsLastUpdate(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:09:00Z"
		)])

		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:09:00Z"), trace.StopTime)

	def test_StepStartedBeforeItsJob(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:02:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:25Z", completed_at="2026-09-17T10:00:50Z")]
		)])

		job = self._SubSpan(trace, "Build")
		self.assertLessEqual(job.StartTime, parseISO8601Timestamp("2026-09-17T10:00:25Z"))
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:25Z"), self._SubSpan(job, "Compile").StartTime)

	def test_StepCompletedAfterItsJob(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:01:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:40Z", completed_at="2026-09-17T10:02:00Z")]
		)])

		job = self._SubSpan(trace, "Build")
		self.assertGreaterEqual(job.StopTime, parseISO8601Timestamp("2026-09-17T10:02:00Z"))
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:02:00Z"), self._SubSpan(job, "Compile").StopTime)

	def test_GroupedJobOutsideTheRun(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			name="Caller / Build",
			created_at="2026-09-17T09:59:00Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:09:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:31Z", completed_at="2026-09-17T10:08:00Z")]
		)])

		self.assertEqual(parseISO8601Timestamp("2026-09-17T09:59:00Z"), trace.StartTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:09:00Z"), trace.StopTime)

	def test_ConsistentTimestampsAreUnchanged(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:02:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:35Z", completed_at="2026-09-17T10:01:50Z")]
		)])

		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:10Z"), trace.StartTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:05:00Z"), trace.StopTime)
