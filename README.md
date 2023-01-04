[![Sourcecode on GitHub](https://img.shields.io/badge/pyTooling-pyTooling-63bf7f.svg?longCache=true&style=flat-square&longCache=true&logo=GitHub)](https://GitHub.com/pyTooling/pyTooling)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling?longCache=true&style=flat-square&logo=Apache&label=code)](LICENSE.md)
[![Documentation](https://img.shields.io/website?longCache=true&style=flat-square&label=pyTooling.github.io%2FpyTooling&logo=GitHub&logoColor=fff&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url=https%3A%2F%2FpyTooling.github.io%2FpyTooling%2Findex.html)](https://pyTooling.github.io/pyTooling/)
[![Documentation License](https://img.shields.io/badge/doc-CC--BY%204.0-green?longCache=true&style=flat-square&logo=CreativeCommons&logoColor=fff)](LICENSE.md)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling/)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/actions/workflow/status/pyTooling/pyTooling/Pipeline.yml?branch=main&longCache=true&style=flat-square&label=Build%20and%20test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://GitHub.com/pyTooling/pyTooling/actions/workflows/Pipeline.yml)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff)](https://libraries.io/github/pyTooling/pyTooling)
[![Codacy - Quality](https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/pyTooling/pyTooling?longCache=true&style=flat-square&logo=Codecov)](https://codecov.io/gh/pyTooling/pyTooling)

![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/pyTooling/pyTooling/Pipeline.yml?branch=main)

<!--
[![Gitter](https://img.shields.io/badge/chat-on%20gitter-4db797.svg?longCache=true&style=flat-square&logo=gitter&logoColor=e8ecef)](https://gitter.im/hdl/community)
[![Dependent repos (via libraries.io)](https://img.shields.io/librariesio/dependent-repos/pypi/pyTooling?longCache=true&style=flat-square&logo=GitHub)](https://github.com/pyTooling/pyTooling/network/dependents)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyTooling)](https://libraries.io/github/pyTooling/pyTooling/sourcerank)
-->

# pyTooling

**pyTooling** is a powerful collection of arbitrary useful abstract data models, classes, decorators, meta-classes and
exceptions. It also provides lots of helper functions e.g. to ease the handling of package descriptions.

It's useful for **any** Python-base project independent if it's a library, framework or CLI tool.

## Introduction

**pyTooling** is a basic collection of powerful helpers needed by almost any Python project. More specialized helpers
can be found in sub-namespaces like:

* [pyTooling.CLIAbstraction](https://github.com/pyTooling/pyTooling.CLIAbstraction)
* [pyTooling.TerminalUI](https://github.com/pyTooling/pyTooling.TerminalUI)

In addition, pyTooling provides a collection of CI job templates for GitHub Actions. This drastically simplifies
GHA-based CI pipelines for Python projects.

## Package Details

### Common Helper Functions

This is a set of useful [helper functions](https://pytooling.github.io/pyTooling/Common/index.html#common-helperfunctions):

* [getsizeof](https://pytooling.github.io/pyTooling/Common/index.html#getsizeof) calculates the "real" size of a data structure.
* [isnestedclass](https://pytooling.github.io/pyTooling/Common/index.html#isnestedclass) checks if a class is nested inside another class.
* [mergedicts](https://pytooling.github.io/pyTooling/Common/index.html#mergedicts) merges multiple dictionaries into a new dictionary.
* [zipdicts](https://pytooling.github.io/pyTooling/Common/index.html#zipdicts) iterate multiple dictionaries simultaneously.


### Common Classes

* Python doesn't provide [call-by-reference parameters](https://pytooling.github.io/pyTooling/Common/CallByRef.html) for
  simple types. This behavior can be emulated with classes provided by the `pyTooling.CallByRef` module.
* Setuptools, PyPI, and others have a varying understanding of license names. The `pyTooling.Licensing` module
  provides [unified license names](https://pytooling.github.io/pyTooling/Common/Licensing.html) as well as license name
  mappings or translations.
* Python has many ways in figuring out the current platform using APIs from `sys`, `platform`, `os`, ….
  Unfortunately, none of the provided standard APIs offers a comprehensive answer. pyTooling provides a
  [unified platform and environment description](https://pytooling.github.io/pyTooling/Common/Platform.html) by
  summarizing multiple platform APIs into a single class instance.
* While Python itself has a good versioning schema, there are no classes provided to abstract version numbers. pyTooling
  provides such a [representations of version numbers](https://pytooling.github.io/pyTooling/Common/Versioning.html)
  following semantic versioning (SemVer) and calendar versioning (CalVer) schemes. It's provided by the
  `pyTooling.Versioning` module.

### Configuration

Various file formats suitable for configuration information share the same features supporting: key-value pairs
(dictionaries), sequences (lists), and simple types like string, integer and float. pyTooling provides an
[abstract configuration file data model](https://pytooling.github.io/pyTooling/Configuration/index.html) supporting
these features. Moreover, concrete [configuration file format reader](https://pytooling.github.io/pyTooling/Configuration/FileFormats.html)
implementations are provided as well.

* [JSON configuration reader](https://pytooling.github.io/pyTooling/Configuration/JSON.html) &rarr; To be implemented.
* [TOML configuration reader](https://pytooling.github.io/pyTooling/Configuration/TOML.html) &rarr; To be implemented.
* [YAML configuration reader](https://pytooling.github.io/pyTooling/Configuration/YAML.html) for the YAML file format.


### Data Structures

pyTooling also provides fast and powerful data structures offering object-oriented APIs:

* [Graph data structure](https://pytooling.github.io/pyTooling/DataStructures/Graph.html)  
  &rarr; A directed graph implementation using a `Vertex` and `Edge`
  class.
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

`class MyClass(metaclass=ExtendedType, useSlots=True):`
  A class defined with enabled [useSlots](https://pytooling.github.io/pyTooling/MetaClasses.html#slotted-type) behavior
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
* [and more...](https://GitHub.com/pyTooling/pyTooling/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).


-------------------------

SPDX-License-Identifier: Apache-2.0
