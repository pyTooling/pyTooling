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

An argument attribute is written **above the handler method that receives it**, and each one adds one entry to that
handler's parser. Every attribute takes :pycode:`dest`, which names the field the parsed value appears under in
:pycode:`args`, and :pycode:`help`, which is what ``--help`` prints.

.. code-block:: Python

   @CommandHandler("create", help="Create a new user.")
   @StringArgument(dest="username", metaName="username", help="Name of the user to create.")
   @LongValuedFlag("--quota", dest="quota", help="Disk quota of the new user.")
   def HandleCreate(self, args) -> None:
     print(f"Creating user '{args.username}' with a quota of {args.quota}.")

Two shapes exist, and the difference is the one :mod:`argparse` itself makes:

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Shape
     - Written as
   * - **positional**
     - a value with no name in front of it - ``UserManager.py create alice``. :pycode:`metaName` is the placeholder
       ``--help`` shows; :pycode:`optional=True` makes it omissible.
   * - **flag**
     - a named option - ``--quota=10G``. The name is the attribute's first parameter, and :pycode:`dest` defaults to it.

.. hint::

   :pycode:`dest` is what the handler reads, so keep it a valid identifier and keep it stable. Renaming the command line
   spelling later - ``--quota`` to ``--disk-quota`` - then changes one string and leaves the handler alone.


.. _ATTR/ArgParse/Positional:

Positional arguments
====================

Each typed variant converts and validates the value before the handler sees it, so a handler never parses a string
itself:

.. list-table::
   :header-rows: 1
   :widths: 42 58

   * - Attribute
     - ``args.<dest>`` is
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.StringArgument`
     - a :class:`str`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.IntegerArgument`
     - an :class:`int`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.FloatArgument`
     - a :class:`float`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.PathArgument`
     - a :class:`~pathlib.Path`

All four take :pycode:`(dest, metaName, optional=False, help="")`.


.. _ATTR/ArgParse/Flags:

Flags
=====

A flag is either present or absent, and ``args.<dest>`` is a :class:`bool`.
:class:`~pyTooling.Attributes.ArgParse.Flag.ShortFlag` writes ``-v``,
:class:`~pyTooling.Attributes.ArgParse.Flag.LongFlag` writes ``--verbose``:

.. code-block:: Python

   @DefaultHandler()
   @LongFlag("--verbose", dest="verbose", help="Print verbose messages.")
   def HandleDefault(self, args) -> None:
     if args.verbose:
       ...

:class:`~pyTooling.Attributes.ArgParse.BooleanFlag.LongBooleanFlag` is the pair form, for an option that has to be
switchable **off** as well: it accepts ``--with-tests`` and ``--without-tests`` and sets one field either way.


.. _ATTR/ArgParse/ValuedFlags:

ValuedFlags
===========

A valued flag carries a value: ``--quota=10G``.
:class:`~pyTooling.Attributes.ArgParse.ValuedFlag.ShortValuedFlag` and
:class:`~pyTooling.Attributes.ArgParse.ValuedFlag.LongValuedFlag` take
:pycode:`(long, dest=None, metaName=None, optional=False, help=None)`.

:class:`~pyTooling.Attributes.ArgParse.OptionalValuedFlag.LongOptionalValuedFlag` accepts **both** forms -
``--color`` and ``--color=always`` - for the option that means one thing bare and another with a value.

:class:`~pyTooling.Attributes.ArgParse.KeyValueFlag.LongKeyValueFlag` collects repeated :pycode:`key=value` pairs into a
mapping, which is the shape of ``-D`` in a compiler.


.. _ATTR/ArgParse/Lists:

Argument Lists
**************

Where an argument may be given more than once, the ``***ListArgument`` variants collect the occurrences into a
:class:`list` instead of keeping the last one:

.. list-table::
   :header-rows: 1
   :widths: 46 54

   * - Attribute
     - ``args.<dest>`` is
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.StringListArgument`
     - :pycode:`list[str]`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.IntegerListArgument`
     - :pycode:`list[int]`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.FloatListArgument`
     - :pycode:`list[float]`
   * - :class:`~pyTooling.Attributes.ArgParse.Argument.PathListArgument`
     - :pycode:`list[Path]`

.. hint::

   A list argument is what makes ``UserManager.py delete alice bob carol`` work. Reach for it whenever the handler
   would otherwise have to split a comma-separated string - the shell already did that work.


.. _ATTR/ArgParse/Commands:

Commands
********

A **command** is a sub-parser: ``UserManager.py create ...`` and ``UserManager.py list`` are two commands with
different arguments. :deco:`~pyTooling.Attributes.ArgParse.CommandHandler` declares one, and the method it decorates
is what runs when a user types it.

.. code-block:: Python

   @CommandHandler("create", help="Create a new user.")
   @StringArgument(dest="username", metaName="username", help="Name of the user to create.")
   def HandleCreate(self, args) -> None:
     ...

:deco:`~pyTooling.Attributes.ArgParse.DefaultHandler` declares the handler for *no* command - the program called
bare. A program has at most one, and its arguments are the ones accepted before any command, which is where a
global ``--verbose`` belongs.

.. attention::

   **Arguments declared on the default handler are global; arguments declared on a command handler belong to that
   command.** ``UserManager.py --verbose create alice`` is therefore right and ``UserManager.py create alice
   --verbose`` is not - the same rule :program:`git` follows.


.. _ATTR/ArgParse/Grouping:

Grouping Arguments
******************

:class:`~pyTooling.Attributes.ArgParse.CommandGroupAttribute` puts related commands under a heading in ``--help``,
which is what keeps a program with twenty commands readable. Derive a group attribute and apply it to the handlers
that belong together:

.. code-block:: Python

   class UserCommands(CommandGroupAttribute):
     """Commands operating on users."""

   class GroupCommands(CommandGroupAttribute):
     """Commands operating on groups."""

   class UserManager(ArgParseHelperMixin):
     @UserCommands("User commands")
     @CommandHandler("create", help="Create a new user.")
     def HandleCreate(self, args) -> None: ...

     @GroupCommands("Group commands")
     @CommandHandler("addgroup", help="Create a new group.")
     def HandleAddGroup(self, args) -> None: ...


.. _ATTR/ArgParse/MixIn:

Split Handlers into multiple classes
************************************

A program with many commands doesn't have to declare them in one class.
:class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin` is a mixin, so handlers can be grouped into mixins of
their own and combined - one file per subject area, and the parser assembled from all of them:

.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class UserHandlers(metaclass=ExtendedType, mixin=True):
     @CommandHandler("create", help="Create a new user.")
     @StringArgument(dest="username", metaName="username", help="Name of the user.")
     def HandleCreate(self, args) -> None: ...

   class GroupHandlers(metaclass=ExtendedType, mixin=True):
     @CommandHandler("addgroup", help="Create a new group.")
     @StringArgument(dest="groupname", metaName="groupname", help="Name of the group.")
     def HandleAddGroup(self, args) -> None: ...

   class UserManager(ArgParseHelperMixin, UserHandlers, GroupHandlers):
     def __init__(self) -> None:
       super().__init__(prog="UserManager.py")

The attributes are found on the assembled class, so a handler moved from one mixin to another needs no change
anywhere else. See :ref:`META/Mixin` for what :pycode:`mixin=True` does.


Classic ``argparse`` Example
****************************

.. literalinclude:: ../../tests/example/OldStyle.py
   :language: python
   :linenos:
   :caption: tests/example/OldStyle.py
   :tab-width: 2


New ``pyTooling.Attributes`` Approach
*************************************

A better and more descriptive solution could look like this:

.. literalinclude:: ../../tests/example/UserManager.py
   :language: python
   :linenos:
   :caption: tests/example/UserManager.py
   :tab-width: 2


.. _ATTR/ArgParse/Consumers:

Consumers
*********

This package is used by:

* ✅ . |br|
  :ref:`pyTooling.Attributes.ArgParse <ATTR/ArgParse>`
