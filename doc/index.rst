.. include:: shields.inc

.. raw:: latex

   \part{Introduction}

.. only:: html

   |  |SHIELD:svg:pyTooling-github| |SHIELD:svg:pyTooling-src-license| |SHIELD:svg:pyTooling-ghp-doc| |SHIELD:svg:pyTooling-doc-license|
   |  |SHIELD:svg:pyTooling-pypi-tag| |SHIELD:svg:pyTooling-pypi-status| |SHIELD:svg:pyTooling-pypi-python|
   |  |SHIELD:svg:pyTooling-gha-test| |SHIELD:svg:pyTooling-lib-status| |SHIELD:svg:pyTooling-codacy-quality| |SHIELD:svg:pyTooling-codacy-coverage| |SHIELD:svg:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:svg:pyTooling-lib-dep| |SHIELD:svg:pyTooling-lib-rank|

.. only:: latex

   |SHIELD:png:pyTooling-github| |SHIELD:png:pyTooling-src-license| |SHIELD:png:pyTooling-ghp-doc| |SHIELD:png:pyTooling-doc-license|
   |SHIELD:png:pyTooling-pypi-tag| |SHIELD:png:pyTooling-pypi-status| |SHIELD:png:pyTooling-pypi-python|
   |SHIELD:png:pyTooling-gha-test| |SHIELD:png:pyTooling-lib-status| |SHIELD:png:pyTooling-codacy-quality| |SHIELD:png:pyTooling-codacy-coverage| |SHIELD:png:pyTooling-codecov-coverage|

.. Disabled shields: |SHIELD:svg:pyTooling-gitter| |SHIELD:png:pyTooling-lib-dep| |SHIELD:png:pyTooling-lib-rank|

--------------------------------------------------------------------------------

pyTooling Documentation
#######################

**pyTooling** is a powerful collection of arbitrary and useful (abstract) data models, lacking classes, decorators, a
new performance boosting meta-class and enhanced exceptions. It also provides lots of helper functions e.g. to ease the
handling of package descriptions or to unify multiple existing APIs into a single API.

It's useful ‒ if not even essential ‒ for **any** Python-based project independent if it's a library, framework, CLI
tool or just a "script".

In addition, pyTooling provides a collection of `CI job templates for GitHub Actions <https://github.com/pyTooling/Actions>`__.
This drastically simplifies GHA-based CI pipelines for Python projects.


Package Details
***************

The following descriptions and code examples give peak onto pyTooling's highlights. But be ensured, there is more to
explore, which can't be highlighted on the main landing page.

Attributes
==========

.. grid:: 2

   .. grid-item::
      :columns: 6

      The :ref:`pyTooling.Attributes <ATTR>` module offers the base implementation of
      `.NET-like attributes <https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/reflection-and-attributes/>`__
      realized with :term:`Python decorators <decorator>`. The annotated and declarative data is stored as instances of
      :ref:`Attribute <ATTR/Predefined/Attribute>` classes in an additional ``__pyattr__`` field per class, method or
      function.

      The annotation syntax (decorator syntax) allows users to attach any structured data to classes, methods or
      functions. In many cases, a user will derive a custom attribute from :ref:`Attribute <ATTR/Predefined/Attribute>`
      and override the ``__init__`` method, so user-defined parameters can be accepted when the attribute is constructed.

      Later, classes, methods or functions can be searched for by querying the attribute class for attribute instance
      usage locations (see example to the right). Another option for class and method attributes is declaring a classes
      using pyTooling's :ref:`META/ExtendedType` meta-class. Here the class itself offers helper methods for discovering
      annotated methods.

      A :ref:`SimpleAttribute <ATTR/Predefined/SimpleAttribute>` class is offered accepting any positional and keyword
      parameters. In a more advanced use case, users are encouraged to derive their own attribute class hierarchy from
      :ref:`Attribute <ATTR/Predefined/Attribute>`.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Function Attributes

            .. code-block:: Python

               from pyTooling.Attributes import Attribute

               class Command(Attribute):
                 def __init__(self, cmd: str, help: str = "") -> None:
                   pass

               class Flag(Attribute):
                 def __init__(self, param: str, short: str = None, long: str = None, help: str = "") -> None:
                   pass

               @Command(cmd="version", help="Print version information.")
               @Flag(param="verbose", short="-v", long="--verbose", help="Default handler.")
               def Handler(self, args) -> None:
                 pass

               for function in Command.GetFunctions():
                 pass

         .. tab-item:: Method Attributes

            .. code-block:: Python

               from pyTooling.Attributes import Attribute
               from pyTooling.MetaClasses import ExtendedType

               class TestCase(Attribute):
                 def __init__(self, name: str) -> None:
                   pass

               class Program(metaclass=ExtendedType):
                  @TestCase(name="Handler routine")
                  def Handler(self, args) -> None:
                    pass



               prog = Program()
               for method, attributes in prog.GetMethodsWithAttributes(predicate=TestCase):
                 pass

         .. tab-item:: Class Attributes

            .. code-block:: Python

               from pyTooling.Attributes import Attribute
               from pyTooling.MetaClasses import ExtendedType

               class TestSuite(Attribute):
                 def __init__(self, name: str) -> None:
                   pass

               @TestSuite(name="Command line interface tests")
               class Program(metaclass=ExtendedType):
                  def Handler(self, args) -> None:
                    pass

               prog = Program()


               for testsuite in TestSuite.GetClasses():
                 pass

ArgParse
--------

.. grid:: 2

   .. grid-item::
      :columns: 6

      Defining commands, arguments or flags for a command line argument parser like :mod:`argparse` is done imperatively.
      This means code executed in-order defines how the parser will accept inputs. Then more user-defined code is needed
      to dispatch the collected and type-converted arguments to handler routines. See an example to the right as
      "Traditional argparse".

      In contrast, :ref:`pyTooling.Attributes.ArgParse <ATTR/ArgParse>` allows the definition of :ref:`commands <ATTR/ArgParse/Commands>`,
      :ref:`arguments <ATTR/ArgParse/Arguments>` or :ref:`flags <ATTR/ArgParse/Flags>` as declarative code attached to
      handler routines using pyTooling's attributes. This allow a cleaner and more readable coding style. Also
      maintainability is improved, as arguments are defined using clear attribute names attached to the matching handler
      routine. Thus parser and handler code is not separated.

      If the command line interface uses many commands, handlers and their arguments can be spread across
      :ref:`mixin classes <ATTR/ArgParse/MixIn>`. Later, the whole CLI is assembled by using multiple inheritance. In
      case handlers use shared argument sets, arguments can be :ref:`grouped <ATTR/ArgParse/Grouping>` and shared by
      defining grouping attributes.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Traditional ArgParse

            .. code-block:: Python

               class Program:
                 def __init__(self) -> None:
                   mainParser = argparse.ArgumentParser()
		             mainParser.set_defaults(func=self.HandleDefault)
                   mainParser.add_argument("-v", "--verbose")
                   subParsers = mainParser.add_subparsers()

                   newUserParser = subParsers.add_parser("new-user", help="Add a new user.")
                   newUserParser.add_argument(dest="username", metaName="username", help="Name of the new user.")
                   newUserParser.add_argument("--quota", dest="quota", help="Max usable disk space.")
                   newUserParser.set_defaults(func=self.NewUserHandler)

                   deleteUserParser = subParsers.add_parser("delete-user", help="Delete a user.")
                   deleteUserParser.add_argument(dest="username", metaName="username", help="Name of the user.")
                   deleteUserParser.add_argument("-f", "--force", dest="force", help="Ignore internal checks.")
                   deleteUserParser.set_defaults(func=self.DeleteUserHandler)

                   listUserParser = subParsers.add_parser("list-user", help="List all users.")
                   listUserParser.set_defaults(func=self.ListUserHandler)

                 def HandleDefault(self, args) -> None:
                   pass

                 def NewUserHandler(self, args) -> None:
                   pass

                 def DeleteUserHandler(self, args) -> None:
                   pass

                 def ListUserHandler(self, args) -> None:
                   pass

         .. tab-item:: pyTooling.Attributes.ArgParse
            :selected:

            .. code-block:: Python

               class Program:
                 @DefaultHandler()
                 @FlagArgument(short="-v", long="--verbose", dest="verbose", help="Show verbose messages.")
                 def HandleDefault(self, args) -> None:
                   pass

                 @CommandHandler("new-user", help="Add a new user.")
                 @StringArgument(dest="username", metaName="username", help="Name of the new user.")
                 @LongValuedFlag("--quota", dest="quota", help="Max usable disk space.")
                 def NewUserHandler(self, args) -> None:
                   pass

                 @CommandHandler("delete-user", help="Delete a user.")
                 @StringArgument(dest="username", metaName="username", help="Name of the user.")
                 @FlagArgument(short="-f", long="--force", dest="force", help="Ignore internal checks.")
                 def DeleteUserHandler(self, args) -> None:
                   pass

                 @CommandHandler("list-user", help="List all users.")
                 def ListUserHandler(self, args) -> None:
                   pass

CLI Abstraction
===============

.. grid:: 2

   .. grid-item::
      :columns: 6

      :ref:`pyTooling.CLIAbstraction <CLIABS>` offers an abstraction layer for command line programs, so they can be
      used easily in Python. There is no need for manually assembling parameter lists or considering the order of
      parameters. All parameters like ``-v`` or ``--value=42`` are described using nested classes on a
      :ref:`Program <CLIABS/Program>` class. Each nested class derived from predefined argument classes knows about the
      correct formatting pattern, character escaping, and if needed about necessary type conversions.

      Such an instance of a program can be converted to an argument list suitable for :class:`subprocess.Popen`.
      In stead of deriving from :ref:`Program <CLIABS/Program>`, abstracted command line tools can derive from
      :ref:`Executable <CLIABS/Executable>` which offers embedded :class:`~subprocess.Popen` behavior.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         class Git(Executable):
           def __new__(cls, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> self:
             cls._executableNames = {
               "Darwin": "git",
               "FreeBSD": "git",
               "Linux": "git",
               "Windows": "git.exe"
             }
             return super().__new__(cls)

           @CLIArgument()
           class FlagHelp(ShortFlag, name="h"): ...

           @CLIArgument()
           class FlagVersion(LongFlag, name="version"): ...

           @CLIArgument()
           class CommandHelp(CommandArgument, name="help"): ...

           @CLIArgument()
           class CommandCommit(CommandArgument, name="commit"): ...

           @CLIArgument()
           class ValueCommitMessage(ShortTupleFlag, name="m"): ...

         tool = Git()
         tool[tool.FlagVersion] = True

         tool.StartProcess()


Common Helper Functions
=======================

.. grid:: 2

   .. grid-item::
      :columns: 6

      This is a set of useful :ref:`helper functions <COMMON/HelperFunctions>`:

      * :ref:`COMMON/Helper/firstElement`, :ref:`COMMON/Helper/lastElement` get the first/last element from an indexable.
      * :ref:`COMMON/Helper/firstItem`, :ref:`COMMON/Helper/lastItem` get the first/last item from an iterable.
      * :ref:`COMMON/Helper/firstKey`, :ref:`COMMON/Helper/firstValue`, :ref:`COMMON/Helper/firstPair` get the first
        key/value/pair from an ordered dictionary.
      * :ref:`COMMON/Helper/getsizeof` calculates the "real" size of a data structure.
      * :ref:`COMMON/Helper/isnestedclass` checks if a class is nested inside another class.
      * :ref:`COMMON/Helper/mergedicts` merges multiple dictionaries into a new dictionary.
      * :ref:`COMMON/Helper/zipdicts` iterate multiple dictionaries simultaneously.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: firstItem

            .. code-block:: Python

               def myFunction(condition: bool) -> Iterable:
                 myList = [3, 21, 5, 7]
                 if condition:
                   return myList[0:2]
                 else
                   return myList[1:3]

               beginOfSequence = myFunction(True)
               first = firstItem(beginOfSequence)


               # 3

         .. tab-item:: mergedicts

            .. code-block:: Python

               from pyTooling.Common import mergedicts

               dictA = {"a": 11, "b": 12}
               dictB = {"x": 21, "y": 22}

               for key, value in mergedicts(dictA, dictB):
                 pass

               # ("a", 11)
               # ("b", 12)
               # ("x", 21)
               # ("y", 22)

         .. tab-item:: zipdicts
            :selected:

            .. code-block:: Python

               from pyTooling.Common import zipdicts

               dictA = {"a": 11, "b": 12, "c": 13}
               dictB = {"a": 21, "b": 22, "c": 23}

               for key, valueA, valueB in zipdicts(dictA, dictB):
                 pass


               # ("a", 11, 21)
               # ("a", 12, 22)
               # ("a", 13, 23)


Common Classes
==============

.. grid:: 2

   .. grid-item::
      :columns: 6

      * :ref:`Call-by-reference parameters <COMMON/CallByRef>`: Python doesn't provide *call-by-reference parameters* for
        simple types. |br|
        This behavior can be emulated with classes provided by the :mod:`pyTooling.CallByRef` module.
      * :ref:`Unified license names <LICENSING>`: Setuptools, PyPI, and others have a varying understanding of license names. |br|
        The :mod:`pyTooling.Licensing` module provides :ref:`unified license names <LICENSING>` as well as license name
        mappings or translations.
      * :ref:`Unified platform and environment description <COMMON/Platform>`: Python has many ways in figuring out the
        current platform using APIs from ``sys``, ``platform``, ``os``, …. Unfortunately, none of the provided standard
        APIs offers a comprehensive answer. pyTooling provides a :ref:`CurrentPlatform <COMMON/CurrentPlatform>`
        singleton summarizing multiple platform APIs into a single class instance.
      * :ref:`Representations of version numbers <VERSIONING>`: While Python itself has a good versioning schema, there
        are no classes provided to abstract a version numbers. pyTooling provides such representations following
        semantic versioning (SemVer) and calendar versioning (CalVer) schemes. The implementation can parse many common
        formats and allows user defined formatting. In addition, versions can be compared with various operators
        including PIPs ``~=`` operator.
      * :ref:`Measuring execution times <COMMON/Stopwatch>` can be achieved by using a stopwatch implementation
        providing start, pause, resume, split and stop features. Internally, Python's *high resolution clock* is used.
        The stopwatch also provides a context manager, so it can be used in a ``with``-statement.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Licenses

            .. code-block:: Python

               pass

         .. tab-item:: Platform

            .. code-block:: Python

               from pytest import mark
               from unittest import TestCase

               from pyTooling.Common import CurrentPlatform

               class MyTests(TestCase):
                 @mark.skipif(not CurrentPlatform.IsNativeWindows, reason="Skipped, if platform isn't native Windows.")
                 def test_OnlyNativeWindows(self) -> None:
                   pass

                 @mark.skipif(not CurrentPlatform.IsMinGW64OnWindows, reason="Skipped, if platform isn't MinGW64.")
                 def test_OnlyMinGW64(self) -> None:
                   pass

                 @mark.skipif(CurrentPlatform.IsPyPy, reason="getsizeof: not supported on PyPy")
                 def test_ObjectSize(self) -> None:
                   pass

         .. tab-item:: Version Classes
            :selected:

            .. code-block:: Python

               from pyTooling.Versioning import SemanticVersion, PythonVersion, CalendarVersion

               version = SemanticVersion("v2.5.4")

               version.Major
               version.Minor
               version.Patch

               if version >= "2.5":
                 print(f"{version:%p%M.%m.%u}")

               # Python versioning from sys.version_info
               from pyTooling.Versioning import PythonVersion, CalendarVersion

               pythonVersion = PythonVersion.FromSysVersionInfo()

               # Calendar versioning
               from pyTooling.Versioning import CalendarVersion

               osvvmVersion = CalendarVersion.Parse("2024.07")

         .. tab-item:: Stopwatch

            .. code-block:: Python

               from pyTooling.Stopwatch import Stopwatch

               sw = Stopwatch("my name", preferPause=True)
               sw.Start()
               # do something
               sw.Pause()

               with sw:
                 # do something

               sw.Resume()
               # do something
               sw.Stop()

               print(f"Start:      {sw.StartTime}")
               print(f"Stop:       {sw.StopTime}")
               print(f"Duration:   {sw.Duration}")
               print(f"Activity:   {sw.Activity}")
               print(f"Inactivity: {sw.Inactivity}")
               print("Splits:")
               for duration, activity in sw:
                  print(f"  {'running for' if activity else 'paused for '} {duration}")


Configuration
=============

.. grid:: 2

   .. grid-item::
      :columns: 6

      Various file formats suitable for configuration information share the same features supporting: key-value pairs
      (dictionaries), sequences (lists), and simple types like string, integer and float. pyTooling provides an
      :ref:`abstract configuration file data model <CONFIG>` supporting these features. Moreover, concrete
      :ref:`configuration file format reader <CONFIG/FileFormat>` implementations are provided as well.

      * :ref:`JSON configuration reader <CONFIG/FileFormat/JSON>` for the JSON file format.
      * :ref:`TOML configuration reader <CONFIG/FileFormat/TOML>`  |rarr| To be implemented.
      * :ref:`YAML configuration reader <CONFIG/FileFormat/YAML>` for the YAML file format.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: JSON

            .. code-block:: Python

               from pathlib import Path
               from pyTooling.Configuration.JSON import Configuration

               configFile = Path("config.json")
               config = Configuration(configFile)

               # Accessing root-level scalar value
               configFileFormatVersion = config["version"]
               # Accessing value in a sequence
               firstItemInList = config["list"][0]
               # Accessing first value in dictionary
               firstItemInDict = config["dict"]["key_1"]

               # Iterate simple list
               simpleList = config["list"]
               for item in simpleList:
                 pass

         .. tab-item:: TOML

            .. todo:: Needs example code

            .. code-block:: Python

               pass

         .. tab-item:: YAML

            .. code-block:: Python

               from pathlib import Path
               from pyTooling.Configuration.YAML import Configuration

               configFile = Path("config.yml")
               config = Configuration(configFile)

               # Accessing root-level scalar value
               configFileFormatVersion = config["version"]
               # Accessing value in a sequence
               firstItemInList = config["list"][0]
               # Accessing first value in dictionary
               firstItemInDict = config["dict"]["key_1"]

               # Iterate simple list
               simpleList = config["list"]
               for item in simpleList:
                 pass

         .. tab-item:: XML

            .. todo:: Needs example code

            .. code-block:: Python

               pass


Data Structures
===============

.. grid:: 2

   .. grid-item::
      :columns: 6

      pyTooling also provides :ref:`fast and powerful data structures <STRUCT>` offering object-oriented APIs:

      * :ref:`Graph data structure <STRUCT/Graph>` |br|
        |rarr| A directed graph implementation using a :class:`~pyTooling.Graph.Vertex` and an
        :class:`~pyTooling.Graph.Edge` class.
      * :ref:`Tree data structure <STRUCT/Tree>` |br|
        |rarr| A fast and simple implementation using a single :class:`~pyTooling.Tree.Node` class.
      * :ref:`Doubly Linked List <STRUCT/LinkedList>` |br|
        |rarr| An object-oriented implementation using a :class:`~pyTooling.List.Node` and a
        :class:`~pyTooling.List.LinkedList` class.
      * :ref:`Path data structure <STRUCT/Path>` |br|
        |rarr| To be documented.
      * :ref:`Finite State Machine data structure <STRUCT/StateMachine>` |br|
        |rarr| A data model for state machines using a :class:`~pyTooling.StateMachine.State` and a
        :class:`~pyTooling.StateMachine.Transition` class.

      .. #* :ref:`Scope data structure <STRUCT/Scope>` |br|
         |rarr| A fast and simple implementation using a single :class:`~pyTooling.Tree.Node` class.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Graph

            .. code-block:: Python

               from pyTooling.Graph import Graph, Vertex

               graph = Graph(name="myGraph")

               # Create new vertices and an edge between them
               vertex1 = Vertex(vertexID=1, graph=graph)
               vertex2 = Vertex(vertexID=2, value="2", graph=graph)
               edge12 = vertex1.EdgeToVertex(vertex2, edgeValue="1 -> 2", weight=15)

               # Create an edge to a new vertex
               edge2x = vertex2.EdgeToNewVertex(vertexID=3)
               vertex3 = edge2x.Destination

               # Create a link between two vertices
               link31 = vertex3.LinkToVertex(vertex1)

         .. tab-item:: Statemachine

            .. todo:: Needs example code

            .. code-block:: Python

               pass

         .. tab-item:: Tree

            .. code-block:: Python

               from pyTooling.Tree import Node

               # Create a new tree by creating a root node (no parent reference)
               root = Node(value="OSVVM Regression Tests")

               # Construct the tree top-down
               lib = Node(value="Utility Library", parent=root)

               # Another standalone node with unique ID (actually an independent tree)
               common = Node(nodeID=5, value="Common")

               # Construct bottom-up
               axi = Node(value="AXI")
               axiCommon = Node(value="AXI4 Common")
               axi.AddChild(axiCommon)

               # Group nodes and handover children at node creation time
               vcList = [common, axi]
               vcs = Node(value="Verification Components", parent=root, children=vcList)

               # Add multiple nodes at once
               axiProtocols = (
                 Node(value="AXI4-Stream"),
                 Node(value="AXI4-Lite"),
                 Node(value="AXI4")
               )
               axi.AddChildren(axiProtocols)

               # Create another standalone node and attach it later to a tree.
               uart = Node(value="UART")
               uart.Parent = vcs

         .. tab-item:: Doubly Linked List

            .. code-block:: Python

               from pyTooling.List import Node

               # Create a new doubly linked list from an iterable
               node = Node(2)
               nodes = (Node(1), node, Node(3))
               linkedList = LinkedList(nodes)

               # Add node before first element
               linkedList.InsertBeforeFirst(Node(0))

               # Add node after last element
               linkedList.InsertAfterLast(Node(4))

               # Get length
               linkedList.Count   # alternatively: len(linkedList)

               # Delete node
               node.Remove()

.. grid:: 3

   .. grid-item:: Graph
      :columns: 4

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
           classDef node fill:#eee,stroke:#777,font-size:smaller;
           classDef node fill:#eee,stroke:#777,font-size:smaller;

   .. grid-item:: Statemachine
      :columns: 3

      .. mermaid::
         :caption: A statemachine graph.

         %%{init: { "flowchart": { "nodeSpacing": 15, "rankSpacing": 30, "curve": "linear", "useMaxWidth": false } } }%%
         graph TD
           A(Idle); B(Check); C(Prepare); D(Read); E(Finished); F(Write) ; G(Retry); H(WriteWait); I(ReadWait)

           A:::mark1 --> B --> C --> F
           F --> H --> E:::cur
           B --> G --> B
           G -.-> A --> C
           D -.-> A
           C ---> D --> I --> E -.-> A

           classDef node fill:#eee,stroke:#777,font-size:smaller;
           classDef cur fill:#9e9,stroke:#6e6;
           classDef mark1 fill:#69f,stroke:#37f,color:#eee;

   .. grid-item:: Tree
      :columns: 5

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


Decorators
==========

.. grid:: 2

   .. grid-item::
      :columns: 6

      * :ref:`META/Abstract`

        * :ref:`DECO/AbstractMethod`: Methods marked with :pycode:`@abstractmethod` are abstract and need to be overwritten in
          a derived class. |br|
          An *abstract method* might be called from the overwriting method.
        * :ref:`DECO/MustOverride`: Methods marked with :pycode:`@mustoverride` are abstract and need to be overridden in a
          derived class. |br|
          It's not allowed to call a *mustoverride method*.

      * :ref:`DECO/DataAccess`

        * :ref:`DECO/readonly`: Methods marked with :pycode:`@readonly` get transformed into a read-only property.
        * ⚠BROKEN⚠: Methods with :ref:`DECO/classproperty` decorator transform methods to class-properties.

      * :ref:`DECO/Documentation`

        * :ref:`DECO/export`: Register a given function or class as publicly accessible in a module. |br|
          Functions and classes exposed like this are also used by Sphinx extensions to (auto-)document public module members.
        * :ref:`DECO/InheritDocString`: The decorator copies the doc-string from a given base-class to the annotated method.

      * :ref:`DECO/Performance`

        * :ref:`DECO/slotted`: Classes marked with :pycode:`@slotted` get transformed into classes using ``__slots__``. |br|
          This is achieve by exchanging the meta-class to :class:`~pyTooling.MetaClasses.ExtendedType`.
        * :ref:`DECO/mixin`: Classes marked with :pycode:`@mixin` do not store their fields in ``__slots__``. |br|
          When such a :term:`mixin-class` is inherited by a class using slots, the fields of the mixin become slots.
        * :ref:`DECO/singleton`: Classes marked with :pycode:`@singleton` get transformed into singleton classes. |br|
          This is achieve by exchanging the meta-class to :class:`~pyTooling.MetaClasses.ExtendedType`.

      * :ref:`DECO/Misc`

        * :ref:`DECO/notimplemented`: This decorator replaces a callable (function or method) with a callable raising a
          :exc:`NotImplementedError`. The original code becomes unreachable.

   .. grid-item::
      :columns: 6

      .. todo:: Needs example code

      .. code-block:: Python

         pass

Exceptions
==========

* :exc:`~pyTooling.Exceptions.EnvironmentException` |br|
  ... is raised when an expected environment variable is missing.
* :exc:`~pyTooling.Exceptions.PlatformNotSupportedException` |br|
  ... is raise if the platform is not supported.
* :exc:`~pyTooling.Exceptions.NotConfiguredException` |br|
  ... is raise if the requested setting is not configured.


Meta-Classes
============

pyTooling provides an :ref:`enhanced meta-class <META>` called :class:`~pyTooling.MetaClasses.ExtendedType` to replace
the default meta-class :class:`type`. It combines features like using slots, abstract methods and creating singletons by
applying a single meta-class. In comparison, Python's approach in to provide multiple specific meta-classes (see
:mod:`abc`) that can't be combined e.g. to a singleton using slots.

:ref:`ExtendedType <META/ExtendedType>` allows to implement :ref:`slotted types <META/Slotted>`,
:ref:`mixins <META/Mixin>`, :ref:`abstract and override methods <META/Abstract>` and :ref:`singletons <META/Singleton>`,
and combinations thereof. Exception messages in case of errors have been improved too.

Slotted types significantly reduce the memory footprint by 4x and decrease the class field access time by 10..25%. While
setting up slotted types needed a lot of manual coding, this is now fully automated by this meta-class. It assumes,
annotated fields are going to be slots. Moreover, it also takes care deferred slots in multiple-inheritance scenarios by
marking secondary base-classes as mixins. This defers slot creation until a mixin is inherited.

.. grid:: 2

   .. grid-item::
      :columns: 6

      :pycode:`class MyClass(metaclass=ExtendedType):`
        A class definition using the :class:`~pyTooling.MetaClasses.ExtendedType` meta-class. I can now implement
        :ref:`abstract methods <META/Abstract>` using the decorators :ref:`DECO/AbstractMethod` or :ref:`DECO/MustOverride`.

      :pycode:`class MyClass(metaclass=ExtendedType, singleton=True):`
        A class defined with enabled :ref:`singleton <META/Singleton>` behavior allows only a single instance of that class to
        exist. If another instance is going to be created, a previously cached instance of that class will be returned.

      :pycode:`class MyClass(metaclass=ExtendedType, slots=True):`
        A class defined with enabled :ref:`slots <META/Slotted>` behavior stores instance fields in slots. The meta-class,
        translates all type-annotated fields in the class definition to slots. Slots allow a more efficient field storage and
        access compared to dynamically stored and accessed fields hosted in ``__dict__``. This improves the memory footprint
        as well as the field access performance of all class instances. This behavior is automatically inherited to all
        derived classes.

      :pycode:`class MyClass(metaclass=ExtendedType, slots=True, mixin=True):`
        A class defined with enabled :ref:`mixin <META/Mixin>` behavior collects type-annotated instance fields so they can be
        added to slots in an inherited class. Thus, slots are not created for mixin-classes but deferred in the inheritance
        hierarchy.

      :pycode:`class MyClass(SlottedObject):`
        A class definition deriving from :class:`~pyTooling.MetaClasses.SlottedObject` will bring the slotted type behavior to
        that class and all its derived classes.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Singleton

            .. code-block:: Python

               class Application(metaclass=ExtendedType, singleton=True):
                  _x: int

                  def __init__(self) -> None:
                     print("Instance of 'App1WithoutParameters' was created")
                     self._x = 10

               instance1 = Application()
               instance2 = Application()
               assert instance1 is instance2

         .. tab-item:: Slotted Class

            .. code-block:: Python

               class Data(metaclass=ExtendedType, slots=True):
                  _x: int
                  _y: int = 12

                  def __init__(self, x: int) -> None:
                    self._x = x

               data = Data(11)

         .. tab-item:: MixIn Class

            .. todo:: Needs example code

            .. code-block:: Python

               def


Packaging
=========

.. grid:: 2

   .. grid-item::
      :columns: 6

      A set of helper functions to describe a Python package for setuptools.

      * Helper Functions:

        * :func:`pyTooling.Packaging.loadReadmeFile` |br|
          Load a ``README.md`` file from disk and provide the content as long description for setuptools.
        * :func:`pyTooling.Packaging.loadRequirementsFile` |br|
          Load a ``requirements.txt`` file from disk and provide the content for setuptools.
        * :func:`pyTooling.Packaging.extractVersionInformation` |br|
          Extract version information from Python source files and provide the data to setuptools.

      * Package Descriptions

        * :func:`pyTooling.Packaging.DescribePythonPackage` |br|
          tbd
        * :func:`pyTooling.Packaging.DescribePythonPackageHostedOnGitHub` |br|
          tbd

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: DescribePythonPackage

            .. code-block:: Python

               from setuptools          import setup

               from pathlib             import Path
               from pyTooling.Packaging import DescribePythonPackage

               pass

         .. tab-item:: DescribePythonPackageHostedOnGitHub
            :selected:

            .. code-block:: Python

               from setuptools          import setup

               from pathlib             import Path
               from pyTooling.Packaging import DescribePythonPackageHostedOnGitHub

               gitHubNamespace =        "Paebbels"
               packageName =            "pyVersioning"
               packageDirectory =       packageName.replace(".", "/")
               packageInformationFile = Path(f"{packageDirectory}/__init__.py")

               setup(
                 **DescribePythonPackageHostedOnGitHub(
                   packageName=packageName,
                   description="Write version information collected from (CI) environment for any programming language as source file.",
                   gitHubNamespace=gitHubNamespace,
                   sourceFileWithVersion=packageInformationFile,
                   consoleScripts={
                     "pyVersioning": "pyVersioning.CLI:main",
                   }
                 )
               )


Terminal
========

.. grid:: 2

   .. grid-item::
      :columns: 6

      The :ref:`pyTooling.TerminalUI <TERM>` package offers a set of helpers to implement a text user interface (TUI) in
      a terminal. It's designed on the idea that command line programs emit one line of text per message. Each message
      can be categorized as normal text, warnings, errors, and many more.

      Therefore, this package offers a :ref:`LineTerminal <TERM/LineTerminal>` implementation, derived from a basic
      :ref:`Terminal <TERM/Terminal>` class. Of cause, it also includes colored outputs based on `colorama`.

      .. todo:: Terminal helpers.

   .. grid-item::
      :columns: 6

      .. todo:: Needs example code


.. _CONTRIBUTORS:

Contributors
************

* `Patrick Lehmann <https://GitHub.com/Paebbels>`__ (Maintainer)
* `Sven Köhler <https://GitHub.com/skoehler>`__
* `Unai Martinez-Corral <https://GitHub.com/umarcor/>`__
* `and more... <https://GitHub.com/pyTooling/pyTooling/graphs/contributors>`__


.. _LICENSE:

License
*******

.. only:: html

   This Python package (source code) is licensed under `Apache License 2.0 <Code-License.html>`__. |br|
   The accompanying documentation is licensed under `Creative Commons - Attribution 4.0 (CC-BY 4.0) <Doc-License.html>`__.

.. only:: latex

   This Python package (source code) is licensed under **Apache License 2.0**. |br|
   The accompanying documentation is licensed under **Creative Commons - Attribution 4.0 (CC-BY 4.0)**.


.. toctree::
   :caption: Overview
   :hidden:

   News
   Installation
   Dependency
   Tutorials/index

.. raw:: latex

   \part{Main Documentation}

.. toctree::
   :caption: Attributes
   :hidden:

   Attributes/index
   Attributes/ArgParse

.. toctree::
   :caption: CLI Abstraction
   :hidden:

   CLIAbstraction/index
   CLIAbstraction/Program
   CLIAbstraction/Executable
   CLIAbstraction/Arguments

.. toctree::
   :caption: Common
   :hidden:

   Common/index
   Common/CallByRef
   Common/Licensing
   Common/Platform
   Common/Stopwatch
   Common/Versioning

.. toctree::
   :caption: Configuration
   :hidden:

   Configuration/index
   Configuration/FileFormats

.. toctree::
   :caption: Data Structures
   :hidden:

   DataStructures/index
   DataStructures/LinkedList
   DataStructures/Cartesian
   DataStructures/Graph
   DataStructures/Path/index
   DataStructures/StateMachine
   DataStructures/Tree

.. toctree::
   :caption: Decorators
   :hidden:

   Decorators

.. toctree::
   :caption: Exceptions and Warnings
   :hidden:

   Exceptions
   Warning/index

.. toctree::
   :caption: Meta Classes
   :hidden:

   MetaClasses

.. toctree::
   :caption: Packaging
   :hidden:

   Packaging

.. toctree::
   :caption: Terminal
   :hidden:

   Terminal/index

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   Python Class Reference <pyTooling/pyTooling>
   unittests/index
   coverage/index
   Doc. Coverage Report <DocCoverage>
   Static Type Check Report ➚ <typing/index>

.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :hidden:

   License
   Doc-License
   Glossary
   genindex
   Python Module Index <modindex>
   TODO
