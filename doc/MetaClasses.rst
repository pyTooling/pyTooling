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


.. _META/ExpectedMembers:

Expected Members
****************

A class that is only complete once it is combined with another uses members it doesn't define itself. Nothing
states that contract, so the class that forgets one fails with an :exc:`AttributeError` on first access - somewhere
else entirely, and only if that code path ever runs.

:pycode:`expects` names those members, and it works in **both directions**:

.. list-table::
   :header-rows: 1
   :widths: 22 46 32

   * - Declared on
     - Meaning
     - Rejected
   * - a class (:pycode:`expects=(...)`)
     - *"whatever I am mixed into must provide these"* - the mixin-class case
     - instantiating the combined class
   * - a **method** (:deco:`expects`)
     - *"my class must provide these"* - including a method on the **primary inheritance line** waiting for a
       mixin-class to contribute them
     - calling that method

The second is the one a :term:`mixin-class` does *not* cover: a class on the primary inheritance line cannot
declare the members class-wide, because it has to stay usable without the mixin. See
:ref:`META/ExpectedMembers/Method`.

The class keyword argument names the members a class needs from whichever class it is mixed into.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class ReportMixin(metaclass=ExtendedType, mixin=True, expects=("_counter", "Write")):
     def Report(self) -> bool:
       return self.Write(f"{self._counter}")

   class Application(TerminalApplication, ReportMixin):
     pass

   Application()   # fine, if 'TerminalApplication' provides '_counter' and 'Write'

A member is provided when it is reachable on the class: a method, a property, a class variable, or a field, for
which :class:`~pyTooling.MetaClasses.ExtendedType` created a slot descriptor when the mixin joined the primary
inheritance line. So a field declared as an annotation counts, and both kinds of member are covered by one list.

When something is missing, instantiating the class raises an
:exc:`~pyTooling.MetaClasses.UnfulfilledExpectationError` naming every missing member and the class expecting it:

.. code-block:: text

   pyTooling.MetaClasses.UnfulfilledExpectationError: Class 'Application' doesn't provide every expected member.
   Missing 'Write', expected by 'ReportMixin'.
   A mixin-class names what it needs from its host class with the 'expects' class keyword argument.

Which members are missing is computed once, when the class is constructed, and kept in :pycode:`__missingMembers__`; the
exception is raised on instantiation. That is the same mechanism an :ref:`abstract class <META/AbstractClass>` uses,
and it has the same consequence: a class may stay incomplete as long as nothing instantiates it, so an intermediate
class can pass an expectation on to its own subclasses. A class that fulfills it again is instantiable, without the
intermediate class having to say anything.

:pycode:`expects` is not limited to mixin-classes - any class can state what its subclasses have to provide. A
mixin-class is the case it exists for, and a mixin-class is never itself incomplete, because it cannot provide what
it expects from its host.


.. _META/ExpectedMembers/Method:

A method expecting what a mixin-class contributes
=================================================

Sometimes only *one* method needs what a mixin-class contributes, while the class itself is perfectly usable
without it. **The marked method sits on the class in the primary inheritance line**, and it waits for a
mixin-class further along the bases to supply what it reads.

The class keyword argument would be too strict here: it would reject a class that never calls the method.

The decorator works from a mixin-class too, and pyTooling uses it that way:
:meth:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin._PrintHelp` has the parsers - they are the mixin's own
fields - but it *writes* through the ``Write***`` methods of
:class:`~pyTooling.TerminalUI.TerminalApplication`, so it expects those. Everything else the mixin does works
without a terminal. Which side declares the expectation is decided by which side owns the method, not by which
side is the mixin.

The :deco:`~pyTooling.MetaClasses.expects` decorator moves the expectation to where it belongs.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType, expects

   class Terminal(metaclass=ExtendedType, slots=True):
     @expects("MainParser", "SubParsers")
     def PrintHelp(self) -> None:
       self.MainParser.print_help()

   Terminal().PrintHelp()                  # UnfulfilledExpectationError

   class Application(Terminal, ArgParseHelperMixin):
     pass

   Application().PrintHelp()               # fine

The class stays usable - constructing it, instantiating it and calling every other method is unaffected. Only the
method that cannot work is replaced, by one raising an
:exc:`~pyTooling.MetaClasses.UnfulfilledExpectationError` that names the missing members:

.. code-block:: text

   UnfulfilledExpectationError: Method 'Terminal.PrintHelp()' expects members this class doesn't provide.
   Missing 'MainParser'.
   Missing 'SubParsers'.
   A method names what it needs from its class with the 'expects' decorator.

The check runs per class, so **a fulfilled expectation costs nothing**: the replacement is not installed at all and
the class holds the original function, with no per-call test. A replacement inherited from a base-class is removed
again as soon as a class provides the members, and a subclass that provides only some of them reports exactly the
ones still missing.

Because it is evaluated per class rather than once at the declaring class, **the mixin-class may arrive any number
of levels further down** - and a sibling that does not mix it in still reports the missing members:

.. code-block:: Python

   class Middle(Terminal):                       # still incomplete, still fine
     pass

   class Application(Middle, ArgParseHelperMixin):
     pass

   Application().PrintHelp()                     # fine
   Terminal().PrintHelp()                        # UnfulfilledExpectationError

A member counts whether it is a method, a property, a class variable, or a field the mixin-class declared as an
annotation - :class:`~pyTooling.MetaClasses.ExtendedType` materialises those as slots when the mixin joins the
primary inheritance line, which is what makes them visible to the check.

.. seealso::

   :ref:`@abstractmethod <META/AbstractMethod>`
      |rarr| Mark a *method* as abstract, when the class itself declares what has to be overridden.


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

The decorator sets :pycode:`__abstractClass__` on the class and recomputes :pycode:`__isAbstract__`, which is the same
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

A class defined with enabled :pycode:`slots` behavior stores instance fields in slots. The meta-class, translates all
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
