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

.. _TRACING/OTLP:

OTLP/JSON Export
################

:mod:`pyTooling.Tracing.OpenTelemetry` writes a trace as **OTLP/JSON**, the OpenTelemetry Protocol's JSON
encoding. One format reaches both usual destinations: an OpenTelemetry collector accepts OTLP natively, and Jaeger
has accepted it since v1.35 - so no translation step stands between a trace and a viewer.

.. code-block:: python

   from pyTooling.Tracing.OpenTelemetry import WriteOTLP

   WriteOTLP(trace, "trace.json", serviceName="myProgram")

.. code-block:: bash

   curl -X POST -H "Content-Type: application/json" -d @trace.json \
        http://localhost:4318/v1/traces

:func:`~pyTooling.Tracing.OpenTelemetry.ToOTLP` returns the same document as a dictionary, for a caller that posts
it directly rather than writing a file.

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

.. note::

   The identifiers are generated per export, so exporting one trace twice yields two different ``traceId`` values.
   That is enough to view a trace, but not for the distributed case the :class:`~pyTooling.Tracing.Trace`
   documentation describes, where spans recorded by several processes are grouped by a shared identifier. Carrying
   identifiers in the data model - and propagating them between processes - is the step that would enable it.

.. attention::

   An :class:`~pyTooling.Tracing.Event` constructed without an explicit ``time`` carries none, because the
   constructor does not stamp the current time. OTLP has no way to say *unknown* - a missing ``timeUnixNano`` reads
   as the Unix epoch - so the exporter substitutes the enclosing span's start time, which at least places the event
   inside the span it belongs to.
