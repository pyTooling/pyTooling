.. _ATTR:

Overview
########

The :mod:`pyTooling.Attributes` package offers implementations of *.NET-like attributes* realized with Python
:term:`decorators <decorator>`. While all user-defined (and pre-defined) *attributes* already offer a powerful API
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
