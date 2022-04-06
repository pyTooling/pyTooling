.. _VER:

Versioning
##########

The :py:mod:`pyTooling.Versioning` package provides auxiliary classes to implement
`semantic <https://semver.org/>`__ and `calendar <https://calver.org/>`__ versioning.


.. _VER:SemVer:

Semantic Versioning
*******************

The :py:class:`~pyTooling.Versioning.SemVersion` class represents of a version number like ``v3.7.12``.

.. rubric:: Example

.. code:: python

   # Construct from string
   version1 = SemVersion("0.22.8")

   # Construct from numbers
   version2 = SemVersion(1, 3, 0)

   # Compare versions
   isNewer = version2 > version1


.. hint::

   Given a version number ``MAJOR.MINOR.PATCH``, increment the:

   * ``MAJOR`` version when you make incompatible API changes,
   * ``MINOR`` version when you add functionality in a backwards compatible manner, and
   * ``PATCH`` version when you make backwards compatible bug fixes.
   * Additional labels for pre-release and build metadata are available as extensions to the ``MAJOR.MINOR.PATCH``
     format.

   Summary taken from `semver.org <https://semver.org/>`__:



Features
========

* Major, minor, patch, build numbers
* Comparison operators
* Construct version number object from string or numbers.


Missing Features
----------------

* preserve prefix letter like ``v``, ``r``
* pre-version and post-version
* additional labels like ``dev``, ``rc``, ``pl``, ``alpha``





.. _VER:CalVer:

Calendar Versioning
*******************

The :py:class:`~pyTooling.Versioning.CalVersion` class represents of a version number like ``2021.10``.

.. rubric:: Example

.. code:: python

   # Construct from string
   version1 = CalVersion("2018.3")
