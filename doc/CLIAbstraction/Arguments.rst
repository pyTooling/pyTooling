.. _CLIABS/Arguments:

Arguments
#########

Every argument class is named by the same three-part rule, so a class name can be read off the command line syntax
it produces - and the syntax guessed from the name:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Part
     - Means
   * - ``***Argument``
     - the **basic** classes, and anything that isn't a named option: a command, a path, a bare value.
   * - ``***Flag``
     - a **named** option - a name the user types, with or without a value attached.
   * - ``Short``, ``Long``, ``Windows``
     - the **prefix character(s)** the name is written with: ``-``, ``--`` and ``/``. Three variants of every flag
       family, differing in nothing else.

So :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag` is *a named option with a value, written with a
double dash* - ``--flag=value`` - and that is the whole name.

.. hint::

   The ``Windows`` variants are not only about the prefix: they use a **colon** where the others use an equals sign,
   because that is what Windows tools expect. ``--flag=value`` on Linux is ``/flag:value`` on Windows.


.. _CLIABS/Arguments:Overview:

Overview
********

.. mermaid::

   graph LR;
     CLA[CommandLineArgument]
     style CLA stroke-dasharray: 5 5

     EA[ExecutableArgument]

     NA[NamedArgument]
     style NA stroke-dasharray: 5 5

     VA[ValuedArgument]
     style VA stroke-dasharray: 5 5

     NVA[NamedAndValuedArgument]
     style NVA stroke-dasharray: 5 5

     BF[BooleanFlag]
     style NVA stroke-dasharray: 5 5

     NTA[NamedTupledArgument]
     style NTA stroke-dasharray: 5 5

     NKVPA[NamedKeyValuePairsArgument]
     style NKVPA stroke-dasharray: 5 5

     CLA ----> EA
     CLA --> NA
     CLA --> VA
     NA --> NVA
     VA --> NVA
     NA --> BF
     VA --> BF
     NA --> NTA
     VA --> NTA
     NA --> NKVPA
     VA --> NKVPA

     CA["<b>CommandArgument</b><br/><div style='font-family: monospace'>command</div>"]
     FA[FlagArgument]
     style FA stroke-dasharray: 5 5

     NA ---> CA
     NA ---> FA

     SA["<b>StringArgument</b><br/><div style='font-family: monospace'>value</div>"]
     SLA["<b>StringListArgument</b><br/><div style='font-family: monospace'>value1 value2</div>"]
     PA["<b>PathArgument</b><br/><div style='font-family: monospace'>file1.txt</div>"]
     PLA["<b>PathListArgument</b><br/><div style='font-family: monospace'>file1.txt file2.txt</div>"]

     VA ---> SA
     VA ---> SLA
     VA ---> PA
     VA ---> PLA

     NVFA["<b>NamedAndValuedFlagArgument</b><br/><div style='font-family: monospace'>output=file.txt</div>"]
     style NVFA stroke-dasharray: 5 5
     NOVFA["<b>NamedAndOptionalValuedFlagArgument</b><br/><div style='font-family: monospace'>output=file.txt</div>"]
     style NOVFA stroke-dasharray: 5 5

     NVA --> NVFA
     NVA --> NOVFA


.. _CLIABS/Arguments/WithPrefix:

Without Prefix Character(s)
***************************

+--------------------------+--------------------------------+-------------------------------------------------------------------+
| **RAW Format**           | **Examples**                   | **Argument Class**                                                |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``executable``           | ``prog``                       | :class:`~pyTooling.CLIAbstraction.Argument.ExecutableArgument`    |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``--``                   | ``prog -option -- file1.txt``  | :class:`~pyTooling.CLIAbstraction.Argument.DelimiterArgument`     |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``command``              | ``prog help``                  | :class:`~pyTooling.CLIAbstraction.Command.CommandArgument`        |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``string``               | ``prog value``                 | :class:`~pyTooling.CLIAbstraction.Argument.StringArgument`        |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``string1`` ``string2``  | ``prog value1 value2``         | :class:`~pyTooling.CLIAbstraction.Argument.StringListArgument`    |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``path``                 | ``prog file1.txt``             | :class:`~pyTooling.CLIAbstraction.Argument.PathArgument`          |
+--------------------------+--------------------------------+-------------------------------------------------------------------+
| ``path1`` ``path2``      | ``prog File1.log File1.log``   | :class:`~pyTooling.CLIAbstraction.Argument.PathListArgument`      |
+--------------------------+--------------------------------+-------------------------------------------------------------------+

Executable
==========

An executable argument represents a program/executable. The internal value is a :class:`Path` object.


Command
=======

Commands are (usually) mutually exclusive arguments and the first argument in a list of arguments to a program. They are
used to logically group arguments.

While commands can or cannot have prefix characters, they shouldn't be confused with flag arguments or string arguments.

**Example:**

* ``prog command -arg1 --argument2``

.. seealso::

   * For simple flags (various formats). |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Flag`
   * For string arguments. |br|
     |rarr| :class:`~pyTooling.CLIAbstraction.Argument.StringArgument`


String
======

A simple argument accepting any string value. If a string has a predefined format, more specific argument classes should
be used like :mod:`~pyTooling.CLIAbstraction.Command`, :mod:`~pyTooling.CLIAbstraction.Flag` or
:class:`~pyTooling.CLIAbstraction.Argument.PathArgument`.

.. seealso::

   * For path argument. |br|
     |rarr| :class:`~pyTooling.CLIAbstraction.Argument.PathArgument`


List of Strings
===============

Like :class:`~pyTooling.CLIAbstraction.Argument.StringArgument` but supporting a list of strings.

.. seealso::

   * For list of path arguments. |br|
     |rarr| :class:`~pyTooling.CLIAbstraction.Argument.PathListArgument`


Path
====

An argument accepting a :class:`~pathlib.Path` object.


List of Paths
=============

Like :class:`~pyTooling.CLIAbstraction.Argument.PathArgument` but supporting a list of paths.


.. _CLIABS/Arguments/WithoutPrefix:

With Prefix Character(s)
************************

Commonly used prefix characters are: single and double dash, single slash, or plus character(s).

.. list-table::
   :header-rows: 1
   :widths: 18 20 18 44

   * - **Single Dash Argument Format**
     - **Double Dash Argument Format**
     - **Single Slash Argument Format**
     - **Argument Class**
   * - ``-command``
     - ``--command``
     - ``/command``
     - :class:`~pyTooling.CLIAbstraction.Command.ShortCommand` |br|
       :class:`~pyTooling.CLIAbstraction.Command.LongCommand` |br|
       :class:`~pyTooling.CLIAbstraction.Command.WindowsCommand`
   * - ``-flag``
     - ``--flag``
     - ``/flag``
     - :class:`~pyTooling.CLIAbstraction.Flag.ShortFlag` |br|
       :class:`~pyTooling.CLIAbstraction.Flag.LongFlag` |br|
       :class:`~pyTooling.CLIAbstraction.Flag.WindowsFlag`
   * - ``-with-flag`` |br|
       ``-without-flag``
     - ``--with-flag`` |br|
       ``--without-flag``
     - ``/with-flag`` |br|
       ``/without-flag``
     - :class:`~pyTooling.CLIAbstraction.BooleanFlag.ShortBooleanFlag` |br|
       :class:`~pyTooling.CLIAbstraction.BooleanFlag.LongBooleanFlag` |br|
       :class:`~pyTooling.CLIAbstraction.BooleanFlag.WindowsBooleanFlag`
   * - ``-flag`` |br|
       ``-flag=value``
     - ``--flag`` |br|
       ``--flag=value``
     - ``/flag`` |br|
       ``/flag:value``
     - :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.ShortOptionalValuedFlag` |br|
       :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.LongOptionalValuedFlag` |br|
       :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.WindowsOptionalValuedFlag`
   * - ``-flag=value``
     - ``--flag=value``
     - ``/flag:value``
     - :class:`~pyTooling.CLIAbstraction.ValuedFlag.ShortValuedFlag` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedFlag.WindowsValuedFlag`
   * - ``-flag=value``
     - ``--flag=value``
     - ``/flag:value``
     - :class:`~pyTooling.CLIAbstraction.ValuedFlagList.ShortValuedFlagList` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedFlagList.LongValuedFlagList` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedFlagList.WindowsValuedFlagList`
   * - ``-flag value``
     - ``--flag value``
     - ``/flag value``
     - :class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.ShortTupleFlag` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.LongTupleFlag` |br|
       :class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.WindowsTupleFlag`
   * - ``-gKey1=value1 -gKey2=value2``
     - ``--gKey1=value1 --gKey2=value2``
     - ``/g:Key1=value1 /g:Key2=value2``
     - :class:`~pyTooling.CLIAbstraction.KeyValueFlag.ShortKeyValueFlag` |br|
       :class:`~pyTooling.CLIAbstraction.KeyValueFlag.LongKeyValueFlag` |br|
       :class:`~pyTooling.CLIAbstraction.KeyValueFlag.WindowsKeyValueFlag`


Command
=======

A **command** selects what a program does - ``git commit``, ``docker build``. It carries no value of its own, so it
is assigned ``None``, and its place in the assembled list follows the order the nested classes are declared in.

.. code-block:: Python

   @CLIArgument()
   class CommandCommit(CommandArgument, name="commit"): ...

   git[git.CommandCommit] = None      # -> commit

:class:`~pyTooling.CLIAbstraction.Command.CommandArgument` writes the bare word, which is what most modern tools
expect. The three prefixed variants exist for programs that spell a command like a flag.

.. mermaid::

   graph LR;
     CLA[CommandLineArgument]
     style CLA stroke-dasharray: 5 5
     CLA --> NA[NamedArgument]
     style NA stroke-dasharray: 5 5
     NA --> CA["<b>CommandArgument</b><br/><div style='font-family: monospace'>command</div>"];
     CA --> SCA["<b>ShortCommand</b><br/><div style='font-family: monospace'>-command</div>"];
     CA --> LCA["<b>LongCommand</b><br/><div style='font-family: monospace'>--command</div>"];
     CA --> WCA["<b>WindowsCommand</b><br/><div style='font-family: monospace'>/command</div>"];


Flag
====

A flag is a command line argument that is either present or not. If present that argument is said to be activated or
true.

3 variants are predefined with prefixes ``-``, ``--`` and ``/``.

.. rubric:: Variants

.. mermaid::

   graph LR;
     CLA[CommandLineArgument]
     style CLA stroke-dasharray: 5 5
     CLA --> NA[NamedArgument]
     style NA stroke-dasharray: 5 5
     NA --> FA[FlagArgument]
     style FA stroke-dasharray: 5 5
     FA --> SFA["<b>ShortFlag</b><br/><div style='font-family: monospace'>-flag</div>"]
     FA --> LFA["<b>LongFlag</b><br/><div style='font-family: monospace'>--flag</div>"]
     FA --> WFA["<b>WindowsFlag</b><br/><div style='font-family: monospace'>/flag</div>"]


Flag with Value
===============

A **valued flag** carries its value in the *same* argv entry, joined by an equals sign - or by a colon on Windows:

.. code-block:: Python

   @CLIArgument()
   class ValueOutput(LongValuedFlag, name="output"): ...

   program[program.ValueOutput] = "build/app"     # -> --output=build/app

This is the right class when the program's help text writes ``--output=FILE``. Where it writes ``--output FILE``,
with a space, the value is a separate argv entry and the class is
:class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.LongTupleFlag` - see :ref:`CLIABS/Arguments/TupleFlag`.


Boolean Flag
============

A plain flag can only be *present*. A **boolean flag** can be switched off as well, because it writes a different
name for each state - which is what a program needs when a feature is on by default:

.. code-block:: Python

   @CLIArgument()
   class BoolTests(LongBooleanFlag, name="tests"): ...

   program[program.BoolTests] = True      # -> --with-tests
   program[program.BoolTests] = False     # -> --without-tests

.. attention::

   The predefined variants write **``with-``/``without-``**, not ``flag``/``no-flag``. A program spelling its pair
   differently - ``--tests``/``--no-tests``, or ``--enable-x``/``--disable-x`` - derives its own class with the two
   patterns it needs:

   .. code-block:: Python

      class NoPrefixBooleanFlag(BooleanFlag, pattern="--{0}", falsePattern="--no-{0}"): ...


Flag with Optional Value
========================

Some options mean one thing on their own and another with a value attached - ``--color`` versus ``--color=always``.
An **optional valued flag** writes whichever form it was given:

.. code-block:: Python

   @CLIArgument()
   class OptionalColor(LongOptionalValuedFlag, name="color"): ...

   program[program.OptionalColor] = None         # -> --color
   program[program.OptionalColor] = "always"     # -> --color=always

Assigning ``None`` is what asks for the bare form, so this is the one class where ``None`` does not mean *"nothing
to write"* - it means *"write the name alone"*.


List of Flags with Value
========================

Where an option may be given more than once - include paths, libraries, defines - a **valued flag list** repeats the
whole flag, once per element of the assigned list:

.. code-block:: Python

   @CLIArgument()
   class ListLib(LongValuedFlagList, name="lib"): ...

   program[program.ListLib] = ["m", "pthread"]    # -> --lib=m --lib=pthread

The list is assigned as a list; the repetition is the class' job. Joining the values into one string by hand -
``--lib=m,pthread`` - is what this class exists to prevent, because very few programs accept it.



.. _CLIABS/Arguments/TupleFlag:

Flag with Value as a Tuple
==========================

A **tuple flag** writes the name and the value as **two** argv entries, with no separator between them:

.. code-block:: Python

   @CLIArgument()
   class ValueMessage(ShortTupleFlag, name="m"): ...

   git[git.ValueMessage] = "initial commit"       # -> -m, 'initial commit'

The difference from :class:`~pyTooling.CLIAbstraction.ValuedFlag.ShortValuedFlag` is invisible in a printed command
line and decisive in :class:`subprocess.Popen`, which receives a list: ``['-m', 'initial commit']`` is two
arguments, ``['-m=initial commit']`` is one. Programs parsing with :func:`getopt` want the former.

.. hint::

   The program's own help text decides. ``-m MESSAGE`` - a space - is a tuple flag; ``-m=MESSAGE`` is a valued flag.
