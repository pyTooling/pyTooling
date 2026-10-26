.. _SCHEMAS/OTLP-Traces-v1.0:

OTLP-Traces v1.0
################

The schema of an **OTLP/JSON document of traces** - ``opentelemetry.proto.trace.v1.TracesData`` in the
`JSON Protobuf Encoding <https://opentelemetry.io/docs/specs/otlp/#json-protobuf-encoding>`__ of the OpenTelemetry
Protocol. :class:`~pyTooling.Tracing.TraceCollection` validates a document against it before reading it, and
:meth:`Trace.WriteOTLPJSONFile() <pyTooling.Tracing.Trace.WriteOTLPJSONFile>` writes documents it accepts.

It states what the encoding requires: lowerCamelCase field names, trace and span identifiers as 32 and 16
hexadecimal digits in either case and never all zeros, an empty ``parentSpanId`` for a root span, enumeration values
as integers, 64-bit integers as decimal strings or numbers, attribute keys that aren't empty, and an ``AnyValue``
naming at most one value. Fields with unknown names are allowed, because an OTLP/JSON receiver ignores them.

What a schema can't state is checked by the reader: two spans or two attributes with the same key, an end before the
start, a timestamp a :class:`~datetime.datetime` can't hold, and spans referencing each other in a cycle.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. admonition:: Download

         :download:`OTLP-Traces-v1.0.schema.json <../../pyTooling/Resources/OTLP-Traces-v1.0.schema.json>`

   .. grid-item::
      :columns: 6

      .. admonition:: Validate a document

         .. code-block:: bash

            check-jsonschema --schemafile OTLP-Traces-v1.0.schema.json Pipeline.otlp.json

.. seealso::

   :ref:`TRACING`
      |rarr| Reading and writing traces as OTLP/JSON.

.. _SCHEMAS/OTLP-Traces-v1.0/Source:

Source
******

.. literalinclude:: ../../pyTooling/Resources/OTLP-Traces-v1.0.schema.json
   :caption: OTLP-Traces-v1.0.schema.json
   :language: json
   :linenos:
   :tab-width: 2
