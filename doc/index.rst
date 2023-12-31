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

**pyTooling** is a powerful collection of arbitrary useful abstract data models, lacking classes, decorators, a new
performance boosting meta-class and enhanced exceptions. It also provides lots of helper functions e.g. to ease the
handling of package descriptions or to unify multiple existing APIs into a single API.

It's useful ‒ if not even essential ‒ for **any** Python-base project independent if it's a library, framework, CLI tool
or just a "script".

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

      The :mod:`pyTooling.Attributes` module offers the base implementation of `.NET-like attributes <https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/reflection-and-attributes/>`__
      realized with Python decorators. The annotated and declarative data is stored as instances of :class:`~pyTooling.Attributes.Attribute`
      classes in an additional ``__pyattr__`` field per class, method or function.

      The annotation syntax allows users to attache any structured data to classes, methods or functions. In many cases,
      a user will derive a custom attribute from :class:`~pyTooling.Attributes.Attribute` and override the ``__init__``
      method, so user-defined parameters can be accepted when the attribute is constructed.

      Later, classes, methods or functions can be searched for by querying the attribute for usage locations (see
      example to the right). Another option for class and method attributes is defining a new classes using pyTooling's
      :class:`~pyTooling.MetaClasses.ExtendedType` meta-class. here the class itself offers helper methods for
      discovering annotated methods.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Function Attributes

            .. code-block:: Python

               from pyTooling.Attributes import Attribute

               class Command(Attribute):
                 def __init__(self, cmd: str, help: str = ""):
                   pass

               class Flag(Attribute):
                 def __init__(self, param: str, short: str = None, long: str = None, help: str = ""):
                   pass

               @Command(cmd="version", help="Print version information.")
               @Flag(param="verbose", short="-v", long="--verbose", help="Default handler.")
               def Handler(self, args):
                 pass

               for function in Command.GetFunctions():
                 pass

         .. tab-item:: Method Attributes

            .. code-block:: Python

               from pyTooling.Attributes import Attribute
               from pyTooling.MetaClasses import ExtendedType

               class TestCase(Attribute):
                 def __init__(self, name: str):
                   pass

               class Program(metaclass=ExtendedType):
                  @TestCase(name="Handler routine")
                  def Handler(self, args):
                    pass

               prog = Program()
               for method, attributes in prog.GetMethodsWithAttributes(predicate=TestCase):
                 pass

ArgParse
--------

.. grid:: 2

   .. grid-item::
      :columns: 6

      Defining commands, arguments or flags for a command line argument parser like :mod:`ArgParse` is done imperatively.
      This means code executed in-order defines how the parser will accept inputs. Then more user-defined code is needed
      to dispatch the collected and type-converted arguments to handler routines.

      In contrast, :mod:`pyTooling.Attributes.ArgParse` allows the definition of commands, arguments and flags as
      declarative code attached to handler routines using pyTooling's attributes. This allows for

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Traditional ArgParse

            .. code-block:: Python

               class Program:
                 def __init__(self):
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

      :mod:`pyTooling.CLIAbstraction` offers an abstraction layer and wrapper for command line programs, so they can be
      used easily in Python. All parameters like ``--value=42`` are implemented as argument classes on the executable.

   .. grid-item::
      :columns: 6

      .. code-block:: Python

         class Git(Executable):
           def __new__(cls, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
             cls._executableNames = {
               "Darwin": "git",
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
        current platform using APIs from ``sys``, ``platform``, ``os``, …. Unfortunately, none of the provided standard APIs
        offers a comprehensive answer. pyTooling provides a :ref:`CurrentPlatform <COMMON/CurrentPlatform>` singleton
        summarizing multiple platform APIs into a single class instance.
      * :ref:`Representations of version numbers <VERSIONING>`: While Python itself has a good versioning schema, there are no
        classes provided to abstract version numbers. pyTooling provides such representations following semantic versioning
        (SemVer) and calendar versioning (CalVer) schemes. It's provided by the :mod:`pyTooling.Versioning` module.

   .. grid-item::
      :columns: 6

      .. tab-set::

         .. tab-item:: Platform

            .. todo:: Needs example code

            .. code-block:: Python

               def

         .. tab-item:: SemanticVersion

            .. todo:: Needs example code

            .. code-block:: Python

               def

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

            .. todo:: Needs example code

            .. code-block:: Python

               pass

         .. tab-item:: TOML

            .. todo:: Needs example code

            .. code-block:: Python

               pass

         .. tab-item:: YAML

            .. todo:: Needs example code

            .. code-block:: Python

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
        |rarr| A directed graph implementation using a :class:`~pyTooling.Graph.Vertex` and an :class:`~pyTooling.Graph.Edge`
        class.
      * :ref:`Path data structure <STRUCT/Path>` |br|
        |rarr| To be documented.
      * :ref:`Finite State Machine data structure <STRUCT/StateMachine>` |br|
        |rarr| A data model for state machines using a :class:`~pyTooling.StateMachine.State` and a
        :class:`~pyTooling.StateMachine.Transition` class.
      * :ref:`Tree data structure <STRUCT/Tree>` |br|
        |rarr| A fast and simple implementation using a single :class:`~pyTooling.Tree.Node` class.

      .. #* :ref:`Scope data structure <STRUCT/Scope>` |br|
         |rarr| A fast and simple implementation using a single :class:`~pyTooling.Tree.Node` class.

   .. grid-item::
      :columns: 6

      .. tab-set::

          .. tab-item:: Graph

            .. todo:: Needs example code

             .. code-block:: Python

                pass

          .. tab-item:: Statemachine

            .. todo:: Needs example code

             .. code-block:: Python

                pass

          .. tab-item:: Tree

            .. todo:: Needs example code

             .. code-block:: Python

                pass

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
      :columns: 4

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
      :columns: 4

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

            .. todo:: Needs example code

            .. code-block:: Python

               def

         .. tab-item:: Slotted Class

            .. todo:: Needs example code

            .. code-block:: Python

               def

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

      .. todo:: Needs example code


Terminal
========

.. grid:: 2

   .. grid-item::
      :columns: 6

      .. todo:: Terminal helpers.

   .. grid-item::
      :columns: 6

      .. todo:: Needs example code

Timer
=====

.. grid:: 2

   .. grid-item::
      :columns: 6

      A :class:`~pyTooling.Timer.Timer` class to measure and accumulate code execution times.

   .. grid-item::
      :columns: 6

      .. todo:: Needs example code

Contributors
************

* `Patrick Lehmann <https://GitHub.com/Paebbels>`__ (Maintainer)
* `Sven Köhler <https://GitHub.com/skoehler>`__
* `Unai Martinez-Corral <https://GitHub.com/umarcor/>`__
* `and more... <https://GitHub.com/pyTooling/pyTooling/graphs/contributors>`__


License
*******

.. only:: html

   This Python package (source code) is licensed under `Apache License 2.0 <Code-License.html>`__. |br|
   The accompanying documentation is licensed under `Creative Commons - Attribution 4.0 (CC-BY 4.0) <Doc-License.html>`__.

.. only:: latex

   This Python package (source code) is licensed under **Apache License 2.0**. |br|
   The accompanying documentation is licensed under **Creative Commons - Attribution 4.0 (CC-BY 4.0)**.


------------------------------------

.. |docdate| date:: %b %d, %Y - %H:%M

.. only:: html

   This document was generated on |docdate|.

.. toctree::
   :caption: Overview
   :hidden:

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
   DataStructures/Graph
   DataStructures/Path/index
   DataStructures/StateMachine
   DataStructures/Tree

.. toctree::
   :caption: Decorators
   :hidden:

   Decorators

.. toctree::
   :caption: Exceptions
   :hidden:

   Exceptions

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

.. toctree::
   :caption: Timer
   :hidden:

   Timer

.. raw:: latex

   \part{References and Reports}

.. toctree::
   :caption: References and Reports
   :hidden:

   pyTooling/pyTooling
   Unittest Report ➚ <unittests/index>
   Coverage Report ➚ <coverage/index>
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
