.. _CLIABS:

Overview
########

:mod:`~pyTooling.CLIAbstraction` offers an abstraction layer for command line programs, so they can be used easily in
Python. There is no need for manually assembling parameter lists or considering the order of parameters. All parameters
like ``-v`` or ``--value=42`` are described as :class:`~pyTooling.CLIAbstraction.Argument.CommandLineArgument` instances
on a :class:`~pyTooling.CLIAbstraction.Program` class. Each argument class like :class:`~pyTooling.CLIAbstraction.Flag.ShortFlag`
or :class:`~pyTooling.CLIAbstraction.Argument.PathArgument` knows about the correct formatting pattern, character
escaping, and if needed about necessary type conversions. A program instance can be converted to an argument list
suitable for :class:`subprocess.Popen`.

While a user-defined command line program abstraction derived from :class:`~pyTooling.CLIAbstraction.Program` only
takes care of maintaining and assembling parameter lists, a more advanced base-class, called :class:`~pyTooling.CLIAbstraction.Executable`,
is offered with embedded :class:`~subprocess.Popen` behavior.


.. _CLIABS/Goals:

Design Goals
************

The main design goals are:

* Offer access to CLI programs as Python classes.
* Abstract CLI arguments (a.k.a. parameter, option, flag, ...) as members on such a Python class.
* Abstract differences in operating systems like argument pattern (POSIX: ``-h`` vs. Windows: ``/h``), path delimiter
  signs (POSIX: ``/`` vs. Windows: ``\``) or executable names.
* Derive program variants from existing programs.
* Assemble parameters as list for handover to :class:`subprocess.Popen` with proper escaping and quoting.
* Launch a program with :class:`~subprocess.Popen` and hide the complexity of Popen.
* Get a generator object for line-by-line output reading to enable postprocessing of outputs.


.. _CLIABS/Example:

Example
*******

The following example implements a portion of the ``git`` program and its ``commit`` sub-command.

1. A new class ``Git`` is derived from :class:`pyTooling.CLIAbstraction.Executable`.
2. A class variable ``_executableNames`` is set, to specify different executable names based on the operating system.
3. Nested classes are used to describe arguments and flags for the Git program.
4. These nested classes are annotated with the ``@CLIArgument`` attribute, which is used to register the nested classes
   in an ordered lookup structure. This declaration order is also used to order arguments when converting to a list for
   :class:`~subprocess.Popen`.

.. grid:: 2

   .. grid-item:: **Usage of** ``Git``
      :columns: 6

      .. code-block:: Python

         # Create a program instance and set common parameters.
         git = Git()
         git[git.FlagVerbose] = True

         # Derive a variant of that pre-configured program.
         commit = git.getCommitTool()
         commit[commit.ValueCommitMessage] = "Bumped dependencies."

         # Launch the program and parse outputs line-by-line.
         commit.StartProcess()
         for line in commit.GetLineReader():
           print(line)

   .. grid-item:: **Declaration of** ``Git``
      :columns: 6

      .. code-block:: Python

         from pyTooling.CLIAbstraction import Executable
         from pyTooling.CLIAbstraction.Command import CommandArgument
         from pyTooling.CLIAbstraction.Flag import LongFlag
         from pyTooling.CLIAbstraction.ValuedTupleFlag import ShortTupleFlag

         class Git(Executable):
           _executableNames: ClassVar[Dict[str, str]] = {
             "Darwin":  "git",
             "FreeBSD": "git",
             "Linux":   "git",
             "Windows": "git.exe"
           }

           @CLIArgument()
           class FlagVerbose(LongFlag, name="verbose"):
             """Print verbose messages."""

           @CLIArgument()
           class CommandCommit(CommandArgument, name="commit"):
             """Command to commit staged files."""

           @CLIArgument()
           class ValueCommitMessage(ShortTupleFlag, name="m"):
             """Specify the commit message."""

           def GetCommitTool(self):
             """Derive a new program from a configured program."""
             tool = self.__class__(executablePath=self._executablePath)
             tool[tool.CommandCommit] = True
             self._CopyParameters(tool)

             return tool


.. _CLIABS/ProgramAPI:

Programm API
************

**Condensed definition of class** :class:`~pyTooling.CLIAbstraction.Program`:

.. condensed-class:: pyTooling.CLIAbstraction.Program


.. _CLIABS/ExecutableAPI:

Executable API
**************

**Condensed definition of class** :class:`~pyTooling.CLIAbstraction.Executable`:

.. condensed-class:: pyTooling.CLIAbstraction.Executable


.. _CLIABS/Consumers:

Consumers
*********

This abstraction layer is used by:

* ✅ Wrap command line interfaces of EDA tools (Electronic Design Automation) in Python classes. |br|
  `pyEDAA.CLITool <https://github.com/edaa-org/pyEDAA.CLITool>`__
