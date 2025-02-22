# ==================================================================================================================== #
#             _____           _ _               ____ _     ___    _    _         _                  _   _              #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___| |   |_ _|  / \  | |__  ___| |_ _ __ __ _  ___| |_(_) ___  _ __   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   | |    | |  / _ \ | '_ \/ __| __| '__/ _` |/ __| __| |/ _ \| '_ \  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |___| |___ | | / ___ \| |_) \__ \ |_| | | (_| | (__| |_| | (_) | | | | #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____|_____|___/_/   \_\_.__/|___/\__|_|  \__,_|\___|\__|_|\___/|_| |_| #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2014-2016 Technische Universität Dresden - Germany, Chair of VLSI-Design, Diagnostics and Architecture     #
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
List of valued flags are argument lists where each item is a valued flag (See
:mod:`~pyTooling.CLIAbstraction.ValuedFlag.ValuedFlag`).

Each list item gets translated into a ``***ValuedFlag``, with the same flag name, but differing values.

.. seealso::

   * For single valued flags. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlag`
   * For list of strings. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Argument.StringListArgument`
   * For list of paths. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Argument.PathListArgument`
"""
from sys    import version_info           # needed for versions before Python 3.11
from typing import List, Union, Iterable, cast, Any

try:
	from pyTooling.Decorators              import export
	from pyTooling.Common                  import getFullyQualifiedName
	from pyTooling.CLIAbstraction.Argument import ValueT, NamedAndValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from Common                          import getFullyQualifiedName
		from CLIAbstraction.Argument         import ValueT, NamedAndValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class ValuedFlagList(NamedAndValuedArgument, pattern="{0}={1}"):
	"""
	Class and base-class for all ValuedFlagList classes, which represents a list of valued flags.

	Each list element gets translated to a valued flag using the pattern for formatting.
	See :mod:`~pyTooling.CLIAbstraction.ValuedFlag` for more details on valued flags.

	**Example:**

	* ``file=file1.log file=file2.log``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "{0}={1}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ValuedFlagList:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)

	def __init__(self, value: List[ValueT]) -> None:
		super().__init__(list(value))

	@property
	def Value(self) -> List[str]:
		"""
		Get the internal value.

		:return: Internal value.
		"""
		return self._value

	@Value.setter
	def Value(self, values: Iterable[str]) -> None:
		"""
		Set the internal value.

		:param values:       List of values to set.
		:raises ValueError:  If a list element is not o type :class:`str`.
		"""
		innerList = cast(list, self._value)
		innerList.clear()
		for value in values:
			if not isinstance(value, str):
				ex = TypeError(f"Value contains elements which are not of type 'str'.")
				if version_info >= (3, 11):  # pragma: no cover
					ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex
			innerList.append(value)

	def AsArgument(self) -> Union[str, Iterable[str]]:
		if self._name is None:
			raise ValueError(f"")  # XXX: add message

		return [self._pattern.format(self._name, value) for value in self._value]

	def __str__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Space separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return " ".join([f"\"{value}\"" for value in self.AsArgument()])

	def __repr__(self) -> str:
		"""
		Return a string representation of this argument instance.

		:return: Comma separated sequence of arguments formatted and each enclosed in double quotes.
		"""
		return ", ".join([f"\"{value}\"" for value in self.AsArgument()])


@export
class ShortValuedFlagList(ValuedFlagList, pattern="-{0}={1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a single dash.

	**Example:**

	* ``-file=file1.log -file=file2.log``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "-{0}={1}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is ShortValuedFlagList:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongValuedFlagList(ValuedFlagList, pattern="--{0}={1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a double dash.

	**Example:**

	* ``--file=file1.log --file=file2.log``
	"""

	def __init_subclass__(cls, *args: Any, pattern: str = "--{0}={1}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is LongValuedFlagList:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsValuedFlagList(ValuedFlagList, pattern="/{0}:{1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a single slash.

	**Example:**

	* ``/file:file1.log /file:file2.log``
	"""

	# TODO: Is it possible to copy the doc-string from super?
	def __init_subclass__(cls, *args: Any, pattern: str = "/{0}:{1}", **kwargs: Any):
		"""
		This method is called when a class is derived.

		:param args:    Any positional arguments.
		:param pattern: This pattern is used to format an argument.
		:param kwargs:  Any keyword argument.
		"""
		kwargs["pattern"] = pattern
		super().__init_subclass__(*args, **kwargs)

	def __new__(cls, *args: Any, **kwargs: Any):
		if cls is WindowsValuedFlagList:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
