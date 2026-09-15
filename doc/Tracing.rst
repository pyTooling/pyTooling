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

:func:`~pyTooling.Tracing.CI.GitHub.ConvertWorkflowRun` does the conversion alone, for a run and jobs that were
fetched another way. It reads both payloads into a :class:`~pyTooling.CI.GitHub.Pipeline` - see :ref:`CI/GitHub` - and
hands that to :func:`~pyTooling.Tracing.CI.GitHub.ConvertPipeline`, which is the entry point when the model was built
elsewhere. Reading the payloads is therefore the model's job, and a field GitHub doesn't document raises
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


.. _TRACING/Render:

Rendering
#########

A trace renders as a **Gantt chart**: one row per timespan, in the tree's order and indented by depth.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing.Render import StepExclusion, ciSpanFilter
   from pyTooling.Tracing.Render.Matplotlib import WriteGantt

   WriteGantt(trace, Path("report/Pipeline.svg"), spanFilter=ciSpanFilter(excludeSteps=StepExclusion.Skipped))

The chart is laid out by :class:`~pyTooling.Tracing.Render.GanttLayout`, independently of the library drawing it:

* Times are seconds after the trace began. A running timespan ends at the layout's current time.
* The pipeline and a called workflow are a line from their begin to their end, a job is a bar. A job's waiting
  timespan (``queued``) is a light gray bar in front of the job's bar. A job that didn't start yet has only its waiting
  bar, on a row of its own.
* A ``spanFilter`` hides timespans, and a hidden timespan hides its sub-spans. A filter created by
  :func:`~pyTooling.Tracing.Render.ciSpanFilter` hides the steps of CI jobs - all of them, the skipped ones, or none, as
  :class:`~pyTooling.Tracing.Render.StepExclusion` selects - and the jobs that were skipped. Steps outnumber jobs by
  far: a pipeline of 74 jobs has 1653 steps, 635 of them skipped.
* Bars are colored by category. :func:`~pyTooling.Tracing.Render.runnerCategory` names the runner image a job ran on,
  and the MSYS2 environment of a job using one, e.g. ``windows-2025 + UCRT64``, because such a job takes significantly
  longer than a native job on the same runner. The environment is taken from a successful step matching
  :data:`~pyTooling.Tracing.Render.MSYS2_SETUP_STEP`, like ``Setup MSYS2 for UCRT64``.

The legend summarizes the pipeline: when it started and finished, with the time zone; its wall time; its **runner
time** - the time all jobs ran, added up, which runners were occupied for; and per category the number of jobs and
their minimum, average and maximum waiting and running times. These statistics count every job that wasn't skipped,
independently of the filter.

:func:`~pyTooling.Tracing.Render.Matplotlib.WriteGantt` writes the chart with :term:`matplotlib` as SVG, PNG or PDF,
chosen by the file's suffix, and :func:`~pyTooling.Tracing.Render.Matplotlib.RenderGantt` returns it as a figure for
further changes. matplotlib is an optional dependency, installed by the extra ``pyTooling[diagram]`` together with
:term:`plotly`, which draws the same chart as an interactive HTML page - see :ref:`TRACING/Render/Plotly`.

In an SVG file, every bar or line is a group with the identifier ``span-<SpanID>``, a waiting bar
``span-<SpanID>-queued``, the end marks of a line ``span-<SpanID>-ends`` and a row's label ``label-<SpanID>``.

.. _TRACING/Render/Collapsible:

Collapsible SVG
===============

With ``collapsible=True``, :func:`~pyTooling.Tracing.Render.Matplotlib.WriteGantt` adds a script to an SVG file:
clicking the label, bar or line of a row with sub-rows hides the rows below it - a called workflow's jobs, or a job's
steps - and moves the following rows up. A second click shows them again, and a marker in front of the label shows
the state.

.. code-block:: python

   WriteGantt(
     trace, Path("report/Pipeline.svg"),
     spanFilter=ciSpanFilter(excludeSteps=StepExclusion.Skipped),
     collapsible=True
   )

The rows of the kinds in ``collapsedKinds`` start collapsed - jobs by default, so a chart with steps opens as compact
as one without them. The script runs where an SVG file is a document: opened in a browser, or embedded by
``<object>`` or inline. An SVG file shown as an image - by ``<img>``, in Markdown or in a pipeline's job summary - is
static and shows every row expanded.

.. _TRACING/Render/Plotly:

Interactive HTML
================

:func:`~pyTooling.Tracing.Render.Plotly.WriteGantt` writes the chart with :term:`plotly` as an HTML page, or as the
plotly figure's JSON, chosen by the file's suffix. :func:`~pyTooling.Tracing.Render.Plotly.RenderGantt` returns it as a
plotly figure for further changes. Both take the same layout as the matplotlib renderer, so the rows, colors and
legend are the same.

.. code-block:: python

   from pyTooling.Tracing.Render.Plotly import WriteGantt

   WriteGantt(trace, Path("report/Pipeline.html"), spanFilter=ciSpanFilter(excludeSteps=StepExclusion.Skipped))

The page can be zoomed and panned. Hovering a bar or line shows the timespan's name, its absolute begin and end, and its
duration, and a click on a legend entry hides or shows a category's bars. The page embeds plotly's JavaScript library -
about 4 MiB - so it works offline, e.g. downloaded from a pipeline's artifacts; ``includePlotlyJS="cdn"`` loads the
library from plotly's CDN instead.

The time axis is a date axis showing the time since the trace began as ``hh:mm:ss``, so its ticks adapt when zooming.
For a trace longer than a day, the ticks start again at ``00:00:00``.
