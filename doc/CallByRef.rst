.. _Common/CallByRef:

CallByRef
#########

The :py:mod:`pyTooling.CallByRef` package contains auxiliary classes to implement call by reference emulation for
function parameter handover. The callee gets enabled to return out-parameters for simple types like :py:class:`bool` and
:py:class:`int` to the caller.

.. admonition:: Python Background

   Python does not allow a user to distinguish between *call-by-value* and *call-by-reference*
   parameter passing. Python's standard types are passed by-value to a function or method.
   Instances of a class are passed by-reference (pointer) to a function or method.

By implementing a wrapper-class :py:class:`~pyTooling.CallByRef.CallByRefParam`, any type's value can be passed
by-reference. In addition, standard types like :py:class:`int` or :py:class:`bool` can be handled
by derived wrapper-classes.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.CallByRef
   :parts: 1

.. admonition:: Example

   .. code-block:: Python

      from pyTooling.CallByRef import CallByRefIntParam

      # define a call-by-reference parameter for integer values
      myInt = CallByRefIntParam(3)

      # a function using a call-by-reference parameter
      def func(param : CallByRefIntParam):
        param <<= param * 4

      # call the function and pass the wrapper object
      func(myInt)

      print(myInt.value)


CallByRefParam
**************

:py:class:`~pyTooling.CallByRef.CallByRefParam` implements a wrapper class for an arbitrary *call-by-reference*
parameter that can be passed to a function or method.

The parameter can be initialized via the constructor. If no init-value was given,
the init value will be ``None``. The wrappers internal value can be updated by
using the inplace shift-left operator ``<=``.

In addition, operators ``=`` and ``!=`` are also implemented for any *call-by-reference*
wrapper. Calls to ``__repr__`` and ``__str__`` are passed to the internal value.

The internal value can be used via ``obj.value``.


Type-Specific *call-by-reference* Classes
*****************************************

CallByRefBoolParam
==================

This is an implementation for the boolean type (:class:`bool`).


CallByRefIntParam
=================

This is an implementation for the integer type (:class:`int`).
