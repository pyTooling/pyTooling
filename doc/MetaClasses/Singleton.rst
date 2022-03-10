Singleton
#########

This class implements the `singleton design pattern <https://en.wikipedia.org/wiki/Singleton_pattern>`_
as a Python meta class.


Example Usage
*************

.. code-block:: Python

   class Terminal(metaclass=Singleton):
     def __init__(self):
       pass

     def WriteLine(self, message):
       print(message)
