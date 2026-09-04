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
