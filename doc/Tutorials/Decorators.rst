Decorators
##########

.. contents:: Table of Contents
   :local:
   :depth: 2

Decorators can be applied to classes or functions/methods. A decorator is a callable, so a function or a class
implementing ``__call__``. Decorator can accept parameters, when a decorator factory returns a specific decorator.

The decorator syntax of Python is syntactic sugar for a function call.

See also :ref:`decorators offered by pyTooling <DECO>`.

.. hint::

   The predefined :func:`~functools.wraps` decorator should be used when creating wrapping or replacing decorators, so
   the name and doc-string of the callable is preserved and decorators can be chained.

+-------------------------------------+---------------------------------------------------+-----------------------------------------+
| Function-based without Parameter    | Function-based with Parameter(s)                  | Class-based with Parameter(s)           |
+=====================================+===================================================+=========================================+
| .. code-block:: Python              | .. code-block:: Python                            | .. code-block:: Python                  |
|                                     |                                                   |                                         |
|    from functools import wraps      |    from functools import wraps                    |    from functools import wraps          |
|                                     |                                                   |                                         |
|    F = TypeVar("F", Callable)       |    F = TypeVar("F", Callable)                     |    F = TypeVar("F", Callable)           |
|                                     |                                                   |                                         |
|    def decorator(func: F) -> F:     |    def decorator_factory(param: int) -> Callable: |    class decoratorclass:                |
|      @wraps(func)                   |      def specific_decorator(func: F) -> F:        |      _param: int                        |
|      def wrapper(*args, **kwargs):  |        @wraps(func)                               |                                         |
|        return func(*args, **kwargs) |        def wrapper(*args, **kwargs):              |      def __init__(self, param: int):    |
|                                     |          kwargs["param"] = param                  |        self._param = param              |
|      return wrapper                 |          return func(*args, **kwargs)             |                                         |
|                                     |                                                   |      def __call__(self, func: F) -> F:  |
|                                     |        return wrapper                             |        @wraps(func)                     |
|                                     |      return specific_Decorator                    |        def wrapper(*args, **kwargs):    |
|                                     |                                                   |          kwargs["param"] = self._param  |
|                                     |                                                   |          return func(*args, **kwargs)   |
|                                     |                                                   |                                         |
|   #                                 |    #                                              |        return wrapper                   |
|                                     |                                                   |                                         |
+-------------------------------------+---------------------------------------------------+-----------------------------------------+
| .. code-block:: Python              | .. code-block:: Python                            | .. code-block:: Python                  |
|                                     |                                                   |                                         |
|    @decorator                       |    @decorator_factory(10)                         |    @decoratorclass(10)                  |
|    def foo(param: int) -> bool:     |    def foo(param: int) -> bool:                   |    def foo(param: int) -> bool:         |
|      pass                           |      pass                                         |      pass                               |
+-------------------------------------+---------------------------------------------------+-----------------------------------------+
| .. code-block:: Python              | .. code-block:: Python                            | .. code-block:: Python                  |
|                                     |                                                   |                                         |
|    def foo(param: int) -> bool:     |    def foo(param: int) -> bool:                   |    def foo(param: int) -> bool:         |
|      pass                           |      pass                                         |      pass                               |
|                                     |                                                   |                                         |
|    foo = decorator(foo)             |    foo = decorator(10)(foo)                       |    foo = decoratorclass(10)(foo)        |
+-------------------------------------+---------------------------------------------------+-----------------------------------------+


Usecase
*******

Modifying Decorator
===================

A modifying decorator returns the original, but modified language item. Existing fields might be modified or new fields
might be added to the language item. It supports classes, functions and methods.

.. code-block:: Python

   F = TypeVar("F", Callable)

   def decorator(func: F) -> F:
     func.__field__ = ...

     return func

   @decorator
   def function(param: int) -> bool:
      pass

   class C:
     @decorator
     def method(self, param: int) -> bool:
       pass

.. seealso::

   The predefined :func:`~functools.wraps` decorator is a modifying decorator because it copies the ``__name__`` and
   ``__doc__`` fields from the original callable to the decorated callable.


Replacing Decorator
===================

A replacing decorator replaces the original language item by a new language item. The new item might have a similar or
completely different behavior as the original item. It supports classes, functions and methods.

.. code-block:: Python

   F = TypeVar("F", Callable)

   def decorator(func: F) -> F:
     def replacement(*args, **kwargs):
       pass

     return replacement

   @decorator
   def function(param: int) -> bool:
      pass

   class C:
     @decorator
     def method(self, param: int) -> bool:
       pass

.. seealso::

   The predefined :func:`property` decorator is a replacing decorator because it replaces the method with a descriptor
   implementing *getter* for a read-only property. It's a special cases, because it's also a wrapping decorator as the
   behavior of the original method is the behavior of the getter.

Wrapping Decorator
==================

.. todo:: TUTORIAL::Wrapping decorator

.. code-block:: Python

   F = TypeVar("F", Callable)

   def decorator(func: F) -> F:
     def wrapper(*args, **kwargs):
       # ...
       return func(*args, **kwargs)

     return replacement

   @decorator
   def function(param: int) -> bool:
      pass

   class C:
     @decorator
     def method(self, param: int) -> bool:
       pass



Parameters
**********

Function-based without Parameters
=================================

.. todo:: TUTORIAL::Function-based without parameters - write a tutorial

.. code-block:: Python

   F = TypeVar("F", Callable)

   def decorator(func: F) -> F:
     def wrapper(*args, **kwargs):
       # ...
       return func(*args, **kwargs)

     return replacement


Function-based with Parameters
==============================

.. todo:: TUTORIAL::Function-based with parameters - write a tutorial

.. code-block:: Python

   F = TypeVar("F", Callable)

   def decorator_factory(param: int) -> Callable:
     def decorator(func: F) -> F:
       def wrapper(*args, **kwargs):
         # ...
         return func(*args, **kwargs)

       return replacement

     return decorator

Class-based with Parameters
===========================

A decorator accepting parameters can also be implemented with a class providing ``__call__``, so it's a callable.

.. todo:: TUTORIAL::Class-based - write a tutorial

.. code-block:: Python

   from functools import wraps

   F = TypeVar("F", Callable)

   class decoratorclass:
     _param: int

     def __init__(self, param: int):
       self._param = param

     def __call__(self, func: F) -> F:
       @wraps(func)
       def wrapper(*args, **kwargs):
         kwargs["param"] = self._param
         return func(*args, **kwargs)

       return wrapper
