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
Readers converting the timing of CI pipelines into a software execution trace (:class:`~pyTooling.Tracing.Trace`).

Every reader marks its timespans with the same attributes, so a renderer or a query doesn't need to know which CI
service a trace came from:

* :attr:`CI.Span.Kind` classifies a timespan by a member of :class:`SpanKind`.
* :class:`OTLP` holds the attribute keys of OpenTelemetry's semantic conventions, nested as the keys themselves are,
  and :class:`Result` the values the conventions allow for a result.

.. hint::

   See :ref:`high-level help <TRACING/CI>` for explanations and usage examples.
"""
from datetime              import datetime
from enum                  import StrEnum
from typing                import ClassVar, Mapping, Optional as Nullable

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Tracing     import AttributeValue, Span, Trace


@export
class OTLP(metaclass=ExtendedType, slots=True):
	"""
	Attribute keys defined by OpenTelemetry's `semantic conventions <https://opentelemetry.io/docs/specs/semconv/>`__.

	The nesting mirrors the key itself: every level is one dot, so :attr:`OTLP.CICD.Pipeline.Task.Run.ID` spells
	``'cicd.pipeline.task.run.id'``. A key can therefore be checked by reading the path that names it.

	.. code-block:: python

	   trace[OTLP.CICD.Pipeline.Name] =        pipeline.Name
	   span[OTLP.CICD.Pipeline.Task.Run.ID] =  str(job.ID)
	"""

	class CICD(metaclass=ExtendedType, slots=True):
		"""Attribute keys of the conventions for **CI/CD pipelines**."""

		class Pipeline(metaclass=ExtendedType, slots=True):
			"""Attribute keys naming a pipeline and its run."""

			Name:   ClassVar[str] = "cicd.pipeline.name"    #: The pipeline's name.
			Result: ClassVar[str] = "cicd.pipeline.result"  #: How the run ended - a member of :class:`Result`.

			class Run(metaclass=ExtendedType, slots=True):
				"""Attribute keys naming one run of a pipeline."""

				ID: ClassVar[str] = "cicd.pipeline.run.id"  #: The run's identifier.

				class URL(metaclass=ExtendedType, slots=True):
					"""Attribute keys naming the addresses of a run."""

					Full: ClassVar[str] = "cicd.pipeline.run.url.full"  #: The run's address.

			class Task(metaclass=ExtendedType, slots=True):
				"""Attribute keys naming a task of a pipeline - a job or a step."""

				Name: ClassVar[str] = "cicd.pipeline.task.name"  #: The task's name, as the service reports it.

				class Run(metaclass=ExtendedType, slots=True):
					"""Attribute keys naming one run of a task."""

					ID:     ClassVar[str] = "cicd.pipeline.task.run.id"      #: The task run's identifier.
					Result: ClassVar[str] = "cicd.pipeline.task.run.result"  #: How the task ended - a member of :class:`Result`.

					class URL(metaclass=ExtendedType, slots=True):
						"""Attribute keys naming the addresses of a task run."""

						Full: ClassVar[str] = "cicd.pipeline.task.run.url.full"  #: The task run's address.

		class Worker(metaclass=ExtendedType, slots=True):
			"""Attribute keys naming the worker a task ran on."""

			Name: ClassVar[str] = "cicd.worker.name"  #: The worker's name.

	class VCS(metaclass=ExtendedType, slots=True):
		"""Attribute keys of the conventions for **version control systems**."""

		class Ref(metaclass=ExtendedType, slots=True):
			"""Attribute keys naming a reference."""

			class Head(metaclass=ExtendedType, slots=True):
				"""Attribute keys naming the reference a pipeline was started on."""

				Name:     ClassVar[str] = "vcs.ref.head.name"      #: The branch or tag the run was started on.
				Revision: ClassVar[str] = "vcs.ref.head.revision"  #: The commit the run was started on.


@export
class CI(metaclass=ExtendedType, slots=True):
	"""
	Attribute keys pyTooling defines for the timespans of a CI pipeline, which the conventions don't cover.

	The nesting mirrors the key the same way :class:`OTLP` does.
	"""

	class Span(metaclass=ExtendedType, slots=True):
		"""Attribute keys classifying a timespan."""

		Kind: ClassVar[str] = "ci.span.kind"  #: What the timespan represents - a member of :class:`SpanKind`.


@export
class SpanKind(StrEnum):
	"""
	What a timespan of a CI pipeline represents.

	These values are pyTooling's own: OpenTelemetry's conventions classify a span by its kind (``SERVER``,
	``INTERNAL``, ...), not by its role in a pipeline.
	"""

	Pipeline = "pipeline"  #: A whole pipeline run - the trace itself.
	Workflow = "workflow"  #: The jobs of a called workflow or a stage, grouped.
	Matrix =   "matrix"    #: A matrix, holding the job instances it produced.
	Queued =   "queued"    #: The time a job waited for a worker, in front of the job's own timespan.
	Job =      "job"       #: A job running on a worker.
	Step =     "step"      #: A step of a job.


@export
class Result(StrEnum):
	"""
	How a pipeline run or a task run ended.

	The conventions fix this set, and a backend groups runs by the string, so a member's :attr:`~enum.Enum.value` is
	what goes on the wire.
	"""

	Success =      "success"       #: It succeeded.
	Failure =      "failure"       #: It failed.
	Timeout =      "timeout"       #: It was stopped by a timeout.
	Skip =         "skip"          #: It was skipped.
	Cancellation = "cancellation"  #: It was cancelled.
	Error =        "error"         #: It ended for any other reason.



@export
class CITimespanMixIn(metaclass=ExtendedType, mixin=True, expects=("__setitem__",)):
	"""
	Mixin-class for a timespan of a CI pipeline.

	A timespan of a pipeline is classified by :attr:`CI.Span.Kind` and carries the attributes the conventions define
	for what it represents. The flavour names its kind in :attr:`KIND`, so the classification is a property of the
	type rather than something every producer remembers to set.
	"""

	KIND: ClassVar[SpanKind]  #: What a timespan of this flavour represents. Every flavour names it.

	def SetAttributes(self, attributes: Mapping[str, Nullable[AttributeValue]]) -> None:
		"""
		Set the attributes whose value is known.

		A service reports a field it doesn't know as ``None``, and one it knows to be empty as an empty string or an
		empty list. Neither is worth an attribute, so both are skipped and the key stays absent instead of naming an
		empty value.

		:param attributes: The attributes by key.
		"""
		for key, value in attributes.items():
			if value is not None and value != "" and value != []:
				self[key] = value


@export
class PipelineTrace(Trace, CITimespanMixIn):
	"""A pipeline run - the trace every other timespan of the run is below."""

	KIND: ClassVar[SpanKind] = SpanKind.Pipeline  #: This flavour represents a pipeline run.

	def __init__(
		self,
		name:         str,
		beginTime:    Nullable[datetime] = None,
		endTime:      Nullable[datetime] = None,
		*,
		pipelineName: Nullable[str] = None,
		runID:        Nullable[str] = None,
		runURL:       Nullable[str] = None,
		result:       Nullable[Result] = None,
		reference:    Nullable[str] = None,
		revision:     Nullable[str] = None,
		attributes:   Nullable[Mapping[str, Nullable[AttributeValue]]] = None
	) -> None:
		"""
		Initializes the trace of a pipeline run.

		:param name:         Name of the trace.
		:param beginTime:    Optional, recorded time when the run began. Default: the time the trace is entered.
		:param endTime:      Optional, recorded time when the run ended. Default: the run is still running.
		:param pipelineName: Optional, the pipeline's name, if it differs from the trace's. Default: the trace's name.
		:param runID:        Optional, the run's identifier. Default: unknown.
		:param runURL:       Optional, the run's address. Default: unknown.
		:param result:       Optional, how the run ended. Default: it hasn't ended.
		:param reference:    Optional, the branch or tag the run was started on. Default: unknown.
		:param revision:     Optional, the commit the run was started on. Default: unknown.
		:param attributes:   Optional, further attributes, e.g. what only one service reports. Default: none.
		"""
		super().__init__(name, beginTime, endTime)

		self[CI.Span.Kind] = self.KIND
		self.SetAttributes({
			OTLP.CICD.Pipeline.Name:         name if pipelineName is None else pipelineName,
			OTLP.CICD.Pipeline.Run.ID:       runID,
			OTLP.CICD.Pipeline.Run.URL.Full: runURL,
			OTLP.CICD.Pipeline.Result:       result,
			OTLP.VCS.Ref.Head.Name:          reference,
			OTLP.VCS.Ref.Head.Revision:      revision
		})

		if attributes is not None:
			self.SetAttributes(attributes)


@export
class TaskSpan(Span, CITimespanMixIn):
	"""
	Base-class of the timespans below a pipeline run.

	Every one of them is a task of the pipeline in the conventions' sense, so every one names itself in
	:attr:`OTLP.CICD.Pipeline.Task.Name <pyTooling.Tracing.CI.OTLP>` - with the name the service reports, which may
	differ from the timespan's when a timespan is named by the part of the tree it sits in.
	"""

	def __init__(
		self,
		name:       str,
		beginTime:  Nullable[datetime] = None,
		endTime:    Nullable[datetime] = None,
		*,
		parent:     Nullable[Span] = None,
		taskName:   Nullable[str] = None,
		attributes: Nullable[Mapping[str, Nullable[AttributeValue]]] = None
	) -> None:
		"""
		Initializes a timespan below a pipeline run.

		:param name:       Name of the timespan.
		:param beginTime:  Optional, recorded time when it began. Default: the time the timespan is entered.
		:param endTime:    Optional, recorded time when it ended. Default: it is still running.
		:param parent:     Optional, the timespan it sits in. Default: no parent.
		:param taskName:   Optional, the name the service reports, if it differs from the timespan's. Default: the
		                   timespan's name.
		:param attributes: Optional, further attributes, e.g. what only one service reports. Default: none.
		"""
		super().__init__(name, beginTime, endTime, parent=parent)

		self[CI.Span.Kind] = self.KIND
		self[OTLP.CICD.Pipeline.Task.Name] = name if taskName is None else taskName

		if attributes is not None:
			self.SetAttributes(attributes)


@export
class WorkflowSpan(TaskSpan):
	"""The jobs of a called workflow or a stage, grouped into one timespan."""

	KIND: ClassVar[SpanKind] = SpanKind.Workflow  #: This flavour represents the jobs of a called workflow or a stage.


@export
class MatrixSpan(TaskSpan):
	"""The instances a matrix produced, grouped into one timespan."""

	KIND: ClassVar[SpanKind] = SpanKind.Matrix  #: This flavour represents the instances of a matrix.


@export
class QueuedSpan(TaskSpan):
	"""The time a job waited for a worker, in front of the job's own timespan."""

	KIND: ClassVar[SpanKind] = SpanKind.Queued  #: This flavour represents a job waiting for a worker.


@export
class JobSpan(TaskSpan):
	"""A job, from the moment it started on a worker until it completed."""

	KIND: ClassVar[SpanKind] = SpanKind.Job  #: This flavour represents a job.

	def __init__(
		self,
		name:       str,
		beginTime:  Nullable[datetime] = None,
		endTime:    Nullable[datetime] = None,
		*,
		parent:     Nullable[Span] = None,
		taskName:   Nullable[str] = None,
		runID:      Nullable[str] = None,
		runURL:     Nullable[str] = None,
		result:     Nullable[Result] = None,
		workerName: Nullable[str] = None,
		attributes: Nullable[Mapping[str, Nullable[AttributeValue]]] = None
	) -> None:
		"""
		Initializes the timespan of a job.

		:param name:       Name of the timespan.
		:param beginTime:  Optional, recorded time when the job started. Default: the time the timespan is entered.
		:param endTime:    Optional, recorded time when the job completed. Default: it is still running.
		:param parent:     Optional, the timespan it sits in. Default: no parent.
		:param taskName:   Optional, the name the service reports, if it differs from the timespan's. Default: the
		                   timespan's name.
		:param runID:      Optional, the job's identifier. Default: unknown.
		:param runURL:     Optional, the job's address. Default: unknown.
		:param result:     Optional, how the job ended. Default: it hasn't ended.
		:param workerName: Optional, name of the worker the job ran on. Default: unknown.
		:param attributes: Optional, further attributes, e.g. what only one service reports. Default: none.
		"""
		super().__init__(name, beginTime, endTime, parent=parent, taskName=taskName)

		self.SetAttributes({
			OTLP.CICD.Pipeline.Task.Run.ID:       runID,
			OTLP.CICD.Pipeline.Task.Run.URL.Full: runURL,
			OTLP.CICD.Pipeline.Task.Run.Result:   result,
			OTLP.CICD.Worker.Name:                workerName
		})

		if attributes is not None:
			self.SetAttributes(attributes)


@export
class StepSpan(TaskSpan):
	"""A step of a job."""

	KIND: ClassVar[SpanKind] = SpanKind.Step  #: This flavour represents a step.

	def __init__(
		self,
		name:       str,
		beginTime:  Nullable[datetime] = None,
		endTime:    Nullable[datetime] = None,
		*,
		parent:     Nullable[Span] = None,
		taskName:   Nullable[str] = None,
		result:     Nullable[Result] = None,
		attributes: Nullable[Mapping[str, Nullable[AttributeValue]]] = None
	) -> None:
		"""
		Initializes the timespan of a step.

		:param name:       Name of the timespan.
		:param beginTime:  Optional, recorded time when the step started. Default: the time the timespan is entered.
		:param endTime:    Optional, recorded time when the step completed. Default: it is still running.
		:param parent:     Optional, the timespan of the job containing the step. Default: no parent.
		:param taskName:   Optional, the name the service reports, if it differs from the timespan's. Default: the
		                   timespan's name.
		:param result:     Optional, how the step ended. Default: it hasn't ended.
		:param attributes: Optional, further attributes, e.g. what only one service reports. Default: none.
		"""
		super().__init__(name, beginTime, endTime, parent=parent, taskName=taskName)

		self.SetAttributes({OTLP.CICD.Pipeline.Task.Run.Result: result})

		if attributes is not None:
			self.SetAttributes(attributes)
