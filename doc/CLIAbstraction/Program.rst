.. _CLIABS:Program:

Program
#######

The :class:`~pyTooling.CLIAbstraction.Program` represents an executable command line program. It offers an interface to
define and enable command line arguments.

**Features:**

* Abstract a command line program as a Python class.
* Abstract arguments of that program as nested classes derived from pre-defined Argument classes. |br|
  See :ref:`CLIABS:Arguments`.
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

   print(git.AsArgument())

Setting Program Names based on OS
*********************************

.. todo::

   * set executable name based on the operating system.

Defining Arguments on a Program
*******************************

.. todo::

   * use decorator ``CLIArgument``
   * usage of nested classes
   * parametrize nested classes with class-arguments

Setting Arguments on a Program
******************************

.. todo::

   * Using dictionary syntax with nested classes as typed keys.
   * Using ``Value`` to change the arguments value at runtime.

Derive Program Variants
***********************

.. todo::

   * Explain helper methods to copy active arguments.
