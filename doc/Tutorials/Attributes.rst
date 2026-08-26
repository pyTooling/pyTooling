.. _TUTORIAL/Attributes:

Attributes
##########

A framework usually needs to know things about a user's code that the code itself doesn't say: which methods are
commands, which classes are plugins, which function handles ``--version``. The imperative answer is a registry that
every module has to remember to call. The declarative answer is an **attribute** - a decorator that carries data and
remembers where it was applied.

.. code-block:: Python

   @Command(name="version", help="Print version information.")
   def versionHandler(args):
     ...

   for handler in Command.GetFunctions():
     ...   # every function annotated with @Command, without a registry anywhere

This tutorial builds one from scratch.

.. seealso::

   :ref:`ATTR`
      |rarr| The reference for :mod:`pyTooling.Attributes`, including the predefined attributes.
   :ref:`TUTORIAL/Decorators`
      |rarr| The decorator mechanics an attribute is built on.


.. _TUTORIAL/Attributes/When:

When an attribute is the right tool
***********************************

Reach for one when **the data belongs to the entity, and the framework has to find the entity by the data**. Both
halves matter:

.. list-table::
   :header-rows: 1
   :widths: 34 66

   * - Use instead
     - When
   * - a plain decorator
     - the decorator *changes* what the function does. An attribute annotates, it doesn't wrap.
   * - a class field or a constant
     - nothing ever searches for it. A dictionary is simpler than an attribute class.
   * - a naming convention
     - the framework can find entities by name and the name is not also the description - ``test_*`` is the classic
       case, and :ref:`its limits <TUTORIAL/UnitTesting/Naming>` are exactly why markers exist.
   * - **an attribute**
     - the annotation is *data* - a name, a help text, a priority - and something has to enumerate every entity
       carrying it.


.. _TUTORIAL/Attributes/Define:

Step 1: define an attribute class
*********************************

Derive from :class:`~pyTooling.Attributes.Attribute` and give the initializer the parameters the annotation should
carry. Expose them as read-only properties, because whoever finds the annotation later has to read them.

.. code-block:: Python

   from pyTooling.Attributes import Attribute
   from pyTooling.Decorators import export, readonly

   @export
   class Command(Attribute):
     """Marks a function as the handler of a command line command."""

     _name: str    #: Name of the command as it is typed by a user.
     _help: str    #: One-line help text for the command.

     def __init__(self, name: str, help: str = "") -> None:
       self._name = name
       self._help = help

     @readonly
     def Name(self) -> str:
       return self._name

     @readonly
     def Help(self) -> str:
       return self._help

That is the whole definition. :class:`~pyTooling.Attributes.Attribute` supplies ``__call__`` - which is what makes
the class usable as a decorator - and the registry the ``Get***`` methods read.

.. hint::

   For a throw-away annotation that carries positional or keyword data and nothing else,
   :class:`~pyTooling.Attributes.SimpleAttribute` skips the class definition:
   ``@SimpleAttribute(kind="setup", order=3)``, read back as ``attribute.Args`` and ``attribute.KwArgs``.


.. _TUTORIAL/Attributes/Apply:

Step 2: apply it
****************

An attribute goes on a function, a method or a class. Several attributes stack, and an entity may carry the same
attribute class more than once.

.. code-block:: Python

   @Command(name="version", help="Print version information.")
   @Command(name="--version", help="Same, as a flag.")
   def versionHandler(args):
     ...

.. attention::

   **The entity is registered when the module is imported**, because that is when the decorator runs. A handler in a
   plug-in module that nothing imports is invisible to ``GetFunctions()`` - which is a feature when plug-ins are
   discovered by import, and a trap when they are not. If entities go missing, check the imports before the
   attributes.


.. _TUTORIAL/Attributes/Find:

Step 3: find what was annotated
*******************************

Three class-methods answer the three kinds of entity, and each yields what was annotated - not the attribute
instances:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Yields
   * - :meth:`Command.GetFunctions() <pyTooling.Attributes.Attribute.GetFunctions>`
     - every **function** annotated with ``@Command``
   * - :meth:`Command.GetClasses() <pyTooling.Attributes.Attribute.GetClasses>`
     - every **class** annotated with it; ``subclassOf=`` narrows further
   * - :meth:`Command.GetMethods() <pyTooling.Attributes.Attribute.GetMethods>`
     - every **method** annotated with it
   * - :meth:`Command.GetAttributes(entity) <pyTooling.Attributes.Attribute.GetAttributes>`
     - the attribute **instances** on one entity - this is where the data is read

So finding the entities and reading their data are two steps:

.. code-block:: Python

   for handler in Command.GetFunctions():
     for attribute in Command.GetAttributes(handler):
       print(f"{attribute.Name:<12} {attribute.Help}")

.. attention::

   The registry records **one entry per application**, so an entity carrying the attribute twice - like
   ``versionHandler`` above - is yielded twice by ``GetFunctions()``. Wrap the result in a :class:`set` (or
   :func:`dict.fromkeys`, to keep the order) when each entity should be processed once.

All three accept ``scope=``, which restricts the result to entities declared in one class or module - useful when
two plug-ins define a command of the same name.


.. _TUTORIAL/Attributes/Methods:

Step 4: methods, and why the meta-class helps
*********************************************

:meth:`~pyTooling.Attributes.Attribute.GetMethods` returns annotated methods of **every** class, which is rarely
what a framework wants - it usually has one object and asks *what does this one offer?* A class built with
:class:`~pyTooling.MetaClasses.ExtendedType` answers that itself:

.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class Application(metaclass=ExtendedType):
     @Command(name="build", help="Build the project.")
     def HandleBuild(self, args):
       ...

     @Command(name="clean", help="Remove build artifacts.")
     def HandleClean(self, args):
       ...

     def _helper(self):   # not annotated, so not found
       ...

   application = Application()
   for method, attributes in application.GetMethodsWithAttributes(predicate=Command).items():
     for attribute in attributes:
       print(f"{attribute.Name:<8} -> {method.__name__}")

.. attention::

   :meth:`~pyTooling.MetaClasses.ExtendedType.GetMethodsWithAttributes` returns a **dictionary** of method to
   attributes, so iterating it yields methods. ``.items()`` is what gives the pairs; iterating the result directly
   and unpacking raises ``TypeError: cannot unpack non-iterable function object``.

``predicate=`` accepts an attribute class or an iterable of them, and it matches **sub-classes** too - which is the
point of the next step.


.. _TUTORIAL/Attributes/Hierarchy:

Step 5: build a hierarchy and filter by it
******************************************

Attribute classes inherit, and each derived class gets its **own** registry - so a specialised attribute is found by
its own name *and* by its base's:

.. code-block:: Python

   class Alias(Command):
     """A command that is a shorthand for another one."""

   @Command(name="version")
   def versionHandler(args): ...

   @Alias(name="v")
   def shortHandler(args): ...

   Alias.GetFunctions()     # -> shortHandler
   Command.GetFunctions()   # -> versionHandler  (only!)

.. important::

   **Base and derived registries are separate, not nested.** ``Command.GetFunctions()`` does *not* return the
   function annotated with ``@Alias``. Each derived class receives fresh registries in
   ``Attribute.__init_subclass__``, which is what stops a derived attribute from reporting entities it was never
   attached to - and the cost is that the base doesn't collect its children's.

   Where sub-class matching *is* wanted, it is
   :meth:`~pyTooling.MetaClasses.ExtendedType.GetMethodsWithAttributes` with ``predicate=Command`` that provides it,
   and :meth:`~pyTooling.Attributes.Attribute.GetAttributes` with ``includeSubClasses=True`` - both of which test
   ``isinstance`` rather than reading one registry.


.. _TUTORIAL/Attributes/Scope:

A word on ``AttributeScope``
****************************

An attribute class may declare where it is meant to be used:

.. code-block:: Python

   from pyTooling.Attributes import Attribute, AttributeScope

   class TestCase(Attribute):
     _scope = AttributeScope.Method

.. caution::

   :class:`~pyTooling.Attributes.AttributeScope` currently documents **intent, not enforcement**. Applying a
   ``Method``-scoped attribute to a plain function raises nothing; the function is simply registered as a function
   and turns up in ``GetFunctions()`` rather than being rejected. Treat ``_scope`` as documentation for now, and
   check the entity kind yourself if a misapplication has to fail.

   Note also that ``_scope`` reads back from an attribute **instance** (``TestCase("x").Scope``), not from the class.


.. _TUTORIAL/Attributes/Example:

Where pyTooling uses this itself
********************************

* :ref:`ATTR/ArgParse` describes a whole :mod:`argparse` command line parser declaratively - the commands, their
  flags and their handlers are attributes on the handler methods.
* :ref:`CLIABS/CLIArgument` marks the nested argument classes of a
  :class:`~pyTooling.CLIAbstraction.Program`, so the outer class collects them when it is created. See
  :ref:`TUTORIAL/CLIAbstraction`.
* :ref:`TESTING/Markers` marks test cases and test suites by *title* instead of by a magic ``test_*`` name.
