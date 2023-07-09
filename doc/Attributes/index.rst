.. _ATTR:

Overview
########


Grouping Attributes
###################


ArgParse
########

pyAttributes Documentation
##########################

The Python package pyAttributes offers implementations of .NET-like attributes
realized with Python decorators. The package also offers a mixin-class to ease
using classes having annotated methods.

In addition, an ArgParseAttributes module is provided, which allows users to
describe complex argparse commond-line argument parser structures in a
declarative way.

Attributes can create a complex class hierarchy. This helps in finding and
filtering for annotated properties and user-defined data. These search
operations can be called globally on the attribute classes or locally within
an annotated class. Therefore the provided helper-mixin should be inherited.

Use Cases
*********

**Annotate properties and user-defined data to methods.**

.. rubric:: Derived use cases:

* Describe a command line argument parser (argparse). |br|
  See `pyAttributes Documentation -> ArgParse Examples <https://pyTooling.GitHub.io/pyAttributes/ArgParse.html>`_
* Mark class members for documentation. |br|
  See `SphinxExtensions <https://sphinxextensions.readthedocs.io/en/latest/>`_ -> DocumentMemberAttribute

.. rubric:: Planned implementations:

* Annotate user-defined data to classes.
* Describe test cases and test suits to get a cleaner syntax for Python's unit
  tests.

Technique
*********

The annotated data is stored in an additional ``__dict__`` entry for each
annotated method. By default the entry is called ``__pyattr__``. Multiple
attributes can be applied to the same method.


Common Attributes
*****************

* :class:`Attribute` class
* :class:`AttributeHelperMixin` class

Special Attributes
******************

This package brings special attribute implementations for:

* Python's :mod:`ArgParse` including sub-parser support.


.. toctree::
   :hidden:

   ArgParse
