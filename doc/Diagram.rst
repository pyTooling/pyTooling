.. _DIAGRAM:

Overview
########

:mod:`pyTooling.Diagram` describes diagrams; it doesn't draw them. A diagram is a small data model - what the
picture *is* - and a renderer turns that model into a picture with whatever library is at hand. Producers and
renderers therefore don't have to know each other: a producer builds the model its own data implies, and every
renderer draws the same model.


.. _DIAGRAM/Gantt:

Gantt Charts
############

:mod:`pyTooling.Diagram.Gantt` describes a **Gantt chart**: rows of bars on a time scale.

.. code-block:: python

   from datetime import datetime, timedelta
   from pyTooling.Diagram.Gantt import Diagram, Row, Bar

   begin =   datetime(2026, 9, 15, 8, 0)
   diagram = Diagram("Nightly build", begin)

   compile = Row("Compile", parent=diagram)
   Bar(begin + timedelta(minutes=1), begin + timedelta(minutes=5), parent=compile)

   test = Row("Test", parent=diagram)
   Bar(begin + timedelta(minutes=5), begin + timedelta(minutes=21), parent=test)

Three classes, each one containing the next:

.. list-table::
   :header-rows: 1
   :widths: 24 76

   * - Class
     - Is
   * - :class:`~pyTooling.Diagram.Gantt.Diagram`
     - the chart: its title, its **origin** and its rows.
   * - :class:`~pyTooling.Diagram.Gantt.Row`
     - the bars drawn on one line, under one name.
   * - :class:`~pyTooling.Diagram.Gantt.Bar`
     - a time range within a row.

An element is created **with its parent** and appends itself to it, so the model is built top down and is never
half-attached. Every element knows the diagram it belongs to - :attr:`~pyTooling.Diagram.Gantt.Bar.Diagram` - so
reaching the origin from a bar costs no walk.


.. _DIAGRAM/Gantt/Offsets:

Three ways to ask where a bar is
================================

A chart is drawn on offsets, a report usually wants times, and a comparison within a row wants neither, so a bar
answers all three:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Property
     - Answers
   * - :attr:`~pyTooling.Diagram.Gantt.Bar.Begin`, :attr:`~pyTooling.Diagram.Gantt.Bar.End`
     - the times themselves, as :class:`~datetime.datetime`.
   * - :attr:`~pyTooling.Diagram.Gantt.Bar.BeginSinceOrigin`, :attr:`~pyTooling.Diagram.Gantt.Bar.EndSinceOrigin`
     - the distance from the **diagram's** origin, as :class:`~datetime.timedelta`.
   * - :attr:`~pyTooling.Diagram.Gantt.Bar.BeginSinceParent`, :attr:`~pyTooling.Diagram.Gantt.Bar.EndSinceParent`
     - the distance from the **row's** begin, which is zero for the row's earliest bar.
   * - :attr:`~pyTooling.Diagram.Gantt.Bar.Duration`
     - the bar's own length.

A distance is a :class:`~datetime.timedelta`, because that is what subtracting two times yields. Where a drawing
library wants a number, the ``***InSeconds`` properties -
:attr:`~pyTooling.Diagram.Gantt.Bar.BeginSinceOriginInSeconds`,
:attr:`~pyTooling.Diagram.Gantt.Bar.EndSinceOriginInSeconds` and
:attr:`~pyTooling.Diagram.Gantt.Bar.DurationInSeconds` - hand out :class:`float` seconds instead.

.. hint::

   **The origin is stated, not derived.** The scale a chart is drawn on usually begins before its first bar - a
   pipeline starts before its first job does - so :class:`~pyTooling.Diagram.Gantt.Diagram` takes the origin as a
   parameter rather than taking the earliest bar's begin.

A row spans its bars: it begins with its earliest and ends with its latest, gaps between them included. A row
without bars has neither, and asking raises a :exc:`~pyTooling.Diagram.DiagramError` rather than answering with
``None``.


.. _DIAGRAM/Gantt/Deriving:

Building one from your own data
===============================

A producer derives from the three classes and adds what its domain knows.
:class:`~pyTooling.Tracing.Render.GanttLayout` does exactly that for a software execution trace: its rows carry the
timespan they show and its depth in the trace's tree, and its bars carry whether a job was waiting for a runner and
whether it is still running. See :ref:`TRACING/Render`.

.. seealso::

   :ref:`TRACING/Render`
      |rarr| A software execution trace as a Gantt chart, and the renderers drawing it.
