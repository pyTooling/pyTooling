.. _CLI:

Overview
########

pyTooling installs a program of its own: :program:`pyTooling`. It is the command line front-end to what the package
models - reading a CI pipeline into a trace, writing that trace, rendering it - so a pipeline job can do those
things without a script of its own.

.. code-block:: bash

   pyTooling help              # what the program can do
   pyTooling help <command>    # what one command can do
   pyTooling version           # which pyTooling is installed

The program is the ``console_scripts`` entry point :pycode:`pyTooling.CLI:main`, which :file:`setup.py` registers,
so it is on the path after :pycode:`pip install pyTooling`. Running the module directly works as well:
:pycode:`python -m pyTooling.CLI` is not a thing, but :pycode:`python -c "from pyTooling.CLI import main; main()"`
is, and so is the installed program.


.. _CLI/Structure:

How a command is declared
#########################

The program is a :class:`~pyTooling.TerminalUI.TerminalApplication` **and** an
:class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin`, so it prints like the first and parses like the
second: a command is a **method** marked with :class:`~pyTooling.Attributes.ArgParse.CommandHandler`, and the
arguments of that command are the attributes written above the method. See :ref:`ATTR/ArgParse` for the attributes
themselves.

.. code-block:: Python

   @CommandHandler("version", help="Display version information.")
   def HandleVersion(self, _: Namespace) -> None:
     ...

Two commands are always there: :pycode:`help`, which prints the help page of the program or of one command, and
:pycode:`version`. A call with no command prints the help page.

**A group of related commands is a mixin-class of its own.**
:class:`~pyTooling.CLI.Application` inherits from all of them, and the attributes are found on the assembled class,
so adding a command means writing a mixin and adding one base-class - see :ref:`ATTR/ArgParse/Mixin`. That is the
same construction :program:`pyedaa-outputfilter` uses.

.. hint::

   The three global switches - ``-q`` / ``--quiet``, ``-v`` / ``--verbose`` and ``-d`` / ``--debug`` - are declared
   on the **default handler**, so they belong before the command: ``pyTooling --verbose version``, not
   ``pyTooling version --verbose``.


.. _CLI/Errors:

What a failure looks like
#########################

:func:`~pyTooling.CLI.main` runs the program inside a ``try ... except``, so a user of the program sees a message
and a non-zero exit code rather than a traceback. A :exc:`~pyTooling.Exceptions.ToolingException` is printed with
its cause and with every note it carries, because the notes are where pyTooling puts the advice - *"check the
repository's name"* rather than only *"404"*.
