[![Sourcecode on GitHub](https://img.shields.io/badge/PyTooling-pyTooling-323131.svg?logo=github&longCache=true)](https://github.com/PyTooling/pyTooling)
[![Sourcecode License](https://img.shields.io/pypi/l/pyTooling?logo=GitHub&label=code%20license)](LICENSE.md)
[![GitHub tag (latest SemVer incl. pre-release)](https://img.shields.io/github/v/tag/PyTooling/pyTooling?logo=GitHub&include_prereleases)](https://github.com/PyTooling/pyTooling/tags)
[![GitHub release (latest SemVer incl. including pre-releases)](https://img.shields.io/github/v/release/PyTooling/pyTooling?logo=GitHub&include_prereleases)](https://github.com/PyTooling/pyTooling/releases/latest)
[![GitHub release date](https://img.shields.io/github/release-date/PyTooling/pyTooling?logo=GitHub)](https://github.com/PyTooling/pyTooling/releases)
[![Dependents (via libraries.io)](https://img.shields.io/librariesio/dependents/pypi/pyTooling?logo=librariesdotio)](https://github.com/PyTooling/pyTooling/network/dependents)  
[![GitHub Workflow - Build and Test Status](https://img.shields.io/github/workflow/status/PyTooling/pyTooling/Unit%20Testing,%20Coverage%20Collection,%20Package,%20Release,%20Documentation%20and%20Publish?label=Pipeline&logo=GitHub%20Actions&logoColor=FFFFFF)](https://github.com/PyTooling/pyTooling/actions/workflows/Pipeline.yml)
[![Codacy - Quality](https://img.shields.io/codacy/grade/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/PyTooling/pyTooling)
[![Codacy - Coverage](https://img.shields.io/codacy/coverage/8dc5205ba8b24e008f2287759096e181?logo=Codacy)](https://www.codacy.com/manual/PyTooling/pyTooling)
[![Codecov - Branch Coverage](https://img.shields.io/codecov/c/github/PyTooling/pyTooling?logo=Codecov)](https://codecov.io/gh/PyTooling/pyTooling)
[![Libraries.io SourceRank](https://img.shields.io/librariesio/sourcerank/pypi/pyTooling?logo=librariesdotio)](https://libraries.io/github/PyTooling/pyTooling/sourcerank)  
[![PyPI](https://img.shields.io/pypi/v/pyTooling?logo=PyPI&logoColor=FBE072)](https://pypi.org/project/pyTooling/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyTooling?logo=PyPI&logoColor=FBE072)
![PyPI - Status](https://img.shields.io/pypi/status/pyTooling?logo=PyPI&logoColor=FBE072)
[![Libraries.io status for latest release](https://img.shields.io/librariesio/release/pypi/pyTooling?logo=librariesdotio)](https://libraries.io/github/PyTooling/pyTooling)
[![Requires.io](https://img.shields.io/requires/github/PyTooling/pyTooling)](https://requires.io/github/PyTooling/pyTooling/requirements/?branch=main)  
[![Documentation License](https://img.shields.io/badge/doc%20license-CC--BY%204.0-green?logo=readthedocs)](LICENSE.md)
[![Documentation - Read Now!](https://img.shields.io/badge/doc-read%20now%20%E2%9E%94-blueviolet?logo=readthedocs)](https://pyTooling.github.io/pyTooling)

# pyTooling

A collection of classes, meta-classes and decorators for Python.

## Classes

### Exceptions

* An exception base-class to derive more powerful exceptions.
  * `ExceptionBase`
* Common exception classes:
  * `EnvironmentException`
  * `PlatformNotSupportedException`
  * `NotConfiguredException`


### Decorators

* `export`  
  Add a class defined in a module to the `__all__` array of a module.

  **Example**

  ```Python
  @export
  class MyClass:
    pass
  ```


### Metaclasses
* `Singleton`  
  Allow only a single instance of a class.  
  &rArr; See documentation of [pyTooling.Singleton](https://pyTooling.readthedocs.io/en/latest/Singleton.html)
* `Overloading`
  Allow method overloading in Python classes. Dispatch method calls based on
  method signatures (type annotations).  
  &rArr; See documentation of [pyTooling.Overloading](https://pyTooling.readthedocs.io/en/latest/Overloading.html)


### Common Classes

#### CallBy

Auxilary classes to implement call by reference.

Python does not allow a user to distinguish between *call-by-value* and *call-by-reference*
parameter passing. Python's standard types are passed by-value to a function or
method. Instances of a class are passed by-reference (pointer) to a function or
method.

By implementing a wrapper-class `CallByRefParam`, any type's value can be
passed by-reference. In addition, derived classes can offer additional methods
and operators for standard types like `int` or `bool`.


**Example**

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


#### Versioning

* `Version`  
  Representation of a version number.



## Contributors

* [Patrick Lehmann](https://github.com/PyTooling) (Maintainer)
* [and more...](https://github.com/PyTooling/pyTooling/graphs/contributors)


## License

This Python package (source code) licensed under [Apache License 2.0](LICENSE.md).  
The accompanying documentation is licensed under [Creative Commons - Attribution 4.0 (CC-BY 4.0)](doc/Doc-License.rst).


-------------------------

SPDX-License-Identifier: Apache-2.0
