.. _GLOSSARY:

Glossary
########

.. glossary::

   Abstract Class
     An :wiki:`abstract class <Abstract_type>` is a type that cannot be instantiated directly. An *abstract* class may
     provide no implementation or an incomplete implementation.

     In pyTooling a class is abstract when :ref:`META/ExtendedType` was applied and either of two things holds:

     * it contains at least one :term:`abstract <Abstract Method>` or :term:`mustoverride <Mustoverride Method>`
       method, or
     * it is decorated with :deco:`~pyTooling.MetaClasses.abstractclass` - for a class that has nothing to mark
       abstract and still exists only to be derived from. The marker describes that one class: a derived class is
       concrete again unless it is decorated itself. See :ref:`META/AbstractClass`.

     If an *abstract* class is instantiated, an :exc:`~pyTooling.MetaClasses.AbstractClassError` is raised.

   Abstract Method
     An *abstract* method provides no implementation (no code) and must therefore be
     :term:`overridden <Overriding>` by all derived classes. It is marked with
     :deco:`~pyTooling.MetaClasses.abstractmethod` - see :ref:`META/AbstractMethod`.

     If an *abstract* method is called, a :exc:`NotImplementedError` is raised. If it is not overridden, an
     :exc:`~pyTooling.MetaClasses.AbstractClassError` is raised when the class is instantiated, because the
     :term:`class is abstract <Abstract Class>`.

   Ancestor
     *Ancestors* are all direct and indirect predecessors of a :term:`node` (:term:`parent node <parent>` and parent
     nodes thereof a.k.a. :term:`grandparents <grandparent>`, grand-grandparent, ..., :term:`root` node).

     In a tree, a node has only a single parent per node, thus a list of ancestors is a direct line from current node to
     the root node.

     .. mermaid::
        :caption: Ancestors of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R:::mark1 --> A
          A:::mark2 --> BL & B & BR
          B:::mark2 --> CL & C & CR
          C:::mark2 --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6,font-size:smaller;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee,font-size:smaller;
          classDef mark2 fill:#69f,stroke:#37f,font-size:smaller;

   Annotation
   Type Hint
     An :external+python:term:`annotation` states the type a variable, a parameter or a return value has. Python
     does not check it - a type checker like :program:`mypy` does, and a library may read it.

     pyTooling reads them: :ref:`META/ExtendedType` derives a class' :term:`slots` from its annotated fields, so a
     field is declared once and the slot follows. Since v10.0.0 an annotation is evaluated lazily (:pep:`563`,
     :pep:`649`), so a class may name a type that doesn't exist yet - including itself.

     Wikipedia: :wiki:`Type signature <Type_signature>`

   Base
   Base-Class
     A *base-class* is an ancestor class for other classes derived therefrom by :term:`inheritance`. A class derived
     from more than one has a primary base-class and, usually, one or more :term:`mixin-classes <Mixin>`.

     .. mermaid::
        :caption: Base-class in a class hierarchy.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          B(BaseClass)
          C(Class)
          I1(Instance);I2(Instance)

          B:::mark1 --> C:::mark2 -..-> I1 & I2

          classDef node font-size:smaller;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee,font-size:smaller;
          classDef mark2 fill:#69f,stroke:#37f,font-size:smaller;

   Basic Authentication
     The *basic* scheme of :rfc:`7617` authorizes a request with a user name and a password, base64-encoded in the
     ``Authorization`` header. It says nothing about who may do what, so it belongs behind TLS.

     :class:`~pyTooling.REST.RESTClient` sends a :term:`bearer token` by default; a client of an API expecting the
     basic scheme overrides :meth:`~pyTooling.REST.RESTClient._RequestHeaders` - see :ref:`REST/Deriving`.

     Wikipedia: :wiki:`Basic access authentication <Basic_access_authentication>`

   Bearer Token
     The *bearer* scheme of :rfc:`6750` authorizes a request with a token in the ``Authorization`` header:
     *whoever bears this token may do what it allows*, so the token is the credential and is never sent to another
     host. An OAuth 2.0 flow hands one out.

     It is what :class:`~pyTooling.REST.RESTClient` sends, and why a ``Link`` header pointing outside the API is
     rejected rather than followed.

   Breadth-First
     *Breadth-first* visits a :term:`graph`'s or :term:`tree`'s :term:`nodes <node>` by distance: everything one
     edge away, then everything two edges away. It finds the shortest path in an unweighted graph, because a node
     is reached the first time by the fewest edges.

     :meth:`Vertex.IterateVerticesBFS <pyTooling.Graph.Vertex.IterateVerticesBFS>` walks a graph that way. See
     :term:`depth-first` for the opposite, and :term:`level-order` for what breadth-first is called in a tree.

     Wikipedia: :wiki:`Breadth-first search <Breadth-first_search>`

   Calendar Version
     A *calendar version* numbers a release by the date it was made - ``2026.09`` - rather than by what changed in
     it. It is the scheme a rolling distribution or a dated dataset uses, where "what changed" has no single answer.

     :class:`~pyTooling.Versioning.CalendarVersion` parses one, in the variants
     :ref:`VERSIONING/CalVerVariants` lists. See :term:`semantic version` for the other scheme.

     `calver.org <https://calver.org/>`__

   Child
     *Children* are all direct successors of a :term:`node`.

     .. mermaid::
        :caption: Children of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          EL:::mark2
          E:::mark2
          ER:::mark2
          DR --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   CLIOption
     A *CLI option* is an argument a program **accepts**: it is declared once, as a nested class of a
     :term:`program`, and describes how that argument is spelled on the command line.

     See :ref:`CLIABS/Program` for how options are declared, and :term:`CLIParameter` for the value one is given.

   CLIParameter
     A *CLI parameter* is a :term:`CLIOption` that has been **set**, together with its value. The options a program
     accepts are fixed when its class is written; the parameters are chosen per program instance, and are what
     :meth:`~pyTooling.CLIAbstraction.Program.ToArgumentList` renders.

   Console Script
   Entry Point
     An *entry point* is a name a distribution publishes for something else to find: the group says what kind of
     thing it is, and the name maps to an object in the distribution. A *console script* is the ``console_scripts``
     group - an installer writes an executable for each of its entries.

     :func:`~pyTooling.Packaging.DescribePythonPackage` declares them, and since v10.0.0 for **any** group, not
     only console scripts - see :ref:`PACKAGING/Descriptions/EntryPoints`.

     `Python Packaging User Guide <https://packaging.python.org/en/latest/specifications/entry-points/>`__

   Content-Type
   Media Type
     A *media type* names the format of a body - ``application/json``, ``text/plain`` - and is what the
     ``Content-Type`` header of :rfc:`9110` carries, optionally with parameters like ``; charset=utf-8``. The
     :rfc:`6839` structured syntax suffix says a type *is written in* another one, so ``application/vnd.github+json``
     is JSON.

     :class:`~pyTooling.REST.MediaType` is the enumeration of the types a REST API sends and receives, and
     :meth:`~pyTooling.REST.MediaType.Matches` answers whether a header names one, suffix and parameters included.

     Wikipedia: :wiki:`Media type <Media_type>`

   Context Manager
     A :external+python:term:`context manager` is an object a ``with``-statement enters and leaves, so what has to
     happen afterwards happens even when the block raises.

     :class:`~pyTooling.Stopwatch.Stopwatch` and :class:`~pyTooling.Tracing.Span` are used that way: entering
     starts the measurement and leaving ends it - see :ref:`COMMON/Stopwatch/ContextManager`. A timespan measured
     elsewhere is constructed with its recorded times instead.

   CopyLeft
     :wiki:`Copyleft <Copyleft>` is a licensing principle requiring that derived works are distributed under the same
     license as the original. The `GPL family <https://www.gnu.org/licenses/licenses.html>`__ is the best known
     example.

     It is the reason a dependency's license matters beyond attribution, and why
     :mod:`pyTooling.Licensing` resolves a license to an :wiki:`SPDX <Software_Package_Data_Exchange>` expression
     rather than to a display name.

     Wikipedia: :wiki:`Copyleft <Copyleft>`

   Cygwin
     :wiki:`Cygwin <Cygwin>` is a :wiki:`POSIX <POSIX>`-compatible programming and runtime environment for Windows.

     Which environment Python runs in is what :class:`~pyTooling.Platform.Platform` reports, because a path, an
     executable's name and the shell differ between :term:`native`, Cygwin, :term:`MSYS2` and :term:`WSL`.

   DAG
     A *directed acyclic graph* (DAG) is a :term:`directed graph <DG>` without backward edges and therefore free of
     cycles.

     .. mermaid::
        :caption: A directed acyclic graph.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph LR
          A(A); B(B); C(C); D(D); E(E); F(F); G(G); H(H); I(I); J(J); K(K)

          A --> B & C & D
          B --> E & F
          C --> E & G
          D --> G & F
          E --> H
          F --> H & I
          G --> I
          H --> J & K
          I --> K & J

          classDef node fill:#eee,stroke:#777,font-size:smaller;

   Descriptor
     A :external+python:term:`descriptor` is an object that defines what reading, writing or deleting an attribute
     does - the mechanism behind a :term:`property`, a method, and a :term:`slot <Slots>`.

     It is why :ref:`META/ExtendedType` can turn an annotated field into a slot: the slot is a descriptor on the
     class, and the value lives in the instance's fixed storage rather than in a ``__dict__``.

   Distribution
   sdist
   Wheel
     A *distribution* is a package as it is published and installed - not the importable directory, but the archive
     the index serves. A **wheel** (:pep:`427`) is the built form, installed by unpacking it; an **sdist** is the
     source form, from which a wheel is built first.

     :func:`~pyTooling.Packaging.DescribePythonPackage` describes what goes into both - see :ref:`PACKAGING`.

     `Python Packaging User Guide <https://packaging.python.org/en/latest/discussions/package-formats/>`__

   DG
     A *directed graph* (DG) is a :term:`graph` where all :term:`edges <edge>` have a direction.

     .. mermaid::
        :caption: A directed graph with cycles (one cycle is denoted by dotted edges).

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph LR
          A(A); B(B); C(C); D(D); E(E); F(F) ; G(G); H(H); I(I)

          A -.-> B -.-> E
          G --> F
          A --> C --> G --> H --> D
          D -.-> A
          D & F --> B
          I ---> E -.-> F -.-> D

          classDef node fill:#eee,stroke:#777,font-size:smaller;

   Decorator
     A :external+python:term:`decorator` is a callable applied to a function, method or class with the ``@``
     syntax, returning a replacement for what it was applied to - or the original, when it only records something
     about it.

     pyTooling uses both forms: :func:`~pyTooling.Decorators.export` records a name in its module's ``__all__`` and
     returns the class unchanged, while :func:`~pyTooling.Decorators.readonly` replaces a method with a property.
     :ref:`Attributes <ATTR>` are decorators too.

     Wikipedia: :wiki:`Decorator <Python_syntax_and_semantics#Decorators>`

   Depth-First
     *Depth-first* follows one branch of a :term:`graph` or :term:`tree` to its end before taking the next. It is
     how a tree is usually walked, in :term:`pre-order` or :term:`post-order` depending on when the
     :term:`node` itself is visited.

     :meth:`Vertex.IterateVerticesDFS <pyTooling.Graph.Vertex.IterateVerticesDFS>` walks a graph that way. See
     :term:`breadth-first` for the opposite.

     Wikipedia: :wiki:`Depth-first search <Depth-first_search>`

   Descendant
     *Descendants* are all direct and indirect successors of a :term:`node` (:term:`child nodes <child>` and child
     nodes thereof a.k.a. :term:`grandchild`, grand-grandchildren, ...).

     .. mermaid::
        :caption: Descendants of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          EL:::mark2
          E:::mark2
          ER:::mark2
          DR --> ERN1 & ERN2
          E --> F1 & F2
          F1:::mark2
          F2:::mark2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Edge
     An *edge* is a relation from :term:`vertex` to vertex in a :term:`graph` - :class:`pyTooling.Graph.Edge`, or
     :class:`~pyTooling.Graph.Link` where the relation crosses into another :term:`subgraph <Graph>`.

   Executable
     An *executable* is a :term:`program` that this API can also **run**: :class:`~pyTooling.CLIAbstraction.Executable`
     adds process handling - starting it, sending it lines, reading its output and waiting for its exit code - to the
     command line abstraction a program provides.

   Extra
     An *extra* is an optional feature of a :term:`distribution`, named in the install as
     ``pyTooling[terminal]``, which pulls the requirements that feature needs.

     pyTooling names an extra after the **feature**, not after the dependency it happens to pull, so an extra
     survives a dependency being replaced. :func:`~pyTooling.Packaging.DescribePythonPackage` declares them from
     ``additionalRequirements``.

   Exception
     An :external+python:ref:`exception <exceptions>` is the object a program raises to signal that it cannot continue
     normally, and the mechanism that transfers control to whatever handles it.

     Every exception pyTooling raises derives from :exc:`~pyTooling.Exceptions.ToolingException`, and carries the
     offending value in a :meth:`note <BaseException.add_note>` rather than only in its message.

     Wikipedia: :wiki:`Exception handling <Exception_handling>`

   Generic
   Type Variable
     A `generic <https://typing.python.org/en/latest/spec/generics.html>`__ type is parametrized by another type,
     so one class serves every element type without losing what a type checker knows: a *type variable* stands for
     the type a use fills in.

     :class:`pyTooling.Tree.Node`, :class:`pyTooling.Graph.Graph` and :class:`~pyTooling.LinkedList.LinkedList` are
     generic in several parameters at once - a node's identifier, its value and its dictionary types are separate
     variables, so a tree of one shape doesn't force the other two.

   Graph
     A *graph* is a data structure made of :term:`vertices <vertex>` (nodes) and vertex-vertex relations called
     :term:`edges <edge>`.

     Special forms of graphs are:

     * Graphs with directions: :term:`Directed Graph <DG>`
     * Directed Graphs without Cycles: :term:`Directed Acyclic Graph <DAG>`
     * Directed Acyclic Graph without Side-Edges: :term:`Tree`

     :mod:`pyTooling.Graph` implements one, with :class:`~pyTooling.Graph.Vertex`, :class:`~pyTooling.Graph.Edge`
     and :class:`~pyTooling.Graph.Subgraph`.

     .. mermaid::
        :caption: A directed graph with backward-edges denoted by dotted vertex relations.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph LR
          A(A); B(B); C(C); D(D); E(E); F(F) ; G(G); H(H); I(I)

          A --> B --> E
          G --> F
          A --> C --> G --> H --> D
          D -.-> A
          D & F -.-> B
          I ---> E --> F --> D

          classDef node fill:#eee,stroke:#777,font-size:smaller;

   Grandchild
     *Grandchildren* are direct successors of a node's :term:`children <child>` and therefore indirect successors of
     a :term:`node`.

     .. mermaid::
        :caption: Grandchildren of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR --> ERN1 & ERN2
          E --> F1 & F2
          F1:::mark2
          F2:::mark2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Grandparent
     A *grandparent* is direct predecessor of a node's :term:`parent` and therefore indirect predecessor of a
     :term:`node`.

     .. mermaid::
        :caption: Grandparent of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B:::mark2 --> CL & C & CR
          C --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Hardlink
     A :wiki:`hard link <Hard_link>` is a second directory entry for the **same** file content. Both entries are equal -
     neither is the original - and the file content (BLOB) exists as long as at least one of them does.

     Unlike a :term:`softlink`, a hard link cannot point at a directory, cannot cross a filesystem boundary, and cannot
     dangle.

   HTTP Method
     The *method* of an HTTP request says what to do with the resource its URL names - ``GET``, ``POST``, ``PUT``,
     ``PATCH``, ``DELETE`` - and :rfc:`9110` defines what each means. The standard library's
     :class:`http.HTTPMethod` enumerates them.

     Which method a request uses decides whether it may be repeated: see :term:`idempotency`.

     Wikipedia: :wiki:`HTTP methods <HTTP#Request_methods>`

   Idempotency
     A request is *idempotent* when sending it twice has the same effect as sending it once - :rfc:`9110` calls
     ``GET``, ``PUT`` and ``DELETE`` idempotent, and ``POST`` and ``PATCH`` not.

     It is what decides whether a failing request may be tried again: :class:`~pyTooling.REST.RESTClient` retries
     the first three and sends the other two once, because a ``POST`` whose answer was lost on the way back may
     have created the resource already - see :ref:`REST/Retries`.

     Wikipedia: :wiki:`Idempotence <Idempotence>`

   Inheritance
     :external+python:ref:`Inheritance <tut-inheritance>` derives a class from another, so the derived class has the
     fields and methods of its :term:`base-class` and may add to or replace them.

     pyTooling's :ref:`META/ExtendedType` takes part in it: a derived class' slots are the fields it declares plus the
     ones it inherits, and an :term:`abstract method` stays abstract until a derived class
     :term:`overrides <Overriding>` it.

     Wikipedia: :wiki:`Inheritance <Inheritance_(object-oriented_programming)>`

   Iterator
   Generator
     An :external+python:term:`iterator` yields its elements one at a time, so a caller can stop after the first
     and nothing computes the rest. A :external+python:term:`generator` is the usual way to write one - a function
     with ``yield``.

     pyTooling's traversals are generators: :meth:`Node.IteratePreOrder <pyTooling.Tree.Node.IteratePreOrder>`,
     :meth:`~pyTooling.Tree.Node.IterateLeafs` and their siblings walk a :term:`tree` lazily, which is what makes
     searching a large tree cheap.

   Job
     A *job* is the unit a :term:`pipeline` schedules onto a :term:`runner`: a sequence of :term:`steps <step>`
     running on one machine, with its own result.

     :class:`pyTooling.CI.GitHub.Job` models one - see :ref:`CI/GitHub`. A job produced by a :term:`matrix` is a
     :class:`~pyTooling.CI.GitHub.MatrixJob` and carries the values it was produced for.

   JSON
     The *JavaScript Object Notation* is a text format for structured data, specified by :rfc:`8259` and
     `json.org <https://www.json.org/>`__.

     pyTooling reads it as a configuration format - :ref:`CONFIG/FileFormat/JSON` - and writes a trace as
     :ref:`OTLP/JSON <TRACING/OTLP>`, with the standard library's :external+python:mod:`json` doing the parsing.

     Wikipedia: :wiki:`JSON <JSON>`

   JSON-Schema
     A `JSON Schema <https://json-schema.org/>`__ describes the structure a :term:`JSON` document must have - which
     members exist, of which type, and which are required - and is a JSON document itself.

     It is to JSON what an :term:`XSD` is to :term:`XML`.

   JUnit
     *JUnit XML* is the test report format every CI service reads, although no standard defines it - it grew out of
     the Java testing framework of that name and every writer adds its own dialect.

     pyTooling writes it, and writes its own format beside it, because JUnit XML cannot express two things a marked
     test suite has: suites **nest**, where JUnit flattens them into a dotted ``classname``, and every item carries
     four names rather than one - see :ref:`TESTING/ReportFormat`.

     Wikipedia: :wiki:`JUnit <JUnit>`

   Label
     A *label* is what a :term:`job` asks of the :term:`runner` it wants - an operating system, an architecture, a
     capability - and what a self-hosted runner is registered with. A service picks a runner whose labels cover the
     job's.

     :attr:`Job.Labels <pyTooling.CI.GitHub.Job.Labels>` reports them.

   Leaf
     A *leaf* is a :term:`node` of a :term:`tree` that has no :term:`children <child>` - the other end of the tree
     from its :term:`root`.

     :attr:`Node.IsLeaf <pyTooling.Tree.Node.IsLeaf>` asks whether a node is one, and
     :meth:`~pyTooling.Tree.Node.IterateLeafs` yields every leaf below a node.

   Level-Order
     *Level-order* visits a :term:`tree`'s :term:`nodes <node>` level by level: the :term:`root`, then its
     :term:`children <child>`, then their children. It is :term:`breadth-first` applied to a tree.

     :meth:`Node.IterateLevelOrder <pyTooling.Tree.Node.IterateLevelOrder>` walks a tree that way. See
     :term:`pre-order` and :term:`post-order` for the two depth-first orders.

     Wikipedia: :wiki:`Level order <Tree_traversal#Breadth-first_search_/_level_order>`

   License Expression
     A *license expression* states how a work is licensed when one identifier can't: ``Apache-2.0 OR MIT`` offers a
     choice, ``GPL-2.0-only WITH Classpath-exception-2.0`` names an exception. :term:`SPDX` defines the syntax.

     :mod:`pyTooling.Licensing` models one as a **tree** - :class:`~pyTooling.Licensing.SPDXLicense` with
     :class:`~pyTooling.Licensing.AndOperator`, :class:`~pyTooling.Licensing.OrOperator`,
     :class:`~pyTooling.Licensing.WithOperator` and :class:`~pyTooling.Licensing.OrLaterOperator` - so the licenses
     in an expression are one comprehension away. See :ref:`LICENSING`.

   Matrix
     A *matrix* is a :term:`job` written once and run several times, once per combination of the values it is
     given - three Python versions on two operating systems are six jobs.

     :class:`pyTooling.CI.GitHub.Matrix` groups the instances a matrix produced, and each
     :class:`~pyTooling.CI.GitHub.MatrixJob` carries the values it was produced for. GitHub reports no matrix as
     such - the instances are recognized by the bracketed values in a job's name - see :ref:`CI/GitHub/Strings`.

   Meta-Class
     A *meta-class* is a class helping to construct classes. Thus, it's the type of a type - the default one is
     :external+python:class:`type`.

     pyTooling's is :class:`~pyTooling.MetaClasses.ExtendedType`, which derives :term:`slots` from a class' annotated
     fields and implements the :term:`abstract class`, :term:`mixin` and :term:`singleton` behaviour this glossary
     describes - see :ref:`META`.

     .. mermaid::
        :caption: Relation of meta-classes, classes and instances.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          T(type)
          ET(MetaClass)
          B(BaseClass)
          M(Mixin)
          C(Class)
          I1(Instance);I2(Instance)

          T --> T
          T:::mark1 --> ET:::mark1 -.class definition.-> B
          B:::mark2 --inheritance--> C:::mark2 -.instantiation..-> I1 & I2
          M --inheritance--> C

          classDef node font-size:smaller;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee,font-size:smaller;
          classDef mark2 fill:#69f,stroke:#37f,font-size:smaller;

   MinGW
     *Minimalist GNU for Windows* is a toolchain building native Windows programs with the GNU compilers. The
     maintained fork is `MinGW-w64 <https://www.mingw-w64.org/>`__, which :term:`MSYS2` ships as one of its
     environments - beside the :term:`UCRT` one - and which :class:`~pyTooling.Platform.Platform` tells apart.

     Wikipedia: :wiki:`MinGW <Mingw-w64>`

   Mixin
   Mixin-Class
     A *mixin class* is a class used as a secondary base-class in multiple inheritance. It contributes fields and
     methods to the class mixing it in, and is not meant to be instantiated on its own.

     pyTooling writes one with :class:`~pyTooling.MetaClasses.ExtendedType` and the ``mixin`` class keyword argument,
     which lets the mixin-class declare fields although it is not the primary base-class:

     .. code-block:: Python

        class ReportMixin(metaclass=ExtendedType, mixin=True, expects=("_counter", "Write")):
          def Report(self) -> bool:
            return self.Write(f"{self._counter}")

     ``expects`` is the other half: a mixin-class contributing methods usually needs fields or methods *from* the
     class mixing it in, and naming them makes the combined class refuse to be instantiated when one is missing -
     see :ref:`META/ExpectedMembers`.

     A class deriving from a mixin-class rather than declaring the meta-class itself is marked with
     :deco:`~pyTooling.MetaClasses.mixin`, so a class that is only ever a secondary base-class says so.

   MRO
     The *method resolution order* is the sequence Python searches a class' bases in, which decides which
     implementation an inherited name resolves to. It is computed once per class (the C3 linearization) and read
     from :attr:`~type.__mro__`.

     It is what makes :term:`multiple inheritance` predictable: a :term:`mixin` listed before a base-class wins,
     and a ``super()`` call follows the order rather than the class it is written in.

     Wikipedia: :wiki:`C3 linearization <C3_linearization>`

   MSYS2
     `MSYS2 <https://www.msys2.org/>`__ is a software distribution and building platform for Windows, providing a
     Unix-like shell, a package manager (``pacman``) and several toolchains - among them :term:`MinGW` and
     :term:`UCRT` - each of which is a separate environment with its own Python.

     Which environment a program runs in is what :class:`pyTooling.Platform.Platform` reports, because a path or an
     executable's name differs between them.

     Wikipedia: :wiki:`MSYS2 <Mingw-w64#MSYS2>`

   Multiple Inheritance
     :external+python:ref:`Multiple inheritance <tut-multiple>` derives a class from more than one base-class. The
     first is the primary base-class; the others usually contribute behaviour rather than identity - a
     :term:`mixin-class`.

     pyTooling's :ref:`META/ExtendedType` is what makes it work with :term:`slots`: a mixin-class marked
     ``mixin=True`` may declare fields although it is not the primary base-class, and they become slots of whichever
     class mixes it in.

     Wikipedia: :wiki:`Multiple inheritance <Multiple_inheritance>`

   Mustoverride Method
     A *must-override* method provides a partial implementation (incomplete code) and must therefore be fully
     implemented by all derived classes. It is marked with :deco:`~pyTooling.MetaClasses.mustoverride`, and unlike an
     :term:`abstract method` its implementation can be called through :external+python:class:`super` - see
     :ref:`META/MustOverwrite`.

     If a *must-override* method is not overridden, an exception is raised when the class is instantiated, because
     the :term:`class is abstract <Abstract Class>`.

   Namespace Package
     A :external+python:term:`namespace package` is a package whose parts may come from several distributions,
     because it has no ``__init__.py`` of its own: importing it merges what every distribution contributes.

     **pyTooling is one.** There is no :file:`pyTooling/__init__.py`, which is why the package's ``__version__``
     lives in :mod:`pyTooling.Common` - named as the ``packageInformationFile`` in :file:`setup.py` - and why
     another distribution could add a :samp:`pyTooling.{Something}` of its own.

   Native
     A *native environment* is a platform just with the operating system. There is no additional environment layer
     like :term:`MSYS2`, :term:`Cygwin` or :term:`WSL`, which is what
     :attr:`Platform.IsNativePlatform <pyTooling.Platform.Platform.IsNativePlatform>` reports.

   Node
     A *node* is one element of a :term:`tree` or a :term:`graph`, holding a value and its relations to other nodes.

     In a tree a node has at most one :term:`parent` - :class:`pyTooling.Tree.Node`; in a graph it is called a
     :term:`vertex` and is connected by :term:`edges <edge>`.

   Nullable
     ``Nullable[T]`` is how pyTooling spells :external+python:data:`typing.Optional`: every module imports it as
     ``from typing import Optional as Nullable``, and every signature uses that spelling.

     It says the value may be ``None`` - nothing more. Whether a parameter is *optional* is decided by its default,
     not by its annotation: a ``Nullable[...]`` parameter without a default is required and may be given ``None``.

   OpenTelemetry
   OTLP
     `OpenTelemetry <https://opentelemetry.io/>`__ is the vendor-neutral standard for traces, metrics and logs, and
     **OTLP** is its protocol. Its JSON encoding is one document every usual destination reads: a collector accepts
     it natively, and Jaeger imports it.

     A :term:`trace` exports itself that way - :meth:`Trace.ToJSON <pyTooling.Tracing.Trace.ToJSON>` and
     :meth:`~pyTooling.Tracing.Trace.WriteJSONFile`, see :ref:`TRACING/OTLP`. pyTooling exports every
     :term:`span` as kind ``INTERNAL``, so the trace follows the conventions' *attributes*, not their span kinds.

     Wikipedia: :wiki:`OpenTelemetry <OpenTelemetry>`

   Overloading
     :wiki:`Overloading <Function_overloading>` is providing several implementations of one name, chosen by the
     arguments they are called with.

     Python has no overloading: a second ``def`` of a name replaces the first. What it has is
     :func:`~typing.overload`, which declares the accepted signatures for a type checker while a single
     implementation dispatches on them itself.

   Overriding
     :wiki:`Overriding <Method_overriding>` replaces a method inherited from a :term:`base-class` with another
     implementation of the same name. Python needs no keyword for it - a ``def`` in the derived class shadows the
     inherited one, and :external+python:class:`super` reaches the replaced implementation.

     pyTooling makes the *obligation* explicit where there is one: an :term:`abstract method` has no implementation
     and must be overridden, a :term:`mustoverride method` has a partial one that must be, and both are checked when
     the class is instantiated - see :ref:`META/AbstractMethod` and :ref:`META/MustOverwrite`.

     Not to be confused with :term:`overloading`, which is several implementations of one name in *one* class.

   Parent
     A *parent* is direct predecessor of a :term:`node`.

     .. mermaid::
        :caption: Parent of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C:::mark2 --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Path
   Path Flavour
     A *path* names a place in a hierarchy as a sequence of elements, not as a string: :mod:`pyTooling.GenericPath`
     holds the elements, and a **flavour** says what the hierarchy looks like - its ``ELEMENT_DELIMITER``,
     its ``ROOT_DELIMITER`` and the ``ELEMENT_TYPE`` its elements have.

     :class:`pyTooling.GenericPath.URL.Path` is the flavour of a :term:`URL`. Composing with ``/`` and removing a
     trailing delimiter are the flavour-independent part, so a new flavour states its three declarations and
     inherits the rest.

     .. note::

        A path that starts at the root is *absolute*, and one that starts where it is read is *relative* - in the
        path sense, which is not this glossary's :term:`relative`, a sibling's descendant in a tree.

   Pipeline
     A *pipeline* is one run of a CI service's automation for one commit: the :term:`jobs <job>` it schedules, the
     :term:`steps <step>` they run, and the result they produce together.

     :class:`pyTooling.CI.GitHub.Pipeline` models a GitHub Actions workflow run as one - with
     :term:`called workflows <workflow>`, :term:`matrices <matrix>`, jobs and steps below it, each knowing its
     parent. See :ref:`CI/GitHub`.

   Post-Order
     :wiki:`Post-order <Tree_traversal#Post-order,_LRN>` is a depth-first traversal of a :term:`tree` visiting a
     :term:`node` **after** its children.

     It is the order to use when a node's result depends on its children's - computing a size, or deleting a subtree.

     See :term:`Pre-Order` for the opposite.

   Pre-Order
     :wiki:`Pre-order <Tree_traversal#Pre-order,_NLR>` is a depth-first traversal of a :term:`tree` visiting a
     :term:`node` **before** its children.

     It is the order to use when a child's handling depends on its parent's - rendering an indented outline, or
     resolving a path from the :term:`root` down.

     See :term:`Post-Order` for the opposite.

   Program
     A *program* is an executable command line application, abstracted as a Python class by
     :class:`~pyTooling.CLIAbstraction.Program`: its name per operating system, and the arguments it accepts as
     :term:`CLI options <CLIOption>`.

     A program only assembles a command line, whereas an :term:`executable` also runs it.

   Property
   Read-only Property
     A :external+python:class:`property` is an attribute computed by a method: reading it calls a getter, and
     assigning it calls a setter - or fails, if there is none.

     pyTooling writes a **read-only property** with :deco:`~pyTooling.Decorators.readonly`, which is a property
     with a getter and nothing else, and which hands out the getter's type rather than :class:`~typing.Any` - see
     :ref:`DECO/readonly`. Assignment behaviour is documented on the getter, because that is the doc-string Sphinx
     renders.

   PyPI
     The `Python Package Index <https://pypi.org/>`__ is the public repository :program:`pip` installs from by
     default.

     It is also what the :rst:dir:`dependency-table` directive queries to resolve a dependency's version and license.

     Wikipedia: :wiki:`Python Package Index <Python_Package_Index>`

   PyPy
     `PyPy <https://pypy.org/>`__ is an alternative Python implementation with a just-in-time compiler, generally
     faster than
     CPython for long-running pure-Python code and slower for anything dominated by C extensions.

     pyTooling's pipelines test against it, which is why the code avoids assuming CPython's reference-counting
     behaviour - an object is not necessarily collected the moment its last name goes away.

     Wikipedia: :wiki:`PyPy <PyPy>`

   Relative
     *Relatives* are :term:`siblings <sibling>` and their :term:`descendants <descendant>`.

     Left relatives are left siblings and all their descendants, whereas right relatives are right siblings and all
     their descendants.

     .. mermaid::
        :caption: Relatives of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL:::mark2 --> ELN1 & ELN2
          ELN1:::mark2
          ELN2:::mark2
          D:::cur --> EL & E & ER
          DR:::mark2 --> ERN1 & ERN2
          ERN1:::mark2
          ERN2:::mark2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Requirement
   Requirements File
     A *requirement* is a distribution another one needs, with the versions it accepts - ``pyTooling ~= 8.19`` -
     and optionally an environment marker saying when it applies at all. A *requirements file* lists them, and may
     include another with ``-r``.

     :class:`~pyTooling.Dependency.Python.RequirementsFile` reads such a file as a **tree**: every file knows its
     parent, its root and the chain between, ``AllRequirements`` yields them in the order the files state them
     with the nearer statement winning, and a cycle raises rather than being read twice. See
     :ref:`DEPENDENCIES/Python`.

   REST
   REST-API
     *Representational State Transfer* is an architectural style for web APIs: a resource is addressed by a
     :term:`URL`, and the HTTP method says what to do with it - read it, create it, replace it, delete it. It is
     described in `chapter 5 of Roy Fielding's dissertation
     <https://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm>`__ rather than by a standard, so what
     an API calls REST varies.

     A REST API usually answers in :term:`JSON`. :mod:`pyTooling.CI.GitHub` reads the payloads GitHub's REST API
     answers with for a workflow run.

     Wikipedia: :wiki:`REST <REST>`

   Root
     All :term:`nodes <node>` in a :term:`tree` have one common :term:`ancestor` called *root*.

     .. mermaid::
        :caption: Root of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R:::mark1 --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee;

   Runner
   Runner Group
     A *runner* is the machine a :term:`job` runs on - hosted by the service or self-hosted - and a *runner group*
     is how several of them are administered together, with who may use them.

     :attr:`Job.RunnerName <pyTooling.CI.GitHub.Job.RunnerName>` and
     :attr:`~pyTooling.CI.GitHub.Job.RunnerGroupName` report which one a job ran on; the :term:`labels <label>` it
     asked for say what it wanted.

   Schema
     A *schema* is a formal description of the structure a document must have, written in a language of its own, so
     that a document can be checked against it instead of by reading it. :term:`XSD` is one for :term:`XML`,
     :term:`JSON-Schema` one for :term:`JSON`.

     pyTooling publishes the schemas of the file formats it writes - see :ref:`SCHEMAS` - so a consumer of such a
     file can validate it without owning pyTooling.

   Schema Validation
     *Schema validation* checks a document against its :term:`schema` and reports where the document deviates - a
     missing element, an attribute of the wrong type, children in the wrong order.

     A file pyTooling writes names its schema, so validating it is one command:

     .. code-block:: Bash

        xmllint --schema TestReport-v0.1.xsd --noout TestReport.xml

   Semantic Version
     A `semantic version <https://semver.org/>`__ numbers a release by what changed in it: ``major.minor.patch``,
     where the major part is raised for a breaking change, the minor for a compatible feature and the patch for a
     fix. A consumer can therefore state what it accepts.

     :class:`~pyTooling.Versioning.SemanticVersion` parses one, in the variants :ref:`VERSIONING/SemVerVariants`
     lists, and :term:`version range` states what a requirement accepts. See :term:`calendar version` for the
     other scheme.

     Wikipedia: :wiki:`Software versioning <Software_versioning#Semantic_versioning>`

   Sentinel
     A *sentinel* is a value that stands for "nothing to say here" where ``None`` is a legitimate value, or where
     the real value can't be written yet.

     :class:`~pyTooling.MetaClasses.ThisClass` is one: a class variable holding the class declaring it can't be
     written in the class body, because the class doesn't exist while its body runs, so the sentinel stands in it
     and :ref:`META/ExtendedType` replaces it with the finished class.

   Sibling
     *Siblings* are all direct :term:`child nodes <child>` of a node's :term:`parent` node except itself.

     .. mermaid::
        :caption: Siblings of the current node are marked in blue.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          R(Root)
          A(...)
          BL(Node); B(GrandParent); BR(Node)
          CL(Uncle); C(Parent); CR(Aunt)
          DL(Sibling); D(Node);  DR(Sibling)
          ELN1(Niece); ELN2(Nephew)
          EL(Child);   E(Child); ER(Child);
          ERN1(Niece);ERN2(Nephew)
          F1(GrandChild); F2(GrandChild)

          R --> A
          A --> BL & B & BR
          B --> CL & C & CR
          C --> DL & D & DR
          DL:::mark2 --> ELN1 & ELN2
          D:::cur --> EL & E & ER
          DR:::mark2 --> ERN1 & ERN2
          E --> F1 & F2

          classDef node fill:#eee,stroke:#777,font-size:smaller;
          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Singleton
     The :wiki:`singleton design pattern <Singleton_pattern>` ensures only a single instance of a class to exist. If
     another instance is going to be created, a previously cached instance of that class will be returned.

     pyTooling writes one with :class:`~pyTooling.MetaClasses.ExtendedType` and ``singleton=True``, or with the
     :deco:`~pyTooling.MetaClasses.singleton` decorator - see :ref:`META/Singleton`.

   Slots
     :external+python:ref:`__slots__ <slots>` fixes the set of instance attributes a class allows, so instances need
     no ``__dict__``.
     That saves memory per instance and turns a **typo into an error** instead of a new attribute.

     pyTooling's :ref:`META/ExtendedType` meta-class derives the slots from the class' annotated fields, so a class
     gets them by declaring its fields rather than by repeating their names.

   Softlink
   Symbolic Link
   Symlink
     A :wiki:`symbolic link <Symbolic_link>` is a file whose content is a **path** to another file or directory.

     Unlike a :term:`hardlink` it may point at a directory, may cross filesystems, and may *dangle* - the target can be
     removed or never have existed, which is why following one is an operation that can fail.

   Span
     A *span* is one timespan of a :term:`trace`: when it began, when it ended, what it is called, and the
     attributes it carries. Spans nest, so a span holds the spans of whatever ran inside it.

     :class:`pyTooling.Tracing.Span` is one. A span is timed by the ``with``-statement that enters and leaves it,
     or constructed with times recorded elsewhere - see :ref:`TRACING/Recorded`.

   SPDX
     The `System Package Data Exchange <https://spdx.dev/>`__ is the standard for stating what a work is licensed
     under: an identifier per license (``Apache-2.0``, ``MIT-0``), an exception list, and a syntax for combining
     them - a :term:`license expression`.

     :mod:`pyTooling.Licensing` is built on it: ``SPDX_INDEX`` maps every identifier it knows to a
     :class:`~pyTooling.Licensing.License`, and a package's license is published as an expression rather than as a
     classifier. See :ref:`LICENSING`.

     Wikipedia: :wiki:`SPDX <Software_Package_Data_Exchange>`

   Step
     A *step* is one command or action of a :term:`job`, run in the job's order on the job's :term:`runner`, with
     its own result.

     :class:`pyTooling.CI.GitHub.Step` models one. A step that never started has no timing to report.

   Subgraph
     A *subgraph* is a part of a :term:`graph` handled as a unit - a cluster the drawing keeps together, or a
     component the algorithm walks on its own.

     :class:`pyTooling.Graph.Subgraph` is one, and it is the difference between the two relations a graph has: an
     :class:`~pyTooling.Graph.Edge` stays inside a graph, while a :class:`~pyTooling.Graph.Link` crosses from one
     subgraph into another.

     Wikipedia: :wiki:`Glossary of graph theory: subgraph <Glossary_of_graph_theory#subgraph>`

   Test Suite
   Testcase
   Marker
     A *testcase* is one test - one thing that either holds or doesn't - and a *test suite* groups testcases and
     further suites, so a run is a tree rather than a list.

     pyTooling *marks* them instead of naming them: :deco:`~pyTooling.Testing.testsuite` and
     :deco:`~pyTooling.Testing.testcase` are the **markers**, and they carry the title a report shows, which
     frees the class' and method's names from having to read as prose. See :ref:`TESTING/Markers`.

   Trace
     A *trace* is the record of one execution: a tree of :term:`spans <span>` with their times, and the attributes
     describing what each of them was.

     :class:`pyTooling.Tracing.Trace` is the root span of such a tree, and exports itself as :term:`OTLP` JSON -
     see :ref:`TRACING`.

     Wikipedia: :wiki:`Tracing <Tracing_(software)>`

   TOML
     *Tom's Obvious, Minimal Language* is a text format for configuration files, specified at
     `toml.io <https://toml.io/>`__. It is what :file:`pyproject.toml` is written in, and the standard library reads
     it with :external+python:mod:`tomllib`.

     As a pyTooling configuration format it is :ref:`planned <CONFIG/FileFormat/TOML>`.

     Wikipedia: :wiki:`TOML <TOML>`

   Tree
     A *tree* is a data structure made of :term:`nodes <node>` and parent-child relations. All nodes in a tree share
     one common :term:`ancestor` called :term:`root`.

     A tree is a special form of a :term:`directed acyclic graph (DAG) <DAG>`.

     :mod:`pyTooling.Tree` implements one, and the family words this glossary defines - :term:`ancestor`,
     :term:`descendant`, :term:`sibling`, :term:`relative` - are the names of its iterators and properties.

   UCRT
     The *Universal C Runtime* is the C runtime library Windows ships itself, so a program linked against it needs
     no runtime of its own. It is the newer of the two :term:`MSYS2` toolchains - ``UCRT64`` beside the
     :term:`MinGW` one - and :class:`~pyTooling.Platform.Platform` reports which of them Python runs in.

     Wikipedia: :wiki:`Microsoft Windows library files: UCRT <Microsoft_Windows_library_files#UCRT>`

   URI
     A *Uniform Resource Identifier* names a resource, and is specified by :rfc:`3986`. It is the general form: a
     :term:`URL` is a URI that says **where** the resource is, a :term:`URN` one that says **what** it is without
     saying where.

     Wikipedia: :wiki:`Uniform Resource Identifier <Uniform_Resource_Identifier>`

   URL
     A *Uniform Resource Locator* is a :term:`URI` that says where a resource is: a scheme, an authority - host,
     port and optionally user and password -, a path, a query and a fragment, as :rfc:`3986` writes them.

     :class:`~pyTooling.GenericPath.URL.URL` parses one, composes it with a resource below it using the ``/``
     operator, and reports what it rejects as a :exc:`~pyTooling.GenericPath.URL.URLError`. Its path is a path
     flavour of :mod:`pyTooling.GenericPath`, so it is a sequence of elements rather than a string.

     Wikipedia: :wiki:`Uniform Resource Locator <URL>`

   URN
     A *Uniform Resource Name* is a :term:`URI` in the ``urn:`` scheme, specified by :rfc:`8141`. It names a
     resource persistently without saying where to get it - ``urn:isbn:0451450523`` is a book, not a download.

     Wikipedia: :wiki:`Uniform Resource Name <Uniform_Resource_Name>`

   Version Range
     A *version range* states which versions a requirement accepts - ``>=1.2.0,<2.0.0`` - as a set with a lower
     and an upper bound, either of which may be open or absent.

     :class:`~pyTooling.Versioning.VersionRange` is one, and a version expression is what a requirements file
     writes, in the four dialects :ref:`VERSIONING/VersionRange` describes. An intersection keeps both operands'
     bound handling, so an excluded bound stays excluded.

   Vertex
     A *vertex* is a :term:`node` in a :term:`graph` - :class:`pyTooling.Graph.Vertex`. Vertices in a graph are
     connected using :term:`edges <edge>`.

   Workflow
     A *workflow* is an automation file a CI service runs - and, below a :term:`pipeline`, a **called** workflow:
     one workflow started by another, whose :term:`jobs <job>` belong to the caller's run.

     :class:`pyTooling.CI.GitHub.Workflow` groups them, nested as deeply as they are called. GitHub reports no
     nesting as such - a called workflow is recognized by the ``Caller / Job`` shape of a job's name, see
     :ref:`CI/GitHub/Strings`.

   WSL
     The *Windows Subsystem for Linux* runs a Linux distribution on Windows. Python running in it **is** Python on
     Linux - :class:`~pyTooling.Platform.Platform` reports Linux, and says it is WSL beside it, because the file
     system and the executables around it are the host's.

     Wikipedia: :wiki:`Windows Subsystem for Linux <Windows_Subsystem_for_Linux>`

   XML
     The *Extensible Markup Language* is a text format for structured data, specified by the W3C's
     `XML recommendation <https://www.w3.org/TR/xml/>`__.

     :mod:`pyTooling.Testing.ReportWriter` writes a test report as one nested XML document, and the
     :term:`XSD <XML-Schema>` describing it is shipped with pyTooling. As a configuration format XML is
     :ref:`planned <CONFIG/FileFormat/XML>`.

     Wikipedia: :wiki:`XML <XML>`

   XML-Schema
   XSD
     An *XML Schema Definition* describes the structure an :term:`XML` document must have - the elements, their
     attributes and their order - and is an XML document itself. It is specified by the W3C's
     `XML Schema <https://www.w3.org/XML/Schema>`__.

     pyTooling publishes one per file format it writes, each rendered with its types drawn as a graph - see
     :ref:`SCHEMAS`.

     Wikipedia: :wiki:`XML Schema <XML_Schema_(W3C)>`

   YAML
     *YAML Ain't Markup Language* is an indentation-based text format for structured data, specified at
     `yaml.org <https://yaml.org/spec/>`__.

     pyTooling reads it as a configuration format - :ref:`CONFIG/FileFormat/YAML`.

     Wikipedia: :wiki:`YAML <YAML>`

