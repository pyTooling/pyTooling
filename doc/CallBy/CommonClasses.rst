CallByRefParam
##############

``CallByRefParam`` implements a wrapper class for an arbitrary *call-by-reference*
parameter that can be passed to a function or method.

The parameter can be initialized via the constructor. If no init-value was given,
the init value will be ``None``. The wrappers internal value can be updated by
using the inplace shift-left operator ``<=``.

In addition, operators ``=`` and ``!=`` are also implemented for any *call-by-reference*
wrapper. Calls to ``__repr__`` and ``__str__`` are passed to the internal value.

The internal value can be used via ``obj.value``.

.. autoclass:: pyCallBy.CallByRefParam
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __eq__, __ne__, __repr__, __str__
