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





Arguments
*********

Flags
=====

ValuedFlags
===========


Argument Lists
**************

Commands
********


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
