Overloading
###########

This class provides a method dispatcher based on method signature's type
annotations.


Example Usage
*************

.. code-block:: Python

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
