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

   Cygwin
     :wiki:`Cygwin` is a :wiki:`POSIX`-compatible programming and runtime environment for Windows.

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
     ...

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

   Exception
     ...

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

   Meta-Class
     A *meta-class* is a class helping to construct classes. Thus, it's the type of a type.

     .. mermaid::
        :caption: Relation of meta-classes, classes and instances.

        %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
        graph TD
          T(type)
          ET(MetaClass)
          B(BaseClass)
          C(Class)
          I1(Instance);I2(Instance)

          T --> T
          T:::mark1 --> ET:::mark1 -.class definition..-> B
          B:::mark2 --> C:::mark2 -.instantiation..-> I1 & I2

          classDef node font-size:smaller;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee,font-size:smaller;
          classDef mark2 fill:#69f,stroke:#37f,font-size:smaller;

   MinGW
     Minimalistic GNU for Windows.

   MSYS2
     ...

   Mustoverride Method
     A *must-override* method provides a partial implementation (incomplete code) and must therefore be fully
     implemented by all derived classes.

     If a *must-override* method is not overridden, an exception is raised when instantiating the class, because the
     :term:`class is abstract <Abstract Class>`.

   native
     A *native environment* is a platform just with the operating system. There is no additional environment layer like
     MSYS2.

   Node
     ...

   Overloading
     ...

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
     ...

   Tree
     A *tree* is a data structure made of :term:`nodes <node>` and parent-child relations. All nodes in a tree share one
     common :term:`ancestor` call :term:`root`.

     A tree is a special form of a :term:`directed acyclic graph (DAG) <DAG>`.

   UCRT
     Universal C Runtime

   Vertex
     A vertex is a :term:`node` in a graph.

   WSL
     Windows System for Linux
