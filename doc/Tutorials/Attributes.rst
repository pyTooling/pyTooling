.. _TUTORIAL/Attributes:

Attributes
##########

A framework usually needs to know things about a user's code that the code itself doesn't say: which classes are
plugins, which function or methods handle a callback. An **attribute** is a decorator that carries that data and
remembers where it was applied - the same idea as
`.NET attributes <https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/reflection-and-attributes/>`__,
which is where :mod:`pyTooling.Attributes` takes it from.

.. code-block:: Python

   @Plugin(name="MyPlugin", version="1.0.0")
   class MyPlugin:
     ...

   for plugin in Plugin.GetClasses():
     ...   # every class annotated with @Plugin, without a registry anywhere

This tutorial builds one from scratch: a plug-in system where a plug-in is a class, its metadata travels with it, and
the framework finds every plug-in without the plug-in ever calling the framework.


.. _TUTORIAL/Attributes/Three:

Three ways to know what a program declares
******************************************

Attributes are the third of them, and the differences are worth seeing side by side before the mechanics.

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Approach
     - How the framework learns
     - Costs
   * - **imperative**
     - the plug-in module calls :pycode:`register(MarkdownReader, "markdown")` itself
     - the call is separate from the thing it registers, so the two drift; and every plug-in has to remember to make
       it
   * - **meta-class / registry**
     - a base-class' :meth:`~object.__init_subclass__` - or a meta-class' :meth:`~object.__new__` - adds each
       subclass to a class variable as it is created
     - nothing to remember, but it only reaches **classes**, it forces the plug-in to derive from *your* base-class,
       and the metadata has nowhere to live except more class variables
   * - **attribute**
     - the decorator records itself on the entity, and the attribute class keeps a registry of where it was applied
     - reaches classes, methods *and* functions, carries typed data of its own, and leaves the plug-in's inheritance
       alone

The registry approach is not a poor relation - :class:`~pyTooling.Attributes.Attribute` uses
:meth:`~object.__init_subclass__` internally for exactly that reason, to give every derived attribute class its own
registry. It is the right tool when *being a subclass* is already the thing you want to enumerate. It stops being
the right tool the moment the annotation carries data, or has to sit on a function.

.. seealso::

   :ref:`ATTR`
      |rarr| The reference for :mod:`pyTooling.Attributes`, including the predefined attributes.
   :ref:`DECO`
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
     - the annotation is *data* - a name, a version, a priority - and something has to enumerate every entity
       carrying it.

A plug-in system needs both halves at once, which is why it is the example this tutorial uses: the name and version
belong to the plug-in class, and the host application has to enumerate every plug-in it can find.


.. _TUTORIAL/Attributes/Plugins:

Example 1: a class-based plug-in mechanism
******************************************

A plug-in is a class, its metadata travels with it, and the host finds every plug-in without the plug-in ever
calling the host. Four steps: define the attribute, apply it, load the modules, find what was annotated.


.. _TUTORIAL/Attributes/Define:

Step 1: define an attribute class
=================================

Derive from :class:`~pyTooling.Attributes.Attribute` and give the initializer the parameters the annotation should
carry. Expose them as read-only properties, because whoever finds the annotation later has to read them.

.. code-block:: Python

   from pyTooling.Attributes import Attribute
   from pyTooling.Decorators import export, readonly
   from pyTooling.Versioning import SemanticVersion

   @export
   class Plugin(Attribute):
     """Marks a class as a plug-in of this application."""

     _name:    str             #: Name the plug-in is selected by.
     _version: SemanticVersion  #: Version of the plug-in, as its author declares it.

     def __init__(self, name: str, version: str = "0.0.0") -> None:
       self._name = name
       self._version = SemanticVersion.Parse(version)

     @readonly
     def Name(self) -> str:
       return self._name

     @readonly
     def Version(self) -> SemanticVersion:
       return self._version

The parameter is accepted as a string and stored as a :class:`~pyTooling.Versioning.SemanticVersion`, so two
plug-in versions can be compared instead of only printed.

That is the whole definition. Two things come from the base-class: ``__call__``, which is what lets the class be
used as a decorator, and the registry that the ``Get***`` methods read.

.. hint::

   For a quick and simple annotation that carries positional or keyword data and nothing else,
   :class:`~pyTooling.Attributes.SimpleAttribute` skips the class definition entirely:

   .. code-block:: Python

      from pyTooling.Attributes import SimpleAttribute

      @SimpleAttribute(kind="reader", order=3)
      class MarkdownReader:
        ...

      attribute = SimpleAttribute.GetAttributes(MarkdownReader)[0]
      attribute.Args     # -> ()
      attribute.KwArgs   # -> {'kind': 'reader', 'order': 3}


.. _TUTORIAL/Attributes/Apply:

Step 2: apply it
================

An attribute goes on a class, a method or a function. Several attributes stack, and an entity may carry the same
attribute class more than once.

The plug-in declares what it *is* through the attribute, and what it *does* through an ordinary base-class the
application defines. The two are independent, and that separation is the point: ``Reader`` is the interface, and
``@Plugin`` is the metadata.

.. code-block:: Python

   from pathlib import Path

   from pyTooling.MetaClasses import ExtendedType, abstractmethod

   # the application's own interface
   class Reader(metaclass=ExtendedType):
     @abstractmethod
     def Read(self, path: Path) -> str:
       """Read the document at 'path' and return its text."""

   # plugins/markdown.py
   @Plugin(name="markdown", version="1.2.0")
   class MarkdownReader(Reader):
     def Read(self, path: Path) -> str:
       return path.read_text(encoding="utf-8")

An attribute carrying no data at all is written without parentheses - :pycode:`@Plugin` rather than
:pycode:`@Plugin()` - but a plug-in almost always has a name, so the parenthesised form is the usual one here.

.. important::

   **The interface is built with** :class:`~pyTooling.MetaClasses.ExtendedType`, and that is not decoration. It
   makes :meth:`~pyTooling.MetaClasses.abstractmethod` reject a plug-in that forgot to implement :pycode:`Read`,
   and - as :ref:`the second example <TUTORIAL/Attributes/Hooks>` shows - it is what makes annotated **methods**
   findable at all. A plug-in class alone does not need it; a plug-in class whose *methods* carry attributes does.


.. _TUTORIAL/Attributes/Load:

Step 3: load the plug-in modules
================================

.. attention::

   An entity is registered when its module is imported, because that is when the decorator runs. A plug-in in a
   module nothing imports is invisible to :pycode:`GetClasses()`.

This is the single thing that catches people out, and for a plug-in system it is not an edge case - it *is* the
mechanism. Discovery is two steps that are easy to mistake for one: **import the modules**, then **ask the
attribute**. A framework that only does the second finds nothing and looks broken.

.. code-block:: Python

   from importlib import import_module
   from pathlib   import Path

   def LoadPlugins(directory: Path) -> None:
     """Import every plug-in module, so its decorators run and register what they annotate."""
     for module in sorted(directory.glob("*.py")):
       if not module.stem.startswith("_"):
         import_module(f"{directory.name}.{module.stem}")

Before that sweep :pycode:`Plugin.GetClasses()` yields nothing; afterwards it yields one class per imported plug-in.
Nothing else changed - the registry was simply empty because no decorator had run yet.

.. tip::

   Scanning a directory is the simplest loader and the right one for plug-ins shipped inside the application. For
   plug-ins installed as *separate distributions*, use
   `entry points <https://packaging.python.org/en/latest/specifications/entry-points/>`__: the installer records
   them, :func:`importlib.metadata.entry_points` lists them without importing anything, and calling
   :meth:`~importlib.metadata.EntryPoint.load` on one imports that module - at which point the attribute registry
   fills exactly as above. The two compose; the attribute doesn't care which one imported the module.


.. _TUTORIAL/Attributes/Find:

Step 4: find what was annotated
===============================

Three class-methods answer the three kinds of entity, and each yields what was annotated - not the attribute
instances:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Yields
   * - :meth:`Plugin.GetClasses() <pyTooling.Attributes.Attribute.GetClasses>`
     - every **class** annotated with ``@Plugin``; ``subclassOf=`` narrows further
   * - :meth:`Plugin.GetFunctions() <pyTooling.Attributes.Attribute.GetFunctions>`
     - every **function** annotated with it
   * - :meth:`Plugin.GetMethods() <pyTooling.Attributes.Attribute.GetMethods>`
     - every **method** annotated with it
   * - :meth:`Plugin.GetAttributes(entity) <pyTooling.Attributes.Attribute.GetAttributes>`
     - the attribute **instances** on one entity - this is where the data is read

So finding the plug-ins and reading their metadata are two steps:

.. code-block:: Python

   for pluginClass in Plugin.GetClasses():
     for attribute in Plugin.GetAttributes(pluginClass):
       print(f"{attribute.Name:<10} {attribute.Version}  -> {pluginClass.__name__}")

.. code-block:: text

   markdown   1.2.0  -> MarkdownReader
   asciidoc   0.1.0  -> AsciiDocReader

``subclassOf=`` is what makes this usable in an application with more than one kind of plug-in. It filters the
**annotated classes by their own base-class**, so one attribute can mark every plug-in while each extension point
asks only for the ones it can use:

.. code-block:: Python

   Plugin.GetClasses(subclassOf=Reader)   # -> MarkdownReader, AsciiDocReader
   Plugin.GetClasses(subclassOf=Writer)   # -> HtmlWriter

``scope=`` restricts the result to entities declared in one module or nested in one class - useful when two plug-ins
declare a class of the same name.

.. attention::

   The registry records **one entry per application**, so an entity carrying the attribute twice is yielded twice by
   :pycode:`GetClasses()`. Wrap the result in a :class:`set` (or :func:`dict.fromkeys`, to keep the order) when each
   entity should be processed once.


.. _TUTORIAL/Attributes/Hooks:

Example 2: hooks on a plug-in's methods
***************************************

The first example annotated *classes*. The same mechanism works one level down, on the **methods inside** a
plug-in: a plug-in that reacts to events declares which method handles which event, instead of the host calling
methods by a magic name.

This example builds on the first - ``Plugin`` still marks the class; ``Hook`` marks the methods within it.


.. _TUTORIAL/Attributes/Methods:

Step 1: define a second attribute
=================================

An attribute class per *kind* of annotation. ``Hook`` carries the event name:

.. code-block:: Python

   class Hook(Attribute):
     """Marks a method as the handler of one application event."""

     _event: str  #: Name of the event this method handles.

     def __init__(self, event: str) -> None:
       self._event = event

     @readonly
     def Event(self) -> str:
       return self._event

.. _TUTORIAL/Attributes/AskOneObject:

Step 2: ask one object what it offers
=====================================

:meth:`~pyTooling.Attributes.Attribute.GetMethods` returns annotated methods of **every** class, which is rarely what
a host wants - it holds one plug-in instance and asks *what does this one offer?* A class built with
:class:`~pyTooling.MetaClasses.ExtendedType` answers that itself:

.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   @Plugin(name="markdown", version="1.2.0")
   class MarkdownReader(Reader, metaclass=ExtendedType):
     @Hook("open")
     def OnOpen(self, path):
       ...

     @Hook("close")
     def OnClose(self, path):
       ...

     def OnError(self, error):   # not annotated, so not found
       ...

   plugin = MarkdownReader()
   for method, attributes in plugin.GetMethodsWithAttributes(predicate=Hook).items():
     for attribute in attributes:
       print(f"{attribute.Event:<6} -> {method.__name__}")

.. code-block:: text

   open   -> OnOpen
   close  -> OnClose

.. attention::

   :meth:`~pyTooling.MetaClasses.ExtendedType.GetMethodsWithAttributes` returns a **dictionary** of method to
   attributes, so iterating it yields methods. ``.items()`` is what gives the pairs; iterating the result directly
   and unpacking raises ``TypeError: cannot unpack non-iterable function object``.

``OnError`` is a perfectly ordinary public method; it is absent from the result because it carries no ``@Hook``,
not because of how it is named. That is the whole difference from a naming convention.

The same answer can be had from the attribute instead of from the object, which is the right way round when the
host wants *every* plug-in's handlers rather than one plug-in's:

.. code-block:: Python

   for method in Hook.GetMethods():
     for attribute in Hook.GetAttributes(method):
       print(f"{attribute.Event:<6} -> {method.__qualname__}")

.. code-block:: text

   open   -> MarkdownReader.OnOpen
   close  -> MarkdownReader.OnClose

.. important::

   :meth:`~pyTooling.Attributes.Attribute.GetMethods` only ever finds methods of classes built with
   :class:`~pyTooling.MetaClasses.ExtendedType`. When the decorator runs, a method in a class body is still a plain
   function - it becomes a method only once the class object exists - so the annotation is filed under *functions*.
   ``ExtendedType`` re-files it while creating the class. Without the meta-class, the same method turns up in
   :pycode:`GetFunctions()` and :pycode:`GetMethods()` stays empty.

``predicate=`` accepts an attribute class or an iterable of them, and it matches **sub-classes** too - which is the
point of the next step.


.. _TUTORIAL/Attributes/Hierarchy:

Step 3: build a hierarchy and filter by it
==========================================

Attribute classes inherit, and each derived class gets its **own** registry - so a specialised attribute is found by
its own name, and only by its own name:

.. code-block:: Python

   class ExperimentalPlugin(Plugin):
     """A plug-in that may be withdrawn without a deprecation period."""

   @Plugin(name="markdown", version="1.2.0")
   class MarkdownReader(Reader): ...

   @ExperimentalPlugin(name="asciidoc", version="0.1.0")
   class AsciiDocReader(Reader): ...

   ExperimentalPlugin.GetClasses()   # -> AsciiDocReader
   Plugin.GetClasses()               # -> MarkdownReader  (only!)

.. important::

   **Base and derived registries are separate, not nested.** :pycode:`Plugin.GetClasses()` does *not* return the
   class annotated with ``@ExperimentalPlugin``. Each derived class receives fresh registries in
   ``Attribute.__init_subclass__``, which is what stops a derived attribute from reporting entities it was never
   attached to - and the cost is that the base doesn't collect its children's.

   So an application wanting *every* plug-in has to ask each attribute class it defines. Where sub-class matching
   *is* wanted for free, it comes from
   :meth:`~pyTooling.MetaClasses.ExtendedType.GetMethodsWithAttributes` with :pycode:`predicate=Plugin`, and from
   :meth:`~pyTooling.Attributes.Attribute.GetAttributes` with :pycode:`includeSubClasses=True` - both of which
   test ``isinstance`` rather than reading one registry.


.. _TUTORIAL/Attributes/Scope:

A word on ``AttributeScope``
****************************

An attribute class may declare where it is meant to be used:

.. code-block:: Python

   from pyTooling.Attributes import Attribute, AttributeScope

   class Hook(Attribute):
     _scope = AttributeScope.Method

.. caution::

   ``_scope`` currently documents **intent, and nothing enforces it** - see
   `#384 <https://github.com/pyTooling/pyTooling/issues/384>`__. Applying a ``Class``-scoped attribute to a
   function is accepted silently, and the function is then registered in a list that attribute's own scope says it
   can never hold.

   Two cases have to be told apart, because only one of them is fixable where the attribute is applied:

   * **class versus function/method** *is* decidable at that moment, so this mismatch should raise and today does
     not;
   * **method versus function** is *not* decidable there - as :ref:`the previous example <TUTORIAL/Attributes/Hooks>`
     explains, a method is still a plain function while the decorator runs.

   So until #384 is resolved: check the entity kind yourself if a misapplication has to fail.

   Note also that ``_scope`` reads back from an attribute **instance** - :pycode:`Hook("open").Scope` - and not
   from the class.


.. _TUTORIAL/Attributes/UseCases:

Attribute use cases
*******************

Plug-ins are one application of the pattern. It recurs wherever a framework has to find code by what it *means*
rather than by what it is called - and three of those are inside pyTooling itself.


.. _TUTORIAL/Attributes/Testcases:

Finding testcases and testsuites
================================

A test runner finds tests by a magic name - ``test_*`` - which forces the identifier to be both the selector and
the description, and leaves nowhere to put a title with spaces in it. An attribute separates the two:

.. code-block:: Python

   class testcase(Attribute):
     """Marks a method as a testcase and gives it a human-readable title."""

     def __init__(self, title: str) -> None:
       self._title = title

     @readonly
     def Title(self) -> str:
       return self._title

   class ArithmeticTests(metaclass=ExtendedType):
     @testcase("adds two positive numbers")
     def CheckAddition(self) -> None:
       ...

The method keeps a name a developer can type on a command line, and the annotation carries the sentence a report
should print. It is the same trade the plug-in example makes: ``MarkdownReader`` keeps a class name Python can
import, and ``@Plugin(name="markdown")`` carries the name a user types.

pyTooling ships this as :ref:`finding testcases and testsuites <TESTING/Markers>`.


.. _TUTORIAL/Attributes/ArgParse:

Declarative argparse
====================

A command line parser is usually built imperatively - one ``add_argument()`` call per flag, far away from the
function that handles it. :ref:`ATTR/ArgParse` inverts that: the commands, their flags and their handlers are
attributes on the handler methods, and the :class:`~argparse.ArgumentParser` is assembled from them.

.. code-block:: Python

   @CommandHandler("build", help="Build the project.")
   @LongValuedFlag("--target", dest="target", help="Build target.")
   def HandleBuild(self, args) -> None:
     ...

The flag and the code that receives it cannot drift apart, because they are the same declaration.


.. _TUTORIAL/Attributes/CLIArguments:

Collecting a program's CLI arguments
====================================

:ref:`CLIABS/CLIArgument` marks the nested argument classes of a
:class:`~pyTooling.CLIAbstraction.Program`, so the outer class collects them when it is created - the same
find-by-annotation step as :pycode:`Plugin.GetClasses()`, scoped to one class instead of a whole module.
