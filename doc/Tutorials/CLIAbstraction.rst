.. _TUTORIAL/CLIAbstraction:

CLI Abstraction
###############

Calling another program from Python usually starts as a list of strings and ends as a bug: a path that needed
quoting, a flag whose spelling differs on Windows, a value concatenated with ``+`` in the wrong place. The list is
assembled far from where the arguments are decided, and nothing checks it.

:mod:`pyTooling.CLIAbstraction` turns the program into a **class** and each of its arguments into a **typed member**.
The assembling, escaping and platform-dependent spelling happen once, in the argument class, instead of at every
call site.

.. code-block:: Python

   git = Git()
   git[git.CommandCommit] = None
   git[git.FlagAll]       = True
   git[git.ValueMessage]  = "initial commit"

   git.ToArgumentList()   # -> ['git', 'commit', '-m', 'initial commit', '-a']

This tutorial builds that class.

.. seealso::

   :ref:`CLIABS`
      |rarr| The reference for :mod:`pyTooling.CLIAbstraction`.
   :ref:`TUTORIAL/Attributes`
      |rarr| ``@CLIArgument`` is an attribute; this is the mechanism behind it.


.. _TUTORIAL/CLIAbstraction/Choose:

Step 1: ``Program`` or ``Executable``?
**************************************

Two base-classes, one question: **does your class need to run the program, or only to describe the call?**

.. list-table::
   :header-rows: 1
   :widths: 22 40 38

   * - Base-class
     - Gives you
     - Choose it when
   * - :class:`~pyTooling.CLIAbstraction.Program`
     - argument members, ``ToArgumentList()``, ``__str__``, the executable resolved on ``PATH`` per platform
     - something else starts the process - a build system, a CI step, :class:`subprocess.Popen` in the caller - or
       you only want to *print* the command line
   * - :class:`~pyTooling.CLIAbstraction.Executable`
     - all of that, plus ``StartProcess()``, ``Send()``, ``GetLineReader()``, ``Terminate()``, ``Wait()`` and
       ``ExitCode``
     - your class starts the process and reads its output

:class:`~pyTooling.CLIAbstraction.Executable` derives from :class:`~pyTooling.CLIAbstraction.Program`, so the
choice is not final: describe first, and change the base-class when the class needs to run something.

.. hint::

   Start with :class:`~pyTooling.CLIAbstraction.Program` when in doubt. A class that only assembles a command line
   is trivially testable - ``ToArgumentList()`` returns a list you can assert on - while a class that starts
   processes needs one to be installed.


.. _TUTORIAL/CLIAbstraction/First:

Step 2: the class and its first argument
****************************************

An argument is a **nested class** derived from one of the predefined argument classes, marked with
:ref:`@CLIArgument() <CLIABS/CLIArgument>`. The nested class contributes nothing but its name and its base - the
base decides the pattern, and ``name=`` fills it in.

.. code-block:: Python

   from pyTooling.CLIAbstraction         import CLIArgument, Program
   from pyTooling.CLIAbstraction.Command import CommandArgument
   from pyTooling.CLIAbstraction.Flag    import ShortFlag, LongFlag

   class Git(Program):
     _executableNames = {
       "Darwin":  "git",
       "FreeBSD": "git",
       "Linux":   "git",
       "Windows": "git.exe",
     }

     @CLIArgument()
     class FlagVersion(LongFlag, name="version"): ...

     @CLIArgument()
     class CommandCommit(CommandArgument, name="commit"): ...

     @CLIArgument()
     class FlagAll(ShortFlag, name="a"): ...

Three things are worth naming:

.. rubric:: ``_executableNames`` maps :attr:`platform.system` to the file name

The executable is looked up on ``PATH`` when the object is constructed, and a missing one raises
:exc:`~pyTooling.CLIAbstraction.CLIAbstractionError` right there rather than at the first call. Pass
``executablePath=`` to bypass the lookup and name a file directly.

.. rubric:: The nested class' own name is how you address the argument

``git[git.CommandCommit]`` - the member name, not the command line spelling. Renaming ``--version`` to ``-V`` later
is a change to ``name=`` alone; every call site keeps working.

.. rubric:: ``...`` is the whole body

The nested class exists to be *named* and to *inherit*. Anything else in its body is a sign the wrong base-class
was chosen.


.. _TUTORIAL/CLIAbstraction/Setting:

Step 3: set the arguments and assemble
**************************************

Arguments are set through the indexer, with the value the argument carries - or ``None`` for one that carries
nothing:

.. code-block:: Python

   git = Git()
   git[git.CommandCommit] = None            # a command: no value
   git[git.FlagAll]       = True            # a flag: on
   git[git.ValueMessage]  = "initial commit"

   print(git.ToArgumentList())
   # ['git', 'commit', '-m', 'initial commit', '-a']

.. attention::

   **The order of the result is the order the arguments were declared in, not the order they were set.** ``-m``
   precedes ``-a`` above because ``ValueMessage`` is declared before ``FlagAll``. Declare the nested classes in the
   order the program expects them - commands before their flags - and the assembled list is right regardless of how
   the caller fills it in.

:meth:`~pyTooling.CLIAbstraction.Program.ToArgumentList` returns the list for :class:`subprocess.Popen`;
``str(program)`` returns the same thing quoted, for a log line or an error message.


.. _TUTORIAL/CLIAbstraction/Choosing:

Step 4: choosing the right argument class
*****************************************

Each predefined class knows one pattern. Pick by **what the program's syntax looks like**, then by prefix style -
every family has a ``Short``, a ``Long`` and a ``Windows`` variant, differing only in ``-``, ``--`` and ``/``.

.. list-table::
   :header-rows: 1
   :widths: 30 26 44

   * - Base-class
     - Assign
     - Renders as
   * - :class:`~pyTooling.CLIAbstraction.Command.CommandArgument`
     - ``None``
     - ``commit``
   * - :class:`~pyTooling.CLIAbstraction.Flag.LongFlag`
     - ``True``
     - ``--quiet``
   * - :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag`
     - ``"build/app"``
     - ``--output=build/app``
   * - :class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.LongTupleFlag`
     - ``"/usr/include"``
     - ``--include``, ``/usr/include`` |br| **two** entries in the list
   * - :class:`~pyTooling.CLIAbstraction.ValuedFlagList.LongValuedFlagList`
     - ``["m", "pthread"]``
     - ``--lib=m``, ``--lib=pthread``
   * - :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.LongOptionalValuedFlag`
     - ``None`` |br| ``"always"``
     - ``--color`` |br| ``--color=always``
   * - :class:`~pyTooling.CLIAbstraction.BooleanFlag.LongBooleanFlag`
     - ``True`` |br| ``False``
     - ``--with-tests`` |br| ``--without-tests``
   * - :class:`~pyTooling.CLIAbstraction.KeyValueFlag.LongKeyValueFlag`
     - ``{"NDEBUG": "1", "LEVEL": "2"}``
     - ``--DNDEBUG=1``, ``--DLEVEL=2``
   * - :class:`~pyTooling.CLIAbstraction.Argument.PathArgument`
     - a :class:`~pathlib.Path`
     - the path, positionally

.. rubric:: Single value vs. tuple vs. list

The three that carry a value differ in how the value reaches ``argv``, and mixing them up is the most common
mistake in an abstraction:

* :class:`~pyTooling.CLIAbstraction.ValuedFlag.LongValuedFlag` - **one** argv entry, name and value joined by
  ``=``. This is ``--output=build/app``.
* :class:`~pyTooling.CLIAbstraction.ValuedTupleFlag.LongTupleFlag` - **two** argv entries, the name and then the
  value. This is ``-m "initial commit"``, and it is what a program using :func:`getopt` with a separate value
  expects.
* :class:`~pyTooling.CLIAbstraction.ValuedFlagList.LongValuedFlagList` - the flag **repeated**, once per element of
  the assigned list. This is ``--lib=m --lib=pthread``, the shape of ``-I``, ``-D`` and ``-l`` in most compilers.

The test is what the program's own help text shows. ``--output=FILE`` is a valued flag; ``--output FILE`` is a tuple
flag; ``--lib LIB (may be given more than once)`` is a flag list.

.. hint::

   :class:`~pyTooling.CLIAbstraction.OptionalValuedFlag.LongOptionalValuedFlag` is for the flag that means one thing
   bare and another with a value - ``--color`` versus ``--color=always``. Assigning ``None`` gives the bare form.


.. _TUTORIAL/CLIAbstraction/Sharing:

Step 5: sharing arguments between program variants
**************************************************

A tool that exists in several variants - a native and a cross compiler, two versions of the same simulator - shares
most of its arguments. Put them in a **mixin** and derive each variant from it, so the argument classes are declared
once:

.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class GitArgumentsMixin(metaclass=ExtendedType, mixin=True):
     _executableNames = {"Linux": "git", "Windows": "git.exe", "Darwin": "git"}

     @CLIArgument()
     class FlagVersion(LongFlag, name="version"): ...

     @CLIArgument()
     class CommandCommit(CommandArgument, name="commit"): ...

   class Git(Program, GitArgumentsMixin): ...

   class GitWithLFS(Git):
     @CLIArgument()
     class CommandLFS(CommandArgument, name="lfs"): ...

See :ref:`META/Mixin` for what ``mixin=True`` does and why the second base-class needs it.


.. _TUTORIAL/CLIAbstraction/Running:

Step 6: running it
******************

Change the base-class to :class:`~pyTooling.CLIAbstraction.Executable` and the same class can start the process and
read its output line by line:

.. code-block:: Python

   class Git(Executable, GitArgumentsMixin): ...

   git = Git()
   git[git.CommandCommit] = None
   git[git.ValueMessage]  = "initial commit"

   git.StartProcess()
   for line in git.GetLineReader():
     print(line)

   git.Wait()
   if git.ExitCode != 0:
     raise BuildError(f"'{git}' failed with exit code {git.ExitCode}.")

.. caution::

   ``dryRun=True`` on the constructor is meant to make the program describe what it *would* run instead of running
   it, so a ``--dry-run`` mode in your own tool needs one constructor argument rather than a branch around every
   call. **It is not usable as it stands**: the dry-run paths call ``self.LogDryRun(...)``, which no class in
   pyTooling defines, so :meth:`~pyTooling.CLIAbstraction.Executable.StartProcess` raises
   :exc:`AttributeError` instead. Provide a ``LogDryRun`` method on your class until that is resolved.

   :meth:`~pyTooling.CLIAbstraction.Executable.GetLineReader` does behave as documented and raises
   :exc:`~pyTooling.CLIAbstraction.DryRunError` when the process was never started.
