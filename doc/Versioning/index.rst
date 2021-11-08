Versioning
##########

The ``pyTooling.Versioning`` package provides auxiliary classes to implement
`semantic <https://semver.org/>`__ and `calendar <https://calver.org/>`__ versioning.

SemVersion
**********

The :class:`SemVersion` class represents of a version number like ``v3.7.12``.

.. autoclass:: pyTooling.Versioning.SemVersion
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __eq__, __ne__, __lt__, __le__, __gt__, __ge__, __repr__, __str__

CalVersion
**********

The :class:`CalVersion` class represents of a version number like ``2021.10``.

.. autoclass:: pyTooling.Versioning.CalVersion
   :show-inheritance:
   :members:
   :private-members:
   :special-members: __init__, __ilshift__, __eq__, __ne__, __lt__, __le__, __gt__, __ge__, __repr__, __str__
