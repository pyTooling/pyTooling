.. _META:

Overview
########

Currently, the following meta-classes are provided:

* :ref:`ExtendedType <META/ExtendedType>` - slotted types, mixin-classes, singletons, abstract classes and expected
  members, in any combination.

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

Each feature is switched on by a class keyword argument:

.. list-table::
   :header-rows: 1
   :widths: 20 50 30

   * - Keyword
     - Effect
     - Section
   * - ``slots=True``
     - Store the annotated fields in ``__slots__`` instead of a ``__dict__``.
     - :ref:`META/Slotted`
   * - ``mixin=True``
     - Collect the annotated fields, and add them to the slots of the class the mixin-class is mixed into.
     - :ref:`META/Mixin`
   * - ``weakref=True``
     - Let instances of a slotted class be referenced weakly, by adding ``__weakref__`` to its slots.
     - :ref:`META/WeakReferences`
   * - ``singleton=True``
     - Create one instance, and return it on every further instantiation.
     - :ref:`META/Singleton`
   * - ``expects=(...)``
     - Name the members the class needs from the class it is mixed into.
     - :ref:`META/ExpectedMembers`

Abstract classes and methods need no keyword: a decorator marks them, and :class:`~pyTooling.MetaClasses.ExtendedType`
rejects instantiating the class - see :ref:`META/AbstractClass`, :ref:`META/AbstractMethod` and
:ref:`META/MustOverwrite`.

.. seealso::

   :doc:`Tutorials/MetaClasses`
      |rarr| What a meta-class is, what to try before writing one, and why slots need one.


.. _META/Slotted:

Slotted
*******

``slots=True`` stores an instance's fields in :term:`__slots__ <slots>` instead of a ``__dict__``. Every annotated
field of the class body becomes a slot. A class variable is annotated as :class:`~typing.ClassVar` and stays a class
variable.

.. rubric:: Example:
.. code-block:: Python

   from typing                import ClassVar
   from pyTooling.MetaClasses import ExtendedType

   class Node(metaclass=ExtendedType, slots=True):
     _SEPARATOR: ClassVar[str] = "/"   # class variable
     _parent:    "Node"                # slot
     _name:      str                   # slot

     def __init__(self, parent: "Node", name: str) -> None:
       self._parent = parent
       self._name =   name

   Node.__slots__                      # ('_parent', '_name')
   Node(None, "root")._nmae = "x"      # AttributeError: no __dict__ for setting new attributes

An instance has no ``__dict__``, so it needs less memory and reads its fields faster, and an assignment to a
misspelt field raises an :exc:`AttributeError` instead of creating a new field.

.. attention::

   A slot has no default value. An initial value in the class body (``_name: str = "root"``) is dropped, and reading
   the field before ``__init__`` assigned it raises an :exc:`AttributeError`. Assign every field in ``__init__``.

.. rubric:: Rules

* **Every base-class uses slots.** A base-class without ``__slots__`` would give each instance a ``__dict__`` anyway:
  :exc:`~pyTooling.MetaClasses.BaseClassWithoutSlotsError`.
* **Derived classes are slotted too.** A class derived from a slotted class lists only its own new fields in
  ``__slots__``; ``__allSlots__`` holds the fields of the whole hierarchy.
* **A field is declared once in a hierarchy.** Annotating a base-class' field again raises an
  :exc:`AttributeError`. Assigning it in the class body without an annotation would hide the slot, and raises a
  :exc:`~pyTooling.MetaClasses.DuplicateFieldInSlotsError`.
* **Only one base-class has non-empty slots.** That is Python's rule; every further base-class is a
  :ref:`mixin-class <META/Mixin>`.
* **Every field is annotated.** A field assigned in the class body without an annotation is neither a slot nor a
  declared class variable. It stays a class attribute, and :class:`~pyTooling.MetaClasses.ExtendedType` reports an
  :exc:`~pyTooling.MetaClasses.UnannotatedFieldWarning` to the nearest :class:`~pyTooling.Warning.WarningCollector`.

.. rubric:: Serialization

A slotted class gets ``__getstate__`` and ``__setstate__``, unless it defines them itself, so its instances work
with :mod:`pickle` and :mod:`copy`. The state is a dictionary of every slot in the hierarchy.

* Pickling an instance with an unassigned slot raises an :exc:`~pyTooling.MetaClasses.ExtendedTypeError` naming the
  field.
* Unpickling a state with a missing or an unexpected field raises an
  :exc:`~pyTooling.MetaClasses.ExtendedTypeError` naming them.


.. _META/SlottedObject:

SlottedObject
=============

Deriving from :class:`~pyTooling.MetaClasses.SlottedObject` makes a class slotted without naming the meta-class, and
the :deco:`~pyTooling.MetaClasses.slotted` decorator recreates a class as a slotted one. All three spellings declare
the same class:

.. list-table::
   :header-rows: 1
   :widths: 34 33 33

   * - Meta-class
     - ``SlottedObject``
     - ``@slotted``
   * - .. code-block:: Python

          class Node(metaclass=ExtendedType, slots=True):
            _name: str

     - .. code-block:: Python

          class Node(SlottedObject):
            _name: str

     - .. code-block:: Python

          @slotted
          class Node:
            _name: str


.. _META/Mixin:

Mixin
*****

Python allows non-empty ``__slots__`` on one inheritance line only. ``mixin=True`` declares a
:term:`mixin-class`: its annotated fields are collected in ``__mixinSlots__`` instead of becoming slots, and they
become slots of the slotted class the mixin-class is mixed into.

.. rubric:: Example:
.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class ParentMixin(metaclass=ExtendedType, mixin=True):
     _parent: "Node"

     def IsRoot(self) -> bool:
       return self._parent is None

   class Node(metaclass=ExtendedType, slots=True):
     _name: str

   class Child(Node, ParentMixin):
     pass

   ParentMixin.__slots__               # ()
   ParentMixin.__mixinSlots__          # ('_parent',)
   Child.__slots__                     # ('_parent',)
   Child.__allSlots__                  # {'_name', '_parent'}

.. rubric:: Rules

* **The primary base-class comes first.** The first base-class is the primary inheritance line and carries the
  slots; every further base-class is a mixin-class.
* **A further base-class with slots is rejected.** A slotted class that isn't a mixin-class raises a
  :exc:`~pyTooling.MetaClasses.BaseClassWithNonEmptySlotsError`; a class without ``__slots__`` at all raises a
  :exc:`~pyTooling.MetaClasses.BaseClassWithoutSlotsError`.
* **Mixin-classes combine.** A mixin-class derived from other mixin-classes collects their fields too, and a
  mixin-class may derive from a class of the primary inheritance line, e.g. to use its members.
* **A mixin-class is used mixed in.** An instance of the mixin-class itself has neither slots for its fields nor a
  ``__dict__``, so it can't hold them.
* **Without slots, fields stay attributes.** Mixed into a class that doesn't use slots, the mixin-class' fields are
  ordinary attributes in the instance's ``__dict__``.
* **The host class doesn't shadow a mixin field.** Assigning a member of that name in the class body raises a
  :exc:`~pyTooling.MetaClasses.DuplicateFieldInSlotsError`.

The :deco:`~pyTooling.MetaClasses.mixin` decorator recreates a class as a mixin-class. A mixin-class names the
members it needs from the class it is mixed into with :ref:`expects <META/ExpectedMembers>`.


.. _META/WeakReferences:

Weak References
***************

A class using :term:`__slots__ <slots>` cannot be referenced weakly. There is no ``__dict__`` for :mod:`weakref` to
put its bookkeeping in, and the slot that would hold it is not created unless it is asked for:

.. code-block:: Python

   class Slotted(metaclass=ExtendedType, slots=True):
     _field: int

   weakref.ref(Slotted())     # TypeError: cannot create weak reference to 'Slotted' object

``weakref=True`` adds ``__weakref__`` to the class' slots, which is what makes an instance weak-referenceable:

.. rubric:: Example:
.. code-block:: Python

   from weakref               import ref
   from pyTooling.MetaClasses import ExtendedType

   class Node(metaclass=ExtendedType, slots=True, weakref=True):
     _parent: "Node"

   node = Node()
   reference = ref(node)      # fine

   reference()                # -> the node
   del node
   reference()                # -> None

The typical reason to want it is a back-reference: a child pointing at its parent keeps the parent alive as long as
the child lives, and a weak reference is how that cycle is avoided.

.. important::

   ``__weakref__`` is a slot like any other, and like any other it may appear **once** in an inheritance
   hierarchy. A derived class inherits the capability; asking for it again declares a duplicate slot:

   .. code-block:: Python

      class Base(metaclass=ExtendedType, slots=True, weakref=True): ...
      class Derived(Base): ...                       # already weak-referenceable
      class Again(Base, weakref=True): ...           # AttributeError: slot '__weakref__' already exists

A mixin-class can ask for it too. ``__weakref__`` is then one of the slots it contributes, and it is added to the
class the mixin-class is mixed into. That class must not have it already - Python rejects the second one with
``TypeError: __weakref__ slot disallowed``:

.. code-block:: Python

   class ParentMixin(metaclass=ExtendedType, mixin=True, weakref=True):
     _parent: "Node"

   class Node(metaclass=ExtendedType, slots=True):
     _name: str

   class Child(Node, ParentMixin): ...               # weak-referenceable

.. attention::

   ``weakref=True`` is the only way to ask for it. Annotating ``__weakref__`` as a field raises an
   :exc:`~pyTooling.MetaClasses.ExtendedTypeError`, as does annotating ``__dict__``: a ``__dict__`` slot accepts any
   attribute on an instance again and gives up what slots save. A class that needs a ``__dict__`` uses
   ``slots=False``.

.. note::

   A class **without** slots is weak-referenceable already, because Python adds ``__weakref__`` itself.
   ``weakref=True`` is therefore only meaningful together with ``slots=True`` or ``mixin=True``.

.. note::

   The restriction is **CPython's**. On PyPy every object is weak-referenceable whether or not the class uses
   slots, so ``weakref=True`` adds the slot but changes nothing observable there. Code written for both keeps the
   keyword: it is what makes the class work on CPython.


.. _META/ExpectedMembers:

Expected Members
****************

A class that is only complete once it is combined with another uses members it doesn't define itself. Nothing
states that contract, so the class that forgets one fails with an :exc:`AttributeError` on first access - somewhere
else entirely, and only if that code path ever runs.

``expects`` names those members, and it works in **both directions**:

.. list-table::
   :header-rows: 1
   :widths: 22 46 32

   * - Declared on
     - Meaning
     - Rejected
   * - a class (``expects=(...)``)
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

Which members are missing is computed once, when the class is constructed, and kept in ``__missingMembers__``; the
exception is raised on instantiation. That is the same mechanism an :ref:`abstract class <META/AbstractClass>` uses,
and it has the same consequence: a class may stay incomplete as long as nothing instantiates it, so an intermediate
class can pass an expectation on to its own subclasses. A class that fulfills it again is instantiable, without the
intermediate class having to say anything.

``expects`` is not limited to mixin-classes - any class can state what its subclasses have to provide. A
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
