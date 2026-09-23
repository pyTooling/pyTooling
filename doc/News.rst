.. _NEWS:

News
####

See `pyTooling Release Pages <https://github.com/pyTooling/pyTooling/releases>`__ for detail release notes on every
release.


Version 10.x (2026)
*******************

.. topic:: `v10.0.0 - unreleased <https://github.com/pyTooling/pyTooling/releases/v10.0.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.REST` is a new package: a small client for JSON REST APIs, built on the standard library, so
     nothing building on it drags an HTTP stack into every consumer.

     * A resource is addressed by its path below :attr:`~pyTooling.REST.RESTClient.APIURL`, which is a
       :class:`~pyTooling.GenericPath.URL.URL`, so the API is stated once instead of in every call.
     * :meth:`~pyTooling.REST.RESTClient.GetJSONObject` reads a resource and says where its next page is;
       :meth:`~pyTooling.REST.RESTClient.PostJSONObject`, :meth:`~pyTooling.REST.RESTClient.PutJSONObject`,
       :meth:`~pyTooling.REST.RESTClient.PatchJSONObject` and :meth:`~pyTooling.REST.RESTClient.DeleteResource`
       write one.
     * The answer's media type is checked before it is read as a JSON object.
       :meth:`MediaType.Matches <pyTooling.REST.MediaType.Matches>` asks whether a ``Content-Type`` header names a
       media type: the header's parameters are ignored, the name is compared case-insensitively, and the :rfc:`6839`
       structured syntax suffix counts, so ``application/vnd.github+json`` is ``application/json``.
     * The next page is read from the :rfc:`8288` ``Link`` header. One pointing outside the client's own API is
       rejected rather than followed, because the token is only sent to that API.
     * A transiently failing request - :data:`~pyTooling.REST.TRANSIENT_HTTP_STATUS`, a timeout, or an unreachable
       API - is tried again after an exponentially growing pause, or one as long as a ``Retry-After`` header
       demands, capped at :data:`~pyTooling.REST.MAXIMUM_RETRY_AFTER`. A request that isn't idempotent - ``POST``
       and ``PATCH`` - is sent once, because repeating it can create or change a resource twice.
     * :meth:`~pyTooling.REST.RESTClient._Authorization` and :meth:`~pyTooling.REST.RESTClient._AddErrorNotes` are
       what a client of one API overrides: the bearer scheme of :rfc:`6750` is the default, and a status means what
       that API says it means.
     * ``JSONObject`` is declared here now; :mod:`pyTooling.CI` re-exports it, so an import naming it there keeps
       working.

   * :mod:`pyTooling.CI` is a new package holding data models of continuous integration services.

     * :mod:`pyTooling.CI.GitHub` reads a GitHub Actions workflow run into a tree of
       :class:`~pyTooling.CI.GitHub.Pipeline`, :class:`~pyTooling.CI.GitHub.Workflow`,
       :class:`~pyTooling.CI.GitHub.Matrix`, :class:`~pyTooling.CI.GitHub.Job` and
       :class:`~pyTooling.CI.GitHub.Step` objects, each knowing its parent and the run it belongs to.
     * A called workflow and a matrix are encoded in a job's name - ``Caller / Job`` and
       ``Job (ubuntu-26.04, 3.14)`` - and :meth:`~pyTooling.CI.GitHub.Pipeline.FromJSON` reads them back into the
       tree. Neither level reports times, so :class:`~pyTooling.CI.GitHub.JobGroup` spans the jobs below it.
     * A job's times **contain its steps**. GitHub reports both in whole seconds and independently, so a step is
       sometimes reported as starting before, or completing after, the job holding it - and a consumer building a
       tree then has a child outside its parent. The job is the timespan that stretches, because the step really
       did run when it says it did, and a group's times follow.
     * A group iterates what it holds **in the order it was queued**, jobs and nested groups alike, rather than
       jobs first and called workflows last. The sort is stable, so elements reporting no time keep the order
       GitHub listed them in.
     * A group's times span what it holds - its jobs, and for a :class:`~pyTooling.CI.GitHub.Workflow` the matrices
       and called workflows below it as well. :class:`~pyTooling.CI.GitHub.Workflow` needed three overrides to say
       that and has none now.
     * A :class:`~pyTooling.CI.GitHub.Pipeline` is the one group reporting times of its own, so it is the one with
       two sets: :attr:`~pyTooling.CI.GitHub.Pipeline.ContentsCreatedAt`,
       :attr:`~pyTooling.CI.GitHub.Pipeline.ContentsStartedAt` and
       :attr:`~pyTooling.CI.GitHub.Pipeline.ContentsCompletedAt` span what the run holds, beside the run's own
       times. They differ, because a job may be queued before the run reports itself created.
     * ``status``, ``conclusion`` and ``event`` become :class:`~pyTooling.CI.GitHub.Status`,
       :class:`~pyTooling.CI.GitHub.Conclusion` and :class:`~pyTooling.CI.GitHub.Event` members, so a value GitHub
       doesn't document raises :exc:`~pyTooling.CI.GitHub.GitHubError` instead of matching no comparison.
     * :class:`~pyTooling.CI.GitHub.PipelineGroup` holds every run of one commit, and
       :meth:`~pyTooling.CI.GitHub.PipelineGroup.ByGitReference` separates a commit's checks from the run at its tag,
       which the API reports under the same commit.
     * :class:`~pyTooling.CI.GitHub.QualifiedNameMixin` reports an element's name the way GitHub does -
       ``Caller / Build (ubuntu-26.04)`` - so the name :meth:`~pyTooling.CI.GitHub.Pipeline.FromJSON` took apart can
       be put back together. :class:`~pyTooling.CI.GitHub.Job` and :class:`~pyTooling.CI.GitHub.Workflow` are named
       that way; the mixin ``expects`` the field it walks, so mixing it into a class without ``_parent`` is reported
       instead of failing with an :exc:`AttributeError` later.
     * Iterating a :class:`~pyTooling.CI.GitHub.Workflow` yields its jobs, its matrices **and** the workflows it
       calls, so the containers one level below it are reachable without asking for each kind separately.
       :meth:`~pyTooling.CI.GitHub.Workflow.IterateJobs` remains the way to reach every job below it. Because an
       element is placed in its group under its own name, every ``in`` of this module takes that name:
       :pycode:`"UnitTesting" in pipeline`.

   * :class:`~pyTooling.MetaClasses.ThisClass` is a sentinel for a class variable whose value is the class declaring
     it.

     * A class variable naming the class it is declared in couldn't be written, because the class doesn't exist while
       its body runs - it had to be assigned after the class statement. ``ClassVar[...] = ThisClass`` says it in the
       body, and :class:`~pyTooling.MetaClasses.ExtendedType` rebinds it once the class exists.
     * Only a variable the class **declared** is rebound; an inherited one keeps the value its own class resolved.
       The value is read back from the class, so an ``__init_subclass__`` that replaced it wins.
     * The sentinel is an empty class rather than a bare object, so a variable annotated as a :class:`type` still
       type-checks.

   * :meth:`~pyTooling.GenericPath.PathMixin.WithoutTrailingDelimiter` returns a path that doesn't end in
     ``ELEMENT_DELIMITER``, and :meth:`~pyTooling.GenericPath.URL.URL.WithoutTrailingSlash` a URL whose path doesn't -
     a URL's element delimiter is the slash. A trailing delimiter is an empty last element, so ``/api/v3/`` and
     ``/api/v3`` are different paths although they usually name the same thing - and a path something is appended to
     wants the latter. A path with none answers with itself.
   * ``URL / resource`` and ``path / resource`` compose - :meth:`~pyTooling.GenericPath.URL.URL.__truediv__` and
     :meth:`~pyTooling.GenericPath.PathMixin.__truediv__`, each taking a string or a path on the right, the way
     :class:`pathlib.PurePath` does. The right side is a **relative reference**: its path goes
     below the left side's, and a string brings its own query and fragment, which the left side's are not carried
     into, the way :rfc:`3986` resolves one. A path that starts with the delimiter names its own root and replaces
     the left side, as :mod:`pathlib` joins a path. A trailing delimiter on the left is dropped first, so composing
     ``/api/`` with ``things`` names ``/api/things`` and not an empty element between them. A string on a URL's right
     side is checked to be a relative reference: it names no authority (no leading ``//``) and no scheme (no ``:`` in
     the first path element, :rfc:`3986`'s ``path-noscheme``), and holds none of the characters the RFC forbids -
     ``URL.Parse("https://example.org/api") / "https://elsewhere.org/things"`` raises instead of appending a URL to a
     path.
   * A path flavour names the type of its elements - ``ELEMENT_TYPE``, beside ``ELEMENT_DELIMITER`` and
     ``ROOT_DELIMITER``. :meth:`~pyTooling.GenericPath.PathMixin.Parse` reads that instead of being handed the path
     and element classes as parameters, so its signature is ``Parse(path, root=None)`` and a flavour needs no
     ``Parse`` of its own - :class:`~pyTooling.GenericPath.URL.Path` lost the one it had. **A flavour outside
     pyTooling passing ``pathCls`` and ``elementCls`` has to drop them and declare ``ELEMENT_TYPE``.**
   * :meth:`~pyTooling.GenericPath.PathMixin.Parse` strips ``ROOT_DELIMITER`` from an absolute path, not as many
     characters as ``ELEMENT_DELIMITER`` is long. The two are the same in a URL, so nothing parses differently today,
     but a path flavour marking its root differently - a drive letter, a host separated by a colon - would have lost
     the wrong number of characters.

   * :mod:`pyTooling.GenericPath.URL` reports what it rejects, and raises
     :exc:`~pyTooling.GenericPath.URL.URLError` for it.

     * :exc:`~pyTooling.GenericPath.URL.URLError` replaces the bare
       :exc:`~pyTooling.Exceptions.ToolingException` the module raised, so a consumer can catch a URL problem
       without catching everything pyTooling raises. It still derives from it.
     * A rejected URL holding a character :rfc:`3986` forbids - a space, a control character, ``<``, ``|``,
       ... - gets a note naming it and its percent-encoding, e.g. *"Character ' ' is not allowed in a URL.
       Write it percent-encoded as '%20'."*
     * :class:`~pyTooling.GenericPath.URL.Protocols` gains ``ws``, ``wss``, ``ssh``, ``sftp``, ``git``,
       ``ldap`` and ``ldaps``. A scheme missing from the enumeration makes a URL unparseable, so the list
       grows as schemes are needed. ``sftp`` is carried by :attr:`~Protocols.SSH` rather than being
       :attr:`~Protocols.FTP` plus :attr:`~Protocols.TLS` - that combination is :attr:`~Protocols.FTPS`.
     * :attr:`~pyTooling.GenericPath.URL.Protocols.IsEncrypted` answers whether a scheme is secured, by TLS or
       by SSH. Testing :attr:`~pyTooling.GenericPath.URL.Protocols.TLS` alone answers *"is this TLS"* and
       misses ``ssh`` and ``sftp``, which are encrypted and carry no TLS flag.
     * ``tcp``, ``udp`` and ``unix`` name an endpoint whose higher protocol is unspecified -
       ``tcp://0.0.0.0:2375`` as the Docker daemon writes it, ``unix:///var/run/docker.sock`` for a local
       socket. They do not combine with the other schemes: ``http://`` runs over TCP without saying so.
     * ``mqtt``/``mqtts``, ``amqp``/``amqps``, ``redis``/``rediss``, ``mongodb`` and
       ``postgres``/``postgresql`` are listed too.
     * A **bracketed IPv6 literal is parsed as the host**: ``https://[2001:db8::1]:8080/path`` gave a host of
       ``None`` and a path of ``[2001:db8::1]:8080/path``, while reassembling into the original string - so a
       round-trip looked correct while the model was wrong.

     * :meth:`~pyTooling.GenericPath.URL.URL.Parse` checks its parameter: ``None`` raises a :exc:`ValueError` and a
       value of another type a :exc:`TypeError` naming it, instead of the :mod:`re` module reporting *"expected
       string or bytes-like object"* about neither the parameter nor the value.
     * An unknown scheme raises a :exc:`~pyTooling.Exceptions.ToolingException` listing the known ones, where
       ``ftpx://host`` used to raise ``KeyError: 'FTPX'``.
     * A query parameter that is no ``key=value`` pair raises a :exc:`~pyTooling.Exceptions.ToolingException` naming
       it, where ``?flag`` used to raise *"not enough values to unpack"*. A ``=`` inside a **value** is legal and no
       longer an error - ``?key=a=b`` parses as ``{"key": "a=b"}``, where it used to raise *"too many values to
       unpack"*.

   * :mod:`pyTooling.MetaClasses`

     * A class or a mixin-class can name the members it expects from wherever it ends up, with the new ``expects``
       class keyword argument. The contract is checked at class construction and reported on instantiation, like an
       abstract class.

   * :mod:`pyTooling.Documentation` is a new module holding the helpers that work on doc-strings.

     * :func:`~pyTooling.Documentation.splitDocString` splits a doc-string into its **summary** - the first
       paragraph - and its **body**. Three unrelated features read a doc-string that way: the doc-string merge
       strategies, a package's short description, and a testcase's names.
     * A summary is a single sentence, so its length is bounded by
       :data:`~pyTooling.Documentation.MAXIMUM_SUMMARY_LENGTH`. A longer first paragraph raises a
       :exc:`~pyTooling.Documentation.DocumentationError`, because it is a body that lost its summary.

   * :mod:`pyTooling.Testing`

     * :class:`~pyTooling.Testing.ApplicationTestcase` no longer requires ``_runnableModule``: a program without a
       ``__main__`` module is tested through its entry point, and only
       :meth:`~pyTooling.Testing.ApplicationTestcase.RunModule` asks for the module.
     * :deco:`~pyTooling.Testing.testsuite` and :deco:`~pyTooling.Testing.testcase` mark what a test runner
       collects, so a testcase's name stops carrying two unrelated jobs at once.
     * Both markers take a title, and both fall back to the doc-string: its summary becomes the summary, its body
       becomes the description. A test item has four names - an ID, a title, a summary and a description.
     * :mod:`pyTooling.Testing.PyTest` is a new pytest plugin collecting what the markers mark. Node IDs are left
       untouched, so test selection, ``pytest-xdist``, ``--last-failed`` and IDE integration are unaffected.
     * :mod:`pyTooling.Testing.ReportWriter` is a second plugin writing a **test report format of our own**,
       opt-in through ``--pytooling-xml=PATH`` and additional - it runs in the same session as ``--junit-xml``, so
       a pipeline keeps the format its dashboard understands while the richer file appears beside it. Test suites
       **nest** instead of being flattened into a dotted ``classname``, every level can carry a title and a
       description, and a description's line breaks survive.
     * The format has a versioned schema, :file:`TestReport-v0.1.xsd`, shipped as a package resource and published
       in the documentation.
     * The names of every test suite level reach the **JUnit** report too, as test suite properties keyed by the
       level's dotted path. The innermost key is the testcase's ``classname`` and every outer one is a prefix of
       it, which is what lets a reader join the two.

   * :mod:`pyTooling.Licensing`

     * **27 more SPDX licenses**, taking ``SPDX_INDEX`` from 4 to 31 - permissive, weak and strong copyleft,
       and public domain. The ``-only``/``-or-later`` pairs are separate licenses, as SPDX defines them, because
       PyPI has a distinct classifier for each.
     * The six **Creative Commons 4.0** licenses (``CC-BY-4.0``, ``CC-BY-SA-4.0``, ``CC-BY-NC-4.0``,
       ``CC-BY-ND-4.0``, ``CC-BY-NC-SA-4.0``, ``CC-BY-NC-ND-4.0``) are among them, for documentation and media. PyPI
       has no classifier for them, so asking one for its classifier raises a :exc:`ValueError`.
     * ``SPDX_INDEX`` is built from the licenses rather than repeating each identifier, so the two can no longer
       disagree.
     * A :class:`~pyTooling.Licensing.License` is hashable and compares equal to its SPDX identifier as a string,
       so it can be a dictionary key and be looked up by what a user writes.

   * :mod:`pyTooling.Attributes.ArgParse`

     * :func:`~pyTooling.Attributes.ArgParse.splitFormat` splits an option's value of the form
       ``[<format>:]<file>`` into the format and the file, for any program declaring an option of that shape. A
       format is more than one character long and holds no path separator, so a Windows drive and a colon deeper
       down a path stay part of the path. The formats are a :class:`~pyTooling.Common.StringEnum`, and a value
       naming none gets its ``DEFAULT`` - or raises a :exc:`ValueError`, if the enumeration declares none.

   * :mod:`pyTooling.CLI`

     * pyTooling installs a **program of its own**: :program:`pyTooling`, the ``console_scripts`` entry point
       :pycode:`pyTooling.CLI:main`. It is a :class:`~pyTooling.TerminalUI.TerminalApplication` whose commands are
       declared as :mod:`pyTooling.Attributes.ArgParse` attributes, and it starts with :pycode:`help` and
       :pycode:`version`. A group of commands is a mixin-class, so a new command adds a base-class and nothing else.
     * The :pycode:`pipeline` command reads a **GitHub Actions workflow run** into a trace -
       :pycode:`--github-pipeline-id`, defaulting to :pycode:`$GITHUB_RUN_ID` - and writes it with
       :pycode:`--trace-file=[<format>:]<file>`, where the format defaults to ``otlp-json``. :pycode:`--force`
       overwrites a file that exists.
     * :pycode:`--gantt=[<format>:]<file>` draws the run as a **Gantt chart** - ``matplotlib-png``,
       ``matplotlib-svg`` or ``matplotlib-pdf``, defaulting to ``matplotlib-png``. The file's suffix has to agree
       with the format.
     * The new application tests in :file:`tests/app` run the installed program.
     * **The program needs the new** ``cli`` **extra**: :pycode:`pip install pyTooling[cli]`. It is the
       ``terminal`` and ``diagram`` extras together - *colorama*, without which a terminal application writes
       nothing, and *matplotlib*, which :pycode:`--gantt` draws with. The minimal installation registers the
       program but leaves both out, and the program then reports the missing package and the commands installing
       it.

   * :mod:`pyTooling.TerminalUI`

     * :meth:`~pyTooling.TerminalUI.TerminalApplication.WriteErrorNote` writes the note belonging to an error - the
       advice for fixing it - as :attr:`Severity.Error <pyTooling.TerminalUI.Severity>` was the only severity of
       its group without one.

   * :mod:`pyTooling.Diagram`

     * A new namespace for **data models of diagrams**, which describe a picture without drawing it.
       :mod:`pyTooling.Diagram.Gantt` describes a **Gantt chart** - a :class:`~pyTooling.Diagram.Gantt.Diagram` of
       :class:`~pyTooling.Diagram.Gantt.Row`\ s of :class:`~pyTooling.Diagram.Gantt.Bar`\ s on a time scale. An
       element is created with its parent and knows the diagram it belongs to, and a bar reports where it is three
       ways: as times, as the distance from the diagram's origin, and as the distance from its row.

   * :mod:`pyTooling.Tracing`

     * :class:`~pyTooling.Tracing.Span` and :class:`~pyTooling.Tracing.Event` are
       :class:`~pyTooling.Tracing.TraceElement`\ s - a **name**, the timespan **enclosing** them, and their
       **attributes**, which each of them declared and validated itself before.
     * A trace's elements answer :meth:`~pyTooling.Tracing.TraceElement.get`, which reads an attribute that may not
       be there and returns a default value instead of raising.

     * A software execution trace exports itself as **OTLP/JSON** - :meth:`~pyTooling.Tracing.Trace.ToJSON`,
       :meth:`~pyTooling.Tracing.Trace.ToJSONString` and :meth:`~pyTooling.Tracing.Trace.WriteJSONFile`. One
       format reaches both usual destinations: an OpenTelemetry collector accepts OTLP natively, and Jaeger has
       accepted it since v1.35.
     * The document is typed rather than a mapping of :class:`~typing.Any`: ten :class:`~typing.TypedDict` classes
       name the OTLP messages they encode, from :class:`~pyTooling.Tracing.OTLPDocument` down to
       :class:`~pyTooling.Tracing.OTLPAnyValue`.
     * A trace and each of its timespans draw their identifiers when they are **constructed**, so exporting one
       trace twice reports the same ``traceId``, and :attr:`~pyTooling.Tracing.Trace.TraceID` can be handed to
       another process.
     * An attribute's value is a :data:`~pyTooling.Tracing.AttributeValue` - the types OTLP's ``AnyValue`` carries,
       nested as deeply as needed. A value of any other type is rejected rather than stringified.
     * A trace and its timespans can be constructed with **recorded times** - ``beginTime`` and ``endTime`` - for
       timespans measured elsewhere, e.g. by a CI service. Without them, a timespan is timed by its
       ``with``-statement as before.
     * :mod:`pyTooling.Tracing.CI.GitHub` reads a **GitHub Actions workflow run** into a trace: jobs, their steps,
       the time each job waited for a runner, and called workflows and matrices as groups. The timespans carry
       OpenTelemetry's CI/CD attributes, so a rendering or a query doesn't depend on the CI service. A transiently
       failing request is tried again.
     * The run is read by :mod:`pyTooling.CI.GitHub`, so reconstructing the tree is the model's job and
       :meth:`~pyTooling.Tracing.CI.GitHub.WorkflowRunTrace.FromPipeline` converts a model that was built elsewhere.
     * Every kind of timespan is a class: :class:`~pyTooling.Tracing.CI.PipelineTrace`,
       :class:`~pyTooling.Tracing.CI.WorkflowSpan`, :class:`~pyTooling.Tracing.CI.MatrixSpan`,
       :class:`~pyTooling.Tracing.CI.QueuedSpan`, :class:`~pyTooling.Tracing.CI.JobSpan` and
       :class:`~pyTooling.Tracing.CI.StepSpan`. Each names its kind in ``KIND`` and takes the conventions'
       attributes as parameters, so a reader states values and never a key, and an unknown value sets no attribute.
       The classes are service-independent, and :mod:`pyTooling.Tracing.CI.GitHub` derives them into flavours that
       build themselves from the model -
       :meth:`JobSpan.FromJob <pyTooling.Tracing.CI.GitHub.JobSpan.FromJob>`. Everything below the trace derives
       from the abstract :class:`~pyTooling.Tracing.CI.TaskSpan`, because it is a *task* in the conventions' sense.
     * The attribute keys are namespaces nested the way the keys themselves are, instead of a flat block of module
       constants: :class:`~pyTooling.Tracing.CI.OTLP` for OpenTelemetry's conventions,
       :class:`~pyTooling.Tracing.CI.CI` for what pyTooling adds and :class:`~pyTooling.Tracing.CI.GitHub.GitHub` for
       what only GitHub reports, so :attr:`OTLP.CICD.Pipeline.Task.Run.ID <pyTooling.Tracing.CI.OTLP>` spells
       ``cicd.pipeline.task.run.id``. The closed value sets are enumerations -
       :class:`~pyTooling.Tracing.CI.SpanKind` and :class:`~pyTooling.Tracing.CI.Result`.
     * A trace **renders as a Gantt chart**: :class:`~pyTooling.Tracing.Render.GanttLayout` arranges the timespans
       in rows independently of a drawing library, and a :class:`~pyTooling.Tracing.Render.Renderer` draws what it
       arranged. :class:`~pyTooling.Tracing.Render.Matplotlib.MatplotlibRenderer` writes the chart as SVG, PNG or
       PDF; matplotlib is installed by the new extra ``pyTooling[diagram]``. Everything no drawing library decides -
       the categories' colors and the legend's texts - is on the base-class, so a second backend repeats none of it.
     * A Gantt chart written as SVG can be **collapsible**: a click on a called workflow or a job hides or shows the
       rows below it.

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.DescribePythonPackage` declares ``consoleScripts``, ``guiScripts`` and
       ``pytestPlugins``, each knowing the entry point group it belongs to. Previously only ``console_scripts`` was
       reachable.
     * A package's **short description is the first paragraph of its module doc-string**, so a package is described
       in one place instead of two. The paragraph is folded into a single line and emphasis around the whole of it
       is removed, because nothing renders ReST where a short description is displayed.
     * The module raises its own :exc:`~pyTooling.Packaging.PackagingError`, so a caller can catch what this module
       reports without catching everything derived from :exc:`~pyTooling.Exceptions.ToolingException`.

   * :mod:`pyTooling.Common`

     * :func:`~pyTooling.Common.parseISO8601Timestamp` parses an ISO 8601 timestamp. Whether a timestamp carrying no
       UTC offset stays naive is the caller's decision, given as ``defaultTimeZone``.
     * :class:`~pyTooling.Common.StringEnum` is a :class:`~enum.StrEnum` that converts a string to the member of
       that value: :meth:`~pyTooling.Common.StringEnum.Parse` rejects a non-string with a :exc:`TypeError` and an
       unknown value with a :exc:`ValueError` listing the values it accepts, and answers a missing value with the
       member the enumeration declares as ``DEFAULT`` - an alias, so it isn't iterated - or with ``None`` where
       there is none. :class:`~pyTooling.REST.MediaType`, :class:`~pyTooling.Tracing.CI.SpanKind` and
       :class:`~pyTooling.Tracing.CI.Result` derive from it.
       :class:`~pyTooling.CI.GitHub.Status`, :class:`~pyTooling.CI.GitHub.Conclusion` and
       :class:`~pyTooling.CI.GitHub.Event` derive from it too, and show how an enumeration of a domain with its
       own exception keeps it: their ``Parse`` calls the inherited one and re-raises a
       :exc:`~pyTooling.CI.GitHub.GitHubError` with the :exc:`ValueError` as its cause.

   * :mod:`pyTooling.Decorators`

     * :deco:`~pyTooling.Decorators.InheritDocString` takes one ``strategy`` argument of the new
       :class:`~pyTooling.Decorators.DocStringMergeStrategy`, replacing the ``merge``, ``summaryOnly`` and
       ``order`` parameters. A new strategy inherits just the base-class' summary.

   * :mod:`pyTooling.LinkedList` and :mod:`pyTooling.Graph`

     * Neither module raises its own base exception any more. ``LinkedList`` gained five specific errors and
       ``Graph`` three, so 20 raise sites name what went wrong.

   .. rubric:: Breaking Changes

   * :warning: **The four mixin-classes of :mod:`pyTooling.GenericPath` are renamed to the ``***Mixin`` spelling**
     the rest of the package uses: ``PathMixIn`` |rarr| :class:`~pyTooling.GenericPath.PathMixin`, ``ElementMixIn``
     |rarr| :class:`~pyTooling.GenericPath.ElementMixin`, ``RootMixIn`` |rarr|
     :class:`~pyTooling.GenericPath.RootMixin` and ``SystemMixIn`` |rarr|
     :class:`~pyTooling.GenericPath.SystemMixin`. They were the last four spelled ``MixIn``, and the old names are
     gone rather than kept as aliases - the same rule the renamed exceptions follow.

   * **32 exception classes are renamed to the** ``***Error`` **suffix**, as :pep:`8` asks for. Only
     :exc:`~pyTooling.Exceptions.ToolingException`, the package's own base exception, keeps ``Exception``. The old
     names were briefly kept as aliases and are removed in the same release, so an ``import`` or an ``except``
     clause naming one has to be updated.
   * ``TerminalApplication._PrintHelp`` moved to
     :class:`~pyTooling.Attributes.ArgParse.ArgParseHelperMixin`, which owns the parsers it prints.
   * :func:`~pyTooling.Packaging.DescribePythonPackage` **raises when it can find no description**, instead of
     publishing a package without one. Either pass ``description``, or give the file named by
     ``sourceFileWithVersion`` a module doc-string.
   * The ``description`` parameter of both ``Describe***`` functions moved behind the required parameters, so a
     caller passing it positionally has to name it.

   .. rubric:: Changes

   * **A package's license is stated as an SPDX expression only; no** ``License ::`` **classifier is added.**
     setuptools deprecated them, and the expression was already there - ``license`` has always been filled from
     :attr:`~pyTooling.Licensing.License.SPDXIdentifier`. A classifier passed by the caller is kept, because it is
     their statement, and reported on the console.
   * 339 f-strings that interpolate nothing lost their ``f`` prefix, across 33 modules.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Testing`

     * The markers were collected as testcases themselves. :deco:`~pyTooling.Testing.testsuite` and
       :deco:`~pyTooling.Testing.testcase` are module-level callables whose names start with ``test``, which is
       what pytest's **default** ``python_functions = ["test*"]`` matches - so importing them put two phantom
       testcases into every module that used them. They passed, which is why nothing looked wrong.

   * :mod:`pyTooling.TerminalUI`

     * A message's indentation was recorded and never printed. ``BaseIndent`` and the ``indent`` parameter of every
       ``Write*`` method reached :attr:`~pyTooling.TerminalUI.Line.Indent` and got lost on the way to the terminal.

   * :file:`doc/conf.py` imported :mod:`pyTooling.Packaging` before inserting the repository into ``sys.path``, so
     nine modules were documented from the *installed* package and the rest from the checkout.

   .. rubric:: Documentation

   * The eighteen constructors in :mod:`pyTooling.Attributes` document their parameters. Each carried the same
     sentence describing ``*args``/``**kwargs``, which none of them takes.
   * The four documentation-coverage findings that were real are fixed: :meth:`pyTooling.Tree.Node.__delitem__`,
     both comparison operators of :class:`~pyTooling.Licensing.License`, and ``abstract_new()``.
   * :ref:`SCHEMAS` is a new section, last in *References and Reports*: a page per schema showing its full source
     with a copy button, and offering the file itself for download. The page includes the schema from the package,
     so there is no second copy to drift.
   * A schema is also **drawn**. The :rst:dir:`xsd-graph` directive reads a schema with ``xmlschema`` and renders it
     with ``sphinx.ext.graphviz`` - complex types as records, containment as labelled edges carrying the
     cardinality, and a node for an enumeration. It ships in
     :mod:`pyTooling.Documentation.Sphinx.XSDSchemaGraph` rather than in this project's :file:`doc/_extensions/`, so
     every project drawing a schema has it from the extension it already enables. ``xmlschema`` is imported when
     the directive runs, so it is needed only where a schema is actually drawn.
   * This release history was written, covering every release back to v0.5.0.

   .. rubric:: Unit Tests

   * Five FigLet banners named a module the file has nothing to do with, copied along with the file they were
     copied from.

Version 9.x (2026)
******************

.. topic:: `v9.0.0 - 20.08.2026 <https://github.com/pyTooling/pyTooling/releases/v9.0.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Testing` is a new module: enhanced classes for writing unit tests with Python's
     :mod:`unittest` framework, which pytest runs as well.

     * :class:`~pyTooling.Testing.ApplicationTestcase` starts the installed program the way a user does, so a test
       covers the ``console_scripts`` entry point, the argument parsing and the exit code.
     * :class:`~pyTooling.Testing.Testcase` adds the assertions newer Python versions gained, so a test suite can
       use them whichever interpreter runs it.

   * :mod:`pyTooling.MetaClasses`

     * :deco:`~pyTooling.MetaClasses.abstractclass` marks a class abstract although it has no abstract method.
     * :class:`~pyTooling.MetaClasses.ExtendedType` forwards any further class keyword argument to
       :meth:`~object.__init_subclass__`.

   .. rubric:: Breaking Changes

   * ``TerminalBaseApplication.CheckPythonVersion()`` and its exit code are removed - a package's
     ``python_requires`` metadata makes the check unnecessary.
   * ``pyTooling.Warning.UnhandledWarningException`` is removed, as v9.0.0 was announced to do.
   * 34 base-classes in :mod:`pyTooling.CLIAbstraction` raise :exc:`~pyTooling.MetaClasses.AbstractClassError`
     instead of :exc:`TypeError` when instantiated directly.
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

   .. rubric:: Changes

   * A :deco:`~pyTooling.Decorators.readonly` property hands out the getter's type instead of :class:`~typing.Any`.

   .. rubric:: Documentation

   * Doc-strings for 10 modules, 47 classes, 127 class fields, 109 dunder methods and the methods that had none;
     134 ``:param:``, 89 ``:returns:`` and 27 ``:raises:`` fields filled in.
   * 41 cross-references pointed nowhere and were corrected; neighbouring modules cross-reference each other.
   * New pages: :file:`doc/Testing.rst` and :file:`doc/Dependency.rst`.

   .. rubric:: Unit Tests

   * The whole suite derives from :class:`pyTooling.Testing.Testcase` instead of :class:`unittest.TestCase`.

Version 8.x (2025/2026)
***********************

.. topic:: `v8.19.0 - 31.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.19.0>`__

   .. rubric:: Changes

   * :mod:`pyTooling.Versioning`, :mod:`pyTooling.Attributes`, :mod:`pyTooling.Warning`

     * Ten properties without a setter are marked :deco:`~pyTooling.Decorators.readonly`.

   * :mod:`pyTooling.MetaClasses`

     * :exc:`~pyTooling.MetaClasses.DuplicateFieldInSlotsError` distinguishes its two causes in the notes: a slot
       inherited from a base-class, and a slot contributed by a mixin-class.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Filesystem`

     * ``Element.Path`` raised ``NotImplemented(...)``, which is a singleton rather than an exception class, so it
       raised :exc:`TypeError` instead of :exc:`NotImplementedError`.

   .. rubric:: Documentation

   * All 337 properties in the package carry a doc-string with a ``:returns:`` field. 80 had none and 25 more had
     no ``:returns:``.
   * A property that computes its result reads *"Read-only property to return ..."*, a plain field access keeps
     *"to access"*.
   * Documentation coverage rose from 76.28 % to 80.97 %.

.. topic:: `v8.18.0 - 30.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.18.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Configuration`

     * Added ``KeyNotFoundException``, ``UnsupportedValueTypeException``, ``InterpolationException`` and
       ``PathExpressionException``. All four were renamed to the ``***Error`` suffix in v10.0.0.

   * :mod:`pyTooling.Dependency`

     * Added ``DependencyException`` as the module's base-exception, three specific exceptions and two warnings.

   * :mod:`pyTooling.MetaClasses`

     * :class:`~pyTooling.MetaClasses.ExtendedType` reports every field assigned in a class body without a type
       annotation, and rejects a slot shadowed by a class member.

   * :mod:`pyTooling.Versioning`

     * :class:`~pyTooling.Versioning.CalendarVersion` accepts the same prefixes as
       :class:`~pyTooling.Versioning.SemanticVersion` and carries a third numeric part.

   .. rubric:: Changes

   * :mod:`pyTooling.Decorators`

     * :deco:`~pyTooling.Decorators.readonly` is a class deriving from :class:`property`, and rejects ``.setter``
       and ``.deleter``. A property declared read-only could be made writable further down the class body.

   * :mod:`pyTooling.MetaClasses`

     * A :class:`~typing.ClassVar` without an initial value no longer becomes a slot.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Configuration`

     * A missing key raised :exc:`ValueError` from an unguarded ``int(key)`` conversion; a missing numeric key and
       a ``null`` value raised an exception with an empty message.

   * :mod:`pyTooling.MetaClasses`

     * The non-slots branch of ``_computeSlots`` had no :pep:`649` fallback, so it saw no annotations on
       Python 3.14.

   * :mod:`pyTooling.Versioning`

     * ``YearMonthDayVersion`` dropped the day from ``__str__`` and ``__repr__``.

.. topic:: `v8.17.0 - 20.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.17.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Streaming`

     * Added ``BlockingPut``, ``QueueReader`` and ``Delay``.

   * :mod:`pyTooling.Warning`

     * Added ``SupervisedWarningCollector``, ``ThreadSupervisor`` and their exceptions (beta).

.. topic:: `v8.16.1 - 08.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.16.1>`__

   .. rubric:: Bug Fixes

   * Reverted a wrong dependency upgrade. Same day as v8.16.0, which carries the features below.

.. topic:: `v8.16.0 - 08.07.2026 <https://github.com/pyTooling/pyTooling/releases/v8.16.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.TerminalUI`

     * Added ``TerminalApplication._PrintHelp``.
     * Reworked ``_PrintVersion``: show project, documentation and issue URLs if defined as dunder-variables.
     * Added ``_GetLatestVersion``, showing whether a newer version is available.

.. topic:: `v8.15.0 - 21.06.2026 <https://github.com/pyTooling/pyTooling/releases/v8.15.0>`__

   .. rubric:: New Features

   * Notes can be attached to warnings raised through ``WarningCollector.Raise``.
   * Added read-only properties ``HasNotes`` and ``Notes`` to all exceptions, and the helper function
     ``addNoteWithItemList``.
   * Added ``ProcessInformation`` and ``MemoryInfo`` to report the memory used by the current process.
   * :mod:`pyTooling.TerminalUI`

     * Added the severity levels ``Exception``, ``ExceptionCause``, ``ExceptionNote``, ``CriticalNote``,
       ``WarningNote`` and ``Silent``, and printing of exception and warning notes.

.. topic:: `v8.14.0 - 21.03.2026 <https://github.com/pyTooling/pyTooling/releases/v8.14.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Filesystem`

     * Added method ``IterateDirectories``.

   * ``pyTooling.Filesystem.Docker``

     * Added ``EmptyDirectories``, ``EmptyDirectoryCount`` and ``WriteEmptyDirectoryFile``.

   .. rubric:: Changes

   * ``pyTooling.Filesystem.Docker``

     * ``WriteLayerFiles`` accepts an optional ``fileNamePattern``.

.. topic:: `v8.13.0 - 19.03.2026 <https://github.com/pyTooling/pyTooling/releases/v8.13.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Filesystem`

     * Scanning reports a :exc:`PermissionError` as a warning and registers broken and unresolvable symbolic links
       at ``Root``.
     * Added ``Directory.IterateFiles``, the ``SymbolicLink`` properties ``IsConnected``, ``IsBroken`` and
       ``IsOutOfRange``, and the ``Root`` lists of broken and unconnected symbolic links.

   * ``pyTooling.Filesystem.Docker`` is a new module computing file lists for Docker image layers, with ``Layer``
     and ``LayerCake``.

   .. rubric:: Changes

   * :mod:`pyTooling.Warning`

     * ``WarningCollector.Raise`` accepts an optional ``cause`` parameter.

.. topic:: `v8.12.0 - 07.02.2026 <https://github.com/pyTooling/pyTooling/releases/v8.12.0>`__

   .. rubric:: Changes

   * Removed bootstrap code (contributed by `@gtsiam <https://github.com/gtsiam>`__).

   .. rubric:: Bug Fixes

   * Fixed a buffer overflow exception caused by ``__GetTerminalSizeOnLinux``.

.. topic:: `v8.11.0 - 18.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.11.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Platform`

     * Detect whether the program runs in a CI environment (AppVeyor, GitHub Actions, GitLab CI, Travis CI), with
       the new properties ``IsCI``, ``IsAppVeyor``, ``IsGitHub``, ``IsGitLab`` and ``IsTravisCI``.

.. topic:: `v8.10.0 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.10.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.CLIAbstraction`

     * Added ``Executable.Wait()``.

   .. rubric:: Changes

   * :mod:`pyTooling.CLIAbstraction`

     * Reworked ``Executable.Terminate()`` and ``Executable.ExitCode``.

.. topic:: `v8.9.1 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.9.1>`__

   .. rubric:: Changes

   * Bumped copyright information.

.. topic:: `v8.9.0 - 08.01.2026 <https://github.com/pyTooling/pyTooling/releases/v8.9.0>`__

   .. rubric:: New Features

   * Added pickle support for all classes using the :class:`~pyTooling.MetaClasses.ExtendedType` metaclass with
     slots enabled.
   * :mod:`pyTooling.Tracing` is a new module for software execution tracing: a ``Trace`` is made of ``Span``\ s,
     each with optional ``Event``\ s.
   * :mod:`pyTooling.Dependency` is a new module with a package dependency graph and a resolution algorithm, plus
     a Python specific variant handling PyPI in ``pyTooling.Dependency.Python``.

   .. rubric:: Bug Fixes

   * Fixed the uninitialized field ``_nodesWithoutID`` in :class:`pyTooling.Tree.Node`.

.. topic:: `v8.8.0 - 10.11.2025 <https://github.com/pyTooling/pyTooling/releases/v8.8.0>`__

   .. rubric:: New Features

   * Added support for critical warnings: a warning that is raised and not handled causes an exception.

     * New ``Warning`` and ``CriticalWarning`` classes, and the ``UnhandledCriticalWarningException`` and
       ``UnhandledExceptionException`` exceptions.
     * ``WarningCollector`` supports iteration, length and item indexing.

   .. rubric:: Changes

   * Removed code specific to Python versions before 3.11.

   .. rubric:: Bug Fixes

   * Removed a wrong ``with_traceback`` overload from ``ExceptionBase``, which caused faults in pytest.

.. topic:: `v8.7.6 - 28.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.6>`__

   .. rubric:: New Features

   * Implemented ``__str__`` for :class:`~pyTooling.Packaging.VersionInformation`.

.. topic:: `v8.7.5 - 27.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.5>`__

   .. rubric:: Changes

   * Bumped dependencies.
   * Fixed a missing ``needs`` rule in the pipeline.

.. topic:: `v8.7.4 - 19.10.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.4>`__

   .. rubric:: Changes

   * Added Python 3.14 support to the wheel package, and dropped Python 3.9 and 3.10.

.. topic:: `v8.7.3 - 21.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.3>`__

   .. rubric:: New Features

   * Supports Python 3.14 (tested with 3.14rc2).

   .. rubric:: Changes

   * ``WarningCollector`` uses thread local data, which improves performance and allows nested contexts.

   .. rubric:: Bug Fixes

   * Reworked accessing annotations in the metaclasses due to :pep:`649`.
   * Worked around a packaging problem with :file:`py.typed`.

.. topic:: `v8.7.2 - 04.09.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.2>`__

   .. rubric:: Bug Fixes

   * Accept :exc:`Exception` instances as warnings (from the failed v8.7.1 release).

   .. rubric:: CI Pipeline

   * Disabled Ubuntu ARM images due to instability at GitHub.

.. topic:: `v8.7.0 - 23.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.7.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Versioning`

     * ``VersionRange.LowerBound``, ``.UpperBound`` and ``.BoundHandling`` can be set via property.

   * :mod:`pyTooling.Platform`

     * Added support for Linux AArch64 and Windows AArch64.

   .. rubric:: Changes

   * Removed the experimental ``classproperty`` decorator - support was explicitly revoked by Python.

.. topic:: `v8.6.0 - 12.08.2025 <https://github.com/pyTooling/pyTooling/releases/v8.6.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Versioning`

     * Added the classes :class:`~pyTooling.Versioning.VersionRange` and :class:`~pyTooling.Versioning.VersionSet`.

.. topic:: `v8.5.1 - 14.06.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.1>`__

   .. rubric:: Bug Fixes

   * Fixed the instantiation of ``YearReleaseVersion`` from ``CalendarVersion.Parse``.

.. topic:: `v8.5.0 - 31.05.2025 <https://github.com/pyTooling/pyTooling/releases/v8.5.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Common`

     * New context manager :class:`~pyTooling.Common.ChangeDirectory`.

   * :mod:`pyTooling.TerminalUI`

     * New ``_PrintHeadline`` and ``_PrintVersion`` methods.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Packaging`

     * Fixed the directory (package) excludes: the exclude list is computed with :func:`os.scandir`, and any
       :file:`__init__.py` from a parent namespace is excluded, because such a file breaks namespace packages
       without notice.

.. topic:: `v8.4.0 - 17.04.2025 <https://github.com/pyTooling/pyTooling/releases/v8.4.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.LinkedList` is a new module: construct from an iterable, insert at either end or around a
     node, sort, reverse, iterate in both directions, and convert to a tuple or list.
   * :mod:`pyTooling.Cartesian2D` and :mod:`pyTooling.Cartesian3D` are new modules with the basic classes
     (``Origin``, ``Point``, ``Offset``, ``Size``, ``Segment``, ``LineSegment``) and shapes (``Trapezium``,
     ``Rectangle``, ``Square``; ``Cuboid``, ``Cube``).
   * :mod:`pyTooling.Filesystem` is a new module collecting file system statistics: subdirectories, files and
     symbolic links, multiple filenames per file object (hardlinks), aggregated subdirectory sizes, a user defined
     collapse function, and conversion to a :mod:`pyTooling.Tree`.

.. topic:: `v8.3.0 - 16.03.2025 <https://github.com/pyTooling/pyTooling/releases/v8.3.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Common`

     * New :func:`~pyTooling.Common.count` function counting the elements of an iterator or generator.

   * :mod:`pyTooling.CLIAbstraction`

     * Added ``__setitem__`` and ``__delitem__`` on ``Environment``.

   .. rubric:: Changes

   * :mod:`pyTooling.CLIAbstraction`

     * The initializer of ``Environment`` allows setting additional variables and deleting existing ones.

   .. rubric:: Documentation

   * Added the :mod:`pyTooling.Warning` documentation.

.. topic:: `v8.2.0 - 23.02.2025 <https://github.com/pyTooling/pyTooling/releases/v8.2.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Warning`

     * Added ``WarningCollector`` to handle warnings like exceptions and send them along the call stack.

.. topic:: `v8.1.0 - 25.01.2025 <https://github.com/pyTooling/pyTooling/releases/v8.1.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Graph`

     * Added the methods ``HasVertexByID``, ``HasVertexByValue`` and ``GetVertexByValue``.

   * :mod:`pyTooling.Versioning`

     * Version classes are hashable.
     * Added the ``gamma`` release level.

   * ``pyTooling.Stopwatch``

     * Added the ``Exclude`` context manager.

.. topic:: `v8.0.3 - 17.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.3>`__

   .. rubric:: Changes

   * :func:`~pyTooling.Common.getResourceFile` and :func:`~pyTooling.Common.readResourceFile` are unconditional in
     the package for Python 3.9+.

   .. rubric:: Bug Fixes

   * README files, requirement files, GraphML files and JSON/YAML configurations are opened with UTF-8 encoding.

.. topic:: `v8.0.2 - 12.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.2>`__

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Versioning`

     * Fixed the usage of a variable ``max`` that was unassigned and fell back to the builtin function.

.. topic:: `v8.0.1 - 10.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.1>`__

   .. rubric:: Bug Fixes

   * Fixed the platform name for MSYS2/MinGW32 with Python 3.12.

.. topic:: `v8.0.0 - 09.11.2024 <https://github.com/pyTooling/pyTooling/releases/v8.0.0>`__

   .. rubric:: New Features

   * Reworked the semantic and calendar version classes:

     * Moved the common implementations to the ``Version`` base-type - the major, minor, micro, build, post, dev,
       release level, release number, hash, prefix and postfix parts, and the comparison operators.
     * Implemented the minimum comparison operator using ``__rshift__`` (``>>``) for PIP's ``~=`` operator.
     * Reworked :class:`~pyTooling.Versioning.SemanticVersion`: comparisons with strings and integers,
       and a ``Parse()`` class-method that uses a regular expression and raises on invalid input.
     * Implemented :class:`~pyTooling.Versioning.CalendarVersion`, previously a dummy, including its comparison
       operators and its ``Parse()`` class-method.
     * Added the validator classes ``WordSizeValidator`` and ``MaxValueValidator``.
     * ``__str__()`` returns only the used version parts, and ``__format__()`` accepts a user defined format
       specification.

   .. rubric:: Breaking Changes

   * Renamed ``SemanticVersion.Patch`` to :attr:`~pyTooling.Versioning.SemanticVersion.Micro`. ``Patch`` remains as
     an alias.
   * Moved ``pyTooling.Platform.PythonVersion`` to :class:`pyTooling.Versioning.PythonVersion`.
   * An instance of the internally used ``PythonVersion`` is created with the class-method
     ``PythonVersion.FromSysVersionInfo()``, because its constructor was buggy.

   .. rubric:: Bug Fixes

   * Added support for Python 3.12 on MSYS2 environments (MinGW64, UCRT64, Clang64).

   .. rubric:: Documentation

   * Added doc-strings to all version classes, and improved the versioning and stopwatch pages.

Version 7.x (2024)
******************

.. topic:: `v7.0.0 - 27.10.2024 <https://github.com/pyTooling/pyTooling/releases/v7.0.0>`__

   .. rubric:: New Features

   * Added support for Python 3.13 and dropped 3.8, which changes ``DEFAULT_PY_VERSIONS`` in
     :mod:`pyTooling.Packaging` to 3.9...3.13.
   * :deco:`~pyTooling.Decorators.InheritDocString` can be applied to classes too.

   .. rubric:: Breaking Changes

   * The faulty ``Timer`` class was reworked and renamed: ``pyTooling.Timer.Timer`` is
     ``pyTooling.Stopwatch.Stopwatch``. It supports start, pause, resume, split and stop, collects active and
     inactive split times, accepts a name, takes the absolute time via :meth:`~datetime.datetime.now`, and can be
     used in a ``with``-statement.

Version 6.x (2024)
******************

.. topic:: `v6.7.0 - 29.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.7.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.TerminalUI`

     * Added ``TerminalApplication.WriteCritical()`` and ``TerminalApplication.ExitOnPreviousCriticalWarnings()``.

   .. rubric:: Changes

   * :mod:`pyTooling.Attributes`

     * A ``ValuedFlag`` may be optional.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Platform`

     * Distinguish macOS for Intel (x86-64) from macOS for ARM (aarch64).

.. topic:: `v6.6.2 - 22.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.6.2>`__

   .. rubric:: Bug Fixes

   * Fixed some coding style issues.

.. topic:: `v6.6.1 - 22.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.6.1>`__

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.TerminalUI`

     * ``TerminalBaseApplication.GetTerminalSize``: added the missing check for FreeBSD (provided by
       `@yurivict <https://github.com/yurivict>`__).

   .. rubric:: CI Pipeline

   * Split the pipeline into a main pipeline, a benchmark pipeline and a performance pipeline.

.. topic:: `v6.6.0 - 18.09.2024 <https://github.com/pyTooling/pyTooling/releases/v6.6.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Graph`

     * Key-value-pairs can be set when creating a graph, a vertex, an edge or a link.

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.loadReadmeFile` supports plain text and ReStructured Text.

   * :mod:`pyTooling.Platform`

     * Added :attr:`~pyTooling.Platform.Platform.StaticLibraryExtension`.

   .. rubric:: Breaking Changes

   * :mod:`pyTooling.Platform`

     * Renamed ``Platform.SharedLibraryExtension`` to
       :attr:`~pyTooling.Platform.Platform.DynamicLibraryExtension`.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Packaging`

     * :func:`~pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` created false URLs when a package name
       contained ``.*`` for the root namespace package.

   * :mod:`pyTooling.Platform`

     * Fixed the extension returned by ``SharedLibraryExtension`` for macOS.

.. topic:: `v6.5.1 - 15.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.5.1>`__

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.GenericPath`

     * Fixed the formatting in ``URL.__str__()`` when the URL has no query part.

.. topic:: `v6.5.0 - 15.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.5.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.GenericPath`

     * :class:`pyTooling.GenericPath.URL.URL` supports basic authentication credentials (username and password),
       with a ``WithoutCredentials()`` method.

   .. rubric:: Changes

   * :mod:`pyTooling.GenericPath`

     * Added parameter checks and doc-strings, improved the regular expression validating and parsing a URL, and
       ``URL.Parse()`` raises a :exc:`~pyTooling.Exceptions.ToolingException` when it doesn't match.

   * :mod:`pyTooling.Packaging`

     * Improved the error message of :func:`~pyTooling.Packaging.loadRequirementsFile` when the file isn't found.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.GenericPath`

     * Fixed the regular expression parsing a URL.

.. topic:: `v6.4.0 - 04.07.2024 <https://github.com/pyTooling/pyTooling/releases/v6.4.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Platform`

     * Added the read-only property :attr:`~pyTooling.Platform.Platform.IsNativeFreeBSD`.

   .. rubric:: Breaking Changes

   * :mod:`pyTooling.Platform`

     * Renamed ``Platforms.OS_BSD`` to ``Platforms.OS_FreeBSD``.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Platform`

     * Fixed ``ExecutableExtension``, ``SharedLibraryExtension`` and ``__str__`` for FreeBSD.

.. topic:: `v6.3.0 - 02.06.2024 <https://github.com/pyTooling/pyTooling/releases/v6.3.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Tree`

     * Accept a custom formatting function per node, returning a one-liner representation for tree rendering.
     * Accept a key-value-pair mapping for a node in the initializer.

   * :mod:`pyTooling.Graph`

     * Accept a key-value-pair mapping in the initializer of every data structure - graph, edge, link, vertex,
       view.

   .. rubric:: Changes

   * :mod:`pyTooling.Tree`

     * The default ASCII characters for tree rendering are more compact.

.. topic:: `v6.2.0 - 30.05.2024 <https://github.com/pyTooling/pyTooling/releases/v6.2.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Common`

     * New helper function :func:`~pyTooling.Common.getFullyQualifiedName`.
     * New helper functions :func:`~pyTooling.Common.getResourceFile` and
       :func:`~pyTooling.Common.readResourceFile` (Python 3.8+).
     * A :exc:`TypeError` carries a note describing the parameter or member type (Python 3.11+).

   .. rubric:: Breaking Changes

   * ``CurrentPlatform`` moved from :mod:`pyTooling.Common` to :mod:`pyTooling.Platform`, because of import
     cycles.

   .. rubric:: Bug Fixes

   * Some functions raised a :exc:`TypeError` when ``None`` was passed; they raise a :exc:`ValueError` now.

.. topic:: `v6.1.0 - 09.04.2024 <https://github.com/pyTooling/pyTooling/releases/v6.1.0>`__

   .. rubric:: Breaking Changes

   * :mod:`pyTooling.Versioning`

     * Removed the method overloads, whose semantics were unclear. The
       :class:`~pyTooling.Versioning.SemanticVersion` constructor is split into ``__init__(major, minor, patch=0,
       build=0, flags=Flags.Clean)`` and the ``Parse(versionString)`` class-method.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Attributes`

     * Fixed the search for methods with attributes in multiple inheritance scenarios.

.. topic:: `v6.0.1 - 16.01.2024 <https://github.com/pyTooling/pyTooling/releases/v6.0.1>`__

   .. rubric:: Bug Fixes

   * Implemented the bootstrap feature in all modules.

.. topic:: `v6.0.0 - 14.01.2024 <https://github.com/pyTooling/pyTooling/releases/v6.0.0>`__

   .. rubric:: New Features

   * Integrated the package ``pyAttributes`` v2.5.9 as :mod:`pyTooling.Attributes`.

     * The ``AttributeHelperMixin`` mixin-class is replaced by the meta-class features of
       :class:`~pyTooling.MetaClasses.ExtendedType`.
     * :mod:`pyTooling.Attributes.ArgParse` was completely reworked.

   * Integrated the namespace package :mod:`pyTooling.CLIAbstraction` v0.4.1, to minimize maintenance efforts.
   * :mod:`pyTooling.Common`

     * Implemented :func:`~pyTooling.Common.firstElement` and :func:`~pyTooling.Common.lastElement`, and
       :func:`~pyTooling.Common.firstItem` and :func:`~pyTooling.Common.lastItem`.
     * Added ``bind`` to bind a normal function as a method.

   * :mod:`pyTooling.Platform`

     * Added *Cygwin*.

   * :mod:`pyTooling.TerminalUI`

     * Added support for an issue tracker URL.

   .. rubric:: Breaking Changes

   * Renamed ``SemVersion`` to :class:`~pyTooling.Versioning.SemanticVersion` and ``CalVersion`` to
     :class:`~pyTooling.Versioning.CalendarVersion`.
   * Renamed ``firstItem`` to :func:`~pyTooling.Common.firstPair`.
   * Removed the Python 3.7 code and its workarounds.

   .. rubric:: Changes

   * A read-only property uses the :deco:`~pyTooling.Decorators.readonly` decorator instead of
     :class:`property`.
   * Improved exception printing, exception messages and type hints.

   .. rubric:: Documentation

   * Switched from the BuildTheDocs theme to the ReadTheDocs theme, and added tabs and grids via
     ``sphinx-design`` - a description beside its example code, and tabs to switch between Linux and Windows or
     JSON, YAML and XML.
   * Integrated the documentation of ``pyAttributes`` and of :mod:`pyTooling.CLIAbstraction`.
   * Added the *News* chapter.

Version 5.x (2023)
******************

.. topic:: `v5.0.0 - 02.07.2023 <https://github.com/pyTooling/pyTooling/releases/v5.0.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.MetaClasses`

     * :class:`~pyTooling.MetaClasses.ExtendedType` supports mixin-classes and the delayed creation of slots, and
       generates initializers for annotated fields and annotated class fields, which previously raised because of
       slots (contributed by `@skoehler <https://github.com/skoehler>`__).
     * New exceptions: ``ExtendedTypeError``, ``BaseClassWithoutSlotsError``, ``BaseClassWithNonEmptySlotsError``,
       ``BaseClassIsNotAMixinError`` and :exc:`~pyTooling.MetaClasses.DuplicateFieldInSlotsError`.

   * :mod:`pyTooling.Decorators`

     * Added the decorators :deco:`~pyTooling.MetaClasses.slotted`, :deco:`~pyTooling.MetaClasses.mixin`,
       :deco:`~pyTooling.MetaClasses.singleton`, :deco:`~pyTooling.Decorators.readonly` and
       :deco:`~pyTooling.Decorators.notimplemented`.

   * :mod:`pyTooling.Configuration`

     * Added JSON support.

   * :mod:`pyTooling.Platform`

     * Added ``PythonVersion`` and ``PythonImplementation`` to distinguish Python versions, and CPython from PyPy.

   * :mod:`pyTooling.Graph`

     * Added ``GetVertexByID`` and ``GetVertexByValue``, the vertex operations
       ``IterateAllOutboundPathsAsVertexList``, ``Delete``, ``DeleteEdgeTo``, ``DeleteEdgeFrom``, ``DeleteLinkTo``
       and ``DeleteLinkFrom``, and ``Delete`` on an edge and on a link.

   * ``pyTooling.StateMachine`` is a new package (alpha).

   .. rubric:: Breaking Changes

   * :class:`~pyTooling.MetaClasses.ExtendedType`: renamed ``useSlots`` to ``slots``.
   * Renamed ``ObjectWithSlots`` to ``SlottedObject``, ``SemVersion`` to
     :class:`~pyTooling.Versioning.SemanticVersion` and ``CalVersion`` to
     :class:`~pyTooling.Versioning.CalendarVersion`.
   * Moved ``AbstractClassError`` and ``MustOverrideClassError`` from :mod:`pyTooling.Exceptions` to
     :mod:`pyTooling.MetaClasses`, and the module ``pyTooling.Common.Platform`` to :mod:`pyTooling.Platform`.

   .. rubric:: Changes

   * :class:`~pyTooling.MetaClasses.ExtendedType` supports multiple inheritance and mixins with deferred slots
     (contributed by `@skoehler <https://github.com/skoehler>`__).
   * Improved the performance of :func:`~pyTooling.Common.mergedicts` by 10x, and the error handling in
     :func:`~pyTooling.Common.mergedicts` and :func:`~pyTooling.Common.zipdicts`.

   .. rubric:: Bug Fixes

   * Reworked :class:`~pyTooling.MetaClasses.ExtendedType` for slots in multiple inheritance scenarios, and the
     internal inheritance graphs, which fixes :mod:`pyTooling.Configuration`, ``pyTooling.GraphML`` and
     :mod:`pyTooling.TerminalUI` (contributed by `@skoehler <https://github.com/skoehler>`__).

Version 4.x (2023)
******************

.. topic:: `v4.0.1 - 26.03.2023 <https://github.com/pyTooling/pyTooling/releases/v4.0.1>`__

   .. rubric:: Changes

   * Republished the package to PyPI. Same day as v4.0.0, which carries the changes below.

.. topic:: `v4.0.0 - 26.03.2023 <https://github.com/pyTooling/pyTooling/releases/v4.0.0>`__

   .. rubric:: New Features

   * :mod:`pyTooling.Graph`

     * Graphs support subgraphs, and export them to GraphML: the new classes ``SubGraph``, ``Link`` and ``View``.
     * Added ``Vertex.Link***Vertex`` to link vertices from disjunctive subgraphs, ``Vertex.HasLink***Vertex`` to
       check whether two such vertices are connected, and ``Vertex.Iterate***boundLinks``.
     * Added ``Graph.IterateLinks``, ``Graph.ReverseLinks`` and ``Graph.RemoveLinks``.
     * Added the ``in`` operator for key-value-pairs.

   .. rubric:: Breaking Changes

   * :mod:`pyTooling.Graph`

     * Renamed the ``Link***Vertex`` methods to ``Edge***Vertex`` and the ``HasLink***Vertex`` methods to
       ``HasEdge***Vertex``.
     * Added more generic type variables to the graph classes.
     * Commented out the unimplemented methods, among them ``PathExistsTo``, ``IterateBFS``, ``IterateDFS``,
       ``IterateTopologically`` and ``MinimumSpanningTree``.

   .. rubric:: Bug Fixes

   * :mod:`pyTooling.Graph`

     * Fixed the ``Component`` class and the references to components.

Version 3.x (2023)
******************

.. topic:: `v3.0.0 - 10.03.2023 <https://github.com/pyTooling/pyTooling/releases/v3.0.0>`__

   .. rubric:: New Features

   * A data model for GraphML - graph, node, edge, key, data and subgraph - and a conversion to GraphML XML files
     from pyTooling's graph and tree data structures.
   * Support for FreeBSD in ``Platform``.

   .. rubric:: Breaking Changes

   * Integrated :mod:`pyTooling.TerminalUI` into pyTooling. This is a breaking change, because the two packages
     overlap in one directory.

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
