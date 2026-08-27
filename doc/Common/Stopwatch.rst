.. _COMMON/Stopwatch:

Stopwatch
#########

.. #contents:: Table of Contents
   :depth: 1

.. grid:: 2

   .. grid-item::
      :columns: 6

      The stopwatch implements a solution to measure and collect timings: e.g. code execution times or test run times.

      The time measurement can be :meth:`started <pyTooling.Stopwatch.Stopwatch.Start>`, :meth:`paused <pyTooling.Stopwatch.Stopwatch.Pause>`,
      :meth:`resumed <pyTooling.Stopwatch.Stopwatch.Resume>` and :meth:`stopped <pyTooling.Stopwatch.Stopwatch.Stop>`. More
      over, split times can be taken too. The measurement is based on :func:`time.perf_counter_ns`. Additionally, starting and
      stopping is preserved as absolute time via :meth:`datetime.datetime.now`.

      Every split time taken is a time delta to the previous stopwatch operation. These are preserved in an internal sequence
      of splits. This sequence includes time deltas of activity and inactivity. Thus, a running stopwatch can be split as well
      as a paused stopwatch.

      The stopwatch can also be used in a :ref:`with-statement <with>`, because it implements the :ref:`context manager protocol <context-managers>`.


   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Start/Stop

            .. code-block:: Python

               from pyTooling.Stopwatch import Stopwatch

               sw = Stopwatch("my name")
               sw.Start()
               # do something
               sw.Stop()

               sw = Stopwatch("other name", started=True)
               # do something
               sw.Stop()

         .. tab-item:: Start/Pause/Resume/Stop

            .. code-block:: Python

               from pyTooling.Stopwatch import Stopwatch

               sw = Stopwatch("my name")
               sw.Start()
               # do something
               sw.Pause()
               # do something other
               sw.Resume()
               # do something again
               sw.Stop()

         .. tab-item:: Using with-statement

            .. code-block:: Python

               from pyTooling.Stopwatch import Stopwatch

               sw = Stopwatch("my name", preferPause=True)
               with sw:
                 # do something

               # do something other

               with sw
                 # do something again


.. _COMMON/Stopwatch/Features:

Features
********

.. grid:: 2

   .. grid-item::
      :columns: 6

      * A stopwatch can be named at creation time.
      * The measurement can be started, paused, resumed and stopped.
      * Split times can be taken while the stopwatch runs.
      * Every split time is preserved, together with whether it measured activity or inactivity.
      * The split times can be iterated, indexed and counted.
      * Activity, inactivity and total duration are available at any time, also while the stopwatch runs.
      * The stopwatch reports its state via four read-only properties.
      * Individual time spans can be excluded from the measurement.
      * The stopwatch is a :ref:`context manager <context-managers>`, and can pause or stop when the block ends.
      * Absolute start and stop times are recorded via :meth:`~datetime.datetime.now`, next to the monotonic
        measurement via :func:`time.perf_counter_ns`.
      * The rendered resolution is configurable, and a format specification renders the duration as hours, minutes and
        seconds, or wholly in seconds, milliseconds, microseconds or nanoseconds.

   .. grid-item::
      :columns: 6

      .. condensed-class:: pyTooling.Stopwatch.Stopwatch


.. _COMMON/Stopwatch/RejectedFeatures:

Out of Scope
============

* **Restarting or resetting.** A stopwatch measures one time span in its lifetime. Create a new stopwatch instead of
  reusing a stopped one.
* **Nesting.** A stopwatch measures one thing. Use one stopwatch per measured thing.
* **Thread-safety.** Two threads operating one stopwatch will interleave their splits.


.. _COMMON/Stopwatch/ByFeature:

By Feature
**********

.. _COMMON/Stopwatch/Name:

Name
====

A stopwatch can be named at creation time, and the name is then a read-only property
:attr:`~pyTooling.Stopwatch.Stopwatch.Name`. The name is optional and defaults to ``None``. It appears in the
stopwatch's string representation, which is what makes a name worth giving when several measurements are printed
together.

.. code-block:: python

   # Create a named stopwatch
   sw = Stopwatch("parsing")

   # Read the name back
   name = sw.Name


.. _COMMON/Stopwatch/StartStop:

Starting and Stopping
=====================

A stopwatch is started either by :meth:`~pyTooling.Stopwatch.Stopwatch.Start` or by passing ``started=True`` to the
constructor. :meth:`~pyTooling.Stopwatch.Stopwatch.Stop` ends the measurement and returns the duration since the
previous operation.

A stopwatch can be started **once**. Starting a running stopwatch, starting a stopped one, or stopping one that was
never started each raise a :exc:`~pyTooling.Stopwatch.StopwatchError`.

.. code-block:: python

   # Start explicitly
   sw = Stopwatch("parsing")
   sw.Start()
   # do something
   duration = sw.Stop()

   # ... or start at creation time
   sw = Stopwatch("parsing", started=True)
   # do something
   duration = sw.Stop()

Besides the monotonic measurement, the absolute times are recorded too, and are available as
:attr:`~pyTooling.Stopwatch.Stopwatch.StartTime` and :attr:`~pyTooling.Stopwatch.Stopwatch.StopTime`. Both are ``None``
until the respective operation happened.

.. code-block:: python

   print(f"{sw.StartTime} -> {sw.StopTime}")


.. _COMMON/Stopwatch/PauseResume:

Pause and Resume
================

A running stopwatch can be paused with :meth:`~pyTooling.Stopwatch.Stopwatch.Pause` and continued with
:meth:`~pyTooling.Stopwatch.Stopwatch.Resume`. Both return the duration of the span that just ended, so a pause/resume
pair tells you both how long the work took and how long the interruption lasted.

Pausing a stopwatch that isn't running, or resuming one that isn't paused, raises a
:exc:`~pyTooling.Stopwatch.StopwatchError`.

.. code-block:: python

   sw = Stopwatch("parsing", started=True)
   # do something
   worked = sw.Pause()
   # do something that shouldn't be measured
   waited = sw.Resume()
   # do something again
   sw.Stop()

The paused span is not lost - it is recorded as an *inactive* split time, and shows up in
:attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity`. A stopwatch accounts for the whole span from start to stop; it never
silently drops time.


.. _COMMON/Stopwatch/Splits:

Split Times
===========

:meth:`~pyTooling.Stopwatch.Stopwatch.Split` takes a split time while the stopwatch runs and returns the duration since
the previous operation. Splitting a stopwatch that isn't running raises a
:exc:`~pyTooling.Stopwatch.StopwatchError`.

Split times are not a separate list of marks - **every** operation that ends a span records one. So
:meth:`~pyTooling.Stopwatch.Stopwatch.Split`, :meth:`~pyTooling.Stopwatch.Stopwatch.Pause`,
:meth:`~pyTooling.Stopwatch.Stopwatch.Resume` and :meth:`~pyTooling.Stopwatch.Stopwatch.Stop` all append one, and each
carries whether the span it measured was activity or inactivity:

+-------------------------------+--------------------------+------------+
| Span                          | Ended by                 | Records    |
+===============================+==========================+============+
| start ⟶ split, resume ⟶ split | ``Split()``              | activity   |
+-------------------------------+--------------------------+------------+
| start ⟶ pause, resume ⟶ pause | ``Pause()``              | activity   |
+-------------------------------+--------------------------+------------+
| pause ⟶ resume                | ``Resume()``             | inactivity |
+-------------------------------+--------------------------+------------+
| resume ⟶ stop                 | ``Stop()`` while running | activity   |
+-------------------------------+--------------------------+------------+
| pause ⟶ stop                  | ``Stop()`` while paused  | inactivity |
+-------------------------------+--------------------------+------------+

.. important::

   A stopwatch that was never paused and never split records **no** split times at all - not even for the one span
   from start to stop. :meth:`~pyTooling.Stopwatch.Stopwatch.Stop` still *returns* that duration, and
   :attr:`~pyTooling.Stopwatch.Stopwatch.Duration` still reports it, but there is nothing to iterate.

   That is the distinction between the two kinds of result. :attr:`~pyTooling.Stopwatch.Stopwatch.Duration` always
   describes the **measurement**: start to stop, whatever happened in between. The split times, and therefore
   :attr:`~pyTooling.Stopwatch.Stopwatch.Activity` and :attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity`, describe
   only the spans that were actually recorded, and are ``0.0`` when none were.

Once split times exist they are consecutive and cover the whole measurement, so they add up: the active spans sum to
:attr:`~pyTooling.Stopwatch.Stopwatch.Activity`, the inactive ones to
:attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity`, and together they are
:attr:`~pyTooling.Stopwatch.Stopwatch.Duration`.

.. rubric:: Example

.. code-block:: python

   sw = Stopwatch("parsing", started=True)
   sleep(0.1); sw.Split()
   sleep(0.1); sw.Pause()
   sleep(0.2); sw.Resume()
   sleep(0.1); sw.Stop()

records four spans:

.. code-block::

    Start      Split      Pause              Resume       Stop
      │          │          │                  │            │
      ├──active──┼──active──┼─────inactive─────┼───active───┤
      │  0.1 s   │  0.1 s   │      0.2 s       │   0.1 s    │
     0.0        0.1        0.2                0.4          0.5  s

.. code-block:: python

   sw.SplitCount     # 4
   sw.ActiveCount    # 3
   sw.InactiveCount  # 1
   sw.Activity       # 0.3
   sw.Inactivity     # 0.2
   sw.Duration       # 0.5

:attr:`~pyTooling.Stopwatch.Stopwatch.HasSplitTimes` reports whether at least one split time was recorded, and
:attr:`~pyTooling.Stopwatch.Stopwatch.SplitCount` how many.

.. note::

   The counts and the durations describe the same spans, including the one that hasn't ended yet.
   :attr:`~pyTooling.Stopwatch.Stopwatch.ActiveCount` and :attr:`~pyTooling.Stopwatch.Stopwatch.InactiveCount`
   answer *"what would the stopwatch report if it stopped right now"*: a running stopwatch is inside an active span,
   so that span is counted, and a paused one is inside an inactive span.

   That keeps them consistent with :attr:`~pyTooling.Stopwatch.Stopwatch.Activity` and
   :attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity`, which have always included the span in progress.

   +---------+-----------------------------------------+
   | State   | The span in progress                    |
   +=========+=========================================+
   | running | counts towards ``ActiveCount``          |
   +---------+-----------------------------------------+
   | paused  | counts towards ``InactiveCount``        |
   +---------+-----------------------------------------+
   | stopped | there is none - every span was recorded |
   +---------+-----------------------------------------+


.. _COMMON/Stopwatch/Iterating:

Iterating Split Times
=====================

The recorded split times are reachable as a sequence: :meth:`~pyTooling.Stopwatch.Stopwatch.__iter__` iterates them,
:meth:`~pyTooling.Stopwatch.Stopwatch.__getitem__` indexes them, and :meth:`~pyTooling.Stopwatch.Stopwatch.__len__`
counts them - the same number as :attr:`~pyTooling.Stopwatch.Stopwatch.SplitCount`.

Each item is a tuple of the span's duration in seconds and a boolean saying whether it was activity:

.. rubric:: Usage

.. code-block:: python

   for duration, isActive in sw:
     print(f"{duration:.3f} s {'running' if isActive else 'paused'}")

.. rubric:: Result

.. code-block::

   0.100 s running
   0.100 s running
   0.200 s paused
   0.100 s running

.. code-block:: python

   # The i-th span
   duration, isActive = sw[0]

   # The last span
   duration, isActive = sw[-1]

   # How many spans
   count = len(sw)


.. _COMMON/Stopwatch/Exclude:

Excluding Time Spans
====================

Sometimes a measured region contains work that shouldn't count - reading a fixture from disk inside a benchmark, or
waiting for a user. :attr:`~pyTooling.Stopwatch.Stopwatch.Exclude` returns a context manager that pauses the stopwatch
when the block is entered and resumes it when the block ends.

It is the mirror image of using the stopwatch itself as a context manager, and it needs a running stopwatch - the
excluded block is recorded as an ordinary inactive span.

.. rubric:: Usage

.. code-block:: python

   sw = Stopwatch("benchmark", started=True)
   for case in cases:
     with sw.Exclude:
       data = loadFixture(case)   # not measured

     process(data)                # measured

   sw.Stop()

.. rubric:: Result

.. code-block:: python

   sw.Activity    # only the process(...) calls
   sw.Inactivity  # only the loadFixture(...) calls

The same context manager object is returned on every access, so it can be used as often as needed.


.. _COMMON/Stopwatch/ContextManager:

Using in a ``with``-statement
=============================

A stopwatch implements the :ref:`context manager protocol <context-managers>`, so a measured region can be written as a
``with``-block. Entering starts an unstarted stopwatch and resumes a paused one; leaving stops it, or pauses it when
the stopwatch was created with ``preferPause=True``.

Entering a running or an already stopped stopwatch raises a :exc:`~pyTooling.Stopwatch.StopwatchError`.

.. tab-set::

   .. tab-item:: Measure one region

      With the default behaviour the block both starts and stops the measurement:

      .. code-block:: python

         with Stopwatch("parsing") as sw:
           # do something

         print(sw.Duration)

   .. tab-item:: Measure several regions

      With ``preferPause=True`` the block pauses instead of stopping, so the same stopwatch can measure several
      regions and accumulate their durations. It has to be stopped explicitly at the end:

      .. code-block:: python

         sw = Stopwatch("parsing", preferPause=True)

         for file in files:
           with sw:
             parse(file)          # measured

           report(file)           # not measured

         sw.Stop()

         print(sw.Activity)       # time spent parsing
         print(sw.Inactivity)     # time spent reporting

.. note::

   ``preferPause=True`` is the inverse of :attr:`~pyTooling.Stopwatch.Stopwatch.Exclude`: the first measures what is
   *inside* the blocks, the second measures what is *outside* them. Which to reach for depends on whether the
   interesting work or the uninteresting work is the part that repeats.


.. _COMMON/Stopwatch/State:

State of a Stopwatch
====================

A stopwatch reports its state through four read-only properties. They are not independent - the table shows the state
after each operation:

.. list-table::
   :header-rows: 1
   :widths: 16 21 21 21 21

   * - After
     - :attr:`~pyTooling.Stopwatch.Stopwatch.IsStarted`
     - :attr:`~pyTooling.Stopwatch.Stopwatch.IsRunning`
     - :attr:`~pyTooling.Stopwatch.Stopwatch.IsPaused`
     - :attr:`~pyTooling.Stopwatch.Stopwatch.IsStopped`
   * - creation
     - ``False``
     - ``False``
     - ``False``
     - ``False``
   * - ``Start()``
     - ``True``
     - ``True``
     - ``False``
     - ``False``
   * - ``Pause()``
     - ``True``
     - ``False``
     - ``True``
     - ``False``
   * - ``Resume()``
     - ``True``
     - ``True``
     - ``False``
     - ``False``
   * - ``Stop()``
     - ``False``
     - ``False``
     - ``False``
     - ``True``

.. attention::

   :attr:`~pyTooling.Stopwatch.Stopwatch.IsStarted` means *"is started and not yet stopped"*, so it turns ``False``
   again when the stopwatch is stopped. To ask whether a stopwatch was ever started, use
   ``sw.IsStarted or sw.IsStopped``.

Each operation is only valid in some of these states, and raises a :exc:`~pyTooling.Stopwatch.StopwatchError`
otherwise. Testing the state first is how a stopwatch is driven from code that doesn't know its history:

.. code-block:: python

   if sw.IsRunning:
     sw.Pause()
   elif sw.IsPaused:
     sw.Resume()


.. _COMMON/Stopwatch/Formatting:

Formatting
==========

:meth:`~pyTooling.Stopwatch.Stopwatch.__str__` renders the stopwatch's state and the duration it measured so far,
including the name if one was given. The duration is always in **seconds**, at the same resolution in every state, so
a running and a stopped stopwatch can be compared without converting anything.

.. rubric:: Usage

.. code-block:: python

   sw = Stopwatch("parsing")
   print(sw)

   sw.Start()
   print(sw)

   sw.Stop()
   print(sw)

.. rubric:: Result

.. code-block::

   Stopwatch parsing: not started
   Stopwatch parsing (running): 2026-08-27 15:50:12.150982 -> now: 0.500
   Stopwatch parsing (stopped): 2026-08-27 15:50:12.150982 -> 2026-08-27 15:50:12.651257: 0.500


.. _COMMON/Stopwatch/Digits:

Resolution
==========

How many fractional digits that duration is rendered with is set by :attr:`~pyTooling.Stopwatch.Stopwatch.Digits`. It
defaults to ``3`` - milliseconds - and can be given at creation time or changed at any point, because it only decides
how the measurement is *displayed*.

.. code-block:: python

   # Give it at creation time
   sw = Stopwatch("parsing", digits=6)

   # ... or change it later
   sw.Digits = 9

A value outside ``0`` to ``9`` raises a :exc:`ValueError`, since a duration in seconds has no more than nine
fractional digits to show - that is the resolution of the underlying :func:`time.perf_counter_ns`.

.. code-block:: python

   sw.Digits = 6
   print(sw)

.. code-block::

   Stopwatch parsing (stopped): 2026-08-27 15:50:12.150982 -> 2026-08-27 15:50:12.651257: 0.500269


.. _COMMON/Stopwatch/Format:

Format Specification
====================

Seconds are the right unit for a benchmark and the wrong one for a test run that lasted an hour. Python has no format
specification for durations - :class:`~datetime.timedelta` doesn't implement ``__format__`` at all, and
:func:`time.strftime` formats a point in time rather than a length of one - so the stopwatch brings its own, in the
same ``%``-placeholder style as :meth:`pyTooling.Versioning.SemanticVersion.__format__`.

An **uppercase** specifier is a field of the duration as it would be displayed. A **lowercase** specifier is the whole
duration expressed in one unit, which is what a report or a comparison wants.

+-----------+--------------------------------------------------------+
| Specifier | Meaning                                                |
+===========+========================================================+
| ``%H``    | hours, not capped - a 26 hour measurement shows ``26`` |
+-----------+--------------------------------------------------------+
| ``%M``    | minutes, ``00`` to ``59``                              |
+-----------+--------------------------------------------------------+
| ``%S``    | seconds, ``00`` to ``59``                              |
+-----------+--------------------------------------------------------+
| ``%L``    | fractional seconds, 3 digits (milliseconds)            |
+-----------+--------------------------------------------------------+
| ``%U``    | fractional seconds, 6 digits (microseconds)            |
+-----------+--------------------------------------------------------+
| ``%N``    | fractional seconds, 9 digits (nanoseconds)             |
+-----------+--------------------------------------------------------+
| ``%s``    | the whole duration in seconds                          |
+-----------+--------------------------------------------------------+
| ``%m``    | the whole duration in milliseconds                     |
+-----------+--------------------------------------------------------+
| ``%u``    | the whole duration in microseconds                     |
+-----------+--------------------------------------------------------+
| ``%n``    | the whole duration in nanoseconds                      |
+-----------+--------------------------------------------------------+

``%%`` renders a literal percent sign, an empty specification falls back to
:meth:`~pyTooling.Stopwatch.Stopwatch.__str__`, and an unknown placeholder raises a :exc:`ValueError`.

.. rubric:: Usage

For a stopwatch that measured 26 hours, 3 minutes and 4.123456789 seconds:

.. code-block:: python

   print(f"{sw:%H:%M:%S}")
   print(f"{sw:%H:%M:%S.%L}")
   print(f"{sw:%H:%M:%S.%U}")
   print(f"{sw:%M:%S.%L}")
   print(f"{sw:%s} s / {sw:%m} ms / {sw:%u} us / {sw:%n} ns")

.. rubric:: Result

.. code-block::

   26:03:04
   26:03:04.123
   26:03:04.123456
   03:04.123
   93784 s / 93784123 ms / 93784123456 us / 93784123456789 ns

.. note::

   The three fractional specifiers render the **same** fraction at three precisions rather than three consecutive
   thirds of it, so ``%S.%U`` is complete on its own and nothing has to be chained.

   ``%H`` deliberately isn't capped at 23. There is no day specifier - a stopwatch measures code execution, so
   ``%H:%M:%S`` is the longest form anyone needs - and capping it would make a 26 hour measurement silently render as
   ``02:03:04``.

   Formatting works from the measured nanoseconds rather than from
   :attr:`~pyTooling.Stopwatch.Stopwatch.Duration`, because splitting a duration into fields wants whole nanoseconds
   and :attr:`~pyTooling.Stopwatch.Stopwatch.Duration` offers seconds as a float. Not for precision: a float holds a
   duration in seconds exactly, to the nanosecond, for a little over 104 days.
