Versioning
##########

The :py:mod:`pyTooling.Versioning` package provides auxiliary classes to implement
`semantic <https://semver.org/>`__ and `calendar <https://calver.org/>`__ versioning.

Semantic Version
****************

The :py:class:`~pyTooling.Versioning.SemVersion` class represents of a version number like ``v3.7.12``.

.. hint::

   Given a version number ``MAJOR.MINOR.PATCH``, increment the:

   * ``MAJOR`` version when you make incompatible API changes,
   * ``MINOR`` version when you add functionality in a backwards compatible manner, and
   * ``PATCH`` version when you make backwards compatible bug fixes.
   * Additional labels for pre-release and build metadata are available as extensions to the ``MAJOR.MINOR.PATCH``
     format.

   Summary taken from `semver.org <https://semver.org/>`__:

Calendar Version
****************

The :py:class:`~pyTooling.Versioning.CalVersion` class represents of a version number like ``2021.10``.
