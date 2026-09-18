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

* :data:`SPAN_KIND` classifies a timespan as :data:`SPAN_KIND_PIPELINE`, :data:`SPAN_KIND_WORKFLOW`,
  :data:`SPAN_KIND_QUEUED`, :data:`SPAN_KIND_JOB` or :data:`SPAN_KIND_STEP`.
* The attributes of OpenTelemetry's semantic conventions for CI/CD name the pipeline, its tasks and their results, e.g.
  :data:`PIPELINE_NAME`, :data:`TASK_NAME` and :data:`TASK_RUN_RESULT`.

.. hint::

   See :ref:`high-level help <TRACING/CI>` for explanations and usage examples.
"""
from datetime              import datetime, timezone
from typing                import Optional as Nullable

from pyTooling.Decorators  import export
from pyTooling.Tracing     import TracingError


__all__ = [
	"SPAN_KIND", "SPAN_KIND_PIPELINE", "SPAN_KIND_WORKFLOW", "SPAN_KIND_QUEUED", "SPAN_KIND_JOB", "SPAN_KIND_STEP",
	"PIPELINE_NAME", "PIPELINE_RUN_ID", "PIPELINE_RUN_URL", "PIPELINE_RESULT",
	"TASK_NAME", "TASK_RUN_ID", "TASK_RUN_URL", "TASK_RUN_RESULT", "WORKER_NAME",
	"RESULT_SUCCESS", "RESULT_FAILURE", "RESULT_TIMEOUT", "RESULT_SKIP", "RESULT_CANCELLATION", "RESULT_ERROR",
]

SPAN_KIND = "ci.span.kind"
"""Attribute classifying what a timespan of a CI pipeline represents."""

SPAN_KIND_PIPELINE = "pipeline"
"""The timespan is a whole pipeline run - the trace itself."""

SPAN_KIND_WORKFLOW = "workflow"
"""The timespan groups the jobs of a called workflow or a stage."""

SPAN_KIND_QUEUED = "queued"
"""The timespan is the time a job waited for a runner, in front of the job's own timespan."""

SPAN_KIND_MATRIX = "matrix"
"""The timespan is a matrix, holding the job instances it produced."""

SPAN_KIND_JOB = "job"
"""The timespan is a job running on a runner."""

SPAN_KIND_STEP = "step"
"""The timespan is a step of a job."""

PIPELINE_NAME = "cicd.pipeline.name"
"""OpenTelemetry CI/CD attribute: the pipeline's name."""

PIPELINE_RUN_ID = "cicd.pipeline.run.id"
"""OpenTelemetry CI/CD attribute: the pipeline run's identifier."""

PIPELINE_RUN_URL = "cicd.pipeline.run.url.full"
"""OpenTelemetry CI/CD attribute: the URL of the pipeline run."""

PIPELINE_RESULT = "cicd.pipeline.result"
"""OpenTelemetry CI/CD attribute: the pipeline run's result - one of the ``RESULT_*`` values."""

TASK_NAME = "cicd.pipeline.task.name"
"""OpenTelemetry CI/CD attribute: the name of a task - a job or a step."""

TASK_RUN_ID = "cicd.pipeline.task.run.id"
"""OpenTelemetry CI/CD attribute: the task run's identifier."""

TASK_RUN_URL = "cicd.pipeline.task.run.url.full"
"""OpenTelemetry CI/CD attribute: the URL of the task run."""

TASK_RUN_RESULT = "cicd.pipeline.task.run.result"
"""OpenTelemetry CI/CD attribute: the task run's result - one of the ``RESULT_*`` values."""

WORKER_NAME = "cicd.worker.name"
"""OpenTelemetry CI/CD attribute: the name of the runner a job ran on."""

RESULT_SUCCESS = "success"
"""OpenTelemetry CI/CD result: the pipeline or task succeeded."""

RESULT_FAILURE = "failure"
"""OpenTelemetry CI/CD result: the pipeline or task failed."""

RESULT_TIMEOUT = "timeout"
"""OpenTelemetry CI/CD result: the pipeline or task was stopped by a timeout."""

RESULT_SKIP = "skip"
"""OpenTelemetry CI/CD result: the pipeline or task was skipped."""

RESULT_CANCELLATION = "cancellation"
"""OpenTelemetry CI/CD result: the pipeline or task was cancelled."""

RESULT_ERROR = "error"
"""OpenTelemetry CI/CD result: the pipeline or task ended for any other reason."""


@export
def parseISO8601Timestamp(value: Nullable[str]) -> Nullable[datetime]:
	"""
	Parse an ISO 8601 timestamp, as CI services report them.

	A timestamp without a time zone is taken as UTC, so every timestamp of a trace can be compared with every other.

	:param value:         The timestamp, e.g. ``'2026-09-15T06:35:24Z'``, or ``None``.
	:returns:             The time zone aware timestamp, or ``None`` if the value is ``None`` or empty.
	:raises TracingError: If the value isn't an ISO 8601 timestamp.
	"""
	if value is None or value == "":
		return None

	try:
		timestamp = datetime.fromisoformat(value)
	except (TypeError, ValueError) as ex:
		error = TracingError(f"'{value}' isn't an ISO 8601 timestamp.")
		error.add_note("CI services report timestamps like '2026-09-15T06:35:24Z'.")
		raise error from ex

	if timestamp.utcoffset() is None:
		timestamp = timestamp.replace(tzinfo=timezone.utc)

	return timestamp
