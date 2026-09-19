# ==================================================================================================================== #
#             _____           _ _               ____ ___                                                               #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|_ _|                                                              #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |    | |                                                               #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___ | |                                                               #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|___|                                                              #
# |_|    |___/                          |___/                                                                          #
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
Unit tests for :mod:`pyTooling.CI.GitHub`.
"""
from datetime            import datetime, timezone
from typing              import Any, Optional as Nullable

from pyTooling.CI.GitHub import Base, PipelineGroup, Pipeline, Workflow, Matrix, MatrixJob, Job, JobGroup, Step
from pyTooling.CI.GitHub import Status, Conclusion, Event, GitHubError, QualifiedNameMixin
from pyTooling.MetaClasses import AbstractClassError, ExtendedType, UnfulfilledExpectationError
from pyTooling.Testing   import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


def _time(seconds: int) -> str:
	"""
	Return a GitHub timestamp the given number of seconds after the run was created.

	:param seconds: Seconds after 2026-09-17T10:00:00Z.
	:returns:       The timestamp, as GitHub formats it.
	"""
	return f"2026-09-17T10:{seconds // 60:02d}:{seconds % 60:02d}Z"


def _run(**fields: Any) -> dict[str, Any]:
	"""
	Build a completed workflow run.

	:param fields: Fields overriding the defaults.
	:returns:      The run, as the GitHub REST API returns it.
	"""
	run = {
		"id": 4711, "name": "Pipeline", "status": "completed", "conclusion": "success",
		"created_at": _time(0), "run_started_at": _time(10), "updated_at": _time(600),
		"run_number": 42, "run_attempt": 1, "event": "push", "head_branch": "dev", "head_sha": "0123abcd",
		"html_url": "https://github.com/owner/repo/actions/runs/4711",
	}
	run.update(fields)

	return run


def _job(name: str, created: int, started: Nullable[int], completed: Nullable[int], **fields: Any) -> dict[str, Any]:
	"""
	Build a job.

	:param name:      The job's name, including any calling workflows' prefixes.
	:param created:   Seconds after the run was created, when the job was created.
	:param started:   Seconds after the run was created, when the job started, or ``None``.
	:param completed: Seconds after the run was created, when the job completed, or ``None``.
	:param fields:    Fields overriding the defaults.
	:returns:         The job, as the GitHub REST API returns it.
	"""
	job = {
		"id": 1, "name": name, "status": "completed" if completed is not None else "in_progress",
		"conclusion": "success" if completed is not None else None,
		"created_at": _time(created),
		"started_at": None if started is None else _time(started),
		"completed_at": None if completed is None else _time(completed),
		"labels": ["ubuntu-26.04"], "runner_name": "GitHub Actions 1", "runner_group_name": "GitHub Actions",
		"steps": [],
	}
	job.update(fields)

	return job


class Enumerations(Testcase):
	def test_ParseStatus(self) -> None:
		self.assertIs(Status.Completed, Status.Parse("completed"))
		self.assertIs(Status.InProgress, Status.Parse("in_progress"))

	def test_ParseConclusion(self) -> None:
		self.assertIs(Conclusion.TimedOut, Conclusion.Parse("timed_out"))
		self.assertIs(Conclusion.StartupFailure, Conclusion.Parse("startup_failure"))

	def test_ParseNothing(self) -> None:
		self.assertIsNone(Status.Parse(None))
		self.assertIsNone(Status.Parse(""))
		self.assertIsNone(Conclusion.Parse(None))
		self.assertIsNone(Conclusion.Parse(""))

	def test_ParseUnknownStatus(self) -> None:
		with self.assertRaises(GitHubError) as context:
			_ = Status.Parse("nonsense")

		self.assertEqual("'nonsense' is not a GitHub status.", str(context.exception))

	def test_ParseUnknownConclusion(self) -> None:
		with self.assertRaises(GitHubError) as context:
			_ = Conclusion.Parse("exploded")

		self.assertEqual("'exploded' is not a GitHub conclusion.", str(context.exception))


class Construction(Testcase):
	def test_EmptyName(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Job("")

		self.assertEqual("Parameter 'name' is empty.", str(context.exception))

	def test_NameType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job(42)

		self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_StatusType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", status="completed")

		self.assertEqual("Parameter 'status' is not of type 'Status'.", str(context.exception))

	def test_ConclusionType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", conclusion="success")

		self.assertEqual("Parameter 'conclusion' is not of type 'Conclusion'.", str(context.exception))

	def test_StepAttachesToItsJob(self) -> None:
		job =  Job("Build")
		step = Step("Compile", 1, parent=job)

		self.assertIs(job, step.Parent)
		self.assertEqual([step], job.Steps)


class Conversion(Testcase):
	def test_Run(self) -> None:
		pipeline = Pipeline.FromJSON(_run())

		self.assertEqual("Pipeline", pipeline.Name)
		self.assertEqual(4711, pipeline.ID)
		self.assertEqual(42, pipeline.RunNumber)
		self.assertEqual(1, pipeline.RunAttempt)
		self.assertIs(Event.Push, pipeline.Event)
		self.assertEqual("dev", pipeline.GitReference)
		self.assertIs(Status.Completed, pipeline.Status)
		self.assertIs(Conclusion.Success, pipeline.Conclusion)
		self.assertIsNone(pipeline.Parent)
		self.assertIs(pipeline, pipeline.Pipeline)

	def test_RunNotCompletedHasNoEndTime(self) -> None:
		pipeline = Pipeline.FromJSON(_run(status="in_progress", conclusion=None))

		self.assertIsNone(pipeline.CompletedAt)
		self.assertIsNone(pipeline.Duration)

	def test_RunType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline.FromJSON("run")

		self.assertEqual("Parameter 'run' is not of type 'dict'.", str(context.exception))

	def test_MissingName(self) -> None:
		with self.assertRaises(GitHubError) as context:
			_ = Pipeline.FromJSON({"id": 1})

		self.assertEqual("Field 'run.name' is missing.", str(context.exception))

	def test_InvalidTimestamp(self) -> None:
		with self.assertRaises(GitHubError) as context:
			_ = Pipeline.FromJSON(_run(created_at="yesterday"))

		self.assertEqual("Field 'run.created_at' isn't an ISO 8601 timestamp.", str(context.exception))

	def test_NaiveTimestampIsUTC(self) -> None:
		pipeline = Pipeline.FromJSON(_run(created_at="2026-09-17T10:00:00"))

		self.assertEqual(timezone.utc, pipeline.CreatedAt.tzinfo)

	def test_Job(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 10, 20, 80)])
		job =      pipeline.Jobs[0]

		self.assertEqual("Build", job.Name)
		self.assertIs(pipeline, job.Parent)
		self.assertEqual(["ubuntu-26.04"], job.Labels)
		self.assertEqual("GitHub Actions", job.RunnerGroupName)
		self.assertEqual(10.0, job.QueuedDuration)
		self.assertEqual(60.0, job.Duration)

	def test_JobNotStarted(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 10, None, None)])
		job =      pipeline.Jobs[0]

		self.assertIsNone(job.StartedAt)
		self.assertIsNone(job.Duration)
		self.assertIsNone(job.QueuedDuration)
		self.assertIs(Status.InProgress, job.Status)
		self.assertIsNone(job.Conclusion)

	def test_Steps(self) -> None:
		steps = [
			{"name": "Set up job", "number": 1, "status": "completed", "conclusion": "success",
			 "started_at": _time(21), "completed_at": _time(25)},
			{"name": "Compile", "number": 2, "status": "completed", "conclusion": "failure",
			 "started_at": _time(25), "completed_at": _time(70)},
		]
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 10, 20, 80, steps=steps)])
		job =      pipeline.Jobs[0]

		self.assertEqual(2, len(job.Steps))
		self.assertEqual(["Set up job", "Compile"], [step.Name for step in job])
		self.assertEqual([1, 2], [step.Number for step in job])
		self.assertIs(Conclusion.Failure, job.Steps[1].Conclusion)
		self.assertIs(job, job.Steps[1].Parent)
		self.assertIs(pipeline, job.Steps[1].Pipeline)

	def test_CalledWorkflowGroupsItsJobs(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Prepare", 10, 20, 60),
			_job("UnitTesting / Linux", 60, 70, 300),
			_job("UnitTesting / Windows", 60, 90, 540),
		])

		self.assertEqual(["Prepare"], [job.Name for job in pipeline.Jobs])
		self.assertEqual(1, len(pipeline.Workflows))

		workflow = pipeline.Workflows["UnitTesting"]
		self.assertEqual("UnitTesting", workflow.Name)
		self.assertEqual(["Linux", "Windows"], [job.Name for job in workflow.Jobs])
		self.assertIs(pipeline, workflow.Parent)

	def test_CalledWorkflowsNest(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Docs / Sphinx / HTML", 60, 70, 180)])

		docs = pipeline.Workflows["Docs"]
		self.assertEqual("Docs", docs.Name)
		self.assertEqual([], docs.Jobs)

		sphinx = docs.Workflows["Sphinx"]
		self.assertEqual("Sphinx", sphinx.Name)

		job = sphinx.Jobs[0]
		self.assertEqual("HTML", job.Name)
		self.assertIs(sphinx, job.Parent)
		self.assertIs(pipeline, job.Pipeline)

	def test_CalledWorkflowSpansItsJobs(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("UnitTesting / Linux", 60, 70, 300),
			_job("UnitTesting / Windows", 60, 90, 540),
		])
		workflow = pipeline.Workflows["UnitTesting"]

		self.assertEqual(datetime(2026, 9, 17, 10, 1, 0, tzinfo=timezone.utc), workflow.CreatedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 1, 10, tzinfo=timezone.utc), workflow.StartedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 9, 0, tzinfo=timezone.utc), workflow.CompletedAt)
		self.assertEqual(470.0, workflow.Duration)

	def test_CalledWorkflowWithARunningJobHasNoEndTime(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("UnitTesting / Linux", 60, 70, 300),
			_job("UnitTesting / Windows", 60, 90, None),
		])

		self.assertIsNone(pipeline.Workflows["UnitTesting"].CompletedAt)

	def test_IterateJobsReachesEveryJob(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Prepare", 10, 20, 60),
			_job("UnitTesting / Linux", 60, 70, 300),
			_job("Docs / Sphinx / HTML", 60, 70, 180),
		])

		self.assertEqual({"Prepare", "Linux", "HTML"}, {job.Name for job in pipeline.IterateJobs()})

	def test_JobType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline.FromJSON(_run(), ["job"])

		self.assertEqual("Job 0 is not of type 'dict'.", str(context.exception))


class Matrices(Testcase):
	def test_MatrixGroupsItsInstances(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Unit Tests (ubuntu-26.04, 3.14)", 60, 70, 300),
			_job("Unit Tests (ubuntu-26.04, 3.11)", 60, 70, 360),
			_job("Unit Tests (windows-2025, 3.14)", 60, 90, 540),
		])

		self.assertEqual([], pipeline.Jobs)
		self.assertEqual(1, len(pipeline.Matrices))

		matrix = pipeline.Matrices["Unit Tests"]
		self.assertEqual("Unit Tests", matrix.Name)
		self.assertEqual(3, len(matrix.Instances))
		self.assertIs(pipeline, matrix.Parent)

	def test_InstanceCarriesItsDimensions(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Unit Tests (ubuntu-26.04, 3.14)", 60, 70, 300)])
		instance = pipeline.Matrices["Unit Tests"].Instances[0]

		self.assertIsInstance(instance, MatrixJob)
		self.assertEqual("Unit Tests", instance.Name)
		self.assertEqual(["ubuntu-26.04", "3.14"], instance.DimensionValues)
		self.assertEqual("Unit Tests (ubuntu-26.04, 3.14)", str(instance))

	def test_MatrixDimensionsOfEveryInstance(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Unit Tests (ubuntu-26.04, 3.14)", 60, 70, 300),
			_job("Unit Tests (windows-2025, 3.11)", 60, 90, 540),
		])

		self.assertEqual(
			[["ubuntu-26.04", "3.14"], ["windows-2025", "3.11"]],
			[instance.DimensionValues for instance in pipeline.Matrices["Unit Tests"].Instances]
		)

	def test_MatrixSpansItsInstances(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Unit Tests (a)", 60, 70, 300),
			_job("Unit Tests (b)", 60, 90, 540),
		])
		matrix = pipeline.Matrices["Unit Tests"]

		self.assertEqual(datetime(2026, 9, 17, 10, 1, 10, tzinfo=timezone.utc), matrix.StartedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 9, 0, tzinfo=timezone.utc), matrix.CompletedAt)
		self.assertEqual(470.0, matrix.Duration)

	def test_MatrixInsideACalledWorkflow(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Docs / Sphinx (html, latex)", 60, 70, 180)])

		workflow = pipeline.Workflows["Docs"]
		self.assertEqual("Docs", workflow.Name)

		matrix = workflow.Matrices["Sphinx"]
		self.assertEqual("Sphinx", matrix.Name)
		self.assertIs(workflow, matrix.Parent)
		self.assertIs(pipeline, matrix.Instances[0].Pipeline)

	def test_IterateJobsReachesMatrixInstances(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Prepare", 10, 20, 60),
			_job("Unit Tests (a)", 60, 70, 300),
			_job("Docs / Sphinx (html)", 60, 70, 180),
		])

		self.assertEqual(3, len(list(pipeline.IterateJobs())))

	def test_AJobWithoutBracketsIsNoMatrix(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Prepare", 10, 20, 60)])

		self.assertEqual(["Prepare"], [job.Name for job in pipeline.Jobs])
		self.assertEqual({}, pipeline.Matrices)
		self.assertNotIsInstance(pipeline.Jobs[0], MatrixJob)

	def test_EmptyBracketsAreNotDimensions(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("(detached)", 10, 20, 60)])

		self.assertEqual(["(detached)"], [job.Name for job in pipeline.Jobs])
		self.assertEqual({}, pipeline.Matrices)

	def test_ASingleBracketedJobBecomesAOneInstanceMatrix(self) -> None:
		"""Documented consequence: the bracketed suffix is a naming convention, not a field of the payload."""
		pipeline = Pipeline.FromJSON(_run(), [_job("Build (fast)", 10, 20, 60)])

		self.assertEqual(1, len(pipeline.Matrices))
		self.assertEqual("Build", pipeline.Matrices["Build"].Name)
		self.assertEqual(["fast"], pipeline.Matrices["Build"].Instances[0].DimensionValues)


class Hierarchy(Testcase):
	def test_GroupsShareTheirBehaviour(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Unit Tests (a)", 60, 70, 300)])

		self.assertIsInstance(pipeline, Workflow)
		self.assertIsInstance(pipeline, JobGroup)
		self.assertIsInstance(pipeline.Matrices["Unit Tests"], JobGroup)
		self.assertNotIsInstance(pipeline.Matrices["Unit Tests"], Workflow)

	def test_MatrixJobIsAJob(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Unit Tests (a)", 60, 70, 300)])
		instance = pipeline.Matrices["Unit Tests"].Instances[0]

		self.assertIsInstance(instance, Job)
		self.assertEqual(10.0, instance.QueuedDuration)
		self.assertEqual(["ubuntu-26.04"], instance.Labels)


class Times(Testcase):
	"""A job's times contain its steps, and a group's contain what is below it."""

	@staticmethod
	def _step(name: str, started: Nullable[int], completed: Nullable[int]) -> dict[str, Any]:
		"""
		Build a step.

		:param name:      The step's name.
		:param started:   Seconds after the run was created, when the step started, or ``None``.
		:param completed: Seconds after the run was created, when the step completed, or ``None``.
		:returns:         The step, as the GitHub REST API returns it.
		"""
		return {
			"name": name, "number": 1, "status": "completed" if completed is not None else "in_progress",
			"conclusion": "success" if completed is not None else None,
			"started_at": None if started is None else _time(started),
			"completed_at": None if completed is None else _time(completed),
		}

	def test_AStepStartingBeforeItsJob(self) -> None:
		"""GitHub reports whole seconds, so a step is sometimes reported as starting before the job holding it."""
		job = Job.FromJSON(_job("Build", 60, 70, 300, steps=[self._step("Checkout", 65, 80)]))

		self.assertEqual(_time(65), job.StartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(60), job.CreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

	def test_AStepCompletingAfterItsJob(self) -> None:
		job = Job.FromJSON(_job("Build", 60, 70, 300, steps=[self._step("Checkout", 70, 320)]))

		self.assertEqual(_time(320), job.CompletedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

	def test_AJobCreatedAfterItsFirstStepStarted(self) -> None:
		"""The job was created at the latest when something of it ran."""
		job = Job.FromJSON(_job("Build", 60, 70, 300, steps=[self._step("Checkout", 55, 80)]))

		self.assertEqual(_time(55), job.CreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(55), job.StartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

	def test_AJobWithConsistentSteps(self) -> None:
		job = Job.FromJSON(_job("Build", 60, 70, 300, steps=[self._step("Checkout", 75, 80)]))

		self.assertEqual(_time(60), job.CreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(70), job.StartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(300), job.CompletedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

	def test_ARunningJobReportsNoCompletion(self) -> None:
		"""A step that completed doesn't complete the job holding it."""
		job = Job.FromJSON(_job("Build", 60, 70, None, steps=[self._step("Checkout", 70, 80)]))

		self.assertIsNone(job.CompletedAt)

	def test_AGroupCoversTheWidenedTimes(self) -> None:
		"""A group aggregates the jobs' times, so it covers a step running outside its job too."""
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 60, 70, 300, steps=[self._step("Checkout", 65, 320)])])
		workflow = Pipeline.FromJSON(_run(), [
			_job("Caller / Build", 60, 70, 300, steps=[self._step("Checkout", 65, 320)])
		]).Workflows["Caller"]

		self.assertEqual(_time(65), workflow.StartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(320), workflow.CompletedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(4711, pipeline.ID, "The run's own times are unaffected.")


	def test_APipelineKeepsItsOwnTimes(self) -> None:
		"""A run reports its times, while 'Contents*At' spans what it holds."""
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 60, 70, 300)])

		self.assertEqual(_time(0), pipeline.CreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(10), pipeline.StartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(60), pipeline.ContentsCreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(70), pipeline.ContentsStartedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertEqual(_time(300), pipeline.ContentsCompletedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))

	def test_AGroupHoldingARunningElementHasNoEnd(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Done", 60, 70, 100), _job("Running", 60, 70, None)])

		self.assertIsNone(pipeline.ContentsCompletedAt)

	def test_AWorkflowHasOnlyTheOneSet(self) -> None:
		"""A called workflow reports no time of its own, so its times are the span of what it holds."""
		workflow = Pipeline.FromJSON(_run(), [_job("Caller / Build", 60, 70, 300)]).Workflows["Caller"]

		self.assertEqual(_time(60), workflow.CreatedAt.strftime("%Y-%m-%dT%H:%M:%SZ"))
		self.assertFalse(hasattr(workflow, "ContentsCreatedAt"), "Only a run has two sets of times.")


class Ordering(Testcase):
	"""A group iterates what it holds in the order it was queued."""

	def test_JobsAreOrderedByQueueTime(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Third", 300, 310, 400), _job("First", 60, 70, 100), _job("Second", 120, 130, 200)
		])

		self.assertEqual(["First", "Second", "Third"], [str(job) for job in pipeline])

	def test_AGroupSortsBesideTheJobs(self) -> None:
		"""A called workflow takes the place its first job was queued at, not a place after every job."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Late", 300, 310, 400), _job("Caller / Early", 60, 70, 100)
		])

		self.assertEqual(["Caller", "Late"], [str(element) for element in pipeline])

	def test_AnElementWithoutATimeSortsLast(self) -> None:
		"""It also keeps the order GitHub listed them in, because the sort is stable."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Unknown A", 0, None, None, created_at=None), _job("Timed", 120, 130, 200),
			_job("Unknown B", 0, None, None, created_at=None)
		])

		self.assertEqual(["Timed", "Unknown A", "Unknown B"], [str(job) for job in pipeline])


class Groups(Testcase):
	"""A push starts one run per matching workflow, so a commit has several pipelines."""

	@staticmethod
	def _Runs(*conclusions: str) -> dict[str, Any]:
		runs = []
		for position, conclusion in enumerate(conclusions):
			runs.append(_run(
				id=position, name=f"Workflow {position}", conclusion=conclusion, head_sha="41364cfc",
				status="completed" if conclusion is not None else "in_progress",
				updated_at=_time(300 + 60 * position)
			))

		return {"total_count": len(runs), "workflow_runs": runs}

	def test_EveryRunOfACommit(self) -> None:
		group = PipelineGroup.FromJSON(self._Runs("success", "failure", "success"))

		self.assertEqual("41364cfc", group.SHA)
		self.assertEqual(3, len(group))
		self.assertEqual(["Workflow 0", "Workflow 1", "Workflow 2"], [pipeline.Name for pipeline in group])
		self.assertIs(group, group.Pipelines[0].Parent)

	def test_AcceptsTheWorkflowRunsArrayDirectly(self) -> None:
		group = PipelineGroup.FromJSON(self._Runs("success")["workflow_runs"])

		self.assertEqual(1, len(group))

	def test_OneFailureMakesTheCommitFail(self) -> None:
		self.assertIs(Conclusion.Failure, PipelineGroup.FromJSON(self._Runs("success", "failure")).Conclusion)
		self.assertIs(Conclusion.Success, PipelineGroup.FromJSON(self._Runs("success", "success")).Conclusion)
		self.assertIs(Conclusion.Cancelled, PipelineGroup.FromJSON(self._Runs("cancelled", "success")).Conclusion)
		self.assertIs(Conclusion.Failure, PipelineGroup.FromJSON(self._Runs("cancelled", "failure")).Conclusion)

	def test_ARunningPipelineLeavesTheVerdictOpen(self) -> None:
		group = PipelineGroup.FromJSON(self._Runs("success", None))

		self.assertIsNone(group.Conclusion)
		self.assertIsNone(group.CompletedAt)

	def test_SpansItsPipelines(self) -> None:
		group = PipelineGroup.FromJSON(self._Runs("success", "success", "success"))

		self.assertEqual(datetime(2026, 9, 17, 10, 0, 10, tzinfo=timezone.utc), group.StartedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 7, 0, tzinfo=timezone.utc), group.CompletedAt)

	def test_IterateJobsReachesEveryPipelinesJobs(self) -> None:
		runs = self._Runs("success", "success")["workflow_runs"]
		jobs = {
			0: [_job("Prepare", 10, 20, 60)],
			1: [_job("Unit Tests (a)", 60, 70, 300), _job("Docs / Sphinx", 60, 70, 180)],
		}
		group = PipelineGroup.FromJSON(runs, jobs)

		self.assertEqual({"Prepare", "Unit Tests", "Sphinx"}, {job.Name for job in group.IterateJobs()})

	def test_DifferentCommitsAreRefused(self) -> None:
		runs = self._Runs("success", "success")["workflow_runs"]
		runs[1]["head_sha"] = "deadbeef"

		with self.assertRaises(GitHubError) as context:
			_ = PipelineGroup.FromJSON(runs)

		self.assertEqual("The runs report different commits.", str(context.exception))

	def test_NoCommitReported(self) -> None:
		runs = self._Runs("success")["workflow_runs"]
		del runs[0]["head_sha"]

		with self.assertRaises(GitHubError) as context:
			_ = PipelineGroup.FromJSON(runs)

		self.assertEqual(
			"None of the runs reports a 'head_sha', and parameter 'sha' wasn't given.",
			str(context.exception)
		)

	def test_CommitGivenExplicitly(self) -> None:
		runs = self._Runs("success")["workflow_runs"]
		del runs[0]["head_sha"]

		self.assertEqual("abcdef", PipelineGroup.FromJSON(runs, sha="abcdef").SHA)

	def test_ARunAtATagSharesTheCommit(self) -> None:
		"""A release pipeline tags its own commit; the run at that tag publishes the release."""
		runs = [
			_run(id=1, name="Pipeline", event="push", head_branch="main", head_sha="2c36ead7",
			     run_started_at=_time(10), updated_at=_time(600)),
			_run(id=2, name="Pipeline", event="workflow_dispatch", head_branch="v1.6.0", head_sha="2c36ead7",
			     run_started_at=_time(960), updated_at=_time(1200)),
		]
		group = PipelineGroup.FromJSON(runs)

		self.assertEqual(2, len(group))

		byRef = group.ByGitReference()
		self.assertEqual({"main", "v1.6.0"}, set(byRef))
		self.assertIs(Event.Push, byRef["main"][0].Event)
		self.assertIs(Event.WorkflowDispatch, byRef["v1.6.0"][0].Event)

	def test_HeadBranchOfATagRunIsTheTag(self) -> None:
		pipeline = Pipeline.FromJSON(_run(event="workflow_dispatch", head_branch="v1.6.0"))

		self.assertEqual("v1.6.0", pipeline.GitReference)

	def test_CalledWorkflowsNestToGitHubsLimit(self) -> None:
		"""GitHub allows four levels of nested reusable workflows, and a job's name carries the whole caller chain."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / C / D / Deep", 60, 120, 240),
			_job("A / B / Other", 60, 120, 180),
		])

		a = pipeline.Workflows["A"]
		b = a.Workflows["B"]
		c = b.Workflows["C"]
		d = c.Workflows["D"]
		self.assertEqual(["A", "B", "C", "D"], [group.Name for group in (a, b, c, d)])

		deep = d.Jobs[0]
		self.assertEqual("Deep", deep.Name)
		self.assertIs(pipeline, deep.Pipeline)

		chain, node = [], deep
		while node is not None:
			chain.append(node.Name)
			node = node.Parent
		self.assertEqual(["Deep", "D", "C", "B", "A", "Pipeline"], chain)

	def test_NestedLevelsAreSharedNotDuplicated(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / C / Deep", 60, 120, 240),
			_job("A / B / Other", 60, 120, 180),
		])

		a = pipeline.Workflows["A"]
		b = a.Workflows["B"]

		self.assertEqual(1, len(a.Workflows))
		self.assertEqual(["Other"], [job.Name for job in b.Jobs])
		self.assertEqual(["C"], list(b.Workflows))

	def test_AMatrixNestedInACalledWorkflow(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / C / Matrixed (x, 1)", 60, 300, 420),
			_job("A / B / C / Matrixed (y, 2)", 60, 300, 540),
		])

		c = pipeline.Workflows["A"].Workflows["B"].Workflows["C"]
		matrix = c.Matrices["Matrixed"]

		self.assertEqual("Matrixed", matrix.Name)
		self.assertEqual(2, len(matrix.Instances))
		self.assertEqual([["x", "1"], ["y", "2"]], [instance.DimensionValues for instance in matrix.Instances])

	def test_OuterLevelsSpanEveryJobBelowThem(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / C / D / Deep", 60, 120, 240),
			_job("A / B / C / Matrixed (y)", 60, 300, 540),
		])

		a = pipeline.Workflows["A"]
		d = a.Workflows["B"].Workflows["C"].Workflows["D"]

		self.assertEqual(datetime(2026, 9, 17, 10, 2, 0, tzinfo=timezone.utc), a.StartedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 9, 0, tzinfo=timezone.utc), a.CompletedAt)
		self.assertEqual(datetime(2026, 9, 17, 10, 4, 0, tzinfo=timezone.utc), d.CompletedAt)


class QualifiedNames(Testcase):
	"""A name taken apart by 'FromJSON' is put back together the way GitHub reported it."""

	def test_AJobOutsideAnyWorkflow(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 60, 120, 240)])

		self.assertEqual("Build", pipeline.Jobs[0].QualifiedName)

	def test_ACalledWorkflowPrefixesItsJobs(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("A / B / C / Deep", 60, 120, 240)])

		deep = pipeline.Workflows["A"].Workflows["B"].Workflows["C"].Jobs[0]
		self.assertEqual("Deep", deep.Name)
		self.assertEqual("A / B / C / Deep", deep.QualifiedName)

	def test_AMatrixIsNotNamedTwice(self) -> None:
		"""A matrix shares its name with the instances it produced, so the walk passes through it."""
		pipeline = Pipeline.FromJSON(_run(), [_job("A / Matrixed (x, 1)", 60, 300, 420)])

		instance = pipeline.Workflows["A"].Matrices["Matrixed"].Instances[0]
		self.assertEqual("Matrixed", instance.Name)
		self.assertEqual("A / Matrixed (x, 1)", instance.QualifiedName)

	def test_AWorkflowNamesItsCallers(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [_job("A / B / C / Deep", 60, 120, 240)])

		a = pipeline.Workflows["A"]
		self.assertEqual("A", a.QualifiedName)
		self.assertEqual("A / B", a.Workflows["B"].QualifiedName)
		self.assertEqual("A / B / C", a.Workflows["B"].Workflows["C"].QualifiedName)

	def test_TheRunIsNotACallingWorkflow(self) -> None:
		"""A 'Pipeline' is a run rather than a called workflow, so its name prefixes nothing."""
		pipeline = Pipeline.FromJSON(_run(name="Caller"), [_job("A / Deep", 60, 120, 240)])

		self.assertEqual("Caller", pipeline.QualifiedName)
		self.assertEqual("A / Deep", pipeline.Workflows["A"].Jobs[0].QualifiedName)

	def test_OnlyAJobAndAWorkflowAreNamedThatWay(self) -> None:
		"""GitHub reports no name for a matrix, and a step's name carries no prefix."""
		self.assertTrue(issubclass(Job, QualifiedNameMixin))
		self.assertTrue(issubclass(Workflow, QualifiedNameMixin))
		self.assertFalse(issubclass(Matrix, QualifiedNameMixin))
		self.assertFalse(issubclass(Step, QualifiedNameMixin))

	def test_TheMixinExpectsTheFieldItWalks(self) -> None:
		self.assertEqual({"_parent"}, set(QualifiedNameMixin.__expectedMembers__))
		for cls in (Job, MatrixJob, Workflow, Pipeline):
			with self.subTest(cls=cls.__name__):
				self.assertEqual(tuple(), cls.__missingMembers__)

	def test_AHostWithoutThatFieldIsRejected(self) -> None:
		class Rootless(metaclass=ExtendedType, slots=True):
			pass

		class Unrooted(Rootless, QualifiedNameMixin):
			pass

		self.assertEqual(("_parent",), Unrooted.__missingMembers__)
		with self.assertRaises(UnfulfilledExpectationError):
			_ = Unrooted()


class ContainedElements(Testcase):
	"""A workflow contains jobs, matrices and further workflows, so it iterates all three."""

	def test_AWorkflowIteratesEveryElementBelowIt(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / Plain", 60, 120, 240),
			_job("A / Matrixed (x)", 60, 300, 420),
			_job("A / B / Deep", 60, 120, 180),
		])

		a = pipeline.Workflows["A"]
		self.assertEqual(3, len(a))
		self.assertListEqual(["Plain", "Matrixed", "B"], [str(element) for element in a])
		self.assertListEqual([Job, Matrix, Workflow], [type(element) for element in a])

	def test_AWorkflowContainsWhatItIterates(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / Plain", 60, 120, 240),
			_job("A / Matrixed (x)", 60, 300, 420),
			_job("A / B / Deep", 60, 120, 180),
		])

		a = pipeline.Workflows["A"]
		for element in a:
			with self.subTest(element=str(element)):
				self.assertIn(str(element), a)

		# a job one level further down belongs to 'B', not to 'A'
		self.assertNotIn("Deep", a)
		self.assertIn("A", pipeline)

	def test_ContainmentTakesAName(self) -> None:
		"""An element is placed in its group under its own name, so containment is asked for that name."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / Deep", 60, 120, 240),
			_job("A / Plain", 60, 120, 180),
			_job("Top", 60, 120, 190),
		])

		a = pipeline.Workflows["A"]
		self.assertIn("B", a)        # a called workflow
		self.assertIn("Plain", a)    # a job
		self.assertNotIn("Top", a)   # a job of the run, not of this workflow
		self.assertNotIn("Deep", a)  # a job of the workflow below

		self.assertIn("Top", pipeline)
		self.assertIn("A", pipeline)

	def test_MatrixInstancesAreAskedForWithTheirValues(self) -> None:
		"""Every instance of a matrix shares the matrix' name, so a job is named by 'str' rather than 'Name'."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Matrixed (x)", 60, 300, 420),
			_job("Matrixed (y)", 60, 300, 540),
		])

		matrix = pipeline.Matrices["Matrixed"]
		self.assertEqual(["Matrixed", "Matrixed"], [instance.Name for instance in matrix.Instances])
		self.assertIn("Matrixed (x)", matrix)
		self.assertNotIn("Matrixed (z)", matrix)
		self.assertNotIn("Matrixed", matrix)  # that is the matrix' own name, not one of its instances'

		self.assertIn("Matrixed", pipeline)   # the matrix, one level up

	def test_AJobIsAskedForItsSteps(self) -> None:
		steps = [
			{"name": "Checkout", "number": 1, "status": "completed", "conclusion": "success",
			 "started_at": _time(120), "completed_at": _time(130)},
		]
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 60, 120, 240, steps=steps)])

		self.assertIn("Checkout", pipeline.Jobs[0])
		self.assertNotIn("Upload", pipeline.Jobs[0])

	def test_IdentityIsAnsweredByTheParent(self) -> None:
		"""Containment asks the name; which container an element really sits in is 'Parent'."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / B / Deep", 60, 120, 240),
			_job("C / B / Deep", 60, 120, 200),
		])

		a = pipeline.Workflows["A"]
		c = pipeline.Workflows["C"]

		self.assertIsNot(a.Workflows["B"], c.Workflows["B"])
		self.assertIs(a, a.Workflows["B"].Parent)
		self.assertIsNot(a, c.Workflows["B"].Parent)

	def test_AMatrixIteratesItsInstances(self) -> None:
		pipeline = Pipeline.FromJSON(_run(), [
			_job("Matrixed (x)", 60, 300, 420),
			_job("Matrixed (y)", 60, 300, 540),
		])

		matrix = pipeline.Matrices["Matrixed"]
		self.assertEqual(2, len(matrix))
		self.assertListEqual(["Matrixed (x)", "Matrixed (y)"], [str(instance) for instance in matrix])

	def test_IterateJobsStillReachesEveryJob(self) -> None:
		"""Iterating a workflow is one level deep; 'IterateJobs' is the whole subtree."""
		pipeline = Pipeline.FromJSON(_run(), [
			_job("A / Plain", 60, 120, 240),
			_job("A / Matrixed (x)", 60, 300, 420),
			_job("A / B / Deep", 60, 120, 180),
		])

		a = pipeline.Workflows["A"]
		self.assertEqual(3, len(a))
		self.assertListEqual(["Plain", "Matrixed", "Deep"], [job.Name for job in a.IterateJobs()])


class ParameterChecks(Testcase):
	"""Every constructor rejects a wrong type, and reports what it was given."""

	def test_TimestampType(self) -> None:
		for parameterName in ("createdAt", "startedAt", "completedAt"):
			with self.subTest(parameter=parameterName):
				with self.assertRaises(TypeError) as context:
					_ = Job("Build", **{parameterName: "2026-09-17T10:00:00Z"})

				self.assertEqual(f"Parameter '{parameterName}' is not of type 'datetime'.", str(context.exception))
				self.assertIn("Got type 'str'.", context.exception.__notes__)

	def test_URLType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", url="https://github.com")

		self.assertEqual("Parameter 'url' is not of type 'URL'.", str(context.exception))

	def test_ParentType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", parent="pipeline")

		self.assertEqual("Parameter 'parent' is not of type 'JobGroup'.", str(context.exception))

	def test_IdentifierType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", identifier="4711")

		self.assertEqual("Parameter 'identifier' is not of type 'int'.", str(context.exception))

	def test_LabelsElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", labels=["ubuntu-26.04", 42])

		self.assertEqual("An element of parameter 'labels' is not of type 'str'.", str(context.exception))
		self.assertIn("Got type 'int'.", context.exception.__notes__)

	def test_RunnerNameType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", runnerName=42)

		self.assertEqual("Parameter 'runnerName' is not of type 'str'.", str(context.exception))

	def test_StepNumberNotPositive(self) -> None:
		for value in (0, -1):
			with self.subTest(number=value):
				with self.assertRaises(ValueError) as context:
					_ = Step("Compile", number=value)

				self.assertEqual("Parameter 'number' is not positive.", str(context.exception))
				self.assertIn(f"Got value '{value}'.", context.exception.__notes__)

	def test_StepNumberType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Step("Compile", number="1")

		self.assertEqual("Parameter 'number' is not of type 'int'.", str(context.exception))

	def test_StepParentType(self) -> None:
		for value in ("job", Workflow("Called"), Pipeline("Pipeline")):
			with self.subTest(parent=type(value).__name__):
				with self.assertRaises(TypeError) as context:
					_ = Step("Compile", parent=value)

				self.assertEqual("Parameter 'parent' is not of type 'Job'.", str(context.exception))

	def test_TheBaseClassesAreAbstract(self) -> None:
		for cls in (Base, JobGroup):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(AbstractClassError):
					_ = cls("x")

	def test_AnElementWithoutAParentRejectsOne(self) -> None:
		self.assertIsNone(PipelineGroup._PARENT_TYPE)

	def test_EachClassDeclaresItsParentType(self) -> None:
		"""One check in 'Base' reports the type the class itself expects."""
		self.assertIs(Job, Step._PARENT_TYPE)
		self.assertIs(JobGroup, Job._PARENT_TYPE)
		self.assertIs(Matrix, MatrixJob._PARENT_TYPE)
		self.assertIs(Workflow, Workflow._PARENT_TYPE)
		self.assertIs(PipelineGroup, Pipeline._PARENT_TYPE)

	def test_AParentOfTheDeclaredTypeIsAccepted(self) -> None:
		job =      Job("Build")
		workflow = Workflow("Called")

		self.assertIs(job, Step("Compile", parent=job).Parent)
		self.assertIs(workflow, Workflow("Inner", parent=workflow).Parent)
		self.assertIs(workflow, Matrix("Unit Tests", parent=workflow).Parent)

	def test_PayloadType(self) -> None:
		for cls in (Step, Job, MatrixJob, Pipeline):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(TypeError) as context:
					_ = cls.FromJSON("payload")

				self.assertIn("is not of type 'dict'.", str(context.exception))

	def test_WorkflowParentType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Workflow("Called", parent="pipeline")

		self.assertEqual("Parameter 'parent' is not of type 'Workflow'.", str(context.exception))

	def test_PipelineEventType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline", event="push")

		self.assertEqual("Parameter 'event' is not of type 'Event'.", str(context.exception))

	def test_PipelineNumberTypes(self) -> None:
		for parameterName in ("identifier", "runNumber", "runAttempt"):
			with self.subTest(parameter=parameterName):
				with self.assertRaises(TypeError) as context:
					_ = Pipeline("Pipeline", **{parameterName: "1"})

				self.assertEqual(f"Parameter '{parameterName}' is not of type 'int'.", str(context.exception))

	def test_PipelineReferenceTypes(self) -> None:
		for parameterName in ("gitReference", "sha"):
			with self.subTest(parameter=parameterName):
				with self.assertRaises(TypeError) as context:
					_ = Pipeline("Pipeline", **{parameterName: 42})

				self.assertEqual(f"Parameter '{parameterName}' is not of type 'str'.", str(context.exception))

	def test_PipelineParentType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline", parent="group")

		self.assertEqual("Parameter 'parent' is not of type 'PipelineGroup'.", str(context.exception))

	def test_PipelineGroupElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PipelineGroup("41364cfc", ["pipeline"])

		self.assertEqual("An element of parameter 'pipelines' is not of type 'Pipeline'.", str(context.exception))

	def test_MatrixJobDimensionValuesElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = MatrixJob("Unit Tests", ["ubuntu-26.04", 314])

		self.assertEqual("An element of parameter 'dimensionValues' is not of type 'str'.", str(context.exception))

	def test_UnknownEvent(self) -> None:
		with self.assertRaises(GitHubError) as context:
			_ = Event.Parse("teleported")

		self.assertEqual("'teleported' is not a GitHub event.", str(context.exception))


class WorkflowFile(Testcase):
	def test_PathAndWorkflowID(self) -> None:
		pipeline = Pipeline.FromJSON(_run(workflow_id=130786985, path=".github/workflows/Pipeline.yml"))

		self.assertEqual(130786985, pipeline.WorkflowID)
		self.assertEqual(".github/workflows/Pipeline.yml", pipeline.Path)

	def test_WorkflowIDType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline", workflowID="130786985")

		self.assertEqual("Parameter 'workflowID' is not of type 'int'.", str(context.exception))

	def test_PathType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline", path=42)

		self.assertEqual("Parameter 'path' is not of type 'str'.", str(context.exception))

	def test_NameIsNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Job(None)

		self.assertEqual("Parameter 'name' is None.", str(context.exception))


class BottomUpConstruction(Testcase):
	"""A job is given its steps, rather than each step attaching itself afterwards."""

	def test_StepsPassedToTheJob(self) -> None:
		steps = [Step("Set up job", 1), Step("Compile", 2)]
		job =   Job("Build", steps=steps)

		self.assertEqual(steps, job.Steps)
		self.assertEqual(2, len(job))
		for step in steps:
			self.assertIs(job, step.Parent)

	def test_StepsElementType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Job("Build", steps=[Step("Set up job", 1), "Compile"])

		self.assertEqual("An element of parameter 'steps' is not of type 'Step'.", str(context.exception))

	def test_APassedStepKnowsThePipeline(self) -> None:
		pipeline = Pipeline("Pipeline")
		job =      Job("Build", steps=[Step("Compile", 1)], parent=pipeline)

		self.assertIs(pipeline, job.Steps[0].Pipeline)

	def test_MatrixJobTakesStepsToo(self) -> None:
		instance = MatrixJob("Unit Tests", ["ubuntu-26.04"], steps=[Step("Compile", 1)])

		self.assertEqual(1, len(instance))
		self.assertIs(instance, instance.Steps[0].Parent)

	def test_FromJSONStillAttachesThem(self) -> None:
		steps = [
			{"name": "Set up job", "number": 1, "status": "completed", "conclusion": "success",
			 "started_at": _time(21), "completed_at": _time(25)},
		]
		pipeline = Pipeline.FromJSON(_run(), [_job("Build", 10, 20, 80, steps=steps)])
		job =      pipeline.Jobs[0]

		self.assertEqual(["Set up job"], [step.Name for step in job])
		self.assertIs(job, job.Steps[0].Parent)
		self.assertIs(pipeline, job.Steps[0].Pipeline)
