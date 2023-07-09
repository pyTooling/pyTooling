.. _CLIABS:Executable:

Executable
##########

The :class:`~pyTooling.CLIAbstraction.Executable` is derived from :class:`~pyTooling.CLIAbstraction.Program`, which
represents an executable command line program. In addition, it offers an API to :class:`subprocess.Popen`, so an
abstracted command line program can be launched.

**Features:**

* Launch an abstracted CLI program using :class:`subproess.Popen`.
* Setup and modify the environment for the launched program.
* Provide a line-based STDOUT reader as generator.


Simple Example
**************

The following example implements a portion of the ``git`` program and its ``--version`` argument.

.. rubric:: Program Definition

.. code-block:: Python
   :name: EXEC:Example:Definition
   :caption: Git program defining --version argument.

   class Git(Executable):
     _executableNames: ClassVar[Dict[str, str]] = {
       "Darwin":  "git",
       "Linux":   "git",
       "Windows": "git.exe"
     }

     @CLIArgument()
     class FlagVersion(LongFlag, name="version"):
       """Print the version information."""


.. rubric:: Program Usage

.. code-block:: Python
   :name: EXEC:Example:Usage
   :caption: Usage of the abstracted Git program.

   git = Git()
   git[git.FlagVersion] = True

   git.StartProcess()
   for line in git.GetLineReader():
     print(line)

