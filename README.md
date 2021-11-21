[![Sourcecode on GitHub](https://img.shields.io/badge/pyTooling-pyTooling-323131.svg?logo=github&longCache=true)](https://GitHub.com/pyTooling/pyTooling)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling?logo=GitHub&label=code%20license)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/pyTooling/pyTooling?logo=GitHub&include_prereleases)](https://GitHub.com/pyTooling/pyTooling/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/pyTooling/pyTooling?logo=GitHub&include_prereleases)](https://GitHub.com/pyTooling/pyTooling/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/pyTooling/pyTooling?logo=GitHub)](https://GitHub.com/pyTooling/pyTooling/releases)
[![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/pyTooling?logo=librariesdotio)](https://GitHub.com/pyTooling/pyTooling/network/dependents)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/workflow/status/pyTooling/pyTooling/Unit%20Testing,%20Coverage%20Collection,%20Package,%20Release,%20Documentation%20and%20Publish?label=Pipeline&logo=GitHub%20Actions&logoColor=FFFFFF)](https://GitHub.com/pyTooling/pyTooling/actions/workflows/Pipeline.yml)
[![Codacy - Quality](https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/pyTooling/pyTooling)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/pyTooling/pyTooling)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/pyTooling/pyTooling?logo=Codecov)](https://codecov.io/gh/pyTooling/pyTooling)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyTooling?logo=librariesdotio)](https://libraries.io/github/pyTooling/pyTooling/sourcerank)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling?logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling?logo=PyPI&logoColor=FBE072)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling?logo=PyPI&logoColor=FBE072)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling?logo=librariesdotio)](https://libraries.io/github/pyTooling/pyTooling)
[![Requires.io](https://img.shields.io/requires/github/pyTooling/pyTooling)](https://requires.io/github/pyTooling/pyTooling/requirements/?branch=main)  
[![Documentation License](https://img.shields.io/badge/doc%20license-CC--BY%204.0-green?logo=readthedocs)](doc/Doc-License.rst)
[![Documentation - Read Now!](https://img.shields.io/badge/doc-read%20now%20%E2%9E%9A-blueviolet?logo=readthedocs)](https://pyTooling.GitHub.io/pyTooling)

# pyTooling

**pyTooling** is a powerful collection of arbitrary useful classes, decorators,
meta-classes and exceptions. It's useful for any Python-base project independent
if it's a library, framework or CLI tool.

## Introduction

*TODO*

## Package Details

### Common Classes

* [pyTooling.CallByRef.*](https://pyTooling.GitHub.io/pyTooling/CallByRef/)  
  Emulation of *call-by-reference* parameters.
* [pyTooling.Versioning.*](https://pyTooling.GitHub.io/pyTooling/Versioning/)  
  Class representations of semantic version (SemVer) and calendar version (CalVer) numbers.


### Decorators

* [export](https://pyTooling.GitHub.io/pyTooling/Decorators/Visibility.html#export)    
  Register the given function or class as publicly accessible in a module.


### Exceptions

* [EnvironmentException](https://pyTooling.GitHub.io/pyTooling/Exceptions/PredefinedExceptions.html#environmentexception)  
  ... is raised when an expected environment variable is missing.
* [PlatformNotSupportedException](https://pyTooling.GitHub.io/pyTooling/Exceptions/PredefinedExceptions.html#platformnotsupportedexception)  
  ... is raise if the platform is not supported.
* [NotConfiguredException](https://pyTooling.GitHub.io/pyTooling/Exceptions/PredefinedExceptions.html#notconfiguredexception)  
  ... is raise if the requested setting is not configured.


### Meta-Classes

* [Singleton](https://pyTooling.GitHub.io/pyTooling/MetaClasses/Singleton.html)  
  Allow only a single instance of a class.
* [Overloading](https://pyTooling.GitHub.io/pyTooling/MetaClasses/Overloading.html)  
  Overloading Allow method overloading in Python classes. Dispatch method calls based on method signatures (type annotations).

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
def func(param : CallByRefIntParam):
  param <<= param * 4

# call the function and pass the wrapper object
func(myInt)

print(myInt.value)
```


## Contributors

* [Patrick Lehmann](https://GitHub.com/Paebbels) (Maintainer)
* [and more...](https://GitHub.com/pyTooling/pyTooling/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).


-------------------------

SPDX-License-Identifier: Apache-2.0
