Meta-Classes
############

.. todo:: Write this tutorial

A Python meta class is a class used to construct instances of other classes.
Python has one default meta class called :class:`type`. It's possible to
write new meta classes from scratch or to derive subclasses from :class:`type`.

Meta classes are used by passing a named parameter to a class definition in
addition to a list of classes for inheritance.

.. code-block:: Python

   class Foo(Bar, metaclass=type):
     pass


.. seealso::

   * https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/
   * https://www.pythontutorial.net/python-oop/python-__new__/
   * https://stackoverflow.com/questions/76468665/why-does-object-new-accept-parameters
