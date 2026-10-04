.. _CLIABS:

Overview
########

:mod:`~pyTooling.CLIAbstraction` offers an abstraction layer for command line programs, so they can be used easily in
Python. There is no need for manually assembling parameter lists or considering the order of parameters. All parameters
like ``-v`` or ``--value=42`` are described as :class:`~pyTooling.CLIAbstraction.Argument.CommandLineArgument` instances
on a :class:`~pyTooling.CLIAbstraction.Program` class. Each argument class like :class:`~pyTooling.CLIAbstraction.Flag.ShortFlag`
or :class:`~pyTooling.CLIAbstraction.Argument.PathArgument` knows about the correct formatting pattern, and if needed
about necessary type conversions. A program instance can be converted to an argument list suitable for
:class:`subprocess.Popen`, which passes each argument to the program without a shell - so no argument needs escaping.

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
* Assemble parameters as list for handover to :class:`subprocess.Popen`, in the order the program declares them.
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
         commit = git.GetCommitTool("Bumped dependencies.", amend=True)

         # Launch the program and parse outputs line-by-line.
         commit.StartProcess()
         for line in commit.GetLineReader():
           print(line)

   .. grid-item:: **Declaration of** ``Git``
      :columns: 6

      .. code-block:: Python

         from pyTooling.CLIAbstraction import CLIArgument, Executable
         from pyTooling.CLIAbstraction.Argument import PathListArgument
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
           class FlagAmend(LongFlag, name="amend"):
             """Replace the tip of the current branch."""

           @CLIArgument()
           class ValueCommitMessage(ShortTupleFlag, name="m"):
             """Specify the commit message."""

           @CLIArgument()
           class ArgumentPaths(PathListArgument):
             """Files to commit."""

           def _CopyParameters(self, tool: "Git") -> None:
             """Copy all parameters of this program to another instance."""
             for key, argument in self.__cliParameters__.items():
               if self._NeedsParameterInitialization(key):
                 tool[key] = argument.Value
               else:
                 tool[key] = True

           def GetCommitTool(
             self,
             message: str,
             amend: bool = False,
             paths: Nullable[Iterable[Path]] = None
           ) -> "Git":
             """Derive a commit command from this program."""
             tool = self.__class__(executablePath=self._executablePath)
             self._CopyParameters(tool)

             tool[tool.CommandCommit] = True
             tool[tool.ValueCommitMessage] = message
             if amend:
               tool[tool.FlagAmend] = True
             if paths is not None:
               tool[tool.ArgumentPaths] = paths

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


.. _CLIABS/Competitors:

Competing Solutions
*******************

The packages below run a program from Python, but describe its command line as strings. pyTooling describes it as
classes: every argument of a program is a nested class of its :class:`~pyTooling.CLIAbstraction.Program`, whose base
class - :class:`~pyTooling.CLIAbstraction.Flag.ShortFlag`, :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag`,
:class:`~pyTooling.CLIAbstraction.Flag.WindowsFlag`, ... - formats it as ``-v``, ``--value=42`` or ``/v``. The
arguments are listed in the order they are declared, and the executable's name is chosen per platform.

.. _CLIABS/subprocess:

subprocess
==========

Source: the standard library's :mod:`subprocess`.

.. rubric:: Disadvantages

* A command line is a list of strings, assembled by the caller in the right order and in each program's syntax.

.. rubric:: Standoff

* :meth:`~pyTooling.CLIAbstraction.Program.ToArgumentList` returns such a list, and
  :class:`~pyTooling.CLIAbstraction.Executable` starts it with :class:`~subprocess.Popen`.

.. rubric:: Advantages

* No dependency, and every option of :class:`~subprocess.Popen` is available.

.. _CLIABS/plumbum:

plumbum
=======

Source: :gh:`plumbum <tomerfiliba/plumbum>`, on PyPI as `plumbum <https://pypi.org/project/plumbum/>`__.

.. rubric:: Disadvantages

* Arguments are bound as strings - ``local["ls"]["-l"]`` - so a flag's syntax is written at every call.

.. rubric:: Advantages

* Pipelines (``|``), redirection (``<``, ``>``), background execution, and commands run on a remote machine over SSH.
* A toolkit for writing command line applications.

.. _CLIABS/sh:

sh
==

Source: :gh:`sh <amoffat/sh>`, on PyPI as `sh <https://pypi.org/project/sh/>`__.

.. rubric:: Disadvantages

* Windows is not supported.
* Keyword arguments become flags by one rule - one letter ``-o value``, more letters ``--name`` - so a program
  using another syntax, like ``/flag`` or ``-flag=value``, is called with strings.

.. rubric:: Advantages

* A program is called like a function, ``sh.git.commit(m="message")``, without declaring it first.

.. _CLIABS/invoke:

invoke
======

Source: :gh:`invoke <pyinvoke/invoke>`, on PyPI as `invoke <https://pypi.org/project/invoke/>`__.

.. rubric:: Disadvantages

* A command is one string run by a shell, so quoting and the shell's syntax are the caller's.

.. rubric:: Standoff

* A task runner - tasks with their own command line - more than a program abstraction.


.. _CLIABS/Consumers:

Consumers
*********

This abstraction layer is used by:

* ✅ Wrap command line interfaces of EDA tools (Electronic Design Automation) in Python classes. |br|
  :gh:`pyEDAA.CLITool <edaa-org/pyEDAA.CLITool>`
