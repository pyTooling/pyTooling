.. _ATTR:

Overview
########

The :mod:`pyTooling.Attributes` package offers the base implementation of `.NET-like attributes <https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/reflection-and-attributes/>`__
realized with :term:`Python decorators <decorator>`. The annotated and declarative data is stored as instances of
:class:`~pyTooling.Attributes.Attribute` classes in an additional ``__pyattr__`` field per class, method or function.
The annotation syntax allows users to attach any structured data to classes, methods or functions. In many cases, a
user will derive a custom attribute from :class:`~pyTooling.Attributes.Attribute` and override the ``__init__`` method,
so user-defined parameters can be accepted when the attribute is constructed.

Later, classes, methods or functions can be searched for by querying the attribute class for attribute instance usage
locations (see 'Function Attributes' example). Another option for class and method attributes is defining a new classes
using pyTooling’s :ref:`META/ExtendedType` meta-class. Here the class itself offers helper methods for discovering
annotated methods (see 'Method Attributes' example). While all *user-defined* (and *pre-defined*) attributes offer a
powerful API derived from :class:`~pyTooling.Attributes.Attribute` class, the full potential can only be experienced
when using class declarations constructed by the :class:`pyTooling.MetaClasses.ExtendedType` meta-class.

Attributes can create a complex class hierarchy. This helps in finding and filtering for annotated data.


.. _ATTR/Goals:

Design Goals
************

The main design goals are:

* Allow meta-data annotation to Python language entities (class, method, function) as declarative syntax.
* Find applied attributes based on attribute type (methods on the attribute).
* Find applied attributes in a scope (find on class and on class' methods).
* Allow building a hierarchy of attribute classes.
* Filter attributes based on their class hierarchy.
* Reduce overhead to class creation time (do not impact object creation time).


.. _ATTR/Example:

Example
*******

.. grid:: 2

   .. grid-item:: **Function Attributes**
      :columns: 6

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         class Command(Attribute):
           def __init__(self, cmd: str, help: str = ""):
             pass

         class Flag(Attribute):
           def __init__(self, param: str, short: str = None, long: str = None, help: str = ""):
             pass

         @Command(cmd="version", help="Print version information.")
         @Flag(param="verbose", short="-v", long="--verbose", help="Default handler.")
         def Handler(self, args):
           pass

         for function in Command.GetFunctions():
           pass

   .. grid-item:: **Method Attributes**
      :columns: 6

      .. code-block:: Python

         from pyTooling.Attributes import Attribute
         from pyTooling.MetaClasses import ExtendedType

         class TestCase(Attribute):
           def __init__(self, name: str):
             pass

         class Program(metaclass=ExtendedType):
            @TestCase(name="Handler routine")
            def Handler(self, args):
              pass



         prog = Program()
         for method, attributes in prog.GetMethodsWithAttributes(predicate=TestCase):
           pass


.. _ATTR/UseCases:

Use Cases
*********

In general all classes, methods and functions can be annotated with additional meta-data. It depends on the application,
framework or library to decide if annotations should be applied imperatively as regular code or declaratively as
attributes via Python decorators.

With this in mind, the following use-cases and ideas can be derived:

.. rubric:: Derived Use Cases:

* Describe a command line argument parser (like ArgParse) in a declarative form. |br|
  See :ref:`pyTooling.Attributes.ArgParse Package and Examples <ATTR/ArgParse>`
* Mark nested classes, so later when the outer class gets instantiated, these nested classes are indexed or
  automatically registered. |br|
  See :ref:`CLIAbstraction <CLIABS>` |rarr| :ref:`CLIABS/CLIArgument`
* Mark methods in a class as test cases and classes as test suites, so test cases and suites are not identified based on
  a magic method name. |br|
  *Investigation ongoing / planned feature.*
* Mark class members as public or private and control visibility in auto-generated documentation. |br|
  See `SphinxExtensions <https://sphinxextensions.readthedocs.io/en/latest/>`_ |rarr| DocumentMemberAttribute


.. _ATTR/Predefined:

Predefined Attributes
*********************

pyTooling's attributes offers the :class:`~pyTooling.Attributes.Attribute` base-class to derive further attribute
classes. A derive :class:`~pyTooling.Attributes.SimpleAttribute` is also offered to accept any ``*args, **kwargs``
parameters for annotation of semi-structured meta-data.

It's recommended to derive an own hierarchy of attribute classes with well-defined parameter lists for the ``__init__``
method. Meta-data stored in attribute should be made accessible via (readonly) properties.

In addition, an :mod:`pyTooling.Attributes.ArgParse` subpackage is provided, which allows users to describe complex
argparse command line argument parser structures in a declarative way.

.. rubric:: Partial inheritance diagram:

.. inheritance-diagram:: pyTooling.Attributes.SimpleAttribute pyTooling.Attributes.ArgParse.DefaultHandler pyTooling.Attributes.ArgParse.CommandHandler pyTooling.Attributes.ArgParse.CommandLineArgument
   :parts: 1


.. _ATTR/Predefined/Attribute:

Attribute
=========

The :class:`~pyTooling.Attributes.Attribute` class implements half of the attribute's feature set. It implements the
instantiation and storage of attribute internal values as well as the search and lookup methods to find attributes. The
second half is implemented in the :class:`~pyTooling.MetaClasses.ExtendedType` meta-class. It adds attribute specific
methods to each class created by that meta-class.

Any attribute is applied on a class, method or function using Python's decorator syntax, because every attribute is
actually a decorator. In addition, such a decorator accepts parameters, which are used to instantiate an attribute class
and handover the parameters to that attribute instance.

Every instance of an attribute is registered at its class in a class variable. Further more, these instances are
distinguished if they are applied to a class, method or function.

* :meth:`~pyTooling.Attributes.Attribute.GetClasses` returns a generator to iterate all classes, this attribute was
  applied to.
* :meth:`~pyTooling.Attributes.Attribute.GetMethods` returns a generator to iterate all methods, this attribute was
  applied to.
* :meth:`~pyTooling.Attributes.Attribute.GetFunctions` returns a generator to iterate all functions, this attribute was
  applied to.
* :meth:`~pyTooling.Attributes.Attribute.GetAttributes` returns a tuple of applied attributes to the given method.


.. grid:: 3

   .. grid-item:: **Apply a class attribute**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute


         @Attribute()
         class MyClass:
           pass

   .. grid-item:: **Apply a method attribute**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         class MyClass:
           @Attribute()
           def MyMethod(self):
             pass

   .. grid-item:: **Apply a function attribute**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute


         @Attribute()
         def MyFunction(param):
           pass



.. grid:: 3

   .. grid-item:: **Find attribute usages of class attributes**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         for cls in Attribute.GetClasses():
           pass

   .. grid-item:: **Find attribute usages of method attributes**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         for method in Attribute.GetMethods():
           pass

   .. grid-item:: **Find attribute usages of function attributes**
      :columns: 4

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         for function in Attribute.GetFunctions():
           pass


.. rubric:: Condensed definition of class :class:`~pyTooling.Attributes.Attribute`

.. condensed-class:: pyTooling.Attributes.Attribute

.. rubric:: Planned Features

* Allow attributes to be applied only once per kind.
* Allow limitation of attributes to classes, methods or functions, so an attribute meant for methods can't be applied to
  a function or class.
* Allow filtering attribute with a predicate function, so values of an attribute instance can be checked too.


.. _ATTR/Predefined/SimpleAttribute:

SimpleAttribute
===============

The :class:`~pyTooling.Attributes.SimpleAttribute` class accepts any positional and any keyword arguments as data. That
data is made available via :attr:`~pyTooling.Attributes.SimpleAttribute.Args` and :attr:`~pyTooling.Attributes.SimpleAttribute.KwArgs`
properties.

.. code-block:: Python

   from pyTooling.Attributes import SimpleAttribute

   @SimpleAttribute(kind="testsuite")
   class MyClass:
     @SimpleAttribute(kind="testcase", id=1, description="Test and operator")
     def test_and(self):
       ...

     @SimpleAttribute(kind="testcase", id=2, description="Test xor operator")
     def test_xor(self):
       ...

**Condensed definition of class** :class:`~pyTooling.Attributes.SimpleAttribute`:

.. code-block:: python

   class SimpleAttribute(Attribute):
      def __init__(self, *args, **kwargs) -> None:
         ...

      @readonly
      def Args(self) -> Tuple[Any, ...]:
         ...

      @readonly
      def KwArgs(self) -> Dict[str, Any]:
         ...


.. _ATTR/UserDefined:

User-Defined Attributes
***********************

It's recommended to derive user-defined attributes from :class:`~pyTooling.Attributes.Attribute`, so the ``__init__``
method can be overriden to accept a well defined parameter list including type hints.

The example defines an ``Annotation`` attribute, which accepts a single string parameter. When the attribute is applied,
the parameter is stored in an  instance. The inner field is then accessible via readonly ``Annotation`` property.

.. grid:: 2

   .. grid-item:: **Find attribute usages of class attributes**
      :columns: 6

      .. condensed-class:: pyTooling.Attributes.SimpleAttribute

   .. grid-item:: **Find attribute usages of class attributes**
      :columns: 6

      .. code-block:: python

         from pyTooling.Attributes import Attribute

         class Annotation(Attribute):
           _annotation: str

           def __init__(self, annotation: str):
             self._annotation = annotation

           @readonly
           def Annotation(self) -> str:
             return self._annotation




.. _ATTR/Searching:

Searching Attributes
********************

An attribute is searched from **either end**: from the entity, to ask what was attached to it, or from the attribute
class, to ask what it was attached to. The second direction is the one a framework needs, and it is what makes an
attribute more than a decorator that stores a value.

.. grid:: 2

   .. grid-item:: **From the entity - what is attached here?**
      :columns: 6

      :meth:`~pyTooling.Attributes.Attribute.GetAttributes` reads the ``__pyattr__`` field of a single method and
      returns the attributes of this kind attached to it.

      .. code-block:: Python

         from pyTooling.Attributes import Attribute

         class Command(Attribute):
           pass

         class Program:
           @Command()
           def Version(self) -> None:
             pass

         attributes = Command.GetAttributes(Program.Version)

   .. grid-item:: **From the attribute - where was I used?**
      :columns: 6

      :meth:`~pyTooling.Attributes.Attribute.GetClasses`,
      :meth:`~pyTooling.Attributes.Attribute.GetMethods` and
      :meth:`~pyTooling.Attributes.Attribute.GetFunctions` return generators over every entity the attribute class was
      attached to - no module has to be imported or walked to find them.

      .. code-block:: Python

         for method in Command.GetMethods():
           print(method)

**No scan is involved in either direction.** Each attribute class keeps three registries -
:attr:`~pyTooling.Attributes.Attribute._classes`, :attr:`~pyTooling.Attributes.Attribute._methods` and
:attr:`~pyTooling.Attributes.Attribute._functions` - and the decorator appends to them while the module is being
imported, so a query is a list traversal at run time rather than a search. The cost is paid once, at class creation
time, which is the design goal above.

Every derived attribute class gets **its own** registries.
``__init_subclass__`` assigns fresh lists per subclass, so ``Command.GetMethods()``
never reports a method that only carries a ``Flag``, although both derive from :class:`~pyTooling.Attributes.Attribute`.

.. attention::

   An entity is only registered once its defining module has been **imported**. An attribute query in a plugin
   architecture therefore answers for the plugins loaded so far, not for the plugins installed.


.. _ATTR/Filtering:

Filtering Attributes
********************

**The first filter is the class the query is sent to.** ``Command.GetMethods()`` returns the methods carrying a
``Command``; ``Attribute.GetMethods()`` returns nothing, because the base-class was never attached to anything. A
hierarchy of attribute classes is therefore a hierarchy of queries, which is the design goal *filter attributes based
on their class hierarchy*.

Subclasses count as the attribute they derive from - but only in the entity direction.
:meth:`~pyTooling.Attributes.Attribute.GetAttributes` matches with :func:`isinstance`, so
``Command.GetAttributes(method)`` also returns a ``SpecialCommand`` attached to that method. The registries behind
:meth:`~pyTooling.Attributes.Attribute.GetMethods` are per class, so that query does **not** see the subclass.

The remaining filters narrow *where* an entity may be declared:

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - Method
     - Parameter
     - Accepts
   * - :meth:`~pyTooling.Attributes.Attribute.GetClasses`
     - ``scope``
     - A module - the class has to be defined in it - or a class, and then the class has to be **nested** in it.
   * - :meth:`~pyTooling.Attributes.Attribute.GetClasses`
     - ``subclassOf``
     - A class the annotated class has to derive from.
   * - :meth:`~pyTooling.Attributes.Attribute.GetMethods`
     - ``scope``
     - The class the method has to be defined in.
   * - :meth:`~pyTooling.Attributes.Attribute.GetFunctions`
     - ``scope``
     - A module the function has to be defined in.

.. code-block:: Python

   # every annotated class in this module
   Command.GetClasses(scope=sys.modules[__name__])

   # ... that is also a 'Handler'
   Command.GetClasses(scope=sys.modules[__name__], subclassOf=Handler)

.. attention::

   :meth:`~pyTooling.Attributes.Attribute.GetFunctions` accepts a **module** as its scope. Passing a class raises
   :exc:`NotImplementedError` rather than returning an empty generator.

.. hint::

   A class built by the :ref:`META/ExtendedType` meta-class offers the filter the other way round:
   ``GetMethodsWithAttributes`` asks *one class* which of its methods carry attributes, and its ``predicate``
   parameter takes an attribute class, an iterable of attribute classes, or ``None`` for all of them. Use it when the
   class is known and the attributes are not; use the queries above when the attribute is known and the classes are
   not.


.. _ATTR/Grouping:

Grouping Attributes
*******************

A set of attributes that always appear together can be applied as **one** attribute. Because every attribute class is
callable, its ``__call__`` is free to attach more than itself, and
:meth:`~pyTooling.Attributes.Attribute._AppendAttribute` is what attaches one attribute to an entity without going
through the decorator syntax.

The group attribute stays a normal attribute: it is registered on the entity like the ones it applies, so the entity
can afterwards be found through the group **or** through any of its members.

.. code-block:: Python

   from pyTooling.Attributes import Attribute, SimpleAttribute

   class GroupAttribute(Attribute):
      _id: str

      def __init__(self, id: str):
         self._id = id

      def __call__(self, entity: Entity) -> Entity:
         self._AppendAttribute(entity, SimpleAttribute(3, 4, id=self._id, name="attr1"))
         self._AppendAttribute(entity, SimpleAttribute(5, 6, id=self._id, name="attr2"))

         return entity


   class Grouped(TestCase):
      def test_Group_Simple(self) -> None:
         @SimpleAttribute(1, 2, id="my", name="Class1")
         @GroupAttribute("grp")
         class MyClass1:
            pass


.. _ATTR/Details:

Implementation Details
**********************

An attribute is stored **twice**, once per direction of the search described above.

.. _ATTR/Details/Entity:

On the entity
=============

The annotated data is stored in an additional ``__dict__`` entry on each annotated class, method or function. The
field is named by :data:`~pyTooling.Attributes.ATTRIBUTES_MEMBER_NAME`, which is ``__pyattr__``, and it holds a
**list**, so multiple attributes can be applied to the same entity.

New attributes are inserted at the **front** of that list. Decorators are applied bottom-up, so inserting rather than
appending gives back the order the decorators were written in:

.. code-block:: Python

   @Command(cmd="version")     # __pyattr__[0]
   @Flag(param="verbose")      # __pyattr__[1]
   def Version(self) -> None:
     pass

.. _ATTR/Details/Registry:

On the attribute class
======================

The same attribute instance is appended to :attr:`~pyTooling.Attributes.Attribute._classes`,
:attr:`~pyTooling.Attributes.Attribute._methods` or :attr:`~pyTooling.Attributes.Attribute._functions` of its own
class, chosen by what the entity is - :class:`~types.MethodType`, :class:`~types.FunctionType` or :class:`type`.
Anything else raises :exc:`TypeError`; class fields and module variables are not supported.

.. _ATTR/Details/Scope:

Scope
=====

:class:`~pyTooling.Attributes.AttributeScope` is an :class:`~enum.IntFlag` naming the language entities an attribute
is meant for - ``Class``, ``Method``, ``Function``, and ``Any`` as their union. A derived attribute states it by
overriding :attr:`~pyTooling.Attributes.Attribute._scope`, and it is readable through
:attr:`~pyTooling.Attributes.Attribute.Scope`.

It is what makes attribute **inheritance** possible: when the :ref:`META/ExtendedType` meta-class builds a class, it
walks the base-classes' ``__pyattr__`` and re-attaches every attribute whose scope contains ``Class`` to the derived
class. An attribute scoped to methods is not inherited this way, because it was never a statement about the class.


.. _ATTR/Consumers:

Consumers
*********

This abstraction layer is used by:

* ✅ Declarative definition of ArgParse parser rules. |br|
  :ref:`pyTooling.Attributes.ArgParse <ATTR/ArgParse>`
