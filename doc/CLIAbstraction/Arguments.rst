.. _CLIABS:Arguments:

Arguments
#########

.. todo:: Naming convention

   * Basic classes |rarr| Argument
   * Named arguments |rarr| Flag
   * Character prefixes |rarr| Short, Long, Windows


.. _CLIABS:Arguments:Overview:

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


.. _CLIABS:Arguments:WithPrefix:

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


.. _CLIABS:Arguments:WithoutPrefix:

With Prefix Character(s)
************************

Commonly used prefix characters are: single and double dash, single slash, or plus character(s).

+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Single Dash Argument Format**   | **Double Dash Argument Format**     | **Single Slash Argument Format**  | **Argument Class**                                                                                                                                                                                                                                   |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-command``                      | ``--command``                       | ``/command``                      | :class:`~pyTooling.CLIAbstraction.Command.ShortCommand`                       |br| :class:`~pyTooling.CLIAbstraction.Command.LongCommand`                       |br| :class:`~pyTooling.CLIAbstraction.Command.WindowsCommand`                       |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag``                         | ``--flag``                          | ``/flag``                         | :class:`~pyTooling.CLIAbstraction.Flag.ShortFlag`                             |br| :class:`~pyTooling.CLIAbstraction.Flag.LongFlag`                             |br| :class:`~pyTooling.CLIAbstraction.Flag.WindowsFlag`                             |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag`` |br| ``-no-flag``       | ``--flag`` |br| ``--no-flag``       | ``/flag`` |br| ``/no-flag``       | :class:`~pyTooling.CLIAbstraction.BooleanFlag.ShortBooleanFlag`               |br| :class:`~pyTooling.CLIAbstraction.BooleanFlag.LongBooleanFlag`               |br| :class:`~pyTooling.CLIAbstraction.BooleanFlag.WindowsBooleanFlag`               |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag`` |br| ``-flag=value``    | ``--flag`` |br| ``--flag=value``    | ``/flag`` |br| ``/flag=value``    | :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.ShortOptionalValuedFlag` |br| :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.LongOptionalValuedFlag` |br| :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.WindowsOptionalValuedFlag` |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag=value``                   | ``--flag=value``                    | ``/flag=value``                   | :class:`~pyTooling.CLIAbstraction.ValuedFlag.ShortValuedFlag`                 |br| :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag`                 |br| :class:`~pyTooling.CLIAbstraction.ValuedFlag.WindowsValuedFlag`                 |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag=value1 -flag=value2``     | ``--flag=value1 --flag=value2``     | ``/flag=value1 /flag=value2``     | :class:`~pyTooling.CLIAbstraction.ValuedFlagList.ShortValuedFlagList`         |br| :class:`~pyTooling.CLIAbstraction.ValuedFlagList.LongValuedFlagList`         |br| :class:`~pyTooling.CLIAbstraction.ValuedFlagList.WindowsValuedFlagList`         |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-flag value``                   | ``--flag value``                    | ``/flag value``                   | :class:`~pyTooling.CLIAbstraction.ShortTupleFlag`                             |br| :class:`~pyTooling.CLIAbstraction.LongTupleFlag`                             |br| :class:`~pyTooling.CLIAbstraction.WindowsTupleFlag`                             |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ``-gKey1=value1 -gKey2=value2``   | ``--gKey1=value1 --gKey2=value2``   | ``/g:Key1=value1 /g:Key2=value2`` | :class:`~pyTooling.CLIAbstraction.KeyValueFlag.ShortKeyValueFlag`             |br| :class:`~pyTooling.CLIAbstraction.KeyValueFlag.LongKeyValueFlag`             |br| :class:`~pyTooling.CLIAbstraction.KeyValueFlag.WindowsKeyValueFlag`             |
+-----------------------------------+-------------------------------------+-----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Command
=======

.. TODO:: Write documentation.

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

.. TODO:: Write documentation.


Boolean Flag
============

.. TODO:: Write documentation.


Flag with Optional Value
========================

.. TODO:: Write documentation.


List of Flags with Value
========================

.. TODO:: Write documentation.


Flag with Value as a Tuple
==========================

.. TODO:: Write documentation.
