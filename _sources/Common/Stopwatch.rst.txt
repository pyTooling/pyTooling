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

      Name
        A stopwatch can be named at creation time.

      Starting and stopping
        The stopwatch can be started and stopped. Once stopped, no further start or pause/resume is possible. A
        stopwatch can't be restarted. A new stopwatch object should be created and the old can be destroyed.

        The stopwatch collects the absolute start (begin) and stop (end) times. It then provides a duration from start
        to stop operation.

      Pause and resume
        A stopwatch can be paused and resumed.

      Split times
        tbd

      Iterating split times
        tbd

      Using in a ``with``-statement
        tbd

      State of a stopwatch
        tbd

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         @export
         class Stopwatch(SlottedObject):
           def __init__(self, name: str = None, started: bool = False, preferPause: bool = False) -> None:
             ...

           def __enter__(self) -> "Stopwatch":
             ...

           def __exit__(self, exc_type: Type[Exception], exc_val: Exception, exc_tb: Traceback) -> bool:
             ...

           def Start(self) -> None:
             ...

           def Split(self) -> float:
             ...

           def Pause(self) -> float:
             ...

           def Resume(self) -> float:
             ...

           def Stop(self):
             ...

           @readonly
           def Name(self) -> Nullable[str]:
             ...

           @readonly
           def IsStarted(self) -> bool:
             ...

           @readonly
           def IsRunning(self) -> bool:
             ...

           @readonly
           def IsPaused(self) -> bool:
             ...

           @readonly
           def IsStopped(self) -> bool:
             ...

           @readonly
           def StartTime(self) -> Nullable[datetime]:
             ...

           @readonly
           def StopTime(self) -> Nullable[datetime]:
             ...

           @readonly
           def HasSplitTimes(self) -> bool:
             ...

           @readonly
           def SplitCount(self) -> int:
             ...

           @readonly
           def ActiveCount(self) -> int:
             ...

           @readonly
           def InactiveCount(self) -> int:
             ...

           @readonly
           def Activity(self) -> float:
             ...

           @readonly
           def Inactivity(self) -> float:
             ...

           @readonly
           def Duration(self) -> float:
             ...

           def __len__(self):
             ...

           def __getitem__(self, index: int) -> Tuple[float, bool]:
             ...

           def __iter__(self) -> Iterator[Tuple[float, bool]]:
             ...
