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

   See :ref:`high-level help <EXECPTION>` for explanations and usage examples.
"""
from typing               import Tuple, Iterable, Any, Optional as Nullable

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
	:param indent:    The indentation of the additional notes.
	:param separator: Separator between items.
	:param maxWidth:  The maximum width of the attached notes.
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

	.. seealso::

	   :deco:`~pyTooling.MetaClasses.overloadable`
	      |rarr| Mark a method as *overloadable*.
	"""

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> Tuple[str, ...]:
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

		:param message:   The exception message.
		"""
		super().__init__()
		self.message = message

	@readonly
	def HasNotes(self) -> bool:
		"""
		Read-only property to return if the warning has attached notes.

		:returns: True, if the warning has attached notes.
		"""
		return hasattr(self, "__notes__") and self.__notes__ is not None and len(self.__notes__) > 0

	@readonly
	def Notes(self) -> Tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()

	def __str__(self) -> str:
		"""
		Returns the exception's message text.

		:returns: The exception's message text.
		"""
		return self.message

	# @DocumentMemberAttribute(False)
	# @MethodAlias(pyExceptions.with_traceback)
	# def with_traceback(self): pass


@export
class EnvironmentException(ExceptionBase):
	"""The exception is raised when an expected environment variable is missing."""


# ConfigurationException
#

@export
class PlatformNotSupportedException(ExceptionBase):
	"""The exception is raise if the platform is not supported."""


@export
class NotConfiguredException(ExceptionBase):
	"""The exception is raise if the requested setting is not configured."""


@export
class MissingDependencyError(ImportError):
	"""
	The exception is raised when an optional dependency of pyTooling is not installed.

	Some modules need a package pyTooling doesn't install by default. Importing such a module without its dependency
	raises this exception instead of the bare :exc:`ImportError`, so the message names the extra that installs it.

	The exception derives from :exc:`ImportError`, because that is what a caller guarding an optional import expects to
	catch, and it carries the missing package and the extra as :attr:`Dependency` and :attr:`Extra`.

	.. admonition:: ``example.py``

	   .. code-block:: python

	      try:
	        from ruamel.yaml import YAML
	      except ImportError as ex:
	        raise MissingDependencyError(dependency="ruamel.yaml", extra="yaml") from ex
	"""

	_dependency: str            #: Field storing the name of the package that is not installed.
	_extra:      Nullable[str]  #: Field storing the name of the pyTooling extra installing that package.

	def __init__(self, message: Nullable[str] = None, /, *, dependency: str, extra: Nullable[str] = None) -> None:
		"""
		Initialize a new missing-dependency error and attach the installation hint as a note.

		:param message:    Optional, the exception message. |br|
		                   When omitted, it is derived from ``dependency`` - every raising site says the same thing, so
		                   there is nothing for the caller to add.
		:param dependency: Name of the package that is not installed.
		:param extra:      Optional, name of the pyTooling extra installing that package. |br|
		                   When given, the note offers ``pyTooling[<extra>]`` next to the package itself.
		"""
		super().__init__(message if message is not None else f"Optional dependency '{dependency}' not installed.")

		self._dependency = dependency
		self._extra = extra

		if extra is None:
			self.add_note(f"Install '{dependency}'.")
		else:
			self.add_note(f"Either install pyTooling with extra 'pyTooling[{extra}]' or install '{dependency}' directly.")

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
		Read-only property to access the name of the pyTooling extra installing the package (:attr:`_extra`).

		:returns: Name of the extra, or ``None`` if the package has no extra of its own.
		"""
		return self._extra


# FIXME: Why not derived from ExceptionBase?
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
	def Notes(self) -> Tuple[str, ...]:
		"""
		Read-only property to return warning's attached notes.

		:returns: Attached notes.
		"""
		return tuple(self.__notes__) if hasattr(self, "__notes__") else tuple()
