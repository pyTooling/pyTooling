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
