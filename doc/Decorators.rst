.. _DECO:

Overview
########

The :py:mod:`pyTooling.Decorators` package provides decorators to:

* help with copying doc-strings from base-classes
* control the visibility of classes and functions defined in a module

.. contents:: Table of Contents
   :depth: 2

.. _DECO/Abstract:

Abstract Methods
################

.. todo::

   DECO:: Refer to :py:func:`~pyTooling.MetaClasses.abstractmethod` and :py:func:`~pyTooling.MetaClasses.mustoverride`
   decorators from :ref:`meta classes <META>`.

.. important::

   Classes using decorators :pycode:`@abstractmethod` or :pycode:`@mustoverrride` need to apply the metaclass
   :ref:`META/ExtendedType` in the class definition.

.. _DECO/AbstractMethod:

@abstractmethod
***************

The :py:func:`~pyTooling.MetaClasses.abstractmethod` decorator marks a method as *abstract*. The original method gets
replaced by a method raising a :py:exc:`NotImplementedError`. When a class containing *abstract* methods is
instantiated, an :py:exc:`~pyTooling.Exceptions.AbstractClassError` is raised.

.. rubric:: Example:
.. code-block:: Python

   class A(metaclass=ExtendedType):
     @abstractmethod
     def method(self) -> int:
       """Methods documentation."""

   class B(A):
     @InheritDocString(A)
     def method(self) -> int:
       return 2

.. hint::

   If the abstract method should contain code that should be called from an overriding method in a derived class, use
   the :ref:`@mustoverride <DECO/MustOverride>` decorator.

.. important::

   The class declaration must apply the metaclass :ref:`META/ExtendedType` so the decorator has an effect.


.. _DECO/MustOverride:

@mustoverride
*************

The :py:func:`~pyTooling.MetaClasses.mustoverride` decorator marks a method as *must override*. When a class containing
*must override* methods is instantiated, an :py:exc:`~pyTooling.Exceptions.MustOverrideClassError` is raised.

In contrast to :ref:`@abstractmethod <DECO/AbstractMethod>`, the method can still be called from a derived class
implementing an overridden method.

.. rubric:: Example:
.. code-block:: Python

   class A(metaclass=ExtendedType):
     @mustoverride
     def method(self) -> int:
       """Methods documentation."""
       return 2

   class B(A):
     @InheritDocString(A)
     def method(self) -> int:
       result = super().method()
       return result + 1

.. hint::

   If the method contain no code and throw an exception when called, use the :ref:`@abstractmethod <DECO/AbstractMethod>`
   decorator.

.. important::

   The class declaration must apply the metaclass :ref:`META/ExtendedType` so the decorator has an effect.

.. _DECO/DataAccess:

Data Access
###########

.. _DECO/classproperty:

@classproperty
**************

.. attention:: Class properties are currently broken in Python.


.. _DECO/Documentation:

Documentation
#############


.. _DECO/Documentation/InheritDocString:

@InheritDocString
*****************

When a method in a derived class shall have the same doc-string as the doc-string of the base-class, then the decorator
:py:func:`~pyTooling.Decorators.InheritDocString` can be used to copy the doc-string from base-class' method to the
method in the derived class.

.. admonition:: Example

   .. code-block:: python

      class BaseClass:
        def method(self):
          """Method's doc-string."""


      class DerivedClass(BaseClass):
        @InheritDocString(BaseClass)
        def method(self):
          pass


.. _DECO/Misc:

Miscellaneous
#############

.. _DECO/OriginalFunction:

@OriginalFunction
*****************

The :py:func:`~pyTooling.MetaClasses.OriginalFunction` decorator attaches the original function or method to a new
function object, when the original gets replaced or wrapped. The original function can be accesses with
:pycode:`meth.__orig_func__`.

.. rubric:: Example:
.. code-block:: Python

   @export
   def abstractmethod(method: M) -> M:
     @OriginalFunction(method)
     @wraps(method)
     def func(self):
       raise NotImplementedError(f"Method '{method.__name__}' is abstract and needs to be overridden in a derived class.")

     func.__abstract__ = True
     return func


.. _DECO/Visibility:

Visibility
##########


.. _DECO/Visibility/export:

@export
*******

The :py:func:`~pyTooling.Decorators.export` decorator makes module's entities (classes and functions) publicly visible.
Therefore, these entities get registered in the module's variable ``__all__``.

Besides making these entities accessible via ``from foo import *``, Sphinx extensions like autoapi are reading
``__all__`` to infer what entities from a module should be auto documented.

.. admonition:: ``module.py``

   .. code-block:: python

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

   .. code-block:: python

      from .module import *

      inst = MyClass()
