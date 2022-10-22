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
     *Ancestors* are all :term:`parent nodes <parent>` and parent nodes thereof (:term:`grandparents <grandparent>`,
     grand-grandparent, ...) from current node to the :term:`root` node.

     In a tree, a :term:`node` has only a single :term:`parent` node, thus a list of ancestors is a direct line.

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee;
          classDef mark2 fill:#69f,stroke:#37f;

   Base-Class
     An ancestor class for other derived classes.

   Children
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Cygwin
     ...

   Decorator
     ...

   Descendants
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Edge
     ...

   Exception
     ...

   Grandchildren
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Grandparent
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Meta-Class
     ...

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
     A parent is an object

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Relatives
     Relatives are siblings and their descendants.

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Root
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark1 fill:#69f,stroke:#37f,color:#eee;

   Siblings
     ...

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

          classDef cur fill:#9e9,stroke:#6e6;
          classDef mark2 fill:#69f,stroke:#37f;

   Singleton
     ...

   Slots
     ...

   UCRT
     Universal C Runtime

   Vertex
     A vertex is a :term:`node` in a graph.

   WSL
     Windows System for Linux
