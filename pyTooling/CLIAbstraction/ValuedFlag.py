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
Valued flags are arguments with a name and an always present value.

The usual delimiter sign between name and value is an equal sign (``=``).

.. seealso::

   * For simple flags. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.Flag`
   * For flags with different pattern based on the boolean value itself. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.BooleanFlag`
   * For flags that have an optional value. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.NamedOptionalValuedFlag`
   * For list of valued flags. |br|
     |rarr| :mod:`~pyTooling.CLIAbstraction.ValuedFlagList`
"""
from typing import Any

try:
	from pyTooling.Decorators              import export
	from pyTooling.CLIAbstraction.Argument import NamedAndValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Versioning] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                      import export
		from CLIAbstraction.Argument         import NamedAndValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Versioning] Could not import directly!")
		raise ex


@export
class ValuedFlag(NamedAndValuedArgument, pattern="{0}={1}"):
	"""
	Class and base-class for all ValuedFlag classes, which represents a flag argument with value.

	A valued flag is a flag name followed by a value. The default delimiter sign is equal (``=``). Name and value are
	passed as one argument to the executable even if the delimiter sign is a whitespace character.

	**Example:**

	* ``width=100``
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
		if cls is ValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class ShortValuedFlag(ValuedFlag, pattern="-{0}={1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a single dash.

	**Example:**

	* ``-optimizer=on``
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
		if cls is ShortValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class LongValuedFlag(ValuedFlag, pattern="--{0}={1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a double dash.

	**Example:**

	* ``--optimizer=on``
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
		if cls is LongValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)


@export
class WindowsValuedFlag(ValuedFlag, pattern="/{0}:{1}"):
	"""
	Represents a :py:class:`ValuedFlagArgument` with a single slash.

	**Example:**

	* ``/optimizer:on``
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
		if cls is WindowsValuedFlag:
			raise TypeError(f"Class '{cls.__name__}' is abstract.")
		return super().__new__(cls, *args, **kwargs)
