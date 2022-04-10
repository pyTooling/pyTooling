.. _META:

Overview
########

Currently, the following meta-classes are provided:

* :ref:`META/Overloading`
* :ref:`META/Singleton`



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
