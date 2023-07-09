ArgParse
########

Many people use Python's :mod:`argparse` command line argument parser. This parser
can handle sub-commands like ``git commit -m "message"`` where *commit* is a
sub-command and ``-m <message>`` is an argument of this sub-command parser. It's
possible to assign a callback function to each individual sub-command parser.

.. rubric:: Advantages

* Declarative description instead of imperative form.
* All options from argparse can be used.
* Declare accepted command-line arguments close to the responsible handler method
* Complex parsers can be distributed accross multiple classes and merged via multiple inheritance.
* Pre-defined argument templates like switch parameters (``--help``).


Classic ``argparse`` Example
****************************

.. literalinclude:: ../tests/example/OldStyle.py
   :language: python
   :linenos:
   :caption: tests/example/OldStyle.py
   :tab-width: 2


New ``pyAttributes`` Approach
*****************************

A better and more descriptive solution could look like this:

.. literalinclude:: ../tests/example/UserManager.py
   :language: python
   :linenos:
   :caption: tests/example/UserManager.py
   :tab-width: 2
