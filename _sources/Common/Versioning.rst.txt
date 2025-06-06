.. _VERSIONING:

Versioning
##########

The :mod:`pyTooling.Versioning` package provides auxiliary classes to implement :ref:`VERSIONING/SemanticVersion`
(following `SemVer <https://semver.org/>`__ rules) and :ref:`VERSIONING/CalendarVersion` (following
`CalVer <https://calver.org/>`__ rules). The latter one has multiple variants due to the meaning of the version's parts
like: year-month version or year-week version.


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
        Operators for ``==``, ``!=``, ``<``, ``<=``, ``>``, ``>=``, ``%=``.

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
