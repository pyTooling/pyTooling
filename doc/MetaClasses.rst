.. _META:

Overview
########

Currently, the following meta-classes are provided:

.. contents:: Table of Contents
   :local:
   :depth: 1



.. seealso::

   Understanding Python metaclasses
     https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/

   Python data model for :ref:`__slots__ <slots>`.


.. _META/Overloading:

Overloading
###########

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



.. _META/ExtendedType:

ExtendedType
############

.. _META/Singleton:

Singleton
*********

.. _META/Slotted:

Slotted Type
************


.. todo::

   Document ``ExtendedType`` which replaces ``Singleton`` and ``SlottedType``.

   This class implements the `singleton design pattern <https://en.wikipedia.org/wiki/Singleton_pattern>`_
   as a Python meta class.

   .. admonition:: Example Usage

      .. code-block:: python

         class Terminal(metaclass=ExtendedType, singleton=True):
           def __init__(self):
             pass

           def WriteLine(self, message):
             print(message)


   All type-annotated fields in a class get stored in a slot rather than in ``__dict__``. This improves the memory
   footprint as well as the field access performance of all class instances. The behavior is automatically inherited to
   all derived classes.

   .. admonition:: Example Usage

      .. code-block:: python

         class Node(metaclass=ExtendedType, useSlots=True):
           _parent: "Node"

           def __init__(self, parent: "Node" = None):
             self._parent = parent

         root = Node()
         node = Node(root)
