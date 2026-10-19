.. _COMMON/Timeout:

Timeout
#######

A :class:`~pyTooling.Timeout.Timeout` limits how long the code in a :ref:`with-statement <with>` may run. Entering the
context makes it the **current timeout of the calling thread** - as a :class:`~pyTooling.Warning.WarningCollector` is
made the current collector - so code anywhere below in the call hierarchy asks for the time left, without the timeout
being passed along as a parameter.

.. code-block:: Python

   from pyTooling.Timeout import Timeout, TimeoutExpiredError

   with Timeout(20.0):
     for package in packages:
       if Timeout.IsExpired():
         raise TimeoutExpiredError("Scanning the dependencies took longer than 20 seconds.", seconds=20.0)

       response = session.get(package.URL, timeout=Timeout.Remaining())

.. important::

   The timeout is **cooperative**. Python can't stop a running thread from outside, so nothing interrupts the code in
   the ``with`` block when the deadline passes. A timeout takes effect where the code checks it - a loop aborting
   itself when :meth:`~pyTooling.Timeout.Timeout.IsExpired` turns ``True`` - and where the time left is handed to a
   blocking call as its own timeout.


.. _COMMON/Timeout/Asking:

Asking for the Time Left
************************

Three classmethods answer for the current timeout of the calling thread:

:meth:`~pyTooling.Timeout.Timeout.Remaining`
  The seconds left as a :class:`float`, ``0.0`` once the timeout expired, and ``None`` when no timeout is current.

:meth:`~pyTooling.Timeout.Timeout.IsExpired`
  ``True`` once the timeout expired; ``False`` before, and when no timeout is current.

:meth:`~pyTooling.Timeout.Timeout.Current`
  The current timeout itself - like :func:`threading.current_thread` returns the thread - or ``None``. Its
  :attr:`~pyTooling.Timeout.Timeout.Seconds` and :attr:`~pyTooling.Timeout.Timeout.Parent` tell how it was set up.

A timeout is entered once at a time: entering it again inside its own ``with`` block raises
:exc:`~pyTooling.Timeout.TimeoutUsageError`. After its block, it can be entered again.

The time left is what a blocking call gets as its own timeout - a request (``requests``: ``timeout=``, ``aiohttp``:
``ClientTimeout(total=...)``), :meth:`threading.Thread.join`, :meth:`concurrent.futures.Future.result`,
:func:`asyncio.timeout` or :func:`asyncio.wait_for`. A loop checks :meth:`~pyTooling.Timeout.Timeout.IsExpired` and
aborts itself by raising :exc:`~pyTooling.Timeout.TimeoutExpiredError`, which is a :exc:`TimeoutError` too.

The time runs from entering the context; the deadline is a :func:`time.monotonic` value, so a change of the system's
clock doesn't shorten or extend it.


.. _COMMON/Timeout/Nesting:

Nesting
*******

A timeout entered while another one is current can only **shorten** the time left, never extend it: its deadline is
the earlier of its own and the outer one's. Leaving the inner context makes the outer timeout current again.

.. code-block:: Python

   with Timeout(20.0):        # the whole dependency scan
     with Timeout(5.0):       # one package: at most 5 seconds, and never beyond the 20
       ...
     with Timeout(60.0):      # still ends with the outer 20 seconds
       ...


.. _COMMON/Timeout/Threads:

Threads and Tasks
*****************

The current timeout is stored per thread.

* :mod:`asyncio` tasks run in the thread of their event loop, so they see the timeout of that thread.
* A new thread starts **without** a current timeout. Hand the time left over to it: wait for it no longer than the
  time left, or let it enter a timeout of its own with the seconds read before starting it.

.. code-block:: Python

   from threading import Thread

   def worker(remaining: float) -> None:
     with Timeout(remaining):
       ...

   with Timeout(20.0):
     thread = Thread(target=worker, args=(Timeout.Remaining(), ))
     thread.start()
     thread.join(timeout=Timeout.Remaining())
