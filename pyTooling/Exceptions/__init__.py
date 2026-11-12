# ==================================================================================================================== #
#                                                                                                                      #
#             _____           _ _               _____                    _   _                                         #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  | ____|_  _____ ___ _ __ | |_(_) ___  _ __  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | |  _| \ \/ / __/ _ \ '_ \| __| |/ _ \| '_ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |___ >  < (_|  __/ |_) | |_| | (_) | | | \__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_____/_/\_\___\___| .__/ \__|_|\___/|_| |_|___/                        #
# |_|    |___/                          |___/                     |_|                                                  #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
A common set of missing exceptions in Python.

.. hint::

   See :ref:`high-level help <EXCEPTION>` for explanations and usage examples.

.. seealso::

   :mod:`pyTooling.Warning`
      |rarr| Warnings, which are collected instead of raised.
   :mod:`pyTooling.MetaClasses`
      |rarr| The exceptions raised for a class that violates the meta-class' rules.
"""
from typing               import ClassVar, Iterable, Any, Optional as Nullable

from pyTooling.Common     import getFullyQualifiedName
from pyTooling.Decorators import export, readonly


@export
def addNoteWithItemList(
	ex:        BaseException,
	message:   str,
	items:     Iterable[Any],
	*,
	indent:    str = "  ",
	separator: str = ", ",
	maxWidth:  int = 100
) -> None:
	"""
	Add a message as a note to the exception. The iterables items are added as a coma separated list. If the list gets too
	long, remaining items will be continued in addition notes.

	:param ex:        Exception to attach the note to.
	:param message:   The message of the note.
	:param items:     An iterable of items to add to the note.
	:param indent:    Optional, the indentation of the additional notes.
	:param separator: Optional, separator between items.
	:param maxWidth:  Optional, the maximum width of the attached notes.
	"""
	note = message
	sep = ""

	for item in items:
		if len(note) + len(newItem := f"{sep}{item}") <= maxWidth:
			note += newItem
			sep = separator
		else:
			ex.add_note(note)

			note = f"{indent}{item}"
			sep = separator

	ex.add_note(note)


@export
class OverloadResolutionError(Exception):
	"""
	The exception is raised, when no matching overloaded method was found.

	.. attention::

	   Method overloading is not implemented yet - the ``overloadable`` decorator and the dispatching machinery are
	   commented out in :mod:`pyTooling.MetaClasses`. Nothing raises this exception today; it is declared so the feature
	   has its exception when it arrives.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


@export
class ExceptionBase(Exception):
	"""Base exception derived from :exc:`Exception <python:Exception>` for all custom exceptions."""

	def __init__(self, message: str = "") -> None:
		"""
		ExceptionBase initializer.

		:param message: Optional, the exception message.
		"""
		super().__init__(message)

	@readonly
	def Message(self) -> str:
		"""
		Read-only property to return the exception's message (first element of :attr:`~BaseException.args`).

		:returns: The exception's message.
		"""
		return self.args[0]

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()

	# @DocumentMemberAttribute(False)
	# @MethodAlias(pyExceptions.with_traceback)
	# def with_traceback(self): pass


@export
class EnvironmentVariableError(ExceptionBase):
	"""The exception is raised when an expected environment variable is missing."""


@export
class ConfigurationError(ExceptionBase):
	"""
	The exception is raised when a configuration is invalid.

	It is the base-exception for configuration problems in pyTooling **and in packages building on it**, so an
	application reading configuration files from several sources can catch them all with one clause instead of one
	per package. :mod:`pyTooling.Configuration` derives its own exceptions from it.

	Attach the details as notes rather than folding them into the message - the value that was rejected, the file it
	came from, the values that would have been accepted:

	.. code-block:: Python

	   ex = ConfigurationError(f"Unknown log level '{value}'.")
	   ex.add_note(f"Configuration file: {path}")
	   ex.add_note(f"Allowed values: {', '.join(levels)}")
	   raise ex
	"""


@export
class PlatformNotSupportedError(ExceptionBase):
	"""The exception is raise if the platform is not supported."""


@export
class NotConfiguredError(ExceptionBase):
	"""The exception is raise if the requested setting is not configured."""


@export
class ToolingException(Exception):
	"""The exception is raised by pyTooling internal features."""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()


@export
class MissingDependencyError(ToolingException, ImportError):
	"""
	The exception is raised when an optional dependency of pyTooling is not installed.

	Some modules need a package pyTooling doesn't install by default. Importing such a module without its dependency
	raises this exception instead of the bare :exc:`ImportError`, so the message names the extra that installs it.

	The exception is a :exc:`ToolingException` and an :exc:`ImportError`: a caller guarding an optional import catches
	:exc:`ImportError`, a caller handling pyTooling's own errors catches :exc:`ToolingException`. It carries the missing
	package, the extra and the package providing the extra as :attr:`Dependency`, :attr:`Extra` and :attr:`Package`;
	:attr:`ImportError.name` is the missing package too.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      try:
	        from ruamel.yaml import YAML
	      except ImportError as ex:
	        raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex

	A package building on pyTooling raises it for its own optional dependencies too. It names itself as the package
	providing the extra, e.g. ``VHDLDomain`` with its extra ``diagram``:

	.. admonition:: ``example.py``

	   .. code-block:: python

	      try:
	        from matplotlib import pyplot
	      except ImportError as ex:
	        raise MissingDependencyError(dependency="matplotlib", extra="diagram", package="VHDLDomain") from ex
	"""

	EXIT_CODE:   ClassVar[int] = 242  #: Exit code an application should use when an optional dependency is missing.

	_dependency: str            #: Field storing the name of the package that is not installed.
	_extra:      Nullable[str]  #: Field storing the name of the extra installing that package.
	_package:    str            #: Field storing the name of the package providing the extra.

	def __init__(
		self,
		message:    Nullable[str] = None,
		/, *,
		dependency: str,
		extra:      Nullable[str] = None,
		package:    str = "pyTooling"
	) -> None:
		"""
		Initialize a new missing-dependency error and attach the installation hint as a note.

		:param message:     Optional, the exception message. |br|
		                    When omitted, it is derived from ``dependency`` - every raising site says the same thing, so
		                    there is nothing for the caller to add.
		:param dependency:  Name of the package that is not installed.
		:param extra:       Optional, name of the extra installing that package. |br|
		                    When given, the note offers ``<package>[<extra>]`` next to the package itself.
		:param package:     Optional, name of the package providing the extra. Default: ``"pyTooling"``. |br|
		                    A package building on pyTooling passes its own name for its own extras.
		:raises ValueError: If parameter 'package' is None.
		:raises TypeError:  If parameter 'package' is not of type :class:`str`.
		:raises ValueError: If parameter 'package' is empty.
		"""
		super().__init__(
			message if message is not None else f"Optional dependency '{dependency}' not installed.",
			name=dependency
		)

		if package is None:
			raise ValueError("Parameter 'package' is None.")
		elif not isinstance(package, str):
			ex = TypeError("Parameter 'package' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(package)}'.")
			raise ex
		elif package == "":
			raise ValueError("Parameter 'package' is empty.")

		self._dependency = dependency
		self._extra =      extra
		self._package =    package

		if extra is None:
			self.add_note(f"Install '{dependency}'.")
		else:
			self.add_note(f"Either install {package} with extra '{package}[{extra}]' or install '{dependency}' directly.")

	@readonly
	def Dependency(self) -> str:
		"""
		Read-only property to access the name of the package that is not installed (:attr:`_dependency`).

		:returns: Name of the missing package.
		"""
		return self._dependency

	@readonly
	def Extra(self) -> Nullable[str]:
		"""
		Read-only property to access the name of the extra installing the package (:attr:`_extra`).

		:returns: Name of the extra, or ``None`` if the package has no extra of its own.
		"""
		return self._extra

	@readonly
	def Package(self) -> str:
		"""
		Read-only property to access the name of the package providing the extra (:attr:`_package`).

		:returns: Name of the package providing the extra.
		"""
		return self._package

	@readonly
	def InstallCommands(self) -> tuple[str, ...]:
		"""
		Read-only property to return the command lines installing the missing package.

		The extra comes first, because it installs the package *and* records why it is needed. Both commands are
		plain text and need no terminal support: an application that cannot even import :mod:`pyTooling.TerminalUI` -
		because *colorama* is the missing package - can print them itself, and
		:meth:`~pyTooling.TerminalUI.TerminalBaseApplication.PrintMissingDependencyError` formats them when it can.

		:returns: One command line per installation option, most specific first.
		"""
		if self._extra is None:
			return (f"pip install {self._dependency}", )

		return (
			f"pip install {self._package}[{self._extra}]",
			f"pip install {self._dependency}"
		)


# FIXME: Why not derived from ExceptionBase?
@export
class DuplicateElementError(Exception):
	"""
	The exception is raised when an element is added to a data structure, which already contains an element of the same
	kind and key.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class DuplicateVertexError(GraphError, DuplicateElementError)``. It has no initializer of its own, so the
	package's base-exception decides how the message is stored.
	"""


@export
class ElementNotFoundError(LookupError):
	"""
	The exception is raised when a data structure contains no element of the requested kind and key.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class SpanNotFoundError(TracingError, ElementNotFoundError)`` in :mod:`pyTooling.Tracing`. It's a
	:exc:`LookupError`, so code catching that catches it too. It has no initializer of its own, so the package's
	base-exception decides how the message is stored.
	"""


@export
class CycleError(Exception):
	"""
	The exception is raised when the elements of a data structure reference each other in a cycle, where the structure
	doesn't permit one.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class SpanCycleError(TracingError, CycleError)`` in :mod:`pyTooling.Tracing`. It has no initializer of its own,
	so the package's base-exception decides how the message is stored.
	"""


@export
class AlreadyInHierarchyError(Exception):
	"""
	The exception is raised when an element is added to a hierarchy, but it's already part of one.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class AlreadyInTreeError(TreeError, AlreadyInHierarchyError)``. It has no initializer of its own, so the
	package's base-exception decides how the message is stored.
	"""


@export
class NotInSameHierarchyError(Exception):
	"""
	The exception is raised when an element is used together with an element of another data structure.

	The element itself is valid, only its ownership is wrong. It's a common base: a package's own exception derives from
	it and from the package's base-exception, e.g. ``class NotInSameTreeError(TreeError, NotInSameHierarchyError)``. It
	has no initializer of its own, so the package's base-exception decides how the message is stored.
	"""


@export
class NotAChildError(Exception):
	"""
	The exception is raised when an element is not a direct child of the element it's removed from or looked up in.

	It's about the direct parent/child relation, not about the whole hierarchy: a grandchild is in the same hierarchy,
	but it's a child of another element. It's a common base: a package's own exception derives from it and from the
	package's base-exception, e.g. ``class NotAChildError(TreeError, NotAChildError)`` in :mod:`pyTooling.Tree`. It has
	no initializer of its own, so the package's base-exception decides how the message is stored.
	"""


@export
class InUseError(Exception):
	"""
	The exception is raised when an element is removed from a data structure, but other elements still use it.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class LibraryInUseError(VHDLModelException, InUseError)`` in pyVHDLModel. It has no initializer of its own, so the
	package's base-exception decides how the message is stored.
	"""


@export
class EmptyError(Exception):
	"""
	The exception is raised when an operation needs at least one element, but a data structure has none.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class EmptyGroupError(Cartesian2DError, EmptyError)`` in :mod:`pyTooling.Cartesian2D.Groups`. It has no initializer
	of its own, so the package's base-exception decides how the message is stored.
	"""


@export
class UnknownKindError(Exception):
	"""
	The exception is raised when an element is of a kind, which a data structure or an operation doesn't expect at its
	place.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class UnknownSymbolKindError(VHDLModelException, UnknownKindError)`` in pyVHDLModel. It has no initializer of its
	own, so the package's base-exception decides how the message is stored.
	"""


@export
class AmbiguousError(Exception):
	"""
	The exception is raised when several elements match, where exactly one is expected.

	It's a common base: a package's own exception derives from it and from the package's base-exception, e.g.
	``class AmbiguousTopLevelError(VHDLModelException, AmbiguousError)`` in pyVHDLModel. It has no initializer of its
	own, so the package's base-exception decides how the message is stored.
	"""


@export
class InvalidOperationError(RuntimeError):
	"""
	The exception is raised when an operation isn't valid for an object.

	E.g. :meth:`Origin2D.Copy() <pyTooling.Cartesian2D.Origin2D.Copy>` raises it, because an origin exists only once.

	It's a common base: a package's own exception derives from it and from the package's base-exception. It's a
	:exc:`RuntimeError`, so code catching that catches it too. It has no initializer of its own, so the package's
	base-exception decides how the message is stored.
	"""
