.. _ATTR/ArgParse:

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


.. _ATTR/ArgParse/Comparison:

Comparison
**********


.. grid:: 2

   .. grid-item:: **pyTooling.Attributes.ArgParse**

      .. code-block:: Python

         class Program:
           @DefaultHandler()
           @FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
           def HandleDefault(self, args) -> None:
             pass

           @CommandHandler("new-user", help="Add a new user.")
           @StringArgument(dest="username", metaName="username", help="Name of the new user.")
           @LongValuedFlag("--quota", dest="quota", help="Max usable disk space.")
           def NewUserHandler(self, args) -> None:
             pass

           @CommandHandler("delete-user", help="Delete a user.")
           @StringArgument(dest="username", metaName="username", help="Name of the user.")
           @FlagArgument(short="-f", long="--force", dest="force", help="Ignore internal checks.")
           def DeleteUserHandler(self, args) -> None:
             pass

           @CommandHandler("list-user", help="List all users.")
           def ListUserHandler(self, args) -> None:
             pass

   .. grid-item:: **Traditional ArgParse**

      .. code-block:: Python

         class Program:
           def __init__(self):
             mainParser = argparse.ArgumentParser()
             mainParser.set_defaults(func=self.HandleDefault)
             mainParser.add_argument("-v", "--verbose")
             subParsers = mainParser.add_subparsers()

             newUserParser = subParsers.add_parser("new-user", help="Add a new user.")
             newUserParser.add_argument(dest="username", metaName="username", help="Name of the new user.")
             newUserParser.add_argument("--quota", dest="quota", help="Max usable disk space.")
             newUserParser.set_defaults(func=self.NewUserHandler)

             deleteUserParser = subParsers.add_parser("delete-user", help="Delete a user.")
             deleteUserParser.add_argument(dest="username", metaName="username", help="Name of the user.")
             deleteUserParser.add_argument("-f", "--force", dest="force", help="Ignore internal checks.")
             deleteUserParser.set_defaults(func=self.DeleteUserHandler)

             listUserParser = subParsers.add_parser("list-user", help="List all users.")
             listUserParser.set_defaults(func=self.ListUserHandler)

           def HandleDefault(self, args) -> None:
             pass

           def NewUserHandler(self, args) -> None:
             pass

           def DeleteUserHandler(self, args) -> None:
             pass

           def ListUserHandler(self, args) -> None:
             pass



.. _ATTR/ArgParse/Arguments:

Arguments
*********

An argument attribute is written **on the handler method that receives it**, and each one becomes exactly one
:meth:`~argparse.ArgumentParser.add_argument` call on the parser belonging to that handler. The attribute's
parameters are the ones :mod:`argparse` already uses - ``dest``, ``help``, ``metaName`` - so nothing new has to be
learned to say what a parser already knows how to do.

They form a hierarchy, and the leaves are what a program writes:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Base-class
     - What it stands for
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.NamedArgument`
     - An argument with a **name** - ``--verbose``.
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.ValuedArgument`
     - An argument with a **value**.
   * - ``NamedAndValuedArgument``
     - Both - ``--quota=5GiB``.
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.PositionalArgument`
     - A value with **no** name, identified by its position.
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.DelimiterArgument`
     - The ``--`` that ends option parsing.

The positional leaves are typed, and the type is what :mod:`argparse` converts the string with:
:class:`~pyTooling.Attributes.ArgParse.Argument.StringArgument`,
:class:`~pyTooling.Attributes.ArgParse.Argument.IntegerArgument`,
:class:`~pyTooling.Attributes.ArgParse.Argument.FloatArgument` and
:class:`~pyTooling.Attributes.ArgParse.Argument.PathArgument`.


.. _ATTR/ArgParse/Flags:

Flags
=====

A :class:`~pyTooling.Attributes.ArgParse.Flag.FlagArgument` is a switch: it carries no value, and the handler
receives :class:`bool` - ``True`` when the switch was given, ``False`` otherwise. The attribute sets
``action="store_const"`` with ``const=True`` and ``default=False``, which is what makes that boolean appear.

.. code-block:: Python

   @FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
   def HandleDefault(self, args) -> None:
     if args.verbose:
       ...

:class:`~pyTooling.Attributes.ArgParse.Flag.ShortFlag` and
:class:`~pyTooling.Attributes.ArgParse.Flag.LongFlag` are the same switch restricted to one spelling, for a program
that offers only ``-v`` or only ``--verbose``.

A switch that has to express *three* states - on, off, and not given - is a
:class:`~pyTooling.Attributes.ArgParse.BooleanFlag.BooleanFlag`, which registers a pair of option strings.
:class:`~pyTooling.Attributes.ArgParse.BooleanFlag.ShortBooleanFlag`,
:class:`~pyTooling.Attributes.ArgParse.BooleanFlag.LongBooleanFlag` and
:class:`~pyTooling.Attributes.ArgParse.BooleanFlag.WindowsBooleanFlag` differ only in how they spell that pair.


.. _ATTR/ArgParse/ValuedFlags:

ValuedFlags
===========

A :class:`~pyTooling.Attributes.ArgParse.ValuedFlag.ValuedFlag` is a named argument **followed by a value in the
same token** - ``--quota=5GiB``. ``metaName`` is what the help page shows in place of the value.

.. code-block:: Python

   @LongValuedFlag("--quota", dest="quota", metaName="size", help="Max usable disk space.")
   def NewUserHandler(self, args) -> None:
     quota = args.quota

:class:`~pyTooling.Attributes.ArgParse.ValuedFlag.ShortValuedFlag` and
:class:`~pyTooling.Attributes.ArgParse.ValuedFlag.LongValuedFlag` fix the spelling, as with the flags above.

Two variants exist for values that aren't a single string:

* :class:`~pyTooling.Attributes.ArgParse.OptionalValuedFlag.OptionalValuedFlag` - the value **may** be omitted, so
  the option carries a default when it is given bare.
* :class:`~pyTooling.Attributes.ArgParse.KeyValueFlag.NamedKeyValuePairsArgument` - the value is itself a
  ``key=value`` pair, so an option may be repeated to build a mapping, as ``-D name=value`` does for a compiler.
  :class:`~pyTooling.Attributes.ArgParse.KeyValueFlag.ShortKeyValueFlag` and
  :class:`~pyTooling.Attributes.ArgParse.KeyValueFlag.LongKeyValueFlag` are its two spellings.


.. _ATTR/ArgParse/ValuedTupleFlags:

ValuedTupleFlags
================

A *tuple* flag is a named argument whose value is a **separate token** - ``--width 100`` rather than
``--width=100``, so name and value reach the program as two arguments.

.. attention::

   Only the base-class ``NamedTupledArgument`` exists so far. There is
   no concrete ``ShortTupleFlag`` / ``LongTupleFlag`` attribute to apply yet, so this form has to be written as a
   :class:`~pyTooling.Attributes.ArgParse.ValuedFlag.ValuedFlag` with ``nargs`` passed through to
   :mod:`argparse` in the meantime.


.. _ATTR/ArgParse/Lists:

Argument Lists
**************

A :class:`~pyTooling.Attributes.ArgParse.Argument.ListArgument` collects **more than one** value into a list, and
the typed variants convert each element:
:class:`~pyTooling.Attributes.ArgParse.Argument.StringListArgument`,
:class:`~pyTooling.Attributes.ArgParse.Argument.IntegerListArgument`,
:class:`~pyTooling.Attributes.ArgParse.Argument.FloatListArgument` and
:class:`~pyTooling.Attributes.ArgParse.Argument.PathListArgument`.

.. code-block:: Python

   @CommandHandler("build", help="Build the given source files.")
   @PathListArgument(dest="sources", metaName="source", help="Source files to build.")
   def BuildHandler(self, args) -> None:
     for source in args.sources:   # a list of 'Path'
       ...

The handler always receives a :class:`list`, including when the command line named a single value.


.. _ATTR/ArgParse/Commands:

Commands
********

A **sub-command** is a method marked with
:class:`~pyTooling.Attributes.ArgParse.CommandHandler`, which creates a sub-parser of that name and routes to the
method when the command is used. The argument attributes below it belong to *that* sub-parser, which is what keeps
a command's arguments next to the code handling them.

Exactly one method may be marked :class:`~pyTooling.Attributes.ArgParse.DefaultHandler`. It receives the arguments
of the **main** parser and runs when no sub-command was given. Marking a second one raises
:exc:`~pyTooling.Attributes.ArgParse.ArgParseError` while the class is being constructed, rather than at the first
call.

.. code-block:: Python

   @DefaultHandler()
   @FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
   def HandleDefault(self, args) -> None:
     ...

   @CommandHandler("list-user", help="List all users.")
   def ListUserHandler(self, args) -> None:
     ...

The class itself mixes in :class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin`, whose constructor builds all
the parsers from the attributes it finds.
:meth:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin.Run` then parses and dispatches, and
:attr:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin.MainParser` and
:attr:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin.SubParsers` expose the underlying
:class:`~argparse.ArgumentParser` objects for anything the attributes don't cover.

.. hint::

   The mixin passes ``**kwargs`` on to :class:`~argparse.ArgumentParser`, and changes two of its defaults:
   ``allow_abbrev=False``, so an abbreviated option isn't silently accepted, and ``exit_on_error=False``, so a
   parse error raises instead of ending the process.


.. _ATTR/ArgParse/Grouping:

Grouping Arguments
******************

:class:`~pyTooling.Attributes.ArgParse.CommandGroupAttribute` collects sub-commands under a named group, so a long
``prog.py --help`` lists related commands together instead of in one flat sequence.

.. code-block:: Python

   @CommandGroupAttribute("User management")
   @CommandHandler("new-user", help="Add a new user.")
   def NewUserHandler(self, args) -> None:
     ...

.. attention::

   This attribute is marked **experimental** in the source and affects the help page only - it changes no parsing
   behaviour.


.. _ATTR/ArgParse/MixIn:

Split Handlers into multiple classes
************************************

Because the handlers are found through attributes rather than through one constructor that builds every parser, a
parser can be **assembled from several classes**. Each class carries the commands it is responsible for, and the
program inherits from all of them:

.. code-block:: Python

   class UserCommands(metaclass=ExtendedType):
     @CommandHandler("new-user", help="Add a new user.")
     def NewUserHandler(self, args) -> None:
       ...

   class GroupCommands(metaclass=ExtendedType):
     @CommandHandler("new-group", help="Add a new group.")
     def NewGroupHandler(self, args) -> None:
       ...

   class Program(UserCommands, GroupCommands, ArgParseHelperMixin):
     def __init__(self) -> None:
       ArgParseHelperMixin.__init__(self, prog="usermgr")

This is what the *Advantages* list above means by *distributed across multiple classes*, and it is the reason the
attribute lookup is a class query rather than a scan: the meta-class already collected the annotated methods of
every base-class by the time the mixin's constructor runs.


.. _ATTR/ArgParse/Consumers:

Consumers
*********

This package is used by:

* ✅ Command line interface of pyEDAA.Reports. |br|
  `pyEDAA.Reports.CLI <https://edaa-org.github.io/pyEDAA.Reports/>`__
* ✅ Command line interface of pyVersioning. |br|
  `pyVersioning.CLI <https://paebbels.github.io/pyVersioning/>`__
