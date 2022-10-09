.. _META:

Overview
########

Currently, the following meta-classes are provided:

.. contents:: Table of Contents
   :depth: 3

.. seealso::

   Meta Classes
     `Understanding Python metaclasses <https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/>`__

   Python Data Model
     General :ref:`Data Model <datamodel>` of Python and section about :ref:`__slots__ <slots>`.

.. _META/ExtendedType:

ExtendedType
############

The new meta-class :py:class:`~pyTooling.MetaClasses.ExtendedType` allows to implement :ref:`singletons <META/Singleton>`,
:ref:`slotted types <META/Slotted>` and combinations thereof.

Since Python 3, meta-classes are applied in a class definition by adding a named parameter called ``metaclass`` to the
list of derived classes (positional parameters). Further named parameters might be given to pass parameters to that new
meta-class.

.. code-block:: python

   class MyClass(metaclass=ExtendedType):
     pass

.. _META/Abstract:

Abstract Method
***************

.. todo:: META:: Needs documentation for Abstract Method

MustOverwrite Method
********************

.. todo:: META:: Needs documentation for MustOverwrite Method


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
        def __init__(self):
          pass

        def WriteLine(self, message):
          print(message)

.. _META/Slotted:

Slotted Type
************

A class defined with enabled ``useSlots`` behavior stores instance fields in slots. The meta-class,
translates all type-annotated fields in a class definition into slots. Slots allow a more efficient field storage and
access compared to dynamically stored and accessed fields hosted by ``__dict__``. This improves the memory footprint
as well as the field access performance of all class instances. This behavior is automatically inherited to all
derived classes.

.. code-block:: python

   class MyClass(metaclass=ExtendedType, useSlots=True):
     pass

.. admonition:: Example Usage

   .. code-block:: python

      class Node(metaclass=ExtendedType, useSlots=True):
        _parent: "Node"

        def __init__(self, parent: "Node" = None):
          self._parent = parent

      root = Node()
      node = Node(root)

.. _META/ObjectWithSlots:

ObjectWithSlots
===============

A class definition deriving from :py:class:`~pyTooling.MetaClasses.ObjectWithSlots` will bring the slotted type
behavior to that class and all derived classes.

.. code-block:: python

   class MyClass(ObjectWithSlots):
     pass


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

        def __init__(self, value : int = 0):
          self.value = value

        def __init__(self, value : str):
          self.value = int(value)

      a = A()
      print(a.value)

      b = A(3)
      print(b.value)

      c = A("42")
      print(c.value)
