.. _CLIABS/Program:

Program
#######

The :class:`~pyTooling.CLIAbstraction.Program` represents an executable command line program. It offers an interface to
define and enable command line arguments.

**Features:**

* Abstract a command line program as a Python class.
* Abstract arguments of that program as nested classes derived from pre-defined Argument classes. |br|
  See :ref:`CLIABS/Arguments`.
* Construct a list of arguments in correct order and with proper escaping ready to be used with e.g. :mod:`subprocess`.

Simple Example
**************

The following example implements a portion of the ``git`` program and its ``--version`` argument.

.. rubric:: Program Definition

.. code-block:: Python
   :name: PROG:Example:Definition
   :caption: Git program defining --version argument.

   class Git(Program):
     _executableNames: ClassVar[Dict[str, str]] = {
       "Darwin":  "git",
       "FreeBSD": "git",
       "Linux":   "git",
       "Windows": "git.exe"
     }

     @CLIArgument()
     class FlagVersion(LongFlag, name="version"):
       """Print the version information."""


.. rubric:: Program Usage

.. code-block:: Python
   :name: PROG:Example:Usage
   :caption: Usage of the abstracted Git program.

   git = Git()
   git[git.FlagVersion] = True

   print(git.ToArgumentList())     # ['/usr/bin/git', '--version']
   print(git)                      # "/usr/bin/git" "--version"

Setting Program Names based on OS
*********************************

The same program is spelled differently per operating system - ``git`` and ``git.exe`` - so the name isn't a single
string but a **mapping from platform to name**, declared as the class variable ``_executableNames``. The keys are the
values :func:`platform.system` returns, and the constructor looks the current one up.

.. code-block:: Python

   class Git(Program):
     _executableNames: ClassVar[Dict[str, str]] = {
       "Darwin":  "git",
       "FreeBSD": "git",
       "Linux":   "git",
       "Windows": "git.exe"
     }

A platform the mapping doesn't name raises :exc:`~pyTooling.CLIAbstraction.CLIAbstractionError`, chained from a
:exc:`~pyTooling.Exceptions.PlatformNotSupportedError` - so *this program doesn't run here* is reported when the
object is constructed rather than when it is started.

Where the executable is looked for depends on what the constructor was given:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Constructor parameter
     - Where the executable comes from
   * - ``executablePath``
     - Exactly that path. It is used as given, and has to exist.
   * - ``binaryDirectoryPath``
     - That directory, joined with the platform's name from ``_executableNames``.
   * - neither
     - The platform's name, resolved through ``PATH`` with :func:`shutil.which`.

A missing executable raises :exc:`~pyTooling.CLIAbstraction.CLIAbstractionError` chained from
:exc:`FileNotFoundError`. With ``dryRun=True`` the check is logged and skipped instead, so a command line can be
assembled and printed on a machine that doesn't have the program installed.

Defining Arguments on a Program
*******************************

An argument is declared as a **nested class** of the program, derived from one of the argument classes in
:ref:`CLIABS/Arguments`, and marked with the :class:`~pyTooling.CLIAbstraction.CLIArgument` attribute.

.. code-block:: Python

   class Git(Program):
     @CLIArgument()
     class FlagVersion(LongFlag, name="version"):
       """Print the version information."""

Three things happen there, and each is deliberate:

**The nesting is the scope.** The class is defined inside the program it belongs to, so an argument cannot be set on
a program that doesn't declare it, and reading the class body is reading that program's command line interface.

**The decorator makes it findable.** :class:`~pyTooling.CLIAbstraction.CLIArgument` is a
:ref:`pyTooling attribute <ATTR>`. When a subclass of :class:`~pyTooling.CLIAbstraction.Program` is created, its
``__init_subclass__`` asks the attribute for every marked class *in this class' scope* and records them in
``__cliOptions__``. A nested class without the decorator is an ordinary nested class and no argument.

**The class-argument carries the spelling.** ``name="version"`` is a class keyword argument, read by the argument
base-class' own ``__init_subclass__`` and combined with that class' pattern - ``--{0}`` for a
:class:`~pyTooling.CLIAbstraction.Flag.LongFlag` - so the class knows how to render itself as ``--version``.

.. hint::

   ``__cliOptions__`` maps each argument class to **the position it was declared at**, and that number is the sort
   key :meth:`~pyTooling.CLIAbstraction.Program.ToArgumentList` uses. The order arguments appear on the command line
   is therefore the order they are declared in the class body, not the order they were set in.


.. _CLIABS/CLIArgument:

CLIArgument
===========

:class:`~pyTooling.CLIAbstraction.CLIArgument` is an :class:`~pyTooling.Attributes.Attribute` and carries no data of
its own - it marks a nested class as *this program's argument*. Marking is all it does; the collection happens once,
when the program class is created, and costs nothing per instance.


Setting Arguments on a Program
******************************

A program instance behaves like a **dictionary whose keys are the argument classes**:

.. code-block:: Python

   git = Git()
   git[git.FlagVersion] = True           # a flag: the value is ignored
   git[git.ValuedOption] = "some value"  # an argument carrying a value

The key is the class, not a string, so a misspelled option is caught by the same tools that catch a misspelled
attribute. Two mistakes raise instead of being accepted:

* an argument class the program doesn't declare - :exc:`KeyError`, naming the program;
* an argument that was already set - :exc:`KeyError`, because setting it twice is a bug rather than an override.

Whether the assigned value is used depends on the argument class.
:meth:`~pyTooling.CLIAbstraction.Program._NeedsParameterInitialization` decides it: a valued argument is constructed
*with* the value, a flag is constructed without one. That is why ``True`` above is not a value but a way of saying
*present*.

Reading the item back returns the **argument object**, whose
:attr:`~pyTooling.CLIAbstraction.Argument.ValuedArgument.Value` can be changed afterwards, so a program can be built
once and re-run with a different value:

.. code-block:: Python

   git[git.ValuedOption].Value = "another value"

:meth:`~pyTooling.CLIAbstraction.Program.ToArgumentList` renders the whole thing - the executable's path first, then
every set argument in declaration order - as the list :mod:`subprocess` expects. ``repr()`` and ``str()`` give the
same list quoted for reading.

Derive Program Variants
***********************

A program class can be derived like any other class, and the derived class **inherits nothing of the arguments**:
``__init_subclass__`` collects the nested classes in *its own* scope, so a variant declares the arguments it
supports, including re-declaring the ones it shares.

.. attention::

   There is currently **no helper to copy the set arguments** of one program instance to another, and no method to
   derive a configured variant from a configured program. A caller that needs one iterates the arguments it set and
   assigns them again on the new instance.
