.. _Common:CallByRef:

CallByRef
#########

The ``pyTooling.CallByRef`` package contains auxilary classes to implement call by
reference emulation for function parameter handover. The callee get enabled to return
out-parameters for simple types like ``bool`` and ``int`` to the caller.

.. note::

   Python does not allow a user to distinguish between *call-by-value* and *call-by-reference*
   parameter passing. Python's standard types are passed by-value to a function or method.
   Instances of a class are passed by-reference (pointer) to a function or method.

By implementing a wrapper-class :class:`CallByRefParam`, any type's value can be passed
by-reference. In addition, standard types like :class:`int` or :class:`bool` can be handled
by derived wrapper-classes.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.CallByRef
   :parts: 1


CallByRefParam
**************

``CallByRefParam`` implements a wrapper class for an arbitrary *call-by-reference*
parameter that can be passed to a function or method.

The parameter can be initialized via the constructor. If no init-value was given,
the init value will be ``None``. The wrappers internal value can be updated by
using the inplace shift-left operator ``<=``.

In addition, operators ``=`` and ``!=`` are also implemented for any *call-by-reference*
wrapper. Calls to ``__repr__`` and ``__str__`` are passed to the internal value.

The internal value can be used via ``obj.value``.

.. autoclass:: pyTooling.CallByRef.CallByRefParam
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __eq__, __ne__, __repr__, __str__


Type-Specific *call-by-reference* Classes
*****************************************

CallByRefBoolParam
==================

This is an implementation for the boolean type (:class:`bool`).

.. autoclass:: pyTooling.CallByRef.CallByRefBoolParam
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __eq__, __ne__, __neg__, __and__, __or__, __iand__, __ior__, __bool__, __int__, __repr__, __str__



CallByRefIntParam
=================

This is an implementation for the integer type (:class:`int`).

.. autoclass:: pyTooling.CallByRef.CallByRefIntParam
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __neg__, __add__, __sub__, __truediv__, __mul__, __mod__, __pow__, __lt__, __le__, __gt__, __ge__, __bool__, __int__, __repr__, __str__
