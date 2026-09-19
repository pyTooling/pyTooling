.. _TRACING:

Overview
########

:mod:`pyTooling.Tracing` records a **software execution trace**: a tree of timespans, each with its own duration,
attributes and events, built with ``with``-statements as a program runs.

.. code-block:: python

   from pyTooling.Tracing import Trace, Span, Event

   with Trace("build") as trace:
     trace["version"] = "10.0.0"

     with Span("compile") as compile:
       compile["files"] = 12
       Event("cache miss", parent=compile)

     with Span("link"):
       ...

   print("\n".join(trace.Format()))

A :class:`~pyTooling.Tracing.Trace` is the root; every :class:`~pyTooling.Tracing.Span` inside it attaches to
whichever span is active on the current thread, so the tree follows the program's structure without being wired up
by hand. An :class:`~pyTooling.Tracing.Event` is a point in time rather than a span, and names its span explicitly.

:meth:`~pyTooling.Tracing.Span.Format` renders the tree as indented lines for a terminal. For anything else, the
trace is exported.

.. _TRACING/Recorded:

Recorded Timespans
==================

A timespan that was measured elsewhere - by a CI service, or read from a log file - already has its times. It is
constructed with them, and attached to its parent by the ``parent`` parameter instead of a ``with``-statement:

.. code-block:: python

   from datetime import datetime, timezone
   from pyTooling.Tracing import Trace, Span

   trace = Trace("Pipeline", beginTime=datetime(2026, 9, 15, 6, 35, 21, tzinfo=timezone.utc),
                             endTime=datetime(2026, 9, 15, 6, 44, 30, tzinfo=timezone.utc))
   job =   Span("UnitTesting", parent=trace, beginTime=datetime(2026, 9, 15, 6, 35, 32, tzinfo=timezone.utc),
                                             endTime=datetime(2026, 9, 15, 6, 37, 10, tzinfo=timezone.utc))
   job["runner"] = "ubuntu-26.04"

   print(job.Duration)   # 98.0

* ``endTime`` requires ``beginTime``, can't precede it, and both are either time zone aware or naive.
* A source reporting a length instead of an end gives ``duration`` in place of ``endTime``, as a
  :class:`~datetime.timedelta` or as a number of seconds - :class:`int` for whole, :class:`float` for
  fractional seconds, the unit :attr:`~pyTooling.Tracing.Span.Duration` reports. It is converted to
  ``endTime``, so every form is stored alike. Giving both ``endTime`` and ``duration`` raises an exception.
* A sub-timespan attached with ``parent`` has to lie within its parent's range. Only the direct parent is checked,
  because containment is transitive.
* A timespan with a ``beginTime`` but no ``endTime`` is still running: its
  :attr:`~pyTooling.Tracing.Span.Duration` is the time since its recorded begin. Assigning
  :attr:`~pyTooling.Tracing.Span.StopTime` reports an end that is already known, and
  :meth:`~pyTooling.Tracing.Span.Stop` ends a timespan that is still running now. Either accepts the end exactly
  once.
* :attr:`~pyTooling.Tracing.Span.State` tells which times are filled in -
  :attr:`~pyTooling.Tracing.SpanState.Empty`, :attr:`~pyTooling.Tracing.SpanState.Running` or
  :attr:`~pyTooling.Tracing.SpanState.Complete` - regardless of whether they were measured or recorded. Only an
  empty timespan can be entered, so a timespan can't be timed twice.
* Without ``beginTime``, a timespan is timed by its ``with``-statement. A timespan constructed with recorded
  times can't be entered - that raises a :exc:`~pyTooling.Tracing.TracingError`.

.. _TRACING/OTLP:

OTLP/JSON Export
################

A :class:`~pyTooling.Tracing.Trace` converts itself to **OTLP/JSON**, the OpenTelemetry Protocol's JSON encoding.
One format reaches both usual destinations: an OpenTelemetry collector accepts OTLP natively, and Jaeger has
accepted it since v1.35 - so no translation step stands between a trace and a viewer.

.. code-block:: python

   from pathlib import Path

   trace.WriteJSONFile(Path("trace.json"), serviceName="myProgram")

.. code-block:: bash

   curl -X POST -H "Content-Type: application/json" -d @trace.json http://localhost:4318/v1/traces

Three methods, for the three things a caller does with the document:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Returns
   * - :meth:`~pyTooling.Tracing.Trace.ToJSON`
     - the document as an :class:`~pyTooling.Tracing.OTLPDocument`, for a caller posting it directly
   * - :meth:`~pyTooling.Tracing.Trace.ToJSONString`
     - the document encoded as a :class:`str`
   * - :meth:`~pyTooling.Tracing.Trace.WriteJSONFile`
     - nothing - it writes the document to the given :class:`~pathlib.Path`

All three take ``scopeName`` and ``scopeVersion``, which name the **instrumentation scope** - the library the spans
are reported as coming from. They default to :data:`~pyTooling.Tracing.OTLP_SCOPE_NAME` and pyTooling's version, so
a program that wraps this tracing in its own API reports itself by passing them rather than by patching the module.

A :class:`~pyTooling.Tracing.Span` and an :class:`~pyTooling.Tracing.Event` convert themselves too, but not
publicly: a lone span is no OTLP document, because it has no service to be reported under. Each level returns its
own part - ``Span._ToOTLPJSON()`` returns itself and everything below it, flattened - and the trace wraps the
result in the document envelope.

The document is not an untyped mapping: every level of it is a :class:`~typing.TypedDict` named after the OTLP
message it encodes, from :class:`~pyTooling.Tracing.OTLPDocument` down to
:class:`~pyTooling.Tracing.OTLPAnyValue`. A caller can annotate what it received, and a typo in a key is a typing
error rather than a document a collector silently rejects.

.. _TRACING/OTLP/Mapping:

How a trace is mapped
=====================

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - pyTooling
     - OTLP
   * - the trace
     - one ``resourceSpans`` entry, whose ``service.name`` attribute is ``serviceName`` - or the trace's name
   * - the tree of spans
     - a **flat** list, whose ``parentSpanId`` references carry the hierarchy
   * - :attr:`~pyTooling.Tracing.Trace.TraceID`, drawn when the trace is constructed
     - ``traceId`` on every span of the trace
   * - :attr:`~pyTooling.Tracing.Span.SpanID`, drawn when the timespan is constructed
     - ``spanId``, and the ``parentSpanId`` of everything below it
   * - :attr:`~pyTooling.Tracing.Span.StartTime` and :attr:`~pyTooling.Tracing.Span.Duration`
     - ``startTimeUnixNano`` and ``endTimeUnixNano``
   * - a span's attributes
     - ``attributes``, each value wrapped by its type
   * - a span's events
     - ``events``

Three details of the encoding are easy to get wrong, and each has a testcase:

* **Identifiers are hex, not base64.** OTLP/JSON deviates from proto3's JSON mapping for ``traceId`` (16 bytes)
  and ``spanId`` (8 bytes), and writes them as lower-case hex.
* **64-bit integers are strings.** A JSON number cannot carry 64 bits exactly, so timestamps and ``intValue``
  attributes are strings - that part *is* proto3's mapping.
* **A duration is nanoseconds.** :attr:`~pyTooling.Tracing.Span.Duration` is in seconds, and the end timestamp is
  computed from it rather than from :attr:`~pyTooling.Tracing.Span.StopTime`, because the duration comes from a
  nanosecond performance counter while the wall clock has microsecond resolution.

.. _TRACING/OTLP/Attributes:

What an attribute may hold
==========================

An attribute's value is one of :data:`~pyTooling.Tracing.AttributeValue`: :class:`bool`, :class:`int`,
:class:`float`, :class:`str`, :class:`bytes`, or a :class:`list`, :class:`tuple` or :class:`dict` of those, nested
as deeply as needed. Each maps to the matching field of OTLP's ``AnyValue``, with :class:`bytes` encoded as base64
and a :class:`dict` becoming a ``kvlistValue``.

A value of any other type raises a :exc:`~pyTooling.Tracing.TracingError` when the trace is exported. Rendering it
with :func:`str` instead would put a Python ``repr`` into a document that a backend then indexes and offers as a
searchable field, which is worse than a failed export.

.. note::

   Both identifiers are drawn when the object is **constructed**, so exporting one trace twice reports the same
   ``traceId`` and the same ``spanId`` values, and :attr:`~pyTooling.Tracing.Trace.TraceID` can be handed to another
   process. That is the identifier a distributed trace is grouped by, as the :class:`~pyTooling.Tracing.Trace`
   documentation describes; propagating it between processes is the remaining step.

.. attention::

   An :class:`~pyTooling.Tracing.Event` always carries a timestamp: the constructor stamps the current system time
   when none is given. OTLP has no way to say *unknown* - a missing ``timeUnixNano`` reads as the Unix epoch - so an
   event without a time would be exported as having happened in 1970.


.. _TRACING/CI:

CI Pipelines
############

:mod:`pyTooling.Tracing.CI` reads the timing of a CI pipeline into a trace, built from
:ref:`recorded timespans <TRACING/Recorded>`. A trace read this way renders and exports like any other, so the time
a pipeline spends waiting for runners and running jobs and steps can be inspected in the same viewers.

.. _TRACING/CI/GitHub:

GitHub Actions
==============

:class:`~pyTooling.Tracing.CI.GitHub.WorkflowRunReader` reads a workflow run through the GitHub REST API, using the
standard library only:

.. code-block:: python

   from os import getenv
   from pathlib import Path
   from pyTooling.Tracing.CI.GitHub import WorkflowRunReader

   reader = WorkflowRunReader("pyTooling/Actions", token=getenv("GITHUB_TOKEN"))
   trace = reader.ReadRun(34937615362)      # optionally: attempt=2
   trace.WriteJSONFile(Path("report/Pipeline.otlp.json"))

Inside a workflow, ``GITHUB_TOKEN`` with the ``actions: read`` permission suffices. A job can't see itself: it is
still running when it reads the run, so a timing job depends on every other job and runs last.

A request failing transiently - HTTP 429, 500, 502, 503 or 504, a timeout, or an unreachable API - is tried again,
``retries`` times (default: 3), after a pause of ``retryDelay`` seconds (default: 2), which doubles with every attempt
or lasts as long as a ``Retry-After`` header demands, up to a minute. HTTP 401, 403 and 404 fail at once.

:meth:`WorkflowRunReader.ConvertWorkflowRun <pyTooling.Tracing.CI.GitHub.WorkflowRunReader.ConvertWorkflowRun>` does
the conversion alone, for a run and jobs that were fetched another way. It is a class method, so converting needs no
reader and therefore no token. It reads both payloads into a :class:`~pyTooling.CI.GitHub.Pipeline` - see
:ref:`CI/GitHub` - and hands that to
:meth:`~pyTooling.Tracing.CI.GitHub.WorkflowRunReader.ConvertPipeline`, which is the entry point when the model was
built elsewhere. Reading the payloads is therefore the model's job, and a field GitHub doesn't document raises
:exc:`~pyTooling.CI.GitHub.GitHubError`.

The run becomes the trace, and every timespan below it is marked by :attr:`~pyTooling.Tracing.CI.CI.Span.Kind` with a
member of :class:`~pyTooling.Tracing.CI.SpanKind`:

+--------------+------------------------------------------------------------------------------------------------------+
| Kind         | Timespan                                                                                             |
+==============+======================================================================================================+
| ``pipeline`` | The workflow run, from its start to its last update once it completed.                               |
+--------------+------------------------------------------------------------------------------------------------------+
| ``workflow`` | A called workflow: the jobs named ``Caller / Job`` are grouped below a timespan ``Caller``.          |
+--------------+------------------------------------------------------------------------------------------------------+
| ``matrix``   | A matrix: the jobs named ``Job (ubuntu-26.04, 3.14)`` are grouped below a timespan ``Job``.          |
+--------------+------------------------------------------------------------------------------------------------------+
| ``queued``   | ``<job> (queued)``, the time a job waited for a runner, in front of the job.                         |
+--------------+------------------------------------------------------------------------------------------------------+
| ``job``      | A job, from its start to its completion.                                                             |
+--------------+------------------------------------------------------------------------------------------------------+
| ``step``     | A step that started, below its job.                                                                  |
+--------------+------------------------------------------------------------------------------------------------------+

Every timespan also carries the attributes of OpenTelemetry's semantic conventions for CI/CD, which
:class:`~pyTooling.Tracing.CI.OTLP` names as a namespace nested the way the keys are - so
:attr:`OTLP.CICD.Pipeline.Task.Run.ID <pyTooling.Tracing.CI.OTLP>` spells ``cicd.pipeline.task.run.id`` and the path
can be read to check the key. The values a result may take are :class:`~pyTooling.Tracing.CI.Result`. What only GitHub
reports is named the same way by :class:`~pyTooling.Tracing.CI.GitHub.GitHub`, e.g.
``github.conclusion`` beside the result it was mapped to. A job's timespan names its runner and the labels it was
requested by, so a renderer can group waiting times per operating system, and a matrix instance additionally lists the
values it was produced for in ``github.matrix.dimensions``.

A task is named the way GitHub reports it - ``Caller / Build (ubuntu-26.04)`` - while the timespan itself is named by
the part the model holds, so a timespan reads in the context its parents already give.

GitHub reports timestamps in whole seconds. A step shorter than a second lasts zero seconds, and an end reported a
second before its begin is moved to the begin.
