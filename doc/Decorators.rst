.. _DECO:

Overview
########

The :mod:`pyTooling.Decorators` package provides decorators to:

* mark functions or methods as *not implemented*.
* control the visibility of classes and functions defined in a module.
* help with copying doc-strings from base-classes.

.. contents:: Table of Contents
   :depth: 2

.. _DECO/Abstract:

Abstract Methods
################

.. todo::

   DECO:: Refer to :func:`~pyTooling.MetaClasses.abstractmethod` and :func:`~pyTooling.MetaClasses.mustoverride`
   decorators from :ref:`meta classes <META>`.

.. important::

   Classes using decorators :ref:`@abstractmethod <DECO/AbstractMethod>` or :ref:`@mustoverride <DECO/MustOverride>`
   need to apply the meta-class :class:`ExtendedType <META/ExtendedType>` in the class definition.

.. _DECO/AbstractMethod:

@abstractmethod
***************

The :func:`~pyTooling.MetaClasses.abstractmethod` decorator marks a method as *abstract*.

The original method gets replaced by a method raising a :exc:`NotImplementedError`. This can happen, if an abstract
method is overridden but called via :pycode:`super()...`.

When a class containing *abstract* methods is instantiated, an :exc:`~pyTooling.Exceptions.AbstractClassError` is raised.

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

   If the abstract method contains code that should be called from an overriding method in a derived class, use the
   :ref:`@mustoverride <DECO/MustOverride>` decorator.

.. important::

   The class declaration must apply the metaclass :ref:`ExtendedType <META/ExtendedType>` so the decorator has an
   effect.


.. _DECO/MustOverride:

@mustoverride
*************

The :func:`~pyTooling.MetaClasses.mustoverride` decorator marks a method as *must override*.

When a class containing *must override* methods is instantiated, an :exc:`~pyTooling.Exceptions.MustOverrideClassError`
is raised.

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

   If the method contain no code and if it should throw an exception when called, use the
   :ref:`@abstractmethod <DECO/AbstractMethod>` decorator.

.. important::

   The class declaration must apply the metaclass :ref:`ExtendedType <META/ExtendedType>` so the decorator has an
   effect.

.. _DECO/DataAccess:

Data Access
###########

.. _DECO/readonly:

@readonly
*********

The :func:`~pyTooling.Decorators.readonly` decorator makes a property *read-only*. Thus the properties :pycode:`setter`
and :pycode:`deleter` can't be used.

.. admonition:: Example

   .. code-block:: Python

      class Data:
        _data: int

        def __init__(self, data: int):
          self._data = data

        @readonly
        @property
        def length(self) -> int:
          return 2 ** self._data


.. _DECO/classproperty:

@classproperty
**************

.. attention:: Class properties are currently broken in Python.


.. _DECO/Documentation:

Documentation
#############

.. _DECO/export:

@export
*******

The :func:`~pyTooling.Decorators.export` decorator makes module's entities (classes and functions) publicly visible.
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


.. _DECO/InheritDocString:

@InheritDocString
*****************

When a method in a derived class shall have the same doc-string as the doc-string of the base-class, then the decorator
:func:`~pyTooling.Decorators.InheritDocString` can be used to copy the doc-string from base-class' method to the
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


.. _DECO/Performance:

Performance
###########

.. _DECO/useslots:

@useslots
*********

.. todo:: DECO::useslots needs documentation


.. _DECO/mixin:

@mixin
******

.. todo:: DECO::mixin needs documentation


.. _DECO/singleton:

@singleton
**********

.. todo:: DECO::singleton needs documentation


.. _DECO/Misc:

Miscellaneous
#############

.. _DECO/notimplemented:

@notimplemented
***************

The :func:`~pyTooling.Decorators.notimplemented` decorator replaces a callable (function or method) with a callable
raising a :exc:`NotImplementedError` containing the decorators message parameter as an error message.

The original callable might contain code, but it's made unreachable by the decorator. The callable's name and doc-string
is copied to the replacing callable. A reference to the original callable is preserved in the
:pycode:`<callable>.__orig_func__` field.

.. admonition:: Example

   .. code-block:: Python

      class Data:
        @notimplemented("This function isn't tested yet.")
        def method(self, param: int):
          return 2 ** param



.. _DECO/OriginalFunction:

@OriginalFunction
*****************

The :func:`~pyTooling.MetaClasses.OriginalFunction` decorator attaches the original callable (function or method) to a
new callable object (function or method). This is helpful when the original callable gets replaced or wrapped e.g. by a
decorator.

The original function can be accesses via :pycode:`<callable>.__orig_func__`.

.. admonition:: Example

   .. code-block:: Python

      @export
      def abstractmethod(method: M) -> M:
        @OriginalFunction(method)
        @wraps(method)
        def func(self):
          raise NotImplementedError(f"Method '{method.__name__}' is abstract and needs to be overridden in a derived class.")

        func.__abstract__ = True
        return func
