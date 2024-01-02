.. _ATTR:

Overview
########

The :mod:`pyTooling.Attributes` package offers the base implementation of `.NET-like attributes <https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/reflection-and-attributes/>`__
realized with :term:`Python decorators <decorator>`. The annotated and declarative data is stored as instances of
:class:`~pyTooling.Attributes.Attribute` classes in an additional ``__pyattr__`` field per class, method or function.
The annotation syntax allows users to attache any structured data to classes, methods or functions. In many cases, a
user will derive a custom attribute from :class:`~pyTooling.Attributes.Attribute` and override the ``__init__`` method,
so user-defined parameters can be accepted when the attribute is constructed.

Later, classes, methods or functions can be searched for by querying the attribute class for attribute instance usage
locations (see 'Function Attributes' example). Another option for class and method attributes is defining a new classes
using pyTooling’s :ref:`META/ExtendedType` meta-class. Here the class itself offers helper methods for discovering
annotated methods (see 'Method Attributes' example). While all *user-defined* (and *pre-defined*) attributes offer a
powerful API derived from :class:`~pyTooling.Attributes.Attribute` class, the full potential can only be experienced
when using class declarations constructed by the :class:`pyTooling.MetaClass.ExtendedType` meta-class.

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

pyTooling's attributes offers the :class:`~pyTooling.Attributes.Attribute` base-class to derive futher attribute classes.
A derive :class:`~pyTooling.Attributes.SimpleAttribute` is also offered to accept any ``*args, **kwargs`` parameters for
annotation of semi-structured meta-data.

It's recommended to derive an own hierarchy of attribute classes with well-defined parameter lists for the ``__init__``
method. Meta-data stored in attribute should be made accessible via (readonly) properties.

In addition, an :mod:`pyTooling.Attributes.ArgParse` subpackage is provided, which allows users to describe complex
argparse command line argument parser structures in a declarative way.

.. rubric:: Partial inheritance diagram:

.. inheritance-diagram:: pyTooling.Attributes.SimpleAttribute pyTooling.Attributes.ArgParse.DefaultHandler pyTooling.Attributes.ArgParse.CommandHandler pyTooling.Attributes.ArgParse.CommandLineArgument
   :parts: 1


**Condensed definition of class** :class:`~pyTooling.Attributes.Attribute`:

.. code-block:: python

   class Attribute:  # (metaclass=ExtendedType, slots=True):
      # Ensure each derived class has its own instances of class variables.
      def __init_subclass__(cls, **kwargs: Dict[str, Any]) -> None:
        ...

      # Make all classes derived from Attribute callable, so they can be used as a decorator.
      def __call__(self, entity: Entity) -> Entity:
        ...

      @classmethod
      def GetFunctions(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
        ...

      @classmethod
      def GetClasses(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
        ...

      @classmethod
      def GetMethods(cls, scope: Type = None, predicate: TAttributeFilter = None) -> Generator[TAttr, None, None]:
        ...

      @classmethod
      def GetAttributes(cls, method: MethodType, includeSubClasses: bool = True) -> Tuple['Attribute', ...]:
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



.. code-block:: python

   class Annotation(Attribute):
     pass

   class Application(metaclass=ExtendedType):
     @Annotation("Some annotation data")
     def annotatedMethod(self):
       pass

   for method in Annotation.GetMethods():
     pass


.. _ATTR/Searching:

Searching Attributes
********************

.. todo:: Attributes:: Searching Attributes


.. _ATTR/Filtering:

Filtering Attributes
********************

.. todo:: Attributes:: Filtering Attributes


.. _ATTR/Grouping:

Grouping Attributes
*******************

.. todo:: Attributes:: Grouping Attributes


.. _ATTR/Details:

Implementation Details
**********************

.. todo:: Attributes:: Implementation details


The annotated data is stored in an additional ``__dict__`` entry for each
annotated method. By default the entry is called ``__pyattr__``. Multiple
attributes can be applied to the same method.


.. _ATTR/Consumers:

Consumers
*********

This abstraction layer is used by:

* ✅ Declarative definition of ArgParse parser rules. |br|
  :ref:`pyTooling.Attributes.ArgParse <ATTR/ArgParse>`
