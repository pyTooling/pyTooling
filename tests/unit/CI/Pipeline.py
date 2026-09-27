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
Unit tests for :mod:`pyTooling.CI.Pipeline`.
"""
from datetime              import datetime, timedelta, timezone

from pyTooling.CI.Pipeline import Base, PipelineGroup, Pipeline, Workflow, Matrix, MatrixJob, MatrixWorkflow, Job
from pyTooling.CI.Pipeline import JobGroup, Step
from pyTooling.CI.Pipeline import Outcome, PipelineError, NeedDependencyError, NeedDependencyCycleError
from pyTooling.CI.Pipeline import ConditionMixin, DependencyMixin, MatrixInstanceMixin, QualifiedNameMixin
from pyTooling.Graph       import BaseGraph, Graph, Subgraph, Vertex
from pyTooling.MetaClasses import AbstractClassError, ExtendedType, UnfulfilledExpectationError
from pyTooling.Tracing.CI  import Result
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


_ORIGIN = datetime(2026, 9, 27, 10, 0, 0, tzinfo=timezone.utc)


def _time(seconds: int) -> datetime:
	"""
	Return a time the given number of seconds after the pipeline was created.

	:param seconds: Seconds after 2026-09-27T10:00:00Z.
	:returns:       The time.
	"""
	return _ORIGIN + timedelta(seconds=seconds)


class Instantiation(Testcase):
	def test_Base(self) -> None:
		for cls in (Base, JobGroup):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(AbstractClassError):
					_ = cls("x")

	def test_PipelineGroup(self) -> None:
		pipeline = Pipeline("Pipeline")
		group = PipelineGroup("0123abcd", [pipeline])

		self.assertEqual("0123abcd", group.Name)
		self.assertIsNone(group.Parent)
		self.assertIsNone(group.Pipeline)
		self.assertListEqual([pipeline], group.Pipelines)
		self.assertIs(group, pipeline.Parent)
		self.assertEqual(1, len(group))
		self.assertIn("Pipeline", group)
		self.assertListEqual([pipeline], list(group))

	def test_PipelineGroup_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PipelineGroup("0123abcd", [Job("Build")])

		self.assertEqual("An element of parameter 'pipelines' is not of type 'Pipeline'.", str(context.exception))

	def test_Pipeline(self) -> None:
		group = PipelineGroup("0123abcd")
		pipeline = Pipeline(
			"Pipeline", condition="$CI_COMMIT_BRANCH == 'main'", createdAt=_time(0), startedAt=_time(10),
			completedAt=_time(600), outcome=Outcome.Success, parent=group
		)

		self.assertEqual("Pipeline", pipeline.Name)
		self.assertEqual("Pipeline", str(pipeline))
		self.assertEqual("Pipeline", pipeline.QualifiedName)
		self.assertEqual("$CI_COMMIT_BRANCH == 'main'", pipeline.Condition)
		self.assertIs(group, pipeline.Parent)
		self.assertIs(pipeline, pipeline.Pipeline)
		self.assertListEqual([pipeline], group.Pipelines)
		self.assertEqual(_time(0), pipeline.CreatedAt)
		self.assertEqual(_time(10), pipeline.StartedAt)
		self.assertEqual(_time(600), pipeline.CompletedAt)
		self.assertEqual(590.0, pipeline.Duration)
		self.assertIs(Outcome.Success, pipeline.Outcome)
		self.assertIsNone(pipeline.Reference)
		self.assertEqual(0, len(pipeline))

	def test_Workflow(self) -> None:
		pipeline = Pipeline("Pipeline")
		workflow = Workflow("Package", reference="pyTooling/Actions/.github/workflows/Package.yml@r8", parent=pipeline)

		self.assertEqual("Package", workflow.Name)
		self.assertEqual("pyTooling/Actions/.github/workflows/Package.yml@r8", workflow.Reference)
		self.assertIs(pipeline, workflow.Parent)
		self.assertIs(pipeline, workflow.Pipeline)
		self.assertDictEqual({"Package": workflow}, pipeline.Workflows)
		self.assertListEqual([], workflow.Needs)
		self.assertListEqual([], workflow.Dependents)

	def test_Workflow_Duplicate(self) -> None:
		pipeline = Pipeline("Pipeline")
		Workflow("Package", parent=pipeline)

		with self.assertRaises(PipelineError) as context:
			_ = Workflow("Package", parent=pipeline)

		self.assertEqual("Workflow 'Pipeline' calls a workflow 'Package' already.", str(context.exception))

	def test_Workflow_ReferenceType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Workflow("Package", reference=42)

		self.assertEqual("Parameter 'reference' is not of type 'str'.", str(context.exception))

	def test_Matrix(self) -> None:
		pipeline = Pipeline("Pipeline")
		matrix = Matrix("Unit Tests", condition="inputs.unittest", parent=pipeline)
		instance = MatrixJob("Unit Tests", ["ubuntu-26.04", "3.14"], parent=matrix)

		self.assertEqual("inputs.unittest", matrix.Condition)
		self.assertDictEqual({"Unit Tests": matrix}, pipeline.Matrices)
		self.assertListEqual([instance], matrix.Instances)
		self.assertListEqual([instance], matrix.Jobs)
		self.assertEqual("Unit Tests (ubuntu-26.04, 3.14)", str(instance))
		self.assertListEqual(["ubuntu-26.04", "3.14"], instance.DimensionValues)
		self.assertIn("Unit Tests (ubuntu-26.04, 3.14)", matrix)
		self.assertIn("Unit Tests", pipeline)

	def test_Matrix_Duplicate(self) -> None:
		pipeline = Pipeline("Pipeline")
		Matrix("Unit Tests", parent=pipeline)

		with self.assertRaises(PipelineError) as context:
			_ = Matrix("Unit Tests", parent=pipeline)

		self.assertEqual("Workflow 'Pipeline' contains a matrix 'Unit Tests' already.", str(context.exception))

	def test_MatrixWorkflow(self) -> None:
		"""A matrix may produce instances of a called workflow."""
		pipeline = Pipeline("Pipeline")
		matrix = Matrix("Tests", parent=pipeline)
		instance = MatrixWorkflow("Tests", ["3.14"], reference="./.github/workflows/Tests.yml", parent=matrix)
		job = Job("Unit", parent=instance)

		self.assertListEqual([instance], matrix.Instances)
		self.assertListEqual([], matrix.Jobs)
		self.assertEqual("Tests (3.14)", str(instance))
		self.assertEqual("Tests (3.14)", instance.QualifiedName)
		self.assertEqual("Tests (3.14) / Unit", job.QualifiedName)
		self.assertListEqual([job], list(pipeline.IterateJobs()))
		self.assertIs(Matrix, MatrixWorkflow._PARENT_TYPE)
		self.assertTrue(issubclass(MatrixWorkflow, MatrixInstanceMixin))
		self.assertFalse(hasattr(instance, "__dict__"))

	def test_MatrixJob_NoValues(self) -> None:
		self.assertEqual("Build", str(MatrixJob("Build")))

	def test_MatrixJob_Mixin(self) -> None:
		"""The dimension values come from a mixin, which a service's job class can mix in as well."""
		self.assertTrue(issubclass(MatrixJob, MatrixInstanceMixin))
		self.assertFalse(issubclass(Job, MatrixInstanceMixin))
		self.assertFalse(hasattr(MatrixJob("Build", ["3.14"]), "__dict__"))

	def test_MatrixJob_ValueType(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = MatrixJob("Build", ["3.14", 3.13])

		self.assertEqual("An element of parameter 'dimensionValues' is not of type 'str'.", str(context.exception))

	def test_Job(self) -> None:
		pipeline = Pipeline("Pipeline")
		job = Job(
			"Build", condition="success()", createdAt=_time(60), startedAt=_time(70), completedAt=_time(130),
			outcome=Outcome.Failure, parent=pipeline
		)
		step = Step("Checkout", condition="always()", startedAt=_time(71), completedAt=_time(75), parent=job)

		self.assertListEqual([job], pipeline.Jobs)
		self.assertEqual("success()", job.Condition)
		self.assertEqual(60.0, job.Duration)
		self.assertIs(Outcome.Failure, job.Outcome)
		self.assertListEqual([step], job.Steps)
		self.assertIs(job, step.Parent)
		self.assertIs(pipeline, step.Pipeline)
		self.assertIsNone(step.CreatedAt)
		self.assertEqual("always()", step.Condition)
		self.assertEqual(1, len(job))
		self.assertIn("Checkout", job)
		self.assertListEqual([step], list(job))

	def test_Name(self) -> None:
		for name, exception, message in (
			(None, ValueError, "Parameter 'name' is None."),
			(42,   TypeError,  "Parameter 'name' is not of type 'str'."),
			("",   ValueError, "Parameter 'name' is empty."),
		):
			with self.subTest(name=name):
				with self.assertRaises(exception) as context:
					_ = Job(name)

				self.assertEqual(message, str(context.exception))

	def test_Facts_Type(self) -> None:
		for parameterName, value in (
			("condition", 42), ("createdAt", "10:00"), ("startedAt", 0), ("completedAt", 0.0), ("outcome", "success")
		):
			with self.subTest(parameter=parameterName):
				with self.assertRaises(TypeError) as context:
					_ = Job("Build", **{parameterName: value})

				self.assertIn(f"Parameter '{parameterName}' is not of type", str(context.exception))

	def test_Condition(self) -> None:
		"""Only an element a definition can give a condition has one."""
		for cls in (Workflow, Pipeline, Matrix, Job, MatrixJob, Step):
			with self.subTest(cls=cls.__name__):
				self.assertTrue(issubclass(cls, ConditionMixin))
				self.assertEqual("always()", cls("x", condition="always()").Condition)

		self.assertFalse(issubclass(PipelineGroup, ConditionMixin))
		self.assertFalse(hasattr(PipelineGroup("x"), "Condition"))

	def test_Condition_Type(self) -> None:
		for cls in (Workflow, Matrix, Job, Step):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(TypeError) as context:
					_ = cls("x", condition=42)

				self.assertEqual("Parameter 'condition' is not of type 'str'.", str(context.exception))

	def test_Parent_Type(self) -> None:
		pipeline = Pipeline("Pipeline")
		job = Job("Build", parent=pipeline)

		for cls, parent, message in (
			(Step,      pipeline,              "Parameter 'parent' is not of type 'Job'."),
			(Job,       job,                   "Parameter 'parent' is not of type 'JobGroup'."),
			(MatrixJob, pipeline,              "Parameter 'parent' is not of type 'Matrix'."),
			(Matrix,    job,                   "Parameter 'parent' is not of type 'Workflow'."),
			(Workflow,  job,                   "Parameter 'parent' is not of type 'Workflow'."),
			(Pipeline,  Pipeline("Other"),     "Parameter 'parent' is not of type 'PipelineGroup'."),
		):
			with self.subTest(cls=cls.__name__):
				with self.assertRaises(TypeError) as context:
					_ = cls("x", parent=parent)

				self.assertEqual(message, str(context.exception))

	def test_ParentTypes(self) -> None:
		self.assertIsNone(PipelineGroup._PARENT_TYPE)
		self.assertIs(PipelineGroup, Pipeline._PARENT_TYPE)
		self.assertIs(Workflow, Workflow._PARENT_TYPE)
		self.assertIs(Workflow, Matrix._PARENT_TYPE)
		self.assertIs(JobGroup, Job._PARENT_TYPE)
		self.assertIs(Matrix, MatrixJob._PARENT_TYPE)
		self.assertIs(Job, Step._PARENT_TYPE)


class Hierarchy(Testcase):
	def test_QualifiedName(self) -> None:
		pipeline = Pipeline("Pipeline")
		caller = Workflow("Caller", parent=pipeline)
		called = Workflow("Called", parent=caller)
		matrix = Matrix("Test", parent=called)
		instance = MatrixJob("Test", ["3.14"], parent=matrix)
		job = Job("Build", parent=pipeline)

		self.assertEqual("Build", job.QualifiedName)
		self.assertEqual("Caller", caller.QualifiedName)
		self.assertEqual("Caller / Called / Test", matrix.QualifiedName)
		self.assertEqual("Caller / Called / Test (3.14)", instance.QualifiedName)

	def test_IterateJobs(self) -> None:
		group = PipelineGroup("0123abcd")
		pipeline = Pipeline("Pipeline", parent=group)
		plain = Job("Plain", parent=pipeline)
		instance = MatrixJob("Test", ["3.14"], parent=Matrix("Test", parent=pipeline))
		deep = Job("Deep", parent=Workflow("Called", parent=pipeline))

		self.assertListEqual([plain, instance, deep], list(pipeline.IterateJobs()))
		self.assertListEqual([plain, instance, deep], list(group.IterateJobs()))

	def test_Contents(self) -> None:
		"""A group iterates its elements in the order they were added, whatever their kind."""
		pipeline = Pipeline("Pipeline")
		workflow = Workflow("Called", parent=pipeline)
		matrix = Matrix("Test", parent=pipeline)
		job = Job("Build", parent=pipeline)
		other = Job("Deploy", parent=pipeline)

		self.assertEqual(4, len(pipeline))
		self.assertListEqual([workflow, matrix, job, other], list(pipeline))
		self.assertListEqual([workflow, matrix, job, other], pipeline.Elements)
		self.assertListEqual([job, other], pipeline.Jobs)
		self.assertDictEqual({"Called": workflow}, pipeline.Workflows)
		self.assertDictEqual({"Test": matrix}, pipeline.Matrices)
		for name in ("Called", "Test", "Build"):
			with self.subTest(name=name):
				self.assertIn(name, pipeline)

		self.assertNotIn("Release", pipeline)

	def test_GetItem(self) -> None:
		"""An element is looked up by its name, as a reader resolving a definition's names does."""
		pipeline = Pipeline("Pipeline")
		workflow = Workflow("Called", parent=pipeline)
		matrix = Matrix("Test", parent=pipeline)
		instance = MatrixJob("Test", ["3.14"], parent=matrix)
		job = Job("Build", parent=pipeline)

		self.assertIs(workflow, pipeline["Called"])
		self.assertIs(matrix, pipeline["Test"])
		self.assertIs(job, pipeline["Build"])
		self.assertIs(instance, matrix["Test (3.14)"])

		with self.assertRaises(KeyError) as context:
			_ = pipeline["Release"]

		self.assertEqual("\"Group 'Pipeline' contains no element 'Release'.\"", str(context.exception))

	def test_Contents_ByCreation(self) -> None:
		"""A group iterates what it holds in the order it was created; unknown times keep their order at the end."""
		pipeline = Pipeline("Pipeline")
		late = Job("Late", createdAt=_time(90), parent=pipeline)
		early = Job("Early", createdAt=_time(30), parent=pipeline)
		unknown = Job("Unknown", parent=pipeline)
		matrix = MatrixJob("Test", ["x"], createdAt=_time(60), parent=Matrix("Test", parent=pipeline)).Parent

		self.assertListEqual([early, matrix, late, unknown], list(pipeline))


class Times(Testcase):
	def test_UnreportedGroup(self) -> None:
		"""A group the service doesn't report spans its contents."""
		pipeline = Pipeline("Pipeline", createdAt=_time(0), startedAt=_time(10), completedAt=_time(600))
		workflow = Workflow("Called", parent=pipeline)
		Job("A", createdAt=_time(60), startedAt=_time(70), completedAt=_time(200), parent=workflow)
		Job("B", createdAt=_time(50), startedAt=_time(80), completedAt=_time(300), parent=workflow)

		self.assertEqual(_time(50), workflow.CreatedAt)
		self.assertEqual(_time(70), workflow.StartedAt)
		self.assertEqual(_time(300), workflow.CompletedAt)
		self.assertEqual(230.0, workflow.Duration)

	def test_ReportedGroup(self) -> None:
		"""A pipeline, or a child pipeline a service reports, keeps its own times beside the span of its contents."""
		pipeline = Pipeline("Pipeline", createdAt=_time(0), startedAt=_time(10))
		Job("A", createdAt=_time(60), startedAt=_time(70), completedAt=_time(200), parent=pipeline)

		self.assertEqual(_time(0), pipeline.CreatedAt)
		self.assertEqual(_time(10), pipeline.StartedAt)
		self.assertIsNone(pipeline.CompletedAt, "A running pipeline hasn't completed, although its jobs have.")
		self.assertEqual(_time(60), pipeline.ContentsCreatedAt)
		self.assertEqual(_time(70), pipeline.ContentsStartedAt)
		self.assertEqual(_time(200), pipeline.ContentsCompletedAt)

	def test_ReportedGroup_OutcomeOnly(self) -> None:
		"""A group given only an outcome is reported, so it keeps that outcome and reports no times."""
		pipeline = Pipeline("Pipeline", outcome=Outcome.Cancellation)
		Job("A", createdAt=_time(60), startedAt=_time(70), completedAt=_time(200), outcome=Outcome.Success, parent=pipeline)

		self.assertIs(Outcome.Cancellation, pipeline.Outcome)
		self.assertIsNone(pipeline.CreatedAt)
		self.assertIs(Outcome.Success, pipeline.ContentsOutcome)

	def test_RunningElement(self) -> None:
		workflow = Workflow("Called")
		Job("Done", createdAt=_time(60), startedAt=_time(70), completedAt=_time(100), parent=workflow)
		Job("Running", createdAt=_time(60), startedAt=_time(70), parent=workflow)

		self.assertIsNone(workflow.CompletedAt)
		self.assertIsNone(workflow.Duration)

	def test_Empty(self) -> None:
		workflow = Workflow("Called")

		self.assertIsNone(workflow.CreatedAt)
		self.assertIsNone(workflow.StartedAt)
		self.assertIsNone(workflow.CompletedAt)
		self.assertIsNone(workflow.Outcome)

	def test_PipelineGroup(self) -> None:
		group = PipelineGroup("0123abcd")
		Pipeline("A", createdAt=_time(0), startedAt=_time(10), completedAt=_time(100), parent=group)
		Pipeline("B", createdAt=_time(5), startedAt=_time(8), completedAt=_time(200), parent=group)

		self.assertEqual(_time(0), group.CreatedAt)
		self.assertEqual(_time(8), group.StartedAt)
		self.assertEqual(_time(200), group.CompletedAt)
		self.assertEqual(192.0, group.Duration)


class Outcomes(Testcase):
	def test_Combine(self) -> None:
		for outcomes, expected in (
			((Outcome.Success, Outcome.Failure, Outcome.Cancellation), Outcome.Failure),
			((Outcome.Cancellation, Outcome.Timeout),                  Outcome.Timeout),
			((Outcome.Error, Outcome.Cancellation),                    Outcome.Error),
			((Outcome.Success, Outcome.Skip),                          Outcome.Success),
			((Outcome.Skip, Outcome.Skip),                             Outcome.Skip),
			((Outcome.Success, None),                                  None),
			((),                                                       None),
		):
			with self.subTest(outcomes=outcomes):
				self.assertIs(expected, Outcome.Combine(outcomes))

	def test_Group(self) -> None:
		group = PipelineGroup("0123abcd")
		pipeline = Pipeline("Pipeline", createdAt=_time(0), outcome=Outcome.Cancellation, parent=group)
		workflow = Workflow("Called", parent=pipeline)
		Job("A", outcome=Outcome.Success, parent=workflow)
		Job("B", outcome=Outcome.Failure, parent=workflow)

		self.assertIs(Outcome.Failure, workflow.Outcome)
		self.assertIs(Outcome.Failure, pipeline.ContentsOutcome)
		self.assertIs(Outcome.Cancellation, pipeline.Outcome, "A pipeline keeps the outcome it was given.")
		self.assertIs(Outcome.Cancellation, group.Outcome)

	def test_Parse(self) -> None:
		self.assertIs(Outcome.Timeout, Outcome.Parse("timeout"))

	def test_OpenTelemetry(self) -> None:
		"""The members and values are those of the conventions, so a trace maps one onto the other."""
		members = {member.name: member.value for member in Outcome}
		self.assertDictEqual({member.name: member.value for member in Result}, members)


class Dependencies(Testcase):
	def test_AddNeed(self) -> None:
		pipeline = Pipeline("Pipeline")
		prepare = Job("Prepare", parent=pipeline)
		matrix = Matrix("Test", parent=pipeline)
		package = Workflow("Package", parent=pipeline)

		matrix.AddNeed(prepare)
		package.AddNeed(prepare)
		package.AddNeed(matrix)

		self.assertListEqual([], prepare.Needs)
		self.assertListEqual([matrix, package], prepare.Dependents)
		self.assertListEqual([prepare], matrix.Needs)
		self.assertListEqual([package], matrix.Dependents)
		self.assertListEqual([prepare, matrix], package.Needs)
		self.assertListEqual([], package.Dependents)

	def test_AddNeed_Pipelines(self) -> None:
		"""Pipelines of one group are siblings, so one can need another."""
		group = PipelineGroup("0123abcd")
		build = Pipeline("Build", parent=group)
		release = Pipeline("Release", parent=group)

		release.AddNeed(build)

		self.assertListEqual([build], release.Needs)

	def test_AddNeed_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			Job("Build").AddNeed(None)

		self.assertEqual("Parameter 'need' is None.", str(context.exception))

	def test_AddNeed_Type(self) -> None:
		pipeline = Pipeline("Pipeline")
		job = Job("Build", parent=pipeline)

		with self.assertRaises(TypeError) as context:
			job.AddNeed(Step("Checkout", parent=job))

		self.assertEqual("Parameter 'need' is not of type 'DependencyMixin'.", str(context.exception))

	def test_AddNeed_NotASibling(self) -> None:
		pipeline = Pipeline("Pipeline")
		prepare = Job("Prepare", parent=pipeline)
		deep = Job("Deep", parent=Workflow("Called", parent=pipeline))

		with self.assertRaises(NeedDependencyError) as context:
			deep.AddNeed(prepare)

		self.assertEqual("'Deep' can't need 'Prepare', which isn't contained in the same group.", str(context.exception))
		self.assertListEqual(["'Deep' is contained in 'Called', 'Prepare' in 'Pipeline'."], context.exception.__notes__)
		self.assertListEqual([], deep.Needs)
		self.assertListEqual([], prepare.Dependents)

	def test_AddNeed_Unplaced(self) -> None:
		"""Elements without a parent aren't siblings."""
		with self.assertRaises(NeedDependencyError):
			Job("A").AddNeed(Job("B"))

	def test_AddNeed_Twice(self) -> None:
		pipeline = Pipeline("Pipeline")
		prepare = Job("Prepare", parent=pipeline)
		build = Job("Build", parent=pipeline)
		build.AddNeed(prepare)

		with self.assertRaises(NeedDependencyError) as context:
			build.AddNeed(prepare)

		self.assertEqual("'Build' needs 'Prepare' already.", str(context.exception))
		self.assertListEqual([prepare], build.Needs)

	def test_AddNeed_Itself(self) -> None:
		job = Job("Build", parent=Pipeline("Pipeline"))

		with self.assertRaises(NeedDependencyCycleError) as context:
			job.AddNeed(job)

		self.assertEqual("'Build' can't need itself.", str(context.exception))

	def test_AddNeed_Cycle(self) -> None:
		pipeline = Pipeline("Pipeline")
		a, b, c, d = (Job(name, parent=pipeline) for name in "ABCD")
		b.AddNeed(a)
		c.AddNeed(b)
		d.AddNeed(c)
		c.AddNeed(a)

		with self.assertRaises(NeedDependencyCycleError) as context:
			a.AddNeed(d)

		self.assertEqual("'A' can't need 'D', because 'D' needs 'A' already.", str(context.exception))
		self.assertListEqual(["Cycle: A -> D -> C -> A."], context.exception.__notes__)
		self.assertListEqual([], a.Needs)
		self.assertListEqual([], d.Dependents)

	def test_AddNeed_DirectCycle(self) -> None:
		pipeline = Pipeline("Pipeline")
		a = Job("A", parent=pipeline)
		b = Matrix("B", parent=pipeline)
		b.AddNeed(a)

		with self.assertRaises(NeedDependencyCycleError) as context:
			a.AddNeed(b)

		self.assertListEqual(["Cycle: A -> B -> A."], context.exception.__notes__)

	def test_Exceptions(self) -> None:
		self.assertTrue(issubclass(NeedDependencyCycleError, NeedDependencyError))
		self.assertTrue(issubclass(NeedDependencyError, PipelineError))

	def test_Mixins(self) -> None:
		for mixin in (DependencyMixin, QualifiedNameMixin):
			with self.subTest(mixin=mixin.__name__):
				self.assertEqual({"_parent"}, set(mixin.__expectedMembers__))

		for cls in (Job, MatrixJob, Matrix, Workflow, Pipeline):
			with self.subTest(cls=cls.__name__):
				self.assertTrue(issubclass(cls, DependencyMixin))
				self.assertEqual(tuple(), cls.__missingMembers__)
				self.assertFalse(hasattr(cls("x"), "__dict__"))

		self.assertFalse(issubclass(Step, DependencyMixin))
		self.assertFalse(issubclass(PipelineGroup, DependencyMixin))

	def test_Mixin_WithoutParent(self) -> None:
		class Rootless(metaclass=ExtendedType, slots=True):
			pass

		class Unrooted(Rootless, DependencyMixin):
			pass

		self.assertEqual(("_parent",), Unrooted.__missingMembers__)
		with self.assertRaises(UnfulfilledExpectationError):
			_ = Unrooted()


class ToGraph(Testcase):
	@staticmethod
	def _Pipeline() -> Pipeline:
		"""
		Build a pipeline: a prepare job, a test matrix, a called workflow with two jobs, and a release job.

		:returns: The pipeline.
		"""
		pipeline = Pipeline("Pipeline")
		prepare = Job("Prepare", parent=pipeline)
		matrix = Matrix("Test", parent=pipeline)
		for version in ("3.13", "3.14"):
			MatrixJob("Test", [version], parent=matrix)
		package = Workflow("Package", reference="./.github/workflows/Package.yml", parent=pipeline)
		build = Job("Build", parent=package)
		Job("Upload", parent=package).AddNeed(build)
		release = Job("Release", parent=pipeline)

		matrix.AddNeed(prepare)
		package.AddNeed(prepare)
		release.AddNeed(prepare)
		release.AddNeed(matrix)
		release.AddNeed(package)

		return pipeline

	@staticmethod
	def _Name(vertex: Vertex) -> str:
		"""
		Return the name a consumer labels a vertex with.

		:param vertex: The vertex.
		:returns:      The qualified name of the element it carries.
		"""
		return vertex.Value.QualifiedName

	def test_Vertices(self) -> None:
		pipeline = self._Pipeline()

		graph = pipeline.ToGraph()

		self.assertIsInstance(graph, Graph)
		self.assertEqual("Pipeline", graph.Name)
		self.assertEqual(4, graph.VertexCount)
		for element in pipeline:
			with self.subTest(element=str(element)):
				vertex = graph.GetVertexByID(element)
				self.assertIs(element, vertex.ID)
				self.assertIs(element, vertex.Value)

		self.assertListEqual(["Prepare", "Test", "Package", "Release"], [self._Name(v) for v in graph.IterateVertices()])

	def _Edges(self, graph: BaseGraph) -> set[tuple[str, str]]:
		"""
		Return the edges of a graph or subgraph by the qualified names of their vertices.

		:param graph: The graph or subgraph.
		:returns:     The pairs of the needed element's and the dependent element's name.
		"""
		return {(self._Name(edge.Source), self._Name(edge.Destination)) for edge in graph.IterateEdges()}

	def test_Edges(self) -> None:
		"""With 'reduce' off, every dependency is an edge."""
		graph = self._Pipeline().ToGraph(reduce=False)

		edges = {("Prepare", "Test"), ("Prepare", "Package"), ("Test", "Release"), ("Package", "Release")}
		self.assertSetEqual(edges | {("Prepare", "Release")}, self._Edges(graph))

	def test_Reduce(self) -> None:
		"""By default, a dependency a longer path implies has no edge."""
		graph = self._Pipeline().ToGraph()

		self.assertSetEqual(
			{("Prepare", "Test"), ("Prepare", "Package"), ("Test", "Release"), ("Package", "Release")}, self._Edges(graph)
		)

	def test_Reduce_Subgraph(self) -> None:
		"""A subgraph is reduced as well, unless 'reduce' is off."""
		pipeline = Pipeline("Pipeline")
		package = Workflow("Package", parent=pipeline)
		build, test, upload = (Job(name, parent=package) for name in ("Build", "Test", "Upload"))
		test.AddNeed(build)
		upload.AddNeed(test)
		upload.AddNeed(build)

		for reduce, edges in (
			(True,  {("Package / Build", "Package / Test"), ("Package / Test", "Package / Upload")}),
			(False, {("Package / Build", "Package / Test"), ("Package / Test", "Package / Upload"),
			         ("Package / Build", "Package / Upload")}),
		):
			with self.subTest(reduce=reduce):
				graph = pipeline.ToGraph(reduce=reduce)
				subgraph = next(iter(graph.Subgraphs))

				self.assertSetEqual(edges, self._Edges(subgraph))
				self.assertListEqual([test, build], upload.Needs, "The model keeps every dependency.")

	def test_Reduce_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline").ToGraph(reduce=1)

		self.assertEqual("Parameter 'reduce' is not of type 'bool'.", str(context.exception))

	def test_Reduce_None(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Pipeline("Pipeline").ToGraph(reduce=None)

		self.assertEqual("Parameter 'reduce' is None.", str(context.exception))

	def test_Subgraphs(self) -> None:
		pipeline = self._Pipeline()
		graph = pipeline.ToGraph()

		subgraphs = {subgraph.Name: subgraph for subgraph in graph.Subgraphs}
		self.assertSetEqual({"Test", "Package"}, set(subgraphs))

		package = subgraphs["Package"]
		self.assertIsInstance(package, Subgraph)
		self.assertSetEqual({"Package / Build", "Package / Upload"}, {self._Name(v) for v in package.IterateVertices()})
		self.assertEqual(1, package.EdgeCount)
		self.assertSetEqual({"Test (3.13)", "Test (3.14)"}, {self._Name(v) for v in subgraphs["Test"].IterateVertices()})

		groupVertex = graph.GetVertexByID(pipeline.Workflows["Package"])
		self.assertListEqual(
			pipeline.Workflows["Package"].Jobs, [link.Destination.Value for link in groupVertex.OutboundLinks]
		)
		self.assertEqual(0, len(graph.GetVertexByID(pipeline.Jobs[0]).OutboundLinks))

	def test_Depth(self) -> None:
		pipeline = Pipeline("Pipeline")
		outer = Workflow("Outer", parent=pipeline)
		inner = Workflow("Inner", parent=outer)
		Job("Deep", parent=inner)

		both = {"Outer", "Outer / Inner"}
		for depth, names in ((None, both), (0, set()), (1, {"Outer"}), (2, both)):
			with self.subTest(depth=depth):
				graph = pipeline.ToGraph(depth)
				self.assertSetEqual(names, {subgraph.Name for subgraph in graph.Subgraphs})

	def test_Depth_Type(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Pipeline("Pipeline").ToGraph("1")

		self.assertEqual("Parameter 'depth' is not of type 'int'.", str(context.exception))

	def test_Depth_Negative(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Pipeline("Pipeline").ToGraph(-1)

		self.assertEqual("Parameter 'depth' is negative.", str(context.exception))

	def test_LeafWorkflow(self) -> None:
		"""A called workflow whose file wasn't read holds nothing and stays a vertex without a subgraph."""
		pipeline = Pipeline("Pipeline")
		Workflow("Foreign", reference="other/repo/.github/workflows/Tool.yml@v1", parent=pipeline)

		graph = pipeline.ToGraph()

		self.assertEqual(1, graph.VertexCount)
		self.assertEqual(0, graph.SubgraphCount)

	def test_DuplicateName(self) -> None:
		"""Two elements of one name are two vertices, because the element is the vertex' ID."""
		pipeline = Pipeline("Pipeline")
		Job("Build", parent=pipeline)
		Job("Build", parent=pipeline)

		graph = pipeline.ToGraph()

		self.assertEqual(2, graph.VertexCount)

	def test_MatrixWorkflow(self) -> None:
		pipeline = Pipeline("Pipeline")
		matrix = Matrix("Tests", parent=pipeline)
		for version in ("3.13", "3.14"):
			Job("Unit", parent=MatrixWorkflow("Tests", [version], parent=matrix))

		graph = pipeline.ToGraph()

		self.assertSetEqual(
			{"Tests", "Tests (3.13)", "Tests (3.14)"}, {subgraph.Name for subgraph in graph.Subgraphs}
		)

	def test_Topologically(self) -> None:
		graph = self._Pipeline().ToGraph()

		order = [self._Name(vertex) for vertex in graph.IterateTopologically()]
		self.assertEqual("Release", order[0])
		self.assertEqual("Prepare", order[-1])
