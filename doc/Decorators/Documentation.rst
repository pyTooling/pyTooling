Documentation
#############

The :py:mod:`pyTooling.Decorators` package provides decorators to help with doc-strings.

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
