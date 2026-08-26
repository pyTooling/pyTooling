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

   trace.WriteOTLPJSONFile(Path("trace.json"), serviceName="myProgram")

.. code-block:: bash

   curl -X POST -H "Content-Type: application/json" -d @trace.json http://localhost:4318/v1/traces

Three methods, for the three things a caller does with the document:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Returns
   * - :meth:`~pyTooling.Tracing.Trace.ToOTLPJSON`
     - the document as an :class:`~pyTooling.Tracing.OTLPDocument`, for a caller posting it directly
   * - :meth:`~pyTooling.Tracing.Trace.ToOTLPJSONString`
     - the document encoded as a :class:`str`
   * - :meth:`~pyTooling.Tracing.Trace.WriteOTLPJSONFile`
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

A timespan and an event carry their attributes like a dictionary: :pycode:`span["key"]`, :pycode:`span["key"] = 1`,
:pycode:`"key" in span`, :pycode:`del span["key"]`, :pycode:`len(span)`, and iteration yielding
:pycode:`(key, value)` pairs. A key that may not be there is read by
:meth:`~pyTooling.Tracing.TraceElement.get`, which returns a default value instead of raising a :exc:`KeyError`.

Both are :class:`~pyTooling.Tracing.TraceElement`\ s: a name, the timespan enclosing them, and those attributes.
A :class:`~pyTooling.Tracing.Span` adds the times and what it contains, an :class:`~pyTooling.Tracing.Event` the
moment it happened.

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


.. _TRACING/OTLP/Import:

OTLP/JSON Import
################

A :class:`~pyTooling.Tracing.Trace` reads itself back from an OTLP/JSON document, so a trace written by one process
- a build step, a worker, an earlier run - can be inspected, formatted or merged by another.

This is the path for a **complete** trace in a document of its own. A document that carries several traces, or only
part of one, is read by a :class:`~pyTooling.Tracing.TraceCollection` - see :ref:`TRACING/OTLP/Collection`.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing import Trace

   trace = Trace.ReadOTLPJSONFile(Path("trace.json"))
   print("\n".join(trace.Format()))

Three class-methods mirror the three export methods:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Class-method
     - Reads
   * - :meth:`~pyTooling.Tracing.Trace.FromOTLPJSON`
     - an :class:`~pyTooling.Tracing.OTLPDocument`, as :func:`json.load` returns it
   * - :meth:`~pyTooling.Tracing.Trace.FromOTLPJSONString`
     - the document encoded as a :class:`str`
   * - :meth:`~pyTooling.Tracing.Trace.ReadOTLPJSONFile`
     - the document from the given :class:`~pathlib.Path`

.. _TRACING/OTLP/Import/Tree:

Reassembling the tree
=====================

OTLP has no nesting: a trace is a **flat** list of spans, and the hierarchy lives in the ``parentSpanId`` references.
Reading is therefore not the mirror image of writing - the references have to be resolved:

* The spans of every ``resourceSpans`` and ``scopeSpans`` entry are collected, because nothing requires a producer
  to put one trace into one entry, and they are grouped by their ``traceId``.
* The span **without** a ``parentSpanId`` becomes the :class:`~pyTooling.Tracing.Trace` itself; every other span is
  created as a sub-span of the one it names, keeping the order the document has it in.
* A document holding more than one trace needs the ``traceID`` parameter to say which one to read. Without it, a
  document of several traces is an error rather than a guess.

A :class:`~pyTooling.Tracing.Span` and an :class:`~pyTooling.Tracing.Event` read themselves too, but not publicly -
``Span._FromOTLPJSON()`` and ``Event._FromOTLPJSON()`` construct one level and attach it to its parent, which is
what :meth:`~pyTooling.Tracing.Trace.FromOTLPJSON` walks the resolved references with. A lone span cannot be read
publicly for the same reason it cannot be written publicly: it has no trace to belong to.

.. _TRACING/OTLP/Import/RoundTrip:

What a round-trip carries
=========================

Exporting a trace, reading it back and exporting it again produces the **same document**, and there is a testcase
saying so. Identifiers, names, the tree, attributes, events and durations all survive.

Four things do not come back, and each of them is a property of OTLP rather than of this reader:

.. list-table::
   :header-rows: 1
   :widths: 32 68

   * - Not read back
     - Why
   * - ``service.name``
     - a parameter of :meth:`~pyTooling.Tracing.Trace.ToOTLPJSON`, not a field of the data model
   * - the instrumentation scope
     - the same - the scope names the library that produced the spans
   * - a span's ``kind``
     - every timespan of this data model is ``SPAN_KIND_INTERNAL``
   * - a :class:`tuple` attribute
     - it returns as a :class:`list`, because OTLP has a single ``arrayValue``

Two details are worth knowing about the timestamps. A :class:`~datetime.datetime` holds microseconds while the
document holds nanoseconds, so a timestamp is **rounded** to the nearest microsecond rather than truncated - the
export scales a :meth:`~datetime.datetime.timestamp` float by 1e9, whose precision at today's epoch is about 256 ns,
and rounding lands back on the microsecond it came from. The duration, in turn, is the difference of the two
timestamps and stays exact, because the performance counter that measured it ran in another process.

.. _TRACING/OTLP/Import/Validation:

What is rejected
================

A document that arrives over the network or out of a file is not trusted. Every field is checked, and a
:exc:`~pyTooling.Tracing.TracingError` names the position it was found at - ``Field
'document.resourceSpans[0].scopeSpans[0].spans[3].spanId' is all zeros.`` - so a broken document can be looked at
rather than guessed about.

Rejected are, among others:

* a mandatory field that is missing or of the wrong type,
* a ``traceId`` or ``spanId`` that isn't 32 or 16 hex digits, or that is all zeros, which OTLP defines as invalid,
* the same ``spanId`` twice within one trace,
* spans that don't form a tree below exactly one root: several roots, a cycle, or a ``parentSpanId`` naming a span
  the document doesn't contain,
* a timespan with one of its two timestamps, or one that ends before it starts,
* an attribute list carrying the same key twice, because a key-value pair holds only one of them,
* an ``AnyValue`` that names no type, two types, or a type OTLP doesn't have.

What is *accepted* although the export never writes it: an upper-case identifier - normalized to lower case, so its
references still resolve - an ``intValue`` or ``timeUnixNano`` written as a JSON number instead of a string, a
``doubleValue`` of ``"NaN"`` or ``"Infinity"``, an integer where a double is expected, and an empty
``parentSpanId`` instead of an absent one. Each of those is proto3's JSON mapping being read as it is written,
which is what a document from another producer looks like.


.. _TRACING/OTLP/Collection:

Collecting traces
#################

A document is not a trace. It carries whatever spans a producer had to hand, and two things follow from that:

* it may hold **several traces** at once, and
* it may hold only **part** of a trace. A distributed execution is exported by each process separately, so the
  timespan enclosing a span is often in a different document than the span itself.

A :class:`~pyTooling.Tracing.TraceCollection` holds both cases. It keeps the traces whose root span has arrived, and
the **fragments** - timespans whose ``parentSpanId`` names a span nothing has delivered yet. A fragment is a real
timespan with its own sub-spans; only its place in the tree is unknown.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing import TraceCollection

   collection = TraceCollection.ReadOTLPJSONFile(Path("frontend.json"))
   collection.AddOTLPJSONFile(Path("worker.json"))
   collection.AddOTLPJSONFile(Path("database.json"))

   for trace in collection:
     print("\n".join(trace.Format()))

   if collection.HasFragments:
     print(f"{collection.FragmentCount} timespans are still waiting for their parent.")

The three documents may be added in **any order**. Each one is linked in both directions: a fragment it brings finds
a parent that arrived earlier, and a span it brings collects the fragments that were waiting for it. When a fragment
is attached, its parent's sub-spans are re-sorted by start time, so the reassembled trace reads like a local one
instead of like the order the files happened to be read in.

.. _TRACING/OTLP/Collection/Lookup:

Looking things up
=================

Both indexes are keyed by identifier, which is what makes the linking possible - and what makes the collection
useful on its own:

.. list-table::
   :header-rows: 1
   :widths: 45 55

   * - Expression
     - Yields
   * - ``collection[traceID]``
     - the :class:`~pyTooling.Tracing.Trace`, for an identifier of 32 hex digits
   * - ``collection[spanID]``
     - the :class:`~pyTooling.Tracing.Span`, for an identifier of 16 hex digits - fragments included
   * - :attr:`~pyTooling.Tracing.TraceCollection.Traces` / :attr:`~pyTooling.Tracing.TraceCollection.Fragments`
     - the complete traces, and the root timespan of each fragment
   * - :meth:`~pyTooling.Tracing.TraceCollection.TraceIDOfSpan`
     - which trace a timespan belongs to - answerable for a fragment, which has no
       :attr:`~pyTooling.Tracing.Span.Trace` to ask
   * - ``for trace in collection`` / ``len(collection)``
     - the **complete** traces; a fragment is not a trace and is neither iterated nor counted as one

A trace identifier is 32 hex digits and a span identifier is 16, so which of the two indexes ``[...]`` searches
follows from the length. The two can't be confused.

.. _TRACING/OTLP/Collection/Writing:

Writing a collection back
=========================

:meth:`~pyTooling.Tracing.TraceCollection.ToOTLPJSON` writes every trace as its own ``resourceSpans`` entry, and a
fragment into the entry of the trace it belongs to - carrying the ``parentSpanId`` it is waiting for, so reading the
document back produces the same fragment rather than a second root span. A trace whose root span never arrived has
no name to report, so its ``service.name`` is its trace identifier.

.. topic:: Which entry point?

   Use :meth:`Trace.FromOTLPJSON <pyTooling.Tracing.Trace.FromOTLPJSON>` when the document holds one complete trace
   and a :class:`~pyTooling.Tracing.Trace` is what the caller wants - it rejects anything else rather than returning
   half a tree. Use :meth:`TraceCollection.FromOTLPJSON <pyTooling.Tracing.TraceCollection.FromOTLPJSON>` when the
   document is whatever a collector handed over.


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

:meth:`WorkflowRunTrace.FromJSON <pyTooling.Tracing.CI.GitHub.WorkflowRunTrace.FromJSON>` does the conversion alone,
for a run and jobs that were fetched another way. It is a class method, so converting needs no reader and therefore
no token. It reads both payloads into a :class:`~pyTooling.CI.GitHub.Pipeline` - see :ref:`CI/GitHub` - and hands
that to :meth:`~pyTooling.Tracing.CI.GitHub.WorkflowRunTrace.FromPipeline`, which is the entry point when the model
was built elsewhere. Reading the payloads is therefore the model's job, and a field GitHub doesn't document raises
:exc:`~pyTooling.CI.GitHub.GitHubError` - as does an answer the reader itself can't read, so everything GitHub says
that can't be made sense of is one exception type. A request that *fails* is a
:exc:`~pyTooling.REST.RESTError`, because nothing about GitHub's answer was wrong - there wasn't one.

The run becomes the trace, and every timespan below it is marked by :attr:`~pyTooling.Tracing.CI.CI.Span.Kind` with a
member of :class:`~pyTooling.Tracing.CI.SpanKind`. Each kind is a class of its own - a
:class:`~pyTooling.Tracing.CI.JobSpan` sets ``ci.span.kind`` to ``job`` because that is what it is, and takes the
attributes of a job as parameters - so a reader states values and never a key, and a reader of another service
builds the same classes:

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

Each flavour builds itself from the model: :meth:`JobSpan.FromJob <pyTooling.Tracing.CI.GitHub.JobSpan.FromJob>` takes
a :class:`~pyTooling.CI.GitHub.Job` and produces the job's timespan, the waiting timespan in front of it, and a
timespan per step. So reading a service means mapping its model onto these classes, and everything else - the kinds,
the attribute keys, and skipping what the service doesn't report - is
:mod:`pyTooling.Tracing.CI`'s.

What the payloads *say* is the model's, including the two facts a timeline depends on: a group's elements come in
the order they were queued, and a job's times contain its steps, because GitHub reports both in whole seconds and a
step is sometimes reported as running outside the job holding it - see :ref:`CI/GitHub`.

GitHub reports timestamps in whole seconds. A step shorter than a second lasts zero seconds, and an end reported a
second before its begin is moved to the begin.


.. _TRACING/Render:

Rendering
#########

A trace renders as a **Gantt chart**: one row per timespan, in the tree's order and indented by depth.

.. code-block:: python

   from pathlib import Path
   from pyTooling.Tracing.Render import GanttLayout, StepExclusion, ciSpanFilter
   from pyTooling.Tracing.Render.Matplotlib import MatplotlibRenderer

   layout = GanttLayout(trace, spanFilter=ciSpanFilter(excludeSteps=StepExclusion.Skipped))
   MatplotlibRenderer(layout).Write(Path("report/Pipeline.svg"))

**Laying out and drawing are two objects.** :class:`~pyTooling.Tracing.Render.GanttLayout` arranges the timespans,
and a :class:`~pyTooling.Tracing.Render.Renderer` draws what it arranged - so a second backend draws the same chart
without repeating the arrangement. The layout:

* A bar keeps the times it was built from: :attr:`~pyTooling.Tracing.Render.GanttBar.BeginTime` and
  :attr:`~pyTooling.Tracing.Render.GanttBar.EndTime` are what the trace recorded, while
  :attr:`~pyTooling.Tracing.Render.GanttBar.Begin` and :attr:`~pyTooling.Tracing.Render.GanttBar.End` are the same
  times as seconds after the trace began, which is the scale a chart is drawn on. A running timespan ends at the
  layout's current time.
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

The renderer draws it. :meth:`~pyTooling.Tracing.Render.Renderer.Write` writes the chart to a file, in the format
the suffix names, and :meth:`~pyTooling.Tracing.Render.Renderer.Render` returns the backend's own object for further
changes - :class:`~pyTooling.Tracing.Render.Matplotlib.MatplotlibRenderer` a :class:`~matplotlib.figure.Figure`,
which isn't registered with :mod:`~matplotlib.pyplot`, so no display is needed. It writes SVG, PNG and PDF, and
matplotlib is an optional dependency, installed by the extra ``pyTooling[diagram]``.

What no drawing library decides is decided once, on the base-class: the color of every category
(:meth:`~pyTooling.Tracing.Render.Renderer.Color`), the chart's title, and the texts of the legend
(:meth:`~pyTooling.Tracing.Render.Renderer.LegendTitle` and
:meth:`~pyTooling.Tracing.Render.Renderer.LegendLabel`). A renderer for another backend derives from
:class:`~pyTooling.Tracing.Render.Renderer`, names the file formats it writes in
:attr:`~pyTooling.Tracing.Render.Renderer.FORMATS`, and implements two methods:
:meth:`~pyTooling.Tracing.Render.Renderer.Render` and ``_Write``.

In an SVG file, every bar or line is a group with the identifier ``span-<SpanID>``, a waiting bar
``span-<SpanID>-queued`` and the end marks of a line ``span-<SpanID>-ends``. Together with
:attr:`~pyTooling.Tracing.Render.GanttRow.ParentSpanID`, a script can find all elements below a called workflow.
