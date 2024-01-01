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
locations (see example). Another option for class and method attributes is defining a new classes using pyTooling’s
:ref:`META/ExtendedType` meta-class. Here the class itself offers helper methods for discovering annotated methods.

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


While all user-defined (and pre-defined) *attributes* already offer a powerful API
derived from :class:`~pyTooling.Attributes.Attribute`, the full potential can be experienced when used with class
declarations using :class:`pyTooling.MetaClass.ExtendedType` as it's meta-class.

.. code-block:: python

   class Annotation(Attribute):
     pass

   class Application(metaclass=ExtendedType):
     @Annotation("Some annotation data")
     def annotatedMethod(self):
       pass

   for method in Annotation.GetMethods():
     pass

In addition, an :mod:`pyTooling.Attributes.ArgParse` module is provided, which allows users to describe complex argparse
command line argument parser structures in a declarative way.

Attributes can create a complex class hierarchy. This helps in finding and filtering for annotated properties and
user-defined data. These search operations can be called globally on the attribute classes or locally within an
annotated class.

Use Cases
*********

**Annotate properties and user-defined data to methods.**

.. rubric:: Derived use cases:

* Describe a command line argument parser (argparse). |br|
  See `pyTooling.Attributes Documentation -> ArgParse Examples <https://pyTooling.GitHub.io/pyTooling.Attributes/ArgParse.html>`_
* Mark class members for documentation. |br|
  See `SphinxExtensions <https://sphinxextensions.readthedocs.io/en/latest/>`_ -> DocumentMemberAttribute

.. rubric:: Planned implementations:

* Annotate user-defined data to classes.
* Describe test cases and test suits to get a cleaner syntax for Python's unit
  tests.

Grouping Attributes
*******************

Technique
*********

The annotated data is stored in an additional ``__dict__`` entry for each
annotated method. By default the entry is called ``__pyattr__``. Multiple
attributes can be applied to the same method.


Common Attributes
*****************

* :class:`~pyTooling.Attributes.Attribute` class

Special Attributes
******************

This package brings special attribute implementations for:

* Python's :mod:`pyTooling.Attributes.ArgParse` including sub-parser support.
