[![Sourcecode on GitHub](https://img.shields.io/badge/pyTooling-pyTooling-63bf7f?longCache=true&style=flat-square&longCache=true&logo=GitHub)](https://GitHub.com/pyTooling/pyTooling)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling?longCache=true&style=flat-square&logo=Apache&label=code)](LICENSE.md)
[![Documentation](https://img.shields.io/website?longCache=true&style=flat-square&label=pyTooling.github.io%2FpyTooling&logo=GitHub&logoColor=fff&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url=https%3A%2F%2FpyTooling.github.io%2FpyTooling%2Findex.html)](https://pyTooling.github.io/pyTooling/)
[![Documentation License](https://img.shields.io/badge/doc-CC--BY%204.0-green?longCache=true&style=flat-square&logo=CreativeCommons&logoColor=fff)](LICENSE.md)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling/)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/actions/workflow/status/pyTooling/pyTooling/Pipeline.yml?branch=main&longCache=true&style=flat-square&label=build%20and%20test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://GitHub.com/pyTooling/pyTooling/actions/workflows/Pipeline.yml)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff)](https://libraries.io/github/pyTooling/pyTooling)
[![Codacy - Quality](https://img.shields.io/codacy/grade/08ef744c0b70490289712b02a7a4cebe?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/08ef744c0b70490289712b02a7a4cebe?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/pyTooling/pyTooling?longCache=true&style=flat-square&logo=Codecov)](https://codecov.io/gh/pyTooling/pyTooling)

<!--
[![Gitter](https://img.shields.io/badge/chat-on%20gitter-4db797?longCache=true&style=flat-square&logo=gitter&logoColor=e8ecef)](https://gitter.im/hdl/community)
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyTooling?longCache=true&style=flat-square&logo=GitHub)](https://github.com/pyTooling/pyTooling/network/dependents)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyTooling)](https://libraries.io/github/pyTooling/pyTooling/sourcerank)
-->

# pyTooling

**pyTooling** is a powerful collection of arbitrary useful abstract data models, missing classes, decorators, a new
performance boosting meta-class and enhanced exceptions. It also provides lots of helper functions e.g. to ease the
handling of package descriptions or to unify multiple existing APIs into a single API.

It's useful - if not even essential - for **any** Python-base project independent if it's a library, framework, CLI tool
or just a "script".

In addition, pyTooling provides a collection of [CI job templates for GitHub Actions](https://github.com/pyTooling/Actions).
This drastically simplifies GHA-based CI pipelines for Python projects.

## Package Details

### Attributes

The [pyTooling.Attributes] module offers the base implementation of *.NET-like attributes* realized with Python
decorators. The annotated and declarative data is stored as instances of Attribute classes in an additional field per
class, method or function.

The annotation syntax (decorator syntax) allows users to attach any structured data to classes, methods or functions. In
many cases, a user will derive a custom attribute from Attribute and override the __init__ method, so user-defined
parameters can be accepted when the attribute is constructed.

Later, classes, methods or functions can be searched for by querying the attribute class for attribute instance usage
locations (see example to the right). Another option for class and method attributes is declaring a classes using
pyTooling’s `ExtendedType` meta-class. Here the class itself offers helper methods for discovering annotated methods.

A `SimpleAttribute` class is offered accepting any positional and keyword parameters. In a more advanced use case, users
are encouraged to derive their own attribute class hierarchy from `Attribute`.


#### Use Cases

In general all classes, methods and functions can be annotated with additional meta-data. It depends on the application,
framework or library to decide if annotations should be applied imperatively as regular code or declaratively as
attributes via Python decorators.

**With this in mind, the following use-cases and ideas can be derived:**

* Describe a command line argument parser (like ArgParse) in a declarative form. |br|
  See [pyTooling.Attributes.ArgParse Package and Examples](https://pytooling.github.io/pyTooling/Attributes/ArgParse.html)
* Mark nested classes, so later when the outer class gets instantiated, these nested classes are indexed or
  automatically registered.  
  See [CLIAbstraction](https://pytooling.github.io/pyTooling/CLIAbstraction/index.html) &rarr; [CLIABS/CLIArgument]
* Mark methods in a class as test cases and classes as test suites, so test cases and suites are not identified based on
  a magic method name.  
  *Investigation ongoing / planned feature.*


#### Using `SimpleAttribute`

````Python
from pyTooling.Attributes import SimpleAttribute

@SimpleAttribute(kind="testsuite")
class MyClass:
  @SimpleAttribute(kind="testcase", id=1, description="Test and operator")
  def test_and(self):
    ...

  @SimpleAttribute(kind="testcase", id=2, description="Test xor operator")
  def test_xor(self):
    ...
````


### CLI Abstraction

[pyTooling.CLIAbstraction] offers an abstraction layer for command line programs, so they can be used easily in Python.
There is no need for manually assembling parameter lists or considering the order of parameters. All parameters like
`-v` or `--value=42` are described as [CommandLineArgument] instances on a [Program] class. Each argument class like
[ShortFlag] or [PathArgument] knows about the correct formatting pattern, character escaping, and if needed about
necessary type conversions. A program instance can be converted to an argument list suitable for [subprocess.Popen].

While a user-defined command line program abstraction derived from [Program] only
takes care of maintaining and assembling parameter lists, a more advanced base-class, called [Executable],
is offered with embedded [subprocess.Popen] behavior.

#### Design Goals

* Offer access to CLI programs as Python classes.
* Abstract CLI arguments (a.k.a. parameter, option, flag, ...) as members on such a Python class.
* Abstract differences in operating systems like argument pattern (POSIX: `-h` vs. Windows: `/h`), path delimiter
  signs (POSIX: `/` vs. Windows: `\`) or executable names.
* Derive program variants from existing programs.
* Assemble parameters as list for handover to [subprocess.Popen] with proper escaping and quoting.
* Launch a program with :class:[subprocess.Popen] and hide the complexity of Popen.
* Get a generator object for line-by-line output reading to enable postprocessing of outputs.


### Common Helper Functions

This is a set of useful [helper functions](https://pytooling.github.io/pyTooling/Common/index.html#common-helperfunctions):

* [getsizeof](https://pytooling.github.io/pyTooling/Common/index.html#getsizeof) calculates the "real" size of a data structure.
* [isnestedclass](https://pytooling.github.io/pyTooling/Common/index.html#isnestedclass) checks if a class is nested inside another class.
* [firstKey](https://pytooling.github.io/pyTooling/Common/index.html#firstkey), [firstValue](https://pytooling.github.io/pyTooling/Common/index.html#firstvalue), [firstPair](https://pytooling.github.io/pyTooling/Common/index.html#firstitem) get the firstItem key/value/item from an ordered dictionary.
* [mergedicts](https://pytooling.github.io/pyTooling/Common/index.html#mergedicts) merges multiple dictionaries into a new dictionary.
* [zipdicts](https://pytooling.github.io/pyTooling/Common/index.html#zipdicts) iterate multiple dictionaries simultaneously.


### Common Classes

* [Call-by-reference parameters](https://pytooling.github.io/pyTooling/Common/CallByRef.html): Python doesn't provide
  *call-by-reference parameters* for simple types.  
  This behavior can be emulated with classes provided by the `pyTooling.CallByRef` module.
* [Unified license names](https://pytooling.github.io/pyTooling/Common/Licensing.html): Setuptools, PyPI, and others
  have a varying understanding of license names.  
  The `pyTooling.Licensing` module provides *unified license names* as well as license name mappings or translations.
* [Unified platform and environment description](https://pytooling.github.io/pyTooling/Common/Platform.html): Python has
  many ways in figuring out the current platform using APIs from `sys`, `platform`, `os`, …. Unfortunately, none of the
  provided standard APIs offers a comprehensive answer. pyTooling provides a `CurrentPlatform` singleton summarizing
  multiple platform APIs into a single class instance.
* [Representations of version numbers](https://pytooling.github.io/pyTooling/Common/Versioning.html): While Python
  itself has a good versioning schema, there are no classes provided to abstract version numbers. pyTooling provides
  such representations following semantic versioning (SemVer) and calendar versioning (CalVer) schemes. It's provided by 
  the `pyTooling.Versioning` module.

### Configuration

Various file formats suitable for configuration information share the same features supporting: key-value pairs
(dictionaries), sequences (lists), and simple types like string, integer and float. pyTooling provides an
[abstract configuration file data model](https://pytooling.github.io/pyTooling/Configuration/index.html) supporting
these features. Moreover, concrete [configuration file format reader](https://pytooling.github.io/pyTooling/Configuration/FileFormats.html)
implementations are provided as well.

* [JSON configuration reader](https://pytooling.github.io/pyTooling/Configuration/JSON.html) for the JSON file format.
* [TOML configuration reader](https://pytooling.github.io/pyTooling/Configuration/TOML.html) &rarr; To be implemented.
* [YAML configuration reader](https://pytooling.github.io/pyTooling/Configuration/YAML.html) for the YAML file format.


### Data Structures

pyTooling also provides [fast and powerful data structures](https://pytooling.github.io/pyTooling/DataStructures/index.html)
offering object-oriented APIs:

* [Graph data structure](https://pytooling.github.io/pyTooling/DataStructures/Graph.html)  
  &rarr; A directed graph implementation using a `Vertex` and an `Edge` class.
* [Path data structure](https://pytooling.github.io/pyTooling/DataStructures/Path/index.html)  
  &rarr; To be documented.
* [Finite State Machine data structure](https://pytooling.github.io/pyTooling/DataStructures/StateMachine.html)  
  &rarr; A data model for state machines using a `State` and a `Transition` class.
* [Tree data structure](https://pytooling.github.io/pyTooling/DataStructures/Tree.html)  
  &rarr; A fast and simple implementation using a single `Node` class.


### Decorators

* [Abstract Methods](https://pytooling.github.io/pyTooling/MetaClasses.html#meta-abstract)
  * Methods marked with `abstractmethod` are abstract and need to be overwritten in a derived class.  
    An *abstract method* might be called from the overwriting method.
  * Methods marked with `mustoverride` are abstract and need to be overridden in a derived class.  
    It's not allowed to call a *mustoverride method*.
* [Documentation](https://pytooling.github.io/pyTooling/Decorators.html#deco-documentation)
  * Copy the doc-string from given base-class via `InheritDocString`.
* [Visibility](https://pytooling.github.io/pyTooling/Decorators.html#deco-visibility)
  * Register the given function or class as publicly accessible in a module via `export`.
* [Documentation](https://pyTooling.GitHub.io/pyTooling/Decorators.html#documentation)
  * [`@InheritDocString`](https://pyTooling.GitHub.io/pyTooling/Decorators.html#inheritdocstring)  
    &rarr; Copy the doc-string from given base-class.
* [Visibility](https://pyTooling.GitHub.io/pyTooling/Decorators.html#visibility)
  * [`@export`](https://pyTooling.GitHub.io/pyTooling/Decorators.html#export)  
    &rarr; Register the given function or class as publicly accessible in a module.


### Exceptions

* [EnvironmentException](https://pyTooling.GitHub.io/pyTooling/Exceptions.html#environmentexception)  
  ... is raised when an expected environment variable is missing.
* [PlatformNotSupportedException](https://pyTooling.GitHub.io/pyTooling/Exceptions.html#platformnotsupportedexception)  
  ... is raise if the platform is not supported.
* [NotConfiguredException](https://pyTooling.GitHub.io/pyTooling/Exceptions.html#notconfiguredexception)  
  ... is raise if the requested setting is not configured.


### Meta-Classes

pyTooling provides an [enhanced meta-class](https://pytooling.github.io/pyTooling/MetaClasses.html) called
`ExtendedType`. This meta-classes allows to implement
[abstract methods](https://pytooling.github.io/pyTooling/MetaClasses.html#abstract-method),
[singletons](https://pytooling.github.io/pyTooling/MetaClasses.html#singleton),
[slotted types](https://pytooling.github.io/pyTooling/MetaClasses.html#slotted-type) and combinations thereof.

`class MyClass(metaclass=ExtendedType):`
  A class definition using that meta-class can implement
  [abstract methods](https://pytooling.github.io/pyTooling/MetaClasses.html#abstract-method) using decorators
  `@abstractmethod` or `@mustoverride`.

`class MyClass(metaclass=ExtendedType, singleton=True):`
  A class defined with enabled [singleton](https://pytooling.github.io/pyTooling/MetaClasses.html#singleton) behavior
  allows only a single instance of that class to exist. If another instance is going to be created, a previously cached
  instance of that class will be returned.

`class MyClass(metaclass=ExtendedType, slots=True):`
  A class defined with enabled [slots](https://pytooling.github.io/pyTooling/MetaClasses.html#slotted-type) behavior
  stores instance fields in slots. The meta-class, translates all type-annotated fields in a class definition into
  slots. Slots allow a more efficient field storage and access compared to dynamically stored and accessed fields hosted
  by `__dict__`. This improves the memory footprint as well as the field access performance of all class instances. This
  behavior is automatically inherited to all derived classes.

`class MyClass(ObjectWithSlots):`
  A class definition deriving from `ObjectWithSlots` will bring the slotted type behavior to that class and all derived
  classes.


### Packaging

A set of helper functions to describe a Python package for setuptools.

* Helper Functions:
  * `loadReadmeFile`  
    Load a `README.md` file from disk and provide the content as long description for setuptools.
  * `loadRequirementsFile`  
    Load a `requirements.txt` file from disk and provide the content for setuptools.
  * `extractVersionInformation`  
    Extract version information from Python source files and provide the data to setuptools.
* Package Descriptions
  * `DescribePythonPackage`  
    tbd
  * `DescribePythonPackageHostedOnGitHub`  
    tbd


### Terminal

A set of helpers to implement a text user interface (TUI) in a terminal.

#### Features

* Colored command line outputs based on `colorama`.
* Message classification in `fatal`, `error`, `warning`, `normal`, `quiet`, ...
* Get information like terminal dimensions from underlying terminal window.


#### Simple Terminal Application

This is a minimal terminal application example which inherits from `LineTerminal`.

```python
from pyTooling.TerminalUI import TerminalApplication

class Application(TerminalApplication):
  def __init__(self) -> None:
    super().__init__()

  def run(self):
    self.WriteNormal("This is a simple application.")
    self.WriteWarning("This is a warning message.")
    self.WriteError("This is an error message.")

# entry point
if __name__ == "__main__":
  Application.CheckPythonVersion((3, 6, 0))
  app = Application()
  app.run()
  app.Exit()
```

### Stopwatch

*tbd*

## Examples

### `@export` Decorator

```Python
from pyTooling.Decorators import export

@export
class MyClass:
  pass
```

### `CallByRefIntParam`

```Python
from pyTooling.CallByRef import CallByRefIntParam

# define a call-by-reference parameter for integer values
myInt = CallByRefIntParam(3)

# a function using a call-by-reference parameter
def func(param: CallByRefIntParam):
  param <<= param * 4

# call the function and pass the wrapper object
func(myInt)

print(myInt.Value)
```


## Contributors

* [Patrick Lehmann](https://GitHub.com/Paebbels) (Maintainer)
* [Sven Köhler](https://GitHub.com/skoehler)
* [Unai Martinez-Corral](https://github.com/umarcor)
* [and more...](https://GitHub.com/pyTooling/pyTooling/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).


-------------------------

SPDX-License-Identifier: Apache-2.0
