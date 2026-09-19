.. _GLOSSARY:

Glossary
########

.. glossary::

   Abstract Class
     A :wiki:`abstract class <Abstract_type>` is a type, that cannot be instantiated directly. An *abstract* class may
     provide no implementation or an incomplete implementation.

     In pyTooling such a type is assumed, when a class contains at least one :term:`abstract <Abstract Method>` or
     :term:`mustoverride <Mustoverride Method>` method and pyToolings meta-class :ref:`META/ExtendedType` was applied.

     If an *abstract* class is instantiated, an exception is raised.

   Abstract Method
     An *abstract* method provides no implementation (no code) and must therefore be implemented by all derived classes.

     If an *abstract* method is called, an exception is raised. Also if, an *abstract* method is not overridden, an
     exception is raised when instantiating the class, because the :term:`class is abstract <Abstract Class>`.

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

   Base
   Base-Class
     A *base-class* is an ancestor class for other classes derived therefrom.

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

   DAG
     A *directed acyclic graph* (DAG) is a :term:`directed graph <DG>` without backward edges and therefore free of cycles.

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
     An *edge* is a relation from :term:`vertex` to vertex in a :term:`graph`.

   Executable
     An *executable* is a :term:`program` that this API can also **run**: :class:`~pyTooling.CLIAbstraction.Executable`
     adds process handling - starting it, sending it lines, reading its output and waiting for its exit code - to the
     command line abstraction a program provides.

   Exception
     An :external+python:ref:`exception <exceptions>` is the object a program raises to signal that it cannot continue
     normally, and the mechanism that transfers control to whatever handles it.

     Every exception pyTooling raises derives from :exc:`~pyTooling.Exceptions.ToolingException`, and carries the
     offending value in a :meth:`note <BaseException.add_note>` rather than only in its message.

     Wikipedia: :wiki:`Exception handling <Exception_handling>`

   Graph
     A *graph* is a data structure made of :term:`vertices <vertex>` (nodes) and vertex-vertex relations called
     :term:`edges <edge>`.

     Special forms of graphs are:

     * Graphs with directions: :term:`Directed Graph <DG>`
     * Directed Graphs without Cycles: :term:`Directed Acyclic Graph <DAG>`
     * Directed Acyclic Graph without Side-Edges: :term:`Tree`

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
     *Grandchildren* are direct successors of a node's :term:`children <child>` and therefore indirect successors of a
    :term:`node`.

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

   Inheritance
     :external+python:ref:`Inheritance <tut-inheritance>` derives a class from another, so the derived class has the
     fields and methods of its :term:`base-class` and may add to or replace them.

     pyTooling's :ref:`META/ExtendedType` takes part in it: a derived class' slots are the fields it declares plus the
     ones it inherits, and an :term:`abstract method` stays abstract until a derived class
     :term:`overrides <Overriding>` it.

     Wikipedia: :wiki:`Inheritance <Inheritance_(object-oriented_programming)>`

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

   Meta-Class
     A *meta-class* is a class helping to construct classes. Thus, it's the type of a type.

     .. mermaid::
        :caption: Relation of meta-classes, classes and instances.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          T(type)
          ET(MetaClass)
          B(BaseClass)
          M(MixIn)
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
     Minimalistic GNU for Windows.

     Wikipedia: :wiki:`MinGW <Mingw-w64>`

   Mixin-Class
   Mixin
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
     implemented by all derived classes.

     If a *must-override* method is not overridden, an exception is raised when instantiating the class, because the
     :term:`class is abstract <Abstract Class>`.

   native
     A *native environment* is a platform just with the operating system. There is no additional environment layer like
     MSYS2.

   Node
     A *node* is one element of a :term:`tree` or a :term:`graph`, holding a value and its relations to other nodes.

     In a tree a node has at most one :term:`parent`; in a graph it is called a :term:`vertex` and is connected by
     :term:`edges <edge>`.

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

   TOML
     *Tom's Obvious, Minimal Language* is a text format for configuration files, specified at
     `toml.io <https://toml.io/>`__. It is what :file:`pyproject.toml` is written in, and the standard library reads
     it with :external+python:mod:`tomllib`.

     As a pyTooling configuration format it is :ref:`planned <CONFIG/FileFormat/TOML>`.

     Wikipedia: :wiki:`TOML <TOML>`

   Tree
     A *tree* is a data structure made of :term:`nodes <node>` and parent-child relations. All nodes in a tree share one
     common :term:`ancestor` call :term:`root`.

     A tree is a special form of a :term:`directed acyclic graph (DAG) <DAG>`.

   UCRT
     Universal C Runtime

     Wikipedia: :wiki:`Microsoft Windows library files: UCRT <Microsoft_Windows_library_files#UCRT>`

   URI
     Uniform Resource Identifier

     Wikipedia: :wiki:`Uniform Resource Identifier <Uniform_Resource_Identifier>`

   URL
     Uniform Resource Locator

     Wikipedia: :wiki:`Uniform Resource Locator <URL>`

   URN
     Uniform Resource Name

     Wikipedia: :wiki:`Uniform Resource Name <Uniform_Resource_Name>`

   Vertex
     A vertex is a :term:`node` in a graph. Vertexes in a graph are connected using :term:`edges <edge>`.

   WSL
     Windows System for Linux

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

