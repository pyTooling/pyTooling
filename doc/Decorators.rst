.. _DECO:

Overview
########

The :mod:`pyTooling.Decorators` package provides decorators to:

* mark functions or methods as *not implemented*.
* control the visibility of classes and functions defined in a module.
* help with copying doc-strings from base-classes.

.. #contents:: Table of Contents
   :depth: 2

.. _DECO/Abstract:

Abstract Methods
################

.. todo::

   DECO:: Refer to :func:`~pyTooling.MetaClasses.abstractmethod` and :func:`~pyTooling.MetaClasses.mustoverride`
   decorators from :ref:`meta classes <META>`.

.. important::

   Classes using method decorators :ref:`@abstractmethod <DECO/AbstractMethod>` or
   :ref:`@mustoverride <DECO/MustOverride>` need to use the meta-class :ref:`ExtendedType <META/ExtendedType>`.

   Alternatively, classes can be derived from :ref:`SlottedObject <META/SlottedObject>` or apply decorators
   :ref:`DECO/slotted` or :ref:`DECO/mixin`.

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

        def __init__(self, data: int) -> None:
          self._data = data

        @readonly
        def Length(self) -> int:
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

.. _DECO/slotted:

@slotted
********

The size of class instances (objects) can be reduced by using :ref:`slots`. This decreases the object creation time and
memory footprint. In addition access to fields faster because there is no time consuming field lookup in ``__dict__``. A
class with 2 ``__dict__`` members has around 520 B whereas the same class structure uses only around 120 B if slots are
used. On CPython 3.10 using slots, the code accessing class fields is 10..25 % faster.

The :class:`~pyTooling.MetaClasses.ExtendedType` meta-class can automatically infer slots from type annotations. Because
the syntax for applying a meta-class is quite heavy, this decorator simplifies the syntax.

+--------------------------------------------------------+---------------------------------------------------------+
| Syntax using Decorator ``slotted``                     | Syntax using meta-class ``ExtendedType``                |
+========================================================+=========================================================+
| .. code-block:: Python                                 | .. code-block:: Python                                  |
|                                                        |                                                         |
|    @export                                             |    @export                                              |
|    @slotted                                            |    class A(metaclass=ExtendedType, slots=True):         |
|    class A:                                            |      _field1: int                                       |
|      _field1: int                                      |      _field2: str                                       |
|      _field2: str                                      |                                                         |
|                                                        |      def __init__(self, arg1: int, arg2: str) -> None:  |
|      def __init__(self, arg1: int, arg2: str) -> None: |        self._field1 = arg1                              |
|        self._field1 = arg1                             |        self._field2 = arg2                              |
|        self._field2 = arg2                             |                                                         |
|                                                        |                                                         |
+--------------------------------------------------------+---------------------------------------------------------+


.. _DECO/mixin:

@mixin
******

The size of class instances (objects) can be reduced by using :ref:`slots` (see :ref:`DECO/slotted`). If slots are used
in multiple inheritance scenarios, only one ancestor line can use slots. For other ancestor lines, it's allowed to
define the slot fields in the inheriting class. Therefore pyTooling allows marking classes as
:term:`mixin-classes <mixin-class>`.

The :class:`~pyTooling.MetaClasses.ExtendedType` meta-class can automatically infer slots from type annotations. If a
class is marked as a mixin-class, the inferred slots are collected and handed over to class defining slots. Because
the syntax for applying a meta-class is quite heavy, this decorator simplifies the syntax.

+--------------------------------------------------------+--------------------------------------------------------+
| Syntax using Decorator ``mixin``                       | Syntax using meta-class ``ExtendedType``               |
+========================================================+========================================================+
| .. code-block:: Python                                 | .. code-block:: Python                                 |
|                                                        |                                                        |
|    @export                                             |                                                        |
|    @slotted                                            |    @export                                             |
|    class A:                                            |    class A(metaclass=ExtendedType, slots=True):        |
|      _field1: int                                      |      _field1: int                                      |
|      _field2: str                                      |      _field2: str                                      |
|                                                        |                                                        |
|      def __init__(self, arg1: int, arg2: str) -> None: |      def __init__(self, arg1: int, arg2: str) -> None: |
|        self._field1 = arg1                             |        self._field1 = arg1                             |
|        self._field2 = arg2                             |        self._field2 = arg2                             |
|                                                        |                                                        |
|    @export                                             |    @export                                             |
|    class B(A):                                         |    class B(A):                                         |
|      _field3: int                                      |      _field3: int                                      |
|      _field4: str                                      |      _field4: str                                      |
|                                                        |                                                        |
|      def __init__(self, arg1: int, arg2: str) -> None: |      def __init__(self, arg1: int, arg2: str) -> None: |
|        self._field3 = arg1                             |        self._field3 = arg1                             |
|        self._field4 = arg2                             |        self._field4 = arg2                             |
|        super().__init__(arg1, arg2)                    |        super().__init__(arg1, arg2)                    |
|                                                        |                                                        |
|    @export                                             |                                                        |
|    @mixin                                              |    @export                                             |
|    class C(A):                                         |    class C(A, mixin=True):                             |
|      _field5: int                                      |      _field5: int                                      |
|      _field6: str                                      |      _field6: str                                      |
|                                                        |                                                        |
|      def Method(self) -> str:                          |      def Method(self) -> str:                          |
|        return f"{self._field5} -> {self._field6}"      |        return f"{self._field5} -> {self._field6}"      |
|                                                        |                                                        |
|    @export                                             |    @export                                             |
|    class D(B, C):                                      |    class D(B, C):                                      |
|      def __init__(self, arg1: int, arg2: str) -> None: |      def __init__(self, arg1: int, arg2: str) -> None: |
|        super().__init__(arg1, arg2)                    |        super().__init__(arg1, arg2)                    |
|                                                        |                                                        |
+--------------------------------------------------------+--------------------------------------------------------+


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
