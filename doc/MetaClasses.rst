.. _META:

Overview
########

Currently, the following meta-classes are provided:

.. #contents:: Table of Contents
   :depth: 3

.. seealso::

   Meta Classes
     `Understanding Python metaclasses <https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/>`__

   Python Data Model
     General :ref:`Data Model <datamodel>` of Python and section about :ref:`__slots__ <slots>`.

.. _META/ExtendedType:

ExtendedType
############

The new meta-class :class:`~pyTooling.MetaClasses.ExtendedType` allows to implement :ref:`singletons <META/Singleton>`,
:ref:`slotted types <META/Slotted>` and combinations thereof.

Since Python 3, meta-classes are applied in a class definition by adding a named parameter called ``metaclass`` to the
list of derived classes (positional parameters). Further named parameters might be given to pass parameters to that new
meta-class.

.. code-block:: python

   class MyClass(metaclass=ExtendedType):
     pass

.. _META/Slotted:

Slotted
*******

.. _META/Mixin:

Mixin
*****


.. _META/AbstractClass:

Abstract Class
**************

A class containing an :ref:`abstract method <META/AbstractMethod>` cannot be instantiated, but some classes have
nothing to mark abstract and still exist only to be derived from - a base-class collecting shared infrastructure,
for instance.

The :deco:`~pyTooling.MetaClasses.abstractclass` decorator declares a class as abstract (inheritance tree inner
node) without the need for abstract methods.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType, abstractclass

   @abstractclass
   class Base(metaclass=ExtendedType):
     def Method(self) -> None:
       ...

   class Derived(Base):
     pass

   Derived()   # fine
   Base()      # raises AbstractClassError

The decorator sets ``__abstractClass__`` on the class and recomputes ``__isAbstract__``, which is the same
computation :class:`~pyTooling.MetaClasses.ExtendedType` runs for abstract methods.

The marker belongs to the decorated class alone: :class:`~pyTooling.MetaClasses.ExtendedType` clears it on every
class it creates, so a derived class is concrete again unless it is decorated itself or inherits an abstract
method. The declaration therefore describes one class rather than a branch of the hierarchy.

.. seealso::

   :deco:`~pyTooling.MetaClasses.abstractmethod`
      |rarr| Mark a *method* as abstract, which makes its class abstract as a consequence.


.. _META/AbstractMethod:

Abstract Method
***************

The :deco:`~pyTooling.MetaClasses.abstractmethod` decorator marks a method as *abstract*. The original method gets
replaced by a method raising a :exc:`NotImplementedError`. When a class containing *abstract* methods is
instantiated, an :exc:`~pyTooling.Exceptions.AbstractClassError` is raised.

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
   the :ref:`@mustoverride <META/MustOverwrite>` decorator.

.. _META/MustOverwrite:

MustOverwrite Method
********************

The :deco:`~pyTooling.MetaClasses.mustoverride` decorator marks a method as *must override*. When a class containing
*must override* methods is instantiated, an :exc:`~pyTooling.Exceptions.MustOverrideClassError` is raised.

In contrast to :ref:`@abstractmethod <META/AbstractMethod>`, the method can still be called from a derived class
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

   If the method contain no code and throw an exception when called, use the :ref:`@abstractmethod <META/AbstractMethod>`
   decorator.


.. _META/Singleton:

Singleton
*********

A class defined with enabled ``singleton`` behavior implements the `singleton design pattern <https://en.wikipedia.org/wiki/Singleton_pattern>`__,
which allows only a single instance of that class to exist. If another instance is going to be created, a previously
cached instance of that class will be returned.

.. code-block:: python

   class MyClass(metaclass=ExtendedType, singleton=True):
     pass

.. admonition:: Example Usage

   .. code-block:: python

      class Terminal(metaclass=ExtendedType, singleton=True):
        def __init__(self) -> None:
          pass

        def WriteLine(self, message):
          print(message)

.. _META/Slottedd:

Slotted Type
************

A class defined with enabled ``slots`` behavior stores instance fields in slots. The meta-class, translates all
type-annotated fields in a class definition into slots. Slots allow a more efficient field storage and access compared
to dynamically stored and accessed fields hosted by ``__dict__``. This improves the memory footprint as well as the
field access performance of all class instances. This behavior is automatically inherited to all derived classes.

.. code-block:: python

   class MyClass(metaclass=ExtendedType, slots=True):
     pass

.. admonition:: Example Usage

   .. code-block:: python

      class Node(metaclass=ExtendedType, slots=True):
        _parent: "Node"

        def __init__(self, parent: "Node" = None) -> None:
          self._parent = parent

      root = Node()
      node = Node(root)

.. _META/SlottedObject:

SlottedObject
=============

A class definition deriving from :class:`~pyTooling.MetaClasses.SlottedObject` will bring the slotted type behavior to
that class and all derived classes.

+----------------------------------------+----------------------------------------+----------------------------------------------------------+
| Deriving from ``SlottedObject``        | Apply ``slotted`` Decorator            | Deriving from ``SlottedObject``                          |
+========================================+========================================+==========================================================+
| .. code-block:: Python                 | .. code-block:: Python                 | .. code-block:: Python                                   |
|                                        |                                        |                                                          |
|    class MyClass(SlottedObject):       |    @slotted                            |    class MyClass(metaclass=ExtendedType, slots=True):    |
|      pass                              |    class MyClass(SlottedObject):       |      pass                                                |
|                                        |      pass                              |                                                          |
+----------------------------------------+----------------------------------------+----------------------------------------------------------+


.. _META/Overloading:

Overloading
###########

.. warning:: This needs a clear definition before overloading makes sense...

This class provides a method dispatcher based on method signature's type
annotations.

.. admonition:: Example Usage

   .. code-block:: python

      class A(metaclass=Overloading):
        value = None

        def __init__(self, value : int = 0) -> None:
          self.value = value

        def __init__(self, value : str) -> None:
          self.value = int(value)

      a = A()
      print(a.value)

      b = A(3)
      print(b.value)

      c = A("42")
      print(c.value)
