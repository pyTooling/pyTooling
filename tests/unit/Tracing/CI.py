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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Unit tests for :mod:`pyTooling.Tracing.CI`: the attribute keys, the span kinds and results, and the timespans of a
pipeline run.
"""
from datetime              import datetime, timezone

from pyTooling.MetaClasses import AbstractClassError
from pyTooling.Tracing.CI  import CI, OTLP, SpanKind, Result, PipelineTrace, TaskSpan, WorkflowSpan, MatrixSpan, \
                                  QueuedSpan, JobSpan, StepSpan
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


BEGIN = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
END =   datetime(2026, 10, 25, 12, 5, 0, tzinfo=timezone.utc)


class AttributeKeys(Testcase):
	"""The nesting of :class:`OTLP` and :class:`CI` spells the key: one level per dot."""

	def test_Pipeline(self) -> None:
		self.assertEqual("cicd.pipeline.name", OTLP.CICD.Pipeline.Name)
		self.assertEqual("cicd.pipeline.result", OTLP.CICD.Pipeline.Result)
		self.assertEqual("cicd.pipeline.run.id", OTLP.CICD.Pipeline.Run.ID)
		self.assertEqual("cicd.pipeline.run.url.full", OTLP.CICD.Pipeline.Run.URL.Full)

	def test_Task(self) -> None:
		self.assertEqual("cicd.pipeline.task.name", OTLP.CICD.Pipeline.Task.Name)
		self.assertEqual("cicd.pipeline.task.run.id", OTLP.CICD.Pipeline.Task.Run.ID)
		self.assertEqual("cicd.pipeline.task.run.result", OTLP.CICD.Pipeline.Task.Run.Result)
		self.assertEqual("cicd.pipeline.task.run.url.full", OTLP.CICD.Pipeline.Task.Run.URL.Full)

	def test_Worker(self) -> None:
		self.assertEqual("cicd.worker.name", OTLP.CICD.Worker.Name)

	def test_VCS(self) -> None:
		self.assertEqual("vcs.ref.head.name", OTLP.VCS.Ref.Head.Name)
		self.assertEqual("vcs.ref.head.revision", OTLP.VCS.Ref.Head.Revision)

	def test_CI(self) -> None:
		self.assertEqual("ci.span.kind", CI.Span.Kind)


class Enumerations(Testcase):
	def test_SpanKind(self) -> None:
		self.assertListEqual(
			["pipeline", "workflow", "matrix", "queued", "job", "step"],
			[member.value for member in SpanKind]
		)

	def test_Result(self) -> None:
		"""The values are the ones OpenTelemetry's conventions allow."""
		self.assertListEqual(
			["success", "failure", "timeout", "skip", "cancellation", "error"],
			[member.value for member in Result]
		)

	def test_Result_Parse(self) -> None:
		self.assertIs(Result.Cancellation, Result.Parse("cancellation"))


class PipelineTraces(Testcase):
	def test_Minimal(self) -> None:
		trace = PipelineTrace("Pipeline")

		self.assertEqual("Pipeline", trace.Name)
		self.assertIs(SpanKind.Pipeline, trace.KIND)
		self.assertIs(SpanKind.Pipeline, trace[CI.Span.Kind])
		self.assertEqual("Pipeline", trace[OTLP.CICD.Pipeline.Name])
		self.assertNotIn(OTLP.CICD.Pipeline.Run.ID, trace)
		self.assertNotIn(OTLP.CICD.Pipeline.Result, trace)

	def test_Times(self) -> None:
		trace = PipelineTrace("Pipeline", BEGIN, END)

		self.assertEqual(BEGIN, trace.StartTime)
		self.assertEqual(END, trace.StopTime)

	def test_PipelineName(self) -> None:
		"""A pipeline name differing from the trace's name goes into the attribute; the trace keeps its own."""
		trace = PipelineTrace("Run 4711", pipelineName="Pipeline")

		self.assertEqual("Run 4711", trace.Name)
		self.assertEqual("Pipeline", trace[OTLP.CICD.Pipeline.Name])

	def test_Attributes(self) -> None:
		trace = PipelineTrace(
			"Pipeline",
			runID="4711",
			runURL="https://github.com/pyTooling/pyTooling/actions/runs/4711",
			result=Result.Success,
			reference="dev",
			revision="0123456789abcdef"
		)

		self.assertEqual("4711", trace[OTLP.CICD.Pipeline.Run.ID])
		self.assertEqual("https://github.com/pyTooling/pyTooling/actions/runs/4711", trace[OTLP.CICD.Pipeline.Run.URL.Full])
		self.assertIs(Result.Success, trace[OTLP.CICD.Pipeline.Result])
		self.assertEqual("dev", trace[OTLP.VCS.Ref.Head.Name])
		self.assertEqual("0123456789abcdef", trace[OTLP.VCS.Ref.Head.Revision])

	def test_FurtherAttributes(self) -> None:
		trace = PipelineTrace("Pipeline", attributes={"github.event": "push"})

		self.assertEqual("push", trace["github.event"])

	def test_UnknownValuesAreSkipped(self) -> None:
		"""``None``, an empty string and an empty list name no value; the key stays absent."""
		trace = PipelineTrace("Pipeline", reference="", attributes={"a": None, "b": "", "c": [], "d": "value"})

		self.assertNotIn(OTLP.VCS.Ref.Head.Name, trace)
		self.assertNotIn("a", trace)
		self.assertNotIn("b", trace)
		self.assertNotIn("c", trace)
		self.assertEqual("value", trace["d"])


class TaskSpans(Testcase):
	def test_Abstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = TaskSpan("Task")

	def test_Workflow(self) -> None:
		trace = PipelineTrace("Pipeline")
		span =  WorkflowSpan("Workflow", parent=trace)

		self.assertIs(trace, span.Parent)
		self.assertIs(SpanKind.Workflow, span[CI.Span.Kind])
		self.assertEqual("Workflow", span[OTLP.CICD.Pipeline.Task.Name])

	def test_Matrix(self) -> None:
		trace = PipelineTrace("Pipeline")
		span =  MatrixSpan("Matrix", parent=trace)

		self.assertIs(trace, span.Parent)
		self.assertIs(SpanKind.Matrix, span[CI.Span.Kind])
		self.assertEqual("Matrix", span[OTLP.CICD.Pipeline.Task.Name])

	def test_Queued(self) -> None:
		trace = PipelineTrace("Pipeline")
		span =  QueuedSpan("Queued", parent=trace)

		self.assertIs(trace, span.Parent)
		self.assertIs(SpanKind.Queued, span[CI.Span.Kind])
		self.assertEqual("Queued", span[OTLP.CICD.Pipeline.Task.Name])

	def test_TaskName(self) -> None:
		"""The name the service reports goes into the attribute; the timespan keeps the name of its place in the tree."""
		span = WorkflowSpan("Package", taskName="Package / Package")

		self.assertEqual("Package", span.Name)
		self.assertEqual("Package / Package", span[OTLP.CICD.Pipeline.Task.Name])

	def test_FurtherAttributes(self) -> None:
		span = MatrixSpan("Matrix", attributes={"matrix.size": 12, "matrix.empty": None})

		self.assertEqual(12, span["matrix.size"])
		self.assertNotIn("matrix.empty", span)


class JobSpans(Testcase):
	def test_Minimal(self) -> None:
		job = JobSpan("Job", BEGIN, END)

		self.assertEqual(BEGIN, job.StartTime)
		self.assertEqual(END, job.StopTime)
		self.assertIs(SpanKind.Job, job[CI.Span.Kind])
		self.assertEqual("Job", job[OTLP.CICD.Pipeline.Task.Name])
		self.assertNotIn(OTLP.CICD.Pipeline.Task.Run.ID, job)
		self.assertNotIn(OTLP.CICD.Pipeline.Task.Run.Result, job)
		self.assertNotIn(OTLP.CICD.Worker.Name, job)

	def test_Attributes(self) -> None:
		jobURL = "https://github.com/pyTooling/pyTooling/actions/runs/4711/job/815"
		trace =  PipelineTrace("Pipeline")
		job =    JobSpan(
			"Job",
			parent=trace,
			taskName="UnitTesting / Job",
			runID="815",
			runURL=jobURL,
			result=Result.Failure,
			workerName="GitHub Actions 42",
			attributes={"github.runner.labels": ["ubuntu-24.04"]}
		)

		self.assertIs(trace, job.Parent)
		self.assertEqual("UnitTesting / Job", job[OTLP.CICD.Pipeline.Task.Name])
		self.assertEqual("815", job[OTLP.CICD.Pipeline.Task.Run.ID])
		self.assertEqual(jobURL, job[OTLP.CICD.Pipeline.Task.Run.URL.Full])
		self.assertIs(Result.Failure, job[OTLP.CICD.Pipeline.Task.Run.Result])
		self.assertEqual("GitHub Actions 42", job[OTLP.CICD.Worker.Name])
		self.assertListEqual(["ubuntu-24.04"], job["github.runner.labels"])


class StepSpans(Testcase):
	def test_Minimal(self) -> None:
		step = StepSpan("Step")

		self.assertIs(SpanKind.Step, step[CI.Span.Kind])
		self.assertEqual("Step", step[OTLP.CICD.Pipeline.Task.Name])
		self.assertNotIn(OTLP.CICD.Pipeline.Task.Run.Result, step)

	def test_Attributes(self) -> None:
		job =  JobSpan("Job")
		step = StepSpan("Step", parent=job, taskName="Run tests", result=Result.Skip, attributes={"github.step.number": 3})

		self.assertIs(job, step.Parent)
		self.assertEqual("Run tests", step[OTLP.CICD.Pipeline.Task.Name])
		self.assertIs(Result.Skip, step[OTLP.CICD.Pipeline.Task.Run.Result])
		self.assertEqual(3, step["github.step.number"])
