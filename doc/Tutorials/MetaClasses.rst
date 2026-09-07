.. _TUTORIAL/MetaClasses:

Meta-Classes
############

A meta-class is a class whose instances are **classes**. Python has one by default, :class:`type`, and every class
statement is a call to it - so a meta-class is the hook for changing what a ``class`` statement produces.

That is a powerful place to stand, and an easy one to over-use. This page explains what Python actually does when
it creates a class, which four lighter tools exist before a meta-class is warranted, and what
:class:`~pyTooling.MetaClasses.ExtendedType` does with the hook once it is warranted.

.. seealso::

   :ref:`META`
      |rarr| The reference for :mod:`pyTooling.MetaClasses` and every option of ``ExtendedType``.


.. _TUTORIAL/MetaClasses/What:

What a ``class`` statement really is
************************************

A class statement is syntactic sugar for a call. These two are the same thing:

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         class Point:
           x: int
           y: int

           def Length(self) -> float:
             ...

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         Point = type(
           "Point",                    # __name__
           (),                         # __bases__
           {                           # the class body,
             "__annotations__": ...,   # already executed
             "Length": ...,
           }
         )

So a class is an **object**, and :class:`type` is the class it is an instance of. ``metaclass=`` replaces which
class that is:

.. code-block:: Python

   class Point(metaclass=MyMeta):
     ...

   # Point = MyMeta("Point", (), {...})
   # type(Point) is MyMeta

.. rubric:: The order of events

Knowing the order is what makes the tools below distinguishable - each hooks a different moment:

#. The class **body is executed** as ordinary code, in its own namespace. Assignments and ``def``\ s become entries
   in a dictionary.
#. The meta-class' :meth:`~object.__new__` receives the name, the bases and that dictionary, and **creates** the
   class object. This is the only moment at which ``__slots__`` can still be set.
#. The meta-class' :meth:`~object.__init__` **initializes** the class object, which already exists.
#. :meth:`~object.__set_name__` is called on every descriptor in the body, told the class and its own attribute
   name.
#. :meth:`~object.__init_subclass__` of the nearest **base-class** is called, told the new subclass.

Steps 4 and 5 are the ones that don't need a meta-class at all.


.. _TUTORIAL/MetaClasses/Alternatives:

Four things to try before a meta-class
**************************************

A meta-class is contagious: every subclass inherits it, and combining two classes with different meta-classes is a
:exc:`TypeError` the user cannot fix. So try these first.

.. list-table::
   :header-rows: 1
   :widths: 26 74

   * - Tool
     - Use when
   * - a **class decorator**
     - the class only needs to be *modified or registered* after it exists. It is not inherited, so a subclass
       decides for itself - which is usually what you want. :deco:`~pyTooling.MetaClasses.slotted`,
       :deco:`~pyTooling.MetaClasses.mixin` and :deco:`~pyTooling.MetaClasses.singleton` are exactly this.
   * - :meth:`~object.__init_subclass__`
     - a **base-class** wants to react to being subclassed - registering the subclass, validating that it defined
       something, giving it its own copy of a class variable. :class:`~pyTooling.Attributes.Attribute` uses it to
       give every derived attribute its own registry.
   * - :meth:`~object.__set_name__`
     - a *descriptor* needs to know the name it was assigned to. This is how a field object learns it is called
       ``x`` without the class repeating the name.
   * - :func:`~typing.dataclass_transform` / :mod:`dataclasses`
     - the goal is only to generate ``__init__``, ``__eq__`` and friends from annotations.
   * - **a meta-class**
     - the class object itself must be *different* - a different ``__slots__``, a different construction protocol,
       a check that has to happen before the class exists. Everything above happens too late for that.

.. hint::

   The deciding question is *"does this have to happen **before** the class object exists?"* ``__slots__`` does -
   Python reads it while allocating the type. Registration does not.


.. _TUTORIAL/MetaClasses/Writing:

Writing one
***********

A meta-class derives from :class:`type` and overrides :meth:`~object.__new__`, :meth:`~object.__init__`, or both.
``__new__`` is where the class is shaped, because it can still change what is passed to :class:`type`:

.. code-block:: Python

   class RegisteringMeta(type):
     _registry: dict[str, type] = {}

     def __new__(cls, name: str, bases: tuple[type, ...], namespace: dict, **kwargs) -> type:
       # the class object doesn't exist yet - the namespace can still be changed
       namespace["__registered__"] = True

       newClass = super().__new__(cls, name, bases, namespace, **kwargs)
       cls._registry[name] = newClass

       return newClass

Two mechanics are worth knowing before writing one for real:

.. rubric:: Keyword arguments in the class statement reach the meta-class

``class Point(metaclass=RegisteringMeta, category="geometry")`` passes :pycode:`category="geometry"` to ``__new__`` and
``__init__``. That is how :class:`~pyTooling.MetaClasses.ExtendedType` receives :pycode:`slots=True`,
:pycode:`mixin=True` and :pycode:`singleton=True`.

.. rubric:: A method defined on the meta-class is a method of the *class*, not of its instances

``RegisteringMeta.Registry`` is callable as :pycode:`Point.Registry()`, not as :pycode:`point.Registry()` - the
same relation as an instance method to an object. This is how a "class property" is built, and why
:class:`~pyTooling.MetaClasses.ExtendedType` can add
:meth:`~pyTooling.MetaClasses.ExtendedType.GetMethodsWithAttributes` to every class it creates.

.. attention::

   **Meta-class conflicts are the reason to keep this rare.** A class can have only one meta-class, so deriving
   from two classes with unrelated meta-classes raises

   ::

      TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the
      metaclasses of all its bases

   at class-creation time. That is Python's own check, and the user of your class cannot work around it.

   pyTooling raises :exc:`~pyTooling.MetaClasses.IncompatibleMetaClassError` for the neighbouring case: one of its
   class decorators - :deco:`~pyTooling.MetaClasses.slotted`, :deco:`~pyTooling.MetaClasses.mixin`,
   :deco:`~pyTooling.MetaClasses.singleton` - applied to a class whose meta-class is neither :class:`type` nor
   derived from :class:`~pyTooling.MetaClasses.ExtendedType`.


.. _TUTORIAL/MetaClasses/ExtendedType:

What ``ExtendedType`` adds
**************************

:class:`~pyTooling.MetaClasses.ExtendedType` is a meta-class because every one of its features has to happen at
class-creation time. Each is switched on by a keyword in the class statement:

.. list-table::
   :header-rows: 1
   :widths: 22 78

   * - Option
     - Effect
   * - :pycode:`slots=True`
     - Derive ``__slots__`` from the class' **annotated fields**, so instances have no ``__dict__``: less memory,
       faster attribute access, and a typo in an assignment raises :exc:`AttributeError` instead of silently
       creating a field. See :ref:`META/Slotted`.
   * - :pycode:`mixin=True`
     - Mark the class as a **mixin**: its fields are collected rather than materialized, and merged when it is
       combined with a primary base-class. This is what makes slots usable with multiple inheritance at all -
       Python forbids two bases with non-empty slots. See :ref:`META/Mixin`.
   * - :pycode:`singleton=True`
     - Construct **one** instance and return it for every further construction. See :ref:`META/Singleton`.
   * - :pycode:`expects=...`
     - Declare the members a mixin needs its host class to provide, and fail at class creation rather than at the
       first call. See :ref:`META/ExpectedMembers`.

and three decorators for methods:
:deco:`~pyTooling.MetaClasses.abstractmethod`, :deco:`~pyTooling.MetaClasses.mustoverride` and
:deco:`~pyTooling.MetaClasses.abstractclass`, which make instantiating an incomplete class an error with a message
naming the method that is missing.

.. code-block:: Python

   from pyTooling.MetaClasses import ExtendedType

   class Point(metaclass=ExtendedType, slots=True):
     _x: int    #: The x coordinate.
     _y: int    #: The y coordinate.

     def __init__(self, x: int, y: int) -> None:
       self._x = x
       self._y = y

   point = Point(1, 2)
   point._z = 3
   # AttributeError: 'Point' object has no attribute '_z' and no __dict__ for setting new attributes

.. hint::

   :class:`~pyTooling.MetaClasses.SlottedObject` is :pycode:`metaclass=ExtendedType, slots=True` under a name, for the
   common case: ``class Point(SlottedObject):`` says the same thing and reads better.

   Where the class already has to name a different base, the decorator form
   :deco:`~pyTooling.MetaClasses.slotted` does the same without a ``metaclass=`` in the class statement.


.. _TUTORIAL/MetaClasses/Slots:

Why slots need a meta-class
***************************

This is the example that shows why the lighter tools don't suffice. ``__slots__`` is read by :class:`type` **while
the class object is being allocated**, so anything that runs later - a decorator, ``__init_subclass__`` - is too
late to add it. A class decorator can only *recreate* the class, which is precisely what
:deco:`~pyTooling.MetaClasses.slotted` does, and why the recreated class is a different object than the one the
decorator received.

Writing ``__slots__`` by hand is also the kind of duplication that rots: the names appear once in the annotations
and again in the tuple, and the two drift. ``ExtendedType`` reads the annotations and derives the tuple, so there is
one list of fields, and it is the one the type checker already reads.

.. code-block:: Python

   # by hand - two lists to keep in step
   class Point:
     __slots__ = ("_x", "_y")
     _x: int
     _y: int

   # with ExtendedType - one list
   class Point(SlottedObject):
     _x: int
     _y: int

.. seealso::

   :ref:`META/ExtendedType`
      |rarr| Every option, with the exceptions each of them can raise.
   :ref:`DECO`
      |rarr| The decorators pyTooling offers, including the class-decorator form of these options.
