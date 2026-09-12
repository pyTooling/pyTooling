.. _VERSIONING:

Versioning
##########

The :mod:`pyTooling.Versioning` package provides auxiliary classes to implement :ref:`VERSIONING/SemanticVersion`
(following `SemVer <https://semver.org/>`__ rules) and :ref:`VERSIONING/CalendarVersion` (following
`CalVer <https://calver.org/>`__ rules). The latter one has multiple variants due to the meaning of the version's parts
like: year-month version or year-week version.

Versions can be grouped by :ref:`version sets <VERSIONING/VersionSet>` and :ref:`version ranges <VERSIONING/VersionRange>`.


.. _VERSIONING/SemanticVersion:

Semantic Versioning
*******************

The :class:`~pyTooling.Versioning.SemanticVersion` class represents of a version number like ``v3.7.12``. It consists of
a major, minor and micro number. The micro number is also known as patch number. The minor and micro numbers are
optional, but usually used by most semantic version numbering schemes. In addition, optional parts can be added like a
prefix, a postfix or a build number.

.. hint::

   Given a version number ``MAJOR.MINOR.MICRO``, increment the:

   * ``MAJOR`` version when you make incompatible API changes,
   * ``MINOR`` version when you add functionality in a backwards compatible manner, and
   * ``MICRO`` version when you make backwards compatible bug fixes.
   * Additional labels for pre-release and build metadata are available as extensions to the ``MAJOR.MINOR.MICRO``
     format.

   Summary taken from `semver.org <https://semver.org/>`__.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. rubric:: Direct Instantiation

      A semantic version can be constructed from parts like major, minor and micro numbers.

      .. code-block:: python

         # Construct from numbers
         version = SemanticVersion(1, 5, 2)

      .. rubric:: Construction from String

      Alternatively, a semantic version can be created from a string containing a semantic version number by using the
      class-method :meth:`~pyTooling.Versioning.SemanticVersion.Parse`. The string is parsed and a semantic version gets
      returned.

      .. code-block:: python

         # Construct from string
         version = SemanticVersion.Parse("0.22.8")

      .. rubric:: Usage

      .. code-block:: python

         # Compare versions
         if version2 > version1:

         # Compare versions
         if version2 >= "1.4.8":

      .. rubric:: Features

      Prefix string
        Represents the prefix like: ``v`` (version), ``r`` (revision), ``i`` (internal version/release), ``ver``
        (version), ``rev`` (revision).

        :green:`v`\ 1.2.3

      Major number
        Represents the major version number in semantic version.

        v\ :green:`1`\ .2.3

      Minor number
        Represents the minor version number in semantic version.

        v1.\ :green:`2`\ .3

      Micro number
        Represents the micro or patch version number in semantic version.

        v1.2.\ :green:`3`

      Build number
        Represents the build number.

        v1.2.3.\ :green:`4`

      Release Level / Release number
        Distinguishes if a version is in *alpha*, *beta*, *release candidate* or *final* release level.

        v1.2.3.\ :green:`alpha4` |br|
        v1.2.3.\ :green:`beta4` |br|
        v1.2.3.\ :green:`rc4`

      Post number
        tbd

        v1.2.3.\ :green:`post4`

      Development number
        tbd

        v1.2.3.\ :green:`dev4`

      Postfix string
        v1.2.3+\ :green:`deb11u5`

      Comparison operators
        Operators for ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``, ``>>``.

      String formatting
        The version number can be formatted as a string with a fixed formatting pattern based on present version parts
        as well as a user-defined formatting via :meth:`~pyTooling.Versioning.SemanticVersion.__format__`

      .. rubric:: Examples

      .. hlist::
         :columns: 3

         * ``v1``
         * ``r1.12``
         * ``i1.2.13+linux_86_64``
         * ``rev1.2.3.14``
         * ``v1.2.3-dev``
         * ``v1.2.3.dev23``
         * ``v1.2.3.alpha1``
         * ``v1.2.3.beta1``
         * ``v1.2.3.rc1+deb25``
         * ``1.2.8.post2``
         * ``1.2.8.post2.dev4``
         * ``v1.2.3.alpha4.post5.dev6+deb11u35``

   .. grid-item::
      :columns: 6

      .. rubric:: Condensed Class Definition

      .. code-block:: Python

         @export
         class SemanticVersion(Version):

           @classmethod
           def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["SemanticVersion"], bool]] = None) -> "Version":
             pass

           @readonly
           def Parts(self) -> Parts:
             pass

           @readonly
           def Prefix(self) -> str:
             pass

           @readonly
           def Major(self) -> int:
             pass

           @readonly
           def Minor(self) -> int:
             pass

           @readonly
           def Micro(self) -> int:
             pass

           @readonly
           def Patch(self) -> int:
             pass

           @readonly
           def ReleaseLevel(self) -> ReleaseLevel:
             pass

           @readonly
           def ReleaseNumber(self) -> int:
             pass

           @readonly
           def Post(self) -> int:
             pass

           @readonly
           def Dev(self) -> int:
             pass

           @readonly
           def Build(self) -> int:
             pass

           @readonly
           def Postfix(self) -> str:
             pass

           @readonly
           def Hash(self) -> str:
             pass

           @readonly
           def Flags(self) -> Flags:
             pass

           def __eq__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __ne__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __lt__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __le__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __gt__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __ge__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __imod__(self, other: Union["SemanticVersion", str, int, None]) -> bool:
             pass

           def __format__(self, formatSpec: str) -> str:
             pass

           def __repr__(self) -> str:
             pass

           def __str__(self) -> str:
             pass

.. _VERSIONING/SemVerVariants:
Variants
========

.. tab-set::

   .. tab-item:: Python Version

      .. grid:: 2

         .. grid-item::
            :columns: 6

            .. rubric:: Examples

            * 3.13.0
            * 3.13.0a4
            * 3.13.0b2
            * 3.13.0rc2

         .. grid-item::
            :columns: 6

            .. rubric:: Condensed Class Definition

            .. code-block:: Python

               @export
               class PythonVersion(SemanticVersion):
                 @classmethod
                 def FromSysVersionInfo(cls) -> "PythonVersion":
                   pass


.. _VERSIONING/CalendarVersion:

Calendar Versioning
*******************

The :class:`~pyTooling.Versioning.CalendarVersion` class represents of a version number like ``2021.10``.

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. rubric:: Direct Instantiation

      Alternatively, a calendar version can be constructed from parts like major, minor and micro numbers. The
      unified naming of parts can be used to map years to major numbers, months to minor numbers, etc.

      .. code-block:: python

         # Construct from numbers
         version = CalendarVersion(2024, 5)

      .. rubric:: Construction from String

      A calendar version can be created from a string containing a calendar version number by using the class-method
      :meth:`~pyTooling.Versioning.CalendarVersion.Parse`. The string is parsed and a calendar version gets returned.

      .. code-block:: python

         # Construct from string
         version = CalendarVersion.Parse("2024.05")

      .. rubric:: Usage

      .. code-block:: python

         # Compare versions
         if version2 > version1:

         # Compare versions
         if version2 >= "2023.02":

      .. rubric:: Features

      Major number
        Represents the major version number in semantic version.

      Minor number
        Represents the minor version number in semantic version.

      Micro number
        Represents the micro or patch version number in semantic version.

      Build number
        Represents the build number.

      Prefix string
        Represents the prefix like: ``v`` (version), ``r`` (revision), ``i`` (internal version/release), ``ver``
        (version), ``rev`` (revision).

      Comparison operators
        Operators for ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``, ``>>``.

      .. rubric:: Missing Features

      * release-level: additional labels like ``dev``, ``rc``, ``pl``, ``alpha``
      * pre-version and post-version

   .. grid-item::
      :columns: 6

      .. rubric:: Condensed Class Definition

      .. code-block:: Python

         @export
         class CalendarVersion(Version):
           @classmethod
           def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["CalendarVersion"], bool]] = None) -> "CalendarVersion":
             pass

           @readonly
           def Parts(self) -> Parts:
             pass

           @readonly
           def Major(self) -> int:
             pass

           @readonly
           def Minor(self) -> int:
             pass

           @readonly
           def Micro(self) -> int:
             pass

           @readonly
           def Patch(self) -> int:
             pass

           @readonly
           def Build(self) -> int:
             pass

           @readonly
           def Flags(self) -> Flags:
             pass

           @readonly
           def Prefix(self) -> str:
             pass

           @readonly
           def Postfix(self) -> str:
             pass

           def __eq__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __ne__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __lt__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __le__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __gt__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __ge__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __imod__(self, other: Union["CalendarVersion", str, int, None]) -> bool:
             pass

           def __format__(self, formatSpec: str) -> str:
             pass

           def __repr__(self) -> str:
             pass

           def __str__(self) -> str:
             pass


.. _VERSIONING/CalVerVariants:

Variants
========

.. hint::

   Calendar versions have multiple format variants:

   * ``YY.MINOR.MICRO``
   * ``YYYY.MINOR.MICRO``
   * ``YY.MM``
   * ``YYYY.0M``
   * ``YYYY.MM.DD``
   * ``YYYY.MM.DD_MICRO``
   * ``YYYY-MM-DD``

   Formats taken from `calver.org <https://calver.org/>`__.

.. tab-set::

   .. tab-item:: Year-Month Version

      .. grid:: 2

         .. grid-item::
            :columns: 6

            .. rubric:: Direct Instantiation

            A year-month version can be constructed from year and month numbers.

            .. code-block:: python

               # Construct from numbers
               version = YearMonthVersion(2024, 5)

            .. rubric:: Construction from String

            A semantic version can also be created from a string containing a year-month version number by using the
            class-method :meth:`~pyTooling.Versioning.YearMonthVersion.Parse`. The string is parsed and a year-month
            version gets returned.

            .. code-block:: python

               # Construct from string
               version = YearMonthVersion.Parse("2024.05")

            .. rubric:: Examples

            * OSVVM: 2024.07
            * Ubuntu: 2024.10

         .. grid-item::
            :columns: 6

            .. rubric:: Condensed Class Definition

            .. code-block:: Python

               @export
               class YearMonthVersion(CalendarVersion):
                 @classmethod
                 def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["YearMonthVersion"], bool]] = None) -> "YearMonthVersion":
                   pass

                 @readonly
                 def Year(self) -> int:
                   pass

                 @readonly
                 def Month(self) -> int:
                   pass


   .. tab-item:: Year-Week Version

      .. grid:: 2

         .. grid-item::
            :columns: 6

            .. rubric:: Direct Instantiation

            A year-week version can be constructed from year and month numbers.

            .. code-block:: python

               # Construct from numbers
               version = YearWeekVersion(2024, 5)

            .. rubric:: Construction from String

            A semantic version can also be created from a string containing a year-week version number by using the
            class-method :meth:`~pyTooling.Versioning.YearWeekVersion.Parse`. The string is parsed and a year-week
            version gets returned.

            .. code-block:: python

               # Construct from string
               version = YearWeekVersion.Parse("2024.05")

            .. rubric:: Examples

            * Production date codes

         .. grid-item::
            :columns: 6

            .. rubric:: Condensed Class Definition

            .. code-block:: Python

               @export
               class YearWeekVersion(CalendarVersion):
                 @classmethod
                 def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["YearWeekVersion"], bool]] = None) -> "YearWeekVersion":
                   pass

                 @readonly
                 def Year(self) -> int:
                   pass

                 @readonly
                 def Week(self) -> int:
                   pass


   .. tab-item:: Year-Release Version

      .. grid:: 2

         .. grid-item::
            :columns: 6

            .. rubric:: Direct Instantiation

            A year-release version can be constructed from year and month numbers.

            .. code-block:: python

               # Construct from numbers
               version = YearReleaseVersion(2024, 2)

            .. rubric:: Construction from String

            A semantic version can also be created from a string containing a year-release version number by using the
            class-method :meth:`~pyTooling.Versioning.YearReleaseVersion.Parse`. The string is parsed and a year-release
            version gets returned.

            .. code-block:: python

               # Construct from string
               version = YearReleaseVersion.Parse("2024.2")

            .. rubric:: Examples

            * Vivado: 2024.1

         .. grid-item::
            :columns: 6

            .. rubric:: Condensed Class Definition

            .. code-block:: Python

               @export
               class YearReleaseVersion(CalendarVersion):
                 @classmethod
                 def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["YearReleaseVersion"], bool]] = None) -> "YearReleaseVersion":
                   pass

                 @readonly
                 def Year(self) -> int:
                   pass

                 @readonly
                 def Release(self) -> int:
                   pass


   .. tab-item:: Year-Month-Day Version

      .. grid:: 2

         .. grid-item::
            :columns: 6

            .. rubric:: Direct Instantiation

            A year-month-day version can be constructed from year, month and day numbers.

            .. code-block:: python

               # Construct from numbers
               version = YearMonthDayVersion(2024, 10, 5)

            .. rubric:: Construction from String

            A semantic version can also be created from a string containing a year-month-day version number by using the
            class-method :meth:`~pyTooling.Versioning.YearMonthDayVersion.Parse`. The string is parsed and a
            year-month-day version gets returned.

            .. code-block:: python

               # Construct from string
               version = YearMonthDayVersion.Parse("2024.10.05")

            .. rubric:: Examples

            * Furo: 2024.04.27

         .. grid-item::
            :columns: 6

            .. rubric:: Condensed Class Definition

            .. code-block:: Python

               @export
               class YearMonthDayVersion(CalendarVersion):
                 @classmethod
                 def Parse(cls, versionString: Nullable[str], validator: Nullable[Callable[["YearMonthDayVersion"], bool]] = None) -> "YearMonthDayVersion":
                   pass

                 @readonly
                 def Year(self) -> int:
                   pass

                 @readonly
                 def Month(self) -> int:
                   pass

                 @readonly
                 def Day(self) -> int:
                   pass

.. _VERSIONING/VersionRange:

VersionRange
************

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyTooling.Versioning.VersionRange` defines a range of versions reaching from a lower to an upper bound.
      It equivalently supports :ref:`semantic <VERSIONING/SemanticVersion>` and :ref:`calendar <VERSIONING/CalendarVersion>`
      versions or derived subclasses thereof. When initializing a version range, an optional
      :class:`~pyTooling.Versioning.RangeBoundHandling` flag specifies if the bounds are inclusive (default) or
      exclusive.

      .. rubric:: Features

      Access bounds and bound handling behavior
        The lower bound of the version range can be read or updated by accessing the
        :attr:`~pyTooling.Versioning.VersionRange.LowerBound` property. Similarly, the upper bound of the version range
        can be read or updated by accessing the :attr:`~pyTooling.Versioning.VersionRange.UpperBound` property.

        The behavior how lower and upper bound are handled can be read or modified by accessing the
        :attr:`~pyTooling.Versioning.VersionRange.BoundHandling` property.

      Comparison of two version ranges
        A version range can be compare to another version range using comparison operators: ``<``, ``<=``, ``>``, ``>=``.

      Comparison of a version range and a version
        A version can be compared with a version range and vise versa using comparison operators: ``<``, ``<=``, ``>``,
        ``>=``.

        The behavior is influenced by the bound handling behavior.

      Contains checks
        A version can be checked if it's contained in a version range using *contains* operators: ``in``, ``not in``.

        The behavior is influenced by the bound handling behavior.

      Intersection
        Two version ranges can be intersected using the ``&`` operator creating a new version range.

        In case of an empty intersection result, an exception is raised.

   .. grid-item::
      :columns: 6

      .. rubric:: Condensed Class Definition

      .. code-block:: python

         @export
         class VersionRange(Generic[V], metaclass=ExtendedType, slots=True):
            def __init__(self, lowerBound: V, upperBound: V, boundHandling: RangeBoundHandling = RangeBoundHandling.BothBoundsInclusive) -> None:

            @property
            def LowerBound(self) -> V:
              pass

            @property
            def UpperBound(self) -> V:
              pass

            @property
            def BoundHandling(self) -> RangeBoundHandling:
              pass

            def __and__(self, other: Any) -> VersionRange[T]:
              pass

            def __lt__(self, other: Any) -> bool:
              pass

            def __le__(self, other: Any) -> bool:
              pass

            def __gt__(self, other: Any) -> bool:
              pass

            def __ge__(self, other: Any) -> bool:
              pass

            def __contains__(self, version: Version) -> bool:
              pass

      .. tab-set::

         .. tab-item:: Instantiation (Inclusive Bounds)

            .. code-block:: python

               from pyTooling.Versioning import SemanticVersion, VersionRange

               versionRange = VersionRange(
                 lowerBound=SemanticVersion(1, 0, 0),
                 upperBound=SemanticVersion(1, 9, 0)
               )

               testVersion = SemanticVersion(1, 4, 3)
               if testVersion in versionRange:
                 pass

         .. tab-item:: Instantiation (Exclusive Upper Bound)

            .. code-block:: python

               from pyTooling.Versioning import SemanticVersion, VersionRange

               versionRange = VersionRange(
                 lowerBound=YearWeekVersion(2023, 34),
                 upperBound=YearWeekVersion(2023, 51),
                 boundHandling=RangeBoundHandling.UpperBoundExclusive)
               )

               testVersion = YearWeekVersion(2023, 51)
               if testVersion not in versionRange:
                 pass


.. _VERSIONING/VersionSet:

VersionSet
**********

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyTooling.Versioning.VersionSet` defines an ordered set (actually a list) of versions. It equivalently
      supports :ref:`semantic <VERSIONING/SemanticVersion>` and :ref:`calendar <VERSIONING/CalendarVersion>` versions or
      derived subclasses thereof.

      .. rubric:: Features

      Accessing versions in the set
        The versions within a version set can be accessed via index operation (``__getitem__``) or iterating
        (``__iter__``) the version set.

        The number of elements is accessible via length operation (``__len__``).

      Comparison of two version sets
        A version set can be compare to another version set using comparison operators: ``<``, ``<=``, ``>``, ``>=``.

      Comparison of a version set and a version
        A version can be compared with a version set and vise versa using comparison operators: ``<``, ``<=``, ``>``,
        ``>=``.

      Contains checks
        A version can be checked if it's contained in a version set using *contains* operators: ``in``, ``not in``.

      Intersection
        Two version set can be intersected using the ``&`` operator creating a new version set.

        In case of an empty intersection result, an exception is raised.

      Union
        Two version sets can be united using the ``|`` operator creating a new version set.


   .. grid-item::
      :columns: 6

      .. rubric:: Condensed Class Definition

      .. code-block:: python

         @export
         class VersionSet(Generic[V], metaclass=ExtendedType, slots=True):
            def __init__(self, versions: Union[Version, Iterable[V]]):
              pass

            def __and__(self, other: VersionSet[V]) -> VersionSet[T]:
              pass

            def __or__(self, other: VersionSet[V]) -> VersionSet[T]:
              pass

            def __lt__(self, other: Any) -> bool:
              pass

            def __le__(self, other: Any) -> bool:
              pass

            def __gt__(self, other: Any) -> bool:
              pass

            def __ge__(self, other: Any) -> bool:
              pass

            def __contains__(self, version: V) -> bool:
              pass

            def __len__(self) -> int:
              pass

            def __iter__(self) -> Iterator[V]:
              pass

            def __getitem__(self, index: int) -> V:
              pass

      .. tab-set::

         .. tab-item:: Instantiation

            .. code-block:: python

               from pyTooling.Versioning import SemanticVersion, VersionSet

               versionSet = VersionSet((
                 YearMonthVersion(2024, 4),
                 YearMonthVersion(2025, 1),
                 YearMonthVersion(2019, 3)
               ))

               testVersion = YearMonthVersion(2019, 3)
               if testVersion in versionSet:
                 pass

         .. tab-item:: Iterating Elements

            .. code-block:: python

               from pyTooling.Versioning import SemanticVersion, VersionSet

               versionSet = VersionSet((
                 YearMonthVersion(2024, 4),
                 YearMonthVersion(2025, 1),
                 YearMonthVersion(2019, 3)
               ))

               for version in versionSet:
                 pass


.. _VERSIONING/Constraints:

Version Constraints and Expressions
***********************************

A :class:`~pyTooling.Versioning.VersionRange` says which versions are acceptable; a **version expression** is how a
packaging ecosystem *writes* that down - ``>=1.2.0,<2.0.0`` in a requirements file, ``^1.2.3`` in a
:file:`package.json`, ``(>= 1.2.0)`` in a :file:`debian/control`.

.. _VERSIONING/Constraints/Expression:

VersionExpression
=================

A :class:`~pyTooling.Versioning.VersionExpression` is a **conjunction** of constraints: every one of them has to be
satisfied, which is what separating them means in every ecosystem that has the notion.

.. code-block:: Python

   from pyTooling.Versioning import VersionExpression, SemanticVersion

   expression = VersionExpression.Parse(">=1.2.0,<2.0.0")

   SemanticVersion.Parse("1.5.0") in expression   # True
   SemanticVersion.Parse("2.0.0") in expression   # False

An expression with **no** constraints matches every version, and
:attr:`~pyTooling.Versioning.VersionExpression.MatchesAnyVersion` reports it - so *no version restriction* is a value
its callers can carry rather than a case they have to special-case.

:attr:`~pyTooling.Versioning.VersionExpression.Constraints` gives the individual
:class:`~pyTooling.Versioning.VersionConstraint` objects, and
:meth:`~pyTooling.Versioning.VersionExpression.ToVersionRange` collapses the whole expression into the single
:ref:`VersionRange <VERSIONING/VersionRange>` it describes - which is the bridge between how a dependency is written
and how it is reasoned about.

.. _VERSIONING/Constraints/Constraint:

VersionConstraint
=================

One :class:`~pyTooling.Versioning.VersionConstraint` is one comparison: a
:class:`~pyTooling.Versioning.VersionComparison` and the version it compares against.

.. list-table::
   :header-rows: 1
   :widths: 25 30 45

   * - Written
     - ``VersionComparison``
     - Meaning
   * - ``==`` ``!=``
     - ``Equal`` ``Unequal``
     - Exactly this version, or anything but it.
   * - ``<`` ``<=`` ``>`` ``>=``
     - ``LessThan`` … ``GreaterThanOrEqual``
     - The four ordering comparisons.
   * - ``~=``
     - ``CompatibleRelease``
     - :pep:`440`'s *compatible release*.
   * - ``^``
     - ``Caret``
     - npm's *may not change the leftmost non-zero part*.
   * - ``~``
     - ``Tilde``
     - npm's *may not change the minor part*.

The last three are **shorthands for a range**, and they are what
:class:`~pyTooling.Versioning.RangeVersionConstraint` implements: *at least the version written, and below a bound
derived from it*. The derived bound is readable as
:attr:`~pyTooling.Versioning.RangeVersionConstraint.UpperBound`, and each subclass derives it differently:

.. list-table::
   :header-rows: 1
   :widths: 32 20 48

   * - Class
     - Example
     - Upper bound
   * - :class:`~pyTooling.Versioning.CompatibleVersionConstraint`
     - ``~=1.2.3``
     - ``1.3.0`` - drop the last part written, increment what becomes the last.
   * - :class:`~pyTooling.Versioning.CaretVersionConstraint`
     - ``^1.2.3``
     - ``2.0.0`` - increment the leftmost non-zero part that was written.
   * - :class:`~pyTooling.Versioning.TildeVersionConstraint`
     - ``~1.2.3``
     - ``1.3.0`` - increment the minor part, or the major one when no minor part was written.

.. attention::

   ``~=`` and ``~`` are **not** the same operator: :pep:`440`'s ``~=`` depends on how many parts were written, while
   npm's ``~`` always works on the minor part. They agree for ``1.2.3`` and disagree for ``1.2``.

.. _VERSIONING/Constraints/Dialects:

Dialects
========

The operators above are not spelled the same everywhere, so an expression is parsed by the class belonging to the
ecosystem it was written in.

.. list-table::
   :header-rows: 1
   :widths: 30 20 50

   * - Class
     - Separator
     - Differences
   * - :class:`~pyTooling.Versioning.PythonVersionExpression`
     - ``,``
     - :pep:`440`: the six ordering comparisons plus ``~=``. Versions parse as
       :class:`~pyTooling.Versioning.PythonVersion`.
   * - :class:`~pyTooling.Versioning.NPMVersionExpression`
     - whitespace
     - Equality is ``=``, never ``==``; there is no ``!=``; adds ``^`` and ``~``. A comma is a syntax error.
   * - :class:`~pyTooling.Versioning.DebianVersionExpression`
     - ``,``
     - Strict comparisons are ``<<`` and ``>>``, equality is ``=``, and there is no ``!=``.

.. attention::

   :class:`~pyTooling.Versioning.DebianVersionExpression` deliberately **rejects** the obsolete ``<`` and ``>``.
   :program:`dpkg` still accepts them with a warning, because they historically meant ``<=`` and ``>=`` - reading
   them as the strict operators would silently invert their meaning.


.. _VERSIONING/Epoch:

Epoch
*****

An **epoch** outranks every other part of a version number, and exists for the case a project's versioning scheme
changed so that the new numbers sort below the old ones. It is readable as
:attr:`~pyTooling.Versioning.Version.Epoch`, and it is present only when the parsed string stated one.

The separator differs by scheme: :class:`~pyTooling.Versioning.SemanticVersion` writes ``1:1.2.3``, while
:class:`~pyTooling.Versioning.PythonVersion` writes ``1!1.2.3`` as :pep:`440` prescribes.


.. _VERSIONING/Validators:

Validators
**********

A version parsed from an untrusted string can carry any number, which is a problem when it has to fit a fixed-width
field later. A **validator** is a callable given to the parser, and it rejects a version instead of letting it
through.

Two factories build one:

* :func:`~pyTooling.Versioning.WordSizeValidator` - bounds each part by a number of **bits**, for a version that has
  to fit a hardware register or a packed struct;
* :func:`~pyTooling.Versioning.MaxValueValidator` - bounds each part by an explicit **maximum**.

Both take one limit for every part (``bits`` / ``max``) or a limit per part (``majorBits``, ``minorBits``,
``microBits``, …), so the common case is one argument.

A rejected version raises :exc:`~pyTooling.Versioning.VersionValidatorError`, whose ``Version`` property is the
version that was rejected.

