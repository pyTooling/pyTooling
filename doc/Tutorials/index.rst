.. _Tutorials:

Tutorials
#########

The other chapters of this documentation describe **what** pyTooling offers, package by package. These tutorials
describe **how to build something with it**, and each of them answers a question that the API reference cannot: not
*what does this class do*, but *which of these classes do I reach for, and in what order*.

Each tutorial is self-contained. Read the one that matches the problem in front of you.


.. _Tutorials/Overview:

What each one is for
********************

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. rubric:: Structuring a program

      :ref:`TUTORIAL/ExceptionHierarchy`
        Give a package one base exception and a shape below it, so a caller can catch *your* failures without
        catching everything. Start here - the decisions are cheap now and expensive later.

      :ref:`TUTORIAL/MetaClasses`
        What a meta-class is, what Python does when it creates a class, and which of the four lighter tools to
        reach for before reaching for a meta-class at all. Background for :class:`~pyTooling.MetaClasses.ExtendedType`.

      :ref:`TUTORIAL/Decorators`
        The three shapes a decorator comes in - function-based with and without parameters, and class-based - and
        what each is good for.

      :ref:`TUTORIAL/Attributes`
        Attach declarative meta-data to classes, methods and functions, then find every entity carrying it. The
        alternative to a registry that every module has to remember to call.

   .. grid-item::
      :columns: 6

      .. rubric:: Building and testing a program

      :ref:`TUTORIAL/CLIAbstraction`
        Wrap a command line program - ``git``, a compiler, a simulator - as a Python class whose arguments are
        typed members instead of hand-assembled strings.

      :ref:`TUTORIAL/TerminalApplication`
        Build a terminal program with coloured output, verbosity levels and an exit-code contract.

      :ref:`TUTORIAL/UnitTesting`
        What to test and in which order, and what the report should call it.

      :ref:`TUTORIAL/ApplicationTesting`
        The other half: testing the program the way a user starts it, through its entry point.


.. _Tutorials/Order:

A suggested order
*****************

For a new package built on pyTooling, the tutorials fall into a natural sequence. Nothing forces it - but each step
makes a decision that the next one builds on:

#. :ref:`TUTORIAL/ExceptionHierarchy` - decide how the package reports failure, **before** there is code that
   raises. Retrofitting a base exception means touching every ``raise``.
#. :ref:`TUTORIAL/MetaClasses` - decide whether the data model needs
   :class:`~pyTooling.MetaClasses.ExtendedType`, and which of its options. Slots are a class-creation decision.
#. :ref:`TUTORIAL/UnitTesting` - decide the levels and the naming while the test suite is still small.
#. :ref:`TUTORIAL/CLIAbstraction` or :ref:`TUTORIAL/TerminalApplication` - the two shapes a command line tool
   takes: one *calls* other programs, the other *is* one.
#. :ref:`TUTORIAL/ApplicationTesting` - once there is an entry point to start.

:ref:`TUTORIAL/Decorators` and :ref:`TUTORIAL/Attributes` are reference material rather than steps; read them when
a declarative annotation would be shorter than the imperative code you are about to write.

.. toctree::
   :hidden:

   ApplicationTesting
   Attributes
   CLIAbstraction
   Decorators
   ExceptionHierarchy
   MetaClasses
   TerminalApplication
   UnitTesting
