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
from urllib.error                import HTTPError

from pyTooling.CI.GitHub         import GitHubError
from pyTooling.Common            import parseISO8601Timestamp
from pyTooling.Exceptions        import ToolingException
from pyTooling.REST              import RESTError
from pyTooling.Tracing           import Span, Trace, TracingError
from pyTooling.Tracing.CI        import CI, OTLP, Result, SpanKind
from pyTooling.Tracing.CI.GitHub import ConvertWorkflowRun, GitHub, WorkflowRunReader
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
	timestamp = datetime(2026, 9, 15, 6, 35, 0, tzinfo=timezone.utc) + timedelta(seconds=seconds)
	return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")


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


def _job(
	name: str,
	created: Nullable[int],
	started: Nullable[int],
	completed: Nullable[int],
	**fields: Any
) -> dict[str, Any]:
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
		"created_at": None if created is None else _time(created),
		"started_at": None if started is None else _time(started),
		"completed_at": None if completed is None else _time(completed),
		"labels": ["ubuntu-26.04"],
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


class AttributeKeys(Testcase):
	"""A namespace of attribute keys is nested the way the key is spelled, so the path names the key."""

	@staticmethod
	def _keys(namespace: type, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
		"""
		Walk a namespace of attribute keys.

		:param namespace: The namespace class to walk.
		:param path:      Names of the enclosing namespaces.
		:returns:         For every key, the path naming it and the key's value.
		"""
		found = []
		for name, member in vars(namespace).items():
			if name.startswith("_"):
				continue
			elif isinstance(member, type):
				found += AttributeKeys._keys(member, path + (name,))
			elif isinstance(member, str):
				found.append((path + (name,), member))

		return found

	def test_EveryPathSpellsItsKey(self) -> None:
		# 'OTLP' names the authority and is not part of the key; 'CI' and 'GitHub' are the key's own prefix
		for namespace, prefix in ((OTLP, ()), (CI, ("CI",)), (GitHub, ("GitHub",))):
			for path, key in self._keys(namespace):
				with self.subTest(path=namespace.__name__ + "." + ".".join(path)):
					self.assertEqual(".".join(prefix + path).lower(), key)

	def test_TheNamespacesAreNotEmpty(self) -> None:
		self.assertEqual(11, len(self._keys(OTLP)))
		self.assertEqual(1, len(self._keys(CI)))
		self.assertEqual(9, len(self._keys(GitHub)))

	def test_TheResultsAreTheOnesTheConventionsAllow(self) -> None:
		self.assertSetEqual(
			{"success", "failure", "timeout", "skip", "cancellation", "error"},
			{result.value for result in Result}
		)

	def test_AnEnumMemberIsWrittenAsItsString(self) -> None:
		"""A backend groups by the attribute's string, so the member has to reach OTLP as that exact string."""
		trace = Trace("Pipeline")
		trace[CI.Span.Kind] = SpanKind.Pipeline
		trace[OTLP.CICD.Pipeline.Result] = Result.Cancellation

		attributes = {
			attribute["key"]: attribute["value"]
			for attribute in trace.ToJSON()["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["attributes"]
		}
		self.assertEqual({"stringValue": "pipeline"}, attributes["ci.span.kind"])
		self.assertEqual({"stringValue": "cancellation"}, attributes["cicd.pipeline.result"])


class Conversion(Testcase):
	def test_Trace(self) -> None:
		trace = ConvertWorkflowRun(_run(), [])

		self.assertEqual("Pipeline", trace.Name)
		self.assertEqual(600.0, trace.Duration)
		self.assertEqual("pipeline", trace[CI.Span.Kind])
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
		self.assertEqual("queued", queued[CI.Span.Kind])
		self.assertEqual(3.0, queued.Duration)
		self.assertListEqual(["ubuntu-26.04"], queued["github.runner.labels"])

		job = children["Build"]
		self.assertEqual("job", job[CI.Span.Kind])
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
			{"name": "Set up job", "number": 1, "status": "completed", "conclusion": "success",
			 "started_at": _time(5), "completed_at": _time(6)},
			{"name": "Compile", "number": 2, "status": "completed", "conclusion": "failure",
			 "started_at": _time(6), "completed_at": _time(9)},
			{"name": "Upload", "number": 3, "status": "completed", "conclusion": "skipped",
			 "started_at": None, "completed_at": None},
		]
		trace = ConvertWorkflowRun(_run(), [_job("Build", 4, 5, 10, steps=steps)])
		job = _children(trace)["Build"]
		stepSpans = list(job.IterateSubSpans())

		self.assertListEqual(["Set up job", "Compile"], [span.Name for span in stepSpans])
		self.assertEqual("step", stepSpans[1][CI.Span.Kind])
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
		jobs = [
			_job("Prepare", 0, 2, 8),
			_job("UnitTesting / Linux", 10, 12, 60),
			_job("UnitTesting / Windows", 10, 30, 90),
		]
		trace = ConvertWorkflowRun(_run(), jobs)
		children = _children(trace)

		spanNames = [span.Name for span in trace.IterateSubSpans()]
		self.assertListEqual(["Prepare (queued)", "Prepare", "UnitTesting"], spanNames)

		group = children["UnitTesting"]
		self.assertEqual("workflow", group[CI.Span.Kind])
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

		self.assertEqual("workflow", publish[CI.Span.Kind])
		self.assertIn("PyPI", _children(publish))

	def test_ReusableWorkflow_Running(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Tests / Linux", 10, 12, 60), _job("Tests / Windows", 10, 30, None)])

		self.assertIsNone(_children(trace)["Tests"].StopTime)

	def test_Order(self) -> None:
		"""Jobs and called workflows are ordered by the time they were queued, not by the API's order."""
		jobs = [_job("Late", 50, 50, 60), _job("Group / Early", 5, 5, 9), _job("Middle", 20, 20, 30)]
		trace = ConvertWorkflowRun(_run(), jobs)

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
		"""Reading the payload is the model's job, so a malformed one raises its exception, not a tracing one."""
		job = _job("Build", 1, 2, 3)
		del job["name"]

		with self.assertRaises(GitHubError) as context:
			_ = ConvertWorkflowRun(_run(), [job])

		self.assertEqual("Field 'jobs[0].name' is missing.", str(context.exception))

	def test_MissingFieldIsStillAToolingException(self) -> None:
		"""Both exceptions derive from it, so a consumer catching the base is unaffected by the change."""
		job = _job("Build", 1, 2, 3)
		del job["name"]

		with self.assertRaises(ToolingException):
			_ = ConvertWorkflowRun(_run(), [job])


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

		return mock.patch("pyTooling.REST.urlopen", side_effect=urlopen), requests

	def _Answers(self) -> dict[str, "_Response"]:
		"""
		Return the answers for a run without jobs.

		:returns: Dictionary of a URL to its response.
		"""
		return {self._api: _Response(_run()), f"{self._api}/jobs?filter=latest&per_page=100": _Response({"jobs": []})}

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

	def test_MissingJobsField(self) -> None:
		patcher, _ = self._Serve({
			self._api:                                     _Response(_run()),
			f"{self._api}/jobs?filter=latest&per_page=100": _Response({}),
		})
		with patcher:
			with self.assertRaises(TracingError) as context:
				_ = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertIn("Field 'jobs' is missing", str(context.exception))

	def test_HTTPErrorExplainsWhatToCheck(self) -> None:
		"""A status GitHub answers with is explained, and the token doesn't reach the message."""
		def urlopen(request, timeout):
			"""
			Nested function failing a request.

			:param request: The request.
			:param timeout: The request's timeout.
			"""
			raise HTTPError(request.full_url, 404, "Not Found", {}, _Response({"message": "Not Found"}))

		with mock.patch("pyTooling.REST.urlopen", side_effect=urlopen):
			with self.assertRaises(RESTError) as context:
				_ = WorkflowRunReader("owner/repo", token="secret").ReadRun(4711)

		self.assertEqual(f"Request failed with HTTP 404: {self._api}", str(context.exception))
		self.assertIn("Answer: Not Found", context.exception.__notes__)
		self.assertIn(
			"Check the repository's name, and that the token may read the repository's actions.",
			context.exception.__notes__
		)
		self.assertNotIn("secret", str(context.exception) + "".join(context.exception.__notes__))

	def test_RetryTransient(self) -> None:
		"""A run is read although the first request failed transiently."""
		requests = []
		answers = self._Answers()
		failed = False

		def urlopen(request, timeout):
			"""
			Nested function failing the first request, then answering from the dictionary.

			:param request: The request.
			:param timeout: The request's timeout.
			:returns:       The response for the request's URL.
			"""
			nonlocal failed
			requests.append(request)
			if not failed:
				failed = True
				raise HTTPError(request.full_url, 504, "failure", {}, _Response({"message": "failure"}))
			return answers[request.full_url]

		with mock.patch("pyTooling.REST.urlopen", side_effect=urlopen):
			with mock.patch("pyTooling.REST.sleep") as sleep:
				trace = WorkflowRunReader("owner/repo").ReadRun(4711)

		self.assertEqual("Pipeline", trace.Name)
		self.assertEqual(3, len(requests), "The run was requested twice, then its jobs.")
		sleep.assert_called_once_with(2.0)

	def test_RetryParameters(self) -> None:
		"""The reader hands the request parameters to the client it is."""
		reader = WorkflowRunReader("owner/repo", retries=5, retryDelay=1)

		self.assertEqual((5, 1.0), (reader.Retries, reader.RetryDelay))
		self.assertEqual((3, 2.0), (WorkflowRunReader("owner/repo").Retries, WorkflowRunReader("owner/repo").RetryDelay))
		with self.assertRaises(TypeError):
			_ = WorkflowRunReader("owner/repo", retries="3")
		with self.assertRaises(ValueError):
			_ = WorkflowRunReader("owner/repo", retryDelay=-0.1)

	def test_Repository(self) -> None:
		for repository in ("repo", "owner/", "owner/repo/extra"):
			with self.subTest(repository=repository):
				with self.assertRaises(ValueError):
					_ = WorkflowRunReader(repository)

		self.assertEqual("owner/repo", WorkflowRunReader("owner/repo").Repository)
		reader = WorkflowRunReader("owner/repo", apiURL="https://ghe.example.com/api/v3/")
		self.assertEqual("https://ghe.example.com/api/v3", reader.APIURL)

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

	def test_StepStartedBeforeItsGroupedJob(self) -> None:
		"""A called workflow derives its times from its jobs, which don't account for a step outside its job."""
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			name="Caller / Build",
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:02:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:15Z", completed_at="2026-09-17T10:00:50Z")]
		)])

		group = self._SubSpan(trace, "Caller")
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:15Z"), group.StartTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:15Z"), self._SubSpan(group, "Build").StartTime)

	def test_StepCompletedAfterItsGroupedJob(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			name="Caller / Build",
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:01:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:40Z", completed_at="2026-09-17T10:02:00Z")]
		)])

		group = self._SubSpan(trace, "Caller")
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:02:00Z"), group.StopTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:02:00Z"), self._SubSpan(group, "Build").StopTime)

	def test_AMatrixHoldsItsWidenedInstances(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			name="Caller / Build (fast)",
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:01:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:10Z", completed_at="2026-09-17T10:03:00Z")]
		)])

		matrix = self._SubSpan(self._SubSpan(trace, "Caller"), "Build")
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:10Z"), matrix.StartTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:03:00Z"), matrix.StopTime)

	def test_ARunningJobLeavesItsGroupRunning(self) -> None:
		trace = ConvertWorkflowRun(dict(self._RUN, status="in_progress", conclusion=None), [
			self._Job(name="Caller / Build", created_at="2026-09-17T10:00:20Z",
			          started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:01:00Z"),
			self._Job(name="Caller / Test", id=12, status="in_progress", conclusion=None,
			          created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at=None),
		])

		self.assertIsNone(self._SubSpan(trace, "Caller").StopTime)

	def test_ConsistentTimestampsAreUnchanged(self) -> None:
		trace = ConvertWorkflowRun(self._RUN, [self._Job(
			created_at="2026-09-17T10:00:20Z", started_at="2026-09-17T10:00:30Z", completed_at="2026-09-17T10:02:00Z",
			steps=[self._Step(started_at="2026-09-17T10:00:35Z", completed_at="2026-09-17T10:01:50Z")]
		)])

		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:00:10Z"), trace.StartTime)
		self.assertEqual(parseISO8601Timestamp("2026-09-17T10:05:00Z"), trace.StopTime)


class Matrices(Testcase):
	"""A matrix becomes a timespan of its own, which the model reconstructs from the jobs' names."""

	def test_MatrixBecomesASpan(self) -> None:
		trace = ConvertWorkflowRun(_run(), [
			_job("Unit Tests (ubuntu-26.04, 3.14)", 10, 12, 60),
			_job("Unit Tests (windows-2025, 3.14)", 10, 12, 90),
		])

		matrix = _children(trace)["Unit Tests"]

		self.assertEqual("matrix", matrix[CI.Span.Kind])
		self.assertEqual(2, len([name for name in _children(matrix) if not name.endswith("(queued)")]))

	def test_InstancesAreNamedByTheirDimensions(self) -> None:
		trace = ConvertWorkflowRun(_run(), [
			_job("Unit Tests (ubuntu-26.04, 3.14)", 10, 12, 60),
			_job("Unit Tests (windows-2025, 3.14)", 10, 12, 90),
		])

		names = set(_children(_children(trace)["Unit Tests"]))

		self.assertIn("Unit Tests (ubuntu-26.04, 3.14)", names)
		self.assertIn("Unit Tests (windows-2025, 3.14)", names)

	def test_InstanceCarriesItsDimensionsAsAnAttribute(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Unit Tests (ubuntu-26.04, 3.14)", 10, 12, 60)])
		instance = _children(_children(trace)["Unit Tests"])["Unit Tests (ubuntu-26.04, 3.14)"]

		self.assertListEqual(["ubuntu-26.04", "3.14"], instance["github.matrix.dimensions"])

	def test_TaskNameKeepsTheCallerPrefix(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("UnitTesting / Unit Tests (ubuntu-26.04)", 10, 12, 60)])
		matrix = _children(_children(trace)["UnitTesting"])["Unit Tests"]
		instance = _children(matrix)["Unit Tests (ubuntu-26.04)"]

		self.assertEqual("UnitTesting / Unit Tests (ubuntu-26.04)", instance["cicd.pipeline.task.name"])

	def test_AMatrixInsideACalledWorkflow(self) -> None:
		trace = ConvertWorkflowRun(_run(), [_job("Docs / Sphinx (html)", 10, 12, 60)])

		workflow = _children(trace)["Docs"]
		self.assertEqual("workflow", workflow[CI.Span.Kind])

		matrix = _children(workflow)["Sphinx"]
		self.assertEqual("matrix", matrix[CI.Span.Kind])
