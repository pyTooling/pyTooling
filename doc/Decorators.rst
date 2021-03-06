.. _DECO:

Overview
########

The :py:mod:`pyTooling.Decorators` package provides decorators to:

* help with copying doc-strings from base-classes
* control the visibility of classes and functions defined in a module


.. _DECO/Documentation:

Documentation
#############


.. _DECO/Documentation/InheritDocString:

InheritDocString
****************

When a method in a derived class shall have the same doc-string as the doc-string of the base-class, then the decorator
:py:func:`~pyTooling.Decorators.InheritDocString` can be used to copy the doc-string from base-class' method to the
method in the derived class.

.. admonition:: Example

   .. code:: python

      class BaseClass:
        def method(self):
          """Method's doc-string."""


      class DerivedClass(BaseClass):
        @InheritDocString(BaseClass)
        def method(self):
          pass


.. _DECO/Visibility:

Visibility
##########


.. _DECO/Visibility/export:

export
******

The :py:func:`~pyTooling.Decorators.export` decorator makes module's entities (classes and functions) publicly visible.
Therefore, these entities get registered in the module's variable ``__all__``.

Besides making these entities accessible via ``from foo import *``, Sphinx extensions like autoapi are reading
``__all__`` to infer what entities from a module should be auto documented.

.. admonition:: ``module.py``

   .. code:: python

      # Creating __all__ is only required, if variables need to be listed too
      __all__ = ["MY_CONST"]

      # Decorators can't be applied to fields, so it was manually registered in __all__
      MY_CONST = 42

      @export
      class MyClass:
        """This is a public class."""

      @export
      def myFunc():
        """This is a public function."""

      # Each application of "@export" will append an entry to __all__

.. admonition:: ``application.py``

   .. code:: python

      from .module import *

      inst = MyClass()
