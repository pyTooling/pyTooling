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
      * Activity, inactivity and total duration are available at any time, also while the stopwatch runs - in seconds
        or in whole nanoseconds.
      * The stopwatch reports its state via four read-only properties.
      * Individual time spans can be excluded from the measurement.
      * The stopwatch is a :ref:`context manager <context-managers>`, and can pause or stop when the block ends.
      * Absolute start and stop times are recorded via :meth:`~datetime.datetime.now`, next to the monotonic
        measurement via :func:`time.perf_counter_ns`.
      * The rendered resolution is configurable, and a format specification renders the duration as hours, minutes and
        seconds, or wholly in seconds, milliseconds, microseconds or nanoseconds.
      * Durations are returned as :class:`~pyTooling.Stopwatch.Duration`, a :class:`~datetime.timedelta` resolving
        nanoseconds and accepting the same format specification.

   .. grid-item::
      :columns: 6

      .. condensed-class:: pyTooling.Stopwatch.Stopwatch


.. _COMMON/Stopwatch/RejectedFeatures:

Out of Scope
============

* **Restarting or resetting.** A stopwatch measures one time span in its lifetime. Create a new stopwatch instead of
  reusing a stopped one (:ref:`example <COMMON/Stopwatch/StartStop/Again>`).
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


.. _COMMON/Stopwatch/StartStop/Again:

Measuring Again
---------------

A stopped stopwatch can't be restarted or reset. Its results stay readable, and a new stopwatch takes the next
measurement:

.. code-block:: python

   durations = []
   for file in files:
     sw = Stopwatch(file.name, started=True)
     parse(file)
     durations.append(sw.Stop())

To add several regions up into **one** measurement instead, pause and resume the same stopwatch
(:ref:`COMMON/Stopwatch/PauseResume`), or create it with ``preferPause=True`` and measure each region in a
``with``-block (:ref:`COMMON/Stopwatch/ContextManager`).


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
   sw.Activity       # Duration(microseconds=300000)
   sw.Inactivity     # Duration(microseconds=200000)
   sw.Duration       # Duration(nanoseconds=500083104)

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


.. _COMMON/Stopwatch/Durations:

The Three Durations
===================

:attr:`~pyTooling.Stopwatch.Stopwatch.Duration` is the measurement as a :class:`~pyTooling.Stopwatch.Duration`, which
is a :class:`~datetime.timedelta` resolving nanoseconds (:ref:`COMMON/Stopwatch/Duration`).
:attr:`~pyTooling.Stopwatch.Stopwatch.DurationInSeconds` is the same measurement in **seconds**, as a :class:`float`,
and :attr:`~pyTooling.Stopwatch.Stopwatch.DurationInNanoseconds` in **whole nanoseconds**, as an :class:`int` - which
is how :func:`time.perf_counter_ns` took it in the first place.

.. code-block:: python

   sw.Duration               # Duration(nanoseconds=250294020)
   print(sw.Duration)        # 0:00:00.250294020
   sw.DurationInSeconds      # 0.250294020
   sw.DurationInNanoseconds  # 250294020

All three answer for the whole measurement: start to stop, or start to now while the stopwatch runs, and zero when it
was never started. A data model stores the :class:`~pyTooling.Stopwatch.Duration`: it prints and formats as hours,
minutes and seconds, compares and calculates to the nanosecond, and
:meth:`~pyTooling.Stopwatch.Duration.total_seconds` still gives the number. A stopped stopwatch computes it once. Reach
for the numbers where a number is needed. :attr:`~pyTooling.Stopwatch.Stopwatch.Activity` and
:attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity` follow the same scheme, with
:attr:`~pyTooling.Stopwatch.Stopwatch.ActivityInSeconds` and :attr:`~pyTooling.Stopwatch.Stopwatch.InactivityInSeconds`.

.. note::

   :attr:`~pyTooling.Stopwatch.Stopwatch.Activity` and :attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity` are built
   from their float seconds, so they resolve **microseconds**.

.. note::

   Precision is not what separates the two numbers. A :class:`float` holds a duration in seconds exactly, to the
   nanosecond, up to :math:`2^{53}` nanoseconds - a little over 104 days - so at any length a stopwatch measures the two
   are interchangeable, and ``DurationInNanoseconds / 1e9`` equals
   :attr:`~pyTooling.Stopwatch.Stopwatch.DurationInSeconds` exactly.


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

   Formatting works from :attr:`~pyTooling.Stopwatch.Stopwatch.DurationInNanoseconds`, because dividing a duration
   into fields wants a whole number of them. Not for precision - see
   :ref:`the two durations <COMMON/Stopwatch/Durations>`.


.. _COMMON/Stopwatch/Duration:

Duration
========

:class:`~pyTooling.Stopwatch.Duration` is a :class:`~datetime.timedelta` resolving **nanoseconds**, with a
:meth:`~pyTooling.Stopwatch.Duration.__format__` method, so the :ref:`format specification <COMMON/Stopwatch/Format>`
of a stopwatch works on a stored duration too. :attr:`~pyTooling.Stopwatch.Stopwatch.Duration`,
:attr:`~pyTooling.Stopwatch.Stopwatch.Activity` and :attr:`~pyTooling.Stopwatch.Stopwatch.Inactivity` return one.

It takes the constructor parameters of :class:`~datetime.timedelta` plus ``nanoseconds``; all of them are added up. An
existing :class:`~datetime.timedelta` is converted by :meth:`~pyTooling.Stopwatch.Duration.FromTimedelta`.

.. rubric:: Usage

.. code-block:: python

   from datetime import timedelta
   from pyTooling.Stopwatch import Duration

   duration = Duration(hours=26, minutes=3, seconds=4, nanoseconds=123456789)
   print(f"{duration:%H:%M:%S.%N}")

   duration = Duration.FromTimedelta(timedelta(minutes=-1, seconds=-30))
   print(f"{duration:%M:%S}")

.. rubric:: Result

.. code-block::

   26:03:04.123456789
   -01:30

The specifiers are those of :meth:`Stopwatch.__format__ <pyTooling.Stopwatch.Stopwatch.__format__>`. A duration can
be negative: the fields are those of the absolute value, with a ``-`` in front of the first placeholder: ``took %s s``
renders ``took -5 s``.

Components
----------

Like a :class:`~datetime.timedelta`, a duration is normalized into components. ``nanoseconds`` is a fourth component
beside the three of :class:`~datetime.timedelta`; :attr:`~datetime.timedelta.microseconds` stays
``nanoseconds // 1000``, so code written for :class:`~datetime.timedelta` sees the duration truncated to microseconds.

+-------------------------------------------------------+----------------+-------------------------------------------+
| Component                                             | Range          | Note                                      |
+=======================================================+================+===========================================+
| :attr:`~datetime.timedelta.days`                      | any            | the only component with a sign            |
+-------------------------------------------------------+----------------+-------------------------------------------+
| :attr:`~datetime.timedelta.seconds`                   | 0 .. 86399     |                                           |
+-------------------------------------------------------+----------------+-------------------------------------------+
| :attr:`~datetime.timedelta.microseconds`              | 0 .. 999999    | ``nanoseconds // 1000``                   |
+-------------------------------------------------------+----------------+-------------------------------------------+
| :attr:`~pyTooling.Stopwatch.Duration.nanoseconds`     | 0 .. 999999999 | the sub-second part at full resolution    |
+-------------------------------------------------------+----------------+-------------------------------------------+

:meth:`~pyTooling.Stopwatch.Duration.total_nanoseconds` returns the whole duration in nanoseconds, as
:meth:`~datetime.timedelta.total_seconds` does in seconds. ``Duration(nanoseconds=-1)`` is ``days=-1``,
``seconds=86399``, ``nanoseconds=999999999``.

Arithmetic and Comparisons
--------------------------

Arithmetic and comparisons involving a duration calculate in nanoseconds; a :class:`~datetime.timedelta` operand on
either side is converted. A result that :class:`~datetime.timedelta` returns as a time delta is a duration: ``+``,
``-``, unary ``-``/``+``, ``abs()``, ``*`` and ``/`` by a number (rounded half to even, like
:class:`~datetime.timedelta`), ``//`` by an integer, ``%`` and the remainder of ``divmod()``. ``datetime + duration``
stays the arithmetic of :class:`~datetime.datetime`, which resolves microseconds.

.. code-block:: python

   total = sw1.Duration + sw2.Duration
   print(f"{total:%H:%M:%S.%N}")

.. attention::

   Comparing a duration with something else than a :class:`~datetime.timedelta` raises a :exc:`TypeError`, also for
   ``==``: ``duration == 0`` is an error, not ``False``.


.. _COMMON/Stopwatch/Competitors:

Competing Solutions
*******************

The timers below measure one time span from a start to a stop. This stopwatch also keeps every split time and whether
it was active, so it reports activity and inactivity separately, and it excludes a time span by a nested
``with``-statement.

.. _COMMON/Stopwatch/stdlib:

Standard Library
================

Source: :func:`time.perf_counter_ns`, :mod:`timeit`.

.. rubric:: Disadvantages

* :func:`time.perf_counter_ns` is a counter: the caller subtracts the values, and keeps and formats them.
* :mod:`timeit` runs a statement many times and reports the result, so it measures a snippet, not a part of a running
  program.

.. rubric:: Standoff

* This stopwatch measures with :func:`time.perf_counter_ns` too.

.. rubric:: Advantages

* No dependency; :mod:`timeit` repeats a measurement and has a command line interface for micro benchmarks.

.. _COMMON/Stopwatch/codetiming:

codetiming
==========

Source: `codetiming <https://pypi.org/project/codetiming/>`__ 1.4.0, released 2022-11-08.

.. rubric:: Disadvantages

* A timer measures from ``start()`` to ``stop()``; there is no pause, no split time and no excluded time span.
* A timer is started again for every measurement, so one measurement can't be interrupted and continued.

.. rubric:: Standoff

* Like this stopwatch, it is used as an object with explicit calls or in a ``with``-statement.

.. rubric:: Advantages

* A timer is also a decorator.
* Measurements of timers with the same name accumulate in ``Timer.timers``, with their count, total, minimum, maximum,
  mean, median and standard deviation.
* The elapsed time is reported to a logger, with a configurable text.

.. _COMMON/Stopwatch/stopwatch.py:

stopwatch.py
============

Source: :gh:`stopwatch.py <ravener/stopwatch.py>`, on PyPI as
`stopwatch.py <https://pypi.org/project/stopwatch.py/>`__ 2.0.1, released 2022-09-04.

.. rubric:: Disadvantages

* No split times, so the time a stopwatch was stopped in between isn't reported.
* No ``with``-statement, no name, and no absolute start or stop time.

.. rubric:: Standoff

* Stopping and starting again continues the measurement, like :meth:`~pyTooling.Stopwatch.Stopwatch.Pause` and
  :meth:`~pyTooling.Stopwatch.Stopwatch.Resume`.
* :func:`str` renders the duration with a configurable number of digits.

.. rubric:: Advantages

* A stopwatch can be reset and restarted, which this stopwatch leaves out of scope.

.. _COMMON/Stopwatch/pytictoc:

pytictoc
========

Source: :gh:`pytictoc <ericcfields/pytictoc>`, on PyPI as `pytictoc <https://pypi.org/project/pytictoc/>`__ 1.5.3,
released 2023-08-02.

.. rubric:: Disadvantages

* ``toc()`` prints the time since the last ``tic()``. A lap is taken by restarting the timer, and only the latest
  elapsed time is kept.
* No pause, and the ``with``-statement prints the time but doesn't return the timer.

.. rubric:: Advantages

* MATLAB's ``tic`` and ``toc``, for code ported from MATLAB.
