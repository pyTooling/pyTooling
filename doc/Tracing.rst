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


.. _TRACING/OTLP/Import:

OTLP/JSON Import
################

A :class:`~pyTooling.Tracing.Trace` reads itself back from an OTLP/JSON document, so a trace written by one process
- a build step, a worker, an earlier run - can be inspected, formatted or merged by another.

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
     - a parameter of :meth:`~pyTooling.Tracing.Trace.ToJSON`, not a field of the data model
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
