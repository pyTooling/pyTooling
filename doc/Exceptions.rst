.. _EXCEPTION:

Overview
########

.. #contents:: Table of Contents
   :depth: 2

The :mod:`pyTooling.Exceptions` package provides the base-classes every other exception in ``pyTooling`` derives
from, and a small set of predefined exceptions for situations that occur in almost every application: a missing
environment variable, an unsupported platform, an unconfigured setting, an invalid configuration, and an optional
dependency that was not installed.

Packages and frameworks building on ``pyTooling`` are meant to derive from these rather than from
:exc:`Exception <python:Exception>` directly, so an application can catch everything raised by its stack with a
single clause.

.. note::

   Exception classes carry the suffix ``***Error``, following :pep:`8`: *"you should use the suffix `Error` on your
   exception names (if the exception actually is an error)"*. The suffix ``***Exception`` is reserved for a
   package's own base-exception — :exc:`ToolingException` here.

   The former names (:pycode:`ConfigurationException`, :pycode:`MissingDependencyException`, …) remain available as
   deprecated aliases and are removed in ``v10.0.0``.


.. _EXCEPTION/Base:

Exception Base Classes
######################


ExceptionBase
*************

The :exc:`ExceptionBase` is the base-class for all exceptions in ``pyTooling`` as well as derived packages and
frameworks.

It keeps the message in :pycode:`self.message` and renders it through :meth:`~object.__str__`, and it adds two
read-only properties for the notes attached with :meth:`~BaseException.add_note`:

* :pycode:`HasNotes` — whether any note is attached. :pycode:`__notes__` only exists once the first note was added,
  so testing this property is safer than testing the attribute.
* :pycode:`Notes` — the attached notes as a tuple, empty when there are none.

.. code-block:: Python

   from pyTooling.Exceptions import ExceptionBase

   class MyPackageError(ExceptionBase):
     """Base-exception of all exceptions raised by 'myPackage'."""

.. attention::

   :exc:`ExceptionBase` does not forward its message to :meth:`Exception.__init__ <python:BaseException>`, so
   :pycode:`ex.args` is empty while :pycode:`str(ex)` returns the message. Code reading :pycode:`ex.args[0]` has to
   read :pycode:`str(ex)` instead.


ToolingException
****************

The :exc:`ToolingException` is the base-exception for errors raised by ``pyTooling``'s *own* features — the
package-level bases such as :exc:`~pyTooling.Graph.GraphError` and :exc:`~pyTooling.Tree.TreeError` derive from it.

It is the one class that keeps the ``***Exception`` suffix, because it names a package rather than an error.
Applications deriving their own hierarchy use :exc:`ExceptionBase`; :exc:`ToolingException` marks *"this came out
of pyTooling itself"*.


.. _EXCEPTION/Predefined:

Predefined Exceptions
#####################

Predefined exceptions of ``pyTooling.Exceptions``.

.. rubric:: Inheritance diagram:

.. inheritance-diagram:: pyTooling.Exceptions
   :parts: 1


EnvironmentVariableError
************************

The :exc:`EnvironmentVariableError` is raised when an environment variable the program depends on is not set.

Use it where the variable is *required*: a program that cannot proceed without ``JAVA_HOME`` should say so once, by
name, instead of failing later with a path error that does not mention the variable at all.

.. code-block:: Python

   from os import environ
   from pyTooling.Exceptions import EnvironmentVariableError

   if (javaHome := environ.get("JAVA_HOME")) is None:
     raise EnvironmentVariableError("Environment variable 'JAVA_HOME' is not set.")

.. hint::

   Until ``v9.0.0`` this class was called ``EnvironmentException``. It was **not** renamed to ``EnvironmentError``,
   because that name is a builtin — a deprecated alias of :exc:`OSError <python:OSError>` — and would have shadowed
   it on import.


ConfigurationError
******************

The :exc:`ConfigurationError` is raised when a configuration is invalid: an unknown key, a value of the wrong type,
a setting that contradicts another one.

It is the base-exception for configuration problems in ``pyTooling`` **and in packages building on it**, so an
application reading configuration from several sources can catch them all with one clause instead of one per
package. :mod:`pyTooling.Configuration` derives :exc:`~pyTooling.Configuration.KeyNotFoundError`,
:exc:`~pyTooling.Configuration.UnsupportedValueTypeError`, :exc:`~pyTooling.Configuration.InterpolationError` and
:exc:`~pyTooling.Configuration.PathExpressionError` from it.

Attach the details as notes rather than folding them into the message — the value that was rejected, the file it
came from, and the values that would have been accepted are three separate facts:

.. code-block:: Python

   from pyTooling.Exceptions import ConfigurationError

   ex = ConfigurationError(f"Unknown log level '{value}'.")
   ex.add_note(f"Configuration file: {path}")
   ex.add_note(f"Allowed values: {', '.join(levels)}")
   raise ex


PlatformNotSupportedError
*************************

The :exc:`PlatformNotSupportedError` is raised when the program is running on a platform it has no implementation
for — a Windows-only registry lookup on Linux, a ``/proc`` reader on macOS.

Raise it where the branch would otherwise fall through silently, so the message names the platform instead of
leaving a :exc:`NameError <python:NameError>` further down:

.. code-block:: Python

   from pyTooling.Common import CurrentPlatform
   from pyTooling.Exceptions import PlatformNotSupportedError

   if CurrentPlatform.IsNativeWindows:
     ...
   elif CurrentPlatform.IsNativeLinux:
     ...
   else:
     raise PlatformNotSupportedError(f"Platform '{CurrentPlatform}' is not supported.")

.. seealso::

   :mod:`pyTooling.Platform`
      |rarr| Detecting the current platform, and its own
      :exc:`~pyTooling.Platform.UnknownPlatformError` for a platform that could not be identified at all.


NotConfiguredError
******************

The :exc:`NotConfiguredError` is raised when a setting that has no default was never configured — the program knows
the setting exists, and knows it has no value.

It differs from :exc:`ConfigurationError` in *what went wrong*: a configuration error means a value was given and
rejected, while this one means no value was given at all.

.. code-block:: Python

   from pyTooling.Exceptions import NotConfiguredError

   if self._installationDirectory is None:
     raise NotConfiguredError("Installation directory of tool 'GHDL' is not configured.")


MissingDependencyError
**********************

The :exc:`MissingDependencyError` is raised when an *optional* dependency is not installed. Unlike the other
predefined exceptions it derives from :exc:`ImportError <python:ImportError>`, so an ``except ImportError`` around
an optional import still catches it.

Some modules need a package ``pyTooling`` does not install by default. Importing such a module without its
dependency raises this exception, and it carries what to install and which extra provides it:

.. code-block:: Python

   from pyTooling.Exceptions import MissingDependencyError

   try:
     from ruamel.yaml import YAML
   except ImportError as ex:  # pragma: no cover
     raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex

:class:`~pyTooling.TerminalUI.TerminalApplication` prints it with
:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.PrintMissingDependencyException`, which names the package and
the command that installs it — and, unlike the other exception printers, does *not* invite a bug report, because
nothing is wrong with the program.


OverloadResolutionError
***********************

The :exc:`OverloadResolutionError` is raised when no overload of a dispatched method matches the given arguments.
It derives from :exc:`Exception <python:Exception>` directly, because it reports a call that cannot be resolved
rather than a failure inside a feature.

.. seealso::

   Base exception class :exc:`ExceptionBase`
      Base class for all exceptions.
   Base exception class :exc:`ToolingException`
      Base class for exceptions raised by pyTooling itself.
