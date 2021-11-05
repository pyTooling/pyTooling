[![Sourcecode on GitHub](https://img.shields.io/badge/Paebbels-pyMetaClasses-323131.svg?logo=github&longCache=true)](https://github.com/Paebbels/pyMetaClasses)
[![Sourcecode License](https://img.shields.io/pypi/l/pyMetaClasses?logo=GitHub&label=code%20license)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/Paebbels/pyMetaClasses?logo=GitHub&include_prereleases)](https://github.com/Paebbels/pyMetaClasses/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/Paebbels/pyMetaClasses?logo=GitHub&include_prereleases)](https://github.com/Paebbels/pyMetaClasses/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/Paebbels/pyMetaClasses?logo=GitHub)](https://github.com/Paebbels/pyMetaClasses/releases)
[![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/pyMetaClasses?logo=librariesdotio)](https://github.com/Paebbels/pyMetaClasses/network/dependents)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/workflow/status/Paebbels/pyMetaClasses/Unit%20Testing,%20Coverage%20Collection,%20Package,%20Release,%20Documentation%20and%20Publish?label=Pipeline&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/Paebbels/pyMetaClasses/actions/workflows/Pipeline.yml)
[![Codacy - Quality](https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/Paebbels/pyMetaClasses)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/Paebbels/pyMetaClasses)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/Paebbels/pyMetaClasses?logo=Codecov)](https://codecov.io/gh/Paebbels/pyMetaClasses)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyMetaClasses?logo=librariesdotio)](https://libraries.io/github/Paebbels/pyMetaClasses/sourcerank)  
[![PyPI](https://img.shields.io/pypi/v/pyMetaClasses?logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyMetaClasses/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyMetaClasses?logo=PyPI&logoColor=FBE072)
![PyPI - Status](https://img.shields.io/pypi/status/pyMetaClasses?logo=PyPI&logoColor=FBE072)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyMetaClasses?logo=librariesdotio)](https://libraries.io/github/Paebbels/pyMetaClasses)
[![Requires.io](https://img.shields.io/requires/github/Paebbels/pyMetaClasses)](https://requires.io/github/Paebbels/pyMetaClasses/requirements/?branch=main)  
[![Read the Docs](https://img.shields.io/readthedocs/pymetaclasses?label=ReadTheDocs&logo=readthedocs)](https://pyMetaClasses.readthedocs.io/)
[![Documentation License](https://img.shields.io/badge/doc%20license-CC--BY%204.0-green?logo=readthedocs)](LICENSE.md)
[![Documentation - Read Now!](https://img.shields.io/badge/doc-read%20now%20%E2%9E%94-blueviolet?logo=readthedocs)](https://pyMetaClasses.readthedocs.io/)

# pyTooling

A collection of MetaClasses for Python.

## Classes

### CallBy

Auxilary classes to implement call by reference.

Python does not allow a user to distinguish between *call-by-value* and *call-by-reference*
parameter passing. Python's standard types are passed by-value to a function or
method. Instances of a class are passed by-reference (pointer) to a function or
method.

By implementing a wrapper-class `CallByRefParam`, any type's value can be
passed by-reference. In addition, derived classes can offer additional methods
and operators for standard types like `int` or `bool`.


#### Example

```Python
# define a call-by-reference parameter for integer values
myInt = CallByRefIntParam()

# a function using a call-by-reference parameter
def func(param : CallByRefIntParam):
  param <<= 3

# call the function and pass the wrapper object
func(myInt)

print(myInt.value)
```

### Decorators

* `export`  
  Add a class defined in a module to the `__all__` array of a module.

#### Example

```Python
@export
class MyClass:
	pass
```



### Exceptions

An exception base-class to derive more powerful exceptions.

### Metaclasses
* `Singleton`  
  Allow only a single instance of a class.  
  &rArr; See documentation of [pyMetaClasses.Singleton](https://pymetaclasses.readthedocs.io/en/latest/Singleton.html)
* `Overloading`
  Allow method overloading in Python classes. Dispatch method calls based on
  method signatures (type annotations).  
  &rArr; See documentation of [pyMetaClasses.Overloading](https://pymetaclasses.readthedocs.io/en/latest/Overloading.html)

### Versioning

* `Version`  
  Representation of a version number.

## Contributors

* [Patrick Lehmann](https://github.com/Paebbels) (Maintainer)
* [and more...](https://github.com/Paebbels/pyMetaClasses/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).


-------------------------

SPDX-License-Identifier: Apache-2.0
