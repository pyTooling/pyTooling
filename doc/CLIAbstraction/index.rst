.. _CLIABS:

Overview
########

pyTooling.CLIAbstraction is an abstraction layer and wrapper for command line programs, so they can be used easily in
Python. All parameters like ``--value=42`` are implemented as argument classes on the executable.


.. _CLIABS:Goals:

Main Goals
**********

* Offer access to CLI programs as Python classes.
* Abstract CLI arguments (a.k.a. parameter, option, flag, ...) as members on such a Python class.
* Derive program variants from existing programs.
* Assemble parameters in list format for handover to :class:`subprocess.Popen` with proper escaping and quoting.
* Launch a program with :class:`~subprocess.Popen` and hide the complexity of Popen.
* Get a generator object for line-by-line output reading to enable postprocessing of outputs.


.. _CLIABS:Usecases:

Use Cases
*********

* Wrap command line interfaces of EDA tools (Electronic Design Automation) in Python classes.


Example
*******

The following example implements a portion of the ``git`` program and its ``commit`` sub-command.

.. rubric:: Program Definition

.. code-block:: Python
   :name: HOME:Example
   :caption: Git program defining commit argument.

   # Definition
   # ======================================
   class Git(Executable):
     _executableNames: ClassVar[Dict[str, str]] = {
       "Darwin":  "git",
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

   # Usage
   # ======================================
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


Consumers
*********

This layer is used by:

* ✅ `pyEDAA.CLITool <https://github.com/edaa-org/pyEDAA.CLITool>`__


.. _news:

News
****

.. only:: html

   Feb. 2022 - Major Update
   ========================

.. only:: latex

   .. rubric:: Major Update

* Reworked names of Argument classes.
* Added missing argument formats like PathArgument.
* Added more unit tests and improved code-coverage.
* Added doc-strings and extended documentation pages.


.. only:: html

   Dec. 2021 - Extracted CLIAbstraction from pyIPCMI
   =================================================

.. only:: latex

   .. rubric:: Extracted CLIAbstraction from pyIPCMI

* The CLI abstraction has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


.. toctree::
   :hidden:

   Program
   Executable
   Arguments
