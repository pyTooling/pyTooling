.. _NEWS:

News
####

See `pyTooling Release Pages <https://github.com/pyTooling/pyTooling/releases>`__ for detail release notes on every
release.


Version 10.x (2026)
*******************

.. topic:: `v10.0.0 - unreleased <https://github.com/pyTooling/pyTooling/releases/v10.0.0>`__

   * Breaking changes

     * **32 exception classes are renamed to the** ``***Error`` **suffix**, as :pep:`8` asks for. Only
       :exc:`~pyTooling.Exceptions.ToolingException`, the package's own base exception, keeps ``Exception``.
       The old names were briefly kept as aliases and are removed in the same release, so an ``import`` or an
       ``except`` clause naming one has to be updated.
     * ``TerminalApplication._PrintHelp`` moved to
       :class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin`, which owns the parsers it prints.

   * :mod:`pyTooling.MetaClasses`

     * A class or a mixin-class can name the members it expects from wherever it ends up, with the new ``expects``
       class keyword argument. The contract is checked at class construction and reported on instantiation, like an
       abstract class.

   * :mod:`pyTooling.Testing`

     * :deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase` mark what a test runner
       collects, so a testcase's name stops carrying two unrelated jobs at once.
     * Both markers take a title, and both fall back to the doc-string: its summary becomes the summary, its body
       becomes the description. A test item has four names - an ID, a title, a summary and a description.
     * :mod:`pyTooling.Testing.PyTest` is a new pytest plugin collecting what the markers mark. Node IDs are left
       untouched, so test selection, ``pytest-xdist``, ``--last-failed`` and IDE integration are unaffected.

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.DescribePythonPackage` declares ``consoleScripts``, ``guiScripts`` and
       ``pytestPlugins``, each knowing the entry point group it belongs to. Previously only ``console_scripts``
       was reachable.

   * :mod:`pyTooling.Decorators`

     * :deco:`~pyTooling.Decorators.InheritDocString` takes one ``strategy`` argument of the new
       :class:`~pyTooling.Decorators.DocStringMergeStrategy`, replacing the ``merge``, ``summaryOnly`` and
       ``order`` parameters. A new strategy inherits just the base-class' summary.

   * :mod:`pyTooling.LinkedList` and :mod:`pyTooling.Graph`

     * Neither module raises its own base exception any more. ``LinkedList`` gained five specific errors and
       ``Graph`` three, so 20 raise sites name what went wrong.

   * Bug fixes

     * :mod:`pyTooling.TerminalUI`: a message's indentation was recorded and never printed. ``BaseIndent`` and the
       ``indent`` parameter of every ``Write*`` method reached :attr:`~pyTooling.TerminalUI.Line.Indent` and got
       lost on the way to the terminal.
     * :file:`doc/conf.py` imported :mod:`pyTooling.Packaging` before inserting the repository into ``sys.path``,
       so nine modules were documented from the *installed* package and the rest from the checkout.

   * Changes

     * 339 f-strings that interpolate nothing lost their ``f`` prefix, across 33 modules.

   * Documentation

     * The eighteen constructors in :mod:`pyTooling.Attributes` document their parameters. Each carried the same
       sentence describing ``*args``/``**kwargs``, which none of them takes.
     * The four documentation-coverage findings that were real are fixed: :meth:`pyTooling.Tree.Node.__delitem__`,
       both comparison operators of :class:`~pyTooling.Licensing.License`, and ``abstract_new()``.

Version 9.x (2026)
******************

.. topic:: `v9.0.0 - 20.08.2026 <https://github.com/pyTooling/pyTooling/releases/v9.0.0>`__

   * :mod:`pyTooling.Testing` is a new module: enhanced classes for writing unit tests with Python's
     :mod:`unittest` framework, which pytest runs as well.

     * :class:`~pyTooling.Testing.ApplicationTestcase` starts the installed program the way a user does, so a test
       covers the ``console_scripts`` entry point, the argument parsing and the exit code.
     * :class:`~pyTooling.Testing.Testcase` adds the assertions newer Python versions gained, so a test suite can
       use them whichever interpreter runs it.

   * Breaking changes

     * ``TerminalBaseApplication.CheckPythonVersion()`` and its exit code are removed - a package's
       ``python_requires`` metadata makes the check unnecessary.
     * ``pyTooling.Warning.UnhandledWarningException`` is removed, as v9.0.0 was announced to do.
     * 34 base-classes in :mod:`pyTooling.CLIAbstraction` raise
       :exc:`~pyTooling.MetaClasses.AbstractClassError` instead of :exc:`TypeError` when instantiated directly.
     * A configuration is read-only: :meth:`pyTooling.Configuration.Node.__setitem__` says so once instead of four
       stubs, and the four methods every backend implements are ``@abstractmethod``.
     * :class:`~pyTooling.Versioning.CalendarVersion` renders only the parts it was given.
       ``YearMonthVersion(2024, 10)`` was ``'2024.10.0'``.
     * :class:`pyTooling.GenericPath.URL.Protocols` is a :class:`~enum.Flag` whose secured schemes are named
       composites, so ``Protocols.TLS in url.Scheme`` answers whether a scheme is encrypted. The numeric values
       change.
     * ``SupervisedThreadException`` takes its message positionally and the attached objects by keyword.
     * Annotations in 26 modules are no longer evaluated at definition time. On Python 3.11-3.13
       ``__annotations__`` yields strings; use :func:`typing.get_type_hints`.

   * :mod:`pyTooling.MetaClasses`

     * :deco:`~pyTooling.MetaClasses.abstractclass` marks a class abstract although it has no abstract method.
     * :class:`~pyTooling.MetaClasses.ExtendedType` forwards any further class keyword argument to
       :meth:`~object.__init_subclass__`.

   * :mod:`pyTooling.Decorators`

     * A :deco:`~pyTooling.Decorators.readonly` property hands out the getter's type instead of :class:`~typing.Any`.

   * Documentation

     * Doc-strings for 10 modules, 47 classes, 127 class fields, 109 dunder methods and the methods that had none;
       134 ``:param:``, 89 ``:returns:`` and 27 ``:raises:`` fields filled in.
     * 41 cross-references pointed nowhere and were corrected; neighbouring modules cross-reference each other.
     * New pages: :file:`doc/Testing.rst` and :file:`doc/Dependency.rst`.

   * Unit tests

     * The whole suite derives from :class:`pyTooling.Testing.Testcase` instead of :class:`unittest.TestCase`.

Version 8.x (2025/2026)
***********************

.. topic:: `v8.19.0 - 31.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.19.0>`__

   * :mod:`pyTooling.Versioning`, :mod:`pyTooling.Attributes`, :mod:`pyTooling.Warning`

     * Ten properties without a setter are marked :deco:`~pyTooling.Decorators.readonly`.

   * :mod:`pyTooling.MetaClasses`

     * :exc:`~pyTooling.MetaClasses.DuplicateFieldInSlotsError` distinguishes its two causes in the notes: a slot
       inherited from a base-class, and a slot contributed by a mixin-class.

   * Bug fixes

     * :mod:`pyTooling.Filesystem`: ``Element.Path`` raised ``NotImplemented(...)``, which is a singleton rather
       than an exception class, so it raised :exc:`TypeError` instead of :exc:`NotImplementedError`.

   * Documentation

     * All 337 properties in the package carry a doc-string with a ``:returns:`` field. 80 had none and 25 more had
       no ``:returns:``.
     * A property that computes its result reads *"Read-only property to return ..."*, a plain field access keeps
       *"to access"*.
     * Documentation coverage rose from 76.28 % to 80.97 %.

.. topic:: `v8.18.0 - 30.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.18.0>`__

   * :mod:`pyTooling.Configuration`

     * Added ``KeyNotFoundException``, ``UnsupportedValueTypeException``, ``InterpolationException`` and
       ``PathExpressionException``. All four were renamed to the ``***Error`` suffix in v10.0.0.

   * :mod:`pyTooling.Dependency`

     * Added ``DependencyException`` as the module's base-exception, three specific exceptions and two warnings.

   * :mod:`pyTooling.MetaClasses`

     * :class:`~pyTooling.MetaClasses.ExtendedType` reports every field assigned in a class body without a type
       annotation, and rejects a slot shadowed by a class member.
     * A :class:`~typing.ClassVar` without an initial value no longer becomes a slot.

   * :mod:`pyTooling.Decorators`

     * :deco:`~pyTooling.Decorators.readonly` is a class deriving from :class:`property`, and rejects
       ``.setter`` and ``.deleter``. A property declared read-only could be made writable further down the class
       body.

   * :mod:`pyTooling.Versioning`

     * :class:`~pyTooling.Versioning.CalendarVersion` accepts the same prefixes as
       :class:`~pyTooling.Versioning.SemanticVersion` and carries a third numeric part.

   * Bug fixes

     * A missing configuration key raised :exc:`ValueError` from an unguarded ``int(key)`` conversion; a missing
       numeric key and a ``null`` value raised an exception with an empty message.
     * The non-slots branch of ``_computeSlots`` had no :pep:`649` fallback, so it saw no annotations on
       Python 3.14.
     * ``YearMonthDayVersion`` dropped the day from ``__str__`` and ``__repr__``.

.. topic:: `v8.17.0 - 20.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.17.0>`__

   * :mod:`pyTooling.Streaming`

     * Added ``BlockingPut``, ``QueueReader`` and ``Delay``.

   * :mod:`pyTooling.Warning`

     * Added ``SupervisedWarningCollector``, ``ThreadSupervisor`` and their exceptions (beta).

.. topic:: `v8.16.1 - 08.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.16.1>`__

   * Reverted a wrong dependency upgrade. Same day as v8.16.0, which carries the features below.

.. topic:: `v8.16.0 - 08.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.16.0>`__

   * :mod:`pyTooling.TerminalUI`

     * Added ``TerminalApplication._PrintHelp``.
     * Reworked ``_PrintVersion``: show project, documentation and issue URLs if defined as dunder-variables.
     * Added ``_GetLatestVersion``, showing whether a newer version is available.

.. topic:: `v8.15.0 - 21.06.2026 <https://github.com/pyTooling/pyTooling/releases/v8.15.0>`__

   * Notes can be attached to warnings raised through ``WarningCollector.Raise``.
   * Added read-only properties ``HasNotes`` and ``Notes`` to all exceptions, and the helper function
     ``addNoteWithItemList``.
   * Added ``ProcessInformation`` and ``MemoryInfo`` to report the memory used by the current process.
   * :mod:`pyTooling.TerminalUI`

     * Added the severity levels ``Exception``, ``ExceptionCause``, ``ExceptionNote``, ``CriticalNote``,
       ``WarningNote`` and ``Silent``, and printing of exception and warning notes.

.. topic:: `v8.14.0 - 21.03.2026 <https://github.com/pyTooling/pyTooling/releases/v8.14.0>`__

   * :mod:`pyTooling.Filesystem`

     * Added method ``IterateDirectories``.

   * ``pyTooling.Filesystem.Docker``

     * Added ``EmptyDirectories``, ``EmptyDirectoryCount`` and ``WriteEmptyDirectoryFile``.
     * ``WriteLayerFiles`` accepts an optional ``fileNamePattern``.

.. topic:: `v8.13.0 - 19.03.2026 <https://github.com/pyTooling/pyTooling/releases/v8.13.0>`__

   * :mod:`pyTooling.Filesystem`

     * Scanning reports a :exc:`PermissionError` as a warning and registers broken and unresolvable symbolic links
       at ``Root``.
     * Added ``Directory.IterateFiles``, the ``SymbolicLink`` properties ``IsConnected``, ``IsBroken`` and
       ``IsOutOfRange``, and the ``Root`` lists of broken and unconnected symbolic links.

   * ``pyTooling.Filesystem.Docker`` is a new module computing file lists for Docker image layers, with ``Layer``
     and ``LayerCake``.

   * ``WarningCollector.Raise`` accepts an optional ``cause`` parameter.

.. topic:: `v8.12.0 - 07.02.2026 <https://github.com/pyTooling/pyTooling/releases/v8.12.0>`__

   * Removed bootstrap code (contributed by `@gtsiam <https://github.com/gtsiam>`__).
   * Fixed a buffer overflow exception caused by ``__GetTerminalSizeOnLinux``.

.. topic:: `v8.11.0 - 18.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.11.0>`__

   * :mod:`pyTooling.Platform`

     * Detect whether the program runs in a CI environment (AppVeyor, GitHub Actions, GitLab CI, Travis CI), with
       the new properties ``IsCI``, ``IsAppVeyor``, ``IsGitHub``, ``IsGitLab`` and ``IsTravisCI``.

.. topic:: `v8.10.0 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.10.0>`__

   * :mod:`pyTooling.CLIAbstraction`

     * Added ``Executable.Wait()``.
     * Reworked ``Executable.Terminate()`` and ``Executable.ExitCode``.

.. topic:: `v8.9.1 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.9.1>`__

   * Bumped copyright information.

.. topic:: `v8.9.0 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.9.0>`__

   * Added pickle support for all classes using the :class:`~pyTooling.MetaClasses.ExtendedType` metaclass with
     slots enabled.
   * :mod:`pyTooling.Tracing` is a new module for software execution tracing: a ``Trace`` is made of ``Span``\ s,
     each with optional ``Event``\ s.
   * :mod:`pyTooling.Dependency` is a new module with a package dependency graph and a resolution algorithm, plus a
     Python specific variant handling PyPI in ``pyTooling.Dependency.Python``.

   * Bug fixes

     * Fixed the uninitialized field ``_nodesWithoutID`` in :class:`pyTooling.Tree.Node`.

.. topic:: `v8.8.0 - 10.11.2025 <https://github.com/pyTooling/pyTooling/releases/v8.8.0>`__

   * Added support for critical warnings: a warning that is raised and not handled causes an exception.

     * New ``Warning`` and ``CriticalWarning`` classes, and the ``UnhandledCriticalWarningException`` and
       ``UnhandledExceptionException`` exceptions.
     * ``WarningCollector`` supports iteration, length and item indexing.

   * Removed code specific to Python versions before 3.11.

   * Bug fixes

     * Removed a wrong ``with_traceback`` overload from ``ExceptionBase``, which caused faults in pytest.

.. topic:: `v8.7.6 - 28.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.6>`__

   * Implemented ``__str__`` for :class:`~pyTooling.Packaging.VersionInformation`.

.. topic:: `v8.7.5 - 27.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.5>`__

   * Bumped dependencies.
   * Fixed a missing ``needs`` rule in the pipeline.

.. topic:: `v8.7.4 - 19.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.4>`__

   * Added Python 3.14 support to the wheel package, and dropped Python 3.9 and 3.10.

.. topic:: `v8.7.3 - 21.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.3>`__

   * Supports Python 3.14 (tested with 3.14rc2).

     * Reworked accessing annotations in the metaclasses due to :pep:`649`.
     * Worked around a packaging problem with :file:`py.typed`.

   * ``WarningCollector`` uses thread local data, which improves performance and allows nested contexts.

.. topic:: `v8.7.2 - 04.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.2>`__

   * Accept :exc:`Exception` instances as warnings (from the failed v8.7.1 release).
   * Disabled Ubuntu ARM images in the pipeline due to instability at GitHub.

.. topic:: `v8.7.0 - 23.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.0>`__

   * :mod:`pyTooling.Versioning`

     * ``VersionRange.LowerBound``, ``.UpperBound`` and ``.BoundHandling`` can be set via property.

   * :mod:`pyTooling.Platform`

     * Added support for Linux AArch64 and Windows AArch64.

   * Removed the experimental ``classproperty`` decorator - support was explicitly revoked by Python.

.. topic:: `v8.6.0 - 12.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.6.0>`__

   * :mod:`pyTooling.Versioning`

     * Added the classes :class:`~pyTooling.Versioning.VersionRange` and
       :class:`~pyTooling.Versioning.VersionSet`.

.. topic:: `v8.5.1 - 14.06.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.1>`__

   * Fixed the instantiation of ``YearReleaseVersion`` from ``CalendarVersion.Parse``.

.. topic:: `v8.5.0 - 31.05.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.0>`__

   * :mod:`pyTooling.Common`

     * New context manager :class:`~pyTooling.Common.ChangeDirectory`.

   * :mod:`pyTooling.TerminalUI`

     * New ``_PrintHeadline`` and ``_PrintVersion`` methods.

   * :mod:`pyTooling.Packaging`

     * Fixed the directory (package) excludes: the exclude list is computed with :func:`os.scandir`, and any
       :file:`__init__.py` from a parent namespace is excluded, because such a file breaks namespace packages
       without notice.

.. topic:: `v8.4.0 - 17.04.2025 <https://github.com/pyTooling/pyTooling/releases/v8.4.0>`__

   * :mod:`pyTooling.LinkedList` is a new module: construct from an iterable, insert at either end or around a
     node, sort, reverse, iterate in both directions, and convert to a tuple or list.
   * :mod:`pyTooling.Cartesian2D` and :mod:`pyTooling.Cartesian3D` are new modules with the basic classes
     (``Origin``, ``Point``, ``Offset``, ``Size``, ``Segment``, ``LineSegment``) and shapes (``Trapezium``,
     ``Rectangle``, ``Square``; ``Cuboid``, ``Cube``).
   * :mod:`pyTooling.Filesystem` is a new module collecting file system statistics: subdirectories, files and
     symbolic links, multiple filenames per file object (hardlinks), aggregated subdirectory sizes, a user defined
     collapse function, and conversion to a :mod:`pyTooling.Tree`.

.. topic:: `v8.3.0 - 16.03.2025 <https://github.com/pyTooling/pyTooling/releases/v8.3.0>`__

   * New count function to count the number of elements in an iterator/generator.
   * Added __setitem__ on pyTooling.CLIAbstraction.Environment.
   * Added __delitem__ on pyTooling.CLIAbstraction.Environment.

.. topic:: `v8.2.0 - 23.02.2025 <https://github.com/pyTooling/pyTooling/releases/v8.2.0>`__

   * Add WarningCollector to handle warnings similar to exceptions and send them along the call stack.

.. topic:: `v8.1.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.1.0>`__

   * Graph

     * Added methods HasVertexByID, HasVertexByValue.
     * Added method GetVertexByValue.

   * Versioning

     * Version classes are now hashable.
     * Added gamma release level.

   * Stopwatch

     * Added Exclude context manager

.. topic:: `v8.0.3 - 17.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.3>`__

   * :func:`~pyTooling.Common.getResourceFile` and :func:`~pyTooling.Common.readResourceFile` are unconditional in
     the package for Python 3.9+.
   * Bug fixes

     * README files, requirement files, GraphML files and JSON/YAML configurations are opened with UTF-8 encoding.

.. topic:: `v8.0.2 - 12.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.2>`__

   * Bug fixes

     * :mod:`pyTooling.Versioning`: fixed the usage of a variable ``max`` that was unassigned and fell back to the
       builtin function.

.. topic:: `v8.0.1 - 10.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.1>`__

   * Bug fixes

     * Fixed the platform name for MSYS2/MinGW32 with Python 3.12.

.. topic:: `v8.0.0 - 09.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.0>`__

   * Reworked semantic and calendar version classes:

     * Moved common implementations to Version base-type.

       * Moved major, minor, micro, build, post, dev, release level, release number, hash, prefix, postfix parts to the base-type.
       * Moved implementations of comparison operators to the base-type: __eq__, __ne__, __lt__, __le__, __gt__, __ge__.
       * Implemented minimum comparison operator using __rshift__ (>>) for PIP's ~= operator.
       * Implemented a formatting helper method _format.

     * Reworked SemanticVersion.

       * Additionally allow comparisons with string and integer types.
       * Enhanced SemanticVersion.Parse() class-method:

         * Raise exceptions on invalid inputs.
         * Use a regular expression to check and split the input.

     * Implemented CalendarVersion (previously a dummy).

       * Added CalendarVersion.Parse() class-method: raise exceptions on invalid inputs.
       * Implemented comparison operators.

     * Added validator classes WordSizeValidator and MaxValueValidator.
     * Added doc-strings.
     * Improved __str__() method to return only used version parts.
     * Added __format__() for user defined formatting specifications.

Version 7.x (2024)
******************

.. topic:: `v7.0.0 - 27.10.2024 <https://github.com/pyTooling/pyTooling/releases/v7.0.0>`__

   * Added support for Python 3.13 (and dropped 3.8).

     * Changed DEFAULT_PY_VERSIONS in pyTooling.Packaging to 3.9...3.13.

   * Reworked faulty Timer class and renamed it to StopWatch.

     * Support start, pause, resume, split and stop operations.
     * Collect active and inactive split times.
     * Accept a name at instantiation.
     * Take absolute time at start and stop via datetime.now().
     * Can be used in a with-statement.

   * @InheritDocString can be applied to classes too.

Version 6.x (2024)
******************

.. topic:: `v6.7.0 - 29.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.7.0>`__

   * :mod:`pyTooling.TerminalUI`

     * Added TerminalApplication.WriteCritical
     * Added TerminalApplication.ExitOnPreviousCriticalWarnings

.. topic:: `v6.6.0 - 18.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.6.0>`__

   * :mod:`pyTooling.Graph`

     * Allow setting key-value-pairs for a graph when creating a new graph.
     * Allow setting key-value-pairs for vertices when creating a new vertex.
     * Allow setting key-value-pairs for edges when creating a new edge.
     * Allow setting key-value-pairs for links when creating a new link.

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.loadReadmeFile` now supports new content formats:

       * plain text
       * ReStructured Text

   * :mod:`pyTooling.Platform`

     * Added :attr:`~pyTooling.Platform.Platform.StaticLibraryExtension`.

.. topic:: `v6.5.0 - 15.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.5.0>`__

   * :mod:`pyTooling.GenericPath`

     * :class:`pyTooling.GenericPath.URL.URL`:

       * Added support for basic authentication credentials (username and password).
       * Added :meth:`pyTooling.GenericPath.URL.URL.WithoutCredentials` method.

.. topic:: `v6.4.0 - 04.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.4.0>`__

   * :mod:`pyTooling.Platform`

     * Added readonly property :attr:`~pyTooling.Platform.Platform.IsNativeFreeBSD` to class Platform.

.. topic:: `v6.3.0 - 02.06.2024 <https://github.com/pyTooling/pyTooling/releases/v6.3.0>`__

   * :mod:`pyTooling.Tree`

     * Accept a custom formatting function per node to return a one-liner representation of a node for tree rendering.
     * Accept a key-value-pair mapping (dictionary) for nodes in a tree in the initializer.

   * :mod:`pyTooling.Graph`

     * Accept a key-value-pair mapping (dictionary) for all data structures (graph, edges, links, vertices, views, ...) in a graph in their initializers.

.. topic:: `v6.2.0 - 30.05.2024 <https://github.com/pyTooling/pyTooling/releases/v6.2.0>`__

   * :mod:`pyTooling.Common`

     * New helper function :func:`pyTooling.Common.getFullyQualifiedName`.
     * Python 3.8+: New helper functions :func:`pyTooling.Common.getResourceFile` and :func:`pyTooling.Common.readResourceFile`.
     * Python 3.11+: In case of :class:`TypeError` add a note to the exception describing the parameter/member type.

.. topic:: `v6.1.0 - 09.04.2024 <https://github.com/pyTooling/pyTooling/releases/v6.1.0>`__

   .. #empty

.. topic:: `v6.0.0 - 14.01.2024 <https://github.com/pyTooling/pyTooling/releases/v6.0.0>`__

   * Integrated ``pyAttributes`` v2.5.1 as :mod:`pyTooling.Attributes`.
   * Integrated :mod:`pyTooling.CLIAbstraction` v0.4.1.

Version 5.x (2023)
******************

.. topic:: `v5.0.0 - 02.07.2023 <https://github.com/pyTooling/pyTooling/releases/v5.0.0>`__

   * New ``ExtendedType`` features:

     * Added support for mixin-classes and delayed creation of slots.
     * Added automatic initializers for annotated fields (previously causing an exception due to slots).
     * Added automatic initializers for annotated class fields (previously causing an exception due to slots).

   * Added new decorators: ``@slotted``, ``@mixin``, ``@singleton``, ``@readonly``, and ``@notimplemented``.

   * Added JSON support for ``pyTooling.Configuration``.
   * New ``Platform`` features:

     * Added ``PythonVersion`` to ``Platform`` to distinguish Python versions.
     * Added ``PythonImplementation`` to ``Platform`` to distinguish CPython and PyPy.

   * New graph features:

     * ``GetVertexByID``
     * ``GetVertexByValue``
     * New vertex operations: ``IterateAllOutboundPathsAsVertexList``, ``Delete`` (itself), ``DeleteEdgeTo``, ``DeleteEdgeFrom``, ``DeleteLinkTo``, ``DeleteLinkFrom``.
     * New edge operations: ``Delete`` (itself)
     * New link operations: ``Delete`` (itself)

   * ``pyToolong.StateMachine`` package (alpha version).

Version 4.x (2023)
******************

.. topic:: `v4.0.1 - 26.03.2023 <https://github.com/pyTooling/pyTooling/releases/v4.0.1>`__

   * Graphs are now supporting subgraphs and exporting subgraphs to GraphML.

     * New ``SubGraph`` class.
     * New ``Link`` class.
     * New ``View`` class.

   * Added ``Vertex.Link***Vertex`` methods to link vertices from disjunctive subgraphs.
   * Added ``Vertex.HasLink***Vertex`` methods check if two vertices from disjunctive subgraphs are connected.
   * Added ``Vertex.Iterate***boundLinks`` to iterate links.
   * Added ``Graph.IterateLinks`` to iterate all links.
   * Added ``Graph.ReverseLinks``, ``Graph.RemoveLinks``.
   * Applied generic types when deriving from subclasses.
   * Added ``in`` operator for key-value

Version 3.x (2023)
******************

.. topic:: `v3.0.0 - 10.03.2023 <https://github.com/pyTooling/pyTooling/releases/v3.0.0>`__

   * Integrated :mod:`pyTooling.TerminalUI`.
   * Support for FreeBSD in ``Platform``.
   * A data model for GraphML (graph, node, edge, key, data and subgraph).
   * A conversion from pyTooling's graph data structure to GraphML XML files.
   * A conversion from pyTooling's tree data structure to GraphML XML files.

Jan. 2023 - Graph enhancements
******************************

* Improved exceptions.
* Added ``ConvertToTree`` method to ``Vertex``.
* Added ``Render`` method to ``Node``.

Nov. 2023 - Graph implementation
********************************

* Added an object-oriented graph implementation.

Archive
*******

Attributes
==========

.. only:: html

   Jan. 2024 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Jan. 2024 - Direct integration into pyTooling

* The standalone package ``pyAttributes`` v2.5.1 has been integrated as :mod:`pyTooling.Attributes` into pyTooling
  v6.0.0.


.. only:: html

   Nov. 2021 - Moved to pyTooling
   ------------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Moved to pyTooling

* Changed repository location from ``Paebbels/pyAttributes`` to ``pyTooling/pyAttributes``.


.. only:: html

   Jan. 2020 - Enhancements
   ------------------------

.. only:: latex

   .. rubric:: Jan. 2020 - Enhancements

* ``GetMethods`` and ``GetAttributes`` adhere to method resolution order (MRO) to find attributes annotated to methods
  from base-classes.
* An ``AttributeHelperMixinclass`` to ease the usage of attributes on a class' methods.


.. only:: html

   Dec. 2019 - Merge from IPCMI
   ----------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Merge from IPCMI

* Merged latest implementation updates from pyIPCMI.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* Basic attribute class.
* Attribute helper classes.
* Package for handling Python's argparse as declarative code.


CallByRef
=========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.CallByRef`` v1.2.1 has been integrated as :mod:`pyTooling.CallByRef` into pyTooling
  vX.X.X.


.. only:: html

   Sep. 2020 - Bug Fixes
   ---------------------

.. only:: latex

   .. rubric:: Sep. 2020 - IBug Fixes

* Some bugfixes.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* Call-by-reference implementation for Python.


CLIAbstraction
==============

.. only:: html

   Jan. 2024 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Jan. 2024 - Direct integration into pyTooling

* The namespace package ``pyTooling.CLIAbstraction`` v0.4.1 has been integrated as :mod:`pyTooling.CLIAbstraction` into
  pyTooling v6.0.0.


.. only:: html

   Feb. 2022 - Major Update
   ------------------------

.. only:: latex

   .. rubric:: Major Update

* Reworked names of Argument classes.
* Added missing argument formats like PathArgument.
* Added more unit tests and improved code-coverage.
* Added doc-strings and extended documentation pages.


.. only:: html

   Dec. 2021 - Extracted CLIAbstraction from pyIPCMI
   -------------------------------------------------

.. only:: latex

   .. rubric:: Extracted CLIAbstraction from pyIPCMI

* The CLI abstraction has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


CommonClasses
=============

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.CommonClasses`` v0.2.3 has been integrated into pyTooling vX.X.X.


.. only:: html

   Feb. 2021 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Feb. 2021 - Initial Release

* Added ``Version`` class.


Exceptions
==========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.Exceptions`` v1.1.1 has been integrated as :mod:`pyTooling.Exceptions` into
  pyTooling vX.X.X.


.. only:: html

   Sep. 2020 - Unit tests
   ----------------------

.. only:: latex

   .. rubric:: Sep. 2020 - Unit tests

* Added unit tests.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* An initial set of exceptions has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


GenericPath
===========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.GenericPath`` v0.2.5 has been integrated as :mod:`pyTooling.GenericPath` into
  pyTooling vX.X.X.

.. only:: html

   Dec. 2021 - Namespace package
   -----------------------------

.. only:: latex

   .. rubric:: Dec. 2021 - Namespace package

* Renamed ``pyGenericPath`` to :mod:`pyTooling.GenericPath`.


.. only:: html

   Oct. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Oct. 2019 - Initial Release

* An initial set of exceptions has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.


MetaClasses
===========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.MetaClasses`` v1.3.1 has been integrated as :mod:`pyTooling.MetaClasses` into
  pyTooling vX.X.X.


.. only:: html

   Aug. 2020 - Overloading
   -----------------------

.. only:: latex

   .. rubric:: Aug. 2020 - Overloading

* First implementation of method overloading via a meta-class.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* First singleton metaclass to implement the singleton pattern in Python.


Packaging
=========

.. only:: html

   Dec. 2021 - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: Dec. 2021 - Direct integration into pyTooling

* The namespace package ``pyTooling.Packaging`` v0.5.0 has been integrated as :mod:`pyTooling.Packaging` into
  pyTooling vX.X.X.


.. only:: html

   Nov. 2021 - Major enhancements
   ------------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Major enhancements

* Reading package information from Python source code via Python's AST.
* Support more licenses.


.. only:: html

   Nov. 2021 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Initial Release

* Abstract setuptools.setup to ease handling of Python package descriptions.
* Read long description from README.md
* Read package dependencies from requirements.txt
* Construct classifiers
* Construct URLs for packages hosted on GitHub.


TerminalUI
==========

.. only:: html

   xxx. 20XX - Direct integration into pyTooling
   ---------------------------------------------

.. only:: latex

   .. rubric:: xxx. 20XX - Direct integration into pyTooling

* The namespace package ``pyTooling.TerminalUI`` v1.5.9 has been integrated as :mod:`pyTooling.TerminalUI` into pyTooling
  vX.X.X.


.. only:: html

   Nov. 2021 - Namespace package
   -----------------------------

.. only:: latex

   .. rubric:: Nov. 2021 - Namespace package

* Renamed ``pyTerminalUI`` to :mod:`pyTooling.TerminalUI`.


.. only:: html

   Aug. 2020 - Enhancements
   ------------------------

.. only:: latex

   .. rubric:: Aug. 2020 - Enhancements

* New ``ExitOnPrevious***`` methods.


.. only:: html

   Dec. 2019 - Initial Release
   ---------------------------

.. only:: latex

   .. rubric:: Dec. 2019 - Initial Release

* TerminalUI has been extracted from `pyIPCMI <https://GitHub.com/Paebbels/pyIPCMI>`__.
* Basic functionality to use a text based application in a terminal window.
