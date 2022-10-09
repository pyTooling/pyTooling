[![Sourcecode on GitHub](https://img.shields.io/badge/pyTooling-pyTooling-63bf7f.svg?longCache=true&style=flat-square&longCache=true&logo=GitHub)](https://GitHub.com/pyTooling/pyTooling)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling?longCache=true&style=flat-square&logo=Apache&label=code)](LICENSE.md)
[![Documentation](https://img.shields.io/website?longCache=true&style=flat-square&label=pyTooling.github.io%2FpyTooling&logo=GitHub&logoColor=fff&up_color=blueviolet&up_message=Read%20now%20%E2%9E%9A&url=https%3A%2F%2FpyTooling.github.io%2FpyTooling%2Findex.html)](https://pyTooling.github.io/pyTooling/)
[![Documentation License](https://img.shields.io/badge/doc-CC--BY%204.0-green?longCache=true&style=flat-square&logo=CreativeCommons&logoColor=fff)](LICENSE.md)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling/)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling?longCache=true&style=flat-square&logo=PyPI&logoColor=FBE072)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/workflow/status/pyTooling/pyTooling/Pipeline/main?longCache=true&style=flat-square&label=Build%20and%20test&logo=GitHub%20Actions&logoColor=FFFFFF)](https://GitHub.com/pyTooling/pyTooling/actions/workflows/Pipeline.yml)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling?longCache=true&style=flat-square&logo=Libraries.io&logoColor=fff)](https://libraries.io/github/pyTooling/pyTooling)
[![Codacy - Quality](https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?longCache=true&style=flat-square&logo=Codacy)](https://www.codacy.com/gh/pyTooling/pyTooling)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/pyTooling/pyTooling?longCache=true&style=flat-square&logo=Codecov)](https://codecov.io/gh/pyTooling/pyTooling)

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

* [pyTooling.CallByRef.*](https://pyTooling.GitHub.io/pyTooling/CallByRef/)  
  Emulation of *call-by-reference* parameters.
* [pyTooling.Versioning.*](https://pyTooling.GitHub.io/pyTooling/Versioning/)  
  Class representations of semantic version (SemVer) and calendar version (CalVer) numbers.


### Data Structures

pyTooling also provides fast and powerful data structures offering object-oriented APIs:

* Trees
  * [Tree data structure](https://pyTooling.GitHub.io/pyTooling/DataStructures/Tree.html)  
    &rarr; A fast and simple implementation using a single `Node` class.


### Decorators

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

* [Overloading](https://pyTooling.GitHub.io/pyTooling/MetaClasses/Overloading.html)  
  &rarr; `Overloading` allows method overloading in Python classes. It dispatches method calls based on method signatures
  (type annotations).
* [Singleton](https://pyTooling.GitHub.io/pyTooling/MetaClasses/Singleton.html)  
  &rarr; A class created from meta-class `Singleton` allows only a single instance to exist. If a further instance is tried to 
  be created, a cached instance will be returned.
* [SlottedType](https://pyTooling.GitHub.io/pyTooling/MetaClasses/SlottedType.html)    
  &rarr; All type-annotated fields in a class get stored in a slot rather than in `__dict__`. This improves the memory
  footprint as well as the field access performance of all class instances. The behavior is automatically inherited to
  all derived classes.


### Packaging

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
