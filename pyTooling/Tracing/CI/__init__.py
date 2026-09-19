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
from enum                  import StrEnum
from typing                import ClassVar

from pyTooling.Decorators  import export
from pyTooling.MetaClasses import ExtendedType


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

