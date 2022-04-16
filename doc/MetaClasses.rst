.. _META:

Overview
########

Currently, the following meta-classes are provided:

* :ref:`META/Overloading`
* :ref:`META/Singleton`
* :ref:`META/SlottedType`


.. seealso::

   Understanding Python metaclasses
     https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/


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



.. _META/Singleton:

Singleton
#########

This class implements the `singleton design pattern <https://en.wikipedia.org/wiki/Singleton_pattern>`_
as a Python meta class.

.. admonition:: Example Usage

   .. code-block:: python

      class Terminal(metaclass=Singleton):
        def __init__(self):
          pass

        def WriteLine(self, message):
          print(message)



.. _META/SlottedType:

SlottedType
###########

All type-annotated fields in a class get stored in a slot rather than in ``__dict__``. This improves the memory
  footprint as well as the field access performance of all class instances. The behavior is automatically inherited to
  all derived classes.

.. admonition:: Example Usage

   .. code-block:: python

      class Node(metaclass=SlottedType):
        _parent: "Node"

        def __init__(self, parent: "Node" = None):
          self._parent = parent

      root = Node()
      node = Node(root)
